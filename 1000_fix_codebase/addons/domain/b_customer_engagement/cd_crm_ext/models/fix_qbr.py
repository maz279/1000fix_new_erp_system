# fix.qbr + fix.qbr.action — the quarterly business review (M07,
# FR-CRM-033…038). Per spec §16.3 the DATA ASSEMBLY and bilingual PDF
# generation are W4-gated on M05 SLA and M34 satisfaction data: this model
# carries scheduling, meeting records and action tracking now; the pack
# assembly seam is labelled honestly (AUT-CRM-07 partial).
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class FixQbr(models.Model):
    """One scheduled quarterly business review for an account."""

    _name = "fix.qbr"
    _description = "Quarterly Business Review"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "scheduled_for desc, id desc"

    partner_id = fields.Many2one(
        "res.partner", string="Account", required=True, index=True, ondelete="cascade"
    )
    period = fields.Char(string="Period (YYYY-Qn)", required=True)
    scheduled_for = fields.Date(string="Scheduled For", required=True)
    held_on = fields.Date(string="Held On", readonly=True)
    state = fields.Selection(
        [
            ("scheduled", "Scheduled"),
            ("data_ready", "Data Pack Ready"),
            ("held", "Held"),
            ("cancelled", "Cancelled"),
        ],
        string="State",
        default="scheduled",
        required=True,
        tracking=True,
    )
    attendees = fields.Text(string="Attendees")
    decisions = fields.Text(string="Discussion & Decisions")
    document_ref = fields.Char(
        string="Document Reference",
        help="The generated bilingual pack (W4 seam: assembly from M05/M34 data "
        "and PDF generation land with the W4 gate)",
    )
    action_ids = fields.One2many("fix.qbr.action", "qbr_id", string="Agreed Actions")
    open_action_count = fields.Integer(string="Open Actions", compute="_compute_actions")
    company_id = fields.Many2one(
        "res.company", string="Company", required=True, default=lambda self: self.env.company
    )

    @api.depends("action_ids.state")
    def _compute_actions(self):
        for qbr in self:
            qbr.open_action_count = len(qbr.action_ids.filtered(lambda a: a.state == "open"))

    def action_mark_data_ready(self, document_ref=None):
        for qbr in self:
            qbr.write({"state": "data_ready", "document_ref": document_ref or qbr.document_ref})
        return True

    def action_mark_held(self, held_on=None):
        """Record the meeting; open actions carry into tracking (FR-CRM-037).

        FLAW-07.3: Mandates executive attendees, meeting decisions/minutes,
        and attached document or presentation reference.
        """
        for qbr in self:
            if qbr.state == "cancelled":
                raise ValidationError("A cancelled QBR cannot be marked held")
            if not qbr.attendees or not qbr.attendees.strip():
                raise ValidationError(
                    "QBR completion mandatory requirement: Executive attendees list cannot be empty (FLAW-07.3 / REQ-07.4)."
                )
            if not qbr.decisions or not qbr.decisions.strip():
                raise ValidationError(
                    "QBR completion mandatory requirement: Discussion, decisions, and minutes must be recorded (FLAW-07.3 / REQ-07.4)."
                )
            if not qbr.document_ref or not qbr.document_ref.strip():
                raise ValidationError(
                    "QBR completion mandatory requirement: Document reference or presentation pack link must be attached (FLAW-07.3 / REQ-07.4)."
                )
            qbr.write({"state": "held", "held_on": held_on or fields.Date.today()})
            from libs.py.fix_events import publish

            publish(
                self.env,
                "qbr.generated",
                "fix.qbr",
                qbr.id,
                {"partner_id": qbr.partner_id.id, "period": qbr.period},
            )
        return True


class FixQbrAction(models.Model):
    """An action agreed at a review, tracked to completion (FR-CRM-037)."""

    _name = "fix.qbr.action"
    _description = "QBR Action"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "due_date, id"

    qbr_id = fields.Many2one("fix.qbr", string="QBR", required=True, ondelete="cascade", index=True)
    description = fields.Char(string="Action", required=True)
    owner_internal = fields.Many2one("res.users", string="Owner (internal)")
    owner_party = fields.Char(string="Owner (client side)")
    due_date = fields.Date(string="Due Date")
    state = fields.Selection(
        [("open", "Open"), ("done", "Done"), ("cancelled", "Cancelled")],
        string="State",
        default="open",
        required=True,
        tracking=True,
    )
    overdue = fields.Boolean(string="Overdue", compute="_compute_overdue", store=False)
    company_id = fields.Many2one(
        "res.company", string="Company", required=True, default=lambda self: self.env.company
    )

    @api.depends("due_date", "state")
    def _compute_overdue(self):
        today = fields.Date.today()
        for action in self:
            action.overdue = bool(
                action.state == "open" and action.due_date and action.due_date < today
            )

    def action_close(self):
        self.write({"state": "done"})
        return True

    def action_cancel(self):
        self.write({"state": "cancelled"})
        return True
