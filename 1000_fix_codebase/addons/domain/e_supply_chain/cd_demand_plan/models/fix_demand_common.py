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
from statistics import NormalDist

from odoo.exceptions import AccessError, UserError

PLANNER = "cd_demand_plan.group_fix_demand_planner"
APPROVER = "cd_demand_plan.group_fix_demand_approver"
ROLE_LABELS = {PLANNER: "Demand Planner", APPROVER: "Demand Plan Approver"}

# z for the one-sided service level (normal distribution). Kept for importers:
# A06 ERP audit M43-08 - every level is now the inverse normal (z_for), so an
# 85% or 97.5% target is honoured instead of silently becoming 95%.
Z_FACTORS = {90: 1.28, 95: 1.65, 98: 2.05, 99: 2.33}
# the service levels the screens offer by default (owner D7: any value works)
DEFAULT_SERVICE_LEVELS = (90.0, 95.0, 98.0, 99.0)

# A06 ERP audit M43-21: the business day is Asia/Dhaka (UTC+6, no DST). M15
# stamps consumed_at in UTC; months and days are Dhaka months and days.
DHAKA_OFFSET = timedelta(hours=6)

PERIOD_RE = re.compile(r"^(\d{4})-(0[1-9]|1[0-2])$")

# Configuration keys (business decisions, report section 7). Defaults are
# the conservative values documented in the runbook.
# A06 ERP audit owner item 9: window 12 months, minimum history 6 months
CFG_FORECAST_WINDOW = "cd_demand_plan.forecast_window_months"  # default 12
CFG_FORECAST_MIN_HISTORY = "cd_demand_plan.forecast_min_history_months"  # default 6
DEFAULT_FORECAST_WINDOW = 12
DEFAULT_FORECAST_MIN_HISTORY = 6
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


def dhaka_today() -> date:
    """Today's business date in Dhaka (M43-21), whatever the server's zone."""
    return (datetime.utcnow() + DHAKA_OFFSET).date()


def dhaka_date(utc_naive: datetime) -> date:
    """The Dhaka business date of a naive UTC timestamp (Odoo Datetime)."""
    return (utc_naive + DHAKA_OFFSET).date()


def _dt(day: date) -> datetime:
    """Dhaka midnight of `day` as the naive UTC timestamp Odoo stores."""
    return datetime.combine(day, time.min) - DHAKA_OFFSET


def z_for(service_level) -> float:
    """M43-08: the one-sided z of a service level in percent, by the inverse
    normal distribution. A level outside 50..99.99 is refused, never replaced
    by a default."""
    try:
        level = float(service_level)
    except (TypeError, ValueError) as exc:
        raise UserError("Service level %r is not a percentage." % (service_level,)) from exc
    if not 50.0 <= level < 100.0:
        raise UserError(
            "Service level %.2f%% is outside 50%% to 99.99%%: no safety stock can be set." % level
        )
    return NormalDist().inv_cdf(level / 100.0)


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
    """Consumed quantity per calendar (Dhaka) month, `months` buckets from `first`."""
    buckets = [0.0] * months
    for row in _consumption_rows(env, company, part, location, first, add_months(first, months)):
        at = dhaka_date(row["consumed_at"])
        idx = (at.year - first.year) * 12 + at.month - first.month
        if 0 <= idx < months:
            buckets[idx] += row["quantity"] or 0.0
    return buckets


def consumed_by_day(env, company, part, location, first: date, days: int) -> list:
    buckets = [0.0] * days
    for row in _consumption_rows(env, company, part, location, first, first + timedelta(days=days)):
        idx = (dhaka_date(row["consumed_at"]) - first).days
        if 0 <= idx < days:
            buckets[idx] += row["quantity"] or 0.0
    return buckets


def has_usable_history(env, company, part, location) -> bool:
    """BRU-DPL-01 readiness, as the forecast's own test: enough of the last
    window months carry M15 consumption for a statistical figure."""
    window = param(env, CFG_FORECAST_WINDOW, DEFAULT_FORECAST_WINDOW, int)
    minimum = param(env, CFG_FORECAST_MIN_HISTORY, DEFAULT_FORECAST_MIN_HISTORY, int)
    first = add_months(dhaka_today().replace(day=1), -window)
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
    """Available OWNED, UNRESTRICTED stock of the part (at the location when
    given). M43-07: stock in quarantine, inspection or blocked is not usable
    to serve demand, so it is not part of the position."""
    domain = [
        ("company_id", "=", company.id),
        ("part_id", "=", part.id),
        ("ownership_class", "=", "owned"),
        ("stock_status", "=", "unrestricted"),
    ]
    if location:
        domain.append(("location_id", "=", location.id))
    rows = env["fix.stock.onhand"].sudo().search_read(domain, ["qty", "reserved"])
    return round(sum((r["qty"] or 0.0) - (r["reserved"] or 0.0) for r in rows), 3)


