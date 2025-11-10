from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db import connection
from .models import Document, Photo


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = [
        'id', 
        'title', 
        'user_link',
        'file_type', 
        'file_size_display',
        'status_badge', 
        'embeddings_count',
        'created_at'
    ]
    list_filter = ['file_type', 'processing_status', 'is_processed', 'created_at']
    search_fields = ['title', 'user_id']
    readonly_fields = [
        'created_at', 
        'updated_at', 
        'processed_at',
        'file_size',
        'embeddings_count',
        'extracted_text_preview'
    ]
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('user_id', 'title', 'file_type', 'file_path', 'file_size')
        }),
        ('Processing Status', {
            'fields': ('processing_status', 'is_processed', 'processing_error', 'processed_at')
        }),
        ('Content', {
            'fields': ('extracted_text_preview',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('metadata', 'embeddings_count'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    actions = ['reprocess_documents', 'mark_as_unprocessed']
    
    def user_link(self, obj):
        """Link to user in public schema"""
        return format_html(
            '<a href="/admin/accounts/user/{}/change/">User {}</a>',
            obj.user_id,
            obj.user_id
        )
    user_link.short_description = 'User'
    
    def file_size_display(self, obj):
        """Human-readable file size"""
        size = obj.file_size
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        else:
            return f"{size / (1024 * 1024):.1f} MB"
    file_size_display.short_description = 'Size'
    
    def status_badge(self, obj):
        """Colored status badge"""
        colors = {
            'pending': '#FFA500',
            'processing': '#2196F3',
            'completed': '#4CAF50',
            'failed': '#F44336'
        }
        color = colors.get(obj.processing_status, '#999')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.processing_status.upper()
        )
    status_badge.short_description = 'Status'
    
    def embeddings_count(self, obj):
        """Count of embeddings for this document"""
        from apps.embeddings.models import Embedding
        count = Embedding.objects.filter(
            source_type='document',
            source_id=obj.id
        ).count()
        return format_html(
            '<span style="font-weight: bold; color: {};">{} embeddings</span>',
            '#4CAF50' if count > 0 else '#F44336',
            count
        )
    embeddings_count.short_description = 'Embeddings'
    
    def extracted_text_preview(self, obj):
        """Preview of extracted text"""
        if obj.extracted_text:
            preview = obj.extracted_text[:500]
            if len(obj.extracted_text) > 500:
                preview += '...'
            return format_html('<pre style="white-space: pre-wrap;">{}</pre>', preview)
        return 'No text extracted'
    extracted_text_preview.short_description = 'Extracted Text Preview'
    
    def reprocess_documents(self, request, queryset):
        """Reprocess selected documents"""
        from .tasks import process_document
        tenant_schema = connection.schema_name
        
        for doc in queryset:
            doc.processing_status = 'pending'
            doc.is_processed = False
            doc.save()
            process_document.delay(doc.id, tenant_schema)
        
        self.message_user(request, f'{queryset.count()} documents queued for reprocessing')
    reprocess_documents.short_description = 'Reprocess selected documents'
    
    def mark_as_unprocessed(self, request, queryset):
        """Mark as unprocessed"""
        queryset.update(processing_status='pending', is_processed=False)
        self.message_user(request, f'{queryset.count()} documents marked as unprocessed')
    mark_as_unprocessed.short_description = 'Mark as unprocessed'


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'photo_preview',
        'user_link',
        'file_size_display',
        'status_badge',
        'embeddings_count',
        'has_description',
        'created_at'
    ]
    list_filter = ['processing_status', 'is_processed', 'created_at']
    search_fields = ['user_id', 'description']
    readonly_fields = [
        'created_at',
        'updated_at',
        'processed_at',
        'file_size',
        'embeddings_count',
        'photo_preview_large',
        'labels_display',
        'text_display'
    ]
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('user_id', 'file_path', 'file_size', 'photo_preview_large')
        }),
        ('Description', {
            'fields': ('description',)
        }),
        ('Processing Status', {
            'fields': ('processing_status', 'is_processed', 'processing_error', 'processed_at')
        }),
        ('Vision API Results', {
            'fields': ('labels_display', 'text_display', 'detected_objects', 'faces', 'colors'),
            'classes': ('collapse',)
        }),
        ('Analysis', {
            'fields': ('detailed_analysis', 'embeddings_count'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    actions = ['reprocess_photos', 'mark_as_unprocessed']
    
    def user_link(self, obj):
        """Link to user in public schema"""
        return format_html(
            '<a href="/admin/accounts/user/{}/change/">User {}</a>',
            obj.user_id,
            obj.user_id
        )
    user_link.short_description = 'User'
    
    def photo_preview(self, obj):
        """Small photo preview"""
        if obj.file_path:
            return format_html('<img src="{}" style="max-width: 50px; max-height: 50px;" />', obj.file_path)
        return 'No image'
    photo_preview.short_description = 'Preview'
    
    def photo_preview_large(self, obj):
        """Large photo preview"""
        if obj.file_path:
            return format_html('<img src="{}" style="max-width: 400px; max-height: 400px;" />', obj.file_path)
        return 'No image'
    photo_preview_large.short_description = 'Photo'
    
    def file_size_display(self, obj):
        """Human-readable file size"""
        size = obj.file_size
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        else:
            return f"{size / (1024 * 1024):.1f} MB"
    file_size_display.short_description = 'Size'
    
    def status_badge(self, obj):
        """Colored status badge"""
        colors = {
            'pending': '#FFA500',
            'processing': '#2196F3',
            'completed': '#4CAF50',
            'failed': '#F44336'
        }
        color = colors.get(obj.processing_status, '#999')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.processing_status.upper()
        )
    status_badge.short_description = 'Status'
    
    def has_description(self, obj):
        """Check if has user description"""
        if obj.description:
            return format_html('<span style="color: green;">✓</span>')
        return format_html('<span style="color: red;">✗</span>')
    has_description.short_description = 'Description'
    
    def embeddings_count(self, obj):
        """Count of embeddings for this photo"""
        from apps.embeddings.models import Embedding
        count = Embedding.objects.filter(
            source_type='photo',
            source_id=obj.id
        ).count()
        return format_html(
            '<span style="font-weight: bold; color: {};">{} embeddings</span>',
            '#4CAF50' if count > 0 else '#F44336',
            count
        )
    embeddings_count.short_description = 'Embeddings'
    
    def labels_display(self, obj):
        """Display detected labels"""
        if obj.labels:
            labels_html = '<br>'.join([f"• {label}" for label in obj.labels[:10]])
            return format_html('<div>{}</div>', labels_html)
        return 'No labels detected'
    labels_display.short_description = 'Detected Labels'
    
    def text_display(self, obj):
        """Display OCR text"""
        if obj.text:
            return format_html('<pre style="white-space: pre-wrap;">{}</pre>', obj.text[:500])
        return 'No text detected'
    text_display.short_description = 'OCR Text'
    
    def reprocess_photos(self, request, queryset):
        """Reprocess selected photos"""
        from .tasks import process_photo
        tenant_schema = connection.schema_name
        
        for photo in queryset:
            photo.processing_status = 'pending'
            photo.is_processed = False
            photo.save()
            process_photo.delay(photo.id, tenant_schema)
        
        self.message_user(request, f'{queryset.count()} photos queued for reprocessing')
    reprocess_photos.short_description = 'Reprocess selected photos'
    
    def mark_as_unprocessed(self, request, queryset):
        """Mark as unprocessed"""
        queryset.update(processing_status='pending', is_processed=False)
        self.message_user(request, f'{queryset.count()} photos marked as unprocessed')
    mark_as_unprocessed.short_description = 'Mark as unprocessed'

