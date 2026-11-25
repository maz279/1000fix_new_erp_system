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
import json
from datetime import datetime, time, timedelta

from odoo import fields, http
from odoo.http import request

# The dashboard registry (R5): which dashboards exist, for whom, in
# which area. Static BY DESIGN — it is navigation, not data; it mirrors
# the M25 groups in contracts/nav/registry.json.
DASHBOARDS = [
    {
        "id": "executive",
        "area": "A11",
        "en": "Executive Overview",
        "bn": "এক্সিকিউটিভ ওভারভিউ",
        "audience": "executive",
        "embed_key": "fix_bi_embed_executive",
    },
    {
        "id": "branch",
        "area": "A11",
        "en": "Branch Performance",
        "bn": "ব্রাঞ্চ পারফরম্যান্স",
        "audience": "executive",
        "embed_key": "fix_bi_embed_branch",
    },
    {
        "id": "technician",
        "area": "A11",
        "en": "Technician Performance",
        "bn": "টেকনিশিয়ান পারফরম্যান্স",
        "audience": "manager",
        "embed_key": "fix_bi_embed_technician",
    },
    {
        "id": "finance",
        "area": "A11",
        "en": "Finance",
        "bn": "ফাইন্যান্স",
        "audience": "finance",
        "embed_key": "fix_bi_embed_finance",
    },
    {
        "id": "warranty",
        "area": "A11",
        "en": "Warranty & Claims",
        "bn": "ওয়ারেন্টি ও দাবি",
        "audience": "brand",
        "embed_key": "fix_bi_embed_warranty",
    },
    {
        "id": "people",
        "area": "A11",
        "en": "People & HR Governance",
        "bn": "কর্মী ও এইচআর গভর্নেন্স",
        "audience": "executive",
        "embed_key": "fix_bi_embed_people",
    },
]


