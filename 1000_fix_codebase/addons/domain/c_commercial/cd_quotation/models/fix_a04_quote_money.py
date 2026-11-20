# A04 ERP audit (20 Nov 2026, stream B2): the M36 quotation and tender money.
#
#   M36-F2  VAT on a quotation is M51's determination per line (the tax
#           invoice's own rule); vat_rate is no longer typed. What the
#           billing plan invoices never exceeds the accepted total.
#   M36-F4  an advance received on a contract / subscription quotation is
#           applied to that contract's / subscription's invoices.
#   M36-F5  quotation.declined has a consumer: the decline is closed out (the
#           M01 estimate is declined and the device's return is scheduled).
#   M36-F7  tender.variation_approved has a consumer: the approved variation
#           becomes an amendment of the tender's contract.
from datetime import timedelta
from decimal import ROUND_HALF_UP, Decimal
from types import SimpleNamespace

from dateutil.relativedelta import relativedelta  # noqa: F401
from odoo import api, fields, models
from odoo.addons.cd_billing_engine.models.fix_billing_engine import allocate_discount
from odoo.exceptions import AccessError, UserError

from .fix_quote_ops import estimate_untaxed

TWO = Decimal("0.01")


class FixQuotationMoney(models.Model):
    _inherit = "fix.quotation"

    # M36-F2: the rate is what M51 determines on the quoted lines (several
    # rates give the effective rate); never typed.
    vat_rate = fields.Float(
        string="VAT Rate (%)",
        compute="_compute_statutory_margins",
        store=True,
        readonly=True,
        digits=(5, 2),
    )
    acceptance_method = fields.Selection(
        selection_add=[("tender_award", "Tender award (Notification of Award)")],
        ondelete={"tender_award": "set null"},
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"vat_rate"}

    # ---- M51 per line -----------------------------------------------------------
    def _fix_quote_determination(self):
        """[(line, det)] - M51's determination of each priced line, the
        overall discount spread pro rata, as the tax invoice will state it.
        Empty when there are no priced lines."""
        self.ensure_one()
        lines = (
            self._scope_lines() if hasattr(self, "_scope_lines") else self.env["fix.quotation.line"]
        )
        if not lines:
            return []
        nets = [Decimal(str(ln.subtotal or 0.0)).quantize(TWO, ROUND_HALF_UP) for ln in lines]
        overall = Decimal(str(self.discount_amount or 0.0)).quantize(TWO, ROUND_HALF_UP)
        overall = min(overall, sum(nets, Decimal("0")))
        shares = (
            allocate_discount(nets, overall)
            if sum(nets, Decimal("0"))
            else [Decimal("0")] * len(nets)
        )
        frame = SimpleNamespace(
            invoice_date=fields.Date.context_today(self),
            company_id=self.company_id or self.env.company,
        )
        Line = self.env["fix.ar.invoice.line"].sudo()
        Treatment = self.env["fix.vat.treatment"]
        out = []
        for line, share in zip(lines, shares, strict=True):
            disc = Decimal(str(line.discount_amount or 0.0)) + share
            det = Line._fix_determined(
                frame,
                0.0,
                line.product_id,
                Treatment,
                qty=line.quantity or 0.0,
                unit_price=line.unit_price or 0.0,
                discount=float(disc),
            )
            out.append((line, det))
        return out

    def _fix_standard_rate(self) -> float:
        self.ensure_one()
        frame = SimpleNamespace(
            invoice_date=fields.Date.context_today(self),
            company_id=self.company_id or self.env.company,
        )
        det = (
            self.env["fix.ar.invoice.line"]
            .sudo()
            ._fix_determined(
                frame, 100.0, self.env["product.product"], self.env["fix.vat.treatment"]
            )
        )
        return float(det.rate or 0.0)

    @api.depends(
        "value",
        "cost_amount",
        "tds_rate",
        "discount_amount",
        "estimate_id.grand_total",
        "estimate_id.vat_amount",
        "estimate_id.vat_rate",
        "line_ids.subtotal",
        "line_ids.quantity",
        "line_ids.unit_price",
        "line_ids.discount_pct",
        "line_ids.product_id",
        "line_ids.is_optional",
        "line_ids.display_type",
    )
    def _compute_statutory_margins(self):
        for rec in self:
            val = rec.value or 0.0
            est = rec.estimate_id.sudo()
            if est and abs(val - estimate_untaxed(est)) <= 0.005:
                # Quoting the estimate as it stands: its own VAT, to the
                # paisa, so the total equals the estimate (and the M01
                # invoice, A02's estimate -> invoice equality).
                vat = round((est.grand_total or 0.0) - val, 2)
                rate = est.vat_rate or 0.0
            else:
                try:
                    determined = rec._fix_quote_determination()
                    if determined:
                        vat = round(sum(float(d.vat_amount) for _l, d in determined), 2)
                        rates = {float(d.rate) for _l, d in determined}
                        rate = (
                            rates.pop()
                            if len(rates) == 1
                            else (round(vat / val * 100.0, 4) if val else 0.0)
                        )
                    else:
                        rate = rec._fix_standard_rate()
                        vat = round(val * rate / 100.0, 2)
                except UserError:
                    # M51 refused (no rate in force): the quotation shows no
                    # VAT and cannot be issued (readiness says why)
                    vat, rate = 0.0, 0.0
            rec.vat_rate = rate
            rec.vat_amount = vat
            rec.amount_total = round(val + vat, 2)
            cost = rec.cost_amount or 0.0
            rec.tds_amount = round(val * ((rec.tds_rate or 0.0) / 100.0), 2)
            known = bool(val and cost > 0.0)
            rec.margin_known = known
            if not known:
                rec.pretax_margin_bdt = rec.net_cash_margin_bdt = 0.0
                rec.net_cash_margin_pct = rec.margin_pct = 0.0
                continue
            rec.pretax_margin_bdt = round(val - cost, 2)
            net_cash = round(val - cost - rec.tds_amount, 2)
            rec.net_cash_margin_bdt = net_cash
            rec.net_cash_margin_pct = round((net_cash / val) * 100.0, 2)
            rec.margin_pct = round(((val - cost) / val) * 100.0, 2)

    def _readiness_problems(self) -> list:
        problems = super()._readiness_problems()
        if (self.value or 0.0) > 0.0 and not self.vat_rate and not self.estimate_id:
            try:
                self._fix_standard_rate()
            except UserError as exc:
                problems.append(
                    "VAT cannot be determined (M51): %s" % (exc.args[0] if exc.args else exc)
                )
        return problems

    # ---- M36-F2: billing-plan invoices never exceed the accepted total ------------
    def _fix_invoiced_total(self, exclude=None):
        self.ensure_one()
        invoices = self.billing_line_ids.mapped("invoice_id").filtered(
            lambda i: i.state != "cancelled"
        )
        if exclude:
            invoices -= exclude
        return round(sum(invoices.mapped("total_payable")), 2)


