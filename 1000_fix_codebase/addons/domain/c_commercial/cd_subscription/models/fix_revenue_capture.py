# cd_subscription: M53 sub-module capture audit (2026-11-17).
#
# Two spec records that the M53 workspace had no way to capture:
#
#   * fix.ssp (FR-REV-006 P0, AUT-REV-03): the stand-alone selling price of
#     an obligation type (optionally per plan) with its method and tolerance
#     band, approved by a second person and then frozen; a change is a new
#     price that supersedes the old one from its effective date. Page 2
#     "Allocation & SSP" used to offer a new Performance Obligation, and the
#     SSP of every obligation was typed on the contract with nothing to check
#     it against. Allocating the price of a contract with more than one
#     obligation now refuses an obligation whose typed SSP is outside the
#     band of the approved SSP in force, and each obligation records which
#     SSP (or none) its allocation used.
#   * fix.contract.modification (FR-REV-008 P1, BRU-REV-04 H, AUT-REV-06): a
#     change to a scheduled contract and its accounting treatment. Page 4
#     "Modifications & Reversals" used to offer a new Subscription, and the
#     system told the user to "cancel and re-create the affected
#     obligations", which threw away the schedule history. Now a modification
#     is requested with its reason and evidence and approved by an Accounting
#     Administrator who did not request it. On approval each scheduled
#     obligation is recognised up to the modification date, its schedule is
#     closed (kept, never edited) and a NEW schedule version recognises the
#     re-allocated remainder; a cumulative catch-up becomes a manual schedule
#     for the CFO (BRU-REV-01); a separate contract only records the link.
from __future__ import annotations

from datetime import timedelta
from decimal import ROUND_HALF_UP, Decimal

from odoo import api, fields, models
from odoo.addons.cd_billing_engine.models.fix_finance_approval import (
    GROUP_ACCOUNTANT,
    GROUP_ADMINISTRATOR,
    require_role,
)
from odoo.exceptions import UserError, ValidationError

from .fix_subscription import OBLIGATION_TYPES

TWO = Decimal("0.01")
LOCK_EXEMPT = {"message_main_attachment_id"}
MOD_SOURCE = "fix.contract.modification.line"


def _require_other_person(env, users, what):
    """Maker-checker: the acting user is none of `users`. Superuser service
    code acts for nobody."""
    if env.su:
        return
    if env.user in users.filtered(lambda u: u):
        raise UserError(
            "Segregation of duties: %s must be done by someone other than %s."
            % (what, ", ".join(users.filtered(lambda u: u).mapped("name")))
        )


def _locked_write(records, vals, open_states, what):
    trusted = records.env.su or records._fix_guard_has_token()
    if trusted or not set(vals) - LOCK_EXEMPT:
        return
    if any(rec.state not in open_states for rec in records):
        raise UserError("%s is a record of what was decided and cannot be edited." % what)


def _split(total, weights):
    """`total` split by `weights` at 2dp half-up, the residue on the largest
    weight, so the parts sum EXACTLY to the total (BRU-REV-05)."""
    price = Decimal(str(total)).quantize(TWO, ROUND_HALF_UP)
    weights = [Decimal(str(w)) for w in weights]
    base = sum(weights, Decimal("0"))
    if base <= 0:
        raise UserError("The obligations carry no standalone price to allocate by.")
    shares = [(price * w / base).quantize(TWO, ROUND_HALF_UP) for w in weights]
    largest = max(range(len(weights)), key=lambda i: weights[i])
    shares[largest] += price - sum(shares, Decimal("0"))
    return [float(s) for s in shares]


# --------------------------------------------------------------------------- SSP
SSP_METHODS = [
    ("observable", "Observable (sold separately)"),
    ("adjusted_market", "Adjusted Market Assessment"),
    ("cost_plus", "Expected Cost plus Margin"),
    ("residual", "Residual (highly variable price)"),
]
PLANS = [("basic", "Basic"), ("standard", "Standard"), ("premium", "Premium")]


