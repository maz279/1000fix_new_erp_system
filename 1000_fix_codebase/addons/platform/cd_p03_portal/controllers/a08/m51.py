# A08 · M51 Tax & Regulatory (BD) — models the generic workspace screens may read,
# and the workflow methods they may call (/p03/model/records, /p03/model/action).
# Each entry: model -> {"order", "limit", "actions"}. Reads also need the
# user's own read access on the model (accounting/payroll groups apply).
# Only ARGUMENT-FREE workflow methods are listed: the workspace calls an
# action on the selected row without parameters.
from datetime import date

from odoo import fields

SURFACES = {
    "fix.mushak.register": {
        "order": "invoice_date desc, id desc",
        "limit": 200,
        "actions": {"action_mark_posted", "action_rebuild_from_events"},
    },
    "fix.vat.return": {
        "order": "period desc, id desc",
        "limit": 100,
        "actions": {"action_prepare", "action_subledger_reconciliation", "action_file_online"},
    },
    "fix.tds.return": {
        "order": "id desc",
        "limit": 100,
        "actions": {"action_prepare", "action_file"},
    },
    "fix.vat.treatment": {"order": "code", "limit": 200, "actions": set()},
    "fix.withholding.certificate": {"order": "id desc", "limit": 200, "actions": {"action_issue"}},
    "fix.withholding.line": {
        "order": "document_date desc, id desc",
        "limit": 300,
        "actions": {"action_issue_certificate"},
    },
    "fix.tax.challan": {
        "order": "challan_date desc, id desc",
        "limit": 200,
        "actions": {"action_link_open_deductions", "action_confirm_deposit"},
    },
    "fix.input.vat.credit": {
        "order": "invoice_date desc, id desc",
        "limit": 300,
        "actions": {"action_check_eligibility"},
    },
    "fix.tax.audit.pack": {
        "order": "date_to desc, id desc",
        "limit": 50,
        "actions": {"action_generate", "action_verify"},
    },
    "fix.tax.rate": {"order": "tax_kind, code, date_from desc", "limit": 300, "actions": set()},
    "fix.tax.parameter": {"order": "key, date_from desc", "limit": 100, "actions": set()},
    "fix.statutory.due.rule": {"order": "obligation", "limit": 100, "actions": set()},
    "fix.statutory.filing": {"order": "filed_on desc", "limit": 200, "actions": set()},
}


def _today(env):
    return fields.Date.context_today(env["res.users"])


def _num(v):
    return round(float(v or 0.0), 2)


def kpis(env):
    """Real M51 tile metrics (None = unreadable for the caller)."""
    out = {}
    try:
        ret = env["fix.vat.return"].search([], order="period desc", limit=1)
        labels = dict(ret._fields["state"].selection)
        out["vat91_latest"] = "%s %s" % (ret.period, labels.get(ret.state)) if ret else "none"
    except Exception:
        out["vat91_latest"] = None
    try:
        credits = env["fix.input.vat.credit"].search([("state", "=", "eligible")])
        out["input_credit_open"] = _num(sum(credits.mapped("signed_vat")))
    except Exception:
        out["input_credit_open"] = None
    try:
        out["certificates_due"] = env["fix.withholding.line"].search_count(
            [("state", "=", "deposited")]
        )
        out["withholding_undeposited"] = _num(
            sum(env["fix.withholding.line"].search([("state", "=", "withheld")]).mapped("amount"))
        )
    except Exception:
        out["certificates_due"] = out["withholding_undeposited"] = None
    try:
        today = _today(env)
        rows = env["fix.statutory.due.rule"].calendar(
            today.replace(day=1), date(today.year + 1, 12, 31)
        )
        upcoming = [r for r in rows if r["status"] in ("due", "overdue")]
        out["overdue_obligations"] = len([r for r in rows if r["status"] == "overdue"])
        out["next_due"] = str(upcoming[0]["due_date"]) if upcoming else "none"
    except Exception:
        out["overdue_obligations"] = out["next_due"] = None
    return out


STATUS_LABELS = {
    "done": "Done",
    "nothing_due": "Nothing due",
    "due": "Due",
    "overdue": "Overdue",
}


def statutory_calendar(env, date_from=None, date_to=None, **params):
    """Due dates computed from the due-day master (fix.statutory.due.rule),
    with status from the returns, deposits and filing evidence."""
    today = _today(env)
    d_from = fields.Date.to_date(date_from) if date_from else today.replace(day=1)
    d_to = fields.Date.to_date(date_to) if date_to else date(today.year, 12, 31)
    rows = []
    for r in env["fix.statutory.due.rule"].calendar(d_from, d_to):
        rule = r["rule"]
        rows.append(
            {
                "due_date": str(r["due_date"]),
                "obligation": rule.name,
                "period": r["period"],
                "authority": rule.authority or "",
                "status": STATUS_LABELS.get(r["status"], r["status"]),
                "detail": r["detail"],
                "basis": "verify with adviser" if rule.verify_with_adviser else "confirmed",
            }
        )
    return {
        "title": "Statutory calendar %s .. %s" % (d_from, d_to),
        "cols": ["due_date", "obligation", "period", "authority", "status", "detail", "basis"],
        "labels": {
            "due_date": "Due",
            "obligation": "Obligation",
            "period": "Period",
            "authority": "Authority",
            "status": "Status",
            "detail": "Evidence",
            "basis": "Due-day basis",
        },
        "rows": rows,
        "notes": "Due days are master data (Tax Rate Master > Statutory Calendar Rules); rows "
        "marked 'verify with adviser' were seeded from secondary sources. Weekend "
        "(Fri/Sat) and fixed public holidays roll forward; moon-dependent holidays are not "
        "applied.",
        "empty": "No statutory due dates in the period.",
    }


