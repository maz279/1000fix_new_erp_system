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
#
# A02 audit P0 (2026-11-03): the remote-session consent code, maintenance
# window approval, patch-policy approval and the post-implementation review
# are whitelisted here with their screen buttons; window "open" is gone (a
# window's state follows its approval and time range).
#
# A02 audit B1 (2026-11-04): the CAB change approval, the SLA credit approval
# and the patch install exception are routed through the M63 engine. Their
# surfaces offer Request / Recall Approval; the decision is taken in the
# approver's inbox, so the record's own approve method is no longer listed.
import logging
from datetime import datetime, time

import pytz
from odoo import fields, http
from odoo.http import request

from ..p03_service_order_api import _require_internal

_logger = logging.getLogger(__name__)

SURFACES = {
    "fix.msp.contract": {
        "order": "id desc",
        "limit": 100,
        "actions": {
            "action_generate_monthly_report",
            "action_compute_sla_credits",
            # BRU-RMS-11 offboarding
            "action_start_offboarding",
            "action_record_access_revoked",
            "action_complete_offboarding",
        },
    },
    # M05 capture audit (2026-11-13): an engineer's health reading of an
    # asset runs the same alerting the collector does, and the alert rules
    # it is measured against are kept here.
    "fix.monitored.asset": {
        "order": "id desc",
        "limit": 200,
        "actions": {"action_record_reading", "action_record_agent_removal"},
    },
    "fix.msp.alert.rule": {
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
        "actions": {
            "action_request_consent",
            "action_verify_consent",
            "action_start",
            "action_end",
            "action_open_recording",  # BRU-RMS-12: shown and logged
        },
    },
    "fix.msp.service.report": {
        "order": "id desc",
        "limit": 100,
        "actions": {"action_generate_bilingual_report"},
    },
    "fix.msp.runbook": {
        "order": "id desc",
        "limit": 100,
        # Log Execution names its asset; an execution with evidence and an
        # outcome is logged on the Runbook Execution form (fix.msp.runbook.run)
        "actions": {"action_execute"},
    },
    # the execution log (spec T-08): logged complete with its outcome, so
    # nothing is left "running" to finish
    "fix.msp.runbook.run": {
        "order": "id desc",
        "limit": 200,
        "actions": set(),
    },
    # FR-RMS-039: backup job outcomes and restore tests per asset
    "fix.msp.backup.job": {
        "order": "run_at desc",
        "limit": 200,
        "actions": set(),
    },
    "fix.msp.patch.policy": {
        "order": "id desc",
        "limit": 100,
        "actions": {"action_approve"},
    },
    "fix.msp.patch.update": {
        "order": "id desc",
        "limit": 200,
        "actions": {
            "action_approve",
            "action_install",
            "action_defer",
            "action_fail",
            "action_record_test",
            "action_request_window_exception",
            "action_request_test_exception",
            "action_recall_approval",
        },
    },
    "fix.msp.sla.credit": {
        "order": "id desc",
        "limit": 100,
        "actions": {"action_request_approval", "action_recall_approval", "action_apply"},
    },
    "fix.msp.oncall.shift": {
        "order": "start_at desc",
        "limit": 100,
        "actions": {"action_activate", "action_close"},
    },
    "fix.msp.maintenance.window": {
        "order": "start_at desc",
        "limit": 100,
        "actions": {"action_approve", "action_close"},
    },
    # M05 spec features built by the audit (2026-11-13)
    "fix.msp.client.contact": {
        "order": "msp_contract_id, escalation_order",
        "limit": 200,
        "actions": set(),
    },
    "fix.msp.major.incident": {
        "order": "id desc",
        "limit": 100,
        "actions": {"action_notify_contacts", "action_resolve", "action_record_review"},
    },
    "fix.msp.service.review": {
        "order": "meeting_date desc",
        "limit": 100,
        "actions": {"action_close"},
    },
    "fix.msp.review.action": {"order": "due_date", "limit": 200, "actions": set()},
    "fix.msp.roadmap.item": {
        "order": "id desc",
        "limit": 200,
        "actions": {
            "action_accept",
            "action_decline",
            "action_deliver",
            "action_create_opportunity",
        },
    },
    "fix.msp.cloud.subscription": {"order": "renewal_date", "limit": 200, "actions": set()},
    "fix.msp.dr.plan": {"order": "id desc", "limit": 100, "actions": set()},
    "fix.msp.dr.test": {"order": "test_date desc", "limit": 200, "actions": set()},
    "fix.msp.change.record": {
        "order": "id desc",
        "limit": 200,
        "actions": {
            "action_request_approval",
            "action_recall_approval",
            "action_reject",
            "action_implement",
            "action_record_review",
            "action_close",
        },
    },
}


