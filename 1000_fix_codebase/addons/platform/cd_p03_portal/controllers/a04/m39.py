# A04 · M39 Subscriptions & Recurring — surfaces, report packs and KPIs over
# the real fix.subscription (3) / fix.subscription.charge / fix.revenue.schedule
# and the new usage, proration and autopay models. MRR is the recorded
# recurring amount of live subscriptions; no revenue is extrapolated.
import datetime
import logging

from odoo import fields, http
from odoo.http import request

from ..p03_service_order_api import _require_internal
from ._scope import scoped

_logger = logging.getLogger(__name__)

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
        # capture audit 2026-11-19: the exception queue is worked by re-rating
        "actions": {"action_rerate"},
    },
    # A04 build (2026-11-04) C3: the plan-change and mandate lifecycles run
    # by their actions (each checks its own role, state and consent).
    "fix.subscription.proration": {
        "order": "effective_date desc, id desc",
        "limit": 200,
        # A04 ERP round 2 M39-F16: a price increase is told to the customer
        # before it applies (BRU-SUB-07)
        "actions": {
            "action_request_approval",
            "action_recall_approval",
            "action_void",
            "action_send_price_notice",
        },
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
    # M39 capture audit (2026-11-19): the records each sub-module page captures.
    "fix.subscription.schedule": {
        "order": "id desc",
        "limit": 200,
        "actions": {"action_activate", "action_regenerate", "action_void"},
    },
    "fix.subscription.line": {
        "order": "subscription_id, id",
        "limit": 300,
        "actions": {"action_approve", "action_end", "action_void"},
    },
    "fix.subscription.billing.run": {
        "order": "id desc",
        "limit": 100,
        "actions": {"action_dry_run", "action_review", "action_commit", "action_void"},
    },
    "fix.subscription.adjustment": {
        "order": "id desc",
        "limit": 200,
        "actions": {"action_request_approval", "action_recall_approval", "action_void"},
    },
    "fix.subscription.lifecycle": {
        "order": "id desc",
        "limit": 200,
        "actions": {"action_submit", "action_approve", "action_reject", "action_void"},
    },
    "fix.subscription.churn": {
        "order": "churn_date desc, id desc",
        "limit": 200,
        "actions": set(),
    },
}

# A04 ERP audit M39-F13 (20 Nov 2026): the packs and KPIs read through
# _scope.scoped (the caller's companies and the requested period), and the
# formulas were corrected:
#   * MRR counts subscriptions under contract that bill (active, trial, past
#     due); a held (suspended) one is excluded - it bills nothing;
#   * churn is monthly: logos cancelled in the period / live at its start;
#   * a cohort is normalised (monthly value, not the cycle amount);
#   * the MRR waterfall bridges opening -> new / expansion / contraction /
#     churn -> closing over the period, and NRR is read from it;
#   * the dunning pack sums the OVERDUE BALANCE of cycle invoices, not the
#     recurring amount.
LIVE = ("active", "trial", "past_due", "hold")
BILLING_LIVE = ("active", "trial", "past_due")
CLOSED = ("churned", "cancelled")


def _period(env, date_from=None, date_to=None):
    """The requested period, defaulting to the current month (Asia/Dhaka)."""
    today = fields.Date.context_today(env.user.with_context(tz="Asia/Dhaka"))
    start = _as_date(date_from) or today.replace(day=1)
    end = _as_date(date_to) or today
    return start, end


def _as_date(value):
    if not value:
        return None
    if isinstance(value, datetime.date):
        return value
    try:
        return fields.Date.to_date(str(value)[:10])
    except (TypeError, ValueError):
        return None


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


def _subs(env, domain=None):
    """Subscriptions of the caller's companies (any start date)."""
    return scoped(env, "fix.subscription", domain or [])


def _live_on(sub, day):
    """Under contract on `day`: started, not yet cancelled."""
    if not sub.start_date or sub.start_date > day:
        return False
    if sub.state in CLOSED:
        return bool(sub.cancelled_on and sub.cancelled_on > day)
    return True


