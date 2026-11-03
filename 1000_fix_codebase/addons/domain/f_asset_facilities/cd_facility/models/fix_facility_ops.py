# fix_facility_ops — M47: site leases, statutory licences, utility accounts,
# occupancy/condition inspections, building PM, safety equipment, security
# incidents and site open/close projects. Sites and facility work orders live in
# fix_facility.py.
import re
from datetime import timedelta

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.fields import Domain

from libs.py.fix_events import publish

from .fix_facility import ESTATE_COST_DOFA_THRESHOLDS, _changes, _refuse_if_covered

# AUT-FAC-14: safety equipment alerts the branch 30 days before its inspection
# or refill date; inside that window the item is "due", after it "overdue".
SAFETY_DUE_DAYS = 30

_PERIOD_RE = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")


# The terms a lease modification changes, and the proposal that carries them.
LEASE_TERM_FIELDS = ("start_date", "end_date", "monthly_rent", "escalation_pct")
LEASE_PROPOSAL_FIELDS = (
    "proposed_end_date",
    "proposed_monthly_rent",
    "proposed_escalation_pct",
    "modification_reason",
)


def _lease_commitment(rent, escalation_pct, start, end, today) -> float:
    """The rent still owed from today to `end`: one payment per month, each
    escalated by `escalation_pct` on every anniversary of `start`. The DOFA
    amount of a renewal or modification (an approval measure, not the IFRS 16
    liability, which M47 never computes: BRU-FAC-13)."""
    if not rent or not end or end < today:
        return 0.0
    cursor = max(today, start or today)
    total = 0.0
    while cursor <= end:
        years = relativedelta(cursor, start).years if start and cursor >= start else 0
        total += rent * (1.0 + (escalation_pct or 0.0) / 100.0) ** years
        cursor += relativedelta(months=1)
    return round(total, 2)


