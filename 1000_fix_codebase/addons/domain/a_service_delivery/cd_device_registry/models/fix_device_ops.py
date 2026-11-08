# fix_device_ops — M17: corporate estates, PM plans, condition grading, identity
# resolution, custody events and installed components. The device master,
# warranties, ownership transfers and history live beside this file.
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from .fix_device import (
    BRANCH_MANAGER_GROUP,
    CUSTODY_EVIDENCE_TYPES,
    DEVICE_DECISION_GROUP,
    NOT_SCRAPPABLE,
    bind_evidence,
    document_from_upload,
    take_upload,
)

# A07 P1 (2026-11-04) M17-12: a plan type names its interval. "custom" keeps
# a plan whose interval is none of the three.
PLAN_MONTHS = {"quarterly": 3, "biannual": 6, "annual": 12}
# Custody events that hand the device to someone (BRU-AST-08/09).
RELEASE_EVENTS = ("issued", "transferred")

# Housekeeping fields mail/ORM write on any record; never a business change.
_BOOKKEEPING = frozenset({"message_follower_ids", "message_main_attachment_id"})


def _latest_today(record):
    """The later of the user's local date and the Dhaka date. A user with no
    time zone set reads UTC, which trails Dhaka by six hours; "not in the
    future" must not refuse today's Dhaka date for them."""
    return max(
        fields.Date.context_today(record),
        fields.Date.context_today(record.with_context(tz="Asia/Dhaka")),
    )


def _changes(records, vals) -> bool:
    """True when `vals` would change a business value on one of `records`.
    Echoing the current value (the P03 form posts every field) is no change."""
    names = [n for n in set(vals) - _BOOKKEEPING if n in records._fields]
    return any(rec._fix_guard_differs(n, vals[n], rec[n]) for rec in records for n in names)


def _is_confirmed(rec) -> bool:
    return rec.state == "confirmed"


_LOG_FIELDS = frozenset({"id", "create_uid", "create_date", "write_uid", "write_date"})


def _business_fields(records) -> set:
    """Every stored field a user could write: what a frozen record locks."""
    return {n for n, f in records._fields.items() if f.store and n not in _LOG_FIELDS}


class FixApprovalMatrixDevice(models.Model):
    """M17 decision domains on the DoA register (A07 audit 2026-11-03)."""

    _inherit = "fix.approval.matrix"

    decision_domain = fields.Selection(
        selection_add=[
            ("device_merge", "Device Identity Merge"),
            ("device_scrap", "Device Scrap"),
        ],
        ondelete={"device_merge": "cascade", "device_scrap": "cascade"},
    )


class FixDeviceEstate(models.Model):
    _name = "fix.device.estate"
    _description = "Corporate Estate"
    _order = "name"

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    client_id = fields.Many2one("res.partner", string="Client", required=True, index=True)
    site = fields.Char(string="Site")
    department = fields.Char()
    cost_centre = fields.Char()
    manager_id = fields.Many2one("hr.employee", string="Estate Manager")
    active = fields.Boolean(default=True)
    notes = fields.Text()


class FixDeviceExtend(models.Model):
    _inherit = "fix.device"

    estate_id = fields.Many2one(
        "fix.device.estate", string="Corporate Estate", ondelete="set null", index=True
    )


