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
    _token_cache = {}  # {bot_token: (schema_name, integration_id, user_id, cached_at)}

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

            # Initialize and start application (required for processing updates)
            await application.initialize()
            await application.start()

            # Store bot info
            self._bots[integration.id] = {
                'app': application,
                'bot_token': bot_token,
                'integration_id': integration.id
            }

            # Set webhook
            # BACKEND_URL must be set in .env file!
            if not settings.BACKEND_URL:
                raise ValueError(
                    "BACKEND_URL is not configured in environment variables. "
                    "Please set BACKEND_URL=https://sloth-ai.lazysoft.pl in your .env file."
                )
            base_url = settings.BACKEND_URL.rstrip('/')
            webhook_url = f"{base_url}/api/integrations/webhooks/telegram/{bot_token}/"
            
            # Telegram requires HTTPS for webhooks
            if not webhook_url.startswith('https://'):
                raise ValueError(
                    f"BACKEND_URL must use HTTPS for Telegram webhooks. "
                    f"Current: {settings.BACKEND_URL}. "
                    f"Please set BACKEND_URL=https://sloth-ai.lazysoft.pl in your .env file."
                )

            logger.info(f"Setting Telegram webhook to: {webhook_url}")

            bot = Bot(token=bot_token)
            try:
                webhook_info = await bot.set_webhook(
                    url=webhook_url,
                    allowed_updates=["message", "callback_query"]
                )
                logger.info(f"Webhook set successfully: {webhook_info}")
            except Exception as webhook_error:
                logger.error(f"Error setting webhook: {webhook_error}")
                raise

            # Update integration status - use sync_to_async for database operations
            from asgiref.sync import sync_to_async
            
            @sync_to_async
            def update_integration_success():
                integration.status = 'active'
                integration.settings['webhook_url'] = webhook_url
                integration.save()
            
            await update_integration_success()

            logger.info(f"Started bot for integration {integration.id}")
            return True

        except Exception as e:
            logger.error(f"Error starting bot for integration {integration.id}: {e}", exc_info=True)
            
            from asgiref.sync import sync_to_async
            
            @sync_to_async
            def update_integration_error():
                integration.status = 'error'
                integration.error_message = str(e)
                integration.save()
            
            await update_integration_error()
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

            # Stop and shutdown application
            try:
                await bot_info['app'].stop()
            except Exception:
                pass
            try:
                await bot_info['app'].shutdown()
            except Exception:
                pass

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
            # Try to lazily start the bot by locating integration across tenants
            try:
                started = await self._lazy_start_bot_by_token(bot_token)
                if not started:
                    # Fallback: handle webhook directly without Application registry
                    logger.error(f"No bot found for token {bot_token[:10]}... Using direct handler.")
                    handled = await self._handle_webhook_direct(bot_token, update_data)
                    return handled
                # Re-check after starting
                bot_info = self.get_bot_by_token(bot_token)
                if not bot_info:
                    logger.error(f"Bot start did not register for token {bot_token[:10]}...")
                    return False
            except Exception as e:
                logger.error(f"Error lazily starting bot for token {bot_token[:10]}: {e}")
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

    async def _lazy_start_bot_by_token(self, bot_token: str) -> bool:
        """
        Try to find and start a Telegram bot by its token across all tenants.
        Used when a webhook arrives before the bot registry is populated in this worker.
        Uses cache to speed up repeated lookups.
        """
        import time
        try:
            from asgiref.sync import sync_to_async
            from apps.accounts.models import Organization
            from apps.accounts.middleware import TenantSchemaContext
            # Local import to avoid circulars
            from .models import Integration as IntegrationModel

            # Check cache first
            cache_entry = self._token_cache.get(bot_token)
            if cache_entry:
                schema_name, integration_id, user_id, cached_at = cache_entry
                if time.time() - cached_at < 300:  # 5 minutes
                    logger.info(f"Lazy start using cached integration for token {bot_token[:10]}")
                else:
                    del self._token_cache[bot_token]
                    cache_entry = None
            
            if not cache_entry:
                @sync_to_async
                def find_integration():
                    # Iterate all organizations; some tenants may have is_active=False but valid integrations
                    for org in Organization.objects.all():
                        try:
                            with TenantSchemaContext(org.schema_name):
                                qs = IntegrationModel.objects.filter(
                                    integration_type='telegram',
                                    status='active'
                                )
                                for integ in qs:
                                    try:
                                        creds = integ.get_credentials()
                                        if creds.get('bot_token') == bot_token:
                                            return org.schema_name, integ.id, integ.user_id
                                    except Exception:
                                        continue
                        except Exception:
                            continue
                    return None, None, None

                schema_name, integration_id, user_id = await find_integration()
                if not schema_name or not integration_id:
                    return False
                
                # Cache the result
                self._token_cache[bot_token] = (schema_name, integration_id, user_id, time.time())

            @sync_to_async
            def get_integration_instance():
                with TenantSchemaContext(schema_name):
                    return IntegrationModel.objects.get(id=integration_id)

            integration = await get_integration_instance()
            return await self.start_bot(integration)
        except Exception as e:
            logger.error(f"Lazy start error for token {bot_token[:10]}: {e}")
            return False

    async def _handle_webhook_direct(self, bot_token: str, update_data) -> bool:
        """
        Stateless fallback: find integration by token, process text message,
        and reply using a fresh Bot without relying on in-memory registry.
        Uses caching to speed up repeated lookups.
        """
        import time
        start_time = time.time()
        
        try:
            from asgiref.sync import sync_to_async
            from apps.accounts.models import Organization, User
            from apps.accounts.middleware import TenantSchemaContext
            from .models import Integration as IntegrationModel

            # Check cache first (cache for 5 minutes)
            cache_entry = self._token_cache.get(bot_token)
            if cache_entry:
                schema_name, integration_id, user_id, cached_at = cache_entry
                if time.time() - cached_at < 300:  # 5 minutes
                    logger.info(f"Using cached integration for token {bot_token[:10]} (cache hit in {time.time() - start_time:.3f}s)")
                else:
                    # Cache expired
                    del self._token_cache[bot_token]
                    cache_entry = None
            
            if not cache_entry:
                @sync_to_async
                def find_integration():
                    # Iterate all organizations; some tenants may have is_active=False but valid integrations
                    for org in Organization.objects.all():
                        try:
                            with TenantSchemaContext(org.schema_name):
                                for integ in IntegrationModel.objects.filter(
                                    integration_type='telegram',
                                    status='active'
                                ):
                                    try:
                                        creds = integ.get_credentials()
                                        if creds.get('bot_token') == bot_token:
                                            return org.schema_name, integ.id, integ.user_id
                                    except Exception:
                                        continue
                        except Exception:
                            continue
                    return None, None, None

                find_start = time.time()
                schema_name, integration_id, user_id = await find_integration()
                logger.info(f"Integration lookup took {time.time() - find_start:.3f}s for token {bot_token[:10]}")
                
                if not schema_name or not integration_id or not user_id:
                    logger.error(f"Direct handler could not resolve integration for token {bot_token[:10]}")
                    return False
                
                # Cache the result
                self._token_cache[bot_token] = (schema_name, integration_id, user_id, time.time())

            # Extract message text and chat_id
            message = update_data.get('message') or {}
            chat = message.get('chat') or {}
            chat_id = chat.get('id')
            text = message.get('text')
            if not chat_id or not text:
                return True  # Nothing to do

            @sync_to_async
            def process_sync():
                from apps.agent.models import Conversation
                with TenantSchemaContext(schema_name):
                    conversation, _ = Conversation.objects.get_or_create(
                        user_id=user_id,
                        source='telegram',
                        external_id=str(chat_id),
                        defaults={'title': 'Telegram'}
                    )
                    from apps.agent.services import AgentService
                    agent = AgentService(user_id=user_id, tenant_schema=schema_name)
                    result = agent.chat(conversation_id=conversation.id, user_message=text)
                    return result

            process_start = time.time()
            result = await process_sync()
            logger.info(f"AI processing took {time.time() - process_start:.3f}s for token {bot_token[:10]}")

            # Reply via fresh bot
            reply_start = time.time()
            reply_bot = Bot(token=bot_token)
            await reply_bot.send_message(chat_id=chat_id, text=result['message'])
            logger.info(f"Reply sent in {time.time() - reply_start:.3f}s for token {bot_token[:10]}")
            
            logger.info(f"Total webhook processing took {time.time() - start_time:.3f}s for token {bot_token[:10]}")
            return True
        except Exception as e:
            logger.error(f"Direct webhook handler error: {e}")
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
            logger.warning(f"No bot info found for token {bot_token[:10]}...")
            return

        integration_id = bot_info['integration_id']

        try:
            # Import sync_to_async for database operations
            from asgiref.sync import sync_to_async
            from apps.accounts.models import User
            from apps.accounts.middleware import TenantSchemaContext

            # Get integration from database (async)
            integration = await sync_to_async(Integration.objects.get)(id=integration_id)

            # Fetch user with organization safely in async context
            @sync_to_async
            def get_user_and_org():
                user_obj = User.objects.select_related('organization').get(id=integration.user_id)
                return user_obj, user_obj.organization

            user, organization = await get_user_and_org()

            # Check if user has organization
            if organization is None:
                logger.error(f"User {user.id} has no organization")
                await update.message.reply_text(
                    "Your account is not properly configured. Please contact support."
                )
                return

            # Increment received messages (async)
            integration.messages_received += 1
            await sync_to_async(integration.save)()

            # Get or create conversation
            chat_id = str(update.effective_chat.id)
            user_first_name = update.effective_user.first_name or "User"

            # Process with AI agent (sync function in async context)
            @sync_to_async
            def process_message():
                with TenantSchemaContext(organization.schema_name):
                    integration_obj = Integration.objects.get(id=integration_id)
                    conversation, _ = Conversation.objects.get_or_create(
                        user_id=integration.user_id,
                        source='telegram',
                        external_id=chat_id,
                        defaults={'title': f'Telegram: {user_first_name}'}
                    )

                    # Process with AI agent
                    agent = AgentService(
                        user_id=integration_obj.user_id,
                        tenant_schema=organization.schema_name
                    )

                    result = agent.chat(
                        conversation_id=conversation.id,
                        user_message=update.message.text
                    )

                    # Increment sent messages
                    integration_obj.messages_sent += 1
                    integration_obj.save()

                    return result

            result = await process_message()

            # Send response
            try:
                # Avoid using Application's bot tied to a different/closed loop.
                # Create a fresh Bot bound to the current event loop.
                reply_bot = Bot(token=bot_token)
                await reply_bot.send_message(chat_id=update.effective_chat.id, text=result['message'])
            except Exception as send_error:
                logger.error(f"Error sending reply via Bot: {send_error}")

        except Exception as e:
            # Detailed error logging
            import traceback
            error_details = traceback.format_exc()
            logger.error(f"Error handling Telegram message: {str(e)}\n{error_details}")

            # Send user-friendly error message
            try:
                await update.message.reply_text(
                    "Sorry, I encountered an error. Please try again later."
                )
            except Exception as send_error:
                logger.error(f"Error sending error message: {send_error}")


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
