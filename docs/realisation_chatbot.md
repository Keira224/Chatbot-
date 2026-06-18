# Réalisation technique du chatbot AcadReminder

## 1. Présentation

Le chatbot AcadReminder est un assistant académique intégré à une application React avec un backend Django. Son objectif est d’aider les étudiants et enseignants à retrouver rapidement :

- les prochaines dates académiques ;
- les examens, inscriptions et soutenances ;
- les lieux des événements ;
- les échéances de paiement ;
- les procédures administratives ;
- les rappels et informations générales de la plateforme.

Le chatbot a été conçu comme un système hybride. Il combine :

1. des réponses locales simples ;
2. une base de connaissances administrable ;
3. les événements enregistrés dans le calendrier ;
4. l’API Gemini ;
5. un mécanisme de validation et de secours ;
6. un cache pour réduire les appels externes.

Cette architecture permet au chatbot de continuer à fonctionner même sans connexion Internet ou sans clé Gemini.

---

## 2. Objectifs techniques

Les objectifs retenus pendant la réalisation étaient les suivants :

- fournir des réponses basées sur les données réelles du calendrier ;
- éviter d’inventer des dates, lieux ou événements ;
- répondre sans Gemini lorsque cela est possible ;
- conserver un historique des conversations ;
- limiter le coût et le nombre d’appels à l’API externe ;
- permettre à l’administrateur de modifier les réponses de référence ;
- protéger l’accès au chatbot avec l’authentification Django ;
- séparer clairement l’interface React de la logique métier Django.

---

## 3. Architecture générale

```text
┌──────────────────────────────┐
│       Interface React        │
│                              │
│ - Zone de conversation       │
│ - Historique                 │
│ - Questions rapides          │
│ - Affichage de la source     │
└──────────────┬───────────────┘
               │
               │ POST JSON
               │ /accounts/api/etudiant/chat/
               ▼
┌──────────────────────────────┐
│       API Django             │
│                              │
│ - Session utilisateur        │
│ - Protection CSRF            │
│ - Validation de la requête   │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│  Orchestrateur du chatbot    │
│  chatbot/services.py         │
│                              │
│ 1. Cache                     │
│ 2. FAQ locale                │
│ 3. Base de connaissances     │
│ 4. Calendrier                │
│ 5. Gemini                    │
│ 6. Validation                │
│ 7. Repli local               │
└───────┬──────────┬───────────┘
        │          │
        ▼          ▼
┌─────────────┐  ┌─────────────┐
│  SQLite     │  │ Gemini API  │
│             │  │             │
│ Événements  │  │ Génération  │
│ Scénarios   │  │ contrôlée   │
│ Historique  │  │             │
└─────────────┘  └─────────────┘
```

---

## 4. Organisation du code

Les principales responsabilités sont réparties ainsi :

| Fichier | Responsabilité |
|---|---|
| `chatbot/models.py` | Modèles de l’historique et de la base de connaissances |
| `chatbot/services.py` | Logique principale et orchestration des réponses |
| `chatbot/admin.py` | Administration des connaissances et messages |
| `chatbot/tests.py` | Tests du moteur, du cache et de Gemini |
| `chatbot/management/commands/seed_chatbot_knowledge.py` | Chargement des scénarios initiaux |
| `accounts/api_views.py` | Endpoint JSON utilisé par React |
| `calendar_app/models.py` | Source des événements académiques |
| `frontend/src/main.jsx` | Interface de conversation |
| `config/settings.py` | Configuration Gemini et cache |

---

## 5. Modèles de données

### 5.1 Historique des messages

Le modèle `ChatMessage` conserve chaque échange.

```python
class ChatMessage(models.Model):
    GEMINI = "gemini"
    CALENDAR = "calendar"
    KNOWLEDGE = "knowledge"
    LOCAL = "local"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="chat_messages",
    )
    question = models.TextField()
    answer = models.TextField()
    source = models.CharField(
        max_length=20,
        choices=SOURCE_CHOICES,
        default=LOCAL,
    )
    created_at = models.DateTimeField(auto_now_add=True)
```

Ce modèle permet de connaître :

- l’auteur de la question ;
- le contenu de la question ;
- la réponse produite ;
- le moteur ayant produit la réponse ;
- la date de l’échange.

Les sources possibles sont :

