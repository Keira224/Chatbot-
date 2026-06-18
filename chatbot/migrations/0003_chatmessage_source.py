from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("chatbot", "0002_chatbotknowledge"),
    ]

    operations = [
        migrations.AddField(
            model_name="chatmessage",
            name="source",
            field=models.CharField(
                choices=[
                    ("gemini", "Gemini"),
                    ("calendar", "Calendrier"),
                    ("knowledge", "Base de connaissances"),
                    ("local", "Reponse locale"),
                ],
                default="local",
                max_length=20,
            ),
        ),
    ]
