# fix_asset_gaps — the two M49 capture gaps left by the 2026-11-17 audit
# (spec 03_Modules/G_Finance_and_Treasury/M49):
#
#   * fix.asset.component   page 3  FR-FXA-014: componentising an asset that
#                           comes into service through the M19 seam (a CWIP
#                           project is componentised by fix.cwip.component)
#   * fix.asset.insurance   page 8  capability 20, BRU-FXA-25, AUT-FXA-20:
#                           insurance cover against the register value, its
#                           review, the gap report to the CFO, and the claim
#                           link from a write-off
#
# Sums insured are restricted to R03, R26 and R27 (spec section 13), i.e. the
# accountant and accounting manager groups: the read-only group has no access.
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from .fix_asset_common import (
    INSURANCE_GAP_TOLERANCE,
    INSURANCE_REVIEW_DAYS,
    MANAGER_GROUP,
    USER_GROUP,
    attach_upload,
    attachment_names,
    check_sod,
    float_param,
    money,
    post_entry,
    require_accounts,
    require_group,
)


def _next(env, code):
    return env["ir.sequence"].next_by_code(code) or "/"


# ---------------------------------------------------------------------------
# page 3 — components of an asset brought into service through the M19 seam
# ---------------------------------------------------------------------------
class FixAssetComponent(models.Model):
    """One component of a registered (draft) asset with its own useful life
    (FR-FXA-014, IAS 16.43). When the asset is put into service from its M19
    seam, its cost is allocated by the components' shares and each component
    becomes its own asset, depreciated independently. A component in another
    asset category is reclassified to that category's asset account."""

    _name = "fix.asset.component"
    _description = "Asset Component"
    _inherit = ["fix.guarded.mixin", "mail.thread"]
    _order = "parent_asset_id, sequence, id"

    parent_asset_id = fields.Many2one(
        "fix.fixed.asset",
        string="Asset (registered, not in service)",
        required=True,
        ondelete="cascade",
        index=True,
        domain="[('state', '=', 'draft')]",
    )
    sequence = fields.Integer(default=10)
    company_id = fields.Many2one(related="parent_asset_id.company_id", store=True, index=True)
    operating_unit_id = fields.Many2one(
        related="parent_asset_id.operating_unit_id", store=True, string="Branch"
    )
    parent_state = fields.Selection(related="parent_asset_id.state", string="Asset State")
    name = fields.Char(string="Component", required=True, tracking=True)
    category_id = fields.Many2one(
        "fix.asset.category",
        string="Asset Category",
        tracking=True,
        help="Empty: the asset's category.",
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
    reclass_move_id = fields.Many2one(
        "account.move",
        string="Reclassification Entry",
        readonly=True,
        copy=False,
        help="Posted when the component's category books to another asset account.",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"asset_id", "reclass_move_id"}

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields() | {"asset_id", "reclass_move_id"}
        if self and self.parent_asset_id.state != "draft":
            locked |= {n for n, f in self._fields.items() if f.store}
        return locked

    def _assert_draft(self, assets):
        live = assets.filtered(lambda a: a.state != "draft")
        if live:
            raise UserError(
                self.env._(
                    "%s is in service: its components are fixed. An asset is split into "
                    "components before it is put into service (IAS 16.43).",
                    ", ".join(live.mapped("display_name")),
                )
            )

    @api.model_create_multi
    def create(self, vals_list):
        require_group(self.env, USER_GROUP, "Recording an asset component")
        Asset = self.env["fix.fixed.asset"]
        Category = self.env["fix.asset.category"]
        for vals in vals_list:
            asset = Asset.browse(vals.get("parent_asset_id"))
            self._assert_draft(asset)
            if not vals.get("life_months"):
                cat = (
                    Category.browse(vals.get("category_id"))
                    if vals.get("category_id")
                    else asset.category_id
                )
                vals["life_months"] = cat.useful_life_months or asset.life_months
        return super().create(vals_list)

    def write(self, vals):
        if self and not self._fix_guard_open():
            self._assert_draft(self.mapped("parent_asset_id"))
            if "parent_asset_id" in vals:
                self._assert_draft(self.env["fix.fixed.asset"].browse(vals["parent_asset_id"]))
        return super().write(vals)

    @api.ondelete(at_uninstall=False)
    def _unlink_while_draft(self):
        self._assert_draft(self.mapped("parent_asset_id"))

    @api.constrains("share_percent", "life_months", "salvage_percent", "parent_asset_id", "name")
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
            if rec.parent_asset_id.cwip_id:
                raise ValidationError(
                    self.env._(
                        "%s came from a CWIP project: it is componentised on the project "
                        "(CWIP Components).",
                        rec.parent_asset_id.display_name,
                    )
                )
            total = sum(rec.parent_asset_id.asset_component_ids.mapped("share_percent"))
            if total > 100.0 + 0.001:
                raise ValidationError(
                    self.env._(
                        "The components of %s would share %s%% of its cost: at most 100%%.",
                        rec.parent_asset_id.display_name,
                        round(total, 2),
                    )
                )


class FixFixedAssetGaps(models.Model):
    _inherit = "fix.fixed.asset"

    asset_component_ids = fields.One2many(
        "fix.asset.component", "parent_asset_id", string="Components"
    )
    asset_component_share_total = fields.Float(
        string="Components (% of Cost)", compute="_compute_asset_component_share_total"
    )
    component_of_id = fields.Many2one(
        "fix.fixed.asset",
        string="Split From",
        readonly=True,
        copy=False,
        index=True,
        help="The asset whose cost this component was split from on going into service.",
    )
    insured_under = fields.Char(
        string="Insured Under",
        compute="_compute_insured_under",
        help="The active insurance policies whose cover includes this asset.",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"component_of_id"}

    @api.depends("asset_component_ids.share_percent")
    def _compute_asset_component_share_total(self):
        for rec in self:
            rec.asset_component_share_total = round(
                sum(rec.asset_component_ids.mapped("share_percent")), 2
            )

    def _compute_insured_under(self):
        Policy = self.env["fix.asset.insurance"].sudo()
        policies = Policy.search([("state", "=", "active")])
        for rec in self:
            covering = policies.filtered(lambda p, a=rec: p._covers(a.sudo()))
            rec.insured_under = ", ".join(covering.mapped("name"))

    def _component_parts(self):
        """The assets this one goes into service as: one per component, the
        cost allocated by share (the last takes the rounding remainder)."""
        self.ensure_one()
        comps = self.asset_component_ids.sorted(lambda c: (c.sequence, c.id))
        total = round(sum(comps.mapped("share_percent")), 2)
        if abs(total - 100.0) > 0.001:
            raise UserError(
                self.env._(
                    "%s: its components share %s%% of the cost — they must share 100%%.",
                    self.display_name,
                    total,
                )
            )
        parts, left = [], money(self.gross)
        for i, comp in enumerate(comps):
            gross = left if i == len(comps) - 1 else money(self.gross * comp.share_percent / 100.0)
            left = money(left - gross)
            parts.append(
                {
                    "component": comp,
                    "name": "%s - %s" % (self.name, comp.name),
                    "category": comp.category_id or self.category_id,
                    "gross": gross,
                    "salvage": money(gross * comp.salvage_percent / 100.0),
                    "life": comp.life_months,
                }
            )
        return parts

    def _activate_from_seam(self, seam, move):
        """FR-FXA-014: an asset with components goes into service as one asset
        per component. The parent record carries the first component; the
        others are new assets split from it. A component in another category
        is reclassified (Dr its asset account / Cr the seam's) in one entry."""
        self.ensure_one()
        if not self.asset_component_ids:
            if self.category_id.componentisation_required:
                raise UserError(
                    self.env._(
                        "%s: category %s is capitalised as components — record the "
                        "components and their lives first (FR-FXA-014).",
                        self.display_name,
                        self.category_id.display_name,
                    )
                )
            return super()._activate_from_seam(seam, move)
        parts = self._component_parts()
        source = self.category_id.asset_account_id
        moving = [p for p in parts if p["category"].asset_account_id != source]
        moving_ids = {p["component"].id for p in moving}
        for part in parts:
            require_accounts(part["category"], ["asset_account_id"], "Asset componentisation")
        reclass = self.env["account.move"]
        if moving:
            require_accounts(self.category_id, ["journal_id"], "Asset componentisation")
            reclass = post_entry(
                self.env,
                self.company_id,
                self.category_id.journal_id,
                fields.Date.context_today(self),
                "Componentisation: %s" % self.display_name,
                [(p["category"].asset_account_id, p["gross"], 0.0, p["name"]) for p in moving]
                + [(source, 0.0, sum(p["gross"] for p in moving), self.display_name)],
                self.operating_unit_id,
            )
        seam.action_mark_consumed()
        first, assets = parts[0], self
        common = {
            "company_id": self.company_id.id,
            "operating_unit_id": self.operating_unit_id.id,
            "custodian_id": self.custodian_id.id,
            "purchase_date": self.purchase_date,
            "depreciation_start": self.depreciation_start,
            "currency_id": self.currency_id.id,
        }
        for part in parts[1:]:
            assets |= (
                self.env["fix.fixed.asset"]
                ._guarded()
                .create(
                    dict(
                        common,
                        name=part["name"],
                        category_id=part["category"].id,
                        gross=part["gross"],
                        salvage=part["salvage"],
                        life_months=part["life"],
                        component_of_id=self.id,
                    )
                )
            )
        self._guarded().write(
            {
                "name": first["name"],
                "category_id": first["category"].id,
                "gross": first["gross"],
                "salvage": first["salvage"],
                "life_months": first["life"],
            }
        )
        for part, asset in zip(parts, assets, strict=True):
            part["component"]._guarded().write(
                {
                    "asset_id": asset.id,
                    "reclass_move_id": reclass.id if part["component"].id in moving_ids else False,
                }
            )
            asset._fix_activate_from_source(move)
        self.message_post(
            body=self.env._(
                "Put into service as %s components: %s.",
                len(parts),
                ", ".join(assets.mapped("display_name")),
            )
        )
        return assets


# ---------------------------------------------------------------------------
# page 8 — insurance cover against the register value
# ---------------------------------------------------------------------------
class FixAssetInsurance(models.Model):
    """An insurance policy and the assets it covers — named assets, or an
    asset class (optionally one branch) — compared with their register value
    (capability 20, BRU-FXA-25). Reviewed at least annually; a gap above the
    tolerance either way is reported to the CFO (AUT-FXA-20)."""

    _name = "fix.asset.insurance"
    _description = "Asset Insurance Policy"
    _inherit = ["fix.guarded.mixin", "mail.thread", "mail.activity.mixin"]
    _order = "period_to desc, id desc"

    reference = fields.Char(string="Reference", readonly=True, copy=False, default="/")
    name = fields.Char(string="Policy Number", required=True, tracking=True)
    insurer_id = fields.Many2one("res.partner", string="Insurer", required=True, tracking=True)
    cover_type = fields.Selection(
        [
            ("all_risk", "All Risks"),
            ("fire", "Fire & Allied Perils"),
            ("burglary", "Burglary & Theft"),
            ("equipment", "Electronic Equipment"),
            ("motor", "Motor"),
            ("other", "Other"),
        ],
        string="Cover",
        required=True,
        default="all_risk",
        tracking=True,
    )
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    scope = fields.Selection(
        [("assets", "Named Assets"), ("category", "Asset Class")],
        string="Covers",
        required=True,
        default="assets",
        tracking=True,
    )
    asset_ids = fields.Many2many(
        "fix.fixed.asset",
        "fix_asset_insurance_asset_rel",
        "insurance_id",
        "asset_id",
        string="Named Assets",
        domain="[('company_id', '=', company_id), ('state', 'in', ('draft', 'active'))]",
    )
    category_ids = fields.Many2many(
        "fix.asset.category",
        "fix_asset_insurance_category_rel",
        "insurance_id",
        "category_id",
        string="Asset Classes",
    )
    operating_unit_id = fields.Many2one(
        "operating.unit",
        string="Branch (location)",
        help="Class cover limited to one location. Empty: the class at every branch.",
    )
    sum_insured = fields.Monetary(string="Sum Insured", required=True, tracking=True)
    premium = fields.Monetary(string="Annual Premium", tracking=True)
    period_from = fields.Date(string="Cover From", required=True, tracking=True)
    period_to = fields.Date(string="Cover To", required=True, tracking=True)
    replaces_id = fields.Many2one(
        "fix.asset.insurance",
        string="Renews / Endorses",
        help="The earlier policy this one supersedes; it closes when this one is activated.",
    )
    policy_doc_ids = fields.Many2many(
        "ir.attachment",
        "fix_asset_insurance_doc_rel",
        "insurance_id",
        "attachment_id",
        string="Policy Documents",
    )
    policy_file = fields.Binary(
        string="Upload Policy Schedule",
        compute="_compute_policy_file",
        inverse="_inverse_policy_file",
    )
    policy_filename = fields.Char(string="Policy File Name")
    policy_doc_names = fields.Char(
        string="Policy Documents Attached", compute="_compute_policy_doc_names"
    )

    covered_count = fields.Integer(string="Assets Covered", compute="_compute_cover")
    register_value = fields.Monetary(
        string="Register Value (NBV)",
        compute="_compute_cover",
        help="Net book value of the assets in service the policy covers.",
    )
    coverage_gap = fields.Monetary(
        string="Coverage Gap (+ under-insured)",
        compute="_compute_cover",
        help="Register value less sum insured: positive means under-insured, negative over-insured.",
    )
    coverage_gap_percent = fields.Float(
        string="Gap % of Register Value", compute="_compute_cover", digits=(6, 2)
    )
    coverage_status = fields.Selection(
        [("ok", "Within Tolerance"), ("under", "Under-Insured"), ("over", "Over-Insured")],
        string="Coverage",
        compute="_compute_cover",
    )

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("active", "In Force"),
            ("expired", "Expired"),
            ("replaced", "Renewed / Replaced"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )
    approved_by_id = fields.Many2one("res.users", string="Activated By", readonly=True, copy=False)
    approved_on = fields.Date(string="Activated On", readonly=True, copy=False)
    review_note = fields.Text(string="Review Note", tracking=True)
    last_reviewed_on = fields.Date(string="Last Reviewed", readonly=True, copy=False)
    reviewed_by_id = fields.Many2one("res.users", string="Reviewed By", readonly=True, copy=False)
    reviewed_register_value = fields.Monetary(
        string="Register Value at Review", readonly=True, copy=False
    )
    reviewed_sum_insured = fields.Monetary(
        string="Sum Insured at Review", readonly=True, copy=False
    )
    reviewed_gap = fields.Monetary(string="Gap at Review", readonly=True, copy=False)
    gap_reported = fields.Boolean(
        string="Gap Reported to CFO", readonly=True, copy=False, tracking=True
    )
    review_due_date = fields.Date(string="Review Due", compute="_compute_review_due")
    review_overdue = fields.Boolean(string="Review Overdue", compute="_compute_review_due")

    _TERMS = (
        "name",
        "insurer_id",
        "cover_type",
        "company_id",
        "currency_id",
        "scope",
        "asset_ids",
        "category_ids",
        "operating_unit_id",
        "sum_insured",
        "premium",
        "period_from",
        "period_to",
        "replaces_id",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "reference",
            "approved_by_id",
            "approved_on",
            "last_reviewed_on",
            "reviewed_by_id",
            "reviewed_register_value",
            "reviewed_sum_insured",
            "reviewed_gap",
            "gap_reported",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and self.state != "draft":
            locked |= set(self._TERMS)
        if self and self.state in ("expired", "replaced", "cancelled"):
            locked |= {"review_note", "policy_file"}
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        recs = super().create(vals_list)
        for rec in recs:
            rec._guarded().write({"reference": _next(self.env, "fix.asset.insurance")})
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
                            "%s is in force: its cover is fixed (%s). Record the endorsement "
                            "or renewal as a new policy that renews this one.",
                            rec.display_name,
                            ", ".join(moved),
                        )
                    )
        return super().write(vals)

    @api.depends("reference", "name")
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = "%s %s" % (rec.reference or "", rec.name or "")

    def _compute_policy_file(self):
        for rec in self:
            rec.policy_file = False

    def _inverse_policy_file(self):
        for rec in self:
            attach_upload(
                rec,
                "policy_doc_ids",
                rec.policy_file,
                rec.policy_filename,
                "Policy schedule %s" % rec.name,
            )

    @api.depends("policy_doc_ids")
    def _compute_policy_doc_names(self):
        for rec in self:
            rec.policy_doc_names = attachment_names(rec.policy_doc_ids)

    def _covers(self, asset):
        """Whether the policy's cover includes `asset` (whatever its state:
        a write-off claims for an asset leaving the register)."""
        self.ensure_one()
        if not asset or asset.company_id != self.company_id:
            return False
        if self.scope == "assets":
            return asset in self.asset_ids
        return asset.category_id in self.category_ids and (
            not self.operating_unit_id or asset.operating_unit_id == self.operating_unit_id
        )

    def _covered_assets(self):
        """The assets the policy covers, in service or registered."""
        self.ensure_one()
        Asset = self.env["fix.fixed.asset"].sudo()
        if self.scope == "assets":
            return self.asset_ids.sudo().filtered(lambda a: a.state in ("draft", "active"))
        if not self.category_ids:
            return Asset
        domain = [
            ("company_id", "=", self.company_id.id),
            ("state", "in", ("draft", "active")),
            ("category_id", "in", self.category_ids.ids),
        ]
        if self.operating_unit_id:
            domain.append(("operating_unit_id", "=", self.operating_unit_id.id))
        return Asset.search(domain)

    def _cover_position(self):
        """(register value, gap, gap %, status) against the current register."""
        self.ensure_one()
        tolerance = float_param(self.env, INSURANCE_GAP_TOLERANCE)
        in_service = self._covered_assets().filtered(lambda a: a.state == "active")
        value = money(sum(in_service.mapped("book_nbv")))
        gap = money(value - self.sum_insured)
        if value:
            percent = round(gap / value * 100.0, 2)
        else:
            percent = 0.0 if not self.sum_insured else -100.0
        status = "ok"
        if abs(percent) > tolerance:
            status = "under" if gap > 0 else "over"
        return value, gap, percent, status

    @api.depends("scope", "asset_ids", "category_ids", "operating_unit_id", "sum_insured")
    def _compute_cover(self):
        for rec in self:
            rec.covered_count = len(rec._covered_assets())
            value, gap, percent, status = rec._cover_position()
            rec.register_value = value
            rec.coverage_gap = gap
            rec.coverage_gap_percent = percent
            rec.coverage_status = status

    def _compute_review_due(self):
        days = int(float_param(self.env, INSURANCE_REVIEW_DAYS))
        today = fields.Date.context_today(self)
        for rec in self:
            base = rec.last_reviewed_on or rec.approved_on
            due = fields.Date.add(base, days=days) if base and rec.state == "active" else False
            rec.review_due_date = due
            rec.review_overdue = bool(due and due < today)

    @api.constrains("sum_insured", "premium", "period_from", "period_to")
    def _check_terms(self):
        for rec in self:
            if rec.sum_insured <= 0:
                raise ValidationError(self.env._("The sum insured must be above zero."))
            if rec.premium < 0:
                raise ValidationError(self.env._("The premium cannot be negative."))
            if rec.period_to <= rec.period_from:
                raise ValidationError(self.env._("The cover ends before it starts."))

    # ---- workflow --------------------------------------------------------
    def action_activate(self):
        """Put the policy in force: an accounting manager (R26 / R03) who did
        not record it. A renewal closes the policy it replaces."""
        require_group(self.env, MANAGER_GROUP, "Activating an insurance policy")
        for rec in self:
            if rec.state != "draft":
                raise UserError(self.env._("Only a draft policy is put in force."))
            check_sod(self.env, rec.create_uid, rec.display_name, rec)
            if rec.scope == "assets" and not rec.asset_ids:
                raise UserError(self.env._("%s names no asset.", rec.display_name))
            if rec.scope == "category" and not rec.category_ids:
                raise UserError(self.env._("%s names no asset class.", rec.display_name))
            other = rec.asset_ids.filtered(lambda a, c=rec.company_id: a.company_id != c)
            if other:
                raise UserError(
                    self.env._(
                        "%s: %s belong to another company.",
                        rec.display_name,
                        ", ".join(other.mapped("display_name")),
                    )
                )
            old = rec.replaces_id
            if old and (old.state != "active" or old.company_id != rec.company_id):
                raise UserError(
                    self.env._(
                        "%s renews %s, which is not in force in this company.",
                        rec.display_name,
                        old.display_name,
                    )
                )
            rec._guarded().write(
                {
                    "state": "active",
                    "approved_by_id": self.env.uid,
                    "approved_on": fields.Date.context_today(rec),
                }
            )
            if old:
                old._guarded().write({"state": "replaced"})
                old.message_post(body=self.env._("Renewed / replaced by %s.", rec.display_name))
        return True

    def action_record_review(self):
        """BRU-FXA-25: compare the sum insured with the register value now
        and stamp it; a gap above the tolerance needs a note and is reported
        to the CFO (a to-do for each accounting administrator)."""
        require_group(self.env, USER_GROUP, "Reviewing insurance cover")
        for rec in self:
            if rec.state != "active":
                raise UserError(self.env._("Only a policy in force is reviewed."))
            value, gap, percent, status = rec._cover_position()
            if status != "ok" and not (rec.review_note or "").strip():
                raise UserError(
                    self.env._(
                        "%s is %s by %s (%s%% of the register value): write the review note "
                        "(the cause and the action proposed) first.",
                        rec.display_name,
                        dict(self._fields["coverage_status"].selection)[status].lower(),
                        abs(gap),
                        abs(percent),
                    )
                )
            rec._guarded().write(
                {
                    "last_reviewed_on": fields.Date.context_today(rec),
                    "reviewed_by_id": self.env.uid,
                    "reviewed_register_value": value,
                    "reviewed_sum_insured": rec.sum_insured,
                    "reviewed_gap": gap,
                    "gap_reported": status != "ok",
                }
            )
            if status != "ok":
                rec._report_gap(status, gap, percent)
        return True

    def _report_gap(self, status, gap, percent):
        self.ensure_one()
        label = dict(self._fields["coverage_status"].selection)[status]
        summary = self.env._("Insurance coverage gap: %s", self.display_name)
        note = self.env._(
            "%s: %s by %s (%s%% of the register value %s; sum insured %s). Review note: %s",
            self.display_name,
            label,
            abs(gap),
            abs(percent),
            self.reviewed_register_value,
            self.sum_insured,
            self.review_note,
        )
        self.sudo().message_post(body=note)
        group = self.env.ref(MANAGER_GROUP, raise_if_not_found=False)
        users = (
            group.sudo().all_user_ids.filtered(
                lambda u: u.active and not u.share and self.company_id in u.company_ids
            )
            if group
            else self.env["res.users"]
        )
        for user in users:
            self.sudo().activity_schedule(
                "mail.mail_activity_data_todo", summary=summary, note=note, user_id=user.id
            )

    def action_expire(self):
        require_group(self.env, USER_GROUP, "Expiring an insurance policy")
        today = fields.Date.context_today(self)
        for rec in self:
            if rec.state != "active":
                raise UserError(self.env._("Only a policy in force expires."))
            if rec.period_to >= today:
                raise UserError(
                    self.env._(
                        "%s is in force until %s: it expires after that date.",
                        rec.display_name,
                        rec.period_to,
                    )
                )
            rec._guarded().write({"state": "expired"})
        return True

    def action_cancel(self):
        require_group(self.env, MANAGER_GROUP, "Cancelling an insurance policy")
        for rec in self:
            if rec.state not in ("draft", "active"):
                raise UserError(self.env._("Only a draft or in-force policy is cancelled."))
            rec._guarded().write({"state": "cancelled"})
        return True


