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
    list_display = ['organization', 'plan', 'status', 'billing_cycle', 'trial_end', 'current_period_end', 'get_user_email']
    list_filter = ['status', 'billing_cycle', 'plan']
    search_fields = ['organization__name', 'organization__owner__email', 'stripe_subscription_id']
    readonly_fields = ['created_at', 'updated_at', 'stripe_subscription_id', 'stripe_customer_id']
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

    fieldsets = (
        ('Organization', {
            'fields': ('organization',)
        }),
        ('Plan & Status', {
            'fields': ('plan', 'status', 'billing_cycle')
        }),
        ('Trial Period', {
            'fields': ('trial_start', 'trial_end')
        }),
        ('Billing Period', {
            'fields': ('current_period_start', 'current_period_end')
        }),
        ('Usage', {
            'fields': ('used_messages', 'used_photos', 'used_documents', 'usage_reset_at'),
            'classes': ('collapse',)
        }),
        ('Stripe', {
            'fields': ('stripe_subscription_id', 'stripe_customer_id'),
            'classes': ('collapse',)
        }),
        ('Cancellation', {
            'fields': ('cancel_at_period_end', 'canceled_at'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['upgrade_to_starter', 'upgrade_to_professional', 'downgrade_to_free', 'activate_subscription', 'cancel_subscription']

    def get_user_email(self, obj):
        """Показує email власника організації"""
        return obj.organization.owner.email if obj.organization.owner else '-'
    get_user_email.short_description = 'User Email'
    get_user_email.admin_order_field = 'organization__owner__email'

    def upgrade_to_starter(self, request, queryset):
        """Апгрейд на Starter план"""
        from django.utils import timezone
        from datetime import timedelta

        try:
            starter_plan = Plan.objects.get(slug='starter')
        except Plan.DoesNotExist:
            self.message_user(request, 'Помилка: Starter план не знайдено в базі даних', level='error')
            return

        count = 0
        for subscription in queryset:
            subscription.plan = starter_plan
            subscription.status = 'active'
            subscription.current_period_end = timezone.now() + timedelta(days=30)
            subscription.save()
            count += 1

        self.message_user(request, f'Успішно оновлено {count} підписок на Starter план')
    upgrade_to_starter.short_description = '⬆️ Апгрейд на Starter'

    def upgrade_to_professional(self, request, queryset):
        """Апгрейд на Professional план"""
        from django.utils import timezone
        from datetime import timedelta

        try:
            professional_plan = Plan.objects.get(slug='professional')
        except Plan.DoesNotExist:
            self.message_user(request, 'Помилка: Professional план не знайдено в базі даних', level='error')
            return

        count = 0
        for subscription in queryset:
            subscription.plan = professional_plan
            subscription.status = 'active'
            subscription.current_period_end = timezone.now() + timedelta(days=30)
            subscription.save()
            count += 1

        self.message_user(request, f'Успішно оновлено {count} підписок на Professional план')
    upgrade_to_professional.short_description = '⬆️ Апгрейд на Professional'

    def downgrade_to_free(self, request, queryset):
        """Даунгрейд на Free план"""
        from django.utils import timezone
        from datetime import timedelta

        try:
            free_plan = Plan.objects.get(slug='free')
        except Plan.DoesNotExist:
            self.message_user(request, 'Помилка: Free план не знайдено в базі даних', level='error')
            return

        count = 0
        for subscription in queryset:
            subscription.plan = free_plan
            subscription.status = 'active'
            subscription.billing_cycle = 'lifetime'
            subscription.current_period_end = timezone.now() + timedelta(days=365 * 10)
            subscription.save()
            count += 1

        self.message_user(request, f'Успішно оновлено {count} підписок на Free план')
    downgrade_to_free.short_description = '⬇️ Даунгрейд на Free'

    def activate_subscription(self, request, queryset):
        """Активувати підписку"""
        count = queryset.update(status='active')
        self.message_user(request, f'Успішно активовано {count} підписок')
    activate_subscription.short_description = '✅ Активувати підписку'

    def cancel_subscription(self, request, queryset):
        """Скасувати підписку"""
        from django.utils import timezone

        count = 0
        for subscription in queryset:
            subscription.status = 'canceled'
            subscription.canceled_at = timezone.now()
            subscription.save()
            count += 1

        self.message_user(request, f'Успішно скасовано {count} підписок')
    cancel_subscription.short_description = '❌ Скасувати підписку'


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
