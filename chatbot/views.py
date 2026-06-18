from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.urls import reverse


@login_required
def chat(request):
    if request.user.is_staff:
        return redirect("accounts:admin_portal")
    return redirect(f"{reverse('accounts:academic_portal')}?view=assistant")
