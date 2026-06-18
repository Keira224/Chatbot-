import json

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_http_methods, require_POST

from calendar_app.forms import AcademicEventForm
from calendar_app.models import AcademicEvent
from chatbot.models import ChatMessage
from chatbot.services import answer_question
from reminders.models import Notification
from reminders.services import generate_notifications_for_user, get_or_create_preference
from .forms import StudentRegistrationForm
from .models import StudentProfile


def json_body(request):
    try:
        return json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return None


def event_data(event):
    return {
        "id": event.pk,
        "title": event.title,
        "description": event.description,
        "event_type": event.event_type,
        "event_type_label": event.get_event_type_display(),
        "start_date": event.start_date.isoformat(),
        "end_date": event.end_date.isoformat(),
        "location": event.location,
        "days_until": event.days_until,
        "status": event.status_label,
        "urgency": event.urgency_class,
        "detail_url": "/accounts/espace-academique/?view=calendar",
        "calendar_url": f"/calendrier/{event.pk}/export.ics",
    }


def notification_data(notification):
    return {
        "id": notification.pk,
        "message": notification.message,
        "is_read": notification.is_read,
        "created_at": notification.created_at.isoformat(),
        "event": event_data(notification.event),
    }


def require_staff(request):
    if not request.user.is_staff:
        return JsonResponse({"detail": "Acces reserve aux administrateurs."}, status=403)
    return None


def user_role_data(user):
    if user.is_staff:
        return {"value": "admin", "label": "Administrateur"}
    try:
        profile = user.student_profile
    except StudentProfile.DoesNotExist:
        profile = StudentProfile.objects.create(user=user)
    return {"value": profile.role, "label": profile.get_role_display()}


def session_user_data(user):
    profile = None if user.is_staff else StudentProfile.objects.get_or_create(user=user)[0]
    role = user_role_data(user)
    return {
        "id": user.pk,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "is_staff": user.is_staff,
        "role": role["value"],
        "role_label": role["label"],
        "student_number": getattr(profile, "student_number", ""),
        "program": getattr(profile, "program", ""),
        "level": getattr(profile, "level", ""),
        "phone": getattr(profile, "phone", ""),
    }


def api_session(request):
    if not request.user.is_authenticated:
        return JsonResponse({"authenticated": False})
    return JsonResponse({"authenticated": True, "user": session_user_data(request.user)})


@require_POST
def api_login(request):
    payload = json_body(request)
    if payload is None:
        return JsonResponse({"detail": "Corps JSON invalide."}, status=400)
    username = str(payload.get("username", "")).strip()
    password = str(payload.get("password", ""))
    user = authenticate(request, username=username, password=password)
    if user is None:
        return JsonResponse({"detail": "Identifiant ou mot de passe incorrect."}, status=400)
    login(request, user)
    return JsonResponse({"user": session_user_data(user)})


@require_POST
def api_register(request):
    payload = json_body(request)
    if payload is None:
        return JsonResponse({"detail": "Corps JSON invalide."}, status=400)
    form = StudentRegistrationForm(payload)
    if not form.is_valid():
        return JsonResponse({"errors": form.errors.get_json_data()}, status=400)
    user = form.save()
    login(request, user)
    return JsonResponse({"user": session_user_data(user)}, status=201)


@require_POST
def api_logout(request):
    logout(request)
    return JsonResponse({"ok": True})


@login_required
@require_http_methods(["PUT"])
def api_profile(request):
    if request.user.is_staff:
        return JsonResponse({"detail": "Le profil administrateur est gere dans Django Admin."}, status=403)
    payload = json_body(request)
    if payload is None:
        return JsonResponse({"detail": "Corps JSON invalide."}, status=400)

    role = payload.get("role")
    valid_roles = {value for value, _ in StudentProfile.ROLE_CHOICES}
    if role not in valid_roles:
        return JsonResponse({"detail": "Role academique invalide."}, status=400)

    email = str(payload.get("email", "")).strip().lower()
    if not email:
        return JsonResponse({"detail": "L'adresse email est obligatoire."}, status=400)
    if User.objects.filter(email__iexact=email).exclude(pk=request.user.pk).exists():
        return JsonResponse({"detail": "Cette adresse email est deja utilisee."}, status=400)

    user = request.user
    user.first_name = str(payload.get("first_name", "")).strip()
    user.last_name = str(payload.get("last_name", "")).strip()
    user.email = email
    user.save(update_fields=["first_name", "last_name", "email"])

    profile, _ = StudentProfile.objects.get_or_create(user=user)
    profile.role = role
    profile.student_number = str(payload.get("student_number", "")).strip()
    profile.program = str(payload.get("program", "")).strip()
    profile.level = str(payload.get("level", "")).strip()
    profile.phone = str(payload.get("phone", "")).strip()
    profile.save()
    return JsonResponse({"user": session_user_data(user)})


