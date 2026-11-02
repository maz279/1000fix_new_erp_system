# A08 · M19 Financial Accounting & GL — models the generic workspace screens may read,
# and the workflow methods they may call (/p03/model/records, /p03/model/action).
# Each entry: model -> {"order", "limit", "actions"}. Reads also need the
# user's own read access on the model (accounting/payroll groups apply).
#
# M19's original 14 screens keep their bespoke kinds served by
# controllers/p03_gl_api.py; the surfaces below back the additions (CoA
# loader, recurring journals, statutory report bridge, nil-return packs and
# the "Group & Inter-Branch" group). Every figure is read from posted ledger
# lines or the models' own records — nothing is invented.
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
    "fix.fx.revaluation": {
        "order": "rate_date desc, id desc",
        "limit": 200,
        "actions": {"action_compute", "action_post"},
    },
    "fix.chart.loader": {
        "order": "id desc",
        "limit": 50,
        "actions": {"action_load_from_csv", "action_link_odoo_accounts", "action_reconcile_chart"},
    },
    "fix.journal.template": {
        "order": "next_run_date, name",
        "limit": 200,
        "actions": {"action_activate", "action_generate_entry", "action_pause"},
    },
    "fix.financial.report.bridge": {
        "order": "generated_at desc, id desc",
        "limit": 200,
        "actions": {"action_generate_report"},
    },
    "fix.nil.return.generator": {
        "order": "period_year desc, period_month desc, id desc",
        "limit": 200,
        "actions": {
            "action_verify_eligibility",
            "action_generate_nil_packs",
            "action_submit_to_nbr",
        },
    },
    "fix.consolidation.book": {
        "order": "consolidation_date desc, id desc",
        "limit": 100,
        "actions": {"action_run_consolidation", "action_generate_eliminations", "action_close"},
    },
    "fix.elimination.entry": {
        "order": "book_id desc, id",
        "limit": 500,
        "actions": set(),
    },
    "fix.intercompany.transaction": {
        "order": "transaction_date desc, id desc",
        "limit": 300,
        "actions": {"action_generate_mirror", "action_match", "action_mark_settled"},
    },
    "fix.intercompany.rule": {
        "order": "code",
        "limit": 200,
        "actions": set(),
    },
    # Allocation rules: the D365 form edits header + targets in one save (the
    # model refuses a rule with no targets, and targets must total 100%).
    "fix.allocation.rule": {
        "order": "name",
        "limit": 200,
        "actions": {"action_run"},
    },
    "fix.chart.account": {"order": "id desc", "limit": 400, "actions": set()},
    "fix.fiscal.period.bridge": {"order": "id desc", "limit": 400, "actions": set()},
    "fix.journal.dimension": {"order": "id desc", "limit": 400, "actions": set()},
    "fix.period.close": {"order": "id desc", "limit": 400, "actions": set()},
}


def _month_start(today=None):
    today = today or datetime.date.today()
    return datetime.date(today.year, today.month, 1)


def _as_date(value, fallback):
    if not value:
        return fallback
    return datetime.date.fromisoformat(str(value)[:10])


def kpis(env):
    """Gross margin MTD from posted income vs cost-of-revenue lines, and the
    inter-company / inter-branch transactions still awaiting a clean match."""
    out = {"gross_margin_mtd": None, "ic_unmatched": None}
    ms = _month_start()
    try:
        groups = env["account.move.line"]._read_group(
            [
                ("parent_state", "=", "posted"),
                ("date", ">=", ms),
                ("company_id", "=", env.company.id),
                ("account_id.account_type", "in", ("income", "expense_direct_cost")),
            ],
            ["account_id"],
            ["balance:sum"],
        )
        revenue = -sum(b or 0.0 for a, b in groups if a.account_type == "income")
        cost = sum(b or 0.0 for a, b in groups if a.account_type == "expense_direct_cost")
        if revenue > 0.005:
            out["gross_margin_mtd"] = "%.1f%%" % ((revenue - cost) / revenue * 100.0)
    except Exception:
        out["gross_margin_mtd"] = None
    try:
        out["ic_unmatched"] = env["fix.intercompany.transaction"].search_count(
            [("state", "in", ("pending_matching", "disputed"))]
        )
    except Exception:
        out["ic_unmatched"] = None
    return out


# --------------------------------------------------------------------------- reports


