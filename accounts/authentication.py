from django.contrib.auth.backends import BaseBackend
from .models import User


class UsernameAuthBackend(BaseBackend):
    def authenticate(self, request, email=None, password=None):
        try:
            user = User.objects.get(username=email)
            if user.check_password(password):
                return user
            return None
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
