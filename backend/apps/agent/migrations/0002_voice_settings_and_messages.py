# Generated manually for voice settings and messages

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('agent', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='VoiceSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField(db_index=True, unique=True)),
                ('voice_name', models.CharField(choices=[('alloy', 'Alloy - Neutral'), ('echo', 'Echo - Male'), ('fable', 'Fable - British Male'), ('onyx', 'Onyx - Deep Male'), ('nova', 'Nova - Female'), ('shimmer', 'Shimmer - Soft Female')], default='nova', max_length=50)),
                ('is_cloned', models.BooleanField(default=False)),
                ('cloned_voice_id', models.CharField(blank=True, max_length=255)),
                ('cloned_voice_sample_path', models.CharField(blank=True, max_length=500)),
                ('tts_enabled', models.BooleanField(default=True)),
                ('tts_speed', models.FloatField(default=1.0)),
                ('stt_enabled', models.BooleanField(default=True)),
                ('auto_detect_language', models.BooleanField(default=True)),
                ('preferred_language', models.CharField(default='uk', max_length=10)),
                ('telegram_voice_enabled', models.BooleanField(default=True)),
                ('whatsapp_voice_enabled', models.BooleanField(default=True)),
                ('web_voice_enabled', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Voice Settings',
                'verbose_name_plural': 'Voice Settings',
                'db_table': 'voice_settings',
            },
        ),
        migrations.CreateModel(
            name='VoiceMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('audio_file_path', models.CharField(max_length=500)),
                ('audio_duration', models.FloatField(default=0.0)),
                ('audio_format', models.CharField(default='mp3', max_length=10)),
                ('transcribed_text', models.TextField(blank=True)),
                ('detected_language', models.CharField(blank=True, max_length=10)),
                ('is_generated', models.BooleanField(default=False)),
                ('voice_used', models.CharField(blank=True, max_length=50)),
                ('generation_time', models.FloatField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('message', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='voice_messages', to='agent.message')),
            ],
            options={
                'verbose_name': 'Voice Message',
                'verbose_name_plural': 'Voice Messages',
                'db_table': 'voice_messages',
                'ordering': ['created_at'],
            },
        ),
    ]
