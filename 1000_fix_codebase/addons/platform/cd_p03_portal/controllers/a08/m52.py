# A08 · M52 AP & Employee Expense — models the generic workspace screens may read,
# and the workflow methods they may call (/p03/model/records, /p03/model/action).
# Each entry: model -> {"order", "limit", "actions"}. Reads also need the
# user's own read access on the model (accounting/payroll groups apply).
# REPORTS are computed over posted/real records with the caller's env.
#
# A08 audit (2026-11-04) M52-13: every transition is an action (the workflow
# and stamp fields are guarded on the models, so a /p03/model/write of
# approval_state / state / payment_state / submitted_by is refused), and the
# KPIs and reports read AS THE CALLER, filtered to the caller's companies
# (the run summary and the TDS register read every row as superuser).
from collections import defaultdict
from datetime import date

from odoo import fields

SURFACES = {
    # A08 S1 (M52-1): a payee bank-detail change is a proposal a second
    # person confirms; the account is not payable until then.
    "fix.payee.bank.change": {
        "order": "id desc",
        "limit": 200,
        "actions": {"action_propose", "action_confirm", "action_reject"},
    },
    # A08 M52-12: an AP approval-matrix change needs a second person.
    "fix.ap.approval.rule.change": {
        "order": "id desc",
        "limit": 200,
        "actions": {"action_apply", "action_reject"},
    },
    "fix.vendor.invoice": {
        "order": "invoice_date desc, id desc",
        "limit": 200,
        "actions": {
            "action_request_payment",
            "action_submit_approval",
            "action_approve",
            "action_reject",
            "action_reset_draft",
            "action_confirm_tds_category",
        },
    },
    "fix.expense.claim": {
        "order": "expense_date desc, id desc",
        "limit": 200,
        "actions": {"action_submit", "action_manager_approve", "action_approve", "action_reject"},
    },
    "fix.ap.approval.rule": {"order": "level", "limit": 50, "actions": set()},
    "fix.payment.run": {
        "order": "payment_date desc, id desc",
        "limit": 100,
        "actions": {
            "action_propose",
            "action_submit",
            "action_approve",
            "action_release",
            "action_sync_bank_status",
            "action_cancel",
        },
    },
    "fix.vendor.note": {
        "order": "note_date desc, id desc",
        "limit": 200,
        "actions": {"action_approve", "action_cancel"},
    },
    "fix.employee.advance": {
        "order": "request_date desc, id desc",
        "limit": 200,
        "actions": {
            "action_approve",
            "action_confirm_disbursement",
            "action_sync_disbursement",
            "action_settle",
            "action_record_recovery",
            "action_confirm_payroll_recovery",
            "action_cancel",
        },
    },
    "fix.expense.rate": {"order": "rate_type, date_from desc", "limit": 200, "actions": set()},
    "fix.expense.policy": {"order": "category_id", "limit": 200, "actions": set()},
    "fix.vendor.tax.profile": {"order": "partner_id", "limit": 300, "actions": set()},
    "fix.expense.category": {"order": "id desc", "limit": 400, "actions": set()},
    "fix.expense.grade": {"order": "id desc", "limit": 400, "actions": set()},
    # A08 M52-7: a line's receipt is attached on the line's own form. Read as the
    # caller: a plain user sees the lines of their own claims only.
    "fix.expense.claim.line": {
        "order": "id desc",
        "limit": 400,
        "actions": set(),
        "rules": True,
    },
}


def _today(env):
    return fields.Date.context_today(env["res.users"])


def _num(v):
    return round(float(v or 0.0), 2)


def _companies(env):
    return [("company_id", "in", env.companies.ids)]


