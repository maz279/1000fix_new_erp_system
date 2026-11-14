# A03 · M35 Marketing Campaigns — surfaces, report packs and KPIs over the
# real fix.campaign / fix.campaign.response records and the new campaign
# operations models. Funnel counts are measured; attributed revenue is a
# declared gap (no order-value key on the response record) and is never
# estimated.
import datetime

from odoo import http
from odoo.http import request

from ..p03_service_order_api import _require_internal

SURFACES = {
    "fix.campaign": {
        "order": "start_date desc, id desc",
        "limit": 200,
        # the lifecycle engine acts from the grid: budget DOFA approval and the
        # FLAW-35.1/35.2 launch gate fire from these actions
        "actions": {
            # R7: the budget is decided from the M63 inbox.
            "action_request_approval",
            "action_recall_approval",
            # A03 audit G-M35-8: the BTRC DND scrub had no screen, so no SMS
            # campaign could pass the launch gate through the workspace.
            "action_scrub_dnd",
            "action_launch",
            "action_pause",
            "action_resume",
            "action_complete",
            # capture audit 2026-11-14: post-suppression reach (BRU-MKT-03)
            "action_estimate_audience",
        },
    },
    "fix.campaign.response": {
        "order": "responded_at desc, id desc",
        "limit": 300,
        "actions": set(),
    },
    "fix.campaign.journey": {
        "order": "name",
        "limit": 200,
        # A03 audit G-M35-8: journeys could be authored but never started.
        "actions": {"action_activate", "action_pause_journey", "action_resume_journey"},
    },
    "fix.campaign.trigger": {
        "order": "name",
        "limit": 200,
        "actions": set(),
    },
    "fix.campaign.offer": {
        "order": "name",
        "limit": 200,
        "actions": set(),
    },
    "fix.campaign.creative": {
        "order": "name",
        "limit": 200,
        # A03 audit G-M35-10: content approval is routed through M63; the
        # approver decides from the inbox, so there is no Approve here.
        "actions": {
            "action_request_approval",
            "action_recall_approval",
            "action_withdraw",
            "action_retire",
            "action_reset_to_draft",
        },
    },
    "fix.campaign.ad": {
        "order": "name",
        "limit": 200,
        "actions": set(),
    },
    "fix.campaign.experiment": {
        "order": "name",
        "limit": 200,
        # capture audit 2026-11-14: the state and winner move only through these
        "actions": {"action_start", "action_conclude"},
    },
    # capture audit 2026-11-14: spend booked outside the estate (BRU-MKT-11)
    # and the versioned attribution model (BRU-MKT-12).
    "fix.campaign.spend": {
        "order": "spend_date desc, id desc",
        "limit": 300,
        "actions": {"action_void"},
    },
    "fix.attribution.model": {
        "order": "code, version desc",
        "limit": 200,
        "actions": {"action_activate"},
    },
    # --- added by the A03 gap-closure build -------------------
    # Each of these is bound by a workspace screen below; an
    # unservable surface is what test_a03_registry_coverage exists
    # to catch, and a surface no screen opens is dead weight it
    # also catches.
    "fix.campaign.journey.step": {
        "order": "journey_id, sequence, id",
        "limit": 300,
        "actions": set(),
    },
    "fix.campaign.journey.member": {
        "order": "next_action_at, id",
        "limit": 300,
        "actions": {"action_pause_member", "action_resume_member"},
    },
    "fix.campaign.touch": {
        "order": "occurred_at desc, id desc",
        "limit": 300,
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


def _campaigns(env):
    return env["fix.campaign"].sudo().search([])


def _responses(env):
    return env["fix.campaign.response"].sudo().search([])


def campaign_funnel(env, date_from=None, date_to=None, **params):
    rows = []
    for c in _campaigns(env):
        responses = _responses(env).filtered(lambda r, cid=c.id: r.campaign_id.id == cid)
        converted = len(responses.filtered(lambda r: r.conversion_status == "converted"))
        recipients = c.recipient_count or 0
        rows.append(
            {
                "campaign": c.name,
                "channel": c.channel,
                "recipients": recipients,
                "responses": len(responses),
                "converted": converted,
                "response_pct": round(len(responses) / recipients * 100.0, 1)
                if recipients
                else 0.0,
                "conversion_pct": round(converted / len(responses) * 100.0, 1)
                if responses
                else 0.0,
            }
        )
    rows.sort(key=lambda r: -r["responses"])
    totals = {
        "campaign": "Total",
        "recipients": sum(r["recipients"] for r in rows),
        "responses": sum(r["responses"] for r in rows),
        "converted": sum(r["converted"] for r in rows),
    }
    return _pack(
        "Campaign Funnel by Channel",
        [
            "campaign",
            "channel",
            "recipients",
            "responses",
            "converted",
            "response_pct",
            "conversion_pct",
        ],
        {
            "campaign": "Campaign",
            "channel": "Channel",
            "recipients": "Recipients",
            "responses": "Responses",
            "converted": "Converted",
            "response_pct": "Response %",
            "conversion_pct": "Conversion %",
        },
        rows,
        [
            "Recipients is the campaign's consent-safe recipient count; responses are "
            "fix.campaign.response rows; converted means conversion_status=converted."
        ],
        totals=totals if rows else None,
        empty="No campaigns yet.",
    )


def _model_in_force(env):
    """The attribution model in force, or None when none has been put in force."""
    Model = env.get("fix.attribution.model")
    return Model.sudo()._current() if Model is not None else None


def attribution_roi(env, date_from=None, date_to=None, **params):
    """Spend against responses, plus what the touch ledger credits to each
    campaign under the attribution model that applies to it: the one pinned
    when it completed, else the one in force (BRU-MKT-12)."""
    Touch = env.get("fix.campaign.touch")
    current = _model_in_force(env)
    credited = {}

    def credit(model):
        method = model.method if model else "position"
        lookback = model.lookback_days if model else 90
        if (method, lookback) not in credited:
            result = (
                Touch.attribute(model=method, lookback_days=lookback)
                if Touch is not None
                else {"rows": []}
            )
            credited[(method, lookback)] = {r["campaign_id"]: r for r in result["rows"]}
        return credited[(method, lookback)]

    rows = []
    for c in _campaigns(env):
        responses = _responses(env).filtered(lambda r, cid=c.id: r.campaign_id.id == cid)
        converted = len(responses.filtered(lambda r: r.conversion_status == "converted"))
        pinned = c.attribution_model_id if "attribution_model_id" in c._fields else None
        model = pinned or current
        hit = credit(model).get(c.id, {})
        conversions = hit.get("attributed_conversions", 0.0)
        complete = bool(conversions) and not hit.get("conversions_without_value")
        revenue = round(hit.get("attributed_revenue", 0.0), 2) if complete else None
        spend = round(c.actual_spend, 2)
        rows.append(
            {
                "campaign": c.name,
                "model": model.display_label if model else "Position-based (no model in force)",
                "budget": round(c.budget, 2),
                "actual_spend": spend,
                "responses": len(responses),
                "converted": converted,
                "attributed_conversions": round(conversions, 2),
                "attributed_revenue": revenue,
                "roi": round(revenue / spend, 2) if revenue is not None and spend else None,
                "cost_per_response": round(c.cost_per_response, 2),
                "cost_per_conversion": round(c.budget / converted, 2) if converted else 0.0,
            }
        )
    rows.sort(key=lambda r: -r["budget"])
    totals = {
        "campaign": "Total",
        "budget": round(sum(r["budget"] for r in rows), 2),
        "actual_spend": round(sum(r["actual_spend"] for r in rows), 2),
        "responses": sum(r["responses"] for r in rows),
        "converted": sum(r["converted"] for r in rows),
        "attributed_conversions": round(sum(r["attributed_conversions"] for r in rows), 2),
    }
    return _pack(
        "Attribution & ROI — spend against what each campaign is credited with",
        [
            "campaign",
            "model",
            "budget",
            "actual_spend",
            "responses",
            "converted",
            "attributed_conversions",
            "attributed_revenue",
            "roi",
            "cost_per_response",
            "cost_per_conversion",
        ],
        {
            "campaign": "Campaign",
            "model": "Attribution Model",
            "budget": "Budget",
            "actual_spend": "Recorded Spend",
            "responses": "Responses",
            "converted": "Converted",
            "attributed_conversions": "Credited Conversions",
            "attributed_revenue": "Credited Revenue",
            "roi": "Return on Spend",
            "cost_per_response": "Cost per Response",
            "cost_per_conversion": "Cost per Conversion",
        },
        rows,
        [
            "Credit is shared across the campaigns that reached a customer before they "
            "converted, by the attribution model shown. A completed campaign keeps the "
            "model that was in force when it closed; a later model does not restate it.",
            "Credited revenue and return on spend are shown only where every credited "
            "conversion has a value on file. Otherwise they read as a dash: a share of an "
            "unknown total is still unknown.",
            "Recorded spend is message cost, offer discounts given and the spend recorded "
            "against the campaign (media, print, agency).",
        ],
        totals=totals if rows else None,
        empty="No campaigns yet.",
    )


def seasonal_performance(env, date_from=None, date_to=None, **params):
    buckets = {}
    for c in _campaigns(env):
        month = c.start_date.strftime("%Y-%m") if c.start_date else "undated"
        row = buckets.setdefault(
            month, {"month": month, "campaigns": 0, "responses": 0, "converted": 0}
        )
        responses = _responses(env).filtered(lambda r, cid=c.id: r.campaign_id.id == cid)
        row["campaigns"] += 1
        row["responses"] += len(responses)
        row["converted"] += len(responses.filtered(lambda r: r.conversion_status == "converted"))
    rows = [buckets[k] for k in sorted(buckets, reverse=True)]
    for row in rows:
        row["conversion_pct"] = (
            round(row["converted"] / row["responses"] * 100.0, 1) if row["responses"] else 0.0
        )
    return _pack(
        "Seasonal Template Performance",
        ["month", "campaigns", "responses", "converted", "conversion_pct"],
        {
            "month": "Start Month",
            "campaigns": "Campaigns",
            "responses": "Responses",
            "converted": "Converted",
            "conversion_pct": "Conversion %",
        },
        rows,
        [
            "Grouped by the campaign's start month — the seasonal pattern the calendar "
            "reveals from real campaigns."
        ],
        empty="No campaigns yet.",
    )


def co_marketing_partner(env, date_from=None, date_to=None, **params):
    """Campaigns run with channel partners (the partners named on the campaign)
    and the market development fund each partner has put against them."""
    Campaign = env["fix.campaign"]
    if "partner_ids" not in Campaign._fields:
        return _pack(
            "Co-Marketing Partner Report",
            ["campaign"],
            {"campaign": "Campaign"},
            [],
            ["The partner programme is not installed, so no campaign can name a partner."],
            empty="No co-marketing campaigns.",
        )
    Rebate = env.get("fix.partner.rebate")
    rows = []
    for c in _campaigns(env).filtered("partner_ids"):
        responses = _responses(env).filtered(lambda r, cid=c.id: r.campaign_id.id == cid)
        funds = (
            Rebate.sudo().search(
                [
                    ("kind", "=", "mdf"),
                    ("campaign_id", "=", c.id),
                    ("state", "in", ("accrued", "approved", "paid")),
                ]
            )
            if Rebate is not None
            else []
        )
        partner_fund = round(sum(f.amount for f in funds), 2)
        rows.append(
            {
                "campaign": c.name,
                "partners": ", ".join(c.partner_ids.mapped("name")),
                "channel": c.channel,
                "budget": round(c.budget, 2),
                "partner_fund": partner_fund,
                "company_share": round(max((c.budget or 0.0) - partner_fund, 0.0), 2),
                "responses": len(responses),
                "converted": len(responses.filtered(lambda r: r.conversion_status == "converted")),
            }
        )
    totals = {
        "campaign": "Total",
        "budget": round(sum(r["budget"] for r in rows), 2),
        "partner_fund": round(sum(r["partner_fund"] for r in rows), 2),
        "responses": sum(r["responses"] for r in rows),
        "converted": sum(r["converted"] for r in rows),
    }
    return _pack(
        "Co-Marketing Partner Report",
        [
            "campaign",
            "partners",
            "channel",
            "budget",
            "partner_fund",
            "company_share",
            "responses",
            "converted",
        ],
        {
            "campaign": "Campaign",
            "partners": "Co-Marketing Partners",
            "channel": "Channel",
            "budget": "Budget",
            "partner_fund": "Partner Fund (accrued, approved or paid)",
            "company_share": "Company Share of Budget",
            "responses": "Responses",
            "converted": "Converted",
        },
        rows,
        [
            "Only campaigns that name a channel partner are shown. The partner fund is "
            "the market development fund the partners have accrued against the campaign; "
            "draft and cancelled funds are not counted."
        ],
        totals=totals if rows else None,
        empty="No campaign names a co-marketing partner yet.",
    )


def lead_to_order(env, date_from=None, date_to=None, **params):
    responses = _responses(env)
    statuses = ["engaged", "converted", "enrolled_loyalty"]
    rows = []
    for status in statuses:
        mine = responses.filtered(lambda r, s=status: r.conversion_status == s)
        rows.append({"status": status, "responses": len(mine)})
    types = {}
    for r in responses:
        types[r.response_type] = types.get(r.response_type, 0) + 1
    for rtype, n in sorted(types.items(), key=lambda kv: -kv[1]):
        rows.append({"status": "type:%s" % rtype, "responses": n})
    total = len(responses)
    converted = len(responses.filtered(lambda r: r.conversion_status == "converted"))
    return _pack(
        "Lead-to-Order Conversion",
        ["status", "responses"],
        {"status": "Outcome / Response Type", "responses": "Responses"},
        rows,
        [
            "Conversion rate: %d of %d responses converted (%.1f%%)."
            % (converted, total, converted / total * 100.0)
            if total
            else "No responses yet."
        ],
        totals={"status": "Total", "responses": total} if rows else None,
        empty="No campaign responses yet.",
    )


def campaign_approval(env, date_from=None, date_to=None, **params):
    rows = []
    for c in _campaigns(env).filtered(lambda x: x.state in ("draft", "paused")):
        rows.append(
            {
                "campaign": c.name,
                "channel": c.channel,
                "state": c.state,
                "budget": round(c.budget, 2),
                "consent_verified": "✓" if c.pdpa_consent_verified else "✗",
                "excluded_no_consent": c.excluded_no_consent_count,
                "estimated_reach": (
                    "%d (%s)" % (c.estimated_reach, c.estimated_at)
                    if getattr(c, "estimated_at", False)
                    else "not estimated"
                ),
                "dnd_scrub": (
                    "%s (%d excluded)" % (c.dnd_scrubbed_at, c.dnd_excluded_count)
                    if c.dnd_scrubbed_at
                    else "not run"
                ),
                "approval": c.approval_state,
                "creatives_waiting": c.creative_unapproved_count,
                "start": str(c.start_date) if c.start_date else "—",
            }
        )
    return _pack(
        "Planning & Approval — campaigns waiting to run",
        [
            "campaign",
            "channel",
            "state",
            "budget",
            "consent_verified",
            "excluded_no_consent",
            "estimated_reach",
            "dnd_scrub",
            "approval",
            "creatives_waiting",
            "start",
        ],
        {
            "campaign": "Campaign",
            "channel": "Channel",
            "state": "State",
            "budget": "Budget",
            "consent_verified": "PDPA Consent Verified",
            "excluded_no_consent": "Excluded (no consent)",
            "estimated_reach": "Estimated Reach (after suppression)",
            "dnd_scrub": "BTRC DND Scrub",
            "approval": "Budget Approval",
            "creatives_waiting": "Creatives Not Approved",
            "start": "Start Date",
        },
        rows,
        [
            "A campaign cannot run until PDPA consent is verified; the excluded count is "
            "the audience deliberately dropped for missing consent. SMS, e-mail and "
            "portal campaigns also need a DND scrub within 24 hours of launch, and every "
            "creative must be approved.",
            "Estimated reach is how many people the campaign would actually reach once "
            "consent, the Do-Not-Disturb registry and the holdout are applied; requesting "
            "budget approval refreshes it.",
        ],
        empty="No campaigns awaiting approval.",
    )


def budget_roi(env, date_from=None, date_to=None, **params):
    pack = attribution_roi(env)
    spend = {c.name: c for c in _campaigns(env)}
    rows = []
    for row in pack["rows"]:
        campaign = spend.get(row["campaign"])
        rows.append(
            {
                "campaign": row["campaign"],
                "budget": row["budget"],
                "actual_spend": round(campaign.actual_spend, 2) if campaign else 0.0,
                "variance": round(campaign.budget_variance, 2) if campaign else 0.0,
                "cost_per_response": row["cost_per_response"],
                "cost_per_conversion": row["cost_per_conversion"],
                "responses": row["responses"],
                "converted": row["converted"],
            }
        )
    return _pack(
        "Budget & ROI",
        [
            "campaign",
            "budget",
            "actual_spend",
            "variance",
            "cost_per_response",
            "cost_per_conversion",
            "responses",
            "converted",
        ],
        {
            "campaign": "Campaign",
            "budget": "Budget",
            "actual_spend": "Recorded Spend",
            "variance": "Budget Remaining",
            "cost_per_response": "Cost / Response",
            "cost_per_conversion": "Cost / Conversion",
            "responses": "Responses",
            "converted": "Converted",
        },
        rows,
        [
            "ROI ratio needs attributed revenue, which the response record does not carry "
            "— cost metrics are shown instead of an invented return.",
            "Recorded spend is the S1 message cost of the campaign's sends plus offer "
            "discounts redeemed; spend booked outside the estate is not on file.",
        ],
        empty="No campaigns yet.",
    )


REPORTS = {
    "campaign_funnel": campaign_funnel,
    "attribution_roi": attribution_roi,
    "seasonal_performance": seasonal_performance,
    "co_marketing_partner": co_marketing_partner,
    "lead_to_order": lead_to_order,
    "campaign_approval": campaign_approval,
    "budget_roi": budget_roi,
}


def _attributed_revenue(env):
    """Conversion value actually on file. A sum, so 0 when none is (None
    only when the touch ledger is not installed).

    A partial total presented as a total is the error this estate's rules
    exist to prevent, so the figure counts only KNOWN values and reads 0
    until there is something real to add up.
    """
    Touch = env.get("fix.campaign.touch")
    if Touch is None:
        return None
    known = Touch.sudo().search([("touch_type", "=", "conversion"), ("value_known", "=", True)])
    return round(sum(known.mapped("value_bdt")), 2)


def kpis(env):
    campaigns = _campaigns(env)
    responses = _responses(env)
    today = datetime.date.today()
    month_start = today.replace(day=1)
    mtd = responses.filtered(lambda r: r.responded_at and r.responded_at.date() >= month_start)
    converted = len(responses.filtered(lambda r: r.conversion_status == "converted"))
    total_budget = sum(campaigns.mapped("budget"))
    recipients = sum(campaigns.mapped("recipient_count"))
    excluded = sum(campaigns.mapped("excluded_no_consent_count"))
    return {
        "active_campaigns": len(campaigns.filtered(lambda c: c.state == "running")),
        "leads_mtd": len(mtd),
        "cac": round(total_budget / converted, 2) if converted else None,
        # PARTLY closed, and the tile says which part. A campaign response
        # still carries no order value -- the stated reason -- so this reads
        # the multi-touch touchpoint ledger and counts only conversions whose
        # value is actually KNOWN. 0 when none are; never an estimate.
        "attributed_revenue": _attributed_revenue(env),
        "open_rate": round(len(responses) / recipients * 100.0, 1) if recipients else None,
        # a count of reachable recipients: 0 when no campaign has any
        "consent_safe_reach": recipients - excluded if recipients else 0,
    }


class P03CampaignApi(http.Controller):
    @http.route("/p03/campaign/kpis", type="jsonrpc", auth="user", readonly=True)
    def campaign_kpis(self, module=None, **kw):
        _require_internal(request.env)
        return {"M35": kpis(request.env)}
