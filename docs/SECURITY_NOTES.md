# Security Notes for Eva Agent

## API Key Management

**IMPORTANT**: The `.env` file contains sensitive API keys. Please ensure:

1. **Never commit `.env` to version control**
   - Add `.env` to `.gitignore`
   - Use environment variables in production

2. **Rotate keys regularly**
   - OpenAI API key
   - Resend API key
   - Zep API key
   - ElevenLabs API key

3. **Use separate keys for development and production**

## Email Security

### Resend Configuration
- Currently using Resend's shared test domain (`onboarding@resend.dev`)
- For production, verify your own domain with Resend
- Update the "from" address in `tool_manager.py`

### Gmail Integration
- Ensure Gmail agent runs on localhost only
- Use OAuth2 for production Gmail access
- Never expose Gmail service publicly without authentication

## Tool Access Security

### File Access
- File tool is restricted to current working directory
- Add allowed paths carefully in `FileToolHandler`
- Never allow access to system directories

### Email Operations
- Validate email addresses before sending
- Implement rate limiting for email sends
- Log all email operations for audit

## Production Checklist

- [ ] Move API keys to secure environment variables
- [ ] Set up proper domain for email sending
- [ ] Implement authentication for tool access
- [ ] Add rate limiting to prevent abuse
- [ ] Enable comprehensive logging
- [ ] Set up monitoring and alerts
- [ ] Regular security audits

## Recommended .gitignore entries

```
.env
.env.local
.env.*.local
*.key
*.pem
```