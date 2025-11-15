from django.contrib import admin
from .models import Integration, WebhookEvent, PhotoRecognitionProvider, UserPhotoRecognitionConfig


@admin.register(Integration)
class IntegrationAdmin(admin.ModelAdmin):
    list_display = ['integration_type', 'user_id', 'status', 'messages_received', 'messages_sent', 'created_at']
    list_filter = ['integration_type', 'status', 'created_at']
    search_fields = ['user_id']
    readonly_fields = ['created_at', 'updated_at', 'last_activity']
    ordering = ['-created_at']


@admin.register(WebhookEvent)
class WebhookEventAdmin(admin.ModelAdmin):
    list_display = ['event_type', 'integration', 'is_processed', 'created_at']
    list_filter = ['is_processed', 'event_type', 'created_at']
    readonly_fields = ['created_at', 'processed_at']
    ordering = ['-created_at']


@admin.register(PhotoRecognitionProvider)
class PhotoRecognitionProviderAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'slug',
        'cost_per_image',
        'available_in_professional_only',
        'is_active',
        'order',
        'created_at'
    ]
    list_filter = ['is_active', 'available_in_professional_only', 'requires_api_key']
    search_fields = ['name', 'slug', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['order', 'name']

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description')
        }),
        ('API Configuration', {
            'fields': ('requires_api_key', 'api_documentation_url')
        }),
        ('Pricing', {
            'fields': ('cost_per_image',)
        }),
        ('Availability', {
            'fields': ('available_in_professional_only', 'is_active', 'order')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(UserPhotoRecognitionConfig)
class UserPhotoRecognitionConfigAdmin(admin.ModelAdmin):
    list_display = [
        'user_id',
        'provider',
        'is_default',
        'is_active',
        'images_processed',
        'total_cost',
        'last_used_at',
        'created_at'
    ]
    list_filter = ['is_default', 'is_active', 'provider', 'created_at']
    search_fields = ['user_id']
    readonly_fields = [
        'created_at',
        'updated_at',
        'images_processed',
        'total_cost',
        'last_used_at',
        'get_masked_api_key'
    ]
    ordering = ['-created_at']

    fieldsets = (
        ('User Configuration', {
            'fields': ('user_id', 'provider', 'api_key_encrypted')
        }),
        ('Settings', {
            'fields': ('is_active', 'is_default')
        }),
        ('Statistics', {
            'fields': ('images_processed', 'total_cost', 'last_used_at'),
            'classes': ('collapse',)
        }),
        ('Security', {
            'fields': ('get_masked_api_key',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_masked_api_key(self, obj):
        """Display masked API key for security"""
        return obj.get_masked_key()
    get_masked_api_key.short_description = 'Masked API Key'
