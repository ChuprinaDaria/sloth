from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from .models import Integration, WebhookEvent
from .telegram_manager import start_telegram_bot, stop_telegram_bot, process_telegram_webhook
from .whatsapp_manager import whatsapp_manager
from .services import GoogleCalendarService
from rest_framework import serializers
import asyncio
import logging

logger = logging.getLogger(__name__)


class IntegrationSerializer(serializers.ModelSerializer):
    webhook_url = serializers.SerializerMethodField()

    class Meta:
        model = Integration
        fields = [
            'id', 'integration_type', 'status', 'settings',
            'messages_received', 'messages_sent', 'last_activity',
            'error_message', 'webhook_url', 'created_at', 'updated_at'
        ]
        read_only_fields = ['messages_received', 'messages_sent', 'last_activity']

    def get_webhook_url(self, obj):
        """Return webhook URL for this integration"""
        if obj.integration_type == 'telegram':
            credentials = obj.get_credentials()
            bot_token = credentials.get('bot_token', '')
            if bot_token:
                from django.conf import settings
                base_url = settings.BACKEND_URL or 'http://localhost:8000'
                return f"{base_url}/api/integrations/webhooks/telegram/{bot_token}/"
        elif obj.integration_type == 'whatsapp':
            from django.conf import settings
            base_url = settings.BACKEND_URL or 'http://localhost:8000'
            return f"{base_url}/api/integrations/webhooks/whatsapp/"
        return None


