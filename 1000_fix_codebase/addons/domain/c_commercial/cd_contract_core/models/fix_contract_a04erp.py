# A04 ERP audit (20 Nov 2026), stream B2: the M08 contract side of the
# money and control findings. The finance legs (invoices, credit notes) live
# in cd_billing_engine/models/fix_a04_contract_billing.py, because this module
# must not depend on the billing engine.
#
#   M08-F1  suspension windows: a suspended day is never billed, and resuming
#           does not back-bill the suspension (fix.contract.suspension);
#   M08-F2  termination ends the term on the notice's effective date and
#           re-prices it, so the billing hand-off bills the stub and credits
#           what was billed beyond it;
#   M08-F7  a term amendment cannot end the contract before its billed-through
#           date (terminate instead: termination credits);
#   M08-F12 an amendment that takes the contract across the Legal threshold
#           waits for a Legal review before it applies;
#   M08-F14 an entitlement line states its quantity (0 = unlimited is a
#           choice, never the default of an empty field).
from datetime import timedelta

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from .fix_contract import (
    IN_FORCE,
    LEGAL,
    LEGAL_REVIEW_FAMILIES,
    LEGAL_REVIEW_THRESHOLD_BDT,
    MANAGER,
    family_profile,
    require_role,
)


class FixContractSuspension(models.Model):
    """One suspension window of a contract: the days it was not in force.
    Written by the engine (suspension, resume, termination), never typed."""

    _name = "fix.contract.suspension"
    _description = "Contract Suspension Window"
    _order = "contract_id, date_from, id"

    contract_id = fields.Many2one(
        "fix.contract", required=True, index=True, ondelete="cascade", readonly=True
    )
    company_id = fields.Many2one(related="contract_id.company_id", store=True, index=True)
    operating_unit_id = fields.Many2one(
        related="contract_id.operating_unit_id", store=True, index=True
    )
    date_from = fields.Date(required=True, readonly=True)
    date_to = fields.Date(readonly=True, help="Empty while the contract is still suspended.")
    compensated = fields.Boolean(
        readonly=True,
        help="The term was extended by these days on resume: the customer still "
        "pays the full term value over the extended term.",
    )
    treatment = fields.Char(readonly=True)

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.su:
            raise UserError("A suspension window is recorded by the contract's suspension only.")
        return super().create(vals_list)

    def write(self, vals):
        if not self.env.su:
            raise UserError("A suspension window is recorded by the contract's suspension only.")
        return super().write(vals)

    def unlink(self):
        if not self.env.su:
            raise UserError("A suspension window is part of the contract's record.")
        return super().unlink()


