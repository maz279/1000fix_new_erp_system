# A04 ERP audit (20 Nov 2026), stream B3: the M09 money legs that never
# reached M20 / the GL.
#
# M09-F2: a protection plan was sold, reserved, claimed on and cancelled with
#   no AR document and no GL entry anywhere (the 4,504.11 cancellation refund
#   was a number on the policy). Now:
#     * activation raises the premium's DRAFT M20 invoice on the customer
#       (source fix.protection.policy). Its issue credits the contract
#       liability (deferred_revenue) and the M53 deferral schedule releases it
#       over the cover term (cd_subscription fix_invoice_deferral);
#     * every reserve movement posts: establish / top-up Dr warranty cost
#       expense / Cr warranty provision; a release reverses it, except the
#       release of a cash or refund settlement, which the M50 payment to the
#       customer debits instead;
#     * a cash / refund settlement is an M50 payment instruction to the
#       customer (Dr provision / Cr bank when treasury releases it);
#     * a cancellation refund is a SUBMITTED M20 credit note on the premium
#       invoice (the M20 ladder approves it; money already paid goes back
#       through M50), and the premium's deferral stops on the day.
#   Account roles (cd_billing_engine.account_code.<role>), defaults on the
#   fix_real chart for the owner to confirm: warranty_provision 200002
#   "Provision for Warranty Extension" (200005 "Provision For Warranty cost"
#   is the alternative), warranty_cost 500229 "Warranty Cost Expense".
# M09-F3: an approved claim write-off moved the claim to written_off and left
#   the OEM invoice issued with its residual; nothing posted. The write-off
#   now writes the OEM invoice off on M20 (fix.ar.writeoff, posted: loss
#   allowance first, the rest to bad-debt expense / Cr AR). The M09 decision
#   (a Finance Manager who did not raise the claim or the request,
#   BRU-WTY-07) is the approval.
# M09-F14: the part of a brand remittance no claim line takes was never
#   booked: it is now a confirmed M20 receipt on the brand (unapplied cash).
from odoo import api, fields, models
from odoo.exceptions import UserError

from .fix_ar_engine import AR_ACCOUNTS, _ar_account, _ar_journal, _post_ar_move
from .fix_billing_engine import dhaka_date

AR_ACCOUNTS.setdefault(
    "warranty_provision", ("200002", "Provision for Warranty Extension (protection reserve)")
)
AR_ACCOUNTS.setdefault("warranty_cost", ("500229", "Warranty Cost Expense"))

PARAM_PREMIUM_VAT = "cd_warranty_claims.protection_premium_vat"
CASH_FULFILMENT = ("cash", "refund")


class FixCreditNoteA04Reasons(models.Model):
    _inherit = "fix.credit.note"

    reason_code = fields.Selection(
        selection_add=[
            ("warranty_claim", "Warranty Claim Re-decided (OEM)"),
            ("protection_refund", "Protection Plan Cancellation Refund"),
        ],
        ondelete={"warranty_claim": "cascade", "protection_refund": "cascade"},
    )


class FixArInvoiceProtectionPremium(models.Model):
    _inherit = "fix.ar.invoice"

    def _revenue_role(self) -> str:
        self.ensure_one()
        if self.source_model == "fix.protection.policy":
            # a protection premium is earned over the cover term (IFRS 15)
            return "deferred_revenue"
        return super()._revenue_role()


def _gl_post(env, company, ou, entry_date, ref, lines):
    """Post a balanced set of (account, label, debit, credit, partner) lines
    on the general journal; refuses when an account or the journal is missing
    (the ledger is the point of these postings)."""
    missing = [label for acc, label, *_rest in lines if not acc]
    if missing:
        raise UserError(
            "Posting refused for %s: account role(s) not configured in %s (system parameter "
            "cd_billing_engine.account_code.<role>): %s" % (ref, company.name, ", ".join(missing))
        )
    if not _ar_journal(env, company):
        raise UserError("Posting refused: %s has no general journal." % company.name)
    dims = env["fix.ar.invoice"]._ar_posting_dims(operating_unit_id=ou.id if ou else None)
    move, note = _post_ar_move(
        env,
        company,
        entry_date,
        ref,
        [(acc.id, label, debit, credit, partner) for acc, label, debit, credit, partner in lines],
        dict.fromkeys(range(len(lines)), dims),
        source="ar",
    )
    if not move:
        raise UserError("Posting refused for %s: %s" % (ref, note or "posting failed"))
    return move


