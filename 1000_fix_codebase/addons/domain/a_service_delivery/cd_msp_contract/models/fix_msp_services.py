# fix_msp_services — M05 spec features the audit (2026-11-13) found with no
# model: client contacts and permissions (FR-RMS-049), major incidents
# (FR-RMS-020), service review meetings (FR-RMS-036), cloud subscriptions
# (FR-RMS-040), DR/BC plans and DR tests (FR-RMS-042/043) and the technology
# roadmap / strategy deliverables (FR-RMS-045/046).
#
# FILE NAME IS LOAD-BEARING: sorts (and so imports) after fix_msp_rules_bru.
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from .msp_roles import GROUP_ENGINEER, require_other_person, require_role

EVIDENCE_MIN = 10


def _text(value, what):
    value = (value or "").strip()
    if len(value) < EVIDENCE_MIN:
        raise UserError("Write %s (at least %d characters)." % (what, EVIDENCE_MIN))
    return value


# --------------------------------------------------------------- FR-RMS-049


class FixMspClientContact(models.Model):
    """Who at the client may do what: raise tickets, approve changes, receive
    the remote-session consent code, and in which order to escalate to them."""

    _name = "fix.msp.client.contact"
    _description = "MSP Client Contact"
    _inherit = ["mail.thread"]
    _order = "msp_contract_id, escalation_order, id"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    msp_contract_id = fields.Many2one(
        "fix.msp.contract", string="MSP Contract", required=True, index=True, ondelete="cascade"
    )
    partner_id = fields.Many2one("res.partner", string="Contact", required=True, tracking=True)
    role = fields.Selection(
        [
            ("it_manager", "IT Manager"),
            ("requester", "Requester"),
            ("approver", "Change Approver"),
            ("viewer", "Report Viewer"),
        ],
        required=True,
        default="requester",
        tracking=True,
    )
    can_raise_tickets = fields.Boolean(string="May Raise Tickets", default=True, tracking=True)
    can_approve_changes = fields.Boolean(string="May Approve Changes", tracking=True)
    can_receive_consent = fields.Boolean(
        string="Receives Remote-Session Consent Codes", tracking=True
    )
    escalation_order = fields.Integer(string="Escalation Order", default=10)
    escalation_channel = fields.Selection(
        [("phone", "Phone"), ("email", "Email"), ("sms", "SMS")],
        string="Escalation Channel",
        default="phone",
        required=True,
    )
    active = fields.Boolean(default=True)

    _contact_unique = models.Constraint(
        "unique(msp_contract_id, partner_id)", "A contact is registered once per MSP contract."
    )

    @api.constrains("partner_id", "msp_contract_id")
    def _check_contact_of_the_client(self):
        for contact in self:
            customer = contact.msp_contract_id.contract_id.customer_id.commercial_partner_id
            if customer and contact.partner_id.commercial_partner_id != customer:
                raise ValidationError(
                    "%s is not a contact of %s, the client of MSP contract %s."
                    % (contact.partner_id.name, customer.name, contact.msp_contract_id.name)
                )


class FixMspContractContacts(models.Model):
    _inherit = "fix.msp.contract"

    client_contact_ids = fields.One2many(
        "fix.msp.client.contact", "msp_contract_id", string="Client Contacts"
    )


