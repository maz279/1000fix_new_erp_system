# fix_fixed_asset — M49: assets on the M19 seam, CWIP, the M54 break
# (P08-M08). Depreciation is a PURE function — 100% covered (DoD-03).
from decimal import Decimal, ROUND_HALF_UP

from odoo import api, fields, models
from odoo.exceptions import UserError

from libs.py.fix_events import publish


def straight_line_monthly(gross: Decimal, salvage: Decimal,
                          life_months: int) -> Decimal:
    """SL depreciation per month: (gross - salvage) / life, 2dp, never
    negative. The financial path's single authority (100% covered)."""
    if life_months <= 0:
        raise ValueError("life must be positive months")
    if salvage < 0 or gross < 0:
        raise ValueError("gross and salvage cannot be negative")
    if salvage > gross:
        raise ValueError("salvage above gross")
    monthly = (gross - salvage) / Decimal(life_months)
    return monthly.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


class FixFixedAsset(models.Model):
    _name = "fix.fixed.asset"
    _description = "Fixed Asset"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "purchase_date desc"

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True)
    category = fields.Char(required=True)
    seam_id = fields.Many2one(
        "fix.fixed.asset.seam", string="Capitalisation Seam (M19)",
        help="Finance posted the capitalisation event; this asset consumed "
             "it (AR-006 pair 14)")
    currency_id = fields.Many2one("res.currency", required=True,
                                  default=lambda self: self.env.ref("base.BDT"))
    gross = fields.Monetary(string="Gross", currency_field="currency_id",
                            required=True)
    salvage = fields.Monetary(string="Salvage Value",
                              currency_field="currency_id")
    life_months = fields.Integer(required=True)
    purchase_date = fields.Date(required=True)
    state = fields.Selection([("draft", "Draft"), ("active", "Active"),
                              ("disposed", "Disposed")],
                             default="draft", required=True, tracking=True)
    monthly_depreciation = fields.Monetary(
        string="Monthly Depreciation", currency_field="currency_id",
        compute="_compute_depreciation", store=True)
    budget_reference = fields.Char(
        string="Budget Reference (Advisory)",
        help="AR-006 5.4 NOT-A-PREREQ: M49 does NOT read M54. This is a "
             "free-text advisory pointer, deliberately NOT a relation — "
             "the M49<->M54 break")

    @api.depends("gross", "salvage", "life_months")
    def _compute_depreciation(self):
        for rec in self:
            if rec.life_months > 0:
                rec.monthly_depreciation = float(straight_line_monthly(
                    Decimal(str(rec.gross)),
                    Decimal(str(rec.salvage or 0)),
                    rec.life_months))
            else:
                rec.monthly_depreciation = 0.0

    @api.model_create_multi
    def create(self, vals_list):
        recs = super().create(vals_list)
        for rec in recs:
            publish(self.env, "asset.capitalized", "fix.fixed.asset", rec.id,
                    {"name": rec.name, "gross": float(rec.gross)})
        return recs

    def action_accrue_month(self):
        """The monthly accrual M54 consumes (AR-006 4.1 pair 14): the
        EVENT carries the amount; M49 never reads budgets."""
        for rec in self:
            if rec.state != "active":
                raise UserError("Only ACTIVE assets accrue depreciation")
            publish(self.env, "depreciation.accrued", "fix.fixed.asset",
                    rec.id, {"asset": rec.name,
                             "amount": float(rec.monthly_depreciation)})

    def action_dispose(self):
        for rec in self:
            rec.state = "disposed"
            publish(self.env, "asset.disposed", "fix.fixed.asset", rec.id,
                    {"name": rec.name})


class FixCwipEntry(models.Model):
    """Capital work in progress: costs accumulate, then capitalise."""
    _name = "fix.cwip.entry"
    _description = "CWIP Entry"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    name = fields.Char(required=True)
    currency_id = fields.Many2one("res.currency", required=True,
                                  default=lambda self: self.env.ref("base.BDT"))
    amount = fields.Monetary(string="Accumulated Cost",
                             currency_field="currency_id", required=True)
    state = fields.Selection([("open", "Open"), ("capitalised", "Capitalised")],
                             default="open", required=True, tracking=True)
    asset_id = fields.Many2one("fix.fixed.asset", string="Resulting Asset",
                               readonly=True)

    def action_capitalise(self, category, life_months, salvage=0.0):
        """CWIP -> fixed asset: the accumulated cost becomes the gross."""
        for rec in self:
            if rec.state != "open":
                raise UserError("CWIP entry already capitalised")
            if rec.amount <= 0:
                raise UserError("Nothing accumulated to capitalise")
            asset = self.env["fix.fixed.asset"].create({
                "name": rec.name,
                "category": category,
                "gross": rec.amount,
                "salvage": salvage,
                "life_months": life_months,
                "purchase_date": fields.Date.today(),
                "state": "active",
            })
            rec.write({"state": "capitalised", "asset_id": asset.id})
            publish(self.env, "cwip.capitalised", "fix.cwip.entry", rec.id,
                    {"asset": asset.name, "amount": float(rec.amount)})
            return asset

    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")