class FixProtectionPolicyMoney(models.Model):
    _inherit = "fix.protection.policy"

    premium_invoice_id = fields.Many2one(
        "fix.ar.invoice",
        string="Premium Invoice (M20)",
        readonly=True,
        copy=False,
        help="The customer's premium invoice: its issue defers the premium over the cover term.",
    )
    refund_credit_note_id = fields.Many2one(
        "fix.credit.note", string="Refund Credit Note (M20)", readonly=True, copy=False
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"premium_invoice_id", "refund_credit_note_id"}

    def _fix_deferral_period(self):
        """(start, end) the premium is recognised over (cd_subscription's
        invoice deferral reads it)."""
        self.ensure_one()
        return self.term_start, self.term_end

    def _fix_premium_line(self):
        """The premium as an invoice line: VAT-inclusive (what the customer
        paid) and split by M51's standard rate, unless the owner sets the
        premium as not subject to VAT (cd_warranty_claims.protection_premium_vat
        = exempt)."""
        from decimal import ROUND_HALF_UP, Decimal

        from odoo.addons.cd_tax_engine_bd.models import tax_logic

        from .fix_billing_engine import m51_determine

        self.ensure_one()
        gross = round(self.premium, 2)
        mode = (self.env["ir.config_parameter"].sudo().get_param(PARAM_PREMIUM_VAT) or "").strip()
        label = "Protection plan %s - %s (%s to %s)" % (
            self.name,
            self.product_id.name,
            self.term_start,
            self.term_end,
        )
        if mode == "exempt":
            return {
                "description": label,
                "taxable_amount": gross,
                "vat_amount": 0.0,
                "line_total": gross,
            }
        probe = m51_determine(
            self.env,
            [tax_logic.TaxLine(product_code="SVC", qty=Decimal("1"), unit_price=Decimal("100.00"))],
            company=self.company_id,
        ).lines[0]
        rate = float(probe.vat_amount) / 100.0
        taxable = float(
            (Decimal(str(gross)) / Decimal(str(1.0 + rate))).quantize(
                Decimal("0.01"), ROUND_HALF_UP
            )
        )
        return {
            "description": label,
            "taxable_amount": taxable,
            "vat_amount": round(gross - taxable, 2),
            "line_total": gross,
        }

    def _fix_raise_premium_invoice(self):
        Invoice = self.env["fix.ar.invoice"].sudo()
        for policy in self:
            if policy.premium_invoice_id or policy.premium <= 0:
                continue
            existing = Invoice.search(
                [("source_model", "=", policy._name), ("source_id", "=", policy.id)], limit=1
            )
            invoice = existing or Invoice.create(
                {
                    "company_id": policy.company_id.id,
                    "operating_unit_id": (
                        policy.operating_unit_id
                        or self.env["operating.unit"]
                        .sudo()
                        .search([("company_id", "=", policy.company_id.id)], limit=1)
                    ).id,
                    "customer_id": policy.partner_id.id,
                    "currency_id": policy.currency_id.id,
                    "source_model": policy._name,
                    "source_id": policy.id,
                    "invoice_date": dhaka_date(fields.Datetime.now()),
                    "manual_reason": "Protection plan premium %s (%s)"
                    % (policy.name, policy.sale_ref or "counter sale"),
                    "line_ids": [(0, 0, policy._fix_premium_line())],
                }
            )
            policy._guarded().write({"premium_invoice_id": invoice.id})
            policy.message_post(
                body="Premium invoice %s raised (draft): finance issues it; the premium is then "
                "recognised over the cover term." % (invoice.name or "#%s" % invoice.id)
            )

    def action_activate(self):
        result = super().action_activate()
        self.filtered(lambda p: p.state == "active")._fix_raise_premium_invoice()
        return result

    def action_cancel(self, reason=None):
        result = super().action_cancel(reason=reason)
        today = dhaka_date(fields.Datetime.now())
        for policy in self.filtered(lambda p: p.state == "cancelled"):
            invoice = policy.premium_invoice_id.sudo()
            if not invoice:
                continue
            if invoice.state == "draft":
                if policy.refund_amount + 0.005 >= policy.premium:
                    invoice.action_cancel(
                        "Policy %s cancelled before its premium was invoiced" % policy.name
                    )
                else:
                    policy.message_post(
                        body="Premium invoice %s is still a draft: issue it, then credit the refund "
                        "of %.2f." % (invoice.display_name, policy.refund_amount)
                    )
                continue
            refund = round(
                min(policy.refund_amount, invoice.total_payable - invoice.credited_amount), 2
            )
            note = self.env["fix.credit.note"]
            if refund > 0.005 and invoice.state in ("issued", "paid"):
                note = (
                    self.env["fix.credit.note"]
                    .sudo()
                    ._fix_request_credit(
                        invoice,
                        refund,
                        "protection_refund",
                        note="Policy %s cancelled (%s): pro-rata refund of the unused cover."
                        % (policy.name, (reason or "").strip()),
                    )
                )
                policy._guarded().write({"refund_credit_note_id": note.id})
            policy._fix_stop_premium_deferral(today, invoice, note)
        return result

    def _fix_stop_premium_deferral(self, on_date, invoice, note):
        """Recognise the premium up to the cancellation, then what is not
        refunded (it is earned: the cover ended), and stop the schedule."""
        self.ensure_one()
        Schedule = self.env.get("fix.revenue.schedule")
        if Schedule is None:
            return
        schedule = Schedule.sudo().search(
            [("source_model", "=", invoice._name), ("source_id", "=", invoice.id)], limit=1
        )
        if not schedule or not hasattr(schedule, "_fix_stop_at"):
            return
        keep = 0.0
        if note:
            ratio = (invoice.vat_amount / invoice.total_payable) if invoice.total_payable else 0.0
            keep = round(note.amount * (1.0 - ratio), 2)
        schedule._fix_stop_at(on_date, keep_deferred=keep)


