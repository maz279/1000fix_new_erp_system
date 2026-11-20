# M39 bills an MSP device uplift (A02 ERP audit M05-F4 / owner item O14, 20 Nov 2026).
#
# Raising an MSP contract's covered devices (M05 action_amend_terms) publishes
# msp.device_uplift, which nothing consumed: 50 -> 80 devices changed no bill.
# The MSP recurring charge is the M39 subscription on the same M08 contract, so
# the uplift becomes that subscription's price change, through M39's own
# controlled path (action_request_price_change): never applied by its
# requester, approved by a second person or the proration DOFA. The new
# recurring amount is the old one plus the added devices at the contract's
# per-device monthly price, for the subscription's billing cycle.
#
# Relay-only (superuser) like every hand-back consumer: the payload is a claim,
# the MSP contract is re-read, and one event requests one change (replays
# return what exists). cd_subscription does not depend on cd_msp_contract: the
# contract is reached by model name, and without M05 there is nothing to bill.
from odoo import api, models
from odoo.exceptions import AccessError, UserError

CYCLE_MONTHS = {"monthly": 1, "quarterly": 3, "annual": 12}
MARKER = "MSP device uplift (event %s)"


class FixSubscriptionMspUplift(models.AbstractModel):
    _name = "fix.subscription.msp.uplift"
    _description = "M39: bill an MSP device uplift"

    @api.model
    def consume_msp_device_uplift(self, event: dict) -> dict:
        if not self.env.su:
            raise AccessError("Only the event relay turns an MSP uplift into a price change.")
        if "fix.msp.contract" not in self.env:
            return {"skipped": "M05 not installed"}
        payload = event.get("payload") or {}
        msp_id = int(event.get("aggregate_id") or payload.get("msp_contract_id") or 0)
        msp = self.env["fix.msp.contract"].browse(msp_id).exists()
        if not msp:
            raise UserError("MSP uplift refused: MSP contract %s does not exist." % msp_id)
        added = int(payload.get("added_devices") or 0)
        if added <= 0:
            return {"skipped": "no devices added"}
        # the claim must match the record: a forged count bills nothing
        if int(payload.get("new_device_count") or -1) != (msp.device_count or 0):
            raise UserError(
                "MSP uplift refused: the event says %s devices, %s holds %s."
                % (payload.get("new_device_count"), msp.name, msp.device_count)
            )
        rate = msp.per_device_monthly or 0.0
        if rate <= 0:
            msp.message_post(
                body="Device uplift of %d not billed: the contract has no per-device price." % added
            )
            return {"skipped": "no per-device price"}
        Sub = self.env["fix.subscription"].sudo()
        subs = Sub.search(
            [
                ("contract_id", "=", msp.contract_id.id),
                ("state", "not in", ("cancelled", "churned")),
            ]
        )
        if len(subs) != 1:
            msp.message_post(
                body="Device uplift of %d (BDT %.2f a month) not billed automatically: the M08 "
                "contract has %d live M39 subscriptions; finance bills it on the right one."
                % (added, added * rate, len(subs))
            )
            return {"skipped": "%d subscriptions" % len(subs)}
        sub = subs
        marker = MARKER % (event.get("event_id") or "")
        seen = (
            self.env["mail.message"]
            .sudo()
            .search_count(
                [("model", "=", sub._name), ("res_id", "=", sub.id), ("body", "ilike", marker)]
            )
        )
        if seen:
            return {"model": sub._name, "id": sub.id, "created": False}
        months = CYCLE_MONTHS.get(sub.billing_cycle, 1)
        new_amount = round((sub.recurring_amount or 0.0) + added * rate * months, 2)
        reason = "%s: %s from %s to %s devices at BDT %.2f per device a month" % (
            marker,
            msp.name,
            payload.get("old_device_count"),
            msp.device_count,
            rate,
        )
        sub.action_request_price_change(new_amount, reason=reason)
        sub.message_post(body=reason)
        return {"model": sub._name, "id": sub.id, "created": True, "new_amount": new_amount}
