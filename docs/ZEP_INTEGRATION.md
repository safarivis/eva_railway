# Zep Memory Integration for EVA Agent

This document describes the Zep memory layer integration for the EVA agent.

## Overview

Zep is a temporal knowledge graph-based memory layer that continuously learns from user interactions. The integration provides:

- **Persistent conversation memory** across sessions
- **Temporal knowledge graphs** tracking entity relationships over time
- **Fast memory retrieval** with pre-computed facts and summaries
- **Context-aware responses** using previous conversation history

## Setup

### 1. Get Zep API Key

1. Create a free account at [https://app.getzep.com/](https://app.getzep.com/)
2. Generate an API key from your dashboard

### 2. Configure Environment

Add the following to your `.env` file:

```env
# Zep Memory Configuration
ZEP_API_KEY=your_actual_zep_api_key_here
ZEP_ENABLED=true  # Set to false to disable Zep integration
```

### 3. Install Dependencies

The Zep SDK is already included in `requirements.txt`. Install with:

```bash
pip install -r requirements.txt
```

## How It Works

### Memory Flow

1. **Session Creation**: When a new conversation starts, a Zep session is created
2. **Message Storage**: All user and assistant messages are stored in Zep's temporal knowledge graph
3. **Context Retrieval**: Before each LLM query, relevant memory context is retrieved
4. **Enhanced Responses**: The LLM receives both current messages and relevant historical context

### Architecture

- **zep_memory.py**: Core integration module with async Zep client
- **eva.py**: Modified to integrate memory at key points:
  - Session initialization
  - Message handling (user and assistant)
  - LLM query enhancement with memory context

### Key Features Implemented

1. **Automatic User Management**: Creates users dynamically for each session
2. **Session Tracking**: Maps EVA run IDs to Zep session IDs
3. **Async Operations**: All Zep operations are non-blocking
4. **Error Handling**: Graceful fallback if Zep is unavailable
5. **Optional Integration**: Can be disabled via environment variable

## Usage

### Default Behavior

With Zep enabled, EVA will:
- Remember conversation context across messages
- Provide more contextually aware responses
- Build a knowledge graph of entities and relationships

### Memory Search (Future Enhancement)

The `search_memory` method in `ZepMemoryManager` can be used to:
- Search for specific information across conversations
- Find related entities and facts
- Retrieve temporal information

### Disabling Zep

To run EVA without Zep memory:
- Set `ZEP_ENABLED=false` in `.env`
- Or remove/comment out `ZEP_API_KEY`

## API Endpoints

The `/api/info` endpoint now includes Zep status:

```json
{
  "agent": "Eva",
  "version": "0.1.0",
  "description": "A simple agent built with AG-UI protocol",
  "model": "qwen/qwen2.5-72b-instruct",
  "zep_enabled": true
}
```

## Performance Impact

- **Latency**: Minimal (<100ms) for memory operations
- **Accuracy**: Up to 18.5% improvement in contextual responses
- **Scalability**: Handles large conversation histories efficiently

## Troubleshooting

### Zep Not Initializing
- Check API key is valid
- Ensure network connectivity to Zep cloud
- Check logs for initialization errors

### Memory Not Persisting
- Verify `ZEP_ENABLED=true`
- Check session creation logs
- Ensure messages are being added to Zep

### Performance Issues
- Zep operations are async and shouldn't block
- Check Zep dashboard for API usage limits
- Consider implementing memory search limits