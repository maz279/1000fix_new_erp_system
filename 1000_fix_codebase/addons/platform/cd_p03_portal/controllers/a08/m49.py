# A08 · M49 Fixed Assets & Capex — models the generic workspace screens may read,
# the workflow methods they may call (/p03/model/records, /p03/model/action),
# the computed reports (/p03/model/report) and the module KPI tiles.
#
# Every report reads with the CALLER's environment (the models' ACL and
# record rules apply) and is computed from posted documents only: posted
# depreciation lines, posted revaluations/impairments and posted disposals.
import datetime
import logging

from odoo import fields

_logger = logging.getLogger(__name__)

# A08 workflow audit (2026-11-04) M49-1/M49-6: capex requests, revaluations
# and disposals are approved from the approver's M63 inbox (routed by amount),
# never by an Approve button on the record; approve and post are separate.
SURFACES = {
    "fix.capex.request": {
        "order": "request_date desc, id desc",
        "limit": 200,
        "actions": {
            "action_submit",
            "action_recall_approval",
            "action_reject",
            "action_create_cwip",
            "action_link_purchase_order",
        },
    },
    "fix.capex.budget": {
        "order": "date_from desc, id desc",
        "limit": 100,
        "actions": {"action_approve", "action_close"},
    },
    "fix.fixed.asset": {
        "order": "purchase_date desc, id desc",
        "limit": 200,
        "actions": {"action_activate", "action_accrue_month", "action_dispose"},
    },
    "fix.cwip.entry": {
        "order": "id desc",
        "limit": 200,
        "actions": {"action_capitalise", "action_book_posted_cost"},
    },
    "fix.asset.category": {"order": "code", "limit": 200, "actions": set()},
    "fix.asset.transfer": {
        "order": "date desc, id desc",
        "limit": 200,
        "actions": {"action_confirm", "action_acknowledge", "action_cancel"},
    },
    "fix.asset.depreciation.run": {
        "order": "period_start desc, id desc",
        "limit": 100,
        "actions": {"action_compute", "action_post"},
    },
    # A08 M49-8: the legacy rate table is read-only and has no form; the rates
    # in force are the M51 master's (the M49-taxrates report).
    "fix.asset.tax.rate": {"order": "code, date_from desc", "limit": 200, "actions": set()},
    "fix.asset.revaluation": {
        "order": "date desc, id desc",
        "limit": 200,
        "actions": {"action_submit", "action_recall_approval", "action_post", "action_cancel"},
    },
    "fix.asset.disposal": {
        "order": "date desc, id desc",
        "limit": 200,
        "actions": {"action_submit", "action_recall_approval", "action_post", "action_cancel"},
        "pickers": {"insurance_id": [("state", "in", ["active", "expired", "replaced"])]},
    },
    "fix.asset.verification.campaign": {
        "order": "date desc, id desc",
        "limit": 100,
        "actions": {"action_start", "action_record_scan", "action_close"},
    },
    "fix.asset.verification.line": {
        "order": "campaign_id desc, id",
        "limit": 500,
        "actions": {"action_mark_found", "action_mark_missing"},
    },
    "fix.lease": {
        "order": "commencement_date desc, id desc",
        "limit": 200,
        "actions": {"action_activate", "action_post_due"},
    },
    "fix.lease.schedule.line": {
        "order": "lease_id, sequence",
        "limit": 500,
        "actions": {"action_post"},
    },
    # Capture audit 2026-11-17: the records the sub-module pages had no
    # capture for (cd_fixed_asset_ext models/fix_asset_capture.py). Every
    # decision is a manager's who did not raise the document.
    "fix.capital.project": {
        "order": "start_date desc, id desc",
        "limit": 200,
        "actions": {
            "action_approve",
            "action_complete",
            "action_record_review",
            "action_cancel",
        },
    },
    "fix.cwip.component": {
        "order": "cwip_id desc, sequence, id",
        "limit": 300,
        "actions": set(),
        "pickers": {"cwip_id": [("state", "=", "open")]},
    },
    "fix.asset.depreciation.change": {
        "order": "id desc",
        "limit": 200,
        "actions": {"action_submit", "action_approve", "action_reject", "action_cancel"},
        "pickers": {"asset_id": [("state", "=", "active")]},
    },
    "fix.asset.impairment.assessment": {
        "order": "assessment_date desc, id desc",
        "limit": 200,
        "actions": {"action_confirm", "action_cancel"},
        "pickers": {"asset_id": [("state", "=", "active")]},
    },
    "fix.asset.verification.variance": {
        "order": "id desc",
        "limit": 300,
        "actions": {"action_propose", "action_approve", "action_reject"},
        "pickers": {"line_id": [("result", "in", ["missing", "misplaced", "unregistered"])]},
    },
    # the two gaps left by the capture audit (models/fix_asset_gaps.py)
    "fix.asset.component": {
        "order": "parent_asset_id desc, sequence, id",
        "limit": 300,
        "actions": set(),
        "pickers": {"parent_asset_id": [("state", "=", "draft"), ("cwip_id", "=", False)]},
    },
    "fix.asset.insurance": {
        "order": "period_to desc, id desc",
        "limit": 200,
        "actions": {"action_activate", "action_record_review", "action_expire", "action_cancel"},
        "pickers": {"asset_ids": [("state", "in", ["draft", "active"])]},
    },
}


