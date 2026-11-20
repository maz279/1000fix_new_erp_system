# ap_lc_settlement — a supplier paid through a letter of credit (A06 ERP audit,
# owner decision D6; findings X09 / M44-11).
#
# The bank remits an import supplier under an LC: M44 records the remittance
# and its bank, margin and exchange legs. Until now the remittance debited an
# "LC clearing" account nothing ever credited, and AP knew nothing of it, so
# the supplier's bill stayed payable and could be paid a second time.
#
# Now the remittance SETTLES the supplier in AP:
#   - against the supplier's posted, unpaid bills in the remittance's scope
#     (its purchase order, or the bills the caller names) it debits trade
#     payables and lowers what each bill still pays (lc_settled_amount ->
#     total_payable); a bill settled in full is Paid and leaves every payment
#     run and Request Payment;
#   - what is left (all of it when no bill exists yet) is a supplier ADVANCE:
#     debit "advances to suppliers" (cd_ap_ext.account_code.supplier_advance,
#     10255 Advance for Purchase on the legacy chart), which the bill takes
#     back when it posts, exactly like an M16 proforma advance.
# A bill already in a payment run (payment in flight) is refused: treasury
# settles it, or the run is cancelled first. Nothing here moves money: the
# caller posts ONE balanced entry with the legs returned and attaches it.
from odoo import api, fields, models
from odoo.exceptions import UserError

from .ap_gl import ap_account

PARAM_SUPPLIER_ADVANCE = "cd_ap_ext.account_code.supplier_advance"
# D6: the legacy chart's 10255 Advance for Purchase. Set once when nobody has
# named the account; a configured value is never overwritten.
DEFAULT_SUPPLIER_ADVANCE_CODE = "10255"


def _q(value):
    return round(value or 0.0, 2)


