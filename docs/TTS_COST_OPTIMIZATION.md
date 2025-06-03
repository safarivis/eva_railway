# EVA TTS Cost Optimization

## Overview

EVA includes intelligent TTS cost optimization to help you save ElevenLabs credits by automatically adjusting response length and frequency when voice mode is enabled.

## Key Features

### 🎤 **Adaptive Response Length**
When `voice_enabled=true`, EVA automatically:
- Keeps responses to 1-2 sentences max
- Uses punchy, direct language
- Maintains wit but with fewer words
- Avoids long explanations unless critical
- Thinks "text message" length, not "essay" length

### 💰 **Cost Tracking**
Real-time monitoring of TTS usage:
- Character count per response
- Estimated cost per interaction
- Daily/weekly budget tracking
- Usage efficiency analysis

### 🚨 **Budget Protection**
Automatic warnings and limits:
- Warning at 80% of daily budget
- Critical alert at 95% of budget
- Automatic reduction of conversation revival frequency
- Shorter revival prompts in voice mode

## Cost Examples

Based on ElevenLabs pricing (~$0.00003 per character):

| Response Type | Characters | Cost |
|---------------|------------|------|
| "Perfect!" | 8 | $0.0002 |
| "Got it, working on that now." | 28 | $0.0008 |
| Long explanation | 200+ | $0.006+ |

**Daily Budget**: $1.00 (default)
**Optimal range**: 50-100 characters per response

## Configuration

### System Prompt Adaptation
```python
# Voice mode adds these instructions:
🎤 VOICE MODE - CREDIT CONSERVATION:
- MAX 1-2 sentences per response
- Be punchy and direct
- Maintain wit but use fewer words
- Avoid explanations unless critical
```

### Cost Tracking Settings
```python
cost_per_character = 0.00003  # ElevenLabs estimate
daily_budget = 1.0           # $1 per day
warning_threshold = 0.8      # 80% of budget
critical_threshold = 0.95    # 95% of budget
```

## API Endpoints

### Get Cost Summary
```bash
GET /api/tts/costs
```

Returns comprehensive cost analysis:
```json
{
  "daily_usage": {
    "total_characters": 1500,
    "total_cost": 0.045,
    "budget_remaining": 0.955,
    "budget_percentage": 4.5
  },
  "efficiency": {
    "average_characters": 85,
    "efficiency_score": "EXCELLENT - Very cost efficient"
  }
}
```

### Check Budget Status
```bash
GET /api/tts/budget
```

Returns current budget status:
```json
{
  "should_limit": false,
  "should_warn": false,
  "budget_used_percentage": 25.5,
  "remaining_budget": 0.745,
  "recommendation": "MODERATE: TTS usage on track"
}
```

### Clean Up Logs
```bash
POST /api/tts/cleanup
```

Removes old usage data (keeps 30 days).

## Smart Optimizations

### 📊 **Response Analysis**
EVA tracks response patterns:
- Short (≤100 chars): Most cost-effective
- Medium (100-300 chars): Acceptable
- Long (>300 chars): Avoided in voice mode

### 🎯 **Conversation Revival Reduction**
In voice mode:
- 70% reduction in revival frequency
- Shorter revival prompts (≤80 chars)
- Focus on most impactful memories only

### 💬 **Context-Aware Optimization**
- Technical explanations → simplified in voice
- Code examples → text-only by default
- Casual chat → naturally concise

## Best Practices

### ✅ **Voice Mode Guidelines**
- Use EVA for quick interactions when voice enabled
- Switch to text mode for detailed discussions
- Monitor daily usage via API endpoints
- Set appropriate daily budgets

### 📈 **Efficiency Tips**
- Aim for <100 characters per response
- Use abbreviations and contractions
- Be direct and conversational
- Save details for follow-up text

### 🔍 **Monitoring**
- Check `/api/tts/costs` daily
- Watch for budget warnings
- Review efficiency scores
- Clean up logs monthly

## Cost Comparison

### Text Mode vs Voice Mode

**Text Mode Response** (No TTS cost):
```
"I can help you debug that Python script. The error suggests you have a missing import statement on line 15. You'll want to add 'import json' at the top of your file. You can also check for any other missing dependencies by running 'pip install -r requirements.txt' to ensure all packages are available."
```
Characters: 312 | Cost: $0.0094

**Voice Mode Response** (Optimized):
```
"Missing import on line 15. Add 'import json' at the top."
```
Characters: 55 | Cost: $0.0017

**Savings**: 82% fewer characters, 82% cost reduction

## Budget Recommendations

### Daily Usage Patterns
- **Light user** (10-20 voice interactions): $0.25/day
- **Regular user** (50-100 interactions): $0.75/day  
- **Heavy user** (200+ interactions): $1.50/day

### Budget Settings
- **Conservative**: $0.50/day (1,667 characters)
- **Standard**: $1.00/day (3,333 characters)
- **Liberal**: $2.00/day (6,667 characters)

## Troubleshooting

### High Costs
1. Check response length via `/api/tts/costs`
2. Verify voice mode is properly optimized
3. Review conversation revival frequency
4. Consider lower daily budget threshold

### Budget Warnings
1. Review efficiency scores
2. Switch to text mode for detailed work
3. Monitor usage patterns
4. Adjust daily budget if needed

---

This system ensures you can enjoy EVA's voice capabilities while maintaining control over ElevenLabs costs through intelligent optimization and monitoring.