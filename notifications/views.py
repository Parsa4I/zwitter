from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from .models import Notification
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import HttpResponseForbidden


class NotificationsListView(LoginRequiredMixin, View):
    def get(self, request):
        notifs = Notification.objects.filter(user=request.user)
        return render(request, "notifications/notifs_list.html", {"notifs": notifs})


class NotificationDetailView(LoginRequiredMixin, View):
    def get(self, request, pk):
        notif = get_object_or_404(Notification, pk=pk)
        if notif.user != request.user:
            return HttpResponseForbidden("You're not allowed on this page.")
        notif.is_read = True
        notif.save()
        return render(request, "notifications/notif_detail.html", {"notif": notif})


class DeleteNotificationView(LoginRequiredMixin, View):
    def get(self, request, pk):
        notif = get_object_or_404(Notification, pk=pk)
        if notif.user != request.user:
            return HttpResponseForbidden("You're not allowed on this page.")
        notif.delete()
        messages.success(request, "Notification deleted", "success")
        return redirect("notifs:notifs_list")


class MarkNotifReadView(LoginRequiredMixin, View):
    def get(self, request, pk):
        notif = get_object_or_404(Notification, pk=pk)
        if notif.user != request.user:
            return HttpResponseForbidden("You're not allowed on this page.")
        notif.is_read = True
        notif.save()
        messages.success(request, "Marked as read", "success")
        return redirect("notifs:notifs_list")


class MarkAllReadView(View):
    def get(self, request):
        Notification.objects.filter(user=request.user, is_read=False).update(
            is_read=True
        )
        messages.success(request, "Marked all as read", "success")
        return redirect("notifs:notifs_list")


class DeleteAllRead(View):
    def get(self, request):
        Notification.objects.filter(user=request.user, is_read=True).delete()
        messages.success(request, "Notifications deleted", "success")
        return redirect("notifs:notifs_list")
