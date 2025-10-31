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
    """Test chat in sandbox (doesn't save to history)"""
    message = request.data.get('message')

    if not message:
        return Response({'error': 'Message is required'}, status=status.HTTP_400_BAD_REQUEST)

    agent = AgentService(
        user_id=request.user.id,
        tenant_schema=request.user.organization.schema_name
    )

    # Create temporary conversation
    conversation = agent.create_conversation(source='web')

    try:
        result = agent.chat(
            conversation_id=conversation.id,
            user_message=message
        )

        # Delete test conversation
        conversation.delete()

        return Response({
            'message': result['message'],
            'tokens_used': result['tokens_used']
        })

    except Exception as e:
        conversation.delete()
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
