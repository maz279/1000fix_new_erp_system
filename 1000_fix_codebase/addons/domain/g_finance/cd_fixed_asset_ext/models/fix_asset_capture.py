# fix_asset_capture — the M49 records the sub-module pages had no capture for
# (capture audit 2026-11-17, spec 03_Modules/G_Finance_and_Treasury/M49):
#
#   * fix.capital.project            page 1  FR-FXA-006/007, BRU-FXA-24
#   * fix.cwip.component             page 3  FR-FXA-014/016
#   * fix.asset.depreciation.change  page 4  FR-FXA-023/024, BRU-FXA-10
#   * fix.asset.impairment.assessment page 5 FR-FXA-032, BRU-FXA-26
#   * fix.asset.verification.variance page 7 FR-FXA-030, BRU-FXA-15/16
#
# Every decision is taken by an accounting manager who did not raise the
# document (check_sod); the stamps and derived figures are guarded fields,
# never typed; nothing here is deleted except a component line of an open
# CWIP project.
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from .fix_asset_common import (
    MANAGER_GROUP,
    PIR_DAYS,
    PIR_THRESHOLD,
    USER_GROUP,
    attach_upload,
    attachment_names,
    check_sod,
    float_param,
    money,
    month_start,
    require_group,
)


def _next(env, code):
    return env["ir.sequence"].next_by_code(code) or "/"


