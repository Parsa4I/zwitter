from django.shortcuts import render
from django.views import View
from django.contrib import messages
from posts.models import Post, Tag
from django.db.models import Count


class HomeView(View):
    def get(self, request):
        tags = (
            Tag.objects.annotate(Count("posts"))
            .order_by("-posts__count")
            .order_by("-posts__updated")[:3]
        )
        return render(request, "pages/home.html", {"tags": tags})
