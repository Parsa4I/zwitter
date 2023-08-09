from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .forms import UserCreationForm, UserChangeForm
from .models import User, OTPCode, Following


class UserAdmin(BaseUserAdmin):
    add_form = UserCreationForm
    form = UserChangeForm

    add_fieldsets = (
        ("Main", {"fields": ("email", "password")}),
        ("Permissions", {"fields": ("is_admin", "is_superuser", "is_active")}),
    )
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "email",
                    "password",
                    "username",
                    "phone_number",
                    "is_active",
                    "is_superuser",
                    "is_admin",
                )
            },
        ),
    )

    list_display = ("pk", "email", "is_admin", "is_superuser", "is_active")
    list_filter = ("is_admin",)

    search_fields = ("email",)
    ordering = ("-last_login",)
    filter_horizontal = ()


class FollowingAdmin(admin.ModelAdmin):
    list_display = ("follower", "followed", "accepted")


admin.site.register(User, UserAdmin)
admin.site.register(OTPCode)
admin.site.register(Following, FollowingAdmin)
