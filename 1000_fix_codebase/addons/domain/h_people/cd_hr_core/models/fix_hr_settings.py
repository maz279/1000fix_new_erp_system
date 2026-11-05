# cd_hr_core — company settings for figures the business must rule (A09 §7).
#
# BUILD_BRIEF §3: where the A09 report or benchmark marks a figure unverified,
# conflicting or "needs counsel", it is a company setting holding the value the
# code used before, never a constant. Each one is listed under "Decisions" in
# the M21 build report.
from odoo import fields, models


class ResCompanyHrSettings(models.Model):
    _inherit = "res.company"

    fix_hr_contract_weekly_hours_cap = fields.Float(
        string="Contract Weekly Hours Cap",
        default=48.0,
        help="DECISION (A09 report §7.4): the code capped contracts at 48 h (BLA s.102 "
        "as cited by the spec) while the attendance code uses 60 h. Counsel to rule.",
    )
    fix_hr_resign_notice_permanent_days = fields.Integer(
        string="Resignation Notice, Permanent Worker (days)",
        default=60,
        help="DECISION: BLA s.27(1), 2013 text (verified): 60 days. The Labour (Amendment) "
        "Act 2026 re-tiers s.27 and was read only in conflicting secondary sources.",
    )
    fix_hr_resign_notice_temporary_days = fields.Integer(
        string="Resignation Notice, Temporary Monthly-Rated Worker (days)",
        default=30,
        help="DECISION: BLA s.27(2), 2013 text: 30 days for a monthly-rated temporary "
        "worker. Confirm against the 2026 gazette.",
    )
    fix_hr_suspension_subsistence_pct = fields.Float(
        string="Suspension Subsistence Allowance (% of wages)",
        default=0.0,
        help="DECISION: BLA s.24 requires a subsistence allowance during suspension; the "
        "rate is not in the A09 benchmark. 0 = not ruled: a suspension cannot start "
        "until labour counsel rules the rate.",
    )
    # BLA s.27(3A) absence without leave (A09 benchmark §2.3 item 7, Verified [45]):
    # more than 10 days absent, a notice giving 10 days to explain or rejoin,
    # then 7 more days for self-defence, then deemed released from the first
    # day of absence. The 2026 amendment was not read in its gazetted text, so
    # the three counts are settings holding the verified 2013 text.
    fix_hr_abandon_absence_days = fields.Integer(
        string="Abandonment: Days Absent Before the Notice (s.27(3A))",
        default=10,
        help="DECISION: BLA s.27(3A) 2013 text (verified): absence of more than 10 days "
        "without leave or information. Confirm against the 2026 gazette.",
    )
    fix_hr_abandon_reply_days = fields.Integer(
        string="Abandonment: Days to Explain or Rejoin (s.27(3A))",
        default=10,
        help="DECISION: BLA s.27(3A) 2013 text (verified): the notice gives 10 days.",
    )
    fix_hr_abandon_hearing_days = fields.Integer(
        string="Abandonment: Further Days for Self-Defence (s.27(3A))",
        default=7,
        help="DECISION: BLA s.27(3A) 2013 text (verified): 7 more days before the worker is "
        "deemed released.",
    )
    # BLA s.19 death in service (benchmark §2.3 item 8): after more than 2 years
    # (2013, verified); the 2026 Act reportedly cuts it to 1 year (Secondary).
    # Payroll (cd_payroll_bd, I1) computes the benefit and reads this setting.
    fix_hr_death_benefit_min_service_years = fields.Float(
        string="Death Benefit: Minimum Continuous Service (years, s.19)",
        default=2.0,
        help="DECISION: BLA s.19 2013 text (verified): more than 2 years of continuous "
        "service. The 2026 amendment reportedly reads 1 year (secondary source only).",
    )
