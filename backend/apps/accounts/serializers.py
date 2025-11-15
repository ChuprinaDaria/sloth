from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import Organization, Profile, ApiKey, Sphere, IntegrationType

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
    sphere = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = [
            'id', 'user_id', 'sphere_id', 'sphere', 'business_name', 'business_type',
            'business_address', 'timezone', 'notification_email',
            'notification_telegram', 'notification_whatsapp',
            'preferences', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user_id', 'created_at', 'updated_at']

    def get_sphere(self, obj):
        """Get sphere details from public schema"""
        if obj.sphere_id:
            try:
                sphere = Sphere.objects.get(id=obj.sphere_id)
                return SphereSerializer(sphere).data
            except Sphere.DoesNotExist:
                return None
        return None


class ApiKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = ApiKey
        fields = [
            'id', 'name', 'key', 'is_active',
            'last_used_at', 'requests_count',
            'created_at', 'expires_at'
        ]
        read_only_fields = ['key', 'last_used_at', 'requests_count', 'created_at']


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom JWT serializer that allows login with either username or email
    """
    username = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    email = serializers.EmailField(required=False, allow_blank=True, allow_null=True)

    def to_internal_value(self, data):
        """
        Convert email to username before validation if username is not provided
        """
        # Ensure we have a dict
        if isinstance(data, dict):
            data_dict = dict(data)  # Create new dict to avoid mutation issues
        elif hasattr(data, '__dict__'):
            data_dict = dict(data.__dict__)
        else:
            # Try to convert
            try:
                data_dict = dict(data) if data else {}
            except (TypeError, ValueError):
                data_dict = {}
        
        # If email is provided but username is not, find user and set username
        email_value = data_dict.get('email')
        username_value = data_dict.get('username')
        
        # Clean values
        email = str(email_value).strip() if email_value else ''
        username = str(username_value).strip() if username_value else ''
        
        if email and not username:
            try:
                user = User.objects.get(email=email)
                data_dict['username'] = user.username
                # Remove email so parent serializer doesn't see it
                data_dict.pop('email', None)
            except (User.DoesNotExist, Exception):
                # If user not found or any error, let parent handle validation
                pass
        
        return super().to_internal_value(data_dict)

    def validate(self, attrs):
        # Get username (should be set by to_internal_value if email was provided)
        username = attrs.get('username', '').strip() if attrs.get('username') else ''
        password = attrs.get('password')

        if not username:
            raise serializers.ValidationError({
                "non_field_errors": ["Either username or email must be provided"]
            })
        
        if not password:
            raise serializers.ValidationError({
                "non_field_errors": ["Password must be provided"]
            })

        # Find user by username
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise serializers.ValidationError({
                "non_field_errors": ["Invalid credentials"]
            })

        # Check password
        if not user.check_password(password):
            raise serializers.ValidationError({
                "non_field_errors": ["Invalid credentials"]
            })

        if not user.is_active:
            raise serializers.ValidationError({
                "non_field_errors": ["User account is disabled"]
            })

        return super().validate(attrs)


class SphereSerializer(serializers.ModelSerializer):
    """Serializer for Sphere model"""
    class Meta:
        model = Sphere
        fields = [
            'id', 'name', 'slug', 'description',
            'icon', 'color', 'is_active', 'order'
        ]
        read_only_fields = ['id']


class IntegrationTypeSerializer(serializers.ModelSerializer):
    """Serializer for IntegrationType model"""
    spheres = SphereSerializer(many=True, read_only=True)

    class Meta:
        model = IntegrationType
        fields = [
            'id', 'slug', 'name', 'integration_type', 'description',
            'spheres', 'requires_oauth', 'oauth_provider',
            'api_documentation_url', 'supports_webhooks',
            'supports_working_hours', 'icon_url', 'logo_url',
            'color', 'available_countries', 'is_active', 'order'
        ]
        read_only_fields = ['id']
