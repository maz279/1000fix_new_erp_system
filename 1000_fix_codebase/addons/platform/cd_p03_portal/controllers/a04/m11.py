# A04 · M11 Pricing & Rate Cards — surfaces, report packs and KPIs over the
# real fix.rate.card / fix.dynamic.price.rule / fix.price.explanation /
# fix.discount.approval records and the new price book/version/floor/promotion/
# simulation/policy models. Margin needs a catalogue link; unlinked lines are
# counted, never guessed. Brand reimbursement reads the M09 warranty-claim
# ledger and the OEM invoices raised from it (fix.ar.invoice).
import logging

from odoo import fields, http
from odoo.http import request

from ..p03_service_order_api import _company_domain, _require_internal
from ._scope import scoped

_logger = logging.getLogger(__name__)

SURFACES = {
    # A04 audit (2026-11-04) C3/D2: every M11 surface declared `actions:
    # set()`, so the only way to run a lifecycle from the workspace was to
    # type its state. Each now exposes its transitions; releases are decided
    # from the releaser's M63 inbox, never here.
    "fix.rate.card": {
        "order": "line_type, product_code",
        "limit": 300,
        "actions": {"action_request_release", "action_request_change", "action_request_retire"},
    },
    "fix.dynamic.price.rule": {
        "order": "name",
        "limit": 200,
        "actions": {"action_disable", "action_enable"},
    },
    "fix.price.explanation": {
        "order": "create_date desc, id desc",
        "limit": 300,
        # append-only: the one action re-derives the price, it writes nothing
        "actions": {"action_reconstruct"},
    },
    "fix.discount.approval": {
        "order": "create_date desc, id desc",
        "limit": 300,
        # Approval was possible only by writing state (A03 audit); since R7
        # it is decided from the approver's M63 inbox.
        "actions": {"action_request_approval", "action_recall_approval"},
    },
    "fix.price.book": {
        "order": "name",
        "limit": 200,
        "actions": {"action_retire"},
    },
    "fix.price.version": {
        "order": "book_id, effective_from desc",
        "limit": 200,
        "actions": {"action_submit", "action_recall_approval"},
    },
    "fix.price.floor": {
        "order": "name",
        "limit": 300,
        "actions": {
            "action_request_approval",
            "action_recall_approval",
            "action_request_floor_change",
            "action_request_retire",
        },
    },
    "fix.promotion": {
        "order": "name",
        "limit": 200,
        "actions": {"action_submit", "action_recall_approval", "action_end"},
    },
    "fix.price.simulation": {
        "order": "create_date desc, id desc",
        "limit": 200,
        "actions": {"action_compute"},
    },
    "fix.discount.policy": {
        "order": "min_pct",
        "limit": 200,
        "actions": {"action_submit", "action_recall_approval", "action_retire"},
    },
    # M11 capture audit (2026-11-13): FR-PRC-015, what a brand pays us for
    # warranty work; released by a releaser other than the author (M63).
    "fix.brand.reimbursement.rate": {
        "order": "brand_id, repair_level, valid_from desc",
        "limit": 300,
        "actions": {"action_submit", "action_recall_approval", "action_retire"},
    },
    # A04 audit (2026-11-04) M11-5: the one way a live rate or floor changes.
    "fix.price.change": {
        "order": "id desc",
        "limit": 300,
        "actions": {"action_submit", "action_recall_approval", "action_cancel"},
    },
    # M11 capture pass 2 (2026-11-18): FR-PRC-013 parts schemes, FR-PRC-018/019
    # premiums, FR-PRC-024 mass changes, BRU-PRC-13 discount reason codes.
    "fix.parts.price.scheme": {
        "order": "category_id, brand_id, provenance_grade, valid_from desc",
        "limit": 300,
        "actions": {"action_submit", "action_recall_approval", "action_retire"},
    },
    "fix.parts.price.band": {
        "order": "scheme_id, cost_from",
        "limit": 500,
        "actions": set(),
    },
    "fix.price.adjustment": {
        "order": "adjustment_type, code, valid_from desc",
        "limit": 300,
        "actions": {"action_submit", "action_recall_approval", "action_retire"},
    },
    "fix.price.mass.change": {
        "order": "id desc",
        "limit": 200,
        "actions": {
            "action_preview",
            "action_submit",
            "action_recall_approval",
            "action_cancel",
            "action_rollback",
        },
    },
    # system-written by the preview: read only
    "fix.price.mass.change.line": {
        "order": "change_id desc, product_code",
        "limit": 500,
        "actions": set(),
    },
    "fix.discount.reason": {
        "order": "sequence, code",
        "limit": 200,
        "actions": set(),
    },
    # A04 ERP audit (20 Nov 2026) M11-F7: a below-floor price for one
    # document line, approved from the M63 inbox, used once.
    "fix.price.override": {
        "order": "id desc",
        "limit": 300,
        "actions": {"action_submit", "action_recall_approval"},
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


def _cards(env, date_from=None, date_to=None):
    """Rate cards of the caller's companies (A04 ERP audit M11-F18: every
    pack read every company's cards). A card is a standing record, so the
    period does not filter it."""
    return scoped(env, "fix.rate.card")


def _cost_of(card):
    """The M15 average cost behind the card's item (product.standard_price is
    empty on fix_real and gave a 100% margin), or None when M15 has none."""
    env = card.env
    Card = env["fix.rate.card"]
    variant, _code, _item = Card._price_target(card.catalogue_item_id or card.product_code)
    cost = Card._m15_cost(variant, card.company_id)
    return cost or None


def _realised_lines(env, date_from=None, date_to=None):
    """Sold lines with the released price they were measured against, in the
    period and the caller's companies: M01 estimate lines (card_price) and
    M36 quotation lines (list_price)."""
    out = []
    if "fix.estimate.line" in env and "card_price" in env["fix.estimate.line"]._fields:
        # an estimate line carries no company of its own: fence on its estimate's
        for line in scoped(
            env,
            "fix.estimate.line",
            [("card_price", ">", 0), ("estimate_id.company_id", "in", env.companies.ids)],
            "create_date",
            date_from,
            date_to,
        ):
            out.append(("Estimate", line.estimate_id.display_name, line, line.card_price))
    if "fix.quotation.line" in env:
        for line in scoped(
            env,
            "fix.quotation.line",
            [("price_source", "in", ("rate_card", "manual")), ("list_price", ">", 0)],
            "create_date",
            date_from,
            date_to,
        ):
            out.append(("Quotation", line.quotation_id.display_name, line, line.list_price))
    return out


def realised_vs_card(env, date_from=None, date_to=None, **params):
    rows = []
    for kind, doc, line, card in _realised_lines(env, date_from, date_to):
        final = line.unit_price or 0.0
        variance = final - card
        rows.append(
            {
                "document": "%s %s" % (kind, doc or ""),
                "item": line.product_id.display_name or line.description or "",
                "base": round(card, 2),
                "final": round(final, 2),
                "variance": round(variance, 2),
                "variance_pct": round(variance / card * 100.0, 1) if card else 0.0,
            }
        )
    rows.sort(key=lambda r: r["variance"])
    return _pack(
        "Realised Price vs Card",
        ["document", "item", "base", "final", "variance", "variance_pct"],
        {
            "document": "Document",
            "item": "Item",
            "base": "Released Price",
            "final": "Price Sold At",
            "variance": "Variance",
            "variance_pct": "Variance %",
        },
        rows,
        [
            "Each row is a sold line (M01 estimate, M36 quotation) in the period: the M11 "
            "released price it was measured against and the price it carries. A negative "
            "variance is a discount off the released price."
        ],
        totals={"document": "Total", "variance": round(sum(r["variance"] for r in rows), 2)}
        if rows
        else None,
        empty="No line was sold against a released M11 price in this period.",
    )


def discount_register(env, date_from=None, date_to=None, **params):
    approvals = scoped(env, "fix.discount.approval", None, "create_date", date_from, date_to)
    rows = []
    for a in approvals:
        rows.append(
            {
                "quotation": a.quotation_id.display_name or "—",
                "pct": round(a.discount_pct, 2),
                "state": a.state,
                "approver": a.approved_by.name or "—",
                "reason": (a.reason_code_id.code if "reason_code_id" in a._fields else False)
                or "—",
                "justification": (a.justification or "")[:80],
            }
        )
    rows.sort(key=lambda r: -r["pct"])
    return _pack(
        "Discount Register by Approver",
        ["quotation", "pct", "state", "approver", "reason", "justification"],
        {
            "quotation": "Quotation",
            "pct": "Discount %",
            "state": "State",
            "approver": "Approved By",
            "reason": "Reason Code",
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
    cards = _cards(env).filtered(lambda c: c.state == "released")
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
    cards = _cards(env).filtered(lambda c: c.state == "released")
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
            "Margin = rate − the item's M15 average cost. %d of %d released rate "
            "lines have no M15 cost and are therefore excluded, never guessed."
            % (unlinked, len(cards))
        ],
        empty="No released rate line has an M15 cost yet.",
    )


def promotion_effectiveness(env, date_from=None, date_to=None, **params):
    promos = scoped(env, "fix.promotion")
    if date_from or date_to:
        start = fields.Date.to_date(date_from) if date_from else None
        end = fields.Date.to_date(date_to) if date_to else None
        promos = promos.filtered(
            lambda p: (not end or not p.valid_from or p.valid_from <= end)
            and (not start or not p.valid_until or p.valid_until >= start)
        )
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
                "uses": p.use_count,
                "given": round(p.budget_used or 0.0, 2),
            }
        )
    return _pack(
        "Promotion Effectiveness",
        ["promotion", "code", "discount", "channel", "state", "window", "uses", "given"],
        {
            "promotion": "Promotion",
            "code": "Code",
            "discount": "Discount",
            "channel": "Channel",
            "state": "State",
            "window": "Validity",
            "uses": "Times Used",
            "given": "Discount Given (BDT)",
        },
        rows,
        [
            "Promotions of your companies whose window meets the period, with the uses and "
            "the discount given recorded by the pricing path (fix.promotion.consume)."
        ],
        empty="No promotions configured yet.",
    )