class FixContractA04Erp(models.Model):
    _inherit = "fix.contract"

    @api.constrains("retention_pct", "ld_rate_pct_per_day", "ld_cap_pct")
    def _check_retention_terms(self):
        for rec in self:
            for name in ("retention_pct", "ld_rate_pct_per_day", "ld_cap_pct"):
                if not 0.0 <= (rec[name] or 0.0) <= 100.0:
                    raise ValidationError(
                        "%s is a percentage between 0 and 100." % rec._fields[name].string
                    )

    suspension_ids = fields.One2many(
        "fix.contract.suspension", "contract_id", string="Suspension Windows", readonly=True
    )
    terminated_on = fields.Date(readonly=True, copy=False)
    # A04 ERP audit M36-F6/F9: the tender's retention and liquidated-damages
    # terms travel with the contract (government billing withholds retention).
    retention_pct = fields.Float(
        string="Retention (%)",
        help="Withheld by the customer from each bill (excl. VAT) until released.",
    )
    ld_rate_pct_per_day = fields.Float(string="Liquidated Damages (% per day)", digits=(5, 3))
    ld_cap_pct = fields.Float(string="LD Cap (%)")
    date_end_before_termination = fields.Date(readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"terminated_on", "date_end_before_termination"}

    # ---- the term value -------------------------------------------------------
    def _fix_months_between(self, date_from, date_to) -> float:
        """Calendar-month slots (fractional) covering [date_from, date_to]."""
        self.ensure_one()
        cache, months, day = {}, 0.0, date_from
        while day and date_to and day <= date_to:
            slot = cache.get(day) or self._fix_slot_bounds(day)
            cursor = slot[0]
            while cursor <= slot[1] and cursor not in cache:
                cache[cursor] = slot
                cursor += timedelta(days=1)
            months += 1.0 / ((slot[1] - slot[0]).days + 1)
            day += timedelta(days=1)
        return months

    def _fix_default_term_value(self) -> float:
        self.ensure_one()
        if not (self.date_start and self.date_end):
            return 0.0
        return round(
            (self.annual_value or 0.0)
            / 12.0
            * self._fix_months_between(self.date_start, self.date_end),
            2,
        )

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec, vals in zip(records, vals_list, strict=True):
            if not vals.get("term_value"):
                rec._guarded().write({"term_value": rec._fix_default_term_value()})
        return records

    def write(self, vals):
        old_state = {rec.id: rec.state for rec in self}
        res = super().write(vals)
        if {"annual_value", "date_start", "date_end"} & set(vals) and "term_value" not in vals:
            # a draft is still being priced: its term value follows
            for rec in self.filtered(lambda r: r.state == "draft"):
                rec._guarded().write({"term_value": rec._fix_default_term_value()})
        if vals.get("state") == "suspended":
            for rec in self.filtered(lambda r: old_state.get(r.id) != "suspended"):
                rec._fix_open_suspension()
        return res

    # ---- suspension windows (M08-F1) -------------------------------------------
    def _fix_open_suspension(self):
        Window = self.env["fix.contract.suspension"].sudo()
        for rec in self:
            if Window.search_count([("contract_id", "=", rec.id), ("date_to", "=", False)]):
                continue
            Window.create(
                {
                    "contract_id": rec.id,
                    "date_from": rec.suspended_on or fields.Date.context_today(rec),
                }
            )

    def _fix_close_suspension(self, last_day, treatment=None):
        """Close the open window on `last_day` (the last suspended day). A
        window that closes before it opens held no day: it is dropped."""
        Window = self.env["fix.contract.suspension"].sudo()
        for rec in self:
            for window in Window.search([("contract_id", "=", rec.id), ("date_to", "=", False)]):
                if last_day < window.date_from:
                    window.unlink()
                    continue
                window.write(
                    {
                        "date_to": last_day,
                        "compensated": treatment == "extend_term",
                        "treatment": treatment or False,
                    }
                )

    def action_resume(self, treatment=None, note=None):
        today = fields.Date.context_today(self)
        suspended = self.filtered(lambda r: r.state == "suspended")
        res = super().action_resume(treatment=treatment, note=note)
        effective = treatment or ("forfeit" if self.env.su else None)
        suspended._fix_close_suspension(today - timedelta(days=1), effective)
        return res

    # ---- termination (M08-F2) ---------------------------------------------------
    def _fix_terminate_term(self, effective_date):
        """The contract ends the day before the termination takes effect; the
        term value loses the days it no longer covers, so the billing hand-off
        bills the stub up to the new end and credits anything billed beyond."""
        for rec in self:
            new_end = max(effective_date - timedelta(days=1), rec.date_start + timedelta(days=1))
            old_end = rec.date_end
            vals = {"terminated_on": effective_date}
            if new_end < old_end:
                lost = rec._fix_fee_between(new_end + timedelta(days=1), old_end, suspended=False)
                vals.update(
                    {
                        "date_end": new_end,
                        "date_end_before_termination": old_end,
                        "term_value": round(max(rec._fix_term_value() - lost, 0.0), 2),
                    }
                )
            rec.sudo()._guarded().write(vals)
            rec._fix_close_suspension(rec.date_end)
            rec.message_post(
                body="Terminated with effect from %s: the term now ends on %s and is worth "
                "BDT %.2f before VAT." % (effective_date, rec.date_end, rec.term_value)
            )

    # ---- billing helpers read by the M20 hand-off --------------------------------
    def _fix_billing_branch(self):
        """The branch the contract's invoices carry (M08-F4): the branch of the
        contract's operating unit (each branch has its own unit)."""
        self.ensure_one()
        return (
            self.env["fix.branch"]
            .sudo()
            .search([("operating_unit_id", "=", self.operating_unit_id.id)], limit=1)
        )

    def _fix_revenue_role(self) -> str:
        self.ensure_one()
        return family_profile(self.family)["revenue_role"]

    def action_print_contract(self):
        """M08-F20: the contract printout (number, BINs, term, price excl. and
        incl. VAT, billing schedule, cover, statutory, signatures)."""
        self.check_access("read")
        report = "cd_contract_core.report_contract"
        return {
            "type": "ir.actions.act_url",
            "url": "/report/pdf/cd_contract_core.report_contract_document/%s"
            % ",".join(str(i) for i in self.ids),
            "target": "new",
            "report": report,
        }


