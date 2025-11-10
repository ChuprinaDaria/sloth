"""
Google Reviews Integration - Google My Business API
"""
import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from django.conf import settings
from datetime import datetime, timedelta
import openai
import json


class GoogleReviewsService:
    """
    Сервіс для роботи з Google Reviews (Google My Business API)
    - Отримання відгуків про бізнес
    - Аналіз позитивних моментів та скарг
    - Створення контексту для AI для роботи з запереченнями
    """

    def __init__(self, user_id, tenant_schema):
        self.user_id = user_id
        self.tenant_schema = tenant_schema
        self.openai_client = openai

    def get_integration_settings(self):
        """Get Google My Business integration settings"""
        from .models import Integration

        try:
            integration = Integration.objects.filter(
                user_id=self.user_id,
                integration_type='google_my_business',
                status='active'
            ).first()

            return integration
        except Exception as e:
            print(f"Error getting Google My Business integration: {e}")
            return None

    def get_reviews(self, limit=100, min_rating=None):
        """
        Отримати відгуки з Google My Business

        Args:
            limit: максимальна кількість відгуків
            min_rating: мінімальний рейтинг (1-5)

        Returns:
            dict: список відгуків
        """
        try:
            # Check Google OAuth env is configured to avoid invalid_request client_id errors
            if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
                return {
                    'success': False,
                    'error': 'Google OAuth is not configured on the server. '
                             'Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET.'
                }

            integration = self.get_integration_settings()
            if not integration:
                return {'success': False, 'error': 'Google My Business not connected'}

            # Get credentials from encrypted storage
            credentials = integration.get_credentials()
            if not credentials.get('access_token'):
                return {'success': False, 'error': 'Google My Business not connected'}

            # Create credentials
            creds = Credentials(
                token=credentials['access_token'],
                refresh_token=credentials.get('refresh_token'),
                token_uri='https://oauth2.googleapis.com/token',
                client_id=settings.GOOGLE_CLIENT_ID,
                client_secret=settings.GOOGLE_CLIENT_SECRET
            )

            # Build My Business service
            service = build('mybusinessaccountmanagement', 'v1', credentials=creds)

            # Get location/account from config
            location_name = integration.config.get('location_name', '')
            if not location_name:
                return {'success': False, 'error': 'Location not configured'}

            # Get reviews
            reviews_service = build('mybusiness', 'v4', credentials=creds)
            reviews_response = reviews_service.accounts().locations().reviews().list(
                parent=location_name,
                pageSize=min(limit, 100)
            ).execute()

            reviews_data = reviews_response.get('reviews', [])

            # Filter by rating if specified
            if min_rating:
                reviews_data = [r for r in reviews_data if r.get('starRating', 0) >= min_rating]

            # Format reviews
            formatted_reviews = []
            for review in reviews_data:
                formatted_reviews.append({
                    'review_id': review.get('reviewId', ''),
                    'reviewer_name': review.get('reviewer', {}).get('displayName', 'Anonymous'),
                    'rating': review.get('starRating', 0),
                    'comment': review.get('comment', ''),
                    'reply': review.get('reviewReply', {}).get('comment', ''),
                    'create_time': review.get('createTime', ''),
                    'update_time': review.get('updateTime', ''),
                })

            return {
                'success': True,
                'reviews': formatted_reviews,
                'total_count': len(formatted_reviews)
            }

        except Exception as e:
            print(f"Error getting Google reviews: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def analyze_reviews_for_ai(self):
        """
        Проаналізувати відгуки для створення контексту для AI

        Returns:
            dict: аналіз відгуків для AI
        """
        try:
            # Get recent reviews (last 100)
            reviews_result = self.get_reviews(limit=100)

            if not reviews_result.get('success'):
                return {
                    'success': False,
                    'error': reviews_result.get('error', 'Unknown error')
                }

            reviews = reviews_result.get('reviews', [])

            if not reviews:
                return {
                    'success': True,
                    'strengths': [],
                    'weaknesses': [],
                    'common_complaints': [],
                    'common_praises': [],
                    'average_rating': 0,
                    'total_reviews': 0,
                }

            # Separate by rating
            positive_reviews = [r for r in reviews if r['rating'] >= 4]
            negative_reviews = [r for r in reviews if r['rating'] <= 2]
            neutral_reviews = [r for r in reviews if r['rating'] == 3]

            # Calculate average rating
            avg_rating = sum(r['rating'] for r in reviews) / len(reviews) if reviews else 0

            # Use AI to analyze patterns
            analysis = self._ai_analyze_reviews(positive_reviews, negative_reviews)

            return {
                'success': True,
                'strengths': analysis.get('strengths', []),
                'weaknesses': analysis.get('weaknesses', []),
                'common_complaints': analysis.get('common_complaints', []),
                'common_praises': analysis.get('common_praises', []),
                'average_rating': round(avg_rating, 1),
                'total_reviews': len(reviews),
                'positive_count': len(positive_reviews),
                'negative_count': len(negative_reviews),
                'neutral_count': len(neutral_reviews),
                'objection_handling_tips': analysis.get('objection_handling_tips', [])
            }

        except Exception as e:
            print(f"Error analyzing reviews: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _ai_analyze_reviews(self, positive_reviews, negative_reviews):
        """
        Використати AI для аналізу відгуків

        Args:
            positive_reviews: список позитивних відгуків
            negative_reviews: список негативних відгуків

        Returns:
            dict: аналіз від AI
        """
        try:
            # Prepare review texts
            positive_texts = [r['comment'] for r in positive_reviews[:30] if r.get('comment')]
            negative_texts = [r['comment'] for r in negative_reviews[:30] if r.get('comment')]

            prompt = f"""
Проаналізуй відгуки про бізнес та надай структуровану інформацію.

Позитивні відгуки ({len(positive_texts)}):
{chr(10).join(f"- {text[:200]}" for text in positive_texts[:15])}

Негативні відгуки ({len(negative_texts)}):
{chr(10).join(f"- {text[:200]}" for text in negative_texts[:15])}

Надай аналіз у JSON форматі:
{{
  "strengths": ["ТОП 5 сильних сторін бізнесу з позитивних відгуків"],
  "common_praises": ["3-5 найчастіших похвал від клієнтів"],
  "weaknesses": ["ТОП 3-5 слабких сторін з негативних відгуків"],
  "common_complaints": ["3-5 найчастіших скарг"],
  "objection_handling_tips": [
    {{
      "objection": "Типове заперечення клієнта",
      "response": "Як AI асистент може відповісти, використовуючи позитивні відгуки"
    }}
  ]
}}

Будь конкретним. Використовуй реальні слова з відгуків.
Для objection_handling_tips - створи 5-7 прикладів на основі реальних скарг та позитивних відгуків.
"""

            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Ти аналітик відгуків. Аналізуй відгуки та надавай структуровані інсайти."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )

            result = json.loads(response.choices[0].message.content)
            return result

        except Exception as e:
            print(f"Error in AI review analysis: {e}")
            return {
                'strengths': [],
                'weaknesses': [],
                'common_complaints': [],
                'common_praises': [],
                'objection_handling_tips': []
            }

    def get_context_for_ai_agent(self):
        """
        Отримати контекст з відгуків для AI агента

        Returns:
            str: форматований контекст для додавання до промпту
        """
        try:
            analysis = self.analyze_reviews_for_ai()

            if not analysis.get('success'):
                return ""

            # Format context for AI
            context_parts = []

            context_parts.append("📊 ІНФОРМАЦІЯ З GOOGLE ВІДГУКІВ:")
            context_parts.append(f"Середній рейтинг: {analysis['average_rating']}/5 ({analysis['total_reviews']} відгуків)")

            if analysis.get('strengths'):
                context_parts.append(f"\n✅ СИЛЬНІ СТОРОНИ (використовуй це при роботі з клієнтами):")
                for strength in analysis['strengths']:
                    context_parts.append(f"  • {strength}")

            if analysis.get('common_praises'):
                context_parts.append(f"\n💬 ЩО НАЙБІЛЬШЕ ХВАЛЯТЬ КЛІЄНТИ:")
                for praise in analysis['common_praises']:
                    context_parts.append(f"  • {praise}")

            if analysis.get('weaknesses'):
                context_parts.append(f"\n⚠️ СЛАБКІ СТОРОНИ (будь готова до таких запитань):")
                for weakness in analysis['weaknesses']:
                    context_parts.append(f"  • {weakness}")

            if analysis.get('objection_handling_tips'):
                context_parts.append(f"\n🎯 РОБОТА З ЗАПЕРЕЧЕННЯМИ:")
                for tip in analysis['objection_handling_tips'][:5]:
                    context_parts.append(f"  • Заперечення: {tip.get('objection', '')}")
                    context_parts.append(f"    Відповідь: {tip.get('response', '')}")

            return "\n".join(context_parts)

        except Exception as e:
            print(f"Error getting context for AI: {e}")
            return ""

    def get_reviews_summary(self):
        """
        Отримати короткий саммарі відгуків для Smart Analytics

        Returns:
            dict: саммарі для аналітики
        """
        try:
            analysis = self.analyze_reviews_for_ai()

            if not analysis.get('success'):
                return {'enabled': False, 'error': analysis.get('error', 'Not configured')}

            return {
                'enabled': True,
                'average_rating': analysis.get('average_rating', 0),
                'total_reviews': analysis.get('total_reviews', 0),
                'positive_count': analysis.get('positive_count', 0),
                'negative_count': analysis.get('negative_count', 0),
                'top_strengths': analysis.get('strengths', [])[:3],
                'top_weaknesses': analysis.get('weaknesses', [])[:3],
                'common_praises': analysis.get('common_praises', [])[:3],
                'common_complaints': analysis.get('common_complaints', [])[:3],
            }

        except Exception as e:
            print(f"Error getting reviews summary: {e}")
            return {'enabled': False, 'error': str(e)}
