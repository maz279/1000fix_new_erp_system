# M62 Data Platform & Governance — pipelines, runs, contracts, metrics and the
# quality/observability surface. The entity, lineage and quality-rule models live
# in fix_metric_registry.py; this file adds the execution side.
#
# A11 audit (2026-11-03) G1-G5: contracts were self-activated and rewritten in
# place; metrics had no version and no consumer register; incidents closed with
# no owner or root cause and could be born closed; retention was a register
# nothing purged and anyone could cut to -12 months; pipeline runs could be
# born 'succeeded' with a million rows from zero read. Every one of those is
# now a control: contracts and metric versions route through the approval
# engine (M63), the active row is frozen, incidents close under evidence
# rules, retention shortens only through an approval, and a legal hold blocks
# every purge.
import datetime

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

CONTRACT_SUBSTANTIVE = (
    "dataset_code",
    "entity_id",
    "producer",
    "consumers",
    "schema_version",
    "guarantees",
    "freshness_sla_minutes",
    "breaking_change_notice_days",
)

# Incident SLA hours by severity (G4): the due time is measured on the M63
# working calendar when one is configured for the company, else wall clock.
INCIDENT_SLA_HOURS = {"critical": 4, "high": 24, "medium": 72, "low": 168}


class FixDataPipeline(models.Model):
    _name = "fix.data.pipeline"
    _description = "Data Ingestion Pipeline"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
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

    def _fix_guarded_fields(self) -> set:
        # A11 audit M62-12 (E44): last_success_at was readonly in the UI only,
        # so a plain write forged a fresh stamp and the Freshness SLA report
        # showed no breach over a pipeline that never succeeded. The stamps are
        # the run engine's act alone (a finish writes them through _guarded()).
        return {"last_run_at", "last_success_at"}

    def action_pause(self):
        for rec in self:
            rec.state = "paused"

    def action_resume(self):
        for rec in self:
            # A11 audit M62-8 (E45): a retired pipeline cannot be resumed.
            if rec.state == "retired":
                raise UserError("This pipeline is retired — retired is retired; create a new one.")
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
    finished_at = fields.Datetime(readonly=True)
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
        # A11 audit M62-8 (E40): a run was born 'succeeded' with 1,000,000
        # rows written from 0 read. A run STARTS; only its own finish/fail
        # action concludes it.
        for vals in vals_list:
            if vals.get("state", "running") != "running":
                raise ValidationError(
                    "A pipeline run starts 'running' — it reaches succeeded or "
                    "failed only through its own finish/fail action."
                )
            # A11 audit M62-8 (E45): a RETIRED pipeline runs nothing — not even
            # a manual backfill. (A paused pipeline may: pausing holds the
            # schedule, a backfill is a deliberate act on live infrastructure.)
            if vals.get("pipeline_id"):
                pipeline = self.env["fix.data.pipeline"].browse(vals["pipeline_id"])
                if pipeline.state == "retired":
                    raise ValidationError(
                        "Pipeline %s is retired — a retired pipeline runs "
                        "nothing. Create a new pipeline for this source." % pipeline.display_name
                    )
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.data.run") or "RUN/New"
        return super().create(vals_list)

    def write(self, vals):
        # The terminal states and their stamps belong to the actions alone
        # (A11 audit E43: failed -> succeeded was one write away).
        guarded = {"state", "finished_at", "duration_minutes"} & set(vals)
        if guarded and not self.env.context.get("fix_data_run_action"):
            for rec in self:
                if "state" in vals and vals["state"] != rec.state:
                    raise UserError(
                        "A run changes state only through Finish or Fail, not by " "editing it."
                    )
        return super().write(vals)

    def _check_row_math(self):
        """A load cannot write more rows than it read and rejected combined
        (A11 audit E42: '1,000,000 written, 0 read' was accepted)."""
        for rec in self:
            read = rec.rows_read or 0
            written = rec.rows_written or 0
            rejected = rec.rows_rejected or 0
            if written > read + rejected:
                raise UserError(
                    "Run %s claims %s row(s) written from %s read and %s rejected — "
                    "a load cannot create rows it never saw."
                    % (rec.display_name, written, read, rejected)
                )

    def action_finish(self):
        for rec in self:
            if rec.state != "running":
                raise UserError("Only a running load can be finished")
            if rec.pipeline_id.state == "retired":
                raise UserError(
                    "Pipeline %s is retired — its runs do not conclude with a "
                    "success stamp." % rec.pipeline_id.display_name
                )
            rec._check_row_math()
            now = fields.Datetime.now()
            minutes = 0.0
            if rec.started_at:
                minutes = round((now - rec.started_at).total_seconds() / 60.0, 2)
            rec.with_context(fix_data_run_action=True).write(
                {"state": "succeeded", "finished_at": now, "duration_minutes": minutes}
            )
            rec.pipeline_id._guarded().write({"last_run_at": now, "last_success_at": now})
            # A11 audit G3: a successful load is the natural moment to measure
            # the entity's quality rules.
            rec._run_entity_quality_checks()

    def action_fail(self):
        for rec in self:
            if rec.state != "running":
                raise UserError("Only a running load can fail")
            now = fields.Datetime.now()
            minutes = 0.0
            if rec.started_at:
                minutes = round((now - rec.started_at).total_seconds() / 60.0, 2)
            failure = rec.failure_reason or "failed by %s" % rec.env.user.name
            rec.with_context(fix_data_run_action=True).write(
                {
                    "state": "failed",
                    "finished_at": now,
                    "duration_minutes": minutes,
                    "failure_reason": failure,
                }
            )

    def _run_entity_quality_checks(self):
        """Measure the entity's measurable rules after a successful load.

        Measuring is the engine's act, not the load finisher's: the runner
        stamps the rule and writes evidence rows it must be able to write."""
        entity = self.pipeline_id.target_entity_id.sudo()
        for rule in entity.rule_ids.filtered(lambda r: r.active):
            try:
                rule.sudo().action_measure()
            except UserError:
                continue  # not measurable — never guessed