class FixQuotationBillingLineMoney(models.Model):
    _inherit = "fix.quotation.billing.line"

    def action_invoice(self):
        """M36-F2 (BRU-QTE-10 / AUT-QTE-15): the plan's invoices total what
        the customer accepted: an invoice that would take the plan above the
        accepted total (incl. VAT, beyond a paisa of rounding per share) is
        refused."""
        res = True
        for line in self:
            quote = line.quotation_id.sudo()
            plan = quote.billing_line_ids.filtered(lambda b: b.kind != "recurring").sorted(
                lambda b: (b.sequence, b.id)
            )
            res = super(FixQuotationBillingLineMoney, line).action_invoice()
            invoice = line.invoice_id
            accepted = quote.accepted_total or quote.amount_total or 0.0
            if not invoice or accepted <= 0.0:
                continue
            total = quote._fix_invoiced_total()
            if total > accepted + 0.01 * max(len(plan), 1):
                raise UserError(
                    "Quotation %s: the billing plan would invoice BDT %.2f, above the BDT %.2f "
                    "the customer accepted (BRU-QTE-10). Correct the plan or the quotation."
                    % (quote.name, total, accepted)
                )
        return res


class FixArInvoiceAdvanceContract(models.Model):
    _inherit = "fix.ar.invoice"

    def _fix_quotation_for_advances(self):
        """M36-F4: a contract period's or a subscription charge's invoice
        bills the accepted quotation the contract / subscription came from,
        so the advance received on that quotation is applied to it."""
        quote = super()._fix_quotation_for_advances()
        if quote:
            return quote
        Quote = self.env["fix.quotation"].sudo()
        source = (
            self.env[self.source_model].sudo().browse(self.source_id).exists()
            if self.source_model in self.env and self.source_id and self.source_id > 0
            else None
        )
        if not source:
            return Quote.browse()
        if self.source_model == "fix.contract.billing.period":
            q = source.contract_id.quotation_id
            return q if q.state == "accepted" else Quote.browse()
        if self.source_model == "fix.subscription.charge" and "subscription_id" in source._fields:
            sub = source.subscription_id
            quote_id = sub["source_quote_id"] if "source_quote_id" in sub._fields else 0
            q = Quote.browse(quote_id).exists() if quote_id else Quote.browse()
            return q if q and q.state == "accepted" else Quote.browse()
        return Quote.browse()