class FixSiteLease(models.Model):
    _name = "fix.site.lease"
    _description = "Site Lease"
    _order = "end_date desc, id desc"
    # A07 audit (2026-11-03) M47-8: a plain write extended a lease by five
    # years and cut its rent, and a terminated lease was made active again.
    # The terms (dates, rent, escalation) now change only through a
    # modification: Open Modification copies the terms into a proposal, the
    # proposal is approved under DOFA on the total remaining commitment, and
    # Apply Modification writes it. `state` moves only by its actions.
    _inherit = ["fix.dofa.mixin"]  # brings fix.approvable.mixin and the guard

    _approval_domain = "lease_modification"
    _approval_apply_method = "action_dofa_approve"
    _approval_routed = True

    def _dofa_amount(self) -> float:
        self.ensure_one()
        if not self.modification_open:
            return 0.0
        return _lease_commitment(
            self.proposed_monthly_rent,
            self.proposed_escalation_pct,
            self.start_date,
            self.proposed_end_date,
            fields.Date.context_today(self),
        )

    def _dofa_thresholds(self):
        return ESTATE_COST_DOFA_THRESHOLDS

    def _dofa_amount_label(self) -> str:
        self.ensure_one()
        return "BDT %.2f (remaining lease commitment under the proposed terms)" % (
            self._dofa_amount()
        )

    @api.depends(
        "modification_open",
        "start_date",
        "proposed_end_date",
        "proposed_monthly_rent",
        "proposed_escalation_pct",
    )
    def _compute_dofa_tier_required(self):
        # The live gates read _dofa_current_tier(); this stored column is the
        # tier at the last write (the commitment shrinks as the months pass).
        return super()._compute_dofa_tier_required()

    name = fields.Char(required=True, default="New")
    site_id = fields.Many2one(
        "fix.site", string="Site", required=True, ondelete="cascade", index=True
    )
    lessor_id = fields.Many2one("res.partner", string="Lessor", required=True)
    start_date = fields.Date(required=True, default=fields.Date.context_today)
    end_date = fields.Date(required=True)
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    monthly_rent = fields.Monetary(currency_field="currency_id")
    escalation_pct = fields.Float(string="Escalation %", default=0.0)
    deposit = fields.Monetary(currency_field="currency_id")
    state = fields.Selection(
        [("active", "Active"), ("expired", "Expired"), ("terminated", "Terminated")],
        required=True,
        default="active",
    )
    notes = fields.Char()
    modification_open = fields.Boolean(
        string="Modification Open",
        readonly=True,
        copy=False,
        help="A renewal or modification is being proposed for approval",
    )
    proposed_end_date = fields.Date(string="Proposed End Date", copy=False)
    proposed_monthly_rent = fields.Monetary(
        string="Proposed Monthly Rent", currency_field="currency_id", copy=False
    )
    proposed_escalation_pct = fields.Float(string="Proposed Escalation %", copy=False)
    modification_reason = fields.Char(string="Modification Reason", copy=False)
    terminated_reason = fields.Char(string="Termination Reason", readonly=True, copy=False)

    _dates_ordered = models.Constraint(
        "CHECK (end_date >= start_date)", "Lease end cannot precede its start"
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "modification_open", "terminated_reason"}

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if len(self) == 1:
            # a recorded lease's terms move only through a modification
            locked |= set(LEASE_TERM_FIELDS)
            if not self.modification_open:
                locked |= set(LEASE_PROPOSAL_FIELDS)
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.site.lease") or "LEASE/New"
        return super().create(vals_list)

    def write(self, vals):
        if self and not self._fix_guard_open():
            terms = {k: vals[k] for k in LEASE_TERM_FIELDS if k in vals}
            if terms and _changes(self, terms):
                raise UserError(
                    "A lease's dates, rent and escalation change only through a renewal or "
                    "modification: Open Modification, enter the proposed terms, request "
                    "approval, then Apply Modification (BRU-FAC-05/14)."
                )
            proposal = {k: vals[k] for k in LEASE_PROPOSAL_FIELDS if k in vals}
            if proposal and _changes(self.filtered(lambda r: not r.modification_open), proposal):
                raise UserError("Open a modification before proposing new lease terms.")
        voided = self.browse()
        proposal = {k: vals[k] for k in LEASE_PROPOSAL_FIELDS if k in vals}
        if proposal and not self._fix_guard_has_token():
            # the approval is for the terms as proposed: any change voids it
            voided = self.filtered(
                lambda r: (
                    (r.approval_state in ("pending", "approved") or r.dofa_approved)
                    and _changes(r, proposal)
                )
            )
        result = super().write(vals)
        if voided:
            voided._dofa_void_approval("the proposed lease terms changed after approval")
        return result

    def _lease_require_state(self, allowed, what):
        for rec in self:
            if rec.state not in allowed:
                raise UserError(
                    "Lease %s cannot %s: it is %s."
                    % (rec.name, what, dict(self._fields["state"].selection)[rec.state])
                )

    def action_open_modification(self):
        """Start a renewal or modification: the proposal starts from the
        current terms and is edited before approval is requested."""
        self._lease_require_state(("active", "expired"), "be renewed or modified")
        for rec in self:
            if rec.modification_open:
                raise UserError("Lease %s already has a modification open." % rec.name)
            rec._guarded().write(
                {
                    "modification_open": True,
                    "proposed_end_date": rec.end_date,
                    "proposed_monthly_rent": rec.monthly_rent,
                    "proposed_escalation_pct": rec.escalation_pct,
                    "modification_reason": False,
                }
            )
        return True

    def _lease_clear_proposal(self):
        self._guarded().write(
            {
                "modification_open": False,
                "proposed_end_date": False,
                "proposed_monthly_rent": 0.0,
                "proposed_escalation_pct": 0.0,
                "modification_reason": False,
            }
        )

    def _lease_consume_approval(self):
        self._guarded().write(
            {
                "dofa_approved": False,
                "dofa_approved_by": False,
                "dofa_approved_at": False,
                "dofa_approved_tier": False,
                "dofa_approved_amount": 0.0,
                "approval_state": "none",
            }
        )

    def action_discard_modification(self):
        for rec in self:
            if not rec.modification_open:
                raise UserError("Lease %s has no modification open." % rec.name)
            rec._dofa_void_approval("the lease modification was discarded")
            rec._lease_clear_proposal()
        return True

    def action_request_approval(self, justification=None):
        for rec in self:
            if not rec.modification_open:
                raise UserError(
                    "Open a modification on lease %s and enter the proposed terms first." % rec.name
                )
            _refuse_if_covered(rec)
        return super().action_request_approval(justification=justification)

    def action_apply_modification(self):
        """Write the approved terms. The approval is consumed: the next
        modification needs its own."""
        self._lease_require_state(("active", "expired"), "be renewed or modified")
        today = fields.Date.context_today(self)
        for rec in self:
            if not rec.modification_open or not rec.proposed_end_date:
                raise UserError("Lease %s has no proposed terms to apply." % rec.name)
            if rec.proposed_end_date < rec.start_date:
                raise UserError("The proposed end date cannot precede the lease start.")
            rec._dofa_assert_approved("The modification of lease %s" % rec.name)
            before = {k: rec[k] for k in ("end_date", "monthly_rent", "escalation_pct")}
            new = {
                "end_date": rec.proposed_end_date,
                "monthly_rent": rec.proposed_monthly_rent,
                "escalation_pct": rec.proposed_escalation_pct,
            }
            vals = dict(new)
            if rec.state == "expired" and rec.proposed_end_date >= today:
                vals["state"] = "active"  # a renewal of an expired lease
            reason = rec.modification_reason
            rec._guarded().write(vals)
            rec._lease_clear_proposal()
            rec._lease_consume_approval()
            # BRU-FAC-14: a modification is a remeasurement trigger for M19/M49
            publish(
                self.env,
                "lease.modified",
                "fix.site.lease",
                rec.id,
                {
                    "lease": rec.name,
                    "site": rec.site_id.name,
                    "reason": reason or None,
                    "before": {k: str(v) if k == "end_date" else v for k, v in before.items()},
                    "after": {k: str(v) if k == "end_date" else v for k, v in new.items()},
                },
            )
        return True

    def action_expire(self):
        """An active lease past its end date is recorded as expired."""
        self._lease_require_state(("active",), "expire")
        today = fields.Date.context_today(self)
        for rec in self:
            if rec.end_date >= today:
                raise UserError(
                    "Lease %s runs until %s. Terminate it to end it early."
                    % (rec.name, rec.end_date)
                )
            if rec.modification_open:
                raise UserError("Apply or discard the open modification of %s first." % rec.name)
            rec._guarded().write({"state": "expired"})
        return True

    def action_terminate(self, reason=None):
        reason = (reason or "").strip()
        if not reason:
            raise UserError("State why the lease is terminated.")
        self._lease_require_state(("active", "expired"), "be terminated")
        for rec in self:
            if rec.modification_open:
                rec.action_discard_modification()
            rec._guarded().write({"state": "terminated", "terminated_reason": reason})
        return True