| Valeur | Signification |
|---|---|
| `local` | Réponse simple produite localement |
| `knowledge` | Réponse provenant de la base de connaissances |
| `calendar` | Réponse calculée depuis les événements |
| `gemini` | Réponse produite et validée depuis Gemini |

### 5.2 Base de connaissances

Le modèle `ChatbotKnowledge` stocke les procédures et réponses de référence.

```python
class ChatbotKnowledge(models.Model):
    title = models.CharField(max_length=180, unique=True)
    sample_question = models.CharField(max_length=255)
    answer = models.TextField()
    keywords = models.CharField(max_length=500)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES)
    audience = models.CharField(max_length=120, blank=True)
    priority = models.PositiveSmallIntegerField(default=10)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

Une connaissance contient :

- un scénario ;
- une question d’exemple ;
- une réponse officielle ;
- une liste de mots-clés ;
- une catégorie ;
- le public concerné ;
- une priorité ;
- un état actif ou inactif.

Les connaissances peuvent être gérées dans Django Admin sans modifier le code.

---

## 6. Chargement des connaissances initiales

Une commande Django initialise la base de connaissances :

```powershell
python manage.py seed_chatbot_knowledge
```

Le fichier concerné est :

```text
chatbot/management/commands/seed_chatbot_knowledge.py
```

Les scénarios couvrent notamment :

- l’inscription administrative et pédagogique ;
- les examens et rattrapages ;
- les paiements ;
- les documents ;
- les soutenances ;
- les besoins des enseignants ;
- les notifications ;
- l’assistance utilisateur.

La commande utilise `update_or_create`. Elle peut donc être relancée sans créer de doublons :

```python
ChatbotKnowledge.objects.update_or_create(
    title=title,
    defaults={
        "sample_question": question,
        "answer": answer,
        "keywords": keywords,
        "category": category,
        "audience": audience,
        "priority": priority,
        "is_active": True,
    },
)
```

---

## 7. Workflow complet d’une question

### Étape 1 — Envoi depuis React

L’utilisateur saisit une question dans l’interface React.

React envoie une requête JSON :

```http
POST /accounts/api/etudiant/chat/
Content-Type: application/json
X-CSRFToken: <jeton>
```

Corps de la requête :

```json
{
  "question": "Quels sont les 3 prochains examens ?"
}
```

### Étape 2 — Contrôle de la session

L’endpoint est protégé avec `login_required`.

```python
@login_required
@require_POST
def api_chat(request):
    ...
```

Un administrateur ne peut pas utiliser cette route :

```python
if request.user.is_staff:
    return JsonResponse(
        {"detail": "Le chatbot est disponible dans l'espace academique."},
        status=403,
    )
```

### Étape 3 — Validation de la question

Le corps JSON est décodé et la question est nettoyée :

```python
payload = json_body(request)
question = (payload or {}).get("question", "").strip()

if not question:
    return JsonResponse(
        {"detail": "La question est obligatoire."},
        status=400,
    )
```

### Étape 4 — Appel de l’orchestrateur

L’API appelle la fonction principale :

```python
result = answer_question(question, include_source=True)
```

La fonction `answer_question` se trouve dans `chatbot/services.py`.

### Étape 5 — Enregistrement de l’échange

Après la génération, l’échange est sauvegardé :

```python
message = ChatMessage.objects.create(
    user=request.user,
    question=question,
    answer=result["answer"],
    source=result["source"],
)
```

### Étape 6 — Réponse vers React

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

React ajoute ensuite le message à l’historique affiché.

---

## 8. Orchestration des réponses

La fonction principale suit cet ordre :

```python
def answer_question(question, include_source=False):
    effective_question = clean_question(question)
    key = chatbot_cache_key(effective_question)

    cached_result = cache.get(key)
    if cached_result:
        return cached_result

    local_answer = answer_common_question(effective_question)

    if local_answer:
        answer = local_answer
        source = ChatMessage.LOCAL
    else:
        knowledge_matches = find_relevant_knowledge(effective_question)

        if should_answer_from_knowledge(
            effective_question,
            knowledge_matches,
        ):
            answer = knowledge_matches[0]["item"].answer
            source = ChatMessage.KNOWLEDGE
        else:
            answer = answer_with_gemini(
                effective_question,
                knowledge_matches,
            )

            if answer:
                source = ChatMessage.GEMINI
            else:
                answer = answer_with_local_rules(effective_question)
                source = ChatMessage.CALENDAR

    result = {"answer": answer, "source": source}
    cache.set(key, result, settings.CHATBOT_CACHE_TIMEOUT)
    return result