class FixDevicePm(models.Model):
    _name = "fix.device.pm"
    _description = "Device PM Plan"
    _inherit = ["fix.guarded.mixin"]
    _order = "next_due"

    def _fix_guarded_fields(self) -> set:
        # A07 audit M17-12: Mark Done is what stamps last_done and rolls the
        # plan on; typing them (or the state) made a plan look serviced.
        return super()._fix_guarded_fields() | {"state", "last_done", "due_notified_for"}

    def _fix_form_locked_fields(self) -> set:
        # A07 operability M17-19: anyone could push a due plan out by typing a
        # date. First set when the plan is created; after that, Reschedule.
        locked = super()._fix_form_locked_fields()
        if len(self) == 1:
            locked |= {"next_due"}
        return locked

    name = fields.Char(required=True, default="New")
    device_id = fields.Many2one(
        "fix.device", string="Device", required=True, ondelete="cascade", index=True
    )
    plan_type = fields.Selection(
        [
            ("quarterly", "Quarterly"),
            ("biannual", "Bi-annual"),
            ("annual", "Annual"),
            ("custom", "Custom interval"),
        ],
        required=True,
        default="annual",
    )
    interval_months = fields.Integer(string="Interval (months)", default=12)
    last_done = fields.Date(string="Last Done")
    next_due = fields.Date(required=True)
    state = fields.Selection(
        [("active", "Active"), ("paused", "Paused")], required=True, default="active"
    )
    notes = fields.Char()
    # AUT-AST-13: the due date the cron last announced, so a plan is announced
    # once per due date however often the job runs.
    due_notified_for = fields.Date(string="Due Announced For", readonly=True, copy=False)

    @api.model
    def _derive_plan(self, vals):
        """A07 audit M17-12 (D5): plan type and interval were two independent
        typed fields ("quarterly" every 12 months). The one given decides the
        other; both given must agree (checked below). A blank interval on a new
        form is not given."""
        if not vals.get("interval_months") and vals.get("plan_type") in PLAN_MONTHS:
            vals.pop("interval_months", None)
        if "plan_type" in vals and "interval_months" not in vals:
            months = PLAN_MONTHS.get(vals["plan_type"])
            if months:
                vals["interval_months"] = months
        elif "interval_months" in vals and "plan_type" not in vals:
            inverse = {v: k for k, v in PLAN_MONTHS.items()}
            vals["plan_type"] = inverse.get(vals["interval_months"], "custom")

    def _drop_echoed_plan_value(self, vals):
        """The form posts both fields on every save, so a new plan type came with
        the old interval as an echo and every change of type was refused (A07
        operability M17-21). The type decides then; any other pair must agree."""
        if len(self) != 1 or not {"plan_type", "interval_months"} <= set(vals):
            return
        if vals["plan_type"] != self.plan_type and vals["interval_months"] == self.interval_months:
            vals.pop("interval_months")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.device.pm") or "DPM/New"
            self._derive_plan(vals)
        return super().create(vals_list)

    def write(self, vals):
        if not self._fix_guard_open() and "next_due" in vals:
            for rec in self:
                if rec._fix_guard_differs("next_due", vals["next_due"], rec.next_due):
                    raise UserError(
                        "The next due date of %s moves only by Reschedule, which needs a Branch "
                        "Manager and a reason, or by Mark Done." % rec.name
                    )
        self._drop_echoed_plan_value(vals)
        self._derive_plan(vals)
        return super().write(vals)

    @api.constrains("plan_type", "interval_months")
    def _check_plan_interval(self):
        for rec in self:
            months = PLAN_MONTHS.get(rec.plan_type)
            if months and rec.interval_months != months:
                raise ValidationError(
                    "A %s plan runs every %d months, not %d. Choose 'Custom interval' for "
                    "another interval."
                    % (
                        dict(rec._fields["plan_type"].selection)[rec.plan_type],
                        months,
                        rec.interval_months,
                    )
                )
            if rec.interval_months <= 0:
                raise ValidationError("The interval of a maintenance plan is at least one month.")

    @api.model
    def cron_pm_due(self):
        """AUT-AST-13 (ir_cron_device_pm_due, daily): announce each active plan
        that is due today or overdue, once per due date, as
        device.maintenance_due for M01 to raise the work (bridge). Idempotent
        and superuser-safe; the stamp is written through the guard."""
        today = fields.Date.context_today(self.with_context(tz="Asia/Dhaka"))
        plans = self.sudo().search([("state", "=", "active"), ("next_due", "<=", today)])
        announced = self.browse()
        for plan in plans:
            if plan.due_notified_for == plan.next_due or not plan.device_id.active:
                continue
            plan._guarded().write({"due_notified_for": plan.next_due})
            plan.device_id._publish(
                "device.maintenance_due",
                {
                    "plan": plan.name,
                    "plan_id": plan.id,
                    "device_id": plan.device_id.id,
                    "owner_id": plan.device_id.owner_id.id or None,
                    "due_date": str(plan.next_due),
                    "overdue_days": (today - plan.next_due).days,
                    "plan_type": plan.plan_type,
                },
            )
            announced |= plan
        return len(announced)

    def action_complete(self):
        """Mark the PM done and roll `next_due` on by the plan's interval.

        A07 audit M17-12: it stamped last_done and left next_due in the past,
        so a serviced plan stayed due forever and "PM Due (30d)" never
        drained. The schedule keeps its anchor (next_due + interval) and is
        rolled again until it lies after today, so a late visit does not leave
        the plan overdue."""
        today = fields.Date.context_today(self)
        for rec in self:
            if rec.state != "active":
                raise UserError("Resume the paused plan %s before marking it done." % rec.name)
            if rec.interval_months <= 0:
                raise UserError("Set the interval (months) of %s first." % rec.name)
            step = relativedelta(months=rec.interval_months)
            next_due = rec.next_due + step
            while next_due <= today:
                next_due += step
            rec._guarded().write({"last_done": today, "next_due": next_due})
        return True

    def action_reschedule(self, next_due=None, reason=None):
        """Move the next due date (A07 operability M17-19): a Branch Manager,
        with a reason on the device's record. The daily job announces the plan
        again when the new date falls due."""
        if not (reason or "").strip():
            raise UserError("Give the reason the plan is rescheduled.")
        try:
            new_due = fields.Date.to_date(next_due)
        except (TypeError, ValueError) as exc:
            raise UserError("Give the new due date as YYYY-MM-DD.") from exc
        if not new_due:
            raise UserError("Give the new due date as YYYY-MM-DD.")
        if new_due < _latest_today(self):
            raise UserError("A plan cannot be rescheduled into the past (%s)." % new_due)
        for rec in self:
            rec.device_id._assert_role(BRANCH_MANAGER_GROUP, "Rescheduling a maintenance plan")
            old = rec.next_due
            rec._guarded().write({"next_due": new_due})
            rec.device_id.message_post(
                body="Maintenance plan %s rescheduled by %s from %s to %s: %s"
                % (rec.name, self.env.user.name, old, new_due, reason.strip())
            )
        return True

    def action_pause(self):
        for rec in self:
            if rec.state != "active":
                raise UserError("Only an active plan can be paused.")
            rec._guarded().write({"state": "paused"})
        return True

    def action_resume(self):
        for rec in self:
            if rec.state != "paused":
                raise UserError("Only a paused plan can be resumed.")
            rec._guarded().write({"state": "active"})
        return True


