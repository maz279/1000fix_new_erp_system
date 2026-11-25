# M62 sub-module capture (audit 2026-11-18).
#
# The user observed that not every M62 sub-module page captures a relevant
# record. Evaluated with the workspace's own fregCreate/fregPanels at HEAD
# 32e24dc9: page 7 (Security & Cost) offered no "+ New" and no chip at all;
# metric VERSIONS (the only path to publication), the consumer register and
# declassification authorisations were served by the API but on no screen and
# no form; and four registers the specification owns had no model:
#
#   page 1  fix.data.source        a registered producing system (spec 10.1,
#                                  FR-DAT-001..004, BRU-DAT-09)
#   page 3  fix.data.dimension     a conformed dimension with its SCD type
#                                  (FR-DAT-010/011)
#   page 4/6 fix.glossary.term     the business glossary (FR-DAT-022)
#   page 7  fix.data.erasure       erasure propagated through the analytical
#                                  layers (FR-DAT-036, BRU-DAT-15, AUT-DAT-13)
#
# It also carries the rules a capture form needs so the captured record can
# work: a pipeline's upstream dependencies and a run's backfill/replay terms
# (FR-DAT-006/008, AUT-DAT-01/16), the contract gate before Silver
# (BRU-DAT-10), a fact's declared grain (BRU-DAT-08), one definition per
# metric (BRU-DAT-01/02), the reason and the impact list on a new version
# (FR-DAT-019, AUT-DAT-08) and no retirement while consumers remain
# (BRU-DAT-04).
#
# This file extends models from both other M62 files, so it is imported last.
import re

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

OFFICER = "cd_metric_registry.group_data_governance_officer"

LAYERS = [("bronze", "Bronze (raw)"), ("silver", "Silver (conformed)"), ("gold", "Gold (serving)")]

# A connection reference NAMES the vault entry; a credential typed into it
# would sit in a readable register (SE-01: no secrets in the estate).
_SECRET_LIKE = re.compile(
    r"(password|passwd|pwd|secret|token|api[_-]?key)\s*[=:]|://[^/\s:@]+:[^/\s@]+@",
    re.IGNORECASE,
)


def _require_officer(env, what):
    if not env.su and not env.user.has_group(OFFICER):
        raise UserError("%s is a Data Governance Officer's act." % what)


def _differs(rec, name, value):
    """True when writing `value` would change `rec[name]` (a form echoes the
    fields it shows, so an unchanged echo must not count as an edit)."""
    field = rec._fields[name]
    current = rec[name]
    if field.type == "many2one":
        return (current.id or False) != (value or False)
    return (current or False) != (value or False)


