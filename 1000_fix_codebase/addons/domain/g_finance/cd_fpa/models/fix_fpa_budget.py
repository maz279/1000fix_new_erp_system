# fix_fpa_budget — M54 budget versions (draft -> submitted -> approved with
# segregation of duties), budget lines measured against the posted GL, and
# driver-based scenario / forecast versions.
#
# A08 remediation (B3, 4 Nov 2026; M54-1, -2, -5, -6, -8, P1-5):
#   - state and the submit/approve stamps are guarded (fix.dofa.mixin): only the
#     transitions write them, so "approved" can no longer be typed (ORM or P03);
#   - approval is a routed M63 request on the version's planned total, decided by
#     a holder of the DOFA tier (Tier 4 = CFO up to cd_fpa.budget_board_threshold,
#     Tier 5 = MD / Board above it) who is also an Accounting Administrator and
#     is not the preparer (creator of the version, its budgets or lines, their last
#     editor) or the submitter;
#   - an approved version is immutable; a revision is a NEW version
#     (action_create_revision) with its own approval, and approving it supersedes
#     the original (BRU-FPA-09/13, T-10, FR-FPA-034);
#   - one approved budget/forecast version per company and fiscal year (index).
#
# Role map (M54-8, decision B1/B3 pending): the spec's approvers are the CFO and,
# above threshold, the CEO/Board. Odoo has no such groups; they are the DOFA tier
# groups of cd_entity_config: tier_4 "CFO / CCO / COO" and tier_5 "Managing
# Director / Board", intersected with account.group_account_manager (so a CCO or
# COO with Tier 4 but no finance role does not approve budgets). Preparation and
# submission are open to the Accountant AND the Accounting Administrator.
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError

from .fix_fpa import VERSION_STATES
from .fix_fpa_engine import month_starts

DRIVER_KEYS = [
    ("orders_per_month", "Service Orders per Month"),
    ("revenue_per_order", "Revenue per Order"),
    ("parts_cost_pct", "Parts Cost % of Revenue"),
    ("labour_hours_per_order", "Labour Hours per Order"),
    ("loaded_labour_rate", "Loaded Labour Rate per Hour"),
    ("overhead_per_month", "Operating Overhead per Month"),
]
MANAGER_GROUP = "account.group_account_manager"
USER_GROUP = "account.group_account_user"
# Spec M54 §8.2: "Approved by the CFO and, above threshold, the CEO or board".
# The spec gives no figure (decision B3); default BDT 10,000,000.
PARAM_BOARD_THRESHOLD = "cd_fpa.budget_board_threshold"
DEFAULT_BOARD_THRESHOLD = 10000000.0
# Fields a version may still receive once it left draft (everything else is the
# approved content; the stamps among them are guarded).
_VERSION_UNLOCKED = {
    "state",
    "submitted_by",
    "submitted_at",
    "approved_by",
    "approved_at",
    "rejection_reason",
    "message_main_attachment_id",
    "dofa_justification",
    "dofa_approved",
    "dofa_approved_by",
    "dofa_approved_at",
    "dofa_approved_tier",
    "dofa_approved_amount",
    "approval_state",
    "approval_request_id",
    "approval_amount_changed_by_id",
}


def _float_param(env, key, default):
    raw = env["ir.config_parameter"].sudo().get_param(key)
    try:
        return float(raw) if raw not in (None, False, "") else float(default)
    except (TypeError, ValueError):
        return float(default)