class FixQuotationConsumers(models.AbstractModel):
    """R8 consumers of the M36 events that need someone to act."""

    _name = "fix.a04.quotation.consumers"
    _description = "A04 Quotation / Tender Event Consumers"

    def _record(self, event, model, label):
        if not self.env.su:
            raise AccessError("Quotation consumers run only from the event relay.")
        aggregate = event.get("aggregate")
        if aggregate and aggregate != model:
            raise UserError(
                "%s refused: the event's aggregate is %s, not %s." % (label, aggregate, model)
            )
        try:
            res_id = int(event.get("aggregate_id") or 0)
        except (TypeError, ValueError):
            res_id = 0
        rec = self.env[model].sudo().browse(res_id).exists() if res_id else None
        if not rec:
            raise UserError("%s refused: there is no %s #%s." % (label, model, res_id))
        return rec

    # ---- M36-F5: a declined quotation is closed out --------------------------------
    @api.model
    def consume_quotation_declined(self, event: dict) -> dict:
        label = "Quotation decline hand-off"
        quote = self._record(event, "fix.quotation", label)
        if quote.state != "declined":
            raise UserError(
                "%s refused: %s is %s, not declined." % (label, quote.name, quote.state)
            )
        if quote.handoff_ids.filtered(
            lambda h: h.kind == "task" and (h.note or "").startswith("Declined")
        ):
            return {"model": quote._name, "id": quote.id, "created": False}
        deadline = fields.Date.context_today(self) + timedelta(days=1)
        order = quote.estimate_id.order_id.sudo() if quote.estimate_id else None
        if quote.quote_type == "service" and order:
            est = quote.estimate_id.sudo()
            if est.quotation_state in ("quoted", "negotiating"):
                est.action_decline(quote.decline_reason or "Quotation %s declined" % quote.name)
            # the M01 side charges the diagnostic fee when the order is
            # cancelled as 'Customer Rejected the Estimate' (A02 afa7b1ca);
            # this hands the counter the device's return to do that
            user = order.create_uid
            if user and user.active and not user.share:
                order.activity_schedule(
                    "mail.mail_activity_data_todo",
                    date_deadline=deadline,
                    summary="Quotation %s declined: return the device" % quote.name,
                    note="The customer declined (%s). Return the device unrepaired and close "
                    "the order as 'Customer Rejected the Estimate' (the diagnostic fee is "
                    "charged then)." % (quote.decline_reason or ""),
                    user_id=user.id,
                )
            quote._log_handoff("task", order, "pending", "Declined: device return scheduled")
            return {"model": order._name, "id": order.id, "created": True}
        owner = quote.create_uid if quote.create_uid and quote.create_uid.active else self.env.user
        quote.activity_schedule(
            "mail.mail_activity_data_todo",
            date_deadline=deadline,
            summary="Quotation %s declined: close out" % quote.name,
            note="Record the loss with the customer, release any reserved stock or "
            "resources, and decide on a revision (%s)." % (quote.decline_reason or ""),
            user_id=owner.id,
        )
        quote._log_handoff("task", None, "pending", "Declined: close-out scheduled")
        return {"model": quote._name, "id": quote.id, "created": True}

    # ---- M36-F7: an approved variation amends the contract ------------------------
    @api.model
    def consume_tender_variation_approved(self, event: dict) -> dict:
        label = "Tender variation hand-off"
        variation = self._record(event, "fix.tender.variation", label)
        if variation.state != "approved":
            raise UserError(
                "%s refused: variation %s is %s." % (label, variation.name, variation.state)
            )
        if variation.amendment_id or variation.applied_to_contract:
            return {"model": variation._name, "id": variation.id, "created": False}
        tender = variation.tender_id
        contract = (
            self.env["fix.contract"].sudo().browse(tender.converted_res_id).exists()
            if tender.converted_res_model == "fix.contract"
            else None
        )
        if not contract:
            raise UserError("%s refused: tender %s has no contract yet." % (label, tender.name))
        quote = tender.quotation_id.sudo() if "quotation_id" in tender._fields else None
        ratio = (
            (quote.value / quote.amount_total)
            if quote and quote.amount_total
            else (contract.term_value / contract.accepted_total if contract.accepted_total else 1.0)
        )
        ex_vat = round((variation.amount or 0.0) * ratio, 2)
        accepted = round((contract.accepted_total or 0.0) + (variation.amount or 0.0), 2)
        if contract.state == "draft":
            contract._guarded().write(
                {
                    "term_value": round(contract._fix_term_value() + ex_vat, 2),
                    "annual_value": round(
                        (contract.annual_value or 0.0)
                        + ex_vat
                        * 12.0
                        / max(
                            contract._fix_months_between(contract.date_start, contract.date_end),
                            1e-9,
                        ),
                        2,
                    ),
                    "accepted_total": accepted,
                }
            )
            variation._guarded().write({"applied_to_contract": True})
            contract.message_post(
                body="Variation %s (BDT %.2f) applied to the draft."
                % (variation.name, variation.amount)
            )
            return {"model": contract._name, "id": contract.id, "created": True}
        today = fields.Date.context_today(self)
        effective = today
        if contract.billed_through_date and contract.billed_through_date >= today:
            effective = contract.billed_through_date + timedelta(days=1)
        months = contract._fix_months_between(effective, contract.date_end)
        if months <= 0:
            raise UserError(
                "%s refused: contract %s has no unbilled term left to vary."
                % (label, contract.code)
            )
        amendment = (
            self.env["fix.contract.amendment"]
            .sudo()
            .create(
                {
                    "name": "Tender variation %s" % variation.name,
                    "contract_id": contract.id,
                    "kind": "pricing",
                    "delta_value": round(ex_vat * 12.0 / months, 2),
                    "effective_from": effective,
                    "note": (variation.reason or "")[:250],
                }
            )
        )
        # the Tender Committee (or the Commercial Manager beyond the cap)
        # approved it through M63: the amendment applies as that decision
        amendment._amendment_apply()
        contract._guarded().write({"accepted_total": accepted})
        variation._guarded().write({"amendment_id": amendment.id, "applied_to_contract": True})
        return {"model": amendment._name, "id": amendment.id, "created": True}


