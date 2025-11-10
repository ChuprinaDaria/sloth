# Generated migration for updating pricing plans

from django.db import migrations


def create_plans(apps, schema_editor):
    """Create new pricing plans"""
    Plan = apps.get_model('subscriptions', 'Plan')

    # Delete old plans if exist
    Plan.objects.all().delete()

    # Free plan
    Plan.objects.create(
        name="Free",
        slug="free",
        description="Start with AI assistant - perfect for trying out",
        price_monthly=0,
        price_yearly=0,
        max_users=1,
        max_documents=10,
        max_photos_per_month=50,
        max_messages_per_month=20,  # 20 dialogs
        max_storage_mb=100,
        features=[
            "telegram",
            "basic_training",
            "smart_analytics",
            "watermarked_messages"
        ],
        trial_days=0,  # No trial for free
        is_active=True,
        is_public=True,
        order=1
    )

    # Starter plan
    Plan.objects.create(
        name="Starter",
        slug="starter",
        description="Perfect for small salons",
        price_monthly=14.99,
        price_yearly=149.90,  # ~2 months free
        max_users=2,
        max_documents=50,
        max_photos_per_month=500,
        max_messages_per_month=100,
        max_storage_mb=500,
        features=[
            "telegram",
            "whatsapp",
            "google_calendar",
            "basic_training",
            "email_support",
            "chat_history_30_days",
            "smart_analytics"
        ],
        trial_days=14,
        is_active=True,
        is_public=True,
        order=2
    )

    # Professional plan - All features included
    Plan.objects.create(
        name="Professional",
        slug="professional",
        description="Everything you need - best for growing businesses",
        price_monthly=49,
        price_yearly=490,  # ~2 months free
        max_users=50,
        max_documents=9999,
        max_photos_per_month=99999,
        max_messages_per_month=999999,  # Unlimited
        max_storage_mb=50000,
        features=[
            "telegram",
            "whatsapp",
            "instagram",
            "instagram_embeddings",
            "google_calendar",
            "google_sheets",
            "gmail",
            "website_widget",
            "api_access",
            "advanced_training",
            "phone_support_24_7",
            "priority_support",
            "unlimited_history",
            "custom_branding",
            "full_ai_analytics",
            "multiple_locations",
            "account_manager",
            "custom_integrations"
        ],
        trial_days=14,
        is_active=True,
        is_public=True,
        order=3
    )


def reverse_plans(apps, schema_editor):
    """Remove plans"""
    Plan = apps.get_model('subscriptions', 'Plan')
    Plan.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_plans, reverse_plans),
    ]
