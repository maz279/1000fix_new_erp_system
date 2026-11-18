# A04 · M12 Marketplace & Sellers — surfaces, report packs and KPIs over the
# real seller (2061) / order (2150) / quote / score / statement / dispute
# records and the new listing model. Fill rates and commissions are measured;
# seller NPS (no survey key on sellers) is a declared gap. Seller stock
# (fix.seller.stock) and seller standards (fix.seller.certification against
# fix.seller.standard) were declared gaps until 12 Nov 2026 and are now built.
import datetime

from odoo import fields, http
from odoo.http import request

from ..p03_service_order_api import _company_domain, _require_internal

SURFACES = {
    # A04 workflow audit (2026-11-03) M12-12: every surface declared
    # `actions: set()` while the forms offered state, cfo_approved,
    # kyc_status, tier and commission_rate as edit fields. The lifecycles are
    # whitelisted; each method checks its own role, state and segregation of
    # duties (cd_marketplace), and the approvals run from the M63 inbox.
    "fix.marketplace.seller": {
        "order": "tier, name",
        "limit": 300,
        "actions": {
            "action_submit_kyc",
            "action_verify_kyc",
            "action_reject_kyc",
            "action_request_approval",
            "action_recall_approval",
        },
    },
    "fix.marketplace.listing": {
        "order": "name",
        "limit": 300,
        "actions": {
            "action_submit",
            "action_recall_approval",
            "action_pause",
            "action_resume",
            "action_withdraw",
            "action_remove",
        },
    },
    "fix.marketplace.dispute": {
        "order": "create_date desc, id desc",
        "limit": 300,
        "actions": {
            "action_investigate",
            "action_arbitrate",
            "action_recall_approval",
            "action_escalate",
        },
    },
    "fix.seller.quote": {
        "order": "create_date desc, id desc",
        "limit": 300,
        "actions": {"action_select"},
    },
    "fix.seller.score": {
        "order": "period desc, id desc",
        "limit": 300,
        "actions": {"action_publish"},
    },
    # fix.seller.statement and fix.payout.run are owned by M53 (a08 surface).
    "fix.marketplace.order": {
        "order": "id desc",
        "limit": 400,
        "actions": {
            "action_start_job",
            "action_complete",
            "action_review",
            "action_earn_commission",
            "action_paid",
            "action_cancel",
        },
    },
    # M12-stock (12 Nov 2026): the seller's reported position per listing and
    # SKU; who reported it and when are stamped by the server.
    "fix.seller.stock": {
        "order": "seller_id, listing_id, sku",
        "limit": 500,
        "actions": set(),
    },
    # M12-training (12 Nov 2026): the standards a seller can hold, mapped to
    # the categories that require them, and the seller's certifications.
    "fix.seller.standard": {
        "order": "code",
        "limit": 300,
        "actions": set(),
    },
    "fix.seller.certification": {
        "order": "expires_on, id",
        "limit": 500,
        "actions": {"action_submit", "action_verify", "action_reject", "action_revoke"},
    },
    # M12 capture audit (13 Nov 2026): Performance Consequences had no record.
    # A warning, probation or suspension is imposed by an operator; lifting it
    # or deciding its appeal is another operator's (BRU-MKP-18), checked in
    # the model.
    "fix.seller.consequence": {
        "order": "effective_from desc, id desc",
        "limit": 300,
        "actions": {
            "action_impose",
            "action_appeal",
            "action_uphold_appeal",
            "action_dismiss_appeal",
            "action_lift",
            "action_cancel",
        },
    },
    # M12 capture audit, second pass (19 Nov 2026): the records pages 5, 6
    # and 11 capture. Each method checks its role, state and segregation of
    # duties in cd_marketplace (fix_marketplace_capture.py).
    "fix.marketplace.job.evidence": {
        "order": "order_id, captured_at, id",
        "limit": 500,
        "actions": set(),
    },
    "fix.seller.review": {
        "order": "create_date desc, id desc",
        "limit": 300,
        "actions": {"action_publish", "action_reject", "action_record_response"},
    },
    "fix.trust.signal": {
        "order": "create_date desc, id desc",
        "limit": 300,
        "actions": {"action_investigate", "action_substantiate", "action_dismiss"},
    },
    # A04 P2 (M12): customer chargebacks against marketplace sales.
    "fix.marketplace.chargeback": {
        "order": "received_on desc, id desc",
        "limit": 300,
        "actions": {
            "action_submit_evidence",
            "action_mark_won",
            "action_mark_lost",
            "action_accept",
        },
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


def _sellers(env):
    return env["fix.marketplace.seller"].search([])


def seller_liquidity(env, date_from=None, date_to=None, **params):
    sellers = _sellers(env)
    listings = env["fix.marketplace.listing"].search([])
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
    scores = env["fix.seller.score"].search([])
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
    scores = env["fix.seller.score"].search([])
    quotes = env["fix.seller.quote"].search([])
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
    disputes = env["fix.marketplace.dispute"].search([])
    orders = env["fix.marketplace.order"].search_count([])
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
    listings = env["fix.marketplace.listing"].search([])
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
    scores = env["fix.seller.score"].search([])
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
    quotes = env["fix.seller.quote"].search([("state", "in", ("pending", "new", "submitted"))])
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


STALE_DAYS = 30
EXPIRING_DAYS = 30
_SOURCE_LABELS = {"seller": "Seller", "operator": "Operator", "import": "Import"}


def _int_param(value, default):
    try:
        number = int(value)
    except (TypeError, ValueError):
        return default
    return number if number > 0 else default


def seller_stock(env, date_from=None, date_to=None, stale_days=None, **params):
    """M12-stock: every seller stock position, per seller, listing and SKU,
    read as the caller inside the company fence; a position whose quantity
    was last reported more than `stale_days` ago is flagged stale."""
    from odoo.addons.cd_p03_portal.controllers.p03_generic_api import _datetime_to_local

    stale_days = _int_param(stale_days, STALE_DAYS)
    positions = env["fix.seller.stock"].search(
        _company_domain(env, "fix.seller.stock"), order="seller_id, listing_id, sku"
    )
    now = fields.Datetime.now()
    rows = []
    for pos in positions:
        age = (now - pos.last_updated).days if pos.last_updated else None
        stale = age is None or age > stale_days
        rows.append(
            {
                "seller": pos.seller_id.name,
                "listing": pos.listing_id.name,
                "sku": pos.sku,
                "part": pos.part_id.display_name if pos.part_id else "—",
                "on_hand": round(pos.qty_on_hand or 0.0, 2),
                "reserved": round(pos.qty_reserved or 0.0, 2),
                "available": round(pos.qty_available or 0.0, 2),
                "last_update": (
                    _datetime_to_local(env, pos.last_updated)[:16] if pos.last_updated else "—"
                ),
                "age_days": age,
                "source": _SOURCE_LABELS.get(pos.source, pos.source or "—"),
                "stale": "✓" if stale else "✗",
            }
        )
    live = env["fix.marketplace.listing"].search(
        [*_company_domain(env, "fix.marketplace.listing"), ("state", "in", ("active", "paused"))]
    )
    bare = live.filtered(lambda ln: not ln.stock_ids)
    notes = [
        "Each row is a seller's reported position for one SKU behind one listing: on hand, "
        "reserved and available (on hand − reserved), as reported by the seller, an "
        "operator or an import. Stale = last reported more than %d days ago." % stale_days,
    ]
    if bare:
        names = ", ".join(bare[:10].mapped("name"))
        more = " and %d more" % (len(bare) - 10) if len(bare) > 10 else ""
        notes.append(
            "%d live listing(s) carry no stock position yet: %s%s." % (len(bare), names, more)
        )
    pack = _pack(
        "Seller Stock",
        [
            "seller",
            "listing",
            "sku",
            "part",
            "on_hand",
            "reserved",
            "available",
            "last_update",
            "age_days",
            "source",
            "stale",
        ],
        {
            "seller": "Seller",
            "listing": "Listing",
            "sku": "SKU",
            "part": "Catalogue Part",
            "on_hand": "On Hand",
            "reserved": "Reserved",
            "available": "Available",
            "last_update": "Last Reported",
            "age_days": "Age (days)",
            "source": "Reported Via",
            "stale": "Stale",
        },
        rows,
        notes,
        totals={
            "seller": "Total",
            "on_hand": round(sum(r["on_hand"] for r in rows), 2),
            "reserved": round(sum(r["reserved"] for r in rows), 2),
            "available": round(sum(r["available"] for r in rows), 2),
            "stale": sum(1 for r in rows if r["stale"] == "✓"),
        }
        if rows
        else None,
        empty="No seller has reported stock yet (Seller Stock Positions).",
    )
    pack["filters"] = [
        {
            "key": "stale_days",
            "label": "Stale after (days)",
            "options": ["30", "7", "14", "60", "90"],
        }
    ]
    return pack


def _codes(certs, with_expiry=False):
    if not certs:
        return "—"
    parts = []
    for cert in certs.sorted(lambda c: c.standard_id.code or ""):
        code = cert.standard_id.code or cert.standard_id.name
        if with_expiry and cert.expires_on:
            code = "%s (until %s)" % (code, cert.expires_on)
        parts.append(code)
    return ", ".join(parts)


def seller_standards(env, date_from=None, date_to=None, expiring_days=None, **params):
    """M12-training: per seller, the standards held, expiring, expired,
    pending verification and MISSING - the standards the seller's approved
    service categories require (fix.seller.standard.category_ids) that the
    seller does not validly hold. Read as the caller inside the company fence."""
    window = _int_param(expiring_days, EXPIRING_DAYS)
    # the reader's calendar; Asia/Dhaka when no zone is set (as the expiry cron)
    tz = env.context.get("tz") or env.user.tz or "Asia/Dhaka"
    today = fields.Date.context_today(env["fix.seller.certification"].with_context(tz=tz))
    sellers = env["fix.marketplace.seller"].search(
        _company_domain(env, "fix.marketplace.seller"), order="name"
    )
    certs = env["fix.seller.certification"].search(
        [*_company_domain(env, "fix.seller.certification"), ("seller_id", "in", sellers.ids)]
    )
    standards = env["fix.seller.standard"].search([])
    rows = []
    for seller in sellers:
        mine = certs.filtered(lambda c, sid=seller.id: c.seller_id.id == sid)
        verified = mine.filtered(lambda c: c.state == "verified")
        held = verified.filtered(lambda c: not c.expires_on or c.expires_on >= today)
        lapsed = (verified - held) | mine.filtered(lambda c: c.state == "expired")
        expiring = held.filtered(lambda c: c.expires_on and (c.expires_on - today).days <= window)
        pending = mine.filtered(lambda c: c.state == "submitted")
        required = standards.filtered(lambda st, cats=seller.category_ids: st.category_ids & cats)
        missing = required - held.mapped("standard_id")
        if not mine and not required:
            continue
        if missing:
            status = "Missing required"
        elif expiring:
            status = "Expiring"
        else:
            status = "OK"
        rows.append(
            {
                "seller": seller.name,
                "tier": seller.tier,
                "held": _codes(held),
                "expiring": _codes(expiring, with_expiry=True),
                "expired": _codes(lapsed, with_expiry=True),
                "missing": ", ".join(missing.sorted("code").mapped("code")) or "—",
                "pending": _codes(pending),
                "status": status,
            }
        )
    order = {"Missing required": 0, "Expiring": 1, "OK": 2}
    rows.sort(key=lambda r: (order[r["status"]], r["seller"]))
    return _pack(
        "Standards & Training",
        ["seller", "tier", "held", "expiring", "expired", "missing", "pending", "status"],
        {
            "seller": "Seller",
            "tier": "Tier",
            "held": "Standards Held",
            "expiring": "Expiring (%d days)" % window,
            "expired": "Expired",
            "missing": "Missing (required by categories)",
            "pending": "Awaiting Verification",
            "status": "Status",
        },
        rows,
        [
            "Held = a certification a compliance reviewer verified that is inside its "
            "validity; expiring = held and ending within %d days; expired = past its date "
            "(whether or not the daily expiry run has visited it)." % window,
            "Missing = a standard one of the seller's approved service categories requires "
            "(the standard's 'Required for Categories') that the seller does not validly "
            "hold. Sellers with no certification and no required standard are not listed.",
        ],
        empty="No seller holds or needs a standard yet (Seller Certifications).",
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
    "seller_standards": seller_standards,
    "seller_stock": seller_stock,
}


def kpis(env):
    sellers = _sellers(env)
    scores = env["fix.seller.score"].search([])
    disputes = env["fix.marketplace.dispute"].search([])
    today = fields.Date.context_today(env["fix.marketplace.order"])
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
