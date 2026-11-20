# fix.field.order.part: A06 final pass B2 (M15-10): a part fitted on a field job
# leaves the M15 ledger.
#
# Field part lines recorded a product.product and never touched M15, so a van
# kept stock that had gone into a customer's device. Same approach as the
# workshop bridge (cd_workshop/models/fix_workshop_part_line_m15.py): only a
# product mapped to an M15 spare part (fix.spare.part.product_id) is issued,
# through M15's own issue; not enough stock refuses the fit. A product that is
# not an M15 part is unchanged unless cd_field_service.m15_issue_required is on.
#
# A06 ERP audit (20 Nov 2026) A06/A08/X22, owner decision D3: M15 picks the
# store by the job's branch and warranty status (the van named on the job or
# the technician's van when it is a store of that kind, else the branch's one
# store of that kind), takes the job's own reservation first and refuses when
# several stores could be meant. The cost M15 issued at is the line's cost.
from odoo import fields, models
from odoo.exceptions import UserError

M15_REQUIRED_PARAM = "cd_field_service.m15_issue_required"


class FixFieldOrderPartM15(models.Model):
    _inherit = "fix.field.order.part"

    m15_consumption_id = fields.Many2one(
        "fix.stock.consumption",
        string="M15 Issue",
        readonly=True,
        copy=False,
        ondelete="restrict",
        help="The M15 spare-parts issue this fitted part caused.",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"m15_consumption_id"}

    def _a06_m15_part(self):
        self.ensure_one()
        return (
            self.env["fix.spare.part"]
            .sudo()
            .search(
                [
                    ("product_id", "=", self.product_id.id),
                    ("company_id", "in", [self.field_order_id.sudo().company_id.id, False]),
                ],
                limit=1,
            )
        )

    def _a06_m15_store(self, technician, part=None):
        """(store, reservation) the part is issued from (D3, M15 decides)."""
        self.ensure_one()
        order = self.field_order_id.sudo()
        service_order = order.order_id
        part = part or self._a06_m15_part()
        return self.env["fix.stock.location"]._fix_job_store(
            order.company_id,
            service_order.branch_id,
            service_order.order_category == "warranty",
            part,
            self.quantity or 0.0,
            technician=technician,
            job_ref=order.name,
            van=self.sudo().van_location_id or order.van_location_id,
        )

    def _a06_m15_location(self, technician):
        """The store the part is issued from (kept for callers of the A02
        bridge: same name and arguments)."""
        return self._a06_m15_store(technician)[0]

    def _a06_issue_from_m15(self):
        """Issue this line through M15, as the system (the technician's rights on
        the job were already checked), with every M15 issue rule."""
        self.ensure_one()
        Issue = self.env["fix.stock.consumption"].sudo()
        part = self._a06_m15_part()
        if not part:
            raw = self.env["ir.config_parameter"].sudo().get_param(M15_REQUIRED_PARAM, "0")
            if str(raw).strip() in ("1", "true", "True"):
                raise UserError(
                    "%s is not an M15 spare part, and %s is on: map the product to a spare "
                    "part before it is fitted." % (self.product_id.display_name, M15_REQUIRED_PARAM)
                )
            return Issue
        order = self.field_order_id.sudo()
        technician = order.technician_id or self.env.user.employee_id
        if not technician:
            raise UserError(
                "Field order %s has no technician to record the issue of %s against."
                % (order.name, part.part_number)
            )
        location, reservation = self._a06_m15_store(technician, part)
        if not location:
            raise UserError(
                "Field order %s has no van or branch store to issue %s from."
                % (order.name, part.part_number)
            )
        vals = {
            "company_id": order.company_id.id,
            "operating_unit_id": order.operating_unit_id.id,
            "service_order_ref": order.name,
            "product_id": part.id,
            "location_id": location.id,
            "technician_id": technician.id,
            "quantity": self.quantity,
            "serial_number": self.lot_serial_number or False,
            "scanned_code": self.lot_serial_number or part.part_number,
        }
        if reservation:
            vals["reservation_id"] = reservation.id
            if reservation.booked_class not in ("owned", "van"):
                vals["issue_class"] = reservation.booked_class
        issue = Issue.create(vals)
        issue.action_scan_and_consume()
        return issue

    def action_consume(self):
        result = super().action_consume()
        for rec in self.filtered(lambda r: not r.m15_consumption_id):
            issue = rec._a06_issue_from_m15()
            if issue:
                vals = {"m15_consumption_id": issue.id}
                # A06 ERP audit X22: the job carries the cost M15 issued at
                issued_at = issue.sudo().unit_cost
                if abs((issued_at or 0.0) - (rec.unit_cost or 0.0)) > 1e-6:
                    vals["unit_cost"] = issued_at
                rec.sudo()._guarded().write(vals)
        return result
