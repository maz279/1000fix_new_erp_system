# M07 sales sequences and playbooks — S10 applied to the seller's cadence.
#
# D365 calls this Sales acceleration: a SEQUENCE is an ordered cadence of
# touches (call, e-mail, visit, task) attached to a lead or opportunity, and a
# PLAYBOOK is the same machinery applied as a deal template. The gap plan
# records both as missing, and records that they share the journey engine's
# pattern rather than needing a second one. They share the actual engine:
# fix.step.runtime.mixin in cd_entity_config, the same code M35 journeys run.
#
# The interesting difference, and the reason sharing the engine was worth
# doing rather than just claiming: a marketing journey step SENDS and moves
# on, while a sales cadence step mostly ASKS A HUMAN TO DO SOMETHING and must
# then wait for them. So most steps here return 'wait' repeatedly until the
# seller closes the activity, and the engine handles that without knowing
# anything about sales. A step model that could only send would have forced a
# second engine.
#
# First-touch SLA: the gap plan asks for "sequence-enforced cadence SLA
# (first touch <= 2h)". That is on the enrolment, measured from enrolment to
# the first completed touch, and breaches are published rather than merely
# coloured in a view.
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish  # FF-28

STEP_TYPES = [
    ("call", "Call the contact"),
    ("email", "Send an e-mail"),
    ("visit", "Site visit"),
    ("task", "Other task"),
    ("wait", "Wait"),
    ("branch", "Branch on the deal state"),
    ("exit", "End the sequence"),
]

# The step types that need a person. These create an activity and the member
# sits on the step until that activity is closed.
MANUAL_STEP_TYPES = {"call", "visit", "task"}

# How long a manual step waits between checks for completion. Minutes, not
# seconds: a seller is not going to close an activity inside a minute, and
# polling faster only burns cron time.
MANUAL_RECHECK_MINUTES = 30


