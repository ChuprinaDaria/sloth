# Generated manually for adding config field and new integration types

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('integrations', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='integration',
            name='config',
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AlterField(
            model_name='integration',
            name='integration_type',
            field=models.CharField(
                choices=[
                    ('telegram', 'Telegram Bot'),
                    ('whatsapp', 'WhatsApp Business'),
                    ('google_calendar', 'Google Calendar'),
                    ('google_sheets', 'Google Sheets'),
                    ('instagram', 'Instagram'),
                    ('website_widget', 'Website Widget'),
                ],
                max_length=30
            ),
        ),
    ]