class FixDataContract(models.Model):
    """A11 audit G1 (M62-5), BRU-DAT-10: a contract is a VERSIONED artefact
    with a producer AND platform signature, and the active row is frozen.

    draft -> (producer signs) -> approval request (M63) -> active. Any change
    to an active contract's terms is refused: the next ruling is a NEW
    VERSION (action_new_version), which supersedes its predecessor when it
    activates."""

    _name = "fix.data.contract"
    _description = "Data Contract"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.approvable.mixin"]
    _order = "dataset_code, version desc"

    _approval_domain = "data_contract"
    _approval_apply_method = "action_activate"
    _approval_group = "cd_metric_registry.group_data_governance_officer"
    _approval_routed = True

    dataset_code = fields.Char(required=True, index=True)
    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    entity_id = fields.Many2one("fix.data.entity", string="Entity", required=True)
    producer = fields.Char(required=True, help="The system/team that publishes the dataset")
    producer_signatory_id = fields.Many2one(
        "res.users",
        string="Producer Signatory",
        help="Who signs for the producer side of the co-signature (BRU-DAT-10).",
    )
    producer_signed_by = fields.Many2one("res.users", readonly=True, copy=False)
    producer_signed_at = fields.Datetime(readonly=True, copy=False)
    consumers = fields.Char(help="Comma-separated consuming teams/systems")
    schema_version = fields.Char(required=True, default="1.0")
    guarantees = fields.Text(
        help="What the producer guarantees: schema, freshness, completeness, null policy."
    )
    freshness_sla_minutes = fields.Integer(default=60)
    breaking_change_notice_days = fields.Integer(default=14)
    version = fields.Integer(required=True, default=1, copy=False)
    predecessor_id = fields.Many2one(
        "fix.data.contract", string="Supersedes", readonly=True, copy=False, ondelete="set null"
    )
    state = fields.Selection(
        [("draft", "Draft"), ("active", "Active"), ("deprecated", "Deprecated")],
        required=True,
        default="draft",
        tracking=True,
    )

    _dataset_unique = models.Constraint(
        "UNIQUE (dataset_code, company_id, version)",
        "Dataset code and version are unique per company",
    )

    @api.model_create_multi
    def create(self, vals_list):
        # Born active would skip the co-signature and the approval entirely.
        for vals in vals_list:
            if vals.get("state", "draft") != "draft":
                raise ValidationError(
                    "A contract is created as a DRAFT — it reaches active only "
                    "through an approved request (M63)."
                )
        return super().create(vals_list)

    @api.constrains("breaking_change_notice_days")
    def _check_notice_days(self):
        # A11 audit M62-5 (E05): the notice period was cut 14 -> 0 in place.
        for rec in self:
            if rec.state == "active" and rec.breaking_change_notice_days < 1:
                raise ValidationError("An active contract must give consumers notice (>= 1 day).")

    def write(self, vals):
        # The active row is frozen (A11 audit E04-E07: schema 1.0 -> 9.9 and
        # notice 14 -> 0 were plain writes). Notes and the request bookkeeping
        # stay editable.
        if self.env.context.get("fix_contract_activation"):
            return super().write(vals)
        # And the LIFECYCLE belongs to its own actions: activation runs from a
        # decided M63 task (action_activate), never from a plain state write.
        if "state" in vals:
            for rec in self:
                if vals["state"] != rec.state:
                    raise UserError(
                        "Contract %s v%s changes state only through its own "
                        "actions — activation comes from an approved request "
                        "(M63), not from editing the field." % (rec.dataset_code, rec.version)
                    )
        for rec in self.filtered(lambda r: r.state == "active"):
            touched = set(CONTRACT_SUBSTANTIVE) & set(vals)
            if touched:
                labels = ", ".join(sorted(touched))
                raise UserError(
                    "Contract %s v%s is ACTIVE and frozen: %s may not change in "
                    "place. Create the next version (New Version) and route it "
                    "for its own producer + platform signature."
                    % (rec.dataset_code, rec.version, labels)
                )
        return super().write(vals)

    def action_producer_sign(self):
        """The producer side of the co-signature: only the named signatory
        (or a governance officer) signs."""
        officer = self.env.user.has_group("cd_metric_registry.group_data_governance_officer")
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only a draft contract can be signed by its producer")
            if not officer and rec.env.user != rec.producer_signatory_id:
                raise UserError(
                    "Only the contract's producer signatory (%s) or a Data "
                    "Governance Officer signs the producer side."
                    % (rec.producer_signatory_id.name or "none named")
                )
            rec.write(
                {
                    "producer_signed_by": rec.env.user.id,
                    "producer_signed_at": fields.Datetime.now(),
                }
            )
        return True

    def action_new_version(self):
        """The next ruling is a new row, never an edit of the active one."""
        new_recs = self.env["fix.data.contract"]
        for rec in self:
            if rec.state != "active":
                raise UserError("Version a contract that is active today")
            draft = rec.copy(
                {
                    "version": rec.version + 1,
                    "predecessor_id": rec.id,
                    "state": "draft",
                    "producer_signed_by": False,
                    "producer_signed_at": False,
                    "approval_state": "none",
                    "approval_request_id": False,
                }
            )
            draft.message_post(
                body="Version %s opened from %s v%s."
                % (draft.version, rec.dataset_code, rec.version)
            )
            new_recs |= draft
        return new_recs

    def action_request_approval(self, justification=None):
        """Platform approval needs the producer signature first."""
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only a draft contract asks for activation.")
            if not rec.producer_signed_by:
                raise UserError(
                    "The producer has not signed v%s yet — the co-signature "
                    "(BRU-DAT-10) is producer first, platform second." % rec.version
                )
        return super().action_request_approval(justification=justification)

    def action_activate(self):
        """The engine calls this AS THE APPROVER once the platform side is
        granted: the decided task in context IS the authorisation (the
        assignee-only decision and the segregation checks ran before it).
        Requires the producer signature, deprecates the predecessor, refuses a
        second active version of the same dataset."""
        self._approval_assert_routed()
        for rec in self:
            if rec.state != "draft":
                raise UserError("Activate a draft contract")
            if not rec.producer_signed_by:
                raise UserError(
                    "The producer side of v%s is unsigned — a contract activates "
                    "on BOTH signatures." % rec.version
                )
            active = self.search(
                [
                    ("dataset_code", "=", rec.dataset_code),
                    ("company_id", "=", rec.company_id.id),
                    ("state", "=", "active"),
                    ("id", "!=", rec.id),
                    ("id", "!=", rec.predecessor_id.id),
                ]
            )
            if active:
                raise UserError(
                    "Contract %s already has an active version (v%s). Version it "
                    "instead." % (rec.dataset_code, active[0].version)
                )
            if rec.predecessor_id and rec.predecessor_id.state == "active":
                rec.predecessor_id.with_context(fix_contract_activation=True).write(
                    {"state": "deprecated"}
                )
            rec.with_context(fix_contract_activation=True).write({"state": "active"})
        return True


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
    version_ids = fields.One2many("fix.metric.version", "definition_id", string="Versions")
    current_version_id = fields.Many2one(
        "fix.metric.version", string="Published Version", compute="_compute_current", store=True
    )
    consumer_ids = fields.One2many("fix.metric.consumer", "definition_id", string="Consumers")

    _code_unique = models.Constraint(
        "UNIQUE (code, company_id)", "Metric code is unique per company"
    )

    @api.model_create_multi
    def create(self, vals_list):
        # Born published would count in the registry with no published
        # version behind it — the definition's state is EARNED by a version
        # routing through M63 (A11 audit E08: only versions carried the
        # born-draft guard; the definition row itself did not).
        for vals in vals_list:
            if vals.get("state", "draft") != "draft":
                raise ValidationError(
                    "A metric definition is created as a DRAFT — it reaches "
                    "published only when one of its versions is published "
                    "through an approved request (M63)."
                )
        return super().create(vals_list)

    @api.depends("version_ids.state")
    def _compute_current(self):
        for rec in self:
            published = rec.version_ids.filtered(lambda v: v.state == "published")
            rec.current_version_id = published[:1]

    def action_retire(self):
        """Retiring is a deliberate act on a published metric; a draft just
        stays draft. Retirement never deletes history."""
        for rec in self:
            if rec.state != "published":
                raise UserError("Retire a published metric")
            rec.write({"state": "retired"})
        return True

    def resolve(self):
        """The published version a BI tile must use (BRU-BID-01): a tile
        resolves a metric by CODE, and only the published version counts."""
        self.ensure_one()
        return self.current_version_id


