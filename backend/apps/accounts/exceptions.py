from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError
from django.conf import settings


def custom_exception_handler(exc, context):
    """
    Custom exception handler for DRF
    """
    import logging
    logger = logging.getLogger(__name__)
    
    # Log the exception for debugging
    logger.error(f"Exception in {context.get('view', 'unknown')}: {type(exc).__name__}: {str(exc)}", exc_info=True)
    
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)

    if response is not None:
        # Extract a readable error message from response.data
        error_message = None
        
        if isinstance(exc, ValidationError):
            # For ValidationError, extract first error message
            if isinstance(response.data, dict):
                # Check for non_field_errors first
                if 'non_field_errors' in response.data and response.data['non_field_errors']:
                    if isinstance(response.data['non_field_errors'], list) and len(response.data['non_field_errors']) > 0:
                        # Handle ErrorDetail objects
                        error_detail = response.data['non_field_errors'][0]
                        if hasattr(error_detail, 'string'):
                            error_message = error_detail.string
                        else:
                            error_message = str(error_detail)
                # Otherwise, get first field error
                elif response.data:
                    first_key = list(response.data.keys())[0]
                    first_value = response.data[first_key]
                    if isinstance(first_value, list) and len(first_value) > 0:
                        # Handle ErrorDetail objects
                        error_detail = first_value[0]
                        if hasattr(error_detail, 'string'):
                            error_message = error_detail.string
                        else:
                            error_message = str(error_detail)
                    else:
                        if hasattr(first_value, 'string'):
                            error_message = first_value.string
                        else:
                            error_message = str(first_value)
            elif isinstance(response.data, list) and len(response.data) > 0:
                error_detail = response.data[0]
                if hasattr(error_detail, 'string'):
                    error_message = error_detail.string
                else:
                    error_message = str(error_detail)
        
        # Fallback to exception string if no message extracted
        if not error_message:
            error_message = str(exc)
        
        # Customize error response format
        custom_response_data = {
            'error': True,
            'message': error_message,
            'details': response.data
        }
        response.data = custom_response_data
    else:
        # If DRF didn't handle it, it's a server error (500)
        # Return a user-friendly error response
        from django.db import IntegrityError
        
        if isinstance(exc, IntegrityError):
            # Handle database integrity errors (e.g., duplicate key)
            error_message = "Database error occurred. Please try again or contact support."
            if "duplicate key" in str(exc).lower() or "unique constraint" in str(exc).lower():
                error_message = "This record already exists. Please check your input."
        else:
            error_message = "An unexpected error occurred. Please try again later."
        
        logger.error(f"Unhandled exception: {type(exc).__name__}: {str(exc)}", exc_info=True)
        
        return Response(
            {
                'error': True,
                'message': error_message,
                'details': {'error': str(exc)} if settings.DEBUG else {}
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
