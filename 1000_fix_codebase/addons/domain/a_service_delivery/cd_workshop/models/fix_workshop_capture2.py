"""M31 capture pass 2 (19 Nov 2026): the records the specification gives each
sub-module page, which no page could capture.

The 13-14 Nov passes gave all nine pages a relevant button. Read against
the specification (§5 FR-WSR-001..053, §9 BRU-WSR-01..14, §10.1 owned
entities), the pages still had nowhere to record most of what a workshop
keeps: the teardown, the instruments used, consumables, the work clock, the
burn-in station and its run, internal rework, the bench hand-over, the
workshop transfer, the shift close and the device's location in the
workshop. Two hard rules were not enforced at all: BRU-WSR-08/12 (warranty
stock and harvested parts) and BRU-WSR-14 (a transfer needs the receiving
workshop's confirmation and a logistics consignment).

Every record here goes through the job's own rules: a closed job takes no
new record, stamps are written by the server, and evidence once recorded is
not edited.
"""

from markupsafe import Markup, escape
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from .fix_workshop_job import (
    CLOSED_JOB_STATES,
    GROUP_SUPERVISOR,
    TECHNICIAN_LOCKED_STATES,
)
from .fix_workshop_test import LEVELS as LEVELS_SELECTION

HIGH_VALUE_PARAM = "cd_workshop.high_value_bdt"
HIGH_VALUE_DEFAULT = 25000.0
COST_TOLERANCE_PARAM = "cd_workshop.cost_variance_tolerance_pct"
COST_TOLERANCE_DEFAULT = 10.0
LEVEL_RANK = {"l1": 1, "l2": 2, "l3": 3}
# a device is physically in the workshop from book-in until it leaves
HELD_STATES = (
    "intake",
    "diagnostic",
    "waiting_parts",
    "in_repair",
    "burn_in",
    "qc_pending",
    "qc_failed",
    "ready",
)
# a transfer moves a job that is not on the bench: one in repair, burn-in or
# QC is first put to Wait for Parts (its technician and QC are fixed)
TRANSFERABLE_STATES = ("draft", "intake", "diagnostic", "waiting_parts", "qc_failed")


def _is_supervisor(env):
    return env.su or env.user.has_group(GROUP_SUPERVISOR)


def _param_float(env, key, default):
    raw = env["ir.config_parameter"].sudo().get_param(key)
    try:
        return float(raw) if raw not in (None, False, "") else default
    except (TypeError, ValueError):
        return default


def _check_job_open(jobs, what):
    for job in jobs:
        if job.state in CLOSED_JOB_STATES:
            raise UserError(
                "Job %s is closed: a closed job is the record of the repair and takes no new %s."
                % (job.name, what)
            )


def _frozen(records, vals, allowed, what):
    """Evidence once recorded is not edited, except the named fields."""
    if records.env.su or records._fix_guard_open():
        return
    # a guarded field is refused by the guard itself, with its own message
    blocked = set(vals) - set(allowed) - records._fix_guarded_fields()
    if blocked:
        raise UserError("%s is evidence once recorded and is not edited." % what)


# ======================================================================
# 1 / 2 / 3: where the device is in the workshop (FR-WSR-005/042/053)
# ======================================================================
class FixWorkshopLocation(models.Model):
    """A place in a workshop that holds devices off the bench: the incoming
    buffer (FR-WSR-005), outgoing staging (FR-WSR-042) and the secure store
    for high-value devices overnight (FR-WSR-053, BRU-WSR-13)."""

    _name = "fix.workshop.location"
    _description = "Workshop Device Location"
    _order = "workshop_id, kind, code"

    workshop_id = fields.Many2one(
        "fix.workshop", string="Workshop", required=True, index=True, ondelete="restrict"
    )
    company_id = fields.Many2one(related="workshop_id.company_id", store=True, readonly=True)
    code = fields.Char(string="Location Code", required=True)
    name = fields.Char(string="Location", required=True)
    kind = fields.Selection(
        [
            ("incoming_buffer", "Incoming Buffer"),
            ("outgoing_staging", "Outgoing Staging"),
            ("secure_store", "Secure Store (high value)"),
        ],
        string="Kind",
        required=True,
        default="incoming_buffer",
    )
    capacity = fields.Integer(string="Capacity (devices)", help="0 means no limit.")
    occupant_count = fields.Integer(string="Devices Here", compute="_compute_occupants")
    active = fields.Boolean(default=True)

    _code_unique = models.Constraint(
        "unique(workshop_id, code)", "A location code is unique within its workshop."
    )

    def _compute_occupants(self):
        Job = self.env["fix.workshop.job"].sudo()
        for rec in self:
            rec.occupant_count = Job.search_count(
                [("current_location_id", "=", rec.id), ("state", "in", HELD_STATES)]
            )

    @api.constrains("capacity")
    def _check_capacity(self):
        for rec in self:
            if rec.capacity < 0:
                raise ValidationError("A capacity cannot be negative.")

    @api.depends("code", "name", "kind")
    def _compute_display_name(self):
        kinds = dict(self._fields["kind"].selection)
        for rec in self:
            rec.display_name = "%s · %s (%s)" % (rec.code, rec.name, kinds.get(rec.kind, ""))


class FixWorkshopCustodyMove(models.Model):
    """One move of a device into a workshop location: the custody trail inside
    the workshop. Never edited or deleted."""

    _name = "fix.workshop.custody.move"
    _description = "Workshop Device Location Move"
    _inherit = ["fix.guarded.mixin"]
    _order = "moved_at desc, id desc"

    job_id = fields.Many2one(
        "fix.workshop.job", string="Repair Job", required=True, index=True, ondelete="restrict"
    )
    location_id = fields.Many2one(
        "fix.workshop.location", string="To Location", required=True, ondelete="restrict"
    )
    location_kind = fields.Selection(related="location_id.kind", string="Kind", readonly=True)
    from_location_id = fields.Many2one(
        "fix.workshop.location", string="From Location", readonly=True
    )
    note = fields.Char(string="Note")
    moved_by_id = fields.Many2one("res.users", string="Moved By", readonly=True)
    moved_at = fields.Datetime(string="Moved At", readonly=True)
    company_id = fields.Many2one(related="job_id.company_id", store=True, readonly=True)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"from_location_id", "moved_by_id", "moved_at"}

    @api.model_create_multi
    def create(self, vals_list):
        Job = self.env["fix.workshop.job"]
        Location = self.env["fix.workshop.location"]
        for vals in vals_list:
            job = Job.browse(vals.get("job_id")).exists()
            location = Location.browse(vals.get("location_id")).exists()
            if not job or not location:
                raise UserError("Choose the repair job and the location it goes to.")
            _check_job_open(job, "location move")
            if job.state == "draft":
                raise UserError(
                    "Job %s is not booked in yet: book it in before placing it." % job.name
                )
            if location.sudo().workshop_id != job.workshop_id:
                raise UserError(
                    "Location %s belongs to %s, not to the job's workshop %s."
                    % (location.code, location.sudo().workshop_id.name, job.workshop_id.name)
                )
            if not location.active:
                raise UserError("Location %s is archived." % location.code)
            if job.current_location_id == location:
                raise UserError("Job %s is already in %s." % (job.name, location.code))
            if location.capacity:
                here = Job.sudo().search_count(
                    [("current_location_id", "=", location.id), ("state", "in", HELD_STATES)]
                )
                if here >= location.capacity:
                    raise UserError(
                        "Location %s is full: %d of %d devices."
                        % (location.code, here, location.capacity)
                    )
        records = super().create(vals_list)
        now = fields.Datetime.now()
        for rec in records:
            rec._guarded().write(
                {
                    "from_location_id": rec.job_id.current_location_id.id or False,
                    "moved_by_id": self.env.uid,
                    "moved_at": now,
                }
            )
            rec.job_id._guarded().write({"current_location_id": rec.location_id.id})
            rec.job_id.message_post(
                body="Device moved to %s%s"
                % (rec.location_id.display_name, (": %s" % rec.note) if rec.note else ".")
            )
        return records

    def write(self, vals):
        _frozen(self, vals, (), "A location move")
        return super().write(vals)

    def unlink(self):
        if not self.env.su:
            raise UserError("The custody trail inside the workshop is never deleted.")
        return super().unlink()


