from django.db import models


class Prompt(models.Model):
    """
    Користувацький промпт для AI агента (в tenant schema)
    """
    user_id = models.IntegerField(db_index=True)

    # System prompt components
    role = models.TextField(
        default="Ти - віртуальний асистент салону краси, але спілкуєшся як жива людина. "
                "Твоя мета - допомогти клієнту, запропонувати послуги та записати на зручний час. "
                "Будь дружньою, емпатичною та проактивною. Розмовляй природно українською мовою."
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
        """Compile full system prompt with natural communication style"""
        parts = [self.role]

        # Add natural communication guidelines
        parts.append("""
ВАЖЛИВО - Поводься як жива людина:
- НЕ використовуй фрази типу "як AI асистент", "я програма", "я бот"
- Спілкуйся природно, з емоціями: "О, як цікаво!", "Розумію вас!", "Чудова ідея!"
- Використовуй емодзі в міру: 😊 ✨ 💇‍♀️ 💅
- Задавай уточнюючі питання щоб краще зрозуміти потреби
- Пропонуй конкретні дії: "Хочете я запишу вас на цей тиждень?"
- Будь проактивною: якщо бачиш що клієнт зацікавлений - одразу пропонуй записатися
        """)

        if self.instructions:
            parts.append(f"\nДодаткові інструкції:\n{self.instructions}")

        if self.context:
            parts.append(f"\nІнформація про салон:\n{self.context}")

        # Add proactive behavior instructions
        parts.append("""
ПРОАКТИВНА ПОВЕДІНКА:
1. Якщо клієнт запитує про послугу → одразу запропонуй записатися
2. Якщо клієнт надіслав фото → проаналізуй, покажи схожі роботи, запропонуй час
3. Якщо обговорюєте деталі → запитай email для підтвердження запису
4. Якщо клієнт згоден → використовуй функцію book_appointment
5. Завжди пропонуй конкретні дати та час, а не загальні фрази

ЗАБОРОНЕНО:
- Казати що ти робот/AI/програма
- Вибачатися за те що ти не людина
- Говорити що не можеш щось зробити (спробуй або запропонуй альтернативу)
        """)

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


class VoiceSettings(models.Model):
    """
    Налаштування голосу для AI агента (в tenant schema)
    """
    VOICE_CHOICES = [
        ('alloy', 'Alloy - Neutral'),
        ('echo', 'Echo - Male'),
        ('fable', 'Fable - British Male'),
        ('onyx', 'Onyx - Deep Male'),
        ('nova', 'Nova - Female'),
        ('shimmer', 'Shimmer - Soft Female'),
    ]

    user_id = models.IntegerField(db_index=True, unique=True)

    # Voice settings
    voice_name = models.CharField(max_length=50, choices=VOICE_CHOICES, default='nova')

    # Voice cloning (for premium users)
    is_cloned = models.BooleanField(default=False)
    cloned_voice_id = models.CharField(max_length=255, blank=True)  # ElevenLabs voice ID
    cloned_voice_sample_path = models.CharField(max_length=500, blank=True)  # Path to sample audio

    # TTS settings
    tts_enabled = models.BooleanField(default=True)
    tts_speed = models.FloatField(default=1.0)  # 0.25 to 4.0

    # STT settings
    stt_enabled = models.BooleanField(default=True)
    auto_detect_language = models.BooleanField(default=True)
    preferred_language = models.CharField(max_length=10, default='uk')  # uk, en, pl, de

    # Messenger-specific settings
    telegram_voice_enabled = models.BooleanField(default=True)
    whatsapp_voice_enabled = models.BooleanField(default=True)
    web_voice_enabled = models.BooleanField(default=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'voice_settings'
        verbose_name = 'Voice Settings'
        verbose_name_plural = 'Voice Settings'

    def __str__(self):
        return f"Voice settings for user {self.user_id}"

    def get_voice_name(self):
        """Get voice name for TTS"""
        if self.is_cloned and self.cloned_voice_id:
            return self.cloned_voice_id
        return self.voice_name


class VoiceMessage(models.Model):
    """
    Голосові повідомлення (в tenant schema)
    """
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name='voice_messages'
    )

    # Audio files
    audio_file_path = models.CharField(max_length=500)  # Original or generated audio
    audio_duration = models.FloatField(default=0.0)  # seconds
    audio_format = models.CharField(max_length=10, default='mp3')  # mp3, ogg, wav

    # Transcription (if from user)
    transcribed_text = models.TextField(blank=True)
    detected_language = models.CharField(max_length=10, blank=True)

    # Generation metadata (if generated by AI)
    is_generated = models.BooleanField(default=False)
    voice_used = models.CharField(max_length=50, blank=True)
    generation_time = models.FloatField(null=True, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'voice_messages'
        verbose_name = 'Voice Message'
        verbose_name_plural = 'Voice Messages'
        ordering = ['created_at']

    def __str__(self):
        return f"Voice message for {self.message_id}"
