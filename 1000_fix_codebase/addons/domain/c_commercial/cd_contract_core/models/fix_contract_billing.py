# fix_contract_billing - the C10 billing periods (A04 report §6 C7 first
# bullet: "Contract billing schedule -> M20 invoices").
#
# fix.contract already carried the two service halves: _fix_billing_schedule()
# computes the in-force term as equal periods of the annual value (pro-rated
# by days, the last period absorbing rounding), and mark_billed_through()
# freezes what an amendment can no longer touch. Nothing bridged them to
# money: no invoice was ever raised, so the billed-through date only moved
# when a test moved it.
#
# A period row is EVIDENCE, not an input: it is raised by the M20 billing
# hand-off (cd_billing_engine's walker) from the contract's own schedule, and
# its amount is the schedule's amount. The invoice link is added on the
# finance side (cd_billing_engine inherits this model), because this module
# must not depend on the billing engine - the walker depends on this module.
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class FixContractBillingPeriod(models.Model):
    """One billing period of a contract and the invoice the M20 hand-off
    raised for it (the invoice itself lives in cd_billing_engine)."""

    _name = "fix.contract.billing.period"
    _description = "Contract Billing Period"
    _order = "period_start, id"

    _period_unique = models.Constraint(
        "UNIQUE (contract_id, period_start)", "One billing period per contract cycle"
    )
    _amount_non_negative = models.Constraint(
        "CHECK (amount >= 0)", "A billing period cannot be negative"
    )

    contract_id = fields.Many2one(
        "fix.contract",
        required=True,
        index=True,
        ondelete="cascade",
        readonly=True,
        help="The contract this period bills. Set by the billing hand-off.",
    )
    company_id = fields.Many2one(
        "res.company",
        related="contract_id.company_id",
        store=True,
        index=True,
        string="Company",
    )
    operating_unit_id = fields.Many2one(
        "operating.unit",
        related="contract_id.operating_unit_id",
        store=True,
        index=True,
        string="Operating Unit",
    )
    currency_id = fields.Many2one(related="contract_id.currency_id")
    period_start = fields.Date(required=True, readonly=True)
    period_end = fields.Date(required=True, readonly=True)
    amount = fields.Monetary(
        string="Charge (VAT excl.)",
        currency_field="currency_id",
        readonly=True,
        help="The schedule's pro-rated amount for this period; the last period "
        "of a term absorbs rounding so the periods total the term value.",
    )

    @api.depends("contract_id.code", "contract_id.name", "period_start", "period_end")
    def _compute_display_name(self):
        for period in self:
            period.display_name = "%s: %s to %s" % (
                period.contract_id.code or period.contract_id.name or "Contract",
                period.period_start,
                period.period_end,
            )

    @api.constrains("period_start", "period_end")
    def _check_period_order(self):
        for period in self:
            if period.period_end < period.period_start:
                raise ValidationError(
                    "A billing period cannot end before it starts (%s)." % period.contract_id.code
                )
