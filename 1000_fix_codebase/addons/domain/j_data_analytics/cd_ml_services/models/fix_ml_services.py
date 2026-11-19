# fix_ml_services — M26: the honest AI/ML model registry + the inference run
# log. Every engine invoked by action_execute is REAL and measured (latency,
# output, caller); the demand-forecast entry fails closed until the M15
# consumption-history seam exists.
#
# A11 audit G7 (M26-3/-4/-5, X01, R01): serving now refuses a model with no
# DEPLOYED version (promotion runs through M63); guard rails are evaluated on
# the inference path and logged on every run; a run is born DRAFT and its
# engine-owned fields (state, output, latency, suggestion) are written only by
# the engine — a portal write can capture the human decision, never forge the
# machine's; and every engine reads its inputs as the CALLER, inside the
# caller's companies, under the caller's record rules — not through sudo.
import json
import logging
import re
import time

from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError
from odoo.tools.translate import _

from .fix_ml_governance import parse_guardrail_rule

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

# What the M26 spec (§5.3-5.5) declares for each kind the estate runs: the
# named consumer, the stated target and the defined fallback (FR-AIM-001).
# Lead scoring and the BI aggregator have no spec line, so no target or
# fallback is invented for them.
PORTFOLIO_FROM_SPEC = {
    "dispatch_scoring": {
        "consumer_modules": "M02 Dispatch",
        "accuracy_target": "70% auto-assign; dispatcher agreement >= 90% (FR-AIM-018)",
        "fallback_definition": "Rule-based scoring",
        "risk_class": "people_affecting",
    },
    "fault_classifier": {
        "consumer_modules": "M01 Service Orders, M32 Conversational AI",
        "accuracy_target": "Top-3 accuracy > 80% (FR-AIM-021)",
        "fallback_definition": "Manual fault selection",
        "risk_class": "operational",
    },
    "predictive_maintenance": {
        "consumer_modules": "M48 Predictive Maintenance, M08",
        "accuracy_target": "Precision > 70% (FR-AIM-025)",
        "fallback_definition": "Calendar-based maintenance",
        "risk_class": "operational",
    },
    "tradein_valuation": {
        "consumer_modules": "M14 Trade-In",
        "accuracy_target": "Within 10% of assessed value, 75% of the time (FR-AIM-027)",
        "fallback_definition": "Depreciation table",
        "risk_class": "financial",
    },
    "demand_forecast": {
        "consumer_modules": "M43 Demand Planning",
        "accuracy_target": "MAPE < 22% (FR-AIM-024)",
        "fallback_definition": "Moving average",
        "risk_class": "operational",
    },
    "lead_scoring": {
        "consumer_modules": "M07 Sales",
        "risk_class": "people_affecting",
    },
    "bi_aggregator": {
        "consumer_modules": "M25 Business Intelligence",
        "risk_class": "advisory",
    },
}

