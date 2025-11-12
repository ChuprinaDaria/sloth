from django.contrib import admin
from django.utils.html import format_html
from .models import Prompt, Conversation, Message, VoiceSettings, VoiceMessage


@admin.register(Prompt)
class PromptAdmin(admin.ModelAdmin):
    """Адміністрація промптів користувачів"""
    list_display = [
        'id',
        'user_link',
        'version',
        'is_active_badge',
        'model',
        'temperature',
        'max_tokens',
        'role_preview',
        'created_at',
        'updated_at'
    ]
    list_filter = ['is_active', 'model', 'created_at', 'updated_at']
    search_fields = ['user_id', 'role', 'instructions', 'context']
    readonly_fields = [
        'created_at',
        'updated_at',
        'version',
        'full_prompt_preview',
        'user_link'
    ]
    
    fieldsets = (
        ('Користувач', {
            'fields': ('user_link', 'user_id', 'is_active', 'version')
        }),
        ('Основні налаштування', {
            'fields': ('role', 'instructions', 'context')
        }),
        ('AI Параметри', {
            'fields': ('model', 'temperature', 'max_tokens')
        }),
        ('Повний промпт (preview)', {
            'fields': ('full_prompt_preview',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    actions = ['activate_prompts', 'deactivate_prompts']
    
    def user_link(self, obj):
        """Посилання на користувача"""
        return format_html(
            '<a href="/admin/accounts/user/{}/change/" style="font-weight: bold;">User {}</a>',
            obj.user_id,
            obj.user_id
        )
    user_link.short_description = 'Користувач'
    
    def is_active_badge(self, obj):
        """Кольоровий бейдж статусу"""
        if obj.is_active:
            return format_html(
                '<span style="background-color: #4CAF50; color: white; padding: 3px 10px; border-radius: 3px; font-weight: bold;">АКТИВНИЙ</span>'
            )
        return format_html(
            '<span style="background-color: #999; color: white; padding: 3px 10px; border-radius: 3px;">НЕАКТИВНИЙ</span>'
        )
    is_active_badge.short_description = 'Статус'
    
    def role_preview(self, obj):
        """Превью ролі"""
        if obj.role:
            preview = obj.role[:100]
            if len(obj.role) > 100:
                preview += '...'
            return format_html('<span title="{}">{}</span>', obj.role, preview)
        return '-'
    role_preview.short_description = 'Роль (preview)'
    
    def full_prompt_preview(self, obj):
        """Повний промпт для перегляду"""
        full_prompt = obj.get_system_prompt()
        return format_html(
            '<div style="max-height: 500px; overflow-y: auto; background: #f5f5f5; padding: 15px; border-radius: 5px;">'
            '<pre style="white-space: pre-wrap; font-family: monospace; font-size: 12px;">{}</pre>'
            '</div>',
            full_prompt
        )
    full_prompt_preview.short_description = 'Повний системний промпт'
    
    def activate_prompts(self, request, queryset):
        """Активувати вибрані промпти"""
        queryset.update(is_active=True)
        self.message_user(request, f'{queryset.count()} промптів активовано')
    activate_prompts.short_description = 'Активувати вибрані промпти'
    
    def deactivate_prompts(self, request, queryset):
        """Деактивувати вибрані промпти"""
        queryset.update(is_active=False)
        self.message_user(request, f'{queryset.count()} промптів деактивовано')
    deactivate_prompts.short_description = 'Деактивувати вибрані промпти'


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    """Адміністрація розмов"""
    list_display = [
        'id',
        'user_link',
        'source',
        'title',
        'message_count',
        'total_tokens',
        'created_at',
        'updated_at'
    ]
    list_filter = ['source', 'created_at', 'updated_at']
    search_fields = ['user_id', 'title', 'external_id']
    readonly_fields = ['created_at', 'updated_at', 'user_link']
    
    def user_link(self, obj):
        """Посилання на користувача"""
        return format_html(
            '<a href="/admin/accounts/user/{}/change/">User {}</a>',
            obj.user_id,
            obj.user_id
        )
    user_link.short_description = 'Користувач'


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """Адміністрація повідомлень"""
    list_display = [
        'id',
        'conversation',
        'role_badge',
        'content_preview',
        'tokens_used',
        'created_at'
    ]
    list_filter = ['role', 'created_at']
    search_fields = ['content', 'conversation__title']
    readonly_fields = ['created_at', 'content_full']
    
    def role_badge(self, obj):
        """Кольоровий бейдж ролі"""
        colors = {
            'user': '#2196F3',
            'assistant': '#4CAF50',
            'system': '#FF9800'
        }
        color = colors.get(obj.role, '#999')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.role.upper()
        )
    role_badge.short_description = 'Роль'
    
    def content_preview(self, obj):
        """Превью контенту"""
        if obj.content:
            preview = obj.content[:100]
            if len(obj.content) > 100:
                preview += '...'
            return format_html('<span title="{}">{}</span>', obj.content, preview)
        return '-'
    content_preview.short_description = 'Контент'
    
    def content_full(self, obj):
        """Повний контент"""
        return format_html('<pre style="white-space: pre-wrap;">{}</pre>', obj.content)
    content_full.short_description = 'Повний контент'

