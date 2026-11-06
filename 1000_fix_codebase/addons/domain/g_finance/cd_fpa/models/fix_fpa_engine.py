# fix_fpa_engine — M54 computations over POSTED data only.
#
# Every figure here is read from the live records: posted journal items and
# their fix.journal.dimension tags (GL), service orders and work orders
# (cd_service_order), parts consumption scans (cd_inventory), approved
# payslips (cd_payroll_bd) and issued AR invoices (cd_billing_engine).
# Nothing is stored or seeded; where a source record is missing the row
# says so (an honest gap) instead of inventing a number.
from collections import defaultdict
from datetime import UTC, date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models

REVENUE_TYPES = ("income", "income_other")
DIRECT_COST_TYPES = ("expense_direct_cost",)
OPEX_TYPES = ("expense", "expense_depreciation")
PNL_TYPES = REVENUE_TYPES + DIRECT_COST_TYPES + OPEX_TYPES
REVENUE_STATES = ("issued", "paid", "credited")
PAYROLL_STATES = ("approved", "paid", "posted")
JOB_EXCLUDED_STATES = ("draft", "cancelled")


def fy_window(today=None):
    """The Bangladesh fiscal year (July-June) containing `today`."""
    today = today or fields.Date.today()
    start = date(today.year if today.month >= 7 else today.year - 1, 7, 1)
    return start, date(start.year + 1, 6, 30)


def as_window(date_from=None, date_to=None):
    """Normalise a report window; defaults to the current fiscal year."""
    fy_from, fy_to = fy_window()
    d_from = fields.Date.to_date(date_from) if date_from else fy_from
    d_to = fields.Date.to_date(date_to) if date_to else fy_to
    if d_to < d_from:
        d_from, d_to = d_to, d_from
    return d_from, d_to


def month_starts(d_from, d_to, cap=36):
    out, cur = [], d_from.replace(day=1)
    while cur <= d_to and len(out) < cap:
        out.append(cur)
        cur = cur + relativedelta(months=1)
    return out


def months_between(d_from, d_to):
    return max(1, len(month_starts(d_from, d_to, cap=1200)))


def pct(part, whole):
    return round(100.0 * part / whole, 1) if whole else None


def money(value):
    return round(value or 0.0, 2)


