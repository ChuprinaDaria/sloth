from django.db import models


class ManualCategory(models.Model):
    """
    Категорії мануалів (спільна для всіх tenant)
    """
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    icon = models.CharField(max_length=50, blank=True)  # Lucide icon name
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'manual_categories'
        verbose_name = 'Manual Category'
        verbose_name_plural = 'Manual Categories'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class Manual(models.Model):
    """
    Мануали/інструкції (в tenant schema)
    """
    INTEGRATION_CHOICES = [
        ('telegram', 'Telegram'),
        ('whatsapp', 'WhatsApp'),
        ('instagram', 'Instagram'),
        ('calendar', 'Google Calendar'),
        ('sheets', 'Google Sheets'),
        ('general', 'General'),
    ]

    # Basic info
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    description = models.TextField(blank=True)

    # Category
    category = models.ForeignKey(
        ManualCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='manuals'
    )
    integration_type = models.CharField(
        max_length=50,
        choices=INTEGRATION_CHOICES,
        default='general'
    )

    # Content
    content = models.TextField(help_text='Markdown or HTML content')

    # Video
    video_url = models.URLField(
        max_length=500,
        blank=True,
        help_text='YouTube, Vimeo, or direct video URL'
    )
    video_thumbnail = models.URLField(max_length=500, blank=True)

    # Multilingual support
    language = models.CharField(
        max_length=5,
        default='en',
        choices=[
            ('en', 'English'),
            ('uk', 'Українська'),
            ('pl', 'Polski'),
            ('de', 'Deutsch'),
        ]
    )

    # Organization
    order = models.IntegerField(default=0)
    is_published = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)

    # Tags
    tags = models.JSONField(default=list, blank=True)

    # Metadata
    metadata = models.JSONField(default=dict, blank=True)

    # Stats
    views_count = models.IntegerField(default=0)
    helpful_count = models.IntegerField(default=0)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'manuals'
        verbose_name = 'Manual'
        verbose_name_plural = 'Manuals'
        ordering = ['order', '-created_at']
        indexes = [
            models.Index(fields=['language', 'is_published']),
            models.Index(fields=['integration_type', 'is_published']),
            models.Index(fields=['slug']),
        ]
        unique_together = [['slug', 'language']]

    def __str__(self):
        return f"{self.title} ({self.language})"


class ManualAttachment(models.Model):
    """
    Додаткові файли до мануалів (скріншоти, PDF тощо)
    """
    manual = models.ForeignKey(
        Manual,
        on_delete=models.CASCADE,
        related_name='attachments'
    )

    title = models.CharField(max_length=255)
    file_path = models.CharField(max_length=500)  # S3 URL or local path
    file_type = models.CharField(max_length=50)  # image, pdf, etc.
    file_size = models.IntegerField()  # bytes

    order = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'manual_attachments'
        verbose_name = 'Manual Attachment'
        verbose_name_plural = 'Manual Attachments'
        ordering = ['order', '-created_at']

    def __str__(self):
        return f"{self.title} - {self.manual.title}"


class ManualFeedback(models.Model):
    """
    Зворотній зв'язок по мануалам від користувачів
    """
    manual = models.ForeignKey(
        Manual,
        on_delete=models.CASCADE,
        related_name='feedback'
    )
    user_id = models.IntegerField(db_index=True)

    is_helpful = models.BooleanField(default=True)
    comment = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'manual_feedback'
        verbose_name = 'Manual Feedback'
        verbose_name_plural = 'Manual Feedback'
        ordering = ['-created_at']
        unique_together = [['manual', 'user_id']]

    def __str__(self):
        return f"Feedback for {self.manual.title} by user {self.user_id}"