# ============================================================ page 1
class FixDataSource(models.Model):
    """A registered producing system or module (spec 10.1 fix.data.source).

    It is what a pipeline ingests from. It has a business owner and a named
    technical steward before it is activated (BRU-DAT-09), and a retired
    source feeds no pipeline."""

    _name = "fix.data.source"
    _description = "Data Source (Producing System)"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "code"

    code = fields.Char(required=True, index=True)
    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    source_type = fields.Selection(
        [
            ("cdc", "Change Data Capture (database)"),
            ("event", "Domain Events (M28)"),
            ("batch", "Batch Extract"),
            ("file", "File Feed"),
            ("api", "External API"),
        ],
        required=True,
        default="cdc",
    )
    owner_module = fields.Char(
        string="Producing Module", required=True, help="e.g. M01 Service Orders, M19 Finance"
    )
    connection_ref = fields.Char(
        string="Connection Reference",
        help="The NAME of the connection or vault entry the platform uses. Never a "
        "password, token or key: those live in the secrets vault.",
    )
    business_owner_id = fields.Many2one("res.users", string="Business Owner")
    steward_id = fields.Many2one("hr.employee", string="Technical Steward")
    active_from = fields.Date(string="Active From")
    description = fields.Text()
    pipeline_ids = fields.One2many("fix.data.pipeline", "data_source_id", string="Pipelines")
    pipeline_count = fields.Integer(compute="_compute_pipeline_count")
    state = fields.Selection(
        [("draft", "Draft"), ("active", "Active"), ("retired", "Retired")],
        required=True,
        default="draft",
        tracking=True,
    )
    activated_by = fields.Many2one("res.users", readonly=True, copy=False)
    activated_at = fields.Datetime(readonly=True, copy=False)

    _code_unique = models.Constraint(
        "UNIQUE (code, company_id)", "Data source code is unique per company"
    )

    @api.depends("pipeline_ids")
    def _compute_pipeline_count(self):
        for rec in self:
            rec.pipeline_count = len(rec.pipeline_ids)

    @api.constrains("connection_ref")
    def _check_no_secret(self):
        for rec in self:
            if rec.connection_ref and _SECRET_LIKE.search(rec.connection_ref):
                raise ValidationError(
                    "The connection reference of %s looks like a credential. Record "
                    "only the NAME of the vault entry; the secret stays in the vault." % rec.code
                )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("state", "draft") != "draft":
                raise ValidationError(
                    "A data source is registered as a DRAFT and activated once it "
                    "has a business owner and a steward."
                )
        return super().create(vals_list)

    def write(self, vals):
        if "state" in vals and not self.env.context.get("fix_data_source_action"):
            for rec in self:
                if vals["state"] != rec.state:
                    raise UserError(
                        "Data source %s changes state only through Activate and "
                        "Retire." % rec.code
                    )
        return super().write(vals)

    def unlink(self):
        raise UserError("A data source is retired, never deleted.")

    def action_activate(self):
        _require_officer(self.env, "Activating a data source")
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only a draft data source is activated.")
            missing = [
                label
                for label, value in (
                    ("a business owner", rec.business_owner_id),
                    ("a technical steward", rec.steward_id),
                )
                if not value
            ]
            if missing:
                raise UserError(
                    "Data source %s cannot be activated without %s (BRU-DAT-09)."
                    % (rec.code, " and ".join(missing))
                )
            rec.with_context(fix_data_source_action=True).write(
                {
                    "state": "active",
                    "activated_by": self.env.user.id,
                    "activated_at": fields.Datetime.now(),
                    "active_from": rec.active_from or fields.Date.context_today(rec),
                }
            )
        return True

    def action_retire(self):
        _require_officer(self.env, "Retiring a data source")
        for rec in self:
            if rec.state != "active":
                raise UserError("Only an active data source is retired.")
            live = rec.pipeline_ids.filtered(lambda p: p.state == "active")
            if live:
                raise UserError(
                    "Data source %s still feeds %s active pipeline(s) (%s): pause or "
                    "retire them first." % (rec.code, len(live), ", ".join(live.mapped("code")))
                )
            rec.with_context(fix_data_source_action=True).write({"state": "retired"})
        return True


