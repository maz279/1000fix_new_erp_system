# cd_cash_position — M50 computed treasury reports (A08 table_report screens).
#
# Every function reads with the CALLER's environment (the models' own access
# rules apply) and returns {cols, labels, rows, totals?, notes?, title?,
# empty?}. Nothing here is stored or seeded: each row is a computation over
# posted GL lines and the treasury documents.
from __future__ import annotations

from collections import defaultdict
from datetime import date, timedelta

from odoo import fields

from .treasury_common import gl_balance, treasury_account

LIQUID_TYPES = ("bank", "cash")


def _d(value, default=None):
    if not value:
        return default
    return fields.Date.to_date(value)


def _company(env):
    return env.company


def _liquid_journals(env, company, types=LIQUID_TYPES):
    return env["account.journal"].search(
        [("type", "in", list(types)), ("company_id", "=", company.id)]
    )


def _has(env, model):
    return model in env


def _r(value):
    return round(value or 0.0, 2)


# --------------------------------------------------------------------------- position


def liquid_position(env, company, as_of=None):
    """(bank+cash GL, drawers, petty, in transit, pending payments)."""
    as_of = as_of or fields.Date.context_today(env.user)
    journals = _liquid_journals(env, company)
    bank_gl = gl_balance(env, journals.mapped("default_account_id"), company, date_to=as_of)
    drawers = sum(
        env["fix.cash.shift"]
        .search([("company_id", "=", company.id), ("state", "in", ("open", "counting"))])
        .mapped("expected_closing")
    )
    petty = sum(
        env["fix.imprest.fund"]
        .search([("company_id", "=", company.id), ("state", "=", "active")])
        .mapped("book_balance")
    )
    cit = sum(
        env["fix.cash.deposit"]
        .search([("company_id", "=", company.id), ("state", "=", "in_transit")])
        .mapped("amount")
    )
    pending = sum(
        env["fix.payment.execution"]
        .search([("company_id", "=", company.id), ("state", "in", ("pending", "prepared", "sent"))])
        .mapped("amount")
    )
    return _r(bank_gl), _r(drawers), _r(petty), _r(cit), _r(pending)


def daily_cash_position(env, date_from=None, date_to=None, **_kw):
    company = _company(env)
    as_of = _d(date_to, fields.Date.context_today(env.user))
    rows = []
    Line = env["fix.bank.statement.line"]
    for journal in _liquid_journals(env, company):
        balance = gl_balance(env, journal.default_account_id, company, date_to=as_of)
        rows.append(
            {
                "item": journal.name,
                "kind": "Bank" if journal.type == "bank" else "Cash",
                "detail": journal.bank_acc_number or journal.code,
                "amount": _r(balance),
                "unmatched": Line.search_count(
                    [("journal_id", "=", journal.id), ("match_state", "=", "unmatched")]
                ),
            }
        )
    _bank, drawers, petty, cit, pending = liquid_position(env, company, as_of)
    rows += [
        {
            "item": "Branch drawers (open shifts)",
            "kind": "Branch cash",
            "detail": "M04 cash shifts",
            "amount": drawers,
            "unmatched": None,
        },
        {
            "item": "Petty cash funds",
            "kind": "Imprest",
            "detail": "Book balances",
            "amount": petty,
            "unmatched": None,
        },
        {
            "item": "Cash-in-transit",
            "kind": "In transit",
            "detail": "Deposits awaiting bank credit",
            "amount": cit,
            "unmatched": None,
        },
        {
            "item": "Payments queued / sent",
            "kind": "Outflow",
            "detail": "Not yet confirmed by the bank",
            "amount": -pending,
            "unmatched": None,
        },
    ]
    total = _r(sum(r["amount"] for r in rows))
    return {
        "title": "Daily Cash Position — %s (as of %s)" % (company.name, as_of),
        "cols": ["item", "kind", "detail", "amount", "unmatched"],
        "labels": {
            "item": "Account / Item",
            "kind": "Type",
            "detail": "Detail",
            "amount": "Amount (BDT)",
            "unmatched": "Unmatched Lines",
        },
        "rows": rows,
        "totals": {"item": "Net cash position", "amount": total},
        "notes": [
            "Bank and cash balances are the posted GL balances of each journal's account.",
            "Queued / sent payments are deducted until the bank confirms them.",
        ],
    }


# --------------------------------------------------------------------------- reconciliation


