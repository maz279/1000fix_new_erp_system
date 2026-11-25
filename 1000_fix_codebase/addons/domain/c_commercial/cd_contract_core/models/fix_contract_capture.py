# M08 capture audit, second pass (18 Nov 2026).
#
# The user saw M08 sub-module pages without a relevant capture. Every page had
# a "+ New" after the 13 Nov pass, but measured against the M08 spec several
# pages offered a button for the wrong record and the records the spec asks a
# person to enter had no model at all:
#
# - PM Schedules (FR-CTR-031/032): "+ New PM Schedule" created ONE ad-hoc
#   visit. The visit frequency was a constant per family (AMC 90 days...), so
#   no contract could carry its own preventive or calibration schedule, its
#   lead time or its site access window.          -> fix.contract.pm.plan
# - Coverage Scope (FR-CTR-014, BRU-CTR-01): cover was an enumerated device
#   list only; "everything the customer owns of this type / at this site" was
#   not expressible, and an AMC contract activated covering nothing.
#                                                  -> fix.contract.coverage.rule
# - Entitlement Engine (FR-CTR-020/022, T-01, BRU-CTR-04/16): no top-up of a
#   live contract, no movement ledger behind the balance, and a cancelled
#   order never gave its entitlement back.
#              -> fix.contract.entitlement.topup, fix.contract.entitlement.movement
# - SLA & Service Credits (FR-CTR-028): no credit scheme - by breach type,
#   priority, cumulative frequency and cap.     -> fix.contract.credit.scheme
# - Churn & Win-Back (FR-CTR-040/043, BRU-CTR-12): no dispute flag or legal
#   hold, and a suspended contract resumed with no declared treatment of the
#   suspended period.        -> fix.contract.dispute, action_resume(treatment)
# - Documents & Signature (FR-CTR-011): activation demanded a completed
#   e-signature envelope, so a contract signed in ink - the usual case for a
#   Bangladeshi corporate customer - could never be activated.
#                                         -> signature_method 'wet' + verification
# - Template-Driven Creation (FR-CTR-006, BRU-CTR-19): no named 1000FiX owner
#   and no master/subsidiary link ("Master Agreements" listed every active
#   contract).                              -> owner_id, parent_contract_id
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish

from .fix_contract import ENVELOPE_EDITABLE_STATES, IN_FORCE, MANAGER, OFFICER, require_role

CLOSED_STATES = ("expired", "terminated")
# BRU-CTR-01 applies to the families that cover customer assets. Managed
# services cover the M05 monitored estate, rental its rented units and a
# marketplace agreement no asset at all.
ASSET_COVER_FAMILIES = ("amc", "ramc")


def _device_types(self):
    return self.env["fix.device.model"]._fields["device_type"].selection


def _contracts_of(env, vals_list):
    return env["fix.contract"].browse(
        list({v["contract_id"] for v in vals_list if v.get("contract_id")})
    )


def _assert_draft_term(env, contracts, what):
    """A term of the contract: typed while it is a draft; afterwards it
    changes through an approved amendment (superuser code is trusted)."""
    if env.su:
        return
    require_role(env, OFFICER, what)
    live = contracts.filtered(lambda k: k.state != "draft")
    if live:
        raise UserError(
            "Contract %s is no longer a draft: its %s are fixed with its other terms."
            % (", ".join(live.mapped("code")), what.lower().replace("changing ", ""))
        )


# =============================================================================
# 6 PM Schedules - the preventive / calibration plan (FR-CTR-031/032)
# =============================================================================
class FixContractPmPlan(models.Model):
    _name = "fix.contract.pm.plan"
    _description = "Contract PM / Calibration Plan"
    _order = "contract_id, schedule_type, id"

    name = fields.Char(string="Plan", required=True)
    contract_id = fields.Many2one("fix.contract", required=True, ondelete="cascade", index=True)
    contract_state = fields.Selection(related="contract_id.state", string="Contract Status")
    schedule_type = fields.Selection(
        [
            ("preventive", "Preventive maintenance"),
            ("calibration", "Calibration"),
            ("inspection", "Statutory inspection / certification"),
        ],
        required=True,
        default="preventive",
    )
    device_id = fields.Many2one(
        "fix.device", string="Asset", help="Empty = every asset the contract covers"
    )
    interval_months = fields.Integer(string="Every (months)", required=True, default=3)
    first_due = fields.Date(
        string="First Visit Due", help="Empty = one interval after the contract starts"
    )
    lead_days = fields.Integer(
        string="Lead Time (days)",
        default=7,
        help="How many days before the visit date it is dispatched",
    )
    access_window = fields.Char(
        string="Site Access Window", help="e.g. Sun-Thu 09:00-17:00, not during Ramadan"
    )
    active = fields.Boolean(default=True)
    visit_ids = fields.One2many("fix.contract.pm.visit", "plan_id", string="Visits")
    visit_count = fields.Integer(compute="_compute_visit_count")

    @api.depends("visit_ids")
    def _compute_visit_count(self):
        for rec in self:
            rec.visit_count = len(rec.visit_ids)

    @api.constrains("contract_id", "interval_months", "lead_days")
    def _check_numbers(self):
        for rec in self:
            if not 1 <= rec.interval_months <= 24:
                raise ValidationError("A plan repeats every 1 to 24 months.")
            if rec.lead_days < 0:
                raise ValidationError("The lead time cannot be negative.")

    @api.constrains("first_due", "contract_id")
    def _check_first_due(self):
        for rec in self:
            k = rec.contract_id
            if rec.first_due and not (k.date_start <= rec.first_due <= k.date_end):
                raise ValidationError(
                    "The first visit of plan %s falls outside the contract term %s - %s."
                    % (rec.name, k.date_start, k.date_end)
                )

    def _plan_assert_editable(self, contracts, vals=None):
        if self.env.su:
            return
        require_role(self.env, OFFICER, "Changing a PM plan")
        for k in contracts:
            if k.state in CLOSED_STATES:
                raise UserError("Contract %s is closed: its PM plans are fixed." % k.code)
            if k.state != "draft":
                # on a contract in force a manager may add a plan, retire one
                # or correct its access window; the schedule itself is a term
                require_role(self.env, MANAGER, "Changing the PM plan of a signed contract")
                if vals is not None and set(vals) - {"active", "access_window", "name"}:
                    raise UserError(
                        "Contract %s is signed: a plan's asset, interval and dates are "
                        "fixed. Retire it and add a new one." % k.code
                    )

    @api.model_create_multi
    def create(self, vals_list):
        self._plan_assert_editable(_contracts_of(self.env, vals_list))
        plans = super().create(vals_list)
        today = fields.Date.context_today(self)
        for plan in plans.filtered(lambda p: p.contract_id.state in IN_FORCE):
            plan.contract_id.sudo()._pm_generate_plan(plan, start=today)
        return plans

    def write(self, vals):
        self._plan_assert_editable(self.mapped("contract_id"), vals)
        res = super().write(vals)
        if vals.get("active") is False:
            today = fields.Date.context_today(self)
            future = (
                self.env["fix.contract.pm.visit"]
                .sudo()
                .with_context(active_test=False)
                .search(
                    [
                        ("plan_id", "in", self.ids),
                        ("state", "=", "scheduled"),
                        ("scheduled_date", ">=", today),
                    ]
                )
            )
            future._guarded().write({"state": "skipped", "skip_reason": "PM plan retired"})
        return res

    def unlink(self):
        self._plan_assert_editable(self.mapped("contract_id"))
        if not self.env.su and self.filtered(lambda p: p.contract_id.state != "draft"):
            raise UserError("A plan of a signed contract is retired, not deleted.")
        return super().unlink()

    def _plan_dates(self, start=None):
        """The visit dates of this plan inside the term, on or after `start`."""
        self.ensure_one()
        k = self.contract_id
        step = relativedelta(months=self.interval_months)
        day = self.first_due or (k.date_start + step)
        dates = []
        while day <= k.date_end:
            if not start or day >= start:
                dates.append(day)
            day = day + step
        return dates


