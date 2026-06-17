from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("calendar_app", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="academicevent",
            name="event_type",
            field=models.CharField(
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
    ]