# ---------------------------------------------------------------------------
# page 1 — capital project and its post-implementation review
# ---------------------------------------------------------------------------
class FixCapitalProject(models.Model):
    """A capital programme grouping capex requests (a branch opening, a
    workshop build-out) under one budget, schedule and accountable owner, and
    its post-implementation review (FR-FXA-006/007, BRU-FXA-24)."""

    _name = "fix.capital.project"
    _description = "Capital Project"
    _inherit = ["fix.guarded.mixin", "mail.thread", "mail.activity.mixin"]
    _order = "start_date desc, id desc"

    reference = fields.Char(string="Reference", readonly=True, copy=False, default="/")
    name = fields.Char(string="Project", required=True, tracking=True)
    kind = fields.Selection(
        [
            ("branch_opening", "Branch Opening"),
            ("workshop", "Workshop Build-Out"),
            ("it", "IT Programme"),
            ("fleet", "Fleet Programme"),
            ("other", "Other"),
        ],
        string="Project Type",
        required=True,
        default="branch_opening",
        tracking=True,
    )
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Branch", tracking=True)
    currency_id = fields.Many2one(related="company_id.currency_id")
    owner_id = fields.Many2one(
        "res.users",
        string="Accountable Owner",
        required=True,
        default=lambda self: self.env.user,
        tracking=True,
    )
    total_budget = fields.Monetary(string="Total Budget", required=True, tracking=True)
    start_date = fields.Date(string="Start Date", tracking=True)
    target_completion = fields.Date(string="Target Completion", tracking=True)
    business_case = fields.Text(string="Business Case and Expected Benefit")
    request_ids = fields.One2many("fix.capex.request", "project_id", string="Capex Requests")
    committed_amount = fields.Monetary(
        string="Approved Capex", compute="_compute_amounts", help="Approved requests."
    )
    actual_cost = fields.Monetary(string="Actual Cost", compute="_compute_amounts")
    headroom = fields.Monetary(string="Budget Headroom", compute="_compute_amounts")
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("active", "Approved - In Progress"),
            ("completed", "Completed"),
            ("reviewed", "Reviewed"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )
    approved_by_id = fields.Many2one("res.users", string="Approved By", readonly=True, copy=False)
    approved_on = fields.Date(string="Approved On", readonly=True, copy=False)
    actual_completion = fields.Date(string="Actual Completion", readonly=True, copy=False)
    review_required = fields.Boolean(
        string="Review Required",
        compute="_compute_review_required",
        store=True,
        help="BRU-FXA-24: a project whose budget is at or above the review threshold.",
    )
    review_due_date = fields.Date(string="Review Due", readonly=True, copy=False)
    review_overdue = fields.Boolean(string="Review Overdue", compute="_compute_review_overdue")
    # the post-implementation review (fix.capital.project.review in the spec,
    # one per project: held on the project)
    review_actual_cost = fields.Monetary(string="Actual Cost at Review", readonly=True, copy=False)
    review_variance = fields.Monetary(
        string="Variance to Budget (+ over)", readonly=True, copy=False
    )
    benefit_assessment = fields.Text(string="Realised Benefit against the Business Case")
    review_conclusion = fields.Selection(
        [
            ("achieved", "Benefit Achieved"),
            ("partial", "Partly Achieved"),
            ("not_achieved", "Not Achieved"),
        ],
        string="Review Conclusion",
    )
    review_doc_ids = fields.Many2many(
        "ir.attachment",
        "fix_capital_project_review_doc_rel",
        "project_id",
        "attachment_id",
        string="Review Documents",
        copy=False,
    )
    review_file = fields.Binary(
        string="Upload Review Document",
        compute="_compute_review_file",
        inverse="_inverse_review_file",
    )
    review_filename = fields.Char(string="Review File Name", copy=False)
    review_doc_names = fields.Char(string="Review Documents", compute="_compute_review_doc_names")
    reviewed_by_id = fields.Many2one("res.users", string="Reviewed By", readonly=True, copy=False)
    reviewed_on = fields.Date(string="Reviewed On", readonly=True, copy=False)

    _TERMS = ("name", "kind", "company_id", "operating_unit_id", "owner_id", "total_budget")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "reference",
            "approved_by_id",
            "approved_on",
            "actual_completion",
            "review_due_date",
            "review_actual_cost",
            "review_variance",
            "reviewed_by_id",
            "reviewed_on",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and self.state != "draft":
            locked |= set(self._TERMS)
        if self and self.state in ("reviewed", "cancelled"):
            locked |= {"benefit_assessment", "review_conclusion", "review_file"}
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        recs = super().create(vals_list)
        for rec in recs:
            rec._guarded().write({"reference": _next(self.env, "fix.capital.project")})
        return recs

    def write(self, vals):
        if self and not self._fix_guard_open():
            for rec in self:
                moved = [
                    n
                    for n in self._TERMS
                    if n in vals
                    and rec.state != "draft"
                    and rec._fix_guard_differs(n, vals[n], rec[n])
                ]
                if moved:
                    raise UserError(
                        self.env._(
                            "%s is approved: its budget, owner and scope are fixed (%s).",
                            rec.display_name,
                            ", ".join(moved),
                        )
                    )
        return super().write(vals)

    @api.depends("reference", "name")
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = "%s %s" % (rec.reference or "", rec.name or "")

    @api.depends("request_ids.state", "request_ids.amount", "total_budget")
    def _compute_amounts(self):
        for rec in self:
            approved = rec.request_ids.filtered(
                lambda r: r.state in ("approved", "cwip", "capitalised")
            )
            rec.committed_amount = money(sum(approved.mapped("amount")))
            rec.actual_cost = money(sum(rec.request_ids.mapped("actual_cost")))
            rec.headroom = money(rec.total_budget - rec.committed_amount)

    @api.depends("total_budget")
    def _compute_review_required(self):
        threshold = float_param(self.env, PIR_THRESHOLD)
        for rec in self:
            rec.review_required = bool(threshold) and rec.total_budget >= threshold

    def _compute_review_overdue(self):
        today = fields.Date.context_today(self)
        for rec in self:
            rec.review_overdue = bool(
                rec.state == "completed"
                and rec.review_required
                and rec.review_due_date
                and rec.review_due_date < today
            )

    def _compute_review_file(self):
        for rec in self:
            rec.review_file = False

    def _inverse_review_file(self):
        for rec in self:
            attach_upload(
                rec,
                "review_doc_ids",
                rec.review_file,
                rec.review_filename,
                "Post-implementation review %s" % rec.reference,
            )

    @api.depends("review_doc_ids")
    def _compute_review_doc_names(self):
        for rec in self:
            rec.review_doc_names = attachment_names(rec.review_doc_ids)

    @api.constrains("total_budget", "name")
    def _check_budget(self):
        for rec in self:
            if rec.total_budget <= 0:
                raise ValidationError(self.env._("A capital project needs a budget above zero."))
            if rec.target_completion and rec.start_date and rec.target_completion < rec.start_date:
                raise ValidationError(self.env._("The target completion is before the start."))

    # ---- workflow --------------------------------------------------------
    def action_approve(self):
        """Approve the project (an accounting manager who did not raise it)."""
        require_group(self.env, MANAGER_GROUP, "Approving a capital project")
        for rec in self:
            if rec.state != "draft":
                raise UserError(self.env._("Only a draft project is approved."))
            check_sod(self.env, rec.owner_id, rec.display_name, rec)
            rec._guarded().write(
                {
                    "state": "active",
                    "approved_by_id": self.env.uid,
                    "approved_on": fields.Date.context_today(rec),
                }
            )
        return True

    def action_complete(self):
        """Record the completion; a project at or above the review threshold
        then has its post-implementation review due (BRU-FXA-24)."""
        require_group(self.env, USER_GROUP, "Completing a capital project")
        today = fields.Date.context_today(self)
        for rec in self:
            if rec.state != "active":
                raise UserError(self.env._("Only an approved project in progress completes."))
            open_requests = rec.request_ids.filtered(lambda r: r.state in ("submitted",))
            if open_requests:
                raise UserError(
                    self.env._(
                        "%s still has requests awaiting approval: %s.",
                        rec.display_name,
                        ", ".join(open_requests.mapped("name")),
                    )
                )
            days = int(float_param(self.env, PIR_DAYS))
            rec._guarded().write(
                {
                    "state": "completed",
                    "actual_completion": today,
                    "review_due_date": fields.Date.add(today, days=days)
                    if rec.review_required
                    else False,
                }
            )
        return True

    def action_record_review(self):
        """The post-implementation review: actual cost and realised benefit
        against the business case, by someone other than the owner."""
        require_group(self.env, USER_GROUP, "Recording a post-implementation review")
        for rec in self:
            if rec.state != "completed":
                raise UserError(self.env._("Only a completed project is reviewed."))
            if not (rec.benefit_assessment or "").strip() or not rec.review_conclusion:
                raise UserError(
                    self.env._(
                        "%s: write the realised benefit and choose the conclusion first.",
                        rec.display_name,
                    )
                )
            if not self.env.su and self.env.user in (rec.owner_id | rec.create_uid):
                raise UserError(
                    self.env._(
                        "Segregation of duties: the owner of %s does not review it.",
                        rec.display_name,
                    )
                )
            actual = money(rec.actual_cost)
            rec._guarded().write(
                {
                    "state": "reviewed",
                    "review_actual_cost": actual,
                    "review_variance": money(actual - rec.total_budget),
                    "reviewed_by_id": self.env.uid,
                    "reviewed_on": fields.Date.context_today(rec),
                }
            )
        return True

    def action_cancel(self):
        require_group(self.env, MANAGER_GROUP, "Cancelling a capital project")
        for rec in self:
            if rec.state not in ("draft", "active"):
                raise UserError(self.env._("Only a draft or approved project is cancelled."))
            live = rec.request_ids.filtered(
                lambda r: r.state in ("submitted", "approved", "cwip", "capitalised")
            )
            if live:
                raise UserError(
                    self.env._(
                        "%s carries approved or pending capex (%s): it cannot be cancelled.",
                        rec.display_name,
                        ", ".join(live.mapped("name")),
                    )
                )
            rec._guarded().write({"state": "cancelled"})
        return True


