# A08 · M53 Revenue Recognition & Settlement — models the generic workspace screens may read,
# and the workflow methods they may call (/p03/model/records, /p03/model/action).
# Each entry: model -> {"order", "limit", "actions"}. Reads also need the
# user's own read access on the model (accounting/payroll groups apply).
import datetime

SURFACES = {
    # --- revenue (IFRS 15) ---
    "fix.performance.obligation": {
        "order": "subscription_id, id",
        "limit": 200,
        "actions": {"action_create_schedule", "action_recognize"},
    },
    "fix.revenue.schedule": {
        "order": "start_date desc, id desc",
        "limit": 200,
        "actions": {"action_recognize_period"},
    },
    "fix.subscription": {
        "order": "next_invoice_date, id desc",
        "limit": 200,
        "actions": {
            "action_generate_charge",
            "action_trigger_dunning",
            "action_reinstate",
            "action_request_refund",
            "action_allocate_price",
        },
    },
    "fix.warranty.provision": {
        "order": "period desc, id desc",
        "limit": 60,
        "actions": {"action_compute", "action_post"},
    },
    "fix.warranty.provision.policy": {"order": "date_from desc", "limit": 50, "actions": set()},
    # --- commission ---
    "fix.commission.ledger": {"order": "id desc", "limit": 200, "actions": {"action_post_to_gl"}},
    "fix.commission.scheme": {
        "order": "scheme_type, date_from desc",
        "limit": 100,
        "actions": set(),
    },
    # --- settlements ---
    "fix.payout.run": {
        "order": "id desc",
        "limit": 100,
        "actions": {
            "action_collect_accrued",
            "action_approve",
            "action_submit_payout",
            "action_generate_beftn",
            "action_query_status",
            "action_confirm_bank_settlement",
            "action_post_payout_to_gl",
        },
    },
    "fix.seller.statement": {
        "order": "period desc, id desc",
        "limit": 100,
        "actions": {"action_issue_statement", "action_settle_statement"},
    },
    "fix.referral": {"order": "id desc", "limit": 200, "actions": {"action_accrue_commission"}},
    "fix.settlement.adjustment": {
        "order": "id desc",
        "limit": 200,
        "actions": {"action_activate", "action_release", "action_forfeit", "action_cancel"},
    },
    "fix.payout.reconciliation": {
        "order": "reconciliation_date desc, id desc",
        "limit": 100,
        "actions": {"action_run_reconciliation"},
    },
}


def _as_date(value, default):
    if not value:
        return default
    if isinstance(value, datetime.date):
        return value
    return datetime.date.fromisoformat(str(value)[:10])


def _round_row(row):
    return {k: (round(v, 2) if isinstance(v, float) else v) for k, v in row.items()}


def contract_balances(env, date_from=None, date_to=None, **params):
    """IFRS 15 contract assets & liabilities per contract, as at date_to:
    billed (issued subscription-charge invoices, net of credit notes, VAT
    excluded) vs recognised (posted recognition of the contract's
    performance obligations). Billed > recognised = contract liability;
    recognised > billed = contract asset."""
    today = datetime.date.today()
    d_to = _as_date(date_to, today)
    d_from = _as_date(date_from, d_to.replace(day=1))
    Sub = env["fix.subscription"]
    Invoice = env["fix.ar.invoice"]
    Line = env["fix.revenue.recognition.line"]
    rows = []
    for sub in Sub.search([("company_id", "in", env.companies.ids)], order="name"):
        charges = sub.charge_ids
        invoices = Invoice.search(
            [
                ("source_model", "=", "fix.subscription.charge"),
                ("source_id", "in", charges.ids),
                ("state", "in", ("issued", "paid", "credited")),
                ("invoice_date", "<=", d_to),
            ]
        )

        def _net(invs):
            total = 0.0
            for inv in invs:
                ratio = (inv.taxable_amount / inv.total_payable) if inv.total_payable else 0.0
                total += inv.taxable_amount - inv.credited_amount * ratio
            return total

        billed = _net(invoices)
        billed_period = _net(invoices.filtered(lambda i: i.invoice_date >= d_from))
        schedules = sub.obligation_ids.mapped("schedule_id")
        lines = Line.search([("schedule_id", "in", schedules.ids), ("date", "<=", d_to)])
        recognised = sum(lines.mapped("amount"))
        recognised_period = sum(lines.filtered(lambda ln: ln.date >= d_from).mapped("amount"))
        if not (billed or recognised):
            continue
        balance = billed - recognised
        rows.append(
            _round_row(
                {
                    "contract": sub.name,
                    "customer": sub.customer_id.name,
                    "transaction_price": sub.contract_value or 0.0,
                    "billed_period": billed_period,
                    "recognised_period": recognised_period,
                    "billed": billed,
                    "recognised": recognised,
                    "contract_liability": max(balance, 0.0),
                    "contract_asset": max(-balance, 0.0),
                }
            )
        )
    cols = [
        "contract",
        "customer",
        "transaction_price",
        "billed_period",
        "recognised_period",
        "billed",
        "recognised",
        "contract_liability",
        "contract_asset",
    ]
    totals = {"contract": "Total"}
    for c in cols[2:]:
        totals[c] = round(sum(r[c] for r in rows), 2)
    return {
        "title": "Contract assets & liabilities as at %s" % d_to,
        "cols": cols,
        "labels": {
            "contract": "Contract",
            "customer": "Customer",
            "transaction_price": "Transaction Price",
            "billed_period": "Billed in Period",
            "recognised_period": "Recognised in Period",
            "billed": "Billed to Date",
            "recognised": "Recognised to Date",
            "contract_liability": "Contract Liability",
            "contract_asset": "Contract Asset",
        },
        "rows": rows,
        "totals": totals if rows else None,
        "empty": "No contract has billing or recognition up to this date.",
        "notes": [
            "Billed = issued cycle-charge invoices (VAT excluded) less credit notes; "
            "recognised = posted recognition of the contract's performance obligations.",
            "Draft invoices are not billed: issue them in M20 first.",
        ],
    }