class FixMspAlertContact(models.Model):
    _inherit = "fix.msp.alert"

    reported_by_contact_id = fields.Many2one(
        "fix.msp.client.contact",
        string="Reported By (Client Contact)",
        ondelete="restrict",
        help="FR-RMS-026/049: a client's ticket names the registered contact who "
        "raised it, and that contact must be allowed to raise tickets.",
    )
    major_incident_id = fields.Many2one(
        "fix.msp.major.incident", string="Major Incident", ondelete="set null"
    )

    @api.constrains("source", "reported_by_contact_id", "msp_contract_id")
    def _check_reporting_contact(self):
        for alert in self:
            if alert.source == "monitoring":
                continue
            contact = alert.reported_by_contact_id
            if not contact:
                raise ValidationError(
                    "A client's ticket names the client contact who reported it. Register "
                    "the contact on Client Contacts first (FR-RMS-049)."
                )
            if contact.msp_contract_id != alert.msp_contract_id or not contact.active:
                raise ValidationError(
                    "%s is not a contact of MSP contract %s."
                    % (contact.partner_id.name, alert.msp_contract_id.name)
                )
            if not contact.can_raise_tickets:
                raise ValidationError(
                    "%s is not allowed to raise tickets for %s."
                    % (contact.partner_id.name, alert.msp_contract_id.name)
                )


class FixRemoteSessionContact(models.Model):
    _inherit = "fix.remote.session"

    @api.constrains("consent_partner_id", "msp_contract_id")
    def _check_consent_contact_permitted(self):
        """When the client has registered its contacts, only one allowed to
        receive consent codes may consent (FR-RMS-049)."""
        for session in self:
            contacts = session.msp_contract_id.client_contact_ids
            if not contacts or not session.consent_partner_id:
                continue
            allowed = contacts.filtered("can_receive_consent").mapped("partner_id")
            if session.consent_partner_id not in allowed:
                raise ValidationError(
                    "%s is not registered to receive consent codes for %s."
                    % (session.consent_partner_id.name, session.msp_contract_id.name)
                )


# --------------------------------------------------------------- FR-RMS-020


class FixMspMajorIncident(models.Model):
    """A declared major incident: every client contact is notified, the
    resolution is recorded, and a post-incident review is written by someone
    other than the person who declared it."""

    _name = "fix.msp.major.incident"
    _description = "MSP Major Incident"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "declared_at desc, id desc"

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "declared_by_id",
            "declared_at",
            "notified_at",
            "notified_count",
            "resolved_at",
            "resolution_note",
            "review_note",
            "reviewed_by_id",
            "closed_at",
        }

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(string="Incident", required=True)
    msp_contract_id = fields.Many2one(
        "fix.msp.contract", string="MSP Contract", required=True, index=True
    )
    impact = fields.Text(string="Impact on the Client", required=True)
    alert_ids = fields.One2many("fix.msp.alert", "major_incident_id", string="Alerts and Tickets")
    state = fields.Selection(
        [
            ("declared", "Declared"),
            ("notified", "Contacts Notified"),
            ("resolved", "Resolved"),
            ("closed", "Closed (reviewed)"),
        ],
        default="declared",
        required=True,
        tracking=True,
    )
    declared_by_id = fields.Many2one(
        "res.users", string="Declared By", default=lambda self: self.env.user, readonly=True
    )
    declared_at = fields.Datetime(default=fields.Datetime.now, readonly=True)
    notified_at = fields.Datetime(readonly=True)
    notified_count = fields.Integer(string="Contacts Notified", readonly=True)
    resolved_at = fields.Datetime(readonly=True)
    resolution_note = fields.Text(readonly=True)
    review_note = fields.Text(string="Post-Incident Review", readonly=True)
    reviewed_by_id = fields.Many2one("res.users", string="Reviewed By", readonly=True)
    closed_at = fields.Datetime(readonly=True)

    @api.model_create_multi
    def create(self, vals_list):
        require_role(self.env, [GROUP_ENGINEER], "Declaring a major incident")
        return super().create(vals_list)

    def action_notify_contacts(self):
        """Notify every active contact of the client (FR-RMS-020)."""
        require_role(self.env, [GROUP_ENGINEER], "Notifying client contacts")
        for inc in self:
            if inc.state != "declared":
                raise UserError("Incident %s has already been notified." % inc.name)
            contacts = inc.msp_contract_id.client_contact_ids.filtered("active")
            if not contacts:
                raise UserError(
                    "MSP contract %s has no registered client contact to notify. Register "
                    "them on Client Contacts first." % inc.msp_contract_id.name
                )
            inc.message_post(
                body="Major incident declared on your managed service: %s. Impact: %s"
                % (inc.name, inc.impact),
                partner_ids=contacts.mapped("partner_id").ids,
                message_type="comment",
                subtype_xmlid="mail.mt_comment",
            )
            inc._guarded().write(
                {
                    "state": "notified",
                    "notified_at": fields.Datetime.now(),
                    "notified_count": len(contacts),
                }
            )
        return True

    def action_resolve(self, note=None):
        require_role(self.env, [GROUP_ENGINEER], "Resolving a major incident")
        text = _text(note, "how the incident was resolved")
        for inc in self:
            if inc.state != "notified":
                raise UserError(
                    "Incident %s is resolved after its client contacts are notified." % inc.name
                )
            inc._guarded().write(
                {"state": "resolved", "resolved_at": fields.Datetime.now(), "resolution_note": text}
            )
        return True

    def action_record_review(self, note=None):
        """The post-incident review: root cause, what changes, follow-ups. By
        someone other than the declarer, and it closes the incident."""
        require_role(self.env, [GROUP_ENGINEER], "Reviewing a major incident")
        text = _text(note, "the post-incident review")
        for inc in self:
            if inc.state != "resolved":
                raise UserError("Incident %s is reviewed once it is resolved." % inc.name)
            require_other_person(self.env, inc.declared_by_id, "Reviewing a major incident")
            inc._guarded().write(
                {
                    "state": "closed",
                    "review_note": text,
                    "reviewed_by_id": self.env.uid,
                    "closed_at": fields.Datetime.now(),
                }
            )
        return True


