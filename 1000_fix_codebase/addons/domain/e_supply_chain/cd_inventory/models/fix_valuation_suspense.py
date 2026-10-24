# cd_inventory — M15->M19 Inventory Valuation Suspense Account Model (GV-005 Stub).
# All inventory stock consumption and baseline loads post valuation to suspense account 110999
# until General Ledger (M19) cutover in Wave 3 / Phase R04.
from __future__ import annotations

from datetime import datetime

from odoo import api, fields, models
from odoo.exceptions import UserError


class FixInventoryValuationSuspense(models.Model):
    """M15 Inventory Valuation Suspense Entries (GV-005 STUB-M15-M19-001).

    Maintains double-entry suspense valuation for all physical parts movements
    prior to full M19 Financial GL activation.
    """

    _name = "fix.inventory.valuation.suspense"
    _description = "Inventory Valuation Suspense Entry"
    _order = "create_date desc, id desc"
    _inherit = ["mail.thread", "mail.activity.mixin"]

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
    name = fields.Char(
        string="Entry Reference",
        required=True,
        copy=False,
        default="New",
        index=True,
    )
    name_bn = fields.Char(
        string="মূল্যায়ন এন্ট্রি রেফারেন্স (বাংলা)",
        help="Bengali reference per DoD-08",
    )

    consumption_id = fields.Many2one(
        "fix.stock.consumption",
        string="Originating Consumption",
        index=True,
        ondelete="set null",
    )
    product_id = fields.Many2one(
        "fix.spare.part",
        string="Spare Part",
        required=True,
        index=True,
    )
    quantity = fields.Float(
        string="Movement Quantity",
        required=True,
        default=0.0,
    )
    unit_cost = fields.Float(
        string="Unit Cost (BDT)",
        required=True,
        default=0.0,
    )
    total_valuation = fields.Float(
        string="Total Valuation (BDT)",
        required=True,
        default=0.0,
    )

    entry_type = fields.Selection(
        [
            ("consumption", "Job Consumption"),
            ("return", "Job Return"),
            ("revaluation", "Inventory Revaluation"),
            ("initial_count", "Physical Baseline Migration"),
        ],
        string="Entry Type",
        required=True,
        default="consumption",
    )

    suspense_account_code = fields.Char(
        string="Suspense Account Code",
        required=True,
        default="110999",
        help="Suspense clearing account code (M15->M19 stub)",
    )
    status = fields.Selection(
        [
            ("pending_gl_cutover", "Pending GL Cutover (M19 Suspense)"),
            ("reconciled", "Reconciled to GL"),
            ("archived", "Archived"),
        ],
        string="GL Status",
        required=True,
        default="pending_gl_cutover",
        index=True,
    )

    stub_reference = fields.Char(
        string="GV-005 Stub Reference",
        required=True,
        default="STUB-M15-M19-001",
        readonly=True,
        help="Reference in docs/traceability/gv-005-stub-register.md",
    )
    stub_expiry_date = fields.Date(
        string="Stub Expiry Target",
        default=lambda self: fields.Date.to_date("2026-11-30"),
        readonly=True,
        help="Expiry target: Wave 3 / Phase R04 M19 GL cutover",
    )

    gl_cutover_ref = fields.Char(string="GL Cutover Voucher Ref")
    reconciled_at = fields.Datetime(string="Reconciled Timestamp")
    legacy_reference = fields.Char(
        string="Legacy Reference",
        index=True,
        readonly=True,
        copy=False,
        help="MIG-03: permanent source-system reference written by the inventory "
        "loader (migrations/load_inventory.py) - never edited, never copied",
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                seq = self.env["ir.sequence"].next_by_code("fix.inventory.valuation.suspense")
                vals["name"] = seq or f"VAL-SUSP-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            if "total_valuation" not in vals and "quantity" in vals and "unit_cost" in vals:
                vals["total_valuation"] = vals["quantity"] * vals["unit_cost"]
        return super().create(vals_list)

    def action_reconcile_to_gl(self, gl_voucher_ref: str) -> dict:
        """Mark suspense entry reconciled against M19 General Ledger."""
        self.ensure_one()
        if not gl_voucher_ref:
            raise UserError("GL Voucher reference is mandatory for reconciliation.")
        self.write(
            {
                "status": "reconciled",
                "gl_cutover_ref": gl_voucher_ref,
                "reconciled_at": fields.Datetime.now(),
            }
        )
        return {"status": "reconciled", "entry": self.name, "gl_voucher": gl_voucher_ref}
