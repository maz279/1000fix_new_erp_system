# A03 · M07 CRM & Sales Pipeline — the models the workspace screens may read,
# the workflow methods they may call, the computed reports and the KPI tiles.
# Substrate: Odoo crm (crm.lead L1) + cd_crm_ext rebuild surfaces.
import datetime
import logging

from odoo import fields

_logger = logging.getLogger(__name__)

SURFACES = {
    "crm.lead": {
        "order": "write_date desc, id desc",
        "limit": 200,
        # A03 audit G-M07-7: the Opportunities buttons were refused because
        # this set was empty. The real transitions, each with its own gate.
        "actions": {
            "action_convert_to_service_order",
            "action_set_won",
            "action_set_lost",
            "action_raise_estimate",
            "action_link_estimate",
            "action_request_contract_verification",
            "action_recall_approval",
            "action_score",
            # M07 audit 2026-11-13: a lead had no way to become an opportunity
            "action_convert_to_opportunity",
        },
    },
    # NOTE: mail.activity is deliberately NOT served: the generic endpoint
    # reads company-wide (sudo) and activities are per-user private. Calls,
    # visits and meetings are logged as fix.sales.activity (FR-CRM-045); a
    # next step with a date becomes a To-Do for its owner.
    "fix.sales.activity": {
        "order": "occurred_at desc, id desc",
        "limit": 300,
        "actions": set(),
    },
    # The key-account master and its decision makers (FR-CRM-028/029): built
    # in cd_crm_ext but served by no screen until the M07 audit 2026-11-13.
    "fix.account": {
        "order": "acv_bdt desc, id desc",
        "limit": 200,
        "actions": set(),
    },
    "fix.account.stakeholder": {
        "order": "account_id, buying_role, name",
        "limit": 300,
        "actions": set(),
    },
    "fix.pipeline": {
        "order": "code",
        "limit": 100,
        "actions": set(),
    },
    "fix.account.assignment": {
        "order": "effective_from desc, id desc",
        "limit": 200,
        "actions": {"action_assign_unowned"},
    },
    "fix.account.plan": {
        "order": "period desc, id desc",
        "limit": 200,
        "actions": {"action_mark_reviewed"},
    },
    "fix.qbr": {
        "order": "scheduled_for desc, id desc",
        "limit": 200,
        "actions": {"action_mark_data_ready", "action_mark_held"},
    },
    "fix.qbr.action": {
        "order": "due_date, id",
        "limit": 300,
        # M07 capture pass 2: an accepted recommendation becomes a pursuit
        # (FR-CRM-038)
        "actions": {"action_close", "action_cancel", "action_raise_opportunity"},
    },
    # --- M07 capture audit, second pass (2026-11-18) ----------------------
    # page 1: the need/authority/budget/timing assessment (FR-CRM-002)
    "fix.lead.qualification": {
        "order": "assessed_at desc, id desc",
        "limit": 300,
        "actions": set(),
        # only a lead still open to assessment; read sudo, so filtered here
        "pickers": {
            "lead_id": [
                ("type", "=", "lead"),
                ("active", "=", True),
                ("qualification_state", "in", ("captured", "qualified")),
            ]
        },
    },
    # page 2: contributors on a pursuit (FR-CRM-013)
    "fix.opportunity.team": {
        "order": "lead_id, id",
        "limit": 300,
        "actions": set(),
        "pickers": {
            "lead_id": [("type", "=", "opportunity"), ("active", "=", True)],
            "user_id": [("share", "=", False)],
        },
    },
    # page 3: targets the forecast is read against (FR-CRM-023)
    "fix.sales.quota": {
        "order": "period desc, owner_id, id",
        "limit": 300,
        "actions": set(),
        "pickers": {"owner_id": [("share", "=", False)]},
    },
    # page 5: the published dedicated-manager criteria (FR-CRM-027, BRU-CRM-09)
    "fix.account.eligibility": {
        "order": "effective_from desc, id desc",
        "limit": 50,
        "actions": set(),
    },
    "fix.renewal": {
        "order": "expiry_date, id",
        "limit": 200,
        # action_engage / action_renew were buttons with no method (G-M07-7).
        "actions": {"action_engage", "action_renew", "action_win", "action_lapse", "action_close"},
    },
    "fix.forecast.snapshot": {
        "order": "period desc, id desc",
        "limit": 200,
        "actions": set(),  # immutability is server-side (BRU-CRM-06)
    },
    # --- added by the A03 gap-closure build -------------------
    # Each of these is bound by a workspace screen below; an
    # unservable surface is what test_a03_registry_coverage exists
    # to catch, and a surface no screen opens is dead weight it
    # also catches.
    "fix.crm.sequence": {
        "order": "name",
        "limit": 200,
        "actions": {"action_activate", "action_pause"},
    },
    "fix.crm.sequence.step": {
        "order": "sequence_id, sequence, id",
        "limit": 300,
        "actions": set(),
    },
    "fix.crm.sequence.enrolment": {
        "order": "next_action_at, id",
        "limit": 300,
        "actions": {"action_pause_member", "action_resume_member"},
    },
    "fix.crm.score.model": {
        "order": "sequence, id",
        "limit": 200,
        "actions": {"action_activate"},
    },
    "fix.crm.score.factor": {
        "order": "model_id, sequence, id",
        "limit": 300,
        "actions": set(),
    },
}


