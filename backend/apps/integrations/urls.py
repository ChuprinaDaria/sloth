from django.urls import path
from .views import (
    IntegrationListView, connect_telegram, connect_whatsapp,
    disconnect_integration, calendar_auth_url, calendar_oauth_callback,
    calendar_available_slots,
    TelegramWebhookView, WhatsAppWebhookView
)

app_name = 'integrations'

urlpatterns = [
    # Integration management
    path('', IntegrationListView.as_view(), name='list'),
    path('telegram/connect/', connect_telegram, name='connect_telegram'),
    path('whatsapp/connect/', connect_whatsapp, name='connect_whatsapp'),
    path('<int:pk>/', disconnect_integration, name='disconnect'),

    # Google Calendar OAuth2
    path('calendar/auth/', calendar_auth_url, name='calendar_auth'),
    path('calendar/callback/', calendar_oauth_callback, name='calendar_callback'),
    path('calendar/slots/', calendar_available_slots, name='calendar_slots'),

    # Webhooks - bot_token in URL path for Telegram
    path('webhooks/telegram/<str:bot_token>/', TelegramWebhookView.as_view(), name='telegram_webhook'),
    path('webhooks/whatsapp/', WhatsAppWebhookView.as_view(), name='whatsapp_webhook'),
]
