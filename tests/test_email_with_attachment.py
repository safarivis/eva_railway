#!/usr/bin/env python3
"""
Test email with attachment functionality directly
"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from integrations.tool_manager import get_tool_manager, ToolCall

async def test_email_with_attachment():
    """Test sending email with a known image attachment"""
    print("🧪 Testing email with attachment functionality...")
    
    # Get tool manager
    tool_manager = get_tool_manager()
    
    # First check if we have any generated images to use
    import glob
    image_files = glob.glob("/home/ldp/eva/media/eva/generated_*.png")
    if not image_files:
        print("❌ No generated images found. Run image generation test first.")
        return False
    
    # Use the most recent image
    latest_image = max(image_files, key=os.path.getctime)
    print(f"📁 Using image: {latest_image}")
    print(f"📊 Image size: {os.path.getsize(latest_image)} bytes")
    
    try:
        # Test email with attachment
        tool_call = ToolCall(
            tool="email",
            action="send",
            parameters={
                "to": ["louisrdup@gmail.com"],
                "subject": "Test Email with Generated Image Attachment",
                "body": f"Hello! This is a test email with the generated image attached. The image is located at: {latest_image}",
                "cc": None,
                "bcc": None,
                "attachments": [latest_image]  # File path to attach
            }
        )
        
        print(f"📤 Sending email with attachment: {os.path.basename(latest_image)}")
        
        response = await tool_manager.call_tool(tool_call)
        
        print(f"✅ Email tool response success: {response.success}")
        
        if response.success:
            result = response.result
            print(f"📧 Email sent successfully!")
            print(f"📬 Message ID: {result.get('message_id', 'unknown')}")
            print(f"📨 Recipients: {result.get('to', [])}")
            print(f"💌 Subject: {result.get('subject', '')}")
        else:
            print(f"❌ Email sending failed: {response.error}")
            
        return response.success
            
    except Exception as e:
        print(f"❌ Error testing email with attachment: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function"""
    print("🔧 Testing email attachment functionality")
    print("=" * 50)
    
    success = await test_email_with_attachment()
    
    print("=" * 50)
    if success:
        print("✅ Email with attachment sent successfully! Check your inbox.")
    else:
        print("❌ Email test failed")

if __name__ == "__main__":
    asyncio.run(main())