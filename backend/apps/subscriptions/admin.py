from django.contrib import admin
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
    list_display = ['organization', 'plan', 'status', 'billing_cycle', 'trial_end', 'current_period_end']
    list_filter = ['status', 'billing_cycle', 'plan']
    search_fields = ['organization__name', 'stripe_subscription_id']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['organization']


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
