# fix_ml_outcome — A07 P1 wiring (2026-11-04): the M48 intervention outcome
# reaches M26's model monitoring.
#
# M26 registers M48 predictive maintenance as m26.predictive.maintenance and
# says its inference-run log is "the ONLY ground truth the platform records":
# what the engine suggested and what the human finally found (suggested_value,
# final_value, overridden), which the override report counts. M48 records the
# outcome of every dispatched intervention (failure confirmed or not, with
# evidence: BRU-IOT-14) and published it to nobody, so the model's hit rate
# was never measured. Each recorded outcome now becomes ONE feedback row on
# the model the prediction names. Nothing is estimated: the row carries the
# prediction as it was made and the outcome as M48 recorded it.
import json

from odoo import api, fields, models
from odoo.exceptions import UserError

DEFAULT_MODEL_CODE = "m26.predictive.maintenance"


class FixMlInferenceRunIotOutcome(models.Model):
    _inherit = "fix.ml.inference.run"

    iot_action_id = fields.Many2one(
        "fix.iot.action",
        string="M48 Intervention",
        readonly=True,
        copy=False,
        index=True,
        help="The prescriptive action whose recorded outcome is this row's ground truth",
    )

    _iot_action_once = models.Constraint(
        "UNIQUE (iot_action_id)", "One outcome record per M48 intervention."
    )
    # A07 ERP audit (2026-11-20) M48-09: the outcome of a prediction no
    # intervention acted on (intervention.outcome_recorded) reached nobody.
    iot_prediction_id = fields.Many2one(
        "fix.predictive.maintenance",
        string="M48 Prediction (direct outcome)",
        readonly=True,
        copy=False,
        index=True,
    )
    _iot_prediction_once = models.Constraint(
        "UNIQUE (iot_prediction_id)", "One direct outcome record per M48 prediction."
    )

    def write(self, vals):
        for name in ("iot_action_id", "iot_prediction_id"):
            if (
                not self.env.su
                and name in vals
                and any((r[name].id or False) != (vals[name] or False) for r in self)
            ):
                raise UserError("The M48 source of an outcome record is set by M48 only.")
        return super().write(vals)

    @api.model
    def _iot_outcome_model(self, prediction):
        Model = self.env["fix.ml.model"].sudo()
        code = (prediction.model_name or "").strip() or DEFAULT_MODEL_CODE
        domain = [("code", "=", code)]
        return (
            Model.search([*domain, ("company_id", "=", prediction.company_id.id)], limit=1)
            or Model.search(domain, limit=1)
            or Model.search([("kind", "=", "predictive_maintenance")], limit=1)
        )

    @api.model
    def consume_iot_intervention_outcome(self, event):
        """iot.intervention_outcome_recorded -> one M26 feedback row: the
        prediction suggested a failure; the intervention confirmed it or not.
        `overridden` marks a prediction the field did not bear out (a false
        alarm). Idempotent per intervention."""
        action = self.env["fix.iot.action"].sudo().browse(event.get("aggregate_id")).exists()
        if not action or action.state != "done":
            return False
        if self.sudo().search_count([("iot_action_id", "=", action.id)]):
            return True
        prediction = action.prediction_id.sudo()
        model = self._iot_outcome_model(prediction)
        if not model:
            return False  # M26 has no predictive-maintenance model registered
        payload = event.get("payload") or {}
        outcome = payload.get("prediction_outcome") or prediction.outcome or "-"
        # M48-09: a failure the intervention prevented bore the prediction out.
        confirmed = (payload.get("outcome") or action.outcome) in ("confirmed", "prevented")
        made = {
            "kind": "outcome_feedback",
            "prediction": prediction.name,
            "equipment": prediction.equipment_id.code or prediction.equipment_id.name,
            "predicted": prediction.prediction,
            "confidence": prediction.confidence,
            "estimated_days_to_failure": prediction.estimated_days_to_failure,
            "predicted_on": fields.Datetime.to_string(prediction.create_date),
            "model_name": prediction.model_name or "",
        }
        found = {
            "action": action.name,
            "action_type": action.action_type,
            "outcome": payload.get("outcome") or action.outcome,
            "prediction_outcome": outcome,
            "evidence_ref": payload.get("evidence_ref") or action.outcome_evidence_ref or "",
            "completed_on": fields.Datetime.to_string(action.completed_on),
        }
        run = self.sudo().create(
            {
                "company_id": prediction.company_id.id or self.env.company.id,
                "model_id": model.id,
                "input_text": json.dumps(made, sort_keys=True, default=str),
                "state": "computed",
                "output_json": json.dumps(found, sort_keys=True, default=str, indent=2),
                "latency_ms": 0,
                "ran_at": action.completed_on or fields.Datetime.now(),
                "ran_by": action.completed_by.id or self.env.uid,
                "suggested_value": prediction.prediction,
                # A07 ERP audit (2026-11-20) M48-09: `overridden` is derived from
                # suggested vs final, so a CONFIRMED (or prevented) failure is
                # recorded as the suggestion itself; it read as overridden before.
                "final_value": prediction.prediction if confirmed else outcome,
                "override_reason": False
                if confirmed
                else ((action.outcome_note or "failure not confirmed")[:250]),
                "iot_action_id": action.id,
            }
        )
        return run

    @api.model
    def consume_iot_direct_outcome(self, event):
        """intervention.outcome_recorded (a prediction no action acted on) -> one
        M26 feedback row keyed on the prediction. "unknown" is recorded but is
        not a verdict: it counts neither way (spec AUT-IOT-16)."""
        prediction = (
            self.env["fix.predictive.maintenance"].sudo().browse(event.get("aggregate_id")).exists()
        )
        if not prediction or prediction.outcome in ("pending", False):
            return False
        if prediction.outcome_action_id:
            return True  # an intervention recorded it: that consumer wrote the row
        if self.sudo().search_count([("iot_prediction_id", "=", prediction.id)]):
            return True
        model = self._iot_outcome_model(prediction)
        if not model:
            return False
        outcome = prediction.outcome
        made = {
            "kind": "outcome_feedback",
            "prediction": prediction.name,
            "asset": prediction.asset_label or "",
            "predicted": prediction.prediction,
            "confidence": prediction.confidence,
            "estimated_days_to_failure": prediction.estimated_days_to_failure,
            "predicted_on": fields.Datetime.to_string(prediction.create_date),
            "model_name": prediction.model_name or "",
        }
        found = {
            "outcome": outcome,
            "intervention_performed": False,
            "evidence_ref": prediction.outcome_evidence_ref or "",
            "recorded_on": fields.Datetime.to_string(prediction.outcome_recorded_on),
        }
        return self.sudo().create(
            {
                "company_id": prediction.company_id.id or self.env.company.id,
                "model_id": model.id,
                "input_text": json.dumps(made, sort_keys=True, default=str),
                "state": "computed",
                "output_json": json.dumps(found, sort_keys=True, default=str, indent=2),
                "latency_ms": 0,
                "ran_at": prediction.outcome_recorded_on or fields.Datetime.now(),
                "ran_by": prediction.outcome_recorded_by.id or self.env.uid,
                "suggested_value": prediction.prediction,
                # confirmed / prevented bore the suggestion out; unknown decides
                # nothing (blank final value: neither way)
                "final_value": prediction.prediction
                if outcome in ("confirmed", "prevented")
                else (outcome if outcome == "false_alarm" else False),
                "override_reason": (prediction.outcome_note or "false alarm")[:250]
                if outcome == "false_alarm"
                else False,
                "iot_prediction_id": prediction.id,
            }
        )
