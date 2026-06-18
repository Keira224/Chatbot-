from django.core.management.base import BaseCommand

from chatbot.models import ChatbotKnowledge


SCENARIOS = [
    ("Role de l'assistant", "Que peux-tu faire ?", "Je peux rechercher les dates du calendrier, expliquer les demarches academiques, retrouver les lieux et resumer les prochaines echeances.", "aide,capacites,faire,assistant,chatbot", "general", "Tous", 30),
    ("Contact scolarite", "Comment contacter la scolarite ?", "Consultez les coordonnees officielles de votre etablissement ou rendez-vous au service de la scolarite pendant les heures d'ouverture.", "contact,scolarite,telephone,email,bureau", "support", "Tous", 12),
    ("Mot de passe oublie", "J'ai oublie mon mot de passe", "Utilisez la procedure de reinitialisation si elle est disponible. Sinon, contactez l'administrateur de la plateforme avec votre identifiant.", "mot de passe,oublie,connexion,compte,identifiant", "support", "Tous", 20),
    ("Modifier le profil", "Comment modifier mon profil ?", "Ouvrez la page Profil, mettez a jour vos informations puis enregistrez. Verifiez notamment votre role, votre departement ou votre filiere.", "modifier,profil,telephone,email,departement,filiere", "support", "Tous", 16),
    ("Inscription administrative", "Comment finaliser mon inscription administrative ?", "Preparez les pieces demandees, verifiez le paiement des frais et deposez le dossier avant la date limite indiquee par la scolarite.", "inscription,administrative,dossier,pieces,scolarite", "registration", "Etudiant", 24),
    ("Inscription pedagogique", "Comment faire l'inscription pedagogique ?", "Selectionnez vos unites d'enseignement sur la plateforme, verifiez votre parcours puis validez avant la date de cloture.", "inscription,pedagogique,unite,enseignement,parcours", "registration", "Etudiant", 24),
    ("Inscription en retard", "Que faire si je rate la date d'inscription ?", "Contactez rapidement la scolarite. Une inscription tardive depend de l'autorisation de l'etablissement et peut exiger un justificatif.", "retard,rate,date,inscription,tardive", "registration", "Etudiant", 22),
    ("Carte etudiante", "Quand recuperer ma carte etudiante ?", "La carte est generalement disponible apres validation de l'inscription administrative. Consultez les annonces de la scolarite.", "carte,etudiante,retirer,recuperer", "registration", "Etudiant", 13),
    ("Choix des cours", "Puis-je modifier mes cours ?", "Une modification est possible pendant la periode d'inscription pedagogique, sous reserve des regles de votre filiere.", "modifier,cours,matiere,unite,choix", "registration", "Etudiant", 14),
    ("Calendrier des examens", "Quand auront lieu les examens ?", "Je consulte les evenements de type Examen dans le calendrier pour vous donner les prochaines dates disponibles.", "examen,examens,date,session,epreuve", "exam", "Tous", 26),
    ("Lieu d'examen", "Ou se deroule mon examen ?", "Le lieu est affiche dans l'evenement correspondant. Verifiez aussi les annonces de derniere minute avant de vous deplacer.", "lieu,salle,examen,amphi,laboratoire", "exam", "Etudiant", 23),
    ("Retard a un examen", "Que faire en cas de retard a l'examen ?", "Presentez-vous immediatement au surveillant. L'admission depend du reglement des examens et du temps de retard.", "retard,examen,surveillant,admission", "exam", "Etudiant", 19),
    ("Absence a un examen", "Je serai absent a un examen", "Informez le service des examens et fournissez un justificatif dans le delai prevu. Une session de remplacement n'est pas automatique.", "absence,absent,examen,justificatif,maladie", "exam", "Etudiant", 22),
    ("Materiel autorise", "Quel materiel est autorise a l'examen ?", "Consultez les consignes de l'enseignant et la convocation. Le materiel autorise varie selon l'epreuve.", "materiel,calculatrice,document,autorise,examen", "exam", "Etudiant", 15),
    ("Publication des notes", "Quand les notes seront-elles publiees ?", "Les resultats sont publies apres correction et deliberation. Consultez l'evenement de publication des resultats ou votre espace academique.", "note,notes,resultat,resultats,publie", "exam", "Etudiant", 18),
    ("Reclamation de note", "Comment faire une reclamation de note ?", "Deposez une reclamation motivee pendant la periode officielle en indiquant la matiere, le groupe et l'evaluation concernee.", "reclamation,note,erreur,resultat,contester", "exam", "Etudiant", 21),
    ("Session de rattrapage", "Qui peut participer au rattrapage ?", "L'acces depend des resultats et du reglement de l'etablissement. Verifiez votre autorisation puis inscrivez-vous avant la date limite.", "rattrapage,session,echec,autorisation", "exam", "Etudiant", 21),
    ("Paiement des frais", "Comment payer les frais universitaires ?", "Effectuez le paiement par le moyen officiel indique par l'etablissement et conservez le recu comme preuve.", "paiement,payer,frais,universitaire,recu", "payment", "Etudiant", 25),
    ("Paiement en plusieurs tranches", "Puis-je payer en plusieurs tranches ?", "Cela depend de la politique de l'etablissement. Consultez les echeances de paiement et contactez le service comptable.", "tranche,echelonnement,paiement,frais", "payment", "Etudiant", 17),
    ("Recu de paiement perdu", "J'ai perdu mon recu de paiement", "Contactez le service comptable avec votre identifiant et les informations de transaction pour demander un duplicata.", "recu,perdu,duplicata,paiement,transaction", "payment", "Etudiant", 18),
    ("Paiement non visible", "Mon paiement n'apparait pas", "Conservez la preuve de transaction et contactez le service comptable. Evitez d'effectuer un second paiement avant verification.", "paiement,non visible,transaction,erreur,validation", "payment", "Etudiant", 22),
    ("Dossier de bourse", "Quels documents faut-il pour la bourse ?", "Preparez le formulaire, le certificat d'inscription et les justificatifs demandes. La liste exacte doit etre confirmee par les affaires sociales.", "bourse,document,dossier,justificatif,affaires sociales", "document", "Etudiant", 18),
    ("Depot de rapport", "Comment deposer mon rapport de stage ?", "Remettez le rapport au format demande, accompagne des validations du maitre de stage et du responsable pedagogique.", "rapport,stage,depot,maitre,validation", "document", "Etudiant", 19),
    ("Document incomplet", "Mon dossier est incomplet", "Ajoutez les pieces manquantes avant la date limite. Si un document est indisponible, contactez le service concerne pour connaitre les alternatives.", "dossier,incomplet,piece,manquante,document", "document", "Tous", 20),
    ("Format du memoire", "Quel format utiliser pour le memoire ?", "Suivez le guide de redaction de votre departement: structure, police, references, nombre d'exemplaires et format numerique.", "format,memoire,redaction,police,reference", "document", "Etudiant", 17),
    ("Choisir un sujet de memoire", "Comment choisir mon sujet de memoire ?", "Choisissez un probleme precis, realisable et lie a votre domaine. Faites valider la fiche de cadrage par votre encadreur.", "sujet,memoire,choisir,cadrage,encadreur", "defense", "Etudiant", 20),
    ("Depot du dossier de soutenance", "Que contient le dossier de soutenance ?", "Le dossier comprend generalement le memoire, la fiche de validation, les autorisations et les exemplaires demandes par le jury.", "dossier,soutenance,memoire,fiche,validation,jury", "defense", "Etudiant", 24),
    ("Preparation de soutenance", "Comment preparer ma soutenance ?", "Preparez une presentation courte: probleme, methode, resultats et recommandations. Repetez et anticipez les questions du jury.", "preparer,soutenance,presentation,jury,question", "defense", "Etudiant", 23),
    ("Duree de soutenance", "Combien de temps dure une soutenance ?", "La duree depend du departement. Verifiez votre convocation et les consignes du responsable des soutenances.", "duree,temps,soutenance,convocation", "defense", "Etudiant", 14),
    ("Absence d'un membre du jury", "Que faire si un membre du jury est absent ?", "Le responsable des soutenances decide du remplacement ou du report. Ne modifiez pas vous-meme le planning.", "jury,absent,absence,report,soutenance", "defense", "Tous", 18),
    ("Planning enseignant", "Comment connaitre mon planning d'enseignement ?", "Consultez le calendrier academique et les communications de votre departement. Signalez rapidement tout conflit d'horaire.", "enseignant,planning,cours,horaire,departement", "teaching", "Enseignant", 22),
    ("Depot des notes enseignant", "Quand deposer les notes ?", "Respectez la date fixee par le service des examens. Verifiez les notes et les absences avant validation definitive.", "enseignant,depot,note,notes,validation", "teaching", "Enseignant", 24),
    ("Modification de note enseignant", "Comment corriger une note deja validee ?", "Suivez la procedure officielle de correction avec justification et validation du responsable pedagogique.", "enseignant,corriger,note,validation,justification", "teaching", "Enseignant", 21),
    ("Organisation d'une reunion", "Comment annoncer une reunion academique ?", "L'administrateur peut ajouter un evenement Reunion avec la date, le lieu, le public concerne et l'objet de la rencontre.", "annoncer,organiser,reunion,academique,administrateur", "teaching", "Enseignant", 18),
    ("Conflit de calendrier", "Deux activites sont programmees au meme moment", "Signalez le conflit au responsable pedagogique avec les deux references. Seule l'administration peut confirmer un changement.", "conflit,chevauchement,horaire,calendrier", "support", "Tous", 20),
    ("Notification non recue", "Je ne recois pas les notifications", "Verifiez vos preferences de rappel, les types d'evenements suivis et votre adresse email. Les notifications internes restent visibles dans l'espace academique.", "notification,alerte,email,non recue,rappel", "support", "Tous", 21),
    ("Modifier les rappels", "Comment changer le delai des rappels ?", "Ouvrez Mes rappels, choisissez les types d'evenements et le delai, puis enregistrez vos preferences.", "modifier,rappel,delai,preference,notification", "support", "Tous", 20),
    ("Exporter le calendrier", "Comment ajouter les evenements a mon agenda ?", "Utilisez Exporter le calendrier pour tous les evenements ou Ajouter agenda sur une carte pour un seul evenement.", "exporter,agenda,ics,calendar,evenement", "support", "Tous", 20),
]


class Command(BaseCommand):
    help = "Ajoute une base de connaissances de demonstration pour le chatbot."

    def handle(self, *args, **options):
        created_count = 0
        updated_count = 0
        for title, question, answer, keywords, category, audience, priority in SCENARIOS:
            _, created = ChatbotKnowledge.objects.update_or_create(
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
            created_count += int(created)
            updated_count += int(not created)

        self.stdout.write(
            self.style.SUCCESS(
                f"Connaissances chatbot pretes. Creees: {created_count}. "
                f"Actualisees: {updated_count}. Total: {len(SCENARIOS)}."
            )
        )
