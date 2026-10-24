# RPC error hardening — no server tracebacks on the wire (OWASP A05:2021).
#
# Stock Odoo hands the full Python traceback to the caller on every error:
#   * JSON-RPC / JSON-2: `error.data.debug` (odoo.http.serialize_exception);
#   * XML-RPC: the fault string of /xmlrpc/2 (int codes) and /xmlrpc (string
#     codes) is the formatted traceback for every non-Odoo exception;
#   * ir.cron "Run Manually": the display_exception action payload (ir_cron
#     bound serialize_exception by name at import).
# Module paths, SQL and record values leak to any authenticated (or, for
# auth="public"/"none" routes, anonymous) client.
#
# cd_entity_config is the T0 module every 1000FiX install carries, and it is a
# SERVER-WIDE module (generate-odoo-conf / compose --load), so the hardening
# is active from startup, before any registry, and stays process-wide:
#   * odoo.http.serialize_exception is wrapped (resolved at call time by the
#     JSON-RPC/JSON-2 dispatchers and the web report/export download paths),
#     and so is ir_cron's own bound reference;
#   * the JSON-RPC dispatcher redacts the payload it emits (defence in depth
#     for handle_error overrides built on a pre-bound serializer);
#   * the rpc addon's two XML-RPC fault builders are wrapped.
# Tracebacks are kept only for developers: `--dev` (config dev_mode) or
# FIX_ENV=local (the DE-11 workstation marker). Error name / message /
# arguments / context and the XML-RPC fault code are always kept — clients
# route on them. Nothing here touches the ORM: importing it is registry-free.
import functools
import importlib
import logging
import os
import traceback
import xmlrpc.client
from collections.abc import Callable, Sequence
from types import ModuleType
from typing import Any, TypeVar, overload

import odoo.exceptions
import odoo.http
from odoo.tools import config, exception_to_unicode

_logger = logging.getLogger(__name__)

_TRACEBACK_MARKER = "Traceback (most recent call last):"
_XMLRPC_MODULE = "odoo.addons.rpc.controllers.xmlrpc"
_IR_CRON_MODULE = "odoo.addons.base.models.ir_cron"
# Odoo's own business errors: their XML-RPC faults carry str(e) only, never a
# traceback, so the stock builders already answer them correctly.
_KNOWN_RPC_ERRORS = (odoo.exceptions.UserError, odoo.exceptions.RedirectWarning)

_T = TypeVar("_T")
# An rpc addon fault builder: exception -> XML-RPC wire payload.
FaultBuilder = Callable[[BaseException], str]


def tracebacks_exposed() -> bool:
    """True only in developer mode (--dev ...) or on a FIX_ENV=local workstation."""
    return bool(config.get("dev_mode")) or os.environ.get("FIX_ENV") == "local"


def _scrub(value: object) -> object:
    """Cut any embedded traceback text out of a message/argument string."""
    if isinstance(value, str) and _TRACEBACK_MARKER in value:
        return value.split(_TRACEBACK_MARKER, 1)[0].rstrip()
    return value


@overload
def redact_error_data(data: dict[str, Any]) -> dict[str, Any]: ...
@overload
def redact_error_data[T](data: T) -> T: ...
def redact_error_data(data: object) -> object:
    """Return a copy of a serialised exception without traceback content.

    Non-dict payloads are returned untouched, and so is everything while
    tracebacks are exposed (dev mode / FIX_ENV=local).
    """
    if not isinstance(data, dict) or tracebacks_exposed():
        return data
    clean = {key: value for key, value in data.items() if key != "debug"}
    if "message" in clean:
        clean["message"] = _scrub(clean["message"])
    if isinstance(clean.get("arguments"), list | tuple):
        clean["arguments"] = type(clean["arguments"])(_scrub(arg) for arg in clean["arguments"])
    return clean


# --- JSON-RPC / JSON-2 ----------------------------------------------------------

_original_serialize_exception = getattr(
    odoo.http.serialize_exception, "__wrapped__", odoo.http.serialize_exception
)


def serialize_exception(
    exception: BaseException,
    *,
    message: str | None = None,
    arguments: Sequence[object] | None = None,
) -> dict[str, Any]:
    """odoo.http.serialize_exception without the traceback outside dev mode."""
    data: dict[str, Any] = _original_serialize_exception(
        exception, message=message, arguments=arguments
    )
    return redact_error_data(data)


