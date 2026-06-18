# AcadReminder

AcadReminder est une plateforme web de gestion des dates académiques importantes. L’interface utilisateur est entièrement développée avec React, tandis que Django fournit l’API, l’authentification, les règles métier et l’accès aux données.

Le projet permet aux étudiants et enseignants de consulter le calendrier académique, configurer leurs rappels et interroger un assistant conversationnel. Les administrateurs disposent d’un espace séparé pour superviser les utilisateurs et gérer les événements.

## État du projet

Rapport mis à jour le 18 juin 2026.

- Interface entièrement migrée vers React.
- Anciens templates Django supprimés.
- Authentification et inscription intégrées à React.
- API Django protégée selon le rôle de l’utilisateur.
- Compilation de production React validée.
- Vérification Django sans erreur.
- 19 tests automatisés réussis.

## Fonctionnalités

### Espace académique

- Inscription comme étudiant ou enseignant.
- Connexion et déconnexion sécurisées avec une session Django.
- Tableau de bord avec statistiques et prochaines échéances.
- Calendrier mensuel interactif.
- Liste, recherche et filtrage des événements.
- Consultation des inscriptions, examens, soutenances, paiements, réunions et dépôts de dossiers.
- Export des événements au format `.ics`.
- Gestion du profil académique.
- Configuration des types de rappels, du délai et des alertes par email.
- Consultation et marquage des notifications comme lues.
- Assistant académique avec historique de conversation.

### Espace administrateur

- Tableau de bord de supervision.
- Statistiques sur les étudiants, enseignants, événements et notifications.
- Liste et recherche des utilisateurs.
- Création, modification et suppression des événements.
- Accès séparé des comptes académiques.
- Administration Django disponible à l’adresse `/admin/`.

### Assistant académique

Le chatbot utilise trois niveaux de réponse :

1. Les scénarios enregistrés dans la base de connaissances.
2. Les événements présents dans le calendrier.
3. Gemini lorsque la clé API est configurée.

Si Gemini est indisponible ou si aucune clé n’est fournie, le moteur local continue de répondre à partir des données académiques disponibles. Les réponses sont mises en cache afin de limiter les appels externes.

## Architecture

```text
Navigateur
   |
   v
Application React
   |
   | Requêtes JSON avec session et protection CSRF
   v
API Django
   |
   +-- Comptes et rôles
   +-- Calendrier académique
   +-- Rappels et notifications
   +-- Chatbot et cache
   |
   v
Base de données SQLite
```

Django sert le fichier compilé `static/react/index.html` pour les pages publiques, académiques et administratives. Les anciennes vues fonctionnelles redirigent vers les écrans correspondants dans React.

## Technologies

### Backend

- Python
- Django 5
- SQLite
- Sessions Django
- Protection CSRF
- API JSON

### Frontend

- React 18
- Vite 6
- Lucide React
- CSS responsive personnalisé

### Intelligence artificielle

- Gemini Developer API
- Moteur local de secours
- Base de connaissances administrable
- Cache Django

## Structure du projet

```text
acadreminder/
├── accounts/          # comptes, rôles, authentification et API
├── calendar_app/      # événements et exports de calendrier
├── chatbot/           # assistant, Gemini et base de connaissances
├── config/            # configuration principale Django
├── docs/              # documentation complémentaire
├── frontend/          # sources React et configuration Vite
├── reminders/         # préférences, notifications et emails
├── static/react/      # application React compilée
├── .env.example       # exemple de configuration
├── manage.py
├── README.md
└── requirements.txt
```

Le dossier `templates/` n’est plus utilisé : l’affichage de l’application est assuré par React.

## Prérequis

- Python 3.11 ou version supérieure.
- Node.js 18 ou version supérieure.
- npm.
- Git.

## Installation sous Windows

```powershell
git clone https://github.com/Keira224/Chatbot-.git
cd "Chatbot-"

python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

Copy-Item .env.example .env

python manage.py migrate
python manage.py seed_academic_events
python manage.py seed_chatbot_knowledge
python manage.py createsuperuser

cd frontend
npm install
npm run build
cd ..

python manage.py runserver
```

## Installation sous macOS ou Linux

