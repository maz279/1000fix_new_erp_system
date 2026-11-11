# A04 · M40 Partner & Channel — surfaces, report packs and KPIs over the real
# fix.partner (8) / fix.referral (7) and the new authorisation, deal, rebate,
# franchise and conflict models. Partner revenue is the referral commission
# actually recorded; no revenue is attributed without a ledger line.
# Co-marketing (a declared gap until 12 Nov 2026) is built from the campaign's
# co-marketing partners (fix.campaign.partner_ids), the MDF's campaign key
# (fix.partner.rebate.campaign_id) and the M35 touch attribution.
import datetime

from odoo import http
from odoo.http import request

from ..p03_service_order_api import _company_domain, _require_internal

# A04 workflow audit (2026-11-04) C3/D2: every M40 surface declared
# `actions: set()`, so the workspace could only edit the state. The
# lifecycles now run from these actions; the server checks the role, the
# state, the evidence (KYC documents, certificate, approved audit) and the
# segregation of duties of each. The rebate payout is approved from the M63
# inbox (Request Payout Approval), never by pressing Approve here.
SURFACES = {
    "fix.partner": {
        "order": "partner_type, name",
        "limit": 300,
        "actions": {
            "action_submit_onboarding",
            "action_verify_kyc",
            "action_onboard",
            "action_return_to_prospect",
            "action_suspend",
            "action_reinstate",
            "action_set_commission_rate",
            "action_request_erasure",
            "action_execute_erasure",
        },
    },
    # fix.referral is owned by M53 (a08 surface) — read through the merge.
    "fix.partner.authorisation": {
        "order": "valid_to, id",
        "limit": 300,
        "actions": {"action_activate", "action_revoke"},
    },
    "fix.partner.deal": {
        "order": "registered_on desc, id desc",
        "limit": 300,
        "actions": {"action_approve", "action_decline", "action_mark_won", "action_mark_lost"},
    },
    "fix.partner.rebate": {
        "order": "period desc, id desc",
        "limit": 300,
        "actions": {
            "action_accrue",
            "action_request_approval",
            "action_recall_approval",
            "action_record_payout",
            "action_cancel",
        },
    },
    "fix.partner.franchise": {
        "order": "start_date, id",
        "limit": 200,
        "actions": {"action_activate", "action_terminate"},
    },
    "fix.partner.conflict": {
        "order": "create_date desc, id desc",
        "limit": 200,
        "actions": {
            "action_mediate",
            "action_rule_partner_a",
            "action_rule_partner_b",
            "action_rule_split",
            "action_rule_direct",
            "action_close",
        },
    },
    # A04 audit M40-2: the technical audit behind the 85% rebate gate.
    "fix.partner.audit": {
        "order": "audit_date desc, id desc",
        "limit": 300,
        "actions": {"action_submit", "action_approve", "action_reject"},
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


def _partners(env):
    return env["fix.partner"].sudo().search([])


def brand_partners(env, date_from=None, date_to=None, **params):
    auths = env["fix.partner.authorisation"].sudo().search([])
    by_brand = {}
    for auth in auths:
        key = auth.brand_id.name if auth.brand_id else "No brand"
        row = by_brand.setdefault(
            key, {"brand": key, "authorisations": 0, "active": 0, "partners": set()}
        )
        row["authorisations"] += 1
        if auth.state == "active":
            row["active"] += 1
        row["partners"].add(auth.partner_id.id)
    rows = []
    for row in by_brand.values():
        rows.append(
            {
                "brand": row["brand"],
                "authorisations": row["authorisations"],
                "active": row["active"],
                "partners": len(row["partners"]),
            }
        )
    rows.sort(key=lambda r: -r["authorisations"])
    return _pack(
        "Brand Partner Relations",
        ["brand", "authorisations", "active", "partners"],
        {
            "brand": "Brand",
            "authorisations": "Authorisations",
            "active": "Active",
            "partners": "Partners",
        },
        rows,
        [
            "Authorisations group the partner's brand credentials; an expired or revoked "
            "authorisation stays visible."
        ],
        empty="No brand authorisations recorded yet.",
    )


def brand_audit_calendar(env, date_from=None, date_to=None, **params):
    auths = env["fix.partner.authorisation"].sudo().search([])
    today = datetime.date.today()
    horizon = today + datetime.timedelta(days=90)
    rows = []
    for auth in auths.filtered(lambda a: a.state == "active" and a.valid_to):
        due = (auth.valid_to - today).days
        if auth.valid_to <= horizon:
            rows.append(
                {
                    "partner": auth.partner_id.name,
                    "brand": auth.brand_id.name if auth.brand_id else "—",
                    "valid_to": str(auth.valid_to),
                    "days_left": due,
                    "state": auth.state,
                }
            )
    rows.sort(key=lambda r: r["days_left"])
    return _pack(
        "Brand Audit Calendar — authorisations due within 90 days",
        ["partner", "brand", "valid_to", "days_left", "state"],
        {
            "partner": "Partner",
            "brand": "Brand",
            "valid_to": "Valid To",
            "days_left": "Days Left",
            "state": "State",
        },
        rows,
        [
            "Audits are the authorisation expiry dates — the calendar reads the "
            "recorded validity window, nothing else."
        ],
        empty="No authorisation expires within 90 days.",
    )


def referral_conversion(env, date_from=None, date_to=None, **params):
    referrals = env["fix.referral"].sudo().search([])
    states = {}
    for ref in referrals:
        state = ref.state or "unknown"
        row = states.setdefault(state, {"state": state, "referrals": 0, "commission": 0.0})
        row["referrals"] += 1
        row["commission"] += ref.commission_amount or 0.0
    rows = []
    for row in states.values():
        row["commission"] = round(row["commission"], 2)
        rows.append(row)
    rows.sort(key=lambda r: -r["referrals"])
    return _pack(
        "Referral Conversion",
        ["state", "referrals", "commission"],
        {"state": "Referral State", "referrals": "Referrals", "commission": "Commission"},
        rows,
        [
            "Commission is the referral's recorded ledger amount; conversion is the "
            "state distribution, not an assumption."
        ],
        totals={
            "state": "Total",
            "referrals": len(referrals),
            "commission": round(sum(r["commission"] for r in rows), 2),
        }
        if rows
        else None,
        empty="No partner referrals yet.",
    )


def partner_revenue(env, date_from=None, date_to=None, **params):
    referrals = env["fix.referral"].sudo().search([])
    deals = env["fix.partner.deal"].sudo().search([])
    today = datetime.date.today()
    month_start = today.replace(day=1)
    rows = []
    for partner in _partners(env):
        partner_refs = referrals.filtered(
            lambda r, pid=partner.id: r.partner_id.id == pid if hasattr(r, "partner_id") else False
        )
        partner_deals = deals.filtered(lambda d, pid=partner.id: d.partner_id.id == pid)
        commission_mtd = sum(
            (r.commission_amount or 0.0)
            for r in partner_refs
            if getattr(r, "create_date", None) and r.create_date.date() >= month_start
        )
        won_value = sum((d.value or 0.0) for d in partner_deals if d.state == "won")
        if not partner_refs and not partner_deals:
            continue
        rows.append(
            {
                "partner": partner.name,
                "type": partner.partner_type,
                "referrals": len(partner_refs),
                "commission_mtd": round(commission_mtd, 2),
                "deals_won": round(won_value, 2),
            }
        )
    rows.sort(key=lambda r: -(r["commission_mtd"] + r["deals_won"]))
    return _pack(
        "Partner Revenue Contribution",
        ["partner", "type", "referrals", "commission_mtd", "deals_won"],
        {
            "partner": "Partner",
            "type": "Type",
            "referrals": "Referrals",
            "commission_mtd": "Commission MTD",
            "deals_won": "Deals Won Value",
        },
        rows,
        [
            "Commission MTD comes from referral ledger lines; deal value is the "
            "registered deal's own amount for won deals."
        ],
        totals={
            "partner": "Total",
            "referrals": sum(r["referrals"] for r in rows),
            "commission_mtd": round(sum(r["commission_mtd"] for r in rows), 2),
            "deals_won": round(sum(r["deals_won"] for r in rows), 2),
        }
        if rows
        else None,
        empty="No partner activity recorded yet.",
    )


def rebate_accruals(env, date_from=None, date_to=None, **params):
    rebates = env["fix.partner.rebate"].sudo().search([])
    rows = []
    for rebate in rebates:
        rows.append(
            {
                "rebate": rebate.name,
                "partner": rebate.partner_id.name,
                "period": rebate.period,
                "kind": rebate.kind,
                "basis": round(rebate.basis or 0.0, 2),
                "rate": round((rebate.rate or 0.0) * 100.0, 2),
                "amount": round(rebate.amount or 0.0, 2),
                "state": rebate.state,
            }
        )
    rows.sort(key=lambda r: -r["amount"])
    accrued = sum(r["amount"] for r in rows if r["state"] == "accrued")
    return _pack(
        "Rebate Accruals",
        ["rebate", "partner", "period", "kind", "basis", "rate", "amount", "state"],
        {
            "rebate": "Rebate",
            "partner": "Partner",
            "period": "Period",
            "kind": "Kind",
            "basis": "Basis",
            "rate": "Rate %",
            "amount": "Amount",
            "state": "State",
        },
        rows,
        ["Amount = basis × rate (computed and stored). Accrued: %s." % round(accrued, 2)],
        totals={"rebate": "Total", "amount": round(sum(r["amount"] for r in rows), 2)}
        if rows
        else None,
        empty="No rebates or MDF accruals yet.",
    )


def conflict_log(env, date_from=None, date_to=None, **params):
    conflicts = env["fix.partner.conflict"].sudo().search([])
    rows = []
    for conflict in conflicts:
        rows.append(
            {
                "conflict": conflict.name,
                "partner_a": conflict.partner_a_id.name,
                "partner_b": conflict.partner_b_id.name or "—",
                "customer": conflict.customer_id.name or "—",
                "state": conflict.state,
                "resolution": conflict.resolution or "—",
            }
        )
    return _pack(
        "Channel Conflict Log",
        ["conflict", "partner_a", "partner_b", "customer", "state", "resolution"],
        {
            "conflict": "Conflict",
            "partner_a": "Partner A",
            "partner_b": "Partner B",
            "customer": "Contested Customer",
            "state": "State",
            "resolution": "Resolution",
        },
        rows,
        [
            "A conflict is a recorded dispute between partners over a customer; "
            "resolution is the outcome narrative."
        ],
        empty="No channel conflicts recorded.",
    )


def alliance_report(env, date_from=None, date_to=None, **params):
    partners = _partners(env).filtered(lambda p: p.partner_type == "alliance")
    rows = []
    for partner in partners:
        rows.append(
            {
                "partner": partner.name,
                "territory": partner.territory or "—",
                "commission": round((partner.commission_rate or 0.0) * 100.0, 2),
                "state": partner.state,
            }
        )
    return _pack(
        "Alliance Benefits — strategic alliance partners",
        ["partner", "territory", "commission", "state"],
        {
            "partner": "Partner",
            "territory": "Territory",
            "commission": "Commission %",
            "state": "State",
        },
        rows,
        [
            "Alliance partners and their recorded commission rate; a dedicated "
            "alliance-benefit schedule is not modelled (declared gap)."
        ],
        empty="No strategic alliance partners yet.",
    )


def reseller_report(env, date_from=None, date_to=None, **params):
    partners = _partners(env).filtered(lambda p: p.partner_type == "reseller")
    deals = env["fix.partner.deal"].sudo().search([])
    rows = []
    for partner in partners:
        mine = deals.filtered(lambda d, pid=partner.id: d.partner_id.id == pid)
        rows.append(
            {
                "partner": partner.name,
                "territory": partner.territory or "—",
                "deals": len(mine),
                "won_value": round(sum((d.value or 0.0) for d in mine if d.state == "won"), 2),
                "state": partner.state,
            }
        )
    rows.sort(key=lambda r: -r["won_value"])
    return _pack(
        "Resellers",
        ["partner", "territory", "deals", "won_value", "state"],
        {
            "partner": "Reseller",
            "territory": "Territory",
            "deals": "Deals",
            "won_value": "Won Value",
            "state": "State",
        },
        rows,
        ["Resellers with their registered deals and won value."],
        empty="No reseller partners yet.",
    )


ATTRIBUTION_MODELS = ["position", "last_touch", "first_touch", "linear", "time_decay"]
_MDF_BUCKETS = {
    "draft": "mdf_planned",
    "accrued": "mdf_accrued",
    "approved": "mdf_approved",
    "paid": "mdf_paid",
}


def _campaign_revenue(env, campaigns, model):
    """Per campaign id, what the M35 touch ledger attributes to it under
    `model`: {id: (conversions, revenue or None, complete?)}. Revenue is only
    the conversions whose value is on file; a campaign with any credited
    conversion of unknown value is not complete."""
    result = env["fix.campaign.touch"].attribute(model=model)
    out = {}
    for row in result["rows"]:
        if row["campaign_id"] in campaigns.ids:
            complete = not row["conversions_without_value"]
            out[row["campaign_id"]] = (
                row["attributed_conversions"],
                row["attributed_revenue"],
                complete,
            )
    return out


def comarketing(env, date_from=None, date_to=None, model=None, **params):
    """M40-comarketing: per channel partner, the campaigns it co-funds
    (fix.campaign.partner_ids), its MDF by state on those campaigns
    (fix.partner.rebate kind 'mdf' with a campaign_id), and the revenue the
    M35 touch attribution credits to those campaigns where the conversion
    value is on file. Read as the caller inside the company fence."""
    model = model if model in ATTRIBUTION_MODELS else ATTRIBUTION_MODELS[0]
    campaigns = env["fix.campaign"].search(
        [*_company_domain(env, "fix.campaign"), ("partner_ids", "!=", False)]
    )
    partners = campaigns.partner_ids.filtered_domain(_company_domain(env, "fix.partner"))
    mdfs = env["fix.partner.rebate"].search(
        [
            ("kind", "=", "mdf"),
            ("campaign_id", "in", campaigns.ids),
            ("state", "in", tuple(_MDF_BUCKETS)),
        ]
    )
    revenue = _campaign_revenue(env, campaigns, model)
    rows = []
    for partner in partners.sorted("name"):
        funded = campaigns.filtered(lambda c, pid=partner.id: pid in c.partner_ids.ids)
        row = {
            "partner": partner.name,
            "campaigns": ", ".join(funded.sorted("name").mapped("name")),
            "mdf_planned": 0.0,
            "mdf_accrued": 0.0,
            "mdf_approved": 0.0,
            "mdf_paid": 0.0,
        }
        for mdf in mdfs.filtered(lambda r, pid=partner.id: r.partner_id.id == pid):
            row[_MDF_BUCKETS[mdf.state]] += mdf.amount or 0.0
        for key in _MDF_BUCKETS.values():
            row[key] = round(row[key], 2)
        credited = [revenue[c.id] for c in funded if c.id in revenue]
        known = [r for r in credited if r[2]]
        conversions = round(sum(r[0] for r in credited), 2)
        if not credited:
            amount, basis = None, "no attributed conversions"
        elif not known:
            amount, basis = None, "no known value — conversions on file carry no order value"
        else:
            amount = round(sum(r[1] for r in known), 2)
            basis = (
                "complete"
                if len(known) == len(credited)
                else "partial — %d of %d campaign(s) with conversions of unknown value excluded"
                % (len(credited) - len(known), len(credited))
            )
        row.update(
            {
                "attributed_conversions": conversions,
                "attributed_revenue": amount,
                "revenue_basis": basis,
            }
        )
        rows.append(row)
    shown = campaigns.filtered(lambda c: c.partner_ids & partners)
    distinct_revenue = round(
        sum(revenue[c.id][1] for c in shown if c.id in revenue and revenue[c.id][2]), 2
    )
    unlinked = env["fix.partner.rebate"].search_count(
        [("kind", "=", "mdf"), ("campaign_id", "=", False), ("state", "!=", "cancelled")]
    )
    notes = [
        "Campaigns are the M35 campaigns that name the partner as a co-marketing partner; "
        "MDF is the partner's market development fund on those campaigns by state "
        "(planned = draft, accrued, approved for payout, paid; cancelled is left out).",
        "Attributed revenue is the %s attribution of the M35 touch ledger, counted only "
        "where every credited conversion of the campaign has its value on file. It is the "
        "co-funded campaigns' revenue, not a partner share: a campaign co-funded by two "
        "partners shows under both, and the total counts it once." % model,
    ]
    if unlinked:
        notes.append(
            "%d MDF accrual(s) name no campaign and are not shown here (see Rebate Accruals)."
            % unlinked
        )
    pack = _pack(
        "Co-Marketing — partners, campaigns and MDF",
        [
            "partner",
            "campaigns",
            "mdf_planned",
            "mdf_accrued",
            "mdf_approved",
            "mdf_paid",
            "attributed_conversions",
            "attributed_revenue",
            "revenue_basis",
        ],
        {
            "partner": "Partner",
            "campaigns": "Co-Funded Campaigns",
            "mdf_planned": "MDF Planned",
            "mdf_accrued": "MDF Accrued",
            "mdf_approved": "MDF Approved",
            "mdf_paid": "MDF Paid",
            "attributed_conversions": "Attributed Conversions",
            "attributed_revenue": "Attributed Revenue",
            "revenue_basis": "Revenue Basis",
        },
        rows,
        notes,
        totals={
            "partner": "Total",
            "mdf_planned": round(sum(r["mdf_planned"] for r in rows), 2),
            "mdf_accrued": round(sum(r["mdf_accrued"] for r in rows), 2),
            "mdf_approved": round(sum(r["mdf_approved"] for r in rows), 2),
            "mdf_paid": round(sum(r["mdf_paid"] for r in rows), 2),
            "attributed_revenue": distinct_revenue,
        }
        if rows
        else None,
        empty="No campaign names a co-marketing partner yet (M35 campaign, Co-Marketing "
        "Partners; or the partner's Co-Marketing Campaigns).",
    )
    pack["filters"] = [
        {"key": "model", "label": "Attribution model", "options": list(ATTRIBUTION_MODELS)}
    ]
    return pack


def health(env, date_from=None, date_to=None, **params):
    deals = env["fix.partner.deal"].sudo().search([])
    conflicts = env["fix.partner.conflict"].sudo().search([])
    rows = []
    for partner in _partners(env):
        partner_deals = deals.filtered(lambda d, pid=partner.id: d.partner_id.id == pid)
        partner_conflicts = conflicts.filtered(lambda c, pid=partner.id: c.partner_a_id.id == pid)
        score = len(partner_deals) * 2 - len(partner_conflicts) * 3
        rows.append(
            {
                "partner": partner.name,
                "type": partner.partner_type,
                "state": partner.state,
                "deals": len(partner_deals),
                "conflicts": len(partner_conflicts),
                "health": "healthy" if score >= 2 else ("watch" if score >= 0 else "at risk"),
            }
        )
    rows.sort(key=lambda r: r["health"])
    return _pack(
        "Health & Risk",
        ["partner", "type", "state", "deals", "conflicts", "health"],
        {
            "partner": "Partner",
            "type": "Type",
            "state": "Onboarding State",
            "deals": "Deals",
            "conflicts": "Conflicts",
            "health": "Health",
        },
        rows[:200],
        [
            "Health is a stated derivation: 2 × deals − 3 × conflicts, with bands "
            "healthy/watch/at-risk. No opaque model score is claimed."
        ],
        empty="No partners yet.",
    )


def ranking(env, date_from=None, date_to=None, **params):
    pack = partner_revenue(env)
    rows = []
    for rank, row in enumerate(pack["rows"], start=1):
        rows.append(
            {
                "rank": rank,
                "partner": row["partner"],
                "type": row["type"],
                "commission_mtd": row["commission_mtd"],
                "deals_won": row["deals_won"],
            }
        )
    return _pack(
        "Ranking & Scorecards",
        ["rank", "partner", "type", "commission_mtd", "deals_won"],
        {
            "rank": "Rank",
            "partner": "Partner",
            "type": "Type",
            "commission_mtd": "Commission MTD",
            "deals_won": "Deals Won Value",
        },
        rows[:100],
        [
            "Ranking = commission MTD + won deal value, descending. Tie-break is the "
            "partner name."
        ],
        empty="No partner activity to rank yet.",
    )


def deal_register(env, date_from=None, date_to=None, **params):
    deals = env["fix.partner.deal"].sudo().search([])
    rows = []
    for deal in deals:
        rows.append(
            {
                "deal": deal.name,
                "partner": deal.partner_id.name,
                "customer": deal.customer_id.name or "—",
                "value": round(deal.value or 0.0, 2),
                "registered": str(deal.registered_on),
                "state": deal.state,
            }
        )
    rows.sort(key=lambda r: -r["value"])
    return _pack(
        "Deal Registration",
        ["deal", "partner", "customer", "value", "registered", "state"],
        {
            "deal": "Deal",
            "partner": "Partner",
            "customer": "End Customer",
            "value": "Deal Value",
            "registered": "Registered",
            "state": "State",
        },
        rows,
        ["Each deal records the partner's protected opportunity and its value."],
        empty="No deal registrations yet.",
    )


def franchises(env, date_from=None, date_to=None, **params):
    franchises = env["fix.partner.franchise"].sudo().search([])
    rows = []
    for franchise in franchises:
        rows.append(
            {
                "franchise": franchise.name,
                "partner": franchise.partner_id.name,
                "territory": franchise.territory,
                "fee": round(franchise.fee or 0.0, 2),
                "start": str(franchise.start_date),
                "end": str(franchise.end_date) if franchise.end_date else "—",
                "state": franchise.state,
            }
        )
    return _pack(
        "Franchise Management",
        ["franchise", "partner", "territory", "fee", "start", "end", "state"],
        {
            "franchise": "Franchise",
            "partner": "Partner",
            "territory": "Territory",
            "fee": "Franchise Fee",
            "start": "Start",
            "end": "End",
            "state": "State",
        },
        rows,
        ["Franchise agreements with territory, fee and validity."],
        empty="No franchise agreements yet.",
    )


REPORTS = {
    "brand_partners": brand_partners,
    "brand_audit_calendar": brand_audit_calendar,
    "referral_conversion": referral_conversion,
    "partner_revenue": partner_revenue,
    "rebate_accruals": rebate_accruals,
    "conflict_log": conflict_log,
    "alliance_report": alliance_report,
    "reseller_report": reseller_report,
    "comarketing": comarketing,
    "health": health,
    "ranking": ranking,
    "deal_register": deal_register,
    "franchises": franchises,
}


def kpis(env):
    partners = _partners(env)
    auths = env["fix.partner.authorisation"].sudo().search([("state", "=", "active")])
    deals = env["fix.partner.deal"].sudo().search([])
    rebates = env["fix.partner.rebate"].sudo().search([("state", "=", "accrued")])
    referrals = env["fix.referral"].sudo().search([])
    today = datetime.date.today()
    horizon = today + datetime.timedelta(days=90)
    audits_due = len(auths.filtered(lambda a: a.valid_to and today <= a.valid_to <= horizon))
    month_start = today.replace(day=1)
    commission_mtd = sum(
        (r.commission_amount or 0.0)
        for r in referrals
        if getattr(r, "create_date", None) and r.create_date.date() >= month_start
    )
    return {
        "brand_partners": len(auths),
        "referral_partners": len(partners.filtered(lambda p: p.partner_type == "referral")),
        "deal_registrations": len(deals),
        "partner_revenue_mtd": round(commission_mtd, 2),
        "audits_due_90d": audits_due,
        "rebates_accrued": round(sum(rebates.mapped("amount")), 2),
    }


class P03PartnerApi(http.Controller):
    @http.route("/p03/partner/kpis", type="jsonrpc", auth="user", readonly=True)
    def partner_kpis(self, module=None, **kw):
        _require_internal(request.env)
        return {"M40": kpis(request.env)}