def _waterfall(env, start, end):
    """Opening / new / expansion / contraction / churn / closing MRR over
    [start, end] from the subscriptions and their applied price changes."""
    subs = _subs(env)
    eve = start - datetime.timedelta(days=1)
    opening_subs = subs.filtered(lambda s: _live_on(s, eve) and s.state != "hold")
    new_subs = subs.filtered(lambda s: s.start_date and start <= s.start_date <= end)
    churned = subs.filtered(
        lambda s: s.state in CLOSED and s.cancelled_on and start <= s.cancelled_on <= end
    )
    prorations = scoped(
        env,
        "fix.subscription.proration",
        [("applied_to_subscription", "=", True), ("subscription_id", "in", subs.ids)],
        "effective_date",
        start,
        end,
    )
    months = {"monthly": 1, "quarterly": 3, "annual": 12}
    expansion = contraction = 0.0
    for p in prorations:
        delta = ((p.new_amount or 0.0) - (p.old_amount or 0.0)) / months.get(
            p.subscription_id.billing_cycle or "monthly", 1
        )
        if p.change_type == "cancel":
            continue
        if delta >= 0:
            expansion += delta
        else:
            contraction += -delta
    opening = sum(opening_subs.mapped("monthly_value"))
    new = sum((new_subs - churned).mapped("monthly_value"))
    lost = sum(churned.filtered(lambda s: s in opening_subs).mapped("monthly_value"))
    closing = sum(
        subs.filtered(lambda s: s.state in BILLING_LIVE and _live_on(s, end)).mapped(
            "monthly_value"
        )
    )
    return {
        "opening": round(opening, 2),
        "new": round(new, 2),
        "expansion": round(expansion, 2),
        "contraction": round(contraction, 2),
        "churn": round(lost, 2),
        "closing": round(closing, 2),
        "opening_logos": len(opening_subs),
        "churned_logos": len(churned.filtered(lambda s: s in opening_subs)),
    }


def mrr_waterfall(env, date_from=None, date_to=None, **params):
    start, end = _period(env, date_from, date_to)
    w = _waterfall(env, start, end)
    rows = [
        {"step": "Opening MRR (%s)" % (start - datetime.timedelta(days=1)), "mrr": w["opening"]},
        {"step": "+ New", "mrr": w["new"]},
        {"step": "+ Expansion", "mrr": w["expansion"]},
        {"step": "- Contraction", "mrr": -w["contraction"]},
        {"step": "- Churn", "mrr": -w["churn"]},
        {"step": "Closing MRR (%s)" % end, "mrr": w["closing"]},
    ]
    nrr = _nrr(w)
    return _pack(
        "MRR Waterfall",
        ["step", "mrr"],
        {"step": "Movement", "mrr": "MRR"},
        rows,
        [
            "MRR is normalised to a month (BRU-SUB-15) and counts subscriptions that bill "
            "(active, trial, past due); a held (suspended) subscription is excluded. "
            "Expansion / contraction are the price changes applied in the period. NRR = "
            "(opening + expansion - contraction - churn) / opening = %s%%. Movements use "
            "today's monthly value of each subscription; the closing line is the live "
            "register, so a residual can remain when prices changed outside a proration."
            % (nrr if nrr is not None else "n/a")
        ],
        empty="No subscriptions yet.",
    )


def _nrr(w):
    if not w["opening"]:
        return None
    kept = w["opening"] + w["expansion"] - w["contraction"] - w["churn"]
    return round(kept / w["opening"] * 100.0, 1)