class FixCrmSequence(models.Model):
    """A cadence of touches, or a playbook. One engine, one discriminator."""

    _name = "fix.crm.sequence"
    _description = "Sales Sequence / Playbook"
    _inherit = ["mail.thread", "fix.step.runtime.mixin"]
    _order = "name"

    # --- the S10 engine contract ---
    _runtime_member_model = "fix.crm.sequence.enrolment"
    _runtime_member_flow_field = "sequence_id"

    name = fields.Char(required=True)
    code = fields.Char(required=True, index=True)
    sequence_kind = fields.Selection(
        [
            ("cadence", "Cadence (sequence of touches)"),
            ("playbook", "Playbook (deal template)"),
        ],
        required=True,
        default="cadence",
        help="D365 ships these as two features built on one mechanism. So do "
        "we: the engine treats them identically and the discriminator exists "
        "for reporting and for the seller's own language.",
    )
    applies_to = fields.Selection(
        [("lead", "Leads"), ("opportunity", "Opportunities"), ("both", "Both")],
        required=True,
        default="both",
    )
    state = fields.Selection(
        [("draft", "Draft"), ("active", "Active"), ("paused", "Paused")],
        required=True,
        default="draft",
        tracking=True,
    )
    first_touch_sla_hours = fields.Float(
        string="First-Touch SLA (hours)",
        default=2.0,
        help="The cadence promise: how soon after enrolment the first touch "
        "must be completed. 0 disables the measurement.",
    )
    step_ids = fields.One2many("fix.crm.sequence.step", "sequence_id", string="Steps", copy=True)
    enrolment_ids = fields.One2many(
        "fix.crm.sequence.enrolment", "sequence_id", string="Enrolments"
    )
    step_count = fields.Integer(compute="_compute_counts")
    active_enrolments = fields.Integer(compute="_compute_counts")
    sla_breaches = fields.Integer(compute="_compute_counts")
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )

    _code_unique = models.Constraint("UNIQUE (code)", "Each sequence code exists once.")

    @api.depends("step_ids", "enrolment_ids.state", "enrolment_ids.first_touch_breached")
    def _compute_counts(self):
        for rec in self:
            rec.step_count = len(rec.step_ids)
            rec.active_enrolments = len(rec.enrolment_ids.filtered(lambda e: e.state == "active"))
            rec.sla_breaches = len(rec.enrolment_ids.filtered("first_touch_breached"))

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------
    def action_activate(self):
        for rec in self:
            if not rec.step_ids:
                raise UserError(
                    "A sequence with no steps has nothing to ask of a seller. "
                    "Add at least one step."
                )
            rec.state = "active"
        return True

    def action_pause(self):
        for rec in self:
            rec.state = "paused"
        return True

    def enrol(self, leads, owner=None):
        """Put leads or opportunities on this cadence. Idempotent per lead."""
        self.ensure_one()
        if self.state != "active":
            raise UserError(
                "Sequence '%s' is %s. Activate it before enrolling anybody."
                % (self.name, self.state)
            )
        Enrolment = self.env["fix.crm.sequence.enrolment"].sudo()
        first = self._runtime_first_step()
        created = Enrolment.browse()
        for lead in leads:
            key = "%d:%d" % (self.id, lead.id)
            if Enrolment.search_count([("enrol_key", "=", key)]):
                continue
            owner_rec = owner or lead.user_id or self.env.user
            due = (
                fields.Datetime.add(fields.Datetime.now(), hours=self.first_touch_sla_hours)
                if self.first_touch_sla_hours
                else False
            )
            created |= Enrolment.create(
                {
                    "sequence_id": self.id,
                    "lead_id": lead.id,
                    "owner_id": owner_rec.id,
                    "current_step_id": first.id if first else False,
                    "enrol_key": key,
                    "first_touch_due_at": due,
                    "next_action_at": fields.Datetime.now(),
                    "company_id": self.company_id.id,
                }
            )
        if created:
            publish(
                self.env,
                "sequence.enrolled",
                "fix.crm.sequence",
                self.id,
                {
                    "sequence": self.name,
                    "kind": self.sequence_kind,
                    "enrolled": len(created),
                    "lead_ids": created.mapped("lead_id").ids,
                },
            )
        return created

    # ------------------------------------------------------------------
    # The S10 contract
    # ------------------------------------------------------------------
    def _runtime_ordered_steps(self):
        self.ensure_one()
        return self.step_ids.filtered("active").sorted(lambda s: (s.sequence, s.id))

    def _runtime_current_step(self, member):
        return member.current_step_id

    def _runtime_set_step(self, member, step):
        member.sudo().write({"current_step_id": step.id if step else False})

    def _runtime_member_still_eligible(self, member):
        """A cadence stops when the deal stops being a deal.

        Chasing a won deal wastes the seller's day, and chasing a lost one
        annoys the customer. Both are ended here rather than by each step.
        """
        self.ensure_one()
        if self.state != "active":
            return False, "Sequence is %s." % self.state
        lead = member.lead_id
        if not lead.exists():
            return False, "The lead was deleted."
        if lead.active is False:
            return False, "The lead was archived."
        if lead.stage_id and lead.stage_id.is_won:
            return False, "Deal is won — the cadence has done its job."
        if lead.probability == 0 and lead.active is False:
            return False, "Deal is lost."
        return True, ""

    def _runtime_execute_step(self, member, step):
        self.ensure_one()
        if step.step_type in MANUAL_STEP_TYPES:
            return self._step_manual(member, step)
        handler = getattr(self, "_step_%s" % step.step_type, None)
        if handler is None:
            return {"action": "fail", "reason": "Step type %r has no handler." % step.step_type}
        return handler(member, step)

    # --- step handlers -------------------------------------------------
    def _step_manual(self, member, step):
        """Ask the owner to do something, then wait until they have.

        The activity is created once per (enrolment, step) and found again on
        every later pass, so a cron that runs twice does not raise two calls
        on the seller's list.
        """
        Activity = self.env["mail.activity"].sudo()
        lead_model_id = self.env["ir.model"]._get_id("crm.lead")
        summary = "%s · %s" % (self.name, step.name)
        existing = Activity.search(
            [
                ("res_model_id", "=", lead_model_id),
                ("res_id", "=", member.lead_id.id),
                ("user_id", "=", member.owner_id.id),
                ("summary", "=", summary),
            ],
            limit=1,
        )
        if not existing:
            # mail.activity rows disappear when marked done, so an absent
            # activity after the step has already asked for one means the
            # seller completed it.
            if member.last_manual_step_id.id == step.id:
                member.sudo().write({"last_manual_step_id": False})
                member._register_touch(step)
                return {"action": "next"}
            Activity.create(
                {
                    "res_model_id": lead_model_id,
                    "res_id": member.lead_id.id,
                    "user_id": member.owner_id.id,
                    "summary": summary,
                    "note": step.instructions or "",
                    "date_deadline": fields.Date.add(
                        fields.Date.context_today(self),
                        days=max(0, step.due_in_days or 0),
                    ),
                }
            )
            member.sudo().write({"last_manual_step_id": step.id})
            return {"action": "wait", "wait_minutes": MANUAL_RECHECK_MINUTES}
        return {"action": "wait", "wait_minutes": MANUAL_RECHECK_MINUTES}

    def _step_wait(self, member, step):
        return {"action": "next"}

    def _step_exit(self, member, step):
        return {"action": "exit", "reason": step.instructions or "Sequence step ended the cadence."}

    def _step_email(self, member, step):
        """Send through S1, so a cadence e-mail is logged and costed like any
        other outbound message rather than vanishing into a mail server."""
        partner = member.lead_id.partner_id or member.lead_id.linked_partner_id
        address = member.lead_id.email_from or (partner.email if partner else "")
        if not address:
            return {
                "action": "next",
                "reason": "No e-mail address on the lead; step skipped.",
            }
        delivery = self.env["fix.notif.delivery"].queue(
            channel="email",
            purpose="service_updates",
            partner=partner or None,
            to_address=address,
            subject=step.email_subject or self.name,
            body=step.email_body or step.instructions or self.name,
            template_values={
                "name": (partner.name if partner else member.lead_id.contact_name) or "",
                "lead": member.lead_id.name or "",
            },
            # A seller following up a deal the prospect asked about is
            # contract-preparatory contact, not a marketing blast. Declared
            # and recorded on the row so it can be reviewed as a class.
            lawful_basis="contract",
            source_model="fix.crm.sequence.enrolment",
            source_id=member.id,
            dedup_key="sequence:%d:step:%d:enrol:%d" % (self.id, step.id, member.id),
            company=self.company_id,
        )
        member.sudo().write({"delivery_ids": [(4, delivery.id)]})
        member._register_touch(step)
        return {"action": "next"}

    def _step_branch(self, member, step):
        result = step._evaluate(member)
        target = step.true_step_id if result else step.false_step_id
        if not target:
            return {
                "action": "complete",
                "reason": "Branch '%s' took the %s arm, which has no next step."
                % (step.name, "true" if result else "false"),
            }
        return {"action": "goto", "next_step": target}

    # ------------------------------------------------------------------
    # Crons
    # ------------------------------------------------------------------
    @api.model
    def cron_advance_sequences(self, limit=500):
        active = self.sudo().search([("state", "=", "active")])
        if not active:
            return {"considered": 0}
        return active._runtime_advance_due(limit=limit)

    @api.model
    def cron_flag_first_touch_breaches(self):
        """Publish the cadence-SLA breaches rather than only displaying them.

        A first-touch promise nobody is told about being broken is not a
        promise. The event goes to the same outbox every other escalation
        uses, so the sales manager's alerting does not need a special case.
        """
        Enrolment = self.env["fix.crm.sequence.enrolment"].sudo()
        due = Enrolment.search(
            [
                ("state", "=", "active"),
                ("first_touch_at", "=", False),
                ("first_touch_breached", "=", False),
                ("first_touch_due_at", "!=", False),
                ("first_touch_due_at", "<=", fields.Datetime.now()),
            ]
        )
        for enrolment in due:
            enrolment.write({"first_touch_breached": True})
            publish(
                self.env,
                "sequence.first_touch_breached",
                "fix.crm.sequence.enrolment",
                enrolment.id,
                {
                    "sequence": enrolment.sequence_id.name,
                    "lead_id": enrolment.lead_id.id,
                    "lead": enrolment.lead_id.name,
                    "owner": enrolment.owner_id.name,
                    "due_at": str(enrolment.first_touch_due_at),
                    "sla_hours": enrolment.sequence_id.first_touch_sla_hours,
                },
            )
        return len(due)


