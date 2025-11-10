# Generated manually for Google My Business and Instagram Posts

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('integrations', '0002_add_email_integration_type'),
    ]

    operations = [
        # Add google_my_business to integration types
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
                    ('google_my_business', 'Google My Business'),
                ]
            ),
        ),
        # Create InstagramPost model
        migrations.CreateModel(
            name='InstagramPost',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField(db_index=True)),
                ('post_id', models.CharField(max_length=255, unique=True, db_index=True)),
                ('caption', models.TextField(blank=True)),
                ('media_type', models.CharField(max_length=50, default='IMAGE')),
                ('media_url', models.URLField(blank=True)),
                ('permalink', models.URLField(blank=True)),
                ('likes', models.IntegerField(default=0)),
                ('comments', models.IntegerField(default=0)),
                ('engagement', models.IntegerField(default=0)),
                ('impressions', models.IntegerField(default=0)),
                ('reach', models.IntegerField(default=0)),
                ('hashtags', models.JSONField(default=list, blank=True)),
                ('embedding', models.JSONField(default=list, blank=True)),
                ('posted_at', models.DateTimeField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Instagram Post',
                'verbose_name_plural': 'Instagram Posts',
                'db_table': 'instagram_posts',
                'ordering': ['-posted_at'],
            },
        ),
        # Add indexes for InstagramPost
        migrations.AddIndex(
            model_name='instagrampost',
            index=models.Index(fields=['user_id', '-posted_at'], name='instagram_p_user_id_a1b2c3_idx'),
        ),
        migrations.AddIndex(
            model_name='instagrampost',
            index=models.Index(fields=['post_id'], name='instagram_p_post_id_d4e5f6_idx'),
        ),
    ]
