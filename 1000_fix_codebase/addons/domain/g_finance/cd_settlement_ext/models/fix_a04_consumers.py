# fix_a04_consumers - the R8 consumers of the A04 money events (A04 build,
# report §6 C7: "Commission -> fix.commission.ledger (M53)" and
# "Rebate -> payable"). The emit side landed with the C2-C13 controls: M12 and
# M40 publish commission.earned, cd_partner publishes partner.rebate_approved -
# and nothing consumed them, the exact FF-48 shape the A02 audit fixed for
# service orders (probe K13: "commission.earned published with 0 consumers").
#
# Same rules as the A02 hand-backs (fix_a02_handback.py), which this file
# reuses for its helpers:
#   * relay only: consume_* runs as superuser from cron_relay; a JSON-RPC
#     caller is refused;
#   * the payload is a claim, not evidence: the source record is re-read by
#     its aggregate id, must be in the state the event announces, and every
#     amount comes from the record. A forged event is refused, dead-lettered,
#     and visible in relay_health();
#   * idempotent per source: a replay returns what exists;
#   * nothing is paid: a commission ledger row is EARNED (its own accrual and
#     payout controls apply later); a rebate payout is a PENDING M50
#     instruction that treasury releases and finance records through
#     action_record_payout with the bank reference.
from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError

# how a storefront/subscription-style rail maps onto an M50 payment method
RAIL_METHOD = {
    "bkash": "mobile_fs",
    "nagad": "mobile_fs",
    "rocket": "mobile_fs",
    "upay": "mobile_fs",
    "mobile_wallet": "mobile_fs",
    "sslcommerz": "bank_transfer",
    "card": "bank_transfer",
    "bank_transfer": "bank_transfer",
    "cash": "cash",
}


