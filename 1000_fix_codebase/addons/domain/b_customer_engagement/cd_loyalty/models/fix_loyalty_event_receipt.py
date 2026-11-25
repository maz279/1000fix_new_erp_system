# fix_loyalty_event_receipt — the idempotency ledger of M10's event consumers.
#
# A03 audit M10-10/M10-11: nothing consumed service_order.closed or
# party.merged, so points were never earned and never followed a merged
# party. The R8 relay now delivers those events, and redelivers on failure,
# so each consumer must do its work once. A receipt is that "once": its key
# names the business fact (this order earned on this programme, this merge
# event was applied), and the UNIQUE key makes a second, concurrent delivery
# fail at the database instead of posting twice.
from odoo import api, fields, models


class FixLoyaltyEventReceipt(models.Model):
    _name = "fix.loyalty.event.receipt"
    _description = "Loyalty Event Consumer Receipt"
    _order = "id desc"
    _rec_name = "key"

    key = fields.Char(required=True, readonly=True, index=True)
    event_id = fields.Char(string="Event ID", readonly=True, index=True)
    event_type = fields.Char(readonly=True, index=True)
    outcome = fields.Char(readonly=True, help="What the consumer did, in plain words.")
    account_id = fields.Many2one(
        "fix.loyalty.account", readonly=True, index=True, ondelete="set null"
    )
    ledger_ids = fields.Many2many("fix.loyalty.ledger", string="Ledger Lines", readonly=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )

    _key_unique = models.Constraint("UNIQUE (key)", "A loyalty event is applied once.")

    @api.model
    def _seen(self, key: str) -> bool:
        return bool(self.sudo().search_count([("key", "=", key)], limit=1))

    @api.model
    def _record(self, key: str, event: dict, outcome: str, account=None, lines=None):
        return self.sudo().create(
            {
                "key": key,
                "event_id": (event or {}).get("event_id") or False,
                "event_type": (event or {}).get("event_type") or False,
                "outcome": outcome[:500],
                "account_id": account.id if account else False,
                "ledger_ids": [(6, 0, lines.ids)] if lines else False,
                "company_id": (account.company_id.id if account else False) or self.env.company.id,
            }
        )
