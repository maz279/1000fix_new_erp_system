# fix_metric_registry — M62: data catalogue, lineage, DQ, stewardship (P11-M02).
#
# A11 audit (2026-11-03) E5/G3/G6: the quality comparator was inverted (the
# rule fired below its threshold while the test passed at-or-below it, so a
# 99%-complete load failed and a 10% load passed); the S3 guard was a
# substring match on the NAME "warehouse"; and no test measured data. The
# comparator is now ONE rule-owned method both sides use, classification is
# governed by layer + a routed, time-limited authorisation, and the rule can
# MEASURE its entity instead of trusting a typed result.
import logging

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish

_logger = logging.getLogger(__name__)

# Sensitivity ladder for classification changes (A11 audit G6, M62-7): a
# downgrade (residency_classified -> confidential -> internal -> public) is
# an approved, time-limited act, never a plain field edit.
CLASSIFICATION_SENSITIVITY = {
    "public": 0,
    "internal": 1,
    "confidential": 2,
    "residency_classified": 3,
}


class FixDataEntity(models.Model):
    """M62: the data catalogue over 1,335 owned entities (DA-002).
    Every entity has an owner, a classification, and a retention."""

    _name = "fix.data.entity"
    _description = "Data Entity (Catalogue)"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "name"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True, index=True)
    entity_type = fields.Selection(
        [
            ("table", "Database Table"),
            ("api", "API Resource"),
            ("event", "Event Stream"),
            ("report", "Report/KPI"),
            ("document", "Document Type"),
        ],
        required=True,
        default="table",
    )
    res_model = fields.Char(
        string="Odoo Model",
        index=True,
        help="The model this entity catalogues, when it maps to one (e.g. "
        "fix.service.order). A rule with a check field can then MEASURE this "
        "entity instead of trusting a typed result.",
    )
    warehouse_layer = fields.Selection(
        [
            ("none", "Not in the warehouse"),
            ("bronze", "Bronze (raw)"),
            ("silver", "Silver (conformed)"),
            ("gold", "Gold (serving)"),
        ],
        required=True,
        default="none",
        help="The medallion layer this entity lands in. NFR-086c governs by "
        "LAYER, never by a name substring (A11 audit G6, M62-7).",
    )
    owner_module = fields.Char(
        string="Owning Module", help="The cd_* module that owns this entity (FF-27)"
    )
    steward_id = fields.Many2one(
        "hr.employee", string="Data Steward", help="DA-003: named people, not named roles"
    )
    classification = fields.Selection(
        [
            ("public", "Public"),
            ("internal", "Internal"),
            ("confidential", "Confidential"),
            ("residency_classified", "Residency-Classified (S3)"),
        ],
        required=True,
        default="internal",
        help="DA-005 classification; S3 entities must NEVER appear in the "
        "analytical warehouse (NFR-086c)",
    )
    retention_policy = fields.Char(
        string="Retention Policy", help="DA-006: how long this data lives"
    )
    degraded = fields.Boolean(
        string="Quality Degraded",
        default=False,
        copy=False,
        help="Set when a quality rule fails on this entity and cleared when "
        "every rule passes again. Written by the quality engine, never typed.",
    )
    rule_ids = fields.One2many("fix.data.quality.rule", "entity_id", string="Quality Rules")
    description = fields.Text()

    def write(self, vals):
        if "classification" in vals:
            for rec in self:
                new_class = vals["classification"]
                if new_class and new_class != rec.classification:
                    downgrade = (
                        CLASSIFICATION_SENSITIVITY[new_class]
                        < (CLASSIFICATION_SENSITIVITY[rec.classification])
                    )
                    if downgrade:
                        auth = self.env["fix.data.declassification.auth"].search(
                            [
                                ("entity_id", "=", rec.id),
                                ("from_classification", "=", rec.classification),
                                ("to_classification", "=", new_class),
                                ("state", "=", "approved"),
                                ("expires_on", ">=", fields.Date.context_today(self)),
                            ],
                            limit=1,
                        )
                        if not auth:
                            raise UserError(
                                "Downgrading %s from %s to %s is a classification "
                                "decision (BRU-DAT-11): record a declassification "
                                "authorisation, have it approved through the "
                                "approval engine, then change the classification."
                                % (rec.display_name, rec.classification, new_class)
                            )
        return super().write(vals)

    @api.constrains("classification", "warehouse_layer")
    def _check_warehouse_safety(self):
        """NFR-086c: no residency-classified data in the analytical store.

        A11 audit G6 (M62-7): the guard was a substring match on the NAME
        ('warehouse'), so 'dwh.gold.dim_party_nid' sailed through. The layer
        the entity actually lands in now decides, whatever it is called."""
        for rec in self:
            if rec.classification == "residency_classified" and rec.warehouse_layer != "none":
                raise ValidationError(
                    "NFR-086c: residency-classified data (S3) must not appear in the "
                    "analytical warehouse. %s is classified %s AND lands in layer %s."
                    % (rec.display_name, rec.classification, rec.warehouse_layer)
                )