# ======================================================================
# 2: the daily ESD verification at the bench (FR-WSR-050)
# ======================================================================
class FixWorkshopEsdCheck(models.Model):
    """The pre-shift wrist-strap and mat reading at a bench. A pass feeds the
    bench's ESD interlock (FLAW-31.2); a failed reading is kept too and takes
    the bench's ESD status down until a passing check."""

    _name = "fix.workshop.esd.check"
    _description = "Bench ESD Verification"
    _inherit = ["fix.guarded.mixin"]
    _order = "checked_at desc, id desc"

    bench_id = fields.Many2one(
        "fix.workshop.bench", string="Bench", required=True, index=True, ondelete="restrict"
    )
    workshop_id = fields.Many2one(related="bench_id.workshop_id", store=True, readonly=True)
    wrist_strap_mohm = fields.Float(string="Wrist Strap (MΩ)", required=True)
    worksurface_mohm = fields.Float(string="Worksurface (MΩ)", required=True)
    passed = fields.Boolean(string="Passed", compute="_compute_passed", store=True)
    note = fields.Char(string="Note")
    checked_by_id = fields.Many2one("res.users", string="Checked By", readonly=True)
    checked_at = fields.Datetime(string="Checked At", readonly=True)
    company_id = fields.Many2one(related="bench_id.company_id", store=True, readonly=True)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"checked_by_id", "checked_at"}

    @api.depends("wrist_strap_mohm", "worksurface_mohm")
    def _compute_passed(self):
        for rec in self:
            rec.passed = (0.0 < rec.wrist_strap_mohm < 35.0) and (
                0.0 < rec.worksurface_mohm < 1000.0
            )

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            rec._guarded().write(
                {"checked_by_id": self.env.uid, "checked_at": fields.Datetime.now()}
            )
            bench = rec.bench_id
            if rec.passed:
                bench.action_log_daily_esd(rec.wrist_strap_mohm, rec.worksurface_mohm)
            else:
                bench._guarded().write(
                    {
                        "wrist_strap_mohm": rec.wrist_strap_mohm,
                        "worksurface_rtg_mohm": rec.worksurface_mohm,
                        "is_esd_safe": False,
                    }
                )
                bench.message_post(
                    body="ESD check FAILED (strap %g MΩ, surface %g MΩ): L2/L3 repair is blocked "
                    "on this bench until a passing check."
                    % (rec.wrist_strap_mohm, rec.worksurface_mohm)
                )
        return records

    def write(self, vals):
        _frozen(self, vals, (), "An ESD check")
        return super().write(vals)

    def unlink(self):
        if not self.env.su:
            raise UserError("An ESD check is compliance evidence and is never deleted.")
        return super().unlink()


# ======================================================================
# 3: the bench hand-over (FR-WSR-015) and the shift close (FR-WSR-017/053)
# ======================================================================
class FixWorkshopBenchHandover(models.Model):
    """Spec entity fix.bench.handover: written by Allocate to Bench whenever a
    job changes bench or technician. Read-only."""

    _name = "fix.workshop.bench.handover"
    _description = "Bench / Technician Hand-Over"
    _order = "occurred_at desc, id desc"

    job_id = fields.Many2one(
        "fix.workshop.job", string="Repair Job", required=True, index=True, ondelete="restrict"
    )
    from_bench_id = fields.Many2one("fix.workshop.bench", string="From Bench", readonly=True)
    to_bench_id = fields.Many2one("fix.workshop.bench", string="To Bench", readonly=True)
    from_technician_id = fields.Many2one("hr.employee", string="From Technician", readonly=True)
    to_technician_id = fields.Many2one("hr.employee", string="To Technician", readonly=True)
    job_state = fields.Char(string="Job State at Hand-Over", readonly=True)
    note = fields.Text(string="Hand-Over Note", readonly=True)
    recorded_by_id = fields.Many2one("res.users", string="Recorded By", readonly=True)
    occurred_at = fields.Datetime(string="Handed Over At", readonly=True)
    company_id = fields.Many2one(related="job_id.company_id", store=True, readonly=True)

    def write(self, vals):
        if not self.env.su:
            raise UserError("A hand-over is the record of who held the job, and is not edited.")
        return super().write(vals)

    def unlink(self):
        if not self.env.su:
            raise UserError("A hand-over is never deleted.")
        return super().unlink()


class FixWorkshopShiftClose(models.Model):
    """The supervisor's shift close (FR-WSR-017, SOP SP-010 steps 22-23): the
    WIP count reconciles to the system or the exception is recorded, and no
    shift closes while a high-value device held overnight is outside the
    secure store (BRU-WSR-13, a hard rule)."""

    _name = "fix.workshop.shift.close"
    _description = "Workshop Shift Close"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "shift_date desc, id desc"

    workshop_id = fields.Many2one(
        "fix.workshop", string="Workshop", required=True, index=True, ondelete="restrict"
    )
    company_id = fields.Many2one(related="workshop_id.company_id", store=True, readonly=True)
    shift_date = fields.Date(string="Shift Date", required=True, default=fields.Date.context_today)
    shift = fields.Selection(
        [("day", "Day"), ("evening", "Evening"), ("night", "Night")],
        string="Shift",
        required=True,
        default="day",
    )
    counted_wip = fields.Integer(string="Devices Counted", required=True)
    exception_note = fields.Text(
        string="Count Exception",
        help="Required when the count does not match the system: what was found and done.",
    )
    system_wip = fields.Integer(string="Devices per System", readonly=True)
    high_value_count = fields.Integer(string="High-Value Devices Held", readonly=True)
    high_value_summary = fields.Text(string="High-Value Devices and Locations", readonly=True)
    state = fields.Selection(
        [("draft", "Open"), ("closed", "Closed")],
        string="Status",
        default="draft",
        required=True,
        readonly=True,
        tracking=True,
    )
    closed_by_id = fields.Many2one("res.users", string="Closed By", readonly=True)
    closed_at = fields.Datetime(string="Closed At", readonly=True)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "system_wip",
            "high_value_count",
            "high_value_summary",
            "closed_by_id",
            "closed_at",
        }

    @api.depends("workshop_id", "shift_date", "shift")
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = "%s · %s · %s" % (
                rec.workshop_id.code or "",
                rec.shift_date or "",
                dict(self._fields["shift"].selection).get(rec.shift, ""),
            )

    def write(self, vals):
        if not self._fix_guard_open() and any(r.state == "closed" for r in self):
            raise UserError("A closed shift is the record of the count and is not edited.")
        return super().write(vals)

    def unlink(self):
        if any(r.state == "closed" for r in self) and not self.env.su:
            raise UserError("A closed shift is never deleted.")
        return super().unlink()

    def _held_jobs(self):
        self.ensure_one()
        return (
            self.env["fix.workshop.job"]
            .sudo()
            .search([("workshop_id", "=", self.workshop_id.id), ("state", "in", HELD_STATES)])
        )

    def action_close(self):
        threshold = _param_float(self.env, HIGH_VALUE_PARAM, HIGH_VALUE_DEFAULT)
        for rec in self:
            if not _is_supervisor(self.env):
                raise UserError("A shift is closed by a workshop supervisor.")
            if rec.state == "closed":
                raise UserError("This shift is already closed.")
            if self.search_count(
                [
                    ("workshop_id", "=", rec.workshop_id.id),
                    ("shift_date", "=", rec.shift_date),
                    ("shift", "=", rec.shift),
                    ("state", "=", "closed"),
                    ("id", "!=", rec.id),
                ]
            ):
                raise UserError("That shift of %s is already closed." % rec.workshop_id.name)
            held = rec._held_jobs()
            if rec.counted_wip != len(held) and not (rec.exception_note or "").strip():
                raise UserError(
                    "The count (%d) does not reconcile to the system (%d devices held). "
                    "Recount, or record the exception before closing (SOP SP-010 step 23)."
                    % (rec.counted_wip, len(held))
                )
            high_value = held.filtered(
                lambda j: j.high_value_device or (j.estimate_ceiling or 0.0) >= threshold
            )
            unsecured = high_value.filtered(lambda j: j.current_location_id.kind != "secure_store")
            if unsecured:
                raise UserError(
                    "BRU-WSR-13: these high-value devices are not in the secure store, so the "
                    "shift cannot close: %s. Move each one with Move Device to Location."
                    % ", ".join(unsecured.mapped("name"))
                )
            summary = "\n".join(
                "%s: %s" % (j.name, j.current_location_id.display_name) for j in high_value
            )
            rec._guarded().write(
                {
                    "state": "closed",
                    "system_wip": len(held),
                    "high_value_count": len(high_value),
                    "high_value_summary": summary or False,
                    "closed_by_id": self.env.uid,
                    "closed_at": fields.Datetime.now(),
                }
            )
        return True


