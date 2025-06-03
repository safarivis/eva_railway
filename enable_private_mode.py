#!/usr/bin/env python3
"""
Quick script to enable private mode for EVA
"""
import httpx
import asyncio

async def enable_private_mode():
    """Enable private mode via API"""
    user_id = "your_user_id"  # Change this to your actual user ID
    password = "eva2415!"
    
    async with httpx.AsyncClient() as client:
        # Enable private mode
        response = await client.post(
            f"http://localhost:8000/api/users/{user_id}/contexts/personal/password",
            json={"password": password}
        )
        
        if response.status_code == 200:
            print("✅ Private mode enabled successfully!")
            print("Personal context now requires password.")
        else:
            print(f"❌ Error: {response.text}")

if __name__ == "__main__":
    print("🔐 Enabling EVA Private Mode...")
    print("Password: eva2415!")
    asyncio.run(enable_private_mode())