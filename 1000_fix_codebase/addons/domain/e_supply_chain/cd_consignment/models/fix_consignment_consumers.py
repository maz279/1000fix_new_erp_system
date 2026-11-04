# M03 relay consumers (A02 audit B2, P1).
#
# consignment.tamper_detected was published by the hub intake and read by
# nobody: a seal or weight mismatch put the consignment on hold and then
# waited for someone to notice the state. This consumer puts the hold in the
# logistics managers' activity queue, which is where the release happens.
from odoo import api, models
from odoo.exceptions import AccessError

from .fix_consignment import GROUP_MANAGER

TAMPER_SUMMARY = "Tamper hold: %s"


class FixConsignmentConsumers(models.Model):
    _inherit = "fix.consignment"

    def _assert_system_consumer(self):
        # consume_* is a public model method, so JSON-RPC can reach it. Only
        # the relay (superuser) may apply an event.
        if not self.env.su:
            raise AccessError("Logistics event consumers run only from the event relay.")

    def _tamper_supervisors(self):
        """The logistics managers who release a hold: those in the
        consignment's operating unit first, else the company's."""
        self.ensure_one()
        group = self.env.ref(GROUP_MANAGER, raise_if_not_found=False)
        if not group:
            return self.env["res.users"]
        users = group.sudo().all_user_ids.filtered(
            lambda u: u.active and not u.share and self.company_id in u.company_ids
        )
        ou = self.operating_unit_id
        if ou and "operating_unit_ids" in users._fields:
            users = users.filtered(lambda u: ou in u.operating_unit_ids) or users
        return users

    @api.model
    def consume_tamper_detected(self, event: dict) -> dict:
        """R8 consumer of consignment.tamper_detected: one to-do per logistics
        manager on the held consignment. Idempotent: a manager who already has
        an open tamper to-do on it gets no second one."""
        self._assert_system_consumer()
        payload = event.get("payload") or {}
        rec_id = event.get("aggregate_id") or payload.get("consignment_id")
        consignment = self.browse(int(rec_id or 0)).exists()
        if not consignment:
            return {"scheduled": 0, "reason": "no such consignment"}
        if consignment.state != "held":
            # released (or closed) before the relay ran: nothing to chase
            return {"scheduled": 0, "reason": "consignment is %s" % consignment.state}
        summary = TAMPER_SUMMARY % consignment.name
        open_todo = consignment.activity_ids.filtered(lambda a: a.summary == summary)
        scheduled = 0
        for user in consignment._tamper_supervisors():
            if open_todo.filtered(lambda a, u=user: a.user_id == u):
                continue
            consignment.activity_schedule(
                "mail.mail_activity_data_todo",
                summary=summary,
                note=payload.get("reason") or consignment.hold_reason or "",
                user_id=user.id,
            )
            scheduled += 1
        return {"scheduled": scheduled}