class FixProtectionReserveGl(models.Model):
    _inherit = "fix.protection.reserve"

    move_id = fields.Many2one("account.move", string="GL Move", readonly=True, copy=False)
    gl_note = fields.Char(string="GL Note", readonly=True, copy=False)

    def _fix_post_movement(self):
        for mv in self:
            policy = mv.policy_id.sudo()
            company = policy.company_id
            amount = round(abs(mv.amount), 2)
            if amount <= 0.005:
                continue
            claim = mv.claim_id
            if mv.amount < 0 and claim and claim.fulfilment_type in CASH_FULFILMENT:
                # the M50 payment to the customer debits the provision
                continue
            provision = _ar_account(self.env, company, "warranty_provision")
            cost = _ar_account(self.env, company, "warranty_cost")
            if not provision or not cost:
                # the AR family's honest skip (gl_note): a chart without the
                # roles posts nothing and says so on the movement
                missing = [
                    r
                    for r, a in (("warranty_provision", provision), ("warranty_cost", cost))
                    if not a
                ]
                mv.sudo().write(
                    {
                        "gl_note": "GL not posted: account role(s) %s not configured in %s "
                        "(cd_billing_engine.account_code.<role>)"
                        % (", ".join(missing), company.name)
                    }
                )
                continue
            ref = "PROTECTION RESERVE %s %s - %s" % (policy.name, mv.movement_type, mv.reason)
            if mv.amount > 0:
                lines = [
                    (cost, "Warranty cost: protection reserve", amount, 0.0, False),
                    (provision, "Protection reserve (provision)", 0.0, amount, False),
                ]
            else:
                lines = [
                    (provision, "Protection reserve released", amount, 0.0, False),
                    (cost, "Warranty cost: reserve released", 0.0, amount, False),
                ]
            move = _gl_post(
                self.env,
                company,
                policy.operating_unit_id,
                dhaka_date(fields.Datetime.now()),
                ref,
                lines,
            )
            mv.sudo().write({"move_id": move.id})

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._fix_post_movement()
        return records


