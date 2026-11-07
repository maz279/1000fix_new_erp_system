# fix.role.assignment - who was actually GIVEN which role (A12 finish, E3/E5).
#
# The earlier resolver read "held" off group membership: a user holding one
# group that several roles share "held" every one of those roles. So a revoke
# kept the group because a role he never had "still needed" it (M29-13), and
# SoD refused him grants over a role he never had (M29-4). 26 of 50 roles on the
# shipped map share a group, so this was the normal case, not an edge case.
#
# This register records the assignment itself, written by the only paths that
# assign: an access request grant and an applied JML event. fix.sod.control
# resolves "held" from it (plus the employee master's roles and, for access
# handed out outside the register, groups that name one role unambiguously).
# It has no user write path: rows change only through those services.
from odoo import api, fields, models
from odoo.exceptions import AccessError


class FixRoleAssignment(models.Model):
    _name = "fix.role.assignment"
    _description = "Role Assignment"
    _order = "granted_on desc, id desc"
    _rec_name = "role_id"

    user_id = fields.Many2one(
        "res.users", string="User", required=True, index=True, ondelete="cascade"
    )
    role_id = fields.Many2one(
        "fix.role", string="Role", required=True, index=True, ondelete="cascade"
    )
    source = fields.Char(
        string="Assigned By", required=True, help="The record that made this assignment."
    )
    request_id = fields.Many2one(
        "fix.access.request", string="Access Request", index=True, ondelete="set null"
    )
    granted_on = fields.Datetime(required=True, default=fields.Datetime.now)
    ended_on = fields.Datetime(index=True)
    end_reason = fields.Char()
    is_live = fields.Boolean(string="Live", compute="_compute_is_live")

    _one_live_assignment = models.UniqueIndex(
        "(user_id, role_id) WHERE ended_on IS NULL",
        "A user holds a role through one live assignment at a time.",
    )

    @api.depends("ended_on")
    def _compute_is_live(self):
        for rec in self:
            rec.is_live = not rec.ended_on

    # ------------------------------------------------------------------
    # Services (private: reachable from code, not over JSON-RPC)
    # ------------------------------------------------------------------
    @api.model
    def _fix_live(self, user, role=None):
        domain = [("user_id", "in", user.ids), ("ended_on", "=", False)]
        if role:
            domain.append(("role_id", "in", role.ids))
        return self.sudo().search(domain)

    @api.model
    def _fix_record(self, user, role, source, request=None):
        """Open the assignment, or refresh the live one. A later grant with no
        end date makes a time-boxed assignment permanent; a time-boxed grant
        never shortens one that is already permanent."""
        live = self._fix_live(user, role)
        if not live:
            return self.sudo().create(
                {
                    "user_id": user.id,
                    "role_id": role.id,
                    "source": source,
                    "request_id": request.id if request else False,
                }
            )
        permanent = not (live.request_id and live.request_id.valid_until)
        if not (request and request.valid_until and permanent):
            live.sudo().write({"source": source, "request_id": request.id if request else False})
        return live

    def _fix_end(self, reason):
        """Close live assignments and the grant request that opened them, so
        the expiry clock never revokes the same grant a second time."""
        now = fields.Datetime.now()
        for rec in self.sudo():
            if rec.ended_on:
                continue
            rec.write({"ended_on": now, "end_reason": (reason or "")[:250]})
            request = rec.request_id
            if request and request.state == "granted":
                request._guarded().write({"state": "revoked"})
                request.message_post(body="Access ended: %s" % (reason or "")[:250])

    @api.model
    def _fix_backfill_from_history(self):
        """One pass over what the workflow really did before this register
        existed: granted requests, applied revokes, applied JML events and
        certification revokes, oldest first. Only a role whose groups the user
        still holds is opened; nothing is inferred from group overlap."""
        if not self.env.su:
            raise AccessError("The role-assignment backfill runs from the migration only.")
        timeline = []
        requests = self.env["fix.access.request"].search([("state", "in", ("granted", "revoked"))])
        for req in requests:
            if req.state == "revoked" and req.request_type != "revoke":
                continue  # an expired grant: its own revocation already happened
            kind = "add" if req.state == "granted" else "end"
            timeline.append(
                (req.decided_on or req.create_date, kind, req.user_id, req.role_id, req)
            )
        events = self.env["fix.jml.event"].search(
            [("state", "=", "applied"), ("event_type", "in", ("joiner", "mover"))]
        )
        for ev in events.filtered(lambda e: e.user_id and e.role_id):
            timeline.append((ev.applied_on or ev.create_date, "add", ev.user_id, ev.role_id, ev))
        for cert in self.env["fix.access.certification"].search([("decision", "=", "revoked")]):
            timeline.append(
                (cert.decided_on or cert.create_date, "end", cert.user_id, cert.role_id, cert)
            )
        opened = 0
        for _when, kind, user, role, origin in sorted(timeline, key=lambda row: row[0]):
            live = self._fix_live(user, role)
            if kind == "end":
                live._fix_end("%s (backfill)" % origin.display_name)
            elif not live and set(user.group_ids.ids) & set(role.group_ids.ids):
                self.create(
                    {
                        "user_id": user.id,
                        "role_id": role.id,
                        "source": "%s,%d" % (origin._name, origin.id),
                        "request_id": origin.id if origin._name == "fix.access.request" else False,
                    }
                )
                opened += 1
        return opened