class FixContractPmVisitPlan(models.Model):
    _inherit = "fix.contract.pm.visit"

    plan_id = fields.Many2one("fix.contract.pm.plan", string="PM Plan", readonly=True, index=True)
    visit_type = fields.Selection(
        [
            ("preventive", "Preventive maintenance"),
            ("calibration", "Calibration"),
            ("inspection", "Statutory inspection / certification"),
        ],
        default="preventive",
        readonly=True,
    )
    dispatch_from = fields.Date(
        compute="_compute_dispatch_from", store=True, help="Visit date minus the plan's lead time"
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"plan_id", "visit_type"}

    @api.depends("scheduled_date", "plan_id.lead_days")
    def _compute_dispatch_from(self):
        for rec in self:
            lead = rec.plan_id.lead_days or 0
            rec.dispatch_from = rec.scheduled_date and rec.scheduled_date - relativedelta(days=lead)


# =============================================================================
# 3 Coverage Scope - coverage by asset type, brand or site (FR-CTR-014)
# =============================================================================
class FixContractCoverageRule(models.Model):
    _name = "fix.contract.coverage.rule"
    _description = "Contract Coverage Rule"
    _order = "contract_id, id"

    contract_id = fields.Many2one("fix.contract", required=True, ondelete="cascade", index=True)
    contract_state = fields.Selection(related="contract_id.state", string="Contract Status")
    device_type = fields.Selection(selection=_device_types, string="Asset Type")
    brand_id = fields.Many2one("fix.brand", string="Brand")
    site_partner_id = fields.Many2one(
        "res.partner",
        string="Site / Department",
        help="An address or department of the customer: its assets are covered",
    )
    cover_from = fields.Date(help="Empty = the contract start")
    cover_to = fields.Date(help="Empty = the contract end")
    note = fields.Char(string="Rule Wording")

    # keyed to contract_id too: a constraint fires only for the fields written, and
    # a rule naming none of type / brand / site writes none of them
    @api.constrains(
        "contract_id", "device_type", "brand_id", "site_partner_id", "cover_from", "cover_to"
    )
    def _check_rule(self):
        for rec in self:
            if not (rec.device_type or rec.brand_id or rec.site_partner_id):
                raise ValidationError(
                    "A coverage rule names an asset type, a brand or a site; to cover "
                    "named assets, list them on the contract."
                )
            if rec.cover_from and rec.cover_to and rec.cover_from > rec.cover_to:
                raise ValidationError("The rule's cover ends before it starts.")
            customer = rec.contract_id.customer_id.commercial_partner_id
            if rec.site_partner_id and rec.site_partner_id.commercial_partner_id != customer:
                raise ValidationError(
                    "Site %s is not an address of the customer %s."
                    % (rec.site_partner_id.display_name, rec.contract_id.customer_id.name)
                )

    @api.model_create_multi
    def create(self, vals_list):
        _assert_draft_term(self.env, _contracts_of(self.env, vals_list), "Changing coverage rules")
        return super().create(vals_list)

    def write(self, vals):
        contracts = self.mapped("contract_id")
        if vals.get("contract_id"):
            contracts |= self.env["fix.contract"].browse(vals["contract_id"])
        _assert_draft_term(self.env, contracts, "Changing coverage rules")
        return super().write(vals)

    def unlink(self):
        _assert_draft_term(self.env, self.mapped("contract_id"), "Changing coverage rules")
        return super().unlink()

    def _rule_window(self):
        self.ensure_one()
        k = self.contract_id
        return self.cover_from or k.date_start, self.cover_to or k.date_end

    def _rule_matches(self, device, day):
        """Does this rule cover `device` on `day`? The asset must belong to
        the contract's customer (or one of its addresses)."""
        self.ensure_one()
        start, end = self._rule_window()
        if not (start <= day <= end):
            return False
        customer = self.contract_id.customer_id.commercial_partner_id
        owner = device.owner_id
        if not owner or owner.commercial_partner_id != customer:
            return False
        if self.device_type and device.device_type != self.device_type:
            return False
        if self.brand_id and device.brand_id != self.brand_id:
            return False
        if self.site_partner_id:
            site = self.site_partner_id
            node = owner
            while node and node != site:
                node = node.parent_id
            if node != site:
                return False
        return True


