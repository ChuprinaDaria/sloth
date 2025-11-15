"""
Encryption utilities for sensitive data
"""
from cryptography.fernet import Fernet
from django.conf import settings
import base64
import hashlib


def get_fernet_key():
    """Get or generate Fernet key from settings"""
    # Use FERNET_KEY from settings if available, otherwise derive from SECRET_KEY
    if hasattr(settings, 'FERNET_KEY'):
        key = settings.FERNET_KEY
    else:
        # Derive a valid Fernet key from SECRET_KEY
        key = base64.urlsafe_b64encode(
            hashlib.sha256(settings.SECRET_KEY.encode()).digest()
        )

    # Ensure it's bytes
    if isinstance(key, str):
        key = key.encode()

    return key


def encrypt_api_key(plaintext: str) -> str:
    """
    Encrypt API key using Fernet symmetric encryption

    Args:
        plaintext: Plain text API key

    Returns:
        Encrypted string (base64 encoded)
    """
    if not plaintext:
        return ""

    f = Fernet(get_fernet_key())
    encrypted = f.encrypt(plaintext.encode())
    return encrypted.decode()


def decrypt_api_key(ciphertext: str) -> str:
    """
    Decrypt API key

    Args:
        ciphertext: Encrypted API key

    Returns:
        Decrypted plain text API key
    """
    if not ciphertext:
        return ""

    try:
        f = Fernet(get_fernet_key())
        decrypted = f.decrypt(ciphertext.encode())
        return decrypted.decode()
    except Exception as e:
        # Log error but don't expose details
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to decrypt API key: {type(e).__name__}")
        raise ValueError("Failed to decrypt API key")


def mask_api_key(api_key: str, show_first: int = 3, show_last: int = 4) -> str:
    """
    Mask API key for display

    Args:
        api_key: Full API key
        show_first: Number of characters to show at start
        show_last: Number of characters to show at end

    Returns:
        Masked key like "sk-...xyz1234"
    """
    if not api_key or len(api_key) < (show_first + show_last):
        return "***"

    return f"{api_key[:show_first]}...{api_key[-show_last:]}"
