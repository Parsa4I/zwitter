from django.db import models
from accounts.models import User
from django.urls import reverse


class Notification(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="notifications"
    )
    title = models.CharField(max_length=255, default="New Notification")
    message = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    mute = models.BooleanField(default=False)

    class Meta:
        ordering = ("-created",)

    def __str__(self):
        return f"{self.user} - {self.created}"

    def get_absolute_url(self):
        return reverse("notifs:notif_detail", args=[self.pk])