class FixSsp(models.Model):
    """The stand-alone selling price of one obligation type (FR-REV-006)."""

    _name = "fix.ssp"
    _description = "Stand-alone Selling Price (IFRS 15)"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "obligation_type, plan, effective_from desc, id desc"

    name = fields.Char(compute="_compute_name", store=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    currency_id = fields.Many2one(related="company_id.currency_id", string="Currency")
    obligation_type = fields.Selection(OBLIGATION_TYPES, required=True, index=True)
    plan = fields.Selection(
        PLANS, string="Plan (empty = every plan)", index=True, help="A plan-specific SSP wins."
    )
    method = fields.Selection(SSP_METHODS, required=True, default="observable")
    value = fields.Monetary(string="Stand-alone Selling Price", currency_field="currency_id")
    tolerance_pct = fields.Float(
        string="Tolerance Band (%)",
        default=10.0,
        help="A contract's typed SSP may differ from this value by at most this percentage.",
    )
    effective_from = fields.Date(required=True, default=fields.Date.context_today)
    effective_to = fields.Date(readonly=True, copy=False)
    basis_ref = fields.Char(
        string="Basis / Evidence",
        required=True,
        help="The price list, sales analysis or cost study the price is taken from.",
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("submitted", "Awaiting Approval"),
            ("active", "Active"),
            ("superseded", "Superseded"),
            ("rejected", "Rejected"),
        ],
        default="draft",
        required=True,
        tracking=True,
        index=True,
    )
    requested_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    requested_at = fields.Datetime(readonly=True, copy=False)
    approved_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    approved_at = fields.Datetime(readonly=True, copy=False)
    reject_reason = fields.Char(readonly=True, copy=False)
    superseded_by_id = fields.Many2one("fix.ssp", readonly=True, copy=False)

    STAMPS = {
        "state",
        "requested_by_id",
        "requested_at",
        "approved_by_id",
        "approved_at",
        "reject_reason",
        "effective_to",
        "superseded_by_id",
    }

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | self.STAMPS

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(s.state != "draft" for s in self):
            locked |= {
                "company_id",
                "obligation_type",
                "plan",
                "method",
                "value",
                "tolerance_pct",
                "effective_from",
                "basis_ref",
            }
        return locked

    @api.depends("obligation_type", "plan", "value", "effective_from")
    def _compute_name(self):
        labels = dict(OBLIGATION_TYPES)
        for s in self:
            s.name = "%s%s from %s" % (
                labels.get(s.obligation_type, "?"),
                " (%s)" % dict(PLANS)[s.plan] if s.plan else "",
                s.effective_from or "?",
            )

    @api.constrains("method", "value", "tolerance_pct", "obligation_type")
    def _check_ssp(self):
        for s in self:
            if s.method != "residual" and s.value <= 0:
                raise ValidationError("A stand-alone selling price is a positive amount.")
            if not 0.0 <= s.tolerance_pct <= 100.0:
                raise ValidationError("The tolerance band is a percentage between 0 and 100.")

    def write(self, vals):
        _locked_write(self, vals, ("draft",), "A submitted stand-alone selling price")
        return super().write(vals)

    def unlink(self):
        if not self.env.su and any(s.state != "draft" for s in self):
            raise UserError("A submitted SSP is kept as history; a new price supersedes it.")
        return super().unlink()

    def action_submit(self):
        require_role(self.env, GROUP_ACCOUNTANT, "Submitting a stand-alone selling price")
        for s in self:
            if s.state != "draft":
                raise UserError("Only a draft SSP is submitted.")
            s._guarded().write(
                {
                    "state": "submitted",
                    "requested_by_id": self.env.uid,
                    "requested_at": fields.Datetime.now(),
                }
            )
        return True

    def action_approve(self):
        """Approved by an Accounting Administrator who did not submit it; it
        supersedes the active SSP of the same type and plan from its date."""
        require_role(self.env, GROUP_ADMINISTRATOR, "Approving a stand-alone selling price")
        now = fields.Datetime.now()
        for s in self:
            if s.state != "submitted":
                raise UserError("Only a submitted SSP is approved.")
            _require_other_person(
                self.env, s.requested_by_id | s.create_uid, "Approving SSP %s" % s.name
            )
            previous = self.sudo().search(
                [
                    ("id", "!=", s.id),
                    ("company_id", "=", s.company_id.id),
                    ("obligation_type", "=", s.obligation_type),
                    ("plan", "=", s.plan or False),
                    ("state", "=", "active"),
                ]
            )
            for old in previous:
                if old.effective_from >= s.effective_from:
                    raise UserError(
                        "%s is already in force from %s: a new price takes effect after it."
                        % (old.name, old.effective_from)
                    )
                old._guarded().write(
                    {
                        "state": "superseded",
                        "effective_to": s.effective_from - timedelta(days=1),
                        "superseded_by_id": s.id,
                    }
                )
            s._guarded().write(
                {"state": "active", "approved_by_id": self.env.uid, "approved_at": now}
            )
        return True

    def action_reject(self, reason=""):
        require_role(self.env, GROUP_ADMINISTRATOR, "Rejecting a stand-alone selling price")
        if not (reason or "").strip():
            raise UserError("State why the SSP is rejected.")
        for s in self:
            if s.state != "submitted":
                raise UserError("Only a submitted SSP is rejected.")
            _require_other_person(self.env, s.requested_by_id, "Rejecting SSP %s" % s.name)
            s._guarded().write({"state": "rejected", "reject_reason": reason.strip()[:250]})
        return True

    @api.model
    def _in_force(self, company, obligation_type, plan, on_date):
        """The approved SSP for the type (a plan-specific one first) on a date."""
        base = [
            ("company_id", "=", company.id),
            ("obligation_type", "=", obligation_type),
            ("state", "in", ("active", "superseded")),
            ("effective_from", "<=", on_date),
            "|",
            ("effective_to", "=", False),
            ("effective_to", ">=", on_date),
        ]
        Ssp = self.sudo()
        if plan:
            found = Ssp.search([*base, ("plan", "=", plan)], order="effective_from desc", limit=1)
            if found:
                return found
        return Ssp.search([*base, ("plan", "=", False)], order="effective_from desc", limit=1)