# ---------------------------------------------------------------- helpers
def _window(date_from=None, date_to=None):
    """The report window; defaults to the Bangladesh fiscal year (July-June)
    to date."""
    today = datetime.date.today()
    dt = fields.Date.to_date(date_to) or today
    if date_from:
        df = fields.Date.to_date(date_from)
    else:
        df = datetime.date(dt.year if dt.month >= 7 else dt.year - 1, 7, 1)
    if df > dt:
        df, dt = dt, df
    return df, dt


def _month_end(day):
    nxt = (day.replace(day=28) + datetime.timedelta(days=4)).replace(day=1)
    return nxt - datetime.timedelta(days=1)


def _r(value):
    return round(value or 0.0, 2)


def _assets(env):
    return env["fix.fixed.asset"].search(
        [("state", "in", ("active", "disposed")), ("company_id", "in", env.companies.ids)]
    )


def _cat_label(asset):
    return asset.category_id.name or asset.category or "—"


def _in(day, df, dt):
    return bool(day) and df <= day <= dt


def _totals(rows, cols, label_col):
    tot = {label_col: "Total"}
    for c in cols:
        if c != label_col and any(isinstance(r.get(c), int | float) for r in rows):
            tot[c] = _r(sum(r.get(c) or 0.0 for r in rows))
    return tot


# ---------------------------------------------------------------- reports
def movement_schedule(env, date_from=None, date_to=None, **_kw):
    """IAS 16.73(e) reconciliation per category: opening, additions,
    revaluation, disposals and closing cost; opening, charge, impairment,
    disposals and closing accumulated depreciation; closing NBV."""
    df, dt = _window(date_from, date_to)
    after = dt + datetime.timedelta(days=1)
    by_cat = {}
    for asset in _assets(env):
        op, cl = asset._position(df), asset._position(after)
        revals = asset.revaluation_ids.filtered(
            lambda r: r.state == "posted" and _in(r.date, df, dt)
        )
        lines = asset.depreciation_line_ids.filtered(
            lambda ln: (
                ln.state == "posted"
                and ln.book == "book"
                and _in(_month_end(ln.period_start), df, dt)
            )
        )
        additions = asset.gross if _in(asset.purchase_date, df, dt) else 0.0
        reval = sum(revals.mapped("cost_delta"))
        dep = sum(lines.mapped("amount"))
        imp = sum(revals.mapped("accum_delta"))
        op_acc, cl_acc = op["dep"] + op["imp"], cl["dep"] + cl["imp"]
        if not any((op["cost"], cl["cost"], additions, reval, dep, imp)):
            continue
        row = by_cat.setdefault(
            _cat_label(asset),
            dict.fromkeys(
                (
                    "opening_cost",
                    "additions",
                    "revaluation",
                    "disposals_cost",
                    "closing_cost",
                    "opening_accum",
                    "depreciation",
                    "impairment",
                    "disposals_accum",
                    "closing_accum",
                    "closing_nbv",
                ),
                0.0,
            ),
        )
        row["opening_cost"] += op["cost"]
        row["additions"] += additions
        row["revaluation"] += reval
        row["disposals_cost"] += op["cost"] + additions + reval - cl["cost"]
        row["closing_cost"] += cl["cost"]
        row["opening_accum"] += op_acc
        row["depreciation"] += dep
        row["impairment"] += imp
        row["disposals_accum"] += op_acc + dep + imp - cl_acc
        row["closing_accum"] += cl_acc
        row["closing_nbv"] += cl["cost"] - cl_acc
    cols = [
        "category",
        "opening_cost",
        "additions",
        "revaluation",
        "disposals_cost",
        "closing_cost",
        "opening_accum",
        "depreciation",
        "impairment",
        "disposals_accum",
        "closing_accum",
        "closing_nbv",
    ]
    rows = [
        {"category": cat, **{k: _r(v) for k, v in vals.items()}}
        for cat, vals in sorted(by_cat.items())
    ]
    return {
        "title": "Fixed Asset Movement Schedule %s to %s" % (df, dt),
        "cols": cols,
        "labels": {
            "category": "Category",
            "opening_cost": "Opening Cost",
            "additions": "Additions",
            "revaluation": "Revaluation",
            "disposals_cost": "Disposals (Cost)",
            "closing_cost": "Closing Cost",
            "opening_accum": "Opening Acc. Dep. & Impairment",
            "depreciation": "Depreciation",
            "impairment": "Impairment (Net)",
            "disposals_accum": "Disposals (Acc. Dep.)",
            "closing_accum": "Closing Acc. Dep. & Impairment",
            "closing_nbv": "Closing NBV",
        },
        "rows": rows,
        "totals": _totals(rows, cols, "category") if rows else None,
        "notes": [
            "Accounting book (IAS 16) from posted depreciation runs, revaluations, "
            "impairments and disposals; draft documents are excluded.",
            "Depreciation counts in the month it is charged for (dated the month end).",
        ],
        "empty": "No asset movement in this period.",
    }


