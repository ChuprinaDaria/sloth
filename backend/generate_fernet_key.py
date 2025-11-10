#!/usr/bin/env python
"""
Generate a Fernet encryption key for securing sensitive data.

Usage: python backend/generate_fernet_key.py
"""
from cryptography.fernet import Fernet

if __name__ == '__main__':
    key = Fernet.generate_key()
    print("Generated FERNET_KEY:")
    print(key.decode())
    print("\nAdd this to your .env file:")
    print(f"FERNET_KEY={key.decode()}")
