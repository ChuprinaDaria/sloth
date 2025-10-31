import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

app = Celery('sloth')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Celery Beat Schedule
app.conf.beat_schedule = {
    # Subscriptions
    'check-trial-expirations': {
        'task': 'apps.subscriptions.tasks.check_trial_expirations',
        'schedule': crontab(hour=0, minute=0),  # Daily at 00:00
    },
    'process-subscription-billing': {
        'task': 'apps.subscriptions.tasks.process_subscription_billing',
        'schedule': crontab(hour=1, minute=0),  # Daily at 01:00
    },
    'check-usage-limits': {
        'task': 'apps.subscriptions.tasks.check_usage_limits',
        'schedule': crontab(minute='0', hour='*/1'),  # Every hour
    },

    # Referrals
    'check-referral-rewards': {
        'task': 'apps.referrals.tasks.check_referral_rewards',
        'schedule': crontab(hour=2, minute=0),  # Daily at 02:00
    },
    'update-referral-stats': {
        'task': 'apps.referrals.tasks.update_referral_stats',
        'schedule': crontab(minute='0', hour='*/1'),  # Every hour
    },

    # Documents
    'cleanup-old-files': {
        'task': 'apps.documents.tasks.cleanup_old_files',
        'schedule': crontab(day_of_week=0, hour=3, minute=0),  # Weekly on Sunday at 03:00
    },
}

app.conf.timezone = 'UTC'


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
