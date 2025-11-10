from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('integrations', '0003_add_google_my_business_and_instagram_posts'),
        ('integrations', '0002_add_config_and_new_integration_types'),
    ]

    operations = [
        # This is a merge migration to ensure both parallel 0002 branches are applied,
        # guaranteeing that the 'config' JSONField exists on 'integrations' table.
    ]


