from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("chatbot", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="ChatbotKnowledge",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=180, unique=True, verbose_name="scenario")),
                ("sample_question", models.CharField(max_length=255, verbose_name="question exemple")),
                ("answer", models.TextField(verbose_name="reponse de reference")),
                ("keywords", models.CharField(max_length=500, verbose_name="mots-cles")),
                (
                    "category",
                    models.CharField(
                        choices=[
                            ("general", "General"),
                            ("registration", "Inscription"),
                            ("exam", "Examens"),
                            ("payment", "Paiement"),
                            ("document", "Documents"),
                            ("defense", "Soutenance"),
                            ("teaching", "Enseignement"),
                            ("support", "Assistance"),
                        ],
                        default="general",
                        max_length=30,
                        verbose_name="categorie",
                    ),
                ),
                ("audience", models.CharField(blank=True, max_length=120, verbose_name="public concerne")),
                ("priority", models.PositiveSmallIntegerField(default=10, verbose_name="priorite")),
                ("is_active", models.BooleanField(default=True, verbose_name="actif")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "connaissance chatbot",
                "verbose_name_plural": "connaissances chatbot",
                "ordering": ["-priority", "category", "title"],
            },
        ),
    ]
