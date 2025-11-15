from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Organization, Profile, ApiKey, Sphere, IntegrationType


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


@admin.register(Sphere)
class SphereAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'icon', 'color', 'is_active', 'order', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'slug', 'description']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['order', 'name']

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description')
        }),
        ('Display', {
            'fields': ('icon', 'color', 'order')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ['created_at', 'updated_at']


@admin.register(IntegrationType)
class IntegrationTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'integration_type', 'get_spheres', 'requires_oauth', 'is_active', 'order']
    list_filter = ['is_active', 'requires_oauth', 'supports_webhooks', 'supports_working_hours', 'spheres']
    search_fields = ['name', 'slug', 'description', 'integration_type']
    filter_horizontal = ['spheres']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['order', 'name']

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'integration_type', 'description')
        }),
        ('Spheres', {
            'fields': ('spheres',)
        }),
        ('OAuth/API Configuration', {
            'fields': ('requires_oauth', 'oauth_provider', 'api_documentation_url')
        }),
        ('Features', {
            'fields': ('supports_webhooks', 'supports_working_hours')
        }),
        ('Display', {
            'fields': ('icon_url', 'logo_url', 'color', 'order')
        }),
        ('Availability', {
            'fields': ('available_countries',),
            'description': 'Enter country codes as JSON array, e.g., ["UA", "PL", "DE"]'
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ['created_at', 'updated_at']

    def get_spheres(self, obj):
        return ", ".join([s.name for s in obj.spheres.all()])

    get_spheres.short_description = 'Spheres'
