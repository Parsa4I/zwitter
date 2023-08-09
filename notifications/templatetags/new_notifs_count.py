from django import template
from ..models import Notification


register = template.Library()


def new_notifs_count(user):
    return Notification.objects.filter(user=user, is_read=False).count()


register.filter("new_notifs_count", new_notifs_count)
