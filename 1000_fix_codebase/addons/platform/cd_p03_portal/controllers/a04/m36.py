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
    "fix.quotation": {
        "order": "create_date desc, id desc",
        "limit": 300,
        "actions": set(),
    },
    "fix.quote.review": {
        "order": "reviewed_at desc, id desc",
        "limit": 300,
        "actions": set(),
    },
    "fix.tender": {
        "order": "due_date, id",
        "limit": 200,
        "actions": set(),
    },
    "fix.tender.bond": {
        "order": "expires_on, id",
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
    quotes = _quotes(env)
    states = ["draft", "sent", "accepted", "declined", "expired"]
    rows = []
    for state in states:
        mine = quotes.filtered(lambda q, s=state: q.state == s)
        rows.append(
            {"state": state, "quotes": len(mine), "value": round(sum(mine.mapped("value")), 2)}
        )
    total = len(quotes)
    accepted = len(quotes.filtered(lambda q: q.state == "accepted"))
    return _pack(
        "Quote Conversion by Channel",
        ["state", "quotes", "value"],
        {"state": "State", "quotes": "Quotations", "value": "Value"},
        rows,
        [
            "Conversion = accepted / all quotations: %d of %d (%.1f%%)."
            % (accepted, total, accepted / total * 100.0 if total else 0.0)
        ],
        totals={"state": "Total", "quotes": total, "value": round(sum(quotes.mapped("value")), 2)}
        if rows
        else None,
        empty="No quotations yet.",
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
    states = ["draft", "submitted", "won", "lost", "cancelled"]
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
    return _pack(
        "Tender Win/Loss",
        ["state", "tenders", "value"],
        {"state": "State", "tenders": "Tenders", "value": "Estimated Value"},
        rows,
        [
            "Win rate = won / (won + lost): %d of %d decided (%.1f%%)."
            % (won, decided, won / decided * 100.0 if decided else 0.0)
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
    margins = [r["margin_pct"] for r in rows if r["margin_pct"]]
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
            "Margin is the value recorded on the quotation at approval time. "
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
        "quotes_open": len(quotes.filtered(lambda q: q.state in ("draft", "sent"))),
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
