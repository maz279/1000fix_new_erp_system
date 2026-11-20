# M39 bills an MSP fee change (A02 ERP audit M05-F4 / owner item O14, 20 Nov 2026;
# A02 ERP pass 2 M05-S05 / S06 / S07, owner decision D8).
#
# The MSP recurring charge is the M39 subscription on the same M08 contract;
# the price master is the M05 contract's terms (D8). Every commercial
# amendment of an MSP contract (covered devices up OR down, per-device price)
# is recorded in its terms history (fix.msp.terms.amendment) with the monthly
# fee delta, and published as msp.commercial_terms_amended. This consumer
# turns the amendments not yet billed into ONE price change of the
# subscription, through M39's own controlled path (a draft proration routed
# for approval: never applied by its requester).
#
# Pass 2 fixed how uplifts were lost or overwritten (M05-S05):
#   * the consumer refused an event whose device count was not the contract's
#     CURRENT count, so of two quick amendments (50 -> 60 -> 80) the first was
#     refused and its 10 devices never billed. The amount now comes from the
#     terms history rows, so delivery order does not matter;
#   * each event asked for "recurring amount + its own delta", so two changes
#     waiting for approval both started from the same amount and the second
#     approval overwrote the first. A change still waiting is superseded by
#     one covering every unbilled amendment, and a proration is applied only
#     while the subscription still has the amount it was computed from
#     (fix_subscription_ops).
#
# msp.client_offboarded (M05-S07): the offboarded client's subscription churns.
#
# Relay-only (superuser) like every hand-back consumer. cd_subscription does
# not depend on cd_msp_contract: the M05 records are reached by model name,
# and without M05 there is nothing to bill.
from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError

from libs.py.fix_events import publish

CYCLE_MONTHS = {"monthly": 1, "quarterly": 3, "annual": 12}
MARKER = "MSP fee change"
LIVE = ("cancelled", "churned")
AMENDMENT_REF = "fix.subscription.proration,%s"


