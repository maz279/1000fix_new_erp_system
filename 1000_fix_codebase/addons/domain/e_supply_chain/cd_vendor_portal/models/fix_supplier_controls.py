# fix_supplier_controls — M42 controls that reach into M16 and M52 (A06 S6/S7).
#
#   - The supplier gate on purchase orders (BRU-PRO-02 / BRU-SRM2-01, fail
#     closed): M16 refuses to approve, send or award to any vendor that is not
#     an active fix.supplier with verified, unexpired documents and no
#     unresolved screening hit. cd_requisition cannot see the register (it
#     loads first), so the gate is filled in here.
#   - Supplier bank details under dual control (BRU-SRM2-07, M42-3): a change
#     is a proposal (fix.supplier.bank.change) with verification evidence,
#     confirmed by a second steward or an approver; until then the supplier
#     carries a payment block; both steps write the security audit trail and
#     publish an event. A direct edit of a supplier's res.partner.bank is
#     refused, whoever holds Contact Creation.
#   - Payment block and the approved payee account reach M52: a blocked
#     supplier's bills are not paid and its payment-run lines are skipped;
#     the run pays the account the confirmed change approved.
#   - SOD-01/SOD-02 at bill approval: the supplier's creator, the PO's buyer
#     and requester and its receivers never approve the bill.
import re

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish  # FF-28

from .fix_supplier import GROUP_APPROVER, GROUP_STEWARD, _not_by, _require

BANK_KEY = "fix_supplier_bank_change"
_BANK_TOKEN = object()
BANK_FIELDS = ("acc_number", "bank_id", "partner_id", "acc_holder_name", "allow_out_payment")


class FixPurchaseOrderSupplierGate(models.Model):
    _inherit = "fix.purchase.order"

    @api.model
    def _fix_vendor_blockers(self, partner):
        problems = super()._fix_vendor_blockers(partner)
        if problems or not partner:
            return problems
        supplier = self.env["fix.supplier"]._for_partner(partner)
        if not supplier:
            return ["it has no supplier record in the M42 register"]
        if supplier.status != "active":
            return ["supplier %s is %s" % (supplier.supplier_code, supplier.status)]
        return supplier._a06_order_problems()


