"""Behavioural tests for libs.py.fix_residency - the sole Z4 client (FF-09).

No network: every request is answered by an in-process urllib handler that is
installed on the client's own opener, so the real opener chain (proxy handling,
redirect refusal, HTTP error processing) is exercised end to end.
"""

from __future__ import annotations

import email.message
import http.client
import io
import json
import logging
import sys
import urllib.error
import urllib.request
import urllib.response
from collections.abc import Callable
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[4]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import libs.py.fix_residency as residency
from libs.py.fix_residency import (
    ResidencyClient,
    ResidencyError,
    ResidencyURLBlocked,
    get_client,
)

pytestmark = [pytest.mark.residency]

Outcome = tuple[int, bytes] | tuple[int, bytes, dict[str, str]] | BaseException


class FakeTransport(urllib.request.BaseHandler):
    """In-process stand-in for the network: answers http:// requests itself."""

    handler_order = 200  # after any ProxyHandler (100), before HTTPHandler (500)

    def __init__(self, responder: Callable[[urllib.request.Request], Outcome]):
        self.responder = responder
        self.requests: list[urllib.request.Request] = []

    def http_open(self, req: urllib.request.Request) -> urllib.response.addinfourl:
        self.requests.append(req)
        outcome = self.responder(req)
        if isinstance(outcome, BaseException):
            raise outcome
        status, payload, *rest = outcome
        headers = email.message.Message()
        for name, value in (rest[0] if rest else {}).items():
            headers[name] = value
        resp = urllib.response.addinfourl(io.BytesIO(payload), headers, req.full_url, code=status)
        resp.msg = http.client.responses.get(status, "")
        return resp


def _ok(body: dict) -> Callable[[urllib.request.Request], Outcome]:
    return lambda _req: (200, json.dumps(body).encode("utf-8"))


@pytest.fixture
def make_client() -> Callable[..., tuple[ResidencyClient, FakeTransport]]:
    def _make(
        responder: Callable[[urllib.request.Request], Outcome],
        base_url: str = "http://residency-service:8100",
    ) -> tuple[ResidencyClient, FakeTransport]:
        client = ResidencyClient(base_url)
        transport = FakeTransport(responder)
        client._opener.add_handler(transport)
        return client, transport

    return _make


# --------------------------------------------------------------------------
# SSRF allowlist (_validate_base_url)
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("http://127.0.0.1:8100", "http://127.0.0.1:8100"),
        ("http://localhost:8100/", "http://localhost:8100"),
        ("http://[::1]:8100//", "http://[::1]:8100"),
        ("http://residency-stub:8100", "http://residency-stub:8100"),
        ("http://residency-service", "http://residency-service"),
        ("HTTP://LOCALHOST:8100/", "HTTP://LOCALHOST:8100"),  # scheme/host are case-insensitive
    ],
)
def test_allowlisted_base_urls_are_accepted_and_normalised(raw: str, expected: str) -> None:
    assert residency._validate_base_url(raw) == expected


@pytest.mark.parametrize(
    "raw",
    [
        "https://127.0.0.1:8100",
        "ftp://localhost/",
        "file:///etc/passwd",
        "127.0.0.1:8100",  # no scheme at all
    ],
)
def test_non_http_schemes_are_blocked(raw: str) -> None:
    with pytest.raises(ResidencyURLBlocked, match="not allowed \\(expected http\\)"):
        residency._validate_base_url(raw)


@pytest.mark.parametrize(
    ("raw", "host"),
    [
        ("http://169.254.169.254/latest/meta-data", "169.254.169.254"),  # cloud metadata
        ("http://example.com:8100", "example.com"),
        ("http://localhost.evil.example", "localhost.evil.example"),
        ("http://127.0.0.1@evil.example/", "evil.example"),  # userinfo smuggling
        ("http://evil.example#@127.0.0.1", "evil.example"),  # fragment smuggling
        ("http://10.0.0.5:8100", "10.0.0.5"),  # private-subnet scanning
        ("http://:8100", None),  # no host
    ],
)
def test_non_allowlisted_hosts_are_blocked(raw: str, host: str | None) -> None:
    with pytest.raises(ResidencyURLBlocked) as excinfo:
        residency._validate_base_url(raw)
    message = str(excinfo.value)
    assert f"host {host!r} not in the residency allowlist" in message
    assert "RESIDENCY_BASE" in message
    # the specific error is still a ResidencyError for callers catching broadly
    assert isinstance(excinfo.value, ResidencyError)


