# A09 · M56 Payroll & Statutory — surfaces, packs and KPIs over payroll periods,
# payslips, BEFTN batches, salary structures, bonus runs, certificates,
# quarterly withholding returns and off-cycle payments.
#
# A09 workflow audit (2026-11-03), P0 A6: every report and KPI here read
# `sudo().search([])` - a plain employee read colleagues' basic, gross and
# net through the salary register, and an officer of one company read
# another company's payslips. Salary data is now read as the caller, only by
# the payroll groups, and only in the caller's allowed companies.
import datetime

from odoo.exceptions import AccessError

PAYROLL_GROUP = "cd_payroll_bd.group_payroll_officer"  # the manager implies it

# A09 M56 build (C1): approvals are routed M63 requests. The screens offer
# "Request Approval" and "Recall"; the decision itself is taken from the
# approver's inbox (M63), never from a payroll screen. The action sets are
# literals so the FF-48 wiring check can read them.

SURFACES = {
    "fix.payroll.period": {
        "order": "period_start desc, id desc",
        "limit": 100,
        "actions": {
            "action_verify_attendance_locked",
            "action_trial_run",
            "action_calculate",
            "action_prevalidate",
            "action_request_approval",
            "action_recall_approval",
            "action_pay",
            "action_post",
            "action_publish_payslips",
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
        # a submitted file is never regenerated; settlement needs the bank's confirmation
        "actions": {"action_settle"},
    },
    "fix.payroll.structure": {"order": "grade", "limit": 100, "actions": set()},
    "fix.payroll.bonus.line": {"order": "run_id desc, employee_id", "limit": 500, "actions": set()},
    "fix.payroll.bonus.run": {
        "order": "bonus_date desc, id desc",
        "limit": 100,
        "actions": {
            "action_compute",
            "action_request_approval",
            "action_recall_approval",
            "action_pay",
            "action_post",
            "action_cancel",
        },
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
        "actions": {
            "action_request_approval",
            "action_recall_approval",
            "action_pay",
            "action_post",
            "action_cancel",
        },
    },
    "fix.wppf.allocation": {
        "order": "fiscal_year desc, id desc",
        "limit": 100,
        "actions": {
            "action_calculate",
            "action_request_approval",
            "action_recall_approval",
            "action_post",
            "action_pay_bwwf",
        },
    },
    # ---- A09 round 2 ------------------------------------------------------------
    # M56-11: the statutory pack; approved from the inbox by a second Payroll
    # Manager, never from this screen
    "fix.statutory.pack": {
        "order": "effective_from desc, version desc, id desc",
        "limit": 100,
        "actions": {
            "action_request_approval",
            "action_recall_approval",
            "action_cancel",
            "action_new_version",
        },
    },
    # BRU-PAY-06: the variance review lines of a trial or calculated run
    "fix.payroll.variance": {
        "order": "period_id desc, kind, abs_variance_pct desc, id",
        "limit": 500,
        "actions": {"action_acknowledge"},
    },
    # M56-1: bank changes inside the cool-off, confirmed by a second person
    "fix.payroll.bank.check": {
        "order": "period_id desc, id",
        "limit": 300,
        "actions": {"action_confirm"},
    },
    # M56-4: the bank's per-item return and the re-issue of failed items
    "fix.beftn.return": {
        "order": "id desc",
        "limit": 100,
        "actions": {"action_import", "action_reissue"},
    },
    "fix.beftn.return.line": {"order": "return_id desc, id", "limit": 500, "actions": set()},
    # wallet-paid salaries: one disbursement file per MFS provider
    "fix.mfs.disbursement": {"order": "id desc", "limit": 100, "actions": {"action_settle"}},
    # FR-PAY-022: the monthly gratuity provision register (written by its cron)
    "fix.payroll.gratuity.accrual": {
        "order": "month desc, employee_id",
        "limit": 500,
        "actions": set(),
    },
    # BRU-PAY-04: an overpaid salary recovered from the next runs (routed)
    "fix.payroll.recovery": {
        "order": "id desc",
        "limit": 200,
        "actions": {"action_request_approval", "action_recall_approval", "action_cancel"},
    },
    "fix.payroll.recovery.line": {"order": "id desc", "limit": 500, "actions": set()},
    # the provider's per-wallet answer to an MFS file, and its re-issue
    "fix.mfs.return": {
        "order": "id desc",
        "limit": 100,
        "actions": {"action_import", "action_reissue"},
    },
    "fix.mfs.return.line": {"order": "return_id desc, id", "limit": 500, "actions": set()},
    # BLA s.19: a death-in-service nominee's account, verified by a second user
    "fix.payroll.nominee.account": {
        "order": "id desc",
        "limit": 200,
        "actions": {"action_verify", "action_cancel"},
    },
    # M56-13: WPPF beneficiaries (worker classification before trustee approval)
    "fix.wppf.beneficiary": {
        "order": "allocation_id desc, employee_id",
        "limit": 500,
        "actions": set(),
    },
}


def _payroll(env, model, domain=(), **kw):
    """`model` records the caller may see as payroll data: the payroll groups
    only, the caller's allowed companies, the caller's own record rules."""
    if not env.user.has_group(PAYROLL_GROUP):
        raise AccessError("Payroll figures are restricted to Payroll Officers and Managers.")
    return env[model].search([("company_id", "in", env.companies.ids), *domain], **kw)


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
    slips = _payroll(env, "fix.payslip")
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
    slips = _payroll(env, "fix.payslip")
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
    slips = _payroll(env, "fix.payslip")
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
    slips = _payroll(env, "fix.payslip")
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
            "Provident-fund contributions per payslip. Gratuity is provided monthly by the "
            "gratuity provision cron (see the Gratuity Provision report) and paid at separation."
        ],
        totals={
            "period": "Total",
            "pf_employee": round(sum(r["pf_employee"] for r in rows), 2),
            "pf_employer": round(sum(r["pf_employer"] for r in rows), 2),
        },
        empty="No PF or gratuity figures on the recorded payslips.",
    )


