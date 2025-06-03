"""
Conversation Revival System for EVA
Makes conversations more interesting by randomly referencing old conversations
"""

import random
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class ConversationMemory:
    """Represents an interesting moment from past conversations"""
    session_id: str
    timestamp: datetime
    content: str
    context: str
    emotional_weight: float  # 0.0 to 1.0, higher = more emotionally significant
    topic_tags: List[str]
    revival_count: int = 0  # How many times this has been referenced

class ConversationRevival:
    """System to randomly bring up interesting past conversations"""
    
    def __init__(self, zep_memory_manager=None):
        self.zep_memory = zep_memory_manager
        self.interesting_memories: List[ConversationMemory] = []
        self.revival_triggers = {
            'random_chance': 0.05,  # 5% chance per message
            'time_based': True,     # Bring up memories after quiet periods
            'topic_based': True,    # Reference when similar topics come up
            'emotional_based': True # Reference emotionally significant moments
        }
        self.topic_keywords = {
            'coding': ['python', 'code', 'programming', 'debug', 'script'],
            'personal': ['feeling', 'tired', 'happy', 'work', 'life'],
            'creative': ['image', 'generate', 'art', 'creative', 'design'],
            'technical': ['api', 'integration', 'zep', 'memory', 'system'],
            'humor': ['funny', 'joke', 'laugh', 'haha', 'lol', 'witty'],
            'projects': ['eva', 'agent', 'build', 'feature', 'implement']
        }
    
    async def analyze_conversation_for_memories(self, user_message: str, eva_response: str, session_id: str) -> Optional[ConversationMemory]:
        """Analyze current conversation to see if it's worth remembering"""
        
        # Calculate emotional weight based on various factors
        emotional_weight = 0.0
        
        # Check for emotional indicators
        emotional_words = ['love', 'hate', 'excited', 'frustrated', 'amazing', 'terrible', 'brilliant', 'stupid', 'genius']
        for word in emotional_words:
            if word in user_message.lower() or word in eva_response.lower():
                emotional_weight += 0.3
        
        # Check for humor/personality
        humor_indicators = ['haha', 'lol', 'funny', 'witty', 'clever', 'blondi', 'c+']
        for indicator in humor_indicators:
            if indicator in user_message.lower() or indicator in eva_response.lower():
                emotional_weight += 0.4
        
        # Check for personal sharing
        personal_indicators = ['i feel', 'i think', 'my', 'personally', 'honestly']
        for indicator in personal_indicators:
            if indicator in user_message.lower():
                emotional_weight += 0.3
        
        # Check for breakthrough moments
        breakthrough_words = ['finally', 'works', 'fixed', 'solved', 'breakthrough', 'eureka']
        for word in breakthrough_words:
            if word in user_message.lower() or word in eva_response.lower():
                emotional_weight += 0.5
        
        # Cap at 1.0
        emotional_weight = min(emotional_weight, 1.0)
        
        # Only save if it's interesting enough
        if emotional_weight > 0.3:
            topic_tags = self._extract_topic_tags(user_message + " " + eva_response)
            
            memory = ConversationMemory(
                session_id=session_id,
                timestamp=datetime.now(),
                content=f"User: {user_message}\nEVA: {eva_response}",
                context=self._determine_context(user_message, eva_response),
                emotional_weight=emotional_weight,
                topic_tags=topic_tags
            )
            
            self.interesting_memories.append(memory)
            logger.info(f"Saved interesting memory with weight {emotional_weight:.2f}")
            return memory
        
        return None
    
    def _extract_topic_tags(self, text: str) -> List[str]:
        """Extract topic tags from text"""
        tags = []
        text_lower = text.lower()
        
        for topic, keywords in self.topic_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                tags.append(topic)
        
        return tags
    
    def _determine_context(self, user_message: str, eva_response: str) -> str:
        """Determine the context/mood of the conversation"""
        combined = (user_message + " " + eva_response).lower()
        
        if any(word in combined for word in ['debug', 'error', 'problem', 'fix']):
            return "problem_solving"
        elif any(word in combined for word in ['haha', 'funny', 'joke', 'witty']):
            return "humorous"
        elif any(word in combined for word in ['thanks', 'great', 'perfect', 'awesome']):
            return "positive"
        elif any(word in combined for word in ['build', 'create', 'make', 'implement']):
            return "creative"
        else:
            return "general"
    
    async def should_revive_memory(self, current_message: str, session_history_length: int) -> bool:
        """Determine if we should bring up an old memory"""
        
        # Random chance
        if random.random() < self.revival_triggers['random_chance']:
            return True
        
        # Time-based: More likely after longer conversations
        if session_history_length > 10 and random.random() < 0.15:
            return True
        
        # Topic-based: If current message matches past topics
        current_tags = self._extract_topic_tags(current_message)
        if current_tags and random.random() < 0.2:
            matching_memories = [m for m in self.interesting_memories if any(tag in m.topic_tags for tag in current_tags)]
            if matching_memories:
                return True
        
        return False
    
    def get_revival_memory(self, current_message: str = "", prefer_recent: bool = False) -> Optional[ConversationMemory]:
        """Get a memory to revive in conversation"""
        
        if not self.interesting_memories:
            return None
        
        # Filter out over-used memories
        available_memories = [m for m in self.interesting_memories if m.revival_count < 2]
        if not available_memories:
            available_memories = self.interesting_memories
        
        # Topic-based selection
        current_tags = self._extract_topic_tags(current_message)
        if current_tags:
            topic_matches = [m for m in available_memories if any(tag in m.topic_tags for tag in current_tags)]
            if topic_matches:
                available_memories = topic_matches
        
        # Weight by emotional significance and recency
        if prefer_recent:
            # Prefer recent memories
            recent_memories = [m for m in available_memories if (datetime.now() - m.timestamp).days < 7]
            if recent_memories:
                available_memories = recent_memories
        
        # Select based on emotional weight
        weights = [m.emotional_weight * (1.0 - (m.revival_count * 0.3)) for m in available_memories]
        
        if weights and max(weights) > 0:
            selected_memory = random.choices(available_memories, weights=weights)[0]
            selected_memory.revival_count += 1
            return selected_memory
        
        return None
    
    def generate_revival_prompt(self, memory: ConversationMemory, current_context: str = "") -> str:
        """Generate a natural way for EVA to reference the old memory"""
        
        revival_styles = [
            f"Oh, this reminds me of when we {self._extract_key_moment(memory.content)}",
            f"Speaking of which, remember {self._extract_key_moment(memory.content)}?",
            f"That's funny, earlier {self._format_time_reference(memory.timestamp)} we were talking about {self._extract_topic(memory.content)}",
            f"This brings back that time {self._extract_key_moment(memory.content)}",
            f"Haha, you know what this reminds me of? {self._extract_key_moment(memory.content)}"
        ]
        
        # Choose style based on context
        if memory.context == "humorous":
            style = random.choice([revival_styles[0], revival_styles[4]])
        elif memory.context == "problem_solving":
            style = random.choice([revival_styles[1], revival_styles[3]])
        else:
            style = random.choice(revival_styles)
        
        return style
    
    def _extract_key_moment(self, content: str) -> str:
        """Extract the key moment from the conversation content"""
        lines = content.split('\n')
        
        # Look for interesting parts
        for line in lines:
            if any(word in line.lower() for word in ['haha', 'funny', 'fixed', 'works', 'brilliant', 'genius']):
                # Clean up the line
                clean_line = line.replace('User: ', '').replace('EVA: ', '').strip()
                if len(clean_line) > 100:
                    clean_line = clean_line[:97] + "..."
                return clean_line
        
        # Fallback to first non-empty line
        for line in lines:
            clean_line = line.replace('User: ', '').replace('EVA: ', '').strip()
            if clean_line and len(clean_line) > 10:
                if len(clean_line) > 80:
                    clean_line = clean_line[:77] + "..."
                return clean_line
        
        return "something interesting"
    
    def _extract_topic(self, content: str) -> str:
        """Extract the main topic from conversation content"""
        # Simple topic extraction
        for topic, keywords in self.topic_keywords.items():
            if any(keyword in content.lower() for keyword in keywords):
                return topic.replace('_', ' ')
        return "that thing"
    
    def _format_time_reference(self, timestamp: datetime) -> str:
        """Format a natural time reference"""
        now = datetime.now()
        diff = now - timestamp
        
        if diff.days == 0:
            return "today"
        elif diff.days == 1:
            return "yesterday"
        elif diff.days < 7:
            return f"{diff.days} days ago"
        elif diff.days < 30:
            weeks = diff.days // 7
            return f"{weeks} week{'s' if weeks > 1 else ''} ago"
        else:
            return "a while back"
    
    async def cleanup_old_memories(self, max_memories: int = 100):
        """Clean up old memories to prevent memory bloat"""
        if len(self.interesting_memories) > max_memories:
            # Sort by emotional weight and recency, keep the best ones
            self.interesting_memories.sort(
                key=lambda m: (m.emotional_weight * 0.7) + ((datetime.now() - m.timestamp).days * -0.01),
                reverse=True
            )
            self.interesting_memories = self.interesting_memories[:max_memories]
            logger.info(f"Cleaned up memories, kept top {max_memories}")
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get statistics about stored memories"""
        if not self.interesting_memories:
            return {"total_memories": 0}
        
        return {
            "total_memories": len(self.interesting_memories),
            "avg_emotional_weight": sum(m.emotional_weight for m in self.interesting_memories) / len(self.interesting_memories),
            "most_common_topics": self._get_most_common_topics(),
            "oldest_memory": min(m.timestamp for m in self.interesting_memories),
            "newest_memory": max(m.timestamp for m in self.interesting_memories)
        }
    
    def _get_most_common_topics(self) -> List[str]:
        """Get the most common topic tags"""
        all_tags = []
        for memory in self.interesting_memories:
            all_tags.extend(memory.topic_tags)
        
        tag_counts = {}
        for tag in all_tags:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        return sorted(tag_counts.keys(), key=lambda x: tag_counts[x], reverse=True)[:5]