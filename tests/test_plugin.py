import importlib.util
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch

from critical_thinking.plugin import before_llm_call, register


class FakeContext:
    def __init__(self):
        self.hooks = {}

    def register_hook(self, name, callback):
        self.hooks[name] = callback

    def get_config(self, key, default=None):
        return default


class PluginTests(unittest.TestCase):
    def test_registers_only_pre_llm_hook(self):
        ctx = FakeContext()
        register(ctx)
        self.assertEqual(set(ctx.hooks), {"pre_llm_call"})
        self.assertTrue(callable(ctx.hooks["pre_llm_call"]))
        self.assertIsNot(ctx.hooks["pre_llm_call"], before_llm_call)

    def test_hermes_v0231_pre_llm_payload_injects_ephemeral_context(self):
        # Hermes v0.23.1 documents these fields for pre_llm_call.
        result = before_llm_call(
            session_id="test-session",
            user_message="Wir sollten ein Hermes-Plugin bauen.",
            conversation_history=[],
            is_first_turn=True,
            model="test-model",
            platform="cli",
        )
        self.assertEqual(set(result), {"context"})
        self.assertIn("REVIEW", result["context"])
        self.assertIn("technical proposal or decision", result["context"])

    def test_personal_message_does_not_inject_critique(self):
        self.assertIsNone(before_llm_call(user_message="Ich bin traurig."))

    def test_technical_proposal_injects_review_guidance(self):
        result = before_llm_call(user_message="Wir sollten ein Hermes-Plugin bauen.")
        self.assertIsInstance(result, dict)
        self.assertIn("context", result)
        self.assertIn("REVIEW", result["context"])

    def test_hedged_technical_proposal_still_gets_review_guidance(self):
        result = before_llm_call(
            user_message="Ich glaube, wir sollten ein weiteres KI-Modell integrieren."
        )
        self.assertIsInstance(result, dict)
        self.assertIn("REVIEW", result["context"])

    def test_information_request_does_not_inject_project_review(self):
        self.assertIsNone(
            before_llm_call(user_message="Ich möchte wissen, wie das Plugin funktioniert?")
        )

    def test_technical_factual_claim_gets_evidence_guidance(self):
        result = before_llm_call(user_message="Das Hermes-Plugin funktioniert garantiert.")
        self.assertIsInstance(result, dict)
        self.assertIn("technical factual claim", result["context"])

    def test_hook_fails_open_when_internal_logic_raises(self):
        with patch("critical_thinking.plugin.classify_message", side_effect=RuntimeError("test")):
            self.assertIsNone(before_llm_call(user_message="Wir sollten ein Plugin bauen."))

    def test_empty_message_fails_open(self):
        self.assertIsNone(before_llm_call(user_message=""))


class HermesLoaderImportTests(unittest.TestCase):
    def test_package_relative_import_matches_hermes_loader_contract(self):
        plugin_dir = Path(__file__).resolve().parents[1]
        parent_name = "hermes_plugins"
        module_name = "hermes_plugins.critical_thinking_engine"

        namespace = sys.modules.get(parent_name)
        if namespace is None:
            namespace = types.ModuleType(parent_name)
            namespace.__path__ = []
            namespace.__package__ = parent_name
            sys.modules[parent_name] = namespace

        spec = importlib.util.spec_from_file_location(
            module_name,
            plugin_dir / "__init__.py",
            submodule_search_locations=[str(plugin_dir)],
        )
        self.assertIsNotNone(spec)
        module = importlib.util.module_from_spec(spec)
        module.__package__ = module_name
        module.__path__ = [str(plugin_dir)]
        sys.modules[module_name] = module
        try:
            spec.loader.exec_module(module)
            self.assertTrue(callable(module.register))
            ctx = FakeContext()
            module.register(ctx)
            self.assertIn("pre_llm_call", ctx.hooks)
        finally:
            for name in list(sys.modules):
                if name == module_name or name.startswith(module_name + "."):
                    sys.modules.pop(name, None)


if __name__ == "__main__":
    unittest.main()