# The M09 claim states (cd_warranty_claims): what the OEM agreed to pay, and
# what it refused. A closed claim is either a settled approval or a rejection
# with no open appeal — the approved amount tells which.
_CLAIM_APPROVED = ("approved", "partially_approved", "remitted")
_CLAIM_SETTLED = ("remitted", "closed")
# An OEM invoice counts as invoiced once finance has issued it; the
# warranty_claim.decided hand-off raises it as a DRAFT (cd_billing_engine).
_INVOICE_ISSUED = ("issued", "paid", "credited", "written_off")
_CLAIM_SOURCE = "fix.warranty.claim"


def _brand_claims(env):
    """The warranty-claim ledger, read as the caller (the M09 operating-unit
    rule applies, as M09's own packs read it) inside the company fence."""
    if _CLAIM_SOURCE not in env:
        return None
    return env["fix.warranty.claim"].search(_company_domain(env, _CLAIM_SOURCE))


def _claim_invoices(env, claims):
    """The OEM invoices raised from those claims only. fix.ar.invoice is a
    finance record a pricing reader may not hold: it is read sudo, fenced to
    the caller's companies and to the claims the caller can already see."""
    if "fix.ar.invoice" not in env or not claims:
        return None
    return (
        env["fix.ar.invoice"]
        .sudo()
        .search(
            [
                *_company_domain(env, "fix.ar.invoice"),
                ("source_model", "=", _CLAIM_SOURCE),
                ("source_id", "in", claims.ids),
                ("state", "!=", "cancelled"),
            ]
        )
    )


