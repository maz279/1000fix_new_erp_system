# A04 · M36 Quotations & Tenders — surfaces, report packs and KPIs over the
# real fix.estimate (+lines) / fix.counter.sale and the new quotation, review,
# tender and bond models. Conversion and win rates are measured; no revenue is
# inferred from an estimate's success.

from odoo import http
from odoo.http import request

from ..p03_service_order_api import _require_internal

SURFACES = {
    # fix.estimate is owned by M01 (a02) and fix.counter.sale by M04 (a02) —
    # single owner each; this module reads them through the merged registry.
    "fix.estimate.line": {
        "order": "estimate_id, id",
        "limit": 300,
        "actions": set(),
    },
    # A04 workflow audit (2026-11-03) D2: every M36 surface declared
    # `actions: set()`, so the only workspace path was typing state. The
    # lifecycles now run through these, under each model's own checks.
    "fix.quotation": {
        "order": "create_date desc, id desc",
        "limit": 300,
        "actions": {
            "action_pull_estimate_lines",
            "action_record_advance",
            "action_apply_template",
            "action_choose_option",
            "action_submit",
            "action_recall_approval",
            "action_send",
            "action_issue_on_channel",
            "action_send_acceptance_otp",
            "action_verify_acceptance_otp",
            "action_record_signed_acceptance",
            "action_decline",
            "action_cancel",
            "action_revise",
            "action_convert",
            "action_create_proforma",
            "action_fix_print",
            "action_fix_print_receipt",
            # capture pass 2 (19 Nov 2026)
            "action_apply_standard_terms",
            "action_record_phone_acceptance",
        },
    },
    # Commercial document standard (17 Nov 2026): the customer's local proforma.
    "fix.sales.proforma": {
        "order": "date desc, id desc",
        "limit": 300,
        "actions": {
            "action_issue",
            "action_convert_to_invoice",
            "action_cancel",
            "action_reset_draft",
            "action_fix_print",
            "action_fix_print_receipt",
        },
    },
    # P2 (12-13 Nov 2026): the billing plan, the hand-off log and contract scope.
    "fix.quotation.billing.line": {
        "order": "quotation_id desc, sequence, id",
        "limit": 300,
        "actions": {"action_invoice"},
    },
    "fix.quotation.handoff": {
        "order": "id desc",
        "limit": 300,
        "actions": set(),
    },
    # Capture audit (2026-11-14): the customer side of the loop - every
    # delivery of an issued version on its channel, and the customer's
    # counter-offer / partial acceptance with its decision.
    "fix.quotation.delivery": {
        "order": "sent_at desc, id desc",
        "limit": 300,
        "actions": set(),
    },
    "fix.quotation.counter": {
        "order": "id desc",
        "limit": 300,
        "actions": {"action_decide"},
    },
    "fix.quotation.counter.line": {
        "order": "counter_id, sequence, id",
        "limit": 500,
        "actions": set(),
    },
    "fix.quotation.template": {
        "order": "sequence, name",
        "limit": 200,
        "actions": set(),
    },
    "fix.contract.scope.line": {
        "order": "contract_id desc, id",
        "limit": 300,
        "actions": set(),
    },
    # Written only by the approval engine's decision (append-only log).
    "fix.quote.review": {
        "order": "reviewed_at desc, id desc",
        "limit": 300,
        "actions": set(),
    },
    "fix.tender": {
        "order": "due_date, id",
        "limit": 200,
        "actions": {
            "action_decide_bid",
            "action_decide_no_bid",
            "action_submit",
            "action_request_award",
            "action_recall_approval",
            "action_record_outcome",
            # a loss is recorded with its governed reason on fix.tender.outcome
            # (capture pass 2): the free-text Record Loss is not served
            "action_cancel",
            "action_create_contract",
            # quote-to-cash, tender part (13 Nov 2026): BOQ, pricing, acceptance
            "action_import_boq",
            "action_price_as_quotation",
            "action_record_acceptance",
        },
    },
    # Variation orders on an awarded tender (report §6 P2 M36, variation cap).
    "fix.tender.variation": {
        "order": "tender_id, id",
        "limit": 200,
        "actions": {"action_request", "action_recall_approval", "action_cancel"},
    },
    "fix.tender.bond": {
        "order": "expires_on, id",
        "limit": 200,
        "actions": {
            "action_activate",
            "action_release",
            "action_claim",
            "action_extend",
            "action_recall_approval",
        },
    },
    # Capture audit, second pass (2026-11-19): the spec records the pages
    # are about that had nowhere to be captured.
    "fix.quotation.standard.term": {
        "order": "quote_type, term_type, sequence, id",
        "limit": 300,
        "actions": set(),
    },
    "fix.quotation.term": {
        "order": "quotation_id desc, term_type, sequence, id",
        "limit": 300,
        "actions": {"action_decide_deviation"},
    },
    "fix.quotation.credit.override": {
        "order": "id desc",
        "limit": 200,
        "actions": {"action_revoke"},
    },
    "fix.quotation.legal.hold": {
        "order": "id desc",
        "limit": 200,
        "actions": {"action_release"},
    },
    "fix.estimate.review": {
        "order": "id desc",
        "limit": 200,
        "actions": {"action_decide"},
    },
    "fix.tender.document": {
        "order": "tender_id desc, sequence, id",
        "limit": 300,
        "actions": set(),
    },
    "fix.tender.outcome": {
        "order": "id desc",
        "limit": 200,
        "actions": set(),
    },
}


