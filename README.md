# AcadReminder

AcadReminder est une application React avec une API Django pour le rappel des dates importantes academiques. Elle permet aux etudiants et enseignants de consulter un calendrier academique, de recevoir des rappels visibles dans l'application et d'interroger un chatbot base sur les evenements enregistres.

## Fonctionnalites

### Utilisateurs academiques

- Inscription avec identification du role : etudiant ou enseignant.
- Connexion, deconnexion et profil academique.
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
- React
- Vite
- SQLite en developpement

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

Les espaces React sont accessibles apres connexion :

- Etudiants et enseignants : `http://127.0.0.1:8000/accounts/espace-academique/`
- Administrateur : `http://127.0.0.1:8000/accounts/espace-admin/`

Les comptes etudiant et enseignant utilisent le meme espace academique et ne peuvent pas utiliser les API d'administration. Un compte administrateur est redirige automatiquement vers son espace dedie apres connexion.

Pour reconstruire le frontend apres une modification :

```powershell
cd frontend
npm install
npm run build
```

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

Le projet met aussi les reponses en cache pendant 6 heures. Une question identique est donc servie sans nouvel appel API. La cle de cache contient l'etat du calendrier : si un evenement est ajoute ou modifie, les anciennes reponses ne sont plus reutilisees.

Vous pouvez renseigner les variables directement dans le fichier `.env` a la racine du projet :

```env
GEMINI_API_KEY=votre-cle-api-gemini
GEMINI_MODEL=gemini-2.5-flash
CHATBOT_CACHE_TIMEOUT=21600
```

Redemarrez Django apres chaque modification du fichier `.env`. Ce fichier est ignore par Git. Le fichier `.env.example` peut servir de modele sans contenir de vraie cle.

PowerShell :

```powershell
$env:GEMINI_API_KEY="votre-cle-api-gemini"
$env:GEMINI_MODEL="gemini-2.5-flash"
$env:CHATBOT_CACHE_TIMEOUT="21600"
python manage.py runserver
```

macOS ou Linux :

```bash
export GEMINI_API_KEY="votre-cle-api-gemini"
export GEMINI_MODEL="gemini-2.5-flash"
export CHATBOT_CACHE_TIMEOUT="21600"
python manage.py runserver
```

Ne placez jamais la vraie cle dans `settings.py`, un template, JavaScript ou un commit Git. Creez une cle depuis Google AI Studio et utilisez de preference une nouvelle cle d'autorisation restreinte a Gemini API.

### Utilisation gratuite

Gemini Developer API propose un niveau gratuit avec des limites de debit. Pour ce projet :

1. Ouvrir Google AI Studio et creer une cle API.
2. Conserver `GEMINI_MODEL="gemini-2.5-flash"` pour des reponses rapides et stables.
3. Placer la cle uniquement dans `GEMINI_API_KEY`.
4. Lancer Django depuis le meme terminal.

Pour une demonstration sans internet ou lorsque la limite gratuite est atteinte, le moteur local et le cache continuent de repondre aux questions basees sur le calendrier. Le cache actuel est en memoire et convient a une demonstration locale. Pour un deploiement avec plusieurs serveurs, utiliser Redis comme backend Django Cache.

### Exposition temporaire avec ngrok

Demarrez d'abord Django avec une configuration publique :

```powershell
$env:DJANGO_SECRET_KEY="une-longue-valeur-aleatoire"
$env:DJANGO_DEBUG="False"
$env:GEMINI_API_KEY="votre-cle-api-gemini"
$env:GEMINI_MODEL="gemini-2.5-flash"
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
├── frontend/        # application React
├── static/
└── docs/
```

## Evolution prevue

- Passage de SQLite a MySQL via la configuration `DATABASES`.
- Envoi de rappels par email.
- Taches planifiees avec Celery ou Django-Q.
- Chatbot plus avance avec NLP ou API IA.
