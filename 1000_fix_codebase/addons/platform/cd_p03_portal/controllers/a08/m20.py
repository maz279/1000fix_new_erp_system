# A08 · M20 AR, Invoicing & Collections — models the generic workspace screens may read,
# and the workflow methods they may call (/p03/model/records, /p03/model/action).
# Each entry: model -> {"order", "limit", "actions"}. Reads also need the
# user's own read access on the model (accounting/payroll groups apply).
#
# The fifteen original M20 screens are bespoke (/p03/ar/* in p03_ar_api.py);
# the credit-control Hold button runs fix.credit.profile.action_toggle_hold
# through /p03/ar/credit-profile/save. The generic surfaces below serve the
# A08 additions: invoice close-out (action_register_paid) and the customer
# VDS certificates (Mushak 6.6 received).
import datetime


def _pack(title, cols, labels, rows, notes, totals=None, empty=None):
    """Table-report payload shared by the M19/M20 packs."""
    return {
        "title": title,
        "cols": cols,
        "labels": labels,
        "rows": rows,
        "totals": totals,
        "notes": notes,
        "empty": empty,
    }


SURFACES = {
    # A08 M20-6: a write-off climbs the credit ladder and draws the ECL
    # allowance first; raised, approved and rejected only by its actions.
    "fix.ar.writeoff": {
        "order": "id desc",
        "limit": 200,
        "actions": {"action_submit", "action_approve", "action_reject"},
    },
    "fix.ar.impairment": {
        "order": "as_of desc, id desc",
        "limit": 200,
        "actions": {"action_compute", "action_post"},
    },
    # A08 M20-5: the approved IFRS 9 loss rates a run stamps at Compute
    "fix.ar.ecl.rate": {
        "order": "date_from desc, id desc",
        "limit": 100,
        "actions": {"action_approve", "action_retire"},
    },
    "fix.ar.invoice": {
        "order": "invoice_date desc, id desc",
        "limit": 200,
        # issue: an Accountant other than the raiser of a manual invoice
        "actions": {"action_register_paid", "action_issue"},
    },
    "fix.ar.receipt": {
        "order": "receipt_date desc, id desc",
        "limit": 200,
        "actions": {"action_confirm", "action_reverse"},
    },
    "fix.credit.note": {
        "order": "create_date desc, id desc",
        "limit": 200,
        # A08 S3: approve within the direct band (second Accountant); above
        # it the approval is decided from the M63 inbox, not here
        "actions": {
            "action_submit",
            "action_approve",
            "action_reject",
            "action_issue",
            "action_rerequest",
            "action_withdraw_to_draft",
        },
    },
    "fix.ar.payment.link": {
        "order": "create_date desc, id desc",
        "limit": 200,
        "actions": set(),
    },
    "fix.vds.certificate.received": {
        "order": "certificate_date desc, id desc",
        "limit": 200,
        "actions": {"action_verify", "action_settle", "action_cancel"},
    },
    # customer TDS / AIT certificates (income tax deducted at source)
    "fix.tds.certificate.received": {
        "order": "certificate_date desc, id desc",
        "limit": 200,
        "actions": {"action_verify", "action_settle", "action_cancel"},
    },
    "fix.ar.consolidated.bill": {
        "order": "id desc",
        "limit": 400,
        "actions": {"action_generate", "action_send"},
    },
    "fix.ar.dispute": {
        "order": "id desc",
        "limit": 400,
        # BRU-ARB-17: one button per outcome code; the note is asked
        "actions": {
            "action_resolve_upheld_credit",
            "action_resolve_partially_upheld",
            "action_resolve_rejected",
            "action_resolve_withdrawn",
            "action_resolve_payment_plan",
        },
    },
    "fix.dunning": {
        "order": "id desc",
        "limit": 400,
        # BRU-ARB-16: one button per suppression reason, an end date, a lift
        "actions": {
            "action_suppress_payment_plan",
            "action_suppress_strategic",
            "action_suppress_dispute",
            "action_lift_suppression",
        },
    },
    # FR-ARB-001/044: the billable-event queue the Billable-Event Intake page
    # lists (it listed invoices before). Read-only: rows come from closed jobs;
    # "Process All Due" / "Generate now" stay on the Billable Events screen.
    "fix.billable.event": {
        "order": "first_seen_at desc, id desc",
        "limit": 400,
        "actions": set(),
    },
    # ---- M20 second capture pass (19 Nov 2026): the spec records ----
    # p8 FR-ARB-032: the reminder ladder per segment / named account
    "fix.ar.dunning.policy": {
        "order": "state, segment, name",
        "limit": 200,
        "actions": {"action_activate", "action_retire"},
        "pickers": {"customer_ids": [("customer_rank", ">", 0)]},
    },
    # A08 wave 5 (M20-F5): the delivery evidence of every reminder the ladder
    # sends — immutable once sent; a failed send is retryable, a sent step is
    # never re-sent.
    "fix.ar.dunning.action": {
        "order": "create_date desc, id desc",
        "limit": 500,
        "actions": {"action_retry"},
    },
    # A08 wave 5 (M20-F5): a call step lands here for the contact centre.
    "fix.ar.dunning.handoff": {
        "order": "priority desc, id desc",
        "limit": 300,
        "actions": {"action_pick_up", "action_done", "action_cancel"},
    },
    # p8 FR-ARB-034: the prioritised collections worklist
    "fix.ar.collection.case": {
        "order": "state, priority_score desc, id",
        "limit": 400,
        "actions": {
            "action_refresh",
            "action_take",
            "action_log_contact",
            "action_close_paid",
            "action_close_promise",
            "action_close_plan",
            "action_close_legal",
            "action_close_uncollectible",
        },
        "pickers": {"assigned_to": [("share", "=", False)]},
    },
    # p8 FR-ARB-035: a promise holds dunning until its date
    "fix.ar.promise": {
        "order": "state, promised_date, id",
        "limit": 400,
        "actions": {"action_cancel"},
        "pickers": {
            "invoice_id": [("state", "=", "issued")],
            "case_id": [("state", "!=", "closed")],
        },
    },
    # p8 FR-ARB-037: instalments agreed by a second person
    "fix.ar.payment.plan": {
        "order": "state, id desc",
        "limit": 200,
        "actions": {"action_activate", "action_cancel"},
        "pickers": {"invoice_ids": [("state", "=", "issued")]},
    },
    "fix.ar.payment.plan.line": {"order": "plan_id, due_date, id", "limit": 400, "actions": set()},
    # p4 FR-ARB-013/014: one delivery record per invoice and channel
    "fix.ar.invoice.delivery": {
        "order": "id desc",
        "limit": 400,
        "actions": {
            "action_mark_sent",
            "action_mark_delivered",
            "action_mark_opened",
            "action_mark_failed",
            "action_retry",
        },
        "pickers": {"invoice_id": [("state", "in", ("issued", "paid"))]},
    },
    # p4 FR-ARB-017: statements of account, frozen once generated
    "fix.ar.statement": {
        "order": "id desc",
        "limit": 400,
        "actions": {"action_generate", "action_mark_delivered"},
    },
    # p5 FR-ARB-028: deposit / retention money held apart from receivables
    "fix.ar.deposit": {
        "order": "state, release_due_at, id desc",
        "limit": 400,
        "actions": {"action_apply", "action_release"},
        "pickers": {
            "receipt_id": [("state", "=", "confirmed"), ("unapplied_amount", ">", 0)],
        },
    },
    # p9 FR-ARB-040: refund of on-account money, authorised by another person
    "fix.ar.refund": {
        "order": "id desc",
        "limit": 400,
        "actions": {"action_authorise", "action_reject"},
        "pickers": {
            "receipt_id": [("state", "=", "confirmed"), ("unapplied_amount", ">", 0)],
        },
    },
    # p10 FR-ARB-043 / BRU-ARB-24: delivered but not invoiced
    "fix.ar.unbilled.exception": {
        "order": "state, age_days desc, id",
        "limit": 400,
        "actions": {
            "action_resolve_invoiced",
            "action_resolve_not_billable",
            "action_resolve_duplicate",
        },
    },
}


