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

from odoo import fields, models
from odoo.exceptions import UserError

from libs.py.payroll_engine import (
    completed_years,
    gratuity,
    resignation_compensation,
)

TWO = Decimal("0.01")

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


def statutory_basis(company) -> str:
    """The rules this company pays by today, pinned on every slip and settlement."""
    tax = company.payroll_tax_table_rule or "unset"
    sep = company.payroll_separation_rule or "unset"
    floor = company.payroll_minimum_basic_monthly or 0.0
    return "tax=%s; separation=%s; min_basic=%s; ot_divisor=%s" % (
        tax,
        sep,
        ("%.2f" % floor) if floor else "unruled",
        "%g" % (company.ot_divisor_hours or 0.0),
    )


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


def separation_figures(
    basic_monthly, joining, separation, exit_type, notice_served_days=0, unused_leave_days=0.0
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
