# M07 — predictive lead and opportunity scoring (D365 Sales Insights parity).
#
# WHAT THE AUDIT FOUND. The dossier claimed lead scoring read "the M26
# registry"; it does not. The Scoring & Routing screen reads fix.pipeline
# stage-gating streams, M26's model records exist, and no M07 field held a
# score. So "scoring" named a screen, not a number.
#
# WHAT THIS DOES, and what it deliberately does not. A score is computed from
# a declared, inspectable factor set and written to `lead_score` with its
# reasons. When an M26 model is registered for leads, the score comes from
# that model instead and says so. When there is no model, the score is a
# TRANSPARENT HEURISTIC and is labelled `heuristic` — not "predictive".
#
# That labelling is the point. A heuristic presented as a prediction is the
# most expensive kind of wrong here: a seller who believes a number came from
# a trained model will drop a lead it scored low, and nobody will ever
# measure whether it should have. So `score_basis` is a field, it is shown,
# and the band thresholds are stated.
import json
import logging

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish  # FF-28

_logger = logging.getLogger(__name__)

# Band boundaries. Stated here rather than configured, because a band nobody
# can point at is a band that drifts to flatter the pipeline.
BAND_HOT = 70
BAND_WARM = 40


class FixCrmScoreFactor(models.Model):
    """One inspectable contribution to a lead score."""

    _name = "fix.crm.score.factor"
    _description = "Lead Score Factor"
    _order = "model_id, sequence, id"

    model_id = fields.Many2one("fix.crm.score.model", required=True, ondelete="cascade", index=True)
    sequence = fields.Integer(required=True, default=10)
    name = fields.Char(required=True)
    code = fields.Char(required=True)
    factor = fields.Selection(
        [
            ("source_quality", "Lead source"),
            ("corporate", "Corporate / company lead"),
            ("has_contact", "Reachable contact details"),
            ("expected_revenue", "Expected revenue at or above a threshold"),
            ("criteria_confirmed", "Qualification criteria confirmed"),
            ("existing_customer", "Already a customer party"),
            ("contract_verified", "Contract verified"),
            ("recent_activity", "Touched in the last N days"),
            ("competitor_present", "A competitor is named (negative)"),
            ("overdue_receivables", "Customer has overdue receivables (negative)"),
        ],
        required=True,
    )
    weight = fields.Float(
        required=True,
        default=10.0,
        help="Points added when the factor holds. Negative weights subtract, "
        "which is how a risk factor is expressed.",
    )
    threshold_value = fields.Char(
        help="For factors that compare: the revenue floor, the day count, or "
        "the comma-separated lead sources that count as good."
    )
    active = fields.Boolean(default=True)

    _code_unique = models.Constraint(
        "UNIQUE (model_id, code)", "A factor code is used once per scoring model."
    )

    def evaluate(self, lead):
        """Does this factor hold for this lead? Returns (bool, detail)."""
        self.ensure_one()
        if self.factor == "source_quality":
            good = {s.strip().lower() for s in (self.threshold_value or "").split(",") if s.strip()}
            actual = (lead.lead_source or "").strip().lower()
            return (actual in good), "source=%s" % (actual or "none")
        if self.factor == "corporate":
            partner = lead.partner_id or lead.linked_partner_id
            return bool(lead.partner_name or (partner and partner.is_company)), ""
        if self.factor == "has_contact":
            return bool(lead.email_from or lead.phone), ""
        if self.factor == "expected_revenue":
            try:
                floor = float(self.threshold_value or 0)
            except ValueError:
                return False, "threshold is not a number"
            return (lead.expected_revenue or 0.0) >= floor, "revenue=%.0f" % (
                lead.expected_revenue or 0.0
            )
        if self.factor == "criteria_confirmed":
            return bool(lead.criteria_confirmed), ""
        if self.factor == "existing_customer":
            return bool(lead.linked_partner_id), ""
        if self.factor == "contract_verified":
            return bool(lead.contract_verified), ""
        if self.factor == "recent_activity":
            try:
                days = int(self.threshold_value or 14)
            except ValueError:
                days = 14
            if not lead.write_date:
                return False, ""
            age = (fields.Datetime.now() - lead.write_date).days
            return age <= days, "last touched %d day(s) ago" % age
        if self.factor == "competitor_present":
            return bool((lead.competitor or "").strip()), lead.competitor or ""
        if self.factor == "overdue_receivables":
            partner = lead.linked_partner_id or lead.partner_id
            if not partner:
                return False, ""
            overdue = lead._overdue_receivables(partner)
            return bool(overdue), "overdue=%s" % overdue
        return False, ""


