# fix_damage_claim — M03 damage claims against a consignment. The claim records
# what was damaged in transit, the claimed value and the adjudication; it is the
# record behind the Damage & Claims report.
from odoo import api, fields, models
from odoo.exceptions import UserError


class FixDamageClaim(models.Model):
    _name = "fix.damage.claim"
    _description = "Consignment Damage Claim"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "claimed_on desc, id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit", required=True)
    consignment_id = fields.Many2one(
        "fix.consignment", string="Consignment", required=True, ondelete="cascade", index=True
    )
    claimed_on = fields.Date(required=True, default=fields.Date.context_today)
    claimant = fields.Selection(
        [
            ("customer", "Customer"),
            ("branch", "Branch"),
            ("rider", "Rider"),
            ("courier", "Courier Partner"),
        ],
        required=True,
        default="customer",
    )
    damage_kind = fields.Selection(
        [
            ("physical", "Physical Damage"),
            ("missing", "Missing / Short"),
            ("water", "Water / Liquid"),
            ("packaging", "Packaging Failure"),
            ("other", "Other"),
        ],
        required=True,
        default="physical",
    )
    description = fields.Text(required=True)
    claimed_amount = fields.Monetary(currency_field="currency_id")
    approved_amount = fields.Monetary(currency_field="currency_id")
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    evidence_ref = fields.Char(help="Photo / scan reference for the damage.")
    liability = fields.Selection(
        [
            ("pending", "Pending"),
            ("carrier", "Carrier"),
            ("branch", "Branch"),
            ("customer", "Customer"),
            ("shared", "Shared"),
        ],
        required=True,
        default="pending",
    )
    state = fields.Selection(
        [
            ("open", "Open"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
            ("settled", "Settled"),
        ],
        required=True,
        default="open",
        tracking=True,
    )

    # --- A02 Enterprise Data Capture & DOFA Adjudication Tier ---
    dofa_tier = fields.Selection(
        [
            ("tier_2", "Tier 2 — Logistics Hub Manager (Up to BDT 15,000)"),
            ("tier_3", "Tier 3 — Head of Supply Chain (BDT 15,001 to 50,000)"),
            ("tier_4", "Tier 4 — CFO / COO (> BDT 50,000)"),
        ],
        string="DOFA Adjudication Tier",
        compute="_compute_dofa_tier",
        store=True,
    )
    approved_by_id = fields.Many2one(
        "res.users",
        string="DOFA Adjudication Approver",
        readonly=True,
        copy=False,
    )
    incident_photo_attachment_id = fields.Many2one(
        "ir.attachment",
        string="Transit Damage Photo / Forensic Report",
    )

    @api.depends("claimed_amount", "approved_amount")
    def _compute_dofa_tier(self):
        for rec in self:
            amt = max(rec.claimed_amount or 0.0, rec.approved_amount or 0.0)
            if amt <= 15000.0:
                rec.dofa_tier = "tier_2"
            elif amt <= 50000.0:
                rec.dofa_tier = "tier_3"
            else:
                rec.dofa_tier = "tier_4"

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.damage.claim") or "DMC/New"
        return super().create(vals_list)

    def action_approve(self):
        for rec in self:
            if rec.state != "open":
                raise UserError("Only an open claim can be approved")
            if not rec.approved_amount:
                raise UserError("Enter the approved amount before approving the claim")
            rec.approved_by_id = self.env.user
            rec.state = "approved"

    def action_reject(self):
        for rec in self:
            if rec.state != "open":
                raise UserError("Only an open claim can be rejected")
            rec.state = "rejected"

    def action_settle(self):
        for rec in self:
            if rec.state != "approved":
                raise UserError("Settle an approved claim")
            rec.state = "settled"
