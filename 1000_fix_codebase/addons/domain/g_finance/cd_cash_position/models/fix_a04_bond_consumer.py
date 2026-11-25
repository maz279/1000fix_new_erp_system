# fix_a04_bond_consumer - the R8 consumer of tender_bond.claimed (A04 report
# §7.10's last open money leg: "tender-bond encashment GL (treasury
# workstream)").
#
# The DOFA-routed claim decision (fix.tender.bond.action_bond_decision_approve)
# records that the procuring entity encashed the bank guarantee - and nothing
# carried the loss to the books. Same rules as the other A04 consumers:
#   * relay only (consume_* is superuser, from cron_relay);
#   * the payload is a claim, not evidence: the bond is re-read, its state
#     must be "claimed", and the amount comes from the record;
#   * idempotent per source (one BOND-ENCASH move per bond, by ref);
#   * nothing is guessed: the loss account and the credit clearing come from
#     the treasury account roles (cd_cash_position.account_code.*), and a
#     missing account refuses the posting with the parameter to configure.
from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError

from .treasury_common import post_treasury_move, treasury_account

MOVE_REF = "BOND-ENCASH-{bond}"


class FixA04BondConsumers(models.AbstractModel):
    """R8 consumer of the tender-bond encashment event (no table of its own)."""

    _name = "fix.a04.bond.consumers"
    _description = "A04 Tender Bond Event Consumers"

    @api.model
    def consume_tender_bond_claimed(self, event: dict) -> dict:
        if not self.env.su:
            raise AccessError("A04 bond consumers run only from the event relay (report C7).")
        label = "Tender bond encashment hand-off"
        aggregate = event.get("aggregate")
        if aggregate and aggregate != "fix.tender.bond":
            raise UserError(
                "%s refused: the event's aggregate is %s, not fix.tender.bond." % (label, aggregate)
            )
        payload = event.get("payload") or {}
        try:
            bond_id = int(event.get("aggregate_id") or 0)
        except (TypeError, ValueError):
            bond_id = 0
        bond = self.env["fix.tender.bond"].sudo().browse(bond_id).exists() if bond_id else None
        if not bond:
            raise UserError("%s refused: there is no fix.tender.bond #%s." % (label, bond_id))
        if bond.state != "claimed":
            raise UserError(
                "%s refused: bond %s is %s, not claimed." % (label, bond.name, bond.state)
            )
        amount = bond.amount or 0.0
        claimed = payload.get("amount")
        if claimed is not None:
            try:
                claimed = float(claimed)
            except (TypeError, ValueError):
                raise UserError("%s refused: the payload amount is not a number." % label) from None
            if abs(claimed - amount) > 0.005:
                raise UserError(
                    "%s refused: the event says BDT %.2f but bond %s says BDT %.2f."
                    % (label, claimed, bond.name, amount)
                )
        if amount <= 0.005:
            raise UserError("%s refused: bond %s has no amount to encash." % (label, bond.name))

        company = bond.tender_id.company_id or self.env.company
        ref = MOVE_REF.format(bond=bond.name)
        existing = (
            self.env["account.move"]
            .sudo()
            .search([("ref", "=", ref), ("company_id", "=", company.id)], limit=1)
        )
        if existing:
            return {"model": existing._name, "id": existing.id, "created": False}

        loss = treasury_account(self.env, company, "bond_encashment_loss")
        clearing = treasury_account(self.env, company, "outgoing_clearing")
        entry_date = bond.claimed_at and fields.Date.to_date(bond.claimed_at)
        entry_date = entry_date or fields.Date.context_today(bond)
        move = post_treasury_move(
            self.env,
            company,
            entry_date,
            ref,
            [
                (
                    loss,
                    "Guarantee encashed: %s (%s)"
                    % (bond.name, bond.claim_reason or "no reason recorded"),
                    amount,
                    0.0,
                    False,
                ),
                (clearing, "Bank: guarantee %s encashed" % bond.name, 0.0, amount, False),
            ],
            source="treasury",
        )
        bond.message_post(
            body="Encashment of BDT %.2f posted by the tender_bond.claimed hand-off: "
            "Dr guarantee encashment loss / Cr outgoing clearing (move %s)."
            % (amount, move.name or move.id)
        )
        return {"model": move._name, "id": move.id, "created": True}
