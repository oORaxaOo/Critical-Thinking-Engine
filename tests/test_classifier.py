import unittest

from critical_thinking.classifier import classify_message
from critical_thinking.models import Intent


class ClassifierTests(unittest.TestCase):
    def test_personal_experience_is_not_misclassified_as_a_proposal(self):
        self.assertEqual(classify_message("Ich fühle mich gerade überfordert."), Intent.PERSONAL_EXPERIENCE)

    def test_opinion_is_classified_without_automatic_critique(self):
        self.assertEqual(classify_message("Ich finde diese Idee gut."), Intent.OPINION)

    def test_technical_proposal_is_detected(self):
        self.assertEqual(classify_message("Wir sollten ein weiteres KI-Modell integrieren."), Intent.PROJECT_PROPOSAL)

    def test_hedged_technical_proposal_is_not_lost_as_an_opinion(self):
        self.assertEqual(
            classify_message("Ich glaube, wir sollten ein weiteres KI-Modell integrieren."),
            Intent.PROJECT_PROPOSAL,
        )

    def test_proposal_with_opinion_preface_is_detected(self):
        self.assertEqual(
            classify_message("Ich finde, wir sollten die API austauschen."),
            Intent.PROJECT_PROPOSAL,
        )

    def test_qualified_wish_to_perform_a_technical_action_is_detected(self):
        self.assertEqual(
            classify_message("Ich möchte ein weiteres KI-Modell integrieren."),
            Intent.PROJECT_PROPOSAL,
        )

    def test_information_request_is_not_misclassified_as_a_proposal(self):
        self.assertEqual(
            classify_message("Ich möchte wissen, wie das Plugin funktioniert?"),
            Intent.QUESTION,
        )

    def test_question_is_detected(self):
        self.assertEqual(classify_message("Warum funktioniert das Plugin nicht?"), Intent.QUESTION)

    def test_empty_and_ambiguous_messages_are_safe(self):
        self.assertEqual(classify_message(""), Intent.UNKNOWN)
        self.assertEqual(classify_message("Interessant."), Intent.UNKNOWN)


if __name__ == "__main__":
    unittest.main()
