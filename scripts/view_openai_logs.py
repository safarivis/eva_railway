#!/usr/bin/env python3
"""
OpenAI Log Viewer - View and analyze OpenAI API logs
"""
import json
import argparse
from datetime import datetime, timedelta
from pathlib import Path
import re

def view_logs(log_file: str, tail: int = 20, follow: bool = False, 
              filter_type: str = None, show_errors_only: bool = False):
    """View OpenAI logs with filtering options"""
    
    log_path = Path("logs/openai") / log_file
    
    if not log_path.exists():
        print(f"❌ Log file not found: {log_path}")
        return
    
    print(f"📋 Viewing: {log_path}")
    print("=" * 60)
    
    # Read lines
    try:
        with open(log_path, 'r') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"❌ Error reading log file: {e}")
        return
    
    # Filter lines
    if show_errors_only:
        lines = [line for line in lines if 'ERROR' in line or '❌' in line]
    
    if filter_type:
        lines = [line for line in lines if filter_type.upper() in line]
    
    # Get last N lines
    if tail > 0:
        lines = lines[-tail:]
    
    # Display lines
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Parse and format JSON logs
        if 'REQUEST START:' in line or 'REQUEST SUCCESS:' in line or 'REQUEST FAILED:' in line:
            try:
                # Extract JSON part
                json_start = line.find('{')
                if json_start != -1:
                    timestamp_part = line[:json_start].strip()
                    json_part = line[json_start:]
                    data = json.loads(json_part)
                    
                    if 'REQUEST START:' in line:
                        print(f"🚀 {timestamp_part}")
                        print(f"   Model: {data.get('model', 'unknown')}")
                        print(f"   Est. Tokens: {data.get('estimated_input_tokens', 0)}")
                        print(f"   Est. Cost: ${data.get('estimated_cost_usd', 0):.6f}")
                        if data.get('has_tools'):
                            print(f"   Tools: {data.get('tool_choice', 'auto')}")
                    
                    elif 'REQUEST SUCCESS:' in line:
                        duration = data.get('duration_seconds', 0)
                        total_tokens = data.get('total_tokens', 0)
                        cost = data.get('actual_cost_usd', 0)
                        cumulative_cost = data.get('cumulative_cost_usd', 0)
                        
                        print(f"✅ {timestamp_part}")
                        print(f"   Duration: {duration}s")
                        print(f"   Tokens: {total_tokens}")
                        print(f"   Cost: ${cost:.6f}")
                        print(f"   Total Cost: ${cumulative_cost:.4f}")
                    
                    elif 'REQUEST FAILED:' in line:
                        print(f"❌ {timestamp_part}")
                        print(f"   Status: {data.get('status_code', 'unknown')}")
                        print(f"   Duration: {data.get('duration_seconds', 0)}s")
                    
                    print()
                else:
                    print(line)
            except json.JSONDecodeError:
                print(line)
        
        elif 'STATS:' in line:
            try:
                json_start = line.find('{')
                if json_start != -1:
                    timestamp_part = line[:json_start].strip()
                    json_part = line[json_start:]
                    data = json.loads(json_part)
                    
                    print(f"📊 {timestamp_part}")
                    print(f"   Requests: {data.get('total_requests', 0)}")
                    print(f"   Total Tokens: {data.get('total_tokens', 0):,}")
                    print(f"   Total Cost: ${data.get('total_cost_usd', 0):.4f}")
                    print(f"   Avg Tokens/Req: {data.get('avg_tokens_per_request', 0):.1f}")
                    print()
            except json.JSONDecodeError:
                print(line)
        
        else:
            # Regular log line
            if '❌' in line or 'ERROR' in line:
                print(f"🚨 {line}")
            elif '✅' in line:
                print(f"✅ {line}")
            else:
                print(f"ℹ️  {line}")

def analyze_costs(days: int = 1):
    """Analyze costs over the last N days"""
    log_path = Path("logs/openai/openai_api.log")
    
    if not log_path.exists():
        print(f"❌ Log file not found: {log_path}")
        return
    
    # Calculate cutoff date
    cutoff_date = datetime.now() - timedelta(days=days)
    
    total_requests = 0
    total_tokens = 0
    total_cost = 0.0
    model_stats = {}
    
    with open(log_path, 'r') as f:
        for line in f:
            if 'REQUEST SUCCESS:' in line:
                try:
                    # Extract timestamp
                    timestamp_match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', line)
                    if timestamp_match:
                        timestamp_str = timestamp_match.group(1)
                        timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                        
                        if timestamp > cutoff_date:
                            # Parse JSON
                            json_start = line.find('{')
                            if json_start != -1:
                                data = json.loads(line[json_start:])
                                
                                total_requests += 1
                                tokens = data.get('total_tokens', 0)
                                cost = data.get('actual_cost_usd', 0)
                                
                                total_tokens += tokens
                                total_cost += cost
                                
                                # Track by model (would need to be in the log)
                                model = data.get('model', 'unknown')
                                if model not in model_stats:
                                    model_stats[model] = {'requests': 0, 'tokens': 0, 'cost': 0.0}
                                
                                model_stats[model]['requests'] += 1
                                model_stats[model]['tokens'] += tokens
                                model_stats[model]['cost'] += cost
                
                except Exception:
                    continue
    
    print(f"\n📊 Cost Analysis - Last {days} day(s)")
    print("=" * 50)
    print(f"Total Requests: {total_requests}")
    print(f"Total Tokens: {total_tokens:,}")
    print(f"Total Cost: ${total_cost:.4f}")
    
    if total_requests > 0:
        print(f"Avg Cost/Request: ${total_cost/total_requests:.6f}")
        print(f"Avg Tokens/Request: {total_tokens/total_requests:.1f}")
    
    if model_stats:
        print(f"\n📈 By Model:")
        for model, stats in model_stats.items():
            print(f"   {model}:")
            print(f"     Requests: {stats['requests']}")
            print(f"     Tokens: {stats['tokens']:,}")
            print(f"     Cost: ${stats['cost']:.6f}")

def main():
    parser = argparse.ArgumentParser(description='View OpenAI API logs')
    parser.add_argument('--file', default='openai_api.log', help='Log file to view')
    parser.add_argument('--tail', type=int, default=20, help='Show last N lines')
    parser.add_argument('--errors', action='store_true', help='Show only errors')
    parser.add_argument('--filter', help='Filter lines containing text')
    parser.add_argument('--analyze', type=int, metavar='DAYS', help='Analyze costs for last N days')
    
    args = parser.parse_args()
    
    if args.analyze:
        analyze_costs(args.analyze)
    else:
        view_logs(
            log_file=args.file,
            tail=args.tail,
            show_errors_only=args.errors,
            filter_type=args.filter
        )

if __name__ == "__main__":
    main()