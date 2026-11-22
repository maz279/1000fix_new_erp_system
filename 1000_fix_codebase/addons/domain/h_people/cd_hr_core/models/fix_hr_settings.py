# cd_hr_core — company settings for figures the business must rule (A09 §7).
#
# BUILD_BRIEF §3: where the A09 report or benchmark marks a figure unverified,
# conflicting or "needs counsel", it is a company setting holding the value the
# code used before, never a constant. Each one is listed under "Decisions" in
# the M21 build report.
import logging

from odoo import fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


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
    # BLA s.19 death in service (benchmark §2.3 item 8). The Labour (Amendment)
    # Act 2026 (Act No. 43 of 2026; lead-verified, the owner's counsel confirms
    # the gazette text) cuts the qualifying service to 1 year (2013 text: more
    # than 2 years). New companies seed at the 2026 figure; EXISTING companies
    # move only through the approved upgrade
    # (cd_hr_core.apply_labour_act_2026_figures / _apply_labour_act_2026_figures).
    # Payroll (cd_payroll_bd, I1) computes the benefit and reads this setting.
    fix_hr_death_benefit_min_service_years = fields.Float(
        string="Death Benefit: Minimum Continuous Service (years, s.19)",
        default=1.0,
        help="BLA s.19 as amended by the Labour (Amendment) Act 2026: 1 year of "
        "continuous service (2013 text: more than 2 years). Payroll (cd_payroll_bd, "
        "I1) computes the benefit and reads this setting.",
    )

    # ---- the Labour (Amendment) Act 2026 figures on EXISTING data (M21-F5 /
    # M55-F2, M21-F6) -----------------------------------------------
    def _apply_labour_act_2026_figures(self):
        """Move EXISTING statutory rows to the Labour (Amendment) Act 2026
        figures — maternity 120 days (s.46, 60 before + 60 after), festival
        holidays 13 (s.118(1)), death-benefit qualifying service 1 year (s.19),
        and casual/sick leave charging the holidays inside them (BLR 2015
        r.106) — ONLY where a row still holds the untouched pre-Act value
        (112 / 11 / 2.0 / True); a value the owner changed is never
        overwritten. Idempotent. Sets the approval parameter as its last step
        so the statutory floors and the maternity split switch together with
        the data. Returns counts only.

        The lead runs this once on production after the owner approves; the
        19.0.0.7.0 post-migrate runs it only when
        cd_hr_core.apply_labour_act_2026_figures == 'approved'."""
        if not (self.env.su or self.env.user.has_group("cd_hr_core.group_hr_officer")):
            raise UserError(
                "Applying the Labour (Amendment) Act 2026 figures needs the HR "
                "Officer role (or the upgrade migration)."
            )
        companies = self.sudo() or self.env["res.company"].sudo().search([])
        result = {
            "companies": len(companies),
            "maternity_types": 0,
            "festival_types": 0,
            "casual_sick_types": 0,
            "death_benefit_companies": 0,
        }
        Type = self.env["fix.leave.type"].sudo()
        # s.46: maternity 112 -> 120 (only the untouched pre-Act value moves)
        maternity = Type.search(
            [
                ("entitlement_days", "=", 112),
                "|",
                ("code", "=", "maternity"),
                ("maternity", "=", True),
            ]
        )
        for t in maternity:
            t.write({"entitlement_days": 120})
            _logger.info(
                "Labour (Amendment) Act 2026: maternity type %s (%s) 112 -> 120 days",
                t.name,
                t.company_id.name,
            )
        result["maternity_types"] = len(maternity)
        # s.118(1): festival holidays 11 -> 13
        festival = Type.search([("code", "=", "festival"), ("entitlement_days", "=", 11)])
        for t in festival:
            t.write({"entitlement_days": 13})
            _logger.info(
                "Labour (Amendment) Act 2026: festival type %s (%s) 11 -> 13 days",
                t.name,
                t.company_id.name,
            )
        result["festival_types"] = len(festival)
        # BLR 2015 r.106: a holiday inside casual or sick leave is charged
        charged = Type.search(
            [("code", "in", ("casual", "sick")), ("excludes_holidays", "=", True)]
        )
        for t in charged:
            t.write({"excludes_holidays": False})
            _logger.info(
                "Labour Rules 2015 r.106: %s type %s (%s) now charges the holidays "
                "inside the leave",
                t.code,
                t.name,
                t.company_id.name,
            )
        result["casual_sick_types"] = len(charged)
        # s.19: death-benefit qualifying service 2 -> 1 year
        for comp in companies:
            if abs((comp.fix_hr_death_benefit_min_service_years or 0.0) - 2.0) < 1e-9:
                comp.write({"fix_hr_death_benefit_min_service_years": 1.0})
                _logger.info(
                    "Labour (Amendment) Act 2026: company %s death-benefit minimum "
                    "service 2 -> 1 year",
                    comp.name,
                )
                result["death_benefit_companies"] += 1
        # last step: the floors and the maternity 60/60 split switch with the data
        self.env["ir.config_parameter"].sudo().set_param(
            "cd_hr_core.apply_labour_act_2026_figures", "approved"
        )
        return result
