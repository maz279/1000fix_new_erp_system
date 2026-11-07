# fix_ppm — M67: project, program, portfolio management (P10-M05 / R08-M03).
#
# A12 workflow audit (2026-11-04) P1-3 / M67-3 / M67-4 / M67-5 / M67-6:
# every state on these models was a plain write, a project went active with
# no budget approval and a failed G1 behind it, and the PM completed and
# billed his own milestones with nothing recorded. Now:
#   - fix.project routes its BUDGET through M63 + DOFA (fix.dofa.mixin):
#     activation needs a value-based approval, the approved budget is
#     baselined and cannot be raised above the baseline without a new
#     approval (BRU-PPM-03/04/05/07);
#   - action_activate refuses when any gate failed and requires the G1 gate
#     closed pass/conditional when the project has one;
#   - states are guarded (fix.guarded.mixin) — they change only through the
#     actions below, from the state the lifecycle allows;
#   - a milestone completes only with tasks done AND an acceptance recorded
#     by someone who is not the project manager (BRU-PPM-11);
#   - tasks and billing lines may not point at another project's milestone.
#
# A12 finish build (2026-11-07), findings F1-F3, F8, F11-F13, F17-F19:
#   - a raise after draft is never a field edit, even from a zero or missing
#     baseline: it goes through Requested Budget and a new DOFA approval, which
#     re-baselines the project when granted (BRU-PPM-07);
#   - the contract value, type, currency and manager freeze at activation; the
#     billing ceiling falls back to the baseline when no contract is recorded;
#   - activation needs a manager, the contract value where the project type
#     requires one, and G1 and G2 closed with a pass. The latest decision per
#     gate wins, so a failed gate can be re-reviewed. A failed gate blocks
#     completion as well as activation;
#   - completion needs at least one milestone, Finance's confirmation that all
#     billing is posted, and a sponsor who is not the project's manager;
#   - actual cost is measured (project-tagged GL postings, task hours x a rate
#     parameter), never typed. With neither, the project says "not measured".
from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError

from libs.py.fix_events import publish

# Budget bands for the DOFA ladder (business decision, report §7 "05-04 §7
# authority matrix"). Same ladder as the estate cost decisions
# (cd_facility ESTATE_COST_DOFA_THRESHOLDS): Tier 2 up to BDT 250,000,
# Tier 3 up to 1,000,000, Tier 4 (CFO) above. An unbudgeted project is
# Tier 0 and needs no DOFA approval.
PROJECT_BUDGET_DOFA_THRESHOLDS = [
    (0.0, "tier_0"),
    (250000.0, "tier_2"),
    (1000000.0, "tier_3"),
    (float("inf"), "tier_4"),
]

SPONSOR_GROUP = "cd_ppm.group_ppm_sponsor"
PM_GROUP = "cd_ppm.group_ppm_project_manager"
FINANCE_GROUP = "account.group_account_invoice"

# Business defaults, configurable (report B8). Comma-separated values.
CONTRACT_TYPES_PARAM = "fix_ppm.contract_value_required_types"
CONTRACT_TYPES_DEFAULT = "client"
ACTIVATION_GATES_PARAM = "fix_ppm.activation_required_gates"
ACTIVATION_GATES_DEFAULT = "g1_initiation,g2_planning"
# The internal cost of one task hour, in the project's currency. Unset means
# hours are not costed: the rate is a finance decision and is never assumed.
COST_RATE_PARAM = "fix_ppm.cost_rate_per_hour"
COST_ACCOUNT_TYPES = ("expense", "expense_depreciation", "expense_direct_cost")


def ppm_convert(env, amount, from_currency, to_currency, company, date):
    """`amount` in `to_currency` at the company's rate, never a raw comparison.

    Odoo's converter reads a currency with no rate row as 1.0, which would pass
    USD 250,000 under a BDT 300,000 ceiling. A missing rate is refused instead."""
    if from_currency == to_currency:
        return amount
    Rate = env["res.currency.rate"].sudo()
    for currency in (from_currency, to_currency):
        if currency == company.currency_id:
            continue
        if not Rate.search_count(
            [
                ("currency_id", "=", currency.id),
                ("name", "<=", date),
                ("company_id", "in", (company.id, False)),
            ],
            limit=1,
        ):
            raise UserError(
                "No exchange rate is recorded for %s on %s: Finance records the rate before "
                "this amount can be compared with the project's ceiling." % (currency.name, date)
            )
    return from_currency._convert(amount, to_currency, company, date)


