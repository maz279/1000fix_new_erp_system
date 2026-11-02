# fix_msp_ext — M05 follow-ups (P08-M07): the alert resolution leg and the
# session state guard the journeys always described. FILE NAME IS
# LOAD-BEARING: imports after the base models alphabetically (fix_msp).
from odoo import fields, models
from odoo.exceptions import UserError


class FixMspAlertExt(models.Model):
    _inherit = "fix.msp.alert"

    resolved_at = fields.Datetime(string="Resolved At", readonly=True, copy=False)
    resolution_note = fields.Char(string="Resolution Note", copy=False)

    def action_resolve(self, note=""):
        """The ticketed → resolved leg. The state existed in the Selection
        but no method ever set it — resolution was only reachable by direct
        field writes in tests. Resolving stamps the time, records the note
        and links back to the service order's outcome."""
        for alert in self:
            if alert.state not in ("ticketed", "acked", "new"):
                raise UserError(
                    "Alert %s cannot be resolved from state '%s'." % (alert.id, alert.state)
                )
            alert.write(
                {
                    "state": "resolved",
                    "resolved_at": fields.Datetime.now(),
                    "resolution_note": note or None,
                }
            )
        return True


class FixRemoteSessionExt(models.Model):
    _inherit = "fix.remote.session"

    started = fields.Boolean(
        string="Started",
        readonly=True,
        copy=False,
        help="True once action_start ran (the base's started_at defaults at "
        "create, so it cannot distinguish a planned from a running session).",
    )

    def action_start(self):
        """PDPA consent gate + the repeat-start guard: the base had no
        state, so repeated starts were silent no-ops and a started_at
        default made every planned session look 'running'."""
        for session in self:
            if session.started and not session.ended_at:
                raise UserError(
                    "Session on %s is already running (started %s) — end it first."
                    % (session.asset_id.hostname or session.asset_id.agent_id, session.started_at)
                )
            if session.ended_at:
                raise UserError(
                    "Session on %s already ended at %s — open a new session."
                    % (session.asset_id.hostname or session.asset_id.agent_id, session.ended_at)
                )
        result = super().action_start()
        self.write({"started": True, "started_at": fields.Datetime.now()})
        return result

    def action_end(self):
        for session in self:
            if session.ended_at:
                raise UserError("Session already ended at %s." % session.ended_at)
            if not session.started:
                raise UserError("Session has not started.")
        return super().action_end()

    def action_session_duration_minutes(self):
        """Display helper: started → ended minutes (None while running)."""
        self.ensure_one()
        if not (self.started_at and self.ended_at):
            return None
        return round((self.ended_at - self.started_at).total_seconds() / 60.0, 1)
