# A02 · M05 Remote Support & MSP — models the generic workspace screens may
# read, the workflow methods they may call, the module KPI payload
# (/p03/msp/kpis) and the built-in reports (/p03/model/report). Same
# contract as a02/m01..m04.
#
# Iteration 2 (2026-10-26): the compliance engines landed in
# cd_msp_contract (runbooks + executions, patch policies + updates, SLA
# credits, on-call rota, maintenance windows, problem & change records),
# so every surface, KPI and report below is LIVE — only backup/restore
# test logging stays an honest absence (it belongs to the M06/M48 seam).
import logging
from datetime import date, datetime

from odoo import http
from odoo.http import request

from ..p03_service_order_api import _require_internal

_logger = logging.getLogger(__name__)

SURFACES = {
    "fix.msp.contract": {
        "order": "id desc",
        "limit": 100,
        "actions": {"action_generate_monthly_report", "action_compute_sla_credits"},
    },
    "fix.monitored.asset": {
        "order": "id desc",
        "limit": 200,
        "actions": set(),
    },
    "fix.msp.alert": {
        "order": "id desc",
        "limit": 200,
        "actions": {
            "action_acknowledge",
            "action_to_ticket",
            "action_resolve",
            "action_escalate",
        },
    },
    "fix.remote.session": {
        "order": "id desc",
        "limit": 200,
        "actions": {"action_start", "action_end"},
    },
    "fix.msp.service.report": {
        "order": "id desc",
        "limit": 100,
        "actions": {"action_generate_bilingual_report"},
    },
    "fix.msp.runbook": {
        "order": "id desc",
        "limit": 100,
        "actions": {"action_execute"},
    },
    "fix.msp.runbook.run": {
        "order": "id desc",
        "limit": 200,
        "actions": {"action_finish"},
    },
    "fix.msp.patch.policy": {
        "order": "id desc",
        "limit": 100,
        "actions": set(),
    },
    "fix.msp.patch.update": {
        "order": "id desc",
        "limit": 200,
        "actions": {"action_approve", "action_install", "action_defer", "action_fail"},
    },
    "fix.msp.sla.credit": {
        "order": "id desc",
        "limit": 100,
        "actions": {"action_approve", "action_apply"},
    },
    "fix.msp.oncall.shift": {
        "order": "start_at desc",
        "limit": 100,
        "actions": {"action_activate", "action_close"},
    },
    "fix.msp.maintenance.window": {
        "order": "start_at desc",
        "limit": 100,
        "actions": {"action_open", "action_close"},
    },
    "fix.msp.change.record": {
        "order": "id desc",
        "limit": 200,
        "actions": {"action_approve", "action_reject", "action_implement", "action_close"},
    },
}


def kpis(env):
    """The M05 module-tile KPI row (registry-canonical metrics) — all six
    measured from the live models since the iteration-2 engines landed."""
    Asset = env["fix.monitored.asset"].sudo()
    Alert = env["fix.msp.alert"].sudo()
    Credit = env["fix.msp.sla.credit"].sudo()
    Patch = env["fix.msp.patch.update"].sudo()
    domain = [("company_id", "in", env.companies.ids)]

    monitored_assets = Asset.search_count(domain)
    open_tickets = Alert.search_count([*domain, ("state", "in", ("acked", "ticketed"))])

    # remote resolution: resolved alerts vs alerts with a ticket
    ticketed = Alert.search([*domain, ("state", "in", ("ticketed", "resolved"))], limit=300)
    resolved = sum(1 for a in ticketed if a.state == "resolved")
    remote_resolution = round(100.0 * resolved / len(ticketed), 1) if ticketed else None

    # SLA credits MTD: committed money (approved + applied) raised this month
    month_start = datetime.combine(date.today().replace(day=1), datetime.min.time())
    credits = Credit.search(
        [
            *domain,
            ("state", "in", ("approved", "applied")),
            ("create_date", ">=", month_start),
        ],
    )
    sla_credits_mtd = round(sum(c.credit_amount for c in credits), 2) if credits else 0.0

    # patch compliance: installed / tracked updates across the estate
    updates = Patch.search(domain, limit=500)
    patch_compliance = (
        round(100.0 * sum(1 for u in updates if u.state == "installed") / len(updates), 1)
        if updates
        else None
    )

    # on-call escalations: alerts escalated beyond first response this month
    oncall_escalations = Alert.search_count(
        [*domain, ("escalated", "=", True), ("create_date", ">=", month_start)]
    )

    return {
        "monitored_assets": monitored_assets,
        "remote_resolution": remote_resolution,
        "open_msp_tickets": open_tickets,
        "sla_credits_mtd": sla_credits_mtd,
        "patch_compliance": patch_compliance,
        "oncall_escalations": oncall_escalations,
    }