class FixBudgetVersion(models.Model):
    """A budget / forecast / scenario version. Budgets and lines are editable
    only while the version is draft; approval is a routed request decided by
    a CFO (or, above the threshold, Board) holder who neither prepared nor
    submitted it. Approving a budget or forecast version supersedes the
    earlier approved one of the same year."""

    _name = "fix.budget.version"
    _description = "Budget Version"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.dofa.mixin"]
    _order = "date_from desc, id desc"
    _approval_domain = "budget_version"
    _approval_routed = True
    _approval_apply_method = "action_dofa_approve"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True, tracking=True)
    version_type = fields.Selection(
        [("budget", "Budget"), ("forecast", "Forecast"), ("scenario", "Scenario")],
        string="Version Type",
        required=True,
        default="budget",
        tracking=True,
    )
    fiscal_year = fields.Char(required=True)
    date_from = fields.Date(string="From", required=True)
    date_to = fields.Date(string="To", required=True)
    state = fields.Selection(
        VERSION_STATES, default="draft", required=True, tracking=True, copy=False
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    budget_ids = fields.One2many("fix.budget", "version_id", string="Budgets", copy=True)
    driver_ids = fields.One2many("fix.fpa.driver", "version_id", string="Drivers", copy=True)
    base_version_id = fields.Many2one(
        "fix.budget.version",
        string="Compared With",
        help="The version this scenario is read against",
    )
    revision_of_id = fields.Many2one(
        "fix.budget.version",
        string="Revision Of",
        readonly=True,
        copy=False,
        help="The approved version this revision replaces once it is approved itself.",
    )
    revision_no = fields.Integer(string="Revision", readonly=True, copy=False, default=0)
    base_date_from = fields.Date(
        string="Drivers Measured From", help="Window the base driver values are measured on"
    )
    base_date_to = fields.Date(string="Drivers Measured To")
    revenue_account_id = fields.Many2one("account.account", string="Revenue Account")
    parts_account_id = fields.Many2one("account.account", string="Parts Cost Account")
    labour_account_id = fields.Many2one("account.account", string="Labour Cost Account")
    overhead_account_id = fields.Many2one("account.account", string="Overhead Account")
    planned_revenue = fields.Monetary(
        compute="_compute_totals", store=True, currency_field="currency_id"
    )
    planned_cost = fields.Monetary(
        compute="_compute_totals", store=True, currency_field="currency_id"
    )
    planned_margin = fields.Monetary(
        compute="_compute_totals", store=True, currency_field="currency_id"
    )
    submitted_by = fields.Many2one("res.users", readonly=True, copy=False, tracking=True)
    submitted_at = fields.Datetime(readonly=True, copy=False)
    approved_by = fields.Many2one("res.users", readonly=True, copy=False, tracking=True)
    approved_at = fields.Datetime(readonly=True, copy=False)
    rejection_reason = fields.Text(copy=False)

    _one_approved_per_year = models.UniqueIndex(
        "(company_id, version_type, fiscal_year) "
        "WHERE state = 'approved' AND version_type IN ('budget', 'forecast')",
        "One approved budget (and one approved forecast) per company and fiscal year.",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "submitted_by",
            "submitted_at",
            "approved_by",
            "approved_at",
            "revision_of_id",
            "revision_no",
        }

    @api.depends(
        "budget_ids.line_ids.planned_amount", "budget_ids.line_ids.account_id.account_type"
    )
    def _compute_totals(self) -> None:
        for ver in self:
            rev = cost = 0.0
            for line in ver.budget_ids.line_ids:
                if line.is_revenue:
                    rev += line.planned_amount
                else:
                    cost += line.planned_amount
            ver.planned_revenue, ver.planned_cost, ver.planned_margin = rev, cost, rev - cost

    @api.depends("planned_revenue", "planned_cost")
    def _compute_dofa_tier_required(self):
        return super()._compute_dofa_tier_required()

    @api.constrains("date_from", "date_to")
    def _check_window(self) -> None:
        for ver in self:
            if ver.date_from > ver.date_to:
                raise ValidationError("Version %s ends before it starts" % ver.name)

    # ------------------------------------------------------------ DOFA

    def _dofa_amount(self) -> float:
        self.ensure_one()
        lines = self.sudo().budget_ids.line_ids
        return round(sum(abs(line.planned_amount) for line in lines), 2)

    def _dofa_thresholds(self):
        return [
            (_float_param(self.env, PARAM_BOARD_THRESHOLD, DEFAULT_BOARD_THRESHOLD), "tier_4"),
            (float("inf"), "tier_5"),
        ]

    def _dofa_amount_label(self) -> str:
        self.ensure_one()
        return "budget version %s (BDT %.2f planned)" % (self.name, self._dofa_amount())

    def _fpa_conflicted_users(self):
        """The preparer (whoever created or last edited the version, its
        budgets or its lines) and the submitter never approve it (BRU-FPA-11)."""
        self.ensure_one()
        rec = self.sudo()
        budgets = rec.budget_ids
        lines = budgets.line_ids
        users = (
            rec.create_uid
            | budgets.mapped("create_uid")
            | budgets.mapped("write_uid")
            | lines.mapped("create_uid")
            | lines.mapped("write_uid")
            | rec.submitted_by
            | rec.approval_request_id.requested_by_id
        )
        return users.filtered(lambda u: not u._is_superuser())

    def _approval_excluded(self):
        return (super()._approval_excluded() | self._fpa_conflicted_users()).sudo()

    def _approval_holders(self, group):
        users = super()._approval_holders(group)
        return users.filtered(lambda u: u.has_group(MANAGER_GROUP))

    # ------------------------------------------------------------ workflow

    def _check_editable(self) -> None:
        for ver in self:
            if ver.state != "draft":
                raise UserError(
                    "Version %s is %s — only a draft version can be changed; an approved "
                    "budget is revised as a new version (Create Revision)."
                    % (ver.name, dict(VERSION_STATES)[ver.state].lower())
                )

    def write(self, vals):
        locked = set(vals) - _VERSION_UNLOCKED
        if locked:
            self._check_editable()
        return super().write(vals)

    def unlink(self):
        for ver in self:
            if ver.state not in ("draft", "rejected"):
                raise UserError(
                    "Version %s is %s and is kept for audit; only draft or rejected "
                    "versions can be deleted" % (ver.name, ver.state)
                )
        return super().unlink()

    def _require_group(self, xmlid, what):
        if not self.env.su and not self.env.user.has_group(xmlid):
            raise AccessError("%s needs the %s role" % (what, self.env.ref(xmlid).name))

    def _require_preparer(self, what):
        """M54-8: the Accountant and the Accounting Administrator both prepare."""
        if self.env.su:
            return
        if not (self.env.user.has_group(USER_GROUP) or self.env.user.has_group(MANAGER_GROUP)):
            raise AccessError("%s needs the Accountant or Accounting Administrator role" % what)

    def action_submit(self):
        """Submit for approval: the version is locked and routed to a CFO (or
        Board, above the threshold) holder who did not prepare or submit it."""
        self._require_preparer("Submitting a budget version")
        for ver in self:
            if ver.state != "draft":
                raise UserError("Only a draft version can be submitted")
            if not ver.budget_ids.line_ids:
                raise UserError("Version %s has no budget lines to submit" % ver.name)
            ver._guarded().write(
                {
                    "state": "submitted",
                    "submitted_by": self.env.uid,
                    "submitted_at": fields.Datetime.now(),
                    "rejection_reason": False,
                }
            )
            ver.action_request_approval(
                justification=ver.dofa_justification
                or "Budget version %s (%s) submitted for approval" % (ver.name, ver.fiscal_year)
            )
        return True

    def _fpa_assert_decider(self):
        self.ensure_one()
        if self.env.su:
            return
        self._require_group(MANAGER_GROUP, "Approving a budget version")
        task = self._approval_task()
        clash = (self.env.user | task.on_behalf_of_id) & self._fpa_conflicted_users()
        if clash:
            raise UserError(
                "Segregation of duties: %s prepared or submitted version %s and cannot approve "
                "it (BRU-FPA-11)." % (", ".join(clash.mapped("name")), self.name)
            )

    def action_dofa_approve(self):
        """The engine's apply method, run from the approver's inbox task."""
        self._approval_assert_routed()
        for ver in self:
            ver._fpa_assert_decider()
            if ver.state != "submitted":
                raise UserError("Only a submitted version can be approved")
        if self.env.su:
            # trusted code (seeds, migrations): no DOFA stamp to grant
            for ver in self:
                ver._fpa_mark_approved()
            return True
        result = super().action_dofa_approve()
        for ver in self:
            ver._fpa_mark_approved()
        return result

    def action_approve(self):
        """Kept for old callers and screens: a budget is approved from the M63
        inbox, so a direct call is refused by the routing guard."""
        return self.action_dofa_approve()

    def _fpa_mark_approved(self):
        self.ensure_one()
        if self.version_type in ("budget", "forecast"):
            previous = self.sudo().search(
                [
                    ("id", "!=", self.id),
                    ("company_id", "=", self.company_id.id),
                    ("version_type", "=", self.version_type),
                    ("fiscal_year", "=", self.fiscal_year),
                    ("state", "=", "approved"),
                ]
            )
            previous._guarded().write({"state": "superseded"})
            # the one-approved-per-year index: supersede before approving
            previous.flush_recordset(["state"])
        self._guarded().write(
            {"state": "approved", "approved_by": self.env.uid, "approved_at": fields.Datetime.now()}
        )
        self.message_post(body="Version approved by %s." % self.env.user.name)

    def _approval_on_rejected(self, comment):
        for ver in self.sudo():
            ver._guarded().write(
                {
                    "state": "rejected",
                    "rejection_reason": comment or ver.rejection_reason or "Rejected",
                }
            )
        return super()._approval_on_rejected(comment)

    def action_reject(self, reason=None):
        """`reason` is what the workspace prompt collects (M54-1): the button
        used to demand a field no form offered, so it could never work."""
        self._require_group(MANAGER_GROUP, "Rejecting a budget version")
        reason = (reason or "").strip()
        for ver in self:
            if ver.state != "submitted":
                raise UserError("Only a submitted version can be rejected")
            if not self.env.su and self.env.user in ver._fpa_conflicted_users():
                raise UserError("Segregation of duties: the preparer or submitter cannot reject.")
            if reason:
                ver.write({"rejection_reason": reason})
            if not ver.rejection_reason:
                raise UserError("State the rejection reason for version %s." % ver.name)
            if ver.approval_state == "pending":
                ver._approval_void(
                    "rejected by %s: %s" % (self.env.user.name, ver.rejection_reason)
                )
            ver._guarded().write({"state": "rejected"})
        return True

    def action_reset_draft(self):
        self._require_preparer("Re-opening a budget version")
        for ver in self:
            if ver.state != "rejected":
                raise UserError("Only a rejected version returns to draft")
            ver._guarded().write({"state": "draft", "submitted_by": False, "submitted_at": False})
        return True

    def action_create_revision(self):
        """BRU-FPA-09/13: an approved version is never edited. A revision is a
        new DRAFT version carrying the same budgets and lines, prepared and
        approved on its own; approving it supersedes the original."""
        self._require_preparer("Revising a budget version")
        revisions = self.browse()
        for ver in self:
            if ver.state != "approved":
                raise UserError("Only an approved version is revised.")
            number = ver.revision_no + 1
            rev = (
                self._guarded()
                .with_context(mail_create_nolog=True)
                .create(
                    {
                        "name": "%s (Rev %d)" % (ver.name.split(" (Rev ")[0], number),
                        "company_id": ver.company_id.id,
                        "operating_unit_id": ver.operating_unit_id.id,
                        "version_type": ver.version_type,
                        "fiscal_year": ver.fiscal_year,
                        "date_from": ver.date_from,
                        "date_to": ver.date_to,
                        "currency_id": ver.currency_id.id,
                        "base_version_id": ver.id,
                        "revision_of_id": ver.id,
                        "revision_no": number,
                    }
                )
            )
            for budget in ver.budget_ids:
                self.env["fix.budget"].create(
                    {
                        "name": budget.name,
                        "version_id": rev.id,
                        "budget_type": budget.budget_type,
                        "operating_unit_id": budget.operating_unit_id.id,
                        "line_ids": [
                            (
                                0,
                                0,
                                {
                                    "account_id": line.account_id.id,
                                    "branch_id": line.branch_id.id,
                                    "business_line_id": line.business_line_id.id,
                                    "cost_centre": line.cost_centre,
                                    "date_from": line.date_from,
                                    "date_to": line.date_to,
                                    "planned_amount": line.planned_amount,
                                },
                            )
                            for line in budget.line_ids
                        ],
                    }
                )
            ver.message_post(body="Revision %s opened by %s." % (rev.name, self.env.user.name))
            revisions |= rev
        return revisions

    # ------------------------------------------------------------ drivers

    def _base_window(self):
        self.ensure_one()
        if self.base_date_from and self.base_date_to:
            return self.base_date_from, self.base_date_to
        return self.date_from - relativedelta(months=12), self.date_from - relativedelta(days=1)

    def action_load_drivers(self):
        """Measure the six drivers on the base window (default: the twelve
        months before the version starts) and store them as base values; a
        scenario value already typed in is kept."""
        engine = self.env["fix.fpa.engine"]
        for ver in self:
            ver._check_editable()
            d_from, d_to = ver._base_window()
            base = engine.drivers_from_actuals(d_from, d_to)
            existing = {d.driver_key: d for d in ver.driver_ids}
            for key, _label in DRIVER_KEYS:
                value = round(base[key], 4)
                if key in existing:
                    drv = existing[key]
                    drv._guarded().write(
                        {
                            "base_value": value,
                            "scenario_value": drv.scenario_value
                            if drv.scenario_value_set
                            else value,
                        }
                    )
                else:
                    self.env["fix.fpa.driver"]._guarded().create(
                        {
                            "version_id": ver.id,
                            "driver_key": key,
                            "base_value": value,
                            "scenario_value": value,
                        }
                    )
            ver.write({"base_date_from": d_from, "base_date_to": d_to})
        return True

    def action_generate_plan(self):
        """Turn the scenario drivers into one monthly budget ("Driver plan")
        on the four configured accounts, replacing an earlier driver plan."""
        for ver in self:
            ver._check_editable()
            missing = [
                label
                for label, acc in (
                    ("revenue", ver.revenue_account_id),
                    ("parts cost", ver.parts_account_id),
                    ("labour cost", ver.labour_account_id),
                    ("overhead", ver.overhead_account_id),
                )
                if not acc
            ]
            if missing:
                raise UserError(
                    "Version %s: set the %s account(s) before generating the plan"
                    % (ver.name, ", ".join(missing))
                )
            drv = {d.driver_key: d.scenario_value for d in ver.driver_ids}
            absent = [label for key, label in DRIVER_KEYS if key not in drv]
            if absent:
                raise UserError(
                    "Version %s: load the drivers first (missing: %s)"
                    % (ver.name, ", ".join(absent))
                )
            revenue = drv["orders_per_month"] * drv["revenue_per_order"]
            monthly = (
                (ver.revenue_account_id, revenue),
                (ver.parts_account_id, revenue * drv["parts_cost_pct"] / 100.0),
                (
                    ver.labour_account_id,
                    drv["orders_per_month"]
                    * drv["labour_hours_per_order"]
                    * drv["loaded_labour_rate"],
                ),
                (ver.overhead_account_id, drv["overhead_per_month"]),
            )
            ver.budget_ids.filtered(lambda b: b.name == "Driver plan").unlink()
            lines = []
            for start in month_starts(ver.date_from, ver.date_to):
                end = min(start + relativedelta(months=1, days=-1), ver.date_to)
                for account, amount in monthly:
                    lines.append(
                        (
                            0,
                            0,
                            {
                                "account_id": account.id,
                                "date_from": max(start, ver.date_from),
                                "date_to": end,
                                "planned_amount": round(amount, 2),
                            },
                        )
                    )
            self.env["fix.budget"].create(
                {
                    "name": "Driver plan",
                    "version_id": ver.id,
                    "budget_type": "operating",
                    "line_ids": lines,
                }
            )
        return True


class FixBudgetLine(models.Model):
    """One planned amount: account x period x optional branch / business line
    / cost centre. Actual and variance are read live from the posted GL."""

    _name = "fix.budget.line"
    _description = "Budget Line"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date_from, account_id"

    budget_id = fields.Many2one("fix.budget", required=True, ondelete="cascade", index=True)
    company_id = fields.Many2one(related="budget_id.company_id", store=True, index=True)
    operating_unit_id = fields.Many2one(
        "operating.unit", string="Operating Unit", compute="_compute_ou", store=True
    )
    version_id = fields.Many2one(related="budget_id.version_id", store=True, index=True)
    currency_id = fields.Many2one(related="budget_id.currency_id")
    account_id = fields.Many2one("account.account", string="Account", required=True)
    is_revenue = fields.Boolean(compute="_compute_is_revenue", store=True)
    branch_id = fields.Many2one("fix.branch", string="Branch")
    business_line_id = fields.Many2one("fix.business.line", string="Business Line")
    cost_centre = fields.Char(string="Cost Centre")
    date_from = fields.Date(string="From", required=True)
    date_to = fields.Date(string="To", required=True)
    planned_amount = fields.Monetary(string="Planned", currency_field="currency_id")
    actual_amount = fields.Monetary(
        string="Actual", compute="_compute_actual", currency_field="currency_id"
    )
    variance = fields.Monetary(
        string="Variance (favourable +)", compute="_compute_actual", currency_field="currency_id"
    )

    @api.depends("branch_id")
    def _compute_ou(self) -> None:
        for line in self:
            line.operating_unit_id = line.branch_id.operating_unit_id

    @api.depends("account_id.account_type")
    def _compute_is_revenue(self) -> None:
        for line in self:
            line.is_revenue = line.account_id.account_type in ("income", "income_other")

    def _compute_actual(self) -> None:
        actuals = self.env["fix.fpa.engine"].line_actuals(self.filtered("id"))
        for line in self:
            actual = actuals.get(line.id, 0.0)
            line.actual_amount = actual
            line.variance = (
                actual - line.planned_amount if line.is_revenue else line.planned_amount - actual
            )

    @api.constrains("date_from", "date_to", "budget_id")
    def _check_period(self) -> None:
        for line in self:
            if line.date_from > line.date_to:
                raise ValidationError("A budget line ends before it starts")
            budget = line.budget_id
            if budget.date_from and (
                line.date_from < budget.date_from or line.date_to > budget.date_to
            ):
                raise ValidationError(
                    "Budget line %s - %s lies outside budget %s (%s - %s)"
                    % (line.date_from, line.date_to, budget.name, budget.date_from, budget.date_to)
                )

    @api.model_create_multi
    def create(self, vals_list):
        budgets = self.env["fix.budget"].browse([v.get("budget_id") for v in vals_list])
        budgets.version_id._check_editable()
        return super().create(vals_list)

    def write(self, vals):
        self.version_id._check_editable()
        return super().write(vals)

    def unlink(self):
        self.version_id._check_editable()
        return super().unlink()


class FixFpaDriver(models.Model):
    """A scenario driver: the base value measured from actuals and the value
    the planner sets for the scenario."""

    _name = "fix.fpa.driver"
    _description = "Scenario Driver"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "version_id, driver_key"
    _version_key_unique = models.Constraint(
        "UNIQUE (version_id, driver_key)", "Each driver appears once per version"
    )

    version_id = fields.Many2one(
        "fix.budget.version", required=True, ondelete="cascade", index=True
    )
    company_id = fields.Many2one(related="version_id.company_id", store=True, index=True)
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    driver_key = fields.Selection(DRIVER_KEYS, string="Driver", required=True)
    base_value = fields.Float(string="Base (Actuals)", digits=(16, 4), readonly=True)
    scenario_value = fields.Float(string="Scenario Value", digits=(16, 4))
    scenario_value_set = fields.Boolean(
        compute="_compute_change", store=True, string="Changed By Planner"
    )
    change_pct = fields.Float(compute="_compute_change", store=True, string="Change %")

    def _fix_guarded_fields(self) -> set:
        # Measured from the actuals by Load Drivers, never typed: the workspace
        # grid posts it back with the row, unchanged (M54-2).
        return super()._fix_guarded_fields() | {"base_value"}

    @api.depends("base_value", "scenario_value")
    def _compute_change(self) -> None:
        for drv in self:
            drv.scenario_value_set = round(drv.scenario_value, 4) != round(drv.base_value, 4)
            drv.change_pct = (
                round(100.0 * (drv.scenario_value - drv.base_value) / drv.base_value, 2)
                if drv.base_value
                else 0.0
            )

    @api.constrains("scenario_value")
    def _check_value(self) -> None:
        for drv in self:
            if drv.scenario_value < 0:
                raise ValidationError("A driver value cannot be negative")

    def write(self, vals):
        self.version_id._check_editable()
        return super().write(vals)
