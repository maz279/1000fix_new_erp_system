# A04 · M40 Partner & Channel — surfaces, report packs and KPIs over the real
# fix.partner (8) / fix.referral (7) and the new authorisation, deal, rebate,
# franchise and conflict models. Partner revenue is the referral commission
# actually recorded; no revenue is attributed without a ledger line.
# Co-marketing (a declared gap until 12 Nov 2026) is built from the campaign's
# co-marketing partners (fix.campaign.partner_ids), the MDF's campaign key
# (fix.partner.rebate.campaign_id) and the M35 touch attribution.
import datetime
import logging

from odoo import fields, http
from odoo.http import request

from ..p03_service_order_api import _company_domain, _require_internal
from ._scope import scoped

_logger = logging.getLogger(__name__)
# A04 ERP audit M40-F22: the standings in which a partner is active.
ACTIVE_STATES = ("onboarded", "probation")

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
            # M40 capture audit (19 Nov 2026)
            "action_generate_onboarding",
            "action_change_tier",
            # A04 ERP audit (20 Nov 2026) M40-F24: the spec's standings
            "action_probation",
            "action_end_probation",
            "action_reactivate",
            "action_start_exit",
            "action_complete_exit",
        },
    },
    # A04 ERP audit M40-F5: a proposed commission rate, applied from the M63
    # inbox (never by a button here).
    "fix.partner.rate.change": {
        "order": "id desc",
        "limit": 300,
        "actions": {"action_request_approval", "action_recall_approval", "action_cancel"},
    },
    # A04 ERP audit M40-F16: the draws of a reseller allocation (read only).
    "fix.reseller.draw": {
        "order": "allocation_id, sequence",
        "limit": 300,
        "actions": set(),
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
    },  # M40 capture audit (19 Nov 2026): the registers each sub-module page
    # captures (programme, onboarding, brand governance, alliance, referral,
    # precedence, reseller, franchise territory/royalty, MDF).
    "fix.partner.programme": {
        "order": "code, version desc",
        "limit": 300,
        "actions": {"action_new_version", "action_publish", "action_retire"},
    },
    "fix.partner.tier": {
        "order": "programme_id, sequence, id",
        "limit": 300,
        "actions": set(),
    },
    "fix.partner.contact.role": {
        "order": "partner_id, role, id",
        "limit": 300,
        "actions": set(),
    },
    "fix.partner.onboarding": {
        "order": "partner_id, sequence, id",
        "limit": 300,
        "actions": {"action_complete", "action_waive"},
    },
    "fix.partner.enablement": {
        "order": "partner_id, expires_on, id",
        "limit": 300,
        "actions": {"action_certify"},
    },
    "fix.brand.obligation": {
        "order": "due_date, id",
        "limit": 300,
        "actions": {"action_mark_met"},
    },
    "fix.brand.audit": {
        "order": "scheduled_on desc, id desc",
        "limit": 300,
        "actions": {"action_close", "action_record_findings", "action_respond"},
    },
    "fix.partner.engagement": {
        "order": "date desc, id desc",
        "limit": 300,
        "actions": set(),
    },
    "fix.alliance.scheme": {
        "order": "valid_from desc, id desc",
        "limit": 300,
        "actions": {"action_activate", "action_close"},
    },
    "fix.alliance.eligibility.check": {
        "order": "checked_at desc, id desc",
        "limit": 300,
        "actions": set(),
    },
    "fix.referral.link": {
        "order": "id desc",
        "limit": 300,
        "actions": {"action_revoke"},
    },
    "fix.partner.lead": {
        "order": "id desc",
        "limit": 300,
        "actions": {"action_convert", "action_mark_lost", "action_qualify"},
    },
    "fix.channel.conflict.rule": {
        "order": "territory, valid_from desc, id desc",
        "limit": 300,
        "actions": {"action_activate", "action_retire"},
    },
    "fix.reseller.allocation": {
        "order": "id desc",
        "limit": 300,
        "actions": {"action_allocate", "action_close", "action_record_draw"},
    },
    "fix.franchise.territory": {
        "order": "code, id",
        "limit": 300,
        "actions": {"action_activate", "action_retire"},
    },
    "fix.franchise.royalty": {
        "order": "period_from desc, id desc",
        "limit": 300,
        "actions": {"action_compute", "action_raise_invoice"},
    },
    "fix.mdf.fund": {
        "order": "id desc",
        "limit": 300,
        "actions": {"action_close", "action_open"},
    },
    "fix.mdf.claim": {
        "order": "id desc",
        "limit": 300,
        "actions": {"action_approve", "action_record_payment", "action_refuse", "action_submit"},
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


def _partners(env, active_only=False):
    domain = [("state", "in", ACTIVE_STATES)] if active_only else []
    return scoped(env, "fix.partner", domain, order="name")


def _today(env):
    return fields.Date.context_today(env.user)


def brand_partners(env, date_from=None, date_to=None, **params):
    """A04 ERP audit M40-F22: one row per BRAND PARTNER (fix.partner of type
    brand), with its authorisations - not a count of authorisations."""
    partners = scoped(env, "fix.partner", [("partner_type", "=", "brand")], order="name")
    auths = scoped(
        env,
        "fix.partner.authorisation",
        [("partner_id", "in", partners.ids)],
        "valid_to",
        date_from,
        date_to,
    )
    rows = []
    for partner in partners:
        mine = auths.filtered(lambda a, pid=partner.id: a.partner_id.id == pid)
        active = mine.filtered(lambda a: a.state == "active")
        rows.append(
            {
                "partner": partner.name,
                "brand": partner.brand_id.name if partner.brand_id else "—",
                "state": partner.state,
                "authorisations": len(mine),
                "active": len(active),
                "next_expiry": str(min(active.mapped("valid_to"))) if active else "—",
            }
        )
    return _pack(
        "Brand Partner Relations",
        ["partner", "brand", "state", "authorisations", "active", "next_expiry"],
        {
            "partner": "Brand Partner",
            "brand": "Brand (M37)",
            "state": "Standing",
            "authorisations": "Authorisations (period)",
            "active": "Active",
            "next_expiry": "Next Expiry",
        },
        rows,
        [
            "One row per brand partner; the authorisations counted are those whose validity "
            "ends in the requested period."
        ],
        empty="No brand partners recorded yet.",
    )


def brand_audit_calendar(env, date_from=None, date_to=None, **params):
    """A04 ERP audit M40-F22: the calendar is the brand audits scheduled in the
    period (fix.brand.audit) AND the authorisations expiring in it (180 days
    ahead when no period is given), not the expiries alone."""
    today = _today(env)
    start = date_from or today
    end = date_to or (today + datetime.timedelta(days=180))
    rows = []
    for audit in scoped(
        env,
        "fix.brand.audit",
        [("state", "!=", "closed")],
        "scheduled_on",
        start,
        end,
        company_field="__none__",
    ):
        rows.append(
            {
                "kind": "Brand audit",
                "partner": audit.authorisation_id.partner_id.name or "—",
                "brand": audit.brand_id.name or "—",
                "date": str(audit.scheduled_on),
                "days_left": (audit.scheduled_on - today).days,
                "state": audit.state,
            }
        )
    for auth in scoped(
        env, "fix.partner.authorisation", [("state", "=", "active")], "valid_to", start, end
    ):
        rows.append(
            {
                "kind": "Authorisation expiry",
                "partner": auth.partner_id.name,
                "brand": auth.brand_id.name if auth.brand_id else "—",
                "date": str(auth.valid_to),
                "days_left": (auth.valid_to - today).days,
                "state": auth.state,
            }
        )
    rows.sort(key=lambda r: r["days_left"])
    return _pack(
        "Brand Audit Calendar — audits and expiries %s to %s" % (start, end),
        ["kind", "partner", "brand", "date", "days_left", "state"],
        {
            "kind": "Event",
            "partner": "Partner",
            "brand": "Brand",
            "date": "Date",
            "days_left": "Days Left",
            "state": "State",
        },
        rows,
        [
            "Scheduled brand audits (FR-PCM-016) and authorisation expiries in the period; "
            "expiries escalate at T-180, T-90 and T-30 days (AUT-PCM-04)."
        ],
        empty="No brand audit or authorisation expiry in the period.",
    )


# A04 ERP audit M40-F14 follow-up (AUT-PCM-04): the escalation bands of a
# brand authorisation, from the model's own thresholds (180 / 90 / 30 days).
def _escalation_band(days_left):
    from odoo.addons.cd_partner.models.fix_partner_ops import AUTHORISATION_WARNINGS

    if days_left < 0:
        return "Lapsed"
    due = [d for d, _g in AUTHORISATION_WARNINGS if days_left <= d]
    return "T-%d" % min(due) if due else "Later"


def authorisations_expiring(env, date_from=None, date_to=None, **params):
    """A04 ERP audit M40-F14 follow-up: every active brand authorisation
    whose validity ends in the period (today to T-180 when no period is
    given), with its escalation band, the threshold already escalated and
    whether brand work on it would still pass the BRU-PCM-08 gate. Read
    through _scope: the caller's companies and the period on valid_to."""
    today = _today(env)
    start = date_from or today
    end = date_to or (today + datetime.timedelta(days=180))
    auths = scoped(
        env,
        "fix.partner.authorisation",
        [("state", "=", "active")],
        "valid_to",
        start,
        end,
        order="valid_to, id",
    )
    rows = []
    for auth in auths:
        days_left = (auth.valid_to - today).days
        rows.append(
            {
                "authorisation": auth.name,
                "partner": auth.partner_id.name,
                "brand": auth.brand_id.name if auth.brand_id else "—",
                "valid_to": str(auth.valid_to),
                "days_left": days_left,
                "band": _escalation_band(days_left),
                "escalated": ("T-%d" % auth.expiry_warned_days)
                if auth.expiry_warned_days
                else "Not yet",
                "partner_state": auth.partner_id.state,
            }
        )
    counts = {}
    for row in rows:
        counts[row["band"]] = counts.get(row["band"], 0) + 1
    return _pack(
        "Authorisations Expiring — %s to %s" % (start, end),
        [
            "authorisation",
            "partner",
            "brand",
            "valid_to",
            "days_left",
            "band",
            "escalated",
            "partner_state",
        ],
        {
            "authorisation": "Authorisation",
            "partner": "Partner",
            "brand": "Brand (M37)",
            "valid_to": "Valid To",
            "days_left": "Days Left",
            "band": "Escalation Band",
            "escalated": "Escalated At",
            "partner_state": "Partner Standing",
        },
        rows,
        [
            "Active brand authorisations whose validity ends in the period. They escalate at "
            "T-180 (channel managers), T-90 (DOFA Tier 3) and T-30 (DOFA Tier 5) days "
            "(AUT-PCM-04); once lapsed, brand work on them is refused (BRU-PCM-08).",
            "By band: %s."
            % (", ".join("%s %d" % (k, counts[k]) for k in sorted(counts)) if counts else "none"),
        ],
        empty="No active brand authorisation expires in the period.",
    )


def referral_conversion(env, date_from=None, date_to=None, **params):
    referrals = scoped(env, "fix.referral", None, "referred_on", date_from, date_to)
    states = {}
    for ref in referrals:
        state = ref.state or "unknown"
        row = states.setdefault(
            state, {"state": state, "referrals": 0, "revenue": 0.0, "commission": 0.0}
        )
        row["referrals"] += 1
        row["revenue"] += ref.base_amount or 0.0
        row["commission"] += ref.commission_amount or 0.0
    rows = []
    for row in states.values():
        row["revenue"] = round(row["revenue"], 2)
        row["commission"] = round(row["commission"], 2)
        rows.append(row)
    rows.sort(key=lambda r: -r["referrals"])
    return _pack(
        "Referral Conversion",
        ["state", "referrals", "revenue", "commission"],
        {
            "state": "Referral State",
            "referrals": "Referrals",
            "revenue": "Referred Revenue",
            "commission": "Commission",
        },
        rows,
        [
            "Referrals dated (referred on) in the period. Referred revenue is the paid M20 "
            "invoice the referral converted on; commission is what it earned."
        ],
        totals={
            "state": "Total",
            "referrals": len(referrals),
            "revenue": round(sum(r["revenue"] for r in rows), 2),
            "commission": round(sum(r["commission"] for r in rows), 2),
        }
        if rows
        else None,
        empty="No partner referrals in the period.",
    )


def partner_revenue(env, date_from=None, date_to=None, **params):
    """A04 ERP audit M40-F22: partner REVENUE is the referred revenue (the
    paid invoices referrals converted on) and won deal value - the commission
    is shown beside it as the cost of that revenue, not as the revenue."""
    referrals = scoped(env, "fix.referral", None, "referred_on", date_from, date_to)
    deals = scoped(env, "fix.partner.deal", None, "registered_on", date_from, date_to)
    rows = []
    for partner in _partners(env):
        partner_refs = referrals.filtered(lambda r, pid=partner.id: r.partner_id.id == pid)
        partner_deals = deals.filtered(lambda d, pid=partner.id: d.partner_id.id == pid)
        if not partner_refs and not partner_deals:
            continue
        rows.append(
            {
                "partner": partner.name,
                "type": partner.partner_type,
                "referrals": len(partner_refs),
                "referred_revenue": round(sum(partner_refs.mapped("base_amount")), 2),
                "commission": round(sum(partner_refs.mapped("commission_amount")), 2),
                "deals_won": round(
                    sum((d.value or 0.0) for d in partner_deals if d.state == "won"), 2
                ),
            }
        )
    rows.sort(key=lambda r: -(r["referred_revenue"] + r["deals_won"]))
    return _pack(
        "Partner Revenue Contribution",
        ["partner", "type", "referrals", "referred_revenue", "commission", "deals_won"],
        {
            "partner": "Partner",
            "type": "Type",
            "referrals": "Referrals",
            "referred_revenue": "Referred Revenue",
            "commission": "Commission (cost)",
            "deals_won": "Deals Won Value",
        },
        rows,
        [
            "Referred revenue = the paid M20 invoices the period's referrals converted on; "
            "commission is the expense of it; deal value is the won registrations' own amount."
        ],
        totals={
            "partner": "Total",
            "referrals": sum(r["referrals"] for r in rows),
            "referred_revenue": round(sum(r["referred_revenue"] for r in rows), 2),
            "commission": round(sum(r["commission"] for r in rows), 2),
            "deals_won": round(sum(r["deals_won"] for r in rows), 2),
        }
        if rows
        else None,
        empty="No partner activity in the period.",
    )


def rebate_accruals(env, date_from=None, date_to=None, **params):
    rebates = scoped(env, "fix.partner.rebate", None, "accrued_at", date_from, date_to)
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
        [
            "Rebates accrued in the period. Basis = the partner's paid M20 invoices of the "
            "rebate period (ex-VAT, net of credit notes); amount = basis × rate. Accrued: %s."
            % round(accrued, 2)
        ],
        totals={"rebate": "Total", "amount": round(sum(r["amount"] for r in rows), 2)}
        if rows
        else None,
        empty="No rebates accrued in the period.",
    )