# ---------------------------------------------------------------- reports


def _msp(env):
    return env["fix.msp.alert"].sudo().with_context(lang="en_US")


def _sla_by_client_report(env, **params):
    Contract = env["fix.msp.contract"].sudo()
    rows = []
    for msp in Contract.search([]):
        reports = msp.report_ids
        if not reports:
            continue
        avg_sla = sum(r.sla_attainment for r in reports) / len(reports)
        rows.append(
            {
                "client": msp.contract_id.customer_id.name or msp.name,
                "periods": len(reports),
                "avg_attainment_pct": round(avg_sla * 100.0, 1),
                "target_pct": round(msp.sla_target_pct, 1),
                "assets": len(msp.asset_ids),
            }
        )
    return {
        "title": "MSP SLA Attainment by Client",
        "cols": ["client", "periods", "avg_attainment_pct", "target_pct", "assets"],
        "labels": {
            "client": "Client",
            "periods": "Reports",
            "avg_attainment_pct": "Avg SLA %",
            "target_pct": "Target %",
            "assets": "Assets",
        },
        "rows": rows,
        "notes": ["Attainment = resolved/alerts per monthly report; target from the contract."],
    }


def _remote_resolution_report(env, **params):
    Alert = _msp(env)
    alerts = Alert.search([("state", "in", ("ticketed", "resolved"))], limit=300)
    ticketed_n = len(alerts)
    resolved_n = sum(1 for a in alerts if a.state == "resolved")
    rows = [
        {"measure": "Alerts with tickets", "value": ticketed_n},
        {"measure": "Resolved", "value": resolved_n},
        {
            "measure": "Resolution rate %",
            "value": round(100.0 * resolved_n / ticketed_n, 1) if ticketed_n else None,
        },
    ]
    return {
        "title": "Remote Resolution Rate",
        "cols": ["measure", "value"],
        "labels": {"measure": "Measure", "value": "Alerts"},
        "rows": rows,
        "notes": ["Alert-to-ticket-to-resolved funnel, live."],
    }


def _alert_conversion_report(env, **params):
    Alert = _msp(env)
    by_state = {}
    for a in Alert.search([], limit=300):
        by_state[a.state] = by_state.get(a.state, 0) + 1
    rows = [{"state": s, "alerts": n} for s, n in sorted(by_state.items())]
    return {
        "title": "Alert-to-Ticket Conversion",
        "cols": ["state", "alerts"],
        "labels": {"state": "Alert State", "alerts": "Alerts"},
        "rows": rows,
        "notes": ["Live alert-state funnel (new → acked → ticketed → resolved)."],
    }


def _estate_health_report(env, **params):
    """Health scoring, measured: per contract the asset mix plus the average
    health score (100 healthy / 50 degraded / 0 offline, minus 5 per open
    alert)."""
    Asset = env["fix.monitored.asset"].sudo()
    assets = Asset.search([("company_id", "in", env.companies.ids)], limit=500)
    if not assets:
        return {
            "title": "Estate Health Scoring",
            "cols": ["note"],
            "labels": {"note": ""},
            "rows": [{"note": "No monitored assets yet — score the estate after onboarding."}],
            "notes": ["Health score = 100/50/0 by state, minus 5 per open alert."],
        }
    by_contract = {}
    for a in assets:
        key = a.msp_contract_id.name or "—"
        by_contract.setdefault(key, []).append(a)
    rows = []
    for contract, group in sorted(by_contract.items()):
        scores = [a.health_score for a in group]
        rows.append(
            {
                "contract": contract,
                "assets": len(group),
                "healthy": sum(1 for a in group if a.health == "healthy"),
                "degraded": sum(1 for a in group if a.health == "degraded"),
                "offline": sum(1 for a in group if a.health == "offline"),
                "avg_score": round(sum(scores) / len(scores), 1),
            }
        )
    return {
        "title": "Estate Health Scoring",
        "cols": ["contract", "assets", "healthy", "degraded", "offline", "avg_score"],
        "labels": {
            "contract": "Contract",
            "assets": "Assets",
            "healthy": "Healthy",
            "degraded": "Degraded",
            "offline": "Offline",
            "avg_score": "Avg Score",
        },
        "rows": rows,
        "notes": ["Health score = 100/50/0 by state, minus 5 per open alert."],
    }


