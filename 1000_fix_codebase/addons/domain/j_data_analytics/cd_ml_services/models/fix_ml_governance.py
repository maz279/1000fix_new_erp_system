# M26 governance: model versions, evaluation gates, guard rails.
#
# A11 audit G7 (M26-1/-2/-9/-11): promotion used to be a field anyone with
# admin typed — a version with two FAILED gates went draft->deployed in one
# write and nobody stamped who deployed it. Now a version is BORN DRAFT, is
# promoted only through the M63 approval engine (a Model Owner who is not the
# registrant decides from their inbox), and only after every evaluation gate
# reads 'passed' by a reviewer who is not the registrant. Gates default
# PENDING — an unevaluated gate can no longer pose as a passed one — and once
# recorded a gate row is evidence: append-only.
import operator
import re

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools.translate import _

from libs.py.fix_events import publish

# Kinds whose output affects people (spec §13 names dispatch ranking and
# seller-facing lead scores): promoting one of these without a PASSED bias
# gate is refused — 'untested' is not silently treated as 'passed'.
PEOPLE_AFFECTING_KINDS = {"dispatch_scoring", "lead_scoring"}

MODEL_OWNER_GROUP = "cd_ml_services.group_ml_model_owner"


def _bias_follows_test(env):
    return env._(
        "The bias status follows the recorded bias test (BRU-AIM-07): record a "
        "Bias Test on Evaluation Gates - it is not typed on the version."
    )


# ---- guard-rail rule syntax (shared with the inference path) --------------
#
# A rail is `<key> <op> <number>` — e.g. 'score >= 40', 'confidence < 0.60'.
# The condition says when the rail FIRES; `action` says what happens then.
_GUARDRAIL_RULE_RE = re.compile(
    r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*(>=|<=|>|<|=)\s*(-?\d+(?:\.\d+)?)\s*$"
)
_GUARDRAIL_OPS = {
    ">=": operator.ge,
    "<=": operator.le,
    ">": operator.gt,
    "<": operator.lt,
    "=": operator.eq,
}


def parse_guardrail_rule(rule):
    """(key, op_fn, threshold) for a well-formed rail rule, else None. The
    inference path and the save-time constraint share this, so what saves is
    exactly what executes."""
    match = rule and _GUARDRAIL_RULE_RE.match(rule.strip())
    if not match:
        return None
    key, op_str, number = match.groups()
    return key, _GUARDRAIL_OPS[op_str], float(number)


