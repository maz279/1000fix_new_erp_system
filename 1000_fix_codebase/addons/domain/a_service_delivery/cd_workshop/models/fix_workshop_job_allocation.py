"""M31 sub-module 3 "Bench Allocation & Queue" (FR-WSR-011 / 015, BRU-WSR-02 / 06).

The page's capture button created a new BENCH (master data) under the
registry name "Bench Allocation", so allocating a repair job to a bench and
a technician had no capture anywhere (M31 audit, 14 Nov 2026). This adds
the allocation itself, and closes the way round it: the Job Routing form
wrote ``bench_id`` directly, which put a job on a bench under maintenance,
a full bench or a bench below the job's level without a word.
"""

from markupsafe import Markup, escape
from odoo import fields, models
from odoo.exceptions import UserError

from .fix_workshop_job import (
    CLOSED_JOB_STATES,
    ROUTING_LOCKED_FIELDS,
    TECHNICIAN_LOCKED_STATES,
)

# a bench's active load (the states fix.workshop.bench.active_job_ids counts).
# A02 ERP audit M31-F18: a job that failed QC keeps its bench for the rework
# (it goes back to in_repair on it), so it holds the bench's capacity; it was
# not counted and the bench was booked to a second job meanwhile.
ACTIVE_BENCH_STATES = (
    "intake",
    "diagnostic",
    "waiting_parts",
    "in_repair",
    "burn_in",
    "qc_pending",
    "qc_failed",
)
LEVEL_RANK = {"l1": 1, "l2": 2, "l3": 3}


class FixWorkshopJobAllocation(models.Model):
    _inherit = "fix.workshop.job"

    bench_handover_note = fields.Text(
        string="Allocation / Hand-over Note",
        tracking=True,
        help="Why the job went to this bench and technician, and what the next "
        "technician must know (FR-WSR-015). Written by Allocate to Bench.",
    )

    def _m31_bench_fit_error(self, bench, workshop, level):
        """Why ``bench`` cannot take this job, or None. The same rules the
        bench's own assignment checks, plus the workshop: a bench belongs to
        one workshop and a job moves workshop on Job Routing first."""
        self.ensure_one()
        bench = bench.sudo()
        if bench.state in ("maintenance", "offline"):
            return "Bench %s is %s." % (
                bench.code,
                dict(bench._fields["state"].selection).get(bench.state, bench.state),
            )
        if workshop and bench.workshop_id != workshop:
            return (
                "Bench %s belongs to %s, not to the job's workshop %s. Move the job on "
                "Job Routing first, or choose a bench of %s."
                % (bench.code, bench.workshop_id.name, workshop.name, workshop.name)
            )
        if LEVEL_RANK.get(bench.repair_level, 0) < LEVEL_RANK.get(level, 0):
            return "Job %s needs %s capability; bench %s is %s only." % (
                self.name,
                (level or "").upper(),
                bench.code,
                (bench.repair_level or "").upper(),
            )
        others = self.sudo().search_count(
            [
                ("bench_id", "=", bench.id),
                ("state", "in", ACTIVE_BENCH_STATES),
                ("id", "!=", self.id or 0),
            ]
        )
        if others >= bench.max_concurrent_jobs:
            return "Bench %s is full: %d of %d jobs." % (
                bench.code,
                others,
                bench.max_concurrent_jobs,
            )
        return None

    def write(self, vals):
        # A plain write of the bench (Job Routing form, imports) goes through
        # the same fit rules as an allocation. Guarded service code is trusted.
        watched = {"bench_id", "workshop_id", "repair_level"} & set(vals)
        if self and watched and not self._fix_guard_open():
            Bench = self.env["fix.workshop.bench"]
            Workshop = self.env["fix.workshop"]
            for rec in self:
                changed = {n for n in watched if rec._fix_guard_differs(n, vals[n], rec[n])}
                if not changed:
                    continue
                if rec.state in TECHNICIAN_LOCKED_STATES and changed & ROUTING_LOCKED_FIELDS:
                    # the job's own lock refuses this change with its reason
                    continue
                bench = Bench.browse(vals["bench_id"]) if "bench_id" in vals else rec.bench_id
                if not bench:
                    continue
                workshop = (
                    Workshop.browse(vals["workshop_id"])
                    if "workshop_id" in vals
                    else rec.workshop_id
                )
                level = vals.get("repair_level", rec.repair_level)
                error = rec._m31_bench_fit_error(bench, workshop, level)
                if error:
                    raise UserError("Job %s cannot go on that bench: %s" % (rec.name, error))
        return super().write(vals)

    def action_allocate_bench(self, bench_id=None, technician_id=None, note=None):
        """Allocate this job to a bench and a technician (FR-WSR-011).

        Re-allocating a job is the hand-over (FR-WSR-015): the previous bench
        is freed, and the note says why, kept on the job and in its chatter.
        The technician must be certified for the job's level (BRU-WSR-02);
        once the job is under way its technician is fixed (QC independence).
        """
        self.ensure_one()
        if not bench_id:
            raise UserError("Choose the bench the job goes to.")
        if self.state in CLOSED_JOB_STATES:
            raise UserError(
                "Job %s is closed: a closed job is the record of the repair." % self.name
            )
        bench = self.env["fix.workshop.bench"].browse(int(bench_id)).exists()
        if not bench:
            raise UserError("That bench no longer exists.")
        technician = self.env["hr.employee"].browse(int(technician_id)) if technician_id else None
        if (
            technician
            and technician != self.technician_id
            and self.state in TECHNICIAN_LOCKED_STATES
        ):
            raise UserError(
                "Job %s is under way: its technician is fixed (QC independence and the "
                "approved estimate are checked against them)." % self.name
            )
        error = self._m31_bench_fit_error(bench, self.workshop_id, self.repair_level)
        if error:
            raise UserError("Job %s cannot go on that bench: %s" % (self.name, error))

        previous_bench, previous_tech = self.bench_id, self.technician_id
        # the technician named here; else, for a job not yet under way with
        # nobody on it, the one stationed at the bench (as the auto-assign does)
        target_tech = technician or previous_tech
        if not target_tech and self.state not in TECHNICIAN_LOCKED_STATES:
            target_tech = bench.sudo().technician_id
        if target_tech and target_tech != previous_tech:
            self._check_technician_certification(target_tech, self.repair_level)

        vals = {"bench_id": bench.id, "bench_handover_note": (note or "").strip() or False}
        if target_tech and target_tech != previous_tech:
            vals["technician_id"] = target_tech.id
        self.write(vals)
        if previous_bench != bench:
            for b in (previous_bench | bench).sudo():
                b._compute_job_count()
            bench.sudo()._emit_bench_assigned(self)

        lines = ["Allocated to bench %s" % bench.code]
        if previous_bench and previous_bench != bench:
            lines[0] += " (from %s)" % previous_bench.code
        if self.technician_id != previous_tech:
            lines.append(
                "Technician: %s → %s"
                % (previous_tech.name or "none", self.technician_id.name or "none")
            )
        if note:
            lines.append("Note: %s" % note.strip())
        self.message_post(body=Markup("<br/>").join(escape(line) for line in lines))
        return True