def kpis(env):
    """Real M52 tile metrics (None = the model is unreadable for the caller)."""
    out = {}
    month_start = _today(env).replace(day=1)
    co = _companies(env)
    try:
        Bill = env["fix.vendor.invoice"]
        out["vendor_bills_open"] = Bill.search_count(
            [*co, ("approval_state", "=", "approved"), ("payment_state", "!=", "paid")]
        )
        out["bills_to_approve"] = Bill.search_count([*co, ("approval_state", "=", "to_approve")])
        out["match_exceptions"] = Bill.search_count(
            [*co, ("match_state", "in", ("unmatched", "blocked"))]
        )
    except Exception:
        out["vendor_bills_open"] = out["bills_to_approve"] = out["match_exceptions"] = None
    try:
        out["expense_claims_pending"] = env["fix.expense.claim"].search_count(
            [*co, ("state", "=", "submitted")]
        )
    except Exception:
        out["expense_claims_pending"] = None
    try:
        lines = env["fix.withholding.line"].search(
            [
                *co,
                ("tax_kind", "=", "tds"),
                ("document_date", ">=", month_start),
                ("state", "!=", "cancelled"),
            ]
        )
        out["tds_mtd"] = _num(sum(lines.mapped("amount")))
    except Exception:
        out["tds_mtd"] = None
    try:
        out["payment_runs_open"] = env["fix.payment.run"].search_count(
            [*co, ("state", "in", ("proposed", "to_approve", "approved", "released"))]
        )
    except Exception:
        out["payment_runs_open"] = None
    try:
        # Duplicate catches YTD: bills this year that share a vendor+reference
        # or a vendor+amount+date with another live bill (the same detection
        # basis as the Duplicate Prevention Log).
        year_start = _today(env).replace(month=1, day=1)
        bills = env["fix.vendor.invoice"].search(
            [*co, ("approval_state", "!=", "rejected"), ("invoice_date", ">=", year_start)]
        )
        by_ref, by_amount = defaultdict(list), defaultdict(list)
        for bill in bills:
            vendor = bill.vendor_id.commercial_partner_id.id
            by_ref[(vendor, (bill.invoice_ref or "").strip().lower())].append(bill)
            by_amount[(vendor, bill.invoice_date, round(bill.gross_amount, 2))].append(bill)
        caught = set()
        for groups in (by_ref, by_amount):
            for group in groups.values():
                if len(group) >= 2:
                    caught.update(b.id for b in group)
        out["duplicate_catches_ytd"] = len(caught)
    except Exception:
        out["duplicate_catches_ytd"] = None
    return out


BUCKETS = [
    ("current", "Not Due"),
    ("d1_30", "1-30"),
    ("d31_60", "31-60"),
    ("d61_90", "61-90"),
    ("d90", "90+"),
]


def _bucket(days):
    if days <= 0:
        return "current"
    if days <= 30:
        return "d1_30"
    if days <= 60:
        return "d31_60"
    if days <= 90:
        return "d61_90"
    return "d90"


def ap_ageing(env, date_from=None, date_to=None, **params):
    """AP ageing by vendor: approved, unpaid bills by days past due at the
    as-of date (period end), less approved notes not yet netted."""
    as_of = fields.Date.to_date(date_to) if date_to else _today(env)
    bills = env["fix.vendor.invoice"].search(
        [
            *_companies(env),
            ("approval_state", "=", "approved"),
            ("payment_state", "!=", "paid"),
            ("invoice_date", "<=", as_of),
        ]
    )
    notes = env["fix.vendor.note"].search(
        [*_companies(env), ("state", "=", "approved"), ("note_date", "<=", as_of)]
    )
    by_vendor = defaultdict(lambda: dict.fromkeys([k for k, _ in BUCKETS], 0.0))
    for bill in bills:
        days = (as_of - (bill.due_date or bill.invoice_date)).days
        by_vendor[bill.vendor_id.commercial_partner_id.display_name][_bucket(days)] += (
            bill.total_payable
        )
    for note in notes:
        by_vendor[note.vendor_id.commercial_partner_id.display_name]["current"] += note.signed_total
    rows, totals = [], dict.fromkeys([k for k, _ in BUCKETS], 0.0)
    for vendor in sorted(by_vendor):
        vals = by_vendor[vendor]
        row = {"vendor": vendor, **{k: _num(v) for k, v in vals.items()}}
        row["total"] = _num(sum(vals.values()))
        rows.append(row)
        for k in totals:
            totals[k] += vals[k]
    totals = {k: _num(v) for k, v in totals.items()}
    totals["total"] = _num(sum(totals.values()))
    totals["vendor"] = "Total"
    return {
        "title": "AP Ageing as of %s" % as_of,
        "cols": ["vendor", *[k for k, _ in BUCKETS], "total"],
        "labels": {"vendor": "Vendor", **dict(BUCKETS), "total": "Total Open"},
        "rows": rows,
        "totals": totals,
        "notes": "Approved, unpaid bills net of TDS/VDS by days past due date; approved "
        "debit/credit notes not yet netted in a payment run are shown as not due.",
        "empty": "No approved, unpaid vendor bills.",
    }


