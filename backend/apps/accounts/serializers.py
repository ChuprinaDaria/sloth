from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import Organization, Profile, ApiKey

User = get_user_model()


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = [
            'id', 'name', 'domain', 'schema_name',
            'max_storage_mb', 'used_storage_mb',
            'is_active', 'created_at'
        ]
        read_only_fields = ['schema_name', 'used_storage_mb', 'created_at']


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    organization_name = serializers.CharField(write_only=True)
    referral_code_used = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = [
            'email', 'username', 'password', 'password_confirm',
            'first_name', 'last_name', 'phone', 'language',
            'organization_name', 'referral_code_used'
        ]

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Passwords don't match"})

        # Check if referral code exists
        if attrs.get('referral_code_used'):
            try:
                User.objects.get(referral_code=attrs['referral_code_used'])
            except User.DoesNotExist:
                raise serializers.ValidationError({"referral_code": "Invalid referral code"})

        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        organization_name = validated_data.pop('organization_name')
        referral_code_used = validated_data.pop('referral_code_used', None)
        password = validated_data.pop('password')

        # Create organization first
        organization = Organization.objects.create(
            name=organization_name,
            domain=f"{organization_name.lower().replace(' ', '-')}.sloth.local"
        )

        # Set referrer if code was used
        if referral_code_used:
            try:
                referrer = User.objects.get(referral_code=referral_code_used)
                validated_data['referred_by'] = referrer
            except User.DoesNotExist:
                pass

        # Create user
        user = User.objects.create_user(
            organization=organization,
            password=password,
            **validated_data
        )

        # Set user as organization owner
        organization.owner = user
        organization.save()

        return user


class UserSerializer(serializers.ModelSerializer):
    organization = OrganizationSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name',
            'phone', 'avatar', 'language', 'referral_code',
            'organization', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'email', 'referral_code', 'created_at']


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone', 'avatar', 'language']


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = [
            'id', 'user_id', 'business_name', 'business_type',
            'business_address', 'timezone', 'notification_email',
            'notification_telegram', 'notification_whatsapp',
            'preferences', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user_id', 'created_at', 'updated_at']


class ApiKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = ApiKey
        fields = [
            'id', 'name', 'key', 'is_active',
            'last_used_at', 'requests_count',
            'created_at', 'expires_at'
        ]
        read_only_fields = ['key', 'last_used_at', 'requests_count', 'created_at']
