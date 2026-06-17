from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="AcademicEvent",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=180, verbose_name="titre")),
                ("description", models.TextField(verbose_name="description")),
                (
                    "event_type",
                    models.CharField(
                        choices=[
                            ("inscription", "Inscription"),
                            ("exam", "Examen"),
                            ("defense", "Soutenance"),
                            ("payment", "Paiement"),
                            ("file_submission", "Depot de dossier"),
                            ("meeting", "Reunion"),
                            ("other", "Autre"),
                        ],
                        max_length=30,
                        verbose_name="type d'evenement",
                    ),
                ),
                ("start_date", models.DateField(verbose_name="date de debut")),
                ("end_date", models.DateField(verbose_name="date de fin")),
                ("location", models.CharField(blank=True, max_length=160, verbose_name="lieu")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "evenement academique",
                "verbose_name_plural": "evenements academiques",
                "ordering": ["start_date", "title"],
            },
        ),
    ]
