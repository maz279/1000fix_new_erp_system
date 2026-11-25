"""rmm-collector JSON-RPC client, alert push and CLI (P08-M07-T04).

urllib.request.urlopen is replaced by an in-memory fake: no network.
"""

from __future__ import annotations

import datetime as dt
import json
import sys
import types
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import rmm_collector
from rmm_collector import AlertDecision, OdooClient, push_alert


class _FakeResponse:
    def __init__(self, body: dict, set_cookie: str = ""):
        self._body = json.dumps(body).encode()
        self.headers = {"Set-Cookie": set_cookie} if set_cookie else {}

    def read(self):
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


@pytest.fixture
def transport(monkeypatch):
    """Queue of canned responses + a log of the requests sent."""
    state = {"responses": [], "requests": []}

    def fake_urlopen(req, timeout):
        state["requests"].append({"req": req, "timeout": timeout, "body": json.loads(req.data)})
        return state["responses"].pop(0)

    monkeypatch.setattr(rmm_collector.urllib.request, "urlopen", fake_urlopen)
    return state


def test_login_posts_credentials_and_captures_session_cookie(transport):
    transport["responses"].append(
        _FakeResponse({"result": {"uid": 2}}, set_cookie="session_id=abc123; Path=/; HttpOnly")
    )
    client = OdooClient()
    client.login("fixdb", "admin", "test-pass")

    sent = transport["requests"][0]
    assert sent["req"].full_url == "http://127.0.0.1:8069/web/session/authenticate"
    assert sent["req"].get_header("Content-type") == "application/json"
    assert sent["req"].get_header("Cookie") is None  # no session yet
    assert sent["timeout"] == 60
    assert sent["body"] == {"params": {"db": "fixdb", "login": "admin", "password": "test-pass"}}
    assert client.cookie == "session_id=abc123"


def test_call_reuses_cookie_and_returns_result(transport):
    transport["responses"].append(_FakeResponse({"result": [1, 2, 3]}))
    client = OdooClient(base="http://localhost:8069")
    client.cookie = "session_id=abc123"

    out = client.call("fix.monitored.asset", "search", [["active", "=", True]], limit=3)

    assert out == [1, 2, 3]
    sent = transport["requests"][0]
    assert sent["req"].full_url == "http://localhost:8069/web/dataset/call_kw"
    assert sent["req"].get_header("Cookie") == "session_id=abc123"
    assert sent["body"] == {
        "params": {
            "model": "fix.monitored.asset",
            "method": "search",
            "args": [[["active", "=", True]]],
            "kwargs": {"limit": 3},
        }
    }
    assert client.cookie == "session_id=abc123"  # no Set-Cookie -> unchanged


def test_call_without_result_key_returns_none(transport):
    transport["responses"].append(_FakeResponse({"jsonrpc": "2.0"}))
    assert OdooClient().call("m", "noop") is None


def test_login_error_raises_with_server_message(transport):
    transport["responses"].append(_FakeResponse({"error": {"data": {"message": "Access Denied"}}}))
    with pytest.raises(RuntimeError, match="Access Denied"):
        OdooClient().login("fixdb", "admin", "wrong")


def test_call_error_with_message(transport):
    transport["responses"].append(
        _FakeResponse({"error": {"data": {"message": "Record does not exist"}}})
    )
    with pytest.raises(RuntimeError, match="Record does not exist"):
        OdooClient().call("m", "read", 99)


def test_call_error_without_message_uses_generic_text(transport):
    transport["responses"].append(_FakeResponse({"error": {"data": {}}}))
    with pytest.raises(RuntimeError, match="rpc error"):
        OdooClient().call("m", "read", 99)


def test_non_local_base_is_refused_before_any_request(transport):
    client = OdooClient(base="http://odoo.example.com:8069")
    with pytest.raises(ValueError, match="refusing non-local endpoint"):
        client.call("m", "read")
    assert transport["requests"] == []


class _RecordingClient:
    def __init__(self):
        self.calls = []

    def call(self, model, method, *args, **kw):
        self.calls.append((model, method, args, kw))


@pytest.mark.parametrize(("severity", "health"), [("major", "offline"), ("minor", "degraded")])
def test_push_alert_ingests_telemetry_with_utc_second_timestamp(monkeypatch, severity, health):
    monkeypatch.setattr(rmm_collector, "time", types.SimpleNamespace(time=lambda: 1_700_000_000.75))
    client = _RecordingClient()

    assert push_alert(client, AlertDecision("AGT-7", severity, "msg")) == 0

    assert client.calls == [
        (
            "fix.monitored.asset",
            "ingest_telemetry",
            ("AGT-7", health, dt.datetime(2023, 11, 14, 22, 13, 20)),
            {},
        )
    ]
    seen_at = client.calls[0][2][2]
    assert seen_at.tzinfo is None
    assert seen_at.microsecond == 0


def test_main_prints_usage_and_returns_zero(capsys):
    assert rmm_collector.main() == 0
    assert "rmm-collector: evaluation library + HTTP push" in capsys.readouterr().out