# Fields only the engine may ever set on a run (G7/R01): a portal write that
# reaches these would forge the machine's half of the decision log.
_ENGINE_OWNED_CREATE_FIELDS = (
    "state",
    "output_json",
    "latency_ms",
    "error_note",
    "suggested_value",
)
# What a human may capture on a computed run: their own decision, and why.
_HUMAN_WRITABLE_FIELDS = ("final_value", "override_reason")


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
    # ---- the portfolio register (FR-AIM-001, BRU-AIM-11) --------------------
    # Capture audit 2026-11-14: the catalogue entry recorded the engine but not
    # what the spec says every model must declare - who consumes it, the
    # target it must meet, the fallback when it cannot answer, its risk class,
    # its owner and when it is next reviewed.
    purpose = fields.Text(help="Why the model exists: the decision it informs.")
    consumer_modules = fields.Char(
        string="Named Consumer(s)", help="The consuming module(s), e.g. 'M02 Dispatch'."
    )
    accuracy_target = fields.Char(
        help="The stated target it is accepted against, e.g. 'top-3 accuracy > 80%'."
    )
    fallback_definition = fields.Text(
        string="Defined Fallback",
        help="What the consumer does when the model is unavailable, times out or abstains.",
    )
    risk_class = fields.Selection(
        [
            ("people_affecting", "People-affecting"),
            ("financial", "Financial"),
            ("operational", "Operational"),
            ("advisory", "Advisory"),
        ],
        help="People-affecting models need a passed bias review (BRU-AIM-07).",
    )
    owner_id = fields.Many2one("res.users", string="Model Owner", index=True)
    review_date = fields.Date(help="Next governance review (BRU-AIM-26: at least annually).")
    # The data-sufficiency prerequisite (FR-AIM-006, lifecycle §8.1): what the
    # training data must hold before the model may be trained or promoted.
    min_history_months = fields.Integer(
        string="Minimum History (months)",
        help="The months of history the training data must cover (BRU-AIM-12).",
    )
    min_volume = fields.Integer(
        string="Minimum Volume (labelled records)",
        help="The labelled records the training data must hold (BRU-AIM-12).",
    )
    weights_json = fields.Text(
        string="Factor Weights (JSON)",
        help="For an explainable factor engine: the weight vector, as governed "
        "data rather than a constant in code. Empty uses the engine default. "
        "These are weights somebody CHOSE, never weights anything fitted, and "
        "the engine returns them with every score so the two cannot be "
        "confused.",
    )
    version_ids = fields.One2many("fix.ml.model.version", "model_id", string="Versions")
    serving_version_id = fields.Many2one(
        "fix.ml.model.version",
        string="Serving Version",
        compute="_compute_serving_version",
        help="The newest DEPLOYED version. G7: inference refuses a model with "
        "none — a model nobody promoted does not serve.",
    )

    @api.model
    def _seed_portfolio_declarations(self):
        """Fill the portfolio declarations the module spec states for the
        estate's kinds (M26 spec §5.3-5.5: consumer, target, fallback) on
        entries that carry none. Only EMPTY fields are filled - a value an
        owner typed is never overwritten. Owner and review date stay empty:
        they are the owner's decision, not the spec's."""
        for model in self.sudo().search([]):
            declared = PORTFOLIO_FROM_SPEC.get(model.kind) or {}
            vals = {k: v for k, v in declared.items() if v and not model[k]}
            if vals:
                model.write(vals)
        return True

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

    def _serving_version(self):
        """The version serving resolves for this model, or empty. The lookup
        itself is privileged: serving integrity is a governance fact, not
        caller data (the boolean gates; nothing is exposed)."""
        self.ensure_one()
        return (
            self.env["fix.ml.model.version"]
            .sudo()
            .search(
                [("model_id", "=", self.id), ("state", "=", "deployed")],
                order="deployed_at desc, id desc",
                limit=1,
            )
        )

    def write(self, vals):
        # A11 audit M26-A02 (model change control): the weights govern every
        # score this engine produces, so a weights edit is a MODEL CHANGE —
        # it must leave a revision row behind (old vector, new vector, who,
        # when), the same way a version registration does. The revision is
        # written by the engine (sudo): it is an audit trail, not a form.
        if "weights_json" in vals:
            for rec in self:
                new_json = (vals.get("weights_json") or "").strip()
                old_json = (rec.weights_json or "").strip()
                if new_json != old_json:
                    self.env["fix.ml.weights.revision"].sudo().create(
                        {
                            "model_id": rec.id,
                            "company_id": rec.company_id.id,
                            "previous_json": rec.weights_json or False,
                            "new_json": vals.get("weights_json") or False,
                            "changed_by": self.env.user.id,
                        }
                    )
        return super().write(vals)

    @api.depends("version_ids.state", "version_ids.deployed_at")
    def _compute_serving_version(self):
        for rec in self:
            rec.serving_version_id = rec._serving_version()

    run_ids = fields.One2many("fix.ml.inference.run", "model_id", string="Inference Runs")
    run_count = fields.Integer(compute="_compute_run_stats")
    last_run_at = fields.Datetime(compute="_compute_run_stats")

    @api.depends("run_ids")
    def _compute_run_stats(self):
        # E6: the counts follow the CALLER — no sudo, company-scoped. A user
        # sees the runs their companies allow them to see, nothing more.
        for rec in self:
            runs = self.env["fix.ml.inference.run"].search(
                [("model_id", "=", rec.id), ("company_id", "in", self.env.companies.ids)],
                order="ran_at desc",
                limit=1000,
            )
            rec.run_count = len(runs)
            rec.last_run_at = runs[:1].ran_at


