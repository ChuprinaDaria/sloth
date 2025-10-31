from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    """
    Custom exception handler for DRF
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)

    if response is not None:
        # Customize error response format
        custom_response_data = {
            'error': True,
            'message': str(exc),
            'details': response.data
        }
        response.data = custom_response_data

    return response
