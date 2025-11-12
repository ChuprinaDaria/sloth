from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db import connection
from django.utils import timezone
from .push_service import PushNotificationService
import json


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def register_push_token(request):
    """Register or update Expo push token for user"""
    expo_push_token = request.data.get('expo_push_token')
    device_name = request.data.get('device_name', '')
    device_type = request.data.get('device_type', 'mobile')

    if not expo_push_token:
        return Response(
            {'error': 'expo_push_token is required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Validate Expo token format
    if not expo_push_token.startswith('ExponentPushToken['):
        return Response(
            {'error': 'Invalid Expo push token format'},
            status=status.HTTP_400_BAD_REQUEST
        )

    user_id = request.user.id
    tenant_schema = request.tenant.schema_name

    with connection.cursor() as cursor:
        cursor.execute(f"SET search_path TO {tenant_schema}")

        # Check if token already exists
        cursor.execute(
            "SELECT id FROM push_tokens WHERE expo_push_token = %s",
            [expo_push_token]
        )
        existing = cursor.fetchone()

        if existing:
            # Update existing token
            cursor.execute("""
                UPDATE push_tokens
                SET user_id = %s, device_name = %s, device_type = %s,
                    is_active = true, last_used_at = NOW(), updated_at = NOW()
                WHERE expo_push_token = %s
            """, [user_id, device_name, device_type, expo_push_token])
        else:
            # Create new token
            cursor.execute("""
                INSERT INTO push_tokens (
                    user_id, expo_push_token, device_name, device_type,
                    is_active, created_at, updated_at, last_used_at
                ) VALUES (%s, %s, %s, %s, true, NOW(), NOW(), NOW())
            """, [user_id, expo_push_token, device_name, device_type])

        connection.commit()

    return Response({
        'success': True,
        'message': 'Push token registered successfully'
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def unregister_push_token(request):
    """Unregister Expo push token"""
    expo_push_token = request.data.get('expo_push_token')

    if not expo_push_token:
        return Response(
            {'error': 'expo_push_token is required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    tenant_schema = request.tenant.schema_name

    with connection.cursor() as cursor:
        cursor.execute(f"SET search_path TO {tenant_schema}")
        cursor.execute(
            "UPDATE push_tokens SET is_active = false WHERE expo_push_token = %s",
            [expo_push_token]
        )
        connection.commit()

    return Response({
        'success': True,
        'message': 'Push token unregistered successfully'
    })


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def notification_settings(request):
    """Get or update user notification settings"""
    user_id = request.user.id
    tenant_schema = request.tenant.schema_name

    if request.method == 'GET':
        with connection.cursor() as cursor:
            cursor.execute(f"SET search_path TO {tenant_schema}")
            cursor.execute(
                "SELECT * FROM notification_settings WHERE user_id = %s",
                [user_id]
            )
            result = cursor.fetchone()

            if not result:
                # Create default settings
                cursor.execute("""
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
                    ) RETURNING *
                """, [user_id])
                result = cursor.fetchone()
                connection.commit()

            columns = [
                'id', 'user_id', 'enabled', 'frequency', 'quiet_hours_enabled',
                'quiet_hours_start', 'quiet_hours_end', 'critical_enabled',
                'important_enabled', 'useful_enabled', 'vip_messages',
                'integration_issues', 'negative_reviews', 'smart_analytics',
                'holidays_reminders', 'achievements', 'pending_conversations',
                'weekly_reports', 'pricing_recommendations', 'content_recommendations',
                'max_notifications_per_day', 'created_at', 'updated_at'
            ]

            settings_dict = dict(zip(columns, result))

            # Convert time fields to string
            settings_dict['quiet_hours_start'] = str(settings_dict['quiet_hours_start'])
            settings_dict['quiet_hours_end'] = str(settings_dict['quiet_hours_end'])
            settings_dict['created_at'] = settings_dict['created_at'].isoformat()
            settings_dict['updated_at'] = settings_dict['updated_at'].isoformat()

            return Response(settings_dict)

    elif request.method == 'PUT':
        # Update settings
        data = request.data

        allowed_fields = [
            'enabled', 'frequency', 'quiet_hours_enabled',
            'quiet_hours_start', 'quiet_hours_end', 'critical_enabled',
            'important_enabled', 'useful_enabled', 'vip_messages',
            'integration_issues', 'negative_reviews', 'smart_analytics',
            'holidays_reminders', 'achievements', 'pending_conversations',
            'weekly_reports', 'pricing_recommendations', 'content_recommendations',
            'max_notifications_per_day'
        ]

        update_fields = []
        update_values = []

        for field in allowed_fields:
            if field in data:
                update_fields.append(f"{field} = %s")
                update_values.append(data[field])

        if not update_fields:
            return Response(
                {'error': 'No fields to update'},
                status=status.HTTP_400_BAD_REQUEST
            )

        update_values.append(user_id)

        with connection.cursor() as cursor:
            cursor.execute(f"SET search_path TO {tenant_schema}")
            cursor.execute(f"""
                UPDATE notification_settings
                SET {', '.join(update_fields)}, updated_at = NOW()
                WHERE user_id = %s
            """, update_values)
            connection.commit()

        return Response({
            'success': True,
            'message': 'Settings updated successfully'
        })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def notification_history(request):
    """Get notification history for user"""
    user_id = request.user.id
    tenant_schema = request.tenant.schema_name

    limit = int(request.GET.get('limit', 50))
    offset = int(request.GET.get('offset', 0))

    with connection.cursor() as cursor:
        cursor.execute(f"SET search_path TO {tenant_schema}")
        cursor.execute("""
            SELECT notification_type, priority, title, body, status, sent_at
            FROM notification_logs
            WHERE user_id = %s
            ORDER BY sent_at DESC
            LIMIT %s OFFSET %s
        """, [user_id, limit, offset])

        results = cursor.fetchall()

        notifications = []
        for row in results:
            notifications.append({
                'notification_type': row[0],
                'priority': row[1],
                'title': row[2],
                'body': row[3],
                'status': row[4],
                'sent_at': row[5].isoformat(),
            })

        # Get total count
        cursor.execute(
            "SELECT COUNT(*) FROM notification_logs WHERE user_id = %s",
            [user_id]
        )
        total = cursor.fetchone()[0]

    return Response({
        'notifications': notifications,
        'total': total,
        'limit': limit,
        'offset': offset
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def test_notification(request):
    """Send a test notification to user"""
    user_id = request.user.id
    tenant_schema = request.tenant.schema_name

    service = PushNotificationService(tenant_schema)

    result = service.send_push_notification(
        user_id=user_id,
        title="Тестове повідомлення 🧪",
        body="Якщо ви бачите це - push-повідомлення працюють!",
        notification_type="test",
        priority="important",
        data={'test': True}
    )

    return Response(result)