def bank_recon_summary(env, date_from=None, date_to=None, **_kw):
    company = _company(env)
    d_from = _d(date_from)
    d_to = _d(date_to, fields.Date.context_today(env.user))
    Line = env["fix.bank.statement.line"]
    rows = []
    journals = _liquid_journals(env, company, ("bank",))
    for journal in journals:
        dom = [
            ("company_id", "=", company.id),
            ("journal_id", "=", journal.id),
            ("date", "<=", d_to),
        ]
        if d_from:
            dom.append(("date", ">=", d_from))
        lines = Line.search(dom)
        unmatched = lines.filtered(lambda ln: ln.match_state == "unmatched")
        last = env["fix.bank.reconciliation"].search(
            [
                ("company_id", "=", company.id),
                ("journal_id", "=", journal.id),
                ("state", "=", "reviewed"),
            ],
            order="period desc",
            limit=1,
        )
        rows.append(
            {
                "account": journal.name,
                "last_reviewed": (
                    "%s (%s)" % (last.period, last.reviewed_by_id.name) if last else "Never"
                ),
                "gl_balance": _r(
                    gl_balance(env, journal.default_account_id, company, date_to=d_to)
                ),
                "lines": len(lines),
                "matched": len(lines) - len(unmatched),
                "unmatched": len(unmatched),
                "unmatched_in": _r(
                    sum(unmatched.filtered(lambda ln: ln.amount > 0).mapped("amount"))
                ),
                "unmatched_out": _r(
                    -sum(unmatched.filtered(lambda ln: ln.amount < 0).mapped("amount"))
                ),
                "awaiting_bank": env["fix.payment.execution"].search_count(
                    [("journal_id", "=", journal.id), ("state", "=", "sent")]
                ),
                "in_transit": _r(
                    sum(
                        env["fix.cash.deposit"]
                        .search([("journal_id", "=", journal.id), ("state", "=", "in_transit")])
                        .mapped("amount")
                    )
                ),
            }
        )
    # lines imported without a bank account
    dom = [("company_id", "=", company.id), ("journal_id", "=", False), ("date", "<=", d_to)]
    if d_from:
        dom.append(("date", ">=", d_from))
    orphan = Line.search(dom)
    if orphan:
        unmatched = orphan.filtered(lambda ln: ln.match_state == "unmatched")
        rows.append(
            {
                "account": "(no bank account on the line)",
                "last_reviewed": "",
                "gl_balance": None,
                "lines": len(orphan),
                "matched": len(orphan) - len(unmatched),
                "unmatched": len(unmatched),
                "unmatched_in": _r(
                    sum(unmatched.filtered(lambda ln: ln.amount > 0).mapped("amount"))
                ),
                "unmatched_out": _r(
                    -sum(unmatched.filtered(lambda ln: ln.amount < 0).mapped("amount"))
                ),
                "awaiting_bank": None,
                "in_transit": None,
            }
        )
    unconfirmed = env["fix.payment.execution"].search_count(
        [
            ("company_id", "=", company.id),
            ("state", "=", "executed"),
            ("bank_confirmed", "=", False),
        ]
    )
    total_lines = sum(r["lines"] for r in rows)
    total_matched = sum(r["matched"] for r in rows)
    return {
        "title": "Bank Reconciliation Summary",
        "cols": [
            "account",
            "gl_balance",
            "lines",
            "matched",
            "unmatched",
            "unmatched_in",
            "unmatched_out",
            "awaiting_bank",
            "in_transit",
            "last_reviewed",
        ],
        "labels": {
            "account": "Bank Account",
            "last_reviewed": "Last Reviewed Statement",
            "gl_balance": "GL Balance",
            "lines": "Statement Lines",
            "matched": "Matched",
            "unmatched": "Unmatched",
            "unmatched_in": "Unmatched Credits",
            "unmatched_out": "Unmatched Debits",
            "awaiting_bank": "Payments Awaiting Bank",
            "in_transit": "Deposits in Transit",
        },
        "rows": rows,
        "totals": {
            "account": "Total",
            "lines": total_lines,
            "matched": total_matched,
            "unmatched": total_lines - total_matched,
        },
        "notes": [
            "Match rate: %s%%."
            % (round(total_matched / total_lines * 100.0, 1) if total_lines else 0.0),
            "Payments executed by a calling module without bank evidence: %s (shown until a statement line confirms them)."
            % unconfirmed,
            "The statement itself, per account and period with its second-person review, is on "
            "Reconciliation Statements.",
        ],
        "empty": "No bank journals.",
    }


def gateway_recon(env, date_from=None, date_to=None, **_kw):
    company = _company(env)
    dom = [("company_id", "=", company.id)]
    if date_from:
        dom.append(("settlement_date", ">=", _d(date_from)))
    if date_to:
        dom.append(("settlement_date", "<=", _d(date_to)))
    sel = dict(env["fix.gateway.settlement"]._fields["state"].selection)
    prov = dict(env["fix.gateway.settlement"]._fields["provider"].selection)
    rows = []
    for b in env["fix.gateway.settlement"].search(dom, order="settlement_date desc, id desc"):
        rows.append(
            {
                "batch": b.name,
                "provider": prov.get(b.provider),
                "date": str(b.settlement_date),
                "lines": b.line_count,
                "gross": _r(b.total_gross),
                "fees": _r(b.total_fee + b.total_fee_vat),
                "net": _r(b.total_net),
                "exceptions": b.exception_count,
                "bank": "Matched" if b.bank_matched else "Awaiting credit",
                "state": sel.get(b.state),
            }
        )
    return {
        "title": "Gateway Settlement Reconciliation (receipts ↔ report ↔ bank)",
        "cols": [
            "batch",
            "provider",
            "date",
            "lines",
            "gross",
            "fees",
            "net",
            "exceptions",
            "bank",
            "state",
        ],
        "labels": {
            "batch": "Batch",
            "provider": "Provider",
            "date": "Settlement Date",
            "lines": "Transactions",
            "gross": "Gross",
            "fees": "Fees + VAT",
            "net": "Net",
            "exceptions": "Exceptions",
            "bank": "Bank Credit",
            "state": "Status",
        },
        "rows": rows,
        "totals": {
            "batch": "Total",
            "lines": sum(r["lines"] for r in rows),
            "gross": _r(sum(r["gross"] for r in rows)),
            "fees": _r(sum(r["fees"] for r in rows)),
            "net": _r(sum(r["net"] for r in rows)),
            "exceptions": sum(r["exceptions"] for r in rows),
        },
        "empty": "No settlement batches in the period — import a provider report on Gateway / MFS Settlement.",
    }