class FixApLcSettlement(models.Model):
    """One leg of a remittance under an LC: the part that settled one bill,
    or the part held as a supplier advance until a bill takes it back."""

    _name = "fix.ap.lc.settlement"
    _description = "Supplier Settlement by LC Remittance"
    _order = "date, id"

    company_id = fields.Many2one("res.company", required=True, index=True, readonly=True)
    operating_unit_id = fields.Many2one("operating.unit", index=True, readonly=True)
    vendor_id = fields.Many2one(
        "res.partner", string="Supplier", required=True, index=True, readonly=True
    )
    purchase_order_id = fields.Many2one(
        "fix.purchase.order", string="Purchase Order", index=True, readonly=True
    )
    scope_key = fields.Char(
        string="Remittance Scope",
        index=True,
        readonly=True,
        help="What the remittance pays for (e.g. 'fix.import.order,12'): the bills of that "
        "scope take an advance back.",
    )
    source_model = fields.Char(readonly=True)
    source_id = fields.Integer(readonly=True, index=True)
    source_ref = fields.Char(string="Remittance", readonly=True)
    kind = fields.Selection(
        [("bill", "Settled a bill"), ("advance", "Supplier advance")],
        required=True,
        readonly=True,
    )
    bill_id = fields.Many2one(
        "fix.vendor.invoice", string="Bill Settled", index=True, readonly=True
    )
    currency_id = fields.Many2one("res.currency", required=True, readonly=True)
    amount = fields.Monetary(currency_field="currency_id", readonly=True)
    amount_bdt = fields.Float(string="Amount (BDT)", readonly=True)
    date = fields.Date(required=True, readonly=True)
    move_id = fields.Many2one("account.move", string="Remittance Entry", readonly=True, index=True)
    application_ids = fields.One2many(
        "fix.ap.lc.advance.application", "settlement_id", string="Taken Back on Bills"
    )
    applied_amount = fields.Monetary(
        currency_field="currency_id", compute="_compute_applied", string="Taken Back"
    )
    remaining_amount = fields.Monetary(
        currency_field="currency_id", compute="_compute_applied", string="Still to Take Back"
    )

    _amount_positive = models.Constraint("CHECK (amount > 0)", "A settlement is positive")

    @api.depends("amount", "kind", "application_ids.amount")
    def _compute_applied(self):
        for rec in self:
            applied = _q(sum(rec.application_ids.mapped("amount")))
            rec.applied_amount = applied
            rec.remaining_amount = _q(rec.amount - applied) if rec.kind == "advance" else 0.0

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.su:
            raise UserError("An LC settlement is written by the remittance that makes it.")
        return super().create(vals_list)

    def write(self, vals):
        if not self.env.su:
            raise UserError("An LC settlement is evidence and is not edited.")
        return super().write(vals)

    def unlink(self):
        raise UserError("An LC settlement is evidence and cannot be deleted.")

    # ------------------------------------------------------------------ API
    @api.model
    def _fix_settle(
        self,
        company,
        operating_unit,
        vendor,
        currency,
        amount,
        amount_bdt,
        on_date,
        ref,
        source,
        purchase_order=None,
        scope_key=None,
        bills=None,
    ):
        """Settle `amount` (in `currency`; `amount_bdt` its BDT value at the
        rate the caller books the payable at) for `vendor`. Returns
        (settlements, legs): legs are the DEBIT lines of the caller's entry,
        [(account, label, bdt_amount, partner)]. `source` is the remittance
        record. Bills in scope: `bills`, else the purchase order's bills."""
        if (amount or 0.0) <= 0:
            raise UserError("An LC remittance settles a positive amount.")
        su = self.sudo()
        partner = vendor.commercial_partner_id
        Bill = self.env["fix.vendor.invoice"].sudo()
        if bills is None:
            bills = Bill.browse()
            if purchase_order:
                bills = Bill.search([("requisition_id", "=", purchase_order.id)])
        bills = bills.sudo().filtered(
            lambda b: b.company_id == company
            and b.vendor_id.commercial_partner_id == partner
            and b.approval_state == "approved"
            and b.move_id
            and b.payment_state != "paid"
        )
        in_flight = bills.filtered(lambda b: b.payment_state == "in_run")
        if in_flight:
            raise UserError(
                "Bill %s of %s is already in a payment run: the LC remittance %s would pay it a "
                "second time. Cancel the run (or let treasury settle it) first."
                % (in_flight[0].invoice_ref, partner.name, ref)
            )
        foreign = bills.filtered(lambda b: b.currency_id != currency)
        if foreign:
            raise UserError(
                "Bill %s is in %s but the LC remittance %s is in %s: it cannot be settled by it."
                % (foreign[0].invoice_ref, foreign[0].currency_id.name, ref, currency.name)
            )
        left = _q(amount)
        left_bdt = _q(amount_bdt)
        rows, legs = [], []
        common = {
            "company_id": company.id,
            "operating_unit_id": operating_unit.id if operating_unit else False,
            "vendor_id": partner.id,
            "purchase_order_id": purchase_order.id if purchase_order else False,
            "scope_key": scope_key or False,
            "source_model": source._name,
            "source_id": source.id,
            "source_ref": ref,
            "currency_id": currency.id,
            "date": on_date,
        }
        for bill in bills.sorted(lambda b: (b.invoice_date, b.id)):
            if left <= 0.005:
                break
            outstanding = _q(bill.total_payable)
            if outstanding <= 0.005:
                continue
            take = _q(min(outstanding, left))
            take_bdt = _q(left_bdt * take / left) if left else 0.0
            rows.append(
                dict(common, kind="bill", bill_id=bill.id, amount=take, amount_bdt=take_bdt)
            )
            legs.append(
                (
                    ap_account(self.env, company, "ap"),
                    "LC remittance %s settles bill %s" % (ref, bill.invoice_ref),
                    take_bdt,
                    partner,
                )
            )
            bill._guarded().write({"lc_settled_amount": _q(bill.lc_settled_amount + take)})
            if bill.total_payable <= 0.005:
                bill._guarded().write({"payment_state": "paid"})
            bill.message_post(
                body="Settled %.2f %s by LC remittance %s." % (take, currency.name, ref)
            )
            left = _q(left - take)
            left_bdt = _q(left_bdt - take_bdt)
        if left > 0.005:
            rows.append(dict(common, kind="advance", amount=left, amount_bdt=left_bdt))
            legs.append(
                (
                    ap_account(self.env, company, "supplier_advance"),
                    "LC remittance %s: advance to %s" % (ref, partner.name),
                    left_bdt,
                    partner,
                )
            )
        return su.create(rows), legs

    def _fix_attach_move(self, move):
        self.sudo().write({"move_id": move.id or False})

    @api.model
    def _fix_default_params(self):
        """D6: the supplier advance account defaults to 10255 Advance for
        Purchase, set only when no account is configured."""
        icp = self.env["ir.config_parameter"].sudo()
        if not icp.get_param(PARAM_SUPPLIER_ADVANCE):
            icp.set_param(PARAM_SUPPLIER_ADVANCE, DEFAULT_SUPPLIER_ADVANCE_CODE)
        return True