class FixAssetDisposalInsurance(models.Model):
    """Claim linkage (FR-FXA-034, AUT-FXA-19): a write-off names the policy
    the claim is made under, which must cover the asset."""

    _inherit = "fix.asset.disposal"

    insurance_id = fields.Many2one(
        "fix.asset.insurance",
        string="Insurance Policy",
        tracking=True,
        groups="account.group_account_user",
        domain="[('state', 'in', ('active', 'expired', 'replaced')), "
        "('company_id', '=', company_id)]",
    )

    @api.constrains("insurance_id", "asset_id")
    def _check_insurance_covers(self):
        for rec in self.sudo().filtered("insurance_id"):
            policy = rec.insurance_id
            if policy.state not in ("active", "expired", "replaced"):
                raise ValidationError(self.env._("%s was never in force.", policy.display_name))
            if not policy._covers(rec.asset_id):
                raise ValidationError(
                    self.env._(
                        "%s does not cover %s: name the policy the asset is insured under.",
                        policy.display_name,
                        rec.asset_id.display_name,
                    )
                )
            if rec.date and not policy.period_from <= rec.date <= policy.period_to:
                raise ValidationError(
                    self.env._(
                        "%s covers %s to %s: the loss on %s falls outside it.",
                        policy.display_name,
                        policy.period_from,
                        policy.period_to,
                        rec.date,
                    )
                )
