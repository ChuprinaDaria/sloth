"""
Utilities для роботи з реферальною системою
"""
from django.utils import timezone
from django.db import transaction
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


def check_and_apply_referral_upgrade(user):
    """
    Перевіряє чи користувач заслужив автоапгрейд на Professional
    Умова: 10 активних реферралів + мінімум 3 платних
    """
    from apps.referrals.models import Referral
    from apps.subscriptions.models import Subscription, Plan

    try:
        # Отримуємо всі активні реферали користувача
        active_referrals = Referral.objects.filter(
            referrer=user,
            status='active'
        ).select_related('referred__organization')

        if active_referrals.count() < 10:
            return False

        # Рахуємо платних реферралів
        paid_count = 0
        for referral in active_referrals:
            try:
                subscription = referral.referred.organization.subscription
                # Вважаємо платним якщо план не Free і статус active
                if subscription.plan.slug != 'free' and subscription.status == 'active':
                    paid_count += 1
            except:
                continue

        if paid_count < 3:
            logger.info(f"User {user.email} has {active_referrals.count()} active referrals but only {paid_count} paid")
            return False

        # Умови виконані! Апгрейдимо на Professional
        logger.info(f"User {user.email} qualified for referral upgrade: {active_referrals.count()} active, {paid_count} paid")

        with transaction.atomic():
            professional_plan = Plan.objects.get(slug='professional')
            subscription = user.organization.subscription

            old_plan = subscription.plan

            # Апгрейдимо план
            subscription.plan = professional_plan
            subscription.status = 'active'
            subscription.billing_cycle = 'lifetime'  # Безкоштовно назавжди
            subscription.current_period_end = timezone.now() + timedelta(days=365 * 10)  # 10 років
            subscription.save()

            # Створюємо запис про нагороду
            from apps.referrals.models import ReferralReward
            ReferralReward.objects.create(
                user=user,
                reward_type='plan_upgrade',
                referral_count=active_referrals.count(),
                old_plan=old_plan,
                new_plan=professional_plan,
                metadata={
                    'paid_referrals': paid_count,
                    'total_referrals': active_referrals.count(),
                    'upgraded_at': timezone.now().isoformat()
                }
            )

            logger.info(f"Successfully upgraded {user.email} to Professional plan")
            return True

    except Exception as e:
        logger.error(f"Error in check_and_apply_referral_upgrade for {user.email}: {str(e)}")
        return False


def apply_referral_trial(referred_user, referrer_user):
    """
    Дає 10-денний trial Professional плану користувачу який використав реферальний код
    """
    from apps.referrals.models import ReferralTrial
    from apps.subscriptions.models import Plan

    try:
        # Перевіряємо чи вже не має trial
        if hasattr(referred_user, 'referral_trial') and referred_user.referral_trial.is_active:
            logger.info(f"User {referred_user.email} already has active referral trial")
            return False

        with transaction.atomic():
            subscription = referred_user.organization.subscription
            original_plan = subscription.plan
            professional_plan = Plan.objects.get(slug='professional')

            # Створюємо запис про trial
            trial = ReferralTrial.objects.create(
                user=referred_user,
                referrer=referrer_user,
                original_plan=original_plan,
                trial_plan=professional_plan
            )

            # Апгрейдимо підписку на Professional
            subscription.plan = professional_plan
            subscription.status = 'trialing'
            subscription.save()

            logger.info(f"Applied 10-day Professional trial for {referred_user.email} (referrer: {referrer_user.email})")
            return True

    except Exception as e:
        logger.error(f"Error in apply_referral_trial for {referred_user.email}: {str(e)}")
        return False


def revert_referral_trial(trial_id):
    """
    Повертає користувача на оригінальний план після закінчення trial періоду
    """
    from apps.referrals.models import ReferralTrial

    try:
        trial = ReferralTrial.objects.select_related(
            'user__organization__subscription',
            'original_plan'
        ).get(id=trial_id)

        if not trial.is_active:
            logger.info(f"Trial {trial_id} is already inactive")
            return False

        # Перевіряємо чи закінчився trial
        if timezone.now() < trial.trial_end:
            logger.info(f"Trial {trial_id} has not ended yet")
            return False

        with transaction.atomic():
            subscription = trial.user.organization.subscription

            # Повертаємо на оригінальний план
            subscription.plan = trial.original_plan
            subscription.status = 'active'
            subscription.save()

            # Позначаємо trial як неактивний
            trial.is_active = False
            trial.reverted_at = timezone.now()
            trial.save()

            logger.info(f"Reverted trial {trial_id} for user {trial.user.email}")
            return True

    except ReferralTrial.DoesNotExist:
        logger.error(f"Trial {trial_id} does not exist")
        return False
    except Exception as e:
        logger.error(f"Error in revert_referral_trial for trial {trial_id}: {str(e)}")
        return False


def update_referral_stats(referrer_user):
    """
    Оновлює статистику реферралів для користувача
    """
    from apps.referrals.models import Referral, ReferralCode

    try:
        referral_code = ReferralCode.objects.get(user=referrer_user)

        # Рахуємо active referrals
        active_count = Referral.objects.filter(
            referrer=referrer_user,
            status='active'
        ).count()

        # Оновлюємо статистику
        referral_code.active_referrals = active_count
        referral_code.save(update_fields=['active_referrals', 'updated_at'])

        # Перевіряємо чи заслуговує на апгрейд
        check_and_apply_referral_upgrade(referrer_user)

        return True

    except ReferralCode.DoesNotExist:
        logger.warning(f"ReferralCode does not exist for user {referrer_user.email}")
        return False
    except Exception as e:
        logger.error(f"Error in update_referral_stats for {referrer_user.email}: {str(e)}")
        return False
