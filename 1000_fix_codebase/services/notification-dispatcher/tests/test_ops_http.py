"""Operations HTTP surface tests — src/main.py (/health /kpis /dlq /fallbacks
and POST /consume/once).

main.py is an entrypoint with a generic basename, so it is loaded under the
unique module name ``notification_dispatcher_main`` (its own
``from src.… import`` lines resolve to this service's ``src`` package).
Requests are driven through the real ``BaseHTTPRequestHandler`` parser over an
in-memory socket double — no port is bound and nothing touches the network;
``serve()`` runs against a fake ``HTTPServer``.
"""

from __future__ import annotations

import importlib.util
import io
import json
import sys
from pathlib import Path
from types import ModuleType

import pytest

SERVICE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SERVICE_DIR))

from src.delivery import FALLBACK_REGISTER
from src.dispatcher import Dispatcher, load_registry

MAIN_PATH = SERVICE_DIR / "src" / "main.py"
MODULE_NAME = "notification_dispatcher_main"
REGISTRY = load_registry()


def load_main(monkeypatch: pytest.MonkeyPatch) -> ModuleType:
    """Execute main.py afresh (module-level config is read at import)."""
    spec = importlib.util.spec_from_file_location(MODULE_NAME, MAIN_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, MODULE_NAME, module)
    saved_path = list(sys.path)
    try:
        spec.loader.exec_module(module)
    finally:
        sys.path[:] = saved_path  # main.py prepends libs/py; keep sys.path as it was
    return module


@pytest.fixture
def main(monkeypatch: pytest.MonkeyPatch) -> ModuleType:
    return load_main(monkeypatch)


class FakeSocket:
    """Just enough of a socket for StreamRequestHandler: reads the raw
    request from memory and collects everything written back."""

    def __init__(self, raw: bytes) -> None:
        self._incoming = io.BytesIO(raw)
        self.sent = bytearray()

    def makefile(self, mode: str, bufsize: int = -1) -> io.BytesIO:
        return self._incoming

    def sendall(self, data: bytes) -> None:
        self.sent += data


def call(
    main: ModuleType,
    dispatcher: Dispatcher,
    method: str,
    path: str,
    body: bytes | None = None,
    content_length: str | None = None,
):
    """Send one HTTP/1.0 request through main.Handler; returns
    (status, headers, raw body). ``content_length`` overrides the header."""
    head = f"{method} {path} HTTP/1.0\r\n"
    if body is not None:
        length = len(body) if content_length is None else content_length
        head += f"Content-Length: {length}\r\n"
    raw = head.encode("ascii") + b"\r\n" + (body or b"")
    main.Handler.dispatcher = dispatcher  # what serve() injects
    sock = FakeSocket(raw)
    main.Handler(sock, ("127.0.0.1", 50123), None)
    response_head, _, response_body = bytes(sock.sent).partition(b"\r\n\r\n")
    status_line, *header_lines = response_head.decode("latin-1").split("\r\n")
    headers = dict(line.split(": ", 1) for line in header_lines)
    return int(status_line.split()[1]), headers, response_body


def call_json(main, dispatcher, method, path, body=None, content_length=None):
    status, headers, raw = call(main, dispatcher, method, path, body, content_length)
    assert headers["Content-Type"] == "application/json; charset=utf-8"
    assert int(headers["Content-Length"]) == len(raw)
    return status, json.loads(raw.decode("utf-8"))


@pytest.fixture
def dispatcher() -> Dispatcher:
    return Dispatcher(registry=REGISTRY)


# --------------------------------------------------------- module config


class TestModuleConfig:
    def test_defaults(self, main):
        assert main.HOST == "127.0.0.1"
        assert main.PORT == 8110

    def test_port_from_environment(self, monkeypatch):
        monkeypatch.setenv("FIX_NOTIFICATION_DISPATCHER_PORT", "9123")
        assert load_main(monkeypatch).PORT == 9123

    def test_import_leaves_sys_path_and_src_package_untouched(self, monkeypatch):
        before = list(sys.path)
        src_package = sys.modules["src"]
        load_main(monkeypatch)
        assert sys.path == before
        assert sys.modules["src"] is src_package

    def test_build_dispatcher_defaults_to_wave_1(self, main):
        built = main.build_dispatcher()
        assert isinstance(built, Dispatcher)
        assert built.router.active_wave == "W1"
        assert set(built.rules) == {"security", "transactional", "service", "marketing"}

    def test_build_dispatcher_honours_active_wave(self, main, monkeypatch):
        monkeypatch.setenv("FIX_ACTIVE_WAVE", "W2")
        assert main.build_dispatcher().router.active_wave == "W2"


# ------------------------------------------------------------- GET routes