# --------------------------------------------------------------------------
# Construction
# --------------------------------------------------------------------------


def test_explicit_base_url_wins_over_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("RESIDENCY_BASE", "http://localhost:9999")
    client = ResidencyClient("http://residency-service:8100/")
    assert client._base == "http://residency-service:8100"


def test_base_url_read_from_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("RESIDENCY_BASE", "http://localhost:9999/")
    assert ResidencyClient()._base == "http://localhost:9999"


def test_default_base_url_is_local_loopback(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("RESIDENCY_BASE", raising=False)
    assert ResidencyClient()._base == "http://127.0.0.1:8100"
    # an empty string is treated as "not configured", not as a URL
    assert ResidencyClient("")._base == "http://127.0.0.1:8100"


def test_blocked_environment_url_fails_at_construction(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("RESIDENCY_BASE", "http://169.254.169.254")
    with pytest.raises(ResidencyURLBlocked):
        ResidencyClient()


def test_opener_installs_the_redirect_refusing_handler() -> None:
    client = ResidencyClient("http://localhost:8100")
    assert any(isinstance(h, residency._NoRedirect) for h in client._opener.handlers)


# --------------------------------------------------------------------------
# Operations (happy paths)
# --------------------------------------------------------------------------


def test_put_posts_key_and_value_as_json(make_client, caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.DEBUG, logger=residency.logger.name)
    reply = {"stored": True, "value_kind": "synthetic", "key": "nid:42"}
    client, transport = make_client(_ok(reply))

    assert client.put("nid:42", "1234567890") == reply

    (req,) = transport.requests
    assert req.get_method() == "POST"
    assert req.full_url == "http://residency-service:8100/put"
    assert json.loads(req.data) == {"key": "nid:42", "value": "1234567890"}
    assert req.get_header("Content-type") == "application/json"
    assert req.timeout == residency._TIMEOUT == 10
    assert "fix_residency: put nid:42 (kind=synthetic)" in caplog.text
    assert "1234567890" not in caplog.text  # the classified value is never logged


def test_get_returns_value_and_logs_synthetic_reads(
    make_client, caplog: pytest.LogCaptureFixture
) -> None:
    caplog.set_level(logging.DEBUG, logger=residency.logger.name)
    client, transport = make_client(_ok({"key": "nid:1", "value": "SYN-1", "kind": "synthetic"}))

    assert client.get("nid:1") == "SYN-1"
    (req,) = transport.requests
    assert req.full_url.endswith("/get")
    assert json.loads(req.data) == {"key": "nid:1"}
    assert "fix_residency: get nid:1 -> synthetic value" in caplog.text


def test_get_of_real_value_is_not_flagged_synthetic(
    make_client, caplog: pytest.LogCaptureFixture
) -> None:
    caplog.set_level(logging.DEBUG, logger=residency.logger.name)
    client, _ = make_client(_ok({"key": "tin:9", "value": "REAL", "kind": "resident"}))

    assert client.get("tin:9") == "REAL"
    assert "synthetic value" not in caplog.text


def test_get_without_value_returns_empty_string(make_client) -> None:
    client, _ = make_client(_ok({"key": "tin:9"}))
    assert client.get("tin:9") == ""


def test_erase_posts_key_and_returns_tombstone(make_client) -> None:
    reply = {"erased": True, "key": "nid:7", "tombstone": "T-1"}
    client, transport = make_client(_ok(reply))

    assert client.erase("nid:7") == reply
    (req,) = transport.requests
    assert (req.get_method(), req.full_url) == ("POST", "http://residency-service:8100/erase")
    assert json.loads(req.data) == {"key": "nid:7"}


def test_health_is_a_bodyless_get(make_client) -> None:
    client, transport = make_client(_ok({"status": "UP", "mode": "synthetic-only"}))

    assert client.health() == {"status": "UP", "mode": "synthetic-only"}
    (req,) = transport.requests
    assert req.get_method() == "GET"
    assert req.full_url == "http://residency-service:8100/health"
    assert req.data is None


# --------------------------------------------------------------------------
# Failure handling
# --------------------------------------------------------------------------


@pytest.mark.parametrize("status", [201, 204])
def test_non_200_success_status_is_an_error(make_client, status: int) -> None:
    client, _ = make_client(lambda _req: (status, b"{}"))
    with pytest.raises(ResidencyError, match=f"HTTP {status} from /put") as excinfo:
        client.put("k", "v")
    assert not isinstance(excinfo.value, ResidencyURLBlocked)


@pytest.mark.parametrize("status", [404, 500, 503])
def test_http_error_status_is_wrapped(make_client, status: int) -> None:
    client, _ = make_client(lambda _req: (status, b'{"error": "boom"}'))
    with pytest.raises(ResidencyError, match="residency service unreachable") as excinfo:
        client.health()
    assert isinstance(excinfo.value.__cause__, urllib.error.HTTPError)
    assert excinfo.value.__cause__.code == status


@pytest.mark.parametrize(
    "failure",
    [
        urllib.error.URLError("connection refused"),
        TimeoutError("timed out"),
        ConnectionRefusedError(10061, "refused"),
        OSError("network down"),
    ],
)
def test_transport_failures_are_wrapped(make_client, failure: BaseException) -> None:
    client, _ = make_client(lambda _req: failure)
    with pytest.raises(ResidencyError, match="residency service unreachable") as excinfo:
        client.get("nid:1")
    assert excinfo.value.__cause__ is failure


def test_redirect_is_refused_and_not_followed(make_client) -> None:
    target = "http://169.254.169.254/latest/meta-data"
    client, transport = make_client(lambda _req: (302, b"", {"Location": target}))

    with pytest.raises(ResidencyURLBlocked, match=r"redirect to .*169.254.169.254.* refused"):
        client.get("nid:1")
    # exactly one request: the redirect target was never contacted
    assert [r.full_url for r in transport.requests] == ["http://residency-service:8100/get"]


def test_no_redirect_handler_refuses_directly() -> None:
    handler = residency._NoRedirect()
    req = urllib.request.Request("http://localhost:8100/get")
    with pytest.raises(ResidencyURLBlocked, match=r"'http://evil.example/' refused"):
        handler.redirect_request(req, None, 301, "Moved", {}, "http://evil.example/")


def test_regression_environment_proxy_is_ignored(
    make_client, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Regression: build_opener() used to install the default ProxyHandler, so an
    http_proxy/HTTP_PROXY variable silently routed classified values to a
    non-allowlisted proxy host despite the "no proxy" design."""
    for name in ("http_proxy", "HTTP_PROXY"):
        monkeypatch.setenv(name, "http://proxy.evil.example:3128")
    for name in ("no_proxy", "NO_PROXY"):
        monkeypatch.delenv(name, raising=False)
    client, transport = make_client(_ok({"stored": True}))

    client.put("nid:1", "secret")

    (req,) = transport.requests
    assert not req.has_proxy()
    assert req.host == "residency-service:8100"


# --------------------------------------------------------------------------
# Singleton
# --------------------------------------------------------------------------


def test_get_client_builds_once_and_reuses(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(residency, "_client", None)
    monkeypatch.setenv("RESIDENCY_BASE", "http://localhost:8100")

    first = get_client()
    assert isinstance(first, ResidencyClient)
    assert first._base == "http://localhost:8100"
    assert residency._client is first

    monkeypatch.setenv("RESIDENCY_BASE", "http://residency-service")
    assert get_client() is first  # env is only read at first construction


def test_get_client_returns_existing_instance(monkeypatch: pytest.MonkeyPatch) -> None:
    existing = ResidencyClient("http://residency-service")
    monkeypatch.setattr(residency, "_client", existing)
    assert get_client() is existing