def churn_nrr_cohorts(env, date_from=None, date_to=None, **params):
    subs = _subs(env)
    by_cohort = {}
    for sub in subs:
        key = sub.start_date.strftime("%Y-%m") if sub.start_date else "undated"
        row = by_cohort.setdefault(
            key,
            {"cohort": key, "subs": 0, "active": 0, "churned": 0, "mrr": 0.0, "churned_mrr": 0.0},
        )
        row["subs"] += 1
        monthly = sub.monthly_value or 0.0  # normalised (M39-F13)
        if sub.state in CLOSED:
            row["churned"] += 1
            row["churned_mrr"] += monthly
        elif sub.state in BILLING_LIVE:
            row["active"] += 1
            row["mrr"] += monthly
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
            "active": "Still Billing",
            "churned": "Churned/Cancelled",
            "retention_pct": "Logo Retention %",
            "mrr": "Live MRR (monthly)",
            "churned_mrr": "Churned MRR (monthly)",
        },
        rows,
        [
            "Cohorts are the subscription start month. Logo retention = still billing / "
            "cohort size; MRR is the monthly value (a quarterly or annual amount divided by "
            "its months)."
        ],
        empty="No subscriptions yet.",
    )


def usage_vs_committed(env, date_from=None, date_to=None, **params):
    usage = scoped(env, "fix.subscription.usage", [], "period_start", date_from, date_to)
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


def _overdue_balance(sub):
    invoices = sub._overdue_unpaid_invoices()
    return round(sum(invoices.mapped("amount_residual")), 2)


def billing_exception_log(env, date_from=None, date_to=None, **params):
    subs = _subs(env, [("state", "in", ("past_due", "hold"))])
    autopay = scoped(env, "fix.subscription.autopay", [("last_result", "=", "failed")])
    failed_subs = autopay.mapped("subscription_id")
    rows = []
    for sub in subs | failed_subs:
        rows.append(
            {
                "subscription": sub.name,
                "plan": sub.plan,
                "state": sub.state,
                "days_overdue": sub.days_overdue,
                "overdue": _overdue_balance(sub),
                "dunning": sub.dunning_step,
                "autopay": "failed" if sub in failed_subs else "—",
            }
        )
    rows.sort(key=lambda r: -(r["days_overdue"] or 0))
    return _pack(
        "Billing Exception Log",
        ["subscription", "plan", "state", "days_overdue", "overdue", "dunning", "autopay"],
        {
            "subscription": "Subscription",
            "plan": "Plan",
            "state": "State",
            "days_overdue": "Days Overdue",
            "overdue": "Overdue Balance",
            "dunning": "Dunning Step",
            "autopay": "Autopay",
        },
        rows,
        [
            "Exceptions are past-due/hold subscriptions plus any subscription whose "
            "autopay mandate last failed; the balance is what is overdue on its cycle invoices."
        ],
        empty="No billing exceptions — every subscription is current.",
    )


def deferred_revenue_bridge(env, date_from=None, date_to=None, **params):
    schedules = scoped(env, "fix.revenue.schedule", [], "start_date", None, date_to)
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
            "Deferred balance comes from the revenue-recognition schedules started by the "
            "period end. An empty bridge means no schedule exists yet — nothing is estimated."
        ],
        totals={"schedule": "Total deferred", "deferred": round(total_deferred, 2)}
        if rows
        else None,
        empty="No revenue-recognition schedules recorded yet.",
    )


def plan_mix(env, date_from=None, date_to=None, **params):
    subs = _subs(env, [("state", "in", list(BILLING_LIVE))])
    by_plan = {}
    for sub in subs:
        row = by_plan.setdefault(
            sub.plan or "unspecified", {"plan": sub.plan or "unspecified", "subs": 0, "mrr": 0.0}
        )
        row["subs"] += 1
        row["mrr"] += sub.monthly_value or 0.0
    rows = sorted(by_plan.values(), key=lambda r: -r["mrr"])
    for row in rows:
        row["mrr"] = round(row["mrr"], 2)
    return _pack(
        "Plan Changes — current plan mix",
        ["plan", "subs", "mrr"],
        {"plan": "Plan", "subs": "Billing Subscriptions", "mrr": "MRR"},
        rows,
        [
            "Plan changes are recorded as proration rows; this pack is the live mix (holds excluded)."
        ],
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
    subs = _subs(env, [("state", "in", ("past_due", "hold"))])
    by_step = {}
    for sub in subs:
        row = by_step.setdefault(
            sub.dunning_step or "none",
            {"step": sub.dunning_step or "none", "subs": 0, "amount": 0.0, "max_days": 0},
        )
        row["subs"] += 1
        row["amount"] += _overdue_balance(sub)
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
            "amount": "Overdue Balance",
            "max_days": "Max Days Overdue",
        },
        rows,
        [
            "The ladder is read from the subscription's recorded dunning step; the amount is "
            "the unpaid residual of its cycle invoices past due (M39-F13), not the recurring "
            "amount."
        ],
        empty="No subscription is in dunning.",
    )