# =============================================================================
# 4 Entitlement Engine - the movement ledger and top-ups (FR-CTR-020/022, T-01)
# =============================================================================
MOVEMENT_TYPES = [
    ("grant", "Granted at activation"),
    ("consume", "Consumed"),
    ("restore", "Restored"),
    ("topup", "Top-up"),
    ("prorate", "Prorated (reinstatement)"),
]


class FixContractEntitlementMovement(models.Model):
    """Append-only: every change of an entitlement balance, with its source
    document (T-01, BRU-CTR-16). Written by the engine, never by a person."""

    _name = "fix.contract.entitlement.movement"
    _description = "Contract Entitlement Movement"
    _order = "moved_on desc, id desc"

    entitlement_id = fields.Many2one(
        "fix.contract.entitlement", required=True, ondelete="cascade", index=True, readonly=True
    )
    contract_id = fields.Many2one(
        related="entitlement_id.contract_id", store=True, index=True, string="Contract"
    )
    entitlement_type = fields.Selection(related="entitlement_id.entitlement_type")
    movement_type = fields.Selection(MOVEMENT_TYPES, required=True, readonly=True)
    quantity = fields.Float(required=True, readonly=True, help="Signed: a draw-down is negative")
    balance_after = fields.Float(readonly=True, help="-1 = unlimited")
    source_ref = fields.Char(string="Source Document", readonly=True)
    actor_id = fields.Many2one("res.users", string="By", readonly=True)
    moved_on = fields.Datetime(readonly=True, default=fields.Datetime.now)

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.context.get("fix_entitlement_ledger"):
            raise UserError(
                "The entitlement ledger is written by the engine (draw-down, top-up, "
                "restoration); it cannot be typed."
            )
        return super().create(vals_list)

    def write(self, vals):
        raise UserError("The entitlement ledger is append-only: a movement is never edited.")

    def unlink(self):
        raise UserError("The entitlement ledger is append-only: a movement is never deleted.")


class FixContractEntitlementLedger(models.Model):
    _inherit = "fix.contract.entitlement"

    movement_ids = fields.One2many(
        "fix.contract.entitlement.movement", "entitlement_id", string="Movements"
    )
    contract_state = fields.Selection(related="contract_id.state", string="Contract Status")

    def _ledger(self, movement_type, quantity, source_ref=""):
        Movement = self.env["fix.contract.entitlement.movement"].sudo()
        for ent in self:
            Movement.with_context(fix_entitlement_ledger=True).create(
                {
                    "entitlement_id": ent.id,
                    "movement_type": movement_type,
                    "quantity": quantity,
                    "balance_after": ent.quantity_remaining,
                    "source_ref": source_ref or False,
                    "actor_id": self.env.uid,
                }
            )

    def consume(self, qty: float, source_ref: str = "") -> bool:
        before = {ent.id: ent.quantity_consumed for ent in self}
        result = super().consume(qty, source_ref=source_ref)
        for ent in self:
            if ent.quantity_consumed != before[ent.id]:
                ent._ledger("consume", -(ent.quantity_consumed - before[ent.id]), source_ref)
        return result

    def restore(self, qty: float, source_ref: str = "") -> bool:
        """BRU-CTR-04 / AUT-CTR-05: give back what a cancelled or reworked
        order drew. Never below zero consumed; the caller makes it once."""
        require_role(self.env, OFFICER, "Restoring a contract entitlement")
        for ent in self:
            give = min(qty, ent.quantity_consumed)
            if give <= 0:
                continue
            ent.sudo()._guarded().write({"quantity_consumed": ent.quantity_consumed - give})
            ent._ledger("restore", give, source_ref)
        return True