```

Version simplifiée du workflow :

```text
Question
   |
   v
Cache disponible ?
   |
   +-- Oui --> retourner la réponse
   |
   +-- Non
         |
         v
Question simple ?
   |
   +-- Oui --> réponse locale
   |
   +-- Non
         |
         v
Connaissance suffisamment pertinente ?
   |
   +-- Oui --> réponse de référence
   |
   +-- Non
         |
         v
Gemini disponible ?
   |
   +-- Oui --> génération puis validation
   |
   +-- Non ou réponse rejetée
         |
         v
Réponse construite depuis le calendrier
```

---

## 9. Nettoyage et compréhension de la question

### 9.1 Normalisation

La fonction `normalize` facilite la recherche de mots-clés :

```python
def normalize(text):
    replacements = {
        "é": "e",
        "è": "e",
        "ê": "e",
        "à": "a",
        "ù": "u",
        "ç": "c",
        "ô": "o",
        "î": "i",
    }

    value = text.lower()

    for source, target in replacements.items():
        value = value.replace(source, target)

    return value
```

Exemple :

```text
"Où se déroule l'épreuve ?"
                |
                v
"ou se deroule l'epreuve ?"
```

### 9.2 Suppression des salutations

Une salutation placée avant une vraie question est retirée :

```text
"Bonjour, quels sont les prochains examens ?"
                         |
                         v
"quels sont les prochains examens ?"
```

Une simple question comme `Bonjour` conserve cependant une réponse locale.

### 9.3 Détection des catégories

Les catégories sont reliées à des mots-clés :

```python
KEYWORD_EVENT_TYPES = {
    AcademicEvent.INSCRIPTION: [
        "inscription",
        "inscriptions",
        "inscrire",
    ],
    AcademicEvent.EXAM: [
        "examen",
        "examens",
        "controle",
        "epreuve",
    ],
    AcademicEvent.DEFENSE: [
        "soutenance",
        "soutenances",
    ],
}
```

La première catégorie détectée sert à filtrer le calendrier.

---

## 10. Recherche dans la base de connaissances

La question et les connaissances sont transformées en ensembles de mots.

Un score est calculé selon :

- les mots-clés : coefficient 4 ;
- le titre et la question d’exemple : coefficient 3 ;
- les mots de la réponse : coefficient 1 ;
- la priorité du scénario.

```python
score = (
    len(question_tokens & keyword_tokens) * 4
    + len(question_tokens & title_tokens) * 3
    + len(question_tokens & answer_tokens)
    + item.priority / 100
)
```

Une connaissance est retenue si son score est supérieur ou égal à 3.

Elle peut être utilisée directement si :

- le meilleur score est supérieur ou égal à 7 ;
- la question ne demande pas une information dynamique du calendrier.

Cette règle évite de répondre avec une procédure générale lorsque l’utilisateur demande une date précise.

---

## 11. Détection des questions dynamiques

Certaines expressions indiquent que la réponse doit utiliser les événements actuels :

```python
live_calendar_terms = [
    "quand",
    "date",
    "aujourd",
    "demain",
    "semaine",
    "prochain",
    "calendrier",
    "lieu",
    "ou se",
    "combien d evenement",
]
```

Exemples :

```text
"Comment préparer ma soutenance ?"
→ base de connaissances

"Quand aura lieu la prochaine soutenance ?"
→ calendrier
```

---

## 12. Sélection des événements

La fonction `relevant_events_for_question` sélectionne les événements utiles.

Elle commence avec les événements à venir :

```python
events = AcademicEvent.objects.upcoming()
```

Elle applique ensuite plusieurs filtres.

### Filtre par type

```python
if "examen" in text:
    events = events.filter(event_type=AcademicEvent.EXAM)
```

### Filtre temporel

```python
if "aujourd" in text:
    events = events.filter(
        start_date__lte=today,
        end_date__gte=today,
    )
elif "demain" in text:
    ...
elif "semaine" in text:
    events = events.filter(
        start_date__lte=today + timedelta(days=7),
    )
