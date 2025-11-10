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
from .tasks import run_async_in_thread, start_telegram_bot_task
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

        # Start the bot in a separate thread to avoid async context issues
        try:
            success = run_async_in_thread(start_telegram_bot(integration))

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
        except TimeoutError:
            return Response(
                {'error': 'Bot connection timed out. Please try again.'},
                status=status.HTTP_408_REQUEST_TIMEOUT
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

    Note: WhatsApp is NOT available for FREE plan (only Telegram allowed)
    """
    # Check if user has FREE plan - WhatsApp is not allowed
    from apps.subscriptions.models import Subscription
    try:
        subscription = request.user.organization.subscription
        if subscription.is_free_plan():
            return Response(
                {'error': 'WhatsApp integration is not available on FREE plan. Please upgrade to Starter plan or higher.'},
                status=status.HTTP_403_FORBIDDEN
            )
    except Exception as e:
        logger.error(f"Error checking subscription for WhatsApp: {e}")

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

    try:
        # Validate required env vars to avoid 500 with "Missing required parameter: client_id"
        if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
            return Response(
                {
                    'error': 'Google OAuth is not configured on the server',
                    'details': 'Missing GOOGLE_CLIENT_ID/GOOGLE_CLIENT_SECRET in environment',
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Build redirect URI - ensure it's properly formatted
        backend_url = settings.BACKEND_URL.rstrip('/')
        redirect_uri = f"{backend_url}/api/integrations/calendar/callback/"

        logger.info(f"Calendar OAuth redirect_uri: {redirect_uri}")

        # Get authorization URL
        auth_url, state = GoogleCalendarService.get_authorization_url(redirect_uri)

        # Store state in session for CSRF protection
        request.session['google_oauth_state'] = state
        request.session['oauth_user_id'] = request.user.id

        return Response({
            'authorization_url': auth_url,
            'state': state,
            'redirect_uri': redirect_uri  # Return for debugging
        })
    except Exception as e:
        logger.error(f"Error generating calendar auth URL: {e}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


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
    error_description = request.GET.get('error_description', '')

    # Check for errors
    if error:
        logger.error(f"OAuth error: {error} - {error_description}")
        return redirect(f"{settings.FRONTEND_URL}/integrations?error={error}")

    if not code:
        logger.error("No authorization code received")
        return redirect(f"{settings.FRONTEND_URL}/integrations?error=no_code")

    # Verify state (CSRF protection)
    session_state = request.session.get('google_oauth_state')
    if state != session_state:
        logger.error(f"State mismatch: {state} != {session_state}")
        return redirect(f"{settings.FRONTEND_URL}/integrations?error=invalid_state")

    # Get user from session
    user_id = request.session.get('oauth_user_id')
    if not user_id:
        logger.error("No user_id in session")
        return redirect(f"{settings.FRONTEND_URL}/integrations?error=no_user")

    try:
        # Exchange code for tokens
        backend_url = settings.BACKEND_URL.rstrip('/')
        redirect_uri = f"{backend_url}/api/integrations/calendar/callback/"

        logger.info(f"Exchanging code with redirect_uri: {redirect_uri}")
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

        logger.info(f"Calendar integration {'created' if created else 'updated'} for user {user_id}")

        # Clear session
        request.session.pop('google_oauth_state', None)
        request.session.pop('oauth_user_id', None)

        # Redirect to frontend success page
        return redirect(f"{settings.FRONTEND_URL}/integrations?success=calendar_connected")

    except Exception as e:
        logger.error(f"Error in OAuth callback: {e}", exc_info=True)
        return redirect(f"{settings.FRONTEND_URL}/integrations?error=callback_failed&message={str(e)}")


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


# ==================== GOOGLE SHEETS INTEGRATION ====================

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def connect_google_sheets(request):
    """
    Create Google Sheets integration and template spreadsheet

    This endpoint:
    1. Uses existing Google OAuth from Calendar (same credentials)
    2. Creates a new spreadsheet with template structure
    3. Saves spreadsheet_id to integration config
    """
    from .google_sheets import GoogleSheetsService

    try:
        # Check if user has Google Calendar integration (same OAuth)
        try:
            calendar_integration = Integration.objects.get(
                user_id=request.user.id,
                integration_type='google_calendar',
                status='active'
            )
        except Integration.DoesNotExist:
            logger.error(f"No active Google Calendar integration for user {request.user.id}")
            return Response({
                'error': 'Google Calendar not connected. Please connect Google Calendar first (uses same OAuth).'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Use the same credentials
        credentials = calendar_integration.get_credentials()

        # Create Sheets service
        sheets_service = GoogleSheetsService(credentials)

        # Create template spreadsheet
        organization_name = request.user.organization.name
        spreadsheet_data = sheets_service.create_template_spreadsheet(organization_name)

        # Create or update Sheets integration
        integration, created = Integration.objects.update_or_create(
            user_id=request.user.id,
            integration_type='google_sheets',
            defaults={
                'status': 'active',
                'config': {
                    'spreadsheet_id': spreadsheet_data['spreadsheet_id'],
                    'spreadsheet_url': spreadsheet_data['spreadsheet_url'],
                    'auto_export_enabled': True,
                    'auto_export_frequency': 'weekly'  # weekly, daily, manual
                }
            }
        )

        # Use the same credentials as Calendar
        integration.set_credentials(credentials)
        integration.save()

        return Response({
            'message': 'Google Sheets connected successfully',
            'integration': IntegrationSerializer(integration).data,
            'spreadsheet_url': spreadsheet_data['spreadsheet_url']
        })

    except Exception as e:
        logger.error(f"Error connecting Google Sheets: {e}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def export_to_sheets(request):
    """
    Manual export to Google Sheets

    Body params:
        - export_type: 'clients' | 'appointments' | 'all'
        - days: for appointments, how many days back (default 30)
    """
    from .google_sheets import GoogleSheetsService, SheetsExportHelper

    export_type = request.data.get('export_type', 'all')
    days = request.data.get('days', 30)

    try:
        # Get Sheets integration
        integration = Integration.objects.get(
            user_id=request.user.id,
            integration_type='google_sheets',
            status='active'
        )

        config = integration.config or {}
        spreadsheet_id = config.get('spreadsheet_id')

        if not spreadsheet_id:
            return Response(
                {'error': 'Spreadsheet not configured. Create a spreadsheet first.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get credentials and create service
        credentials = integration.get_credentials()
        sheets_service = GoogleSheetsService(credentials)

        tenant_schema = request.user.organization.schema_name
        results = {}

        # Export clients
        if export_type in ['clients', 'all']:
            clients_data = SheetsExportHelper.prepare_clients_export(tenant_schema)
            rows = sheets_service.export_clients(spreadsheet_id, clients_data)
            results['clients'] = f"{rows} clients exported"

        # Export appointments
        if export_type in ['appointments', 'all']:
            appointments_data = SheetsExportHelper.prepare_appointments_export(tenant_schema, days)
            rows = sheets_service.export_appointments(spreadsheet_id, appointments_data)
            results['appointments'] = f"{rows} appointments exported"

        return Response({
            'message': 'Export completed successfully',
            'results': results,
            'spreadsheet_url': config.get('spreadsheet_url')
        })

    except Integration.DoesNotExist:
        return Response(
            {'error': 'Google Sheets not connected'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Error exporting to Sheets: {e}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ==================== INSTAGRAM INTEGRATION ====================

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def instagram_auth_url(request):
    """
    Get Instagram/Facebook OAuth authorization URL

    Returns URL to redirect user for Instagram authorization via Facebook
    """
    from .instagram_manager import InstagramManager
    from django.conf import settings
    import secrets

    try:
        # Build redirect URI - ensure it's properly formatted
        backend_url = settings.BACKEND_URL.rstrip('/')
        redirect_uri = f"{backend_url}/api/integrations/instagram/callback/"

        # Generate state for CSRF protection
        state = secrets.token_urlsafe(32)

        # Store in session
        request.session['instagram_oauth_state'] = state
        request.session['oauth_user_id'] = request.user.id

        logger.info(f"Instagram OAuth redirect_uri: {redirect_uri}")

        # Get authorization URL
        auth_url = InstagramManager.get_authorization_url(redirect_uri, state)

        return Response({
            'authorization_url': auth_url,
            'state': state,
            'redirect_uri': redirect_uri  # Return for debugging
        })
    except Exception as e:
        logger.error(f"Error generating Instagram auth URL: {e}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.AllowAny])  # Will verify via session
def instagram_oauth_callback(request):
    """
    Instagram OAuth2 callback endpoint

    Facebook redirects here after user authorizes
    """
    from .instagram_manager import InstagramManager
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
    session_state = request.session.get('instagram_oauth_state')
    if state != session_state:
        return redirect(f"{settings.FRONTEND_URL}/integrations?error=invalid_state")

    # Get user from session
    user_id = request.session.get('oauth_user_id')
    if not user_id:
        return redirect(f"{settings.FRONTEND_URL}/integrations?error=no_user")

    try:
        # Exchange code for tokens
        backend_url = settings.BACKEND_URL.rstrip('/')
        redirect_uri = f"{backend_url}/api/integrations/instagram/callback/"

        logger.info(f"Exchanging Instagram code with redirect_uri: {redirect_uri}")
        result = InstagramManager.exchange_code_for_token(code, redirect_uri)

        # If no Instagram accounts found
        if not result['instagram_accounts']:
            return redirect(f"{settings.FRONTEND_URL}/integrations?error=no_instagram_account")

        # Get user
        from apps.accounts.models import User
        user = User.objects.get(id=user_id)

        # For now, use the first Instagram account
        # TODO: Let user choose if multiple accounts
        ig_account = result['instagram_accounts'][0]

        # Create or update integration
        integration, created = Integration.objects.update_or_create(
            user_id=user.id,
            integration_type='instagram',
            defaults={
                'status': 'active',
                'config': {
                    'instagram_username': ig_account['username'],
                    'instagram_name': ig_account['name'],
                    'page_id': ig_account['page_id'],
                    'page_name': ig_account['page_name'],
                    'auto_reply_enabled': True,
                    'working_hours': {
                        'start': '09:00',
                        'end': '20:00',
                        'days': ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']
                    }
                }
            }
        )

        # Store credentials
        integration.set_credentials({
            'access_token': ig_account['page_access_token'],
            'instagram_account_id': ig_account['id'],
            'page_id': ig_account['page_id']
        })
        integration.save()

        # Subscribe to webhooks
        from .instagram_manager import InstagramManager
        manager = InstagramManager(integration)
        manager.subscribe_to_webhooks()

        # Clear session
        request.session.pop('instagram_oauth_state', None)
        request.session.pop('oauth_user_id', None)

        # Redirect to frontend success page
        return redirect(f"{settings.FRONTEND_URL}/integrations?success=instagram_connected&username={ig_account['username']}")

    except Exception as e:
        logger.error(f"Error in Instagram OAuth callback: {e}")
        return redirect(f"{settings.FRONTEND_URL}/integrations?error=callback_failed")


@method_decorator(csrf_exempt, name='dispatch')
class InstagramWebhookView(APIView):
    """
    Instagram webhook endpoint (via Facebook Graph API)

    URL: /api/integrations/webhooks/instagram/

    Handles verification challenge and incoming messages
    """
    permission_classes = []

    def get(self, request):
        """
        Webhook verification (Facebook sends this during setup)
        """
        mode = request.GET.get('hub.mode')
        token = request.GET.get('hub.verify_token')
        challenge = request.GET.get('hub.challenge')

        # Verify token should match what we set in Facebook App settings
        import os
        verify_token = os.getenv('FACEBOOK_WEBHOOK_VERIFY_TOKEN', 'sloth_instagram_webhook_2024')

        if mode == 'subscribe' and token == verify_token:
            logger.info("Instagram webhook verified")
            return JsonResponse({'hub.challenge': int(challenge)})

        return JsonResponse({'error': 'Forbidden'}, status=403)

    def post(self, request):
        """
        Incoming Instagram messages
        """
        try:
            data = request.data

            # Log webhook event
            WebhookEvent.objects.create(
                source='instagram',
                event_type='message',
                payload=data
            )

            # Process message asynchronously
            from .instagram_manager import InstagramManagerSingleton

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            # Extract Instagram account ID from webhook data
            entry = data.get('entry', [])[0] if data.get('entry') else {}
            messaging = entry.get('messaging', [])[0] if entry.get('messaging') else {}
            instagram_account_id = messaging.get('recipient', {}).get('id', '')

            if instagram_account_id:
                manager_singleton = InstagramManagerSingleton()
                loop.run_until_complete(
                    manager_singleton.process_webhook(instagram_account_id, data)
                )

            loop.close()

            return JsonResponse({'ok': True})

        except Exception as e:
            logger.error(f"Instagram webhook error: {e}")
            return JsonResponse({'error': str(e)}, status=500)


# ==================== WEBSITE WIDGET INTEGRATION ====================

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def setup_website_widget(request):
    """
    Setup website chat widget integration

    Body params:
        - theme: 'light' | 'dark' | 'brand'
        - custom_colors: {} (optional)
        - position: 'bottom-right' | 'bottom-left'
        - welcome_message: str
        - placeholder: str
        - icon_url: str (optional)
        - show_branding: bool
        - auto_open: bool
        - auto_open_delay: int (ms)
    """
    from .widget_service import WidgetService

    try:
        # Get or create widget integration
        integration, created = Integration.objects.get_or_create(
            user_id=request.user.id,
            integration_type='website_widget',
            defaults={'status': 'active'}
        )

        # Generate widget key if new
        if created or not integration.config.get('widget_key'):
            widget_key = WidgetService.generate_widget_key(request.user.organization.id)
        else:
            widget_key = integration.config.get('widget_key')

        # Update configuration
        config = {
            'widget_key': widget_key,
            'theme': request.data.get('theme', 'light'),
            'custom_colors': request.data.get('custom_colors', {}),
            'position': request.data.get('position', 'bottom-right'),
            'welcome_message': request.data.get('welcome_message', 'Привіт! Як я можу допомогти?'),
            'placeholder': request.data.get('placeholder', 'Напишіть повідомлення...'),
            'icon_url': request.data.get('icon_url', None),
            'show_branding': request.data.get('show_branding', True),
            'auto_open': request.data.get('auto_open', False),
            'auto_open_delay': request.data.get('auto_open_delay', 3000),
        }

        integration.config = config
        integration.save()

        # Get embed code
        from django.conf import settings
        backend_url = settings.BACKEND_URL or request.build_absolute_uri('/').rstrip('/')
        embed_code = WidgetService.generate_embed_code(widget_key, backend_url)

        return Response({
            'message': 'Website widget configured successfully',
            'integration': IntegrationSerializer(integration).data,
            'widget_key': widget_key,
            'embed_code': embed_code,
            'preview_url': f"{backend_url}/api/integrations/widget/preview/{widget_key}/"
        })

    except Exception as e:
        logger.error(f"Error setting up website widget: {e}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_widget_config(request):
    """
    Get current widget configuration
    """
    from .widget_service import WidgetService

    try:
        integration = Integration.objects.get(
            user_id=request.user.id,
            integration_type='website_widget'
        )

        config = WidgetService.get_widget_config(integration)

        return Response({
            'config': config,
            'integration': IntegrationSerializer(integration).data
        })

    except Integration.DoesNotExist:
        return Response(
            {'error': 'Widget not configured'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([permissions.AllowAny])  # Public endpoint for widget
def widget_chat(request, widget_key):
    """
    Public chat endpoint for website widget

    Body:
        - message: str
        - session_id: str (optional, for conversation continuity)
    """
    from .widget_service import WidgetService
    from apps.agent.services import AgentService
    from apps.agent.models import Conversation, Message
    from django.db import connection

    try:
        # Validate widget key
        integration = WidgetService.validate_widget_key(widget_key)

        if not integration:
            return Response(
                {'error': 'Invalid widget key'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Get message
        user_message = request.data.get('message')
        session_id = request.data.get('session_id')

        if not user_message:
            return Response(
                {'error': 'Message is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get tenant schema
        tenant_schema = integration.organization.schema_name

        # Switch to tenant schema
        with connection.cursor() as cursor:
            cursor.execute(f"SET search_path TO {tenant_schema}, public")

        # Find or create conversation
        if session_id:
            try:
                conversation = Conversation.objects.get(
                    external_id=session_id,
                    source='website_widget'
                )
            except Conversation.DoesNotExist:
                conversation = Conversation.objects.create(
                    source='website_widget',
                    external_id=session_id,
                    client_name='Website Visitor',
                    metadata={'widget_key': widget_key}
                )
        else:
            # Create new conversation
            import uuid
            session_id = str(uuid.uuid4())
            conversation = Conversation.objects.create(
                source='website_widget',
                external_id=session_id,
                client_name='Website Visitor',
                metadata={'widget_key': widget_key}
            )

        # Save user message
        Message.objects.create(
            conversation=conversation,
            role='user',
            content=user_message
        )

        # Get AI response
        agent_service = AgentService(tenant_schema)
        ai_response = agent_service.chat(
            conversation_id=conversation.id,
            user_message=user_message
        )

        return Response({
            'message': ai_response['message']['content'],
            'session_id': session_id
        })

    except Exception as e:
        logger.error(f"Widget chat error: {e}")
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
