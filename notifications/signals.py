from django.dispatch import receiver
from django.db.models.signals import post_save
from django.core.mail import send_mail
from django.conf import settings
from .models import Notification
from . import tasks


@receiver(post_save, sender=Notification)
def notify_user(sender, instance, created, **kwargs):
    if created and not instance.mute:
        tasks.send_notif_email_task.delay(instance.title, instance.user.email)
