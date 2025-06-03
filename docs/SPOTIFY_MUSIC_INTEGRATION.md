# Spotify Music Integration for Eva

Eva now supports Spotify music control through the Spotify Web API, allowing users to control playback, create playlists, and search for music using natural language commands.

## Features

### 🎵 Playback Control
- **Play music**: "Play some jazz music", "Play songs by The Beatles"
- **Pause/Resume**: "Pause the music", "Resume playback"
- **Skip tracks**: "Skip to next song", "Go back to previous track"
- **Current status**: "What's currently playing?"

### 🎧 Music Search
- **Track search**: "Find songs by Adele"
- **Artist search**: "Search for Taylor Swift"
- **Album search**: "Find albums by Pink Floyd" 
- **Playlist search**: "Look for workout playlists"

### 📝 Playlist Management
- **Create playlists**: "Create a playlist called Study Music"
- **Add tracks**: "Add this song to my workout playlist"
- **Custom descriptions**: Playlists created with contextual descriptions

## Setup Instructions

### 1. Create Spotify App
1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Click "Create an App"
3. Fill in app name and description
4. Set the Redirect URI to: `http://localhost:8000/spotify/callback`
5. Copy your Client ID and Client Secret

### 2. Configure Environment Variables
```bash
export SPOTIFY_CLIENT_ID=your_client_id_here
export SPOTIFY_CLIENT_SECRET=your_client_secret_here
export SPOTIFY_REDIRECT_URI=http://localhost:8000/spotify/callback
```

### 3. Authenticate with Spotify
1. Ask Eva: "Check my Spotify connection"
2. Eva will provide an authorization URL
3. Visit the URL and authorize Eva to access your Spotify account
4. You'll be redirected back (the callback URL handling is automatic)

## Supported Commands

### Authentication
- "Check my Spotify connection"
- "Connect Eva to Spotify"

### Music Search
- "Search for [artist/song/album]"
- "Find music by [artist]"
- "Look for [genre] music"

### Playback Control
- "Play [song/artist/playlist]"
- "Pause the music"
- "Skip this song" / "Next track"
- "Previous song" / "Go back"
- "What's playing?" / "Current song"

### Playlist Management
- "Create a playlist called [name]"
- "Add [song] to [playlist]"
- "Make a [genre] playlist"

## Technical Details

### API Endpoints Used
- **Authentication**: `https://accounts.spotify.com/authorize`
- **Token Management**: `https://accounts.spotify.com/api/token`
- **Search**: `https://api.spotify.com/v1/search`
- **Playback Control**: `https://api.spotify.com/v1/me/player/*`
- **Playlist Management**: `https://api.spotify.com/v1/users/{user_id}/playlists`

### Required Scopes
The integration requests these Spotify scopes:
- `playlist-read-private` - Read private playlists
- `playlist-read-collaborative` - Read collaborative playlists
- `playlist-modify-public` - Create/modify public playlists
- `playlist-modify-private` - Create/modify private playlists
- `user-modify-playback-state` - Control playback
- `user-read-playback-state` - Read playback state
- `user-read-currently-playing` - Read current track
- `user-library-read` - Read saved music
- `user-library-modify` - Save/remove music

### Token Management
- Access tokens are automatically refreshed when expired
- Tokens are saved to `data/spotify_tokens.json`
- Secure token storage with automatic persistence

## Limitations

1. **Spotify Premium Required**: Playback control requires Spotify Premium
2. **Active Device Needed**: A Spotify device must be active for playback control
3. **Rate Limits**: Spotify API has rate limits (handled automatically)
4. **Regional Restrictions**: Some content may not be available in all regions

## Troubleshooting

### "No active device found"
- Open Spotify on any device (phone, computer, web player)
- Start playing any song briefly to activate the device
- Try the Eva command again

### "Token expired" 
- Eva will automatically refresh tokens
- If refresh fails, re-authenticate: "Check my Spotify connection"

### "Track not found"
- Try more specific search terms
- Check spelling of artist/song names
- Some tracks may not be available on Spotify

### "Insufficient client scope"
- Re-authorize Eva with Spotify to ensure all scopes are granted
- Check that your Spotify app has the correct redirect URI

## Examples

```
User: "Play some chill jazz music"
Eva: Let me search for chill jazz music and start playback for you.
[Searches for jazz music and starts playing]

User: "Create a workout playlist"
Eva: I'll create a new workout playlist for you.
[Creates playlist named "Workout Playlist [date]"]

User: "What's currently playing?"
Eva: Currently playing "Blue in Green" by Miles Davis from the album "Kind of Blue"

User: "Skip to the next song"
Eva: Skipped to the next track in your queue.
```

## Files

- `integrations/spotify_music_handler.py` - Main Spotify API integration
- `integrations/tool_manager.py` - Tool registration and schema
- `tests/test_spotify_music.py` - Integration tests
- `data/spotify_tokens.json` - Stored authentication tokens (auto-created)

## Security Notes

- Client secrets are stored as environment variables only
- Access tokens are stored locally with automatic refresh
- No sensitive data is logged or transmitted unnecessarily
- Tokens expire automatically and require re-authentication if refresh fails