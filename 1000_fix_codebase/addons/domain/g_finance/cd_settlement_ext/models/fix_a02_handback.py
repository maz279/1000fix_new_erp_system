# fix_a02_handback — the A02 money hand-backs to finance (A02 audit B2, P1).
#
# Three A02 events reached the outbox and stopped there (FF-48 baseline): a
# paid order was cancelled, a transit-damage claim was settled, an MSP SLA
# credit was applied, and finance never heard of any of them. Each is now an
# R8 relay consumer that raises the finance document, in draft or pending,
# for finance to approve:
#
#   service_order.refund_requested -> a draft M20 credit note against the
#       order's invoice; with no invoice, a pending M50 refund instruction;
#   damage.claim.settled -> a pending M50 payout instruction to the claimant,
#       and a draft M20 recovery invoice to the courier when the courier is
#       the liable party;
#   msp.sla_credit_applied -> a draft M20 credit note to the MSP customer.
#
# Rules the three share:
#   * superuser only: consume_* is reachable over JSON-RPC, and only the relay
#     (cron_relay, sudo) may turn an event into a money document;
#   * the payload is a claim, not evidence: the source record is re-read by
#     the event's aggregate id, it must be in the state the event announces,
#     and every amount comes from the record. A forged event is REFUSED with
#     an error, so the relay records a failed (then dead-lettered) delivery;
#   * idempotent per source record: (source_model, source_id) is unique on
#     every document raised here, so a replay returns what exists, and a user
#     cannot pre-create a document under a hand-back key;
#   * nothing is paid: treasury releases an instruction and finance approves
#     and issues a credit note, under the controls those models enforce. The
#     amount raised is the ceiling: it cannot be raised afterwards;
#   * GL accounts are configured, never guessed (the settlement pattern,
#     system parameter cd_settlement_ext.account_code.<role>). A role with no
#     account leaves the M50 debit empty, so M50 clears the payment to its
#     outgoing-payments account, and the instruction says so.
from odoo import Command, api, fields, models
from odoo.addons.cd_billing_engine.models.fix_ar_engine import _ar_account
from odoo.exceptions import AccessError, UserError, ValidationError

# role -> (M20 role used when no system parameter names an account, label).
# customer_refund: an M20 receipt credited the customer's AR control line, so
# the refund debits it back. damage_claim_expense: the chart has no account
# that is certainly "transit damage claims", so it has no default.
HANDBACK_ACCOUNTS = {
    "customer_refund": ("ar", "Customer refund (the customer's money held on AR control)"),
    "damage_claim_expense": (None, "Transit damage claim expense"),
    # A04 C7: an approved channel rebate's payout (M40 -> M50). A partner
    # payable, not AR money; the GL account is finance's to configure
    # (cd_settlement_ext.account_code.partner_rebate_payout).
    "partner_rebate_payout": (None, "Channel partner rebate payout"),
}

# the source models whose M50 instructions are hand-backs, and the field
# holding the amount the instruction may not exceed
HANDBACK_PAYMENT_SOURCES = {
    "fix.service.order": "amount_settled_bdt",
    "fix.damage.claim": "settled_amount",
}
# the M20 receipt tender -> the M50 method the refund goes back by
RECEIPT_REFUND_METHOD = {
    "cash": "cash",
    "cheque": "bank_transfer",
    "bank_transfer": "bank_transfer",
    "bkash": "mobile_fs",
    "nagad": "mobile_fs",
    "mobile_wallet": "mobile_fs",
    "card": "bank_transfer",
}
RELAY_ONLY = "is set only by the event relay (A02 audit B2)"