@login_required
def api_student_dashboard(request):
    if request.user.is_staff:
        return JsonResponse({"detail": "Utilisez l'espace administrateur."}, status=403)

    generate_notifications_for_user(request.user)
    all_events = AcademicEvent.objects.all().order_by("-start_date", "title")
    upcoming = AcademicEvent.objects.upcoming()
    notifications = request.user.notifications.select_related("event").order_by("-created_at")
    preference = get_or_create_preference(request.user)
    chat_messages = request.user.chat_messages.order_by("-created_at")[:8]

    return JsonResponse(
        {
            "summary": {
                "upcoming_events": upcoming.count(),
                "unread_notifications": notifications.filter(is_read=False).count(),
                "next_event": event_data(upcoming.first()) if upcoming.exists() else None,
            },
            "events": [event_data(event) for event in all_events],
            "upcoming_events": [event_data(event) for event in upcoming[:12]],
            "notifications": [notification_data(item) for item in notifications[:12]],
            "preference": {
                "event_types": preference.selected_event_types(),
                "reminder_days": preference.reminder_days,
                "email_enabled": preference.email_enabled,
            },
            "event_types": [
                {"value": value, "label": label}
                for value, label in AcademicEvent.EVENT_TYPES
            ],
            "chat_messages": [
                {
                    "id": message.pk,
                    "question": message.question,
                    "answer": message.answer,
                    "source": message.source,
                    "source_label": message.get_source_display(),
                    "created_at": message.created_at.isoformat(),
                }
                for message in reversed(chat_messages)
            ],
        }
    )


@login_required
@require_POST
def api_chat(request):
    if request.user.is_staff:
        return JsonResponse({"detail": "Le chatbot est disponible dans l'espace academique."}, status=403)
    payload = json_body(request)
    question = (payload or {}).get("question", "").strip()
    if not question:
        return JsonResponse({"detail": "La question est obligatoire."}, status=400)
    result = answer_question(question, include_source=True)
    message = ChatMessage.objects.create(
        user=request.user,
        question=question,
        answer=result["answer"],
        source=result["source"],
    )
    return JsonResponse(
        {
            "message": {
                "id": message.pk,
                "question": message.question,
                "answer": message.answer,
                "source": message.source,
                "source_label": message.get_source_display(),
                "created_at": message.created_at.isoformat(),
            }
        },
        status=201,
    )


@login_required
@require_POST
def api_mark_notifications_read(request):
    if request.user.is_staff:
        return JsonResponse({"detail": "Action reservee aux utilisateurs academiques."}, status=403)
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return JsonResponse({"ok": True})


@login_required
@require_http_methods(["PUT"])
def api_student_preferences(request):
    if request.user.is_staff:
        return JsonResponse({"detail": "Action reservee aux utilisateurs academiques."}, status=403)
    payload = json_body(request)
    if payload is None:
        return JsonResponse({"detail": "Corps JSON invalide."}, status=400)

    valid_types = {value for value, _ in AcademicEvent.EVENT_TYPES}
    event_types = payload.get("event_types", [])
    reminder_days = payload.get("reminder_days")
    valid_days = {value for value, _ in get_or_create_preference(request.user).REMINDER_DAY_CHOICES}
    if not isinstance(event_types, list) or not set(event_types).issubset(valid_types):
        return JsonResponse({"detail": "Types d'evenements invalides."}, status=400)
    if reminder_days not in valid_days:
        return JsonResponse({"detail": "Delai de rappel invalide."}, status=400)

    preference = get_or_create_preference(request.user)
    preference.set_event_types(event_types)
    preference.reminder_days = reminder_days
    preference.email_enabled = bool(payload.get("email_enabled"))
    preference.save()
    generate_notifications_for_user(request.user)
    return JsonResponse({"ok": True})


@login_required
def api_admin_dashboard(request):
    denied = require_staff(request)
    if denied:
        return denied

    events = AcademicEvent.objects.all()
    today = timezone.localdate()
    academic_users = User.objects.filter(is_staff=False)
    recent_users = User.objects.select_related("student_profile").order_by("-date_joined")
    return JsonResponse(
        {
            "summary": {
                "users": academic_users.count(),
                "students": academic_users.filter(student_profile__role=StudentProfile.STUDENT).count(),
                "teachers": academic_users.filter(student_profile__role=StudentProfile.TEACHER).count(),
                "events": events.count(),
                "upcoming_events": events.filter(end_date__gte=today).count(),
                "unread_notifications": Notification.objects.filter(is_read=False).count(),
            },
            "events": [event_data(event) for event in events.order_by("start_date")],
            "users": [admin_user_data(user) for user in recent_users],
            "event_types": [
                {"value": value, "label": label}
                for value, label in AcademicEvent.EVENT_TYPES
            ],
        }
    )


def admin_user_data(user):
    role = user_role_data(user)
    profile = getattr(user, "student_profile", None)
    return {
        "id": user.pk,
        "name": user.get_full_name() or user.username,
        "email": user.email,
        "role": role["label"],
        "role_value": role["value"],
        "program": getattr(profile, "program", ""),
        "date_joined": user.date_joined.isoformat(),
    }


@login_required
@require_http_methods(["POST"])
def api_admin_event_create(request):
    denied = require_staff(request)
    if denied:
        return denied
    payload = json_body(request)
    if payload is None:
        return JsonResponse({"detail": "Corps JSON invalide."}, status=400)
    form = AcademicEventForm(payload)
    if not form.is_valid():
        return JsonResponse({"errors": form.errors.get_json_data()}, status=400)
    event = form.save()
    return JsonResponse({"event": event_data(event)}, status=201)


@login_required
@require_http_methods(["PUT", "DELETE"])
def api_admin_event_detail(request, pk):
    denied = require_staff(request)
    if denied:
        return denied
    event = get_object_or_404(AcademicEvent, pk=pk)
    if request.method == "DELETE":
        event.delete()
        return JsonResponse({"ok": True})

    payload = json_body(request)
    if payload is None:
        return JsonResponse({"detail": "Corps JSON invalide."}, status=400)
    form = AcademicEventForm(payload, instance=event)
    if not form.is_valid():
        return JsonResponse({"errors": form.errors.get_json_data()}, status=400)
    event = form.save()
    return JsonResponse({"event": event_data(event)})