class FixCapexRequestProject(models.Model):
    _inherit = "fix.capex.request"

    project_id = fields.Many2one(
        "fix.capital.project",
        string="Capital Project",
        index=True,
        tracking=True,
        domain="[('state', '=', 'active'), ('company_id', '=', company_id)]",
    )

    def _fix_terms_fields(self) -> set:
        return super()._fix_terms_fields() | {"project_id"}

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and self.state not in ("draft", "rejected"):
            locked |= {"project_id"}
        return locked

    def _check_project(self):
        for rec in self.filtered("project_id"):
            project = rec.project_id.sudo()
            if project.state != "active":
                raise UserError(
                    self.env._(
                        "%s: the capital project %s is not approved and in progress.",
                        rec.name,
                        project.display_name,
                    )
                )
            if project.company_id != rec.company_id:
                raise UserError(self.env._("%s: the project is another company's.", rec.name))
            others = project.request_ids.filtered(
                lambda r, me=rec: (
                    r != me and r.state in ("submitted", "approved", "cwip", "capitalised")
                )
            )
            if money(sum(others.mapped("amount")) + rec.amount) > money(project.total_budget):
                raise UserError(
                    self.env._(
                        "%s would take %s over its budget of %s (already approved or pending: %s).",
                        rec.name,
                        project.display_name,
                        project.total_budget,
                        money(sum(others.mapped("amount"))),
                    )
                )

    def action_submit(self):
        self._check_project()
        return super().action_submit()


# ---------------------------------------------------------------------------
# page 3 — componentisation of a CWIP project
# ---------------------------------------------------------------------------
class FixCwipComponent(models.Model):
    """One component of a CWIP project, with its own useful life (FR-FXA-014):
    on capitalisation the project's cost is allocated by the components'
    shares and each becomes its own asset, depreciated independently
    (FR-FXA-016 "one or more active assets ... by an approved basis")."""

    _name = "fix.cwip.component"
    _description = "CWIP Component"
    _inherit = ["fix.guarded.mixin", "mail.thread"]
    _order = "cwip_id, sequence, id"

    cwip_id = fields.Many2one(
        "fix.cwip.entry",
        string="CWIP Project",
        required=True,
        ondelete="cascade",
        index=True,
        domain="[('state', '=', 'open')]",
    )
    sequence = fields.Integer(default=10)
    company_id = fields.Many2one(related="cwip_id.company_id", store=True, index=True)
    operating_unit_id = fields.Many2one(
        related="cwip_id.operating_unit_id", store=True, string="Branch"
    )
    cwip_state = fields.Selection(related="cwip_id.state", string="Project State")
    name = fields.Char(string="Component", required=True, tracking=True)
    category_id = fields.Many2one(
        "fix.asset.category",
        string="Asset Category",
        tracking=True,
        help="Empty: the project's category.",
    )
    share_percent = fields.Float(
        string="Share of Cost %", required=True, digits=(5, 2), tracking=True
    )
    life_months = fields.Integer(
        string="Useful Life (Months)",
        tracking=True,
        help="Empty: the category's default life.",
    )
    salvage_percent = fields.Float(string="Residual % of its Cost", digits=(5, 2))
    asset_id = fields.Many2one(
        "fix.fixed.asset", string="Resulting Asset", readonly=True, copy=False
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"asset_id"}

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields() | {"asset_id"}
        if self and self.cwip_id.state != "open":
            locked |= {n for n, f in self._fields.items() if f.store}
        return locked

    def _assert_open(self, cwips):
        closed = cwips.filtered(lambda c: c.state != "open")
        if closed:
            raise UserError(
                self.env._(
                    "%s is capitalised: its components are fixed.",
                    ", ".join(closed.mapped("name")),
                )
            )

    @api.model_create_multi
    def create(self, vals_list):
        require_group(self.env, USER_GROUP, "Recording a CWIP component")
        Cwip = self.env["fix.cwip.entry"]
        Category = self.env["fix.asset.category"]
        for vals in vals_list:
            cwip = Cwip.browse(vals.get("cwip_id"))
            self._assert_open(cwip)
            if not vals.get("life_months"):
                cat = (
                    Category.browse(vals.get("category_id"))
                    if vals.get("category_id")
                    else cwip.category_id
                )
                vals["life_months"] = cat.useful_life_months or cwip.life_months
        return super().create(vals_list)

    def write(self, vals):
        if self and not self._fix_guard_open():
            self._assert_open(self.mapped("cwip_id"))
            if "cwip_id" in vals:
                self._assert_open(self.env["fix.cwip.entry"].browse(vals["cwip_id"]))
        return super().write(vals)

    @api.ondelete(at_uninstall=False)
    def _unlink_while_open(self):
        self._assert_open(self.mapped("cwip_id"))

    @api.constrains("share_percent", "life_months", "salvage_percent", "cwip_id", "name")
    def _check_component(self):
        for rec in self:
            if not 0.0 < rec.share_percent <= 100.0:
                raise ValidationError(
                    self.env._("A component's share is above 0 and at most 100%.")
                )
            if rec.life_months <= 0:
                raise ValidationError(
                    self.env._("%s: give the component its useful life in months.", rec.name)
                )
            if not 0.0 <= rec.salvage_percent < 100.0:
                raise ValidationError(
                    self.env._("The residual is from 0 to under 100% of the cost.")
                )
            total = sum(rec.cwip_id.component_ids.mapped("share_percent"))
            if total > 100.0 + 0.001:
                raise ValidationError(
                    self.env._(
                        "The components of %s would share %s%% of its cost: at most 100%%.",
                        rec.cwip_id.name,
                        round(total, 2),
                    )
                )