# M50 COD report. Two channels clear COD clearing (debited by the M20 cod
# receipt on a verified delivery): in-house riders (fix.cod.settlement:
# Dr cash/bank remitted [+ Dr rider shortage] / Cr COD clearing expected) and,
# since G10, third-party couriers (fix.courier.remittance: Dr bank net + Dr
# courier charges / Cr COD clearing gross). The report lists both, with each
# channel's total, and proves its figures against the ledger: a settled row
# shows what its own entry credited to COD clearing, and the period's gross
# settled, net banked and charges are tied to the COD clearing, bank and
# charges movements; a COD clearing credit no settlement made is called out.
_COD_COLS = [
    "channel",
    "ref",
    "date",
    "orders",
    "gross",
    "charges",
    "net",
    "variance",
    "gl_cleared",
    "tie",
    "state",
]
_COD_SUMMED = ("orders", "gross", "charges", "net", "variance", "gl_cleared")
RIDER_CHANNEL = "Rider"
COURIER_CHANNEL = "Courier"


def _cod_entry_split(move, clearing, cash_account, charges_account):
    """(credited to COD clearing, debited to the bank / cash account, debited
    to courier charges) by one settlement or remittance entry."""
    cleared = banked = charged = 0.0
    for line in move.line_ids:
        if clearing and line.account_id == clearing:
            cleared += line.credit - line.debit
        elif cash_account and line.account_id == cash_account:
            banked += line.debit - line.credit
        elif charges_account and line.account_id == charges_account:
            charged += line.debit - line.credit
    return _r(cleared), _r(banked), _r(charged)


def _cod_tie_label(row, split):
    cleared, banked, charged = split
    off = []
    if abs(cleared - row["gross"]) > 0.005:
        off.append("COD clearing %.2f vs gross %.2f" % (cleared, row["gross"]))
    if abs(banked - row["net"]) > 0.005:
        off.append("bank %.2f vs net %.2f" % (banked, row["net"]))
    if abs(charged - row["charges"]) > 0.005:
        off.append("charges %.2f vs %.2f" % (charged, row["charges"]))
    return "Ties" if not off else "Off: " + "; ".join(off)


def _cod_summed(rows):
    out = {}
    for key in _COD_SUMMED:
        total = sum(r[key] or 0 for r in rows)
        out[key] = total if key == "orders" else _r(total)
    return out


def _cod_channel_group(row):
    """Riders are one channel; each courier is its own."""
    return RIDER_CHANNEL + "s" if row["channel"].startswith(RIDER_CHANNEL) else row["channel"]