def _as_date(value, fallback=None):
    if not value:
        return fallback
    if isinstance(value, datetime.datetime):
        return value.date()
    if isinstance(value, datetime.date):
        return value
    return datetime.date.fromisoformat(str(value)[:10])


def _period_of(value):
    if not value:
        return None
    if isinstance(value, str):
        value = datetime.date.fromisoformat(value[:10])
    return value.strftime("%Y-%m")


def vds_claim_register(env, date_from=None, date_to=None, **params):
    """VDS received per VAT period (the Mushak 9.1 VDS adjustment working):
    certificates by state, read with the caller's own access rights."""
    Cert = env["fix.vds.certificate.received"]
    domain = [("company_id", "in", env.companies.ids), ("state", "!=", "cancelled")]
    p_from, p_to = _period_of(date_from), _period_of(date_to)
    if p_from:
        domain.append(("period", ">=", p_from))
    if p_to:
        domain.append(("period", "<=", p_to))
    rows_by_period = {}
    for cert in Cert.search(domain, order="period"):
        row = rows_by_period.setdefault(
            cert.period,
            {
                "period": cert.period,
                "certificates": 0,
                "draft": 0.0,
                "verified": 0.0,
                "settled": 0.0,
                "claimed": 0.0,
                "total": 0.0,
            },
        )
        row["certificates"] += 1
        row[cert.state] += cert.vds_amount
        row["total"] += cert.vds_amount
    rows = [
        {k: (round(v, 2) if isinstance(v, float) else v) for k, v in r.items()}
        for r in rows_by_period.values()
    ]
    cols = ["period", "certificates", "draft", "verified", "settled", "claimed", "total"]
    totals = {"period": "Total"}
    for c in cols[1:]:
        totals[c] = round(sum(r[c] for r in rows), 2)
    return {
        "title": "VDS received (Mushak 6.6) by VAT period",
        "cols": cols,
        "labels": {
            "period": "VAT Period",
            "certificates": "Certificates",
            "draft": "Draft",
            "verified": "Verified",
            "settled": "Settled — to claim in 9.1",
            "claimed": "Claimed in 9.1",
            "total": "Total VDS",
        },
        "rows": rows,
        "totals": totals if rows else None,
        "empty": "No VDS certificates recorded for these periods.",
        "notes": [
            "Settled certificates have cleared the receivable (Dr VDS receivable / Cr AR) "
            "and await the Mushak 9.1 VDS adjustment; the tax return marks them claimed.",
        ],
    }


# ---------------------------------------------------------------------------
# The registry's six AR reports. Each is a live computation over the real
# models (fix.ar.invoice / receipt / credit.note / dispute / dunning /
# segment.membership); nothing is invented and an empty basis says so.
# ---------------------------------------------------------------------------

