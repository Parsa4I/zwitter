from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from posts.models import Post, Tag, Like
from .serializers import PostSerializer, PostCreateSerializer
from accounts.models import User, Following
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from utils import get_tags_list
from rest_framework import status
from rest_framework.exceptions import ValidationError
from django.db.models import Q
from itertools import chain


class PostAPIView(APIView):
    def get(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        serializer = PostSerializer(post, context={"request": request})
        return Response(serializer.data)


class PostsListAPIView(generics.GenericAPIView):
    def get(self, request):
        if request.user.is_authenticated:
            user_followings = Following.objects.filter(
                follower=request.user, accepted=True
            )

            following_users = []
            for following in user_followings:
                following_users.append(following.followed.pk)

            following_users_posts = Post.objects.filter(user__in=following_users)

            normal_posts = Post.objects.filter(~Q(user__in=following_users))

            posts = following_users_posts | normal_posts
        else:
            posts = Post.objects.all()

        q = request.GET.get("q")
        if q:
            posts = posts.search(q)

        page = self.paginate_queryset(posts)

        serializer = PostSerializer(page, many=True, context={"request": request})
        return self.get_paginated_response(serializer.data)


class UserPostsListAPIView(generics.GenericAPIView):
    def get(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        posts = Post.objects.filter(user=user)
        page = self.paginate_queryset(posts)
        serializer = PostSerializer(page, many=True, context={"request": request})
        return self.get_paginated_response(serializer.data)


class TagPostsAPIView(generics.GenericAPIView):
    def get(self, request, title):
        tag = get_object_or_404(Tag, title=title)
        posts = tag.posts.all()
        page = self.paginate_queryset(posts)
        serializer = PostSerializer(page, many=True, context={"request": request})
        return self.get_paginated_response(serializer.data)


class PostCreateAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = PostCreateSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            if data.get("image") and data.get("video"):
                raise ValidationError("A post can only have one media file.")
            post = Post.objects.create(
                user=request.user,
                body=data["body"],
                image=data.get("image"),
                video=data.get("video"),
            )
            post.tags.set(get_tags_list(data.get("tags", "")))
            post.save()
            return Response(
                {"message": f"{post.post_type} post created."}, status.HTTP_201_CREATED
            )
        return Response({"errors": serializer.errors}, status.HTTP_400_BAD_REQUEST)


class RepostAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, pk):
        source_post = get_object_or_404(Post, pk=pk)
        post = Post.objects.create(user=request.user, post_type="REP")
        post.reposted_from = (
            source_post.reposted_from if source_post.post_type == "REP" else source_post
        )
        post.tags.set(source_post.tags.all())
        post.save()
        return Response({"message": "Reposted successfully."}, status.HTTP_200_OK)


class ReplyAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, pk):
        serializer = PostCreateSerializer(data=request.data)
        if serializer.is_valid():
            root = get_object_or_404(Post, pk=pk)
            data = serializer.validated_data
            if data.get("image") and data.get("video"):
                raise ValidationError("A post can only have one media file.")
            post = Post.objects.create(
                user=request.user,
                body=data["body"],
                image=data.get("image"),
                video=data.get("video"),
            )
            post.tags.set(get_tags_list(data.get("tags", "")))
            post.tags.add(*list(root.tags.all()))
            post.root = root
            post.save()
            return Response(
                {"message": f"{post.post_type} post created."}, status.HTTP_200_OK
            )
        return Response({"errors": serializer.errors}, status.HTTP_400_BAD_REQUEST)


class LikePostAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        like, created = Like.objects.get_or_create(user=request.user, post=post)

        if not created:
            like.delete()
            return Response({"message": "Post unliked."}, status.HTTP_200_OK)

        return Response({"message": "Post liked."}, status.HTTP_200_OK)


class DeletePostAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def delete(self, request, pk):
        post = get_object_or_404(Post, pk=pk)

        if post.user == request.user:
            post.delete()
            return Response({"message": "Post deleted."}, status.HTTP_200_OK)

        return Response(
            {"message": "This post is not yours to delete."},
            status.HTTP_400_BAD_REQUEST,
        )


class UpdatePostAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def patch(self, request, pk):
        serializer = PostCreateSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            post = get_object_or_404(Post, pk=pk, user=request.user)

            if data.get("body"):
                post.body = data.get("body")

            if data.get("image") and data.get("video"):
                raise ValidationError("A post can't have more than one media file.")

            if data.get("image"):
                post.video = None
                post.image = data.get("image")

            if data.get("video"):
                post.image = None
                post.video = data.get("video")

            if data.get("tags"):
                tags = get_tags_list(data.get("tags"))
                post.tags.set(tags)

            post.save()

            return Response({"message": "Post updated"}, status.HTTP_200_OK)


class IsLikedAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        is_liked = Like.objects.filter(user=request.user, post=post).exists()
        return Response({"is_liked": is_liked})
