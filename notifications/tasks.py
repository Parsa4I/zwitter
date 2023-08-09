from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task
def send_notif_email_task(subject, to):
    send_mail(
        subject,
        "Check the details on our website!",
        settings.EMAIL_HOST_USER,
        (to,),
    )
