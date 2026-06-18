from datetime import timedelta
import hashlib
import json
import logging
import re
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from django.conf import settings
from django.core.cache import cache
from django.db.models import Count, Max
from django.utils import timezone

from calendar_app.models import AcademicEvent
from chatbot.models import ChatbotKnowledge, ChatMessage

logger = logging.getLogger(__name__)


KEYWORD_EVENT_TYPES = {
    AcademicEvent.INSCRIPTION: ["inscription", "inscriptions", "inscrire"],
    AcademicEvent.EXAM: ["examen", "examens", "controle", "epreuve"],
    AcademicEvent.DEFENSE: ["soutenance", "soutenances"],
    AcademicEvent.PAYMENT: ["paiement", "payer", "frais"],
    AcademicEvent.FILE_SUBMISSION: ["depot", "dossier", "dossiers", "memoire"],
    AcademicEvent.MEETING: ["reunion", "reunions", "information"],
}

LOCAL_FAQ = {
    "bonjour": "Bonjour. Je peux vous aider a retrouver les examens, inscriptions, paiements, reunions, depots de dossiers et soutenances du calendrier.",
    "salut": "Bonjour. Posez-moi une question sur une date academique ou demandez-moi les prochains evenements.",
    "merci": "Avec plaisir. Vous pouvez aussi me demander les evenements de cette semaine ou la prochaine date importante.",
}


def normalize(text):
    replacements = {"é": "e", "è": "e", "ê": "e", "à": "a", "ù": "u", "ç": "c", "ô": "o", "î": "i"}
    value = text.lower()
    for source, target in replacements.items():
        value = value.replace(source, target)
    return value


def clean_question(question):
    value = question.strip()
    normalized = normalize(value)
    greetings = ["bonjour", "bonsoir", "salut", "hello"]
    for greeting in greetings:
        if normalized == greeting:
            return value
        if normalized.startswith(f"{greeting} "):
            return value[len(greeting):].lstrip(" ,.!?:;-")
    return value


def answer_question(question, include_source=False):
    effective_question = clean_question(question)
    key = chatbot_cache_key(effective_question)
    cached_result = cache.get(key)
    if cached_result:
        if isinstance(cached_result, str):
            cached_result = {"answer": cached_result, "source": ChatMessage.LOCAL}
        return cached_result if include_source else cached_result["answer"]

    local_answer = answer_common_question(effective_question)
    if local_answer:
        answer = local_answer
        source = ChatMessage.LOCAL
    else:
        knowledge_matches = find_relevant_knowledge(effective_question)
        if should_answer_from_knowledge(effective_question, knowledge_matches):
            answer = knowledge_matches[0]["item"].answer
            source = ChatMessage.KNOWLEDGE
        else:
            answer = answer_with_gemini(effective_question, knowledge_matches)
            if answer:
                source = ChatMessage.GEMINI
            else:
                answer = (
                    answer_with_local_rules(effective_question)
                    if is_live_calendar_question(effective_question)
                    else answer_from_knowledge(knowledge_matches) or answer_with_local_rules(effective_question)
                )
                source = ChatMessage.CALENDAR if is_live_calendar_question(effective_question) else ChatMessage.KNOWLEDGE

    result = {"answer": answer, "source": source}
    cache.set(key, result, getattr(settings, "CHATBOT_CACHE_TIMEOUT", 21600))
    return result if include_source else answer


def chatbot_cache_key(question):
    calendar_state = AcademicEvent.objects.aggregate(total=Count("id"), updated_at=Max("updated_at"))
    knowledge_state = ChatbotKnowledge.objects.filter(is_active=True).aggregate(total=Count("id"), updated_at=Max("updated_at"))
    calendar_updated = calendar_state["updated_at"].isoformat() if calendar_state["updated_at"] else "empty"
    knowledge_updated = knowledge_state["updated_at"].isoformat() if knowledge_state["updated_at"] else "empty"
    raw_key = (
        f"version:{getattr(settings, 'CHATBOT_CACHE_VERSION', '1')}|"
        f"{normalize(question).strip()}|"
        f"events:{calendar_state['total']}:{calendar_updated}|"
        f"knowledge:{knowledge_state['total']}:{knowledge_updated}"
    )
    digest = hashlib.sha256(raw_key.encode("utf-8")).hexdigest()
    return f"chatbot:answer:{digest}"