AGE_SLOTS = ("current", "d1_30", "d31_60", "d61_90", "d90_plus")


def _open_invoices(env):
    """Issued invoices with a residual, company-scoped."""
    return (
        env["fix.ar.invoice"]
        .search([("company_id", "in", env.companies.ids), ("state", "=", "issued")])
        .filtered(lambda i: i.amount_residual > 0.005)
    )


def _age_slot(inv, today):
    days_past = (today - inv.invoice_date).days - inv._payment_terms_days()
    if days_past <= 0:
        return "current"
    if days_past <= 30:
        return "d1_30"
    if days_past <= 60:
        return "d31_60"
    if days_past <= 90:
        return "d61_90"
    return "d90_plus"


def _takeon_open(env, as_of=None):
    """Each customer's legacy take-on still open on the AR control (journal
    MIG, cd_billing_engine.account_code.ar), in the caller's companies:
    [{"company", "partner_id" (commercial; 0 = no party), "residual",
    "date"}]. None when the caller may not read the GL (the AR ledger lines
    are finance-only); the reports then say so instead of hiding it."""
    if not env["account.move.line"].has_access("read"):
        return None
    from odoo.addons.cd_billing_engine.models.fix_ar_engine import takeon_ar_opening

    out = []
    for company in env.companies:
        for partner_id, opening in takeon_ar_opening(env, company, as_of=as_of).items():
            if abs(opening["residual"]) > 0.005:
                out.append(
                    {
                        "company": company,
                        "partner_id": partner_id,
                        "residual": opening["residual"],
                        "date": opening["date"],
                    }
                )
    return out


def _takeon_slot(opening, today):
    """Aged from the take-on date (the lines' due date)."""
    from odoo.addons.cd_billing_engine.models.fix_ar_engine import age_slot

    return age_slot((today - opening["date"]).days)


def _opening_label(on):
    from odoo.addons.cd_billing_engine.models.fix_ar_engine import takeon_label

    return takeon_label(on)


TAKEON_NOTE = (
    "Opening balances taken on from the legacy system (journal MIG, one line per party "
    "on the AR control) are listed as their own line, 'Opening balance (take-on <date>)', "
    "at what is still open on them and aged from the take-on date."
)
TAKEON_HIDDEN = (
    "Opening balances taken on from the legacy system are GL lines, visible to finance "
    "roles only: they are not in this table for your role."
)


def _party_key(partner):
    """The commercial entity a balance belongs to; a party whose stored
    commercial partner is unset (raw-loaded rows) is its own; 0 = none."""
    return (partner.commercial_partner_id or partner).id or 0


def _ar_window(date_from, date_to):
    start = _as_date(date_from, None)
    end = _as_date(date_to, None)
    return start, end


def ageing_by_segment(env, date_from=None, date_to=None, **params):
    """Open AR bucketed by the customer's CURRENT segment membership. The
    bucket boundary is the invoice date plus the customer's own credit terms
    (fix.credit.profile), exactly the rule the ageing jobs use."""
    today = _as_date(date_to, datetime.date.today())
    invoices = _open_invoices(env)
    takeon = _takeon_open(env, as_of=today)
    partner_ids = sorted(
        set(invoices.mapped("customer_id").ids)
        | {t["partner_id"] for t in takeon or [] if t["partner_id"]}
    )
    segment_of = {}
    if partner_ids:
        for mem in env["fix.segment.membership"].search(
            [("partner_id", "in", partner_ids), ("exited_at", "=", False)]
        ):
            segment_of.setdefault(mem.partner_id.id, mem.segment_id.name or "Unsegmented")
    by_seg = {}
    for inv in invoices:
        seg = segment_of.get(inv.customer_id.id) or "Unsegmented"
        row = by_seg.setdefault(
            seg, {"segment": seg, "invoices": 0, "total": 0.0, **{s: 0.0 for s in AGE_SLOTS}}
        )
        row["invoices"] += 1
        row[_age_slot(inv, today)] += inv.amount_residual
        row["total"] += inv.amount_residual
    for opening in takeon or []:
        seg = segment_of.get(opening["partner_id"]) or "Unsegmented"
        key = "%s · %s" % (seg, _opening_label(opening["date"]))
        row = by_seg.setdefault(
            key, {"segment": key, "invoices": 0, "total": 0.0, **{s: 0.0 for s in AGE_SLOTS}}
        )
        row[_takeon_slot(opening, today)] += opening["residual"]
        row["total"] += opening["residual"]
    rows = [
        {k: (round(v, 2) if isinstance(v, float) else v) for k, v in r.items()}
        for r in sorted(by_seg.values(), key=lambda r: -r["total"])
    ]
    cols = ["segment", "invoices", *list(AGE_SLOTS), "total"]
    totals = {"segment": "Total", "invoices": sum(r["invoices"] for r in rows)}
    for c in (*AGE_SLOTS, "total"):
        totals[c] = round(sum(r[c] for r in rows), 2)
    return {
        "title": "AR Ageing by Customer Segment — as of %s" % today,
        "cols": cols,
        "labels": {
            "segment": "Customer Segment",
            "invoices": "Open Invoices",
            "current": "Current",
            "d1_30": "1-30",
            "d31_60": "31-60",
            "d61_90": "61-90",
            "d90_plus": "90+",
            "total": "Total Open",
        },
        "rows": rows,
        "totals": totals if rows else None,
        "empty": "No open issued invoices or opening balances — nothing to age.",
        "notes": [
            "Each invoice is aged by the days since its invoice date less the customer's own "
            "credit terms; segments are the customer's current segment memberships.",
            TAKEON_NOTE if takeon is not None else TAKEON_HIDDEN,
        ],
    }


