# fix_supplier — M42: the supplier register and its governance records. The
# vendor portal module owns the supplier subject (it already depends on the
# requisition module), so the models live here and M16 reads the activation
# state through the supplier record.
from odoo import api, fields, models
from odoo.exceptions import UserError

MANDATORY_DOCS = ("trade_licence", "tin", "vat")


class FixSupplier(models.Model):
    _name = "fix.supplier"
    _description = "Supplier"
    _order = "name"

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    partner_id = fields.Many2one(
        "res.partner", string="Contact", required=True, ondelete="restrict", index=True
    )
    supplier_code = fields.Char(required=True, default="New", copy=False)
    segment = fields.Selection(
        [
            ("strategic", "Strategic"),
            ("preferred", "Preferred"),
            ("transactional", "Transactional"),
            ("probationary", "Probationary"),
        ],
        required=True,
        default="transactional",
    )
    category = fields.Char(string="Spend Category")
    buyer_id = fields.Many2one("hr.employee", string="Buyer")
    onboarded_on = fields.Date()
    status = fields.Selection(
        [
            ("prospect", "Prospect"),
            ("qualified", "Qualified"),
            ("active", "Active"),
            ("suspended", "Suspended"),
            ("deactivated", "Deactivated"),
        ],
        required=True,
        default="prospect",
        index=True,
    )
    notes = fields.Text()

    _partner_unique = models.Constraint("UNIQUE (partner_id)", "One supplier record per partner")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("supplier_code", "New") == "New":
                vals["supplier_code"] = (
                    self.env["ir.sequence"].next_by_code("fix.supplier") or "SUP/New"
                )
        return super().create(vals_list)


class FixSupplierDocument(models.Model):
    _name = "fix.supplier.document"
    _description = "Supplier Document"
    _order = "valid_to desc, id desc"

    name = fields.Char(required=True, default="New")
    supplier_id = fields.Many2one(
        "fix.supplier", string="Supplier", required=True, ondelete="cascade", index=True
    )
    doc_type = fields.Selection(
        [
            ("trade_licence", "Trade Licence"),
            ("tin", "TIN Certificate"),
            ("vat", "VAT Registration"),
            ("iso", "ISO Certificate"),
            ("insurance", "Insurance"),
            ("bank", "Bank Details"),
            ("contract", "Signed Contract"),
            ("other", "Other"),
        ],
        required=True,
        default="trade_licence",
    )
    number = fields.Char(string="Document Number")
    valid_from = fields.Date()
    valid_to = fields.Date()
    file_ref = fields.Char(string="File Reference")
    state = fields.Selection(
        [("valid", "Valid"), ("pending", "Pending"), ("expired", "Expired")],
        required=True,
        default="pending",
    )

    @api.depends("state", "valid_to")
    def _compute_is_valid(self):
        today = fields.Date.context_today(self)
        for rec in self:
            rec.is_valid = bool(
                rec.state == "valid" and (not rec.valid_to or rec.valid_to >= today)
            )

    is_valid = fields.Boolean(compute="_compute_is_valid", store=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.supplier.document") or "SDOC/New"
                )
        return super().create(vals_list)


