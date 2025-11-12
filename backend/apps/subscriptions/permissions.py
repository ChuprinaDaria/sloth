"""
Permission utilities for checking plan features
"""
from functools import wraps
from rest_framework.response import Response
from rest_framework import status


def get_user_plan(user):
    """Get user's current subscription plan"""
    if not hasattr(user, 'organization') or not user.organization:
        return None

    try:
        subscription = user.organization.subscription
        return subscription.plan
    except:
        return None


def has_feature(user, feature_slug):
    """Check if user's plan has a specific feature"""
    plan = get_user_plan(user)
    if not plan:
        return False

    return feature_slug in plan.features


def require_feature(feature_slug, error_message=None):
    """
    Decorator to require a specific plan feature

    Usage:
        @require_feature('telegram')
        def my_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            if not has_feature(request.user, feature_slug):
                plan = get_user_plan(request.user)
                plan_name = plan.name if plan else "Free"

                message = error_message or f"This feature is not available in your {plan_name} plan. Please upgrade to access {feature_slug}."

                return Response(
                    {'error': message, 'feature_required': feature_slug, 'current_plan': plan_name},
                    status=status.HTTP_403_FORBIDDEN
                )

            return view_func(request, *args, **kwargs)
        return wrapped_view
    return decorator


def get_plan_features(plan_slug):
    """Get list of features for a specific plan"""
    from .models import Plan

    try:
        plan = Plan.objects.get(slug=plan_slug)
        return plan.features
    except Plan.DoesNotExist:
        return []


# Feature constants for easy reference
class Features:
    # Integrations
    TELEGRAM = 'telegram'
    WHATSAPP = 'whatsapp'
    INSTAGRAM = 'instagram'
    INSTAGRAM_EMBEDDINGS = 'instagram_embeddings'
    GOOGLE_CALENDAR = 'google_calendar'
    GOOGLE_SHEETS = 'google_sheets'
    GMAIL = 'gmail'
    WEBSITE_WIDGET = 'website_widget'
    API_ACCESS = 'api_access'

    # Training
    BASIC_TRAINING = 'basic_training'
    ADVANCED_TRAINING = 'advanced_training'

    # Support
    EMAIL_SUPPORT = 'email_support'
    PRIORITY_SUPPORT = 'priority_support'
    PHONE_SUPPORT_24_7 = 'phone_support_24_7'
    ACCOUNT_MANAGER = 'account_manager'

    # History
    CHAT_HISTORY_30_DAYS = 'chat_history_30_days'
    UNLIMITED_HISTORY = 'unlimited_history'

    # Analytics
    SMART_ANALYTICS = 'smart_analytics'
    FULL_AI_ANALYTICS = 'full_ai_analytics'

    # Other
    CUSTOM_BRANDING = 'custom_branding'
    MULTIPLE_LOCATIONS = 'multiple_locations'
    CUSTOM_INTEGRATIONS = 'custom_integrations'
    WATERMARKED_MESSAGES = 'watermarked_messages'


def check_message_limit(user):
    """Check if user has reached message limit"""
    try:
        subscription = user.organization.subscription
        plan = subscription.plan

        # Unlimited messages (Professional/Enterprise)
        if plan.max_messages_per_month >= 999999:
            return True, None

        # Check if within limit
        if subscription.used_messages < plan.max_messages_per_month:
            return True, None

        return False, f"You've reached your monthly limit of {plan.max_messages_per_month} messages. Please upgrade your plan."
    except:
        return False, "Could not verify message limit"


def check_photo_limit(user):
    """Check if user has reached photo upload limit"""
    try:
        subscription = user.organization.subscription
        plan = subscription.plan

        if subscription.used_photos < plan.max_photos_per_month:
            return True, None

        return False, f"You've reached your monthly limit of {plan.max_photos_per_month} photos. Please upgrade your plan."
    except:
        return False, "Could not verify photo limit"


def check_document_limit(user):
    """Check if user has reached document limit"""
    try:
        subscription = user.organization.subscription
        plan = subscription.plan

        if subscription.used_documents < plan.max_documents:
            return True, None

        return False, f"You've reached your limit of {plan.max_documents} documents. Please upgrade your plan."
    except:
        return False, "Could not verify document limit"
