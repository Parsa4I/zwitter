from celery import shared_task
from utils import send_otp_code
from .models import OTPCode


@shared_task
def send_otp_code_task(recipient):
    code = send_otp_code(recipient)
    OTPCode.objects.filter(email=recipient).delete()
    OTPCode.objects.create(code=code, email=recipient)
