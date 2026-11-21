# A06 ERP audit integration (21 Nov 2026): received-not-billed for goods that
# are not spare parts.
#
# The bill clears GRNI (100503) for every line of its PO (P12 / X03). GRNI is
# credited at receipt by M15's real-time posting for spare parts, by the
# service entry for services (P05) and by M44 for imports - but an M16 goods
# receipt of anything else (tools, consumables, stationery bought on a PO)
# made no M15 receipt and credited nothing: its bill left a stuck GRNI debit.
# Such goods are now accrued like a service when the M16 receipt is posted:
# Dr the product's expense account / Cr GRNI at the receipt value. Skipped:
# spare parts (M15 posts them), a service entry's receipt (P05 posts it), an
# import's GRN (M44 posts it) and a capital purchase (CWIP, X25).
from odoo import fields, models

from .ap_gl import ap_account, ap_journal, post_ap_move
from .fix_ap_ext import _q


class FixPurchaseReceiptGrniGoods(models.Model):
    _inherit = "fix.purchase.receipt"

    ap_grni_move_id = fields.Many2one(
        "account.move", string="GRNI Accrual (non-stock goods)", readonly=True, copy=False
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"ap_grni_move_id"}

    def action_post(self):
        result = super().action_post()
        if self.env.context.get("fix_service_entry_post"):
            return result  # P05: the service entry posts its own accrual
        for rec in self.filtered(lambda r: r.state == "posted" and not r.ap_grni_move_id):
            rec._fix_accrue_non_stock_goods()
        return result

    def _fix_is_spare_part(self, product, company):
        if not product or "fix.spare.part" not in self.env:
            return False
        return bool(
            self.env["fix.spare.part"]
            .sudo()
            .search_count([("product_id", "=", product.id), ("company_id", "=", company.id)])
        )

    def _fix_accrue_non_stock_goods(self):
        """Posted as the system once the receipt passed M16's own checks: the
        receiver holds no accounting rights."""
        self.ensure_one()
        env = self.env(su=True)
        rec = self.sudo()
        order = rec.purchase_order_id
        company = order.company_id
        if "capex_request_id" in order._fields and order.capex_request_id:
            return  # X25: capitalised through CWIP, never accrued here
        if "import_order_id" in rec._fields and rec.import_order_id:
            return  # M44 posts the import's own GRNI entry
        if "fix.purchase.service.entry" in env and env["fix.purchase.service.entry"].search_count(
            [("receipt_id", "=", rec.id)]
        ):
            return  # P05: the service entry posts it
        lines = []
        partner = order.vendor_id.commercial_partner_id
        for line in rec.line_ids:
            product = line.po_line_id.product_id
            qty = line.qty_received or 0.0
            if qty <= 0 or product.type == "service" or self._fix_is_spare_part(product, company):
                continue
            value = _q((line.unit_value_bdt or 0.0) * qty)
            if not value:
                continue
            expense = product.product_tmpl_id.with_company(company)._get_product_accounts().get(
                "expense"
            ) or ap_account(env, company, "expense")
            label = "Goods received %s %s %s" % (rec.name, order.name, product.display_name)
            lines += [
                (expense, label, value, 0.0, partner),
                (ap_account(env, company, "grni"), label, 0.0, value, partner),
            ]
        if not lines:
            return
        move = post_ap_move(
            env,
            company,
            ap_journal(env, company, "purchase"),
            fields.Date.context_today(rec.with_context(tz="Asia/Dhaka")),
            "Goods received (non-stock) %s %s" % (rec.name, order.name),
            lines,
            order.operating_unit_id,
        )
        rec._guarded().write({"ap_grni_move_id": move.id})
