from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.urls import reverse
from django.views.decorators.http import require_POST

from .models import Notification


def react_redirect(request, view):
    if request.user.is_staff:
        return redirect("accounts:admin_portal")
    return redirect(f"{reverse('accounts:academic_portal')}?view={view}")


@login_required
def preferences(request):
    return react_redirect(request, "preferences")


@login_required
def notifications(request):
    return react_redirect(request, "notifications")


@login_required
@require_POST
def mark_as_read(request, pk):
    Notification.objects.filter(pk=pk, user=request.user).update(is_read=True)
    return react_redirect(request, "notifications")


@login_required
@require_POST
def mark_all_as_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return react_redirect(request, "notifications")
