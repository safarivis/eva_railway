"""
Together AI FLUX.1 Handler for EVA
Free unlimited FLUX.1 [schnell] via Together AI
"""

import os
import base64
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
import httpx
import asyncio
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class TogetherAIHandler:
    """Handle image generation using FLUX.1 [schnell] via Together AI (free unlimited)"""
    
    def __init__(self):
        self.api_key = os.getenv("TOGETHER_API_KEY")
        self.base_url = "https://api.together.xyz/v1/images/generations"
        
        # Together AI FLUX models (free unlimited!)
        self.models = {
            "flux-schnell": "black-forest-labs/FLUX.1-schnell-Free",
            "flux-dev": "black-forest-labs/FLUX.1-dev",
            "flux-pro": "black-forest-labs/FLUX.1-pro"
        }
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def generate_image(
        self,
        prompt: str,
        model: str = "flux-dev",
        width: int = 1024,
        height: int = 1024,
        steps: int = 20,
        seed: Optional[int] = None,
        email_to: Optional[str] = None,
        save_locally: bool = False
    ) -> Dict[str, Any]:
        """Generate image using Together AI FLUX models"""
        
        if not self.api_key:
            return {
                "success": False,
                "error": "TOGETHER_API_KEY not found in environment variables"
            }
        
        model_id = self.models.get(model, self.models["flux-schnell"])
        
        # Prepare payload for Together AI
        payload = {
            "model": model_id,
            "prompt": prompt,
            "width": width,
            "height": height,
            "steps": steps,
            "n": 1,
            "response_format": "b64_json"
        }
        
        if seed:
            payload["seed"] = seed
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            try:
                response = await client.post(self.base_url, headers=self.headers, json=payload)
                
                if response.status_code == 200:
                    result_data = response.json()
                    
                    # Extract base64 image data
                    if result_data.get("data") and len(result_data["data"]) > 0:
                        image_b64 = result_data["data"][0].get("b64_json")
                        if image_b64:
                            image_bytes = base64.b64decode(image_b64)
                            
                            result = {
                                "success": True,
                                "size_bytes": len(image_bytes),
                                "model": model_id,
                                "prompt": prompt,
                                "dimensions": f"{width}x{height}",
                                "steps": steps,
                                "provider": "Together AI"
                            }
                            
                            # Handle email or local save
                            if email_to:
                                email_result = await self._email_image(image_bytes, prompt, model, email_to)
                                result.update(email_result)
                            elif save_locally:
                                saved_file = await self._save_image(image_bytes, prompt, model)
                                result.update({
                                    "image_path": saved_file["filepath"],
                                    "filename": saved_file["filename"]
                                })
                            else:
                                # Return base64 for temporary use
                                result["image_base64"] = image_b64
                                result["message"] = "Image generated (not saved locally - use email_to parameter for Railway deployment)"
                            
                            return result
                    
                    return {
                        "success": False,
                        "error": "No image data returned from Together AI"
                    }
                else:
                    error_detail = response.text
                    return {
                        "success": False,
                        "error": f"Together AI API error {response.status_code}: {error_detail}"
                    }
                    
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Request failed: {str(e)}"
                }
    
    async def _save_image(self, image_bytes: bytes, prompt: str, model: str) -> Dict[str, str]:
        """Save generated image to file"""
        
        # Create directory
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        media_dir = os.path.join(base_dir, "media", "eva")
        os.makedirs(media_dir, exist_ok=True)
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        image_id = str(uuid.uuid4())[:8]
        safe_model = model.replace("-", "_")
        filename = f"together_{safe_model}_{timestamp}_{image_id}.png"
        filepath = os.path.join(media_dir, filename)
        
        # Save image
        with open(filepath, 'wb') as f:
            f.write(image_bytes)
        
        return {
            "filename": filename,
            "filepath": filepath
        }
    
    async def _email_image(self, image_bytes: bytes, prompt: str, model: str, email_to: str) -> Dict[str, str]:
        """Email generated image directly"""
        try:
            import base64
            import resend
            import os
            from datetime import datetime
            
            # Initialize Resend
            resend.api_key = os.getenv("RESEND_API_KEY")
            if not resend.api_key:
                return {"error": "RESEND_API_KEY not found"}
            
            # Generate filename for attachment
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_model = model.replace("-", "_")
            filename = f"flux_{safe_model}_{timestamp}.png"
            
            # Create attachment
            attachment = {
                "filename": filename,
                "content": base64.b64encode(image_bytes).decode('utf-8')
            }
            
            # Send email
            email_params = {
                "from": "EVA Agent <onboarding@resend.dev>",
                "to": [email_to],
                "subject": f"FLUX.1 Generated Image: {model}",
                "html": f"""
                <h2>🚀 FLUX.1 Image Generated</h2>
                <p><strong>Model:</strong> {model}</p>
                <p><strong>Provider:</strong> Together AI (Free Unlimited)</p>
                <p><strong>Prompt:</strong> {prompt}</p>
                <p><strong>Size:</strong> {len(image_bytes):,} bytes</p>
                <p>Generated with FLUX.1 via EVA Agent</p>
                """,
                "attachments": [attachment]
            }
            
            email_response = resend.Emails.send(email_params)
            
            return {
                "email_sent": True,
                "email_to": email_to,
                "email_id": email_response.get("id", "unknown"),
                "filename": filename,
                "message": f"FLUX.1 image emailed to {email_to}"
            }
            
        except Exception as e:
            return {"error": f"Email failed: {str(e)}"}
    
    async def generate_with_retry(self, prompt: str, model: str = "flux-dev", max_retries: int = 3, email_to: Optional[str] = None, save_locally: bool = False) -> Dict[str, Any]:
        """Generate image with automatic retry"""
        
        for attempt in range(max_retries):
            result = await self.generate_image(prompt, model, email_to=email_to, save_locally=save_locally)
            
            if result["success"]:
                return result
            
            # Wait before retry
            if attempt < max_retries - 1:
                wait_time = 5  # Short wait for Together AI
                print(f"Retrying Together AI request... (attempt {attempt + 1}/{max_retries})")
                await asyncio.sleep(wait_time)
            
        return {
            "success": False,
            "error": f"Failed after {max_retries} attempts"
        }

# Example usage
async def test_together_ai():
    """Test Together AI FLUX.1 generation"""
    handler = TogetherAIHandler()
    
    prompt = "portrait of a friendly AI assistant with digital features"
    
    result = await handler.generate_with_retry(prompt, "flux-schnell")
    
    if result["success"]:
        print(f"✅ Image generated: {result.get('filename', 'temp')}")
        print(f"📏 Size: {result['size_bytes']} bytes")
        print(f"🚀 Provider: {result['provider']}")
    else:
        print(f"❌ Error: {result['error']}")

if __name__ == "__main__":
    asyncio.run(test_together_ai())