class FixMetricVersion(models.Model):
    """A11 audit G2 (M62-4), BRU-DAT-02/03: a metric definition is versioned;
    a version is reviewed by the steward, then approved (M63) before it is
    published. The author never publishes alone."""

    _name = "fix.metric.version"
    _description = "Metric Definition Version"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.approvable.mixin"]
    _order = "definition_id, version desc"

    _approval_domain = "metric_definition"
    _approval_apply_method = "action_approve_publish"
    _approval_group = "cd_metric_registry.group_data_governance_officer"
    _approval_routed = True

    name = fields.Char(compute="_compute_name", store=True)
    definition_id = fields.Many2one(
        "fix.metric.definition", required=True, ondelete="cascade", index=True
    )
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    version = fields.Integer(required=True, default=1, copy=False)
    definition_text = fields.Text(
        required=True,
        help="The formula THIS version states (numerator/denominator in words).",
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
    source_entity_id = fields.Many2one("fix.data.entity", string="Source Entity")
    steward_reviewed_by = fields.Many2one("res.users", readonly=True, copy=False)
    steward_reviewed_at = fields.Datetime(readonly=True, copy=False)
    state = fields.Selection(
        [("draft", "Draft"), ("published", "Published"), ("retired", "Retired")],
        required=True,
        default="draft",
        tracking=True,
    )
    published_by = fields.Many2one("res.users", readonly=True, copy=False)
    published_at = fields.Datetime(readonly=True, copy=False)

    _version_unique = models.Constraint(
        "UNIQUE (definition_id, version)", "One version number per definition"
    )

    @api.model_create_multi
    def create(self, vals_list):
        # Born published would skip the steward review and the approval.
        for vals in vals_list:
            if vals.get("state", "draft") != "draft":
                raise ValidationError(
                    "A metric version is created as a DRAFT — it reaches "
                    "published only through an approved request (M63)."
                )
        return super().create(vals_list)

    @api.depends("definition_id.code", "version")
    def _compute_name(self):
        for rec in self:
            rec.name = "%s v%s" % (rec.definition_id.code or "?", rec.version)

    def _steward_users(self):
        """The users who may record the steward review: the source entity's
        steward (their linked user) or a governance officer."""
        self.ensure_one()
        users = self.env["res.users"]
        entity = self.source_entity_id or self.definition_id.source_entity_id
        if entity and entity.steward_id:
            users |= entity.steward_id.sudo().user_id
        return users

    def action_steward_review(self):
        """BRU-DAT-02: the steward reviews BEFORE the approval request."""
        officer = self.env.user.has_group("cd_metric_registry.group_data_governance_officer")
        for rec in self:
            if rec.state != "draft":
                raise UserError("Review a draft version")
            if not officer and rec.env.user not in rec._steward_users():
                raise UserError(
                    "Only the metric's data steward (or a Data Governance "
                    "Officer) records the steward review."
                )
            rec.write(
                {
                    "steward_reviewed_by": rec.env.user.id,
                    "steward_reviewed_at": fields.Datetime.now(),
                }
            )
        return True

    def action_request_approval(self, justification=None):
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only a draft version asks for publication.")
            if not rec.steward_reviewed_by:
                raise UserError(
                    "The steward has not reviewed v%s yet — review comes first, "
                    "then the approval request (BRU-DAT-02/03)." % rec.version
                )
        return super().action_request_approval(justification=justification)

    def write(self, vals):
        # G2: publication runs from a decided M63 task; a plain state write
        # would publish without the steward review or the approval.
        if "state" in vals and not self.env.context.get("fix_metric_publish"):
            for rec in self:
                if vals["state"] != rec.state:
                    raise UserError(
                        "Metric version %s changes state only through its own "
                        "actions — publication comes from an approved request "
                        "(M63), not from editing the field." % rec.display_name
                    )
        return super().write(vals)

    def action_approve_publish(self):
        """The engine calls this AS THE APPROVER: the decided task in context
        is the authorisation. Publish this version and retire any earlier
        published version of the same definition."""
        self._approval_assert_routed()
        for rec in self:
            if rec.state != "draft":
                raise UserError("Publish a draft version")
            if not rec.steward_reviewed_by:
                raise UserError("The steward review is missing.")
            older = self.search(
                [
                    ("definition_id", "=", rec.definition_id.id),
                    ("state", "=", "published"),
                    ("id", "!=", rec.id),
                ]
            )
            older.with_context(fix_metric_publish=True).write({"state": "retired"})
            rec.with_context(fix_metric_publish=True).write(
                {
                    "state": "published",
                    "published_by": rec.env.user.id,
                    "published_at": fields.Datetime.now(),
                }
            )
            rec.definition_id.write({"state": "published"})
        return True


class FixMetricConsumer(models.Model):
    """A11 audit G2: the consumer register — who reads a metric, so a
    retirement can be checked against real consumers first."""

    _name = "fix.metric.consumer"
    _description = "Metric Consumer"
    _order = "definition_id, consumer"
    _rec_name = "consumer"

    definition_id = fields.Many2one(
        "fix.metric.definition", required=True, ondelete="cascade", index=True
    )
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    consumer = fields.Char(
        required=True, help="The consuming module, report or team (e.g. M25:executive_pack)."
    )
    note = fields.Char()

    _consumer_unique = models.Constraint(
        "UNIQUE (definition_id, consumer)", "One register row per consumer per metric"
    )

    @api.constrains("definition_id", "consumer")
    def _check_consumer_unique(self) -> None:
        # The SQL constraint is the backstop; this raises the readable error
        # on the ORM path (a raw UniqueViolation helps nobody in the UI).
        for rec in self:
            dup = self.search_count(
                [
                    ("definition_id", "=", rec.definition_id.id),
                    ("consumer", "=", rec.consumer),
                    ("id", "!=", rec.id),
                ]
            )
            if dup:
                raise ValidationError(
                    "'%s' is already registered as a consumer of %s — the "
                    "register keeps one row per consumer per metric."
                    % (rec.consumer, rec.definition_id.display_name)
                )

    @api.model_create_multi
    def create(self, vals_list):
        # Pre-check before the INSERT: the SQL unique constraint fires during
        # the insert itself, and a raw UniqueViolation is not a usable error.
        for vals in vals_list:
            if vals.get("definition_id") and vals.get("consumer"):
                dup = self.search_count(
                    [
                        ("definition_id", "=", vals["definition_id"]),
                        ("consumer", "=", vals["consumer"]),
                    ]
                )
                if dup:
                    definition = self.env["fix.metric.definition"].browse(vals["definition_id"])
                    raise ValidationError(
                        "'%s' is already registered as a consumer of %s — the "
                        "register keeps one row per consumer per metric."
                        % (vals["consumer"], definition.display_name)
                    )
        return super().create(vals_list)


class FixDataQualityTest(models.Model):
    """A11 audit E5/G3: a test row is an IMMUTABLE record of one check, and
    its verdict comes from the RULE's comparator (one maths for both sides)."""

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
    passed = fields.Boolean(compute="_compute_passed", store=False)
    measured = fields.Boolean(
        default=False,
        help="True when a runner measured the value; a manually typed result "
        "is labelled as such.",
    )
    note = fields.Char()

    @api.depends("observed_value", "threshold", "rule_id")
    def _compute_passed(self):
        for rec in self:
            if rec.rule_id:
                rec.passed = rec.rule_id._evaluate(rec.observed_value)
            else:
                rec.passed = rec.observed_value >= rec.threshold

    def write(self, vals):
        raise UserError("A quality test row is evidence and cannot be edited.")

    def unlink(self):
        raise UserError("A quality test row is evidence and cannot be deleted.")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.data.quality.test") or "DQT/New"
                )
            # A11 audit M62-3 (E23): the tester typed a threshold of 1000 and
            # 'passed' anything. The evidence row records the RULE's threshold
            # at run time — a typed value is overwritten, never trusted (the
            # verdict computes from the rule's own comparator anyway).
            if vals.get("rule_id"):
                rule = self.env["fix.data.quality.rule"].browse(vals["rule_id"])
                vals["threshold"] = rule.threshold
        return super().create(vals_list)


