from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Organization, Profile, ApiKey


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ['name', 'domain', 'schema_name', 'owner', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'domain', 'schema_name']
    readonly_fields = ['schema_name', 'created_at', 'updated_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'domain', 'schema_name', 'owner')
        }),
        ('Storage', {
            'fields': ('max_storage_mb', 'used_storage_mb')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'organization', 'referral_code', 'is_active', 'created_at']
    list_filter = ['is_active', 'is_staff', 'language', 'created_at']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'referral_code']

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('organization', 'phone', 'avatar', 'language')
        }),
        ('Referral', {
            'fields': ('referral_code', 'referred_by')
        }),
    )

    readonly_fields = ['referral_code', 'created_at', 'updated_at']


@admin.register(ApiKey)
class ApiKeyAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'key_preview', 'is_active', 'requests_count', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'user__email', 'key']
    readonly_fields = ['key', 'requests_count', 'last_used_at', 'created_at']

    def key_preview(self, obj):
        return f"{obj.key[:8]}..."

    key_preview.short_description = 'Key Preview'