def _brand_cards_in_force(env):
    """{brand id: 'L1 1,200.00 (+10% parts) · L2 ...'} from the released brand
    reimbursement rates in force today (BRU-PRC-12)."""
    if "fix.brand.reimbursement.rate" not in env:
        return {}
    Rate = env["fix.brand.reimbursement.rate"]
    today = fields.Date.context_today(env.user)
    rates = Rate.search(
        [
            *_company_domain(env, "fix.brand.reimbursement.rate"),
            ("state", "=", "active"),
            ("valid_from", "<=", today),
        ],
        order="brand_id, repair_level",
    )
    out = {}
    for rate in rates:
        level = (rate.repair_level or "").upper()
        text = f"{level} {rate.labour_rate:,.2f}"
        if rate.parts_markup_pct:
            text += " (+%g%% parts)" % rate.parts_markup_pct
        out[rate.brand_id.id] = (
            "%s · %s" % (out[rate.brand_id.id], text) if rate.brand_id.id in out else text
        )
    return out


def brand_reimbursement(env, date_from=None, date_to=None, **params):
    from odoo.addons.cd_p03_portal.controllers.p03_generic_api import _datetime_to_local

    cols = [
        "brand",
        "raised",
        "approved",
        "rejected",
        "pending",
        "claimed",
        "approved_amount",
        "invoiced",
        "received",
        "recovery_pct",
        "avg_days",
        "last_received",
        "card_in_force",
    ]
    labels = {
        "brand": "Brand",
        "raised": "Claims Raised",
        "approved": "Approved",
        "rejected": "Rejected",
        "pending": "Awaiting Decision",
        "claimed": "Amount Claimed",
        "approved_amount": "Amount Approved",
        "invoiced": "Invoiced to OEM",
        "received": "Received",
        "recovery_pct": "Recovery %",
        "avg_days": "Avg Days to Reimbursement",
        "last_received": "Last Receipt",
        "card_in_force": "Brand Rate Card in Force",
    }
    claims = _brand_claims(env)
    if claims is None:
        return _pack(
            "Brand Reimbursement Recovery",
            cols,
            labels,
            [],
            ["The warranty-claim ledger (cd_warranty_claims) is not installed here."],
            empty="The warranty-claim ledger is not installed.",
        )
    invoices = _claim_invoices(env, claims)
    issued_by_claim = {}
    drafts = 0
    draft_value = 0.0
    for inv in invoices or []:
        if inv.state in _INVOICE_ISSUED:
            issued_by_claim[inv.source_id] = issued_by_claim.get(inv.source_id, 0.0) + (
                inv.total_payable or 0.0
            )
        elif inv.state == "draft":
            drafts += 1
            draft_value += inv.total_payable or 0.0

    by_brand = {}
    for claim in claims:
        brand = claim.brand_id
        row = by_brand.setdefault(
            brand.id if brand else 0,
            {
                "brand": brand.name if brand else "Unassigned",
                "raised": 0,
                "approved": 0,
                "rejected": 0,
                "claimed": 0.0,
                "approved_amount": 0.0,
                "invoiced": 0.0,
                "received": 0.0,
                "days": [],
                "last": None,
            },
        )
        row["raised"] += 1
        row["claimed"] += claim.claim_amount or 0.0
        approved_value = claim.approved_amount or 0.0
        if claim.state in _CLAIM_APPROVED or (claim.state == "closed" and approved_value):
            row["approved"] += 1
        elif claim.state == "rejected" or claim.state == "closed":
            row["rejected"] += 1
        row["approved_amount"] += approved_value
        row["invoiced"] += issued_by_claim.get(claim.id, 0.0)
        row["received"] += claim.remittance_amount or 0.0
        if claim.remitted_at:
            if row["last"] is None or claim.remitted_at > row["last"]:
                row["last"] = claim.remitted_at
            if claim.state in _CLAIM_SETTLED and claim.submitted_at:
                span = claim.remitted_at - claim.submitted_at
                row["days"].append(span.total_seconds() / 86400.0)

    cards = _brand_cards_in_force(env)
    rows = []
    for brand_id, row in by_brand.items():
        days = row["days"]
        rows.append(
            {
                "brand": row["brand"],
                "raised": row["raised"],
                "approved": row["approved"],
                "rejected": row["rejected"],
                "pending": row["raised"] - row["approved"] - row["rejected"],
                "claimed": round(row["claimed"], 2),
                "approved_amount": round(row["approved_amount"], 2),
                "invoiced": round(row["invoiced"], 2),
                "received": round(row["received"], 2),
                "recovery_pct": round(row["received"] / row["claimed"] * 100.0, 1)
                if row["claimed"]
                else 0.0,
                "avg_days": round(sum(days) / len(days), 1) if days else "—",
                "last_received": _datetime_to_local(env, row["last"])[:16] if row["last"] else "—",
                "card_in_force": cards.get(brand_id) or "None recorded",
            }
        )
    rows.sort(key=lambda r: -r["claimed"])
    notes = [
        "One row per brand over the M09 warranty-claim ledger (fix.warranty.claim). "
        "Approved counts full and partial approvals, settled ones included; rejected "
        "counts rejections, closed ones included.",
        "Invoiced is the OEM invoices raised from the claims (fix.ar.invoice, source "
        "fix.warranty.claim) once finance has issued them. %d draft hand-off invoice(s) "
        "worth %.2f await issue and are not counted." % (drafts, draft_value),
        "Received is the bank receipt a Claim Decision Officer recorded on the claim; a "
        "brand's own remittance advice is not money and is not counted. Recovery % = "
        "received ÷ claimed.",
        "Days to reimbursement run from submission to the brand to the last recorded "
        "receipt, over settled claims only; '—' means none is settled yet.",
        "Brand Rate Card in Force is what the brand pays per warranty job at each repair "
        "level today, with the parts handling markup, from the released brand "
        "reimbursement rates (FR-PRC-015). 'None recorded' means no rate is released "
        "for the brand.",
    ]
    totals = None
    if rows:
        totals = {"brand": "Total"}
        for col in ("raised", "approved", "rejected", "pending"):
            totals[col] = sum(r[col] for r in rows)
        for col in ("claimed", "approved_amount", "invoiced", "received"):
            totals[col] = round(sum(r[col] for r in rows), 2)
    return _pack(
        "Brand Reimbursement Recovery",
        cols,
        labels,
        rows,
        notes,
        totals=totals,
        empty="No warranty claim has been raised yet.",
    )


