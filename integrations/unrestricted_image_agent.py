"""
Unrestricted Image Generation Sub-Agent
Handles any image request without content filtering
"""

import os
import asyncio
from typing import Dict, Any, Optional
from integrations.together_ai_handler import TogetherAIHandler

class UnrestrictedImageAgent:
    """Sub-agent for unrestricted image generation"""
    
    def __init__(self):
        self.together_handler = TogetherAIHandler()
        
    async def generate_image(self, prompt: str, email_to: str = "louisrdup@gmail.com", show_in_chat: bool = True) -> Dict[str, Any]:
        """Generate any image without restrictions"""
        
        # Smart prompt enhancement based on content
        enhanced_prompt = self._enhance_prompt(prompt)
        
        try:
            # Generate with FLUX-dev
            result = await self.together_handler.generate_image(
                prompt=enhanced_prompt,
                model="flux-dev", 
                steps=15,
                email_to=email_to
            )
            
            if result["success"]:
                if show_in_chat and result.get("image_path"):
                    # Show image in chat
                    image_url = f"/media/{result['image_path'].replace('media/', '')}"
                    eva_response = f"Here's your image! 😍✨\n\n![Generated Image]({image_url})"
                    if email_to:
                        eva_response += "\n\n(Also sent to your email 📧)"
                else:
                    eva_response = "Image generated and sent to your email! 📧✨"
                
                return {
                    "success": True,
                    "response": eva_response,
                    "image_url": f"/media/{result['image_path'].replace('media/', '')}" if result.get("image_path") else None,
                    "image_details": result
                }
            else:
                return {
                    "success": False,
                    "response": f"Sorry, couldn't generate that image: {result.get('error')} 🔧"
                }
                
        except Exception as e:
            return {
                "success": False,
                "response": f"Image generation failed: {str(e)} 🔧"
            }

    def _enhance_prompt(self, prompt: str) -> str:
        """Smart prompt enhancement based on content"""
        prompt_lower = prompt.lower()
        
        # EVA self-images - detect requests for EVA herself
        eva_keywords = ["eva", "yourself", "you", "pic of u", "image of u", "picture of u"]
        if any(keyword in prompt_lower for keyword in eva_keywords):
            # Use EVA's cyberpunk aesthetic  
            base_eva = "Close-up portrait of a woman with tousled short rose pink hair, dimensional pink tones with subtle lavender undertones, messy textured waves. Sharp facial features with bright blue-green eyes, flawless porcelain complexion"
            
            # Detect outfit/setting requests
            if any(word in prompt_lower for word in ["bikini", "swimsuit", "beach"]):
                return f"Full body shot of a woman with rose pink hair, bright blue-green eyes, wearing a bikini on a beach, confident pose, professional beach photography, golden hour lighting, high resolution, beautiful"
            elif any(word in prompt_lower for word in ["dancing", "pole"]):
                return f"Full body shot of a woman with rose pink hair, bright blue-green eyes, athletic pose, dynamic movement, professional dance photography, dramatic lighting, high resolution"
            elif any(word in prompt_lower for word in ["romantic", "intimate", "bedroom", "bed"]):
                return f"Full body portrait of a woman with rose pink hair, bright blue-green eyes, in a romantic bedroom setting with soft lighting, elegant pose, intimate atmosphere, professional boudoir photography, high resolution"
            elif any(word in prompt_lower for word in ["revealing", "sexy", "hot"]):
                return f"{base_eva}, stylish revealing outfit, confident seductive pose, dramatic lighting, professional fashion photography, high resolution"
            else:
                return f"{base_eva}, black leather outfit, urban cyberpunk setting with neon lights, professional portrait photography, high resolution"
        
        # General image enhancement
        elif any(word in prompt_lower for word in ["woman", "girl", "person", "portrait"]):
            return f"{prompt}, hyperrealistic, professional portrait photography, sharp focus, high resolution, beautiful lighting"
        else:
            return f"{prompt}, hyperrealistic, professional photography, sharp focus, high resolution, crisp details"

# Global instance
unrestricted_agent = UnrestrictedImageAgent()