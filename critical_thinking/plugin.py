"""Hermes integration. The hook is deliberately cheap and fail-open."""

import logging
from pathlib import Path
from typing import Any, Callable

from .classifier import classify_message
from .policy import choose_review_level, should_inject_review
from .prompt_builder import build_review_context

logger = logging.getLogger(__name__)


def before_llm_call(
    *,
    kie_publisher: Callable[..., Any] | None = None,
    **kwargs: Any,
):
    """Inject bounded review guidance and optionally publish metadata to KIE."""
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

        if kie_publisher is not None:
            try:
                kie_publisher(
                    intent=request.intent.value,
                    review_level=request.level.value,
                    reason=request.reason,
                    signals=request.signals,
                    user_requested=request.user_requested,
                    context_injected=True,
                )
            except Exception as exc:
                # Publishing is optional; KIE failures never block the CTE hook.
                logger.warning("KIE review publication unavailable (%s)", type(exc).__name__)

        return {"context": context}
    except Exception:
        # The CTE must never prevent Hermes from answering.
        logger.exception("Critical Thinking Engine hook failed; continuing without review context")
        return None


def _configured_publisher(ctx: Any) -> Callable[..., Any] | None:
    getter = getattr(ctx, "get_config", None)
    if not callable(getter):
        return None
    try:
        database = getter("kie_database", default=None)
    except Exception:
        return None
    if not isinstance(database, str) or not database.strip():
        return None
    if not Path(database).expanduser().is_absolute():
        logger.warning("CTE KIE publication disabled: kie_database must be an absolute path")
        return None

    try:
        from kie.publisher import publish_critical_thinking_review
    except ImportError:
        logger.warning("CTE KIE publication disabled: KIE publisher is not installed")
        return None

    def publish(**metadata: Any) -> Any:
        return publish_critical_thinking_review(database, **metadata)

    return publish


def register(ctx):
    """Register the CTE's single dynamic per-turn hook."""
    publisher = _configured_publisher(ctx)
    if publisher is None:
        ctx.register_hook("pre_llm_call", before_llm_call)
        return

    def hook(**kwargs: Any):
        return before_llm_call(kie_publisher=publisher, **kwargs)

    ctx.register_hook("pre_llm_call", hook)
