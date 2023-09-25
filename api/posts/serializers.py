from posts.models import Post, Like, Tag, PostView
from rest_framework import serializers
from api.accounts.serializers import UserInlineSerializer


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
            "url",
        )

    def get_likes_count(self, obj):
        return Like.objects.filter(post=obj).count()

    def get_views_count(self, obj):
        return PostView.objects.filter(post=obj).count()


class PostSerializer(PostInlineSerializer):
    user = UserInlineSerializer()

    class Meta:
        model = Post
        fields = PostInlineSerializer.Meta.fields + ("user",)