# --------------------------------------------------------------- FR-RMS-036


class FixMspServiceReview(models.Model):
    """A client service review meeting: who attended, the report discussed,
    the actions agreed. It closes only when every action is done."""

    _name = "fix.msp.service.review"
    _description = "MSP Service Review Meeting"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "meeting_date desc, id desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    msp_contract_id = fields.Many2one(
        "fix.msp.contract", string="MSP Contract", required=True, index=True
    )
    meeting_date = fields.Date(string="Meeting Date", required=True, default=fields.Date.today)
    attendees = fields.Text(string="Attendees", required=True)
    service_report_id = fields.Many2one("fix.msp.service.report", string="Service Report Discussed")
    summary = fields.Text(string="Discussion & Decisions")
    action_ids = fields.One2many("fix.msp.review.action", "review_id", string="Actions Agreed")
    next_review_date = fields.Date(string="Next Review")
    state = fields.Selection(
        [("held", "Held"), ("closed", "Closed")], default="held", required=True, tracking=True
    )
    open_action_count = fields.Integer(compute="_compute_open_actions", string="Open Actions")

    @api.depends("action_ids.done")
    def _compute_open_actions(self):
        for review in self:
            review.open_action_count = len(review.action_ids.filtered(lambda a: not a.done))

    @api.constrains("service_report_id", "msp_contract_id")
    def _check_report_of_the_contract(self):
        for review in self:
            if review.service_report_id and (
                review.service_report_id.msp_contract_id != review.msp_contract_id
            ):
                raise ValidationError("The service report discussed is another contract's.")

    @api.constrains("meeting_date", "next_review_date")
    def _check_dates(self):
        for review in self:
            if review.next_review_date and review.next_review_date <= review.meeting_date:
                raise ValidationError("The next review is after this meeting.")

    def action_close(self):
        require_role(self.env, [GROUP_ENGINEER], "Closing a service review")
        for review in self:
            if review.open_action_count:
                raise UserError(
                    "%d action(s) agreed at the %s review are still open: complete them "
                    "before the review is closed." % (review.open_action_count, review.meeting_date)
                )
            review.state = "closed"
        return True