```

### Nombre demandé

Une expression régulière détecte des demandes comme :

```text
"les 5 prochains événements"
```

```python
match = re.search(
    r"\b(\d{1,2})\s+(?:prochains?\s+)?evenements?\b",
    normalize(question),
)
```

Le nombre est limité entre 1 et 20 pour éviter un contexte trop important.

---

## 13. Construction du prompt Gemini

Gemini reçoit uniquement les données nécessaires.

Chaque événement est transformé en ligne structurée :

```text
- Examen final
  | type: Examen
  | debut: 25/06/2026
  | fin: 25/06/2026
  | lieu: Amphi A
  | details: Evaluation de fin de semestre
```

Le prompt contient :

- le rôle de l’assistant ;
- la langue attendue ;
- les règles de réponse ;
- la date du jour ;
- les événements pertinents ;
- les procédures de référence pertinentes ;
- la question de l’utilisateur.

Extrait des contraintes :

```text
Tu es l'assistant academique AcadReminder.
Reponds en francais.
Utilise uniquement les événements fournis pour les dates et les lieux.
N'invente aucune date, aucun lieu et aucun événement.
Si l'information n'existe pas, indique-le clairement.
```

Cette approche est une forme de génération augmentée par récupération :

```text
Recherche des données
        +
Ajout au contexte
        +
Génération par Gemini
```

---

## 14. Appel de l’API Gemini

La configuration est chargée depuis `.env` :

```env
GEMINI_API_KEY=votre-cle-api-gemini
GEMINI_MODEL=gemini-2.5-flash
CHATBOT_CACHE_TIMEOUT=21600
CHATBOT_CACHE_VERSION=3
```

Dans `config/settings.py` :

```python
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL = os.environ.get(
    "GEMINI_MODEL",
    "gemini-2.5-flash",
)
```

L’URL est construite côté serveur :

```python
url = (
    "https://generativelanguage.googleapis.com/"
    f"v1beta/models/{model}:generateContent"
)
```

Paramètres de génération :

```python
"generationConfig": {
    "temperature": 0.15,
    "maxOutputTokens": 2048,
    "responseMimeType": "text/plain",
    "thinkingConfig": {
        "thinkingBudget": 0,
    },
}
```

Le choix d’une température basse rend les réponses plus stables et moins créatives.

Le délai maximal de la requête est de 12 secondes :

```python
with urlopen(request, timeout=12) as response:
    ...
```

Si Gemini atteint la limite de jetons, une seconde tentative est réalisée avec une limite supérieure.

---

## 15. Validation des réponses Gemini

Une réponse Gemini n’est pas acceptée automatiquement.

Elle est rejetée si :

- l’API retourne une erreur ;
- aucun candidat n’est disponible ;
- la génération n’est pas terminée normalement ;
- la réponse est trop courte ;
- les événements attendus ne sont pas présents.

```python
def validate_gemini_answer(question, result, expected_events):
    answer = result.get("text") or ""

    if result.get("finish_reason") not in {"", "STOP"}:
        return False

    if len(answer) < 120:
        return False

    ...
```

Pour une question liée au calendrier, le validateur vérifie la présence des titres des événements attendus :

```python
included_titles = sum(
    title in normalized_answer
    for title in expected_titles
)
```

Cette validation réduit le risque qu’une réponse soit incomplète ou non fondée sur les données du projet.

---

## 16. Moteur local de secours

Si Gemini est indisponible ou si sa réponse est rejetée, le chatbot produit une réponse locale.

Le moteur local sait :

- compter les événements ;
- filtrer par type ;
- filtrer par période ;
- afficher les lieux ;
- afficher les prochaines dates ;
- présenter les descriptions ;
- calculer le nombre de jours avant une échéance.

Exemple de réponse :

```text
Voici les informations confirmées dans le calendrier académique :

