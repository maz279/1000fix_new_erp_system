# M34 — the ISO 10002:2018 cl. 7 complaint lifecycle as guarded transitions.
#
# A03 workflow audit (2026-11-03, report §4.6, findings M34-1..M34-7): eight
# states were declared and two had methods, so nothing entered most of them
# except a raw state write; nobody owned a complaint; the 72-hour escalation
# notified nobody; SLA clocks never stopped; "five_why_verified" gated nothing;
# and nothing reopened a complaint. The lifecycle is now:
#
#   new (received, acknowledged at create)
#     -> assessed       action_assess        owner + severity confirmed
#     -> investigating  action_investigate
#     -> ncr_raised     action_raise_ncr     (M23 links the real NCR)
#     -> root_cause     action_record_root_cause
#     -> capa_open      action_open_capa
#     -> verification   action_request_verification
#     -> responded      action_respond       concession must be approved (M63)
#     -> accepted       action_customer_accept   | action_customer_reject
#     -> closed         action_close         money document + survey      -> investigating
#     -> (reopen)       action_reopen        within the reopen window
#   new/assessed/investigating -> rejected   action_decline (not upheld)
#
# Every field a transition owns is guarded (fix.guarded.mixin): it changes only
# inside these methods.
import re
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish  # FF-28

KPIS = ("first_response", "resolution")
OPEN_STATES = (
    "new",
    "assessed",
    "investigating",
    "ncr_raised",
    "root_cause",
    "capa_open",
    "verification",
    "responded",
    "accepted",
)
INVESTIGATION_STATES = ("investigating", "ncr_raised", "root_cause", "capa_open", "verification")
FINISHED_STATES = ("closed", "rejected")
SEVERITIES = ("minor", "major", "critical")
SEVERITY_RANK = {s: i for i, s in enumerate(SEVERITIES)}

# Switches (ir.config_parameter). Each default is the safe reading; see the
# module runbook and the A03 P2 report for the business rulings they await.
PARAM_ESCALATION_USER = "cd_cx_feedback.escalation_user"
PARAM_REOPEN_WINDOW_DAYS = "cd_cx_feedback.reopen_window_days"
PARAM_CLOSE_WITHOUT_REPLY_DAYS = "cd_cx_feedback.close_without_reply_days"
PARAM_RCA_VERIFIER_GROUP = "cd_cx_feedback.rca_verifier_group"
DEFAULT_REOPEN_WINDOW_DAYS = 30


