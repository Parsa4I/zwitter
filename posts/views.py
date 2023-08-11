from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from .forms import CreatePostForm, AttachPictureForm, AttachVideoForm
from .models import Post, Tag, Like
from accounts.models import Following
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from utils import get_tags_list
from django.core.paginator import Paginator
from itertools import chain
from django.db.models import Q
from utils import notify, notify_followers, add_view
from django.http import HttpResponseForbidden
from .serializers import PostSerializer
from rest_framework.generics import ListAPIView


class PostsListView(View):
    def get(self, request):
        if request.user.is_authenticated:
            users_followings = Following.objects.filter(follower=request.user)
            following_users = []
            for following in users_followings:
                following_users.append(following.followed.pk)

            following_users_posts = Post.objects.filter(user__in=following_users)
            normal_posts = Post.objects.filter(~Q(user__in=following_users))

            posts = list(chain(following_users_posts, normal_posts))
        else:
            posts = Post.objects.all().order_by("-updated")

        paginator = Paginator(object_list=posts, per_page=10, orphans=5)
        page_number = request.GET.get("page", 1)
        posts = paginator.get_page(page_number)

        for post in posts:
            add_view(request, post)

        paginator_range = posts.paginator.get_elided_page_range(page_number)
        return render(
            request,
            "posts/posts_list.html",
            {"posts": posts, "paginator_range": paginator_range},
        )


class CreatePostView(LoginRequiredMixin, View):
    form_class = CreatePostForm
    template_name = "posts/create_form.html"

    def get(self, request):
        return render(request, self.template_name, {"form": self.form_class()})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            body = form.cleaned_data["body"]
            tag_titles = form.cleaned_data["tags"]
            tags = get_tags_list(tag_titles)

            if "post-body" in request.POST:
                post = Post.objects.create(
                    user=request.user, body=body, post_type="TXT"
                )

                for tag in tags:
                    post.tags.add(tag)
                post.save()

                notify_followers(request.user, post)
                messages.success(request, "Posted successfully", "success")
                return redirect("posts:posts")

            elif "attach-pic" in request.POST:
                request.session["post_body"] = body
                request.session["post_tags"] = [tag.pk for tag in tags]
                return redirect("posts:attach_picture")

            elif "attach-vid" in request.POST:
                request.session["post_body"] = body
                request.session["post_tags"] = [tag.pk for tag in tags]
                return redirect("posts:attach_video")
        return render(request, self.template_name, {"form": form})


class AttachPictureView(LoginRequiredMixin, View):
    form_class = AttachPictureForm
    template_name = "posts/attach_picture.html"

    def dispatch(self, request, *args, **kwargs):
        if not request.session.get("post_body"):
            return redirect("posts:create_post")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        return render(request, self.template_name, {"form": self.form_class()})

    def post(self, request):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            cd = form.cleaned_data
            post = Post.objects.create(
                user=request.user,
                body=request.session["post_body"],
                image=cd["image"],
                post_type="IMG",
            )

            root = None
            root_pk = request.session.get("replied_post_pk", None)
            if root_pk:
                root = Post.objects.get(pk=root_pk)
                if root.root:
                    root = root.root
                post.root = root
                del request.session["replied_post_pk"]

            for tag_pk in request.session["post_tags"]:
                post.tags.add(Tag.objects.get(pk=tag_pk))
            if root:
                for tag in root.tags.all():
                    post.tags.add(tag)
            post.save()
            del request.session["post_tags"]
            del request.session["post_body"]
            if root_pk:
                notify(
                    root.user,
                    "New Reply",
                    f'<a href="{request.user.get_absolute_url()}">{request.user} replied to your <a href="{root.get_absolute_url()}">root</a>.',
                )
                messages.success(request, "Replied successfully", "success")
                return redirect("posts:post_post_detail", pk=root_pk)
            notify_followers(request.user, post)
            messages.success(request, "Posted successfully", "success")
            return redirect("posts:posts")
        messages.error(
            request, "An error occurred. Fix the issues listed below.", "danger"
        )
        return render(request, self.template_name, {"form": form})


class AttachVideoView(LoginRequiredMixin, View):
    form_class = AttachVideoForm
    template_name = "posts/attach_video.html"

    def dispatch(self, request, *args, **kwargs):
        if not request.session.get("post_body"):
            return redirect("posts:create_post")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        return render(request, self.template_name, {"form": self.form_class()})

    def post(self, request):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            cd = form.cleaned_data
            post = Post.objects.create(
                user=request.user,
                body=request.session["post_body"],
                video=cd["video"],
                post_type="VID",
            )

            root = None
            root_pk = request.session.get("replied_post_pk", None)
            if root_pk:
                root = Post.objects.get(pk=root_pk)
                if root.root:
                    root = root.root
                post.root = root
                del request.session["replied_post_pk"]

            for tag_pk in request.session["post_tags"]:
                post.tags.add(Tag.objects.get(pk=tag_pk))
            if root:
                for tag in root.tags.all():
                    post.tags.add(tag)
            post.save()
            del request.session["post_tags"]
            del request.session["post_body"]
            if root_pk:
                notify(
                    root.user,
                    "New Reply",
                    f'<a href="{request.user.get_absolute_url()}">{request.user} replied to your <a href="{root.get_absolute_url()}">root</a>.',
                )
                messages.success(request, "Replied successfully", "success")
                return redirect("posts:post_post_detail", pk=root_pk)
            notify_followers(request.user, post)
            messages.success(request, "Posted successfully", "success")
            return redirect("posts:posts")
        messages.error(
            request, "An error occurred. Fix the issues listed below.", "danger"
        )
        return render(request, self.template_name, {"form": form})