class FixMlModelVersion(models.Model):
    """One version of a registered model: artifact, metrics, bias/drift
    observations, deployment mode and the model card."""

    _name = "fix.ml.model.version"
    _description = "AI/ML Model Version"
    _inherit = ["mail.thread", "fix.approvable.mixin"]
    _order = "model_id, version desc"

    # ---- the M63 routing contract (G7) --------------------------------------
    _approval_routed = True
    _approval_domain = "ml_promotion"
    _approval_apply_method = "action_deploy"
    _approval_group = MODEL_OWNER_GROUP

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
    # Capture audit pass 2 (2026-11-19): the bias status FOLLOWS the newest
    # bias test (fix.ml.bias.test) - it used to be typed on the version by the
    # person who registered it.
    bias_status = fields.Selection(
        [("untested", "Untested"), ("passed", "Passed"), ("failed", "Failed")],
        required=True,
        default="untested",
    )
    training_run_id = fields.Many2one(
        "fix.ml.training.run",
        string="Training Run",
        ondelete="restrict",
        index=True,
        help="The reproducible run that produced this version (FR-AIM-004 lineage).",
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
            ("demoted", "Auto-Demoted"),
            ("retired", "Retired"),
        ],
        required=True,
        default="draft",
        copy=False,
        tracking=True,
    )
    approved_by = fields.Many2one("res.users", readonly=True, copy=False)
    deployed_at = fields.Datetime(readonly=True, copy=False)
    demoted_at = fields.Datetime(readonly=True, copy=False)
    demotion_reason = fields.Char(readonly=True, copy=False)
    gate_ids = fields.One2many("fix.ml.evaluation.gate", "version_id", string="Evaluation Gates")
    drift_observation_ids = fields.One2many(
        "fix.ml.drift.observation", "version_id", string="Drift Observations"
    )
    bias_test_ids = fields.One2many("fix.ml.bias.test", "version_id", string="Bias Tests")
    performance_ids = fields.One2many(
        "fix.ml.performance.observation", "version_id", string="Production Performance"
    )

    @api.constrains("training_run_id", "model_id")
    def _check_training_run(self):
        for rec in self:
            run = rec.training_run_id
            if not run:
                continue
            if run.model_id != rec.model_id:
                raise ValidationError(
                    _("Training run %s trained model %s, not %s.")
                    % (run.display_name, run.model_id.code, rec.model_id.code)
                )
            if run.outcome != "succeeded":
                raise ValidationError(
                    _("Training run %s did not succeed: it produced no version.") % run.display_name
                )

    def _sync_drift_score(self):
        """drift_score = the highest PSI observed on the version's newest
        monitoring day (capture audit 2026-11-14). Written by the engine: the
        observation is the evidence, the score its summary."""
        observations = self.env["fix.ml.drift.observation"].sudo()
        for version in self:
            rows = observations.search([("version_id", "=", version.id)])
            if not rows:
                continue
            newest = max(rows.mapped("observed_at")).date()
            score = max(r.psi for r in rows if r.observed_at.date() == newest)
            version.sudo().write({"drift_score": score})

    # M26-9: the stored compute had no @api.depends, so every version was
    # named False. It depends on exactly what it reads.
    @api.depends("model_id.code", "version")
    def _compute_name(self):
        for rec in self:
            rec.name = "%s %s" % (rec.model_id.code or "?", rec.version or "")

    # ---- lifecycle guards (M26-1) -------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        # A version is born DRAFT; state/approved_by/deployed_at belong to
        # the engine (or the superuser seeding baselines).
        for vals in vals_list:
            if not self.env.su and any(
                vals.get(k)
                for k in ("state", "approved_by", "deployed_at", "demoted_at", "demotion_reason")
            ):
                raise UserError(
                    _(
                        "A model version is created as a DRAFT and reaches "
                        "'deployed' only through a promotion request (M26) — "
                        "state, approver and deploy date are not typeable."
                    )
                )
            if not self.env.su and vals.get("bias_status", "untested") not in (
                False,
                "untested",
            ):
                raise UserError(_bias_follows_test(self.env))
        return super().create(vals_list)

    def write(self, vals):
        engine = self.env.su or self.env.context.get("ml_promotion_engine")
        if not engine and any(
            k in vals
            for k in ("state", "approved_by", "deployed_at", "demoted_at", "demotion_reason")
        ):
            raise UserError(
                _(
                    "A model version changes state only through its lifecycle "
                    "actions (Request Promotion / Deploy / Retire), never by "
                    "editing the field (M26)."
                )
            )
        if (
            not self.env.su
            and "bias_status" in vals
            and any(rec.bias_status != vals["bias_status"] for rec in self)
        ):
            raise UserError(_bias_follows_test(self.env))
        return super().write(vals)

    # ---- the registrant / reviewer contract ---------------------------------
    def _registrant_id(self):
        """Who registered this version (SoD reference point)."""
        self.ensure_one()
        return self.create_uid

    def action_evaluate(self):
        """Draft -> evaluated: the registrant has keyed in the measured
        metrics and the model card, and asks for gate reviews."""
        for rec in self:
            if rec.state != "draft":
                raise UserError(_("Only a draft version can be marked evaluated."))
            if not (rec.model_card or "").strip():
                raise UserError(
                    _(
                        "Complete the model card before evaluation — purpose, "
                        "intended use and limitations are part of the record, "
                        "not decoration (BRU-AIM-08)."
                    )
                )
            if not (rec.metrics_json or "").strip():
                raise UserError(
                    _(
                        "Key in the measured metrics from the evaluation run "
                        "before asking for gate reviews — no number is invented."
                    )
                )
            rec.with_context(ml_promotion_engine=True).write({"state": "evaluated"})
        return True

    def _assert_gates_promotable(self):
        """Every gate 'passed', recorded by a reviewer who is not the
        registrant; a version with no gates fails closed."""
        self.ensure_one()
        gates = self.gate_ids
        registrant = self._registrant_id()
        if not gates:
            raise UserError(
                _(
                    "Version %s has no evaluation gate results — promotion "
                    "fails closed until a reviewer records them."
                )
                % self.display_name
            )
        not_passed = gates.filtered(lambda g: g.result != "passed")
        if not_passed:
            raise UserError(
                _(
                    "Version %s cannot be promoted: gate(s) %s are %s. Every "
                    "gate must read 'passed' — a pending or failed gate "
                    "blocks deployment (BRU-AIM-13)."
                )
                % (
                    self.display_name,
                    ", ".join(not_passed.mapped("gate")),
                    ", ".join(
                        dict(not_passed._fields["result"].selection)[r]
                        for r in not_passed.mapped("result")
                    ),
                )
            )
        own = gates.filtered(lambda g: g.checked_by and g.checked_by == registrant)
        if own:
            raise UserError(
                _(
                    "Version %s cannot be promoted: gate(s) %s were recorded "
                    "by the registrant %s. A gate counts only when a "
                    "reviewer who did not register the version signed it "
                    "(spec §13 SoD)."
                )
                % (self.display_name, ", ".join(own.mapped("gate")), registrant.name)
            )
        if self.bias_status == "failed":
            raise UserError(
                _(
                    "Version %s failed its bias review — a failed bias gate "
                    "blocks every promotion."
                )
                % self.display_name
            )
        # BRU-AIM-12 (capture audit pass 2): the newest data-sufficiency gate
        # of the model must read 'met'. None recorded fails closed, as gates do.
        sufficiency = (
            self.env["fix.ml.data.sufficiency"]
            .sudo()
            .search(
                [("model_id", "=", self.model_id.id)], order="evaluated_at desc, id desc", limit=1
            )
        )
        if not sufficiency:
            raise UserError(
                _(
                    "Model %s has no data-sufficiency gate - promotion fails "
                    "closed until the training data is measured against the "
                    "model's declared minimum history and volume (BRU-AIM-12)."
                )
                % self.model_id.code
            )
        if sufficiency.result != "met":
            raise UserError(
                _(
                    "Model %s is deferred: its newest data-sufficiency gate "
                    "found the prerequisite unmet (revisit %s). A model cannot "
                    "be promoted on insufficient data (BRU-AIM-12)."
                )
                % (self.model_id.code, sufficiency.deferred_until or "-")
            )
        if self.model_id.kind in PEOPLE_AFFECTING_KINDS and self.bias_status != "passed":
            raise UserError(
                _(
                    "Model kind '%s' affects people, so version %s needs a "
                    "PASSED bias review before promotion — 'untested' is not "
                    "'passed' (BRU-AIM-07)."
                )
                % (self.model_id.kind, self.display_name)
            )
        # BRU-AIM-11 (A2-F10): a model deploys only with a named consumer, an
        # accuracy target and a defined fallback — "or not deployed". The rule
        # runs at PROMOTION only, so the grandfathered deployed baselines keep
        # serving; it is NEW promotions that fail closed until the owner
        # completes the declaration. An advisory model states no target (the
        # BI aggregator measures nothing it could miss), so the target is
        # demanded of every other risk class.
        missing = []
        if not (self.model_id.consumer_modules or "").strip():
            missing.append("a named consumer (Named Consumer(s))")
        if not (self.model_id.fallback_definition or "").strip():
            missing.append("a defined fallback (Defined Fallback)")
        if (
            self.model_id.risk_class != "advisory"
            and not (self.model_id.accuracy_target or "").strip()
        ):
            missing.append("an accuracy target (Accuracy Target)")
        if missing:
            raise UserError(
                _(
                    "Model %s cannot be promoted: its portfolio declaration "
                    "lacks %s. A model without a consumer, a target and a "
                    "fallback is not deployed (BRU-AIM-11). Declare the "
                    "missing %s on its Portfolio Declaration, or retire the "
                    "model."
                )
                % (self.model_id.code, " and ".join(missing), "entry/entries")
            )

    def action_request_promotion(self, justification=None):
        """Route the promotion through M63: a Model Owner who is not the
        registrant decides. Refused before routing unless every gate holds."""
        for rec in self:
            if rec.state not in ("draft", "evaluated"):
                raise UserError(
                    _("Only a draft or evaluated version can request promotion (current: %s).")
                    % rec.state
                )
            rec._assert_gates_promotable()
            rec.action_request_approval(
                justification=justification
                or "Deploy %s %s (%s)" % (rec.model_id.code, rec.version, rec.model_id.kind)
            )
        return True

    def action_deploy(self):
        """The engine calls this AS THE MODEL OWNER once the request is
        granted: stamp state/approver/deploy date. Nothing else reaches here
        (the routed assert is the proof)."""
        self._approval_assert_routed()
        for rec in self:
            if rec.state not in ("draft", "evaluated", "approved"):
                raise UserError(
                    _("Only a draft/evaluated/approved version can deploy (current: %s).")
                    % rec.state
                )
            approver = rec.env.user
            if approver == rec._registrant_id():
                raise UserError(
                    _(
                        "The registrant cannot deploy their own version — the "
                        "promotion must be decided by another Model Owner "
                        "(spec §13 SoD)."
                    )
                )
            rec.with_context(ml_promotion_engine=True).write(
                {
                    "state": "deployed",
                    "approved_by": approver.id,
                    "deployed_at": fields.Datetime.now(),
                }
            )
            rec.message_post(
                body=_(
                    "Deployed by %s through the M63 promotion request. "
                    "Serving resolves this version from now on."
                )
                % approver.name
            )
            # A2-F09: the promotion is a domain event — its consumer posts the
            # audit trail on the model's chatter (and any future GRC subscriber
            # reads it from the outbox).
            publish(
                self.env,
                "model.promoted",
                "fix.ml.model",
                rec.model_id.id,
                {
                    "model": rec.model_id.code,
                    "version": rec.version,
                    "actor": approver.name,
                    "reason": _(
                        "Deployed through the M63 promotion request; serving resolves this version."
                    ),
                },
            )
        return True

    def action_retire(self, confirmation=None):
        """Deployed (or auto-demoted) -> retired: a Model Owner's act, never a
        field edit. FR-AIM-010 / AUT-AIM-22: retirement is blocked without the
        consumers' confirmation that the fallback is now the standing path -
        the confirmation is recorded on the version."""
        for rec in self:
            if rec.state not in ("deployed", "demoted"):
                raise UserError(
                    _("Only a deployed or demoted version can be retired (current: %s).")
                    % rec.state
                )
            if not (self.env.su or self.env.user.has_group(MODEL_OWNER_GROUP)):
                raise UserError(_("Retiring a deployed version is a Model Owner act (M26)."))
            if not self.env.su and not (confirmation or "").strip():
                raise UserError(
                    _(
                        "Record the consumers' confirmation before retiring %s: who "
                        "confirmed that the fallback (%s) is now the standing path "
                        "(FR-AIM-010)."
                    )
                    % (rec.display_name, rec.model_id.fallback_definition or "not declared")
                )
            rec.with_context(ml_promotion_engine=True).write({"state": "retired"})
            if (confirmation or "").strip():
                rec.message_post(
                    body=_("Retired by %s. Consumer confirmation: %s")
                    % (self.env.user.name, confirmation.strip())
                )
            # A2-F09: retirement is a domain event too — consumers of the model
            # (and M60 GRC) learn the fallback is now the standing path.
            publish(
                self.env,
                "model.retired",
                "fix.ml.model",
                rec.model_id.id,
                {
                    "model": rec.model_id.code,
                    "version": rec.version,
                    "actor": self.env.user.name,
                    "reason": (confirmation or "").strip()
                    or _("Retired by a Model Owner with no confirmation text."),
                },
            )
        return True

    def _approval_on_rejected(self, comment):
        for rec in self:
            rec.message_post(
                body=_("Promotion request rejected: %s") % (comment or "no comment recorded")
            )


