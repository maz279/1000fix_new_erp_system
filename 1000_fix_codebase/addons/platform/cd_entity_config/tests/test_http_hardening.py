# OWASP A05 — JSON error responses carry no server traceback outside dev mode.
#
# The JSON-RPC dispatcher is driven exactly like odoo.http.Request does it:
# dispatch() raises inside the endpoint (here: a real ORM call on the live,
# rolled-back `odoo_env`), handle_error() turns the exception into the wire
# response, and the test inspects the bytes a client would receive.
import json

import odoo.http
import pytest
import werkzeug.exceptions
import werkzeug.wrappers
from odoo.addons.cd_entity_config import http_hardening
from odoo.exceptions import UserError, ValidationError
from odoo.tools import config, json_default


class FakeJsonRequest:
    """The slice of odoo.http.Request the JSON dispatchers use (no db: the
    endpoint is called directly, as for a nodb route)."""

    db = None

    def __init__(self, payload=None):
        self._payload = payload or {"jsonrpc": "2.0", "id": 7, "params": {}}
        self.params = {}

    def get_json_data(self):
        return self._payload

    def make_json_response(self, data, headers=None, cookies=None, status=200):
        body = json.dumps(data, ensure_ascii=False, default=json_default)
        return werkzeug.wrappers.Response(
            body, status=status, headers=headers, content_type="application/json"
        )


def _jsonrpc(endpoint, payload=None):
    dispatcher = odoo.http._dispatchers["jsonrpc"](FakeJsonRequest(payload))
    try:
        response = dispatcher.dispatch(endpoint, {})
    except Exception as exc:  # what Request._serve_db/_serve_nodb do
        response = dispatcher.handle_error(exc)
    text = response.get_data(as_text=True)
    return json.loads(text), text


@pytest.fixture
def production(monkeypatch):
    monkeypatch.setitem(config, "dev_mode", [])
    monkeypatch.delenv("FIX_ENV", raising=False)


@pytest.fixture
def approve_draft_request(odoo_env):
    """An endpoint whose live ORM call raises: approving a draft MDM request."""
    partner = odoo_env["res.partner"].create({"name": "RPC Probe"})
    change = odoo_env["fix.mdm.change.request"].create(
        {"title": "probe", "model_name": "res.partner", "record_id": partner.id}
    )

    def endpoint(**_params):
        change.action_approve()

    return endpoint


# --- live JSON-RPC dispatch ---------------------------------------------------------


def test_production_error_keeps_contract_but_drops_traceback(production, approve_draft_request):
    payload, wire = _jsonrpc(approve_draft_request)

    assert payload["id"] == 7 and payload["jsonrpc"] == "2.0"
    error = payload["error"]
    assert (error["code"], error["message"]) == (0, "Odoo Server Error")
    assert error["data"] == {
        "name": "odoo.exceptions.ValidationError",
        "message": "Only submitted requests can be approved.",
        "arguments": ["Only submitted requests can be approved."],
        "context": {},
    }
    assert "debug" not in error["data"]
    assert "Traceback" not in wire
    assert "fix_mdm_change_request.py" not in wire


@pytest.mark.parametrize(
    ("dev_mode", "fix_env"), [(["reload", "qweb"], None), ([], "local")], ids=["dev", "local"]
)
def test_dev_mode_or_local_workstation_keeps_the_traceback(
    monkeypatch, approve_draft_request, dev_mode, fix_env
):
    monkeypatch.setitem(config, "dev_mode", dev_mode)
    if fix_env:
        monkeypatch.setenv("FIX_ENV", fix_env)
    else:
        monkeypatch.delenv("FIX_ENV", raising=False)

    payload, _wire = _jsonrpc(approve_draft_request)

    debug = payload["error"]["data"]["debug"]
    assert debug.startswith("Traceback (most recent call last):")
    assert "action_approve" in debug
    assert payload["error"]["data"]["message"] == "Only submitted requests can be approved."


def test_non_local_environment_name_is_still_redacted(monkeypatch, approve_draft_request):
    monkeypatch.setitem(config, "dev_mode", [])
    monkeypatch.setenv("FIX_ENV", "staging")
    payload, wire = _jsonrpc(approve_draft_request)
    assert "debug" not in payload["error"]["data"]
    assert "Traceback" not in wire


def test_unexpected_server_errors_are_redacted_too(production, odoo_env):
    def endpoint(**_params):
        return odoo_env["no.such.model"]

    payload, wire = _jsonrpc(endpoint)
    assert payload["error"]["data"]["name"] == "builtins.KeyError"
    assert "debug" not in payload["error"]["data"]
    assert "Traceback" not in wire


