# A09 · M56 Payroll & Statutory — surfaces, packs and KPIs over payroll periods,
# payslips, BEFTN batches, salary structures, bonus runs, certificates,
# quarterly withholding returns and off-cycle payments.
import datetime

SURFACES = {
    "fix.payroll.period": {
        "order": "period_start desc, id desc",
        "limit": 100,
        "actions": {
            "action_verify_attendance_locked",
            "action_calculate",
            "action_approve",
            "action_pay",
            "action_post",
        },
    },
    "fix.payslip": {
        "order": "period_id desc, employee_id",
        "limit": 500,
        "actions": {"action_compute_separation", "action_compute_retrenchment"},
    },
    "fix.beftn.batch": {
        "order": "submitted_at desc, id desc",
        "limit": 100,
        "actions": {"action_generate_beftn_file", "action_settle"},
    },
    "fix.payroll.structure": {"order": "grade", "limit": 100, "actions": set()},
    "fix.payroll.bonus.run": {
        "order": "bonus_date desc, id desc",
        "limit": 100,
        "actions": {"action_approve", "action_pay"},
    },
    "fix.payroll.certificate": {
        "order": "fiscal_year desc, id desc",
        "limit": 300,
        "actions": {"action_compute_from_payslips", "action_issue"},
    },
    "fix.payroll.return": {
        "order": "period desc",
        "limit": 100,
        "actions": {"action_reconcile_payslips", "action_file"},
    },
    "fix.payroll.offcycle": {
        "order": "payment_date desc, id desc",
        "limit": 300,
        "actions": {"action_approve", "action_pay"},
    },
    "fix.wppf.allocation": {
        "order": "fiscal_year desc, id desc",
        "limit": 100,
        "actions": {"action_calculate", "action_approve", "action_post"},
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
        "empty": empty,
    }


def salary_register(env, date_from=None, date_to=None, **params):
    """Salary register: every payslip in the period with gross and net."""
    slips = env["fix.payslip"].sudo().search([])
    rows = []
    for slip in slips:
        rows.append(
            {
                "period": slip.period_id.name,
                "employee": slip.employee_id.name,
                "basic": round(float(slip.basic or 0.0), 2),
                "gross": round(float(slip.gross or 0.0), 2),
                "overtime": round(float(slip.overtime or 0.0), 2),
                "net": round(float(slip.net or 0.0), 2),
                "state": slip.period_id.state,
            }
        )
    rows.sort(key=lambda r: (r["period"], r["employee"]))
    return _pack(
        "Salary Register — %d slips" % len(rows),
        ["period", "employee", "basic", "gross", "overtime", "net", "state"],
        {
            "period": "Period",
            "employee": "Employee",
            "basic": "Basic",
            "gross": "Gross",
            "overtime": "Overtime",
            "net": "Net Pay",
            "state": "Period State",
        },
        rows,
        ["Figures are the payslip's stored amounts after the gross-to-net engine ran."],
        totals={
            "period": "Total",
            "basic": round(sum(r["basic"] for r in rows), 2),
            "gross": round(sum(r["gross"] for r in rows), 2),
            "overtime": round(sum(r["overtime"] for r in rows), 2),
            "net": round(sum(r["net"] for r in rows), 2),
        },
        empty="No payslips recorded.",
    )


def payroll_cost_allocation(env, date_from=None, date_to=None, **params):
    """Payroll cost allocation by branch: gross, tax and net per branch."""
    slips = env["fix.payslip"].sudo().search([])
    groups = {}
    for slip in slips:
        branch = (
            slip.employee_id.operating_unit_id.name
            if slip.employee_id.operating_unit_id
            else "Unassigned"
        )
        g = groups.setdefault(branch, {"slips": 0, "gross": 0.0, "tax": 0.0, "pf": 0.0, "net": 0.0})
        g["slips"] += 1
        g["gross"] += float(slip.gross or 0.0)
        g["tax"] += float(getattr(slip, "tax_withheld", 0.0) or 0.0)
        g["pf"] += float(getattr(slip, "pf_employee", 0.0) or 0.0)
        g["net"] += float(slip.net or 0.0)
    rows = [
        {
            "branch": k,
            "slips": v["slips"],
            "gross": round(v["gross"], 2),
            "tax": round(v["tax"], 2),
            "pf": round(v["pf"], 2),
            "net": round(v["net"], 2),
        }
        for k, v in sorted(groups.items())
    ]
    return _pack(
        "Payroll Cost Allocation — by branch",
        ["branch", "slips", "gross", "tax", "pf", "net"],
        {
            "branch": "Branch",
            "slips": "Payslips",
            "gross": "Gross",
            "tax": "Income Tax",
            "pf": "PF (Employee)",
            "net": "Net Pay",
        },
        rows,
        [
            "Payroll cost by the employee's operating unit; the M19 posting consumes these "
            "figures per period."
        ],
        totals={
            "branch": "Total",
            "slips": sum(r["slips"] for r in rows),
            "gross": round(sum(r["gross"] for r in rows), 2),
            "tax": round(sum(r["tax"] for r in rows), 2),
            "pf": round(sum(r["pf"] for r in rows), 2),
            "net": round(sum(r["net"] for r in rows), 2),
        },
        empty="No payslips recorded.",
    )


def tax_deduction_summary(env, date_from=None, date_to=None, **params):
    """Tax deduction summary by period."""
    slips = env["fix.payslip"].sudo().search([])
    groups = {}
    for slip in slips:
        key = slip.period_id.name
        g = groups.setdefault(key, {"employees": set(), "gross": 0.0, "tax": 0.0})
        g["employees"].add(slip.employee_id.id)
        g["gross"] += float(slip.gross or 0.0)
        g["tax"] += float(getattr(slip, "tax_withheld", 0.0) or 0.0)
    rows = [
        {
            "period": k,
            "employees": len(v["employees"]),
            "gross": round(v["gross"], 2),
            "tax": round(v["tax"], 2),
            "effective_rate": round(v["tax"] / v["gross"] * 100.0, 2) if v["gross"] else 0.0,
        }
        for k, v in sorted(groups.items())
    ]
    return _pack(
        "Tax Deduction Summary — AY 2026-27",
        ["period", "employees", "gross", "tax", "effective_rate"],
        {
            "period": "Period",
            "employees": "Employees",
            "gross": "Gross",
            "tax": "Tax Withheld",
            "effective_rate": "Effective Rate %",
        },
        rows,
        [
            "Effective rate = tax withheld over gross for the period; the payslip computes tax "
            "on the annual taxable base with the slab engine."
        ],
        totals={
            "period": "Total",
            "gross": round(sum(r["gross"] for r in rows), 2),
            "tax": round(sum(r["tax"] for r in rows), 2),
        },
        empty="No payslips recorded.",
    )


def pf_gratuity_provisions(env, date_from=None, date_to=None, **params):
    """PF and gratuity provisions from the payslips and the gratuity action."""
    slips = env["fix.payslip"].sudo().search([])
    rows = []
    for slip in slips:
        pf_emp = float(getattr(slip, "pf_employee", 0.0) or 0.0)
        pf_er = float(getattr(slip, "pf_employer", 0.0) or 0.0)
        if not (pf_emp or pf_er):
            continue
        rows.append(
            {
                "period": slip.period_id.name,
                "employee": slip.employee_id.name,
                "pf_employee": round(pf_emp, 2),
                "pf_employer": round(pf_er, 2),
            }
        )
    return _pack(
        "PF & Gratuity Provisions",
        ["period", "employee", "pf_employee", "pf_employer"],
        {
            "period": "Period",
            "employee": "Employee",
            "pf_employee": "PF Employee",
            "pf_employer": "PF Employer",
        },
        rows,
        [
            "Provident-fund contributions per payslip. Gratuity is NOT accrued per payslip: the "
            "Labour Act gratuity is computed at separation by the payslip's separation action, so "
            "it is shown on the Final Settlements screen, not invented here."
        ],
        totals={
            "period": "Total",
            "pf_employee": round(sum(r["pf_employee"] for r in rows), 2),
            "pf_employer": round(sum(r["pf_employer"] for r in rows), 2),
        },
        empty="No PF or gratuity figures on the recorded payslips.",
    )


def payroll_variance(env, date_from=None, date_to=None, **params):
    """Payroll variance: latest two periods compared per employee."""
    periods = env["fix.payroll.period"].sudo().search([], order="period_start desc", limit=2)
    if len(periods) < 2:
        return _pack(
            "Payroll Variance — needs two periods",
            [],
            {},
            [],
            ["Two calculated periods are required for a variance."],
            empty="Fewer than two payroll periods exist.",
        )
    current, previous = periods[0], periods[1]
    cur_slips = {
        s.employee_id.id: s
        for s in env["fix.payslip"].sudo().search([("period_id", "=", current.id)])
    }
    prev_slips = {
        s.employee_id.id: s
        for s in env["fix.payslip"].sudo().search([("period_id", "=", previous.id)])
    }
    rows = []
    for emp_id in sorted(set(cur_slips) | set(prev_slips)):
        cur = cur_slips.get(emp_id)
        prev = prev_slips.get(emp_id)
        name = (cur or prev).employee_id.name
        cur_net = float(cur.net or 0.0) if cur else 0.0
        prev_net = float(prev.net or 0.0) if prev else 0.0
        rows.append(
            {
                "employee": name,
                "previous": round(prev_net, 2),
                "current": round(cur_net, 2),
                "variance": round(cur_net - prev_net, 2),
                "pct": round((cur_net - prev_net) / prev_net * 100.0, 2) if prev_net else 0.0,
            }
        )
    rows.sort(key=lambda r: -abs(r["variance"]))
    return _pack(
        "Payroll Variance — %s vs %s" % (current.name, previous.name),
        ["employee", "previous", "current", "variance", "pct"],
        {
            "employee": "Employee",
            "previous": "Previous Net",
            "current": "Current Net",
            "variance": "Variance",
            "pct": "Variance %",
        },
        rows,
        [
            "Compared on net pay; an employee present in only one period shows the full amount "
            "as variance."
        ],
        totals={
            "employee": "Total",
            "previous": round(sum(r["previous"] for r in rows), 2),
            "current": round(sum(r["current"] for r in rows), 2),
            "variance": round(sum(r["variance"] for r in rows), 2),
        },
        empty="No payslips in the two periods.",
    )


REPORTS = {
    "salary_register": salary_register,
    "payroll_cost_allocation": payroll_cost_allocation,
    "tax_deduction_summary": tax_deduction_summary,
    "pf_gratuity": pf_gratuity_provisions,
    "payroll_variance": payroll_variance,
}


def kpis(env):
    today = datetime.date.today()
    periods = env["fix.payroll.period"].sudo().search([], order="period_start desc", limit=1)
    latest = periods[:1]
    slips = env["fix.payslip"].sudo().search([])
    month_start = today.replace(day=1)
    tax_mtd = sum(
        float(getattr(s, "tax_withheld", 0.0) or 0.0)
        for s in slips
        if s.period_id.period_start and s.period_id.period_start >= month_start
    )
    bonus = env["fix.payroll.bonus.run"].sudo().search([("state", "!=", "paid")])
    corrections = env["fix.payroll.offcycle"].sudo().search([("state", "!=", "paid")])
    return {
        "payroll_cycle": latest.name if latest else "—",
        "gross_payroll": round(
            sum(float(s.gross or 0.0) for s in slips if latest and s.period_id.id == latest.id), 2
        ),
        "run_duration": len(slips.filtered(lambda s, ln=latest: ln and s.period_id.id == ln.id)),
        "corrections": len(corrections),
        "tax_withheld_mtd": round(tax_mtd, 2),
        "festival_bonus_accrued": round(sum(float(b.total_amount or 0.0) for b in bonus), 2),
    }
