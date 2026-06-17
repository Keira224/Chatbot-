from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="StudentProfile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("student_number", models.CharField(blank=True, max_length=30, verbose_name="matricule")),
                ("program", models.CharField(blank=True, max_length=120, verbose_name="programme")),
                ("level", models.CharField(blank=True, max_length=80, verbose_name="niveau")),
                ("phone", models.CharField(blank=True, max_length=30, verbose_name="telephone")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="student_profile",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "profil etudiant",
                "verbose_name_plural": "profils etudiants",
            },
        ),
    ]