def cod_report(env, date_from=None, date_to=None, **_kw):
    company = _company(env)
    if not _has(env, "fix.storefront.order"):
        return {
            "cols": [],
            "rows": [],
            "empty": "No COD source model is installed (storefront orders).",
        }
    from .courier_remittance import live_cod_orders

    d_from, d_to = _d(date_from), _d(date_to)
    clearing = treasury_account(env, company, "cod_clearing", required=False)
    charges_account = treasury_account(env, company, "courier_charges", required=False)
    settled = []  # (row, entry split) of the settled documents: the tie

    def in_period(field):
        dom = [("company_id", "=", company.id)]
        if d_from:
            dom.append((field, ">=", d_from))
        if d_to:
            dom.append((field, "<=", d_to))
        return dom

    def finish(row, doc, cash_account):
        if doc.state == "settled" and doc.move_id:
            split = _cod_entry_split(doc.move_id, clearing, cash_account, charges_account)
            row["gl_cleared"], row["tie"] = split[0], _cod_tie_label(row, split)
            settled.append((row, split))
        else:
            row["gl_cleared"], row["tie"] = None, ""
        return row

    details = []
    Settlement = env["fix.cod.settlement"]
    sel = dict(Settlement._fields["state"].selection)
    for s in Settlement.search(in_period("settlement_date"), order="settlement_date, id"):
        row = {
            "channel": "%s — %s" % (RIDER_CHANNEL, s.rider_id.name or "-"),
            "ref": s.name,
            "date": str(s.settlement_date),
            "orders": s.order_count,
            "gross": _r(s.expected_amount),
            "charges": 0.0,
            "net": _r(s.remitted_amount),
            "variance": _r(s.variance),
            "state": sel.get(s.state),
        }
        details.append(finish(row, s, s.remittance_journal_id.default_account_id))
    if _has(env, "fix.courier.remittance"):
        Remittance = env["fix.courier.remittance"]
        rsel = dict(Remittance._fields["state"].selection)
        for r in Remittance.search(in_period("remittance_date"), order="remittance_date, id"):
            row = {
                "channel": "%s — %s" % (COURIER_CHANNEL, r.courier_id.name or "-"),
                "ref": r.name,
                "date": str(r.remittance_date),
                "orders": r.order_count,
                "gross": _r(r.gross_amount),
                "charges": _r(r.total_charges),
                "net": _r(r.net_amount),
                # net + charges - gross: 0 on any submitted remittance
                "variance": _r(-r.difference),
                "state": rsel.get(r.state),
            }
            details.append(finish(row, r, r.journal_id.default_account_id))

    # delivered COD not yet in any live settlement or remittance: held by the
    # rider, else by the courier that carried it (one owner per order)
    orders = env["fix.storefront.order"].search(
        [
            ("company_id", "=", company.id),
            ("payment_rail", "=", "cod"),
            ("state", "not in", ("cancelled", "draft")),
            ("carrier_consignment_id.state", "=", "delivered"),
        ]
    )
    held = defaultdict(lambda: [0, 0.0])
    for o in orders - live_cod_orders(env, company):
        cons = o.carrier_consignment_id
        if cons.rider_id:
            key = "%s — %s" % (RIDER_CHANNEL, cons.rider_id.name)
        elif "courier_partner_id" in cons._fields and cons.courier_partner_id:
            if o._fix_cod_paid_elsewhere():
                continue  # prepaid or settled by another receipt: no cash held
            key = "%s — %s" % (COURIER_CHANNEL, cons.courier_partner_id.name)
        else:
            continue
        held[key][0] += 1
        held[key][1] += o.total_amount
    for channel, (count, amount) in sorted(held.items()):
        details.append(
            {
                "channel": channel,
                "ref": "—",
                "date": "",
                "orders": count,
                "gross": _r(amount),
                "charges": None,
                "net": None,
                "variance": None,
                "gl_cleared": None,
                "tie": "",
                "state": "Unsettled",
            }
        )

    # per-channel totals, shown after each channel's rows
    groups = defaultdict(list)
    for row in details:
        groups[_cod_channel_group(row)].append(row)
    rows, channel_totals = [], []
    for channel in sorted(groups, key=lambda k: (not k.startswith(RIDER_CHANNEL), k)):
        members = sorted(
            groups[channel], key=lambda r: (r["state"] == "Unsettled", r["date"], r["ref"])
        )
        total = dict(_cod_summed(members), channel=channel)
        channel_totals.append(total)
        rows.extend(members)
        rows.append(dict(total, channel="%s — total" % channel, ref="", date="", tie="", state=""))

    # the tie: the report's settled figures against what the ledger moved
    credits = debits = 0.0
    if clearing:
        dom = [
            ("account_id", "=", clearing.id),
            ("company_id", "=", company.id),
            ("parent_state", "=", "posted"),
        ]
        if d_from:
            dom.append(("date", ">=", d_from))
        if d_to:
            dom.append(("date", "<=", d_to))
        lines = env["account.move.line"].search(dom)
        credits = _r(sum(lines.mapped("credit")))
        debits = _r(sum(lines.mapped("debit")))
    gross_settled = _r(sum(r["gross"] for r, _split in settled))
    tie = {
        "gross_settled": gross_settled,
        "gl_cleared_by_entries": _r(sum(split[0] for _row, split in settled)),
        "gl_cod_clearing_credits": credits,
        "gl_cod_clearing_debits": debits,
        "gross_difference": _r(gross_settled - credits),
        "net_banked": _r(sum(r["net"] for r, _split in settled)),
        "gl_net_banked": _r(sum(split[1] for _row, split in settled)),
        "charges": _r(sum(r["charges"] for r, _split in settled)),
        "gl_charges": _r(sum(split[2] for _row, split in settled)),
    }
    notes = [
        "Channels: in-house riders (COD settlements) and third-party couriers (courier "
        "remittances, net of the delivery and COD charges they deduct). Gross = the cash on "
        "delivery of the orders; Net = what reached the bank or cash; Variance = net + "
        "charges - gross (a rider's shortage is recovered from the rider).",
    ]
    if not clearing:
        notes.append(
            "COD clearing GL account not configured (cd_cash_position.account_code."
            "cod_clearing): the report cannot be tied to the ledger."
        )
    else:
        notes.append(
            "GL Cleared = what the row's own entry credited to COD clearing (%s). In the "
            "period COD clearing was debited %.2f (cash collected on delivery) and credited "
            "%.2f." % (clearing.code, debits, credits)
        )
        if abs(tie["gross_difference"]) > 0.005:
            notes.append(
                "Does NOT tie: COD clearing was credited %.2f in the period but the settled "
                "gross is %.2f: %.2f of credits came from no settlement or remittance."
                % (credits, gross_settled, -tie["gross_difference"])
            )
        else:
            notes.append(
                "Ties: settled gross %.2f = COD clearing credits %.2f." % (gross_settled, credits)
            )
    for label, reported, booked in (
        ("Net banked", tie["net_banked"], tie["gl_net_banked"]),
        ("Charges", tie["charges"], tie["gl_charges"]),
    ):
        if abs(reported - booked) > 0.005:
            notes.append(
                "Does NOT tie: %s %.2f, but the entries debited %.2f." % (label, reported, booked)
            )
        else:
            notes.append("%s %.2f = the entries' debits." % (label, reported))
    notes.append(
        "Cash collected by field technicians on service orders is not recorded by any model "
        "yet, so it is not in this report."
    )
    return {
        "title": "COD Settlement Report (riders and couriers)",
        "cols": list(_COD_COLS),
        "labels": {
            "channel": "Channel",
            "ref": "Settlement / Remittance",
            "date": "Date",
            "orders": "Orders",
            "gross": "Gross Collected",
            "charges": "Charges Deducted",
            "net": "Net Banked",
            "variance": "Variance",
            "gl_cleared": "GL Cleared (COD clearing)",
            "tie": "GL Tie",
            "state": "Status",
        },
        "rows": rows,
        "totals": dict(_cod_summed(details), channel="Total"),
        "channel_totals": channel_totals,
        "tie": tie,
        "notes": notes,
        "empty": "No COD collections, settlements or courier remittances in the period.",
    }


# --------------------------------------------------------------------------- branch cash