class FixPerformanceObligationSsp(models.Model):
    _inherit = "fix.performance.obligation"

    ssp_id = fields.Many2one("fix.ssp", string="SSP Used", readonly=True, copy=False, index=True)
    ssp_basis = fields.Selection(
        [("ssp", "Approved SSP (within its band)"), ("contract", "Typed on the contract")],
        string="SSP Basis",
        readonly=True,
        copy=False,
        help="What the allocation's stand-alone price rests on (FR-REV-006).",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"ssp_id", "ssp_basis"}

    def _fix_ssp_check(self):
        """AUT-REV-03: the typed SSP lies within the band of the approved SSP
        in force, else the allocation of THIS contract is refused."""
        Ssp = self.env["fix.ssp"]
        out = {}
        for ob in self:
            sub = ob.subscription_id
            on = ob.start_date or sub.start_date or fields.Date.context_today(ob)
            ssp = Ssp._in_force(sub.company_id, ob.obligation_type, sub.plan, on)
            if ssp and ssp.method != "residual":
                band = ssp.value * ssp.tolerance_pct / 100.0
                if abs(ob.standalone_price - ssp.value) > band + 0.005:
                    raise UserError(
                        "Obligation %s carries a stand-alone price of %.2f; the approved SSP "
                        "%s is %.2f within %.1f%%. Correct the price or approve a new SSP "
                        "before allocating (AUT-REV-03)."
                        % (ob.name, ob.standalone_price, ssp.name, ssp.value, ssp.tolerance_pct)
                    )
            out[ob.id] = ssp
        return out


