# fix.work.order.part: A06 final pass B2 (M15-10): a part consumed on a work
# order leaves the M15 ledger.
#
# Work-order parts recorded a product.product and never touched M15. A line here
# is the consumption itself (no draft state), so creating it issues the part.
# Same approach as the workshop bridge (cd_workshop/models/
# fix_workshop_part_line_m15.py): only a product mapped to an M15 spare part is
# issued, through M15's own issue; not enough stock refuses the line. A product
# that is not an M15 part is unchanged unless cd_service_order.m15_issue_required
# is on.
#
# A06 ERP audit (20 Nov 2026) A06/A08/X22, owner decision D3: the store is no
# longer the first branch store found. M15 picks it by the job's branch and
# warranty status (warranty jobs draw only from warranty stores, other jobs
# never do), takes the job's own reservation first, and refuses when several
# stores could be meant. The cost M15 issued the part at is the line's cost.
from odoo import api, fields, models
from odoo.exceptions import UserError

from .fix_service_order import PARTS_ISSUE_STATES

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

    def _a06_m15_store(self, technician, part=None):
        """(store, reservation) the part is issued from (D3, M15 decides)."""
        self.ensure_one()
        order = self.work_order_id.sudo().order_id
        part = part or self._a06_m15_part()
        return self.env["fix.stock.location"]._fix_job_store(
            order.company_id,
            order.branch_id,
            order.order_category == "warranty",
            part,
            self.quantity or 0.0,
            technician=technician,
            job_ref=order.name,
        )

    def _a06_m15_location(self, technician):
        """The store the part is issued from (kept for callers of the A02
        bridge: same name and arguments)."""
        return self._a06_m15_store(technician)[0]

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
        location, reservation = self._a06_m15_store(technician, part)
        if not location:
            raise UserError(
                "Work order %s has no van or branch store to issue %s from."
                % (work_order.name, part.part_number)
            )
        vals = {
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
        if reservation:
            vals["reservation_id"] = reservation.id
            if reservation.booked_class not in ("owned", "van"):
                vals["issue_class"] = reservation.booked_class
        issue = Issue.create(vals)
        issue.action_scan_and_consume()
        return issue

    @api.model_create_multi
    def create(self, vals_list):
        # A02 ERP audit M01-F11: stock is issued only to an order that is
        # approved for repair (or back from a failed QC). Parts were drawn
        # against draft, unapproved and cancelled orders. Trusted service code
        # (data loads) is exempt; the technician API checks the state itself.
        if not self.env.su:
            work_orders = (
                self.env["fix.work.order"]
                .sudo()
                .browse([v["work_order_id"] for v in vals_list if v.get("work_order_id")])
            )
            for wo in work_orders:
                if wo.state == "cancelled" or wo.order_id.state not in PARTS_ISSUE_STATES:
                    raise UserError(
                        "Parts are issued to an approved order in repair. Order %s is %s "
                        "(work order %s is %s)."
                        % (wo.order_id.name, wo.order_id.state, wo.name, wo.state)
                    )
        lines = super().create(vals_list)
        for line in lines:
            issue = line._a06_issue_from_m15()
            if issue:
                vals = {"m15_consumption_id": issue.id}
                # A06 ERP audit X22: the job carries the cost M15 issued at
                issued_at = issue.sudo().unit_cost
                if abs((issued_at or 0.0) - (line.unit_cost or 0.0)) > 1e-6:
                    vals["unit_cost"] = issued_at
                line._guarded().sudo().write(vals)
        return lines

    def unlink(self):
        if not self.env.su and self.filtered("m15_consumption_id"):
            raise UserError(
                "This part was issued from M15: return it from the issue instead of deleting "
                "the line."
            )
        return super().unlink()
