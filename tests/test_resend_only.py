"""
Quick test for Resend email sending
"""
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def test_resend():
    """Test Resend email sending"""
    try:
        import resend
        resend.api_key = os.getenv("RESEND_API_KEY")
        
        print("🚀 Testing Resend Email Send")
        print(f"API Key: {resend.api_key[:10]}...")
        
        # Send test email
        params = {
            "from": "Eva Agent <onboarding@resend.dev>",
            "to": ["louisrdup@gmail.com"],
            "subject": "Test from Eva Agent",
            "text": "This is a test email from Eva Agent using Resend!",
            "html": "<p>This is a <strong>test email</strong> from Eva Agent using Resend!</p>"
        }
        
        print("\nSending email...")
        result = resend.Emails.send(params)
        
        print(f"✅ Success! Email ID: {result.get('id')}")
        print(f"Full result: {result}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"Error type: {type(e).__name__}")

if __name__ == "__main__":
    asyncio.run(test_resend())