class FixDataPipelineCapture(models.Model):
    _inherit = "fix.data.pipeline"

    data_source_id = fields.Many2one(
        "fix.data.source", string="Data Source", index=True, ondelete="restrict"
    )
    layer = fields.Selection(
        LAYERS,
        required=True,
        default="bronze",
        help="The medallion layer this pipeline writes (FR-DAT-009).",
    )
    owner_id = fields.Many2one("res.users", string="Pipeline Owner")
    upstream_ids = fields.Many2many(
        "fix.data.pipeline",
        "fix_data_pipeline_upstream_rel",
        "downstream_id",
        "upstream_id",
        string="Runs After (Upstream)",
        help="Pipelines whose load this one depends on. A run is refused while an "
        "upstream's latest load failed, is still running or never succeeded "
        "(FR-DAT-008, AUT-DAT-01).",
    )

    @api.model_create_multi
    def create(self, vals_list):
        sources = self.env["fix.data.source"]
        for vals in vals_list:
            if vals.get("data_source_id") and not vals.get("source_system"):
                vals["source_system"] = sources.browse(vals["data_source_id"]).code
        return super().create(vals_list)

    @api.constrains("data_source_id")
    def _check_source_active(self):
        for rec in self:
            if rec.data_source_id and rec.data_source_id.state != "active":
                raise ValidationError(
                    "Pipeline %s: data source %s is %s. A pipeline ingests only from an "
                    "ACTIVE source (owner and steward named)."
                    % (rec.code, rec.data_source_id.code, rec.data_source_id.state)
                )

    @api.constrains("upstream_ids")
    def _check_upstream_acyclic(self):
        for rec in self:
            seen = set()
            frontier = rec.upstream_ids
            while frontier:
                if rec in frontier:
                    raise ValidationError(
                        "Pipeline %s cannot run after itself: its upstream chain leads "
                        "back to it." % rec.code
                    )
                new = frontier.filtered(lambda p, s=seen: p.id not in s)
                seen.update(new.ids)
                frontier = new.mapped("upstream_ids")

    def _upstream_blockers(self):
        """The upstream pipelines whose state forbids a run of this one."""
        self.ensure_one()
        Run = self.env["fix.data.run"].sudo()
        blockers = []
        for up in self.sudo().upstream_ids:
            latest = Run.search(
                [("pipeline_id", "=", up.id)], order="started_at desc, id desc", limit=1
            )
            if not latest:
                blockers.append("%s has never run" % up.code)
            elif latest.state == "failed":
                blockers.append("%s: its latest load %s failed" % (up.code, latest.name))
            elif latest.state == "running":
                blockers.append("%s: its load %s is still running" % (up.code, latest.name))
        return blockers


class FixDataRunCapture(models.Model):
    _inherit = "fix.data.run"

    period_from = fields.Date(string="Period From")
    period_to = fields.Date(string="Period To")
    replay_of_run_id = fields.Many2one(
        "fix.data.run", string="Replays Run", ondelete="restrict", index=True
    )
    reason = fields.Text(help="Why this backfill or replay is run (it restates published figures).")

    _RUN_TERMS = (
        "pipeline_id",
        "kind",
        "stage",
        "period_from",
        "period_to",
        "replay_of_run_id",
        "reason",
    )

    def _check_run_terms(self, vals, starting):
        """The terms a run starts on. `vals` holds the run's full terms."""
        Pipeline = self.env["fix.data.pipeline"]
        pipeline = Pipeline.browse(vals.get("pipeline_id") or 0).exists()
        kind = vals.get("kind") or "scheduled"
        if kind in ("backfill", "replay"):
            if not (vals.get("period_from") and vals.get("period_to")):
                raise ValidationError(
                    "A %s rebuilds a stated period: give Period From and Period To "
                    "(AUT-DAT-16)." % kind
                )
            if fields.Date.to_date(vals["period_from"]) > fields.Date.to_date(vals["period_to"]):
                raise ValidationError("The period of a %s ends after it starts." % kind)
            if not (vals.get("reason") or "").strip():
                raise ValidationError(
                    "A %s restates figures that may already be published: state why "
                    "(BRU-DAT-24)." % kind
                )
        if kind == "replay":
            original = self.browse(vals.get("replay_of_run_id") or 0).exists()
            if not original:
                raise ValidationError("A replay names the run it replays.")
            if pipeline and original.pipeline_id != pipeline:
                raise ValidationError(
                    "Run %s belongs to pipeline %s: a replay runs the same pipeline."
                    % (original.name, original.pipeline_id.code)
                )
            if original.state == "running":
                raise ValidationError(
                    "Run %s is still running: nothing to replay yet." % original.name
                )
        elif vals.get("replay_of_run_id"):
            raise ValidationError("Only a replay names a run it replays.")
        if pipeline and vals.get("stage") in ("silver", "gold"):
            contract = (
                self.env["fix.data.contract"]
                .sudo()
                .search_count(
                    [
                        ("entity_id", "=", pipeline.target_entity_id.id),
                        ("company_id", "=", pipeline.company_id.id),
                        ("state", "=", "active"),
                    ]
                )
            )
            if not contract:
                raise ValidationError(
                    "%s lands %s in %s, but the entity has no ACTIVE data contract. "
                    "A producer's data enters Silver only under a signed contract "
                    "(BRU-DAT-10)."
                    % (pipeline.code, pipeline.target_entity_id.display_name, vals["stage"])
                )
        if pipeline and starting:
            blockers = pipeline._upstream_blockers()
            if blockers:
                raise ValidationError(
                    "%s runs after its upstream loads, and %s. A downstream load never "
                    "runs on a failed upstream (AUT-DAT-01)." % (pipeline.code, "; ".join(blockers))
                )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            self._check_run_terms(vals, starting=True)
        return super().create(vals_list)

    def write(self, vals):
        if not self.env.context.get("fix_data_run_action"):
            terms = set(self._RUN_TERMS) & set(vals)
            for rec in self:
                if rec.state != "running":
                    edited = [
                        k
                        for k in vals
                        # a state change keeps the base refusal ("only through
                        # Finish or Fail"); every other field is refused here
                        if k in rec._fields
                        and k not in ("state", "failure_reason")
                        and _differs(rec, k, vals[k])
                    ]
                    if edited:
                        raise UserError(
                            "Run %s is %s: a concluded load is history and is not "
                            "edited (%s)." % (rec.name, rec.state, ", ".join(sorted(edited)))
                        )
                    continue
                if terms:
                    merged = {k: rec[k] for k in self._RUN_TERMS}
                    merged = {k: (v.id if hasattr(v, "_name") else v) for k, v in merged.items()}
                    merged.update({k: vals[k] for k in terms})
                    self._check_run_terms(
                        merged,
                        starting="pipeline_id" in vals
                        and _differs(rec, "pipeline_id", vals["pipeline_id"]),
                    )
        return super().write(vals)


