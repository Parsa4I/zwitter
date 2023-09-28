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


class PostSerializer(serializers.ModelSerializer):
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
    user = UserInlineSerializer()

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
            "user",
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


class PostCreateUpdateSerializer(serializers.Serializer):
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

    def validate(self, attrs):
        if attrs.get("image") and attrs.get("video"):
            raise ValidationError("A post can only have one media file.")
        return super().validate(attrs)

    def create(self, validated_data):
        post = Post.objects.create(
            user=self.context["request"].user,
            body=validated_data["body"],
            image=validated_data.get("image"),
            video=validated_data.get("video"),
        )
        post.tags.set(get_tags_list(validated_data.get("tags", "")))
        post.save()

        return post

    def update(self, instance, validated_data):
        instance.body = validated_data.get("body", instance.body)

        image = validated_data.get("image")
        video = validated_data.get("video")

        if instance.post_type == "IMG":
            if video:
                instance.image = None
                instance.video = video
            else:
                instance.image = image

        if instance.post_type == "VID":
            if image:
                instance.video = None
                instance.image = image
            else:
                instance.video = video

        tags = validated_data.get("tags", "")
        if tags:
            instance.tags = get_tags_list(tags)

        instance.save()
        return instance
