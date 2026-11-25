# A12 · Platform & Technology — per-module workspace surfaces and KPIs.
from odoo import http
from odoo.http import request

from ..p03_service_order_api import _require_internal
from . import m28, m29, m30, m64, m65, m66, m67

MODULES = {
    "M28": m28,
    "M29": m29,
    "M30": m30,
    "M64": m64,
    "M65": m65,
    "M66": m66,
    "M67": m67,
}

SURFACES = {}
for _mod in MODULES.values():
    for _model, _conf in _mod.SURFACES.items():
        if _model in SURFACES:
            raise ValueError("A12 surface %s is declared by two modules" % _model)
        SURFACES[_model] = _conf

# A12 workflow audit (2026-11-04) R4: no A12 surface declared what
# /p03/model/write may set, so the form endpoint wrote any non-readonly field
# it was sent - a ticket's state, an access request's decision, a ladder's
# in_force flag. Each mNN module owns the whitelist for its own surfaces in
# its module-level WRITABLE dict (same shape as controllers/a06/writable.py,
# per-module so no builder edits another builder's file); the merge here
# applies it. test_a12_write_whitelist.py fails while any surface is missing.
WRITABLE = {}
for _mod in MODULES.values():
    _module_writable = getattr(_mod, "WRITABLE", {})
    for _model, _fields in _module_writable.items():
        if _model in WRITABLE:
            raise ValueError("A12 writable %s is declared by two modules" % _model)
        WRITABLE[_model] = _fields
for _model, _conf in SURFACES.items():
    if _model in WRITABLE:
        _conf["writable"] = WRITABLE[_model]


KPIS = {
    "M28": m28.kpis,
    "M29": m29.kpis,
    "M30": m30.kpis,
    "M64": m64.kpis,
    "M65": m65.kpis,
    "M66": m66.kpis,
    "M67": m67.kpis,
}


def kpis(env, module=None):
    out = {}
    for code, fn in KPIS.items():
        if module in (None, code):
            out[code] = fn(env)
    return out


class P03PlatformApi(http.Controller):
    @http.route("/p03/platform/kpis", type="jsonrpc", auth="user", readonly=True)
    def platform_kpis(self, module=None, **kw):
        _require_internal(request.env)
        return kpis(request.env, module)

    @http.route("/p03/security/kpis", type="jsonrpc", auth="user", readonly=True)
    def security_kpis(self, **kw):
        # The workspace reads res[<module code>], so the payload is keyed by it.
        _require_internal(request.env)
        return {"M29": m29.kpis(request.env)}
