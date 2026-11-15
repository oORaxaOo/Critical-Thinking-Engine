import unittest

from critical_thinking.plugin import before_llm_call, register


class FakeContext:
    def __init__(self):
        self.hooks = {}

    def register_hook(self, name, callback):
        self.hooks[name] = callback


class PluginTests(unittest.TestCase):
    def test_registers_only_pre_llm_hook(self):
        ctx = FakeContext()
        register(ctx)
        self.assertEqual(set(ctx.hooks), {"pre_llm_call"})
        self.assertIs(ctx.hooks["pre_llm_call"], before_llm_call)

    def test_personal_message_does_not_inject_critique(self):
        self.assertIsNone(before_llm_call(user_message="Ich bin traurig."))

    def test_technical_proposal_injects_review_guidance(self):
        result = before_llm_call(user_message="Wir sollten ein Hermes-Plugin bauen.")
        self.assertIsInstance(result, dict)
        self.assertIn("context", result)
        self.assertIn("REVIEW", result["context"])

    def test_empty_message_fails_open(self):
        self.assertIsNone(before_llm_call(user_message=""))


if __name__ == "__main__":
    unittest.main()
