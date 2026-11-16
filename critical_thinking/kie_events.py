"""Privacy-bounded publisher for KIE review-routing metadata."""
from __future__ import annotations

import json
from pathlib import Path
import socket
from typing import Any
from uuid import uuid4

_MAX_MESSAGE_BYTES = 64 * 1024


def _send(socket_path: str | Path | None, payload: dict[str, Any]) -> bool:
    """Send one small event to KIE; a missing receiver never blocks CTE."""
    if not isinstance(socket_path, (str, Path)) or not str(socket_path).strip():
        return False
    path = Path(socket_path).expanduser()
    if not path.is_absolute():
        return False
    message = {
        "event_id": str(uuid4()),
        "engine_id": "critical_thinking",
        "event_type": "critical_thinking.review_routed",
        "payload": payload,
    }
    try:
        encoded = json.dumps(message, ensure_ascii=False, allow_nan=False, separators=(",", ":")).encode("utf-8")
        if len(encoded) > _MAX_MESSAGE_BYTES:
            return False
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
            client.settimeout(0.15)
            client.connect(str(path))
            client.sendall(encoded + b"\n")
            response = client.makefile("rb").readline(1024)
        return json.loads(response.decode("utf-8")).get("ok") is True
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        return False


def publish_review_routed(socket_path: str | Path | None, request: Any) -> bool:
    """Publish only CTE classification metadata, never the original message."""
    try:
        payload = {
            "intent": request.intent.value,
            "review_level": request.level.value,
            "user_requested": bool(request.user_requested),
            "signals": list(request.signals[:8]),
        }
        if payload["review_level"] not in {"review", "critical"}:
            return False
        return _send(socket_path, payload)
    except (AttributeError, TypeError, ValueError):
        return False


__all__ = ["publish_review_routed"]
