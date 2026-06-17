from django.core.management.base import BaseCommand

from reminders.services import generate_notifications_for_all_users


class Command(BaseCommand):
    help = "Generate automatic in-app and email reminders for all active students."

    def handle(self, *args, **options):
        totals = generate_notifications_for_all_users()
        self.stdout.write(
            self.style.SUCCESS(
                "Rappels generes: "
                f"{totals['created']} notification(s), "
                f"{totals['emails_sent']} email(s), "
                f"{totals['users']} etudiant(s) traite(s)."
            )
        )
