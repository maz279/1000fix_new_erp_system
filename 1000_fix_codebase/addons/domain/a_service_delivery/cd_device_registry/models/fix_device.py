# fix.device — THE device model (P04-M01-T02/T03).
# Serial number and IMEI uniqueness: a collision at 5 million assets is a
# data-integrity failure, not an edge case. Duplicate detection enforced.
from odoo import api, fields, models
from odoo.exceptions import ValidationError

import logging

logger = logging.getLogger(__name__)


class FixDevice(models.Model):
    """A physical device registered in the 1000FiX estate.

    The device IS the transacting entity — service orders, warranty claims,
    ownership transfers and device history all reference this record.
    """
    _name = "fix.device"
    _description = "Device"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc"

    # AS-03
    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit",
                                        index=True)

    # Identity (T03: uniqueness enforced, duplicates rejected)
    serial_number = fields.Char(string="Serial Number", index=True, tracking=True,
                                help="Manufacturer serial number — unique when present")
    imei_1 = fields.Char(string="IMEI 1", index=True,
                         help="Primary IMEI for mobile devices — unique when present")
    imei_2 = fields.Char(string="IMEi 2 (Dual SIM)", index=True)
    mac_address = fields.Char(string="MAC Address", index=True)
    legacy_reference = fields.Char(
        string="Legacy Reference", index=True, copy=False,
        help="MIG-03: permanent source system reference (FR-SRM-088)")

    # Classification (references the M37 catalogue kernel)
    device_model_id = fields.Many2one("fix.device.model", string="Device Model",
                                      required=True, ondelete="restrict", index=True)
    brand_id = fields.Many2one(related="device_model_id.brand_id", store=True,
                               string="Brand")
    device_type = fields.Selection(related="device_model_id.device_type", store=True,
                                   string="Device Type")

    # Current owner (linked to the party kernel)
    owner_id = fields.Many2one("res.partner", string="Current Owner",
                               domain=[("is_company", "=", False)],
                               help="The party currently owning this device")
    purchase_date = fields.Date(string="Purchase Date")
    purchase_channel = fields.Selection(
        [("1000fix", "1000FiX"), ("brand_store", "Brand Store"),
         ("third_party", "Third Party"), ("online", "Online"), ("unknown", "Unknown")],
        default="unknown")

    # Warranty status (T04: consumed by M09 in Phase 7)
    warranty_id = fields.One2many("fix.warranty", "device_id", string="Warranty")
    warranty_status = fields.Selection(
        [("in_warranty", "In Warranty"), ("out_of_warranty", "Out of Warranty"),
         ("extended", "Extended Warranty"), ("unknown", "Unknown")],
        compute="_compute_warranty_status", store=True, tracking=True,
        help="Derived from the warranty record's dates and status")

    # Device state
    state = fields.Selection(
        [("registered", "Registered"), ("in_service", "In Service"),
         ("repaired", "Repaired"), ("returned", "Returned to Owner"),
         ("transferred", "Ownership Transferred"), ("scrapped", "Scrapped"),
         ("lost", "Lost/Stolen")],
        default="registered", required=True, tracking=True, index=True)

    # Branch scope
    branch_id = fields.Many2one("fix.branch", string="Registered At")

    # History (T07: every service order, permanently)
    history_ids = fields.One2many("fix.device.history", "device_id",
                                  string="Device History")

    # Documents (T06: through the M24-core attachment API)
    document_ids = fields.One2many("fix.document", "res_id",
                                   domain=[("res_model", "=", "fix.device")],
                                   string="Documents")

    # M17 W2 Completion Slice: Device Lifecycle Management
    lifecycle_stage = fields.Selection(
        [
            ("active", "Active Lifecycle"),
            ("vintage", "Vintage (Limited Parts Support)"),
            ("end_of_life", "End of Life (No OEM Parts)"),
            ("obsolete", "Obsolete / Recycle Only"),
        ],
        default="active",
        required=True,
        tracking=True,
        help="M17 W2: device hardware lifecycle progression affecting spare parts availability",
    )
    end_of_support_date = fields.Date(string="End of Support Date", tracking=True)
    estimated_residual_value_bdt = fields.Monetary(
        string="Estimated Residual Value (BDT)",
        currency_field="currency_id",
        default=0.0,
    )
    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        default=lambda self: self.env.ref("base.BDT", raise_if_not_found=False) or self.env.company.currency_id,
    )

    active = fields.Boolean(default=True, tracking=True)
    name = fields.Char(compute="_compute_name", store=True)

    # Odoo 19 dropped the legacy constraint tuple list;
    # models.Constraint attributes (migrated by tooling/scripts/migrate-sql-constraints.py)
    _serial_unique_when_set = models.Constraint('UNIQUE (serial_number)', 'This serial number is already registered (duplicate detection).')
    _imei1_unique_when_set = models.Constraint('UNIQUE (imei_1)', 'This IMEI is already registered (duplicate detection).')

    @api.depends("device_model_id", "serial_number")
    def _compute_name(self):
        for rec in self:
            parts = [rec.device_model_id.name or "Device"]
            if rec.serial_number:
                parts.append(f"S/N {rec.serial_number}")
            rec.name = " — ".join(parts)

    @api.depends("warranty_id.end_date", "warranty_id.status")
    def _compute_warranty_status(self):
        from datetime import date
        today = date.today()
        for rec in self:
            rec.warranty_status = "unknown"
            for w in rec.warranty_id:
                if w.status == "active" and w.end_date and w.end_date >= today:
                    rec.warranty_status = "in_warranty"
                    break
                elif w.status == "active":
                    rec.warranty_status = "out_of_warranty"
                    break

    @api.constrains("serial_number", "imei_1")
    def _check_identity_format(self):
        for rec in self:
            if rec.imei_1 and (not rec.imei_1.isdigit() or len(rec.imei_1) != 15):
                raise ValidationError(
                    f"IMEI must be exactly 15 digits, got {len(rec.imei_1)}: {rec.imei_1}")

    # Events (T08)
    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            self._emit("device.registered", rec)
        return records

    def write(self, vals):
        result = super().write(vals)
        if "owner_id" in vals:
            for rec in self:
                self._emit("device.transferred", rec)
        if "warranty_id" in vals:
            for rec in self:
                self._emit("device.warranty_updated", rec)
        return result

    def action_transfer_ownership(self, new_owner_id: int):
        """Transfer ownership (T05: portal P01 exposes this in Phase 5)."""
        self.ensure_one()
        old_owner = self.owner_id
        self.write({"owner_id": new_owner_id, "state": "transferred"})
        self.env["fix.device.ownership"].create({
            "device_id": self.id,
            "from_partner_id": old_owner.id if old_owner else False,
            "to_partner_id": new_owner_id,
            "transfer_date": fields.Date.today(),
        })

    def _emit(self, event_type: str, rec) -> None:
        from libs.py.fix_events import publish
        publish(self.env, event_type, "fix.device", rec.id, {
            "device_id": rec.id,
            "serial_number": rec.serial_number,
            "brand": rec.brand_id.name if rec.brand_id else None,
            "model": rec.device_model_id.name,
            "owner_id": rec.owner_id.id if rec.owner_id else None,
        })

    def add_history(self, event_type: str, description: str, order_id=None):
        """Add a permanent history entry (T07)."""
        self.env["fix.device.history"].create({
            "device_id": self.id,
            "event_type": event_type,
            "description": description,
            "service_order_id": order_id,
            "date": fields.Datetime.now(),
        })

    def get_compatible_parts(self, category=None):
        """M17 W2: Query spare parts compatibility matrix for this device model."""
        self.ensure_one()
        domain = [("model_id", "=", self.device_model_id.id), ("active", "=", True)]
        if category:
            domain.append(("category", "=", category))
        return self.env["fix.device.part.compatibility"].search(domain)