def branch_cash(env, date_from=None, date_to=None, **_kw):
    company = _company(env)
    d_to = _d(date_to, fields.Date.context_today(env.user))
    d_from = _d(date_from, d_to - timedelta(days=30))
    shifts = env["fix.cash.shift"].search(
        [("company_id", "=", company.id), ("shift_date", ">=", d_from), ("shift_date", "<=", d_to)]
    )
    deposits = env["fix.cash.deposit"].search(
        [
            ("company_id", "=", company.id),
            ("business_date", ">=", d_from),
            ("business_date", "<=", d_to),
            ("state", "not in", ("draft", "cancelled")),
        ]
    )
    days = defaultdict(lambda: env["fix.cash.shift"])
    for sh in shifts:
        days[(sh.branch_id, sh.shift_date)] |= sh
    dep_by = defaultdict(lambda: env["fix.cash.deposit"])
    for dep in deposits:
        dep_by[(dep.branch_id, dep.business_date)] |= dep
    rows = []
    for key in sorted(set(days) | set(dep_by), key=lambda k: (k[1], k[0].name or ""), reverse=True):
        branch, day = key
        day_shifts = days.get(key, env["fix.cash.shift"])
        counted_shifts = day_shifts.filtered(
            lambda s: s.state in ("closed", "reconciled", "discrepancy")
        )
        open_shifts = day_shifts - counted_shifts
        deps = dep_by.get(key, env["fix.cash.deposit"])
        due = sum(counted_shifts.mapped("closing_counted")) - sum(
            counted_shifts.mapped("opening_float")
        )
        deposited = sum(deps.mapped("amount"))
        credited = sum(
            deps.filtered(lambda d: d.state in ("credited", "variance")).mapped("credited_amount")
        )
        undeposited = round(due - deposited, 2)
        if open_shifts:
            status = "Drawer open"
        elif undeposited > 0.005:
            status = "Undeposited"
        elif deps.filtered(lambda d: d.state == "in_transit"):
            status = "In transit"
        elif deps.filtered(lambda d: d.state == "variance"):
            status = "Bank variance"
        elif due > 0.005 or deposited:
            status = "Reconciled"
        else:
            status = "No cash"
        rows.append(
            {
                "branch": branch.name,
                "day": str(day),
                "shifts": len(day_shifts),
                "receipts": _r(sum(day_shifts.mapped("cash_payments"))),
                "refunds": _r(
                    sum(day_shifts.mapped("cash_refunds")) + sum(day_shifts.mapped("cash_advances"))
                ),
                "expected": _r(sum(day_shifts.mapped("expected_closing"))),
                "counted": _r(sum(counted_shifts.mapped("closing_counted"))),
                "drawer_variance": _r(sum(counted_shifts.mapped("variance"))),
                "deposit_due": _r(due),
                "deposited": _r(deposited),
                "credited": _r(credited),
                "undeposited": _r(undeposited),
                "status": status,
            }
        )
    cols = [
        "branch",
        "day",
        "shifts",
        "receipts",
        "refunds",
        "expected",
        "counted",
        "drawer_variance",
        "deposit_due",
        "deposited",
        "credited",
        "undeposited",
        "status",
    ]
    totals = {"branch": "Total"}
    for c in cols[3:-1]:
        totals[c] = _r(sum(r[c] for r in rows))
    return {
        "title": "Branch Cash Consolidation",
        "cols": cols,
        "labels": {
            "branch": "Branch",
            "day": "Cash Day",
            "shifts": "Shifts",
            "receipts": "Cash Receipts",
            "refunds": "Refunds + Advances",
            "expected": "Expected Closing",
            "counted": "Counted",
            "drawer_variance": "Drawer Variance",
            "deposit_due": "To Deposit",
            "deposited": "Deposited",
            "credited": "Bank Credited",
            "undeposited": "Undeposited",
            "status": "Status",
        },
        "rows": rows,
        "totals": totals,
        "notes": [
            "To deposit = counted closing cash less the float the drawer opened with.",
            "Deposits come from Cash-in-Transit; 'Bank Credited' is confirmed by a bank statement line.",
        ],
        "empty": "No cash shifts in the period.",
    }


def branch_cash_uncollected(env, days=30):
    today = fields.Date.context_today(env.user)
    out = branch_cash(env, date_from=today - timedelta(days=days), date_to=today)
    return _r(sum(max(r["undeposited"], 0.0) for r in out["rows"]))


# --------------------------------------------------------------------------- forecast


def _monday(day):
    return day - timedelta(days=day.weekday())


def _ar_items(env, company):
    """[(due_date, amount_open, amount_total)] of issued AR invoices."""
    if not _has(env, "fix.ar.invoice"):
        return []
    out = []
    invoices = env["fix.ar.invoice"].search(
        [("company_id", "=", company.id), ("state", "in", ("issued", "paid"))]
    )
    for inv in invoices:
        terms = inv._payment_terms_days() if hasattr(inv, "_payment_terms_days") else 30
        out.append(
            (inv.invoice_date + timedelta(days=terms), inv.amount_residual, inv.total_payable)
        )
    return out


def _ap_items(env, company):
    """[(due_date, open_amount, total)] of vendor bills not yet paid nor queued."""
    if not _has(env, "fix.vendor.invoice"):
        return [], None
    Bill = env["fix.vendor.invoice"]
    due_field = next(
        (f for f in ("date_due", "due_date", "invoice_date_due") if f in Bill._fields), None
    )
    default_terms = int(
        env["ir.config_parameter"].sudo().get_param("cd_cash_position.forecast_ap_terms_days") or 30
    )
    dom = [("company_id", "=", company.id)]
    if "state" in Bill._fields:
        dom.append(("state", "not in", ("draft", "cancelled", "cancel", "rejected")))
    bills = Bill.search(dom)
    queued = {
        p.source_id: p.state
        for p in env["fix.payment.execution"].search(
            [("source_model", "=", "fix.vendor.invoice"), ("source_id", "in", bills.ids)]
        )
    }
    out = []
    for bill in bills:
        due = (
            bill[due_field]
            if due_field and bill[due_field]
            else bill.invoice_date + timedelta(days=default_terms)
        )
        is_paid = queued.get(bill.id) == "executed" or (
            "state" in Bill._fields and bill.state == "paid"
        )
        is_queued = queued.get(bill.id) in ("pending", "sent")
        open_amount = 0.0 if (is_paid or is_queued) else bill.total_payable
        out.append((due, open_amount, bill.total_payable))
    return out, (None if due_field else default_terms)