class FixDataContractCapture(models.Model):
    _inherit = "fix.data.contract"

    data_source_id = fields.Many2one(
        "fix.data.source",
        string="Producing Source",
        index=True,
        ondelete="restrict",
        help="The registered source whose data the contract governs (spec 10.1).",
    )


# ============================================================ page 5
class FixDataQualityRuleCapture(models.Model):
    _inherit = "fix.data.quality.rule"

    severity = fields.Selection(
        [("low", "Low"), ("medium", "Medium"), ("high", "High"), ("critical", "Critical")],
        help="The severity of the incident a failure opens (FR-DAT-024). Empty: high "
        "below 50%, else medium.",
    )

    @api.constrains("check_field", "entity_id")
    def _check_field_exists(self):
        for rec in self:
            model = rec.entity_id.res_model
            if (
                rec.check_field
                and model
                and model in self.env
                and rec.check_field not in self.env[model]._fields
            ):
                raise ValidationError(
                    "Rule %s: %s has no column %r - the runner could never measure it."
                    % (rec.name, model, rec.check_field)
                )


# ============================================================ page 3
class FixDataEntityCapture(models.Model):
    _inherit = "fix.data.entity"

    model_kind = fields.Selection(
        [
            ("fact", "Fact"),
            ("dimension", "Dimension"),
            ("reference", "Reference / Lookup"),
            ("other", "Other"),
        ],
        string="Model Role",
        required=True,
        default="other",
    )
    grain_declaration = fields.Char(
        string="Declared Grain",
        help="What one row means, e.g. 'one row per service order per status change'. "
        "A fact declares it (BRU-DAT-08).",
    )
    dimension_ids = fields.One2many("fix.data.dimension", "entity_id", string="Dimension")

    @api.constrains("model_kind", "grain_declaration")
    def _check_fact_grain(self):
        for rec in self:
            if rec.model_kind == "fact" and not (rec.grain_declaration or "").strip():
                raise ValidationError(
                    "%s is a fact: declare its grain (what one row means) - a fact "
                    "without a declared grain cannot be built (BRU-DAT-08)." % rec.display_name
                )

    @api.constrains("res_model")
    def _check_res_model(self):
        for rec in self:
            if rec.res_model and rec.res_model not in self.env:
                raise ValidationError(
                    "%s: %r is not a model of this system, so nothing could be measured "
                    "or purged on it." % (rec.display_name, rec.res_model)
                )