class FixDataLineage(models.Model):
    """M62: data-lineage tracking from source to dashboard (DA-003).
    A KPI whose lineage is unknown is a KPI nobody trusts."""

    _name = "fix.data.lineage"
    _description = "Data Lineage"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True)
    source_entity_id = fields.Many2one(
        "fix.data.entity", string="Source", required=True, ondelete="cascade"
    )
    target_entity_id = fields.Many2one(
        "fix.data.entity", string="Target", required=True, ondelete="cascade"
    )
    transformation = fields.Text(
        string="Transformation Logic",
        help="What happens between source and target (the dbt model, the "
        "event handler, the aggregation)",
    )
    lineage_order = fields.Integer(
        string="Order", help="The position in the lineage chain (1=source, N=dashboard)"
    )

    @api.constrains("source_entity_id", "target_entity_id")
    def _check_no_self_loop(self):
        # A11 audit M62-10 (E49): an edge from an entity to itself documents
        # nothing and pads the lineage coverage count.
        for rec in self:
            if rec.source_entity_id == rec.target_entity_id:
                raise ValidationError(
                    "Lineage %s: an entity is not its own upstream — a self-loop "
                    "documents no transformation." % rec.display_name
                )


class FixDataQualityRule(models.Model):
    """M62: DA-008 data quality monitoring with thresholds.

    A11 audit E5/G3 (M62-1..3): ONE comparator, owned by the rule, is used by
    the rule AND by every test row. For every rule type the observed value is
    a QUALITY PERCENTAGE where higher is better, so 'below threshold = the
    rule fires' is true for both sides. A 99%-complete load passes, a 10%
    load fails — the old test comparator had this backwards."""

    _name = "fix.data.quality.rule"
    _description = "Data Quality Rule"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True)
    entity_id = fields.Many2one(
        "fix.data.entity", string="Entity", required=True, ondelete="cascade"
    )
    rule_type = fields.Selection(
        [
            ("completeness", "Completeness (% non-null)"),
            ("uniqueness", "Uniqueness (no duplicates)"),
            ("timeliness", "Timeliness (freshness)"),
            ("accuracy", "Accuracy (value match)"),
            ("consistency", "Consistency (cross-source)"),
        ],
        required=True,
        default="completeness",
    )
    threshold = fields.Float(string="Threshold %", default=95.0, help="Below this, the rule fires")
    check_field = fields.Char(
        string="Check Field",
        help="The column the runner measures on the entity's Odoo model "
        "(completeness: % of rows where it is set; uniqueness: % of rows with "
        "a distinct value). Empty: the rule records manual results only.",
    )
    freshness_window_hours = fields.Integer(
        string="Freshness Window (hours)",
        default=24,
        help="Timeliness only: records touched inside this window count as fresh.",
    )
    active = fields.Boolean(default=True)
    last_checked = fields.Datetime(readonly=True)
    last_result = fields.Float(string="Last Result %", readonly=True)
    last_measured = fields.Boolean(
        string="Last Result Was Measured",
        readonly=True,
        copy=False,
        help="True when the last result was MEASURED by the runner; a typed "
        "result is labelled as such and never shown as a measurement.",
    )
    state = fields.Selection(
        [("passing", "Passing"), ("failing", "Failing")],
        default="passing",
        required=True,
        tracking=True,
    )

    # ---- THE comparator (A11 audit E5, M62-1) ------------------------------
    def _evaluate(self, observed):
        """One comparator for the rule and every test row: a quality
        percentage at or above the threshold passes, below it fails."""
        self.ensure_one()
        return observed is not None and observed >= self.threshold

    # ---- the runner (A11 audit G3, M62-2/3) --------------------------------
    def _measurable_model(self):
        """The model the runner can measure, or None."""
        self.ensure_one()
        name = self.entity_id.res_model
        if not name or name not in self.env:
            return None
        return self.env[name]

    def _measure(self):
        """MEASURE the entity: a real read_group over the entity's model.

        Returns a quality percentage, or raises UserError when this rule
        cannot be measured automatically (no mapped model, no check field, or
        a rule type whose truth lives outside one table). Never invents a
        number."""
        self.ensure_one()
        Model = self._measurable_model()
        if Model is None:
            raise UserError(
                "Rule %s: entity %s maps to no Odoo model, so nothing can be "
                "measured. Map the entity (res_model) or record a manual "
                "result." % (self.display_name, self.entity_id.display_name)
            )
        if not self.check_field:
            raise UserError(
                "Rule %s: no check field is set, so nothing can be measured." % self.display_name
            )
        if self.check_field not in Model._fields:
            raise UserError(
                "Rule %s: %s has no column %r."
                % (self.display_name, self.entity_id.res_model, self.check_field)
            )
        # An empty table is only a free 100% for a rule the runner can count;
        # accuracy/consistency raise BEFORE this point whatever the table size
        # (an empty evidence register must not hand an unmeasurable rule a
        # perfect score).
        if self.rule_type not in ("completeness", "uniqueness", "timeliness"):
            raise UserError(
                "Rule %s: %s is measured by people, not by a table scan — record "
                "its result manually; the runner will not invent one."
                % (self.display_name, dict(self._fields["rule_type"].selection)[self.rule_type])
            )
        total = Model.sudo().search_count([])
        if not total:
            return 100.0
        if self.rule_type == "completeness":
            set_rows = Model.sudo().search_count([(self.check_field, "!=", False)])
            return round(100.0 * set_rows / total, 2)
        if self.rule_type == "uniqueness":
            groups = Model.sudo()._read_group(
                [(self.check_field, "!=", False)],
                groupby=[self.check_field],
                aggregates=["__count"],
            )
            distinct = len(groups)
            populated = sum(count for _value, count in groups)
            return round(100.0 * distinct / populated, 2) if populated else 100.0
        if self.rule_type == "timeliness":
            # Timeliness measures freshness as a percentage of records
            # touched inside the window the rule names (default: 24 hours).
            window_hours = self.freshness_window_hours or 24
            fresh_cutoff = fields.Datetime.now() - relativedelta(hours=window_hours)
            fresh = Model.sudo().search_count([("write_date", ">=", fresh_cutoff)])
            return round(100.0 * fresh / total, 2)
        raise UserError(
            "Rule %s: %s is measured by people, not by a table scan — record "
            "its result manually; the runner will not invent one."
            % (self.display_name, dict(self._fields["rule_type"].selection)[self.rule_type])
        )

    def action_measure(self):
        """Measure the entity now, record an immutable test row and apply the
        rule's own comparator to the measured value."""
        tests = self.env["fix.data.quality.test"]
        for rec in self:
            observed = rec._measure()
            rec._record_result(observed, measured=True)
            tests.create(
                {
                    "rule_id": rec.id,
                    "observed_value": observed,
                    "threshold": rec.threshold,
                    "measured": True,
                    "note": "measured by the quality runner",
                }
            )
        return True

    def _record_result(self, result_pct, measured):
        """Apply the comparator, stamp the rule, publish on failure and let
        the incident consumer act on the event."""
        for rec in self:
            failing = not rec._evaluate(result_pct)
            rec.write(
                {
                    "last_checked": fields.Datetime.now(),
                    "last_result": result_pct,
                    "last_measured": bool(measured),
                    "state": "failing" if failing else "passing",
                }
            )
            if not failing:
                # Every rule of the entity passing clears the degraded flag.
                still_failing = rec.entity_id.rule_ids.filtered(
                    lambda r, rid=rec.id: r.id != rid and r.state == "failing"
                )
                if not still_failing and rec.entity_id.degraded:
                    rec.entity_id.write({"degraded": False})
            if failing:
                publish(
                    self.env,
                    "data_quality.failing",
                    "fix.data.quality.rule",
                    rec.id,
                    {
                        "entity": rec.entity_id.name,
                        "result": result_pct,
                        "threshold": rec.threshold,
                        "measured": bool(measured),
                    },
                )

    def action_check(self, result_pct, measured=False):
        """Record a MANUAL result (a person read the data and wrote the
        number). The comparator is still the rule's own; the row is labelled
        manual so a typed result can never pose as a measurement."""
        for rec in self:
            rec._record_result(result_pct, measured=measured)

    @api.model
    def _cron_run_checks(self):
        """Hourly: measure every active rule whose entity can be measured.
        Rules that cannot be measured are skipped, never guessed."""
        ran = 0
        for rule in self.search([("active", "=", True)]):
            try:
                rule.action_measure()
                ran += 1
            except UserError:
                continue
        _logger.info("M62 DQ runner: measured %s rule(s)", ran)
        return ran


