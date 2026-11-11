# cd_ap_ext — vendor debit / credit notes (CD-M52-01, A08 M52).
#
# A supplier's credit note (Mushak 6.7 — returns, price decreases) reduces
# what 1000 FiX owes and the input VAT claimed; a supplier's debit note
# (Mushak 6.8 — price increases) adds to both. Each note is linked to the
# bill it adjusts, approved with segregation of duties, posted to the GL,
# recorded as an input-VAT adjustment for the 9.1, and netted in the next
# payment run.
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from .ap_gl import ap_account, ap_journal, post_ap_move
from .fix_ap_controls import require_finance
from .fix_ap_ext import PAYABLE_MATCH_STATES, _q

# A08 M52-12 (F3): the creator rewrote created_by and approved his own
# 15,000 debit note. Stamps and state change only through the actions.
NOTE_GUARDED = {
    "state",
    "created_by",
    "approved_by",
    "move_id",
    "input_credit_id",
    "payment_run_id",
}
NOTE_TERMS = {
    "invoice_id",
    "note_type",
    "mushak_ref",
    "note_date",
    "reason",
    "amount",
    "vat_amount",
    "company_id",
}


class FixVendorNote(models.Model):
    _name = "fix.vendor.note"
    _description = "Vendor Debit / Credit Note (Mushak 6.7 / 6.8)"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "note_date desc, id desc"

    name = fields.Char(compute="_compute_name", store=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one(
        related="invoice_id.operating_unit_id", store=True, index=True
    )
    invoice_id = fields.Many2one(
        "fix.vendor.invoice", string="Bill", required=True, index=True, ondelete="restrict"
    )
    vendor_id = fields.Many2one(related="invoice_id.vendor_id", store=True, string="Vendor")
    note_type = fields.Selection(
        [
            ("decrease", "Credit note from vendor (Mushak 6.7) - reduces payable"),
            ("increase", "Debit note from vendor (Mushak 6.8) - increases payable"),
        ],
        required=True,
        default="decrease",
        tracking=True,
    )
    mushak_ref = fields.Char(string="Mushak 6.7 / 6.8 No", tracking=True)
    note_date = fields.Date(required=True, default=fields.Date.context_today)
    reason = fields.Selection(
        [
            ("return", "Goods returned"),
            ("price", "Price change"),
            ("quantity", "Quantity correction"),
            ("quality", "Quality claim"),
            ("other", "Other"),
        ],
        required=True,
        default="return",
    )
    description = fields.Char()
    currency_id = fields.Many2one(related="invoice_id.currency_id")
    amount = fields.Monetary(
        string="Value (excl. VAT)", currency_field="currency_id", required=True
    )
    vat_amount = fields.Monetary(string="VAT", currency_field="currency_id", default=0.0)
    total = fields.Monetary(currency_field="currency_id", compute="_compute_total", store=True)
    signed_total = fields.Monetary(
        string="Effect on Payable",
        currency_field="currency_id",
        compute="_compute_total",
        store=True,
        help="Negative reduces what is owed to the vendor",
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("approved", "Approved & Posted"),
            ("applied", "Netted in Payment Run"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )
    created_by = fields.Many2one(
        "res.users", default=lambda self: self.env.user, readonly=True, copy=False
    )
    approved_by = fields.Many2one("res.users", readonly=True, copy=False)
    move_id = fields.Many2one("account.move", string="GL Entry", readonly=True, copy=False)
    input_credit_id = fields.Many2one("fix.input.vat.credit", readonly=True, copy=False)
    payment_run_id = fields.Many2one("fix.payment.run", readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | NOTE_GUARDED

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(note.state != "draft" for note in self):
            locked |= NOTE_TERMS
        return locked

    def write(self, vals):
        if NOTE_TERMS & set(vals) and not self._fix_guard_open():
            fixed = self.filtered(lambda n: n.state != "draft")
            changed = [
                n
                for n in NOTE_TERMS & set(vals)
                if any(note._fix_guard_differs(n, vals[n], note[n]) for note in fixed)
            ]
            if changed:
                raise UserError(
                    "Note %s is %s: %s can no longer change."
                    % (fixed[0].name, fixed[0].state, ", ".join(sorted(changed)))
                )
        return super().write(vals)

    def unlink(self):
        if self.filtered(lambda n: n.state != "draft") and not self.env.su:
            raise UserError("Only a draft vendor note is deleted.")
        return super().unlink()

    @api.depends("note_type", "mushak_ref", "invoice_id.invoice_ref")
    def _compute_name(self):
        for note in self:
            form = "6.7" if note.note_type == "decrease" else "6.8"
            note.name = "Mushak %s %s (%s)" % (
                form,
                note.mushak_ref or "draft",
                note.invoice_id.invoice_ref or "",
            )

    @api.depends("amount", "vat_amount", "note_type")
    def _compute_total(self):
        for note in self:
            note.total = _q(note.amount + note.vat_amount)
            note.signed_total = -note.total if note.note_type == "decrease" else note.total

    @api.constrains("amount", "vat_amount", "invoice_id", "note_type")
    def _check_note(self):
        for note in self:
            if note.amount <= 0 or note.vat_amount < 0:
                raise ValidationError("A note carries a positive value and no negative VAT")
            if note.note_type == "decrease":
                others = note.invoice_id.note_ids.filtered(
                    lambda n: n.note_type == "decrease" and n.state != "cancelled"
                )
                if sum(others.mapped("amount")) > note.invoice_id.subtotal + 0.005:
                    raise ValidationError(
                        "Credit notes cannot exceed the value of bill %s"
                        % note.invoice_id.invoice_ref
                    )

    def action_approve(self):
        """Approve and post. SoD: the approver did not create the note."""
        require_finance(self.env, "Approving a vendor note")
        for note in self:
            if note.state != "draft":
                raise UserError("Only a draft note is approved")
            if note.invoice_id.approval_state != "approved" or not note.invoice_id.move_id:
                raise UserError("A note adjusts an approved, posted bill")
            if not (note.mushak_ref or "").strip():
                raise UserError("Enter the vendor's Mushak 6.7 / 6.8 number first")
            if self.env.user in (note.created_by | note.create_uid):
                raise UserError("Segregation of duties: the note's creator cannot approve it")
            if note.note_type == "increase":
                note._check_increase_gate()
            if note.invoice_id.payment_state == "paid" and note.note_type == "decrease":
                # still allowed: the vendor then owes a refund, netted next run
                pass
            note._post()
            note._record_vat_adjustment()
            note._guarded().write({"state": "approved", "approved_by": self.env.user.id})
        return True

    def _check_increase_gate(self):
        """A debit note adds to what is owed, so it passes what a bill of that
        value passes. It was approved by any one accountant and netted into the
        next payment run: past the three-way match and past the matrix.

        Match: a PO bill rises only to the value its PO approval covers.
        Matrix: the approver may sign the top level the amount needs (all the
        increases on the bill together, so one note is not split into several).
        The note has one approver stamp, so the top level signs for the lot."""
        self.ensure_one()
        inv, user = self.invoice_id, self.env.user
        posted = inv.note_ids.filtered(lambda n: n.state in ("approved", "applied")) - self
        raised = posted.filtered(lambda n: n.note_type == "increase")
        if inv.match_state not in PAYABLE_MATCH_STATES:
            raise UserError(
                "G3-06: bill %s is %s (%s): it takes no debit note until its three-way "
                "match holds." % (inv.invoice_ref, inv.match_state, inv.match_detail)
            )
        room = inv._ap_po_headroom()
        if room is not None:
            credited = sum((posted - raised).mapped("amount"))
            net = self.amount + sum(raised.mapped("amount")) - credited
            if net > room + 0.01:
                raise UserError(
                    "G3-06: debit note %s would lift bill %s by BDT %.2f, but its purchase order "
                    "covers BDT %.2f more for the quantities billed. A price increase needs a "
                    "PO change order first; a further quantity is a new bill."
                    % (self.name, inv.invoice_ref, net, max(room, 0.0))
                )
        total = self.total + sum(raised.mapped("total"))
        levels = inv._ap_levels(amount=total)
        if not levels:
            raise UserError(
                "No approval-matrix level covers BDT %.2f in %s — maintain the AP approval "
                "matrix first" % (total, inv.company_id.name)
            )
        top = levels[-1]
        if not inv._ap_may_sign(user, top):
            raise UserError(
                "AP approval matrix: debit notes on bill %s add BDT %.2f, which level %d (%s) "
                "approves — a member of %s."
                % (inv.invoice_ref, total, top.level, top.name, top.group_id.display_name)
            )

    def action_cancel(self):
        for note in self:
            if note.state != "draft":
                raise UserError("Only a draft note can be cancelled (reverse a posted one)")
            note._guarded().write({"state": "cancelled"})
        return True

    def _post(self):
        self.ensure_one()
        inv, env = self.invoice_id, self.env
        company = inv.company_id
        partner = inv.vendor_id.commercial_partner_id
        label = "%s %s" % (self.name, partner.name)
        expense = (
            inv._expense_account(inv.line_ids[:1])
            if inv.line_ids
            else ap_account(env, company, "expense")
        )
        ap = ap_account(env, company, "ap")
        vat = ap_account(env, company, "vat_input") if self.vat_amount else None
        if self.note_type == "decrease":
            lines = [
                (ap, label, self.total, 0.0, partner),
                (expense, label, 0.0, self.amount, partner),
            ]
            if vat:
                lines.append((vat, "Input VAT " + label, 0.0, self.vat_amount, partner))
        else:
            lines = [
                (expense, label, self.amount, 0.0, partner),
                (ap, label, 0.0, self.total, partner),
            ]
            if vat:
                lines.append((vat, "Input VAT " + label, self.vat_amount, 0.0, partner))
        move = post_ap_move(
            env,
            company,
            ap_journal(env, company, "purchase"),
            self.note_date,
            label,
            lines,
            inv.operating_unit_id,
        )
        self._guarded().write({"move_id": move.id})

    def _record_vat_adjustment(self):
        """The note's VAT is an input-VAT adjustment of its own period's 9.1."""
        self.ensure_one()
        if not self.vat_amount:
            return
        inv = self.invoice_id
        profile = inv._tax_profile()
        credit = self.env["fix.input.vat.credit"].create(
            {
                "company_id": inv.company_id.id,
                "operating_unit_id": inv.operating_unit_id.id,
                "partner_id": inv.vendor_id.commercial_partner_id.id,
                "supplier_bin": profile.bin or False,
                "supplier_enlisted": profile.turnover_enlisted,
                "supplier_mushak_no": self.mushak_ref,
                "invoice_date": self.note_date,
                "taxable_amount": self.amount,
                "vat_amount": self.vat_amount,
                "adjustment_type": self.note_type,
                # the supplier 6.3 credit this 6.7 / 6.8 adjusts (M51 checks it)
                "original_credit_id": inv.input_credit_id.id or False,
                "currency_id": inv.currency_id.id,
                "source_ref": self.name,
                "vendor_invoice_id": inv.id,
            }
        )
        credit.action_check_eligibility()
        self._guarded().write({"input_credit_id": credit.id})
