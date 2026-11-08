# fix.field.order.part: A06 final pass B2 (M15-10): a part fitted on a field job
# leaves the M15 ledger.
#
# Field part lines recorded a product.product and never touched M15, so a van
# kept stock that had gone into a customer's device. Same approach as the
# workshop bridge (cd_workshop/models/fix_workshop_part_line_m15.py): only a
# product mapped to an M15 spare part (fix.spare.part.product_id) is issued,
# through M15's own issue, from the technician's van where there is one, else
# from the job's branch store; not enough stock refuses the fit. A product that
# is not an M15 part is unchanged unless cd_field_service.m15_issue_required is on.
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

    def _a06_m15_location(self, technician):
        """The technician's van where there is one, else the job's branch store."""
        self.ensure_one()
        order = self.field_order_id.sudo()
        Location = self.env["fix.stock.location"].sudo()
        van = self.sudo().van_location_id or order.van_location_id
        if not van and technician:
            van = Location.search(
                [
                    ("technician_id", "=", technician.id),
                    ("location_type", "=", "van"),
                    ("state", "=", "active"),
                ],
                limit=1,
            )
        if van:
            return van
        branch = order.order_id.branch_id
        if not branch:
            return Location
        return Location.search(
            [
                ("branch_id", "=", branch.id),
                ("location_type", "=", "branch"),
                ("state", "=", "active"),
                ("company_id", "=", order.company_id.id),
            ],
            limit=1,
        )

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
        location = self._a06_m15_location(technician)
        if not location:
            raise UserError(
                "Field order %s has no van or branch store to issue %s from."
                % (order.name, part.part_number)
            )
        issue = Issue.create(
            {
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
        )
        issue.action_scan_and_consume()
        return issue

    def action_consume(self):
        result = super().action_consume()
        for rec in self.filtered(lambda r: not r.m15_consumption_id):
            issue = rec._a06_issue_from_m15()
            if issue:
                rec._guarded().write({"m15_consumption_id": issue.id})
        return result