# ======================================================================
# 4: escalation to a specialist (FR-WSR-029)
# ======================================================================
class FixWorkshopEscalation(models.Model):
    """A repair escalated to a higher level, a specialist technician or
    another workshop, with the reason and the bench context at the time. A
    supervisor other than the requester accepts it; acceptance applies it
    through the job's own routes (level lock, certification, bench rules,
    or a workshop transfer)."""

    _name = "fix.workshop.escalation"
    _description = "Workshop Repair Escalation"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "requested_at desc, id desc"

    job_id = fields.Many2one(
        "fix.workshop.job", string="Repair Job", required=True, index=True, ondelete="restrict"
    )
    escalation_type = fields.Selection(
        [
            ("higher_level", "Higher Repair Level"),
            ("specialist", "Specialist Technician"),
            ("other_workshop", "Another Workshop"),
        ],
        string="Escalate To",
        required=True,
        default="higher_level",
    )
    to_level = fields.Selection(LEVELS_SELECTION, string="New Repair Level")
    to_technician_id = fields.Many2one("hr.employee", string="Specialist Technician")
    to_workshop_id = fields.Many2one("fix.workshop", string="Receiving Workshop")
    reason = fields.Text(string="Why Escalate", required=True)
    context_snapshot = fields.Text(string="Bench Context at Escalation", readonly=True)
    state = fields.Selection(
        [("requested", "Requested"), ("accepted", "Accepted"), ("declined", "Declined")],
        string="Status",
        default="requested",
        required=True,
        readonly=True,
        tracking=True,
    )
    requested_by_id = fields.Many2one("res.users", string="Raised By", readonly=True)
    requested_at = fields.Datetime(string="Raised At", readonly=True)
    decided_by_id = fields.Many2one("res.users", string="Decided By", readonly=True)
    decided_at = fields.Datetime(string="Decided At", readonly=True)
    decision_note = fields.Text(string="Decision Note", readonly=True)
    transfer_id = fields.Many2one("fix.workshop.transfer", string="Transfer Raised", readonly=True)
    company_id = fields.Many2one(related="job_id.company_id", store=True, readonly=True)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "context_snapshot",
            "state",
            "requested_by_id",
            "requested_at",
            "decided_by_id",
            "decided_at",
            "decision_note",
            "transfer_id",
        }

    @api.model
    def _check_target_values(self, job, kind, to_level, to_technician_id, to_workshop_id):
        if kind == "higher_level":
            if LEVEL_RANK.get(to_level, 0) <= LEVEL_RANK.get(job.repair_level, 0):
                raise UserError(
                    "Escalate to a level above the job's own (%s)."
                    % (job.repair_level or "").upper()
                )
        elif kind == "specialist":
            if not to_technician_id or to_technician_id == job.technician_id.id:
                raise UserError("Name the specialist technician the job goes to.")
        elif not to_workshop_id or to_workshop_id == job.workshop_id.id:
            raise UserError("Name the other workshop the job goes to.")

    def _check_target(self):
        for rec in self:
            rec._check_target_values(
                rec.job_id,
                rec.escalation_type,
                rec.to_level,
                rec.to_technician_id.id,
                rec.to_workshop_id.id,
            )

    @api.model_create_multi
    def create(self, vals_list):
        Job = self.env["fix.workshop.job"]
        for vals in vals_list:
            job = Job.browse(vals.get("job_id")).exists()
            if not job:
                raise UserError("Choose the repair job to escalate.")
            _check_job_open(job, "escalation")
            if not (vals.get("reason") or "").strip():
                raise UserError("Say why the repair is escalated.")
            self._check_target_values(
                job,
                vals.get("escalation_type") or "higher_level",
                vals.get("to_level"),
                vals.get("to_technician_id"),
                vals.get("to_workshop_id"),
            )
            if self.search_count([("job_id", "=", job.id), ("state", "=", "requested")]):
                raise UserError("Job %s already has an escalation waiting." % job.name)
        records = super().create(vals_list)
        for rec in records:
            job = rec.job_id.sudo()
            snapshot = "\n".join(
                [
                    "State: %s · Level: %s · Technician: %s · Bench: %s"
                    % (
                        job.state,
                        (job.repair_level or "").upper(),
                        job.technician_id.name or "-",
                        job.bench_id.code or "-",
                    ),
                    "Findings: %s" % (job.diagnostic_findings or "-"),
                    "Actions so far: %s" % (job.repair_action_summary or "-"),
                ]
            )
            rec._guarded().write(
                {
                    "context_snapshot": snapshot,
                    "requested_by_id": self.env.uid,
                    "requested_at": fields.Datetime.now(),
                }
            )
            rec.job_id.message_post(body="Escalation raised: %s" % rec.reason)
        return records

    def write(self, vals):
        if not self._fix_guard_open() and any(r.state != "requested" for r in self):
            raise UserError("A decided escalation is not edited.")
        res = super().write(vals)
        if {"escalation_type", "to_level", "to_technician_id", "to_workshop_id"} & set(vals):
            self._check_target()
        return res

    def _assert_decider(self):
        self.ensure_one()
        if not _is_supervisor(self.env):
            raise UserError("An escalation is decided by a workshop supervisor.")
        if self.requested_by_id == self.env.user and not self.env.su:
            raise UserError("The person who raised an escalation does not decide it.")
        if self.state != "requested":
            raise UserError("This escalation is already decided.")

    def action_accept(self, note=None):
        for rec in self:
            rec._assert_decider()
            job = rec.job_id
            vals = {}
            if rec.escalation_type == "higher_level":
                # the job's own lock refuses a level change on a job under way
                job.write({"repair_level": rec.to_level})
            elif rec.escalation_type == "specialist":
                if job.bench_id:
                    job.action_allocate_bench(
                        bench_id=job.bench_id.id,
                        technician_id=rec.to_technician_id.id,
                        note="Escalated: %s" % rec.reason,
                    )
                else:
                    if job.state in TECHNICIAN_LOCKED_STATES:
                        raise UserError("Job %s is under way: its technician is fixed." % job.name)
                    job._check_technician_certification(rec.to_technician_id, job.repair_level)
                    job.write({"technician_id": rec.to_technician_id.id})
            else:
                transfer = self.env["fix.workshop.transfer"].create(
                    {
                        "job_id": job.id,
                        "to_workshop_id": rec.to_workshop_id.id,
                        "reason": "Escalation: %s" % rec.reason,
                    }
                )
                vals["transfer_id"] = transfer.id
            vals.update(
                {
                    "state": "accepted",
                    "decided_by_id": self.env.uid,
                    "decided_at": fields.Datetime.now(),
                    "decision_note": note or False,
                }
            )
            rec._guarded().write(vals)
        return True

    def action_decline(self, note=None):
        for rec in self:
            rec._assert_decider()
            if not (note or "").strip():
                raise UserError("Say why the escalation is declined.")
            rec._guarded().write(
                {
                    "state": "declined",
                    "decided_by_id": self.env.uid,
                    "decided_at": fields.Datetime.now(),
                    "decision_note": note,
                }
            )
            rec.job_id.message_post(body="Escalation declined: %s" % note)
        return True


