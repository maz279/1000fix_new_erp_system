# fix_spine_work_order — A07 P1 bridge: the M47 facility work order as the
# one work-order spine (report §6 P1).
#
# The M47 work order keeps ITS lifecycle, unchanged: draft -> DOFA spend
# approval -> scheduled -> (permit to work) -> in progress -> completed with
# evidence -> verified by a Facility Manager who neither raised nor completed
# it. This module adds what the spine needs on it:
#   - the asset (equipment / vehicle / IoT device / prescriptive action) and
#     the origin (which source raised it), set only by the routing transition;
#   - one OPEN work order per source item (a partial unique index);
#   - verification completes the source through the source's own method:
#     M47 PM, M45 PM and M46 service are marked done; an M45 calibration WO
#     needs the calibration recorded in M45 first; an M48 action receives the
#     work order as its outcome evidence and waits for the outcome, which only
#     M48 records (BRU-IOT-14). A source that would refuse completion
#     (no odometer, no technician) refuses the verification, naming why.
from odoo import api, fields, models
from odoo.exceptions import UserError

from .fix_maintenance_demand import ORIGINS, SO_CLOSED, WO_OPEN

SPINE_LINKS = (
    "spine_demand_id",
    "vehicle_id",
    "iot_device_id",
    "iot_action_id",
    "prediction_id",
    "equipment_pm_id",
    "vehicle_pm_id",
    "spine_calibration_due",
    "spine_calibration_id",
    "spine_conflict_assignment_ids",
)


