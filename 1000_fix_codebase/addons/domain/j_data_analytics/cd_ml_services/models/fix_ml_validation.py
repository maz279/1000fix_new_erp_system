# M26 lifecycle evidence (capture audit, second pass, 2026-11-19).
#
# The first pass (2026-11-14) gave every M26 sub-module page a capture. Read
# against the spec's lifecycle (§8.1) and owned entities (§10.1), four pages
# still had nowhere to record what a person decides or measures there:
#
#   Training Pipelines   no training run (FR-AIM-002/003, T-10, entity
#                        fix.training.run): the page captured a version, so a
#                        version named no reproducible run at all
#   Evaluation Gates     no data-sufficiency gate (FR-AIM-006 P0, BRU-AIM-12 H,
#                        entity fix.data.sufficiency.gate) and no bias test
#                        (FR-AIM-042 P0, BRU-AIM-07 H, entity fix.bias.test):
#                        the bias status was typed on the version by the
#                        person who registered it
#   Deployment & Monitoring
#                        no production performance (FR-AIM-008 P0, BRU-AIM-19,
#                        entity fix.model.performance): nothing recorded a
#                        floor, so nothing could ever be demoted
#
#   fix.ml.training.run          a reproducible training execution; append-only
#   fix.ml.data.sufficiency      the model's declared prerequisite against what
#                                the data holds; the result is derived;
#                                promotion needs the newest one 'met'
#   fix.ml.bias.test             fairness evidence by someone who is neither the
#                                registrant nor the model's owner; it SETS the
#                                version's bias status
#   fix.ml.performance.observation
#                                a production metric against its floor; a breach
#                                demotes the version when a prior champion can
#                                be restored (T-02: never leave a consumer with
#                                no model AND no decision)
import json

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools.translate import _

from libs.py.fix_events import publish


def _evidence_refusal(env, what):
    return UserError(
        env._("A %s is evidence and cannot be edited (M26) - record a new one.") % what
    )


class FixMlTrainingRun(models.Model):
    """One training run, recorded with everything needed to reproduce it
    (T-10): code version, data snapshot, feature versions, hyperparameters and
    environment. A version names the run that produced it."""

    _name = "fix.ml.training.run"
    _description = "AI/ML Training Run"
    _order = "ended_at desc, id desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    name = fields.Char(compute="_compute_name", store=True)
    model_id = fields.Many2one("fix.ml.model", required=True, ondelete="restrict", index=True)
    model_code = fields.Char(related="model_id.code", store=True)
    code_version = fields.Char(
        required=True, help="The commit or tag of the training code, e.g. 'a1b2c3d'."
    )
    data_snapshot_ref = fields.Char(
        string="Data Snapshot",
        required=True,
        help="The point-in-time snapshot of the M62 feature store the run read.",
    )
    feature_versions = fields.Text(
        required=True, help="Each feature and its version, e.g. 'travel_km@3, skill_match@2'."
    )
    hyperparameters = fields.Text(
        string="Hyperparameters (JSON)", required=True, help="A JSON object."
    )
    environment_ref = fields.Char(
        string="Environment",
        required=True,
        help="The container image or lock file the run executed in.",
    )
    started_at = fields.Datetime(required=True)
    ended_at = fields.Datetime(required=True)
    outcome = fields.Selection(
        [
            ("succeeded", "Succeeded"),
            ("failed", "Failed"),
            ("abandoned", "Abandoned"),
        ],
        required=True,
    )
    metrics_json = fields.Text(
        string="Evaluation Metrics (JSON)",
        help="The run's measured evaluation results; required when it succeeded.",
    )
    failure_note = fields.Char(help="Why the run failed or was abandoned.")
    m06_data_excluded = fields.Boolean(
        string="No recovered M06 customer data",
        help="BRU-AIM-03: recovered customer data is never training data.",
    )
    trained_by = fields.Many2one("res.users", readonly=True, index=True)
    version_ids = fields.One2many("fix.ml.model.version", "training_run_id", string="Versions")

    @api.depends("model_id.code", "code_version", "ended_at")
    def _compute_name(self):
        for rec in self:
            rec.name = "%s @ %s (%s)" % (
                rec.model_id.code or "?",
                rec.code_version or "?",
                rec.ended_at.strftime("%Y-%m-%d") if rec.ended_at else "?",
            )

    @api.constrains(
        "started_at", "ended_at", "outcome", "metrics_json", "failure_note", "hyperparameters"
    )
    def _check_run(self):
        for rec in self:
            if rec.ended_at < rec.started_at:
                raise ValidationError(_("A training run cannot end before it started."))
            try:
                params = json.loads(rec.hyperparameters or "")
            except ValueError as exc:
                raise ValidationError(_("Hyperparameters must be a JSON object: %s") % exc) from exc
            if not isinstance(params, dict):
                raise ValidationError(_("Hyperparameters must be a JSON object."))
            if rec.outcome == "succeeded":
                try:
                    metrics = json.loads(rec.metrics_json or "")
                except ValueError as exc:
                    raise ValidationError(
                        _("A succeeded run records its evaluation metrics as JSON: %s") % exc
                    ) from exc
                if not isinstance(metrics, dict) or not metrics:
                    raise ValidationError(
                        _("A succeeded run records its evaluation metrics (a JSON object).")
                    )
            elif not (rec.failure_note or "").strip():
                raise ValidationError(_("Say why the run failed or was abandoned."))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("m06_data_excluded"):
                raise UserError(
                    _(
                        "Confirm that the training data holds no recovered M06 "
                        "customer data - it is never used to train any model "
                        "(BRU-AIM-03)."
                    )
                )
            vals["trained_by"] = self.env.user.id
        return super().create(vals_list)

    def write(self, vals):
        # the version link is the One2many's inverse, written on the version
        raise _evidence_refusal(self.env, _("training run"))

    def unlink(self):
        raise UserError(_("A training run is evidence and cannot be deleted (M26)."))


