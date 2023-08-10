from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from .forms import UserRegisterForm, VerifyForm, LoginForm, ChangeUsernameForm
from .models import User, OTPCode, Following
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
)
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from posts.models import Post
from django.urls import reverse
from . import tasks
from django.core.paginator import Paginator
from utils import notify, add_view


class UserRegisterView(View):
    form_class = UserRegisterForm
    template_name = "accounts/register.html"

    def get(self, request):
        return render(request, self.template_name, {"form": self.form_class()})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            tasks.send_otp_code_task.delay(cd["email"])
            request.session["user_registration_info"] = {
                "email": cd["email"],
                "password": cd["password"],
            }
            messages.success(request, "Code sent.", "success")
            return redirect("accounts:verify")
        messages.error(
            request, "Invalid form. Please fix the issues listed below.", "danger"
        )
        return render(request, self.template_name, {"form": form})


class Verify(View):
    form_class = VerifyForm
    template_name = "accounts/verify.html"

    def get(self, request):
        return render(request, self.template_name, {"form": self.form_class()})

    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():
            email = request.session["user_registration_info"]["email"]
            password = request.session["user_registration_info"]["password"]
            otp = get_object_or_404(OTPCode, email=email)

            if otp.code == form.cleaned_data["code"]:
                user = User.objects.create_user(email=email, password=password)
                messages.success(request, "Signed up successfully.", "success")
                del request.session["user_registration_info"]
                otp.delete()
                user = authenticate(request, email=email, password=password)
                login(request, user)
                return redirect("accounts:profile", pk=user.pk)

            messages.error(request, "Wrong code", "danger")
            return render(request, self.template_name, {"form": self.form_class()})

        return render(request, self.template_name, {"form": form})


class LoginView(View):
    form_class = LoginForm
    template_name = "accounts/login.html"

    def setup(self, request, *args, **kwargs):
        self.next = request.GET.get("next", None)
        return super().setup(request, *args, **kwargs)

    def get(self, request):
        return render(request, self.template_name, {"form": self.form_class()})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            cd = form.cleaned_data

            user = authenticate(request, email=cd["email"], password=cd["password"])
            if user:
                login(request, user)
                messages.success(request, "Logged in successfully.", "success")
                if self.next:
                    return redirect(self.next)
                return redirect("accounts:profile", pk=user.pk)

            messages.error(request, "username and/or password are wrong.", "danger")
        return render(request, self.template_name, {"form": form})


class LogoutView(View):
    def get(self, request):
        if request.user.is_authenticated:
            logout(request)
            messages.success(request, "Logged out successfully", "success")
        else:
            messages.error(request, "You are not logged in.", "danger")
        return redirect("pages:home")


class UserPasswordResetView(PasswordResetView):
    template_name = "accounts/password_reset.html"
    success_url = reverse_lazy("accounts:password_reset_done")
    email_template_name = "accounts/email_template.html"


class UserPasswordResetDoneView(PasswordResetDoneView):
    template_name = "accounts/password_reset_done.html"


class UserPasswordResetConfirmView(PasswordResetConfirmView):
    success_url = reverse_lazy("accounts:password_reset_complete")
    template_name = "accounts/password_reset_confirm.html"


class UserPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = "accounts/password_reset_complete.html"