def dual_book(env, date_from=None, date_to=None, **_kw):
    """Book vs tax depreciation per asset, and the closing temporary
    difference (carrying amount minus tax written-down value)."""
    df, dt = _window(date_from, date_to)
    after = dt + datetime.timedelta(days=1)
    rows = []
    for asset in _assets(env):
        lines = asset.depreciation_line_ids.filtered(
            lambda ln: ln.state == "posted" and _in(_month_end(ln.period_start), df, dt)
        )
        cl = asset._position(after)
        if not lines and not cl["cost"]:
            continue
        has_tax = bool(asset.category_id.tax_rate_code)
        book_nbv = cl["cost"] - cl["dep"] - cl["imp"]
        tax_wdv = (asset.gross - cl["tax"]) if (has_tax and cl["cost"]) else 0.0
        rows.append(
            {
                "asset": "%s %s" % (asset.code or "", asset.name),
                "category": _cat_label(asset),
                "book_dep": _r(sum(lines.filtered(lambda ln: ln.book == "book").mapped("amount"))),
                "tax_dep": _r(sum(lines.filtered(lambda ln: ln.book == "tax").mapped("amount"))),
                "book_nbv": _r(book_nbv),
                "tax_wdv": _r(tax_wdv),
                "difference": _r(book_nbv - tax_wdv) if has_tax else None,
            }
        )
    cols = ["asset", "category", "book_dep", "tax_dep", "book_nbv", "tax_wdv", "difference"]
    unverified = env["fix.tax.rate"].search_count(
        [("tax_kind", "=", "depreciation"), ("verify_with_adviser", "=", True)]
    )
    notes = [
        "Tax book: ITA 2023 Third Schedule reducing balance on the annual written-down value "
        "(the year's allowance spread over its months), rates from the M51 Tax Rate Master; "
        "the return computation follows the Act's own rules.",
        "Difference = carrying amount minus tax WDV (taxable temporary difference when positive). "
        "Deferred tax = difference x the applicable corporate rate, to be confirmed by the tax adviser.",
    ]
    if unverified:
        notes.append(
            "%s tax depreciation rate(s) are not yet verified by the tax adviser." % unverified
        )
    return {
        "title": "Depreciation (Dual Book) %s to %s" % (df, dt),
        "cols": cols,
        "labels": {
            "asset": "Asset",
            "category": "Category",
            "book_dep": "Book Depreciation",
            "tax_dep": "Tax Depreciation",
            "book_nbv": "Book NBV",
            "tax_wdv": "Tax WDV",
            "difference": "Temporary Difference",
        },
        "rows": rows,
        "totals": _totals(rows, cols, "asset") if rows else None,
        "notes": notes,
        "empty": "No depreciation posted in this period.",
    }