class FixFpaEngine(models.AbstractModel):
    _name = "fix.fpa.engine"
    _description = "FP&A Computation Engine"

    # ------------------------------------------------------------------ GL

    def _companies(self):
        return self.env.companies.ids

    @api.model
    def gl_lines(self, date_from, date_to, account_types=PNL_TYPES, account_ids=None):
        """Posted journal items in the window, each with its account type and
        its dimension tags (branch / business line / cost centre)."""
        domain = [
            ("parent_state", "=", "posted"),
            ("date", ">=", date_from),
            ("date", "<=", date_to),
            ("company_id", "in", self._companies()),
        ]
        if account_ids is not None:
            domain.append(("account_id", "in", list(account_ids)))
        elif account_types:
            domain.append(("account_id.account_type", "in", list(account_types)))
        lines = self.env["account.move.line"].search_read(
            domain, ["balance", "account_id", "date", "partner_id"]
        )
        if not lines:
            return []
        acc_ids = {ln["account_id"][0] for ln in lines if ln["account_id"]}
        acc_type = {
            a["id"]: a["account_type"]
            for a in self.env["account.account"].browse(list(acc_ids)).read(["account_type"])
        }
        dims = {}
        for d in self.env["fix.journal.dimension"].search_read(
            [("move_line_id", "in", [ln["id"] for ln in lines])],
            ["move_line_id", "branch_id", "business_line", "cost_centre"],
        ):
            dims[d["move_line_id"][0]] = d
        out = []
        for ln in lines:
            dim = dims.get(ln["id"]) or {}
            acc = ln["account_id"][0] if ln["account_id"] else False
            out.append(
                {
                    "id": ln["id"],
                    "date": ln["date"],
                    "balance": ln["balance"] or 0.0,
                    "account_id": acc,
                    "account_type": acc_type.get(acc),
                    "partner_id": ln["partner_id"][0] if ln["partner_id"] else False,
                    "branch_id": dim["branch_id"][0] if dim.get("branch_id") else False,
                    "business_line": dim.get("business_line") or False,
                    "cost_centre": dim.get("cost_centre") or False,
                }
            )
        return out

    @staticmethod
    def signed_amount(line):
        """Revenue positive (credit), costs positive (debit)."""
        if line["account_type"] in REVENUE_TYPES:
            return -line["balance"]
        return line["balance"]

    @api.model
    def pnl_by(self, date_from, date_to, key):
        """{key value: {revenue, direct, opex}} from posted P&L items."""
        out = defaultdict(lambda: {"revenue": 0.0, "direct": 0.0, "opex": 0.0})
        for ln in self.gl_lines(date_from, date_to):
            bucket = out[ln[key]]
            if ln["account_type"] in REVENUE_TYPES:
                bucket["revenue"] += -ln["balance"]
            elif ln["account_type"] in DIRECT_COST_TYPES:
                bucket["direct"] += ln["balance"]
            elif ln["account_type"] in OPEX_TYPES:
                bucket["opex"] += ln["balance"]
        return out

    @api.model
    def pnl_totals(self, date_from, date_to):
        tot = {"revenue": 0.0, "direct": 0.0, "opex": 0.0}
        for bucket in self.pnl_by(date_from, date_to, "account_type").values():
            for k in tot:
                tot[k] += bucket[k]
        return tot

    @api.model
    def pool_amount(self, pools, date_from, date_to):
        """Posted balance of the pools' element accounts in the window."""
        accounts = pools.element_ids.account_ids
        if not accounts:
            return 0.0
        return sum(
            ln["balance"] for ln in self.gl_lines(date_from, date_to, account_ids=accounts.ids)
        )

    # ------------------------------------------------------------ business lines

    @api.model
    def business_lines(self):
        return (
            self.env["fix.business.line"]
            .with_context(active_test=True)
            .search(["|", ("company_id", "=", False), ("company_id", "in", self._companies())])
        )

    # ---------------------------------------------------------------- operations

    def _has(self, model):
        return model in self.env

    def _dt_bounds(self, date_from, date_to):
        """Half-open UTC bounds for a window given as the USER's calendar dates.

        Stored timestamps (`create_date`, work-order finish stamps) are UTC,
        while the window arrives as the user's local dates. Combining those
        dates with `time.min` and comparing them directly dropped the first
        `utcoffset` hours of every local day: for Asia/Dhaka (+06) nothing
        created between local 00:00 and 05:59 counted in that day's window, and
        every such record was reported against the previous day instead. It is
        the same defect, and the same fix, as
        `cd_p03_portal/controllers/p03_service_order_api.py::_day_start_utc`.
        """
        tz = ZoneInfo(self.env.context.get("tz") or self.env.user.tz or "UTC")
        start = datetime.combine(date_from, time.min, tzinfo=tz)
        end = datetime.combine(date_to + timedelta(days=1), time.min, tzinfo=tz)
        return (
            start.astimezone(UTC).replace(tzinfo=None),
            end.astimezone(UTC).replace(tzinfo=None),
        )

    @api.model
    def service_orders(self, date_from, date_to, extra_domain=None):
        if not self._has("fix.service.order"):
            return self.env["res.partner"].browse()
        start, end = self._dt_bounds(date_from, date_to)
        domain = [
            ("create_date", ">=", start),
            ("create_date", "<", end),
            ("state", "not in", JOB_EXCLUDED_STATES),
            ("company_id", "in", self._companies()),
            *(extra_domain or []),
        ]
        return self.env["fix.service.order"].search(domain, order="id")

    @api.model
    def productive_hours(self, date_from, date_to):
        """{employee id: hours} from work orders finished in the window."""
        hours = defaultdict(float)
        if not self._has("fix.work.order"):
            return hours
        start, end = self._dt_bounds(date_from, date_to)
        for wo in self.env["fix.work.order"].search_read(
            [
                ("end_time", ">=", start),
                ("end_time", "<", end),
                ("duration_hours", ">", 0),
                ("company_id", "in", self._companies()),
            ],
            ["technician_id", "duration_hours", "order_id"],
        ):
            emp = wo["technician_id"][0] if wo["technician_id"] else False
            if emp:
                hours[emp] += wo["duration_hours"]
        return hours

    @api.model
    def payroll_cost(self, date_from, date_to, employee_ids=None):
        """{employee id: gross + employer PF} of payslips in approved (or
        later) payroll periods overlapping the window, prorated by the days
        of the period that fall inside it. Read with sudo: management
        costing needs the aggregate, never the payslip detail — callers
        decide who may see a per-person figure."""
        cost = defaultdict(float)
        if not self._has("fix.payslip"):
            return cost
        domain = [
            ("period_id.period_start", "<=", date_to),
            ("period_id.period_end", ">=", date_from),
            ("period_id.state", "in", PAYROLL_STATES),
            ("company_id", "in", self._companies()),
        ]
        if employee_ids is not None:
            domain.append(("employee_id", "in", list(employee_ids)))
        for slip in self.env["fix.payslip"].sudo().search(domain):
            period = slip.period_id
            days = (period.period_end - period.period_start).days + 1
            inside = (
                min(period.period_end, date_to) - max(period.period_start, date_from)
            ).days + 1
            share = inside / days if days > 0 else 0.0
            cost[slip.employee_id.id] += ((slip.gross or 0.0) + (slip.pf_employer or 0.0)) * share
        return cost

    @api.model
    def technician_rates(self, date_from, date_to):
        """Technician loaded cost per productive hour:
        (payroll cost + overhead share) / productive hours, where the
        overhead is the posted cost of the pools flagged "load into
        technician rate", spread by productive-hour share."""
        hours = self.productive_hours(date_from, date_to)
        technicians = set(hours)
        for order in self.service_orders(date_from, date_to).filtered("technician_id"):
            technicians.add(order.technician_id.id)
        payroll = self.payroll_cost(date_from, date_to, technicians)
        pools = self.env["fix.cost.pool"].search(
            [("include_in_labour_rate", "=", True), ("company_id", "in", self._companies())]
        )
        overhead_total = self.pool_amount(pools, date_from, date_to) if pools else 0.0
        total_hours = sum(hours.values())
        rates = {}
        for emp in technicians:
            h = hours.get(emp, 0.0)
            share = overhead_total * h / total_hours if total_hours else 0.0
            pay = payroll.get(emp, 0.0)
            gaps = []
            if not pay:
                gaps.append("no approved payslip in the period")
            if not h:
                gaps.append("no work-order hours recorded")
            rates[emp] = {
                "payroll": pay,
                "overhead": share,
                "hours": h,
                "rate": (pay + share) / h if (h and pay) else None,
                "gaps": gaps,
            }
        return rates, overhead_total

    @api.model
    def job_costs(self, date_from, date_to):
        """Per service order received in the window: revenue (issued AR
        invoices net of VAT and credits), parts at cost (inventory
        consumption scans; the work-order part list only when no scan
        exists), labour hours x the technician's loaded rate."""
        orders = self.service_orders(date_from, date_to)
        if not orders:
            return []
        rates, _overhead = self.technician_rates(date_from, date_to)
        names = {o.name: o.id for o in orders}

        revenue = defaultdict(float)
        if self._has("fix.ar.invoice"):
            for inv in self.env["fix.ar.invoice"].search_read(
                [
                    ("source_model", "=", "fix.service.order"),
                    ("source_id", "in", orders.ids),
                    ("state", "in", REVENUE_STATES),
                ],
                ["source_id", "taxable_amount", "total_payable", "credited_amount"],
            ):
                net = inv["taxable_amount"] or 0.0
                if inv["total_payable"] and inv["credited_amount"]:
                    net *= max(0.0, 1 - inv["credited_amount"] / inv["total_payable"])
                revenue[inv["source_id"]] += net

        scanned = defaultdict(float)
        if self._has("fix.stock.consumption"):
            for scan in self.env["fix.stock.consumption"].search_read(
                [("service_order_ref", "in", list(names)), ("state", "=", "consumed")],
                ["service_order_ref", "total_cost"],
            ):
                scanned[names[scan["service_order_ref"]]] += scan["total_cost"] or 0.0

        wo_parts = defaultdict(float)
        hours = defaultdict(float)
        labour = defaultdict(float)
        unrated = defaultdict(bool)
        if self._has("fix.work.order"):
            work_orders = self.env["fix.work.order"].search([("order_id", "in", orders.ids)])
            for wo in work_orders:
                oid = wo.order_id.id
                for part in wo.parts_consumed_ids:
                    wo_parts[oid] += (part.quantity or 0.0) * (part.unit_cost or 0.0)
                if wo.duration_hours:
                    hours[oid] += wo.duration_hours
                    emp = (wo.technician_id or wo.order_id.technician_id).id
                    rate = (rates.get(emp) or {}).get("rate")
                    if rate is None:
                        unrated[oid] = True
                    else:
                        labour[oid] += wo.duration_hours * rate

        rows = []
        for order in orders:
            oid = order.id
            gaps = []
            if oid in scanned:
                parts = scanned[oid]
            else:
                parts = wo_parts.get(oid, 0.0)
                if parts:
                    gaps.append("parts from work-order list (no consumption scan)")
            if not hours.get(oid):
                gaps.append("no labour hours recorded")
            elif unrated.get(oid):
                gaps.append("technician has no loaded rate")
            if not revenue.get(oid) and order.order_category not in ("warranty", "goodwill"):
                gaps.append("no issued invoice")
            rev = revenue.get(oid, 0.0)
            cost = parts + labour.get(oid, 0.0)
            rows.append(
                {
                    "order_id": oid,
                    "order": order.name,
                    "customer_id": order.customer_id.id,
                    "customer": order.customer_id.display_name,
                    "branch": order.branch_id.display_name,
                    "branch_id": order.branch_id.id,
                    "technician": order.technician_id.name or "",
                    "category": dict(order._fields["order_category"].selection).get(
                        order.order_category, order.order_category
                    ),
                    "category_key": order.order_category,
                    "revenue": rev,
                    "parts_cost": parts,
                    "labour_hours": hours.get(oid, 0.0),
                    "labour_cost": labour.get(oid, 0.0),
                    "total_cost": cost,
                    "margin": rev - cost,
                    "margin_pct": pct(rev - cost, rev),
                    "complete": bool(hours.get(oid)) and not unrated.get(oid),
                    "gaps": gaps,
                }
            )
        return rows

    @api.model
    def branch_driver(self, date_from, date_to, basis):
        """{branch id: driver quantity} for an allocation basis."""
        out = defaultdict(float)
        if basis == "service_orders":
            for order in self.service_orders(date_from, date_to):
                out[order.branch_id.id] += 1
        elif basis == "labour_hours" and self._has("fix.work.order"):
            start, end = self._dt_bounds(date_from, date_to)
            for wo in self.env["fix.work.order"].search(
                [
                    ("end_time", ">=", start),
                    ("end_time", "<", end),
                    ("duration_hours", ">", 0),
                    ("company_id", "in", self._companies()),
                ]
            ):
                out[wo.order_id.branch_id.id] += wo.duration_hours
        elif basis == "revenue":
            for key, bucket in self.pnl_by(date_from, date_to, "branch_id").items():
                if key and bucket["revenue"] > 0:
                    out[key] += bucket["revenue"]
        return out

    @api.model
    def business_line_driver(self, date_from, date_to):
        out = defaultdict(float)
        codes = {bl.code: bl.id for bl in self.business_lines()}
        for code, bucket in self.pnl_by(date_from, date_to, "business_line").items():
            if code in codes and bucket["revenue"] > 0:
                out[codes[code]] += bucket["revenue"]
        return out

    # ------------------------------------------------------------- budgets

    @staticmethod
    def clip(line, date_from=None, date_to=None):
        """(from, to) of the line's window inside the report window, or None."""
        start = max(line.date_from, date_from) if date_from else line.date_from
        end = min(line.date_to, date_to) if date_to else line.date_to
        return (start, end) if start <= end else None

    @api.model
    def planned_in_window(self, line, date_from=None, date_to=None):
        """The part of a line's plan that falls in the report window, pro rata
        to days (A08 M54-6: a September report used to compare the full-year
        plan with August+September actuals)."""
        window = self.clip(line, date_from, date_to)
        if not window:
            return 0.0
        total_days = (line.date_to - line.date_from).days + 1
        days = (window[1] - window[0]).days + 1
        if days >= total_days:
            return line.planned_amount
        return round(line.planned_amount * days / total_days, 2)

    @api.model
    def line_actuals(self, budget_lines, date_from=None, date_to=None):
        """{budget line id: actual} from posted GL items matching the line's
        account, window and dimension filters — the line's window clipped to
        the report window when one is given. Revenue lines are positive
        credits, cost/capital lines positive debits."""
        if not budget_lines:
            return {}
        d_from = min(budget_lines.mapped("date_from"))
        d_to = max(budget_lines.mapped("date_to"))
        if date_from:
            d_from = max(d_from, date_from)
        if date_to:
            d_to = min(d_to, date_to)
        if d_from > d_to:
            return {bl.id: 0.0 for bl in budget_lines}
        gl = self.gl_lines(d_from, d_to, account_ids=budget_lines.account_id.ids)
        by_account = defaultdict(list)
        for ln in gl:
            by_account[ln["account_id"]].append(ln)
        out = {}
        for bl in budget_lines:
            total = 0.0
            window = self.clip(bl, date_from, date_to)
            if not window:
                out[bl.id] = 0.0
                continue
            for ln in by_account.get(bl.account_id.id, []):
                if not (window[0] <= ln["date"] <= window[1]):
                    continue
                if bl.branch_id and ln["branch_id"] != bl.branch_id.id:
                    continue
                if bl.business_line_id and ln["business_line"] != bl.business_line_id.code:
                    continue
                if bl.cost_centre and ln["cost_centre"] != bl.cost_centre:
                    continue
                total += self.signed_amount(ln)
            out[bl.id] = total
        return out

    @api.model
    def drivers_from_actuals(self, date_from, date_to):
        """Base values of the scenario drivers, measured on the window."""
        months = months_between(date_from, date_to)
        jobs = self.job_costs(date_from, date_to)
        n = len(jobs)
        with_rev = [j for j in jobs if j["revenue"]]
        rev = sum(j["revenue"] for j in with_rev)
        parts = sum(j["parts_cost"] for j in with_rev)
        with_hours = [j for j in jobs if j["labour_hours"]]
        hrs = sum(j["labour_hours"] for j in with_hours)
        lab = sum(j["labour_cost"] for j in with_hours if j["complete"])
        rated_hrs = sum(j["labour_hours"] for j in with_hours if j["complete"])
        totals = self.pnl_totals(date_from, date_to)
        return {
            "orders_per_month": n / months,
            "revenue_per_order": rev / len(with_rev) if with_rev else 0.0,
            "parts_cost_pct": 100.0 * parts / rev if rev else 0.0,
            "labour_hours_per_order": hrs / len(with_hours) if with_hours else 0.0,
            "loaded_labour_rate": lab / rated_hrs if rated_hrs else 0.0,
            "overhead_per_month": totals["opex"] / months,
        }

    # -------------------------------------------------------------- helpers

    @staticmethod
    def deciles(rows, key):
        """Rank rows by `key` (descending) and stamp decile 1 (best)..10."""
        ordered = sorted(rows, key=lambda r: r[key], reverse=True)
        n = len(ordered)
        for idx, row in enumerate(ordered, start=1):
            row["rank"] = idx
            row["decile"] = min(10, (idx - 1) * 10 // n + 1)
        return ordered