# ---------------------------------------------------------------- reports
def _r(v):
    return round(v or 0.0, 2)


def pipeline_by_stream(env, **_kw):
    """Open opportunities grouped by pipeline/revenue stream (registry report)."""
    Pipeline = env["fix.pipeline"]
    Opportunity = env["crm.lead"]
    rows = []
    for pipeline in Pipeline.search([]):
        opps = Opportunity.search(
            [("type", "=", "opportunity"), ("pipeline_id", "=", pipeline.id), ("active", "=", True)]
        )
        if not opps:
            continue
        weighted = sum((o.expected_revenue or 0.0) * (o.probability or 0) / 100.0 for o in opps)
        rows.append(
            {
                "stream": pipeline.name,
                "open": len(opps),
                "value": _r(sum(opps.mapped("expected_revenue"))),
                "weighted": _r(weighted),
                "commit": _r(
                    sum(o.expected_revenue for o in opps if o.forecast_category == "commit")
                ),
            }
        )
    unassigned = Opportunity.search(
        [("type", "=", "opportunity"), ("pipeline_id", "=", False), ("active", "=", True)]
    )
    if unassigned:
        rows.append(
            {
                "stream": "(unassigned pipeline)",
                "open": len(unassigned),
                "value": _r(sum(unassigned.mapped("expected_revenue"))),
                "weighted": _r(
                    sum(
                        (o.expected_revenue or 0.0) * (o.probability or 0) / 100.0
                        for o in unassigned
                    )
                ),
                "commit": _r(
                    sum(o.expected_revenue for o in unassigned if o.forecast_category == "commit")
                ),
            }
        )
    cols = ["stream", "open", "value", "weighted", "commit"]
    return {
        "title": "Pipeline by Stream",
        "cols": cols,
        "labels": {
            "stream": "Revenue Stream",
            "open": "Open Opportunities",
            "value": "Pipeline Value",
            "weighted": "Weighted",
            "commit": "Commit",
        },
        "rows": rows,
        "empty": "No open opportunities.",
    }


def funnel_conversion(env, **_kw):
    """Lead → qualified → opportunity → won, by stage (conversion funnel)."""
    Lead = env["crm.lead"]
    leads = Lead.search([("type", "=", "lead")])
    # include archived (lost) opportunities — the default search hides them
    opps_all = Lead.with_context(active_test=False).search([("type", "=", "opportunity")])
    opps_active = opps_all.filtered(lambda o: o.active)
    won = opps_all.filtered(lambda o: o.probability == 100)
    lost = opps_all.filtered(lambda o: not o.active)
    rows = [
        {
            "stage": "Leads captured",
            "count": len(leads),
        },
        {
            "stage": "Opportunities created",
            "count": len(opps_all),
        },
        {
            "stage": "Open opportunities",
            "count": len(opps_active),
        },
        {
            "stage": "Won",
            "count": len(won),
        },
        {
            "stage": "Lost (with reason)",
            "count": len(lost.filtered(lambda o: o.lost_reason_code)),
        },
        {
            "stage": "Lost (reason missing)",
            "count": len(lost.filtered(lambda o: not o.lost_reason_code)),
        },
    ]
    cols = ["stage", "count"]
    return {
        "title": "Funnel Conversion",
        "cols": cols,
        "labels": {"stage": "Funnel Stage", "count": "Records"},
        "rows": rows,
        "notes": ["'reason missing' is a BRU-CRM-05 hygiene count — it should trend to zero."],
        "empty": "No CRM records yet.",
    }