1. Examen final
Date : le 25/06/2026 (commence dans 7 jours).
Lieu : Amphi A.
Détails : Évaluation de fin de semestre.
```

Le chatbot reste donc opérationnel :

- sans clé Gemini ;
- sans Internet ;
- lorsque la limite gratuite est atteinte ;
- lorsqu’une réponse externe est invalide.

---

## 17. Cache des réponses

Le cache évite de recalculer ou de renvoyer la même question à Gemini.

La clé est construite avec :

- la version du cache ;
- la question normalisée ;
- le nombre d’événements ;
- la dernière modification du calendrier ;
- le nombre de connaissances actives ;
- la dernière modification des connaissances.

```python
raw_key = (
    f"version:{settings.CHATBOT_CACHE_VERSION}|"
    f"{normalize(question).strip()}|"
    f"events:{event_count}:{event_updated}|"
    f"knowledge:{knowledge_count}:{knowledge_updated}"
)
```

La clé finale est un hash SHA-256 :

```python
digest = hashlib.sha256(
    raw_key.encode("utf-8"),
).hexdigest()
```

### Invalidation automatique

Lorsque l’administrateur :

- ajoute un événement ;
- modifie un événement ;
- ajoute une connaissance ;
- modifie une connaissance ;

l’état des données change. Une nouvelle clé est produite, donc l’ancienne réponse n’est plus réutilisée.

### Configuration actuelle

```python
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "acadreminder-cache",
        "TIMEOUT": 21600,
    }
}
```

`LocMemCache` convient au développement. Redis est recommandé pour un déploiement avec plusieurs serveurs.

---

## 18. Intégration dans React

React utilise une fonction générique pour appeler l’API :

```javascript
async function api(url, options = {}) {
  const response = await fetch(url, {
    credentials: "same-origin",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCookie("csrftoken"),
      ...options.headers,
    },
    ...options,
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || "Une erreur est survenue.");
  }

  return data;
}
```

Pour envoyer une question :

```javascript
const result = await api("/accounts/api/etudiant/chat/", {
  method: "POST",
  body: JSON.stringify({ question }),
});
```

Le nouveau message est ensuite ajouté à l’état React :

```javascript
setMessages((current) => [
  ...current,
  result.message,
]);
```

L’interface existe sous deux formes :

- une page complète consacrée à l’assistant ;
- un panneau de discussion accessible depuis les autres vues.

---

## 19. Sécurité

### Authentification

Le chatbot nécessite une session Django valide.

### Protection CSRF

React lit le cookie `csrftoken` et l’envoie dans l’en-tête :

```http
X-CSRFToken: <token>
```

### Protection de la clé Gemini

La clé est stockée uniquement dans `.env` :

```env
GEMINI_API_KEY=...
```

Elle n’est jamais :

- envoyée dans React ;
- stockée dans JavaScript ;
- écrite dans le dépôt Git ;
- retournée dans une réponse JSON.

### Contrôle des rôles

Seuls les étudiants et enseignants authentifiés peuvent appeler l’endpoint du chatbot.

### Validation des entrées

Le backend vérifie :

- la présence d’un corps JSON valide ;
- la présence de la question ;
- le type de requête HTTP ;
- le rôle de l’utilisateur.

---

## 20. Gestion des erreurs

Le système traite plusieurs situations.

| Situation | Comportement |
|---|---|
| Question vide | Réponse HTTP 400 |
| JSON invalide | Réponse HTTP 400 |
| Utilisateur non connecté | Redirection ou refus d’accès |
| Administrateur sur l’API étudiant | Réponse HTTP 403 |
| Clé Gemini absente | Moteur local |
| Erreur réseau Gemini | Journalisation et moteur local |
| Réponse Gemini tronquée | Nouvelle tentative ou moteur local |
| Aucun événement trouvé | Message explicite |
| Connaissance non trouvée | Calendrier, Gemini ou repli local |

---

## 21. Tests automatisés

Les tests sont situés dans :

```text
chatbot/tests.py
accounts/tests.py
```

Ils vérifient notamment :

- la réutilisation d’une réponse mise en cache ;
- l’invalidation du cache après modification du calendrier ;
- la réponse directe d’un scénario de connaissance ;
- le calcul de pertinence des scénarios ;
- le nettoyage des salutations ;
- l’envoi des événements pertinents à Gemini ;
- la limitation du nombre d’événements dans le prompt ;
- le contenu du moteur local ;
- le rejet d’une réponse Gemini tronquée ;
- les permissions de l’API ;
- la séparation entre espace académique et espace administrateur.

Commandes :

```powershell
python manage.py check
python manage.py test accounts chatbot
```

État de la dernière validation :

```text
19 tests exécutés
19 tests réussis
0 erreur
```

---

## 22. Processus de réalisation

### Phase 1 — Modélisation

- création de `ChatMessage` ;
- création de `ChatbotKnowledge` ;
- ajout du champ `source` ;
- création des migrations.

### Phase 2 — Moteur local

- normalisation des questions ;
- détection des mots-clés ;
- filtrage des événements ;
- formatage des réponses.

### Phase 3 — Base de connaissances

- création des catégories ;
- création de la commande de peuplement ;
- calcul d’un score de pertinence ;
- gestion depuis Django Admin.

### Phase 4 — Intégration Gemini

- création du prompt ;
- envoi de la requête HTTP ;
- configuration du modèle ;
- traitement des erreurs réseau ;
- validation des réponses.

### Phase 5 — Cache

- création d’une clé liée aux données ;
- mise en cache des réponses ;
- invalidation automatique.

### Phase 6 — API

- création de l’endpoint JSON ;
- protection par session ;
- protection CSRF ;
- enregistrement de l’historique.

### Phase 7 — Interface React

- création de la page assistant ;
- création du panneau de discussion ;
- affichage de l’historique ;
- gestion du chargement et des erreurs.

### Phase 8 — Tests

- tests des règles locales ;
- tests du cache ;
- tests du prompt ;
- tests du repli ;
- tests des permissions.

---

## 23. Workflow d’exploitation

### Première installation

```powershell
python manage.py migrate
python manage.py seed_academic_events
python manage.py seed_chatbot_knowledge
```

### Démarrage

```powershell
python manage.py runserver
```

### Modification des connaissances

1. Se connecter à `/admin/`.
2. Ouvrir les connaissances chatbot.
3. Ajouter ou modifier un scénario.
4. Enregistrer.
5. La nouvelle version sera automatiquement prise en compte dans les prochaines clés de cache.

### Modification du modèle Gemini

Dans `.env` :

```env
GEMINI_MODEL=gemini-2.5-flash
```

Redémarrer ensuite Django.

### Forcer le renouvellement général du cache

Modifier :

```env
CHATBOT_CACHE_VERSION=4
```

Puis redémarrer Django.

---

## 24. Limites actuelles

- La normalisation des accents est partielle.
- La recherche de connaissances repose sur des mots-clés et non sur des embeddings.
- Le cache en mémoire n’est pas partagé entre plusieurs processus.
- L’historique est limité aux huit derniers messages dans le tableau de bord.
- Il n’existe pas encore de conversation distincte avec un titre.
- Gemini est appelé avec `urllib` sans bibliothèque cliente spécialisée.
- Les réponses ne sont pas diffusées progressivement en streaming.
- Le chatbot ne lit pas encore de documents PDF ou Word.

---

## 25. Roadmap proposée

### Court terme

- compléter la normalisation Unicode ;
- ajouter davantage de tests API ;
- ajouter une pagination de l’historique ;
- permettre la suppression d’une conversation ;
- afficher la source de chaque réponse plus clairement ;
- ajouter des indicateurs de chargement plus détaillés.

### Moyen terme

- remplacer `LocMemCache` par Redis ;
- organiser les messages en conversations ;
- ajouter des retours utilisateur utiles/inutiles ;
- améliorer la recherche des connaissances ;
- ajouter une journalisation structurée ;
- ajouter des métriques sur les appels Gemini.

### Long terme

- utiliser des embeddings pour la recherche sémantique ;
- intégrer une base vectorielle ;
- permettre l’import de règlements et documents académiques ;
- ajouter un système RAG documentaire ;
- diffuser les réponses en streaming ;
- prendre en charge plusieurs établissements ;
- personnaliser les réponses selon la filière et le niveau ;
- ajouter une politique de conservation des conversations.

Roadmap visuelle :

```text
Version actuelle
   |
   +-- Moteur local
   +-- Calendrier
   +-- Base de connaissances
   +-- Gemini
   +-- Cache
   +-- Historique
   |
   v
Prochaine version
   |
   +-- Redis
   +-- Conversations
   +-- Feedback utilisateur
   +-- Meilleure observabilité
   |
   v
Version avancée
   |
   +-- Embeddings
   +-- Base vectorielle
   +-- Documents académiques
   +-- RAG
   +-- Streaming
```

---

## 26. Résumé

Le chatbot AcadReminder a été réalisé comme un service hybride et résilient.

Son fonctionnement ne dépend pas entièrement de Gemini :

- les questions simples sont traitées localement ;
- les procédures sont recherchées dans une base administrable ;
- les dates et lieux proviennent du calendrier Django ;
- Gemini améliore la formulation lorsque cela est nécessaire ;
- les réponses externes sont contrôlées avant utilisation ;
- un moteur local prend le relais en cas d’échec ;
- le cache améliore les performances ;
- l’historique permet de suivre les échanges.

Cette architecture apporte un compromis entre intelligence artificielle, fiabilité des données, coût d’utilisation et continuité de service.
