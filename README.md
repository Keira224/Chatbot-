# AcadReminder

AcadReminder est une application web Django de rappel des dates importantes academiques. Elle permet aux etudiants de consulter un calendrier academique, de recevoir des rappels visibles dans l'application et d'interroger un chatbot simple base sur les evenements enregistres.

## Fonctionnalites

### Acteur etudiant

- Authentification etudiante : inscription, connexion, deconnexion, profil.
- Calendrier academique : liste, detail, recherche et filtre par type.
- Types d'evenements : inscription, examen, soutenance, paiement, depot de dossier, reunion, autre.
- Chatbot academique : reponses basees sur des mots-cles et les donnees de la base.
- Rappels : preferences par type d'evenement et delai de notification.
- Notifications internes affichees dans le tableau de bord.
- Tableau de bord actif : statistiques, urgences de la semaine et prochaine echeance.
- Export `.ics` pour ajouter les evenements dans Google Calendar, Outlook ou Apple Calendar.
- Questions rapides dans le chatbot pour faciliter la demonstration.
- Action pour marquer toutes les notifications comme lues.

### Acteur administrateur

- Ajout, modification et suppression des evenements via Django Admin.
- Gestion des utilisateurs via Django Admin.
- Page de supervision avec statistiques systeme.
- Administration Django configuree pour les evenements, profils, rappels et discussions.

## Technologies utilisees

- Python
- Django
- SQLite en developpement
- Django Templates
- Bootstrap 5

## Installation

Depuis le dossier du projet :

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_academic_events
python manage.py createsuperuser
python manage.py runserver
```

Sur macOS ou Linux :

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_academic_events
python manage.py createsuperuser
python manage.py runserver
```

L'application sera disponible sur `http://127.0.0.1:8000/`.

## Commandes utiles

```bash
python manage.py runserver
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_academic_events
python manage.py check
```

## Intelligence artificielle Gemini

Le chatbot utilise Gemini si la variable d'environnement `GEMINI_API_KEY` est definie. Si la cle est absente ou si l'appel echoue, l'application revient automatiquement au chatbot local base sur les evenements du calendrier.

PowerShell :

```powershell
$env:GEMINI_API_KEY="votre-cle-api-gemini"
$env:GEMINI_MODEL="gemini-3.5-flash"
python manage.py runserver
```

macOS ou Linux :

```bash
export GEMINI_API_KEY="votre-cle-api-gemini"
export GEMINI_MODEL="gemini-3.5-flash"
python manage.py runserver
```

Ne placez jamais la vraie cle dans `settings.py`, un template, JavaScript ou un commit Git. Creez une cle depuis Google AI Studio et utilisez de preference une nouvelle cle d'autorisation restreinte a Gemini API.

### Exposition temporaire avec ngrok

Demarrez d'abord Django avec une configuration publique :

```powershell
$env:DJANGO_SECRET_KEY="une-longue-valeur-aleatoire"
$env:DJANGO_DEBUG="False"
$env:GEMINI_API_KEY="votre-cle-api-gemini"
$env:GEMINI_MODEL="gemini-3.5-flash"
$env:ALLOWED_HOSTS="127.0.0.1,localhost,votre-domaine.ngrok-free.app"
$env:CSRF_TRUSTED_ORIGINS="https://votre-domaine.ngrok-free.app"
python manage.py runserver --insecure
```

Dans un second terminal :

```powershell
ngrok http 8000
```

Si ngrok attribue un nouveau domaine, mettez a jour `ALLOWED_HOSTS` et `CSRF_TRUSTED_ORIGINS`, puis relancez Django. Ngrok convient a une demonstration temporaire, pas a un hebergement permanent.

L'option `--insecure` sert uniquement a charger les fichiers CSS pendant cette demonstration locale avec `DEBUG=False`. Pour un vrai deploiement, utilisez un serveur web ou un service d'hebergement pour les fichiers statiques.

## Structure du projet

```text
acadreminder/
├── manage.py
├── requirements.txt
├── README.md
├── .gitignore
├── config/
├── accounts/
├── calendar_app/
├── chatbot/
├── reminders/
├── templates/
├── static/
└── docs/
```

## Evolution prevue

- Passage de SQLite a MySQL via la configuration `DATABASES`.
- Envoi de rappels par email.
- Taches planifiees avec Celery ou Django-Q.
- Chatbot plus avance avec NLP ou API IA.
