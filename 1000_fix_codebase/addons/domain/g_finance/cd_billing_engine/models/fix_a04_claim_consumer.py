# fix_a04_claim_consumer - the R8 consumer of warranty_claim.decided
# (A04 build, report §6 C7: the warranty claim's money leg). The claim's own
# controls decided it (M09: brand decision provenance, amount pinning,
# remittance reconciliation); the event was published - and nothing consumed
# it: the receivable on the brand only existed if finance noticed by hand.
#
# Same rules as the A02 hand-backs (cd_settlement_ext/models/fix_a02_handback.py):
#   * relay only: consume_* runs as superuser from cron_relay; a JSON-RPC
#     caller is refused;
#   * the payload is a claim, not evidence: the claim is re-read by its
#     aggregate id, must sit in the state the event announces, and the amount
#     comes from the record. A forged event is refused, dead-lettered, and
#     visible in relay_health();
#   * idempotent per source (fix.ar.invoice is UNIQUE (source_model, source_id));
#   * nothing is collected: the invoice is DRAFT. Finance reviews and issues
#     it (M20's own gapless sequence, GL posting and dunning apply after);
#   * a rejection is a normal outcome, not a fault: the event is acknowledged
#     as a no-op so it does not sit dead-lettered forever.
from odoo import api, models
from odoo.exceptions import AccessError, UserError

# claim states that carry an amount the brand owes us
APPROVED_STATES = ("approved", "partially_approved")


class FixA04ClaimConsumers(models.AbstractModel):
    """R8 consumer of the warranty-claim decision event (no table of its own)."""

    _name = "fix.a04.claim.consumers"
    _description = "A04 Warranty Claim Event Consumers"

    @api.model
    def consume_warranty_claim_decided(self, event: dict) -> dict:
        """warranty_claim.decided -> a DRAFT M20 invoice on the OEM brand.

        The brand master carries no partner link (fix.brand is catalogue
        data), so the OEM's billing partner is the res.partner whose ref is
        the brand's code - the same code the brand API and the M08
        authorisations key on. No unique match means no invoice: a guess here
        would bill the wrong OEM, so the event dead-letters for a human
        instead."""
        if not self.env.su:
            raise AccessError("A04 claim consumers run only from the event relay (report C7).")
        label = "Warranty claim hand-off"
        aggregate = event.get("aggregate")
        if aggregate and aggregate != "fix.warranty.claim":
            raise UserError(
                "%s refused: the event's aggregate is %s, not fix.warranty.claim."
                % (label, aggregate)
            )
        payload = event.get("payload") or {}
        try:
            claim_id = int(event.get("aggregate_id") or 0)
        except (TypeError, ValueError):
            claim_id = 0
        claim = (
            self.env["fix.warranty.claim"].sudo().browse(claim_id).exists() if claim_id else None
        )
        if not claim:
            raise UserError("%s refused: there is no fix.warranty.claim #%s." % (label, claim_id))

        # a rejection has no money leg: acknowledge, don't dead-letter
        if claim.state == "rejected":
            return {"model": claim._name, "id": claim.id, "created": False, "skipped": "rejected"}

        if claim.state not in APPROVED_STATES:
            raise UserError(
                "%s refused: claim %s is %s, not an approved state."
                % (label, claim.claim_no, claim.state)
            )
        amount = claim.approved_amount or 0.0
        claimed = payload.get("approved_amount")
        if claimed is not None:
            try:
                claimed = float(claimed)
            except (TypeError, ValueError):
                raise UserError("%s refused: approved_amount is not a number." % label) from None
            if abs(claimed - amount) > 0.005:
                raise UserError(
                    "%s refused: the event says BDT %.2f but claim %s says BDT %.2f."
                    % (label, claimed, claim.claim_no, amount)
                )
        if amount <= 0.005:
            raise UserError(
                "%s refused: claim %s carries no approved amount." % (label, claim.claim_no)
            )

        # idempotent per source: one invoice per claim, ever
        Invoice = self.env["fix.ar.invoice"].sudo()
        existing = Invoice.search(
            [("source_model", "=", claim._name), ("source_id", "=", claim.id)], limit=1
        )
        if existing:
            return {"model": existing._name, "id": existing.id, "created": False}

        # the OEM's billing partner: res.partner keyed by the brand's code
        brand = claim.brand_id
        if not brand or not brand.code:
            raise UserError(
                "%s refused: claim %s has no brand code to bill." % (label, claim.claim_no)
            )
        oem = self.env["res.partner"].sudo().search([("ref", "=", brand.code)], limit=2)
        if len(oem) != 1:
            raise UserError(
                "%s refused: the brand code %s matches %d res.partner rows (need exactly 1) "
                "- fix the OEM partner master before billing claim %s."
                % (label, brand.code, len(oem), claim.claim_no)
            )

        invoice = Invoice.create(
            {
                "company_id": claim.company_id.id,
                "operating_unit_id": claim.operating_unit_id.id,
                "customer_id": oem.id,
                "currency_id": claim.currency_id.id,
                "source_model": claim._name,
                "source_id": claim.id,
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "description": "Warranty claim %s reimbursement (%s)"
                            % (claim.claim_no, brand.name),
                            "taxable_amount": amount,
                            "vat_amount": 0.0,
                            "line_total": amount,
                        },
                    )
                ],
            }
        )
        invoice.message_post(
            body="Raised by the warranty_claim.decided hand-off of %s: draft invoice for "
            "BDT %.2f to %s (brand code %s). Finance reviews and issues it - nothing is "
            "collected before then." % (claim.claim_no, amount, oem.name, brand.code)
        )
        return {"model": invoice._name, "id": invoice.id, "created": True}