def _period_bounds(env, date_from=None, date_to=None):
    """The report period as UTC datetimes. The dates the screen sends are the
    reader's calendar days (Asia/Dhaka when no zone is set), not UTC days: a
    UTC cut would move every alert raised before 06:00 into the day before."""
    tz = pytz.timezone(env.context.get("tz") or env.user.tz or "Asia/Dhaka")

    def _utc(day, end):
        if not day:
            return None
        local = datetime.combine(fields.Date.to_date(day), time.max if end else time.min)
        return tz.localize(local).astimezone(pytz.utc).replace(tzinfo=None)

    return _utc(date_from, False), _utc(date_to, True)


def _period_domain(env, field, date_from=None, date_to=None):
    start, end = _period_bounds(env, date_from, date_to)
    domain = []
    if start:
        domain.append((field, ">=", start))
    if end:
        domain.append((field, "<=", end))
    return domain


def _company(env):
    return [("company_id", "in", env.companies.ids)]


def _period_note(date_from=None, date_to=None):
    if date_from or date_to:
        return "Period: %s to %s (raised in the period)." % (
            date_from or "start",
            date_to or "today",
        )
    return "All periods."


# The desk: what clients reported and every alert that became a ticket
# (the MSP Tickets screen shows exactly this set).
DESK = ["|", ("state", "in", ("ticketed", "resolved")), ("source", "!=", "monitoring")]


def _resolution_counts(env, extra=None):
    """Remote resolution, measured: of the alerts resolved, how many were
    closed without raising a service order (fixed remotely). The old figure
    divided resolved by "ticketed or resolved", which counted alerts resolved
    without a ticket as tickets and so measured nothing."""
    Alert = env["fix.msp.alert"].sudo()
    base = _company(env) + list(extra or [])
    raised = Alert.search_count(base)
    resolved = Alert.search_count([*base, ("state", "=", "resolved")])
    remote = Alert.search_count([*base, ("state", "=", "resolved"), ("order_id", "=", False)])
    return {
        "raised": raised,
        "resolved": resolved,
        "remote": remote,
        "via_order": resolved - remote,
        "open": raised - resolved,
        "rate": round(100.0 * remote / resolved, 1) if resolved else None,
    }


def kpis(env):
    """The M05 module-tile KPI row (registry-canonical metrics), measured
    from the live models with the same definitions as the reports."""
    Asset = env["fix.monitored.asset"].sudo()
    Alert = env["fix.msp.alert"].sudo()
    Credit = env["fix.msp.sla.credit"].sudo()
    Patch = env["fix.msp.patch.update"].sudo()
    domain = _company(env)
    month_start, _end = _period_bounds(env, fields.Date.context_today(Alert).replace(day=1))

    # open desk items: client reports and tickets not yet resolved
    open_tickets = Alert.search_count(domain + DESK + [("state", "!=", "resolved")])

    # SLA credits MTD: committed money (approved + applied) raised this month
    credits = Credit.search(
        [*domain, ("state", "in", ("approved", "applied")), ("create_date", ">=", month_start)]
    )
    tracked = Patch.search_count(domain)
    installed = Patch.search_count([*domain, ("state", "=", "installed")])
    return {
        "monitored_assets": Asset.search_count(domain),
        "remote_resolution": _resolution_counts(env)["rate"],
        "open_msp_tickets": open_tickets,
        "sla_credits_mtd": round(sum(credits.mapped("credit_amount")), 2),
        "patch_compliance": round(100.0 * installed / tracked, 1) if tracked else None,
        "oncall_escalations": Alert.search_count(
            [*domain, ("escalated", "=", True), ("create_date", ">=", month_start)]
        ),
    }


