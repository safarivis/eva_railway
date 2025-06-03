"""
TTS Cost Tracker for ElevenLabs Credit Management
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import os

@dataclass
class TTSUsage:
    """Track TTS usage for cost estimation"""
    timestamp: datetime
    character_count: int
    estimated_cost: float
    session_id: str
    content_preview: str  # First 50 chars for debugging

class TTSCostTracker:
    """Track and manage TTS costs"""
    
    def __init__(self, storage_path: str = "logs/tts_usage.json"):
        self.storage_path = storage_path
        self.usage_history: List[TTSUsage] = []
        self.cost_per_character = 0.00003  # Approximate ElevenLabs cost per character
        self.daily_budget = 1.0  # $1 per day budget
        
        # Ensure logs directory exists
        os.makedirs(os.path.dirname(storage_path), exist_ok=True)
        
        # Load existing usage
        self._load_usage_history()
    
    def estimate_cost(self, text: str) -> float:
        """Estimate cost for converting text to speech"""
        char_count = len(text)
        return char_count * self.cost_per_character
    
    def track_usage(self, text: str, session_id: str) -> TTSUsage:
        """Track TTS usage"""
        char_count = len(text)
        cost = self.estimate_cost(text)
        
        usage = TTSUsage(
            timestamp=datetime.now(),
            character_count=char_count,
            estimated_cost=cost,
            session_id=session_id,
            content_preview=text[:50] + "..." if len(text) > 50 else text
        )
        
        self.usage_history.append(usage)
        self._save_usage_history()
        
        return usage
    
    def get_daily_usage(self, date: Optional[datetime] = None) -> Dict:
        """Get usage statistics for a specific day"""
        if date is None:
            date = datetime.now()
        
        start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)
        
        daily_usage = [
            usage for usage in self.usage_history
            if start_of_day <= usage.timestamp < end_of_day
        ]
        
        total_characters = sum(usage.character_count for usage in daily_usage)
        total_cost = sum(usage.estimated_cost for usage in daily_usage)
        
        return {
            "date": date.strftime("%Y-%m-%d"),
            "total_characters": total_characters,
            "total_cost": total_cost,
            "usage_count": len(daily_usage),
            "budget_remaining": max(0, self.daily_budget - total_cost),
            "budget_percentage": min(100, (total_cost / self.daily_budget) * 100)
        }
    
    def get_weekly_usage(self) -> Dict:
        """Get usage statistics for the past week"""
        now = datetime.now()
        week_ago = now - timedelta(days=7)
        
        weekly_usage = [
            usage for usage in self.usage_history
            if usage.timestamp >= week_ago
        ]
        
        total_characters = sum(usage.character_count for usage in weekly_usage)
        total_cost = sum(usage.estimated_cost for usage in weekly_usage)
        
        # Daily breakdown
        daily_breakdown = []
        for i in range(7):
            day = now - timedelta(days=i)
            day_stats = self.get_daily_usage(day)
            daily_breakdown.append(day_stats)
        
        return {
            "period": "last_7_days",
            "total_characters": total_characters,
            "total_cost": total_cost,
            "usage_count": len(weekly_usage),
            "daily_breakdown": daily_breakdown
        }
    
    def should_limit_tts(self) -> Dict:
        """Check if TTS should be limited due to budget concerns"""
        today = self.get_daily_usage()
        
        warning_threshold = 0.8  # 80% of budget
        critical_threshold = 0.95  # 95% of budget
        
        budget_used = today["budget_percentage"] / 100
        
        return {
            "should_limit": budget_used > critical_threshold,
            "should_warn": budget_used > warning_threshold,
            "budget_used_percentage": today["budget_percentage"],
            "remaining_budget": today["budget_remaining"],
            "recommendation": self._get_recommendation(budget_used)
        }
    
    def _get_recommendation(self, budget_used: float) -> str:
        """Get recommendation based on budget usage"""
        if budget_used > 0.95:
            return "CRITICAL: Daily budget nearly exhausted. Disable TTS or reduce response length."
        elif budget_used > 0.8:
            return "WARNING: High TTS usage today. Consider shorter responses."
        elif budget_used > 0.5:
            return "MODERATE: TTS usage on track. Monitor for rest of day."
        else:
            return "LOW: TTS budget usage is healthy."
    
    def get_character_efficiency_stats(self) -> Dict:
        """Analyze character efficiency in TTS usage"""
        if not self.usage_history:
            return {"message": "No usage data available"}
        
        recent_usage = self.usage_history[-50:]  # Last 50 uses
        
        char_counts = [usage.character_count for usage in recent_usage]
        avg_chars = sum(char_counts) / len(char_counts)
        
        # Categorize response lengths
        short_responses = len([c for c in char_counts if c <= 100])
        medium_responses = len([c for c in char_counts if 100 < c <= 300])
        long_responses = len([c for c in char_counts if c > 300])
        
        return {
            "recent_samples": len(recent_usage),
            "average_characters": round(avg_chars, 1),
            "shortest_response": min(char_counts),
            "longest_response": max(char_counts),
            "distribution": {
                "short_responses_<=100": short_responses,
                "medium_responses_100-300": medium_responses,
                "long_responses_>300": long_responses
            },
            "efficiency_score": self._calculate_efficiency_score(char_counts)
        }
    
    def _calculate_efficiency_score(self, char_counts: List[int]) -> str:
        """Calculate efficiency score based on response lengths"""
        avg_chars = sum(char_counts) / len(char_counts)
        
        if avg_chars <= 120:
            return "EXCELLENT - Very cost efficient"
        elif avg_chars <= 200:
            return "GOOD - Cost efficient"
        elif avg_chars <= 300:
            return "MODERATE - Could be more efficient"
        else:
            return "POOR - Consider shorter responses"
    
    def cleanup_old_usage(self, days_to_keep: int = 30):
        """Clean up old usage data"""
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        original_count = len(self.usage_history)
        self.usage_history = [
            usage for usage in self.usage_history
            if usage.timestamp >= cutoff_date
        ]
        
        removed_count = original_count - len(self.usage_history)
        self._save_usage_history()
        
        return {
            "removed_entries": removed_count,
            "remaining_entries": len(self.usage_history),
            "days_kept": days_to_keep
        }
    
    def _load_usage_history(self):
        """Load usage history from storage"""
        try:
            if os.path.exists(self.storage_path):
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                    self.usage_history = [
                        TTSUsage(
                            timestamp=datetime.fromisoformat(item['timestamp']),
                            character_count=item['character_count'],
                            estimated_cost=item['estimated_cost'],
                            session_id=item['session_id'],
                            content_preview=item.get('content_preview', '')
                        )
                        for item in data
                    ]
        except Exception as e:
            print(f"Error loading TTS usage history: {e}")
            self.usage_history = []
    
    def _save_usage_history(self):
        """Save usage history to storage"""
        try:
            data = []
            for usage in self.usage_history:
                usage_dict = asdict(usage)
                usage_dict['timestamp'] = usage.timestamp.isoformat()
                data.append(usage_dict)
            
            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving TTS usage history: {e}")
    
    def get_cost_summary(self) -> Dict:
        """Get comprehensive cost summary"""
        daily = self.get_daily_usage()
        weekly = self.get_weekly_usage()
        limits = self.should_limit_tts()
        efficiency = self.get_character_efficiency_stats()
        
        return {
            "daily_usage": daily,
            "weekly_usage": {
                "total_cost": weekly["total_cost"],
                "total_characters": weekly["total_characters"],
                "usage_count": weekly["usage_count"]
            },
            "budget_status": limits,
            "efficiency": efficiency,
            "settings": {
                "cost_per_character": self.cost_per_character,
                "daily_budget": self.daily_budget
            }
        }