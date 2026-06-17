from django.db import models
from django.urls import reverse
from django.utils import timezone


class AcademicEventQuerySet(models.QuerySet):
    def upcoming(self):
        return self.filter(end_date__gte=timezone.localdate()).order_by("start_date", "title")


class AcademicEvent(models.Model):
    INSCRIPTION = "inscription"
    EXAM = "exam"
    DEFENSE = "defense"
    PAYMENT = "payment"
    FILE_SUBMISSION = "file_submission"
    MEETING = "meeting"
    OTHER = "other"

    EVENT_TYPES = [
        (INSCRIPTION, "Inscription"),
        (EXAM, "Examen"),
        (DEFENSE, "Soutenance"),
        (PAYMENT, "Paiement"),
        (FILE_SUBMISSION, "Depot de dossier"),
        (MEETING, "Reunion"),
        (OTHER, "Autre"),
    ]

    title = models.CharField("titre", max_length=180)
    description = models.TextField("description")
    event_type = models.CharField("type d'evenement", max_length=30, choices=EVENT_TYPES)
    start_date = models.DateField("date de debut")
    end_date = models.DateField("date de fin")
    location = models.CharField("lieu", max_length=160, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = AcademicEventQuerySet.as_manager()

    class Meta:
        ordering = ["start_date", "title"]
        verbose_name = "evenement academique"
        verbose_name_plural = "evenements academiques"

    def __str__(self):
        return f"{self.title} ({self.get_event_type_display()})"

    def get_absolute_url(self):
        return reverse("calendar_app:event_detail", kwargs={"pk": self.pk})

    @property
    def days_until(self):
        return (self.start_date - timezone.localdate()).days

    @property
    def status_label(self):
        if self.days_until < 0 and self.end_date < timezone.localdate():
            return "Termine"
        if self.start_date <= timezone.localdate() <= self.end_date:
            return "En cours"
        if self.days_until == 0:
            return "Aujourd'hui"
        if self.days_until == 1:
            return "Demain"
        if self.days_until <= 7:
            return f"Dans {self.days_until} jours"
        return "A venir"

    @property
    def urgency_class(self):
        if self.start_date <= timezone.localdate() <= self.end_date:
            return "success"
        if 0 <= self.days_until <= 3:
            return "danger"
        if 4 <= self.days_until <= 7:
            return "warning"
        return "primary"
