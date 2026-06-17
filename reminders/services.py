from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone

from calendar_app.models import AcademicEvent

from .models import Notification, ReminderPreference


def get_or_create_preference(user):
    preference, _ = ReminderPreference.objects.get_or_create(user=user)
    return preference


def generate_notifications_for_user(user):
    """Create in-app reminders for events matching the student's preferences."""
    preference = get_or_create_preference(user)
    today = timezone.localdate()
    limit_date = today + timedelta(days=preference.reminder_days)

    events = AcademicEvent.objects.filter(
        event_type__in=preference.selected_event_types(),
        start_date__gte=today,
        start_date__lte=limit_date,
    )

    created_count = 0
    emailed_count = 0
    for event in events:
        days_left = (event.start_date - today).days
        if days_left == 0:
            delay_text = "aujourd'hui"
        elif days_left == 1:
            delay_text = "demain"
        else:
            delay_text = f"dans {days_left} jours"

        notification, created = Notification.objects.get_or_create(
            user=user,
            event=event,
            due_date=today,
            defaults={"message": f"{event.title} commence {delay_text}."},
        )
        if created:
            created_count += 1
        if preference.email_enabled and send_notification_email(notification):
            emailed_count += 1

    return {"created": created_count, "emails_sent": emailed_count}


def generate_notifications_for_all_users():
    """Create reminders for every active non-staff user. Designed for scheduled execution."""
    totals = {"users": 0, "created": 0, "emails_sent": 0}
    users = get_user_model().objects.filter(is_active=True, is_staff=False)
    for user in users:
        result = generate_notifications_for_user(user)
        totals["users"] += 1
        totals["created"] += result["created"]
        totals["emails_sent"] += result["emails_sent"]
    return totals


def send_notification_email(notification):
    if notification.email_sent_at or not notification.user.email:
        return False

    event = notification.event
    subject = f"Rappel academique : {event.title}"
    body = "\n".join(
        [
            f"Bonjour {notification.user.get_full_name() or notification.user.username},",
            "",
            notification.message,
            "",
            f"Type : {event.get_event_type_display()}",
            f"Debut : {event.start_date:%d/%m/%Y}",
            f"Fin : {event.end_date:%d/%m/%Y}",
            f"Lieu : {event.location or 'Non precise'}",
            "",
            "Connectez-vous a AcadReminder pour consulter le detail.",
        ]
    )

    try:
        send_mail(
            subject,
            body,
            getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@acadreminder.local"),
            [notification.user.email],
            fail_silently=False,
        )
    except Exception as exc:
        notification.email_error = str(exc)
        notification.save(update_fields=["email_error"])
        return False

    notification.email_sent_at = timezone.now()
    notification.email_error = ""
    notification.save(update_fields=["email_sent_at", "email_error"])
    return True
