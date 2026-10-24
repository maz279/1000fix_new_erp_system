"""The OTP hand-off to the notification dispatcher (``otp_delivery``).

The transport is exercised against a real HTTP server bound to an ephemeral
loopback port (no external call); the rest with ``_post_json`` replaced.
"""

import json
import threading
import urllib.error
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, HTTPServer
from unittest.mock import patch

import pytest
from odoo.addons.cd_customer_portal.controllers import otp_delivery

PHONE = "01712345678"


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch):
    monkeypatch.delenv(otp_delivery.DISPATCHER_URL_ENV, raising=False)
    monkeypatch.delenv("FIX_ENV", raising=False)


@contextmanager
def _dispatcher(status=200, body=None, location=None):
    """A stand-in dispatcher on 127.0.0.1:<ephemeral>; yields (base_url, requests)."""
    received = []

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            length = int(self.headers.get("Content-Length", "0"))
            received.append(
                (self.path, self.headers.get("Content-Type"), json.loads(self.rfile.read(length)))
            )
            payload = json.dumps(body if body is not None else {}).encode()
            self.send_response(status)
            if location:
                self.send_header("Location", location)
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

        def log_message(self, *args):
            pass

    server = HTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_address[1]}", received
    finally:
        server.shutdown()
        server.server_close()


# --- endpoint configuration (DE-11) -------------------------------------------------


def test_default_endpoint_is_the_dispatchers_loopback_bind():
    assert otp_delivery.dispatcher_endpoint() == "http://127.0.0.1:8110/consume/once"


def test_configured_endpoint_is_normalised(monkeypatch):
    monkeypatch.setenv(otp_delivery.DISPATCHER_URL_ENV, " http://notification-dispatcher:8110/ ")
    assert otp_delivery.dispatcher_endpoint() == (
        "http://notification-dispatcher:8110/consume/once"
    )


@pytest.mark.parametrize(
    "url",
    [
        "ftp://127.0.0.1:8110",
        "http://",
        "http://user:pw@127.0.0.1:8110",
        "http://127.0.0.1:8110/?token=x",
        "http://127.0.0.1:8110/#frag",
    ],
)
def test_malformed_or_credential_bearing_urls_are_refused(monkeypatch, url):
    monkeypatch.setenv(otp_delivery.DISPATCHER_URL_ENV, url)
    with pytest.raises(otp_delivery.OtpDeliveryError):
        otp_delivery.dispatcher_endpoint()


def test_non_production_never_reaches_a_remote_host(monkeypatch):
    monkeypatch.setenv(otp_delivery.DISPATCHER_URL_ENV, "https://dispatcher.example.com")
    with pytest.raises(otp_delivery.OtpDeliveryError, match="DE-11"):
        otp_delivery.dispatcher_endpoint()
    monkeypatch.setenv("FIX_ENV", "staging")
    with pytest.raises(otp_delivery.OtpDeliveryError, match="DE-11"):
        otp_delivery.dispatcher_endpoint()
    monkeypatch.setenv("FIX_ENV", "production")
    assert otp_delivery.dispatcher_endpoint() == "https://dispatcher.example.com/consume/once"


# --- the event ------------------------------------------------------------------------


def test_otp_event_addresses_the_phone_with_the_nt007_variables():
    event = otp_delivery.otp_event(PHONE, "123456", 300, "en")
    payload = event["payload"]
    assert event["event_type"] == "security.otp_requested"
    assert payload["addresses"] == {"audience_any": "8801712345678"}
    assert payload["variables"] == {"code": "123456", "valid_minutes": 5}
    assert payload["recipients"] == [
        {"audience": "audience_any", "party_id": 0, "preferred_language": "en"}
    ]
    assert payload["event_time"] > 0


def test_otp_event_defaults_unknown_languages_to_bengali():
    payload = otp_delivery.otp_event(PHONE, "123456", 30, "fr")["payload"]
    assert payload["recipients"][0]["preferred_language"] == "bn"
    assert payload["variables"]["valid_minutes"] == 1  # never "0 minutes"


# --- the transport --------------------------------------------------------------------


def test_send_otp_posts_the_event_to_the_dispatcher(monkeypatch):
    accepted = {"decisions": [{"event": "security.otp_requested", "state": "delivered"}]}
    with _dispatcher(body=accepted) as (base, received):
        monkeypatch.setenv(otp_delivery.DISPATCHER_URL_ENV, base)
        otp_delivery.send_otp(PHONE, "654321", 300, "bn")
    [(path, content_type, event)] = received
    assert path == "/consume/once"
    assert content_type == "application/json"
    assert event["event_type"] == "security.otp_requested"
    assert event["payload"]["variables"]["code"] == "654321"


def test_a_dispatcher_redirect_is_refused_not_followed(monkeypatch):
    with _dispatcher(status=307, location="http://127.0.0.1:9/steal") as (base, received):
        monkeypatch.setenv(otp_delivery.DISPATCHER_URL_ENV, base)
        with pytest.raises(urllib.error.HTTPError):
            otp_delivery._post_json(base + "/consume/once", {"x": 1})
        with pytest.raises(otp_delivery.OtpDeliveryError, match="HTTPError"):
            otp_delivery.send_otp(PHONE, "654321", 300)
    assert len(received) == 2  # the redirect target was never contacted


def test_an_empty_answer_is_not_a_delivery(monkeypatch):
    with _dispatcher(body={}) as (base, _received):
        monkeypatch.setenv(otp_delivery.DISPATCHER_URL_ENV, base)
        with pytest.raises(otp_delivery.OtpDeliveryError, match="did not deliver"):
            otp_delivery.send_otp(PHONE, "654321", 300)


@pytest.mark.parametrize(
    "answer",
    [
        {"decisions": [{"state": "dead", "reason": "all channels failed"}]},
        {"decisions": [{"state": "suppressed"}, "junk"]},
        {"decisions": None},
        ["not", "a", "dict"],
    ],
)
def test_undelivered_decisions_raise_without_the_code(answer):
    with (
        patch.object(otp_delivery, "_post_json", return_value=answer),
        pytest.raises(otp_delivery.OtpDeliveryError) as err,
    ):
        otp_delivery.send_otp(PHONE, "987654", 300)
    assert "987654" not in str(err.value)


@pytest.mark.parametrize(
    "failure",
    [urllib.error.URLError("refused"), TimeoutError(), OSError("reset"), ValueError("bad json")],
)
def test_transport_failures_raise_a_delivery_error(failure):
    with (
        patch.object(otp_delivery, "_post_json", side_effect=failure),
        pytest.raises(otp_delivery.OtpDeliveryError, match="unreachable") as err,
    ):
        otp_delivery.send_otp(PHONE, "987654", 300)
    assert err.value.__cause__ is None  # the request (with the code) is not chained
    assert "987654" not in str(err.value)


def test_an_unreachable_dispatcher_is_a_delivery_error(monkeypatch):
    with _dispatcher() as (base, _received):
        pass  # server closed: the port refuses connections now
    monkeypatch.setenv(otp_delivery.DISPATCHER_URL_ENV, base)
    with pytest.raises(otp_delivery.OtpDeliveryError, match="unreachable"):
        otp_delivery.send_otp(PHONE, "654321", 300)
