# cd_fpa: M54 sub-module capture audit (2026-11-17).
#
# Four spec records the M54 workspace had no way to capture:
#
#   * fix.cost.centre (FR-FPA-001 P0): the management cost centre, with a
#     named owner, its parent, its branch and whether it absorbs or
#     allocates cost. The estate carried the cost centre only as free text
#     on budget lines and journal dimensions, so no variance could be put to
#     an accountable owner (BRU-FPA-12).
#   * fix.activity.rate (FR-FPA-012/013 P0, BRU-FPA-16 H): the planned, fully
#     loaded rate for a technician hour (or workshop hour, delivery,
#     contact), approved by an Accounting Administrator who did not prepare
#     or submit it and applied consistently. Job costing applied whatever
#     each technician's actual rate came to over the report window, so the
#     same hour cost differently depending on the window asked for. An
#     approved rate is frozen; a change is a new rate that, once approved,
#     closes the old one the day before it takes effect, so the history
#     stays and past job costs are explained by the rate then in force.
#   * fix.budget.target (FR-FPA-029 P0, spec 8.2 "Target set"): the top-down
#     revenue, cost or margin target the CFO issues for a budget version,
#     company-wide or by branch, business line or cost centre. The plan is
#     read against it live, and submitting a version posts the departures.
#   * fix.variance.explanation (FR-FPA-037 P0, BRU-FPA-12 H, AUT-FPA-08): the
#     accountable owner's explanation of a budget variance on a line, a
#     branch or a business line, for a period. The figures are measured
#     from the approved budget and the posted GL when it is raised, never
#     typed. The owner submits; an Accounting Administrator who is neither
#     the owner nor the submitter accepts or returns it. A monthly job raises
#     one for every approved line whose variance last month passed the
#     threshold, and a daily job gives overdue ones a to-do for their owner.
from __future__ import annotations

import logging
from datetime import timedelta

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

ACCOUNT_USER = "account.group_account_user"
ACCOUNT_MANAGER = "account.group_account_manager"
# Bangladesh weekend (Friday, Saturday): a "working day" deadline skips them.
WEEKEND = (4, 5)
PARAM_THRESHOLD_AMOUNT = "cd_fpa.variance_threshold_amount"
PARAM_THRESHOLD_PCT = "cd_fpa.variance_threshold_pct"
# Spec Q-05 leaves the threshold to the CFO; until set, a variance of at least
# BDT 50,000 AND at least 10% of plan needs an explanation.
DEFAULT_THRESHOLD_AMOUNT = 50000.0
DEFAULT_THRESHOLD_PCT = 10.0
EXPLAIN_WORKING_DAYS = 3
LOCK_EXEMPT = {"message_main_attachment_id", "activity_ids", "message_follower_ids"}

ACTIVITY_TYPES = [
    ("technician_hour", "Technician Hour"),
    ("workshop_hour", "Workshop Hour"),
    ("delivery", "Delivery"),
    ("contact", "Customer Contact"),
]
RATE_STATES = [
    ("draft", "Draft"),
    ("submitted", "Submitted"),
    ("approved", "Approved"),
    ("rejected", "Rejected"),
    ("superseded", "Superseded"),
]
ROOT_CAUSES = [
    ("timing", "Timing (posted in another period)"),
    ("volume", "Volume (more or fewer jobs)"),
    ("price", "Price or rate"),
    ("mix", "Mix (service, branch or channel mix)"),
    ("one_off", "One-off event"),
    ("coding", "Wrong ledger coding"),
    ("budget_error", "Budget set wrongly"),
    ("other", "Other (explained below)"),
]


def _require_group(env, xmlid, what):
    if env.su or env.user.has_group(xmlid):
        return
    raise UserError(
        "%s needs the %s role."
        % (what, "Accounting Administrator" if xmlid == ACCOUNT_MANAGER else "Accountant")
    )


def _require_finance(env, what):
    if env.su or env.user.has_group(ACCOUNT_USER) or env.user.has_group(ACCOUNT_MANAGER):
        return
    raise UserError("%s needs the Accountant or Accounting Administrator role." % what)


def _require_other_person(env, users, what):
    """Maker-checker: the acting user is none of `users`."""
    if env.su:
        return
    users = users.filtered(lambda u: u)
    if env.user in users:
        raise UserError(
            "Segregation of duties: %s must be done by someone other than %s."
            % (what, ", ".join(users.mapped("name")))
        )


def _float_param(env, key, default):
    raw = env["ir.config_parameter"].sudo().get_param(key)
    try:
        return float(raw) if raw not in (None, False, "") else float(default)
    except (TypeError, ValueError):
        return float(default)


def add_working_days(start, days):
    """`start` plus `days` Bangladesh working days (Friday and Saturday off)."""
    day = start
    left = days
    while left > 0:
        day += timedelta(days=1)
        if day.weekday() not in WEEKEND:
            left -= 1
    return day


def _changes(records, vals):
    """True when `vals` would change a stored value (the P03 form posts back
    every field it shows, unchanged ones included)."""
    names = [n for n in vals if n in records._fields and n not in LOCK_EXEMPT]
    return any(rec._fix_guard_differs(n, vals[n], rec[n]) for rec in records for n in names)


def _changed_names(records, vals):
    return {
        n
        for n in vals
        if n in records._fields and n not in LOCK_EXEMPT
        for rec in records
        if rec._fix_guard_differs(n, vals[n], rec[n])
    }


