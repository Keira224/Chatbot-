from django.contrib import admin

from .models import StudentProfile


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "student_number", "program", "level", "phone")
    search_fields = ("user__username", "user__first_name", "user__last_name", "student_number", "program")
    list_filter = ("program", "level")