class FixTenderVariationLink(models.Model):
    _inherit = "fix.tender.variation"

    amendment_id = fields.Many2one("fix.contract.amendment", readonly=True, copy=False)
    applied_to_contract = fields.Boolean(readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"amendment_id", "applied_to_contract"}


# =============================================================================
# M36-F6: the cash legs of tender bonds reach the GL
# =============================================================================
# Account roles (cd_quotation.account_code.<role>). Defaults are fix_real's
# chart, verified on fix_real_a04 (20 Nov 2026); OWNER confirms each:
#   bond_margin   100035 "BG Margin" (asset_current): the cash margin the bank
#                 holds against a bank guarantee
#   bond_deposit  100031 "Security Deposit" (asset_current): an EMD / bid
#                 security paid by pay order, held by the procuring entity
#   bond_charges  500226 "Tender & Gvt Project Expense": the bank's guarantee
#                 commission
#   bond_funding  the bank account the money leaves from: the M20 bank role
#                 (cd_billing_engine.account_code.bank, 100105 on fix_real)
# A missing account REFUSES the activation / release (fail closed). The
# encashment loss itself is posted by cd_cash_position's tender_bond.claimed
# consumer (Dr loss / Cr outgoing clearing for the full amount); this side
# only returns the money already held (Dr outgoing clearing / Cr margin or
# deposit), so the bank leg is amount - held.
BOND_PARAM = "cd_quotation.account_code.%s"
BOND_DEFAULTS = {
    "bond_margin": "100035",
    "bond_deposit": "100031",
    "bond_charges": "500226",
    "bond_funding": None,
}