def nbv_by_category(env, date_from=None, date_to=None, **_kw):
    """Cost, accumulated depreciation & impairment, NBV and tax WDV per
    category as at the end of the window."""
    _df, dt = _window(date_from, date_to)
    after = dt + datetime.timedelta(days=1)
    by_cat = {}
    for asset in _assets(env):
        cl = asset._position(after)
        if not cl["cost"]:
            continue
        row = by_cat.setdefault(
            _cat_label(asset), {"count": 0, "cost": 0.0, "accum": 0.0, "nbv": 0.0, "tax_wdv": 0.0}
        )
        row["count"] += 1
        row["cost"] += cl["cost"]
        row["accum"] += cl["dep"] + cl["imp"]
        row["nbv"] += cl["cost"] - cl["dep"] - cl["imp"]
        if asset.category_id.tax_rate_code:
            row["tax_wdv"] += asset.gross - cl["tax"]
    rows = [
        {
            "category": cat,
            "count": v["count"],
            "cost": _r(v["cost"]),
            "accum": _r(v["accum"]),
            "nbv": _r(v["nbv"]),
            "tax_wdv": _r(v["tax_wdv"]),
        }
        for cat, v in sorted(by_cat.items())
    ]
    cols = ["category", "count", "cost", "accum", "nbv", "tax_wdv"]
    return {
        "title": "NBV by Category as at %s" % dt,
        "cols": cols,
        "labels": {
            "category": "Category",
            "count": "Assets",
            "cost": "Cost / Revalued",
            "accum": "Acc. Dep. & Impairment",
            "nbv": "Net Book Value",
            "tax_wdv": "Tax WDV",
        },
        "rows": rows,
        "totals": _totals(rows, cols, "category") if rows else None,
        "notes": ["Right-of-use assets carry no tax WDV (rent is deducted as paid)."],
        "empty": "No assets in service at this date.",
    }


def capex_vs_budget(env, date_from=None, date_to=None, **_kw):
    """Capital budgets overlapping the window: committed (approved
    requests), actual (CWIP / capitalised cost) and what is left."""
    df, dt = _window(date_from, date_to)
    budgets = env["fix.capex.budget"].search(
        [
            ("company_id", "in", env.companies.ids),
            ("date_from", "<=", dt),
            ("date_to", ">=", df),
        ],
        order="date_from, name",
    )
    states = dict(env["fix.capex.budget"]._fields["state"]._description_selection(env))
    rows = [
        {
            "budget": b.name,
            "fiscal_year": b.fiscal_year or "",
            "branch": b.operating_unit_id.name or "Company-wide",
            "state": states.get(b.state, b.state),
            "amount": _r(b.amount),
            "committed": _r(b.committed_amount),
            "actual": _r(b.actual_amount),
            "available": _r(b.available_amount),
            "utilisation_pct": b.utilisation_pct,
        }
        for b in budgets
    ]
    cols = [
        "budget",
        "fiscal_year",
        "branch",
        "state",
        "amount",
        "committed",
        "actual",
        "available",
        "utilisation_pct",
    ]
    totals = None
    if rows:
        totals = _totals(rows, cols, "budget")
        totals["utilisation_pct"] = (
            round(totals["committed"] / totals["amount"] * 100.0, 1) if totals["amount"] else None
        )
    return {
        "title": "Capex vs Budget %s to %s" % (df, dt),
        "cols": cols,
        "labels": {
            "budget": "Budget",
            "fiscal_year": "Fiscal Year",
            "branch": "Branch",
            "state": "Status",
            "amount": "Budget",
            "committed": "Committed",
            "actual": "Actual",
            "available": "Available",
            "utilisation_pct": "Utilisation %",
        },
        "rows": rows,
        "totals": totals,
        "notes": [
            "Committed = approved capex requests (approved, in CWIP or capitalised); "
            "actual = cost accumulated on their CWIP projects."
        ],
        "empty": "No capital budget covers this period.",
    }


