"""
Management command to seed PhotoRecognitionProvider database with default providers
"""
from django.core.management.base import BaseCommand
from apps.integrations.models import PhotoRecognitionProvider
from django.db import connection


class Command(BaseCommand):
    help = 'Seed photo recognition providers in public schema'

    def handle(self, *args, **options):
        # Make sure we're in public schema (these are global providers)
        with connection.cursor() as cursor:
            cursor.execute("SET search_path TO public")

        providers_data = [
            {
                'slug': 'gpt4_vision',
                'name': 'GPT-4 Vision (OpenAI)',
                'description': 'OpenAI GPT-4 with vision capabilities. Excellent for detailed analysis of hair and styling.',
                'requires_api_key': True,
                'api_documentation_url': 'https://platform.openai.com/docs/guides/vision',
                'cost_per_image': 0.01,
                'available_in_professional_only': False,  # Available in STARTER too
                'is_active': True,
                'order': 1
            },
            {
                'slug': 'claude_opus',
                'name': 'Claude 3 Opus (Anthropic)',
                'description': 'Anthropic Claude 3 Opus with vision. Most capable model for complex analysis.',
                'requires_api_key': True,
                'api_documentation_url': 'https://docs.anthropic.com/claude/docs/vision',
                'cost_per_image': 0.015,
                'available_in_professional_only': True,
                'is_active': True,
                'order': 2
            },
            {
                'slug': 'claude_sonnet',
                'name': 'Claude 3.5 Sonnet (Anthropic)',
                'description': 'Anthropic Claude 3.5 Sonnet with vision. Balanced performance and cost.',
                'requires_api_key': True,
                'api_documentation_url': 'https://docs.anthropic.com/claude/docs/vision',
                'cost_per_image': 0.008,
                'available_in_professional_only': True,
                'is_active': True,
                'order': 3
            },
            {
                'slug': 'gemini_pro',
                'name': 'Gemini 1.5 Pro (Google)',
                'description': 'Google Gemini Pro with vision capabilities. Great for creative analysis.',
                'requires_api_key': True,
                'api_documentation_url': 'https://ai.google.dev/gemini-api/docs/vision',
                'cost_per_image': 0.0025,
                'available_in_professional_only': True,
                'is_active': True,
                'order': 4
            },
        ]

        created_count = 0
        updated_count = 0

        for provider_data in providers_data:
            provider, created = PhotoRecognitionProvider.objects.update_or_create(
                slug=provider_data['slug'],
                defaults={
                    'name': provider_data['name'],
                    'description': provider_data['description'],
                    'requires_api_key': provider_data['requires_api_key'],
                    'api_documentation_url': provider_data['api_documentation_url'],
                    'cost_per_image': provider_data['cost_per_image'],
                    'available_in_professional_only': provider_data['available_in_professional_only'],
                    'is_active': provider_data['is_active'],
                    'order': provider_data['order'],
                }
            )

            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created provider: {provider.name}')
                )
            else:
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'↻ Updated provider: {provider.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nSeed completed: {created_count} created, {updated_count} updated'
            )
        )