def _stream_label(env, schedule):
    if schedule.source_model == "fix.performance.obligation":
        obligation = env["fix.performance.obligation"].browse(schedule.source_id).exists()
        if obligation:
            return dict(obligation._fields["obligation_type"].selection).get(
                obligation.obligation_type, obligation.obligation_type
            )
    return schedule.source_model or "—"


def deferred_revenue_bridge(env, date_from=None, date_to=None, **params):
    """Deferred-revenue roll-forward by revenue stream for the period:
    opening deferred + new deferrals - recognised - released = closing."""
    today = datetime.date.today()
    d_to = _as_date(date_to, today)
    d_from = _as_date(date_from, d_to.replace(day=1))
    Schedule = env["fix.revenue.schedule"]
    Line = env["fix.revenue.recognition.line"]
    streams = {}
    for schedule in Schedule.search(
        [("company_id", "in", env.companies.ids), ("start_date", "<=", d_to)]
    ):
        if schedule.state == "cancelled" and (
            not schedule.cancelled_date or schedule.cancelled_date < d_from
        ):
            continue  # cancelled before this period: nothing left to bridge
        key = _stream_label(env, schedule)
        row = streams.setdefault(
            key,
            {
                "stream": key,
                "opening": 0.0,
                "new": 0.0,
                "recognised": 0.0,
                "released": 0.0,
                "closing": 0.0,
            },
        )
        lines = Line.search([("schedule_id", "=", schedule.id), ("date", "<=", d_to)])
        before = sum(lines.filtered(lambda ln: ln.date < d_from).mapped("amount"))
        during = sum(lines.filtered(lambda ln: ln.date >= d_from).mapped("amount"))
        if schedule.start_date < d_from:
            row["opening"] += schedule.total_amount - before
        else:
            row["new"] += schedule.total_amount
        row["recognised"] += during
        if not (schedule.state == "cancelled" and schedule.cancelled_date <= d_to):
            row["closing"] += schedule.total_amount - before - during
    rows = []
    for row in streams.values():
        row["released"] = row["opening"] + row["new"] - row["recognised"] - row["closing"]
        rows.append(_round_row(row))
    cols = ["stream", "opening", "new", "recognised", "released", "closing"]
    totals = {"stream": "Total"}
    for c in cols[1:]:
        totals[c] = round(sum(r[c] for r in rows), 2)
    return {
        "title": "Deferred revenue bridge %s to %s" % (d_from, d_to),
        "cols": cols,
        "labels": {
            "stream": "Revenue Stream",
            "opening": "Opening Deferred",
            "new": "New Deferrals",
            "recognised": "Recognised",
            "released": "Released (cancellations)",
            "closing": "Closing Deferred",
        },
        "rows": rows,
        "totals": totals if rows else None,
        "empty": "No revenue schedules in this period.",
        "notes": [
            "Recognised = posted recognition lines in the period (Dr contract liability / "
            "Cr revenue); released = the unrecognised remainder of cancelled schedules.",
        ],
    }


REPORTS = {
    "contract_balances": contract_balances,
    "deferred_revenue_bridge": deferred_revenue_bridge,
}


def kpis(env):
    """Real M53 tile metrics (BDT unless a count)."""
    companies = env.companies.ids
    month_start = datetime.date.today().replace(day=1)
    schedules = env["fix.revenue.schedule"].search(
        [("company_id", "in", companies), ("state", "=", "active")]
    )
    lines = env["fix.revenue.recognition.line"].search(
        [("company_id", "in", companies), ("date", ">=", month_start)]
    )
    escrow = env["fix.settlement.adjustment"].search(
        [
            ("company_id", "in", companies),
            ("adjustment_type", "=", "escrow"),
            ("state", "=", "active"),
        ]
    )
    return {
        "deferred_revenue_balance": round(sum(schedules.mapped("deferred_balance")), 2),
        "recognised_mtd": round(sum(lines.mapped("amount")), 2),
        "escrow_held_amount": round(sum(escrow.mapped("amount")), 2),
    }
