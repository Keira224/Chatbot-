from django.contrib import admin

from .models import AcademicEvent


@admin.register(AcademicEvent)
class AcademicEventAdmin(admin.ModelAdmin):
    list_display = ("title", "event_type", "start_date", "end_date", "location")
    list_filter = ("event_type", "start_date")
    search_fields = ("title", "description", "location")
    date_hierarchy = "start_date"