class FixDataIncident(models.Model):
    """A11 audit G4 (M62-8): an incident has an owner, a classification and a
    root cause; closed is final; high and critical incidents cannot be closed
    by their own reporter; the SLA due time comes from the M63 calendar."""

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
    classification = fields.Selection(
        [
            ("quality_breach", "Quality Breach"),
            ("freshness", "Freshness / SLA Breach"),
            ("data_loss", "Data Loss or Corruption"),
            ("security", "Security / Classification"),
            ("other", "Other"),
        ],
        default="quality_breach",
    )
    owner_id = fields.Many2one("res.users", string="Owner", index=True)
    detected_at = fields.Datetime(required=True, default=fields.Datetime.now)
    due_at = fields.Datetime(compute="_compute_due_at", store=True)
    description = fields.Text()
    resolution = fields.Text()
    root_cause = fields.Text(
        help="Required before the incident can close: what actually caused it."
    )
    source_event_id = fields.Char(
        readonly=True,
        copy=False,
        index=True,
        help="The data_quality.failing event that opened this incident "
        "(idempotency for the event consumer).",
    )
    state = fields.Selection(
        [("open", "Open"), ("fixed", "Fixed"), ("closed", "Closed")],
        required=True,
        default="open",
        tracking=True,
    )
    resolved_at = fields.Datetime(readonly=True)

    _source_event_unique = models.Constraint(
        "UNIQUE (source_event_id)",
        "One incident per source event",
    )

    @api.depends("severity", "detected_at")
    def _compute_due_at(self):
        # G4: "SLA through the M63 calendar" — the approval engine's own
        # calendar walk (branch calendar, then the company default, else wall
        # clock) carries the due time over working hours. One calendar
        # implementation, reused, not a second one.
        Request = self.env["fix.approval.request"].sudo()
        calendar = Request._approval_calendar()
        for rec in self:
            base = rec.detected_at or fields.Datetime.now()
            hours = INCIDENT_SLA_HOURS.get(rec.severity, 72)
            rec.due_at = Request._approval_add_business_hours(base, hours, calendar)

    @api.model_create_multi
    def create(self, vals_list):
        # A11 audit M62-8 (E28/31): incidents were born closed. An incident
        # STARTS open; only its own actions move it.
        for vals in vals_list:
            if vals.get("state", "open") != "open":
                raise ValidationError(
                    "An incident is created OPEN. It closes through Fix then "
                    "Close, with an owner, a root cause and a resolution."
                )
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.data.incident") or "DQI/New"
                )
        return super().create(vals_list)

    def write(self, vals):
        # Closed is FINAL (A11 audit E31: reopened and downgraded after close),
        # and the lifecycle belongs to the actions (G4): fixed and closed are
        # reached through Fix and Close with their evidence rules, not typed.
        if self.env.context.get("fix_incident_engine"):
            return super().write(vals)
        for rec in self.filtered(lambda r: r.state == "closed"):
            raise UserError(
                "Incident %s is closed — a closed incident is final. A NEW "
                "finding is a NEW incident." % rec.display_name
            )
        if "state" in vals:
            for rec in self:
                if vals["state"] != rec.state:
                    raise UserError(
                        "Incident %s changes state only through Fix and Close "
                        "— with an owner, a root cause and a resolution, not "
                        "by editing the field." % rec.display_name
                    )
        return super().write(vals)

    def unlink(self):
        raise UserError("A data incident is evidence and cannot be deleted.")

    def action_fix(self):
        for rec in self:
            if rec.state != "open":
                raise UserError("Only an open incident can be marked fixed")
            if not rec.owner_id:
                raise UserError("Assign an owner before marking the incident fixed.")
            rec.with_context(fix_incident_engine=True).write({"state": "fixed"})

    def action_close(self):
        officer = self.env.user.has_group("cd_metric_registry.group_data_governance_officer")
        for rec in self:
            if rec.state != "fixed":
                raise UserError("Close an incident that has been fixed")
            missing = [
                label
                for label, value in (
                    ("owner", rec.owner_id),
                    ("root cause", (rec.root_cause or "").strip()),
                    ("resolution", (rec.resolution or "").strip()),
                )
                if not value
            ]
            if missing:
                raise UserError(
                    "Incident %s cannot close without %s." % (rec.display_name, ", ".join(missing))
                )
            # A11 audit E30: the reporter closed their own high-severity
            # finding. For high/critical, closing belongs to someone else
            # (four eyes); an officer may close what anyone reported.
            if (
                rec.severity in ("high", "critical")
                and not officer
                and not rec.env.su
                and rec.create_uid
                and rec.env.user == rec.create_uid
            ):
                raise UserError(
                    "A high or critical incident is not closed by its own "
                    "reporter — route it to the owner or a Data Governance "
                    "Officer."
                )
            rec.with_context(fix_incident_engine=True).write(
                {"state": "closed", "resolved_at": fields.Datetime.now()}
            )
        return True

    # ---- the data_quality.failing consumer (A11 audit G3, M62-9) ------------
    @api.model
    def consume_data_quality_failing(self, event: dict):
        """The event relay hands every data_quality.failing event here.

        Opens an incident for the failing rule's entity and marks the subject
        area degraded, idempotently per event: a redelivered event finds its
        incident (source_event_id) and does nothing."""
        event_id = event.get("event_id") or ""
        if event_id and self.sudo().search([("source_event_id", "=", event_id)], limit=1):
            return True
        payload = event.get("payload") or {}
        rule = (
            self.env["fix.data.quality.rule"]
            .sudo()
            .browse(int(event.get("aggregate_id") or 0))
            .exists()
        )
        if not rule:
            return True  # the rule is gone; its events concern nobody
        entity = rule.entity_id.sudo()
        entity.write({"degraded": True})
        if not self.sudo().search(
            [
                ("rule_id", "=", rule.id),
                ("state", "=", "open"),
            ],
            limit=1,
        ):
            severity = "high" if float(payload.get("result") or 0.0) < 50.0 else "medium"
            self.sudo().create(
                {
                    "name": "New",
                    "company_id": entity.company_id.id or event.get("company_id") or False,
                    "entity_id": entity.id,
                    "rule_id": rule.id,
                    "title": "Quality rule failing: %s" % rule.display_name,
                    "severity": severity,
                    "classification": "quality_breach",
                    "description": (
                        "Measured %s%% against a %s%% threshold (%s result, event %s)."
                        % (
                            payload.get("result"),
                            payload.get("threshold"),
                            "a measured" if payload.get("measured") else "a manually recorded",
                            event_id or "n/a",
                        )
                    ),
                    "source_event_id": event_id or False,
                }
            )
        return True


