# cd_cx_feedback — M34 Customer Experience + M42 Supplier Performance
# (P07-M06, CD-M34-nn/CD-M42-nn).
#
# M34: feedback/survey/rating capture, the complaint lifecycle with
# escalation, and survey triggering FROM service_order.closed events (AS-08 —
# no synchronous call into M01). T03/T07: the M23 NCR/CAPA linkages are
# REGISTERED STUBS with expiry dates (AR-006 §5.4 STUB + GV-005).
#
# M42: a READ-AND-SCORE consumer of M16 events (AR-006 §4.1 pair 10 — the
# asymmetric interface designed in Phase 6, implemented here): scorecards
# computed from goods.received / po.issued events, never a reach into M16.
import base64
import hashlib
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish  # FF-28

# A 1-5 rating at or below this is a detractor. ONE constant for both the NPS
# score and the recovery trigger: they disagreed (A03 audit M34-10), so a
# rating of 3 scored as a detractor (-100) yet raised no recovery task.
DETRACTOR_MAX_RATING = 3


class FixSurvey(models.Model):
    """T04: the post-service survey, triggered by consuming
    service_order.closed (NT-024's deferred send — never at completion)."""

    _name = "fix.survey"
    _description = "Service Survey"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc, id desc"
    # Odoo 19 dropped the legacy constraint tuple list;
    # models.Constraint attributes (migrated by tooling/scripts/migrate-sql-constraints.py)
    _order_unique = models.Constraint("UNIQUE (service_order_id)", "One survey per service order")

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", required=True, index=True)
    service_order_id = fields.Many2one(
        "fix.service.order", string="Service Order", required=True, ondelete="cascade", index=True
    )
    customer_id = fields.Many2one(related="service_order_id.customer_id", store=True, index=True)
    state = fields.Selection(
        [
            ("pending", "Pending"),
            ("sent", "Sent"),
            ("responded", "Responded"),
            ("expired", "Expired"),
        ],
        default="pending",
        required=True,
        tracking=True,
    )
    rating = fields.Selection(
        [
            ("1", "খুব খারাপ / Very Poor"),
            ("2", "খারাপ / Poor"),
            ("3", "মোটামুটি / Fair"),
            ("4", "ভালো / Good"),
            ("5", "খুব ভালো / Excellent"),
        ],
        string="Overall Rating (NPS-style)",
    )
    nps_score = fields.Integer(
        compute="_compute_nps", store=True, help="-100..+100 — detractors(1-3) vs promoters(5)"
    )
    comment = fields.Text()
    source_event_id = fields.Char(
        readonly=True, index=True, help="The service_order.closed event — replay key"
    )
    # --- dispatch bookkeeping (A03 gap-plan W1/W2) --------------------
    # 'sent' used to mean "a survey row was created". It now means a message
    # was queued on the S1 delivery service, and these three fields say which
    # one, on what channel, or why nothing went out.
    dispatch_channel = fields.Selection(
        [("sms", "SMS"), ("email", "E-mail"), ("whatsapp", "WhatsApp"), ("push", "Push")],
        string="Dispatch Channel",
        readonly=True,
        copy=False,
    )
    dispatch_delivery_id = fields.Many2one(
        "fix.notif.delivery",
        string="Delivery Row",
        readonly=True,
        copy=False,
        ondelete="set null",
        help="The S1 delivery row for this survey invitation. Empty means no "
        "message was queued, and dispatch_suppressed_reason says why.",
    )
    dispatch_suppressed_reason = fields.Text(
        string="Not Dispatched Because",
        readonly=True,
        copy=False,
        help="The throttle or consent reason the invitation was withheld. A "
        "survey that was never sent must not look like one awaiting a reply.",
    )

    @api.depends("service_order_id.display_name")
    def _compute_display_name(self):
        # No name field, so every many2one to a survey rendered "fix.survey,15".
        # One survey per order (_order_unique), so the order names it.
        for survey in self:
            order = survey.service_order_id.display_name
            survey.display_name = (
                "জরিপ (Survey) · %s" % order if order else "জরিপ (Survey) #%s" % survey.id
            )

    @api.depends("rating")
    def _compute_nps(self):
        for survey in self:
            if not survey.rating:
                survey.nps_score = 0
            elif int(survey.rating) >= 5:
                survey.nps_score = 100
            elif int(survey.rating) <= DETRACTOR_MAX_RATING:
                survey.nps_score = -100
            else:
                survey.nps_score = 0

    @api.model
    def consume_order_closed(self, event: dict) -> "FixSurvey | None":
        """T04: journey 1 ends here — the closed event triggers the survey
        (deferred per NT-024, never at completion time). Idempotent on the
        order.

        A03 audit M34-4: this had no caller, so 22 closed orders produced no
        survey. It is now the R8 consumer of service_order.closed
        (data/fix_cx_event_consumers.xml) and takes the relay's event dict.
        An event for another aggregate, or for an order that no longer
        exists, is acknowledged and ignored rather than raised: a consumer
        that throws is retried and dead-lettered, which would report a data
        gap as a fault."""
        if event.get("aggregate") not in (None, "fix.service.order"):
            return None
        order_id = event.get("aggregate_id") or (event.get("payload") or {}).get("order_id")
        if not order_id:
            return None
        existing = self.search([("service_order_id", "=", int(order_id))])
        if existing:
            return existing
        # AS-03: the survey belongs to the order's operating unit (the field is
        # required - the former create omitted it, so every survey failed)
        order = self.env["fix.service.order"].browse(int(order_id)).exists()
        if not order:
            return None
        survey = self.create(
            {
                "service_order_id": order.id,
                "operating_unit_id": (
                    order.operating_unit_id or order.branch_id.operating_unit_id
                ).id,
                "source_event_id": event.get("event_id", ""),
                "state": "pending",
            }
        )
        survey.action_dispatch_invitation()
        return survey

    # ------------------------------------------------------------------
    # Dispatch (A03 gap-plan: throttle enforcement + S1)
    # ------------------------------------------------------------------
    def _dispatch_target(self):
        """Where to invite this customer, or why we cannot.

        Returns (channel, address, reason). A walk-in whose phone was never
        recorded is a real and common case, so "nobody to write to" is an
        ANSWER here rather than an exception: S1 rightly refuses to invent a
        destination, and this is the caller deciding what to do about it.

        SMS is preferred because it is the channel the whole customer base
        has; e-mail is used when that is all we hold. The choice is recorded
        on the survey, so response-rate analysis by channel has a real basis.
        """
        self.ensure_one()
        partner = self.customer_id
        if not partner:
            return (
                None,
                None,
                (
                    "No customer is identified on the service order, so there is "
                    "nobody to invite."
                ),
            )
        # getattr: res.partner carries `mobile` in some Odoo builds and not
        # others, and a survey must not crash on the ones without it.
        phone = (getattr(partner, "mobile", False) or partner.phone or "").strip()
        if phone:
            return "sms", phone, ""
        email = (partner.email or "").strip()
        if email:
            return "email", email, ""
        return (
            None,
            None,
            (
                "No phone or e-mail is on file for this customer, so the survey "
                "invitation cannot be addressed. The survey stays pending rather "
                "than counting as asked."
            ),
        )

    def action_dispatch_invitation(self):
        """Send the survey invitation, or record why it was withheld.

        Two gates, in this order:
          1. the M34 per-customer monthly contact cap (fix.cx.throttle) --
             a customer with four repairs in a month should not get four
             surveys;
          2. the S1 delivery service, which applies the M33 consent decision
             and the BTRC window and logs the message either way.

        A withheld invitation leaves the survey 'pending' with a stated
        reason, never 'sent'. That distinction is the whole point: an NPS
        basis computed over surveys that were never asked is a fiction.
        """
        Throttle = self.env["fix.cx.throttle"]
        Delivery = self.env["fix.notif.delivery"]
        for survey in self:
            if survey.state != "pending" or survey.dispatch_delivery_id:
                continue
            channel, address, address_reason = survey._dispatch_target()
            if not channel:
                survey.write({"dispatch_suppressed_reason": address_reason})
                publish(
                    self.env,
                    "survey.invitation_withheld",
                    "fix.survey",
                    survey.id,
                    {
                        "partner_id": survey.customer_id.id or None,
                        "channel": None,
                        "reason": address_reason,
                        "gate": "addressable",
                    },
                )
                continue
            verdict = Throttle.evaluate(survey.customer_id, channel)
            if not verdict["allowed"]:
                survey.write(
                    {
                        "dispatch_channel": channel,
                        "dispatch_suppressed_reason": verdict["reason"],
                    }
                )
                publish(
                    self.env,
                    "survey.invitation_withheld",
                    "fix.survey",
                    survey.id,
                    {
                        "partner_id": survey.customer_id.id or None,
                        "channel": channel,
                        "reason": verdict["reason"],
                        "gate": "throttle",
                    },
                )
                continue

            order_name = survey.service_order_id.name or str(survey.service_order_id.id)
            body = (
                "1000FiX Services: অর্ডার %s সম্পন্ন হয়েছে। আপনার অভিজ্ঞতা ১-৫ "
                "স্কেলে জানান। / Order %s is complete. Rate your experience 1-5. "
                "Hotline 16743" % (order_name, order_name)
            )
            delivery = Delivery.queue(
                channel=channel,
                purpose="service_updates",
                partner=survey.customer_id or None,
                to_address=address,
                body=body,
                # Declared basis, recorded on every row: the customer is being
                # asked about a repair they commissioned. If Legal rules this
                # needs opt-in consent instead, the affected sends are findable
                # by this exact value and one declaration changes.
                lawful_basis="contract",
                source_model="fix.survey",
                source_id=survey.id,
                source_event_id=survey.source_event_id or None,
                dedup_key="survey-invite:%d" % survey.id,
                operating_unit=survey.operating_unit_id,
                company=survey.company_id,
            )
            if delivery.state == "suppressed":
                survey.write(
                    {
                        "dispatch_channel": channel,
                        "dispatch_delivery_id": delivery.id,
                        "dispatch_suppressed_reason": delivery.consent_reason,
                    }
                )
                publish(
                    self.env,
                    "survey.invitation_withheld",
                    "fix.survey",
                    survey.id,
                    {
                        "partner_id": survey.customer_id.id or None,
                        "channel": channel,
                        "reason": delivery.consent_reason,
                        "gate": "consent",
                        "delivery_id": delivery.id,
                    },
                )
                continue

            Throttle.register_send(survey.customer_id, channel, company=survey.company_id)
            survey.write(
                {
                    "state": "sent",
                    "dispatch_channel": channel,
                    "dispatch_delivery_id": delivery.id,
                    "dispatch_suppressed_reason": False,
                }
            )
        return True

    @api.model
    def cron_retry_withheld_invitations(self, limit=200):
        """Re-offer invitations that a monthly cap withheld.

        A survey withheld in January is still worth asking in February: the
        cap is a frequency rule, not a cancellation. One that was withheld on
        CONSENT grounds is not retried here -- consent changing is an event,
        not something to poll for.
        """
        pending = self.sudo().search(
            [
                ("state", "=", "pending"),
                ("dispatch_suppressed_reason", "!=", False),
                ("dispatch_delivery_id", "=", False),
            ],
            limit=limit,
        )
        before = len(pending.filtered(lambda s: s.state == "pending"))
        pending.action_dispatch_invitation()
        sent = len(pending.filtered(lambda s: s.state == "sent"))
        return {"considered": before, "dispatched": sent}


