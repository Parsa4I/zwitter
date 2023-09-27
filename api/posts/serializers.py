from posts.models import Post, Like, Tag, PostView
from rest_framework import serializers
from api.accounts.serializers import UserInlineSerializer
from django.core.validators import FileExtensionValidator
from rest_framework.exceptions import ValidationError
from utils import get_tags_list


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("pk", "title")


class PostInlineSerializer(serializers.ModelSerializer):
    likes_count = serializers.SerializerMethodField()
    tags = TagSerializer(many=True)
    views_count = serializers.SerializerMethodField()
    url = serializers.HyperlinkedIdentityField("api_posts:post_detail")
    reposted_from = serializers.HyperlinkedRelatedField(
        "api_posts:post_detail", read_only=True
    )
    root = serializers.HyperlinkedRelatedField("api_posts:post_detail", read_only=True)
    reposts_count = serializers.SerializerMethodField()
    replies_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = (
            "pk",
            "body",
            "image",
            "video",
            "post_type",
            "created",
            "updated",
            "tags",
            "root",
            "reposted_from",
            "likes_count",
            "views_count",
            "reposts_count",
            "replies_count",
            "url",
        )

    def get_likes_count(self, obj):
        return Like.objects.filter(post=obj).count()

    def get_views_count(self, obj):
        return PostView.objects.filter(post=obj).count()

    def get_reposts_count(self, obj):
        return Post.objects.filter(reposted_from=obj).count()

    def get_replies_count(self, obj):
        return obj.replies.count()


class PostSerializer(PostInlineSerializer):
    user = UserInlineSerializer()

    class Meta:
        model = Post
        fields = PostInlineSerializer.Meta.fields + ("user",)


class PostCreateSerializer(serializers.Serializer):
    body = serializers.CharField()
    image = serializers.ImageField(required=False)
    video = serializers.FileField(
        required=False,
        validators=[
            FileExtensionValidator(
                allowed_extensions=["MOV", "avi", "mp4", "webm", "mkv"]
            )
        ],
    )
    tags = serializers.CharField(required=False)