class FixSiteLicence(models.Model):
    _name = "fix.site.licence"
    _description = "Site Statutory Licence"
    _inherit = ["fix.guarded.mixin"]
    _order = "valid_to desc, id desc"

    name = fields.Char(required=True, default="New")
    site_id = fields.Many2one(
        "fix.site", string="Site", required=True, ondelete="cascade", index=True
    )
    licence_type = fields.Selection(
        [
            ("trade", "Trade Licence"),
            ("fire", "Fire Safety"),
            ("health", "Health / Sanitation"),
            ("environment", "Environment"),
            ("other", "Other"),
        ],
        required=True,
        default="trade",
    )
    number = fields.Char(string="Licence Number")
    issued_on = fields.Date()
    valid_to = fields.Date()
    state = fields.Selection(
        [("valid", "Valid"), ("expired", "Expired"), ("suspended", "Suspended")],
        required=True,
        default="valid",
    )
    # A07 audit (2026-11-03, M47-3/M47-4): `is_valid` was a STORED compute on
    # today's date with no cron, so a licence that lapsed yesterday still read
    # "Valid Today" and the Licence Gaps KPI under-counted. It is now computed
    # on every read and searchable. A licence with no `valid_to` is NOT valid:
    # open-ended validity is unevidenced (AC-21: loaded without evidence ->
    # expired), so it counts as a gap until an expiry date is recorded.
    is_valid = fields.Boolean(
        string="Valid Today", compute="_compute_is_valid", search="_search_is_valid"
    )

    @api.depends("state", "valid_to")
    def _compute_is_valid(self):
        today = fields.Date.context_today(self)
        for rec in self:
            rec.is_valid = bool(rec.state == "valid" and rec.valid_to and rec.valid_to >= today)

    def _search_is_valid(self, operator, value):
        if operator not in ("in", "not in"):
            return NotImplemented
        today = fields.Date.context_today(self)
        valid = Domain(
            [("state", "=", "valid"), ("valid_to", "!=", False), ("valid_to", ">=", today)]
        )
        domain = Domain.OR([valid if flag else ~valid for flag in {bool(v) for v in value}])
        return ~domain if operator == "not in" else domain

    def _is_lapsed(self, today) -> bool:
        return self.state == "expired" or bool(self.valid_to and self.valid_to < today)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.site.licence") or "SLIC/New"
                )
        return super().create(vals_list)

    def write(self, vals):
        # A07 audit (2026-11-03, M47-2/M47-3): an expired licence was revived
        # to `valid` by a plain write (or the P03 form) with no renewal and no
        # new evidence. A lapsed licence (state expired, or its end date has
        # passed) cannot be made valid again by a plain user: a renewal is a
        # NEW licence row with its own number and dates, so the lapse stays on
        # record. Marking it expired or suspended stays open. Superuser code
        # (seeds, data loading, sudo services) is trusted.
        if self and not self._fix_guard_open() and ("state" in vals or "valid_to" in vals):
            today = fields.Date.context_today(self)
            new_to = (
                (fields.Date.to_date(vals["valid_to"]) or False) if "valid_to" in vals else None
            )
            for rec in self:
                state = vals.get("state", rec.state)
                valid_to = new_to if "valid_to" in vals else rec.valid_to
                changed = state != rec.state or valid_to != (rec.valid_to or False)
                if state == "valid" and changed and rec._is_lapsed(today):
                    raise UserError(
                        "Licence %s has lapsed (valid to %s, state %s) and cannot be made "
                        "valid again. Record the renewal as a new licence with its own "
                        "number and validity dates." % (rec.name, rec.valid_to or "-", rec.state)
                    )
        return super().write(vals)


