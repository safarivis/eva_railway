# Eva's Persistent Memory System

Eva now includes a comprehensive session persistence system that ensures conversations and memory contexts survive across restarts.

## Overview

The persistence system automatically:
- Saves all conversation sessions to disk
- Preserves Zep memory session mappings
- Restores recent sessions on startup
- Maintains user context across restarts
- Handles large conversation histories efficiently

## Key Features

### 1. Automatic Session Persistence
- All conversations are automatically saved to `data/sessions/`
- Sessions are saved after each user interaction
- Large conversations (>10 messages) are stored in separate files for performance

### 2. Session Restoration
- Recent sessions (last 24 hours) are automatically restored on startup
- Older sessions can be manually restored via API
- Sessions older than 30 days are automatically cleaned up

### 3. Zep Memory Integration
- Zep session IDs are persisted alongside Eva sessions
- Memory context is preserved across restarts
- Contextual memories (work/personal/creative) are maintained

### 4. User-Centric Design
- Sessions are organized by user ID
- Easy retrieval of all sessions for a specific user
- Export functionality for user data portability

## Architecture

### Session Persistence Module (`core/session_persistence.py`)
```python
SessionPersistence
├── sessions_file: active_sessions.json
├── zep_mappings_file: zep_mappings.json
└── conversation_history_dir/
    ├── session_id_1.json
    ├── session_id_2.json
    └── ...
```

### Data Storage Structure

#### Active Sessions File
```json
{
  "sessions": {
    "session_id": {
      "messages": [...],  // Last 10 messages
      "context": "work",
      "mode": "assistant",
      "base_user_id": "user_123",
      "created_at": "2024-01-01T10:00:00",
      "last_saved": "2024-01-01T11:30:00",
      "full_history_available": true
    }
  }
}
```

#### Zep Mappings File
```json
{
  "eva_session_id": "zep_session_id",
  ...
}
```

## API Endpoints

### Get User Sessions
```bash
GET /api/sessions/{user_id}
```
Returns all sessions for a specific user.

### Restore Session
```bash
POST /api/sessions/{session_id}/restore
```
Manually restore a persisted session to active memory.

### Export User Data
```bash
POST /api/users/{user_id}/export
```
Export all conversation data for a user.

### System Info
```bash
GET /api/info
```
Now includes persistence statistics:
- `persistence_enabled`: Always true
- `active_sessions`: Number of sessions in memory
- `persisted_sessions`: Total persisted sessions

## Usage Examples

### 1. Simple Chat with Persistence
```python
# First conversation
POST /api/chat-simple
{
  "message": "Hello Eva!",
  "user_id": "louis",
  "context": "general",
  "mode": "friend"
}

# Restart Eva...

# Continue conversation (automatically restored)
POST /api/chat-simple
{
  "message": "Do you remember what we talked about?",
  "user_id": "louis",
  "context": "general",
  "mode": "friend"
}
```

### 2. View User's Session History
```bash
curl http://localhost:8000/api/sessions/louis
```

### 3. Export User Data
```bash
curl -X POST http://localhost:8000/api/users/louis/export
```

## Implementation Details

### Modified Components

1. **eva.py**
   - Added session persistence initialization
   - Modified create_run to check for existing sessions
   - Updated all message handlers to save sessions
   - Added restore_sessions_on_startup()

2. **zep_memory.py**
   - Added create_or_get_session() method
   - Integrated with session persistence
   - Automatic Zep mapping restoration

3. **eva_voice_workflow.py**
   - Voice sessions are also persisted
   - Maintains context across voice interactions

### Performance Considerations

- Main session file only stores last 10 messages
- Full history stored in separate files
- Async I/O for non-blocking saves
- Automatic cleanup of old sessions

## Testing

Run the test script to verify persistence:
```bash
python tests/test_session_persistence.py
```

## Migration from Non-Persistent Eva

No migration needed! The system will automatically start persisting new sessions. Existing Zep memories remain intact and will be mapped to new persistent sessions.

## Troubleshooting

### Sessions Not Persisting
1. Check `data/sessions/` directory permissions
2. Verify disk space availability
3. Check logs for persistence errors

### Memory Not Restored
1. Ensure session was saved (check active_sessions.json)
2. Verify Zep API key is configured
3. Check zep_mappings.json for session mapping

### Large Sessions Slow to Load
- Consider adjusting the message history limit
- Use the restore endpoint for on-demand loading
- Check conversation history file sizes

## Future Enhancements

- [ ] Compression for large conversation histories
- [ ] Configurable retention policies
- [ ] Session encryption for sensitive contexts
- [ ] Backup/restore functionality
- [ ] Multi-user session sharing