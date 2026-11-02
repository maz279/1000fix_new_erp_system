# A09 · People & Workforce — per-module workspace surfaces and KPI payload.
from odoo import http
from odoo.http import request

from ..p03_service_order_api import _require_internal
from . import m21, m22, m55, m56, m57, m58, m59

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
        SURFACES[_model] = _conf


def kpis(env, module=None):
    if module:
        mod = MODULES.get(module)
        return {module: mod.kpis(env)} if mod else {}
    return {code: mod.kpis(env) for code, mod in MODULES.items()}


class P03PeopleApi(http.Controller):
    @http.route("/p03/people/kpis", type="jsonrpc", auth="user", readonly=True)
    def people_kpis(self, module=None, **kw):
        _require_internal(request.env)
        return kpis(request.env, module)
