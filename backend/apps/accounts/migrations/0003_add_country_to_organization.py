# Generated manually for adding country field to Organization

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='organization',
            name='country',
            field=models.CharField(blank=True, default='', max_length=2),
        ),
    ]