class FixMlEvaluationGate(models.Model):
    """One evaluation gate result for a model version.

    A11 audit M26-1: `result` used to default to 'passed' — a gate nobody
    evaluated read as cleared. It now defaults to PENDING, the reviewer is
    stamped by the engine (not typed), a reviewer who is also the version's
    registrant is refused (four eyes), and a recorded gate row is evidence:
    append-only."""

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
        [
            ("pending", "Pending"),
            ("passed", "Passed"),
            ("failed", "Failed"),
        ],
        required=True,
        default="pending",
    )
    checked_by = fields.Many2one("res.users", readonly=True)
    checked_at = fields.Datetime(default=fields.Datetime.now, required=True)
    notes = fields.Char()

    @api.model_create_multi
    def create(self, vals_list):
        # checked_by is STAMPED, never typed (M26-1: the reviewer was
        # forgeable). A gate is recorded by the person who actually ran the
        # evaluation, who must not be the version's registrant.
        for vals in vals_list:
            vals["checked_by"] = self.env.user.id
        versions = (
            self.env["fix.ml.model.version"].browse(
                {v for vals in vals_list if (v := vals.get("version_id"))}
            )
            if any(vals.get("version_id") for vals in vals_list)
            else self.env["fix.ml.model.version"]
        )
        if not self.env.su:
            for rec in versions:
                if rec.create_uid and rec.create_uid == self.env.user:
                    raise UserError(
                        _(
                            "You registered version %s, so you cannot record "
                            "its gate results — a reviewer who is not the "
                            "registrant must sign them (spec §13 SoD)."
                        )
                        % rec.display_name
                    )
        records = super().create(vals_list)
        # A2-F09: a FAILED gate is a lifecycle event. On a deployed version it
        # is evidence only (it does not move the state — D-L15), but it is
        # exactly what the model's owner must learn about, so the consumer
        # raises a to-do for them (and posts the chatter record).
        for record in records.filtered(lambda g: g.result == "failed"):
            publish(
                self.env,
                "model.gate_failed",
                "fix.ml.model",
                record.version_id.model_id.id,
                {
                    "model": record.version_id.model_id.code,
                    "version": record.version_id.version,
                    "actor": (record.checked_by or self.env.user).name,
                    "gate": record.gate,
                    "reason": record.notes or _("Gate '%s' was recorded failed.") % record.gate,
                },
            )
        return records

    def write(self, vals):
        raise UserError(
            _("An evaluation gate row is evidence and cannot be edited (M26) — record a new gate.")
        )

    def unlink(self):
        raise UserError(_("An evaluation gate row is evidence and cannot be deleted (M26)."))