def disposal_gains(env, date_from=None, date_to=None, **_kw):
    """Posted disposals with proceeds, NBV derecognised and gain/loss."""
    df, dt = _window(date_from, date_to)
    disposals = env["fix.asset.disposal"].search(
        [
            ("state", "=", "posted"),
            ("company_id", "in", env.companies.ids),
            ("date", ">=", df),
            ("date", "<=", dt),
        ],
        order="date, id",
    )
    kinds = dict(env["fix.asset.disposal"]._fields["kind"]._description_selection(env))
    rows = [
        {
            "reference": d.name,
            "asset": d.asset_id.display_name,
            "kind": kinds.get(d.kind, d.kind),
            "date": str(d.date),
            "proceeds": _r(d.proceeds),
            "nbv": _r(d.nbv),
            "gain_loss": _r(d.gain_loss),
            "tax_wdv": _r(d.tax_wdv),
            "tax_balancing": _r(d.tax_balancing),
            "entry": d.move_id.name or "",
        }
        for d in disposals
    ]
    cols = [
        "reference",
        "asset",
        "kind",
        "date",
        "proceeds",
        "nbv",
        "gain_loss",
        "tax_wdv",
        "tax_balancing",
        "entry",
    ]
    return {
        "title": "Disposal Gains/Losses %s to %s" % (df, dt),
        "cols": cols,
        "labels": {
            "reference": "Reference",
            "asset": "Asset",
            "kind": "Type",
            "date": "Date",
            "proceeds": "Proceeds",
            "nbv": "NBV Derecognised",
            "gain_loss": "Gain (+) / Loss (-)",
            "tax_wdv": "Tax WDV",
            "tax_balancing": "Balancing Charge (+) / Allowance (-)",
            "entry": "Journal Entry",
        },
        "notes": [
            "The tax columns are a memo for the tax computation: proceeds less the tax "
            "written-down value. They post nothing; the tax adviser confirms the treatment."
        ],
        "rows": rows,
        "totals": _totals(rows, cols, "reference") if rows else None,
        "empty": "No disposals posted in this period.",
    }


def lease_summary(env, date_from=None, date_to=None, **_kw):
    """IFRS 16 per lease: liability at the window end (per schedule), its
    current / non-current split, interest and ROU depreciation of the
    window, and months due but not yet posted."""
    df, dt = _window(date_from, date_to)
    leases = env["fix.lease"].search(
        [("company_id", "in", env.companies.ids), ("state", "in", ("active", "ended"))],
        order="name",
    )
    rows = []
    for lease in leases:
        lines = lease.schedule_line_ids.sorted("sequence")
        upto = lines.filtered(lambda ln: _month_end(ln.period_start) <= dt)
        liability = upto[-1].closing if upto else lease.initial_liability
        later = lines.filtered(lambda ln: _month_end(ln.period_start) > dt)[:12]
        current = min(sum(later.mapped("principal")), liability)
        window = lines.filtered(lambda ln: _in(_month_end(ln.period_start), df, dt))
        due_unposted = lines.filtered(
            lambda ln: ln.state == "draft" and ln.period_start <= dt.replace(day=1)
        )
        rou = (
            lease.asset_id._position(dt + datetime.timedelta(days=1))
            if lease.asset_id
            else {"cost": 0.0, "dep": 0.0, "imp": 0.0}
        )
        rows.append(
            {
                "lease": "%s %s" % (lease.reference or "", lease.name),
                "branch": lease.operating_unit_id.name or "",
                "rou_nbv": _r(rou["cost"] - rou["dep"] - rou["imp"]),
                "liability": _r(liability),
                "current": _r(current),
                "non_current": _r(liability - current),
                "interest": _r(sum(window.mapped("interest"))),
                "depreciation": _r(sum(window.mapped("depreciation"))),
                "payments": _r(sum(window.mapped("payment"))),
                "unposted_due": len(due_unposted),
            }
        )
    cols = [
        "lease",
        "branch",
        "rou_nbv",
        "liability",
        "current",
        "non_current",
        "interest",
        "depreciation",
        "payments",
        "unposted_due",
    ]
    return {
        "title": "IFRS 16 Lease Summary %s to %s" % (df, dt),
        "cols": cols,
        "labels": {
            "lease": "Lease",
            "branch": "Branch",
            "rou_nbv": "ROU Asset NBV (Posted)",
            "liability": "Lease Liability",
            "current": "Current (12 Months)",
            "non_current": "Non-Current",
            "interest": "Interest",
            "depreciation": "ROU Depreciation",
            "payments": "Payments",
            "unposted_due": "Months Due, Not Posted",
        },
        "rows": rows,
        "totals": _totals(rows, cols, "lease") if rows else None,
        "notes": [
            "Liability, interest, depreciation and payments follow the contractual schedule; "
            "months due but not posted are counted so the GL lag is visible.",
            "Short-term and low-value leases (IFRS 16.5) are expensed through AP and are not listed.",
        ],
        "empty": "No active leases.",
    }


