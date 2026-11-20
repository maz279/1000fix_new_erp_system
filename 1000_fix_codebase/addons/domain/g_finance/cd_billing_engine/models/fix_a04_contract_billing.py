# fix_a04_contract_billing - the contract money legs the A04 ERP audit
# (20 Nov 2026, stream B2) found missing. Each is the estate's M20 pattern:
# a DRAFT fix.ar.invoice (VAT by M51, Finance issues it) or a SUBMITTED
# fix.credit.note (routed approval), idempotent per source, and raised by an
# event consumer that re-reads the record (the payload is a claim).
#
#   M08-F2  contract.terminated: the stub up to the new end is billed, what
#           was billed beyond it is credited, the penalty is invoiced;
#   M08-F3  contract.entitlement_topped_up: the top-up is invoiced;
#   M08-F5  the contract family's revenue account role
#           (cd_billing_engine.account_code.contract_revenue_<family>);
#   M08-F11 the daily service-credit job: SLA breaches of a billed period
#           earn the contract's credit scheme, credited through M20.
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError

from .fix_ar_engine import _ar_account

PARAM = "cd_billing_engine.account_code.%s"
# The revenue account each contract family earns into, by role. Defaults are
# fix_real's chart (verified on fix_real_a04 20 Nov 2026): 400107 "AMC /
# Managed Service Income", 400108 "Rental Service Income"; the other
# families fall back to the service revenue role (400100 "Service Sales
# Income"). OWNER confirms; each is overridable by its parameter.
CONTRACT_REVENUE_DEFAULTS = {
    "contract_revenue_amc": "400107",
    "contract_revenue_managed": "400107",
    "contract_revenue_rental": "400108",
    "contract_revenue_ramc": None,
    "contract_revenue_marketplace": None,
}
# A termination penalty / break fee is not service revenue: 400109 "Other
# Income" (income_other) on fix_real. OWNER confirms.
PENALTY_ROLE = "contract_penalty_income"
PENALTY_DEFAULT = "400109"

CONTRACT_EVENT_MODELS = {
    "contract.terminated": "fix.contract.termination",
    "contract.entitlement_topped_up": "fix.contract",
}


def _account_by_code(env, company, code):
    if not code:
        return env["account.account"]
    return (
        env["account.account"]
        .sudo()
        .with_company(company)
        .search([("code", "=", code), ("company_ids", "in", company.id)], limit=1)
    )


def role_account(env, company, role, default_code):
    code = env["ir.config_parameter"].sudo().get_param(PARAM % role) or default_code
    return _account_by_code(env, company, code)


def contract_revenue_account(env, contract):
    """The revenue account of the contract's family, else service revenue."""
    role = "contract_revenue_%s" % contract._fix_revenue_role()
    account = role_account(env, contract.company_id, role, CONTRACT_REVENUE_DEFAULTS.get(role))
    return account or _ar_account(env, contract.company_id, "revenue")


class FixArInvoiceContractRole(models.Model):
    _inherit = "fix.ar.invoice"

    def _revenue_role(self) -> str:
        """A04 ERP audit M08-F5: a contract period billed in ARREARS is earned
        when it is invoiced - it credits the family's revenue account, not the
        contract liability (and M53 schedules no deferral for it)."""
        self.ensure_one()
        if self.source_model == "fix.contract.billing.period" and self.revenue_account_id:
            return "revenue"
        return super()._revenue_role()


class FixCreditNoteContractReasons(models.Model):
    _inherit = "fix.credit.note"

    reason_code = fields.Selection(
        selection_add=[
            ("contract_termination", "Contract Terminated (billed beyond the end)"),
            ("service_credit", "SLA Service Credit (contract)"),
        ],
        ondelete={"contract_termination": "cascade", "service_credit": "cascade"},
    )


class FixContractTerminationMoney(models.Model):
    _inherit = "fix.contract.termination"

    penalty_invoice_id = fields.Many2one("fix.ar.invoice", readonly=True, copy=False)
    credit_note_ids = fields.Many2many(
        "fix.credit.note",
        "fix_contract_termination_credit_rel",
        "termination_id",
        "credit_id",
        string="Credits Raised",
        readonly=True,
        copy=False,
    )
    billing_settled_on = fields.Datetime(readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "penalty_invoice_id",
            "credit_note_ids",
            "billing_settled_on",
        }