# ---------------------------------------------------------------- reports


def _sla_by_client_report(env, **params):
    """Per MSP contract: the average attainment of its monthly reports. A
    report with no attainment figure (flagged by the credit run) is left out
    of the average: it was read as 0% and dragged the client down."""
    Contract = env["fix.msp.contract"].sudo()
    Report = env["fix.msp.service.report"].sudo()
    rows = []
    for msp in Contract.search(_company(env), order="name"):
        measured = Report.search(
            [("msp_contract_id", "=", msp.id), ("sla_attainment", "!=", False)]
        )
        unmeasured = len(msp.report_ids) - len(measured)
        if not msp.report_ids:
            continue
        avg = sum(measured.mapped("sla_attainment")) / len(measured) if measured else None
        rows.append(
            {
                "client": msp.contract_id.customer_id.name or "—",
                "contract": msp.name,
                "periods": len(measured),
                "unmeasured": unmeasured,
                "avg_attainment_pct": round(avg * 100.0, 1) if avg is not None else None,
                "target_pct": round(msp.sla_target_pct, 1),
                "assets": len(msp.asset_ids),
            }
        )
    return {
        "title": "MSP SLA Attainment by Client",
        "cols": [
            "client",
            "contract",
            "periods",
            "unmeasured",
            "avg_attainment_pct",
            "target_pct",
            "assets",
        ],
        "labels": {
            "client": "Client",
            "contract": "MSP Contract",
            "periods": "Months Measured",
            "unmeasured": "Months Without a Figure",
            "avg_attainment_pct": "Avg SLA %",
            "target_pct": "Target %",
            "assets": "Assets",
        },
        "rows": rows,
        "notes": [
            "Attainment = alerts resolved within the contract's resolution target / alerts "
            "judged, per monthly report; target from the contract. A month whose report has "
            "no figure is counted separately, not as 0%."
        ],
    }


def _remote_resolution_report(env, date_from=None, date_to=None, **params):
    c = _resolution_counts(env, _period_domain(env, "create_date", date_from, date_to))
    rows = [
        {"measure": "Alerts and tickets raised", "value": c["raised"]},
        {"measure": "Resolved", "value": c["resolved"]},
        {"measure": "Resolved remotely (no service order)", "value": c["remote"]},
        {"measure": "Resolved through a service order", "value": c["via_order"]},
        {"measure": "Still open", "value": c["open"]},
        {"measure": "Remote resolution rate %", "value": c["rate"]},
    ]
    return {
        "title": "Remote Resolution Rate",
        "cols": ["measure", "value"],
        "labels": {"measure": "Measure", "value": "Count"},
        "rows": rows,
        "notes": [
            "Remote resolution rate = resolved without a service order / resolved.",
            _period_note(date_from, date_to),
        ],
    }


