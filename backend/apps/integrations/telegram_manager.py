"""
Telegram Integration Service with dynamic bot management

Webhook mode - all bots share one webhook endpoint, but are routed by bot token
"""
import asyncio
from telegram import Update, Bot
from telegram.ext import Application, MessageHandler, CommandHandler, filters
from django.conf import settings
from apps.agent.services import AgentService
from apps.agent.models import Conversation
from .models import Integration
import logging

logger = logging.getLogger(__name__)


class TelegramBotManager:
    """
    Singleton manager for all Telegram bots

    Manages multiple bots (one per user) using webhook mode.
    All bots share the same webhook URL but are differentiated by bot token.
    """

    _instance = None
    _bots = {}  # {integration_id: {'app': Application, 'bot_token': str}}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def start_bot(self, integration):
        """
        Start/register a Telegram bot for a user

        This doesn't actually "run" the bot in long-polling mode.
        Instead, it registers the bot to handle webhooks.
        """
        if integration.id in self._bots:
            logger.info(f"Bot for integration {integration.id} already running")
            return True

        credentials = integration.get_credentials()
        bot_token = credentials.get('bot_token')

        if not bot_token:
            logger.error(f"No bot token for integration {integration.id}")
            return False

        try:
            # Create Application (new in python-telegram-bot 20.x)
            application = Application.builder().token(bot_token).build()

            # Add handlers
            application.add_handler(CommandHandler("start", self._handle_start))
            application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self._handle_message))

            # Store bot info
            self._bots[integration.id] = {
                'app': application,
                'bot_token': bot_token,
                'integration_id': integration.id
            }

            # Set webhook
            base_url = settings.BACKEND_URL or 'https://your-domain.com'
            webhook_url = f"{base_url}/api/integrations/webhooks/telegram/{bot_token}/"

            bot = Bot(token=bot_token)
            await bot.set_webhook(
                url=webhook_url,
                allowed_updates=["message", "callback_query"]
            )

            # Update integration status
            integration.status = 'active'
            integration.settings['webhook_url'] = webhook_url
            integration.save()

            logger.info(f"Started bot for integration {integration.id}")
            return True

        except Exception as e:
            logger.error(f"Error starting bot for integration {integration.id}: {e}")
            integration.status = 'error'
            integration.error_message = str(e)
            integration.save()
            return False

    async def stop_bot(self, integration_id):
        """Stop/unregister a Telegram bot"""
        if integration_id not in self._bots:
            return

        try:
            bot_info = self._bots[integration_id]
            bot = Bot(token=bot_info['bot_token'])

            # Remove webhook
            await bot.delete_webhook()

            # Remove from manager
            del self._bots[integration_id]

            logger.info(f"Stopped bot for integration {integration_id}")

        except Exception as e:
            logger.error(f"Error stopping bot {integration_id}: {e}")

    def get_bot_by_token(self, bot_token):
        """Find bot application by token"""
        for integration_id, bot_info in self._bots.items():
            if bot_info['bot_token'] == bot_token:
                return bot_info
        return None

    async def process_webhook_update(self, bot_token, update_data):
        """
        Process incoming webhook update

        Called by the webhook endpoint when Telegram sends an update
        """
        bot_info = self.get_bot_by_token(bot_token)

        if not bot_info:
            logger.error(f"No bot found for token {bot_token[:10]}...")
            return False

        try:
            # Create Update object from webhook data
            update = Update.de_json(update_data, bot_info['app'].bot)

            # Process update through the application
            await bot_info['app'].process_update(update)

            return True

        except Exception as e:
            logger.error(f"Error processing webhook update: {e}")
            return False

    async def _handle_start(self, update: Update, context):
        """Handle /start command"""
        await update.message.reply_text(
            "👋 Hello! I'm your AI assistant. How can I help you today?"
        )

    async def _handle_message(self, update: Update, context):
        """Handle incoming text messages"""
        # Get integration from bot token
        bot_token = context.application.bot.token
        bot_info = self.get_bot_by_token(bot_token)

        if not bot_info:
            return

        integration_id = bot_info['integration_id']

        try:
            # Get integration from database
            from apps.accounts.models import User
            from apps.accounts.middleware import TenantSchemaContext

            integration = Integration.objects.get(id=integration_id)
            user = User.objects.get(id=integration.user_id)

            # Increment received messages
            integration.messages_received += 1
            integration.save()

            # Get or create conversation
            chat_id = str(update.effective_chat.id)

            with TenantSchemaContext(user.organization.schema_name):
                conversation, _ = Conversation.objects.get_or_create(
                    user_id=integration.user_id,
                    source='telegram',
                    external_id=chat_id,
                    defaults={'title': f'Telegram: {update.effective_user.first_name}'}
                )

                # Process with AI agent
                agent = AgentService(
                    user_id=integration.user_id,
                    tenant_schema=user.organization.schema_name
                )

                result = agent.chat(
                    conversation_id=conversation.id,
                    user_message=update.message.text
                )

                # Send response
                await update.message.reply_text(result['message'])

                # Increment sent messages
                integration.messages_sent += 1
                integration.save()

        except Exception as e:
            logger.error(f"Error handling message: {e}")
            await update.message.reply_text(
                "Sorry, I encountered an error. Please try again later."
            )


# Singleton instance
telegram_bot_manager = TelegramBotManager()


# Helper functions for views
async def start_telegram_bot(integration):
    """Start a Telegram bot for an integration"""
    return await telegram_bot_manager.start_bot(integration)


async def stop_telegram_bot(integration_id):
    """Stop a Telegram bot"""
    return await telegram_bot_manager.stop_bot(integration_id)


async def process_telegram_webhook(bot_token, update_data):
    """Process incoming Telegram webhook"""
    return await telegram_bot_manager.process_webhook_update(bot_token, update_data)