class FixMlGuardrail(models.Model):
    """A guard rail applied to a model's output on the inference path.

    A11 audit M26-2/G03: rails existed as configuration no engine read. The
    rule syntax the inference path enforces is `<key> <op> <number>` (for
    example ``score >= 40`` or ``confidence < 0.60``); `action` says what a
    violation does — block the output, flag it for human review, or engage
    the declared fallback. Every application is recorded on the inference
    run's output (the immutable decision log)."""

    _name = "fix.ml.guardrail"
    _description = "AI/ML Guard Rail"
    _order = "name"

    name = fields.Char(required=True)
    model_id = fields.Many2one("fix.ml.model", ondelete="cascade", index=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    rule = fields.Char(
        required=True,
        help="The condition, stated precisely: <key> <op> <number>, e.g. "
        "'score >= 40' or 'confidence < 0.60'. The key is read from the "
        "engine's output (a scalar key, or a key of each row when the output "
        "is a list).",
    )
    threshold = fields.Float(
        help="Derived from `rule` on every save (A2-F14): the parsed number in "
        "the rule is what the inference path enforces, so this field carries "
        "the same number for the screens and can never disagree with it."
    )
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

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            parsed = parse_guardrail_rule(vals.get("rule"))
            if parsed:
                # A2-F14(b): one source. The enforced number is parsed from
                # `rule`; `threshold` is written FROM it, so a rail cannot
                # display one number while the engine enforces another.
                vals["threshold"] = parsed[2]
        return super().create(vals_list)

    def write(self, vals):
        if "rule" in vals:
            vals = dict(vals)
            parsed = parse_guardrail_rule(vals.get("rule"))
            if parsed:
                vals["threshold"] = parsed[2]
            else:
                vals.pop("threshold", None)
        elif "threshold" in vals:
            # A threshold typed on its own states nothing the rule does not:
            # the rule is the enforced source, so the number is dropped rather
            # than saved as a decorative second value.
            vals = {key: value for key, value in vals.items() if key != "threshold"}
        return super().write(vals)

    @api.constrains("rule")
    def _check_rule(self):
        # What saves is what executes: a rail whose rule does not parse is
        # refused at save time, never silently skipped at inference time.
        for rec in self:
            if rec.rule and parse_guardrail_rule(rec.rule) is None:
                raise ValidationError(
                    _(
                        "Guard rail '%s': rule %r does not parse. State it as "
                        "<key> <op> <number>, e.g. 'score >= 40' or "
                        "'confidence < 0.60'."
                    )
                    % (rec.name, rec.rule)
                )


class FixMlWeightsRevision(models.Model):
    """A11 audit M26-A02 (model change control): every change to a model's
    factor weights is recorded as an immutable revision row — old vector, new
    vector, who, when. The weights govern every score the engine produces,
    so a silent edit changed the model without leaving a version, a gate or
    an approval behind. Revisions are written by the engine (sudo) only:
    they are an audit trail, not a form."""

    _name = "fix.ml.weights.revision"
    _description = "AI/ML Model Weights Revision"
    _order = "changed_at desc, id desc"
    _rec_name = "changed_at"

    model_id = fields.Many2one("fix.ml.model", required=True, ondelete="cascade", index=True)
    model_code = fields.Char(related="model_id.code", store=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    previous_json = fields.Text(string="Previous Weights (JSON)")
    new_json = fields.Text(string="New Weights (JSON)")
    changed_by = fields.Many2one(
        "res.users", default=lambda self: self.env.user, readonly=True, index=True
    )
    changed_at = fields.Datetime(default=fields.Datetime.now, required=True)

    def write(self, vals):
        raise UserError(
            _(
                "A weights revision is evidence and cannot be edited (M26) — the next change records a new row."
            )
        )

    def unlink(self):
        raise UserError(_("A weights revision is evidence and cannot be deleted (M26)."))


class FixApprovalMatrixM26Domains(models.Model):
    """Register M26's decision domain on the M63 matrix."""

    _inherit = "fix.approval.matrix"

    decision_domain = fields.Selection(
        selection_add=[("ml_promotion", "AI/ML Model Promotion")],
        ondelete=dict.fromkeys(("ml_promotion",), "cascade"),
    )
