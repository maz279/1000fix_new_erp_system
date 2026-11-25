# M34 — an approved concession produces its money document (A03 audit M34-9).
#
# The concession was approved under DOFA (routed through M63) and then went
# nowhere: no credit note, voucher or refund referenced a complaint, so the
# "Compensation & Goodwill" tab listed credit notes unrelated to any
# complaint. The remedy is now issued as the document its type names:
#
#   waiver, refund -> fix.credit.note (M20, reason 'goodwill') against the AR
#                     invoice of the complaint's service order, submitted into
#                     M20's own authority rule; Finance issues and posts it;
#   discount       -> fix.loyalty.voucher (M10), fixed BDT, activated.
#
# WHEN: at closure, not at approval. The approval authorises an offer; the
# customer may still reject the response, and a rejected or renegotiated
# remedy must not leave a credit behind. Closure needs the customer's
# acceptance, so the document follows the remedy that was actually agreed.
#
# Idempotent by amount: a complaint is documented up to its approved
# concession, never beyond. A reopened complaint whose concession is raised
# (and re-approved) gets a document for the difference only.
#
# Where no document can be made (no service order, no invoice, a refund larger
# than the invoice), complaint.concession_settled carries the amount and the
# reason, and the complaint records it, so Finance has a hand-off rather than
# a silent gap.
from odoo import fields, models

from libs.py.fix_events import publish  # FF-28

PARAM_VOUCHER_VALID_DAYS = "cd_cx_feedback.concession_voucher_valid_days"
DEFAULT_VOUCHER_VALID_DAYS = 90


class FixCreditNoteComplaint(models.Model):
    _inherit = "fix.credit.note"

    complaint_id = fields.Many2one(
        "fix.complaint",
        string="Complaint",
        readonly=True,
        copy=False,
        index=True,
        ondelete="set null",
        help="The M34 complaint whose approved concession this credit settles.",
    )


class FixLoyaltyVoucherComplaint(models.Model):
    _inherit = "fix.loyalty.voucher"

    complaint_id = fields.Many2one(
        "fix.complaint",
        string="Complaint",
        readonly=True,
        copy=False,
        index=True,
        ondelete="set null",
        help="The M34 complaint whose approved concession this voucher settles.",
    )


