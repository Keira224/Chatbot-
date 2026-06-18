from django.conf import settings
from django.db import models


class ChatMessage(models.Model):
    GEMINI = "gemini"
    CALENDAR = "calendar"
    KNOWLEDGE = "knowledge"
    LOCAL = "local"
    SOURCE_CHOICES = [
        (GEMINI, "Gemini"),
        (CALENDAR, "Calendrier"),
        (KNOWLEDGE, "Base de connaissances"),
        (LOCAL, "Reponse locale"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="chat_messages")
    question = models.TextField()
    answer = models.TextField()
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default=LOCAL)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
        verbose_name = "message chatbot"
        verbose_name_plural = "messages chatbot"

    def __str__(self):
        return f"{self.user.username} - {self.question[:40]}"


class ChatbotKnowledge(models.Model):
    GENERAL = "general"
    REGISTRATION = "registration"
    EXAM = "exam"
    PAYMENT = "payment"
    DOCUMENT = "document"
    DEFENSE = "defense"
    TEACHING = "teaching"
    SUPPORT = "support"

    CATEGORY_CHOICES = [
        (GENERAL, "General"),
        (REGISTRATION, "Inscription"),
        (EXAM, "Examens"),
        (PAYMENT, "Paiement"),
        (DOCUMENT, "Documents"),
        (DEFENSE, "Soutenance"),
        (TEACHING, "Enseignement"),
        (SUPPORT, "Assistance"),
    ]

    title = models.CharField("scenario", max_length=180, unique=True)
    sample_question = models.CharField("question exemple", max_length=255)
    answer = models.TextField("reponse de reference")
    keywords = models.CharField("mots-cles", max_length=500)
    category = models.CharField("categorie", max_length=30, choices=CATEGORY_CHOICES, default=GENERAL)
    audience = models.CharField("public concerne", max_length=120, blank=True)
    priority = models.PositiveSmallIntegerField("priorite", default=10)
    is_active = models.BooleanField("actif", default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-priority", "category", "title"]
        verbose_name = "connaissance chatbot"
        verbose_name_plural = "connaissances chatbot"

    def __str__(self):
        return self.title

    def keyword_list(self):
        return [item.strip() for item in self.keywords.split(",") if item.strip()]