class FixSupplierBankChange(models.Model):
    """A proposed change of a supplier's payee bank account."""

    _name = "fix.supplier.bank.change"
    _description = "Supplier Bank-Detail Change"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "id desc"

    name = fields.Char(required=True, default="New", copy=False, readonly=True)
    supplier_id = fields.Many2one(
        "fix.supplier", string="Supplier", required=True, index=True, ondelete="restrict"
    )
    company_id = fields.Many2one(related="supplier_id.company_id", store=True, readonly=True)
    acc_number = fields.Char(string="New Account Number", required=True)
    bank_id = fields.Many2one("res.bank", string="Bank")
    routing_number = fields.Char(string="BEFTN Routing Number")
    acc_holder_name = fields.Char(string="Account Holder")
    verification_ref = fields.Char(
        string="Call-Back Verification",
        help="Who confirmed the change with the supplier on a known number, when, and how.",
    )
    evidence_ref = fields.Char(string="Evidence File Reference")
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("proposed", "Proposed"),
            ("confirmed", "Confirmed"),
            ("rejected", "Rejected"),
        ],
        required=True,
        default="draft",
        tracking=True,
    )
    proposed_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    proposed_at = fields.Datetime(readonly=True, copy=False)
    confirmed_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    confirmed_at = fields.Datetime(readonly=True, copy=False)
    reject_reason = fields.Char(readonly=True, copy=False)
    previous_bank_id = fields.Many2one("res.partner.bank", readonly=True, copy=False)
    partner_bank_id = fields.Many2one("res.partner.bank", readonly=True, copy=False)

    CHANGE_TERMS = (
        "supplier_id",
        "acc_number",
        "bank_id",
        "routing_number",
        "acc_holder_name",
        "verification_ref",
        "evidence_ref",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "proposed_by_id",
            "proposed_at",
            "confirmed_by_id",
            "confirmed_at",
            "reject_reason",
            "previous_bank_id",
            "partner_bank_id",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(r.state != "draft" for r in self):
            locked |= set(self.CHANGE_TERMS)
        return locked

    @api.constrains("routing_number")
    def _check_routing(self):
        for rec in self:
            if rec.routing_number and not re.fullmatch(r"\d{9}", rec.routing_number.strip()):
                raise ValidationError("A BEFTN routing number is 9 digits.")

    @api.model_create_multi
    def create(self, vals_list):
        _require(self.env, "Proposing a bank-detail change", GROUP_STEWARD)
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.supplier.bank.change") or "SBANK/New"
                )
        return super().create(vals_list)

    def write(self, vals):
        if (
            set(self.CHANGE_TERMS) & set(vals)
            and not self._fix_guard_has_token()
            and any(r.state != "draft" for r in self)
        ):
            raise UserError("A proposed bank-detail change is fixed; reject it and propose again.")
        return super().write(vals)

    def _audit(self, detail):
        self.ensure_one()
        self.env["fix.security.audit"].sudo().create(
            {
                "event": "privileged",
                "object_ref": "fix.supplier,%s" % self.supplier_id.id,
                "detail": detail[:250],
                "actor_id": self.env.uid,
            }
        )

    def action_propose(self):
        _require(self.env, "Proposing a bank-detail change", GROUP_STEWARD)
        for rec in self:
            if rec.state != "draft":
                raise UserError("Bank change %s is %s." % (rec.name, rec.state))
            if not (rec.verification_ref or "").strip() or not (rec.evidence_ref or "").strip():
                raise UserError(
                    "Record the call-back verification and the evidence file for bank change "
                    "%s before proposing it." % rec.name
                )
            rec._guarded().write(
                {
                    "state": "proposed",
                    "proposed_by_id": self.env.uid,
                    "proposed_at": fields.Datetime.now(),
                }
            )
            supplier = rec.supplier_id.sudo()
            supplier._guarded().write({"payment_block": True})
            supplier.message_post(
                body="Bank-detail change %s proposed: payments blocked." % rec.name
            )
            rec._audit("Supplier bank change %s proposed (payment block set)" % rec.name)
            publish(
                self.env,
                "supplier.bank_change.proposed",
                "fix.supplier",
                supplier.id,
                {"change": rec.name, "proposed_by": self.env.uid},
            )
        return True

    def action_confirm(self):
        """A second steward or an approver confirms: the account is written,
        becomes the approved payee and the block lifts."""
        _require(self.env, "Confirming a bank-detail change", GROUP_STEWARD, GROUP_APPROVER)
        Bank = self.env["res.partner.bank"].sudo().with_context(**{BANK_KEY: _BANK_TOKEN})
        for rec in self:
            if rec.state != "proposed":
                raise UserError(
                    "Confirm a proposed bank change (%s is %s)." % (rec.name, rec.state)
                )
            _not_by(
                self.env, rec.proposed_by_id | rec.create_uid, "proposed this bank-detail change"
            )
            supplier = rec.supplier_id.sudo()
            partner = supplier.partner_id.commercial_partner_id
            account = Bank.search(
                [("partner_id", "=", partner.id), ("acc_number", "=", rec.acc_number)], limit=1
            )
            vals = {"bank_id": rec.bank_id.id or False}
            if rec.acc_holder_name:
                vals["acc_holder_name"] = rec.acc_holder_name
            if account:
                account.write(vals)
            else:
                account = Bank.create(dict(vals, partner_id=partner.id, acc_number=rec.acc_number))
            rec._guarded().write(
                {
                    "state": "confirmed",
                    "confirmed_by_id": self.env.uid,
                    "confirmed_at": fields.Datetime.now(),
                    "previous_bank_id": supplier.bank_account_id.id or False,
                    "partner_bank_id": account.id,
                }
            )
            pending = self.sudo().search_count(
                [
                    ("supplier_id", "=", supplier.id),
                    ("state", "=", "proposed"),
                    ("id", "!=", rec.id),
                ]
            )
            supplier._guarded().write(
                {"bank_account_id": account.id, "payment_block": bool(pending)}
            )
            supplier.message_post(body="Bank-detail change %s confirmed." % rec.name)
            rec._audit(
                "Supplier bank change %s confirmed; payee account %s" % (rec.name, account.id)
            )
            publish(
                self.env,
                "supplier.bank_change.confirmed",
                "fix.supplier",
                supplier.id,
                {"change": rec.name, "confirmed_by": self.env.uid, "partner_bank_id": account.id},
            )
        return True

    def action_reject(self, reason=None):
        _require(self.env, "Rejecting a bank-detail change", GROUP_STEWARD, GROUP_APPROVER)
        for rec in self:
            if rec.state not in ("draft", "proposed"):
                raise UserError("Bank change %s is %s." % (rec.name, rec.state))
            if not (reason or "").strip():
                raise UserError("State why bank change %s is rejected." % rec.name)
            rec._guarded().write({"state": "rejected", "reject_reason": reason.strip()})
            supplier = rec.supplier_id.sudo()
            pending = self.sudo().search_count(
                [("supplier_id", "=", supplier.id), ("state", "=", "proposed")]
            )
            supplier._guarded().write({"payment_block": bool(pending)})
            rec._audit("Supplier bank change %s rejected: %s" % (rec.name, reason.strip()))
        return True


