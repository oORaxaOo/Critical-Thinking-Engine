import json
import socketserver
import tempfile
import threading
import unittest
from pathlib import Path

from critical_thinking.kie_events import publish_review_routed
from critical_thinking.models import Intent, ReviewLevel, ReviewRequest


class _CaptureServer(socketserver.ThreadingUnixStreamServer):
    daemon_threads = True


class KIEEventPublisherTests(unittest.TestCase):
    def setUp(self):
        self._temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self._temporary.cleanup)
        self.root = Path(self._temporary.name)
        self.socket_path = self.root / "kie.sock"
        self.received = []

    def _capture(self, callback):
        class Handler(socketserver.StreamRequestHandler):
            def handle(inner_self):
                self.received.append(json.loads(inner_self.rfile.readline(65537)))
                inner_self.wfile.write(b'{"ok":true}\n')
                inner_self.wfile.flush()

        server = _CaptureServer(str(self.socket_path), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            self.assertTrue(callback(self.socket_path))
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)
        return self.received[0]

    def test_publisher_sends_only_review_metadata_and_no_message_text(self):
        request = ReviewRequest(
            intent=Intent.PROJECT_PROPOSAL,
            level=ReviewLevel.CRITICAL,
            reason="private reason is deliberately omitted",
            user_requested=False,
            signals=("datenschutz", "security"),
        )
        message = self._capture(lambda path: publish_review_routed(path, request))

        self.assertEqual(message["engine_id"], "critical_thinking")
        self.assertEqual(message["event_type"], "critical_thinking.review_routed")
        self.assertEqual(message["payload"], {
            "intent": "project_proposal",
            "review_level": "critical",
            "user_requested": False,
            "signals": ["datenschutz", "security"],
        })
        self.assertNotIn("private reason", json.dumps(message))

    def test_publisher_is_disabled_without_socket_path(self):
        request = ReviewRequest(Intent.QUESTION, ReviewLevel.NORMAL, "no review")
        self.assertFalse(publish_review_routed(None, request))

    def test_publisher_fails_open_when_kie_socket_is_unavailable(self):
        request = ReviewRequest(Intent.FACTUAL_CLAIM, ReviewLevel.REVIEW, "technical claim")
        self.assertFalse(publish_review_routed(self.root / "missing.sock", request))

    def test_normal_review_is_not_published(self):
        request = ReviewRequest(Intent.OPINION, ReviewLevel.NORMAL, "opinions are not challenged")
        self.assertFalse(publish_review_routed(self.socket_path, request))


if __name__ == "__main__":
    unittest.main()
