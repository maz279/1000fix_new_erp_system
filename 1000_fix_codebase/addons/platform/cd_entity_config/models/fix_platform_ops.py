# fix_platform_ops — M30 (announcements), M64 (MDM: steward/DQ/code lists),
# M65 (locale packs, jurisdiction rules). Branch/entity/config/feature-flag/
# country-pack models live in the sibling files of this module.
from odoo import api, fields, models
from odoo.exceptions import UserError


class FixPlatformAnnouncement(models.Model):
    _name = "fix.platform.announcement"
    _description = "Platform Announcement"
    _order = "publish_on desc, id desc"

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    severity = fields.Selection(
        [("info", "Information"), ("warning", "Warning"), ("critical", "Critical")],
        required=True,
        default="info",
    )
    body = fields.Text()
    publish_on = fields.Date(required=True, default=fields.Date.context_today)
    expires_on = fields.Date()
    audience = fields.Selection(
        [("all", "All users"), ("internal", "Internal only"), ("technicians", "Field technicians")],
        required=True,
        default="all",
    )
    state = fields.Selection(
        [("draft", "Draft"), ("published", "Published"), ("retired", "Retired")],
        required=True,
        default="draft",
    )

    def action_publish(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError("Publish a draft announcement")
            rec.state = "published"

    def action_retire(self):
        for rec in self:
            rec.state = "retired"


class FixMdmSteward(models.Model):
    _name = "fix.mdm.steward"
    _description = "Data Steward Request"
    _order = "created_at desc, id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    request_type = fields.Selection(
        [
            ("create", "Create Record"),
            ("update", "Update Record"),
            ("merge", "Merge Duplicates"),
            ("deactivate", "Deactivate"),
        ],
        required=True,
        default="update",
    )
    res_model = fields.Char(string="Master Model", required=True, index=True)
    record_ref = fields.Char(string="Record Reference")
    reason = fields.Text(required=True)
    requested_by_id = fields.Many2one("hr.employee", string="Requested By")
    steward_id = fields.Many2one("hr.employee", string="Assigned Steward", index=True)
    created_at = fields.Datetime(required=True, default=fields.Datetime.now)
    decided_at = fields.Datetime()
    decision_note = fields.Char()
    state = fields.Selection(
        [
            ("submitted", "Submitted"),
            ("in_review", "In Review"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
        ],
        required=True,
        default="submitted",
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.mdm.steward") or "STE/New"
        return super().create(vals_list)

    def action_review(self):
        for rec in self:
            if rec.state != "submitted":
                raise UserError("Review a submitted request")
            rec.state = "in_review"

    def action_approve(self):
        for rec in self:
            if rec.state != "in_review":
                raise UserError("Approve a request in review")
            rec.write({"state": "approved", "decided_at": fields.Datetime.now()})

    def action_reject(self):
        for rec in self:
            if rec.state != "in_review":
                raise UserError("Reject a request in review")
            rec.write({"state": "rejected", "decided_at": fields.Datetime.now()})


class FixMdmDqRule(models.Model):
    _name = "fix.mdm.dq.rule"
    _description = "Data Quality Rule"
    _order = "code"

    code = fields.Char(required=True)
    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    res_model = fields.Char(string="Master Model", required=True)
    field_name = fields.Char(required=True)
    rule_type = fields.Selection(
        [
            ("completeness", "Completeness"),
            ("uniqueness", "Uniqueness"),
            ("format", "Format"),
            ("range", "Range"),
            ("referential", "Referential"),
        ],
        required=True,
        default="completeness",
    )
    expression = fields.Char(required=True, help="The checked condition, e.g. 'not null'")
    severity = fields.Selection(
        [("critical", "Critical"), ("major", "Major"), ("minor", "Minor")],
        required=True,
        default="major",
    )
    active = fields.Boolean(default=True)

    _code_unique = models.Constraint(
        "UNIQUE (code, company_id)", "A DQ rule code is unique per company"
    )


class FixMdmCodeList(models.Model):
    _name = "fix.mdm.code.list"
    _description = "Governed Code List"
    _order = "code"

    code = fields.Char(required=True)
    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    domain_area = fields.Char(string="Domain (e.g. currency, country, unit)")
    state = fields.Selection(
        [("draft", "Draft"), ("published", "Published"), ("retired", "Retired")],
        required=True,
        default="draft",
    )
    entry_ids = fields.One2many("fix.mdm.code.entry", "list_id", string="Entries")

    def action_publish(self):
        for rec in self:
            rec.state = "published"


class FixMdmCodeEntry(models.Model):
    _name = "fix.mdm.code.entry"
    _description = "Code List Entry"
    _order = "list_id, value"

    list_id = fields.Many2one("fix.mdm.code.list", required=True, ondelete="cascade", index=True)
    company_id = fields.Many2one(related="list_id.company_id", store=True, index=True)
    value = fields.Char(required=True)
    label = fields.Char(required=True)
    label_bn = fields.Char(string="Label (Bengali)")
    active = fields.Boolean(default=True)

    _value_unique = models.Constraint(
        "UNIQUE (list_id, value)", "A code value is unique inside its list"
    )


class FixLocalePack(models.Model):
    _name = "fix.locale.pack"
    _description = "Locale Pack"
    _order = "code"

    code = fields.Char(required=True, help="e.g. bn_BD, en_US")
    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    number_format = fields.Selection(
        [("en_in", "Indian grouping (1,00,000)"), ("en_us", "Western grouping (100,000)")],
        default="en_in",
        required=True,
    )
    first_day_of_week = fields.Selection(
        [("6", "Saturday"), ("0", "Monday")],
        default="6",
        required=True,
        string="First Day of Week",
    )
    date_format = fields.Char(default="DD/MM/YYYY", required=True)
    coverage_pct = fields.Integer(
        string="Translation Coverage %",
        help="Measured coverage of the pack against the source strings.",
    )
    state = fields.Selection(
        [("draft", "Draft"), ("active", "Active"), ("retired", "Retired")],
        required=True,
        default="draft",
    )

    _code_unique = models.Constraint(
        "UNIQUE (code, company_id)", "A locale code is unique per company"
    )

    def action_activate(self):
        for rec in self:
            rec.state = "active"


class FixJurisdictionRule(models.Model):
    _name = "fix.jurisdiction.rule"
    _description = "Jurisdiction Rule"
    _order = "jurisdiction"

    jurisdiction = fields.Char(required=True, help="e.g. BD-NBR, BD-DIFE, City Corporation")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    rule_area = fields.Selection(
        [
            ("tax", "Tax"),
            ("labour", "Labour"),
            ("fire", "Fire Safety"),
            ("environment", "Environment"),
            ("data", "Data Protection"),
        ],
        required=True,
        default="tax",
    )
    requirement = fields.Char(required=True)
    frequency = fields.Selection(
        [
            ("monthly", "Monthly"),
            ("quarterly", "Quarterly"),
            ("annual", "Annual"),
            ("event", "Event-Driven"),
        ],
        required=True,
        default="annual",
    )
    authority = fields.Char()
    penalty = fields.Char(string="Penalty for Non-Compliance")
    active = fields.Boolean(default=True)
