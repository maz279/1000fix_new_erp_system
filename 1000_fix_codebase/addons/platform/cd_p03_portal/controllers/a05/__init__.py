# A05 · Circular Economy — per-module workspace surfaces, report packs and
# KPI payloads (rental, trade-in, e-waste). Same shape as controllers/a04.
from odoo import http
from odoo.http import request

from ..p03_service_order_api import _require_internal
from . import m13, m14, m18
from .writable import WRITABLE

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

# A05 workflow audit (2026-11-03) D1/E3: no A05 surface declared what
# /p03/model/write may set (24 of 24 models writable, 0 whitelists), so the
# form endpoint wrote a reservation's state, a payout's approval state or an
# ESG value. Generated from the workspace forms (form_fields.py --a05).
for _model, _conf in SURFACES.items():
    _conf["writable"] = WRITABLE[_model]


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
