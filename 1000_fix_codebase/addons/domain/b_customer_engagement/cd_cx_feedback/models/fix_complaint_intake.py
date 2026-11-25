# M34 — complaint intake from the channels customers actually use.
#
# A03 audit M34-8: the only intake was a manual create. The M27 macro refused
# on purpose ("open the complaint form rather than guessing"), the customer
# portal had no endpoint, and a detractor survey raised a follow-up that
# nothing linked to a complaint. Three intakes now create (or link) a real
# complaint, each idempotent on its source:
#   - fix.conversation.action_create_complaint   (M27, one per conversation)
#   - fix.complaint.portal_submit_complaint       (the customer portal; the
#     authenticated route is controllers/complaint_portal.py)
#   - fix.cx.followup.action_raise_complaint      (a detractor follow-up)
from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError

PARAM_PORTAL_OU = "cd_cx_feedback.portal_operating_unit_id"

INTAKE_CHANNELS = [
    ("manual", "Entered by Staff"),
    ("contact_centre", "Contact Centre (M27)"),
    ("portal", "Customer Portal"),
    ("survey", "Detractor Survey Follow-up"),
]


class FixComplaintIntake(models.Model):
    _inherit = "fix.complaint"

    intake_channel = fields.Selection(
        INTAKE_CHANNELS, string="Received Through", default="manual", readonly=True, copy=False
    )
    intake_ref = fields.Char(
        string="Intake Reference",
        readonly=True,
        copy=False,
        index=True,
        help="The source's own key (conversation, portal request), so a retried "
        "submission finds the complaint it already created.",
    )
    conversation_id = fields.Many2one(
        "fix.conversation", string="Contact-Centre Conversation", readonly=True, copy=False
    )
    followup_ids = fields.One2many(
        "fix.cx.followup", compute="_compute_followup_ids", string="Detractor Follow-ups"
    )

    def _compute_followup_ids(self):
        # A lookup, not owned lines: the follow-up belongs to its survey.
        Followup = self.env["fix.cx.followup"]
        for rec in self:
            rec.followup_ids = (
                Followup.search([("complaint_id", "=", rec.id)])
                if isinstance(rec.id, int)
                else Followup
            )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"intake_channel", "intake_ref", "conversation_id"}

    @api.model
    def _intake_create(self, vals: dict):
        """Create a complaint from an intake channel, or return the one that
        intake already created (same intake_ref)."""
        ref = vals.get("intake_ref")
        if ref:
            existing = self.sudo().search([("intake_ref", "=", ref)], limit=1)
            if existing:
                return existing
        return self._guarded().create(vals)

    # ------------------------------------------------------------------
    # The customer portal
    # ------------------------------------------------------------------
    @api.model
    def _portal_partner(self, partner_id=None):
        """Whom a portal call acts for: the session user's own partner.

        An internal user (an agent filing on a customer's behalf) may name the
        partner; a portal user never can, so a customer files and reads only
        their own complaints (EA-05, as cd_customer_portal does)."""
        user = self.env.user
        if user._is_public():
            raise AccessError("Sign in to raise or read a complaint.")
        if partner_id and user._is_internal():
            partner = self.env["res.partner"].sudo().browse(int(partner_id)).exists()
            if not partner:
                raise UserError("Unknown customer.")
            return partner
        return user.partner_id.sudo()

    @api.model
    def _portal_operating_unit(self, order):
        if order:
            unit = order.operating_unit_id or order.branch_id.operating_unit_id
            if unit:
                return unit
        param = self.env["ir.config_parameter"].sudo().get_param(PARAM_PORTAL_OU)
        unit = (
            self.env["operating.unit"].sudo().browse(int(param)).exists()
            if param and str(param).isdigit()
            else None
        )
        return unit or self.env["operating.unit"].sudo().search(
            [("company_id", "=", self.env.company.id)], order="id", limit=1
        )

    @api.model
    def portal_submit_complaint(
        self,
        subject=None,
        description=None,
        category=None,
        service_order_id=None,
        description_bn=None,
        request_ref=None,
        partner_id=None,
    ):
        """Raise a complaint for the signed-in customer. Returns its summary.

        `request_ref` is the client's idempotency key: a retried submission
        returns the complaint the first one created."""
        partner = self._portal_partner(partner_id)
        subject = (subject or "").strip()
        description = (description or "").strip()
        if not subject or not description:
            raise UserError("Give the complaint a subject and describe what happened.")
        categories = dict(self._fields["category"].selection)
        category = category or "service_quality"
        if category not in categories:
            raise UserError("Unknown complaint category %r." % category)
        order = self.env["fix.service.order"]
        if service_order_id:
            order = order.sudo().browse(int(service_order_id)).exists()
            owner = order.customer_id.commercial_partner_id
            if not order or owner != partner.commercial_partner_id:
                raise UserError("That service order is not one of yours.")
        unit = self._portal_operating_unit(order)
        if not unit:
            raise UserError("No operating unit is configured to receive portal complaints.")
        # sudo: a portal user holds no ACL on complaints. Authorisation is
        # the partner check above; the complaint is still created as them.
        complaint = self.sudo()._intake_create(
            {
                "name": subject[:200],
                "description": description,
                "description_bn": (description_bn or "").strip() or False,
                "category": category,
                "severity": "minor",
                "customer_id": partner.id,
                "service_order_id": order.id or False,
                "operating_unit_id": unit.id,
                "company_id": unit.company_id.id or self.env.company.id,
                "intake_channel": "portal",
                "intake_ref": "portal:%d:%s" % (partner.id, request_ref) if request_ref else False,
            }
        )
        return complaint._portal_summary()

    def _portal_summary(self) -> dict:
        """What the customer may see of their complaint."""
        self.ensure_one()
        states = dict(self._fields["state"].selection)
        return {
            "id": self.id,
            "subject": self.name,
            "state": self.state,
            "state_label": states.get(self.state, self.state),
            "acknowledged_at": fields.Datetime.to_string(self.acknowledged_at)
            if self.acknowledged_at
            else None,
            "response": self.customer_response or None,
            "awaiting_your_decision": self.state == "responded",
            "closed_at": fields.Datetime.to_string(self.closed_at) if self.closed_at else None,
        }

    @api.model
    def portal_list_complaints(self, partner_id=None) -> list:
        partner = self._portal_partner(partner_id)
        complaints = self.sudo().search(
            [("customer_id", "child_of", partner.commercial_partner_id.id)],
            order="create_date desc, id desc",
            limit=50,
        )
        return [c._portal_summary() for c in complaints]

    @api.model
    def portal_complaint_decision(self, complaint_id=None, accept=None, note=None, partner_id=None):
        """The customer accepts or rejects the response from the portal."""
        partner = self._portal_partner(partner_id)
        complaint = self.sudo().browse(int(complaint_id or 0)).exists()
        if (
            not complaint
            or complaint.customer_id.commercial_partner_id != partner.commercial_partner_id
        ):
            raise UserError("That complaint is not one of yours.")
        if accept:
            complaint.action_customer_accept(note=note)
        else:
            complaint.action_customer_reject(reason=note)
        return complaint._portal_summary()


