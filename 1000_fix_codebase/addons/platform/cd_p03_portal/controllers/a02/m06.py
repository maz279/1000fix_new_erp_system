# A02 · M06 Data Services & Recovery — the surfaces the generic workspace
# screens read, the workflow methods they may call, the module KPI payload
# (/p03/data/kpis) and the built-in reports (/p03/model/report). Same
# contract as a02/m01..m05.
#
# Iteration 2 (2026-10-27): the lab engines landed in cd_data_case
# (specialisms, attempts, sealed media units, cleanroom slots, evaluations,
# quotations, backup plans & restore tests), so every registry screen, KPI
# and report below is LIVE over real models. The Z4 step-up access action
# is whitelisted too: it fails closed without a valid TOTP code (SC-002).
#
# A02 audit P1/P2 (2026-11-04): named Z4 staff, the forensic image record and
# verification, the verified handover (target serial, one-time code) and the
# routed re-quote price change (Request / Recall Approval; the lab manager
# decides in the M63 inbox).
import logging
from datetime import date, datetime

from odoo import http
from odoo.exceptions import AccessError
from odoo.http import request

from ..p03_service_order_api import _require_internal

_logger = logging.getLogger(__name__)

SURFACES = {
    "fix.data.recovery.case": {
        "order": "id desc",
        "limit": 200,
        "actions": {
            "action_take_custody",
            "action_log_custody_transfer",
            "action_route_to_z4",
            "action_assign_staff",
            "action_assign_me",
            "action_record_image",
            "action_verify_image",
            # M06 sub-module capture (2026-11-13): FR-DTS-006 files and GB
            "action_record_inventory",
            "action_confirm_target_serial",
            "action_request_handover_otp",
            "action_record_destructive_consent",
            "action_start_recovery",
            "action_recovered",
            "action_mark_unrecoverable",
            "action_handover",
            "action_purge",
            "action_close",
            "action_access_recovered_data",
        },
    },
    "fix.data.wipe.certificate": {
        "order": "id desc",
        "limit": 200,
        "actions": {"action_verify", "action_mark_failed"},
    },
    "fix.z4.access.audit": {
        "order": "access_time desc",
        "limit": 200,
        "actions": set(),
    },
    "fix.data.recovery.attempt": {
        "order": "id desc",
        "limit": 200,
        "actions": {"action_finish"},
    },
    "fix.data.media.unit": {
        "order": "id desc",
        "limit": 200,
        # A02 audit M06-11: only the strict seal break (a named witness) is offered
        "actions": {
            "action_transfer",
            "action_break_seal_with_witness",
            "action_return",
        },
    },
    "fix.data.cleanroom.slot": {
        "order": "start_at desc",
        "limit": 100,
        "actions": {"action_use", "action_cancel"},
    },
    "fix.data.evaluation": {
        "order": "id desc",
        "limit": 200,
        "actions": {"action_complete"},
    },
    "fix.data.quote": {
        "order": "id desc",
        "limit": 200,
        "actions": {
            "action_send",
            "action_accept",
            "action_decline",
            "action_requote",
            "action_request_approval",
            "action_recall_approval",
        },
    },
    "fix.data.backup.plan": {
        "order": "id desc",
        "limit": 100,
        "actions": {"action_log_test"},
    },
}


