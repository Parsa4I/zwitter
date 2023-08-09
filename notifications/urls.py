from django.urls import path
from . import views


app_name = "notifs"
urlpatterns = [
    path("notifs-list/", views.NotificationsListView.as_view(), name="notifs_list"),
    path(
        "notif-detail/<int:pk>/",
        views.NotificationDetailView.as_view(),
        name="notif_detail",
    ),
    path(
        "delete-notif/<int:pk>/",
        views.DeleteNotificationView.as_view(),
        name="delete_notif",
    ),
    path("mark-read/<int:pk>/", views.MarkNotifReadView.as_view(), name="mark_read"),
    path(
        "mark-all-notifs-read/", views.MarkAllReadView.as_view(), name="mark_all_read"
    ),
    path("delete-all-read/", views.DeleteAllRead.as_view(), name="delete_all_read"),
]
