from django.db import models
from django.utils import timezone
from django.utils.crypto import get_random_string
from datetime import timedelta
from apps.accounts.models import Organization, User


class Plan(models.Model):
    """
    Тарифні плани (в public schema)
    """
    PLAN_TYPE_CHOICES = [
        ('free', 'Free Forever'),
        ('paid', 'Paid Plan'),
    ]

    name = models.CharField(max_length=100)  # Free, Starter, Professional, Enterprise
    slug = models.SlugField(unique=True, db_index=True)
    description = models.TextField(blank=True)
    plan_type = models.CharField(max_length=10, choices=PLAN_TYPE_CHOICES, default='paid')

    # Pricing (0 for free plan)
    price_monthly = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    price_yearly = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Stripe
    stripe_price_id_monthly = models.CharField(max_length=255, blank=True)
    stripe_price_id_yearly = models.CharField(max_length=255, blank=True)

    # Limits
    max_users = models.IntegerField(default=1)
    max_documents = models.IntegerField(default=100)
    max_photos_per_month = models.IntegerField(default=1000)
    max_messages_per_month = models.IntegerField(default=5000)
    max_conversations_per_month = models.IntegerField(default=50)  # For FREE plan
    max_integrations = models.IntegerField(default=1)  # Max number of active integrations
    max_storage_mb = models.IntegerField(default=1000)

    # Features (JSON array of feature slugs)
    features = models.JSONField(default=list)

    # Watermark
    has_watermark = models.BooleanField(default=True)  # Show "Powered by Sloth" watermark

    # Status
    is_active = models.BooleanField(default=True)
    is_public = models.BooleanField(default=True)  # Show in pricing page
    order = models.IntegerField(default=0)  # Display order

    class Meta:
        db_table = 'plans'
        verbose_name = 'Plan'
        verbose_name_plural = 'Plans'
        ordering = ['order', 'price_monthly']

    def __str__(self):
        return self.name


class Subscription(models.Model):
    """
    Підписка організації (в public schema)
    """
    STATUS_CHOICES = [
        ('free', 'Free Forever'),  # Free plan with limits
        ('active', 'Active'),       # Paid plan active
        ('past_due', 'Past Due'),
        ('canceled', 'Canceled'),
        ('unpaid', 'Unpaid'),
    ]

    BILLING_CYCLE_CHOICES = [
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
        ('lifetime', 'Lifetime'),
    ]

    organization = models.OneToOneField(
        Organization,
        on_delete=models.CASCADE,
        related_name='subscription'
    )
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT, related_name='subscriptions')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='free')

    # Billing
    stripe_subscription_id = models.CharField(max_length=255, blank=True)
    stripe_customer_id = models.CharField(max_length=255, blank=True)
    billing_cycle = models.CharField(
        max_length=10,
        choices=BILLING_CYCLE_CHOICES,
        default='monthly'
    )

    # Trial period (kept for backward compatibility, but not used for free plan)
    trial_start = models.DateTimeField(default=timezone.now, null=True, blank=True)
    trial_end = models.DateTimeField(null=True, blank=True)

    # Billing period
    current_period_start = models.DateTimeField(default=timezone.now)
    current_period_end = models.DateTimeField(null=True, blank=True)

    # Cancellation
    cancel_at_period_end = models.BooleanField(default=False)
    canceled_at = models.DateTimeField(null=True, blank=True)

    # Usage tracking (resets monthly)
    used_messages = models.IntegerField(default=0)
    used_photos = models.IntegerField(default=0)
    used_documents = models.IntegerField(default=0)
    used_conversations = models.IntegerField(default=0)  # Track conversations for FREE plan
    usage_reset_at = models.DateTimeField(default=timezone.now)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'subscriptions'
        verbose_name = 'Subscription'
        verbose_name_plural = 'Subscriptions'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.organization.name} - {self.plan.name} ({self.status})"

    def save(self, *args, **kwargs):
        # Set current_period_end if not set (only for paid plans)
        if not self.pk and not self.current_period_end and self.status != 'free':
            if self.billing_cycle == 'monthly':
                self.current_period_end = self.current_period_start + timedelta(days=30)
            elif self.billing_cycle == 'yearly':
                self.current_period_end = self.current_period_start + timedelta(days=365)

        super().save(*args, **kwargs)

    def is_free_plan(self):
        """Check if this is a free plan"""
        return self.plan.plan_type == 'free' or self.status == 'free'

    def has_watermark(self):
        """Check if should show watermark"""
        return self.plan.has_watermark

    def is_within_limits(self, limit_type):
        """Check if subscription is within usage limits"""
        limits = {
            'messages': (self.used_messages, self.plan.max_messages_per_month),
            'photos': (self.used_photos, self.plan.max_photos_per_month),
            'documents': (self.used_documents, self.plan.max_documents),
            'conversations': (self.used_conversations, self.plan.max_conversations_per_month),
        }

        if limit_type in limits:
            used, max_allowed = limits[limit_type]
            return used < max_allowed

        return True

    def has_feature(self, feature_slug):
        """Check if subscription plan has a specific feature"""
        return feature_slug in self.plan.features

    def can_use_email_integration(self):
        """Check if user can use email integration (not available on FREE plan)"""
        return not self.is_free_plan()

    def can_add_integration(self):
        """Check if user can add more integrations"""
        from apps.integrations.models import Integration

        # Count active integrations for this user's organization
        active_integrations = Integration.objects.filter(
            user_id__in=self.organization.users.values_list('id', flat=True),
            status='active'
        ).count()

        return active_integrations < self.plan.max_integrations

    def increment_usage(self, usage_type):
        """Increment usage counter"""
        if usage_type == 'messages':
            self.used_messages += 1
        elif usage_type == 'photos':
            self.used_photos += 1
        elif usage_type == 'documents':
            self.used_documents += 1
        elif usage_type == 'conversations':
            self.used_conversations += 1

        self.save(update_fields=[f'used_{usage_type}'])

    def reset_monthly_usage(self):
        """Reset usage counters (called monthly by celery task)"""
        self.used_messages = 0
        self.used_photos = 0
        self.used_conversations = 0
        self.usage_reset_at = timezone.now()
        self.save(update_fields=['used_messages', 'used_photos', 'used_conversations', 'usage_reset_at'])