# ------------------------------------------------------------------ M16 readers
def on_order(env, company, products, location=None, part=None) -> float:
    """Quantity already on its way (M43-05).

    With a location the netting is the LOCATION's, as its stock and policy
    are: open requisitions raised for the location's branch, the unreceived
    balance of open purchase orders delivering to that branch, M15 transfers
    dispatched to the location and not yet received, and M44 import orders
    receiving at the location that are not yet received (an import with an M16
    PO already counted for the branch is not counted twice). Without a
    location the figure is company-wide, imports with no M16 PO included."""
    if not products:
        return 0.0
    branch = location.branch_id if location and "branch_id" in location._fields else None
    req_domain = [
        ("company_id", "=", company.id),
        ("product_id", "in", products.ids),
        ("state", "not in", CLOSED_REQ_STATES),
    ]
    po_domain = [
        ("product_id", "in", products.ids),
        ("order_id.company_id", "=", company.id),
        ("order_id.state", "in", OPEN_PO_STATES),
    ]
    if location:
        # a location with no branch has nothing of M16's addressed to it
        req_domain.append(("branch_id", "=", branch.id if branch else False))
        po_domain.append(("order_id.branch_id", "=", branch.id if branch else False))
    reqs = env["fix.requisition"].sudo().search_read(req_domain, ["qty"])
    qty = sum(r["qty"] or 0.0 for r in reqs)
    lines = (
        env["fix.purchase.order.line"]
        .sudo()
        .search_read(po_domain, ["qty_ordered", "qty_received", "order_id"])
    )
    counted_pos = {r["order_id"][0] for r in lines if r["order_id"]}
    qty += sum(max((r["qty_ordered"] or 0.0) - (r["qty_received"] or 0.0), 0.0) for r in lines)
    parts = part or env["fix.spare.part"].sudo().search([("product_id", "in", products.ids)])
    if location and parts and "fix.stock.transfer.line" in env:
        for tl in (
            env["fix.stock.transfer.line"]
            .sudo()
            .search(
                [
                    ("part_id", "in", parts.ids),
                    ("transfer_id.to_location_id", "=", location.id),
                    ("transfer_id.state", "=", "dispatched"),
                ]
            )
        ):
            qty += max((tl.qty or 0.0) - (tl.received_qty or 0.0), 0.0)
    if parts and "fix.import.order.line" in env:
        domain = [
            ("part_id", "in", parts.ids),
            ("order_id.company_id", "=", company.id),
            ("order_id.state", "in", ("draft", "shipped", "customs", "cleared")),
        ]
        if location:
            domain.append(("order_id.location_id", "=", location.id))
        for il in env["fix.import.order.line"].sudo().search(domain):
            po = il.order_id.purchase_order_id
            if po and po.id in counted_pos:
                continue
            qty += il.quantity or 0.0
    return round(qty, 3)


# ------------------------------------------------------------------ formulas
def safety_stock(service_level, stddev, lead_days, avg_daily=0.0, lead_stddev=0.0) -> float:
    """M43-01 / BRU-DPL-07: SS = z x sqrt(L x sd_d^2 + d^2 x sd_L^2): demand
    variability over the lead time AND lead-time variability at the average
    demand. z is the inverse normal of the service level (M43-08)."""
    lead = max(lead_days or 0.0, 0.0)
    variance = lead * (stddev or 0.0) ** 2 + (avg_daily or 0.0) ** 2 * (lead_stddev or 0.0) ** 2
    if variance <= 0:
        return 0.0
    return round(z_for(service_level) * sqrt(variance), 2)


def order_up_to(position, rop, target) -> float:
    """S8 / M43-06: order when the INVENTORY POSITION (usable stock + on
    order) is at or below the reorder point, up to the target (max) level.
    The reorder point already carries the lead-time demand, so the forecast is
    not subtracted a second time. Never above the target, never negative."""
    if position > rop:
        return 0.0
    return round(max(0.0, target - position), 3)


def to_bdt(env, company, amount, currency, on_date, rate=None) -> float:
    """M43-04 / M43-15: an amount in BDT. A stamped rate (BDT per unit, e.g.
    the PO's approval rate) wins; else the currency's rate on the date. A
    foreign amount with no rate is refused, never read as BDT."""
    bdt = env.ref("base.BDT")
    if not currency or currency == bdt:
        return amount or 0.0
    if rate:
        return round((amount or 0.0) * rate, 2)
    if not currency.sudo().rate_ids:
        raise UserError(
            "No %s rate to convert %.2f to BDT: record the exchange rate first."
            % (currency.name, amount or 0.0)
        )
    return round(currency._convert(amount or 0.0, bdt, company, on_date), 2)


def po_line_bdt_price(env, company, line) -> float:
    """The unit price of a purchase-order line in BDT (M43-04)."""
    order = line.order_id
    rate = order.fx_rate if "fx_rate" in order._fields and order.fx_rate else None
    when = order.date_order if "date_order" in order._fields and order.date_order else dhaka_today()
    if isinstance(when, datetime):
        when = when.date()
    currency = line.currency_id if "currency_id" in line._fields else order.currency_id
    return to_bdt(env, company, line.unit_price or 0.0, currency, when, rate)


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
        .search(
            [("order_id.company_id", "=", company.id), ("order_id.state", "in", OPEN_PO_STATES)]
        )
    )
    # M43-15: a USD purchase order is converted, never added to BDT as it is
    committed = sum(r["estimate_amount"] or 0.0 for r in reqs) + sum(
        max((ln.qty_ordered or 0.0) - (ln.qty_received or 0.0), 0.0)
        * po_line_bdt_price(env, company, ln)
        for ln in po_lines
    )
    remaining = round(planned - actual - committed, 2)
    return remaining, (
        "Parts budget (%s): planned BDT %.2f, actual BDT %.2f, committed BDT %.2f, "
        "remaining BDT %.2f."
        % (", ".join(accounts.mapped("code")), planned, actual, committed, remaining)
    )
