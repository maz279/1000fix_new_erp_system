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
