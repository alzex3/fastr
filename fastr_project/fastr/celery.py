import os

from celery import Celery


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fastr.settings')

app = Celery('fastr')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