# ======================================================================
# 5: teardown (FR-WSR-019) and instrument use (FR-WSR-025/040, BRU-WSR-09)
# ======================================================================
class FixWorkshopTeardown(models.Model):
    """Spec entity fix.teardown.record: what was taken off the device, in
    order, and its condition, with a photo where the procedure asks for one."""

    _name = "fix.workshop.teardown"
    _description = "Workshop Teardown Record"
    _inherit = ["fix.guarded.mixin"]
    _order = "job_id, sequence, id"

    job_id = fields.Many2one(
        "fix.workshop.job", string="Repair Job", required=True, index=True, ondelete="restrict"
    )
    sequence = fields.Integer(string="Step", default=10)
    component = fields.Char(string="Component Removed", required=True)
    designator = fields.Char(string="Board Position / Designator")
    condition = fields.Selection(
        [
            ("good", "Good"),
            ("worn", "Worn"),
            ("damaged", "Physically Damaged"),
            ("corroded", "Corroded"),
            ("burnt", "Burnt / Heat Damage"),
            ("liquid", "Liquid Damage"),
            ("missing", "Missing / Previously Replaced"),
        ],
        string="Condition",
        required=True,
    )
    photo_attachment_id = fields.Many2one("ir.attachment", string="Photo")
    note = fields.Text(string="Observation")
    recorded_by_id = fields.Many2one("res.users", string="Recorded By", readonly=True)
    recorded_at = fields.Datetime(string="Recorded At", readonly=True)
    company_id = fields.Many2one(related="job_id.company_id", store=True, readonly=True)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"recorded_by_id", "recorded_at"}

    def _check_open(self, jobs):
        _check_job_open(jobs, "teardown record")
        for job in jobs:
            if job.qc_passed:
                raise UserError("Job %s has passed QC: its teardown is fixed." % job.name)

    @api.model_create_multi
    def create(self, vals_list):
        Job = self.env["fix.workshop.job"]
        for vals in vals_list:
            self._check_open(Job.browse(vals.get("job_id")).exists())
        records = super().create(vals_list)
        records._guarded().write(
            {"recorded_by_id": self.env.uid, "recorded_at": fields.Datetime.now()}
        )
        return records

    def write(self, vals):
        if not self._fix_guard_open():
            self._check_open(self.mapped("job_id"))
            if "job_id" in vals:
                raise UserError("A teardown step stays on the job it was recorded on.")
        return super().write(vals)

    def unlink(self):
        if not self.env.su:
            raise UserError("A teardown step is repair evidence and is never deleted.")
        return super().unlink()


class FixWorkshopInstrumentUse(models.Model):
    """Spec entity fix.equipment.usage at the bench: which instrument was used
    on which repair, from when to when, and whether its calibration was valid
    then. An out-of-calibration use is recorded and flagged, never hidden: the
    job is marked for QC review (BRU-WSR-09), and M45's usage register gets
    the row its impact assessment reads."""

    _name = "fix.workshop.instrument.use"
    _description = "Workshop Instrument Use"
    _inherit = ["fix.guarded.mixin"]
    _order = "used_from desc, id desc"

    job_id = fields.Many2one(
        "fix.workshop.job", string="Repair Job", required=True, index=True, ondelete="restrict"
    )
    equipment_id = fields.Many2one(
        "fix.equipment", string="Instrument", required=True, ondelete="restrict"
    )
    purpose = fields.Char(string="Used For", help="e.g. rail measurement, rework, final test")
    used_from = fields.Datetime(string="Used From", required=True, default=fields.Datetime.now)
    used_to = fields.Datetime(string="Used To")
    hours = fields.Float(string="Hours", compute="_compute_hours", store=True)
    calibration_valid = fields.Boolean(string="Calibration Valid at Use", readonly=True)
    calibration_problem = fields.Char(string="Calibration Problem", readonly=True)
    used_by_id = fields.Many2one("res.users", string="Recorded By", readonly=True)
    usage_id = fields.Many2one("fix.equipment.usage", string="M45 Usage Row", readonly=True)
    company_id = fields.Many2one(related="job_id.company_id", store=True, readonly=True)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "calibration_valid",
            "calibration_problem",
            "used_by_id",
            "usage_id",
        }

    @api.depends("used_from", "used_to")
    def _compute_hours(self):
        for rec in self:
            if rec.used_from and rec.used_to and rec.used_to > rec.used_from:
                rec.hours = round((rec.used_to - rec.used_from).total_seconds() / 3600.0, 2)
            else:
                rec.hours = 0.0

    @api.constrains("used_from", "used_to")
    def _check_times(self):
        for rec in self:
            if rec.used_to and rec.used_from and rec.used_to < rec.used_from:
                raise ValidationError("An instrument use cannot end before it starts.")
            if rec.used_from and rec.used_from > fields.Datetime.now():
                raise ValidationError("A use is recorded once the instrument has been used.")

    @api.model_create_multi
    def create(self, vals_list):
        Job = self.env["fix.workshop.job"]
        for vals in vals_list:
            _check_job_open(Job.browse(vals.get("job_id")).exists(), "instrument use")
        records = super().create(vals_list)
        for rec in records:
            equipment = rec.equipment_id.sudo()
            job = rec.job_id
            day = fields.Datetime.context_timestamp(rec, rec.used_from).date()
            if day == fields.Date.context_today(rec):
                holder = self.env.user.sudo().employee_ids | job.sudo().technician_id
                problem = equipment._m45_fitness_problem(holder=holder)
            else:
                problem = equipment._m45_fitness_problem_on(day)
            usage = self.env["fix.equipment.usage"].m45_record_qc_use(
                equipment,
                job.name,
                "na",
                source=rec,
                service_order_ref=job.sudo().order_id.name or None,
            )
            rec._guarded().write(
                {
                    "calibration_valid": not problem,
                    "calibration_problem": problem or False,
                    "used_by_id": self.env.uid,
                    "usage_id": usage.id or False,
                }
            )
            if problem:
                job._guarded().write({"calibration_review": True})
                job.message_post(
                    body="BRU-WSR-09: %s was used out of calibration (%s). This repair's QC is "
                    "marked for review." % (equipment.name, problem)
                )
        return records

    def write(self, vals):
        # only the end of the use and its purpose are filled in later
        _frozen(self, vals, ("used_to", "purpose"), "An instrument use")
        if not self._fix_guard_open():
            _check_job_open(self.mapped("job_id"), "instrument use")
        return super().write(vals)

    def unlink(self):
        if not self.env.su:
            raise UserError("An instrument use is calibration evidence and is never deleted.")
        return super().unlink()


# ======================================================================
# 6: consumables (FR-WSR-024)
# ======================================================================
class FixWorkshopConsumableUsage(models.Model):
    """Spec entity fix.consumable.usage: solder, flux, paste, adhesive and
    cleaning agents used on a repair, costed at the item's standard cost."""

    _name = "fix.workshop.consumable.usage"
    _description = "Workshop Consumable Usage"
    _inherit = ["fix.guarded.mixin"]
    _order = "id desc"

    job_id = fields.Many2one(
        "fix.workshop.job", string="Repair Job", required=True, index=True, ondelete="restrict"
    )
    product_id = fields.Many2one(
        "product.product", string="Consumable", required=True, ondelete="restrict"
    )
    quantity = fields.Float(string="Quantity", required=True, default=1.0)
    uom_name = fields.Char(related="product_id.uom_id.name", string="Unit", readonly=True)
    unit_cost = fields.Float(string="Unit Cost (BDT)", readonly=True)
    subtotal = fields.Float(string="Cost (BDT)", compute="_compute_subtotal", store=True)
    notes = fields.Char(string="Notes")
    recorded_by_id = fields.Many2one("res.users", string="Recorded By", readonly=True)
    recorded_at = fields.Datetime(string="Recorded At", readonly=True)
    company_id = fields.Many2one(related="job_id.company_id", store=True, readonly=True)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"unit_cost", "recorded_by_id", "recorded_at"}

    @api.depends("quantity", "unit_cost")
    def _compute_subtotal(self):
        for rec in self:
            rec.subtotal = round((rec.quantity or 0.0) * (rec.unit_cost or 0.0), 2)

    @api.constrains("quantity")
    def _check_quantity(self):
        for rec in self:
            if rec.quantity <= 0:
                raise ValidationError("A consumable quantity must be above zero.")

    @api.model_create_multi
    def create(self, vals_list):
        Job = self.env["fix.workshop.job"]
        for vals in vals_list:
            _check_job_open(Job.browse(vals.get("job_id")).exists(), "consumable")
        records = super().create(vals_list)
        for rec in records:
            rec._guarded().write(
                {
                    "unit_cost": rec.product_id.sudo().standard_price or 0.0,
                    "recorded_by_id": self.env.uid,
                    "recorded_at": fields.Datetime.now(),
                }
            )
        return records

    def write(self, vals):
        if not self._fix_guard_open():
            _check_job_open(self.mapped("job_id"), "consumable change")
            if {"job_id", "product_id"} & set(vals):
                raise UserError("Record a new line instead of moving a consumable line.")
        return super().write(vals)

    def unlink(self):
        if not self.env.su:
            _check_job_open(self.mapped("job_id"), "consumable change")
        return super().unlink()