def _pack(title, cols, labels, rows, notes, totals=None, empty=None):
    return {
        "title": title,
        "cols": cols,
        "labels": labels,
        "rows": rows,
        "totals": totals,
        "notes": notes,
        "empty": empty or "No data in this basis yet.",
    }


def _quotes(env):
    return env["fix.quotation"].sudo().search([])


def quote_conversion(env, date_from=None, date_to=None, **params):
    """FR-QTE-033/039: conversion by the channel each quotation first reached
    the customer on (its first recorded delivery). Superseded versions are
    left out: the version that replaced one carries the decision."""
    quotes = _quotes(env).filtered(lambda q: q.state in ("sent", "accepted", "declined", "expired"))
    labels = dict(env["fix.quotation.delivery"]._fields["channel"].selection)
    buckets = {}
    for quote in quotes:
        key = quote.delivery_channel or "none"
        row = buckets.setdefault(
            key,
            {
                "channel": labels.get(key, "No delivery recorded"),
                "issued": 0,
                "viewed": 0,
                "accepted": 0,
                "declined": 0,
                "expired": 0,
                "open": 0,
                "value": 0.0,
            },
        )
        row["issued"] += 1
        row["viewed"] += 1 if quote.first_viewed_at else 0
        row[
            {"accepted": "accepted", "declined": "declined", "expired": "expired"}.get(
                quote.state, "open"
            )
        ] += 1
        row["value"] += quote.value or 0.0
    rows = []
    order = [k for k, _l in env["fix.quotation.delivery"]._fields["channel"].selection] + ["none"]
    for key in order:
        row = buckets.get(key)
        if not row:
            continue
        decided = row["accepted"] + row["declined"] + row["expired"]
        row["conversion_pct"] = round(row["accepted"] / decided * 100.0, 1) if decided else 0.0
        row["value"] = round(row["value"], 2)
        rows.append(row)
    accepted = sum(r["accepted"] for r in rows)
    decided = sum(r["accepted"] + r["declined"] + r["expired"] for r in rows)
    return _pack(
        "Quote Conversion by Channel",
        [
            "channel",
            "issued",
            "viewed",
            "accepted",
            "declined",
            "expired",
            "open",
            "conversion_pct",
            "value",
        ],
        {
            "channel": "First Delivered By",
            "issued": "Issued",
            "viewed": "Viewed",
            "accepted": "Accepted",
            "declined": "Declined",
            "expired": "Expired",
            "open": "With Customer",
            "conversion_pct": "Conversion %",
            "value": "Value (excl. VAT)",
        },
        rows,
        [
            "Conversion = accepted / decided (accepted, declined or expired): %d of %d "
            "(%.1f%%). The channel is the first delivery recorded on the quotation."
            % (accepted, decided, accepted / decided * 100.0 if decided else 0.0)
        ],
        totals={
            "channel": "Total",
            "issued": sum(r["issued"] for r in rows),
            "accepted": accepted,
            "value": round(sum(r["value"] for r in rows), 2),
        }
        if rows
        else None,
        empty="No quotation has been issued yet.",
    )