class FixMspReviewAction(models.Model):
    _name = "fix.msp.review.action"
    _description = "MSP Service Review Action"
    _order = "due_date, id"

    review_id = fields.Many2one(
        "fix.msp.service.review", required=True, ondelete="cascade", index=True
    )
    company_id = fields.Many2one(related="review_id.company_id", store=True)
    name = fields.Char(string="Action", required=True)
    owner_id = fields.Many2one("res.users", string="Owner")
    due_date = fields.Date(string="Due")
    done = fields.Boolean(string="Done")


# --------------------------------------------------------------- FR-RMS-040


class FixMspCloudSubscription(models.Model):
    """A client cloud subscription managed under the contract: seats, cost
    and renewal, flagged 30 days before it renews."""

    _name = "fix.msp.cloud.subscription"
    _description = "MSP Cloud Subscription"
    _inherit = ["mail.thread"]
    _order = "renewal_date, id"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    msp_contract_id = fields.Many2one(
        "fix.msp.contract", string="MSP Contract", required=True, index=True
    )
    provider = fields.Selection(
        [
            ("m365", "Microsoft 365"),
            ("google", "Google Workspace"),
            ("azure", "Microsoft Azure"),
            ("aws", "Amazon Web Services"),
            ("other", "Other"),
        ],
        required=True,
    )
    name = fields.Char(string="Plan / Subscription", required=True)
    seats = fields.Integer(string="Seats / Licences", default=1)
    seats_used = fields.Integer(string="Seats In Use")
    currency_id = fields.Many2one(related="msp_contract_id.currency_id")
    unit_cost = fields.Monetary(string="Monthly Cost per Seat", currency_field="currency_id")
    monthly_cost = fields.Monetary(
        compute="_compute_monthly_cost", store=True, currency_field="currency_id"
    )
    renewal_date = fields.Date(string="Renews On", required=True)
    state = fields.Selection(
        [("active", "Active"), ("cancelled", "Cancelled")], default="active", required=True
    )
    renewal_due = fields.Boolean(
        compute="_compute_renewal_due", string="Renews Within 30 Days", search="_search_renewal_due"
    )

    @api.depends("seats", "unit_cost")
    def _compute_monthly_cost(self):
        for sub in self:
            sub.monthly_cost = (sub.seats or 0) * (sub.unit_cost or 0.0)

    @api.depends("state", "renewal_date")
    def _compute_renewal_due(self):
        limit = fields.Date.context_today(self) + timedelta(days=30)
        for sub in self:
            sub.renewal_due = sub.state == "active" and sub.renewal_date <= limit

    def _search_renewal_due(self, operator, value):
        limit = fields.Date.context_today(self) + timedelta(days=30)
        due = [("state", "=", "active"), ("renewal_date", "<=", limit)]
        # Odoo normalises "= True" to "in [True]"
        if operator in ("in", "not in"):
            wanted = True in (value or [])
            positive = wanted if operator == "in" else not wanted
        else:
            positive = (operator == "=") == bool(value)
        return due if positive else ["!", "&", *due]

    @api.constrains("seats", "seats_used", "unit_cost")
    def _check_seats(self):
        for sub in self:
            if sub.seats < 0 or sub.seats_used < 0 or (sub.unit_cost or 0) < 0:
                raise ValidationError("Seats and cost cannot be negative.")


# --------------------------------------------------------------- FR-RMS-042/043