def dunning_effectiveness(env, date_from=None, date_to=None, **params):
    """The NT-006 ladder's effectiveness: per step, how many reminders were
    recorded, how much overdue they cover, how many are suppressed, and how
    many of those invoices have since been paid or credited."""
    runs = env["fix.dunning"].search([("company_id", "in", env.companies.ids)])
    by_step = {}
    for d in runs:
        row = by_step.setdefault(
            d.step,
            {
                "step": d.step,
                "reminders": 0,
                "invoices": set(),
                "overdue": 0.0,
                "suppressed": 0,
                "recovered": 0,
            },
        )
        row["reminders"] += 1
        row["invoices"].add(d.invoice_id.id)
        row["overdue"] += d.overdue_amount or 0.0
        if d.suppressed:
            row["suppressed"] += 1
        if d.invoice_id.state in ("paid", "credited"):
            row["recovered"] += 1
    rows = []
    for step in ("reminder", "final", "escalate"):
        r = by_step.get(step)
        if not r:
            continue
        rows.append(
            {
                "step": step,
                "reminders": r["reminders"],
                "invoices": len(r["invoices"]),
                "overdue": round(r["overdue"], 2),
                "suppressed": r["suppressed"],
                "recovered": r["recovered"],
                "recovery_pct": round(r["recovered"] / r["reminders"] * 100.0, 1)
                if r["reminders"]
                else 0.0,
            }
        )
    totals = {
        "step": "Total",
        "reminders": sum(r["reminders"] for r in rows),
        "invoices": sum(r["invoices"] for r in rows),
        "overdue": round(sum(r["overdue"] for r in rows), 2),
        "suppressed": sum(r["suppressed"] for r in rows),
        "recovered": sum(r["recovered"] for r in rows),
    }
    totals["recovery_pct"] = (
        round(totals["recovered"] / totals["reminders"] * 100.0, 1) if totals["reminders"] else 0.0
    )
    return {
        "title": "Dunning Effectiveness — NT-006 ladder, live",
        "cols": [
            "step",
            "reminders",
            "invoices",
            "overdue",
            "suppressed",
            "recovered",
            "recovery_pct",
        ],
        "labels": {
            "step": "Ladder Step",
            "reminders": "Reminders",
            "invoices": "Distinct Invoices",
            "overdue": "Overdue Covered",
            "suppressed": "Suppressed",
            "recovered": "Recovered (paid/credited)",
            "recovery_pct": "Recovery %",
        },
        "rows": rows,
        "totals": totals if rows else None,
        "empty": "No dunning runs yet — run the ladder from the Dunning Worklist.",
        "notes": [
            "One row per ladder step; 'recovered' counts invoices now paid or credited. "
            "Suppressed invoices (dispute / payment plan / strategic) are counted, never hidden.",
        ],
    }


def payment_method_mix(env, date_from=None, date_to=None, **params):
    """Receipts by tender over the window: captured and confirmed values,
    the confirmed share, and money still unapplied."""
    start, end = _ar_window(date_from, date_to)
    domain = [("company_id", "in", env.companies.ids)]
    if start:
        domain.append(("receipt_date", ">=", start))
    if end:
        domain.append(("receipt_date", "<=", end))
    receipts = env["fix.ar.receipt"].search(domain)
    by_method = {}
    for r in receipts:
        row = by_method.setdefault(
            r.method,
            {"method": r.method, "receipts": 0, "amount": 0.0, "confirmed": 0.0, "unapplied": 0.0},
        )
        row["receipts"] += 1
        row["amount"] += r.amount
        if r.state == "confirmed":
            row["confirmed"] += r.amount
            row["unapplied"] += r.unapplied_amount
    confirmed_total = sum(r["confirmed"] for r in by_method.values())
    rows = []
    for r in sorted(by_method.values(), key=lambda r: -r["amount"]):
        r["share_pct"] = (
            round(r["confirmed"] / confirmed_total * 100.0, 1) if confirmed_total else 0.0
        )
        rows.append({k: (round(v, 2) if isinstance(v, float) else v) for k, v in r.items()})
    totals = {
        "method": "Total",
        "receipts": sum(r["receipts"] for r in rows),
        "amount": round(sum(r["amount"] for r in rows), 2),
        "confirmed": round(confirmed_total, 2),
        "unapplied": round(sum(r["unapplied"] for r in rows), 2),
        "share_pct": 100.0 if confirmed_total else 0.0,
    }
    return {
        "title": "Payment Method Mix — receipts by tender",
        "cols": ["method", "receipts", "amount", "confirmed", "share_pct", "unapplied"],
        "labels": {
            "method": "Tender",
            "receipts": "Receipts",
            "amount": "Captured",
            "confirmed": "Confirmed",
            "share_pct": "Share of Confirmed %",
            "unapplied": "Unapplied",
        },
        "rows": rows,
        "totals": totals if rows else None,
        "empty": "No receipts captured in this period.",
        "notes": [
            "Only CONFIRMED receipts move money (draft captures are listed in the workbook but "
            "do not count as collected). Share is of confirmed value.",
        ],
    }


