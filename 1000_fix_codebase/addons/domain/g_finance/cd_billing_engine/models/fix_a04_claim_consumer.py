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
#   * idempotent: what the books already hold for the claim (its invoices less
#     their credit notes) is compared with what the brand now owes, and only
#     the difference is booked;
#   * nothing is collected: an invoice is DRAFT and a reduction is a SUBMITTED
#     credit note on M20's approval ladder. Finance reviews and issues them.
#
# A04 ERP audit (20 Nov 2026):
#   * M09-F1 / X4: the OEM's billing partner is the brand's partner_id
#     (cd_warranty_claims), the ref == brand code partner only as the legacy
#     fallback. 0 of fix_real's 161 brands resolved, so every receivable
#     dead-lettered; the refusal now says what to link.
#   * M09-F7: an appeal re-decides a claim. A lower or rejected re-decision left
#     the first OEM invoice on AR (1,500 owed after the brand rejected); a
#     higher one was ignored. The difference is now booked: a draft invoice is
#     dropped, an issued one is credited (credit note, reason warranty_claim),
#     and an increase raises a supplementary draft on the decision record.
#   * M09-F9: the reimbursement credits 400110 "In Warranty Claim Income"
#     (role warranty_claim_income), not service sales 400100. VAT on an OEM
#     reimbursement is an M51/owner decision: the invoice keeps the current
#     no-VAT treatment unless cd_billing_engine.warranty_claim_vat_mode is
#     "standard" (M51 determination on the reimbursement), and says which.
from decimal import ROUND_HALF_UP, Decimal

from odoo import api, models
from odoo.addons.cd_tax_engine_bd.models import tax_logic
from odoo.exceptions import AccessError, UserError

from .fix_ar_engine import AR_ACCOUNTS, _ar_account
from .fix_billing_engine import m51_determine

# claim states that carry an amount the brand owes us
APPROVED_STATES = ("approved", "partially_approved")
DECISION_MODEL = "fix.warranty.claim.decision"
PARAM_VAT_MODE = "cd_billing_engine.warranty_claim_vat_mode"
TWO = Decimal("0.01")

# M09-F9: the account the OEM reimbursement credits (fix_real: 400110 In
# Warranty Claim Income, type income). Overridable by
# cd_billing_engine.account_code.warranty_claim_income; the owner confirms.
AR_ACCOUNTS.setdefault(
    "warranty_claim_income", ("400110", "In Warranty Claim Income (OEM reimbursement)")
)


