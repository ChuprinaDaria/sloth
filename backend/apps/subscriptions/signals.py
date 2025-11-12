from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.accounts.models import Organization
from .models import Subscription, Plan


@receiver(post_save, sender=Organization)
def create_default_subscription(sender, instance, created, **kwargs):
    """
    Disabled: subscription is created explicitly in UserRegistrationSerializer.create().
    This signal no longer creates subscriptions to avoid race conditions.
    """
    return