class FixDeviceCondition(models.Model):
    _name = "fix.device.condition"
    _description = "Device Condition Grade"
    _inherit = ["fix.guarded.mixin"]
    _order = "graded_on desc, id desc"

    def _fix_guarded_fields(self) -> set:
        # A07 audit M17-10: grades were born "confirmed" (also via P03), the
        # grader confirmed his own, and a confirmed D was rewritten to A. The
        # bulk-readiness and data-quality reports read this flag.
        return super()._fix_guarded_fields() | {"state", "confirmed_by_id", "confirmed_at"}

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if len(self) == 1 and self.state == "confirmed":
            locked |= _business_fields(self)
        return locked

    def write(self, vals):
        # A confirmed grade is evidence: it is never re-graded, only superseded
        # by a new grading record.
        if not self._fix_guard_open() and _changes(self.filtered(_is_confirmed), vals):
            raise UserError("A confirmed condition grade cannot be changed. Record a new grading.")
        return super().write(vals)

    name = fields.Char(required=True, default="New")
    device_id = fields.Many2one(
        "fix.device", string="Device", required=True, ondelete="cascade", index=True
    )
    grade = fields.Selection(
        [("a", "A — Like new"), ("b", "B — Good"), ("c", "C — Fair"), ("d", "D — Poor")],
        required=True,
        default="b",
    )
    cosmetic_notes = fields.Char()
    functional_ok = fields.Boolean(default=True)
    battery_health_pct = fields.Integer(string="Battery Health %", default=100)
    inspector_id = fields.Many2one("hr.employee", string="Inspector")
    graded_on = fields.Date(required=True, default=fields.Date.context_today)
    state = fields.Selection(
        [("draft", "Draft"), ("confirmed", "Confirmed")], required=True, default="draft"
    )
    confirmed_by_id = fields.Many2one("res.users", string="Confirmed By", readonly=True, copy=False)
    confirmed_at = fields.Datetime(string="Confirmed At", readonly=True, copy=False)
    notes = fields.Text()

    _battery_range = models.Constraint(
        "CHECK (battery_health_pct >= 0 AND battery_health_pct <= 100)",
        "Battery health is a 0–100 percentage",
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.device.condition") or "DCON/New"
                )
        return super().create(vals_list)

    def action_confirm(self):
        """Confirm a draft grade. SoD: the user who recorded the grade does not
        confirm it (A07 audit M17-10); the confirmer and time are stamped."""
        for rec in self:
            if rec.state != "draft":
                raise UserError("Confirm a draft condition record")
            if not self.env.su and rec.create_uid == self.env.user:
                raise UserError(
                    "Segregation of duties: you recorded this grade, so another user must "
                    "confirm it."
                )
            rec._guarded().write(
                {
                    "state": "confirmed",
                    "confirmed_by_id": self.env.uid,
                    "confirmed_at": fields.Datetime.now(),
                }
            )
        return True


