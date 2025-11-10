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
        ('google_sheets', 'Google Sheets'),
        ('instagram', 'Instagram'),
        ('website_widget', 'Website Widget'),
        ('email', 'Email Integration'),
        ('google_my_business', 'Google My Business'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending Setup'),
        ('active', 'Active'),
        ('error', 'Error'),
        ('disabled', 'Disabled'),
    ]

    user_id = models.IntegerField(db_index=True)
    integration_type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Encrypted credentials
    credentials_encrypted = models.TextField(blank=True)

    # Settings (non-sensitive)
    settings = models.JSONField(default=dict, blank=True)

    # Configuration (non-sensitive, for integration-specific settings)
    config = models.JSONField(default=dict, blank=True)

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
        if not settings.FERNET_KEY:
            raise ValueError(
                "FERNET_KEY not found in settings. "
                "Generate one with: python backend/generate_fernet_key.py"
            )

        # Use Fernet for symmetric encryption
        f = Fernet(settings.FERNET_KEY.encode())

        credentials_json = json.dumps(credentials_dict)
        encrypted = f.encrypt(credentials_json.encode())
        self.credentials_encrypted = encrypted.decode()

    def get_credentials(self):
        """Decrypt and return credentials"""
        if not self.credentials_encrypted:
            return {}

        if not settings.FERNET_KEY:
            raise ValueError(
                "FERNET_KEY not found in settings. "
                "Generate one with: python backend/generate_fernet_key.py"
            )

        f = Fernet(settings.FERNET_KEY.encode())

        try:
            decrypted = f.decrypt(self.credentials_encrypted.encode())
            return json.loads(decrypted.decode())
        except Exception as e:
            print(f"Error decrypting credentials: {e}")
            return {}

    @property
    def is_active(self):
        """Check if integration is active"""
        return self.status == 'active'

    @property
    def organization(self):
        """Get organization from user"""
        from apps.accounts.models import User
        try:
            user = User.objects.get(id=self.user_id)
            return user.organization
        except User.DoesNotExist:
            return None


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


class InstagramPost(models.Model):
    """
    Instagram пости з embeddings для RAG (в tenant schema)
    Тільки для Enterprise тарифу
    """
    user_id = models.IntegerField(db_index=True)
    post_id = models.CharField(max_length=255, unique=True, db_index=True)

    # Post data
    caption = models.TextField(blank=True)
    media_type = models.CharField(max_length=50, default='IMAGE')  # IMAGE, VIDEO, CAROUSEL_ALBUM
    media_url = models.URLField(blank=True)
    permalink = models.URLField(blank=True)

    # Metrics
    likes = models.IntegerField(default=0)
    comments = models.IntegerField(default=0)
    engagement = models.IntegerField(default=0)
    impressions = models.IntegerField(default=0)
    reach = models.IntegerField(default=0)

    # Analysis
    hashtags = models.JSONField(default=list, blank=True)  # List of hashtags
    embedding = models.JSONField(default=list, blank=True)  # Vector embedding for RAG

    # Timestamps
    posted_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'instagram_posts'
        verbose_name = 'Instagram Post'
        verbose_name_plural = 'Instagram Posts'
        ordering = ['-posted_at']
        indexes = [
            models.Index(fields=['user_id', '-posted_at']),
            models.Index(fields=['post_id']),
        ]

    def __str__(self):
        return f"Instagram post {self.post_id} - {self.caption[:50]}"