class FixProtectionClaimMoney(models.Model):
    _inherit = "fix.protection.claim"

    payment_ref = fields.Char(string="Payment Instruction (M50)", readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"payment_ref"}

    def action_settle(self):
        for claim in self.filtered(lambda c: c.fulfilment_type in CASH_FULFILMENT):
            if "fix.payment.execution" not in self.env:
                raise UserError(
                    "%s is settled in cash: the payment to the customer goes through treasury "
                    "(M50), which is not installed." % claim.name
                )
        result = super().action_settle()
        for claim in self.filtered(
            lambda c: c.state == "settled" and c.fulfilment_type in CASH_FULFILMENT
        ):
            claim._fix_request_customer_payment()
        return result

    def _fix_request_customer_payment(self):
        self.ensure_one()
        if self.payment_ref:
            return
        policy = self.policy_id.sudo()
        company = policy.company_id
        provision = _ar_account(self.env, company, "warranty_provision")
        if not provision:
            raise UserError(
                "Settlement refused: account role warranty_provision is not configured in %s."
                % company.name
            )
        customer = self.partner_id.commercial_partner_id.sudo()
        pay = self.env["fix.payment.execution"]._fix_request_payment(
            self._name,
            self.id,
            customer,
            customer.bank_ids[:1],
            round(self.approved_amount, 2),
            policy.currency_id,
            "Protection claim %s settlement (%s)" % (self.name, policy.name),
            self.decided_by_id,
            company_id=company.id,
            operating_unit_id=(policy.operating_unit_id.id or False),
            method="bank_transfer",
            payee=customer.display_name,
            debit_account_id=provision.id,
        )
        self._guarded().write({"payment_ref": pay.name})
        self.message_post(
            body="Payment instruction %s (BDT %.2f) is pending with treasury; its release debits "
            "the protection reserve." % (pay.name, self.approved_amount)
        )


class FixClaimWriteoffPosting(models.Model):
    _inherit = "fix.claim.writeoff"

    ar_writeoff_id = fields.Many2one(
        "fix.ar.writeoff", string="AR Write-off (M20)", readonly=True, copy=False
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"ar_writeoff_id"}

    def action_approve(self):
        self._decide()  # the role and BRU-WTY-07 segregation checks first
        invoices = {}
        for rec in self:
            claim = rec.claim_id.sudo()
            invoice = claim._oem_invoice()
            if not invoice or invoice.state != "issued":
                raise UserError(
                    "Write-off %s: the brand's OEM invoice for %s is %s. The write-off is booked "
                    "against the receivable, so the invoice is issued first."
                    % (rec.name, claim.claim_no, invoice.state if invoice else "not raised")
                )
            invoice.invalidate_recordset(["amount_residual"])
            if rec.amount > invoice.amount_residual + 0.005:
                raise UserError(
                    "Write-off %s of %.2f exceeds the %.2f still open on OEM invoice %s."
                    % (rec.name, rec.amount, invoice.amount_residual, invoice.name)
                )
            invoices[rec.id] = invoice
        result = super().action_approve()
        for rec in self.filtered(lambda r: r.state == "approved"):
            rec._fix_post_ar_writeoff(invoices[rec.id])
        return result

    def _fix_post_ar_writeoff(self, invoice):
        self.ensure_one()
        Writeoff = self.env["fix.ar.writeoff"].sudo()
        claim = self.claim_id.sudo()
        wo = Writeoff.create(
            {
                "invoice_id": invoice.id,
                "reason": "Warranty claim %s written off (%s): %s"
                % (claim.claim_no, self.name, (self.reason or "")[:150]),
                "recovery_history": "Claim %s approved %.2f, remitted %.2f; write-off %s requested "
                "by %s, approved by %s (BRU-WTY-07)."
                % (
                    claim.claim_no,
                    claim.approved_amount,
                    claim.remittance_amount,
                    self.name,
                    self.requested_by_id.name,
                    self.approved_by_id.name,
                ),
            }
        )
        wo._guarded().write(
            {
                "state": "requested",
                "amount": round(self.amount, 2),
                "requested_by_id": self.requested_by_id.id,
                "requested_at": fields.Datetime.now(),
            }
        )
        invoice.invalidate_recordset(["amount_residual"])
        if abs(invoice.amount_residual - wo.amount) <= 0.005:
            wo._fin_after_approve()  # posts and closes the invoice as written off
        else:
            wo._fix_post_partial()
        self.sudo()._guarded().write({"ar_writeoff_id": wo.id})
        claim.message_post(
            body="Write-off %s booked on OEM invoice %s as %s." % (self.name, invoice.name, wo.name)
        )
        return wo