class FixMlInferenceRun(models.Model):
    """M26: one measured inference run. action_execute dispatches to the real
    engine named by the model's kind and stores its actual output.

    G7/R01: the run is the decision log. It is born DRAFT; state, output,
    latency, error and the engine's suggestion are written ONLY by the engine;
    a human may add their final decision and a reason. `suggested_value` is
    derived by the engine from the output; `overridden` is derived from the
    two — neither is typeable."""

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
    suggested_value = fields.Char(
        string="Engine Suggestion",
        readonly=True,
        help="Written by the engine from the run's output when the output "
        "carries a decidable scalar (score/probability). Not typeable.",
    )
    final_value = fields.Char(string="Final Human Decision")
    overridden = fields.Boolean(
        compute="_compute_overridden",
        store=True,
        help="Derived: the human decision differs from the engine suggestion. "
        "Set by comparing the two values — not by typing a flag.",
    )
    override_reason = fields.Char()

    @api.depends("final_value", "suggested_value")
    def _compute_overridden(self):
        for rec in self:
            rec.overridden = bool(
                (rec.final_value or "").strip()
                and (rec.suggested_value or "").strip()
                and (rec.final_value or "").strip() != (rec.suggested_value or "").strip()
            )

    # ---- immutability (G7/R01) ---------------------------------------------

    @api.model_create_multi
    def create(self, vals_list):
        # A run is born DRAFT: the engine's half of the decision log cannot
        # exist before the engine ran. The gateway (server code driving the
        # engine, e.g. M07's scorer) uses sudo or the gateway context.
        gateway = self.env.su or self.env.context.get("ml_inference_gateway")
        for vals in vals_list:
            if not gateway:
                injected = [f for f in _ENGINE_OWNED_CREATE_FIELDS if vals.get(f)]
                if injected:
                    raise UserError(
                        _(
                            "An inference run is created as a DRAFT and the "
                            "engine's fields are written by the engine, not by "
                            "the create form (M26): %s."
                        )
                        % ", ".join(injected)
                    )
        return super().create(vals_list)

    def _changed_keys(self, vals):
        """The keys of `vals` that would change at least one of these runs.
        Capture audit 2026-11-14: the workspace form posts every field it
        shows, so recording the human decision on a computed run sent the
        model and input back unchanged - and the guard below refused the
        whole save. An unchanged echo changes nothing and is not an edit."""
        changed = []
        for key, value in vals.items():
            field = self._fields.get(key)
            if field is None:
                changed.append(key)
                continue
            for rec in self:
                current = field.convert_to_write(rec[key], rec)
                if field.type in ("many2one", "char", "text"):
                    # an empty reference or text reads False either way
                    current = current or False
                    value = value or False
                if current != value:
                    changed.append(key)
                    break
        return changed

    def write(self, vals):
        engine = self.env.su or self.env.context.get("ml_engine_run")
        if not engine:
            echoed = set(vals) - set(self._changed_keys(vals)) - set(_HUMAN_WRITABLE_FIELDS)
            vals = {k: v for k, v in vals.items() if k not in echoed}
            off_limits = [k for k in vals if k not in _HUMAN_WRITABLE_FIELDS]
            if off_limits:
                raise UserError(
                    _(
                        "An inference run is the decision log: only the human "
                        "decision (final value, override reason) may be "
                        "recorded on it — the engine's half is not editable "
                        "(M26): %s."
                    )
                    % ", ".join(sorted(off_limits))
                )
            # BRU-AIM-05 (H, capture audit pass 2): every human override is
            # captured WITH its reason - checked before anything is written.
            for rec in self:
                final = (vals.get("final_value", rec.final_value) or "").strip()
                reason = (vals.get("override_reason", rec.override_reason) or "").strip()
                suggested = (rec.suggested_value or "").strip()
                if final and suggested and final != suggested and not reason:
                    raise UserError(
                        _(
                            "Your decision (%s) differs from the engine's "
                            "suggestion (%s): give the override reason - every "
                            "override is captured with its reason and fed back "
                            "into training (BRU-AIM-05)."
                        )
                        % (final, suggested)
                    )
        return super().write(vals)

    def unlink(self):
        # Not part of the report's ask; runs are a log, and logs outlive
        # convenience. Superuser (data hygiene) still may.
        if not self.env.su:
            raise UserError(
                _(
                    "An inference run is the decision log and cannot be deleted — mark it failed instead (M26)."
                )
            )
        return super().unlink()

    # ------------------------------------------------------------------
    # caller scope (E6/X01) — engines read inputs as the CALLER
    # ------------------------------------------------------------------

    def _caller(self):
        """The run's caller env: the real user, no superuser mode, the
        caller's companies. Every engine reads its inputs through this —
        never through sudo."""
        return self.sudo(False)

    def _caller_search(self, model_name, domain):
        """Search a target model as the caller, inside the caller's companies
        when the target carries a company (X01: cross-company rows used to be
        readable through the sudo). An access refusal becomes a run failure
        with a clean reason, not a crash."""
        caller = self._caller()
        target = caller.env[model_name]
        if "company_id" in target._fields:
            domain = [*domain, ("company_id", "in", caller.env.companies.ids)]
        try:
            return target.search(domain)
        except AccessError as exc:
            raise UserError(
                _("The caller may not read %s, so the engine has nothing to " "compute on: %s")
                % (model_name, exc)
            ) from exc

    def _caller_read(self, model_name, res_id):
        """Read one record as the caller: record rules and companies apply, so
        a caller cannot score another company's lead through the engine."""
        caller = self._caller()
        rec = caller.env[model_name].browse(int(res_id)).exists()
        if not rec:
            raise UserError(_("%s %s does not exist.") % (model_name, res_id))
        try:
            rec.check_access("read")
        except AccessError as exc:
            raise UserError(
                _(
                    "The caller may not read %s %s, so the engine refuses to "
                    "compute on it (M26/X01): %s"
                )
                % (model_name, res_id, exc)
            ) from exc
        return rec

    # ------------------------------------------------------------------
    # engines — every one is a real computation over live records
    # ------------------------------------------------------------------

    def _engine_dispatch_scoring(self):
        self.ensure_one()
        if not self.field_order_id:
            raise UserError("Dispatch scoring needs a Field Order as input.")
        order = self._caller_read("fix.field.order", self.field_order_id.id)
        return order.action_suggest_technicians(limit=5)

    def _engine_fault_classifier(self):
        self.ensure_one()
        text = (self.input_text or "").strip().lower()
        if not text:
            raise UserError("Fault classification needs input text.")
        tokens = {t for t in re.split(r"[^0-9a-zA-Zঀ-৿]+", text) if len(t) > 2}
        results = []
        codes = self._caller_search("fix.fault.code", [("active", "=", True)])
        for code in codes:
            haystack = " ".join(
                part.lower() for part in (code.code, code.name, code.description or "") if part
            )
            hay_tokens = {t for t in re.split(r"[^0-9a-zA-Zঀ-৿]+", haystack) if len(t) > 2}
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
        preds = self._caller_search("fix.predictive.maintenance", [])
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
        requests = self._caller_search("fix.tradein.request", [])
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
        logs = self._caller().env["fix.bi.sync.log"]
        freshness = logs.freshness_minutes(companies=self.env.companies.ids)
        newest = logs.search(
            [("status", "=", "success"), ("company_id", "in", self.env.companies.ids)],
            order="ran_at desc",
            limit=1,
        )
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
        carry `lead_id`. The lead is read LIVE AS THE CALLER (X01: the sudo
        browse let any caller score any company's lead) rather than trusted
        from the payload: a score computed from stale caller-supplied values
        would be unauditable.
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
        lead = self._caller_read("crm.lead", lead_id)

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
        score = max(0, min(100, round(total)))

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

    # ------------------------------------------------------------------
    # guard rails on the inference path (G7/M26-2/G03)
    # ------------------------------------------------------------------

    @api.model
    def _rail_numeric(self, value):
        if isinstance(value, bool):
            return None
        if isinstance(value, int | float):
            return float(value)
        try:
            return float(str(value).strip())
        except ValueError:
            return None

    def _rail_values(self, output, key):
        """Every number the rule's key can bind to: the scalar key of a dict
        output, or that key on each row of a list output."""
        if isinstance(output, dict):
            if key in output:
                v = self._rail_numeric(output[key])
                if v is not None:
                    yield v
        elif isinstance(output, list):
            for row in output:
                if isinstance(row, dict) and key in row:
                    v = self._rail_numeric(row[key])
                    if v is not None:
                        yield v

    def _apply_guardrails(self, output):
        """Evaluate the model's active rails against the engine output.

        Returns (output, blocked_reason, suppress_suggestion). `block` fails
        the run (blocked_reason); `flag` appends a guardrails note for human
        review; `fallback` flags AND suppresses the engine's suggestion (the
        deterministic rule governs). Every application — including rails that
        could not evaluate — is recorded in the run's output, so the log
        shows what protected the decision."""
        self.ensure_one()
        rails = (
            self.env["fix.ml.guardrail"]
            .sudo()
            .search(
                [
                    "|",
                    ("model_id", "=", False),
                    ("model_id", "=", self.model_id.id),
                    ("active", "=", True),
                ]
            )
        )
        if not rails:
            return output, None, False
        notes = []
        suggestion_suppressed = False
        for rail in rails:
            parsed = parse_guardrail_rule(rail.rule)
            if parsed is None:
                # Refused at save time; a legacy row still on disk must not
                # silently pass.
                notes.append(
                    {"rail": rail.name, "status": "not_evaluable", "reason": "rule does not parse"}
                )
                continue
            key, op, threshold = parsed
            values = list(self._rail_values(output, key))
            if not values:
                notes.append(
                    {
                        "rail": rail.name,
                        "status": "not_evaluable",
                        "reason": "key %r carries no number in this output" % key,
                    }
                )
                continue
            violated = [v for v in values if op(v, threshold)]
            if not violated:
                continue
            entry = {
                "rail": rail.name,
                "rule": rail.rule,
                "action": rail.action,
                "observed": violated[0],
                "threshold": threshold,
            }
            if rail.action == "block":
                return (
                    output,
                    "guard rail '%s' blocked the output (%s)" % (rail.name, rail.rule),
                    False,
                )
            notes.append(entry)
            if rail.action == "fallback":
                suggestion_suppressed = True
        if isinstance(output, dict):
            output = dict(output)
            output["guardrails"] = notes
        return output, None, suggestion_suppressed

    # ------------------------------------------------------------------
    # execution
    # ------------------------------------------------------------------

    def _suggestion_of(self, output):
        """The decidable scalar the engine suggests, when the output carries
        one (G7): the suggestion is DERIVED from the recorded output, never
        typed."""
        if not isinstance(output, dict):
            return False
        for key in ("score", "probability"):
            value = self._rail_numeric(output.get(key))
            if value is not None:
                as_int = round(value)
                return str(as_int if value > 1 else value)
        return False

    def action_execute(self):
        """Run the model's REAL engine and record output + measured latency.

        G7: serving is refused — outward, before any engine runs — for a
        model with no DEPLOYED version; the guard rails are evaluated on the
        output; the engine's half of the run (state, output, latency,
        suggestion) is written under the engine context only."""
        for rec in self:
            engine = self._ENGINES.get(rec.model_id.kind)
            if not engine:
                raise UserError("No engine registered for model kind %s" % rec.model_id.kind)
            serving = rec.model_id._serving_version()
            if not serving:
                raise UserError(
                    _(
                        "Model %s has no DEPLOYED version — serving is refused "
                        "until a version is promoted through the M63 request "
                        "(M26 G7). Current registry status: %s."
                    )
                    % (rec.model_id.code, rec.model_id.status)
                )
            started = time.perf_counter()
            try:
                output = engine(rec)
            except UserError as exc:
                rec.with_context(ml_engine_run=True).write(
                    {"state": "failed", "error_note": str(exc), "latency_ms": 0}
                )
                continue
            except AccessError as exc:
                rec.with_context(ml_engine_run=True).write(
                    {
                        "state": "failed",
                        "error_note": "The caller may not read the engine's " "inputs: %s" % exc,
                        "latency_ms": 0,
                    }
                )
                continue
            elapsed_ms = int((time.perf_counter() - started) * 1000)
            output, blocked, suppress = rec._apply_guardrails(output)
            if blocked:
                rec.with_context(ml_engine_run=True).write(
                    {
                        "state": "failed",
                        "error_note": blocked,
                        "latency_ms": elapsed_ms,
                        "suggested_value": False,
                    }
                )
                _logger.warning("M26 inference %s blocked: %s", rec.model_id.code, blocked)
                continue
            vals = {
                "state": "computed",
                "output_json": json.dumps(output, default=str, indent=2, ensure_ascii=False),
                "latency_ms": elapsed_ms,
                "error_note": False,
                "suggested_value": False if suppress else rec._suggestion_of(output),
            }
            rec.with_context(ml_engine_run=True).write(vals)
            _logger.info(
                "M26 inference %s computed in %dms (serving %s)",
                rec.model_id.code,
                elapsed_ms,
                serving.display_name,
            )
        return True
