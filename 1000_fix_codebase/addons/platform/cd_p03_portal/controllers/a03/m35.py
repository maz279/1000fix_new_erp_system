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
            "action_approve_budget",
            "action_launch",
            "action_pause",
            "action_resume",
            "action_complete",
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
        "actions": set(),
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
        "actions": set(),
    },
    "fix.campaign.ad": {
        "order": "name",
        "limit": 200,
        "actions": set(),
    },
    "fix.campaign.experiment": {
        "order": "name",
        "limit": 200,
        "actions": set(),
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


def attribution_roi(env, date_from=None, date_to=None, **params):
    rows = []
    for c in _campaigns(env):
        responses = _responses(env).filtered(lambda r, cid=c.id: r.campaign_id.id == cid)
        converted = len(responses.filtered(lambda r: r.conversion_status == "converted"))
        rows.append(
            {
                "campaign": c.name,
                "budget": round(c.budget, 2),
                "responses": len(responses),
                "converted": converted,
                "cost_per_response": round(c.cost_per_response, 2),
                "cost_per_conversion": round(c.budget / converted, 2) if converted else 0.0,
            }
        )
    rows.sort(key=lambda r: -r["budget"])
    totals = {
        "campaign": "Total",
        "budget": round(sum(r["budget"] for r in rows), 2),
        "responses": sum(r["responses"] for r in rows),
        "converted": sum(r["converted"] for r in rows),
    }
    return _pack(
        "Attribution & ROI — spend against responses and conversions",
        [
            "campaign",
            "budget",
            "responses",
            "converted",
            "cost_per_response",
            "cost_per_conversion",
        ],
        {
            "campaign": "Campaign",
            "budget": "Budget",
            "responses": "Responses",
            "converted": "Converted",
            "cost_per_response": "Cost per Response",
            "cost_per_conversion": "Cost per Conversion",
        },
        rows,
        [
            "Attributed REVENUE is a declared gap: the response record carries no order "
            "value, so revenue-per-campaign is not estimated here. Cost metrics are real."
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
    corporate = _campaigns(env).filtered(lambda c: c.target_audience_type == "corporate_amc")
    rows = []
    for c in corporate:
        responses = _responses(env).filtered(lambda r, cid=c.id: r.campaign_id.id == cid)
        rows.append(
            {
                "campaign": c.name,
                "channel": c.channel,
                "responses": len(responses),
                "converted": len(responses.filtered(lambda r: r.conversion_status == "converted")),
            }
        )
    return _pack(
        "Co-Marketing Partner Report",
        ["campaign", "channel", "responses", "converted"],
        {
            "campaign": "Corporate Campaign",
            "channel": "Channel",
            "responses": "Responses",
            "converted": "Converted",
        },
        rows,
        [
            "Only corporate-AMC campaigns are shown. A dedicated co-marketing partner "
            "model (partner share, co-branded budget) does not exist — declared gap."
        ],
        empty="No corporate co-marketing campaigns yet.",
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
            "start",
        ],
        {
            "campaign": "Campaign",
            "channel": "Channel",
            "state": "State",
            "budget": "Budget",
            "consent_verified": "PDPA Consent Verified",
            "excluded_no_consent": "Excluded (no consent)",
            "start": "Start Date",
        },
        rows,
        [
            "A campaign cannot run until PDPA consent is verified; the excluded count is "
            "the audience deliberately dropped for missing consent."
        ],
        empty="No campaigns awaiting approval.",
    )


def budget_roi(env, date_from=None, date_to=None, **params):
    pack = attribution_roi(env)
    rows = []
    for row in pack["rows"]:
        rows.append(
            {
                "campaign": row["campaign"],
                "budget": row["budget"],
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
            "cost_per_response",
            "cost_per_conversion",
            "responses",
            "converted",
        ],
        {
            "campaign": "Campaign",
            "budget": "Budget",
            "cost_per_response": "Cost / Response",
            "cost_per_conversion": "Cost / Conversion",
            "responses": "Responses",
            "converted": "Converted",
        },
        rows,
        [
            "ROI ratio needs attributed revenue, which the response record does not carry "
            "— cost metrics are shown instead of an invented return."
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
    """Conversion value actually on file, or None when none is.

    A partial total presented as a total is the error this estate's rules
    exist to prevent, so the figure stays None until there is something real
    to add up.
    """
    Touch = env.get("fix.campaign.touch")
    if Touch is None:
        return None
    known = Touch.sudo().search([("touch_type", "=", "conversion"), ("value_known", "=", True)])
    if not known:
        return None
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
        # value is actually KNOWN. None when none are; never an estimate.
        "attributed_revenue": _attributed_revenue(env),
        "open_rate": round(len(responses) / recipients * 100.0, 1) if recipients else None,
        "consent_safe_reach": recipients - excluded if recipients else None,
    }


class P03CampaignApi(http.Controller):
    @http.route("/p03/campaign/kpis", type="jsonrpc", auth="user", readonly=True)
    def campaign_kpis(self, module=None, **kw):
        _require_internal(request.env)
        return {"M35": kpis(request.env)}
