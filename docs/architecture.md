# Architecture - AcadReminder

## Vue generale

Le projet suit une architecture Django classique avec separation par domaine fonctionnel.

## Applications

- `accounts` : inscription, connexion, tableau de bord et profil etudiant.
- `calendar_app` : modele et vues des evenements academiques.
- `chatbot` : discussion et service de reponse par mots-cles.
- `reminders` : preferences de rappel et notifications internes.

## Acteurs

- Etudiant : cree un compte, consulte le calendrier, dialogue avec le chatbot, recoit les notifications et personnalise ses rappels.
- Administrateur : ajoute, modifie et supprime les evenements, gere les utilisateurs et supervise le systeme depuis la page de supervision et Django Admin.

## Fonctionnalites transversales

- Les exports `.ics` sont generes depuis `calendar_app.views` sans dependance externe.
- Les notifications sont creees par `reminders.services.generate_notifications_for_user`.
- Le tableau de bord combine les donnees du calendrier et des rappels pour donner une vue active a l'etudiant.

## Donnees principales

- `AcademicEvent` : evenement academique avec type, dates, lieu et description.
- `StudentProfile` : informations complementaires de l'utilisateur Django.
- `ReminderPreference` : types suivis et delai de rappel.
- `Notification` : rappel visible dans l'application.
- `ChatMessage` : historique des questions et reponses.

## Evolutivite

SQLite est utilise en developpement. Pour MySQL, il suffira d'adapter `DATABASES` dans `config/settings.py` et d'installer le connecteur approprie.