class FixWorkshopPartLineSourceRules(models.Model):
    """BRU-WSR-08 / BRU-WSR-12 (hard rules, not enforced before): OEM warranty
    stock is used only on a warranty repair, and a harvested component never
    on one."""

    _inherit = "fix.workshop.part.line"

    @api.constrains("source_origin", "job_id")
    def _check_source_against_warranty(self):
        for rec in self:
            category = rec.job_id.sudo().order_id.order_category
            if rec.source_origin == "oem_consignment" and category != "warranty":
                raise ValidationError(
                    "BRU-WSR-08: brand-supplied warranty stock cannot be used on job %s, which "
                    "is not a warranty repair." % rec.job_id.name
                )
            if rec.source_origin == "donor_board_harvest" and category == "warranty":
                raise ValidationError(
                    "BRU-WSR-12: a harvested component cannot be used on warranty repair %s."
                    % rec.job_id.name
                )


# ======================================================================
# 7: burn-in stations and runs (FR-WSR-033/034, BRU-WSR-07)
# ======================================================================
class FixWorkshopBurninStation(models.Model):
    """Spec entity fix.burnin.station: a constrained resource. Once a workshop
    has a station, its burn-in runs start at a station."""

    _name = "fix.workshop.burnin.station"
    _description = "Burn-In Station"
    _order = "workshop_id, code"

    workshop_id = fields.Many2one(
        "fix.workshop", string="Workshop", required=True, index=True, ondelete="restrict"
    )
    company_id = fields.Many2one(related="workshop_id.company_id", store=True, readonly=True)
    code = fields.Char(string="Station Code", required=True)
    name = fields.Char(string="Station", required=True)
    capacity = fields.Integer(string="Devices at Once", required=True, default=4)
    load_profile = fields.Char(string="Default Load Profile")
    running_count = fields.Integer(string="Running Now", compute="_compute_running")
    active = fields.Boolean(default=True)

    _code_unique = models.Constraint(
        "unique(workshop_id, code)", "A station code is unique within its workshop."
    )

    def _compute_running(self):
        Session = self.env["fix.workshop.burnin.session"].sudo()
        for rec in self:
            rec.running_count = Session.search_count(
                [("station_id", "=", rec.id), ("outcome", "=", "running")]
            )

    @api.constrains("capacity")
    def _check_capacity(self):
        for rec in self:
            if rec.capacity < 1:
                raise ValidationError("A burn-in station holds at least one device.")

    @api.depends("code", "name")
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = "%s · %s" % (rec.code, rec.name)


class FixWorkshopBurninSession(models.Model):
    """Spec entity fix.burnin.session: one burn-in run of a job at a station.
    Starting it starts the job's burn-in. Its duration is the protocol's (or
    the policy minimum for L2/L3): it may be extended, never shortened
    (BRU-WSR-07). Pass/Fail Burn-In on the job closes it."""

    _name = "fix.workshop.burnin.session"
    _description = "Burn-In Run"
    _inherit = ["fix.guarded.mixin"]
    _order = "started_at desc, id desc"

    job_id = fields.Many2one(
        "fix.workshop.job", string="Repair Job", required=True, index=True, ondelete="restrict"
    )
    station_id = fields.Many2one(
        "fix.workshop.burnin.station", string="Station", required=True, ondelete="restrict"
    )
    load_profile = fields.Char(string="Load Profile")
    required_minutes = fields.Float(string="Required Minutes")
    minimum_minutes = fields.Float(string="Protocol Minimum", readonly=True)
    started_at = fields.Datetime(string="Started At", readonly=True)
    due_at = fields.Datetime(string="Due At", compute="_compute_due", store=True)
    completed_at = fields.Datetime(string="Completed At", readonly=True)
    outcome = fields.Selection(
        [("running", "Running"), ("passed", "Passed"), ("failed", "Failed")],
        string="Outcome",
        default="running",
        required=True,
        readonly=True,
    )
    started_by_id = fields.Many2one("res.users", string="Started By", readonly=True)
    company_id = fields.Many2one(related="job_id.company_id", store=True, readonly=True)

    def _fix_guarded_fields(self) -> set:
        guarded = super()._fix_guarded_fields() | {
            "minimum_minutes",
            "started_at",
            "completed_at",
            "outcome",
            "started_by_id",
        }
        if self:
            guarded |= {"required_minutes", "job_id", "station_id"}
        return guarded

    @api.depends("started_at", "required_minutes")
    def _compute_due(self):
        from datetime import timedelta

        for rec in self:
            rec.due_at = (
                rec.started_at + timedelta(minutes=rec.required_minutes or 0.0)
                if rec.started_at
                else False
            )

    def _minimum_for(self, job):
        minimum = 0.0
        if job.repair_level in ("l2", "l3"):
            minimum = job._m31_burn_in_min_minutes()
        protocol_minutes = job.sudo().test_result_ids.mapped("protocol_id.burn_in_minutes")
        return max([minimum, *[float(m or 0) for m in protocol_minutes]])

    @api.model_create_multi
    def create(self, vals_list):
        Job = self.env["fix.workshop.job"]
        Station = self.env["fix.workshop.burnin.station"]
        for vals in vals_list:
            job = Job.browse(vals.get("job_id")).exists()
            station = Station.browse(vals.get("station_id")).exists()
            if not job or not station:
                raise UserError("Choose the job and the burn-in station.")
            _check_job_open(job, "burn-in run")
            if station.sudo().workshop_id != job.workshop_id:
                raise UserError(
                    "Station %s is in %s, not in the job's workshop."
                    % (station.code, station.sudo().workshop_id.name)
                )
            if not station.active:
                raise UserError("Station %s is archived." % station.code)
            running = self.sudo().search_count(
                [("station_id", "=", station.id), ("outcome", "=", "running")]
            )
            if running >= station.capacity:
                raise UserError(
                    "Station %s is full: %d of %d devices are running."
                    % (station.code, running, station.capacity)
                )
            minimum = self._minimum_for(job)
            required = float(vals.get("required_minutes") or 0.0) or minimum
            if required < minimum:
                raise UserError(
                    "BRU-WSR-07: burn-in cannot be shortened below the protocol's %.0f minutes."
                    % minimum
                )
            vals["required_minutes"] = required
            vals.setdefault("load_profile", station.load_profile or False)
            vals["_minimum"] = minimum
        minimums = [vals.pop("_minimum") for vals in vals_list]
        records = super().create(vals_list)
        for rec, minimum in zip(records, minimums, strict=True):
            rec.job_id.with_context(m31_burnin_station=True).action_start_burn_in()
            rec._guarded().write(
                {
                    "minimum_minutes": minimum,
                    "started_at": rec.job_id.burn_in_started_at or fields.Datetime.now(),
                    "started_by_id": self.env.uid,
                }
            )
            rec.job_id.message_post(
                body="Burn-in started at station %s for %.0f minutes."
                % (rec.station_id.code, rec.required_minutes)
            )
        return records

    def action_extend(self, minutes=0.0):
        """Extension is permitted, reduction is not (BRU-WSR-07)."""
        try:
            minutes = float(minutes or 0.0)
        except (TypeError, ValueError):
            minutes = 0.0
        for rec in self:
            if rec.outcome != "running":
                raise UserError("Only a running burn-in is extended.")
            if minutes <= 0:
                raise UserError("Give the extra minutes; a burn-in is never shortened.")
            rec._guarded().write({"required_minutes": rec.required_minutes + minutes})
            rec.job_id.message_post(body="Burn-in extended by %.0f minutes." % minutes)
        return True

    def write(self, vals):
        if not self._fix_guard_open() and any(r.outcome != "running" for r in self):
            raise UserError("A finished burn-in run is not edited.")
        return super().write(vals)

    def unlink(self):
        if not self.env.su:
            raise UserError("A burn-in run is never deleted.")
        return super().unlink()


# ======================================================================
# 8: internal rework (FR-WSR-038, BRU-WSR-10) and transfers (FR-WSR-016, BRU-WSR-14)
# ======================================================================
class FixWorkshopRework(models.Model):
    """Spec entity fix.workshop.rework: one internal rework loop, written by
    Fail QC and Fail Burn-In. Counted separately from customer comebacks and
    never hidden: no one edits or deletes it."""

    _name = "fix.workshop.rework"
    _description = "Internal Rework Loop"
    _order = "raised_at desc, id desc"

    job_id = fields.Many2one(
        "fix.workshop.job", string="Repair Job", required=True, index=True, ondelete="restrict"
    )
    iteration = fields.Integer(string="Loop No.", readonly=True)
    failed_at_state = fields.Selection(
        [("burn_in", "Burn-In"), ("qc", "Quality Control")],
        string="Failed At",
        readonly=True,
    )
    reason = fields.Text(string="Failure Reason", readonly=True)
    attributed_to_id = fields.Many2one("hr.employee", string="Repairing Technician", readonly=True)
    repair_level = fields.Char(string="Level", readonly=True)
    raised_by_id = fields.Many2one("res.users", string="Recorded By", readonly=True)
    raised_at = fields.Datetime(string="Recorded At", readonly=True)
    company_id = fields.Many2one(related="job_id.company_id", store=True, readonly=True)

    def write(self, vals):
        if not self.env.su:
            raise UserError("BRU-WSR-10: internal rework is never edited or hidden.")
        return super().write(vals)

    def unlink(self):
        if not self.env.su:
            raise UserError("BRU-WSR-10: internal rework is never deleted.")
        return super().unlink()