class FixComplaint(models.Model):
    """T02: the complaint lifecycle — complaint -> non-conformance -> root
    cause -> CAPA -> verification -> closure (journey 14)."""

    _name = "fix.complaint"
    _description = "Complaint"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.dofa.mixin"]

    # A03 audit R7: a concession is approved from the approver's M63 inbox.
    _approval_domain = "concession"
    _approval_apply_method = "action_approve_concession"
    _approval_routed = True
    _order = "create_date desc, id desc"

    # REQ-34.3 service-recovery thresholds in BDT. As with M10 the REQ text and
    # the DOFA matrix disagree (REQ: >1,000 Tier 2, >5,000 Tier 3; matrix:
    # <=500 Tier 1, <=2,500 Tier 2, <=10,000 Tier 3). The REQ text is
    # implemented; switching to the matrix is this one list.
    _DOFA_CONCESSION_THRESHOLDS = [
        (1000.0, "tier_1"),
        (5000.0, "tier_2"),
        (10000.0, "tier_3"),
        (float("inf"), "tier_4"),
    ]

    def _dofa_amount(self) -> float:
        self.ensure_one()
        return self.concession_amount or 0.0

    def _dofa_thresholds(self):
        return self._DOFA_CONCESSION_THRESHOLDS

    def _dofa_amount_label(self) -> str:
        self.ensure_one()
        return "a %s of BDT %.2f" % (
            dict(self._fields["concession_type"].selection).get(self.concession_type, "concession"),
            self.concession_amount or 0.0,
        )

    @api.depends("concession_amount")
    def _compute_dofa_tier_required(self):
        return super()._compute_dofa_tier_required()

    def _fix_guarded_fields(self) -> set:
        # The lifecycle and the concession sign-off change only through the
        # actions below: a plain write closed a critical complaint with no
        # RCA or CAPA, and forged the approval on a BDT 250,000 refund.
        return super()._fix_guarded_fields() | {
            "state",
            "concession_approved",
            "concession_approver_id",
            "post_closure_survey_sent_at",
        }

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", required=True, index=True)
    name = fields.Char(required=True)
    customer_id = fields.Many2one(
        "res.partner", string="Customer", required=True, index=True, ondelete="restrict"
    )
    service_order_id = fields.Many2one(
        "fix.service.order", string="Service Order", index=True, ondelete="set null"
    )
    category = fields.Selection(
        [
            ("service_quality", "Service Quality"),
            ("delay", "Delay / SLA"),
            ("billing", "Billing"),
            ("staff_conduct", "Staff Conduct"),
            ("device_damage", "Device Damage"),
            ("other", "Other"),
        ],
        required=True,
        default="service_quality",
    )
    severity = fields.Selection(
        [("minor", "Minor"), ("major", "Major"), ("critical", "Critical")],
        default="minor",
        required=True,
        tracking=True,
    )
    # ISO 10002:2018 cl. 7 as states (A03 audit M34-3). 'new' is receipt;
    # acknowledgement is stamped at create (cl. 7.3 asks for it at once), so
    # it is a timestamp rather than a state somebody has to remember to set.
    # Every state below has a transition method in fix_complaint_lifecycle.py.
    state = fields.Selection(
        [
            ("new", "Received"),
            ("assessed", "Assessed"),
            ("investigating", "Investigating"),
            ("ncr_raised", "NCR Raised"),
            ("root_cause", "Root Cause Identified"),
            ("capa_open", "CAPA Open"),
            ("verification", "CAPA Verification"),
            ("responded", "Response Sent"),
            ("accepted", "Customer Accepted"),
            ("closed", "Closed"),
            ("rejected", "Declined (not upheld)"),
        ],
        default="new",
        required=True,
        tracking=True,
    )
    description = fields.Text(required=True)
    name_bn = fields.Char(
        string="Subject (Bengali)",
        help="DE-17: the complaint subject as the customer stated it. A "
        "complaint quoted back to a customer in a language they did not use "
        "reads as a different complaint.",
    )
    description_bn = fields.Text(
        string="Description (Bengali)",
        help="DE-17: the customer's own words. Kept alongside the English "
        "working text rather than replacing it, because the original wording "
        "is the evidence in a dispute.",
    )
    resolution = fields.Text()
    # T03: the M23 NCR/CAPA linkage stubs (registered, with expiry)
    ncr_stub_ref = fields.Char(
        readonly=True,
        help="AR-006 §5.4 STUB: M23 lands W5 — the NCR "
        "reference links then; stub expiry 2027-03-31",
    )
    capa_stub_ref = fields.Char(
        string="CAPA Reference",
        tracking=True,
        help="The CAPA that resolved this complaint, entered by the quality owner "
        "when M23 (cd_qms_process) is not installed. With M23 installed the "
        "complaint's linked CAPA record (capa_id) is what counts.",
    )
    # ISO 10002 Root Cause & DOFA Concession fields (FLAW-34.1, FLAW-34.2, FLAW-34.3)
    root_cause_5why = fields.Text(
        string="5-Why Root Cause Analysis",
        tracking=True,
        help="Mandatory 5-Why root cause breakdown before closing critical/major complaints (FLAW-34.1)",
    )
    five_why_verified = fields.Boolean(string="5-Why RCA Verified", default=False, tracking=True)
    concession_amount = fields.Monetary(
        string="Recovery Concession (BDT)",
        currency_field="currency_id",
        default=0.0,
        tracking=True,
    )
    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        default=lambda self: self.env.ref("base.BDT", raise_if_not_found=False)
        or self.env.company.currency_id,
    )
    concession_type = fields.Selection(
        [
            ("none", "None"),
            ("waiver", "Diagnostic Fee Waiver"),
            ("discount", "Discount Voucher"),
            ("refund", "Cash / MFS Refund"),
        ],
        default="none",
        string="Concession Type",
        tracking=True,
    )
    concession_approved = fields.Boolean(
        string="Concession DOFA Approved", default=False, tracking=True
    )
    concession_approver_id = fields.Many2one(
        "res.users", string="DOFA Approver", readonly=True, tracking=True
    )
    acknowledged_at = fields.Datetime(string="Formal Acknowledgment Sent At", readonly=True)
    # --- S9 SLA binding per severity (A03 gap-plan M34 row) -----------
    # The engine is M01's (fix.sla.kpi.instance). M34 does not re-implement a
    # clock; it names the policy its severity buys and lets the engine run it.
    sla_policy_id = fields.Many2one(
        "fix.sla.policy",
        string="SLA Policy",
        readonly=True,
        copy=False,
        help="Resolved from the severity at intake. Empty means no policy is "
        "configured for that severity, which is reported rather than assumed.",
    )
    sla_instance_ids = fields.One2many(
        "fix.sla.kpi.instance",
        compute="_compute_sla_instances",
        string="SLA Clocks",
        help="The append-only instance series for this complaint. A resume "
        "cancels an instance and creates its successor, so there may be "
        "several per KPI.",
    )
    sla_resolution_state = fields.Char(
        compute="_compute_sla_instances",
        string="Resolution SLA",
        help="The live resolution clock's state, or why there is none.",
    )
    # REQ-34.5 / REQ-34.6 closed-loop fields
    escalated_at = fields.Datetime(
        string="Escalated to COO At", readonly=True, copy=False, tracking=True
    )
    quality_warning = fields.Boolean(
        string="Branch Quality Warning",
        default=False,
        readonly=True,
        copy=False,
        tracking=True,
        help="Set when the complaint breached the 72-hour resolution SLA (REQ-34.5).",
    )
    post_closure_survey_sent_at = fields.Datetime(
        string="Post-Resolution Survey Sent At", readonly=True, copy=False
    )

    # --- REQ-34.4 evidence repository ------------------------------------
    # Damage photographs, written complaints, technician incident reports,
    # CCTV references and signed settlement releases. The A03 audit
    # (2026-10-31) found these had nowhere to live: the docs tab was a label
    # with no storage, while cd_document_core already offered SHA-256 digests
    # and retention classes. A03 simply never used it.
    EVIDENCE_RETENTION_DAYS = 730  # Consumer Rights Protection Act 2009

    evidence_ids = fields.One2many(
        "fix.document",
        compute="_compute_evidence",
        string="Complaint Evidence",
        help="Checksummed evidence on the estate document repository.",
    )
    evidence_count = fields.Integer(compute="_compute_evidence", string="Evidence Files")
    evidence_sha256_list = fields.Char(compute="_compute_evidence", string="Evidence Digests")
    evidence_retention_until = fields.Date(
        string="Evidence Retained Until",
        compute="_compute_evidence_retention",
        store=True,
        help="REQ-34.4: 730 days from intake, for DNCRP and regulatory inquiry.",
    )

    def _compute_evidence(self):
        Document = self.env["fix.document"]
        for rec in self:
            docs = (
                Document.search([("res_model", "=", "fix.complaint"), ("res_id", "=", rec.id)])
                if rec.id
                else Document.browse()
            )
            rec.evidence_ids = docs
            rec.evidence_count = len(docs)
            rec.evidence_sha256_list = ", ".join(
                d.checksum_sha256 for d in docs if d.checksum_sha256
            )

    @api.depends("create_date")
    def _compute_evidence_retention(self):
        for rec in self:
            start = fields.Date.to_date(rec.create_date) or fields.Date.today()
            rec.evidence_retention_until = start + timedelta(days=rec.EVIDENCE_RETENTION_DAYS)

    def attach_evidence(self, attachment_id, name=None, evidence_category="photo"):
        """REQ-34.4: register evidence against the checksummed repository."""
        self.ensure_one()
        attachment = self.env["ir.attachment"].browse(attachment_id).exists()
        if not attachment:
            raise ValidationError("Evidence attachment %s not found." % attachment_id)
        # The digest is taken at ATTACH time, not deferred to a later archive
        # sync: evidence that is only hashed once it reaches Mayan is
        # unverifiable in the window that matters for a dispute.
        payload = base64.b64decode(attachment.datas or b"")
        if not payload:
            raise ValidationError("The evidence file is empty; nothing to digest.")
        document = self.env["fix.document"].create(
            {
                "name": name or attachment.name,
                "company_id": self.company_id.id,
                "operating_unit_id": self.operating_unit_id.id,
                "attachment_id": attachment.id,
                "res_model": "fix.complaint",
                "res_id": self.id,
                "checksum_sha256": hashlib.sha256(payload).hexdigest(),
                "payload_size_bytes": len(payload),
                "description": "Complaint evidence (%s) for %s" % (evidence_category, self.name),
            }
        )
        self.message_post(
            body="Evidence '%s' attached with digest %s."
            % (document.name, document.checksum_sha256 or "pending")
        )
        return document

    # ------------------------------------------------------------------
    # S9 SLA binding (gap-plan M34: "add SLA binding per severity")
    # ------------------------------------------------------------------
    # Which SLA service_type/priority a complaint severity buys. Mapped as
    # data-in-code rather than guessed per call: the severity ladder is M34's
    # and the policy vocabulary is M01's, so the join has to be stated
    # somewhere and this is the one place it is.
    _SEVERITY_PRIORITY = {
        "critical": "emergency",
        "major": "urgent",
        "minor": "normal",
    }

    def _resolve_sla_policy(self):
        """The policy this complaint's severity buys, or an empty recordset.

        A03 audit M34-5: the choice ignored branch and operating unit. An M34
        binding rule (fix.complaint.sla.rule) now decides first, most specific
        scope winning: branch, then operating unit, then severity alone.
        fix.sla.policy itself is estate-wide master data with no scope of its
        own, so the scope lives on the binding, not on the policy. With no
        rule the severity's priority picks the policy, as before.

        Returns empty when nothing matches, which the caller reports rather
        than papering over: inventing a deadline for a severity nobody has
        configured a promise for would be worse than having none.
        """
        self.ensure_one()
        rule = self.env["fix.complaint.sla.rule"].sudo()._match(self)
        if rule:
            return rule.policy_id
        Policy = self.env["fix.sla.policy"]
        priority = self._SEVERITY_PRIORITY.get(self.severity, "normal")
        return Policy.sudo().search(
            [("active", "=", True), ("priority", "=", priority)],
            order="response_hours",
            limit=1,
        )

    def _start_sla_clocks(self, kpis=("first_response", "resolution"), started_at=None):
        """Open the acknowledgement and resolution clocks for this complaint."""
        Instance = self.env.get("fix.sla.kpi.instance")
        if Instance is None:
            return False
        for rec in self:
            policy = rec.sla_policy_id or rec._resolve_sla_policy()
            if not policy:
                continue
            if not rec.sla_policy_id:
                rec._guarded().write({"sla_policy_id": policy.id})
            for kpi in kpis:
                Instance.sudo().start_for(
                    rec, policy, kpi, partner=rec.customer_id or None, started_at=started_at
                )
        return True

    @api.depends("severity", "state")
    def _compute_sla_instances(self):
        Instance = self.env.get("fix.sla.kpi.instance")
        for rec in self:
            if Instance is None or not rec.id:
                rec.sla_instance_ids = [(5, 0, 0)]
                rec.sla_resolution_state = "SLA engine not installed"
                continue
            found = Instance.sudo().search([("res_model", "=", rec._name), ("res_id", "=", rec.id)])
            rec.sla_instance_ids = [(6, 0, found.ids)]
            live = found.filtered(
                lambda i: i.kpi_code == "resolution" and i.state in ("in_progress", "paused")
            )
            if live:
                rec.sla_resolution_state = "%s, due %s" % (
                    live[0].state,
                    live[0].target_at,
                )
            elif found.filtered(lambda i: i.kpi_code == "resolution"):
                finished = found.filtered(lambda i: i.kpi_code == "resolution")
                rec.sla_resolution_state = finished.sorted("id")[-1].state
            elif not rec.sla_policy_id:
                rec.sla_resolution_state = "no SLA policy configured for severity '%s'" % (
                    rec.severity or "?"
                )
            else:
                rec.sla_resolution_state = "not started"

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            # FLAW-34.3 / ISO 10002 Clause 7.3: Immediate formal complaint acknowledgment
            rec._guarded().write({"acknowledged_at": fields.Datetime.now()})
            # S9: the promise starts when the complaint is raised, not when
            # somebody remembers to start a timer.
            rec._start_sla_clocks()
            publish(
                self.env,
                "complaint.acknowledged",
                "fix.complaint",
                rec.id,
                {
                    "complaint_no": rec.name,
                    "customer_id": rec.customer_id.id,
                    "severity": rec.severity,
                    "acknowledged_at": fields.Datetime.to_string(rec.acknowledged_at),
                },
            )
        return records

    def _dofa_void_approval(self, reason: str):
        # The concession flag is the same approval in this model's words;
        # it cannot outlive the DOFA stamp it was set from.
        self.filtered("concession_approved")._guarded().write(
            {"concession_approved": False, "concession_approver_id": False}
        )
        return super()._dofa_void_approval(reason)

    def action_approve_concession(self):
        """REQ-34.3: real DOFA authority over a service-recovery concession.

        This used to check only that the amount was positive and then stamp
        self.env.user, so a BDT 500,000 settlement was self-approved by the
        officer who raised it (audit 2026-10-31). fix.dofa.mixin now derives
        the tier from the amount, requires the approver to hold that tier's
        group, and refuses self-approval.
        """
        for complaint in self:
            if complaint.concession_amount <= 0:
                raise ValidationError("No concession amount specified to approve.")
            complaint.action_dofa_approve()
            complaint._guarded().write(
                {
                    "concession_approved": True,
                    "concession_approver_id": self.env.user.id,
                }
            )
            # A03 audit M34-9: the hand-off Finance and M10 can act on even
            # before the complaint closes. The money document itself is
            # created at closure (_settle_concession), once the customer has
            # accepted the remedy it pays for.
            publish(
                self.env,
                "complaint.concession_approved",
                "fix.complaint",
                complaint.id,
                {
                    "complaint": complaint.name,
                    "partner_id": complaint.customer_id.id,
                    "concession_type": complaint.concession_type,
                    "amount": complaint.concession_amount,
                    "currency": complaint.currency_id.name or "BDT",
                    "tier": complaint.dofa_approved_tier or None,
                    "approved_by": self.env.user.id,
                },
            )

    def action_investigate(self):
        """ISO 10002 cl. 7.5-7.6: assessment opens the investigation.

        Without it nothing could enter 'investigating', so the NCR step below
        was reachable only by writing the state field directly — which is now
        refused. The investigation follows the initial assessment (owner and
        severity, action_assess): an investigation nobody owns is the
        unassigned complaint the audit found (M34-6)."""
        for complaint in self:
            if complaint.state != "assessed":
                raise UserError(
                    "Assess complaint %s first (confirm its owner and severity); only an "
                    "assessed complaint moves into investigation." % complaint.name
                )
            if not complaint.owner_id:
                raise UserError("Complaint %s has no owner to investigate it." % complaint.name)
            complaint._guarded().write({"state": "investigating"})
            complaint.message_post(body="Investigation opened by %s." % self.env.user.name)

    def action_raise_ncr(self):
        """Journey 14: complaint -> NCR. Until M23 (W5), the stub records
        the linkage intent with an expiry — the GV-005 registration."""
        for complaint in self:
            if complaint.state != "investigating":
                raise UserError("Investigate before raising the NCR")
            complaint._guarded().write(
                {
                    "state": "ncr_raised",
                    "ncr_stub_ref": "NCR-STUB/%s" % complaint.id,
                }
            )
            publish(
                self.env,
                "complaint.ncr_raised",
                "fix.complaint",
                complaint.id,
                {"complaint": complaint.name, "stub": True},
            )

    def _capa_closure_denial(self) -> str:
        """'' when the complaint's CAPA evidence allows a CRITICAL closure.

        With M23 installed (cd_qms_process extends this model with capa_id;
        no dependency is declared - M23 depends on this module), the linked
        CAPA must be VERIFIED or CLOSED. Without M23 the quality owner must
        enter the CAPA reference."""
        self.ensure_one()
        if "capa_id" in self._fields:
            capa = self["capa_id"]
            if not capa:
                return "no CAPA is linked"
            if capa.state not in ("verified", "closed"):
                return "linked CAPA is '%s', not verified" % capa.state
            return ""
        return "" if (self.capa_stub_ref or "").strip() else "no CAPA reference is entered"

    def _rca_denial(self) -> str:
        """'' when the 5-Why evidence allows this complaint to proceed.

        FLAW-34.1: a major or critical complaint needs a written 5-Why, and
        (A03 audit, "five_why_verified gates nothing") that 5-Why verified by
        someone other than its author (action_verify_root_cause)."""
        self.ensure_one()
        if self.severity not in ("major", "critical"):
            return ""
        if not self.root_cause_5why or len(self.root_cause_5why.strip()) < 20:
            return (
                "ISO 10002 compliance violation: 5-Why Root Cause Analysis is mandatory "
                "before closing Major or Critical complaints (FLAW-34.1)."
            )
        if not self.five_why_verified:
            return (
                "The 5-Why Root Cause Analysis of this %s complaint is written but not "
                "verified. A second person verifies it (Verify Root Cause) before the "
                "complaint is answered or closed." % self.severity
            )
        return ""

    def _concession_denial(self):
        """Raise unless any concession on the complaint is approved for its amount."""
        self.ensure_one()
        # REQ-34.3: the concession must carry an approval that still covers
        # its amount. _dofa_assert_approved also catches the case where the
        # amount was raised after a lower-tier sign-off.
        if self.concession_amount > 0:
            if not self.concession_approved:
                raise ValidationError(
                    f"Recovery concession of BDT {self.concession_amount} "
                    f"({self.concession_type}) requires formal corporate DOFA "
                    f"approval before closure (REQ-34.3)."
                )
            self._dofa_assert_approved("Service recovery concession")

    def action_close(self, resolution: str):
        """ISO 10002 cl. 7.9: close a complaint the customer has accepted.

        The evidence checks run first so a refusal names what is missing; the
        lifecycle position runs last. A03 audit M34-1/M34-3: closing used to
        work from 'new', skipping assessment, investigation and the
        customer's answer."""
        for complaint in self:
            if complaint.state in ("closed", "rejected"):
                raise UserError("Complaint %s is already %s" % (complaint.name, complaint.state))
            if not (resolution or "").strip():
                raise UserError("Record the resolution before closing the complaint")
            denial = complaint._rca_denial()
            if denial:
                raise ValidationError(denial)
            complaint._concession_denial()
            if complaint.severity == "critical":
                denial = complaint._capa_closure_denial()
                if denial:
                    raise UserError(
                        "A CRITICAL complaint closes only through CAPA verification "
                        "(journey 14) — no shortcut: %s" % denial
                    )
            complaint._closure_position_check()
            complaint._guarded().write(
                {"state": "closed", "resolution": resolution, "closed_at": fields.Datetime.now()}
            )
            complaint._stop_sla_clocks("complaint closed")
            complaint._settle_concession()
            complaint._trigger_post_closure_survey()

    def _trigger_post_closure_survey(self):
        """REQ-34.6: an independent satisfaction check after closure, to verify
        the customer agrees the matter is actually resolved.

        Dispatch goes out as an event, the way complaint.acknowledged does
        (AS-08): the notification engine owns the channel, and fix.survey is
        the post-SERVICE instrument — one per service order — so it is not the
        vehicle for a post-COMPLAINT check.
        """
        for complaint in self:
            if complaint.post_closure_survey_sent_at:
                continue
            complaint._guarded().write({"post_closure_survey_sent_at": fields.Datetime.now()})
            publish(
                self.env,
                "complaint.post_closure_survey_dispatched",
                "fix.complaint",
                complaint.id,
                {
                    "complaint": complaint.name,
                    "partner_id": complaint.customer_id.id,
                    "severity": complaint.severity,
                    "channel": "sms",
                    # A reopened complaint is surveyed again after its next
                    # closure; the cycle tells the consumer which one this is.
                    "cycle": complaint.reopen_count,
                },
            )

    @api.model
    def cron_escalate_stale_complaints(self):
        """REQ-34.5: a complaint unresolved 72 hours after intake escalates to
        the COO and flags its branch as a quality warning.

        A03 audit M34-6: the escalation flagged and posted chatter but
        assigned and notified nobody. It now names an escalation owner
        (_escalation_owner: a configured user, else the Tier 4 holders), gives
        them a to-do on the complaint, and the complaint.escalated_72h
        consumer opens their M63 exception task."""
        cutoff = fields.Datetime.now() - timedelta(hours=72)
        stale = self.search(
            [
                ("state", "not in", ("closed", "rejected")),
                ("create_date", "<=", cutoff),
                ("escalated_at", "=", False),
            ]
        )
        for complaint in stale:
            owner = complaint._escalation_owner()
            complaint._guarded().write(
                {
                    "escalated_at": fields.Datetime.now(),
                    "quality_warning": True,
                    "escalation_owner_id": owner.id or False,
                }
            )
            if owner:
                complaint._notify_user(
                    owner,
                    "Escalated complaint: %s" % complaint.name,
                    "Unresolved 72 hours after intake (REQ-34.5). You are the escalation "
                    "owner; the current owner is %s." % (complaint.owner_id.name or "nobody"),
                )
                body = (
                    "Unresolved 72 hours after intake — escalated to %s and the "
                    "operating unit flagged Quality Warning (REQ-34.5)." % owner.name
                )
            else:
                body = (
                    "Unresolved 72 hours after intake and the operating unit flagged "
                    "Quality Warning (REQ-34.5). NOBODY could be notified: no user holds "
                    "DOFA Tier 4 and the parameter cd_cx_feedback.escalation_user is not "
                    "set. Appoint the escalation owner."
                )
            complaint.message_post(body=body)
            publish(
                self.env,
                "complaint.escalated_72h",
                "fix.complaint",
                complaint.id,
                {
                    "complaint": complaint.name,
                    "severity": complaint.severity,
                    "operating_unit_id": complaint.operating_unit_id.id,
                    "hours_open": 72,
                    "escalation_owner_id": owner.id or None,
                    "owner_id": complaint.owner_id.id or None,
                },
            )
        return len(stale)


