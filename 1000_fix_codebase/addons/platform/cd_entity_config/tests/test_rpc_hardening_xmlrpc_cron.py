# OWASP A05 — XML-RPC faults and the ir.cron "Run Manually" error payload carry
# no server traceback outside dev mode; the hardening is active as soon as
# cd_entity_config is imported as a server-wide module (no registry needed).
#
# XML-RPC is driven through the real rpc controller routes (/xmlrpc/2 and
# /xmlrpc) and odoo.http.dispatch_rpc, with errors raised by the real service
# dispatchers before any database is touched.
import importlib
import json
import logging
import subprocess
import sys
import textwrap
import threading
import xmlrpc.client
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import odoo.http
import pytest
from odoo.addons.cd_entity_config import http_hardening
from odoo.tools import config

CODE_ROOT = Path(__file__).resolve().parents[4]
XMLRPC_CTRL = importlib.import_module("odoo.addons.rpc.controllers.xmlrpc")
RPC_PKG = importlib.import_module("odoo.addons.rpc.controllers")
IR_CRON = importlib.import_module("odoo.addons.base.models.ir_cron")


@pytest.fixture
def production(monkeypatch):
    monkeypatch.setitem(config, "dev_mode", [])
    monkeypatch.delenv("FIX_ENV", raising=False)


@pytest.fixture(params=["dev_mode", "fix_env_local"])
def developer(request, monkeypatch):
    if request.param == "dev_mode":
        monkeypatch.setitem(config, "dev_mode", ["reload", "qweb"])
        monkeypatch.delenv("FIX_ENV", raising=False)
    else:
        monkeypatch.setitem(config, "dev_mode", [])
        monkeypatch.setenv("FIX_ENV", "local")


@pytest.fixture
def xmlrpc_fault(monkeypatch):
    """Call an XML-RPC route; return (Fault decoded from the wire, raised exc)."""
    thread = threading.current_thread()
    for attr in ("uid", "dbname"):  # dispatch_rpc resets these on the thread
        monkeypatch.setattr(thread, attr, getattr(thread, attr, None), raising=False)

    def call(route, service, method, params):
        body = xmlrpc.client.dumps(tuple(params), methodname=method).encode()
        fake = SimpleNamespace(db=None, httprequest=SimpleNamespace(get_data=lambda: body))
        monkeypatch.setattr(XMLRPC_CTRL, "request", fake)
        monkeypatch.setattr(RPC_PKG, "request", fake)
        odoo.http._request_stack.push(fake)  # dispatch_rpc borrows the request
        raised = None
        try:
            getattr(XMLRPC_CTRL.XMLRPC(), route)(service)
        except Exception as exc:  # the route re-raises with error_response set
            raised = exc
        finally:
            odoo.http._request_stack.pop()
        assert raised is not None, "the RPC call was expected to fail"
        with pytest.raises(xmlrpc.client.Fault) as fault:
            xmlrpc.client.loads(raised.error_response.get_data())
        return fault.value, raised

    return call


BAD_UID = ("fix_test", "not-a-uid", "secret", "res.partner", "search", [[]])


# --- /xmlrpc/2 (integer fault codes) ---------------------------------------------------


def test_xmlrpc2_application_error_keeps_code_and_message_only(production, xmlrpc_fault):
    fault, raised = xmlrpc_fault("xmlrpc_2", "object", "execute_kw", BAD_UID)
    assert isinstance(raised, ValueError)
    assert fault.faultCode == 1  # RPC_FAULT_CODE_APPLICATION_ERROR
    assert fault.faultString == "ValueError: invalid literal for int() with base 10: 'not-a-uid'"
    assert "Traceback" not in fault.faultString


def test_xmlrpc2_keeps_the_traceback_for_developers(developer, xmlrpc_fault):
    fault, _raised = xmlrpc_fault("xmlrpc_2", "object", "execute_kw", BAD_UID)
    assert fault.faultCode == 1
    assert fault.faultString.startswith("Traceback (most recent call last):")
    assert "uid = int(uid)" in fault.faultString


def test_xmlrpc2_odoo_business_errors_keep_their_stock_fault(production, xmlrpc_fault):
    no_password = ("fix_test", 2, "", "res.partner", "search", [[]])
    fault, raised = xmlrpc_fault("xmlrpc_2", "object", "execute_kw", no_password)
    assert type(raised).__name__ == "AccessDenied"
    assert fault.faultCode == 3  # RPC_FAULT_CODE_ACCESS_DENIED
    assert fault.faultString == "Access Denied"


# --- /xmlrpc (legacy string fault codes) ---------------------------------------------------


def test_xmlrpc_legacy_application_error_drops_the_traceback(production, xmlrpc_fault):
    fault, _raised = xmlrpc_fault("xmlrpc_1", "common", "no_such_method", ())
    assert fault.faultCode == "Method not found: no_such_method"
    assert fault.faultString == ""


def test_xmlrpc_legacy_keeps_the_traceback_for_developers(developer, xmlrpc_fault):
    fault, _raised = xmlrpc_fault("xmlrpc_1", "common", "no_such_method", ())
    assert fault.faultCode == "Method not found: no_such_method"
    assert fault.faultString.startswith("Traceback (most recent call last):")


# --- XML-RPC patch installation ---------------------------------------------------------------