```bash
git clone https://github.com/Keira224/Chatbot-.git
cd Chatbot-

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env

python manage.py migrate
python manage.py seed_academic_events
python manage.py seed_chatbot_knowledge
python manage.py createsuperuser

cd frontend
npm install
npm run build
cd ..

python manage.py runserver
```

Ouvrir ensuite `http://127.0.0.1:8000/`.

## Configuration

Créer un fichier `.env` à la racine du projet à partir de `.env.example` :

```env
DJANGO_SECRET_KEY=remplacez-par-une-longue-cle-secrete
DJANGO_DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
CSRF_TRUSTED_ORIGINS=http://127.0.0.1:8000,http://localhost:8000

GEMINI_API_KEY=votre-cle-api-gemini
GEMINI_MODEL=gemini-2.5-flash
CHATBOT_CACHE_TIMEOUT=21600
CHATBOT_CACHE_VERSION=3
```

`GEMINI_API_KEY` est facultative. Le fichier `.env` est ignoré par Git et ne doit jamais être ajouté au dépôt.

Après une modification du fichier `.env`, redémarrer le serveur Django.

## Utilisation

### Adresses principales

- Application : `http://127.0.0.1:8000/`
- Espace académique : `http://127.0.0.1:8000/accounts/espace-academique/`
- Espace administrateur : `http://127.0.0.1:8000/accounts/espace-admin/`
- Administration Django : `http://127.0.0.1:8000/admin/`

L’application redirige automatiquement chaque utilisateur vers l’espace correspondant à son rôle.

### Développement du frontend

Pour modifier React :

```powershell
cd frontend
npm install
npm run dev
```

Pour générer les fichiers utilisés par Django :

```powershell
cd frontend
npm run build
```

La compilation est écrite dans `static/react/`.

### Commandes Django utiles

```powershell
python manage.py check
python manage.py makemigrations
python manage.py migrate
python manage.py seed_academic_events
python manage.py seed_chatbot_knowledge
python manage.py generate_reminders
python manage.py createsuperuser
python manage.py runserver
```

## Tests et validation

Exécuter les tests :

```powershell
python manage.py test accounts chatbot
```

Exécuter les contrôles complets avant un commit :

```powershell
python manage.py check
python manage.py test accounts chatbot

cd frontend
npm run build
```

État de la dernière validation :

- `python manage.py check` : réussi.
- `python manage.py test accounts chatbot` : 19 tests réussis.
- `npm run build` : réussi.

Les tests couvrent notamment :

- la séparation des espaces étudiant, enseignant et administrateur ;
- les permissions des API d’administration ;
- l’inscription et les rôles ;
- les données du tableau de bord ;
- le cache du chatbot ;
- la sélection des événements pertinents ;
- le moteur local et le repli en cas de réponse Gemini invalide.

## Sécurité

- Les mots de passe sont gérés par le système d’authentification Django.
- Les requêtes d’écriture utilisent la protection CSRF.
- Les API administratives vérifient le statut administrateur.
- La clé Gemini reste exclusivement côté serveur.
- Le fichier `.env`, la base SQLite et les environnements virtuels sont ignorés par Git.
- En production, désactiver le mode debug et utiliser une clé Django secrète robuste.

## Déploiement

Pour un environnement public :

- définir `DJANGO_DEBUG=False` ;
- configurer `ALLOWED_HOSTS` et `CSRF_TRUSTED_ORIGINS` ;
- exécuter `npm run build` ;
- exécuter `python manage.py collectstatic` ;
- utiliser PostgreSQL ou MySQL à la place de SQLite ;
- servir Django avec un serveur WSGI ou ASGI ;
- servir les fichiers statiques avec un service dédié ;
- utiliser Redis pour partager le cache entre plusieurs instances.

Ngrok peut être utilisé pour une démonstration temporaire, mais ne constitue pas un hébergement de production.

## Améliorations prévues

- Planification automatique des rappels avec Celery.
- Backend Redis pour le cache et les tâches.
- Envoi d’emails avec un fournisseur SMTP.
- Historique de conversations plus complet.
- Pagination des événements et utilisateurs.
- Déploiement avec PostgreSQL.
- Tests frontend automatisés.
