from django.conf import settings
from django.db import models

from calendar_app.models import AcademicEvent


class ReminderPreference(models.Model):
    REMINDER_DAY_CHOICES = [
        (7, "7 jours avant"),
        (3, "3 jours avant"),
        (1, "1 jour avant"),
        (0, "Le jour meme"),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reminder_preference")
    event_types = models.CharField("types suivis", max_length=255, default="inscription,exam,defense,payment,file_submission,meeting")
    reminder_days = models.PositiveSmallIntegerField("delai du rappel", choices=REMINDER_DAY_CHOICES, default=7)
    email_enabled = models.BooleanField("recevoir les rappels par email", default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "preference de rappel"
        verbose_name_plural = "preferences de rappel"

    def __str__(self):
        return f"Preferences de {self.user.username}"

    def selected_event_types(self):
        return [item for item in self.event_types.split(",") if item]

    def set_event_types(self, values):
        self.event_types = ",".join(values)


class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    event = models.ForeignKey(AcademicEvent, on_delete=models.CASCADE, related_name="notifications")
    message = models.CharField(max_length=255)
    due_date = models.DateField("date de rappel")
    is_read = models.BooleanField("lue", default=False)
    email_sent_at = models.DateTimeField("email envoye le", null=True, blank=True)
    email_error = models.TextField("erreur email", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("user", "event", "due_date")
        verbose_name = "notification"
        verbose_name_plural = "notifications"

    def __str__(self):
        status = "lue" if self.is_read else "non lue"
        return f"{self.user.username} - {self.event.title} ({status})"
