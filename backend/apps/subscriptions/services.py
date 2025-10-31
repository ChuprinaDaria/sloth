import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeService:
    """Service for Stripe payment integration"""

    def create_checkout_session(self, user, plan, billing_cycle='monthly'):
        """Create Stripe checkout session for subscription"""
        price_id = (
            plan.stripe_price_id_monthly
            if billing_cycle == 'monthly'
            else plan.stripe_price_id_yearly
        )

        session = stripe.checkout.Session.create(
            customer_email=user.email,
            payment_method_types=['card'],
            line_items=[{
                'price': price_id,
                'quantity': 1,
            }],
            mode='subscription',
            success_url=f"{settings.FRONTEND_URL}/subscription/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{settings.FRONTEND_URL}/pricing",
            metadata={
                'user_id': user.id,
                'organization_id': user.organization.id,
                'plan_id': plan.id,
                'billing_cycle': billing_cycle,
            }
        )

        return session

    def cancel_subscription(self, subscription_id):
        """Cancel subscription at period end"""
        return stripe.Subscription.modify(
            subscription_id,
            cancel_at_period_end=True
        )

    def get_subscription(self, subscription_id):
        """Get Stripe subscription"""
        return stripe.Subscription.retrieve(subscription_id)

    def create_customer(self, user):
        """Create Stripe customer"""
        return stripe.Customer.create(
            email=user.email,
            name=f"{user.first_name} {user.last_name}",
            metadata={
                'user_id': user.id,
                'organization_id': user.organization.id,
            }
        )