class FixA04ClaimConsumers(models.AbstractModel):
    """R8 consumer of the warranty-claim decision event (no table of its own)."""

    _name = "fix.a04.claim.consumers"
    _description = "A04 Warranty Claim Event Consumers"

    # ------------------------------------------------------------ helpers
    @api.model
    def _claim_invoices(self, claim):
        """Every OEM invoice the claim's decisions raised (not cancelled)."""
        Invoice = self.env["fix.ar.invoice"].sudo()
        domain = [
            "|",
            "&",
            ("source_model", "=", claim._name),
            ("source_id", "=", claim.id),
            "&",
            ("source_model", "=", DECISION_MODEL),
            ("source_id", "in", claim.decision_ids.ids or [0]),
        ]
        return Invoice.search([*domain, ("state", "!=", "cancelled")], order="id")

    @api.model
    def _booked(self, invoices):
        """The VAT-exclusive amount the books hold for the claim: the invoices'
        taxable value less every credit note still standing on them."""
        booked = 0.0
        for inv in invoices:
            total = inv.total_payable or 0.0
            taxable = total - (inv.vat_amount or 0.0)
            ratio = (taxable / total) if total else 1.0
            credits = inv.credit_note_ids.filtered(lambda n: n.state != "rejected")
            booked += taxable - sum(credits.mapped("amount")) * ratio
        return round(booked, 2)

    @api.model
    def _oem_partner(self, claim, label):
        brand = claim.brand_id
        if not brand:
            raise UserError("%s refused: claim %s has no brand to bill." % (label, claim.claim_no))
        partner = brand.billing_partner() if hasattr(brand, "billing_partner") else None
        if not partner:
            raise UserError(
                "%s refused: brand %s (%s) has no OEM billing partner. Link the brand's legal "
                "entity on the brand (OEM Billing Partner, fix.brand.partner_id) - or give "
                "exactly one res.partner the ref %s - before billing claim %s."
                % (label, brand.name, brand.code or "-", brand.code or "-", claim.claim_no)
            )
        return partner

    @api.model
    def _line_vals(self, claim, amount):
        """The reimbursement line and the VAT note: no VAT (the current
        treatment) unless the owner sets the M51 standard determination."""
        mode = (self.env["ir.config_parameter"].sudo().get_param(PARAM_VAT_MODE) or "none").strip()
        description = "Warranty claim %s reimbursement (%s)" % (claim.claim_no, claim.brand_id.name)
        if mode == "standard":
            det = m51_determine(
                self.env,
                [
                    tax_logic.TaxLine(
                        product_code="SVC",
                        qty=Decimal("1"),
                        unit_price=Decimal(str(amount)).quantize(TWO, ROUND_HALF_UP),
                    )
                ],
                company=claim.company_id,
            ).lines[0]
            return {
                "description": description,
                "taxable_amount": float(det.taxable_amount),
                "vat_amount": float(det.vat_amount),
                "line_total": float(det.line_total),
            }, "VAT: M51 standard determination (cd_billing_engine.warranty_claim_vat_mode)."
        return {
            "description": description,
            "taxable_amount": amount,
            "vat_amount": 0.0,
            "line_total": amount,
        }, (
            "VAT: none charged on the OEM reimbursement (current treatment, pending the M51/"
            "owner decision; cd_billing_engine.warranty_claim_vat_mode)."
        )

    @api.model
    def _raise_invoice(self, claim, amount, source_model, source_id, label):
        oem = self._oem_partner(claim, label)
        line, vat_note = self._line_vals(claim, amount)
        income = _ar_account(self.env, claim.company_id, "warranty_claim_income")
        vals = {
            "company_id": claim.company_id.id,
            "operating_unit_id": claim.operating_unit_id.id,
            "customer_id": oem.id,
            "currency_id": claim.currency_id.id,
            "source_model": source_model,
            "source_id": source_id,
            # FR-ARB-010: an invoice not raised from a closed order is
            # issued only with a reason (E2E3 E3-06, fix_real copy, 11 Nov).
            "manual_reason": "Warranty claim %s - OEM reimbursement (%s)"
            % (claim.claim_no, claim.brand_id.code or claim.brand_id.name),
            "line_ids": [(0, 0, line)],
        }
        if income:
            vals["revenue_account_id"] = income.id
        invoice = self.env["fix.ar.invoice"].sudo().create(vals)
        invoice.message_post(
            body="Raised by the warranty_claim.decided hand-off of %s: draft invoice for "
            "BDT %.2f to %s (brand %s). Finance reviews and issues it - nothing is "
            "collected before then. %s%s"
            % (
                claim.claim_no,
                amount,
                oem.name,
                claim.brand_id.code or claim.brand_id.name,
                vat_note,
                ""
                if income
                else " Income account role warranty_claim_income is not on this chart: the "
                "default revenue role applies.",
            )
        )
        return invoice

    @api.model
    def _reduce(self, claim, invoices, reduce_by, label):
        """Take `reduce_by` (VAT-exclusive) off what the books hold: drafts
        are dropped first (and re-raised for any remainder by the caller),
        then issued invoices are credited through the M20 ladder."""
        notes = self.env["fix.credit.note"]
        drafts = invoices.filtered(lambda i: i.state == "draft")
        dropped = self._booked(drafts)
        for inv in drafts:
            inv.sudo().action_cancel(
                "%s: the brand's decision on %s changed (appeal)" % (label, claim.claim_no)
            )
        remaining = round(reduce_by - dropped, 2)
        if remaining <= 0.005:
            return notes
        for inv in invoices.filtered(lambda i: i.state in ("issued", "paid")).sorted("id", True):
            if remaining <= 0.005:
                break
            total = inv.total_payable or 0.0
            taxable = total - (inv.vat_amount or 0.0)
            open_taxable = self._booked(inv)
            take = min(remaining, open_taxable)
            if take <= 0.005:
                continue
            gross = round(take * (total / taxable), 2) if taxable else take
            notes |= (
                self.env["fix.credit.note"]
                .sudo()
                ._fix_request_credit(
                    inv,
                    gross,
                    "warranty_claim",
                    note="%s: the brand re-decided claim %s at BDT %.2f (appeal); BDT %.2f of "
                    "this invoice is no longer owed."
                    % (label, claim.claim_no, claim.approved_amount, take),
                )
            )
            remaining = round(remaining - take, 2)
        if remaining > 0.005:
            claim.message_post(
                body="%s: BDT %.2f more is no longer owed by the brand but no OEM invoice is "
                "open to credit; finance reviews it." % (label, remaining)
            )
        return notes

    # ------------------------------------------------------------ consumer
    @api.model
    def consume_warranty_claim_decided(self, event: dict) -> dict:
        """warranty_claim.decided -> the OEM's receivable matches the decision."""
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

        if claim.state == "rejected":
            target = 0.0
        elif claim.state in APPROVED_STATES:
            target = round(claim.approved_amount or 0.0, 2)
            claimed = payload.get("approved_amount")
            if claimed is not None:
                try:
                    claimed = float(claimed)
                except (TypeError, ValueError):
                    raise UserError(
                        "%s refused: approved_amount is not a number." % label
                    ) from None
                if abs(claimed - target) > 0.005:
                    raise UserError(
                        "%s refused: the event says BDT %.2f but claim %s says BDT %.2f."
                        % (label, claimed, claim.claim_no, target)
                    )
            if target <= 0.005:
                raise UserError(
                    "%s refused: claim %s carries no approved amount." % (label, claim.claim_no)
                )
        else:
            raise UserError(
                "%s refused: claim %s is %s, not an approved state."
                % (label, claim.claim_no, claim.state)
            )

        invoices = self._claim_invoices(claim)
        delta = round(target - self._booked(invoices), 2)
        if abs(delta) <= 0.005:
            if not invoices:
                return {
                    "model": claim._name,
                    "id": claim.id,
                    "created": False,
                    "skipped": "rejected",
                }
            return {"model": invoices._name, "id": invoices[:1].id, "created": False}
        if delta < 0:
            notes = self._reduce(claim, invoices, -delta, label)
            invoices = self._claim_invoices(claim)
            delta = round(target - self._booked(invoices), 2)
            if delta <= 0.005:
                return {
                    "model": "fix.credit.note",
                    "ids": notes.ids,
                    "created": bool(notes),
                    "reduced": True,
                }
        # an increase (or the first decision): a draft for the difference
        Invoice = self.env["fix.ar.invoice"].sudo()
        on_claim = Invoice.search_count(
            [("source_model", "=", claim._name), ("source_id", "=", claim.id)]
        )
        if not on_claim:
            source_model, source_id = claim._name, claim.id
        else:
            decision = claim.decision_ids.sorted("id")[-1:]
            if not decision or Invoice.search_count(
                [("source_model", "=", DECISION_MODEL), ("source_id", "=", decision.id)]
            ):
                raise UserError(
                    "%s refused: claim %s needs a further BDT %.2f but its latest decision "
                    "already raised an invoice." % (label, claim.claim_no, delta)
                )
            source_model, source_id = DECISION_MODEL, decision.id
        invoice = self._raise_invoice(claim, delta, source_model, source_id, label)
        return {"model": invoice._name, "id": invoice.id, "created": True}