class PostDetailView(View):
    def get(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        replies = post.replies.all()
        paginator = Paginator(object_list=replies, per_page=10, orphans=5)
        page_number = request.GET.get("page", 1)
        replies = paginator.get_page(page_number)
        paginator_range = replies.paginator.get_elided_page_range(page_number)

        add_view(request, post)
        for reply in replies:
            add_view(request, reply)

        return render(
            request,
            "posts/post_detail.html",
            {"post": post, "posts": replies, "paginator_range": paginator_range},
        )


class TagPostView(View):
    def get(self, request, title):
        tag = get_object_or_404(Tag, title=title)
        posts = tag.posts.distinct()
        tag_count = tag.posts.count()
        paginator = Paginator(object_list=posts, per_page=10, orphans=5)
        page_number = request.GET.get("page", 1)
        posts = paginator.get_page(page_number)
        paginator_range = posts.paginator.get_elided_page_range(page_number)
        return render(
            request,
            "posts/posts_list.html",
            {
                "posts": posts,
                "tag": tag,
                "tag_count": tag_count,
                "paginator_range": paginator_range,
            },
        )


class LikePostView(LoginRequiredMixin, View):
    def setup(self, request, *args, **kwargs):
        self.next = request.GET.get("next", None)
        return super().setup(request, *args, **kwargs)

    def get(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        try:
            Like.objects.get(user=request.user, post=post).delete()
        except:
            Like.objects.create(user=request.user, post=post)
            if request.user != post.user:
                notify(
                    post.user,
                    "Post Liked",
                    f'<a href="{request.user.get_absolute_url()}">{request.user}</a> liked your <a href="{post.get_absolute_url()}">post</a>.',
                    True,
                )
        if self.next:
            return redirect(self.next)
        return redirect(post.get_absolute_url())


class ReplyView(LoginRequiredMixin, View):
    form_class = CreatePostForm
    template_name = "posts/create_form.html"

    def get(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        request.session["replied_post_pk"] = post.pk
        return render(
            request,
            self.template_name,
            {"form": self.form_class(), "reply": True, "post": post},
        )

    def post(self, request, pk):
        form = self.form_class(request.POST)
        if form.is_valid():
            body = form.cleaned_data["body"]
            tag_titles = form.cleaned_data["tags"]
            tags = get_tags_list(tag_titles)
            root = Post.objects.get(pk=pk)
            if root.root:
                root = root.root

            if "post-body" in request.POST:
                post = Post.objects.create(
                    user=request.user, body=body, post_type="TXT", root=root
                )

                for tag in tags:
                    post.tags.add(tag)
                for tag in root.tags.all():
                    post.tags.add(tag)
                post.save()

                del request.session["replied_post_pk"]

                if request.user != root.user:
                    notify(
                        root.user,
                        "New Reply",
                        f'<a href="{request.user.get_absolute_url()}">{request.user} replied to your <a href="{root.get_absolute_url()}">root</a>.',
                    )
                messages.success(request, "Replied successfully", "success")
                return redirect("posts:post_detail", pk=root.pk)

            elif "attach-pic" in request.POST:
                request.session["post_body"] = body
                request.session["post_tags"] = [tag.pk for tag in tags]
                return redirect("posts:attach_picture")

            elif "attach-vid" in request.POST:
                request.session["post_body"] = body
                request.session["post_tags"] = [tag.pk for tag in tags]
                return redirect("posts:attach_video")
        return render(request, self.template_name, {"form": form})


class RepostView(LoginRequiredMixin, View):
    def setup(self, request, pk, *args, **kwargs):
        self.source_post = get_object_or_404(Post, pk=pk)
        return super().setup(request, *args, **kwargs)

    def get(self, request, pk):
        return render(request, "posts/repost.html", {"post": self.source_post})

    def post(self, request, pk):
        if "yes" in request.POST:
            post = Post.objects.create(user=request.user, post_type="REP")
            post.reposted_from = (
                self.source_post.reposted_from
                if self.source_post.post_type == "REP"
                else self.source_post
            )
            post.tags.set(self.source_post.tags.all())
            post.save()
            notify(
                post.reposted_from.user,
                "New Repost",
                f'<a href="{request.user.get_absolute_url()}">{request.user}</a> reposted <a href="{post.reposted_from.get_absolute_url()}">this post</a>.',
            )
            notify_followers(request.user, post)
            messages.success(request, "Reposted successfully.", "success")
            return redirect("posts:post_detail", pk=post.pk)
        if "no" in request.POST:
            return redirect("posts:post_detail", pk=self.source_post.pk)


class DeletePostView(LoginRequiredMixin, View):
    def get(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        if request.user != post.user:
            return HttpResponseForbidden(
                "You are not allowed to delete othe users' posts"
            )
        return render(request, "posts/delete_post.html", {"post": post})

    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        if request.user != post.user:
            return HttpResponseForbidden(
                "You are not allowed to delete othe users' posts"
            )
        post.delete()
        messages.success(request, "Post deleted", "success")
        return redirect("accounts:profile", pk=request.user.pk)


class PostsListAPIView(ListAPIView):
    model = Post
    serializer_class = PostSerializer

    def get_queryset(self):
        if self.request.user.is_authenticated:
            users_followings = Following.objects.filter(follower=self.request.user)
            following_users = []
            for following in users_followings:
                following_users.append(following.followed.pk)

            following_users_posts = Post.objects.filter(user__in=following_users)
            normal_posts = Post.objects.filter(~Q(user__in=following_users))

            posts = list(chain(following_users_posts, normal_posts))
        else:
            posts = Post.objects.all().order_by("-updated")

        for post in posts:
            add_view(self.request, post)

        return posts
