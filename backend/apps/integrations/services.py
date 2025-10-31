import telegram
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from twilio.rest import Client
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from django.conf import settings
from apps.agent.services import AgentService
from apps.agent.models import Conversation
from .models import Integration


class TelegramService:
    """Service for Telegram Bot integration"""

    def __init__(self, integration):
        self.integration = integration
        credentials = integration.get_credentials()
        self.bot_token = credentials.get('bot_token', settings.TELEGRAM_BOT_TOKEN)
        self.bot = Bot(token=self.bot_token)

    async def send_message(self, chat_id, text):
        """Send message to Telegram"""
        try:
            await self.bot.send_message(chat_id=chat_id, text=text)
            self.integration.messages_sent += 1
            self.integration.save()
            return True
        except Exception as e:
            print(f"Error sending Telegram message: {e}")
            return False

    async def handle_message(self, update: Update, context):
        """Handle incoming Telegram message"""
        chat_id = update.effective_chat.id
        user_message = update.message.text

        # Increment received counter
        self.integration.messages_received += 1
        self.integration.save()

        # Get or create conversation for this Telegram chat
        from apps.accounts.middleware import TenantSchemaContext
        from django.contrib.auth import get_user_model

        User = get_user_model()
        user = User.objects.get(id=self.integration.user_id)

        with TenantSchemaContext(user.organization.schema_name):
            conversation, _ = Conversation.objects.get_or_create(
                user_id=self.integration.user_id,
                source='telegram',
                external_id=str(chat_id)
            )

            # Process message with AI agent
            agent = AgentService(
                user_id=self.integration.user_id,
                tenant_schema=user.organization.schema_name
            )

            try:
                result = agent.chat(
                    conversation_id=conversation.id,
                    user_message=user_message
                )

                # Send response
                await self.send_message(chat_id, result['message'])

            except Exception as e:
                await self.send_message(
                    chat_id,
                    "Sorry, I encountered an error processing your message."
                )

    def setup_webhook(self, webhook_url):
        """Setup Telegram webhook"""
        try:
            import asyncio
            asyncio.run(self.bot.set_webhook(url=webhook_url))
            return True
        except Exception as e:
            print(f"Error setting Telegram webhook: {e}")
            return False


class WhatsAppService:
    """Service for WhatsApp Business (via Twilio)"""

    def __init__(self, integration):
        self.integration = integration
        credentials = integration.get_credentials()

        self.client = Client(
            credentials.get('account_sid', settings.TWILIO_ACCOUNT_SID),
            credentials.get('auth_token', settings.TWILIO_AUTH_TOKEN)
        )
        self.from_number = credentials.get('whatsapp_number', settings.TWILIO_WHATSAPP_NUMBER)

    def send_message(self, to_number, message):
        """Send WhatsApp message"""
        try:
            message = self.client.messages.create(
                body=message,
                from_=f'whatsapp:{self.from_number}',
                to=f'whatsapp:{to_number}'
            )

            self.integration.messages_sent += 1
            self.integration.save()

            return message.sid

        except Exception as e:
            print(f"Error sending WhatsApp message: {e}")
            return None

    def handle_webhook(self, from_number, message_body):
        """Handle incoming WhatsApp message"""
        # Increment received counter
        self.integration.messages_received += 1
        self.integration.save()

        # Get or create conversation
        from apps.accounts.middleware import TenantSchemaContext
        from django.contrib.auth import get_user_model

        User = get_user_model()
        user = User.objects.get(id=self.integration.user_id)

        with TenantSchemaContext(user.organization.schema_name):
            conversation, _ = Conversation.objects.get_or_create(
                user_id=self.integration.user_id,
                source='whatsapp',
                external_id=from_number
            )

            # Process with AI agent
            agent = AgentService(
                user_id=self.integration.user_id,
                tenant_schema=user.organization.schema_name
            )

            try:
                result = agent.chat(
                    conversation_id=conversation.id,
                    user_message=message_body
                )

                # Send response
                self.send_message(from_number, result['message'])

            except Exception as e:
                self.send_message(
                    from_number,
                    "Sorry, I encountered an error processing your message."
                )


class GoogleCalendarService:
    """Service for Google Calendar integration"""

    def __init__(self, integration):
        self.integration = integration
        credentials_dict = integration.get_credentials()

        self.credentials = Credentials(
            token=credentials_dict.get('access_token'),
            refresh_token=credentials_dict.get('refresh_token'),
            token_uri='https://oauth2.googleapis.com/token',
            client_id=settings.GOOGLE_CLIENT_ID,
            client_secret=settings.GOOGLE_CLIENT_SECRET
        )

        self.service = build('calendar', 'v3', credentials=self.credentials)

    def list_events(self, max_results=10):
        """List upcoming calendar events"""
        try:
            events_result = self.service.events().list(
                calendarId='primary',
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            return events_result.get('items', [])

        except Exception as e:
            print(f"Error listing calendar events: {e}")
            return []

    def create_event(self, summary, start_time, end_time, description=''):
        """Create calendar event"""
        try:
            event = {
                'summary': summary,
                'description': description,
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': 'UTC',
                },
            }

            event = self.service.events().insert(
                calendarId='primary',
                body=event
            ).execute()

            return event

        except Exception as e:
            print(f"Error creating calendar event: {e}")
            return None