def win_rate_by_source(env, **_kw):
    """Won vs lost opportunities by lead source."""
    Lead = env["crm.lead"]
    sources = dict(Lead._fields["lead_source"]._description_selection(env))
    rows = []
    for key, label in sources.items():
        # include archived (lost) deals — the default search hides them and
        # zeroed the Lost column (audit 2026-10-31)
        closed = Lead.with_context(active_test=False).search(
            [("type", "=", "opportunity"), ("lead_source", "=", key)]
        )
        if not closed:
            continue
        won = closed.filtered(lambda o: o.probability == 100)
        lost = closed.filtered(lambda o: not o.active)
        decided = len(won) + len(lost)
        rows.append(
            {
                "source": label,
                "won": len(won),
                "lost": len(lost),
                "win_rate": _r(100.0 * len(won) / decided) if decided else None,
            }
        )
    cols = ["source", "won", "lost", "win_rate"]
    return {
        "title": "Win Rate by Source",
        "cols": cols,
        "labels": {"source": "Lead Source", "won": "Won", "lost": "Lost", "win_rate": "Win Rate %"},
        "rows": rows,
        "empty": "No closed opportunities.",
    }


def am_scorecard(env, **_kw):
    """Account-manager scorecard: owned accounts, pipeline, won this year."""
    Assignment = env["fix.account.assignment"]
    Opportunity = env["crm.lead"]
    year = datetime.date.today().year
    rows = []
    for owner in Assignment.search([]).mapped("owner_id"):
        accounts = Assignment.search(
            [("owner_id", "=", owner.id), ("effective_to", "=", False)]
        ).mapped("partner_id")
        opps = Opportunity.search([("type", "=", "opportunity"), ("user_id", "=", owner.id)])
        won_ytd = opps.filtered(
            lambda o: o.probability == 100 and o.create_date and o.create_date.year == year
        )
        rows.append(
            {
                "manager": owner.name,
                "accounts": len(accounts),
                "open_opps": len(opps.filtered(lambda o: o.active)),
                "pipeline": _r(sum(opps.filtered(lambda o: o.active).mapped("expected_revenue"))),
                "won_ytd": len(won_ytd),
                "won_value_ytd": _r(sum(won_ytd.mapped("expected_revenue"))),
            }
        )
    cols = ["manager", "accounts", "open_opps", "pipeline", "won_ytd", "won_value_ytd"]
    return {
        "title": "Account Manager Scorecard",
        "cols": cols,
        "labels": {
            "manager": "Manager",
            "accounts": "Accounts",
            "open_opps": "Open Opps",
            "pipeline": "Open Pipeline",
            "won_ytd": "Won YTD",
            "won_value_ytd": "Won Value YTD",
        },
        "rows": rows,
        "empty": "No account assignments yet.",
    }


def renewal_risk(env, **_kw):
    """Renewal pursuits by risk band, value and play (registry report)."""
    Renewal = env["fix.renewal"]
    rows = []
    for band in ("high", "medium", "low"):
        renewals = Renewal.search([("risk_band", "=", band), ("state", "=", "open")])
        if not renewals:
            continue
        rows.append(
            {
                "risk_band": band.upper(),
                "count": len(renewals),
                "value": _r(sum(renewals.mapped("value"))),
                "nearest_expiry": str(min(renewals.mapped("expiry_date"))),
            }
        )
    cols = ["risk_band", "count", "value", "nearest_expiry"]
    return {
        "title": "Renewal Risk Report",
        "cols": cols,
        "labels": {
            "risk_band": "Risk Band",
            "count": "Open Renewals",
            "value": "Value at Risk",
            "nearest_expiry": "Nearest Expiry",
        },
        "rows": rows,
        "notes": [
            "Risk scoring sources (utilisation, satisfaction, SLA) arrive with M05/M34 data."
        ],
        "empty": "No open renewals.",
    }


def crosssell_attach(env, **_kw):
    """Cross-sell share of the pipeline (attach rate, registry report)."""
    Opportunity = env["crm.lead"]
    opps = Opportunity.search([("type", "=", "opportunity"), ("active", "=", True)])
    cross = opps.filtered(lambda o: o.is_cross_sell)
    total_value = sum(opps.mapped("expected_revenue"))
    cross_value = sum(cross.mapped("expected_revenue"))
    rows = [
        {
            "metric": "Cross-sell opportunities",
            "value": len(cross),
        },
        {
            "metric": "All open opportunities",
            "value": len(opps),
        },
        {
            "metric": "Attach rate (count) %",
            "value": _r(100.0 * len(cross) / len(opps)) if opps else 0.0,
        },
        {
            "metric": "Attach rate (value) %",
            "value": _r(100.0 * cross_value / total_value) if total_value else 0.0,
        },
    ]
    cols = ["metric", "value"]
    return {
        "title": "Cross-Sell Attach Rate",
        "cols": cols,
        "labels": {"metric": "Metric", "value": "Value"},
        "rows": rows,
        "empty": "No open opportunities.",
    }


