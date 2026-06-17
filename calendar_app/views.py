import calendar
from datetime import date, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.text import slugify
from django.utils import timezone

from .forms import AcademicEventForm, EventSearchForm
from .models import AcademicEvent


def event_list(request):
    form = EventSearchForm(request.GET or None)
    events = AcademicEvent.objects.all()

    if form.is_valid():
        query = form.cleaned_data.get("q")
        event_type = form.cleaned_data.get("event_type")
        if query:
            events = events.filter(Q(title__icontains=query) | Q(description__icontains=query) | Q(location__icontains=query))
        if event_type:
            events = events.filter(event_type=event_type)

    labels = dict(AcademicEvent.EVENT_TYPES)
    type_stats = [
        {"label": labels.get(item["event_type"], item["event_type"]), "total": item["total"]}
        for item in AcademicEvent.objects.values("event_type").annotate(total=Count("id"))
    ]
    return render(request, "calendar_app/event_list.html", {"form": form, "events": events, "type_stats": type_stats})


def event_detail(request, pk):
    event = get_object_or_404(AcademicEvent, pk=pk)
    return render(request, "calendar_app/event_detail.html", {"event": event})


def is_staff_user(user):
    return user.is_authenticated and user.is_staff


@login_required
@user_passes_test(is_staff_user)
def event_manage(request):
    form = EventSearchForm(request.GET or None)
    events = AcademicEvent.objects.all()
    if form.is_valid():
        query = form.cleaned_data.get("q")
        event_type = form.cleaned_data.get("event_type")
        if query:
            events = events.filter(Q(title__icontains=query) | Q(description__icontains=query) | Q(location__icontains=query))
        if event_type:
            events = events.filter(event_type=event_type)

    context = {
        "form": form,
        "events": events,
        "total_events": AcademicEvent.objects.count(),
        "upcoming_events": AcademicEvent.objects.upcoming().count(),
        "past_events": AcademicEvent.objects.filter(end_date__lt=timezone.localdate()).count(),
    }
    return render(request, "calendar_app/event_manage.html", context)


@login_required
@user_passes_test(is_staff_user)
def event_create(request):
    if request.method == "POST":
        form = AcademicEventForm(request.POST)
        if form.is_valid():
            event = form.save()
            messages.success(request, "Evenement ajoute avec succes.")
            return redirect("calendar_app:event_detail", pk=event.pk)
    else:
        form = AcademicEventForm()
    return render(request, "calendar_app/event_form.html", {"form": form, "mode": "create"})


@login_required
@user_passes_test(is_staff_user)
def event_update(request, pk):
    event = get_object_or_404(AcademicEvent, pk=pk)
    if request.method == "POST":
        form = AcademicEventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, "Evenement mis a jour.")
            return redirect("calendar_app:event_detail", pk=event.pk)
    else:
        form = AcademicEventForm(instance=event)
    return render(request, "calendar_app/event_form.html", {"form": form, "event": event, "mode": "update"})


@login_required
@user_passes_test(is_staff_user)
def event_delete(request, pk):
    event = get_object_or_404(AcademicEvent, pk=pk)
    if request.method == "POST":
        event.delete()
        messages.success(request, "Evenement supprime.")
        return redirect("calendar_app:event_manage")
    return render(request, "calendar_app/event_confirm_delete.html", {"event": event})


def monthly_calendar(request):
    today = timezone.localdate()
    year = parse_int(request.GET.get("year"), today.year)
    month = parse_int(request.GET.get("month"), today.month)
    if month < 1 or month > 12:
        year = today.year
        month = today.month
    try:
        current_month = date(year, month, 1)
    except ValueError:
        current_month = date(today.year, today.month, 1)
        year = current_month.year
        month = current_month.month
    previous_month = add_months(current_month, -1)
    next_month = add_months(current_month, 1)
    _, last_day = calendar.monthrange(year, month)
    month_start = current_month
    month_end = date(year, month, last_day)

    events = AcademicEvent.objects.filter(start_date__lte=month_end, end_date__gte=month_start).order_by("start_date", "title")
    events_by_day = {day: [] for day in range(1, last_day + 1)}
    for event in events:
        first_visible_day = max(event.start_date, month_start).day
        last_visible_day = min(event.end_date, month_end).day
        for day in range(first_visible_day, last_visible_day + 1):
            events_by_day[day].append(event)

    month_days = calendar.Calendar(firstweekday=0).monthdatescalendar(year, month)
    weeks = [
        [
            {
                "date": day,
                "in_month": day.month == month,
                "is_today": day == today,
                "events": events_by_day.get(day.day, []) if day.month == month else [],
            }
            for day in week
        ]
        for week in month_days
    ]

    context = {
        "weeks": weeks,
        "current_month": current_month,
        "previous_month": previous_month,
        "next_month": next_month,
        "events_count": events.count(),
        "month_events": events,
        "weekdays": ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"],
    }
    return render(request, "calendar_app/monthly_calendar.html", context)


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


def parse_int(value, default):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def add_months(value, offset):
    month_index = value.month - 1 + offset
    year = value.year + month_index // 12
    month = month_index % 12 + 1
    return date(year, month, 1)
