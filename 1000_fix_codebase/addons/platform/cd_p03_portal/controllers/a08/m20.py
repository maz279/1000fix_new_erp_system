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
        "actions": {"action_submit", "action_approve", "action_issue"},
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
    "fix.ar.consolidated.bill": {
        "order": "id desc",
        "limit": 400,
        "actions": {"action_generate", "action_send"},
    },
    "fix.ar.dispute": {"order": "id desc", "limit": 400, "actions": set()},
    "fix.dunning": {"order": "id desc", "limit": 400, "actions": set()},
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
    partner_ids = invoices.mapped("customer_id").ids
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
        "empty": "No open issued invoices — nothing to age.",
        "notes": [
            "Bucket boundary = (as-of date − invoice date) − the customer's own credit terms "
            "(fix.credit.profile); segments are the customer's current fix.segment memberships.",
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
            "Rows are restricted to invoices whose source is a brand/warranty claim "
            "(source_model contains 'brand' or 'claim'). Ordinary customer invoices are never "
            "reported as brand receivables.",
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
            {"bucket": "Ageing bucket", "exposure": "Exposure", "rate": "Loss rate %",
             "provision": "Provision"},
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


REPORTS = {
    "ecl_provision": ecl_provision,
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
