import unittest

from critical_thinking.models import Intent, ReviewLevel
from critical_thinking.policy import choose_review_level, should_inject_review


class PolicyTests(unittest.TestCase):
    def test_personal_experience_stays_normal_even_with_technical_words(self):
        request = choose_review_level("Ich fühle mich wegen des Servers überfordert.", Intent.PERSONAL_EXPERIENCE)
        self.assertEqual(request.level, ReviewLevel.NORMAL)
        self.assertFalse(should_inject_review(request))

    def test_technical_proposal_gets_review(self):
        request = choose_review_level("Wir sollten ein Hermes-Plugin bauen.", Intent.PROJECT_PROPOSAL)
        self.assertEqual(request.level, ReviewLevel.REVIEW)

    def test_sensitive_architecture_change_gets_critical(self):
        request = choose_review_level("Wir sollten die komplette Architektur ändern.", Intent.PROJECT_PROPOSAL)
        self.assertEqual(request.level, ReviewLevel.CRITICAL)

    def test_explicit_review_request_gets_critical(self):
        request = choose_review_level("Prüfe kritisch: Ist dieser Plan sinnvoll?", Intent.QUESTION)
        self.assertEqual(request.level, ReviewLevel.CRITICAL)
        self.assertTrue(request.user_requested)

    def test_explicit_review_request_can_challenge_an_opinion(self):
        request = choose_review_level("Ich finde das gut. Prüfe kritisch, ob das stimmt.", Intent.OPINION)
        self.assertEqual(request.level, ReviewLevel.CRITICAL)

    def test_security_question_does_not_trigger_critical_review(self):
        request = choose_review_level("Wie lösche ich alte Testdaten?", Intent.QUESTION)
        self.assertEqual(request.level, ReviewLevel.NORMAL)

    def test_unrelated_question_does_not_trigger_review(self):
        request = choose_review_level("Wie spät ist es?", Intent.QUESTION)
        self.assertEqual(request.level, ReviewLevel.NORMAL)


if __name__ == "__main__":
    unittest.main()
