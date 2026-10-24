# cd_inventory — Barcode/QR Scan-to-Consume & Parts Consumption Engine (M15, CD-M15-01).
from __future__ import annotations

import logging
from datetime import datetime

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class FixStockConsumption(models.Model):
    """Real-time parts consumption on repair jobs via barcode / QR scanning."""

    _name = "fix.stock.consumption"
    _description = "Job Parts Consumption"
    _inherit = ["mail.thread", "mail.activity.mixin"]

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

    product_id = fields.Many2one("fix.spare.part", string="Spare Part", required=True, index=True)
    location_id = fields.Many2one(
        "fix.stock.location", string="Deduction Location / Van", required=True, index=True
    )
    technician_id = fields.Many2one(
        "hr.employee", string="Consuming Technician", required=True, index=True
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

    return_reason = fields.Selection(
        [
            ("wrong_diagnosis", "Defect misdiagnosed - part not needed"),
            ("defective_new", "Part DOA / defective out of box"),
            ("customer_refusal", "Customer declined estimate"),
            ("excess_draw", "Excess van stock drawn and returned"),
        ],
        string="Return Reason",
    )
    return_notes = fields.Text(string="Return Notes")
    returned_at = fields.Datetime(string="Return Timestamp")

    @api.depends("quantity", "unit_cost")
    def _compute_total_cost(self):
        for rec in self:
            rec.total_cost = rec.quantity * rec.unit_cost

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.stock.consumption")
                    or f"CNS-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                )
        return super().create(vals_list)

    def action_scan_and_consume(self) -> dict:
        """Atomic scan-to-consume: deducts stock, records valuation, emits outbox event."""
        self.ensure_one()
        if self.state != "draft":
            raise UserError("Only draft scans can be confirmed for consumption.")

        part = self.product_id
        if not part:
            raise ValidationError("No valid spare part assigned to consumption.")

        # Check serialization
        if part.is_serialized and not self.serial_number:
            raise ValidationError(
                f"Part {part.part_number} is serialized. Serial number is mandatory."
            )

        # Check stock balance
        if part.qty_available < self.quantity:
            raise UserError(
                f"Insufficient stock for {part.part_number}: {part.qty_available} available, {self.quantity} requested."
            )

        # Deduct stock
        part.sudo().write({"qty_available": part.qty_available - self.quantity})

        now_utc = fields.Datetime.now()
        self.write(
            {
                "state": "consumed",
                "consumed_at": now_utc,
                "unit_cost": part.unit_cost,
            }
        )

        # Post GV-005 suspense valuation entry (M15 -> M19 stub)
        suspense_model = self.env["fix.inventory.valuation.suspense"]
        suspense_entry = suspense_model.sudo().create(
            {
                "consumption_id": self.id,
                "product_id": part.id,
                "quantity": self.quantity,
                "unit_cost": part.unit_cost,
                "total_valuation": self.quantity * part.unit_cost,
                "entry_type": "consumption",
                "suspense_account_code": "110999",
                "status": "pending_gl_cutover",
            }
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

    def action_return_part(self, reason: str, notes: str = "") -> dict:
        """Atomic part return: restores inventory, reverses suspense valuation, emits outbox event."""
        self.ensure_one()
        if self.state != "consumed":
            raise UserError("Only consumed parts can be returned to inventory.")

        part = self.product_id
        part.sudo().write({"qty_available": part.qty_available + self.quantity})

        now_utc = fields.Datetime.now()
        self.write(
            {
                "state": "returned",
                "return_reason": reason,
                "return_notes": notes,
                "returned_at": now_utc,
            }
        )

        # Post reverse suspense valuation entry
        suspense_model = self.env["fix.inventory.valuation.suspense"]
        suspense_entry = suspense_model.sudo().create(
            {
                "consumption_id": self.id,
                "product_id": part.id,
                "quantity": -self.quantity,
                "unit_cost": part.unit_cost,
                "total_valuation": -(self.quantity * part.unit_cost),
                "entry_type": "return",
                "suspense_account_code": "110999",
                "status": "pending_gl_cutover",
            }
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
        }
