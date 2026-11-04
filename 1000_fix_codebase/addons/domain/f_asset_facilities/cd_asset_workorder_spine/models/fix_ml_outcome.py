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

    def write(self, vals):
        if (
            not self.env.su
            and "iot_action_id" in vals
            and any((r.iot_action_id.id or False) != (vals["iot_action_id"] or False) for r in self)
        ):
            raise UserError("The M48 intervention of an outcome record is set by M48 only.")
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
        confirmed = (payload.get("outcome") or action.outcome) == "confirmed"
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
                "final_value": outcome,
                "overridden": not confirmed,
                "override_reason": False
                if confirmed
                else ((action.outcome_note or "failure not confirmed")[:250]),
                "iot_action_id": action.id,
            }
        )
        return run