class FixProject(models.Model):
    _name = "fix.project"
    _description = "Project"
    # fix.dofa.mixin brings fix.approvable.mixin and fix.guarded.mixin; the
    # DOFA stamp is applied by the M63 engine in the approver's inbox.
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.dofa.mixin"]
    _order = "date_start desc"

    # M63 routing: the record's own DOFA approve method applies the stamp.
    _approval_domain = "other"
    _approval_routed = True

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True)
    code = fields.Char(string="Project Code", readonly=True, copy=False)
    project_type = fields.Selection(
        [
            ("internal", "Internal"),
            ("client", "Client Project"),
            ("infrastructure", "Infrastructure"),
        ],
        required=True,
        default="internal",
    )
    manager_id = fields.Many2one("hr.employee", string="Project Manager")
    date_start = fields.Date()
    date_end = fields.Date()
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    budget = fields.Monetary(string="Budget", currency_field="currency_id")
    budget_requested = fields.Monetary(
        string="Requested Budget",
        currency_field="currency_id",
        copy=False,
        help="An overrun on a running project: the new budget this project asks for. "
        "Request Budget Approval routes it at its own DOFA tier; when granted it "
        "becomes the budget and the new baseline (BRU-PPM-07).",
    )
    # M67-2: the billing ceiling. Zero means "no contract value recorded": the
    # ceiling then falls back to the baselined budget, so it is never open.
    contract_value = fields.Monetary(
        string="Contract Value",
        currency_field="currency_id",
        help="The approved contract/billing ceiling: billing of this project may not "
        "exceed it. Frozen at activation; with no contract value the baselined budget "
        "is the ceiling.",
    )
    contract_value_requested = fields.Monetary(
        string="Requested Contract Value",
        currency_field="currency_id",
        copy=False,
        help="A contract variation on a running project. Routed with Request Budget "
        "Approval; when granted it becomes the contract value.",
    )
    baseline_budget = fields.Monetary(
        string="Baselined Budget",
        currency_field="currency_id",
        readonly=True,
        copy=False,
        help="The budget as approved when the project was activated. Raising the "
        "budget above the baseline needs a new DOFA approval (BRU-PPM-05/07).",
    )
    # BRU-PPM-12: measured, never typed. Not stored: the hourly rate is a
    # parameter and the GL postings live in another module.
    actual_cost = fields.Monetary(
        string="Actual Cost",
        currency_field="currency_id",
        compute="_compute_cost",
        help="Project-tagged expense postings in the ledger plus task hours at the "
        "configured rate. Zero with Cost Basis 'Not measured' means nothing real was "
        "available to measure, not that the project cost nothing.",
    )
    cost_measured = fields.Boolean(string="Cost Measured", compute="_compute_cost")
    cost_basis = fields.Char(string="Cost Basis", compute="_compute_cost")
    budget_variance = fields.Monetary(
        compute="_compute_variance",
        string="Budget Variance",
        currency_field="currency_id",
    )
    variance_pct = fields.Float(compute="_compute_variance", string="Variance %")
    billed_revenue = fields.Monetary(
        string="Billed Revenue",
        currency_field="currency_id",
        compute="_compute_billed",
        help="Posted customer invoices of this project, net of retention.",
    )
    retention_held = fields.Monetary(
        string="Retention Held",
        currency_field="currency_id",
        compute="_compute_billed",
        help="Deducted from the posted invoices and not billed yet.",
    )
    billing_confirmed_by_id = fields.Many2one(
        "res.users", string="Billing Confirmed By", readonly=True, copy=False, tracking=True
    )
    billing_confirmed_on = fields.Datetime(string="Billing Confirmed On", readonly=True, copy=False)
    billing_confirmed_amount = fields.Monetary(
        string="Billing Confirmed Amount",
        currency_field="currency_id",
        readonly=True,
        copy=False,
        help="What Finance confirmed as posted. Billing that moves afterwards needs a "
        "new confirmation.",
    )
    closed_by_id = fields.Many2one(
        "res.users", string="Closed By", readonly=True, copy=False, tracking=True
    )
    closed_on = fields.Datetime(string="Closed On", readonly=True, copy=False)
    progress_pct = fields.Float(string="Progress %", default=0.0)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("active", "Active"),
            ("on_hold", "On Hold"),
            ("completed", "Completed"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )
    template_id = fields.Many2one(
        "fix.project.template",
        string="Created From Template",
        readonly=True,
        copy=False,
        help="M67-10/BRU-PPM-19: the template the project was instantiated from.",
    )
    template_version = fields.Char(readonly=True, copy=False)
    milestone_ids = fields.One2many("fix.project.milestone", "project_id", string="Milestones")
    task_ids = fields.One2many("fix.project.task", "project_id", string="Tasks")
    billing_ids = fields.One2many("fix.project.billing", "project_id", string="Billing Lines")
    # NOTE: gate_ids (fix.project.gate reverse relation) is declared in
    # cd_itsm/models/fix_itsm_ops.py, next to the gate model: cd_itsm depends
    # on cd_ppm (the gate's project_id), so this module cannot reference
    # fix.project.gate at load time. The field resolves by name, so
    # self.gate_ids below works unchanged.

    # ---- guarded workflow fields (M67-5) ---------------------------------
    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "baseline_budget",
            "billing_confirmed_by_id",
            "billing_confirmed_on",
            "billing_confirmed_amount",
            "closed_by_id",
            "closed_on",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and self.state != "draft":
            # BRU-PPM-05: once delivery starts the baseline, the contract and
            # the manager the gates were reviewed against are frozen. A blank
            # manager on a legacy project stays open so it can be named once.
            locked |= {"baseline_budget", "contract_value", "currency_id", "project_type"}
            if self.manager_id:
                locked.add("manager_id")
        if not self or self.state == "draft":
            locked |= {"budget_requested", "contract_value_requested"}
        if self and self.approval_state in ("pending", "approved"):
            locked.add("dofa_justification")
        return locked

    # ---- DOFA / M63 hooks (P1-3) ------------------------------------------
    def _dofa_amount(self) -> float:
        """The figure a decision covers. On a running project that is whichever
        is highest of the budget, the requested budget and the requested contract
        value, so an overrun routes at the tier of the amount it asks for."""
        self.ensure_one()
        if self.state in ("active", "on_hold"):
            return max(
                self.budget or 0.0,
                self.budget_requested or 0.0,
                self.contract_value_requested or 0.0,
            )
        return self.budget or 0.0

    def _dofa_thresholds(self):
        return PROJECT_BUDGET_DOFA_THRESHOLDS

    def _dofa_amount_label(self) -> str:
        self.ensure_one()
        return "BDT %.2f (project budget)" % self._dofa_amount()

    @api.depends("budget", "budget_requested", "contract_value_requested", "state")
    def _compute_dofa_tier_required(self):
        return super()._compute_dofa_tier_required()

    def _approval_excluded(self):
        # §13 SoD: the project manager never approves the budget they will
        # spend (BRU-PPM-04). The engine already excludes requester/creator.
        excluded = super()._approval_excluded()
        if self.manager_id:
            excluded |= self.manager_id.sudo().user_id
        return excluded.sudo()

    def _approval_pinned_fields(self) -> set:
        # The approval covers the budget AND who runs the project. Granting a
        # contract variation writes contract_value through the guard: that
        # write is the approval taking effect, so it must not void itself.
        pinned = super()._approval_pinned_fields() | {"manager_id", "contract_value"}
        if self._fix_guard_has_token():
            pinned.discard("contract_value")
        return pinned

    # ---- computed ----------------------------------------------------------
    @api.depends("task_ids.actual_hours")
    def _compute_cost(self):
        raw_rate = self.env["ir.config_parameter"].sudo().get_param(COST_RATE_PARAM)
        try:
            rate = float(raw_rate) if raw_rate else 0.0
        except (TypeError, ValueError):
            rate = 0.0
        for rec in self:
            hours = sum(rec.sudo().task_ids.mapped("actual_hours"))
            labour = hours * rate if rate > 0 else 0.0
            ledger = rec._ppm_ledger_cost()
            basis = []
            if ledger is not None:
                basis.append("Ledger postings tagged %s" % rec.code)
            if labour:
                basis.append("%.1f task hours x %.2f" % (hours, rate))
            rec.actual_cost = labour + (ledger or 0.0)
            rec.cost_measured = bool(basis)
            rec.cost_basis = " + ".join(basis) or "Not measured"

    def _ppm_ledger_cost(self):
        """Posted expense lines carrying this project in the M19 project
        dimension, in the project's currency. None when no such posting exists,
        or when it cannot be converted: unknown is not the same as zero."""
        self.ensure_one()
        if not self.id or not self.code:
            return None
        dimensions = (
            self.env["fix.journal.dimension"]
            .sudo()
            .search([("project_ref", "=", self.code), ("company_id", "=", self.company_id.id)])
        )
        lines = dimensions.mapped("move_line_id").filtered(
            lambda line: line.parent_state == "posted"
            and line.account_id.account_type in COST_ACCOUNT_TYPES
        )
        if not lines:
            return None
        try:
            return ppm_convert(
                self.env,
                sum(lines.mapped("balance")),
                self.company_id.currency_id,
                self.currency_id,
                self.company_id,
                fields.Date.context_today(self),
            )
        except UserError:
            return None

    @api.depends("budget", "actual_cost", "cost_measured")
    def _compute_variance(self):
        for rec in self:
            if not rec.cost_measured:
                # Variance against a cost nobody measured would read as savings.
                rec.budget_variance = 0.0
                rec.variance_pct = 0.0
                continue
            rec.budget_variance = (rec.budget or 0.0) - (rec.actual_cost or 0.0)
            rec.variance_pct = ((rec.budget_variance / rec.budget) * 100.0) if rec.budget else 0.0

    @api.depends("billing_ids.state", "billing_ids.amount", "billing_ids.retention_pct")
    def _compute_billed(self):
        for rec in self:
            billed = held = 0.0
            lines = rec.sudo().billing_ids.filtered(lambda b: b.state in ("invoiced", "paid"))
            for line in lines:
                try:
                    billed += line._amount_in_project_currency(line.net_amount)
                    held += line._amount_in_project_currency(line.retention_amount)
                except UserError:
                    continue
            rec.billed_revenue = billed
            rec.retention_held = held

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals["code"] = self.env["ir.sequence"].next_by_code("fix.project") or "PRJ/New"
        recs = super().create(vals_list)
        for rec in recs:
            publish(
                self.env,
                "project.created",
                "fix.project",
                rec.id,
                {"name": rec.name, "type": rec.project_type},
            )
        return recs

    def _ppm_refuse_frozen_change(self, vals):
        """F2, F8, F11: what freezes when delivery starts, at the ORM and not only
        on the form. The P03 form posts every field it shows, so an unchanged
        value passes and only a change is refused."""
        self.ensure_one()
        changed = {
            name
            for name in vals
            if name in self._fields and self._fix_guard_differs(name, vals[name], self[name])
        }
        requested = changed & {"budget_requested", "contract_value_requested"}
        if requested and self.state not in ("active", "on_hold"):
            raise UserError(
                "A requested budget or contract value is an overrun on a running project. A "
                "draft project's budget is set on Budget itself; a closed project takes no new "
                "request."
            )
        if "dofa_justification" in changed and self.approval_state in ("pending", "approved"):
            raise UserError(
                "The justification of %s is what the approver read. It cannot be rewritten "
                "while the approval stands." % self.display_name
            )
        if self.state == "draft":
            return
        if "manager_id" in changed and self.manager_id:
            raise UserError(
                "The manager of %s is frozen since it was activated: the approval and the gate "
                "reviews were given against this manager (BRU-PPM-05)." % self.display_name
            )
        frozen = changed & {"contract_value", "currency_id", "project_type"}
        if frozen:
            raise UserError(
                "%s of %s is frozen at activation. A contract variation goes through Requested "
                "Contract Value and a new approval."
                % (", ".join(self._fields[n].string for n in sorted(frozen)), self.display_name)
            )
        if "budget" in changed:
            # BRU-PPM-05/07 (M67-4, pj_09, F2): a zero or missing baseline is not
            # an open budget. Lowering is always allowed.
            new = vals["budget"] or 0.0
            baseline = self.baseline_budget or 0.0
            if new > self.budget + 0.005 and new > baseline + 0.005:
                raise UserError(
                    "The budget of %s was baselined at BDT %.2f. Raising it above the baseline "
                    "is an overrun that needs a new approval: enter it in Requested Budget and "
                    "use Request Budget Approval." % (self.display_name, baseline)
                )

    def _ppm_refuse_ceiling_below_billing(self, vals):
        """F15: the ceiling cannot be lowered below what is already billed. Only
        an actual lowering is checked, so a legacy project that is already over
        its ceiling can still save its other fields."""
        for rec in self:
            ceiling = rec._billing_ceiling(
                contract=vals.get("contract_value", rec.contract_value),
                budget=vals.get("budget", rec.budget),
            )
            if ceiling >= rec._billing_ceiling() - 0.005:
                continue
            committed = rec._billing_committed()
            if committed > ceiling + 0.005:
                raise ValidationError(
                    "%s already carries BDT %.2f of billing: its ceiling cannot drop to BDT %.2f. "
                    "Cancel the lines first." % (rec.display_name, committed, ceiling)
                )

    def write(self, vals):
        if self and not self._fix_guard_open():
            for rec in self:
                rec._ppm_refuse_frozen_change(vals)
            if {"contract_value", "budget"} & set(vals):
                self._ppm_refuse_ceiling_below_billing(vals)
        return super().write(vals)

    @api.constrains("manager_id")
    def _check_manager_is_not_a_reviewer(self):
        # F12: the gate's own constraint only fires on the gate. Naming a gate's
        # reviewer as manager afterwards made the review a self-review.
        for rec in self.filtered("manager_id"):
            clash = rec.sudo().gate_ids.filtered(lambda g, m=rec.manager_id: g.reviewer_id == m)
            if clash:
                raise ValidationError(
                    "%s reviews gate %s of this project and cannot also manage it: gate review "
                    "is independent (M67-6)."
                    % (rec.manager_id.display_name, ", ".join(clash.mapped("name")))
                )

    # ---- who ---------------------------------------------------------------
    def _ppm_delivery_users(self):
        """Who delivers this project and so may not judge it: its manager, and
        whoever raised it while no manager is named."""
        self.ensure_one()
        record = self.sudo()
        return record.manager_id.user_id or record.create_uid

    def _ppm_assert_sponsor(self, what):
        """A sponsor who is not delivering this project. Superuser code is trusted."""
        if self.env.su:
            return
        for rec in self:
            if self.env.user in rec._ppm_delivery_users():
                raise UserError(
                    "Segregation of duties: %s is not for the manager of %s."
                    % (what, rec.display_name)
                )
        if not self.env.user.has_group(SPONSOR_GROUP):
            raise AccessError("%s needs the Project Sponsor role, which you do not hold." % what)

    # ---- billing ceiling ---------------------------------------------------
    def _billing_ceiling(self, contract=None, budget=None):
        """F8: the contract value, else the baselined budget, else the budget.
        Never open: 'checked by the DOFA approval instead' was not true, because
        DOFA looks at the budget and never at billing."""
        self.ensure_one()
        contract = self.contract_value if contract is None else contract
        budget = self.budget if budget is None else budget
        return contract or self.baseline_budget or budget or 0.0

    def _billing_committed(self):
        """Every line not cancelled, net of retention, in the project's currency.
        A search, not the one2many: during a create the inverse cache may not
        carry the line being validated yet."""
        self.ensure_one()
        lines = (
            self.env["fix.project.billing"]
            .sudo()
            .search([("project_id", "=", self.id), ("state", "!=", "cancelled")])
        )
        return sum(line._amount_in_project_currency(line.net_amount) for line in lines)

    # ---- gates (F12) -------------------------------------------------------
    def _latest_gate_decisions(self):
        """{gate kind: its latest review that carries a decision}. A re-review
        supersedes the earlier verdict; a later review still undecided does not."""
        self.ensure_one()
        latest = {}
        for gate in self.sudo().gate_ids.filtered("decision").sorted("id"):
            latest[gate.gate] = gate
        return latest

    def _gates_refuse_failure(self, what):
        failed = [g for g in self._latest_gate_decisions().values() if g.decision == "fail"]
        if failed:
            raise UserError(
                "Gate %s of this project closed as FAIL: a failed stage gate blocks %s until a "
                "re-review passes it (BRU-PPM-16)." % (", ".join(g.name for g in failed), what)
            )

    @api.model
    def _ppm_param_list(self, key, default):
        """A comma-separated parameter. Unset takes the default; 'none' empties it."""
        value = self.env["ir.config_parameter"].sudo().get_param(key)
        if value is False or value is None:
            value = default
        items = [item.strip() for item in value.split(",")]
        return [item for item in items if item and item != "none"]

    # ---- lifecycle (M67-5: every transition checks its from-state) --------
    def _gate_entry_ready(self):
        """A failed gate blocks delivery; the required gates must have passed."""
        self.ensure_one()
        self._gates_refuse_failure("the next phase")
        latest = self._latest_gate_decisions()
        labels = dict(self.env["fix.project.gate"]._fields["gate"].selection)
        for key in self._ppm_param_list(ACTIVATION_GATES_PARAM, ACTIVATION_GATES_DEFAULT):
            gate = latest.get(key)
            if not gate or gate.state != "closed" or gate.decision not in ("pass", "conditional"):
                raise UserError(
                    "Gate %s is not closed with a pass/conditional pass: activate the project "
                    "after this gate (BRU-PPM-03)." % labels.get(key, key)
                )
        return True

    def action_request_approval(self, justification=None):
        """A draft project's budget, or on a running project an overrun, a contract
        variation, or the approval a legacy project never had."""
        for rec in self:
            if rec.state in ("active", "on_hold"):
                overrun = (rec.budget_requested or 0.0) > (rec.baseline_budget or 0.0) + 0.005
                variation = (rec.contract_value_requested or 0.0) > (rec.contract_value or 0.0)
                legacy = (rec.budget or 0.0) > 0.0 and not rec.baseline_budget
                if not (overrun or variation or legacy):
                    raise UserError(
                        "%s runs on its approved baseline. Enter the new figure in Requested "
                        "Budget or Requested Contract Value first." % rec.display_name
                    )
            elif rec.state != "draft":
                raise UserError("A %s project takes no budget approval." % rec.state)
            # F1: the approver is refused without a justification, so the request
            # stops here instead of reaching an inbox where it can never be approved.
            # One typed on the form counts, and travels with the request as if the
            # button had prompted for it: the approver reads it on the request.
            stated = (justification or "").strip() or rec.dofa_justification or None
            if (
                rec._dofa_tier_rank(rec._dofa_current_tier()) >= rec._dofa_tier_rank("tier_2")
                and not (stated or "").strip()
            ):
                raise UserError(
                    "State why %s needs this budget: the approver cannot sign it off without a "
                    "written justification." % rec.display_name
                )
            # Guard token: this replaces the justification of an earlier round.
            super(FixProject, rec._guarded()).action_request_approval(justification=stated)
        return True

    def action_dofa_approve(self):
        """Granting a running project's request applies it: the new baseline."""
        result = super().action_dofa_approve()
        for rec in self.filtered(lambda r: r.state in ("active", "on_hold")):
            budget = max(rec.budget or 0.0, rec.budget_requested or 0.0)
            vals = {"budget": budget, "baseline_budget": budget, "budget_requested": 0.0}
            if rec.contract_value_requested:
                vals.update(
                    {
                        "contract_value": rec.contract_value_requested,
                        "contract_value_requested": 0.0,
                    }
                )
            rec._guarded().write(vals)
            rec.message_post(
                body="Budget baselined at BDT %.2f on approval by %s."
                % (budget, self.env.user.name)
            )
        return result

    def action_activate(self):
        """Delivery starts only with an approved budget and a passing gate."""
        required_types = self._ppm_param_list(CONTRACT_TYPES_PARAM, CONTRACT_TYPES_DEFAULT)
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only a draft project can be activated.")
            rec._dofa_assert_approved("Activation of project %s" % rec.display_name)
            if not rec.manager_id:
                raise UserError(
                    "Name the project manager of %s before it is activated: approvals and gate "
                    "reviews are independent of that person." % rec.display_name
                )
            if rec.project_type in required_types and not rec.contract_value:
                raise UserError(
                    "Record the contract value of %s before it is activated: it is the billing "
                    "ceiling of a %s project."
                    % (
                        rec.display_name,
                        dict(rec._fields["project_type"].selection)[rec.project_type],
                    )
                )
            rec._gate_entry_ready()
            rec._guarded().write(
                {
                    "state": "active",
                    "baseline_budget": rec.budget,
                    "date_start": rec.date_start or fields.Date.context_today(rec),
                }
            )
            rec.message_post(
                body="Project activated. Budget baselined at BDT %.2f under %s."
                % (rec.baseline_budget, rec.dofa_approved_tier or "no DOFA tier")
            )

    def action_hold(self):
        for rec in self:
            if rec.state != "active":
                raise UserError("Only an active project can be put on hold.")
            rec._guarded().write({"state": "on_hold"})

    def action_resume(self):
        for rec in self:
            if rec.state != "on_hold":
                raise UserError("Only a project on hold can be resumed.")
            if rec.budget and not rec.baseline_budget:
                raise UserError(
                    "%s has no approved baseline. Request its budget approval before it resumes."
                    % rec.display_name
                )
            rec._gate_entry_ready()
            rec._guarded().write({"state": "active"})

    def action_cancel(self):
        for rec in self:
            if rec.state in ("completed", "cancelled"):
                raise UserError("This project is already %s." % rec.state)
            rec._guarded().write({"state": "cancelled"})

    def _ppm_closing_billing_checks(self):
        """BRU-PPM-13: nothing left to raise, and what was raised is posted."""
        self.ensure_one()
        unbilled = self.sudo().billing_ids.filtered(lambda b: b.state in ("planned", "ready"))
        if unbilled:
            raise UserError(
                "%d billing line(s) are not invoiced yet: raise or cancel them "
                "before closing the project (BRU-PPM-13)." % len(unbilled)
            )

    def action_confirm_billing(self):
        """F18: Finance confirms that everything billed on this project is posted."""
        if not self.env.su and not self.env.user.has_group(FINANCE_GROUP):
            raise AccessError("Finance confirms the project's billing: you hold no invoicing role.")
        self.check_access("read")
        for rec in self:
            if rec.state != "active":
                raise UserError("Only an active project's billing is confirmed for closure.")
            if not self.env.su and self.env.user in rec._ppm_delivery_users():
                raise UserError(
                    "Segregation of duties: the manager of %s does not confirm its billing."
                    % rec.display_name
                )
            rec._ppm_closing_billing_checks()
            rec.sudo()._guarded().write(
                {
                    "billing_confirmed_by_id": self.env.user.id,
                    "billing_confirmed_on": fields.Datetime.now(),
                    "billing_confirmed_amount": rec._billing_committed(),
                }
            )
            rec.sudo().message_post(
                body="Billing confirmed as posted by %s: BDT %.2f."
                % (self.env.user.name, rec.billing_confirmed_amount)
            )

    def action_complete(self):
        """F18: a sponsor closes the project; the manager does not close his own."""
        self._ppm_assert_sponsor("Closing a project")
        for rec in self:
            if rec.state != "active":
                raise UserError("Only an active project can be completed.")
            if not rec.milestone_ids:
                raise UserError(
                    "%s has no milestones: nothing was delivered and accepted, so it cannot "
                    "complete. Cancel it if the work stopped." % rec.display_name
                )
            open_ms = rec.milestone_ids.filtered(lambda m: m.state != "done")
            if open_ms:
                raise UserError("%d milestone(s) still open" % len(open_ms))
            rec._ppm_closing_billing_checks()
            rec._gates_refuse_failure("project completion")
            lines = rec.sudo().billing_ids.filtered(lambda b: b.state != "cancelled")
            if lines:
                if not rec.billing_confirmed_by_id:
                    raise UserError(
                        "Finance has not confirmed that the billing of %s is posted."
                        % rec.display_name
                    )
                if abs(rec.billing_confirmed_amount - rec._billing_committed()) > 0.005:
                    raise UserError(
                        "The billing of %s moved after Finance confirmed it: Finance confirms "
                        "it again." % rec.display_name
                    )
            rec._guarded().write(
                {
                    "state": "completed",
                    "closed_by_id": self.env.user.id,
                    "closed_on": fields.Datetime.now(),
                }
            )
            publish(self.env, "project.completed", "fix.project", rec.id, {"name": rec.name})

    # ---- event consumers (A12 P2 hand-offs; FF-48) -------------------------
    # Registered in data/fix_a12_event_consumers.xml. The relay calls them as
    # superuser with the event dict; they must stay idempotent.
    @api.model
    def consume_project_created(self, event):
        """project.created: keep the project's own trail of its hand-off."""
        project = self.browse(event.get("aggregate_id") or 0).exists()
        if project:
            project.message_post(
                body="Project creation handed to downstream consumers (event %s)."
                % event.get("event_id")
            )
        return True

    @api.model
    def consume_project_completed(self, event):
        """project.completed: record the closure hand-off on the project."""
        project = self.browse(event.get("aggregate_id") or 0).exists()
        if project:
            project.message_post(
                body="Project closure handed to downstream consumers (event %s)."
                % event.get("event_id")
            )
        return True


