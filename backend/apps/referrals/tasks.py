from celery import shared_task
from django.utils import timezone
from .models import Referral, ReferralReward, ReferralCode, ReferralTrial
from apps.subscriptions.models import Plan, Subscription
import logging

logger = logging.getLogger(__name__)


@shared_task
def check_referral_rewards():
    """
    Check if users have reached referral milestones (50 active users)
    and grant plan upgrades
    """
    # Milestones for rewards
    MILESTONES = [50, 100, 150, 200]

    # Get all users with active referrals
    users_with_referrals = ReferralCode.objects.filter(active_referrals__gte=50)

    for referral_code in users_with_referrals:
        user = referral_code.user

        # Check each milestone
        for milestone in MILESTONES:
            if referral_code.active_referrals >= milestone:
                # Check if reward was already granted
                if not ReferralReward.objects.filter(
                    user=user,
                    referral_count=milestone
                ).exists():
                    # Grant reward - upgrade to next plan
                    try:
                        current_subscription = user.organization.subscription
                        current_plan = current_subscription.plan

                        # Get next plan (by price)
                        next_plan = Plan.objects.filter(
                            price_monthly__gt=current_plan.price_monthly,
                            is_active=True
                        ).order_by('price_monthly').first()

                        if next_plan:
                            # Upgrade subscription
                            old_plan = current_subscription.plan
                            current_subscription.plan = next_plan
                            current_subscription.save()

                            # Create reward record
                            ReferralReward.objects.create(
                                user=user,
                                reward_type='plan_upgrade',
                                referral_count=milestone,
                                old_plan=old_plan,
                                new_plan=next_plan
                            )

                            print(f"Upgraded {user.email} from {old_plan.name} to {next_plan.name} for {milestone} referrals")

                    except Exception as e:
                        print(f"Error granting reward to {user.email}: {e}")

    return "Checked referral rewards"


@shared_task
def update_referral_stats():
    """
    Update referral statistics (count active referrals)
    """
    referral_codes = ReferralCode.objects.all()

    for referral_code in referral_codes:
        # Count active referrals (users with active subscriptions)
        active_count = Referral.objects.filter(
            referrer=referral_code.user,
            status='active'
        ).count()

        total_count = Referral.objects.filter(
            referrer=referral_code.user
        ).count()

        referral_code.active_referrals = active_count
        referral_code.total_signups = total_count
        referral_code.save(update_fields=['active_referrals', 'total_signups', 'updated_at'])

    return f"Updated {referral_codes.count()} referral codes"


@shared_task
def check_and_apply_auto_upgrades():
    """
    Перевіряє всіх користувачів з реферралами на умови автоапгрейду:
    10 активних реферралів + мінімум 3 платних = Professional назавжди
    """
    from .utils import check_and_apply_referral_upgrade

    # Отримуємо користувачів з >= 10 активними реферралами
    users_to_check = ReferralCode.objects.filter(active_referrals__gte=10)

    upgraded_count = 0
    for referral_code in users_to_check:
        try:
            # Перевіряємо чи вже має Professional
            subscription = referral_code.user.organization.subscription
            if subscription.plan.slug == 'professional':
                continue

            # Перевіряємо умови та апгрейдимо
            if check_and_apply_referral_upgrade(referral_code.user):
                upgraded_count += 1
                logger.info(f"Auto-upgraded {referral_code.user.email} to Professional")

        except Exception as e:
            logger.error(f"Error checking auto-upgrade for {referral_code.user.email}: {str(e)}")

    return f"Checked {users_to_check.count()} users, upgraded {upgraded_count}"


@shared_task
def revert_expired_referral_trials():
    """
    Повертає користувачів на оригінальний план після закінчення 10-денного trial
    Запускається щогодини
    """
    from .utils import revert_referral_trial

    now = timezone.now()

    # Знаходимо активні trial які закінчились
    expired_trials = ReferralTrial.objects.filter(
        is_active=True,
        trial_end__lt=now
    )

    reverted_count = 0
    for trial in expired_trials:
        try:
            if revert_referral_trial(trial.id):
                reverted_count += 1
                logger.info(f"Reverted trial for {trial.user.email} back to {trial.original_plan.name}")
        except Exception as e:
            logger.error(f"Error reverting trial {trial.id}: {str(e)}")

    return f"Checked {expired_trials.count()} expired trials, reverted {reverted_count}"


@shared_task
def send_trial_expiry_reminders():
    """
    Відправляє нагадування користувачам за 1 день до закінчення trial
    """
    from datetime import timedelta

    tomorrow = timezone.now() + timedelta(days=1)
    tomorrow_start = tomorrow.replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow_end = tomorrow.replace(hour=23, minute=59, second=59, microsecond=999999)

    # Знаходимо trial які закінчуються завтра
    expiring_trials = ReferralTrial.objects.filter(
        is_active=True,
        trial_end__gte=tomorrow_start,
        trial_end__lte=tomorrow_end
    ).select_related('user', 'original_plan', 'trial_plan')

    sent_count = 0
    for trial in expiring_trials:
        try:
            # TODO: Відправити email нагадування
            logger.info(f"Trial expires tomorrow for {trial.user.email}")
            sent_count += 1
        except Exception as e:
            logger.error(f"Error sending reminder for trial {trial.id}: {str(e)}")

    return f"Sent {sent_count} trial expiry reminders"
