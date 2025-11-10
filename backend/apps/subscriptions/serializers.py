from rest_framework import serializers
from .models import Plan, Subscription, ActivationCode, Invoice


class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = [
            'id', 'name', 'slug', 'description', 'plan_type',
            'price_monthly', 'price_yearly',
            'max_users', 'max_documents', 'max_photos_per_month',
            'max_messages_per_month', 'max_conversations_per_month',
            'max_integrations', 'max_storage_mb',
            'features', 'has_watermark', 'is_active'
        ]


class SubscriptionSerializer(serializers.ModelSerializer):
    plan = PlanSerializer(read_only=True)
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    is_free_plan = serializers.SerializerMethodField()
    has_watermark = serializers.SerializerMethodField()
    can_add_integration = serializers.SerializerMethodField()

    # Usage percentages
    messages_usage_percent = serializers.SerializerMethodField()
    photos_usage_percent = serializers.SerializerMethodField()
    documents_usage_percent = serializers.SerializerMethodField()
    conversations_usage_percent = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = [
            'id', 'organization_name', 'plan', 'status', 'billing_cycle',
            'is_free_plan', 'has_watermark', 'can_add_integration',
            'trial_start', 'trial_end', 'current_period_start', 'current_period_end',
            'cancel_at_period_end', 'canceled_at',
            'used_messages', 'used_photos', 'used_documents', 'used_conversations',
            'messages_usage_percent', 'photos_usage_percent', 'documents_usage_percent',
            'conversations_usage_percent',
            'created_at', 'updated_at'
        ]

    def get_is_free_plan(self, obj):
        return obj.is_free_plan()

    def get_has_watermark(self, obj):
        return obj.has_watermark()

    def get_can_add_integration(self, obj):
        return obj.can_add_integration()

    def get_messages_usage_percent(self, obj):
        if obj.plan.max_messages_per_month == 0:
            return 0
        return round((obj.used_messages / obj.plan.max_messages_per_month) * 100, 2)

    def get_photos_usage_percent(self, obj):
        if obj.plan.max_photos_per_month == 0:
            return 0
        return round((obj.used_photos / obj.plan.max_photos_per_month) * 100, 2)

    def get_documents_usage_percent(self, obj):
        if obj.plan.max_documents == 0:
            return 0
        return round((obj.used_documents / obj.plan.max_documents) * 100, 2)

    def get_conversations_usage_percent(self, obj):
        if obj.plan.max_conversations_per_month == 0:
            return 0
        return round((obj.used_conversations / obj.plan.max_conversations_per_month) * 100, 2)


class ActivationCodeSerializer(serializers.ModelSerializer):
    plan_name = serializers.CharField(source='plan.name', read_only=True)

    class Meta:
        model = ActivationCode
        fields = [
            'id', 'code', 'plan', 'plan_name', 'duration_days',
            'is_used', 'used_by', 'used_at', 'expires_at', 'created_at'
        ]
        read_only_fields = ['code', 'is_used', 'used_by', 'used_at']


class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = [
            'id', 'amount', 'currency', 'status',
            'period_start', 'period_end', 'due_date', 'paid_at',
            'invoice_pdf', 'created_at'
        ]
