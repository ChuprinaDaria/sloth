from django.db import models
from django.utils.translation import gettext_lazy as _


class PrivacyPolicy(models.Model):
    """Privacy Policy content in multiple languages"""

    LANGUAGE_CHOICES = [
        ('uk', 'Українська'),
        ('en', 'English'),
        ('pl', 'Polski'),
        ('ru', 'Русский'),
    ]

    language = models.CharField(
        max_length=2,
        choices=LANGUAGE_CHOICES,
        unique=True,
        verbose_name=_('Language')
    )
    title = models.CharField(
        max_length=255,
        verbose_name=_('Title')
    )
    content = models.TextField(
        verbose_name=_('Content'),
        help_text=_('Supports HTML and Markdown')
    )
    last_updated = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Last Updated')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Active')
    )
    version = models.CharField(
        max_length=50,
        default='1.0',
        verbose_name=_('Version')
    )

    class Meta:
        verbose_name = _('Privacy Policy')
        verbose_name_plural = _('Privacy Policies')
        ordering = ['language']

    def __str__(self):
        return f"{self.get_language_display()} - v{self.version}"


class TermsOfService(models.Model):
    """Terms of Service content in multiple languages"""

    LANGUAGE_CHOICES = [
        ('uk', 'Українська'),
        ('en', 'English'),
        ('pl', 'Polski'),
        ('ru', 'Русский'),
    ]

    language = models.CharField(
        max_length=2,
        choices=LANGUAGE_CHOICES,
        unique=True,
        verbose_name=_('Language')
    )
    title = models.CharField(
        max_length=255,
        verbose_name=_('Title')
    )
    content = models.TextField(
        verbose_name=_('Content'),
        help_text=_('Supports HTML and Markdown')
    )
    last_updated = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Last Updated')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Active')
    )
    version = models.CharField(
        max_length=50,
        default='1.0',
        verbose_name=_('Version')
    )

    class Meta:
        verbose_name = _('Terms of Service')
        verbose_name_plural = _('Terms of Service')
        ordering = ['language']

    def __str__(self):
        return f"{self.get_language_display()} - v{self.version}"


class SupportContact(models.Model):
    """Support contact information"""

    email = models.EmailField(
        default='support@lazysoft.pl',
        verbose_name=_('Support Email')
    )
    telegram = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('Telegram')
    )
    phone = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Phone')
    )
    working_hours = models.CharField(
        max_length=255,
        default='Пн-Пт 9:00-18:00',
        verbose_name=_('Working Hours')
    )
    response_time = models.CharField(
        max_length=100,
        default='До 24 годин',
        verbose_name=_('Response Time')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Active')
    )

    class Meta:
        verbose_name = _('Support Contact')
        verbose_name_plural = _('Support Contacts')

    def __str__(self):
        return self.email

    @classmethod
    def get_active(cls):
        """Get active support contact"""
        return cls.objects.filter(is_active=True).first()


class AppDownloadLinks(models.Model):
    """App download links for iOS and Android"""

    ios_app_id = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('iOS App ID'),
        help_text=_('App Store App ID (numbers only)')
    )
    ios_url = models.URLField(
        blank=True,
        null=True,
        verbose_name=_('iOS App Store URL')
    )
    android_package = models.CharField(
        max_length=100,
        default='pl.lazysoft.slothai',
        verbose_name=_('Android Package Name')
    )
    android_url = models.URLField(
        blank=True,
        null=True,
        verbose_name=_('Android Play Store URL')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Active')
    )
    coming_soon = models.BooleanField(
        default=True,
        verbose_name=_('Coming Soon'),
        help_text=_('Show "Coming Soon" message instead of download links')
    )

    class Meta:
        verbose_name = _('App Download Links')
        verbose_name_plural = _('App Download Links')

    def __str__(self):
        return 'Mobile App Download Links'

    @classmethod
    def get_active(cls):
        """Get active download links"""
        return cls.objects.filter(is_active=True).first()

    def get_ios_url(self):
        """Get full iOS App Store URL"""
        if self.ios_url:
            return self.ios_url
        elif self.ios_app_id:
            return f"https://apps.apple.com/app/id{self.ios_app_id}"
        return None

    def get_android_url(self):
        """Get full Android Play Store URL"""
        if self.android_url:
            return self.android_url
        elif self.android_package:
            return f"https://play.google.com/store/apps/details?id={self.android_package}"
        return None
