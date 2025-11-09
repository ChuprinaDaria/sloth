"""
Smart Analytics Service - AI-powered insights generation
"""
import openai
from django.conf import settings
from django.utils import timezone
from datetime import timedelta, datetime
from .models import Conversation, Message
import json
import holidays

openai.api_key = settings.OPENAI_API_KEY


class SmartAnalyticsService:
    """Generate AI-powered insights from conversation data"""

    def __init__(self, user_id, tenant_schema, language='en'):
        self.user_id = user_id
        self.tenant_schema = tenant_schema
        self.language = language
        self.country = self._get_user_country()

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

        # Add enhanced analysis
        holiday_insights = self._analyze_holidays(conversations)
        pricing_insights = self._analyze_pricing_opportunities(hour_distribution, conversations)
        sentiment_insights = self._analyze_sentiment(messages)

        return {
            'has_data': True,
            'total_conversations': total_conversations,
            'total_messages': messages.count(),
            'hour_distribution': hour_distribution,
            'top_keywords': top_keywords,
            'recent_conversations': recent_convs,
            'average_messages_per_conversation': messages.count() / max(total_conversations, 1),
            'holiday_insights': holiday_insights,
            'pricing_insights': pricing_insights,
            'sentiment_insights': sentiment_insights,
        }

    def _get_user_country(self):
        """Get user's country from organization"""
        try:
            from apps.accounts.models import User
            user = User.objects.get(id=self.user_id)
            if user.organization and user.organization.country:
                return user.organization.country
        except Exception as e:
            print(f"Error getting user country: {e}")
        return 'US'  # Default to US

    def _analyze_holidays(self, conversations):
        """Analyze bookings around holidays and predict busy periods"""
        try:
            # Get holidays for user's country
            country_holidays = holidays.country_holidays(self.country)

            # Find upcoming holidays (next 60 days)
            today = timezone.now().date()
            upcoming_holidays = []
            for i in range(1, 61):
                date = today + timedelta(days=i)
                if date in country_holidays:
                    upcoming_holidays.append({
                        'date': date,
                        'name': country_holidays[date],
                        'days_until': i
                    })

            # Analyze historical patterns around holidays
            holiday_patterns = []
            for holiday_info in upcoming_holidays[:5]:  # Next 5 holidays
                days_before = 7
                holiday_date = holiday_info['date']
                start_date = holiday_date - timedelta(days=days_before)

                # Count conversations in the week before this holiday in previous years
                similar_period_convs = conversations.filter(
                    created_at__date__gte=start_date - timedelta(days=365),
                    created_at__date__lte=start_date - timedelta(days=358)
                ).count()

                if similar_period_convs > 0:
                    holiday_patterns.append({
                        'holiday': holiday_info['name'],
                        'date': str(holiday_date),
                        'days_until': holiday_info['days_until'],
                        'historical_bookings': similar_period_convs
                    })

            return holiday_patterns

        except Exception as e:
            print(f"Error analyzing holidays: {e}")
            return []

    def _analyze_pricing_opportunities(self, hour_distribution, conversations):
        """Identify high-demand periods for potential price optimization"""
        insights = []

        # Analyze day-of-week patterns
        day_distribution = {}
        for conv in conversations:
            day = conv.created_at.strftime('%A')
            day_distribution[day] = day_distribution.get(day, 0) + 1

        if day_distribution:
            # Find peak days
            sorted_days = sorted(day_distribution.items(), key=lambda x: x[1], reverse=True)
            if len(sorted_days) >= 2:
                peak_day = sorted_days[0]
                avg_bookings = sum(day_distribution.values()) / len(day_distribution)

                # If peak day is 50% more than average, suggest pricing optimization
                if peak_day[1] > avg_bookings * 1.5:
                    insights.append({
                        'type': 'high_demand_day',
                        'day': peak_day[0],
                        'bookings': peak_day[1],
                        'percentage_above_average': round(((peak_day[1] / avg_bookings) - 1) * 100, 1)
                    })

        # Analyze time slots
        if hour_distribution:
            sorted_hours = sorted(hour_distribution.items(), key=lambda x: x[1], reverse=True)
            if len(sorted_hours) >= 3:
                peak_hours = sorted_hours[:3]
                avg_hourly = sum(hour_distribution.values()) / len(hour_distribution)

                high_demand_hours = [h for h, count in peak_hours if count > avg_hourly * 1.5]
                if high_demand_hours:
                    insights.append({
                        'type': 'high_demand_hours',
                        'hours': high_demand_hours,
                        'bookings_count': sum(hour_distribution[h] for h in high_demand_hours)
                    })

        # Find free slots (hours with no bookings)
        all_hours = set(range(8, 21))  # Business hours 8 AM - 9 PM
        booked_hours = set(hour_distribution.keys())
        free_hours = all_hours - booked_hours

        if free_hours:
            insights.append({
                'type': 'available_slots',
                'hours': sorted(list(free_hours))
            })

        return insights

    def _analyze_sentiment(self, messages):
        """Analyze conversation sentiment to identify VIP, dissatisfied, and problematic clients"""
        insights = {
            'frequent_users': [],
            'potentially_dissatisfied': [],
            'negative_interactions': []
        }

        # Group messages by conversation and analyze patterns
        user_messages = messages.filter(role='user')

        # Identify frequent users (more than 5 conversations)
        from django.db.models import Count
        frequent_conversations = user_messages.values('conversation_id').annotate(
            msg_count=Count('id')
        ).filter(msg_count__gte=5).order_by('-msg_count')[:5]

        for conv_data in frequent_conversations:
            conv_id = conv_data['conversation_id']
            msg_count = conv_data['msg_count']
            insights['frequent_users'].append({
                'conversation_id': conv_id,
                'message_count': msg_count
            })

        # Analyze recent messages for negative keywords
        negative_keywords = ['cancel', 'unhappy', 'disappointed', 'bad', 'terrible',
                            'worst', 'не задоволений', 'не подобається', 'погано',
                            'відміна', 'скасувати', 'жахливо']

        recent_messages = user_messages.order_by('-created_at')[:100]
        for msg in recent_messages:
            content_lower = msg.content.lower()
            if any(keyword in content_lower for keyword in negative_keywords):
                insights['potentially_dissatisfied'].append({
                    'conversation_id': msg.conversation_id,
                    'message': msg.content[:100],
                    'date': msg.created_at.isoformat()
                })

        return insights

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

        # Format enhanced insights for AI
        holiday_info = ""
        if stats['holiday_insights']:
            holiday_info = f"\n\nUpcoming holidays and patterns:\n"
            for h in stats['holiday_insights']:
                holiday_info += f"- {h['holiday']} in {h['days_until']} days (historical bookings: {h['historical_bookings']})\n"

        pricing_info = ""
        if stats['pricing_insights']:
            pricing_info = "\n\nPricing opportunities:\n"
            for p in stats['pricing_insights']:
                if p['type'] == 'high_demand_day':
                    pricing_info += f"- High demand on {p['day']} ({p['percentage_above_average']}% above average)\n"
                elif p['type'] == 'high_demand_hours':
                    pricing_info += f"- High demand hours: {', '.join(map(str, p['hours']))}\n"
                elif p['type'] == 'available_slots':
                    pricing_info += f"- Available time slots: {', '.join(map(str, p['hours']))}\n"

        sentiment_info = ""
        if stats['sentiment_insights']:
            s = stats['sentiment_insights']
            if s['frequent_users']:
                sentiment_info += f"\n- {len(s['frequent_users'])} frequent users identified (potential VIPs for bonuses)\n"
            if s['potentially_dissatisfied']:
                sentiment_info += f"\n- {len(s['potentially_dissatisfied'])} potentially dissatisfied clients detected\n"

        user_prompt = f"""
Analyze this conversation data and provide insights:

Data:
- Total conversations: {data_summary['total_conversations']}
- Total messages: {data_summary['total_messages']}
- Average messages per conversation: {data_summary['avg_messages']}
- Peak hours: {self._get_peak_hours(stats['hour_distribution'])}
- Top topics/keywords: {', '.join(data_summary['top_topics'])}
{holiday_info}{pricing_info}{sentiment_info}

Provide insights in this JSON format:
{{
  "insights": [
    {{
      "type": "trend|warning|time|clients|recommendation|holiday|pricing|vip",
      "title": "Short title",
      "message": "Detailed insight",
      "action": "Actionable recommendation (optional)"
    }}
  ]
}}

Focus on:
1. Holiday predictions - warn about busy periods before holidays
2. Pricing optimization - suggest raising prices on high-demand days/times
3. Time patterns - when most bookings occur
4. Client behavior - frequent users (offer bonuses), dissatisfied clients (contact them)
5. Available slots - point out free time windows

Be conversational and specific. Use examples like "30% of your clients message after 8 PM" instead of generic statements.
Generate 5-8 insights covering different aspects.
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