class FixDataDimension(models.Model):
    """A conformed dimension (spec 10.1 fix.dimension, FR-DAT-010/011)."""

    _name = "fix.data.dimension"
    _description = "Conformed Dimension"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "name"

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    entity_id = fields.Many2one(
        "fix.data.entity", string="Catalogue Entity", required=True, ondelete="cascade", index=True
    )
    natural_key = fields.Char(
        required=True, help="The business key the dimension conforms on, e.g. party_code."
    )
    surrogate_key_strategy = fields.Selection(
        [
            ("sequence", "Warehouse sequence"),
            ("hash", "Hash of the natural key"),
            ("natural", "Natural key used as is"),
        ],
        required=True,
        default="sequence",
    )
    scd_type = fields.Selection(
        [
            ("type0", "Type 0 - fixed, never changes"),
            ("type1", "Type 1 - overwrite, no history"),
            ("type2", "Type 2 - new row per change (full history)"),
            ("type3", "Type 3 - previous value kept"),
        ],
        string="Slowly-Changing Type",
        required=True,
        default="type2",
    )
    tracked_attributes = fields.Text(
        help="The attributes whose history is kept (Type 2/3): a transaction is analysed "
        "against the values in force when it happened (FR-DAT-011)."
    )
    attributes = fields.Text(string="Attribute List")
    source_master_module = fields.Char(
        string="Master Owned By", help="The module that owns the operational master, e.g. M33."
    )
    fact_entity_ids = fields.Many2many(
        "fix.data.entity",
        "fix_data_dimension_fact_rel",
        "dimension_id",
        "entity_id",
        string="Used By Facts",
        help="The fact entities that use this dimension identically (conformed).",
    )

    _entity_unique = models.Constraint(
        "UNIQUE (entity_id)", "A catalogue entity is described by one dimension"
    )

    @api.constrains("scd_type", "tracked_attributes")
    def _check_tracked(self):
        for rec in self:
            if rec.scd_type in ("type2", "type3") and not (rec.tracked_attributes or "").strip():
                raise ValidationError(
                    "Dimension %s keeps history (%s): name the attributes it tracks."
                    % (rec.name, dict(rec._fields["scd_type"].selection)[rec.scd_type])
                )

    @api.constrains("entity_id", "fact_entity_ids")
    def _check_roles(self):
        for rec in self:
            if rec.entity_id.model_kind == "fact":
                raise ValidationError("%s is a fact, not a dimension." % rec.entity_id.display_name)
            wrong = rec.fact_entity_ids.filtered(lambda e: e.model_kind != "fact")
            if wrong:
                raise ValidationError(
                    "Only facts use a dimension; %s %s not declared as fact(s)."
                    % (", ".join(wrong.mapped("display_name")), "is" if len(wrong) == 1 else "are")
                )

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            if rec.entity_id.model_kind == "other":
                rec.entity_id.write({"model_kind": "dimension"})
        return records


