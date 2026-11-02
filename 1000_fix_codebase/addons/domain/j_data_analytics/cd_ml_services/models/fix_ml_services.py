# fix_ml_services — M26: the honest AI/ML model registry + the inference run
# log. Every engine invoked by action_execute is REAL and measured (latency,
# output, caller); the demand-forecast entry fails closed until the M15
# consumption-history seam exists.
import json
import logging
import re
import time

from odoo import api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

MODEL_KINDS = [
    ("dispatch_scoring", "Dispatch Scoring (explainable ranking)"),
    ("fault_classifier", "Fault Classification (taxonomy match)"),
    ("predictive_maintenance", "Predictive Maintenance (M48)"),
    ("tradein_valuation", "Trade-In Valuation (grading)"),
    ("bi_aggregator", "BI Metric Aggregator (M25)"),
    ("demand_forecast", "Demand Forecast"),
    ("lead_scoring", "Lead Scoring (explainable factor weights, M07)"),
]

# The default weight vector for the lead-scoring engine, used when a model
# record carries no vector of its own. Positive weights add, negative
# weights subtract -- a risk factor is expressed as a negative weight rather
# than as a special case in code. These are a STARTING POINT for Sales to
# tune, not a fitted result, and the engine reports them with every score so
# nobody can mistake one for the other.
LEAD_SCORE_DEFAULT_WEIGHTS = {
    "is_corporate": 20,
    "criteria_confirmed": 20,
    "contract_verified": 15,
    "has_contact": 10,
    "existing_customer": 15,
    "revenue_at_or_above_100k": 20,
    "revenue_at_or_above_500k": 10,
    "competitor_present": -10,
    "stale_over_30_days": -15,
}


class FixMlModel(models.Model):
    """M26: one catalog entry per REAL engine — implementation and owning
    module are stated honestly; 'planned' entries describe seams, not
    fabricated capability."""

    _name = "fix.ml.model"
    _description = "AI/ML Model (Registry)"
    _order = "code"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    name = fields.Char(required=True)
    code = fields.Char(required=True, index=True)
    kind = fields.Selection(MODEL_KINDS, required=True)
    implementation = fields.Selection(
        [
            ("live_engine", "Live engine (deterministic, explainable)"),
            ("rule_based", "Rule-based (deterministic)"),
            ("planned", "Planned — seam exists, engine not built"),
        ],
        required=True,
        default="rule_based",
    )
    status = fields.Selection(
        [("production", "Production"), ("planned", "Planned")], required=True, default="production"
    )
    owning_module = fields.Char(
        string="Owning Module", help="The addon that implements the engine."
    )
    notes = fields.Text()
    weights_json = fields.Text(
        string="Factor Weights (JSON)",
        help="For an explainable factor engine: the weight vector, as governed "
        "data rather than a constant in code. Empty uses the engine default. "
        "These are weights somebody CHOSE, never weights anything fitted, and "
        "the engine returns them with every score so the two cannot be "
        "confused.",
    )

    def factor_weights(self):
        """The weight vector in force for this model."""
        self.ensure_one()
        if (self.weights_json or "").strip():
            try:
                loaded = json.loads(self.weights_json)
            except ValueError as exc:
                raise UserError(
                    "Model '%s' has invalid weights_json: %s" % (self.code, exc)
                ) from exc
            if not isinstance(loaded, dict):
                raise UserError(
                    "Model '%s' weights_json must be a JSON object of "
                    "factor -> weight." % self.code
                )
            return {str(k): float(v) for k, v in loaded.items()}
        return dict(LEAD_SCORE_DEFAULT_WEIGHTS)

    run_ids = fields.One2many("fix.ml.inference.run", "model_id", string="Inference Runs")
    run_count = fields.Integer(compute="_compute_run_stats")
    last_run_at = fields.Datetime(compute="_compute_run_stats")

    @api.depends("run_ids")
    def _compute_run_stats(self):
        for rec in self:
            runs = (
                self.env["fix.ml.inference.run"]
                .sudo()
                .search([("model_id", "=", rec.id)], order="ran_at desc", limit=1000)
            )
            rec.run_count = len(runs)
            rec.last_run_at = runs[:1].ran_at


