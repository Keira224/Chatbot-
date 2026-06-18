from pathlib import Path

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import redirect
from django.views.decorators.csrf import ensure_csrf_cookie

REACT_INDEX = Path(settings.BASE_DIR) / "static" / "react" / "index.html"


@ensure_csrf_cookie
def react_app(request):
    if not REACT_INDEX.exists():
        return HttpResponse(
            "Le frontend React n'est pas construit. Executez `cd frontend && npm run build`.",
            status=503,
            content_type="text/plain; charset=utf-8",
        )
    return HttpResponse(REACT_INDEX.read_text(encoding="utf-8"))


def dashboard(request):
    return react_app(request)


def profile(request):
    return react_app(request)


def home_redirect(request):
    return react_app(request)


def academic_portal(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect("accounts:admin_portal")
    return react_app(request)


def student_portal(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect("accounts:admin_portal")
    return redirect("accounts:academic_portal")


def admin_portal(request):
    if request.user.is_authenticated and not request.user.is_staff:
        return redirect("accounts:academic_portal")
    return react_app(request)


def admin_supervision(request):
    return redirect("accounts:admin_portal")