class FixArWriteoffPartial(models.Model):
    _inherit = "fix.ar.writeoff"

    def _fix_post_partial(self):
        """Part of an invoice written off (a claim write-off of part of the
        brand's debt): the same posting as a full write-off - the loss
        allowance first, the rest to bad-debt expense / Cr AR - and the
        invoice stays issued for the rest."""
        self.ensure_one()
        wo = self.sudo()
        invoice = wo.invoice_id
        company = invoice.company_id
        allowance_acc, available = wo._allowance()
        use = round(min(wo.amount, available), 2) if allowance_acc else 0.0
        excess = round(wo.amount - use, 2)
        debit_lines = []
        if use > 0.005:
            debit_lines.append(("ecl_provision", allowance_acc, use, invoice.customer_id.id))
        if excess > 0.005:
            debit_lines.append(
                (
                    "writeoff_expense",
                    _ar_account(wo.env, company, "writeoff_expense"),
                    excess,
                    False,
                )
            )
        move = invoice._post_reversal_gl(
            "WRITE-OFF INV %s (part) — %s" % (invoice.name, wo.reason),
            debit_lines,
            [("ar", _ar_account(wo.env, company, "ar"), wo.amount, invoice.customer_id.id)],
        )
        wo._guarded().write(
            {
                "state": "posted",
                "move_id": move.id,
                "allowance_account_id": allowance_acc.id if use > 0.005 else False,
                "allowance_amount": use,
                "expense_amount": excess,
            }
        )


class FixBrandRemittanceUnmatched(models.Model):
    _inherit = "fix.brand.remittance"

    unmatched_receipt_id = fields.Many2one(
        "fix.ar.receipt", string="Unallocated Cash Receipt (M20)", readonly=True, copy=False
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"unmatched_receipt_id"}

    def action_match(self):
        result = super().action_match()
        for rec in self.filtered(lambda r: r.state == "unmatched" and not r.unmatched_receipt_id):
            amount = round(rec.unmatched_amount, 2)
            if amount <= 0.005:
                continue
            partner = (
                rec.brand_id.billing_partner()
                if hasattr(rec.brand_id, "billing_partner")
                else False
            )
            if not partner:
                rec.message_post(
                    body="BDT %.2f of this payment is not on any claim and is NOT booked: brand %s "
                    "has no OEM billing partner to hold it. Link it, then book the receipt."
                    % (amount, rec.brand_id.name)
                )
                continue
            ou = (
                self.env["operating.unit"]
                .sudo()
                .search([("company_id", "=", rec.company_id.id)], limit=1)
            )
            receipt = (
                self.env["fix.ar.receipt"]
                .sudo()
                .with_company(rec.company_id)
                .create(
                    {
                        "company_id": rec.company_id.id,
                        "operating_unit_id": ou.id or False,
                        "customer_id": partner.id,
                        "amount": amount,
                        "method": "bank_transfer",
                        "reference": "%s (unallocated, %s)" % (rec.bank_ref, rec.name),
                        "receipt_date": rec.received_on,
                    }
                )
            )
            receipt.action_confirm()
            rec._guarded().write({"unmatched_receipt_id": receipt.id})
            rec.message_post(
                body="BDT %.2f not on any claim booked as receipt %s on %s (unapplied cash)."
                % (amount, receipt.name, partner.name)
            )
        return result
