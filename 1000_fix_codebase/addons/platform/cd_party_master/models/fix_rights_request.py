# fix.rights.request — PDPA data-subject rights as tracked cases (M33,
# FR-CPM-040…044, BRU-CPM-10/11). Every request carries the statutory
# 30-day clock; fulfilment needs evidence; nothing is deleted silently.
import logging
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import ValidationError

from .fix_party_security import DPO_GROUP, require_group

_logger = logging.getLogger(__name__)

_OPEN_STATES = ("received", "verified", "in_progress")
# ir.config_parameter: how many days before the statutory due date the
# handler is reminded (the escalation fires once the date has passed).
REMINDER_DAYS_PARAM = "cd_party_master.rights_reminder_days"


class FixRightsRequest(models.Model):
    """A data-subject request: access, portability, rectification, erasure or
    withdrawal — tracked from receipt to evidenced fulfilment."""

    _name = "fix.rights.request"
    _description = "Data-Subject Rights Request"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "received_at desc, id desc"

    def _fix_guarded_fields(self) -> set:
        # The lifecycle and its evidence belong to the DPO's actions and the
        # clock cron (A03 audit M33-6/M33-7).
        return super()._fix_guarded_fields() | {
            "state",
            "identity_verified",
            "evidence_ref",
            "fulfilled_at",
            "rejected_reason",
            "reminded_at",
            "escalated_at",
        }

    partner_id = fields.Many2one(
        "res.partner",
        string="Party",
        required=True,
        index=True,
        # statutory records outlive the party record (retention overrides erasure)
        ondelete="restrict",
    )
    request_type = fields.Selection(
        [
            ("access", "Right of Access"),
            ("portability", "Right of Portability"),
            ("rectification", "Right of Rectification"),
            ("erasure", "Right of Erasure"),
            ("withdrawal", "Consent Withdrawal (all purposes)"),
        ],
        string="Request Type",
        required=True,
        tracking=True,
    )
    received_at = fields.Datetime(string="Received At", default=fields.Datetime.now, readonly=True)
    statutory_due = fields.Date(
        string="Statutory Due",
        compute="_compute_statutory_due",
        store=True,
        help="PDPA: the response is due within 30 days of receipt",
    )
    state = fields.Selection(
        [
            ("received", "Received"),
            ("verified", "Identity Verified"),
            ("in_progress", "In Progress"),
            ("fulfilled", "Fulfilled"),
            ("rejected", "Rejected"),
        ],
        string="State",
        default="received",
        required=True,
        tracking=True,
    )
    identity_verified = fields.Boolean(string="Identity Verified")
    decision = fields.Char(string="Decision Summary")
    evidence_ref = fields.Char(
        string="Evidence Reference",
        help="Export file ID / rectification notice ID — fulfilment without evidence is not fulfilment",
    )
    fulfilled_at = fields.Datetime(string="Fulfilled At", readonly=True)
    rejected_reason = fields.Char(string="Rejection Reason")
    # BRU-CPM-10: a rectification must be NOTIFIED to the data subject
    # within 30 days — record when the notification went out.
    notified_at = fields.Datetime(
        string="Party Notified At",
        help="Rectification notifications: the party is told within 30 days (BRU-CPM-10)",
    )
    handler_id = fields.Many2one(
        "res.users",
        string="Handler",
        tracking=True,
        help="Who works the request. The 30-day reminder goes to them (or to every "
        "Data Protection Officer when empty); the overdue escalation goes to the DPOs.",
    )
    reminded_at = fields.Datetime(string="Reminder Sent At", readonly=True)
    escalated_at = fields.Datetime(string="Escalated At", readonly=True)
    company_id = fields.Many2one(
        "res.company", string="Company", required=True, default=lambda self: self.env.company
    )

    @api.depends("received_at")
    def _compute_statutory_due(self):
        for req in self:
            received = req.received_at or fields.Datetime.now()
            req.statutory_due = (received + timedelta(days=30)).date()

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            from libs.py.fix_events import publish

            publish(
                self.env,
                "rights_request.received",
                "fix.rights.request",
                rec.id,
                {
                    "partner_id": rec.partner_id.id,
                    "request_type": rec.request_type,
                    "statutory_due": str(rec.statutory_due),
                },
            )
        return records

    def action_verify(self):
        require_group(self.env, DPO_GROUP, "Verifying the identity of a data subject")
        for req in self:
            # It had no state check: verifying a FULFILLED request reopened it
            # (A03 audit M33-7).
            if req.state != "received":
                raise ValidationError(
                    "Only a newly received request is identity-verified (current: %s)" % req.state
                )
            req._guarded().write({"identity_verified": True, "state": "verified"})
        return True

    def action_start(self):
        require_group(self.env, DPO_GROUP, "Starting work on a rights request")
        for req in self:
            if req.state != "verified":
                raise ValidationError("Only a verified request can move to In Progress")
            req._guarded().write({"state": "in_progress"})
        return True

    def action_fulfil(self, evidence=None):
        """Fulfil with evidence — an unevidenced fulfilment is not a
        fulfilment (AC-09)."""
        require_group(self.env, DPO_GROUP, "Fulfilling a rights request")
        for req in self:
            if req.state not in ("in_progress", "verified"):
                raise ValidationError(
                    "The request must be in progress before fulfilment (current: %s)" % req.state
                )
            if not evidence:
                raise ValidationError(
                    "Fulfilment needs its evidence reference — export ID, notice ID or file ref"
                )
            # BRU-CPM-10 (hard block): a rectification is notified to the
            # data subject. notified_at was a field nothing read (M33 capture
            # audit pass 2, 2026-11-19).
            if req.request_type == "rectification" and not req.notified_at:
                raise ValidationError(
                    "Record when the party was told of the correction (Party Notified At) "
                    "before closing a rectification (BRU-CPM-10)."
                )
            req._guarded().write(
                {
                    "state": "fulfilled",
                    "fulfilled_at": fields.Datetime.now(),
                    "evidence_ref": evidence,
                }
            )
            from libs.py.fix_events import publish

            publish(
                self.env,
                "rights_request.fulfilled",
                "fix.rights.request",
                req.id,
                {
                    "partner_id": req.partner_id.id,
                    "request_type": req.request_type,
                    "evidence_ref": evidence,
                },
            )
        return True

    def action_reject(self, reason=None):
        """Reject with a stated basis — an erasure may only be rejected on a
        statutory retention override, and the override must be stated to the
        party (BRU-CPM-11)."""
        for req in self:
            if req.state not in _OPEN_STATES:
                raise ValidationError("A %s request cannot be rejected" % req.state)
            if not reason:
                raise ValidationError("A rejection needs its stated basis")
        require_group(self.env, DPO_GROUP, "Rejecting a rights request")
        for req in self:
            req._guarded().write({"state": "rejected", "rejected_reason": reason})
        return True

    # ---- the 30-day statutory clock (A03 audit M33-7) ------------------------
    @api.model
    def _rights_reminder_days(self) -> int:
        icp = self.env["ir.config_parameter"].sudo()
        try:
            return max(int(icp.get_param(REMINDER_DAYS_PARAM, "7") or 7), 0)
        except ValueError:
            return 7

    def _rights_dpo_users(self):
        group = self.env.ref(DPO_GROUP, raise_if_not_found=False)
        if not group:
            return self.env["res.users"]
        return group.sudo().all_user_ids.filtered(
            lambda u: u.active and not u.share and self.company_id in u.company_ids
        )

    def _rights_notify(self, users, summary: str, note: str) -> None:
        self.ensure_one()
        for user in users:
            self.activity_schedule(
                "mail.mail_activity_data_todo",
                date_deadline=self.statutory_due,
                summary=summary,
                note=note,
                user_id=user.id,
            )
        if not users:
            _logger.warning(
                "rights request %s: %s, but nobody holds the DPO group", self.id, summary
            )
        self.message_post(body=note)

    @api.model
    def cron_rights_request_clock(self):
        """Remind as the statutory date approaches, escalate once it passes.

        statutory_due was displayed and nothing read it. Each open request
        gets one reminder (to its handler, else the DPOs) inside the reminder
        window, and one escalation (to every DPO and the handler) once
        overdue; both are stamped, so a second run does nothing new."""
        today = fields.Date.context_today(self)
        window = today + timedelta(days=self._rights_reminder_days())
        from libs.py.fix_events import publish

        Req = self.sudo()._guarded()
        reminded = escalated = 0
        for req in Req.search([("state", "in", _OPEN_STATES), ("statutory_due", "<=", window)]):
            payload = {
                "partner_id": req.partner_id.id,
                "request_type": req.request_type,
                "statutory_due": str(req.statutory_due),
            }
            if req.statutory_due < today:
                if req.escalated_at:
                    continue
                req._rights_notify(
                    req._rights_dpo_users() | req.handler_id,
                    "OVERDUE data-subject request",
                    "The statutory deadline %s has passed for this %s request. Escalated "
                    "to the Data Protection Officer." % (req.statutory_due, req.request_type),
                )
                req.write({"escalated_at": fields.Datetime.now()})
                publish(self.env, "rights_request.overdue", req._name, req.id, payload)
                escalated += 1
            elif not req.reminded_at:
                req._rights_notify(
                    req.handler_id or req._rights_dpo_users(),
                    "Data-subject request due %s" % req.statutory_due,
                    "This %s request must be fulfilled or refused by %s (30-day statutory "
                    "clock)." % (req.request_type, req.statutory_due),
                )
                req.write({"reminded_at": fields.Datetime.now()})
                publish(self.env, "rights_request.due_soon", req._name, req.id, payload)
                reminded += 1
        return {"reminded": reminded, "escalated": escalated}

    # ---- R8 consumer ----------------------------------------------------------
    @api.model
    def consume_party_merged(self, event):
        """Open requests follow the data subject to the surviving record;
        decided ones stay where they were made (they are the statutory record).
        Idempotent: a second delivery finds no open request on the victim.
        Logged, so a merge reversal moves them back (A03 audit W1)."""
        Log = self.env["fix.party.repoint.log"]
        merge = Log._event_merge(event)
        if not merge:
            return 0
        survivor, victim = merge.survivor_id, merge.victim_id
        open_reqs = self.sudo().search(
            [("partner_id", "=", victim.id), ("state", "in", _OPEN_STATES)]
        )
        open_reqs = Log.repoint(merge, open_reqs, "partner_id", victim, survivor)
        for req in open_reqs:
            req.message_post(
                body="Re-pointed from merged party %s to %s."
                % (victim.display_name, survivor.display_name)
            )
        return len(open_reqs)