class FixContractTopupMoney(models.Model):
    _inherit = "fix.contract.entitlement.topup"

    invoice_id = fields.Many2one("fix.ar.invoice", readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"invoice_id"}


class FixContractPeriodServiceCredit(models.Model):
    _inherit = "fix.contract.billing.period"

    service_credit_checked = fields.Boolean(readonly=True, copy=False)
    service_credit_note_id = fields.Many2one("fix.credit.note", readonly=True, copy=False)
    service_credit_breaches = fields.Integer(readonly=True, copy=False)

    # breach type of the credit scheme -> the SLA clock (KPI) that measures it
    BREACH_KPIS = {
        "response": ("first_response",),
        "restoration": ("resolution",),
        "resolution": ("resolution",),
        "onsite": ("onsite", "on_site_arrival"),
        "availability": ("availability", "uptime"),
    }
    PRIORITY_MAP = {"p1": "emergency", "p2": "urgent", "p3": "high", "p4": "normal"}

    def _period_breaches(self, scheme):
        """The SLA breaches of the contract's orders that fell in the period,
        for the scheme's breach type and priority."""
        self.ensure_one()
        contract = self.contract_id
        orders = self.env["fix.service.order"].sudo().search([("contract_id", "=", contract.id)])
        if scheme.priority != "any":
            orders = orders.filtered(lambda o: o.priority == self.PRIORITY_MAP[scheme.priority])
        if not orders:
            return 0
        start = fields.Datetime.to_datetime(self.period_start)
        end = fields.Datetime.to_datetime(self.period_end) + timedelta(days=1)
        return (
            self.env["fix.sla.kpi.instance"]
            .sudo()
            .search_count(
                [
                    ("res_model", "=", "fix.service.order"),
                    ("res_id", "in", orders.ids),
                    ("kpi_code", "in", list(self.BREACH_KPIS.get(scheme.breach_type, ()))),
                    ("state", "=", "breached"),
                    ("breached_at", ">=", start),
                    ("breached_at", "<", end),
                ]
            )
        )

    @api.model
    def cron_contract_service_credits(self):
        """Daily (A04 ERP audit M08-F11): every billed period whose invoice is
        issued is checked once against its contract's service-credit scheme.
        Breaches earn the scheme's credit (capped per rule), requested as a
        SUBMITTED M20 credit note on the period's invoice. Returns the number
        of credit notes raised."""
        if not self.env.su:
            raise AccessError("The service-credit job runs as the scheduled service only.")
        today = fields.Date.context_today(self)
        periods = self.sudo().search(
            [
                ("service_credit_checked", "=", False),
                ("period_end", "<", today),
                ("invoice_id", "!=", False),
                ("invoice_id.state", "in", ("issued", "paid")),
            ]
        )
        raised = 0
        Credit = self.env["fix.credit.note"].sudo()
        for period in periods:
            schemes = period.contract_id.credit_scheme_ids
            if not schemes:
                period.write({"service_credit_checked": True})
                continue
            try:
                with self.env.cr.savepoint():
                    breaches, credit = 0, 0.0
                    for scheme in schemes:
                        count = period._period_breaches(scheme)
                        breaches += count
                        credit += scheme._scheme_credit(count, period.amount)
                    credit = round(min(credit, period.amount), 2)
                    vals = {"service_credit_checked": True, "service_credit_breaches": breaches}
                    if credit > 0.005:
                        invoice = period.invoice_id
                        gross = (
                            round(credit * invoice.total_payable / invoice.taxable_amount, 2)
                            if invoice.taxable_amount
                            else credit
                        )
                        note = Credit._fix_request_credit(
                            invoice,
                            min(gross, invoice.amount_residual or gross),
                            "service_credit",
                            note="Service credit for %d SLA breach(es) in %s to %s (contract %s)."
                            % (
                                breaches,
                                period.period_start,
                                period.period_end,
                                period.contract_id.code,
                            ),
                        )
                        vals["service_credit_note_id"] = note.id
                        raised += 1
                    period.write(vals)
            except UserError as exc:
                period.contract_id.message_post(
                    body="Service credit for %s not raised: %s"
                    % (period.display_name, exc.args[0] if exc.args else exc)
                )
        return raised


