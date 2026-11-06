# cd_cash_position — a bounced customer cheque re-opens the AR it paid
# (A08, B1 -> B4 hand-off: cheque.bounced).
#
# Lives HERE, not in cd_billing_engine: the extension adds a Many2one to
# fix.cheque (this module's register), while fix.ar.receipt arrives through
# this module's storefront -> billing dependency chain. Declaring the edge
# the other way (billing depends on cash) closed the cycle
# billing -> cash -> storefront -> billing and Odoo's loop detector skipped
# every module in it.
#
# Treasury (M50, fix.cheque.action_bounce) records the bank's return and, for
# a cheque that had CLEARED, reverses the bank side itself: Dr returned
# cheques receivable / Cr bank. Until now AR never heard of it: the invoice
# the cheque paid stayed "paid" and the customer's AR showed nothing owed.
#
# This R8 consumer of cheque.bounced re-opens it, exactly once:
#   * the M20 receipt of the cheque (by its number / the cheque's source
#     reference, same customer, cheque tender) is found; its allocations are
#     removed so the invoices it paid are issued again with their residual;
#   * the AR posting goes through the M19 API (source "receipt"):
#       cleared cheque   Dr AR (customer) / Cr returned cheques receivable —
#                        the account B1 debited (system parameter
#                        cd_cash_position.account_code.cheque_returned,
#                        refused when unset); the bank is NOT credited again;
#       never cleared    Dr AR / Cr the account the receipt was cleared into
#                        (the money never arrived; B1 posted nothing);
#   * the receipt is marked reversed, naming the cheque and the entry, so a
#     replay returns what exists (idempotent per cheque).
# The payload is a claim: the cheque is re-read and must be a bounced
# RECEIVED cheque; a forged event is refused (the relay records the failure).
from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError

PARAM_CHEQUE_RETURNED = "cd_cash_position.account_code.cheque_returned"


