"""
Test Eva API directly with tool calling
"""
import httpx
import asyncio

async def test_eva_api():
    """Test Eva's API with a direct tool-calling prompt"""
    
    print("🤖 Testing Eva API with explicit tool instructions\n")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Create a more explicit prompt that should trigger tool use
        response = await client.post(
            "http://localhost:8000/api/chat-simple",
            json={
                "message": "Please use the email tool to send an email to louisrdup@gmail.com with subject 'Test from Eva' and body 'This is a test email sent through Eva's email tool.'",
                "user_id": "test_user",
                "context": "general", 
                "mode": "assistant"
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"Eva's response:\n{result.get('response', 'No response')}")
        else:
            print(f"Error: {response.status_code}")
            print(response.text)

if __name__ == "__main__":
    asyncio.run(test_eva_api())