class FixMlInferenceRun(models.Model):
    """M26: one measured inference run. action_execute dispatches to the real
    engine named by the model's kind and stores its actual output."""

    _name = "fix.ml.inference.run"
    _description = "AI/ML Inference Run"
    _order = "ran_at desc, id desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    model_id = fields.Many2one("fix.ml.model", required=True, ondelete="restrict")
    model_code = fields.Char(related="model_id.code", store=True)
    input_text = fields.Text(string="Input (free text)")
    field_order_id = fields.Many2one(
        "fix.field.order", string="Field Order (dispatch scoring input)"
    )
    state = fields.Selection(
        [("draft", "Draft"), ("computed", "Computed"), ("failed", "Failed")],
        default="draft",
        required=True,
    )
    output_json = fields.Text(string="Output (JSON)", readonly=True)
    latency_ms = fields.Integer(readonly=True)
    error_note = fields.Char(readonly=True)
    ran_at = fields.Datetime(default=fields.Datetime.now, required=True)
    ran_by = fields.Many2one("res.users", default=lambda self: self.env.user, readonly=True)
    # Human-in-the-loop capture: what the engine suggested, what the operator
    # finally did. This is the ONLY ground truth the platform records — the
    # override report counts it; accuracy is never estimated from nothing.
    suggested_value = fields.Char(string="Engine Suggestion", readonly=True)
    final_value = fields.Char(string="Final Human Decision")
    overridden = fields.Boolean(
        help="Set when the human decision differs from the engine suggestion."
    )
    override_reason = fields.Char()

    # ------------------------------------------------------------------
    # engines — every one is a real computation over live records
    # ------------------------------------------------------------------

    def _engine_dispatch_scoring(self):
        self.ensure_one()
        if not self.field_order_id:
            raise UserError("Dispatch scoring needs a Field Order as input.")
        return self.field_order_id.sudo().action_suggest_technicians(limit=5)

    def _engine_fault_classifier(self):
        self.ensure_one()
        text = (self.input_text or "").strip().lower()
        if not text:
            raise UserError("Fault classification needs input text.")
        tokens = {t for t in re.split(r"[^0-9a-zA-Z\u0980-\u09ff]+", text) if len(t) > 2}
        results = []
        codes = self.env["fix.fault.code"].sudo().search([("active", "=", True)])
        for code in codes:
            haystack = " ".join(
                part.lower() for part in (code.code, code.name, code.description or "") if part
            )
            hay_tokens = {
                t for t in re.split(r"[^0-9a-zA-Z\u0980-\u09ff]+", haystack) if len(t) > 2
            }
            overlap = tokens & hay_tokens
            score = len(overlap)
            if score:
                results.append(
                    {
                        "fault_code": code.code,
                        "name": code.name,
                        "category": code.category,
                        "severity": code.default_severity,
                        "matched_terms": sorted(overlap)[:6],
                        "score": score,
                    }
                )
        results.sort(key=lambda item: (-item["score"], item["fault_code"]))
        return results[:5]

    def _engine_predictive_maintenance(self):
        self.ensure_one()
        preds = self.env["fix.predictive.maintenance"].sudo().search([])
        by_state = {}
        for pred in preds:
            by_state[pred.prediction] = by_state.get(pred.prediction, 0) + 1
        imminent = [
            {"equipment": p.equipment_id.name, "days": p.estimated_days_to_failure}
            for p in preds
            if p.prediction == "failure_predicted"
        ][:10]
        return {
            "total_predictions": len(preds),
            "by_state": by_state,
            "failure_predicted": imminent,
        }

    def _engine_tradein_valuation(self):
        self.ensure_one()
        requests = self.env["fix.tradein.request"].sudo().search([])
        by_state = {}
        value_field = "inventory_valuation" if "inventory_valuation" in requests._fields else None
        values = [r[value_field] for r in requests if value_field and r[value_field]]
        for req in requests:
            by_state[req.state] = by_state.get(req.state, 0) + 1
        return {
            "total_requests": len(requests),
            "by_state": by_state,
            "avg_inventory_valuation": round(sum(values) / len(values), 2) if values else None,
        }

    def _engine_bi_aggregator(self):
        self.ensure_one()
        logs = self.env["fix.bi.sync.log"].sudo()
        freshness = logs.freshness_minutes()
        newest = logs.search([("status", "=", "success")], order="ran_at desc", limit=1)
        snapshot = json.loads(newest.snapshot_json) if newest and newest.snapshot_json else None
        return {"freshness_minutes": freshness, "latest_snapshot": snapshot}

    def _engine_lead_scoring(self):
        """Score one lead from live record facts and a declared weight vector.

        Explainable by construction: the return carries the score, every
        factor that fired, its weight, and the vector used. `rule_based` is a
        first-class implementation in this registry, and this engine is
        registered as exactly that -- it is deterministic and it is not a
        prediction.

        Input is the JSON payload M07 writes into `input_text`, which must
        carry `lead_id`. The lead is read LIVE rather than trusted from the
        payload: a score computed from stale caller-supplied values would be
        unauditable.
        """
        self.ensure_one()
        raw = (self.input_text or "").strip()
        if not raw:
            raise UserError("Lead scoring needs its JSON input payload.")
        try:
            payload = json.loads(raw)
        except ValueError as exc:
            raise UserError("Lead scoring input is not JSON: %s" % exc) from exc
        lead_id = payload.get("lead_id")
        if not lead_id:
            raise UserError("Lead scoring input carries no lead_id.")
        if "crm.lead" not in self.env:
            raise UserError(
                "crm.lead is not installed in this database, so no lead could " "be scored."
            )
        lead = self.env["crm.lead"].sudo().browse(int(lead_id)).exists()
        if not lead:
            raise UserError("Lead %s does not exist." % lead_id)

        weights = self.model_id.factor_weights()
        revenue = lead.expected_revenue or 0.0
        partner = lead.partner_id or getattr(lead, "linked_partner_id", False)
        age_days = (fields.Datetime.now() - lead.write_date).days if lead.write_date else 0
        facts = {
            "is_corporate": bool(lead.partner_name or (partner and partner.is_company)),
            "criteria_confirmed": bool(getattr(lead, "criteria_confirmed", False)),
            "contract_verified": bool(getattr(lead, "contract_verified", False)),
            "has_contact": bool(lead.email_from or lead.phone),
            "existing_customer": bool(getattr(lead, "linked_partner_id", False)),
            "revenue_at_or_above_100k": revenue >= 100000.0,
            "revenue_at_or_above_500k": revenue >= 500000.0,
            "competitor_present": bool((getattr(lead, "competitor", "") or "").strip()),
            "stale_over_30_days": age_days > 30,
        }

        contributions = []
        total = 0.0
        for factor, holds in facts.items():
            weight = weights.get(factor, 0.0)
            if not holds or not weight:
                continue
            total += weight
            contributions.append({"factor": factor, "weight": weight})
        score = max(0, min(100, int(round(total))))

        return {
            "lead_id": lead.id,
            "score": score,
            "band": "hot" if score >= 70 else ("warm" if score >= 40 else "cold"),
            "factors": contributions,
            "weights_used": weights,
            "implementation": self.model_id.implementation,
            "basis": "Deterministic weighted factor model. These are weights "
            "somebody chose, not weights anything fitted -- the registry "
            "records this engine as %s." % self.model_id.implementation,
            "expected_revenue": revenue,
            "age_days": age_days,
        }

    def _engine_demand_forecast(self):
        # Fail closed: the seam (fix.demand.plan.forecast_quantity expects an
        # M26 model) exists, but no consumption-history source is wired yet —
        # a fabricated forecast would violate the estate's honesty rules.
        raise UserError(
            "Demand forecast engine is not built yet — awaiting the M15 "
            "consumption-history seam. The registry entry stays 'planned'."
        )

    _ENGINES = {
        "dispatch_scoring": _engine_dispatch_scoring,
        "fault_classifier": _engine_fault_classifier,
        "predictive_maintenance": _engine_predictive_maintenance,
        "tradein_valuation": _engine_tradein_valuation,
        "bi_aggregator": _engine_bi_aggregator,
        "demand_forecast": _engine_demand_forecast,
        "lead_scoring": _engine_lead_scoring,
    }

    def action_execute(self):
        """Run the model's REAL engine and record output + measured latency."""
        for rec in self:
            engine = self._ENGINES.get(rec.model_id.kind)
            if not engine:
                raise UserError("No engine registered for model kind %s" % rec.model_id.kind)
            started = time.perf_counter()
            try:
                output = engine(rec)
            except UserError as exc:
                rec.write({"state": "failed", "error_note": str(exc), "latency_ms": 0})
                continue
            elapsed_ms = int((time.perf_counter() - started) * 1000)
            rec.write(
                {
                    "state": "computed",
                    "output_json": json.dumps(output, default=str, indent=2, ensure_ascii=False),
                    "latency_ms": elapsed_ms,
                    "error_note": False,
                }
            )
            _logger.info("M26 inference %s computed in %dms", rec.model_id.code, elapsed_ms)
        return True