class FixCostCentre(models.Model):
    """A management cost centre (FR-FPA-001): code, owner, parent, branch and
    how it behaves in allocation. The code is the one written on budget lines
    and journal dimensions; the owner is who explains its variances."""

    _name = "fix.cost.centre"
    _description = "Cost Centre"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "code"
    _code_company_unique = models.Constraint(
        "UNIQUE (company_id, code)", "A cost-centre code is used once per company"
    )

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    code = fields.Char(required=True, tracking=True)
    name = fields.Char(required=True, tracking=True)
    name_bn = fields.Char(string="Name (Bengali)")
    parent_id = fields.Many2one(
        "fix.cost.centre", string="Parent Cost Centre", index=True, ondelete="restrict"
    )
    child_ids = fields.One2many("fix.cost.centre", "parent_id", string="Child Cost Centres")
    branch_id = fields.Many2one("fix.branch", string="Branch", tracking=True)
    owner_id = fields.Many2one(
        "res.users",
        string="Owner",
        required=True,
        tracking=True,
        help="Accountable for the centre's budget and for explaining its variances.",
    )
    centre_type = fields.Selection(
        [
            ("absorbing", "Absorbing (receives allocated cost)"),
            ("allocating", "Allocating (spreads its cost)"),
            ("both", "Both"),
        ],
        string="Allocation Behaviour",
        required=True,
        default="absorbing",
        tracking=True,
    )
    date_from = fields.Date(string="Active From")
    date_to = fields.Date(string="Active To")
    note = fields.Text(string="What It Covers")
    active = fields.Boolean(default=True, tracking=True)

    @api.depends("code", "name")
    def _compute_display_name(self) -> None:
        for centre in self:
            centre.display_name = (
                "%s %s" % (centre.code, centre.name) if centre.code else centre.name
            )

    @api.constrains("parent_id", "code")
    def _check_parent(self) -> None:
        if self._has_cycle():
            raise ValidationError("A cost centre cannot be its own parent, directly or not.")
        for centre in self:
            if centre.parent_id and centre.parent_id.company_id != centre.company_id:
                raise ValidationError("A cost centre's parent belongs to the same company.")

    @api.constrains("date_from", "date_to", "code")
    def _check_dates(self) -> None:
        for centre in self:
            if centre.date_from and centre.date_to and centre.date_from > centre.date_to:
                raise ValidationError("Cost centre %s ends before it starts." % centre.code)

    @api.model
    def owner_for_code(self, code, company):
        """The owner of the active cost centre with this code, or nobody."""
        if not code:
            return self.env["res.users"]
        centre = self.sudo().search(
            [("code", "=", code.strip()), ("company_id", "=", company.id)], limit=1
        )
        return centre.owner_id