# Sets serialize_exception.__wrapped__ only (name/doc/module stay ours).
functools.update_wrapper(
    serialize_exception, _original_serialize_exception, assigned=(), updated=()
)

# The dispatcher registered for routing_type "jsonrpc" when this module loads.
_JsonRPCDispatcher: Any = odoo.http._dispatchers["jsonrpc"]


class HardenedJsonRPCDispatcher(_JsonRPCDispatcher):
    """The JSON-RPC dispatcher with its error payload redacted.

    Declaring the same routing_type re-registers the class in
    odoo.http._dispatchers (Dispatcher.__init_subclass__), the supported way
    to specialise a dispatcher.
    """

    routing_type = "jsonrpc"

    def _response(self, result: object = None, error: object = None) -> Any:
        if isinstance(error, dict) and "data" in error:
            error = {**error, "data": redact_error_data(error["data"])}
        return super()._response(result=result, error=error)


# --- XML-RPC ----------------------------------------------------------------------


def _application_fault_int(exc: BaseException) -> xmlrpc.client.Fault:
    """/xmlrpc/2: keep the application-error code and the exception line."""
    message = "".join(traceback.format_exception_only(exc)).strip()
    return xmlrpc.client.Fault(1, message)  # RPC_FAULT_CODE_APPLICATION_ERROR


def _application_fault_string(exc: BaseException) -> xmlrpc.client.Fault:
    """/xmlrpc (legacy): the message stays the faultCode, the traceback goes."""
    return xmlrpc.client.Fault(exception_to_unicode(exc), "")


class _HardenedFaultBuilder:
    """An rpc fault builder that redacts the traceback outside dev mode.

    The stock builder stays reachable as ``__wrapped__``; ``_fix_hardened``
    marks the patch so re-installing it never double-wraps.
    """

    _fix_hardened = True

    def __init__(
        self,
        module: ModuleType,
        original: FaultBuilder,
        application_fault: Callable[[BaseException], xmlrpc.client.Fault],
    ) -> None:
        self.__wrapped__ = original
        self._module = module
        self._application_fault = application_fault

    def __call__(self, exc: BaseException) -> str:
        if tracebacks_exposed() or isinstance(exc, _KNOWN_RPC_ERRORS):
            return self.__wrapped__(exc)
        wire: str = self._module.dumps(self._application_fault(exc))
        return wire


def _harden_fault_builder(
    module: ModuleType,
    name: str,
    application_fault: Callable[[BaseException], xmlrpc.client.Fault],
) -> FaultBuilder:
    """Wrap one of the rpc addon's fault builders (idempotent)."""
    current: FaultBuilder = getattr(module, name)
    if getattr(current, "_fix_hardened", False):
        return current
    original: FaultBuilder = getattr(current, "__wrapped__", current)
    builder = _HardenedFaultBuilder(module, original, application_fault)
    setattr(module, name, builder)
    return builder


def _install_xmlrpc() -> bool:
    """Route the XML-RPC fault builders through the redacting wrappers.

    The /xmlrpc and /xmlrpc/2 routes resolve them as module globals at call
    time. Returns False when the rpc addon is not on the addons path.
    """
    try:
        module = importlib.import_module(_XMLRPC_MODULE)
    except ImportError:
        _logger.warning("http_hardening: rpc addon not importable, XML-RPC faults unpatched")
        return False
    _harden_fault_builder(module, "xmlrpc_handle_exception_int", _application_fault_int)
    _harden_fault_builder(module, "xmlrpc_handle_exception_string", _application_fault_string)
    return True


# --- installation -------------------------------------------------------------------


def install() -> None:
    """Apply every patch; idempotent (safe on re-import and server-wide load).

    The dispatcher subclass registers itself at import.
    """
    if odoo.http.serialize_exception is not serialize_exception:
        odoo.http.serialize_exception = serialize_exception
    ir_cron = importlib.import_module(_IR_CRON_MODULE)
    if ir_cron.serialize_exception is not serialize_exception:
        # ir_cron bound the serializer by name at import: rebind the global.
        vars(ir_cron)["serialize_exception"] = serialize_exception
    _install_xmlrpc()
    _logger.debug("http_hardening: RPC error tracebacks redacted outside dev mode")


install()
