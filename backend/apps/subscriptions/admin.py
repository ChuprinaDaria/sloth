from django.contrib import admin
from django.utils.html import format_html
from .models import Plan, Subscription, ActivationCode, Invoice


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'price_monthly', 'price_yearly', 'is_active', 'is_public', 'order']
    list_filter = ['is_active', 'is_public']
    search_fields = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['order', 'price_monthly']


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = [
        'organization', 
        'plan', 
        'status_badge',
        'billing_cycle', 
        'usage_display',
        'trial_end', 
        'current_period_end'
    ]
    list_filter = ['status', 'billing_cycle', 'plan']
    search_fields = ['organization__name', 'stripe_subscription_id']
    readonly_fields = [
        'created_at', 
        'updated_at',
        'usage_details',
        'documents_count',
        'embeddings_count'
    ]
    raw_id_fields = ['organization']
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('organization', 'plan', 'status', 'billing_cycle')
        }),
        ('Usage & Limits', {
            'fields': ('usage_details', 'documents_count', 'embeddings_count')
        }),
        ('Stripe', {
            'fields': ('stripe_subscription_id', 'stripe_customer_id'),
            'classes': ('collapse',)
        }),
        ('Dates', {
            'fields': ('trial_end', 'current_period_start', 'current_period_end', 'canceled_at', 'created_at', 'updated_at')
        }),
    )
    
    def status_badge(self, obj):
        """Colored status badge"""
        colors = {
            'active': '#4CAF50',
            'trialing': '#2196F3',
            'past_due': '#FF9800',
            'canceled': '#F44336',
            'incomplete': '#FFC107',
            'incomplete_expired': '#9E9E9E',
            'unpaid': '#F44336',
            'paused': '#9E9E9E'
        }
        color = colors.get(obj.status, '#999')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.status.upper()
        )
    status_badge.short_description = 'Status'
    
    def usage_display(self, obj):
        """Show usage summary"""
        usage = obj.usage.get('documents', 0)
        return format_html(
            '<span style="font-weight: bold;">{} docs</span>',
            usage
        )
    usage_display.short_description = 'Usage'
    
    def usage_details(self, obj):
        """Detailed usage information"""
        import json
        
        usage_json = json.dumps(obj.usage, indent=2)
        return format_html('<pre>{}</pre>', usage_json)
    usage_details.short_description = 'Usage Details'
    
    def documents_count(self, obj):
        """Count documents for this organization"""
        from django.db import connection
        from apps.documents.models import Document
        
        # Switch to tenant schema
        schema_name = obj.organization.schema_name
        with connection.cursor() as cursor:
            cursor.execute(f"SET search_path TO {schema_name}")
            count = Document.objects.count()
            cursor.execute("SET search_path TO public")
        
        return format_html(
            '<span style="font-weight: bold; color: #2196F3;">{} documents</span>',
            count
        )
    documents_count.short_description = 'Documents in DB'
    
    def embeddings_count(self, obj):
        """Count embeddings for this organization"""
        from django.db import connection
        from apps.embeddings.models import Embedding
        
        # Switch to tenant schema
        schema_name = obj.organization.schema_name
        with connection.cursor() as cursor:
            cursor.execute(f"SET search_path TO {schema_name}")
            count = Embedding.objects.count()
            cursor.execute("SET search_path TO public")
        
        return format_html(
            '<span style="font-weight: bold; color: #4CAF50;">{} embeddings</span>',
            count
        )
    embeddings_count.short_description = 'Embeddings in DB'


@admin.register(ActivationCode)
class ActivationCodeAdmin(admin.ModelAdmin):
    list_display = ['code', 'plan', 'duration_days', 'is_used', 'used_by', 'expires_at', 'created_at']
    list_filter = ['is_used', 'plan', 'created_at']
    search_fields = ['code']
    readonly_fields = ['code', 'used_at', 'created_at']
    raw_id_fields = ['used_by', 'created_by']

    actions = ['generate_codes']

    def generate_codes(self, request, queryset):
        # This action could be expanded to batch-generate codes
        pass

    generate_codes.short_description = "Generate activation codes"


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['id', 'subscription', 'amount', 'currency', 'status', 'period_start', 'paid_at']
    list_filter = ['status', 'created_at']
    search_fields = ['stripe_invoice_id', 'subscription__organization__name']
    readonly_fields = ['created_at', 'updated_at']
