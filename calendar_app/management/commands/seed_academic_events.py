from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from calendar_app.models import AcademicEvent


class Command(BaseCommand):
    help = "Ajoute des evenements academiques de demonstration."

    def handle(self, *args, **options):
        today = timezone.localdate()
        samples = [
            ("Ouverture des inscriptions pedagogiques", "Inscription en ligne pour le semestre.", AcademicEvent.INSCRIPTION, 3, 10, "Scolarite"),
            ("Paiement des frais universitaires", "Dernier delai de paiement des frais.", AcademicEvent.PAYMENT, 7, 7, "Comptabilite"),
            ("Depot des dossiers de soutenance", "Depot des memoires et fiches de validation.", AcademicEvent.FILE_SUBMISSION, 14, 18, "Departement"),
            ("Examens du premier semestre", "Session normale des examens.", AcademicEvent.EXAM, 24, 30, "Campus principal"),
            ("Reunion d'information des etudiants", "Presentation des consignes academiques et administratives.", AcademicEvent.MEETING, 32, 32, "Amphi A"),
            ("Soutenances de fin de cycle", "Passage devant le jury.", AcademicEvent.DEFENSE, 38, 42, "Salle de conference"),
        ]

        created_count = 0
        for title, description, event_type, start_offset, end_offset, location in samples:
            _, created = AcademicEvent.objects.update_or_create(
                title=title,
                defaults={
                    "description": description,
                    "event_type": event_type,
                    "start_date": today + timedelta(days=start_offset),
                    "end_date": today + timedelta(days=end_offset),
                    "location": location,
                },
            )
            created_count += int(created)

        self.stdout.write(self.style.SUCCESS(f"Donnees de test pretes. Nouveaux evenements: {created_count}"))