class FixContractEntitlementA04Erp(models.Model):
    _inherit = "fix.contract.entitlement"

    @api.model_create_multi
    def create(self, vals_list):
        # A04 ERP audit M08-F14: a line saved with no quantity was unlimited
        # (50 of 50 draws succeeded). The quantity is stated: 0 means
        # unlimited only when someone typed it.
        for vals in vals_list:
            qty = vals.get("quantity_included")
            # identity, not equality: 0 == False, and 0 is a stated "unlimited"
            if qty is None or qty is False or qty == "":
                raise ValidationError(
                    "State the quantity this entitlement includes (enter 0 only for an "
                    "unlimited entitlement)."
                )
        return super().create(vals_list)


class FixContractAmendmentA04Erp(models.Model):
    _inherit = "fix.contract.amendment"

    legal_review_required = fields.Boolean(
        compute="_compute_legal_review_required",
        help="The amendment takes the contract's total value across the Legal "
        "review threshold: Legal reviews it before it applies.",
    )
    legal_reviewed_by = fields.Many2one("res.users", readonly=True, copy=False)
    legal_reviewed_on = fields.Datetime(readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"legal_reviewed_by", "legal_reviewed_on"}

    def _fix_term_value_delta(self) -> float:
        """How much the amendment moves the contract's total value."""
        self.ensure_one()
        contract = self.contract_id
        if not (contract.date_start and contract.date_end):
            return 0.0
        if self.kind == "pricing" and self.delta_value:
            start = max(self.effective_from or contract.date_start, contract.date_start)
            return round(
                (self.delta_value or 0.0)
                / 12.0
                * contract._fix_months_between(start, contract.date_end),
                2,
            )
        if self.kind == "term" and self.new_date_end:
            if self.new_date_end > contract.date_end:
                return round(
                    contract._fix_fee_between(
                        contract.date_end + timedelta(days=1), self.new_date_end, suspended=False
                    ),
                    2,
                )
            return -round(
                contract._fix_fee_between(
                    self.new_date_end + timedelta(days=1), contract.date_end, suspended=False
                ),
                2,
            )
        return 0.0

    @api.depends("kind", "delta_value", "new_date_end", "contract_id.term_value")
    def _compute_legal_review_required(self):
        for rec in self:
            contract = rec.contract_id
            if not contract or rec.state == "applied" or contract.family in LEGAL_REVIEW_FAMILIES:
                rec.legal_review_required = False
                continue
            before = contract._fix_term_value()
            after = before + rec._fix_term_value_delta()
            rec.legal_review_required = bool(before < LEGAL_REVIEW_THRESHOLD_BDT <= after)

    def _amendment_validate(self):
        res = super()._amendment_validate()
        for rec in self.filtered(lambda r: r.kind == "term" and r.new_date_end):
            billed = rec.contract_id.billed_through_date
            if billed and rec.new_date_end < billed:
                # A04 ERP audit M08-F7: shortening below what was billed
                # stranded the over-billing (98,630 billed vs a new 59,507).
                raise UserError(
                    "Amendment %s would end contract %s on %s, but it is billed through "
                    "%s. End it by a termination notice instead: termination credits "
                    "what was billed beyond its end."
                    % (rec.name, rec.contract_id.code, rec.new_date_end, billed)
                )
        return res

    def action_legal_review(self, note=None):
        """Legal clears an amendment that crosses the threshold (M08-F12): a
        reviewer who neither raised nor approved it."""
        require_role(self.env, LEGAL, "Legal review of a contract amendment")
        for rec in self:
            if not rec.legal_review_required:
                raise UserError("Amendment %s does not need Legal review." % rec.name)
            if rec.legal_reviewed_by:
                raise UserError("Amendment %s is already reviewed by Legal." % rec.name)
            if rec.state not in ("submitted", "approved"):
                raise UserError(
                    "Amendment %s is %s: there is nothing to review." % (rec.name, rec.state)
                )
            conflicted = rec.create_uid | rec.dofa_approved_by
            if self.env.user in conflicted and not self.env.su:
                raise UserError(
                    "Segregation of duties: you raised or approved amendment %s." % rec.name
                )
            rec.sudo()._guarded().write(
                {"legal_reviewed_by": self.env.user.id, "legal_reviewed_on": fields.Datetime.now()}
            )
            rec.sudo().message_post(
                body="Legal review completed by %s. %s" % (self.env.user.name, note or "")
            )
        today = fields.Date.context_today(self)
        self.sudo().filtered(
            lambda r: r.state == "approved" and r.effective_from <= today
        )._amendment_apply()
        return True

    def _amendment_apply(self):
        for rec in self:
            if rec.state == "applied":
                continue
            if rec.legal_review_required and not rec.legal_reviewed_by:
                rec.sudo().message_post(
                    body="Approved, but it takes contract %s across BDT %s: it applies once "
                    "Legal has reviewed it."
                    % (rec.contract_id.code, f"{LEGAL_REVIEW_THRESHOLD_BDT:,.0f}")
                )
                continue
            contract = rec.contract_id.sudo()
            delta = rec._fix_term_value_delta()
            before = contract._fix_term_value()
            super(FixContractAmendmentA04Erp, rec)._amendment_apply()
            if rec.state == "applied" and delta:
                contract._guarded().write({"term_value": round(before + delta, 2)})
        return True


