# cd_storefront_finance — a storefront return in the books.
#
# E2E3 flow 4: the returned item never came back into stock, and the refund
# was completed by a native out_refund (account.move) that debited revenue
# never credited, wrote a 6.7 with no 6.3 and sat outside the M20 sub-ledger.
# Now, for both return models (they share fix.storefront.refund.mixin):
#   restock  when the item is received and inspected it comes back into the
#            M15 location it left, at the cost it left with, with its
#            valuation suspense row: resalable (grade A) into unrestricted
#            stock, anything else into quarantine (BRU-INV-08);
#   credit   when the refund is approved (the M63 DOFA decision), an M20
#            credit note for the approved amount is raised against the
#            order's invoice and submitted into M20's own ladder. Finance
#            approves and issues it: the 6.7 against the order's 6.3, the GL
#            mirror (Dr revenue + VAT / Cr AR) and the money back as an M50
#            instruction (BRU-ARB-11). Issuing it completes the return.
# A native account.move is no longer a storefront refund.
from __future__ import annotations

import logging
import re

from odoo import api, fields, models
from odoo.addons.cd_storefront.models.fix_storefront_refund import GROUP_PAYMENT
from odoo.exceptions import UserError
from odoo.tools import SQL

from libs.py.fix_events import publish

from .fix_engine_ext import SOURCE
from .fix_storefront_books import RETRY_GROUPS, _message, request_credit_note

_logger = logging.getLogger(__name__)

RESTOCK_STATES = [
    ("none", "Not Evaluated"),
    ("not_required", "Nothing to Restock"),
    ("pending", "Pending"),
    ("restocked", "Restocked"),
]
BOOKS_STATES = [("none", "Nothing to Post"), ("pending", "Pending Posting"), ("posted", "Posted")]
LEG_LABELS = {"restock": "Restock", "credit": "M20 credit note"}
# reasons that say the item is faulty: it is quarantined as defective
FAULT_REASONS = ("defective", "doa", "warranty", "not_as_described")
RETURN_POSTING_FIELDS = {
    "ar_credit_note_id",
    "restock_state",
    "books_state",
    "books_note",
    "books_attempted_at",
}