def approval_cycle(env, date_from=None, date_to=None, **params):
    reviews = env["fix.quote.review"].sudo().search([])
    by_quote = {}
    for review in reviews:
        row = by_quote.setdefault(
            review.quotation_id.id,
            {
                "quotation": review.quotation_id.name,
                "reviews": 0,
                "decisions": [],
                "first": review.reviewed_at,
                "last": review.reviewed_at,
            },
        )
        row["reviews"] += 1
        row["decisions"].append(review.decision or "")
        if review.reviewed_at and (not row["first"] or review.reviewed_at < row["first"]):
            row["first"] = review.reviewed_at
        if review.reviewed_at and (not row["last"] or review.reviewed_at > row["last"]):
            row["last"] = review.reviewed_at
    rows = []
    for row in by_quote.values():
        hours = None
        if row["first"] and row["last"]:
            hours = round((row["last"] - row["first"]).total_seconds() / 3600.0, 1)
        rows.append(
            {
                "quotation": row["quotation"],
                "reviews": row["reviews"],
                "decision": row["decisions"][-1] if row["decisions"] else "",
                "cycle_hours": hours if hours is not None else 0.0,
            }
        )
    rows.sort(key=lambda r: -r["cycle_hours"])
    return _pack(
        "Approval Cycle Time",
        ["quotation", "reviews", "decision", "cycle_hours"],
        {
            "quotation": "Quotation",
            "reviews": "Reviews",
            "decision": "Last Decision",
            "cycle_hours": "Cycle (hours)",
        },
        rows,
        [
            "Cycle = last minus first review timestamp. A single review has a zero "
            "cycle by definition."
        ],
        empty="No quotation reviews recorded yet.",
    )


def decline_pareto(env, date_from=None, date_to=None, **params):
    quotes = _quotes(env).filtered(lambda q: q.state == "declined")
    reasons = {}
    for quote in quotes:
        key = (quote.decline_reason or "unspecified").strip() or "unspecified"
        reasons[key] = reasons.get(key, 0) + 1
    total = len(quotes)
    rows = []
    cumulative = 0
    for reason, count in sorted(reasons.items(), key=lambda kv: -kv[1]):
        cumulative += count
        rows.append(
            {
                "reason": reason,
                "quotes": count,
                "share_pct": round(count / total * 100.0, 1) if total else 0.0,
                "cumulative_pct": round(cumulative / total * 100.0, 1) if total else 0.0,
            }
        )
    return _pack(
        "Decline Reasons Pareto",
        ["reason", "quotes", "share_pct", "cumulative_pct"],
        {
            "reason": "Decline Reason",
            "quotes": "Quotations",
            "share_pct": "Share %",
            "cumulative_pct": "Cumulative %",
        },
        rows,
        ["Reasons are recorded on the quotation when it is declined."],
        totals={"reason": "Total", "quotes": total} if rows else None,
        empty="No declined quotations yet.",
    )


def tender_winloss(env, date_from=None, date_to=None, **params):
    tenders = env["fix.tender"].sudo().search([])
    states = ["draft", "no_bid", "submitted", "won", "lost", "cancelled"]
    rows = []
    for state in states:
        mine = tenders.filtered(lambda t, s=state: t.state == s)
        rows.append(
            {
                "state": state,
                "tenders": len(mine),
                "value": round(sum(mine.mapped("estimated_value")), 2),
            }
        )
    decided = len(tenders.filtered(lambda t: t.state in ("won", "lost")))
    won = len(tenders.filtered(lambda t: t.state == "won"))
    # FR-QTE-048: the governed loss reasons (Record a Tender Outcome)
    reasons = dict(env["fix.tender"]._fields["loss_reason_code"].selection)
    lost = tenders.filtered(lambda t: t.state in ("lost", "cancelled") and t.loss_reason_code)
    by_reason = {}
    for tender in lost:
        by_reason[tender.loss_reason_code] = by_reason.get(tender.loss_reason_code, 0) + 1
    reason_note = (
        "Loss reasons: "
        + ", ".join(
            "%s %d" % (reasons.get(code, code), n)
            for code, n in sorted(by_reason.items(), key=lambda kv: -kv[1])
        )
        + "."
        if by_reason
        else "No loss reason recorded yet."
    )
    return _pack(
        "Tender Win/Loss",
        ["state", "tenders", "value"],
        {"state": "State", "tenders": "Tenders", "value": "Estimated Value"},
        rows,
        [
            "Win rate = won / (won + lost): %d of %d decided (%.1f%%)."
            % (won, decided, won / decided * 100.0 if decided else 0.0),
            reason_note,
        ],
        totals={
            "state": "Total",
            "tenders": len(tenders),
            "value": round(sum(tenders.mapped("estimated_value")), 2),
        }
        if rows
        else None,
        empty="No tenders yet.",
    )


