# fix.rental.sku — rental SKU model for M13 (P03-M06-T03).
# Built in the kernel so M13 (Phase 9, circular business) composes rather
# than duplicates.
from odoo import api, fields, models
from odoo.exceptions import ValidationError

from .catalogue_roles import ROLE_OFFICER, require_role

RATE_FIELDS = ("daily_rate", "weekly_rate", "monthly_rate", "security_deposit")


class FixRentalSku(models.Model):
    """A rental SKU: an item that can be rented (not just sold).

    M13's circular business model rents equipment. The rental SKU carries
    rental-specific pricing (daily/weekly/monthly) alongside the standard
    product pricing. Built here (T1 kernel) so M13 composes in Phase 9.
    """

    _name = "fix.rental.sku"
    _description = "Rental SKU"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one(
        "operating.unit", string="Operating Unit", help="AS-03: the OU this rental SKU is scoped to"
    )
    catalogue_item_id = fields.Many2one(
        "fix.catalogue.item",
        string="Catalogue Item",
        required=True,
        # A04 audit (2026-11-04) M37-3: deleting the item cascaded its rental
        # SKUs away; a referenced item is now kept (BRU-CAT-03).
        ondelete="restrict",
        index=True,
        help="The catalogue item this rental SKU wraps",
    )
    name = fields.Char(
        related="catalogue_item_id.product_tmpl_id.name", string="Name", readonly=True
    )

    # AS-10: rental pricing — all Monetary with explicit currency_id
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    daily_rate = fields.Monetary(
        string="Daily Rate", currency_field="currency_id", help="AS-10: Monetary, never Float"
    )
    weekly_rate = fields.Monetary(string="Weekly Rate", currency_field="currency_id")
    monthly_rate = fields.Monetary(string="Monthly Rate", currency_field="currency_id")
    security_deposit = fields.Monetary(
        string="Security Deposit",
        currency_field="currency_id",
        help="Refundable deposit required at rental start",
    )

    max_rental_days = fields.Integer(string="Maximum Rental Duration (days)", help="0 = no limit")
    requires_inspection_return = fields.Boolean(
        default=True, help="Whether the item must be inspected on return (M01 QC path)"
    )
    active = fields.Boolean(default=True)

    # A04 audit M37-6 (rs_01): a negative rate or deposit was accepted, which
    # pays the customer to rent and refunds a deposit never taken.
    _rates_not_negative = models.Constraint(
        "CHECK (COALESCE(daily_rate, 0) >= 0 AND COALESCE(weekly_rate, 0) >= 0 "
        "AND COALESCE(monthly_rate, 0) >= 0 AND COALESCE(security_deposit, 0) >= 0 "
        "AND COALESCE(max_rental_days, 0) >= 0)",
        "Rental rates, deposit and maximum duration cannot be negative.",
    )

    @staticmethod
    def _check_rate_vals(vals):
        # Before the INSERT/UPDATE: a ValidationError, not the CHECK's
        # IntegrityError.
        bad = [f for f in (*RATE_FIELDS, "max_rental_days") if (vals.get(f) or 0) < 0]
        if bad:
            raise ValidationError(
                "Rental rates, deposit and maximum duration cannot be negative (%s)."
                % ", ".join(bad)
            )

    @api.model_create_multi
    def create(self, vals_list):
        require_role(self.env, (ROLE_OFFICER,), "Changing a rental SKU")
        for vals in vals_list:
            self._check_rate_vals(vals)
        return super().create(vals_list)

    def write(self, vals):
        require_role(self.env, (ROLE_OFFICER,), "Changing a rental SKU")
        self._check_rate_vals(vals)
        return super().write(vals)
