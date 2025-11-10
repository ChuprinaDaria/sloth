# Generated migration for ReferralTrial model

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('referrals', '0001_initial'),
        ('subscriptions', '0002_update_plans'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ReferralTrial',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('trial_start', models.DateTimeField(auto_now_add=True)),
                ('trial_end', models.DateTimeField()),
                ('is_active', models.BooleanField(default=True)),
                ('reverted_at', models.DateTimeField(blank=True, null=True)),
                ('original_plan', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='subscriptions.plan')),
                ('referrer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='trials_granted', to=settings.AUTH_USER_MODEL)),
                ('trial_plan', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='subscriptions.plan')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='referral_trial', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Referral Trial',
                'verbose_name_plural': 'Referral Trials',
                'db_table': 'referral_trials',
                'ordering': ['-trial_start'],
            },
        ),
    ]
