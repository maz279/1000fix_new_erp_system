# A09 · People & Workforce — per-module workspace surfaces and KPI payload.
from odoo import http
from odoo.exceptions import AccessError
from odoo.http import request

from ..p03_service_order_api import _require_internal
from . import m21, m22, m55, m56, m57, m58, m59
from .writable import WRITABLE

MODULES = {
    "M21": m21,
    "M55": m55,
    "M56": m56,
    "M57": m57,
    "M22": m22,
    "M58": m58,
    "M59": m59,
}

SURFACES = {}
for _mod in MODULES.values():
    for _model, _conf in _mod.SURFACES.items():
        if _model in SURFACES:
            raise ValueError("A09 surface %s is declared by two modules" % _model)
        # A09 audit M21-5: the workspace read every list and form with sudo,
        # so a plain user saw contracts the record rules hide and another
        # company's employees. People data is read under the caller's own
        # record rules (p03_generic_api honours "rules").
        SURFACES[_model] = {**_conf, "rules": True}

# B1 (A09 workflow audit): every A09 surface declares what /p03/model/write
# may set on it, generated from the workspace forms (form_fields.py --a09).
for _model, _conf in SURFACES.items():
    _conf["writable"] = WRITABLE[_model]


def _module_kpis(env, mod):
    # KPIs are computed as the caller (A09 audit A6): a figure built from
    # records the caller may not read is withheld, not computed with sudo.
    try:
        return mod.kpis(env)
    except AccessError:
        return {}


def kpis(env, module=None):
    if module:
        mod = MODULES.get(module)
        return {module: _module_kpis(env, mod)} if mod else {}
    return {code: _module_kpis(env, mod) for code, mod in MODULES.items()}


class P03PeopleApi(http.Controller):
    @http.route("/p03/people/kpis", type="jsonrpc", auth="user", readonly=True)
    def people_kpis(self, module=None, **kw):
        _require_internal(request.env)
        return kpis(request.env, module)
