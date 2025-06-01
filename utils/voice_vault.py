#!/usr/bin/env python3
"""
Voice Vault - Simple encrypted voice file manager
"""

import os
import sys
import json
import hashlib
import getpass
from pathlib import Path
from datetime import datetime
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import PBKDF2
import base64

class VoiceVault:
    def __init__(self, vault_dir="voice_recordings"):
        self.vault_dir = Path(vault_dir)
        self.encrypted_dir = self.vault_dir / "encrypted"
        self.temp_dir = self.vault_dir / "temp"
        self.index_file = self.vault_dir / ".vault_index"
        
        # Create directories with secure permissions
        self.vault_dir.mkdir(exist_ok=True, mode=0o700)
        self.encrypted_dir.mkdir(exist_ok=True, mode=0o700)
        self.temp_dir.mkdir(exist_ok=True, mode=0o700)
        
        os.chmod(self.vault_dir, 0o700)
        os.chmod(self.encrypted_dir, 0o700)
        os.chmod(self.temp_dir, 0o700)
        
        self.password = None
        self.authenticated = False
    
    def authenticate(self, password=None):
        """Authenticate with password"""
        if password is None:
            password = getpass.getpass("🔐 Enter vault password: ")
        
        auth_file = self.vault_dir / ".auth"
        
        if not auth_file.exists():
            # First time setup
            confirm = getpass.getpass("🔐 Confirm password: ")
            if password != confirm:
                print("❌ Passwords don't match")
                return False
            
            # Store password hash
            salt = get_random_bytes(16)
            password_hash = PBKDF2(password, salt, 32, count=100000)
            
            with open(auth_file, 'wb') as f:
                f.write(salt + password_hash)
            
            os.chmod(auth_file, 0o600)
            print("✅ Vault password set")
        else:
            # Verify existing password
            with open(auth_file, 'rb') as f:
                data = f.read()
            
            salt = data[:16]
            stored_hash = data[16:]
            password_hash = PBKDF2(password, salt, 32, count=100000)
            
            if password_hash != stored_hash:
                print("❌ Invalid password")
                return False
        
        self.password = password
        self.authenticated = True
        return True
    
    def _get_key(self, salt):
        """Derive encryption key from password"""
        return PBKDF2(self.password, salt, 32, count=100000)
    
    def encrypt_file(self, file_path, description=""):
        """Encrypt and store a voice file"""
        if not self.authenticated:
            print("❌ Not authenticated")
            return None
        
        file_path = Path(file_path)
        if not file_path.exists():
            print(f"❌ File not found: {file_path}")
            return None
        
        # Generate file ID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_id = f"voice_{timestamp}"
        
        # Read file
        with open(file_path, 'rb') as f:
            data = f.read()
        
        # Encrypt
        salt = get_random_bytes(16)
        key = self._get_key(salt)
        cipher = AES.new(key, AES.MODE_GCM)
        ciphertext, tag = cipher.encrypt_and_digest(data)
        
        # Store encrypted file
        encrypted_path = self.encrypted_dir / f"{file_id}.vault"
        with open(encrypted_path, 'wb') as f:
            f.write(salt + cipher.nonce + tag + ciphertext)
        
        os.chmod(encrypted_path, 0o600)
        
        # Update index
        self._update_index(file_id, {
            'original_name': file_path.name,
            'description': description,
            'timestamp': timestamp,
            'size': len(data)
        })
        
        print(f"🔒 Encrypted: {file_path.name} → {file_id}")
        return file_id
    
    def decrypt_file(self, file_id, output_path=None):
        """Decrypt a voice file"""
        if not self.authenticated:
            print("❌ Not authenticated")
            return None
        
        encrypted_path = self.encrypted_dir / f"{file_id}.vault"
        if not encrypted_path.exists():
            print(f"❌ File not found: {file_id}")
            return None
        
        # Read encrypted file
        with open(encrypted_path, 'rb') as f:
            data = f.read()
        
        salt = data[:16]
        nonce = data[16:32]
        tag = data[32:48]
        ciphertext = data[48:]
        
        # Decrypt
        key = self._get_key(salt)
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        
        try:
            plaintext = cipher.decrypt_and_verify(ciphertext, tag)
        except ValueError:
            print("❌ Decryption failed - file may be corrupted")
            return None
        
        # Determine output path
        if output_path is None:
            index = self._load_index()
            if file_id in index:
                original_name = index[file_id]['original_name']
                output_path = self.temp_dir / original_name
            else:
                output_path = self.temp_dir / f"{file_id}.wav"
        
        # Write decrypted file
        with open(output_path, 'wb') as f:
            f.write(plaintext)
        
        os.chmod(output_path, 0o600)
        print(f"🔓 Decrypted: {file_id} → {output_path}")
        return str(output_path)
    
    def _update_index(self, file_id, metadata):
        """Update the index file"""
        index = self._load_index()
        index[file_id] = metadata
        
        with open(self.index_file, 'w') as f:
            json.dump(index, f, indent=2)
        
        os.chmod(self.index_file, 0o600)
    
    def _load_index(self):
        """Load the index file"""
        if not self.index_file.exists():
            return {}
        
        try:
            with open(self.index_file, 'r') as f:
                return json.load(f)
        except:
            return {}
    
    def list_files(self):
        """List all encrypted files"""
        if not self.authenticated:
            print("❌ Not authenticated")
            return {}
        
        return self._load_index()
    
    def delete_file(self, file_id):
        """Delete an encrypted file"""
        if not self.authenticated:
            print("❌ Not authenticated")
            return False
        
        encrypted_path = self.encrypted_dir / f"{file_id}.vault"
        if encrypted_path.exists():
            os.remove(encrypted_path)
            
            # Update index
            index = self._load_index()
            if file_id in index:
                del index[file_id]
                with open(self.index_file, 'w') as f:
                    json.dump(index, f, indent=2)
            
            print(f"🗑️  Deleted: {file_id}")
            return True
        
        print(f"❌ File not found: {file_id}")
        return False
    
    def cleanup_temp(self):
        """Clean up temporary files"""
        count = 0
        for file in self.temp_dir.glob("*"):
            try:
                os.remove(file)
                count += 1
            except:
                pass
        
        if count > 0:
            print(f"🧹 Cleaned up {count} temporary files")

