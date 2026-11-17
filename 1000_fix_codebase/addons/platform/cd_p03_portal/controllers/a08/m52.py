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
            "action_open_match_case",
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
    # Legacy AP register take-on (accounts_payable report 2026-11-09 §5.4):
    # the wizard's transitions run through the generic action route like
    # every other surface; the posting itself goes through the M19 funnel.
    "fix.ap.takeon.batch": {
        "order": "id desc",
        "limit": 50,
        "actions": {"action_stage", "action_validate", "action_post", "action_rollback"},
    },
    "fix.ap.takeon.line": {
        "order": "batch_id desc, row_no",
        "limit": 500,
        "actions": set(),
    },
    # M52 capture audit (2026-11-17): the records each sub-module page captures.
    "fix.ap.match.tolerance": {
        "order": "id desc",
        "limit": 200,
        "actions": {"action_submit", "action_approve", "action_reject"},
    },
    "fix.ap.match.exception": {"order": "id desc", "limit": 300, "actions": {"action_resolve"}},
    "fix.ap.dispute": {
        "order": "id desc",
        "limit": 300,
        "actions": {"action_resolve", "action_withdraw"},
    },
    "fix.ap.vendor.statement": {
        "order": "statement_date desc, id desc",
        "limit": 300,
        "actions": {"action_compare", "action_sign_off"},
    },
    "fix.ap.ageing.snapshot": {"order": "as_of desc, id desc", "limit": 200, "actions": set()},
    "fix.ap.ageing.snapshot.line": {"order": "id desc", "limit": 1000, "actions": set()},
    "fix.ap.grni.accrual": {
        "order": "period_end desc, id desc",
        "limit": 100,
        "actions": {"action_compute", "action_confirm"},
    },
    "fix.expense.card": {"order": "id desc", "limit": 300, "actions": set()},
    "fix.expense.card.transaction": {
        "order": "txn_date desc, id desc",
        "limit": 500,
        "actions": {"action_explain", "action_approve", "action_dispute", "action_reopen"},
    },
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


def ap_ageing(env, date_from=None, date_to=None, **params):
    """AP ageing by vendor: approved, unpaid bills by days past due at the
    as-of date (period end), less approved notes not yet netted. The same
    computation a kept ageing snapshot freezes."""
    from odoo.addons.cd_ap_ext.models.fix_ap_capture import BUCKETS, ageing_by_vendor

    as_of = fields.Date.to_date(date_to) if date_to else _today(env)
    by_vendor, takeon_note = ageing_by_vendor(env, env.companies, as_of)
    keys = [k for k, _ in BUCKETS]
    rows, totals = [], dict.fromkeys(keys, 0.0)
    for vendor in sorted(by_vendor):
        vals = by_vendor[vendor]
        row = {"vendor": vendor, **{k: _num(vals[k]) for k in keys}}
        row["total"] = _num(sum(vals[k] for k in keys))
        rows.append(row)
        for k in totals:
            totals[k] += vals[k]
    totals = {k: _num(v) for k, v in totals.items()}
    totals["total"] = _num(sum(totals.values()))
    totals["vendor"] = "Total"
    return {
        "title": "AP Ageing as of %s" % as_of,
        "cols": ["vendor", *keys, "total"],
        "labels": {"vendor": "Vendor", **dict(BUCKETS), "total": "Total Open"},
        "rows": rows,
        "totals": totals,
        "notes": "Approved, unpaid bills net of TDS/VDS by days past due date; approved "
        "debit/credit notes not yet netted in a payment run are shown as not due. " + takeon_note,
        "empty": "No approved, unpaid vendor bills or opening balances.",
    }


def grni_accruals(env, date_from=None, date_to=None, **params):
    """Goods received not invoiced: per PO line, received quantity less the
    quantity on live vendor bills for that PO and product, at the PO price.
    Source: the goods-received quantities on purchase orders (cd_requisition)."""
    if "fix.purchase.order.line" not in env:
        return {"cols": [], "rows": [], "empty": "No receipt source (cd_requisition) installed."}
    from odoo.addons.cd_ap_ext.models.fix_ap_capture import grni_rows

    as_of = fields.Date.to_date(date_to) if date_to else _today(env)
    rows, total = [], 0.0
    for r in grni_rows(env, as_of):
        pol = r["po_line"]
        recd = r["received_on"]
        rows.append(
            {
                "po": pol.order_id.name or "",
                "vendor": pol.order_id.vendor_id.display_name,
                "product": pol.product_id.display_name,
                "received": _num(r["received"]),
                "invoiced": _num(r["invoiced"]),
                "open_qty": _num(r["open_qty"]),
                "unit_price": _num(r["unit_price"]),
                "accrual": _num(r["accrual"]),
                "received_on": str(recd) if recd else "",
                "age_days": r["age_days"] if r["age_days"] is not None else "",
            }
        )
        total += r["accrual"]
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
        "notes": "Receipts are the goods-received quantities recorded on purchase orders, "
        "dated by their goods receipt. The accrual is valued at the purchase order unit "
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