class FixSupplierQualification(models.Model):
    _name = "fix.supplier.qualification"
    _description = "Supplier Qualification"
    _order = "create_date desc, id desc"

    name = fields.Char(required=True, default="New")
    supplier_id = fields.Many2one(
        "fix.supplier", string="Supplier", required=True, ondelete="cascade", index=True
    )
    stage = fields.Selection(
        [
            ("documents", "Documents"),
            ("site_audit", "Site Audit"),
            ("sample_approval", "Sample Approval"),
            ("finance", "Finance Review"),
            ("activation", "Activation"),
        ],
        required=True,
        default="documents",
    )
    submitted_on = fields.Date(required=True, default=fields.Date.context_today)
    auditor_id = fields.Many2one("hr.employee", string="Auditor")
    score = fields.Float(string="Score (0–100)")
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("in_review", "In Review"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
        ],
        required=True,
        default="draft",
    )
    approved_on = fields.Date()
    notes = fields.Text()

    _score_range = models.Constraint(
        "CHECK (score >= 0 AND score <= 100)", "The score is a 0–100 value"
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.supplier.qualification")
                    or "SQUAL/New"
                )
        return super().create(vals_list)

    def action_start(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError("Start a draft qualification")
            rec.state = "in_review"

    def action_approve(self):
        for rec in self:
            if rec.state != "in_review":
                raise UserError("Approve a qualification in review")
            rec.write({"state": "approved", "approved_on": fields.Date.context_today(self)})
            if rec.supplier_id.status == "prospect":
                rec.supplier_id.status = "qualified"

    def action_reject(self):
        for rec in self:
            rec.state = "rejected"


class FixSupplierActivation(models.Model):
    """The activation gate: a supplier goes active only when the qualification
    is approved AND every mandatory document is valid today."""

    _name = "fix.supplier.activation"
    _description = "Supplier Activation Gate"
    _order = "create_date desc, id desc"

    name = fields.Char(required=True, default="New")
    supplier_id = fields.Many2one(
        "fix.supplier", string="Supplier", required=True, ondelete="cascade", index=True
    )
    qualification_id = fields.Many2one(
        "fix.supplier.qualification", string="Qualification", ondelete="set null"
    )
    activated_on = fields.Date()
    state = fields.Selection(
        [("draft", "Draft"), ("activated", "Activated"), ("blocked", "Blocked")],
        required=True,
        default="draft",
    )
    blocker = fields.Char()

    def _blockers(self):
        self.ensure_one()
        problems = []
        supplier = self.supplier_id
        if not self.qualification_id or self.qualification_id.state != "approved":
            problems.append("no approved qualification")
        docs = self.env["fix.supplier.document"].search([("supplier_id", "=", supplier.id)])
        for doc_type in MANDATORY_DOCS:
            doc = docs.filtered(lambda d, t=doc_type: d.doc_type == t and d.is_valid)
            if not doc:
                problems.append("no valid %s" % doc_type)
        return problems

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.supplier.activation") or "SACT/New"
                )
        return super().create(vals_list)

    def action_activate(self):
        for rec in self:
            problems = rec._blockers()
            if problems:
                rec.write({"state": "blocked", "blocker": ", ".join(problems)})
                raise UserError("Activation blocked: %s" % ", ".join(problems))
            rec.write(
                {
                    "state": "activated",
                    "activated_on": fields.Date.context_today(self),
                    "blocker": False,
                }
            )
            rec.supplier_id.status = "active"


class FixSupplierRequalification(models.Model):
    _name = "fix.supplier.requalification"
    _description = "Supplier Re-Qualification"
    _order = "due_on desc, id desc"

    name = fields.Char(required=True, default="New")
    supplier_id = fields.Many2one(
        "fix.supplier", string="Supplier", required=True, ondelete="cascade", index=True
    )
    due_on = fields.Date(required=True)
    completed_on = fields.Date()
    outcome = fields.Selection([("pass", "Pass"), ("conditional", "Conditional"), ("fail", "Fail")])
    state = fields.Selection(
        [("due", "Due"), ("scheduled", "Scheduled"), ("done", "Done")],
        required=True,
        default="due",
    )
    notes = fields.Char()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.supplier.requalification")
                    or "SREQ/New"
                )
        return super().create(vals_list)

    def action_complete(self):
        for rec in self:
            if rec.state == "done":
                raise UserError("This re-qualification is already complete")
            if not rec.outcome:
                raise UserError("Record the outcome before completing the re-qualification")
            rec.write({"state": "done", "completed_on": fields.Date.context_today(self)})