class FixDeviceIdentity(models.Model):
    _name = "fix.device.identity"
    _description = "Device Identity Resolution"
    # fix.approvable.mixin already carries fix.guarded.mixin.
    _inherit = ["fix.approvable.mixin"]
    _order = "create_date desc, id desc"

    # A07 audit (2026-11-03) M17-3 / BRU-AST-04: the creator merged his own
    # candidate, rows were born "merged", a merged row was re-decided as
    # rejected and a merge was undone by two writes. A merge archives another
    # customer's device, so it is now a routed M63 decision taken by a Tier 2
    # holder who neither raised nor requested it. A07 P2 (2026-11-04): the
    # merge re-points every row of the duplicate to the survivor and keeps the
    # lineage (fix.device.merge), reversible inside its window. The decider is
    # the Device Quality Manager (BRU-AST-04), P0's Tier 2 stand-in replaced.
    _approval_domain = "device_merge"
    _approval_apply_method = "action_merge"
    _approval_group = DEVICE_DECISION_GROUP
    _approval_routed = True

    # Once the candidate is requested or decided, these describe the pair the
    # approver signs off; they are not moved underneath the decision.
    _PAIR_FIELDS = ("primary_device_id", "duplicate_device_id", "match_reason", "match_score")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "resolved_on",
            "resolved_by_id",
            "merge_id",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if len(self) == 1 and (self.state != "candidate" or self.approval_state == "pending"):
            locked |= set(self._PAIR_FIELDS)
        return locked

    def write(self, vals):
        voided = self.browse()
        if not self._fix_guard_open() and set(self._PAIR_FIELDS) & set(vals):
            pair = {k: vals[k] for k in self._PAIR_FIELDS if k in vals}
            if _changes(self.filtered(lambda r: r.state != "candidate"), pair):
                raise UserError(
                    "A merged or rejected resolution is final. Raise a new candidate instead."
                )
            voided = self.filtered(
                lambda r: r.approval_state in ("pending", "approved") and _changes(r, pair)
            )
        result = super().write(vals)
        if voided:
            voided._approval_void("the device pair changed after approval was requested")
        return result

    name = fields.Char(required=True, default="New")
    primary_device_id = fields.Many2one(
        "fix.device", string="Surviving Device", required=True, ondelete="cascade", index=True
    )
    duplicate_device_id = fields.Many2one(
        "fix.device", string="Duplicate Device", required=True, ondelete="cascade", index=True
    )
    match_reason = fields.Char(required=True)
    match_score = fields.Float(string="Match Score %", default=100.0)
    state = fields.Selection(
        [
            ("candidate", "Candidate"),
            ("merged", "Merged"),
            ("rejected", "Rejected"),
            ("reversed", "Merge Reversed"),
        ],
        required=True,
        default="candidate",
    )
    merge_id = fields.Many2one(
        "fix.device.merge", string="Merge Lineage", readonly=True, copy=False
    )
    resolved_on = fields.Date(readonly=True)
    resolved_by_id = fields.Many2one("res.users", string="Resolved By", readonly=True, copy=False)
    notes = fields.Text()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.device.identity") or "DIDR/New"
                )
        return super().create(vals_list)

    def _merge_mismatch(self) -> list:
        """What differs between the two devices beyond the identifier the
        candidate was raised on. Live, DIDR/2026/0002 merged two devices of
        different owners and models (M17-3)."""
        self.ensure_one()
        primary, dup = self.primary_device_id, self.duplicate_device_id
        out = []
        if primary.owner_id != dup.owner_id:
            out.append("owners")
        if primary.device_model_id != dup.device_model_id:
            out.append("models")
        return out

    def _merge_check_pair(self, justification):
        for rec in self:
            if rec.primary_device_id == rec.duplicate_device_id:
                raise UserError("A device cannot be merged into itself")
            if rec.state != "candidate":
                raise UserError("Only a candidate resolution can be merged")
            mismatch = rec._merge_mismatch()
            if mismatch and not (justification or "").strip():
                raise UserError(
                    "%s and %s have different %s. Say in the approval justification why they "
                    "are the same physical device."
                    % (
                        rec.primary_device_id.display_name,
                        rec.duplicate_device_id.display_name,
                        " and ".join(mismatch),
                    )
                )

    def _approval_needed(self) -> bool:
        return self.state == "candidate"

    def action_request_approval(self, justification=None):
        """Route the merge to a Tier 2 holder. A pair with different owners or
        models is refused unless the justification says why."""
        self._merge_check_pair(justification)
        return super().action_request_approval(justification=justification)

    def action_merge(self):
        """Merge: archive the duplicate (it is never deleted, so its history
        stays auditable). The M63 apply method: reached only from the
        approver's inbox; a direct press is refused."""
        self._approval_assert_routed()
        # Superuser code with no deciding task (data loading, service calls).
        trusted = self.env.su and not self._approval_task()
        authority = self._approval_authority_user()
        acting = self._approval_acting_users()
        for rec in self:
            req = rec.approval_request_id.sudo()
            rec._merge_check_pair(req.justification if not trusted else "system")
            if not trusted:
                if not authority.has_group(DEVICE_DECISION_GROUP):
                    raise UserError(
                        "Merging devices requires the Device Quality Manager role, which %s "
                        "does not hold." % authority.name
                    )
                if acting & (rec.create_uid | req.requested_by_id):
                    raise UserError(
                        "Segregation of duties: you raised or requested this merge, so "
                        "another approver must decide it."
                    )
            lineage = self.env["fix.device.merge"]._record(rec)
            rec.duplicate_device_id._guarded().write({"active": False})
            rec._guarded().write(
                {
                    "state": "merged",
                    "resolved_on": fields.Date.context_today(self),
                    "resolved_by_id": self.env.uid,
                    "merge_id": lineage.id,
                }
            )
            rec.duplicate_device_id.message_post(
                body="Archived as a duplicate of %s (%s, approved by %s)."
                % (rec.primary_device_id.display_name, rec.name, self.env.user.name)
            )
        return True

    def action_reject(self):
        """Not a duplicate: close the candidate. Only a candidate is decided,
        and a merge request still pending is withdrawn with it."""
        for rec in self:
            if rec.state != "candidate":
                raise UserError("Only a candidate resolution can be rejected")
            rec._approval_void("the candidate was rejected as not a duplicate")
            rec._guarded().write(
                {
                    "state": "rejected",
                    "resolved_on": fields.Date.context_today(self),
                    "resolved_by_id": self.env.uid,
                }
            )
        return True


