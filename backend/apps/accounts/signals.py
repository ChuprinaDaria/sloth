from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import connection
from .models import Organization


@receiver(post_save, sender=Organization)
def create_tenant_schema(sender, instance, created, **kwargs):
    """
    Створює нову PostgreSQL schema при створенні організації
    """
    if created:
        with connection.cursor() as cursor:
            # Create schema
            cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {instance.schema_name}")

            # Grant permissions
            cursor.execute(f"GRANT ALL ON SCHEMA {instance.schema_name} TO {connection.settings_dict['USER']}")

            # Set schema for migration
            cursor.execute(f"SET search_path TO {instance.schema_name}, public")

            # Run migrations for tenant schema
            from django.core.management import call_command
            try:
                # Migrate tenant-specific models
                call_command('migrate', '--database', 'default', '--skip-checks')
            except Exception as e:
                print(f"Error migrating tenant schema {instance.schema_name}: {e}")

            # Reset to public schema
            cursor.execute("SET search_path TO public")
