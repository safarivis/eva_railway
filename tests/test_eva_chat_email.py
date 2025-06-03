"""
Test Eva's email orchestration through chat
"""
import asyncio
import httpx
import json

async def test_eva_email_chat():
    """Test Eva handling email requests through chat"""
    
    print("🤖 Testing Eva Email Orchestration\n")
    
    # Test the simple chat endpoint
    async with httpx.AsyncClient() as client:
        # Test 1: Send email request
        print("1. Testing email send through Eva:")
        response = await client.post(
            "http://localhost:8000/api/chat-simple",
            json={
                "message": "Send an email to louisrdup@gmail.com saying 'This is a test from Eva orchestration'",
                "user_id": "test_user",
                "context": "general",
                "mode": "assistant"
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Eva responded: {result.get('response', 'No response')[:200]}...")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
        
        print("\n2. Testing inbox check (will fail without Gmail agent):")
        response = await client.post(
            "http://localhost:8000/api/chat-simple",
            json={
                "message": "Check my inbox for recent emails",
                "user_id": "test_user",
                "context": "general",
                "mode": "assistant"
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"Eva responded: {result.get('response', 'No response')[:200]}...")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")


async def check_eva_running():
    """Check if Eva is running"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/")
            return response.status_code == 200
    except:
        return False


if __name__ == "__main__":
    print("Checking if Eva is running...")
    if asyncio.run(check_eva_running()):
        print("✅ Eva is running on port 8000\n")
        asyncio.run(test_eva_email_chat())
    else:
        print("❌ Eva is not running!")
        print("\nTo start Eva:")
        print("cd /home/ldp/louisdup/agents/eva_agent")
        print("python core/eva.py")
        print("\nOr use the run script:")
        print("./scripts/run_eva.sh")