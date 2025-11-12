from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.accounts.models import Organization
from .models import Subscription, Plan


@receiver(post_save, sender=Organization)
def create_default_subscription(sender, instance, created, **kwargs):
    """
    Create default free trial subscription for new organizations
    
    NOTE: Subscription is now created in UserRegistrationSerializer.create()
    to have better control over subscription parameters. This signal is kept
    for backward compatibility but checks if subscription already exists.
    """
    if created:
        # Check if subscription already exists (created by serializer)
        if Subscription.objects.filter(organization=instance).exists():
            return
        
        # Get free/trial plan
        try:
            free_plan = Plan.objects.filter(price_monthly=0).first()
            if not free_plan:
                try:
                    free_plan = Plan.objects.get(slug='free')
                except Plan.DoesNotExist:
                    free_plan = Plan.objects.first()

            if free_plan:
                # Double-check to avoid race condition
                subscription, created_sub = Subscription.objects.get_or_create(
                    organization=instance,
                    defaults={
                        'plan': free_plan,
                        'status': 'trialing'
                    }
                )
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error creating default subscription for {instance.id}: {e}")
