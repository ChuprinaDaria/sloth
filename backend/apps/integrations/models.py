from django.db import models
from django.core.exceptions import ValidationError
import json
import base64
import hashlib
from cryptography.fernet import Fernet
from django.conf import settings


class Integration(models.Model):
    """
    Зовнішні інтеграції (в tenant schema)
    """
    TYPE_CHOICES = [
        ('telegram', 'Telegram Bot'),
        ('whatsapp', 'WhatsApp Business'),
        ('google_calendar', 'Google Calendar'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending Setup'),
        ('active', 'Active'),
        ('error', 'Error'),
        ('disabled', 'Disabled'),
    ]

    user_id = models.IntegerField(db_index=True)
    integration_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Encrypted credentials
    credentials_encrypted = models.TextField(blank=True)

    # Settings (non-sensitive)
    settings = models.JSONField(default=dict, blank=True)

    # Stats
    messages_received = models.IntegerField(default=0)
    messages_sent = models.IntegerField(default=0)
    last_activity = models.DateTimeField(null=True, blank=True)

    # Error tracking
    error_message = models.TextField(blank=True)
    error_count = models.IntegerField(default=0)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'integrations'
        verbose_name = 'Integration'
        verbose_name_plural = 'Integrations'
        unique_together = ['user_id', 'integration_type']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_integration_type_display()} - {self.status}"

    @staticmethod
    def _get_encryption_key():
        """Generate proper Fernet key from SECRET_KEY using SHA256"""
        # Use SHA256 to generate 32-byte key from SECRET_KEY (regardless of its length)
        key_bytes = hashlib.sha256(settings.SECRET_KEY.encode()).digest()
        # Fernet requires base64-encoded key
        return base64.urlsafe_b64encode(key_bytes)

    @staticmethod
    def _get_legacy_key():
        """Legacy key generation (for backwards compatibility)"""
        # Old insecure method - only for migration
        return settings.SECRET_KEY.encode()[:32]

    def set_credentials(self, credentials_dict):
        """Encrypt and store credentials"""
        # Use proper encryption key
        key = self._get_encryption_key()
        f = Fernet(key)

        credentials_json = json.dumps(credentials_dict)
        encrypted = f.encrypt(credentials_json.encode())
        self.credentials_encrypted = encrypted.decode()

    def get_credentials(self):
        """Decrypt and return credentials"""
        if not self.credentials_encrypted:
            return {}

        # Try new key first
        try:
            key = self._get_encryption_key()
            f = Fernet(key)
            decrypted = f.decrypt(self.credentials_encrypted.encode())
            return json.loads(decrypted.decode())
        except Exception:
            # Try legacy key for backwards compatibility
            try:
                legacy_key = self._get_legacy_key()
                f = Fernet(legacy_key)
                decrypted = f.decrypt(self.credentials_encrypted.encode())
                credentials = json.loads(decrypted.decode())

                # Re-encrypt with new key and save
                self.set_credentials(credentials)
                self.save(update_fields=['credentials_encrypted'])

                return credentials
            except Exception as e:
                print(f"Error decrypting credentials: {e}")
                return {}


class WebhookEvent(models.Model):
    """
    Вебхуки від інтеграцій (в tenant schema)
    """
    integration = models.ForeignKey(Integration, on_delete=models.CASCADE, related_name='webhook_events')
    event_type = models.CharField(max_length=100)
    payload = models.JSONField()

    # Processing
    is_processed = models.BooleanField(default=False)
    processed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'webhook_events'
        verbose_name = 'Webhook Event'
        verbose_name_plural = 'Webhook Events'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['integration', '-created_at']),
            models.Index(fields=['is_processed']),
        ]

    def __str__(self):
        return f"{self.event_type} - {self.created_at}"