class ResPartnerBankSupplierGuard(models.Model):
    """A supplier's bank account changes only through a confirmed
    fix.supplier.bank.change (BRU-SRM2-07)."""

    _inherit = "res.partner.bank"

    def _fix_supplier_partners(self, partners):
        commercial = partners.mapped("commercial_partner_id")
        if not commercial:
            return self.env["res.partner"]
        suppliers = (
            self.env["fix.supplier"]
            .sudo()
            .search([("partner_id", "in", (partners | commercial).ids)])
        )
        return suppliers.mapped("partner_id.commercial_partner_id")

    def _fix_bank_guard(self, partners):
        if self.env.su or self.env.context.get(BANK_KEY) is _BANK_TOKEN:
            return
        if self._fix_supplier_partners(partners):
            raise UserError(
                "A supplier's bank details change only through a bank-detail change request "
                "(proposed with verification, confirmed by a second person)."
            )

    @api.model_create_multi
    def create(self, vals_list):
        partners = self.env["res.partner"].browse(
            [v["partner_id"] for v in vals_list if v.get("partner_id")]
        )
        self._fix_bank_guard(partners)
        return super().create(vals_list)

    def write(self, vals):
        if set(BANK_FIELDS) & set(vals):
            partners = self.mapped("partner_id")
            if vals.get("partner_id"):
                partners |= self.env["res.partner"].browse(vals["partner_id"])
            self._fix_bank_guard(partners)
        return super().write(vals)

    def unlink(self):
        self._fix_bank_guard(self.mapped("partner_id"))
        return super().unlink()


class FixVendorInvoiceSupplierControls(models.Model):
    _inherit = "fix.vendor.invoice"

    def _fix_supplier(self):
        self.ensure_one()
        return self.env["fix.supplier"]._for_partner(self.vendor_id)

    def action_approve(self):
        """SOD-01 / SOD-02 (BRU-PRO-04/05): whoever created the supplier, raised
        or requested the PO, or received its goods does not approve the bill."""
        if not self.env.su:
            for inv in self:
                order = inv.sudo().requisition_id
                conflicted = inv._fix_supplier().create_uid
                if order:
                    conflicted |= (
                        order.buyer_id
                        | order.create_uid
                        | order.requisition_id.requested_by.user_id
                        | order.receipt_ids.filtered(lambda r: r.state == "posted").mapped(
                            "receiver_id"
                        )
                    )
                if self.env.user in conflicted:
                    raise UserError(
                        "Segregation of duties (SOD-01/SOD-02): you created the supplier, raised "
                        "or requested the purchase order, or received its goods; another approver "
                        "approves bill %s." % inv.invoice_ref
                    )
        return super().action_approve()

    def action_request_payment(self):
        for inv in self:
            supplier = inv._fix_supplier()
            if supplier and supplier.payment_block:
                raise UserError(
                    "Supplier %s has a bank-detail change awaiting confirmation: payments are "
                    "blocked until it is confirmed." % supplier.supplier_code
                )
        return super().action_request_payment()


class FixPaymentRunLineSupplierControls(models.Model):
    _inherit = "fix.payment.run.line"

    def _apply_skip_rules(self):
        result = super()._apply_skip_rules()
        Supplier = self.env["fix.supplier"]
        for line in self:
            supplier = Supplier._for_partner(line.partner_id)
            if not supplier:
                continue
            if supplier.payment_block:
                line.write(
                    {
                        "state": "skipped",
                        "skip_reason": "Supplier bank-detail change awaiting confirmation: "
                        "payment blocked",
                    }
                )
            elif supplier.bank_account_id:
                line.write({"bank_account_id": supplier.bank_account_id.id})
        return result