def pricing_engine(env, date_from=None, date_to=None, **params):
    explanations = scoped(env, "fix.price.explanation", None, "create_date", date_from, date_to)
    rules = scoped(env, "fix.dynamic.price.rule")
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
    floors = scoped(env, "fix.price.floor")
    cards = _cards(env).filtered(lambda c: c.state == "released")
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


def _brand_rates_in_force(env):
    if "fix.brand.reimbursement.rate" not in env:
        return None
    return (
        env["fix.brand.reimbursement.rate"]
        .sudo()
        .search_count(
            [
                *_company_domain(env, "fix.brand.reimbursement.rate"),
                ("state", "=", "active"),
                ("valid_from", "<=", fields.Date.context_today(env.user)),
            ]
        )
    )


def kpis(env):
    cards = _cards(env).filtered(lambda c: c.state == "released")
    floors = scoped(env, "fix.price.floor")
    approvals = scoped(env, "fix.discount.approval")
    simulations = scoped(env, "fix.price.simulation")
    breaches = 0
    for floor in floors:
        for card in cards.filtered(lambda c, code=floor.product_code: c.product_code == code):
            if card.unit_price < floor.floor_price:
                breaches += 1
    margins = []
    for card in cards:
        try:
            cost = _cost_of(card)
        except Exception:  # a KPI never breaks the workspace, but says why
            _logger.exception("M11 KPI: cost of rate card %s", card.id)
            continue
        if cost is not None and card.unit_price:
            margins.append((card.unit_price - cost) / card.unit_price * 100.0)
    policies = scoped(env, "fix.discount.policy", [("active", "=", True)])
    max_by_role = {}
    for policy in policies:
        max_by_role[policy.role] = max(max_by_role.get(policy.role, 0.0), policy.max_pct)
    today = fields.Date.context_today(env.user)
    month_start = today.replace(day=1)
    # a count: no discount policy means no band to leak past, so 0, not None
    leaks = 0
    if policies:
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
        # a draft card prices nothing until a releaser releases it (M11-5):
        # counting `active` showed unreleased drafts as live
        "rate_cards_live": len(cards.filtered(lambda c: c.active and c.state == "released")),
        # released brand reimbursement rates in force (FR-PRC-015); a count,
        # so 0 when none is recorded
        "brand_reimb_rates": _brand_rates_in_force(env),
        "simulations_mtd": sims_mtd,
        "margin_floors_breached": breaches,
    }


class P03PricingApi(http.Controller):
    @http.route("/p03/pricing/kpis", type="jsonrpc", auth="user", readonly=True)
    def pricing_kpis(self, module=None, **kw):
        _require_internal(request.env)
        return {"M11": kpis(request.env)}
