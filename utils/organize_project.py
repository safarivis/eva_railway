#!/usr/bin/env python3
"""
Organize EVA Agent Project Files
"""

import os
import shutil
from pathlib import Path

def organize_project():
    """Organize all project files into a clean structure"""
    
    # Define directory structure
    dirs = {
        "core": "Core EVA agent files",
        "voice": "Voice interface scripts", 
        "integrations": "External service integrations",
        "utils": "Utility scripts and helpers",
        "scripts": "Standalone scripts and tools",
        "tests": "Test files",
        "docs": "Documentation files",
        "configs": "Configuration files",
        "logs": "Log files"
    }
    
    # Create directories
    for dir_name, desc in dirs.items():
        Path(dir_name).mkdir(exist_ok=True)
        print(f"📁 Created {dir_name}/ - {desc}")
    
    # Define file mappings
    file_mappings = {
        # Core EVA files
        "eva.py": "core/",
        "eva_fixed.py": "core/",
        "start_eva.py": "core/",
        "eva_agent.py": "core/",
        
        # Voice interface files
        "claude_voice_direct.py": "voice/",
        "claude_voice_direct_fixed.py": "voice/",
        "claude_voice_seamless.py": "voice/",
        "eva_voice_workflow.py": "voice/",
        "eva_terminal_voice.py": "voice/",
        "eva_terminal_voice_adjusted.py": "voice/",
        "eva_terminal_ptt.py": "voice/",
        "eva_terminal_ptt_simple.py": "voice/",
        "eva_ptt_simplified.py": "voice/",
        "simple_voice_eva.py": "voice/",
        "simple_voice_paste.py": "voice/",
        "simple_ptt_voice.py": "voice/",
        "voice_to_active_window.py": "voice/",
        "voice_to_claude_simple.py": "voice/",
        "voice_to_clipboard.py": "voice/",
        "voice_gui.py": "voice/",
        "direct_voice_to_claude.py": "voice/",
        "realtime_voice.py": "voice/",
        "minimal_voice_claude_code.py": "voice/",
        "natural_voice_coding.py": "voice/",
        "claude_code_voice_integration.py": "voice/",
        "claude_code_terminal_voice.py": "voice/",
        "simple_voice_recognition.py": "voice/",
        "eva_voice_speechrecognition.py": "voice/",
        
        # Integrations
        "elevenlabs_integration.py": "integrations/",
        "zep_memory.py": "integrations/",
        "zep_context_manager.py": "integrations/",
        "speechrecognition_stt.py": "integrations/",
        "private_context_auth.py": "integrations/",
        
        # Utils and tools
        "cli_client.py": "utils/",
        "secure_voice_manager.py": "utils/",
        "voice_vault.py": "utils/",
        "organize_voice_files.py": "utils/",
        "organize_project.py": "utils/",
        
        # Test files
        "test_*.py": "tests/",
        "check_*.py": "tests/",
        "direct_*.py": "tests/",
        
        # Scripts
        "global_voice_claude_setup.py": "scripts/",
        "voice_coding_examples.py": "scripts/",
        
        # Log files
        "*.log": "logs/",
        "eva_log.txt": "logs/"
    }
    
    # Move files
    moved_count = 0
    for pattern, dest_dir in file_mappings.items():
        if "*" in pattern:
            # Handle glob patterns
            files = list(Path(".").glob(pattern))
        else:
            # Handle specific files
            files = [Path(pattern)] if Path(pattern).exists() else []
        
        for file_path in files:
            if file_path.is_file():
                dest_path = Path(dest_dir) / file_path.name
                try:
                    # Skip if already in correct location
                    if file_path.parent == Path(dest_dir):
                        continue
                        
                    shutil.move(str(file_path), str(dest_path))
                    print(f"  ✓ {file_path.name} → {dest_dir}")
                    moved_count += 1
                except Exception as e:
                    print(f"  ✗ Error moving {file_path.name}: {e}")
    
    # Move documentation files
    doc_files = ["*.md", "*.txt"]
    for pattern in doc_files:
        for file_path in Path(".").glob(pattern):
            if file_path.name not in ["requirements.txt", "client_requirements.txt", "terminal_requirements.txt"]:
                try:
                    dest = Path("docs") / file_path.name
                    shutil.move(str(file_path), str(dest))
                    print(f"  ✓ {file_path.name} → docs/")
                    moved_count += 1
                except Exception as e:
                    print(f"  ✗ Error moving {file_path.name}: {e}")
    
    # Move shell scripts
    for sh_file in Path(".").glob("*.sh"):
        try:
            dest = Path("scripts") / sh_file.name
            shutil.move(str(sh_file), str(dest))
            print(f"  ✓ {sh_file.name} → scripts/")
            moved_count += 1
        except Exception as e:
            print(f"  ✗ Error moving {sh_file.name}: {e}")
    
    print(f"\n✅ Organized {moved_count} files")
    
    # Create main README
    readme_content = """# EVA Agent Project

An intelligent AI assistant with voice capabilities and contextual memory.

## Project Structure

```
eva_agent/
├── core/               # Core EVA agent files
├── voice/              # Voice interface scripts  
├── integrations/       # External service integrations
├── utils/              # Utility scripts and helpers
├── scripts/            # Standalone scripts and tools
├── tests/              # Test files
├── docs/               # Documentation
├── configs/            # Configuration files
├── logs/               # Log files
├── static/             # Web interface files
├── voice_recordings/   # Secure voice recordings (private)
└── venv/               # Python virtual environment
```

## Quick Start

1. Activate virtual environment:
   ```bash
   source venv/bin/activate
   ```

2. Start EVA server:
   ```bash
   python core/eva.py
   ```

3. Use voice interface:
   ```bash
   python voice/claude_voice_direct_fixed.py
   ```

## Key Features

- 🎤 Voice interaction with speech recognition
- 🔊 Text-to-speech responses
- 🧠 Contextual memory with Zep integration
- 🔐 Secure voice recording storage
- 🌐 Web interface
- 🤖 Multiple personality modes

## Documentation

See the `docs/` directory for detailed documentation.
"""
    
    with open("README.md", "w") as f:
        f.write(readme_content)
    print("\n📝 Created main README.md")

if __name__ == "__main__":
    organize_project()