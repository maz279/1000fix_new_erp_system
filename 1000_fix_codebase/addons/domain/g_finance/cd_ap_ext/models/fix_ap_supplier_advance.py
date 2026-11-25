# fix_ap_supplier_advance — paying a local supplier's advance and taking it
# back on its bill (user request, 13 Nov 2026).
#
# M16 records a supplier advance against an approved proforma and has it
# approved by a second person (cd_requisition fix_purchase_proforma.py), but
# nothing paid it and no bill ever took it back. Now:
#   - Request Payment on an APPROVED advance (an Accountant) raises the same
#     payment.requested event a bill's Request Payment does; treasury (M50)
#     re-reads the payee, bank and amount from the advance and executes it
#     under its own authorisation; when the bank confirms, the advance is
#     paid and posts Dr advances to suppliers / Cr the clearing treasury
#     debited (a returned payment reverses it);
#   - when a bill of the same purchase order posts, the order's paid advances
#     not yet taken back reduce what the bill pays: the bill credits advances
#     to suppliers instead of trade payables for that part, oldest advance
#     first, never more than the bill's own payable; what is left stays for
#     the order's next bill. Each take-back is recorded per advance and bill.
# The advances account is a role with no default (cd_ap_ext.account_code.
# supplier_advance): nothing posts until finance names it.
from odoo import api, fields, models
from odoo.exceptions import UserError

from libs.py.fix_events import publish  # FF-28

from .ap_gl import ap_account
from .fix_ap_controls import require_finance

SOURCE = "fix.purchase.advance"


def _advance_bdt_today(adv):
    """A06 D5: what paying `adv` costs in BDT today (a BDT advance: itself).
    The payment entry debits the advance account with it, and the bill takes
    the advance back at that BDT (_fix_advance_bdt)."""
    from odoo.addons.cd_requisition.models.fix_requisition import bdt_rate

    if adv.currency_id == adv.company_id.currency_id:
        return adv.amount
    return round(adv.amount * bdt_rate(adv.env, adv.currency_id, adv.company_id), 2)


def _q(value):
    return round(value or 0.0, 2)


class FixPurchaseAdvancePayment(models.Model):
    _inherit = "fix.purchase.advance"

    state = fields.Selection(
        selection_add=[
            ("payment_requested", "Payment Requested"),
            ("paid", "Paid"),
        ],
        ondelete={"payment_requested": "set default", "paid": "set default"},
    )
    payment_move_id = fields.Many2one(
        "account.move", string="Payment Entry", readonly=True, copy=False
    )
    payment_failure = fields.Char(readonly=True, copy=False)
    application_ids = fields.One2many(
        "fix.purchase.advance.application", "advance_id", string="Taken Back on Bills"
    )
    applied_amount = fields.Monetary(
        string="Taken Back", currency_field="currency_id", compute="_compute_applied"
    )
    remaining_amount = fields.Monetary(
        string="Still to Take Back", currency_field="currency_id", compute="_compute_applied"
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"payment_move_id", "payment_failure"}

    @api.depends("amount", "application_ids.amount")
    def _compute_applied(self):
        for adv in self:
            adv.applied_amount = _q(sum(adv.application_ids.mapped("amount")))
            adv.remaining_amount = _q((adv.amount or 0.0) - adv.applied_amount)

    def action_cancel(self):
        for adv in self:
            if adv.state in ("payment_requested", "paid"):
                raise UserError(
                    "Advance %s is %s: treasury holds or has paid it." % (adv.name, adv.state)
                )
        return super().action_cancel()

    def action_request_payment(self):
        """Ask treasury to pay an approved advance (payment.requested)."""
        require_finance(self.env, "Requesting a supplier advance payment")
        for adv in self:
            if adv.state != "approved":
                raise UserError(
                    "Only an approved advance is paid (%s is %s)." % (adv.name, adv.state)
                )
            po = adv.purchase_order_id.sudo()
            if po.state in ("cancelled", "superseded", "closed"):
                raise UserError(
                    "Purchase order %s is %s: its advance is not paid." % (po.name, po.state)
                )
            # the accountant's role is checked above; the advance is M16's
            # record, written for them
            adv.sudo()._guarded().write({"state": "payment_requested", "payment_failure": False})
            publish(
                self.env,
                "payment.requested",
                SOURCE,
                adv.id,
                {
                    "vendor_id": adv.vendor_id.id,
                    # A06 D5: treasury pays BDT, a foreign advance at the day's rate
                    "amount": _advance_bdt_today(adv),
                    "currency": adv.company_id.currency_id.name,
                    "advance_currency": adv.currency_id.name,
                    "advance_amount_currency": adv.amount,
                    "invoice_ref": adv.name,
                    "operating_unit_id": adv.operating_unit_id.id,
                    "company_id": adv.company_id.id,
                    "payee_partner_id": adv.vendor_id.commercial_partner_id.id,
                    "approved_by": adv.decided_by_id.id,
                },
            )
        return True


