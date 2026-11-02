# A04 · M11 Pricing & Rate Cards — surfaces, report packs and KPIs over the
# real fix.rate.card / fix.dynamic.price.rule / fix.price.explanation /
# fix.discount.approval records and the new price book/version/floor/promotion/
# simulation/policy models. Margin needs a catalogue link; unlinked lines are
# counted, never guessed.
import datetime

from odoo import http
from odoo.http import request

from ..p03_service_order_api import _require_internal

SURFACES = {
    "fix.rate.card": {
        "order": "line_type, product_code",
        "limit": 300,
        "actions": set(),
    },
    "fix.dynamic.price.rule": {
        "order": "name",
        "limit": 200,
        "actions": set(),
    },
    "fix.price.explanation": {
        "order": "create_date desc, id desc",
        "limit": 300,
        "actions": set(),
    },
    "fix.discount.approval": {
        "order": "create_date desc, id desc",
        "limit": 300,
        "actions": set(),
    },
    "fix.price.book": {
        "order": "name",
        "limit": 200,
        "actions": set(),
    },
    "fix.price.version": {
        "order": "book_id, effective_from desc",
        "limit": 200,
        "actions": set(),
    },
    "fix.price.floor": {
        "order": "name",
        "limit": 300,
        "actions": set(),
    },
    "fix.promotion": {
        "order": "name",
        "limit": 200,
        "actions": set(),
    },
    "fix.price.simulation": {
        "order": "create_date desc, id desc",
        "limit": 200,
        "actions": set(),
    },
    "fix.discount.policy": {
        "order": "min_pct",
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


def _cards(env):
    return env["fix.rate.card"].sudo().search([])


def _cost_of(card):
    item = card.catalogue_item_id
    if not item or not item.product_tmpl_id:
        return None
    value = getattr(item.product_tmpl_id, "standard_price", None)
    try:
        return float(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def realised_vs_card(env, date_from=None, date_to=None, **params):
    explanations = env["fix.price.explanation"].sudo().search([])
    rows = []
    for exp in explanations:
        base = exp.base_price or 0.0
        final = exp.final_price or 0.0
        variance = final - base
        rows.append(
            {
                "explanation": exp.name,
                "base": round(base, 2),
                "final": round(final, 2),
                "variance": round(variance, 2),
                "variance_pct": round(variance / base * 100.0, 1) if base else 0.0,
                "model_driven": "✓" if exp.model_driven else "✗",
            }
        )
    rows.sort(key=lambda r: -abs(r["variance"]))
    return _pack(
        "Realised Price vs Card",
        ["explanation", "base", "final", "variance", "variance_pct", "model_driven"],
        {
            "explanation": "Price Explanation",
            "base": "Card / Base Price",
            "final": "Final Price",
            "variance": "Variance",
            "variance_pct": "Variance %",
            "model_driven": "Model Driven",
        },
        rows,
        [
            "Each row is a recorded price explanation: the base (card) price against the "
            "final applied price and the variance."
        ],
        totals={"explanation": "Total", "variance": round(sum(r["variance"] for r in rows), 2)}
        if rows
        else None,
        empty="No price explanations recorded yet.",
    )


def discount_register(env, date_from=None, date_to=None, **params):
    approvals = env["fix.discount.approval"].sudo().search([])
    rows = []
    for a in approvals:
        rows.append(
            {
                "quotation": a.quotation_id.display_name or "—",
                "pct": round(a.discount_pct, 2),
                "state": a.state,
                "approver": a.approved_by.name or "—",
                "justification": (a.justification or "")[:80],
            }
        )
    rows.sort(key=lambda r: -r["pct"])
    return _pack(
        "Discount Register by Approver",
        ["quotation", "pct", "state", "approver", "justification"],
        {
            "quotation": "Quotation",
            "pct": "Discount %",
            "state": "State",
            "approver": "Approved By",
            "justification": "Justification",
        },
        rows,
        [
            "Every discount above the policy band needs an approval row with its "
            "justification — the register is the audit trail."
        ],
        empty="No discount approvals recorded yet.",
    )


def rate_card_utilisation(env, date_from=None, date_to=None, **params):
    cards = _cards(env)
    by_type = {}
    for card in cards:
        row = by_type.setdefault(
            card.line_type,
            {
                "type": card.line_type,
                "lines": 0,
                "prices": [],
                "linked": 0,
            },
        )
        row["lines"] += 1
        row["prices"].append(card.unit_price)
        if card.catalogue_item_id:
            row["linked"] += 1
    rows = []
    for row in by_type.values():
        prices = row["prices"]
        rows.append(
            {
                "type": row["type"],
                "lines": row["lines"],
                "avg_price": round(sum(prices) / len(prices), 2) if prices else 0.0,
                "min_price": round(min(prices), 2) if prices else 0.0,
                "max_price": round(max(prices), 2) if prices else 0.0,
                "linked_pct": round(row["linked"] / row["lines"] * 100.0, 1)
                if row["lines"]
                else 0.0,
            }
        )
    rows.sort(key=lambda r: -r["lines"])
    return _pack(
        "Rate-Card Utilisation",
        ["type", "lines", "avg_price", "min_price", "max_price", "linked_pct"],
        {
            "type": "Line Type",
            "lines": "Rate Lines",
            "avg_price": "Average Rate",
            "min_price": "Min Rate",
            "max_price": "Max Rate",
            "linked_pct": "Linked to Catalogue %",
        },
        rows,
        [
            "Linked % is the share of rate lines carrying a catalogue-item link — the "
            "link is what makes margin analysis possible."
        ],
        totals={"type": "Total", "lines": sum(r["lines"] for r in rows)} if rows else None,
        empty="No rate cards yet.",
    )


def margin_by_line(env, date_from=None, date_to=None, **params):
    cards = _cards(env)
    rows = []
    unlinked = 0
    for card in cards:
        cost = _cost_of(card)
        if cost is None:
            unlinked += 1
            continue
        margin = card.unit_price - cost
        rows.append(
            {
                "product": card.product_code,
                "type": card.line_type,
                "price": round(card.unit_price, 2),
                "cost": round(cost, 2),
                "margin": round(margin, 2),
                "margin_pct": round(margin / card.unit_price * 100.0, 1)
                if card.unit_price
                else 0.0,
            }
        )
    rows.sort(key=lambda r: r["margin_pct"])
    return _pack(
        "Margin by Service Line",
        ["product", "type", "price", "cost", "margin", "margin_pct"],
        {
            "product": "Product Code",
            "type": "Line Type",
            "price": "Rate",
            "cost": "Cost",
            "margin": "Margin",
            "margin_pct": "Margin %",
        },
        rows,
        [
            "Margin = rate − the linked catalogue item's standard cost. %d of %d rate "
            "lines have no catalogue link and are therefore excluded, never guessed."
            % (unlinked, len(cards))
        ],
        empty="No rate line has a catalogue link with a cost yet.",
    )


def promotion_effectiveness(env, date_from=None, date_to=None, **params):
    promos = env["fix.promotion"].sudo().search([])
    rows = []
    for p in promos:
        rows.append(
            {
                "promotion": p.name,
                "code": p.code,
                "discount": ("%s%%" % p.value)
                if p.discount_type == "percent"
                else ("৳%s" % p.value),
                "channel": p.channel,
                "state": p.state,
                "window": "%s → %s" % (p.valid_from or "—", p.valid_until or "—"),
            }
        )
    return _pack(
        "Promotion Effectiveness",
        ["promotion", "code", "discount", "channel", "state", "window"],
        {
            "promotion": "Promotion",
            "code": "Code",
            "discount": "Discount",
            "channel": "Channel",
            "state": "State",
            "window": "Validity",
        },
        rows,
        [
            "Redemption/usage telemetry is not modelled — this pack lists the live "
            "promotions and their windows. Effectiveness per redemption is a declared gap."
        ],
        empty="No promotions configured yet.",
    )


def brand_reimbursement(env, date_from=None, date_to=None, **params):
    return _pack(
        "Brand Reimbursement Recovery",
        ["brand", "claims", "claimed", "recovered", "recovery_pct"],
        {
            "brand": "Brand",
            "claims": "Warranty Claims",
            "claimed": "Claimed Value",
            "recovered": "Recovered Value",
            "recovery_pct": "Recovery %",
        },
        [],
        [
            "Brand reimbursement requires the warranty-claim ledger (M08/M40). The "
            "pricing module records brand labour rates but no claim recovery key "
            "exists here — declared gap, nothing estimated."
        ],
        empty="Brand reimbursement tracking needs the warranty-claim ledger (declared gap).",
    )


def pricing_engine(env, date_from=None, date_to=None, **params):
    explanations = env["fix.price.explanation"].sudo().search([])
    rules = env["fix.dynamic.price.rule"].sudo().search([])
    model_driven = len(explanations.filtered(lambda e: e.model_driven))
    variances = [(e.final_price or 0.0) - (e.base_price or 0.0) for e in explanations]
    rows = [
        {
            "metric": "Price explanations",
            "value": len(explanations),
            "basis": "fix.price.explanation",
        },
        {"metric": "Model-driven", "value": model_driven, "basis": "model_driven flag"},
        {
            "metric": "Dynamic rules",
            "value": len(rules),
            "basis": "active=%d" % len(rules.filtered(lambda r: r.active)),
        },
        {
            "metric": "Average variance",
            "value": round(sum(variances) / len(variances), 2) if variances else 0.0,
            "basis": "final − base per explanation",
        },
    ]
    return _pack(
        "Pricing Engine — explanation coverage",
        ["metric", "value", "basis"],
        {"metric": "Measure", "value": "Value", "basis": "Basis"},
        rows,
        [
            "Every applied price must be explainable; model-driven prices carry the "
            "dynamic rule that produced them."
        ],
    )


def floors_vs_rate(env, date_from=None, date_to=None, **params):
    floors = env["fix.price.floor"].sudo().search([])
    cards = _cards(env)
    rows = []
    for floor in floors:
        linked = cards.filtered(lambda c, code=floor.product_code: c.product_code == code)
        for card in linked:
            breach = card.unit_price < floor.floor_price
            rows.append(
                {
                    "product": floor.product_code,
                    "floor": round(floor.floor_price, 2),
                    "rate": round(card.unit_price, 2),
                    "delta": round(card.unit_price - floor.floor_price, 2),
                    "breach": "✗ FLOOR" if breach else "✓",
                }
            )
    rows.sort(key=lambda r: r["delta"])
    return _pack(
        "Price Floors vs Rate Cards",
        ["product", "floor", "rate", "delta", "breach"],
        {
            "product": "Product Code",
            "floor": "Floor Price",
            "rate": "Rate",
            "delta": "Rate − Floor",
            "breach": "Below Floor?",
        },
        rows,
        ["Any rate below its floor is flagged — the quote engine must refuse it."],
        empty="No floor is matched by a rate-card line yet.",
    )


REPORTS = {
    "realised_vs_card": realised_vs_card,
    "discount_register": discount_register,
    "rate_card_utilisation": rate_card_utilisation,
    "margin_by_line": margin_by_line,
    "promotion_effectiveness": promotion_effectiveness,
    "brand_reimbursement": brand_reimbursement,
    "pricing_engine": pricing_engine,
    "floors_vs_rate": floors_vs_rate,
}


def kpis(env):
    cards = _cards(env)
    floors = env["fix.price.floor"].sudo().search([])
    approvals = env["fix.discount.approval"].sudo().search([])
    simulations = env["fix.price.simulation"].sudo().search([])
    breaches = 0
    for floor in floors:
        for card in cards.filtered(lambda c, code=floor.product_code: c.product_code == code):
            if card.unit_price < floor.floor_price:
                breaches += 1
    margins = []
    for card in cards:
        cost = _cost_of(card)
        if cost is not None and card.unit_price:
            margins.append((card.unit_price - cost) / card.unit_price * 100.0)
    policies = env["fix.discount.policy"].sudo().search([("active", "=", True)])
    max_by_role = {}
    for policy in policies:
        max_by_role[policy.role] = max(max_by_role.get(policy.role, 0.0), policy.max_pct)
    today = datetime.date.today()
    month_start = today.replace(day=1)
    leaks = None
    if policies:
        leaks = 0
        for approval in approvals.filtered(
            lambda a: a.create_date and a.create_date.date() >= month_start
        ):
            band = max_by_role.get("agent", 0.0)
            if approval.discount_pct > band:
                leaks += 1
    sims_mtd = len(
        simulations.filtered(lambda s: s.create_date and s.create_date.date() >= month_start)
    )
    return {
        "realised_margin": round(sum(margins) / len(margins), 1) if margins else None,
        "discount_leaks_mtd": leaks,
        "rate_cards_live": len(cards.filtered(lambda c: c.active)),
        "brand_reimb_rates": None,  # brand-claim ledger not linked (declared gap)
        "simulations_mtd": sims_mtd,
        "margin_floors_breached": breaches,
    }


class P03PricingApi(http.Controller):
    @http.route("/p03/pricing/kpis", type="jsonrpc", auth="user", readonly=True)
    def pricing_kpis(self, module=None, **kw):
        _require_internal(request.env)
        return {"M11": kpis(request.env)}