class ActivationCode(models.Model):
    """
    Коди активації для безкоштовних підписок (адмін панель)
    """
    code = models.CharField(max_length=50, unique=True, db_index=True)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, related_name='activation_codes')

    # Duration (0 = unlimited/lifetime)
    duration_days = models.IntegerField(default=30)

    # Creator
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_codes'
    )

    # Usage
    is_used = models.BooleanField(default=False)
    used_by = models.ForeignKey(
        Organization,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='used_codes'
    )
    used_at = models.DateTimeField(null=True, blank=True)

    # Expiration
    expires_at = models.DateTimeField(null=True, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'activation_codes'
        verbose_name = 'Activation Code'
        verbose_name_plural = 'Activation Codes'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.code} - {self.plan.name}"

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self._generate_code()
        super().save(*args, **kwargs)

    def _generate_code(self):
        """Generate unique activation code"""
        while True:
            code = f"SLOTH-{get_random_string(8).upper()}"
            if not ActivationCode.objects.filter(code=code).exists():
                return code

    def is_valid(self):
        """Check if code is still valid"""
        if self.is_used:
            return False
        if self.expires_at and timezone.now() > self.expires_at:
            return False
        return True


class Invoice(models.Model):
    """
    Рахунки (в public schema)
    """
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('open', 'Open'),
        ('paid', 'Paid'),
        ('uncollectible', 'Uncollectible'),
        ('void', 'Void'),
    ]

    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.CASCADE,
        related_name='invoices'
    )

    # Stripe
    stripe_invoice_id = models.CharField(max_length=255, blank=True)

    # Amount
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')

    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')

    # Dates
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()
    due_date = models.DateTimeField(null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    # PDF
    invoice_pdf = models.URLField(blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'invoices'
        verbose_name = 'Invoice'
        verbose_name_plural = 'Invoices'
        ordering = ['-created_at']

    def __str__(self):
        return f"Invoice {self.id} - {self.subscription.organization.name}"