def payroll_variance(env, date_from=None, date_to=None, **params):
    """Payroll variance (BRU-PAY-06): the latest run's net per employee
    against the previous PAID period, as computed by its calculation or, before
    that, by its trial run; with the threshold and who acknowledged what."""
    lines = _payroll(env, "fix.payroll.variance", order="period_id desc, id desc", limit=1)
    if not lines:
        return _pack(
            "Payroll Variance — no trial or calculated run yet",
            [],
            {},
            [],
            [
                "Run a trial or calculate a period: the variance is recorded against the "
                "previous paid period."
            ],
            empty="No variance recorded.",
        )
    period = lines.period_id
    kind = (
        "run"
        if _payroll(
            env,
            "fix.payroll.variance",
            [("period_id", "=", period.id), ("kind", "=", "run")],
            limit=1,
        )
        else "trial"
    )
    rows_rec = _payroll(
        env,
        "fix.payroll.variance",
        [("period_id", "=", period.id), ("kind", "=", kind)],
        order="abs_variance_pct desc, id",
    )
    threshold = period.company_id.payroll_variance_threshold_pct or 0.0
    rows = [
        {
            "employee": r.employee_id.name,
            "previous": round(r.previous_net, 2),
            "current": round(r.current_net, 2),
            "variance": round(r.variance, 2),
            "pct": "new" if r.no_comparison else round(r.variance_pct, 2),
            "flag": "over" if r._over(threshold) else "",
            "acknowledged": r.acknowledged_by_id.name or "",
        }
        for r in rows_rec
    ]
    previous = rows_rec[:1].previous_period_id.name or "no paid period"
    return _pack(
        "Payroll Variance — %s (%s) vs %s" % (period.name, kind, previous),
        ["employee", "previous", "current", "variance", "pct", "flag", "acknowledged"],
        {
            "employee": "Employee",
            "previous": "Previous Paid Net",
            "current": "Current Net",
            "variance": "Variance",
            "pct": "Variance %",
            "flag": "Over Threshold",
            "acknowledged": "Acknowledged By",
        },
        rows,
        [
            "Threshold %s: an employee over it blocks the approval until a reviewer who did not "
            "calculate the run acknowledges it." % ("%g%%" % threshold if threshold else "off (0)")
        ],
        totals={
            "employee": "Total",
            "previous": round(sum(r["previous"] for r in rows), 2),
            "current": round(sum(r["current"] for r in rows), 2),
            "variance": round(sum(r["variance"] for r in rows), 2),
        },
        empty="No payslips in the two periods.",
    )