class FixContractTerminationA04Erp(models.Model):
    _inherit = "fix.contract.termination"

    def action_execute_termination(self):
        res = super().action_execute_termination()
        for rec in self.filtered(lambda r: r.state == "effective" and r.kind == "termination"):
            contract = rec.contract_id.sudo()
            if contract.state == "terminated" and not contract.terminated_on:
                contract._fix_terminate_term(rec.effective_date)
        return res


# =============================================================================
# M08-F16: preventive visits are dispatched on their dispatch date
# =============================================================================
class FixContractPmVisitDispatch(models.Model):
    _inherit = "fix.contract.pm.visit"

    @api.model
    def cron_dispatch_due_pm_visits(self):
        """Daily, idempotent (A04 ERP audit M08-F16): every scheduled visit
        whose dispatch date (visit date less the plan's lead time) has come,
        on a contract in force, opens its service order. A visit that cannot
        be dispatched (no branch, contract not in force) is left scheduled and
        the contract's chatter says why. Returns the number dispatched."""
        today = fields.Date.context_today(self)
        visits = self.sudo().search(
            [
                ("state", "=", "scheduled"),
                ("service_order_id", "=", False),
                ("dispatch_from", "<=", today),
                ("contract_id.state", "in", IN_FORCE),
            ]
        )
        done = 0
        for visit in visits:
            try:
                with self.env.cr.savepoint():
                    visit.action_create_service_order()
                    done += 1
            except (UserError, ValidationError) as exc:
                visit.contract_id.message_post(
                    body="PM visit of %s on %s not dispatched: %s"
                    % (
                        visit.device_id.display_name,
                        visit.scheduled_date,
                        exc.args[0] if exc.args else exc,
                    )
                )
        return done


# =============================================================================
# M08-F15: an entitlement has a period, a reset and an exhaustion policy
# =============================================================================
class FixContractEntitlementMovementReset(models.Model):
    _inherit = "fix.contract.entitlement.movement"

    movement_type = fields.Selection(
        selection_add=[("reset", "Reset (new entitlement period)")],
        ondelete={"reset": "cascade"},
    )