class FixFacilityWorkOrderSpine(models.Model):
    _inherit = "fix.facility.work.order"

    # A07 P1 bridge: one source item raises at most one OPEN work order,
    # whichever path (consumer, cron, a person routing a demand) raises it.
    _spine_one_open_per_source = models.UniqueIndex(
        "(spine_source_ref) WHERE spine_source_ref IS NOT NULL "
        "AND state NOT IN ('verified', 'cancelled')",
        "This source already has an open work order.",
    )

    spine_demand_id = fields.Many2one(
        "fix.maintenance.demand",
        string="Maintenance Demand",
        readonly=True,
        copy=False,
        index=True,
        ondelete="set null",
    )
    spine_origin = fields.Selection(
        [("request", "Request"), ("m47_pm", "M47 Building Services PM"), *ORIGINS],
        string="Origin",
        compute="_compute_spine",
        store=True,
        index=True,
    )
    spine_source_ref = fields.Char(
        string="Source Key", compute="_compute_spine", store=True, index=True, copy=False
    )
    spine_asset_kind = fields.Selection(
        [
            ("site", "Site / Building"),
            ("equipment", "Equipment (M45)"),
            ("vehicle", "Vehicle (M46)"),
            ("iot", "IoT-Monitored Asset (M48)"),
        ],
        string="Asset Kind",
        compute="_compute_spine",
        store=True,
    )
    vehicle_id = fields.Many2one(
        "fleet.vehicle", string="Vehicle (M46)", readonly=True, copy=False, index=True
    )
    iot_device_id = fields.Many2one(
        "fix.iot.device", string="IoT Device (M48)", readonly=True, copy=False
    )
    iot_action_id = fields.Many2one(
        "fix.iot.action", string="Prescriptive Action (M48)", readonly=True, copy=False, index=True
    )
    prediction_id = fields.Many2one(
        "fix.predictive.maintenance", string="Prediction (M48)", readonly=True, copy=False
    )
    equipment_pm_id = fields.Many2one(
        "fix.equipment.pm", string="M45 PM Job", readonly=True, copy=False, index=True
    )
    vehicle_pm_id = fields.Many2one(
        "fix.vehicle.pm", string="M46 Service", readonly=True, copy=False, index=True
    )
    spine_calibration_due = fields.Date(string="Calibration Due", readonly=True, copy=False)
    spine_calibration_id = fields.Many2one(
        "fix.calibration", string="Calibration Recorded", readonly=True, copy=False
    )
    spine_conflict_assignment_ids = fields.Many2many(
        "fix.vehicle.assignment",
        "fix_wo_spine_assignment_conflict_rel",
        "work_order_id",
        "assignment_id",
        string="Duty Bookings Clashing",
        readonly=True,
        copy=False,
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | set(SPINE_LINKS)

    @api.depends(
        "spine_demand_id",
        "pm_id",
        "vehicle_id",
        "iot_device_id",
        "iot_action_id",
        "prediction_id",
        "equipment_id",
    )
    def _compute_spine(self):
        for rec in self:
            demand = rec.spine_demand_id
            if demand:
                rec.spine_origin = demand.origin
                rec.spine_source_ref = "%s,%s,%s" % (
                    demand.source_model,
                    demand.source_res_id,
                    demand.source_key,
                )
            elif rec.pm_id:
                rec.spine_origin = "m47_pm"
                rec.spine_source_ref = "fix.site.pm,%s" % rec.pm_id.id
            else:
                rec.spine_origin = "request"
                rec.spine_source_ref = False
            if rec.vehicle_id:
                rec.spine_asset_kind = "vehicle"
            elif rec.iot_action_id or rec.prediction_id or rec.iot_device_id:
                rec.spine_asset_kind = "iot"
            elif rec.equipment_id:
                rec.spine_asset_kind = "equipment"
            else:
                rec.spine_asset_kind = "site"

    def _wo_person_raised(self) -> bool:
        return super()._wo_person_raised() and not self.spine_demand_id

    # ------------------------------------------------------------ verify
    def _spine_completion_problems(self):
        """Why the source of this (completed) work order would refuse to be
        completed with it. Checked before the verification is written."""
        self.ensure_one()
        problems = []
        epm = self.equipment_pm_id.sudo()
        if epm and epm.state == "open" and not (epm.technician_id or self.assigned_to):
            problems.append(
                "M45 job %s records who did the work: assign the engineer on this work order"
                % epm.name
            )
        vpm = self.vehicle_pm_id.sudo()
        if vpm and vpm.state == "open":
            if (vpm.odometer or 0) <= 0:
                problems.append(
                    "record the odometer at service on M46 service %s (a Fleet Officer does)"
                    % vpm.name
                )
            if (
                self.actual_cost
                and vpm.cost
                and abs((vpm.cost or 0.0) - (self.actual_cost or 0.0)) > 0.005
            ):
                problems.append(
                    "the actual cost %.2f differs from the cost %.2f on M46 service %s: correct "
                    "one of them (the service cost goes to M52)"
                    % (self.actual_cost, vpm.cost, vpm.name)
                )
        if self.spine_origin == "m45_calibration" and not self._spine_calibration_since():
            problems.append(
                "record the calibration of %s (a passing one, with its certificate) in M45: "
                "the work order does not stand in for it" % self.equipment_id.display_name
            )
        return problems

    def _spine_calibration_since(self):
        self.ensure_one()
        if not self.equipment_id:
            return self.env["fix.calibration"]
        since = fields.Date.to_date(self.create_date) if self.create_date else None
        # a failed or rejected calibration certifies nothing, so it completes nothing
        domain = [
            ("equipment_id", "=", self.equipment_id.id),
            ("superseded_by_id", "=", False),
            ("result", "in", ("pass", "adjusted")),
            ("decision_state", "!=", "rejected"),
        ]
        if since:
            domain.append(("calibrated_on", ">=", since))
        return (
            self.env["fix.calibration"]
            .sudo()
            .search(domain, order="calibrated_on desc, id desc", limit=1)
        )

    def _spine_complete_source(self):
        """After verification: complete the source through its own method, as
        the platform service (the verifier need not hold the source's role;
        the evidence it would ask for is checked above and comes from the
        verified work order)."""
        for rec in self:
            done = []
            when = fields.Date.context_today(rec, rec.completed_at or fields.Datetime.now())
            when = min(when, fields.Date.context_today(rec))
            pm = rec.pm_id.sudo()
            if pm and pm.state == "open":
                pm.action_done(done_on=when)
                done.append("M47 PM %s marked done" % pm.name)
            epm = rec.equipment_pm_id.sudo()
            if epm and epm.state == "open":
                vals = {}
                if not epm.technician_id:
                    vals["technician_id"] = rec.assigned_to.id
                if not (epm.notes or "").strip():
                    vals["notes"] = "Work order %s: %s" % (rec.name, rec.completion_notes or "")
                if vals:
                    epm.write(vals)
                epm.action_done()
                done.append("M45 job %s marked done" % epm.name)
            vpm = rec.vehicle_pm_id.sudo()
            if vpm and vpm.state == "open":
                if rec.actual_cost and not vpm.cost:
                    vpm.write({"cost": rec.actual_cost})
                vpm.action_done()
                done.append("M46 service %s completed" % vpm.name)
            if rec.spine_origin == "m45_calibration":
                cal = rec._spine_calibration_since()
                rec._guarded().write({"spine_calibration_id": cal.id})
                done.append("calibration %s on file" % cal.display_name)
            demand = rec.spine_demand_id.sudo()
            if demand.source_model == "fix.equipment.oos":
                # A07 P1 wiring: the hold is the Quality Manager's to resolve
                hold = self.env["fix.equipment.oos"].sudo().browse(demand.source_res_id).exists()
                if hold.state == "open":
                    done.append(
                        "M45 hold %s stays open until it is returned to service in M45" % hold.name
                    )
            action = rec.iot_action_id.sudo()
            if action and action.state == "dispatched":
                if not (action.outcome_evidence_ref or "").strip():
                    action.write({"outcome_evidence_ref": "Work order %s (verified)" % rec.name})
                done.append(
                    "M48 action %s has its evidence; its outcome is recorded in M48" % action.name
                )
            prediction = (rec.prediction_id or action.prediction_id).sudo()
            if prediction:
                prediction.message_post(
                    body="Work order %s verified by %s. The outcome is recorded by completing "
                    "the prescriptive action in M48." % (rec.name, self.env.user.name)
                )
            demands = (
                rec.spine_demand_id
                | self.env["fix.maintenance.demand"].sudo().search([("work_order_id", "=", rec.id)])
            ).sudo()
            demands.filtered(lambda d: d.state == "routed")._guarded().write({"state": "done"})
            if done:
                rec.message_post(body="Source completed: %s." % "; ".join(done))
        return True

    def action_verify(self, notes=None):
        spine = self.filtered(
            lambda w: (
                w.state == "completed"
                and (w.spine_origin not in (False, "request") or w.iot_action_id)
            )
        )
        # M47's own checks (state, Facility Manager, SoD, invoice reference)
        # speak first; a source that would refuse completion then refuses the
        # whole verification, which rolls back with the error.
        result = super().action_verify(notes=notes)
        for rec in spine:
            problems = rec._spine_completion_problems()
            if problems:
                raise UserError("%s cannot be verified yet: %s." % (rec.name, "; ".join(problems)))
        spine._spine_complete_source()
        return result

    def action_cancel(self, reason=None):
        result = super().action_cancel(reason=reason)
        Demand = self.env["fix.maintenance.demand"].sudo()
        for rec in self.filtered(lambda w: w.state == "cancelled"):
            Demand.search([("work_order_id", "=", rec.id)])._spine_reopen_after_cancel(rec)
        return result


class FixIotActionSpineLink(models.Model):
    """The M48 action shows the order the spine raised for it (read-only):
    M48 never acts on the asset (BRU-IOT-12), the order does."""

    _inherit = "fix.iot.action"

    spine_work_order_id = fields.Many2one(
        "fix.facility.work.order", string="Work Order", compute="_compute_spine_orders"
    )
    spine_service_order_id = fields.Many2one(
        "fix.service.order", string="Service Order (M01)", compute="_compute_spine_orders"
    )

    def _compute_spine_orders(self):
        WorkOrder = self.env["fix.facility.work.order"].sudo()
        Demand = self.env["fix.maintenance.demand"].sudo()
        for rec in self:
            wo = WorkOrder.search([("iot_action_id", "=", rec.id)], order="id desc", limit=1)
            demand = Demand.search([("iot_action_id", "=", rec.id)], order="id desc", limit=1)
            rec.spine_work_order_id = wo or demand.work_order_id
            rec.spine_service_order_id = demand.service_order_id

    def _fix_completion_blockers(self):
        """A07 (2026-11-07): an action could be completed, and its finding recorded,
        while the order doing the work was still open. A work order is open until
        it is verified (WO_OPEN), a service order until delivered or closed."""
        blockers = super()._fix_completion_blockers()
        for rec in self.sudo():
            demands = (
                self.env["fix.maintenance.demand"].sudo().search([("iot_action_id", "=", rec.id)])
            )
            orders = (
                self.env["fix.facility.work.order"].sudo().search([("iot_action_id", "=", rec.id)])
                | demands.work_order_id
            )
            for demand in demands.filtered(lambda d: d.state == "pending"):
                blockers.append(
                    "%s has no order yet (%s)" % (demand.name, demand.blocker or "not routed")
                )
            for wo in orders.filtered(lambda w: w.state in WO_OPEN):
                blockers.append("work order %s is still open" % wo.name)
            for so in demands.service_order_id.filtered(lambda s: s.state not in SO_CLOSED):
                blockers.append("service order %s is still open" % so.name)
        return blockers
