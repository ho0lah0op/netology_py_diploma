import os

from celery import Celery


CELERY_TASK_ALWAYS_EAGER = False

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'orders.settings')
celery_app = Celery('orders')
celery_app.config_from_object('django.conf:settings', namespace='CELERY')
celery_app.autodiscover_tasks()