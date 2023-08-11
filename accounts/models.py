from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from .managers import UserManager
from django.core.validators import MinValueValidator, MaxValueValidator
from django.urls import reverse


class User(AbstractBaseUser):
    username = models.CharField(max_length=255, blank=True, null=True, unique=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=11, blank=True, null=True, unique=True)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = []

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin

    def __str__(self):
        if self.username:
            return self.username
        return self.email

    def get_absolute_url(self):
        return reverse("accounts:profile", args=[self.pk])

    def is_followed(self, by):
        return Following.objects.filter(follower=by, followed=self).exists()

    def __str__(self):
        if self.username:
            return self.username
        return self.email


class OTPCode(models.Model):
    code = models.PositiveSmallIntegerField(
        validators=[MaxValueValidator(9999), MinValueValidator(1000)]
    )
    email = models.EmailField()

    def __str__(self):
        return f"{self.code} - {self.email}"


class Following(models.Model):
    follower = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="following"
    )
    followed = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="followers"
    )
    accepted = models.BooleanField(default=False)
    mute = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.follower} followed {self.followed}"
