import os
from celery import Celery
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'orphanage_backend.settings.base')

app = Celery('orphanage_backend')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Celery Beat Schedule
app.conf.beat_schedule = {
    'send-daily-reports': {
        'task': 'apps.reports.tasks.generate_daily_reports',
        'schedule': 86400.0,  # 24 hours
    },
    'check-medical-appointments': {
        'task': 'apps.planning.tasks.check_upcoming_appointments',
        'schedule': 3600.0,  # 1 hour
    },
    'inventory-alerts': {
        'task': 'apps.inventory.tasks.check_low_stock',
        'schedule': 21600.0,  # 6 hours
    },
    'cleanup-expired-tokens': {
        'task': 'apps.accounts.tasks.cleanup_expired_tokens',
        'schedule': 3600.0,  # 1 hour
    },
}

app.conf.timezone = 'Europe/Paris'

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