class FixContractEntitlementTopup(models.Model):
    """FR-CTR-022: more entitlement sold mid-term, applied once a Contract
    Manager who did not raise it accepts it; billed through M39 from the
    contract.entitlement_topped_up event."""

    _name = "fix.contract.entitlement.topup"
    _description = "Contract Entitlement Top-Up"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "id desc"

    name = fields.Char(string="Top-Up Reference", required=True, tracking=True)
    entitlement_id = fields.Many2one(
        "fix.contract.entitlement", string="Entitlement", required=True, index=True
    )
    contract_id = fields.Many2one(
        related="entitlement_id.contract_id", store=True, string="Contract", index=True
    )
    quantity = fields.Float(string="Additional Quantity", required=True)
    customer_reference = fields.Char(
        string="Customer Acceptance",
        required=True,
        help="The accepted quotation or the customer's purchase order number",
    )
    currency_id = fields.Many2one(related="entitlement_id.contract_id.currency_id")
    amount = fields.Monetary(string="Price Charged", currency_field="currency_id")
    reason = fields.Text()
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("submitted", "Awaiting Manager"),
            ("applied", "Applied"),
            ("rejected", "Rejected"),
        ],
        default="draft",
        required=True,
        readonly=True,
        tracking=True,
    )
    requested_by = fields.Many2one(
        "res.users", readonly=True, default=lambda self: self.env.user, copy=False
    )
    decided_by = fields.Many2one("res.users", readonly=True, copy=False)
    decided_on = fields.Datetime(readonly=True, copy=False)
    reject_reason = fields.Text(readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "requested_by",
            "decided_by",
            "decided_on",
            "reject_reason",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if len(self) == 1 and self.state != "draft":
            locked |= {
                "name",
                "entitlement_id",
                "quantity",
                "customer_reference",
                "amount",
                "reason",
            }
        return locked

    @api.constrains("quantity", "entitlement_id")
    def _check_topup(self):
        for rec in self:
            if rec.quantity <= 0:
                raise ValidationError("A top-up adds a positive quantity.")
            if rec.entitlement_id.quantity_included == 0:
                raise ValidationError(
                    "Entitlement %s is unlimited: there is nothing to top up."
                    % rec.entitlement_id.display_name
                )

    @api.model_create_multi
    def create(self, vals_list):
        require_role(self.env, OFFICER, "Raising an entitlement top-up")
        recs = super().create(vals_list)
        for rec in recs:
            rec._topup_assert_contract()
        return recs

    def write(self, vals):
        if self and not self._fix_guard_open():
            done = self.filtered(lambda r: r.state != "draft")
            if done and set(vals) - {"message_main_attachment_id"}:
                raise UserError(
                    "Top-up %s is %s: it is no longer edited." % (done[0].name, done[0].state)
                )
        return super().write(vals)

    def _topup_assert_contract(self):
        k = self.contract_id
        if k.state not in IN_FORCE:
            raise UserError(
                "Contract %s is %s: only a contract in force is topped up (a draft's "
                "entitlement is simply edited)."
                % (k.code, dict(k._fields["state"].selection)[k.state])
            )

    def action_submit(self):
        require_role(self.env, OFFICER, "Submitting an entitlement top-up")
        for rec in self:
            if rec.state != "draft":
                raise UserError("Top-up %s is already %s." % (rec.name, rec.state))
            rec._topup_assert_contract()
            rec.sudo()._guarded().write({"state": "submitted"})
        return True

    def action_apply(self):
        """A Contract Manager who did not raise it applies the top-up: the
        entitlement grows, the ledger records it, M39 bills it."""
        require_role(self.env, MANAGER, "Applying an entitlement top-up")
        for rec in self:
            if rec.state != "submitted":
                raise UserError("Top-up %s is %s, not awaiting a manager." % (rec.name, rec.state))
            if not self.env.su and rec.requested_by == self.env.user:
                raise UserError(
                    "Top-up %s: whoever raised it cannot apply it (segregation of duties)."
                    % rec.name
                )
            rec._topup_assert_contract()
            ent = rec.entitlement_id.sudo()
            ent._guarded().write({"quantity_included": ent.quantity_included + rec.quantity})
            ent._ledger("topup", rec.quantity, rec.name)
            rec.sudo()._guarded().write(
                {
                    "state": "applied",
                    "decided_by": self.env.uid,
                    "decided_on": fields.Datetime.now(),
                }
            )
            publish(
                self.env,
                "contract.entitlement_topped_up",
                "fix.contract",
                rec.contract_id.id,
                {
                    "code": rec.contract_id.code,
                    "topup_id": rec.id,
                    "entitlement_type": ent.entitlement_type,
                    "quantity": rec.quantity,
                    "amount": float(rec.amount or 0.0),
                    "customer_reference": rec.customer_reference,
                },
            )
        return True

    def action_reject(self, reason=None):
        require_role(self.env, MANAGER, "Rejecting an entitlement top-up")
        reason = (reason or "").strip()
        if not reason:
            raise UserError("State why the top-up is rejected.")
        for rec in self:
            if rec.state != "submitted":
                raise UserError("Top-up %s is %s, not awaiting a manager." % (rec.name, rec.state))
            rec.sudo()._guarded().write(
                {
                    "state": "rejected",
                    "reject_reason": reason,
                    "decided_by": self.env.uid,
                    "decided_on": fields.Datetime.now(),
                }
            )
        return True


# =============================================================================
# 5 SLA & Service Credits - the credit scheme (FR-CTR-028)
# =============================================================================
BREACH_TYPES = [
    ("response", "Response time"),
    ("onsite", "On-site arrival"),
    ("restoration", "Restoration"),
    ("resolution", "Resolution"),
    ("availability", "Availability / uptime"),
]


class FixContractCreditScheme(models.Model):
    _name = "fix.contract.credit.scheme"
    _description = "Contract Service Credit Scheme"
    _order = "contract_id, breach_type, priority, id"

    contract_id = fields.Many2one("fix.contract", required=True, ondelete="cascade", index=True)
    contract_state = fields.Selection(related="contract_id.state", string="Contract Status")
    breach_type = fields.Selection(BREACH_TYPES, required=True, default="response")
    priority = fields.Selection(
        [
            ("any", "Any priority"),
            ("p1", "P1 - critical"),
            ("p2", "P2 - high"),
            ("p3", "P3 - normal"),
            ("p4", "P4 - low"),
        ],
        required=True,
        default="any",
    )
    credit_basis = fields.Selection(
        [("pct_fee", "% of the period fee"), ("fixed", "Fixed amount (BDT)")],
        required=True,
        default="pct_fee",
    )
    credit_value = fields.Float(required=True, help="Per breach: a percentage or an amount")
    cumulative_rule = fields.Selection(
        [
            ("per_breach", "Same credit for every breach"),
            ("escalating", "Escalating: the n-th breach in the period earns n x the credit"),
        ],
        required=True,
        default="per_breach",
    )
    cap_pct = fields.Float(
        string="Cap (% of period fee)",
        required=True,
        default=10.0,
        help="Most this rule can credit",
    )
    note = fields.Char(string="Clause Reference")

    @api.constrains("contract_id", "credit_value", "cap_pct", "credit_basis")
    def _check_values(self):
        for rec in self:
            if rec.credit_value <= 0:
                raise ValidationError("A service credit is a positive value.")
            if not 0 < rec.cap_pct <= 100:
                raise ValidationError(
                    "The cap is a share of the period fee, above 0 and at most 100%."
                )
            if rec.credit_basis == "pct_fee" and rec.credit_value > 100:
                raise ValidationError("A credit cannot exceed the period fee.")

    @api.model_create_multi
    def create(self, vals_list):
        _assert_draft_term(
            self.env, _contracts_of(self.env, vals_list), "Changing service credit rules"
        )
        return super().create(vals_list)

    def write(self, vals):
        _assert_draft_term(self.env, self.mapped("contract_id"), "Changing service credit rules")
        return super().write(vals)

    def unlink(self):
        _assert_draft_term(self.env, self.mapped("contract_id"), "Changing service credit rules")
        return super().unlink()

    def _scheme_credit(self, breaches, period_fee):
        """The credit this rule earns for `breaches` of its type in one
        period, capped. `breaches` is the count."""
        self.ensure_one()
        if breaches <= 0 or period_fee <= 0:
            return 0.0
        unit = (
            period_fee * self.credit_value / 100.0
            if self.credit_basis == "pct_fee"
            else self.credit_value
        )
        multiplier = (
            breaches if self.cumulative_rule == "per_breach" else breaches * (breaches + 1) / 2.0
        )
        return round(min(unit * multiplier, period_fee * self.cap_pct / 100.0), 2)


# =============================================================================
# 9 Churn & Win-Back - disputes and legal hold (FR-CTR-043, BRU-CTR-12)
# =============================================================================
class FixContractDispute(models.Model):
    _name = "fix.contract.dispute"
    _description = "Contract Dispute"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "state, opened_on desc, id desc"

    name = fields.Char(string="Dispute", required=True, tracking=True)
    contract_id = fields.Many2one("fix.contract", required=True, index=True, ondelete="restrict")
    contract_state = fields.Selection(related="contract_id.state", string="Contract Status")
    raised_by_party = fields.Selection(
        [("customer", "Customer"), ("us", "1000FiX")], required=True, default="customer"
    )
    opened_on = fields.Date(required=True, default=fields.Date.context_today)
    description = fields.Text(string="What Is Disputed", required=True)
    state = fields.Selection(
        [("open", "Open"), ("resolved", "Resolved")],
        default="open",
        required=True,
        readonly=True,
        tracking=True,
    )
    resolution = fields.Text(readonly=True, copy=False)
    resolved_by = fields.Many2one("res.users", readonly=True, copy=False)
    resolved_on = fields.Datetime(readonly=True, copy=False)
    held_document_ids = fields.Many2many(
        "fix.document", string="Documents Held", readonly=True, copy=False
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "resolution",
            "resolved_by",
            "resolved_on",
            "held_document_ids",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if len(self) == 1 and self.state == "resolved":
            locked |= {"name", "contract_id", "raised_by_party", "opened_on", "description"}
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        require_role(self.env, OFFICER, "Flagging a contract dispute")
        recs = super().create(vals_list)
        for rec in recs:
            if rec.contract_id.state == "draft":
                raise UserError(
                    "Contract %s is a draft: there is no agreement to dispute yet."
                    % rec.contract_id.code
                )
            rec._dispute_hold_documents()
            rec.contract_id.message_post(body="Dispute %s opened: %s" % (rec.name, rec.description))
            publish(
                self.env,
                "contract.dispute_opened",
                "fix.contract",
                rec.contract_id.id,
                {
                    "code": rec.contract_id.code,
                    "dispute_id": rec.id,
                    "raised_by": rec.raised_by_party,
                },
            )
        return recs

    def write(self, vals):
        if self and not self._fix_guard_open():
            if self.filtered(lambda r: r.state == "resolved") and set(vals) - {
                "message_main_attachment_id"
            }:
                raise UserError("A resolved dispute is closed.")
            if "contract_id" in vals:
                raise UserError("A dispute stays on the contract it was raised against.")
        return super().write(vals)

    def unlink(self):
        if not self.env.su:
            raise UserError(
                "A dispute is resolved, not deleted: it is part of the contract record."
            )
        return super().unlink()

    def _dispute_hold_documents(self):
        """BRU-CTR-12: the contract's documents go on M24 legal hold (through
        the hold register) for as long as the dispute is open."""
        self.ensure_one()
        docs = self.contract_id.sudo()._contract_documents().filtered(lambda d: not d.legal_hold)
        if docs:
            docs.sudo().action_legal_hold(
                "Contract dispute %s (%s)" % (self.name, self.contract_id.code)
            )
        self.sudo()._guarded().write({"held_document_ids": [(6, 0, docs.ids)]})

    def action_resolve(self, resolution=None):
        """A Contract Manager who did not open it closes the dispute with the
        resolution; the holds it placed are released unless another open
        dispute of the contract still needs them."""
        require_role(self.env, MANAGER, "Resolving a contract dispute")
        resolution = (resolution or "").strip()
        if not resolution:
            raise UserError("State how the dispute was resolved.")
        for rec in self:
            if rec.state != "open":
                raise UserError("Dispute %s is already resolved." % rec.name)
            if not self.env.su and rec.create_uid == self.env.user:
                raise UserError(
                    "Dispute %s: whoever opened it cannot close it (segregation of duties)."
                    % rec.name
                )
            rec.sudo()._guarded().write(
                {
                    "state": "resolved",
                    "resolution": resolution,
                    "resolved_by": self.env.uid,
                    "resolved_on": fields.Datetime.now(),
                }
            )
            still_held = (
                self.sudo()
                .search([("contract_id", "=", rec.contract_id.id), ("state", "=", "open")])
                .mapped("held_document_ids")
            )
            release = (rec.held_document_ids - still_held).filtered("legal_hold")
            if release:
                release.sudo().action_release_hold(
                    "Dispute %s resolved: %s" % (rec.name, resolution)
                )
            publish(
                self.env,
                "contract.dispute_resolved",
                "fix.contract",
                rec.contract_id.id,
                {"code": rec.contract_id.code, "dispute_id": rec.id},
            )
        return True


# =============================================================================
# The contract side
# =============================================================================
REINSTATEMENT_TREATMENTS = [
    ("extend_term", "Restored: the term is extended by the suspended days"),
    ("forfeit", "Forfeited: the suspended period is lost"),
    ("prorate", "Prorated: entitlement reduced for the suspended days"),
]


class FixContractCapture(models.Model):
    _inherit = "fix.contract"

    # --- 1 owner and master agreement (BRU-CTR-19, FR-CTR-006) -------------
    owner_id = fields.Many2one(
        "res.users",
        string="Contract Owner (1000FiX)",
        tracking=True,
        domain=[("share", "=", False)],
        default=lambda self: self.env.user if not self.env.su else False,
        help="The named 1000FiX owner the contract carries at all times",
    )
    parent_contract_id = fields.Many2one(
        "fix.contract",
        string="Master Agreement",
        index=True,
        domain=[("parent_contract_id", "=", False)],
        help="Set on a subsidiary contract: the master agreement it rolls up to",
    )
    child_contract_ids = fields.One2many(
        "fix.contract", "parent_contract_id", string="Subsidiary Contracts"
    )
    subsidiary_count = fields.Integer(compute="_compute_subsidiary_count", store=True)
    is_master_agreement = fields.Boolean(compute="_compute_subsidiary_count", store=True)

    # --- 3 coverage rules / 5 credit scheme / 6 PM plans -------------------
    coverage_rule_ids = fields.One2many(
        "fix.contract.coverage.rule", "contract_id", string="Coverage Rules", copy=True
    )
    credit_scheme_ids = fields.One2many(
        "fix.contract.credit.scheme", "contract_id", string="Service Credit Scheme", copy=True
    )
    pm_plan_ids = fields.One2many(
        "fix.contract.pm.plan", "contract_id", string="PM Plans", copy=True
    )

    # --- 9 disputes and reinstatement (FR-CTR-040/043) ---------------------
    dispute_ids = fields.One2many("fix.contract.dispute", "contract_id", string="Disputes")
    in_dispute = fields.Boolean(compute="_compute_in_dispute", store=True)
    suspended_on = fields.Date(readonly=True, copy=False)
    reinstatement_treatment = fields.Selection(
        REINSTATEMENT_TREATMENTS, string="Suspended-Period Treatment", readonly=True, copy=False
    )
    reinstatement_note = fields.Text(readonly=True, copy=False)
    reinstated_by = fields.Many2one("res.users", readonly=True, copy=False)
    reinstated_on = fields.Datetime(readonly=True, copy=False)

    # --- 11 wet-ink signature (FR-CTR-011) ---------------------------------
    signature_method = fields.Selection(
        [("electronic", "Electronic (M24 envelope)"), ("wet", "Wet ink (scanned original)")],
        required=True,
        default="electronic",
        tracking=True,
    )
    wet_signed_on = fields.Date(string="Signed On (ink)", copy=False)
    wet_signed_file_id = fields.Many2one(
        "ir.attachment",
        string="Scanned Signed Original (upload)",
        copy=False,
        help="Filed in Document Management (M24) as the contract's signed original",
    )
    wet_signed_document_id = fields.Many2one(
        "fix.document", string="Signed Original (M24)", copy=False
    )
    wet_signature_recorded_by = fields.Many2one("res.users", readonly=True, copy=False)
    wet_signature_verified_by = fields.Many2one("res.users", readonly=True, copy=False)
    wet_signature_verified_on = fields.Datetime(readonly=True, copy=False)

    WET_FIELDS = (
        "signature_method",
        "wet_signed_on",
        "wet_signed_file_id",
        "wet_signed_document_id",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "suspended_on",
            "reinstatement_treatment",
            "reinstatement_note",
            "reinstated_by",
            "reinstated_on",
            "wet_signature_recorded_by",
            "wet_signature_verified_by",
            "wet_signature_verified_on",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if len(self) == 1:
            if self.state != "draft":
                locked.add("parent_contract_id")
            if self.state not in ENVELOPE_EDITABLE_STATES:
                locked |= set(self.WET_FIELDS)
        return locked

    @api.depends("child_contract_ids")
    def _compute_subsidiary_count(self):
        for rec in self:
            rec.subsidiary_count = len(rec.child_contract_ids)
            rec.is_master_agreement = bool(rec.child_contract_ids)

    @api.depends("dispute_ids.state")
    def _compute_in_dispute(self):
        for rec in self:
            rec.in_dispute = any(d.state == "open" for d in rec.dispute_ids)

    @api.constrains("parent_contract_id", "customer_id")
    def _check_master(self):
        for rec in self:
            parent = rec.parent_contract_id
            if not parent:
                continue
            if parent == rec or parent.parent_contract_id:
                raise ValidationError(
                    "A master agreement is a top-level contract: %s cannot be the master of %s."
                    % (parent.code, rec.code)
                )
            if rec.child_contract_ids:
                raise ValidationError(
                    "%s has subsidiaries: it is a master, not a subsidiary." % rec.code
                )
            if parent.customer_id.commercial_partner_id != rec.customer_id.commercial_partner_id:
                raise ValidationError(
                    "Master agreement %s belongs to %s, not to %s."
                    % (parent.code, parent.customer_id.name, rec.customer_id.name)
                )

    def write(self, vals):
        if self and not self._fix_guard_open():
            if "parent_contract_id" in vals:
                frozen = self.filtered(
                    lambda r: r.state != "draft"
                    and r._fix_guard_differs(
                        "parent_contract_id", vals["parent_contract_id"], r.parent_contract_id
                    )
                )
                if frozen:
                    raise UserError(
                        "The master agreement of contract %s is fixed once it leaves draft."
                        % frozen[0].code
                    )
            wet = set(vals) & set(self.WET_FIELDS)
            if wet:
                moved = self.filtered(
                    lambda r: any(r._fix_guard_differs(n, vals[n], r[n]) for n in wet)
                )
                late = moved.filtered(lambda r: r.state not in ENVELOPE_EDITABLE_STATES)
                if late:
                    raise UserError(
                        "Contract %s is signed: how and when it was signed is part of the record."
                        % late[0].code
                    )
                res = super().write(vals)
                if "wet_signed_file_id" in vals:
                    moved._wet_file_signed_original()
                if moved:
                    # a changed scan or date is a new claim: verified afresh
                    moved._guarded().write(
                        {
                            "wet_signature_recorded_by": self.env.uid,
                            "wet_signature_verified_by": False,
                            "wet_signature_verified_on": False,
                        }
                    )
                return res
        if vals.get("state") == "suspended" and "suspended_on" not in vals:
            vals = dict(vals, suspended_on=fields.Date.context_today(self))
        return super().write(vals)

    def _wet_file_signed_original(self):
        """An uploaded scan becomes the contract's signed original in M24, so
        it is checksummed, retained and can be put on legal hold."""
        Doc = self.env["fix.document"].sudo()
        for rec in self.filtered("wet_signed_file_id"):
            if rec.wet_signed_document_id.attachment_id == rec.wet_signed_file_id:
                continue
            doc = Doc.create(
                {
                    "name": "Signed original %s" % (rec.code or rec.name),
                    "attachment_id": rec.wet_signed_file_id.id,
                    "document_type": "contract",
                    "res_model": "fix.contract",
                    "res_id": rec.id,
                    "company_id": rec.company_id.id,
                    "operating_unit_id": rec.operating_unit_id.id,
                }
            )
            rec._guarded().write({"wet_signed_document_id": doc.id})

    # --- cover --------------------------------------------------------------
    def _contract_covers_device(self, device, day=None):
        """Is `device` covered by this contract on `day`: listed by name, or
        caught by a coverage rule (FR-CTR-013/014)?"""
        self.ensure_one()
        day = day or fields.Date.context_today(self)
        if device in self.covered_device_ids:
            return True
        return any(rule._rule_matches(device, day) for rule in self.coverage_rule_ids)

    def _pm_devices(self, day=None):
        """The assets a preventive schedule visits: the listed ones and those
        a coverage rule catches today among the customer's registered assets."""
        self.ensure_one()
        devices = self.covered_device_ids
        if self.coverage_rule_ids:
            day = day or fields.Date.context_today(self)
            owned = (
                self.env["fix.device"]
                .sudo()
                .search([("owner_id", "child_of", self.customer_id.commercial_partner_id.id)])
            )
            devices |= owned.filtered(
                lambda d: any(
                    r._rule_matches(d, max(day, r._rule_window()[0]))
                    for r in self.coverage_rule_ids
                )
            )
        return devices

    def _contract_documents(self):
        """Every M24 document of the contract: the signed copy (envelope or
        ink), obligation evidence and documents filed against it."""
        self.ensure_one()
        docs = (
            self.env["fix.document"]
            .sudo()
            .search([("res_model", "=", "fix.contract"), ("res_id", "=", self.id)])
        )
        docs |= self.esignature_envelope_id.sudo().document_id
        docs |= self.wet_signed_document_id.sudo()
        docs |= self.obligation_ids.sudo().mapped("evidence_document_id")
        return docs

    # --- PM generation from the plans ----------------------------------------
    def _pm_generate_plan(self, plan, start=None, devices=None):
        Visit = self.env["fix.contract.pm.visit"].sudo()._guarded()
        made = Visit.browse()
        targets = plan.device_id or (devices if devices is not None else self._pm_devices())
        for day in plan._plan_dates(start=start):
            for device in targets:
                made |= Visit.create(
                    {
                        "contract_id": self.id,
                        "device_id": device.id,
                        "scheduled_date": day,
                        "state": "scheduled",
                        "plan_id": plan.id,
                        "visit_type": plan.schedule_type,
                    }
                )
        return made

    def _generate_pm_schedule(self):
        """T06 at activation: the contract's own plans when it has any;
        otherwise the family's standard interval over the covered assets
        (listed or caught by a coverage rule)."""
        plans = self.pm_plan_ids.filtered("active")
        if plans:
            for plan in plans:
                self._pm_generate_plan(plan)
            return
        if self.coverage_rule_ids and not self.covered_device_ids:
            devices = self._pm_devices()
            if devices:
                self._generate_pm_schedule_for(devices, self.date_start)
            return
        return super()._generate_pm_schedule()

    def _generate_pm_schedule_for(self, devices, start):
        plans = self.pm_plan_ids.filtered(lambda p: p.active and not p.device_id)
        if plans:
            made = self.env["fix.contract.pm.visit"]
            for plan in plans:
                made |= self._pm_generate_plan(plan, start=start, devices=devices)
            return made
        return super()._generate_pm_schedule_for(devices, start)

    # --- submission, signature, activation -----------------------------------
    def action_request_approval(self, justification=None):
        for rec in self.filtered(lambda r: not r.owner_id):
            # BRU-CTR-19: a contract never goes forward without a named owner
            rec.sudo()._guarded().write({"owner_id": self.env.uid})
        return super().action_request_approval(justification=justification)

    def _wet_signature_problems(self):
        self.ensure_one()
        problems = []
        doc = self.wet_signed_document_id.sudo()
        if not doc:
            problems.append("no scanned signed original is attached")
        elif not doc.attachment_id:
            problems.append("the signed original has no file")
        if not self.wet_signed_on:
            problems.append("the signing date is not recorded")
        elif self.wet_signed_on > fields.Date.context_today(self):
            problems.append("the signing date is in the future")
        if not self.wet_signature_verified_by:
            problems.append("the scanned original is not verified by a second officer")
        return problems

    def _contract_envelope_problems(self):
        if self.signature_method == "wet":
            return self._wet_signature_problems()
        return super()._contract_envelope_problems()

    def _contract_signed_document(self):
        self.ensure_one()
        if self.signature_method == "wet":
            if self.wet_signature_verified_by and self.wet_signed_document_id.attachment_id:
                return self.wet_signed_document_id
            return self.env["fix.document"]
        return super()._contract_signed_document()

    def action_verify_wet_signature(self):
        """A second Contract Officer checks the scan against the original:
        the customer's signature, the date, every page initialled."""
        require_role(self.env, OFFICER, "Verifying a wet-ink signature")
        for rec in self:
            if rec.signature_method != "wet":
                raise UserError(
                    "Contract %s is signed electronically, through its envelope." % rec.code
                )
            if rec.state not in ENVELOPE_EDITABLE_STATES:
                raise UserError("Contract %s is already signed and in force." % rec.code)
            problems = [p for p in rec._wet_signature_problems() if "verified" not in p]
            if problems:
                raise UserError("Contract %s: %s." % (rec.code, "; ".join(problems)))
            if not self.env.su and rec.wet_signature_recorded_by == self.env.user:
                raise UserError(
                    "Contract %s: whoever recorded the signed original cannot verify it "
                    "(segregation of duties)." % rec.code
                )
            rec.sudo()._guarded().write(
                {
                    "wet_signature_verified_by": self.env.uid,
                    "wet_signature_verified_on": fields.Datetime.now(),
                }
            )
            rec.message_post(body="Wet-ink signature verified by %s." % self.env.user.name)
        return True

    def action_activate(self):
        if not self.env.su:
            for rec in self:
                if (
                    rec.family in ASSET_COVER_FAMILIES
                    and not rec.covered_device_ids
                    and not rec.coverage_rule_ids
                ):
                    raise UserError(
                        "Contract %s covers nothing: list its covered assets or add a "
                        "coverage rule before it is activated (BRU-CTR-01)." % rec.code
                    )
        res = super().action_activate()
        for rec in self.filtered(lambda r: r.state in IN_FORCE):
            granted = rec.entitlement_ids.filtered(
                lambda e: not e.movement_ids.filtered(lambda m: m.movement_type == "grant")
            )
            for ent in granted:
                ent._ledger("grant", ent.quantity_included, rec.code)
            if rec.signature_method == "wet" and rec.wet_signed_document_id:
                rec.wet_signed_document_id.sudo().write({"signature_locked": True})
        return res

    # --- reinstatement (FR-CTR-040) ------------------------------------------
    def action_resume(self, treatment=None, note=None):
        """Suspended -> Active with a DECLARED treatment of the suspended
        period: the term extended by the suspended days, the period
        forfeited, or each counted entitlement prorated down."""
        require_role(self.env, MANAGER, "Resuming a suspended contract")
        if treatment not in dict(REINSTATEMENT_TREATMENTS):
            if not self.env.su:
                raise UserError(
                    "Declare how the suspended period is treated: term extended, "
                    "forfeited or entitlement prorated."
                )
            treatment = "forfeit"
        today = fields.Date.context_today(self)
        for rec in self:
            rec._contract_require_state(("suspended",), "be resumed")
            days = max((today - rec.suspended_on).days, 0) if rec.suspended_on else 0
            vals = {
                "reinstatement_treatment": treatment,
                "reinstatement_note": (note or "").strip() or False,
                "reinstated_by": self.env.uid,
                "reinstated_on": fields.Datetime.now(),
                "suspended_on": False,
            }
            if treatment == "extend_term" and days:
                vals["date_end"] = rec.date_end + relativedelta(days=days)
            rec.sudo()._guarded().write(vals)
            if treatment == "prorate" and days:
                term = max((rec.date_end - rec.date_start).days + 1, 1)
                for ent in rec.entitlement_ids.filtered(lambda e: e.quantity_included > 0):
                    cut = round(ent.quantity_included * days / term, 2)
                    cut = min(cut, ent.quantity_included - ent.quantity_consumed)
                    if cut > 0:
                        ent.sudo()._guarded().write(
                            {"quantity_included": ent.quantity_included - cut}
                        )
                        ent._ledger(
                            "prorate", -cut, "Reinstatement after %d suspended day(s)" % days
                        )
        return super().action_resume()


class FixServiceOrderEntitlementRestore(models.Model):
    """AUT-CTR-05 / BRU-CTR-04: a cancelled order gives back what it drew."""

    _inherit = "fix.service.order"

    contract_entitlement_restored = fields.Boolean(readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        return set(super()._fix_guarded_fields()) | {"contract_entitlement_restored"}

    def action_cancel(self, *args, **kwargs):
        res = super().action_cancel(*args, **kwargs)
        for order in self.filtered(
            lambda o: o.state == "cancelled"
            and o.contract_entitlement_id
            and not o.contract_entitlement_restored
        ):
            order.contract_entitlement_id.sudo().restore(
                order.contract_entitlement_qty or 1.0, source_ref="%s cancelled" % order.name
            )
            order.sudo()._guarded().write({"contract_entitlement_restored": True})
        return res