# Utility functions for easy file management
def secure_existing_files():
    """Move existing voice files to the vault"""
    vault = VoiceVault()
    if not vault.authenticate():
        return
    
    # Find all voice files in current directory
    voice_files = []
    for pattern in ["*.wav", "*recording*.wav", "*voice*.wav", "*audio*.wav"]:
        voice_files.extend(Path(".").glob(pattern))
    
    if not voice_files:
        print("No voice files found to secure")
        return
    
    print(f"Found {len(voice_files)} voice files to secure:")
    for f in voice_files:
        print(f"  {f.name}")
    
    if input("\nSecure these files? (y/N): ").lower() == 'y':
        secured = 0
        for file_path in voice_files:
            file_id = vault.encrypt_file(file_path, f"Auto-secured from {file_path.name}")
            if file_id:
                # Remove original file
                try:
                    os.remove(file_path)
                    secured += 1
                except:
                    print(f"⚠️  Couldn't remove original: {file_path}")
        
        print(f"✅ Secured {secured} files")

def main():
    """Command line interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Voice Vault - Encrypted Voice File Manager")
    parser.add_argument("action", choices=["encrypt", "decrypt", "list", "delete", "cleanup", "secure"], 
                       help="Action to perform")
    parser.add_argument("--file", help="File to encrypt")
    parser.add_argument("--id", help="File ID for decrypt/delete")
    parser.add_argument("--desc", help="Description for encrypted file")
    parser.add_argument("--output", help="Output path for decrypted file")
    
    args = parser.parse_args()
    
    if args.action == "secure":
        secure_existing_files()
        return
    
    vault = VoiceVault()
    if not vault.authenticate():
        sys.exit(1)
    
    if args.action == "encrypt":
        if not args.file:
            print("❌ --file required")
            sys.exit(1)
        vault.encrypt_file(args.file, args.desc or "")
    
    elif args.action == "decrypt":
        if not args.id:
            print("❌ --id required")
            sys.exit(1)
        vault.decrypt_file(args.id, args.output)
    
    elif args.action == "list":
        files = vault.list_files()
        if not files:
            print("📁 Vault is empty")
        else:
            print(f"\n🔐 Voice Vault ({len(files)} files):")
            print("-" * 60)
            for file_id, meta in files.items():
                print(f"📄 {file_id}")
                print(f"   Original: {meta['original_name']}")
                print(f"   Time: {meta['timestamp']}")
                print(f"   Size: {meta['size']} bytes")
                if meta['description']:
                    print(f"   Note: {meta['description']}")
                print()
    
    elif args.action == "delete":
        if not args.id:
            print("❌ --id required")
            sys.exit(1)
        vault.delete_file(args.id)
    
    elif args.action == "cleanup":
        vault.cleanup_temp()

if __name__ == "__main__":
    main()