class FixCrmScoreModel(models.Model):
    """A named scoring model: either an M26 classifier or a declared heuristic."""

    _name = "fix.crm.score.model"
    _description = "Lead Scoring Model"
    _inherit = ["mail.thread"]
    _order = "sequence, id"

    sequence = fields.Integer(default=10)
    name = fields.Char(required=True)
    code = fields.Char(required=True, index=True)
    applies_to = fields.Selection(
        [("lead", "Leads"), ("opportunity", "Opportunities"), ("both", "Both")],
        required=True,
        default="both",
    )
    basis = fields.Selection(
        [
            ("heuristic", "Declared heuristic (inspectable factors)"),
            ("m26_model", "Registered M26 engine (deterministic — not a fitted model)"),
        ],
        required=True,
        default="heuristic",
        help="A heuristic is NOT a prediction, and the score records which it "
        "was. A seller who thinks a number came from a trained model will "
        "act on it differently. The registered M26 lead-scoring engine is "
        "rule-based: chosen factor weights over live facts, never a fitted "
        "statistical model — and it is labelled as exactly that.",
    )
    m26_model_ref = fields.Char(
        string="M26 Model Reference",
        help="The registered ML model to call. Resolved softly: when M26 is "
        "absent the model reports that rather than scoring silently.",
    )
    factor_ids = fields.One2many("fix.crm.score.factor", "model_id", string="Factors", copy=True)
    state = fields.Selection(
        [("draft", "Draft"), ("active", "Active"), ("retired", "Retired")],
        required=True,
        default="draft",
        tracking=True,
    )
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company
    )

    _code_unique = models.Constraint("UNIQUE (code)", "Each scoring model code exists once.")

    @api.constrains("basis", "factor_ids", "m26_model_ref")
    def _check_model_can_score(self):
        for rec in self:
            if rec.basis == "heuristic" and not rec.factor_ids:
                raise ValidationError(
                    "Heuristic model '%s' declares no factors, so every lead "
                    "would score zero." % rec.name
                )
            if rec.basis == "m26_model" and not (rec.m26_model_ref or "").strip():
                raise ValidationError(
                    "Model '%s' claims an M26 basis but names no model." % rec.name
                )

    def action_activate(self):
        for rec in self:
            rec.state = "active"
        return True

    @api.model
    def active_model_for(self, lead):
        kind = "opportunity" if lead.type == "opportunity" else "lead"
        return self.sudo().search(
            [
                ("state", "=", "active"),
                ("active", "=", True),
                ("applies_to", "in", ("both", kind)),
            ],
            order="sequence, id",
            limit=1,
        )

    def score(self, lead):
        """Score one lead. Returns {score, band, basis, reasons}."""
        self.ensure_one()
        if self.basis == "m26_model":
            return self._score_via_m26(lead)
        total = 0.0
        reasons = []
        for factor in self.factor_ids.filtered("active").sorted(lambda f: (f.sequence, f.id)):
            holds, detail = factor.evaluate(lead)
            if not holds:
                continue
            total += factor.weight
            reasons.append(
                "%s %+.0f%s" % (factor.name, factor.weight, (" (%s)" % detail) if detail else "")
            )
        bounded = max(0, min(100, int(round(total))))
        return {
            "score": bounded,
            "band": self._band(bounded),
            "basis": "heuristic",
            "reasons": "; ".join(reasons) or "No scoring factor applied.",
            "model": self.code,
        }

    def _score_via_m26(self, lead):
        """Ask M26 through its real API, and report honestly when it cannot.

        M26's interface is fix.ml.inference.run: create a run against a
        registered fix.ml.model, call action_execute(), read output_json.
        action_execute() raises when no engine is registered for the model's
        kind, and at the time of writing M26 registers six kinds, none of
        them lead scoring.

        Three things this deliberately does NOT do, because each would put a
        number in front of a seller that the number does not deserve:
        it does not invent a model; it does not register the M07 heuristic as
        an M26 model and report it as a prediction; and it does not fall back
        to the heuristic silently under an 'm26_model' label. An absent model
        yields the ABSENCE of a score, which is different from a score of
        zero and is labelled differently.
        """
        self.ensure_one()
        Registry = self.env.get("fix.ml.model")
        Run = self.env.get("fix.ml.inference.run")
        if Registry is None or Run is None:
            return {
                "score": 0,
                "band": "unscored",
                "basis": "m26_unavailable",
                "reasons": "The M26 model registry is not installed in this "
                "database, so no prediction was made. This is the absence of "
                "a score, not a score of zero.",
                "model": self.code,
            }
        model = Registry.sudo().search(
            ["|", ("name", "=", self.m26_model_ref), ("code", "=", self.m26_model_ref)],
            limit=1,
        )
        if not model:
            return {
                "score": 0,
                "band": "unscored",
                "basis": "m26_unavailable",
                "reasons": "No registered M26 model matches %r." % self.m26_model_ref,
                "model": self.code,
            }
        payload = json.dumps(
            {
                "lead_id": lead.id,
                "lead_source": lead.lead_source or "",
                "expected_revenue": lead.expected_revenue or 0.0,
                "is_corporate": bool(lead.partner_name),
                "criteria_confirmed": bool(lead.criteria_confirmed),
                "contract_verified": bool(lead.contract_verified),
                "has_competitor": bool(lead.competitor),
            },
            ensure_ascii=False,
        )
        run = (
            Run.sudo()
            .with_context(ml_inference_gateway=True)
            .create(
                {
                    "model_id": model.id,
                    "input_text": payload,
                    "company_id": lead.company_id.id or self.env.company.id,
                }
            )
        )
        try:
            run.action_execute()
        except UserError as exc:
            # The expected path today: M26 registers no engine for this kind.
            return {
                "score": 0,
                "band": "unscored",
                "basis": "m26_unavailable",
                "reasons": "M26 model '%s' (kind %s) has no registered engine, "
                "so nothing was predicted: %s. The seam is wired; the model "
                "side is not built." % (model.code, model.kind, exc),
                "model": self.code,
            }
        if run.state != "computed":
            return {
                "score": 0,
                "band": "unscored",
                "basis": "m26_unavailable",
                "reasons": "M26 run %d did not compute: %s"
                % (run.id, run.error_note or "no reason recorded"),
                "model": self.code,
            }
        try:
            output = json.loads(run.output_json or "{}")
        except ValueError:
            output = {}
        raw = output.get("score", output.get("probability"))
        if raw is None:
            return {
                "score": 0,
                "band": "unscored",
                "basis": "m26_unavailable",
                "reasons": "M26 run %d returned no 'score' or 'probability' "
                "key, so there is nothing to read as a score." % run.id,
                "model": self.code,
            }
        numeric = float(raw)
        # A probability comes back 0..1; a score comes back 0..100. Both are
        # accepted and normalised to the same scale.
        bounded = max(0, min(100, int(round(numeric * 100 if numeric <= 1 else numeric))))
        return {
            "score": bounded,
            "band": self._band(bounded),
            "basis": "m26_model",
            "reasons": "Scored by the registered M26 engine %s "
            "(implementation %s — chosen factor weights, not a fitted "
            "prediction; run %d, %dms)."
            % (model.code, model.implementation, run.id, run.latency_ms or 0),
            "model": self.code,
        }

    @api.model
    def _band(self, score):
        if score >= BAND_HOT:
            return "hot"
        if score >= BAND_WARM:
            return "warm"
        return "cold"