class FixSupplierScorecard(models.Model):
    _name = "fix.supplier.performance"
    _description = "Supplier Scorecard"
    _order = "period desc, id desc"

    name = fields.Char(required=True, default="New")
    supplier_id = fields.Many2one(
        "fix.supplier", string="Supplier", required=True, ondelete="cascade", index=True
    )
    period = fields.Char(required=True, help="YYYY-MM")
    quality_score = fields.Float(string="Quality (0–100)", default=0.0)
    delivery_score = fields.Float(string="Delivery (0–100)", default=0.0)
    cost_score = fields.Float(string="Cost (0–100)", default=0.0)
    responsiveness_score = fields.Float(string="Responsiveness (0–100)", default=0.0)
    total_score = fields.Float(compute="_compute_total", store=True, string="Total")
    grade = fields.Selection(
        [("a", "A"), ("b", "B"), ("c", "C"), ("d", "D")],
        compute="_compute_total",
        store=True,
        string="Grade",
    )
    reviewed_on = fields.Date(required=True, default=fields.Date.context_today)
    state = fields.Selection(
        [("draft", "Draft"), ("published", "Published")], required=True, default="draft"
    )

    _scores_range = models.Constraint(
        "CHECK (quality_score >= 0 AND quality_score <= 100 AND delivery_score >= 0 "
        "AND delivery_score <= 100 AND cost_score >= 0 AND cost_score <= 100 "
        "AND responsiveness_score >= 0 AND responsiveness_score <= 100)",
        "Scorecard components are 0–100 values",
    )

    @api.depends("quality_score", "delivery_score", "cost_score", "responsiveness_score")
    def _compute_total(self):
        for rec in self:
            total = (
                (rec.quality_score or 0.0) * 0.35
                + (rec.delivery_score or 0.0) * 0.30
                + (rec.cost_score or 0.0) * 0.20
                + (rec.responsiveness_score or 0.0) * 0.15
            )
            rec.total_score = round(total, 1)
            rec.grade = (
                "a" if total >= 85 else ("b" if total >= 70 else ("c" if total >= 55 else "d"))
            )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.supplier.performance") or "SPERF/New"
                )
        return super().create(vals_list)

    def action_publish(self):
        for rec in self:
            rec.state = "published"


class FixSupplierCar(models.Model):
    _name = "fix.supplier.car"
    _description = "Corrective Action Request"
    _order = "due_date desc, id desc"

    name = fields.Char(required=True, default="New")
    supplier_id = fields.Many2one(
        "fix.supplier", string="Supplier", required=True, ondelete="cascade", index=True
    )
    issue = fields.Char(required=True)
    root_cause = fields.Text()
    action_plan = fields.Text()
    severity = fields.Selection(
        [("minor", "Minor"), ("major", "Major"), ("critical", "Critical")],
        required=True,
        default="major",
    )
    raised_on = fields.Date(required=True, default=fields.Date.context_today)
    due_date = fields.Date(required=True)
    closed_on = fields.Date()
    state = fields.Selection(
        [("open", "Open"), ("actioned", "Actioned"), ("closed", "Closed")],
        required=True,
        default="open",
    )
    is_overdue = fields.Boolean(compute="_compute_overdue", store=True)

    @api.depends("due_date", "state")
    def _compute_overdue(self):
        today = fields.Date.context_today(self)
        for rec in self:
            rec.is_overdue = bool(rec.due_date and rec.state != "closed" and rec.due_date < today)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.supplier.car") or "SCAR/New"
                )
        return super().create(vals_list)

    def action_action(self):
        for rec in self:
            if not rec.action_plan:
                raise UserError("Record the action plan before marking it actioned")
            rec.state = "actioned"

    def action_close(self):
        for rec in self:
            if rec.state != "actioned":
                raise UserError("Close an actioned CAR")
            rec.write({"state": "closed", "closed_on": fields.Date.context_today(self)})