class FixA04ContractConsumers(models.AbstractModel):
    """R8 consumers of the contract money events (no table of its own)."""

    _name = "fix.a04.contract.consumers"
    _description = "A04 Contract Money Event Consumers"

    def _fix_event_record(self, event, event_type, label):
        if not self.env.su:
            raise AccessError("Contract money consumers run only from the event relay.")
        model = CONTRACT_EVENT_MODELS[event_type]
        aggregate = event.get("aggregate")
        if aggregate and aggregate != model:
            raise UserError(
                "%s refused: the event's aggregate is %s, not %s." % (label, aggregate, model)
            )
        try:
            res_id = int(event.get("aggregate_id") or 0)
        except (TypeError, ValueError):
            res_id = 0
        record = self.env[model].sudo().browse(res_id).exists() if res_id else None
        if not record:
            raise UserError("%s refused: there is no %s #%s." % (label, model, res_id))
        return record, event.get("payload") or {}

    # ---- M08-F2: termination ------------------------------------------------------
    @api.model
    def consume_contract_terminated(self, event: dict) -> dict:
        label = "Contract termination hand-off"
        termination, _payload = self._fix_event_record(event, "contract.terminated", label)
        if termination.state != "effective":
            raise UserError(
                "%s refused: notice %s is %s." % (label, termination.name, termination.state)
            )
        if termination.kind != "termination":
            return {"skipped": "suspension: no money moves on suspension"}
        if termination.billing_settled_on:
            return {"model": termination._name, "id": termination.id, "created": False}
        result = self._settle_termination(termination)
        termination._guarded().write({"billing_settled_on": fields.Datetime.now()})
        return result

    def _settle_termination(self, termination):
        contract = termination.contract_id.sudo()
        if contract.state != "terminated":
            raise UserError("Contract %s is %s, not terminated." % (contract.code, contract.state))
        if not contract.terminated_on:
            contract._fix_terminate_term(termination.effective_date)
        Period = self.env["fix.contract.billing.period"].sudo()
        end = contract.date_end
        # 1. drafts that reach beyond the new end are re-billed to the end
        for period in Period.search([("contract_id", "=", contract.id), ("period_end", ">", end)]):
            invoice = period.invoice_id
            if invoice and invoice.state == "draft":
                invoice.action_cancel(
                    reason="Contract %s terminated: re-billed to %s" % (contract.code, end)
                )
                period.unlink()
            elif not invoice:
                period.unlink()
        remaining = Period.search([("contract_id", "=", contract.id)])
        contract._guarded().write(
            {"billed_through_date": max(remaining.mapped("period_end")) if remaining else False}
        )
        # 2. the stub (the unbilled days up to the new end)
        stub = Period._bill_contract(contract, end)
        # 3. what was billed beyond the end is credited
        credits = self.env["fix.credit.note"]
        over = round(contract._fix_billed_total() - contract._fix_billing_target(), 2)
        if over > 0.005:
            issued = Period.search(
                [("contract_id", "=", contract.id), ("invoice_id.state", "in", ("issued", "paid"))],
                order="period_start desc",
            )
            for period in issued:
                if over <= 0.005:
                    break
                invoice = period.invoice_id
                share = round(min(over, period.amount), 2)
                gross = (
                    round(share * invoice.total_payable / invoice.taxable_amount, 2)
                    if invoice.taxable_amount
                    else share
                )
                credits |= (
                    self.env["fix.credit.note"]
                    .sudo()
                    ._fix_request_credit(
                        invoice,
                        gross,
                        "contract_termination",
                        note="Contract %s terminated with effect from %s: BDT %.2f (excl. VAT) of "
                        "this period was billed beyond the new end %s."
                        % (contract.code, termination.effective_date, share, end),
                    )
                )
                over = round(over - share, 2)
        # 4. the penalty / break fee
        penalty = self.env["fix.ar.invoice"]
        if (termination.penalty_amount or 0.0) > 0.005:
            penalty = (
                self.env["fix.ar.invoice"]
                .sudo()
                ._fix_source_invoice(
                    termination._name,
                    termination.id,
                    None,
                    contract.customer_id,
                    [
                        {
                            "description": "Termination penalty / break fee - contract %s (%s)"
                            % (contract.code, termination.reason),
                            "taxable_amount": termination.penalty_amount,
                        }
                    ],
                    "Contract %s termination %s: penalty" % (contract.code, termination.name),
                    contract.company_id,
                    credit_account=role_account(
                        self.env, contract.company_id, PENALTY_ROLE, PENALTY_DEFAULT
                    )
                    or None,
                    operating_unit=contract.operating_unit_id,
                    branch=contract._fix_billing_branch() or None,
                    invoice_date=fields.Date.context_today(self),
                    issue=False,
                )
            )
        termination._guarded().write(
            {
                "penalty_invoice_id": penalty.id or False,
                "credit_note_ids": [(6, 0, credits.ids)],
            }
        )
        contract.message_post(
            body="Termination settled: %d stub invoice(s), %d credit note(s) requested, "
            "penalty invoice %s."
            % (stub, len(credits), penalty.display_name if penalty else "none")
        )
        return {
            "model": termination._name,
            "id": termination.id,
            "created": True,
            "stub_invoices": stub,
            "credit_notes": credits.ids,
            "penalty_invoice": penalty.id or False,
        }

    # ---- M08-F3: entitlement top-up -----------------------------------------------
    @api.model
    def consume_contract_entitlement_topped_up(self, event: dict) -> dict:
        label = "Entitlement top-up hand-off"
        contract, payload = self._fix_event_record(event, "contract.entitlement_topped_up", label)
        try:
            topup_id = int(payload.get("topup_id") or 0)
        except (TypeError, ValueError):
            topup_id = 0
        topup = self.env["fix.contract.entitlement.topup"].sudo().browse(topup_id).exists()
        if not topup or topup.contract_id != contract:
            raise UserError(
                "%s refused: top-up #%s is not on contract %s." % (label, topup_id, contract.code)
            )
        if topup.state != "applied":
            raise UserError(
                "%s refused: top-up %s is %s, not applied." % (label, topup.name, topup.state)
            )
        if topup.invoice_id:
            return {"model": "fix.ar.invoice", "id": topup.invoice_id.id, "created": False}
        amount = topup.amount or 0.0
        claimed = payload.get("amount")
        if claimed is not None and abs(float(claimed) - amount) > 0.005:
            raise UserError(
                "%s refused: the event says BDT %.2f but top-up %s says BDT %.2f."
                % (label, float(claimed), topup.name, amount)
            )
        if amount <= 0.005:
            return {"skipped": "top-up %s carries no price" % topup.name}
        invoice = (
            self.env["fix.ar.invoice"]
            .sudo()
            ._fix_source_invoice(
                topup._name,
                topup.id,
                None,
                contract.customer_id,
                [
                    {
                        "description": "Entitlement top-up %s: +%g %s on contract %s (%s)"
                        % (
                            topup.name,
                            topup.quantity,
                            topup.entitlement_id.entitlement_type,
                            contract.code,
                            topup.customer_reference,
                        ),
                        "taxable_amount": amount,
                    }
                ],
                "Contract %s entitlement top-up %s" % (contract.code, topup.name),
                contract.company_id,
                credit_account=contract_revenue_account(self.env, contract) or None,
                operating_unit=contract.operating_unit_id,
                branch=contract._fix_billing_branch() or None,
                invoice_date=fields.Date.context_today(self),
                issue=False,
            )
        )
        topup._guarded().write({"invoice_id": invoice.id})
        return {"model": invoice._name, "id": invoice.id, "created": True}


