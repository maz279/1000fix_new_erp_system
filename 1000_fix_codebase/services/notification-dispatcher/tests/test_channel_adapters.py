"""Channel adapter tests — INT-010/011 SMS, INT-012 WhatsApp, INT-013 email,
Novu push, NT-018 in-app, NT-021 alert (P04-M05-T03…T05).

No packet leaves the process: the adapters' gateway opener
(``channels._OPENER.open``) is replaced by a recording stub — or, for the
redirect tests, ``http.client.HTTPConnection`` beneath it is scripted — and
DNS (``socket.getaddrinfo``) is faked for the production SSRF guard. The
conftest clears every gateway env var, so each adapter starts in its dry-run
default.
"""

from __future__ import annotations

import http.client
import io
import json
import socket
import sys
import urllib.error
import urllib.request
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src import channels
from src.channels import (
    CHANNELS,
    AlertChannel,
    EmailChannel,
    InAppChannel,
    PushChannel,
    SendRefused,
    SMSChannel,
    WhatsAppChannel,
    _host_is_rejected_in_production,
    _validate_outbound_url,
    build_channels,
)

PRIMARY_SMS_URL = "http://localhost:9001/sms"
REDUNDANT_SMS_URL = "http://localhost:9002/sms-backup"
MSISDN = "8801700000000"


class _FakeResponse:
    def __init__(self, body: bytes) -> None:
        self._body = body

    def read(self) -> bytes:
        return self._body

    def __enter__(self) -> _FakeResponse:
        return self

    def __exit__(self, *exc_info: object) -> bool:
        return False


class GatewayStub:
    """Stands in for the gateway opener: records every request; answers per URL with
    a canned body, or raises the canned transport error for that URL."""

    def __init__(self) -> None:
        self.routes: dict[str, bytes | BaseException] = {}
        self.requests: list[tuple[urllib.request.Request, float | None]] = []

    def __call__(self, request: urllib.request.Request, timeout: float | None = None):
        self.requests.append((request, timeout))
        outcome = self.routes.get(request.full_url, b'{"id": "GW-1"}')
        if isinstance(outcome, BaseException):
            raise outcome
        return _FakeResponse(outcome)

    def urls(self) -> list[str]:
        return [request.full_url for request, _ in self.requests]

    def payload(self, index: int = -1) -> dict:
        return json.loads(self.requests[index][0].data)

    def header(self, name: str, index: int = -1) -> str | None:
        return self.requests[index][0].get_header(name)


@pytest.fixture
def gateway(monkeypatch: pytest.MonkeyPatch) -> GatewayStub:
    stub = GatewayStub()
    monkeypatch.setattr(channels._OPENER, "open", stub)
    return stub