class FixArReceiptChequeBounce(models.Model):
    _inherit = "fix.ar.receipt"

    bounced_cheque_id = fields.Many2one(
        "fix.cheque", string="Returned Cheque", readonly=True, copy=False, index=True
    )
    bounce_move_id = fields.Many2one(
        "account.move", string="Cheque Return AR Entry", readonly=True, copy=False
    )

    _bounced_cheque_unique = models.Constraint(
        "UNIQUE (bounced_cheque_id)", "A returned cheque re-opens one receipt"
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"bounced_cheque_id", "bounce_move_id"}

    @api.model
    def _fix_cheque_receipt(self, cheque):
        """The confirmed M20 cheque receipt the returned cheque settled."""
        Receipt = self.sudo()
        base = [
            ("company_id", "=", cheque.company_id.id),
            ("state", "=", "confirmed"),
            ("method", "=", "cheque"),
            ("customer_id", "child_of", cheque.partner_id.commercial_partner_id.id),
        ]
        keys = [k for k in {(cheque.cheque_no or "").strip(), (cheque.source_ref or "").strip()} if k]
        found = Receipt.browse()
        if keys:
            found = Receipt.search(
                [*base, "|", ("name", "in", keys), ("reference", "in", keys)]
            )
        if not found and cheque.source_ref:
            # the source reference names the invoice the cheque paid
            invoices = self.env["fix.ar.invoice"].sudo().search(
                [("company_id", "=", cheque.company_id.id), ("name", "=", cheque.source_ref)]
            )
            found = invoices.allocation_ids.receipt_id.filtered_domain(base)
        found = found.filtered(lambda r: abs(r.amount - cheque.amount) <= 0.005)
        if len(found) != 1:
            raise UserError(
                "Cheque-return hand-back refused: %s confirmed cheque receipt(s) of %.2f match "
                "cheque %s (%s); finance re-opens the invoice by hand."
                % (len(found), cheque.amount, cheque.cheque_no, cheque.source_ref or "no reference")
            )
        return found

    @api.model
    def consume_cheque_bounced(self, event: dict) -> dict:
        """R8 consumer of cheque.bounced (B1 -> B4)."""
        if not self.env.su:
            raise AccessError("The cheque-return consumer runs only from the event relay.")
        label = "Cheque-return hand-back"
        if (event.get("aggregate") or "fix.cheque") != "fix.cheque":
            raise UserError("%s refused: the event is not a cheque's." % label)
        try:
            cheque_id = int(event.get("aggregate_id") or 0)
        except (TypeError, ValueError):
            cheque_id = 0
        cheque = self.env["fix.cheque"].sudo().browse(cheque_id).exists() if cheque_id else None
        if not cheque:
            raise UserError("%s refused: there is no cheque #%s." % (label, cheque_id))
        if cheque.direction != "received":
            # an ISSUED cheque is treasury's / the paying module's (M50 re-queues it)
            return {"skipped": "issued cheque"}
        existing = self.sudo().search([("bounced_cheque_id", "=", cheque.id)], limit=1)
        if existing:
            return {"model": existing._name, "id": existing.id, "created": False}
        if cheque.state != "bounced":
            raise UserError(
                "%s refused: cheque %s is %s, not returned." % (label, cheque.cheque_no, cheque.state)
            )
        payload = event.get("payload") or {}
        if payload.get("amount") is not None and abs(float(payload["amount"]) - cheque.amount) > 0.005:
            raise UserError("%s refused: the event's amount is not the cheque's." % label)
        receipt = self._fix_cheque_receipt(cheque)
        company = receipt.company_id
        from odoo.addons.cd_billing_engine.models.fix_ar_engine import (
            _ar_account,
            _post_ar_move,
        )

        ar = _ar_account(self.env, company, "ar")
        if not ar:
            raise UserError("%s refused: no AR control account in %s." % (label, company.name))
        if cheque.bounce_move_id:
            # B1 reversed the bank (Dr returned cheques / Cr bank): AR takes
            # the returned-cheques receivable back to the customer's account
            code = self.env["ir.config_parameter"].sudo().get_param(PARAM_CHEQUE_RETURNED)
            credit = (
                self.env["account.account"]
                .sudo()
                .with_company(company)
                .search([("code", "=", code), ("company_ids", "in", company.id)], limit=1)
                if code
                else self.env["account.account"]
            )
            if not credit:
                raise UserError(
                    "%s refused: no returned-cheques account in %s — set the system parameter "
                    "%s (nothing is posted to a guessed account)."
                    % (label, company.name, PARAM_CHEQUE_RETURNED)
                )
        else:
            # never cleared: the money never arrived and B1 posted nothing
            credit = receipt.account_id
            if not credit:
                raise UserError("%s refused: receipt %s records no cleared-into account." % (
                    label, receipt.name))
        invoices = receipt.allocation_ids.mapped("invoice_id")
        dims = self.env["fix.ar.invoice"]._ar_posting_dims(receipt.branch_id.id)
        move, note = _post_ar_move(
            self.env,
            company,
            fields.Date.context_today(self),
            "CHEQUE RETURNED %s — RCT %s (%s)" % (cheque.cheque_no, receipt.name, cheque.bounce_reason or ""),
            [
                (ar.id, "AR re-opened: cheque %s returned" % cheque.cheque_no, receipt.amount, 0.0,
                 receipt.customer_id.id),
                (credit.id, "Returned cheque %s" % cheque.cheque_no, 0.0, receipt.amount,
                 receipt.customer_id.id),
            ],
            {0: dims, 1: dims},
            source="receipt",
        )
        if not move:
            raise UserError("%s refused: %s" % (label, note or "the M19 posting failed"))
        # the invoices the cheque paid are open again (their allocations are
        # removed; the receipt keeps its history in the chatter)
        for invoice in invoices.filtered(lambda i: i.state == "paid"):
            invoice._guarded().write({"state": "issued", "paid_date": False})
        receipt.allocation_ids.sudo().unlink()
        receipt.sudo()._guarded().write(
            {
                "state": "reversed",
                "reversal_reason": ("Cheque %s returned: %s" % (cheque.cheque_no, cheque.bounce_reason or ""))[:500],
                "bounced_cheque_id": cheque.id,
                "bounce_move_id": move.id,
            }
        )
        for invoice in invoices:
            invoice.sudo().message_post(
                body="Re-opened: cheque %s (receipt %s) was returned by the bank (%s); %.2f is "
                "owed again." % (cheque.cheque_no, receipt.name, cheque.bounce_reason or "", receipt.amount)
            )
        return {"model": receipt._name, "id": receipt.id, "created": True, "move_id": move.id,
                "invoices": invoices.ids}