def answer_common_question(question):
    text = normalize(question).strip()
    for keyword, answer in LOCAL_FAQ.items():
        if text == keyword:
            return answer

    if any(value in text for value in ["que peux tu faire", "comment peux tu aider", "aide moi", "besoin d aide"]):
        return (
            "Je peux rechercher les prochaines dates, filtrer par type d'evenement, "
            "indiquer les lieux et resumer les echeances de la semaine."
        )
    if "combien" in text and "evenement" in text and not any(keyword in text for keywords in KEYWORD_EVENT_TYPES.values() for keyword in keywords):
        count = AcademicEvent.objects.upcoming().count()
        return f"Le calendrier contient {count} evenement(s) a venir."
    return None


def tokenize(value):
    cleaned = normalize(value)
    for character in "?,.;:!'\"()[]/-_":
        cleaned = cleaned.replace(character, " ")
    return {token for token in cleaned.split() if len(token) > 2}


def find_relevant_knowledge(question, limit=5):
    question_tokens = tokenize(question)
    if not question_tokens:
        return []

    matches = []
    for item in ChatbotKnowledge.objects.filter(is_active=True):
        keyword_tokens = tokenize(" ".join(item.keyword_list()))
        title_tokens = tokenize(f"{item.title} {item.sample_question}")
        answer_tokens = tokenize(item.answer)
        score = (
            len(question_tokens & keyword_tokens) * 4
            + len(question_tokens & title_tokens) * 3
            + len(question_tokens & answer_tokens)
            + item.priority / 100
        )
        if score >= 3:
            matches.append({"item": item, "score": score})
    return sorted(matches, key=lambda match: match["score"], reverse=True)[:limit]


def should_answer_from_knowledge(question, matches):
    if not matches or matches[0]["score"] < 7:
        return False
    return not is_live_calendar_question(question)


def is_live_calendar_question(question):
    text = normalize(question)
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
    return any(term in text for term in live_calendar_terms)


def answer_from_knowledge(matches):
    if not matches:
        return None
    return matches[0]["item"].answer


def answer_with_gemini(question, knowledge_matches=None):
    api_key = getattr(settings, "GEMINI_API_KEY", "")
    if not api_key:
        return None

    model = getattr(settings, "GEMINI_MODEL", "gemini-2.5-flash")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    prompt = build_gemini_prompt(question, knowledge_matches)
    expected_events = list(relevant_events_for_question(question))
    result = request_gemini(url, api_key, prompt, max_output_tokens=2048)
    if result["finish_reason"] == "MAX_TOKENS":
        result = request_gemini(url, api_key, prompt, max_output_tokens=4096)
    if not validate_gemini_answer(question, result, expected_events):
        logger.warning("Gemini answer rejected because it was incomplete or insufficiently grounded.")
        return None
    return result["text"]


def request_gemini(url, api_key, prompt, max_output_tokens):
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt,
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.15,
            "maxOutputTokens": max_output_tokens,
            "responseMimeType": "text/plain",
            "thinkingConfig": {
                "thinkingBudget": 0,
            },
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
        return {"text": None, "finish_reason": "ERROR"}

    candidates = data.get("candidates", [])
    if not candidates:
        return {"text": None, "finish_reason": "NO_CANDIDATE"}
    candidate = candidates[0]
    parts = candidate.get("content", {}).get("parts", [])
    answer_parts = [
        part.get("text", "").strip()
        for part in parts
        if part.get("text") and not part.get("thought")
    ]
    finish_reason = candidate.get("finishReason", "")
    answer = "\n".join(answer_parts).strip() or None
    if finish_reason and finish_reason != "STOP":
        logger.warning("Gemini stopped with finish reason %s", finish_reason)
    return {"text": answer, "finish_reason": finish_reason}


def build_gemini_prompt(question, knowledge_matches=None):
    today = timezone.localdate()
    events = relevant_events_for_question(question)
    event_lines = []
    for event in events:
        event_lines.append(
            "- {title} | type: {event_type} | debut: {start:%d/%m/%Y} | fin: {end:%d/%m/%Y} | lieu: {location} | details: {description}".format(
                title=event.title,
                event_type=event.get_event_type_display(),
                start=event.start_date,
                end=event.end_date,
                location=event.location or "Non precise",
                description=event.description,
            )
        )

    events_context = "\n".join(event_lines) or "Aucun evenement a venir dans le calendrier."
    knowledge_matches = knowledge_matches if knowledge_matches is not None else find_relevant_knowledge(question)
    if is_live_calendar_question(question):
        knowledge_matches = []
    knowledge_lines = [
        f"- {match['item'].title}: {match['item'].answer}"
        for match in knowledge_matches[:5]
    ]
    knowledge_context = "\n".join(knowledge_lines) or "Aucune procedure interne pertinente n'a ete trouvee."
    return "\n".join(
        [
            "Tu es l'assistant academique AcadReminder.",
            "Reponds en francais, de maniere courte, claire et utile pour un etudiant ou un enseignant.",
            "Reponds en texte simple. N'utilise pas de Markdown, pas d'asterisques et pas de tableaux.",
            "Pour chaque evenement, donne le titre, la date ou periode, le lieu et une courte explication utile.",
            "Utilise uniquement les evenements fournis ci-dessous pour les dates et les lieux.",
            "N'invente aucune date, aucun lieu et aucun evenement absent du contexte.",
            "Si plusieurs evenements sont demandes, presente-les sur des lignes separees et termine chaque evenement avant de passer au suivant.",
            "Utilise les procedures de reference pour les demarches generales.",
            requested_count_instruction(question),
            "Si l'information n'existe pas dans ce contexte, dis que le calendrier ne contient pas encore cette information.",
            f"Date du jour: {today:%d/%m/%Y}",
            "",
            "Evenements connus:",
            events_context,
            "",
            "Procedures de reference pertinentes:",
            knowledge_context,
            "",
            f"Question de l'utilisateur: {question}",
        ]
    )


