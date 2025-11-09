# Generated manually for freemium plan changes

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0001_initial'),
    ]

    operations = [
        # Add new fields to Plan model
        migrations.AddField(
            model_name='plan',
            name='plan_type',
            field=models.CharField(
                choices=[('free', 'Free Forever'), ('paid', 'Paid Plan')],
                default='paid',
                max_length=10
            ),
        ),
        migrations.AddField(
            model_name='plan',
            name='max_conversations_per_month',
            field=models.IntegerField(default=50),
        ),
        migrations.AddField(
            model_name='plan',
            name='max_integrations',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='plan',
            name='has_watermark',
            field=models.BooleanField(default=True),
        ),
        migrations.RemoveField(
            model_name='plan',
            name='trial_days',
        ),
        migrations.AlterField(
            model_name='plan',
            name='price_monthly',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='plan',
            name='price_yearly',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),

        # Update Subscription model
        migrations.AlterField(
            model_name='subscription',
            name='status',
            field=models.CharField(
                choices=[
                    ('free', 'Free Forever'),
                    ('active', 'Active'),
                    ('past_due', 'Past Due'),
                    ('canceled', 'Canceled'),
                    ('unpaid', 'Unpaid'),
                ],
                default='free',
                max_length=20
            ),
        ),
        migrations.AddField(
            model_name='subscription',
            name='used_conversations',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='subscription',
            name='trial_start',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='subscription',
            name='trial_end',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='subscription',
            name='current_period_end',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
