"""
Signals для автоматичної обробки реферальних подій
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from apps.subscriptions.models import Subscription
from .models import Referral
from .utils import update_referral_stats
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Subscription)
def handle_subscription_change(sender, instance, created, **kwargs):
    """
    Обробляє зміни підписки:
    - Оновлює статус реферала на 'active' коли підписка стає платною
    - Перевіряє умови для автоапгрейду реферера
    """
    if created:
        return  # Не обробляємо нові підписки

    try:
        user = instance.organization.owner
        if not user:
            return

        # Перевіряємо чи користувач має реферрал
        try:
            referral = Referral.objects.get(referred=user)
        except Referral.DoesNotExist:
            return  # Користувач не був зареферений

        # Перевіряємо чи підписка стала активною та платною
        if instance.status == 'active' and instance.plan.slug != 'free':
            if referral.status != 'active':
                # Позначаємо реферрал як активний
                referral.status = 'active'
                if not referral.activated_at:
                    referral.activated_at = timezone.now()
                referral.save()

                logger.info(f"Activated referral for {user.email}, referrer: {referral.referrer.email}")

                # Оновлюємо статистику реферера
                update_referral_stats(referral.referrer)

        # Якщо підписка стала неактивною
        elif instance.status in ['canceled', 'unpaid']:
            if referral.status == 'active':
                referral.status = 'inactive'
                referral.save()

                logger.info(f"Deactivated referral for {user.email}")

                # Оновлюємо статистику реферера
                update_referral_stats(referral.referrer)

    except Exception as e:
        logger.error(f"Error in handle_subscription_change: {str(e)}")
