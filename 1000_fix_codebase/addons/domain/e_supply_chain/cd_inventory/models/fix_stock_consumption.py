# cd_inventory — Barcode/QR Scan-to-Consume & Parts Consumption Engine (M15, CD-M15-01).
#
# A06 audit (2026-11-03) M15-3/-5/-6/-15: the issue checked the company-wide
# aggregate, skipped the ledger where the location held no bucket, never
# reduced van stock, took quarantined / in-transit / reserved stock, valued
# the issue at the master's standard cost, accepted -5 (adding stock) and
# 0.25 PCS, issued one serial to two jobs and a serial never received, and a
# forged `consumed` state let a "return" create stock from nothing. Now the
# issue takes UNRESTRICTED, unreserved stock from the bucket of the location
# it names (the `van` class at a van, issued by its custodian), at that
# bucket's average cost; serials are one unit, received, in stock at that
# location, and leave it on issue; the state and the cost are guarded and a
# consumed record is final. A return comes back at the cost it left with;
# a part returned as defective goes to quarantine.
from __future__ import annotations

import logging
from datetime import datetime

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from .fix_inventory_approval import check_location_usable, check_quantity, location_class

_logger = logging.getLogger(__name__)

# The job models an issue can be charged to, looked up only when their addon
# is installed (no manifest dependency on the service-delivery addons).
JOB_MODELS = ("fix.service.order", "fix.workshop.job", "fix.field.order")
WORK_ORDER_MODEL = "fix.work.order"

RETURN_REASONS = [
    ("wrong_diagnosis", "Defect misdiagnosed - part not needed"),
    ("defective_new", "Part DOA / defective out of box"),
    ("customer_refusal", "Customer declined estimate"),
    ("excess_draw", "Excess van stock drawn and returned"),
]


