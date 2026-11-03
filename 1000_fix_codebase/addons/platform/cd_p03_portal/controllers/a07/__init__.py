# A07 · Assets & Facilities — per-module workspace surfaces and KPI payload.
from odoo import http
from odoo.http import request

from ..p03_service_order_api import _require_internal
from . import m17, m45, m46, m47, m48
from .writable import WRITABLE

MODULES = {
    "M17": m17,
    "M45": m45,
    "M46": m46,
    "M47": m47,
    "M48": m48,
}

SURFACES = {}
for _mod in MODULES.values():
    for _model, _conf in _mod.SURFACES.items():
        if _model in SURFACES:
            raise ValueError("A07 surface %s is declared by two modules" % _model)
        SURFACES[_model] = _conf

# A07 workflow audit (2026-11-03) D1: no A07 surface declared what
# /p03/model/write may set, so the form endpoint wrote any non-readonly field
# it was sent - a work order's state, a calibration's result, a consent's
# state. Generated from the workspace forms (form_fields.py --a07).
for _model, _conf in SURFACES.items():
    _conf["writable"] = WRITABLE[_model]


def kpis(env, module=None):
    if module in (None, "M17"):
        return {"M17": m17.kpis(env)}
    if module in ("M45",):
        return {"M45": m45.kpis(env)}
    if module in ("M46",):
        return {"M46": m46.kpis(env)}
    if module in ("M47",):
        return {"M47": m47.kpis(env)}
    if module in ("M48",):
        return {"M48": m48.kpis(env)}
    return {}


class P03AssetApi(http.Controller):
    @http.route("/p03/asset/kpis", type="jsonrpc", auth="user", readonly=True)
    def asset_kpis(self, module=None, **kw):
        _require_internal(request.env)
        return kpis(request.env, module)
