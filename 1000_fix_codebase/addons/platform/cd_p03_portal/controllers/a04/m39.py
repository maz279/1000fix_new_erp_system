# A04 · M39 Subscriptions & Recurring — surfaces, report packs and KPIs over
# the real fix.subscription (3) / fix.subscription.charge / fix.revenue.schedule
# and the new usage, proration and autopay models. MRR is the recorded
# recurring amount of live subscriptions; no revenue is extrapolated.
import datetime

from odoo import http
from odoo.http import request

from ..p03_service_order_api import _require_internal

SURFACES = {
    # fix.subscription / fix.revenue.schedule are owned by M53 (a08 surface) and
    # read through the merged registry. fix.subscription.charge is M39's own
    # billing-run screen, so M39 declares it — an undeclared model left the
    # "Billing Runs" screen dead ("Model not served").
    "fix.subscription.charge": {
        "order": "id desc",
        "limit": 400,
        "actions": set(),
    },
    "fix.subscription.usage": {
        "order": "period_start desc, id desc",
        "limit": 300,
        "actions": set(),
    },
    # A04 build (2026-11-04) C3: the plan-change and mandate lifecycles run
    # by their actions (each checks its own role, state and consent).
    "fix.subscription.proration": {
        "order": "effective_date desc, id desc",
        "limit": 200,
        "actions": {"action_request_approval", "action_recall_approval", "action_void"},
    },
    "fix.subscription.autopay": {
        "order": "id desc",
        "limit": 200,
        "actions": {
            "action_send_consent_otp",
            "action_verify_consent_otp",
            "action_verify_signed_form",
            "action_activate",
            "action_revoke",
        },
    },
}

LIVE = ("active", "trial", "past_due", "hold")


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


def _subs(env):
    return env["fix.subscription"].sudo().search([])


def mrr_waterfall(env, date_from=None, date_to=None, **params):
    subs = _subs(env)
    live = subs.filtered(lambda s: s.state in LIVE)
    by_plan = {}
    for sub in live:
        row = by_plan.setdefault(
            sub.plan or "unspecified",
            {
                "plan": sub.plan or "unspecified",
                "subs": 0,
                "mrr": 0.0,
            },
        )
        row["subs"] += 1
        row["mrr"] += sub.recurring_amount or 0.0
    rows = list(by_plan.values())
    for row in rows:
        row["mrr"] = round(row["mrr"], 2)
    rows.sort(key=lambda r: -r["mrr"])
    charges = env["fix.subscription.charge"].sudo().search([])
    by_period = {}
    for charge in charges:
        key = charge.period_start.strftime("%Y-%m") if charge.period_start else "undated"
        by_period[key] = round(by_period.get(key, 0.0) + (charge.amount or 0.0), 2)
    notes = [
        "MRR by plan from live subscriptions. Billed periods recorded: %s."
        % (", ".join("%s=%s" % (k, v) for k, v in sorted(by_period.items())) or "none")
    ]
    totals = (
        {"plan": "Total MRR", "subs": len(live), "mrr": round(sum(r["mrr"] for r in rows), 2)}
        if rows
        else None
    )
    return _pack(
        "MRR Waterfall",
        ["plan", "subs", "mrr"],
        {"plan": "Plan", "subs": "Live Subscriptions", "mrr": "MRR"},
        rows,
        notes,
        totals=totals,
        empty="No live subscriptions yet.",
    )


def churn_nrr_cohorts(env, date_from=None, date_to=None, **params):
    subs = _subs(env)
    by_cohort = {}
    for sub in subs:
        key = sub.start_date.strftime("%Y-%m") if sub.start_date else "undated"
        row = by_cohort.setdefault(
            key,
            {
                "cohort": key,
                "subs": 0,
                "active": 0,
                "churned": 0,
                "mrr": 0.0,
                "churned_mrr": 0.0,
            },
        )
        row["subs"] += 1
        amount = sub.recurring_amount or 0.0
        if sub.state in ("churned", "cancelled"):
            row["churned"] += 1
            row["churned_mrr"] += amount
        elif sub.state in LIVE:
            row["active"] += 1
            row["mrr"] += amount
    rows = [by_cohort[k] for k in sorted(by_cohort, reverse=True)]
    for row in rows:
        row["retention_pct"] = round(row["active"] / row["subs"] * 100.0, 1) if row["subs"] else 0.0
        row["mrr"] = round(row["mrr"], 2)
        row["churned_mrr"] = round(row["churned_mrr"], 2)
    return _pack(
        "Churn & NRR Cohorts",
        ["cohort", "subs", "active", "churned", "retention_pct", "mrr", "churned_mrr"],
        {
            "cohort": "Start Cohort",
            "subs": "Subscriptions",
            "active": "Still Active",
            "churned": "Churned/Cancelled",
            "retention_pct": "Logo Retention %",
            "mrr": "Live MRR",
            "churned_mrr": "Churned MRR",
        },
        rows,
        [
            "Cohorts are the subscription start month. Logo retention = active / cohort "
            "size; churned MRR is the recurring amount lost."
        ],
        empty="No subscriptions yet.",
    )


