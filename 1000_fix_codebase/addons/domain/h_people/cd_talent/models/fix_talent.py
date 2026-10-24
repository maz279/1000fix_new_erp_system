# fix_talent — M58: talent acquisition and onboarding (P09-M08).
from odoo import fields, models

from libs.py.fix_events import publish


class FixJobRequisition(models.Model):
    """M58: talent acquisition. The joiner event drives M29 provisioning."""

    _name = "fix.job.requisition"
    _description = "Job Requisition"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True)
    department_id = fields.Many2one("hr.department", string="Department")
    position_id = fields.Many2one("fix.org.position", string="Position")
    openings = fields.Integer(default=1, required=True)
    state = fields.Selection(
        [("draft", "Draft"), ("open", "Open"), ("hired", "Hired"), ("closed", "Closed")],
        default="draft",
        required=True,
        tracking=True,
    )

    def action_open(self):
        for rec in self:
            rec.state = "open"

    def action_hired(self):
        for rec in self:
            rec.state = "hired"
            publish(
                self.env,
                "employee.hired",
                "fix.job.requisition",
                rec.id,
                {"position": rec.position_id.name or rec.name},
            )


class FixCandidate(models.Model):
    _name = "fix.candidate"
    _description = "Candidate"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True)
    email = fields.Char()
    phone = fields.Char()
    requisition_id = fields.Many2one("fix.job.requisition", string="Requisition")
    state = fields.Selection(
        [
            ("applied", "Applied"),
            ("screening", "Screening"),
            ("interview", "Interview"),
            ("offered", "Offered"),
            ("hired", "Hired"),
            ("rejected", "Rejected"),
        ],
        default="applied",
        required=True,
        tracking=True,
    )

    def action_screen(self):
        for rec in self:
            rec.state = "screening"

    def action_interview(self):
        for rec in self:
            rec.state = "interview"

    def action_offer(self):
        for rec in self:
            rec.state = "offered"

    def action_hire(self):
        for rec in self:
            rec.state = "hired"
            # Create onboarding plan automatically
            plan = self.env["fix.onboarding.plan"].create(
                {
                    "name": f"Onboarding: {rec.name}",
                    "candidate_id": rec.id,
                    "requisition_id": rec.requisition_id.id if rec.requisition_id else False,
                    "position_id": rec.requisition_id.position_id.id
                    if rec.requisition_id
                    else False,
                    "department_id": rec.requisition_id.department_id.id
                    if rec.requisition_id
                    else False,
                    "company_id": rec.company_id.id,
                    "operating_unit_id": rec.operating_unit_id.id
                    if rec.operating_unit_id
                    else False,
                }
            )
            publish(
                self.env,
                "candidate.hired",
                "fix.candidate",
                rec.id,
                {"candidate": rec.name, "onboarding_plan_id": plan.id},
            )


class FixOnboardingPlan(models.Model):
    """M58 / MV-01: Onboarding lifecycle. On completion, emits the authoritative
    'employee.joined' event consumed by M29 provisioning, M61 knowledge, and cd_payroll_bd."""

    _name = "fix.onboarding.plan"
    _description = "Employee Onboarding Plan"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True)
    candidate_id = fields.Many2one("fix.candidate", string="Candidate", required=True)
    requisition_id = fields.Many2one("fix.job.requisition", string="Job Requisition")
    employee_id = fields.Many2one("hr.employee", string="Created Employee Record")
    position_id = fields.Many2one("fix.org.position", string="Position")
    department_id = fields.Many2one("hr.department", string="Department")
    joined_date = fields.Date(string="Joining Date", default=fields.Date.today, required=True)

    # Statutory & Operational Onboarding Checklist
    nid_verified = fields.Boolean(
        string="NID / Identity Verified",
        default=False,
        tracking=True,
        help="Bangladesh NID or Passport verified against election commission/official source",
    )
    contract_signed = fields.Boolean(
        string="Employment Contract Executed",
        default=False,
        tracking=True,
        help="Formal written employment contract executed under BLA 2006 §5",
    )
    it_assets_allocated = fields.Boolean(
        string="IT Equipment & Assets Allocated",
        default=False,
        tracking=True,
        help="Workstation, diagnostic laptop, test benches allocated in M17",
    )
    keycloak_provisioned = fields.Boolean(
        string="Keycloak Identity & Corporate SSO Provisioned",
        default=False,
        tracking=True,
        help="Keycloak realm account, MFA token, and OIDC federation configured",
    )
    bank_details_captured = fields.Boolean(
        string="Payroll & BEFTN Bank Details Captured",
        default=False,
        tracking=True,
        help="Bank routing number, account number registered in M44 payroll engine",
    )
    safety_kit_issued = fields.Boolean(
        string="PPE & Workshop Safety Kit Issued",
        default=False,
        tracking=True,
        help="ESD wristband, anti-static mat, safety goggles, and lab coat issued under M59 HSE",
    )

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("in_progress", "In Progress"),
            ("completed", "Completed"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )

    def action_start(self):
        for rec in self:
            rec.state = "in_progress"

    def action_complete(self):
        for rec in self:
            from odoo.exceptions import UserError

            if not (
                rec.nid_verified
                and rec.contract_signed
                and rec.keycloak_provisioned
                and rec.bank_details_captured
            ):
                raise UserError(
                    "Cannot complete onboarding: statutory prerequisites (NID, Contract, "
                    "Keycloak SSO, Bank details) must be fully verified."
                )
            rec.state = "completed"
            publish(
                self.env,
                "employee.joined",
                "fix.onboarding.plan",
                rec.id,
                {
                    "onboarding_id": rec.id,
                    "candidate_name": rec.candidate_id.name,
                    "position": rec.position_id.name if rec.position_id else "",
                    "department": rec.department_id.name if rec.department_id else "",
                    "joined_date": str(rec.joined_date),
                },
            )
