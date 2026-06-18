from django.contrib import admin

from .models import ChatbotKnowledge, ChatMessage


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ("user", "question", "source", "created_at")
    search_fields = ("user__username", "question", "answer")
    list_filter = ("source", "created_at")


@admin.register(ChatbotKnowledge)
class ChatbotKnowledgeAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "audience", "priority", "is_active", "updated_at")
    search_fields = ("title", "sample_question", "answer", "keywords")
    list_filter = ("category", "audience", "is_active")
    list_editable = ("priority", "is_active")
