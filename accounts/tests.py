import json
from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from calendar_app.models import AcademicEvent
from .models import StudentProfile


class PortalAccessTests(TestCase):
    def setUp(self):
        self.student = User.objects.create_user(username="student", password="test-password")
        StudentProfile.objects.create(user=self.student, role=StudentProfile.STUDENT)
        self.teacher = User.objects.create_user(username="teacher", password="test-password")
        StudentProfile.objects.create(
            user=self.teacher,
            role=StudentProfile.TEACHER,
            program="Departement Informatique",
        )
        self.admin = User.objects.create_user(username="admin", password="test-password", is_staff=True)

    def test_student_is_redirected_away_from_admin_portal(self):
        self.client.force_login(self.student)

        response = self.client.get(reverse("accounts:admin_portal"))

        self.assertRedirects(response, reverse("accounts:academic_portal"))

    def test_admin_is_redirected_away_from_student_portal(self):
        self.client.force_login(self.admin)

        response = self.client.get(reverse("accounts:student_portal"))

        self.assertRedirects(response, reverse("accounts:admin_portal"))

    def test_student_cannot_create_event_through_admin_api(self):
        self.client.force_login(self.student)

        response = self.client.post(
            reverse("accounts:api_admin_event_create"),
            data=json.dumps(self.event_payload()),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(AcademicEvent.objects.count(), 0)

    def test_admin_can_create_event_through_api(self):
        self.client.force_login(self.admin)

        response = self.client.post(
            reverse("accounts:api_admin_event_create"),
            data=json.dumps(self.event_payload()),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(AcademicEvent.objects.count(), 1)
        self.assertEqual(AcademicEvent.objects.get().title, "Examen final")

    def test_student_dashboard_returns_upcoming_events(self):
        AcademicEvent.objects.create(**self.event_payload())
        self.client.force_login(self.student)

        response = self.client.get(reverse("accounts:api_student_dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["summary"]["upcoming_events"], 1)
        self.assertEqual(response.json()["events"][0]["title"], "Examen final")
        self.assertEqual(response.json()["upcoming_events"][0]["title"], "Examen final")

    def test_teacher_uses_the_academic_portal(self):
        self.client.force_login(self.teacher)

        response = self.client.get(reverse("accounts:academic_portal"))
        session_response = self.client.get(reverse("accounts:api_session"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(session_response.json()["user"]["role"], StudentProfile.TEACHER)
        self.assertEqual(session_response.json()["user"]["role_label"], "Enseignant")

    def test_registration_records_teacher_role(self):
        response = self.client.post(
            reverse("accounts:api_register"),
            data=json.dumps({
                "role": StudentProfile.TEACHER,
                "username": "new_teacher",
                "first_name": "Mariama",
                "last_name": "Camara",
                "email": "mariama@example.com",
                "student_number": "ENS-42",
                "program": "Departement de Mathematiques",
                "level": "Maitre-assistante",
                "phone": "620000000",
                "password1": "A-secure-password-2026",
                "password2": "A-secure-password-2026",
            }),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["user"]["role"], StudentProfile.TEACHER)
        profile = User.objects.get(username="new_teacher").student_profile
        self.assertEqual(profile.role, StudentProfile.TEACHER)

    def test_anonymous_session_is_returned_as_json(self):
        response = self.client.get(reverse("accounts:api_session"))

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()["authenticated"])

    def test_admin_dashboard_counts_students_and_teachers(self):
        self.client.force_login(self.admin)

        response = self.client.get(reverse("accounts:api_admin_dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["summary"]["students"], 1)
        self.assertEqual(response.json()["summary"]["teachers"], 1)
        roles = {item["role"] for item in response.json()["users"]}
        self.assertIn("Etudiant", roles)
        self.assertIn("Enseignant", roles)

    @staticmethod
    def event_payload():
        start_date = timezone.localdate() + timedelta(days=5)
        return {
            "title": "Examen final",
            "description": "Evaluation de fin de semestre.",
            "event_type": AcademicEvent.EXAM,
            "start_date": start_date.isoformat(),
            "end_date": start_date.isoformat(),
            "location": "Amphi A",
        }