class FixMspDrPlan(models.Model):
    """A client disaster-recovery / continuity plan with its recovery
    targets and how often it must be tested."""

    _name = "fix.msp.dr.plan"
    _description = "MSP DR / BC Plan"
    _inherit = ["mail.thread"]
    _order = "msp_contract_id, name"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    msp_contract_id = fields.Many2one(
        "fix.msp.contract", string="MSP Contract", required=True, index=True
    )
    name = fields.Char(string="Plan", required=True)
    scope = fields.Text(string="Systems Covered", required=True)
    rto_hours = fields.Float(string="Recovery Time Objective (h)", required=True)
    rpo_hours = fields.Float(string="Recovery Point Objective (h)", required=True)
    test_interval_days = fields.Integer(string="Test Every (days)", default=180, required=True)
    test_ids = fields.One2many("fix.msp.dr.test", "plan_id", string="Tests")
    last_test_date = fields.Date(compute="_compute_test_dates", string="Last Test", store=True)
    next_test_due = fields.Date(compute="_compute_test_dates", string="Next Test Due", store=True)
    active = fields.Boolean(default=True)

    @api.depends("test_ids.test_date", "test_interval_days", "create_date")
    def _compute_test_dates(self):
        for plan in self:
            last = max(plan.test_ids.mapped("test_date"), default=False)
            plan.last_test_date = last
            start = last or (plan.create_date and plan.create_date.date())
            plan.next_test_due = (
                start + timedelta(days=plan.test_interval_days or 0) if start else False
            )

    @api.constrains("rto_hours", "rpo_hours", "test_interval_days")
    def _check_targets(self):
        for plan in self:
            if plan.rto_hours <= 0 or plan.rpo_hours < 0 or plan.test_interval_days <= 0:
                raise ValidationError(
                    "A DR plan needs a positive RTO, an RPO of zero or more, and a test interval."
                )


class FixMspDrTest(models.Model):
    """One DR test: what was achieved against the plan's targets, with its
    evidence. "Passed" is only recorded when both targets were met."""

    _name = "fix.msp.dr.test"
    _description = "MSP DR Test"
    _inherit = ["fix.guarded.mixin"]
    _order = "test_date desc, id desc"

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "plan_id",
            "test_date",
            "outcome",
            "rto_achieved_hours",
            "rpo_achieved_hours",
            "evidence",
            "tested_by_id",
        }

    def _fix_form_locked_fields(self) -> set:
        if not self:
            return {"tested_by_id"}
        return super()._fix_form_locked_fields()

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    plan_id = fields.Many2one("fix.msp.dr.plan", string="DR Plan", required=True, index=True)
    msp_contract_id = fields.Many2one(related="plan_id.msp_contract_id", store=True)
    test_date = fields.Date(required=True, default=fields.Date.today)
    outcome = fields.Selection(
        [("passed", "Passed"), ("partial", "Partial"), ("failed", "Failed")], required=True
    )
    rto_achieved_hours = fields.Float(string="Recovery Time Achieved (h)", required=True)
    rpo_achieved_hours = fields.Float(string="Data Loss Window Achieved (h)", required=True)
    meets_targets = fields.Boolean(compute="_compute_meets", store=True, string="Met Targets")
    evidence = fields.Text(string="Evidence", required=True)
    tested_by_id = fields.Many2one(
        "res.users", string="Tested By", default=lambda self: self.env.user, readonly=True
    )

    @api.depends("rto_achieved_hours", "rpo_achieved_hours", "plan_id")
    def _compute_meets(self):
        for test in self:
            test.meets_targets = bool(test.plan_id) and (
                test.rto_achieved_hours <= test.plan_id.rto_hours
                and test.rpo_achieved_hours <= test.plan_id.rpo_hours
            )

    @api.model_create_multi
    def create(self, vals_list):
        """Recorded once by an engineer; afterwards it is evidence."""
        if self._fix_guard_open():
            return super().create(vals_list)
        require_role(self.env, [GROUP_ENGINEER], "Recording a DR test")
        for vals in vals_list:
            _text(vals.get("evidence"), "the evidence of the DR test")
        return super(FixMspDrTest, self._guarded()).create(vals_list).with_env(self.env)

    @api.constrains("outcome", "rto_achieved_hours", "rpo_achieved_hours")
    def _check_outcome_matches_targets(self):
        for test in self:
            if test.rto_achieved_hours < 0 or test.rpo_achieved_hours < 0:
                raise ValidationError("Achieved recovery times cannot be negative.")
            if test.outcome == "passed" and not test.meets_targets:
                raise ValidationError(
                    "The test missed its targets (RTO %g h, RPO %g h): it is Partial or "
                    "Failed, not Passed." % (test.plan_id.rto_hours, test.plan_id.rpo_hours)
                )


