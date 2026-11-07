# fix_demand_common — M43 shared helpers: roles, configuration, period
# arithmetic and the M15 / M16 readers every planning figure is computed from.
#
# A06 audit (2026-11-03) M43-3: every planning figure was typed. The readers
# below are the only sources: M15 consumption (`fix.stock.consumption`, state
# consumed) for demand history and actuals, M15 on-hand (`fix.stock.onhand`,
# owned stock only: consignment and customer stock are not ours to plan on)
# for the stock position, and M16 open requisitions / purchase-order lines
# for stock on order. They read with sudo() scoped to the record's company,
# so a figure does not depend on which operating units the person computing
# it happens to see.
import re
from calendar import monthrange
from datetime import date, datetime, time, timedelta
from math import ceil, sqrt

from odoo.exceptions import AccessError, UserError

PLANNER = "cd_demand_plan.group_fix_demand_planner"
APPROVER = "cd_demand_plan.group_fix_demand_approver"
ROLE_LABELS = {PLANNER: "Demand Planner", APPROVER: "Demand Plan Approver"}

# z for the one-sided service level (normal distribution)
Z_FACTORS = {90: 1.28, 95: 1.65, 98: 2.05, 99: 2.33}

PERIOD_RE = re.compile(r"^(\d{4})-(0[1-9]|1[0-2])$")

# Configuration keys (business decisions, report section 7). Defaults are
# the conservative values documented in the runbook.
CFG_FORECAST_WINDOW = "cd_demand_plan.forecast_window_months"  # default 3
CFG_FORECAST_MIN_HISTORY = "cd_demand_plan.forecast_min_history_months"  # default 2
CFG_POLICY_HISTORY_DAYS = "cd_demand_plan.policy_history_days"  # default 90
CFG_REVIEW_PERIOD_DAYS = "cd_demand_plan.review_period_days"  # default 30
CFG_SEGMENT_WINDOW_MONTHS = "cd_demand_plan.segment_window_months"  # default 12
CFG_ABC_A_SHARE = "cd_demand_plan.abc_a_share"  # default 0.80
CFG_ABC_B_SHARE = "cd_demand_plan.abc_b_share"  # default 0.95
CFG_XYZ_X_CV = "cd_demand_plan.xyz_x_max_cv"  # default 0.5
CFG_XYZ_Y_CV = "cd_demand_plan.xyz_y_max_cv"  # default 1.0
CFG_LEAD_TIME_WINDOW_DAYS = "cd_demand_plan.lead_time_window_days"  # default 365
CFG_ENFORCE_BUDGET = "cd_demand_plan.enforce_budget"  # default 0 = report only

OPEN_PO_STATES = ("draft", "sent", "acknowledged", "partially_received")
CLOSED_REQ_STATES = ("converted", "rejected", "cancelled")


def param(env, key, default, cast=float):
    raw = env["ir.config_parameter"].sudo().get_param(key)
    if raw in (None, False, ""):
        return default
    try:
        return cast(raw)
    except (TypeError, ValueError) as exc:
        raise UserError(
            "Configuration %s = %r is not a valid %s." % (key, raw, cast.__name__)
        ) from exc


def has_role(env, *xmlids) -> bool:
    return env.su or any(env.user.has_group(x) for x in xmlids)


def require_role(env, *xmlids, what="This step"):
    if has_role(env, *xmlids):
        return
    raise AccessError(
        "%s needs the %s role." % (what, " or ".join(ROLE_LABELS.get(x, x) for x in xmlids))
    )


def refuse_self_decision(env, preparers, what):
    """Two-person rule: the deciding user (env.user, never a parameter) is not
    one of the people who prepared or changed the record."""
    if env.su:
        return
    if env.user in preparers:
        raise UserError(
            "%s must be decided by someone other than the person who prepared or "
            "changed it (segregation of duties)." % what
        )


# ------------------------------------------------------------------ periods
def month_start(period: str) -> date:
    match = PERIOD_RE.match(period or "")
    if not match:
        raise UserError("Period %r is not a YYYY-MM month." % (period,))
    return date(int(match.group(1)), int(match.group(2)), 1)


def add_months(first: date, months: int) -> date:
    years, month0 = divmod(first.month - 1 + months, 12)
    return date(first.year + years, month0 + 1, 1)


def month_end(first: date) -> date:
    return date(first.year, first.month, monthrange(first.year, first.month)[1])


def period_of(day: date) -> str:
    return "%04d-%02d" % (day.year, day.month)


def months_between(start: date, end: date) -> list:
    """YYYY-MM labels of every month the [start, end] range touches."""
    if not start or not end or end < start:
        return []
    out, cur = [], date(start.year, start.month, 1)
    while cur <= end:
        out.append(period_of(cur))
        cur = add_months(cur, 1)
    return out


def _dt(day: date) -> datetime:
    return datetime.combine(day, time.min)