def invoice_accuracy(env, date_from=None, date_to=None, **params):
    """Invoice accuracy: the share of invoiced value issued without a credit
    note or dispute, plus the exception list (each invoice with its credits,
    open disputes and reason)."""
    start, end = _ar_window(date_from, date_to)
    domain = [("company_id", "in", env.companies.ids), ("state", "!=", "draft")]
    if start:
        domain.append(("invoice_date", ">=", start))
    if end:
        domain.append(("invoice_date", "<=", end))
    invoices = env["fix.ar.invoice"].search(domain)
    rows = []
    invoiced = credited = disputed = 0.0
    for inv in invoices:
        inv_credits = sum(n.amount for n in inv.credit_note_ids if n.state == "issued")
        open_disputes = sum(
            d.amount_disputed
            for d in env["fix.ar.dispute"].search(
                [("invoice_id", "=", inv.id), ("state", "=", "open")]
            )
        )
        invoiced += inv.total_payable
        credited += inv_credits
        disputed += open_disputes
        if inv_credits <= 0.005 and open_disputes <= 0.005:
            continue
        reason = ""
        issued_notes = inv.credit_note_ids.filtered(lambda n: n.state == "issued")
        if issued_notes:
            reason = dict(issued_notes[0]._fields["reason_code"].selection).get(
                issued_notes[0].reason_code, issued_notes[0].reason_code
            )
        elif open_disputes > 0.005:
            d = env["fix.ar.dispute"].search(
                [("invoice_id", "=", inv.id), ("state", "=", "open")], limit=1
            )
            reason = d.reason or "Dispute"
        rows.append(
            {
                "invoice": inv.name or "AR/%s" % inv.id,
                "customer": inv.customer_id.name,
                "date": str(inv.invoice_date),
                "total": round(inv.total_payable, 2),
                "credited": round(inv_credits, 2),
                "disputed": round(open_disputes, 2),
                "reason": reason,
                "state": inv.state,
            }
        )
    accuracy = round((1.0 - (credited + disputed) / invoiced) * 100.0, 1) if invoiced else None
    totals = {
        "invoice": "Total",
        "total": round(invoiced, 2),
        "credited": round(credited, 2),
        "disputed": round(disputed, 2),
        "reason": "Accuracy %",
        "state": accuracy,
    }
    return {
        "title": "Invoice Accuracy — first-time-right, exceptions listed",
        "cols": ["invoice", "customer", "date", "total", "credited", "disputed", "reason", "state"],
        "labels": {
            "invoice": "Invoice",
            "customer": "Customer",
            "date": "Date",
            "total": "Invoice Total",
            "credited": "Credited (issued notes)",
            "disputed": "Open Disputed",
            "reason": "Reason",
            "state": "State / Accuracy %",
        },
        "rows": rows,
        "totals": totals if invoices else None,
        "empty": "No issued invoices in this period.",
        "notes": [
            "Accuracy % = 1 − (issued credit value + open disputed value) / invoiced value. "
            "Draft/rejected credit notes are excluded — only issued credits touched the books.",
        ],
    }


def brand_receivable_ageing(env, date_from=None, date_to=None, **params):
    """Brand/warranty-claim receivables only (source_model names a claim
    source). Until M08/M12 claim events feed the ledger the table is honestly
    empty — it never re-labels ordinary customer invoices as brand claims."""
    today = _as_date(date_to, datetime.date.today())
    invoices = _open_invoices(env).filtered(
        lambda i: "brand" in (i.source_model or "").lower()
        or "claim" in (i.source_model or "").lower()
    )
    rows = []
    # a brand's own legacy take-on: the OEM billing partner is the res.partner
    # whose ref is a brand code (the warranty-claim hand-off's own rule)
    takeon = _takeon_open(env, as_of=today)
    brand_partners = set()
    if takeon and "fix.brand" in env:
        codes = [c for c in env["fix.brand"].sudo().search([]).mapped("code") if c]
        if codes:
            brand_partners = {
                _party_key(p) for p in env["res.partner"].sudo().search([("ref", "in", codes)])
            }
    Partner = env["res.partner"].sudo()
    for opening in takeon or []:
        if opening["partner_id"] not in brand_partners:
            continue
        rows.append(
            {
                "invoice": _opening_label(opening["date"]),
                "customer": Partner.browse(opening["partner_id"]).name,
                "date": str(opening["date"]),
                "residual": round(opening["residual"], 2),
                "bucket": _takeon_slot(opening, today),
                "state": "take-on",
            }
        )
    for inv in invoices:
        rows.append(
            {
                "invoice": inv.name or "AR/%s" % inv.id,
                "customer": inv.customer_id.name,
                "date": str(inv.invoice_date),
                "residual": round(inv.amount_residual, 2),
                "bucket": _age_slot(inv, today),
                "state": inv.state,
            }
        )
    totals = {
        "invoice": "Total",
        "residual": round(sum(r["residual"] for r in rows), 2),
    }
    return {
        "title": "Brand Receivable Ageing — claim-source invoices only",
        "cols": ["invoice", "customer", "date", "residual", "bucket", "state"],
        "labels": {
            "invoice": "Invoice",
            "customer": "Brand / Customer",
            "date": "Invoice Date",
            "residual": "Open Residual",
            "bucket": "Ageing Bucket",
            "state": "State",
        },
        "rows": rows,
        "totals": totals if rows else None,
        "empty": "No brand-claim invoices yet — M08/M12 claim events are the source (FR-ARB-009).",
        "notes": [
            "Only invoices raised for a brand or warranty claim are included; ordinary "
            "customer invoices are never reported as brand receivables.",
            "A brand's opening balance taken on from the legacy system (the partner whose ref "
            "is the brand code) is its own line, aged from the take-on date."
            if takeon is not None
            else TAKEON_HIDDEN,
        ],
    }


