from django.db import models


class Prompt(models.Model):
    """
    Користувацький промпт для AI агента (в tenant schema)
    """
    user_id = models.IntegerField(db_index=True)

    # System prompt components
    role = models.TextField(
        default="You are a helpful AI assistant for a beauty salon. "
                "You help with scheduling appointments, answering questions, and providing information."
    )
    instructions = models.TextField(
        blank=True,
        help_text="Additional instructions for the AI"
    )
    context = models.TextField(
        blank=True,
        help_text="Business context, services, pricing, etc."
    )

    # Settings
    temperature = models.FloatField(default=0.7)
    max_tokens = models.IntegerField(default=500)
    model = models.CharField(max_length=100, default='gpt-4-turbo-preview')

    # Status
    is_active = models.BooleanField(default=True)
    version = models.IntegerField(default=1)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'prompts'
        verbose_name = 'Prompt'
        verbose_name_plural = 'Prompts'
        ordering = ['-created_at']

    def __str__(self):
        return f"Prompt v{self.version} for user {self.user_id}"

    def get_system_prompt(self):
        """Compile full system prompt"""
        parts = [self.role]

        if self.instructions:
            parts.append(f"\nInstructions:\n{self.instructions}")

        if self.context:
            parts.append(f"\nContext:\n{self.context}")

        return "\n".join(parts)


class Conversation(models.Model):
    """
    Розмова з AI агентом (в tenant schema)
    """
    SOURCE_CHOICES = [
        ('web', 'Web Interface'),
        ('telegram', 'Telegram'),
        ('whatsapp', 'WhatsApp'),
        ('api', 'API'),
    ]

    user_id = models.IntegerField(db_index=True)
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='web')
    external_id = models.CharField(max_length=255, blank=True)  # telegram chat_id, etc

    # Optional title
    title = models.CharField(max_length=255, blank=True)

    # Stats
    message_count = models.IntegerField(default=0)
    total_tokens = models.IntegerField(default=0)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'conversations'
        verbose_name = 'Conversation'
        verbose_name_plural = 'Conversations'
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['user_id', '-updated_at']),
            models.Index(fields=['source', 'external_id']),
        ]

    def __str__(self):
        return f"Conversation {self.id} - {self.source}"


class Message(models.Model):
    """
    Повідомлення в розмові (в tenant schema)
    """
    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
        ('system', 'System'),
    ]

    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    content = models.TextField()

    # Attachments
    photo_id = models.IntegerField(null=True, blank=True)  # Reference to Photo

    # RAG context (JSON array of embedding IDs used)
    context_used = models.JSONField(default=list, blank=True)

    # Metadata
    tokens_used = models.IntegerField(default=0)
    processing_time = models.FloatField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'messages'
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['conversation', 'created_at']),
        ]

    def __str__(self):
        return f"{self.role}: {self.content[:50]}"
