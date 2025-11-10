from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import ReferralCode, Referral, ReferralReward
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


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


class ActivateReferralCodeView(APIView):
    """Activate referral code for existing users"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        from .utils import apply_referral_trial, update_referral_stats
        from .models import ReferralTrial
        from django.db import transaction, IntegrityError
        import logging

        logger = logging.getLogger(__name__)

        referral_code = request.data.get('code', '').strip()

        if not referral_code:
            return Response(
                {'error': 'Referral code is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Use transaction to prevent race conditions
            with transaction.atomic():
                # Check if user already has active trial
                if hasattr(request.user, 'referral_trial') and request.user.referral_trial.is_active:
                    return Response(
                        {'error': 'You already have an active referral trial'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # Check if user already used a referral code (correct check for related manager)
                if Referral.objects.filter(referred=request.user).exists():
                    return Response(
                        {'error': 'You have already used a referral code'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # Find referrer by code
                referrer = User.objects.get(referral_code=referral_code)

                # Can't use own referral code
                if referrer == request.user:
                    return Response(
                        {'error': 'You cannot use your own referral code'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # Create Referral record (atomic with checks above)
                referral = Referral.objects.create(
                    referrer=referrer,
                    referred=request.user,
                    status='pending'
                )

                # Update referrer's stats
                referral_code_obj, created = ReferralCode.objects.get_or_create(
                    user=referrer,
                    defaults={'code': referral_code}
                )
                referral_code_obj.total_signups += 1
                referral_code_obj.save()

                # Apply 10-day Professional trial
                success = apply_referral_trial(request.user, referrer)

                if success:
                    # Update referrer's stats
                    update_referral_stats(referrer)

                    logger.info(f"Activated referral trial for {request.user.email} from {referrer.email}")

                    return Response({
                        'success': True,
                        'message': 'Referral code activated! You now have 10 days of Professional plan.'
                    })
                else:
                    return Response(
                        {'error': 'Failed to activate trial. Please try again.'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )

        except User.DoesNotExist:
            return Response(
                {'error': 'Invalid referral code'},
                status=status.HTTP_404_NOT_FOUND
            )
        except IntegrityError:
            logger.warning(f"Duplicate referral attempt for {request.user.email}")
            return Response(
                {'error': 'You have already used a referral code'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error activating referral code for {request.user.email}: {str(e)}")
            return Response(
                {'error': 'An error occurred. Please try again.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