def _alert_conversion_report(env, date_from=None, date_to=None, **params):
    Alert = env["fix.msp.alert"].sudo().with_context(lang="en_US")
    base = _company(env) + _period_domain(env, "create_date", date_from, date_to)
    labels = dict(Alert._fields["state"].selection)
    sources = dict(Alert._fields["source"].selection)
    rows = []
    for key, source_label in sources.items():
        scoped = [*base, ("source", "=", key)]
        total = Alert.search_count(scoped)
        if not total:
            continue
        counts = {s: Alert.search_count([*scoped, ("state", "=", s)]) for s in labels}
        with_order = Alert.search_count([*scoped, ("order_id", "!=", False)])
        rows.append(
            {
                "source": source_label,
                "raised": total,
                **{s: counts[s] for s in labels},
                "converted_pct": round(100.0 * with_order / total, 1),
            }
        )
    cols = ["source", "raised", *labels, "converted_pct"]
    return {
        "title": "Alert-to-Ticket Conversion",
        "cols": cols,
        "labels": {
            "source": "Reported Through",
            "raised": "Raised",
            **labels,
            "converted_pct": "Became a Service Order %",
        },
        "rows": rows,
        "notes": [
            "Each alert or client report counts once, in its current state.",
            _period_note(date_from, date_to),
        ],
    }


def _estate_health_report(env, **params):
    """Health scoring, measured: per contract the asset mix plus the average
    health score (100 healthy / 50 degraded / 0 offline, minus 5 per open
    alert)."""
    Asset = env["fix.monitored.asset"].sudo()
    assets = Asset.search(_company(env))
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
        by_contract.setdefault(a.msp_contract_id.name or "—", []).append(a)
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
    updates = Patch.search(_company(env))
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


def _sla_credit_register_report(env, date_from=None, date_to=None, **params):
    """Credits whose service month falls in the period (the period label is
    the month the credit is FOR, not the day it was computed)."""
    Credit = env["fix.msp.sla.credit"].sudo().with_context(lang="en_US")
    domain = list(_company(env))
    if date_from:
        domain.append(("period_label", ">=", str(date_from)[:7]))
    if date_to:
        domain.append(("period_label", "<=", str(date_to)[:7]))
    credits = Credit.search(domain, order="period_label desc, id desc")
    states = dict(Credit._fields["state"].selection)
    if not credits:
        return {
            "title": "SLA Credit Register",
            "cols": ["note"],
            "labels": {"note": ""},
            "rows": [
                {
                    "note": "No SLA credits in this period — Compute SLA Credits on a contract "
                    "drafts one for a month whose report missed its target."
                }
            ],
            "notes": [
                "Credits: draft → approved → applied to billing.",
                _period_note(date_from, date_to),
            ],
        }
    rows = [
        {
            "contract": c.msp_contract_id.name,
            "period": c.period_label,
            "attainment_pct": c.attainment_pct,
            "target_pct": c.target_pct,
            "amount": c.credit_amount,
            "manual": "Manual" if c.is_manual else "Computed",
            "state": states.get(c.state, c.state),
        }
        for c in credits
    ]
    return {
        "title": "SLA Credit Register",
        "cols": ["contract", "period", "attainment_pct", "target_pct", "amount", "manual", "state"],
        "labels": {
            "contract": "Contract",
            "period": "Service Month",
            "attainment_pct": "Attained %",
            "target_pct": "Target %",
            "amount": "Credit (BDT)",
            "manual": "Basis",
            "state": "State",
        },
        "rows": rows,
        "notes": [
            "Credits: draft → approved → applied to billing.",
            _period_note(date_from, date_to),
        ],
    }


