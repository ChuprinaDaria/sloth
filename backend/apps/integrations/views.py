from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from .models import Integration, WebhookEvent
from .services import TelegramService, WhatsAppService, GoogleCalendarService
from rest_framework import serializers


class IntegrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Integration
        fields = [
            'id', 'integration_type', 'status', 'settings',
            'messages_received', 'messages_sent', 'last_activity',
            'error_message', 'created_at', 'updated_at'
        ]
        read_only_fields = ['messages_received', 'messages_sent', 'last_activity']


class IntegrationListView(generics.ListAPIView):
    """List user's integrations"""
    serializer_class = IntegrationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Integration.objects.filter(user_id=self.request.user.id)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def connect_telegram(request):
    """Connect Telegram bot"""
    bot_token = request.data.get('bot_token')

    if not bot_token:
        return Response({'error': 'Bot token is required'}, status=status.HTTP_400_BAD_REQUEST)

    # Create or update integration
    integration, created = Integration.objects.update_or_create(
        user_id=request.user.id,
        integration_type='telegram',
        defaults={
            'status': 'active',
        }
    )

    integration.set_credentials({'bot_token': bot_token})
    integration.save()

    # Setup webhook
    telegram_service = TelegramService(integration)
    webhook_url = f"{request.scheme}://{request.get_host()}/api/integrations/webhooks/telegram/"

    if telegram_service.setup_webhook(webhook_url):
        return Response({
            'message': 'Telegram bot connected successfully',
            'integration': IntegrationSerializer(integration).data
        })
    else:
        return Response(
            {'error': 'Failed to setup webhook'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def connect_whatsapp(request):
    """Connect WhatsApp Business"""
    account_sid = request.data.get('account_sid')
    auth_token = request.data.get('auth_token')
    whatsapp_number = request.data.get('whatsapp_number')

    if not all([account_sid, auth_token, whatsapp_number]):
        return Response(
            {'error': 'All Twilio credentials are required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Create or update integration
    integration, created = Integration.objects.update_or_create(
        user_id=request.user.id,
        integration_type='whatsapp',
        defaults={
            'status': 'active',
        }
    )

    integration.set_credentials({
        'account_sid': account_sid,
        'auth_token': auth_token,
        'whatsapp_number': whatsapp_number
    })
    integration.save()

    return Response({
        'message': 'WhatsApp connected successfully',
        'integration': IntegrationSerializer(integration).data,
        'webhook_url': f"{request.scheme}://{request.get_host()}/api/integrations/webhooks/whatsapp/"
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def connect_calendar(request):
    """Connect Google Calendar"""
    access_token = request.data.get('access_token')
    refresh_token = request.data.get('refresh_token')

    if not access_token:
        return Response({'error': 'Access token is required'}, status=status.HTTP_400_BAD_REQUEST)

    # Create or update integration
    integration, created = Integration.objects.update_or_create(
        user_id=request.user.id,
        integration_type='google_calendar',
        defaults={
            'status': 'active',
        }
    )

    integration.set_credentials({
        'access_token': access_token,
        'refresh_token': refresh_token
    })
    integration.save()

    return Response({
        'message': 'Google Calendar connected successfully',
        'integration': IntegrationSerializer(integration).data
    })


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def disconnect_integration(request, pk):
    """Disconnect integration"""
    try:
        integration = Integration.objects.get(id=pk, user_id=request.user.id)
        integration.delete()
        return Response({'message': 'Integration disconnected'})
    except Integration.DoesNotExist:
        return Response({'error': 'Integration not found'}, status=status.HTTP_404_NOT_FOUND)


# Webhook endpoints (CSRF exempt)

@method_decorator(csrf_exempt, name='dispatch')
class TelegramWebhookView(APIView):
    """Telegram webhook endpoint"""
    permission_classes = []

    def post(self, request):
        # TODO: Verify webhook signature
        payload = request.data

        # Store webhook event
        # Process in background task
        return JsonResponse({'ok': True})


@method_decorator(csrf_exempt, name='dispatch')
class WhatsAppWebhookView(APIView):
    """WhatsApp webhook endpoint"""
    permission_classes = []

    def post(self, request):
        # Twilio webhook payload
        from_number = request.POST.get('From', '').replace('whatsapp:', '')
        message_body = request.POST.get('Body', '')

        if not from_number or not message_body:
            return JsonResponse({'error': 'Invalid webhook'}, status=400)

        # Find integration by phone number mapping
        # For now, this is simplified - in production, you'd need proper mapping

        return JsonResponse({'ok': True})