class FixWorkshopTransfer(models.Model):
    """A repair order moved to another workshop for a specialist stage. The
    receiving workshop confirms it, which raises the M03 consignment for the
    move and hands the job over (BRU-WSR-14). The receiving side then records
    the arrival."""

    _name = "fix.workshop.transfer"
    _description = "Workshop Transfer"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "requested_at desc, id desc"

    job_id = fields.Many2one(
        "fix.workshop.job", string="Repair Job", required=True, index=True, ondelete="restrict"
    )
    from_workshop_id = fields.Many2one("fix.workshop", string="From Workshop", readonly=True)
    to_workshop_id = fields.Many2one(
        "fix.workshop", string="Receiving Workshop", required=True, ondelete="restrict"
    )
    stage = fields.Char(string="Specialist Stage", help="e.g. BGA reballing, L3 board repair")
    reason = fields.Text(string="Why Transfer", required=True)
    state = fields.Selection(
        [
            ("requested", "Awaiting Receiving Workshop"),
            ("in_transit", "Confirmed · In Transit"),
            ("received", "Received"),
            ("declined", "Declined"),
            ("cancelled", "Cancelled"),
        ],
        string="Status",
        default="requested",
        required=True,
        readonly=True,
        tracking=True,
    )
    consignment_id = fields.Many2one("fix.consignment", string="M03 Consignment", readonly=True)
    requested_by_id = fields.Many2one("res.users", string="Requested By", readonly=True)
    requested_at = fields.Datetime(string="Requested At", readonly=True)
    confirmed_by_id = fields.Many2one("res.users", string="Confirmed By", readonly=True)
    confirmed_at = fields.Datetime(string="Confirmed At", readonly=True)
    received_by_id = fields.Many2one("res.users", string="Received By", readonly=True)
    received_at = fields.Datetime(string="Received At", readonly=True)
    decline_note = fields.Text(string="Decline / Cancel Note", readonly=True)
    company_id = fields.Many2one(related="job_id.company_id", store=True, readonly=True)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "from_workshop_id",
            "state",
            "consignment_id",
            "requested_by_id",
            "requested_at",
            "confirmed_by_id",
            "confirmed_at",
            "received_by_id",
            "received_at",
            "decline_note",
        }

    @api.model_create_multi
    def create(self, vals_list):
        Job = self.env["fix.workshop.job"]
        for vals in vals_list:
            job = Job.browse(vals.get("job_id")).exists()
            if not job:
                raise UserError("Choose the repair job to transfer.")
            _check_job_open(job, "transfer")
            if job.state not in TRANSFERABLE_STATES:
                raise UserError(
                    "Job %s is on the bench (%s): its technician and QC are fixed. Put it to "
                    "Wait for Parts before transferring it." % (job.name, job.state)
                )
            if vals.get("to_workshop_id") == job.workshop_id.id:
                raise UserError("The receiving workshop must be another workshop.")
            if not (vals.get("reason") or "").strip():
                raise UserError("Say why the job moves to another workshop.")
            if self.search_count(
                [("job_id", "=", job.id), ("state", "in", ("requested", "in_transit"))]
            ):
                raise UserError("Job %s already has a transfer under way." % job.name)
        records = super().create(vals_list)
        for rec in records:
            rec._guarded().write(
                {
                    "from_workshop_id": rec.job_id.workshop_id.id,
                    "requested_by_id": self.env.uid,
                    "requested_at": fields.Datetime.now(),
                }
            )
            rec.job_id.message_post(
                body="Transfer to %s requested: %s" % (rec.to_workshop_id.name, rec.reason)
            )
        return records

    def write(self, vals):
        if not self._fix_guard_open() and any(r.state != "requested" for r in self):
            raise UserError("A confirmed or closed transfer is not edited.")
        return super().write(vals)

    def unlink(self):
        if not self.env.su:
            raise UserError("A transfer is never deleted; cancel it instead.")
        return super().unlink()

    def _is_receiving_side(self):
        self.ensure_one()
        if self.env.su:
            return True
        manager = self.to_workshop_id.sudo().manager_id
        return _is_supervisor(self.env) or (manager and manager == self.env.user)

    def action_confirm(self):
        """The receiving workshop accepts the job: the consignment is raised and
        the job moves, off its old bench and out of its old location."""
        for rec in self:
            if rec.state != "requested":
                raise UserError("Only a requested transfer is confirmed.")
            if not rec._is_receiving_side():
                raise UserError(
                    "BRU-WSR-14: the receiving workshop confirms a transfer (its manager or a "
                    "workshop supervisor)."
                )
            if rec.requested_by_id == self.env.user and not self.env.su:
                raise UserError("The person who requested a transfer does not confirm it.")
            job = rec.job_id
            if job.state not in TRANSFERABLE_STATES:
                raise UserError("Job %s went back on the bench: it cannot move now." % job.name)
            src, dst = rec.from_workshop_id.sudo(), rec.to_workshop_id.sudo()
            consignment = (
                self.env["fix.consignment"]
                .sudo()
                .create(
                    {
                        "consignment_type": "branch_transfer",
                        "scheduled_date": fields.Datetime.now(),
                        "origin_branch_id": src.branch_id.id or False,
                        "dest_branch_id": dst.branch_id.id or False,
                        "service_order_id": job.sudo().order_id.id or False,
                        "company_id": job.company_id.id,
                    }
                )
            )
            old_bench = job.bench_id
            move = {"workshop_id": dst.id, "bench_id": False, "current_location_id": False}
            if job.state not in TECHNICIAN_LOCKED_STATES:
                move["technician_id"] = False
            job.with_context(m31_workshop_transfer=True)._guarded().write(move)
            if old_bench:
                old_bench.sudo()._compute_job_count()
            rec._guarded().write(
                {
                    "state": "in_transit",
                    "consignment_id": consignment.id,
                    "confirmed_by_id": self.env.uid,
                    "confirmed_at": fields.Datetime.now(),
                }
            )
            job.message_post(
                body="Transferred to %s on consignment %s." % (dst.name, consignment.name)
            )
        return True

    def action_receive(self):
        for rec in self:
            if rec.state != "in_transit":
                raise UserError("Only a transfer in transit is received.")
            if not rec._is_receiving_side() and not self.env.user.has_group(
                "cd_workshop.group_fix_workshop_user"
            ):
                raise UserError("The receiving workshop records the arrival.")
            rec._guarded().write(
                {
                    "state": "received",
                    "received_by_id": self.env.uid,
                    "received_at": fields.Datetime.now(),
                }
            )
            rec.job_id.message_post(body="Received at %s." % rec.to_workshop_id.name)
        return True

    def action_decline(self, note=None):
        for rec in self:
            if rec.state != "requested":
                raise UserError("Only a requested transfer is declined.")
            if not rec._is_receiving_side():
                raise UserError("The receiving workshop declines a transfer.")
            if not (note or "").strip():
                raise UserError("Say why the transfer is declined.")
            rec._guarded().write({"state": "declined", "decline_note": note})
        return True

    def action_cancel(self, note=None):
        for rec in self:
            if rec.state != "requested":
                raise UserError("Only a requested transfer is cancelled.")
            if rec.requested_by_id != self.env.user and not _is_supervisor(self.env):
                raise UserError("The requester or a supervisor cancels a transfer.")
            rec._guarded().write({"state": "cancelled", "decline_note": note or False})
        return True


