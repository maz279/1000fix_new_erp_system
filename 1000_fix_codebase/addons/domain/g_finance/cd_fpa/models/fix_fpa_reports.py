# fix_fpa_reports — the M54 table reports served to the P03 workspace
# (controllers/a08/m54.py REPORTS). Each returns
# {title, cols, labels, rows, totals?, notes?, empty?}; every figure comes
# from fix.fpa.engine reads of posted / live records.
from collections import defaultdict

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from odoo.exceptions import AccessError

from .fix_fpa_engine import as_window, money, month_starts, pct

MAX_JOB_ROWS = 500
MARGIN_BANDS = [
    ("loss", "Loss (< 0%)", None, 0.0),
    ("b0", "0 – 20%", 0.0, 20.0),
    ("b20", "20 – 40%", 20.0, 40.0),
    ("b40", "40 – 60%", 40.0, 60.0),
    ("b60", "60% and above", 60.0, None),
]


def _label_window(d_from, d_to):
    return f"{d_from:%d %b %Y} – {d_to:%d %b %Y}"


def _sum(rows, cols):
    return {c: money(sum((r.get(c) or 0.0) for r in rows)) for c in cols}


class FixFpaEngineReports(models.AbstractModel):
    _inherit = "fix.fpa.engine"

    # ------------------------------------------------------------ costing

    @api.model
    def report_job_costing(self, date_from=None, date_to=None, **_kw):
        d_from, d_to = as_window(date_from, date_to)
        jobs = self.job_costs(d_from, d_to)
        cols = [
            "order",
            "customer",
            "branch",
            "technician",
            "category",
            "revenue",
            "parts_cost",
            "labour_hours",
            "labour_cost",
            "margin",
            "margin_pct",
            "gaps",
        ]
        labels = {
            "order": "Service Order",
            "customer": "Customer",
            "branch": "Branch",
            "technician": "Technician",
            "category": "Category",
            "revenue": "Revenue (net)",
            "parts_cost": "Parts at Cost",
            "labour_hours": "Labour Hours",
            "labour_cost": "Labour Cost",
            "margin": "Job Margin",
            "margin_pct": "Margin %",
            "gaps": "Costing Gaps",
        }
        rows = []
        for j in sorted(jobs, key=lambda r: r["margin"]):
            row = {c: j[c] for c in cols if c != "gaps"}
            for c in ("revenue", "parts_cost", "labour_cost", "margin"):
                row[c] = money(row[c])
            row["labour_hours"] = round(row["labour_hours"], 2)
            row["gaps"] = "; ".join(j["gaps"]) or "complete"
            rows.append(row)
        complete = sum(1 for j in jobs if j["complete"])
        totals = _sum(rows, ["revenue", "parts_cost", "labour_hours", "labour_cost", "margin"])
        totals["order"] = f"{len(jobs)} jobs"
        totals["margin_pct"] = pct(totals["margin"], totals["revenue"])
        notes = [
            "Service orders received in the window (draft and cancelled excluded).",
            "Revenue = issued AR invoices for the order, net of VAT and credit notes.",
            "Parts = inventory consumption scans at valuation cost; labour = work-order "
            "hours × the technician's loaded rate for the same window.",
            f"Costing complete (labour hours recorded and rated) on {complete} of {len(jobs)} jobs.",
        ]
        if len(rows) > MAX_JOB_ROWS:
            notes.append(
                f"Showing the {MAX_JOB_ROWS} lowest-margin jobs of {len(rows)}; totals cover all."
            )
            rows = rows[:MAX_JOB_ROWS]
        return {
            "title": "Job / work-order costing · " + _label_window(d_from, d_to),
            "cols": cols,
            "labels": labels,
            "rows": rows,
            "totals": totals,
            "notes": notes,
            "empty": "No service orders received in this window.",
        }

    @api.model
    def report_job_margin_distribution(self, date_from=None, date_to=None, **_kw):
        d_from, d_to = as_window(date_from, date_to)
        jobs = self.job_costs(d_from, d_to)
        buckets = defaultdict(list)
        for j in jobs:
            if not j["complete"]:
                buckets["incomplete"].append(j)
            elif not j["revenue"]:
                buckets["no_revenue"].append(j)
            else:
                m = j["margin_pct"]
                for key, _label, lo, hi in MARGIN_BANDS:
                    if (lo is None or m >= lo) and (hi is None or m < hi):
                        buckets[key].append(j)
                        break
        order = [(k, label) for k, label, _lo, _hi in MARGIN_BANDS] + [
            ("no_revenue", "Costed, no revenue (warranty / goodwill / not invoiced)"),
            ("incomplete", "Costing incomplete (no rated labour hours)"),
        ]
        rows = []
        for key, label in order:
            items = buckets.get(key, [])
            rev = sum(j["revenue"] for j in items)
            cost = sum(j["total_cost"] for j in items)
            rows.append(
                {
                    "band": label,
                    "jobs": len(items),
                    "share_pct": pct(len(items), len(jobs)),
                    "revenue": money(rev),
                    "cost": money(cost),
                    "margin": money(rev - cost),
                    "avg_margin": money((rev - cost) / len(items)) if items else 0.0,
                }
            )
        totals = _sum(rows, ["jobs", "revenue", "cost", "margin"])
        totals["band"] = "All jobs"
        return {
            "title": "Job margin distribution · " + _label_window(d_from, d_to),
            "cols": ["band", "jobs", "share_pct", "revenue", "cost", "margin", "avg_margin"],
            "labels": {
                "band": "Margin Band",
                "jobs": "Jobs",
                "share_pct": "% of Jobs",
                "revenue": "Revenue",
                "cost": "Job Cost",
                "margin": "Margin",
                "avg_margin": "Avg Margin / Job",
            },
            "rows": rows if jobs else [],
            "totals": totals if jobs else None,
            "notes": ["Bands use margin % of net revenue on fully costed jobs."],
            "empty": "No service orders received in this window.",
        }

    def _can_see_people_cost(self):
        return self.env.su or (
            ("fix.payslip" in self.env and self.env["fix.payslip"].has_access("read"))
            or self.env.user.has_group("account.group_account_manager")
        )

    @api.model
    def report_technician_loaded_cost(self, date_from=None, date_to=None, **_kw):
        if not self._can_see_people_cost():
            raise AccessError(
                "Technician loaded cost shows per-person pay: it needs payroll read access "
                "or the Finance Manager role."
            )
        d_from, d_to = as_window(date_from, date_to)
        rates, overhead = self.technician_rates(d_from, d_to)
        jobs = defaultdict(int)
        for order in self.service_orders(d_from, d_to).filtered("technician_id"):
            jobs[order.technician_id.id] += 1
        employees = self.env["hr.employee"].sudo().browse(list(rates)).exists()
        names = {e.id: e.name for e in employees}
        rows = []
        for emp, r in rates.items():
            rows.append(
                {
                    "technician": names.get(emp, "#%s" % emp),
                    "payroll": money(r["payroll"]),
                    "overhead": money(r["overhead"]),
                    "hours": round(r["hours"], 2),
                    "rate": money(r["rate"]) if r["rate"] is not None else None,
                    "jobs": jobs.get(emp, 0),
                    "gaps": "; ".join(r["gaps"]) or "complete",
                }
            )
        rows.sort(key=lambda r: (r["rate"] is None, -(r["rate"] or 0)))
        totals = _sum(rows, ["payroll", "overhead", "hours", "jobs"])
        totals["technician"] = f"{len(rows)} technicians"
        totals["rate"] = (
            money((totals["payroll"] + totals["overhead"]) / totals["hours"])
            if totals["hours"]
            else None
        )
        return {
            "title": "Technician loaded cost · " + _label_window(d_from, d_to),
            "cols": ["technician", "payroll", "overhead", "hours", "rate", "jobs", "gaps"],
            "labels": {
                "technician": "Technician",
                "payroll": "Payroll Cost (gross + employer PF)",
                "overhead": "Overhead Share",
                "hours": "Productive Hours",
                "rate": "Loaded Rate / Hour",
                "jobs": "Jobs Assigned",
                "gaps": "Gaps",
            },
            "rows": rows,
            "totals": totals,
            "notes": [
                "Payroll = payslips of approved, paid or posted payroll periods overlapping the "
                "window, prorated by the days of each period inside it.",
                "Overhead = posted cost of the cost pools flagged 'Load into technician rate' "
                f"({money(overhead):,.2f} BDT), spread by productive-hour share.",
                "Productive hours = work-order time (start → end) finished in the window.",
            ],
            "empty": "No technician has work orders or assigned service orders in this window.",
        }

    # ------------------------------------------------------- profitability

    @api.model
    def report_business_line_pnl(self, date_from=None, date_to=None, **_kw):
        d_from, d_to = as_window(date_from, date_to)
        pnl = self.pnl_by(d_from, d_to, "business_line")
        lines = self.business_lines()
        rows, seen, silent = [], set(), []

        def row(code, name, b):
            gross = b["revenue"] - b["direct"]
            contrib = gross - b["opex"]
            return {
                "code": code,
                "line": name,
                "revenue": money(b["revenue"]),
                "direct": money(b["direct"]),
                "gross": money(gross),
                "opex": money(b["opex"]),
                "contribution": money(contrib),
                "margin_pct": pct(contrib, b["revenue"]),
            }

        empty = {"revenue": 0.0, "direct": 0.0, "opex": 0.0}
        for bl in lines:
            b = pnl.get(bl.code, empty)
            seen.add(bl.code)
            if not b["revenue"]:
                silent.append(bl.code)
            rows.append(row(bl.code, bl.name, b))
        for code, b in sorted(pnl.items(), key=lambda kv: str(kv[0])):
            if code and code not in seen:
                rows.append(row(code, "Not in business-line master data", b))
        if pnl.get(False):
            rows.append(row("—", "No business-line tag on the posting", pnl[False]))
        totals = _sum(rows, ["revenue", "direct", "gross", "opex", "contribution"])
        totals["line"] = "Company total"
        totals["margin_pct"] = pct(totals["contribution"], totals["revenue"])
        notes = [
            "Posted journal items on income / direct-cost / expense accounts, grouped by the "
            "business-line dimension; line names come from the business-line master (MD-036).",
            f"{len(lines)} active business lines in master data.",
        ]
        if silent:
            notes.append("No revenue in the window (WRN-DIM-006): " + ", ".join(silent))
        return {
            "title": "Business-line P&L · " + _label_window(d_from, d_to),
            "cols": [
                "code",
                "line",
                "revenue",
                "direct",
                "gross",
                "opex",
                "contribution",
                "margin_pct",
            ],
            "labels": {
                "code": "Code",
                "line": "Business Line",
                "revenue": "Revenue",
                "direct": "Direct Cost",
                "gross": "Gross Margin",
                "opex": "Operating Expense",
                "contribution": "Contribution",
                "margin_pct": "Margin %",
            },
            "rows": rows,
            "totals": totals,
            "notes": notes,
            "empty": "No business lines in master data and no postings in this window.",
        }

    @api.model
    def branch_league(self, d_from, d_to):
        pnl = self.pnl_by(d_from, d_to, "branch_id")
        jobs = defaultdict(int)
        for order in self.service_orders(d_from, d_to):
            jobs[order.branch_id.id] += 1
        branches = (
            self.env["fix.branch"]
            .with_context(active_test=False)
            .search([("company_id", "in", self._companies())])
        )
        rows = []
        empty = {"revenue": 0.0, "direct": 0.0, "opex": 0.0}
        for br in branches:
            b = pnl.get(br.id, empty)
            if not (br.active or b["revenue"] or b["direct"] or b["opex"]):
                continue
            gross = b["revenue"] - b["direct"]
            contrib = gross - b["opex"]
            rows.append(
                {
                    "branch_id": br.id,
                    "branch": f"{br.code} {br.name}",
                    "revenue": money(b["revenue"]),
                    "direct": money(b["direct"]),
                    "gross": money(gross),
                    "opex": money(b["opex"]),
                    "contribution": money(contrib),
                    "margin_pct": pct(contrib, b["revenue"]),
                    "jobs": jobs.get(br.id, 0),
                    "per_job": money(contrib / jobs[br.id]) if jobs.get(br.id) else None,
                }
            )
        rows.sort(key=lambda r: r["contribution"], reverse=True)
        for idx, r in enumerate(rows, start=1):
            r["rank"] = idx
        return rows, pnl.get(False)

    @api.model
    def report_branch_profitability(self, date_from=None, date_to=None, **_kw):
        d_from, d_to = as_window(date_from, date_to)
        rows, unassigned = self.branch_league(d_from, d_to)
        if unassigned:
            gross = unassigned["revenue"] - unassigned["direct"]
            rows.append(
                {
                    "rank": None,
                    "branch": "No branch tag on the posting",
                    "revenue": money(unassigned["revenue"]),
                    "direct": money(unassigned["direct"]),
                    "gross": money(gross),
                    "opex": money(unassigned["opex"]),
                    "contribution": money(gross - unassigned["opex"]),
                    "margin_pct": pct(gross - unassigned["opex"], unassigned["revenue"]),
                    "jobs": None,
                    "per_job": None,
                }
            )
        cols = [
            "rank",
            "branch",
            "revenue",
            "direct",
            "gross",
            "opex",
            "contribution",
            "margin_pct",
            "jobs",
            "per_job",
        ]
        totals = _sum(rows, ["revenue", "direct", "gross", "opex", "contribution", "jobs"])
        totals["branch"] = "Company total"
        totals["margin_pct"] = pct(totals["contribution"], totals["revenue"])
        negative = [r["branch"] for r in rows if r.get("rank") and r["contribution"] < 0]
        notes = [
            "League table by contribution from posted GL items tagged with the branch "
            "dimension; operating expense includes posted overhead allocations.",
            "Jobs = service orders received at the branch in the window.",
        ]
        if negative:
            notes.append(f"{len(negative)} branch(es) with negative contribution.")
        return {
            "title": "Branch profitability league · " + _label_window(d_from, d_to),
            "cols": cols,
            "labels": {
                "rank": "#",
                "branch": "Branch",
                "revenue": "Revenue",
                "direct": "Direct Cost",
                "gross": "Gross Margin",
                "opex": "Opex + Allocated",
                "contribution": "Contribution",
                "margin_pct": "Margin %",
                "jobs": "Jobs",
                "per_job": "Contribution / Job",
            },
            "rows": [{c: r.get(c) for c in cols} for r in rows],
            "totals": totals,
            "notes": notes,
            "empty": "No branches and no postings in this window.",
        }

    @api.model
    def report_customer_profitability(self, date_from=None, date_to=None, **_kw):
        d_from, d_to = as_window(date_from, date_to)
        per = {}
        for j in self.job_costs(d_from, d_to):
            c = per.setdefault(
                j["customer_id"],
                {
                    "customer": j["customer"],
                    "orders": 0,
                    "revenue": 0.0,
                    "parts_cost": 0.0,
                    "labour_cost": 0.0,
                    "incomplete": 0,
                },
            )
            c["orders"] += 1
            c["revenue"] += j["revenue"]
            c["parts_cost"] += j["parts_cost"]
            c["labour_cost"] += j["labour_cost"]
            c["incomplete"] += 0 if j["complete"] else 1
        rows = []
        for c in per.values():
            c["margin"] = c["revenue"] - c["parts_cost"] - c["labour_cost"]
            rows.append(c)
        rows = self.deciles(rows, "margin")
        cols = [
            "rank",
            "decile",
            "customer",
            "orders",
            "revenue",
            "parts_cost",
            "labour_cost",
            "margin",
            "margin_pct",
            "incomplete",
        ]
        out = []
        for r in rows:
            out.append(
                {
                    "rank": r["rank"],
                    "decile": r["decile"],
                    "customer": r["customer"],
                    "orders": r["orders"],
                    "revenue": money(r["revenue"]),
                    "parts_cost": money(r["parts_cost"]),
                    "labour_cost": money(r["labour_cost"]),
                    "margin": money(r["margin"]),
                    "margin_pct": pct(r["margin"], r["revenue"]),
                    "incomplete": r["incomplete"],
                }
            )
        totals = _sum(
            out, ["orders", "revenue", "parts_cost", "labour_cost", "margin", "incomplete"]
        )
        totals["customer"] = f"{len(out)} customers"
        totals["margin_pct"] = pct(totals["margin"], totals["revenue"])
        return {
            "title": "Customer profitability · " + _label_window(d_from, d_to),
            "cols": cols,
            "labels": {
                "rank": "#",
                "decile": "Decile",
                "customer": "Customer",
                "orders": "Orders",
                "revenue": "Revenue",
                "parts_cost": "Parts",
                "labour_cost": "Labour",
                "margin": "Job Margin",
                "margin_pct": "Margin %",
                "incomplete": "Jobs Not Fully Costed",
            },
            "rows": out,
            "totals": totals,
            "notes": [
                "Job margin per customer from job costing (revenue − parts − loaded labour); "
                "decile 1 holds the most profitable tenth.",
                "Branch overhead is not pushed down to customers.",
            ],
            "empty": "No service orders received in this window.",
        }

    @api.model
    def report_unit_economics(self, date_from=None, date_to=None, **_kw):
        d_from, d_to = as_window(date_from, date_to)
        jobs = self.job_costs(d_from, d_to)
        groups = defaultdict(list)
        for j in jobs:
            groups[j["category"]].append(j)

        def stats(label, items):
            n = len(items)
            costed = [j for j in items if j["complete"]]
            rev = sum(j["revenue"] for j in items)
            parts = sum(j["parts_cost"] for j in items)
            labour = sum(j["labour_cost"] for j in costed)
            hours = sum(j["labour_hours"] for j in items)
            c = len(costed)
            # labour averaged over fully costed orders, applied to every order
            labour_total = labour / c * n if c else 0.0
            contrib = rev - parts - labour_total
            return {
                "category": label,
                "orders": n,
                "costed": c,
                "rev_per_order": money(rev / n) if n else None,
                "parts_per_order": money(parts / n) if n else None,
                "hours_per_order": round(hours / n, 2) if n else None,
                "labour_per_costed": money(labour / c) if c else None,
                "contrib_per_order": money(contrib / n) if n else None,
                "contrib_pct": pct(contrib, rev),
            }

        rows = [stats(k, v) for k, v in sorted(groups.items())]
        totals = stats("All repairs", jobs) if jobs else None
        return {
            "title": "Unit economics per repair · " + _label_window(d_from, d_to),
            "cols": [
                "category",
                "orders",
                "costed",
                "rev_per_order",
                "parts_per_order",
                "hours_per_order",
                "labour_per_costed",
                "contrib_per_order",
                "contrib_pct",
            ],
            "labels": {
                "category": "Order Category",
                "orders": "Orders",
                "costed": "Fully Costed",
                "rev_per_order": "Revenue / Order",
                "parts_per_order": "Parts / Order",
                "hours_per_order": "Labour Hours / Order",
                "labour_per_costed": "Labour Cost / Costed Order",
                "contrib_per_order": "Contribution / Order",
                "contrib_pct": "Contribution %",
            },
            "rows": rows,
            "totals": totals,
            "notes": [
                "Contribution per order = revenue − parts − labour, with labour averaged over "
                "fully costed orders (orders without rated hours would understate it).",
            ],
            "empty": "No service orders received in this window.",
        }

    # ---------------------------------------------------------- budgeting

    def approved_budget_lines(self, d_from, d_to, version_id=None, version_type="budget"):
        domain = [
            ("date_from", "<=", d_to),
            ("date_to", ">=", d_from),
            ("company_id", "in", self._companies()),
        ]
        if version_id:
            domain.append(("version_id", "=", int(version_id)))
        else:
            domain += [
                ("version_id.state", "=", "approved"),
                ("version_id.version_type", "=", version_type),
            ]
        return self.env["fix.budget.line"].search(domain)

    @api.model
    def report_budget_variance(self, date_from=None, date_to=None, version_id=None, **_kw):
        d_from, d_to = as_window(date_from, date_to)
        lines = self.approved_budget_lines(d_from, d_to, version_id)
        actuals = self.line_actuals(lines)
        rows = []
        for ln in lines:
            actual = actuals.get(ln.id, 0.0)
            var = actual - ln.planned_amount if ln.is_revenue else ln.planned_amount - actual
            rows.append(
                {
                    "version": ln.version_id.name,
                    "period": f"{ln.date_from:%b %Y}"
                    if ln.date_from.replace(day=1) == ln.date_to.replace(day=1)
                    else f"{ln.date_from} – {ln.date_to}",
                    "account": ln.account_id.display_name,
                    "branch": ln.branch_id.display_name or "",
                    "business_line": ln.business_line_id.display_name or "",
                    "cost_centre": ln.cost_centre or "",
                    "planned": money(ln.planned_amount),
                    "actual": money(actual),
                    "variance": money(var),
                    "variance_pct": pct(var, ln.planned_amount),
                    "flag": "Favourable" if var >= 0 else "Adverse",
                }
            )
        totals = _sum(rows, ["planned", "actual", "variance"])
        totals["version"] = f"{len(rows)} lines"
        adverse = sum(1 for r in rows if r["flag"] == "Adverse")
        return {
            "title": "Budget vs actual · " + _label_window(d_from, d_to),
            "cols": [
                "version",
                "period",
                "account",
                "branch",
                "business_line",
                "cost_centre",
                "planned",
                "actual",
                "variance",
                "variance_pct",
                "flag",
            ],
            "labels": {
                "version": "Version",
                "period": "Period",
                "account": "Account",
                "branch": "Branch",
                "business_line": "Business Line",
                "cost_centre": "Cost Centre",
                "planned": "Budget",
                "actual": "Actual (GL)",
                "variance": "Variance",
                "variance_pct": "Variance %",
                "flag": "Status",
            },
            "rows": rows,
            "totals": totals,
            "notes": [
                "Lines of APPROVED budget versions overlapping the window; actual = posted GL "
                "on the line's account, period and dimension filters.",
                "Variance is signed favourable-positive: revenue above budget or cost below it.",
                f"{adverse} adverse line(s).",
            ],
            "empty": "No approved budget lines overlap this window.",
        }

    @api.model
    def report_rolling_forecast(self, date_from=None, date_to=None, **_kw):
        d_from, d_to = as_window(date_from, date_to)
        # context_today, not Date.today(): the window the caller passes is in
        # the user's calendar, and Bangladesh runs UTC+6. Between 18:00 UTC
        # and midnight UTC the two disagree, and on the first of the month
        # they disagree by a MONTH — the current month then failed to match
        # its own row and fell through to the run-rate basis
        # (found 2026-11-01 while certifying A04).
        today = fields.Date.context_today(self)
        current = today.replace(day=1)
        months = month_starts(d_from, d_to, cap=24)
        # actuals per month (revenue / cost) from the posted GL
        actual = defaultdict(lambda: [0.0, 0.0])
        hist_from = min(months[0], current - relativedelta(months=3)) if months else d_from
        for ln in self.gl_lines(hist_from, max(d_to, today)):
            m = ln["date"].replace(day=1)
            if ln["account_type"] in ("income", "income_other"):
                actual[m][0] += -ln["balance"]
            else:
                actual[m][1] += ln["balance"]
        # the approved forecast version, when one covers the month
        fc_lines = self.approved_budget_lines(d_from, d_to, version_type="forecast")
        forecast = defaultdict(lambda: [0.0, 0.0])
        fc_name = defaultdict(str)
        for ln in fc_lines:
            m = ln.date_from.replace(day=1)
            forecast[m][0 if ln.is_revenue else 1] += ln.planned_amount
            fc_name[m] = ln.version_id.name
        closed = [current - relativedelta(months=k) for k in (1, 2, 3)]
        run_rev = sum(actual[m][0] for m in closed) / 3.0
        run_cost = sum(actual[m][1] for m in closed) / 3.0
        rows, cum = [], 0.0
        for m in months:
            if m < current:
                basis, rev, cost = "Actual", *actual[m]
            elif m == current:
                basis, rev, cost = "Actual (month to date)", *actual[m]
            elif m in forecast:
                basis, rev, cost = f"Forecast: {fc_name[m]}", *forecast[m]
            else:
                basis, rev, cost = "Run-rate (avg of last 3 closed months)", run_rev, run_cost
            net = rev - cost
            cum += net
            rows.append(
                {
                    "month": f"{m:%b %Y}",
                    "basis": basis,
                    "revenue": money(rev),
                    "cost": money(cost),
                    "net": money(net),
                    "cumulative": money(cum),
                }
            )
        totals = _sum(rows, ["revenue", "cost", "net"])
        totals["month"] = "Window outlook"
        return {
            "title": "Rolling forecast · " + _label_window(d_from, d_to),
            "cols": ["month", "basis", "revenue", "cost", "net", "cumulative"],
            "labels": {
                "month": "Month",
                "basis": "Basis",
                "revenue": "Revenue",
                "cost": "Cost",
                "net": "Net Result",
                "cumulative": "Cumulative",
            },
            "rows": rows,
            "totals": totals,
            "notes": [
                "Past months are posted actuals; future months use the approved forecast "
                "version where it has lines, otherwise the average of the last three closed months.",
                "Cost = every posted P&L debit (direct cost, expense, depreciation).",
            ],
            "empty": "The window has no months.",
        }

    # ------------------------------------------------------------- board

    @api.model
    def board_pack_rows(self, d_from, d_to):
        rows = []

        def add(section, metric, amount=None, detail=""):
            rows.append({"section": section, "metric": metric, "amount": amount, "detail": detail})

        t = self.pnl_totals(d_from, d_to)
        gross = t["revenue"] - t["direct"]
        add("P&L", "Revenue", money(t["revenue"]))
        add("P&L", "Direct cost", money(t["direct"]))
        add("P&L", "Gross margin", money(gross), f"{pct(gross, t['revenue']) or 0}% of revenue")
        add("P&L", "Operating expense", money(t["opex"]))
        add("P&L", "Operating result", money(gross - t["opex"]))

        lines = self.approved_budget_lines(d_from, d_to)
        actuals = self.line_actuals(lines)
        var = sum(
            (actuals.get(ln.id, 0.0) - ln.planned_amount)
            if ln.is_revenue
            else (ln.planned_amount - actuals.get(ln.id, 0.0))
            for ln in lines
        )
        add("Budget", "Approved budget lines", None, f"{len(lines)} lines")
        add("Budget", "Variance (favourable +)", money(var))

        league, _ = self.branch_league(d_from, d_to)
        if league:
            top, bottom = league[0], league[-1]
            add("Branches", "Top branch", top["contribution"], top["branch"])
            add("Branches", "Bottom branch", bottom["contribution"], bottom["branch"])
            add(
                "Branches",
                "Negative-contribution branches",
                None,
                str(sum(1 for r in league if r["contribution"] < 0)),
            )

        bl_pnl = self.pnl_by(d_from, d_to, "business_line")
        names = {bl.code: bl.name for bl in self.business_lines()}
        ranked = sorted(
            ((code, b["revenue"]) for code, b in bl_pnl.items() if code), key=lambda kv: -kv[1]
        )
        if ranked:
            code, rev = ranked[0]
            add("Business lines", "Largest line by revenue", money(rev), names.get(code, code))
        add(
            "Business lines",
            "Lines without revenue",
            None,
            str(sum(1 for code in names if not bl_pnl.get(code, {}).get("revenue"))),
        )

        jobs = self.job_costs(d_from, d_to)
        complete = [j for j in jobs if j["complete"]]
        add("Jobs", "Service orders received", None, str(len(jobs)))
        add(
            "Jobs",
            "Job costing coverage",
            None,
            f"{pct(len(complete), len(jobs)) or 0}% fully costed",
        )
        if complete:
            add(
                "Jobs",
                "Average margin per fully costed job",
                money(sum(j["margin"] for j in complete) / len(complete)),
            )
        fc = self.report_rolling_forecast(d_from, d_to)
        add("Outlook", "Window net result (actual + forecast)", fc["totals"]["net"])
        return rows

    @api.model
    def report_board_pack(self, date_from=None, date_to=None, **_kw):
        d_from, d_to = as_window(date_from, date_to)
        return {
            "title": "Board pack · " + _label_window(d_from, d_to),
            "cols": ["section", "metric", "amount", "detail"],
            "labels": {
                "section": "Section",
                "metric": "Metric",
                "amount": "Amount (BDT)",
                "detail": "Detail",
            },
            "rows": self.board_pack_rows(d_from, d_to),
            "notes": [
                "Assembled live from the M54 reports for the window. To keep and export a "
                "pack, use Board Pack Archive → Assemble (CSV file on the record).",
            ],
        }
