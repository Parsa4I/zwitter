from rest_framework import serializers
from .validators import validate_unique_email
from accounts.models import User, Following


class UserRegisterSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255, validators=[validate_unique_email])
    password1 = serializers.CharField(min_length=4, max_length=255)
    password2 = serializers.CharField(min_length=4, max_length=255)

    def validate(self, attrs):
        pass1 = attrs.get("password1")
        pass2 = attrs.get("password2")
        if pass1 and pass2 and pass1 != pass2:
            raise serializers.ValidationError("Passwords must match.")
        return attrs


class OTPCodeSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)
    otp_code = serializers.IntegerField(min_value=1000, max_value=9999)


class UserInlineSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField("api_accounts:user")

    class Meta:
        model = User
        fields = ("username", "email", "url")


class UserSerializer(serializers.ModelSerializer):
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "is_active",
            "is_admin",
            "is_superuser",
            "last_login",
            "followers_count",
            "following_count",
        )

    def get_followers_count(self, obj):
        return Following.objects.filter(followed=obj, accepted=True).count()

    def get_following_count(self, obj):
        return Following.objects.filter(follower=obj, accepted=True).count()


class FollowRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Following
        fields = ("follower",)


class FollowingSerializer(serializers.ModelSerializer):
    follower = UserInlineSerializer()
    followed = UserInlineSerializer()

    class Meta:
        model = Following
        fields = ("follower", "followed", "mute")
