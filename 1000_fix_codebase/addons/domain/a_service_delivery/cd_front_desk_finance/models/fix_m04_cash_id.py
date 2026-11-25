# M04 capture audit (18 Nov 2026): the high-value cash ID check
# (cd_front_desk fix.cash.id.check, FR-FRD-019 / BRU-FRD-04) for the
# multi-item basket. A basket is ONE cash payment, so the threshold applies to
# the basket's total, not to each item's sale: a BDT 60,000 basket of two
# BDT 30,000 items needs the customer's NID. One check covers the basket and
# every counter sale it raises.
from odoo import api, fields, models
from odoo.exceptions import UserError


class FixCashIdCheckBasket(models.Model):
    _inherit = "fix.cash.id.check"

    _basket_unique = models.Constraint("UNIQUE (basket_id)", "A basket has one ID check.")

    basket_id = fields.Many2one(
        "fix.counter.basket", string="Counter Basket", index=True, ondelete="restrict"
    )

    @api.model
    def _hv_target(self, sale):
        if sale.basket_id:
            return self._hv_basket_target(sale.basket_id)
        return super()._hv_target(sale)

    @api.model
    def _hv_basket_target(self, basket):
        key = self.env["fix.counter.sale"]._counter_method_for(basket.payment_method_id)
        return basket, basket.total, key == "cash"

    @api.model
    def _hv_target_from_vals(self, vals):
        basket = self.env["fix.counter.basket"].browse(vals.get("basket_id")).exists()
        sale = self.env["fix.counter.sale"].browse(vals.get("sale_id")).exists()
        if basket and sale:
            raise UserError("Choose the counter sale or the basket, not both.")
        if basket:
            return self._hv_basket_target(basket)
        return super()._hv_target_from_vals(vals)

    @api.model
    def _hv_check_for(self, record):
        if record._name == "fix.counter.basket":
            return self.sudo().search([("basket_id", "=", record.id)], limit=1)
        return super()._hv_check_for(record)

    @api.model
    def _hv_link_vals(self, record):
        if record._name == "fix.counter.basket":
            return {"basket_id": record.id, "sale_id": False}
        return super()._hv_link_vals(record)


class FixCounterBasketHighValue(models.Model):
    _inherit = "fix.counter.basket"

    def action_confirm(self):
        Check = self.env["fix.cash.id.check"]
        for basket in self:
            if basket.state == "draft":
                Check._hv_require(*Check._hv_basket_target(basket))
        return super().action_confirm()
