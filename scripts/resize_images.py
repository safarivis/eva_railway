#!/usr/bin/env python3
"""
Resize images in /home/ldp/eva/media/ to create smaller versions
Creates _small versions with max dimension of 512px
"""
import os
import sys
from PIL import Image
from pathlib import Path
import argparse

def resize_image(input_path, max_size=512, quality=85):
    """Resize image to have max dimension of max_size pixels"""
    try:
        # Open image
        img = Image.open(input_path)
        
        # Get original dimensions
        width, height = img.size
        print(f"  Original: {width}x{height}")
        
        # Calculate new dimensions maintaining aspect ratio
        if width > max_size or height > max_size:
            if width > height:
                new_width = max_size
                new_height = int(height * (max_size / width))
            else:
                new_height = max_size
                new_width = int(width * (max_size / height))
        else:
            print(f"  Already small enough, skipping")
            return None
            
        # Resize image
        img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Generate output filename
        input_path = Path(input_path)
        output_name = f"{input_path.stem}_small{input_path.suffix}"
        output_path = input_path.parent / output_name
        
        # Convert RGBA to RGB if saving as JPEG
        if input_path.suffix.lower() in ['.jpg', '.jpeg'] and img_resized.mode in ['RGBA', 'P']:
            # Create white background
            background = Image.new('RGB', img_resized.size, (255, 255, 255))
            if img_resized.mode == 'P':
                img_resized = img_resized.convert('RGBA')
            background.paste(img_resized, mask=img_resized.split()[3] if img_resized.mode == 'RGBA' else None)
            img_resized = background
        
        # Save resized image
        if input_path.suffix.lower() in ['.jpg', '.jpeg']:
            img_resized.save(output_path, 'JPEG', quality=quality, optimize=True)
        else:
            img_resized.save(output_path, quality=quality, optimize=True)
            
        print(f"  Resized: {new_width}x{new_height}")
        print(f"  Saved: {output_path}")
        
        # Show file sizes
        original_size = os.path.getsize(input_path)
        new_size = os.path.getsize(output_path)
        reduction = (1 - new_size/original_size) * 100
        print(f"  Size: {original_size//1024}KB -> {new_size//1024}KB ({reduction:.1f}% reduction)")
        
        return output_path
        
    except Exception as e:
        print(f"  ERROR: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description='Resize images to smaller versions')
    parser.add_argument('--path', default='/home/ldp/eva/media/', help='Path to search for images')
    parser.add_argument('--max-size', type=int, default=512, help='Maximum dimension in pixels')
    parser.add_argument('--quality', type=int, default=85, help='JPEG quality (1-100)')
    args = parser.parse_args()
    
    # Find all image files
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
    image_files = []
    
    for root, dirs, files in os.walk(args.path):
        for file in files:
            if any(file.lower().endswith(ext) for ext in image_extensions):
                # Skip files that are already _small versions
                if '_small' not in file:
                    image_files.append(os.path.join(root, file))
    
    print(f"Found {len(image_files)} images to process")
    print(f"Max size: {args.max_size}px, Quality: {args.quality}%\n")
    
    # Process each image
    successful = 0
    for i, img_path in enumerate(image_files, 1):
        print(f"\n[{i}/{len(image_files)}] Processing: {img_path}")
        result = resize_image(img_path, args.max_size, args.quality)
        if result:
            successful += 1
    
    print(f"\n✅ Successfully resized {successful}/{len(image_files)} images")

if __name__ == "__main__":
    main()