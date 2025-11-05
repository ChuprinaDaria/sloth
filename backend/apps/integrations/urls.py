from django.urls import path
from .views import (
    IntegrationListView, connect_telegram, connect_whatsapp,
    disconnect_integration, calendar_auth_url, calendar_oauth_callback,
    calendar_available_slots,
    connect_google_sheets, export_to_sheets,
    instagram_auth_url, instagram_oauth_callback,
    setup_website_widget, get_widget_config, widget_chat,
    TelegramWebhookView, WhatsAppWebhookView, InstagramWebhookView
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

    # Google Sheets
    path('sheets/connect/', connect_google_sheets, name='connect_sheets'),
    path('sheets/export/', export_to_sheets, name='export_sheets'),

    # Instagram OAuth2
    path('instagram/auth/', instagram_auth_url, name='instagram_auth'),
    path('instagram/callback/', instagram_oauth_callback, name='instagram_callback'),

    # Website Widget
    path('widget/setup/', setup_website_widget, name='setup_widget'),
    path('widget/config/', get_widget_config, name='widget_config'),
    path('widget/chat/<str:widget_key>/', widget_chat, name='widget_chat'),

    # Webhooks - bot_token in URL path for Telegram
    path('webhooks/telegram/<str:bot_token>/', TelegramWebhookView.as_view(), name='telegram_webhook'),
    path('webhooks/whatsapp/', WhatsAppWebhookView.as_view(), name='whatsapp_webhook'),
    path('webhooks/instagram/', InstagramWebhookView.as_view(), name='instagram_webhook'),
]
