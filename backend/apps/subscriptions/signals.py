from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.accounts.models import Organization
from .models import Subscription, Plan


@receiver(post_save, sender=Organization)
def create_default_subscription(sender, instance, created, **kwargs):
    """
    Create default free trial subscription for new organizations
    """
    if created:
        # Get free/trial plan
        try:
            free_plan = Plan.objects.filter(price_monthly=0).first()
            if not free_plan:
                free_plan = Plan.objects.first()

            if free_plan:
                Subscription.objects.create(
                    organization=instance,
                    plan=free_plan,
                    status='trialing'
                )
        except Exception as e:
            print(f"Error creating default subscription: {e}")
