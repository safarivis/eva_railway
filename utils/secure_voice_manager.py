#!/usr/bin/env python3
"""
Secure Voice Manager - Encrypt and manage voice recordings with password protection
"""

import os
import sys
import hashlib
import getpass
from pathlib import Path
from datetime import datetime
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import json

class SecureVoiceManager:
    def __init__(self, base_dir="voice_recordings"):
        self.base_dir = Path(base_dir)
        self.encrypted_dir = self.base_dir / "encrypted"
        self.temp_dir = self.base_dir / "temp"
        self.index_file = self.encrypted_dir / ".index.enc"
        
        # Ensure directories exist with proper permissions
        self.encrypted_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.temp_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
        
        # Set restrictive permissions
        os.chmod(self.base_dir, 0o700)
        os.chmod(self.encrypted_dir, 0o700)
        os.chmod(self.temp_dir, 0o700)
        
        self._fernet = None
        self._password_hash = None
    
    def _derive_key(self, password: str, salt: bytes) -> bytes:
        """Derive encryption key from password"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
    
    def _get_password(self, prompt="Enter password: ") -> str:
        """Get password from user securely"""
        return getpass.getpass(prompt)
    
    def authenticate(self, password: str = None) -> bool:
        """Authenticate with password"""
        if password is None:
            password = self._get_password("Enter voice recordings password: ")
        
        # Check if this is first time setup
        password_file = self.encrypted_dir / ".auth"
        
        if not password_file.exists():
            # First time setup
            confirm = self._get_password("Confirm password: ")
            if password != confirm:
                print("❌ Passwords don't match")
                return False
            
            # Generate salt and store password hash
            salt = os.urandom(16)
            password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
            
            auth_data = {
                'salt': base64.b64encode(salt).decode(),
                'hash': base64.b64encode(password_hash).decode()
            }
            
            # Write auth file with restricted permissions
            with open(password_file, 'w') as f:
                json.dump(auth_data, f)
            os.chmod(password_file, 0o600)
            
            print("✅ Password set for voice recordings")
        else:
            # Load existing auth data
            with open(password_file, 'r') as f:
                auth_data = json.load(f)
            
            salt = base64.b64decode(auth_data['salt'])
            stored_hash = base64.b64decode(auth_data['hash'])
            
            # Verify password
            password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
            if password_hash != stored_hash:
                print("❌ Invalid password")
                return False
        
        # Set up encryption
        key = self._derive_key(password, salt)
        self._fernet = Fernet(key)
        self._password_hash = password_hash
        
        return True
    
    def encrypt_file(self, file_path: str, description: str = "") -> str:
        """Encrypt a voice file and store it securely"""
        if not self._fernet:
            raise ValueError("Not authenticated. Call authenticate() first.")
        
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Generate unique ID for the file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_id = f"voice_{timestamp}_{file_path.stem}"
        
        # Read and encrypt file
        with open(file_path, 'rb') as f:
            data = f.read()
        
        encrypted_data = self._fernet.encrypt(data)
        
        # Store encrypted file
        encrypted_path = self.encrypted_dir / f"{file_id}.enc"
        with open(encrypted_path, 'wb') as f:
            f.write(encrypted_data)
        
        # Set restrictive permissions
        os.chmod(encrypted_path, 0o600)
        
        # Update index
        self._update_index(file_id, {
            'original_name': file_path.name,
            'description': description,
            'timestamp': timestamp,
            'size': len(data)
        })
        
        print(f"✅ File encrypted and stored as: {file_id}")
        return file_id
    
    def decrypt_file(self, file_id: str, output_path: str = None) -> str:
        """Decrypt a voice file"""
        if not self._fernet:
            raise ValueError("Not authenticated. Call authenticate() first.")
        
        encrypted_path = self.encrypted_dir / f"{file_id}.enc"
        if not encrypted_path.exists():
            raise FileNotFoundError(f"Encrypted file not found: {file_id}")
        
        # Read and decrypt file
        with open(encrypted_path, 'rb') as f:
            encrypted_data = f.read()
        
        decrypted_data = self._fernet.decrypt(encrypted_data)
        
        # Determine output path
        if output_path is None:
            index = self._load_index()
            if file_id in index:
                original_name = index[file_id]['original_name']
                output_path = self.temp_dir / original_name
            else:
                output_path = self.temp_dir / f"{file_id}.wav"
        
        output_path = Path(output_path)
        
        # Write decrypted file
        with open(output_path, 'wb') as f:
            f.write(decrypted_data)
        
        # Set permissions
        os.chmod(output_path, 0o600)
        
        return str(output_path)
    
    def _update_index(self, file_id: str, metadata: dict):
        """Update the encrypted index file"""
        index = self._load_index()
        index[file_id] = metadata
        
        # Encrypt and save index
        index_data = json.dumps(index).encode()
        encrypted_index = self._fernet.encrypt(index_data)
        
        with open(self.index_file, 'wb') as f:
            f.write(encrypted_index)
        
        os.chmod(self.index_file, 0o600)
    
    def _load_index(self) -> dict:
        """Load and decrypt the index file"""
        if not self.index_file.exists():
            return {}
        
        try:
            with open(self.index_file, 'rb') as f:
                encrypted_data = f.read()
            
            decrypted_data = self._fernet.decrypt(encrypted_data)
            return json.loads(decrypted_data.decode())
        except Exception:
            return {}
    
    def list_files(self) -> dict:
        """List all encrypted voice files"""
        if not self._fernet:
            raise ValueError("Not authenticated. Call authenticate() first.")
        
        return self._load_index()
    
    def delete_file(self, file_id: str) -> bool:
        """Delete an encrypted voice file"""
        if not self._fernet:
            raise ValueError("Not authenticated. Call authenticate() first.")
        
        encrypted_path = self.encrypted_dir / f"{file_id}.enc"
        if not encrypted_path.exists():
            return False
        
        # Remove file
        os.remove(encrypted_path)
        
        # Update index
        index = self._load_index()
        if file_id in index:
            del index[file_id]
            index_data = json.dumps(index).encode()
            encrypted_index = self._fernet.encrypt(index_data)
            
            with open(self.index_file, 'wb') as f:
                f.write(encrypted_index)
        
        return True
    
    def cleanup_temp(self):
        """Clean up temporary decrypted files"""
        for file in self.temp_dir.glob("*"):
            try:
                os.remove(file)
            except:
                pass

def main():
    """Command line interface for secure voice manager"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Secure Voice File Manager")
    parser.add_argument("action", choices=["encrypt", "decrypt", "list", "delete", "cleanup"], 
                       help="Action to perform")
    parser.add_argument("--file", help="File to encrypt/decrypt")
    parser.add_argument("--id", help="File ID for decrypt/delete operations")
    parser.add_argument("--description", help="Description for encrypted file")
    parser.add_argument("--output", help="Output path for decrypted file")
    
    args = parser.parse_args()
    
    manager = SecureVoiceManager()
    
    if not manager.authenticate():
        sys.exit(1)
    
    try:
        if args.action == "encrypt":
            if not args.file:
                print("❌ --file required for encrypt")
                sys.exit(1)
            file_id = manager.encrypt_file(args.file, args.description or "")
            print(f"File ID: {file_id}")
        
        elif args.action == "decrypt":
            if not args.id:
                print("❌ --id required for decrypt")
                sys.exit(1)
            output_path = manager.decrypt_file(args.id, args.output)
            print(f"Decrypted to: {output_path}")
        
        elif args.action == "list":
            files = manager.list_files()
            if not files:
                print("No encrypted files found")
            else:
                print("\nEncrypted Voice Files:")
                print("-" * 50)
                for file_id, metadata in files.items():
                    print(f"ID: {file_id}")
                    print(f"  Original: {metadata['original_name']}")
                    print(f"  Time: {metadata['timestamp']}")
                    print(f"  Description: {metadata['description']}")
                    print(f"  Size: {metadata['size']} bytes")
                    print()
        
        elif args.action == "delete":
            if not args.id:
                print("❌ --id required for delete")
                sys.exit(1)
            if manager.delete_file(args.id):
                print(f"✅ Deleted {args.id}")
            else:
                print(f"❌ File not found: {args.id}")
        
        elif args.action == "cleanup":
            manager.cleanup_temp()
            print("✅ Temporary files cleaned up")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()