class FixActivityRate(models.Model):
    """A planned, fully loaded activity rate (FR-FPA-012/013, BRU-FPA-16)."""

    _name = "fix.activity.rate"
    _description = "Planned Activity Rate"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "effective_from desc, id desc"

    name = fields.Char(string="Reference", readonly=True, copy=False, default="/")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    activity_type = fields.Selection(
        ACTIVITY_TYPES, string="Activity", required=True, default="technician_hour", tracking=True
    )
    branch_id = fields.Many2one(
        "fix.branch",
        string="Branch",
        tracking=True,
        help="Leave empty for the rate every branch uses unless it has its own.",
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    planned_rate = fields.Monetary(
        string="Planned Rate per Unit", currency_field="currency_id", tracking=True
    )
    basis = fields.Text(
        string="Composition",
        help="What the rate loads: salary, benefits, tools, vehicle, training and "
        "non-productive time, with the figures used.",
    )
    measure_from = fields.Date(string="Compare With Actuals From")
    measure_to = fields.Date(string="Compare With Actuals To")
    measured_rate = fields.Monetary(
        string="Actual Loaded Rate (measured)", currency_field="currency_id", readonly=True
    )
    measured_hours = fields.Float(string="Productive Hours Measured", readonly=True)
    measured_at = fields.Datetime(readonly=True)
    effective_from = fields.Date(string="Effective From", tracking=True)
    effective_to = fields.Date(string="Effective To", tracking=True)
    state = fields.Selection(RATE_STATES, default="draft", required=True, tracking=True, copy=False)
    submitted_by = fields.Many2one("res.users", readonly=True, copy=False)
    submitted_at = fields.Datetime(readonly=True, copy=False)
    approved_by = fields.Many2one("res.users", readonly=True, copy=False, tracking=True)
    approved_at = fields.Datetime(readonly=True, copy=False)
    rejection_reason = fields.Text(readonly=True, copy=False)
    superseded_by_id = fields.Many2one(
        "fix.activity.rate", string="Replaced By", readonly=True, copy=False
    )

    _GUARDED = {
        "name",
        "state",
        "measured_rate",
        "measured_hours",
        "measured_at",
        "submitted_by",
        "submitted_at",
        "approved_by",
        "approved_at",
        "rejection_reason",
        "superseded_by_id",
    }
    # once approved, only the system closes the window (supersession)
    _OPEN_STATES = ("draft", "rejected")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | self._GUARDED

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(r.state not in self._OPEN_STATES for r in self):
            locked |= {n for n in self._fields if n not in LOCK_EXEMPT}
        return locked

    @api.depends("name", "activity_type", "branch_id", "planned_rate")
    def _compute_display_name(self) -> None:
        labels = dict(ACTIVITY_TYPES)
        for rate in self:
            rate.display_name = "%s %s %s %.2f" % (
                rate.name if rate.name and rate.name != "/" else "",
                labels.get(rate.activity_type, ""),
                rate.branch_id.display_name or "(all branches)",
                rate.planned_rate or 0.0,
            )

    @api.constrains("planned_rate", "effective_from", "effective_to", "basis", "activity_type")
    def _check_rate(self) -> None:
        for rate in self:
            if (rate.planned_rate or 0.0) <= 0:
                raise ValidationError("A planned rate must be more than zero.")
            if not rate.effective_from:
                raise ValidationError("A planned rate needs the date it takes effect.")
            if rate.effective_to and rate.effective_to < rate.effective_from:
                raise ValidationError("A planned rate cannot end before it takes effect.")
            if not (rate.basis or "").strip():
                raise ValidationError(
                    "Say what the rate loads (salary, benefits, tools, vehicle, training, "
                    "non-productive time): an unexplained rate cannot be approved."
                )
            if rate.measure_from and rate.measure_to and rate.measure_from > rate.measure_to:
                raise ValidationError("The comparison window ends before it starts.")

    @api.model_create_multi
    def create(self, vals_list):
        _require_finance(self.env, "Recording a planned activity rate")
        rates = super().create(vals_list)
        for rate in rates:
            rate._guarded().write(
                {"name": self.env["ir.sequence"].next_by_code("fix.activity.rate") or "/"}
            )
        return rates

    def write(self, vals):
        frozen = any(r.state not in self._OPEN_STATES for r in self)
        if frozen and not self._fix_guard_open() and _changes(self, vals):
            raise UserError(
                "A submitted or approved rate is a record of what was decided and cannot "
                "be edited. Record a new rate: once approved it replaces this one from "
                "its effective date (BRU-FPA-16)."
            )
        return super().write(vals)

    def unlink(self):
        if not self.env.su and any(r.state not in self._OPEN_STATES for r in self):
            raise UserError("Only a draft or rejected rate can be deleted.")
        return super().unlink()

    # ------------------------------------------------------------ actions
    def action_measure(self):
        """Measure the actual loaded technician rate over the comparison window
        (payroll + loaded overhead over productive hours), so the approver sees
        the planned rate beside what the ledger says an hour actually cost."""
        _require_finance(self.env, "Measuring a planned rate against actuals")
        engine = self.env["fix.fpa.engine"]
        for rate in self:
            if rate.state not in self._OPEN_STATES:
                raise UserError("Only a draft rate is measured.")
            if rate.activity_type != "technician_hour":
                raise UserError(
                    "Only the technician-hour rate is measured from payroll and work orders; "
                    "say in the composition how this rate was built."
                )
            d_to = rate.measure_to or (rate.effective_from - timedelta(days=1))
            d_from = rate.measure_from or (d_to - relativedelta(months=12) + timedelta(days=1))
            rates, _overhead = engine.technician_rates(d_from, d_to)
            rated = [r for r in rates.values() if r["rate"] is not None]
            hours = sum(r["hours"] for r in rated)
            cost = sum(r["payroll"] + r["overhead"] for r in rated)
            rate._guarded().write(
                {
                    "measure_from": d_from,
                    "measure_to": d_to,
                    "measured_rate": round(cost / hours, 2) if hours else 0.0,
                    "measured_hours": round(hours, 2),
                    "measured_at": fields.Datetime.now(),
                }
            )
        return True

    def action_submit(self):
        _require_finance(self.env, "Submitting a planned rate")
        for rate in self:
            if rate.state not in self._OPEN_STATES:
                raise UserError("Only a draft or rejected rate can be submitted.")
            rate._guarded().write(
                {
                    "state": "submitted",
                    "submitted_by": self.env.uid,
                    "submitted_at": fields.Datetime.now(),
                    "rejection_reason": False,
                }
            )
        return True

    def action_approve(self):
        """An Accounting Administrator who neither prepared nor submitted the
        rate approves it (the CFO, BRU-FPA-16, until a CFO group exists). The
        rate in force for the same activity and branch ends the day before."""
        _require_group(self.env, ACCOUNT_MANAGER, "Approving a planned rate")
        today = fields.Date.context_today(self)
        for rate in self:
            if rate.state != "submitted":
                raise UserError("Only a submitted rate can be approved.")
            _require_other_person(
                self.env,
                rate.create_uid | rate.write_uid | rate.submitted_by,
                "approving rate %s" % rate.name,
            )
            current = self.search(
                [
                    ("id", "!=", rate.id),
                    ("state", "=", "approved"),
                    ("company_id", "=", rate.company_id.id),
                    ("activity_type", "=", rate.activity_type),
                    ("branch_id", "=", rate.branch_id.id),
                    "|",
                    ("effective_to", "=", False),
                    ("effective_to", ">=", rate.effective_from),
                ]
            )
            if current and rate.effective_from < today:
                raise UserError(
                    "Rate %s would replace %s from %s, a date already past: job costs "
                    "already measured at the old rate would change. A replacement takes "
                    "effect today or later." % (rate.name, current[0].name, rate.effective_from)
                )
            for old in current:
                if old.effective_from >= rate.effective_from:
                    old._guarded().write({"state": "superseded", "superseded_by_id": rate.id})
                else:
                    old._guarded().write(
                        {
                            "effective_to": rate.effective_from - timedelta(days=1),
                            "superseded_by_id": rate.id,
                        }
                    )
            rate._guarded().write(
                {
                    "state": "approved",
                    "approved_by": self.env.uid,
                    "approved_at": fields.Datetime.now(),
                }
            )
        return True

    def action_reject(self, reason=None):
        _require_group(self.env, ACCOUNT_MANAGER, "Rejecting a planned rate")
        if not (reason or "").strip():
            raise UserError("Say why the rate is rejected.")
        for rate in self:
            if rate.state != "submitted":
                raise UserError("Only a submitted rate can be rejected.")
            _require_other_person(self.env, rate.submitted_by, "rejecting rate %s" % rate.name)
            rate._guarded().write({"state": "rejected", "rejection_reason": reason.strip()})
        return True

    # ------------------------------------------------------------ lookup
    @api.model
    def rate_book(self, activity_type, companies):
        """A resolver (branch id, date) -> approved planned rate or None. A
        branch's own rate wins over the all-branch rate."""
        rows = self.sudo().search_read(
            [
                ("state", "=", "approved"),
                ("activity_type", "=", activity_type),
                ("company_id", "in", list(companies)),
            ],
            ["branch_id", "effective_from", "effective_to", "planned_rate"],
            order="effective_from desc",
        )

        def resolve(branch_id, on_date):
            if not on_date:
                return None
            best = None
            for row in rows:
                if row["effective_from"] > on_date:
                    continue
                if row["effective_to"] and row["effective_to"] < on_date:
                    continue
                own = row["branch_id"] and row["branch_id"][0] == branch_id
                if own:
                    return row["planned_rate"]
                if not row["branch_id"] and best is None:
                    best = row["planned_rate"]
            return best

        return resolve


class FixBudgetTarget(models.Model):
    """A top-down budget target (FR-FPA-029, spec 8.2 "Target set")."""

    _name = "fix.budget.target"
    _description = "Budget Target"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "version_id, scope_type, id"

    name = fields.Char(string="Reference", readonly=True, copy=False, default="/")
    version_id = fields.Many2one(
        "fix.budget.version",
        string="Budget Version",
        index=True,
        ondelete="restrict",
        domain="[('version_type', 'in', ('budget', 'forecast')), "
        "('state', 'in', ('draft', 'submitted'))]",
    )
    company_id = fields.Many2one(related="version_id.company_id", store=True, index=True)
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    fiscal_year = fields.Char(related="version_id.fiscal_year", store=True)
    currency_id = fields.Many2one(related="version_id.currency_id")
    scope_type = fields.Selection(
        [
            ("company", "Whole Company"),
            ("branch", "Branch"),
            ("business_line", "Business Line"),
            ("cost_centre", "Cost Centre"),
        ],
        string="Target For",
        required=True,
        default="company",
    )
    branch_id = fields.Many2one("fix.branch", string="Branch")
    business_line_id = fields.Many2one("fix.business.line", string="Business Line")
    cost_centre_id = fields.Many2one("fix.cost.centre", string="Cost Centre")
    target_type = fields.Selection(
        [("revenue", "Revenue"), ("cost", "Cost"), ("margin", "Margin")],
        string="Target Measure",
        required=True,
        default="revenue",
    )
    target_amount = fields.Monetary(string="Target", currency_field="currency_id", tracking=True)
    note = fields.Text(string="Guidance to Preparers")
    plan_amount = fields.Monetary(
        string="Planned in the Version", currency_field="currency_id", compute="_compute_plan"
    )
    departure = fields.Monetary(
        string="Plan − Target", currency_field="currency_id", compute="_compute_plan"
    )
    departure_pct = fields.Float(string="Departure %", compute="_compute_plan")
    state = fields.Selection(
        [("draft", "Draft"), ("issued", "Issued"), ("withdrawn", "Withdrawn")],
        default="draft",
        required=True,
        tracking=True,
        copy=False,
    )
    issued_by = fields.Many2one("res.users", readonly=True, copy=False)
    issued_at = fields.Datetime(readonly=True, copy=False)
    withdrawn_by = fields.Many2one("res.users", readonly=True, copy=False)
    withdraw_reason = fields.Text(readonly=True, copy=False)

    _GUARDED = {"name", "state", "issued_by", "issued_at", "withdrawn_by", "withdraw_reason"}

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | self._GUARDED

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(t.state != "draft" for t in self):
            locked |= {n for n in self._fields if n not in LOCK_EXEMPT}
        return locked

    def _scope_lines(self):
        self.ensure_one()
        lines = self.version_id.sudo().budget_ids.line_ids
        if self.scope_type == "branch":
            return lines.filtered(lambda ln: ln.branch_id == self.branch_id)
        if self.scope_type == "business_line":
            return lines.filtered(lambda ln: ln.business_line_id == self.business_line_id)
        if self.scope_type == "cost_centre":
            code = (self.cost_centre_id.code or "").strip()
            return lines.filtered(lambda ln: (ln.cost_centre or "").strip() == code)
        return lines

    @api.depends(
        "version_id.budget_ids.line_ids.planned_amount",
        "scope_type",
        "branch_id",
        "business_line_id",
        "cost_centre_id",
        "target_type",
        "target_amount",
    )
    def _compute_plan(self) -> None:
        for target in self:
            if not target.version_id:
                target.plan_amount = target.departure = target.departure_pct = 0.0
                continue
            lines = target._scope_lines()
            rev = sum(ln.planned_amount for ln in lines if ln.is_revenue)
            cost = sum(ln.planned_amount for ln in lines if not ln.is_revenue)
            plan = {"revenue": rev, "cost": cost, "margin": rev - cost}[target.target_type]
            target.plan_amount = plan
            target.departure = plan - (target.target_amount or 0.0)
            target.departure_pct = (
                round(100.0 * target.departure / abs(target.target_amount), 2)
                if target.target_amount
                else 0.0
            )

    @api.depends("name", "scope_type", "target_type")
    def _compute_display_name(self) -> None:
        for target in self:
            scope = (
                target.branch_id.display_name
                or target.business_line_id.display_name
                or target.cost_centre_id.display_name
                or "Company"
            )
            target.display_name = "%s %s %s" % (
                target.name if target.name and target.name != "/" else "",
                scope,
                dict(target._fields["target_type"].selection).get(target.target_type, ""),
            )

    @api.constrains("scope_type", "branch_id", "business_line_id", "cost_centre_id", "version_id")
    def _check_scope(self) -> None:
        need = {
            "branch": "branch_id",
            "business_line": "business_line_id",
            "cost_centre": "cost_centre_id",
        }
        for target in self:
            if not target.version_id:
                raise ValidationError("A target is set for a budget version.")
            if target.version_id.version_type == "scenario":
                raise ValidationError("Targets are set for budget and forecast versions only.")
            field = need.get(target.scope_type)
            if field and not target[field]:
                raise ValidationError(
                    "A %s target names the %s."
                    % (
                        dict(target._fields["scope_type"].selection)[target.scope_type].lower(),
                        target._fields[field].string.lower(),
                    )
                )
            for other in set(need.values()) - {field}:
                if target[other]:
                    raise ValidationError(
                        "A target has one scope: clear the %s."
                        % target._fields[other].string.lower()
                    )

    @api.constrains("target_amount", "target_type")
    def _check_amount(self) -> None:
        for target in self:
            if not target.target_amount:
                raise ValidationError("A target needs an amount.")
            if target.target_type != "margin" and target.target_amount < 0:
                raise ValidationError("A revenue or cost target is a positive amount.")

    @api.model_create_multi
    def create(self, vals_list):
        _require_group(self.env, ACCOUNT_MANAGER, "Setting a budget target")
        targets = super().create(vals_list)
        for target in targets:
            target._guarded().write(
                {"name": self.env["ir.sequence"].next_by_code("fix.budget.target") or "/"}
            )
        return targets

    def write(self, vals):
        issued = any(t.state != "draft" for t in self)
        if issued and not self._fix_guard_open() and _changes(self, vals):
            raise UserError(
                "An issued target is what the preparers were told; withdraw it and issue "
                "a new one instead of changing it."
            )
        return super().write(vals)

    def unlink(self):
        if not self.env.su and any(t.state != "draft" for t in self):
            raise UserError("Only a draft target can be deleted; withdraw an issued one.")
        return super().unlink()

    def _scope_key(self):
        return (
            self.version_id.id,
            self.scope_type,
            self.branch_id.id,
            self.business_line_id.id,
            self.cost_centre_id.id,
            self.target_type,
        )

    def action_issue(self):
        _require_group(self.env, ACCOUNT_MANAGER, "Issuing a budget target")
        for target in self:
            if target.state != "draft":
                raise UserError("Only a draft target can be issued.")
            if target.version_id.state not in ("draft", "submitted"):
                raise UserError(
                    "Version %s is %s: targets are issued before a version is approved."
                    % (target.version_id.name, target.version_id.state)
                )
            key = target._scope_key()
            clash = self.search(
                [
                    ("id", "!=", target.id),
                    ("state", "=", "issued"),
                    ("version_id", "=", target.version_id.id),
                ]
            ).filtered(lambda t, key=key: t._scope_key() == key)
            if clash:
                raise UserError(
                    "Target %s is already issued for this scope and measure; withdraw it first."
                    % clash[0].name
                )
            target._guarded().write(
                {"state": "issued", "issued_by": self.env.uid, "issued_at": fields.Datetime.now()}
            )
        return True

    def action_withdraw(self, reason=None):
        _require_group(self.env, ACCOUNT_MANAGER, "Withdrawing a budget target")
        if not (reason or "").strip():
            raise UserError("Say why the target is withdrawn.")
        for target in self:
            if target.state != "issued":
                raise UserError("Only an issued target can be withdrawn.")
            target._guarded().write(
                {
                    "state": "withdrawn",
                    "withdrawn_by": self.env.uid,
                    "withdraw_reason": reason.strip(),
                }
            )
        return True


class FixBudgetVersionTargets(models.Model):
    """AUT-FPA-13: a submitted version is compared with its issued targets."""

    _inherit = "fix.budget.version"

    target_ids = fields.One2many("fix.budget.target", "version_id", string="Targets")

    def action_submit(self):
        res = super().action_submit()
        for ver in self:
            targets = ver.target_ids.filtered(lambda t: t.state == "issued")
            if not targets:
                continue
            rows = [
                "%s: plan %.2f against target %.2f (%+.2f, %+.2f%%)"
                % (t.display_name, t.plan_amount, t.target_amount, t.departure, t.departure_pct)
                for t in targets
            ]
            ver.message_post(body="Submitted against the issued targets:\n" + "\n".join(rows))
        return res


class FixVarianceExplanation(models.Model):
    """The owner's explanation of a budget variance (FR-FPA-037, BRU-FPA-12)."""

    _name = "fix.variance.explanation"
    _description = "Variance Explanation"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "due_date desc, id desc"

    name = fields.Char(string="Reference", readonly=True, copy=False, default="/")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    scope_type = fields.Selection(
        [("line", "Budget Line"), ("branch", "Branch"), ("business_line", "Business Line")],
        string="Variance Of",
        required=True,
        default="line",
    )
    budget_line_id = fields.Many2one(
        "fix.budget.line",
        string="Budget Line",
        index=True,
        domain="[('version_id.state', '=', 'approved')]",
    )
    branch_id = fields.Many2one("fix.branch", string="Branch", index=True)
    business_line_id = fields.Many2one("fix.business.line", string="Business Line")
    cost_centre_id = fields.Many2one("fix.cost.centre", string="Cost Centre")
    date_from = fields.Date(string="Period From")
    date_to = fields.Date(string="Period To")
    version_id = fields.Many2one("fix.budget.version", string="Approved Version", readonly=True)
    planned = fields.Monetary(string="Budget", currency_field="currency_id", readonly=True)
    actual = fields.Monetary(string="Actual (GL)", currency_field="currency_id", readonly=True)
    variance = fields.Monetary(
        string="Variance (favourable +)", currency_field="currency_id", readonly=True
    )
    variance_pct = fields.Float(string="Variance %", readonly=True)
    threshold_amount = fields.Monetary(
        string="Threshold Amount", currency_field="currency_id", readonly=True
    )
    threshold_pct = fields.Float(string="Threshold %", readonly=True)
    breached = fields.Boolean(string="Above Threshold", readonly=True)
    measured_at = fields.Datetime(readonly=True)
    owner_id = fields.Many2one("res.users", string="Accountable Owner", tracking=True, index=True)
    due_date = fields.Date(string="Explain By", readonly=True)
    explanation = fields.Text(string="Explanation")
    root_cause = fields.Selection(ROOT_CAUSES, string="Root Cause")
    action_committed = fields.Text(string="Action Committed")
    state = fields.Selection(
        [
            ("open", "Awaiting Explanation"),
            ("submitted", "Submitted"),
            ("accepted", "Accepted"),
            ("returned", "Returned"),
        ],
        default="open",
        required=True,
        tracking=True,
        copy=False,
    )
    submitted_by = fields.Many2one("res.users", readonly=True, copy=False)
    submitted_at = fields.Datetime(readonly=True, copy=False)
    accepted_by = fields.Many2one("res.users", readonly=True, copy=False)
    accepted_at = fields.Datetime(readonly=True, copy=False)
    return_reason = fields.Text(readonly=True, copy=False)
    overdue = fields.Boolean(compute="_compute_overdue", string="Overdue")

    _MEASURED = {
        "version_id",
        "planned",
        "actual",
        "variance",
        "variance_pct",
        "threshold_amount",
        "threshold_pct",
        "breached",
        "measured_at",
        "due_date",
    }
    _GUARDED = _MEASURED | {
        "name",
        "state",
        "submitted_by",
        "submitted_at",
        "accepted_by",
        "accepted_at",
        "return_reason",
    }
    # what the variance is OF: fixed once measured (raise a new one instead)
    _SCOPE = {
        "scope_type",
        "budget_line_id",
        "branch_id",
        "business_line_id",
        "date_from",
        "date_to",
        "company_id",
    }
    _OWNER_TEXT = {"explanation", "root_cause", "action_committed"}

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | self._GUARDED

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self:
            locked |= self._SCOPE
            if any(e.state in ("submitted", "accepted") for e in self):
                locked |= {n for n in self._fields if n not in LOCK_EXEMPT}
        return locked

    def _compute_overdue(self) -> None:
        today = fields.Date.context_today(self)
        for exp in self:
            exp.overdue = bool(
                exp.state in ("open", "returned") and exp.due_date and exp.due_date < today
            )

    @api.depends("name", "scope_type", "date_from")
    def _compute_display_name(self) -> None:
        for exp in self:
            scope = (
                exp.budget_line_id.account_id.display_name
                if exp.scope_type == "line"
                else (exp.branch_id or exp.business_line_id).display_name
            )
            exp.display_name = "%s %s %s" % (
                exp.name if exp.name and exp.name != "/" else "",
                scope or "",
                exp.date_from or "",
            )

    @api.constrains(
        "scope_type", "budget_line_id", "branch_id", "business_line_id", "date_from", "date_to"
    )
    def _check_scope(self) -> None:
        for exp in self:
            if not exp.date_from or not exp.date_to:
                raise ValidationError("A variance is explained for a period: give both dates.")
            if exp.date_from > exp.date_to:
                raise ValidationError("The period ends before it starts.")
            need = {
                "line": "budget_line_id",
                "branch": "branch_id",
                "business_line": "business_line_id",
            }[exp.scope_type]
            if not exp[need]:
                raise ValidationError(
                    "A %s variance names the %s."
                    % (
                        dict(exp._fields["scope_type"].selection)[exp.scope_type].lower(),
                        exp._fields[need].string.lower(),
                    )
                )
            if exp.scope_type == "line" and exp.budget_line_id.version_id.state != "approved":
                raise ValidationError(
                    "A variance is measured against the approved budget version (BRU-FPA-10); "
                    "line %s belongs to a version that is not approved."
                    % exp.budget_line_id.display_name
                )

    # ------------------------------------------------------------ measuring
    def _scope_lines(self):
        """The approved budget lines the variance is measured on."""
        self.ensure_one()
        engine = self.env["fix.fpa.engine"]
        if self.scope_type == "line":
            line = self.budget_line_id
            ok = (
                line.version_id.state == "approved"
                and line.date_from <= self.date_to
                and line.date_to >= self.date_from
            )
            return line if ok else line.browse()
        lines = engine.approved_budget_lines(self.date_from, self.date_to)
        if self.scope_type == "branch":
            return lines.filtered(lambda ln: ln.branch_id == self.branch_id)
        return lines.filtered(lambda ln: ln.business_line_id == self.business_line_id)

    def _measure(self):
        """{field: value} measured from the approved budget and the posted GL."""
        self.ensure_one()
        engine = self.env["fix.fpa.engine"]
        lines = self._scope_lines()
        if not lines:
            raise UserError(
                "No line of the approved budget falls in %s – %s for this %s: there is no "
                "variance to explain."
                % (
                    self.date_from,
                    self.date_to,
                    dict(self._fields["scope_type"].selection)[self.scope_type].lower(),
                )
            )
        actuals = engine.line_actuals(lines, self.date_from, self.date_to)
        planned = actual = var = 0.0
        for ln in lines:
            p = engine.planned_in_window(ln, self.date_from, self.date_to)
            a = actuals.get(ln.id, 0.0)
            planned += p
            actual += a
            var += (a - p) if ln.is_revenue else (p - a)
        thr_amount = _float_param(self.env, PARAM_THRESHOLD_AMOUNT, DEFAULT_THRESHOLD_AMOUNT)
        thr_pct = _float_param(self.env, PARAM_THRESHOLD_PCT, DEFAULT_THRESHOLD_PCT)
        pct = round(100.0 * var / abs(planned), 2) if planned else 0.0
        return {
            "version_id": lines[0].version_id.id,
            "planned": round(planned, 2),
            "actual": round(actual, 2),
            "variance": round(var, 2),
            "variance_pct": pct,
            "threshold_amount": thr_amount,
            "threshold_pct": thr_pct,
            "breached": abs(var) >= thr_amount and (not planned or abs(pct) >= thr_pct),
            "measured_at": fields.Datetime.now(),
        }

    def _default_owner(self):
        """The cost-centre owner, else the branch's or the version's preparer."""
        self.ensure_one()
        Centre = self.env["fix.cost.centre"]
        owner = self.cost_centre_id.owner_id
        if not owner and self.scope_type == "line":
            owner = Centre.owner_for_code(self.budget_line_id.cost_centre, self.company_id)
        if not owner and self.version_id:
            owner = self.version_id.submitted_by or self.version_id.create_uid
        return owner

    @api.model_create_multi
    def create(self, vals_list):
        _require_finance(self.env, "Raising a variance explanation")
        records = super().create(vals_list)
        today = fields.Date.context_today(self)
        for exp in records:
            exp._refuse_duplicate()
            stamps = exp._measure()
            stamps.update(
                {
                    "name": self.env["ir.sequence"].next_by_code("fix.variance.explanation") or "/",
                    "due_date": add_working_days(today, EXPLAIN_WORKING_DAYS),
                }
            )
            exp._guarded().write(stamps)
            if not exp.owner_id:
                owner = exp._default_owner()
                if owner:
                    exp._guarded().write({"owner_id": owner.id})
            if exp.owner_id:
                exp.message_subscribe(partner_ids=exp.owner_id.partner_id.ids)
        return records

    def _refuse_duplicate(self):
        self.ensure_one()
        clash = self.search(
            [
                ("id", "!=", self.id),
                ("company_id", "=", self.company_id.id),
                ("scope_type", "=", self.scope_type),
                ("budget_line_id", "=", self.budget_line_id.id),
                ("branch_id", "=", self.branch_id.id),
                ("business_line_id", "=", self.business_line_id.id),
                ("date_from", "=", self.date_from),
                ("date_to", "=", self.date_to),
            ],
            limit=1,
        )
        if clash:
            raise UserError("Explanation %s already covers this variance and period." % clash.name)

    def write(self, vals):
        if self and not self._fix_guard_open():
            changed = _changed_names(self, vals)
            if changed & self._SCOPE:
                raise UserError(
                    "The variance was measured for this scope and period; raise a new "
                    "explanation for another one."
                )
            if changed and any(e.state in ("submitted", "accepted") for e in self):
                raise UserError(
                    "A submitted explanation is under review and an accepted one is final; "
                    "it changes only if the reviewer returns it."
                )
            if "owner_id" in changed:
                _require_group(self.env, ACCOUNT_MANAGER, "Reassigning a variance explanation")
            if changed & self._OWNER_TEXT:
                for exp in self:
                    if exp.owner_id and self.env.user != exp.owner_id:
                        raise UserError(
                            "Only the accountable owner, %s, writes the explanation "
                            "(BRU-FPA-12)." % exp.owner_id.name
                        )
        return super().write(vals)

    def unlink(self):
        if not self.env.su:
            raise UserError(
                "A variance explanation is part of the close record; it is never deleted."
            )
        return super().unlink()

    # ------------------------------------------------------------ actions
    def action_remeasure(self):
        """Measure again (late postings) while the explanation is still open."""
        _require_finance(self.env, "Re-measuring a variance")
        for exp in self:
            if exp.state not in ("open", "returned"):
                raise UserError("Only an open explanation is re-measured.")
            exp._guarded().write(exp._measure())
        return True

    def action_submit(self):
        for exp in self:
            if exp.state not in ("open", "returned"):
                raise UserError("Only an open or returned explanation can be submitted.")
            if not exp.owner_id:
                raise UserError("Name the accountable owner first.")
            if not self.env.su and self.env.user != exp.owner_id:
                raise UserError(
                    "Only the accountable owner, %s, submits the explanation (BRU-FPA-12)."
                    % exp.owner_id.name
                )
            if not (exp.explanation or "").strip() or not exp.root_cause:
                raise UserError("Give the explanation and its root cause before submitting.")
            exp._guarded().write(
                {
                    "state": "submitted",
                    "submitted_by": self.env.uid,
                    "submitted_at": fields.Datetime.now(),
                    "return_reason": False,
                }
            )
        return True

    def _assert_reviewer(self, what):
        _require_group(self.env, ACCOUNT_MANAGER, what)
        for exp in self:
            if exp.state != "submitted":
                raise UserError("Only a submitted explanation is reviewed.")
            _require_other_person(self.env, exp.owner_id | exp.submitted_by, what)

    def action_accept(self):
        self._assert_reviewer("Accepting a variance explanation")
        self._guarded().write(
            {"state": "accepted", "accepted_by": self.env.uid, "accepted_at": fields.Datetime.now()}
        )
        return True

    def action_return(self, reason=None):
        if not (reason or "").strip():
            raise UserError("Say what the owner must add or correct.")
        self._assert_reviewer("Returning a variance explanation")
        self._guarded().write({"state": "returned", "return_reason": reason.strip()})
        for exp in self:
            exp.message_post(
                body="Returned: %s" % reason.strip(), partner_ids=exp.owner_id.partner_id.ids
            )
        return True

    # ------------------------------------------------------------ automation
    @api.model
    def _last_month(self, today=None):
        today = today or fields.Date.context_today(self)
        first = today.replace(day=1)
        last_from = first - relativedelta(months=1)
        return last_from, first - timedelta(days=1)

    @api.model
    def _cron_raise_explanations(self, today=None):
        """AUT-FPA-07/08: raise an explanation for every line of the approved
        budget whose variance last month passed the threshold."""
        env = self.env(su=True)
        Exp = env["fix.variance.explanation"]
        engine = env["fix.fpa.engine"]
        d_from, d_to = Exp._last_month(today)
        thr_amount = _float_param(env, PARAM_THRESHOLD_AMOUNT, DEFAULT_THRESHOLD_AMOUNT)
        thr_pct = _float_param(env, PARAM_THRESHOLD_PCT, DEFAULT_THRESHOLD_PCT)
        lines = env["fix.budget.line"].search(
            [
                ("version_id.state", "=", "approved"),
                ("date_from", "<=", d_to),
                ("date_to", ">=", d_from),
            ]
        )
        actuals = engine.line_actuals(lines, d_from, d_to) if lines else {}
        raised = Exp.browse()
        for ln in lines:
            planned = engine.planned_in_window(ln, d_from, d_to)
            actual = actuals.get(ln.id, 0.0)
            var = (actual - planned) if ln.is_revenue else (planned - actual)
            pct = abs(100.0 * var / planned) if planned else 100.0
            if abs(var) < thr_amount or pct < thr_pct:
                continue
            if Exp.search_count(
                [
                    ("scope_type", "=", "line"),
                    ("budget_line_id", "=", ln.id),
                    ("date_from", "=", d_from),
                    ("date_to", "=", d_to),
                ]
            ):
                continue
            raised |= Exp.with_company(ln.company_id).create(
                {
                    "company_id": ln.company_id.id,
                    "scope_type": "line",
                    "budget_line_id": ln.id,
                    "date_from": d_from,
                    "date_to": d_to,
                    "operating_unit_id": ln.operating_unit_id.id,
                }
            )
        for exp in raised.filtered("owner_id"):
            exp.activity_schedule(
                "mail.mail_activity_data_todo",
                date_deadline=exp.due_date,
                summary="Explain the %s variance" % exp.display_name,
                user_id=exp.owner_id.id,
            )
        if raised:
            _logger.info("M54: raised %s variance explanation(s) for %s", len(raised), d_from)
        return raised

    @api.model
    def _cron_overdue(self, today=None):
        """AUT-FPA-08: an overdue explanation gets a to-do for its owner."""
        env = self.env(su=True)
        today = today or fields.Date.context_today(self)
        late = env["fix.variance.explanation"].search(
            [
                ("state", "in", ("open", "returned")),
                ("due_date", "<", today),
                ("owner_id", "!=", False),
            ]
        )
        todo = env.ref("mail.mail_activity_data_todo")
        for exp in late:
            if exp.activity_ids.filtered(lambda a: a.activity_type_id == todo):
                continue
            exp.activity_schedule(
                "mail.mail_activity_data_todo",
                date_deadline=today,
                summary="Overdue: explain the %s variance (was due %s)"
                % (exp.display_name, exp.due_date),
                user_id=exp.owner_id.id,
            )
        return late


class FixFpaEngineRates(models.AbstractModel):
    """Job costing applies the approved planned rate where one is in force."""

    _inherit = "fix.fpa.engine"

    @api.model
    def planned_rate_book(self, activity_type="technician_hour"):
        if "fix.activity.rate" not in self.env:
            return lambda _branch, _day: None
        return self.env["fix.activity.rate"].rate_book(activity_type, self._companies())