# ============================================================ page 4
class FixMetricDefinitionCapture(models.Model):
    _inherit = "fix.metric.definition"

    # What a tile resolves follows the published VERSION; once published, the
    # definition is changed only by publishing a new one (BRU-DAT-01/02).
    _M62_FROZEN = ("code", "definition", "grain", "source_entity_id")

    def write(self, vals):
        if not self.env.su and not self.env.context.get("fix_metric_publish"):
            # the rule book is the officer's: a plain user gets the access
            # refusal, not this one
            self.check_access("write")
            frozen = set(self._M62_FROZEN) & set(vals)
            for rec in self.filtered(lambda r: r.state in ("published", "retired")):
                changed = sorted(k for k in frozen if _differs(rec, k, vals[k]))
                if changed:
                    raise UserError(
                        "Metric %s is %s: %s change only by publishing a new version "
                        "(draft it, steward review, approval) - there is no edit path "
                        "(BRU-DAT-02)." % (rec.code, rec.state, ", ".join(changed))
                    )
        return super().write(vals)

    def action_retire(self):
        for rec in self:
            if rec.consumer_ids:
                raise UserError(
                    "Metric %s still has %s registered consumer(s) (%s). A metric is not "
                    "retired while anyone reads it (BRU-DAT-04): move them to its "
                    "successor and remove them from the register first."
                    % (
                        rec.code,
                        len(rec.consumer_ids),
                        ", ".join(rec.consumer_ids.mapped("consumer")),
                    )
                )
        return super().action_retire()