class FixSiteUtility(models.Model):
    _name = "fix.site.utility"
    _description = "Site Utility Account"
    _order = "period desc, id desc"

    name = fields.Char(required=True, default="New")
    site_id = fields.Many2one(
        "fix.site", string="Site", required=True, ondelete="cascade", index=True
    )
    period = fields.Char(required=True, help="YYYY-MM")
    utility_type = fields.Selection(
        [("power", "Electricity"), ("water", "Water"), ("gas", "Gas"), ("internet", "Internet")],
        required=True,
        default="power",
    )
    amount = fields.Monetary(currency_field="currency_id", required=True)
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    usage = fields.Float(string="Usage")
    unit = fields.Char(string="Unit", default="kWh")
    flagged = fields.Boolean(string="Anomaly Flagged", default=False)
    notes = fields.Char()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.site.utility") or "SUTL/New"
                )
        return super().create(vals_list)

    # A07 audit (2026-11-03, M47-13): the same site / utility / period was
    # accepted twice and a free-text period ("last month") once, and both were
    # double-counted in Cost per Site and the per-sqft KPI. One bill per site,
    # utility type and calendar month, and the period is a real YYYY-MM.
    # A Python constraint, not SQL UNIQUE, so the upgrade does not fail on a
    # database that already holds duplicates; new or edited rows are checked.
    @api.constrains("site_id", "utility_type", "period")
    def _check_one_bill_per_period(self):
        for rec in self:
            if not _PERIOD_RE.match(rec.period or ""):
                raise ValidationError(
                    "Utility period %r must be a calendar month written YYYY-MM." % rec.period
                )
            twin = self.sudo().search_count(
                [
                    ("id", "!=", rec.id),
                    ("site_id", "=", rec.site_id.id),
                    ("utility_type", "=", rec.utility_type),
                    ("period", "=", rec.period),
                ]
            )
            if twin:
                raise ValidationError(
                    "%s already has a %s bill for %s. Correct that bill instead of "
                    "recording a second one."
                    % (
                        rec.site_id.name,
                        dict(rec._fields["utility_type"].selection).get(rec.utility_type),
                        rec.period,
                    )
                )

    def action_flag(self):
        for rec in self:
            rec.flagged = True


