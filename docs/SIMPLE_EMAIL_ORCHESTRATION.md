# Eva Email Orchestration - Simple Setup

Eva can orchestrate email operations using your existing email agents:
- **Resend** for sending emails (fast & reliable)
- **Gmail agent** for reading, searching, and managing inbox

## How It Works

```
You: "Send an email to john about the meeting"
Eva: [Understands request] → [Calls Resend API] → "Email sent!"

You: "Check my inbox"
Eva: [Understands request] → [Calls Gmail agent] → "You have 5 new emails..."
```

## Current Setup

### 1. Resend (for sending)
- ✅ API key configured: `re_cVueKT1X_PqjhBhgR4sj8JdJK9Us8iFpR`
- ✅ Using test domain: `onboarding@resend.dev`
- ✅ Falls back to Gmail if needed

### 2. Gmail Agent (for everything else)
- List emails
- Read specific emails  
- Search emails
- Manage labels

## Quick Test

```bash
cd /home/ldp/louisdup/agents/eva_agent
python tests/test_eva_email_orchestration.py
```

## Usage Examples

### Through Eva Chat/Voice:

```
"Send an email to sarah@example.com saying the report is ready"
"Show me emails from yesterday"
"Search for emails about invoices"
"Read the latest email from John"
```

## Adding More Tools

The tool manager is designed to be modular. To add a new tool:

1. Create a handler in `tool_manager.py`:
```python
class CalendarToolHandler:
    async def handle_call(self, action: str, parameters: Dict[str, Any]) -> ToolResponse:
        # Your calendar logic here
```

2. Register it:
```python
self.handlers["calendar"] = CalendarToolHandler()
```

3. Eva automatically understands the new tool!

## Architecture Benefits

- ✅ **Simple**: Direct API calls, no complex SDKs
- ✅ **Modular**: Easy to add/remove tools
- ✅ **Reliable**: Each tool is independent
- ✅ **Fast**: Minimal overhead
- ✅ **Maintainable**: You control the code

## Next Steps

1. **Gmail Agent**: Make sure it's running:
   ```bash
   cd /path/to/email-gateway-agent
   npm start
   ```

2. **Production Domain**: For production, set up your own domain with Resend

3. **Add More Agents**: Follow the same pattern for calendar, file access, etc.

## Security Notes

- Never commit API keys to git
- Use environment variables
- Validate all inputs
- Log operations for audit

That's it! Eva can now orchestrate emails through simple, direct integrations.