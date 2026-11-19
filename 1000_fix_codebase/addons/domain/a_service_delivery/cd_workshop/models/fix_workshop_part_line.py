# fix.workshop.part.line — Consumed Spare Part Line (CD-M31-01 / M15 Integration).
#
# A02 workflow audit (2026-11-03), M31-4: reservation_state defaulted to
# "reserved" with no reservation made, a technician consumed BDT 75,000 of
# parts on a job nobody had approved, then rewrote the line and deleted it, and
# a delivered job's part cost went from 500 to 90,000. The line is now guarded:
# its reservation and consumption fields move only through the actions below,
# consumption needs a job in repair and stays within the approved estimate, and
# a consumed line (or any line of a closed job) is frozen and undeletable.
# M15 stock moves are still not posted (the consumption reference is a stub).
import logging

from odoo import api, fields, models
from odoo.exceptions import UserError

logger = logging.getLogger(__name__)

# A02 ERP audit M31-F13: unit_cost was typed by the bench, and every
# ceiling check reads the subtotal it drives. It is the part's standard cost
# when the line is added and the M15 issue cost when the part is fitted.
GUARDED_LINE_FIELDS = frozenset(
    {"reservation_state", "consumption_ref", "consumed_at", "consumed_by_id", "unit_cost"}
)
# what a consumed line, or any line of a closed job, records: frozen
LINE_FROZEN_FIELDS = frozenset(
    {
        "job_id",
        "product_id",
        "quantity",
        "unit_cost",
        "currency_id",
        "lot_serial_number",
        "source_origin",
        "donor_board_serial",
        "circuit_designator",
    }
)
CLOSED_JOB_STATES = ("delivered", "unrepairable", "cancelled")


