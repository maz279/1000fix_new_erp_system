# fix.qc.checklist — QC enforcement (P04-M03-T07).
# Owned by M01 in W1-W2 until M23 arrives in W5 (AR-006 section 5.2 stub).
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class FixQC(models.Model):
    """A QC checklist for a service order.

    M23 linkage is a GV-005 stub with expiry (P04-M03-T07).
    """
    _name = "fix.qc.checklist"
    _description = "QC Checklist"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    order_id = fields.Many2one("fix.service.order", string="Service Order",
                               required=True, ondelete="cascade", index=True)
    work_order_id = fields.Many2one("fix.work.order", string="Work Order")

    inspector_id = fields.Many2one("hr.employee", string="QC Inspector",
                                   help="BRU-SRM-18: must be a person other than the repairing technician above BDT 25,000")
    state = fields.Selection(
        [("pending", "Pending"), ("in_progress", "In Progress"),
         ("passed", "Passed"), ("failed", "Failed")],
        default="pending", required=True, tracking=True)
    checked_at = fields.Datetime(readonly=True)
    notes = fields.Text()

    item_ids = fields.One2many("fix.qc.item", "checklist_id", string="Checklist Items")
    all_passed = fields.Boolean(compute="_compute_all_passed", store=True)

    @api.depends("item_ids.passed")
    def _compute_all_passed(self):
        for rec in self:
            items = rec.item_ids
            rec.all_passed = bool(items) and all(item.passed for item in items)

    def action_complete(self):
        for rec in self:
            if not rec.item_ids:
                raise ValidationError("QC checklist must have at least one item.")
            if not rec.all_passed:
                rec.state = "failed"
            else:
                rec.state = "passed"
            rec.checked_at = fields.Datetime.now()

    @api.constrains("inspector_id", "work_order_id")
    def _check_independent_inspector(self):
        """BRU-SRM-18: independent QC by a person other than the repairing technician."""
        for rec in self:
            if (rec.work_order_id and rec.inspector_id
                    and rec.inspector_id == rec.work_order_id.technician_id):
                raise ValidationError(
                    "QC inspector must be a different person from the repairing technician "
                    "(BRU-SRM-18: independent QC is mandatory above BDT 25,000).")


class FixQCItem(models.Model):
    _name = "fix.qc.item"
    _description = "QC Checklist Item"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    checklist_id = fields.Many2one("fix.qc.checklist", required=True, ondelete="cascade")
    name = fields.Char(required=True)
    passed = fields.Boolean(default=False)
    notes = fields.Char()
    sequence = fields.Integer(default=10)