def _handback_account(env, company, role):
    """(account, note): the configured account for a hand-back role, or an
    empty account and the reason. Never guessed."""
    ar_role, label = HANDBACK_ACCOUNTS[role]
    param = "cd_settlement_ext.account_code.%s" % role
    code = env["ir.config_parameter"].sudo().get_param(param)
    Account = env["account.account"].with_company(company)
    if code:
        account = Account.search([("code", "=", code), ("company_ids", "in", company.id)], limit=1)
        if account:
            return account, False
        reason = "no GL account %s exists in %s (system parameter %s)" % (code, company.name, param)
    else:
        account = _ar_account(env, company, ar_role) if ar_role else Account
        if account:
            return account, False
        reason = "no GL account is configured for %s in %s; set system parameter %s" % (
            label,
            company.name,
            param,
        )
    return Account, (
        "Debit account not set: %s. Until it is, M50 posts the payment to its "
        "outgoing-payments clearing account." % reason
    )


class FixFinanceHandback(models.AbstractModel):
    """The R8 consumers of the A02 money events (no table of its own: each
    document raised carries its source)."""

    _name = "fix.finance.handback"
    _description = "A02 Finance Hand-back Consumers"

    # ------------------------------------------------------------ shared
    def _handback_assert_relay(self):
        if not self.env.su:
            raise AccessError(
                "Finance hand-back consumers run only from the event relay (A02 audit B2)."
            )

    def _handback_source(self, event, model, label):
        """The record the event names, re-read from the database."""
        aggregate = event.get("aggregate")
        if aggregate and aggregate != model:
            raise UserError(
                "%s refused: the event's aggregate is %s, not %s." % (label, aggregate, model)
            )
        try:
            rec_id = int(event.get("aggregate_id") or 0)
        except (TypeError, ValueError):
            rec_id = 0
        record = self.env[model].sudo().browse(rec_id).exists() if rec_id > 0 else None
        if not record:
            raise UserError("%s refused: there is no %s #%s." % (label, model, rec_id))
        return record, event.get("payload") or {}

    @staticmethod
    def _handback_check_amount(label, payload, key, actual):
        """An amount in the payload must be the record's own."""
        if payload.get(key) is None:
            return
        try:
            claimed = float(payload[key])
        except (TypeError, ValueError):
            raise UserError("%s refused: the event's %s is not a number." % (label, key)) from None
        if abs(claimed - actual) > 0.005:
            raise UserError(
                "%s refused: the event says BDT %.2f but the record says BDT %.2f."
                % (label, claimed, actual)
            )

    def _handback_note(self, record, marker, body):
        """Post `body` on `record` once per marker."""
        seen = (
            self.env["mail.message"]
            .sudo()
            .search_count(
                [
                    ("model", "=", record._name),
                    ("res_id", "=", record.id),
                    ("body", "ilike", marker),
                ]
            )
        )
        if not seen:
            record.sudo().message_post(body="%s %s" % (marker, body))

    def _handback_ou(self, company, *candidates):
        for ou in candidates:
            if ou:
                return ou
        return self.env["operating.unit"].sudo().search([("company_id", "=", company.id)], limit=1)

    def _handback_instruction(self, source, vals, role):
        """A pending M50 instruction for `source` (one per source record)."""
        Execution = self.env["fix.payment.execution"].sudo()
        existing = Execution.search(
            [("source_model", "=", source._name), ("source_id", "=", source.id)], limit=1
        )
        if existing:
            return existing
        company = self.env["res.company"].browse(vals["company_id"])
        account, account_note = _handback_account(self.env, company, role)
        pay = Execution.create(
            dict(
                vals,
                source_model=source._name,
                source_id=source.id,
                debit_account_id=account.id or False,
            )
        )
        pay.message_post(
            body="Raised by the finance hand-back of %s %s for treasury to check and release. "
            "Nothing is paid until treasury releases it and the bank confirms it.%s"
            % (source._description, source.display_name, " " + account_note if account_note else "")
        )
        return pay

    # ------------------------------------------------ M01 cancelled-order refund
    def _refund_method(self, order):
        """Back the way the money came: the M20 receipt's tender, the counter's
        cash; else a bank transfer (treasury may change it before release)."""
        if order.settlement_source == "m20_receipt" and order.invoice_ref:
            receipt = (
                self.env["fix.ar.receipt"]
                .sudo()
                .search(
                    [
                        ("state", "=", "confirmed"),
                        ("customer_id", "child_of", order.customer_id.commercial_partner_id.id),
                        "|",
                        ("name", "=", order.invoice_ref),
                        ("reference", "=", order.invoice_ref),
                    ],
                    limit=1,
                )
            )
            if receipt:
                return RECEIPT_REFUND_METHOD.get(receipt.method, "bank_transfer")
        if order.settlement_source == "counter":
            return "cash"
        return "bank_transfer"

    @api.model
    def consume_service_order_refund_requested(self, event: dict) -> dict:
        """R8 consumer of service_order.refund_requested (A02 audit M01-12/B2).

        A paid order was cancelled. The order's issued invoice gets a draft
        credit note for what it can still credit; with no invoice the
        customer's money goes back through a pending M50 instruction."""
        self._handback_assert_relay()
        label = "Refund hand-back"
        order, payload = self._handback_source(event, "fix.service.order", label)
        amount = order.amount_settled_bdt or 0.0
        # An amount that is not the record's is refused even on a replay.
        self._handback_check_amount(label, payload, "amount_bdt", amount)
        CreditNote = self.env["fix.credit.note"].sudo()
        key = [("source_model", "=", order._name), ("source_id", "=", order.id)]
        note = CreditNote.search(key, limit=1)
        if note:
            return {"model": note._name, "id": note.id, "created": False}
        pay = self.env["fix.payment.execution"].sudo().search(key, limit=1)
        if pay:
            return {"model": pay._name, "id": pay.id, "created": False}
        if order.state != "cancelled" or order.payment_settlement_state != "refund_due":
            raise UserError(
                "%s refused: order %s is %s with settlement '%s', not a cancelled order with "
                "a refund due." % (label, order.name, order.state, order.payment_settlement_state)
            )
        if amount <= 0.005:
            raise UserError("%s refused: order %s has no settled amount." % (label, order.name))
        company = order.company_id
        customer = order.customer_id.commercial_partner_id
        marker = "Finance hand-back (refund):"
        invoice = (
            self.env["fix.ar.invoice"]
            .sudo()
            .search(
                [
                    ("source_model", "=", order._name),
                    ("source_id", "=", order.id),
                    ("state", "in", ("issued", "paid")),
                ],
                limit=1,
            )
        )
        # The invoice must be the order customer's own: a refund is never
        # turned into a credit on somebody else's account.
        if invoice and invoice.customer_id.commercial_partner_id != customer:
            invoice = invoice.browse()
        creditable = round(invoice.total_payable - invoice.credited_amount, 2) if invoice else 0.0
        if creditable > 0.005:
            credit = min(amount, creditable)
            note = CreditNote.create(
                {
                    "company_id": invoice.company_id.id,
                    "operating_unit_id": invoice.operating_unit_id.id,
                    "invoice_id": invoice.id,
                    "customer_id": invoice.customer_id.id,
                    "amount": credit,
                    "reason_code": "order_cancelled",
                    "source_model": order._name,
                    "source_id": order.id,
                    "source_amount": credit,
                    "source_event_id": event.get("event_id") or False,
                }
            )
            rest = round(amount - credit, 2)
            body = (
                "draft credit note #%s for BDT %.2f against invoice %s, for finance to approve "
                "and issue. Paying the customer's resulting credit back in cash is a separate "
                "treasury instruction.%s"
                % (
                    note.id,
                    credit,
                    invoice.name,
                    " BDT %.2f of the settlement is more than the invoice can still credit; "
                    "finance refunds it separately." % rest
                    if rest > 0.005
                    else "",
                )
            )
            note.message_post(body="Raised from cancelled order %s: %s" % (order.name, body))
            self._handback_note(order, marker, body)
            return {"model": note._name, "id": note.id, "created": True}
        pay = self._handback_instruction(
            order,
            {
                "company_id": company.id,
                "operating_unit_id": self._handback_ou(
                    company, order.operating_unit_id, order.branch_id.operating_unit_id
                ).id,
                "payee": order.customer_id.name,
                "partner_id": order.customer_id.id,
                "amount": amount,
                "method": self._refund_method(order),
            },
            "customer_refund",
        )
        self._handback_note(
            order,
            marker,
            "pending treasury refund %s of BDT %.2f to %s (no invoice to credit). Treasury "
            "releases it; nothing is paid before then."
            % (pay.name, amount, order.customer_id.name),
        )
        return {"model": pay._name, "id": pay.id, "created": True}

    # ------------------------------------------------ M03 settled damage claim
    def _courier_finance_partner(self, courier):
        """The res.partner finance bills or pays for a courier: its own link
        when the courier master carries one, else the partner whose Reference
        is the courier code (one only). Never matched by name."""
        if not courier:
            return self.env["res.partner"]
        if "partner_id" in courier._fields and courier.partner_id:
            return courier.partner_id
        matches = (
            self.env["res.partner"]
            .sudo()
            .search([("ref", "=", courier.code), ("ref", "!=", False)], limit=2)
        )
        return matches if len(matches) == 1 else self.env["res.partner"]

    def _claim_payee(self, claim):
        """(payee name, partner, why-not) for the claimant of a claim."""
        consignment = claim.consignment_id.sudo()
        Partner = self.env["res.partner"]
        if claim.claimant == "customer":
            customer = consignment.service_order_id.customer_id
            if customer:
                return customer.name, customer, None
            return None, Partner, "consignment %s names no customer to pay" % consignment.name
        if claim.claimant == "rider":
            rider = consignment.rider_id
            if rider:
                return rider.name, rider.work_contact_id, None
            return None, Partner, "consignment %s names no rider to pay" % consignment.name
        if claim.claimant == "courier":
            courier = consignment.courier_partner_id
            if courier:
                return courier.name, self._courier_finance_partner(courier), None
            return None, Partner, "consignment %s names no courier to pay" % consignment.name
        return (
            None,
            Partner,
            "the claimant is the branch, so the loss stays inside the company (no external "
            "payee)",
        )

    @api.model
    def consume_damage_claim_settled(self, event: dict) -> dict:
        """R8 consumer of damage.claim.settled (A02 audit M03-6/B2).

        The settled payout becomes a pending M50 instruction to the claimant
        (an M19 payable that treasury releases). When the courier is liable,
        a draft M20 recovery invoice is raised to the courier for the same
        amount."""
        self._handback_assert_relay()
        label = "Damage-claim hand-back"
        claim, payload = self._handback_source(event, "fix.damage.claim", label)
        if claim.state != "settled":
            raise UserError(
                "%s refused: claim %s is %s, not settled." % (label, claim.name, claim.state)
            )
        amount = claim.settled_amount or 0.0
        if amount <= 0.005:
            raise UserError("%s refused: claim %s has no settled amount." % (label, claim.name))
        self._handback_check_amount(label, payload, "amount", amount)
        company = claim.company_id
        consignment = claim.consignment_id.sudo()
        ou = self._handback_ou(company, claim.operating_unit_id, consignment.operating_unit_id)
        key = [("source_model", "=", claim._name), ("source_id", "=", claim.id)]
        result = {"payable": False, "recovery": False}
        lines = []

        payable = self.env["fix.payment.execution"].sudo().search(key, limit=1)
        if not payable:
            payee, partner, why = self._claim_payee(claim)
            if payee:
                payable = self._handback_instruction(
                    claim,
                    {
                        "company_id": company.id,
                        "operating_unit_id": ou.id,
                        "payee": payee,
                        "partner_id": partner.id or False,
                        "currency_id": claim.currency_id.id,
                        "amount": amount,
                    },
                    "damage_claim_expense",
                )
                lines.append(
                    "pending treasury payout %s of BDT %.2f to %s, for treasury to release."
                    % (payable.name, amount, payee)
                )
            else:
                lines.append("no payout raised: %s." % why)
        result["payable"] = payable.id if payable else False

        Invoice = self.env["fix.ar.invoice"].sudo()
        recovery = Invoice.search(key, limit=1)
        courier = consignment.courier_partner_id
        if claim.liability == "carrier" and not recovery:
            partner = self._courier_finance_partner(courier)
            if not courier:
                lines.append("the carrier is liable but the consignment names no courier.")
            elif not partner:
                lines.append(
                    "recovery of BDT %.2f from %s NOT raised: the courier has no finance "
                    "partner (a contact whose Reference is the courier code %s). Create it and "
                    "raise the recovery in M20." % (amount, courier.name, courier.code)
                )
            else:
                recovery = Invoice.create(
                    {
                        "company_id": company.id,
                        "operating_unit_id": ou.id,
                        "branch_id": (consignment.dest_branch_id or consignment.origin_branch_id).id
                        or False,
                        "customer_id": partner.id,
                        "currency_id": claim.currency_id.id,
                        "source_model": claim._name,
                        "source_id": claim.id,
                        "manual_reason": "Courier damage recovery, claim %s" % claim.name,
                        "line_ids": [
                            Command.create(
                                {
                                    "description": "Transit damage recovery: claim %s, "
                                    "consignment %s" % (claim.name, consignment.name),
                                    "taxable_amount": amount,
                                    "vat_amount": 0.0,
                                    "line_total": amount,
                                }
                            )
                        ],
                    }
                )
                recovery.message_post(
                    body="Draft recovery raised from settled damage claim %s (the courier is "
                    "liable), for finance to review and issue." % claim.name
                )
                lines.append(
                    "draft recovery invoice #%s of BDT %.2f to %s, for finance to issue."
                    % (recovery.id, amount, partner.name)
                )
        elif claim.liability == "shared":
            lines.append(
                "liability is shared and the courier's share is not recorded, so no recovery "
                "was raised; finance raises it in M20 once the share is agreed."
            )
        result["recovery"] = recovery.id if recovery else False
        if lines:
            self._handback_note(claim, "Finance hand-back (damage claim):", " ".join(lines))
        return result

    # ------------------------------------------------ M05 applied SLA credit
    def _sla_invoice(self, credit, customer, amount):
        """The latest issued MSP invoice of the credit's contract that can take
        the whole credit (subscription billing), else none."""
        Invoice = self.env["fix.ar.invoice"].sudo()
        if "fix.subscription.charge" not in self.env:
            return Invoice
        charges = (
            self.env["fix.subscription.charge"]
            .sudo()
            .search(
                [
                    ("subscription_id.contract_id", "=", credit.msp_contract_id.contract_id.id),
                    ("invoice_id.state", "in", ("issued", "paid")),
                    ("company_id", "=", credit.company_id.id),
                ],
                order="period_start desc, id desc",
            )
        )
        for invoice in charges.mapped("invoice_id"):
            if invoice.customer_id.commercial_partner_id != customer.commercial_partner_id:
                continue
            if invoice.total_payable - invoice.credited_amount + 0.005 >= amount:
                return invoice
        return Invoice

    @api.model
    def consume_msp_sla_credit_applied(self, event: dict) -> dict:
        """R8 consumer of msp.sla_credit_applied (A02 audit 7c/B2).

        The applied credit becomes a draft M20 credit note to the MSP
        customer, against the contract's latest invoice that can take it. With
        no such invoice it stays a draft for the customer; finance links the
        invoice before it can be submitted or issued."""
        self._handback_assert_relay()
        label = "SLA-credit hand-back"
        credit, payload = self._handback_source(event, "fix.msp.sla.credit", label)
        amount = credit.approved_amount or 0.0
        self._handback_check_amount(label, payload, "amount", amount)
        CreditNote = self.env["fix.credit.note"].sudo()
        note = CreditNote.search(
            [("source_model", "=", credit._name), ("source_id", "=", credit.id)], limit=1
        )
        if note:
            return {"model": note._name, "id": note.id, "created": False}
        if credit.state != "applied":
            raise UserError(
                "%s refused: credit %s is %s, not applied."
                % (label, credit.display_name, credit.state)
            )
        if amount <= 0.005:
            raise UserError("%s refused: credit %s has no approved amount." % (label, credit.id))
        if abs((credit.credit_amount or 0.0) - amount) > 0.005:
            raise UserError(
                "%s refused: credit %s was approved at BDT %.2f but stands at BDT %.2f."
                % (label, credit.id, amount, credit.credit_amount or 0.0)
            )
        msp = credit.msp_contract_id
        contract = msp.contract_id
        customer = contract.customer_id
        if not customer:
            raise UserError(
                "%s refused: contract %s names no customer." % (label, contract.display_name)
            )
        company = credit.company_id
        invoice = self._sla_invoice(credit, customer, amount)
        note = CreditNote.create(
            {
                "company_id": company.id,
                "operating_unit_id": self._handback_ou(
                    company,
                    invoice.operating_unit_id,
                    credit.operating_unit_id,
                    msp.operating_unit_id,
                    contract.operating_unit_id,
                ).id,
                "invoice_id": invoice.id or False,
                "customer_id": (invoice.customer_id or customer).id,
                "amount": amount,
                "reason_code": "sla_credit",
                "source_model": credit._name,
                "source_id": credit.id,
                "source_amount": amount,
                "source_event_id": event.get("event_id") or False,
            }
        )
        where = (
            "against invoice %s" % invoice.name
            if invoice
            else "with no invoice yet: finance links the invoice it credits before it can be "
            "submitted"
        )
        body = (
            "draft credit note #%s for BDT %.2f (%s, %s) %s, for finance to approve and issue."
            % (
                note.id,
                amount,
                msp.name,
                credit.period_label,
                where,
            )
        )
        note.message_post(body="Raised from applied SLA credit: %s" % body)
        self._handback_note(credit, "Finance hand-back (SLA credit):", body)
        return {"model": note._name, "id": note.id, "created": True}


