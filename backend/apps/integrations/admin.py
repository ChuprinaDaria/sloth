from django.contrib import admin
from .models import Integration, WebhookEvent, IntegrationWorkingHours


class IntegrationWorkingHoursInline(admin.TabularInline):
    model = IntegrationWorkingHours
    extra = 0


@admin.register(Integration)
class IntegrationAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_id', 'integration_type_slug', 'status', 'messages_sent', 'messages_received', 'last_activity']
    list_filter = ['status', 'integration_type_slug', 'created_at']
    search_fields = ['user_id', 'integration_type_slug']
    readonly_fields = ['messages_sent', 'messages_received', 'last_activity', 'created_at', 'updated_at']
    inlines = [IntegrationWorkingHoursInline]

    fieldsets = (
        ('Basic Information', {
            'fields': ('user_id', 'integration_type_id', 'integration_type_slug', 'status')
        }),
        ('Settings', {
            'fields': ('settings',)
        }),
        ('Statistics', {
            'fields': ('messages_sent', 'messages_received', 'last_activity')
        }),
        ('Errors', {
            'fields': ('error_message', 'error_count'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(WebhookEvent)
class WebhookEventAdmin(admin.ModelAdmin):
    list_display = ['id', 'integration', 'event_type', 'is_processed', 'processed_at', 'created_at']
    list_filter = ['is_processed', 'event_type', 'created_at']
    search_fields = ['event_type', 'integration__user_id']
    readonly_fields = ['created_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('integration', 'event_type', 'payload')
        }),
        ('Processing', {
            'fields': ('is_processed', 'processed_at', 'error_message')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(IntegrationWorkingHours)
class IntegrationWorkingHoursAdmin(admin.ModelAdmin):
    list_display = ['integration', 'weekday', 'start_time', 'end_time', 'is_enabled']
    list_filter = ['weekday', 'is_enabled', 'created_at']
    search_fields = ['integration__user_id', 'integration__integration_type_slug']

    fieldsets = (
        ('Integration', {
            'fields': ('integration',)
        }),
        ('Schedule', {
            'fields': ('weekday', 'start_time', 'end_time', 'is_enabled')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ['created_at', 'updated_at']
