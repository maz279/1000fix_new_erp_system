# fix_payroll_statutory — M56: the statutory figures payroll computes, and the
# company settings that hold the figures nobody has ruled on yet.
#
# A09 workflow audit (2026-11-03), M56-11 / P2 pay / report §7.3-7.4:
#   * the separation bands, the tax tables and the minimum tax are constants
#     in libs/py/payroll_engine that no repository source confirms. They stay
#     what they are today, but each company now records WHICH rule it pays by
#     (a decision flag), and every payslip and settlement pins that basis, so
#     a later ruling is a visible change, never a silent one;
#   * the minimum-wage floor depends on the wage-board sector (§7.4): it is a
#     company setting, 0 until someone rules the sector;
#   * what plain statute does say is computed here and cited: retrenchment
#     notice of one month or wages in lieu (BLA 2006 s.20(1)(a)), service
#     compensation of 30 days' wages per completed year or gratuity, whichever
#     is higher (s.20(2)(c)/s.26(4)/s.27(4)), and the festival bonus capped at
#     one month's basic, at most two a year, after a year's service (Labour
#     Rules 2015 r.111(5)).
#
# Pure functions (no ORM) come first so the settlement, the payslip and the
# bonus run share one implementation.
import hashlib
import json
import re
from datetime import date
from decimal import ROUND_HALF_UP, Decimal

from dateutil.relativedelta import relativedelta
from odoo import fields, models
from odoo.exceptions import UserError

from libs.py.payroll_engine import (
    TAX_FREE_THRESHOLDS,
    TAX_SLABS,
    completed_years,
    gratuity,
    resignation_compensation,
)

TWO = Decimal("0.01")

# A09 round 2 decision settings. Each default is what the code does today.
TDS_METHODS = [
    ("monthly_annualised", "This month x 12 (today's method)"),
    ("ytd", "Year-to-date over the Bangladesh fiscal year (July - June)"),
]
BONUS_TDS_RULES = [
    ("none", "No withholding on a festival bonus (today)"),
    ("marginal", "Withhold at the employee's payslip marginal rate"),
]

# BLA 2006 s.20(1)(a): one month's written notice, or wages in lieu.
RETRENCHMENT_NOTICE_DAYS = 30
# BLA 2006 s.26(1)(a): 120 days' notice for a monthly-rated permanent worker
# terminated otherwise than for misconduct (the figure the engine already uses).
TERMINATION_NOTICE_DAYS = 120
# s.20(2)(c) / s.26(4): 30 days' wages per completed year of service.
SERVICE_COMPENSATION_DAYS = 30
# Labour Rules 2015 r.111(5): a festival bonus is at most one month's basic,
# a worker receives at most two in a year, after one year of continuous service.
FESTIVAL_BONUS_CAP_MONTHS = Decimal("1")
FESTIVAL_BONUSES_PER_YEAR = 2
FESTIVAL_BONUS_SERVICE_YEARS = 1

# Decision flags (report §7.3 tax adviser, §7.4 labour counsel). Each has only
# the value the code uses today; a ruling adds its option and the code for it.
TAX_TABLE_RULES = [
    (
        "engine_fy2026_27",
        "Engine table FY 2026-27 (375k/400k/475k/500k; 10-30% slabs; minimum tax "
        "5,000/4,000/3,000) - NOT confirmed by a tax adviser",
    ),
]
SEPARATION_RULES = [
    (
        "engine_2026_amendment",
        "Engine bands citing a Labour (Amendment) Act 2026 (gratuity from 5 years, 45 days "
        "above 12; resignation 7/15/30 days) - NOT verified by labour counsel",
    ),
]


def q2(value) -> Decimal:
    return Decimal(str(value)).quantize(TWO, rounding=ROUND_HALF_UP)


def digest_rows(rows) -> str:
    """SHA-256 over a sorted list of tuples: the pin of what was approved."""
    return hashlib.sha256(json.dumps(sorted(rows), default=str).encode()).hexdigest()


def statutory_basis(company, pack=None) -> str:
    """The rules this company pays by, pinned on every slip and settlement.

    With a statutory pack (fix.statutory.pack, M56-11) the pack's version and
    figures are the basis; without one, the company's decision flags."""
    floor = company.payroll_minimum_basic_monthly or 0.0
    if pack:
        return "pack=v%d (%s); tax=%s; separation=%s; min_basic=%s; ot_divisor=%s; ceiling=%s" % (
            pack.version,
            "as coded, unsourced" if pack.basis == "as_coded" else "sourced",
            pack.tax_table_rule,
            pack.separation_rule,
            ("%.2f" % floor) if floor else "unruled",
            "%g" % pack.ot_divisor_hours,
            "%g" % pack.exemption_ceiling,
        )
    tax = company.payroll_tax_table_rule or "unset"
    sep = company.payroll_separation_rule or "unset"
    return "tax=%s; separation=%s; min_basic=%s; ot_divisor=%s" % (
        tax,
        sep,
        ("%.2f" % floor) if floor else "unruled",
        "%g" % (company.ot_divisor_hours or 0.0),
    )