def kpis(env):
    """The M06 module-tile KPI row (registry-canonical metrics), all live."""
    Case = env["fix.data.recovery.case"].sudo()
    Cert = env["fix.data.wipe.certificate"].sudo()
    Slot = env["fix.data.cleanroom.slot"].sudo()
    Eval = env["fix.data.evaluation"].sudo()
    domain = [("company_id", "in", env.companies.ids)]

    active_cases = Case.search_count(
        [*domain, ("state", "not in", ("purged", "closed", "unrecoverable"))]
    )

    # recovery success: recovered vs decided-unrecoverable
    recovered = Case.search_count([*domain, ("state", "=", "recovered")])
    unrecoverable = Case.search_count([*domain, ("state", "=", "unrecoverable")])
    decided = recovered + unrecoverable
    recovery_success = round(100.0 * recovered / decided, 1) if decided else None

    now = datetime.now()
    cleanroom_slots = Slot.search_count(
        [*domain, ("state", "=", "planned"), ("start_at", ">=", now)]
    )

    month_start = datetime.combine(date.today().replace(day=1), datetime.min.time())
    destruction_certs_mtd = Cert.search_count([("create_date", ">=", month_start)])

    # eval turnaround: average hours media-received → verdict
    evals = Eval.search([("evaluated_at", "!=", False)], limit=200)
    eval_turnaround = round(sum(e.eval_hours for e in evals) / len(evals), 1) if evals else None

    purge_verifications = Case.search_count([*domain, ("state", "=", "purged")])

    return {
        "active_cases": active_cases,
        "recovery_success": recovery_success,
        "cleanroom_slots": cleanroom_slots,
        "destruction_certs_mtd": destruction_certs_mtd,
        "eval_turnaround": eval_turnaround,
        "purge_verifications": purge_verifications,
    }


# ---------------------------------------------------------------- reports


def _require_data_operator(env, title):
    """A02 audit M06-3 (Z2, Z4): the reports read cases through sudo, so
    they listed customers (and recovered file names) to any internal user.
    A report that lists cases or customers is for the data-recovery role."""
    if env.su or env.user.has_group("cd_data_case.group_data_recovery_operator"):
        return
    raise AccessError(
        "%s lists data-recovery cases and customers: it is open to the "
        "Data Recovery Operator role only." % title
    )


def _success_by_specialism(env, **params):
    Case = env["fix.data.recovery.case"].sudo().with_context(lang="en_US")
    cases = Case.search([("state", "in", ("recovered", "unrecoverable"))], limit=400)
    buckets = {}
    labels = dict(type(Case).specialism.selection)
    for case in cases:
        key = case.specialism or "unassigned"
        b = buckets.setdefault(key, {"recovered": 0, "unrecoverable": 0})
        b["recovered" if case.state == "recovered" else "unrecoverable"] += 1
    rows = []
    for key in sorted(buckets):
        b = buckets[key]
        decided = b["recovered"] + b["unrecoverable"]
        rows.append(
            {
                "specialism": labels.get(key, key),
                "recovered": b["recovered"],
                "unrecoverable": b["unrecoverable"],
                "success_pct": round(100.0 * b["recovered"] / decided, 1) if decided else None,
            }
        )
    return {
        "title": "Recovery Success by Specialism",
        "cols": ["specialism", "recovered", "unrecoverable", "success_pct"],
        "labels": {
            "specialism": "Specialism",
            "recovered": "Recovered",
            "unrecoverable": "Unrecoverable",
            "success_pct": "Success %",
        },
        "rows": rows,
        "notes": ["Decided cases (recovered + unrecoverable) only, live."],
    }


def _case_cycle_time(env, **params):
    Case = env["fix.data.recovery.case"].sudo()
    cases = Case.search([("state", "in", ("purged", "closed", "unrecoverable"))], limit=300)
    rows = []
    closed_total = purged_total = unrecoverable_total = 0
    n_closed = n_purged = n_unrecoverable = 0
    for case in cases:
        days = None
        if case.received_at:
            end = case.write_date or case.received_at
            days = round((end - case.received_at).total_seconds() / 86400.0, 1)
        if days is None:
            continue
        if case.state == "purged":
            purged_total += days
            n_purged += 1
        elif case.state == "unrecoverable":
            unrecoverable_total += days
            n_unrecoverable += 1
        else:
            closed_total += days
            n_closed += 1

    def avg(total, n):
        return round(total / n, 1) if n else None

    rows = [
        {
            "outcome": "Purged (completed journey)",
            "cases": n_purged,
            "avg_days": avg(purged_total, n_purged),
        },
        {"outcome": "Closed", "cases": n_closed, "avg_days": avg(closed_total, n_closed)},
        {
            "outcome": "Unrecoverable",
            "cases": n_unrecoverable,
            "avg_days": avg(unrecoverable_total, n_unrecoverable),
        },
    ]
    return {
        "title": "Case Cycle Time",
        "cols": ["outcome", "cases", "avg_days"],
        "labels": {"outcome": "Outcome", "cases": "Cases", "avg_days": "Avg Days"},
        "rows": rows,
        "notes": ["Media received → last write, per terminal state."],
    }


