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

    # Sphere - reference to Sphere ID in public schema
    sphere_id = models.IntegerField(null=True, blank=True, db_index=True)

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


class Sphere(models.Model):
    """
    Сфера діяльності (Sphere of Business) - в public schema
    Визначає область бізнесу користувача та доступні інтеграції
    """
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, db_index=True)
    description = models.TextField(blank=True)

    # Display
    icon = models.CharField(max_length=100, blank=True)  # CSS class or emoji
    color = models.CharField(max_length=7, default='#3B82F6')  # Hex color

    # Status
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'spheres'
        verbose_name = 'Sphere'
        verbose_name_plural = 'Spheres'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class IntegrationType(models.Model):
    """
    Тип інтеграції (в public schema)
    Визначає які інтеграції доступні для кожної сфери
    """
    # Загальні інтеграції
    GENERAL = 'general'

    # Google Suite
    GOOGLE_CALENDAR = 'google_calendar'
    GOOGLE_MEET = 'google_meet'
    GOOGLE_SHEETS = 'google_sheets'
    GMAIL = 'gmail'

    # Соціальні мережі та месенджери
    TELEGRAM = 'telegram'
    WHATSAPP = 'whatsapp'
    INSTAGRAM = 'instagram'
    FACEBOOK_MESSENGER = 'facebook_messenger'

    # Scheduling
    CALENDLY = 'calendly'
    ZOOM = 'zoom'

    # Beauty Sphere
    BOOKSY = 'booksy'
    DIKIDI = 'dikidi'
    EASYWEEK = 'easyweek'
    TREATWELL = 'treatwell'
    PLANITY = 'planity'
    RESERVIO = 'reservio'
    SALONIZED = 'salonized'
    SIMPLYBOOK_ME = 'simplybook_me'
    SQUARE_APPOINTMENTS = 'square_appointments'
    FRESHA = 'fresha'

    # Health Sphere
    ZNANY_LEKARZ = 'znany_lekarz'  # Doctoralia
    DOCTOLIB = 'doctolib'
    JAMEDA = 'jameda'
    DOC_UA = 'doc_ua'
    HELSI = 'helsi'
    PATIENT_ACCESS = 'patient_access'
    ZOCDOC = 'zocdoc'
    PRACTO = 'practo'

    INTEGRATION_TYPE_CHOICES = [
        # General
        (GOOGLE_CALENDAR, 'Google Calendar'),
        (GOOGLE_MEET, 'Google Meet'),
        (GOOGLE_SHEETS, 'Google Sheets'),
        (GMAIL, 'Gmail'),
        (TELEGRAM, 'Telegram'),
        (WHATSAPP, 'WhatsApp'),
        (INSTAGRAM, 'Instagram'),
        (FACEBOOK_MESSENGER, 'Facebook Messenger'),
        (CALENDLY, 'Calendly'),
        (ZOOM, 'Zoom'),

        # Beauty
        (BOOKSY, 'Booksy'),
        (DIKIDI, 'Dikidi'),
        (EASYWEEK, 'EasyWeek'),
        (TREATWELL, 'Treatwell'),
        (PLANITY, 'Planity'),
        (RESERVIO, 'Reservio'),
        (SALONIZED, 'Salonized'),
        (SIMPLYBOOK_ME, 'SimplyBook.me'),
        (SQUARE_APPOINTMENTS, 'Square Appointments'),
        (FRESHA, 'Fresha'),

        # Health
        (ZNANY_LEKARZ, 'Znany Lekarz / Doctoralia'),
        (DOCTOLIB, 'Doctolib'),
        (JAMEDA, 'Jameda'),
        (DOC_UA, 'Doc.ua'),
        (HELSI, 'Helsi'),
        (PATIENT_ACCESS, 'Patient Access'),
        (ZOCDOC, 'Zocdoc'),
        (PRACTO, 'Practo'),
    ]

    slug = models.SlugField(unique=True, db_index=True, max_length=50)
    name = models.CharField(max_length=100)
    integration_type = models.CharField(max_length=50, choices=INTEGRATION_TYPE_CHOICES)
    description = models.TextField(blank=True)

    # Spheres (Many-to-Many)
    spheres = models.ManyToManyField(Sphere, related_name='integration_types')

    # OAuth/API Configuration
    requires_oauth = models.BooleanField(default=True)
    oauth_provider = models.CharField(max_length=50, blank=True)  # google, facebook, custom
    api_documentation_url = models.URLField(blank=True)

    # Features
    supports_webhooks = models.BooleanField(default=False)
    supports_working_hours = models.BooleanField(default=False)  # True для Meta та Telegram

    # Display
    icon_url = models.URLField(blank=True)
    logo_url = models.URLField(blank=True)
    color = models.CharField(max_length=7, default='#3B82F6')

    # Availability by country (JSON array of country codes)
    available_countries = models.JSONField(default=list, blank=True)

    # Status
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'integration_types'
        verbose_name = 'Integration Type'
        verbose_name_plural = 'Integration Types'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name
