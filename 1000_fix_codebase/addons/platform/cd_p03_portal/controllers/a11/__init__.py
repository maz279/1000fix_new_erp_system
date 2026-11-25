# A11 · Insights & Intelligence — per-module workspace surfaces, merged so
# the generic endpoints serve exactly what the module files declare (same
# shape as controllers/a02 and controllers/a08). M25/M26 KPIs are served by
# their own controllers (p03_finance_api routes /p03/bi/kpis, /p03/ml/kpis).
from odoo import http
from odoo.http import request

from ..p03_service_order_api import _require_internal
from . import m25, m26, m62, m63

MODULES = {
    "M25": m25,
    "M26": m26,
    "M62": m62,
    "M63": m63,
}

KPIS = {
    "M62": m62.kpis,
    "M63": m63.kpis,
}

SURFACES = {}
for _mod in MODULES.values():
    for _model, _conf in _mod.SURFACES.items():
        if _model in SURFACES:
            raise ValueError("A11 surface %s is declared by two modules" % _model)
        SURFACES[_model] = _conf


def kpis(env, module=None):
    return {code: fn(env) for code, fn in KPIS.items() if module in (None, code)}


class P03WorkflowApi(http.Controller):
    @http.route("/p03/workflow/kpis", type="jsonrpc", auth="user", readonly=True)
    def workflow_kpis(self, module=None, **kw):
        _require_internal(request.env)
        return kpis(request.env, module)

    @http.route("/p03/dataops/kpis", type="jsonrpc", auth="user", readonly=True)
    def dataops_kpis(self, **kw):
        # The workspace reads res[<module code>]; keep the payload keyed by it.
        _require_internal(request.env)
        return {"M62": m62.kpis(request.env)}
