# fix.mdm.change.request — the master-data change-request model (P03-M07-T01).
# MV-04: MDM governance moved to W1 because it governs the W1 kernels.
# A change request is the auditable path for master-data modifications that
# require governance review (not every write — only governed changes).
import logging

from odoo import api, fields, models
from odoo.exceptions import ValidationError

logger = logging.getLogger(__name__)

CHANGE_REQUEST_STATES = [
    ("draft", "Draft"),
    ("submitted", "Submitted"),
    ("under_review", "Under Review"),
    ("approved", "Approved"),
    ("rejected", "Rejected"),
    ("implemented", "Implemented"),
    ("cancelled", "Cancelled"),
]


class FixMdmChangeRequest(models.Model):
    """A master-data change request.

    Governed changes (identity documents, critical classifications, brand
    authorisations) go through this model before being applied to the master.
    This is M64-core's primary governance mechanism.
    """

    _name = "fix.mdm.change.request"
    _description = "MDM Change Request"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit")

    reference = fields.Char(
        string="Reference",
        readonly=True,
        default=lambda self: self.env["ir.sequence"].next_by_code("fix.mdm.change.request")
        or "NEW",
    )
    title = fields.Char(required=True, tracking=True)
    description = fields.Text()
    state = fields.Selection(
        CHANGE_REQUEST_STATES, default="draft", required=True, tracking=True, index=True
    )

    # The governed master record
    model_name = fields.Char(
        string="Target Model",
        required=True,
        help="Odoo model name, e.g. 'res.partner' or 'fix.catalogue.item'",
    )
    record_id = fields.Integer(
        string="Target Record ID",
        required=True,
        help="The database ID of the record this change request governs",
    )

    # The proposed change (JSON diff)
    proposed_changes = fields.Text(
        string="Proposed Changes (JSON)", help="A JSON object of {field: new_value} pairs"
    )
    current_values = fields.Text(
        string="Current Values (JSON)",
        readonly=True,
        help="Snapshot of current values at submission time",
    )

    # Review
    submitted_by = fields.Many2one("res.users", readonly=True, tracking=True)
    reviewed_by = fields.Many2one("res.users", readonly=True, tracking=True)
    reviewed_at = fields.Datetime(readonly=True)
    review_notes = fields.Text()
    priority = fields.Selection(
        [("low", "Low"), ("normal", "Normal"), ("high", "High"), ("urgent", "Urgent")],
        default="normal",
        required=True,
        tracking=True,
    )

    # Events (AS-08)
    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            self._emit("mdm.change_requested", rec)
        return records

    def write(self, vals):
        result = super().write(vals)
        if "state" in vals:
            for rec in self:
                event = (
                    "mdm.change_approved"
                    if rec.state == "approved"
                    else "mdm.change_rejected"
                    if rec.state == "rejected"
                    else None
                )
                if event:
                    self._emit(event, rec)
        return result

    def action_submit(self):
        for rec in self:
            if rec.state != "draft":
                raise ValidationError("Only draft requests can be submitted.")
            rec.write(
                {
                    "state": "submitted",
                    "submitted_by": self.env.uid,
                    "current_values": rec._snapshot_current(),
                }
            )

    def action_approve(self):
        for rec in self:
            if rec.state not in ("submitted", "under_review"):
                raise ValidationError("Only submitted requests can be approved.")
            rec.write(
                {
                    "state": "approved",
                    "reviewed_by": self.env.uid,
                    "reviewed_at": fields.Datetime.now(),
                }
            )

    def action_reject(self):
        for rec in self:
            rec.write(
                {
                    "state": "rejected",
                    "reviewed_by": self.env.uid,
                    "reviewed_at": fields.Datetime.now(),
                }
            )

    def _snapshot_current(self) -> str:
        """Snapshot the current values of the governed record."""
        import json

        try:
            model = self.env[self.model_name].browse(self.record_id)
            if model.exists() and self.proposed_changes:
                fields_to_capture = list(json.loads(self.proposed_changes).keys())
                return json.dumps(model.read(fields_to_capture)[0], default=str)
        except Exception:
            logger.warning(
                "MDM snapshot of %s/%s failed", self.model_name, self.record_id, exc_info=True
            )
        return "{}"

    def _emit(self, event_type: str, rec) -> None:
        from libs.py.fix_events import publish

        publish(
            self.env,
            event_type,
            "fix.mdm.change.request",
            rec.id,
            {
                "reference": rec.reference,
                "model_name": rec.model_name,
                "record_id": rec.record_id,
                "state": rec.state,
            },
        )