class TestGetRoutes:
    def test_health(self, main, dispatcher, capsys):
        status, body = call_json(main, dispatcher, "GET", "/health")
        assert status == 200
        assert body == {
            "status": "UP",
            "module": "M27",
            "cd": "CD-M27-nn",
            "wave": "W1",
            "consent_classes": ["marketing", "security", "service", "transactional"],
            "events": 27,
            "dry_run_default": True,
        }
        # Access log goes through the service-prefixed log_message override.
        assert 'notification-dispatcher: "GET /health HTTP/1.0" 200 -' in capsys.readouterr().out

    def test_regression_health_counts_events_not_documentation_keys(self, main, dispatcher):
        """Regression: /health reported len(event_matrix), which counts the
        registry's "comment" string as an event (28 instead of 27)."""
        rows = REGISTRY["event_matrix"]
        assert len(rows) == 28
        assert "comment" in rows
        _, body = call_json(main, dispatcher, "GET", "/health")
        assert body["events"] == sum(isinstance(row, dict) for row in rows.values()) == 27

    def test_kpis_mirror_the_dispatcher_snapshot(self, main, dispatcher):
        dispatcher.handle({"event_type": "not.an.event", "payload": {}})
        status, body = call_json(main, dispatcher, "GET", "/kpis")
        assert status == 200
        assert body == dispatcher.kpi_snapshot()
        assert body["counts"]["dead"] == 1

    def test_dlq_lists_dead_letters(self, main, dispatcher):
        status, body = call_json(main, dispatcher, "GET", "/dlq")
        assert (status, body) == (200, {"count": 0, "records": []})
        dispatcher.handle({"event_type": "not.an.event", "payload": {}})
        dead = dispatcher.tracker.dead_letters[0]
        status, body = call_json(main, dispatcher, "GET", "/dlq")
        assert body == {
            "count": 1,
            "records": [{"id": dead.id, "event": "not.an.event", "party_id": 0, "state": "dead"}],
        }

    def test_fallback_register_is_served_as_utf8(self, main, dispatcher):
        status, body = call_json(main, dispatcher, "GET", "/fallbacks")
        assert status == 200
        assert body == FALLBACK_REGISTER
        _, _, raw = call(main, dispatcher, "GET", "/fallbacks")
        assert "→".encode() in raw  # ensure_ascii=False: no \u escapes

    def test_unknown_get_path_is_404(self, main, dispatcher):
        assert call_json(main, dispatcher, "GET", "/admin") == (404, {"error": "not found"})


# ------------------------------------------------------------ POST route


class TestConsumeOnce:
    def test_unknown_post_path_is_404(self, main, dispatcher):
        status, body = call_json(main, dispatcher, "POST", "/consume/all", b"{}")
        assert (status, body) == (404, {"error": "not found"})
        assert dispatcher.tracker.records == []

    def test_invalid_json_is_400_and_nothing_is_dispatched(self, main, dispatcher):
        status, body = call_json(main, dispatcher, "POST", "/consume/once", b"{not json")
        assert (status, body) == (400, {"error": "invalid json"})
        assert dispatcher.tracker.records == []

    def test_event_is_dispatched_and_decisions_returned(self, main, dispatcher):
        event = {
            "event_type": "service.order.ready_for_collection",
            "payload": {
                "recipients": [{"audience": "customer", "party_id": 7}],
                "addresses": {"customer": "8801700000000"},
            },
        }
        status, body = call_json(
            main, dispatcher, "POST", "/consume/once", json.dumps(event).encode()
        )
        assert status == 200
        assert body["decisions"] == [
            {
                "event": "service.order.ready_for_collection",
                "party_id": 7,
                "state": "delivered",
                "reason": "sent:sms:dry-run",  # conftest leaves every gateway unconfigured
            }
        ]
        assert body["kpis"]["counts"]["delivered"] == 1

    def test_missing_body_is_treated_as_an_empty_event(self, main, dispatcher):
        status, body = call_json(main, dispatcher, "POST", "/consume/once")
        assert status == 200
        assert body["decisions"] == [
            {"event": "", "state": "dead", "reason": "event '' is not in the NT-001 matrix"}
        ]

    @pytest.mark.parametrize("raw", [b"[1, 2]", b'"event"', b"null", b"7"])
    def test_regression_non_object_json_is_400(self, main, dispatcher, raw):
        """Regression: valid JSON that is not an object reached
        Dispatcher.handle() and crashed it (no response) instead of a 400."""
        status, body = call_json(main, dispatcher, "POST", "/consume/once", raw)
        assert (status, body) == (400, {"error": "event must be a JSON object"})
        assert dispatcher.tracker.records == []

    def test_regression_undecodable_body_is_400(self, main, dispatcher):
        """Regression: a body that is not UTF-8 raised UnicodeDecodeError,
        which the JSONDecodeError handler did not catch."""
        status, body = call_json(main, dispatcher, "POST", "/consume/once", b'{"a": "\x80"}')
        assert (status, body) == (400, {"error": "invalid json"})

    @pytest.mark.parametrize("length", ["abc", "-1", "1e3"])
    def test_regression_bad_content_length_is_400(self, main, dispatcher, length):
        """Regression: a non-integer Content-Length raised ValueError (no
        response); a negative one made the handler read until EOF, which on a
        live socket blocks the single-threaded server."""
        status, body = call_json(main, dispatcher, "POST", "/consume/once", b"{}", length)
        assert (status, body) == (400, {"error": "invalid content-length"})
        assert dispatcher.tracker.records == []


# ----------------------------------------------------------------- serve


def test_serve_binds_loopback_and_injects_the_dispatcher(main, monkeypatch, capsys):
    servers: list[FakeServer] = []

    class FakeServer:
        def __init__(self, address, handler):
            self.address, self.handler, self.served = address, handler, False
            servers.append(self)

        def serve_forever(self):
            self.served = True

    monkeypatch.setenv("FIX_ACTIVE_WAVE", "W2")
    monkeypatch.setattr(main, "HTTPServer", FakeServer)
    main.serve()
    (server,) = servers
    assert server.address == ("127.0.0.1", 8110)
    assert server.handler is main.Handler
    assert server.served is True
    assert isinstance(main.Handler.dispatcher, Dispatcher)
    assert main.Handler.dispatcher.router.active_wave == "W2"
    assert "listening on 127.0.0.1:8110 (dry-run default" in capsys.readouterr().out