# =============================================================================
# M36-F6: retention on government tender billing
# =============================================================================
# A contract that carries a retention % (from its tender) has that share of
# each bill (excl. VAT) withheld by the customer until it is released (end of
# the defects-liability period). At issue the withheld part leaves the
# collectable receivable: Dr Retention Receivable / Cr AR control, and the
# invoice's residual (what dunning chases) excludes it. Releasing it moves
# it back: Dr AR / Cr Retention Receivable. Role
# cd_billing_engine.account_code.contract_retention_receivable, default
# 100031 "Security Deposit" on fix_real (asset_current) - OWNER confirms.
RETENTION_ROLE = "contract_retention_receivable"
RETENTION_DEFAULT = "100031"


class FixArInvoiceRetention(models.Model):
    _inherit = "fix.ar.invoice"

    retention_withheld = fields.Monetary(
        string="Retention Withheld", currency_field="currency_id", readonly=True, copy=False
    )
    retention_released = fields.Monetary(
        string="Retention Released", currency_field="currency_id", readonly=True, copy=False
    )
    retention_move_id = fields.Many2one("account.move", readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "retention_withheld",
            "retention_released",
            "retention_move_id",
        }

    def _raw_residual(self) -> float:
        held = (self.retention_withheld or 0.0) - (self.retention_released or 0.0)
        return super()._raw_residual() - held

    @api.depends(
        "total_payable",
        "allocation_ids.amount",
        "credit_note_ids.amount",
        "credit_note_ids.state",
        "vds_certificate_ids.vds_amount",
        "vds_certificate_ids.state",
        "tds_certificate_ids.tds_amount",
        "tds_certificate_ids.state",
        "writeoff_ids.amount",
        "writeoff_ids.state",
        "retention_withheld",
        "retention_released",
    )
    def _compute_payment(self):
        return super()._compute_payment()

    def _fix_retention_contract(self):
        self.ensure_one()
        if self.source_model != "fix.contract.billing.period" or not self.source_id:
            return self.env["fix.contract"]
        period = self.env["fix.contract.billing.period"].sudo().browse(self.source_id).exists()
        return period.contract_id if period else self.env["fix.contract"]

    def _fix_post_retention(self, amount, release=False):
        self.ensure_one()
        from .fix_ar_engine import _ar_account, _post_ar_move

        company = self.company_id
        ar = _ar_account(self.env, company, "ar")
        held = role_account(self.env, company, RETENTION_ROLE, RETENTION_DEFAULT)
        if not (ar and held):
            return None, "GL not posted: AR or %s unconfigured" % RETENTION_ROLE
        partner = self.customer_id.id
        label = "%s retention %s" % ("Released" if release else "Withheld", self.name)
        lines = (
            [(ar.id, label, amount, 0.0, partner), (held.id, label, 0.0, amount, partner)]
            if release
            else [(held.id, label, amount, 0.0, partner), (ar.id, label, 0.0, amount, partner)]
        )
        dims = self._ar_posting_dims(self.branch_id.id)
        return _post_ar_move(
            self.env,
            company,
            fields.Date.context_today(self),
            label,
            lines,
            dict.fromkeys(range(2), dims),
            source="ar",
        )

    def action_issue(self):
        res = super().action_issue()
        for inv in self.filtered(lambda i: i.state == "issued" and not i.retention_withheld):
            contract = inv._fix_retention_contract()
            pct = contract.retention_pct if contract else 0.0
            if not pct:
                continue
            amount = round((inv.taxable_amount or 0.0) * pct / 100.0, 2)
            if amount <= 0.005:
                continue
            move, note = inv._fix_post_retention(amount)
            inv._guarded().write(
                {"retention_withheld": amount, "retention_move_id": move.id if move else False}
            )
            inv.message_post(
                body="Retention %.2f%% withheld: BDT %.2f (%s)."
                % (pct, amount, move.name if move else note)
            )
        return res

    def action_release_retention(self):
        """The defects-liability period is over: the retention becomes
        collectable again (an Accountant's act)."""
        from .fix_finance_approval import GROUP_ACCOUNTANT, require_role

        require_role(self.env, GROUP_ACCOUNTANT, "Releasing retention")
        for inv in self:
            open_ = round((inv.retention_withheld or 0.0) - (inv.retention_released or 0.0), 2)
            if open_ <= 0.005:
                raise UserError("Invoice %s holds no retention to release." % inv.name)
            move, note = inv.sudo()._fix_post_retention(open_, release=True)
            inv.sudo()._guarded().write({"retention_released": inv.retention_withheld})
            inv.message_post(
                body="Retention BDT %.2f released (%s)." % (open_, move.name if move else note)
            )
        return True
