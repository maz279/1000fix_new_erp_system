"""A02 ERP audit, pass 2 (20 Nov 2026) - M31 Workshop & Depot Repair,
findings M31-01..M31-09 on the job (the reports and the job card are in
cd_p03_portal).

  M31-01  the repair level and the technician are fixed while the job waits
          for parts or is back from a failed QC; a supervisor revises the
          level (action_revise_level, event workshop.job.level_revised) and
          the level never drops once the repair started. QC's segregation of
          duties is held against everyone who booked time or parts on it.
  M31-02  the bench RELEASES a QC-passed job to the front desk (state
          'released', outgoing staging); the customer hand-over is M01's and
          the job closes when M01 delivers the order
          (consume_service_order_delivered).
  M31-03  a job is the work of a service order, a refurbishment (M14) or an
          M45 work order: it is not created or booked in without one, and
          its order is never cleared.
  M31-04  QC passes on the job's own test protocol: every step's latest
          result passed, and dated after the burn-in; the burn-in lasts the
          protocol's minutes (an L1 protocol that sets minutes too).
  M31-06  the labour rate is stored on each time segment; clocks stop when
          the job goes to QC or closes; no clock starts in QC; a supervisor
          corrects a segment with a reason.
  M31-08  cancel is a supervisor's, with the reason; M01 hears of it,
          reservations are released and M15 issues returned BEFORE the job
          is cancelled.
  M31-09  a BER compares the estimated repair cost with the device value,
          needs a photo, and is always approved (tier 1 at least).
"""

import logging

from markupsafe import Markup, escape
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish

from .fix_workshop_job import (
    CLOSED_JOB_STATES,
    GROUP_SUPERVISOR,
    GROUP_TECHNICIAN,
)

_logger = logging.getLogger(__name__)

LEVEL_RANK = {"l1": 1, "l2": 2, "l3": 3}
# a supervisor revises the level while the job is not on the bench
LEVEL_REVISABLE_STATES = ("draft", "intake", "diagnostic", "waiting_parts", "qc_failed")
# the work clock stops when the job leaves the bench for test or closes
CLOCK_STOP_STATES = ("qc_pending", "ready", "released", *CLOSED_JOB_STATES)
# ...and no clock starts on a job in QC or released
NO_CLOCK_STATES = ("qc_pending", "ready", "released")
# the test protocol is fixed once the job is handed to burn-in / QC
PROTOCOL_LOCKED_STATES = ("burn_in", "qc_pending", "ready", "released", *CLOSED_JOB_STATES)
# M31-09: a BER is declared when repairing costs this share of the device's
# value or more (a policy number: 100 = the repair costs at least the value)
BER_RATIO_PARAM = "cd_workshop.ber_cost_to_value_pct"
BER_RATIO_DEFAULT = 100.0
BER_PHOTO_TYPES = ("pre_repair_photo", "during_repair_photo")
# M31-08: why an M15 issue of a cancelled job goes back
CANCEL_RETURN_REASON = "wrong_diagnosis"

A02R2_GUARDED = frozenset(
    {
        "repair_started_at",
        "released_at",
        "released_by_id",
        "release_location_id",
        "cancel_reason",
        "cancelled_by_id",
        "ber_estimated_repair_cost",
        "ber_device_value",
    }
)


def _param_float(env, key, default):
    raw = env["ir.config_parameter"].sudo().get_param(key)
    try:
        return float(raw) if raw not in (None, False, "") else default
    except (TypeError, ValueError):
        return default