def cash_forecast(env, date_from=None, date_to=None, weeks=13, trailing=4, **_kw):
    company = _company(env)
    today = fields.Date.context_today(env.user)
    this_week = _monday(today)
    starts = [this_week + timedelta(weeks=i) for i in range(-trailing, weeks)]
    horizon_end = starts[-1] + timedelta(days=6)

    def week_of(day):
        if day < this_week:
            return None
        start = _monday(day)
        return start if start <= starts[-1] else None

    fc = defaultdict(lambda: defaultdict(float))  # week -> bucket -> amount (forward: open docs)
    past = defaultdict(lambda: defaultdict(float))  # week -> bucket -> amount (trailing: due docs)

    def add(day, bucket, open_amount, total_amount):
        if day < this_week and _monday(day) >= starts[0]:
            past[_monday(day)][bucket] += total_amount
        if open_amount <= 0.005:
            return
        wk = week_of(day) if day >= this_week else this_week  # overdue -> this week
        if wk:
            fc[wk][bucket] += open_amount

    for due, open_amt, total in _ar_items(env, company):
        add(due, "ar_in", open_amt, total)
    ap, ap_default = _ap_items(env, company)
    for due, open_amt, total in ap:
        add(due, "ap_out", open_amt, total)
    for pay in env["fix.payment.execution"].search(
        [("company_id", "=", company.id), ("state", "in", ("pending", "prepared", "sent"))]
    ):
        add(pay.value_date or today, "payments_out", pay.amount, pay.amount)
    if _has(env, "fix.payout.run"):
        for run in env["fix.payout.run"].search(
            [
                ("company_id", "=", company.id),
                ("state", "in", ("approved", "executing", "file_generated")),
            ]
        ):
            day = run.approved_date.date() if run.approved_date else today
            add(day, "payouts_out", run.total_payable, run.total_payable)
    for inst in env["fix.facility.repayment"].search(
        [
            ("company_id", "=", company.id),
            ("due_date", ">=", starts[0]),
            ("due_date", "<=", horizon_end),
        ]
    ):
        add(inst.due_date, "debt_out", 0.0 if inst.state == "paid" else inst.total, inst.total)
    for inst in env["fix.facility.repayment"].search(
        [("company_id", "=", company.id), ("due_date", "<", this_week), ("state", "=", "planned")]
    ):
        fc[this_week]["debt_out"] += inst.total
    for b in env["fix.gateway.settlement"].search(
        [
            ("company_id", "=", company.id),
            ("state", "in", ("imported", "exceptions", "matched")),
            ("statement_line_id", "=", False),
        ]
    ):
        add(b.settlement_date, "other_in", b.total_net, b.total_net)
    for item in env["fix.cash.forecast.item"].search([("company_id", "=", company.id)]):
        bucket = "other_in" if item.direction == "inflow" else "recurring_out"
        for day in item.occurrences(starts[0], horizon_end):
            future = day >= today
            add(day, bucket, item.amount if future else 0.0, item.amount)

    liquid = _liquid_journals(env, company).mapped("default_account_id")
    opening = gl_balance(env, liquid, company, date_to=this_week - timedelta(days=1))
    rows = []
    running = opening
    for start in starts:
        end = start + timedelta(days=6)
        trailing_week = end < this_week
        b = past[start] if trailing_week else fc[start]
        inflow = b["ar_in"] + b["other_in"]
        outflow = (
            b["ap_out"] + b["payments_out"] + b["payouts_out"] + b["debt_out"] + b["recurring_out"]
        )
        net = _r(inflow - outflow)
        actual = None
        if start <= today:
            moves = env["account.move.line"]._read_group(
                [
                    ("company_id", "=", company.id),
                    ("account_id", "in", liquid.ids),
                    ("parent_state", "=", "posted"),
                    ("date", ">=", start),
                    ("date", "<=", min(end, today)),
                ],
                [],
                ["balance:sum"],
            )
            actual = _r(moves[0][0]) if moves else 0.0
        if not trailing_week:
            running += net
        rows.append(
            {
                "week": "W%s %s" % (start.isocalendar()[1], "(actual)" if trailing_week else ""),
                "start": str(start),
                "ar_in": _r(b["ar_in"]),
                "other_in": _r(b["other_in"]),
                "ap_out": _r(b["ap_out"]),
                "payments_out": _r(b["payments_out"]),
                "payouts_out": _r(b["payouts_out"]),
                "debt_out": _r(b["debt_out"]),
                "recurring_out": _r(b["recurring_out"]),
                "net": net,
                "actual": actual,
                "variance": _r(actual - net) if actual is not None else None,
                "closing": None if trailing_week else _r(running),
            }
        )
    notes = [
        "Opening liquid balance (bank + cash GL at %s): %s."
        % (this_week - timedelta(days=1), _r(opening)),
        "Trailing %s weeks compare what fell due (forecast) with the posted bank/cash movement (actual); "
        "the next %s weeks project open documents. Overdue items fall into the current week."
        % (trailing, weeks),
        "Sources: AR invoices (due = invoice date + customer terms), vendor bills, payments queued in treasury, "
        "payout runs, loan instalments, gateway settlements awaiting credit, recurring cash items.",
    ]
    if ap_default is not None:
        notes.append(
            "Vendor bills carry no due date yet: assumed invoice date + %s days "
            "(system parameter cd_cash_position.forecast_ap_terms_days)." % ap_default
        )
    return {
        "title": "13-Week Cash Forecast — %s" % company.name,
        "cols": [
            "week",
            "start",
            "ar_in",
            "other_in",
            "ap_out",
            "payments_out",
            "payouts_out",
            "debt_out",
            "recurring_out",
            "net",
            "actual",
            "variance",
            "closing",
        ],
        "labels": {
            "week": "Week",
            "start": "Starts",
            "ar_in": "AR Collections",
            "other_in": "Other Inflows",
            "ap_out": "Vendor Bills",
            "payments_out": "Queued Payments",
            "payouts_out": "Payout Runs",
            "debt_out": "Loan Service",
            "recurring_out": "Recurring Outflows",
            "net": "Net Forecast",
            "actual": "Actual Net",
            "variance": "Variance",
            "closing": "Projected Closing",
        },
        "rows": rows,
        "notes": notes,
    }


