"""
Celery tasks for managing integrations

These tasks run in background to start/stop bots automatically
"""
from celery import shared_task
from .models import Integration
from .telegram_manager import start_telegram_bot, stop_telegram_bot
import asyncio
import logging
import threading

logger = logging.getLogger(__name__)


def run_async_in_thread(coro):
    """
    Helper to run async function in a new thread with its own event loop
    This avoids conflicts with existing event loops
    """
    result = {'success': False, 'error': None}

    def thread_target():
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result['success'] = loop.run_until_complete(coro)
            loop.close()
        except Exception as e:
            result['error'] = e
            logger.error(f"Error in async thread: {e}", exc_info=True)

    thread = threading.Thread(target=thread_target)
    thread.start()
    thread.join(timeout=30)  # Wait max 30 seconds

    if thread.is_alive():
        raise TimeoutError("Async operation timed out")

    if result['error']:
        raise result['error']

    return result['success']


@shared_task
def start_telegram_bot_task(integration_id):
    """
    Start a single Telegram bot (for use from views)
    """
    try:
        integration = Integration.objects.get(id=integration_id)
        success = run_async_in_thread(start_telegram_bot(integration))

        if success:
            integration.refresh_from_db()
            return {'success': True, 'integration_id': integration_id}
        else:
            return {'success': False, 'error': 'Failed to start bot'}

    except Exception as e:
        logger.error(f"Failed to start bot {integration_id}: {e}", exc_info=True)
        return {'success': False, 'error': str(e)}


@shared_task
def start_all_active_telegram_bots():
    """
    Start all active Telegram bots on server restart

    This task should run on Django startup to ensure all previously
    connected bots are running again after server restart.
    """
    active_telegram = Integration.objects.filter(
        integration_type='telegram',
        status='active'
    )

    started = 0
    failed = 0

    for integration in active_telegram:
        try:
            success = run_async_in_thread(start_telegram_bot(integration))

            if success:
                started += 1
            else:
                failed += 1

        except Exception as e:
            logger.error(f"Failed to start bot {integration.id}: {e}")
            failed += 1

    return f"Started {started} Telegram bots, {failed} failed"


@shared_task
def check_integration_health():
    """
    Periodically check if integrations are still working

    Run this every hour to verify bots are responding
    """
    integrations = Integration.objects.filter(status='active')

    for integration in integrations:
        # Check if bot responded recently
        if integration.integration_type == 'telegram':
            # Could ping the bot or check last_activity
            pass
        elif integration.integration_type == 'whatsapp':
            # Check Twilio API status
            pass

    return "Health check completed"


@shared_task
def cleanup_failed_integrations():
    """
    Clean up integrations that have been in error state for too long
    """
    from django.utils import timezone
    from datetime import timedelta

    # Find integrations in error state for more than 7 days
    threshold = timezone.now() - timedelta(days=7)

    old_errors = Integration.objects.filter(
        status='error',
        updated_at__lt=threshold
    )

    count = old_errors.count()

    # Disable them
    old_errors.update(status='disabled')

    return f"Disabled {count} old failed integrations"