def usage_vs_committed(env, date_from=None, date_to=None, **params):
    usage = env["fix.subscription.usage"].sudo().search([])
    rows = []
    for row in usage:
        rows.append(
            {
                "subscription": row.subscription_id.name,
                "period": "%s → %s" % (row.period_start, row.period_end),
                "metric": row.metric,
                "committed": row.committed,
                "used": row.quantity,
                "overage": row.overage_quantity,
                "overage_charge": round(row.overage_charge or 0.0, 2),
            }
        )
    rows.sort(key=lambda r: -r["overage_charge"])
    return _pack(
        "Usage vs Committed",
        ["subscription", "period", "metric", "committed", "used", "overage", "overage_charge"],
        {
            "subscription": "Subscription",
            "period": "Period",
            "metric": "Metric",
            "committed": "Committed",
            "used": "Used",
            "overage": "Overage",
            "overage_charge": "Overage Charge",
        },
        rows,
        [
            "Overage is computed by the model: max(used − committed, 0) × the recorded "
            "overage rate."
        ],
        totals={
            "subscription": "Total",
            "overage_charge": round(sum(r["overage_charge"] for r in rows), 2),
        }
        if rows
        else None,
        empty="No usage meters recorded yet.",
    )


def billing_exception_log(env, date_from=None, date_to=None, **params):
    subs = _subs(env).filtered(lambda s: s.state in ("past_due", "hold"))
    autopay = env["fix.subscription.autopay"].sudo().search([])
    failed = autopay.filtered(lambda a: a.last_result == "failed")
    rows = []
    for sub in subs:
        rows.append(
            {
                "subscription": sub.name,
                "plan": sub.plan,
                "state": sub.state,
                "days_overdue": sub.days_overdue,
                "dunning": sub.dunning_step,
                "autopay": "failed" if sub.id in failed.mapped("subscription_id").ids else "—",
            }
        )
    for mandate in failed:
        if mandate.subscription_id.id not in subs.ids:
            rows.append(
                {
                    "subscription": mandate.subscription_id.name,
                    "plan": mandate.subscription_id.plan,
                    "state": mandate.subscription_id.state,
                    "days_overdue": mandate.subscription_id.days_overdue,
                    "dunning": mandate.subscription_id.dunning_step,
                    "autopay": "failed",
                }
            )
    rows.sort(key=lambda r: -(r["days_overdue"] or 0))
    return _pack(
        "Billing Exception Log",
        ["subscription", "plan", "state", "days_overdue", "dunning", "autopay"],
        {
            "subscription": "Subscription",
            "plan": "Plan",
            "state": "State",
            "days_overdue": "Days Overdue",
            "dunning": "Dunning Step",
            "autopay": "Autopay",
        },
        rows,
        [
            "Exceptions are past-due/hold subscriptions plus any subscription whose "
            "autopay mandate last failed."
        ],
        empty="No billing exceptions — every subscription is current.",
    )


def deferred_revenue_bridge(env, date_from=None, date_to=None, **params):
    schedules = env["fix.revenue.schedule"].sudo().search([])
    rows = []
    total_deferred = 0.0
    for schedule in schedules:
        deferred = schedule.deferred_balance or 0.0
        total_deferred += deferred
        rows.append(
            {
                "schedule": schedule.display_name,
                "state": schedule.state,
                "deferred": round(deferred, 2),
                "start": str(getattr(schedule, "start_date", "") or "—"),
            }
        )
    return _pack(
        "Deferred Revenue Bridge",
        ["schedule", "state", "deferred", "start"],
        {
            "schedule": "Recognition Schedule",
            "state": "State",
            "deferred": "Deferred Balance",
            "start": "Start",
        },
        rows,
        [
            "Deferred balance comes from the revenue-recognition schedules. An empty "
            "bridge means no schedule exists yet — nothing is estimated."
        ],
        totals={"schedule": "Total deferred", "deferred": round(total_deferred, 2)}
        if rows
        else None,
        empty="No revenue-recognition schedules recorded yet.",
    )


def plan_mix(env, date_from=None, date_to=None, **params):
    pack = mrr_waterfall(env)
    rows = []
    for row in pack["rows"]:
        rows.append({"plan": row["plan"], "subs": row["subs"], "mrr": row["mrr"]})
    return _pack(
        "Plan Changes — current plan mix",
        ["plan", "subs", "mrr"],
        {"plan": "Plan", "subs": "Live Subscriptions", "mrr": "MRR"},
        rows,
        ["Plan changes are recorded as proration rows; this pack is the live mix."],
        totals={
            "plan": "Total",
            "subs": sum(r["subs"] for r in rows),
            "mrr": round(sum(r["mrr"] for r in rows), 2),
        }
        if rows
        else None,
        empty="No live subscriptions yet.",
    )