class CrmLeadScoring(models.Model):
    """The score field the dossier claimed existed, and the routing action."""

    _inherit = "crm.lead"

    lead_score = fields.Integer(
        string="Lead Score",
        readonly=True,
        copy=False,
        index=True,
        help="0-100. Written only by the scoring engine; score_basis says " "what produced it.",
    )
    lead_score_band = fields.Selection(
        [
            ("hot", "Hot"),
            ("warm", "Warm"),
            ("cold", "Cold"),
            ("unscored", "Not scored"),
        ],
        readonly=True,
        copy=False,
        default="unscored",
    )
    lead_score_basis = fields.Selection(
        [
            ("heuristic", "Declared heuristic"),
            ("m26_model", "Registered M26 engine (deterministic rules)"),
            ("m26_unavailable", "M26 unavailable — not scored"),
        ],
        readonly=True,
        copy=False,
        help="Never hidden. A heuristic shown as a prediction changes what a "
        "seller does with it.",
    )
    lead_score_reasons = fields.Text(readonly=True, copy=False)
    lead_score_model_id = fields.Many2one(
        "fix.crm.score.model", string="Scoring Model", readonly=True, copy=False
    )
    lead_scored_at = fields.Datetime(readonly=True, copy=False)

    def action_score(self):
        """Score these leads with the active model."""
        Model = self.env["fix.crm.score.model"]
        for lead in self:
            model = Model.active_model_for(lead)
            if not model:
                lead.write(
                    {
                        "lead_score": 0,
                        "lead_score_band": "unscored",
                        "lead_score_basis": False,
                        "lead_score_reasons": "No active scoring model applies "
                        "to this record type.",
                        "lead_scored_at": fields.Datetime.now(),
                    }
                )
                continue
            result = model.score(lead)
            lead.write(
                {
                    "lead_score": result["score"],
                    "lead_score_band": result["band"],
                    "lead_score_basis": result["basis"],
                    "lead_score_reasons": result["reasons"],
                    "lead_score_model_id": model.id,
                    "lead_scored_at": fields.Datetime.now(),
                }
            )
        return True

    def action_route_by_score(self, sequence=None):
        """Put hot leads on a cadence. The routing half of the gap row.

        A score with no consequence is a decoration, which is what the
        Scoring & Routing screen amounted to. Enrolling a hot lead on a
        sequence is the consequence.
        """
        Sequence = self.env["fix.crm.sequence"]
        target = sequence
        if target is None:
            # fix.crm.sequence has no `sequence` field (A03 audit G-M07-4:
            # ordering by it raised "Invalid field"); the oldest active
            # cadence is the default route.
            target = Sequence.sudo().search(
                [("state", "=", "active"), ("sequence_kind", "=", "cadence")],
                order="id",
                limit=1,
            )
        if not target:
            raise UserError(
                "No active sales cadence exists to route scored leads onto. "
                "Create and activate one first."
            )
        hot = self.filtered(lambda lead: lead.lead_score_band == "hot")
        if not hot:
            return {"routed": 0, "note": "No hot leads in this selection."}
        enrolled = target.enrol(hot)
        publish(
            self.env,
            "lead.routed_by_score",
            "crm.lead",
            hot[0].id,
            {
                "sequence": target.code,
                "leads": len(enrolled),
                "band": "hot",
                "basis": hot[0].lead_score_basis,
            },
        )
        return {"routed": len(enrolled), "sequence": target.code}

    @api.model
    def cron_rescore_open_leads(self, limit=2000):
        """Re-score open pipeline nightly. A stale score misleads.

        A03 audit G-M07-8: cron 56 on fix_dev failed on its only run
        (failure_count=1, 0 leads ever scored), while the same method scores
        cleanly on fix_test and fix_test_m07, run directly and through its
        ir.cron server action (where the cron also shows failure_count 0).
        The cron was created with nextcall=now, so its one run was the
        install-time first fire, and two other A03 crons (M33 dedup, M10
        requalify) failed in the same second on fix_dev (2026-11-02 01:16).
        That points to a shared trigger, most likely the running 8069 server
        firing new crons with Python classes that predated the `-u`, rather
        than to this code; fix_dev's log was not available to confirm it.
        Whatever the trigger, the old method ran every lead in one
        transaction, so any one failure scored nobody. Now each lead is scored
        in its own savepoint and a failure is counted and logged, and new M07
        crons are first scheduled for the following night.
        """
        leads = self.sudo().search(
            [("active", "=", True), ("stage_id.is_won", "=", False)], limit=limit
        )
        scored, failed = 0, 0
        for lead in leads:
            try:
                with self.env.cr.savepoint():
                    lead.action_score()
                scored += 1
            except Exception:  # one lead must not cost the others their score
                failed += 1
                _logger.exception("M07 rescore: lead %s could not be scored", lead.id)
        return {"scored": scored, "failed": failed}