class FixPurchaseAdvanceApplication(models.Model):
    """One take-back of a supplier advance on one bill."""

    _name = "fix.purchase.advance.application"
    _description = "Supplier Advance Taken Back on a Bill"
    _order = "id"

    advance_id = fields.Many2one(
        "fix.purchase.advance", required=True, ondelete="restrict", index=True
    )
    bill_id = fields.Many2one("fix.vendor.invoice", required=True, ondelete="restrict", index=True)
    company_id = fields.Many2one(related="advance_id.company_id", store=True, index=True)
    operating_unit_id = fields.Many2one(
        related="advance_id.operating_unit_id", store=True, index=True
    )
    currency_id = fields.Many2one(related="advance_id.currency_id")
    amount = fields.Monetary(currency_field="currency_id", required=True)

    _amount_positive = models.Constraint("CHECK (amount > 0)", "A take-back must be positive")


class FixVendorInvoiceSupplierAdvance(models.Model):
    _inherit = "fix.vendor.invoice"

    advance_application_ids = fields.One2many(
        "fix.purchase.advance.application", "bill_id", string="Supplier Advances Taken Back"
    )

    def _apply_supplier_advances(self):
        """At posting: take the PO's paid, not yet taken back advances off what
        this bill pays, oldest first, never more than its own payable."""
        self.ensure_one()
        po = self.requisition_id
        if not po or self.advance_applied:
            return
        advances = (
            self.env["fix.purchase.advance"]
            .sudo()
            .search(
                [("purchase_order_id", "=", po.id), ("state", "=", "paid")],
                order="decided_on, id",
            )
            .filtered(lambda a: a.remaining_amount > 0.005)
        )
        if not advances:
            return
        if advances.mapped("currency_id") != self.currency_id:
            raise UserError(
                "Bill %s is in %s but the advances of purchase order %s are in %s: they cannot "
                "be taken back on it."
                % (
                    self.invoice_ref,
                    self.currency_id.name,
                    po.name,
                    ", ".join(advances.mapped("currency_id.name")),
                )
            )
        room = _q(self.total_payable)
        take = []
        for adv in advances:
            if room <= 0.005:
                break
            amount = _q(min(adv.remaining_amount, room))
            take.append((0, 0, {"advance_id": adv.id, "amount": amount}))
            room = _q(room - amount)
        if not take:
            return
        self.sudo().write({"advance_application_ids": take})
        total = _q(sum(self.advance_application_ids.mapped("amount")))
        self._guarded().write({"advance_applied": total})

    def _fix_advance_bdt(self):
        """A06 D5: an M16 advance is taken back at the BDT it was paid at:
        the debit its payment posted on the advance account, pro rata; a BDT
        advance at its own figure. An unpaid-in-BDT foreign advance (no
        payment entry) is refused rather than guessed."""
        total = super()._fix_advance_bdt()
        account = None
        for app in self.advance_application_ids.sudo():
            adv = app.advance_id
            if adv.currency_id == self.company_id.currency_id:
                total += app.amount
                continue
            account = account or ap_account(self.env, self.company_id, "supplier_advance")
            paid = sum(
                adv.payment_move_id.line_ids.filtered(
                    lambda ml, a=account: ml.account_id == a
                ).mapped("debit")
            )
            if not paid or not adv.amount:
                raise UserError(
                    "Advance %s is in %s and has no payment entry on the advance account: the BDT "
                    "it was paid at is unknown, so bill %s cannot take it back."
                    % (adv.display_name, adv.currency_id.name, self.invoice_ref)
                )
            total += app.amount * paid / adv.amount
        return total


class FixPaymentExecutionSupplierAdvance(models.Model):
    _inherit = "fix.payment.execution"

    def _payment_resolvers(self):
        resolvers = super()._payment_resolvers()
        resolvers[SOURCE] = self._resolve_supplier_advance
        return resolvers

    def _resolve_supplier_advance(self, adv, payload):
        if adv.state != "payment_requested":
            raise UserError(
                "Supplier advance %s is %s, not awaiting payment." % (adv.display_name, adv.state)
            )
        partner = adv.vendor_id.commercial_partner_id
        banks = partner.bank_ids
        return {
            "source_model": SOURCE,
            "source_id": adv.id,
            "partner": partner,
            "bank": banks if len(banks) == 1 else self.env["res.partner.bank"],
            "amount": _advance_bdt_today(adv),
            "currency": adv.company_id.currency_id,
            "approver": adv.decided_by_id,
            "ref": payload.get("invoice_ref") or adv.name,
            "options": {
                "company_id": adv.company_id.id,
                "operating_unit_id": adv.operating_unit_id.id,
            },
        }