class FixConversationComplaint(models.Model):
    """M27 -> M34: a complaint raised from the conversation it came in on."""

    _inherit = "fix.conversation"

    complaint_id = fields.Many2one(
        "fix.complaint",
        string="Complaint",
        readonly=True,
        copy=False,
        index=True,
        ondelete="set null",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"complaint_id"}

    def _complaint_description(self) -> str:
        self.ensure_one()
        said = [
            t.text
            for t in self.turn_ids.sorted(lambda t: (t.sequence, t.id))
            if t.speaker == "customer" and (t.text or "").strip()
        ]
        parts = [p for p in (self.wrapup_notes, "\n".join(said)) if (p or "").strip()]
        return "\n\n".join(parts) or (
            "Raised from contact-centre conversation %s (%s)."
            % (self.display_name, self.intent or self.channel)
        )

    def action_create_complaint(self, category=None, severity=None):
        """Create the complaint this conversation is about, and link it.

        Idempotent per conversation: a second press returns the complaint
        the first one created. Requires an identified customer: a complaint
        nobody can be answered on is not one (the M27 macro's reason for
        refusing was that it would have guessed)."""
        Complaint = self.env["fix.complaint"]
        complaint = Complaint
        for conv in self:
            if conv.complaint_id:
                complaint |= conv.complaint_id
                continue
            if not conv.customer_id:
                raise UserError(
                    "Identify the customer on conversation %s before raising a complaint."
                    % conv.display_name
                )
            categories = dict(Complaint._fields["category"].selection)
            new = Complaint._intake_create(
                {
                    "name": "Complaint via %s: %s"
                    % (
                        dict(conv._fields["channel"].selection).get(conv.channel),
                        conv.display_name,
                    ),
                    "description": conv._complaint_description(),
                    "category": category if category in categories else "service_quality",
                    "severity": severity if severity in ("minor", "major", "critical") else "minor",
                    "customer_id": conv.customer_id.id,
                    "operating_unit_id": conv.operating_unit_id.id,
                    "company_id": conv.company_id.id,
                    "intake_channel": "contact_centre",
                    "intake_ref": "conversation:%d" % conv.id,
                    "conversation_id": conv.id,
                }
            )
            conv._guarded().write({"complaint_id": new.id})
            conv.message_post(body="Complaint %s raised from this conversation." % new.name)
            complaint |= new
        if len(complaint) == 1:
            return {
                "type": "ir.actions.act_window",
                "res_model": "fix.complaint",
                "res_id": complaint.id,
                "view_mode": "form",
                "complaint_id": complaint.id,
                "name": complaint.name,
            }
        return True


