# fix.qc.checklist — QC enforcement (P04-M03-T07).
# Owned by M01 in W1-W2 until M23 arrives in W5 (AR-006 section 5.2 stub).
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

_QC_INSPECTOR_GROUP = "cd_service_order.group_so_qc_inspector"
_DONE = ("passed", "failed")


class FixQC(models.Model):
    """A QC checklist for a service order.

    M23 linkage is a GV-005 stub with expiry (P04-M03-T07).
    """

    _name = "fix.qc.checklist"
    _description = "QC Checklist"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]

    def _fix_guarded_fields(self) -> set:
        # A02 audit M01-6: a checklist written state='passed' with zero items
        # opened the Ready gate, and the repairing technician named himself
        # inspector. Only action_complete sets these, as the acting user.
        return super()._fix_guarded_fields() | {
            "state",
            "checked_at",
            "inspector_id",
            "inspected_by",
        }

    # A completed inspection is evidence: its results are frozen.
    _FROZEN_WHEN_DONE = frozenset(
        {
            "order_id",
            "work_order_id",
            "visual_inspection_passed",
            "functional_test_passed",
            "safety_electrical_passed",
            "cleaning_sanitization_passed",
            "test_report_attachment_id",
            "item_ids",
        }
    )

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if self and any(c.state in _DONE for c in self):
            locked |= self._FROZEN_WHEN_DONE
        return locked

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    order_id = fields.Many2one(
        "fix.service.order", string="Service Order", required=True, ondelete="cascade", index=True
    )
    work_order_id = fields.Many2one("fix.work.order", string="Work Order")

    inspector_id = fields.Many2one(
        "hr.employee",
        string="QC Inspector",
        readonly=True,
        copy=False,
        help="BRU-SRM-18: must be a person other than the repairing technician above "
        "BDT 25,000. Stamped from the user who completes the checklist.",
    )
    inspected_by = fields.Many2one("res.users", string="Inspected By", readonly=True, copy=False)
    state = fields.Selection(
        [
            ("pending", "Pending"),
            ("in_progress", "In Progress"),
            ("passed", "Passed"),
            ("failed", "Failed"),
        ],
        default="pending",
        required=True,
        readonly=True,
        copy=False,
        tracking=True,
    )
    checked_at = fields.Datetime(readonly=True, copy=False)
    notes = fields.Text()

    # --- A02 Enterprise Data Capture (M01 QC Checklist Multi-Tab Specification) ---
    visual_inspection_passed = fields.Boolean(
        string="Cosmetic & Housing Assembly Verified",
        default=True,
        tracking=True,
    )
    functional_test_passed = fields.Boolean(
        string="Full Hardware & I/O Functional Test Passed",
        default=True,
        tracking=True,
    )
    safety_electrical_passed = fields.Boolean(
        string="Electrical Grounding & Thermal Safety Passed",
        default=True,
        tracking=True,
    )
    cleaning_sanitization_passed = fields.Boolean(
        string="Ultrasonic / Isopropyl Sanitization Completed",
        default=True,
        tracking=True,
    )
    test_report_attachment_id = fields.Many2one(
        "ir.attachment",
        string="Automated Diagnostic & Burn-In Log (PDF)",
        help="Attached hardware diagnostic report or burn-in telemetry sheet.",
    )

    item_ids = fields.One2many("fix.qc.item", "checklist_id", string="Checklist Items")
    all_passed = fields.Boolean(compute="_compute_all_passed", store=True)

    @api.depends("item_ids.passed")
    def _compute_all_passed(self):
        for rec in self:
            items = rec.item_ids
            rec.all_passed = bool(items) and all(item.passed for item in items)

    def write(self, vals):
        if self and not self._fix_guard_open():
            done = self.filtered(lambda c: c.state in _DONE)
            if done and set(vals) & self._FROZEN_WHEN_DONE:
                raise UserError(
                    "The QC checklist of %s is %s: its inspection record can no longer "
                    "change." % (done[:1].order_id.name, done[:1].state)
                )
        return super().write(vals)

    def _fix_assert_independent(self) -> None:
        """BRU-SRM-18 / SOD-07 (A02 audit M01-6): the inspector is the acting
        user, holds the QC Inspector role, and neither repaired the device
        nor completed the repair."""
        self.ensure_one()
        if self.env.su:
            return
        user = self.env.user
        if not user.has_group(_QC_INSPECTOR_GROUP):
            raise UserError(
                "Only a QC Inspector completes a QC checklist. Ask an appointed inspector."
            )
        order = self.order_id
        technicians = (
            order.technician_id
            | self.work_order_id.technician_id
            | order.work_order_ids.mapped("technician_id")
        )
        employee = user.employee_id
        if (employee and employee in technicians) or user in technicians.mapped("user_id"):
            raise UserError(
                "Segregation of duties: the technician who repaired order %s cannot "
                "inspect it." % order.name
            )
        if order.repair_completed_by and order.repair_completed_by == user:
            raise UserError(
                "Segregation of duties: the person who completed the repair of %s cannot "
                "inspect it." % order.name
            )

    def action_complete(self):
        for rec in self:
            if rec.state in _DONE:
                raise UserError("This QC checklist is already %s." % rec.state)
            if not rec.item_ids:
                raise ValidationError("QC checklist must have at least one item.")
            rec._fix_assert_independent()
            passed = rec.all_passed
            employee = self.env.user.employee_id
            rec._guarded().write(
                {
                    "state": "passed" if passed else "failed",
                    "checked_at": fields.Datetime.now(),
                    "inspected_by": self.env.user.id,
                    "inspector_id": employee.id if employee else rec.inspector_id.id,
                }
            )
            # A failed inspection sends the order back to rework.
            if not passed and rec.order_id.state == "qc_pending":
                rec.order_id.action_qc_fail()

    @api.constrains("inspector_id", "work_order_id")
    def _check_independent_inspector(self):
        """BRU-SRM-18: independent QC by a person other than the repairing technician."""
        for rec in self:
            if (
                rec.work_order_id
                and rec.inspector_id
                and rec.inspector_id == rec.work_order_id.technician_id
            ):
                raise ValidationError(
                    "QC inspector must be a different person from the repairing technician "
                    "(BRU-SRM-18: independent QC is mandatory above BDT 25,000)."
                )


class FixQCItem(models.Model):
    _name = "fix.qc.item"
    _description = "QC Checklist Item"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    checklist_id = fields.Many2one("fix.qc.checklist", required=True, ondelete="cascade")
    name = fields.Char(required=True)
    passed = fields.Boolean(default=False)
    notes = fields.Char()
    sequence = fields.Integer(default=10)

    # A completed inspection's items are its evidence (A02 audit M01-6).
    def _fix_assert_open(self, checklists) -> None:
        done = checklists.filtered(lambda c: c.state in _DONE and not c._fix_guard_open())
        if done:
            raise UserError(
                "The QC checklist is already %s: its items can no longer change." % done[:1].state
            )

    @api.model_create_multi
    def create(self, vals_list):
        ids = [v["checklist_id"] for v in vals_list if v.get("checklist_id")]
        self._fix_assert_open(self.env["fix.qc.checklist"].browse(ids))
        return super().create(vals_list)

    def write(self, vals):
        self._fix_assert_open(self.checklist_id)
        return super().write(vals)

    def unlink(self):
        self._fix_assert_open(self.checklist_id)
        return super().unlink()
