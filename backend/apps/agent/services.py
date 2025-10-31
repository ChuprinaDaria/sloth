import openai
import time
from django.conf import settings
from apps.embeddings.tasks import search_similar
from .models import Prompt, Conversation, Message

openai.api_key = settings.OPENAI_API_KEY


class AgentService:
    """Service for AI agent chat functionality"""

    def __init__(self, user_id, tenant_schema):
        self.user_id = user_id
        self.tenant_schema = tenant_schema

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

        # Add conversation history
        messages.extend(history)

        # Add current user message
        messages.append({"role": "user", "content": user_message})

        # Call OpenAI API
        try:
            response = openai.chat.completions.create(
                model=prompt.model,
                messages=messages,
                temperature=prompt.temperature,
                max_tokens=prompt.max_tokens
            )

            assistant_message = response.choices[0].message.content
            tokens_used = response.usage.total_tokens

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

            # This would normally be done in a signal or middleware
            # subscription.increment_usage('messages')

            return {
                'message': assistant_message,
                'tokens_used': tokens_used,
                'processing_time': time.time() - start_time,
                'context_used': len(context_ids)
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

    def create_conversation(self, source='web', external_id=''):
        """Create new conversation"""
        conversation = Conversation.objects.create(
            user_id=self.user_id,
            source=source,
            external_id=external_id
        )
        return conversation