class FixSubscriptionSsp(models.Model):
    _inherit = "fix.subscription"

    modification_ids = fields.One2many(
        "fix.contract.modification", "subscription_id", string="Contract Modifications"
    )

    def _allocate_price(self, contract_value):
        found = {}
        for sub in self:
            live = sub.obligation_ids.filtered(lambda o: o.state != "cancelled")
            # the SSP decides the split only when there is something to split
            if len(live) > 1:
                found.update(live._fix_ssp_check())
        result = super()._allocate_price(contract_value)
        for sub in self:
            for ob in sub.obligation_ids.filtered(lambda o: o.state == "allocated"):
                ssp = found.get(ob.id)
                ob._guarded().write(
                    {
                        "ssp_id": ssp.id if ssp else False,
                        "ssp_basis": "ssp" if ssp else "contract",
                    }
                )
        return result


# --------------------------------------------------------------------------- modifications
NATURES = [
    ("price", "Price change"),
    ("term", "Term change (new end date and its price)"),
    ("scope", "Added distinct goods or services"),
]
TREATMENTS = [
    ("prospective", "Prospective (remaining consideration over the remaining term)"),
    ("cumulative_catchup", "Cumulative catch-up"),
    ("separate_contract", "Separate contract"),
]


class FixContractModification(models.Model):
    """A change to a scheduled contract and its IFRS 15 treatment."""

    _name = "fix.contract.modification"
    _description = "Contract Modification (IFRS 15)"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "modification_date desc, id desc"

    name = fields.Char(required=True, copy=False, readonly=True, default="New")
    subscription_id = fields.Many2one(
        "fix.subscription", string="Contract", required=True, index=True, ondelete="restrict"
    )
    company_id = fields.Many2one(related="subscription_id.company_id", store=True, index=True)
    operating_unit_id = fields.Many2one(
        related="subscription_id.operating_unit_id", store=True, string="Operating Unit"
    )
    customer_id = fields.Many2one(related="subscription_id.customer_id", store=True)
    currency_id = fields.Many2one(related="subscription_id.currency_id")
    modification_date = fields.Date(
        string="Effective Date", required=True, default=fields.Date.context_today
    )
    nature = fields.Selection(NATURES, required=True, default="price")
    treatment = fields.Selection(TREATMENTS, required=True, default="prospective")
    new_contract_value = fields.Monetary(
        string="New Transaction Price", currency_field="currency_id"
    )
    new_end_date = fields.Date(string="New Contract End")
    separate_subscription_id = fields.Many2one(
        "fix.subscription",
        string="Separate Contract",
        help="The new contract that carries the added goods or services.",
    )
    reason = fields.Text(required=True)
    evidence_ref = fields.Char(string="Evidence (addendum / signed change)", required=True)
    current_price = fields.Monetary(
        string="Current Transaction Price",
        currency_field="currency_id",
        compute="_compute_current",
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("submitted", "Awaiting Approval"),
            ("applied", "Approved and Applied"),
            ("rejected", "Rejected"),
        ],
        default="draft",
        required=True,
        tracking=True,
        index=True,
    )
    requested_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    requested_at = fields.Datetime(readonly=True, copy=False)
    approved_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    approved_at = fields.Datetime(readonly=True, copy=False)
    reject_reason = fields.Char(readonly=True, copy=False)
    line_ids = fields.One2many(
        "fix.contract.modification.line", "modification_id", string="Obligations Re-scheduled"
    )
    catchup_amount = fields.Monetary(
        string="Cumulative Catch-up", currency_field="currency_id", readonly=True, copy=False
    )
    catchup_schedule_id = fields.Many2one(
        "fix.revenue.schedule", string="Catch-up Schedule (CFO)", readonly=True, copy=False
    )

    STAMPS = {
        "name",
        "state",
        "requested_by_id",
        "requested_at",
        "approved_by_id",
        "approved_at",
        "reject_reason",
        "catchup_amount",
        "catchup_schedule_id",
    }

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | self.STAMPS

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(m.state != "draft" for m in self):
            locked |= {
                "subscription_id",
                "modification_date",
                "nature",
                "treatment",
                "new_contract_value",
                "new_end_date",
                "separate_subscription_id",
                "reason",
                "evidence_ref",
            }
        return locked

    @api.depends("subscription_id")
    def _compute_current(self):
        for m in self:
            m.current_price = m.subscription_id._transaction_price() if m.subscription_id else 0.0

    @api.constrains(
        "nature",
        "treatment",
        "new_contract_value",
        "new_end_date",
        "separate_subscription_id",
        "modification_date",
        "subscription_id",
    )
    def _check_modification(self):
        for m in self:
            if (m.nature == "scope") != (m.treatment == "separate_contract"):
                raise ValidationError(
                    "Added distinct goods or services are a separate contract, and only they are."
                )
            if m.nature == "scope":
                other = m.separate_subscription_id
                if not other or other == m.subscription_id:
                    raise ValidationError("Name the separate contract that carries the addition.")
                if other.company_id != m.subscription_id.company_id:
                    raise ValidationError("The separate contract belongs to another company.")
                continue
            if m.new_contract_value <= 0:
                raise ValidationError("Give the new transaction price of the contract.")
            if m.nature == "term" and (not m.new_end_date or m.new_end_date <= m.modification_date):
                raise ValidationError(
                    "A term change gives a new end date after the effective date."
                )

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        Seq = self.env["ir.sequence"].sudo()
        for rec in records.filtered(lambda r: r.name == "New"):
            # the reference is a stamp: written after create, never typed
            rec._guarded().write(
                {"name": Seq.next_by_code("fix.contract.modification") or "CMOD/%s" % rec.id}
            )
        return records

    def write(self, vals):
        _locked_write(self, vals, ("draft",), "A submitted contract modification")
        return super().write(vals)

    def unlink(self):
        if not self.env.su and any(m.state != "draft" for m in self):
            raise UserError("A submitted contract modification is kept as history.")
        return super().unlink()

    # ---- workflow ---------------------------------------------------------------
    def _active_obligations(self):
        self.ensure_one()
        obs = self.subscription_id.obligation_ids.filtered(lambda o: o.state != "cancelled")
        scheduled = obs.filtered(lambda o: o.state == "scheduled")
        return obs, scheduled

    def action_submit(self):
        require_role(self.env, GROUP_ACCOUNTANT, "Requesting a contract modification")
        for m in self:
            if m.state != "draft":
                raise UserError("Only a draft modification is submitted.")
            if m.nature != "scope":
                _obs, scheduled = m._active_obligations()
                if not scheduled:
                    raise UserError(
                        "%s has no scheduled obligation: change its price with Request "
                        "Transaction Price instead." % m.subscription_id.name
                    )
            m._guarded().write(
                {
                    "state": "submitted",
                    "requested_by_id": self.env.uid,
                    "requested_at": fields.Datetime.now(),
                }
            )
        return True

    def action_reject(self, reason=""):
        require_role(self.env, GROUP_ADMINISTRATOR, "Rejecting a contract modification")
        if not (reason or "").strip():
            raise UserError("State why the modification is rejected.")
        for m in self:
            if m.state != "submitted":
                raise UserError("Only a submitted modification is rejected.")
            _require_other_person(self.env, m.requested_by_id, "Rejecting %s" % m.name)
            m._guarded().write({"state": "rejected", "reject_reason": reason.strip()[:250]})
        return True

    def action_approve(self):
        """AUT-REV-06: approved by an Accounting Administrator who did not
        request it, and applied at once."""
        require_role(self.env, GROUP_ADMINISTRATOR, "Approving a contract modification")
        for m in self:
            if m.state != "submitted":
                raise UserError("Only a submitted modification is approved.")
            _require_other_person(
                self.env, m.requested_by_id | m.create_uid, "Approving %s" % m.name
            )
            if m.nature == "scope":
                m._guarded().write(
                    {
                        "state": "applied",
                        "approved_by_id": self.env.uid,
                        "approved_at": fields.Datetime.now(),
                    }
                )
                for sub in m.subscription_id | m.separate_subscription_id:
                    sub.message_post(
                        body="%s: %s accounted for as a separate contract (%s)."
                        % (m.name, m.separate_subscription_id.name, m.evidence_ref)
                    )
                continue
            m._apply_reschedule()
        return True

    def _apply_reschedule(self):
        self.ensure_one()
        today = fields.Date.context_today(self)
        when = self.modification_date
        if when > today:
            raise UserError(
                "%s takes effect on %s: it is approved on or after that date, so no revenue "
                "is recognised ahead of time." % (self.name, when)
            )
        sub = self.subscription_id
        obs, scheduled = self._active_obligations()
        waiting = obs - scheduled - obs.filtered(lambda o: o.state == "satisfied")
        if waiting:
            raise UserError(
                "Obligations %s of %s are not scheduled yet: schedule them (or cancel them) "
                "before the contract is modified." % (", ".join(waiting.mapped("name")), sub.name)
            )
        bad = scheduled.filtered(lambda o: o.schedule_id.state not in ("active", "complete"))
        if bad:
            raise UserError(
                "The schedules of %s are %s: decide them first."
                % (", ".join(bad.mapped("name")), ", ".join(bad.mapped("schedule_id.state")))
            )
        live = scheduled.filtered(lambda o: o.schedule_id.state == "active")
        if not live:
            raise UserError("Every obligation of %s is fully recognised." % sub.name)
        for ob in live:
            if when < ob.schedule_id.start_date:
                raise UserError(
                    "%s takes effect before %s starts recognising (%s)."
                    % (self.name, ob.name, ob.schedule_id.start_date)
                )
            # 1. what the old terms earned up to the modification date
            ob.schedule_id.action_recognize_period(as_of=when)
        live.invalidate_recordset()
        live = live.filtered(lambda o: o.schedule_id.state == "active")
        done = obs - live
        settled = sum(done.mapped(lambda o: o.schedule_id.recognized_amount or 0.0))
        to_allocate = round(self.new_contract_value - settled, 2)
        recognised = {ob.id: ob.schedule_id.recognized_amount for ob in live}
        if to_allocate <= sum(recognised.values()) + 0.005:
            raise UserError(
                "The new price %.2f does not exceed the revenue already recognised on %s "
                "(%.2f): a reduction below recognised revenue is a reversal (credit note), "
                "not a modification."
                % (self.new_contract_value, sub.name, settled + sum(recognised.values()))
            )
        shares = _split(to_allocate, live.mapped("standalone_price"))
        Line = self.env["fix.contract.modification.line"].sudo()
        Schedule = self.env["fix.revenue.schedule"].sudo()
        catchup_total = 0.0
        for ob, share in zip(live, shares, strict=True):
            old = ob.schedule_id
            done_amt = recognised[ob.id]
            end = self.new_end_date or old.end_date
            if end <= when:
                raise UserError("%s would end before the modification takes effect." % ob.name)
            catchup = 0.0
            if self.treatment == "cumulative_catchup":
                term = max((end - old.start_date).days, 1)
                elapsed = (when - old.start_date).days
                catchup = round(share * elapsed / term - done_amt, 2)
                if catchup < 0:
                    raise UserError(
                        "%s would reverse %.2f of recognised revenue on %s: treat it "
                        "prospectively, or as a reversal (credit note)."
                        % (self.name, -catchup, ob.name)
                    )
            remaining = round(share - done_amt - catchup, 2)
            if remaining <= 0:
                raise UserError("Nothing remains to recognise on %s after the change." % ob.name)
            line = Line.create(
                {
                    "modification_id": self.id,
                    "obligation_id": ob.id,
                    "previous_schedule_id": old.id,
                    "previous_allocation": ob.allocated_amount,
                    "recognised_before": done_amt,
                    "new_allocation": share,
                    "catchup_amount": catchup,
                    "remaining_amount": remaining,
                }
            )
            # 2. the old schedule is closed and kept (BRU-REV-04)
            old._guarded().write({"state": "cancelled", "cancelled_date": when})
            old.message_post(body="Closed by %s: a new schedule version continues it." % self.name)
            # 3. the new version recognises the remainder
            new = Schedule._guarded().create(
                {
                    "company_id": old.company_id.id,
                    "operating_unit_id": old.operating_unit_id.id,
                    "source_model": MOD_SOURCE,
                    "source_id": line.id,
                    "subscription_id": sub.id,
                    "description": "%s — %s (v. %s)" % (sub.name, ob.name, self.name),
                    "total_amount": remaining,
                    "start_date": when,
                    "end_date": end,
                }
            )
            line._guarded().write({"new_schedule_id": new.id})
            ob._guarded().write({"schedule_id": new.id, "allocated_amount": share})
            if ob.satisfaction == "over_time" and self.new_end_date:
                ob.write({"end_date": self.new_end_date})
            catchup_total += catchup
        stamp = {
            "state": "applied",
            "approved_by_id": self.env.uid,
            "approved_at": fields.Datetime.now(),
            "catchup_amount": round(catchup_total, 2),
        }
        if catchup_total > 0.005:
            # BRU-REV-01: an immediate release is a manual schedule for the CFO
            stamp["catchup_schedule_id"] = (
                self.env["fix.revenue.schedule"]
                .create(
                    {
                        "company_id": sub.company_id.id,
                        "operating_unit_id": sub.operating_unit_id.id,
                        "subscription_id": sub.id,
                        "description": "%s — cumulative catch-up (%s)" % (sub.name, self.name),
                        "total_amount": round(catchup_total, 2),
                        "start_date": when - timedelta(days=1),
                        "end_date": when,
                        "manual_reason": "Cumulative catch-up of contract modification %s: %s"
                        % (self.name, self.reason),
                        "evidence_ref": self.evidence_ref,
                    }
                )
                .id
            )
        sub_vals = {"contract_value": self.new_contract_value}
        if self.new_end_date:
            sub_vals["contract_end_date"] = self.new_end_date
        sub._guarded().write(sub_vals)
        self._guarded().write(stamp)
        sub.message_post(
            body="%s applied (%s): transaction price %.2f, %d obligation(s) re-scheduled."
            % (self.name, dict(TREATMENTS)[self.treatment], self.new_contract_value, len(live))
        )