def _backup_log_report(env, date_from=None, date_to=None, **params):
    """FR-RMS-039: the backup jobs and restore tests recorded per asset, with
    the run of failures each asset is on."""
    Job = env["fix.msp.backup.job"].sudo().with_context(lang="en_US")
    domain = _company(env) + _period_domain(env, "run_at", date_from, date_to)
    jobs = Job.search(domain, order="run_at desc, id desc")
    outcomes = dict(Job._fields["outcome"].selection)
    if not jobs:
        return {
            "title": "Backup & Restore Test Log",
            "cols": ["note"],
            "labels": {"note": ""},
            "rows": [
                {
                    "note": "No backup job recorded in this period — record each job with "
                    "+ Record a Backup Job on Backup Jobs."
                }
            ],
            "notes": [
                "A failed job raises an alert on its asset.",
                _period_note(date_from, date_to),
            ],
        }
    rows = [
        {
            "run_at": fields.Datetime.context_timestamp(Job, j.run_at).strftime("%Y-%m-%d %H:%M"),
            "contract": j.msp_contract_id.name,
            "asset": j.asset_id.hostname or j.asset_id.agent_id,
            "plan": j.plan_ref,
            "outcome": outcomes.get(j.outcome, j.outcome),
            "restore_tested": "Yes" if j.restore_tested else "No",
            "consecutive_failures": j.consecutive_failures,
        }
        for j in jobs
    ]
    return {
        "title": "Backup & Restore Test Log",
        "cols": [
            "run_at",
            "contract",
            "asset",
            "plan",
            "outcome",
            "restore_tested",
            "consecutive_failures",
        ],
        "labels": {
            "run_at": "Run At",
            "contract": "Contract",
            "asset": "Asset",
            "plan": "Backup Plan",
            "outcome": "Outcome",
            "restore_tested": "Restore Tested",
            "consecutive_failures": "Failures in a Row",
        },
        "rows": rows,
        "notes": [
            "A failed or partial job raises an alert on its asset; a restore test proves "
            "the backup can be read back.",
            _period_note(date_from, date_to),
        ],
    }


def _cloud_cost_report(env, **params):
    """FR-RMS-041: what each client spends on cloud subscriptions and what
    paying only for the seats in use would save."""
    Sub = env["fix.msp.cloud.subscription"].sudo().with_context(lang="en_US")
    subs = Sub.search([*_company(env), ("state", "=", "active")], order="msp_contract_id, name")
    providers = dict(Sub._fields["provider"].selection)
    rows = []
    for sub in subs:
        unused = max((sub.seats or 0) - (sub.seats_used or 0), 0)
        saving = round(unused * (sub.unit_cost or 0.0), 2)
        rows.append(
            {
                "contract": sub.msp_contract_id.name,
                "provider": providers.get(sub.provider, sub.provider),
                "plan": sub.name,
                "seats": sub.seats,
                "used": sub.seats_used,
                "monthly_cost": round(sub.monthly_cost, 2),
                "saving": saving,
                "advice": (
                    "Release %d unused seat(s)" % unused
                    if unused
                    else ("Renews within 30 days: review" if sub.renewal_due else "Right-sized")
                ),
            }
        )
    if not rows:
        rows = [{"advice": "No active cloud subscription is tracked yet."}]
    return {
        "title": "Cloud Cost & Optimisation",
        "cols": [
            "contract",
            "provider",
            "plan",
            "seats",
            "used",
            "monthly_cost",
            "saving",
            "advice",
        ],
        "labels": {
            "contract": "Contract",
            "provider": "Provider",
            "plan": "Plan",
            "seats": "Seats",
            "used": "In Use",
            "monthly_cost": "Monthly Cost (BDT)",
            "saving": "Possible Saving / Month (BDT)",
            "advice": "Recommendation",
        },
        "rows": rows,
        "notes": [
            "Saving = unused seats x cost per seat. Seats in use are as recorded on the subscription."
        ],
    }


