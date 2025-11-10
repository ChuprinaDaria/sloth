from django.apps import AppConfig


class SubscriptionsConfig(AppConfig):
    name = 'apps.subscriptions'
    verbose_name = 'Subscriptions'

    def ready(self):
        # Import signal handlers
        from . import signals  # noqa: F401


