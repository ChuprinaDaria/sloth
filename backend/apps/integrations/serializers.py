from rest_framework import serializers
from .models import Integration, WebhookEvent, IntegrationWorkingHours
from apps.accounts.serializers import IntegrationTypeSerializer
from apps.accounts.models import IntegrationType


class IntegrationWorkingHoursSerializer(serializers.ModelSerializer):
    """Serializer for IntegrationWorkingHours model"""
    weekday_display = serializers.CharField(source='get_weekday_display', read_only=True)

    class Meta:
        model = IntegrationWorkingHours
        fields = [
            'id', 'integration', 'weekday', 'weekday_display',
            'start_time', 'end_time', 'is_enabled',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class IntegrationSerializer(serializers.ModelSerializer):
    """Serializer for Integration model"""
    integration_type_details = serializers.SerializerMethodField()
    working_hours = IntegrationWorkingHoursSerializer(many=True, read_only=True)

    class Meta:
        model = Integration
        fields = [
            'id', 'user_id', 'integration_type_id', 'integration_type_slug',
            'integration_type_details', 'status', 'settings',
            'messages_received', 'messages_sent', 'last_activity',
            'error_message', 'error_count', 'working_hours',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'messages_received', 'messages_sent', 'last_activity',
            'error_count', 'created_at', 'updated_at'
        ]

    def get_integration_type_details(self, obj):
        """Get integration type details from public schema"""
        try:
            integration_type = IntegrationType.objects.get(id=obj.integration_type_id)
            return IntegrationTypeSerializer(integration_type).data
        except IntegrationType.DoesNotExist:
            return None


class IntegrationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new integration"""

    class Meta:
        model = Integration
        fields = [
            'integration_type_id', 'settings'
        ]

    def validate_integration_type_id(self, value):
        """Validate that integration type exists"""
        try:
            integration_type = IntegrationType.objects.get(id=value)
            if not integration_type.is_active:
                raise serializers.ValidationError("This integration type is not available")
        except IntegrationType.DoesNotExist:
            raise serializers.ValidationError("Invalid integration type")

        return value

    def create(self, validated_data):
        """Create integration with user_id from request"""
        request = self.context.get('request')
        validated_data['user_id'] = request.user.id

        # Get integration type slug
        integration_type = IntegrationType.objects.get(id=validated_data['integration_type_id'])
        validated_data['integration_type_slug'] = integration_type.slug

        return super().create(validated_data)


class WebhookEventSerializer(serializers.ModelSerializer):
    """Serializer for WebhookEvent model"""
    class Meta:
        model = WebhookEvent
        fields = [
            'id', 'integration', 'event_type', 'payload',
            'is_processed', 'processed_at', 'error_message',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']
