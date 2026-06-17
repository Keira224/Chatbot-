from datetime import timedelta
import json
import logging
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from django.conf import settings
from django.utils import timezone

from calendar_app.models import AcademicEvent

logger = logging.getLogger(__name__)


KEYWORD_EVENT_TYPES = {
    AcademicEvent.INSCRIPTION: ["inscription", "inscriptions", "inscrire"],
    AcademicEvent.EXAM: ["examen", "examens", "controle", "epreuve"],
    AcademicEvent.DEFENSE: ["soutenance", "soutenances"],
    AcademicEvent.PAYMENT: ["paiement", "payer", "frais"],
    AcademicEvent.FILE_SUBMISSION: ["depot", "dossier", "dossiers", "memoire"],
    AcademicEvent.MEETING: ["reunion", "reunions", "information"],
}


def normalize(text):
    replacements = {"é": "e", "è": "e", "ê": "e", "à": "a", "ù": "u", "ç": "c", "ô": "o", "î": "i"}
    value = text.lower()
    for source, target in replacements.items():
        value = value.replace(source, target)
    return value


def answer_question(question):
    gemini_answer = answer_with_gemini(question)
    if gemini_answer:
        return gemini_answer
    return answer_with_local_rules(question)


def answer_with_gemini(question):
    api_key = getattr(settings, "GEMINI_API_KEY", "")
    if not api_key:
        return None

    model = getattr(settings, "GEMINI_MODEL", "gemini-3.5-flash")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": build_gemini_prompt(question),
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 700,
        },
    }
    request = Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": api_key,
        },
        method="POST",
    )

    try:
        with urlopen(request, timeout=12) as response:
            data = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
        logger.warning("Gemini unavailable, falling back to local chatbot: %s", exc)
        return None

    candidates = data.get("candidates", [])
    if not candidates:
        return None
    parts = candidates[0].get("content", {}).get("parts", [])
    answer_parts = [part.get("text", "").strip() for part in parts if part.get("text")]
    return "\n".join(answer_parts).strip() or None


def build_gemini_prompt(question):
    today = timezone.localdate()
    events = AcademicEvent.objects.upcoming()[:12]
    event_lines = []
    for event in events:
        event_lines.append(
            "- {title} | type: {event_type} | debut: {start:%d/%m/%Y} | fin: {end:%d/%m/%Y} | lieu: {location}".format(
                title=event.title,
                event_type=event.get_event_type_display(),
                start=event.start_date,
                end=event.end_date,
                location=event.location or "Non precise",
            )
        )

    events_context = "\n".join(event_lines) or "Aucun evenement a venir dans le calendrier."
    return "\n".join(
        [
            "Tu es l'assistant academique AcadReminder.",
            "Reponds en francais, de maniere courte, claire et utile pour un etudiant.",
            "Utilise uniquement les evenements fournis ci-dessous pour les dates et les lieux.",
            "Si l'information n'existe pas dans ce contexte, dis que le calendrier ne contient pas encore cette information.",
            f"Date du jour: {today:%d/%m/%Y}",
            "",
            "Evenements connus:",
            events_context,
            "",
            f"Question de l'etudiant: {question}",
        ]
    )


def answer_with_local_rules(question):
    text = normalize(question)
    events = AcademicEvent.objects.upcoming()

    matched_type = None
    for event_type, keywords in KEYWORD_EVENT_TYPES.items():
        if any(keyword in text for keyword in keywords):
            matched_type = event_type
            break

    if matched_type:
        events = events.filter(event_type=matched_type)

    today = timezone.localdate()
    if "aujourd" in text:
        events = events.filter(start_date__lte=today, end_date__gte=today)
    elif "demain" in text:
        tomorrow = today + timedelta(days=1)
        events = events.filter(start_date__lte=tomorrow, end_date__gte=tomorrow)
    elif "semaine" in text:
        events = events.filter(start_date__lte=today + timedelta(days=7))

    if "combien" in text:
        count = events.count()
        return f"J'ai trouve {count} evenement(s) correspondant a votre question."

    if "prochaine" in text or "important" in text or "date" in text or "calendrier" in text:
        events = events[:5]
    else:
        events = events[:3]

    events = list(events)
    if not events:
        return "Je n'ai trouve aucune echeance correspondant a votre question."

    lines = ["Voici les informations trouvees dans le calendrier academique :"]
    for event in events:
        days_left = (event.start_date - today).days
        if days_left == 0:
            delay = "aujourd'hui"
        elif days_left == 1:
            delay = "demain"
        else:
            delay = f"dans {days_left} jour(s)"
        lines.append(f"- {event.title} : du {event.start_date:%d/%m/%Y} au {event.end_date:%d/%m/%Y}, {delay}.")
    return "\n".join(lines)
