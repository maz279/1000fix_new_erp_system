# cd_hr_core — the A09 approval spine (A09 workflow audit B3, B4, B5, C1).
#
# The audit found no A09 document routed for approval: leave, attendance,
# transfer, exit, requisition, offer, JSA, certification, incentive, bonus,
# WPPF and off-cycle were approved by whoever pressed the button, usually the
# person who raised them, and a state write skipped even that. This mixin puts
# every A09 approval on the M63 engine (fix.approvable.mixin) with the rules an
# HR system needs on top of it:
#
#   * routed only: the record's approve method runs from an inbox task, never
#     directly (`_approval_routed`);
#   * self, initiator and SUBJECT exclusion: the requester, the creator, the
#     preparer and the employee the record is about never decide it. When
#     everyone is excluded the request is refused, never skipped;
#   * line manager first (`_approval_manager_first`): leave and attendance go
#     to the subject's manager, then to the role group when there is none;
#   * a DOFA tier only once the business has ruled one: until a
#     fix.dofa.ladder is in force for the model, the role approver decides.
#     The amounts that need a director are a policy decision (A09 report §7.2),
#     not something to type into code.
from odoo import fields, models
from odoo.exceptions import UserError

# Decision domains for the M63 rule book (fix.approval.matrix). A row with one
# of these keys sets the SLA, voting policy, escalation and approver group for
# that kind of HR decision without a code change.
PEOPLE_DECISION_DOMAINS = [
    ("hr_master_change", "HR: Sensitive Master-Data Change"),
    ("hr_contract", "HR: Employment Contract"),
    ("hr_movement", "HR: Transfer / Promotion"),
    ("hr_exit", "HR: Exit and Final Settlement"),
    ("hr_disciplinary", "HR: Disciplinary Action"),
    ("hr_leave", "HR: Leave"),
    ("hr_attendance", "HR: Attendance Exception / Overtime"),
    ("hr_payroll_release", "HR: Payroll Release"),
    ("hr_offcycle", "HR: Off-Cycle Payment"),
    ("hr_bonus", "HR: Festival Bonus Run"),
    ("hr_wppf", "HR: WPPF Allocation"),
    ("hr_incentive", "HR: Incentive Run / Recognition"),
    ("hr_review", "HR: Performance Review Calibration"),
    ("hr_requisition", "HR: Job Requisition"),
    ("hr_offer", "HR: Job Offer"),
    ("hr_background_check", "HR: Background Check Clearance"),
    ("hr_certification", "HR: Certification Grant / Waiver"),
    ("hr_hse", "HR: HSE Approval (JSA, Incident Closure)"),
]


class FixApprovalMatrixPeople(models.Model):
    _inherit = "fix.approval.matrix"

    decision_domain = fields.Selection(
        selection_add=PEOPLE_DECISION_DOMAINS,
        ondelete={key: "cascade" for key, _label in PEOPLE_DECISION_DOMAINS},
    )


class FixPeopleApprovalMixin(models.AbstractModel):
    """An A09 record whose approval is a routed M63 request."""

    _name = "fix.people.approval.mixin"
    _inherit = ["fix.approvable.mixin"]
    _description = "People & Workforce Routed Approval"

    _approval_routed = True
    # True: the subject employee's line manager decides first.
    _approval_manager_first = False

    # ---- who the record is about and who prepared it ------------------------
    def _approval_subject_employees(self):
        """The employee(s) the record is about. Override when the field differs."""
        if "employee_id" in self._fields:
            return self.mapped("employee_id")
        return self.env["hr.employee"]

    def _approval_preparers(self):
        """Users who prepared or computed the record (never its approver)."""
        return self.env["res.users"]

    def _approval_excluded(self):
        excluded = super()._approval_excluded()
        subjects = self._approval_subject_employees().sudo().mapped("user_id")
        return (excluded | subjects | self._approval_preparers()).sudo()

    # ---- the DOFA tier, once ruled ------------------------------------------
    def _approval_tier(self):
        """The tier a RULED ladder gives this amount; False until one is in force."""
        self.ensure_one()
        if "fix.dofa.ladder" not in self.env:
            return False
        company = self.company_id if "company_id" in self._fields else self.env.company
        ruled = self.env["fix.dofa.ladder"].thresholds_for(self._name, company=company)
        if not ruled:
            return False
        amount = abs(self._approval_amount() or 0.0)
        tier = ruled[-1][1]
        for bound, band_tier in ruled:
            if amount <= bound:
                tier = band_tier
                break
        return False if tier == "tier_0" else tier

    # ---- line manager first -------------------------------------------------
    def _approval_line_managers(self):
        managers = self._approval_subject_employees().sudo().mapped("parent_id.user_id")
        return managers.filtered(lambda u: u.active and not u.share)

    def _approval_resolve(self, rule, tier):
        if self._approval_manager_first and not tier and not rule.approver_group_id:
            managers = self._approval_line_managers() - self._approval_excluded()
            if managers:
                return self._approval_substitutes(managers)
        return super()._approval_resolve(rule, tier)

    # ---- helpers for the record's own approve method --------------------------
    def _people_decider(self):
        """The user whose authority decides (the absent approver for a delegate)."""
        return self._approval_authority_user()

    def _people_conflicted_users(self):
        """Who may never decide this record, judged at DECISION time.

        `_approval_excluded()` includes env.user because it runs when the
        request is raised; inside the approve method env.user is the approver,
        so the requester is taken from the request instead."""
        self.ensure_one()
        req = self.approval_request_id.sudo()
        subjects = self._approval_subject_employees().sudo().mapped("user_id")
        return (
            self.create_uid | req.requested_by_id | subjects | self._approval_preparers()
        ).sudo()

    def _people_assert_not_conflicted(self):
        """Belt and braces inside the approve method: the requester, creator,
        preparer and subject never decide, even if a task reached them."""
        for rec in self:
            if rec.env.su and not rec._approval_task():
                continue
            if rec._approval_acting_users() & rec._people_conflicted_users():
                raise UserError(
                    "You cannot decide %s: you requested, prepared or are the subject of it."
                    % rec.display_name
                )
