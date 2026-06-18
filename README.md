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

Le chatbot est un système hybride. Il ne transmet pas directement toutes les questions à Gemini : il recherche d’abord une réponse locale fiable, puis utilise l’IA uniquement lorsque cela apporte une valeur supplémentaire.

Ordre de traitement :

1. Recherche d’une réponse déjà présente dans le cache.
2. Traitement des questions simples : salutation, aide ou nombre d’événements.
3. Recherche dans la base de connaissances.
4. Préparation d’un contexte contenant uniquement les événements pertinents.
5. Appel à Gemini si une clé API est configurée.
6. Validation de la réponse Gemini.
7. Repli vers le moteur local si Gemini est absent, indisponible ou imprécis.
8. Enregistrement de la question, de la réponse et de sa source.

La source affichée dans l’historique peut être :

- `Gemini` : réponse générée par le modèle externe ;
- `Calendrier` : réponse construite à partir des événements ;
- `Base de connaissances` : procédure enregistrée dans Django ;
- `Réponse locale` : salutation ou réponse déterministe simple.

### Chaîne de traitement du chatbot

```text
Utilisateur React
      |
      | POST /accounts/api/etudiant/chat/
      v
API Django authentifiée
      |
      v
Nettoyage et normalisation de la question
      |
      v
Recherche dans le cache
      |
      +---- réponse trouvée ----------------------+
      |                                          |
      | non                                      |
      v                                          |
FAQ locale et base de connaissances              |
      |                                          |
      v                                          |
Sélection des événements pertinents              |
      |                                          |
      v                                          |
Construction d’un prompt contrôlé                |
      |                                          |
      v                                          |
Gemini configuré ?                               |
      |                                          |
   oui|     |non                                  |
      v     v                                     |
Validation  Moteur local                         |
      |       |                                   |
      +-------+-----------------------------------+
              |
              v
Cache + enregistrement dans ChatMessage
              |
              v
Réponse JSON vers React
```

### Compréhension des questions

Avant le traitement, la question est normalisée :

- conversion en minuscules ;
- suppression partielle des accents pour la recherche ;
- retrait des salutations placées avant une vraie question ;
- découpage en mots significatifs ;
- détection du type d’événement demandé.

Le moteur reconnaît notamment :

- `inscription`, `inscrire` ;
- `examen`, `contrôle`, `épreuve` ;
- `soutenance` ;
- `paiement`, `frais` ;
- `dépôt`, `dossier`, `mémoire` ;
- `réunion`.

Il interprète aussi des périodes comme `aujourd’hui`, `demain`, `cette semaine` ou `ce mois`, ainsi que des quantités telles que « les 5 prochains événements ».

### Base de connaissances

Le modèle `ChatbotKnowledge` contient les réponses de référence qui ne dépendent pas directement du calendrier :

- titre du scénario ;
- question d’exemple ;
- réponse officielle ;
- mots-clés ;
- catégorie ;
- public concerné ;
- priorité ;
- état actif ou inactif.

La recherche attribue un score aux scénarios selon les mots présents dans la question, le titre, la question d’exemple, la réponse et la priorité. Une réponse suffisamment pertinente peut être utilisée directement sans appel à Gemini.

Les scénarios de démonstration sont chargés avec :

```powershell
python manage.py seed_chatbot_knowledge
```

Ils couvrent notamment les inscriptions, examens, paiements, documents, soutenances, enseignants, comptes et notifications. Ils peuvent ensuite être modifiés depuis Django Admin.

### Sélection des événements

Pour une question liée au calendrier, Django interroge `AcademicEvent.objects.upcoming()` puis applique les filtres détectés :

- type d’événement ;
- période demandée ;
- nombre maximal d’éléments.

Seuls les événements retenus sont ajoutés au contexte envoyé à Gemini. Pour chaque événement, le contexte contient :

- le titre ;
- le type ;
- la date de début et de fin ;
- le lieu ;
- la description.