class FixCreditNoteHandback(models.Model):
    """A hand-back credit note carries its source, its customer and the
    amount it may not exceed. One raised before its invoice exists (an SLA
    credit) waits in draft until finance links the invoice."""

    _inherit = "fix.credit.note"

    invoice_id = fields.Many2one(
        required=False,
        help="The invoice credited. A hand-back credit note may start without one; it is "
        "linked before it is submitted.",
    )
    reason_code = fields.Selection(
        selection_add=[
            ("order_cancelled", "Order Cancelled (Refund)"),
            ("sla_credit", "MSP SLA Credit"),
        ],
        ondelete={
            "order_cancelled": lambda notes: notes.write({"reason_code": "return"}),
            "sla_credit": lambda notes: notes.write({"reason_code": "service_failure"}),
        },
    )
    customer_id = fields.Many2one(
        "res.partner", string="Customer", readonly=True, index=True, ondelete="restrict"
    )
    source_model = fields.Char(string="Hand-back Source", readonly=True, index=True, copy=False)
    source_id = fields.Integer(string="Hand-back Source ID", readonly=True, index=True, copy=False)
    source_amount = fields.Monetary(
        string="Hand-back Amount",
        currency_field="currency_id",
        readonly=True,
        copy=False,
        help="The amount the source record handed back; the credit cannot exceed it.",
    )
    source_event_id = fields.Char(string="Hand-back Event", readonly=True, copy=False)

    _handback_source_unique = models.Constraint(
        "UNIQUE (source_model, source_id)",
        "One hand-back credit note per source record (A02 audit B2)",
    )

    _HANDBACK_FIELDS = frozenset(
        {"customer_id", "source_model", "source_id", "source_amount", "source_event_id"}
    )

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.su:
            for vals in vals_list:
                if self._HANDBACK_FIELDS & {k for k, v in vals.items() if v}:
                    raise UserError("A hand-back credit note %s." % RELAY_ONLY)
        return super().create(vals_list)

    def write(self, vals):
        if not self.env.su and self._HANDBACK_FIELDS & set(vals):
            raise UserError("The hand-back source of a credit note %s." % RELAY_ONLY)
        return super().write(vals)

    @api.constrains("invoice_id", "customer_id", "source_model", "amount", "source_amount")
    def _check_handback(self):
        for note in self:
            if not note.invoice_id and not (note.source_model and note.customer_id):
                raise ValidationError("A credit note needs the invoice it credits.")
            if not note.source_model:
                continue
            if note.amount > (note.source_amount or 0.0) + 0.005:
                raise ValidationError(
                    "Credit note #%s cannot exceed the BDT %.2f its source handed back."
                    % (note.id, note.source_amount or 0.0)
                )
            if (
                note.invoice_id
                and note.customer_id
                and note.invoice_id.customer_id.commercial_partner_id
                != note.customer_id.commercial_partner_id
            ):
                raise ValidationError(
                    "Credit note #%s is for %s; it cannot credit an invoice of %s."
                    % (note.id, note.customer_id.name, note.invoice_id.customer_id.name)
                )

    def _handback_require_invoice(self, step):
        for note in self:
            if not note.invoice_id:
                raise UserError(
                    "Credit note #%s has no invoice yet: link the invoice it credits before %s."
                    % (note.id, step)
                )

    def action_submit(self):
        self._handback_require_invoice("submitting it")
        return super().action_submit()

    def action_approve(self):
        self._handback_require_invoice("approving it")
        return super().action_approve()

    def action_issue(self):
        self._handback_require_invoice("issuing it")
        return super().action_issue()


