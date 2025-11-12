from django.apps import AppConfig
import logging
import threading


class IntegrationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.integrations'
    verbose_name = 'Integrations'

    def ready(self):
        """
        Called when Django starts

        Start all active Telegram bots that were previously connected
        """
        logger = logging.getLogger(__name__)

        def bootstrap_telegram_bots():
            """
            Run in background thread to avoid blocking startup:
            - Iterate all organizations (public schema)
            - Switch to each tenant schema
            - Start all active telegram bots in that schema
            This ensures every gunicorn worker has in-memory registry populated.
            """
            try:
                from apps.accounts.models import Organization
                from apps.accounts.middleware import TenantSchemaContext
                from .models import Integration
                from .telegram_manager import start_telegram_bot
                from .tasks import run_async_in_thread

                orgs = Organization.objects.filter(is_active=True)
                for org in orgs:
                    try:
                        with TenantSchemaContext(org.schema_name):
                            active_bots = Integration.objects.filter(
                                integration_type='telegram',
                                status='active'
                            )
                            for integration in active_bots:
                                try:
                                    run_async_in_thread(start_telegram_bot(integration))
                                except Exception as bot_err:
                                    logger.warning(
                                        f"Could not start Telegram bot {integration.id} "
                                        f"for tenant {org.schema_name}: {bot_err}"
                                    )
                    except Exception as tenant_err:
                        logger.error(f"Error bootstrapping tenant {org.schema_name}: {tenant_err}")
            except Exception as e:
                logger.error(f"Failed to bootstrap Telegram bots: {e}")

        # Start in background (daemon) so we don't block startup
        try:
            thread = threading.Thread(target=bootstrap_telegram_bots, daemon=True)
            thread.start()
        except Exception as e:
            logger.warning(f"Could not launch Telegram bots bootstrap thread: {e}")
