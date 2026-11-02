# A06 · Supply Chain — per-module workspace surfaces, report packs and KPI
# payloads. Same shape as controllers/a05.
from odoo import http
from odoo.http import request

from ..p03_service_order_api import _require_internal
from . import m15, m16, m41, m42, m43, m44

MODULES = {
    "M15": m15,
    "M16": m16,
    "M41": m41,
    "M42": m42,
    "M43": m43,
    "M44": m44,
}

SURFACES = {}
for _mod in MODULES.values():
    for _model, _conf in _mod.SURFACES.items():
        if _model in SURFACES:
            raise ValueError("A06 surface %s is declared by two modules" % _model)
        SURFACES[_model] = _conf


def kpis(env, module=None):
    if module in (None, "M15"):
        return {"M15": m15.kpis(env)}
    if module in ("M16",):
        return {"M16": m16.kpis(env)}
    if module in ("M41",):
        return {"M41": m41.kpis(env)}
    if module in ("M42",):
        return {"M42": m42.kpis(env)}
    if module in ("M43",):
        return {"M43": m43.kpis(env)}
    if module in ("M44",):
        return {"M44": m44.kpis(env)}
    return {}


class P03SupplyApi(http.Controller):
    @http.route("/p03/supply/kpis", type="jsonrpc", auth="user", readonly=True)
    def supply_kpis(self, module=None, **kw):
        _require_internal(request.env)
        return kpis(request.env, module)
