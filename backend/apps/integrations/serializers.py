from rest_framework import serializers
from .models import PhotoRecognitionProvider, UserPhotoRecognitionConfig
from apps.core.utils.encryption import encrypt_api_key, decrypt_api_key


class PhotoRecognitionProviderSerializer(serializers.ModelSerializer):
    """Serializer for PhotoRecognitionProvider"""

    class Meta:
        model = PhotoRecognitionProvider
        fields = [
            'id',
            'slug',
            'name',
            'description',
            'requires_api_key',
            'api_documentation_url',
            'cost_per_image',
            'available_in_professional_only',
            'is_active',
            'order'
        ]
        read_only_fields = ['id']


class UserPhotoRecognitionConfigSerializer(serializers.ModelSerializer):
    """Serializer for UserPhotoRecognitionConfig"""
    provider_name = serializers.CharField(source='provider.name', read_only=True)
    provider_slug = serializers.CharField(source='provider.slug', read_only=True)
    masked_api_key = serializers.SerializerMethodField()
    api_key = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = UserPhotoRecognitionConfig
        fields = [
            'id',
            'provider',
            'provider_name',
            'provider_slug',
            'api_key',
            'masked_api_key',
            'is_active',
            'is_default',
            'images_processed',
            'total_cost',
            'last_used_at',
            'created_at'
        ]
        read_only_fields = [
            'id',
            'images_processed',
            'total_cost',
            'last_used_at',
            'created_at',
            'masked_api_key'
        ]

    def get_masked_api_key(self, obj):
        """Return masked API key"""
        return obj.get_masked_key()

    def create(self, validated_data):
        """Create new config with encrypted API key"""
        api_key = validated_data.pop('api_key', None)

        if api_key:
            validated_data['api_key_encrypted'] = encrypt_api_key(api_key)

        return super().create(validated_data)

    def update(self, instance, validated_data):
        """Update config, encrypting API key if provided"""
        api_key = validated_data.pop('api_key', None)

        if api_key:
            instance.api_key_encrypted = encrypt_api_key(api_key)

        return super().update(instance, validated_data)


class PhotoRecognitionConfigCreateSerializer(serializers.Serializer):
    """Serializer for creating/updating photo recognition config"""
    provider_slug = serializers.SlugField()
    api_key = serializers.CharField(
        max_length=500,
        help_text="Your API key for this provider"
    )
    is_default = serializers.BooleanField(default=False)
    test_key = serializers.BooleanField(
        default=True,
        help_text="Test API key before saving"
    )

    def validate_provider_slug(self, value):
        """Validate provider exists and is active"""
        try:
            provider = PhotoRecognitionProvider.objects.get(
                slug=value,
                is_active=True
            )
            self.context['provider'] = provider
            return value
        except PhotoRecognitionProvider.DoesNotExist:
            raise serializers.ValidationError(
                f"Provider '{value}' not found or inactive"
            )

    def validate(self, data):
        """Additional validation"""
        # Check if user has permission for this provider
        user = self.context['request'].user
        provider = self.context.get('provider')

        if provider and provider.available_in_professional_only:
            # Check subscription
            try:
                subscription = user.subscription
                if subscription.plan.slug != 'professional':
                    raise serializers.ValidationError(
                        "This provider is only available for Professional plan users"
                    )
            except Exception:
                raise serializers.ValidationError(
                    "Subscription information not available"
                )

        return data
