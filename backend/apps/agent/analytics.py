"""
Smart Analytics Service - AI-powered insights generation
"""
import openai
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .models import Conversation, Message
import json

openai.api_key = settings.OPENAI_API_KEY


class SmartAnalyticsService:
    """Generate AI-powered insights from conversation data"""

    def __init__(self, user_id, tenant_schema, language='en'):
        self.user_id = user_id
        self.tenant_schema = tenant_schema
        self.language = language

    def generate_insights(self):
        """
        Generate smart insights using AI

        Returns insights in user's language about:
        - Peak activity times
        - No-show patterns
        - Popular topics/services
        - Client behavior patterns
        - Actionable recommendations
        """
        # Collect data for analysis
        stats = self._collect_statistics()

        if not stats['has_data']:
            return {
                'insights': [],
                'summary': self._get_no_data_message(),
                'generated_at': timezone.now().isoformat(),
            }

        # Generate AI insights
        insights = self._generate_ai_insights(stats)

        return {
            'insights': insights,
            'summary': self._generate_summary(insights),
            'generated_at': timezone.now().isoformat(),
        }

    def _collect_statistics(self):
        """Collect conversation statistics for analysis"""
        # Get conversations from last 30 days
        thirty_days_ago = timezone.now() - timedelta(days=30)

        conversations = Conversation.objects.filter(
            user_id=self.user_id,
            created_at__gte=thirty_days_ago
        ).select_related().prefetch_related('messages')

        if not conversations.exists():
            return {'has_data': False}

        # Collect statistics
        total_conversations = conversations.count()
        messages = Message.objects.filter(
            conversation__in=conversations
        )

        # Time-based analysis
        hour_distribution = {}
        for conv in conversations:
            hour = conv.created_at.hour
            hour_distribution[hour] = hour_distribution.get(hour, 0) + 1

        # Message content analysis (extract keywords)
        keywords = {}
        for msg in messages.filter(role='user')[:100]:  # Last 100 user messages
            content_lower = msg.content.lower()
            # Simple keyword extraction
            for word in content_lower.split():
                if len(word) > 4:  # Skip short words
                    keywords[word] = keywords.get(word, 0) + 1

        # Top keywords
        top_keywords = sorted(keywords.items(), key=lambda x: x[1], reverse=True)[:10]

        # Recent conversations pattern
        recent_convs = list(conversations.order_by('-created_at')[:20])

        return {
            'has_data': True,
            'total_conversations': total_conversations,
            'total_messages': messages.count(),
            'hour_distribution': hour_distribution,
            'top_keywords': top_keywords,
            'recent_conversations': recent_convs,
            'average_messages_per_conversation': messages.count() / max(total_conversations, 1),
        }

    def _generate_ai_insights(self, stats):
        """Use GPT to generate human-readable insights"""
        # Prepare data summary for AI
        data_summary = {
            'total_conversations': stats['total_conversations'],
            'total_messages': stats['total_messages'],
            'avg_messages': round(stats['average_messages_per_conversation'], 1),
            'hour_distribution': stats['hour_distribution'],
            'top_topics': [kw[0] for kw in stats['top_keywords'][:5]],
        }

        # Language-specific prompts
        system_prompts = {
            'en': "You are a business analytics AI assistant. Analyze the data and provide 3-5 actionable insights in simple, conversational English. Focus on patterns, trends, and practical recommendations.",
            'uk': "Ти - AI асистент з аналітики бізнесу. Проаналізуй дані та надай 3-5 корисних інсайтів простою, розмовною українською мовою. Фокусуйся на патернах, трендах та практичних рекомендаціях.",
            'pl': "Jesteś asystentem AI do analityki biznesowej. Przeanalizuj dane i dostarcz 3-5 praktycznych spostrzeżeń prostym, konwersacyjnym językiem polskim. Skup się na wzorcach, trendach i praktycznych rekomendacjach.",
            'de': "Du bist ein KI-Assistent für Business-Analytik. Analysiere die Daten und liefere 3-5 umsetzbare Erkenntnisse in einfachem, umgangssprachlichem Deutsch. Konzentriere dich auf Muster, Trends und praktische Empfehlungen.",
        }

        system_prompt = system_prompts.get(self.language, system_prompts['en'])

        user_prompt = f"""
Analyze this conversation data and provide insights:

Data:
- Total conversations: {data_summary['total_conversations']}
- Total messages: {data_summary['total_messages']}
- Average messages per conversation: {data_summary['avg_messages']}
- Peak hours: {self._get_peak_hours(stats['hour_distribution'])}
- Top topics/keywords: {', '.join(data_summary['top_topics'])}

Provide insights in this JSON format:
{{
  "insights": [
    {{
      "type": "trend|warning|time|clients|recommendation",
      "title": "Short title",
      "message": "Detailed insight",
      "action": "Actionable recommendation (optional)"
    }}
  ]
}}

Focus on:
1. When clients are most active
2. Any concerning patterns (e.g., repeated topics that might indicate issues)
3. Popular topics/services
4. Practical business recommendations

Be conversational and specific. Use examples like "30% of your clients message after 8 PM" instead of generic statements.
"""

        try:
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=1000,
                response_format={"type": "json_object"}
            )

            result = json.loads(response.choices[0].message.content)
            return result.get('insights', [])

        except Exception as e:
            print(f"Error generating AI insights: {e}")
            # Fallback to basic insights
            return self._generate_fallback_insights(stats)

    def _generate_fallback_insights(self, stats):
        """Generate basic insights without AI"""
        insights = []

        # Peak time insight
        peak_hour = max(stats['hour_distribution'].items(), key=lambda x: x[1])[0]
        insights.append({
            'type': 'time',
            'title': self._translate('peak_time_title'),
            'message': self._translate('peak_time_message').format(hour=peak_hour),
            'action': self._translate('peak_time_action')
        })

        # Activity insight
        if stats['total_conversations'] > 10:
            insights.append({
                'type': 'trend',
                'title': self._translate('activity_title'),
                'message': self._translate('activity_message').format(count=stats['total_conversations']),
            })

        # Top topics
        if stats['top_keywords']:
            top_topic = stats['top_keywords'][0][0]
            insights.append({
                'type': 'clients',
                'title': self._translate('popular_topic_title'),
                'message': self._translate('popular_topic_message').format(topic=top_topic),
            })

        return insights

    def _get_peak_hours(self, hour_dist):
        """Get peak hours from distribution"""
        if not hour_dist:
            return []
        sorted_hours = sorted(hour_dist.items(), key=lambda x: x[1], reverse=True)
        return [f"{h}:00" for h, _ in sorted_hours[:3]]

    def _generate_summary(self, insights):
        """Generate overall summary"""
        summaries = {
            'en': f"Based on {len(insights)} insights, your business is showing interesting patterns. Focus on the recommendations to improve client experience.",
            'uk': f"На основі {len(insights)} інсайтів, ваш бізнес показує цікаві патерни. Зверніть увагу на рекомендації для покращення клієнтського досвіду.",
            'pl': f"Na podstawie {len(insights)} spostrzeżeń, Twój biznes pokazuje interesujące wzorce. Skup się na rekomendacjach, aby poprawić doświadczenie klientów.",
            'de': f"Basierend auf {len(insights)} Erkenntnissen zeigt Ihr Unternehmen interessante Muster. Konzentrieren Sie sich auf die Empfehlungen zur Verbesserung der Kundenerfahrung.",
        }
        return summaries.get(self.language, summaries['en'])

    def _get_no_data_message(self):
        """Get message for no data"""
        messages = {
            'en': "Not enough data yet. Start chatting with clients to see AI-powered insights!",
            'uk': "Ще недостатньо даних. Почніть спілкуватися з клієнтами, щоб побачити AI інсайти!",
            'pl': "Jeszcze za mało danych. Zacznij rozmawiać z klientami, aby zobaczyć spostrzeżenia AI!",
            'de': "Noch nicht genug Daten. Beginnen Sie mit Kunden zu chatten, um KI-Erkenntnisse zu sehen!",
        }
        return messages.get(self.language, messages['en'])

    def _translate(self, key):
        """Basic translations for fallback insights"""
        translations = {
            'en': {
                'peak_time_title': 'Peak Activity Time',
                'peak_time_message': 'Most clients contact you around {}:00',
                'peak_time_action': 'Consider being most responsive during this time',
                'activity_title': 'Growing Activity',
                'activity_message': 'You had {} conversations in the last 30 days',
                'popular_topic_title': 'Popular Topic',
                'popular_topic_message': 'Clients frequently mention: {}',
            },
            'uk': {
                'peak_time_title': 'Пікова активність',
                'peak_time_message': 'Більшість клієнтів пишуть близько {}:00',
                'peak_time_action': 'Розгляньте можливість бути найбільш доступними в цей час',
                'activity_title': 'Зростаюча активність',
                'activity_message': 'У вас було {} діалогів за останні 30 днів',
                'popular_topic_title': 'Популярна тема',
                'popular_topic_message': 'Клієнти часто згадують: {}',
            }
        }
        lang_trans = translations.get(self.language, translations['en'])
        return lang_trans.get(key, key)
