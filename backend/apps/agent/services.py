import openai
import time
import json
from django.conf import settings
from apps.embeddings.tasks import search_similar
from apps.documents.photo_analysis import PhotoAnalysisService
from apps.documents.models import Photo
from .models import Prompt, Conversation, Message
from .voice_service import VoiceService
from .email_service import EmailService
from apps.integrations.email_integration import EmailIntegrationService

openai.api_key = settings.OPENAI_API_KEY


class AgentService:
    """Service for AI agent chat functionality with calendar, voice, and email integration"""

    def __init__(self, user_id, tenant_schema):
        self.user_id = user_id
        self.tenant_schema = tenant_schema
        self.calendar_tools = None
        self.voice_service = VoiceService(user_id, tenant_schema)
        self.email_service = EmailService()

        # Load calendar tools if available
        try:
            from apps.integrations.calendar_ai_tools import get_calendar_tools_for_user
            self.calendar_tools = get_calendar_tools_for_user(user_id, tenant_schema)
        except Exception as e:
            print(f"Calendar tools not available: {e}")

        # Load Google Reviews service
        try:
            from apps.integrations.google_reviews import GoogleReviewsService
            self.reviews_service = GoogleReviewsService(user_id, tenant_schema)
        except Exception as e:
            print(f"Reviews service not available: {e}")
            self.reviews_service = None

        # Load Instagram service
        try:
            from apps.integrations.instagram_service import InstagramService
            self.instagram_service = InstagramService(user_id, tenant_schema)
        except Exception as e:
            print(f"Instagram service not available: {e}")
            self.instagram_service = None

        # Load Email integration service (for Gmail analysis)
        try:
            self.email_integration = EmailIntegrationService(user_id, tenant_schema)
        except Exception as e:
            print(f"Email integration not available: {e}")
            self.email_integration = None

    def get_or_create_prompt(self):
        """Get active prompt for user"""
        prompt = Prompt.objects.filter(
            user_id=self.user_id,
            is_active=True
        ).first()

        if not prompt:
            prompt = Prompt.objects.create(user_id=self.user_id)

        return prompt

    def chat(self, conversation_id, user_message, photo_id=None, audio_file=None):
        """
        Process chat message with RAG, voice support, and proactive booking

        Args:
            conversation_id: ID розмови
            user_message: текст повідомлення (або None якщо тільки audio)
            photo_id: ID фото (опційно)
            audio_file: шлях до аудіо файлу (опційно)
        """
        start_time = time.time()

        # Get conversation
        conversation = Conversation.objects.get(id=conversation_id, user_id=self.user_id)

        # Get prompt settings
        prompt = self.get_or_create_prompt()

        # Process audio if provided (STT)
        detected_language = None
        if audio_file and not user_message:
            transcription = self.voice_service.transcribe_audio(audio_file)
            if transcription['success']:
                user_message = transcription['text']
                detected_language = transcription.get('language', 'uk')

        # Detect language from text if not from audio
        if not detected_language:
            detected_language = self._detect_language(user_message)

        # Store detected language (removed metadata - field doesn't exist)
        #TODO: Add metadata field to Conversation model if needed
        # conversation.save()

        # Save user message
        user_msg = Message.objects.create(
            conversation=conversation,
            role='user',
            content=user_message,
            photo_id=photo_id,
            metadata={'language': detected_language}  # This is OK - Message has metadata field
        )

        # Link audio to message if provided
        if audio_file:
            self.voice_service.process_voice_message(user_msg.id, audio_file, is_from_user=True)

        # Process photo if provided
        photo_analysis_context = None
        if photo_id:
            photo_analysis_context = self._process_client_photo(photo_id)

        # Search for relevant context using RAG
        context_results = search_similar(
            query_text=user_message,
            tenant_schema=self.tenant_schema,
            limit=5
        )

        # Build context from embeddings
        rag_context = self._build_rag_context(context_results)
        context_ids = [r['id'] for r in context_results]

        # Get conversation history
        history = self._get_conversation_history(conversation, limit=10)

        # Build messages for OpenAI with language instruction
        language_names = {
            'uk': 'українською',
            'pl': 'po polsku',
            'de': 'auf Deutsch',
            'en': 'in English'
        }
        language_instruction = f"\nВАЖЛИВО: Клієнт спілкується {language_names.get(detected_language, 'українською')}. Відповідай ТІЛЬКИ {language_names.get(detected_language, 'українською')}!\nЯкщо в базі знань інформація іншою мовою - переклади її на мову клієнта.\n"

        messages = [
            {"role": "system", "content": prompt.get_system_prompt() + language_instruction},
        ]

        # Add Google Reviews context for objection handling
        if self.reviews_service:
            try:
                reviews_context = self.reviews_service.get_context_for_ai_agent()
                if reviews_context:
                    messages.append({
                        "role": "system",
                        "content": reviews_context
                    })
            except Exception as e:
                print(f"Error getting reviews context: {e}")

        # Add RAG context if available
        if rag_context:
            messages.append({
                "role": "system",
                "content": f"Relevant information from your knowledge base:\n{rag_context}"
            })

        # Add Instagram posts context for Enterprise plan users
        if self.instagram_service:
            try:
                instagram_context = self._get_instagram_context_for_rag(user_message)
                if instagram_context:
                    messages.append({
                        "role": "system",
                        "content": f"Relevant Instagram posts:\n{instagram_context}"
                    })
            except Exception as e:
                print(f"Error getting Instagram context: {e}")

        # Add photo analysis context if available
        if photo_analysis_context:
            messages.append({
                "role": "system",
                "content": f"Photo Analysis Results:\n{photo_analysis_context}"
            })

        # Add calendar availability context if available
        if self.calendar_tools and self.calendar_tools.is_available():
            # Check if message is about booking/appointment
            booking_keywords = ['запис', 'бронь', 'appointment', 'book', 'schedule', 'slot', 'available']
            if any(keyword in user_message.lower() for keyword in booking_keywords):
                try:
                    # Get upcoming appointments as context
                    upcoming = self.calendar_tools.list_upcoming_appointments()
                    messages.append({
                        "role": "system",
                        "content": f"Calendar Integration Available. Current appointments:\n{upcoming}"
                    })
                except:
                    pass

        # Add conversation history
        messages.extend(history)

        # Add current user message
        messages.append({"role": "user", "content": user_message})

        # Define function tools for OpenAI
        tools = []
        if self.calendar_tools and self.calendar_tools.is_available():
            tools = [
                {
                    "type": "function",
                    "function": {
                        "name": "check_calendar_availability",
                        "description": "Check available time slots in the calendar for a specific date",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "date": {
                                    "type": "string",
                                    "description": "The date to check (e.g., 'tomorrow', 'next monday', '2024-11-15')"
                                },
                                "duration_minutes": {
                                    "type": "integer",
                                    "description": "Appointment duration in minutes (default 60)"
                                }
                            },
                            "required": ["date"]
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "book_appointment",
                        "description": "Book an appointment in the calendar (domain-agnostic: meeting, service, etc.)",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "customer_name": {"type": "string", "description": "Client name (optional)"},
                                "customer_email": {"type": "string", "description": "Client email (optional)"},
                                "client_phone": {"type": "string", "description": "Client phone (optional)"},
                                "service": {"type": "string", "description": "Type of service (e.g., 'Haircut', 'Manicure')"},
                                "date": {"type": "string", "description": "Date (e.g., 'tomorrow', '2024-11-15')"},
                                "time": {"type": "string", "description": "Time (e.g., '14:00', '2:00 PM')"},
                                "duration_minutes": {"type": "integer", "description": "Duration in minutes (default 60)"},
                                "create_meet": {"type": "boolean", "description": "Create Google Meet link (default true)"},
                                "master": {"type": "string", "description": "Assignee/owner (optional)"},
                                "price": {"type": "number", "description": "Price/amount (optional)"}
                            },
                            "required": ["service", "date", "time"]
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "list_appointments_for_date",
                        "description": "List all calendar events for a specific date",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "date": {
                                    "type": "string",
                                    "description": "The date (e.g., '1.10.2025', '2025-10-01', 'today')"
                                }
                            },
                            "required": ["date"]
                        }
                    }
                }
            ]

        # Email tools (if email integration connected)
        email_tools_available = False
        if self.email_integration:
            try:
                # Probe integration exists
                if self.email_integration.get_integration_settings():
                    email_tools_available = True
            except Exception:
                email_tools_available = False

        if email_tools_available:
            tools.extend([
                {
                    "type": "function",
                    "function": {
                        "name": "list_recent_emails",
                        "description": "Get recent emails summary for last N days.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "days": {"type": "integer", "description": "How many days back", "default": 7},
                                "max_results": {"type": "integer", "description": "Max emails to return", "default": 10}
                            }
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "find_email",
                        "description": "Search emails by sender/subject/free query (Gmail syntax).",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "query": {"type": "string", "description": "Free-form Gmail query, e.g. 'from:john subject:invoice'"},
                                "days": {"type": "integer", "description": "How many days back", "default": 30},
                                "max_results": {"type": "integer", "description": "Max emails", "default": 10}
                            },
                            "required": ["query"]
                        }
                    }
                }
            ])

        # Call OpenAI API
        try:
            # Add calendar booking guidance if calendar tools available
            if self.calendar_tools and self.calendar_tools.is_available():
                messages.append({
                    "role": "system",
                    "content": (
                        "If the user asks to schedule/book, extract service, date, time from natural Ukrainian text "
                        "(support formats like '13.11.25', '9-00', '9:00'). "
                        "Also extract phone, email, assignee (master/owner), price if present. "
                        "If any critical fields (service/date/time) are missing, ask a brief follow-up. "
                        "Use booking tools with all available fields. Proceed even if email/phone are missing."
                    )
                })

            # First call - may request function calls
            response = openai.chat.completions.create(
                model=prompt.model,
                messages=messages,
                temperature=prompt.temperature,
                max_tokens=prompt.max_tokens,
                tools=tools if tools else None,
                tool_choice="auto" if tools else None
            )

            # Check if AI wants to call a function
            response_message = response.choices[0].message
            tool_calls = response_message.tool_calls

            if tool_calls:
                # AI wants to use calendar tools
                messages.append(response_message)

                # Execute each tool call
                for tool_call in tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)

                    # Execute the function
                    if function_name == "check_calendar_availability":
                        function_response = self.calendar_tools.check_availability(
                            date_str=function_args.get('date'),
                            duration_minutes=function_args.get('duration_minutes', 60)
                        )
                    elif function_name == "book_appointment":
                        function_response = self.calendar_tools.book_appointment(
                            customer_name=function_args.get('customer_name'),
                            customer_email=function_args.get('customer_email'),
                            client_phone=function_args.get('client_phone'),
                            service=function_args.get('service'),
                            date_str=function_args.get('date'),
                            time_str=function_args.get('time'),
                            duration_minutes=function_args.get('duration_minutes', 60),
                            create_meet=function_args.get('create_meet', True),
                            master=function_args.get('master'),
                            price=function_args.get('price')
                        )
                    elif function_name == "list_appointments_for_date":
                        function_response = self.calendar_tools.list_appointments_for_date(
                            date_str=function_args.get('date')
                        )
                    elif function_name == "list_recent_emails" and email_tools_available:
                        function_response = self.email_integration.list_recent_emails(
                            days=function_args.get('days', 7),
                            max_results=function_args.get('max_results', 10)
                        )
                    elif function_name == "find_email" and email_tools_available:
                        function_response = self.email_integration.search_emails(
                            query=function_args.get('query', ''),
                            days=function_args.get('days', 30),
                            max_results=function_args.get('max_results', 10)
                        )
                    else:
                        function_response = "Function not found"

                    # Add function response to messages
                    if not isinstance(function_response, str):
                        try:
                            function_response = json.dumps(function_response, ensure_ascii=False)
                        except Exception:
                            function_response = str(function_response)
                    messages.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": function_response
                    })

                # Call OpenAI again with function results
                second_response = openai.chat.completions.create(
                    model=prompt.model,
                    messages=messages,
                    temperature=prompt.temperature,
                    max_tokens=prompt.max_tokens
                )

                assistant_message = second_response.choices[0].message.content
                tokens_used = response.usage.total_tokens + second_response.usage.total_tokens

            else:
                # No function calls, use direct response
                assistant_message = response_message.content
                tokens_used = response.usage.total_tokens

            # Check if user is on FREE plan and add watermark
            try:
                from apps.subscriptions.models import Subscription
                from apps.accounts.models import User

                user = User.objects.get(id=self.user_id)
                if user.organization and hasattr(user.organization, 'subscription'):
                    subscription = user.organization.subscription
                    if subscription.has_watermark():
                        # Add watermark to the message
                        watermark = "\n\n🦥 _Powered by [Sloth AI](https://sloth.ai)_"
                        assistant_message = assistant_message + watermark
            except Exception as e:
                print(f"Error adding watermark: {e}")

            # Save assistant message
            assistant_msg = Message.objects.create(
                conversation=conversation,
                role='assistant',
                content=assistant_message,
                context_used=context_ids,
                tokens_used=tokens_used,
                processing_time=time.time() - start_time
            )

            # Update conversation stats
            conversation.message_count += 2
            conversation.total_tokens += tokens_used
            conversation.save()

            # Track usage
            from apps.subscriptions.models import Subscription
            from apps.accounts.models import User

            # Increment conversations counter for FREE plan
            try:
                user = User.objects.get(id=self.user_id)
                if user.organization and hasattr(user.organization, 'subscription'):
                    subscription = user.organization.subscription
                    if subscription.is_free_plan():
                        subscription.increment_usage('conversations')
            except Exception as e:
                print(f"Error tracking usage: {e}")

            return {
                'message': assistant_message,
                'tokens_used': tokens_used,
                'processing_time': time.time() - start_time,
                'context_used': len(context_ids),
                'function_calls_made': len(tool_calls) if tool_calls else 0
            }

        except Exception as e:
            # Log error
            print(f"Error in AI chat: {e}")
            raise

    def _build_rag_context(self, results):
        """Build context string from search results"""
        if not results:
            return ""

        context_parts = []
        for i, result in enumerate(results, 1):
            context_parts.append(
                f"[Source {i} - {result['source_type']}]\n{result['content']}\n"
            )

        return "\n".join(context_parts)

    def _get_conversation_history(self, conversation, limit=10):
        """Get recent conversation history"""
        messages = Message.objects.filter(
            conversation=conversation
        ).order_by('-created_at')[:limit]

        # Reverse to chronological order
        messages = list(reversed(messages))

        history = []
        for msg in messages:
            if msg.role in ['user', 'assistant']:
                history.append({
                    "role": msg.role,
                    "content": msg.content
                })

        return history

    def _process_client_photo(self, photo_id):
        """
        Process client's photo: analyze, find similar, generate questions

        Args:
            photo_id: ID of the photo uploaded by client

        Returns:
            str: formatted context about the photo analysis
        """
        try:
            # Get photo
            photo = Photo.objects.get(id=photo_id)

            # Initialize photo analysis service
            photo_service = PhotoAnalysisService(tenant_schema=self.tenant_schema)

            # Analyze the photo if not already processed
            if not photo.is_processed:
                analysis_result = photo_service.analyze_photo(photo_id, photo.file_path)
                if analysis_result['status'] != 'success':
                    return None
            else:
                # Load existing analysis
                analysis_result = {
                    'detailed_analysis': photo.detailed_analysis
                }

            client_analysis = analysis_result['detailed_analysis']

            # Find similar photos from user's portfolio
            similar_photos = photo_service.find_similar_photos(
                client_photo_analysis=client_analysis,
                user_id=self.user_id,
                limit=5
            )

            # Generate questions and recommendations
            questions_data = photo_service.generate_client_questions(
                client_photo_analysis=client_analysis,
                similar_photos=similar_photos
            )

            # Format context for AI
            context_parts = []

            # Add photo analysis
            context_parts.append("=== CLIENT PHOTO ANALYSIS ===")
            context_parts.append(f"Category: {client_analysis.get('category', 'unknown')}")

            if client_analysis.get('hair_analysis', {}).get('present'):
                hair = client_analysis['hair_analysis']
                context_parts.append("\nHair Analysis:")
                context_parts.append(f"- Color: {hair.get('color', 'N/A')}")
                context_parts.append(f"- Length: {hair.get('length', 'N/A')}")
                context_parts.append(f"- Condition: {hair.get('condition', 'N/A')}")
                context_parts.append(f"- Texture: {hair.get('texture', 'N/A')}")
                context_parts.append(f"- Style: {hair.get('style', 'N/A')}")
                if hair.get('visible_treatments'):
                    context_parts.append(f"- Previous treatments: {', '.join(hair['visible_treatments'])}")

            if client_analysis.get('skin_analysis', {}).get('present'):
                skin = client_analysis['skin_analysis']
                context_parts.append("\nSkin Analysis:")
                context_parts.append(f"- Tone: {skin.get('tone', 'N/A')}")
                context_parts.append(f"- Condition: {skin.get('condition', 'N/A')}")
                if skin.get('visible_concerns'):
                    context_parts.append(f"- Concerns: {', '.join(skin['visible_concerns'])}")

            # Add overall assessment
            if client_analysis.get('overall_assessment'):
                context_parts.append(f"\nOverall: {client_analysis['overall_assessment']}")

            # Add similar portfolio examples
            if similar_photos:
                context_parts.append("\n=== SIMILAR WORK FROM YOUR PORTFOLIO ===")
                for i, similar in enumerate(similar_photos[:3], 1):
                    context_parts.append(f"\nExample {i} (Similarity: {similar['similarity_score']:.0%}):")
                    if similar.get('description'):
                        context_parts.append(f"- Description: {similar['description']}")
                    services = similar.get('analysis', {}).get('service_suggestions', [])
                    if services:
                        context_parts.append(f"- Services performed: {', '.join(services)}")

            # Add AI-generated recommendations
            if questions_data:
                context_parts.append("\n=== RECOMMENDED APPROACH ===")

                if questions_data.get('clarifying_questions'):
                    context_parts.append("\nQuestions to ask client:")
                    for q in questions_data['clarifying_questions']:
                        context_parts.append(f"- {q}")

                if questions_data.get('service_recommendations'):
                    context_parts.append("\nRecommended services:")
                    for s in questions_data['service_recommendations']:
                        context_parts.append(f"- {s}")

                if questions_data.get('estimated_details'):
                    details = questions_data['estimated_details']
                    context_parts.append(f"\nEstimated details:")
                    context_parts.append(f"- Duration: {details.get('duration', 'N/A')}")
                    context_parts.append(f"- Complexity: {details.get('complexity', 'N/A')}")

            context_parts.append("\n=== INSTRUCTIONS ===")
            context_parts.append("Use this analysis to:")
            context_parts.append("1. Acknowledge what you see in the photo specifically")
            context_parts.append("2. Reference similar work from the portfolio")
            context_parts.append("3. Ask relevant clarifying questions")
            context_parts.append("4. Provide service recommendations and pricing")
            context_parts.append("5. Be conversational and helpful in Ukrainian")

            return "\n".join(context_parts)

        except Exception as e:
            print(f"Error processing client photo: {e}")
            return None

    def _detect_language(self, text):
        """
        Визначити мову тексту клієнта

        Args:
            text: текст повідомлення

        Returns:
            str: код мови (uk, en, pl, de)
        """
        if not text:
            return 'uk'

        try:
            # Українські слова-маркери
            uk_markers = ['привіт', 'добрий', 'запис', 'хочу', 'треба', 'можна', 'будь', 'який', 'коли', 'де', 'що']
            # Польські
            pl_markers = ['dzień', 'dobry', 'chcę', 'proszę', 'czy', 'jak', 'kiedy', 'gdzie', 'witam', 'cześć']
            # Німецькі
            de_markers = ['guten', 'hallo', 'ich', 'möchte', 'bitte', 'wie', 'wann', 'wo', 'danke', 'schön']
            # Англійські
            en_markers = ['hello', 'good', 'want', 'need', 'please', 'how', 'when', 'where', 'thank', 'day']

            text_lower = text.lower()

            # Підрахунок співпадінь
            uk_count = sum(1 for marker in uk_markers if marker in text_lower)
            pl_count = sum(1 for marker in pl_markers if marker in text_lower)
            de_count = sum(1 for marker in de_markers if marker in text_lower)
            en_count = sum(1 for marker in en_markers if marker in text_lower)

            # Визначити найбільш ймовірну мову
            counts = {
                'uk': uk_count,
                'pl': pl_count,
                'de': de_count,
                'en': en_count
            }

            detected = max(counts, key=counts.get)

            # Якщо не знайдено маркерів - за замовчуванням українська
            if counts[detected] == 0:
                return 'uk'

            return detected

        except Exception as e:
            print(f"Error detecting language: {e}")
            return 'uk'

    def _get_instagram_context_for_rag(self, query_text):
        """
        Отримати релевантні Instagram пости для RAG (тільки для MAX)

        Args:
            query_text: текст запиту клієнта

        Returns:
            str: форматований контекст з Instagram постів
        """
        try:
            # Check if user has Enterprise plan
            if not self.instagram_service or not self.instagram_service.check_enterprise_plan():
                return None

            from apps.integrations.models import InstagramPost
            import numpy as np

            # Get user's Instagram posts with embeddings
            posts = InstagramPost.objects.filter(
                user_id=self.user_id
            ).exclude(embedding=[])[:50]

            if not posts:
                return None

            # Create embedding for query
            import openai
            query_embedding = openai.embeddings.create(
                model="text-embedding-3-small",
                input=query_text
            ).data[0].embedding

            # Calculate cosine similarity
            similarities = []
            for post in posts:
                post_embedding = np.array(post.embedding)
                query_emb = np.array(query_embedding)

                # Cosine similarity
                similarity = np.dot(post_embedding, query_emb) / (
                    np.linalg.norm(post_embedding) * np.linalg.norm(query_emb)
                )

                similarities.append({
                    'post': post,
                    'similarity': similarity
                })

            # Sort by similarity and get top 3
            similarities.sort(key=lambda x: x['similarity'], reverse=True)
            top_posts = similarities[:3]

            # Filter by minimum similarity threshold
            relevant_posts = [p for p in top_posts if p['similarity'] > 0.5]

            if not relevant_posts:
                return None

            # Format context
            context_parts = []
            context_parts.append("=== RELEVANT INSTAGRAM POSTS ===")

            for i, item in enumerate(relevant_posts, 1):
                post = item['post']
                context_parts.append(f"\nPost {i} (Relevance: {item['similarity']:.0%}):")
                context_parts.append(f"Caption: {post.caption[:200]}")
                if post.hashtags:
                    context_parts.append(f"Hashtags: {', '.join(post.hashtags[:5])}")
                context_parts.append(f"Engagement: {post.likes} likes, {post.comments} comments")

            context_parts.append("\nУse this Instagram content to show examples of your work.")

            return "\n".join(context_parts)

        except Exception as e:
            print(f"Error getting Instagram context: {e}")
            return None

    def create_conversation(self, source='web', external_id=''):
        """Create new conversation"""
        conversation = Conversation.objects.create(
            user_id=self.user_id,
            source=source,
            external_id=external_id
        )
        return conversation
