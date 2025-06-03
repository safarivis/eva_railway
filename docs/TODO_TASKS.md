# EVA Agent TODO Tasks

## 🔧 High Priority - Bug Fixes

### 🔧 Critical Tool Workflow Issues
- [ ] **Fix "None" response problem**
  - EVA returns "None" instead of completing tool workflows
  - Tool calls succeed but EVA doesn't continue to next steps
  - Affects multi-step workflows (file creation → TTS → email)
  - System prompt updates not fixing the issue

- [ ] **Fix incomplete multi-step workflows**
  - File creation works but workflow stops
  - Should complete: write file → generate TTS → email → respond
  - EVA doesn't automatically continue after successful tool calls
  - Need to fix tool calling continuation logic

### 📁 File Browsing Issues
- [ ] **Debug file tool implementation**
  - Check file tool in tool_manager.py
  - Test file reading with simple requests
  - Verify file path handling and permissions
  - Ensure file tool is properly registered
  - Test reading from tiny_images directory specifically

- [ ] **Fix file browsing workflow**
  - Test directory listing functionality
  - Verify file reading with different file types
  - Check base64 encoding for images
  - Ensure proper error handling

### 🖼️ Image Generation Issues
- [ ] **Troubleshoot image generation**
  - Test DALL-E API integration
  - Verify gpt-image-1 model access
  - Check image saving to local filesystem
  - Test image generation tool calling workflow
  - Verify attachment functionality for email

- [ ] **Fix image workflow**
  - Test end-to-end: generate → save → email
  - Check file path handling for generated images
  - Verify image format support (PNG, JPEG, WebP)
  - Test micro image generation for tiny_images folder

### 📧 Email Integration Issues
- [ ] **Fix email workflow completion**
  - Email tool not being called after file creation
  - Test email sending with text files
  - Test email sending with audio attachments
  - Verify Resend API integration works
  - Test with Gmail domain verification issues

## 🎵 Medium Priority - New Features

### 🎶 Music System Implementation
- [ ] **Design music architecture**
  - Research music APIs (Spotify, Apple Music, YouTube Music)
  - Design playlist creation system
  - Plan music playback integration
  - Consider local vs streaming music support

- [ ] **Implement music tool**
  - Create music_tool.py with playlist functions
  - Add music search and discovery
  - Implement playlist creation/modification
  - Add music playback controls (play, pause, skip)
  - Support for different music services

- [ ] **Music integration features**
  - Voice commands for music control
  - Smart playlist generation based on mood/context
  - Music recommendations based on conversation
  - Integration with voice workflows

### 🎧 Music Tool Specifications
- [ ] **Core Functions**
  - `search_music(query, service)` - Search for songs/artists
  - `create_playlist(name, description)` - Create new playlist
  - `add_to_playlist(playlist_id, track_id)` - Add songs
  - `play_music(track_or_playlist_id)` - Start playback
  - `control_playback(action)` - Play/pause/skip/volume

- [ ] **Advanced Features**
  - `generate_playlist_by_mood(mood, duration)` - AI playlist creation
  - `get_recommendations(based_on)` - Music discovery
  - `analyze_music_taste()` - Learn user preferences
  - `share_playlist(playlist_id, method)` - Export/share playlists

## 🧪 Testing & Validation

### File System Testing
- [ ] Test file reading from various directories
- [ ] Test image file handling specifically
- [ ] Verify permission handling for different file types
- [ ] Test with relative vs absolute paths

### Image Generation Testing
- [ ] Test DALL-E 2 vs DALL-E 3 vs gpt-image-1
- [ ] Test different image sizes and formats
- [ ] Test image saving to filesystem
- [ ] Test email attachment workflow

### Music System Testing
- [ ] Test music service API connections
- [ ] Test playlist CRUD operations
- [ ] Test music search functionality
- [ ] Test playback controls
- [ ] Test voice command integration

## 📋 Documentation Needed