def _receipt_dates(env, po_line_ids):
    """Last goods.received event per PO line (the receipt date), from the
    event outbox — metadata only, read as superuser."""
    if not po_line_ids or "fix.event.outbox" not in env:
        return {}
    events = (
        env["fix.event.outbox"]
        .sudo()
        .search(
            [
                ("event_type", "=", "goods.received"),
                ("aggregate", "=", "fix.purchase.order.line"),
                ("aggregate_id", "in", list(po_line_ids)),
            ],
            order="id",
        )
    )
    return {e.aggregate_id: e.create_date.date() for e in events}


def grni_accruals(env, date_from=None, date_to=None, **params):
    """Goods received not invoiced: per PO line, received quantity less the
    quantity on live vendor bills for that PO and product, at the PO price.
    Source: fix.purchase.order(.line).qty_received (cd_requisition GRN intake)."""
    if "fix.purchase.order.line" not in env:
        return {"cols": [], "rows": [], "empty": "No receipt source (cd_requisition) installed."}
    as_of = fields.Date.to_date(date_to) if date_to else _today(env)
    po_lines = env["fix.purchase.order.line"].search(
        [("qty_received", ">", 0), ("order_id.state", "!=", "cancelled")]
    )
    bills = env["fix.vendor.invoice"].search(
        [
            ("requisition_id", "in", po_lines.order_id.ids),
            ("approval_state", "!=", "rejected"),
        ]
    )
    invoiced = defaultdict(float)
    for bill in bills:
        for line in bill.line_ids:
            invoiced[(bill.requisition_id.id, line.product_id.id)] += line.quantity
    received_on = _receipt_dates(env, po_lines.ids)
    rows, total = [], 0.0
    for pol in po_lines:
        order = pol.order_id
        key = (order.id, pol.product_id.id)
        # bills reference the PO and product: consume the invoiced quantity
        # across the PO's lines of that product in order
        consumed = min(invoiced.get(key, 0.0), pol.qty_received)
        invoiced[key] = invoiced.get(key, 0.0) - consumed
        open_qty = pol.qty_received - consumed
        if open_qty <= 0.0001:
            continue
        accrual = open_qty * pol.unit_price
        recd = received_on.get(pol.id)
        rows.append(
            {
                "po": order.name or "",
                "vendor": order.vendor_id.display_name,
                "product": pol.product_id.display_name,
                "received": _num(pol.qty_received),
                "invoiced": _num(pol.qty_received - open_qty),
                "open_qty": _num(open_qty),
                "unit_price": _num(pol.unit_price),
                "accrual": _num(accrual),
                "received_on": str(recd) if recd else "",
                "age_days": (as_of - recd).days if recd else "",
            }
        )
        total += accrual
    return {
        "title": "GRNI accruals as of %s" % as_of,
        "cols": [
            "po",
            "vendor",
            "product",
            "received",
            "invoiced",
            "open_qty",
            "unit_price",
            "accrual",
            "received_on",
            "age_days",
        ],
        "labels": {
            "po": "PO",
            "vendor": "Vendor",
            "product": "Product",
            "received": "Received",
            "invoiced": "Invoiced",
            "open_qty": "Not Invoiced",
            "unit_price": "PO Price",
            "accrual": "Accrual",
            "received_on": "Last Receipt",
            "age_days": "Age (days)",
        },
        "rows": rows,
        "totals": {"po": "Total", "accrual": _num(total)},
        "notes": "Receipts are the GRN quantities recorded on purchase orders (cd_requisition); "
        "receipt dates come from the goods.received events. The accrual is at the PO unit "
        "price, excluding VAT.",
        "empty": "No goods received awaiting a vendor bill.",
    }


