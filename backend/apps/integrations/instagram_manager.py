"""
Instagram Direct Messages Integration
Офіційна інтеграція через Meta Graph API
"""

import requests
import asyncio
from asgiref.sync import sync_to_async
from apps.integrations.models import Integration
from apps.agent.services import AgentService
from apps.agent.models import Conversation, Message
from django.db import connection
import json
import logging

logger = logging.getLogger(__name__)


class InstagramManager:
    """
    Менеджер для роботи з Instagram Direct Messages через Meta Graph API

    Офіційний метод вимагає:
    1. Instagram Business/Creator акаунт
    2. Facebook Page підключену до Instagram
    3. Meta App з дозволами: pages_messaging, instagram_basic, instagram_manage_messages
    """

    GRAPH_API_VERSION = 'v18.0'
    GRAPH_API_URL = f'https://graph.facebook.com/{GRAPH_API_VERSION}'

    def __init__(self, integration):
        """
        Args:
            integration: Integration модель з типом 'instagram'
        """
        self.integration = integration
        self.credentials = integration.get_credentials()
        self.access_token = self.credentials.get('access_token')
        self.instagram_account_id = self.credentials.get('instagram_account_id')
        self.page_id = self.credentials.get('page_id')

        self.config = integration.config or {}
        self.auto_reply_enabled = self.config.get('auto_reply_enabled', True)
        self.working_hours = self.config.get('working_hours', {'start': '09:00', 'end': '20:00'})

    @classmethod
    def get_authorization_url(cls, redirect_uri, state):
        """
        Генерує URL для Facebook OAuth авторизації

        Args:
            redirect_uri: URL для redirect після авторизації
            state: CSRF токен

        Returns:
            str: Authorization URL
        """
        from urllib.parse import urlencode

        # Permissions потрібні для Instagram messaging
        permissions = [
            'pages_show_list',
            'pages_messaging',
            'pages_manage_metadata',
            'instagram_basic',
            'instagram_manage_messages',
            'instagram_manage_comments'
        ]

        params = {
            'client_id': '<FACEBOOK_APP_ID>',  # TODO: Додати в settings
            'redirect_uri': redirect_uri,
            'state': state,
            'scope': ','.join(permissions),
            'response_type': 'code'
        }

        return f"https://www.facebook.com/v18.0/dialog/oauth?{urlencode(params)}"

    @classmethod
    def exchange_code_for_token(cls, code, redirect_uri):
        """
        Обмінює authorization code на access token

        Returns:
            dict: {
                'access_token': '...',
                'user_id': '...',
                'pages': [...],  # Список Facebook Pages
                'instagram_accounts': [...]  # Підключені Instagram акаунти
            }
        """
        import os

        # Отримуємо short-lived token
        params = {
            'client_id': os.getenv('FACEBOOK_APP_ID'),
            'client_secret': os.getenv('FACEBOOK_APP_SECRET'),
            'redirect_uri': redirect_uri,
            'code': code
        }

        response = requests.get(
            f'{cls.GRAPH_API_URL}/oauth/access_token',
            params=params
        )
        response.raise_for_status()
        data = response.json()

        short_token = data['access_token']

        # Отримуємо long-lived token (60 днів)
        params = {
            'grant_type': 'fb_exchange_token',
            'client_id': os.getenv('FACEBOOK_APP_ID'),
            'client_secret': os.getenv('FACEBOOK_APP_SECRET'),
            'fb_exchange_token': short_token
        }

        response = requests.get(
            f'{cls.GRAPH_API_URL}/oauth/access_token',
            params=params
        )
        response.raise_for_status()
        data = response.json()

        long_token = data['access_token']

        # Отримуємо список Facebook Pages користувача
        response = requests.get(
            f'{cls.GRAPH_API_URL}/me/accounts',
            params={'access_token': long_token}
        )
        response.raise_for_status()
        pages = response.json().get('data', [])

        # Для кожної Page отримуємо підключені Instagram акаунти
        instagram_accounts = []
        for page in pages:
            page_token = page['access_token']
            page_id = page['id']

            response = requests.get(
                f'{cls.GRAPH_API_URL}/{page_id}',
                params={
                    'fields': 'instagram_business_account',
                    'access_token': page_token
                }
            )

            if response.ok:
                ig_data = response.json()
                if 'instagram_business_account' in ig_data:
                    ig_account = ig_data['instagram_business_account']

                    # Отримуємо додаткову інфо про Instagram акаунт
                    ig_response = requests.get(
                        f'{cls.GRAPH_API_URL}/{ig_account["id"]}',
                        params={
                            'fields': 'username,name,profile_picture_url',
                            'access_token': page_token
                        }
                    )

                    if ig_response.ok:
                        ig_info = ig_response.json()
                        instagram_accounts.append({
                            'id': ig_account['id'],
                            'username': ig_info.get('username'),
                            'name': ig_info.get('name'),
                            'profile_picture_url': ig_info.get('profile_picture_url'),
                            'page_id': page_id,
                            'page_name': page['name'],
                            'page_access_token': page_token
                        })

        return {
            'access_token': long_token,
            'pages': pages,
            'instagram_accounts': instagram_accounts
        }

    def send_message(self, recipient_id, message_text):
        """
        Відправляє повідомлення в Instagram Direct

        Args:
            recipient_id: Instagram Scoped ID (IGSID) отримувача
            message_text: Текст повідомлення

        Returns:
            dict: Відповідь API
        """
        url = f'{self.GRAPH_API_URL}/{self.instagram_account_id}/messages'

        payload = {
            'recipient': {'id': recipient_id},
            'message': {'text': message_text}
        }

        params = {'access_token': self.access_token}

        response = requests.post(url, json=payload, params=params)

        if not response.ok:
            logger.error(f"Instagram API error: {response.text}")
            response.raise_for_status()

        return response.json()

    def send_media(self, recipient_id, media_url, media_type='image'):
        """
        Відправляє медіа (фото) в Instagram Direct

        Args:
            recipient_id: IGSID отримувача
            media_url: URL медіа файлу
            media_type: 'image' або 'video'
        """
        url = f'{self.GRAPH_API_URL}/{self.instagram_account_id}/messages'

        if media_type == 'image':
            attachment = {
                'type': 'image',
                'payload': {'url': media_url}
            }
        else:
            attachment = {
                'type': 'video',
                'payload': {'url': media_url}
            }

        payload = {
            'recipient': {'id': recipient_id},
            'message': {'attachment': attachment}
        }

        params = {'access_token': self.access_token}

        response = requests.post(url, json=payload, params=params)
        response.raise_for_status()

        return response.json()

    async def process_incoming_message(self, webhook_data):
        """
        Обробка вхідного повідомлення з Instagram webhook

        Args:
            webhook_data: Дані з Meta webhook
        """
        try:
            # Парсимо webhook дані
            entry = webhook_data.get('entry', [])[0]
            messaging = entry.get('messaging', [])[0]

            sender_id = messaging['sender']['id']
            recipient_id = messaging['recipient']['id']

            # Перевіряємо що повідомлення для нашого Instagram акаунту
            if recipient_id != self.instagram_account_id:
                logger.warning(f"Message not for our account: {recipient_id}")
                return

            # Отримуємо текст повідомлення
            message_data = messaging.get('message', {})
            message_text = message_data.get('text', '')
            message_id = message_data.get('mid')

            if not message_text:
                logger.info("No text in message, skipping")
                return

            # Перевіряємо чи увімкнено автовідповіді
            if not self.auto_reply_enabled:
                logger.info("Auto-reply disabled")
                return

            # Отримуємо інфо про відправника
            sender_info = await self._get_sender_info(sender_id)
            sender_username = sender_info.get('username', 'Unknown')
            sender_name = sender_info.get('name', sender_username)

            # Знаходимо або створюємо розмову
            tenant_schema = self.integration.organization.schema_name

            # Safely set schema using psycopg2.sql.Identifier to prevent SQL injection
            from psycopg2 import sql
            with connection.cursor() as cursor:
                cursor.execute(
                    sql.SQL("SET search_path TO {}, public").format(sql.Identifier(tenant_schema))
                )

            conversation, created = await sync_to_async(Conversation.objects.get_or_create)(
                source='instagram',
                external_id=sender_id,
                defaults={
                    'client_name': sender_name,
                    'phone_number': '',  # Instagram не дає номер
                    'email': '',
                    'metadata': {'instagram_username': sender_username}
                }
            )

            # Зберігаємо повідомлення користувача
            await sync_to_async(Message.objects.create)(
                conversation=conversation,
                role='user',
                content=message_text,
                metadata={'message_id': message_id}
            )

            # Обробляємо через AI Agent
            agent_service = AgentService(tenant_schema)

            try:
                ai_response = await sync_to_async(agent_service.chat)(
                    conversation_id=conversation.id,
                    user_message=message_text
                )

                # Відправляємо відповідь
                self.send_message(sender_id, ai_response['message']['content'])

            except Exception as e:
                logger.error(f"Error processing with AI: {e}")
                # Відправляємо fallback повідомлення
                self.send_message(
                    sender_id,
                    "Вибачте, сталася помилка. Спробуйте ще раз або зв'яжіться з нами пізніше."
                )

        except Exception as e:
            logger.error(f"Error processing Instagram message: {e}", exc_info=True)

    async def _get_sender_info(self, sender_id):
        """
        Отримує інформацію про відправника
        """
        try:
            response = requests.get(
                f'{self.GRAPH_API_URL}/{sender_id}',
                params={
                    'fields': 'id,username,name,profile_pic',
                    'access_token': self.access_token
                }
            )

            if response.ok:
                return response.json()

        except Exception as e:
            logger.error(f"Error getting sender info: {e}")

        return {'username': 'Unknown', 'name': 'Unknown'}

    def subscribe_to_webhooks(self):
        """
        Підписується на webhooks для Instagram повідомлень
        Викликається при активації інтеграції
        """
        # Subscribe до Page webhooks
        url = f'{self.GRAPH_API_URL}/{self.page_id}/subscribed_apps'

        params = {
            'subscribed_fields': 'messages,messaging_postbacks,messaging_optins',
            'access_token': self.access_token
        }

        response = requests.post(url, params=params)

        if not response.ok:
            logger.error(f"Webhook subscription failed: {response.text}")
            response.raise_for_status()

        return response.json()


