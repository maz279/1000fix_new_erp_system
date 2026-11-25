# A08 · M51 Tax & Regulatory (BD) — models the generic workspace screens may read,
# and the workflow methods they may call (/p03/model/records, /p03/model/action).
# Each entry: model -> {"order", "limit", "actions"}. Reads also need the
# user's own read access on the model (accounting/payroll groups apply).
# Only ARGUMENT-FREE workflow methods are listed: the workspace calls an
# action on the selected row without parameters.
from datetime import date, timedelta

from odoo import fields

# A08 workflow audit (2026-11-04) M51-13: the register's engine methods
# (action_mark_posted, action_rebuild_from_events) and the free-standing
# certificate issue (action_issue) are no longer workspace actions: a register
# row is posted by its invoice posting, the register rebuilds from events as an
# administrator's engine run, and a certificate is issued from its deposited
# deduction. Statutory master rows change by proposal + activation (M51-6).
MASTER_ACTIONS = {
    "action_record_adviser_verification",
    "action_cfo_signoff",
    "action_activate",
    "action_reject_proposal",
}

SURFACES = {
    "fix.mushak.register": {
        "order": "invoice_date desc, id desc",
        "limit": 200,
        "actions": set(),
    },
    "fix.mushak.correction": {
        "order": "id desc",
        "limit": 200,
        "actions": {"action_approve", "action_reject"},
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
    "fix.vat.treatment": {"order": "code", "limit": 200, "actions": set(MASTER_ACTIONS)},
    "fix.withholding.certificate": {"order": "id desc", "limit": 200, "actions": set()},
    "fix.withholding.line": {
        "order": "document_date desc, id desc",
        "limit": 300,
        "actions": {
            "action_issue_certificate",
            "action_apply_statutory_uplift",
            "action_request_void",
            "action_request_reopen",
            "action_approve_correction",
            "action_reject_correction",
            "action_clear_duplicate",
        },
    },
    "fix.tax.challan": {
        "order": "challan_date desc, id desc",
        "limit": 200,
        "actions": {
            "action_link_open_deductions",
            "action_record_verification",
            "action_confirm_deposit",
        },
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
    "fix.tax.rate": {
        "order": "tax_kind, code, date_from desc",
        "limit": 300,
        "actions": set(MASTER_ACTIONS),
    },
    "fix.tax.parameter": {
        "order": "key, date_from desc",
        "limit": 100,
        "actions": set(MASTER_ACTIONS),
    },
    "fix.statutory.due.rule": {"order": "obligation", "limit": 100, "actions": set(MASTER_ACTIONS)},
    "fix.statutory.filing": {"order": "filed_on desc", "limit": 200, "actions": set()},
    # M51 sub-module capture audit (2026-11-17)
    "fix.marketplace.tax.model": {
        "order": "company_id, date_from desc, id desc",
        "limit": 50,
        "actions": set(MASTER_ACTIONS),
    },
    "fix.vat.return.amendment": {
        "order": "id desc",
        "limit": 100,
        "actions": {"action_submit", "action_approve", "action_reject", "action_mark_filed"},
    },
    "fix.tax.notice": {
        "order": "response_due, id desc",
        "limit": 200,
        "actions": {"action_generate_pack", "action_record_response", "action_close"},
    },
}


# The statutory masters with a two-step sign-off, for the queue and the tile.
SIGNOFF_MASTERS = (
    ("fix.tax.rate", "Tax Rate"),
    ("fix.tax.parameter", "Statutory Parameter"),
    ("fix.vat.treatment", "VAT Treatment"),
    ("fix.statutory.due.rule", "Calendar Rule"),
    ("fix.marketplace.tax.model", "Marketplace VAT Model"),
)


def _companies(env):
    return [("company_id", "in", env.companies.ids)]


def _today(env):
    return fields.Date.context_today(env["res.users"])


def _num(v):
    return round(float(v or 0.0), 2)


def kpis(env):
    """Real M51 tile metrics (None = unreadable for the caller)."""
    out = {}
    try:
        ret = env["fix.vat.return"].search(_companies(env), order="period desc", limit=1)
        labels = dict(ret._fields["state"].selection)
        out["vat91_latest"] = "%s %s" % (ret.period, labels.get(ret.state)) if ret else "none"
    except Exception:
        out["vat91_latest"] = None
    try:
        credits = env["fix.input.vat.credit"].search([("state", "=", "eligible"), *_companies(env)])
        out["input_credit_open"] = _num(sum(credits.mapped("signed_vat")))
    except Exception:
        out["input_credit_open"] = None
    try:
        out["certificates_due"] = env["fix.withholding.line"].search_count(
            [("state", "=", "deposited"), *_companies(env)]
        )
        out["withholding_undeposited"] = _num(
            sum(
                env["fix.withholding.line"]
                .search([("state", "=", "withheld"), *_companies(env)])
                .mapped("amount")
            )
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
    try:
        out["signoff_pending"] = sum(
            env[model].search_count([("state", "=", "active"), ("signoff_state", "!=", "signed")])
            for model, _label in SIGNOFF_MASTERS
        )
    except Exception:
        out["signoff_pending"] = None
    try:
        # moved from the finance route so the module owns every tile metric
        out["mushak_records"] = env["fix.mushak.register"].search_count(_companies(env))
        out["vat_returns_count"] = env["fix.vat.return"].search_count(_companies(env))
    except Exception:
        out["mushak_records"] = out["vat_returns_count"] = None
    try:
        out["open_notices"] = env["fix.tax.notice"].search_count(
            [("state", "!=", "closed"), *_companies(env)]
        )
    except Exception:
        out["open_notices"] = None
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


def signoff_queue(env, date_from=None, date_to=None, **params):
    """BRU-TAX-22: every statutory master row in force or proposed that is not
    signed off by the adviser and the CFO, and the step it waits for. Rows in
    force keep working meanwhile (see fix_tax_master.ENFORCE_SIGNOFF_PARAM)."""
    next_step = {
        "adviser": "Record the adviser's written confirmation (Accounting Administrator)",
        "cfo": "CFO sign-off, by someone other than who recorded the confirmation",
    }
    rows = []
    for model, label in SIGNOFF_MASTERS:
        states = dict(env[model]._fields["state"].selection)
        stages = dict(env[model]._fields["signoff_state"].selection)
        for row in env[model].search(
            [("state", "in", ("active", "proposed")), ("signoff_state", "!=", "signed")]
        ):
            rows.append(
                {
                    "master": label,
                    "row": row.display_name,
                    "status": states.get(row.state),
                    "stage": stages.get(row.signoff_state),
                    "adviser": row.adviser_reference or "",
                    "next": next_step[row.signoff_state]
                    if row.state == "active" or row.signoff_state == "adviser"
                    else "CFO activates the proposal",
                }
            )
    return {
        "title": "Statutory master sign-off queue: %d row(s)" % len(rows),
        "cols": ["master", "row", "status", "stage", "adviser", "next"],
        "labels": {
            "master": "Master",
            "row": "Row",
            "status": "Status",
            "stage": "Waiting For",
            "adviser": "Adviser Confirmation",
            "next": "Next Step",
        },
        "rows": rows,
        "notes": [
            "Rates and parameters in force stay in use while they await sign-off, or every "
            "bill and invoice would stop; a deduction or Mushak line that uses one shows Rate "
            "Unconfirmed. Sign each one off on its own master screen (Tax Rate Master, "
            "Statutory Parameters, Tax Determination Service, Statutory Calendar Rules). Once "
            "this list is empty, an administrator can switch on enforcement so that an "
            "unsigned rate is refused."
        ],
        "empty": "Every statutory master row is signed off.",
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
        [("invoice_date", ">=", d_from), ("invoice_date", "<=", d_to), *_companies(env)],
        order="invoice_date",
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
            *_companies(env),
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


def vat_return_draft(env, date_from=None, date_to=None, **params):
    """Mushak 9.1 return draft: one row per VAT return with its computation."""
    rows = []
    for ret in env["fix.vat.return"].search(_companies(env)):
        rows.append(
            {
                "period": ret.period,
                "taxable": _num(ret.total_taxable),
                "output_vat": _num(ret.output_vat),
                "input_vat": _num(ret.input_vat),
                "net_payable": _num(ret.net_payable),
                "nil": "Yes" if ret.nil_return else "No",
                "due": str(ret.due_date or "—"),
                "state": dict(ret._fields["state"].selection).get(ret.state, ret.state),
            }
        )
    rows.sort(key=lambda r: r["period"], reverse=True)
    return {
        "title": "Mushak 9.1 Return Draft — computed per VAT period",
        "cols": [
            "period",
            "taxable",
            "output_vat",
            "input_vat",
            "net_payable",
            "nil",
            "due",
            "state",
        ],
        "labels": {
            "period": "Period",
            "taxable": "Taxable Value",
            "output_vat": "Output VAT",
            "input_vat": "Input VAT",
            "net_payable": "Net Payable",
            "nil": "Nil Return",
            "due": "Due Date",
            "state": "State",
        },
        "rows": rows,
        "totals": {
            "period": "Total",
            "taxable": _num(sum(r["taxable"] for r in rows)),
            "output_vat": _num(sum(r["output_vat"] for r in rows)),
            "input_vat": _num(sum(r["input_vat"] for r in rows)),
            "net_payable": _num(sum(r["net_payable"] for r in rows)),
        },
        "notes": "The draft is the ledger's computation per period; filing evidence lives on the "
        "Filing Evidence screen.",
        "empty": "No VAT returns recorded.",
    }


def vat_reconciliation(env, date_from=None, date_to=None, **params):
    """VAT reconciliation: the return's output/input VAT vs the source
    registers (Mushak sales records and input credits) for the same period."""
    # A08: read as the caller in their companies; the period key is YYYY-MM
    # (the old "%m-%y" key never matched a return, so every variance read 100%).
    returns = env["fix.vat.return"].search(_companies(env))
    mushak = env["fix.mushak.register"].search(_companies(env))
    credits = env["fix.input.vat.credit"].search([("state", "=", "claimed"), *_companies(env)])
    rows = []
    for ret in returns:
        period = ret.period
        sales_vat = sum(
            m.vat_amount
            for m in mushak
            if m.invoice_date and m.invoice_date.strftime("%Y-%m") == period
        )
        credit_vat = sum(c.signed_vat for c in credits if c.vat_return_id == ret)
        rows.append(
            {
                "period": period,
                "sales_records_vat": _num(sales_vat),
                "return_output_vat": _num(ret.output_vat),
                "output_variance": _num(ret.output_vat - sales_vat),
                "credit_register_vat": _num(credit_vat),
                "return_input_vat": _num(ret.input_vat),
                "input_variance": _num(ret.input_vat - credit_vat),
            }
        )
    rows.sort(key=lambda r: r["period"], reverse=True)
    mismatches = len(
        [r for r in rows if abs(r["output_variance"]) > 0.05 or abs(r["input_variance"]) > 0.05]
    )
    return {
        "title": "VAT Reconciliation — return vs source registers per period",
        "cols": [
            "period",
            "sales_records_vat",
            "return_output_vat",
            "output_variance",
            "credit_register_vat",
            "return_input_vat",
            "input_variance",
        ],
        "labels": {
            "period": "Period",
            "sales_records_vat": "Mushak Sales VAT",
            "return_output_vat": "Return Output VAT",
            "output_variance": "Output Variance",
            "credit_register_vat": "Input Credit Register",
            "return_input_vat": "Return Input VAT",
            "input_variance": "Input Variance",
        },
        "rows": rows,
        "notes": [
            "Output VAT per Mushak 6.2/6.3 sales records and input VAT per the credit "
            "register, compared with the filed return. %d period(s) with a variance." % mismatches
        ],
        "empty": "No VAT returns recorded.",
    }


def tds_annual_summary(env, date_from=None, date_to=None, **params):
    """TDS annual summary: the fiscal year's withholding grouped by statutory
    section, with deposited vs outstanding."""
    today = _today(env)
    fy_start = today.replace(month=7, day=1)
    if today.month < 7:
        fy_start = fy_start.replace(year=fy_start.year - 1)
    fy_end = fy_start.replace(year=fy_start.year + 1) - timedelta(days=1)
    lines = env["fix.withholding.line"].search(
        [
            ("tax_kind", "=", "tds"),
            ("document_date", ">=", fy_start),
            ("document_date", "<=", fy_end),
            ("state", "!=", "cancelled"),
            *_companies(env),
        ]
    )
    groups = {}
    for line in lines:
        key = line.section or "Unclassified"
        g = groups.setdefault(
            key, {"base": 0.0, "amount": 0.0, "deposited": 0.0, "deductees": set()}
        )
        g["base"] += float(line.base_amount or 0.0)
        g["amount"] += float(line.amount or 0.0)
        if line.state in ("deposited", "certified"):
            g["deposited"] += float(line.amount or 0.0)
        if line.partner_id:
            g["deductees"].add(line.partner_id.id)
    rows = [
        {
            "section": k,
            "base": _num(v["base"]),
            "withheld": _num(v["amount"]),
            "deposited": _num(v["deposited"]),
            "outstanding": _num(v["amount"] - v["deposited"]),
            "deductees": len(v["deductees"]),
        }
        for k, v in sorted(groups.items())
    ]
    unconfirmed = len(lines.filtered("rate_flagged"))
    return {
        "title": "TDS Annual Summary — FY %s-%s by statutory section"
        % (fy_start.year, fy_end.year),
        "cols": ["section", "base", "withheld", "deposited", "outstanding", "deductees"],
        "labels": {
            "section": "ITA Section",
            "base": "Base",
            "withheld": "Withheld",
            "deposited": "Deposited",
            "outstanding": "Outstanding",
            "deductees": "Deductees",
        },
        "rows": rows,
        "totals": {
            "section": "Total",
            "base": _num(sum(r["base"] for r in rows)),
            "withheld": _num(sum(r["withheld"] for r in rows)),
            "deposited": _num(sum(r["deposited"] for r in rows)),
            "outstanding": _num(sum(r["outstanding"] for r in rows)),
        },
        "notes": [
            "Bangladesh fiscal year (July-June); deposited means the deduction is covered by "
            "a deposit challan or a certificate.",
            "%d of %d deduction(s) use a rate not yet signed off by the adviser and the CFO "
            "(Sign-Off Queue)." % (unconfirmed, len(lines)),
        ],
        "empty": "No TDS withholding this fiscal year.",
    }


def vds_deduction_register(env, date_from=None, date_to=None, **params):
    """VDS deduction register: every VDS line with its challan and state."""
    domain = [("tax_kind", "=", "vds"), *_companies(env)]
    if date_from:
        domain.append(("document_date", ">=", date_from))
    if date_to:
        domain.append(("document_date", "<=", date_to))
    lines = env["fix.withholding.line"].search(domain)
    rows = []
    for line in lines:
        rows.append(
            {
                "date": str(line.document_date),
                "vendor": line.partner_id.display_name if line.partner_id else "—",
                "bin": line.partner_bin or "—",
                "base": _num(line.base_amount),
                "rate": _num(line.rate),
                "amount": _num(line.amount),
                "source": line.source_ref or "—",
                "challan": line.challan_no or "—",
                "state": dict(line._fields["state"].selection).get(line.state, line.state),
                "basis": "Rate unconfirmed" if line.rate_flagged else "Signed off",
            }
        )
    rows.sort(key=lambda r: r["date"], reverse=True)
    return {
        "title": "VDS Deduction Register (Mushak 6.6)",
        "cols": [
            "date",
            "vendor",
            "bin",
            "base",
            "rate",
            "amount",
            "source",
            "challan",
            "state",
            "basis",
        ],
        "labels": {
            "date": "Date",
            "vendor": "Vendor",
            "bin": "Vendor BIN",
            "base": "Base",
            "rate": "Rate %",
            "amount": "VDS",
            "source": "Source Document",
            "challan": "Challan No",
            "state": "State",
            "basis": "Rate Basis",
        },
        "rows": rows,
        "totals": {
            "date": "Total",
            "base": _num(sum(r["base"] for r in rows)),
            "amount": _num(sum(r["amount"] for r in rows)),
        },
        "notes": "VAT withheld at source on supplier bills, with the A-Challan deposit reference.",
        "empty": "No VDS deductions recorded.",
    }


def sd_at_liability(env, date_from=None, date_to=None, **params):
    """SD and AT liability from the assessed Bill of Entry duty cascade (M44).
    Import assessments are the only place the platform holds SD/AT amounts, so
    this pack reports them rather than inventing a domestic SD/AT estimate."""
    # A06 R4: a paid Bill of Entry is corrected by a reversal, so only assessed
    # and paid entries carry a liability; read as the caller, in their companies.
    boes = env["fix.import.boe"].search(
        [("state", "in", ("assessed", "paid")), ("company_id", "in", env.companies.ids)]
    )
    rows = []
    for boe in boes:
        rows.append(
            {
                "boe": boe.boe_no,
                "assessed_on": str(boe.assessed_on or "-"),
                "currency": boe.currency_id.name if boe.currency_id else "-",
                "cd": round(boe.cd_amount or 0.0, 2),
                "rd": round(boe.rd_amount or 0.0, 2),
                "sd": round(boe.sd_amount or 0.0, 2),
                "at": round(boe.at_amount or 0.0, 2),
                "vat": round(boe.vat_amount or 0.0, 2),
                "total": round(boe.total_tax or 0.0, 2),
            }
        )
    sd_total = round(sum(r["sd"] for r in rows), 2)
    at_total = round(sum(r["at"] for r in rows), 2)
    return {
        "title": "SD & AT Liability - %d assessed Bill of Entry record(s)" % len(rows),
        "cols": ["boe", "assessed_on", "currency", "cd", "rd", "sd", "at", "vat", "total"],
        "labels": {
            "boe": "Bill of Entry",
            "assessed_on": "Assessed On",
            "currency": "Currency",
            "cd": "CD",
            "rd": "RD",
            "sd": "SD",
            "at": "AT",
            "vat": "VAT",
            "total": "Total Duty & Tax",
        },
        "rows": rows,
        "totals": {"boe": "Total", "sd": sd_total, "at": at_total},
        "notes": [
            "Scope note: SD and AT are recorded on the import duty cascade (M44 Bill of Entry). "
            "Domestic SD/AT lines are not captured in this build, so none are estimated here."
        ],
        "empty": "No assessed Bill of Entry records.",
    }


REPORTS = {
    "sd_at_liability": sd_at_liability,
    "statutory_calendar": statutory_calendar,
    "signoff_queue": signoff_queue,
    "mushak_610": mushak_610,
    "note_register": note_register,
    "vat_return_draft": vat_return_draft,
    "vat_reconciliation": vat_reconciliation,
    "tds_annual_summary": tds_annual_summary,
    "vds_deduction_register": vds_deduction_register,
}
