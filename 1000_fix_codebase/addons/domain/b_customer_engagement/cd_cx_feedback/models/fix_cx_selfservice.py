# M34 CX self-service records: detractor follow-ups, survey distribution
# throttling and review capture. All three are real records the closed-loop
# and VoC reports read; nothing is fabricated.
from odoo import api, fields, models
from odoo.exceptions import UserError

# The default per-customer monthly CX contact cap, matching the
# max_per_month field default. One post-service survey a month is the
# declared policy; a steward raises it per party where the relationship
# warrants it.
DEFAULT_SURVEY_CAP_PER_MONTH = 1


class FixCxFollowup(models.Model):
    """Closed-loop recovery task for a detractor (NPS ≤ 6 or low rating)."""

    _name = "fix.cx.followup"
    _description = "Detractor Follow-up"
    _order = "due_date, id"

    name = fields.Char(compute="_compute_name", store=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    survey_id = fields.Many2one("fix.survey", required=True, ondelete="cascade", index=True)
    customer_id = fields.Many2one(related="survey_id.customer_id", store=True)
    reason = fields.Selection(
        [
            ("detractor_nps", "Detractor (NPS ≤ 6)"),
            ("low_rating", "Low rating (≤ 3)"),
            ("complaint_linked", "Linked complaint"),
            ("callback", "Requested callback"),
        ],
        required=True,
        default="detractor_nps",
    )
    owner_id = fields.Many2one("res.users", string="Recovery Owner")
    due_date = fields.Date(required=True)
    state = fields.Selection(
        [
            ("open", "Open"),
            ("contacted", "Customer Contacted"),
            ("recovered", "Recovered"),
            ("closed", "Closed — no recovery"),
        ],
        required=True,
        default="open",
    )
    notes = fields.Text()
    closed_at = fields.Datetime(readonly=True)
    contacted_at = fields.Datetime(readonly=True, string="First Contact At")
    customer_confirmed_at = fields.Datetime(
        readonly=True,
        string="Customer Confirmed At",
        help="BRU-CXM-04: when the customer acknowledged the recovery.",
    )
    customer_confirmation = fields.Text(
        readonly=True,
        string="Customer's Confirmation",
        help="What the customer said when confirming they are satisfied.",
    )

    def _compute_name(self):
        for rec in self:
            rec.name = "Follow-up · %s" % (rec.survey_id.service_order_id.name or rec.survey_id.id)

    # M34 capture audit, second pass (14 Nov 2026): "Mark Recovered" closed a
    # loop with no word from the customer, and "Close (Not Recovered)" closed
    # one nobody had contacted. BRU-CXM-03 (a loop case cannot be dismissed
    # without contact) and BRU-CXM-04 (it closes only on confirmed customer
    # acknowledgement, never on internal action alone) are hard blocks.
    def _require_contacted(self, act):
        for rec in self:
            if rec.state in ("recovered", "closed"):
                raise UserError("This follow-up is already closed.")
            if rec.state != "contacted":
                raise UserError(
                    "%s needs a recorded contact with the customer first (Record Contact): "
                    "a detractor follow-up cannot be closed without contact." % act
                )

    def action_close_recovered(self, confirmation=None):
        """FR-CXM-024: close on the customer's own acknowledgement."""
        confirmation = (confirmation or "").strip()
        if not confirmation:
            raise UserError(
                "Write what the customer said to confirm they are satisfied: a loop "
                "closes on the customer's acknowledgement, not on internal action."
            )
        self._require_contacted("Mark Recovered")
        now = fields.Datetime.now()
        for rec in self:
            rec.write(
                {
                    "state": "recovered",
                    "closed_at": now,
                    "customer_confirmed_at": now,
                    "customer_confirmation": confirmation,
                    "notes": rec._note_line("Recovered, customer confirmed", confirmation),
                }
            )
        return True

    # M34 capture audit (2026-11-13): 'contacted' and 'closed' had no
    # transition, so the workspace offered the state as a typed field.
    def _note_line(self, label, text):
        self.ensure_one()
        stamp = fields.Datetime.to_string(fields.Datetime.now())
        line = "[%s] %s by %s: %s" % (stamp, label, self.env.user.name, text)
        return "%s\n%s" % (self.notes, line) if self.notes else line

    def action_mark_contacted(self, note=None):
        """FR-CXM-022: first contact with the detractor is a recorded fact."""
        note = (note or "").strip()
        if not note:
            raise UserError("Say what was discussed with the customer.")
        for rec in self:
            if rec.state != "open":
                raise UserError("Only an open follow-up can record a first contact.")
            rec.write(
                {
                    "state": "contacted",
                    "contacted_at": fields.Datetime.now(),
                    "notes": rec._note_line("Contacted", note),
                }
            )
        return True

    def action_close_unrecovered(self, reason=None):
        """Close a follow-up the customer could not be won back on, with why."""
        reason = (reason or "").strip()
        if not reason:
            raise UserError("Say why the customer could not be recovered.")
        self._require_contacted("Close (Not Recovered)")
        for rec in self:
            rec.write(
                {
                    "state": "closed",
                    "closed_at": fields.Datetime.now(),
                    "notes": rec._note_line("Closed, not recovered", reason),
                }
            )
        return True


class FixCxThrottle(models.Model):
    """Per-customer survey distribution cap (frequency throttling)."""

    _name = "fix.cx.throttle"
    _description = "Survey Distribution Throttle"
    _order = "partner_id"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    partner_id = fields.Many2one("res.partner", required=True, index=True, ondelete="cascade")
    channel = fields.Selection(
        [("email", "E-mail"), ("sms", "SMS"), ("whatsapp", "WhatsApp")],
        required=True,
        default="sms",
    )
    max_per_month = fields.Integer(required=True, default=1)
    sent_this_month = fields.Integer(readonly=True, default=0)
    last_sent_at = fields.Datetime(readonly=True)
    suppressed = fields.Boolean(help="Suppress all CX outreach to this customer.")
    reason = fields.Char()

    _unique_partner_channel = models.Constraint(
        "UNIQUE (partner_id, channel)", "One throttle rule per customer and channel."
    )

    # ------------------------------------------------------------------
    # Enforcement (A03 gap-plan W2; the 2 Nov audit found this table
    # declared and populated but never consulted -- the dispatch path did
    # not read it, so the cap was decorative).
    # ------------------------------------------------------------------
    def _reset_if_new_period(self):
        """Roll the monthly counter when the calendar month has turned.

        The counter is reset lazily, on read, rather than by a cron: a cron
        that fails to run would silently suppress a month of outreach, and
        the lazy form cannot drift.
        """
        now = fields.Datetime.now()
        for rec in self:
            last = rec.last_sent_at
            if last and (last.year, last.month) != (now.year, now.month):
                rec.sudo().write({"sent_this_month": 0})

    @api.model
    def evaluate(self, partner, channel="sms"):
        """May we send CX outreach to this party on this channel now?

        Returns {allowed, reason, rule_id, sent_this_month, max_per_month}.
        No rule on file means nothing has been sent to this party this month,
        so the answer is yes -- the row is created by register_send() when the
        first message actually goes out.
        """
        partner_id = getattr(partner, "id", partner) or False
        if not partner_id:
            return {
                "allowed": True,
                "reason": "No identified party, so no per-customer cap applies.",
                "rule_id": False,
                "sent_this_month": 0,
                "max_per_month": 0,
            }
        rule = self.sudo().search(
            [("partner_id", "=", partner_id), ("channel", "=", channel)], limit=1
        )
        if not rule:
            return {
                "allowed": True,
                "reason": "No throttle counter yet for this party on %s." % channel,
                "rule_id": False,
                "sent_this_month": 0,
                "max_per_month": DEFAULT_SURVEY_CAP_PER_MONTH,
            }
        rule._reset_if_new_period()
        if rule.suppressed:
            return {
                "allowed": False,
                "reason": "All CX outreach to this party is suppressed%s."
                % ((": " + rule.reason) if rule.reason else ""),
                "rule_id": rule.id,
                "sent_this_month": rule.sent_this_month,
                "max_per_month": rule.max_per_month,
            }
        if rule.max_per_month and rule.sent_this_month >= rule.max_per_month:
            return {
                "allowed": False,
                "reason": "Monthly CX contact cap reached for this party on %s: "
                "%d of %d already sent this month."
                % (channel, rule.sent_this_month, rule.max_per_month),
                "rule_id": rule.id,
                "sent_this_month": rule.sent_this_month,
                "max_per_month": rule.max_per_month,
            }
        return {
            "allowed": True,
            "reason": "Within the monthly cap (%d of %d used)."
            % (rule.sent_this_month, rule.max_per_month),
            "rule_id": rule.id,
            "sent_this_month": rule.sent_this_month,
            "max_per_month": rule.max_per_month,
        }

    @api.model
    def register_send(self, partner, channel="sms", company=None):
        """Count a message that actually went out, creating the counter row
        on first use. Called only AFTER a send is accepted, so the counter
        never charges a party for a message they were not sent."""
        partner_id = getattr(partner, "id", partner) or False
        if not partner_id:
            return False
        rule = self.sudo().search(
            [("partner_id", "=", partner_id), ("channel", "=", channel)], limit=1
        )
        if not rule:
            rule = self.sudo().create(
                {
                    "partner_id": partner_id,
                    "channel": channel,
                    "max_per_month": DEFAULT_SURVEY_CAP_PER_MONTH,
                    "company_id": getattr(company, "id", company) or self.env.company.id,
                }
            )
        else:
            rule._reset_if_new_period()
        rule.sudo().write(
            {
                "sent_this_month": rule.sent_this_month + 1,
                "last_sent_at": fields.Datetime.now(),
            }
        )
        return rule


class FixCxReview(models.Model):
    """An external review / testimonial captured for VoC and marketing."""

    _name = "fix.cx.review"
    _description = "Customer Review"
    _order = "reviewed_at desc, id desc"

    name = fields.Char(required=True, help="Short headline.")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    source = fields.Selection(
        [
            ("google", "Google"),
            ("facebook", "Facebook"),
            ("website", "Website"),
            ("other", "Other"),
        ],
        required=True,
        default="google",
    )
    customer_id = fields.Many2one("res.partner", string="Customer")
    service_order_id = fields.Many2one("fix.service.order", string="Service Order")
    rating = fields.Integer(required=True, default=5, help="1–5 stars.")
    text = fields.Text()
    state = fields.Selection(
        [("new", "New"), ("published", "Published"), ("flagged", "Flagged for review")],
        required=True,
        default="new",
    )
    reviewed_at = fields.Date(default=fields.Date.context_today, required=True)

    # M34 capture audit, second pass (14 Nov 2026): the review form let anyone
    # type "Published", and nothing recorded the customer's consent.
    # BRU-CXM-13 (hard block): a review is published only with the customer's
    # explicit consent. FR-CXM-040 also asks for moderation and a reply.
    publication_consent = fields.Boolean(
        readonly=True, string="Customer Consented to Publication", copy=False
    )
    consent_evidence = fields.Text(
        readonly=True,
        copy=False,
        help="How and when the customer agreed (call, SMS reply, signed form).",
    )
    consent_recorded_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    consent_recorded_at = fields.Datetime(readonly=True, copy=False)
    moderated_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    moderated_at = fields.Datetime(readonly=True, copy=False)
    moderation_note = fields.Text(readonly=True, copy=False)
    reply_text = fields.Text(readonly=True, copy=False, string="Our Reply")
    replied_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    replied_at = fields.Datetime(readonly=True, copy=False)

    @api.constrains("state", "publication_consent", "consent_evidence")
    def _check_consent(self):
        for rec in self:
            if rec.state == "published" and not rec.publication_consent:
                raise UserError(
                    "Review '%s' cannot be published: the customer has not consented "
                    "(Record Consent first)." % rec.name
                )
            if rec.publication_consent and not (rec.consent_evidence or "").strip():
                raise UserError("Consent to publish needs a record of how the customer agreed.")

    @api.constrains("rating")
    def _check_rating(self):
        for rec in self:
            if not 1 <= (rec.rating or 0) <= 5:
                raise UserError("A review rating is 1 to 5 stars.")

    def action_record_consent(self, evidence=None):
        evidence = (evidence or "").strip()
        if not evidence:
            raise UserError("Say how the customer agreed to publication (call, SMS reply, form).")
        self.write(
            {
                "publication_consent": True,
                "consent_evidence": evidence,
                "consent_recorded_by_id": self.env.uid,
                "consent_recorded_at": fields.Datetime.now(),
            }
        )
        return True

    def action_publish(self):
        for rec in self:
            if not rec.publication_consent:
                raise UserError(
                    "Review '%s' has no recorded customer consent: Record Consent first." % rec.name
                )
            if rec.state == "published":
                continue
            rec.write(
                {
                    "state": "published",
                    "moderated_by_id": self.env.uid,
                    "moderated_at": fields.Datetime.now(),
                }
            )
        return True

    def action_flag(self, reason=None):
        reason = (reason or "").strip()
        if not reason:
            raise UserError("Say why the review is held back (abusive, fake, names staff...).")
        self.write(
            {
                "state": "flagged",
                "moderated_by_id": self.env.uid,
                "moderated_at": fields.Datetime.now(),
                "moderation_note": reason,
            }
        )
        return True

    def action_withdraw_consent(self, reason=None):
        """The customer withdrew consent: the review comes off the website."""
        reason = (reason or "").strip()
        if not reason:
            raise UserError("Record what the customer asked for.")
        for rec in self:
            rec.write(
                {
                    "state": "new" if rec.state == "published" else rec.state,
                    "publication_consent": False,
                    "consent_evidence": "%s\n[withdrawn %s by %s] %s"
                    % (
                        rec.consent_evidence or "",
                        fields.Datetime.to_string(fields.Datetime.now()),
                        self.env.user.name,
                        reason,
                    ),
                }
            )
        return True

    def action_reply(self, reply=None):
        reply = (reply or "").strip()
        if not reply:
            raise UserError("Write the reply.")
        self.write(
            {
                "reply_text": reply,
                "replied_by_id": self.env.uid,
                "replied_at": fields.Datetime.now(),
            }
        )
        return True
