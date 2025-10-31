from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.crypto import get_random_string
import secrets


class Organization(models.Model):
    """
    Організація (Tenant) - кожна має окрему PostgreSQL schema
    """
    schema_name = models.CharField(max_length=63, unique=True, db_index=True)
    name = models.CharField(max_length=255)
    domain = models.CharField(max_length=255, unique=True)

    # Owner
    owner = models.ForeignKey(
        'User',
        on_delete=models.PROTECT,
        related_name='owned_organizations',
        null=True
    )

    # Storage limits
    max_storage_mb = models.IntegerField(default=1000)
    used_storage_mb = models.IntegerField(default=0)

    # Status
    is_active = models.BooleanField(default=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'organizations'
        verbose_name = 'Organization'
        verbose_name_plural = 'Organizations'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.schema_name:
            # Generate unique schema name
            self.schema_name = f"tenant_{get_random_string(12).lower()}"
        super().save(*args, **kwargs)


class User(AbstractUser):
    """
    Користувач (в public schema)
    """
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('uk', 'Ukrainian'),
        ('pl', 'Polish'),
        ('de', 'German'),
    ]

    # Organization relationship
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='users',
        null=True,
        blank=True
    )

    # Profile fields
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES, default='en')

    # Referral tracking
    referral_code = models.CharField(max_length=20, unique=True, db_index=True)
    referred_by = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='referred_users'
    )

    # Additional timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']

    def __str__(self):
        return self.email or self.username

    def save(self, *args, **kwargs):
        if not self.referral_code:
            # Generate unique referral code
            self.referral_code = self._generate_referral_code()
        super().save(*args, **kwargs)

    def _generate_referral_code(self):
        """Generate unique referral code"""
        while True:
            code = get_random_string(8).upper()
            if not User.objects.filter(referral_code=code).exists():
                return code


class Profile(models.Model):
    """
    Профіль користувача (в tenant schema)
    Цей модель зберігається в окремій схемі кожного клієнта
    """
    user_id = models.IntegerField(unique=True, db_index=True)

    # Business information
    business_name = models.CharField(max_length=255, blank=True)
    business_type = models.CharField(max_length=100, blank=True)  # salon, spa, clinic
    business_address = models.TextField(blank=True)

    # Settings
    timezone = models.CharField(max_length=50, default='UTC')
    notification_email = models.EmailField()
    notification_telegram = models.BooleanField(default=True)
    notification_whatsapp = models.BooleanField(default=False)

    # Preferences
    preferences = models.JSONField(default=dict, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'profiles'
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'

    def __str__(self):
        return f"Profile for user_id {self.user_id}"


class ApiKey(models.Model):
    """
    API ключі для інтеграцій
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='api_keys')
    name = models.CharField(max_length=255)
    key = models.CharField(max_length=64, unique=True, db_index=True)

    # Permissions
    is_active = models.BooleanField(default=True)

    # Usage tracking
    last_used_at = models.DateTimeField(null=True, blank=True)
    requests_count = models.IntegerField(default=0)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'api_keys'
        verbose_name = 'API Key'
        verbose_name_plural = 'API Keys'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.key[:8]}..."

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self._generate_api_key()
        super().save(*args, **kwargs)

    def _generate_api_key(self):
        """Generate secure API key"""
        return f"sk_{secrets.token_urlsafe(40)}"