def gratuity_provision(env, date_from=None, date_to=None, **params):
    """FR-PAY-022: the monthly gratuity provision register."""
    recs = _payroll(env, "fix.payroll.gratuity.accrual", order="month desc, employee_id")
    rows = [
        {
            "month": r.month,
            "employee": r.employee_id.name,
            "years": r.completed_years,
            "liability": round(r.liability, 2),
            "accrual": round(r.accrual, 2),
            "posted": r.move_id.name or "",
        }
        for r in recs
    ]
    return _pack(
        "Gratuity Provision — %d rows" % len(rows),
        ["month", "employee", "years", "liability", "accrual", "posted"],
        {
            "month": "Month",
            "employee": "Employee",
            "years": "Completed Years",
            "liability": "Owed at Month End",
            "accrual": "Month's Movement",
            "posted": "GL Entry",
        },
        rows,
        [
            "Computed monthly by the existing separation rule (the statutory pack's bands, as "
            "coded and unsourced until a sourced pack is approved)."
        ],
        totals={
            "month": "Total",
            "accrual": round(sum(r["accrual"] for r in rows), 2),
        },
        empty="No gratuity provision recorded yet.",
    )


def my_payslips(env, date_from=None, date_to=None, **params):
    """Employee self-service (FR-PAY-051): the caller's OWN published
    payslips, and nobody else's. No payroll role needed; no other slip shown."""
    rows = env["fix.payslip"].fix_my_payslips()
    return _pack(
        "My Payslips — %d published" % len(rows),
        ["period", "basic", "gross", "pf", "tax", "net", "published_on"],
        {
            "period": "Period",
            "basic": "Basic",
            "gross": "Gross",
            "pf": "Provident Fund",
            "tax": "Income Tax Withheld",
            "net": "Net Pay",
            "published_on": "Published On",
        },
        rows,
        [
            "Your own payslips, once payroll has paid and published the run. Each carries a "
            "content digest; the Bengali payslip prints from the same figures."
        ],
        empty="No published payslip yet.",
    )


REPORTS = {
    "my_payslips": my_payslips,
    "salary_register": salary_register,
    "payroll_cost_allocation": payroll_cost_allocation,
    "tax_deduction_summary": tax_deduction_summary,
    "pf_gratuity": pf_gratuity_provisions,
    "payroll_variance": payroll_variance,
    "gratuity_provision": gratuity_provision,
}


def kpis(env):
    # an AccessError for a non-payroll caller withholds the M56 figures
    # (a09.kpis), it never computes them
    today = datetime.date.today()
    periods = _payroll(env, "fix.payroll.period", order="period_start desc", limit=1)
    latest = periods[:1]
    slips = _payroll(env, "fix.payslip")
    month_start = today.replace(day=1)
    tax_mtd = sum(
        float(getattr(s, "tax_withheld", 0.0) or 0.0)
        for s in slips
        if s.period_id.period_start and s.period_id.period_start >= month_start
    )
    bonus = _payroll(env, "fix.payroll.bonus.run", [("state", "in", ("computed", "approved"))])
    corrections = _payroll(env, "fix.payroll.offcycle", [("state", "in", ("draft", "approved"))])
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
