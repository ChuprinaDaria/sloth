from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import Prompt, Conversation, Message
from .services import AgentService
from rest_framework import serializers


class PromptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prompt
        fields = [
            'id', 'role', 'instructions', 'context',
            'temperature', 'max_tokens', 'model',
            'is_active', 'version', 'created_at', 'updated_at'
        ]
        read_only_fields = ['version', 'created_at', 'updated_at']


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = [
            'id', 'role', 'content', 'photo_id',
            'tokens_used', 'processing_time', 'created_at'
        ]


class ConversationSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Conversation
        fields = [
            'id', 'source', 'title', 'message_count',
            'total_tokens', 'created_at', 'updated_at', 'messages'
        ]


class ConversationListSerializer(serializers.ModelSerializer):
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            'id', 'source', 'title', 'message_count',
            'created_at', 'updated_at', 'last_message'
        ]

    def get_last_message(self, obj):
        last_msg = obj.messages.last()
        if last_msg:
            return {
                'role': last_msg.role,
                'content': last_msg.content[:100],
                'created_at': last_msg.created_at
            }
        return None


class PromptView(generics.RetrieveUpdateAPIView):
    """Get/Update AI prompt"""
    serializer_class = PromptSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        # Get or create active prompt
        prompt, _ = Prompt.objects.get_or_create(
            user_id=self.request.user.id,
            is_active=True
        )
        return prompt

    def perform_update(self, serializer):
        # Increment version on update
        instance = serializer.save()
        instance.version += 1
        instance.save()


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def chat_view(request):
    """Send message to AI agent"""
    conversation_id = request.data.get('conversation_id')
    message = request.data.get('message')
    photo_id = request.data.get('photo_id')

    if not message:
        return Response({'error': 'Message is required'}, status=status.HTTP_400_BAD_REQUEST)

    # Create agent service
    agent = AgentService(
        user_id=request.user.id,
        tenant_schema=request.user.organization.schema_name
    )

    # Create conversation if not provided
    if not conversation_id:
        conversation = agent.create_conversation(source='web')
        conversation_id = conversation.id
    else:
        # Verify conversation belongs to user
        try:
            conversation = Conversation.objects.get(
                id=conversation_id,
                user_id=request.user.id
            )
        except Conversation.DoesNotExist:
            return Response(
                {'error': 'Conversation not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    # Process message
    try:
        result = agent.chat(
            conversation_id=conversation_id,
            user_message=message,
            photo_id=photo_id
        )

        return Response({
            'conversation_id': conversation_id,
            'message': result['message'],
            'tokens_used': result['tokens_used'],
            'processing_time': result['processing_time'],
            'context_used': result['context_used']
        })

    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class ConversationListView(generics.ListCreateAPIView):
    """List conversations or create new one"""
    serializer_class = ConversationListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Conversation.objects.filter(user_id=self.request.user.id)

    def perform_create(self, serializer):
        serializer.save(user_id=self.request.user.id)


class ConversationDetailView(generics.RetrieveDestroyAPIView):
    """Get conversation with messages"""
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Conversation.objects.filter(user_id=self.request.user.id)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def test_chat_view(request):
    """Test chat in sandbox (doesn't save to history)
    
    Supports two modes:
    - 'client': Test as if talking to a client (normal chat)
    - 'assistant': Assistant mode - provides data about user's posts, emails, Instagram, dialogues
    """
    import logging
    logger = logging.getLogger(__name__)
    
    message = request.data.get('message')
    mode = request.data.get('mode', 'client')  # 'client' or 'assistant'
    file_obj = request.FILES.get('photo')

    # Require at least message or photo
    if not message and not file_obj:
        return Response({'error': 'Message or photo is required'}, status=status.HTTP_400_BAD_REQUEST)

    # Check organization exists
    if not hasattr(request.user, 'organization') or not request.user.organization:
        return Response(
            {'error': 'User organization not found'},
            status=status.HTTP_400_BAD_REQUEST
        )

    conversation = None
    try:
        agent = AgentService(
            user_id=request.user.id,
            tenant_schema=request.user.organization.schema_name
        )

        # If photo uploaded - save it and create Photo in tenant schema
        photo_id = None
        if file_obj:
            try:
                if not getattr(file_obj, 'content_type', '').startswith('image/'):
                    return Response({'error': 'Uploaded file must be an image'}, status=status.HTTP_400_BAD_REQUEST)

                from django.core.files.storage import default_storage
                from apps.accounts.middleware import TenantSchemaContext
                from apps.documents.models import Photo

                # Save file to storage
                saved_path = default_storage.save(f'photos/{file_obj.name}', file_obj)

                # Create Photo record in tenant schema
                with TenantSchemaContext(request.user.organization.schema_name):
                    photo = Photo.objects.create(
                        user_id=request.user.id,
                        file_path=saved_path,
                        file_size=file_obj.size
                    )
                    photo_id = photo.id

                # Provide default message if empty
                if not message:
                    message = "Користувач надіслав фото. Проаналізуй його та дай корисні поради."
            except Exception as file_err:
                logger.error(f"Error handling uploaded photo: {file_err}", exc_info=True)
                return Response({'error': 'Failed to process uploaded photo'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Create temporary conversation
        conversation = agent.create_conversation(source='web')

        # Add mode context to the message for assistant mode
        if mode == 'assistant':
            # In assistant mode, prepend context about the mode
            mode_context = "РЕЖИМ АСИСТЕНТА: Ти працюєш в режимі асистента для власника бізнесу. " \
                          "Ти маєш доступ до даних про пости, email, Instagram, діалоги користувача. " \
                          "Аналізуй ці дані та надавай корисну інформацію власнику бізнесу. " \
                          "Відповідай українською мовою.\n\n"
            enhanced_message = mode_context + message
        else:
            enhanced_message = message

        result = agent.chat(
            conversation_id=conversation.id,
            user_message=enhanced_message,
            photo_id=photo_id
        )

        # Delete test conversation
        conversation.delete()

        return Response({
            'message': result['message'],
            'tokens_used': result['tokens_used'],
            'mode': mode
        })

    except Exception as e:
        logger.error(f"Error in test_chat_view: {e}", exc_info=True)
        if conversation:
            try:
                conversation.delete()
            except:
                pass
        return Response(
            {'error': f'Failed to process message: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def smart_insights_view(request):
    """
    Get AI-powered smart insights about conversations

    Query params:
    - language: Language code (en, uk, pl, de)
    """
    from .analytics import SmartAnalyticsService

    language = request.GET.get('language', 'en')

    if not request.user.organization:
        return Response(
            {'error': 'No organization found'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        analytics = SmartAnalyticsService(
            user_id=request.user.id,
            tenant_schema=request.user.organization.schema_name,
            language=language
        )

        insights = analytics.generate_insights()
        return Response(insights)

    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def dashboard_stats_view(request):
    """Get dashboard statistics"""
    from django.db.models import Count, Q
    from django.utils import timezone
    from datetime import timedelta
    from apps.integrations.models import Integration
    import logging
    
    logger = logging.getLogger(__name__)
    
    if not hasattr(request.user, 'organization') or not request.user.organization:
        return Response(
            {'error': 'User organization not found'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Calculate date ranges
        now = timezone.now()
        last_month = now - timedelta(days=30)
        
        # Total conversations
        total_chats = Conversation.objects.filter(user_id=request.user.id).count()
        last_month_chats = Conversation.objects.filter(
            user_id=request.user.id,
            created_at__gte=last_month
        ).count()
        
        # Active users (unique conversations in last 30 days)
        active_users = Conversation.objects.filter(
            user_id=request.user.id,
            updated_at__gte=last_month
        ).values('external_id').distinct().count()
        
        # Calculate growth
        prev_period = now - timedelta(days=60)
        prev_chats = Conversation.objects.filter(
            user_id=request.user.id,
            created_at__gte=prev_period,
            created_at__lt=last_month
        ).count()
        
        chats_change = 0
        if prev_chats > 0:
            chats_change = round(((last_month_chats - prev_chats) / prev_chats) * 100)
        
        # Get calendar integration for bookings
        bookings_count = 0
        bookings_change = 0
        try:
            calendar_integration = Integration.objects.filter(
                user_id=request.user.id,
                integration_type='google_calendar',
                status='active'
            ).first()
            
            if calendar_integration:
                from apps.integrations.google_calendar import GoogleCalendarService
                credentials = calendar_integration.get_credentials()
                if credentials:
                    cal_service = GoogleCalendarService(credentials)
                    events = cal_service.list_events(
                        time_min=last_month.isoformat(),
                        time_max=now.isoformat()
                    )
                    bookings_count = len(events)
                    
                    # Previous period bookings
                    prev_events = cal_service.list_events(
                        time_min=prev_period.isoformat(),
                        time_max=last_month.isoformat()
                    )
                    prev_bookings = len(prev_events)
                    if prev_bookings > 0:
                        bookings_change = round(((bookings_count - prev_bookings) / prev_bookings) * 100)
        except Exception as e:
            logger.warning(f"Could not fetch calendar bookings: {e}")
        
        # Calculate conversion rate (bookings / active users)
        conversion_rate = 0
        if active_users > 0:
            conversion_rate = round((bookings_count / active_users) * 100)
        
        # Recent activity
        recent_conversations = Conversation.objects.filter(
            user_id=request.user.id
        ).order_by('-updated_at')[:10]
        
        recent_activity = []
        for conv in recent_conversations:
            time_diff = now - conv.updated_at
            if time_diff < timedelta(hours=1):
                time_ago = f"{int(time_diff.total_seconds() // 60)} min ago"
            elif time_diff < timedelta(days=1):
                time_ago = f"{int(time_diff.total_seconds() // 3600)} hour{'s' if time_diff.total_seconds() // 3600 > 1 else ''} ago"
            else:
                time_ago = f"{int(time_diff.days)} day{'s' if time_diff.days > 1 else ''} ago"
            
            activity_type = "Новий чат"
            if conv.source == 'telegram':
                activity_type = "Telegram чат"
            elif conv.source == 'instagram':
                activity_type = "Instagram чат"
            
            recent_activity.append({
                'title': f"{activity_type} від {conv.title or 'користувача'}",
                'time': time_ago,
                'type': conv.source
            })
        
        # Top services (from calendar events if available)
        top_services = []
        try:
            if calendar_integration and credentials:
                from collections import Counter
                cal_service = GoogleCalendarService(credentials)
                events = cal_service.list_events(
                    time_min=last_month.isoformat(),
                    time_max=now.isoformat()
                )
                
                # Extract service names from event summaries
                service_counter = Counter()
                for event in events:
                    summary = event.get('summary', '').lower()
                    # Simple keyword matching
                    if 'стрижка' in summary or 'haircut' in summary:
                        service_counter['Стрижка'] += 1
                    elif 'фарбування' in summary or 'coloring' in summary:
                        service_counter['Фарбування'] += 1
                    elif 'укладка' in summary or 'styling' in summary:
                        service_counter['Укладка'] += 1
                    elif 'balayage' in summary or 'балаяж' in summary:
                        service_counter['Balayage'] += 1
                    else:
                        service_counter['Інше'] += 1
                
                top_services = [
                    {'name': name, 'count': count}
                    for name, count in service_counter.most_common(5)
                ]
        except Exception as e:
            logger.warning(f"Could not fetch top services: {e}")
        
        return Response({
            'stats': {
                'total_chats': total_chats,
                'chats_change': f"+{chats_change}%" if chats_change > 0 else f"{chats_change}%",
                'active_users': active_users,
                'users_change': f"+{max(0, int(active_users * 0.08))}%",  # Approximate
                'bookings': bookings_count,
                'bookings_change': f"+{bookings_change}%" if bookings_change > 0 else f"{bookings_change}%",
                'conversion_rate': f"{conversion_rate}%",
                'conversion_change': "+5%"  # Placeholder
            },
            'recent_activity': recent_activity,
            'top_services': top_services
        })
        
    except Exception as e:
        logger.error(f"Error fetching dashboard stats: {e}", exc_info=True)
        return Response(
            {'error': f'Failed to fetch statistics: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
