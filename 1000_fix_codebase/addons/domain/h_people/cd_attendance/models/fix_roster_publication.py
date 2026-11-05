# fix_roster_publication — M55 BRU-WFM-12 / FR-WFM-041/042: the roster lifecycle.
#
# A09 audit M55-10: roster slots were plain rows, with no draft, approval,
# publication or change control, so a supervisor's edit reached the employee
# and dispatch the moment it was typed. Now:
#
#   fix.roster.slot             draft --(publication approved)--> published.
#                               A published slot's employee, day, shift and
#                               branch change only through an approved change
#                               request; an employee reads published slots only.
#   fix.roster.publication      the planner submits the draft slots of a period;
#                               someone other than the planner (and other than
#                               any rostered employee) approves through the M63
#                               engine (fix.people.approval.mixin).
#   fix.roster.change.request   a change or removal of a published slot, routed
#                               the same way.
#
# BLA s.109: when a woman withdraws her night-work consent, the night slots
# already rostered for her from today on are re-checked: a draft slot is
# removed, a published one is flagged (dispatch refuses it) and a routed
# removal request is raised.
from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError

from .fix_attendance import SUPERVISOR_GROUP

SLOT_TERMS = ("employee_id", "date", "shift_id", "branch_id", "company_id")


class ResCompanyRoster(models.Model):
    _inherit = "res.company"

    # A09 decision: FR-WFM-041 wants a "defined minimum notice" that no source states
    fix_roster_notice_days = fields.Integer(
        string="Roster Publication Notice (days)",
        default=0,
        help="A roster is published at least this many days before its first slot "
        "(FR-WFM-041). 0 = no minimum notice (not ruled; A09 decision).",
    )
    fix_roster_dispatch_published_only = fields.Boolean(
        string="Dispatch Reads the Published Roster Only",
        default=False,
        help="When set, M02 dispatch treats a technician as rostered only on a PUBLISHED "
        "slot. Off keeps today's behaviour (any slot counts) until the business decides.",
    )