@pytest.fixture
def production(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FIX_ENV", "production")


def resolve_to(monkeypatch: pytest.MonkeyPatch, *addresses: str) -> list[str]:
    """Fake DNS: every lookup answers with ``addresses``; returns the log of
    hosts looked up."""
    looked_up: list[str] = []

    def fake_getaddrinfo(host, port, *args, **kwargs):
        looked_up.append(host)
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", (addr, 0)) for addr in addresses]

    monkeypatch.setattr(socket, "getaddrinfo", fake_getaddrinfo)
    return looked_up


# ------------------------------------------------------------ SSRF guard


class TestLocalUrlPolicy:
    def test_allowlisted_compose_url_is_returned_unchanged(self):
        url = "http://mailpit:8025/api/v1/send?batch=1"
        assert _validate_outbound_url(url, "FIX_EMAIL_API_URL") == url

    def test_non_http_scheme_refused(self):
        with pytest.raises(SendRefused, match="scheme 'ftp' not allowed"):
            _validate_outbound_url("ftp://localhost/drop", "FIX_SMS_GATEWAY_URL")

    def test_host_outside_allowlist_names_the_environment(self, monkeypatch):
        # Every non-production environment (staging included) is jailed.
        monkeypatch.setenv("FIX_ENV", "staging")
        with pytest.raises(SendRefused, match=r"outside the local allowlist \(FIX_ENV=staging\)"):
            _validate_outbound_url("http://gateway.example.com/send", "FIX_SMS_GATEWAY_URL")

    def test_userinfo_in_url_refused(self):
        with pytest.raises(SendRefused, match="credentials must not be embedded"):
            _validate_outbound_url("http://svc-account@localhost/send", "FIX_SMS_GATEWAY_URL")

    @pytest.mark.parametrize(
        "key", ["token", "apikey", "api_key", "access_token", "signature", "secret", "API_KEY"]
    )
    def test_credential_like_query_parameter_refused(self, key):
        with pytest.raises(SendRefused, match="credential-like query parameter refused"):
            _validate_outbound_url(f"http://localhost/send?ok=1&{key}=x", "FIX_SMS_GATEWAY_URL")


class TestProductionUrlPolicy:
    @pytest.mark.usefixtures("production")
    def test_plain_http_refused_in_production(self, monkeypatch):
        looked_up = resolve_to(monkeypatch, "8.8.8.8")
        with pytest.raises(SendRefused, match="production gateways must be https, got http"):
            _validate_outbound_url("http://gw.example.com/send", "FIX_SMS_GATEWAY_URL")
        assert looked_up == []  # refused before any DNS lookup

    @pytest.mark.usefixtures("production")
    def test_public_https_gateway_accepted(self, monkeypatch):
        looked_up = resolve_to(monkeypatch, "8.8.8.8")
        url = "https://GW.Example.com/send"
        assert _validate_outbound_url(url, "FIX_SMS_GATEWAY_URL") == url
        assert looked_up == ["gw.example.com"]  # host is lower-cased before the lookup

    @pytest.mark.usefixtures("production")
    def test_unresolvable_host_refused(self, monkeypatch):
        def no_such_host(*args, **kwargs):
            raise socket.gaierror("Name or service not known")

        monkeypatch.setattr(socket, "getaddrinfo", no_such_host)
        with pytest.raises(SendRefused) as excinfo:
            _validate_outbound_url("https://nx.example.com/send", "FIX_SMS_GATEWAY_URL")
        assert "does not resolve" in str(excinfo.value)
        assert "production SSRF guard" in str(excinfo.value)

    @pytest.mark.usefixtures("production")
    def test_any_private_answer_among_public_ones_is_refused(self, monkeypatch):
        # DNS rebinding shape: the first answer is public, a later one private.
        resolve_to(monkeypatch, "8.8.8.8", "10.0.0.7")
        with pytest.raises(SendRefused, match=r"non-public address 10.0.0.7"):
            _validate_outbound_url("https://gw.example.com/send", "FIX_SMS_GATEWAY_URL")

    @pytest.mark.usefixtures("production")
    def test_credentials_refused_even_for_public_production_host(self, monkeypatch):
        resolve_to(monkeypatch, "1.1.1.1")
        with pytest.raises(SendRefused, match="credentials must not be embedded"):
            _validate_outbound_url("https://svc@gw.example.com/send", "FIX_SMS_GATEWAY_URL")


class TestNonPublicAddressDetection:
    @pytest.mark.parametrize(
        ("address", "shown"),
        [
            ("10.1.2.3", "10.1.2.3"),  # private
            ("127.0.0.1", "127.0.0.1"),  # loopback
            ("169.254.169.254", "169.254.169.254"),  # link-local metadata
            ("224.0.0.1", "224.0.0.1"),  # multicast
            ("0.0.0.0", "0.0.0.0"),  # unspecified  # noqa: S104 - an address under test, not a bind
            ("fe80::1%eth0", "fe80::1"),  # scoped IPv6 link-local: zone id stripped
        ],
    )
    def test_non_public_answers_are_rejected(self, monkeypatch, address, shown):
        resolve_to(monkeypatch, address)
        reason = _host_is_rejected_in_production("gw.example.com")
        assert reason == f"host 'gw.example.com' resolves to non-public address {shown}"

    def test_public_answers_are_accepted(self, monkeypatch):
        resolve_to(monkeypatch, "8.8.8.8", "1.1.1.1")
        assert _host_is_rejected_in_production("gw.example.com") is None

    def test_unparseable_sockaddr_is_skipped_not_trusted_blindly(self, monkeypatch):
        resolve_to(monkeypatch, "not-an-ip", "8.8.8.8")
        assert _host_is_rejected_in_production("gw.example.com") is None
        resolve_to(monkeypatch, "not-an-ip", "192.168.1.1")
        assert "192.168.1.1" in _host_is_rejected_in_production("gw.example.com")


# --------------------------------------------------------- base behaviour


class TestBaseChannel:
    def test_render_substitutes_every_known_placeholder(self):
        rendered = EmailChannel().render(
            "Dear {{name}}, {{amount}} for {{ref}} ({{name}}) {{unknown}}",
            {"name": "Rahim", "amount": 1500, "ref": "TRK-1"},
        )
        assert rendered == "Dear Rahim, 1500 for TRK-1 (Rahim) {{unknown}}"

    def test_configured_follows_stripped_url_env(self, monkeypatch):
        assert EmailChannel().configured is False
        monkeypatch.setenv("FIX_EMAIL_API_URL", "   ")
        assert EmailChannel().configured is False
        monkeypatch.setenv("FIX_EMAIL_API_URL", " http://mailpit:8025/api/v1/send \n")
        channel = EmailChannel()
        assert channel.configured is True
        assert channel.url == "http://mailpit:8025/api/v1/send"

    def test_post_refuses_an_unconfigured_channel(self, gateway):
        with pytest.raises(RuntimeError, match="unconfigured channel must not reach _post"):
            EmailChannel()._post({"to": ["x"]})
        assert gateway.requests == []

    def test_post_sends_one_json_post_with_timeout(self, monkeypatch, gateway):
        monkeypatch.setenv("FIX_EMAIL_API_URL", "http://mailpit:8025/api/v1/send")
        assert EmailChannel()._post({"to": ["a@example.test"], "text": "hi"}) == {"id": "GW-1"}
        request, timeout = gateway.requests[0]
        assert request.full_url == "http://mailpit:8025/api/v1/send"
        assert request.get_method() == "POST"
        assert timeout == 10
        assert request.get_header("Content-type") == "application/json"
        assert request.get_header("Authorization") is None  # no token configured
        assert gateway.payload() == {"to": ["a@example.test"], "text": "hi"}

    def test_regression_bearer_header_uses_the_stripped_token(self, monkeypatch, gateway):
        """Regression: _post re-read the raw env var for the Authorization
        header, so a mounted secret with a trailing newline produced
        'Bearer <tok>\\n' (http.client rejects it with ValueError) even though
        the stripped value had been checked. The stripped token is sent now."""
        monkeypatch.setenv("FIX_EMAIL_API_URL", "http://mailpit:8025/api/v1/send")
        monkeypatch.setenv("FIX_EMAIL_API_TOKEN", "  dummy-test-token\n")
        EmailChannel()._post({"text": "hi"})
        assert gateway.header("Authorization") == "Bearer dummy-test-token"

    def test_empty_gateway_body_reads_as_empty_object(self, monkeypatch, gateway):
        monkeypatch.setenv("FIX_NOVU_API_URL", "http://novu:3000/v1/events")
        gateway.routes["http://novu:3000/v1/events"] = b""
        assert PushChannel()._post({"message": "x"}) == {}

    def test_bad_url_is_refused_before_any_packet_leaves(self, monkeypatch, gateway):
        monkeypatch.setenv("FIX_NOVU_API_URL", "http://evil.example.com/v1/events")
        with pytest.raises(SendRefused, match="FIX_NOVU_API_URL"):
            PushChannel()._post({"message": "x"})
        assert gateway.requests == []


# ------------------------------------------------------------------- SMS


def sms_channel(monkeypatch, *, primary=False, redundant=False, redundant_only=False):
    if primary:
        monkeypatch.setenv("FIX_SMS_GATEWAY_URL", PRIMARY_SMS_URL)
        monkeypatch.setenv("FIX_SMS_GATEWAY_TOKEN", "primary-test-token")
    if redundant:
        monkeypatch.setenv("FIX_SMS_REDUNDANT_GATEWAY_URL", REDUNDANT_SMS_URL)
        monkeypatch.setenv("FIX_SMS_REDUNDANT_GATEWAY_TOKEN", "redundant-test-token")
    if redundant_only:
        monkeypatch.setenv("FIX_SMS_REDUNDANT_ONLY", "1")
    return SMSChannel()


class TestSmsPolicyGuards:
    @pytest.mark.parametrize("route", ["", "promo", "MASKING"])
    def test_undeclared_route_refused_before_any_send(self, monkeypatch, gateway, route):
        channel = sms_channel(monkeypatch, primary=True)
        with pytest.raises(SendRefused, match="without a declared route"):
            channel.send(MSISDN, "x", sms_route=route)
        assert gateway.requests == []

    def test_masking_route_uses_the_registered_sender(self, monkeypatch, gateway):
        result = sms_channel(monkeypatch, primary=True).send(
            MSISDN, "Your repair is ready -1000FiX", sms_route="masking"
        )
        assert result.status == "delivered"
        assert gateway.payload() == {
            "to": MSISDN,
            "message": "Your repair is ready -1000FiX",
            "route": "masking",
            "sender": "1000FiX",
        }

    def test_non_masking_route_uses_a_numeric_sender(self, monkeypatch, gateway):
        sms_channel(monkeypatch, primary=True).send(MSISDN, "Offer!", sms_route="non-masking")
        assert gateway.payload()["sender"] == "numeric"
        assert gateway.payload()["route"] == "non-masking"


class TestSmsRouting:
    def test_redundant_configured_property(self, monkeypatch):
        assert SMSChannel().redundant_configured is False
        assert sms_channel(monkeypatch, redundant=True).redundant_configured is True

    def test_primary_delivery_returns_provider_id_and_bearer(self, monkeypatch, gateway):
        gateway.routes[PRIMARY_SMS_URL] = b'{"id": 4471}'
        result = sms_channel(monkeypatch, primary=True, redundant=True).send(
            MSISDN, "x", sms_route="masking"
        )
        assert (result.channel, result.status, result.provider_id) == ("sms", "delivered", "4471")
        assert gateway.urls() == [PRIMARY_SMS_URL]  # secondary untouched on success
        assert gateway.header("Authorization") == "Bearer primary-test-token"

    def test_primary_response_without_id_gives_empty_provider_id(self, monkeypatch, gateway):
        gateway.routes[PRIMARY_SMS_URL] = b"{}"
        result = sms_channel(monkeypatch, primary=True).send(MSISDN, "x", sms_route="masking")
        assert result.provider_id == ""

    def test_primary_failure_without_secondary_is_a_visible_failure(self, monkeypatch, gateway):
        gateway.routes[PRIMARY_SMS_URL] = urllib.error.URLError("connection refused")
        result = sms_channel(monkeypatch, primary=True).send(MSISDN, "x", sms_route="masking")
        assert result.status == "failed"
        assert result.detail == "primary gateway failed: <urlopen error connection refused>"

    def test_int011_failover_to_secondary_after_primary_timeout(self, monkeypatch, gateway):
        gateway.routes[PRIMARY_SMS_URL] = TimeoutError("timed out")
        gateway.routes[REDUNDANT_SMS_URL] = b'{"id": "RED-7"}'
        result = sms_channel(monkeypatch, primary=True, redundant=True).send(
            MSISDN, "x", sms_route="masking"
        )
        assert result.status == "delivered"
        assert result.provider_id == "RED-7"
        assert result.detail == "INT-011 failover after primary error"
        assert gateway.urls() == [PRIMARY_SMS_URL, REDUNDANT_SMS_URL]
        assert gateway.header("Authorization") == "Bearer redundant-test-token"
        assert gateway.payload()["sender"] == "1000FiX"

    def test_primary_and_secondary_both_failing(self, monkeypatch, gateway):
        gateway.routes[PRIMARY_SMS_URL] = urllib.error.URLError("primary down")
        gateway.routes[REDUNDANT_SMS_URL] = OSError("secondary reset")
        result = sms_channel(monkeypatch, primary=True, redundant=True).send(
            MSISDN, "x", sms_route="masking"
        )
        assert result.status == "failed"
        assert result.detail == "primary and redundant gateways failed: secondary reset"

    def test_secondary_alone_dispatches_when_primary_unconfigured(self, monkeypatch, gateway):
        monkeypatch.setenv("FIX_SMS_REDUNDANT_GATEWAY_URL", REDUNDANT_SMS_URL)
        gateway.routes[REDUNDANT_SMS_URL] = b'{"id": "RED-8"}'
        result = SMSChannel().send(MSISDN, "x", sms_route="masking")
        assert (result.status, result.provider_id) == ("delivered", "RED-8")
        assert result.detail == "INT-011 redundant secondary dispatch"
        assert gateway.header("Authorization") is None  # no secondary token configured

    def test_secondary_alone_failing(self, monkeypatch, gateway):
        gateway.routes[REDUNDANT_SMS_URL] = urllib.error.URLError("no route")
        result = sms_channel(monkeypatch, redundant=True).send(MSISDN, "x", sms_route="masking")
        assert result.status == "failed"
        assert result.detail == "redundant gateway error: <urlopen error no route>"

    def test_nothing_configured_is_a_dry_run(self, gateway):
        result = SMSChannel().send(MSISDN, "x", sms_route="masking")
        assert (result.status, result.detail) == (
            "dry-run",
            "gateway unconfigured (local default)",
        )
        assert gateway.requests == []

    def test_redundant_only_mode_bypasses_the_primary(self, monkeypatch, gateway):
        gateway.routes[REDUNDANT_SMS_URL] = b'{"id": "RED-9"}'
        result = sms_channel(monkeypatch, primary=True, redundant=True, redundant_only=True).send(
            MSISDN, "x", sms_route="masking"
        )
        assert result.status == "delivered"
        assert result.detail == "dispatched via INT-011 redundant secondary gateway"
        assert gateway.urls() == [REDUNDANT_SMS_URL]

    def test_redundant_only_mode_gateway_error(self, monkeypatch, gateway):
        gateway.routes[REDUNDANT_SMS_URL] = TimeoutError("slow")
        result = sms_channel(monkeypatch, redundant=True, redundant_only=True).send(
            MSISDN, "x", sms_route="masking"
        )
        assert result.status == "failed"
        assert result.detail == "INT-011 redundant gateway error: slow"

    def test_redundant_only_flag_must_be_exactly_one(self, monkeypatch, gateway):
        monkeypatch.setenv("FIX_SMS_REDUNDANT_ONLY", "true")
        result = sms_channel(monkeypatch, primary=True).send(MSISDN, "x", sms_route="masking")
        assert result.status == "delivered"
        assert gateway.urls() == [PRIMARY_SMS_URL]

    def test_secondary_url_goes_through_the_ssrf_guard(self, monkeypatch, gateway):
        monkeypatch.setenv("FIX_SMS_REDUNDANT_GATEWAY_URL", "http://169.254.169.254/latest")
        with pytest.raises(SendRefused, match="SMS_REDUNDANT_GATEWAY"):
            SMSChannel().send(MSISDN, "x", sms_route="masking")
        assert gateway.requests == []


# ------------------------------------------------- other gateway adapters

GATEWAY_ADAPTERS = [
    pytest.param(
        WhatsAppChannel,
        "FIX_WHATSAPP_API_URL",
        "http://localhost:9003/whatsapp",
        "WhatsApp API unconfigured",
        {"to": "rcpt-1", "type": "text", "text": {"body": "Hello\nsecond line"}},
        id="whatsapp",
    ),
    pytest.param(
        EmailChannel,
        "FIX_EMAIL_API_URL",
        "http://mailpit:8025/api/v1/send",
        "email API unconfigured (EP-11 Mailpit in compose)",
        {"to": ["rcpt-1"], "subject": "Hello", "text": "Hello\nsecond line"},
        id="email",
    ),
    pytest.param(
        PushChannel,
        "FIX_NOVU_API_URL",
        "http://novu:3000/v1/events",
        "Novu unconfigured",
        {"subscriberId": "rcpt-1", "message": "Hello\nsecond line"},
        id="push",
    ),
    pytest.param(
        AlertChannel,
        "FIX_ALERT_WEBHOOK_URL",
        "http://localhost:9004/alert",
        "alert webhook unconfigured",
        {"text": "Hello\nsecond line"},
        id="alert",
    ),
]


class TestGatewayAdapters:
    @pytest.mark.parametrize(("cls", "env", "url", "dry_detail", "payload"), GATEWAY_ADAPTERS)
    def test_unconfigured_adapter_is_a_dry_run(self, gateway, cls, env, url, dry_detail, payload):
        result = cls().send("rcpt-1", "Hello\nsecond line")
        assert (result.channel, result.status, result.detail) == (
            cls.channel,
            "dry-run",
            dry_detail,
        )
        assert gateway.requests == []

    @pytest.mark.parametrize(("cls", "env", "url", "dry_detail", "payload"), GATEWAY_ADAPTERS)
    def test_configured_adapter_posts_its_payload(
        self, monkeypatch, gateway, cls, env, url, dry_detail, payload
    ):
        monkeypatch.setenv(env, url)
        gateway.routes[url] = b'{"id": "P-42"}'
        result = cls().send("rcpt-1", "Hello\nsecond line")
        assert (result.channel, result.status, result.provider_id) == (
            cls.channel,
            "delivered",
            "P-42",
        )
        assert gateway.urls() == [url]
        assert gateway.payload() == payload

    @pytest.mark.parametrize(("cls", "env", "url", "dry_detail", "payload"), GATEWAY_ADAPTERS)
    def test_regression_gateway_outage_is_a_failed_result_not_a_crash(
        self, monkeypatch, gateway, cls, env, url, dry_detail, payload
    ):
        """Regression: only the SMS adapter turned transport errors into a
        'failed' result; WhatsApp/email/push/alert let URLError escape, which
        aborted Dispatcher.handle() and made the NT-001 §4 retry + fallback
        ladder (push -> SMS, email bounce -> SMS) unreachable."""
        monkeypatch.setenv(env, url)
        gateway.routes[url] = urllib.error.HTTPError(url, 503, "Service Unavailable", {}, None)
        result = cls().send("rcpt-1", "Hello")
        assert (result.channel, result.status) == (cls.channel, "failed")
        assert result.detail == "gateway error: HTTP Error 503: Service Unavailable"

    def test_email_subject_is_the_first_line_capped_at_120_chars(self, monkeypatch, gateway):
        monkeypatch.setenv("FIX_EMAIL_API_URL", "http://mailpit:8025/api/v1/send")
        EmailChannel().send("rcpt-1", "S" * 130 + "\nbody")
        assert gateway.payload()["subject"] == "S" * 120

    def test_in_app_never_posts_even_when_a_url_is_set(self, monkeypatch, gateway):
        monkeypatch.setenv("FIX_INAPP_API_URL", "http://localhost:9005/inbox")
        result = InAppChannel().send("rcpt-1", "Hello")
        assert (result.channel, result.status) == ("in_app", "dry-run")
        assert "outbox" in result.detail
        assert gateway.requests == []


def test_build_channels_returns_one_adapter_per_channel():
    built = build_channels()
    assert tuple(built) == CHANNELS
    assert {name: type(adapter) for name, adapter in built.items()} == {
        "sms": SMSChannel,
        "whatsapp": WhatsAppChannel,
        "email": EmailChannel,
        "push": PushChannel,
        "in_app": InAppChannel,
        "alert": AlertChannel,
    }
    assert all(adapter.channel == name for name, adapter in built.items())


# ------------------------------------------------------ gateway replies


class TestGatewayReplies:
    @pytest.mark.parametrize("reply", [b"OK", b"[1, 2]", b'"queued"', b"null"])
    def test_regression_non_object_reply_to_an_accepted_send_is_delivered(
        self, monkeypatch, gateway, reply
    ):
        """Regression: a 2xx reply whose body is not a JSON object (plain
        'OK', a list, a string) raised JSONDecodeError/AttributeError after the
        gateway had already accepted the message — the event aborted and a
        re-delivery would double-send. The send is delivered, without an id."""
        gateway.routes[PRIMARY_SMS_URL] = reply
        result = sms_channel(monkeypatch, primary=True).send(MSISDN, "x", sms_route="masking")
        assert (result.status, result.provider_id) == ("delivered", "")

    def test_regression_non_json_reply_from_the_secondary_gateway(self, monkeypatch, gateway):
        """Regression: same defect on the INT-011 secondary route."""
        gateway.routes[REDUNDANT_SMS_URL] = b"ACCEPTED"
        result = sms_channel(monkeypatch, redundant=True).send(MSISDN, "x", sms_route="masking")
        assert (result.status, result.provider_id) == ("delivered", "")
        assert result.detail == "INT-011 redundant secondary dispatch"

    def test_regression_empty_email_body_gets_an_empty_subject(self, monkeypatch, gateway):
        """Regression: the subject was rendered.splitlines()[0], which raised
        IndexError for an empty body and aborted the event."""
        monkeypatch.setenv("FIX_EMAIL_API_URL", "http://mailpit:8025/api/v1/send")
        result = EmailChannel().send("rcpt-1", "")
        assert result.status == "delivered"
        assert gateway.payload() == {"to": ["rcpt-1"], "subject": "", "text": ""}


# --------------------------------------------- the real urllib handler chain


class _RawSocket:
    def __init__(self, raw: bytes) -> None:
        self._raw = raw

    def makefile(self, mode: str, *args: object) -> io.BytesIO:
        return io.BytesIO(self._raw)


def _http_reply(status: str, headers: dict[str, str], body: bytes = b"") -> bytes:
    lines = [f"HTTP/1.1 {status}", *(f"{k}: {v}" for k, v in headers.items())]
    lines.append(f"Content-Length: {len(body)}")
    return ("\r\n".join(lines) + "\r\n\r\n").encode("latin-1") + body


@pytest.fixture
def http_wire(monkeypatch: pytest.MonkeyPatch) -> tuple[list[tuple[str, str, str]], list[bytes]]:
    """Below urllib: http.client.HTTPConnection is replaced by a scripted
    double, so the adapters' real opener + handler chain runs (redirect
    handling included) without opening a socket. Returns (request log,
    queue of raw replies)."""
    log: list[tuple[str, str, str]] = []
    replies: list[bytes] = []

    class ScriptedConnection(http.client.HTTPConnection):
        # Inherits the class-level helpers urllib reads (debuglevel,
        # _get_content_length); never opens a socket.
        def request(self, method, url, body=None, headers=None, **kwargs) -> None:
            log.append((method, self.host, url))

        def getresponse(self) -> http.client.HTTPResponse:
            response = http.client.HTTPResponse(_RawSocket(replies.pop(0)))
            response.begin()
            return response

        def close(self) -> None:
            return None

    monkeypatch.setattr(http.client, "HTTPConnection", ScriptedConnection)
    return log, replies


class TestRedirectsNeverFollowed:
    METADATA = "http://169.254.169.254/latest/meta-data"

    def test_accepted_send_over_the_real_handler_chain(self, monkeypatch, http_wire):
        log, replies = http_wire
        replies.append(
            _http_reply("200 OK", {"Content-Type": "application/json"}, b'{"id": "W-1"}')
        )
        monkeypatch.setenv("FIX_EMAIL_API_URL", "http://mailpit:8025/api/v1/send")
        result = EmailChannel().send("rcpt-1", "Hello")
        assert (result.status, result.provider_id) == ("delivered", "W-1")
        assert [method for method, _, _ in log] == ["POST"]

    def test_regression_redirect_is_a_failed_send_not_followed(self, monkeypatch, http_wire):
        """Regression (SSRF): urllib.request.urlopen's default opener follows
        3xx redirects, so a gateway (or anything answering for it) could
        bounce the send to an address the SSRF guard never validated — e.g.
        the cloud metadata service — despite hard rule 2 ('Redirects are
        never followed'). A redirect is now a visible failed send."""
        log, replies = http_wire
        replies += [
            _http_reply("302 Found", {"Location": self.METADATA}),
            _http_reply("200 OK", {}, b'{"id": "IMDS"}'),
        ]
        monkeypatch.setenv("FIX_EMAIL_API_URL", "http://mailpit:8025/api/v1/send")
        result = EmailChannel().send("rcpt-1", "Hello")
        assert result.status == "failed"
        assert result.detail == "gateway error: HTTP Error 302: Found"
        assert len(log) == 1  # nothing was sent to the redirect target

    def test_regression_secondary_sms_gateway_redirect_not_followed(self, monkeypatch, http_wire):
        """Regression (SSRF): the INT-011 secondary route had the same hole."""
        log, replies = http_wire
        replies += [
            _http_reply("303 See Other", {"Location": self.METADATA}),
            _http_reply("200 OK", {}, b'{"id": "IMDS"}'),
        ]
        result = sms_channel(monkeypatch, redundant=True).send(MSISDN, "x", sms_route="masking")
        assert result.status == "failed"
        assert result.detail == "redundant gateway error: HTTP Error 303: See Other"
        assert len(log) == 1
