# cd_supplier_scorecard — M42 performance review cycle and corrective
# action requests (FR-SRM2-030/031, CD-M42-03).
#
# The scorecard itself is COMPUTED from M16/M41 facts (T-04/T-05) by
# fix.supplier.scorecard (cd_cx_feedback, the asymmetric pair-10 consumer);
# no one types a score in. What people capture here is the review meeting
# and the corrective action.
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish  # FF-28

from odoo.addons.cd_vendor_ext.models.fix_supplier_profile import (
    G_QUALITY, check_sod, require_group)

# FR-SRM2-030: strategic quarterly, preferred half-yearly, approved annually.
REVIEW_CADENCE_DAYS = {"strategic": 91, "preferred": 182, "approved": 365,
                       "transactional": 365, "restricted": 91}


class FixSupplierReview(models.Model):
    """FR-SRM2-030: a scheduled performance review with minuted outcomes."""

    _name = "fix.supplier.review"
    _description = "Supplier Performance Review"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "scheduled_for desc, id desc"
    _p03_capture = {
        "module": "M42",
        "form": "Performance Review",
        "fields": ["profile_id", "period", "scheduled_for", "held_on", "scorecard_id",
                   "attendees", "agenda", "minutes", "outcomes"],
    }

    company_id = fields.Many2one("res.company", string="Company", required=True,
                                 index=True, default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one(
        "operating.unit", string="Operating Unit", index=True,
        default=lambda self: self.env.user._get_default_operating_unit())
    profile_id = fields.Many2one("fix.supplier.profile", string="Supplier",
                                 required=True, index=True, ondelete="cascade")
    period = fields.Char(string="Review Period", required=True,
                         help="e.g. 2026-Q3 or 2026-H2")
    scheduled_for = fields.Date(string="Scheduled For", required=True)
    held_on = fields.Date(string="Held On")
    scorecard_id = fields.Many2one("fix.supplier.scorecard", string="Scorecard")
    attendees = fields.Text(string="Attendees")
    agenda = fields.Text(string="Agenda")
    minutes = fields.Text(string="Minutes")
    outcomes = fields.Text(string="Outcomes & Actions")
    next_review_due = fields.Date(string="Next Review Due",
                                  compute="_compute_next_review_due", store=True)
    state = fields.Selection(
        [("scheduled", "Scheduled"), ("held", "Held"), ("cancelled", "Cancelled")],
        string="Status", default="scheduled", required=True, tracking=True)

    @api.depends("scheduled_for", "held_on", "profile_id.segment")
    def _compute_next_review_due(self):
        for review in self:
            anchor = review.held_on or review.scheduled_for
            days = REVIEW_CADENCE_DAYS.get(review.profile_id.segment, 365)
            review.next_review_due = anchor + timedelta(days=days) if anchor else False

    @api.constrains("scorecard_id", "profile_id")
    def _check_scorecard_supplier(self):
        for review in self:
            if (review.scorecard_id
                    and review.scorecard_id.vendor_id != review.profile_id.partner_id):
                raise ValidationError("The scorecard belongs to a different supplier")

    def action_mark_held(self):
        for review in self:
            if review.state != "scheduled":
                raise UserError("Only a scheduled review can be marked held")
            if not (review.minutes or "").strip():
                raise UserError("Minute the review before marking it held")
        self.write({"state": "held"})
        for review in self:
            if not review.held_on:
                review.held_on = fields.Date.today()

    def action_cancel(self):
        self.filtered(lambda r: r.state == "scheduled").write({"state": "cancelled"})


class FixSupplierCar(models.Model):
    """FR-SRM2-031: a corrective action request tracked to verified closure;
    the raiser cannot verify it (§13 SoD); overdue CARs escalate."""

    _name = "fix.supplier.car"
    _description = "Supplier Corrective Action Request"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "due_date, id"
    _p03_capture = {
        "module": "M42",
        "form": "CAR",
        "fields": ["profile_id", "source", "issue", "required_action",
                   "owner_user_id", "due_date", "ncr_ref"],
    }

    company_id = fields.Many2one("res.company", string="Company", required=True,
                                 index=True, default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one(
        "operating.unit", string="Operating Unit", index=True,
        default=lambda self: self.env.user._get_default_operating_unit())
    name = fields.Char(string="CAR Reference", readonly=True, copy=False, index=True)
    profile_id = fields.Many2one("fix.supplier.profile", string="Supplier",
                                 required=True, index=True, ondelete="restrict")
    source = fields.Selection(
        [("scorecard", "Scorecard"), ("inspection", "Inspection"),
         ("delivery", "Delivery"), ("audit", "Audit")],
        string="Source", required=True)
    issue = fields.Text(string="Issue", required=True)
    required_action = fields.Text(string="Required Action", required=True)
    owner_user_id = fields.Many2one("res.users", string="Owner", required=True,
                                    default=lambda self: self.env.user)
    due_date = fields.Date(string="Due Date", required=True, index=True)
    ncr_ref = fields.Char(string="M23 NCR Reference",
                          help="M42 -> M23 stub: the supplier non-conformance "
                               "reference until M23 NCR lands (IR-002 P08-M06-T05)")
    supplier_response = fields.Text(string="Supplier Response")
    root_cause = fields.Text(string="Root Cause")
    verified_by = fields.Many2one("res.users", string="Verified By", readonly=True)
    verified_at = fields.Datetime(string="Verified At", readonly=True)
    effectiveness = fields.Selection(
        [("effective", "Effective"), ("partial", "Partially Effective"),
         ("not_effective", "Not Effective")], string="Effectiveness")
    escalation_level = fields.Integer(string="Escalation Level", default=0,
                                      readonly=True)
    state = fields.Selection(
        [("open", "Open"), ("responded", "Supplier Responded"),
         ("action_taken", "Action Taken"), ("verified", "Verified Closed"),
         ("escalated", "Escalated")],
        string="Status", default="open", required=True, tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("name"):
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "fix.supplier.car") or "CAR/NEW"
        cars = super().create(vals_list)
        for car in cars:
            publish(self.env, "supplier.car_raised", "fix.supplier.car", car.id, {
                "profile_id": car.profile_id.id, "source": car.source,
                "due_date": str(car.due_date)})
        return cars

    @api.constrains("due_date")
    def _check_due(self):
        for car in self:
            if car.due_date and car.create_date and car.due_date < car.create_date.date():
                raise ValidationError("A CAR cannot be due before it is raised")

    def action_record_response(self):
        for car in self:
            if car.state not in ("open", "escalated"):
                raise UserError("A response is recorded on an open CAR")
            if not (car.supplier_response or "").strip():
                raise UserError("Enter the supplier response first")
        self.write({"state": "responded"})

    def action_mark_action_taken(self):
        for car in self:
            if car.state != "responded":
                raise UserError("Record the supplier response first")
            if not (car.root_cause or "").strip():
                raise UserError("A root cause is required before closure")
        self.write({"state": "action_taken"})

    def action_verify_effective(self):
        """§13: CAR verification is a Quality Manager right (R32)."""
        require_group(self.env, G_QUALITY,
                      "Only the Quality Manager can verify a corrective action")
        for car in self:
            if car.state != "action_taken":
                raise UserError("Only a CAR with action taken can be verified")
            check_sod(car, "create_uid", self.env.user,
                      "The user who raised a CAR cannot verify its closure")
            if not car.effectiveness:
                raise UserError("Record the effectiveness of the action")
        self.write({"state": "verified", "verified_by": self.env.user.id,
                    "verified_at": fields.Datetime.now()})

    @api.model
    def _cron_escalate_overdue(self):
        """Escalate overdue CARs (FR-SRM2-031); the second escalation tier
        belongs to the Supply Chain Director (§13)."""
        overdue = self.search([("state", "in", ("open", "responded")),
                               ("due_date", "<", fields.Date.today())])
        for car in overdue:
            car.write({"state": "escalated",
                       "escalation_level": car.escalation_level + 1})
        return len(overdue)