class FixSubscriptionMspUplift(models.AbstractModel):
    _name = "fix.subscription.msp.uplift"
    _description = "M39: bill an MSP fee change"

    def _msp_assert_relay(self):
        if not self.env.su:
            raise AccessError("Only the event relay turns an MSP fee change into a price change.")

    def _msp_contract(self, event):
        payload = event.get("payload") or {}
        msp_id = int(event.get("aggregate_id") or payload.get("msp_contract_id") or 0)
        msp = self.env["fix.msp.contract"].sudo().browse(msp_id).exists()
        if not msp:
            raise UserError("MSP fee change refused: MSP contract %s does not exist." % msp_id)
        return msp

    def _msp_live_subscriptions(self, msp):
        return (
            self.env["fix.subscription"]
            .sudo()
            .search([("contract_id", "=", msp.contract_id.id), ("state", "not in", LIVE)])
        )

    @api.model
    def consume_msp_commercial_terms_amended(self, event: dict) -> dict:
        self._msp_assert_relay()
        if "fix.msp.terms.amendment" not in self.env:
            return {"skipped": "M05 not installed"}
        msp = self._msp_contract(event)
        payload = event.get("payload") or {}
        amendment = (
            self.env["fix.msp.terms.amendment"]
            .sudo()
            .browse(int(payload.get("amendment_id") or 0))
            .exists()
        )
        if not amendment or amendment.msp_contract_id != msp:
            raise UserError(
                "MSP fee change refused: amendment %s is not a terms change of %s."
                % (payload.get("amendment_id"), msp.name)
            )
        return self._msp_bill_pending(msp)

    @api.model
    def consume_msp_device_uplift(self, event: dict) -> dict:
        """The pre-pass-2 event (still in the outbox on a live server): the
        contract's unbilled amendments are billed the same way."""
        self._msp_assert_relay()
        if "fix.msp.terms.amendment" not in self.env:
            return {"skipped": "M05 not installed"}
        return self._msp_bill_pending(self._msp_contract(event))

    def _msp_bill_pending(self, msp):
        """One price change for every amendment of ``msp`` not yet billed."""
        Amendment = self.env["fix.msp.terms.amendment"].sudo()._guarded()
        Proration = self.env["fix.subscription.proration"].sudo()
        rows = Amendment.search(
            [("msp_contract_id", "=", msp.id), ("billing_state", "in", ("pending", "requested"))],
            order="effective_date, id",
        )
        # a requested change whose proration is no longer in flight: billed
        # when it was approved; flagged when a person voided or rejected it
        # (finance decided; the reconciliation report shows the difference)
        in_flight = Proration
        for row in rows.filtered(lambda r: r.billing_state == "requested"):
            pro = self._msp_proration_of(row)
            if pro and pro.state in ("draft", "pending"):
                in_flight |= pro
            elif pro and pro.state in ("approved", "invoiced"):
                row.write({"billing_state": "billed"})
            else:
                row.write(
                    {
                        "billing_state": "flagged",
                        "billing_note": "Its price change was voided or rejected in M39.",
                    }
                )
        rows = rows.filtered(lambda r: r.billing_state in ("pending", "requested"))
        if not rows.filtered(lambda r: r.billing_state == "pending"):
            return {"created": False, "reason": "nothing new to bill"}
        subs = self._msp_live_subscriptions(msp)
        if len(subs) != 1:
            note = (
                "the M08 contract has %d live M39 subscriptions; finance bills it on the right one"
                % len(subs)
            )
            rows.filtered(lambda r: r.billing_state == "pending").write(
                {"billing_state": "flagged", "billing_note": note[:250]}
            )
            msp.message_post(
                body="MSP fee change of BDT %.2f a month not billed automatically: %s."
                % (sum(rows.mapped("monthly_delta")), note)
            )
            return {"skipped": "%d subscriptions" % len(subs)}
        sub = subs
        for pro in in_flight:
            # superseded by one change covering every unbilled amendment
            pro._approval_void("superseded by a later MSP fee change")
            pro._guarded().write({"state": "void", "approval_state": "none"})
            pro.message_post(body="Voided: superseded by a later MSP fee change of %s." % msp.name)
        months = CYCLE_MONTHS.get(sub.billing_cycle, 1)
        delta = round(sum(rows.mapped("monthly_delta")), 2)
        new_amount = round(max((sub.recurring_amount or 0.0) + delta * months, 0.0), 2)
        effective = max(min(rows.mapped("effective_date")), sub.start_date or fields.Date.today())
        reason = "%s of %s (%s): BDT %+.2f a month - %s" % (
            MARKER,
            msp.name,
            ", ".join("terms #%s from %s" % (r.id, r.effective_date) for r in rows),
            delta,
            "; ".join(r.reason or "" for r in rows)[:200],
        )
        proration = Proration.create_for_plan_change(sub, new_amount, effective_date=effective)
        proration.action_request_approval(justification=reason)
        rows.write({"billing_state": "requested", "billing_ref": AMENDMENT_REF % proration.id})
        sub.message_post(body=reason)
        return {
            "model": sub._name,
            "id": sub.id,
            "created": True,
            "new_amount": new_amount,
            "proration_id": proration.id,
        }

    def _msp_proration_of(self, row):
        ref = row.billing_ref or ""
        if not ref.startswith("fix.subscription.proration,"):
            return self.env["fix.subscription.proration"]
        return (
            self.env["fix.subscription.proration"]
            .sudo()
            .browse(int(ref.split(",")[1] or 0))
            .exists()
        )

    @api.model
    def consume_msp_client_offboarded(self, event: dict) -> dict:
        """M05-S07: an offboarded client's MSP subscription churns (billing
        stops; outstanding balances ride the M20 collections ladder)."""
        self._msp_assert_relay()
        if "fix.msp.contract" not in self.env:
            return {"skipped": "M05 not installed"}
        msp = self._msp_contract(event)
        if msp.lifecycle != "offboarded":
            raise UserError("MSP offboarding refused: %s is not offboarded." % msp.name)
        churned = 0
        for sub in self._msp_live_subscriptions(msp):
            sub._guarded().write({"state": "churned", "cancelled_on": fields.Date.today()})
            sub.message_post(
                body="Churned: the MSP client of %s was offboarded (%s)."
                % (msp.name, msp.offboarded_at)
            )
            publish(
                self.env,
                "subscription.churned",
                "fix.subscription",
                sub.id,
                {"reason": "msp_offboarded", "msp_contract_id": msp.id},
            )
            churned += 1
        return {"churned": churned}
