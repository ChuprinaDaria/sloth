from django.apps import AppConfig


class IntegrationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.integrations'
    verbose_name = 'Integrations'

    def ready(self):
        """
        Called when Django starts

        Start all active Telegram bots that were previously connected
        """
        # Import here to avoid AppRegistryNotReady error
        # Тимчасово закоментовано щоб не блокувати старт
        # from .tasks import start_all_active_telegram_bots

        # Start bots in background task (don't block Django startup)
        # try:
        #     start_all_active_telegram_bots.delay()
        # except Exception as e:
        #     import logging
        #     logger = logging.getLogger(__name__)
        #     logger.warning(f"Could not start Telegram bots on startup: {e}")
