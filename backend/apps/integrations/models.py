from django.db import models
from django.core.exceptions import ValidationError
import json
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

    def set_credentials(self, credentials_dict):
        """Encrypt and store credentials"""
        # Use Fernet for symmetric encryption
        key = settings.SECRET_KEY.encode()[:32]  # Use first 32 bytes of SECRET_KEY
        f = Fernet(key)

        credentials_json = json.dumps(credentials_dict)
        encrypted = f.encrypt(credentials_json.encode())
        self.credentials_encrypted = encrypted.decode()

    def get_credentials(self):
        """Decrypt and return credentials"""
        if not self.credentials_encrypted:
            return {}

        key = settings.SECRET_KEY.encode()[:32]
        f = Fernet(key)

        try:
            decrypted = f.decrypt(self.credentials_encrypted.encode())
            return json.loads(decrypted.decode())
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


class PhotoRecognitionProvider(models.Model):
    """
    AI models for photo recognition (global, not tenant-specific)
    Stored in public schema
    """
    slug = models.SlugField(max_length=50, unique=True, db_index=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    # API configuration
    requires_api_key = models.BooleanField(default=True)
    api_documentation_url = models.URLField(max_length=500, blank=True)

    # Pricing
    cost_per_image = models.DecimalField(
        max_digits=10,
        decimal_places=5,
        help_text="Estimated cost per image in USD"
    )

    # Availability
    available_in_professional_only = models.BooleanField(
        default=False,
        help_text="If True, only Professional plan users can use this provider"
    )
    is_active = models.BooleanField(default=True)

    # UI ordering
    order = models.IntegerField(default=0)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'photo_recognition_providers'
        verbose_name = 'Photo Recognition Provider'
        verbose_name_plural = 'Photo Recognition Providers'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class UserPhotoRecognitionConfig(models.Model):
    """
    User's configuration for photo recognition providers (in tenant schema)
    """
    user_id = models.IntegerField(db_index=True)
    provider = models.ForeignKey(
        PhotoRecognitionProvider,
        on_delete=models.CASCADE,
        related_name='user_configs'
    )

    # Encrypted API key
    api_key_encrypted = models.TextField()

    # Status
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)

    # Stats
    images_processed = models.IntegerField(default=0)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    last_used_at = models.DateTimeField(null=True, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_photo_recognition_configs'
        verbose_name = 'User Photo Recognition Config'
        verbose_name_plural = 'User Photo Recognition Configs'
        unique_together = ['user_id', 'provider']
        ordering = ['-is_default', '-created_at']
        indexes = [
            models.Index(fields=['user_id', 'is_default']),
            models.Index(fields=['user_id', 'is_active']),
        ]

    def __str__(self):
        return f"User {self.user_id} - {self.provider.name}"

    def save(self, *args, **kwargs):
        # Ensure only one default per user
        if self.is_default:
            UserPhotoRecognitionConfig.objects.filter(
                user_id=self.user_id,
                is_default=True
            ).exclude(id=self.id).update(is_default=False)
        super().save(*args, **kwargs)

    def get_masked_key(self):
        """Return masked API key for display"""
        if not self.api_key_encrypted:
            return ""
        try:
            from apps.core.utils.encryption import decrypt_api_key
            full_key = decrypt_api_key(self.api_key_encrypted)
            if len(full_key) > 8:
                return f"{full_key[:3]}...{full_key[-4:]}"
            return "***"
        except Exception:
            return "***"

