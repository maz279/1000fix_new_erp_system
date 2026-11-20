# cd_supplier_risk — M42 supplier risk assessment (FR-SRM2-033,
# CD-M42-04).
#
# Six dimensions (financial, operational, geographic, compliance,
# counterfeit, continuity) roll up to an overall tier; an approved
# assessment moves the profile's risk tier, and a critical single-source
# dependency needs a named qualified alternate or an accepted exception.
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish  # FF-28

from odoo.addons.cd_vendor_ext.models.fix_supplier_profile import check_sod

RATING = [("1", "1 - Low"), ("2", "2 - Moderate"), ("3", "3 - Elevated"),
          ("4", "4 - High"), ("5", "5 - Critical")]

# Next assessment is due sooner the riskier the supplier.
REASSESS_DAYS = {"low": 730, "medium": 365, "high": 180, "critical": 90}

DIMENSIONS = ("financial", "operational", "geographic", "compliance",
              "counterfeit", "continuity")


def overall_tier(ratings):
    """Worst-dimension-dominant roll-up: any 5 is critical; any 4 or a mean
    of 3+ is high; a mean of 2+ is medium; otherwise low."""
    values = [int(r) for r in ratings if r]
    if not values:
        return "low"
    worst, mean = max(values), sum(values) / len(values)
    if worst >= 5:
        return "critical"
    if worst >= 4 or mean >= 3:
        return "high"
    if mean >= 2:
        return "medium"
    return "low"


class FixSupplierRisk(models.Model):
    _name = "fix.supplier.risk"
    _description = "Supplier Risk Assessment"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "assessed_at desc, id desc"
    _p03_capture = {
        "module": "M42",
        "form": "Risk Assessment",
        "fields": ["profile_id", "assessed_at", "financial", "operational",
                   "geographic", "compliance", "counterfeit", "continuity",
                   "single_source_critical", "alternate_profile_id",
                   "exception_note", "mitigations"],
    }

    company_id = fields.Many2one("res.company", string="Company", required=True,
                                 index=True, default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one(
        "operating.unit", string="Operating Unit", index=True,
        default=lambda self: self.env.user._get_default_operating_unit())
    profile_id = fields.Many2one("fix.supplier.profile", string="Supplier",
                                 required=True, index=True, ondelete="cascade")
    assessed_at = fields.Date(string="Assessed On", required=True,
                              default=fields.Date.today)
    financial = fields.Selection(RATING, string="Financial Risk", required=True)
    operational = fields.Selection(RATING, string="Operational Risk", required=True)
    geographic = fields.Selection(RATING, string="Geographic Risk", required=True)
    compliance = fields.Selection(RATING, string="Compliance Risk", required=True)
    counterfeit = fields.Selection(RATING, string="Counterfeit Risk", required=True)
    continuity = fields.Selection(RATING, string="Continuity Risk", required=True)
    overall_tier = fields.Selection(
        [("low", "Low"), ("medium", "Medium"), ("high", "High"),
         ("critical", "Critical")],
        string="Overall Tier", compute="_compute_overall", store=True)
    next_assessment_due = fields.Date(string="Next Assessment Due",
                                      compute="_compute_overall", store=True)
    single_source_critical = fields.Boolean(
        string="Sole Source for Critical Parts",
        help="FR-SRM2-033: a single-source dependency for critical parts needs a "
             "named qualified alternate or an accepted, approved exception")
    alternate_profile_id = fields.Many2one("fix.supplier.profile",
                                           string="Qualified Alternate Supplier")
    exception_note = fields.Text(string="Single-Source Exception")
    mitigations = fields.Text(string="Mitigations")
    assessor_id = fields.Many2one("res.users", string="Assessor",
                                  default=lambda self: self.env.user, readonly=True)
    approved_by = fields.Many2one("res.users", string="Approved By", readonly=True)
    state = fields.Selection(
        [("draft", "Draft"), ("submitted", "Submitted"), ("approved", "Approved"),
         ("rejected", "Rejected")],
        string="Status", default="draft", required=True, tracking=True)

    @api.depends(*DIMENSIONS, "assessed_at")
    def _compute_overall(self):
        for risk in self:
            tier = overall_tier([risk[d] for d in DIMENSIONS])
            risk.overall_tier = tier
            risk.next_assessment_due = (
                risk.assessed_at + timedelta(days=REASSESS_DAYS[tier])
                if risk.assessed_at else False)

    @api.constrains("single_source_critical", "alternate_profile_id",
                    "exception_note", "profile_id")
    def _check_single_source(self):
        for risk in self:
            if risk.alternate_profile_id and risk.alternate_profile_id == risk.profile_id:
                raise ValidationError("A supplier cannot be its own alternate")
            if risk.single_source_critical and not (
                    risk.alternate_profile_id or (risk.exception_note or "").strip()):
                raise ValidationError(
                    "A single-source critical dependency needs a named alternate "
                    "supplier or a documented exception (FR-SRM2-033)")

    def action_submit(self):
        self.filtered(lambda r: r.state == "draft").write({"state": "submitted"})

    def action_approve(self):
        for risk in self:
            if risk.state != "submitted":
                raise UserError("Only a submitted assessment can be approved")
            check_sod(risk, "assessor_id", self.env.user,
                      "The assessor cannot approve their own risk assessment")
            risk.profile_id.risk_tier = risk.overall_tier
            risk.write({"state": "approved", "approved_by": self.env.user.id})
            publish(self.env, "supplier.risk_assessed", "fix.supplier.risk", risk.id, {
                "profile_id": risk.profile_id.id, "overall_tier": risk.overall_tier,
                "single_source_critical": risk.single_source_critical})

    def action_reject(self):
        self.filtered(lambda r: r.state == "submitted").write({"state": "rejected"})
