# BRU-FRD-10 (A02 ERP audit M04-F16): a protection plan or membership sold
# over the counter is sold only once the customer has accepted its terms.
#
# Nothing said which products carry terms, and a counter sale of a protection
# plan confirmed with no customer and no acceptance on record. The product
# now says whether its counter sale needs the terms accepted (set by the
# owner on each protection / membership product: an unflagged product sells
# as before), and the sale records who accepted, when, and which customer.
# The acceptance is a stamp of the counter action, never a typed field, and a
# confirm of a flagged product without it is refused.
from odoo import fields, models
from odoo.exceptions import UserError

from .fix_cash_shift import GROUP_CASHIER, GROUP_MANAGER


class ProductTemplateCounterTerms(models.Model):
    _inherit = "product.template"

    fd_counter_terms_required = fields.Boolean(
        string="Counter Sale Needs Terms Acceptance",
        help="BRU-FRD-10: a protection plan or membership. Its counter sale is confirmed only "
        "after the customer has accepted its terms at the counter.",
    )


class FixCounterSaleTerms(models.Model):
    _inherit = "fix.counter.sale"

    terms_required = fields.Boolean(
        related="product_id.product_tmpl_id.fd_counter_terms_required",
        string="Terms Acceptance Required",
    )
    terms_accepted_at = fields.Datetime(string="Terms Accepted At", readonly=True, copy=False)
    terms_accepted_by = fields.Many2one(
        "res.users", string="Terms Acceptance Taken By", readonly=True, copy=False
    )
    terms_accepted_partner_id = fields.Many2one(
        "res.partner", string="Terms Accepted By (Customer)", readonly=True, copy=False
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "terms_accepted_at",
            "terms_accepted_by",
            "terms_accepted_partner_id",
        }

    def _fd_terms_ok(self) -> bool:
        self.ensure_one()
        if not self.terms_required:
            return True
        return bool(self.terms_accepted_at) and self.terms_accepted_partner_id == self.customer_id

    def action_accept_terms(self):
        """The customer has read and accepted the product's terms at the
        counter (BRU-FRD-10). Stamped from the acting cashier and pinned to
        the customer on the sale."""
        if not self._fd_has(GROUP_CASHIER, GROUP_MANAGER):
            raise UserError("Only a Front Desk Cashier records a customer's terms acceptance.")
        for sale in self:
            if sale.state != "draft":
                raise UserError("Terms are accepted before sale %s is confirmed." % sale.name)
            if not sale.terms_required:
                raise UserError("%s carries no terms to accept." % sale.product_id.display_name)
            if not sale.customer_id:
                raise UserError(
                    "Sale %s: choose the customer who accepts the terms first." % sale.name
                )
            sale._guarded().write(
                {
                    "terms_accepted_at": fields.Datetime.now(),
                    "terms_accepted_by": self.env.uid,
                    "terms_accepted_partner_id": sale.customer_id.id,
                }
            )
            sale.message_post(
                body="Terms of %s accepted by %s at the counter."
                % (sale.product_id.display_name, sale.customer_id.display_name)
            )
        return True

    def action_confirm(self):
        for sale in self:
            if sale.state == "draft" and not sale._fd_terms_ok():
                raise UserError(
                    "Sale %s is a %s: the customer accepts its terms before it is sold "
                    "(BRU-FRD-10). Record the acceptance first."
                    % (
                        sale.name,
                        sale.product_id.display_name,
                    )
                )
        return super().action_confirm()
