# fix_asset_lifecycle — M49 asset lifecycle documents:
#   * fix.asset.transfer    — branch / custodian moves with a history
#   * fix.asset.revaluation — IAS 16 revaluation, IAS 36 impairment / reversal
#   * fix.asset.disposal    — sale / scrap / write-off with gain or loss
# Revaluations and disposals are approved by an accounting manager who is not
# the requester (SoD) and post through account.move on the category accounts.
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from .fix_asset_common import (
    MANAGER_GROUP,
    USER_GROUP,
    check_sod,
    money,
    post_entry,
    require_accounts,
    require_group,
)


class FixAssetTransfer(models.Model):
    _name = "fix.asset.transfer"
    _description = "Asset Transfer"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date desc, id desc"

    name = fields.Char(string="Reference", readonly=True, copy=False, default="/")
    asset_id = fields.Many2one(
        "fix.fixed.asset",
        string="Asset",
        required=True,
        index=True,
        domain="[('state', '=', 'active')]",
        tracking=True,
    )
    company_id = fields.Many2one(related="asset_id.company_id", store=True, index=True)
    date = fields.Date(
        string="Transfer Date", required=True, default=fields.Date.context_today, tracking=True
    )
    from_operating_unit_id = fields.Many2one(
        "operating.unit", string="From Branch", readonly=True, copy=False
    )
    from_custodian_id = fields.Many2one(
        "hr.employee", string="From Custodian", readonly=True, copy=False
    )
    operating_unit_id = fields.Many2one("operating.unit", string="To Branch", tracking=True)
    to_custodian_id = fields.Many2one("hr.employee", string="To Custodian", tracking=True)
    reason = fields.Text(string="Reason")
    state = fields.Selection(
        [("draft", "Draft"), ("done", "Done"), ("cancelled", "Cancelled")],
        default="draft",
        required=True,
        tracking=True,
    )
    done_by_id = fields.Many2one("res.users", string="Confirmed By", readonly=True, copy=False)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "/") == "/":
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.asset.transfer") or "/"
        return super().create(vals_list)

    def action_confirm(self):
        """Move the asset. The from-side is captured at confirmation, so the
        history shows exactly where the asset was. No GL entry: the asset
        account is company-wide; the branch is a posting dimension."""
        require_group(self.env, USER_GROUP, "Confirming a transfer")
        for rec in self:
            if rec.state != "draft":
                raise UserError(self.env._("Only draft transfers can be confirmed."))
            asset = rec.asset_id
            if asset.state != "active":
                raise UserError(self.env._("Only active assets can be transferred."))
            to_ou = rec.operating_unit_id or asset.operating_unit_id
            to_custodian = rec.to_custodian_id or asset.custodian_id
            if to_ou == asset.operating_unit_id and to_custodian == asset.custodian_id:
                raise UserError(
                    self.env._("Choose a different branch or custodian — nothing would move.")
                )
            rec.write(
                {
                    "from_operating_unit_id": asset.operating_unit_id.id,
                    "from_custodian_id": asset.custodian_id.id,
                    "operating_unit_id": to_ou.id,
                    "to_custodian_id": to_custodian.id,
                    "state": "done",
                    "done_by_id": self.env.user.id,
                }
            )
            asset.write({"operating_unit_id": to_ou.id, "custodian_id": to_custodian.id})
        return True

    def action_cancel(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError(self.env._("Only draft transfers can be cancelled."))
            rec.state = "cancelled"
        return True


class FixAssetRevaluation(models.Model):
    _name = "fix.asset.revaluation"
    _description = "Asset Revaluation / Impairment"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date desc, id desc"

    name = fields.Char(string="Reference", readonly=True, copy=False, default="/")
    asset_id = fields.Many2one(
        "fix.fixed.asset",
        string="Asset",
        required=True,
        index=True,
        domain="[('state', '=', 'active')]",
        tracking=True,
    )
    company_id = fields.Many2one(related="asset_id.company_id", store=True, index=True)
    operating_unit_id = fields.Many2one(
        related="asset_id.operating_unit_id", store=True, string="Branch"
    )
    currency_id = fields.Many2one(related="asset_id.currency_id")
    kind = fields.Selection(
        [
            ("revaluation", "Revaluation (IAS 16)"),
            ("impairment", "Impairment (IAS 36)"),
            ("impairment_reversal", "Impairment Reversal (IAS 36)"),
        ],
        string="Type",
        required=True,
        default="revaluation",
        tracking=True,
    )
    date = fields.Date(string="Date", required=True, default=fields.Date.context_today)
    new_value = fields.Monetary(
        string="Fair Value / Recoverable Amount",
        required=True,
        tracking=True,
        help="Revaluation: the fair value (IAS 16.31). Impairment: the recoverable "
        "amount — higher of fair value less costs of disposal and value in use (IAS 36.18).",
    )
    basis = fields.Text(string="Basis / Valuer Report")
    requested_by_id = fields.Many2one(
        "res.users", string="Requested By", default=lambda self: self.env.user, readonly=True
    )
    approved_by_id = fields.Many2one("res.users", string="Approved By", readonly=True, copy=False)
    state = fields.Selection(
        [("draft", "Draft"), ("posted", "Posted"), ("cancelled", "Cancelled")],
        default="draft",
        required=True,
        tracking=True,
    )
    carrying_amount = fields.Monetary(string="Carrying Amount Before", readonly=True, copy=False)
    cost_delta = fields.Monetary(string="Change in Cost", readonly=True, copy=False)
    accum_delta = fields.Monetary(string="Change in Impairment", readonly=True, copy=False)
    surplus_amount = fields.Monetary(
        string="To Revaluation Surplus (OCI)", readonly=True, copy=False
    )
    pl_amount = fields.Monetary(
        string="To Profit or Loss (Loss +, Gain -)", readonly=True, copy=False
    )
    move_id = fields.Many2one("account.move", string="Journal Entry", readonly=True, copy=False)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "/") == "/":
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.asset.revaluation") or "/"
        return super().create(vals_list)

    @api.constrains("new_value")
    def _check_value(self):
        for rec in self:
            if rec.new_value < 0:
                raise ValidationError(
                    self.env._("A fair value / recoverable amount cannot be negative.")
                )

    def _split(self):
        """The IAS 16 / IAS 36 split of the change in carrying amount:
        cost_delta, accum_delta, surplus_amount (+ credit OCI), pl_amount
        (+ loss, - gain)."""
        self.ensure_one()
        asset = self.asset_id
        others = asset.revaluation_ids.filtered(lambda r: r.state == "posted" and r != self)
        carrying = asset.book_nbv
        surplus = money(sum(others.mapped("surplus_amount")))
        if self.kind == "revaluation":
            diff = money(self.new_value - carrying)
            if not diff:
                raise UserError(self.env._("The fair value equals the carrying amount."))
            if diff > 0:
                # IAS 16.39: reverse earlier revaluation losses in P&L first
                prior_loss = money(
                    sum(others.filtered(lambda r: r.kind == "revaluation").mapped("pl_amount"))
                )
                to_pl = min(diff, max(prior_loss, 0.0))
                return carrying, diff, 0.0, money(diff - to_pl), -to_pl
            decrease = -diff
            from_surplus = min(decrease, max(surplus, 0.0))  # IAS 16.40
            return carrying, diff, 0.0, -from_surplus, money(decrease - from_surplus)
        if self.kind == "impairment":
            loss = money(carrying - self.new_value)
            if loss <= 0:
                raise UserError(
                    self.env._(
                        "The recoverable amount is not below the carrying amount — no impairment."
                    )
                )
            from_surplus = min(loss, max(surplus, 0.0))  # IAS 36.61 (revalued assets)
            return carrying, 0.0, loss, -from_surplus, money(loss - from_surplus)
        gain = money(self.new_value - carrying)
        if gain <= 0:
            raise UserError(self.env._("The recoverable amount is not above the carrying amount."))
        impaired = money(sum(others.mapped("accum_delta")))
        if gain > impaired:
            raise UserError(
                self.env._(
                    "An impairment reversal is capped at the net impairment recognised "
                    "(%s) — IAS 36.117.",
                    impaired,
                )
            )
        return carrying, 0.0, -gain, 0.0, -gain

    def action_post(self):
        """Approve and post (accounting manager, not the requester)."""
        require_group(self.env, MANAGER_GROUP, "Posting a revaluation / impairment")
        for rec in self:
            if rec.state != "draft":
                raise UserError(self.env._("Only draft documents can be posted."))
            check_sod(self.env, rec.requested_by_id, rec.name)
            asset = rec.asset_id
            if asset.state != "active":
                raise UserError(self.env._("Only active assets can be revalued or impaired."))
            cat = asset.category_id
            if not cat:
                raise UserError(
                    self.env._("Choose the asset category of %s first.", asset.display_name)
                )
            carrying, cost_delta, accum_delta, surplus, pl = rec._split()
            needed = ["journal_id"]
            if cost_delta:
                needed.append("asset_account_id")
            if accum_delta:
                needed.append("accumulated_account_id")
            if surplus:
                needed.append("revaluation_surplus_account_id")
            if pl:
                needed.append("impairment_account_id")
            require_accounts(cat, needed, "Revaluation / impairment")
            label = "%s %s" % (rec.name, asset.display_name)
            lines = []
            if cost_delta:
                lines.append((cat.asset_account_id, cost_delta, 0.0, label))
            if accum_delta:
                lines.append((cat.accumulated_account_id, 0.0, accum_delta, label))
            if surplus:
                lines.append((cat.revaluation_surplus_account_id, 0.0, surplus, label))
            if pl:
                lines.append((cat.impairment_account_id, pl, 0.0, label))
            move = post_entry(self.env, asset.company_id, cat.journal_id, rec.date, rec.name, lines)
            rec.write(
                {
                    "state": "posted",
                    "approved_by_id": self.env.user.id,
                    "carrying_amount": carrying,
                    "cost_delta": cost_delta,
                    "accum_delta": accum_delta,
                    "surplus_amount": surplus,
                    "pl_amount": pl,
                    "move_id": move.id,
                }
            )
        return True

    def action_cancel(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError(self.env._("Only draft documents can be cancelled."))
            rec.state = "cancelled"
        return True


class FixAssetDisposal(models.Model):
    _name = "fix.asset.disposal"
    _description = "Asset Disposal / Write-Off"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date desc, id desc"

    name = fields.Char(string="Reference", readonly=True, copy=False, default="/")
    asset_id = fields.Many2one(
        "fix.fixed.asset",
        string="Asset",
        required=True,
        index=True,
        domain="[('state', '=', 'active')]",
        tracking=True,
    )
    company_id = fields.Many2one(related="asset_id.company_id", store=True, index=True)
    operating_unit_id = fields.Many2one(
        related="asset_id.operating_unit_id", store=True, string="Branch"
    )
    currency_id = fields.Many2one(related="asset_id.currency_id")
    kind = fields.Selection(
        [("sale", "Sale"), ("scrap", "Scrap"), ("write_off", "Write-Off (Lost / Missing)")],
        string="Type",
        required=True,
        default="sale",
        tracking=True,
    )
    date = fields.Date(
        string="Disposal Date", required=True, default=fields.Date.context_today, tracking=True
    )
    partner_id = fields.Many2one("res.partner", string="Buyer")
    proceeds = fields.Monetary(string="Proceeds", tracking=True)
    proceeds_account_id = fields.Many2one(
        "account.account",
        string="Proceeds Account",
        help="Receivable / bank clearing account the sale proceeds are debited to.",
    )
    reason = fields.Text(string="Reason")
    requested_by_id = fields.Many2one(
        "res.users", string="Requested By", default=lambda self: self.env.user, readonly=True
    )
    approved_by_id = fields.Many2one("res.users", string="Approved By", readonly=True, copy=False)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("approved", "Approved"),
            ("posted", "Posted"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )
    cost = fields.Monetary(string="Cost Removed", readonly=True, copy=False)
    accumulated = fields.Monetary(
        string="Accumulated Depreciation Removed", readonly=True, copy=False
    )
    nbv = fields.Monetary(string="Net Book Value", readonly=True, copy=False)
    gain_loss = fields.Monetary(string="Gain (+) / Loss (-)", readonly=True, copy=False)
    move_id = fields.Many2one("account.move", string="Journal Entry", readonly=True, copy=False)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "/") == "/":
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.asset.disposal") or "/"
        return super().create(vals_list)

    @api.constrains("proceeds", "kind")
    def _check_proceeds(self):
        for rec in self:
            if rec.proceeds < 0:
                raise ValidationError(self.env._("Proceeds cannot be negative."))
            if rec.kind == "write_off" and rec.proceeds:
                raise ValidationError(
                    self.env._("A write-off has no proceeds — use Sale or Scrap.")
                )

    def action_approve(self):
        require_group(self.env, MANAGER_GROUP, "Approving a disposal")
        for rec in self:
            if rec.state != "draft":
                raise UserError(self.env._("Only draft disposals can be approved."))
            check_sod(self.env, rec.requested_by_id, rec.name)
            rec.write({"state": "approved", "approved_by_id": self.env.user.id})
        return True

    def action_post(self):
        """Derecognise the asset (IAS 16.67-71): Dr accumulated depreciation,
        Dr proceeds, Cr asset cost; the difference is the gain or loss. Run the
        month's depreciation before disposing so the NBV is current."""
        require_group(self.env, USER_GROUP, "Posting a disposal")
        for rec in self:
            if rec.state != "approved":
                raise UserError(self.env._("Approve the disposal before posting it."))
            asset = rec.asset_id
            if asset.state != "active":
                raise UserError(self.env._("%s is not an active asset.", asset.display_name))
            cat = asset.category_id
            if not cat:
                raise UserError(
                    self.env._("Choose the asset category of %s first.", asset.display_name)
                )
            cost = asset.cost
            accumulated = money(asset.accumulated_depreciation + asset.impairment_total)
            nbv = money(cost - accumulated)
            gain_loss = money(rec.proceeds - nbv)
            needed = ["journal_id", "asset_account_id"]
            if accumulated:
                needed.append("accumulated_account_id")
            if gain_loss > 0:
                needed.append("gain_account_id")
            elif gain_loss < 0:
                needed.append("loss_account_id")
            require_accounts(cat, needed, "Disposal")
            if rec.proceeds and not rec.proceeds_account_id:
                raise UserError(self.env._("Choose the proceeds account for %s.", rec.name))
            label = "%s %s" % (rec.name, asset.display_name)
            lines = [
                (cat.accumulated_account_id, accumulated, 0.0, label),
                (rec.proceeds_account_id, rec.proceeds, 0.0, label),
                (cat.asset_account_id, 0.0, cost, label),
            ]
            if gain_loss > 0:
                lines.append((cat.gain_account_id, 0.0, gain_loss, label))
            elif gain_loss < 0:
                lines.append((cat.loss_account_id, -gain_loss, 0.0, label))
            lines = [ln for ln in lines if ln[0]]
            move = post_entry(self.env, asset.company_id, cat.journal_id, rec.date, rec.name, lines)
            rec.write(
                {
                    "state": "posted",
                    "cost": cost,
                    "accumulated": accumulated,
                    "nbv": nbv,
                    "gain_loss": gain_loss,
                    "move_id": move.id,
                }
            )
            asset._mark_disposed(rec.date)
        return True

    def action_cancel(self):
        for rec in self:
            if rec.state not in ("draft", "approved"):
                raise UserError(self.env._("A posted disposal cannot be cancelled."))
            rec.state = "cancelled"
        return True
