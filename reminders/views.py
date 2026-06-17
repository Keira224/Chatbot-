from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.shortcuts import redirect, render

from .forms import ReminderPreferenceForm
from .models import Notification
from .services import generate_notifications_for_user, get_or_create_preference


@login_required
def preferences(request):
    preference = get_or_create_preference(request.user)
    if request.method == "POST":
        form = ReminderPreferenceForm(request.POST, instance=preference)
        if form.is_valid():
            form.save()
            generate_notifications_for_user(request.user)
            messages.success(request, "Preferences de rappel mises a jour.")
            return redirect("reminders:preferences")
    else:
        form = ReminderPreferenceForm(instance=preference)
    return render(request, "reminders/preferences.html", {"form": form})


@login_required
def notifications(request):
    generate_notifications_for_user(request.user)
    items = Notification.objects.select_related("event").filter(user=request.user)
    context = {
        "notifications": items,
        "total_notifications": items.count(),
        "unread_notifications": items.filter(is_read=False).count(),
        "emails_sent": items.exclude(email_sent_at__isnull=True).count(),
    }
    return render(request, "reminders/notifications.html", context)


@login_required
@require_POST
def mark_as_read(request, pk):
    Notification.objects.filter(pk=pk, user=request.user).update(is_read=True)
    return redirect("reminders:notifications")


@login_required
@require_POST
def mark_all_as_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    messages.success(request, "Toutes les notifications ont ete marquees comme lues.")
    return redirect("reminders:notifications")
