# A10 · Governance, Risk & Quality — per-module workspace surfaces and KPIs.
from odoo import http
from odoo.http import request

from ..p03_service_order_api import _require_internal
from . import m23, m24, m60, m61
from .writable import WRITABLE

MODULES = {
    "M23": m23,
    "M60": m60,
    "M24": m24,
    "M61": m61,
}

SURFACES = {}
for _mod in MODULES.values():
    for _model, _conf in _mod.SURFACES.items():
        if _model in SURFACES:
            raise ValueError("A10 surface %s is declared by two modules" % _model)
        # R1: a surface accepts exactly the fields its workspace forms offer
        # as editable (generated; a KeyError here means the map is stale —
        # regenerate controllers/a10/writable.py).
        _conf["writable"] = WRITABLE[_model]
        SURFACES[_model] = _conf


def kpis(env, module=None):
    if module in (None, "M23"):
        return {"M23": m23.kpis(env)}
    if module in ("M60",):
        return {"M60": m60.kpis(env)}
    if module in ("M24",):
        return {"M24": m24.kpis(env)}
    if module in ("M61",):
        return {"M61": m61.kpis(env)}
    return {}


class P03GovernanceApi(http.Controller):
    @http.route("/p03/grc/kpis", type="jsonrpc", auth="user", readonly=True)
    def grc_kpis(self, module=None, **kw):
        _require_internal(request.env)
        return kpis(request.env, module)