# ------------------------------------------------------------------ M15 readers
def _consumption_rows(env, company, part, location, start: date, stop: date):
    domain = [
        ("company_id", "=", company.id),
        ("product_id", "=", part.id),
        ("state", "=", "consumed"),
        ("consumed_at", ">=", _dt(start)),
        ("consumed_at", "<", _dt(stop)),
    ]
    if location:
        domain.append(("location_id", "=", location.id))
    return (
        env["fix.stock.consumption"]
        .sudo()
        .search_read(domain, ["quantity", "consumed_at", "unit_cost"])
    )


def consumed_by_month(env, company, part, location, first: date, months: int) -> list:
    """Consumed quantity per calendar month, `months` buckets from `first`."""
    buckets = [0.0] * months
    for row in _consumption_rows(env, company, part, location, first, add_months(first, months)):
        at = row["consumed_at"]
        idx = (at.year - first.year) * 12 + at.month - first.month
        if 0 <= idx < months:
            buckets[idx] += row["quantity"] or 0.0
    return buckets


def consumed_by_day(env, company, part, location, first: date, days: int) -> list:
    buckets = [0.0] * days
    for row in _consumption_rows(env, company, part, location, first, first + timedelta(days=days)):
        idx = (row["consumed_at"].date() - first).days
        if 0 <= idx < days:
            buckets[idx] += row["quantity"] or 0.0
    return buckets


def has_usable_history(env, company, part, location) -> bool:
    """BRU-DPL-01 readiness, as the forecast's own test: enough of the last
    window months carry M15 consumption for a statistical figure."""
    window = param(env, CFG_FORECAST_WINDOW, 3, int)
    minimum = param(env, CFG_FORECAST_MIN_HISTORY, 2, int)
    first = add_months(date.today().replace(day=1), -window)
    buckets = consumed_by_month(env, company, part, location, first, window)
    return sum(1 for b in buckets if b > 0) >= minimum


def consumed_value(env, company, part, first: date, stop: date) -> float:
    return sum(
        (r["quantity"] or 0.0) * (r["unit_cost"] or 0.0)
        for r in _consumption_rows(env, company, part, False, first, stop)
    )


def mean_and_stddev(values: list) -> tuple:
    if not values:
        return 0.0, 0.0
    mean = sum(values) / len(values)
    if len(values) < 2:
        return mean, 0.0
    var = sum((v - mean) ** 2 for v in values) / (len(values) - 1)
    return mean, sqrt(var)


def on_hand(env, company, part, location) -> float:
    """Available OWNED stock of the part (at the location when given)."""
    domain = [
        ("company_id", "=", company.id),
        ("part_id", "=", part.id),
        ("ownership_class", "=", "owned"),
    ]
    if location:
        domain.append(("location_id", "=", location.id))
    rows = env["fix.stock.onhand"].sudo().search_read(domain, ["qty", "reserved"])
    return round(sum((r["qty"] or 0.0) - (r["reserved"] or 0.0) for r in rows), 3)


# ------------------------------------------------------------------ M16 readers
def on_order(env, company, products) -> float:
    """Quantity already on its way: open requisitions plus the unreceived
    balance of open purchase-order lines for these products."""
    if not products:
        return 0.0
    reqs = (
        env["fix.requisition"]
        .sudo()
        .search_read(
            [
                ("company_id", "=", company.id),
                ("product_id", "in", products.ids),
                ("state", "not in", CLOSED_REQ_STATES),
            ],
            ["qty"],
        )
    )
    qty = sum(r["qty"] or 0.0 for r in reqs)
    lines = (
        env["fix.purchase.order.line"]
        .sudo()
        .search_read(
            [
                ("product_id", "in", products.ids),
                ("order_id.company_id", "=", company.id),
                ("order_id.state", "in", OPEN_PO_STATES),
            ],
            ["qty_ordered", "qty_received"],
        )
    )
    qty += sum(max((r["qty_ordered"] or 0.0) - (r["qty_received"] or 0.0), 0.0) for r in lines)
    return round(qty, 3)


# ------------------------------------------------------------------ formulas
def safety_stock(service_level, stddev, lead_days) -> float:
    z = Z_FACTORS.get(int(service_level or 95), 1.65)
    return round(z * (stddev or 0.0) * sqrt(max(lead_days or 0, 0)), 2)


def order_up_to(projected, rop, target) -> float:
    """S8: order when the projected position is at or below the reorder point,
    up to the target (max) level; never above the target, never negative."""
    if projected > rop:
        return 0.0
    return round(max(0.0, target - projected), 3)


def apply_moq_pack(qty, moq, pack) -> float:
    """M43-5: a positive order is at least the MOQ and a whole number of
    packs. Rounding up may end above the target by less than one pack (or up
    to the MOQ): the supplier's terms win over the target level."""
    if qty <= 0:
        return 0.0
    qty = max(qty, moq or 0.0)
    if pack and pack > 0:
        qty = ceil(round(qty / pack, 9)) * pack
    return round(qty, 3)


