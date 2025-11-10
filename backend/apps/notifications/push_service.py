import requests
from django.utils import timezone
from django.db import connection
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class PushNotificationService:
    """Service for sending push notifications via Expo"""

    EXPO_PUSH_URL = "https://exp.host/--/api/v2/push/send"

    NOTIFICATION_PRIORITIES = {
        'critical': {
            'priority': 'high',
            'sound': 'default',
            'badge': 1,
        },
        'important': {
            'priority': 'default',
            'sound': 'default',
            'badge': 1,
        },
        'useful': {
            'priority': 'default',
            'sound': None,
            'badge': 0,
        },
    }

    def __init__(self, tenant_schema: str):
        self.tenant_schema = tenant_schema

    def _execute_query(self, query, params=None):
        """Execute query in tenant schema"""
        with connection.cursor() as cursor:
            cursor.execute(f"SET search_path TO {self.tenant_schema}")
            cursor.execute(query, params or [])
            return cursor.fetchall()

    def _execute_insert(self, query, params=None):
        """Execute insert query in tenant schema"""
        with connection.cursor() as cursor:
            cursor.execute(f"SET search_path TO {self.tenant_schema}")
            cursor.execute(query, params or [])
            connection.commit()

    def get_user_settings(self, user_id: int) -> Optional[Dict]:
        """Get user notification settings"""
        query = """
            SELECT * FROM notification_settings WHERE user_id = %s
        """
        results = self._execute_query(query, [user_id])

        if not results:
            # Create default settings
            self._create_default_settings(user_id)
            results = self._execute_query(query, [user_id])

        if results:
            columns = [
                'id', 'user_id', 'enabled', 'frequency', 'quiet_hours_enabled',
                'quiet_hours_start', 'quiet_hours_end', 'critical_enabled',
                'important_enabled', 'useful_enabled', 'vip_messages',
                'integration_issues', 'negative_reviews', 'smart_analytics',
                'holidays_reminders', 'achievements', 'pending_conversations',
                'weekly_reports', 'pricing_recommendations', 'content_recommendations',
                'max_notifications_per_day', 'created_at', 'updated_at'
            ]
            return dict(zip(columns, results[0]))
        return None

    def _create_default_settings(self, user_id: int):
        """Create default notification settings for user"""
        query = """
            INSERT INTO notification_settings (
                user_id, enabled, frequency, quiet_hours_enabled,
                quiet_hours_start, quiet_hours_end, critical_enabled,
                important_enabled, useful_enabled, vip_messages,
                integration_issues, negative_reviews, smart_analytics,
                holidays_reminders, achievements, pending_conversations,
                weekly_reports, pricing_recommendations, content_recommendations,
                max_notifications_per_day, created_at, updated_at
            ) VALUES (
                %s, true, 'all', true, '22:00', '08:00', true, true, true,
                true, true, true, true, true, true, true, true, true, true,
                3, NOW(), NOW()
            )
        """
        self._execute_insert(query, [user_id])

    def get_active_tokens(self, user_id: int) -> List[str]:
        """Get all active push tokens for user"""
        query = """
            SELECT expo_push_token FROM push_tokens
            WHERE user_id = %s AND is_active = true
        """
        results = self._execute_query(query, [user_id])
        return [row[0] for row in results]

    def check_rate_limit(self, user_id: int, priority: str) -> bool:
        """Check if user has exceeded daily notification limit"""
        # Critical notifications bypass rate limit
        if priority == 'critical':
            return True

        settings = self.get_user_settings(user_id)
        if not settings:
            return True

        max_per_day = settings['max_notifications_per_day']

        # Count non-critical notifications sent today
        query = """
            SELECT COUNT(*) FROM notification_logs
            WHERE user_id = %s
            AND priority != 'critical'
            AND status = 'sent'
            AND sent_at >= %s
        """
        today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        results = self._execute_query(query, [user_id, today_start])

        count = results[0][0] if results else 0
        return count < max_per_day

    def is_in_quiet_hours(self, settings: Dict) -> bool:
        """Check if current time is in quiet hours"""
        if not settings['quiet_hours_enabled']:
            return False

        now = timezone.localtime().time()
        start = settings['quiet_hours_start']
        end = settings['quiet_hours_end']

        # Handle overnight quiet hours (e.g., 22:00 - 08:00)
        if start > end:
            return now >= start or now < end
        else:
            return start <= now < end

    def should_send_notification(
        self,
        user_id: int,
        notification_type: str,
        priority: str
    ) -> tuple[bool, str]:
        """
        Determine if notification should be sent based on user settings
        Returns: (should_send, reason)
        """
        settings = self.get_user_settings(user_id)

        if not settings or not settings['enabled']:
            return False, "Notifications disabled"

        # Check frequency setting
        frequency = settings['frequency']
        if frequency == 'none':
            return False, "User disabled all notifications"
        elif frequency == 'critical' and priority != 'critical':
            return False, f"User only wants critical notifications"
        elif frequency == 'important' and priority == 'useful':
            return False, f"User only wants important+ notifications"

        # Check priority-specific settings
        if priority == 'critical' and not settings['critical_enabled']:
            return False, "Critical notifications disabled"
        elif priority == 'important' and not settings['important_enabled']:
            return False, "Important notifications disabled"
        elif priority == 'useful' and not settings['useful_enabled']:
            return False, "Useful notifications disabled"

        # Check specific notification type
        type_setting_map = {
            'vip_message': 'vip_messages',
            'integration_issue': 'integration_issues',
            'negative_review': 'negative_reviews',
            'smart_analytics': 'smart_analytics',
            'holiday_reminder': 'holidays_reminders',
            'achievement': 'achievements',
            'pending_conversations': 'pending_conversations',
            'weekly_report': 'weekly_reports',
            'pricing_recommendation': 'pricing_recommendations',
            'content_recommendation': 'content_recommendations',
        }

        setting_key = type_setting_map.get(notification_type)
        if setting_key and not settings.get(setting_key, True):
            return False, f"{notification_type} notifications disabled"

        # Check quiet hours (only for non-critical)
        if priority != 'critical' and self.is_in_quiet_hours(settings):
            return False, "In quiet hours"

        # Check rate limit (only for non-critical)
        if not self.check_rate_limit(user_id, priority):
            return False, "Daily rate limit exceeded"

        return True, "OK"

    def send_push_notification(
        self,
        user_id: int,
        title: str,
        body: str,
        notification_type: str,
        priority: str = 'important',
        data: Optional[Dict] = None
    ) -> Dict:
        """
        Send push notification to user

        Args:
            user_id: User ID
            title: Notification title
            body: Notification body
            notification_type: Type of notification (vip_message, negative_review, etc.)
            priority: critical, important, or useful
            data: Additional data to send with notification

        Returns:
            Dict with status and details
        """
        # Check if should send
        should_send, reason = self.should_send_notification(user_id, notification_type, priority)

        if not should_send:
            # Log as skipped
            self._log_notification(
                user_id, notification_type, priority, title, body,
                data or {}, 'skipped', reason
            )
            return {
                'success': False,
                'reason': reason,
                'status': 'skipped'
            }

        # Get push tokens
        tokens = self.get_active_tokens(user_id)

        if not tokens:
            self._log_notification(
                user_id, notification_type, priority, title, body,
                data or {}, 'failed', 'No active push tokens'
            )
            return {
                'success': False,
                'reason': 'No active push tokens',
                'status': 'failed'
            }

        # Prepare notification payload
        priority_config = self.NOTIFICATION_PRIORITIES.get(priority, self.NOTIFICATION_PRIORITIES['important'])

        messages = []
        for token in tokens:
            message = {
                'to': token,
                'title': title,
                'body': body,
                'data': data or {},
                'priority': priority_config['priority'],
                'channelId': priority,
            }

            if priority_config['sound']:
                message['sound'] = priority_config['sound']

            if priority_config['badge']:
                message['badge'] = priority_config['badge']

            messages.append(message)

        # Send to Expo
        try:
            response = requests.post(
                self.EXPO_PUSH_URL,
                json=messages,
                headers={
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                }
            )

            response.raise_for_status()
            expo_response = response.json()

            # Log notification
            self._log_notification(
                user_id, notification_type, priority, title, body,
                data or {}, 'sent', '', expo_response
            )

            return {
                'success': True,
                'status': 'sent',
                'expo_response': expo_response
            }

        except requests.RequestException as e:
            error_msg = str(e)
            logger.error(f"Failed to send push notification: {error_msg}")

            self._log_notification(
                user_id, notification_type, priority, title, body,
                data or {}, 'failed', error_msg
            )

            return {
                'success': False,
                'reason': error_msg,
                'status': 'failed'
            }

    def _log_notification(
        self,
        user_id: int,
        notification_type: str,
        priority: str,
        title: str,
        body: str,
        data: Dict,
        status: str,
        error_message: str = '',
        expo_response: Dict = None
    ):
        """Log notification to database"""
        query = """
            INSERT INTO notification_logs (
                user_id, notification_type, priority, title, body, data,
                status, error_message, expo_response, sent_at, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
        """

        import json
        self._execute_insert(query, [
            user_id, notification_type, priority, title, body,
            json.dumps(data), status, error_message,
            json.dumps(expo_response or {})
        ])

    def send_bulk_notifications(self, notifications: List[Dict]) -> Dict:
        """
        Send multiple notifications at once

        Args:
            notifications: List of notification dicts with keys:
                - user_id, title, body, notification_type, priority, data

        Returns:
            Summary of sent/failed/skipped notifications
        """
        results = {
            'sent': 0,
            'failed': 0,
            'skipped': 0,
            'details': []
        }

        for notif in notifications:
            result = self.send_push_notification(
                user_id=notif['user_id'],
                title=notif['title'],
                body=notif['body'],
                notification_type=notif['notification_type'],
                priority=notif.get('priority', 'important'),
                data=notif.get('data')
            )

            results[result['status']] += 1
            results['details'].append(result)

        return results