def test_not_found_keeps_the_404_contract(production):
    def endpoint(**_params):
        raise werkzeug.exceptions.NotFound()

    payload, _wire = _jsonrpc(endpoint)
    assert (payload["error"]["code"], payload["error"]["message"]) == (404, "404: Not Found")
    assert "debug" not in payload["error"]["data"]


def test_successful_calls_are_untouched(production, odoo_env):
    def endpoint(**params):
        return {"partners": odoo_env["res.partner"].search_count([]) >= 0, **params}

    payload, _wire = _jsonrpc(endpoint, {"jsonrpc": "2.0", "id": 3, "params": {"x": 1}})
    assert payload == {"jsonrpc": "2.0", "id": 3, "result": {"partners": True, "x": 1}}


def test_dispatcher_redacts_payloads_built_from_the_unwrapped_serializer(production):
    """Defence in depth: a handle_error override that bound the ORIGINAL
    serialize_exception before this addon loaded still cannot leak."""
    dispatcher = odoo.http._dispatchers["jsonrpc"](FakeJsonRequest())
    try:
        raise UserError("Stock is locked")
    except UserError as exc:
        raw = http_hardening._original_serialize_exception(exc)
    assert raw["debug"]  # the stock serializer does carry the traceback

    response = dispatcher._response(error={"code": 0, "message": "x", "data": raw})

    data = json.loads(response.get_data(as_text=True))["error"]["data"]
    assert "debug" not in data
    assert data["message"] == "Stock is locked"


def test_dispatcher_passes_errors_without_data_through(production):
    dispatcher = odoo.http._dispatchers["jsonrpc"](FakeJsonRequest())
    response = dispatcher._response(error={"code": 1, "message": "bare"})
    assert json.loads(response.get_data(as_text=True))["error"] == {"code": 1, "message": "bare"}


def test_the_hardened_dispatcher_is_the_registered_jsonrpc_dispatcher():
    assert issubclass(odoo.http._dispatchers["jsonrpc"], http_hardening.HardenedJsonRPCDispatcher)


# --- JSON-2 dispatcher + the wrapped serializer ------------------------------------------


def test_json2_errors_are_redacted(production):
    dispatcher = odoo.http._dispatchers["json2"](FakeJsonRequest())
    try:
        raise ValidationError("Bad postcode")
    except ValidationError as exc:
        response = dispatcher.handle_error(exc)
    body = json.loads(response.get_data(as_text=True))
    assert response.status_code == 422
    assert body["message"] == "Bad postcode"
    assert "debug" not in body


def test_serialize_exception_honours_message_and_arguments_overrides(production):
    assert odoo.http.serialize_exception is http_hardening.serialize_exception
    data = odoo.http.serialize_exception(
        RuntimeError("internal detail"), message="Shown", arguments=("Shown", 500)
    )
    assert data == {
        "name": "builtins.RuntimeError",
        "message": "Shown",
        "arguments": ("Shown", 500),
        "context": {},
    }


def test_traceback_text_embedded_in_message_or_arguments_is_cut(production):
    leaked = 'boom\nTraceback (most recent call last):\n  File "/srv/odoo/x.py", line 1'
    data = http_hardening.redact_error_data(
        {"name": "E", "message": leaked, "arguments": [leaked, 42], "debug": "tb"}
    )
    assert data == {"name": "E", "message": "boom", "arguments": ["boom", 42]}
    as_tuple = http_hardening.redact_error_data({"message": "ok", "arguments": (leaked,)})
    assert as_tuple == {"message": "ok", "arguments": ("boom",)}
    assert http_hardening.redact_error_data({"name": "E"}) == {"name": "E"}


def test_non_dict_payloads_are_returned_untouched(production):
    assert http_hardening.redact_error_data("plain text") == "plain text"
    assert http_hardening.redact_error_data(None) is None


def test_install_is_idempotent_and_repairs_a_reset_serializer(monkeypatch):
    monkeypatch.setattr(
        odoo.http, "serialize_exception", http_hardening._original_serialize_exception
    )
    http_hardening.install()
    assert odoo.http.serialize_exception is http_hardening.serialize_exception
    http_hardening.install()
    assert odoo.http.serialize_exception is http_hardening.serialize_exception
    assert (
        http_hardening.serialize_exception.__wrapped__
        is http_hardening._original_serialize_exception
    )