class FixApLcAdvanceApplication(models.Model):
    """One take-back of an LC advance on one bill."""

    _name = "fix.ap.lc.advance.application"
    _description = "LC Advance Taken Back on a Bill"
    _order = "id"

    settlement_id = fields.Many2one(
        "fix.ap.lc.settlement", required=True, ondelete="restrict", index=True
    )
    bill_id = fields.Many2one("fix.vendor.invoice", required=True, ondelete="restrict", index=True)
    company_id = fields.Many2one(related="settlement_id.company_id", store=True, index=True)
    currency_id = fields.Many2one(related="settlement_id.currency_id")
    amount = fields.Monetary(currency_field="currency_id", required=True)

    _amount_positive = models.Constraint("CHECK (amount > 0)", "A take-back must be positive")

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.su:
            raise UserError("An advance take-back is written by the bill's posting.")
        return super().create(vals_list)

    def write(self, vals):
        raise UserError("An advance take-back is evidence and is not edited.")

    def unlink(self):
        raise UserError("An advance take-back is evidence and cannot be deleted.")


class FixVendorInvoiceLcSettlement(models.Model):
    _inherit = "fix.vendor.invoice"

    lc_settled_amount = fields.Monetary(
        string="Settled by LC",
        currency_field="currency_id",
        readonly=True,
        copy=False,
        help="Paid to the supplier by LC remittances after the bill posted (M44).",
    )
    lc_settlement_ids = fields.One2many("fix.ap.lc.settlement", "bill_id", string="LC Settlements")
    lc_advance_application_ids = fields.One2many(
        "fix.ap.lc.advance.application", "bill_id", string="LC Advances Taken Back"
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"lc_settled_amount"}

    @api.depends("lc_settled_amount")
    def _compute_totals(self) -> None:
        super()._compute_totals()
        for inv in self:
            if inv.lc_settled_amount:
                inv.total_payable = _q(inv.total_payable - inv.lc_settled_amount)

    def _fix_lc_advance_scope(self):
        """The LC advances this bill may take back: its purchase order's.
        Modules that pay without a PO (M44 imports) widen the scope."""
        self.ensure_one()
        if self.requisition_id:
            return [("purchase_order_id", "=", self.requisition_id.id)]
        return []

    def _apply_supplier_advances(self):
        super()._apply_supplier_advances()
        self._apply_lc_advances()

    def _post_approved_bill(self):
        res = super()._post_approved_bill()
        # an LC advance that covers the whole bill leaves nothing to pay
        if self.move_id and self.payment_state == "not_paid" and self.total_payable <= 0.005:
            self._guarded().write({"payment_state": "paid"})
        return res

    def _apply_lc_advances(self):
        """At posting: the supplier's LC advances in the bill's scope reduce
        what it pays (credit advances to suppliers instead of payables), oldest
        first, never more than its own payable."""
        self.ensure_one()
        if self.lc_advance_application_ids:
            return
        scope = self._fix_lc_advance_scope()
        if not scope:
            return
        advances = (
            self.env["fix.ap.lc.settlement"]
            .sudo()
            .search(
                [
                    *scope,
                    ("kind", "=", "advance"),
                    ("company_id", "=", self.company_id.id),
                    ("vendor_id", "=", self.vendor_id.commercial_partner_id.id),
                    ("move_id", "!=", False),
                ],
                order="date, id",
            )
            .filtered(lambda a: a.remaining_amount > 0.005)
        )
        if not advances:
            return
        if advances.mapped("currency_id") != self.currency_id:
            raise UserError(
                "Bill %s is in %s but the LC advances paid to %s are in %s: they cannot be taken "
                "back on it."
                % (
                    self.invoice_ref,
                    self.currency_id.name,
                    self.vendor_id.display_name,
                    ", ".join(advances.mapped("currency_id.name")),
                )
            )
        room = _q(self.total_payable)
        take = []
        for adv in advances:
            if room <= 0.005:
                break
            amount = _q(min(adv.remaining_amount, room))
            take.append({"settlement_id": adv.id, "bill_id": self.id, "amount": amount})
            room = _q(room - amount)
        if not take:
            return
        self.env["fix.ap.lc.advance.application"].sudo().create(take)
        lc_total = _q(sum(row["amount"] for row in take))
        self._guarded().write({"advance_applied": _q((self.advance_applied or 0.0) + lc_total)})
        self.message_post(
            body="LC advances of %.2f %s taken back on this bill."
            % (lc_total, self.currency_id.name)
        )