def validate_gemini_answer(question, result, expected_events):
    answer = result.get("text") or ""
    if result.get("finish_reason") not in {"", "STOP"}:
        return False
    if len(answer) < 120:
        return False
    if not is_live_calendar_question(question) or not expected_events:
        return True

    requested_count = extract_requested_count(question) or min(len(expected_events), 3)
    expected_titles = [normalize(event.title) for event in expected_events[:requested_count]]
    normalized_answer = normalize(answer)
    included_titles = sum(title in normalized_answer for title in expected_titles)
    return included_titles >= min(requested_count, len(expected_titles))


def relevant_events_for_question(question):
    text = normalize(question)
    today = timezone.localdate()
    events = AcademicEvent.objects.upcoming()

    for event_type, keywords in KEYWORD_EVENT_TYPES.items():
        if any(keyword in text for keyword in keywords):
            events = events.filter(event_type=event_type)
            break

    if "aujourd" in text:
        events = events.filter(start_date__lte=today, end_date__gte=today)
    elif "demain" in text:
        tomorrow = today + timedelta(days=1)
        events = events.filter(start_date__lte=tomorrow, end_date__gte=tomorrow)
    elif "semaine" in text:
        events = events.filter(start_date__lte=today + timedelta(days=7))
    elif "mois" in text:
        events = events.filter(start_date__lte=today + timedelta(days=31))

    requested_count = extract_requested_count(question)
    return events[: requested_count or 20]


def extract_requested_count(question):
    match = re.search(r"\b(\d{1,2})\s+(?:prochains?\s+)?evenements?\b", normalize(question))
    if not match:
        return None
    return min(max(int(match.group(1)), 1), 20)


def requested_count_instruction(question):
    requested_count = extract_requested_count(question)
    if requested_count:
        return f"Donne exactement {requested_count} evenement(s), si le contexte en contient suffisamment."
    return "Selectionne les informations les plus pertinentes pour repondre a la question."


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

    if "lieu" in text or "ou " in text:
        events = list(events[:5])
        if not events:
            return "Je n'ai trouve aucun lieu correspondant dans le calendrier."
        lines = ["Voici les lieux indiques dans le calendrier :"]
        for event in events:
            lines.append(f"- {event.title} : {event.location or 'lieu non precise'}.")
        return "\n".join(lines)

    requested_count = extract_requested_count(question)
    if requested_count:
        events = events[:requested_count]
    elif "prochaine" in text or "prochain" in text or "important" in text or "date" in text or "calendrier" in text:
        events = events[:5]
    else:
        events = events[:3]

    events = list(events)
    if not events:
        return "Je n'ai trouve aucune echeance correspondant a votre question."

    return format_grounded_event_answer(events, today)


def format_grounded_event_answer(events, today=None):
    today = today or timezone.localdate()
    lines = ["Voici les informations confirmees dans le calendrier academique :"]
    for index, event in enumerate(events, start=1):
        days_left = (event.start_date - today).days
        if days_left == 0:
            delay = "commence aujourd'hui"
        elif days_left == 1:
            delay = "commence demain"
        elif days_left > 1:
            delay = f"commence dans {days_left} jours"
        else:
            delay = "est deja commence"

        period = f"le {event.start_date:%d/%m/%Y}"
        if event.end_date != event.start_date:
            period = f"du {event.start_date:%d/%m/%Y} au {event.end_date:%d/%m/%Y}"

        lines.extend(
            [
                "",
                f"{index}. {event.title}",
                f"Date : {period} ({delay}).",
                f"Lieu : {event.location or 'non precise dans le calendrier'}.",
                f"Details : {event.description}",
            ]
        )
    return "\n".join(lines)
