from datetime import timedelta
from unittest.mock import patch

from django.core.cache import cache
from django.test import TestCase
from django.utils import timezone

from calendar_app.models import AcademicEvent

from .models import ChatbotKnowledge
from .services import (
    answer_question,
    build_gemini_prompt,
    chatbot_cache_key,
    clean_question,
    extract_requested_count,
    find_relevant_knowledge,
    format_grounded_event_answer,
    validate_gemini_answer,
)


class ChatbotCacheTests(TestCase):
    def setUp(self):
        cache.clear()

    @patch("chatbot.services.answer_common_question", return_value=None)
    @patch("chatbot.services.answer_with_gemini", return_value="Reponse simulee par l'IA")
    def test_same_question_uses_cached_answer(self, gemini_mock, _common_mock):
        first_answer = answer_question("Explique-moi la prochaine activite academique")
        second_answer = answer_question("Explique-moi la prochaine activite academique")

        self.assertEqual(first_answer, second_answer)
        self.assertEqual(gemini_mock.call_count, 1)

    def test_calendar_update_changes_cache_key(self):
        event = AcademicEvent.objects.create(
            title="Reunion academique",
            description="Reunion de coordination.",
            event_type=AcademicEvent.MEETING,
            start_date=timezone.localdate() + timedelta(days=3),
            end_date=timezone.localdate() + timedelta(days=3),
            location="Salle A",
        )
        first_key = chatbot_cache_key("Quand est la reunion ?")

        event.location = "Salle B"
        event.save()
        second_key = chatbot_cache_key("Quand est la reunion ?")

        self.assertNotEqual(first_key, second_key)

    def test_knowledge_scenario_answers_without_gemini(self):
        ChatbotKnowledge.objects.create(
            title="Reclamation de note",
            sample_question="Comment reclamer une note ?",
            answer="Deposez une reclamation motivee au service des examens.",
            keywords="reclamation,note,contester,resultat",
            category=ChatbotKnowledge.EXAM,
            priority=20,
        )

        with patch("chatbot.services.answer_with_gemini") as gemini_mock:
            answer = answer_question("Comment faire une reclamation de note ?")

        self.assertIn("reclamation motivee", answer)
        gemini_mock.assert_not_called()

    def test_knowledge_search_returns_relevant_scenario(self):
        relevant = ChatbotKnowledge.objects.create(
            title="Paiement non visible",
            sample_question="Mon paiement n'apparait pas",
            answer="Contactez le service comptable.",
            keywords="paiement,transaction,non visible,validation",
            category=ChatbotKnowledge.PAYMENT,
            priority=20,
        )
        ChatbotKnowledge.objects.create(
            title="Preparation soutenance",
            sample_question="Comment preparer ma soutenance ?",
            answer="Preparez votre presentation.",
            keywords="soutenance,jury,presentation",
            category=ChatbotKnowledge.DEFENSE,
            priority=20,
        )

        matches = find_relevant_knowledge("Pourquoi mon paiement n'est pas visible ?")

        self.assertEqual(matches[0]["item"], relevant)

    def test_greeting_is_removed_from_a_real_question(self):
        self.assertEqual(
            clean_question("Bonjour quels sont les evenements cette semaine ?"),
            "quels sont les evenements cette semaine ?",
        )

    @patch("chatbot.services.answer_with_gemini", return_value="Voici les evenements de la semaine.")
    def test_question_starting_with_greeting_reaches_gemini(self, gemini_mock):
        answer = answer_question("Bonjour quels sont les evenements cette semaine ?")

        self.assertEqual(answer, "Voici les evenements de la semaine.")
        gemini_mock.assert_called_once()

    def test_gemini_prompt_contains_relevant_calendar_events(self):
        start_date = timezone.localdate() + timedelta(days=2)
        AcademicEvent.objects.create(
            title="Reunion de coordination",
            description="Coordination des activites academiques.",
            event_type=AcademicEvent.MEETING,
            start_date=start_date,
            end_date=start_date,
            location="Salle du conseil",
        )

        prompt = build_gemini_prompt("Quels sont les evenements cette semaine ?")

        self.assertIn("Reunion de coordination", prompt)
        self.assertIn("Salle du conseil", prompt)

    def test_requested_event_count_limits_prompt_context(self):
        for index in range(5):
            start_date = timezone.localdate() + timedelta(days=index + 1)
            AcademicEvent.objects.create(
                title=f"Evenement {index + 1}",
                description="Activite academique.",
                event_type=AcademicEvent.MEETING,
                start_date=start_date,
                end_date=start_date,
                location="Campus",
            )

        prompt = build_gemini_prompt("Donne-moi les 3 evenements de cette semaine")

        self.assertEqual(extract_requested_count("les 3 evenements"), 3)
        self.assertIn("Donne exactement 3 evenement(s)", prompt)
        self.assertNotIn("Evenement 4", prompt)

    def test_grounded_fallback_contains_dates_location_and_description(self):
        start_date = timezone.localdate() + timedelta(days=2)
        event = AcademicEvent.objects.create(
            title="Examen de reseaux",
            description="Evaluation ecrite sur les protocoles et la securite.",
            event_type=AcademicEvent.EXAM,
            start_date=start_date,
            end_date=start_date,
            location="Salle 12",
        )

        answer = format_grounded_event_answer([event])

        self.assertIn("Examen de reseaux", answer)
        self.assertIn(start_date.strftime("%d/%m/%Y"), answer)
        self.assertIn("Salle 12", answer)
        self.assertIn("protocoles et la securite", answer)

    def test_truncated_gemini_answer_is_rejected(self):
        start_date = timezone.localdate() + timedelta(days=2)
        event = AcademicEvent.objects.create(
            title="Examen de reseaux",
            description="Evaluation ecrite.",
            event_type=AcademicEvent.EXAM,
            start_date=start_date,
            end_date=start_date,
            location="Salle 12",
        )

        is_valid = validate_gemini_answer(
            "Quel est le prochain examen ?",
            {"text": "Examen de reseaux : du 20/", "finish_reason": "MAX_TOKENS"},
            [event],
        )

        self.assertFalse(is_valid)
