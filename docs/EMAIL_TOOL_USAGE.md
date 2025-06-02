# Email Tool Usage Guide

## Overview

EVA's email tool provides email sending capabilities through the Resend API. This tool is integrated into EVA's function calling system and can be accessed through natural language requests.

## Configuration

### Environment Variables
```bash
# Required
RESEND_API_KEY=your_resend_api_key

# Optional - Email service configuration
GMAIL_SERVICE_URL=http://localhost:3000  # Not currently used
```

### Resend Setup
1. Sign up at [resend.com](https://resend.com)
2. Get your API key from the dashboard
3. Add to your `.env` file as `RESEND_API_KEY`

## Usage

### Via Chat Interface

Ask EVA to send emails using natural language:

```
"send me a test email"
"use the email tool to send a message to someone@example.com"
"send an email with subject 'Meeting Notes' to colleague@company.com"
```

### Via API

```bash
curl -X POST http://localhost:8000/api/chat-simple \
  -H "Content-Type: application/json" \
  -d '{
    "message": "use the email tool to send me a test email",
    "user_id": "test_user",
    "context": "general",
    "mode": "assistant"
  }'
```

### Direct Tool Call

```python
from integrations.tool_manager import get_tool_manager, ToolCall

tool_manager = get_tool_manager()
result = await tool_manager.call_tool(
    ToolCall(
        tool='email',
        action='send',
        parameters={
            'to': ['recipient@example.com'],
            'subject': 'Test Email',
            'body': 'This is a test email from EVA'
        }
    )
)
```

## Tool Parameters

### Email Tool Schema

```json
{
  "tool": "email",
  "action": "send",
  "parameters": {
    "to": ["recipient@example.com"],           // Required: List of recipients
    "subject": "Email Subject",                // Required: Email subject
    "body": "Email content here",              // Required: Email body (text)
    "html": "<p>HTML content</p>",             // Optional: HTML version
    "cc": ["cc@example.com"],                  // Optional: CC recipients
    "bcc": ["bcc@example.com"]                 // Optional: BCC recipients
  }
}
```

### Response Format

```json
{
  "success": true,
  "result": {
    "message_id": "f0f9a42c-93cb-425d-a3f3-46f03f7a3938",
    "status": "sent",
    "to": ["recipient@example.com"],
    "subject": "Email Subject"
  },
  "error": null
}
```

## Technical Details

### From Address
- Uses Resend's verified domain: `Eva Agent <onboarding@resend.dev>`
- Can be overridden with custom verified domains

### Supported Actions
- **send**: Send an email via Resend API
- Other actions (read, list, search) are not currently supported

### Error Handling
- Invalid recipients: Returns error with details
- Missing API key: Returns configuration error
- Resend API errors: Returns detailed error message

## Examples

### Basic Email
```
User: "Send me a quick test email"
EVA: Uses email tool to send test email to configured user address
```

### Custom Email
```
User: "Send an email to john@company.com with subject 'Project Update' saying the project is on track"
EVA: Sends formatted email with specified parameters
```

### Multiple Recipients
```
User: "Send meeting notes to the team at team@company.com and manager@company.com"
EVA: Sends email to multiple recipients
```

## Troubleshooting

### Common Issues

1. **Domain verification error**
   - Ensure using Resend's verified domain for FROM address
   - Or verify your own domain in Resend dashboard

2. **API key not found**
   - Check `RESEND_API_KEY` in environment variables
   - Restart EVA server after adding the key

3. **EVA not calling email tool**
   - Use explicit language: "use the email tool"
   - Be specific about email addresses and content

### Debug Mode

Enable debug logging to see tool call details:
```python
import logging
logging.getLogger('integrations.tool_manager').setLevel(logging.DEBUG)
```

## Security Considerations

- API keys are stored in environment variables only
- No email content is logged in production
- Tool calls are audited in EVA's conversation logs
- File system access is restricted to prevent unauthorized email access

## Integration Architecture

```
EVA Core (OpenAI Function Calling)
    ↓
Tool Manager (integrations/tool_manager.py)
    ↓
Email Tool Handler (EmailToolHandler)
    ↓
Resend API (resend Python package)
    ↓
Email Delivery
```

## Future Enhancements

- [ ] Email reading capabilities (requires Gmail API or IMAP)
- [ ] Email templates and formatting
- [ ] Attachment support
- [ ] Email scheduling
- [ ] Custom domain configuration
- [ ] Email analytics and tracking