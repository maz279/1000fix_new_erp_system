# M39 subscription operations: usage metering, proration changes and autopay
# mandates on top of fix.subscription / fix.subscription.charge and the
# revenue-recognition schedules.
from odoo import api, fields, models


class FixSubscriptionUsage(models.Model):
    _name = "fix.subscription.usage"
    _description = "Subscription Usage Meter"
    _order = "period_start desc, id desc"

    subscription_id = fields.Many2one(
        "fix.subscription", required=True, ondelete="cascade", index=True
    )
    period_start = fields.Date(required=True)
    period_end = fields.Date(required=True)
    metric = fields.Char(required=True, help="What is metered (seats, GB, prints…).")
    quantity = fields.Float(required=True, default=0.0)
    committed = fields.Float(required=True, default=0.0)
    overage_quantity = fields.Float(compute="_compute_overage", string="Overage")
    overage_charge = fields.Monetary(currency_field="currency_id", compute="_compute_overage")
    overage_rate = fields.Float(default=0.0, help="BDT per overage unit.")
    currency_id = fields.Many2one(related="subscription_id.currency_id", store=True)

    @api.depends("quantity", "committed", "overage_rate")
    def _compute_overage(self):
        for rec in self:
            over = max(0.0, (rec.quantity or 0.0) - (rec.committed or 0.0))
            rec.overage_quantity = over
            rec.overage_charge = round(over * (rec.overage_rate or 0.0), 2)


class FixSubscriptionProration(models.Model):
    _name = "fix.subscription.proration"
    _description = "Subscription Proration"
    _order = "effective_date desc, id desc"

    name = fields.Char(required=True)
    subscription_id = fields.Many2one(
        "fix.subscription", required=True, ondelete="cascade", index=True
    )
    change_type = fields.Selection(
        [("upgrade", "Upgrade"), ("downgrade", "Downgrade"), ("cancel", "Cancellation")],
        required=True,
        default="upgrade",
    )
    from_plan = fields.Char()
    to_plan = fields.Char()
    amount = fields.Monetary(currency_field="currency_id")
    currency_id = fields.Many2one(related="subscription_id.currency_id", store=True)
    effective_date = fields.Date(required=True)
    state = fields.Selection(
        [("draft", "Draft"), ("invoiced", "Invoiced"), ("void", "Void")],
        required=True,
        default="draft",
    )


class FixSubscriptionAutopay(models.Model):
    _name = "fix.subscription.autopay"
    _description = "Subscription Autopay Mandate"
    _order = "id desc"

    subscription_id = fields.Many2one(
        "fix.subscription", required=True, ondelete="cascade", index=True
    )
    method = fields.Selection(
        [("card", "Card"), ("bkash", "bKash"), ("nagad", "Nagad"), ("bank", "Bank mandate")],
        required=True,
        default="card",
    )
    mandate_ref = fields.Char(help="Gateway mandate / token reference.")
    state = fields.Selection(
        [("active", "Active"), ("revoked", "Revoked"), ("expired", "Expired")],
        required=True,
        default="active",
    )
    last_attempt_at = fields.Datetime(readonly=True)
    last_result = fields.Selection(
        [("none", "Never charged"), ("success", "Success"), ("failed", "Failed")],
        required=True,
        default="none",
        readonly=True,
    )
