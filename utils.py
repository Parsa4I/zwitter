import random
from django.core.mail import send_mail
from django.conf import settings
from posts.models import Tag, Post, PostView
from notifications.models import Notification
from accounts.models import Following


def send_otp_code(recipient):
    code = random.randint(1000, 9999)
    sent = send_mail(
        subject="Zwitter - OTP",
        message=f"Your code is:\n{code}",
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[recipient],
    )
    if sent:
        return code
    return False


def get_tags_list(tag_titles):
    tags = []
    if tag_titles != "":
        tag_titles = tag_titles.split(",")
        tag_titles = [tag.strip().lower().replace(" ", "_") for tag in tag_titles]
        for tag_title in tag_titles:
            if not tag_title.isspace() and tag_title != "":
                try:
                    tags.append(Tag.objects.get(title=tag_title))
                except:
                    tags.append(Tag.objects.create(title=tag_title))
    return tags


def notify(user, title, message, mute=False):
    Notification.objects.create(user=user, message=message, title=title, mute=mute)


def notify_followers(user, post):
    followings = Following.objects.filter(followed=user)
    for following in followings:
        if not following.mute:
            notify(
                following.follower,
                "New Post",
                f'<a href="{following.followed.get_absolute_url()}">{following.followed}</a> has a new <a href="{post.get_absolute_url()}">post</a>.',
            )


def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


def add_view(request, post):
    ip = get_client_ip(request)
    PostView.objects.get_or_create(ip=ip, post=post)
