from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect, render

from calendar_app.models import AcademicEvent
from reminders.models import Notification
from reminders.services import generate_notifications_for_user

from .forms import StudentProfileForm, StudentRegistrationForm, UserUpdateForm
from .models import StudentProfile


def register(request):
    if request.method == "POST":
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Votre compte etudiant a ete cree.")
            return redirect("accounts:dashboard")
    else:
        form = StudentRegistrationForm()
    return render(request, "accounts/register.html", {"form": form})


class StudentLoginView(LoginView):
    template_name = "accounts/login.html"


class StudentLogoutView(LogoutView):
    template_name = "accounts/login.html"


@login_required
def dashboard(request):
    generate_notifications_for_user(request.user)
    upcoming_events = AcademicEvent.objects.upcoming()
    events = upcoming_events[:5]
    urgent_events = [event for event in upcoming_events if 0 <= event.days_until <= 7][:4]
    notifications = request.user.notifications.select_related("event").order_by("-created_at")[:5]
    context = {
        "events": events,
        "urgent_events": urgent_events,
        "notifications": notifications,
        "total_upcoming_events": upcoming_events.count(),
        "unread_count": request.user.notifications.filter(is_read=False).count(),
        "next_event": upcoming_events.first(),
    }
    return render(request, "accounts/dashboard.html", context)


@login_required
def profile(request):
    profile_obj, _ = StudentProfile.objects.get_or_create(user=request.user)
    if request.method == "POST":
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = StudentProfileForm(request.POST, instance=profile_obj)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Profil mis a jour.")
            return redirect("accounts:profile")
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = StudentProfileForm(instance=profile_obj)
    return render(request, "accounts/profile.html", {"user_form": user_form, "profile_form": profile_form})


def is_administrator(user):
    return user.is_authenticated and user.is_staff


@login_required
@user_passes_test(is_administrator)
def admin_supervision(request):
    context = {
        "students_count": User.objects.filter(is_staff=False).count(),
        "admins_count": User.objects.filter(is_staff=True).count(),
        "events_count": AcademicEvent.objects.count(),
        "upcoming_events_count": AcademicEvent.objects.upcoming().count(),
        "notifications_count": Notification.objects.count(),
        "unread_notifications_count_total": Notification.objects.filter(is_read=False).count(),
        "recent_events": AcademicEvent.objects.order_by("-created_at")[:6],
        "recent_users": User.objects.order_by("-date_joined")[:6],
    }
    return render(request, "accounts/admin_supervision.html", context)
