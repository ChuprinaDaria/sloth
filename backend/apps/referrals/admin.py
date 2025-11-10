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
        """>7=0G8B8 @5D5@@0;8 O: 0:B82=V"""
        from django.utils import timezone

        count = 0
        for referral in queryset:
            if referral.status != 'active':
                referral.status = 'active'
                if not referral.activated_at:
                    referral.activated_at = timezone.now()
                referral.save()
                count += 1

                # =>2;NT<> AB0B8AB8:C @5D5@5@0
                from .utils import update_referral_stats
                update_referral_stats(referral.referrer)

        self.message_user(request, f'>7=0G5=> {count} @5D5@@0;V2 O: 0:B82=V')
    mark_as_active.short_description = ' >7=0G8B8 O: 0:B82=V'

    def mark_as_inactive(self, request, queryset):
        """>7=0G8B8 @5D5@@0;8 O: =50:B82=V"""
        count = queryset.update(status='inactive')

        # =>2;NT<> AB0B8AB8:C 4;O 2AVE @5D5@5@V2
        from .utils import update_referral_stats
        for referral in queryset:
            update_referral_stats(referral.referrer)

        self.message_user(request, f'>7=0G5=> {count} @5D5@@0;V2 O: =50:B82=V')
    mark_as_inactive.short_description = 'L >7=0G8B8 O: =50:B82=V'


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
        """V4>1@065==O AB0BCAC 7 :>;L>@>2>N <VB:>N"""
        from django.utils import timezone

        if not obj.is_active:
            return format_html('<span style="color: gray;">L 50:B82=89</span>')

        if timezone.now() > obj.trial_end:
            return format_html('<span style="color: red;">ð 0:V=G82AO</span>')

        return format_html('<span style="color: green;"> :B82=89</span>')
    is_active_display.short_description = 'Status'

    def revert_trials_now(self, request, queryset):
        """>25@=CB8 :>@8ABC20GV2 =0 >@83V=0;L=89 ?;0="""
        from .utils import revert_referral_trial

        count = 0
        for trial in queryset:
            if trial.is_active and revert_referral_trial(trial.id):
                count += 1

        self.message_user(request, f'>25@=5=> {count} trial ?5@V>4V2')
    revert_trials_now.short_description = 'ê >25@=CB8 =0 >@83V=0;L=89 ?;0='
