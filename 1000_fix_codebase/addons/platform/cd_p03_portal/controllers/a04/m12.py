# A04 · M12 Marketplace & Sellers — surfaces, report packs and KPIs over the
# real seller (2061) / order (2150) / quote / score / statement / dispute
# records and the new listing model. Fill rates and commissions are measured;
# seller NPS (no survey key on sellers) is a declared gap.
import datetime

from odoo import http
from odoo.http import request

from ..p03_service_order_api import _require_internal

SURFACES = {
    "fix.marketplace.seller": {
        "order": "tier, name",
        "limit": 300,
        "actions": set(),
    },
    "fix.marketplace.listing": {
        "order": "name",
        "limit": 300,
        "actions": set(),
    },
    "fix.marketplace.dispute": {
        "order": "create_date desc, id desc",
        "limit": 300,
        "actions": set(),
    },
    "fix.seller.quote": {
        "order": "create_date desc, id desc",
        "limit": 300,
        "actions": set(),
    },
    "fix.seller.score": {
        "order": "period desc, id desc",
        "limit": 300,
        "actions": set(),
    },
    # fix.seller.statement and fix.payout.run are owned by M53 (a08 surface).
    "fix.marketplace.order": {"order": "id desc", "limit": 400, "actions": set()},
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


def _sellers(env):
    return env["fix.marketplace.seller"].sudo().search([])


def seller_liquidity(env, date_from=None, date_to=None, **params):
    sellers = _sellers(env)
    listings = env["fix.marketplace.listing"].sudo().search([])
    by_tier = {}
    for seller in sellers:
        row = by_tier.setdefault(
            seller.tier or "unspecified",
            {
                "tier": seller.tier or "unspecified",
                "sellers": 0,
                "active": 0,
                "listings": 0,
                "jobs": 0,
            },
        )
        row["sellers"] += 1
        if seller.active:
            row["active"] += 1
        row["listings"] += len(listings.filtered(lambda ln, sid=seller.id: ln.seller_id.id == sid))
        row["jobs"] += seller.total_jobs or 0
    rows = [by_tier[k] for k in by_tier]
    rows.sort(key=lambda r: -r["sellers"])
    return _pack(
        "Supply-Demand Liquidity",
        ["tier", "sellers", "active", "listings", "jobs"],
        {
            "tier": "Tier",
            "sellers": "Sellers",
            "active": "Active",
            "listings": "Listings",
            "jobs": "Jobs Done",
        },
        rows,
        ["Liquidity by seller tier: active supply and the listings/jobs it carries."],
        totals={
            "tier": "Total",
            "sellers": len(sellers),
            "active": sum(r["active"] for r in rows),
            "listings": sum(r["listings"] for r in rows),
        }
        if rows
        else None,
        empty="No marketplace sellers yet.",
    )


def scorecard_distribution(env, date_from=None, date_to=None, **params):
    scores = env["fix.seller.score"].sudo().search([])
    bands = {"0-40": 0, "40-60": 0, "60-80": 0, "80-100": 0}
    rows_by_seller = {}
    for score in scores:
        value = score.composite or 0.0
        if value < 40:
            bands["0-40"] += 1
        elif value < 60:
            bands["40-60"] += 1
        elif value < 80:
            bands["60-80"] += 1
        else:
            bands["80-100"] += 1
        rows_by_seller.setdefault(
            score.seller_id.id,
            {
                "seller": score.seller_id.name,
                "composite": value,
                "acceptance": score.acceptance_rate or 0.0,
                "on_time": score.on_time_rate or 0.0,
                "dispute": score.dispute_rate or 0.0,
            },
        )
    rows = []
    for band, count in bands.items():
        rows.append({"band": band, "sellers": count})
    detail = sorted(rows_by_seller.values(), key=lambda r: -r["composite"])[:50]
    return _pack(
        "Seller Scorecard Distribution",
        ["band", "sellers"],
        {"band": "Composite Score Band", "sellers": "Sellers"},
        rows,
        [
            "Score bands from the measured composite. Top sellers: %s."
            % (", ".join("%s (%.1f)" % (r["seller"], r["composite"]) for r in detail[:5]) or "none")
        ],
        totals={"band": "Total", "sellers": sum(r["sellers"] for r in rows)} if rows else None,
        empty="No seller scorecards yet.",
    )


def fill_rate(env, date_from=None, date_to=None, **params):
    scores = env["fix.seller.score"].sudo().search([])
    quotes = env["fix.seller.quote"].sudo().search([])
    by_state = {}
    for quote in quotes:
        by_state[quote.state] = by_state.get(quote.state, 0) + 1
    decided = sum(s.quotes_decided or 0 for s in scores)
    awarded = sum(s.orders_awarded or 0 for s in scores)
    rows = [{"state": k, "quotes": v} for k, v in sorted(by_state.items(), key=lambda kv: -kv[1])]
    return _pack(
        "Fill Rate & Time-to-Accept",
        ["state", "quotes"],
        {"state": "Quote State", "quotes": "Quotes"},
        rows,
        [
            "Fill rate = orders_awarded / quotes_decided across scorecards: %d of %d "
            "(%.1f%%)." % (awarded, decided, awarded / decided * 100.0 if decided else 0.0)
        ],
        totals={"state": "Total", "quotes": len(quotes)} if rows else None,
        empty="No seller quotes yet.",
    )


def commission_revenue(env, date_from=None, date_to=None, **params):
    statements = env["fix.seller.statement"].sudo().search([])
    by_period = {}
    for st in statements:
        row = by_period.setdefault(
            st.period or "undated",
            {
                "period": st.period or "undated",
                "statements": 0,
                "gmv": 0.0,
                "commission": 0.0,
                "platform_fee": 0.0,
            },
        )
        row["statements"] += 1
        row["gmv"] += st.gross_gmv or 0.0
        row["commission"] += st.commission_amount or 0.0
        row["platform_fee"] += st.platform_fee or 0.0
    rows = [by_period[k] for k in sorted(by_period, reverse=True)]
    for row in rows:
        for key in ("gmv", "commission", "platform_fee"):
            row[key] = round(row[key], 2)
    return _pack(
        "Commission Revenue",
        ["period", "statements", "gmv", "commission", "platform_fee"],
        {
            "period": "Period",
            "statements": "Statements",
            "gmv": "GMV",
            "commission": "Commission",
            "platform_fee": "Platform Fee",
        },
        rows,
        ["Commission and platform fees are the statement's own recorded amounts."],
        totals={
            "period": "Total",
            "statements": len(statements),
            "gmv": round(sum(r["gmv"] for r in rows), 2),
            "commission": round(sum(r["commission"] for r in rows), 2),
            "platform_fee": round(sum(r["platform_fee"] for r in rows), 2),
        }
        if rows
        else None,
        empty="No seller statements yet.",
    )


def dispute_rate(env, date_from=None, date_to=None, **params):
    disputes = env["fix.marketplace.dispute"].sudo().search([])
    orders = env["fix.marketplace.order"].sudo().search_count([])
    by_state = {}
    for dispute in disputes:
        by_state[dispute.state] = by_state.get(dispute.state, 0) + 1
    rows = [{"state": k, "disputes": v} for k, v in sorted(by_state.items(), key=lambda kv: -kv[1])]
    return _pack(
        "Dispute Rate & Outcomes",
        ["state", "disputes"],
        {"state": "Dispute State", "disputes": "Disputes"},
        rows,
        [
            "Dispute rate = disputes / marketplace orders: %d / %d (%.2f%%)."
            % (len(disputes), orders, len(disputes) / orders * 100.0 if orders else 0.0)
        ],
        totals={"state": "Total", "disputes": len(disputes)} if rows else None,
        empty="No disputes recorded.",
    )


def kyc_queue(env, date_from=None, date_to=None, **params):
    sellers = _sellers(env)
    rows = []
    for seller in sellers.filtered(lambda s: s.kyc_status != "verified"):
        rows.append(
            {
                "seller": seller.name,
                "kyc": seller.kyc_status,
                "mode": seller.kyc_review_mode,
                "submitted": str(seller.kyc_submission_date) if seller.kyc_submission_date else "—",
                "nid": seller.nid_number or "—",
                "tin": seller.tin_number or "—",
                "trade_license": seller.trade_license_no or "—",
            }
        )
    return _pack(
        "KYC & Approval",
        ["seller", "kyc", "mode", "submitted", "nid", "tin", "trade_license"],
        {
            "seller": "Seller",
            "kyc": "KYC Status",
            "mode": "Review Mode",
            "submitted": "Submitted",
            "nid": "NID",
            "tin": "TIN",
            "trade_license": "Trade Licence",
        },
        rows[:200],
        [
            "Sellers whose KYC is not verified. Documents are referenced on the record; "
            "no document content is fabricated."
        ],
        empty="Every seller is KYC-verified.",
    )


def agreements(env, date_from=None, date_to=None, **params):
    sellers = _sellers(env)
    rows = []
    for seller in sellers:
        rows.append(
            {
                "seller": seller.name,
                "tier": seller.tier,
                "cfo_approved": "✓" if seller.cfo_approved else "✗",
                "approved_on": str(seller.cfo_approval_date) if seller.cfo_approval_date else "—",
                "payout_hold": "✓" if seller.payout_hold else "✗",
            }
        )
    return _pack(
        "Agreements & Tiers",
        ["seller", "tier", "cfo_approved", "approved_on", "payout_hold"],
        {
            "seller": "Seller",
            "tier": "Tier",
            "cfo_approved": "CFO Approved",
            "approved_on": "Approved On",
            "payout_hold": "Payout Hold",
        },
        rows[:200],
        [
            "Tier and CFO approval as recorded on the seller agreement; a payout hold "
            "blocks remittance until released."
        ],
        empty="No marketplace sellers yet.",
    )


def listing_coverage(env, date_from=None, date_to=None, **params):
    listings = env["fix.marketplace.listing"].sudo().search([])
    by_state = {}
    for listing in listings:
        row = by_state.setdefault(
            listing.state, {"state": listing.state, "listings": 0, "sellers": set()}
        )
        row["listings"] += 1
        row["sellers"].add(listing.seller_id.id)
    rows = []
    for row in by_state.values():
        rows.append(
            {"state": row["state"], "listings": row["listings"], "sellers": len(row["sellers"])}
        )
    return _pack(
        "Listings & Moderation",
        ["state", "listings", "sellers"],
        {"state": "Listing State", "listings": "Listings", "sellers": "Sellers"},
        rows,
        [
            "Moderation state per listing; a removed listing is a moderation outcome, "
            "not a deletion."
        ],
        empty="No marketplace listings yet.",
    )


def oversight(env, date_from=None, date_to=None, **params):
    sellers = _sellers(env)
    flagged = sellers.filtered(lambda s: s.payout_hold or (s.rating and s.rating < 3.5))
    rows = []
    for seller in flagged:
        rows.append(
            {
                "seller": seller.name,
                "tier": seller.tier,
                "rating": seller.rating,
                "payout_hold": "✓" if seller.payout_hold else "✗",
                "kyc": seller.kyc_status,
                "jobs": seller.total_jobs,
            }
        )
    return _pack(
        "Execution Oversight",
        ["seller", "tier", "rating", "payout_hold", "kyc", "jobs"],
        {
            "seller": "Seller",
            "tier": "Tier",
            "rating": "Rating",
            "payout_hold": "Payout Hold",
            "kyc": "KYC",
            "jobs": "Jobs Done",
        },
        rows,
        [
            "Sellers under oversight: payout hold or rating below 3.5. Rating is the "
            "recorded seller rating."
        ],
        empty="No seller is under oversight.",
    )


def seller_wallet(env, date_from=None, date_to=None, **params):
    statements = env["fix.seller.statement"].sudo().search([])
    by_seller = {}
    for st in statements:
        row = by_seller.setdefault(
            st.seller_partner_id.id,
            {
                "seller": st.seller_partner_id.name or "—",
                "statements": 0,
                "net": 0.0,
                "settled": 0.0,
                "unsettled": 0.0,
            },
        )
        row["statements"] += 1
        row["net"] += st.net_payable or 0.0
        if st.state in ("settled", "paid"):
            row["settled"] += st.net_payable or 0.0
        else:
            row["unsettled"] += st.net_payable or 0.0
    rows = []
    for row in by_seller.values():
        rows.append(
            {
                "seller": row["seller"],
                "statements": row["statements"],
                "net": round(row["net"], 2),
                "settled": round(row["settled"], 2),
                "unsettled": round(row["unsettled"], 2),
            }
        )
    rows.sort(key=lambda r: -r["unsettled"])
    return _pack(
        "Seller Wallets & Payouts",
        ["seller", "statements", "net", "settled", "unsettled"],
        {
            "seller": "Seller",
            "statements": "Statements",
            "net": "Net Payable",
            "settled": "Settled",
            "unsettled": "Unsettled",
        },
        rows,
        [
            "Unsettled net payable is what the wallet still owes; settled statements "
            "carry their payment run."
        ],
        totals={
            "seller": "Total",
            "net": round(sum(r["net"] for r in rows), 2),
            "settled": round(sum(r["settled"] for r in rows), 2),
            "unsettled": round(sum(r["unsettled"] for r in rows), 2),
        }
        if rows
        else None,
        empty="No seller statements yet.",
    )


def fees_register(env, date_from=None, date_to=None, **params):
    statements = env["fix.seller.statement"].sudo().search([])
    rows = []
    for st in statements:
        rows.append(
            {
                "statement": st.name,
                "period": st.period,
                "platform_fee": round(st.platform_fee or 0.0, 2),
                "commission": round(st.commission_amount or 0.0, 2),
                "tds": round(st.tds_withheld or 0.0, 2),
                "clawback": round(st.clawback_amount or 0.0, 2),
                "state": st.state,
            }
        )
    return _pack(
        "Fees & Promotion",
        ["statement", "period", "platform_fee", "commission", "tds", "clawback", "state"],
        {
            "statement": "Statement",
            "period": "Period",
            "platform_fee": "Platform Fee",
            "commission": "Commission",
            "tds": "TDS",
            "clawback": "Clawback",
            "state": "State",
        },
        rows[:200],
        [
            "Fees are the statement's recorded deductions — platform fee, commission, "
            "withheld TDS and clawbacks."
        ],
        empty="No seller statements yet.",
    )


def reviews_summary(env, date_from=None, date_to=None, **params):
    scores = env["fix.seller.score"].sudo().search([])
    bands = {"0-2": 0, "2-3": 0, "3-4": 0, "4-5": 0, "unrated": 0}
    for score in scores:
        rating = score.review_rating or 0.0
        if not score.orders_rated:
            bands["unrated"] += 1
        elif rating < 2:
            bands["0-2"] += 1
        elif rating < 3:
            bands["2-3"] += 1
        elif rating < 4:
            bands["3-4"] += 1
        else:
            bands["4-5"] += 1
    rows = [{"band": k, "scores": v} for k, v in bands.items()]
    return _pack(
        "Ratings & Reviews",
        ["band", "scores"],
        {"band": "Review Rating Band", "scores": "Scorecards"},
        rows,
        [
            "Rating bands from the scorecard's recorded review_rating; 'unrated' means "
            "no order was rated in the period."
        ],
        empty="No seller scorecards yet.",
    )


def trust_bands(env, date_from=None, date_to=None, **params):
    sellers = _sellers(env)
    rows = []
    for seller in sellers.filtered(lambda s: s.rating and s.rating < 3.0)[:200]:
        rows.append(
            {
                "seller": seller.name,
                "rating": seller.rating,
                "kyc": seller.kyc_status,
                "hold": "✓" if seller.payout_hold else "✗",
                "jobs": seller.total_jobs,
            }
        )
    return _pack(
        "Fraud & Trust Ops",
        ["seller", "rating", "kyc", "hold", "jobs"],
        {
            "seller": "Seller",
            "rating": "Rating",
            "kyc": "KYC",
            "hold": "Payout Hold",
            "jobs": "Jobs",
        },
        rows,
        [
            "Low-trust sellers = rating below 3.0. These are the accounts fraud ops "
            "review first; no opaque risk score is claimed."
        ],
        empty="No low-trust sellers.",
    )


def broadcast_backlog(env, date_from=None, date_to=None, **params):
    quotes = (
        env["fix.seller.quote"].sudo().search([("state", "in", ("pending", "new", "submitted"))])
    )
    rows = []
    for quote in quotes[:200]:
        rows.append(
            {
                "order": quote.marketplace_order_id.display_name or "—",
                "seller": quote.seller_id.name or "—",
                "price": round(quote.quoted_price or 0.0, 2),
                "eta_days": quote.eta_days,
                "state": quote.state,
            }
        )
    return _pack(
        "Job Broadcast — open quotes awaiting a decision",
        ["order", "seller", "price", "eta_days", "state"],
        {
            "order": "Marketplace Order",
            "seller": "Seller",
            "price": "Quoted Price",
            "eta_days": "ETA (days)",
            "state": "State",
        },
        rows,
        [
            "The broadcast backlog is the set of quotes not yet decided; the award "
            "happens from the Bidding & Award screen."
        ],
        empty="No open quotes — every bid is decided.",
    )


def training_gap(env, date_from=None, date_to=None, **params):
    return _pack(
        "Standards & Training",
        ["seller", "tier", "status"],
        {"seller": "Seller", "tier": "Tier", "status": "Training Status"},
        [],
        [
            "No marketplace training/standards model exists in the estate — this is a "
            "declared gap. Seller tier is the only recorded capability signal."
        ],
        empty="Training records need a standards model (declared gap).",
    )


def stock_gap(env, date_from=None, date_to=None, **params):
    return _pack(
        "Seller Stock",
        ["seller", "sku", "quantity"],
        {"seller": "Seller", "sku": "SKU", "quantity": "Quantity"},
        [],
        [
            "Seller-owned stock is not modelled (marketplace listings carry no stock "
            "record). Declared gap — no quantity is invented."
        ],
        empty="Seller stock needs a stock model (declared gap).",
    )


REPORTS = {
    "seller_liquidity": seller_liquidity,
    "scorecard_distribution": scorecard_distribution,
    "fill_rate": fill_rate,
    "commission_revenue": commission_revenue,
    "dispute_rate": dispute_rate,
    "kyc_queue": kyc_queue,
    "agreements": agreements,
    "listing_coverage": listing_coverage,
    "oversight": oversight,
    "seller_wallet": seller_wallet,
    "fees_register": fees_register,
    "reviews_summary": reviews_summary,
    "trust_bands": trust_bands,
    "broadcast_backlog": broadcast_backlog,
    "training_gap": training_gap,
    "stock_gap": stock_gap,
}


def kpis(env):
    sellers = _sellers(env)
    scores = env["fix.seller.score"].sudo().search([])
    disputes = env["fix.marketplace.dispute"].sudo().search([])
    today = datetime.date.today()
    month_start = today.replace(day=1)
    payouts_mtd = len(
        env["fix.payout.run"]
        .sudo()
        .search([("create_date", ">=", datetime.datetime.combine(month_start, datetime.time.min))])
    )
    decided = sum(s.quotes_decided or 0 for s in scores)
    awarded = sum(s.orders_awarded or 0 for s in scores)
    open_disputes = len(disputes.filtered(lambda d: d.state not in ("resolved", "closed")))
    return {
        "active_sellers": len(sellers.filtered(lambda s: s.active)),
        "job_fill_rate": round(awarded / decided * 100.0, 1) if decided else None,
        "marketplace_share": None,  # no cross-channel GMV denominator (declared gap)
        "disputes_open": open_disputes,
        "payouts_mtd": payouts_mtd,
        "seller_nps": None,  # no NPS survey keyed to sellers (declared gap)
    }


class P03MarketplaceApi(http.Controller):
    @http.route("/p03/marketplace/kpis", type="jsonrpc", auth="user", readonly=True)
    def marketplace_kpis(self, module=None, **kw):
        _require_internal(request.env)
        return {"M12": kpis(request.env)}