# ======================================================================
# 9: the work clock (FR-WSR-026) and the cost build-up (FR-WSR-043/044)
# ======================================================================
class FixWorkshopTimeLog(models.Model):
    """One segment of a technician's time on a job: started now, stopped
    later, active work or waiting. Booked as the work proceeds (SOP SP-010
    step 10), never typed afterwards."""

    _name = "fix.workshop.time.log"
    _description = "Workshop Labour Time Segment"
    _inherit = ["fix.guarded.mixin"]
    _order = "started_at desc, id desc"

    job_id = fields.Many2one(
        "fix.workshop.job", string="Repair Job", required=True, index=True, ondelete="restrict"
    )
    technician_id = fields.Many2one("hr.employee", string="Technician", readonly=True, index=True)
    activity = fields.Selection(
        [("active", "Active Work"), ("waiting", "Waiting (parts, instrument, decision)")],
        string="Activity",
        required=True,
        default="active",
    )
    started_at = fields.Datetime(string="Started", readonly=True)
    ended_at = fields.Datetime(string="Stopped", readonly=True)
    minutes = fields.Float(string="Minutes", compute="_compute_minutes", store=True)
    running = fields.Boolean(string="Running", compute="_compute_minutes", store=True)
    note = fields.Char(string="Note")
    company_id = fields.Many2one(related="job_id.company_id", store=True, readonly=True)

    def _fix_guarded_fields(self) -> set:
        guarded = super()._fix_guarded_fields() | {"technician_id", "started_at", "ended_at"}
        if self:
            guarded |= {"job_id", "activity"}
        return guarded

    @api.depends("started_at", "ended_at")
    def _compute_minutes(self):
        for rec in self:
            rec.running = bool(rec.started_at and not rec.ended_at)
            if rec.started_at and rec.ended_at:
                rec.minutes = round((rec.ended_at - rec.started_at).total_seconds() / 60.0, 1)
            else:
                rec.minutes = 0.0

    @api.model_create_multi
    def create(self, vals_list):
        Job = self.env["fix.workshop.job"]
        employee = self.env.user.employee_id
        if not employee and not self.env.su:
            raise UserError("Your user has no employee record, so it has no work clock.")
        for vals in vals_list:
            job = Job.browse(vals.get("job_id")).exists()
            _check_job_open(job, "time booking")
            if job.state == "draft":
                raise UserError("Job %s is not booked in yet." % job.name)
            open_log = self.sudo().search(
                [("technician_id", "=", employee.id), ("running", "=", True)], limit=1
            )
            if open_log:
                raise UserError(
                    "Your clock is running on %s: stop it before starting another."
                    % open_log.job_id.name
                )
        records = super().create(vals_list)
        records._guarded().write(
            {"technician_id": employee.id or False, "started_at": fields.Datetime.now()}
        )
        return records

    def action_stop(self, note=None):
        for rec in self:
            if not rec.running:
                raise UserError("This clock is already stopped.")
            if rec.technician_id != self.env.user.employee_id and not _is_supervisor(self.env):
                raise UserError("A technician stops his own clock (or a supervisor does).")
            vals = {"ended_at": fields.Datetime.now()}
            if note:
                vals["note"] = note
            rec._guarded().write(vals)
            rec.job_id._m31_sync_logged_minutes()
        return True

    def write(self, vals):
        plain = set(vals) - self._fix_guarded_fields()
        if plain and not self._fix_guard_open() and any(not r.running for r in self):
            raise UserError("A stopped time segment is the labour record and is not edited.")
        return super().write(vals)

    def unlink(self):
        if not self.env.su:
            raise UserError("Labour time is never deleted.")
        return super().unlink()


class FixWorkshopCostLine(models.Model):
    """Spec entity fix.repair.cost.line: the cost build-up of a repair, written
    by Build Cost Sheet from what the job recorded."""

    _name = "fix.workshop.cost.line"
    _description = "Repair Cost Build-Up Line"
    _order = "job_id, sequence, id"

    job_id = fields.Many2one(
        "fix.workshop.job", string="Repair Job", required=True, index=True, ondelete="cascade"
    )
    sequence = fields.Integer(default=10)
    cost_type = fields.Selection(
        [
            ("labour", "Labour"),
            ("parts", "Components"),
            ("consumables", "Consumables"),
            ("equipment", "Equipment Time"),
            ("overhead", "Overhead Absorption"),
        ],
        string="Cost Type",
        readonly=True,
    )
    description = fields.Char(string="Basis", readonly=True)
    quantity = fields.Float(string="Quantity", readonly=True)
    rate = fields.Float(string="Rate", readonly=True)
    amount = fields.Float(string="Amount (BDT)", readonly=True)
    built_at = fields.Datetime(string="Built At", readonly=True)
    company_id = fields.Many2one(related="job_id.company_id", store=True, readonly=True)

    def write(self, vals):
        if not self.env.su:
            raise UserError("A cost line is derived: rebuild the cost sheet instead.")
        return super().write(vals)


