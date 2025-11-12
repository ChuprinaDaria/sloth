from django.contrib import admin
from django.utils.html import format_html
from .models import ReferralCode, Referral, ReferralReward, ReferralTrial


@admin.register(ReferralCode)
class ReferralCodeAdmin(admin.ModelAdmin):
    list_display = ['code', 'user_email', 'total_signups', 'active_referrals', 'created_at']
    search_fields = ['code', 'user__email']
    readonly_fields = ['code', 'created_at', 'updated_at']
    ordering = ['-active_referrals', '-total_signups']

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User'
    user_email.admin_order_field = 'user__email'


@admin.register(Referral)
class ReferralAdmin(admin.ModelAdmin):
    list_display = ['referrer_email', 'referred_email', 'status', 'created_at', 'activated_at']
    list_filter = ['status', 'created_at']
    search_fields = ['referrer__email', 'referred__email']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'

    actions = ['mark_as_active', 'mark_as_inactive']

    def referrer_email(self, obj):
        return obj.referrer.email
    referrer_email.short_description = 'Referrer'
    referrer_email.admin_order_field = 'referrer__email'

    def referred_email(self, obj):
        return obj.referred.email
    referred_email.short_description = 'Referred'
    referred_email.admin_order_field = 'referred__email'

    def mark_as_active(self, request, queryset):
        """Позначити реферали як активні"""
        from django.utils import timezone

        count = 0
        for referral in queryset:
            if referral.status != 'active':
                referral.status = 'active'
                if not referral.activated_at:
                    referral.activated_at = timezone.now()
                referral.save()
                count += 1

                # Оновлюємо статистику реферера
                from .utils import update_referral_stats
                update_referral_stats(referral.referrer)

        self.message_user(request, f'Позначено {count} рефералів як активні')
    mark_as_active.short_description = 'Позначити як активні'

    def mark_as_inactive(self, request, queryset):
        """Позначити реферали як неактивні"""
        count = queryset.update(status='inactive')

        # Оновлюємо статистику для всіх рефереров
        from .utils import update_referral_stats
        for referral in queryset:
            update_referral_stats(referral.referrer)

        self.message_user(request, f'Позначено {count} рефералів як неактивні')
    mark_as_inactive.short_description = 'Позначити як неактивні'


@admin.register(ReferralReward)
class ReferralRewardAdmin(admin.ModelAdmin):
    list_display = ['user_email', 'reward_type', 'referral_count', 'old_plan', 'new_plan', 'granted_at']
    list_filter = ['reward_type', 'granted_at']
    search_fields = ['user__email']
    readonly_fields = ['granted_at']
    date_hierarchy = 'granted_at'

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User'
    user_email.admin_order_field = 'user__email'


@admin.register(ReferralTrial)
class ReferralTrialAdmin(admin.ModelAdmin):
    list_display = ['user_email', 'referrer_email', 'trial_plan', 'trial_start', 'trial_end', 'is_active_display']
    list_filter = ['is_active', 'trial_start', 'trial_end']
    search_fields = ['user__email', 'referrer__email']
    readonly_fields = ['trial_start', 'reverted_at']
    date_hierarchy = 'trial_start'

    actions = ['revert_trials_now']

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User'
    user_email.admin_order_field = 'user__email'

    def referrer_email(self, obj):
        return obj.referrer.email
    referrer_email.short_description = 'Referrer'
    referrer_email.admin_order_field = 'referrer__email'

    def is_active_display(self, obj):
        """Відображення статусу з кольоровою міткою"""
        from django.utils import timezone

        if not obj.is_active:
            return format_html('<span style="color: gray;">Неактивний</span>')

        if timezone.now() > obj.trial_end:
            return format_html('<span style="color: red;">Закінчився</span>')

        return format_html('<span style="color: green;">Активний</span>')
    is_active_display.short_description = 'Status'

    def revert_trials_now(self, request, queryset):
        """Повернути користувачів на оригінальний план"""
        from .utils import revert_referral_trial

        count = 0
        for trial in queryset:
            if trial.is_active and revert_referral_trial(trial.id):
                count += 1

        self.message_user(request, f'Повернено {count} trial періодів')
    revert_trials_now.short_description = 'Повернути на оригінальний план'
