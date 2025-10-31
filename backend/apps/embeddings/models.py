from django.db import models


class Embedding(models.Model):
    """
    Векторні представлення тексту (в tenant schema, використовує pgvector)
    """
    SOURCE_CHOICES = [
        ('document', 'Document'),
        ('photo', 'Photo'),
        ('message', 'Message'),
        ('prompt', 'Prompt'),
    ]

    # Source tracking
    source_type = models.CharField(max_length=20, choices=SOURCE_CHOICES, db_index=True)
    source_id = models.IntegerField(db_index=True)

    # Content
    content = models.TextField()  # оригінальний текст

    # Vector (pgvector extension) - dimension 1536 for OpenAI ada-002
    # This will be created with raw SQL since Django doesn't natively support vector type
    # vector = vector(1536)

    # Metadata
    metadata = models.JSONField(default=dict, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'embeddings'
        verbose_name = 'Embedding'
        verbose_name_plural = 'Embeddings'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['source_type', 'source_id']),
        ]

    def __str__(self):
        return f"{self.source_type}:{self.source_id} - {self.content[:50]}"


class VectorStore(models.Model):
    """
    Налаштування векторного сховища (в tenant schema)
    """
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    # Settings
    embedding_model = models.CharField(max_length=100, default='text-embedding-ada-002')
    chunk_size = models.IntegerField(default=1000)
    chunk_overlap = models.IntegerField(default=200)

    # Stats
    total_embeddings = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'vector_stores'
        verbose_name = 'Vector Store'
        verbose_name_plural = 'Vector Stores'

    def __str__(self):
        return self.name