class FixCrmSequenceStep(models.Model):
    """One touch in a cadence."""

    _name = "fix.crm.sequence.step"
    _description = "Sales Sequence Step"
    _order = "sequence_id, sequence, id"

    # Both of these defaulted to the label "Sequence" (Odoo derives it from
    # the field name, and sequence_id drops the _id), so a form drew two
    # different fields under one heading and the loader warned about it. Name
    # them for what they are: the playbook, and the position within it.
    sequence_id = fields.Many2one(
        "fix.crm.sequence",
        string="Playbook",
        required=True,
        ondelete="cascade",
        index=True,
    )
    sequence = fields.Integer(string="Step Order", required=True, default=10)
    name = fields.Char(required=True)
    step_type = fields.Selection(STEP_TYPES, required=True, default="call")
    active = fields.Boolean(default=True)
    wait_minutes = fields.Integer(
        string="Wait Before This Step (min)",
        default=0,
        help="Applied when the enrolment ENTERS this step.",
    )
    due_in_days = fields.Integer(
        string="Activity Due In (days)",
        default=0,
        help="Deadline on the activity raised for a manual step.",
    )
    instructions = fields.Text(
        help="What the seller should actually do or say. The point of a "
        "cadence is that this is written down once."
    )
    email_subject = fields.Char()
    email_body = fields.Text()
    # --- branch ---
    condition_kind = fields.Selection(
        [
            ("always", "Always true"),
            ("has_contact", "Lead has a contact e-mail or phone"),
            ("is_opportunity", "Lead has been qualified to an opportunity"),
            ("criteria_confirmed", "Qualification criteria confirmed"),
            ("contract_verified", "Contract verified"),
        ],
        default="always",
    )
    true_step_id = fields.Many2one(
        "fix.crm.sequence.step", string="If True, Go To", ondelete="set null"
    )
    false_step_id = fields.Many2one(
        "fix.crm.sequence.step", string="If False, Go To", ondelete="set null"
    )

    _sequence_unique = models.Constraint(
        "UNIQUE (sequence_id, sequence)",
        "Two steps of one sequence cannot share a sequence number.",
    )

    @api.constrains("step_type", "email_subject", "email_body", "instructions")
    def _check_step_is_actionable(self):
        for rec in self:
            if rec.step_type in MANUAL_STEP_TYPES and not (rec.instructions or "").strip():
                raise ValidationError(
                    "Step '%s' asks a seller to act but says nothing about what "
                    "to do. Write the instruction — that is what a cadence is "
                    "for." % rec.name
                )
            if rec.step_type == "email" and not (
                (rec.email_body or "").strip() or (rec.instructions or "").strip()
            ):
                raise ValidationError("E-mail step '%s' has no body." % rec.name)

    @api.constrains("true_step_id", "false_step_id", "sequence_id")
    def _check_branch_arms_are_local(self):
        for rec in self:
            for arm in (rec.true_step_id, rec.false_step_id):
                if arm and arm.sequence_id != rec.sequence_id:
                    raise ValidationError(
                        "Branch step '%s' points at a step of another sequence." % rec.name
                    )

    def _evaluate(self, member):
        """Bounded conditions over the deal. No expression evaluation."""
        self.ensure_one()
        lead = member.lead_id
        kind = self.condition_kind or "always"
        if kind == "always":
            return True
        if kind == "has_contact":
            # getattr: crm.lead carries `mobile` in some Odoo releases and
            # not others, and a cadence must not crash on an upgrade that
            # drops it.
            return bool(lead.email_from or lead.phone or getattr(lead, "mobile", False))
        if kind == "is_opportunity":
            return lead.type == "opportunity"
        if kind == "criteria_confirmed":
            return bool(lead.criteria_confirmed)
        if kind == "contract_verified":
            return bool(lead.contract_verified)
        return False