class FixProjectMilestone(models.Model):
    _name = "fix.project.milestone"
    _description = "Project Milestone"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True)
    project_id = fields.Many2one("fix.project", required=True, ondelete="cascade")
    due_date = fields.Date()
    state = fields.Selection(
        [("pending", "Pending"), ("done", "Done")], default="pending", required=True, tracking=True
    )
    overdue = fields.Boolean(
        readonly=True,
        copy=False,
        help="Set by the overdue-milestone cron (M67-11/R3): a pending milestone "
        "past its due date.",
    )
    accepted_by_id = fields.Many2one(
        "res.users", string="Accepted By", readonly=True, copy=False, tracking=True
    )
    accepted_on = fields.Datetime(string="Accepted On", readonly=True, copy=False)
    acceptance_note = fields.Char(
        string="Acceptance Evidence",
        copy=False,
        help="BRU-PPM-11: the evidence reference (client sign-off, UAT report) "
        "for the milestone's acceptance.",
    )
    task_ids = fields.One2many("fix.project.task", "milestone_id", string="Milestone Tasks")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "overdue",
            "accepted_by_id",
            "accepted_on",
            # F17: the acceptance evidence is what was accepted, not a note.
            "acceptance_note",
        }

    def action_accept(self, acceptance_note=None):
        """A sponsor who does not deliver the project accepts the milestone."""
        for rec in self:
            if rec.state != "pending":
                raise UserError("Only a pending milestone can be accepted.")
            if not (acceptance_note or "").strip():
                raise UserError("Record the acceptance evidence (sign-off reference).")
            if not self.env.su:
                project = rec.project_id.sudo()
                if not project.manager_id:
                    raise UserError(
                        "Project %s names no manager, so nobody can show the acceptance is "
                        "independent. Name the project manager first." % project.display_name
                    )
                if project.manager_id.user_id == self.env.user:
                    raise UserError(
                        "Segregation of duties: the project manager cannot accept "
                        "their own milestone (BRU-PPM-11). A project sponsor records "
                        "the acceptance, with the client's sign-off as its evidence."
                    )
                if not self.env.user.has_group(SPONSOR_GROUP):
                    raise AccessError(
                        "Accepting a milestone needs the Project Sponsor role, which you do "
                        "not hold (F17)."
                    )
            rec._guarded().write(
                {
                    "accepted_by_id": self.env.user.id,
                    "accepted_on": fields.Datetime.now(),
                    "acceptance_note": acceptance_note,
                }
            )
            rec.message_post(
                body="Milestone accepted by %s (evidence: %s)."
                % (self.env.user.name, acceptance_note)
            )

    def action_complete(self):
        for rec in self:
            if rec.state != "pending":
                raise UserError("This milestone is already %s." % rec.state)
            if not rec.accepted_by_id:
                raise UserError(
                    "The milestone has no recorded acceptance: the sponsor accepts the "
                    "delivered milestone before it completes (BRU-PPM-11)."
                )
            open_tasks = rec.task_ids.filtered(lambda t: t.state not in ("done", "cancelled"))
            if open_tasks:
                raise UserError("%d task(s) still open in milestone" % len(open_tasks))
            rec._guarded().write({"state": "done"})
            publish(
                self.env,
                "project.milestone_completed",
                "fix.project.milestone",
                rec.id,
                {"milestone": rec.name, "project": rec.project_id.name},
            )

    @api.model
    def cron_flag_overdue_milestones(self):
        """R3/M67-11: flag pending milestones past their due date."""
        today = fields.Date.context_today(self)
        overdue = self.sudo().search(
            [("state", "=", "pending"), ("overdue", "=", False), ("due_date", "<", today)]
        )
        for milestone in overdue:
            milestone.sudo()._guarded().write({"overdue": True})
            milestone.message_post(
                body="Milestone is past its due date %s and still pending." % milestone.due_date
            )
        return True

    @api.model
    def consume_project_milestone_completed(self, event):
        """project.milestone_completed: progress becomes the computed ratio of
        completed milestones (M67-7: computed, not typed)."""
        milestone = self.browse(event.get("aggregate_id") or 0).exists()
        if not milestone or milestone.state != "done":
            return True
        project = milestone.project_id
        total = len(project.milestone_ids)
        done = len(project.milestone_ids.filtered(lambda m: m.state == "done"))
        project.sudo().write({"progress_pct": round(100.0 * done / total, 2) if total else 0.0})
        return True


