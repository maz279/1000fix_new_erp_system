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
from datetime import datetime, time

import pytz
from odoo import fields, http
from odoo.exceptions import AccessError
from odoo.http import request

from ..p03_service_order_api import _require_internal

_logger = logging.getLogger(__name__)

SURFACES = {
    "fix.data.recovery.case": {
        "order": "id desc",
        "limit": 200,
        # A02 pass 2 review: read AS THE CALLER (M06-02 - an operator sees
        # his assigned cases and the intake queue, lab managers all), and
        # every list or form read lands in the case read log
        "caller_scoped": True,
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
            # A02 ERP audit M06-F1: hand-over without a paid invoice
            "action_approve_credit",
            "action_waive_charge",
            "action_purge",
            "action_close",
            "action_access_recovered_data",
            # A02 pass 2 M06-01 / M06-03: the lab manager's customer
            # correction, and the receiver's confirmation of a hand-off
            "action_correct_customer",
            "action_confirm_custody",
            # A02 pass 2 review: the requester withdraws an unconfirmed hand-off
            "action_withdraw_handoff",
        },
    },
    "fix.data.wipe.certificate": {
        "order": "id desc",
        "limit": 200,
        # A02 pass 2 M06-09: the second person witnesses a destruction
        "actions": {"action_verify", "action_mark_failed", "action_witness_destruction"},
    },
    "fix.z4.access.audit": {
        "order": "access_time desc",
        "limit": 200,
        "actions": set(),
    },
    "fix.data.recovery.attempt": {
        "order": "id desc",
        "limit": 200,
        "caller_scoped": True,
        "actions": {"action_finish"},
    },
    "fix.data.media.unit": {
        "order": "id desc",
        "limit": 200,
        "caller_scoped": True,
        # A02 audit M06-11: only the strict seal break (a named witness) is offered
        "actions": {
            "action_transfer",
            "action_break_seal_with_witness",
            # A02 ERP audit M06-F11 / F9: the witness's own confirmation; destruction
            "action_confirm_seal_break",
            "action_return",
            "action_destroy",
            # A02 pass 2 M06-03: the receiver confirms a move or a return
            "action_confirm_move",
            "action_withdraw_move",
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
        "caller_scoped": True,
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
    # M06 capture pass 2 (2026-11-18): the records five pages could not
    # capture (cd_data_case models/fix_data_capture.py), and the custody
    # ledger every move writes, which no screen listed.
    # A02 pass 2: the sanitisation matrix (D16, the Quality Manager keeps it)
    # and the case read log (M06-02, lab managers read it)
    "fix.data.sanitisation.rule": {"order": "media_kind, id", "limit": 200, "actions": set()},
    "fix.data.case.read.log": {
        "order": "read_at desc, id desc",
        "limit": 300,
        "actions": set(),
        "caller_scoped": True,
    },
    "fix.data.custody.event": {
        "order": "event_at desc, id desc",
        "limit": 200,
        "caller_scoped": True,
        "actions": set(),
    },
    "fix.data.confidentiality.undertaking": {
        "order": "id desc",
        "limit": 200,
        "actions": {"action_revoke"},
    },
    "fix.data.retention.hold": {
        "order": "id desc",
        "limit": 200,
        "actions": {"action_approve", "action_reject", "action_release"},
    },
    "fix.data.recovered.inventory": {
        "order": "id desc",
        "limit": 200,
        "actions": set(),
    },
    "fix.data.wipe.request": {
        "order": "id desc",
        "limit": 200,
        "actions": {"action_cancel"},
    },
    "fix.data.backup.test": {
        "order": "tested_at desc, id desc",
        "limit": 200,
        "actions": set(),
    },
    "fix.data.backup.run": {
        "order": "started_at desc, id desc",
        "limit": 200,
        "actions": set(),
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

    # recovery success: of the decided cases, how many were recovered. A02 ERP
    # audit M06-F16: only cases still sitting in 'recovered' counted, so every
    # case handed over, purged or closed dropped out of the rate.
    outcomes = _outcomes(Case.search([*domain, ("state", "in", DECIDED_STATES)]))
    recovered, unrecoverable = outcomes["recovered"], outcomes["unrecoverable"]
    decided = recovered + unrecoverable
    recovery_success = round(100.0 * recovered / decided, 1) if decided else None

    cleanroom_slots = Slot.search_count(
        [*domain, ("state", "=", "planned"), ("start_at", ">=", fields.Datetime.now())]
    )

    # M06-F20: verified certificates of this Dhaka month, this company's only
    # (it counted every certificate of every company and state, from a naive
    # local midnight)
    destruction_certs_mtd = Cert.search_count(
        [
            *domain,
            ("sanitization_status", "=", "verified"),
            ("verified_at", ">=", _dhaka_month_start(env)),
        ]
    )

    # eval turnaround: average hours media-received → verdict
    evals = Eval.search([*domain, ("evaluated_at", "!=", False)])
    eval_turnaround = round(sum(e.eval_hours for e in evals) / len(evals), 1) if evals else None

    purge_verifications = Case.search_count([*domain, ("state", "=", "purged")])
    # A02 pass 2 M06-11 (D17): handed-over cases past their retention date,
    # not those kept on an approved retention (legal) hold (A02 pass 2 review)
    purge_overdue = len(
        Case.search(
            [
                *domain,
                ("state", "=", "handover"),
                ("retention_until", "!=", False),
                ("retention_until", "<", fields.Date.context_today(Case)),
            ]
        ).filtered(lambda case: not case._retention_held())
    )

    return {
        "active_cases": active_cases,
        "recovery_success": recovery_success,
        "cleanroom_slots": cleanroom_slots,
        "destruction_certs_mtd": destruction_certs_mtd,
        "eval_turnaround": eval_turnaround,
        "purge_verifications": purge_verifications,
        "purge_overdue": purge_overdue,
    }


DECIDED_STATES = ("recovered", "handover", "purged", "closed", "unrecoverable")


def _outcomes(cases):
    """{'recovered': n, 'unrecoverable': n} over ``cases`` by their outcome,
    not their current state (a recovered case moves on to handover, purge and
    close). A case closed without an outcome (a declined quotation) is not
    decided."""
    counts = {"recovered": 0, "unrecoverable": 0}
    for case in cases:
        outcome = case._data_outcome()
        if outcome in counts:
            counts[outcome] += 1
    return counts


def _dhaka_month_start(env):
    """The first instant of the current Dhaka calendar month, in UTC."""
    tz = pytz.timezone(env.context.get("tz") or env.user.tz or "Asia/Dhaka")
    first = datetime.now(tz).date().replace(day=1)
    return tz.localize(datetime.combine(first, time.min)).astimezone(pytz.utc).replace(tzinfo=None)


def _day_bounds(env, date_from=None, date_to=None):
    """The report period as UTC datetimes of the reader's (Dhaka) days."""
    tz = pytz.timezone(env.context.get("tz") or env.user.tz or "Asia/Dhaka")

    def _utc(day, end):
        if not day:
            return None
        local = datetime.combine(fields.Date.to_date(day), time.max if end else time.min)
        return tz.localize(local).astimezone(pytz.utc).replace(tzinfo=None)

    return _utc(date_from, False), _utc(date_to, True)


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
    cases = Case.search([("company_id", "in", env.companies.ids), ("state", "in", DECIDED_STATES)])
    buckets = {}
    labels = dict(type(Case).specialism.selection)
    for case in cases:
        # by outcome, not current state (A02 ERP audit M06-F16)
        outcome = case._data_outcome()
        if outcome not in ("recovered", "unrecoverable"):
            continue
        key = case.specialism or "unassigned"
        b = buckets.setdefault(key, {"recovered": 0, "unrecoverable": 0})
        b[outcome] += 1
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
    # A02 pass 2 M06-08 / X5-07: the caller's companies, the data-lab role,
    # every case (no cap), and the clock stops at the hand-over to the customer
    _require_data_operator(env, "Case Cycle Time")
    Case = env["fix.data.recovery.case"].sudo()
    cases = Case.search(
        [
            ("company_id", "in", env.companies.ids),
            ("state", "in", ("purged", "closed", "unrecoverable")),
        ]
    )
    rows = []
    closed_total = purged_total = unrecoverable_total = 0
    n_closed = n_purged = n_unrecoverable = 0
    for case in cases:
        days = None
        if case.received_at:
            end = case.handover_at or case.write_date or case.received_at
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
        "notes": [
            "Media received → hand-over to the customer (the last change for a case never "
            "handed over), per terminal state; this company's cases."
        ],
    }


def _service_revenue(env, date_from=None, date_to=None, **params):
    """What the decided cases bill (A02 ERP audit M06-F17): it summed every
    accepted quotation, including unrecoverable no-data-no-fee cases that
    owe nothing, left out the donor fee and read every company. Now: the
    case's own billing rule (recovery fee + donor fee when recovered; under
    no-data-no-fee only the donor fee when unrecoverable), this company's
    cases, accepted in the period."""
    _require_data_operator(env, "Data Service Revenue")
    Quote = env["fix.data.quote"].sudo()
    start, end = _day_bounds(env, date_from, date_to)
    domain = [("state", "=", "accepted"), ("company_id", "in", env.companies.ids)]
    if start:
        domain.append(("accepted_at", ">=", start))
    if end:
        domain.append(("accepted_at", "<=", end))
    quotes = Quote.search(domain)
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
    rows = []
    billed_total = 0.0
    for case in quotes.mapped("case_id").sorted("name"):
        quote, lines, outcome = case._data_billable()
        billable = round(sum(amount for _d, amount in lines), 2)
        billed_total += billable
        invoice = case._data_invoice()
        rows.append(
            {
                "case": case.name,
                "outcome": outcome or "not decided",
                "quoted_bdt": round((quote.amount or 0.0) + (quote.donor_fee_bdt or 0.0), 2),
                "billable_bdt": billable,
                "invoice": (invoice.name if invoice and invoice.name != "New" else "")
                or ("draft AR/%s" % invoice.id if invoice else "-"),
                "invoice_state": invoice.state if invoice else "-",
            }
        )
    return {
        "title": "Data Service Revenue",
        "cols": ["case", "outcome", "quoted_bdt", "billable_bdt", "invoice", "invoice_state"],
        "labels": {
            "case": "Case",
            "outcome": "Outcome",
            "quoted_bdt": "Quoted incl. Donor Fee (BDT)",
            "billable_bdt": "Billable before VAT (BDT)",
            "invoice": "M20 Invoice",
            "invoice_state": "Invoice State",
        },
        "rows": rows,
        "notes": [
            "Billable = recovery fee + donor fee when recovered; under no-data-no-fee only the "
            "donor fee when unrecoverable; nothing until the outcome. Total BDT %.2f before VAT."
            % billed_total,
            "Quotations accepted in the period, this company's cases.",
        ],
    }


def _destruction_audit(env, **params):
    _require_data_operator(env, "Destruction & Purge Audit")
    Case = env["fix.data.recovery.case"].sudo()
    Cert = env["fix.data.wipe.certificate"].sudo()
    fence = [("company_id", "in", env.companies.ids)]
    purged = Case.search([*fence, ("state", "=", "purged")])
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
    pending = Cert.search([*fence, ("sanitization_status", "=", "pending_verification")])
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
    _require_data_operator(env, "Backup Compliance")
    Plan = env["fix.data.backup.plan"].sudo()
    plans = Plan.search([("company_id", "in", env.companies.ids)])
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
    types = dict(env["fix.data.recovered.inventory"]._fields["file_type"].selection)
    cases = Case.search(
        [
            ("company_id", "in", env.companies.ids),
            ("state", "in", ("recovering", "recovered", "handover")),
        ]
    )
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
                # M06 capture pass 2: FR-DTS-006 is "by type and size"
                "by_type": ", ".join(
                    "%s %d (%.2f GB)"
                    % (types.get(line.file_type, line.file_type), line.file_count, line.size_gb)
                    for line in case.inventory_line_ids
                )
                or "-",
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
            "by_type",
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
            "by_type": "By File Type",
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