class FixWorkshopPartLine(models.Model):
    """A spare part consumed during execution of a workshop repair job.

    Integrates with M15 cd_inventory for barcode scanning, stock decrements,
    and suspense valuation postings.
    """

    _name = "fix.workshop.part.line"
    _description = "Workshop Consumed Part Line"
    # fix.dofa.mixin brings fix.guarded.mixin and the M63 routed approval
    # used for a part beyond the approved estimate (A02 audit B1; the rules
    # are in fix_workshop_part_line_p1p2.py)
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.dofa.mixin"]
    _order = "job_id, id"

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | GUARDED_LINE_FIELDS

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if len(self) == 1 and self._m31_line_frozen():
            locked |= LINE_FROZEN_FIELDS
        return locked

    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        index=True,
        default=lambda self: self.env.company,
    )
    operating_unit_id = fields.Many2one(
        "operating.unit",
        string="Operating Unit",
        index=True,
    )
    job_id = fields.Many2one(
        "fix.workshop.job",
        string="Workshop Job",
        required=True,
        ondelete="cascade",
        index=True,
    )

    product_id = fields.Many2one(
        "product.product",
        string="Spare Part",
        required=True,
        index=True,
    )
    part_number = fields.Char(
        string="SKU / Part Number",
        related="product_id.default_code",
        store=True,
    )
    # Not stored: a stored related of the translatable product name is computed in
    # one language only (Odoo warns); nothing needs a frozen snapshot of the name.
    part_name = fields.Char(
        string="Part Description",
        related="product_id.name",
    )
    quantity = fields.Float(
        string="Quantity",
        default=1.0,
        required=True,
    )

    # AS-10: Monetary total with currency
    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        required=True,
        default=lambda self: self.env.ref("base.BDT", raise_if_not_found=False)
        or self.env.company.currency_id,
    )
    unit_cost = fields.Monetary(
        string="Unit Cost",
        currency_field="currency_id",
    )
    subtotal = fields.Monetary(
        string="Subtotal",
        compute="_compute_subtotal",
        store=True,
        currency_field="currency_id",
    )

    lot_serial_number = fields.Char(
        string="Serial / Lot Number",
        help="Serial number of the replaced component for parts genealogy tracking",
    )
    consumption_ref = fields.Char(
        string="Stock Consumption Ref",
        readonly=True,
        copy=False,
        help="Linked M15 consumption transaction reference",
    )
    source_origin = fields.Selection(
        [
            ("central_warehouse", "Central Warehouse (M15)"),
            ("branch_store", "Branch / Depot Local Store"),
            ("donor_board_harvest", "Donor Board IC Harvest"),
            ("oem_consignment", "OEM Warranty Consignment Stock"),
        ],
        string="Part Source Origin",
        default="central_warehouse",
        required=True,
    )
    donor_board_serial = fields.Char(
        string="Donor Board S/N",
        help="Required when harvesting an IC/component from a donor board",
    )
    circuit_designator = fields.Char(
        string="Board Schematic Designator",
        help="e.g. U3100, Q7030, J5800",
    )
    reservation_state = fields.Selection(
        [
            ("draft", "Draft"),
            ("reserved", "Reserved in M15"),
            ("consumed", "Consumed on Bench"),
            ("released", "Reservation Released"),
        ],
        string="M15 Reservation Status",
        # A02 audit M31-4: was "reserved" with no reservation ever made
        default="draft",
        required=True,
        readonly=True,
        tracking=True,
    )
    consumed_at = fields.Datetime(string="Consumed At", readonly=True, copy=False)
    consumed_by_id = fields.Many2one("res.users", string="Consumed By", readonly=True, copy=False)
    part_photo_attachment_id = fields.Many2one(
        "ir.attachment",
        string="Old vs New Part Verification Photo",
    )
    notes = fields.Char(string="Fitment Notes")

    @api.depends("quantity", "unit_cost")
    def _compute_subtotal(self):
        for rec in self:
            rec.subtotal = (rec.quantity or 0.0) * (rec.unit_cost or 0.0)

    @api.onchange("product_id")
    def _onchange_product_id(self):
        if self.product_id:
            self.unit_cost = self.product_id.standard_price

    def _m31_line_frozen(self) -> bool:
        self.ensure_one()
        return self.reservation_state == "consumed" or (
            self.job_id.sudo().state in CLOSED_JOB_STATES
        )

    @api.model_create_multi
    def create(self, vals_list):
        # A02 audit M31-4 / P31-10: a part added to a closed job changed its cost
        if not self._fix_guard_open():
            jobs = (
                self.env["fix.workshop.job"]
                .sudo()
                .browse([v["job_id"] for v in vals_list if v.get("job_id")])
            )
            closed = jobs.filtered(lambda j: j.state in CLOSED_JOB_STATES)
            if closed:
                raise UserError(
                    "Parts cannot be added to job %s: it is closed (%s)."
                    % (closed[0].name, closed[0].state)
                )
        # The part's standard cost when none is given. The backend form's
        # onchange did this; a line added from the workspace (M31 Part
        # Fitment, 2026-11-12) runs no onchange and cost 0, so the job's
        # parts total and the estimate check missed the part entirely.
        # A02 ERP audit M31-F13: and the cost is the system's, never typed:
        # a caller may only echo the standard cost (the backend onchange).
        Product = self.env["product.product"].sudo()
        trusted = self._fix_guard_open()
        costs = []
        for vals in vals_list:
            standard = (
                Product.browse(vals["product_id"]).standard_price if vals.get("product_id") else 0.0
            )
            given = vals.pop("unit_cost", None)
            if given is not None and not trusted and abs((given or 0.0) - standard) > 1e-6:
                self._fix_guard_refuse({"unit_cost"})
            costs.append(given if (trusted and given is not None) else standard)
        records = super().create(vals_list)
        for rec, cost in zip(records, costs, strict=True):
            rec._guarded().write({"unit_cost": cost})
        return records

    def write(self, vals):
        touched = LINE_FROZEN_FIELDS & set(vals)
        if self and touched and not self._fix_guard_open():
            for rec in self:
                if not rec._m31_line_frozen():
                    continue
                changed = sorted(n for n in touched if rec._fix_guard_differs(n, vals[n], rec[n]))
                if changed:
                    raise UserError(
                        "%s cannot be changed on a %s part line: the consumed quantity and "
                        "cost are the record of what went into the device."
                        % (
                            ", ".join(rec._fields[n].string or n for n in changed),
                            "consumed" if rec.reservation_state == "consumed" else "closed job's",
                        )
                    )
        result = super().write(vals)
        # A02 ERP audit M31-F13: a part changed on an open line takes the new
        # part's standard cost (the cost is not typed)
        if "product_id" in vals and not self._fix_guard_open():
            for rec in self.filtered(lambda r: r.reservation_state in ("draft", "reserved")):
                rec._guarded().write({"unit_cost": rec.product_id.sudo().standard_price})
        return result

    def unlink(self):
        # A02 audit M31-4 / P31-09b: a consumed line was deleted without trace
        if not self._fix_guard_open():
            for rec in self:
                if rec._m31_line_frozen():
                    raise UserError(
                        "Part line %s on job %s cannot be deleted: it is %s. Consumed "
                        "parts stay on the job record."
                        % (
                            rec.part_number or rec.product_id.display_name,
                            rec.job_id.name,
                            "consumed"
                            if rec.reservation_state == "consumed"
                            else "on a closed job",
                        )
                    )
        return super().unlink()

    def _m31_approved_parts_ceiling(self):
        """The money the customer approved for this job's order, or None when
        no approved estimate caps it (no order, or a zero-charge order whose
        cover M01 decided without an estimate)."""
        self.ensure_one()
        order = self.job_id.sudo().order_id
        if not order or "estimate_ids" not in order._fields:
            return None
        approved = order.estimate_ids.filtered(lambda e: e.state == "approved")
        if not approved:
            return None
        total = 0.0
        for est in approved:
            # M01 may pin what was approved; prefer it over the live total
            pinned = est["approved_total"] if "approved_total" in est._fields else 0.0
            total += pinned or est.grand_total or 0.0
        return total

    def action_consume_part(self):
        """HS-05: Confirm bench consumption of a spare part and stamp the M15 ref.

        A02 audit M31-3 / M31-4 (BRU-WSR-11): parts are consumed only on a job
        that is in repair (which needs an approved order), and never beyond the
        approved estimate. An overrun is REFUSED rather than approved here: the
        estimate is revised and re-approved in M01, so the customer approves
        the new price."""
        for rec in self:
            if rec.reservation_state not in ("draft", "reserved"):
                raise UserError(
                    "Part line %s is already %s." % (rec.display_name, rec.reservation_state)
                )
            job = rec.job_id.sudo()
            if job.state != "in_repair":
                raise UserError(
                    "Parts are consumed on the bench while job %s is in repair (it is %s)."
                    % (job.name, job.state)
                )
            ceiling = rec._m31_approved_parts_ceiling()
            if ceiling is not None:
                consumed = sum(
                    job.part_line_ids.filtered(
                        lambda ln: ln.reservation_state == "consumed"
                    ).mapped("subtotal")
                )
                after = consumed + (rec.subtotal or 0.0)
                if after > ceiling + 0.005:
                    raise UserError(
                        "BRU-WSR-11: consuming %s (BDT %.2f) would take job %s's parts to "
                        "BDT %.2f, above the approved estimate of BDT %.2f. Revise the "
                        "estimate and have it re-approved before fitting more parts."
                        % (
                            rec.part_number or rec.product_id.display_name,
                            rec.subtotal or 0.0,
                            job.name,
                            after,
                            ceiling,
                        )
                    )
            rec._guarded().write(
                {
                    "reservation_state": "consumed",
                    "consumption_ref": rec.consumption_ref or f"M15-CONS-{rec.id}",
                    "consumed_at": fields.Datetime.now(),
                    "consumed_by_id": self.env.user.id,
                }
            )
        return True

    def action_reserve(self):
        """Mark a draft line reserved. M15 stock reservation is not wired yet:
        this records the intent only (A02 audit M31-4; the stock move is P1)."""
        for rec in self:
            if rec.reservation_state != "draft":
                raise UserError("Only a draft part line can be reserved.")
            rec._guarded().write({"reservation_state": "reserved"})
        return True

    def action_release_reservation(self):
        """HS-05: Release an unconsumed spare part reservation back to M15 inventory."""
        for rec in self:
            if rec.reservation_state not in ("draft", "reserved"):
                raise UserError(
                    "Part line %s is %s; only an unconsumed line can be released."
                    % (rec.display_name, rec.reservation_state)
                )
            rec._guarded().write({"reservation_state": "released"})
        return True