def bond_account(env, company, role):
    params = env["ir.config_parameter"].sudo()
    code = params.get_param(BOND_PARAM % role)
    if not code and role == "bond_funding":
        code = params.get_param("cd_billing_engine.account_code.bank")
    if not code and role == "bond_clearing":
        code = params.get_param("cd_cash_position.account_code.outgoing_clearing")
    code = code or BOND_DEFAULTS.get(role)
    account = env["account.account"]
    if code:
        account = (
            env["account.account"]
            .sudo()
            .with_company(company)
            .search([("code", "=", code), ("company_ids", "in", company.id)], limit=1)
        )
    if not account:
        raise UserError(
            "Tender bond posting refused: no account for '%s' in %s. Set the system "
            "parameter %s to the chart account (fail closed, A04 ERP audit M36-F6)."
            % (role, company.name, BOND_PARAM % role)
        )
    return account


class FixTenderBondMoney(models.Model):
    _inherit = "fix.tender.bond"

    instrument = fields.Selection(
        [
            ("bank_guarantee", "Bank guarantee"),
            ("pay_order", "Pay order / cash deposit (EMD)"),
        ],
        default="bank_guarantee",
        required=True,
        help="A bank guarantee holds only its cash margin; a pay order is the full "
        "amount paid over to the procuring entity.",
    )
    margin_amount = fields.Monetary(
        string="Cash Margin Held by the Bank",
        currency_field="currency_id",
        help="The cash margin the bank blocked against the guarantee (from the bank "
        "advice); 0 = none.",
    )
    charges_amount = fields.Monetary(
        string="Bank Commission", currency_field="currency_id", help="Charged by the bank at issue."
    )
    funding_move_id = fields.Many2one("account.move", readonly=True, copy=False)
    release_move_id = fields.Many2one("account.move", readonly=True, copy=False)
    claim_move_id = fields.Many2one("account.move", readonly=True, copy=False)

    @api.constrains("margin_amount", "charges_amount", "amount")
    def _check_money(self):
        for rec in self:
            if (rec.margin_amount or 0.0) < 0 or (rec.charges_amount or 0.0) < 0:
                raise UserError("A margin or a bank commission cannot be negative.")
            if (rec.margin_amount or 0.0) > (rec.amount or 0.0) + 0.005:
                raise UserError("The cash margin cannot exceed the guarantee amount.")

    def _held_amount(self) -> float:
        self.ensure_one()
        if self.instrument == "pay_order":
            return self.amount or 0.0
        return self.margin_amount or 0.0

    def _held_role(self) -> str:
        return "bond_deposit" if self.instrument == "pay_order" else "bond_margin"

    def _post(self, ref, lines, entry_date=None):
        """Post through M19 (the AR posting helper), dims of the tender's unit."""
        from odoo.addons.cd_billing_engine.models.fix_ar_engine import _post_ar_move

        self.ensure_one()
        company = self.tender_id.company_id or self.env.company
        unit = self.tender_id.operating_unit_id
        dims = self.env["fix.ar.invoice"]._ar_posting_dims(operating_unit_id=unit.id or None)
        move, note = _post_ar_move(
            self.env,
            company,
            entry_date or fields.Date.context_today(self),
            ref,
            lines,
            dict.fromkeys(range(len(lines)), dims),
            source="treasury",
        )
        if not move:
            raise UserError("Tender bond posting refused: %s" % (note or "the engine refused it"))
        return move

    def action_activate(self):
        res = super().action_activate()
        labels = dict(self._fields["instrument"].selection)
        for rec in self.filtered(lambda b: b.state == "active" and not b.funding_move_id):
            held, charges = rec._held_amount(), rec.charges_amount or 0.0
            if held <= 0.005 and charges <= 0.005:
                continue
            company = rec.tender_id.company_id or self.env.company
            funding = bond_account(self.env, company, "bond_funding")
            partner = rec.tender_id.client_id.id or False
            lines = []
            if held > 0.005:
                held_acc = bond_account(self.env, company, rec._held_role())
                label = "%s held: %s" % (labels[rec.instrument], rec.name)
                lines.append((held_acc.id, label, held, 0.0, partner))
            if charges > 0.005:
                charge_acc = bond_account(self.env, company, "bond_charges")
                lines.append((charge_acc.id, "Bank commission: %s" % rec.name, charges, 0.0, False))
            lines.append((funding.id, "Bank: %s" % rec.name, 0.0, round(held + charges, 2), False))
            move = rec._post("BOND-FUND-%s" % rec.name, lines)
            rec._guarded().write({"funding_move_id": move.id})
        return res

    def action_bond_decision_approve(self):
        res = super().action_bond_decision_approve()
        for rec in self:
            held = rec._held_amount()
            if held <= 0.005 or not rec.funding_move_id:
                continue
            company = rec.tender_id.company_id or self.env.company
            held_acc = bond_account(self.env, company, rec._held_role())
            partner = rec.tender_id.client_id.id or False
            if rec.state == "released" and not rec.release_move_id:
                funding = bond_account(self.env, company, "bond_funding")
                move = rec._post(
                    "BOND-RELEASE-%s" % rec.name,
                    [
                        (funding.id, "Bank: %s returned" % rec.name, held, 0.0, False),
                        (held_acc.id, "Released: %s" % rec.name, 0.0, held, partner),
                    ],
                )
                rec._guarded().write({"release_move_id": move.id})
            elif rec.state == "claimed" and not rec.claim_move_id:
                clearing = bond_account(self.env, company, "bond_clearing")
                move = rec._post(
                    "BOND-CLAIM-HELD-%s" % rec.name,
                    [
                        (
                            clearing.id,
                            "Encashed from the money held: %s" % rec.name,
                            held,
                            0.0,
                            False,
                        ),
                        (held_acc.id, "Encashed: %s" % rec.name, 0.0, held, partner),
                    ],
                )
                rec._guarded().write({"claim_move_id": move.id})
        return res