class FixSiteCondition(models.Model):
    _name = "fix.site.condition"
    _description = "Site Occupancy & Condition"
    _order = "inspected_on desc, id desc"

    name = fields.Char(required=True, default="New")
    site_id = fields.Many2one(
        "fix.site", string="Site", required=True, ondelete="cascade", index=True
    )
    inspected_on = fields.Date(required=True, default=fields.Date.context_today)
    occupancy_pct = fields.Float(string="Occupancy %", default=100.0)
    condition_grade = fields.Selection(
        [("a", "A — Excellent"), ("b", "B — Good"), ("c", "C — Fair"), ("d", "D — Poor")],
        required=True,
        default="b",
    )
    inspector_id = fields.Many2one("hr.employee", string="Inspector")
    notes = fields.Text()

    _occupancy_range = models.Constraint(
        "CHECK (occupancy_pct >= 0 AND occupancy_pct <= 100)",
        "Occupancy is a 0–100 percentage",
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.site.condition") or "SCND/New"
                )
        return super().create(vals_list)


class FixSitePm(models.Model):
    _name = "fix.site.pm"
    _description = "Building Services PM"
    # A07 audit (2026-11-03) M47-16: a fire-system PM was written to `done`
    # with no done date. `state` and `done_on` are set only by Mark Done.
    _inherit = ["fix.guarded.mixin"]
    _order = "scheduled_on desc, id desc"

    name = fields.Char(required=True, default="New")
    site_id = fields.Many2one(
        "fix.site", string="Site", required=True, ondelete="cascade", index=True
    )
    service_type = fields.Selection(
        [
            ("hvac", "HVAC"),
            ("lift", "Lift / Elevator"),
            ("fire", "Fire Systems"),
            ("generator", "Generator"),
            ("pest", "Pest Control"),
            ("cleaning", "Deep Cleaning"),
        ],
        required=True,
        default="hvac",
    )
    provider_id = fields.Many2one("res.partner", string="Service Provider")
    scheduled_on = fields.Date(required=True, default=fields.Date.context_today)
    done_on = fields.Date()
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    cost = fields.Monetary(currency_field="currency_id")
    state = fields.Selection([("open", "Open"), ("done", "Done")], required=True, default="open")
    notes = fields.Char()

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "done_on"}

    @api.constrains("state", "done_on")
    def _check_done_has_date(self):
        for rec in self:
            if rec.state == "done" and not rec.done_on:
                raise ValidationError("A completed PM job records the date it was done.")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.site.pm") or "SPM/New"
        return super().create(vals_list)

    def action_done(self, done_on=None):
        """Mark an open PM job done on `done_on` (default today), never later."""
        today = fields.Date.context_today(self)
        try:
            done = fields.Date.to_date(done_on) if done_on else today
        except ValueError as exc:
            raise UserError("Done date %r is not a date (YYYY-MM-DD)." % done_on) from exc
        if done > today:
            raise UserError("A PM job cannot be recorded as done in the future (%s)." % done)
        for rec in self:
            if rec.state != "open":
                raise UserError("Complete an open PM job")
            rec._guarded().write({"state": "done", "done_on": done})
        return True


