from django.http import JsonResponse
from rest_framework import status


class SubscriptionLimitMiddleware:
    """
    Middleware для перевірки лімітів підписки
    """

    ENDPOINTS_TO_CHECK = {
        '/api/agent/chat/': 'messages',
        '/api/photos/upload/': 'photos',
        '/api/documents/upload/': 'documents',
    }

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip for unauthenticated requests
        if not request.user.is_authenticated:
            return self.get_response(request)

        # Check subscription status
        if hasattr(request.user, 'organization') and request.user.organization:
            subscription = getattr(request.user.organization, 'subscription', None)

            if subscription:
                # Check if subscription is active
                if subscription.status not in ['active', 'trialing']:
                    if request.path.startswith('/api/') and request.method in ['POST', 'PUT', 'PATCH']:
                        return JsonResponse(
                            {
                                'error': 'Subscription expired',
                                'message': 'Your subscription has expired. Please upgrade to continue.'
                            },
                            status=402  # Payment Required
                        )

                # Check usage limits for specific endpoints
                for endpoint, limit_type in self.ENDPOINTS_TO_CHECK.items():
                    if request.path.startswith(endpoint) and request.method == 'POST':
                        if not subscription.is_within_limits(limit_type):
                            return JsonResponse(
                                {
                                    'error': f'{limit_type.capitalize()} limit exceeded',
                                    'message': f'You have reached your monthly {limit_type} limit. Please upgrade your plan.'
                                },
                                status=429  # Too Many Requests
                            )

        response = self.get_response(request)
        return response