class FixRosterSlotPublication(models.Model):
    _inherit = "fix.roster.slot"

    # no field default on purpose: slots that existed before publication are
    # published by the upgrade hook (state IS NULL), new ones start in draft
    state = fields.Selection(
        [("draft", "Draft"), ("published", "Published")],
        readonly=True,
        index=True,
        tracking=True,
        copy=False,
    )
    publication_id = fields.Many2one(
        "fix.roster.publication", readonly=True, index=True, copy=False, ondelete="set null"
    )
    published_at = fields.Datetime(readonly=True, copy=False)
    night_consent_flag = fields.Boolean(
        string="Night-Work Consent Withdrawn",
        readonly=True,
        copy=False,
        help="BLA s.109: she withdrew her consent after this night slot was published; it "
        "is not dispatched and its removal is requested.",
    )
    change_request_ids = fields.One2many(
        "fix.roster.change.request", "slot_id", string="Change Requests", readonly=True
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "publication_id",
            "published_at",
            "night_consent_flag",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and (self.state == "published" or self._fix_in_live_publication()):
            locked |= set(SLOT_TERMS)
        return locked

    def _fix_in_live_publication(self):
        self.ensure_one()
        return bool(self.publication_id and self.publication_id.state == "submitted")

    @api.model_create_multi
    def create(self, vals_list):
        slots = super().create(vals_list)
        slots.filtered(lambda s: not s.state)._guarded().write({"state": "draft"})
        return slots

    def write(self, vals):
        if self and not self._fix_guard_open():
            terms = set(SLOT_TERMS) & set(vals)
            if terms:
                for slot in self:
                    if not [n for n in terms if slot._fix_guard_differs(n, vals[n], slot[n])]:
                        continue
                    if slot.state == "published":
                        raise UserError(
                            "%s is published: a change goes through a roster change request "
                            "(BRU-WFM-12)." % slot.display_label
                        )
                    if slot._fix_in_live_publication():
                        raise UserError(
                            "%s is awaiting publication approval (%s): recall the publication "
                            "to change it." % (slot.display_label, slot.publication_id.name)
                        )
        return super().write(vals)

    def unlink(self):
        if not self._fix_guard_open():
            for slot in self:
                if slot.state == "published":
                    raise UserError(
                        "%s is published: its removal goes through a roster change request."
                        % slot.display_label
                    )
                if slot._fix_in_live_publication():
                    raise UserError(
                        "%s is awaiting publication approval: recall the publication first."
                        % slot.display_label
                    )
        return super().unlink()

    def action_ask_change(self, reason=None):
        """FR-WFM-042/043: the rostered employee asks for a change to a
        published slot. A DRAFT change request is opened for the supervisors,
        who say what it changes to and submit it; the employee never decides."""
        if not (reason or "").strip():
            raise UserError("Say what you need changed, and why.")
        CR = self.env["fix.roster.change.request"]
        out = CR
        for slot in self:
            if slot.sudo().employee_id.user_id != self.env.user:
                raise AccessError("You ask for a change of your own roster slots only.")
            if slot.state != "published":
                raise UserError("%s is not published yet." % slot.display_label)
            # RAP X-02: the employee holds no write on change requests; the
            # draft is opened in their name as superuser
            out |= CR.sudo().create(
                {"slot_id": slot.id, "kind": "change", "reason": reason.strip()}
            )
        return {"change_request_ids": out.ids}

    @api.model
    def _fix_publish_legacy_slots(self):
        """Data hook (idempotent): slots that existed before the publication
        lifecycle are the roster people already work to - published."""
        legacy = self.sudo().search([("state", "=", False)])
        if legacy:
            legacy._guarded().write({"state": "published", "published_at": fields.Datetime.now()})
        return len(legacy)

    # ---- BLA s.109: a withdrawn night-work consent ---------------------------
    def _fix_recheck_night_consent(self, employee, date_from, date_to, user):
        """Night slots of `employee` in [date_from, date_to] from today on that
        no remaining consent covers: drafts removed, published ones flagged and
        their removal requested. Never fails the withdrawal itself."""
        Consent = self.env["fix.night.work.consent"].sudo()
        start = max(date_from, fields.Date.context_today(self))
        slots = self.sudo().search(
            [
                ("employee_id", "=", employee.id),
                ("date", ">=", start),
                ("date", "<=", date_to),
            ]
        )
        removed = flagged = 0
        for slot in slots:
            if not slot.shift_id._fix_covers_night() or Consent._fix_covering(employee, slot.date):
                continue
            if slot.state != "published":
                if slot.publication_id and slot.publication_id.state == "submitted":
                    slot.publication_id._fix_void("a rostered night slot lost its consent")
                slot._guarded().unlink()
                removed += 1
                continue
            slot._guarded().write({"night_consent_flag": True})
            slot.message_post(
                body="Night-work consent withdrawn (BLA s.109): this slot is not dispatched "
                "and its removal is requested."
            )
            flagged += 1
            try:
                with self.env.cr.savepoint():
                    self.env["fix.roster.change.request"].with_user(user).sudo()._fix_raise(
                        slot,
                        "remove",
                        "Night-work consent withdrawn (BLA s.109)",
                    )
            except UserError:
                # nobody can decide it yet: the flag keeps her off the night
                slot.message_post(body="No approver for the removal request: it stays flagged.")
        return removed, flagged


class FixNightWorkConsentWithdrawal(models.Model):
    _inherit = "fix.night.work.consent"

    def action_withdraw(self):
        res = super().action_withdraw()
        Slot = self.env["fix.roster.slot"]
        for rec in self:
            Slot._fix_recheck_night_consent(
                rec.employee_id, rec.date_from, rec.date_to, self.env.user
            )
        return res


class FixRosterPublication(models.Model):
    """The planner's draft slots of a period, published once approved."""

    _name = "fix.roster.publication"
    _description = "Roster Publication"
    _inherit = [
        "mail.thread",
        "fix.people.approval.mixin",
        "fix.people.inbox.decide.mixin",
    ]
    _order = "date_from desc, id desc"

    _approval_domain = "hr_attendance"
    _approval_apply_method = "action_approve"
    _approval_group = SUPERVISOR_GROUP

    name = fields.Char(compute="_compute_name", store=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    branch_id = fields.Many2one("fix.branch", string="Branch")
    date_from = fields.Date(required=True)
    date_to = fields.Date(required=True)
    slot_ids = fields.One2many("fix.roster.slot", "publication_id", string="Slots", readonly=True)
    slot_count = fields.Integer(readonly=True)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("submitted", "Awaiting Approval"),
            ("published", "Published"),
            ("rejected", "Rejected"),
            ("cancelled", "Recalled"),
        ],
        default="draft",
        required=True,
        readonly=True,
        tracking=True,
        index=True,
    )
    planner_id = fields.Many2one("res.users", string="Planned By", readonly=True)
    submitted_at = fields.Datetime(readonly=True)
    decided_by_id = fields.Many2one("res.users", string="Decided By", readonly=True)
    decided_at = fields.Datetime(readonly=True)
    rejection_reason = fields.Text(readonly=True)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "slot_count",
            "planner_id",
            "submitted_at",
            "decided_by_id",
            "decided_at",
            "rejection_reason",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and self.state != "draft":
            locked |= {"company_id", "operating_unit_id", "branch_id", "date_from", "date_to"}
        return locked

    @api.depends("date_from", "date_to", "branch_id")
    def _compute_name(self):
        for rec in self:
            rec.name = "Roster %s to %s%s" % (
                rec.date_from or "",
                rec.date_to or "",
                " (%s)" % rec.branch_id.name if rec.branch_id else "",
            )

    @api.constrains("date_from", "date_to")
    def _check_dates(self):
        for rec in self:
            if rec.date_to < rec.date_from:
                raise ValidationError("A roster period cannot end before it starts.")

    def write(self, vals):
        if (
            self
            and not self._fix_guard_open()
            and {"company_id", "operating_unit_id", "branch_id", "date_from", "date_to"} & set(vals)
            and self.filtered(lambda r: r.state != "draft")
        ):
            raise UserError("A submitted or published roster period is not changed.")
        return super().write(vals)

    # ---- who it is about and who planned it ------------------------------------
    def _approval_subject_employees(self):
        return self.sudo().mapped("slot_ids.employee_id")

    def _approval_preparers(self):
        return self.sudo().mapped("planner_id")

    def _fix_assert_planner(self):
        if not (self.env.su or self.env.user.has_group(SUPERVISOR_GROUP)):
            raise AccessError("Only an Attendance Supervisor plans and submits a roster.")

    def _fix_candidate_slots(self):
        self.ensure_one()
        domain = [
            ("company_id", "=", self.company_id.id),
            ("date", ">=", self.date_from),
            ("date", "<=", self.date_to),
            ("state", "=", "draft"),
            "|",
            ("publication_id", "=", False),
            ("publication_id.state", "in", ("rejected", "cancelled")),
        ]
        if self.operating_unit_id:
            domain.append(("operating_unit_id", "=", self.operating_unit_id.id))
        if self.branch_id:
            domain.append(("branch_id", "=", self.branch_id.id))
        return self.env["fix.roster.slot"].sudo().search(domain)

    def _fix_check_notice(self):
        for rec in self:
            notice = rec.company_id.fix_roster_notice_days
            if not notice:
                continue
            first = min(rec.slot_ids.mapped("date")) if rec.slot_ids else rec.date_from
            if (first - fields.Date.context_today(rec)).days < notice:
                raise UserError(
                    "%s starts on %s: a roster is published at least %d days ahead "
                    "(FR-WFM-041)." % (rec.name, first, notice)
                )

    # ---- transitions ---------------------------------------------------------------
    def action_submit(self):
        self._fix_assert_planner()
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only a draft roster period is submitted.")
            slots = rec._fix_candidate_slots()
            if not slots:
                raise UserError("%s has no draft slots to publish." % rec.name)
            slots._guarded().write({"publication_id": rec.id})
            rec._guarded().write(
                {
                    "state": "submitted",
                    "slot_count": len(slots),
                    "planner_id": self.env.user.id,
                    "submitted_at": fields.Datetime.now(),
                }
            )
            rec._fix_check_notice()
            rec.action_request_approval()
        return True

    def action_approve(self):
        """Applied by the M63 engine in the approver's environment."""
        self._approval_assert_routed()
        self._people_assert_not_conflicted()
        decider = self._people_decider()
        now = fields.Datetime.now()
        for rec in self:
            if rec.state != "submitted":
                raise UserError("Only a roster awaiting approval is published.")
            slots = rec.sudo().slot_ids
            if len(slots) != rec.slot_count or slots.filtered(lambda s: s.state != "draft"):
                raise UserError(
                    "%s changed after it was submitted: recall it and submit it again." % rec.name
                )
            rec._fix_check_notice()
            # the s.100 and s.109 rules are re-checked on what is published
            slots._check_daily_schedule()
            slots._check_women_night_work()
            slots._guarded().write({"state": "published", "published_at": now})
            rec._guarded().write(
                {"state": "published", "decided_by_id": decider.id, "decided_at": now}
            )
            rec.message_post(
                body="Published by %s: %d slots. The rostered employees now see them."
                % (decider.name, len(slots))
            )
        return True

    def _approval_on_rejected(self, comment):
        for rec in self:
            rec._guarded().write(
                {
                    "state": "rejected",
                    "decided_by_id": rec._people_decider().id,
                    "decided_at": fields.Datetime.now(),
                    "rejection_reason": comment or False,
                }
            )

    def action_reject(self, reason=None):
        if not (reason or "").strip():
            raise UserError("State why this roster is rejected.")
        return self.action_inbox_reject(reason=reason)

    def _fix_void(self, reason):
        for rec in self.filtered(lambda r: r.state == "submitted"):
            if rec.approval_state == "pending":
                rec.approval_request_id.sudo()._finish(
                    "voided", "voided", self.env.user, comment=reason, record_state="none"
                )
            rec._guarded().write({"state": "cancelled"})

    def action_cancel(self):
        """The planner recalls a roster awaiting approval (its slots stay draft)."""
        self._fix_assert_planner()
        for rec in self:
            if rec.state != "submitted":
                raise UserError("Only a roster awaiting approval is recalled.")
            rec._fix_void("recalled by %s" % self.env.user.name)
        return True


