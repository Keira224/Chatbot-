from django.urls import path

from . import views

app_name = "reminders"

urlpatterns = [
    path("preferences/", views.preferences, name="preferences"),
    path("notifications/", views.notifications, name="notifications"),
    path("notifications/tout-lire/", views.mark_all_as_read, name="mark_all_as_read"),
    path("notifications/<int:pk>/lue/", views.mark_as_read, name="mark_as_read"),
]