def test_xmlrpc_patch_is_idempotent_and_repairs_a_reset(monkeypatch):
    hardened_int = XMLRPC_CTRL.xmlrpc_handle_exception_int
    assert hardened_int._fix_hardened is True
    assert http_hardening._install_xmlrpc() is True
    assert XMLRPC_CTRL.xmlrpc_handle_exception_int is hardened_int  # not double-wrapped

    stock = hardened_int.__wrapped__
    monkeypatch.setattr(XMLRPC_CTRL, "xmlrpc_handle_exception_int", stock)
    http_hardening._install_xmlrpc()
    rewrapped = XMLRPC_CTRL.xmlrpc_handle_exception_int
    assert rewrapped is not stock and rewrapped.__wrapped__ is stock


def test_missing_rpc_addon_is_reported_not_fatal(monkeypatch, caplog):
    monkeypatch.setitem(sys.modules, "odoo.addons.rpc.controllers.xmlrpc", None)
    with caplog.at_level(logging.WARNING):
        assert http_hardening._install_xmlrpc() is False
    assert "XML-RPC faults unpatched" in caplog.text


# --- ir.cron "Run Manually" -----------------------------------------------------------------


def _run_failing_cron(env):
    """method_direct_trigger on a cron whose server action really fails.

    The stock _process_job runs the action in a NEW, committed cursor; it is
    replaced by a run inside the rolled-back test transaction that fails and
    logs exactly like ir.cron's _run_job does.
    """
    cron = env["ir.cron"].create(
        {
            "name": "Probe failing job",
            "model_id": env.ref("base.model_res_partner").id,
            "state": "code",
            "code": "result = 1 / 0",
            "interval_number": 1,
            "interval_type": "days",
        }
    )

    def run_in_test_transaction(cls, cron_cr, job):
        try:
            cron.ir_actions_server_id.run()
        except Exception:
            logging.getLogger(IR_CRON.__name__).exception("Job %r failed", job["cron_name"])

    with mock.patch.object(
        type(env["ir.cron"]), "_process_job", classmethod(run_in_test_transaction)
    ):
        return cron.method_direct_trigger()


def test_cron_error_payload_has_no_traceback_outside_dev_mode(production, odoo_env):
    assert IR_CRON.serialize_exception is http_hardening.serialize_exception
    action = _run_failing_cron(odoo_env)
    assert action["tag"] == "display_exception"
    data = action["params"]["data"]
    assert data["name"] == "builtins.RuntimeError"
    assert "debug" not in data
    assert "Traceback" not in json.dumps(action, default=str)


def test_cron_error_payload_keeps_the_traceback_for_developers(developer, odoo_env):
    debug = _run_failing_cron(odoo_env)["params"]["data"]["debug"]
    assert "Traceback (most recent call last):" in debug
    assert "division by zero" in debug


def test_install_repairs_a_reset_cron_reference(monkeypatch):
    monkeypatch.setattr(
        IR_CRON, "serialize_exception", http_hardening._original_serialize_exception
    )
    http_hardening.install()
    assert IR_CRON.serialize_exception is http_hardening.serialize_exception


# --- server-wide load (no registry) ----------------------------------------------------------

_SERVER_WIDE_PROBE = textwrap.dedent(
    """
    import importlib.util, json, sys
    from pathlib import Path

    root = Path.cwd()
    sys.path[:0] = [str(root), str(root / "vendor" / "odoo")]
    import odoo
    from odoo.tools import config

    spec = importlib.util.spec_from_file_location(
        "gen", root / "tooling" / "scripts" / "generate-odoo-conf.py"
    )
    gen = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gen)
    config["addons_path"] = [str((root / p).resolve()) for p in gen.build_addons_path().split(",")]
    config["server_wide_modules"] = ["base", "web", "cd_entity_config"]
    from odoo.modules.module import initialize_sys_path
    initialize_sys_path()

    from odoo.service.server import load_server_wide_modules
    load_server_wide_modules()  # exactly what odoo-bin does at startup

    import odoo.http, odoo.sql_db
    from odoo.modules.registry import Registry
    hardening = sys.modules["odoo.addons.cd_entity_config.http_hardening"]
    xmlrpc_ctrl = sys.modules["odoo.addons.rpc.controllers.xmlrpc"]
    ir_cron = sys.modules["odoo.addons.base.models.ir_cron"]
    print(json.dumps({
        "serialize_exception": odoo.http.serialize_exception is hardening.serialize_exception,
        "jsonrpc_dispatcher": issubclass(
            odoo.http._dispatchers["jsonrpc"], hardening.HardenedJsonRPCDispatcher
        ),
        "xmlrpc_int": getattr(xmlrpc_ctrl.xmlrpc_handle_exception_int, "_fix_hardened", False),
        "xmlrpc_string": getattr(
            xmlrpc_ctrl.xmlrpc_handle_exception_string, "_fix_hardened", False
        ),
        "ir_cron": ir_cron.serialize_exception is hardening.serialize_exception,
        "registries": len(Registry.registries),
        "db_pool": odoo.sql_db._Pool is not None,
    }))
    """
)


def test_server_wide_load_activates_the_hardening_without_a_registry():
    """A fresh interpreter loads base,web,cd_entity_config the way odoo-bin
    does for --load: every patch is live, no registry was built and no
    database connection was opened (import is ORM-free)."""
    proc = subprocess.run(  # noqa: S603 - fixed argv, in-repo probe script
        [sys.executable, "-c", _SERVER_WIDE_PROBE],
        cwd=CODE_ROOT,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert proc.returncode == 0, proc.stderr[-4000:]
    assert json.loads(proc.stdout.strip().splitlines()[-1]) == {
        "serialize_exception": True,
        "jsonrpc_dispatcher": True,
        "xmlrpc_int": True,
        "xmlrpc_string": True,
        "ir_cron": True,
        "registries": 0,
        "db_pool": False,
    }
