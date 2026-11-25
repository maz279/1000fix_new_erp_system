"""Behavioural tests for the local (synthetic-only) residency service stub.

The stub's ``Handler`` is driven through raw HTTP bytes over an in-memory fake
connection - full request parsing and response writing, but no socket and no
listening server. The final test runs the real ``libs.py.fix_residency``
client against the stub the same way, pinning the client/stub contract.
"""

from __future__ import annotations

import email.message
import hashlib
import http.client
import importlib.util
import io
import json
import re
import sys
import urllib.request
import urllib.response
from pathlib import Path
from types import ModuleType

import pytest

_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from libs.py.fix_residency import ResidencyClient, ResidencyError

pytestmark = [pytest.mark.residency]

_APP_PATH = Path(__file__).resolve().parents[1] / "app.py"
_MODULE_NAME = "z4_local_stub_app"  # unique: never shadows a generic ``app`` module


def _load_stub() -> ModuleType:
    if _MODULE_NAME in sys.modules:
        return sys.modules[_MODULE_NAME]
    spec = importlib.util.spec_from_file_location(_MODULE_NAME, _APP_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[_MODULE_NAME] = module
    spec.loader.exec_module(module)
    return module


stub = _load_stub()


class _FakeConnection:
    """Socket stand-in: serves the raw request, collects the raw response."""

    def __init__(self, raw: bytes) -> None:
        self._incoming = io.BytesIO(raw)
        self.sent = bytearray()

    def makefile(self, mode: str, *_args: object, **_kwargs: object) -> io.BytesIO:
        assert "r" in mode  # the handler writes through sendall()
        return self._incoming

    def sendall(self, data: bytes) -> None:
        self.sent += data


class _ReplaySocket:
    def __init__(self, data: bytes) -> None:
        self._data = data

    def makefile(self, *_args: object, **_kwargs: object) -> io.BytesIO:
        return io.BytesIO(self._data)


def _raw_request(
    method: str, path: str, body: bytes | None = None, headers: dict[str, str] | None = None
) -> bytes:
    lines = [f"{method} {path} HTTP/1.1", "Host: localhost"]
    if body is not None:
        lines.append(f"Content-Length: {len(body)}")
    lines += [f"{k}: {v}" for k, v in (headers or {}).items()]
    return ("\r\n".join(lines) + "\r\n\r\n").encode("ascii") + (body or b"")


def _serve(raw: bytes) -> http.client.HTTPResponse:
    conn = _FakeConnection(raw)
    stub.Handler(conn, ("127.0.0.1", 54321), None)
    resp = http.client.HTTPResponse(_ReplaySocket(bytes(conn.sent)))  # type: ignore[arg-type]
    resp.begin()
    return resp


def _call(
    method: str, path: str, payload: object = None, raw_body: bytes | None = None
) -> tuple[int, dict]:
    body = (
        raw_body
        if raw_body is not None
        else (None if payload is None else json.dumps(payload).encode())
    )
    resp = _serve(_raw_request(method, path, body))
    data = resp.read()
    assert resp.getheader("Content-Type") == "application/json"
    assert int(resp.getheader("Content-Length")) == len(data)
    return resp.status, json.loads(data)


def _expected_synthetic(key: str) -> str:
    return "SYNTHETIC-LOCAL-ONLY-" + hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]


# --------------------------------------------------------------------------
# synthetic_value
# --------------------------------------------------------------------------


def test_synthetic_value_is_deterministic_and_bannered() -> None:
    assert stub.SYNTHETIC_BANNER == "SYNTHETIC-LOCAL-ONLY"
    assert stub.synthetic_value("nid:1") == _expected_synthetic("nid:1")
    assert stub.synthetic_value("nid:1") == stub.synthetic_value("nid:1")
    assert stub.synthetic_value("nid:1") != stub.synthetic_value("nid:2")
    assert stub.synthetic_value("নাম").startswith("SYNTHETIC-LOCAL-ONLY-")  # non-ASCII keys


# --------------------------------------------------------------------------
# GET
# --------------------------------------------------------------------------


def test_health_reports_synthetic_only_mode(capsys: pytest.CaptureFixture[str]) -> None:
    assert _call("GET", "/health") == (200, {"status": "UP", "mode": "synthetic-only"})
    # every request is access-logged to stdout via log_message()
    assert '"GET /health HTTP/1.1" 200 -' in capsys.readouterr().out


@pytest.mark.parametrize("path", ["/", "/get", "/health/extra", "/health?x=1"])
def test_unknown_get_paths_are_404(path: str) -> None:
    assert _call("GET", path) == (404, {"error": "not found"})


# --------------------------------------------------------------------------
# POST
# --------------------------------------------------------------------------


