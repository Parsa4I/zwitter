from django.contrib import admin
from .models import Post, Tag, Like, PostView
from .forms import PostAdminForm


class PostAdmin(admin.ModelAdmin):
    form = PostAdminForm
    list_display = ("pk", "user", "updated", "post_type")
    raw_id_fields = ("root", "tags")


class LikeAdmin(admin.ModelAdmin):
    raw_id_fields = ("user", "post")


admin.site.register(Post, PostAdmin)
admin.site.register(Tag)
admin.site.register(Like, LikeAdmin)
admin.site.register(PostView)
