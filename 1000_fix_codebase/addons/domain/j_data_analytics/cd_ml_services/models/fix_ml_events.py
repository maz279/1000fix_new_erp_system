# fix_ml_events — the M26 lifecycle events and their in-Odoo consumers.
#
# A2-F09: the module published one event (`telemetry.model_suspended`, consumed
# by the M48 routing in cd_asset_workorder_spine) and nothing else, so a
# promotion, a retirement, a failed gate, a completed bias test or a drift
# alert stopped at the register — M60 GRC and the model's owner learned
# nothing. The spec's lifecycle (§12.3) names these as domain events.
#
# Every event published here has a consumer registered as data
# (fix.event.consumer, in data/fix_ml_event_consumers.xml): the fitness gate
# FF-48 (tooling/fitness/check_deployment_wiring.py) refuses a published event
# with no consumer — an event nobody acts on is code that never runs in
# production. There is no external subscriber yet (M60 may consume later); the
# in-module consumer's effect is the audit trail a person can act on:
#
#   model.promoted            -> chatter post on the model (who deployed what)
#   model.retired             -> chatter post on the model (with the consumers'
#                                confirmation)
#   model.bias_test_completed -> chatter post on the model (the fairness result)
#   model.gate_failed         -> to-do activity for the model's owner, due
#                                today (no owner: chatter only — owner_id is
#                                NULL on the live estate)
#   model.drift_alert         -> the same to-do activity, for a drift
#                                observation in the alert band
#
# Idempotency: the consumer posts its chatter message with the event's
# event_id in the body; a redelivered event (relay retry, Backfill) finds its
# message and stops before creating a second activity. The relay already
# delivers once per (subscription, event) — this is the defence in depth the
# estate's consumer contract (DI-05) asks for.
import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)

# The idempotency anchor a consumer looks for before acting on an event.
EVENT_MARKER = "[event %s]"

# What each event means on the model's record. The format argument is the
# event payload; every payload carries model, version, actor and reason.
EVENT_TITLES = {
    "model.promoted": "Model promoted: %(model)s %(version)s deployed by %(actor)s",
    "model.retired": "Model retired: %(model)s %(version)s retired by %(actor)s",
    "model.bias_test_completed": "Bias test completed: %(model)s %(version)s — %(assessment)s",
    "model.gate_failed": "Evaluation gate FAILED: %(model)s %(version)s — %(gate)s",
    "model.drift_alert": "Drift alert: %(model)s %(version)s — %(feature)s PSI %(psi)s",
}

# The two events that demand a person's attention (an activity when the model
# names an owner); the rest are the audit trail.
ATTENTION_EVENTS = {"model.gate_failed", "model.drift_alert"}


class FixMlModelEvents(models.Model):
    """The in-Odoo consumer of M26's lifecycle events, and the chatter helpers
    the publisher side and the consumer share."""

    _inherit = "fix.ml.model"

    def _event_already_logged(self, event_id):
        """True when this model's chatter already carries `event_id`."""
        self.ensure_one()
        if not event_id:
            return False
        return bool(
            self.env["mail.message"]
            .sudo()
            .search_count(
                [
                    ("model", "=", "fix.ml.model"),
                    ("res_id", "=", self.id),
                    ("body", "ilike", EVENT_MARKER % event_id),
                ]
            )
        )

    def _post_event_message(self, body, event_id):
        """Post the event on the model's chatter — the durable audit trail and
        the idempotency anchor. Returns the message (or None on a redelivery)."""
        self.ensure_one()
        if self._event_already_logged(event_id):
            return None
        return self.message_post(
            body="%s %s" % (body, EVENT_MARKER % event_id),
            message_type="comment",
            subtype_xmlid="mail.mt_note",
        )

    def _raise_event_activity(self, summary, note, event_id):
        """A to-do activity for the model's owner, due today. Only when the
        model names an owner: without one the chatter post is the alert (a
        to-do assigned to nobody is noise, not a control)."""
        self.ensure_one()
        if not self.owner_id:
            return False
        activity_type = self.env.ref("mail.mail_activity_data_todo", raise_if_not_found=False)
        if not activity_type:
            return False
        # Odoo 19: mail.activity.res_model is related to res_model_id.model
        # (readonly), so the ir.model id is what the create supplies.
        model_id = self.env["ir.model"]._get_id("fix.ml.model")
        if not model_id:
            return False
        return (
            self.env["mail.activity"]
            .sudo()
            .create(
                {
                    "res_model_id": model_id,
                    "res_id": self.id,
                    "activity_type_id": activity_type.id,
                    "summary": summary[:250],
                    "note": "%s %s" % (note, EVENT_MARKER % event_id),
                    "user_id": self.owner_id.id,
                    "date_deadline": fields.Date.context_today(self),
                }
            )
        )

    @api.model
    def consume_model_event(self, event):
        """The relay hands every M26 lifecycle event here (one subscription per
        event type, all pointing at this method). Idempotent per event_id; the
        effect is a chatter post, plus a to-do for the owner on an alert."""
        event_type = (event or {}).get("event_type") or ""
        if event_type not in EVENT_TITLES:
            _logger.warning("M26 consumer received an unsubscribed event: %s", event_type)
            return True
        event_id = event.get("event_id") or ""
        model = self.env["fix.ml.model"].sudo().browse(int(event.get("aggregate_id") or 0)).exists()
        if not model:
            return True  # the model is gone; its events concern nobody
        if model._event_already_logged(event_id):
            return True
        payload = dict(event.get("payload") or {})
        payload.setdefault("model", model.code)
        payload.setdefault("version", "")
        payload.setdefault("actor", "system")
        payload.setdefault("reason", "")
        payload.setdefault("assessment", "")
        payload.setdefault("gate", "")
        payload.setdefault("feature", "")
        payload.setdefault("psi", "")
        try:
            summary = EVENT_TITLES[event_type] % payload
        except (KeyError, TypeError, ValueError):
            summary = "%s: %s" % (event_type, model.code)
        body = summary
        if payload.get("reason"):
            body = "%s<br/>%s" % (body, payload["reason"])
        model._post_event_message(body, event_id)
        if event_type in ATTENTION_EVENTS:
            model._raise_event_activity(summary, body, event_id)
        return True
