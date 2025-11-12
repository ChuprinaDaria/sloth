from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.utils import timezone
from .models import Plan, Subscription, ActivationCode, Invoice
from .serializers import (
    PlanSerializer, SubscriptionSerializer,
    ActivationCodeSerializer, InvoiceSerializer
)
from .services import StripeService


class PlanListView(generics.ListAPIView):
    """List all public plans"""
    serializer_class = PlanSerializer
    permission_classes = [permissions.AllowAny]
    queryset = Plan.objects.filter(is_public=True, is_active=True)


class SubscriptionView(generics.RetrieveAPIView):
    """Get current subscription"""
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user.organization.subscription


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def activate_code(request):
    """Activate subscription with code"""
    code = request.data.get('code')

    if not code:
        return Response(
            {'error': 'Code is required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        activation_code = ActivationCode.objects.get(code=code)
    except ActivationCode.DoesNotExist:
        return Response(
            {'error': 'Invalid activation code'},
            status=status.HTTP_404_NOT_FOUND
        )

    if not activation_code.is_valid():
        return Response(
            {'error': 'Code is expired or already used'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Activate subscription
    organization = request.user.organization
    subscription = organization.subscription

    # Update subscription
    subscription.plan = activation_code.plan
    subscription.status = 'active'

    if activation_code.duration_days == 0:
        # Lifetime
        subscription.billing_cycle = 'lifetime'
        subscription.current_period_end = timezone.now() + timezone.timedelta(days=36500)
    else:
        subscription.current_period_end = timezone.now() + timezone.timedelta(
            days=activation_code.duration_days
        )

    subscription.save()

    # Mark code as used
    activation_code.is_used = True
    activation_code.used_by = organization
    activation_code.used_at = timezone.now()
    activation_code.save()

    return Response({
        'message': 'Subscription activated successfully',
        'subscription': SubscriptionSerializer(subscription).data
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_checkout_session(request):
    """Create Stripe checkout session"""
    import logging
    logger = logging.getLogger(__name__)
    
    plan_id = request.data.get('plan_id')
    billing_cycle = request.data.get('billing_cycle', 'monthly')

    # Check organization exists
    if not hasattr(request.user, 'organization') or not request.user.organization:
        return Response(
            {'error': 'User organization not found'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        plan = Plan.objects.get(id=plan_id)
    except Plan.DoesNotExist:
        return Response(
            {'error': 'Invalid plan'},
            status=status.HTTP_404_NOT_FOUND
        )

    # Check Stripe is configured
    from django.conf import settings
    if not settings.STRIPE_SECRET_KEY:
        logger.error("STRIPE_SECRET_KEY is not configured")
        return Response(
            {'error': 'Payment processing is not configured'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    # Check price ID exists
    price_id = (
        plan.stripe_price_id_monthly
        if billing_cycle == 'monthly'
        else plan.stripe_price_id_yearly
    )
    
    if not price_id:
        return Response(
            {'error': f'Stripe price ID not configured for {billing_cycle} billing cycle'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # Create Stripe checkout session
        stripe_service = StripeService()
        session = stripe_service.create_checkout_session(
            user=request.user,
            plan=plan,
            billing_cycle=billing_cycle
        )

        return Response({'checkout_url': session.url})
    except Exception as e:
        logger.error(f"Error creating Stripe checkout session: {e}", exc_info=True)
        return Response(
            {'error': f'Failed to create checkout session: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def cancel_subscription(request):
    """Cancel subscription at period end"""
    subscription = request.user.organization.subscription

    if subscription.billing_cycle == 'lifetime':
        return Response(
            {'error': 'Cannot cancel lifetime subscription'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Cancel via Stripe if exists
    if subscription.stripe_subscription_id:
        stripe_service = StripeService()
        stripe_service.cancel_subscription(subscription.stripe_subscription_id)

    subscription.cancel_at_period_end = True
    subscription.canceled_at = timezone.now()
    subscription.save()

    return Response({
        'message': 'Subscription will be canceled at period end',
        'subscription': SubscriptionSerializer(subscription).data
    })


class UsageView(generics.RetrieveAPIView):
    """Get subscription usage stats"""
    permission_classes = [permissions.IsAuthenticated]

    def retrieve(self, request):
        subscription = request.user.organization.subscription

        usage = {
            'messages': {
                'used': subscription.used_messages,
                'limit': subscription.plan.max_messages_per_month,
                'percentage': round((subscription.used_messages / subscription.plan.max_messages_per_month) * 100, 2)
                if subscription.plan.max_messages_per_month > 0 else 0
            },
            'photos': {
                'used': subscription.used_photos,
                'limit': subscription.plan.max_photos_per_month,
                'percentage': round((subscription.used_photos / subscription.plan.max_photos_per_month) * 100, 2)
                if subscription.plan.max_photos_per_month > 0 else 0
            },
            'documents': {
                'used': subscription.used_documents,
                'limit': subscription.plan.max_documents,
                'percentage': round((subscription.used_documents / subscription.plan.max_documents) * 100, 2)
                if subscription.plan.max_documents > 0 else 0
            },
            'storage': {
                'used': request.user.organization.used_storage_mb,
                'limit': subscription.plan.max_storage_mb,
                'percentage': round((request.user.organization.used_storage_mb / subscription.plan.max_storage_mb) * 100, 2)
                if subscription.plan.max_storage_mb > 0 else 0
            },
            'reset_at': subscription.usage_reset_at
        }

        return Response(usage)
