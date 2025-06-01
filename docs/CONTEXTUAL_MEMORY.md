# Contextual Memory System for EVA Agent

This document explains the enhanced contextual memory system that allows separation of work/personal concerns and different agent modes.

## Overview

The contextual memory system provides:

1. **Context Separation**: Keep work, personal, creative, and research conversations separate
2. **Mode-Based Behavior**: Different agent personalities for different tasks
3. **Persistent User Identity**: Your conversations are remembered across sessions
4. **Cross-Context Awareness**: Optional ability to reference related contexts

## Memory Contexts

### Available Contexts

- **General**: Default context for everyday conversations
- **Work**: Professional and work-related discussions
- **Personal**: Private matters and personal life
- **Creative**: Creative projects, brainstorming, and artistic endeavors
- **Research**: Academic research, learning, and study topics

Each context maintains its own:
- Conversation history
- Entity relationships
- Temporal knowledge graph
- User preferences

### Context Isolation

By default, contexts are completely isolated. This means:
- Work conversations won't mix with personal ones
- Each context builds its own understanding of you
- Privacy is maintained between contexts

## Agent Modes

### Available Modes

1. **Assistant** (Default)
   - Professional, helpful, and efficient
   - Focus on clear, actionable responses

2. **Coach**
   - Supportive life and career coaching
   - Asks reflective questions
   - Focuses on personal growth

3. **Tutor**
   - Educational approach
   - Breaks down complex topics
   - Checks understanding

4. **Advisor**
   - Professional analysis
   - Balanced recommendations
   - Risk/benefit assessment

5. **Friend**
   - Casual, empathetic conversation
   - More personal engagement
   - Relaxed tone

6. **Analyst**
   - Data-focused responses
   - Structured analysis
   - Pattern recognition

7. **Creative**
   - Innovative thinking
   - Brainstorming partner
   - Out-of-the-box ideas

## Using Contextual Memory

### Web Interface

Access the contextual interface at: `http://localhost:8000/static/index_contextual.html`

1. **Set Your User ID**: A unique ID is auto-generated or you can set your own
2. **Choose Context**: Select the appropriate context for your conversation
3. **Select Mode**: Pick the agent mode that fits your needs
4. **Start Chatting**: Your conversation will be remembered in that context

### API Usage

When creating a new run, include context and mode:

```json
POST /agents/eva/runs
{
  "messages": [{"role": "user", "content": "Hello"}],
  "context": "work",
  "mode": "advisor",
  "user_id": "john_doe_123"
}
```

### CLI Usage

To use contexts with the CLI client, you'll need to modify it to support the new parameters:

```python
# Example modification for cli_client.py
async def create_run(message, context="general", mode="assistant", user_id=None):
    data = {
        "messages": [{"role": "user", "content": message}],
        "stream": True,
        "context": context,
        "mode": mode,
        "user_id": user_id
    }
    # ... rest of the code
```

## Memory Management

### How It Works

1. **User Creation**: Each context creates a separate user profile (e.g., `john_work`, `john_personal`)
2. **Session Tracking**: Sessions are tagged with context and mode metadata
3. **Memory Retrieval**: Only relevant context memory is loaded for each conversation
4. **Temporal Awareness**: Tracks when facts were learned and when they changed

### Cross-Context Features

While contexts are isolated by default, you can enable cross-context awareness:

- **Work + Research**: Work context can reference your research findings
- **Creative + Personal**: Creative projects can consider personal preferences
- **Configurable**: You control which contexts can share information

## API Endpoints

### Context Information

```bash
GET /api/contexts
# Returns available contexts and modes with descriptions
```

### User Context Summary

```bash
GET /api/users/{user_id}/contexts
# Shows which contexts have been used by a user
```

### Switch Context Mid-Conversation

```bash
POST /api/runs/{run_id}/switch_context
{
  "context": "personal",
  "mode": "friend"
}
```

## Best Practices

### Context Selection

- **Work Context**: Project discussions, professional advice, work-related planning
- **Personal Context**: Life planning, personal goals, private matters
- **Creative Context**: Writing projects, art ideas, creative brainstorming
- **Research Context**: Learning new topics, academic work, investigations

### Mode Selection

- Use **Coach** mode for personal development conversations
- Use **Tutor** mode when learning new skills
- Use **Analyst** mode for data-heavy discussions
- Use **Friend** mode for casual chats

### Privacy Tips

1. **Consistent Context Use**: Always use the same context for related topics
2. **User ID Management**: Use the same user ID across devices for continuity
3. **Context Switching**: Be mindful when switching contexts mid-conversation

## Examples

### Work Context with Advisor Mode

```
Context: Work
Mode: Advisor

User: "I'm considering switching to a management role"
EVA: "Let me analyze this career transition for you. Based on our previous discussions about your technical expertise and project leadership experience, here are the key considerations..."
```

### Personal Context with Coach Mode

```
Context: Personal  
Mode: Coach

User: "I want to improve my work-life balance"
EVA: "I remember you mentioning feeling overwhelmed last month. What specific aspects of balance are most challenging for you right now? Let's explore what an ideal balance would look like for you..."
```

### Creative Context with Creative Mode

```
Context: Creative
Mode: Creative

User: "I need ideas for my sci-fi novel"
EVA: "Building on the cyberpunk themes we explored last week, what if we blend in some biopunk elements? Imagine a world where your protagonist's neural implants start developing their own ecosystem..."
```

## Technical Details

### Storage Structure

Each user-context combination creates:
- Separate Zep user profile
- Isolated conversation sessions
- Independent knowledge graphs
- Context-specific metadata

### Performance

- Context switching is instant
- Memory retrieval adds <100ms latency
- Each context can scale independently
- No performance penalty for multiple contexts

## Troubleshooting

### Context Not Remembering

1. Check you're using the same user ID
2. Verify you're in the correct context
3. Ensure Zep is properly initialized

### Mode Not Applying

1. Confirm the mode is set in the request
2. Check for mode-specific instructions in responses
3. Verify the session has the correct mode metadata

### Cross-Context Not Working

1. This feature requires additional configuration
2. Check if contexts are properly linked
3. Verify permissions for context sharing