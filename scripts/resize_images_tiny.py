#!/usr/bin/env python3
"""
Create ultra-tiny versions of images for LLM vision models
Optimized for minimal token usage while maintaining visibility
"""
import os
import sys
from PIL import Image, ImageOps
import argparse

def resize_image_tiny(input_path, output_path, max_size=128, quality=60):
    """
    Resize image to ultra-tiny size optimized for LLM vision
    
    Args:
        input_path: Path to input image
        output_path: Path to save resized image
        max_size: Maximum dimension (128px is usually enough for LLMs)
        quality: JPEG quality (lower = smaller file)
    """
    try:
        with Image.open(input_path) as img:
            # Convert to RGB if needed (for JPEG)
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            # Calculate new size maintaining aspect ratio
            width, height = img.size
            if width > height:
                new_width = max_size
                new_height = int((height * max_size) / width)
            else:
                new_height = max_size
                new_width = int((width * max_size) / height)
            
            # Resize with high-quality resampling
            img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Save as JPEG with compression for minimum size
            img_resized.save(output_path, 'JPEG', quality=quality, optimize=True)
            
            return True
            
    except Exception as e:
        print(f"Error resizing {input_path}: {e}")
        return False

def process_directory(input_dir, max_size=128, quality=60, suffix="_tiny"):
    """Process all images in a directory"""
    
    supported_formats = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp')
    processed = 0
    total_original_size = 0
    total_new_size = 0
    
    print(f"🔍 Scanning {input_dir} for images...")
    
    for filename in os.listdir(input_dir):
        if filename.lower().endswith(supported_formats):
            # Skip already processed tiny images
            if suffix in filename:
                continue
                
            input_path = os.path.join(input_dir, filename)
            
            # Create output filename
            name, ext = os.path.splitext(filename)
            output_filename = f"{name}{suffix}.jpg"  # Always save as JPEG for size
            output_path = os.path.join(input_dir, output_filename)
            
            # Skip if tiny version already exists
            if os.path.exists(output_path):
                print(f"⏭️  Skipping {filename} (tiny version exists)")
                continue
            
            original_size = os.path.getsize(input_path)
            
            print(f"📐 Resizing {filename} to {max_size}px...")
            
            if resize_image_tiny(input_path, output_path, max_size, quality):
                new_size = os.path.getsize(output_path)
                reduction = ((original_size - new_size) / original_size) * 100
                
                print(f"✅ {filename} -> {output_filename}")
                print(f"   Original: {original_size:,} bytes")
                print(f"   Tiny: {new_size:,} bytes")
                print(f"   Reduction: {reduction:.1f}%")
                print()
                
                total_original_size += original_size
                total_new_size += new_size
                processed += 1
            else:
                print(f"❌ Failed to resize {filename}")
    
    if processed > 0:
        total_reduction = ((total_original_size - total_new_size) / total_original_size) * 100
        print(f"📊 Summary:")
        print(f"   Processed: {processed} images")
        print(f"   Original total: {total_original_size:,} bytes ({total_original_size/1024/1024:.1f} MB)")
        print(f"   Tiny total: {total_new_size:,} bytes ({total_new_size/1024/1024:.1f} MB)")
        print(f"   Total reduction: {total_reduction:.1f}%")
        print(f"   Average size per tiny image: {total_new_size//processed:,} bytes")
    else:
        print("No new images to process!")

def main():
    parser = argparse.ArgumentParser(description='Create ultra-tiny images for LLM vision models')
    parser.add_argument('--dir', default='/home/ldp/eva/media', help='Directory containing images')
    parser.add_argument('--size', type=int, default=128, help='Maximum dimension in pixels (default: 128)')
    parser.add_argument('--quality', type=int, default=60, help='JPEG quality 1-100 (default: 60)')
    parser.add_argument('--suffix', default='_tiny', help='Suffix for output files (default: _tiny)')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.dir):
        print(f"❌ Directory not found: {args.dir}")
        return
    
    print(f"🖼️  Creating ultra-tiny images for LLM vision")
    print(f"📁 Input directory: {args.dir}")
    print(f"📐 Max size: {args.size}px")
    print(f"🗜️  JPEG quality: {args.quality}")
    print(f"📝 Suffix: {args.suffix}")
    print("=" * 50)
    
    process_directory(args.dir, args.size, args.quality, args.suffix)
    
    print("\n✨ Ultra-tiny image creation complete!")
    print("💡 These tiny images are perfect for LLM vision models while using minimal tokens.")

if __name__ == "__main__":
    main()