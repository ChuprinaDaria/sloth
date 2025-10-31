from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class Document(models.Model):
    """
    Завантажені документи (в tenant schema)
    """
    TYPE_CHOICES = [
        ('pdf', 'PDF'),
        ('docx', 'Word Document'),
        ('txt', 'Text File'),
        ('xlsx', 'Excel'),
        ('csv', 'CSV'),
    ]

    user_id = models.IntegerField(db_index=True)  # Reference to User from public schema
    title = models.CharField(max_length=255)
    file_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    file_path = models.CharField(max_length=500)  # S3 URL or local path
    file_size = models.IntegerField()  # bytes

    # Processing status
    is_processed = models.BooleanField(default=False)
    processing_status = models.CharField(max_length=20, default='pending')  # pending, processing, completed, failed
    processing_error = models.TextField(blank=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    # Extracted content
    extracted_text = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'documents'
        verbose_name = 'Document'
        verbose_name_plural = 'Documents'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user_id', '-created_at']),
            models.Index(fields=['processing_status']),
        ]

    def __str__(self):
        return self.title


class Photo(models.Model):
    """
    Завантажені фото (в tenant schema)
    """
    user_id = models.IntegerField(db_index=True)
    file_path = models.CharField(max_length=500)
    file_size = models.IntegerField()

    # Vision API results
    is_processed = models.BooleanField(default=False)
    processing_status = models.CharField(max_length=20, default='pending')
    processing_error = models.TextField(blank=True)

    # Google Vision results
    labels = models.JSONField(default=list, blank=True)  # detected labels
    text = models.TextField(blank=True)  # OCR text
    objects = models.JSONField(default=list, blank=True)  # detected objects
    faces = models.JSONField(default=list, blank=True)  # face detection
    colors = models.JSONField(default=list, blank=True)  # dominant colors

    # Metadata
    metadata = models.JSONField(default=dict, blank=True)

    # Timestamps
    processed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'photos'
        verbose_name = 'Photo'
        verbose_name_plural = 'Photos'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user_id', '-created_at']),
        ]

    def __str__(self):
        return f"Photo {self.id} - {self.created_at}"


class ProcessingJob(models.Model):
    """
    Celery задачі обробки (в tenant schema)
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    celery_task_id = models.CharField(max_length=255, unique=True, db_index=True)

    # Generic relation to Document or Photo
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    progress = models.IntegerField(default=0)  # 0-100
    error_message = models.TextField(blank=True)

    # Timestamps
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'processing_jobs'
        verbose_name = 'Processing Job'
        verbose_name_plural = 'Processing Jobs'
        ordering = ['-created_at']

    def __str__(self):
        return f"Job {self.celery_task_id} - {self.status}"
