"""
Email Integration Service - Gmail and Custom Email Support
"""
import os
import base64
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime, timedelta


class EmailIntegrationService:
    """
    Сервіс для інтеграції з email (Gmail API + SMTP)
    Підтримує Gmail та корпоративні email
    """

    def __init__(self, user_id, tenant_schema):
        self.user_id = user_id
        self.tenant_schema = tenant_schema

    def get_integration_settings(self):
        """Get email integration settings for user"""
        from .models import Integration

        try:
            integration = Integration.objects.filter(
                user_id=self.user_id,
                integration_type='email',
                status='active'
            ).first()

            return integration
        except Exception as e:
            print(f"Error getting email integration: {e}")
            return None

    def is_gmail(self, email):
        """Check if email is Gmail"""
        return email.endswith('@gmail.com')

    def send_email_via_gmail_api(self, to_email, subject, message_body, html=False):
        """
        Відправити email через Gmail API

        Args:
            to_email: одержувач
            subject: тема
            message_body: текст повідомлення
            html: чи це HTML повідомлення

        Returns:
            dict: результат відправки
        """
        try:
            integration = self.get_integration_settings()
            if not integration:
                return {'success': False, 'error': 'Gmail not connected'}

            # Get credentials from encrypted storage
            credentials = integration.get_credentials()
            if not credentials.get('access_token'):
                return {'success': False, 'error': 'Gmail not connected'}

            # Створити credentials з токену
            creds = Credentials(
                token=credentials['access_token'],
                refresh_token=credentials.get('refresh_token'),
                token_uri='https://oauth2.googleapis.com/token',
                client_id=settings.GOOGLE_CLIENT_ID,
                client_secret=settings.GOOGLE_CLIENT_SECRET
            )

            # Build Gmail service
            service = build('gmail', 'v1', credentials=creds)

            # Create message
            if html:
                message = MIMEMultipart('alternative')
                message['to'] = to_email
                message['from'] = integration.config.get('email', '')
                message['subject'] = subject

                text_part = MIMEText(message_body, 'plain')
                html_part = MIMEText(message_body, 'html')
                message.attach(text_part)
                message.attach(html_part)
            else:
                message = MIMEText(message_body)
                message['to'] = to_email
                message['from'] = integration.config.get('email', '')
                message['subject'] = subject

            # Encode message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

            # Send message
            sent_message = service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()

            return {
                'success': True,
                'message_id': sent_message['id']
            }

        except Exception as e:
            print(f"Error sending via Gmail API: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def send_email_via_smtp(self, to_email, subject, message_body):
        """
        Відправити email через SMTP (для корпоративних email)

        Args:
            to_email: одержувач
            subject: тема
            message_body: текст

        Returns:
            dict: результат
        """
        try:
            integration = self.get_integration_settings()
            if not integration:
                # Використати Django's default email
                send_mail(
                    subject=subject,
                    message=message_body,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[to_email],
                    fail_silently=False,
                )
                return {'success': True}

            # Використати налаштування з інтеграції
            smtp_config = integration.config.get('smtp', {})

            if not smtp_config:
                # Fallback to default
                send_mail(
                    subject=subject,
                    message=message_body,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[to_email],
                    fail_silently=False,
                )
                return {'success': True}

            # TODO: Custom SMTP implementation
            # For now, use Django's default
            send_mail(
                subject=subject,
                message=message_body,
                from_email=smtp_config.get('from_email', settings.DEFAULT_FROM_EMAIL),
                recipient_list=[to_email],
                fail_silently=False,
            )

            return {'success': True}

        except Exception as e:
            print(f"Error sending via SMTP: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def send_email(self, to_email, subject, message_body, html=False):
        """
        Універсальний метод відправки email

        Args:
            to_email: одержувач
            subject: тема
            message_body: текст
            html: HTML чи ні

        Returns:
            dict: результат
        """
        integration = self.get_integration_settings()

        # Якщо є Gmail інтеграція - використати Gmail API
        if integration and integration.config.get('provider') == 'gmail':
            return self.send_email_via_gmail_api(to_email, subject, message_body, html)
        else:
            # Інакше - SMTP
            return self.send_email_via_smtp(to_email, subject, message_body)

    def get_gmail_analytics(self, days=30):
        """
        Отримати аналітику з Gmail

        Args:
            days: за скільки днів

        Returns:
            dict: статистика email
        """
        try:
            integration = self.get_integration_settings()
            if not integration or integration.config.get('provider') != 'gmail':
                return {'success': False, 'error': 'Gmail not connected'}

            # Get credentials from encrypted storage
            credentials = integration.get_credentials()
            if not credentials.get('access_token'):
                return {'success': False, 'error': 'Gmail credentials missing'}

            # Створити credentials
            creds = Credentials(
                token=credentials['access_token'],
                refresh_token=credentials.get('refresh_token'),
                token_uri='https://oauth2.googleapis.com/token',
                client_id=settings.GOOGLE_CLIENT_ID,
                client_secret=settings.GOOGLE_CLIENT_SECRET
            )

            # Build Gmail service
            service = build('gmail', 'v1', credentials=creds)

            # Розрахувати дату
            since_date = (datetime.now() - timedelta(days=days)).strftime('%Y/%m/%d')

            # Отримати статистику
            # 1. Всього отриманих email
            received_query = f'after:{since_date} in:inbox'
            received_results = service.users().messages().list(
                userId='me',
                q=received_query,
                maxResults=500
            ).execute()

            received_count = len(received_results.get('messages', []))

            # 2. Відправлені email
            sent_query = f'after:{since_date} in:sent'
            sent_results = service.users().messages().list(
                userId='me',
                q=sent_query,
                maxResults=500
            ).execute()

            sent_count = len(sent_results.get('messages', []))

            # 3. Непрочитані
            unread_results = service.users().messages().list(
                userId='me',
                q='is:unread',
                maxResults=500
            ).execute()

            unread_count = len(unread_results.get('messages', []))

            # 4. Важливі (starred)
            starred_results = service.users().messages().list(
                userId='me',
                q='is:starred',
                maxResults=100
            ).execute()

            starred_count = len(starred_results.get('messages', []))

            # 5. Топ відправників (за останні 30 днів)
            top_senders = self._analyze_top_senders(service, received_results.get('messages', [])[:100])

            # 6. Середня кількість email на день
            avg_per_day = received_count / max(days, 1)

            return {
                'success': True,
                'period_days': days,
                'total_received': received_count,
                'total_sent': sent_count,
                'unread': unread_count,
                'starred': starred_count,
                'avg_per_day': round(avg_per_day, 1),
                'top_senders': top_senders,
                'email': integration.config.get('email', ''),
            }

        except Exception as e:
            print(f"Error getting Gmail analytics: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _analyze_top_senders(self, service, messages):
        """Проаналізувати топ відправників"""
        try:
            sender_counts = {}

            for msg in messages[:50]:  # Обмежити для швидкості
                try:
                    message = service.users().messages().get(
                        userId='me',
                        id=msg['id'],
                        format='metadata',
                        metadataHeaders=['From']
                    ).execute()

                    headers = message.get('payload', {}).get('headers', [])
                    for header in headers:
                        if header['name'] == 'From':
                            sender = header['value']
                            # Витягти email адресу
                            if '<' in sender and '>' in sender:
                                sender_email = sender.split('<')[1].split('>')[0]
                            else:
                                sender_email = sender

                            sender_counts[sender_email] = sender_counts.get(sender_email, 0) + 1
                            break

                except Exception as e:
                    continue

            # Сортувати по кількості
            sorted_senders = sorted(sender_counts.items(), key=lambda x: x[1], reverse=True)

            return [
                {'email': sender, 'count': count}
                for sender, count in sorted_senders[:5]
            ]

        except Exception as e:
            print(f"Error analyzing senders: {e}")
            return []

    def check_email_quota(self):
        """
        Перевірити квоту email для користувача

        Returns:
            dict: інформація про квоту
        """
        try:
            from apps.subscriptions.models import Subscription
            from apps.accounts.models import User

            user = User.objects.get(id=self.user_id)
            if not user.organization:
                return {'has_quota': False, 'reason': 'No organization'}

            subscription = user.organization.subscription

            # FREE план не має email
            if subscription.is_free_plan():
                return {
                    'has_quota': False,
                    'reason': 'Email integration requires paid subscription'
                }

            return {
                'has_quota': True,
                'plan': subscription.plan.name
            }

        except Exception as e:
            print(f"Error checking email quota: {e}")
            return {'has_quota': False, 'reason': str(e)}
