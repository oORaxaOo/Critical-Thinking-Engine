"""Hermes integration. The hook is deliberately cheap and fail-open."""

import logging

from .classifier import classify_message
from .policy import choose_review_level, should_inject_review
from .prompt_builder import build_review_context
from .kie_events import publish_hook_failure, publish_review_routed

logger = logging.getLogger(__name__)


def before_llm_call(**kwargs):
    """Inject bounded review guidance for relevant turns only."""
    event_publisher = kwargs.pop("_kie_event_publisher", None)
    failure_publisher = kwargs.pop("_kie_failure_publisher", None)
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
        if callable(event_publisher):
            try:
                event_publisher(request)
            except Exception as exc:
                logger.warning("KIE event publication failed (%s); continuing without ingress", type(exc).__name__)
        return {"context": context}
    except Exception:
        # The CTE must never prevent Hermes from answering.
        logger.exception("Critical Thinking Engine hook failed; continuing without review context")
        if callable(failure_publisher):
            try:
                failure_publisher()
            except Exception:
                logger.debug("KIE CTE failure event could not be published", exc_info=True)
        return None


def register(ctx):
    """Register the CTE hook and optional metadata-only KIE publisher."""
    try:
        socket_path = ctx.get_config("kie_event_socket", default=None)
    except Exception:
        socket_path = None

    def hook(**kwargs):
        return before_llm_call(
            **kwargs,
            _kie_event_publisher=lambda request: publish_review_routed(socket_path, request),
            _kie_failure_publisher=lambda: publish_hook_failure(socket_path),
        )

    ctx.register_hook("pre_llm_call", hook)
