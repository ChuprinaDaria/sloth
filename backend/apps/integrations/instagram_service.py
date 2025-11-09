"""
Instagram Integration - Instagram Graph API
"""
import os
import requests
from django.conf import settings
from django.utils import timezone
from datetime import datetime, timedelta
import openai
import json
from collections import Counter


class InstagramService:
    """
    Сервіс для роботи з Instagram Graph API
    - Отримання постів з бізнес акаунту
    - Створення embeddings для RAG (тільки для Enterprise тарифу)
    - Повна аналітика (для Enterprise тарифу)
    - Рекомендації для контент-плану
    """

    def __init__(self, user_id, tenant_schema):
        self.user_id = user_id
        self.tenant_schema = tenant_schema
        self.openai_client = openai

    def get_integration_settings(self):
        """Get Instagram integration settings"""
        from .models import Integration

        try:
            integration = Integration.objects.filter(
                user_id=self.user_id,
                integration_type='instagram',
                status='active'
            ).first()

            return integration
        except Exception as e:
            print(f"Error getting Instagram integration: {e}")
            return None

    def check_enterprise_plan(self):
        """Check if user has Enterprise plan for advanced features"""
        try:
            from apps.subscriptions.models import Subscription
            from apps.accounts.models import User

            user = User.objects.get(id=self.user_id)
            if not user.organization:
                return False

            subscription = user.organization.subscription

            # Check if plan has 'instagram_embeddings' feature
            return subscription.has_feature('instagram_embeddings')

        except Exception as e:
            print(f"Error checking Enterprise plan: {e}")
            return False

    def get_posts(self, limit=50):
        """
        Отримати пости з Instagram

        Args:
            limit: кількість постів (макс 100)

        Returns:
            dict: список постів
        """
        try:
            integration = self.get_integration_settings()
            if not integration:
                return {'success': False, 'error': 'Instagram not connected'}

            # Get access token from config
            access_token = integration.config.get('access_token', '')
            instagram_account_id = integration.config.get('instagram_account_id', '')

            if not access_token or not instagram_account_id:
                return {'success': False, 'error': 'Instagram not configured'}

            # Instagram Graph API endpoint
            url = f"https://graph.instagram.com/{instagram_account_id}/media"

            params = {
                'fields': 'id,caption,media_type,media_url,permalink,timestamp,like_count,comments_count,insights.metric(engagement,impressions,reach)',
                'access_token': access_token,
                'limit': min(limit, 100)
            }

            response = requests.get(url, params=params)

            if response.status_code != 200:
                return {
                    'success': False,
                    'error': f'Instagram API error: {response.status_code}'
                }

            data = response.json()
            posts = data.get('data', [])

            # Format posts
            formatted_posts = []
            for post in posts:
                formatted_posts.append({
                    'post_id': post.get('id', ''),
                    'caption': post.get('caption', ''),
                    'media_type': post.get('media_type', ''),
                    'media_url': post.get('media_url', ''),
                    'permalink': post.get('permalink', ''),
                    'timestamp': post.get('timestamp', ''),
                    'likes': post.get('like_count', 0),
                    'comments': post.get('comments_count', 0),
                    'engagement': self._get_insight_value(post.get('insights', {}), 'engagement'),
                    'impressions': self._get_insight_value(post.get('insights', {}), 'impressions'),
                    'reach': self._get_insight_value(post.get('insights', {}), 'reach'),
                })

            return {
                'success': True,
                'posts': formatted_posts,
                'total_count': len(formatted_posts)
            }

        except Exception as e:
            print(f"Error getting Instagram posts: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _get_insight_value(self, insights, metric_name):
        """Helper to extract insight value"""
        if not insights or 'data' not in insights:
            return 0

        for insight in insights['data']:
            if insight.get('name') == metric_name:
                return insight.get('values', [{}])[0].get('value', 0)

        return 0

    def create_embeddings_from_posts(self):
        """
        Створити embeddings з постів Instagram для RAG
        Тільки для Enterprise тарифу!

        Returns:
            dict: результат створення embeddings
        """
        try:
            # Check if user has Enterprise plan
            if not self.check_enterprise_plan():
                return {
                    'success': False,
                    'error': 'Instagram embeddings available only for Enterprise plan'
                }

            # Get recent posts
            posts_result = self.get_posts(limit=50)

            if not posts_result.get('success'):
                return posts_result

            posts = posts_result.get('posts', [])

            if not posts:
                return {
                    'success': True,
                    'message': 'No posts to process',
                    'embeddings_created': 0
                }

            # Create or update InstagramPost records with embeddings
            from .models import InstagramPost

            embeddings_created = 0

            for post in posts:
                # Check if post already exists
                existing_post = InstagramPost.objects.filter(
                    user_id=self.user_id,
                    post_id=post['post_id']
                ).first()

                if existing_post:
                    # Skip if already has embedding
                    if existing_post.embedding:
                        continue

                # Create embedding from caption
                caption = post.get('caption', '')
                if not caption:
                    continue

                # Use OpenAI embeddings
                embedding_response = openai.embeddings.create(
                    model="text-embedding-3-small",
                    input=caption
                )

                embedding_vector = embedding_response.data[0].embedding

                # Extract hashtags
                hashtags = [word[1:] for word in caption.split() if word.startswith('#')]

                # Create or update post
                if existing_post:
                    existing_post.embedding = embedding_vector
                    existing_post.hashtags = hashtags
                    existing_post.likes = post.get('likes', 0)
                    existing_post.comments = post.get('comments', 0)
                    existing_post.save()
                else:
                    InstagramPost.objects.create(
                        user_id=self.user_id,
                        post_id=post['post_id'],
                        caption=caption,
                        media_type=post.get('media_type', ''),
                        media_url=post.get('media_url', ''),
                        permalink=post.get('permalink', ''),
                        posted_at=datetime.fromisoformat(post['timestamp'].replace('Z', '+00:00')),
                        likes=post.get('likes', 0),
                        comments=post.get('comments', 0),
                        engagement=post.get('engagement', 0),
                        impressions=post.get('impressions', 0),
                        reach=post.get('reach', 0),
                        hashtags=hashtags,
                        embedding=embedding_vector
                    )

                embeddings_created += 1

            return {
                'success': True,
                'embeddings_created': embeddings_created,
                'total_posts': len(posts)
            }

        except Exception as e:
            print(f"Error creating embeddings: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def analyze_content_vs_client_questions(self):
        """
        Порівняти контент Instagram з питаннями клієнтів у чаті
        Генерує рекомендації для контент-плану

        Returns:
            dict: рекомендації для контенту
        """
        try:
            # Get posts
            posts_result = self.get_posts(limit=50)

            if not posts_result.get('success'):
                return {
                    'success': False,
                    'error': posts_result.get('error', 'Unknown error')
                }

            posts = posts_result.get('posts', [])

            # Analyze post topics
            post_topics = self._extract_topics_from_posts(posts)

            # Get client questions from conversations
            from apps.agent.models import Message, Conversation

            # Get recent client messages
            recent_conversations = Conversation.objects.filter(
                user_id=self.user_id,
                created_at__gte=timezone.now() - timedelta(days=30)
            )

            client_messages = Message.objects.filter(
                conversation__in=recent_conversations,
                role='user'
            )[:200]

            # Analyze client questions
            client_topics = self._extract_topics_from_messages(client_messages)

            # Compare and generate recommendations
            recommendations = self._generate_content_recommendations(post_topics, client_topics, posts)

            return {
                'success': True,
                'post_topics': post_topics,
                'client_topics': client_topics,
                'recommendations': recommendations
            }

        except Exception as e:
            print(f"Error analyzing content vs questions: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _extract_topics_from_posts(self, posts):
        """Extract topics from Instagram posts"""
        all_captions = " ".join([p.get('caption', '') for p in posts])

        # Extract hashtags
        hashtags = []
        for post in posts:
            caption = post.get('caption', '')
            post_hashtags = [word[1:].lower() for word in caption.split() if word.startswith('#')]
            hashtags.extend(post_hashtags)

        # Count hashtag frequency
        hashtag_counts = Counter(hashtags)

        # Use AI to extract themes
        try:
            prompt = f"""
Проаналізуй підписи до постів Instagram та визнач основні теми/послуги.

Підписи постів (фрагменти):
{all_captions[:2000]}

Надай список у JSON:
{{
  "topics": [
    {{"topic": "Назва теми/послуги", "frequency": процент_від_загального_контенту}}
  ]
}}

Визнач 5-10 основних тем.
"""

            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Ти аналітик контенту Instagram."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )

            result = json.loads(response.choices[0].message.content)
            topics = result.get('topics', [])

        except Exception as e:
            print(f"Error extracting topics: {e}")
            topics = []

        return {
            'topics': topics,
            'top_hashtags': [{'hashtag': tag, 'count': count} for tag, count in hashtag_counts.most_common(10)]
        }

    def _extract_topics_from_messages(self, messages):
        """Extract topics from client messages"""
        all_messages = " ".join([m.content for m in messages if m.content])

        try:
            prompt = f"""
Проаналізуй повідомлення клієнтів та визнач про які послуги/теми вони найчастіше питають.

Повідомлення клієнтів (фрагменти):
{all_messages[:3000]}

Надай список у JSON:
{{
  "topics": [
    {{"topic": "Назва послуги/теми", "frequency": процент_запитів}}
  ]
}}

Визнач 5-10 найпопулярніших тем.
"""

            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Ти аналітик клієнтських запитів."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )

            result = json.loads(response.choices[0].message.content)
            return result.get('topics', [])

        except Exception as e:
            print(f"Error extracting client topics: {e}")
            return []

    def _generate_content_recommendations(self, post_topics, client_topics, posts):
        """Generate content recommendations based on gap analysis"""
        try:
            prompt = f"""
Порівняй теми в Instagram постах з темами про які питають клієнти.
Надай конкретні рекомендації для контент-плану.

Теми в Instagram постах:
{json.dumps(post_topics, ensure_ascii=False)}

Теми запитів клієнтів:
{json.dumps(client_topics, ensure_ascii=False)}

Надай рекомендації у JSON:
{{
  "recommendations": [
    {{
      "type": "missing_content|underrepresented|overrepresented|well_balanced",
      "topic": "Назва теми/послуги",
      "current_coverage": "процент в Instagram",
      "client_interest": "процент запитів",
      "recommendation": "Конкретна рекомендація що робити",
      "priority": "high|medium|low"
    }}
  ]
}}

Створи 7-10 найважливіших рекомендацій.
"""

            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Ти SMM експерт, який аналізує контент план."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                response_format={"type": "json_object"}
            )

            result = json.loads(response.choices[0].message.content)
            return result.get('recommendations', [])

        except Exception as e:
            print(f"Error generating recommendations: {e}")
            return []

    def get_full_analytics(self, period='month'):
        """
        Повна аналітика Instagram (тільки для Enterprise тарифу)

        Args:
            period: 'week', 'month', 'year'

        Returns:
            dict: детальна аналітика
        """
        try:
            # Check if user has Enterprise plan
            if not self.check_enterprise_plan():
                return {
                    'success': False,
                    'error': 'Full Instagram analytics available only for Enterprise plan'
                }

            # Determine time range
            if period == 'week':
                days = 7
            elif period == 'month':
                days = 30
            else:  # year
                days = 365

            # Get posts for period
            posts_result = self.get_posts(limit=100)

            if not posts_result.get('success'):
                return posts_result

            all_posts = posts_result.get('posts', [])

            # Filter by period
            cutoff_date = timezone.now() - timedelta(days=days)
            posts = [
                p for p in all_posts
                if datetime.fromisoformat(p['timestamp'].replace('Z', '+00:00')) >= cutoff_date
            ]

            if not posts:
                return {
                    'success': True,
                    'analytics': {},
                    'message': f'No posts in the last {period}'
                }

            # Calculate analytics
            analytics = self._calculate_analytics(posts, period)

            return {
                'success': True,
                'period': period,
                'analytics': analytics
            }

        except Exception as e:
            print(f"Error getting full analytics: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _calculate_analytics(self, posts, period):
        """Calculate detailed analytics from posts"""
        total_posts = len(posts)
        total_likes = sum(p.get('likes', 0) for p in posts)
        total_comments = sum(p.get('comments', 0) for p in posts)
        total_engagement = sum(p.get('engagement', 0) for p in posts)
        total_impressions = sum(p.get('impressions', 0) for p in posts)
        total_reach = sum(p.get('reach', 0) for p in posts)

        # Average metrics
        avg_likes = total_likes / total_posts if total_posts > 0 else 0
        avg_comments = total_comments / total_posts if total_posts > 0 else 0
        avg_engagement = total_engagement / total_posts if total_posts > 0 else 0

        # Engagement rate
        engagement_rate = (total_engagement / total_impressions * 100) if total_impressions > 0 else 0

        # Best performing posts
        best_posts = sorted(posts, key=lambda x: x.get('engagement', 0), reverse=True)[:5]

        # Extract hashtags
        all_hashtags = []
        for post in posts:
            caption = post.get('caption', '')
            hashtags = [word[1:].lower() for word in caption.split() if word.startswith('#')]
            all_hashtags.extend(hashtags)

        hashtag_counts = Counter(all_hashtags)
        top_hashtags = [
            {'hashtag': tag, 'count': count}
            for tag, count in hashtag_counts.most_common(10)
        ]

        # Post frequency by day of week
        posts_by_day = {}
        for post in posts:
            timestamp = datetime.fromisoformat(post['timestamp'].replace('Z', '+00:00'))
            day_name = timestamp.strftime('%A')
            posts_by_day[day_name] = posts_by_day.get(day_name, 0) + 1

        # Best time to post (based on engagement)
        posts_by_hour = {}
        engagement_by_hour = {}
        for post in posts:
            timestamp = datetime.fromisoformat(post['timestamp'].replace('Z', '+00:00'))
            hour = timestamp.hour
            posts_by_hour[hour] = posts_by_hour.get(hour, 0) + 1
            engagement_by_hour[hour] = engagement_by_hour.get(hour, 0) + post.get('engagement', 0)

        # Calculate average engagement per hour
        avg_engagement_by_hour = {
            hour: engagement_by_hour.get(hour, 0) / posts_by_hour.get(hour, 1)
            for hour in engagement_by_hour.keys()
        }

        best_hours = sorted(avg_engagement_by_hour.items(), key=lambda x: x[1], reverse=True)[:3]

        return {
            'overview': {
                'total_posts': total_posts,
                'total_likes': total_likes,
                'total_comments': total_comments,
                'total_engagement': total_engagement,
                'total_impressions': total_impressions,
                'total_reach': total_reach,
            },
            'averages': {
                'avg_likes_per_post': round(avg_likes, 1),
                'avg_comments_per_post': round(avg_comments, 1),
                'avg_engagement_per_post': round(avg_engagement, 1),
                'engagement_rate': round(engagement_rate, 2),
            },
            'best_posts': [
                {
                    'caption': p.get('caption', '')[:100],
                    'likes': p.get('likes', 0),
                    'comments': p.get('comments', 0),
                    'engagement': p.get('engagement', 0),
                    'permalink': p.get('permalink', ''),
                }
                for p in best_posts
            ],
            'hashtags': {
                'top_hashtags': top_hashtags,
                'total_unique_hashtags': len(hashtag_counts),
            },
            'posting_patterns': {
                'posts_by_day': posts_by_day,
                'best_hours_to_post': [
                    {'hour': f'{hour}:00', 'avg_engagement': round(eng, 1)}
                    for hour, eng in best_hours
                ],
            },
        }
