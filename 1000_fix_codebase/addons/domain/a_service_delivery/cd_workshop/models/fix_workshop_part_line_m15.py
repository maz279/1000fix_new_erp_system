# fix.workshop.part.line — A06 M15-10: a fitted spare part leaves the M15 ledger.
#
# A06 workflow audit (2026-11-03) M15-10: the workshop's part lines never
# called M15, so a part fitted on the bench left no trace in the spare-parts
# ledger while M15 issues carried a free-text job reference. The A02 build
# (CD-M31-02) validates an Odoo stock.move where a workshop names an Odoo
# stock location; the company's spare parts, though, live in M15's own ledger
# (fix.stock.onhand). So when the line's product is an M15 spare part
# (fix.spare.part.product_id) and no Odoo move carried it, consuming the line
# issues it from the workshop's M15 store through M15's own issue
# (fix.stock.consumption.action_scan_and_consume): average cost, location
# bucket, serial control and the job link all apply, and the line keeps the
# issue it caused. A product that is not an M15 part is unchanged unless
# cd_workshop.m15_issue_required is on.
from odoo import fields, models
from odoo.exceptions import UserError

M15_REQUIRED_PARAM = "cd_workshop.m15_issue_required"


class FixWorkshopM15Store(models.Model):
    _inherit = "fix.workshop"

    m15_location_id = fields.Many2one(
        "fix.stock.location",
        string="M15 Parts Store",
        domain="[('location_type', 'in', ('branch', 'central'))]",
        help="The M15 spare-parts location this workshop's bench issues from. Empty: "
        "the active branch store of the workshop's branch hub.",
    )

    def _a06_m15_store(self):
        self.ensure_one()
        if self.m15_location_id:
            return self.m15_location_id
        if not self.branch_id:
            return self.env["fix.stock.location"]
        return (
            self.env["fix.stock.location"]
            .sudo()
            .search(
                [
                    ("branch_id", "=", self.branch_id.id),
                    ("location_type", "=", "branch"),
                    ("state", "=", "active"),
                    ("company_id", "=", self.company_id.id),
                ],
                limit=1,
            )
        )


class FixWorkshopPartLineM15(models.Model):
    _inherit = "fix.workshop.part.line"

    m15_consumption_id = fields.Many2one(
        "fix.stock.consumption",
        string="M15 Issue",
        readonly=True,
        copy=False,
        ondelete="restrict",
        help="The M15 spare-parts issue this fitted part caused.",
    )
    # lot_serial_number records the REPLACED component (parts genealogy); a
    # serialized M15 part is issued by the serial of the unit fitted.
    fitted_serial_number = fields.Char(
        string="Fitted Part Serial",
        copy=False,
        help="Serial of the spare part taken from stock and fitted. Required for a "
        "serialized M15 part: M15 issues one received serial, once.",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"m15_consumption_id"}

    def _a06_m15_part(self):
        self.ensure_one()
        if not self.product_id:
            return self.env["fix.spare.part"]
        job = self.job_id.sudo()
        return (
            self.env["fix.spare.part"]
            .sudo()
            .search(
                [
                    ("product_id", "=", self.product_id.id),
                    ("company_id", "in", [job.company_id.id, False]),
                ],
                limit=1,
            )
        )

    def _a06_m15_required(self) -> bool:
        raw = self.env["ir.config_parameter"].sudo().get_param(M15_REQUIRED_PARAM, "0")
        return str(raw).strip() in ("1", "true", "True")

    def _a06_issue_from_m15(self):
        """Issue this line from the workshop's M15 store, as the system (the
        technician holds no stock rights), with every M15 issue rule."""
        self.ensure_one()
        job = self.job_id.sudo()
        part = self._a06_m15_part()
        if not part:
            if self._a06_m15_required():
                raise UserError(
                    "%s is not an M15 spare part, and %s is on: map the product to a spare "
                    "part before it is fitted." % (self.product_id.display_name, M15_REQUIRED_PARAM)
                )
            return self.env["fix.stock.consumption"]
        store = job.workshop_id._a06_m15_store() if job.workshop_id else False
        if not store:
            raise UserError(
                "Workshop %s has no M15 parts store: set one on the workshop (or give its "
                "branch hub an active branch store) before %s is fitted."
                % (job.workshop_id.name or "-", part.part_number)
            )
        if part.is_serialized and abs((self.quantity or 0.0) - 1.0) > 1e-9:
            raise UserError(
                "%s is serialized: fit it one unit per part line, each with the serial of "
                "the unit fitted (M15 issues one received serial once)." % part.part_number
            )
        technician = job.technician_id or self.env.user.employee_id
        if not technician:
            raise UserError(
                "Job %s has no technician to record the issue of %s against."
                % (job.name, part.part_number)
            )
        issue = (
            self.env["fix.stock.consumption"]
            .sudo()
            .create(
                {
                    "company_id": job.company_id.id,
                    "service_order_ref": job.name,
                    "product_id": part.id,
                    "location_id": store.id,
                    "technician_id": technician.id,
                    "quantity": self.quantity,
                    "serial_number": self.fitted_serial_number or False,
                    "scanned_code": self.fitted_serial_number or part.part_number,
                }
            )
        )
        issue.action_scan_and_consume()
        return issue

    def action_return_to_m15(self, reason=None, notes=""):
        """An unused or DOA part comes off the bench: M15 takes it back at the
        cost it was issued at (a DOA part goes to quarantine), and the line
        stops counting towards the job's parts cost. Only while the job is in
        repair, and only for a part this line issued from M15."""
        for rec in self:
            issue = rec.m15_consumption_id.sudo()
            if not issue or issue.state != "consumed":
                raise UserError("Part line %s carries no M15 issue to return." % rec.display_name)
            job = rec.job_id.sudo()
            if job.state != "in_repair":
                raise UserError(
                    "A part comes off the bench only while job %s is in repair (it is %s)."
                    % (job.name, job.state)
                )
            issue.action_return_part(reason=reason, notes=notes or "")
            rec._guarded().write({"reservation_state": "released"})
        return True

    def action_consume_part(self):
        result = super().action_consume_part()
        for rec in self.filtered(lambda r: not r.stock_move_id and not r.m15_consumption_id):
            issue = rec._a06_issue_from_m15()
            if issue:
                rec._guarded().write(
                    {"m15_consumption_id": issue.id, "consumption_ref": issue.name}
                )
        return result
