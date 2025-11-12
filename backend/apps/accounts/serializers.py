from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import Organization, Profile, ApiKey

User = get_user_model()


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = [
            'id', 'name', 'domain', 'schema_name', 'country',
            'max_storage_mb', 'used_storage_mb',
            'is_active', 'created_at'
        ]
        read_only_fields = ['schema_name', 'used_storage_mb', 'created_at']


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    organization_name = serializers.CharField(write_only=True)
    country = serializers.CharField(write_only=True, required=False, allow_blank=True)
    referral_code_used = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = [
            'email', 'username', 'password', 'password_confirm',
            'first_name', 'last_name', 'phone', 'language',
            'organization_name', 'country', 'referral_code_used'
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
        from apps.subscriptions.models import Plan, Subscription
        from django.utils import timezone
        from django.db import transaction
        from datetime import timedelta
        import logging

        logger = logging.getLogger(__name__)

        validated_data.pop('password_confirm')
        organization_name = validated_data.pop('organization_name')
        country = validated_data.pop('country', '')
        referral_code_used = validated_data.pop('referral_code_used', None)
        password = validated_data.pop('password')

        # Store referrer if code was used (query once)
        referrer = None
        if referral_code_used:
            try:
                referrer = User.objects.get(referral_code=referral_code_used)
                validated_data['referred_by'] = referrer
            except User.DoesNotExist:
                pass

        # Wrap all DB operations in transaction
        with transaction.atomic():
            # Create organization first
            organization = Organization.objects.create(
                name=organization_name,
                domain=f"{organization_name.lower().replace(' ', '-')}.sloth.local"
            )

            # Create user
            user = User.objects.create_user(
                organization=organization,
                password=password,
                **validated_data
            )

            # Set user as organization owner
            organization.owner = user
            organization.save()

            # Create Free subscription automatically (use get_or_create to avoid duplicates)
            try:
                free_plan = Plan.objects.get(slug='free')
                subscription, created = Subscription.objects.get_or_create(
                    organization=organization,
                    defaults={
                        'plan': free_plan,
                        'status': 'free',  # Free plan status
                        'billing_cycle': 'lifetime',
                        'trial_start': timezone.now(),
                        'trial_end': timezone.now() + timedelta(days=365*10),  # Far future
                        'current_period_start': timezone.now(),
                        'current_period_end': timezone.now() + timedelta(days=365*10),
                    }
                )
                if not created:
                    logger.info(f"Subscription already exists for organization {organization.id}, skipping creation")
            except Plan.DoesNotExist:
                logger.warning(f"Free plan not found for organization {organization.id}")
                raise  # Fail registration if Free plan doesn't exist

            # Handle referral if code was used
            if referral_code_used and referrer:
                try:
                    from apps.referrals.models import Referral, ReferralCode
                    from apps.referrals.utils import apply_referral_trial, update_referral_stats

                    # Create Referral record
                    referral = Referral.objects.create(
                        referrer=referrer,
                        referred=user,
                        status='pending'  # Will become active when user pays or gets trial
                    )

                    # Create or update ReferralCode stats
                    referral_code_obj, created = ReferralCode.objects.get_or_create(
                        user=referrer,
                        defaults={'code': referral_code_used}
                    )
                    referral_code_obj.total_signups += 1
                    referral_code_obj.save()

                    # Apply 10-day Professional trial
                    apply_referral_trial(user, referrer)

                    # Update referrer's stats
                    update_referral_stats(referrer)

                    logger.info(f"Applied referral trial for {user.email} from {referrer.email}")

                except Exception as e:
                    logger.error(f"Error processing referral for {user.email}: {str(e)}")
                    # Don't fail entire registration, just log the error

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


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom JWT serializer that allows login with either username or email
    """
    username_field = 'email'  # Use email as primary field
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make username not required
        self.fields['username'] = serializers.CharField(required=False, write_only=True)
        # Add email field
        self.fields[self.username_field] = serializers.EmailField(required=True, write_only=True)

    def validate(self, attrs):
        # Get email and password
        email = attrs.get('email', '').strip().lower()
        password = attrs.get('password')

        if not email:
            raise serializers.ValidationError({
                "email": ["Email is required"]
            })
        
        if not password:
            raise serializers.ValidationError({
                "password": ["Password is required"]
            })

        # Find user by email (case-insensitive)
        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({
                "non_field_errors": ["Invalid email or password"]
            })

        # Check password
        if not user.check_password(password):
            raise serializers.ValidationError({
                "non_field_errors": ["Invalid email or password"]
            })

        if not user.is_active:
            raise serializers.ValidationError({
                "non_field_errors": ["User account is disabled"]
            })

        # Set username for parent class
        attrs['username'] = user.username
        
        refresh = self.get_token(user)
        
        attrs['refresh'] = str(refresh)
        attrs['access'] = str(refresh.access_token)

        return attrs