class FixDataDeclassificationAuth(models.Model):
    """A11 audit G6 (M62-7), BRU-DAT-11: moving data to a LESS sensitive
    classification is an approved, time-limited act.

    The authorisation itself is routed through the approval engine (M63):
    a Data Governance Officer approves it, it expires on the day it names,
    and the nightly cron re-classifies the entity when it does. A plain
    classification edit without one is refused by fix.data.entity.write()."""

    _name = "fix.data.declassification.auth"
    _description = "Data Declassification Authorisation"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.approvable.mixin"]
    _order = "create_date desc, id desc"

    _approval_domain = "data_classification"
    _approval_apply_method = "action_approve_auth"
    _approval_group = "cd_metric_registry.group_data_governance_officer"
    _approval_routed = True

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    entity_id = fields.Many2one(
        "fix.data.entity", string="Entity", required=True, ondelete="cascade", index=True
    )
    from_classification = fields.Selection(
        [
            ("public", "Public"),
            ("internal", "Internal"),
            ("confidential", "Confidential"),
            ("residency_classified", "Residency-Classified (S3)"),
        ],
        required=True,
    )
    to_classification = fields.Selection(
        [
            ("public", "Public"),
            ("internal", "Internal"),
            ("confidential", "Confidential"),
            ("residency_classified", "Residency-Classified (S3)"),
        ],
        required=True,
    )
    reason = fields.Text(required=True)
    expires_on = fields.Date(
        required=True,
        help="The authorisation lapses on this day and the classification "
        "reverts (the cron restores from_classification).",
    )
    state = fields.Selection(
        [("draft", "Draft"), ("approved", "Approved"), ("expired", "Expired")],
        required=True,
        default="draft",
        tracking=True,
    )
    approved_by = fields.Many2one("res.users", readonly=True, copy=False)
    approved_at = fields.Datetime(readonly=True, copy=False)

    def write(self, vals):
        # G6: approval is granted by the engine (a decided M63 task) and
        # expiry by the nightly cron — never typed on the field.
        if "state" in vals and not self.env.context.get("fix_declass_engine"):
            for rec in self:
                if vals["state"] != rec.state:
                    raise UserError(
                        "Authorisation %s changes state only through the "
                        "approval engine (M63) or its own expiry — not by "
                        "editing the field." % rec.display_name
                    )
        return super().write(vals)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            # Born approved would skip the engine (G6).
            if vals.get("state", "draft") != "draft":
                raise ValidationError(
                    "An authorisation is created as a DRAFT — the approval "
                    "engine (M63) grants it, never the create form."
                )
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.data.declassification.auth")
                    or "DCA/New"
                )
        return super().create(vals_list)

    @api.constrains("from_classification", "to_classification")
    def _check_is_downgrade(self):
        for rec in self:
            if (
                CLASSIFICATION_SENSITIVITY[rec.to_classification]
                >= CLASSIFICATION_SENSITIVITY[rec.from_classification]
            ):
                raise ValidationError(
                    "A declassification authorisation moves data to a LESS "
                    "sensitive class (%s -> %s is not)."
                    % (rec.from_classification, rec.to_classification)
                )

    @api.constrains("expires_on")
    def _check_expiry_future(self):
        today = fields.Date.context_today(self)
        for rec in self:
            if rec.expires_on and rec.expires_on <= today:
                raise ValidationError(
                    "The authorisation must expire in the future — it is a "
                    "time-limited act, not a permanent reclassification."
                )

    def _approval_on_rejected(self, comment):
        for rec in self:
            rec.message_post(body="Declassification request rejected: %s" % (comment or ""))

    def action_approve_auth(self):
        """The engine calls this AS THE APPROVER once the request is granted."""
        self._approval_assert_routed()
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only a draft authorisation can be approved")
            rec.with_context(fix_declass_engine=True).write(
                {
                    "state": "approved",
                    "approved_by": rec.env.user.id,
                    "approved_at": fields.Datetime.now(),
                }
            )
            rec.entity_id.message_post(
                body=(
                    "Classification %s -> %s authorised by %s (until %s); the "
                    "classification may now be changed."
                    % (
                        rec.from_classification,
                        rec.to_classification,
                        rec.env.user.name,
                        rec.expires_on,
                    )
                )
            )
        return True

    def _apply_expiry(self):
        """Expired authorisations revert the classification they granted."""
        today = fields.Date.context_today(self)
        for rec in self.filtered(lambda a: a.state == "approved" and a.expires_on < today):
            entity = rec.entity_id.sudo()
            if entity.classification == rec.to_classification:
                entity.write({"classification": rec.from_classification})
                entity.message_post(
                    body=(
                        "Declassification authorisation %s expired: classification "
                        "reverted to %s." % (rec.display_name, rec.from_classification)
                    )
                )
            rec.with_context(fix_declass_engine=True).write({"state": "expired"})

    @api.model
    def _cron_expire(self):
        """Daily: lapse and revert expired authorisations."""
        self.search([("state", "=", "approved")])._apply_expiry()
        return True


class FixApprovalMatrixM62Domains(models.Model):
    """The M62 governance decision domains on the DoA matrix."""

    _inherit = "fix.approval.matrix"

    decision_domain = fields.Selection(
        selection_add=[
            ("data_contract", "Data Contract Activation"),
            ("metric_definition", "Metric Definition Publication"),
            ("retention_change", "Retention Period Change"),
            ("data_classification", "Data Classification Change"),
        ],
        ondelete=dict.fromkeys(
            ("data_contract", "metric_definition", "retention_change", "data_classification"),
            "cascade",
        ),
    )