def test_assert_local_confirms_local_env() -> None:
    assert _call("POST", "/assert-local") == (200, {"fix_env": "local", "ok": True})


def test_put_acknowledges_without_echoing_the_value() -> None:
    status, body = _call("POST", "/put", {"key": "nid:42", "value": "1234567890"})
    assert status == 200
    assert body == {"stored": True, "value_kind": "synthetic", "key": "nid:42"}
    assert "1234567890" not in json.dumps(body)


def test_get_returns_the_synthetic_value_for_the_key() -> None:
    status, body = _call("POST", "/get", {"key": "passport:7"})
    assert status == 200
    assert body == {
        "key": "passport:7",
        "value": _expected_synthetic("passport:7"),
        "kind": "synthetic",
    }


def test_erase_returns_a_deterministic_tombstone() -> None:
    status, body = _call("POST", "/erase", {"key": "tin:9"})
    assert status == 200
    assert body == {
        "erased": True,
        "key": "tin:9",
        "tombstone": _expected_synthetic("tombstone:tin:9"),
    }


def test_non_string_key_is_coerced_to_string() -> None:
    status, body = _call("POST", "/get", {"key": 123})
    assert (status, body["key"], body["value"]) == (200, "123", _expected_synthetic("123"))


@pytest.mark.parametrize("path", ["/put", "/get", "/erase"])
@pytest.mark.parametrize("payload", [{}, {"key": ""}, {"value": "orphan"}])
def test_missing_key_is_rejected(path: str, payload: dict) -> None:
    assert _call("POST", path, payload) == (400, {"error": "key required"})


def test_post_without_body_or_content_length_is_rejected() -> None:
    assert _call("POST", "/get") == (400, {"error": "key required"})
    assert _call("POST", "/get", raw_body=b"") == (400, {"error": "key required"})


def test_unparseable_json_is_rejected() -> None:
    assert _call("POST", "/put", raw_body=b"{not json") == (400, {"error": "invalid json"})


@pytest.mark.parametrize("raw_body", [b"[1, 2]", b"null", b'"nid:1"', b"42"])
def test_regression_non_object_json_is_rejected_not_crashed(raw_body: bytes) -> None:
    """Regression: syntactically valid but non-object JSON (array, null, string,
    number) reached ``req.get`` and crashed the handler with AttributeError,
    dropping the connection without any response."""
    assert _call("POST", "/get", raw_body=raw_body) == (400, {"error": "invalid json"})


@pytest.mark.parametrize("path", ["/", "/health", "/delete", "/put/extra"])
def test_unknown_post_paths_are_404(path: str) -> None:
    assert _call("POST", path, {"key": "k"}) == (404, {"error": "not found"})


def test_log_message_prints_formatted_line(capsys: pytest.CaptureFixture[str]) -> None:
    handler = stub.Handler.__new__(stub.Handler)  # no connection needed to log
    handler.log_message("%s served in %dms", "/get", 3)
    assert re.fullmatch(r"[\w-]+: /get served in 3ms\n", capsys.readouterr().out)


# --------------------------------------------------------------------------
# Contract with the real client (libs.py.fix_residency)
# --------------------------------------------------------------------------


class _StubTransport(urllib.request.BaseHandler):
    """Routes the client's urllib requests into the stub handler in-process."""

    handler_order = 200

    def http_open(self, req: urllib.request.Request) -> urllib.response.addinfourl:
        # Host / Content-Length are re-derived by _raw_request
        headers = {
            k: v for k, v in req.header_items() if k.lower() not in ("host", "content-length")
        }
        resp = _serve(_raw_request(req.get_method(), req.selector, req.data, headers))
        msg = email.message.Message()
        for name, value in resp.getheaders():
            msg[name] = value
        out = urllib.response.addinfourl(
            io.BytesIO(resp.read()), msg, req.full_url, code=resp.status
        )
        out.msg = resp.reason
        return out


@pytest.fixture
def client() -> ResidencyClient:
    c = ResidencyClient("http://localhost:8100")
    c._opener.add_handler(_StubTransport())
    return c


def test_client_round_trip_against_stub(client: ResidencyClient) -> None:
    assert client.health() == {"status": "UP", "mode": "synthetic-only"}
    assert client.put("nid:1", "1234567890")["value_kind"] == "synthetic"
    assert client.get("nid:1") == _expected_synthetic("nid:1")
    assert client.erase("nid:1")["tombstone"] == _expected_synthetic("tombstone:nid:1")


def test_client_surfaces_stub_rejection_as_residency_error(client: ResidencyClient) -> None:
    with pytest.raises(ResidencyError, match="HTTP Error 400"):
        client.get("")