- [ ] **File Tool Usage Guide** - How to use file browsing features
- [ ] **Image Generation Guide** - Complete image workflow documentation
- [ ] **Music Integration Guide** - How to use music features
- [ ] **Troubleshooting Guide** - Common issues and solutions

## 🔍 Investigation Areas

### File Tool Issues
- Check if file tool is in the tool registry
- Verify file path resolution
- Test different file types (text, images, etc.)
- Check permission handling

### Image Generation Issues  
- Test OpenAI image API directly
- Check local file saving functionality
- Verify tool calling workflow
- Test email attachment process

### Music System Requirements
- Research available music APIs
- Check authentication requirements
- Plan local vs cloud music support
- Design voice command interface

## 📱 Social Media Integration - New Feature

### 🎯 Platform Integration Plan
- [ ] **LinkedIn Integration**
  - OAuth 2.0 authentication setup
  - LinkedIn API v2 implementation
  - Permissions: `w_member_social` for posting
  - Features: Text posts, article sharing, image posts
  - Create linkedin_handler.py

- [ ] **X (Twitter) Integration**
  - Twitter API v2 setup
  - OAuth 2.0 or API Key authentication
  - Elevated access application for posting
  - Features: Tweets, threads, media uploads, scheduling
  - Create x_handler.py (twitter_handler.py)

- [ ] **YouTube Integration**
  - Google OAuth 2.0 setup
  - YouTube Data API v3 implementation
  - Channel management scope
  - Features: Video uploads, descriptions, thumbnails, playlists
  - Create youtube_handler.py

- [ ] **Instagram Integration**
  - Instagram Graph API (business accounts only)
  - Facebook app setup required
  - Instagram Basic Display API limitations
  - Features: Photo posts, stories (if available), captions
  - Create instagram_handler.py

### 🛠️ Implementation Approach
- [ ] **Unified Social Media Manager**
  - Create social_media_manager.py
  - Common interface for all platforms
  - Unified post scheduling
  - Cross-platform posting with single command
  - Platform-specific formatting

- [ ] **Individual Platform Handlers**
  - Separate handler for each platform
  - Platform-specific features and limitations
  - Error handling for API limits
  - Media format conversion as needed

- [ ] **Authentication Management**
  - OAuth token storage and refresh
  - Multi-account support
  - Secure credential management
  - Session persistence

### 📋 Social Media Tool Specifications
- [ ] **Core Functions**
  - `post_to_platform(platform, content, media=None)` - Post to specific platform
  - `post_to_all(content, platforms=[])` - Cross-platform posting
  - `schedule_post(platform, content, datetime)` - Schedule future posts
  - `upload_media(platform, file_path)` - Handle media uploads
  - `get_post_analytics(platform, post_id)` - Track engagement

- [ ] **Advanced Features**
  - `optimize_content(content, platform)` - Platform-specific optimization
  - `generate_hashtags(content, platform)` - AI-powered hashtag suggestions
  - `create_thread(platform, messages)` - Multi-part posts (Twitter threads)
  - `cross_post_with_adaptation(content)` - Adapt content for each platform

### 🧪 Testing Requirements
- [ ] Test OAuth flows for each platform
- [ ] Test posting text content
- [ ] Test media uploads (images, videos)
- [ ] Test scheduling functionality
- [ ] Test error handling and rate limits
- [ ] Test cross-platform posting

### 📚 Documentation Needed
- [ ] Social Media Integration Guide
- [ ] Platform-specific setup instructions
- [ ] API key and OAuth setup walkthrough
- [ ] Usage examples for each platform
- [ ] Troubleshooting common issues

### 🚀 Implementation Priority
1. Start with X (Twitter) - simplest API
2. LinkedIn - professional content
3. YouTube - video content
4. Instagram - most complex due to Facebook requirements

---

**Note**: These tasks should be completed in priority order. High priority bug fixes should be addressed before implementing new features. Social media integration is a medium-priority feature that will significantly expand Eva's capabilities.