# =============================================================================
# M36-F15: what the customer accepted under stays as it was
# =============================================================================
# The customer's PO reference, the template the quotation was built from and
# the language it was printed in stayed editable after acceptance, so the
# record no longer said what was accepted.
DECIDED_LOCKED = ("customer_po_ref", "customer_po_date", "template_id", "document_lang")
DECIDED_STATES = ("accepted", "declined", "expired", "cancelled", "superseded")


class FixQuotationDecidedLock(models.Model):
    _inherit = "fix.quotation"

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if self and any(q.state in DECIDED_STATES for q in self):
            locked |= {f for f in DECIDED_LOCKED if f in self._fields}
        return locked

    def write(self, vals):
        if not self._fix_guard_open():
            touched = [f for f in DECIDED_LOCKED if f in vals and f in self._fields]
            if touched:
                hit = self.filtered(
                    lambda q: q.state in DECIDED_STATES
                    and any(q._fix_guard_differs(f, vals[f], q[f]) for f in touched)
                )
                if hit:
                    raise UserError(
                        "Quotation %s is %s: its PO reference, template and print language "
                        "are part of what was decided." % (hit[0].name, hit[0].state)
                    )
        return super().write(vals)


# =============================================================================
# M36-F14: the quotation's cost is what its lines cost (M15), not typed
# =============================================================================
class FixQuotationLineCost(models.Model):
    _inherit = "fix.quotation"

    def _fix_lines_cost(self):
        """The direct cost of the priced lines: each line's unit cost, else
        the M15 average cost of its product (standard_price). None when no
        line carries a cost (a manual line with no item): the typed estimate
        then stays, and the margin is flagged as typed."""
        self.ensure_one()
        lines = (
            self._scope_lines() if hasattr(self, "_scope_lines") else self.env["fix.quotation.line"]
        )
        total, known = 0.0, False
        for line in lines:
            unit = line.cost_unit or (
                line.product_id.sudo().standard_price if line.product_id else 0.0
            )
            if unit:
                known = True
            total += (line.quantity or 0.0) * (unit or 0.0)
        return round(total, 2) if known else None

    def _sync_from_lines(self):
        res = super()._sync_from_lines()
        for rec in self.exists().filtered(lambda q: q.state in ("draft", "approved")):
            cost = rec._fix_lines_cost()
            if cost is not None and abs(cost - (rec.cost_amount or 0.0)) > 0.005:
                rec._guarded().write({"cost_amount": cost})
        return res


