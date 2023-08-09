from django.db import models
from accounts.models import User
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
from django.urls import reverse


class Tag(models.Model):
    title = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("posts:tag", args=[self.title])


class Post(models.Model):
    TEXT = "TXT"
    IMAGE = "IMG"
    VIDEO = "VID"
    REPOST = "REP"
    POST_TYPE_CHOICES = [
        (TEXT, "Text"),
        (IMAGE, "Image"),
        (VIDEO, "Video"),
        (REPOST, "Repost"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    body = models.TextField(max_length=4000, null=True, blank=True)
    image = models.ImageField(null=True, blank=True)
    video = models.FileField(
        validators=[
            FileExtensionValidator(
                allowed_extensions=["MOV", "avi", "mp4", "webm", "mkv"]
            )
        ],
        null=True,
        blank=True,
    )
    post_type = models.CharField(max_length=3, choices=POST_TYPE_CHOICES, default=TEXT)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    tags = models.ManyToManyField(Tag, related_name="posts", blank=True)
    root = models.ForeignKey(
        "self", on_delete=models.CASCADE, related_name="replies", blank=True, null=True
    )
    reposted_from = models.ForeignKey(
        "self", on_delete=models.CASCADE, related_name="reposts", null=True, blank=True
    )

    class Meta:
        ordering = ("-updated",)

    def __str__(self):
        return f"{self.pk} - {self.user} - {self.post_type}"

    def save(self, *args, **kwargs):
        if not (self.image and self.video):
            if self.image:
                self.post_type = self.IMAGE
            elif self.video:
                self.post_type = self.VIDEO
            elif self.reposted_from:
                self.post_type = self.REPOST
            else:
                self.post_type = self.TEXT
            super().save(*args, **kwargs)
        else:
            raise ValidationError("A post can't have 2 media files at the same time.")

    def get_absolute_url(self):
        return reverse("posts:post_detail", args=[self.pk])

    def is_liked(self, user):
        if not user.is_authenticated:
            return False
        return Like.objects.filter(post=self, user=user).exists()

    @property
    def views_count(self):
        return PostView.objects.filter(post=self).count()


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="likes")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")

    def __str__(self):
        return f"{self.user} liked [{self.post}]"


class PostView(models.Model):
    ip = models.GenericIPAddressField()
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="views")

    def __str__(self):
        return f"{self.ip} - {self.post}"
