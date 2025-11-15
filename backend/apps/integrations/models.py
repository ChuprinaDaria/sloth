from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
import json
from cryptography.fernet import Fernet
from django.conf import settings


class Integration(models.Model):
    """
    Зовнішні інтеграції (в tenant schema)
    """
    STATUS_CHOICES = [
        ('pending', 'Pending Setup'),
        ('active', 'Active'),
        ('error', 'Error'),
        ('disabled', 'Disabled'),
    ]

    user_id = models.IntegerField(db_index=True)

    # Reference to IntegrationType in public schema (by ID)
    integration_type_id = models.IntegerField(db_index=True)
    integration_type_slug = models.CharField(max_length=50)  # Denormalized for quick access

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
        unique_together = ['user_id', 'integration_type_id']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.integration_type_slug} - {self.status}"

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


class IntegrationWorkingHours(models.Model):
    """
    Години роботи AI агента для інтеграцій (в tenant schema)
    Визначає коли замість користувача відповідає AI агент
    Використовується для Meta (Instagram, Facebook Messenger) та Telegram
    """
    WEEKDAY_CHOICES = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]

    integration = models.ForeignKey(
        Integration,
        on_delete=models.CASCADE,
        related_name='working_hours'
    )

    # Weekday (0=Monday, 6=Sunday)
    weekday = models.IntegerField(choices=WEEKDAY_CHOICES)

    # Time range (AI agent works during these hours)
    start_time = models.TimeField()  # e.g., 09:00
    end_time = models.TimeField()    # e.g., 18:00

    # Is enabled
    is_enabled = models.BooleanField(default=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'integration_working_hours'
        verbose_name = 'Integration Working Hours'
        verbose_name_plural = 'Integration Working Hours'
        ordering = ['weekday', 'start_time']
        indexes = [
            models.Index(fields=['integration', 'weekday']),
        ]

    def __str__(self):
        return f"{self.integration} - {self.get_weekday_display()} {self.start_time}-{self.end_time}"

    def is_working_now(self):
        """Check if AI agent should be working right now"""
        if not self.is_enabled:
            return False

        now = timezone.now()
        current_weekday = now.weekday()
        current_time = now.time()

        if current_weekday != self.weekday:
            return False

        return self.start_time <= current_time <= self.end_time