class FixProjectTask(models.Model):
    _name = "fix.project.task"
    _description = "Project Task"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "id asc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True)
    project_id = fields.Many2one("fix.project", required=True, ondelete="cascade")
    milestone_id = fields.Many2one("fix.project.milestone", string="Milestone", ondelete="set null")
    assigned_to = fields.Many2one("hr.employee", string="Assigned To")
    planned_hours = fields.Float(string="Planned Hours", default=0.0)
    # Hours feed the project's measured cost, so a change leaves a trail.
    actual_hours = fields.Float(string="Actual Hours", default=0.0, tracking=True)
    state = fields.Selection(
        [
            ("todo", "To Do"),
            ("in_progress", "In Progress"),
            ("done", "Done"),
            ("cancelled", "Cancelled"),
        ],
        default="todo",
        required=True,
        tracking=True,
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state"}

    @api.constrains("project_id", "milestone_id")
    def _check_milestone_project(self):
        # M67-6 (ms_05): a task of project A may not link to project B's
        # milestone — the milestone gate would count another project's work.
        for task in self:
            if task.milestone_id and task.milestone_id.project_id != task.project_id:
                raise ValidationError(
                    "The milestone %s belongs to another project: a task may only "
                    "link to a milestone of its own project." % task.milestone_id.display_name
                )

    def _ppm_worker(self):
        """F19: the assignee works his own task, and a project manager any. The
        assignee holds no write on the register, so the transition runs as the
        service role once this check has passed."""
        self.check_access("read")
        if self.env.su:
            return self
        if not self.env.user.has_group(PM_GROUP):
            for rec in self:
                if rec.sudo().assigned_to.user_id != self.env.user:
                    raise AccessError(
                        "Task %s is worked by its assignee or a project manager." % rec.name
                    )
        return self.sudo()

    def action_start(self):
        for rec in self._ppm_worker():
            if rec.state != "todo":
                raise UserError("Only a to-do task can be started.")
            rec._guarded().write({"state": "in_progress"})

    def action_done(self):
        for rec in self._ppm_worker():
            if rec.state not in ("todo", "in_progress"):
                raise UserError("A %s task cannot be marked done." % rec.state)
            rec._guarded().write({"state": "done"})

    def action_cancel(self):
        for rec in self._ppm_worker():
            if rec.state in ("done", "cancelled"):
                raise UserError("This task is already %s." % rec.state)
            rec._guarded().write({"state": "cancelled"})

    def action_log_hours(self, hours=None):
        """The assignee records the hours he worked; they accumulate."""
        try:
            hours = float(hours or 0.0)
        except (TypeError, ValueError):
            hours = 0.0
        if hours <= 0.0:
            raise UserError("Enter the hours worked, as a number above zero.")
        for rec in self._ppm_worker():
            if rec.state in ("done", "cancelled"):
                raise UserError("A %s task takes no more hours." % rec.state)
            rec.write({"actual_hours": rec.actual_hours + hours})