class IntegrationListView(generics.ListAPIView):
    """List user's integrations"""
    serializer_class = IntegrationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Integration.objects.filter(user_id=self.request.user.id)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def connect_telegram(request):
    """
    Connect Telegram bot

    This will:
    1. Create Integration record
    2. Start the bot (register for webhooks)
    3. Set up webhook with Telegram
    """
    bot_token = request.data.get('bot_token')

    if not bot_token:
        return Response({'error': 'Bot token is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Create or update integration
        integration, created = Integration.objects.update_or_create(
            user_id=request.user.id,
            integration_type='telegram',
            defaults={
                'status': 'pending',
            }
        )

        # Store credentials
        integration.set_credentials({'bot_token': bot_token})
        integration.save()

        # Start the bot asynchronously
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        success = loop.run_until_complete(start_telegram_bot(integration))
        loop.close()

        if success:
            # Refresh from DB to get updated status
            integration.refresh_from_db()

            return Response({
                'message': 'Telegram bot connected successfully',
                'integration': IntegrationSerializer(integration).data
            })
        else:
            return Response(
                {'error': 'Failed to start Telegram bot. Check bot token.'},
                status=status.HTTP_400_BAD_REQUEST
            )

    except Exception as e:
        logger.error(f"Error connecting Telegram: {e}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def connect_whatsapp(request):
    """
    Connect WhatsApp Business

    User needs to:
    1. Create Twilio account
    2. Get WhatsApp-enabled number
    3. Provide credentials here
    4. Manually set webhook in Twilio console to our webhook URL
    """
    account_sid = request.data.get('account_sid')
    auth_token = request.data.get('auth_token')
    whatsapp_number = request.data.get('whatsapp_number')

    if not all([account_sid, auth_token, whatsapp_number]):
        return Response(
            {'error': 'All Twilio credentials are required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # Create or update integration
        integration, created = Integration.objects.update_or_create(
            user_id=request.user.id,
            integration_type='whatsapp',
            defaults={
                'status': 'active',
            }
        )

        # Store credentials
        integration.set_credentials({
            'account_sid': account_sid,
            'auth_token': auth_token,
            'whatsapp_number': whatsapp_number
        })

        # Setup webhook
        from django.conf import settings
        base_url = settings.BACKEND_URL or f"{request.scheme}://{request.get_host()}"
        webhook_url = f"{base_url}/api/integrations/webhooks/whatsapp/"

        whatsapp_manager.setup_webhook(integration, webhook_url)

        return Response({
            'message': 'WhatsApp connected successfully',
            'integration': IntegrationSerializer(integration).data,
            'instructions': f'Please configure this webhook URL in your Twilio console: {webhook_url}'
        })

    except Exception as e:
        logger.error(f"Error connecting WhatsApp: {e}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def calendar_auth_url(request):
    """
    Get Google OAuth2 authorization URL

    Returns URL to redirect user for Google Calendar authorization
    """
    from .google_calendar import GoogleCalendarService
    from django.conf import settings

    # Build redirect URI
    redirect_uri = f"{settings.BACKEND_URL}/api/integrations/calendar/callback/"

    # Get authorization URL
    auth_url, state = GoogleCalendarService.get_authorization_url(redirect_uri)

    # Store state in session for CSRF protection
    request.session['google_oauth_state'] = state
    request.session['oauth_user_id'] = request.user.id

    return Response({
        'authorization_url': auth_url,
        'state': state
    })


@api_view(['GET'])
@permission_classes([permissions.AllowAny])  # Will verify via session
def calendar_oauth_callback(request):
    """
    OAuth2 callback endpoint

    Google redirects here after user authorizes
    """
    from .google_calendar import GoogleCalendarService
    from django.conf import settings
    from django.shortcuts import redirect

    # Get authorization code
    code = request.GET.get('code')
    state = request.GET.get('state')
    error = request.GET.get('error')

    # Check for errors
    if error:
        return redirect(f"{settings.FRONTEND_URL}/integrations?error={error}")

    # Verify state (CSRF protection)
    session_state = request.session.get('google_oauth_state')
    if state != session_state:
        return redirect(f"{settings.FRONTEND_URL}/integrations?error=invalid_state")

    # Get user from session
    user_id = request.session.get('oauth_user_id')
    if not user_id:
        return redirect(f"{settings.FRONTEND_URL}/integrations?error=no_user")

    try:
        # Exchange code for tokens
        redirect_uri = f"{settings.BACKEND_URL}/api/integrations/calendar/callback/"
        tokens = GoogleCalendarService.exchange_code_for_tokens(code, redirect_uri)

        # Create or update integration
        from apps.accounts.models import User
        user = User.objects.get(id=user_id)

        integration, created = Integration.objects.update_or_create(
            user_id=user.id,
            integration_type='google_calendar',
            defaults={
                'status': 'active',
            }
        )

        integration.set_credentials(tokens)
        integration.save()

        # Clear session
        request.session.pop('google_oauth_state', None)
        request.session.pop('oauth_user_id', None)

        # Redirect to frontend success page
        return redirect(f"{settings.FRONTEND_URL}/integrations?success=calendar_connected")

    except Exception as e:
        logger.error(f"Error in OAuth callback: {e}")
        return redirect(f"{settings.FRONTEND_URL}/integrations?error=callback_failed")


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def calendar_available_slots(request):
    """
    Get available time slots for booking

    Query params:
        - date: YYYY-MM-DD or "tomorrow", "next monday"
        - duration: duration in minutes (default 60)
    """
    from .calendar_ai_tools import get_calendar_tools_for_user

    date_str = request.GET.get('date', 'today')
    duration = int(request.GET.get('duration', 60))

    calendar_tools = get_calendar_tools_for_user(
        request.user.id,
        request.user.organization.schema_name
    )

    result = calendar_tools.check_availability(date_str, duration)

    return Response({'slots': result})


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def disconnect_integration(request, pk):
    """Disconnect integration"""
    try:
        integration = Integration.objects.get(id=pk, user_id=request.user.id)

        # Stop bot if Telegram
        if integration.integration_type == 'telegram':
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(stop_telegram_bot(integration.id))
            loop.close()

        integration.delete()
        return Response({'message': 'Integration disconnected'})

    except Integration.DoesNotExist:
        return Response({'error': 'Integration not found'}, status=status.HTTP_404_NOT_FOUND)


# Webhook endpoints (CSRF exempt for external services)

@method_decorator(csrf_exempt, name='dispatch')
class TelegramWebhookView(APIView):
    """
    Telegram webhook endpoint

    URL pattern: /api/integrations/webhooks/telegram/<bot_token>/

    Each bot has unique webhook URL with its token in the path.
    This allows us to identify which Integration to use.
    """
    permission_classes = []

    def post(self, request, bot_token):
        try:
            # Get update data from Telegram
            update_data = request.data

            # Process webhook asynchronously
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            success = loop.run_until_complete(
                process_telegram_webhook(bot_token, update_data)
            )
            loop.close()

            if success:
                return JsonResponse({'ok': True})
            else:
                return JsonResponse({'ok': False, 'error': 'Processing failed'}, status=500)

        except Exception as e:
            logger.error(f"Telegram webhook error: {e}")
            return JsonResponse({'ok': False, 'error': str(e)}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class WhatsAppWebhookView(APIView):
    """
    WhatsApp webhook endpoint (Twilio)

    URL: /api/integrations/webhooks/whatsapp/

    All WhatsApp messages come here. We identify the user by the 'To' number.
    """
    permission_classes = []

    def post(self, request):
        try:
            # Twilio sends data as form-encoded
            from_number = request.POST.get('From', '')  # Customer's number
            to_number = request.POST.get('To', '')      # Your Twilio number
            message_body = request.POST.get('Body', '')

            if not all([from_number, to_number, message_body]):
                return JsonResponse({'error': 'Invalid webhook data'}, status=400)

            # Process message
            success = whatsapp_manager.process_incoming_message(
                from_number,
                to_number,
                message_body
            )

            if success:
                return JsonResponse({'ok': True})
            else:
                return JsonResponse({'ok': False}, status=500)

        except Exception as e:
            logger.error(f"WhatsApp webhook error: {e}")
            return JsonResponse({'error': str(e)}, status=500)