# --------------------------------------------------------------- FR-RMS-045/046


class FixMspRoadmapItem(models.Model):
    """A strategy deliverable or technology recommendation for the client;
    an accepted one can become a sales opportunity (M07)."""

    _name = "fix.msp.roadmap.item"
    _description = "MSP Technology Roadmap Item"
    _inherit = ["mail.thread"]
    _order = "target_quarter, id"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    msp_contract_id = fields.Many2one(
        "fix.msp.contract", string="MSP Contract", required=True, index=True
    )
    kind = fields.Selection(
        [
            ("refresh", "Hardware Refresh"),
            ("recommendation", "Recommendation"),
            ("deliverable", "Strategy Deliverable"),
        ],
        required=True,
        default="recommendation",
    )
    name = fields.Char(string="Item", required=True)
    description = fields.Text(string="Rationale")
    asset_id = fields.Many2one("fix.monitored.asset", string="Asset Concerned")
    target_quarter = fields.Char(string="Target Quarter (e.g. 2027-Q1)")
    estimated_value = fields.Monetary(string="Estimated Value (BDT)", currency_field="currency_id")
    currency_id = fields.Many2one(related="msp_contract_id.currency_id")
    state = fields.Selection(
        [
            ("proposed", "Proposed"),
            ("accepted", "Accepted by Client"),
            ("delivered", "Delivered"),
            ("declined", "Declined"),
        ],
        default="proposed",
        required=True,
        tracking=True,
    )
    lead_id = fields.Many2one("crm.lead", string="Sales Opportunity", readonly=True, copy=False)

    @api.constrains("asset_id", "msp_contract_id")
    def _check_asset_of_contract(self):
        for item in self:
            if item.asset_id and item.asset_id.msp_contract_id != item.msp_contract_id:
                raise ValidationError("The asset concerned is another contract's.")

    @api.constrains("target_quarter")
    def _check_quarter(self):
        import re

        for item in self:
            if item.target_quarter and not re.fullmatch(r"\d{4}-Q[1-4]", item.target_quarter):
                raise ValidationError("Write the target quarter as YYYY-Qn, e.g. 2027-Q1.")

    def _move(self, frm, to, what):
        require_role(self.env, [GROUP_ENGINEER], what)
        for item in self:
            if item.state not in frm:
                raise UserError("%s is %s." % (item.name, item.state))
            item.state = to
        return True

    def action_accept(self):
        return self._move(("proposed",), "accepted", "Recording the client's acceptance")

    def action_decline(self):
        return self._move(("proposed",), "declined", "Recording the client's decline")

    def action_deliver(self):
        return self._move(("accepted",), "delivered", "Recording a delivered roadmap item")

    def action_create_opportunity(self):
        """Feed sales (FR-RMS-046): an accepted refresh or recommendation
        becomes an M07 opportunity for the client, once."""
        require_role(self.env, [GROUP_ENGINEER], "Raising a sales opportunity")
        for item in self:
            if item.state != "accepted":
                raise UserError("Only an item the client accepted becomes an opportunity.")
            if item.lead_id:
                raise UserError("%s already has opportunity %s." % (item.name, item.lead_id.name))
            customer = item.msp_contract_id.contract_id.customer_id
            lead = (
                self.env["crm.lead"]
                .sudo()
                .create(
                    {
                        "name": "%s: %s" % (customer.name or item.msp_contract_id.name, item.name),
                        "type": "opportunity",
                        "partner_id": customer.id or False,
                        "expected_revenue": item.estimated_value or 0.0,
                        "description": item.description or "",
                    }
                )
            )
            item.lead_id = lead
            item.message_post(body="Sales opportunity %s raised." % lead.name)
        return True
