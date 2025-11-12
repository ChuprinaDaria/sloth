# Generated manually for adding photo analysis fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='photo',
            name='description',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='photo',
            name='detailed_analysis',
            field=models.JSONField(blank=True, default=dict),
        ),
    ]