class FixComplaintConcession(models.Model):
    _inherit = "fix.complaint"

    # Computed lookups, not owned lines: the credit note belongs to M20 and the
    # voucher to M10; the complaint only points at what settled it.
    concession_credit_note_ids = fields.One2many(
        "fix.credit.note",
        compute="_compute_concession_documents",
        string="Concession Credit Notes",
    )
    concession_voucher_ids = fields.One2many(
        "fix.loyalty.voucher",
        compute="_compute_concession_documents",
        string="Concession Vouchers",
    )
    concession_settled_amount = fields.Monetary(
        string="Concession Documented (BDT)",
        currency_field="currency_id",
        compute="_compute_concession_documents",
    )
    concession_settlement_note = fields.Text(
        string="Concession Settlement",
        readonly=True,
        copy=False,
        help="What document settled the concession, or why none could be made.",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"concession_settlement_note"}

    def _concession_documents(self):
        """(credit notes, vouchers) raised for this complaint, sudo."""
        self.ensure_one()
        if not isinstance(self.id, int):
            return self.env["fix.credit.note"], self.env["fix.loyalty.voucher"]
        domain = [("complaint_id", "=", self.id)]
        return (
            self.env["fix.credit.note"].sudo().search(domain),
            self.env["fix.loyalty.voucher"].sudo().search(domain),
        )

    def _compute_concession_documents(self):
        for rec in self:
            notes, vouchers = rec._concession_documents()
            rec.concession_credit_note_ids = notes
            rec.concession_voucher_ids = vouchers
            rec.concession_settled_amount = rec._concession_documented_amount()

    def _concession_documented_amount(self) -> float:
        self.ensure_one()
        notes, vouchers = self._concession_documents()
        notes = notes.filtered(lambda n: n.state != "rejected")
        vouchers = vouchers.filtered(
            lambda v: v.state != "cancelled" and v.discount_type == "fixed_bdt"
        )
        return sum(notes.mapped("amount")) + sum(vouchers.mapped("discount_value"))

    def _settle_concession(self):
        """Create the money document for whatever approved concession is not
        yet documented. Called by action_close."""
        for rec in self:
            if rec.concession_amount <= 0 or not rec.concession_approved:
                continue
            outstanding = round(rec.concession_amount - rec._concession_documented_amount(), 2)
            if outstanding <= 0.005:
                continue
            if rec.concession_type == "discount":
                document, note = rec._issue_concession_voucher(outstanding)
            else:
                document, note = rec._raise_concession_credit_note(outstanding)
            rec._guarded().write({"concession_settlement_note": note})
            rec.message_post(body=note)
            publish(
                self.env,
                "complaint.concession_settled",
                "fix.complaint",
                rec.id,
                {
                    "complaint": rec.name,
                    "partner_id": rec.customer_id.id,
                    "concession_type": rec.concession_type,
                    "amount": outstanding,
                    "document_model": document._name if document else None,
                    "document_id": document.id if document else None,
                    "settled": bool(document),
                    "note": note,
                },
            )

    def _raise_concession_credit_note(self, amount):
        """(credit note, note) or (None, why not)."""
        self.ensure_one()
        order = self.service_order_id
        if not order:
            return None, (
                "No credit note: the complaint has no service order, so there is no "
                "invoice to credit. Finance settles the BDT %.2f %s from the "
                "complaint.concession_settled event." % (amount, self.concession_type)
            )
        invoice = (
            self.env["fix.ar.invoice"]
            .sudo()
            .search(
                [
                    ("source_model", "=", "fix.service.order"),
                    ("source_id", "=", order.id),
                    ("state", "in", ("issued", "paid")),
                ],
                order="id desc",
                limit=1,
            )
        )
        if not invoice:
            return None, (
                "No credit note: service order %s has no issued invoice. Finance "
                "settles the BDT %.2f %s from the complaint.concession_settled event."
                % (order.name, amount, self.concession_type)
            )
        if amount > invoice.total_payable + 0.005:
            return None, (
                "No credit note: the BDT %.2f concession exceeds invoice %s (BDT %.2f). "
                "A refund beyond the invoice is a payout Finance makes from the "
                "complaint.concession_settled event."
                % (amount, invoice.name, invoice.total_payable)
            )
        note = (
            self.env["fix.credit.note"]
            .sudo()
            .create(
                {
                    "company_id": invoice.company_id.id,
                    "operating_unit_id": invoice.operating_unit_id.id,
                    "invoice_id": invoice.id,
                    "amount": amount,
                    "reason_code": "goodwill",
                    "complaint_id": self.id,
                }
            )
        )
        # Into M20's own authority rule (above BDT 25,000 its manager
        # approves). Issuing and the GL posting stay with Finance.
        note.action_submit()
        return note, (
            "Credit note #%d raised for BDT %.2f against invoice %s (%s); Finance issues it."
            % (note.id, amount, invoice.name, note.state)
        )

    def _issue_concession_voucher(self, amount):
        """(voucher, note): a fixed-BDT M10 voucher for the customer."""
        self.ensure_one()
        days = int(
            self.env["ir.config_parameter"].sudo().get_param(PARAM_VOUCHER_VALID_DAYS)
            or DEFAULT_VOUCHER_VALID_DAYS
        )
        today = fields.Date.context_today(self)
        voucher = (
            self.env["fix.loyalty.voucher"]
            .sudo()
            .create(
                {
                    "company_id": self.company_id.id,
                    "operating_unit_id": self.operating_unit_id.id,
                    "partner_id": self.customer_id.id,
                    "discount_type": "fixed_bdt",
                    "discount_value": amount,
                    "valid_from": today,
                    "valid_until": fields.Date.add(today, days=days),
                    "name_bn": "অভিযোগ %s এর ক্ষতিপূরণ ভাউচার" % self.name,
                    "complaint_id": self.id,
                }
            )
        )
        voucher.action_activate()
        return voucher, (
            "Voucher %s issued for BDT %.2f, valid until %s."
            % (voucher.name, amount, voucher.valid_until)
        )