def conflict_log(env, date_from=None, date_to=None, **params):
    conflicts = scoped(env, "fix.partner.conflict", None, "create_date", date_from, date_to)
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
        ["Conflicts raised in the period and their DOFA ruling."],
        empty="No channel conflicts in the period.",
    )


def alliance_report(env, date_from=None, date_to=None, **params):
    partners = scoped(env, "fix.partner", [("partner_type", "=", "alliance")], order="name")
    schemes = scoped(
        env,
        "fix.alliance.scheme",
        [("partner_id", "in", partners.ids)],
        "valid_from",
        None,
        date_to,
    )
    rows = []
    for partner in partners:
        mine = schemes.filtered(lambda sc, pid=partner.id: sc.partner_id.id == pid)
        rows.append(
            {
                "partner": partner.name,
                "territory": partner.territory or "—",
                "commission": round((partner.commission_rate or 0.0) * 100.0, 2),
                "schemes": len(mine.filtered(lambda sc: sc.state == "active")),
                "state": partner.state,
            }
        )
    return _pack(
        "Alliance Benefits — strategic alliance partners",
        ["partner", "territory", "commission", "schemes", "state"],
        {
            "partner": "Partner",
            "territory": "Territory",
            "commission": "Commission %",
            "schemes": "Active Schemes",
            "state": "State",
        },
        rows,
        ["Alliance partners, their approved commission rate and their active schemes."],
        empty="No strategic alliance partners yet.",
    )


