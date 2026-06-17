from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("calendar_app", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="ReminderPreference",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("event_types", models.CharField(default="inscription,exam,defense,payment,file_submission,meeting", max_length=255, verbose_name="types suivis")),
                ("reminder_days", models.PositiveSmallIntegerField(choices=[(7, "7 jours avant"), (3, "3 jours avant"), (1, "1 jour avant"), (0, "Le jour meme")], default=7, verbose_name="delai du rappel")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("user", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="reminder_preference", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "verbose_name": "preference de rappel",
                "verbose_name_plural": "preferences de rappel",
            },
        ),
        migrations.CreateModel(
            name="Notification",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("message", models.CharField(max_length=255)),
                ("due_date", models.DateField(verbose_name="date de rappel")),
                ("is_read", models.BooleanField(default=False, verbose_name="lue")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("event", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="notifications", to="calendar_app.academicevent")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="notifications", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "verbose_name": "notification",
                "verbose_name_plural": "notifications",
                "ordering": ["-created_at"],
                "unique_together": {("user", "event", "due_date")},
            },
        ),
    ]