class FixPaymentExecutionHandback(models.Model):
    """An M50 instruction raised by a hand-back is pinned to its source: the
    payee, the source and the amount ceiling are the relay's, and the money
    goes only to the payee's own account."""

    _inherit = "fix.payment.execution"

    _HANDBACK_LOCKED = frozenset({"source_model", "source_id", "payee", "partner_id"})

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.su and any(
            vals.get("source_model") in HANDBACK_PAYMENT_SOURCES for vals in vals_list
        ):
            raise UserError("A hand-back payment instruction %s." % RELAY_ONLY)
        return super().create(vals_list)

    def write(self, vals):
        touches_handback = vals.get("source_model") in HANDBACK_PAYMENT_SOURCES or (
            self._HANDBACK_LOCKED & set(vals)
            and any(p.source_model in HANDBACK_PAYMENT_SOURCES for p in self)
        )
        if touches_handback and not self.env.su:
            raise UserError("The source and payee of a hand-back instruction %s." % RELAY_ONLY)
        return super().write(vals)

    @api.constrains("amount", "source_model", "source_id", "partner_id", "partner_bank_id")
    def _check_handback_instruction(self):
        for pay in self.filtered(lambda p: p.source_model in HANDBACK_PAYMENT_SOURCES):
            source = self.env[pay.source_model].sudo().browse(pay.source_id).exists()
            ceiling = source[HANDBACK_PAYMENT_SOURCES[pay.source_model]] if source else 0.0
            if pay.amount > (ceiling or 0.0) + 0.005:
                raise ValidationError(
                    "%s cannot exceed the BDT %.2f its source handed back."
                    % (pay.name, ceiling or 0.0)
                )
            bank_owner = pay.partner_bank_id.partner_id.commercial_partner_id
            if bank_owner and pay.partner_id and bank_owner != pay.partner_id.commercial_partner_id:
                raise ValidationError(
                    "%s pays %s: the account or wallet must be the payee's own."
                    % (pay.name, pay.partner_id.name)
                )


class FixArInvoiceHandback(models.Model):
    """A courier recovery raised from a damage claim credits recovery income,
    not service revenue."""

    _inherit = "fix.ar.invoice"

    def _revenue_role(self) -> str:
        self.ensure_one()
        if self.source_model == "fix.damage.claim":
            return "claim_recovery"
        return super()._revenue_role()

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.su and any(
            vals.get("source_model") == "fix.damage.claim" for vals in vals_list
        ):
            raise UserError("A damage-claim recovery invoice %s." % RELAY_ONLY)
        return super().create(vals_list)

    def write(self, vals):
        if not self.env.su and vals.get("source_model") == "fix.damage.claim":
            raise UserError("A damage-claim recovery invoice %s." % RELAY_ONLY)
        return super().write(vals)
