# cd_cash_position — Rider COD Settlement (A08 · M50, finance side only).
#
# Source of truth for what a rider collected: storefront orders paid "Cash on
# Delivery" (fix.storefront.order.payment_rail = cod) whose logistics
# consignment (fix.consignment) was delivered by that rider. The rider app
# and the collection itself belong to Logistics; finance settles the
# rider's remittance against the expected COD and books any shortage.
# Service-order cash collected by field technicians is NOT a COD source yet
# (no model records it) — the settlement says so instead of guessing.
from __future__ import annotations

from odoo import api, fields, models
from odoo.exceptions import UserError

from .treasury_common import bank_account_of, post_treasury_move, treasury_account


class FixCodSettlement(models.Model):
    _name = "fix.cod.settlement"
    _description = "Rider COD Settlement"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "settlement_date desc, id desc"

    name = fields.Char(string="Settlement Ref", readonly=True, copy=False, index=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", required=True, index=True)
    branch_id = fields.Many2one("fix.branch", string="Receiving Branch", index=True)
    rider_id = fields.Many2one("hr.employee", string="Rider", required=True, index=True)
    settlement_date = fields.Date(required=True, default=fields.Date.context_today)
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    order_ids = fields.Many2many(
        "fix.storefront.order",
        "fix_cod_settlement_order_rel",
        "settlement_id",
        "order_id",
        string="COD Orders",
        readonly=True,
    )
    order_count = fields.Integer(compute="_compute_amounts", store=True, string="Orders")
    expected_amount = fields.Monetary(
        string="COD Expected", currency_field="currency_id", compute="_compute_amounts", store=True
    )
    remittance_method = fields.Selection(
        [("cash", "Cash to Branch"), ("bank", "Bank Deposit"), ("mfs", "bKash / Nagad")],
        default="cash",
        required=True,
    )
    remittance_journal_id = fields.Many2one(
        "account.journal",
        string="Received Into",
        domain="[('type', 'in', ('bank', 'cash')), ('company_id', '=', company_id)]",
    )
    remitted_amount = fields.Monetary(
        string="Remitted", currency_field="currency_id", tracking=True
    )
    remittance_ref = fields.Char(string="Remittance Ref / TrxID")
    variance = fields.Monetary(
        currency_field="currency_id",
        compute="_compute_amounts",
        store=True,
        help="Remitted less expected: negative = rider short",
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("submitted", "Submitted"),
            ("settled", "Settled"),
            ("disputed", "Disputed"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )
    submitted_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    settled_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    dispute_reason = fields.Char(tracking=True)
    move_id = fields.Many2one("account.move", string="GL Entry", readonly=True, copy=False)

    @api.depends("order_ids.total_amount", "remitted_amount")
    def _compute_amounts(self):
        for rec in self:
            rec.order_count = len(rec.order_ids)
            rec.expected_amount = sum(rec.order_ids.mapped("total_amount"))
            rec.variance = round(rec.remitted_amount - rec.expected_amount, 2)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("name"):
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.cod.settlement") or "COD"
        return super().create(vals_list)

    @api.model
    def _open_cod_orders(self, rider, company):
        """Delivered COD orders of this rider not yet in a live settlement."""
        orders = self.env["fix.storefront.order"].search(
            [
                ("company_id", "=", company.id),
                ("payment_rail", "=", "cod"),
                ("state", "not in", ("cancelled", "draft")),
                ("carrier_consignment_id.rider_id", "=", rider.id),
                ("carrier_consignment_id.state", "=", "delivered"),
            ]
        )
        settled = self.search(
            [("company_id", "=", company.id), ("state", "!=", "disputed")]
        ).mapped("order_ids")
        return orders - settled

    def action_load_orders(self):
        """Pull every delivered, unsettled COD order of the rider."""
        for rec in self:
            if rec.state != "draft":
                raise UserError("Orders are loaded on a draft settlement only.")
            orders = self._open_cod_orders(rec.rider_id, rec.company_id) | rec.order_ids
            rec.order_ids = [(6, 0, orders.ids)]
        return True

    def action_submit(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only a draft settlement is submitted.")
            if not rec.order_ids:
                raise UserError(
                    "No delivered COD orders for %s — nothing to settle." % rec.rider_id.name
                )
            if rec.remitted_amount < 0:
                raise UserError("The remitted amount cannot be negative.")
            if not rec.remittance_journal_id:
                raise UserError("Select the cash/bank account the remittance was received into.")
            if rec.remittance_method != "cash" and not (rec.remittance_ref or "").strip():
                raise UserError("A bank/MFS remittance needs its reference (TrxID / slip no).")
            rec.write({"state": "submitted", "submitted_by_id": self.env.uid})
        return True

    def action_settle(self):
        """Approve and post: Dr cash/bank (remitted) + Dr rider shortage
        (short) / Cr COD clearing (expected) [+ Cr rider shortage if over].
        The approver must not be the submitter (SoD)."""
        for rec in self:
            if rec.state != "submitted":
                raise UserError("Only a submitted settlement is settled.")
            if rec.submitted_by_id == self.env.user:
                raise UserError("Segregation of duties: the submitter cannot settle their own COD.")
            if not self.env.user.has_group("account.group_account_manager"):
                raise UserError("Settling COD needs the accounting manager role.")
            cash = bank_account_of(rec.remittance_journal_id)
            clearing = treasury_account(self.env, rec.company_id, "cod_clearing")
            lines = [(cash, "COD remitted %s" % rec.name, rec.remitted_amount, 0.0, None)]
            if rec.variance < -0.005:
                shortage = treasury_account(self.env, rec.company_id, "rider_shortage")
                lines.append(
                    (shortage, "Rider short %s" % rec.rider_id.name, -rec.variance, 0.0, None)
                )
            elif rec.variance > 0.005:
                shortage = treasury_account(self.env, rec.company_id, "rider_shortage")
                lines.append(
                    (shortage, "Rider over %s" % rec.rider_id.name, 0.0, rec.variance, None)
                )
            lines.append((clearing, "COD collected %s" % rec.name, 0.0, rec.expected_amount, None))
            move = post_treasury_move(
                self.env,
                rec.company_id,
                rec.settlement_date,
                "COD %s — %s" % (rec.name, rec.rider_id.name),
                lines,
                branch=rec.branch_id,
                source="treasury",
            )
            rec.write({"state": "settled", "settled_by_id": self.env.uid, "move_id": move.id})
        return True

    def action_dispute(self):
        for rec in self:
            if rec.state not in ("draft", "submitted"):
                raise UserError("A settled COD is not disputed — reverse its entry instead.")
            if not (rec.dispute_reason or "").strip():
                raise UserError("Record the dispute reason first.")
            rec.state = "disputed"
        return True