class FixSupplierReview(models.Model):
    _name = "fix.supplier.review"
    _description = "Supplier Review"
    _order = "review_date desc, id desc"

    name = fields.Char(required=True, default="New")
    supplier_id = fields.Many2one(
        "fix.supplier", string="Supplier", required=True, ondelete="cascade", index=True
    )
    review_type = fields.Selection(
        [("quarterly", "Quarterly"), ("annual", "Annual")],
        required=True,
        default="quarterly",
    )
    review_date = fields.Date(required=True, default=fields.Date.context_today)
    attendees = fields.Char()
    outcomes = fields.Text()
    state = fields.Selection(
        [("scheduled", "Scheduled"), ("done", "Done")], required=True, default="scheduled"
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.supplier.review") or "SRVW/New"
                )
        return super().create(vals_list)

    def action_complete(self):
        for rec in self:
            if rec.state != "scheduled":
                raise UserError("Complete a scheduled review")
            rec.state = "done"


class FixSupplierRisk(models.Model):
    _name = "fix.supplier.risk"
    _description = "Supplier Risk Assessment"
    _order = "assessed_on desc, id desc"

    name = fields.Char(required=True, default="New")
    supplier_id = fields.Many2one(
        "fix.supplier", string="Supplier", required=True, ondelete="cascade", index=True
    )
    risk_type = fields.Selection(
        [
            ("financial", "Financial"),
            ("operational", "Operational"),
            ("geographic", "Geographic"),
            ("compliance", "Compliance"),
            ("quality", "Quality"),
        ],
        required=True,
        default="quality",
    )
    likelihood = fields.Integer(default=3)
    impact = fields.Integer(default=3)
    risk_score = fields.Integer(compute="_compute_score", store=True)
    band = fields.Selection(
        [("low", "Low"), ("medium", "Medium"), ("high", "High"), ("critical", "Critical")],
        compute="_compute_score",
        store=True,
    )
    mitigation = fields.Text()
    assessed_on = fields.Date(required=True, default=fields.Date.context_today)
    state = fields.Selection(
        [("open", "Open"), ("mitigated", "Mitigated")], required=True, default="open"
    )

    _factors_range = models.Constraint(
        "CHECK (likelihood >= 1 AND likelihood <= 5 AND impact >= 1 AND impact <= 5)",
        "Likelihood and impact are 1–5",
    )

    @api.depends("likelihood", "impact")
    def _compute_score(self):
        for rec in self:
            score = (rec.likelihood or 0) * (rec.impact or 0)
            rec.risk_score = score
            rec.band = (
                "critical"
                if score >= 20
                else ("high" if score >= 12 else ("medium" if score >= 6 else "low"))
            )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.supplier.risk") or "SRISK/New"
                )
        return super().create(vals_list)

    def action_mitigate(self):
        for rec in self:
            if not rec.mitigation:
                raise UserError("Record the mitigation before closing the risk")
            rec.state = "mitigated"


class FixSupplierScreening(models.Model):
    _name = "fix.supplier.screening"
    _description = "Supplier Compliance Screening"
    _order = "screened_on desc, id desc"

    name = fields.Char(required=True, default="New")
    supplier_id = fields.Many2one(
        "fix.supplier", string="Supplier", required=True, ondelete="cascade", index=True
    )
    screening_type = fields.Selection(
        [
            ("sanctions", "Sanctions List"),
            ("coi", "Conflict of Interest"),
            ("abac", "Anti-Bribery / ABAC"),
            ("pep", "PEP Check"),
        ],
        required=True,
        default="sanctions",
    )
    result = fields.Selection(
        [("clear", "Clear"), ("hit", "Hit"), ("pending", "Pending")],
        required=True,
        default="pending",
    )
    screened_on = fields.Date(required=True, default=fields.Date.context_today)
    reference = fields.Char()
    state = fields.Selection(
        [("pending", "Pending"), ("cleared", "Cleared"), ("flagged", "Flagged")],
        required=True,
        default="pending",
    )
    notes = fields.Char()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.supplier.screening") or "SSCRN/New"
                )
        return super().create(vals_list)

    def action_clear(self):
        for rec in self:
            if rec.result == "hit":
                raise UserError("A screening hit cannot be cleared")
            if rec.result != "clear":
                raise UserError("Record a clear result before clearing the screening")
            rec.state = "cleared"

    def action_flag(self):
        for rec in self:
            rec.state = "flagged"
