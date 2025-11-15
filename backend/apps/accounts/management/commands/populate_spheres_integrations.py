from django.core.management.base import BaseCommand
from apps.accounts.models import Sphere, IntegrationType


class Command(BaseCommand):
    help = 'Populate Spheres and Integration Types with initial data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting to populate Spheres and Integration Types...'))

        # Create Spheres
        spheres = self.create_spheres()
        self.stdout.write(self.style.SUCCESS(f'Created {len(spheres)} spheres'))

        # Create Integration Types
        integration_count = self.create_integration_types(spheres)
        self.stdout.write(self.style.SUCCESS(f'Created {integration_count} integration types'))

        self.stdout.write(self.style.SUCCESS('Successfully populated Spheres and Integration Types!'))

    def create_spheres(self):
        """Create business spheres"""
        spheres_data = [
            {
                'name': 'General',
                'slug': 'general',
                'description': 'General business - suitable for all industries',
                'icon': '🏢',
                'color': '#3B82F6',
                'order': 1
            },
            {
                'name': 'Beauty & Wellness',
                'slug': 'beauty',
                'description': 'Beauty salons, spas, barbershops, nail studios',
                'icon': '💅',
                'color': '#EC4899',
                'order': 2
            },
            {
                'name': 'Health & Medical',
                'slug': 'health',
                'description': 'Medical clinics, doctors, dentists, physiotherapists',
                'icon': '⚕️',
                'color': '#10B981',
                'order': 3
            },
        ]

        spheres = {}
        for data in spheres_data:
            sphere, created = Sphere.objects.get_or_create(
                slug=data['slug'],
                defaults=data
            )
            if created:
                self.stdout.write(f'  Created sphere: {sphere.name}')
            else:
                # Update existing
                for key, value in data.items():
                    setattr(sphere, key, value)
                sphere.save()
                self.stdout.write(f'  Updated sphere: {sphere.name}')

            spheres[data['slug']] = sphere

        return spheres

    def create_integration_types(self, spheres):
        """Create integration types for each sphere"""

        # General integrations (available for all spheres)
        general_integrations = [
            {
                'slug': 'google-calendar',
                'name': 'Google Calendar',
                'integration_type': IntegrationType.GOOGLE_CALENDAR,
                'description': 'Sync appointments with Google Calendar',
                'requires_oauth': True,
                'oauth_provider': 'google',
                'supports_webhooks': True,
                'supports_working_hours': False,
                'color': '#4285F4',
                'order': 1
            },
            {
                'slug': 'google-meet',
                'name': 'Google Meet',
                'integration_type': IntegrationType.GOOGLE_MEET,
                'description': 'Create video meetings with Google Meet',
                'requires_oauth': True,
                'oauth_provider': 'google',
                'supports_webhooks': False,
                'supports_working_hours': False,
                'color': '#00897B',
                'order': 2
            },
            {
                'slug': 'google-sheets',
                'name': 'Google Sheets',
                'integration_type': IntegrationType.GOOGLE_SHEETS,
                'description': 'Export and sync data with Google Sheets',
                'requires_oauth': True,
                'oauth_provider': 'google',
                'supports_webhooks': False,
                'supports_working_hours': False,
                'color': '#0F9D58',
                'order': 3
            },
            {
                'slug': 'gmail',
                'name': 'Gmail',
                'integration_type': IntegrationType.GMAIL,
                'description': 'Send emails via Gmail',
                'requires_oauth': True,
                'oauth_provider': 'google',
                'supports_webhooks': True,
                'supports_working_hours': False,
                'color': '#EA4335',
                'order': 4
            },
            {
                'slug': 'telegram',
                'name': 'Telegram',
                'integration_type': IntegrationType.TELEGRAM,
                'description': 'Communicate with clients via Telegram Bot',
                'requires_oauth': False,
                'oauth_provider': 'telegram',
                'supports_webhooks': True,
                'supports_working_hours': True,
                'color': '#0088CC',
                'order': 5
            },
            {
                'slug': 'whatsapp',
                'name': 'WhatsApp Business',
                'integration_type': IntegrationType.WHATSAPP,
                'description': 'Connect WhatsApp Business API',
                'requires_oauth': True,
                'oauth_provider': 'whatsapp',
                'supports_webhooks': True,
                'supports_working_hours': False,
                'color': '#25D366',
                'order': 6
            },
            {
                'slug': 'instagram',
                'name': 'Instagram',
                'integration_type': IntegrationType.INSTAGRAM,
                'description': 'Manage Instagram messages and comments',
                'requires_oauth': True,
                'oauth_provider': 'facebook',
                'supports_webhooks': True,
                'supports_working_hours': True,
                'color': '#E4405F',
                'order': 7
            },
            {
                'slug': 'facebook-messenger',
                'name': 'Facebook Messenger',
                'integration_type': IntegrationType.FACEBOOK_MESSENGER,
                'description': 'Respond to Facebook Messenger messages',
                'requires_oauth': True,
                'oauth_provider': 'facebook',
                'supports_webhooks': True,
                'supports_working_hours': True,
                'color': '#0084FF',
                'order': 8
            },
            {
                'slug': 'calendly',
                'name': 'Calendly',
                'integration_type': IntegrationType.CALENDLY,
                'description': 'Sync with Calendly scheduling',
                'requires_oauth': True,
                'oauth_provider': 'calendly',
                'supports_webhooks': True,
                'supports_working_hours': False,
                'color': '#006BFF',
                'order': 9
            },
            {
                'slug': 'zoom',
                'name': 'Zoom',
                'integration_type': IntegrationType.ZOOM,
                'description': 'Create and manage Zoom meetings',
                'requires_oauth': True,
                'oauth_provider': 'zoom',
                'supports_webhooks': True,
                'supports_working_hours': False,
                'color': '#2D8CFF',
                'order': 10
            },
        ]

        # Beauty-specific integrations
        beauty_integrations = [
            {
                'slug': 'booksy',
                'name': 'Booksy',
                'integration_type': IntegrationType.BOOKSY,
                'description': 'Connect Booksy appointment system (Poland, USA, UK, Canada, Australia)',
                'requires_oauth': True,
                'oauth_provider': 'booksy',
                'supports_webhooks': True,
                'supports_working_hours': False,
                'available_countries': ['PL', 'US', 'GB', 'CA', 'AU'],
                'color': '#FF6B9D',
                'order': 20
            },
            {
                'slug': 'dikidi',
                'name': 'Dikidi',
                'integration_type': IntegrationType.DIKIDI,
                'description': 'Connect Dikidi - #1 booking system for salons in Ukraine',
                'requires_oauth': True,
                'oauth_provider': 'dikidi',
                'supports_webhooks': True,
                'supports_working_hours': False,
                'available_countries': ['UA'],
                'color': '#FF5252',
                'order': 21
            },
            {
                'slug': 'easyweek',
                'name': 'EasyWeek',
                'integration_type': IntegrationType.EASYWEEK,
                'description': 'Connect EasyWeek booking system (Ukraine, Poland)',
                'requires_oauth': True,
                'oauth_provider': 'easyweek',
                'supports_webhooks': True,
                'supports_working_hours': False,
                'available_countries': ['UA', 'PL'],
                'color': '#4CAF50',
                'order': 22
            },
            {
                'slug': 'treatwell',
                'name': 'Treatwell',
                'integration_type': IntegrationType.TREATWELL,
                'description': 'Connect Treatwell (UK, Germany, France, Spain, Italy)',
                'requires_oauth': True,
                'oauth_provider': 'treatwell',
                'supports_webhooks': True,
                'supports_working_hours': False,
                'available_countries': ['GB', 'DE', 'FR', 'ES', 'IT'],
                'color': '#00BFA5',
                'order': 23
            },
            {
                'slug': 'planity',
                'name': 'Planity',
                'integration_type': IntegrationType.PLANITY,
                'description': 'Connect Planity (France, Belgium)',
                'requires_oauth': True,
                'oauth_provider': 'planity',
                'supports_webhooks': True,
                'supports_working_hours': False,
                'available_countries': ['FR', 'BE'],
                'color': '#FF4081',
                'order': 24
            },
            {
                'slug': 'reservio',
                'name': 'Reservio',
                'integration_type': IntegrationType.RESERVIO,
                'description': 'Connect Reservio (Spain, Czech Republic, Slovakia)',
                'requires_oauth': True,
                'oauth_provider': 'reservio',
                'supports_webhooks': True,
                'supports_working_hours': False,
                'available_countries': ['ES', 'CZ', 'SK'],
                'color': '#2196F3',
                'order': 25
            },
            {
                'slug': 'salonized',
                'name': 'Salonized',
                'integration_type': IntegrationType.SALONIZED,
                'description': 'Connect Salonized (Netherlands, Belgium)',
                'requires_oauth': True,
                'oauth_provider': 'salonized',
                'supports_webhooks': True,
                'supports_working_hours': False,
                'available_countries': ['NL', 'BE'],
                'color': '#9C27B0',
                'order': 26
            },
            {
                'slug': 'simplybook-me',
                'name': 'SimplyBook.me',
                'integration_type': IntegrationType.SIMPLYBOOK_ME,
                'description': 'Connect SimplyBook.me - global booking system',
                'requires_oauth': True,
                'oauth_provider': 'simplybook',
                'supports_webhooks': True,
                'supports_working_hours': False,
                'available_countries': [],
                'color': '#673AB7',
                'order': 27
            },
            {
                'slug': 'square-appointments',
                'name': 'Square Appointments',
                'integration_type': IntegrationType.SQUARE_APPOINTMENTS,
                'description': 'Connect Square Appointments - global booking',
                'requires_oauth': True,
                'oauth_provider': 'square',
                'supports_webhooks': True,
                'supports_working_hours': False,
                'available_countries': [],
                'color': '#000000',
                'order': 28
            },
            {
                'slug': 'fresha',
                'name': 'Fresha',
                'integration_type': IntegrationType.FRESHA,
                'description': 'Connect Fresha (UK, Global)',
                'requires_oauth': True,
                'oauth_provider': 'fresha',
                'supports_webhooks': True,
                'supports_working_hours': False,
                'available_countries': ['GB'],
                'color': '#1DE9B6',
                'order': 29
            },
        ]

        # Health-specific integrations
        health_integrations = [
            {
                'slug': 'znany-lekarz',
                'name': 'Znany Lekarz / Doctoralia',
                'integration_type': IntegrationType.ZNANY_LEKARZ,
                'description': 'Connect Znany Lekarz / Doctoralia (Poland, Spain, Italy, Brazil, Mexico)',
                'requires_oauth': True,
                'oauth_provider': 'doctoralia',
                'supports_webhooks': True,
                'supports_working_hours': False,
                'available_countries': ['PL', 'ES', 'IT', 'BR', 'MX'],
                'color': '#00A99D',
                'order': 40
            },
            {
                'slug': 'doctolib',
                'name': 'Doctolib',
                'integration_type': IntegrationType.DOCTOLIB,
                'description': 'Connect Doctolib (France, Germany, Italy)',
                'requires_oauth': True,
                'oauth_provider': 'doctolib',
                'supports_webhooks': True,
                'supports_working_hours': False,
                'available_countries': ['FR', 'DE', 'IT'],
                'color': '#0596DE',
                'order': 41
            },
            {
                'slug': 'jameda',
                'name': 'Jameda',
                'integration_type': IntegrationType.JAMEDA,
                'description': 'Connect Jameda (Germany)',
                'requires_oauth': True,
                'oauth_provider': 'jameda',
                'supports_webhooks': True,
                'supports_working_hours': False,
                'available_countries': ['DE'],
                'color': '#FF6600',
                'order': 42
            },
            {
                'slug': 'doc-ua',
                'name': 'Doc.ua',
                'integration_type': IntegrationType.DOC_UA,
                'description': 'Connect Doc.ua - medical appointments in Ukraine',
                'requires_oauth': True,
                'oauth_provider': 'docua',
                'supports_webhooks': True,
                'supports_working_hours': False,
                'available_countries': ['UA'],
                'color': '#2196F3',
                'order': 43
            },
            {
                'slug': 'helsi',
                'name': 'Helsi',
                'integration_type': IntegrationType.HELSI,
                'description': 'Connect Helsi - medical records system in Ukraine',
                'requires_oauth': True,
                'oauth_provider': 'helsi',
                'supports_webhooks': True,
                'supports_working_hours': False,
                'available_countries': ['UA'],
                'color': '#4CAF50',
                'order': 44
            },
            {
                'slug': 'patient-access',
                'name': 'Patient Access',
                'integration_type': IntegrationType.PATIENT_ACCESS,
                'description': 'Connect Patient Access (UK)',
                'requires_oauth': True,
                'oauth_provider': 'patientaccess',
                'supports_webhooks': True,
                'supports_working_hours': False,
                'available_countries': ['GB'],
                'color': '#00897B',
                'order': 45
            },
            {
                'slug': 'zocdoc',
                'name': 'Zocdoc',
                'integration_type': IntegrationType.ZOCDOC,
                'description': 'Connect Zocdoc (USA)',
                'requires_oauth': True,
                'oauth_provider': 'zocdoc',
                'supports_webhooks': True,
                'supports_working_hours': False,
                'available_countries': ['US'],
                'color': '#FFB300',
                'order': 46
            },
            {
                'slug': 'practo',
                'name': 'Practo',
                'integration_type': IntegrationType.PRACTO,
                'description': 'Connect Practo (India)',
                'requires_oauth': True,
                'oauth_provider': 'practo',
                'supports_webhooks': True,
                'supports_working_hours': False,
                'available_countries': ['IN'],
                'color': '#1C8B7E',
                'order': 47
            },
        ]

        # Create integration types
        count = 0

        # General integrations (available for all spheres)
        for integration_data in general_integrations:
            integration, created = IntegrationType.objects.get_or_create(
                slug=integration_data['slug'],
                defaults={k: v for k, v in integration_data.items() if k != 'slug'}
            )

            if not created:
                # Update existing
                for key, value in integration_data.items():
                    if key != 'slug':
                        setattr(integration, key, value)
                integration.save()

            # Add to all spheres
            integration.spheres.set([spheres['general'], spheres['beauty'], spheres['health']])
            count += 1
            self.stdout.write(f'  Created/Updated integration: {integration.name} (General - all spheres)')

        # Beauty integrations
        for integration_data in beauty_integrations:
            integration, created = IntegrationType.objects.get_or_create(
                slug=integration_data['slug'],
                defaults={k: v for k, v in integration_data.items() if k != 'slug'}
            )

            if not created:
                # Update existing
                for key, value in integration_data.items():
                    if key != 'slug':
                        setattr(integration, key, value)
                integration.save()

            # Add to beauty sphere only
            integration.spheres.set([spheres['beauty']])
            count += 1
            self.stdout.write(f'  Created/Updated integration: {integration.name} (Beauty)')

        # Health integrations
        for integration_data in health_integrations:
            integration, created = IntegrationType.objects.get_or_create(
                slug=integration_data['slug'],
                defaults={k: v for k, v in integration_data.items() if k != 'slug'}
            )

            if not created:
                # Update existing
                for key, value in integration_data.items():
                    if key != 'slug':
                        setattr(integration, key, value)
                integration.save()

            # Add to health sphere only
            integration.spheres.set([spheres['health']])
            count += 1
            self.stdout.write(f'  Created/Updated integration: {integration.name} (Health)')

        return count
