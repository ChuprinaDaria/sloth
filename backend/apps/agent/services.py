import openai
import time
import json
from django.conf import settings
from apps.embeddings.tasks import search_similar
from apps.documents.photo_analysis import PhotoAnalysisService
from apps.documents.models import Photo
from .models import Prompt, Conversation, Message

openai.api_key = settings.OPENAI_API_KEY


class AgentService:
    """Service for AI agent chat functionality with calendar integration"""

    def __init__(self, user_id, tenant_schema):
        self.user_id = user_id
        self.tenant_schema = tenant_schema
        self.calendar_tools = None

        # Load calendar tools if available
        try:
            from apps.integrations.calendar_ai_tools import get_calendar_tools_for_user
            self.calendar_tools = get_calendar_tools_for_user(user_id, tenant_schema)
        except Exception as e:
            print(f"Calendar tools not available: {e}")

    def get_or_create_prompt(self):
        """Get active prompt for user"""
        prompt = Prompt.objects.filter(
            user_id=self.user_id,
            is_active=True
        ).first()

        if not prompt:
            prompt = Prompt.objects.create(user_id=self.user_id)

        return prompt

    def chat(self, conversation_id, user_message, photo_id=None):
        """
        Process chat message with RAG
        """
        start_time = time.time()

        # Get conversation
        conversation = Conversation.objects.get(id=conversation_id, user_id=self.user_id)

        # Get prompt settings
        prompt = self.get_or_create_prompt()

        # Save user message
        user_msg = Message.objects.create(
            conversation=conversation,
            role='user',
            content=user_message,
            photo_id=photo_id
        )

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

        # Build messages for OpenAI
        messages = [
            {"role": "system", "content": prompt.get_system_prompt()},
        ]

        # Add RAG context if available
        if rag_context:
            messages.append({
                "role": "system",
                "content": f"Relevant information from your knowledge base:\n{rag_context}"
            })

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
                        "description": "Book an appointment in the calendar",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "customer_name": {"type": "string", "description": "Customer's full name"},
                                "customer_email": {"type": "string", "description": "Customer's email"},
                                "service": {"type": "string", "description": "Type of service (e.g., 'Haircut', 'Manicure')"},
                                "date": {"type": "string", "description": "Date (e.g., 'tomorrow', '2024-11-15')"},
                                "time": {"type": "string", "description": "Time (e.g., '14:00', '2:00 PM')"},
                                "duration_minutes": {"type": "integer", "description": "Duration in minutes (default 60)"},
                                "create_meet": {"type": "boolean", "description": "Create Google Meet link (default true)"}
                            },
                            "required": ["customer_name", "customer_email", "service", "date", "time"]
                        }
                    }
                }
            ]

        # Call OpenAI API
        try:
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
                            service=function_args.get('service'),
                            date_str=function_args.get('date'),
                            time_str=function_args.get('time'),
                            duration_minutes=function_args.get('duration_minutes', 60),
                            create_meet=function_args.get('create_meet', True)
                        )
                    else:
                        function_response = "Function not found"

                    # Add function response to messages
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

    def create_conversation(self, source='web', external_id=''):
        """Create new conversation"""
        conversation = Conversation.objects.create(
            user_id=self.user_id,
            source=source,
            external_id=external_id
        )
        return conversation
