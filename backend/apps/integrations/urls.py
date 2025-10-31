from django.urls import path
from .views import (
    IntegrationListView, connect_telegram, connect_whatsapp,
    connect_calendar, disconnect_integration,
    TelegramWebhookView, WhatsAppWebhookView
)

app_name = 'integrations'

urlpatterns = [
    # Integration management
    path('', IntegrationListView.as_view(), name='list'),
    path('telegram/connect/', connect_telegram, name='connect_telegram'),
    path('whatsapp/connect/', connect_whatsapp, name='connect_whatsapp'),
    path('calendar/connect/', connect_calendar, name='connect_calendar'),
    path('<int:pk>/', disconnect_integration, name='disconnect'),

    # Webhooks - bot_token in URL path for Telegram
    path('webhooks/telegram/<str:bot_token>/', TelegramWebhookView.as_view(), name='telegram_webhook'),
    path('webhooks/whatsapp/', WhatsAppWebhookView.as_view(), name='whatsapp_webhook'),
]