class FixMlDataSufficiency(models.Model):
    """The data-sufficiency gate (lifecycle §8.1, FR-AIM-006, BRU-AIM-12):
    the model's DECLARED minimum history and volume, against what the training
    data actually holds. The bar is copied from the model's portfolio
    declaration - the evaluator cannot lower it - and the result is derived.
    Not met is DEFERRED with a revisit date, never rejected (AUT-AIM-02)."""

    _name = "fix.ml.data.sufficiency"
    _description = "AI/ML Data-Sufficiency Gate"
    _order = "evaluated_at desc, id desc"
    _rec_name = "model_id"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    model_id = fields.Many2one("fix.ml.model", required=True, ondelete="restrict", index=True)
    required_history_months = fields.Integer(readonly=True)
    required_volume = fields.Integer(readonly=True)
    observed_history_months = fields.Integer(required=True)
    observed_volume = fields.Integer(required=True, help="Labelled records available.")
    source_modules = fields.Char(
        required=True, help="Where the data comes from, e.g. 'M01 service orders'."
    )
    result = fields.Selection(
        [("met", "Met - may proceed to training"), ("deferred", "Deferred - prerequisite unmet")],
        compute="_compute_result",
        store=True,
    )
    deferred_until = fields.Date(help="When the prerequisite is revisited (required if unmet).")
    prerequisite_note = fields.Text(help="What has to exist before the model can be trained.")
    evaluated_at = fields.Datetime(required=True, default=fields.Datetime.now)
    evaluated_by = fields.Many2one("res.users", readonly=True, index=True)

    @api.depends(
        "observed_history_months", "observed_volume", "required_history_months", "required_volume"
    )
    def _compute_result(self):
        for rec in self:
            met = (
                rec.observed_history_months >= rec.required_history_months
                and rec.observed_volume >= rec.required_volume
            )
            rec.result = "met" if met else "deferred"

    @api.constrains("observed_history_months", "observed_volume", "result", "deferred_until")
    def _check_values(self):
        for rec in self:
            if rec.observed_history_months < 0 or rec.observed_volume < 0:
                raise ValidationError(_("Observed history and volume cannot be negative."))
            if rec.result == "deferred" and not rec.deferred_until:
                raise ValidationError(
                    _(
                        "The prerequisite is not met: set the date it is "
                        "revisited (a deferred model is not cancelled)."
                    )
                )

    @api.model_create_multi
    def create(self, vals_list):
        ml_models = self.env["fix.ml.model"]
        for vals in vals_list:
            model = ml_models.browse(vals.get("model_id")).exists()
            if not model:
                continue
            if model.min_history_months <= 0 and model.min_volume <= 0:
                raise UserError(
                    _(
                        "Model %s declares no minimum history or volume. Declare "
                        "them on its Portfolio Declaration first - the gate "
                        "measures the data against the model's own declaration "
                        "(FR-AIM-006)."
                    )
                    % model.code
                )
            vals["required_history_months"] = model.min_history_months
            vals["required_volume"] = model.min_volume
            vals["evaluated_by"] = self.env.user.id
        return super().create(vals_list)

    def write(self, vals):
        raise _evidence_refusal(self.env, _("data-sufficiency gate"))

    def unlink(self):
        raise UserError(_("A data-sufficiency gate is evidence and cannot be deleted (M26)."))


