from django.contrib import admin
from django.urls import include, path

from accounts.views import home_redirect

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home_redirect, name="home"),
    path("accounts/", include("accounts.urls")),
    path("calendrier/", include("calendar_app.urls")),
    path("chatbot/", include("chatbot.urls")),
    path("rappels/", include("reminders.urls")),
]