# Singleton для управління активними Instagram інтеграціями
class InstagramManagerSingleton:
    _instance = None
    _managers = {}  # {integration_id: InstagramManager}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_manager(self, integration_id):
        """Отримує менеджер для конкретної інтеграції"""
        if integration_id not in self._managers:
            try:
                integration = Integration.objects.get(
                    id=integration_id,
                    integration_type='instagram'
                )
                self._managers[integration_id] = InstagramManager(integration)
            except Integration.DoesNotExist:
                return None

        return self._managers[integration_id]

    def reload_manager(self, integration_id):
        """Перезавантажує менеджер (після оновлення credentials)"""
        if integration_id in self._managers:
            del self._managers[integration_id]
        return self.get_manager(integration_id)

    async def process_webhook(self, instagram_account_id, webhook_data):
        """
        Обробляє webhook для конкретного Instagram акаунту
        """
        # Знаходимо інтеграцію по instagram_account_id
        try:
            integration = await sync_to_async(Integration.objects.get)(
                integration_type='instagram',
                is_active=True,
                credentials_encrypted__contains=instagram_account_id
            )

            manager = self.get_manager(integration.id)
            if manager:
                await manager.process_incoming_message(webhook_data)

        except Integration.DoesNotExist:
            logger.warning(f"No integration found for Instagram account: {instagram_account_id}")