def winloss_summary(env, **_kw):
    """Registry screen 'Win/Loss Analysis' — decided opportunities with the
    mandatory loss intelligence (competitor, competitor price, reason code;
    FLAW-07.2 enforces capture on the way to Lost)."""
    Lead = env["crm.lead"]
    # decided set MUST include archived (lost) deals — the default search hides
    # them and inflated the win rate to 100% (audit 2026-10-31: SQL showed 3
    # won of 4 decided while the tile computed 3/3).
    decided = (
        Lead.with_context(active_test=False)
        .search([("type", "=", "opportunity")])
        .filtered(lambda o: o.probability == 100 or not o.active)
    )
    rows = []
    for o in decided:
        won = o.probability == 100
        rows.append(
            {
                "opportunity": o.name,
                "customer": o.partner_id.display_name if o.partner_id else "—",
                "outcome": "Won" if won else "Lost",
                "value": o.expected_revenue or 0.0,
                "competitor": (o.competitor or "—") if not won else "—",
                "competitor_price": o.competitor_price_bdt
                if (not won and o.competitor_price_bdt)
                else None,
                "reason": (o.lost_reason_code or "—") if not won else "—",
            }
        )
    rows.sort(key=lambda r: str(r.get("opportunity")), reverse=True)
    won_n = sum(1 for r in rows if r["outcome"] == "Won")
    return {
        "title": "Win/Loss Analysis",
        "cols": [
            "opportunity",
            "customer",
            "outcome",
            "value",
            "competitor",
            "competitor_price",
            "reason",
        ],
        "labels": {
            "opportunity": "Opportunity",
            "customer": "Customer",
            "outcome": "Outcome",
            "value": "Deal Value (BDT)",
            "competitor": "Winning Competitor",
            "competitor_price": "Competitor Price (BDT)",
            "reason": "Loss Reason Code",
        },
        "rows": rows[:300],
        "notes": [f"{won_n} won / {len(rows) - won_n} lost decided opportunities."],
        "empty": "No decided opportunities yet.",
    }


REPORTS = {
    "pipeline_by_stream": pipeline_by_stream,
    "funnel_conversion": funnel_conversion,
    "win_rate_by_source": win_rate_by_source,
    "am_scorecard": am_scorecard,
    "renewal_risk": renewal_risk,
    "crosssell_attach": crosssell_attach,
    "winloss_summary": winloss_summary,
}


# ---------------------------------------------------------------- KPIs
def kpis(env):
    """The registry's six M07 tiles — live reads, never literals."""
    out = {}

    def safe(key, fn):
        try:
            out[key] = fn()
        except Exception:
            _logger.debug("M07 KPI %s unavailable", key, exc_info=True)
            out[key] = None

    Lead = env["crm.lead"]
    open_opps = Lead.search([("type", "=", "opportunity"), ("active", "=", True)])

    safe(
        "weighted_pipeline",
        lambda: _r(
            sum((o.expected_revenue or 0.0) * (o.probability or 0) / 100.0 for o in open_opps)
        ),
    )
    # decided set MUST include archived (lost) deals — the default search hides
    # them and inflated the win rate to 100% (audit 2026-10-31: SQL showed 3
    # won of 4 decided while the tile computed 3/3).
    decided = (
        Lead.with_context(active_test=False)
        .search([("type", "=", "opportunity")])
        .filtered(lambda o: o.probability == 100 or not o.active)
    )
    won_count = len(decided.filtered(lambda o: o.probability == 100))
    safe("win_rate", lambda: _r(100.0 * won_count / len(decided)) if decided else 0.0)
    today = fields.Date.today()
    t90 = (today + datetime.timedelta(days=90)).isoformat()
    safe(
        "renewals_t90",
        lambda: env["fix.renewal"].search_count(
            [("state", "=", "open"), ("expiry_date", "<=", t90)]
        ),
    )
    year = today.year
    safe(
        "new_corp_logos_ytd",
        lambda: env["fix.account.assignment"].search_count(
            [
                ("assignment_type", "in", ("account", "dedicated")),
                ("effective_from", ">=", f"{year}-01-01"),
            ]
        ),
    )
    month_start = today.replace(day=1)
    safe(
        "qbrs_this_month",
        lambda: env["fix.qbr"].search_count(
            [("scheduled_for", ">=", month_start), ("scheduled_for", "<=", today)]
        ),
    )
    safe(
        "referral_leads",
        lambda: Lead.search_count([("type", "=", "lead"), ("lead_source", "=", "referral")]),
    )
    return out
