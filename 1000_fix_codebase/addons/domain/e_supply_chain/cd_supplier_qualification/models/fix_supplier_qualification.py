# cd_supplier_qualification — M42 qualification, the activation gate and
# integrity screening (FR-SRM2-008..015, FR-SRM2-019/020, CD-M42-02).
#
# T-01/T-02: the activation decision is evaluated per (supplier, category,
# company, date) and fails CLOSED. T-03: an approved qualification is
# immutable; re-qualification creates a new version.
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish  # FF-28

from odoo.addons.cd_vendor_ext.models.fix_supplier_profile import (
    G_MANAGER, G_QUALITY, RISK_TIERS, check_sod, require_group)

# Tiers at which the scorer may not be the sole approver (§13 SoD).
STRICT_TIERS = ("high", "critical")


class FixQualificationQuestionnaire(models.Model):
    """FR-SRM2-008: a category- and tier-specific questionnaire template
    with weights, a pass threshold and mandatory criteria."""

    _name = "fix.qualification.questionnaire"
    _description = "Qualification Questionnaire Template"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "name, version desc"

    company_id = fields.Many2one("res.company", string="Company", required=True,
                                 index=True, default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one(
        "operating.unit", string="Operating Unit", index=True,
        default=lambda self: self.env.user._get_default_operating_unit())
    name = fields.Char(string="Questionnaire", required=True)
    category_id = fields.Many2one("product.category", string="Spend Category",
                                  index=True)
    risk_tier = fields.Selection(RISK_TIERS, string="Risk Tier")
    question_ids = fields.One2many("fix.qualification.question", "questionnaire_id",
                                   string="Questions")
    pass_threshold = fields.Float(string="Pass Threshold", default=70.0)
    validity_days = fields.Integer(string="Validity (days)", default=365)
    version = fields.Integer(string="Version", default=1)
    active = fields.Boolean(default=True)

    @api.constrains("pass_threshold", "validity_days")
    def _check_threshold(self):
        for q in self:
            if not 0 <= q.pass_threshold <= 100:
                raise ValidationError("The pass threshold is a 0-100 score")
            if q.validity_days <= 0:
                raise ValidationError("Qualification validity must be positive")


class FixQualificationQuestion(models.Model):
    _name = "fix.qualification.question"
    _description = "Qualification Question"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "sequence, id"

    company_id = fields.Many2one("res.company", string="Company",
                                 related="questionnaire_id.company_id", store=True)
    operating_unit_id = fields.Many2one(
        "operating.unit", string="Operating Unit",
        related="questionnaire_id.operating_unit_id", store=True)
    questionnaire_id = fields.Many2one("fix.qualification.questionnaire",
                                       string="Questionnaire", required=True,
                                       ondelete="cascade", index=True)
    sequence = fields.Integer(default=10)
    question = fields.Text(string="Question", required=True)
    weight = fields.Float(string="Weight", default=1.0)
    mandatory = fields.Boolean(string="Mandatory Criterion")
    evidence_required = fields.Boolean(string="Evidence Required")


class FixSupplierQualification(models.Model):
    """FR-SRM2-008/009/011/012: an immutable, versioned qualification for
    one supplier in one spend category."""

    _name = "fix.supplier.qualification"
    _description = "Supplier Qualification"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "profile_id, category_id, version desc"
    _p03_capture = {
        "module": "M42",
        "form": "Qualification Questionnaire",
        "fields": ["profile_id", "category_id", "questionnaire_id", "responses",
                   "evidence_note", "score", "anti_bribery_declared",
                   "code_of_conduct_version"],
    }
    _version_unique = models.Constraint(
        "UNIQUE (profile_id, category_id, company_id, version)",
        "One qualification version per supplier, category and entity (T-03)")

    company_id = fields.Many2one("res.company", string="Company", required=True,
                                 index=True, default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one(
        "operating.unit", string="Operating Unit", index=True,
        default=lambda self: self.env.user._get_default_operating_unit())
    profile_id = fields.Many2one("fix.supplier.profile", string="Supplier",
                                 required=True, index=True, ondelete="restrict")
    category_id = fields.Many2one("product.category", string="Spend Category",
                                  required=True, index=True)
    questionnaire_id = fields.Many2one("fix.qualification.questionnaire",
                                       string="Questionnaire")
    version = fields.Integer(string="Version", readonly=True, copy=False)
    responses = fields.Text(string="Questionnaire Responses", required=True)
    evidence_note = fields.Text(string="Evidence Provided")
    score = fields.Float(string="Score", required=True)
    threshold = fields.Float(string="Pass Threshold", compute="_compute_result",
                             store=True)
    result = fields.Selection([("pass", "Pass"), ("fail", "Fail")], string="Result",
                              compute="_compute_result", store=True)
    anti_bribery_declared = fields.Boolean(string="Anti-Bribery Declaration Signed")
    code_of_conduct_version = fields.Char(string="Code of Conduct Version Accepted")
    scored_by = fields.Many2one("res.users", string="Scored By",
                                default=lambda self: self.env.user, readonly=True)
    approved_by = fields.Many2one("res.users", string="Approved By", readonly=True)
    approved_at = fields.Datetime(string="Approved At", readonly=True)
    valid_from = fields.Date(string="Valid From", readonly=True)
    valid_until = fields.Date(string="Valid Until", readonly=True, index=True)
    state = fields.Selection(
        [("draft", "Draft"), ("submitted", "Submitted"), ("approved", "Approved"),
         ("rejected", "Rejected"), ("expired", "Expired"),
         ("superseded", "Superseded")],
        string="Status", default="draft", required=True, tracking=True)

    _IMMUTABLE = {"profile_id", "category_id", "questionnaire_id", "responses",
                  "evidence_note", "score", "anti_bribery_declared",
                  "code_of_conduct_version", "scored_by", "approved_by",
                  "approved_at", "valid_from", "valid_until", "version"}

    @api.depends("score", "questionnaire_id.pass_threshold")
    def _compute_result(self):
        for qual in self:
            threshold = qual.questionnaire_id.pass_threshold if qual.questionnaire_id else 70.0
            qual.threshold = threshold
            qual.result = "pass" if qual.score >= threshold else "fail"

    @api.constrains("score")
    def _check_score(self):
        for qual in self:
            if not 0 <= qual.score <= 100:
                raise ValidationError("The qualification score is 0-100")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            prior = self.search([
                ("profile_id", "=", vals.get("profile_id")),
                ("category_id", "=", vals.get("category_id")),
                ("company_id", "=", vals.get("company_id", self.env.company.id)),
            ], order="version desc", limit=1)
            vals["version"] = (prior.version or 0) + 1
        quals = super().create(vals_list)
        quals.mapped("profile_id").action_start_qualification()
        return quals

    def write(self, vals):
        if self._IMMUTABLE & set(vals) and any(
                q.state in ("approved", "expired", "superseded") for q in self):
            raise UserError("An approved qualification is immutable; "
                            "re-qualify with a new version (T-03)")
        return super().write(vals)

    def action_submit(self):
        for qual in self:
            if qual.state != "draft":
                raise UserError("Only a draft qualification can be submitted")
            if not qual.anti_bribery_declared:
                raise UserError("The anti-bribery declaration is a qualification "
                                "condition (FR-SRM2-019)")
        self.write({"state": "submitted"})

    def action_approve(self):
        """FR-SRM2-009: approved by the Quality Manager or Procurement
        Manager (the manager group implies quality)."""
        require_group(self.env, G_QUALITY, "Only the Quality Manager or "
                      "Procurement Manager can approve a qualification")
        for qual in self:
            if qual.state != "submitted":
                raise UserError("Only a submitted qualification can be approved")
            if qual.result != "pass":
                raise UserError("A failing qualification cannot be approved")
            if qual.profile_id.risk_tier in STRICT_TIERS:
                check_sod(qual, "scored_by", self.env.user,
                          "At high and critical tiers the scorer cannot be the "
                          "sole approver")
            validity = qual.questionnaire_id.validity_days or 365
            today = fields.Date.today()
            # Locked fields are set through the ORM super-write path.
            super(FixSupplierQualification, qual).write({
                "state": "approved", "approved_by": self.env.user.id,
                "approved_at": fields.Datetime.now(), "valid_from": today,
                "valid_until": today + timedelta(days=validity)})
            older = self.search([
                ("id", "!=", qual.id), ("profile_id", "=", qual.profile_id.id),
                ("category_id", "=", qual.category_id.id),
                ("company_id", "=", qual.company_id.id), ("state", "=", "approved")])
            super(FixSupplierQualification, older).write({"state": "superseded"})
            if qual.category_id not in qual.profile_id.category_ids:
                qual.profile_id.category_ids = [(4, qual.category_id.id)]
            if qual.profile_id.state in ("prospect", "under_qualification", "suspended"):
                qual.profile_id._activate()
            publish(self.env, "supplier.qualified", "fix.supplier.qualification",
                    qual.id, {"profile_id": qual.profile_id.id,
                              "category_id": qual.category_id.id,
                              "company_id": qual.company_id.id,
                              "valid_until": str(qual.valid_until)})

    def action_reject(self):
        require_group(self.env, G_QUALITY, "Only the Quality Manager or "
                      "Procurement Manager can reject a qualification")
        for qual in self:
            if qual.state != "submitted":
                raise UserError("Only a submitted qualification can be rejected")
        self.write({"state": "rejected"})

    @api.model
    def check_activation(self, partner_id, category_id, company_id=None, on_date=None):
        """FR-SRM2-010 / T-01 / T-02: the synchronous decision M16 calls
        before any purchase order. Returns {"allow": bool, "reason": str}.
        Fails CLOSED: any missing or doubtful input denies."""
        try:
            company_id = company_id or self.env.company.id
            on_date = fields.Date.to_date(on_date) if on_date else fields.Date.today()
            profile = self.env["fix.supplier.profile"].search([
                ("partner_id", "=", int(partner_id)),
                ("company_id", "=", int(company_id))], limit=1)
            if not profile:
                return {"allow": False, "reason": "no supplier profile for this entity"}
            if profile.state != "active":
                return {"allow": False, "reason": f"supplier is {profile.state}"}
            qual = self.search([
                ("profile_id", "=", profile.id), ("category_id", "=", int(category_id)),
                ("company_id", "=", int(company_id)), ("state", "=", "approved"),
                ("valid_from", "<=", on_date), ("valid_until", ">=", on_date)], limit=1)
            if not qual:
                return {"allow": False,
                        "reason": "no valid qualification for this category"}
            return {"allow": True, "reason": f"qualified v{qual.version} "
                                             f"until {qual.valid_until}"}
        except Exception as exc:  # T-01: fail closed, never permit on error
            return {"allow": False, "reason": f"activation check failed: {exc}"}

    @api.model
    def _cron_expire_qualifications(self):
        """FR-SRM2-011: de-activate automatically on lapse — a supplier with
        no remaining valid qualification is suspended."""
        today = fields.Date.today()
        lapsed = self.search([("state", "=", "approved"), ("valid_until", "<", today)])
        super(FixSupplierQualification, lapsed).write({"state": "expired"})
        for profile in lapsed.mapped("profile_id"):
            still_valid = self.search_count([
                ("profile_id", "=", profile.id), ("state", "=", "approved"),
                ("valid_until", ">=", today)])
            if not still_valid and profile.state == "active":
                profile.action_suspend(reason="Qualification lapsed (FR-SRM2-011)")
        return len(lapsed)


class FixSupplierScreening(models.Model):
    """FR-SRM2-019/020: sanctions, conflict-of-interest and related-party
    screening with the anti-bribery and code-of-conduct declarations."""

    _name = "fix.supplier.screening"
    _description = "Supplier Integrity Screening"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "screened_on desc, id desc"
    _p03_capture = {
        "module": "M42",
        "form": "Integrity Screening Declaration",
        "fields": ["profile_id", "screened_on", "sanctions_result", "sanctions_source",
                   "coi_declared", "coi_details", "related_party",
                   "anti_bribery_declared", "code_of_conduct_accepted",
                   "code_of_conduct_version"],
    }

    company_id = fields.Many2one("res.company", string="Company", required=True,
                                 index=True, default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one(
        "operating.unit", string="Operating Unit", index=True,
        default=lambda self: self.env.user._get_default_operating_unit())
    profile_id = fields.Many2one("fix.supplier.profile", string="Supplier",
                                 required=True, index=True, ondelete="cascade")
    screened_on = fields.Date(string="Screened On", required=True,
                              default=fields.Date.today)
    sanctions_result = fields.Selection(
        [("clear", "Clear"), ("potential_match", "Potential Match"),
         ("confirmed_match", "Confirmed Match")],
        string="Sanctions Result", required=True, default="clear")
    sanctions_source = fields.Char(string="Sanctions List(s) Checked")
    coi_declared = fields.Boolean(string="Conflict of Interest Declared")
    coi_details = fields.Text(string="Conflict of Interest Details")
    related_party = fields.Boolean(string="Related Party")
    anti_bribery_declared = fields.Boolean(string="Anti-Bribery Declaration Signed")
    code_of_conduct_accepted = fields.Boolean(string="Code of Conduct Accepted")
    code_of_conduct_version = fields.Char(string="Code of Conduct Version")
    outcome = fields.Selection(
        [("clear", "Clear"), ("review", "Needs Review"), ("fail", "Fail")],
        string="Outcome", compute="_compute_outcome", store=True)
    reviewed_by = fields.Many2one("res.users", string="Reviewed By", readonly=True)
    review_note = fields.Text(string="Review Note")
    state = fields.Selection(
        [("draft", "Draft"), ("submitted", "Submitted"), ("cleared", "Cleared"),
         ("escalated", "Escalated")],
        string="Status", default="draft", required=True, tracking=True)

    @api.depends("sanctions_result", "coi_declared", "related_party",
                 "anti_bribery_declared")
    def _compute_outcome(self):
        for s in self:
            if s.sanctions_result == "confirmed_match" or not s.anti_bribery_declared:
                s.outcome = "fail"
            elif s.sanctions_result == "potential_match" or s.coi_declared or s.related_party:
                s.outcome = "review"
            else:
                s.outcome = "clear"

    @api.constrains("coi_declared", "coi_details", "code_of_conduct_accepted",
                    "code_of_conduct_version")
    def _check_declarations(self):
        for s in self:
            if s.coi_declared and not (s.coi_details or "").strip():
                raise ValidationError("A declared conflict of interest needs details")
            if s.code_of_conduct_accepted and not s.code_of_conduct_version:
                raise ValidationError("Record which code-of-conduct version was "
                                      "accepted (FR-SRM2-020)")

    def action_submit(self):
        self.filtered(lambda s: s.state == "draft").write({"state": "submitted"})

    def action_clear(self):
        require_group(self.env, G_MANAGER,
                      "Only a Procurement Manager can clear a screening")
        for s in self:
            if s.state != "submitted":
                raise UserError("Only a submitted screening can be cleared")
            if s.outcome == "fail":
                raise UserError("A failing screening cannot be cleared; escalate it")
            check_sod(s, "create_uid", self.env.user,
                      "The user who captured a screening cannot clear it")
        self.write({"state": "cleared", "reviewed_by": self.env.user.id})

    def action_escalate(self):
        self.filtered(lambda s: s.state == "submitted").write(
            {"state": "escalated", "reviewed_by": self.env.user.id})
        for s in self:
            publish(self.env, "supplier.screening_escalated", "fix.supplier.screening",
                    s.id, {"profile_id": s.profile_id.id, "outcome": s.outcome})