class FixSupplierScorecard(models.Model):
    """M42 (T05/T06): the vendor scorecard — computed FROM consumed M16
    events (goods.received, po.issued), the asymmetric interface. M42 never
    reads M16 tables and M16 never knows M42 exists."""

    _name = "fix.supplier.scorecard"
    _description = "Supplier Scorecard"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    # Odoo 19 dropped the legacy constraint tuple list;
    # models.Constraint attributes (migrated by tooling/scripts/migrate-sql-constraints.py)
    _vendor_period_unique = models.Constraint(
        "UNIQUE (vendor_id, period)", "One scorecard per vendor and period"
    )

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", required=True, index=True)
    vendor_id = fields.Many2one(
        "res.partner", string="Vendor", required=True, index=True, ondelete="cascade"
    )
    period = fields.Char(required=True, size=7, index=True, help="YYYY-MM")
    po_count = fields.Integer(default=0, readonly=True)
    lines_on_time = fields.Integer(default=0, readonly=True)
    lines_late = fields.Integer(default=0, readonly=True)
    on_time_pct = fields.Float(compute="_compute_scores", store=True)
    rejection_count = fields.Integer(
        default=0, readonly=True, help="From the M52 matcher's blocked invoices"
    )
    score = fields.Float(
        compute="_compute_scores",
        store=True,
        help="0-100: 60% on-time, 40% quality (100 - rejections)",
    )

    @api.depends("lines_on_time", "lines_late", "rejection_count", "po_count")
    def _compute_scores(self):
        for card in self:
            total_lines = card.lines_on_time + card.lines_late
            on_time = (100.0 * card.lines_on_time / total_lines) if total_lines else 100.0
            quality = max(0.0, 100.0 - 10.0 * card.rejection_count)
            card.on_time_pct = round(on_time, 2)
            card.score = round(0.6 * on_time + 0.4 * quality, 2)

    @api.model
    def consume_goods_received(self, event: dict) -> None:
        """Pair 10's consuming half: one goods.received line event scores
        on-time vs late (receipt within the PO's scheduled window)."""
        payload = event.get("payload", {})
        vendor = payload.get("vendor_id")
        if not vendor:
            return
        period = str(payload.get("po_date", fields.Date.today()))[:7]
        card = self.search([("vendor_id", "=", vendor), ("period", "=", period)])
        if not card:
            # AS-03: the event's operating unit, else the company's first one
            # (the field is required - the former create omitted it)
            ou_id = payload.get("operating_unit_id") or (
                self.env["operating.unit"]
                .search([("company_id", "=", self.env.company.id)], limit=1)
                .id
            )
            card = self.create(
                {"vendor_id": vendor, "period": period, "po_count": 0, "operating_unit_id": ou_id}
            )
        late = bool(payload.get("late", False))
        if late:
            card.lines_late += 1
        else:
            card.lines_on_time += 1

    @api.model
    def publish_all_scorecards(self):
        """T06: scorecards publish through events — the P05 vendor portal
        reads them via the API, never from M42 tables."""
        for card in self.search([]):
            publish(
                self.env,
                "supplier.scorecard",
                "fix.supplier.scorecard",
                card.id,
                {
                    "vendor_id": card.vendor_id.id,
                    "period": card.period,
                    "score": card.score,
                    "on_time_pct": card.on_time_pct,
                },
            )
