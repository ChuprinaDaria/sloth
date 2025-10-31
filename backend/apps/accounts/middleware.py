from django.db import connection
from django.http import JsonResponse


class TenantMiddleware:
    """
    Middleware для автоматичного перемикання PostgreSQL schema
    на основі організації користувача
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip for unauthenticated requests or admin
        if not request.user.is_authenticated or request.path.startswith('/admin/'):
            response = self.get_response(request)
            return response

        # Get tenant schema from user's organization
        if hasattr(request.user, 'organization') and request.user.organization:
            schema_name = request.user.organization.schema_name

            # Set schema for this request
            with connection.cursor() as cursor:
                cursor.execute(f'SET search_path TO {schema_name}, public')

        response = self.get_response(request)
        return response


class TenantSchemaContext:
    """
    Context manager for temporary schema switching
    """

    def __init__(self, schema_name):
        self.schema_name = schema_name
        self.previous_schema = None

    def __enter__(self):
        with connection.cursor() as cursor:
            # Get current schema
            cursor.execute('SHOW search_path')
            self.previous_schema = cursor.fetchone()[0]

            # Set new schema
            cursor.execute(f'SET search_path TO {self.schema_name}, public')

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Restore previous schema
        if self.previous_schema:
            with connection.cursor() as cursor:
                cursor.execute(f'SET search_path TO {self.previous_schema}')