class FixCxFollowupComplaint(models.Model):
    """A detractor follow-up raises, or links, the complaint it reveals."""

    _inherit = "fix.cx.followup"

    complaint_id = fields.Many2one(
        "fix.complaint",
        string="Complaint",
        readonly=True,
        copy=False,
        index=True,
        ondelete="set null",
    )

    def _open_complaint_for_order(self):
        self.ensure_one()
        order = self.survey_id.service_order_id
        if not order:
            return self.env["fix.complaint"]
        return (
            self.env["fix.complaint"]
            .sudo()
            .search(
                [
                    ("service_order_id", "=", order.id),
                    ("state", "not in", ("closed", "rejected")),
                ],
                order="create_date desc",
                limit=1,
            )
        )

    def _link(self, complaint):
        for rec in self:
            trigger = dict(rec._fields["reason"].selection).get(rec.reason, rec.reason)
            rec.sudo().write(
                {
                    "complaint_id": complaint.id,
                    "reason": "complaint_linked",
                    "notes": (
                        (rec.notes or "")
                        + "\nLinked to complaint %s (trigger: %s)." % (complaint.name, trigger)
                    ).strip(),
                }
            )

    def _link_open_complaint(self):
        """Link an open complaint already raised on the same order, if any."""
        for rec in self.filtered(lambda r: not r.complaint_id):
            existing = rec._open_complaint_for_order()
            if existing:
                rec._link(existing)
        return True

    def action_raise_complaint(self):
        """Raise a complaint from this follow-up, or link the open one.

        Idempotent: the follow-up keeps the complaint it raised."""
        Complaint = self.env["fix.complaint"]
        for rec in self:
            if rec.complaint_id:
                continue
            existing = rec._open_complaint_for_order()
            if existing:
                rec._link(existing)
                continue
            survey = rec.survey_id
            if not survey.customer_id:
                raise UserError("The survey has no identified customer to raise a complaint for.")
            complaint = Complaint._intake_create(
                {
                    "name": "Detractor follow-up: %s" % (survey.service_order_id.name or survey.id),
                    "description": (survey.comment or rec.notes or "").strip()
                    or "Low satisfaction on survey %s." % survey.id,
                    "category": "service_quality",
                    "severity": "minor",
                    "customer_id": survey.customer_id.id,
                    "service_order_id": survey.service_order_id.id,
                    "operating_unit_id": survey.operating_unit_id.id,
                    "company_id": survey.company_id.id,
                    "intake_channel": "survey",
                    "intake_ref": "followup:%d" % rec.id,
                }
            )
            rec._link(complaint)
        return True