# --------------------------------------------------------------------------- bank charges


def bank_charges(env, date_from=None, date_to=None, **_kw):
    company = _company(env)
    d_to = _d(date_to, fields.Date.context_today(env.user))
    d_from = _d(date_from, date(d_to.year, 1, 1))
    buckets = defaultdict(lambda: defaultdict(float))
    account = treasury_account(env, company, "bank_charges", required=False)
    notes = []
    if account:
        for ml in env["account.move.line"].search(
            [
                ("company_id", "=", company.id),
                ("account_id", "=", account.id),
                ("parent_state", "=", "posted"),
                ("date", ">=", d_from),
                ("date", "<=", d_to),
            ]
        ):
            buckets[ml.date.strftime("%Y-%m")]["bank_charges"] += ml.balance
    else:
        notes.append(
            "Bank-charges GL account not configured (cd_cash_position.account_code.bank_charges): "
            "only gateway fees and unbooked charge lines are shown."
        )
    for b in env["fix.gateway.settlement"].search(
        [
            ("company_id", "=", company.id),
            ("state", "=", "posted"),
            ("settlement_date", ">=", d_from),
            ("settlement_date", "<=", d_to),
        ]
    ):
        month = b.settlement_date.strftime("%Y-%m")
        buckets[month]["gateway_fees"] += b.total_fee
        buckets[month]["gateway_vat"] += b.total_fee_vat
    for ln in env["fix.bank.statement.line"].search(
        [
            ("company_id", "=", company.id),
            ("is_bank_charge", "=", True),
            ("charge_move_id", "=", False),
            ("date", ">=", d_from),
            ("date", "<=", d_to),
        ]
    ):
        buckets[ln.date.strftime("%Y-%m")]["unbooked"] += abs(ln.amount)
    rows = []
    for month in sorted(buckets, reverse=True):
        b = buckets[month]
        rows.append(
            {
                "month": month,
                "bank_charges": _r(b["bank_charges"]),
                "gateway_fees": _r(b["gateway_fees"]),
                "gateway_vat": _r(b["gateway_vat"]),
                "unbooked": _r(b["unbooked"]),
                "total": _r(sum(b.values())),
            }
        )
    cols = ["month", "bank_charges", "gateway_fees", "gateway_vat", "unbooked", "total"]
    return {
        "title": "Bank Charges Analysis",
        "cols": cols,
        "labels": {
            "month": "Month",
            "bank_charges": "Bank Charges (GL)",
            "gateway_fees": "Gateway Fees (MDR)",
            "gateway_vat": "VAT on Gateway Fees",
            "unbooked": "Flagged, Not Booked",
            "total": "Total",
        },
        "rows": rows,
        "totals": {"month": "Total", **{c: _r(sum(r[c] for r in rows)) for c in cols[1:]}},
        "notes": notes,
        "empty": "No bank or gateway charges in the period.",
    }


# --------------------------------------------------------------------------- FX


def fx_holdings(env, date_from=None, date_to=None, **_kw):
    company = _company(env)
    today = fields.Date.context_today(env.user)
    ccy = company.currency_id
    rows = []
    for journal in _liquid_journals(env, company, ("bank",)).filtered(
        lambda j: j.currency_id and j.currency_id != ccy
    ):
        account = journal.default_account_id
        groups = env["account.move.line"]._read_group(
            [
                ("account_id", "=", account.id),
                ("parent_state", "=", "posted"),
                ("company_id", "=", company.id),
            ],
            [],
            ["amount_currency:sum", "balance:sum"],
        )
        foreign, book = groups[0] if groups else (0.0, 0.0)
        foreign = foreign or 0.0
        book = book or 0.0
        rate_rec = env["res.currency.rate"].search(
            [
                ("currency_id", "=", journal.currency_id.id),
                ("company_id", "in", (company.id, False)),
            ],
            order="name desc",
            limit=1,
        )
        revalued = journal.currency_id._convert(foreign, ccy, company, today)
        rows.append(
            {
                "account": journal.name,
                "currency": journal.currency_id.name,
                "foreign": _r(foreign),
                "rate": round(revalued / foreign, 4) if foreign else None,
                "rate_date": str(rate_rec.name) if rate_rec else "no rate",
                "book": _r(book),
                "revalued": _r(revalued),
                "unrealised": _r(revalued - book),
            }
        )
    return {
        "title": "FX Holdings — valued at the latest rate",
        "cols": [
            "account",
            "currency",
            "foreign",
            "rate",
            "rate_date",
            "book",
            "revalued",
            "unrealised",
        ],
        "labels": {
            "account": "Bank Account",
            "currency": "Currency",
            "foreign": "Foreign Balance",
            "rate": "BDT per Unit",
            "rate_date": "Rate Date",
            "book": "Book Value (BDT)",
            "revalued": "At Latest Rate (BDT)",
            "unrealised": "Unrealised Gain / (Loss)",
        },
        "rows": rows,
        "totals": {
            "account": "Total",
            "book": _r(sum(r["book"] for r in rows)),
            "revalued": _r(sum(r["revalued"] for r in rows)),
            "unrealised": _r(sum(r["unrealised"] for r in rows)),
        },
        "notes": [
            "Rates come from the currency rate table (Accounting ▸ Currencies); keep them current — "
            "no rate feed is called. The unrealised difference is not posted here."
        ],
        "empty": "No foreign-currency bank accounts (set a currency on a bank journal).",
    }


