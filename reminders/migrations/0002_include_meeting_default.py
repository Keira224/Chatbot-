from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("reminders", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="reminderpreference",
            name="event_types",
            field=models.CharField(
                default="inscription,exam,defense,payment,file_submission,meeting",
                max_length=255,
                verbose_name="types suivis",
            ),
        ),
    ]
