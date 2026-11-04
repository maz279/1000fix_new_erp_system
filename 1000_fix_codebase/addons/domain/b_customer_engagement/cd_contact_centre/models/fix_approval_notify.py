# Approver notifications for M63 approval events (A11 audit P2).
#
# The engine publishes approval.requested / .reminder / .escalated / .decided
# and nobody told the approver: a payout or write-off waited in an inbox its
# holder did not know was due, which is how "nobody could approve it" turns
# into "nobody was told to". These consumers queue an e-mail and an SMS to
# each approver through the one exit, fix.notif.delivery.queue(), so the
# consent verdict (contract basis — deciding approvals is the approver's
# job), the BTRC curfew, the provider and the evidence row all apply. Staff
# notices are internal operational messages; the bilingual customer bodies
# of M01 do not apply, so these are English-only by design.
#
# cd_workflow_engine IS a dependency of this module, so the request is read
# directly; the routed RECORD may live anywhere, so it is read through the
# registry exactly as the M01 notifications read the service order.
import logging

from odoo import api, models
from odoo.exceptions import AccessError, ValidationError

logger = logging.getLogger(__name__)

_A11_KINDS = {
    "requested": {
        "subject": "Approval waiting: {request}",
        "body": "1000FiX: approval {request} ({record}) is waiting in your M63 "
        "inbox - tier {tier}, BDT {amount}. Open the workspace to decide it.",
    },
    "reminder": {
        "subject": "Overdue approval: {request}",
        "body": "1000FiX: approval {request} ({record}) is OVERDUE in your M63 "
        "inbox. Please decide it now.",
    },
    "escalated": {
        "subject": "Escalated approval: {request}",
        "body": "1000FiX: approval {request} ({record}) was escalated to you "
        "(level {level}). It is in your M63 inbox.",
    },
    "decided": {
        "subject": "Approval {state}: {request}",
        "body": "1000FiX: your approval request {request} ({record}) was " "{state} by {decider}.",
    },
}


class FixNotifDeliveryApprovals(models.Model):
    _inherit = "fix.notif.delivery"

    @api.model
    def _a11_assert_relay(self):
        if not self.env.su:
            raise AccessError("Notification event consumers run only from the event relay.")

    @api.model
    def _a11_request(self, event):
        """The fix.approval.request an approval.* event is about, if any."""
        name = (event.get("payload") or {}).get("request")
        if not name:
            return self.env["fix.approval.request"]
        return self.env["fix.approval.request"].sudo().search([("name", "=", name)], limit=1)

    @api.model
    def _a11_record_name(self, request):
        """The routed record's display name, or '' when it is gone."""
        if not request or not request.res_model:
            return ""
        Model = self.env.get(request.res_model)
        if Model is None:
            return ""
        record = Model.sudo().browse(request.res_id).exists()
        return record.display_name if record else ""

    @api.model
    def _a11_values(self, event, kind):
        payload = event.get("payload") or {}
        request = self._a11_request(event)
        state = payload.get("state") or ""
        decider = ""
        if payload.get("decided_by"):
            decider = self.env["res.users"].sudo().browse(int(payload["decided_by"])).name
        return {
            "request": payload.get("request") or request.name or "the request",
            "record": self._a11_record_name(request) or "record",
            "tier": (request.tier or "").replace("tier_", "T") or "-",
            "amount": "%.2f" % (request.amount or 0.0),
            "level": payload.get("level") or 1,
            "state": state,
            "decider": decider or "the workflow",
        }

    @api.model
    def _a11_notify_users(self, event, kind, users):
        """Queue e-mail and SMS to each user once (dedup per event+user+channel).

        A user with no address on file is skipped for that channel, not
        dead-lettered: the event was delivered, the person just cannot be
        reached on a channel they have no address for.
        """
        request = self._a11_request(event)
        text = _A11_KINDS[kind]
        values = self._a11_values(event, kind)
        queued, skipped = 0, []
        for user in users:
            partner = user.partner_id
            if not partner:
                skipped.append("%s: no partner" % user.name)
                continue
            for channel in ("email", "sms"):
                try:
                    delivery = self.queue(
                        channel=channel,
                        purpose="service_updates",
                        partner=partner,
                        body=text["body"].format(**values),
                        subject=text["subject"].format(**values) if channel == "email" else None,
                        lawful_basis="contract",
                        source_model="fix.approval.request",
                        source_id=request.id or None,
                        source_event_id=event.get("event_id"),
                        dedup_key="a11-approval:%s:%s:%s:%s"
                        % (kind, event.get("event_id") or 0, user.id, channel),
                        company=request.company_id or None,
                    )
                except ValidationError as exc:
                    skipped.append("%s/%s: %s" % (user.name, channel, exc))
                    continue
                if delivery.state != "suppressed":
                    queued += 1
        return {"queued": queued, "skipped": skipped}

    # ---- consumers ----------------------------------------------------------

    @api.model
    def consume_approval_requested(self, event: dict) -> dict:
        """E-mail and SMS every approver the request was routed to."""
        self._a11_assert_relay()
        payload = event.get("payload") or {}
        users = (
            self.env["res.users"].sudo().browse([int(u) for u in payload.get("approver_ids") or []])
        )
        users = users.exists()
        if not users:
            return {"queued": 0, "reason": "no approvers in the event"}
        return self._a11_notify_users(event, "requested", users)

    @api.model
    def consume_approval_reminder(self, event: dict) -> dict:
        """Remind the users whose inbox task is still open."""
        self._a11_assert_relay()
        request = self._a11_request(event)
        if not request:
            return {"queued": 0, "reason": "request not found"}
        users = request.task_ids.filtered(lambda t: t.state == "pending").mapped("assigned_user_id")
        if not users:
            return {"queued": 0, "reason": "no pending tasks"}
        return self._a11_notify_users(event, "reminder", users)

    @api.model
    def consume_approval_escalated(self, event: dict) -> dict:
        """Tell the escalation targets the request is now theirs."""
        self._a11_assert_relay()
        payload = event.get("payload") or {}
        users = self.env["res.users"].sudo().browse([int(u) for u in payload.get("to") or []])
        users = users.exists()
        if not users:
            return {"queued": 0, "reason": "no escalation targets in the event"}
        return self._a11_notify_users(event, "escalated", users)

    @api.model
    def consume_approval_decided(self, event: dict) -> dict:
        """Close the loop with the person who asked."""
        self._a11_assert_relay()
        request = self._a11_request(event)
        if not request:
            return {"queued": 0, "reason": "request not found"}
        if not request.requested_by_id:
            return {"queued": 0, "reason": "no requester to notify"}
        return self._a11_notify_users(event, "decided", request.requested_by_id)
