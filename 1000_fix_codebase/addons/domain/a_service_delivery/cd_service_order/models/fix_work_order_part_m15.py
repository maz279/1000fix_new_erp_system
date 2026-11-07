# fix.work.order.part: A06 final pass B2 (M15-10): a part consumed on a work
# order leaves the M15 ledger.
#
# Work-order parts recorded a product.product and never touched M15. A line here
# is the consumption itself (no draft state), so creating it issues the part.
# Same approach as the workshop bridge (cd_workshop/models/
# fix_workshop_part_line_m15.py): only a product mapped to an M15 spare part is
# issued, through M15's own issue, from the technician's van where there is one,
# else from the job's branch store; not enough stock refuses the line. A product
# that is not an M15 part is unchanged unless cd_service_order.m15_issue_required
# is on.
from odoo import api, fields, models
from odoo.exceptions import UserError

M15_REQUIRED_PARAM = "cd_service_order.m15_issue_required"


class FixWorkOrderPartM15(models.Model):
    _name = "fix.work.order.part"
    _inherit = ["fix.work.order.part", "fix.guarded.mixin"]

    m15_consumption_id = fields.Many2one(
        "fix.stock.consumption",
        string="M15 Issue",
        readonly=True,
        copy=False,
        ondelete="restrict",
        help="The M15 spare-parts issue this part caused.",
    )
    fitted_serial_number = fields.Char(
        string="Fitted Part Serial",
        copy=False,
        help="Serial of the spare part taken from stock. Required for a serialized M15 "
        "part: M15 issues one received serial, once.",
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
                    ("company_id", "in", [self.work_order_id.sudo().company_id.id, False]),
                ],
                limit=1,
            )
        )

    def _a06_m15_location(self, technician):
        """The technician's van where there is one, else the job's branch store."""
        self.ensure_one()
        Location = self.env["fix.stock.location"].sudo()
        if technician:
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
        order = self.work_order_id.sudo().order_id
        if not order.branch_id:
            return Location
        return Location.search(
            [
                ("branch_id", "=", order.branch_id.id),
                ("location_type", "=", "branch"),
                ("state", "=", "active"),
                ("company_id", "=", order.company_id.id),
            ],
            limit=1,
        )

    def _a06_issue_from_m15(self):
        """Issue this line through M15, as the system (the caller already checked
        the work order is the technician's), with every M15 issue rule."""
        self.ensure_one()
        Issue = self.env["fix.stock.consumption"].sudo()
        part = self._a06_m15_part()
        if not part:
            raw = self.env["ir.config_parameter"].sudo().get_param(M15_REQUIRED_PARAM, "0")
            if str(raw).strip() in ("1", "true", "True"):
                raise UserError(
                    "%s is not an M15 spare part, and %s is on: map the product to a spare "
                    "part before it is consumed."
                    % (self.product_id.display_name, M15_REQUIRED_PARAM)
                )
            return Issue
        work_order = self.work_order_id.sudo()
        technician = work_order.technician_id or self.env.user.employee_id
        if not technician:
            raise UserError(
                "Work order %s has no technician to record the issue of %s against."
                % (work_order.name, part.part_number)
            )
        location = self._a06_m15_location(technician)
        if not location:
            raise UserError(
                "Work order %s has no van or branch store to issue %s from."
                % (work_order.name, part.part_number)
            )
        issue = Issue.create(
            {
                "company_id": work_order.order_id.company_id.id,
                "operating_unit_id": work_order.order_id.operating_unit_id.id,
                "service_order_ref": work_order.order_id.name,
                "work_order_ref": work_order.name,
                "product_id": part.id,
                "location_id": location.id,
                "technician_id": technician.id,
                "quantity": self.quantity,
                "serial_number": self.fitted_serial_number or False,
                "scanned_code": self.fitted_serial_number or part.part_number,
            }
        )
        issue.action_scan_and_consume()
        return issue

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        for line in lines:
            issue = line._a06_issue_from_m15()
            if issue:
                line._guarded().sudo().write({"m15_consumption_id": issue.id})
        return lines

    def unlink(self):
        if not self.env.su and self.filtered("m15_consumption_id"):
            raise UserError(
                "This part was issued from M15: return it from the issue instead of deleting "
                "the line."
            )
        return super().unlink()