# =============================================================================
# M36-F10: the contract a proposal becomes carries what was proposed
# =============================================================================
class FixQuotationEntitlement(models.Model):
    """An entitlement a contract quotation proposes (visits, incidents, hours,
    loaners); copied onto the M08 contract when the quotation converts."""

    _name = "fix.quotation.entitlement"
    _description = "Quotation Proposed Entitlement"
    _order = "quotation_id, id"

    quotation_id = fields.Many2one("fix.quotation", required=True, ondelete="cascade", index=True)
    company_id = fields.Many2one(related="quotation_id.company_id", store=True, index=True)
    entitlement_type = fields.Selection(
        [
            ("visits", "Preventive Visits"),
            ("incidents", "Repair Incidents"),
            ("hours", "Labour Hours"),
            ("loaners", "Loaner Devices"),
        ],
        required=True,
        default="incidents",
    )
    quantity_included = fields.Float(required=True, help="0 = unlimited (state it on purpose).")
    device_id = fields.Many2one("fix.device", string="Specific Asset")

    @api.model_create_multi
    def create(self, vals_list):
        quotes = self.env["fix.quotation"].browse(
            {v.get("quotation_id") for v in vals_list} - {None}
        )
        self.env["fix.quotation.line"]._assert_editable(quotes)
        return super().create(vals_list)

    def write(self, vals):
        self.env["fix.quotation.line"]._assert_editable(self.quotation_id)
        return super().write(vals)

    def unlink(self):
        self.env["fix.quotation.line"]._assert_editable(self.quotation_id)
        return super().unlink()


class FixQuotationContractTerms(models.Model):
    _inherit = "fix.quotation"

    contract_entitlement_ids = fields.One2many(
        "fix.quotation.entitlement", "quotation_id", string="Proposed Entitlements", copy=True
    )
    contract_sla_policy_ids = fields.Many2many(
        "fix.sla.policy",
        "fix_quotation_sla_policy_rel",
        "quotation_id",
        "policy_id",
        string="Proposed Service Levels",
    )

    def _fulfil_contract_scope(self, contract):
        """The contract also gets the covered assets of the quoted lines, the
        proposed service levels and entitlements (M36-F10: 0 / 0 / 0)."""
        res = super()._fulfil_contract_scope(contract)
        if not contract:
            return res
        contract = contract.sudo()
        devices = self._scope_lines().mapped("device_id")
        vals = {}
        if devices:
            vals["covered_device_ids"] = [(4, d.id) for d in devices]
        if self.contract_sla_policy_ids:
            vals["sla_policy_ids"] = [(4, p.id) for p in self.contract_sla_policy_ids]
        if vals and contract.state == "draft":
            contract.write(vals)
        if contract.state == "draft" and not contract.entitlement_ids:
            Ent = self.env["fix.contract.entitlement"].sudo()
            for proposed in self.contract_entitlement_ids:
                Ent.create(
                    {
                        "contract_id": contract.id,
                        "entitlement_type": proposed.entitlement_type,
                        "quantity_included": proposed.quantity_included,
                        "device_id": proposed.device_id.id or False,
                    }
                )
        return res