class FixMlBiasTest(models.Model):
    """Fairness evidence for a version (FR-AIM-042, BRU-AIM-07): the segments
    tested, the metric per segment, the disparity and the assessment. The
    version's bias status FOLLOWS the newest test - nobody types it. Spec §13:
    the model owner and the bias reviewer are incompatible, and the person who
    registered the version does not review its fairness either."""

    _name = "fix.ml.bias.test"
    _description = "AI/ML Bias & Fairness Test"
    _order = "tested_at desc, id desc"
    _rec_name = "version_id"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    version_id = fields.Many2one(
        "fix.ml.model.version", required=True, ondelete="cascade", index=True
    )
    model_id = fields.Many2one(related="version_id.model_id", store=True, index=True)
    segments_tested = fields.Text(
        required=True, help="The segments compared, e.g. 'branch; tenure band; gender'."
    )
    metric_by_segment = fields.Text(required=True, help="The measured metric for each segment.")
    max_disparity = fields.Float(
        string="Largest Disparity", digits=(6, 4), help="The widest gap measured between segments."
    )
    assessment = fields.Selection(
        [("passed", "Passed - no material disparity"), ("failed", "Failed - material disparity")],
        required=True,
    )
    notes = fields.Text()
    tested_at = fields.Datetime(required=True, default=fields.Datetime.now)
    next_due = fields.Date(required=True, help="The next recurring test (BRU-AIM-26).")
    documented_by = fields.Many2one("res.users", readonly=True, index=True)

    @api.constrains("max_disparity", "next_due", "tested_at")
    def _check_values(self):
        for rec in self:
            if rec.max_disparity < 0:
                raise ValidationError(_("A disparity cannot be negative."))
            if rec.next_due <= rec.tested_at.date():
                raise ValidationError(_("The next bias test falls after this one."))

    @api.model_create_multi
    def create(self, vals_list):
        versions = self.env["fix.ml.model.version"]
        for vals in vals_list:
            vals["documented_by"] = self.env.user.id
            version = versions.browse(vals.get("version_id")).exists()
            if not version or self.env.su:
                continue
            if version.state == "retired":
                raise UserError(_("Version %s is retired.") % version.display_name)
            if version.create_uid == self.env.user:
                raise UserError(
                    _(
                        "You registered version %s, so you cannot document its "
                        "bias test - a reviewer who did not build it must (spec §13 SoD)."
                    )
                    % version.display_name
                )
            if version.model_id.owner_id == self.env.user:
                raise UserError(
                    _(
                        "You own model %s, so you cannot review its fairness - "
                        "the check must be external to the model's beneficiary "
                        "(spec §13 SoD)."
                    )
                    % version.model_id.code
                )
        records = super().create(vals_list)
        for rec in records:
            # the engine's write: the status follows the evidence
            rec.version_id.sudo().write(
                {
                    "bias_status": rec.assessment,
                    "bias_notes": _("Bias test of %s by %s: %s")
                    % (
                        rec.tested_at.strftime("%Y-%m-%d"),
                        rec.documented_by.name,
                        rec.segments_tested,
                    ),
                }
            )
            # A2-F09: a completed bias test is a domain event — its consumer
            # posts the result on the model's chatter (M60 GRC may consume it
            # from the outbox later).
            publish(
                self.env,
                "model.bias_test_completed",
                "fix.ml.model",
                rec.model_id.id,
                {
                    "model": rec.model_id.code,
                    "version": rec.version_id.version,
                    "actor": (rec.documented_by or self.env.user).name,
                    "assessment": dict(rec._fields["assessment"].selection).get(
                        rec.assessment, rec.assessment
                    ),
                    "reason": _("Segments tested: %s") % (rec.segments_tested or ""),
                },
            )
        return records

    def write(self, vals):
        raise _evidence_refusal(self.env, _("bias test"))

    def unlink(self):
        raise UserError(_("A bias test is evidence and cannot be deleted (M26)."))


