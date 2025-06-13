"""
Stable Diffusion XL Lightning Handler for EVA
Fast, free image generation using SDXL Lightning
"""

import os
import base64
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
import httpx
import asyncio
import json

class SDXLLightningHandler:
    """Handle image generation using SDXL Lightning via Hugging Face API"""
    
    def __init__(self):
        self.hf_api_key = os.getenv("HUGGINGFACE_API_KEY")
        self.base_url = "https://api-inference.huggingface.co/models"
        
        # SDXL Lightning models (ultra-fast)
        self.models = {
            "sdxl-lightning-2step": "ByteDance/SDXL-Lightning",
            "sdxl-lightning-4step": "ByteDance/SDXL-Lightning", 
            "sdxl-lightning-8step": "ByteDance/SDXL-Lightning"
        }
        
        self.headers = {
            "Authorization": f"Bearer {self.hf_api_key}",
            "Content-Type": "application/json"
        }
    
    async def generate_image(
        self,
        prompt: str,
        model: str = "sdxl-lightning-2step",
        width: int = 1024,
        height: int = 1024,
        num_inference_steps: int = 2,
        guidance_scale: float = 1.0,
        seed: Optional[int] = None,
        email_to: Optional[str] = None,
        save_locally: bool = False
    ) -> Dict[str, Any]:
        """Generate image using SDXL Lightning model"""
        
        # Determine steps based on model
        if "2step" in model:
            num_inference_steps = 2
        elif "4step" in model:
            num_inference_steps = 4
        elif "8step" in model:
            num_inference_steps = 8
        
        model_id = self.models.get(model, self.models["sdxl-lightning-2step"])
        url = f"{self.base_url}/{model_id}"
        
        # Prepare payload for SDXL Lightning
        payload = {
            "inputs": prompt,
            "parameters": {
                "width": width,
                "height": height,
                "num_inference_steps": num_inference_steps,
                "guidance_scale": guidance_scale
            }
        }
        
        if seed:
            payload["parameters"]["seed"] = seed
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            try:
                response = await client.post(url, headers=self.headers, json=payload)
                
                if response.status_code == 200:
                    # HF API returns image bytes directly
                    image_bytes = response.content
                    
                    result = {
                        "success": True,
                        "size_bytes": len(image_bytes),
                        "model": model_id,
                        "prompt": prompt,
                        "dimensions": f"{width}x{height}",
                        "steps": num_inference_steps
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
                        import base64
                        result["image_base64"] = base64.b64encode(image_bytes).decode('utf-8')
                        result["message"] = "Image generated (not saved locally - use email_to parameter for Railway deployment)"
                    
                    return result
                elif response.status_code == 503:
                    # Model is loading
                    estimated_time = response.json().get("estimated_time", 20)
                    return {
                        "success": False,
                        "error": f"SDXL Lightning model is loading, estimated time: {estimated_time}s. Please try again.",
                        "retry_after": estimated_time
                    }
                else:
                    error_detail = response.text
                    return {
                        "success": False,
                        "error": f"SDXL Lightning API error {response.status_code}: {error_detail}"
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
        filename = f"sdxl_{safe_model}_{timestamp}_{image_id}.png"
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
            filename = f"sdxl_{safe_model}_{timestamp}.png"
            
            # Create attachment
            attachment = {
                "filename": filename,
                "content": base64.b64encode(image_bytes).decode('utf-8')
            }
            
            # Send email
            email_params = {
                "from": "EVA Agent <onboarding@resend.dev>",
                "to": [email_to],
                "subject": f"SDXL Lightning Generated Image: {model}",
                "html": f"""
                <h2>⚡ SDXL Lightning Image Generated</h2>
                <p><strong>Model:</strong> {model}</p>
                <p><strong>Prompt:</strong> {prompt}</p>
                <p><strong>Size:</strong> {len(image_bytes):,} bytes</p>
                <p>Generated with SDXL Lightning via EVA Agent</p>
                """,
                "attachments": [attachment]
            }
            
            email_response = resend.Emails.send(email_params)
            
            return {
                "email_sent": True,
                "email_to": email_to,
                "email_id": email_response.get("id", "unknown"),
                "filename": filename,
                "message": f"SDXL Lightning image emailed to {email_to}"
            }
            
        except Exception as e:
            return {"error": f"Email failed: {str(e)}"}
    
    async def generate_with_retry(self, prompt: str, model: str = "sdxl-lightning-2step", max_retries: int = 3, email_to: Optional[str] = None, save_locally: bool = False) -> Dict[str, Any]:
        """Generate image with automatic retry for model loading"""
        
        for attempt in range(max_retries):
            result = await self.generate_image(prompt, model, email_to=email_to, save_locally=save_locally)
            
            if result["success"]:
                return result
            
            if "retry_after" in result:
                wait_time = min(result["retry_after"], 30)  # Cap at 30 seconds
                print(f"SDXL Lightning model loading, waiting {wait_time}s... (attempt {attempt + 1}/{max_retries})")
                await asyncio.sleep(wait_time)
                continue
            else:
                # Other error, don't retry
                return result
        
        return {
            "success": False,
            "error": f"Failed after {max_retries} attempts"
        }

# Example usage
async def test_sdxl():
    """Test SDXL Lightning image generation"""
    handler = SDXLLightningHandler()
    
    prompt = "portrait of a friendly AI assistant with digital features"
    
    result = await handler.generate_with_retry(prompt, "sdxl-lightning-2step")
    
    if result["success"]:
        print(f"✅ Image generated: {result.get('filename', 'temp')}")
        print(f"📏 Size: {result['size_bytes']} bytes")
        print(f"⚡ Steps: {result['steps']}")
    else:
        print(f"❌ Error: {result['error']}")

if __name__ == "__main__":
    asyncio.run(test_sdxl())