class FixCrmSequenceEnrolment(models.Model):
    """One lead's progress through one cadence."""

    _name = "fix.crm.sequence.enrolment"
    _description = "Sales Sequence Enrolment"
    _inherit = ["fix.step.member.mixin", "mail.thread"]
    _order = "next_action_at, id"
    _rec_name = "lead_id"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    sequence_id = fields.Many2one("fix.crm.sequence", required=True, ondelete="cascade", index=True)
    lead_id = fields.Many2one("crm.lead", required=True, ondelete="cascade", index=True)
    owner_id = fields.Many2one("res.users", string="Owner", required=True, index=True)
    current_step_id = fields.Many2one(
        "fix.crm.sequence.step", string="Current Step", ondelete="set null"
    )
    last_manual_step_id = fields.Many2one(
        "fix.crm.sequence.step",
        string="Awaiting Completion Of",
        help="The manual step whose activity is outstanding. Set when the "
        "activity is raised and cleared when it is found closed, which is how "
        "the engine tells 'not asked yet' from 'asked and done'.",
    )
    enrol_key = fields.Char(required=True, index=True)
    first_touch_due_at = fields.Datetime(string="First Touch Due")
    first_touch_at = fields.Datetime(string="First Touch Completed", readonly=True)
    first_touch_breached = fields.Boolean(readonly=True, index=True)
    touches_completed = fields.Integer(default=0, readonly=True)
    delivery_ids = fields.Many2many("fix.notif.delivery", string="Messages Sent", readonly=True)

    _enrol_key_unique = models.Constraint(
        "UNIQUE (enrol_key)", "This lead is already enrolled in this sequence."
    )

    def _register_touch(self, step):
        """Record that a touch actually happened, and stop the SLA clock."""
        self.ensure_one()
        vals = {"touches_completed": self.touches_completed + 1}
        if not self.first_touch_at:
            vals["first_touch_at"] = fields.Datetime.now()
        self.sudo().write(vals)
        return True