class FixComplaintSlaRule(models.Model):
    """Which SLA policy a complaint of a given severity buys, in which scope.

    fix.sla.policy is estate-wide master data with no branch or operating
    unit (its own docstring), so scoping a complaint promise by branch has to
    live on M34's side of the join. A rule with neither branch nor unit is
    the estate default for that severity (A03 audit M34-5)."""

    _name = "fix.complaint.sla.rule"
    _description = "Complaint SLA Binding"
    _order = "sequence, id"

    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    severity = fields.Selection(
        [("minor", "Minor"), ("major", "Major"), ("critical", "Critical")], required=True
    )
    branch_id = fields.Many2one(
        "fix.branch",
        string="Branch",
        index=True,
        help="Applies to complaints whose service order is at this branch.",
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit", index=True)
    policy_id = fields.Many2one("fix.sla.policy", string="SLA Policy", required=True)

    @api.model
    def _match(self, complaint):
        """The most specific active rule for the complaint, or an empty set."""
        rules = self.search(
            [
                ("severity", "=", complaint.severity),
                ("policy_id.active", "=", True),
            ]
        )
        branch = complaint.service_order_id.branch_id
        unit = complaint.operating_unit_id
        for candidate in (
            rules.filtered(lambda r: r.branch_id and r.branch_id == branch),
            rules.filtered(lambda r: not r.branch_id and r.operating_unit_id == unit and unit),
            rules.filtered(lambda r: not r.branch_id and not r.operating_unit_id),
        ):
            if candidate:
                return candidate[:1]
        return self.browse()


class FixComplaintLifecycle(models.Model):
    _inherit = "fix.complaint"

    owner_id = fields.Many2one(
        "res.users",
        string="Complaint Owner",
        readonly=True,
        copy=False,
        index=True,
        tracking=True,
        help="Who answers for this complaint. Set by Assess, Take Ownership or "
        "Assign, never typed: an assignment notifies the new owner.",
    )
    assigned_at = fields.Datetime(readonly=True, copy=False)
    assessed_at = fields.Datetime(string="Assessed At", readonly=True, copy=False)
    assessed_by_id = fields.Many2one("res.users", string="Assessed By", readonly=True, copy=False)
    escalation_owner_id = fields.Many2one(
        "res.users",
        string="Escalation Owner",
        readonly=True,
        copy=False,
        tracking=True,
        help="REQ-34.5: who the 72-hour escalation was assigned to.",
    )
    root_cause_author_id = fields.Many2one(
        "res.users", string="5-Why Written By", readonly=True, copy=False
    )
    five_why_verified_by_id = fields.Many2one(
        "res.users", string="5-Why Verified By", readonly=True, copy=False
    )
    five_why_verified_at = fields.Datetime(string="5-Why Verified At", readonly=True, copy=False)
    customer_response = fields.Text(
        string="Response Given to the Customer",
        readonly=True,
        copy=False,
        help="ISO 10002 cl. 7.7-7.8: the decision and remedy communicated.",
    )
    responded_at = fields.Datetime(string="Responded At", readonly=True, copy=False)
    customer_decision = fields.Selection(
        [("pending", "Awaiting the Customer"), ("accepted", "Accepted"), ("rejected", "Rejected")],
        string="Customer Decision",
        readonly=True,
        copy=False,
        tracking=True,
    )
    customer_decision_at = fields.Datetime(readonly=True, copy=False)
    customer_decision_note = fields.Text(string="Customer's Words", readonly=True, copy=False)
    customer_rejection_count = fields.Integer(
        string="Responses Rejected", readonly=True, copy=False, default=0
    )
    closed_at = fields.Datetime(string="Closed At", readonly=True, copy=False)
    reopen_count = fields.Integer(string="Times Reopened", readonly=True, copy=False, default=0)
    reopened_at = fields.Datetime(readonly=True, copy=False)
    reopen_reason = fields.Text(readonly=True, copy=False)
    post_closure_delivery_id = fields.Many2one(
        "fix.notif.delivery",
        string="Post-Resolution Survey Message",
        readonly=True,
        copy=False,
        ondelete="set null",
    )
    post_closure_survey_note = fields.Text(
        string="Post-Resolution Survey Not Sent Because", readonly=True, copy=False
    )

    # ------------------------------------------------------------------
    # Guards
    # ------------------------------------------------------------------
    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "owner_id",
            "assigned_at",
            "assessed_at",
            "assessed_by_id",
            "escalation_owner_id",
            "escalated_at",
            "quality_warning",
            "acknowledged_at",
            "sla_policy_id",
            "resolution",
            "five_why_verified",
            "five_why_verified_by_id",
            "five_why_verified_at",
            "root_cause_author_id",
            "customer_response",
            "responded_at",
            "customer_decision",
            "customer_decision_at",
            "customer_decision_note",
            "customer_rejection_count",
            "closed_at",
            "reopen_count",
            "reopened_at",
            "reopen_reason",
            "post_closure_delivery_id",
            "post_closure_survey_note",
        }

    def _fix_state_locked_fields(self) -> set:
        """Fields frozen by where THIS complaint is in its lifecycle.

        Severity is the triage decision: after assessment it changes only
        through Reassess, which rebinds the SLA and records why. Otherwise a
        critical complaint could be relabelled minor to skip its CAPA."""
        if not self or len(self) != 1:
            return set()
        locked = set()
        if self.state != "new":
            locked.add("severity")
        if self.state in FINISHED_STATES:
            locked |= {
                "customer_id",
                "service_order_id",
                "category",
                "description",
                "concession_amount",
                "concession_type",
            }
        return locked

    def _fix_form_locked_fields(self) -> set:
        return super()._fix_form_locked_fields() | self._fix_state_locked_fields()

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        written = records.filtered(lambda r: r.root_cause_5why and not r.root_cause_author_id)
        written._guarded().write({"root_cause_author_id": self.env.uid})
        return records

    def write(self, vals):
        if self and not self._fix_guard_open():
            for rec in self:
                locked = rec._fix_state_locked_fields() & set(vals)
                changed = [n for n in locked if rec._fix_guard_differs(n, vals[n], rec[n])]
                if changed:
                    raise UserError(
                        "%s cannot be changed on complaint %s while it is %s. Use its "
                        "workflow action (Reassess, Reopen) instead."
                        % (
                            ", ".join(sorted(self._fields[n].string or n for n in changed)),
                            rec.name,
                            dict(self._fields["state"].selection).get(rec.state, rec.state),
                        )
                    )
        severity_before = {rec.id: rec.severity for rec in self} if "severity" in vals else {}
        result = super().write(vals)
        if "root_cause_5why" in vals:
            self._root_cause_edited()
        if severity_before:
            moved = self.filtered(
                lambda r: r.state not in FINISHED_STATES and r.severity != severity_before[r.id]
            )
            for rec in moved:
                rec._rebind_sla_clocks(
                    "severity changed from %s to %s" % (severity_before[rec.id], rec.severity)
                )
        return result

    def _root_cause_edited(self):
        """A 5-Why edited after verification is no longer the one verified."""
        for rec in self:
            vals = {"root_cause_author_id": self.env.uid}
            if rec.five_why_verified:
                vals.update(
                    {
                        "five_why_verified": False,
                        "five_why_verified_by_id": False,
                        "five_why_verified_at": False,
                    }
                )
                rec.message_post(
                    body="The 5-Why was edited after it was verified; the verification "
                    "is withdrawn and a second person must verify it again."
                )
            rec._guarded().write(vals)

    # ------------------------------------------------------------------
    # Ownership and notification (M34-6)
    # ------------------------------------------------------------------
    def _notify_user(self, user, summary, note):
        """A to-do on the complaint: the assignee's inbox and e-mail notice."""
        self.ensure_one()
        return self.activity_schedule(
            "mail.mail_activity_data_todo",
            date_deadline=fields.Date.context_today(self),
            summary=summary,
            note=note,
            user_id=user.id,
        )

    def _resolve_user(self, assignee):
        """A user from an id, a recordset or a login, refusing anything else."""
        Users = self.env["res.users"].sudo()
        if hasattr(assignee, "_name") and assignee._name == "res.users":
            user = assignee
        elif isinstance(assignee, int) or (isinstance(assignee, str) and assignee.isdigit()):
            user = Users.browse(int(assignee)).exists()
        else:
            user = Users.search([("login", "=", (assignee or "").strip())], limit=1)
        if not user or not user.active or user.share:
            raise UserError(
                "No active internal user matches %r. Give the login of the person who "
                "will own the complaint." % (assignee,)
            )
        return user

    def _set_owner(self, user, note=None):
        for rec in self:
            if rec.state in FINISHED_STATES:
                raise UserError("Complaint %s is %s; reopen it first." % (rec.name, rec.state))
            previous = rec.owner_id
            rec._guarded().write({"owner_id": user.id, "assigned_at": fields.Datetime.now()})
            if user != self.env.user:
                rec._notify_user(
                    user,
                    "Complaint assigned to you: %s" % rec.name,
                    note or "Assigned by %s." % self.env.user.name,
                )
            rec.message_post(
                body="Owner %s → %s (by %s)."
                % (previous.name or "none", user.name, self.env.user.name)
            )
            publish(
                self.env,
                "complaint.assigned",
                "fix.complaint",
                rec.id,
                {"complaint": rec.name, "owner_id": user.id, "previous_owner_id": previous.id},
            )

    def action_take_ownership(self):
        """The current user owns the complaint from now on."""
        self._set_owner(self.env.user)
        return True

    def action_assign(self, assignee=None, note=None):
        """Assign the complaint to another internal user and notify them.

        `assignee` is a user id or a login (the workspace asks for a login)."""
        user = self._resolve_user(assignee)
        self._set_owner(user, note=note)
        return True

    # ------------------------------------------------------------------
    # ISO 10002 cl. 7.4-7.5: assessment
    # ------------------------------------------------------------------
    @staticmethod
    def _parse_severity(text):
        """'major: device returned damaged' -> ('major', 'device returned damaged')."""
        raw = (text or "").strip()
        if not raw:
            return None, ""
        match = re.match(r"^\s*(minor|major|critical)\b[\s:,\-–—]*(.*)$", raw, re.I | re.S)
        if not match:
            raise UserError(
                "Start with the severity: minor, major or critical (optionally followed "
                "by the reason), not %r." % raw[:40]
            )
        return match.group(1).lower(), match.group(2).strip()

    def action_assess(self, severity=None):
        """Initial assessment: confirm the severity and who owns the complaint.

        The assessor owns it when nobody does yet. The first-response SLA
        clock measures intake to this first human action (fix.sla.policy:
        'Assignment to first action'), so it stops here."""
        new_severity, _reason = self._parse_severity(severity)
        for rec in self:
            if rec.state != "new":
                raise UserError("Only a received (new) complaint is assessed; use Reassess.")
            vals = {
                "state": "assessed",
                "assessed_at": fields.Datetime.now(),
                "assessed_by_id": self.env.uid,
            }
            if new_severity:
                vals["severity"] = new_severity
            if not rec.owner_id:
                vals.update({"owner_id": self.env.uid, "assigned_at": fields.Datetime.now()})
            rec._guarded().write(vals)
            rec._stop_sla_clocks("assessed", kpis=("first_response",))
            rec.message_post(
                body="Assessed by %s: severity %s, owner %s."
                % (self.env.user.name, rec.severity, rec.owner_id.name)
            )
            publish(
                self.env,
                "complaint.assessed",
                "fix.complaint",
                rec.id,
                {"complaint": rec.name, "severity": rec.severity, "owner_id": rec.owner_id.id},
            )
        return True

    def action_reassess(self, severity=None, reason=None):
        """Change the severity after assessment, rebinding the SLA policy.

        A downgrade needs a reason: it removes the RCA and CAPA obligations a
        major or critical complaint carries."""
        new_severity, parsed_reason = self._parse_severity(severity)
        reason = (reason or parsed_reason or "").strip()
        if not new_severity:
            raise UserError("Give the new severity: minor, major or critical.")
        for rec in self:
            if rec.state in FINISHED_STATES or rec.state == "new":
                raise UserError(
                    "Reassess applies to an open, assessed complaint (this one is %s)." % rec.state
                )
            if new_severity == rec.severity:
                continue
            if SEVERITY_RANK[new_severity] < SEVERITY_RANK[rec.severity] and not reason:
                raise UserError(
                    "Lowering complaint %s from %s to %s needs a stated reason."
                    % (rec.name, rec.severity, new_severity)
                )
            old = rec.severity
            rec._guarded().write({"severity": new_severity})
            rec.message_post(
                body="Severity %s → %s by %s%s."
                % (old, new_severity, self.env.user.name, (": %s" % reason) if reason else "")
            )
        return True

    # ------------------------------------------------------------------
    # cl. 7.6: investigation (action_investigate / action_raise_ncr live on
    # the base model; M23 extends the NCR step)
    # ------------------------------------------------------------------
    def action_record_root_cause(self):
        for rec in self:
            if rec.state not in ("investigating", "ncr_raised"):
                raise UserError("Record the root cause while the complaint is under investigation.")
            if not rec.root_cause_5why or len(rec.root_cause_5why.strip()) < 20:
                raise ValidationError(
                    "Write the 5-Why root cause analysis (at least 20 characters) first."
                )
            rec._guarded().write({"state": "root_cause"})
            rec.message_post(body="Root cause recorded by %s." % self.env.user.name)
        return True

    def action_verify_root_cause(self):
        """The 5-Why sign-off, by someone other than the person who wrote it.

        A03 audit: five_why_verified was a Boolean anyone could tick and
        nothing read. It is now set only here, and _rca_denial makes a
        major or critical complaint wait for it before the response and the
        closure. Editing the 5-Why afterwards withdraws it."""
        xmlid = (
            self.env["ir.config_parameter"].sudo().get_param(PARAM_RCA_VERIFIER_GROUP) or ""
        ).strip()
        for rec in self:
            if rec.state in FINISHED_STATES:
                raise UserError("Complaint %s is %s." % (rec.name, rec.state))
            if not rec.root_cause_5why or len(rec.root_cause_5why.strip()) < 20:
                raise ValidationError("There is no 5-Why root cause analysis to verify yet.")
            if rec.five_why_verified:
                raise UserError("The 5-Why of complaint %s is already verified." % rec.name)
            if rec.root_cause_author_id == self.env.user:
                raise UserError(
                    "Segregation of duties: you wrote this 5-Why, so a second person "
                    "verifies it."
                )
            if xmlid and not self.env.user.has_group(xmlid):
                raise UserError("Verifying a 5-Why needs the group %s." % xmlid)
            rec._guarded().write(
                {
                    "five_why_verified": True,
                    "five_why_verified_by_id": self.env.uid,
                    "five_why_verified_at": fields.Datetime.now(),
                }
            )
            rec.message_post(body="5-Why verified by %s." % self.env.user.name)
        return True

    def action_open_capa(self):
        for rec in self:
            if rec.state != "root_cause":
                raise UserError("Open the CAPA once the root cause is recorded.")
            has_capa = rec["capa_id"] if "capa_id" in rec._fields else False
            if not has_capa and not (rec.capa_stub_ref or "").strip():
                raise UserError("Link the CAPA (or enter its reference) before opening it.")
            rec._guarded().write({"state": "capa_open"})
            rec.message_post(body="CAPA opened by %s." % self.env.user.name)
        return True

    def action_request_verification(self):
        for rec in self:
            if rec.state != "capa_open":
                raise UserError("Only an open CAPA goes to verification.")
            rec._guarded().write({"state": "verification"})
            rec.message_post(body="CAPA sent for verification by %s." % self.env.user.name)
        return True

    # ------------------------------------------------------------------
    # cl. 7.7-7.8: response and the customer's decision
    # ------------------------------------------------------------------
    def action_request_approval(self, justification=None):
        """A concession is requested while the complaint is being worked,
        and only once it says what kind of remedy it is."""
        for rec in self:
            if rec.state not in ("new", "assessed", *INVESTIGATION_STATES):
                raise UserError(
                    "A concession is approved before the response goes to the customer; "
                    "complaint %s is %s." % (rec.name, rec.state)
                )
            if rec.concession_amount > 0 and rec.concession_type in (False, "none"):
                raise UserError(
                    "Choose the concession type (waiver, discount voucher or refund) "
                    "before requesting its approval."
                )
        return super().action_request_approval(justification=justification)

    def action_respond(self, response=None):
        """Communicate the decision and remedy to the customer.

        Nothing may be offered that is not authorised: a concession must be
        approved for its amount, and a major or critical complaint must have
        a verified 5-Why, before the response is sent."""
        text = (response or "").strip()
        for rec in self:
            if rec.state not in INVESTIGATION_STATES:
                raise UserError("Respond once the complaint has been investigated.")
            if not text:
                raise UserError("Write the response given to the customer.")
            if not rec.owner_id:
                raise UserError("Complaint %s has no owner." % rec.name)
            denial = rec._rca_denial()
            if denial:
                raise ValidationError(denial)
            if rec.concession_amount > 0 and rec.concession_type in (False, "none"):
                raise UserError("Choose the concession type before offering it.")
            rec._concession_denial()
            rec._guarded().write(
                {
                    "state": "responded",
                    "customer_response": text,
                    "responded_at": fields.Datetime.now(),
                    "customer_decision": "pending",
                    "customer_decision_at": False,
                    "customer_decision_note": False,
                }
            )
            publish(
                self.env,
                "complaint.responded",
                "fix.complaint",
                rec.id,
                {
                    "complaint": rec.name,
                    "partner_id": rec.customer_id.id,
                    "concession_type": rec.concession_type,
                    "concession_amount": rec.concession_amount,
                },
            )
        return True

    def action_customer_accept(self, note=None):
        """The customer accepts the response (agent-recorded or from the portal)."""
        for rec in self:
            if rec.state != "responded":
                raise UserError("Only a response awaiting the customer can be accepted.")
            rec._guarded().write(
                {
                    "state": "accepted",
                    "customer_decision": "accepted",
                    "customer_decision_at": fields.Datetime.now(),
                    "customer_decision_note": (note or "").strip() or False,
                }
            )
            rec.message_post(
                body="Customer accepted the response (recorded by %s)." % self.env.user.name
            )
        return True

    def action_customer_reject(self, reason=None):
        """The customer rejects the response; the complaint goes back to work.

        ISO 10002 cl. 7.8: a rejected response leaves the complaint open and
        is recorded. A changed concession then needs a new approval (raising
        the amount voids the old one)."""
        text = (reason or "").strip()
        for rec in self:
            if rec.state != "responded":
                raise UserError("Only a response awaiting the customer can be rejected.")
            if not text:
                raise UserError("Record why the customer rejected the response.")
            rec._guarded().write(
                {
                    "state": "investigating",
                    "customer_decision": "rejected",
                    "customer_decision_at": fields.Datetime.now(),
                    "customer_decision_note": text,
                    "customer_rejection_count": rec.customer_rejection_count + 1,
                }
            )
            rec.message_post(body="Customer rejected the response: %s" % text)
            publish(
                self.env,
                "complaint.response_rejected",
                "fix.complaint",
                rec.id,
                {"complaint": rec.name, "times": rec.customer_rejection_count},
            )
        return True

    # ------------------------------------------------------------------
    # cl. 7.9: closure, decline, reopen
    # ------------------------------------------------------------------
    def _closure_position_check(self):
        """A complaint closes once the customer has accepted the response.

        Switch cd_cx_feedback.close_without_reply_days (default 0 = off):
        when set, a response the customer has not answered for that many days
        may also close. Whether silence counts as acceptance is a business
        ruling, so the default waits for an answer."""
        self.ensure_one()
        if self.state == "accepted":
            return
        days = int(
            self.env["ir.config_parameter"].sudo().get_param(PARAM_CLOSE_WITHOUT_REPLY_DAYS) or 0
        )
        if (
            self.state == "responded"
            and days > 0
            and self.responded_at
            and self.responded_at <= fields.Datetime.now() - timedelta(days=days)
        ):
            return
        raise UserError(
            "Complaint %s is %s. It closes after the response is sent and the customer "
            "accepts it (ISO 10002 cl. 7.8-7.9)."
            % (self.name, dict(self._fields["state"].selection).get(self.state, self.state))
        )

    def action_decline(self, reason=None):
        """Decline a complaint that is not upheld (duplicate, out of scope).

        Only before a response is made: once a remedy has been offered, the
        customer's decision is what ends it."""
        text = (reason or "").strip()
        for rec in self:
            if rec.state not in ("new", "assessed", "investigating"):
                raise UserError("Only a complaint not yet answered can be declined.")
            if not text:
                raise UserError("State why the complaint is not upheld.")
            if rec.concession_approved:
                raise UserError("A complaint with an approved concession cannot be declined.")
            rec._guarded().write(
                {"state": "rejected", "resolution": text, "closed_at": fields.Datetime.now()}
            )
            rec._stop_sla_clocks("declined")
            rec.message_post(body="Declined (not upheld) by %s: %s" % (self.env.user.name, text))
            publish(
                self.env,
                "complaint.declined",
                "fix.complaint",
                rec.id,
                {"complaint": rec.name, "reason": text},
            )
        return True

    def action_reopen(self, reason=None):
        """Reopen a closed or declined complaint.

        Rules: a stated reason; within cd_cx_feedback.reopen_window_days of
        closure (default 30; after that it is a new complaint); back to
        investigation with its owner; a fresh resolution clock; and the
        post-resolution survey re-armed for the next closure (A03 audit M34-7:
        a reopened complaint used to keep its 'survey sent' stamp)."""
        text = (reason or "").strip()
        window = int(
            self.env["ir.config_parameter"].sudo().get_param(PARAM_REOPEN_WINDOW_DAYS)
            or DEFAULT_REOPEN_WINDOW_DAYS
        )
        now = fields.Datetime.now()
        for rec in self:
            if rec.state not in FINISHED_STATES:
                raise UserError("Only a closed or declined complaint can be reopened.")
            if not text:
                raise UserError("State why the complaint is reopened.")
            if rec.closed_at and rec.closed_at < now - timedelta(days=window):
                raise UserError(
                    "Complaint %s closed more than %d days ago; raise a new complaint "
                    "that refers to it instead." % (rec.name, window)
                )
            rec._guarded().write(
                {
                    "state": "investigating" if rec.owner_id else "new",
                    "reopen_count": rec.reopen_count + 1,
                    "reopened_at": now,
                    "reopen_reason": text,
                    "closed_at": False,
                    "customer_decision": False,
                    "customer_decision_at": False,
                    "customer_decision_note": False,
                    "post_closure_survey_sent_at": False,
                    "post_closure_delivery_id": False,
                    "post_closure_survey_note": False,
                }
            )
            rec._start_sla_clocks(kpis=("resolution",), started_at=now)
            if rec.owner_id and rec.owner_id != self.env.user:
                rec._notify_user(rec.owner_id, "Complaint reopened: %s" % rec.name, text)
            rec.message_post(body="Reopened by %s: %s" % (self.env.user.name, text))
            publish(
                self.env,
                "complaint.reopened",
                "fix.complaint",
                rec.id,
                {"complaint": rec.name, "reason": text, "times": rec.reopen_count},
            )
        return True

    # ------------------------------------------------------------------
    # SLA clocks (M34-5)
    # ------------------------------------------------------------------
    def _sla_engine(self):
        Instance = self.env.get("fix.sla.kpi.instance")
        return Instance.sudo() if Instance is not None else None

    def _stop_sla_clocks(self, reason, kpis=KPIS):
        """Finish the live clocks: the promise was kept by this transition.

        Without this a closed complaint's clocks ran on and the breach cron
        later marked them breached."""
        Instance = self._sla_engine()
        if Instance is None:
            return
        for rec in self:
            for kpi in kpis:
                Instance.for_record(rec, kpi).succeed()

    @staticmethod
    def _series_origin(instance):
        """When the promise a clock belongs to started (before any resume)."""
        while instance.supersedes_id:
            instance = instance.supersedes_id
        return instance.started_at

    def _rebind_sla_clocks(self, reason):
        """Move the live clocks to the policy the complaint now buys.

        As Dynamics 365 does when a case's SLA changes: the running instance
        is cancelled and a new one starts from the same origin, so a raised
        severity tightens the deadline from intake, not from the change. A
        KPI that already finished is left alone."""
        Instance = self._sla_engine()
        if Instance is None:
            return
        for rec in self:
            policy = rec._resolve_sla_policy()
            if not policy:
                rec.message_post(
                    body="Severity is now %s, for which no SLA policy is configured; the "
                    "existing clocks keep running." % rec.severity
                )
                continue
            if policy == rec.sla_policy_id:
                continue
            for kpi in KPIS:
                series = Instance.for_record(rec, kpi, live_only=False)
                live = series.filtered(lambda i: i.state in ("in_progress", "paused"))
                if series and not live:
                    continue
                if not series and kpi == "first_response" and rec.state != "new":
                    continue
                origin = (
                    rec._series_origin(live[:1]) if live else (rec.reopened_at or rec.create_date)
                )
                live.cancel("%s; rebound to SLA policy %s" % (reason, policy.code))
                Instance.start_for(
                    rec, policy, kpi, partner=rec.customer_id or None, started_at=origin
                )
            previous = rec.sla_policy_id
            rec._guarded().write({"sla_policy_id": policy.id})
            rec.message_post(
                body="SLA policy %s → %s (%s)." % (previous.code or "none", policy.code, reason)
            )

    @api.model
    def cron_backfill_sla_clocks(self):
        """Open the clocks an open complaint should have and does not.

        Idempotent: a KPI with any instance, live or finished, is skipped,
        so a second run starts nothing. The clock starts at intake (or the
        reopen), because that is when the promise began: a complaint raised
        before the S9 binding, or before a policy existed, reads as late if it
        is late. First response is not backfilled for a complaint already past
        assessment, since its moment is gone. Scheduled daily so a policy
        configured later still reaches the complaints already open."""
        Instance = self._sla_engine()
        if Instance is None:
            return {"considered": 0, "clocks_started": 0}
        complaints = self.sudo().search([("state", "not in", FINISHED_STATES)])
        started = 0
        for rec in complaints:
            missing = tuple(
                kpi
                for kpi in KPIS
                if not Instance.for_record(rec, kpi, live_only=False)
                and not (kpi == "first_response" and rec.state != "new")
            )
            if not missing:
                continue
            before = Instance.search_count([("res_model", "=", rec._name), ("res_id", "=", rec.id)])
            rec._start_sla_clocks(kpis=missing, started_at=rec.reopened_at or rec.create_date)
            started += (
                Instance.search_count([("res_model", "=", rec._name), ("res_id", "=", rec.id)])
                - before
            )
        return {"considered": len(complaints), "clocks_started": started}

    # ------------------------------------------------------------------
    # 72-hour escalation (REQ-34.5, M34-6)
    # ------------------------------------------------------------------
    def _escalation_owner(self):
        """Who a 72-hour escalation goes to: the COO-level role.

        cd_cx_feedback.escalation_user (a login or user id) names the person
        when the business has appointed one. Otherwise the DOFA Tier 4 holders
        (CFO / CCO / COO), the record's operating unit first, routed to the
        lowest competent level as the M63 engine does, first by id. Empty when
        nobody holds the role: the caller then says so."""
        self.ensure_one()
        Users = self.env["res.users"].sudo()
        ref = (
            self.env["ir.config_parameter"].sudo().get_param(PARAM_ESCALATION_USER) or ""
        ).strip()
        if ref:
            user = Users.search([("login", "=", ref)], limit=1)
            if not user and ref.isdigit():
                user = Users.browse(int(ref)).exists()
            if user and user.active and not user.share:
                return user
        group = self.env.ref("cd_entity_config.group_dofa_tier_4", raise_if_not_found=False)
        holders = self._approval_lowest_competent(self._approval_holders(group), "tier_4")
        return holders.sorted("id")[:1]

    @api.model
    def consume_escalated_72h(self, event: dict):
        """R8 consumer of complaint.escalated_72h: an M63 exception task.

        One per complaint (a complaint escalates once in its life), assigned
        to the escalation owner, or left unassigned with that said in its name
        so the M63 inbox shows the gap instead of hiding it."""
        complaint = self.browse(int(event.get("aggregate_id") or 0)).exists()
        if not complaint:
            return None
        Task = self.env["fix.workflow.task"].sudo()
        existing = Task.search(
            [
                ("res_model", "=", self._name),
                ("res_id", "=", complaint.id),
                ("task_type", "=", "exception"),
            ],
            limit=1,
        )
        if existing:
            return existing
        owner = complaint.escalation_owner_id or complaint._escalation_owner()
        name = "72h escalation: %s" % complaint.name
        if not owner:
            name += " (no escalation owner appointed)"
        # The task's assignment and state are guarded (cd_workflow_engine);
        # the relay runs as superuser and this is the transition that sets them.
        return Task._guarded().create(
            {
                "name": name,
                "company_id": complaint.company_id.id,
                "task_type": "exception",
                "res_model": self._name,
                "res_id": complaint.id,
                "assigned_user_id": owner.id or False,
                "assigned_to_id": owner.employee_ids[:1].id or False,
                "due_at": fields.Datetime.now() + timedelta(hours=24),
            }
        )

    # ------------------------------------------------------------------
    # Post-resolution survey (REQ-34.6, M34-7)
    # ------------------------------------------------------------------
    def _contact_target(self):
        """(channel, address, reason): SMS first, else e-mail, else why not."""
        self.ensure_one()
        partner = self.customer_id
        phone = (getattr(partner, "mobile", False) or partner.phone or "").strip()
        if phone:
            return "sms", phone, ""
        email = (partner.email or "").strip()
        if email:
            return "email", email, ""
        return None, None, "No phone or e-mail is on file for the customer."

    @api.model
    def consume_post_closure_survey(self, event: dict):
        """R8 consumer of complaint.post_closure_survey_dispatched: send it.

        The event was published with no consumer, so no message ever went
        out. The S1 delivery service applies consent and the BTRC window and
        keeps the row either way. The monthly survey cap (fix.cx.throttle) is
        NOT applied: this checks a complaint's resolution, which REQ-34.6
        requires, and is not outreach. Idempotent per closure cycle."""
        complaint = self.browse(int(event.get("aggregate_id") or 0)).exists()
        if not complaint or complaint.state != "closed":
            return None
        cycle = int((event.get("payload") or {}).get("cycle", complaint.reopen_count) or 0)
        if cycle != complaint.reopen_count:
            return None  # an earlier closure's event; that cycle is over
        if complaint.post_closure_delivery_id:
            return complaint.post_closure_delivery_id
        channel, address, reason = complaint._contact_target()
        if not channel:
            complaint._guarded().write({"post_closure_survey_note": reason})
            return None
        body = (
            "1000FiX Services: আপনার অভিযোগ %s নিষ্পত্তি হয়েছে। সমাধানে আপনি সন্তুষ্ট কি? "
            "১-৫ উত্তর দিন। / Your complaint %s is resolved. Are you satisfied? "
            "Reply 1-5. Hotline 16743" % (complaint.name, complaint.name)
        )
        delivery = self.env["fix.notif.delivery"].queue(
            channel=channel,
            purpose="service_updates",
            partner=complaint.customer_id,
            to_address=address,
            body=body,
            lawful_basis="contract",
            source_model=self._name,
            source_id=complaint.id,
            source_event_id=event.get("event_id") or None,
            dedup_key="complaint-closure-survey:%d:%d" % (complaint.id, cycle),
            operating_unit=complaint.operating_unit_id,
            company=complaint.company_id,
        )
        complaint._guarded().write(
            {
                "post_closure_delivery_id": delivery.id,
                "post_closure_survey_note": delivery.consent_reason
                if delivery.state == "suppressed"
                else False,
            }
        )
        return delivery