def dunning_ladder(env, date_from=None, date_to=None, **params):
    subs = _subs(env).filtered(lambda s: s.state in ("past_due", "hold"))
    by_step = {}
    for sub in subs:
        row = by_step.setdefault(
            sub.dunning_step or "none",
            {
                "step": sub.dunning_step or "none",
                "subs": 0,
                "amount": 0.0,
                "max_days": 0,
            },
        )
        row["subs"] += 1
        row["amount"] += sub.recurring_amount or 0.0
        row["max_days"] = max(row["max_days"], sub.days_overdue or 0)
    rows = sorted(by_step.values(), key=lambda r: -r["max_days"])
    for row in rows:
        row["amount"] = round(row["amount"], 2)
    return _pack(
        "Dunning Coordination",
        ["step", "subs", "amount", "max_days"],
        {
            "step": "Dunning Step",
            "subs": "Subscriptions",
            "amount": "Recurring Amount",
            "max_days": "Max Days Overdue",
        },
        rows,
        [
            "The ladder is read from the subscription's recorded dunning step and "
            "overdue days; service hold is a state, not an assumption."
        ],
        empty="No subscription is in dunning.",
    )


def recurring_forecast(env, date_from=None, date_to=None, **params):
    subs = _subs(env).filtered(lambda s: s.state in LIVE and s.next_invoice_date)
    horizon = datetime.date.today() + datetime.timedelta(days=90)
    upcoming = subs.filtered(lambda s: s.next_invoice_date <= horizon)
    rows = []
    for sub in upcoming.sorted("next_invoice_date"):
        rows.append(
            {
                "subscription": sub.name,
                "customer": sub.customer_id.name or "—",
                "plan": sub.plan,
                "next_invoice": str(sub.next_invoice_date),
                "amount": round(sub.recurring_amount or 0.0, 2),
            }
        )
    return _pack(
        "Recurring Forecast — next 90 days",
        ["subscription", "customer", "plan", "next_invoice", "amount"],
        {
            "subscription": "Subscription",
            "customer": "Customer",
            "plan": "Plan",
            "next_invoice": "Next Invoice",
            "amount": "Amount",
        },
        rows,
        [
            "Forecast = live subscriptions whose recorded next_invoice_date falls in "
            "the next 90 days. No projection beyond the recorded schedule."
        ],
        totals={"subscription": "Total", "amount": round(sum(r["amount"] for r in rows), 2)}
        if rows
        else None,
        empty="No subscription invoices due in the next 90 days.",
    )


def proration_summary(env, date_from=None, date_to=None, **params):
    prorations = env["fix.subscription.proration"].sudo().search([])
    rows = []
    for row in prorations:
        rows.append(
            {
                "proration": row.name,
                "subscription": row.subscription_id.name,
                "change": row.change_type,
                "from_plan": row.from_plan or "—",
                "to_plan": row.to_plan or "—",
                "amount": round(row.amount or 0.0, 2),
                "state": row.state,
            }
        )
    rows.sort(key=lambda r: -r["amount"])
    return _pack(
        "Proration Engine — mid-cycle changes",
        ["proration", "subscription", "change", "from_plan", "to_plan", "amount", "state"],
        {
            "proration": "Proration",
            "subscription": "Subscription",
            "change": "Change",
            "from_plan": "From Plan",
            "to_plan": "To Plan",
            "amount": "Amount",
            "state": "State",
        },
        rows,
        [
            "Each row is a recorded upgrade/downgrade/cancellation proration with its "
            "amount and invoicing state."
        ],
        totals={"proration": "Total", "amount": round(sum(r["amount"] for r in rows), 2)}
        if rows
        else None,
        empty="No proration rows recorded yet.",
    )


REPORTS = {
    "mrr_waterfall": mrr_waterfall,
    "churn_nrr_cohorts": churn_nrr_cohorts,
    "usage_vs_committed": usage_vs_committed,
    "billing_exception_log": billing_exception_log,
    "deferred_revenue_bridge": deferred_revenue_bridge,
    "plan_mix": plan_mix,
    "dunning_ladder": dunning_ladder,
    "recurring_forecast": recurring_forecast,
    "proration_summary": proration_summary,
}


def kpis(env):
    subs = _subs(env)
    live = subs.filtered(lambda s: s.state in LIVE)
    mrr = sum(live.mapped("recurring_amount"))
    churned = len(subs.filtered(lambda s: s.state in ("churned", "cancelled")))
    exceptions = len(subs.filtered(lambda s: s.state in ("past_due", "hold")))
    dunning = len(subs.filtered(lambda s: s.dunning_step and s.dunning_step != "none"))
    total = len(subs)
    return {
        "mrr": round(mrr, 2),
        "arr": round(mrr * 12.0, 2),
        "nrr": None,  # needs expansion/contraction history (proration timeline)
        "churn_logo": round(churned / total * 100.0, 1) if total else None,
        "billing_exceptions": exceptions,
        "dunning_in_progress": dunning,
    }


class P03SubscriptionApi(http.Controller):
    @http.route("/p03/subscription/kpis", type="jsonrpc", auth="user", readonly=True)
    def subscription_kpis(self, module=None, **kw):
        _require_internal(request.env)
        return {"M39": kpis(request.env)}