def register_gl_reconciliation(env, date_from=None, date_to=None, **_kw):
    """BRU-FXA-03 (A08 M49-10): the register against its GL control accounts
    per category, for the caller's companies, read as the caller."""
    rows = []
    for company in env.companies:
        for row in env["fix.fixed.asset"]._fix_register_gl_reconciliation(company):
            rows.append(dict(row, company=company.name))
    cols = ["company", "category", "line", "account", "register", "gl", "variance"]
    out_of_balance = len([r for r in rows if abs(r["variance"]) > 0.005])
    return {
        "title": "Register to GL Reconciliation",
        "cols": cols,
        "labels": {
            "company": "Company",
            "category": "Category",
            "line": "Line",
            "account": "Control Account",
            "register": "Register",
            "gl": "GL (posted)",
            "variance": "Variance",
        },
        "rows": rows,
        "notes": [
            "Cost and accumulated depreciation/impairment of assets in service, and open CWIP, "
            "against the posted balance of each category's control account. %d line(s) out of "
            "balance." % out_of_balance
        ],
        "empty": "No asset categories with control accounts.",
    }


def tax_depreciation_rates(env, date_from=None, date_to=None, **_kw):
    """The ITA 2023 Third Schedule rates the tax book uses: M51 master rows of
    kind 'depreciation' (BRU-FXA-13), with their adviser status. Maintained on
    the M51 Tax Rate Master screen (proposal + second-manager activation)."""
    rates = env["fix.tax.rate"].search(
        [("tax_kind", "=", "depreciation"), ("state", "!=", "retired")],
        order="code, date_from desc",
    )
    states = dict(env["fix.tax.rate"]._fields["state"]._description_selection(env))
    rows = [
        {
            "code": r.code,
            "name": r.name,
            "rate": r.rate,
            "date_from": str(r.date_from),
            "date_to": str(r.date_to or ""),
            "adviser": "verify with adviser" if r.verify_with_adviser else "confirmed",
            "state": states.get(r.state, r.state),
        }
        for r in rates
    ]
    return {
        "title": "Tax Depreciation Rates (ITA 2023 Third Schedule, M51 master)",
        "cols": ["code", "name", "rate", "date_from", "date_to", "adviser", "state"],
        "labels": {
            "code": "Class",
            "name": "Asset Class",
            "rate": "Rate % a Year",
            "date_from": "From",
            "date_to": "To",
            "adviser": "Adviser",
            "state": "Status",
        },
        "rows": rows,
        "notes": [
            "The tax book refuses a rate flagged verify-with-adviser; record the adviser's "
            "confirmation on the M51 Tax Rate Master."
        ],
        "empty": "No tax depreciation rates in the M51 master.",
    }


REPORTS = {
    "tax_depreciation_rates": tax_depreciation_rates,
    "register_gl_reconciliation": register_gl_reconciliation,
    "movement_schedule": movement_schedule,
    "dual_book": dual_book,
    "nbv_by_category": nbv_by_category,
    "capex_vs_budget": capex_vs_budget,
    "disposal_gains": disposal_gains,
    "lease_summary": lease_summary,
}


# ---------------------------------------------------------------- KPIs
def kpis(env):
    """Module tiles: gross block and NBV of assets in service, open CWIP
    cost, book depreciation posted for the current month, lease liability."""
    out = {}
    companies = [("company_id", "in", env.companies.ids)]

    def safe(key, fn):
        try:
            out[key] = fn()
        except Exception:  # unreadable for this user -> honest placeholder
            _logger.debug("M49 KPI %s unavailable", key, exc_info=True)
            out[key] = None

    def _active():
        return env["fix.fixed.asset"].search([("state", "=", "active"), *companies])

    safe("m49_gross_block", lambda: _r(sum(_active().mapped("cost"))))
    safe("m49_nbv", lambda: _r(sum(_active().mapped("book_nbv"))))
    safe(
        "m49_cwip_open",
        lambda: _r(
            sum(env["fix.cwip.entry"].search([("state", "=", "open"), *companies]).mapped("amount"))
        ),
    )
    month = datetime.date.today().replace(day=1)
    safe(
        "m49_dep_mtd",
        lambda: _r(
            sum(
                env["fix.asset.depreciation.line"]
                .search(
                    [
                        ("book", "=", "book"),
                        ("state", "=", "posted"),
                        ("period_start", "=", month),
                        *companies,
                    ]
                )
                .mapped("amount")
            )
        ),
    )
    safe(
        "m49_lease_liability",
        lambda: _r(
            sum(
                env["fix.lease"]
                .search([("state", "=", "active"), *companies])
                .mapped("liability_balance")
            )
        ),
    )
    return out
