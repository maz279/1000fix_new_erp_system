# M26 assurance records (capture audit 2026-11-14): the evidence the
# Deployment & Monitoring and GenAI & RAG sub-module pages capture.
#
# Before this, those pages had nothing to capture. "Deployment & Monitoring"
# was create:false, so the fallback test the spec makes a hard rule
# (BRU-AIM-06 / FR-AIM-013: "record the result") and the drift observations
# the monitoring run produces (FR-AIM-009, T-06) had no record at all - the
# drift score was a number typed on the version, with no history. The AI risk
# register (spec §3.1 #13, §10.1 fix.ai.risk, BRU-AIM-26) did not exist, so
# the risks that gate a self-hosted GenAI roll-out (customer data leaving the
# estate, prompt injection, ungrounded answers) had nowhere to be recorded.
#
#   fix.ml.fallback.test     evidence that a consumer's fallback works when the
#                            model is switched off; append-only
#   fix.ml.drift.observation one monitoring observation (PSI / KS per feature)
#                            for a deployed version; append-only; the version's
#                            drift score follows the newest observations
#   fix.ml.ai.risk           the AI risk register: a reviewed, owned register
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools.translate import _

# A PSI at or above 0.2 is the conventional "significant shift" line, and the
# Drift Report already bands >= 0.2 as an alert; an observation may state its
# own threshold.
DEFAULT_PSI_THRESHOLD = 0.2


