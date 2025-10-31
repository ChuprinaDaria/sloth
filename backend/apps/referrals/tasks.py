from celery import shared_task
from django.utils import timezone
from .models import Referral, ReferralReward, ReferralCode
from apps.subscriptions.models import Plan, Subscription


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