class FixMetricVersionCapture(models.Model):
    _inherit = "fix.metric.version"

    change_reason = fields.Text(
        help="Why the definition changes. Required on every version after the first "
        "(FR-DAT-019)."
    )
    impact_snapshot = fields.Text(
        string="Impact (consumers notified)",
        readonly=True,
        copy=False,
        help="The registered consumers of the metric when publication was requested: "
        "who the change reaches (AUT-DAT-08).",
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("version") and vals.get("definition_id"):
                last = self.sudo().search(
                    [("definition_id", "=", vals["definition_id"])], order="version desc", limit=1
                )
                vals["version"] = (last.version or 0) + 1
        return super().create(vals_list)

    def write(self, vals):
        if not self.env.context.get("fix_metric_publish"):
            text = {"definition_id", "version", "definition_text", "grain", "source_entity_id"}
            for rec in self.filtered("steward_reviewed_by"):
                changed = sorted(k for k in text & set(vals) if _differs(rec, k, vals[k]))
                if changed:
                    raise UserError(
                        "Version %s was reviewed by the steward: %s no longer change. "
                        "Draft a new version." % (rec.display_name, ", ".join(changed))
                    )
        return super().write(vals)

    def action_request_approval(self, justification=None):
        for rec in self:
            earlier = self.sudo().search_count(
                [("definition_id", "=", rec.definition_id.id), ("id", "!=", rec.id)]
            )
            if earlier and not (rec.change_reason or "").strip():
                raise UserError(
                    "Version %s changes an existing metric: record the reason for the "
                    "change first (FR-DAT-019)." % rec.display_name
                )
            consumers = rec.definition_id.sudo().consumer_ids
            snapshot = (
                "\n".join(
                    "%s (%s)"
                    % (
                        c.consumer,
                        dict(c._fields["consumer_type"].selection).get(c.consumer_type, "-"),
                    )
                    for c in consumers
                )
                if consumers
                else "No registered consumer."
            )
            rec.with_context(fix_metric_publish=True).write({"impact_snapshot": snapshot})
        return super().action_request_approval(justification=justification)

    def action_approve_publish(self):
        res = super().action_approve_publish()
        for rec in self:
            definition = rec.definition_id
            definition.with_context(fix_metric_publish=True).write(
                {
                    "definition": rec.definition_text,
                    "grain": rec.grain,
                    "source_entity_id": (rec.source_entity_id or definition.source_entity_id).id
                    or False,
                }
            )
            # The definition has no chatter: the note goes on the published
            # version, which does.
            if definition.consumer_ids:
                rec.message_post(
                    body="Version %s published. Registered consumers notified: %s"
                    % (rec.version, rec.impact_snapshot or "-")
                )
        return res


class FixMetricConsumerCapture(models.Model):
    _inherit = "fix.metric.consumer"

    consumer_type = fields.Selection(
        [
            ("dashboard", "Dashboard"),
            ("report", "Report"),
            ("api", "API"),
            ("model", "ML Model"),
            ("portal", "Portal"),
            ("module", "Module"),
        ],
        string="Consumer Type",
        default="report",
    )


class FixGlossaryTerm(models.Model):
    """The business glossary (FR-DAT-022): a term, its plain meaning in English
    and Bengali, an owner, and the metrics and datasets it explains."""

    _name = "fix.glossary.term"
    _description = "Business Glossary Term"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "term_en"
    _rec_name = "term_en"

    term_en = fields.Char(string="Term (English)", required=True, index=True)
    term_bn = fields.Char(string="Term (Bengali)")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    definition = fields.Text(string="Plain-Language Meaning", required=True)
    definition_bn = fields.Text(string="Meaning (Bengali)")
    owner_id = fields.Many2one("res.users", string="Business Owner", required=True)
    synonyms = fields.Char(help="Other names people use, comma-separated.")
    metric_ids = fields.Many2many(
        "fix.metric.definition",
        "fix_glossary_term_metric_rel",
        "term_id",
        "metric_id",
        string="Related Metrics",
    )
    entity_ids = fields.Many2many(
        "fix.data.entity",
        "fix_glossary_term_entity_rel",
        "term_id",
        "entity_id",
        string="Related Datasets",
    )
    active = fields.Boolean(default=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("owner_id"):
                raise ValidationError(
                    "Glossary term %r needs a named business owner (BRU-DAT-09)."
                    % (vals.get("term_en") or "")
                )
        return super().create(vals_list)

    @api.constrains("term_en", "company_id")
    def _check_unique_term(self):
        for rec in self:
            clash = self.with_context(active_test=False).search_count(
                [
                    ("term_en", "=ilike", (rec.term_en or "").strip()),
                    ("company_id", "=", rec.company_id.id),
                    ("id", "!=", rec.id),
                ]
            )
            if clash:
                raise ValidationError(
                    "'%s' is already in the glossary: one meaning per term." % rec.term_en
                )


# ============================================================ page 7
class FixDataDeclassificationAuthCapture(models.Model):
    _inherit = "fix.data.declassification.auth"

    @api.model_create_multi
    def create(self, vals_list):
        Entity = self.env["fix.data.entity"]
        for vals in vals_list:
            entity = Entity.browse(vals.get("entity_id") or 0).exists()
            if not entity:
                continue
            current = entity.classification
            if not vals.get("from_classification"):
                vals["from_classification"] = current
            elif vals["from_classification"] != current:
                raise ValidationError(
                    "%s is classified %s today: an authorisation moves it FROM its "
                    "current classification, not from %s."
                    % (entity.display_name, current, vals["from_classification"])
                )
        return super().create(vals_list)


class FixDataRetentionPolicyCapture(models.Model):
    _inherit = "fix.data.retention.policy"

    @api.model_create_multi
    def create(self, vals_list):
        # Page 7's "+ New" captures a policy; it is named after its entity, not
        # left as "New" (the form has no name field).
        Entity = self.env["fix.data.entity"]
        for vals in vals_list:
            if vals.get("name", "New") == "New" and vals.get("entity_id"):
                vals["name"] = Entity.browse(vals["entity_id"]).display_name or "New"
        return super().create(vals_list)


class FixDataErasure(models.Model):
    """An erasure propagated through the analytical estate (spec 10.1
    fix.erasure.request, FR-DAT-036, BRU-DAT-15, AUT-DAT-13).

    Opened for an M33 erasure request (automatically when the DPO starts it),
    worked layer by layer, and completed only with every layer done and the
    evidence named. Completed is final."""

    _name = "fix.data.erasure"
    _description = "Analytical Erasure Propagation"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "requested_at desc, id desc"

    _LAYER_FIELDS = (
        "bronze_done",
        "silver_done",
        "gold_done",
        "feature_store_done",
        "extracts_done",
    )

    name = fields.Char(required=True, default="New", copy=False)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    request_id = fields.Many2one(
        "fix.rights.request",
        string="Erasure Request (M33)",
        required=True,
        index=True,
        ondelete="restrict",
        domain=[("request_type", "=", "erasure")],
    )
    partner_id = fields.Many2one(related="request_id.partner_id", store=True, string="Party")
    statutory_due = fields.Date(related="request_id.statutory_due", string="Statutory Due")
    requested_at = fields.Datetime(default=fields.Datetime.now, readonly=True)
    bronze_done = fields.Boolean(string="Bronze (raw) erased")
    silver_done = fields.Boolean(string="Silver (conformed) erased")
    gold_done = fields.Boolean(string="Gold (serving) erased")
    feature_store_done = fields.Boolean(string="Feature store erased")
    extracts_done = fields.Boolean(string="Extracts and sandboxes erased")
    evidence_ref = fields.Char(
        string="Completion Evidence", help="The purge job, ticket or report proving the erasure."
    )
    note = fields.Text()
    state = fields.Selection(
        [("open", "Open"), ("completed", "Completed")],
        required=True,
        default="open",
        tracking=True,
    )
    completed_by = fields.Many2one("res.users", readonly=True, copy=False)
    completed_at = fields.Datetime(readonly=True, copy=False)

    _request_unique = models.Constraint(
        "UNIQUE (request_id)", "One analytical erasure per erasure request"
    )

    @api.model_create_multi
    def create(self, vals_list):
        Request = self.env["fix.rights.request"].sudo()
        for vals in vals_list:
            if vals.get("state", "open") != "open":
                raise ValidationError("An analytical erasure starts OPEN.")
            request = Request.browse(vals.get("request_id") or 0).exists()
            if request and request.request_type != "erasure":
                raise ValidationError(
                    "%s is a %s request: only an erasure request is propagated."
                    % (request.display_name, request.request_type)
                )
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.data.erasure") or "ERA/New"
        return super().create(vals_list)

    def write(self, vals):
        if not self.env.context.get("fix_erasure_action"):
            if "state" in vals:
                for rec in self:
                    if vals["state"] != rec.state:
                        raise UserError("An erasure completes only through Complete.")
            for rec in self.filtered(lambda r: r.state == "completed"):
                raise UserError(
                    "Erasure %s is completed - its evidence is final." % rec.display_name
                )
        return super().write(vals)

    def unlink(self):
        raise UserError("An analytical erasure is evidence and is never deleted.")

    def action_complete(self):
        _require_officer(self.env, "Completing an analytical erasure")
        for rec in self:
            if rec.state != "open":
                raise UserError("Erasure %s is already completed." % rec.display_name)
            missing = [rec._fields[name].string for name in self._LAYER_FIELDS if not rec[name]]
            if missing:
                raise UserError(
                    "Erasure %s is not complete: %s not done. An incomplete erasure is a "
                    "regulatory failure (BRU-DAT-15)." % (rec.display_name, "; ".join(missing))
                )
            if not (rec.evidence_ref or "").strip():
                raise UserError(
                    "Name the completion evidence before completing %s." % rec.display_name
                )
            rec.with_context(fix_erasure_action=True).write(
                {
                    "state": "completed",
                    "completed_by": self.env.user.id,
                    "completed_at": fields.Datetime.now(),
                }
            )
            rec.request_id.sudo().message_post(
                body="Analytical estate erasure %s completed by %s (evidence: %s)."
                % (rec.name, self.env.user.name, rec.evidence_ref)
            )
        return True


class FixRightsRequestErasure(models.Model):
    _inherit = "fix.rights.request"

    def action_start(self):
        res = super().action_start()
        Erasure = self.env["fix.data.erasure"].sudo()
        for req in self.filtered(lambda r: r.request_type == "erasure"):
            if not Erasure.search_count([("request_id", "=", req.id)]):
                Erasure.create(
                    {"request_id": req.id, "company_id": req.company_id.id or self.env.company.id}
                )
        return res