# ======================================================================
# the job side
# ======================================================================
class FixWorkshopJobCapture2(models.Model):
    _inherit = "fix.workshop.job"

    current_location_id = fields.Many2one(
        "fix.workshop.location", string="Current Location", readonly=True, tracking=True
    )
    high_value_device = fields.Boolean(
        string="High-Value Device",
        tracking=True,
        help="Held overnight in the secure store (BRU-WSR-13). A job whose approved amount "
        "reaches the high-value threshold counts as high value too.",
    )
    calibration_review = fields.Boolean(
        string="QC Marked for Review (instrument out of calibration)", readonly=True
    )
    teardown_ids = fields.One2many("fix.workshop.teardown", "job_id", string="Teardown")
    instrument_use_ids = fields.One2many(
        "fix.workshop.instrument.use", "job_id", string="Instruments Used"
    )
    consumable_ids = fields.One2many(
        "fix.workshop.consumable.usage", "job_id", string="Consumables"
    )
    time_log_ids = fields.One2many("fix.workshop.time.log", "job_id", string="Time Booked")
    rework_ids = fields.One2many("fix.workshop.rework", "job_id", string="Rework Loops")
    cost_line_ids = fields.One2many("fix.workshop.cost.line", "job_id", string="Cost Build-Up")
    logged_active_minutes = fields.Float(string="Clocked Active Minutes", compute="_compute_clock")
    logged_waiting_minutes = fields.Float(
        string="Clocked Waiting Minutes", compute="_compute_clock"
    )
    consumables_total = fields.Float(string="Consumables (BDT)", compute="_compute_full_cost")
    full_cost = fields.Float(string="Full Repair Cost (BDT)", compute="_compute_full_cost")
    cost_variance = fields.Float(string="Cost vs Approved (BDT)", compute="_compute_full_cost")
    cost_variance_flag = fields.Boolean(
        string="Variance Beyond Tolerance", compute="_compute_full_cost"
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"current_location_id", "calibration_review"}

    @api.depends("time_log_ids.minutes", "time_log_ids.activity")
    def _compute_clock(self):
        for rec in self:
            logs = rec.time_log_ids
            rec.logged_active_minutes = sum(
                logs.filtered(lambda t: t.activity == "active").mapped("minutes")
            )
            rec.logged_waiting_minutes = sum(
                logs.filtered(lambda t: t.activity == "waiting").mapped("minutes")
            )

    @api.depends("cost_line_ids.amount", "consumable_ids.subtotal", "estimate_ceiling")
    def _compute_full_cost(self):
        tolerance = _param_float(self.env, COST_TOLERANCE_PARAM, COST_TOLERANCE_DEFAULT)
        for rec in self:
            rec.consumables_total = sum(rec.consumable_ids.mapped("subtotal"))
            rec.full_cost = sum(rec.cost_line_ids.mapped("amount"))
            approved = rec.estimate_ceiling or 0.0
            rec.cost_variance = rec.full_cost - approved if (approved and rec.full_cost) else 0.0
            rec.cost_variance_flag = bool(
                approved and rec.full_cost and rec.cost_variance > approved * tolerance / 100.0
            )

    def _m31_sync_logged_minutes(self):
        """The clock is the labour record once it is used (FR-WSR-026)."""
        for rec in self:
            if rec.state in CLOSED_JOB_STATES:
                continue
            rec.sudo().write({"actual_logged_minutes": rec.logged_active_minutes})

    def write(self, vals):
        # BRU-WSR-14: once booked into a workshop, a job moves to another only
        # by a confirmed Workshop Transfer, which raises the consignment
        if (
            "workshop_id" in vals
            and not self.env.su
            and not self.env.context.get("m31_workshop_transfer")
        ):
            for rec in self:
                if rec.state != "draft" and rec._fix_guard_differs(
                    "workshop_id", vals["workshop_id"], rec.workshop_id
                ):
                    raise UserError(
                        "BRU-WSR-14: job %s is booked into %s. It moves to another workshop only "
                        "by a Workshop Transfer, confirmed by the receiving workshop with its "
                        "logistics consignment (Rework & Transfers page)."
                        % (rec.name, rec.workshop_id.name)
                    )
        return super().write(vals)

    # --- 3: the hand-over record behind every allocation ---------------------
    def action_allocate_bench(self, bench_id=None, technician_id=None, note=None):
        self.ensure_one()
        before = (self.bench_id, self.technician_id, self.state)
        # FR-WSR-015: a job already on a bench that changes bench or
        # technician is a hand-over, and a hand-over carries its note
        handover = before[0] and (
            (bench_id and int(bench_id) != before[0].id)
            or (technician_id and int(technician_id) != before[1].id)
        )
        if handover and not (note or "").strip():
            raise UserError(
                "Job %s is on bench %s: moving it is a hand-over. Write the hand-over note: "
                "where the work stands and what the next technician must know."
                % (self.name, before[0].code)
            )
        res = super().action_allocate_bench(
            bench_id=bench_id, technician_id=technician_id, note=note
        )
        if (self.bench_id, self.technician_id) != before[:2]:
            self.env["fix.workshop.bench.handover"].sudo().create(
                {
                    "job_id": self.id,
                    "from_bench_id": before[0].id or False,
                    "to_bench_id": self.bench_id.id or False,
                    "from_technician_id": before[1].id or False,
                    "to_technician_id": self.technician_id.id or False,
                    "job_state": before[2],
                    "note": (note or "").strip() or False,
                    "recorded_by_id": self.env.uid,
                    "occurred_at": fields.Datetime.now(),
                }
            )
        return res

    # --- 7: burn-in at a station -----------------------------------------------
    def _m31_open_burnin_session(self):
        self.ensure_one()
        return (
            self.env["fix.workshop.burnin.session"]
            .sudo()
            .search([("job_id", "=", self.id), ("outcome", "=", "running")], limit=1)
        )

    def action_start_burn_in(self):
        if not self.env.context.get("m31_burnin_station"):
            Station = self.env["fix.workshop.burnin.station"].sudo()
            for rec in self:
                if Station.search_count([("workshop_id", "=", rec.workshop_id.id)]):
                    raise UserError(
                        "Workshop %s runs burn-in at its stations (FR-WSR-034): start job %s "
                        "with Start Burn-In at a Station." % (rec.workshop_id.name, rec.name)
                    )
        return super().action_start_burn_in()

    def action_pass_burn_in(self):
        for rec in self:
            session = rec._m31_open_burnin_session()
            if session and rec.burn_in_started_at:
                elapsed = (fields.Datetime.now() - rec.burn_in_started_at).total_seconds() / 60.0
                if elapsed < session.required_minutes:
                    raise UserError(
                        "BRU-WSR-07: job %s's burn-in at %s runs %.0f minutes (running: %.0f)."
                        % (rec.name, session.station_id.code, session.required_minutes, elapsed)
                    )
        res = super().action_pass_burn_in()
        self._m31_close_burnin("passed")
        return res

    def action_fail_burn_in(self, reason=""):
        sessions = {rec.id: rec._m31_open_burnin_session() for rec in self}
        res = super().action_fail_burn_in(reason=reason)
        self._m31_close_burnin("failed", sessions)
        for rec in self:
            rec._m31_record_rework("burn_in", reason)
        return res

    def _m31_close_burnin(self, outcome, sessions=None):
        for rec in self:
            session = (sessions or {}).get(rec.id) or rec._m31_open_burnin_session()
            if session:
                session._guarded().write(
                    {
                        "outcome": outcome,
                        "completed_at": rec.burn_in_completed_at or fields.Datetime.now(),
                    }
                )

    # --- 8: the rework record behind every failure -----------------------------
    def action_fail_qc(self, reason=""):
        res = super().action_fail_qc(reason=reason)
        for rec in self:
            rec._m31_record_rework("qc", reason)
        return res

    def _m31_record_rework(self, at_state, reason):
        self.ensure_one()
        Rework = self.env["fix.workshop.rework"].sudo()
        Rework.create(
            {
                "job_id": self.id,
                "iteration": Rework.search_count([("job_id", "=", self.id)]) + 1,
                "failed_at_state": at_state,
                "reason": reason or False,
                "attributed_to_id": self.technician_id.id or False,
                "repair_level": (self.repair_level or "").upper(),
                "raised_by_id": self.env.uid,
                "raised_at": fields.Datetime.now(),
            }
        )

    # --- 5: an out-of-calibration repair marks its QC for review ---------------
    def action_pass_qc(self, notes=""):
        res = super().action_pass_qc(notes=notes)
        for rec in self.filtered("calibration_review"):
            rec.message_post(
                body="BRU-WSR-09: this QC pass is marked for review: an instrument used on the "
                "repair was out of calibration."
            )
        return res

    # --- 9: the cost build-up --------------------------------------------------
    def action_build_cost_sheet(self):
        """FR-WSR-043/044: labour minutes at the workshop rate, components,
        consumables, equipment time and overhead, from what the job recorded."""
        Line = self.env["fix.workshop.cost.line"].sudo()
        now = fields.Datetime.now()
        for rec in self:
            ws = rec.workshop_id.sudo()
            minutes = rec.logged_active_minutes or rec.actual_logged_minutes or 0.0
            lines = []
            if ws.labour_rate_per_hour:
                lines.append(
                    (
                        "labour",
                        "%.0f active minutes at the workshop rate" % minutes,
                        round(minutes / 60.0, 2),
                        ws.labour_rate_per_hour,
                        round(minutes / 60.0 * ws.labour_rate_per_hour, 2),
                    )
                )
            else:
                lines.append(
                    (
                        "labour",
                        "Recorded labour figure (the workshop has no hourly rate)",
                        1.0,
                        rec.labour_total or 0.0,
                        rec.labour_total or 0.0,
                    )
                )
            parts = rec.sudo().part_line_ids
            lines.append(
                (
                    "parts",
                    "%d part line(s) at standard cost" % len(parts),
                    float(len(parts)),
                    0.0,
                    round(sum(parts.mapped("subtotal")), 2),
                )
            )
            cons = rec.sudo().consumable_ids
            lines.append(
                (
                    "consumables",
                    "%d consumable line(s)" % len(cons),
                    float(len(cons)),
                    0.0,
                    round(sum(cons.mapped("subtotal")), 2),
                )
            )
            hours = sum(rec.sudo().instrument_use_ids.mapped("hours"))
            lines.append(
                (
                    "equipment",
                    "%.2f instrument hours" % hours,
                    hours,
                    ws.equipment_rate_per_hour or 0.0,
                    round(hours * (ws.equipment_rate_per_hour or 0.0), 2),
                )
            )
            direct = sum(line[4] for line in lines)
            pct = ws.overhead_pct or 0.0
            lines.append(
                (
                    "overhead",
                    "%.1f%% of direct cost" % pct,
                    direct,
                    pct,
                    round(direct * pct / 100.0, 2),
                )
            )
            rec.sudo().cost_line_ids.unlink()
            Line.create(
                [
                    {
                        "job_id": rec.id,
                        "sequence": i * 10,
                        "cost_type": t,
                        "description": d,
                        "quantity": q,
                        "rate": r,
                        "amount": a,
                        "built_at": now,
                    }
                    for i, (t, d, q, r, a) in enumerate(lines, start=1)
                ]
            )
            rec.invalidate_recordset(["cost_line_ids", "full_cost", "cost_variance"])
            body = [escape("Cost sheet built: %.2f BDT" % rec.full_cost)]
            if rec.cost_variance_flag:
                body.append(
                    escape(
                        "Variance %.2f BDT above the approved %.2f exceeds the tolerance."
                        % (rec.cost_variance, rec.estimate_ceiling)
                    )
                )
            rec.message_post(body=Markup("<br/>").join(body))
        return True


class FixWorkshopCostRates(models.Model):
    _inherit = "fix.workshop"

    labour_rate_per_hour = fields.Float(
        string="Labour Rate (BDT / hour)", tracking=True, help="FR-WSR-043: the applicable rate."
    )
    equipment_rate_per_hour = fields.Float(string="Equipment Rate (BDT / hour)", tracking=True)
    overhead_pct = fields.Float(string="Overhead Absorption (%)", tracking=True)
    location_ids = fields.One2many("fix.workshop.location", "workshop_id", string="Locations")
    burnin_station_ids = fields.One2many(
        "fix.workshop.burnin.station", "workshop_id", string="Burn-In Stations"
    )
