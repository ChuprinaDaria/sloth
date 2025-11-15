from django.contrib import admin
from .models import ManualCategory, Manual, ManualAttachment, ManualFeedback


@admin.register(ManualCategory)
class ManualCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'icon', 'order', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['order', 'name']


class ManualAttachmentInline(admin.TabularInline):
    model = ManualAttachment
    extra = 1
    fields = ['title', 'file_path', 'file_type', 'file_size', 'order']


class ManualFeedbackInline(admin.TabularInline):
    model = ManualFeedback
    extra = 0
    readonly_fields = ['user_id', 'is_helpful', 'comment', 'created_at']
    can_delete = False


@admin.register(Manual)
class ManualAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'language',
        'integration_type',
        'category',
        'is_published',
        'is_featured',
        'order',
        'views_count',
        'helpful_count',
        'created_at'
    ]
    list_filter = ['language', 'integration_type', 'is_published', 'is_featured', 'category']
    search_fields = ['title', 'description', 'content', 'tags']
    prepopulated_fields = {'slug': ('title',)}
    ordering = ['order', '-created_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'description', 'language')
        }),
        ('Organization', {
            'fields': ('category', 'integration_type', 'order', 'tags')
        }),
        ('Content', {
            'fields': ('content',),
            'classes': ('wide',)
        }),
        ('Video', {
            'fields': ('video_url', 'video_thumbnail'),
            'classes': ('collapse',)
        }),
        ('Publishing', {
            'fields': ('is_published', 'is_featured', 'published_at')
        }),
        ('Statistics', {
            'fields': ('views_count', 'helpful_count'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
    )

    inlines = [ManualAttachmentInline, ManualFeedbackInline]

    readonly_fields = ['views_count', 'helpful_count']

    def save_model(self, request, obj, form, change):
        if obj.is_published and not obj.published_at:
            from django.utils import timezone
            obj.published_at = timezone.now()
        super().save_model(request, obj, form, change)


@admin.register(ManualAttachment)
class ManualAttachmentAdmin(admin.ModelAdmin):
    list_display = ['title', 'manual', 'file_type', 'file_size', 'order', 'created_at']
    list_filter = ['file_type']
    search_fields = ['title', 'manual__title']
    ordering = ['manual', 'order', '-created_at']


@admin.register(ManualFeedback)
class ManualFeedbackAdmin(admin.ModelAdmin):
    list_display = ['manual', 'user_id', 'is_helpful', 'created_at']
    list_filter = ['is_helpful', 'created_at']
    search_fields = ['manual__title', 'comment']
    readonly_fields = ['manual', 'user_id', 'is_helpful', 'comment', 'created_at']
    ordering = ['-created_at']
