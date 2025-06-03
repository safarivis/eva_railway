"""
Test script for Eva's Pipedream Connect orchestration
Demonstrates access to thousands of APIs through a single SDK
"""
import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import Eva's Pipedream orchestrator
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from integrations.pipedream_orchestrator import get_pipedream_orchestrator


async def test_pipedream_apps():
    """Test available Pipedream apps and actions"""
    
    print("🚀 Eva Pipedream Connect Test\n")
    
    # Get the orchestrator
    orchestrator = get_pipedream_orchestrator()
    
    print("Available Pipedream Apps:")
    apps = orchestrator.get_available_apps()
    for app in apps:
        print(f"\n📱 {app.name} ({app.slug})")
        print(f"   {app.description}")
        
        # Show available actions
        actions = orchestrator.get_app_actions(app.slug)
        if actions:
            print("   Actions:")
            for action_name, action_desc in actions.items():
                print(f"   • {action_name}: {action_desc}")
    
    print("\n" + "="*60 + "\n")


async def test_gmail_operations():
    """Test Gmail operations through Pipedream"""
    
    print("📧 Testing Gmail Integration\n")
    
    orchestrator = get_pipedream_orchestrator()
    
    # Test 1: List emails
    print("1. List inbox emails:")
    result = await orchestrator.execute_action(
        app_slug="gmail",
        action="list",
        params={"limit": 5}
    )
    print(f"   Result: {result['success']}")
    if result['success']:
        print(f"   {result['result']['message']}")
    print()
    
    # Test 2: Send email (will use Resend primary, Pipedream fallback)
    print("2. Send email:")
    result = await orchestrator.execute_action(
        app_slug="gmail",
        action="send",
        params={
            "to": ["test@example.com"],
            "subject": "Test from Eva via Pipedream",
            "body": "This email was sent by Eva using Pipedream Connect!"
        }
    )
    print(f"   Result: {result['success']}")
    if result['success']:
        print(f"   Provider: {result['result'].get('provider', 'pipedream')}")
    print()
    
    # Test 3: Search emails
    print("3. Search emails:")
    result = await orchestrator.execute_action(
        app_slug="gmail",
        action="search",
        params={
            "query": "important",
            "limit": 3
        }
    )
    print(f"   Result: {result['success']}")
    print()


async def test_multi_app_workflow():
    """Test a workflow using multiple Pipedream apps"""
    
    print("🔄 Multi-App Workflow Test\n")
    
    orchestrator = get_pipedream_orchestrator()
    
    # Simulate a workflow: Read email → Create Notion page → Send Slack notification
    print("Workflow: Email → Notion → Slack\n")
    
    # Step 1: Search for project emails
    print("1. Search Gmail for project updates:")
    gmail_result = await orchestrator.execute_action(
        app_slug="gmail",
        action="search",
        params={"query": "project update", "limit": 1}
    )
    print(f"   Found emails: {gmail_result['success']}")
    
    # Step 2: Create Notion page
    print("\n2. Create Notion page for project:")
    notion_result = await orchestrator.execute_action(
        app_slug="notion",
        action="create_page",
        params={
            "title": "Project Update Summary",
            "content": "Summary of recent project emails"
        }
    )
    print(f"   Page created: {notion_result['success']}")
    
    # Step 3: Send Slack notification
    print("\n3. Send Slack notification:")
    slack_result = await orchestrator.execute_action(
        app_slug="slack",
        action="send_message",
        params={
            "channel": "#projects",
            "text": "New project update summary created in Notion!"
        }
    )
    print(f"   Message sent: {slack_result['success']}")
    
    print("\n✅ Workflow completed!")


async def test_eva_conversation():
    """Simulate Eva handling various Pipedream-powered requests"""
    
    print("\n💬 Simulating Eva Conversations\n")
    
    orchestrator = get_pipedream_orchestrator()
    
    # Simulate various user requests
    conversations = [
        {
            "user": "Check my Gmail inbox",
            "app": "gmail",
            "action": "list",
            "params": {"limit": 5}
        },
        {
            "user": "Create a new document in Google Drive",
            "app": "google_drive",
            "action": "create_file",
            "params": {"name": "Meeting Notes.txt", "content": "Today's meeting notes..."}
        },
        {
            "user": "Send a Slack message to the team channel",
            "app": "slack",
            "action": "send_message",
            "params": {"channel": "#team", "text": "Great work everyone!"}
        },
        {
            "user": "Play some music on Spotify",
            "app": "spotify",
            "action": "play",
            "params": {"query": "relaxing jazz"}
        }
    ]
    
    for conv in conversations:
        print(f"User: {conv['user']}")
        print(f"Eva: I'll help you with that...")
        
        result = await orchestrator.execute_action(
            app_slug=conv['app'],
            action=conv['action'],
            params=conv['params']
        )
        
        if result['success']:
            print(f"     ✓ {result['result']['message']}")
        else:
            print(f"     ✗ Error: {result.get('error', 'Unknown error')}")
        print()


async def test_connect_flow():
    """Test the OAuth connection flow"""
    
    print("🔐 OAuth Connection Flow Test\n")
    
    orchestrator = get_pipedream_orchestrator()
    
    # Simulate connecting a new app
    print("Connecting Gmail for user 'eva_user_123':")
    result = await orchestrator.connect_app(
        app_slug="gmail",
        user_id="eva_user_123"
    )
    
    if result['success']:
        print(f"✓ Auth URL generated: {result['auth_url'][:50]}...")
        print(f"  Message: {result['message']}")
    else:
        print(f"✗ Error: {result['error']}")


if __name__ == "__main__":
    print("="*60)
    print("Eva + Pipedream Connect Integration Test")
    print("="*60)
    
    # Run all tests
    asyncio.run(test_pipedream_apps())
    asyncio.run(test_gmail_operations())
    asyncio.run(test_multi_app_workflow())
    asyncio.run(test_eva_conversation())
    asyncio.run(test_connect_flow())
    
    print("\n" + "="*60)
    print("✅ All tests completed!")
    print("\nNext steps:")
    print("1. Create an OAuth client in Pipedream dashboard")
    print("2. Add the client ID to your .env file")
    print("3. Connect apps through Pipedream Connect")
    print("4. Eva will have access to thousands of APIs!")
    print("="*60)