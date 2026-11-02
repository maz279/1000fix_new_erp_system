# M62 Data Platform & Governance — pipelines, runs, contracts, metrics and the
# quality/observability surface. The entity, lineage and quality-rule models live
# in fix_metric_registry.py; this file adds the execution side.
from odoo import api, fields, models
from odoo.exceptions import UserError


class FixDataPipeline(models.Model):
    _name = "fix.data.pipeline"
    _description = "Data Ingestion Pipeline"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "code"

    code = fields.Char(required=True, index=True)
    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    source_system = fields.Char(required=True, help="e.g. odoo_fix, bKash settlement SFTP")
    target_entity_id = fields.Many2one("fix.data.entity", string="Target Entity", required=True)
    load_mode = fields.Selection(
        [
            ("cdc", "CDC (change data capture)"),
            ("full", "Full load"),
            ("incremental", "Incremental (watermark)"),
        ],
        required=True,
        default="cdc",
    )
    schedule = fields.Selection(
        [
            ("realtime", "Real-time"),
            ("hourly", "Hourly"),
            ("daily", "Daily"),
            ("weekly", "Weekly"),
            ("manual", "Manual"),
        ],
        required=True,
        default="daily",
    )
    freshness_sla_minutes = fields.Integer(string="Freshness SLO (minutes)", default=60)
    last_run_at = fields.Datetime(readonly=True)
    last_success_at = fields.Datetime(readonly=True)
    state = fields.Selection(
        [("active", "Active"), ("paused", "Paused"), ("retired", "Retired")],
        required=True,
        default="active",
        tracking=True,
    )

    _code_unique = models.Constraint(
        "UNIQUE (code, company_id)", "Pipeline code is unique per company"
    )

    def action_pause(self):
        for rec in self:
            rec.state = "paused"

    def action_resume(self):
        for rec in self:
            rec.state = "active"


class FixDataRun(models.Model):
    _name = "fix.data.run"
    _description = "Data Pipeline Run"
    _order = "started_at desc, id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    pipeline_id = fields.Many2one(
        "fix.data.pipeline", string="Pipeline", required=True, ondelete="cascade", index=True
    )
    kind = fields.Selection(
        [("scheduled", "Scheduled"), ("backfill", "Backfill"), ("replay", "Replay")],
        required=True,
        default="scheduled",
    )
    stage = fields.Selection(
        [("bronze", "Bronze (raw)"), ("silver", "Silver (conformed)"), ("gold", "Gold (serving)")],
        required=True,
        default="bronze",
        help="The medallion layer this run lands in.",
    )
    started_at = fields.Datetime(required=True, default=fields.Datetime.now)
    finished_at = fields.Datetime()
    duration_minutes = fields.Float(readonly=True)
    rows_read = fields.Integer()
    rows_written = fields.Integer()
    rows_rejected = fields.Integer()
    state = fields.Selection(
        [("running", "Running"), ("succeeded", "Succeeded"), ("failed", "Failed")],
        required=True,
        default="running",
        index=True,
    )
    failure_reason = fields.Char()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.data.run") or "RUN/New"
        return super().create(vals_list)

    def action_finish(self):
        for rec in self:
            if rec.state != "running":
                raise UserError("Only a running load can be finished")
            now = fields.Datetime.now()
            minutes = 0.0
            if rec.started_at:
                minutes = round((now - rec.started_at).total_seconds() / 60.0, 2)
            rec.write({"state": "succeeded", "finished_at": now, "duration_minutes": minutes})
            rec.pipeline_id.write({"last_run_at": now, "last_success_at": now})

    def action_fail(self):
        for rec in self:
            if rec.state != "running":
                raise UserError("Only a running load can fail")
            now = fields.Datetime.now()
            minutes = 0.0
            if rec.started_at:
                minutes = round((now - rec.started_at).total_seconds() / 60.0, 2)
            rec.write({"state": "failed", "finished_at": now, "duration_minutes": minutes})


