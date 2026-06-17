from django.conf import settings
from django.db import models


class StudentProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="student_profile")
    student_number = models.CharField("matricule", max_length=30, blank=True)
    program = models.CharField("programme", max_length=120, blank=True)
    level = models.CharField("niveau", max_length=80, blank=True)
    phone = models.CharField("telephone", max_length=30, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "profil etudiant"
        verbose_name_plural = "profils etudiants"

    def __str__(self):
        full_name = self.user.get_full_name()
        return full_name or self.user.username