# ------------------------------------------------------------------ M16 lead times
def observed_lead_times(env, company, products, since: date) -> list:
    """Days from the PO being sent to its posted goods receipt, one sample per
    posted receipt line of these products received since `since`. Lines of a
    PO never sent (no sent_at) or received before it was sent are ignored.
    BRU-ITC-19: an import with no PO has no M16 receipt, so its own receipt
    gives the sample; a PO-linked import is already counted by its M16 GRN."""
    if not products:
        return []
    return _m16_lead_times(env, company, products, since) + _m44_lead_times(
        env, company, products, since
    )


def _m44_lead_times(env, company, products, since: date) -> list:
    """Days from the commitment (the approved proforma, else the order's
    creation) to the receipt of an import with no M16 PO."""
    if "fix.import.order.line" not in env:
        return []
    lines = (
        env["fix.import.order.line"]
        .sudo()
        .search(
            [
                ("part_id.product_id", "in", products.ids),
                ("order_id.company_id", "=", company.id),
                ("order_id.received_on", ">=", since),
                ("order_id.m16_receipt_id", "=", False),
            ]
        )
    )
    out = []
    for line in lines:
        order = line.order_id
        proformas = (
            env["fix.import.proforma"]
            .sudo()
            .search([("order_id", "=", order.id), ("state", "=", "approved")])
        )
        stamps = [d for d in proformas.mapped("decided_on") if d]
        start = min(stamps) if stamps else order.create_date
        days = (order.received_on - start.date()).days
        if days >= 0:
            out.append(days)
    return out


def _m16_lead_times(env, company, products, since: date) -> list:
    if "fix.purchase.receipt.line" not in env:
        return []
    lines = (
        env["fix.purchase.receipt.line"]
        .sudo()
        .search(
            [
                ("product_id", "in", products.ids),
                ("receipt_id.state", "=", "posted"),
                ("receipt_id.company_id", "=", company.id),
                ("receipt_id.received_on", ">=", since),
            ]
        )
    )
    out = []
    for line in lines:
        order = line.receipt_id.purchase_order_id
        received = line.receipt_id.received_on
        if not (order.sent_at and received):
            continue
        days = (received - order.sent_at.date()).days
        if days >= 0:
            out.append(days)
    return out


# ------------------------------------------------------------------ FP&A budget
def budget_headroom(env, company, on_date):
    """(remaining, note) of the parts-cost budget in force on `on_date`:
    planned - posted actual - open M16 commitments (open requisitions that
    carry a product, unreceived open PO lines). remaining is None, with the
    reason in the note, when no check is possible."""
    if "fix.budget.line" not in env or "fix.budget.version" not in env:
        return None, "No budget check: the FP&A budget module (fix.budget) is not installed."
    versions = (
        env["fix.budget.version"]
        .sudo()
        .search(
            [
                ("company_id", "=", company.id),
                ("state", "=", "approved"),
                ("date_from", "<=", on_date),
                ("date_to", ">=", on_date),
            ]
        )
    )
    if not versions:
        return None, "No budget check: no approved budget version covers %s." % on_date
    accounts = versions.mapped("parts_account_id")
    if not accounts:
        return None, "No budget check: the approved budget version names no parts cost account."
    lines = (
        env["fix.budget.line"]
        .sudo()
        .search(
            [
                ("version_id", "in", versions.ids),
                ("account_id", "in", accounts.ids),
                ("date_from", "<=", on_date),
                ("date_to", ">=", on_date),
            ]
        )
    )
    if not lines:
        return None, "No budget check: no parts budget line covers %s." % on_date
    planned = sum(lines.mapped("planned_amount"))
    actual = sum(lines.mapped("actual_amount"))
    reqs = (
        env["fix.requisition"]
        .sudo()
        .search_read(
            [
                ("company_id", "=", company.id),
                ("product_id", "!=", False),
                ("state", "not in", CLOSED_REQ_STATES),
            ],
            ["estimate_amount"],
        )
    )
    po_lines = (
        env["fix.purchase.order.line"]
        .sudo()
        .search_read(
            [("order_id.company_id", "=", company.id), ("order_id.state", "in", OPEN_PO_STATES)],
            ["qty_ordered", "qty_received", "unit_price"],
        )
    )
    committed = sum(r["estimate_amount"] or 0.0 for r in reqs) + sum(
        max((r["qty_ordered"] or 0.0) - (r["qty_received"] or 0.0), 0.0) * (r["unit_price"] or 0.0)
        for r in po_lines
    )
    remaining = round(planned - actual - committed, 2)
    return remaining, (
        "Parts budget (%s): planned BDT %.2f, actual BDT %.2f, committed BDT %.2f, "
        "remaining BDT %.2f."
        % (", ".join(accounts.mapped("code")), planned, actual, committed, remaining)
    )
