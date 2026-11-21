# A08 · M53 Revenue Recognition & Settlement — models the generic workspace screens may read,
# and the workflow methods they may call (/p03/model/records, /p03/model/action).
# Each entry: model -> {"order", "limit", "actions"}. Reads also need the
# user's own read access on the model (accounting/payroll groups apply).
import datetime

SURFACES = {
    # A08 M53-1/3: payout-run rows are pinned at approval; read-only here.
    "fix.payout.run.line": {"order": "id desc", "limit": 500, "actions": set()},
    # --- revenue (IFRS 15) ---
    "fix.performance.obligation": {
        "order": "subscription_id, id",
        "limit": 200,
        "actions": {"action_create_schedule", "action_recognize"},
    },
    "fix.revenue.schedule": {
        "order": "start_date desc, id desc",
        "limit": 200,
        "actions": {
            "action_recognize_period",
            "action_request_cfo_approval",
            "action_cancel_held",
            "action_reopen_as_manual",
        },
    },
    "fix.subscription": {
        "order": "next_invoice_date, id desc",
        "limit": 200,
        # A04 ERP audit (2026-11-21) M39-F9: a cycle is billed only by a
        # reviewed billing run (BRU-SUB-17), never by a button on one
        # subscription - action_generate_charge needs the run's token.
        "actions": {
            "action_trigger_dunning",
            "action_reinstate",
            "action_request_refund",
            "action_allocate_price",
            "action_generate_revrec_schedule",
            "action_request_contract_value",
            "action_approve_contract_value",
        },
        # A04 hand-off closure (2026-11-05): what the subscription form may
        # set through /p03/model/write. The state, dunning ladder and refund
        # stamps are model-readonly and guarded on fix.subscription; a
        # mid-term price or plan change runs through an approved proration,
        # never the form.
        "writable": frozenset(
            {
                "name",
                "customer_id",
                "contract_id",
                "plan",
                "billing_cycle",
                "recurring_amount",
                "start_date",
                "next_invoice_date",
                "grace_period_days",
                "consolidated",
                "currency_id",
                "company_id",
                "operating_unit_id",
                "contract_value",
                "contract_end_date",
            }
        ),
    },
    "fix.warranty.provision": {
        "order": "period desc, id desc",
        "limit": 60,
        "actions": {"action_compute", "action_post"},
    },
    "fix.warranty.provision.policy": {"order": "date_from desc", "limit": 50, "actions": set()},
    # --- commission ---
    "fix.commission.ledger": {
        "order": "id desc",
        "limit": 200,
        "actions": {
            "action_post_to_gl",
            "action_link_source",
            "action_void_unsourced",
            "action_void_all_unsourced",
        },
    },
    "fix.commission.scheme": {
        "order": "scheme_type, date_from desc",
        "limit": 100,
        "actions": set(),
    },
    # --- settlements ---
    "fix.payout.run": {
        "order": "id desc",
        "limit": 100,
        # A08 F2: approval is decided from the M63 inbox; money moves only as
        # M50 payment instructions confirmed from the bank statement
        "actions": {
            "action_collect_accrued",
            "action_prepare",
            "action_request_payments",
            "action_query_status",
            "action_cancel",
            "action_rerequest_unpaid",
            "action_drop_unpaid",
            "action_open_reconciliation",
        },
    },
    "fix.seller.statement": {
        "order": "period desc, id desc",
        "limit": 100,
        "actions": {"action_issue_statement", "action_settle_statement", "action_attach_challan"},
    },
    "fix.referral": {
        "order": "id desc",
        "limit": 200,
        # M53-4: convert from the paid invoice (the referral manager), earn,
        # then finance accrues
        "actions": {"action_convert", "action_earn_commission", "action_accrue_commission"},
    },
    "fix.settlement.adjustment": {
        "order": "id desc",
        "limit": 200,
        "actions": {"action_activate", "action_release", "action_forfeit", "action_cancel"},
    },
    "fix.payout.reconciliation": {
        "order": "reconciliation_date desc, id desc",
        "limit": 100,
        "actions": {"action_run_reconciliation", "action_investigate", "action_resolve_break"},
    },
    # --- capture audit 2026-11-17: the records pages 2, 4, 5, 7 and 8 lacked ---
    "fix.ssp": {
        "order": "obligation_type, effective_from desc, id desc",
        "limit": 200,
        "actions": {"action_submit", "action_approve", "action_reject"},
    },
    "fix.contract.modification": {
        "order": "modification_date desc, id desc",
        "limit": 200,
        "actions": {"action_submit", "action_approve", "action_reject"},
    },
    "fix.contract.modification.line": {"order": "id desc", "limit": 200, "actions": set()},
    "fix.revenue.presentation": {
        "order": "arrangement, effective_from desc, id desc",
        "limit": 50,
        "actions": {"action_submit", "action_approve", "action_reject"},
    },
    "fix.payout.hold": {
        "order": "id desc",
        "limit": 200,
        "actions": {"action_raise", "action_release"},
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
        [
            ("company_id", "in", env.companies.ids),
            ("start_date", "<=", d_to),
            # awaiting the CFO, or held with no contract: nothing is deferred (M53-6)
            ("state", "not in", ("draft", "held")),
        ]
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


def rev_rec_by_stream(env, date_from=None, date_to=None, **params):
    """Revenue recognition by stream: contracted, recognised to date and the
    deferred remainder, per revenue stream across all schedules."""
    schedules = env["fix.revenue.schedule"].search([("company_id", "in", env.companies.ids)])
    groups = {}
    for sch in schedules:
        key = _stream_label(env, sch)
        g = groups.setdefault(
            key, {"contracts": 0, "total": 0.0, "recognized": 0.0, "deferred": 0.0}
        )
        g["contracts"] += 1
        g["total"] += float(sch.total_amount or 0.0)
        g["recognized"] += float(sch.recognized_amount or 0.0)
        g["deferred"] += float(sch.deferred_balance or 0.0)
    rows = [
        {
            "stream": k,
            "contracts": v["contracts"],
            "contracted": round(v["total"], 2),
            "recognized": round(v["recognized"], 2),
            "deferred": round(v["deferred"], 2),
            "pct_recognized": round(v["recognized"] / v["total"] * 100.0, 1) if v["total"] else 0.0,
        }
        for k, v in sorted(groups.items(), key=lambda kv: -kv[1]["total"])
    ]
    return {
        "title": "Revenue Recognition by Stream",
        "cols": ["stream", "contracts", "contracted", "recognized", "deferred", "pct_recognized"],
        "labels": {
            "stream": "Revenue Stream",
            "contracts": "Schedules",
            "contracted": "Contracted",
            "recognized": "Recognised to Date",
            "deferred": "Deferred Balance",
            "pct_recognized": "% Recognised",
        },
        "rows": rows,
        "totals": {
            "stream": "Total",
            "contracts": sum(r["contracts"] for r in rows),
            "contracted": round(sum(r["contracted"] for r in rows), 2),
            "recognized": round(sum(r["recognized"] for r in rows), 2),
            "deferred": round(sum(r["deferred"] for r in rows), 2),
        },
        "notes": "Streams are the performance-obligation types (and raw source models for "
        "non-PO schedules); % recognised is against the contracted amount.",
        "empty": "No revenue schedules recorded.",
    }


def commission_accrual(env, date_from=None, date_to=None, **params):
    """Commission accrual: every ledger entry with its scheme rate, TDS and
    net, and the accrual state."""
    domain = [("company_id", "in", env.companies.ids)]
    if date_from:
        domain.append(("create_date", ">=", date_from))
    if date_to:
        domain.append(("create_date", "<=", date_to))
    lines = env["fix.commission.ledger"].search(domain)
    rows = []
    for ln in lines:
        rows.append(
            {
                "entry": ln.name,
                "seller": ln.seller_partner_id.display_name if ln.seller_partner_id else "—",
                "source": ln.source_ref or "—",
                "gross": round(float(ln.gross_amount or 0.0), 2),
                "rate": round(float(ln.commission_rate or 0.0) * 100, 2),
                "commission": round(float(ln.commission_amount or 0.0), 2),
                "tds": round(float(ln.tds_amount or 0.0), 2),
                "net": round(float(ln.net_payable or 0.0), 2),
                "state": dict(ln._fields["state"].selection).get(ln.state, ln.state),
            }
        )
    return {
        "title": "Commission Accrual Ledger",
        "cols": ["entry", "seller", "source", "gross", "rate", "commission", "tds", "net", "state"],
        "labels": {
            "entry": "Entry",
            "seller": "Seller / Partner",
            "source": "Source Reference",
            "gross": "Gross Basis",
            "rate": "Rate %",
            "commission": "Commission",
            "tds": "TDS Withheld",
            "net": "Net Payable",
            "state": "State",
        },
        "rows": rows,
        "totals": {
            "entry": "Total",
            "gross": round(sum(r["gross"] for r in rows), 2),
            "commission": round(sum(r["commission"] for r in rows), 2),
            "tds": round(sum(r["tds"] for r in rows), 2),
            "net": round(sum(r["net"] for r in rows), 2),
        },
        "notes": "TDS withheld at source per ITA 2023 section 140 on commissions, from the scheme in force and the payee's PSR.",
        "empty": "No commission entries recorded.",
    }


def payout_reconciliation(env, date_from=None, date_to=None, **params):
    """Payout reconciliation: each rail statement vs the system's payout run,
    with count and amount match flags and the unmatched remainder."""
    recs = env["fix.payout.reconciliation"].search([("company_id", "in", env.companies.ids)])
    rows = []
    for r in recs:
        rows.append(
            {
                "recon": r.name,
                "run": r.payout_run_id.name if r.payout_run_id else "—",
                "rail": r.rail_name or "—",
                "date": str(r.reconciliation_date or "—"),
                "system_count": r.system_count,
                "rail_count": r.rail_count,
                "count_ok": "✓" if r.count_matched else "✗",
                "system_amount": round(float(r.system_amount or 0.0), 2),
                "rail_amount": round(float(r.rail_amount or 0.0), 2),
                "amount_ok": "✓" if r.amount_matched else "✗",
                "unmatched": round(float(r.unmatched_amount or 0.0), 2),
            }
        )
    return {
        "title": "Payout Reconciliation — rail statement vs payout run",
        "cols": [
            "recon",
            "run",
            "rail",
            "date",
            "system_count",
            "rail_count",
            "count_ok",
            "system_amount",
            "rail_amount",
            "amount_ok",
            "unmatched",
        ],
        "labels": {
            "recon": "Reconciliation",
            "run": "Payout Run",
            "rail": "Rail",
            "date": "Date",
            "system_count": "System Count",
            "rail_count": "Rail Count",
            "count_ok": "Counts",
            "system_amount": "System Amount",
            "rail_amount": "Rail Amount",
            "amount_ok": "Amounts",
            "unmatched": "Unmatched",
        },
        "rows": rows,
        "totals": {
            "recon": "Total",
            "system_amount": round(sum(r["system_amount"] for r in rows), 2),
            "rail_amount": round(sum(r["rail_amount"] for r in rows), 2),
            "unmatched": round(sum(r["unmatched"] for r in rows), 2),
        },
        "notes": "Counts and amounts are matched independently; the unmatched remainder is what "
        "the rail statement did not settle.",
        "empty": "No payout reconciliations recorded.",
    }


def clawback_register(env, date_from=None, date_to=None, **params):
    """Clawback & escrow register: adjustments held against future payouts,
    with recovery progress."""
    domain = [
        ("adjustment_type", "in", ("clawback", "escrow")),
        ("company_id", "in", env.companies.ids),
    ]
    if date_from:
        domain.append(("create_date", ">=", date_from))
    if date_to:
        domain.append(("create_date", "<=", date_to))
    adjustments = env["fix.settlement.adjustment"].search(domain)
    rows = []
    for a in adjustments:
        rows.append(
            {
                "ref": a.name,
                "type": dict(a._fields["adjustment_type"].selection).get(
                    a.adjustment_type, a.adjustment_type
                ),
                "seller": a.seller_partner_id.display_name if a.seller_partner_id else "—",
                "amount": round(float(a.amount or 0.0), 2),
                "recovered": round(float(a.recovered_amount or 0.0), 2),
                "outstanding": round(float(a.amount or 0.0) - float(a.recovered_amount or 0.0), 2),
                "state": dict(a._fields["state"].selection).get(a.state, a.state),
            }
        )
    return {
        "title": "Clawback & Escrow Register",
        "cols": ["ref", "type", "seller", "amount", "recovered", "outstanding", "state"],
        "labels": {
            "ref": "Reference",
            "type": "Type",
            "seller": "Seller",
            "amount": "Amount",
            "recovered": "Recovered",
            "outstanding": "Outstanding",
            "state": "State",
        },
        "rows": rows,
        "totals": {
            "ref": "Total",
            "amount": round(sum(r["amount"] for r in rows), 2),
            "recovered": round(sum(r["recovered"] for r in rows), 2),
            "outstanding": round(sum(r["outstanding"] for r in rows), 2),
        },
        "notes": "Escrow holds freeze disputed amounts; clawbacks recover from future payouts.",
        "empty": "No clawbacks or escrow holds recorded.",
    }


REPORTS = {
    "contract_balances": contract_balances,
    "deferred_revenue_bridge": deferred_revenue_bridge,
    "rev_rec_by_stream": rev_rec_by_stream,
    "commission_accrual": commission_accrual,
    "payout_reconciliation": payout_reconciliation,
    "clawback_register": clawback_register,
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