class FixRosterChangeRequest(models.Model):
    """BRU-WFM-12 / FR-WFM-042: a change to a published slot is approved."""

    _name = "fix.roster.change.request"
    _description = "Roster Change Request"
    _inherit = [
        "mail.thread",
        "fix.people.approval.mixin",
        "fix.people.inbox.decide.mixin",
    ]
    _order = "id desc"

    _approval_domain = "hr_attendance"
    _approval_apply_method = "action_approve"
    _approval_group = SUPERVISOR_GROUP

    name = fields.Char(compute="_compute_name", store=True)
    company_id = fields.Many2one(
        "res.company",
        required=True,
        index=True,
        readonly=True,
        default=lambda self: self.env.company,
    )
    # kept when an approved removal deletes the slot (old_* hold what it was)
    slot_id = fields.Many2one("fix.roster.slot", index=True, ondelete="set null", readonly=True)
    kind = fields.Selection(
        [("change", "Change the Slot"), ("remove", "Remove the Slot")],
        required=True,
        default="change",
    )
    # what the slot was when the request was made (B5: what is decided)
    old_employee_id = fields.Many2one("hr.employee", string="Employee", readonly=True)
    old_date = fields.Date(string="Date", readonly=True)
    old_shift_id = fields.Many2one("fix.shift.template", string="Shift", readonly=True)
    new_employee_id = fields.Many2one("hr.employee", string="New Employee")
    new_date = fields.Date()
    new_shift_id = fields.Many2one("fix.shift.template", string="New Shift")
    new_branch_id = fields.Many2one("fix.branch", string="New Branch")
    reason = fields.Text(required=True)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("submitted", "Awaiting Approval"),
            ("approved", "Applied"),
            ("rejected", "Rejected"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
        required=True,
        readonly=True,
        tracking=True,
        index=True,
    )
    decided_by_id = fields.Many2one("res.users", string="Decided By", readonly=True)
    decided_at = fields.Datetime(readonly=True)
    rejection_reason = fields.Text(readonly=True)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "company_id",
            "old_employee_id",
            "old_date",
            "old_shift_id",
            "decided_by_id",
            "decided_at",
            "rejection_reason",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and self.state != "draft":
            locked |= {
                "kind",
                "new_employee_id",
                "new_date",
                "new_shift_id",
                "new_branch_id",
                "reason",
            }
        return locked

    @api.depends("slot_id", "kind")
    def _compute_name(self):
        for rec in self:
            rec.name = "RCR %s: %s" % (rec.old_employee_id.name or "", rec.old_date or "")

    def _approval_subject_employees(self):
        return self.sudo().mapped("old_employee_id") | self.sudo().mapped("new_employee_id")

    def _fix_assert_may_request(self, slot):
        if self.env.su or self.env.user.has_group(SUPERVISOR_GROUP):
            return
        raise AccessError(
            "A roster change is raised by an Attendance Supervisor; the rostered employee "
            "asks for one from the slot (Ask for a Change)."
        )

    @api.model_create_multi
    def create(self, vals_list):
        Slot = self.env["fix.roster.slot"].sudo()
        for vals in vals_list:
            slot = Slot.browse(vals.get("slot_id")).exists()
            if not slot:
                raise UserError("A roster change request names an existing slot.")
            self._fix_assert_may_request(slot)
            if slot.state != "published":
                raise UserError(
                    "%s is not published: a draft slot is edited directly." % slot.display_label
                )
        recs = super().create(vals_list)
        for rec in recs:
            slot = Slot.browse(rec.slot_id.id)
            rec._guarded().write(
                {
                    "company_id": slot.company_id.id,
                    "old_employee_id": slot.employee_id.id,
                    "old_date": slot.date,
                    "old_shift_id": slot.shift_id.id,
                }
            )
        return recs

    def write(self, vals):
        if self and not self._fix_guard_open():
            if "slot_id" in vals and any(
                r._fix_guard_differs("slot_id", vals["slot_id"], r.slot_id) for r in self
            ):
                raise UserError("A roster change request stays on the slot it was raised for.")
            terms = {"kind", "new_employee_id", "new_date", "new_shift_id", "new_branch_id"}
            if terms & set(vals) and self.filtered(lambda r: r.state != "draft"):
                raise UserError("A submitted roster change is not edited: cancel it and ask again.")
        return super().write(vals)

    @api.model
    def _fix_raise(self, slot, kind, reason, **new):
        req = self.create({"slot_id": slot.id, "kind": kind, "reason": reason, **new})
        req.action_submit()
        return req

    def action_submit(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only a draft roster change is submitted.")
            if rec.kind == "change" and not (
                rec.new_employee_id or rec.new_date or rec.new_shift_id or rec.new_branch_id
            ):
                raise UserError("Say what the slot changes to.")
            if rec.slot_id.sudo().change_request_ids.filtered(
                lambda r, me=rec: r != me and r.state == "submitted"
            ):
                raise UserError(
                    "%s already has a change awaiting approval." % rec.slot_id.display_label
                )
            rec._guarded().write({"state": "submitted"})
            rec.action_request_approval()
        return True

    def action_approve(self):
        """Applied by the M63 engine in the approver's environment."""
        self._approval_assert_routed()
        self._people_assert_not_conflicted()
        decider = self._people_decider()
        for rec in self:
            if rec.state != "submitted":
                raise UserError("Only a roster change awaiting approval is applied.")
            slot = rec.slot_id.sudo()
            if (slot.employee_id, slot.date, slot.shift_id) != (
                rec.old_employee_id,
                rec.old_date,
                rec.old_shift_id,
            ):
                raise UserError("%s changed after this request was made." % slot.display_label)
            rec._guarded().write(
                {
                    "state": "approved",
                    "decided_by_id": decider.id,
                    "decided_at": fields.Datetime.now(),
                }
            )
            if rec.kind == "remove":
                slot.message_post(
                    body="Removed by roster change %s (%s)." % (rec.name, decider.name)
                )
                slot._guarded().unlink()
                continue
            vals = {}
            for src, dst in (
                ("new_employee_id", "employee_id"),
                ("new_date", "date"),
                ("new_shift_id", "shift_id"),
                ("new_branch_id", "branch_id"),
            ):
                if rec[src]:
                    vals[dst] = rec[src].id if hasattr(rec[src], "id") else rec[src]
            # the s.100/s.109 constraints run on the changed slot
            slot._guarded().write({**vals, "night_consent_flag": False})
            slot.message_post(body="Changed by roster change %s (%s)." % (rec.name, decider.name))
        return True

    def _approval_on_rejected(self, comment):
        for rec in self:
            rec._guarded().write(
                {
                    "state": "rejected",
                    "decided_by_id": rec._people_decider().id,
                    "decided_at": fields.Datetime.now(),
                    "rejection_reason": comment or False,
                }
            )

    def action_reject(self, reason=None):
        if not (reason or "").strip():
            raise UserError("State why this roster change is rejected.")
        return self.action_inbox_reject(reason=reason)

    def action_cancel(self):
        for rec in self:
            if rec.state not in ("draft", "submitted"):
                raise UserError("%s is %s and cannot be cancelled." % (rec.name, rec.state))
            if not (
                self.env.su
                or rec.create_uid == self.env.user
                or self.env.user.has_group(SUPERVISOR_GROUP)
            ):
                raise AccessError("Only the requester or a supervisor cancels %s." % rec.name)
            if rec.approval_state == "pending":
                rec.approval_request_id.sudo()._finish(
                    "recalled", "recalled", self.env.user, record_state="none"
                )
            rec.sudo()._guarded().write({"state": "cancelled"})
        return True