class FixDeviceCustody(models.Model):
    """A custody event: insert-only for users (FR-AST-020).

    A07 audit (2026-11-03) M17-4: events were rewritten after the fact (lost
    became found, another party, another date), also through P03, and could
    be dated in the future. A wrong event is corrected by recording the next
    one; superuser service code stays trusted.

    A07 P1 (2026-11-04) M17-4, BRU-AST-08/09: a release ("Issued to
    Customer") needs a confirmed condition grade of this device, photographic
    evidence and an accessory reconciliation, and goes only to the owner; no
    device flagged lost, scrapped or NEIR-blocked is released to anyone; a
    "Reported Lost" event puts the device in the lost register."""

    _name = "fix.device.custody"
    _description = "Device Custody Event"
    # The guard mixin is used for its trust check and form lock; no field is
    # "guarded" because a user sets every field once, at creation.
    _inherit = ["fix.guarded.mixin"]
    _order = "event_date desc, id desc"

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if len(self) == 1 and self.id:
            locked |= _business_fields(self) | {"evidence_file", "evidence_filename"}
        return locked

    def write(self, vals):
        if not self._fix_guard_open() and _changes(self, vals):
            raise UserError(
                "A custody event is a permanent record and is never edited. Record the "
                "next event (returned, found...) instead."
            )
        return super().write(vals)

    def unlink(self):
        if not self._fix_guard_open():
            raise UserError("A custody event is a permanent record and is never deleted.")
        return super().unlink()

    @api.constrains("event_date")
    def _check_event_date_not_future(self):
        for rec in self:
            if rec.event_date and rec.event_date > _latest_today(rec):
                raise ValidationError(
                    "A custody event cannot be dated in the future (%s)." % rec.event_date
                )

    name = fields.Char(required=True, default="New")
    device_id = fields.Many2one(
        "fix.device", string="Device", required=True, ondelete="cascade", index=True
    )
    event = fields.Selection(
        [
            ("issued", "Issued to Customer"),
            ("returned", "Returned to 1000FiX"),
            ("transferred", "Transferred"),
            ("lost", "Reported Lost"),
            ("found", "Recovered"),
        ],
        required=True,
        default="issued",
    )
    from_party_id = fields.Many2one("res.partner", string="From")
    to_party_id = fields.Many2one("res.partner", string="To")
    custodian_id = fields.Many2one("hr.employee", string="Custodian")
    event_date = fields.Date(required=True, default=fields.Date.context_today)
    reference = fields.Char()
    notes = fields.Char()
    # BRU-AST-08 / FR-AST-020: the release evidence.
    condition_id = fields.Many2one(
        "fix.device.condition",
        string="Condition Grade at Release",
        domain="[('device_id', '=', device_id), ('state', '=', 'confirmed')]",
    )
    evidence_document_id = fields.Many2one(
        "fix.document", string="Photographic Evidence", help="Hand-over photographs (M24)."
    )
    # A07 operability (2026-11-07): the photograph taken at the counter, uploaded
    # on the form; it becomes the document above.
    evidence_file = fields.Binary(string="Upload Photograph", store=False)
    evidence_filename = fields.Char(string="Photograph File Name", store=False)
    accessories_reconciled = fields.Boolean(
        string="Accessories Reconciled",
        help="The accessories received at intake were checked back (FR-AST-015).",
    )
    accessory_notes = fields.Char(string="Accessory Discrepancies")
    signature_ref = fields.Char(string="Signature Reference")

    @api.model
    def _check_release(self, vals):
        """BRU-AST-08/09 for a user's release event."""
        device = self.env["fix.device"].browse(vals.get("device_id")).exists()
        if not device:
            return
        label = dict(self._fields["event"].selection)[vals["event"]]
        if device.state in NOT_SCRAPPABLE:
            raise UserError(
                "%s is %s: it is not released to anyone until the flag is cleared "
                "(BRU-AST-09)." % (device.display_name, device._state_label())
            )
        device._neir_assert_not_blocked("be released")
        party = self.env["res.partner"].browse(vals.get("to_party_id") or 0).exists()
        if not party:
            raise UserError("Name who receives %s (%s)." % (device.display_name, label))
        if vals["event"] != "issued":
            return
        if not device._owner_is(party):
            raise UserError(
                "%s belongs to %s; it is issued to its owner, not to %s."
                % (device.display_name, device.owner_id.name or "nobody", party.name)
            )
        missing = []
        cond = self.env["fix.device.condition"].browse(vals.get("condition_id") or 0).exists()
        if not cond or cond.device_id != device or cond.state != "confirmed":
            missing.append("a confirmed condition grade of this device")
        if not vals.get("evidence_document_id"):
            missing.append("photographic evidence")
        if not vals.get("accessories_reconciled"):
            missing.append("the accessory reconciliation")
        if missing:
            raise UserError(
                "%s cannot be released without %s (BRU-AST-08)."
                % (device.display_name, ", ".join(missing))
            )

    @api.model_create_multi
    def create(self, vals_list):
        trusted = self._fix_guard_open()
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.device.custody") or "DCUS/New"
                )
            data, filename = take_upload(vals, "evidence_file", "evidence_filename")
            device = self.env["fix.device"].browse(vals.get("device_id") or 0).exists()
            if data and device:
                vals["evidence_document_id"] = document_from_upload(
                    self.env,
                    device,
                    data,
                    filename,
                    "custody_photo",
                    "Custody photograph - %s" % device.display_name,
                    device._name,
                    device.id,
                ).id
            if not trusted and vals.get("event", "issued") in RELEASE_EVENTS:
                self._check_release(dict(vals, event=vals.get("event", "issued")))
        records = super().create(vals_list)
        for rec in records:
            device = rec.device_id
            if rec.evidence_document_id and not trusted:
                bind_evidence(
                    rec.evidence_document_id,
                    [rec, device],
                    "custody evidence",
                    CUSTODY_EVIDENCE_TYPES,
                )
                used = self.sudo().search(
                    [
                        ("evidence_document_id", "=", rec.evidence_document_id.id),
                        ("id", "!=", rec.id),
                    ],
                    limit=1,
                )
                if used:
                    raise UserError(
                        "%s is already the evidence of custody event %s. Each hand-over needs "
                        "its own photograph." % (rec.evidence_document_id.sudo().name, used.name)
                    )
            if rec.event == "lost" and device.state not in NOT_SCRAPPABLE:
                device._flag_lost(
                    "Custody event %s: %s" % (rec.name, rec.notes or "reported lost"), "custody"
                )
            device._publish(
                "device.custody_recorded",
                {
                    "device_id": device.id,
                    "custody": rec.name,
                    "event": rec.event,
                    "from_party_id": rec.from_party_id.id or None,
                    "to_party_id": rec.to_party_id.id or None,
                    "event_date": str(rec.event_date),
                    "condition_grade": rec.condition_id.grade or None,
                    "evidence_document_id": rec.evidence_document_id.id or None,
                    "signature_ref": rec.signature_ref or None,
                },
            )
        return records


