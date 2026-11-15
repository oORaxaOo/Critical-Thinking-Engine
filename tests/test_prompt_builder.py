import unittest

from critical_thinking.models import Intent, ReviewLevel, ReviewRequest
from critical_thinking.prompt_builder import build_review_context


class PromptBuilderTests(unittest.TestCase):
    def test_review_context_requires_a_clear_position_and_alternative(self):
        request = ReviewRequest(Intent.PROJECT_PROPOSAL, ReviewLevel.REVIEW, "test")
        prompt = build_review_context(request)
        self.assertIn("SUPPORT, CHANGE, REJECT", prompt)
        self.assertIn("practical better alternative", prompt)
        self.assertIn("Do not agree merely", prompt)

    def test_normal_level_has_no_context(self):
        request = ReviewRequest(Intent.UNKNOWN, ReviewLevel.NORMAL, "none")
        self.assertEqual(build_review_context(request), "")


if __name__ == "__main__":
    unittest.main()
