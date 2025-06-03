# Eva Email Orchestration

Eva can now orchestrate email operations through natural language commands, using Resend for sending emails and Gmail for all other email operations.

## Architecture

Eva acts as an intelligent orchestrator that:
1. Understands natural language requests about emails
2. Routes operations to the appropriate service (Resend or Gmail)
3. Handles responses and presents them conversationally

## How It Works

### Tool Calling System

Eva uses OpenAI's function calling feature to determine when and how to use tools:

```python
# When you say: "Send an email to john@example.com about the meeting"
# Eva understands and calls:
ToolCall(
    tool="email",
    action="send",
    parameters={
        "to": ["john@example.com"],
        "subject": "Meeting Information",
        "body": "Here are the details about our meeting..."
    }
)
```

### Email Services

1. **Resend (Primary for Sending)**
   - Fast, reliable email delivery
   - HTML email support
   - Delivery tracking
   - Falls back to Gmail if needed

2. **Gmail (All Other Operations)**
   - List inbox
   - Read emails
   - Search emails
   - Manage labels

## Usage Examples

### Through Chat/Voice

```
You: "Check my inbox"
Eva: "I'll check your inbox for you... Found 5 recent emails:
     - From: client@company.com - Subject: Project Update
     - From: team@work.com - Subject: Meeting Tomorrow
     ..."

You: "Send an email to sarah@example.com saying the report is ready"
Eva: "I'll send that email for you... Email sent successfully!"

You: "Search for emails about invoices"
Eva: "I'll search for emails about invoices... Found 3 matching emails..."
```

### Tool Configuration

The tool system is configured in `integrations/tool_manager.py`:

```python
class ToolManager:
    def __init__(self):
        self.handlers = {
            "email": EmailToolHandler(),
            "file": FileToolHandler(),
            "web_search": WebSearchToolHandler(),
        }
```

## Setup Requirements

### 1. Environment Variables

Add to your `.env` file:

```bash
# Resend API (for sending emails)
RESEND_API_KEY=your_resend_api_key

# Gmail Service URL (for other operations)
GMAIL_SERVICE_URL=http://localhost:3000

# OpenAI (Eva's brain)
OPENAI_API_KEY=your_openai_api_key
```

### 2. Resend Setup

1. Sign up at [resend.com](https://resend.com)
2. Verify your domain or use their test domain
3. Get your API key
4. Add to `.env` file

### 3. Gmail Agent Setup

Run the Gmail agent service (from the email gateway agent):

```bash
cd /path/to/email-gateway-agent
npm install
npm start
```

## Adding New Tools

Eva's tool system is modular. To add a new tool:

1. Create a handler class:
```python
class MusicToolHandler:
    async def handle_call(self, action: str, parameters: Dict[str, Any]) -> ToolResponse:
        if action == "play":
            # Implement music playing logic
            pass
```

2. Register in ToolManager:
```python
self.handlers["music"] = MusicToolHandler()
```

3. Add tool description:
```python
self.tool_descriptions["music"] = {
    "description": "Control music playback",
    "actions": {
        "play": "Play a song or playlist",
        "pause": "Pause current playback",
        "next": "Skip to next track"
    }
}
```

## Security Considerations

- File access is restricted to allowed directories
- Email sending requires authentication
- All tool calls are logged
- Sensitive operations require confirmation

## Future Enhancements

1. **Calendar Integration**
   - Schedule meetings from emails
   - Check availability
   - Send calendar invites

2. **Smart Email Composition**
   - Eva learns your writing style
   - Suggests responses
   - Handles follow-ups

3. **Email Analytics**
   - Response time tracking
   - Communication patterns
   - Priority detection

4. **Multi-Account Support**
   - Switch between email accounts
   - Unified inbox view
   - Cross-account search

## Testing

Run the test script to verify everything works:

```bash
cd eva_agent
python tests/test_eva_email_orchestration.py
```

## Troubleshooting

### Resend not working?
- Check API key is valid
- Verify domain is configured
- Check email from address

### Gmail operations failing?
- Ensure Gmail agent is running
- Check GMAIL_SERVICE_URL is correct
- Verify Gmail credentials

### Tool calls not recognized?
- Check OpenAI model supports function calling
- Verify tool schema is correct
- Check system prompt includes tool instructions