from datetime import timedelta

from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.text import slugify

from .models import AcademicEvent


def academic_redirect(request, view):
    if not request.user.is_authenticated:
        return redirect("accounts:login")
    if request.user.is_staff:
        return redirect("accounts:admin_portal")
    return redirect(f"{reverse('accounts:academic_portal')}?view={view}")


def admin_events_redirect(request):
    if not request.user.is_authenticated:
        return redirect("accounts:login")
    if not request.user.is_staff:
        return redirect("accounts:academic_portal")
    return redirect(f"{reverse('accounts:admin_portal')}?view=events")


def event_list(request):
    return academic_redirect(request, "calendar")


def event_detail(request, pk):
    return academic_redirect(request, "calendar")


def monthly_calendar(request):
    return academic_redirect(request, "monthly")


def event_manage(request):
    return admin_events_redirect(request)


def event_create(request):
    return admin_events_redirect(request)


def event_update(request, pk):
    return admin_events_redirect(request)


def event_delete(request, pk):
    return admin_events_redirect(request)


def event_ics(request, pk):
    event = get_object_or_404(AcademicEvent, pk=pk)
    response = HttpResponse(build_ics([event]), content_type="text/calendar")
    response["Content-Disposition"] = f'attachment; filename="{slugify(event.title)}.ics"'
    return response


def upcoming_events_ics(request):
    events = AcademicEvent.objects.upcoming()
    response = HttpResponse(build_ics(events), content_type="text/calendar")
    response["Content-Disposition"] = 'attachment; filename="acadreminder-calendrier.ics"'
    return response


def build_ics(events):
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//AcadReminder//Calendrier Academique//FR"]
    for event in events:
        lines.extend(
            [
                "BEGIN:VEVENT",
                f"UID:acadreminder-event-{event.pk}@local",
                f"SUMMARY:{escape_ics(event.title)}",
                f"DESCRIPTION:{escape_ics(event.description)}",
                f"LOCATION:{escape_ics(event.location)}",
                f"DTSTART;VALUE=DATE:{event.start_date:%Y%m%d}",
                f"DTEND;VALUE=DATE:{event.end_date + timedelta(days=1):%Y%m%d}",
                "END:VEVENT",
            ]
        )
    lines.append("END:VCALENDAR")
    return "\r\n".join(lines)


def escape_ics(value):
    return str(value or "").replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")