def collections_productivity(env, date_from=None, date_to=None, **params):
    """Collections output per operating unit over the window: confirmed
    receipts, value collected, average receipt, unapplied cash and dunning
    actions recorded."""
    start, end = _ar_window(date_from, date_to)
    r_domain = [("company_id", "in", env.companies.ids), ("state", "=", "confirmed")]
    if start:
        r_domain.append(("receipt_date", ">=", start))
    if end:
        r_domain.append(("receipt_date", "<=", end))
    receipts = env["fix.ar.receipt"].search(r_domain)
    d_domain = [("company_id", "in", env.companies.ids)]
    if start:
        d_domain.append(("step_date", ">=", start))
    if end:
        d_domain.append(("step_date", "<=", end))
    dunning = env["fix.dunning"].search(d_domain)
    by_ou = {}
    for r in receipts:
        key = r.operating_unit_id.name or "Unassigned"
        row = by_ou.setdefault(
            key, {"unit": key, "receipts": 0, "collected": 0.0, "unapplied": 0.0, "dunning": 0}
        )
        row["receipts"] += 1
        row["collected"] += r.amount
        row["unapplied"] += r.unapplied_amount
    for d in dunning:
        key = d.operating_unit_id.name or "Unassigned"
        row = by_ou.setdefault(
            key, {"unit": key, "receipts": 0, "collected": 0.0, "unapplied": 0.0, "dunning": 0}
        )
        row["dunning"] += 1
    rows = []
    for r in sorted(by_ou.values(), key=lambda r: -r["collected"]):
        r["avg_receipt"] = round(r["collected"] / r["receipts"], 2) if r["receipts"] else 0.0
        rows.append({k: (round(v, 2) if isinstance(v, float) else v) for k, v in r.items()})
    totals = {
        "unit": "Total",
        "receipts": sum(r["receipts"] for r in rows),
        "collected": round(sum(r["collected"] for r in rows), 2),
        "avg_receipt": round(
            sum(r["collected"] for r in rows) / sum(r["receipts"] for r in rows), 2
        )
        if sum(r["receipts"] for r in rows)
        else 0.0,
        "unapplied": round(sum(r["unapplied"] for r in rows), 2),
        "dunning": sum(r["dunning"] for r in rows),
    }
    return {
        "title": "Collections Productivity — confirmed receipts per operating unit",
        "cols": ["unit", "receipts", "collected", "avg_receipt", "unapplied", "dunning"],
        "labels": {
            "unit": "Operating Unit",
            "receipts": "Confirmed Receipts",
            "collected": "Collected",
            "avg_receipt": "Avg Receipt",
            "unapplied": "Unapplied Cash",
            "dunning": "Dunning Actions",
        },
        "rows": rows,
        "totals": totals if rows else None,
        "empty": "No confirmed receipts or dunning actions in this period.",
        "notes": [
            "Collected value counts confirmed receipts only; drafts are excluded. "
            "Dunning actions are ladder records with a step date in the window.",
        ],
    }