class FixRetentionPolicy(models.Model):
    """A11 audit G5 (M62-6): retention has a statutory floor, a positive
    period, one policy per entity, an approval to shorten, a legal hold that
    blocks every purge and deactivation, and a purge with an evidence log."""

    _name = "fix.data.retention.policy"
    _description = "Data Retention & Cost Policy"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.approvable.mixin"]
    _order = "entity_id"

    _approval_domain = "retention_change"
    _approval_apply_method = "action_apply_shorten"
    _approval_group = "cd_metric_registry.group_data_governance_officer"
    # True: the SHORTENING runs only from a decided task. A plain policy needs
    # no approval to exist.
    _approval_routed = True

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
    statutory_floor_months = fields.Integer(
        string="Statutory Floor (months)",
        default=0,
        help="The minimum the law allows for this data class (a Legal/B4 "
        "decision). A period below the floor is refused outright — no "
        "approval can shorten past it.",
    )
    pending_months = fields.Integer(
        string="Shortening To",
        readonly=True,
        copy=False,
        help="The shorter period awaiting approval. Applied by the approval "
        "engine (M63) when the request is granted.",
    )
    storage_cost_per_gb = fields.Float(string="Storage cost / GB (BDT)", default=12.0)
    volume_gb = fields.Float(string="Current volume (GB)")
    monthly_cost = fields.Float(compute="_compute_cost", store=True)
    purge_rule = fields.Char(
        help="What happens at the end of retention: archive, pseudonymise, delete."
    )
    legal_hold = fields.Boolean(
        string="Legal Hold",
        default=False,
        copy=False,
        help="Blocks every purge AND every shortening or deactivation of this "
        "policy until an officer lifts it (Purview pattern).",
    )
    active = fields.Boolean(default=True)

    @api.depends("storage_cost_per_gb", "volume_gb")
    def _compute_cost(self):
        for rec in self:
            rec.monthly_cost = round((rec.volume_gb or 0.0) * (rec.storage_cost_per_gb or 0.0), 2)

    @api.constrains("retention_months", "statutory_floor_months")
    def _check_period(self):
        # A11 audit E32-E34: 84 -> 1, 0, -12 were all accepted. A retention
        # period is positive and never below the statutory floor.
        for rec in self:
            if rec.retention_months is False or rec.retention_months < 1:
                raise ValidationError(
                    "Policy %s: a retention period is at least 1 month (got %s)."
                    % (rec.display_name, rec.retention_months)
                )
            if rec.retention_months < (rec.statutory_floor_months or 0):
                raise ValidationError(
                    "Policy %s: %s month(s) is below the statutory floor of %s "
                    "for this data class. No approval can shorten past the law."
                    % (
                        rec.display_name,
                        rec.retention_months,
                        rec.statutory_floor_months,
                    )
                )

    @api.constrains("entity_id", "active")
    def _check_one_policy_per_entity(self):
        # A11 audit E38: contradictory duplicates were allowed.
        for rec in self.filtered("active"):
            clash = self.search_count(
                [
                    ("entity_id", "=", rec.entity_id.id),
                    ("active", "=", True),
                    ("id", "!=", rec.id),
                ]
            )
            if clash:
                raise ValidationError(
                    "Entity %s already has an active retention policy — one "
                    "policy per entity." % rec.entity_id.display_name
                )

    def _require_officer(self, what):
        if not self.env.user.has_group("cd_metric_registry.group_data_governance_officer"):
            raise UserError("%s is a Data Governance Officer's act." % what)

    def write(self, vals):
        if self.env.context.get("fix_retention_apply"):
            return super().write(vals)
        # A legal hold is an officer's switch, and while it holds, nothing
        # moves: not the period, not the active flag, not the hold itself.
        if "legal_hold" in vals:
            for rec in self:
                if vals["legal_hold"] != rec.legal_hold:
                    self._require_officer("Lifting or setting a legal hold")
        held = self.filtered("legal_hold")
        if held:
            blocking = {"retention_months", "active", "pending_months"} & set(vals)
            if blocking:
                raise UserError(
                    "Policy %s is under LEGAL HOLD: %s cannot change until an "
                    "officer lifts the hold." % (held[0].display_name, ", ".join(sorted(blocking)))
                )
        # Shortening an active policy is an approval, not an edit
        # (A11 audit E35/E36: anyone cut 84 -> 1 or switched the policy off).
        if "retention_months" in vals:
            for rec in self.filtered("active"):
                new_months = vals["retention_months"]
                if new_months is not False and new_months < rec.retention_months:
                    raise UserError(
                        "Shortening %s from %s to %s month(s) is a retention "
                        "change: request it (Request Shortening) so it is "
                        "approved through the approval engine (M63)."
                        % (rec.display_name, rec.retention_months, new_months)
                    )
        if "active" in vals and not vals["active"]:
            for _rec in self:
                self._require_officer("Deactivating a retention policy")
        return super().write(vals)

    def unlink(self):
        raise UserError("A retention policy is deactivated, never deleted.")

    def action_request_shorten(self, new_months):
        """Route a shorter period through M63. The constraint still applies:
        the statutory floor is a floor for the approver too."""
        for rec in self:
            new_months = int(new_months)
            if rec.legal_hold:
                raise UserError("Policy %s is under legal hold." % rec.display_name)
            if new_months >= rec.retention_months:
                raise UserError(
                    "%s months is not shorter than the current %s."
                    % (new_months, rec.retention_months)
                )
            if new_months < 1 or new_months < (rec.statutory_floor_months or 0):
                raise UserError(
                    "%s month(s) is below the statutory floor (%s) or not a "
                    "period at all." % (new_months, rec.statutory_floor_months or 1)
                )
            rec.write({"pending_months": new_months})
            rec.action_request_approval(
                justification="Shorten retention %s -> %s month(s)"
                % (rec.retention_months, new_months)
            )
        return True

    def action_apply_shorten(self):
        """The engine calls this AS THE APPROVER: apply the approved shorter
        period. Only an inbox task reaches here (the assert is the routing
        proof), so a direct call — an author shortening their own policy —
        cannot happen."""
        self._approval_assert_routed()
        for rec in self:
            if not rec.pending_months:
                raise UserError("No shortening is pending on this policy.")
            rec.with_context(fix_retention_apply=True).write(
                {"retention_months": rec.pending_months, "pending_months": 0}
            )
            rec.message_post(
                body="Retention shortened to %s month(s) by %s through M63."
                % (rec.retention_months, rec.env.user.name)
            )
        return True

    def _purge_cutoff(self):
        self.ensure_one()
        return fields.Date.context_today(self) - relativedelta(months=self.retention_months)

    def action_purge(self):
        """Run the disposition: WITH an evidence row. When the entity maps to
        a model and the rule says delete, records past the cutoff are
        deleted; anything else is REPORTED (the evidence row carries the
        eligible count). A legal hold refuses the whole action."""
        self._require_officer("Running a disposition")
        Evidence = self.env["fix.data.purge.evidence"]
        done = self.env["fix.data.purge.evidence"]
        for rec in self:
            if rec.legal_hold:
                raise UserError(
                    "Policy %s is under LEGAL HOLD — nothing is purged until "
                    "the hold is lifted." % rec.display_name
                )
            cutoff = rec._purge_cutoff()
            entity = rec.entity_id.sudo()
            model_name = entity.res_model
            purged = 0
            eligible = 0
            action_taken = "reported"
            if model_name and model_name in self.env:
                Model = self.env[model_name].sudo()
                date_field = "create_date" if "create_date" in Model._fields else None
                if date_field:
                    cutoff_dt = datetime.datetime.combine(cutoff, datetime.time.min)
                    eligible = Model.search_count([(date_field, "<", cutoff_dt)])
                    if eligible and (rec.purge_rule or "").strip().lower() == "delete":
                        old = Model.search([(date_field, "<", cutoff_dt)])
                        purged = len(old)
                        old.unlink()
                        action_taken = "purged"
                    elif eligible:
                        action_taken = "eligible"
            done |= Evidence.create(
                {
                    "policy_id": rec.id,
                    "company_id": rec.company_id.id,
                    "cutoff": cutoff,
                    "eligible": eligible,
                    "purged": purged,
                    "action": action_taken,
                    "note": "run by %s" % self.env.user.name,
                }
            )
            rec.message_post(
                body="Disposition run to %s: %s eligible, %s purged (%s)."
                % (cutoff, eligible, purged, action_taken)
            )
        return done

    @api.model
    def _cron_report_disposition(self):
        """Weekly: report what is past retention without deleting anything —
        the evidence log the disposition decision is taken from."""
        evidence = self.env["fix.data.purge.evidence"]
        for rec in self.search([("active", "=", True)]):
            cutoff = rec._purge_cutoff()
            entity = rec.entity_id.sudo()
            model_name = entity.res_model
            eligible = 0
            if model_name and model_name in self.env:
                Model = self.env[model_name].sudo()
                if "create_date" in Model._fields:
                    eligible = Model.search_count(
                        [("create_date", "<", fields.Datetime.combine(cutoff, datetime.time.min))]
                    )
            if eligible and not evidence.search_count(
                [("policy_id", "=", rec.id), ("action", "=", "eligible"), ("cutoff", "=", cutoff)]
            ):
                evidence.create(
                    {
                        "policy_id": rec.id,
                        "company_id": rec.company_id.id,
                        "cutoff": cutoff,
                        "eligible": eligible,
                        "purged": 0,
                        "action": "eligible",
                        "note": "weekly disposition report",
                    }
                )
        return True


class FixDataPurgeEvidence(models.Model):
    """A11 audit G5: the disposition evidence log. Append-only."""

    _name = "fix.data.purge.evidence"
    _description = "Retention Disposition Evidence"
    _order = "create_date desc, id desc"
    _rec_name = "cutoff"

    company_id = fields.Many2one("res.company", required=True, index=True)
    policy_id = fields.Many2one(
        "fix.data.retention.policy", required=True, ondelete="cascade", index=True
    )
    cutoff = fields.Date(required=True)
    eligible = fields.Integer(help="Records past retention at run time.")
    purged = fields.Integer(help="Records actually deleted (0 unless the rule says delete).")
    action = fields.Selection(
        [("eligible", "Eligible (reported)"), ("purged", "Purged"), ("reported", "Reported")],
        required=True,
    )
    note = fields.Char()
    ran_by = fields.Many2one("res.users", default=lambda self: self.env.user, readonly=True)

    def write(self, vals):
        raise UserError("Disposition evidence is append-only.")

    def unlink(self):
        raise UserError("Disposition evidence is append-only.")
