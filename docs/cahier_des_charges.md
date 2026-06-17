# CAHIER DES CHARGES

## Projet : AcadReminder - Chatbot de rappel des dates importantes academiques

---

# Informations Generales

| Element | Detail |
| --- | --- |
| Nom du projet | AcadReminder |
| Type de projet | Application web academique |
| Domaine | Gestion academique et assistance etudiante |
| Client cible | Etablissements universitaires et etudiants |
| Realise par | Ousmane Keira |
| Matricule | 664185012340 |
| Niveau | Licence 3 |
| Technologie principale | Django |
| Base de donnees | SQLite / MySQL |
| Methodologie | Genie Logiciel |

---

# 1. Contexte du Projet

Dans plusieurs etablissements universitaires, les etudiants oublient souvent les dates importantes liees aux activites academiques telles que :

- les inscriptions ;
- les examens ;
- les soutenances ;
- les depots de dossiers ;
- les paiements administratifs.

Ces oublis entrainent des retards, des penalites administratives et des difficultes academiques.

Le projet AcadReminder vise a developper une plateforme web intelligente permettant aux etudiants :

- de consulter facilement le calendrier academique ;
- de recevoir des rappels automatiques ;
- d'interagir avec un chatbot academique capable de repondre aux questions liees aux echeances universitaires.

---

# 2. Problematique

Comment aider les etudiants a suivre efficacement les echeances academiques afin de reduire les oublis et ameliorer l'organisation universitaire ?

---

# 3. Objectifs du Projet

## 3.1 Objectif General

Developper une application web permettant la gestion intelligente des rappels academiques pour les etudiants.

## 3.2 Objectifs Specifiques

Le systeme devra permettre :

- l'authentification des etudiants ;
- la consultation des evenements academiques ;
- la reception de notifications et rappels ;
- la personnalisation des rappels ;
- l'utilisation d'un chatbot academique ;
- la gestion des evenements par un administrateur.

---

# 4. Description Generale du Systeme

AcadReminder est une application web developpee avec Django permettant :

- l'affichage des evenements academiques ;
- la gestion des rappels ;
- l'interaction via un chatbot ;
- la gestion administrative des evenements.

Le systeme sera accessible depuis un navigateur web.

---

# 5. Acteurs du Systeme

## 5.1 Etudiant

L'etudiant peut :

- creer un compte ;
- se connecter ;
- consulter les evenements ;
- discuter avec le chatbot ;
- recevoir des notifications ;
- personnaliser ses rappels.

## 5.2 Administrateur

L'administrateur peut :

- ajouter des evenements ;
- modifier des evenements ;
- supprimer des evenements ;
- gerer les utilisateurs ;
- superviser le systeme.

---

# 6. Fonctionnalites Fonctionnelles

## 6.1 Gestion des Comptes

Le systeme doit permettre :

- l'inscription ;
- la connexion ;
- la deconnexion ;
- la gestion du profil utilisateur.

## 6.2 Gestion du Calendrier Academique

Le systeme doit permettre :

- l'ajout d'evenements ;
- la modification d'evenements ;
- la suppression d'evenements ;
- l'affichage des evenements ;
- la recherche d'evenements.

### Types d'evenements

- Inscription
- Examen
- Soutenance
- Paiement
- Depot de dossier
- Reunion
- Autre

## 6.3 Chatbot Academique

Le chatbot doit :

- repondre aux questions simples ;
- rechercher les evenements dans la base de donnees ;
- afficher les dates importantes ;
- guider les etudiants.

### Exemples de questions

- Quand commencent les examens ?
- Quelle est la date limite d'inscription ?
- Quand aura lieu la soutenance ?
- Quelles sont les prochaines echeances ?

## 6.4 Notifications et Rappels

Le systeme doit permettre :

- l'envoi de rappels automatiques ;
- l'affichage des notifications ;
- la personnalisation des delais de rappel.

### Delais possibles

- 7 jours avant
- 3 jours avant
- 1 jour avant
- Jour meme

## 6.5 Tableau de Bord Etudiant

Le tableau de bord doit afficher :

- les prochains evenements ;
- les notifications ;
- les preferences de rappel ;
- les statistiques simples.

---

# 7. Besoins Non Fonctionnels

Le systeme devra etre :

## 7.1 Securise

- authentification securisee ;
- protection des donnees ;
- gestion des sessions.

## 7.2 Rapide

- chargement rapide des pages ;
- optimisation des requetes.

## 7.3 Maintenable

- architecture claire ;
- code commente ;
- modularite.

## 7.4 Responsive

Le systeme devra fonctionner sur :

- ordinateur ;
- tablette ;
- smartphone.

---

# 8. Technologies Utilisees

| Element | Technologie |
| --- | --- |
| Backend | Django |
| Frontend | HTML5, CSS3, Bootstrap 5 |
| Base de donnees | SQLite / MySQL |
| Langage principal | Python |
| Versionnement | Git & GitHub |
| IDE recommande | VS Code |

---

# 9. Architecture Technique

## Architecture choisie

Architecture MVC/MVT de Django :

- Model : gestion des donnees ;
- View : logique metier ;
- Template : interface utilisateur.

---

# 10. Structure Previsionnelle du Projet

```text
acadreminder/
├── accounts/
├── calendar_app/
├── chatbot/
├── reminders/
├── templates/
├── static/
├── docs/
├── manage.py
├── requirements.txt
└── README.md
```

---

# 11. Base de Donnees

## 11.1 Table Etudiant

| Champ | Type |
| --- | --- |
| id | Integer |
| nom | String |
| email | String |
| mot_de_passe | String |

## 11.2 Table Evenement

| Champ | Type |
| --- | --- |
| id | Integer |
| title | String |
| description | Text |
| event_type | String |
| start_date | Date |
| end_date | Date |
| location | String |

## 11.3 Table Notification

| Champ | Type |
| --- | --- |
| id | Integer |
| user | ForeignKey |
| evenement | ForeignKey |
| message | Text |
| is_read | Boolean |

---

# 12. Interfaces du Systeme

Le systeme comportera les interfaces suivantes :

- Page d'accueil
- Connexion
- Inscription
- Tableau de bord
- Calendrier academique
- Detail evenement
- Chatbot
- Notifications
- Profil utilisateur
- Supervision administrateur

---

# 13. Contraintes Techniques

- Utilisation de Django ;
- Compatibilite avec SQLite ;
- Deploiement local simple ;
- Projet executable avec :

```bash
python manage.py runserver
```

---

# 14. Livrables Attendus

Le projet devra fournir :

- le code source complet ;
- la base de donnees ;
- le cahier des charges ;
- le README ;
- le guide d'installation ;
- la documentation technique ;
- les captures d'ecran ;
- la presentation finale.

---

# 15. Planning Previsionnel

| Phase | Description |
| --- | --- |
| Analyse | Etude des besoins |
| Conception | Architecture et base de donnees |
| Developpement | Creation du systeme |
| Tests | Verification des fonctionnalites |
| Documentation | Redaction des documents |
| Presentation | Soutenance du projet |

---

# 16. Conclusion

Le projet AcadReminder permettra de moderniser la gestion des rappels academiques en offrant aux etudiants un systeme intelligent de consultation et de notification des echeances universitaires.

Grace a son chatbot integre et a son systeme de rappels personnalises, cette plateforme contribuera a ameliorer l'organisation academique des etudiants et a reduire les oublis administratifs.
