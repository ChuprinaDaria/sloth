"""
Notification triggers - functions to send notifications on specific events
"""

from .push_service import PushNotificationService
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class NotificationTriggers:
    """Triggers for sending push notifications on various events"""

    def __init__(self, tenant_schema: str):
        self.service = PushNotificationService(tenant_schema)

    # CRITICAL NOTIFICATIONS

    def notify_vip_message(self, user_id: int, client_name: str, message_preview: str, conversation_id: int):
        """VIP client sent a message"""
        return self.service.send_push_notification(
            user_id=user_id,
            title=f"💎 VIP клієнт {client_name}",
            body=message_preview[:100],
            notification_type='vip_message',
            priority='critical',
            data={
                'conversation_id': conversation_id,
                'client_name': client_name,
                'action': 'open_conversation'
            }
        )

    def notify_integration_failure(self, user_id: int, integration_name: str, error_message: str):
        """Integration stopped working"""
        return self.service.send_push_notification(
            user_id=user_id,
            title=f"⚠️ {integration_name} відключився",
            body=f"Клієнти не отримують відповіді. {error_message}",
            notification_type='integration_issue',
            priority='critical',
            data={
                'integration_name': integration_name,
                'action': 'open_integrations'
            }
        )

    def notify_negative_review(self, user_id: int, reviewer_name: str, rating: int, review_text: str):
        """Negative review received"""
        stars = '⭐' * rating
        return self.service.send_push_notification(
            user_id=user_id,
            title=f"⚠️ Новий {rating}-зірковий відгук",
            body=f"{reviewer_name}: {review_text[:80]}...",
            notification_type='negative_review',
            priority='critical',
            data={
                'reviewer_name': reviewer_name,
                'rating': rating,
                'action': 'open_reviews'
            }
        )

    # IMPORTANT NOTIFICATIONS

    def notify_smart_analytics(self, user_id: int, insight_title: str, insight_message: str, insight_data: dict):
        """Important business insight from AI"""
        return self.service.send_push_notification(
            user_id=user_id,
            title=f"📊 {insight_title}",
            body=insight_message,
            notification_type='smart_analytics',
            priority='important',
            data={
                'insight_data': insight_data,
                'action': 'open_analytics'
            }
        )

    def notify_holiday_reminder(self, user_id: int, holiday_name: str, expected_increase: int, date: str):
        """Upcoming holiday with expected traffic"""
        return self.service.send_push_notification(
            user_id=user_id,
            title=f"📅 {date}: {holiday_name}",
            body=f"Очікується +{expected_increase}% запитів. Підготуйтесь!",
            notification_type='holiday_reminder',
            priority='important',
            data={
                'holiday_name': holiday_name,
                'date': date,
                'expected_increase': expected_increase,
                'action': 'open_analytics'
            }
        )

    def notify_achievement(self, user_id: int, achievement_title: str, achievement_description: str):
        """User reached a milestone"""
        return self.service.send_push_notification(
            user_id=user_id,
            title=f"🎉 {achievement_title}",
            body=achievement_description,
            notification_type='achievement',
            priority='important',
            data={
                'action': 'open_profile'
            }
        )

    def notify_pending_conversations(self, user_id: int, count: int, oldest_hours: int):
        """Conversations waiting for response"""
        return self.service.send_push_notification(
            user_id=user_id,
            title=f"🔔 {count} клієнтів очікують",
            body=f"Найдавніша розмова: {oldest_hours} год тому",
            notification_type='pending_conversations',
            priority='important',
            data={
                'count': count,
                'oldest_hours': oldest_hours,
                'action': 'open_conversations'
            }
        )

    # USEFUL NOTIFICATIONS

    def notify_weekly_report(
        self,
        user_id: int,
        total_clients: int,
        avg_rating: float,
        top_question: str,
        growth_percent: int
    ):
        """Weekly summary report"""
        return self.service.send_push_notification(
            user_id=user_id,
            title="📈 Тижневий звіт",
            body=f"{total_clients} клієнтів, рейтинг {avg_rating:.1f}⭐, {growth_percent:+d}% зростання",
            notification_type='weekly_report',
            priority='useful',
            data={
                'total_clients': total_clients,
                'avg_rating': avg_rating,
                'top_question': top_question,
                'growth_percent': growth_percent,
                'action': 'open_analytics'
            }
        )

    def notify_pricing_recommendation(
        self,
        user_id: int,
        service_name: str,
        current_price: int,
        recommended_price: int,
        potential_increase: int
    ):
        """Pricing optimization suggestion"""
        return self.service.send_push_notification(
            user_id=user_id,
            title="💰 Рекомендація по цінам",
            body=f"{service_name}: можна збільшити до {recommended_price} грн (+{potential_increase}% до доходу)",
            notification_type='pricing_recommendation',
            priority='useful',
            data={
                'service_name': service_name,
                'current_price': current_price,
                'recommended_price': recommended_price,
                'action': 'open_analytics'
            }
        )

    def notify_content_recommendation(
        self,
        user_id: int,
        topic: str,
        reason: str,
        priority_level: str
    ):
        """Content gap analysis recommendation"""
        emoji = '🔴' if priority_level == 'high' else '🟡' if priority_level == 'medium' else '🟢'
        return self.service.send_push_notification(
            user_id=user_id,
            title=f"{emoji} Ідея для контенту",
            body=f"Тема: {topic}. {reason}",
            notification_type='content_recommendation',
            priority='useful',
            data={
                'topic': topic,
                'reason': reason,
                'priority_level': priority_level,
                'action': 'open_instagram'
            }
        )

    # BATCH NOTIFICATIONS

    def send_daily_digest(self, user_id: int, digest_data: dict):
        """Send daily digest if there are multiple pending notifications"""
        insights_count = digest_data.get('insights_count', 0)
        pending_count = digest_data.get('pending_conversations', 0)
        new_reviews = digest_data.get('new_reviews', 0)

        summary_parts = []
        if insights_count:
            summary_parts.append(f"{insights_count} нових інсайтів")
        if pending_count:
            summary_parts.append(f"{pending_count} клієнтів очікують")
        if new_reviews:
            summary_parts.append(f"{new_reviews} нових відгуків")

        body = "• " + "\n• ".join(summary_parts) if summary_parts else "Все спокійно 😊"

        return self.service.send_push_notification(
            user_id=user_id,
            title="📋 Підсумок дня",
            body=body,
            notification_type='daily_digest',
            priority='useful',
            data={
                'digest_data': digest_data,
                'action': 'open_home'
            }
        )


# Helper functions for easy integration

def notify_vip_message(tenant_schema: str, user_id: int, client_name: str, message: str, conversation_id: int):
    """Quick function to send VIP message notification"""
    triggers = NotificationTriggers(tenant_schema)
    return triggers.notify_vip_message(user_id, client_name, message, conversation_id)


def notify_integration_failure(tenant_schema: str, user_id: int, integration: str, error: str):
    """Quick function to send integration failure notification"""
    triggers = NotificationTriggers(tenant_schema)
    return triggers.notify_integration_failure(user_id, integration, error)


def notify_negative_review(tenant_schema: str, user_id: int, reviewer: str, rating: int, text: str):
    """Quick function to send negative review notification"""
    triggers = NotificationTriggers(tenant_schema)
    return triggers.notify_negative_review(user_id, reviewer, rating, text)
