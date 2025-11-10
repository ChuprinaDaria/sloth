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
    list_display = ['organization', 'plan', 'status', 'billing_cycle', 'trial_end', 'current_period_end', 'get_user_email']
    list_filter = ['status', 'billing_cycle', 'plan']
    search_fields = ['organization__name', 'organization__owner__email', 'stripe_subscription_id']
    readonly_fields = ['created_at', 'updated_at', 'stripe_subscription_id', 'stripe_customer_id']
    raw_id_fields = ['organization']

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
