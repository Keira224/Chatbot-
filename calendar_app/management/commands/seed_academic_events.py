from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from calendar_app.models import AcademicEvent


class Command(BaseCommand):
    help = "Ajoute des evenements academiques de demonstration."

    def handle(self, *args, **options):
        today = timezone.localdate()
        samples = [
            (
                "Cloture des inscriptions administratives",
                "Dernier delai pour finaliser le dossier administratif et fournir les pieces manquantes.",
                AcademicEvent.INSCRIPTION,
                -28,
                -24,
                "Service de la scolarite",
            ),
            (
                "Session de rattrapage du semestre precedent",
                "Epreuves de rattrapage pour les unites d'enseignement non validees.",
                AcademicEvent.EXAM,
                -20,
                -16,
                "Campus principal",
            ),
            (
                "Depot des rapports de stage",
                "Remise du rapport final signe par le maitre de stage et le responsable pedagogique.",
                AcademicEvent.FILE_SUBMISSION,
                -13,
                -10,
                "Secretariat du departement",
            ),
            (
                "Reunion du conseil pedagogique",
                "Bilan du semestre et validation des propositions d'amelioration des enseignements.",
                AcademicEvent.MEETING,
                -7,
                -7,
                "Salle du conseil",
            ),
            (
                "Ouverture des inscriptions pedagogiques",
                "Selection en ligne des unites d'enseignement et validation du parcours du semestre.",
                AcademicEvent.INSCRIPTION,
                -2,
                6,
                "Plateforme numerique",
            ),
            (
                "Paiement des frais universitaires",
                "Reglement de la premiere tranche et retrait du recu a conserver dans le dossier.",
                AcademicEvent.PAYMENT,
                1,
                1,
                "Service comptable",
            ),
            (
                "Reunion d'information des etudiants",
                "Presentation de l'etablissement, des services et des responsables de filiere.",
                AcademicEvent.MEETING,
                2,
                2,
                "Amphitheatre central",
            ),
            (
                "Test de positionnement en anglais",
                "Evaluation obligatoire pour constituer les groupes de niveau du semestre.",
                AcademicEvent.EXAM,
                3,
                3,
                "Laboratoire de langues",
            ),
            (
                "Depot des demandes de bourse",
                "Transmission du formulaire, des justificatifs de revenus et du certificat d'inscription.",
                AcademicEvent.FILE_SUBMISSION,
                5,
                9,
                "Bureau des affaires sociales",
            ),
            (
                "Reunion d'information sur les stages",
                "Presentation des conventions, du suivi pedagogique et des criteres d'evaluation.",
                AcademicEvent.MEETING,
                7,
                7,
                "Amphi B",
            ),
            (
                "Examen de programmation web",
                "Evaluation pratique portant sur Django, les API web et les interfaces utilisateur.",
                AcademicEvent.EXAM,
                10,
                10,
                "Laboratoire informatique 2",
            ),
            (
                "Depot des sujets de memoire",
                "Les etudiants de fin de cycle soumettent leur sujet et une fiche de cadrage validee.",
                AcademicEvent.FILE_SUBMISSION,
                12,
                15,
                "Direction des etudes",
            ),
            (
                "Paiement de la deuxieme tranche des frais",
                "Dernier delai de paiement avant suspension temporaire de l'acces aux services.",
                AcademicEvent.PAYMENT,
                16,
                16,
                "Service comptable",
            ),
            (
                "Examens du premier semestre",
                "Session normale des examens ecrits et pratiques du premier semestre.",
                AcademicEvent.EXAM,
                20,
                26,
                "Campus principal",
            ),
            (
                "Inscription aux ateliers de recherche",
                "Choix d'un atelier methodologique selon le domaine de recherche ou de specialisation.",
                AcademicEvent.INSCRIPTION,
                23,
                29,
                "Espace numerique",
            ),
            (
                "Reunion des enseignants",
                "Coordination des evaluations, harmonisation des baremes et calendrier des corrections.",
                AcademicEvent.MEETING,
                28,
                28,
                "Salle des professeurs",
            ),
            (
                "Depot des dossiers de soutenance",
                "Depot du memoire, de la fiche de validation et des exemplaires demandes par le jury.",
                AcademicEvent.FILE_SUBMISSION,
                32,
                36,
                "Secretariat des soutenances",
            ),
            (
                "Soutenances de fin de cycle",
                "Presentation des projets de fin de cycle devant les jurys du departement informatique.",
                AcademicEvent.DEFENSE,
                38,
                40,
                "Salle de conference A",
            ),
            (
                "Soutenance de master gestion",
                "Presentation des memoires de master et deliberation des jurys.",
                AcademicEvent.DEFENSE,
                42,
                44,
                "Salle de conference B",
            ),
            (
                "Publication des resultats du semestre",
                "Mise a disposition des resultats et ouverture de la periode de reclamation.",
                AcademicEvent.OTHER,
                47,
                47,
                "Plateforme numerique",
            ),
            (
                "Depot des reclamations de notes",
                "Les reclamations doivent indiquer la matiere, le groupe et le motif de la demande.",
                AcademicEvent.FILE_SUBMISSION,
                48,
                52,
                "Service des examens",
            ),
            (
                "Inscription a la session de rattrapage",
                "Inscription obligatoire pour les etudiants autorises a reprendre une evaluation.",
                AcademicEvent.INSCRIPTION,
                55,
                59,
                "Scolarite en ligne",
            ),
            (
                "Session de rattrapage",
                "Epreuves de rattrapage selon le planning publie par le service des examens.",
                AcademicEvent.EXAM,
                63,
                68,
                "Campus principal",
            ),
            (
                "Ceremonie de remise des diplomes",
                "Ceremonie officielle pour les diplomes de licence et de master.",
                AcademicEvent.OTHER,
                78,
                78,
                "Grande salle polyvalente",
            ),
        ]

        created_count = 0
        updated_count = 0
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
            updated_count += int(not created)

        self.stdout.write(
            self.style.SUCCESS(
                f"Donnees de test pretes. Nouveaux evenements: {created_count}. "
                f"Evenements actualises: {updated_count}. Total attendu: {len(samples)}."
            )
        )