class FixCwipEntryComponents(models.Model):
    _inherit = "fix.cwip.entry"

    component_ids = fields.One2many("fix.cwip.component", "cwip_id", string="Components")
    component_share_total = fields.Float(
        string="Components (% of Cost)", compute="_compute_component_share_total"
    )
    component_asset_ids = fields.One2many(
        "fix.fixed.asset", "cwip_id", string="Capitalised Assets", readonly=True
    )

    @api.depends("component_ids.share_percent")
    def _compute_component_share_total(self):
        for rec in self:
            rec.component_share_total = round(sum(rec.component_ids.mapped("share_percent")), 2)

    def _capitalisation_parts(self, category, life, residual):
        self.ensure_one()
        comps = self.component_ids.sorted(lambda c: (c.sequence, c.id))
        if not comps:
            if category.componentisation_required:
                raise UserError(
                    self.env._(
                        "%s: category %s is capitalised as components — record the "
                        "components and their lives first (FR-FXA-014).",
                        self.name,
                        category.display_name,
                    )
                )
            return super()._capitalisation_parts(category, life, residual)
        total = round(sum(comps.mapped("share_percent")), 2)
        if abs(total - 100.0) > 0.001:
            raise UserError(
                self.env._(
                    "%s: its components share %s%% of the cost — they must share 100%%.",
                    self.name,
                    total,
                )
            )
        parts, left = [], money(self.amount)
        for i, comp in enumerate(comps):
            gross = left if i == len(comps) - 1 else money(self.amount * comp.share_percent / 100.0)
            left = money(left - gross)
            parts.append(
                {
                    "name": "%s - %s" % (self.name, comp.name),
                    "category": comp.category_id or category,
                    "gross": gross,
                    "salvage": money(gross * comp.salvage_percent / 100.0),
                    "life": comp.life_months,
                    "asset_vals": {"cwip_component_id": comp.id},
                }
            )
        return parts

    def _after_capitalise(self, assets):
        res = super()._after_capitalise(assets)
        for asset in assets.filtered("cwip_component_id"):
            asset.cwip_component_id._guarded().write({"asset_id": asset.id})
        return res


# ---------------------------------------------------------------------------
# page 4 — useful life / residual change, suspension and reinstatement
# ---------------------------------------------------------------------------
class FixFixedAssetCapture(models.Model):
    _inherit = "fix.fixed.asset"

    depreciation_suspended = fields.Boolean(
        string="Depreciation Suspended",
        readonly=True,
        copy=False,
        tracking=True,
        help="FR-FXA-024: suspended by an approved depreciation change; the accounting "
        "book charges nothing until it is reinstated (the tax book is independent).",
    )
    cwip_component_id = fields.Many2one(
        "fix.cwip.component", string="CWIP Component", readonly=True, copy=False
    )
    depreciation_change_ids = fields.One2many(
        "fix.asset.depreciation.change", "asset_id", string="Depreciation Changes"
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"depreciation_suspended", "cwip_component_id"}

    def action_accrue_month(self):
        suspended = self.filtered("depreciation_suspended")
        if suspended:
            raise UserError(
                self.env._(
                    "Depreciation of %s is suspended: reinstate it through a depreciation "
                    "change first.",
                    ", ".join(suspended.mapped("display_name")),
                )
            )
        return super().action_accrue_month()


class FixAssetDepreciationRunSuspension(models.Model):
    _inherit = "fix.asset.depreciation.run"

    def _candidate_assets(self):
        assets = super()._candidate_assets()
        if self.book == "book":
            assets = assets.filtered(lambda a: not a.depreciation_suspended)
        return assets