def ar_subledger_gl_recon(env, date_from=None, date_to=None, **params):
    """M20-4: the AR sub-ledger against the GL control account, per customer.
    Sub-ledger = what the receipts, credits, VDS and write-offs leave open on
    issued and paid invoices, less money received but not yet applied; GL = the
    posted balance of the AR account for that customer. A difference is listed,
    never adjusted. Read as the caller, in the caller's companies."""
    from odoo.addons.cd_billing_engine.models.fix_ar_engine import _ar_account

    labels = {
        "company": "Company",
        "customer": "Customer",
        "invoices_open": "Open on Invoices",
        "takeon_open": "Opening Balance (take-on)",
        "unapplied": "Unapplied Receipts",
        "subledger": "Sub-ledger Balance",
        "gl": "GL Balance",
        "difference": "Difference",
    }
    cols = list(labels)
    title = "AR Sub-ledger to GL Reconciliation"
    if not env["account.move.line"].has_access("read"):
        return _pack(
            title,
            cols,
            labels,
            [],
            ["Visible to finance roles only."],
            empty="Not available to your role.",
        )
    from odoo.addons.cd_billing_engine.models.fix_ar_engine import takeon_ar_opening

    rows = []
    notes = []
    takeon_dates = set()
    MoveLine = env["account.move.line"].sudo()
    Partner = env["res.partner"].sudo()
    for company in env.companies:
        ar = _ar_account(env, company, "ar")
        if not ar:
            notes.append(
                "%s has no AR account configured (cd_billing_engine.account_code.ar): not "
                "reconciled." % company.name
            )
            continue
        side = {}
        for inv in env["fix.ar.invoice"].search(
            [("company_id", "=", company.id), ("state", "in", ("issued", "paid"))]
        ):
            key = _party_key(inv.customer_id)
            side.setdefault(key, [0.0, 0.0])[0] += inv.amount_residual
        for receipt in env["fix.ar.receipt"].search(
            [("company_id", "=", company.id), ("state", "=", "confirmed")]
        ):
            key = _party_key(receipt.customer_id)
            side.setdefault(key, [0.0, 0.0])[1] += receipt.unapplied_amount
        # the legacy take-on still open is part of the customer's sub-ledger
        # (without it every taken-on customer showed a false difference)
        takeon = {}
        for key, opening in takeon_ar_opening(env, company).items():
            if abs(opening["residual"]) > 0.005:
                takeon[key] = opening["residual"]
                takeon_dates.add(opening["date"])
        gl = {}
        for line in MoveLine.search(
            [
                ("company_id", "=", company.id),
                ("account_id", "=", ar.id),
                ("parent_state", "=", "posted"),
            ]
        ):
            key = _party_key(line.partner_id)
            gl[key] = gl.get(key, 0.0) + line.balance
        for key in sorted(set(side) | set(gl) | set(takeon)):
            open_amount, unapplied = side.get(key, (0.0, 0.0))
            opening = takeon.get(key, 0.0)
            balance = round(gl.get(key, 0.0), 2)
            subledger = round(open_amount + opening - unapplied, 2)
            if not key and abs(subledger) < 0.005 and abs(balance) < 0.005:
                continue  # party-less lines that net to nothing (a take-on and its rollback)
            rows.append(
                {
                    "company": company.name,
                    "customer": Partner.browse(key).name if key else "(no customer on the GL line)",
                    "invoices_open": round(open_amount, 2),
                    "takeon_open": round(opening, 2),
                    "unapplied": round(unapplied, 2),
                    "subledger": subledger,
                    "gl": balance,
                    "difference": round(subledger - balance, 2),
                }
            )
    rows.sort(key=lambda r: -abs(r["difference"]))
    totals = {"company": "Total"}
    for col in cols[2:]:
        totals[col] = round(sum(r[col] for r in rows), 2)
    differing = sum(1 for r in rows if abs(r["difference"]) > 0.005)
    if takeon_dates:
        labels["takeon_open"] = "Opening Balance (take-on %s)" % ", ".join(
            str(d) for d in sorted(takeon_dates)
        )
    return _pack(
        "%s: %d customer(s) differ" % (title, differing),
        cols,
        labels,
        rows,
        [
            "Differences are listed for a person to explain and are never adjusted here. "
            "Largest differences first.",
            "Sub-ledger = open on invoices + the legacy take-on still open (journal MIG on "
            "the AR control) − unapplied receipts.",
            *notes,
        ],
        totals=totals if rows else None,
        empty="No receivable or AR posting in your companies.",
    )


def ecl_provision(env, date_from=None, date_to=None, **params):
    """IFRS 9 expected credit loss: exposure per ageing bucket x the loss rate
    stated on the run. Shows the movement against the provision already booked.

    A08 M20-5: read as the caller (finance roles only) in the caller's
    companies; the latest POSTED run, else the latest computed one — never a
    draft anyone could type."""
    Run = env["fix.ar.impairment"]
    if not Run.has_access("read"):
        return _pack(
            "IFRS 9 ECL Provision",
            ["bucket", "exposure", "rate", "provision"],
            {
                "bucket": "Ageing bucket",
                "exposure": "Exposure",
                "rate": "Loss rate %",
                "provision": "Provision",
            },
            [],
            ["The IFRS 9 provision is visible to finance roles only."],
            empty="Not available to your role.",
        )
    domain = [("company_id", "in", env.companies.ids)]
    runs = Run.search(
        [*domain, ("state", "=", "posted")], order="as_of desc, id desc", limit=1
    ) or Run.search([*domain, ("state", "=", "computed")], order="as_of desc, id desc", limit=1)
    rows = []
    if not runs:
        return _pack(
            "IFRS 9 ECL Provision - no run recorded",
            ["bucket", "exposure", "rate", "provision"],
            {
                "bucket": "Ageing bucket",
                "exposure": "Exposure",
                "rate": "Loss rate %",
                "provision": "Provision",
            },
            rows,
            [
                "No impairment run exists yet. Open a run, compute it from the open AR ageing "
                "and post the provision movement."
            ],
            empty="No impairment run.",
        )
    run = runs[0]
    for line in run.line_ids:
        rows.append(
            {
                "bucket": line.bucket_label,
                "exposure": round(line.exposure, 2),
                "rate": line.rate,
                "provision": round(line.provision, 2),
            }
        )
    return _pack(
        "IFRS 9 ECL Provision %s - %s (as of %s)" % (run.name, run.state, run.as_of),
        ["bucket", "exposure", "rate", "provision"],
        {
            "bucket": "Ageing bucket",
            "exposure": "Exposure",
            "rate": "Loss rate %",
            "provision": "Provision",
        },
        rows,
        [
            "Exposure comes from the open AR invoices aged against their due dates; the "
            "loss rate is the run's stated IFRS 9 simplified-approach rate. Movement to post: "
            "%s." % ("%.2f" % run.movement)
        ],
        totals={
            "bucket": "Total",
            "exposure": round(run.total_exposure, 2),
            "provision": round(run.total_provision, 2),
        },
        empty="No open receivable to provision.",
    )


# ---------------------------------------------------------------------------
# The M20 report screens as report packs (13 Nov 2026): AR Aging, Revenue
# Leakage and the Customer Statement render on bespoke screens; as packs
# they download as CSV/Excel/PDF and go by email like every other built-in
# report, read through the SAME functions their screens call.
# ---------------------------------------------------------------------------
_AGE_COLS = ["current", "d1_30", "d31_60", "d61_90", "d90_plus"]