class FixStorefrontRefundBooks(models.AbstractModel):
    _inherit = "fix.storefront.refund.mixin"

    ar_credit_note_id = fields.Many2one(
        "fix.credit.note",
        string="Refund Credit Note (M20)",
        readonly=True,
        copy=False,
        index=True,
        ondelete="restrict",
        help="The M20 credit note against the order's invoice that pays this refund: its "
        "Mushak 6.7, the GL mirror and the refund instruction.",
    )
    ar_credit_note_state = fields.Selection(
        related="ar_credit_note_id.state", string="Credit Note State"
    )
    restock_state = fields.Selection(
        RESTOCK_STATES, string="Restock", default="none", required=True, readonly=True, copy=False
    )
    books_state = fields.Selection(
        BOOKS_STATES, string="Books", default="none", required=True, readonly=True, copy=False
    )
    books_note = fields.Text(string="Posting Note", readonly=True, copy=False)
    books_attempted_at = fields.Datetime(string="Last Posting Run", readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | RETURN_POSTING_FIELDS

    # ------------------------------------------------------------ transitions
    def action_receive_and_inspect(self, condition=None):
        result = super().action_receive_and_inspect(condition=condition)
        self._sfb_post()
        return result

    def action_approve_refund(self):
        result = super().action_approve_refund()
        self._sfb_post()
        return result

    def action_retry_posting(self):
        if not (self.env.su or any(self.env.user.has_group(g) for g in RETRY_GROUPS)):
            raise UserError("Only storefront or finance staff may retry a return's posting.")
        self._sfb_post()
        return True

    @api.model
    def _sfb_cron_returns(self, limit=200):
        rows = self.sudo().search(
            [
                "|",
                "|",
                ("books_state", "=", "pending"),
                "&",
                ("inspected_at", "!=", False),
                ("restock_state", "=", "none"),
                "&",
                ("state", "=", "refund_approved"),
                ("ar_credit_note_id", "=", False),
            ],
            order="books_attempted_at asc, id asc",
            limit=limit,
        )
        rows._sfb_post()
        return len(rows)

    # ------------------------------------------------------------ the M20 credit note
    def _sfb_find_ar_credit_note(self, credit_note):
        Note = self.env["fix.credit.note"].sudo()
        if isinstance(credit_note, models.BaseModel):
            return credit_note.sudo().exists() if credit_note._name == Note._name else Note
        if isinstance(credit_note, int):
            return Note.browse(credit_note).exists()
        found = re.fullmatch(r"(?:CN/)?(\d+)", str(credit_note or "").strip())
        return Note.browse(int(found.group(1))).exists() if found else Note

    def action_record_credit_note(self, credit_note=None):
        """A storefront refund is completed by the issued M20 credit note
        against its order's invoice - never a native account.move (E3-08).
        Issuing that note completes the return by itself; finance may also
        record it here."""
        self._sf_require([GROUP_PAYMENT], "Recording a refund's credit note")
        note = self._sfb_find_ar_credit_note(credit_note)
        if not note:
            raise UserError(
                "A storefront refund is completed by the M20 credit note against the order's "
                "invoice (its Mushak 6.7), raised when the refund was approved; %r is not one. "
                "A native credit note (account.move) is not a storefront refund." % (credit_note,)
            )
        for rec in self:
            rec._sfb_record_m20_credit(note)
        return True

    def _sfb_record_m20_credit(self, note):
        self.ensure_one()
        rec = self.sudo()
        if rec.state != "refund_approved":
            raise UserError(
                "%s: only an approved refund is completed by its credit note." % rec._sf_label()
            )
        rec._dofa_assert_approved("The refund")
        invoice = rec.order_id.ar_invoice_id
        if rec.ar_credit_note_id and rec.ar_credit_note_id != note:
            raise UserError(
                "%s is paid by M20 credit note #%s, not #%s."
                % (rec._sf_label(), rec.ar_credit_note_id.id, note.id)
            )
        if note.state != "issued":
            raise UserError(
                "M20 credit note #%s is %s: it completes the refund once finance issues it."
                % (note.id, dict(note._fields["state"].selection)[note.state])
            )
        if not invoice or note.invoice_id != invoice:
            raise UserError(
                "M20 credit note #%s credits %s, not the invoice of order %s."
                % (note.id, note.invoice_id.name or "no invoice", rec.order_id.name)
            )
        if abs((note.amount or 0.0) - (rec.refund_amount or 0.0)) > 0.005:
            raise UserError(
                "M20 credit note #%s is for BDT %.2f; the approved refund is BDT %.2f."
                % (note.id, note.amount, rec.refund_amount)
            )
        for model in ("fix.storefront.return", "fix.storefront.rma"):
            used = self.env[model].sudo().search([("ar_credit_note_id", "=", note.id)])
            if model == rec._name:
                used -= rec
            if used:
                raise UserError(
                    "M20 credit note #%s already pays %s." % (note.id, used[0].display_name)
                )
        ref = "CN/%s" % note.id
        if note.mushak_note_id:
            ref += " (Mushak 6.7 %s)" % note.mushak_note_id.mushak_no
        rec._guarded().write(
            {
                "ar_credit_note_id": note.id,
                "credit_note_ref": ref,
                "refunded_at": fields.Datetime.now(),
                "refunded_by_id": self.env.uid,
                "state": "refunded",
            }
        )
        publish(
            rec.env,
            "storefront.refund_processed",
            rec._name,
            rec.id,
            {
                "rma_number": rec.name,
                "customer": rec.customer_id.name,
                "refund_amount": float(rec.refund_amount or 0.0),
                "condition": rec.inspected_condition,
                "credit_note_ref": ref,
            },
        )

    # ---------------------------------------------------------------- engine
    def _sfb_post(self):
        for rec in self:
            if rec.order_id:
                rec._sfb_post_one()

    def _sfb_todo(self):
        self.ensure_one()
        legs = []
        if self.inspected_at and self.restock_state in ("none", "pending"):
            legs.append("restock")
        if (
            self.state == "refund_approved"
            and not self.ar_credit_note_id
            and (self.refund_amount or 0.0) > 0.005
        ):
            legs.append("credit")
        return legs

    def _sfb_post_one(self):
        self.ensure_one()
        rec = self.sudo().with_company(self.company_id)
        self.env.flush_all()
        self.env.cr.execute(
            SQL("SELECT id FROM %s WHERE id = %s FOR UPDATE", SQL.identifier(rec._table), rec.id)
        )
        rec.invalidate_recordset()
        problems = []
        for leg in rec._sfb_todo():
            try:
                with self.env.cr.savepoint():
                    getattr(rec, "_sfb_leg_%s" % leg)()
            except Exception as exc:
                if not isinstance(exc, UserError | ValueError):
                    _logger.exception("storefront return %s: %s step failed", rec.name, leg)
                problems.append("%s: %s" % (LEG_LABELS[leg], _message(exc)))
                self.env.invalidate_all()
                if leg == "restock" and rec.restock_state == "none":
                    rec._guarded().write({"restock_state": "pending"})
        rec._sfb_record(problems)

    def _sfb_record(self, problems):
        self.ensure_one()
        if self._sfb_todo():
            new = "pending"
        elif self.ar_credit_note_id or self.restock_state == "restocked":
            new = "posted"
        else:
            new = "none"
        note = "\n".join(problems) or False
        changed = (new, note or False) != (self.books_state, self.books_note or False)
        self._guarded().write(
            {"books_state": new, "books_note": note, "books_attempted_at": fields.Datetime.now()}
        )
        if changed and hasattr(self, "message_post"):
            label = dict(BOOKS_STATES)[new]
            self.message_post(
                body="Books: %s." % label if not note else "Books: %s - %s" % (label, note)
            )

    # ---------------------------------------------------------------- steps
    def _sfb_leg_restock(self):
        """The order's goods come back to the location they left, at the cost
        they left with. Resalable (grade A) into unrestricted stock; anything
        else into quarantine, where the M15 scrap / release decision is
        taken. The whole order comes back: a return names no lines."""
        order = self.order_id.sudo()
        # returned before they ever left the ledger: nothing to bring back
        # (and what was reserved for them is free again - M38-F6)
        unissued = order.line_ids.filtered(lambda ln: ln.stock_state in ("none", "pending"))
        unissued._sfb_release_reservation()
        unissued.write({"stock_state": "cancelled"})
        issued = order.line_ids.filtered(lambda ln: ln.stock_state == "issued")
        if not issued:
            self._guarded().write({"restock_state": "not_required"})
            return
        resalable = self.inspected_condition == "grade_a"
        status = "unrestricted" if resalable else "quarantine"
        Onhand = self.env["fix.stock.onhand"]
        for line in issued:
            part, location = line.stock_part_id, line.stock_location_id
            cls = line.stock_ownership_class or "owned"
            cost, qty, lot = line.stock_unit_cost, line.quantity, line.stock_lot_id
            Onhand._apply(part, location, cls, qty, cost, status=status)
            if lot:
                lot._fix_move("in_stock" if resalable else "quarantined", location, 1.0)
            if not resalable:
                self.env["fix.stock.quarantine"].sudo()._guarded().with_context(
                    fix_quarantine_in_place=True
                ).create(
                    {
                        "part_id": part.id,
                        "location_id": location.id,
                        "company_id": order.company_id.id,
                        "ownership_class": cls,
                        "lot_id": lot.id or False,
                        "qty": qty,
                        "reason": "defective"
                        if self.reason in FAULT_REASONS
                        else "customer_return",
                        "notes": "Returned on %s of storefront order %s (inspected %s)"
                        % (self.name, order.name, self.inspected_condition),
                        "source_ref": self.name,
                    }
                )
            self.env["fix.inventory.valuation.suspense"]._fix_post(
                SOURCE,
                part,
                qty,
                cost,
                "%s/%s" % (order.name, self.name),
                location=location,
                ownership=cls,
            )
            line.write({"stock_state": "returned"})
        self._guarded().write({"restock_state": "restocked"})

    def _sfb_leg_credit(self):
        """The approved refund as an M20 credit note against the order's
        invoice, submitted into M20's ladder."""
        order = self.order_id.sudo()
        if not order.ar_invoice_id:
            order._sfb_post()
            order.invalidate_recordset()
        invoice = order.ar_invoice_id
        if not invoice or invoice.state not in ("issued", "paid"):
            raise UserError(
                "Order %s has no issued M20 invoice to credit yet%s: post the order first."
                % (order.name, " (%s)" % order.posting_note if order.posting_note else "")
            )
        if invoice.customer_id.commercial_partner_id != self.customer_id.commercial_partner_id:
            raise UserError(
                "Invoice %s is to %s, the return is from %s."
                % (invoice.name, invoice.customer_id.name, self.customer_id.name)
            )
        # A04 ERP audit M38-F3: one refund per return. A treasury instruction
        # raised for it outside this credit note (the former relay path) means
        # the money is already on its way: refuse a second payment.
        if "fix.payment.execution" in self.env:
            other = (
                self.env["fix.payment.execution"]
                .sudo()
                .search(
                    [
                        ("source_model", "=", self._name),
                        ("source_id", "=", self.id),
                        ("state", "not in", ("cancelled", "rejected", "failed")),
                    ],
                    limit=1,
                )
            )
            if other:
                raise UserError(
                    "%s is already being refunded by treasury instruction %s: cancel it before "
                    "the credit note pays the customer again (one refund per return)."
                    % (self.name, other.name)
                )
        note = request_credit_note(
            self,
            invoice,
            self.refund_amount,
            "return",
            "Raised by the storefront bridge: refund %s of BDT %.2f on order %s, approved by "
            "%s; credit against invoice %s, for finance to approve and issue."
            % (
                self.name,
                self.refund_amount,
                order.name,
                self.dofa_approved_by.name or self.env.user.name,
                invoice.name,
            ),
        )
        self._guarded().write({"ar_credit_note_id": note.id})


class FixCreditNoteStorefront(models.Model):
    """Issuing the credit note of a storefront refund completes the refund."""

    _inherit = "fix.credit.note"

    # The rail a storefront refund goes back on: the one the order was paid
    # over (the same map cd_cash_position's refund consumer used before the
    # bridge invoiced every paid order). A bKash customer is refunded to the
    # wallet, never by bank transfer to an account they may not have.
    _SF_RAIL_METHOD = {
        "bkash": "mobile_fs",
        "nagad": "mobile_fs",
        "rocket": "mobile_fs",
        "upay": "mobile_fs",
        "mobile_wallet": "mobile_fs",
    }

    _SF_SOURCES = ("fix.storefront.return", "fix.storefront.rma", "fix.storefront.order")

    @api.model_create_multi
    def create(self, vals_list):
        """A04 ERP audit M38-F3: one live credit note per storefront return
        (or cancelled order). Two paths each raised one for the same 1,150
        return; a second is refused whoever raises it."""
        if "source_model" in self._fields:
            for vals in vals_list:
                model, sid = vals.get("source_model"), vals.get("source_id")
                if model in self._SF_SOURCES and sid:
                    dup = self.sudo().search(
                        [
                            ("source_model", "=", model),
                            ("source_id", "=", sid),
                            ("state", "!=", "rejected"),
                        ],
                        limit=1,
                    )
                    if dup:
                        raise UserError(
                            "%s #%s is already credited by M20 credit note #%s: one refund per "
                            "storefront return." % (model, sid, dup.id)
                        )
        return super().create(vals_list)

    def _fix_refund_method(self):
        invoice = self.invoice_id
        if invoice.source_model == "fix.storefront.order" and invoice.source_id:
            order = self.env["fix.storefront.order"].sudo().browse(invoice.source_id).exists()
            if order:
                return self._SF_RAIL_METHOD.get(order.payment_rail, "bank_transfer")
        return super()._fix_refund_method()

    def action_issue(self):
        result = super().action_issue()
        issued = self.filtered(lambda n: n.state == "issued")
        if not issued:
            return result
        for model in ("fix.storefront.return", "fix.storefront.rma"):
            refunds = (
                self.env[model]
                .sudo()
                .search(
                    [("ar_credit_note_id", "in", issued.ids), ("state", "=", "refund_approved")]
                )
            )
            for refund in refunds:
                try:
                    with self.env.cr.savepoint():
                        refund._sfb_record_m20_credit(refund.ar_credit_note_id)
                except UserError as exc:
                    refund.message_post(
                        body="Credit note #%s was issued but the refund was not completed: %s"
                        % (refund.ar_credit_note_id.id, _message(exc))
                    )
        return result
