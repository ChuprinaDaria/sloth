#!/usr/bin/env python
"""
Generate a valid Fernet key for encrypting integration credentials
"""
from cryptography.fernet import Fernet

# Generate a new Fernet key
key = Fernet.generate_key()

print("=" * 60)
print("Generated Fernet Key:")
print("=" * 60)
print(key.decode())
print("=" * 60)
print("\nAdd this to your .env file:")
print(f"FERNET_KEY={key.decode()}")
print("=" * 60)