Cette sélection réduit le volume du prompt et limite les réponses inventées.

### Intégration Gemini

L’appel est effectué côté serveur avec l’API Gemini `generateContent`. La clé n’est jamais envoyée au navigateur.

Le prompt demande au modèle :

- de répondre en français ;
- de rester court et clair ;
- d’utiliser uniquement les événements fournis pour les dates et les lieux ;
- de ne rien inventer ;
- de signaler lorsque l’information n’existe pas ;
- de présenter chaque événement avec sa période, son lieu et une explication.

La température est fixée à `0.15` afin de favoriser des réponses stables. Le délai réseau est limité à 12 secondes.

### Validation et mécanisme de secours

Une réponse Gemini n’est pas acceptée automatiquement. Le backend la rejette notamment si :

- l’appel réseau échoue ;
- aucun candidat n’est retourné ;
- la génération est interrompue ;
- la réponse est trop courte ;
- les événements attendus ne sont pas cités dans une réponse liée au calendrier.

En cas de rejet, le moteur local produit une réponse structurée depuis la base de données. Il peut indiquer les événements, périodes, délais, lieux et descriptions sans dépendre d’un service externe.

### Cache et invalidation

Chaque réponse est mise en cache pendant la durée définie par `CHATBOT_CACHE_TIMEOUT`, soit six heures par défaut.

La clé de cache contient :

- la version configurée dans `CHATBOT_CACHE_VERSION` ;
- la question normalisée ;
- le nombre d’événements et leur dernière modification ;
- le nombre de connaissances actives et leur dernière modification.

Ainsi, une modification du calendrier ou de la base de connaissances produit automatiquement une nouvelle clé. Une ancienne réponse ne sera donc pas réutilisée après une mise à jour des données.

Le cache actuel utilise `LocMemCache`. Il convient au développement et aux démonstrations sur un seul processus. Pour un déploiement avec plusieurs instances Django, Redis est recommandé.

### Historique des conversations

Chaque échange validé crée un objet `ChatMessage` contenant :

- l’utilisateur ;
- la question ;
- la réponse ;
- la source utilisée ;
- la date de création.

Le tableau de bord académique retourne les huit messages les plus récents afin d’afficher l’historique dans React.

### API du chatbot

Endpoint :

```text
POST /accounts/api/etudiant/chat/
```

Cette route nécessite une session Django authentifiée et un jeton CSRF. Elle est réservée aux étudiants et enseignants.

Exemple de requête :

```json
{
  "question": "Quels sont les 3 prochains examens ?"
}
```

Exemple de réponse :

```json
{
  "message": {
    "id": 12,
    "question": "Quels sont les 3 prochains examens ?",
    "answer": "Voici les informations confirmées...",
    "source": "calendar",
    "source_label": "Calendrier",
    "created_at": "2026-06-18T10:30:00Z"
  }
}
```

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
   +-- Orchestrateur du chatbot
   |      +-- FAQ locale
   |      +-- Base de connaissances
   |      +-- Données du calendrier
   |      +-- Gemini
   |      +-- Validation et repli local
   |      +-- Cache
   |
   v
Base de données SQLite
```

Django sert le fichier compilé `static/react/index.html` pour les pages publiques, académiques et administratives. Les anciennes vues fonctionnelles redirigent vers les écrans correspondants dans React.

### Répartition des responsabilités

| Composant | Responsabilité |
|---|---|
| `frontend/src/main.jsx` | Interface React, envoi des questions et affichage de l’historique |
| `accounts/api_views.py` | Authentification de la requête et endpoint JSON du chatbot |
| `chatbot/services.py` | Orchestration, recherche, Gemini, validation, cache et moteur local |
| `chatbot/models.py` | Historique des messages et base de connaissances |
| `calendar_app/models.py` | Source officielle des événements académiques |
| `config/settings.py` | Clé Gemini, modèle, version et durée du cache |

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