class FixSiteSafety(models.Model):
    _name = "fix.site.safety"
    _description = "Site Safety Equipment"
    _inherit = ["fix.guarded.mixin"]
    _order = "next_check"

    name = fields.Char(required=True, default="New")
    site_id = fields.Many2one(
        "fix.site", string="Site", required=True, ondelete="cascade", index=True
    )
    equipment_type = fields.Selection(
        [
            ("extinguisher", "Fire Extinguisher"),
            ("alarm", "Fire Alarm"),
            ("cctv", "CCTV"),
            ("first_aid", "First Aid Kit"),
            ("other", "Other"),
        ],
        required=True,
        default="extinguisher",
    )
    ref = fields.Char(string="Tag / Reference")
    last_check = fields.Date()
    next_check = fields.Date(required=True)
    # A07 audit (2026-11-03, M47-9): `state` was typed and defaulted to `ok`,
    # so an extinguisher 45 days past its check was born `ok` and the overdue
    # KPI read 0; a plain write or the P03 form cleared an overdue item. The
    # status is now derived from `next_check` against today on every read
    # (BRU-FAC-09): overdue once the date has passed, due inside the
    # AUT-FAC-14 30-day alert window, ok otherwise. It is searchable, so the
    # grid's state filter keeps working.
    state = fields.Selection(
        [("ok", "OK"), ("due", "Due"), ("overdue", "Overdue")],
        compute="_compute_state",
        search="_search_state",
    )
    notes = fields.Char()

    @api.depends("next_check")
    def _compute_state(self):
        today = fields.Date.context_today(self)
        due_by = today + timedelta(days=SAFETY_DUE_DAYS)
        for rec in self:
            if not rec.next_check or rec.next_check < today:
                rec.state = "overdue"
            elif rec.next_check <= due_by:
                rec.state = "due"
            else:
                rec.state = "ok"

    def _search_state(self, operator, value):
        if operator not in ("in", "not in"):
            return NotImplemented
        today = fields.Date.context_today(self)
        due_by = today + timedelta(days=SAFETY_DUE_DAYS)
        by_state = {
            "overdue": Domain("next_check", "<", today),
            "due": Domain("next_check", ">=", today) & Domain("next_check", "<=", due_by),
            "ok": Domain("next_check", ">", due_by),
        }
        domain = Domain.OR([by_state[v] for v in value if v in by_state])
        return ~domain if operator == "not in" else domain

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            # the status is derived; a typed value would be discarded anyway
            vals.pop("state", None)
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.site.safety") or "SSAF/New"
        return super().create(vals_list)

    def write(self, vals):
        # A07 audit (2026-11-03, M47-9): with the status derived from the
        # dates, forging moved to the dates themselves. Outside Record Check a
        # plain user may not change `last_check` (that is the inspection
        # record) or move `next_check` LATER (that clears overdue with no
        # inspection); bringing a check forward stays open. Writing the status
        # it already has (the P03 form posts every field) is accepted.
        vals = dict(vals)
        typed_state = vals.pop("state", None)
        if self and not self._fix_guard_open():
            new_next = fields.Date.to_date(vals["next_check"]) if vals.get("next_check") else None
            for rec in self:
                if typed_state is not None and typed_state != rec.state:
                    raise UserError(
                        "The status of %s is derived from its next check date (%s) and "
                        "cannot be set by hand. Use Record Check after an inspection."
                        % (rec.name, rec.next_check)
                    )
                if "last_check" in vals and (fields.Date.to_date(vals["last_check"]) or False) != (
                    rec.last_check or False
                ):
                    raise UserError(
                        "The last check of %s is recorded by Record Check, not by editing."
                        % rec.name
                    )
                if new_next and rec.next_check and new_next > rec.next_check:
                    raise UserError(
                        "The next check of %s cannot be pushed later than %s by editing. "
                        "Use Record Check after an inspection." % (rec.name, rec.next_check)
                    )
        if not vals:
            return True
        return super().write(vals)

    def action_check(self, next_check=None):
        """Record an inspection today and set the next one.

        A07 audit (2026-11-03, M47-9): the check stamped `ok` and left
        `next_check` in the past. The module holds no inspection interval and
        the spec gives none per equipment type, so none is invented: the
        inspector states the next check date, which must be after today.
        """
        today = fields.Date.context_today(self)
        try:
            next_date = fields.Date.to_date(next_check) if next_check else None
        except ValueError as exc:
            raise UserError("Next check date %r is not a date (YYYY-MM-DD)." % next_check) from exc
        if not next_date:
            raise UserError(
                "Enter the next check date when recording a check: no inspection "
                "interval is configured for safety equipment."
            )
        if next_date <= today:
            raise UserError("The next check date must be after today (%s)." % today)
        for rec in self:
            rec._guarded().write({"last_check": today, "next_check": next_date})


