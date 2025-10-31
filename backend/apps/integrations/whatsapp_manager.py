"""
WhatsApp Integration via Twilio

Webhook-based approach - simpler than Telegram
Each user gets one WhatsApp number, Twilio sends webhooks
"""
from twilio.rest import Client
from django.conf import settings
from apps.agent.services import AgentService
from apps.agent.models import Conversation
from apps.accounts.models import User
from apps.accounts.middleware import TenantSchemaContext
from .models import Integration
import logging

logger = logging.getLogger(__name__)


class WhatsAppManager:
    """
    WhatsApp Business manager via Twilio

    Simpler than Telegram - each Twilio number is mapped to one user.
    No need for dynamic bot management.
    """

    @staticmethod
    def send_message(integration, to_number, message):
        """Send WhatsApp message via Twilio"""
        try:
            credentials = integration.get_credentials()

            client = Client(
                credentials.get('account_sid', settings.TWILIO_ACCOUNT_SID),
                credentials.get('auth_token', settings.TWILIO_AUTH_TOKEN)
            )

            from_number = credentials.get('whatsapp_number', settings.TWILIO_WHATSAPP_NUMBER)

            message = client.messages.create(
                body=message,
                from_=f'whatsapp:{from_number}',
                to=f'whatsapp:{to_number}'
            )

            # Increment sent counter
            integration.messages_sent += 1
            integration.save()

            return message.sid

        except Exception as e:
            logger.error(f"Error sending WhatsApp message: {e}")
            integration.error_count += 1
            integration.error_message = str(e)
            integration.save()
            return None

    @staticmethod
    def process_incoming_message(from_number, to_number, message_body):
        """
        Process incoming WhatsApp message

        Called by webhook endpoint
        """
        try:
            # Find integration by WhatsApp number
            # We need to find which user owns this Twilio number
            integration = Integration.objects.filter(
                integration_type='whatsapp',
                status='active',
                credentials_encrypted__contains=to_number.replace('whatsapp:', '')
            ).first()

            if not integration:
                logger.error(f"No integration found for WhatsApp number {to_number}")
                return False

            # Get user
            user = User.objects.get(id=integration.user_id)

            # Increment received messages
            integration.messages_received += 1
            integration.save()

            # Get or create conversation
            clean_from_number = from_number.replace('whatsapp:', '')

            with TenantSchemaContext(user.organization.schema_name):
                conversation, _ = Conversation.objects.get_or_create(
                    user_id=integration.user_id,
                    source='whatsapp',
                    external_id=clean_from_number,
                    defaults={'title': f'WhatsApp: {clean_from_number}'}
                )

                # Process with AI agent
                agent = AgentService(
                    user_id=integration.user_id,
                    tenant_schema=user.organization.schema_name
                )

                result = agent.chat(
                    conversation_id=conversation.id,
                    user_message=message_body
                )

                # Send response
                WhatsAppManager.send_message(
                    integration,
                    clean_from_number,
                    result['message']
                )

            return True

        except Exception as e:
            logger.error(f"Error processing WhatsApp message: {e}")
            return False

    @staticmethod
    def setup_webhook(integration, webhook_url):
        """
        Setup Twilio webhook

        Note: This needs to be done in Twilio console or via API
        Twilio doesn't allow programmatic webhook setup for WhatsApp
        """
        integration.settings['webhook_url'] = webhook_url
        integration.status = 'active'
        integration.save()

        return True


# Singleton instance
whatsapp_manager = WhatsAppManager()
