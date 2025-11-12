from django.contrib import admin
from .models import PrivacyPolicy, TermsOfService, SupportContact, AppDownloadLinks


@admin.register(PrivacyPolicy)
class PrivacyPolicyAdmin(admin.ModelAdmin):
    list_display = ['language', 'title', 'version', 'last_updated', 'is_active']
    list_filter = ['language', 'is_active']
    search_fields = ['title', 'content']
    readonly_fields = ['last_updated']

    fieldsets = (
        ('Основна інформація', {
            'fields': ('language', 'title', 'version', 'is_active')
        }),
        ('Контент', {
            'fields': ('content',),
            'classes': ('wide',)
        }),
        ('Метадані', {
            'fields': ('last_updated',),
            'classes': ('collapse',)
        }),
    )


@admin.register(TermsOfService)
class TermsOfServiceAdmin(admin.ModelAdmin):
    list_display = ['language', 'title', 'version', 'last_updated', 'is_active']
    list_filter = ['language', 'is_active']
    search_fields = ['title', 'content']
    readonly_fields = ['last_updated']

    fieldsets = (
        ('Основна інформація', {
            'fields': ('language', 'title', 'version', 'is_active')
        }),
        ('Контент', {
            'fields': ('content',),
            'classes': ('wide',)
        }),
        ('Метадані', {
            'fields': ('last_updated',),
            'classes': ('collapse',)
        }),
    )


@admin.register(SupportContact)
class SupportContactAdmin(admin.ModelAdmin):
    list_display = ['email', 'telegram', 'phone', 'working_hours', 'is_active']
    list_filter = ['is_active']

    fieldsets = (
        ('Контактна інформація', {
            'fields': ('email', 'telegram', 'phone')
        }),
        ('Режим роботи', {
            'fields': ('working_hours', 'response_time')
        }),
        ('Статус', {
            'fields': ('is_active',)
        }),
    )


@admin.register(AppDownloadLinks)
class AppDownloadLinksAdmin(admin.ModelAdmin):
    list_display = ['ios_app_id', 'android_package', 'coming_soon', 'is_active']
    list_filter = ['is_active', 'coming_soon']

    fieldsets = (
        ('iOS', {
            'fields': ('ios_app_id', 'ios_url'),
            'description': 'Введіть або App ID, або повний URL'
        }),
        ('Android', {
            'fields': ('android_package', 'android_url'),
            'description': 'Введіть або Package Name, або повний URL'
        }),
        ('Статус', {
            'fields': ('is_active', 'coming_soon')
        }),
    )

    def has_add_permission(self, request):
        # Дозволити тільки один запис
        if AppDownloadLinks.objects.exists():
            return False
        return super().has_add_permission(request)
