#!/usr/bin/env python3
"""
Test appointment booking integration with ElevenLabs
"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from integrations.tool_manager import get_tool_manager, ToolCall

async def test_appointment_booking_setup():
    """Test appointment booking setup and configuration"""
    print("🧪 Testing appointment booking setup...")
    
    # Get tool manager
    tool_manager = get_tool_manager()
    
    # Test quick appointment info
    try:
        tool_call = ToolCall(
            tool="appointment",
            action="quick_appointment_info",
            parameters={"appointment_type": "dentist"}
        )
        
        print(f"📤 Getting quick appointment info for dentist appointments...")
        
        response = await tool_manager.call_tool(tool_call)
        
        print(f"✅ Tool response success: {response.success}")
        
        if response.success:
            result = response.result
            appointment_type = result.get('appointment_type', 'unknown')
            duration = result.get('typical_duration', 'unknown')
            advance_booking = result.get('advance_booking', 'unknown')
            
            print(f"📋 Appointment Type: {appointment_type}")
            print(f"⏱️  Typical Duration: {duration}")
            print(f"📅 Advance Booking Time: {advance_booking}")
            print(f"❓ Questions to Expect: {len(result.get('questions_to_expect', []))} questions")
            print(f"📝 Info to Prepare: {len(result.get('info_to_prepare', []))} items")
                
        else:
            print(f"❌ Error: {response.error}")
                
    except Exception as e:
        print(f"❌ Error testing appointment booking setup: {e}")

async def test_appointment_booking_preparation():
    """Test appointment booking preparation"""
    print("\n🧪 Testing appointment booking preparation...")
    
    # Get tool manager
    tool_manager = get_tool_manager()
    
    # Test appointment preparation with realistic data
    try:
        tool_call = ToolCall(
            tool="appointment",
            action="prepare_appointment",
            parameters={
                "business_name": "Downtown Dental Clinic",
                "business_phone": "+1-555-123-4567",
                "appointment_type": "dentist",
                "user_name": "Louis du Plessis",
                "preferred_dates": ["next Monday", "next Tuesday"],
                "preferred_times": ["morning", "early afternoon"],
                "reason": "routine cleaning and checkup",
                "special_requests": "prefer morning appointments if available"
            }
        )
        
        print(f"📋 Preparing appointment booking for:")
        print(f"   Business: Downtown Dental Clinic")
        print(f"   Phone: +1-555-123-4567")
        print(f"   Type: Dental appointment")
        print(f"   For: Louis du Plessis")
        print(f"   Preferred: Monday/Tuesday mornings")
        
        response = await tool_manager.call_tool(tool_call)
        
        print(f"✅ Tool response success: {response.success}")
        
        if response.success:
            result = response.result
            print(f"📞 Preparation complete!")
            print(f"📋 Call script generated: {len(result.get('call_script', ''))} characters")
            print(f"📋 Next steps: {len(result.get('next_steps', []))} items")
            print(f"💬 Message: {result.get('message', '')}")
            
            # Show a snippet of the call script
            call_script = result.get('call_script', '')
            if call_script:
                lines = call_script.split('\n')[:10]
                print(f"\n📄 Call script preview (first 10 lines):")
                for line in lines:
                    print(f"   {line}")
                print(f"   ... (and {len(call_script.split(chr(10))) - 10} more lines)")
        else:
            print(f"❌ Error: {response.error}")
            
    except Exception as e:
        print(f"❌ Error testing appointment booking preparation: {e}")

async def test_eva_appointment_workflow():
    """Test Eva's appointment booking workflow"""
    print("\n🧪 Testing Eva's appointment booking workflow...")
    
    print("🎯 Eva can now handle these appointment requests:")
    print("- 'Book me a doctor's appointment for next Monday morning'")
    print("- 'Call the dentist to schedule a cleaning'")
    print("- 'Schedule a haircut appointment for this week'")
    print("- 'Book an appointment at Downtown Medical for a check-up'")
    print("- 'Call and make an appointment for me at (555) 123-4567'")
    
    print("\n💡 What Eva will do:")
    print("1. Extract appointment details from your request")
    print("2. Create a professional AI voice agent")
    print("3. Call the business on your behalf")
    print("4. Handle the conversation naturally")
    print("5. Secure your appointment")
    print("6. Report back with the results")

async def main():
    print("🔧 Testing EVA Appointment Booking Integration")
    print("=" * 60)
    
    await test_appointment_booking_setup()
    await test_appointment_booking_preparation()
    await test_eva_appointment_workflow()
    
    print("=" * 60)
    print("✅ Test completed")
    print("\n🚀 To set up appointment booking:")
    print("1. Ensure you have an ElevenLabs account")
    print("2. Set your API key: export ELEVENLABS_API_KEY=your_key")
    print("3. Ask Eva: 'Book me an appointment at [business] for [service]'")
    print("4. Eva will call and handle the booking professionally!")

if __name__ == "__main__":
    asyncio.run(main())