class FixStockConsumption(models.Model):
    """Real-time parts consumption on repair jobs via barcode / QR scanning."""

    _name = "fix.stock.consumption"
    _description = "Job Parts Consumption"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]

    company_id = fields.Many2one(
        "res.company",
        required=True,
        index=True,
        default=lambda self: self.env.company,
    )
    operating_unit_id = fields.Many2one(
        "operating.unit",
        string="Operating Unit",
        index=True,
    )
    name = fields.Char(
        string="Consumption Reference",
        required=True,
        copy=False,
        default="New",
        index=True,
    )
    name_bn = fields.Char(string="ব্যবহারের রেফারেন্স (বাংলা)", help="Bengali reference per DoD-08")

    service_order_ref = fields.Char(string="Service Order Reference", required=True, index=True)
    work_order_ref = fields.Char(string="Work Order Reference", index=True)
    # A06 M15-10: the job the reference resolved to when the part was issued
    job_model = fields.Char(string="Job Model", readonly=True, copy=False)
    job_res_id = fields.Integer(string="Job ID", readonly=True, copy=False)
    work_order_res_id = fields.Integer(string="Work Order ID", readonly=True, copy=False)

    product_id = fields.Many2one("fix.spare.part", string="Spare Part", required=True, index=True)
    location_id = fields.Many2one(
        "fix.stock.location", string="Deduction Location / Van", required=True, index=True
    )
    technician_id = fields.Many2one(
        "hr.employee", string="Consuming Technician", required=True, index=True
    )
    ownership_class = fields.Selection(
        [
            ("owned", "Owned Stock"),
            ("consignment", "Supplier Consignment"),
            ("customer", "Customer Property"),
            ("van", "Van Stock"),
            ("bench", "Bench / WIP"),
            ("warranty", "Warranty Reserve"),
        ],
        string="Issued From Class",
        readonly=True,
        copy=False,
    )
    lot_id = fields.Many2one(
        "fix.stock.lot", string="Issued Serial / Lot", readonly=True, copy=False
    )

    quantity = fields.Float(string="Consumed Quantity", default=1.0, required=True)
    serial_number = fields.Char(string="Part Serial Number / IMEI")
    scanned_code = fields.Char(string="Raw Scanned Barcode/QR", required=True)

    state = fields.Selection(
        [
            ("draft", "Draft Scan"),
            ("consumed", "Consumed on Job"),
            ("returned", "Returned to Location"),
            ("cancelled", "Cancelled"),
        ],
        string="Status",
        default="draft",
        tracking=True,
    )

    consumed_at = fields.Datetime(string="Consumption Timestamp")
    unit_cost = fields.Float(string="Unit Valuation Cost (BDT)", default=0.0)
    total_cost = fields.Float(
        string="Total Valuation Cost (BDT)", compute="_compute_total_cost", store=True
    )

    return_reason = fields.Selection(RETURN_REASONS, string="Return Reason")
    return_notes = fields.Text(string="Return Notes")
    returned_at = fields.Datetime(string="Return Timestamp")

    # what an issue fixes: the job, the part, the place and the quantity
    _ISSUE_FIELDS = (
        "service_order_ref",
        "work_order_ref",
        "product_id",
        "location_id",
        "technician_id",
        "quantity",
        "serial_number",
        "scanned_code",
        "company_id",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "consumed_at",
            "unit_cost",
            "ownership_class",
            "lot_id",
            "return_reason",
            "returned_at",
            "job_model",
            "job_res_id",
            "work_order_res_id",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if len(self) == 1 and self.state not in (False, "draft"):
            locked |= set(self._ISSUE_FIELDS) | {"return_notes"}
        return locked

    @api.depends("quantity", "unit_cost")
    def _compute_total_cost(self):
        for rec in self:
            rec.total_cost = rec.quantity * rec.unit_cost

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].sudo().next_by_code("fix.stock.consumption")
                    or f"CNS-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                )
        return super().create(vals_list)

    def write(self, vals):
        if self and not self._fix_guard_open():
            frozen = {k: vals[k] for k in (*self._ISSUE_FIELDS, "return_notes") if k in vals}
            issued = self.filtered(lambda r: r.state not in (False, "draft"))
            if frozen and any(
                rec._fix_guard_differs(k, v, rec[k]) for rec in issued for k, v in frozen.items()
            ):
                raise UserError(
                    "An issued part is final: its job, part, location, quantity and cost "
                    "cannot change. Return it and issue again."
                )
        return super().write(vals)

    # ---------------------------------------------------------------- checks
    def _resolve_job(self):
        """A06 M15-10: the job reference must name a real job of this company
        (service order, workshop job or field order, whichever addons are
        installed). Returns (model, id, work_order_id); refuses a reference
        that resolves to nothing."""
        self.ensure_one()
        installed = [m for m in JOB_MODELS if m in self.env]
        if not installed:
            return False, 0, 0
        ref = (self.service_order_ref or "").strip()
        found = (False, 0)
        for model in installed:
            Model = self.env[model].sudo()
            domain = [("name", "=", ref)]
            if "company_id" in Model._fields:
                domain.append(("company_id", "in", [self.company_id.id, False]))
            job = Model.search(domain, limit=1) if ref else Model.browse()
            if job:
                found = (model, job.id)
                break
        if not found[0]:
            raise UserError(
                "Job reference %r matches no service order, workshop job or field order: "
                "a part is issued only to a real job (FR-INV-022)." % ref
            )
        work_order_id = 0
        wo_ref = (self.work_order_ref or "").strip()
        if wo_ref and WORK_ORDER_MODEL in self.env:
            work_order = self.env[WORK_ORDER_MODEL].sudo().search([("name", "=", wo_ref)], limit=1)
            if not work_order:
                raise UserError("Work order reference %r matches no work order." % wo_ref)
            work_order_id = work_order.id
        return found[0], found[1], work_order_id

    def _check_issue(self):
        """Every rule an issue must satisfy before stock moves."""
        self.ensure_one()
        part = self.product_id
        if not part:
            raise ValidationError("No valid spare part assigned to consumption.")
        if part.state == "obsolete":
            raise UserError("%s is obsolete and cannot be issued to a job." % part.part_number)
        check_quantity(part, self.quantity, "issue quantity")
        location = self.location_id
        check_location_usable(location, self.env)
        if location.location_type in ("quarantine", "scrap"):
            raise UserError(
                "%s is a %s location: stock there is not issuable."
                % (location.code, location.location_type)
            )
        if location.location_type == "van":
            if self.technician_id != location.technician_id:
                raise UserError(
                    "Van %s is in the custody of %s: %s cannot draw from it (FR-INV-028)."
                    % (
                        location.code,
                        location.technician_id.name or "nobody",
                        self.technician_id.name,
                    )
                )
            hold = (
                self.env["fix.stock.van.recon"]
                .sudo()
                .search([("location_id", "=", location.id), ("state", "=", "discrepancy")], limit=1)
            )
            if hold:
                raise UserError(
                    "Van %s has an unresolved stock discrepancy (%s, variance %s): issues "
                    "from it are held until an Inventory Controller resolves it "
                    "(BRU-INV-12)." % (location.code, hold.name, hold.variance)
                )
        if part.is_serialized:
            if not self.serial_number:
                raise ValidationError(
                    f"Part {part.part_number} is serialized. Serial number is mandatory."
                )
            if abs(self.quantity - 1.0) > 1e-9:
                raise UserError(
                    "%s is serialized: one issue takes one serial (one unit), not %s."
                    % (part.part_number, self.quantity)
                )
            lot = self.env["fix.stock.lot"]._fix_find(part, self.serial_number)
            if not lot:
                raise UserError(
                    "Serial %s of %s was never received: it cannot be issued (BRU-INV-14). "
                    "Quarantine the unit and report it." % (self.serial_number, part.part_number)
                )
            if lot.status != "in_stock" or lot.location_id != location or (lot.qty or 0.0) < 1.0:
                raise UserError(
                    "Serial %s is %s at %s, not in stock at %s: it cannot be issued again."
                    % (
                        lot.name,
                        dict(lot._fields["status"].selection).get(lot.status),
                        lot.location_id.code or "-",
                        location.code,
                    )
                )
            return lot
        return self.env["fix.stock.lot"]

    def action_scan_and_consume(self) -> dict:
        """Atomic scan-to-consume: deducts the location bucket, values the
        issue at the bucket's average cost, books the suspense entry and
        emits the outbox event."""
        self.ensure_one()
        if self.state != "draft":
            raise UserError("Only draft scans can be confirmed for consumption.")
        lot = self._check_issue()
        job_model, job_id, work_order_id = self._resolve_job()
        part = self.product_id
        cls = location_class(self.location_id)
        Onhand = self.env["fix.stock.onhand"]
        bucket = Onhand._bucket(part, self.location_id, cls)
        available = (bucket.qty - bucket.reserved) if bucket else 0.0
        if available + 1e-9 < self.quantity:
            raise UserError(
                f"Insufficient stock for {part.part_number} at {self.location_id.code}: "
                f"{round(available, 4)} available, {self.quantity} requested."
            )
        cost = bucket.unit_cost or 0.0
        Onhand._apply(part, self.location_id, cls, -self.quantity)
        if lot:
            lot._guarded().write({"status": "issued", "qty": 0.0})

        now_utc = fields.Datetime.now()
        self._guarded().write(
            {
                "state": "consumed",
                "consumed_at": now_utc,
                "unit_cost": cost,
                "ownership_class": cls,
                "lot_id": lot.id or False,
                "job_model": job_model,
                "job_res_id": job_id,
                "work_order_res_id": work_order_id,
            }
        )

        # Post GV-005 suspense valuation entry (M15 -> M19 stub)
        suspense_entry = (
            self.env["fix.inventory.valuation.suspense"]
            .sudo()
            .create(
                {
                    "company_id": self.company_id.id,
                    "operating_unit_id": self.location_id.operating_unit_id.id or False,
                    "consumption_id": self.id,
                    "product_id": part.id,
                    "quantity": self.quantity,
                    "unit_cost": cost,
                    "total_valuation": self.quantity * cost,
                    "entry_type": "consumption",
                    "source_ref": self.name,
                    "suspense_account_code": "110999",
                    "status": "pending_gl_cutover",
                }
            )
        )

        # Emit M15 outbox event: stock.consumed
        event_payload = {
            "consumption_id": self.id,
            "consumption_ref": self.name,
            "service_order_ref": self.service_order_ref,
            "work_order_ref": self.work_order_ref or "",
            "part_id": part.id,
            "part_number": part.part_number,
            "quantity": self.quantity,
            "location_id": self.location_id.id,
            "location_code": self.location_id.code,
            "technician_id": self.technician_id.id,
            "serial_number": self.serial_number or "",
            "scanned_code": self.scanned_code,
            "consumed_at": str(now_utc),
            "suspense_entry_id": suspense_entry.id,
        }

        try:
            from libs.py.fix_events import publish

            publish(self.env, "stock.consumed", "fix.stock.consumption", self.id, event_payload)
        except Exception:
            _logger.exception("stock.consumed event publish failed for %s", self.id)

        return {
            "status": "consumed",
            "consumption_ref": self.name,
            "remaining_qty": part.qty_available,
            "valuation_entry": suspense_entry.name,
        }

    def action_return_part(self, reason: str | None = None, notes: str = "") -> dict:
        """Atomic part return at the cost it was issued at. A part returned
        as defective (DOA) goes to quarantine, not back to available stock."""
        self.ensure_one()
        if self.state != "consumed":
            raise UserError("Only consumed parts can be returned to inventory.")
        if reason not in dict(RETURN_REASONS):
            raise UserError(
                "Give the return reason: %s." % ", ".join(k for k, _l in RETURN_REASONS)
            )
        part = self.product_id
        check_location_usable(self.location_id, self.env)
        cls = self.ownership_class or location_class(self.location_id)
        defective = reason == "defective_new"
        Onhand = self.env["fix.stock.onhand"]
        Onhand._apply(
            part,
            self.location_id,
            cls,
            self.quantity,
            self.unit_cost,
            status="quarantine" if defective else "unrestricted",
        )
        lot = self.lot_id
        if lot:
            lot._guarded().write(
                {
                    "status": "quarantined" if defective else "in_stock",
                    "qty": 1.0,
                    "location_id": self.location_id.id,
                }
            )
        quarantine = self.env["fix.stock.quarantine"]
        if defective:
            quarantine = (
                quarantine.sudo()
                ._guarded()
                .with_context(fix_quarantine_in_place=True)
                .create(
                    {
                        "part_id": part.id,
                        "location_id": self.location_id.id,
                        "company_id": self.company_id.id,
                        "ownership_class": cls,
                        "lot_id": lot.id or False,
                        "qty": self.quantity,
                        "reason": "defective",
                        "notes": "Returned as defective from %s" % self.name,
                        "source_ref": self.name,
                    }
                )
            )

        now_utc = fields.Datetime.now()
        self._guarded().write(
            {
                "state": "returned",
                "return_reason": reason,
                "returned_at": now_utc,
            }
        )
        if notes:
            self.sudo()._guarded().write({"return_notes": notes})

        # Post reverse suspense valuation entry, at the ISSUE cost
        suspense_entry = (
            self.env["fix.inventory.valuation.suspense"]
            .sudo()
            .create(
                {
                    "company_id": self.company_id.id,
                    "operating_unit_id": self.location_id.operating_unit_id.id or False,
                    "consumption_id": self.id,
                    "product_id": part.id,
                    "quantity": -self.quantity,
                    "unit_cost": self.unit_cost,
                    "total_valuation": -(self.quantity * self.unit_cost),
                    "entry_type": "return",
                    "source_ref": self.name,
                    "suspense_account_code": "110999",
                    "status": "pending_gl_cutover",
                }
            )
        )

        # Emit M15 outbox event: stock.returned
        event_payload = {
            "consumption_id": self.id,
            "consumption_ref": self.name,
            "service_order_ref": self.service_order_ref,
            "part_id": part.id,
            "part_number": part.part_number,
            "quantity": self.quantity,
            "location_id": self.location_id.id,
            "return_reason": reason,
            "returned_at": str(now_utc),
            "suspense_entry_id": suspense_entry.id,
        }

        try:
            from libs.py.fix_events import publish

            publish(self.env, "stock.returned", "fix.stock.consumption", self.id, event_payload)
        except Exception:
            _logger.exception("stock.returned event publish failed for %s", self.id)

        return {
            "status": "returned",
            "consumption_ref": self.name,
            "restored_qty": part.qty_available,
            "quarantine": quarantine.name or None,
        }
