from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import Subscription
from .services import StripeService


@shared_task
def check_trial_expirations():
    """Check and update trial subscriptions that have expired"""
    expired_trials = Subscription.objects.filter(
        status='trialing',
        trial_end__lte=timezone.now()
    )

    for subscription in expired_trials:
        if subscription.stripe_subscription_id:
            # Stripe will handle billing
            subscription.status = 'active'
        else:
            # No payment method, mark as unpaid
            subscription.status = 'unpaid'

        subscription.save()

    return f"Processed {expired_trials.count()} expired trials"


@shared_task
def process_subscription_billing():
    """Process subscription billing for the day"""
    stripe_service = StripeService()

    subscriptions_to_bill = Subscription.objects.filter(
        status='active',
        current_period_end__date=timezone.now().date()
    )

    for subscription in subscriptions_to_bill:
        if subscription.stripe_subscription_id:
            try:
                # Retrieve latest subscription data from Stripe
                stripe_sub = stripe_service.get_subscription(subscription.stripe_subscription_id)

                # Update local subscription
                subscription.current_period_start = timezone.datetime.fromtimestamp(
                    stripe_sub.current_period_start
                )
                subscription.current_period_end = timezone.datetime.fromtimestamp(
                    stripe_sub.current_period_end
                )
                subscription.status = stripe_sub.status
                subscription.save()

            except Exception as e:
                print(f"Error processing subscription {subscription.id}: {e}")

    return f"Processed {subscriptions_to_bill.count()} subscriptions"


@shared_task
def check_usage_limits():
    """Check and notify users approaching usage limits"""
    subscriptions = Subscription.objects.filter(status__in=['trialing', 'active'])

    for subscription in subscriptions:
        # Check each limit type
        limits_exceeded = []

        if subscription.used_messages >= subscription.plan.max_messages_per_month:
            limits_exceeded.append('messages')

        if subscription.used_photos >= subscription.plan.max_photos_per_month:
            limits_exceeded.append('photos')

        if subscription.used_documents >= subscription.plan.max_documents:
            limits_exceeded.append('documents')

        if limits_exceeded:
            # TODO: Send notification email
            print(f"Limits exceeded for {subscription.organization.name}: {limits_exceeded}")

    return f"Checked {subscriptions.count()} subscriptions"


@shared_task
def reset_monthly_usage():
    """Reset monthly usage counters"""
    subscriptions = Subscription.objects.filter(
        status__in=['trialing', 'active'],
        usage_reset_at__lte=timezone.now()
    )

    for subscription in subscriptions:
        subscription.used_messages = 0
        subscription.used_photos = 0
        subscription.used_documents = 0
        subscription.usage_reset_at = timezone.now() + timedelta(days=30)
        subscription.save()

    return f"Reset usage for {subscriptions.count()} subscriptions"
