from django.conf import settings
from django.db import models


class StudentProfile(models.Model):
    STUDENT = "student"
    TEACHER = "teacher"
    ROLE_CHOICES = [
        (STUDENT, "Etudiant"),
        (TEACHER, "Enseignant"),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="student_profile")
    role = models.CharField("role", max_length=20, choices=ROLE_CHOICES, default=STUDENT)
    student_number = models.CharField("matricule ou identifiant", max_length=30, blank=True)
    program = models.CharField("filiere ou departement", max_length=120, blank=True)
    level = models.CharField("niveau ou fonction", max_length=80, blank=True)
    phone = models.CharField("telephone", max_length=30, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "profil academique"
        verbose_name_plural = "profils academiques"

    def __str__(self):
        full_name = self.user.get_full_name()
        return full_name or self.user.username

    @property
    def role_label(self):
        return self.get_role_display()
