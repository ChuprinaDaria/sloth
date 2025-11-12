# Generated manually for email integration type

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('integrations', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='integration',
            name='integration_type',
            field=models.CharField(
                max_length=30,
                choices=[
                    ('telegram', 'Telegram Bot'),
                    ('whatsapp', 'WhatsApp Business'),
                    ('google_calendar', 'Google Calendar'),
                    ('google_sheets', 'Google Sheets'),
                    ('instagram', 'Instagram'),
                    ('website_widget', 'Website Widget'),
                    ('email', 'Email Integration'),
                ]
            ),
        ),
    ]