class FixAssetDepreciationChange(models.Model):
    """A change of useful life or residual value, or a suspension /
    reinstatement of depreciation, approved and applied prospectively only
    (FR-FXA-023/024, BRU-FXA-10). The book charge is the remaining carrying
    amount over the remaining life, so the change moves only months not yet
    charged."""

    _name = "fix.asset.depreciation.change"
    _description = "Depreciation Change"
    _inherit = ["fix.guarded.mixin", "mail.thread", "mail.activity.mixin"]
    _order = "id desc"

    name = fields.Char(string="Reference", readonly=True, copy=False, default="/")
    asset_id = fields.Many2one(
        "fix.fixed.asset",
        string="Asset",
        required=True,
        index=True,
        tracking=True,
        domain="[('state', '=', 'active')]",
    )
    company_id = fields.Many2one(related="asset_id.company_id", store=True, index=True)
    operating_unit_id = fields.Many2one(
        related="asset_id.operating_unit_id", store=True, string="Branch"
    )
    currency_id = fields.Many2one(related="asset_id.currency_id")
    kind = fields.Selection(
        [
            ("life", "Useful Life / Residual Value"),
            ("suspend", "Suspend Depreciation (idle / held for disposal)"),
            ("reinstate", "Reinstate Depreciation"),
        ],
        string="Change",
        required=True,
        default="life",
        tracking=True,
    )
    current_life_months = fields.Integer(related="asset_id.life_months", string="Current Life")
    current_salvage = fields.Monetary(related="asset_id.salvage", string="Current Residual")
    months_charged = fields.Integer(related="asset_id.book_months_done", string="Months Charged")
    new_life_months = fields.Integer(
        string="New Useful Life (Months, Total)",
        compute="_compute_new_terms",
        store=True,
        readonly=False,
        precompute=True,
        tracking=True,
    )
    new_salvage = fields.Monetary(
        string="New Residual Value",
        compute="_compute_new_terms",
        store=True,
        readonly=False,
        precompute=True,
        tracking=True,
    )
    reason = fields.Text(string="Justification", required=True)
    requested_by_id = fields.Many2one(
        "res.users", string="Requested By", default=lambda self: self.env.user, readonly=True
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("submitted", "Submitted"),
            ("approved", "Approved - Applied"),
            ("rejected", "Rejected"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )
    approved_by_id = fields.Many2one("res.users", string="Decided By", readonly=True, copy=False)
    approved_on = fields.Datetime(string="Decided On", readonly=True, copy=False)
    applied_from = fields.Date(
        string="Applies From",
        readonly=True,
        copy=False,
        help="The first month not yet charged on the accounting book when it was approved.",
    )
    previous_life_months = fields.Integer(string="Life Before", readonly=True, copy=False)
    previous_salvage = fields.Monetary(string="Residual Before", readonly=True, copy=False)
    rejection_reason = fields.Text(string="Rejection Reason", readonly=True, copy=False)

    _TERMS = ("asset_id", "kind", "new_life_months", "new_salvage", "reason")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "name",
            "state",
            "requested_by_id",
            "approved_by_id",
            "approved_on",
            "applied_from",
            "previous_life_months",
            "previous_salvage",
            "rejection_reason",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and self.state != "draft":
            locked |= set(self._TERMS)
        return locked

    @api.depends("asset_id")
    def _compute_new_terms(self):
        for rec in self:
            if rec.asset_id and not rec.new_life_months:
                rec.new_life_months = rec.asset_id.life_months
            if rec.asset_id and not rec.new_salvage:
                rec.new_salvage = rec.asset_id.salvage

    @api.model_create_multi
    def create(self, vals_list):
        require_group(self.env, USER_GROUP, "Requesting a depreciation change")
        recs = super().create(vals_list)
        for rec in recs:
            rec._guarded().write({"name": _next(self.env, "fix.asset.depreciation.change")})
        return recs

    def write(self, vals):
        if self and not self._fix_guard_open():
            done = self.filtered(lambda r: r.state != "draft")
            if any(
                r._fix_guard_differs(n, vals[n], r[n])
                for r in done
                for n in self._TERMS
                if n in vals
            ):
                raise UserError(self.env._("A submitted depreciation change cannot be edited."))
        return super().write(vals)

    def _assert_applicable(self):
        """The change is valid on the asset as it is NOW (checked at submit and
        again at approval: depreciation may have run in between)."""
        self.ensure_one()
        asset = self.asset_id
        if asset.state != "active":
            raise UserError(self.env._("%s is not in service.", asset.display_name))
        if not (self.reason or "").strip():
            raise UserError(self.env._("%s: write the justification.", self.name))
        if self.kind == "life":
            done = asset.book_months_done
            if self.new_life_months <= done:
                raise UserError(
                    self.env._(
                        "%s: the new life (%s months) must exceed the %s month(s) already "
                        "charged — a change applies prospectively only (BRU-FXA-10).",
                        asset.display_name,
                        self.new_life_months,
                        done,
                    )
                )
            if self.new_salvage < 0 or money(self.new_salvage) > money(asset.book_nbv):
                raise UserError(
                    self.env._(
                        "%s: the residual value must be from 0 to the net book value (%s).",
                        asset.display_name,
                        asset.book_nbv,
                    )
                )
            if self.new_life_months == asset.life_months and money(self.new_salvage) == money(
                asset.salvage
            ):
                raise UserError(self.env._("%s: nothing would change.", self.name))
        elif self.kind == "suspend" and asset.depreciation_suspended:
            raise UserError(self.env._("%s is already suspended.", asset.display_name))
        elif self.kind == "reinstate" and not asset.depreciation_suspended:
            raise UserError(self.env._("%s is not suspended.", asset.display_name))

    def action_submit(self):
        require_group(self.env, USER_GROUP, "Submitting a depreciation change")
        for rec in self:
            if rec.state != "draft":
                raise UserError(self.env._("Only a draft change is submitted."))
            rec._assert_applicable()
            rec._guarded().write({"state": "submitted"})
        return True

    def _first_uncharged_month(self):
        asset = self.asset_id
        posted = asset.depreciation_line_ids.filtered(
            lambda ln: ln.book == "book" and ln.state == "posted"
        )
        if posted:
            last = max(posted.mapped("period_start"))
            return fields.Date.add(last, months=1)
        return month_start(asset.depreciation_start or asset.purchase_date)

    def action_approve(self):
        """Approve and apply: an accounting manager who did not request it."""
        require_group(self.env, MANAGER_GROUP, "Approving a depreciation change")
        for rec in self:
            if rec.state != "submitted":
                raise UserError(self.env._("Only a submitted change is approved."))
            check_sod(self.env, rec.requested_by_id, rec.name, rec)
            rec._assert_applicable()
            asset = rec.asset_id
            stamps = {
                "state": "approved",
                "approved_by_id": self.env.uid,
                "approved_on": fields.Datetime.now(),
                "applied_from": rec._first_uncharged_month(),
                "previous_life_months": asset.life_months,
                "previous_salvage": asset.salvage,
            }
            if rec.kind == "life":
                asset._guarded().write(
                    {"life_months": rec.new_life_months, "salvage": rec.new_salvage}
                )
            else:
                asset._guarded().write({"depreciation_suspended": rec.kind == "suspend"})
            rec._guarded().write(stamps)
            asset.message_post(
                body=self.env._(
                    "Depreciation change %s applied from %s: %s (%s).",
                    rec.name,
                    stamps["applied_from"],
                    dict(rec._fields["kind"].selection)[rec.kind],
                    rec.reason,
                )
            )
        return True

    def action_reject(self, reason=None):
        require_group(self.env, MANAGER_GROUP, "Rejecting a depreciation change")
        reason = (reason or "").strip()
        if not reason:
            raise UserError(self.env._("Give the reason for the rejection."))
        for rec in self:
            if rec.state != "submitted":
                raise UserError(self.env._("Only a submitted change is rejected."))
            check_sod(self.env, rec.requested_by_id, rec.name, rec)
            rec._guarded().write(
                {
                    "state": "rejected",
                    "approved_by_id": self.env.uid,
                    "approved_on": fields.Datetime.now(),
                    "rejection_reason": reason,
                }
            )
        return True

    def action_cancel(self):
        require_group(self.env, USER_GROUP, "Cancelling a depreciation change")
        for rec in self:
            if rec.state not in ("draft", "submitted"):
                raise UserError(self.env._("Only a draft or submitted change is cancelled."))
            rec._guarded().write({"state": "cancelled"})
        return True


# ---------------------------------------------------------------------------
# page 5 — impairment assessment (recorded whether or not impairment results)
# ---------------------------------------------------------------------------
INDICATORS = (
    "ind_damage",
    "ind_idle",
    "ind_performance",
    "ind_market",
    "ind_environment",
    "ind_other",
)


class FixAssetImpairmentAssessment(models.Model):
    """The impairment indicator assessment of an asset or a branch (the
    cash-generating unit), annual or on a trigger event, with the test result
    — recorded whether or not an impairment results (FR-FXA-032, BRU-FXA-26).
    A confirmed impairment of an asset raises the IAS 36 impairment document
    (fix.asset.revaluation) that the CFO tier approves and posts."""

    _name = "fix.asset.impairment.assessment"
    _description = "Impairment Assessment"
    _inherit = ["fix.guarded.mixin", "mail.thread", "mail.activity.mixin"]
    _order = "assessment_date desc, id desc"

    name = fields.Char(string="Reference", readonly=True, copy=False, default="/")
    scope = fields.Selection(
        [("asset", "One Asset"), ("branch", "Branch (Cash-Generating Unit)")],
        string="Scope",
        required=True,
        default="asset",
        tracking=True,
    )
    asset_id = fields.Many2one(
        "fix.fixed.asset",
        string="Asset",
        index=True,
        tracking=True,
        domain="[('state', '=', 'active')]",
    )
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one(
        "operating.unit",
        string="Branch",
        compute="_compute_operating_unit",
        store=True,
        readonly=False,
        precompute=True,
        tracking=True,
    )
    currency_id = fields.Many2one(related="company_id.currency_id")
    assessment_date = fields.Date(
        string="Assessment Date", required=True, default=fields.Date.context_today
    )
    trigger = fields.Selection(
        [("annual", "Annual Assessment"), ("event", "Trigger Event")],
        string="Occasion",
        required=True,
        default="annual",
    )
    ind_damage = fields.Boolean(string="Physical Damage or Obsolescence")
    ind_idle = fields.Boolean(string="Idle, Discontinued or to be Disposed of")
    ind_performance = fields.Boolean(string="Performance Worse than Expected (Branch Losses)")
    ind_market = fields.Boolean(string="Significant Fall in Market Value")
    ind_environment = fields.Boolean(string="Adverse Technological, Economic or Legal Change")
    ind_other = fields.Boolean(string="Other Indicator")
    indicator_note = fields.Text(string="Indicators Observed and Evidence")
    conclusion = fields.Selection(
        [
            ("no_indicator", "No Indicator - No Test Needed"),
            ("no_impairment", "Tested - Recoverable Amount Covers the Carrying Amount"),
            ("impaired", "Tested - Impairment Required"),
        ],
        string="Conclusion",
        required=True,
        default="no_indicator",
        tracking=True,
    )
    recoverable_amount = fields.Monetary(
        string="Recoverable Amount",
        help="The higher of fair value less costs of disposal and value in use (IAS 36).",
    )
    basis = fields.Text(string="Test Basis (cash flows, discount rate, valuer)")
    assessed_by_id = fields.Many2one(
        "res.users", string="Assessed By", default=lambda self: self.env.user, readonly=True
    )
    state = fields.Selection(
        [("draft", "Draft"), ("confirmed", "Confirmed"), ("cancelled", "Cancelled")],
        default="draft",
        required=True,
        tracking=True,
    )
    carrying_amount = fields.Monetary(string="Carrying Amount", readonly=True, copy=False)
    impairment_loss = fields.Monetary(string="Impairment Loss", readonly=True, copy=False)
    confirmed_by_id = fields.Many2one("res.users", string="Confirmed By", readonly=True, copy=False)
    confirmed_on = fields.Date(string="Confirmed On", readonly=True, copy=False)
    revaluation_id = fields.Many2one(
        "fix.asset.revaluation", string="Impairment Raised", readonly=True, copy=False
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "name",
            "state",
            "assessed_by_id",
            "carrying_amount",
            "impairment_loss",
            "confirmed_by_id",
            "confirmed_on",
            "revaluation_id",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and self.state != "draft":
            locked |= {n for n, f in self._fields.items() if f.store}
        return locked

    @api.depends("asset_id")
    def _compute_operating_unit(self):
        for rec in self:
            if rec.asset_id:
                rec.operating_unit_id = rec.asset_id.operating_unit_id

    @api.model_create_multi
    def create(self, vals_list):
        require_group(self.env, USER_GROUP, "Recording an impairment assessment")
        Asset = self.env["fix.fixed.asset"]
        for vals in vals_list:
            if vals.get("asset_id"):
                vals["company_id"] = Asset.browse(vals["asset_id"]).company_id.id
        recs = super().create(vals_list)
        for rec in recs:
            rec._guarded().write({"name": _next(self.env, "fix.asset.impairment.assessment")})
        return recs

    def write(self, vals):
        if self and not self._fix_guard_open():
            moving = {k for k in vals if not k.startswith(("message_", "activity_"))}
            if moving and self.filtered(lambda r: r.state != "draft"):
                raise UserError(self.env._("A confirmed assessment is not edited."))
        return super().write(vals)

    @api.constrains("scope", "asset_id", "operating_unit_id", "conclusion", *INDICATORS)
    def _check_scope(self):
        for rec in self:
            if rec.scope == "asset" and not rec.asset_id:
                raise ValidationError(self.env._("Choose the asset assessed."))
            if rec.scope == "branch" and not rec.operating_unit_id:
                raise ValidationError(self.env._("Choose the branch assessed."))
            if rec.conclusion == "no_indicator" and any(rec[f] for f in INDICATORS):
                raise ValidationError(
                    self.env._(
                        "An indicator was observed: the asset is tested (IAS 36.9) — choose a "
                        "tested conclusion."
                    )
                )

    def _carrying(self):
        self.ensure_one()
        if self.scope == "asset":
            return money(self.asset_id.book_nbv)
        assets = self.env["fix.fixed.asset"].search(
            [
                ("company_id", "=", self.company_id.id),
                ("operating_unit_id", "=", self.operating_unit_id.id),
                ("state", "=", "active"),
            ]
        )
        return money(sum(assets.mapped("book_nbv")))

    def action_confirm(self):
        """Confirm the assessment: an accounting manager who did not make it.
        The carrying amount is stamped; a tested conclusion must agree with
        it; an impairment raises the draft IAS 36 document."""
        require_group(self.env, MANAGER_GROUP, "Confirming an impairment assessment")
        for rec in self:
            if rec.state != "draft":
                raise UserError(self.env._("Only a draft assessment is confirmed."))
            check_sod(self.env, rec.assessed_by_id, rec.name, rec)
            if any(rec[f] for f in INDICATORS) and not (rec.indicator_note or "").strip():
                raise UserError(self.env._("%s: describe the indicators observed.", rec.name))
            carrying = rec._carrying()
            stamps = {
                "state": "confirmed",
                "carrying_amount": carrying,
                "confirmed_by_id": self.env.uid,
                "confirmed_on": fields.Date.context_today(rec),
            }
            if rec.conclusion != "no_indicator":
                if rec.recoverable_amount <= 0 or not (rec.basis or "").strip():
                    raise UserError(
                        self.env._(
                            "%s: a tested conclusion needs the recoverable amount and the "
                            "test basis.",
                            rec.name,
                        )
                    )
                short = money(carrying - rec.recoverable_amount)
                if rec.conclusion == "no_impairment" and short > 0:
                    raise UserError(
                        self.env._(
                            "%s: the recoverable amount (%s) is below the carrying amount "
                            "(%s) — the conclusion is an impairment.",
                            rec.name,
                            rec.recoverable_amount,
                            carrying,
                        )
                    )
                if rec.conclusion == "impaired":
                    if short <= 0:
                        raise UserError(
                            self.env._(
                                "%s: the recoverable amount covers the carrying amount — "
                                "nothing is impaired.",
                                rec.name,
                            )
                        )
                    if rec.scope != "asset":
                        raise UserError(
                            self.env._(
                                "%s: allocate a branch impairment to its assets — record one "
                                "assessment per asset impaired.",
                                rec.name,
                            )
                        )
                    stamps["impairment_loss"] = short
                    stamps["revaluation_id"] = (
                        self.env["fix.asset.revaluation"]
                        .create(
                            {
                                "asset_id": rec.asset_id.id,
                                "kind": "impairment",
                                "date": rec.assessment_date,
                                "new_value": rec.recoverable_amount,
                                "basis": "%s: %s" % (rec.name, rec.basis),
                            }
                        )
                        .id
                    )
            rec._guarded().write(stamps)
        return True

    def action_cancel(self):
        require_group(self.env, USER_GROUP, "Cancelling an impairment assessment")
        for rec in self:
            if rec.state != "draft":
                raise UserError(self.env._("Only a draft assessment is cancelled."))
            rec._guarded().write({"state": "cancelled"})
        return True


# ---------------------------------------------------------------------------
# page 7 — verification variance investigation
# ---------------------------------------------------------------------------
VARIANCES = ("missing", "misplaced", "unregistered")
ALLOWED_ACTIONS = {
    "missing": ("located", "write_off", "explained"),
    "misplaced": ("located", "transfer", "explained"),
    "unregistered": ("register", "explained"),
}


class FixAssetVerificationLineName(models.Model):
    """A result has no name field: without one the variance form's picker
    showed "fix.asset.verification.line,12". It reads campaign / tag / result."""

    _inherit = "fix.asset.verification.line"

    @api.depends("campaign_id.name", "asset_id.code", "scanned_tag", "result")
    def _compute_display_name(self):
        labels = dict(self._fields["result"].selection)
        for rec in self:
            rec.display_name = "%s / %s / %s" % (
                rec.campaign_id.name or "-",
                rec.asset_id.code or rec.scanned_tag or "-",
                labels.get(rec.result, rec.result or "-"),
            )


class FixAssetVerificationVariance(models.Model):
    """The investigation of one verification variance — missing, found at
    another branch, or not in the register — and the register correction it
    proposes, approved by an accountant who neither counted nor proposed it
    (FR-FXA-030, BRU-FXA-15/16). Approval applies the correction: the result
    is corrected, or a transfer or write-off document is raised for its own
    approval."""

    _name = "fix.asset.verification.variance"
    _description = "Verification Variance"
    _inherit = ["fix.guarded.mixin", "mail.thread", "mail.activity.mixin"]
    _order = "id desc"

    name = fields.Char(string="Reference", readonly=True, copy=False, default="/")
    line_id = fields.Many2one(
        "fix.asset.verification.line",
        string="Verification Result",
        required=True,
        index=True,
        domain="[('result', 'in', ('missing', 'misplaced', 'unregistered'))]",
    )
    campaign_id = fields.Many2one(related="line_id.campaign_id", store=True, string="Campaign")
    company_id = fields.Many2one(related="line_id.company_id", store=True, index=True)
    operating_unit_id = fields.Many2one(
        related="line_id.operating_unit_id", store=True, string="Expected Branch"
    )
    asset_id = fields.Many2one(related="line_id.asset_id", store=True, string="Asset")
    scanned_tag = fields.Char(related="line_id.scanned_tag", string="Scanned Tag")
    scanned_operating_unit_id = fields.Many2one(
        related="line_id.scanned_operating_unit_id", string="Found At"
    )
    variance_type = fields.Selection(
        [
            ("missing", "Missing"),
            ("misplaced", "Found at Another Branch"),
            ("unregistered", "Found - Not in Register"),
        ],
        string="Variance",
        readonly=True,
    )
    investigator_id = fields.Many2one(
        "res.users", string="Investigator", default=lambda self: self.env.user, tracking=True
    )
    explanation = fields.Text(string="Investigation Findings")
    proposed_action = fields.Selection(
        [
            ("located", "Asset Located - Correct the Result to Found"),
            ("transfer", "Register Branch Wrong - Raise a Transfer"),
            ("write_off", "Lost / Stolen / Destroyed - Raise a Write-Off"),
            ("register", "Not in the Register - Capitalise through Its Source"),
            ("explained", "Explained - No Register Change"),
        ],
        string="Proposed Correction",
        tracking=True,
    )
    incident_ref = fields.Char(string="Incident Reference (write-off)", tracking=True)
    state = fields.Selection(
        [
            ("open", "Under Investigation"),
            ("proposed", "Correction Proposed"),
            ("approved", "Approved - Applied"),
            ("rejected", "Rejected"),
        ],
        default="open",
        required=True,
        tracking=True,
    )
    proposed_by_id = fields.Many2one("res.users", string="Proposed By", readonly=True, copy=False)
    approved_by_id = fields.Many2one("res.users", string="Decided By", readonly=True, copy=False)
    approved_on = fields.Datetime(string="Decided On", readonly=True, copy=False)
    rejection_reason = fields.Text(string="Rejection Reason", readonly=True, copy=False)
    transfer_id = fields.Many2one(
        "fix.asset.transfer", string="Transfer Raised", readonly=True, copy=False
    )
    disposal_id = fields.Many2one(
        "fix.asset.disposal", string="Write-Off Raised", readonly=True, copy=False
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "name",
            "state",
            "variance_type",
            "proposed_by_id",
            "approved_by_id",
            "approved_on",
            "rejection_reason",
            "transfer_id",
            "disposal_id",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self:
            locked |= {"line_id"}
        if self and self.state != "open":
            locked |= {"investigator_id", "explanation", "proposed_action", "incident_ref"}
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        require_group(self.env, USER_GROUP, "Opening a variance investigation")
        Line = self.env["fix.asset.verification.line"]
        for vals in vals_list:
            line = Line.browse(vals.get("line_id"))
            if line.result not in VARIANCES:
                raise UserError(
                    self.env._(
                        "%s is not a variance (it is %s): only a missing, misplaced or "
                        "unregistered result is investigated.",
                        line.display_name,
                        line.result,
                    )
                )
            if self.search_count(
                [("line_id", "=", line.id), ("state", "in", ("open", "proposed", "approved"))]
            ):
                raise UserError(self.env._("%s is already under investigation.", line.display_name))
        recs = super().create(vals_list)
        for rec in recs:
            rec._guarded().write(
                {
                    "name": _next(self.env, "fix.asset.verification.variance"),
                    "variance_type": rec.line_id.result,
                }
            )
        return recs

    def write(self, vals):
        if (
            self
            and not self._fix_guard_open()
            and "line_id" in vals
            and any(r._fix_guard_differs("line_id", vals["line_id"], r.line_id) for r in self)
        ):
            raise UserError(self.env._("A variance stays on the result it investigates."))
        return super().write(vals)

    def action_propose(self):
        require_group(self.env, USER_GROUP, "Proposing a variance correction")
        for rec in self:
            if rec.state != "open":
                raise UserError(self.env._("Only a variance under investigation is proposed."))
            if not (rec.explanation or "").strip() or not rec.proposed_action:
                raise UserError(
                    self.env._("%s: write the findings and choose the correction first.", rec.name)
                )
            allowed = ALLOWED_ACTIONS[rec.variance_type]
            if rec.proposed_action not in allowed:
                raise UserError(
                    self.env._(
                        "%s: a %s result is corrected by: %s.",
                        rec.name,
                        dict(rec._fields["variance_type"].selection)[rec.variance_type],
                        ", ".join(
                            dict(rec._fields["proposed_action"].selection)[a] for a in allowed
                        ),
                    )
                )
            if rec.proposed_action == "write_off" and not (rec.incident_ref or "").strip():
                raise UserError(
                    self.env._(
                        "%s: a write-off needs the incident reference (BRU-FXA-19).", rec.name
                    )
                )
            if rec.proposed_action == "transfer" and not rec.scanned_operating_unit_id:
                raise UserError(
                    self.env._("%s: the branch it was found at is not recorded.", rec.name)
                )
            rec._guarded().write({"state": "proposed", "proposed_by_id": self.env.uid})
        return True

    def _check_deciders(self):
        """BRU-FXA-15/16: neither the counter nor the proposer decides."""
        for rec in self:
            if self.env.su:
                continue
            counter = rec.campaign_id.sudo().responsible_id
            if self.env.user == counter:
                raise UserError(
                    self.env._(
                        "Segregation of duties: the counter of %s does not decide its "
                        "variances (BRU-FXA-15).",
                        rec.campaign_id.name,
                    )
                )
            check_sod(self.env, rec.proposed_by_id, rec.name, rec)

    def action_approve(self):
        require_group(self.env, MANAGER_GROUP, "Approving a variance correction")
        for rec in self:
            if rec.state != "proposed":
                raise UserError(self.env._("Only a proposed correction is approved."))
            rec._check_deciders()
            vals = {
                "state": "approved",
                "approved_by_id": self.env.uid,
                "approved_on": fields.Datetime.now(),
            }
            line = rec.line_id
            asset = rec.asset_id
            if rec.proposed_action == "located":
                line._guarded().write(
                    {
                        "result": "found",
                        "scanned_at": fields.Datetime.now(),
                        "corrected_by_id": self.env.uid,
                    }
                )
            elif rec.proposed_action == "transfer":
                vals["transfer_id"] = (
                    self.env["fix.asset.transfer"]
                    .create(
                        {
                            "asset_id": asset.id,
                            "date": fields.Date.context_today(rec),
                            "operating_unit_id": rec.scanned_operating_unit_id.id,
                            "reason": "%s: %s" % (rec.name, rec.explanation),
                        }
                    )
                    .id
                )
            elif rec.proposed_action == "write_off":
                vals["disposal_id"] = (
                    self.env["fix.asset.disposal"]
                    .create(
                        {
                            "asset_id": asset.id,
                            "kind": "write_off",
                            "date": fields.Date.context_today(rec),
                            "incident_ref": rec.incident_ref,
                            "reason": "%s: %s" % (rec.name, rec.explanation),
                        }
                    )
                    .id
                )
            rec._guarded().write(vals)
        return True

    def action_reject(self, reason=None):
        require_group(self.env, MANAGER_GROUP, "Rejecting a variance correction")
        reason = (reason or "").strip()
        if not reason:
            raise UserError(self.env._("Give the reason for the rejection."))
        for rec in self:
            if rec.state != "proposed":
                raise UserError(self.env._("Only a proposed correction is rejected."))
            rec._check_deciders()
            rec._guarded().write(
                {
                    "state": "rejected",
                    "approved_by_id": self.env.uid,
                    "approved_on": fields.Datetime.now(),
                    "rejection_reason": reason,
                }
            )
        return True
