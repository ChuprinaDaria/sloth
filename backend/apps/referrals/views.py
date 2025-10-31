from rest_framework import generics, permissions
from rest_framework.response import Response
from .models import ReferralCode, Referral, ReferralReward
from rest_framework import serializers


class ReferralStatsSerializer(serializers.Serializer):
    code = serializers.CharField()
    total_signups = serializers.IntegerField()
    active_referrals = serializers.IntegerField()
    next_milestone = serializers.IntegerField()
    progress_to_milestone = serializers.FloatField()


class ReferralListView(generics.ListAPIView):
    """List user's referrals"""
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        referrals = Referral.objects.filter(referrer=request.user).select_related('referred')

        data = [{
            'id': ref.id,
            'email': ref.referred.email,
            'status': ref.status,
            'created_at': ref.created_at,
            'activated_at': ref.activated_at
        } for ref in referrals]

        return Response(data)


class ReferralStatsView(generics.RetrieveAPIView):
    """Get referral statistics"""
    serializer_class = ReferralStatsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def retrieve(self, request):
        # Get or create referral code stats
        referral_code, _ = ReferralCode.objects.get_or_create(
            user=request.user,
            defaults={'code': request.user.referral_code}
        )

        # Calculate next milestone
        milestones = [50, 100, 150, 200]
        next_milestone = next((m for m in milestones if m > referral_code.active_referrals), 200)

        # Calculate progress
        progress = (referral_code.active_referrals / next_milestone) * 100 if next_milestone else 100

        data = {
            'code': referral_code.code,
            'total_signups': referral_code.total_signups,
            'active_referrals': referral_code.active_referrals,
            'next_milestone': next_milestone,
            'progress_to_milestone': round(progress, 2)
        }

        return Response(data)


class MyReferralCodeView(generics.RetrieveAPIView):
    """Get user's referral code"""
    permission_classes = [permissions.IsAuthenticated]

    def retrieve(self, request):
        return Response({
            'code': request.user.referral_code,
            'referral_url': f"{request.scheme}://{request.get_host()}/register?ref={request.user.referral_code}"
        })
