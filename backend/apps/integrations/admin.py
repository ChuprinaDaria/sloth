from django.contrib import admin
from django.utils.html import format_html
from .models import Integration, InstagramPost


@admin.register(Integration)
class IntegrationAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_id', 'integration_type', 'status', 'created_at']
    list_filter = ['integration_type', 'status', 'created_at']
    search_fields = ['user_id', 'integration_type']


@admin.register(InstagramPost)
class InstagramPostAdmin(admin.ModelAdmin):
    """Адміністрація Instagram постів з ембедінгами"""
    list_display = [
        'id',
        'post_preview',
        'user_link',
        'caption_preview',
        'media_type',
        'metrics_display',
        'has_embedding',
        'hashtags_count',
        'posted_at',
        'created_at'
    ]
    list_filter = ['media_type', 'posted_at', 'created_at']
    search_fields = ['post_id', 'caption', 'user_id']
    readonly_fields = [
        'created_at',
        'updated_at',
        'post_preview_large',
        'embedding_info',
        'metrics_display',
        'hashtags_display'
    ]
    
    fieldsets = (
        ('Основна інформація', {
            'fields': ('user_link', 'user_id', 'post_id', 'media_type', 'post_preview_large')
        }),
        ('Контент', {
            'fields': ('caption', 'permalink', 'media_url')
        }),
        ('Метрики', {
            'fields': ('metrics_display', 'likes', 'comments', 'engagement', 'impressions', 'reach')
        }),
        ('Аналіз', {
            'fields': ('hashtags_display', 'embedding_info'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('posted_at', 'created_at', 'updated_at')
        }),
    )
    
    def user_link(self, obj):
        """Посилання на користувача"""
        return format_html(
            '<a href="/admin/accounts/user/{}/change/" style="font-weight: bold;">User {}</a>',
            obj.user_id,
            obj.user_id
        )
    user_link.short_description = 'Користувач'
    
    def post_preview(self, obj):
        """Мініатюра поста"""
        if obj.media_url:
            if obj.media_type == 'VIDEO':
                return format_html(
                    '<div style="width: 50px; height: 50px; background: #000; color: white; display: flex; align-items: center; justify-content: center; border-radius: 4px;">'
                    '▶️'
                    '</div>'
                )
            return format_html(
                '<a href="{}" target="_blank">'
                '<img src="{}" style="max-width: 50px; max-height: 50px; border-radius: 4px; object-fit: cover;" />'
                '</a>',
                obj.permalink or obj.media_url,
                obj.media_url
            )
        return format_html('<span style="color: #999;">No media</span>')
    post_preview.short_description = 'Preview'
    
    def post_preview_large(self, obj):
        """Великий превью поста"""
        if obj.media_url:
            if obj.media_type == 'VIDEO':
                return format_html(
                    '<div style="text-align: center; padding: 20px; background: #f5f5f5; border-radius: 8px;">'
                    '<p style="font-size: 48px; margin: 0;">▶️</p>'
                    '<p style="margin-top: 10px; color: #666;">Video Post</p>'
                    '<a href="{}" target="_blank" style="color: #007bff;">View on Instagram</a>'
                    '</div>',
                    obj.permalink or obj.media_url
                )
            return format_html(
                '<div style="text-align: center;">'
                '<a href="{}" target="_blank">'
                '<img src="{}" style="max-width: 100%; max-height: 500px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); object-fit: contain;" />'
                '</a>'
                '<p style="margin-top: 10px; color: #666;">Click to open on Instagram</p>'
                '</div>',
                obj.permalink or obj.media_url,
                obj.media_url
            )
        return format_html('<div style="color: #999; padding: 20px; text-align: center;">No media available</div>')
    post_preview_large.short_description = 'Media Preview'
    
    def caption_preview(self, obj):
        """Превью підпису"""
        if obj.caption:
            preview = obj.caption[:100]
            if len(obj.caption) > 100:
                preview += '...'
            return format_html('<span title="{}">{}</span>', obj.caption, preview)
        return format_html('<span style="color: #999;">No caption</span>')
    caption_preview.short_description = 'Caption'
    
    def metrics_display(self, obj):
        """Відображення метрик"""
        return format_html(
            '<div style="font-size: 12px;">'
            '<div>❤️ {}</div>'
            '<div>💬 {}</div>'
            '<div>📊 Engagement: {}</div>'
            '<div>👁️ Impressions: {}</div>'
            '<div>📈 Reach: {}</div>'
            '</div>',
            obj.likes,
            obj.comments,
            obj.engagement,
            obj.impressions,
            obj.reach
        )
    metrics_display.short_description = 'Metrics'
    
    def has_embedding(self, obj):
        """Перевірка наявності ембедінгу"""
        if obj.embedding and isinstance(obj.embedding, list) and len(obj.embedding) > 0:
            return format_html(
                '<span style="background-color: #4CAF50; color: white; padding: 3px 10px; border-radius: 3px; font-weight: bold;">'
                '✓ ЕМБЕДІНГ ({})'
                '</span>',
                len(obj.embedding)
            )
        return format_html(
            '<span style="background-color: #F44336; color: white; padding: 3px 10px; border-radius: 3px;">'
            '✗ НЕМАЄ'
            '</span>'
        )
    has_embedding.short_description = 'Embedding'
    
    def embedding_info(self, obj):
        """Детальна інформація про ембедінґ"""
        if obj.embedding and isinstance(obj.embedding, list) and len(obj.embedding) > 0:
            # Показуємо перші 10 значень для оцінки якості
            preview = obj.embedding[:10]
            return format_html(
                '<div style="background: #f5f5f5; padding: 15px; border-radius: 5px; max-height: 300px; overflow-y: auto;">'
                '<p><strong>Розмір вектора:</strong> {}</p>'
                '<p><strong>Перші 10 значень (для оцінки якості):</strong></p>'
                '<pre style="white-space: pre-wrap; font-family: monospace; font-size: 11px;">{}</pre>'
                '<p style="color: #666; font-size: 12px; margin-top: 10px;">'
                'Ці значення використовуються для пошуку схожих постів через cosine similarity'
                '</p>'
                '</div>',
                len(obj.embedding),
                ', '.join([f'{val:.6f}' for val in preview])
            )
        return format_html('<span style="color: #999;">Ембедінґ не створено</span>')
    embedding_info.short_description = 'Інформація про ембедінґ'
    
    def hashtags_count(self, obj):
        """Кількість хештегів"""
        if obj.hashtags and isinstance(obj.hashtags, list):
            return len(obj.hashtags)
        return 0
    hashtags_count.short_description = 'Hashtags'
    
    def hashtags_display(self, obj):
        """Відображення хештегів"""
        if obj.hashtags and isinstance(obj.hashtags, list) and len(obj.hashtags) > 0:
            hashtags_html = ' '.join([f'<span style="background: #E3F2FD; padding: 2px 8px; border-radius: 3px; margin: 2px; display: inline-block;">#{tag}</span>' for tag in obj.hashtags[:20]])
            return format_html('<div>{}</div>', hashtags_html)
        return format_html('<span style="color: #999;">Немає хештегів</span>')
    hashtags_display.short_description = 'Hashtags'

