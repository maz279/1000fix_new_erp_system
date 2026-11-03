# fix_device_ops — M17: corporate estates, PM plans, condition grading, identity
# resolution, custody events and installed components. The device master,
# warranties, ownership transfers and history live beside this file.
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from .fix_device import DEVICE_DECISION_GROUP

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
        return super()._fix_guarded_fields() | {"state", "last_done"}

    name = fields.Char(required=True, default="New")
    device_id = fields.Many2one(
        "fix.device", string="Device", required=True, ondelete="cascade", index=True
    )
    plan_type = fields.Selection(
        [("quarterly", "Quarterly"), ("biannual", "Bi-annual"), ("annual", "Annual")],
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

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.device.pm") or "DPM/New"
        return super().create(vals_list)

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
    # holder who neither raised nor requested it. Lineage re-pointing
    # (history, warranty, orders to the survivor) is P2 and not built here.
    _approval_domain = "device_merge"
    _approval_apply_method = "action_merge"
    _approval_group = DEVICE_DECISION_GROUP
    _approval_routed = True

    # Once the candidate is requested or decided, these describe the pair the
    # approver signs off; they are not moved underneath the decision.
    _PAIR_FIELDS = ("primary_device_id", "duplicate_device_id", "match_reason", "match_score")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "resolved_on", "resolved_by_id"}

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
        [("candidate", "Candidate"), ("merged", "Merged"), ("rejected", "Rejected")],
        required=True,
        default="candidate",
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
                        "Merging devices requires DOFA Tier 2 (Branch / Operations Manager) "
                        "authority, which %s does not hold." % authority.name
                    )
                if acting & (rec.create_uid | req.requested_by_id):
                    raise UserError(
                        "Segregation of duties: you raised or requested this merge, so "
                        "another approver must decide it."
                    )
            rec.duplicate_device_id._guarded().write({"active": False})
            rec._guarded().write(
                {
                    "state": "merged",
                    "resolved_on": fields.Date.context_today(self),
                    "resolved_by_id": self.env.uid,
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
    one; superuser service code stays trusted."""

    _name = "fix.device.custody"
    _description = "Device Custody Event"
    # The guard mixin is used for its trust check and form lock; no field is
    # "guarded" because a user sets every field once, at creation.
    _inherit = ["fix.guarded.mixin"]
    _order = "event_date desc, id desc"

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if len(self) == 1 and self.id:
            locked |= _business_fields(self)
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

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.device.custody") or "DCUS/New"
                )
        return super().create(vals_list)


class FixDeviceComponent(models.Model):
    _name = "fix.device.component"
    _description = "Installed Device Component"
    _inherit = ["fix.guarded.mixin"]
    _order = "installed_on desc, id desc"

    def _fix_guarded_fields(self) -> set:
        # A07 audit M17-11: a removed part was re-installed by write, and a part
        # "removed" with no date. Removal is the action below.
        return super()._fix_guarded_fields() | {"state", "removed_on"}

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

    def action_remove(self):
        for rec in self:
            if rec.state != "installed":
                raise UserError("Remove an installed component")
            rec._guarded().write(
                {"state": "removed", "removed_on": fields.Date.context_today(self)}
            )
        return True
