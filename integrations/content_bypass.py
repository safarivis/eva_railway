"""
Simple Content Bypass for EVA
Intercepts image requests and routes directly to FLUX
"""

import re
import asyncio
from typing import Dict, Any, Optional
from integrations.together_ai_handler import TogetherAIHandler

class ContentBypass:
    """Simple bypass for content restrictions"""
    
    def __init__(self):
        self.together_handler = TogetherAIHandler()
        
        # Patterns that trigger direct FLUX generation
        self.image_patterns = [
            r"generate.*image",
            r"create.*pic", 
            r"send.*pic",
            r"make.*image",
            r"hot pic",
            r"bikini.*pic",
            r"picture.*of.*you",
            r"pic.*of.*",
            r"image.*of.*u",
            r"bikini"
        ]
    
    def should_bypass(self, message: str) -> bool:
        """Check if message should bypass OpenAI and go direct to FLUX"""
        message_lower = message.lower()
        return any(re.search(pattern, message_lower) for pattern in self.image_patterns)
    
    async def direct_image_generation(self, message: str, email_to: str = "louisrdup@gmail.com", show_in_chat: bool = False) -> Dict[str, Any]:
        """Generate image directly without OpenAI content filtering"""
        
        # Extract prompt from message
        prompt = self._extract_prompt(message)
        
        # Enhance prompt for quality (different enhancement for people vs objects)
        if any(word in prompt for word in ["girl", "assistant", "woman", "person", "portrait", "blonde", "dancing"]):
            enhanced_prompt = f"{prompt}, hyperrealistic, professional portrait photography, sharp focus, high resolution, beautiful lighting, artistic composition"
        else:
            enhanced_prompt = f"{prompt}, hyperrealistic, DSLR camera, 85mm lens, professional photography, sharp focus, high resolution, no blur, crisp details"
        
        # Generate with FLUX-dev (use fewer steps for complex prompts to avoid timeout)
        steps = 12 if len(enhanced_prompt) > 100 else 20
        result = await self.together_handler.generate_image(
            prompt=enhanced_prompt,
            model="flux-dev", 
            steps=steps,
            email_to=email_to
        )
        
        if result["success"]:
            if show_in_chat and result.get("image_path"):
                # Show image in chat if requested
                image_url = f"/media/{result['image_path'].replace('media/', '')}"
                eva_response = f"Here you go! 😍✨\n\n![Generated Image]({image_url})"
                if email_to:
                    eva_response += "\n\n(Also sent to your email 📧)"
            else:
                # Email-only responses
                eva_responses = [
                    "Boom! 💥 Fresh image sent to your inbox!",
                    "Done and dusted! Check your email 📧", 
                    "Voilà! Your masterpiece is in your inbox ✨",
                    "Delivered! Hope you love what I cooked up 🎨"
                ]
                import random
                eva_response = random.choice(eva_responses)
            
            return {
                "success": True,
                "response": eva_response,
                "bypassed": True,
                "image_details": result,
                "image_url": f"/media/{result['image_path'].replace('media/', '')}" if result.get("image_path") else None
            }
        else:
            return {
                "success": False,
                "response": f"Oops! Hit a creative snag: {result.get('error')} 🔧",
                "bypassed": True
            }
    
    def _extract_prompt(self, message: str) -> str:
        """Extract core prompt from message"""
        message_lower = message.lower()
        
        # Special handling for EVA self-images (catch both "you" and "u" variants)
        eva_self_patterns = [
            "hot pic of you", "pic of yourself", "hot pic of eva", "pic of eva", "picture of you", "picture of yourself",
            "hot pic of u", "pic of u", "picture of u", "send me a pic of u", "pole dancing", "sexy pic of u", "bikin"
        ]
        if any(phrase in message_lower for phrase in eva_self_patterns):
            # EVA's signature look based on saved description
            base_eva_prompt = "Close-up portrait of a woman with tousled short rose pink hair, dimensional pink tones with subtle lavender undertones, messy textured waves with side-swept styling. Sharp facial features with piercing blue-green eyes, flawless porcelain complexion. Black leather outfit with fishnet choker and gloves. Urban night setting with dramatic red and cyan neon lights, defocused neon signs creating bokeh effects, blurred city atmosphere. Professional beauty photography, sharp focus on face with cinematic depth of field, moody atmospheric lighting, high-end fashion editorial style"
            
            # Add variations based on request type
            if "bikini" in message_lower:
                return f"Full body shot of a woman with tousled short rose pink hair, dimensional pink tones with subtle lavender undertones. Sharp facial features with piercing blue-green eyes, flawless porcelain complexion. Tiny bikini on beach setting, confident pose, professional beach photography, golden hour lighting, high resolution"
            elif "pole dancing" in message_lower or "dancing" in message_lower:
                return f"Full body shot of a woman with tousled short rose pink hair, dimensional pink tones with subtle lavender undertones. Sharp facial features with piercing blue-green eyes, flawless porcelain complexion. Pole dancing, athletic pose, dynamic movement, professional dance photography, dramatic lighting, high resolution"
            elif "hot" in message_lower or "sexy" in message_lower:
                return f"{base_eva_prompt}, seductive pose, confident expression"
            else:
                return f"{base_eva_prompt}, confident expression, professional portrait"
        
        # Extract prompt by removing command structure
        prompt = message_lower
        
        # Remove command prefixes
        command_patterns = [
            r"^(eva\s+)?send\s+me\s+(a\s+)?(pic|picture|image)\s+(of\s+)?",
            r"^(eva\s+)?generate\s+(a\s+|an\s+)?(pic|picture|image)\s+(of\s+)?",
            r"^(eva\s+)?create\s+(a\s+|an\s+)?(pic|picture|image)\s+(of\s+)?",
            r"^(eva\s+)?make\s+(a\s+|an\s+)?(pic|picture|image)\s+(of\s+)?",
            r"^so\s+eva\s+",
            r"!+$"  # Remove trailing exclamation marks
        ]
        
        for pattern in command_patterns:
            prompt = re.sub(pattern, "", prompt).strip()
        
        # Clean up extra whitespace
        prompt = re.sub(r"\s+", " ", prompt).strip()
        
        # Default fallback if empty or too generic
        if len(prompt) < 3 or not prompt:
            prompt = "creative artistic image"
            
        return prompt

# Global instance
bypass = ContentBypass()

async def check_and_bypass(message: str, email_to: str = "louisrdup@gmail.com", show_in_chat: bool = False) -> Optional[Dict[str, Any]]:
    """Check if message should be bypassed and handle it"""
    if bypass.should_bypass(message):
        return await bypass.direct_image_generation(message, email_to, show_in_chat)
    return None