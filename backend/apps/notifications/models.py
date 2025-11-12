from django.db import models
from django.contrib.postgres.fields import JSONField
from django.utils import timezone


class PushToken(models.Model):
    """Store Expo push tokens for mobile devices"""

    user_id = models.IntegerField(db_index=True)
    expo_push_token = models.CharField(max_length=255, unique=True)
    device_name = models.CharField(max_length=255, blank=True)
    device_type = models.CharField(max_length=50, default='mobile')  # mobile, tablet
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_used_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'push_tokens'
        indexes = [
            models.Index(fields=['user_id', 'is_active']),
        ]

    def __str__(self):
        return f"PushToken for user {self.user_id}: {self.expo_push_token[:20]}..."


class NotificationSettings(models.Model):
    """User preferences for push notifications"""

    FREQUENCY_CHOICES = [
        ('all', 'Всі повідомлення'),
        ('important', 'Тільки важливі'),
        ('critical', 'Тільки критичні'),
        ('none', 'Вимкнено'),
    ]

    user_id = models.IntegerField(unique=True, db_index=True)

    # General settings
    enabled = models.BooleanField(default=True)
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='all')

    # Quiet hours
    quiet_hours_enabled = models.BooleanField(default=True)
    quiet_hours_start = models.TimeField(default='22:00')  # 22:00
    quiet_hours_end = models.TimeField(default='08:00')    # 08:00

    # Notification types
    critical_enabled = models.BooleanField(default=True)  # VIP messages, integration failures, negative reviews
    important_enabled = models.BooleanField(default=True)  # Analytics, holidays, achievements
    useful_enabled = models.BooleanField(default=True)    # Weekly reports, recommendations

    # Specific notification types
    vip_messages = models.BooleanField(default=True)
    integration_issues = models.BooleanField(default=True)
    negative_reviews = models.BooleanField(default=True)
    smart_analytics = models.BooleanField(default=True)
    holidays_reminders = models.BooleanField(default=True)
    achievements = models.BooleanField(default=True)
    pending_conversations = models.BooleanField(default=True)
    weekly_reports = models.BooleanField(default=True)
    pricing_recommendations = models.BooleanField(default=True)
    content_recommendations = models.BooleanField(default=True)

    # Rate limiting
    max_notifications_per_day = models.IntegerField(default=3)  # Excluding critical

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'notification_settings'

    def __str__(self):
        return f"NotificationSettings for user {self.user_id}"

    def is_in_quiet_hours(self):
        """Check if current time is in quiet hours"""
        if not self.quiet_hours_enabled:
            return False

        now = timezone.localtime().time()
        start = self.quiet_hours_start
        end = self.quiet_hours_end

        # Handle overnight quiet hours (e.g., 22:00 - 08:00)
        if start > end:
            return now >= start or now < end
        else:
            return start <= now < end


class NotificationLog(models.Model):
    """Track sent notifications for rate limiting and analytics"""

    PRIORITY_CHOICES = [
        ('critical', 'Критичне'),
        ('important', 'Важливе'),
        ('useful', 'Корисне'),
    ]

    STATUS_CHOICES = [
        ('sent', 'Відправлено'),
        ('failed', 'Помилка'),
        ('skipped', 'Пропущено'),
        ('grouped', 'Згруповано'),
    ]

    user_id = models.IntegerField(db_index=True)
    notification_type = models.CharField(max_length=100)  # vip_message, negative_review, etc.
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES)

    title = models.CharField(max_length=255)
    body = models.TextField()
    data = models.JSONField(default=dict, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='sent')
    error_message = models.TextField(blank=True)

    expo_response = models.JSONField(default=dict, blank=True)

    sent_at = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notification_logs'
        indexes = [
            models.Index(fields=['user_id', 'sent_at']),
            models.Index(fields=['notification_type', 'sent_at']),
        ]
        ordering = ['-sent_at']

    def __str__(self):
        return f"{self.notification_type} for user {self.user_id} - {self.status}"