def _service_revenue(env, **params):
    _require_data_operator(env, "Data Service Revenue")
    Quote = env["fix.data.quote"].sudo()
    quotes = Quote.search([("state", "=", "accepted")], limit=300)
    if not quotes:
        return {
            "title": "Data Service Revenue",
            "cols": ["note"],
            "labels": {"note": ""},
            "rows": [
                {
                    "note": "No accepted quotations yet — revenue lights up with the first acceptance."
                }
            ],
            "notes": ["Accepted quotations only (no-data-no-fee economics)."],
        }
    by_case = {}
    for q in quotes:
        by_case.setdefault(q.case_id.name or "—", []).append(q)
    rows = [
        {
            "case": name,
            "quotes": len(group),
            "accepted_bdt": round(sum(q.amount for q in group), 2),
        }
        for name, group in sorted(by_case.items())
    ]
    return {
        "title": "Data Service Revenue",
        "cols": ["case", "quotes", "accepted_bdt"],
        "labels": {"case": "Case", "quotes": "Quotes", "accepted_bdt": "Accepted (BDT)"},
        "rows": rows,
        "notes": ["Accepted quotations only (no-data-no-fee economics)."],
    }


def _destruction_audit(env, **params):
    _require_data_operator(env, "Destruction & Purge Audit")
    Case = env["fix.data.recovery.case"].sudo()
    Cert = env["fix.data.wipe.certificate"].sudo()
    purged = Case.search([("state", "=", "purged")], limit=200)
    rows = [
        {
            "case": c.name,
            "customer": c.customer_id.name,
            "certificate": c.purge_certificate_id.name or "—",
            "method": c.purge_certificate_id.method or "—",
            "verification": (c.purge_certificate_id.verification_hash or "")[:16],
            "verified_at": str(c.purge_certificate_id.verified_at or "—")[:16],
        }
        for c in purged
    ]
    pending = Cert.search([("sanitization_status", "=", "pending_verification")], limit=100)
    return {
        "title": "Destruction & Purge Audit",
        "cols": ["case", "customer", "certificate", "method", "verification", "verified_at"],
        "labels": {
            "case": "Case",
            "customer": "Customer",
            "certificate": "Certificate",
            "method": "Method",
            "verification": "SHA-256 (first 16)",
            "verified_at": "Verified At",
        },
        "rows": rows,
        "notes": [
            "Purged cases with their verified certificates; %s certificate(s) await verification."
            % len(pending)
        ],
    }


def _backup_compliance(env, **params):
    Plan = env["fix.data.backup.plan"].sudo()
    plans = Plan.search([], limit=300)
    if not plans:
        return {
            "title": "Backup Restore-Test Compliance",
            "cols": ["note"],
            "labels": {"note": ""},
            "rows": [{"note": "No backup plans yet — add one to start the restore-test register."}],
            "notes": ["Compliant = latest restore test passed and the next test is not overdue."],
        }
    rows = [
        {
            "plan": p.name,
            "customer": p.customer_id.name,
            "type": dict(type(p).plan_type.selection).get(p.plan_type, p.plan_type),
            "last_test": str(p.last_test_date or "—")[:16],
            "result": p.last_test_result or "never",
            "next_due": str(p.next_test_due or "—"),
            "compliant": "yes" if p.compliant else "NO",
        }
        for p in plans
    ]
    ok = sum(1 for p in plans if p.compliant)
    return {
        "title": "Backup Restore-Test Compliance",
        "cols": ["plan", "customer", "type", "last_test", "result", "next_due", "compliant"],
        "labels": {
            "plan": "Plan",
            "customer": "Customer",
            "type": "Type",
            "last_test": "Last Test",
            "result": "Result",
            "next_due": "Next Due",
            "compliant": "Compliant",
        },
        "rows": rows,
        "notes": [
            "Compliant = latest restore test passed and the next test is not overdue. %s/%s compliant."
            % (ok, len(plans))
        ],
    }


