from django.urls import path

from . import views

app_name = "calendar_app"

urlpatterns = [
    path("", views.event_list, name="event_list"),
    path("mois/", views.monthly_calendar, name="monthly_calendar"),
    path("gestion/", views.event_manage, name="event_manage"),
    path("nouveau/", views.event_create, name="event_create"),
    path("export.ics", views.upcoming_events_ics, name="events_ics"),
    path("<int:pk>/modifier/", views.event_update, name="event_update"),
    path("<int:pk>/supprimer/", views.event_delete, name="event_delete"),
    path("<int:pk>/", views.event_detail, name="event_detail"),
    path("<int:pk>/export.ics", views.event_ics, name="event_ics"),
]