def recurring_forecast(env, date_from=None, date_to=None, **params):
    subs = _subs(env, [("state", "in", list(BILLING_LIVE))]).filtered("next_invoice_date")
    today = fields.Date.context_today(env.user)
    horizon = today + datetime.timedelta(days=90)
    rows = []
    scheduled = (
        env["fix.subscription.schedule.period"]
        .sudo()
        .search(
            [
                ("state", "=", "planned"),
                ("schedule_id.state", "=", "active"),
                ("subscription_id", "in", subs.ids),
                ("billing_date", "<=", horizon),
            ],
            order="billing_date, id",
        )
    )
    for period in scheduled:
        sub = period.subscription_id
        rows.append(
            {
                "subscription": sub.name,
                "customer": sub.customer_id.name or "—",
                "plan": sub.plan,
                "next_invoice": str(period.billing_date),
                "amount": round(period._fix_price_now(), 2),
            }
        )
    upcoming = (subs - scheduled.mapped("subscription_id")).filtered(
        lambda s: s.next_invoice_date <= horizon and not s._active_schedule()
    )
    for sub in upcoming.sorted("next_invoice_date"):
        end, amount = sub._fix_cycle_window(sub.next_invoice_date)
        if not end:
            continue
        rows.append(
            {
                "subscription": sub.name,
                "customer": sub.customer_id.name or "—",
                "plan": sub.plan,
                "next_invoice": str(sub.next_invoice_date),
                "amount": round(amount, 2),
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
            "Forecast = the planned periods of active billing schedules at today's price, and "
            "otherwise the next cycle within the contract term, within the next 90 days."
        ],
        totals={"subscription": "Total", "amount": round(sum(r["amount"] for r in rows), 2)}
        if rows
        else None,
        empty="No subscription invoices due in the next 90 days.",
    )


def proration_summary(env, date_from=None, date_to=None, **params):
    prorations = scoped(env, "fix.subscription.proration", [], "effective_date", date_from, date_to)
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
            "amount and invoicing state, effective in the period."
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


def kpis(env, date_from=None, date_to=None):
    """M39-F13: through scoped(), for the period (default: this month)."""
    out = {
        "mrr": None,
        "arr": None,
        "nrr": None,
        "churn_logo": None,
        "billing_exceptions": None,
        "dunning_in_progress": None,
    }
    try:
        start, end = _period(env, date_from, date_to)
        billing = _subs(env, [("state", "in", list(BILLING_LIVE))])
        mrr = sum(billing.mapped("monthly_value"))
        w = _waterfall(env, start, end)
        out.update(
            {
                "mrr": round(mrr, 2),
                "arr": round(mrr * 12.0, 2),
                "nrr": _nrr(w),
                # logos lost in the period / logos live at its start (monthly churn)
                "churn_logo": round(w["churned_logos"] / w["opening_logos"] * 100.0, 1)
                if w["opening_logos"]
                else None,
                "billing_exceptions": len(_subs(env, [("state", "in", ("past_due", "hold"))])),
                "dunning_in_progress": len(
                    _subs(env, [("dunning_step", "not in", (False, "none"))])
                ),
            }
        )
    except Exception:  # a KPI tile must not break the screen, but is never silent
        _logger.exception("M39 KPIs failed")
    return out


class P03SubscriptionApi(http.Controller):
    @http.route("/p03/subscription/kpis", type="jsonrpc", auth="user", readonly=True)
    def subscription_kpis(self, module=None, **kw):
        _require_internal(request.env)
        return {"M39": kpis(request.env)}