def expense_by_category(env, date_from=None, date_to=None, **params):
    """Approved and paid expense claims by category for the period."""
    d_from = fields.Date.to_date(date_from) if date_from else date(1900, 1, 1)
    d_to = fields.Date.to_date(date_to) if date_to else _today(env)
    claims = env["fix.expense.claim"].search(
        [
            *_companies(env),
            ("state", "in", ("approved", "paid")),
            ("expense_date", ">=", d_from),
            ("expense_date", "<=", d_to),
        ]
    )
    agg = defaultdict(lambda: [0, 0.0])
    for claim in claims:
        if claim.line_ids:
            for line in claim.line_ids:
                agg[line.category_id.display_name][0] += 1
                agg[line.category_id.display_name][1] += line.amount
        else:
            agg["(no category lines)"][0] += 1
            agg["(no category lines)"][1] += claim.amount
    rows = [
        {"category": k, "lines": v[0], "amount": _num(v[1])}
        for k, v in sorted(agg.items(), key=lambda kv: -kv[1][1])
    ]
    return {
        "title": "Expense by category %s .. %s" % (d_from, d_to),
        "cols": ["category", "lines", "amount"],
        "labels": {"category": "Category", "lines": "Lines", "amount": "Amount"},
        "rows": rows,
        "totals": {"category": "Total", "amount": _num(sum(r["amount"] for r in rows))},
        "empty": "No approved expense claims in the period.",
    }


def duplicate_bills(env, date_from=None, date_to=None, **params):
    """Duplicate-prevention log: bills sharing a vendor and invoice reference
    (refused at submission), and same-vendor same-amount same-date pairs."""
    bills = env["fix.vendor.invoice"].search(
        [*_companies(env), ("approval_state", "!=", "rejected")]
    )
    by_ref, by_amount = defaultdict(list), defaultdict(list)
    for bill in bills:
        vendor = bill.vendor_id.commercial_partner_id.id
        by_ref[(vendor, (bill.invoice_ref or "").strip().lower())].append(bill)
        by_amount[(vendor, bill.invoice_date, round(bill.gross_amount, 2))].append(bill)
    rows = []
    for rule, groups in (("Same reference", by_ref), ("Same amount and date", by_amount)):
        for group in groups.values():
            if len(group) < 2:
                continue
            for bill in group:
                rows.append(
                    {
                        "rule": rule,
                        "vendor": bill.vendor_id.display_name,
                        "invoice_ref": bill.invoice_ref,
                        "invoice_date": str(bill.invoice_date),
                        "gross": _num(bill.gross_amount),
                        "approval": dict(bill._fields["approval_state"].selection).get(
                            bill.approval_state
                        ),
                    }
                )
    return {
        "title": "Duplicate prevention log",
        "cols": ["rule", "vendor", "invoice_ref", "invoice_date", "gross", "approval"],
        "labels": {
            "rule": "Rule",
            "vendor": "Vendor",
            "invoice_ref": "Vendor Ref",
            "invoice_date": "Date",
            "gross": "Gross",
            "approval": "Approval",
        },
        "rows": rows,
        "notes": "A bill whose vendor and reference match a live bill is refused at submission.",
        "empty": "No suspected duplicate bills.",
    }