class FixContractEntitlementPolicy(models.Model):
    _inherit = "fix.contract.entitlement"

    reset_period = fields.Selection(
        [("term", "Once per term"), ("annual", "Every contract year"), ("monthly", "Every month")],
        default="term",
        required=True,
        help="How often the included quantity is renewed. A balance does not carry over.",
    )
    exhaustion_policy = fields.Selection(
        [
            ("chargeable", "Further work is chargeable (standard paid service)"),
            ("block", "Further work needs the Contract Manager"),
        ],
        default="chargeable",
        required=True,
    )
    period_start = fields.Date(
        string="Current Period From",
        readonly=True,
        copy=False,
        help="The start of the entitlement period the balance belongs to.",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"period_start"}

    def _fix_period_start_on(self, day):
        """The start of the entitlement period that holds `day`."""
        self.ensure_one()
        start = self.contract_id.date_start
        if not start or self.reset_period == "term" or day < start:
            return start
        step = 12 if self.reset_period == "annual" else 1
        months = (day.year - start.year) * 12 + (day.month - start.month)
        n = months // step
        candidate = start + relativedelta(months=n * step)
        if candidate > day:
            candidate = start + relativedelta(months=(n - 1) * step)
        return candidate

    @api.model
    def cron_reset_entitlements(self):
        """Daily, idempotent: a periodic entitlement of a contract in force
        whose period has rolled over starts again at its full quantity (the
        ledger records the reset). Returns the number reset."""
        today = fields.Date.context_today(self)
        lines = self.sudo().search(
            [
                ("reset_period", "in", ("annual", "monthly")),
                ("contract_id.state", "in", IN_FORCE),
                ("quantity_included", ">", 0),
            ]
        )
        reset = 0
        for ent in lines:
            current = ent._fix_period_start_on(today)
            if ent.period_start == current:
                continue
            if not ent.period_start:
                ent._guarded().write({"period_start": current})
                continue
            used = ent.quantity_consumed
            ent._guarded().write({"quantity_consumed": 0.0, "period_start": current})
            if used:
                ent._ledger("reset", used, "Entitlement period from %s" % current)
            reset += 1
        return reset


class FixServiceOrderExhaustion(models.Model):
    _inherit = "fix.service.order"

    def _fix_consume_contract_entitlement(self):
        """M08-F15: a contract whose exhausted entitlement says 'block' does
        not let the order slip through as standard paid work: the Contract
        Manager decides it."""
        for order in self.filtered(
            lambda o: o.order_category == "amc" and not o.contract_entitlement_id
        ):
            contract = order.contract_id.sudo()
            if not contract or order._fix_contract_entitlement_line():
                continue
            types = order._fix_entitlement_types()
            blocked = contract.entitlement_ids.filtered(
                lambda e, types=types: e.exhaustion_policy == "block"
                and e.entitlement_type in types
                and e.quantity_included > 0
                and e.quantity_remaining < 1
            )
            if blocked and not (self.env.su or self.env.user.has_group(MANAGER)):
                raise UserError(
                    "Order %s: the %s entitlement of contract %s is used up and the contract "
                    "says further work needs the Contract Manager."
                    % (order.name, blocked[0].entitlement_type, contract.code)
                )
        return super()._fix_consume_contract_entitlement()


# =============================================================================
# M08-F21: a priced scope change (asset attached / detached) is prorated
# =============================================================================
class FixContractAmendmentScopeMoney(models.Model):
    _inherit = "fix.contract.amendment"

    def _dofa_amount(self) -> float:
        self.ensure_one()
        if self.kind == "scope" and self.delta_value:
            return abs(self.delta_value)
        return super()._dofa_amount()

    def _fix_term_value_delta(self) -> float:
        self.ensure_one()
        if self.kind == "scope" and self.delta_value:
            contract = self.contract_id
            start = max(self.effective_from or contract.date_start, contract.date_start)
            return round(
                self.delta_value / 12.0 * contract._fix_months_between(start, contract.date_end), 2
            )
        return super()._fix_term_value_delta()

    def _amendment_apply(self):
        for rec in self:
            if rec.state == "applied" or rec.kind != "scope" or not rec.delta_value:
                super(FixContractAmendmentScopeMoney, rec)._amendment_apply()
                continue
            contract = rec.contract_id.sudo()
            before = contract.annual_value
            if before + rec.delta_value <= 0:
                raise UserError(
                    "Amendment %s would leave contract %s with no value."
                    % (rec.name, contract.code)
                )
            super(FixContractAmendmentScopeMoney, rec)._amendment_apply()
            if rec.state == "applied":
                after = round(before + rec.delta_value, 2)
                contract._guarded().write({"annual_value": after})
                rec._guarded().write({"value_before": before, "value_after": after})
        return True


# the in-force states, re-exported for the billing hand-off
CONTRACT_IN_FORCE = IN_FORCE