def _recovered_inventory(env, **params):
    """The recovered-data inventory: how much is ACTUALLY stored against each
    active case (its attachments) - honest, including empty.

    A02 audit M06-3 (Z2): this listed recovered FILE NAMES through sudo() to
    any internal user, with no step-up and no audit row (spec 13: the ERP
    never shows file names). It now gives counts and sizes only, to the
    data-recovery role; the files themselves open through the case's Z4
    step-up access, which is audited per read.

    M06 sub-module capture (2026-11-13): the attachments are the case's own
    documents (NDA, consent, receipt), not the recovered data, which never
    enters the ERP. The inventory the lab recorded (files and GB, FR-DTS-006)
    is shown first; the documents keep their own columns."""
    _require_data_operator(env, "The recovered-data inventory")
    Case = env["fix.data.recovery.case"].sudo().with_context(lang="en_US")
    Attachment = env["ir.attachment"].sudo()
    states = dict(type(Case).state.selection)
    cases = Case.search([("state", "in", ("recovering", "recovered", "handover"))], limit=100)
    rows = []
    for case in cases:
        atts = Attachment.search(
            [("res_model", "=", "fix.data.recovery.case"), ("res_id", "=", case.id)]
        )
        rows.append(
            {
                "case": case.name,
                "customer": case.customer_id.name,
                "stage": states.get(case.state, case.state),
                "recovered_files": case.recovered_files_count,
                "recovered_gb": round(case.recovered_volume_gb or 0.0, 2),
                "files": len(atts),
                "size_kb": round(sum(atts.mapped("file_size")) / 1024.0, 1),
                "zone": case.residency_zone,
            }
        )
    return {
        "title": "Recovered-Data Inventory (Z4)",
        "cols": [
            "case",
            "customer",
            "stage",
            "recovered_files",
            "recovered_gb",
            "files",
            "size_kb",
            "zone",
        ],
        "labels": {
            "case": "Case",
            "customer": "Customer",
            "stage": "Stage",
            "recovered_files": "Recovered Files",
            "recovered_gb": "Recovered GB",
            "files": "Case Documents",
            "size_kb": "Documents KB",
            "zone": "Zone",
        },
        "rows": rows,
        "notes": [
            "Recovered files and GB are what the lab recorded for each case; a case still "
            "showing 0 has no inventory recorded yet.",
            "Case documents are the signed papers kept on the case (agreement, consent, "
            "receipt). File names are never listed here: open them through the case's Z4 "
            "step-up access.",
        ],
    }


REPORTS = {
    "recovery_success_by_specialism": _success_by_specialism,
    "case_cycle_time": _case_cycle_time,
    "data_service_revenue": _service_revenue,
    "destruction_purge_audit": _destruction_audit,
    "backup_restore_compliance": _backup_compliance,
    "recovered_inventory": _recovered_inventory,
}


class P03M06Controller(http.Controller):
    @http.route("/p03/data/kpis", type="jsonrpc", auth="user", readonly=True)
    def data_kpis(self, **kw):
        _require_internal(request.env)
        try:
            return {"M06": kpis(request.env)}
        except Exception:
            _logger.exception("p03 data_kpis failed")
            return {"error": "KPI computation failed"}