def _licence_compliance_report(env, **params):
    """FR-RMS-052: seats in use against seats bought. More in use than
    bought is a licence breach; the subscriptions are the ones tracked under
    each contract."""
    Sub = env["fix.msp.cloud.subscription"].sudo().with_context(lang="en_US")
    subs = Sub.search([*_company(env), ("state", "=", "active")], order="msp_contract_id, name")
    rows = []
    for sub in subs:
        gap = (sub.seats_used or 0) - (sub.seats or 0)
        rows.append(
            {
                "contract": sub.msp_contract_id.name,
                "plan": sub.name,
                "seats": sub.seats,
                "used": sub.seats_used,
                "status": (
                    "Non-compliant: %d licence(s) short" % gap
                    if gap > 0
                    else "Compliant (%d spare)" % -gap
                ),
            }
        )
    if not rows:
        rows = [{"status": "No active subscription is tracked yet."}]
    return {
        "title": "Licence Compliance",
        "cols": ["contract", "plan", "seats", "used", "status"],
        "labels": {
            "contract": "Contract",
            "plan": "Subscription",
            "seats": "Licences Bought",
            "used": "In Use",
            "status": "Compliance",
        },
        "rows": rows,
        "notes": [
            "Covers the subscriptions tracked under each MSP contract; software installed "
            "on the client's own devices is not inventoried."
        ],
    }


def _security_posture_report(env, **params):
    """FR-RMS-044: each client's security posture as one periodic
    deliverable: patching, monitoring coverage, backups, recurring incidents
    and DR testing."""
    Contract = env["fix.msp.contract"].sudo()
    Patch = env["fix.msp.patch.update"].sudo()
    Alert = env["fix.msp.alert"].sudo()
    Job = env["fix.msp.backup.job"].sudo()
    Plan = env["fix.msp.dr.plan"].sudo()
    today = fields.Date.context_today(Contract)
    rows = []
    for msp in Contract.search(_company(env), order="name"):
        tracked = Patch.search_count([("msp_contract_id", "=", msp.id)])
        installed = Patch.search_count(
            [("msp_contract_id", "=", msp.id), ("state", "=", "installed")]
        )
        critical_open = Patch.search_count(
            [
                ("msp_contract_id", "=", msp.id),
                ("severity", "in", ("critical", "high")),
                ("state", "!=", "installed"),
            ]
        )
        gaps = Alert.search_count(
            [
                ("msp_contract_id", "=", msp.id),
                ("coverage_gap", "=", True),
                ("state", "!=", "resolved"),
            ]
        )
        failing = len(
            {
                (j.asset_id.id, j.plan_ref)
                for j in Job.search([("msp_contract_id", "=", msp.id)], order="run_at desc")
                if j.consecutive_failures
            }
        )
        overdue = Plan.search_count(
            [("msp_contract_id", "=", msp.id), ("next_test_due", "<", today)]
        )
        rows.append(
            {
                "contract": msp.name,
                "assets": msp.enrolled_count,
                "patch_pct": round(100.0 * installed / tracked, 1) if tracked else None,
                "critical_open": critical_open,
                "coverage_gaps": gaps,
                "failing_backups": failing,
                "dr_overdue": overdue,
            }
        )
    if not rows:
        rows = [{"contract": "No MSP contract yet."}]
    return {
        "title": "Security Posture",
        "cols": [
            "contract",
            "assets",
            "patch_pct",
            "critical_open",
            "coverage_gaps",
            "failing_backups",
            "dr_overdue",
        ],
        "labels": {
            "contract": "Contract",
            "assets": "Monitored Assets",
            "patch_pct": "Patch Compliance %",
            "critical_open": "Critical / High Patches Open",
            "coverage_gaps": "Open Coverage Gaps",
            "failing_backups": "Backup Plans Failing",
            "dr_overdue": "DR Tests Overdue",
        },
        "rows": rows,
        "notes": [
            "A backup plan is failing while its latest jobs have failed since its last success."
        ],
    }


REPORTS = {
    "sla_by_client": _sla_by_client_report,
    "remote_resolution": _remote_resolution_report,
    "estate_health": _estate_health_report,
    "patch_compliance": _patch_compliance_report,
    "alert_conversion": _alert_conversion_report,
    "sla_credit_register": _sla_credit_register_report,
    "backup_log": _backup_log_report,
    "cloud_cost": _cloud_cost_report,
    "licence_compliance": _licence_compliance_report,
    "security_posture": _security_posture_report,
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
