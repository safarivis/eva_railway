# EVA Vision and Image Improvements Documentation

## Overview
This document outlines the comprehensive improvements made to EVA's image handling capabilities, aligning with OpenAI's latest vision and image generation APIs.

## 🎯 Vision Improvements

### 1. Detail Parameter Support
- Added `detail` parameter to image analysis requests (`low`, `high`, `auto`)
- `low`: Fast processing with 85 tokens, 512x512px resolution
- `high`: Better understanding with higher resolution processing
- `auto`: Let the model decide based on the image

### 2. URL-based Image Support
- EVA can now analyze images from URLs directly
- No need to download images first
- Supports both base64-encoded and URL-based images

### 3. Enhanced Chat Interface
```bash
# Local file with default detail
/image /home/ldp/eva/media/eva.jpeg

# URL with custom message
/image https://example.com/photo.jpg What is this building?

# High detail analysis
/image photo.jpg "Analyze every detail" detail:high

# Low detail for quick analysis
/image screenshot.png "What color is dominant?" detail:low
```

## 🎨 Image Generation Tool

### Features
- **gpt-image-1**: Default model with world knowledge for realistic images
- **DALL-E 3**: Artistic images with style options
- **DALL-E 2**: Classic image generation

### Tool Usage
EVA can now generate images when asked:
- "Generate an image of a sunset over mountains"
- "Create a picture of a glass cabinet with semi-precious stones"
- "Make an image of a futuristic city"

### Model-Specific Parameters

#### gpt-image-1
- `background`: transparent, opaque, or auto
- `moderation`: low or auto
- `output_format`: png, jpeg, or webp
- `output_compression`: 0-100%
- `quality`: auto, high, medium, low

#### DALL-E 3
- `size`: 1024x1024, 1792x1024, 1024x1792
- `quality`: standard or hd
- `style`: vivid or natural

## 🔧 Function Calling Improvements

### 1. Strict Mode
All tools now use `strict: true` for reliable schema validation.

### 2. Tool Choice Control
- `tool_choice: "auto"` - Let EVA decide
- `tool_choice: "required"` - Force tool use
- `tool_choice: "none"` - No tools
- `tool_choice: "image_tool"` - Use specific tool

### 3. Parallel Tool Calls
Control whether multiple tools can be called in parallel with `parallel_tool_calls` parameter.

### 4. Enhanced Error Handling
- JSON parsing validation
- 30-second timeout protection
- Graceful error recovery
- Detailed error messages

## 📋 Available Tools

### 1. Email Tool
- Send emails using Resend API
- Support for CC/BCC
- HTML content support

### 2. File Tool
- Read text and binary files
- Automatic image detection
- Path resolution (relative/absolute)
- Directory listing

### 3. Web Search Tool
- Search for current information
- Placeholder for integration

### 4. Image Tool (NEW)
- Generate images with AI
- Support for all OpenAI image models
- Model-specific parameter handling

## 🚀 Usage Examples

### Basic Image Analysis
```python
python eva_chat.py
> /image /home/ldp/eva/media/eva.jpeg
```

### URL Image Analysis with High Detail
```python
> /image https://example.com/diagram.png "Explain this diagram" detail:high
```

### Image Generation
```python
> Generate an image of a serene Japanese garden with cherry blossoms
# EVA will use the image_tool to create this
```

### Tool Control
```python
> Analyze this image without using any tools
# Use tool_choice:"none" internally

> Generate an image using DALL-E 3 specifically
# EVA will use image_tool with model:"dall-e-3"
```

## 🔐 Security Notes

- File access remains unrestricted (be careful!)
- Image URLs are validated by OpenAI
- Base64 encoding for local files
- Tool timeout protection (30 seconds)

## 📊 Token Usage

### Vision Costs (gpt-4-vision-preview)
- Low detail: 85 base tokens
- High detail: Calculated based on 512px tiles
- Auto: Model decides optimal processing

### Image Generation
- Billed per image generated
- Varies by model and parameters

## 🎯 Best Practices

1. Use `detail:"low"` for:
   - Color/shape questions
   - Quick identification
   - Token savings

2. Use `detail:"high"` for:
   - Text reading
   - Detailed analysis
   - Complex diagrams

3. Use `gpt-image-1` for:
   - Realistic images
   - World knowledge requirements
   - Specific object details

4. Use `DALL-E 3` for:
   - Artistic creations
   - Stylized images
   - Creative prompts

## 🐛 Troubleshooting

### Image Not Found
- Check file path (absolute vs relative)
- Verify file exists: `ls -la /path/to/image`

### Vision API Errors
- Check image size (<50MB)
- Verify supported format (PNG, JPEG, WEBP, GIF)
- Ensure no NSFW content

### Generation Failures
- Check API key is valid
- Verify model availability
- Review prompt for policy violations

## 🔄 Future Enhancements

1. **Multiple Image Support** - Analyze multiple images in one request
2. **Image Editing** - Edit existing images with prompts
3. **Image Variations** - Create variations of existing images
4. **Streaming Support** - Stream image generation progress
5. **Cost Tracking** - Track token usage for images

---

*Last Updated: [Current Date]*
*EVA Version: 0.1.0*