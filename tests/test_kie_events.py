import json
import socket
import socketserver
import threading

from critical_thinking.kie_events import publish_review_routed
from critical_thinking.models import Intent, ReviewLevel, ReviewRequest


class _CaptureServer(socketserver.ThreadingUnixStreamServer):
    daemon_threads = True


def test_publisher_sends_only_review_metadata_and_no_message_text(tmp_path):
    path = tmp_path / "kie.sock"
    received = []
    ready = threading.Event()

    class Handler(socketserver.StreamRequestHandler):
        def handle(self):
            received.append(json.loads(self.rfile.readline(65537)))
            self.wfile.write(b'{"ok":true}\n')
            self.wfile.flush()

    server = _CaptureServer(str(path), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        request = ReviewRequest(
            intent=Intent.PROJECT_PROPOSAL,
            level=ReviewLevel.CRITICAL,
            reason="private reason is deliberately omitted",
            user_requested=False,
            signals=("datenschutz", "integration"),
        )
        assert publish_review_routed(path, request) is True
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)

    message = received[0]
    assert message["engine_id"] == "critical_thinking"
    assert message["event_type"] == "critical_thinking.review_routed"
    assert message["payload"] == {
        "intent": "project_proposal",
        "review_level": "critical",
        "user_requested": False,
        "signals": ["datenschutz", "integration"],
    }
    assert "private reason" not in json.dumps(message)


def test_publisher_is_disabled_without_socket_path():
    request = ReviewRequest(Intent.QUESTION, ReviewLevel.NORMAL, "no review")
    assert publish_review_routed(None, request) is False


def test_publisher_fails_open_when_kie_socket_is_unavailable(tmp_path):
    request = ReviewRequest(Intent.FACTUAL_CLAIM, ReviewLevel.REVIEW, "technical claim")
    assert publish_review_routed(tmp_path / "missing.sock", request) is False


def test_normal_review_is_not_published(tmp_path):
    request = ReviewRequest(Intent.OPINION, ReviewLevel.NORMAL, "opinions are not challenged")
    assert publish_review_routed(tmp_path / "unused.sock", request) is False