class FixDataContract(models.Model):
    _name = "fix.data.contract"
    _description = "Data Contract"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "dataset_code"

    dataset_code = fields.Char(required=True, index=True)
    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    entity_id = fields.Many2one("fix.data.entity", string="Entity", required=True)
    producer = fields.Char(required=True, help="The system/team that publishes the dataset")
    consumers = fields.Char(help="Comma-separated consuming teams/systems")
    schema_version = fields.Char(required=True, default="1.0")
    guarantees = fields.Text(
        help="What the producer guarantees: schema, freshness, completeness, null policy."
    )
    freshness_sla_minutes = fields.Integer(default=60)
    breaking_change_notice_days = fields.Integer(default=14)
    state = fields.Selection(
        [("draft", "Draft"), ("active", "Active"), ("deprecated", "Deprecated")],
        required=True,
        default="draft",
        tracking=True,
    )

    _dataset_unique = models.Constraint(
        "UNIQUE (dataset_code, company_id)", "Dataset code is unique per company"
    )

    def action_activate(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError("Activate a draft contract")
            rec.state = "active"


class FixMetricDefinition(models.Model):
    _name = "fix.metric.definition"
    _description = "Metric Definition"
    _order = "code"

    code = fields.Char(required=True, index=True)
    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    domain_area = fields.Selection(
        [
            ("service", "Service"),
            ("finance", "Finance"),
            ("sales", "Sales"),
            ("people", "People"),
            ("supply", "Supply Chain"),
            ("quality", "Quality"),
            ("customer", "Customer"),
            ("platform", "Platform"),
        ],
        required=True,
        default="service",
    )
    grain = fields.Selection(
        [
            ("event", "Event"),
            ("day", "Day"),
            ("week", "Week"),
            ("month", "Month"),
            ("quarter", "Quarter"),
            ("fiscal_year", "Fiscal year"),
        ],
        required=True,
        default="month",
    )
    definition = fields.Text(
        required=True, help="The formula in words, including numerator/denominator."
    )
    source_entity_id = fields.Many2one("fix.data.entity", string="Source Entity")
    owner_role = fields.Char(help="Accountable business role (R-nn) for this metric")
    state = fields.Selection(
        [("draft", "Draft"), ("published", "Published"), ("retired", "Retired")],
        required=True,
        default="draft",
    )

    _code_unique = models.Constraint(
        "UNIQUE (code, company_id)", "Metric code is unique per company"
    )

    def action_publish(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError("Publish a draft metric")
            rec.state = "published"


class FixDataQualityTest(models.Model):
    _name = "fix.data.quality.test"
    _description = "Data Quality Test Run"
    _order = "checked_at desc, id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    rule_id = fields.Many2one(
        "fix.data.quality.rule",
        string="Quality Rule",
        required=True,
        ondelete="cascade",
        index=True,
    )
    checked_at = fields.Datetime(required=True, default=fields.Datetime.now)
    observed_value = fields.Float(help="What the test measured (e.g. null ratio, duplicate count).")
    threshold = fields.Float(help="Copied from the rule at run time.")
    passed = fields.Boolean(compute="_compute_passed", store=True)
    note = fields.Char()

    @api.depends("observed_value", "threshold")
    def _compute_passed(self):
        for rec in self:
            rec.passed = bool(
                rec.observed_value is not None
                and rec.threshold is not None
                and rec.observed_value <= rec.threshold
            )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.data.quality.test") or "DQT/New"
                )
            if vals.get("rule_id") and not vals.get("threshold"):
                rule = self.env["fix.data.quality.rule"].browse(vals["rule_id"])
                vals["threshold"] = rule.threshold
        return super().create(vals_list)


class FixDataIncident(models.Model):
    _name = "fix.data.incident"
    _description = "Data Quality Incident"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "detected_at desc, id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    entity_id = fields.Many2one("fix.data.entity", string="Entity", required=True, index=True)
    rule_id = fields.Many2one("fix.data.quality.rule", string="Quality Rule")
    title = fields.Char(required=True)
    severity = fields.Selection(
        [("low", "Low"), ("medium", "Medium"), ("high", "High"), ("critical", "Critical")],
        required=True,
        default="medium",
        tracking=True,
    )
    detected_at = fields.Datetime(required=True, default=fields.Datetime.now)
    description = fields.Text()
    resolution = fields.Text()
    state = fields.Selection(
        [("open", "Open"), ("fixed", "Fixed"), ("closed", "Closed")],
        required=True,
        default="open",
        tracking=True,
    )
    resolved_at = fields.Datetime(readonly=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.data.incident") or "DQI/New"
                )
        return super().create(vals_list)

    def action_fix(self):
        for rec in self:
            if rec.state != "open":
                raise UserError("Only an open incident can be marked fixed")
            rec.state = "fixed"

    def action_close(self):
        for rec in self:
            if rec.state != "fixed":
                raise UserError("Close an incident that has been fixed")
            rec.write({"state": "closed", "resolved_at": fields.Datetime.now()})


class FixRetentionPolicy(models.Model):
    _name = "fix.data.retention.policy"
    _description = "Data Retention & Cost Policy"
    _order = "entity_id"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    entity_id = fields.Many2one("fix.data.entity", string="Entity", required=True, index=True)
    tier = fields.Selection(
        [("hot", "Hot (queryable)"), ("warm", "Warm (weekly)"), ("cold", "Cold (archive)")],
        required=True,
        default="hot",
    )
    retention_months = fields.Integer(required=True, default=24)
    storage_cost_per_gb = fields.Float(string="Storage cost / GB (BDT)", default=12.0)
    volume_gb = fields.Float(string="Current volume (GB)")
    monthly_cost = fields.Float(compute="_compute_cost", store=True)
    purge_rule = fields.Char(
        help="What happens at the end of retention: archive, pseudonymise, delete."
    )
    active = fields.Boolean(default=True)

    @api.depends("storage_cost_per_gb", "volume_gb")
    def _compute_cost(self):
        for rec in self:
            rec.monthly_cost = round((rec.volume_gb or 0.0) * (rec.storage_cost_per_gb or 0.0), 2)
