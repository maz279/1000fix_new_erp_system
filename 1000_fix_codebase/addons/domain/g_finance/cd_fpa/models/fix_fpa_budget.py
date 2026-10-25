# fix_fpa_budget — M54 budget versions (draft -> submitted -> approved with
# segregation of duties), budget lines measured against the posted GL, and
# driver-based scenario / forecast versions.
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


class FixBudgetVersion(models.Model):
    """A budget / forecast / scenario version. Budgets and lines are editable
    only while the version is draft; approval needs a Finance Manager who
    did not submit it (segregation of duties). Approving a budget or
    forecast version supersedes the earlier approved one of the same year."""

    _name = "fix.budget.version"
    _description = "Budget Version"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date_from desc, id desc"

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

    @api.constrains("date_from", "date_to")
    def _check_window(self) -> None:
        for ver in self:
            if ver.date_from > ver.date_to:
                raise ValidationError("Version %s ends before it starts" % ver.name)

    # ------------------------------------------------------------ workflow

    def _check_editable(self) -> None:
        for ver in self:
            if ver.state != "draft":
                raise UserError(
                    "Version %s is %s — only a draft version can be changed; reject or copy it"
                    % (ver.name, dict(VERSION_STATES)[ver.state].lower())
                )

    def write(self, vals):
        locked = set(vals) - {
            "state",
            "submitted_by",
            "submitted_at",
            "approved_by",
            "approved_at",
            "rejection_reason",
            "message_main_attachment_id",
        }
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

    def action_submit(self):
        self._require_group(USER_GROUP, "Submitting a budget version")
        for ver in self:
            if ver.state != "draft":
                raise UserError("Only a draft version can be submitted")
            if not ver.budget_ids.line_ids:
                raise UserError("Version %s has no budget lines to submit" % ver.name)
            ver.write(
                {
                    "state": "submitted",
                    "submitted_by": self.env.uid,
                    "submitted_at": fields.Datetime.now(),
                    "rejection_reason": False,
                }
            )
        return True

    def action_approve(self):
        self._require_group(MANAGER_GROUP, "Approving a budget version")
        for ver in self:
            if ver.state != "submitted":
                raise UserError("Only a submitted version can be approved")
            if ver.submitted_by == self.env.user:
                raise UserError(
                    "Segregation of duties: %s submitted version %s and cannot approve it"
                    % (self.env.user.name, ver.name)
                )
            if ver.version_type in ("budget", "forecast"):
                self.search(
                    [
                        ("id", "!=", ver.id),
                        ("company_id", "=", ver.company_id.id),
                        ("version_type", "=", ver.version_type),
                        ("fiscal_year", "=", ver.fiscal_year),
                        ("state", "=", "approved"),
                    ]
                ).write({"state": "superseded"})
            ver.write(
                {
                    "state": "approved",
                    "approved_by": self.env.uid,
                    "approved_at": fields.Datetime.now(),
                }
            )
        return True

    def action_reject(self):
        self._require_group(MANAGER_GROUP, "Rejecting a budget version")
        for ver in self:
            if ver.state != "submitted":
                raise UserError("Only a submitted version can be rejected")
            if not ver.rejection_reason:
                raise UserError(
                    "Write the rejection reason on version %s (open the record) first" % ver.name
                )
            ver.write({"state": "rejected"})
        return True

    def action_reset_draft(self):
        self._require_group(USER_GROUP, "Re-opening a budget version")
        for ver in self:
            if ver.state != "rejected":
                raise UserError("Only a rejected version returns to draft")
            ver.write({"state": "draft", "submitted_by": False, "submitted_at": False})
        return True

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
                    drv.write(
                        {
                            "base_value": value,
                            "scenario_value": drv.scenario_value
                            if drv.scenario_value_set
                            else value,
                        }
                    )
                else:
                    self.env["fix.fpa.driver"].create(
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
    _inherit = ["mail.thread", "mail.activity.mixin"]
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