def ar_aging(env, **_params):
    from ..p03_ar_api import aging_live_rows

    rows = [dict(r, total=round(sum(r[c] for c in _AGE_COLS), 2)) for r in aging_live_rows(env)]
    rows.sort(key=lambda r: -r["total"])
    totals = {c: round(sum(r[c] for r in rows), 2) for c in [*_AGE_COLS, "total"]}
    totals["customer"] = "Total"
    return _pack(
        "AR Aging by Customer (as of %s)" % datetime.date.today(),
        ["customer", *_AGE_COLS, "total"],
        {
            "customer": "Customer",
            "current": "Current",
            "d1_30": "1-30 Days",
            "d31_60": "31-60 Days",
            "d61_90": "61-90 Days",
            "d90_plus": "Over 90 Days",
            "total": "Total Open",
        },
        rows,
        [
            "Open balances on issued invoices, aged from the invoice date after the "
            "customer's payment terms.",
            "A customer's balance brought over from the legacy system is its own line, "
            "aged from the take-on date.",
        ],
        totals=totals,
        empty="No customer has an open balance.",
    )


def revenue_leakage(env, **_params):
    from odoo.addons.cd_billing_engine.models.fix_ar_engine import compute_leakage

    data = compute_leakage(env)
    rows = [
        {
            "kind": "Closed order not invoiced",
            "reference": r["order"],
            "customer": r["customer"] or "",
            "age_days": r["age_days"],
            "detail": "Escalation: %s" % r["escalation"],
        }
        for r in data.get("unbilled_closed_orders") or []
    ]
    rows += [
        {
            "kind": "Billing event %s" % (r["state"] or "").replace("_", " "),
            "reference": r["source"],
            "customer": "",
            "age_days": r["age_days"],
            "detail": "%s attempt(s). %s" % (r["attempts"], r["error"] or ""),
        }
        for r in data.get("failed_events") or []
    ]
    return _pack(
        "Revenue Leakage",
        ["kind", "reference", "customer", "age_days", "detail"],
        {
            "kind": "Leak",
            "reference": "Reference",
            "customer": "Customer",
            "age_days": "Age (days)",
            "detail": "Detail",
        },
        rows,
        [
            "Service orders that were closed without an invoice, oldest first.",
            "Billing events that failed or were skipped; they stay listed until billed "
            "and never expire silently.",
        ],
        empty="No leakage: every closed order is invoiced and no billing event failed.",
    )


def customer_statement(env, customer_id=None, date_from=None, date_to=None, **_params):
    from odoo.addons.cd_billing_engine.models.fix_ar_engine import compute_customer_statement

    labels = {
        "date": "Date",
        "kind": "Type",
        "ref": "Reference",
        "detail": "Detail",
        "charge": "Charge / (Credit)",
        "running": "Balance",
    }
    cols = ["date", "kind", "ref", "detail", "charge", "running"]
    if not customer_id:
        return _pack(
            "Customer Statement",
            cols,
            labels,
            [],
            ["Choose a customer to produce a statement."],
            empty="No customer chosen.",
        )
    start = _as_date(date_from, datetime.date.today().replace(day=1))
    end = _as_date(date_to, datetime.date.today())
    stmt = compute_customer_statement(env, int(customer_id), start, end)
    name = env["res.partner"].browse(int(customer_id)).name or ""
    running = stmt["opening"]
    rows = [
        {
            "date": stmt["date_from"],
            "kind": "Opening",
            "ref": "",
            "detail": "Balance brought forward",
            "charge": None,
            "running": round(running, 2),
        }
    ]
    kinds = {"invoice": "Invoice", "credit": "Credit note", "receipt": "Receipt"}
    for r in stmt["rows"]:
        running = round(running + r["charge"], 2)
        rows.append(
            {
                "date": r["date"],
                "kind": kinds.get(r["kind"], (r["kind"] or "").title()),
                "ref": r["ref"],
                "detail": r["detail"] or "",
                "charge": r["charge"],
                "running": running,
            }
        )
    return _pack(
        "Statement of Account — %s" % name,
        cols,
        labels,
        rows,
        [
            "Opening balance %s; closing balance %s (BDT)."
            % (f"{stmt['opening']:,.2f}", f"{stmt['closing']:,.2f}"),
            "Invoices and credit notes count from their issue date; receipts from the "
            "date they were confirmed.",
        ],
        totals={"detail": "Closing balance", "running": stmt["closing"]},
        empty="No movement in this period.",
    )


REPORTS = {
    "ar_aging": ar_aging,
    "revenue_leakage": revenue_leakage,
    "customer_statement": customer_statement,
    "ecl_provision": ecl_provision,
    "ar_subledger_gl_recon": ar_subledger_gl_recon,
    "vds_claim_register": vds_claim_register,
    "ageing_by_segment": ageing_by_segment,
    "dunning_effectiveness": dunning_effectiveness,
    "payment_method_mix": payment_method_mix,
    "invoice_accuracy": invoice_accuracy,
    "brand_receivable_ageing": brand_receivable_ageing,
    "collections_productivity": collections_productivity,
}


def kpis(env):
    """VDS settled but not yet claimed in a 9.1 return (BDT)."""
    certs = env["fix.vds.certificate.received"].search(
        [("company_id", "in", env.companies.ids), ("state", "=", "settled")]
    )
    return {"vds_unclaimed": round(sum(certs.mapped("vds_amount")), 2)}