class FixDeviceComponent(models.Model):
    _name = "fix.device.component"
    _description = "Installed Device Component"
    _inherit = ["fix.guarded.mixin"]
    _order = "installed_on desc, id desc"

    def _fix_guarded_fields(self) -> set:
        # A07 audit M17-11: a removed part was re-installed by write, and a part
        # "removed" with no date. Removal is the action below; so is the
        # removed part's disposition (FR-AST-028).
        return super()._fix_guarded_fields() | {"state", "removed_on", "disposition"}

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if len(self) == 1 and self.state == "removed":
            locked |= _business_fields(self)
        return locked

    def write(self, vals):
        # A removed installation is genealogy: its dates and part are history.
        removed = self.filtered(lambda r: r.state == "removed")
        if not self._fix_guard_open() and _changes(removed, vals):
            raise UserError(
                "A removed component is part of the device's history and is not edited. "
                "Record a new installation instead."
            )
        return super().write(vals)

    @api.constrains("serial_no", "state")
    def _check_serial_installed_once(self):
        """One serial, one device at a time (genealogy, M17-11). Compared
        case- and space-insensitively, in SQL so a part installed in a device
        the user cannot see still counts."""
        self.flush_model(["serial_no", "state", "device_id"])
        for rec in self.filtered(lambda r: r.state == "installed" and (r.serial_no or "").strip()):
            self.env.cr.execute(
                "SELECT device_id FROM fix_device_component WHERE state = 'installed' "
                "AND id != %s AND upper(btrim(serial_no)) = %s LIMIT 1",
                (rec.id, rec.serial_no.strip().upper()),
            )
            row = self.env.cr.fetchone()
            if row:
                raise ValidationError(
                    "Component serial %s is already installed in %s. Remove it there first."
                    % (rec.serial_no, self.env["fix.device"].sudo().browse(row[0]).display_name)
                )

    @api.constrains("part_number", "part_name", "source_ref", "device_id", "state")
    def _check_part_compatible(self):
        """A07 audit M17-11: a part the compatibility matrix grades "Tested
        Incompatible" for the device's model was installed, because the
        component had no link to the matrix. The part is matched by its number,
        or by the part reference typed in its name or source (case- and
        space-insensitive); the matrix is read whatever the user's scope."""
        Matrix = self.env["fix.device.part.compatibility"].sudo()
        for rec in self.filtered(lambda r: r.state == "installed"):
            refs = {
                (v or "").strip().upper()
                for v in (rec.part_number, rec.part_name, rec.source_ref)
                if (v or "").strip()
            }
            if not refs:
                continue
            bad = Matrix.search(
                [
                    ("model_id", "=", rec.device_id.device_model_id.id),
                    ("compatibility_type", "=", "incompatible"),
                ]
            ).filtered(lambda m, refs=refs: m.part_number.strip().upper() in refs)
            if bad:
                raise ValidationError(
                    "%s is graded '%s' for %s in the compatibility matrix and cannot be "
                    "installed."
                    % (
                        bad[0].part_number,
                        dict(bad._fields["compatibility_type"].selection)["incompatible"],
                        rec.device_id.device_model_id.name,
                    )
                )

    @api.constrains("warranty_until", "installed_on", "removed_on")
    def _check_genealogy_dates(self):
        for rec in self:
            if rec.warranty_until and rec.installed_on and rec.warranty_until < rec.installed_on:
                raise ValidationError("A part's warranty cannot end before it was fitted.")
            if rec.removed_on and rec.installed_on and rec.removed_on < rec.installed_on:
                raise ValidationError("A part cannot be removed before it was fitted.")

    @api.constrains("service_order_model", "service_order_id", "lot_model", "lot_id")
    def _check_references(self):
        """The causing job and the stock lot are referenced by model and id
        (M01 and M15 load after the registry); a reference must exist."""
        for rec in self:
            for model_field, id_field in (
                ("service_order_model", "service_order_id"),
                ("lot_model", "lot_id"),
            ):
                model, res_id = rec[model_field], rec[id_field]
                if not res_id:
                    continue
                if model not in self.env.registry:
                    raise ValidationError("%s is not installed on this database." % model)
                if not self.env[model].sudo().browse(res_id).exists():
                    raise ValidationError("%s #%s does not exist." % (model, res_id))

    device_id = fields.Many2one(
        "fix.device", string="Device", required=True, ondelete="cascade", index=True
    )
    part_name = fields.Char(string="Part / Component", required=True)
    serial_no = fields.Char(string="Component Serial")
    installed_on = fields.Date(required=True, default=fields.Date.context_today)
    removed_on = fields.Date()
    source_ref = fields.Char(string="Source Order / PO")
    state = fields.Selection(
        [("installed", "Installed"), ("removed", "Removed")], required=True, default="installed"
    )
    notes = fields.Char()
    # A07 P2 (2026-11-04) FR-AST-027/028 genealogy: the part, its lot, the job
    # and technician that fitted it, its own warranty, the stock it was drawn
    # from, and what became of it when removed.
    part_number = fields.Char(string="Part Number", index=True)
    product_id = fields.Many2one("product.product", string="Part (Catalogue)", index=True)
    lot_model = fields.Char(default="stock.lot", readonly=True)
    lot_id = fields.Many2oneReference(string="Stock Lot", model_field="lot_model")
    service_order_model = fields.Char(default="fix.service.order", readonly=True)
    service_order_id = fields.Many2oneReference(
        string="Causing Job", model_field="service_order_model", index=True
    )
    technician_id = fields.Many2one("hr.employee", string="Fitted By")
    warranty_until = fields.Date(string="Part Warranty Until")
    ownership_class = fields.Selection(
        [
            ("company_stock", "1000FiX stock"),
            ("customer_supplied", "Customer supplied"),
            ("brand_supplied", "Brand supplied (warranty)"),
            ("consignment", "Consignment"),
        ],
        string="Ownership Class",
    )
    disposition = fields.Selection(
        [
            ("returned_to_customer", "Returned to customer"),
            ("harvested", "Harvested"),
            ("scrapped", "Scrapped"),
            ("returned_to_brand", "Returned to brand"),
        ],
        string="Removed-Part Disposition",
        readonly=True,
        copy=False,
    )

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            rec.device_id._publish(
                "device.genealogy_recorded",
                {
                    "device_id": rec.device_id.id,
                    "component_id": rec.id,
                    "part_number": rec.part_number or None,
                    "part_name": rec.part_name,
                    "serial_no": rec.serial_no or None,
                    "warranty_until": str(rec.warranty_until) if rec.warranty_until else None,
                    "service_order_id": rec.service_order_id or None,
                },
            )
        return records

    def _check_disposition(self, disposition):
        if disposition and disposition not in dict(self._fields["disposition"].selection):
            raise UserError("Unknown disposition %r." % (disposition,))

    def action_remove(self, disposition=None):
        self._check_disposition(disposition)
        for rec in self:
            if rec.state != "installed":
                raise UserError("Remove an installed component")
            vals = {"state": "removed", "removed_on": fields.Date.context_today(self)}
            if disposition:
                vals["disposition"] = disposition
            rec._guarded().write(vals)
        return True

    def action_record_disposition(self, disposition=None):
        """Record what became of a removed part, once (FR-AST-028)."""
        if not disposition:
            raise UserError("Choose the removed part's disposition.")
        self._check_disposition(disposition)
        for rec in self:
            if rec.state != "removed" or rec.disposition:
                raise UserError("Only a removed part with no disposition is recorded.")
            rec._guarded().write({"disposition": disposition})
        return True

    # P03 buttons
    def action_dispose_returned(self):
        return self.action_record_disposition("returned_to_customer")

    def action_dispose_scrapped(self):
        return self.action_record_disposition("scrapped")

    def action_dispose_harvested(self):
        return self.action_record_disposition("harvested")

    def action_dispose_returned_to_brand(self):
        return self.action_record_disposition("returned_to_brand")