def _patch_compliance_report(env, **params):
    Patch = env["fix.msp.patch.update"].sudo()
    updates = Patch.search([("company_id", "in", env.companies.ids)], limit=500)
    if not updates:
        return {
            "title": "Patch Compliance Report",
            "cols": ["note"],
            "labels": {"note": ""},
            "rows": [
                {"note": "No patch updates tracked yet — the register fills as patches land."}
            ],
            "notes": ["Compliance = installed / tracked updates, live."],
        }
    by_contract = {}
    for u in updates:
        by_contract.setdefault(u.msp_contract_id.name or "—", []).append(u)
    rows = []
    for contract, group in sorted(by_contract.items()):
        installed = sum(1 for u in group if u.state == "installed")
        rows.append(
            {
                "contract": contract,
                "tracked": len(group),
                "installed": installed,
                "missing": sum(1 for u in group if u.state in ("missing", "approved")),
                "failed": sum(1 for u in group if u.state == "failed"),
                "compliance_pct": round(100.0 * installed / len(group), 1),
            }
        )
    return {
        "title": "Patch Compliance Report",
        "cols": ["contract", "tracked", "installed", "missing", "failed", "compliance_pct"],
        "labels": {
            "contract": "Contract",
            "tracked": "Tracked",
            "installed": "Installed",
            "missing": "Missing",
            "failed": "Failed",
            "compliance_pct": "Compliance %",
        },
        "rows": rows,
        "notes": ["Compliance = installed / tracked updates, live."],
    }


def _sla_credit_register_report(env, **params):
    Credit = env["fix.msp.sla.credit"].sudo()
    credits = Credit.search([("company_id", "in", env.companies.ids)], limit=300)
    if not credits:
        return {
            "title": "SLA Credit Register",
            "cols": ["note"],
            "labels": {"note": ""},
            "rows": [
                {
                    "note": "No SLA credits raised yet — run Compute SLA Credits on a contract "
                    "whose monthly report missed its target."
                }
            ],
            "notes": ["Credits: draft → approved → applied (M20 billing seam)."],
        }
    rows = [
        {
            "contract": c.msp_contract_id.name,
            "period": c.period_label,
            "attainment_pct": c.attainment_pct,
            "target_pct": c.target_pct,
            "amount": c.credit_amount,
            "state": c.state,
        }
        for c in credits
    ]
    return {
        "title": "SLA Credit Register",
        "cols": ["contract", "period", "attainment_pct", "target_pct", "amount", "state"],
        "labels": {
            "contract": "Contract",
            "period": "Period",
            "attainment_pct": "Attained %",
            "target_pct": "Target %",
            "amount": "Credit (BDT)",
            "state": "State",
        },
        "rows": rows,
        "notes": ["Credits: draft → approved → applied (M20 billing seam)."],
    }


def _absent_report(title, note):
    def _report(env, **params):
        return {
            "title": title,
            "cols": ["note"],
            "labels": {"note": ""},
            "rows": [{"note": note}],
            "notes": [note],
        }

    return _report


REPORTS = {
    "sla_by_client": _sla_by_client_report,
    "remote_resolution": _remote_resolution_report,
    "estate_health": _estate_health_report,
    "patch_compliance": _patch_compliance_report,
    "alert_conversion": _alert_conversion_report,
    "sla_credit_register": _sla_credit_register_report,
    "backup_log": _absent_report(
        "Backup & Restore Test Log",
        "Backup test logging is not built yet — it arrives with the "
        "M06/M48 backup-telemetry integration; patch and SLA engines are live.",
    ),
}


class P03M05Controller(http.Controller):
    @http.route("/p03/msp/kpis", type="jsonrpc", auth="user", readonly=True)
    def msp_kpis(self, **kw):
        _require_internal(request.env)
        try:
            return {"M05": kpis(request.env)}
        except Exception:
            _logger.exception("p03 msp_kpis failed")
            return {"error": "KPI computation failed"}
