#!/usr/bin/env python3
"""
Organize Voice Files - Move and organize voice recordings
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

def organize_voice_files():
    """Organize voice files into directories by type and date"""
    
    # Create organized directory structure
    voice_dir = Path("voice_recordings")
    voice_dir.mkdir(exist_ok=True)
    
    # Create subdirectories
    subdirs = {
        "claude_recordings": voice_dir / "claude_recordings",
        "eva_recordings": voice_dir / "eva_recordings", 
        "voice_clips": voice_dir / "voice_clips",
        "other": voice_dir / "other"
    }
    
    for subdir in subdirs.values():
        subdir.mkdir(exist_ok=True, mode=0o700)
    
    # Set restrictive permissions on main directory
    os.chmod(voice_dir, 0o700)
    
    # Find all voice files
    voice_files = []
    patterns = ["*.wav", "*.mp3", "*.m4a", "*.ogg"]
    
    for pattern in patterns:
        voice_files.extend(Path(".").glob(pattern))
    
    if not voice_files:
        print("No voice files found to organize")
        return
    
    print(f"Found {len(voice_files)} voice files:")
    
    # Organize files by type
    moved_count = 0
    for file_path in voice_files:
        if file_path.is_file():
            # Determine destination based on filename
            filename = file_path.name.lower()
            
            if "claude" in filename:
                dest_dir = subdirs["claude_recordings"]
            elif "eva" in filename:
                dest_dir = subdirs["eva_recordings"]
            elif "voice" in filename:
                dest_dir = subdirs["voice_clips"]
            else:
                dest_dir = subdirs["other"]
            
            # Move file
            dest_path = dest_dir / file_path.name
            
            # Handle duplicates
            counter = 1
            while dest_path.exists():
                stem = file_path.stem
                suffix = file_path.suffix
                dest_path = dest_dir / f"{stem}_{counter}{suffix}"
                counter += 1
            
            try:
                shutil.move(str(file_path), str(dest_path))
                # Set restrictive permissions
                os.chmod(dest_path, 0o600)
                print(f"📁 Moved: {file_path.name} → {dest_dir.name}/{dest_path.name}")
                moved_count += 1
            except Exception as e:
                print(f"❌ Error moving {file_path.name}: {e}")
    
    print(f"\n✅ Organized {moved_count} voice files")
    print(f"📁 Files moved to: {voice_dir.absolute()}")
    
    # Create README with security info
    readme_path = voice_dir / "README.md"
    readme_content = f"""# Voice Recordings Directory

This directory contains organized voice recordings with restricted access.

## Directory Structure
- `claude_recordings/` - Recordings from Claude voice interactions
- `eva_recordings/` - Recordings from EVA voice interactions  
- `voice_clips/` - General voice clips
- `other/` - Other audio files

## Security
- Directory permissions: 700 (owner only)
- File permissions: 600 (owner read/write only)
- Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Usage
- Files are protected from other users
- Use `voice_vault.py` for encryption if needed
- Regularly clean up old recordings
"""
    
    with open(readme_path, 'w') as f:
        f.write(readme_content)
    
    os.chmod(readme_path, 0o600)
    
    # Show directory structure
    print(f"\n📊 Directory structure:")
    for subdir_name, subdir_path in subdirs.items():
        file_count = len(list(subdir_path.glob("*")))
        print(f"  {subdir_name}: {file_count} files")

if __name__ == "__main__":
    organize_voice_files()