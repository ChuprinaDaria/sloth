# Generated migration for core app
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PrivacyPolicy',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language', models.CharField(choices=[('uk', 'Українська'), ('en', 'English'), ('pl', 'Polski'), ('ru', 'Русский')], max_length=2, unique=True, verbose_name='Language')),
                ('title', models.CharField(max_length=255, verbose_name='Title')),
                ('content', models.TextField(help_text='Supports HTML and Markdown', verbose_name='Content')),
                ('last_updated', models.DateTimeField(auto_now=True, verbose_name='Last Updated')),
                ('is_active', models.BooleanField(default=True, verbose_name='Active')),
                ('version', models.CharField(default='1.0', max_length=50, verbose_name='Version')),
            ],
            options={
                'verbose_name': 'Privacy Policy',
                'verbose_name_plural': 'Privacy Policies',
                'ordering': ['language'],
            },
        ),
        migrations.CreateModel(
            name='TermsOfService',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language', models.CharField(choices=[('uk', 'Українська'), ('en', 'English'), ('pl', 'Polski'), ('ru', 'Русский')], max_length=2, unique=True, verbose_name='Language')),
                ('title', models.CharField(max_length=255, verbose_name='Title')),
                ('content', models.TextField(help_text='Supports HTML and Markdown', verbose_name='Content')),
                ('last_updated', models.DateTimeField(auto_now=True, verbose_name='Last Updated')),
                ('is_active', models.BooleanField(default=True, verbose_name='Active')),
                ('version', models.CharField(default='1.0', max_length=50, verbose_name='Version')),
            ],
            options={
                'verbose_name': 'Terms of Service',
                'verbose_name_plural': 'Terms of Service',
                'ordering': ['language'],
            },
        ),
        migrations.CreateModel(
            name='SupportContact',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(default='support@lazysoft.pl', max_length=254, verbose_name='Support Email')),
                ('telegram', models.CharField(blank=True, max_length=100, null=True, verbose_name='Telegram')),
                ('phone', models.CharField(blank=True, max_length=50, null=True, verbose_name='Phone')),
                ('working_hours', models.CharField(default='Пн-Пт 9:00-18:00', max_length=255, verbose_name='Working Hours')),
                ('response_time', models.CharField(default='До 24 годин', max_length=100, verbose_name='Response Time')),
                ('is_active', models.BooleanField(default=True, verbose_name='Active')),
            ],
            options={
                'verbose_name': 'Support Contact',
                'verbose_name_plural': 'Support Contacts',
            },
        ),
        migrations.CreateModel(
            name='AppDownloadLinks',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ios_app_id', models.CharField(blank=True, help_text='App Store App ID (numbers only)', max_length=50, null=True, verbose_name='iOS App ID')),
                ('ios_url', models.URLField(blank=True, null=True, verbose_name='iOS App Store URL')),
                ('android_package', models.CharField(default='pl.lazysoft.slothai', max_length=100, verbose_name='Android Package Name')),
                ('android_url', models.URLField(blank=True, null=True, verbose_name='Android Play Store URL')),
                ('is_active', models.BooleanField(default=True, verbose_name='Active')),
                ('coming_soon', models.BooleanField(default=True, help_text='Show "Coming Soon" message instead of download links', verbose_name='Coming Soon')),
            ],
            options={
                'verbose_name': 'App Download Links',
                'verbose_name_plural': 'App Download Links',
            },
        ),
    ]