class ProfileView(View):
    template_name = "accounts/profile.html"

    def get(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        posts = Post.objects.filter(user=user)
        paginator = Paginator(object_list=posts, per_page=10, orphans=5)
        page_number = request.GET.get("page", 1)
        posts = paginator.get_page(page_number)
        paginator_range = posts.paginator.get_elided_page_range(page_number)
        if request.user == user and not user.username:
            change_username_url = reverse("accounts:change_username")
            messages.warning(
                request,
                f'Your profile is not complete. Add a username <a href="{change_username_url}">here</a>.',
                "warning safe",
            )

        follow_requests = None
        if request.user == user:
            follow_requests = Following.objects.filter(followed=user, accepted=False)

        following = Following.objects.filter(follower=user, accepted=True)
        followers = Following.objects.filter(followed=user, accepted=True)
        is_requested = Following.objects.filter(
            follower=request.user, followed=user, accepted=False
        ).exists()
        is_followed = Following.objects.filter(
            follower=request.user, followed=user, accepted=True
        ).exists()
        is_mute = False
        if is_followed:
            is_mute = Following.objects.get(
                follower=request.user, followed=user, accepted=True
            ).mute

        for post in posts:
            add_view(request, post)

        return render(
            request,
            self.template_name,
            {
                "posts": posts,
                "profile_user": user,
                "follow_requests": follow_requests,
                "following": following,
                "followers": followers,
                "paginator_range": paginator_range,
                "is_requested": is_requested,
                "is_followed": is_followed,
                "is_mute": is_mute,
            },
        )


class ChangeUsernameView(LoginRequiredMixin, View):
    form_class = ChangeUsernameForm
    template_name = "accounts/change_username.html"

    def get(self, request):
        return render(request, self.template_name, {"form": self.form_class()})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            if not User.objects.filter(username=username).exists():
                request.user.username = username
                request.user.save()
                messages.success(request, "Username successfully changed.", "success")
                return redirect("accounts:profile", pk=request.user.pk)
            else:
                messages.error(request, "This username already exists.", "danger")
        return render(request, self.template_name, {"form": form})


class FollowView(LoginRequiredMixin, View):
    def setup(self, request, *args, **kwargs):
        self.next = request.GET.get("next")
        return super().setup(request, *args, **kwargs)

    def get(self, request, pk):
        user_to_follow = get_object_or_404(User, pk=pk)

        if user_to_follow == request.user:
            messages.error(request, "You can't follow yourself. (Obviously!)", "danger")
            return redirect("accounts:profile", pk=user_to_follow.pk)

        if Following.objects.filter(
            follower=request.user, followed=user_to_follow
        ).exists():
            Following.objects.get(
                follower=request.user, followed=user_to_follow
            ).delete()
            notify(
                user_to_follow,
                "Unfollowed",
                f'<a href="{request.user.get_absolute_url()}">{request.user}</a> has unfollowed you.',
            )
            messages.success(request, "Unfollowed", "success")
            return redirect("accounts:profile", pk=user_to_follow.pk)

        Following.objects.create(
            follower=request.user, followed=user_to_follow, accepted=False
        )
        notify(
            user_to_follow,
            "New Follow Request",
            f'<a href="{request.user.get_absolute_url()}">{request.user}</a> wants to follow you. Check out your <a href="/accounts/follow-requests/"> follow requests</a>.',
        )
        messages.success(request, "Following request sent", "success")
        return redirect("accounts:profile", pk=user_to_follow.pk)


class FollowRequests(LoginRequiredMixin, View):
    def get(self, request):
        follow_requests = Following.objects.filter(
            followed=request.user, accepted=False
        )
        return render(
            request,
            "accounts/follow_requests.html",
            {"follow_requests": follow_requests},
        )


class AcceptFollow(LoginRequiredMixin, View):
    def get(self, reqeust, pk):
        following = get_object_or_404(Following, pk=pk)
        if reqeust.user == following.followed:
            following.accepted = True
            following.save()
            notify(
                following.follower,
                "Follow Request Accepted",
                f'<a href="{following.followed.get_absolute_url()}">following.followed</a> has accepted your follow request.',
            )
            return redirect("accounts:follow_requests")
        return redirect("accounts:profile", pk=reqeust.user.pk)


class DeclineFollow(LoginRequiredMixin, View):
    def get(self, reqeust, pk):
        following = get_object_or_404(Following, pk=pk)
        if reqeust.user == following.followed:
            following.delete()
            notify(
                following.follower,
                "Follow Request Declined",
                f'<a href="{following.followed.get_absolute_url()}">following.followed</a> has declined your follow request.',
            )
            return redirect("accounts:follow_requests")
        return redirect("accounts:profile", pk=reqeust.user.pk)


class FollowersView(View):
    def get(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        followers = Following.objects.filter(followed=user)
        return render(
            request,
            "accounts/follows.html",
            {"follows": followers, "followers": True, "profile_user": user},
        )


class FollowingView(View):
    def get(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        followers = Following.objects.filter(follower=user)
        return render(
            request,
            "accounts/follows.html",
            {"follows": followers, "followers": False, "profile_user": user},
        )


class MuteView(View):
    def get(self, request, pk):
        following = get_object_or_404(
            Following, follower=request.user, followed=get_object_or_404(User, pk=pk)
        )
        if following.mute:
            following.mute = False
        else:
            following.mute = True
        following.save()
        return redirect("accounts:profile", pk=following.followed.pk)


# class CustomObtainAuthToken(ObtainAuthToken):
#     serializer_class = CustomAuthTokenSerializer

#     def post(self, request, *args, **kwargs):
#         serializer = self.serializer_class(
#             data=request.data, context={"request": request}
#         )
#         serializer.is_valid(raise_exception=True)
#         user = serializer.validated_data["user"]
#         token, created = Token.objects.get_or_create(user=user)
#         return Response({"token": token.key})


# class UserRegisterAPIView(APIView):
#     def post(self, request):
#         serializer = UserRegisterSerializer(data=request.data)
#         if serializer.is_valid():
#             user = User.objects.create_user(
#                 email=serializer.validated_data["email"],
#                 password=serializer.validated_data["password"],
#             )
#             token = Token.objects.create(user=user)
#             return Response({"token": token.key})
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class UserLoginAPIView(APIView):
#     def post(self, request):
#         serializer = UserLoginSerializer(data=request.data)
#         if serializer.is_valid():
#             username = serializer.data.get("username", None)
#             password = serializer.data.get("password", None)
#             user = authenticate(request, email=username, password=password)
#             if username and password:
#                 token, created = Token.objects.get_or_create(user=user)
#                 return Response(
#                     {"token": token.key, "user": UserSerializer(instance=user).data}
#                 )
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