def fiscal_year_of(day):
    """(start, end) of the Bangladesh fiscal year (1 July - 30 June) holding `day`."""
    start_year = day.year if day.month >= 7 else day.year - 1
    return date(start_year, 7, 1), date(start_year + 1, 6, 30)


def fiscal_months_remaining(day) -> int:
    """Months from `day`'s month to June, both included (July -> 12, June -> 1)."""
    return (6 - day.month) % 12 + 1


def marginal_rate(annual_taxable, category="general", disabled_dependents=0) -> Decimal:
    """The slab rate the last taka of `annual_taxable` is taxed at under the
    engine's table (0 below the tax-free threshold). Read from the engine's
    own constants: no rate is typed here."""
    taxable = Decimal(str(annual_taxable or 0))
    threshold = TAX_FREE_THRESHOLDS.get(category or "general", TAX_FREE_THRESHOLDS["general"])
    threshold += Decimal("50000") * Decimal(str(disabled_dependents or 0))
    remaining = taxable - threshold
    if remaining <= 0:
        return Decimal("0")
    for width, rate in TAX_SLABS:
        if width is None or remaining <= width:
            return rate
        remaining -= width
    return TAX_SLABS[-1][1]


def fiscal_year_bounds(label):
    """Bangladesh fiscal year 1 July - 30 June from '2025-26' or '2025-2026'."""
    match = re.fullmatch(r"\s*(\d{4})\s*[-/]\s*(\d{2}|\d{4})\s*", label or "")
    if not match:
        raise UserError(
            "Fiscal year %r is not a Bangladesh fiscal year such as 2025-26 (1 July to 30 June)."
            % label
        )
    start = int(match.group(1))
    end = match.group(2)
    end_year = int(end) if len(end) == 4 else (start // 100) * 100 + int(end)
    if end_year != start + 1:
        raise UserError(
            "Fiscal year %r must run from one July to the next June (e.g. 2025-26)." % label
        )
    return date(start, 7, 1), date(end_year, 6, 30)


# BLA 2006 s.19 (death in service): 30 days' wages per completed year of
# service or any part of a year above six months; 45 days where the worker
# died at work or from a work accident; or the gratuity, if higher. The
# minimum continuous service is a company setting held by cd_hr_core
# (res.company.fix_hr_death_benefit_min_service_years), read, never typed here.
DEATH_DAYS_PER_YEAR = 30
DEATH_AT_WORK_DAYS_PER_YEAR = 45
DEATH_PART_YEAR_MONTHS = 6


def death_rules(exit_rec):
    """(minimum continuous service in years, died at work) for a death exit.

    Both come from M21 (cd_hr_core round 2): the company setting and the
    exit's flag. Without them installed there is no death rule to apply, and
    a death settlement is refused rather than computed on a typed figure."""
    company = exit_rec.company_id or exit_rec.employee_id.company_id
    if "fix_hr_death_benefit_min_service_years" not in company._fields:
        raise UserError(
            "The BLA s.19 death-in-service rule (cd_hr_core) is not installed: no death "
            "benefit is computed."
        )
    at_work = bool(exit_rec["death_at_work"]) if "death_at_work" in exit_rec._fields else False
    return float(company.fix_hr_death_benefit_min_service_years or 0.0), at_work


def death_service_years(joining, separation):
    """s.19: completed years, plus one for a part year above six months."""
    span = relativedelta(separation, joining)
    extra = 1 if (span.months, span.days) > (DEATH_PART_YEAR_MONTHS, 0) else 0
    return span.years + extra


def separation_figures(
    basic_monthly,
    joining,
    separation,
    exit_type,
    notice_served_days=0,
    unused_leave_days=0.0,
    death_min_service_years=None,
    death_at_work=False,
):
    """The final-settlement lines for one separation, as [(key, label, amount)].

    `exit_type` is the fix.hr.exit exit type. The compensation the engine
    computes from the uncited 2026 bands (gratuity, resignation) is used as it
    is today and flagged; the statute this module can cite is applied here."""
    basic = Decimal(str(basic_monthly or 0.0))
    if basic <= 0:
        raise UserError("A separation is computed from a positive contract basic.")
    if separation < joining:
        raise UserError(
            "The separation date %s is before the joining date %s." % (separation, joining)
        )
    years = completed_years(joining, separation)
    daily = basic / Decimal(30)
    served = max(int(notice_served_days or 0), 0)
    grat = gratuity(basic, joining, separation)
    lines = []

    def higher_of_service_or_gratuity(service, label):
        # s.20(2)(c), s.26(4), s.27(4): "... or gratuity, if any, whichever is higher"
        if grat > service:
            lines.append(("gratuity", "Gratuity (higher than %s)" % label, q2(grat)))
        else:
            lines.append(("service_compensation", label, q2(service)))

    if exit_type == "retrenchment":
        notice = daily * max(RETRENCHMENT_NOTICE_DAYS - served, 0)
        if notice:
            lines.append(
                ("notice_pay", "Notice pay in lieu (BLA s.20(1)(a), one month)", q2(notice))
            )
        higher_of_service_or_gratuity(
            daily * SERVICE_COMPENSATION_DAYS * years,
            "Retrenchment compensation, 30 days per completed year (BLA s.20(2)(c))",
        )
    elif exit_type == "termination":
        notice = daily * max(TERMINATION_NOTICE_DAYS - served, 0)
        if notice:
            lines.append(("notice_pay", "Notice pay in lieu (BLA s.26, 120 days)", q2(notice)))
        higher_of_service_or_gratuity(
            daily * SERVICE_COMPENSATION_DAYS * years,
            "Termination compensation, 30 days per completed year (BLA s.26(4))",
        )
    elif exit_type == "resignation":
        higher_of_service_or_gratuity(
            resignation_compensation(basic, joining, separation),
            "Resignation compensation (BLA s.27, engine bands)",
        )
    elif exit_type in ("retirement", "contract_end"):
        if grat:
            lines.append(("gratuity", "Gratuity (engine bands)", q2(grat)))
    elif exit_type == "death":
        if death_min_service_years is None:
            raise UserError("A death-in-service settlement needs the s.19 minimum service.")
        span = relativedelta(separation, joining)
        service = span.years + span.months / 12.0 + span.days / 365.0
        if service > float(death_min_service_years):
            days = DEATH_AT_WORK_DAYS_PER_YEAR if death_at_work else DEATH_DAYS_PER_YEAR
            higher_of_service_or_gratuity(
                daily * days * death_service_years(joining, separation),
                "Death benefit, %d days per year of service%s (BLA s.19)"
                % (days, " - death at work" if death_at_work else ""),
            )
        elif grat:
            # under the minimum service s.19 pays nothing; the gratuity, if any, stays due
            lines.append(("gratuity", "Gratuity (engine bands)", q2(grat)))
    elif exit_type == "abandonment":
        # s.27(3A) abandonment: whether any compensation is due is a labour-counsel
        # question (A09 report §7.4); nothing is computed beyond the earned leave.
        pass
    else:
        raise UserError("No settlement rule is defined for exit type %r." % exit_type)

    unused = Decimal(str(unused_leave_days or 0.0))
    if unused > 0:
        lines.append(
            (
                "leave_encashment",
                "Unused earned leave, %s day(s) at basic / 30 (BLA s.11)" % unused.normalize(),
                q2(daily * unused),
            )
        )
    return years, lines


def notice_served_days(notice_date, last_working_day) -> int:
    if not notice_date or not last_working_day:
        return 0
    return max((fields.Date.to_date(last_working_day) - fields.Date.to_date(notice_date)).days, 0)


class ResCompanyPayrollStatutory(models.Model):
    """The payroll figures awaiting a business ruling (A09 report §7.3/§7.4)."""

    _inherit = "res.company"

    payroll_tax_table_rule = fields.Selection(
        TAX_TABLE_RULES,
        string="Salary Tax Table (decision)",
        default="engine_fy2026_27",
        help="Which salary tax table payroll withholds by. The only option is the engine's "
        "built-in FY 2026-27 table, which no repository source confirms and which contradicts "
        "the hr.employee category labels. A tax adviser's ruling adds the confirmed table "
        "(A09 report §7.3).",
    )
    payroll_separation_rule = fields.Selection(
        SEPARATION_RULES,
        string="Gratuity & Resignation Bands (decision)",
        default="engine_2026_amendment",
        help="Which gratuity and resignation bands a final settlement uses. The only option is "
        "the engine's, citing a 2026 amendment no repository source holds. Labour counsel's "
        "ruling adds the confirmed bands (A09 report §7.4).",
    )
    payroll_minimum_basic_monthly = fields.Float(
        string="Minimum Monthly Basic (wage-board floor)",
        default=0.0,
        help="The minimum-wage floor payroll pre-validation enforces. 0 means no sector has "
        "been ruled yet (A09 report §7.4): only a zero or negative basic is then refused.",
    )
    payroll_return_due_day = fields.Integer(
        string="Withholding Return Due Day",
        default=25,
        help="Day of the month after the return period's end by which the salary withholding "
        "return is due (spec BRU-PAY-16). The s.177 frequency itself awaits a tax ruling.",
    )
    payroll_beftn_account_no = fields.Char(
        string="Off-Cycle / Bonus Originating Account",
        help="The company's originating bank account for off-cycle and festival-bonus BEFTN files.",
    )
    payroll_beftn_routing_no = fields.Char(
        string="Off-Cycle / Bonus Originating Routing No",
        help="9-digit BEFTN routing code of the originating account above.",
    )
    payroll_wppf_expense_account_id = fields.Many2one(
        "account.account", string="WPPF Expense Account"
    )
    payroll_wppf_payable_account_id = fields.Many2one(
        "account.account", string="WPPF Payable Account"
    )
    # ---- A09 round 2 (M56-11/14, M56-1, FR-PAY-004/022, M56-13) ----------------
    # Each is a business decision; each default keeps today's behaviour.
    payroll_tds_method = fields.Selection(
        TDS_METHODS,
        string="Salary TDS Method (decision)",
        default="monthly_annualised",
        required=True,
        help="How the monthly withholding is projected. Today: this month's income x 12. "
        "Year-to-date projects the fiscal year's income from the committed payslips so far "
        "plus this month for the months left, and spreads the balance (ITA 2023 s.86, "
        "FR-PAY-004/015). Which one the business uses is a tax adviser's call.",
    )
    payroll_bonus_tds = fields.Selection(
        BONUS_TDS_RULES,
        string="Festival Bonus TDS (decision)",
        default="none",
        required=True,
        help="Today a festival bonus is paid with no withholding. 'Marginal' withholds at the "
        "slab rate of the employee's latest committed payslip.",
    )
    payroll_variance_threshold_pct = fields.Float(
        string="Payroll Variance Threshold (%)",
        default=0.0,
        help="BRU-PAY-06: approval is refused while an employee's net pay moved by more than "
        "this percentage against the previous paid period and no reviewer acknowledged it. "
        "0 = off (today). The threshold itself is a business decision.",
    )
    payroll_bank_cooloff_days = fields.Integer(
        string="Bank-Change Cool-Off (days)",
        default=0,
        help="M56-1: a salary account or wallet changed within this many days before the run "
        "is refused at pre-validation until a second person confirms it. 0 = off (today).",
    )
    payroll_wppf_min_service_months = fields.Integer(
        string="WPPF Minimum Service (months)",
        default=0,
        help="BLA Ch. XV beneficiary service requirement. 0 = every active employee counts, "
        "as the allocation does today; the figure (6 or 9 months are both cited) is labour "
        "counsel's call.",
    )
    payroll_wppf_bank_account_id = fields.Many2one(
        "account.account",
        string="WPPF / BWWF Paying Bank Account",
        help="The bank account the BWWF deposit is paid from (credited when the BWWF payment "
        "is recorded).",
    )
    payroll_recovery_monthly_cap = fields.Float(
        string="Overpayment Recovery: Monthly Cap (BDT)",
        default=0.0,
        help="The most an approved overpayment recovery deducts from one month's run. 0 = the "
        "whole remaining balance in the next run (capped only by that run's net). No statutory "
        "cap is assumed; BRU-PAY-12's aggregate deduction cap is a business / counsel ruling.",
    )
    payroll_recovery_source = fields.Selection(
        [
            ("payroll", "The monthly payroll run only (today)"),
            ("any_payment", "Any payroll payment (run, off-cycle, festival bonus)"),
        ],
        string="Overpayment Recovery: Taken From",
        default="payroll",
        required=True,
        help="Where an approved overpayment recovery may be deducted. Injury compensation, "
        "final settlements and death-in-service nominee payments are never reduced.",
    )
    payroll_recovery_account_id = fields.Many2one(
        "account.account",
        string="Overpayment Recovery Account",
        help="Credited with what a run recovers (the employee receivable or the expense the "
        "overpayment was booked to - finance's choice).",
    )
    payroll_gratuity_expense_account_id = fields.Many2one(
        "account.account", string="Gratuity Expense Account"
    )
    payroll_gratuity_provision_account_id = fields.Many2one(
        "account.account", string="Gratuity Provision Account"
    )
