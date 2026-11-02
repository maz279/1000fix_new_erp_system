# M26 governance: model versions, evaluation gates, guard rails. These are
# real configuration/governance records; evaluation results are keyed in by
# the reviewer (no metric is invented), and a version only reaches
# 'deployed' through the approval chain.
from odoo import fields, models


class FixMlModelVersion(models.Model):
    """One version of a registered model: artifact, metrics, bias/drift
    observations, deployment mode and the model card."""

    _name = "fix.ml.model.version"
    _description = "AI/ML Model Version"
    _order = "model_id, version desc"

    name = fields.Char(compute="_compute_name", store=True)
    model_id = fields.Many2one("fix.ml.model", required=True, ondelete="cascade", index=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    version = fields.Char(required=True, help="Semantic version of the artifact.")
    artifact_ref = fields.Char(help="Registry/artifact URI — never a fabricated path.")
    training_dataset = fields.Char(help="Dataset the version was trained on (certified scope).")
    metrics_json = fields.Text(
        string="Metrics (JSON)", help="Measured metrics keyed in from the evaluation run."
    )
    bias_status = fields.Selection(
        [("untested", "Untested"), ("passed", "Passed"), ("failed", "Failed")],
        required=True,
        default="untested",
    )
    bias_notes = fields.Text()
    drift_score = fields.Float(help="Observed drift score (0..1) from the monitoring run.")
    deployment_mode = fields.Selection(
        [
            ("none", "Not Deployed"),
            ("batch", "Batch"),
            ("online", "Online (real time)"),
            ("edge", "Edge (device side)"),
        ],
        required=True,
        default="none",
    )
    model_card = fields.Text(help="Purpose, intended use, limitations, ethical notes.")
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("evaluated", "Evaluated"),
            ("approved", "Approved"),
            ("deployed", "Deployed"),
            ("retired", "Retired"),
        ],
        required=True,
        default="draft",
    )
    approved_by = fields.Many2one("res.users", readonly=True)
    deployed_at = fields.Datetime(readonly=True)
    gate_ids = fields.One2many("fix.ml.evaluation.gate", "version_id", string="Evaluation Gates")

    def _compute_name(self):
        for rec in self:
            rec.name = "%s %s" % (rec.model_id.code or "?", rec.version or "")


class FixMlEvaluationGate(models.Model):
    """One evaluation gate result for a model version (pass/fail, reviewer)."""

    _name = "fix.ml.evaluation.gate"
    _description = "AI/ML Evaluation Gate"
    _order = "checked_at desc, id desc"

    version_id = fields.Many2one(
        "fix.ml.model.version", required=True, ondelete="cascade", index=True
    )
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    gate = fields.Selection(
        [
            ("accuracy", "Accuracy / F1"),
            ("latency", "Latency budget"),
            ("bias", "Bias & fairness"),
            ("explainability", "Explainability"),
            ("safety", "Safety / abuse"),
        ],
        required=True,
        default="accuracy",
    )
    result = fields.Selection(
        [("passed", "Passed"), ("failed", "Failed")], required=True, default="passed"
    )
    checked_by = fields.Many2one("res.users", default=lambda self: self.env.user, readonly=True)
    checked_at = fields.Datetime(default=fields.Datetime.now, required=True)
    notes = fields.Char()


class FixMlGuardrail(models.Model):
    """A guard rail applied to a model's output (block, flag, fallback)."""

    _name = "fix.ml.guardrail"
    _description = "AI/ML Guard Rail"
    _order = "name"

    name = fields.Char(required=True)
    model_id = fields.Many2one("fix.ml.model", ondelete="cascade", index=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    rule = fields.Char(required=True, help="The condition, stated precisely.")
    threshold = fields.Float()
    action = fields.Selection(
        [
            ("flag", "Flag for human review"),
            ("block", "Block the output"),
            ("fallback", "Fall back to the deterministic rule"),
        ],
        required=True,
        default="flag",
    )
    active = fields.Boolean(default=True)
    note = fields.Char()