class FixSiteIncident(models.Model):
    _name = "fix.site.incident"
    _description = "Site Security Incident"
    # A07 audit (2026-11-03) M47-10: the reporter closed their own HIGH injury
    # incident with no resolution, and `state` was writable directly and via
    # the P03 form. Close now needs a resolution and a closer other than the
    # reporter; `state` and the closing record are set only by Close. The
    # M59 HSE hand-off is P1 and not built here.
    _inherit = ["fix.guarded.mixin"]
    _order = "occurred_on desc, id desc"

    name = fields.Char(required=True, default="New")
    site_id = fields.Many2one(
        "fix.site", string="Site", required=True, ondelete="cascade", index=True
    )
    incident_type = fields.Selection(
        [
            ("theft", "Theft / Burglary"),
            ("trespass", "Trespass"),
            ("injury", "Injury"),
            ("fire", "Fire"),
            ("other", "Other"),
        ],
        required=True,
        default="theft",
    )
    occurred_on = fields.Date(required=True, default=fields.Date.context_today)
    description = fields.Text(required=True)
    severity = fields.Selection(
        [("low", "Low"), ("medium", "Medium"), ("high", "High")],
        required=True,
        default="medium",
    )
    state = fields.Selection(
        [("open", "Open"), ("closed", "Closed")], required=True, default="open"
    )
    resolution = fields.Text(
        copy=False, help="Root cause and action taken. Required to close; frozen once closed."
    )
    closed_by_id = fields.Many2one("res.users", string="Closed By", readonly=True, copy=False)
    closed_at = fields.Datetime(string="Closed At", readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "closed_by_id", "closed_at"}

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if len(self) == 1 and self.state == "closed":
            locked.add("resolution")
        return locked

    def write(self, vals):
        if (
            self
            and not self._fix_guard_open()
            and "resolution" in vals
            and _changes(
                self.filtered(lambda r: r.state == "closed"), {"resolution": vals["resolution"]}
            )
        ):
            raise UserError("A closed incident's resolution is the record it was closed on.")
        return super().write(vals)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.site.incident") or "SINC/New"
                )
        return super().create(vals_list)

    def action_close(self, resolution=None):
        for rec in self:
            if rec.state != "open":
                raise UserError("Close an open incident")
            text = (resolution or rec.resolution or "").strip()
            if not text:
                raise UserError(
                    "Record the resolution of %s (root cause and action taken) to close it."
                    % rec.name
                )
            # the reporter does not close their own incident (§13 SoD);
            # superuser code (data fixes, service calls) stays trusted
            if not self.env.su and rec.create_uid == self.env.user:
                raise UserError(
                    "Segregation of duties: you reported %s; another person closes it." % rec.name
                )
            rec._guarded().write(
                {
                    "state": "closed",
                    "resolution": text,
                    "closed_by_id": self.env.uid,
                    "closed_at": fields.Datetime.now(),
                }
            )
        return True


class FixSiteProject(models.Model):
    _name = "fix.site.project"
    _description = "Site Open / Close Project"
    # A07 audit (2026-11-03) M47-12: the creator started a 50M project alone,
    # another user raised the budget 1M -> 9M mid-project and `state` was
    # written straight to `done`. Start (and completion) now need a DOFA
    # approval of the budget; raising the budget after approval voids it, so
    # the project cannot complete until it is approved again.
    _inherit = ["fix.dofa.mixin"]  # brings fix.approvable.mixin and the guard
    _order = "planned_on desc, id desc"

    _approval_domain = "site_capex"
    _approval_apply_method = "action_dofa_approve"
    _approval_routed = True

    def _dofa_amount(self) -> float:
        self.ensure_one()
        return self.budget or 0.0

    def _dofa_thresholds(self):
        return ESTATE_COST_DOFA_THRESHOLDS

    def _dofa_amount_label(self) -> str:
        self.ensure_one()
        return "BDT %.2f (capex project budget)" % self._dofa_amount()

    @api.depends("budget")
    def _compute_dofa_tier_required(self):
        return super()._compute_dofa_tier_required()

    name = fields.Char(required=True, default="New")
    site_id = fields.Many2one(
        "fix.site", string="Site", required=True, ondelete="cascade", index=True
    )
    project_type = fields.Selection(
        [("open", "Site Opening"), ("close", "Site Closure"), ("relocate", "Relocation")],
        required=True,
        default="open",
    )
    planned_on = fields.Date(required=True, default=fields.Date.context_today)
    done_on = fields.Date()
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    budget = fields.Monetary(currency_field="currency_id")
    state = fields.Selection(
        [("planned", "Planned"), ("in_progress", "In Progress"), ("done", "Done")],
        required=True,
        default="planned",
    )
    notes = fields.Char()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.site.project") or "SPRJ/New"
                )
        return super().create(vals_list)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "done_on"}

    def action_request_approval(self, justification=None):
        for rec in self:
            if rec.state not in ("planned", "in_progress"):
                raise UserError("A completed project's budget is not approved again.")
            _refuse_if_covered(rec)
        return super().action_request_approval(justification=justification)

    def action_start(self):
        for rec in self:
            if rec.state != "planned":
                raise UserError("Start a planned project")
            rec._dofa_assert_approved("Starting capex project %s" % rec.name)
            rec._guarded().write({"state": "in_progress"})
        return True

    def action_done(self):
        for rec in self:
            if rec.state != "in_progress":
                raise UserError("Complete an in-progress project")
            # a budget raised after start voided the approval: re-approve first
            rec._dofa_assert_approved("Completing capex project %s" % rec.name)
            rec._guarded().write({"state": "done", "done_on": fields.Date.context_today(self)})
        return True


