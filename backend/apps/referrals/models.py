from django.db import models
from apps.accounts.models import User


class ReferralCode(models.Model):
    """
    Реферальний код користувача (в public schema)
    Note: Users already have referral_code field, this is for extended stats
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='referral_stats')
    code = models.CharField(max_length=20, unique=True, db_index=True)

    # Statistics
    total_signups = models.IntegerField(default=0)
    active_referrals = models.IntegerField(default=0)  # users with active subscription

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'referral_codes'
        verbose_name = 'Referral Code'
        verbose_name_plural = 'Referral Codes'

    def __str__(self):
        return f"{self.user.email} - {self.code}"


class Referral(models.Model):
    """
    Реферальне відношення (в public schema)
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),      # зареєструвався, але не активував підписку
        ('active', 'Active'),        # активна підписка
        ('inactive', 'Inactive'),    # неактивна підписка
    ]

    referrer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='referrals_given'
    )
    referred = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='referral_received'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    activated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'referrals'
        verbose_name = 'Referral'
        verbose_name_plural = 'Referrals'
        unique_together = ['referrer', 'referred']

    def __str__(self):
        return f"{self.referrer.email} -> {self.referred.email}"


class ReferralReward(models.Model):
    """
    Нагороди за досягнення реферальних цілей (в public schema)
    """
    REWARD_TYPE_CHOICES = [
        ('plan_upgrade', 'Plan Upgrade'),
        ('discount', 'Discount'),
        ('credits', 'Credits'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='referral_rewards')
    reward_type = models.CharField(max_length=20, choices=REWARD_TYPE_CHOICES, default='plan_upgrade')

    # Condition
    referral_count = models.IntegerField()  # 50, 100, 150...

    # Reward details
    old_plan = models.ForeignKey(
        'subscriptions.Plan',
        on_delete=models.SET_NULL,
        null=True,
        related_name='+'
    )
    new_plan = models.ForeignKey(
        'subscriptions.Plan',
        on_delete=models.SET_NULL,
        null=True,
        related_name='+'
    )

    # Metadata
    metadata = models.JSONField(default=dict, blank=True)

    # Timestamps
    granted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'referral_rewards'
        verbose_name = 'Referral Reward'
        verbose_name_plural = 'Referral Rewards'
        ordering = ['-granted_at']

    def __str__(self):
        return f"{self.user.email} - {self.referral_count} referrals"
