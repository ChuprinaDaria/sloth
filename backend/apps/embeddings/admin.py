from django.contrib import admin
from django.utils.html import format_html
from django.db import connection
from .models import Embedding, VectorStore


@admin.register(Embedding)
class EmbeddingAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'source_badge',
        'source_id',
        'content_preview',
        'has_vector',
        'created_at'
    ]
    list_filter = ['source_type', 'created_at']
    search_fields = ['content', 'source_id']
    readonly_fields = [
        'created_at',
        'content_display',
        'vector_info',
        'metadata_display'
    ]
    
    fieldsets = (
        ('Source', {
            'fields': ('source_type', 'source_id')
        }),
        ('Content', {
            'fields': ('content_display',)
        }),
        ('Vector', {
            'fields': ('vector_info',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('metadata_display',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )
    
    actions = ['delete_embeddings', 'regenerate_embeddings']
    
    def source_badge(self, obj):
        """Colored source type badge"""
        colors = {
            'document': '#2196F3',
            'photo': '#E91E63',
            'message': '#9C27B0',
            'prompt': '#FF9800'
        }
        color = colors.get(obj.source_type, '#999')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.source_type.upper()
        )
    source_badge.short_description = 'Source Type'
    
    def content_preview(self, obj):
        """Short preview of content"""
        preview = obj.content[:100]
        if len(obj.content) > 100:
            preview += '...'
        return preview
    content_preview.short_description = 'Content Preview'
    
    def content_display(self, obj):
        """Full content display"""
        return format_html('<pre style="white-space: pre-wrap;">{}</pre>', obj.content)
    content_display.short_description = 'Full Content'
    
    def has_vector(self, obj):
        """Check if vector exists"""
        # Query raw SQL to check if vector column has data
        with connection.cursor() as cursor:
            cursor.execute(
                f"SELECT vector IS NOT NULL FROM {self._meta.db_table} WHERE id = %s",
                [obj.id]
            )
            result = cursor.fetchone()
            has_vector = result[0] if result else False
        
        if has_vector:
            return format_html('<span style="color: green; font-size: 20px;">✓</span>')
        return format_html('<span style="color: red; font-size: 20px;">✗</span>')
    has_vector.short_description = 'Vector'
    
    def vector_info(self, obj):
        """Vector information"""
        with connection.cursor() as cursor:
            try:
                cursor.execute(
                    f"SELECT vector IS NOT NULL FROM {self._meta.db_table} WHERE id = %s",
                    [obj.id]
                )
                result = cursor.fetchone()
                has_vector = result[0] if result else False
                
                if has_vector:
                    return format_html(
                        '<div style="color: green;">✓ Vector exists (1536 dimensions)</div>'
                    )
                else:
                    return format_html(
                        '<div style="color: red;">✗ No vector generated</div>'
                    )
            except Exception as e:
                return format_html(
                    '<div style="color: orange;">Error checking vector: {}</div>',
                    str(e)
                )
    vector_info.short_description = 'Vector Information'
    
    def metadata_display(self, obj):
        """Display metadata as formatted JSON"""
        import json
        return format_html(
            '<pre>{}</pre>',
            json.dumps(obj.metadata, indent=2, ensure_ascii=False)
        )
    metadata_display.short_description = 'Metadata'
    
    def delete_embeddings(self, request, queryset):
        """Delete selected embeddings"""
        count = queryset.count()
        queryset.delete()
        self.message_user(request, f'{count} embeddings deleted')
    delete_embeddings.short_description = 'Delete selected embeddings'
    
    def regenerate_embeddings(self, request, queryset):
        """Regenerate embeddings for selected items"""
        from apps.documents.models import Document, Photo
        from apps.documents.tasks import process_document, process_photo
        tenant_schema = connection.schema_name
        
        count = 0
        for embedding in queryset:
            if embedding.source_type == 'document':
                try:
                    doc = Document.objects.get(id=embedding.source_id)
                    doc.processing_status = 'pending'
                    doc.is_processed = False
                    doc.save()
                    process_document.delay(doc.id, tenant_schema)
                    count += 1
                except Document.DoesNotExist:
                    pass
            elif embedding.source_type == 'photo':
                try:
                    photo = Photo.objects.get(id=embedding.source_id)
                    photo.processing_status = 'pending'
                    photo.is_processed = False
                    photo.save()
                    process_photo.delay(photo.id, tenant_schema)
                    count += 1
                except Photo.DoesNotExist:
                    pass
        
        self.message_user(request, f'{count} items queued for reprocessing')
    regenerate_embeddings.short_description = 'Regenerate embeddings'


@admin.register(VectorStore)
class VectorStoreAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'name',
        'embedding_model',
        'chunk_size',
        'chunk_overlap',
        'total_embeddings',
        'last_updated'
    ]
    list_filter = ['embedding_model', 'last_updated']
    search_fields = ['name', 'description']
    readonly_fields = ['total_embeddings', 'last_updated', 'created_at']
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'description')
        }),
        ('Settings', {
            'fields': ('embedding_model', 'chunk_size', 'chunk_overlap')
        }),
        ('Statistics', {
            'fields': ('total_embeddings', 'last_updated', 'created_at')
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Update total_embeddings count
        for vs in qs:
            vs.total_embeddings = Embedding.objects.count()
            vs.save()
        return qs

