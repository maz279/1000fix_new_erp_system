# M34 CX self-service records: detractor follow-ups, survey distribution
# throttling and review capture. All three are real records the closed-loop
# and VoC reports read; nothing is fabricated.
from odoo import api, fields, models

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

    def _compute_name(self):
        for rec in self:
            rec.name = "Follow-up · %s" % (rec.survey_id.service_order_id.name or rec.survey_id.id)

    def action_close_recovered(self):
        for rec in self:
            rec.write({"state": "recovered", "closed_at": fields.Datetime.now()})
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