class FixMlPerformanceObservation(models.Model):
    """Production performance of a SERVING version over a period (FR-AIM-008,
    entity fix.model.performance): a metric, its target and its floor, on a
    labelled sample. A breach of the floor demotes the version automatically
    (BRU-AIM-19, T-05) - when a prior champion can be restored. With no prior
    champion the version keeps serving and the breach is escalated: T-02 says
    a model problem never blocks the business process."""

    _name = "fix.ml.performance.observation"
    _description = "AI/ML Production Performance Observation"
    _order = "period_end desc, id desc"
    _rec_name = "metric_name"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    version_id = fields.Many2one(
        "fix.ml.model.version", required=True, ondelete="cascade", index=True
    )
    model_id = fields.Many2one(related="version_id.model_id", store=True, index=True)
    period_start = fields.Date(required=True)
    period_end = fields.Date(required=True)
    metric_name = fields.Char(required=True, help="e.g. 'top-3 accuracy', 'MAPE', 'AUC'.")
    value = fields.Float(required=True, digits=(12, 4))
    target = fields.Float(required=True, digits=(12, 4))
    floor = fields.Float(
        required=True, digits=(12, 4), help="Crossing it demotes the version (BRU-AIM-19)."
    )
    higher_is_better = fields.Boolean(
        default=True, help="Off for error metrics such as MAPE or MAE."
    )
    labelled_sample_size = fields.Integer(required=True)
    breached = fields.Boolean(compute="_compute_breached", store=True)
    action_taken = fields.Selection(
        [
            ("none", "None - within the floor"),
            ("demoted", "Demoted - prior champion restored"),
            ("escalated", "Escalated - no prior champion to restore"),
        ],
        readonly=True,
    )
    note = fields.Char()
    recorded_by = fields.Many2one("res.users", readonly=True, index=True)

    @api.depends("value", "floor", "higher_is_better")
    def _compute_breached(self):
        for rec in self:
            rec.breached = rec.value < rec.floor if rec.higher_is_better else rec.value > rec.floor

    @api.constrains("period_start", "period_end", "labelled_sample_size", "target", "floor")
    def _check_values(self):
        for rec in self:
            if rec.period_end < rec.period_start:
                raise ValidationError(_("The period cannot end before it starts."))
            if rec.labelled_sample_size <= 0:
                raise ValidationError(
                    _("Performance is measured on labelled outcomes: the sample cannot be empty.")
                )
            floor_below = (
                rec.floor <= rec.target if rec.higher_is_better else rec.floor >= rec.target
            )
            if not floor_below:
                raise ValidationError(
                    _("The floor lies on the wrong side of the target for this metric.")
                )

    @api.model_create_multi
    def create(self, vals_list):
        versions = self.env["fix.ml.model.version"]
        for vals in vals_list:
            vals["recorded_by"] = self.env.user.id
            vals.pop("action_taken", None)
            version = versions.browse(vals.get("version_id")).exists()
            if version and version.state != "deployed":
                raise UserError(
                    _("Production performance is measured on a serving version: %s is %s.")
                    % (version.display_name, version.state)
                )
        records = super().create(vals_list)
        for rec in records:
            rec._apply_floor()
        return records

    def _apply_floor(self):
        """AUT-AIM-07: demote on a breach and restore the prior champion -
        without human initiation (the recorder does not choose)."""
        self.ensure_one()
        version = self.version_id.sudo()
        if not self.breached:
            action = "none"
        else:
            prior = version.search(
                [
                    ("model_id", "=", version.model_id.id),
                    ("state", "=", "deployed"),
                    ("id", "!=", version.id),
                ],
                order="deployed_at desc, id desc",
                limit=1,
            )
            reason = _("%s %.4f breached the floor %.4f (%s to %s, %d labelled)") % (
                self.metric_name,
                self.value,
                self.floor,
                self.period_start,
                self.period_end,
                self.labelled_sample_size,
            )
            if prior:
                version.with_context(ml_promotion_engine=True).write(
                    {
                        "state": "demoted",
                        "demoted_at": fields.Datetime.now(),
                        "demotion_reason": reason,
                    }
                )
                version.message_post(
                    body=_("Auto-demoted: %s. Serving restored to %s.")
                    % (reason, prior.display_name)
                )
                action = "demoted"
            else:
                version.message_post(
                    body=_(
                        "Performance floor breached: %s. No prior champion exists "
                        "to restore, so this version keeps serving and the "
                        "consumer's defined fallback stands ready. Escalated to "
                        "the CTO for investigation (AUT-AIM-07)."
                    )
                    % reason
                )
                action = "escalated"
        self.sudo().with_context(ml_performance_engine=True).write({"action_taken": action})

    def write(self, vals):
        if self.env.context.get("ml_performance_engine") and set(vals) == {"action_taken"}:
            return super().write(vals)
        raise _evidence_refusal(self.env, _("performance observation"))

    def unlink(self):
        raise UserError(_("A performance observation is evidence and cannot be deleted (M26)."))
