from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("inscription/", views.register, name="register"),
    path("connexion/", views.StudentLoginView.as_view(), name="login"),
    path("deconnexion/", views.StudentLogoutView.as_view(), name="logout"),
    path("tableau-de-bord/", views.dashboard, name="dashboard"),
    path("profil/", views.profile, name="profile"),
    path("administration/supervision/", views.admin_supervision, name="admin_supervision"),
]
