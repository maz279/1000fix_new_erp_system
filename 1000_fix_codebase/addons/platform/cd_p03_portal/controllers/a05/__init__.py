# A05 · Circular Economy — per-module workspace surfaces, report packs and
# KPI payloads (rental, trade-in, e-waste). Same shape as controllers/a04.
from odoo import http
from odoo.http import request

from ..p03_service_order_api import _require_internal
from . import m13, m14, m18

MODULES = {
    "M13": m13,
    "M14": m14,
    "M18": m18,
}

SURFACES = {}
for _mod in MODULES.values():
    for _model, _conf in _mod.SURFACES.items():
        if _model in SURFACES:
            raise ValueError("A05 surface %s is declared by two modules" % _model)
        SURFACES[_model] = _conf


def kpis(env, module=None):
    """One payload for the A05 module home: every figure is a live read."""
    if module in (None, "M13"):
        return {"M13": m13.kpis(env)}
    if module in ("M14",):
        return {"M14": m14.kpis(env)}
    if module in ("M18",):
        return {"M18": m18.kpis(env)}
    return {}


class P03CircularApi(http.Controller):
    @http.route("/p03/circular/kpis", type="jsonrpc", auth="user", readonly=True)
    def circular_kpis(self, module=None, **kw):
        _require_internal(request.env)
        return kpis(request.env, module)
