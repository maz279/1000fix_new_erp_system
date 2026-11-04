# cd_inventory — Multi-location & Van Stock Locations (M15, CD-M15-01).
from __future__ import annotations

import logging

from odoo import api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class FixStockLocation(models.Model):
    """Multi-location storage facility including branch warehouses and mobile van stock."""

    _name = "fix.stock.location"
    _description = "Inventory Location & Van Stock"
    # A06 audit (2026-11-03): the status and the audit stamps were free
    # fields; they now change only through their actions.
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
    name = fields.Char(string="Location Name", required=True, tracking=True)
    name_bn = fields.Char(string="লোকেশন নাম (বাংলা)", help="Bengali name per DoD-08")
    code = fields.Char(string="Location Code", required=True, size=16, index=True)

    location_type = fields.Selection(
        [
            ("central", "Central Warehouse"),
            ("branch", "Branch Hub / Workshop"),
            ("van", "Mobile Technician Van Stock"),
            ("quarantine", "Quarantine / Inspection"),
            ("scrap", "Scrap / E-Waste Disposal"),
        ],
        string="Location Type",
        required=True,
        default="branch",
        tracking=True,
    )

    branch_id = fields.Many2one("fix.branch", string="Branch Hub", index=True)
    technician_id = fields.Many2one(
        "hr.employee",
        string="Custodian Technician",
        index=True,
        help="Designated field technician for mobile van stock",
    )
    van_plate = fields.Char(string="Vehicle Registration / Plate Number")
    is_van_stock = fields.Boolean(
        string="Is Van Stock",
        compute="_compute_is_van_stock",
        store=True,
    )
    is_van_location = fields.Boolean(
        string="Is Van Location",
        compute="_compute_is_van_stock",
        store=True,
    )

    parent_id = fields.Many2one("fix.stock.location", string="Parent Location", index=True)
    state = fields.Selection(
        [("draft", "Draft"), ("active", "Active"), ("inactive", "Inactive")],
        string="Status",
        default="active",
        tracking=True,
    )
    active = fields.Boolean(default=True)
    last_audit_date = fields.Date(string="Last Physical Audit Date")
    audit_discrepancy_count = fields.Integer(string="Audit Discrepancies", default=0)
    legacy_reference = fields.Char(
        string="Legacy Reference",
        index=True,
        readonly=True,
        copy=False,
        help="MIG-03: permanent source-system reference written by the inventory "
        "loader (migrations/load_inventory.py) - never edited, never copied",
    )

    _code_company_unique = models.Constraint(
        "UNIQUE (code, company_id)",
        "Location code must be unique per company.",
    )

    @api.depends("location_type")
    def _compute_is_van_stock(self):
        for loc in self:
            val = loc.location_type == "van"
            loc.is_van_stock = val
            loc.is_van_location = val

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "last_audit_date",
            "audit_discrepancy_count",
        }

    def action_set_active(self):
        self._guarded().write({"state": "active"})
        return True

    def action_set_inactive(self):
        """An inactive location moves no stock (every movement checks it)."""
        self._guarded().write({"state": "inactive"})
        return True

    @api.constrains("location_type", "technician_id")
    def _check_van_technician(self):
        for loc in self:
            if loc.location_type == "van" and not loc.technician_id:
                raise ValidationError(
                    "Mobile van stock locations must designate a custodian technician."
                )

    def action_audit_van_stock(self, audited_skus: list[dict] | None = None) -> dict:
        """Execute mobile van stock physical reconciliation audit."""
        self.ensure_one()
        if self.location_type != "van":
            raise ValidationError("Van stock audit can only be performed on van stock locations.")

        if not audited_skus:
            # A06 audit M15-16: an audit with no lines used to report 100%
            # accuracy; nothing audited is not an accurate van.
            raise ValidationError("A van stock audit needs at least one audited line.")
        total_audited = len(audited_skus)
        discrepancies = sum(1 for s in audited_skus if s.get("discrepancy_qty", 0) != 0)

        self._guarded().write(
            {"last_audit_date": fields.Date.today(), "audit_discrepancy_count": discrepancies}
        )

        # Emit van.reconciled outbox event
        accuracy_pct = round((total_audited - discrepancies) / total_audited * 100.0, 1)
        event_payload = {
            "van_id": self.id,
            "van_code": self.code,
            "technician_id": self.technician_id.id if self.technician_id else False,
            "audited_qty": total_audited,
            "discrepancy_qty": discrepancies,
            "accuracy_pct": accuracy_pct,
            "audit_date": str(self.last_audit_date),
        }

        try:
            from libs.py.fix_events import publish

            publish(self.env, "van.reconciled", "fix.stock.location", self.id, event_payload)
        except Exception:
            _logger.exception("van.reconciled event publish failed for location %s", self.id)

        return {
            "van_id": self.id,
            "audited_count": total_audited,
            "discrepancies": discrepancies,
            "accuracy_pct": accuracy_pct,
            "status": "reconciled",
        }