# --------------------------------------------------------------------------- cheques


def cheque_register(env, date_from=None, date_to=None, **_kw):
    """R8 (CIH capability report, 2026-11-09): the cheque pack — every
    instrument of the register in the period with its lifecycle stamps,
    PDC maturity and stale aging (NI Act 1881 banking practice honours a
    cheque six months), clearing latency (deposit → cleared against the
    BACPS cycle), and the register-vs-GL tie-out of the cheque-in-hand
    account: in-hand value on paper must equal the staging GL balance."""
    company = _company(env)
    today = fields.Date.context_today(env.user)
    d_to = _d(date_to, today)
    d_from = _d(date_from, date(d_to.year, 1, 1))
    stale_after = timedelta(days=182)
    domain = [
        ("company_id", "=", company.id),
        ("received_date", ">=", d_from),
        ("received_date", "<=", d_to),
    ]
    rows = []
    in_hand = 0.0
    pdc_held = 0
    stale_held = 0
    bounced = 0
    for chq in env["fix.cheque"].search(domain, order="received_date desc, id desc"):
        held = chq.state in ("received", "deposited")
        bounced += 1 if chq.state == "bounced" else 0
        if held:
            in_hand += chq.amount
            pdc_held += 1 if chq.is_pdc else 0
            stale_held += 1 if chq.cheque_date < today - stale_after else 0
        latency = None
        if chq.cleared_date and chq.deposited_date:
            latency = (chq.cleared_date - chq.deposited_date).days
        rows.append(
            {
                "cheque_no": chq.cheque_no,
                "party": chq.partner_id.display_name or chq.payee_name or "",
                "drawee_bank": chq.drawee_bank or "",
                "direction": dict(chq._fields["direction"].selection).get(
                    chq.direction, chq.direction
                ),
                "amount": _r(chq.amount),
                "received_date": str(chq.received_date or ""),
                "cheque_date": str(chq.cheque_date or ""),
                "state": dict(chq._fields["state"].selection).get(chq.state, chq.state),
                "pdc": "PDC" if chq.is_pdc else "",
                "stale": "STALE" if chq.cheque_date < today - stale_after else "",
                "cleared_date": str(chq.cleared_date or ""),
                "latency_days": latency,
                "bounces": chq.bounce_count,
            }
        )
    notes = []
    cih = treasury_account(env, company, "cheque_in_hand", required=False)
    if cih:
        gl_cih = gl_balance(env, cih, company, date_to=d_to)
        notes.append(
            "Cheque-in-hand GL %s balance %.2f vs register in-hand %.2f%s."
            % (
                cih.code,
                gl_cih,
                _r(in_hand),
                " — tied out"
                if abs(gl_cih - _r(in_hand)) < 0.005
                else " — DIFFERENCE: reconcile the register against the GL",
            )
        )
    else:
        notes.append(
            "Cheque-in-hand GL not configured (cd_cash_position.account_code."
            "cheque_in_hand): the register-vs-GL tie-out is not shown."
        )
    if pdc_held:
        notes.append("%d post-dated cheque(s) still held before their date." % pdc_held)
    if stale_held:
        notes.append(
            "%d held cheque(s) are past the six-month validity of banking practice "
            "(NI Act 1881) — present or return them; a bank will refuse a stale cheque."
            % stale_held
        )
    if bounced:
        notes.append(
            "%d bounced cheque(s) in the period — NI Act s.138 notice clock applies." % bounced
        )
    cols = [
        "cheque_no",
        "party",
        "drawee_bank",
        "direction",
        "amount",
        "received_date",
        "cheque_date",
        "state",
        "pdc",
        "stale",
        "cleared_date",
        "latency_days",
        "bounces",
    ]
    return {
        "title": "Cheque Register & Cheques-in-Hand",
        "cols": cols,
        "labels": {
            "cheque_no": "Cheque No",
            "party": "Party",
            "drawee_bank": "Drawn On",
            "direction": "Direction",
            "amount": "Amount (BDT)",
            "received_date": "Received",
            "cheque_date": "Cheque Date",
            "state": "State",
            "pdc": "PDC",
            "stale": "Stale",
            "cleared_date": "Cleared",
            "latency_days": "Deposit→Clear (days)",
            "bounces": "Bounces",
        },
        "rows": rows,
        "totals": {
            "cheque_no": "Total",
            "amount": _r(sum(r["amount"] for r in rows)),
            "bounces": sum(r["bounces"] for r in rows),
        },
        "notes": notes,
        "empty": "No cheques received in the period.",
    }


# --------------------------------------------------------------------------- KPIs


def kpis(env):
    company = _company(env)
    bank, drawers, petty, cit, pending = liquid_position(env, company)
    return {
        "cash_position": _r(bank + drawers + petty + cit - pending),
        "branch_cash_uncollected": branch_cash_uncollected(env),
        "payments_awaiting_bank": env["fix.payment.execution"].search_count(
            [("company_id", "=", company.id), ("state", "=", "sent")]
        ),
    }


REPORTS = {
    "daily_cash_position": daily_cash_position,
    "bank_recon_summary": bank_recon_summary,
    "gateway_recon": gateway_recon,
    "cod_report": cod_report,
    "branch_cash": branch_cash,
    "cash_forecast": cash_forecast,
    "bank_charges": bank_charges,
    "fx_holdings": fx_holdings,
    "cheque_register": cheque_register,
}