def reseller_report(env, date_from=None, date_to=None, **params):
    partners = scoped(env, "fix.partner", [("partner_type", "=", "reseller")], order="name")
    deals = scoped(env, "fix.partner.deal", None, "registered_on", date_from, date_to)
    draws = scoped(env, "fix.reseller.draw", None, "create_date", date_from, date_to)
    rows = []
    for partner in partners:
        mine = deals.filtered(lambda d, pid=partner.id: d.partner_id.id == pid)
        drawn = draws.filtered(lambda d, pid=partner.id: d.partner_id.id == pid)
        rows.append(
            {
                "partner": partner.name,
                "territory": partner.territory or "—",
                "deals": len(mine),
                "won_value": round(sum((d.value or 0.0) for d in mine if d.state == "won"), 2),
                "drawn_value": round(sum(d.qty * d.unit_price for d in drawn), 2),
                "state": partner.state,
            }
        )
    rows.sort(key=lambda r: -(r["won_value"] + r["drawn_value"]))
    return _pack(
        "Resellers",
        ["partner", "territory", "deals", "won_value", "drawn_value", "state"],
        {
            "partner": "Reseller",
            "territory": "Territory",
            "deals": "Deals",
            "won_value": "Won Value",
            "drawn_value": "Drawn (M11 price)",
            "state": "State",
        },
        rows,
        ["Resellers with the period's registered deals and their draws at the M11 price."],
        empty="No reseller partners yet.",
    )


