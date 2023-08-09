from celery import Celery
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "zwitter.settings")

app = Celery("zwitter")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