def margin_approved(env, date_from=None, date_to=None, **params):
    quotes = _quotes(env).filtered(lambda q: q.state == "accepted")
    rows = []
    for quote in quotes:
        rows.append(
            {
                "quotation": quote.name,
                "customer": quote.customer_id.name or "—",
                "value": round(quote.value, 2),
                "margin_pct": round(quote.margin_pct, 1),
                "signed": "✓" if quote.esign_state == "signed" else "✗",
            }
        )
    rows.sort(key=lambda r: r["margin_pct"])
    # A quote with no recorded cost has an unknown margin, not 0% or 100%.
    margins = [round(q.margin_pct, 1) for q in quotes if q.margin_known]
    return _pack(
        "Margin on Approved Quotes",
        ["quotation", "customer", "value", "margin_pct", "signed"],
        {
            "quotation": "Quotation",
            "customer": "Customer",
            "value": "Value",
            "margin_pct": "Margin %",
            "signed": "E-Signed",
        },
        rows,
        [
            "Margin is computed from the quotation's value and recorded direct cost. "
            "Average margin: %.1f%%." % (sum(margins) / len(margins))
            if margins
            else "No accepted quotation carries a margin yet."
        ],
        totals={"quotation": "Total", "value": round(sum(r["value"] for r in rows), 2)}
        if rows
        else None,
        empty="No accepted quotations yet.",
    )


def esign_status(env, date_from=None, date_to=None, **params):
    quotes = _quotes(env)
    rows = []
    for quote in quotes:
        rows.append(
            {
                "quotation": quote.name,
                "state": quote.state,
                "esign": quote.esign_state,
                "signed_at": quote.signed_at.strftime("%Y-%m-%d %H:%M") if quote.signed_at else "—",
                "valid_until": str(quote.valid_until) if quote.valid_until else "—",
            }
        )
    return _pack(
        "E-Signature Status",
        ["quotation", "state", "esign", "signed_at", "valid_until"],
        {
            "quotation": "Quotation",
            "state": "State",
            "esign": "E-Sign State",
            "signed_at": "Signed At",
            "valid_until": "Valid Until",
        },
        rows,
        [
            "Signature state is recorded on the quotation; the signing provider is the "
            "e-signature integration (M24)."
        ],
        empty="No quotations yet.",
    )


def tender_compliance(env, date_from=None, date_to=None, **params):
    tenders = env["fix.tender"].sudo().search([])
    bonds = env["fix.tender.bond"].sudo().search([])
    rows = []
    for tender in tenders:
        mine = bonds.filtered(lambda b, tid=tender.id: b.tender_id.id == tid)
        rows.append(
            {
                "tender": tender.name,
                "client": tender.client_name,
                "due": str(tender.due_date),
                "compliance_pct": tender.compliance_pct,
                "bonds": len(mine),
                "bond_value": round(sum(mine.mapped("amount")), 2),
                "state": tender.state,
            }
        )
    rows.sort(key=lambda r: -r["compliance_pct"])
    return _pack(
        "Tender Compliance & Bonds",
        ["tender", "client", "due", "compliance_pct", "bonds", "bond_value", "state"],
        {
            "tender": "Tender",
            "client": "Client",
            "due": "Due Date",
            "compliance_pct": "Compliance %",
            "bonds": "Bonds",
            "bond_value": "Bond Value",
            "state": "State",
        },
        rows,
        [
            "Compliance % is the recorded bid compliance; bonds are the actual bond "
            "records attached to the tender."
        ],
        empty="No tenders yet.",
    )


REPORTS = {
    "quote_conversion": quote_conversion,
    "approval_cycle": approval_cycle,
    "decline_pareto": decline_pareto,
    "tender_winloss": tender_winloss,
    "margin_approved": margin_approved,
    "esign_status": esign_status,
    "tender_compliance": tender_compliance,
}


def kpis(env):
    quotes = _quotes(env)
    tenders = env["fix.tender"].sudo().search([])
    reviews = env["fix.quote.review"].sudo().search([])
    accepted = len(quotes.filtered(lambda q: q.state == "accepted"))
    by_quote = {}
    for review in reviews:
        row = by_quote.setdefault(review.quotation_id.id, [])
        row.append(review.reviewed_at)
    cycles = []
    for stamps in by_quote.values():
        stamps = [s for s in stamps if s]
        if len(stamps) >= 2:
            cycles.append((max(stamps) - min(stamps)).total_seconds() / 3600.0)
    return {
        "quotes_open": len(quotes.filtered(lambda q: q.state in ("draft", "approved", "sent"))),
        "conversion": round(accepted / len(quotes) * 100.0, 1) if quotes else None,
        "awaiting_customer": len(quotes.filtered(lambda q: q.state == "sent")),
        "avg_turnaround": round(sum(cycles) / len(cycles), 1) if cycles else None,
        "tenders_live": len(tenders.filtered(lambda t: t.state in ("draft", "submitted"))),
        "declined_conversion": None,  # the diagnostic-fee conversion is not modelled
    }


class P03QuoteApi(http.Controller):
    @http.route("/p03/quote/kpis", type="jsonrpc", auth="user", readonly=True)
    def quote_kpis(self, module=None, **kw):
        _require_internal(request.env)
        return {"M36": kpis(request.env)}
