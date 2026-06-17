from django.contrib import admin

from .models import Notification, ReminderPreference


@admin.register(ReminderPreference)
class ReminderPreferenceAdmin(admin.ModelAdmin):
    list_display = ("user", "event_types", "reminder_days", "email_enabled", "updated_at")
    search_fields = ("user__username", "user__first_name", "user__last_name")
    list_filter = ("reminder_days", "email_enabled")


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "event", "due_date", "is_read", "email_sent_at", "created_at")
    list_filter = ("is_read", "email_sent_at", "due_date", "event__event_type")
    search_fields = ("user__username", "event__title", "message")