class FixWorkshopJobA02R2(models.Model):
    _inherit = "fix.workshop.job"

    # M31-01
    repair_started_at = fields.Datetime(
        string="Repair First Started", readonly=True, copy=False,
        help="When the job first went on the bench; the repair level never drops after it.",
    )  # fmt: skip
    # M31-02
    released_at = fields.Datetime(string="Released to Front Desk", readonly=True, copy=False)
    released_by_id = fields.Many2one("res.users", string="Released By", readonly=True, copy=False)
    release_location_id = fields.Many2one(
        "fix.workshop.location", string="Outgoing Staging", readonly=True, copy=False
    )
    # M31-03: the M45 work order an internal job carries out
    maintenance_request_id = fields.Many2one(
        "maintenance.request",
        string="M45 Work Order",
        index=True,
        ondelete="restrict",
        help="The M45 maintenance work order this internal job carries out (a job is the "
        "work of a service order, a refurbishment or an M45 work order).",
    )
    # M31-04
    protocol_id = fields.Many2one(
        "fix.workshop.test.protocol",
        string="Test Protocol",
        index=True,
        ondelete="restrict",
        tracking=True,
        help="The protocol QC is judged on: every step needs a passing latest result, "
        "recorded after the burn-in. Its burn-in minutes set the run (BRU-WSR-07).",
    )
    # M31-07
    estimated_cost = fields.Float(
        string="Estimated Cost (BDT)",
        compute="_compute_estimated_cost",
        help="What the approved estimate expected the repair to cost the workshop: its part "
        "lines at the parts' standard cost and its labour hours at the workshop rate.",
    )
    # M31-08
    cancel_reason = fields.Text(string="Cancellation Reason", readonly=True, copy=False)
    cancelled_by_id = fields.Many2one("res.users", string="Cancelled By", readonly=True, copy=False)
    # M31-09
    ber_estimated_repair_cost = fields.Monetary(
        string="BER: Estimated Repair Cost",
        readonly=True,
        copy=False,
        currency_field="currency_id",
    )
    ber_device_value = fields.Monetary(
        string="BER: Device Value", readonly=True, copy=False, currency_field="currency_id"
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | A02R2_GUARDED

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if len(self) == 1:
            if self.state != "draft":
                locked |= {"maintenance_request_id"}
            if self.state in PROTOCOL_LOCKED_STATES:
                locked |= {"protocol_id"}
        return locked

    # ------------------------------------------------------------ M31-03
    def _m31_tradein_link(self):
        self.ensure_one()
        TradeIn = self.env.get("fix.tradein")
        if TradeIn is None or "workshop_job_id" not in TradeIn._fields:
            return False
        return bool(TradeIn.sudo().search_count([("workshop_job_id", "=", self.id)]))

    def _m31_origin(self):
        """What this job is the work of, or None."""
        self.ensure_one()
        job = self.sudo()
        if job.order_id:
            return "service order %s" % job.order_id.name
        if job.maintenance_request_id:
            return "M45 work order %s" % job.maintenance_request_id.display_name
        if self._m31_tradein_link():
            return "refurbishment"
        return None

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.su:
            for vals in vals_list:
                if not (vals.get("order_id") or vals.get("maintenance_request_id")):
                    raise UserError(
                        "A workshop job is the work of a service order (M01), a refurbishment "
                        "(M14) or an M45 work order: name the order or the work order. A job "
                        "with none skips the approval, the cost ceiling and the settlement."
                    )
        return super().create(vals_list)

    def write(self, vals):
        if self and not self._fix_guard_open():
            for rec in self:
                if (
                    "order_id" in vals
                    and rec.order_id
                    and rec._fix_guard_differs("order_id", vals["order_id"], rec.order_id)
                ):
                    raise UserError(
                        "Job %s is the work of service order %s: its order is never cleared "
                        "or changed (the approval, the cost ceiling and the settlement are "
                        "read from it)." % (rec.name, rec.order_id.name)
                    )
                if (
                    "maintenance_request_id" in vals
                    and rec.state != "draft"
                    and (
                        rec._fix_guard_differs(
                            "maintenance_request_id",
                            vals["maintenance_request_id"],
                            rec.maintenance_request_id,
                        )
                    )
                ):
                    raise UserError("Job %s is booked in: its M45 work order is fixed." % rec.name)
                if (
                    "protocol_id" in vals
                    and rec.state in PROTOCOL_LOCKED_STATES
                    and rec._fix_guard_differs("protocol_id", vals["protocol_id"], rec.protocol_id)
                ):
                    raise UserError(
                        "Job %s is in test or closed: its test protocol is fixed (QC is judged "
                        "on it)." % rec.name
                    )
        return super().write(vals)

    def action_intake(self):
        if not self.env.su:
            for rec in self:
                if not rec._m31_origin():
                    raise UserError(
                        "Job %s is not booked in: it names no service order, refurbishment or "
                        "M45 work order." % rec.name
                    )
        return super().action_intake()

    # ------------------------------------------------------------ M31-01
    def action_revise_level(self, level=None, reason=None):
        """A Workshop Supervisor revises the repair level, with the reason,
        while the job is off the bench. It never drops once the repair has
        started (a downgrade skipped the burn-in of the rework)."""
        self._m31_require_group((GROUP_SUPERVISOR,), "Revising a repair level")
        level = (level or "").strip().lower()
        reason = (reason or "").strip()
        if level not in LEVEL_RANK:
            raise UserError("Give the new repair level (l1, l2 or l3).")
        if not reason:
            raise UserError("Say why the repair level is revised.")
        for rec in self:
            if rec.state not in LEVEL_REVISABLE_STATES:
                raise UserError(
                    "Job %s is %s: its level is revised off the bench only (waiting for parts, "
                    "back from a failed QC, or before the repair)." % (rec.name, rec.state)
                )
            old = rec.repair_level
            if level == old:
                raise UserError("Job %s is already %s." % (rec.name, level.upper()))
            if rec.repair_started_at and LEVEL_RANK[level] < LEVEL_RANK.get(old, 0):
                raise UserError(
                    "Job %s went on the bench as %s: the level does not drop once the repair "
                    "started (the rework keeps the burn-in and the certification of %s)."
                    % (rec.name, (old or "").upper(), (old or "").upper())
                )
            if rec.bench_id:
                error = rec._m31_bench_fit_error(rec.bench_id, rec.workshop_id, level)
                if error:
                    raise UserError("Job %s cannot be %s: %s" % (rec.name, level.upper(), error))
            if rec.technician_id and level in ("l2", "l3"):
                rec._check_technician_certification(rec.technician_id, level)
            rec._guarded().write({"repair_level": level})
            rec.message_post(
                body="Repair level revised %s -> %s by %s: %s"
                % ((old or "").upper(), level.upper(), self.env.user.name, reason)
            )
            publish(
                self.env,
                "workshop.job.level_revised",
                "fix.workshop.job",
                rec.id,
                {
                    "job_id": rec.id,
                    "job_name": rec.name,
                    "service_order_id": rec.sudo().order_id.id or False,
                    "old_level": old,
                    "new_level": level,
                    "reason": reason,
                    "revised_by": self.env.uid,
                },
            )
        return True

    def _m31_contributors(self):
        """(users, employees) who worked the repair: the technician, everyone
        who booked time on it, fitted a part or used a consumable."""
        self.ensure_one()
        job = self.sudo()
        employees = job.technician_id | job.time_log_ids.mapped("technician_id")
        users = employees.mapped("user_id")
        users |= job.part_line_ids.filtered(lambda ln: ln.reservation_state == "consumed").mapped(
            "consumed_by_id"
        )
        users |= job.consumable_ids.mapped("recorded_by_id")
        return users, employees

    def _m31_assert_qc_inspector(self):
        super()._m31_assert_qc_inspector()
        if self.env.su:
            return
        users, employees = self._m31_contributors()
        user = self.env.user
        if user in users or (user.sudo().employee_ids & employees):
            raise ValidationError(
                "BRU-SRM-18 Violation: %s booked time or parts on job %s, so an independent "
                "inspector runs its QC." % (user.name, self.name)
            )

    # ------------------------------------------------------------ transitions
    def _transition(self, new_state: str):
        if new_state in CLOCK_STOP_STATES:
            # M31-06: the work clock stops when the job leaves the bench
            self._m31_stop_clocks("job moved to %s" % new_state)
        result = super()._transition(new_state)
        if new_state == "in_repair":
            for rec in self.filtered(lambda j: not j.repair_started_at):
                rec._guarded().write({"repair_started_at": fields.Datetime.now()})
        return result

    def _m31_stop_clocks(self, why):
        now = fields.Datetime.now()
        for rec in self:
            running = rec.sudo().time_log_ids.filtered("running")
            if not running:
                continue
            for log in running:
                log._guarded().write({"ended_at": now, "note": log.note or why})
            rec._m31_sync_logged_minutes()

    # ------------------------------------------------------------ M31-02
    def action_release(self, location_id=None):
        """Release a QC-passed job to the front desk: the device goes to the
        workshop's outgoing staging (when it has one). The order is moved to
        Ready by the job's QC; the customer hand-over is M01's."""
        Location = self.env["fix.workshop.location"].sudo()
        for rec in self:
            rec._m31_require_group((GROUP_TECHNICIAN, GROUP_SUPERVISOR), "Releasing a job")
            rec._validate_transition("released")
            if not rec.qc_passed:
                raise UserError("Job %s has not passed QC: it is not released." % rec.name)
            staging = Location.browse(int(location_id)).exists() if location_id else Location
            if staging and (
                staging.workshop_id != rec.workshop_id or staging.kind != "outgoing_staging"
            ):
                raise UserError("%s is not an outgoing staging of %s." % (
                    staging.display_name, rec.workshop_id.name))  # fmt: skip
            if not staging:
                staging = Location.search(
                    [
                        ("workshop_id", "=", rec.workshop_id.id),
                        ("kind", "=", "outgoing_staging"),
                        ("active", "=", True),
                    ],
                    limit=1,
                )
            if staging and rec.current_location_id != staging:
                self.env["fix.workshop.custody.move"].create(
                    {"job_id": rec.id, "location_id": staging.id, "note": "released"}
                )
            rec._guarded().write(
                {
                    "released_at": fields.Datetime.now(),
                    "released_by_id": self.env.uid,
                    "release_location_id": staging.id or False,
                }
            )
        return super().action_release()

    @api.model
    def consume_service_order_delivered(self, event: dict) -> dict:
        """M01 handed the device to the customer: the workshop job of the
        order closes (M31-02). Relay only, idempotent."""
        if not self.env.su:
            raise UserError("Workshop event consumers run only from the event relay.")
        payload = event.get("payload") or {}
        order_id = payload.get("service_order_id") or payload.get("order_id")
        order_id = order_id or event.get("aggregate_id")
        jobs = self.sudo().search(
            [("order_id", "=", int(order_id or 0)), ("state", "in", ("ready", "released"))]
        )
        closed = []
        for job in jobs.with_context(m31_order_delivered=True):
            if job.state == "ready":
                job._guarded().write(
                    {"released_at": fields.Datetime.now(), "released_by_id": self.env.uid}
                )
                job._transition("released")
            job.action_deliver()
            job.message_post(body="Closed: M01 handed the device to the customer.")
            closed.append(job.id)
        return {"closed": closed}

    # ------------------------------------------------------------ M31-04
    def _m31_burn_in_required(self) -> bool:
        self.ensure_one()
        return self.repair_level in ("l2", "l3") or bool(
            self.sudo().protocol_id.burn_in_minutes or 0
        )

    def _m31_required_burn_in_minutes(self) -> float:
        self.ensure_one()
        minimum = self._m31_burn_in_min_minutes() if self.repair_level in ("l2", "l3") else 0.0
        return max(minimum, float(self.sudo().protocol_id.burn_in_minutes or 0))

    def _m31_check_protocol_results(self):
        """Every step of the job's protocol has a latest result that passed,
        recorded after the burn-in run ended."""
        self.ensure_one()
        job = self.sudo()
        protocol = job.protocol_id
        if not protocol:
            raise UserError(
                "Job %s has no test protocol: QC is judged on the protocol's tests. Choose the "
                "protocol and record its results first." % self.name
            )
        if not protocol.step_ids:
            raise UserError("Test protocol %s has no tests to judge QC on." % protocol.display_name)
        latest = {}
        for res in job.test_result_ids.sorted(
            lambda r: (r.tested_at or fields.Datetime.now(), r.id)
        ):
            latest[res.step_id.id] = res
        missing, failed, stale = [], [], []
        for step in protocol.step_ids:
            res = latest.get(step.id)
            if not res:
                missing.append(step.display_name)
            elif not res.passed:
                failed.append(step.display_name)
            elif job.burn_in_completed_at and res.tested_at < job.burn_in_completed_at:
                stale.append(step.display_name)
        problems = []
        if missing:
            problems.append("no result for %s" % ", ".join(missing))
        if failed:
            problems.append("the latest result failed for %s" % ", ".join(failed))
        if stale:
            problems.append("recorded before the burn-in ended for %s" % ", ".join(stale))
        if problems:
            raise UserError(
                "Job %s cannot pass QC on protocol %s: %s."
                % (self.name, protocol.display_name, "; ".join(problems))
            )

    def action_pass_qc(self, notes=""):
        # an inspector's pass; trusted system code (imports, seeds) is not
        # an inspection and is let through, as by the book-in gate
        for rec in self if not self.env.su else self.browse():
            rec._m31_check_protocol_results()
        return super().action_pass_qc(notes=notes)

    # ------------------------------------------------------------ M31-07
    @api.depends("order_id", "workshop_id.labour_rate_per_hour")
    def _compute_estimated_cost(self):
        for rec in self:
            est = rec._m31_governing_estimate()
            rate = rec.workshop_id.sudo().labour_rate_per_hour or 0.0
            cost = 0.0
            for line in est.sudo().line_ids if est else []:
                if line.line_type in ("labour", "service", "installation", "support"):
                    cost += (line.quantity or 0.0) * rate
                elif line.product_id:
                    cost += (line.quantity or 0.0) * (line.product_id.standard_price or 0.0)
            rec.estimated_cost = round(cost, 2)

    # ------------------------------------------------------------ M31-08
    def action_cancel(self, reason=""):
        """Cancel a job: a Workshop Supervisor's decision, with the reason
        (or M01's own cancellation cascade). Reserved parts are released and
        parts M15 issued to the job go back BEFORE the job is cancelled (M15
        refuses a return from a closed job); M01 is told."""
        system = self.env.su or self.env.context.get("m31_ber_closing")
        reason = (reason or self.env.context.get("m31_cancel_reason") or "").strip()
        if not system:
            self._m31_require_group((GROUP_SUPERVISOR,), "Cancelling a workshop job")
            if not reason:
                raise UserError("Say why the workshop job is cancelled.")
        for rec in self:
            rec._validate_transition("cancelled")
            rec._m31_unwind_parts(reason or "job cancelled")
        result = super().action_cancel()
        for rec in self.filtered(lambda j: j.state == "cancelled"):
            rec._guarded().write(
                {"cancel_reason": reason or False, "cancelled_by_id": self.env.uid}
            )
            rec._m31_notify_order_cancelled(reason)
        return result

    def _m31_unwind_parts(self, why):
        self.ensure_one()
        lines = self.sudo().part_line_ids
        returned, kept = [], []
        for line in lines.filtered(lambda ln: ln.reservation_state in ("draft", "reserved")):
            line.action_release_reservation()
        for line in lines.filtered(lambda ln: ln.reservation_state == "consumed"):
            issue = line.m15_consumption_id if "m15_consumption_id" in line._fields else None
            if not issue or issue.state != "consumed":
                kept.append(line.display_name)
                continue
            try:
                with self.env.cr.savepoint():
                    issue.sudo().action_return_part(
                        reason=CANCEL_RETURN_REASON, notes="Job %s cancelled: %s" % (self.name, why)
                    )
                    line._guarded().write({"reservation_state": "released"})
                returned.append(issue.name)
            except UserError as exc:
                kept.append("%s (%s)" % (issue.name, exc))
        if returned or kept:
            body = [escape("Cancellation: parts unwound.")]
            if returned:
                body.append(escape("Returned to stores: %s" % ", ".join(returned)))
            if kept:
                body.append(escape("Not returned, for the store to decide: %s" % ", ".join(kept)))
            self.message_post(body=Markup("<br/>").join(body))

    def _m31_notify_order_cancelled(self, reason):
        self.ensure_one()
        order = self.sudo().order_id
        if not order:
            return
        if order.state != "cancelled":
            order.message_post(
                body="Workshop job %s was cancelled by %s: %s. The order needs a decision "
                "(cancel it, or route the repair again)."
                % (self.name, self.env.user.name, reason or "-")
            )
        publish(
            self.env,
            "workshop.job.cancelled",
            "fix.workshop.job",
            self.id,
            {
                "workshop_job_id": self.id,
                "job_name": self.name,
                "service_order_id": order.id,
                "service_order_ref": order.name,
                "reason": reason or "",
            },
        )

    # ------------------------------------------------------------ M31-09
    def _dofa_current_tier(self) -> str:
        tier = super()._dofa_current_tier()
        if self.ber_proposed_at and tier == "tier_0":
            # a write-off of nothing sunk is still a supervisor's decision
            return "tier_1"
        return tier

    @api.depends("ber_writeoff_amount", "ber_proposed_at", "total_repair_cost")
    def _compute_dofa_writeoff_tier(self):
        for rec in self:
            tier = rec._dofa_current_tier()
            rec.dofa_writeoff_tier = (
                tier if tier in ("tier_1", "tier_2", "tier_3", "tier_4") else "none"
            )

    def _m31_check_ber_photo(self):
        self.ensure_one()
        photos = self.sudo().evidence_ids.filtered(
            lambda ev: ev.evidence_type in BER_PHOTO_TYPES
            and ev.document_id.res_model == self._name
            and ev.document_id.res_id == self.id
        )
        if not photos:
            raise UserError(
                "A BER on job %s needs a photo of the device as found (a pre-repair or "
                "during-repair photo filed on the job)." % self.name
            )

    def action_propose_ber(
        self, reason="", writeoff_amount=0.0, estimated_repair_cost=None, device_value=None
    ):
        try:
            cost = float(estimated_repair_cost or 0.0)
            value = float(device_value or 0.0)
        except (TypeError, ValueError):
            raise UserError("The repair cost and the device value are amounts in BDT.") from None
        if cost <= 0 or value <= 0:
            raise UserError(
                "A BER compares the estimated repair cost with the device's value: give both "
                "(BDT)."
            )
        ratio = _param_float(self.env, BER_RATIO_PARAM, BER_RATIO_DEFAULT)
        if cost < value * ratio / 100.0:
            raise UserError(
                "The repair (BDT %.2f) costs less than %.0f%% of the device's value (BDT %.2f): "
                "it is economic to repair, not BER." % (cost, ratio, value)
            )
        for rec in self:
            rec._m31_check_ber_photo()
        result = super().action_propose_ber(reason=reason, writeoff_amount=writeoff_amount)
        for rec in self:
            rec._guarded().write({"ber_estimated_repair_cost": cost, "ber_device_value": value})
            rec.message_post(
                body="BER basis: repair BDT %.2f against a device value of BDT %.2f."
                % (cost, value)
            )
        return result


class FixWorkshopTimeLogA02R2(models.Model):
    """M31-06: the rate is the one in force when the time was booked (a rate
    change re-costed every past job), the clock stops with the job and a
    supervisor corrects a wrong segment with a reason."""

    _inherit = "fix.workshop.time.log"

    rate_per_hour = fields.Float(
        string="Labour Rate (BDT / hour)",
        readonly=True,
        help="The workshop's labour rate when this time was booked.",
    )
    corrected_by_id = fields.Many2one("res.users", string="Corrected By", readonly=True)
    correction_note = fields.Text(string="Correction", readonly=True)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "rate_per_hour",
            "corrected_by_id",
            "correction_note",
        }

    @api.model_create_multi
    def create(self, vals_list):
        Job = self.env["fix.workshop.job"]
        for vals in vals_list:
            job = Job.browse(vals.get("job_id")).exists()
            if job and job.state in NO_CLOCK_STATES:
                raise UserError(
                    "Job %s is %s: the bench work is done, so no clock starts on it."
                    % (job.name, job.state)
                )
        records = super().create(vals_list)
        for rec in records:
            rec._guarded().write(
                {"rate_per_hour": rec.job_id.sudo().workshop_id.labour_rate_per_hour or 0.0}
            )
        return records

    def action_stop(self, note=None):
        for rec in self:
            if rec.job_id.state in CLOSED_JOB_STATES:
                raise UserError(
                    "Job %s is closed: its clocks were stopped when it closed." % rec.job_id.name
                )
        return super().action_stop(note=note)

    def action_correct(self, started_at=None, ended_at=None, reason=None):
        """A Workshop Supervisor corrects a stopped segment (a clock left
        running overnight, a start booked on the wrong job's time); the old
        times stay on record in the correction note and the job's chatter."""
        if not (self.env.su or self.env.user.has_group(GROUP_SUPERVISOR)):
            raise UserError("A time segment is corrected by a workshop supervisor.")
        reason = (reason or "").strip()
        if not reason:
            raise UserError("Say why the time segment is corrected.")
        start = fields.Datetime.to_datetime(started_at) if started_at else None
        end = fields.Datetime.to_datetime(ended_at) if ended_at else None
        for rec in self:
            if rec.running:
                raise UserError("Stop the clock before correcting it.")
            if rec.job_id.state in CLOSED_JOB_STATES:
                raise UserError("Job %s is closed: its labour record is final." % rec.job_id.name)
            if rec.technician_id and rec.technician_id in self.env.user.employee_ids:
                raise UserError("A supervisor does not correct his own time.")
            new_start, new_end = start or rec.started_at, end or rec.ended_at
            if not (new_start and new_end) or new_end <= new_start:
                raise UserError("A segment ends after it starts.")
            if new_end > fields.Datetime.now():
                raise UserError("A segment cannot end in the future.")
            note = "%s -> %s was %s -> %s (%s, by %s)" % (
                new_start,
                new_end,
                rec.started_at,
                rec.ended_at,
                reason,
                self.env.user.name,
            )
            rec._guarded().write(
                {
                    "started_at": new_start,
                    "ended_at": new_end,
                    "corrected_by_id": self.env.uid,
                    "correction_note": "\n".join(filter(None, [rec.correction_note, note])),
                }
            )
            rec.job_id._m31_sync_logged_minutes()
            rec.job_id.message_post(body="Time segment corrected: %s" % note)
        return True


class FixWorkshopA02R2(models.Model):
    """M31-12: the supervisors of a workshop (who accept a transfer into it)."""

    _inherit = "fix.workshop"

    supervisor_user_ids = fields.Many2many(
        "res.users",
        "fix_workshop_supervisor_rel",
        "workshop_id",
        "user_id",
        string="Workshop Supervisors",
        help="Workshop Supervisors of THIS workshop: with its manager, they accept a job "
        "transferred into it (BRU-WSR-14).",
    )