def mushak_610(env, date_from=None, date_to=None, **params):
    """Mushak 6.10 high-value register: sales (Mushak 6.3 issued) and
    purchases (supplier 6.3 received) above the threshold master value."""
    today = _today(env)
    d_from = fields.Date.to_date(date_from) if date_from else today.replace(day=1)
    d_to = fields.Date.to_date(date_to) if date_to else today
    threshold = env["fix.tax.parameter"].get_value("mushak610_threshold", d_to)
    rows = []
    sales = env["fix.mushak.register"].search(
        [("invoice_date", ">=", d_from), ("invoice_date", "<=", d_to)], order="invoice_date"
    )
    for s in sales.filtered(lambda r: r.total_payable > threshold):
        rows.append(
            {
                "side": "Sale",
                "date": str(s.invoice_date),
                "number": s.mushak_no,
                "party": s.customer_name,
                "bin": s.customer_bin or "",
                "taxable": _num(s.taxable_amount),
                "vat": _num(s.vat_amount),
                "total": _num(s.total_payable),
            }
        )
    purchases = env["fix.input.vat.credit"].search(
        [
            ("invoice_date", ">=", d_from),
            ("invoice_date", "<=", d_to),
            ("adjustment_type", "=", "invoice"),
        ],
        order="invoice_date",
    )
    for p in purchases.filtered(lambda r: r.taxable_amount + r.vat_amount > threshold):
        rows.append(
            {
                "side": "Purchase",
                "date": str(p.invoice_date),
                "number": p.supplier_mushak_no or "",
                "party": p.partner_id.display_name,
                "bin": p.supplier_bin or "",
                "taxable": _num(p.taxable_amount),
                "vat": _num(p.vat_amount),
                "total": _num(p.taxable_amount + p.vat_amount),
            }
        )
    rows.sort(key=lambda r: (r["date"], r["side"]))
    return {
        "title": "Mushak 6.10 high-value register (above BDT %s) %s .. %s"
        % (f"{threshold:,.0f}", d_from, d_to),
        "cols": ["side", "date", "number", "party", "bin", "taxable", "vat", "total"],
        "labels": {
            "side": "Side",
            "date": "Date",
            "number": "Mushak 6.3 No",
            "party": "Customer / Supplier",
            "bin": "BIN",
            "taxable": "Value",
            "vat": "VAT",
            "total": "Total",
        },
        "rows": rows,
        "notes": "Threshold from statutory parameter mushak610_threshold (seeded BDT 200,000, "
        "verify with adviser). Submitted with the 9.1 return.",
        "empty": "No invoice above the threshold in the period.",
    }


def note_register(env, date_from=None, date_to=None, **params):
    """Credit / debit note register (Mushak 6.7 / 6.8): vendor notes received
    (cd_ap_ext) and customer credit notes issued (cd_billing_engine)."""
    today = _today(env)
    d_from = fields.Date.to_date(date_from) if date_from else date(today.year, 1, 1)
    d_to = fields.Date.to_date(date_to) if date_to else today
    rows = []
    if "fix.vendor.note" in env:
        for n in env["fix.vendor.note"].search(
            [("note_date", ">=", d_from), ("note_date", "<=", d_to), ("state", "!=", "cancelled")],
            order="note_date",
        ):
            rows.append(
                {
                    "side": "Purchase",
                    "form": "6.7" if n.note_type == "decrease" else "6.8",
                    "date": str(n.note_date),
                    "number": n.mushak_ref or "",
                    "party": n.vendor_id.display_name,
                    "against": n.invoice_id.invoice_ref or "",
                    "value": _num(n.amount),
                    "vat": _num(n.vat_amount),
                    "state": dict(n._fields["state"].selection).get(n.state),
                }
            )
    if "fix.credit.note" in env:
        for c in env["fix.credit.note"].search(
            [("state", "=", "issued"), ("issued_at", ">=", d_from), ("issued_at", "<=", d_to)],
            order="issued_at",
        ):
            inv = c.invoice_id
            rows.append(
                {
                    "side": "Sale",
                    "form": "6.7",
                    "date": str(c.issued_at.date()) if c.issued_at else "",
                    "number": "CN/%s" % c.id,
                    "party": inv.customer_id.display_name,
                    "against": (inv.mushak_id.mushak_no if inv.mushak_id else inv.name) or "",
                    "value": _num(c.amount),
                    "vat": "",
                    "state": "Issued",
                }
            )
    rows.sort(key=lambda r: r["date"])
    return {
        "title": "Credit / debit note register (Mushak 6.7 / 6.8) %s .. %s" % (d_from, d_to),
        "cols": ["side", "form", "date", "number", "party", "against", "value", "vat", "state"],
        "labels": {
            "side": "Side",
            "form": "Mushak",
            "date": "Date",
            "number": "Note No",
            "party": "Party",
            "against": "Against Invoice",
            "value": "Value",
            "vat": "VAT",
            "state": "State",
        },
        "rows": rows,
        "notes": "Purchase-side notes carry the vendor's 6.7/6.8 number; customer credit notes "
        "are listed from AR (their VAT split is not stored on the AR credit note).",
        "empty": "No credit or debit notes in the period.",
    }


REPORTS = {
    "statutory_calendar": statutory_calendar,
    "mushak_610": mushak_610,
    "note_register": note_register,
}