def tds_register(env, date_from=None, date_to=None, **params):
    """TDS/VDS deduction register: every withholding line raised on vendor
    documents, with the challan and certificate state."""
    domain = [("tax_kind", "in", ("tds", "vds"))]
    if date_from:
        domain.append(("document_date", ">=", date_from))
    if date_to:
        domain.append(("document_date", "<=", date_to))
    try:
        lines = env["fix.withholding.line"].search(domain + _companies(env))
    except Exception:  # the caller cannot read the tax sub-ledger
        lines = env["fix.withholding.line"]
    rows = []
    for line in lines:
        rows.append(
            {
                "date": str(line.document_date),
                "kind": dict(line._fields["tax_kind"].selection).get(line.tax_kind, line.tax_kind),
                "vendor": line.partner_id.display_name if line.partner_id else "—",
                "section": line.section or "—",
                "base": _num(line.base_amount),
                "rate": _num(line.rate),
                "amount": _num(line.amount),
                "source": line.source_ref or "—",
                "challan": line.challan_no or "—",
                "state": dict(line._fields["state"].selection).get(line.state, line.state),
            }
        )
    rows.sort(key=lambda r: r["date"], reverse=True)
    return {
        "title": "TDS / VDS Deduction Register",
        "cols": [
            "date",
            "kind",
            "vendor",
            "section",
            "base",
            "rate",
            "amount",
            "source",
            "challan",
            "state",
        ],
        "labels": {
            "date": "Date",
            "kind": "Kind",
            "vendor": "Vendor",
            "section": "Section",
            "base": "Base",
            "rate": "Rate %",
            "amount": "Amount",
            "source": "Source Document",
            "challan": "Challan No",
            "state": "Certificate",
        },
        "rows": rows,
        "totals": {
            "date": "Total",
            "base": _num(sum(r["base"] for r in rows)),
            "amount": _num(sum(r["amount"] for r in rows)),
        },
        "notes": [
            "Every TDS/VDS line raised at source on vendor documents, with the "
            "deposit challan and the certificate lifecycle."
        ],
        "empty": "No TDS/VDS deductions recorded.",
    }


def payment_run_summary(env, date_from=None, date_to=None, **params):
    """Payment run summary: one row per run with bill counts, deductions and
    the net released to the bank, on the rails actually used."""
    try:
        runs = env["fix.payment.run"].search(_companies(env))
    except Exception:  # the caller holds no accounting role
        runs = env["fix.payment.run"]
    rows = []
    for run in runs:
        lines = run.line_ids
        rows.append(
            {
                "run": run.name,
                "payment_date": str(run.payment_date),
                "rail": dict(run._fields["rail"].selection).get(run.rail, run.rail),
                "bills": run.bill_count if "bill_count" in run._fields else len(lines),
                "gross": _num(sum(lines.mapped("gross_amount")))
                if lines
                else _num(run.total_amount),
                "tds": _num(run.total_tds),
                "vds": _num(run.total_vds),
                "net": _num(run.total_amount),
                "prepared": run.prepared_by.name if run.prepared_by else "—",
                "approved": run.approved_by.name if run.approved_by else "—",
                "state": dict(run._fields["state"].selection).get(run.state, run.state),
            }
        )
    rows.sort(key=lambda r: r["payment_date"], reverse=True)
    return {
        "title": "Payment Run Summary",
        "cols": [
            "run",
            "payment_date",
            "rail",
            "bills",
            "gross",
            "tds",
            "vds",
            "net",
            "prepared",
            "approved",
            "state",
        ],
        "labels": {
            "run": "Run",
            "payment_date": "Payment Date",
            "rail": "Rail",
            "bills": "Bills",
            "gross": "Gross",
            "tds": "TDS",
            "vds": "VDS",
            "net": "Net Released",
            "prepared": "Prepared By",
            "approved": "Approved By",
            "state": "State",
        },
        "rows": rows,
        "totals": {
            "run": "Total",
            "bills": sum(r["bills"] for r in rows),
            "gross": _num(sum(r["gross"] for r in rows)),
            "tds": _num(sum(r["tds"] for r in rows)),
            "vds": _num(sum(r["vds"] for r in rows)),
            "net": _num(sum(r["net"] for r in rows)),
        },
        "notes": [
            "One row per payment run; the net is what was released to the bank "
            "after TDS/VDS deductions."
        ],
        "empty": "No payment runs recorded.",
    }


REPORTS = {
    "ap_ageing": ap_ageing,
    "grni_accruals": grni_accruals,
    "expense_by_category": expense_by_category,
    "duplicate_bills": duplicate_bills,
    "tds_register": tds_register,
    "payment_run_summary": payment_run_summary,
}
