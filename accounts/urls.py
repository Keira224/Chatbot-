from django.urls import path

from . import views
from . import api_views

app_name = "accounts"

urlpatterns = [
    path("inscription/", views.react_app, name="register"),
    path("connexion/", views.react_app, name="login"),
    path("deconnexion/", views.react_app, name="logout"),
    path("espace-academique/", views.academic_portal, name="academic_portal"),
    path("espace-etudiant/", views.student_portal, name="student_portal"),
    path("espace-admin/", views.admin_portal, name="admin_portal"),
    path("tableau-de-bord/", views.dashboard, name="dashboard"),
    path("profil/", views.profile, name="profile"),
    path("administration/supervision/", views.admin_supervision, name="admin_supervision"),
    path("api/session/", api_views.api_session, name="api_session"),
    path("api/auth/connexion/", api_views.api_login, name="api_login"),
    path("api/auth/inscription/", api_views.api_register, name="api_register"),
    path("api/auth/deconnexion/", api_views.api_logout, name="api_logout"),
    path("api/profil/", api_views.api_profile, name="api_profile"),
    path("api/etudiant/", api_views.api_student_dashboard, name="api_student_dashboard"),
    path("api/etudiant/chat/", api_views.api_chat, name="api_chat"),
    path("api/etudiant/notifications/lues/", api_views.api_mark_notifications_read, name="api_mark_notifications_read"),
    path("api/etudiant/preferences/", api_views.api_student_preferences, name="api_student_preferences"),
    path("api/admin/", api_views.api_admin_dashboard, name="api_admin_dashboard"),
    path("api/admin/evenements/", api_views.api_admin_event_create, name="api_admin_event_create"),
    path("api/admin/evenements/<int:pk>/", api_views.api_admin_event_detail, name="api_admin_event_detail"),
]