class FixA04FinanceConsumers(models.AbstractModel):
    """R8 consumers of the A04 money events (no table of its own)."""

    _name = "fix.a04.finance.consumers"
    _description = "A04 Finance Event Consumers"

    def _a04_assert_relay(self):
        if not self.env.su:
            raise AccessError("A04 finance consumers run only from the event relay (report C7).")

    def _a04_source(self, event, model, label):
        handback = self.env["fix.finance.handback"]
        return handback._handback_source(event, model, label)

    # ------------------------------------------------ M12/M40 commission.earned
    @api.model
    def consume_commission_earned(self, event: dict) -> dict:
        """commission.earned -> one M53 fix.commission.ledger row, EARNED.

        Two aggregates publish this event: a marketplace order (M12, seller
        commission - the platform's revenue) and a referral (M40, the channel
        partner's commission - the platform's expense). The ledger already
        models both payee types; nothing here decides rates or amounts, they
        are re-read from the record the event names."""
        self._a04_assert_relay()
        aggregate = event.get("aggregate")
        if aggregate == "fix.marketplace.order":
            return self._commission_marketplace(event)
        if aggregate == "fix.referral":
            return self._commission_referral(event)
        raise UserError(
            "Commission hand-off refused: commission.earned carries aggregate %s, "
            "expected fix.marketplace.order or fix.referral." % aggregate
        )

    def _commission_ledger_exists(self, source_type, source_ref):
        return (
            self.env["fix.commission.ledger"]
            .sudo()
            .search([("source_type", "=", source_type), ("source_ref", "=", source_ref)], limit=1)
        )

    def _commission_marketplace(self, event):
        label = "Commission hand-off (marketplace)"
        order, payload = self._a04_source(event, "fix.marketplace.order", label)
        # idempotent per order, whichever door raised the row (M53-15): a replay
        # after the order moved on returns what exists
        Ledger = self.env["fix.commission.ledger"].sudo()
        existing = Ledger.search([("marketplace_order_id", "=", order.id)], limit=1)
        if existing:
            return {"model": existing._name, "id": existing.id, "created": False}
        if order.state not in ("commissioned", "paid"):
            raise UserError(
                "%s refused: order %s is %s, not commissioned." % (label, order.name, order.state)
            )
        # the seller is the awarded quote's: the order itself carries none
        seller = order.selected_quote_id.seller_id
        if not seller or not seller.partner_id:
            raise UserError(
                "%s refused: order %s has no seller partner to credit." % (label, order.name)
            )
        gross = order.awarded_price or order.selected_quote_id.quoted_price or 0.0
        rate = order.commission_rate or 0.0
        source_ref = "fix.marketplace.order/%s" % order.id
        handback = self.env["fix.finance.handback"]
        handback._handback_check_amount(label, payload, "gross", gross)
        handback._handback_check_amount(
            label, payload, "commission", order.commission_amount or 0.0
        )
        existing = self._commission_ledger_exists("marketplace", source_ref)
        if existing:
            return {"model": existing._name, "id": existing.id, "created": False}
        if gross <= 0.005 or not 0 < rate <= 1:
            raise UserError(
                "%s refused: order %s carries no commission (gross %.2f, rate %.4f)."
                % (label, order.name, gross, rate)
            )
        # the row carries its order (Accrue needs it) and the scheme in force,
        # whose rate and TDS apply (BRU-REV-10); no scheme yet = Accrue refuses
        tier = seller.tier if "tier" in seller._fields else False
        scheme = self.env["fix.commission.scheme"]._find(
            "seller", fields.Date.context_today(self), order.company_id, seller_tier=tier
        )
        row = Ledger.create(
            {
                "company_id": order.company_id.id,
                "operating_unit_id": order.operating_unit_id.id
                or handback._handback_ou(order.company_id).id,
                "seller_partner_id": seller.partner_id.id,
                "source_type": "marketplace",
                "marketplace_order_id": order.id,
                "scheme_id": scheme.id or False,
                "gross_amount": gross,
                "commission_rate": rate,
                "source_ref": source_ref,
            }
        )
        row.message_post(
            body="Raised by the commission.earned hand-off of order %s: gross BDT %.2f at "
            "%.2f%%. Earned only - the buyer dispute window, the GL accrual and the payout "
            "run keep their own controls." % (order.name, gross, rate * 100.0)
        )
        # a dispute raised before the commission existed holds it now (M53-7)
        from .fix_settlement_m53 import OPEN_DISPUTE_STATES

        Adjustment = self.env["fix.settlement.adjustment"].sudo()
        for dispute in (
            self.env["fix.marketplace.dispute"]
            .sudo()
            .search([("order_id", "=", order.id), ("state", "in", OPEN_DISPUTE_STATES)])
        ):
            Adjustment._fix_escrow_for_dispute(dispute)
        return {"model": row._name, "id": row.id, "created": True}

    def _commission_referral(self, event):
        label = "Commission hand-off (referral)"
        referral, payload = self._a04_source(event, "fix.referral", label)
        if referral.state != "commissioned":
            raise UserError(
                "%s refused: referral %s is %s, not commissioned."
                % (label, referral.name, referral.state)
            )
        partner = referral.partner_id
        if not partner or not partner.partner_id:
            raise UserError(
                "%s refused: referral %s has no channel partner to credit." % (label, referral.name)
            )
        gross = referral.base_amount or 0.0
        rate = partner.commission_rate or 0.0
        source_ref = "fix.referral/%s" % referral.id
        handback = self.env["fix.finance.handback"]
        handback._handback_check_amount(label, payload, "gross", gross)
        handback._handback_check_amount(
            label, payload, "commission", referral.commission_amount or 0.0
        )
        existing = self._commission_ledger_exists("partner_referral", source_ref) or (
            self.env["fix.commission.ledger"]
            .sudo()
            .search([("referral_id", "=", referral.id)], limit=1)
        )
        if existing:
            return {"model": existing._name, "id": existing.id, "created": False}
        if gross <= 0.005 or not 0 < rate <= 1:
            raise UserError(
                "%s refused: referral %s carries no commission (base %.2f, rate %.4f)."
                % (label, referral.name, gross, rate)
            )
        scheme = self.env["fix.commission.scheme"]._find(
            "partner",
            fields.Date.context_today(self),
            referral.company_id,
            partner_type=partner.partner_type,
        )
        row = (
            self.env["fix.commission.ledger"]
            .sudo()
            .create(
                {
                    "company_id": referral.company_id.id,
                    "operating_unit_id": referral.operating_unit_id.id
                    or handback._handback_ou(referral.company_id).id,
                    "seller_partner_id": partner.partner_id.id,
                    "source_type": "partner_referral",
                    "referral_id": referral.id,
                    "scheme_id": scheme.id or False,
                    "gross_amount": gross,
                    "commission_rate": rate,
                    "source_ref": source_ref,
                }
            )
        )
        # finance's Accrue Commission picks up THIS row (M53-4: a second create
        # hit UNIQUE referral_id)
        referral.sudo()._guarded().write({"commission_ledger_id": row.id})
        row.message_post(
            body="Raised by the commission.earned hand-off of referral %s: base BDT %.2f at "
            "%.2f%% per the partner's agreed rate. Earned only - the expense accrual "
            "(Dr commission expense / Cr partner payable) is action_post_to_gl's, and the "
            "payout run's." % (referral.name, gross, rate * 100.0)
        )
        return {"model": row._name, "id": row.id, "created": True}

    # ------------------------------------------------ M40 partner.rebate_approved
    @api.model
    def consume_partner_rebate_approved(self, event: dict) -> dict:
        """partner.rebate_approved -> a PENDING M50 payout instruction.

        The rebate's own controls decided it (DOFA ladder, approver,
        amount pin). What was missing is the payable: finance had to notice
        the approval by hand. The instruction is the ceiling - treasury
        releases it, finance records the payout with the bank reference
        (action_record_payout), and nothing is paid before then."""
        self._a04_assert_relay()
        label = "Rebate hand-off"
        rebate, payload = self._a04_source(event, "fix.partner.rebate", label)
        if rebate.state != "approved":
            raise UserError(
                "%s refused: rebate %s is %s, not approved." % (label, rebate.name, rebate.state)
            )
        amount = rebate.amount or 0.0
        handback = self.env["fix.finance.handback"]
        handback._handback_check_amount(label, payload, "amount", amount)
        if amount <= 0.005:
            raise UserError("%s refused: rebate %s has no amount." % (label, rebate.name))
        partner = rebate.partner_id
        finance_partner = partner.partner_id if partner else False
        if not finance_partner:
            raise UserError(
                "%s refused: rebate %s has no channel partner to pay." % (label, rebate.name)
            )
        # the rebate master carries no company of its own: the relay delivers
        # with the event's company (cron_relay -> with_company), which is the
        # company the approval was recorded under.
        company = self.env.company
        pay = handback._handback_instruction(
            rebate,
            {
                "company_id": company.id,
                "operating_unit_id": handback._handback_ou(company).id,
                "payee": finance_partner.name,
                "partner_id": finance_partner.id,
                "amount": amount,
                "method": "bank_transfer",
            },
            "partner_rebate_payout",
        )
        handback._handback_note(
            rebate,
            "Finance hand-back (rebate):",
            "pending treasury payout %s of BDT %.2f to %s. Treasury releases it; finance "
            "records the payout against the bank reference."
            % (pay.name, amount, finance_partner.name),
        )
        return {"model": pay._name, "id": pay.id, "created": True}

    # ------------------------------------------------ RAIL map (shared shape)
    @api.model
    def rail_method(self, rail):
        """A payment rail as an M50 method (storefront rails and friends)."""
        return RAIL_METHOD.get(rail, "bank_transfer")