class FixMlFallbackTest(models.Model):
    """One fallback test: the model was disabled (or its failure simulated)
    and the consuming module's behaviour was observed. BRU-AIM-06: every
    consumer has a TESTED fallback - this row is that test. Evidence:
    append-only, the tester is stamped."""

    _name = "fix.ml.fallback.test"
    _description = "AI/ML Fallback Test"
    _order = "tested_at desc, id desc"
    _rec_name = "consumer_module"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    model_id = fields.Many2one("fix.ml.model", required=True, ondelete="restrict", index=True)
    model_code = fields.Char(related="model_id.code", store=True)
    consumer_module = fields.Char(
        required=True,
        help="The consuming module whose fallback was exercised, e.g. 'M02 dispatch'.",
    )
    method = fields.Selection(
        [
            ("disabled", "Model disabled (gateway returned the fallback)"),
            ("simulated", "Failure simulated (timeout / low confidence)"),
        ],
        required=True,
    )
    consumer_behaviour = fields.Text(
        required=True,
        help="What the consuming module actually did while the model was unavailable.",
    )
    outcome = fields.Selection(
        [("passed", "Passed - the process carried on"), ("failed", "Failed - the process blocked")],
        required=True,
    )
    incidents_raised = fields.Integer(help="Incidents the test raised (target zero).")
    tested_at = fields.Datetime(required=True, default=fields.Datetime.now)
    tested_by = fields.Many2one("res.users", readonly=True, index=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals["tested_by"] = self.env.user.id
        return super().create(vals_list)

    @api.constrains("incidents_raised")
    def _check_incidents(self):
        for rec in self:
            if rec.incidents_raised < 0:
                raise ValidationError(_("Incidents raised cannot be negative."))

    def write(self, vals):
        raise UserError(
            _("A fallback test is evidence and cannot be edited (M26) - record a new test.")
        )

    def unlink(self):
        raise UserError(_("A fallback test is evidence and cannot be deleted (M26)."))


class FixMlDriftObservation(models.Model):
    """One drift observation from a monitoring run: a feature's population
    stability index (and KS statistic) for a deployed version. Breached is
    derived from the PSI and the threshold, never typed. The version's drift
    score is the highest PSI of its newest monitoring day."""

    _name = "fix.ml.drift.observation"
    _description = "AI/ML Drift Observation"
    _order = "observed_at desc, id desc"
    _rec_name = "feature_name"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    version_id = fields.Many2one(
        "fix.ml.model.version", required=True, ondelete="cascade", index=True
    )
    model_id = fields.Many2one(related="version_id.model_id", store=True, index=True)
    feature_name = fields.Char(required=True, help="The served feature that was checked.")
    psi = fields.Float(string="PSI", required=True, digits=(6, 4))
    ks_statistic = fields.Float(string="KS Statistic", digits=(6, 4))
    threshold = fields.Float(
        string="PSI Threshold", required=True, default=DEFAULT_PSI_THRESHOLD, digits=(6, 4)
    )
    breached = fields.Boolean(compute="_compute_breached", store=True)
    observed_at = fields.Datetime(required=True, default=fields.Datetime.now)
    note = fields.Char()
    recorded_by = fields.Many2one("res.users", readonly=True, index=True)

    @api.depends("psi", "threshold")
    def _compute_breached(self):
        for rec in self:
            rec.breached = rec.psi >= rec.threshold

    @api.constrains("psi", "ks_statistic", "threshold")
    def _check_values(self):
        for rec in self:
            if rec.psi < 0 or rec.threshold <= 0:
                raise ValidationError(
                    _("A PSI cannot be negative and the threshold must be above zero.")
                )
            if not 0 <= rec.ks_statistic <= 1:
                raise ValidationError(_("A KS statistic lies between 0 and 1."))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals["recorded_by"] = self.env.user.id
        versions = self.env["fix.ml.model.version"].browse(
            {v for vals in vals_list if (v := vals.get("version_id"))}
        )
        for version in versions:
            if version.state != "deployed":
                raise UserError(
                    _("Drift is observed on a version that serves: %s is %s, not deployed.")
                    % (version.display_name, version.state)
                )
        records = super().create(vals_list)
        records.mapped("version_id")._sync_drift_score()
        return records

    def write(self, vals):
        raise UserError(
            _("A drift observation is evidence and cannot be edited (M26) - record a new one.")
        )

    def unlink(self):
        raise UserError(_("A drift observation is evidence and cannot be deleted (M26)."))


class FixMlAiRisk(models.Model):
    """The AI risk register (spec §10.1 fix.ai.risk): a risk, by model or
    estate-wide (a generative roll-out has risks before any model exists),
    with its likelihood, impact, treatment, control, owner and review date.
    Reviewed at least annually (BRU-AIM-26)."""

    _name = "fix.ml.ai.risk"
    _description = "AI Risk Register Entry"
    _inherit = ["mail.thread"]
    _order = "review_date, id desc"
    _rec_name = "name"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    name = fields.Char(string="Risk", required=True, tracking=True)
    model_id = fields.Many2one(
        "fix.ml.model",
        ondelete="restrict",
        index=True,
        help="Empty for an estate-wide risk (e.g. a generative roll-out).",
    )
    category = fields.Selection(
        [
            ("bias", "Bias & fairness"),
            ("accuracy", "Accuracy & drift"),
            ("privacy", "Privacy & data protection"),
            ("security", "Security & prompt injection"),
            ("generative", "Generative AI (grounding, egress, labelling)"),
            ("availability", "Availability & fallback"),
            ("compliance", "Compliance & audit"),
        ],
        required=True,
        tracking=True,
    )
    description = fields.Text(required=True)
    likelihood = fields.Selection(
        [("low", "Low"), ("medium", "Medium"), ("high", "High")], required=True, tracking=True
    )
    impact = fields.Selection(
        [("low", "Low"), ("medium", "Medium"), ("high", "High")], required=True, tracking=True
    )
    treatment = fields.Text(help="What reduces the risk.")
    control_ref = fields.Char(
        string="Control Reference", help="The rule or control that holds it, e.g. BRU-AIM-10."
    )
    owner_id = fields.Many2one("res.users", string="Risk Owner", required=True, tracking=True)
    review_date = fields.Date(required=True, tracking=True)
    state = fields.Selection(
        [
            ("open", "Open"),
            ("treated", "Treated"),
            ("accepted", "Accepted"),
            ("closed", "Closed"),
        ],
        required=True,
        default="open",
        tracking=True,
    )