class FixContractModificationLine(models.Model):
    """One obligation re-scheduled by a modification (written by the model)."""

    _name = "fix.contract.modification.line"
    _description = "Contract Modification: Obligation Re-scheduled"
    _inherit = ["fix.guarded.mixin"]
    _order = "modification_id, id"

    modification_id = fields.Many2one(
        "fix.contract.modification", required=True, index=True, ondelete="cascade"
    )
    company_id = fields.Many2one(related="modification_id.company_id", store=True, index=True)
    currency_id = fields.Many2one(related="modification_id.currency_id")
    obligation_id = fields.Many2one("fix.performance.obligation", required=True, index=True)
    previous_schedule_id = fields.Many2one("fix.revenue.schedule", string="Previous Version")
    new_schedule_id = fields.Many2one("fix.revenue.schedule", string="New Version")
    previous_allocation = fields.Monetary(currency_field="currency_id")
    recognised_before = fields.Monetary(
        string="Recognised Before the Change", currency_field="currency_id"
    )
    new_allocation = fields.Monetary(currency_field="currency_id")
    catchup_amount = fields.Monetary(string="Catch-up", currency_field="currency_id")
    remaining_amount = fields.Monetary(
        string="Remaining (new version)", currency_field="currency_id"
    )


class FixRevenueScheduleModification(models.Model):
    _inherit = "fix.revenue.schedule"

    def _recognition_refusal(self):
        if self.source_model != MOD_SOURCE:
            return super()._recognition_refusal()
        line = self._source_record()
        if not line:
            return "its contract modification line no longer exists"
        if line.modification_id.state not in ("submitted", "applied"):
            return "its contract modification %s is %s" % (
                line.modification_id.name,
                line.modification_id.state,
            )
        if line.new_schedule_id and line.new_schedule_id != self:
            return "its modification line is scheduled by %s" % line.new_schedule_id.display_name
        if line.new_schedule_id and line.obligation_id.schedule_id != self:
            return "its obligation is scheduled by %s" % line.obligation_id.schedule_id.display_name
        if self.total_amount > line.remaining_amount + 0.005:
            return "total %.2f is above the remaining %.2f of %s" % (
                self.total_amount,
                line.remaining_amount,
                line.modification_id.name,
            )
        return None