ATTRIBUTION_MODELS = ["position", "last_touch", "first_touch", "linear", "time_decay"]
_MDF_BUCKETS = {
    "draft": "mdf_planned",
    "accrued": "mdf_accrued",
    "approved": "mdf_approved",
    "paid": "mdf_paid",
}
# A04 ERP audit M40-F26: an MDF claim's state in the same buckets (a claim
# under evidence review is the claimed, accrued-to-be amount).
_CLAIM_BUCKETS = {
    "draft": "mdf_planned",
    "submitted": "mdf_accrued",
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
    # A04 ERP audit M40-F26: the MDF is an evidenced claim on the partner's
    # fund now; the legacy MDF rebates above keep their history.
    claims = env["fix.mdf.claim"].search(
        [
            *_company_domain(env, "fix.mdf.claim"),
            ("campaign_id", "in", campaigns.ids),
            ("state", "in", tuple(_CLAIM_BUCKETS)),
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
        for claim in claims.filtered(lambda r, pid=partner.id: r.partner_id.id == pid):
            row[_CLAIM_BUCKETS[claim.state]] += claim.amount or 0.0
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
    ) + env["fix.mdf.claim"].search_count(
        [
            *_company_domain(env, "fix.mdf.claim"),
            ("campaign_id", "=", False),
            ("state", "in", tuple(_CLAIM_BUCKETS)),
        ]
    )
    notes = [
        "Campaigns are the M35 campaigns that name the partner as a co-marketing partner; "
        "MDF is the partner's MDF claims on those campaigns by state (planned = draft claim, "
        "accrued = under evidence review, approved = payment instructed, paid; a refused "
        "claim is left out), plus MDF raised as a rebate before 21 Nov 2026.",
        "Attributed revenue is the %s attribution of the M35 touch ledger, counted only "
        "where every credited conversion of the campaign has its value on file. It is the "
        "co-funded campaigns' revenue, not a partner share: a campaign co-funded by two "
        "partners shows under both, and the total counts it once." % model,
    ]
    if unlinked:
        notes.append(
            "%d MDF claim(s) or legacy MDF accrual(s) name no campaign and are not shown here "
            "(see MDF Claims and Rebate Accruals)." % unlinked
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


# A04 ERP audit M40-F22 (FR-PCM-018, T-08, BRU-PCM-18): the health score
# decomposes into named factors with their weights. Equal weights over the
# factors that have data are an OWNER default until the CCO rules them.
HEALTH_FACTORS = [
    ("audit", "Technical audit"),
    ("obligations", "Obligation compliance"),
    ("brand_audit", "Brand audit findings"),
    ("claims", "Claim performance (M09)"),
    ("volume", "Volume trend"),
    ("engagement", "Contact engagement"),
]


def _health_factors(env, partner, start, end):
    """{factor: 0..100 or None (no data)} for one partner over [start, end]."""
    span = max((end - start).days, 1)
    prev_start = start - datetime.timedelta(days=span)
    out = dict.fromkeys(k for k, _l in HEALTH_FACTORS)
    out["audit"] = partner.technical_audit_score if partner.technical_audit_id else None
    obligations = (
        env["fix.brand.obligation"]
        .sudo()
        .search([("partner_id", "=", partner.id), ("due_date", "<=", end), ("state", "!=", "open")])
    )
    if obligations:
        out["obligations"] = (
            100.0 * len(obligations.filtered(lambda o: o.state == "met")) / len(obligations)
        )
    if partner.brand_id:
        audits = (
            env["fix.brand.audit"]
            .sudo()
            .search(
                [
                    ("brand_id", "=", partner.brand_id.id),
                    ("state", "in", ("conducted", "responded", "closed")),
                    ("scheduled_on", ">=", start),
                    ("scheduled_on", "<=", end),
                ]
            )
        )
        if audits:
            clean = audits.filtered(lambda a: not (a.findings or "").strip())
            out["brand_audit"] = 100.0 * len(clean) / len(audits)
        if "fix.warranty.claim" in env:
            Claim = env["fix.warranty.claim"].sudo()
            decided = Claim.search(
                [
                    ("brand_id", "=", partner.brand_id.id),
                    ("state", "in", ("approved", "partially_approved", "rejected")),
                    ("create_date", ">=", fields.Datetime.to_datetime(start)),
                    (
                        "create_date",
                        "<",
                        fields.Datetime.to_datetime(end) + datetime.timedelta(days=1),
                    ),
                ]
            )
            if decided:
                approved = decided.filtered(lambda c: c.state != "rejected")
                out["claims"] = 100.0 * len(approved) / len(decided)

    def _volume(a, b):
        return env["fix.referral"].sudo().search_count(
            [("partner_id", "=", partner.id), ("referred_on", ">=", a), ("referred_on", "<=", b)]
        ) + env["fix.partner.deal"].sudo().search_count(
            [
                ("partner_id", "=", partner.id),
                ("registered_on", ">=", a),
                ("registered_on", "<=", b),
            ]
        )

    now, before = _volume(start, end), _volume(prev_start, start - datetime.timedelta(days=1))
    if now or before:
        out["volume"] = 100.0 if now >= before else 100.0 * now / before
    engaged = (
        env["fix.partner.engagement"]
        .sudo()
        .search_count([("partner_id", "=", partner.id), ("date", ">=", start), ("date", "<=", end)])
    )
    out["engagement"] = 100.0 if engaged else 0.0
    return out


def health(env, date_from=None, date_to=None, **params):
    today = _today(env)
    end = fields.Date.to_date(date_to) if date_to else today
    start = fields.Date.to_date(date_from) if date_from else end - datetime.timedelta(days=90)
    rows = []
    for partner in _partners(env, active_only=True):
        factors = _health_factors(env, partner, start, end)
        known = {k: v for k, v in factors.items() if v is not None}
        weight = round(100.0 / len(known), 2) if known else 0.0
        score = round(sum(known.values()) / len(known), 1) if known else None
        row = {
            "partner": partner.name,
            "type": partner.partner_type,
            "score": score if score is not None else "—",
            "health": "no data"
            if score is None
            else ("healthy" if score >= 75 else ("watch" if score >= 50 else "at risk")),
            "weights": ", ".join("%s %.0f%%" % (k, weight) for k in known) or "—",
        }
        for key, _label in HEALTH_FACTORS:
            row[key] = round(factors[key], 1) if factors[key] is not None else "—"
        rows.append(row)
    rows.sort(key=lambda r: (r["score"] if isinstance(r["score"], float) else 999))
    labels = {
        "partner": "Partner",
        "type": "Type",
        "score": "Health Score",
        "health": "Band",
        "weights": "Weights Applied",
    }
    labels.update(dict(HEALTH_FACTORS))
    return _pack(
        "Health & Risk — %s to %s" % (start, end),
        ["partner", "type", *[k for k, _l in HEALTH_FACTORS], "weights", "score", "health"],
        labels,
        rows[:200],
        [
            "FR-PCM-018: each factor is 0-100 from source data - technical audit score; "
            "obligations met of those due; brand audits without findings; M09 claims approved "
            "of those decided (brand partners); referrals + deals against the previous period "
            "of equal length; engagement logged in the period. Quality (M23) has no per-partner "
            "measure yet and is not counted.",
            "Score = the weighted mean of the factors with data, equal weights (an owner "
            "default until the CCO rules the weights); bands 75 / 50.",
        ],
        empty="No active partners.",
    )


def ranking(env, date_from=None, date_to=None, **params):
    pack = partner_revenue(env, date_from=date_from, date_to=date_to)
    rows = []
    for rank, row in enumerate(pack["rows"], start=1):
        rows.append(
            {
                "rank": rank,
                "partner": row["partner"],
                "type": row["type"],
                "referred_revenue": row["referred_revenue"],
                "deals_won": row["deals_won"],
            }
        )
    return _pack(
        "Ranking & Scorecards",
        ["rank", "partner", "type", "referred_revenue", "deals_won"],
        {
            "rank": "Rank",
            "partner": "Partner",
            "type": "Type",
            "referred_revenue": "Referred Revenue",
            "deals_won": "Deals Won Value",
        },
        rows[:100],
        [
            "Ranking = referred revenue + won deal value in the period, descending. "
            "Tie-break is the partner name."
        ],
        empty="No partner activity to rank in the period.",
    )


def deal_register(env, date_from=None, date_to=None, **params):
    deals = scoped(env, "fix.partner.deal", None, "registered_on", date_from, date_to)
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
    franchises = scoped(env, "fix.partner.franchise", None, "start_date", None, date_to)
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
    "authorisations_expiring": authorisations_expiring,
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
    """A04 ERP audit M40-F21/F22: company-scoped, and each figure measures
    what its label says. A failing figure is logged and shown as None."""
    today = _today(env)
    month_start = today.replace(day=1)
    horizon = today + datetime.timedelta(days=90)
    out = {}

    def _kpi(key, fn):
        try:
            out[key] = fn()
        except Exception:  # a KPI never takes the workspace down, but it is logged
            _logger.exception("M40 KPI %s failed", key)
            out[key] = None

    active = [("state", "in", ACTIVE_STATES)]
    _kpi(
        "brand_partners",
        lambda: len(scoped(env, "fix.partner", [("partner_type", "=", "brand"), *active])),
    )
    _kpi(
        "referral_partners",
        lambda: len(scoped(env, "fix.partner", [("partner_type", "=", "referral"), *active])),
    )
    _kpi(
        "deal_registrations",
        lambda: len(
            scoped(
                env, "fix.partner.deal", [("state", "in", ("registered", "conflict", "approved"))]
            )
        ),
    )
    _kpi(
        "partner_revenue_mtd",
        lambda: round(
            sum(
                scoped(
                    env,
                    "fix.referral",
                    [("state", "in", ("converted", "commissioned"))],
                    "referred_on",
                    month_start,
                    today,
                ).mapped("base_amount")
            ),
            2,
        ),
    )
    _kpi(
        "audits_due_90d",
        lambda: len(
            scoped(
                env,
                "fix.partner.authorisation",
                [("state", "=", "active")],
                "valid_to",
                today,
                horizon,
            )
        )
        + len(
            scoped(
                env,
                "fix.brand.audit",
                [("state", "=", "scheduled")],
                "scheduled_on",
                today,
                horizon,
                company_field="__none__",
            )
        ),
    )
    _kpi(
        "rebates_accrued",
        lambda: round(
            sum(scoped(env, "fix.partner.rebate", [("state", "=", "accrued")]).mapped("amount")), 2
        ),
    )
    return out


class P03PartnerApi(http.Controller):
    @http.route("/p03/partner/kpis", type="jsonrpc", auth="user", readonly=True)
    def partner_kpis(self, module=None, **kw):
        _require_internal(request.env)
        return {"M40": kpis(request.env)}