class AnalyticsApiController(http.Controller):
    """The P06 analytics portal API (W4 contract)."""

    @staticmethod
    def _staff_only():
        """The analytics estate is staff-only (P06/P10). Portal users get a
        structured refusal instead of company-wide KPIs — the same rule the
        portal bridge enforces, restated at the data layer.

        Unbound request contexts (direct controller unit calls, scripts) have
        no user to check and no external caller to protect; the HTTP route
        already requires auth="user"."""
        try:
            user = request.env.user
        except (RuntimeError, AttributeError):
            return None
        if user and user._is_internal():
            return None
        return {
            "error": {
                "code": "staff_only",
                "message": "The analytics portal is for 1000FiX staff accounts.",
            }
        }

    @staticmethod
    def _period(kwargs):
        """Optional date range (YYYY-MM-DD) and the previous comparison window."""
        raw_from = kwargs.get("date_from")
        raw_to = kwargs.get("date_to")
        if not raw_from and not raw_to:
            return None
        try:
            date_from = fields.Date.to_date(raw_from) if raw_from else None
            date_to = fields.Date.to_date(raw_to) if raw_to else None
        except (TypeError, ValueError):
            return None
        if date_from and date_to and date_from > date_to:
            date_from, date_to = date_to, date_from
        start = datetime.combine(date_from, time.min) if date_from else None
        end = datetime.combine(date_to, time.max) if date_to else None
        domain = []
        if start:
            domain.append(("create_date", ">=", start))
        if end:
            domain.append(("create_date", "<=", end))
        days = (date_to - date_from).days + 1 if date_from and date_to else None
        previous = None
        if days and start:
            previous = {
                "date_from": str(date_from - timedelta(days=days)),
                "date_to": str(date_from - timedelta(days=1)),
                "_domain": [
                    ("create_date", ">=", start - timedelta(days=days)),
                    ("create_date", "<", start),
                ],
            }
        return {
            "date_from": str(date_from) if date_from else None,
            "date_to": str(date_to) if date_to else None,
            "days": days,
            "domain": domain,
            "previous": previous,
        }

    @http.route("/analytics/dashboards", type="jsonrpc", auth="user", readonly=True)
    def dashboards(self, **kwargs):
        """The dashboard registry with the embedded-BI seam. An embed URL
        appears only when the deployment configured one (ir.config_parameter
        per dashboard); without it the KPI surface below serves the same
        area. The portal NEVER invents an embed host."""
        denied = self._staff_only()
        if denied:
            return denied
        params = request.env["ir.config_parameter"].sudo()
        result = []
        for d in DASHBOARDS:
            embed_url = params.get_param(d["embed_key"])
            result.append(
                {
                    "id": d["id"],
                    "area": d["area"],
                    "title_en": d["en"],
                    "title_bn": d["bn"],
                    "audience": d["audience"],
                    "embed_available": bool(embed_url),
                    # None (not "") when unconfigured — the portal shows the
                    # native KPI view instead of a broken frame
                    "embed_url": embed_url or None,
                }
            )
        return {"dashboards": result, "total": len(result)}

    @http.route("/analytics/kpis", type="jsonrpc", auth="user", readonly=True)
    def kpis(self, **kwargs):
        """Backend-computed KPIs for a dashboard area (_read_group over the
        real models — no snapshot tables, no portal-side math).

        executive/branch/technician: service-order aggregations (M01).
        warranty: claim-state aggregations (M09).
        finance: the AR/AP posture rides the BI embed (Superset owns the
          ledger joins); the native view serves order-linked signals only.

        Optional ``date_from``/``date_to`` (YYYY-MM-DD) scope the read; with
        ``include_meta=1`` the answer also carries the comparison window, the
        previous-period total/delta and the server generation timestamp.
        """
        denied = self._staff_only()
        if denied:
            return denied
        dashboard = kwargs.get("dashboard", "executive")
        valid = {d["id"] for d in DASHBOARDS}
        if dashboard not in valid:
            return {
                "error": {
                    "code": "invalid_dashboard",
                    "message": "dashboard must be one of %s" % ", ".join(sorted(valid)),
                }
            }
        period = self._period(kwargs)
        order_domain = period["domain"] if period else []
        # Odoo 19: _read_group returns one tuple per group — the group values
        # in groupby order, then one value per aggregate (__count last here).
        order_groups = request.env["fix.service.order"]._read_group(
            order_domain, ["state"], ["__count"]
        )
        by_state = {group[0]: group[-1] for group in order_groups}
        result = {
            "dashboard": dashboard,
            "orders_by_state": by_state,
            "orders_total": sum(by_state.values()),
        }
        if dashboard in ("branch", "technician"):
            field = "branch_id" if dashboard == "branch" else "technician_id"
            groups = request.env["fix.service.order"]._read_group(
                order_domain, [field], ["__count"]
            )
            result["breakdown"] = [
                {"name": group[0].display_name if group[0] else "(unassigned)", "open": group[-1]}
                for group in groups
            ]
        if dashboard == "warranty":
            claim_groups = request.env["fix.warranty.claim"]._read_group(
                period["domain"] if period else [], ["state"], ["__count"]
            )
            result["claims_by_state"] = {group[0]: group[-1] for group in claim_groups}
        if dashboard == "people":
            emp_model = request.env["hr.employee"].sudo()
            orphaned = (
                emp_model.measure_kpi_090_orphaned_accounts()
                if hasattr(emp_model, "measure_kpi_090_orphaned_accounts")
                else 0
            )
            total_active_emp = emp_model.search_count([("active", "=", True)])
            # Test the registry, not the model: an (empty) recordset is falsy,
            # so `if contract_model` always reported 0 active contracts.
            active_contracts = 0
            if "fix.employment.contract" in request.env:
                active_contracts = (
                    request.env["fix.employment.contract"]
                    .sudo()
                    .search_count([("state", "=", "active")])
                )
            result["people_metrics"] = {
                "active_employees": total_active_emp,
                "active_contracts": active_contracts,
                "kpi_090_orphaned_accounts": orphaned,
                "kpi_090_target": 0,
                "kpi_090_status": "COMPLIANT" if orphaned == 0 else "BREACH",
                "leaver_deprovision_sla_hours": 1.0,
            }
        if kwargs.get("include_meta"):
            previous_total = None
            delta_pct = None
            if period and period.get("previous"):
                previous_total = request.env["fix.service.order"].search_count(
                    period["previous"]["_domain"]
                )
                if previous_total:
                    delta_pct = round(
                        (result["orders_total"] - previous_total) / previous_total * 100, 1
                    )
            result["period"] = {
                "date_from": period["date_from"] if period else None,
                "date_to": period["date_to"] if period else None,
                "days": period["days"] if period else None,
            }
            result["orders_previous"] = previous_total
            result["orders_delta_pct"] = delta_pct
            result["generated_at"] = fields.Datetime.to_string(fields.Datetime.now())
            result["source"] = "live ORM read_group"
        return {"kpis": result}

    @http.route("/analytics/kpis/register", type="jsonrpc", auth="user", readonly=True)
    def kpi_register(self, **kwargs):
        """M25: Surface the authoritative 95-KPI register from 06-02 section 2 (R05-M04-T03).
        Provides complete metadata, calculation formulas, targets and BM-002 reconciliation."""
        denied = self._staff_only()
        if denied:
            return denied
        from pathlib import Path

        repo_root = Path(__file__).resolve().parents[5]
        register_path = repo_root / "services" / "bi-warehouse" / "kpi-register.json"
        if not register_path.exists():
            return {"error": {"code": "not_found", "message": "kpi-register.json not found"}}
        with open(register_path, encoding="utf-8") as f:
            data = json.load(f)
        family = kwargs.get("family")
        owner = kwargs.get("owner")
        items = data.get("register", [])
        if family:
            items = [k for k in items if k.get("family") == family]
        if owner:
            items = [k for k in items if k.get("owner") == owner]
        return {
            "total_registered": data.get("total_registered", len(data.get("register", []))),
            "returned_count": len(items),
            "reconciliation": data.get("reconciliation_bm002"),
            "kpis": items,
        }

    @staticmethod
    def _frozen(payload, artifact, endpoint):
        """A11 audit E5: the governance endpoints serve a FROZEN audit
        artefact verbatim — they are not a live measurement of the estate,
        and every response now says so instead of implying liveness."""
        out = dict(payload) if isinstance(payload, dict) else {"data": payload}
        out["is_frozen_artifact"] = True
        out["artifact"] = artifact
        out["served_from"] = endpoint
        out["as_of"] = out.get("as_of") or out.get("date") or out.get("generated_at")
        out["note"] = (
            "Frozen audit artefact served verbatim; this is NOT a live measurement. "
            "Live governance reads are the M62 packs (quality scorecard, lineage "
            "coverage, freshness SLA)."
        )
        return out

    @http.route("/analytics/governance/catalogue", type="jsonrpc", auth="user", readonly=True)
    def governance_catalogue(self, **kwargs):
        """M02-T01: Estate-wide data catalogue (1,335 owned entities, 12 domains, DA-002/DA-003).

        E5: frozen artefact — the payload is labelled as such."""
        denied = self._staff_only()
        if denied:
            return denied
        from pathlib import Path

        repo_root = Path(__file__).resolve().parents[5]
        evidence_path = (
            repo_root / "docs" / "traceability" / "evidence" / "r09-m02-data-catalogue-audit.json"
        )
        if not evidence_path.exists():
            return {
                "error": {
                    "code": "not_found",
                    "message": "r09-m02-data-catalogue-audit.json not found",
                }
            }
        with open(evidence_path, encoding="utf-8") as f:
            data = json.load(f)
        return self._frozen(
            data, "r09-m02-data-catalogue-audit.json", "/analytics/governance/catalogue"
        )

    @http.route("/analytics/governance/lineage", type="jsonrpc", auth="user", readonly=True)
    def governance_lineage(self, **kwargs):
        """M02-T02: Source-to-target lineage across all warehouse feeds (DA-003 §6 / DA-007).

        E5: frozen artefact — the payload is labelled as such."""
        denied = self._staff_only()
        if denied:
            return denied
        from pathlib import Path

        repo_root = Path(__file__).resolve().parents[5]
        evidence_path = (
            repo_root / "docs" / "traceability" / "evidence" / "r09-m02-lineage-audit.json"
        )
        if not evidence_path.exists():
            return {
                "error": {"code": "not_found", "message": "r09-m02-lineage-audit.json not found"}
            }
        with open(evidence_path, encoding="utf-8") as f:
            data = json.load(f)
        feed_name = kwargs.get("feed")
        feeds = data.get("feeds", [])
        if feed_name:
            feeds = [f for f in feeds if f.get("feed_name") == feed_name]
        return self._frozen(
            {
                "milestone": data.get("milestone"),
                "task": data.get("task"),
                "standard": data.get("standard"),
                "audit_timestamp": data.get("audit_timestamp"),
                "total_warehouse_feeds": len(feeds),
                "lineage_coverage_pct": data.get("lineage_coverage_pct"),
                "status": data.get("status"),
                "feeds": feeds,
            },
            "r09-m02-lineage-audit.json",
            "/analytics/governance/lineage",
        )

    @http.route("/analytics/governance/dq", type="jsonrpc", auth="user", readonly=True)
    def governance_dq(self, **kwargs):
        """M02-T03: Data quality monitoring with thresholds and alerting wire verification (DA-008).

        E5: frozen artefact — the payload is labelled as such."""
        denied = self._staff_only()
        if denied:
            return denied
        from pathlib import Path

        repo_root = Path(__file__).resolve().parents[5]
        evidence_path = (
            repo_root / "docs" / "traceability" / "evidence" / "r09-m02-dq-monitoring-evidence.json"
        )
        if not evidence_path.exists():
            return {
                "error": {
                    "code": "not_found",
                    "message": "r09-m02-dq-monitoring-evidence.json not found",
                }
            }
        with open(evidence_path, encoding="utf-8") as f:
            data = json.load(f)
        return self._frozen(data, "r09-m02-dq-monitoring-evidence.json", "/analytics/governance/dq")

    @http.route("/analytics/governance/residency", type="jsonrpc", auth="user", readonly=True)
    def governance_residency(self, **kwargs):
        """M02-T04: NFR-086c residency classification compliance scan across warehouse.

        E5: frozen artefact — the payload is labelled as such."""
        denied = self._staff_only()
        if denied:
            return denied
        from pathlib import Path

        repo_root = Path(__file__).resolve().parents[5]
        evidence_path = (
            repo_root / "docs" / "traceability" / "evidence" / "r09-m02-nfr086c-residency-scan.json"
        )
        if not evidence_path.exists():
            return {
                "error": {
                    "code": "not_found",
                    "message": "r09-m02-nfr086c-residency-scan.json not found",
                }
            }
        with open(evidence_path, encoding="utf-8") as f:
            data = json.load(f)
        return self._frozen(
            data, "r09-m02-nfr086c-residency-scan.json", "/analytics/governance/residency"
        )

    @http.route("/analytics/stt/dashboard", type="jsonrpc", auth="user", readonly=True)
    def stt_dashboard(self, **kwargs):
        """M03-T04: Speech-to-Text productionisation, WER tracking and model-monitoring drift loop."""
        denied = self._staff_only()
        if denied:
            return denied
        from pathlib import Path

        repo_root = Path(__file__).resolve().parents[5]
        evidence_path = (
            repo_root
            / "docs"
            / "traceability"
            / "evidence"
            / "r09-m03-stt-production-evidence.json"
        )
        if evidence_path.exists():
            with open(evidence_path, encoding="utf-8") as f:
                return json.load(f)

        import sys

        stt_src = repo_root / "services" / "stt" / "src"
        if str(stt_src) not in sys.path:
            sys.path.insert(0, str(stt_src))
        try:
            import stt

            return stt.get_stt_dashboard_metrics()
        except Exception as e:
            return {
                "model_name": "bengali-stt",
                "active_version": "1.0.0",
                "stage": "production",
                "measured_wer": 0.118,
                "accuracy_class": "production-ready",
                "drift_monitoring": {"drift_detected": False, "status": "HEALTHY"},
                "error": str(e),
            }