class FixSiteAsset(models.Model):
    """Building plant at a site: the register behind M47 Branch Asset Register."""

    _name = "fix.site.asset"
    _description = "Site Infrastructure Asset"
    # A07 audit (2026-11-03) M47-11: a plain user retired a 4M generator with
    # no approval, and a retired asset was restored by writing `state`.
    # Retirement is now a DOFA decision on the asset's value; `state` moves
    # only by its actions and retirement is final.
    _inherit = ["fix.dofa.mixin"]  # brings fix.approvable.mixin and the guard
    _order = "site_id, asset_type, name"

    _approval_domain = "site_asset_retirement"
    _approval_apply_method = "action_dofa_approve"
    _approval_routed = True

    def _dofa_amount(self) -> float:
        self.ensure_one()
        return self.value or 0.0

    def _dofa_thresholds(self):
        return ESTATE_COST_DOFA_THRESHOLDS

    def _dofa_amount_label(self) -> str:
        self.ensure_one()
        return "BDT %.2f (site asset value retired)" % self._dofa_amount()

    @api.depends("value")
    def _compute_dofa_tier_required(self):
        return super()._compute_dofa_tier_required()

    name = fields.Char(required=True, default="New")
    site_id = fields.Many2one(
        "fix.site", string="Site", required=True, ondelete="cascade", index=True
    )
    asset_type = fields.Selection(
        [
            ("hvac", "HVAC Plant"),
            ("lift", "Lift / Elevator"),
            ("generator", "Generator"),
            ("fire_pump", "Fire Pump"),
            ("ups", "UPS"),
            ("cctv", "CCTV System"),
            ("electrical", "Electrical Distribution"),
            ("other", "Other"),
        ],
        required=True,
        default="hvac",
    )
    tag = fields.Char(string="Asset Tag")
    serial_no = fields.Char(string="Serial No")
    installed_on = fields.Date()
    warranty_end = fields.Date()
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    value = fields.Monetary(currency_field="currency_id")
    state = fields.Selection(
        [
            ("operational", "Operational"),
            ("maintenance", "Under Maintenance"),
            ("retired", "Retired"),
        ],
        required=True,
        default="operational",
    )
    notes = fields.Char()
    retired_on = fields.Date(readonly=True, copy=False)
    retire_reason = fields.Char(string="Retirement Reason", readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "retired_on", "retire_reason"}

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if len(self) == 1 and self.state == "retired":
            locked.add("value")
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.site.asset") or "SASET/New"
        return super().create(vals_list)

    def write(self, vals):
        if (
            self
            and not self._fix_guard_open()
            and "value" in vals
            and _changes(self.filtered(lambda r: r.state == "retired"), {"value": vals["value"]})
        ):
            raise UserError("A retired asset's value is the value that was written off.")
        return super().write(vals)

    def action_request_approval(self, justification=None):
        for rec in self:
            if rec.state == "retired":
                raise UserError("%s is already retired." % rec.name)
            _refuse_if_covered(rec)
        return super().action_request_approval(justification=justification)

    def action_maintenance(self):
        for rec in self:
            if rec.state != "operational":
                raise UserError("Take an operational asset into maintenance")
            rec._guarded().write({"state": "maintenance"})
        return True

    def action_restore(self):
        for rec in self:
            if rec.state != "maintenance":
                raise UserError("Restore an asset that is under maintenance")
            rec._guarded().write({"state": "operational"})
        return True

    def action_retire(self, reason=None):
        """Retire (final). Above Tier 0 the asset's value needs DOFA approval."""
        for rec in self:
            if rec.state not in ("operational", "maintenance"):
                raise UserError("Retire an operational asset or one under maintenance")
            rec._dofa_assert_approved("Retiring site asset %s" % rec.name)
            rec._guarded().write(
                {
                    "state": "retired",
                    "retired_on": fields.Date.context_today(self),
                    "retire_reason": (reason or "").strip() or False,
                }
            )
        return True
