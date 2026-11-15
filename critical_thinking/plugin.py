"""Hermes integration. The hook is deliberately cheap and fail-open."""

import logging

from .classifier import classify_message
from .policy import choose_review_level, should_inject_review
from .prompt_builder import build_review_context

logger = logging.getLogger(__name__)


def before_llm_call(**kwargs):
    """Inject bounded review guidance for relevant turns only."""
    try:
        message = kwargs.get("user_message", "")
        if not isinstance(message, str) or not message.strip():
            return None

        intent = classify_message(message)
        request = choose_review_level(message, intent)
        if not should_inject_review(request):
            return None

        context = build_review_context(request)
        if not context:
            return None
        return {"context": context}
    except Exception:
        # The CTE must never prevent Hermes from answering.
        logger.exception("Critical Thinking Engine hook failed; continuing without review context")
        return None


def register(ctx):
    """Register the CTE's single dynamic per-turn hook."""
    ctx.register_hook("pre_llm_call", before_llm_call)
