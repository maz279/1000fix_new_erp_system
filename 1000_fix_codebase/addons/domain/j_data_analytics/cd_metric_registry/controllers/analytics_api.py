# P06 Analytics & Executive API — the W4 contract endpoints (PP5).
#
# Two halves:
#   /analytics/dashboards — the dashboard registry with the embedded-BI
#     seam: embed URLs come from ir.config_parameter ONLY (never source
#     literals — the Superset/Grafana endpoint is deployment config).
#     No data crosses this seam; the BI tool queries the warehouse.
#   /analytics/kpis — read_group aggregations over the real business
#     models (service orders, warranty claims). The portal layer holds
#     NO data and computes NOTHING (AS-09); it renders backend numbers.
from odoo import http
from odoo.http import request

import json

# The dashboard registry (R5): which dashboards exist, for whom, in
# which area. Static BY DESIGN — it is navigation, not data; it mirrors
# the M25 groups in contracts/nav/registry.json.
DASHBOARDS = [
    {"id": "executive", "area": "A11", "en": "Executive Overview",
     "bn": "এক্সিকিউটিভ ওভারভিউ",
     "audience": "executive", "embed_key": "fix_bi_embed_executive"},
    {"id": "branch", "area": "A11", "en": "Branch Performance",
     "bn": "ব্রাঞ্চ পারফরম্যান্স",
     "audience": "executive", "embed_key": "fix_bi_embed_branch"},
    {"id": "technician", "area": "A11", "en": "Technician Performance",
     "bn": "টেকনিশিয়ান পারফরম্যান্স",
     "audience": "manager", "embed_key": "fix_bi_embed_technician"},
    {"id": "finance", "area": "A11", "en": "Finance",
     "bn": "ফাইন্যান্স",
     "audience": "finance", "embed_key": "fix_bi_embed_finance"},
    {"id": "warranty", "area": "A11", "en": "Warranty & Claims",
     "bn": "ওয়ারেন্টি ও দাবি",
     "audience": "brand", "embed_key": "fix_bi_embed_warranty"},
]


class AnalyticsApiController(http.Controller):
    """The P06 analytics portal API (W4 contract)."""

    @http.route("/analytics/dashboards", type="json", auth="user",
                readonly=True)
    def dashboards(self, **kwargs):
        """The dashboard registry with the embedded-BI seam. An embed URL
        appears only when the deployment configured one (ir.config_parameter
        per dashboard); without it the KPI surface below serves the same
        area. The portal NEVER invents an embed host."""
        params = request.env["ir.config_parameter"].sudo()
        result = []
        for d in DASHBOARDS:
            embed_url = params.get_param(d["embed_key"])
            result.append({
                "id": d["id"],
                "area": d["area"],
                "title_en": d["en"],
                "title_bn": d["bn"],
                "audience": d["audience"],
                "embed_available": bool(embed_url),
                # None (not "") when unconfigured — the portal shows the
                # native KPI view instead of a broken frame
                "embed_url": embed_url or None,
            })
        return {"dashboards": result, "total": len(result)}

    @http.route("/analytics/kpis", type="json", auth="user", readonly=True)
    def kpis(self, **kwargs):
        """Backend-computed KPIs for a dashboard area (read_group over the
        real models — no snapshot tables, no portal-side math).

        executive/branch/technician: service-order aggregations (M01).
        warranty: claim-state aggregations (M09).
        finance: the AR/AP posture rides the BI embed (Superset owns the
          ledger joins); the native view serves order-linked signals only.
        """
        dashboard = kwargs.get("dashboard", "executive")
        valid = {d["id"] for d in DASHBOARDS}
        if dashboard not in valid:
            return {"error": {"code": "invalid_dashboard",
                              "message": "dashboard must be one of %s"
                                         % ", ".join(sorted(valid))}}
        order_groups = request.env["fix.service.order"].read_group(
            [], ["id:count(id)"], ["state"], lazy=False)
        by_state = {g["state"]: g["id"] for g in order_groups}
        result = {
            "dashboard": dashboard,
            "orders_by_state": by_state,
            "orders_total": sum(by_state.values()),
        }
        if dashboard in ("branch", "technician"):
            field = "branch_id" if dashboard == "branch" else "technician_id"
            groups = request.env["fix.service.order"].read_group(
                [], ["id:count(id)"], [field], lazy=False)
            result["breakdown"] = [
                {"name": g[field][1] if g[field] else "(unassigned)",
                 "open": g["id"]}
                for g in groups]
        if dashboard == "warranty":
            claim_groups = request.env["fix.warranty.claim"].read_group(
                [], ["id:count(id)"], ["state"], lazy=False)
            result["claims_by_state"] = {g["state"]: g["id"]
                                         for g in claim_groups}
        return {"kpis": result}