def ic_balances(env, date_from=None, date_to=None, **_params):
    """Due-to / due-from balances per counterparty pair, from the POSTED due
    lines of every mirrored, not-yet-settled inter-company / inter-branch
    transaction dated up to the as-of date. The due-from is what the
    originating side carries in its books, the due-to what the counterparty
    carries; a non-zero difference is an out-of-balance pair to resolve."""
    as_of = _as_date(date_to, datetime.date.today())
    txns = env["fix.intercompany.transaction"].search(
        [
            ("state", "in", ("pending_matching", "matched", "disputed")),
            ("transaction_date", "<=", as_of),
        ]
    )
    pairs = {}
    for txn in txns:
        src_line, tgt_line = txn.source_due_line_id.sudo(), txn.target_due_line_id.sudo()
        if not (src_line and tgt_line):
            continue
        if txn.scope == "interbranch":
            origin = txn.source_branch_id.name or txn.source_entity_id.code
            counter = txn.target_branch_id.name or txn.target_entity_id.code
        else:
            origin, counter = txn.source_entity_id.code, txn.target_entity_id.code
        key = (txn.scope, origin, counter)
        row = pairs.setdefault(
            key,
            {
                "scope": dict(txn._fields["scope"].selection).get(txn.scope, txn.scope),
                "origin": origin,
                "counterparty": counter,
                "open_count": 0,
                "disputed": 0,
                "due_from": 0.0,
                "due_to": 0.0,
            },
        )
        row["open_count"] += 1
        row["disputed"] += 1 if txn.state == "disputed" else 0
        if src_line.move_id.state == "posted":
            row["due_from"] += src_line.balance
        if tgt_line.move_id.state == "posted":
            row["due_to"] += -tgt_line.balance
    rows = []
    for key in sorted(pairs):
        row = pairs[key]
        row["due_from"] = round(row["due_from"], 2)
        row["due_to"] = round(row["due_to"], 2)
        row["difference"] = round(row["due_from"] - row["due_to"], 2)
        rows.append(row)
    totals = {
        "due_from": round(sum(r["due_from"] for r in rows), 2),
        "due_to": round(sum(r["due_to"] for r in rows), 2),
        "difference": round(sum(r["difference"] for r in rows), 2),
        "open_count": sum(r["open_count"] for r in rows),
    }
    return {
        "title": "Due-To / Due-From Balances as of %s" % as_of,
        "cols": [
            "scope",
            "origin",
            "counterparty",
            "open_count",
            "disputed",
            "due_from",
            "due_to",
            "difference",
        ],
        "labels": {
            "scope": "Scope",
            "origin": "Originating Entity / Branch",
            "counterparty": "Counterparty",
            "open_count": "Open Transactions",
            "disputed": "Disputed",
            "due_from": "Due-From (originating books)",
            "due_to": "Due-To (counterparty books)",
            "difference": "Difference",
        },
        "rows": rows,
        "totals": totals,
        "notes": [
            "Posted due lines of mirrored inter-company / inter-branch transactions not yet "
            "settled, in each company's own currency.",
            "Settled transactions drop out once both due lines are reconciled in the ledger.",
        ],
        "empty": "No open inter-company or inter-branch balances up to %s." % as_of,
    }


def close_sla(env, date_from=None, date_to=None, **_params):
    """Month-end closes that missed the 5-day target: closed late
    (fix.period.close.action_fail_close_target) and still open past target."""
    Close = env["fix.period.close"]
    today = datetime.date.today()
    rows = []
    for rec in Close.action_fail_close_target():
        period_end = rec["period_end"]
        rows.append(
            {
                "period_end": str(period_end),
                "status": "Closed late",
                "days": round(rec["close_duration_days"] or 0.0, 1),
                "over_target": round(
                    (rec["close_duration_days"] or 0.0) - Close.CLOSE_TARGET_DAYS, 1
                ),
            }
        )
    overdue = Close.search(
        [("state", "!=", "closed"), ("target_completion_date", "<", today)],
        order="period_end desc",
    )
    for close in overdue:
        days_open = (today - close.period_end).days
        rows.append(
            {
                "period_end": str(close.period_end),
                "status": "Open past target",
                "days": float(days_open),
                "over_target": float(days_open - Close.CLOSE_TARGET_DAYS),
            }
        )
    rows.sort(key=lambda r: r["period_end"], reverse=True)
    return {
        "title": "Close SLA Breaches (target %d days)" % Close.CLOSE_TARGET_DAYS,
        "cols": ["period_end", "status", "days", "over_target"],
        "labels": {
            "period_end": "Period End",
            "status": "Status",
            "days": "Days Since Period End",
            "over_target": "Days Over Target",
        },
        "rows": rows,
        "notes": ["Target: every month-end close completes within 5 days of period end (G3-04)."],
        "empty": "No close has missed the 5-day target.",
    }


def fx_revaluation(env, date_from=None, date_to=None, **params):
    """Open foreign-currency balances at their closing rate (IAS 21). The gain or
    loss is measured per journal item: booked base vs the same foreign balance at
    the closing rate. Zero when the company holds no open FX balance."""
    runs = env["fix.fx.revaluation"].sudo().search([], order="rate_date desc, id desc", limit=1)
    rows = []
    if not runs:
        return _pack(
            "FX Revaluation - no run recorded",
            ["deal", "partner", "currency", "foreign", "booked", "restated", "gain_loss"],
            {
                "deal": "Document",
                "partner": "Partner",
                "currency": "Currency",
                "foreign": "Foreign balance",
                "booked": "Booked (BDT)",
                "restated": "Restated (BDT)",
                "gain_loss": "Gain / (loss)",
            },
            rows,
            [
                "No revaluation run exists yet. Open a run, compute it at the closing rate "
                "and post the unrealized difference."
            ],
            empty="No FX revaluation run.",
        )
    run = runs[0]
    for line in run.line_ids:
        rows.append(
            {
                "deal": line.move_line_id.move_id.name if line.move_line_id else "-",
                "partner": line.partner_id.name or "-",
                "currency": line.foreign_currency_id.name or "-",
                "foreign": round(line.foreign_balance, 2),
                "booked": round(line.old_base, 2),
                "restated": round(line.new_base, 2),
                "gain_loss": round(line.gain_loss, 2),
            }
        )
    return _pack(
        "FX Revaluation %s - %s (%s)" % (run.name, run.state, run.rate_date),
        ["deal", "partner", "currency", "foreign", "booked", "restated", "gain_loss"],
        {
            "deal": "Document",
            "partner": "Partner",
            "currency": "Currency",
            "foreign": "Foreign balance",
            "booked": "Booked (BDT)",
            "restated": "Restated (BDT)",
            "gain_loss": "Gain / (loss)",
        },
        rows,
        [
            "Restated at the closing rate effective on the run date; the gain or loss is "
            "unrealized until the balance settles (IAS 21.23)."
        ],
        totals={"deal": "Net", "gain_loss": round(sum(r["gain_loss"] for r in rows), 2)},
        empty="No open foreign-currency balance.",
    )


REPORTS = {
    "fx_revaluation": fx_revaluation,
    "ic_balances": ic_balances,
    "close_sla": close_sla,
}
