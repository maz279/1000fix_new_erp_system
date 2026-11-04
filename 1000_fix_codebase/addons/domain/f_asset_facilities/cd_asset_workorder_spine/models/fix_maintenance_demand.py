# fix_maintenance_demand — A07 P1 bridge: the one work-order spine's intake.
#
# A07 audit (2026-11-04) report §6 P1 "One work-order spine": M45 PM and
# calibration, M46 service due, M47 PM and M48 interventions each kept their
# own "open/done" job with no work order, no spend approval, no permit and no
# verification behind it, and M48 dispatched to nobody (iot.action_dispatched,
# predictive_maintenance.wo_created and device.maintenance_due had no
# consumer). Every such demand now lands here, once per source item, and is
# routed to the M47 facility work order (internal assets) or a DRAFT M01
# service order (customer-premises assets, a customer's device plan).
#
# A demand that cannot be routed from the facts on file (no M47 site for the
# branch, two sites for it, no registered customer device) is NOT guessed: it
# stays pending with what it needs, and a person completes the fact and routes
# it (action_route). Nothing here posts, closes or decides anything.
from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError

WO_MODEL = "fix.facility.work.order"
WO_OPEN = ("draft", "scheduled", "in_progress", "completed")
SO_CLOSED = ("delivered", "closed", "cancelled")
FACILITY_MANAGER = "cd_facility.group_facility_manager"
SO_COMMERCIAL_APPROVER = "cd_service_order.group_so_commercial_approver"
DHAKA = "Asia/Dhaka"

ORIGINS = [
    ("m45_pm", "M45 Equipment PM / Corrective Job"),
    ("m45_calibration", "M45 Calibration (Due or Hold)"),
    # A07 P1 wiring (2026-11-04): an M45 out-of-service hold for a fault, damage
    # or a missing condition check, and a silent M48 telemetry stream
    ("m45_repair", "M45 Out of Service (Repair / Check)"),
    ("m48_silent", "M48 Telemetry Stream Silent"),
    ("m46_service", "M46 Vehicle Service Due"),
    ("m48_prediction", "M48 Predicted Failure"),
    ("m48_action", "M48 Dispatched Intervention"),
    ("m17_device_pm", "M17 Device Maintenance Plan"),
]
WORK_TYPES = [
    ("maintenance", "Preventive Maintenance"),
    ("repair", "Emergency Repair"),
    ("upgrade", "Infrastructure Upgrade"),
    ("inspection", "Compliance Inspection"),
]
# What a person may complete on a pending demand before routing it.
ROUTING_FIELDS = (
    "site_id",
    "branch_id",
    "device_id",
    "technician_id",
    "scheduled_date",
    "description",
)
# The source, the asset and the outcome: set by the consumers and the
# routing transition only.
SYSTEM_FIELDS = {
    "name",
    "company_id",
    "operating_unit_id",
    "origin",
    "target",
    "source_model",
    "source_res_id",
    "source_key",
    "source_ref",
    "work_type",
    "estimated_cost",
    "currency_id",
    "equipment_id",
    "vehicle_id",
    "iot_device_id",
    "iot_action_id",
    "prediction_id",
    "equipment_pm_id",
    "vehicle_pm_id",
    "device_pm_id",
    "partner_id",
    "calibration_due",
    "state",
    "blocker",
    "work_order_id",
    "service_order_id",
    "route_count",
    "routed_by_id",
    "routed_at",
    "dismissed_by_id",
    "dismissed_at",
    "dismiss_reason",
    "source_log",
}
NO_KEY = "-"


def _today(env):
    return fields.Date.context_today(env["res.users"].with_context(tz=DHAKA))


class FixMaintenanceDemand(models.Model):
    _name = "fix.maintenance.demand"
    _description = "Maintenance Demand (Work-Order Spine)"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "id desc"

    # The idempotency key of every consumer: one demand per source item.
    _source_once = models.Constraint(
        "UNIQUE (source_model, source_res_id, source_key)",
        "A source item raises one maintenance demand.",
    )

    name = fields.Char(required=True, readonly=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit", index=True)
    origin = fields.Selection(ORIGINS, required=True, readonly=True, index=True)
    target = fields.Selection(
        [
            ("work_order", "Facility Work Order (M47 spine)"),
            ("service_order", "Preventive Service Order (M01)"),
        ],
        required=True,
        readonly=True,
    )
    source_model = fields.Char(required=True, readonly=True, index=True)
    source_res_id = fields.Integer(required=True, readonly=True, index=True)
    source_key = fields.Char(
        required=True,
        readonly=True,
        default=NO_KEY,
        help="Distinguishes demands of one record (the due date of a calibration or plan).",
    )
    source_ref = fields.Char(string="Source", readonly=True)
    description = fields.Text(required=True)
    scheduled_date = fields.Date()
    work_type = fields.Selection(WORK_TYPES, default="maintenance", required=True, readonly=True)
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    estimated_cost = fields.Monetary(currency_field="currency_id", readonly=True)
    # the asset and the source records
    equipment_id = fields.Many2one("fix.equipment", string="Equipment (M45)", readonly=True)
    vehicle_id = fields.Many2one("fleet.vehicle", string="Vehicle (M46)", readonly=True)
    iot_device_id = fields.Many2one("fix.iot.device", string="IoT Device (M48)", readonly=True)
    iot_action_id = fields.Many2one(
        "fix.iot.action", string="Prescriptive Action (M48)", readonly=True, index=True
    )
    prediction_id = fields.Many2one(
        "fix.predictive.maintenance", string="Prediction (M48)", readonly=True, index=True
    )
    equipment_pm_id = fields.Many2one("fix.equipment.pm", string="M45 PM Job", readonly=True)
    vehicle_pm_id = fields.Many2one("fix.vehicle.pm", string="M46 Service", readonly=True)
    device_pm_id = fields.Many2one("fix.device.pm", string="M17 Device Plan", readonly=True)
    calibration_due = fields.Date(string="Calibration Due", readonly=True)
    partner_id = fields.Many2one("res.partner", string="Customer", readonly=True)
    # what a person completes before routing
    site_id = fields.Many2one("fix.site", string="Site (M47)")
    branch_id = fields.Many2one("fix.branch", string="Branch")
    device_id = fields.Many2one("fix.device", string="Customer Device (M17)")
    technician_id = fields.Many2one("hr.employee", string="Technician / Engineer")
    # outcome
    state = fields.Selection(
        [
            ("pending", "Needs Routing"),
            ("routed", "Routed"),
            ("done", "Completed"),
            ("dismissed", "Dismissed"),
        ],
        required=True,
        default="pending",
        readonly=True,
        index=True,
        tracking=True,
    )
    blocker = fields.Text(
        string="What It Needs",
        readonly=True,
        help="Why the demand could not be routed automatically, and what a person "
        "must complete before routing it.",
    )
    work_order_id = fields.Many2one(WO_MODEL, string="Work Order", readonly=True, index=True)
    service_order_id = fields.Many2one(
        "fix.service.order", string="Service Order", readonly=True, index=True
    )
    route_count = fields.Integer(readonly=True, default=0)
    routed_by_id = fields.Many2one("res.users", string="Routed By", readonly=True)
    routed_at = fields.Datetime(readonly=True)
    dismissed_by_id = fields.Many2one("res.users", string="Dismissed By", readonly=True)
    dismissed_at = fields.Datetime(readonly=True)
    dismiss_reason = fields.Text(readonly=True)
    source_log = fields.Text(
        string="Source Updates",
        readonly=True,
        help="What the source reported after the demand was raised (returned to service, "
        "another silent stream, the work order reopened), one line per event.",
    )

    # ------------------------------------------------------------ guard
    def _fix_guarded_fields(self) -> set:
        guarded = super()._fix_guarded_fields() | SYSTEM_FIELDS
        if any(rec.state != "pending" for rec in self):
            # a routed demand is the record of what was raised from what
            guarded |= set(ROUTING_FIELDS)
        return guarded

    def unlink(self):
        if not self.env.su:
            raise UserError(
                "A maintenance demand is the record of what a source raised: dismiss it "
                "with a reason instead of deleting it."
            )
        return super().unlink()

    # ------------------------------------------------------------ helpers
    def _spine_target_open(self) -> bool:
        self.ensure_one()
        if self.target == "work_order":
            return bool(self.work_order_id) and self.work_order_id.state in WO_OPEN
        return bool(self.service_order_id) and self.service_order_id.state not in SO_CLOSED

    @api.model
    def _spine_find(self, source, key=NO_KEY):
        return (
            self.sudo()
            .with_context(active_test=False)
            .search(
                [
                    ("source_model", "=", source._name),
                    ("source_res_id", "=", source.id),
                    ("source_key", "=", key or NO_KEY),
                ],
                limit=1,
            )
        )

    @api.model
    def _spine_raise(self, origin, source, vals, key=NO_KEY, label=None):
        """The demand of `source` (created once), routed when it can be."""
        existing = self._spine_find(source, key)
        if existing:
            return existing
        labels = dict(ORIGINS)
        vals = dict(
            vals,
            origin=origin,
            source_model=source._name,
            source_res_id=source.id,
            source_key=key or NO_KEY,
            source_ref=label or source.display_name,
            name="%s: %s" % (labels[origin], label or source.display_name),
        )
        demand = self.sudo()._guarded().create(vals)
        demand._spine_route()
        return demand

    def _spine_log(self, marker, text):
        """Append a source update once (`marker` makes redelivery a no-op).
        Returns False when it was already logged."""
        self.ensure_one()
        tag = "[%s]" % marker
        if tag in (self.source_log or ""):
            return False
        line = "%s %s %s" % (_today(self.env), tag, text)
        self.sudo()._guarded().write(
            {"source_log": "\n".join(filter(None, (self.source_log, line)))}
        )
        self.message_post(body=text)
        return True

    def _spine_resolve_site(self):
        """(site, problem): the M47 site the work is done at, from the facts on
        file. Two candidate sites, or none, is a question for a person."""
        self.ensure_one()
        if self.site_id:
            return self.site_id, None
        if self.iot_device_id.site_id:
            return self.iot_device_id.site_id, None
        asset = self.vehicle_id or self.equipment_id
        branch = self.branch_id or (asset.branch_id if asset else self.env["fix.branch"])
        if not branch:
            return None, (
                "the %s names no branch, so its M47 site is not known: choose the site"
                % (asset._description.lower() if asset else "asset")
            )
        Site = self.env["fix.site"].sudo()
        sites = Site.search([("branch_id", "=", branch.id), ("state", "!=", "closed")])
        live = sites.filtered(lambda s: s.state == "active")
        pick = live if len(live) == 1 else (sites if len(sites) == 1 else Site)
        if pick:
            return pick, None
        if not sites:
            return None, "branch %s has no M47 site: choose the site" % branch.display_name
        return None, "branch %s has %d M47 sites (%s): choose the site" % (
            branch.display_name,
            len(sites),
            ", ".join(sites.mapped("name")),
        )

    def _spine_work_order_vals(self):
        self.ensure_one()
        site, problem = self._spine_resolve_site()
        if problem:
            return None, [problem]
        return {
            "site_id": site.id,
            "company_id": site.company_id.id,
            "operating_unit_id": (site.operating_unit_id or self.operating_unit_id).id,
            "work_type": self.work_type,
            "description": self.description,
            "scheduled_date": self.scheduled_date or _today(self.env),
            "estimated_cost": self.estimated_cost,
            "currency_id": self.currency_id.id,
            "equipment_id": self.equipment_id.id,
            "assigned_to": self.technician_id.id,
            "spine_demand_id": self.id,
            "vehicle_id": self.vehicle_id.id,
            "iot_device_id": self.iot_device_id.id,
            "iot_action_id": self.iot_action_id.id,
            "prediction_id": self.prediction_id.id,
            "equipment_pm_id": self.equipment_pm_id.id,
            "vehicle_pm_id": self.vehicle_pm_id.id,
            "spine_calibration_due": self.calibration_due,
        }, []

    def _spine_service_order_vals(self):
        self.ensure_one()
        problems = []
        device = self.device_id.sudo()
        if not device:
            problems.append(
                "a customer-premises asset is serviced on the customer's registered device "
                "(M17): choose the device"
            )
        customer = self.partner_id or device.owner_id
        if device and not customer:
            problems.append("device %s has no owner on record (M17)" % device.display_name)
        elif device and self.partner_id and device.owner_id and device.owner_id != self.partner_id:
            problems.append(
                "device %s belongs to %s, not to %s"
                % (device.display_name, device.owner_id.display_name, self.partner_id.display_name)
            )
        branch = self.branch_id or device.branch_id or self.site_id.branch_id
        if not branch:
            problems.append("no branch: choose the branch that takes the order")
        if problems:
            return None, problems
        return {
            "device_id": device.id,
            "customer_id": customer.id,
            "branch_id": branch.id,
            "company_id": self.company_id.id,
            "operating_unit_id": self.operating_unit_id.id,
            "service_type": "pm_schedule" if self.origin == "m17_device_pm" else "onsite",
            "order_category": "standard",
            "fault_description": self.description,
            "technician_id": self.technician_id.id,
            # DI-04: one order per routing of this demand, however often retried
            "idempotency_key": "a07-spine:%s:%s" % (self.id, self.route_count + 1),
        }, []

    def _spine_route(self, manual=False):
        """Route each pending demand to its target. Automatic routing (the
        consumers, the cron) runs as superuser and leaves a demand it cannot
        route pending with what it needs; a person's routing raises it."""
        for rec in self:
            if rec.state != "pending":
                continue
            builder = (
                rec._spine_work_order_vals
                if rec.target == "work_order"
                else rec._spine_service_order_vals
            )
            vals, problems = builder()
            if problems:
                if manual:
                    raise UserError(
                        "%s cannot be routed yet: %s." % (rec.name, "; ".join(problems))
                    )
                text = "; ".join(problems)
                if rec.blocker != text:
                    rec.sudo()._guarded().write({"blocker": text})
                continue
            env = self.env if manual else self.env(su=True)
            if rec.target == "work_order":
                target = env[WO_MODEL]._guarded().create(vals)
                link = {"work_order_id": target.id}
            else:
                target = env["fix.service.order"].create(vals)
                link = {"service_order_id": target.id}
            rec.sudo()._guarded().write(
                dict(
                    link,
                    state="routed",
                    blocker=False,
                    route_count=rec.route_count + 1,
                    routed_by_id=self.env.uid if manual else False,
                    routed_at=fields.Datetime.now(),
                )
            )
            rec.message_post(body="Routed to %s." % target.display_name)
        return True

    # ------------------------------------------------------------ actions
    def action_route(self):
        """A person routes a pending demand once its missing fact is filled
        in (or re-routes one whose work order was cancelled). A work order is
        raised by a Facility Manager; a service order by someone M01 lets
        create one, as the M01 intake would."""
        for rec in self:
            if rec.state != "pending":
                raise UserError(
                    "%s is %s: only a pending demand is routed." % (rec.name, rec.state)
                )
            if rec.target == "work_order":
                if not self.env.su and not self.env.user.has_group(FACILITY_MANAGER):
                    raise AccessError("A work order is raised from a demand by a Facility Manager.")
            else:
                self.env["fix.service.order"].check_access("create")
            rec._spine_route(manual=True)
        return True

    def action_dismiss(self, reason=None):
        """No work is needed (the asset was disposed of, the demand is a
        duplicate of a job already raised by hand): dismissed with a reason."""
        reason = (reason or "").strip()
        if not reason:
            raise UserError("State why the demand is dismissed.")
        for rec in self:
            if rec.state != "pending":
                raise UserError("Only a pending demand is dismissed.")
            allowed = (
                (FACILITY_MANAGER,)
                if rec.target == "work_order"
                else (
                    FACILITY_MANAGER,
                    SO_COMMERCIAL_APPROVER,
                )
            )
            if not self.env.su and not any(self.env.user.has_group(g) for g in allowed):
                raise AccessError(
                    "A maintenance demand is dismissed by a Facility Manager%s."
                    % ("" if rec.target == "work_order" else " or a Service Commercial Approver")
                )
            rec._guarded().write(
                {
                    "state": "dismissed",
                    "dismissed_by_id": self.env.uid,
                    "dismissed_at": fields.Datetime.now(),
                    "dismiss_reason": reason,
                }
            )
            rec.message_post(body="Dismissed by %s: %s" % (self.env.user.name, reason))
        return True

    def _spine_reopen_after_cancel(self, work_order):
        """The work order raised for this demand was cancelled: the demand
        goes back to the queue, to be routed again or dismissed."""
        for rec in self.sudo().filtered(lambda d: d.work_order_id == work_order):
            if rec.state != "routed":
                continue
            rec._guarded().write(
                {
                    "state": "pending",
                    "blocker": "work order %s was cancelled: route it again or dismiss it"
                    % work_order.name,
                }
            )
            rec.message_post(body="Work order %s was cancelled." % work_order.name)

    # ------------------------------------------------------------ M48 routing
    @api.model
    def _spine_m48_vals(self, prediction, action=None):
        prediction = prediction.sudo()
        equipment = prediction.equipment_id
        devices = self.env["fix.iot.device"].sudo().search([("equipment_id", "=", equipment.id)])
        customers = devices.mapped("partner_id")
        sites = devices.mapped("site_id")
        vals = {
            "company_id": prediction.company_id.id,
            "operating_unit_id": prediction.operating_unit_id.id,
            "equipment_id": equipment.id,
            "prediction_id": prediction.id,
            "iot_device_id": devices.id if len(devices) == 1 else False,
            "site_id": sites.id if len(sites) == 1 else False,
            "work_type": "maintenance",
            "target": "service_order" if customers else "work_order",
            "partner_id": customers.id if len(customers) == 1 else False,
        }
        what = "Predicted failure of %s (%s) on prediction %s, model %s, %s day(s) to failure" % (
            equipment.name,
            equipment.code or "",
            prediction.name,
            prediction.model_name or "-",
            prediction.estimated_days_to_failure,
        )
        if action:
            action = action.sudo()
            vals.update(
                {
                    "iot_action_id": action.id,
                    "technician_id": action.technician_id.id,
                    "scheduled_date": action.scheduled_on,
                }
            )
            what += ": dispatched action %s (%s, %s priority)" % (
                action.name,
                dict(action._fields["action_type"].selection).get(action.action_type),
                action.priority,
            )
        vals["description"] = what + "."
        return vals, customers

    @api.model
    def _spine_m48_host(self, prediction):
        """An open demand of this prediction, still without an action."""
        return (
            self.sudo()
            .search([("prediction_id", "=", prediction.id), ("state", "in", ("pending", "routed"))])
            .filtered(lambda d: d.state == "pending" or d._spine_target_open())
        )

    def _spine_m48_customer_problem(self, customers):
        if len(customers) > 1:
            text = (
                "the equipment is monitored for several customers (%s): it cannot be told "
                % (", ".join(customers.mapped("display_name")))
                + "whose premises it is on"
            )
            self.sudo()._guarded().write({"blocker": text})

    # ------------------------------------------------------------ consumers
    @api.model
    def consume_iot_action_dispatched(self, event):
        """iot.action_dispatched -> the intervention's work order (internal
        asset) or DRAFT M01 order (customer premises). An open demand of the
        same prediction takes the action instead of raising a second order."""
        action = self.env["fix.iot.action"].sudo().browse(event.get("aggregate_id")).exists()
        if not action or action.state != "dispatched":
            return False
        if self.sudo().search_count([("iot_action_id", "=", action.id)]):
            return True  # redelivery: already taken
        host = self._spine_m48_host(action.prediction_id).filtered(lambda d: not d.iot_action_id)
        if host:
            host = host[0]
            host._guarded().write(
                {
                    "iot_action_id": action.id,
                    "technician_id": host.technician_id.id or action.technician_id.id,
                }
            )
            wo = host.work_order_id
            if wo and wo.state in WO_OPEN:
                wo._guarded().write(
                    {
                        "iot_action_id": action.id,
                        "assigned_to": wo.assigned_to.id or action.technician_id.id,
                    }
                )
                wo.message_post(body="M48 action %s dispatched on this work order." % action.name)
            host.message_post(body="M48 action %s dispatched on this demand." % action.name)
            return True
        vals, customers = self._spine_m48_vals(action.prediction_id, action)
        demand = self._spine_raise("m48_action", action, vals, label=action.name)
        demand._spine_m48_customer_problem(customers)
        return True

    @api.model
    def consume_predictive_wo_created(self, event):
        """predictive_maintenance.wo_created -> the prediction's preventive
        work order (internal) or DRAFT M01 order (customer premises)."""
        Pred = self.env["fix.predictive.maintenance"].sudo()
        prediction = Pred.browse(event.get("aggregate_id")).exists()
        if not prediction or prediction.prediction != "failure_predicted":
            return False
        if self._spine_find(prediction) or self._spine_m48_host(prediction):
            return True  # redelivery, or an action's order already covers it
        vals, customers = self._spine_m48_vals(prediction)
        demand = self._spine_raise("m48_prediction", prediction, vals, label=prediction.name)
        demand._spine_m48_customer_problem(customers)
        return True

    @api.model
    def consume_vehicle_service_due(self, event):
        """vehicle.service_due -> the service's work order on the spine."""
        pm = self.env["fix.vehicle.pm"].sudo().browse(event.get("aggregate_id")).exists()
        if not pm or pm.state != "open":
            return False
        vehicle = pm.vehicle_id
        payload = event.get("payload") or {}
        labels = dict(pm._fields["pm_type"].selection)
        due = []
        if pm.due_date:
            due.append("due %s" % pm.due_date)
        if pm.due_odometer:
            due.append("due at %s km" % pm.due_odometer)
        vals = {
            "company_id": vehicle.company_id.id or self.env.company.id,
            "operating_unit_id": vehicle.operating_unit_id.id,
            "target": "work_order",
            "work_type": "repair" if pm.pm_type == "repair" else "maintenance",
            "vehicle_id": vehicle.id,
            "vehicle_pm_id": pm.id,
            "branch_id": vehicle.branch_id.id,
            "estimated_cost": pm.cost,
            "currency_id": pm.currency_id.id,
            "scheduled_date": pm.scheduled_on,
            "description": "Vehicle %s: %s %s (%s; trigger %s)."
            % (
                vehicle.name or vehicle.license_plate or "",
                labels.get(pm.pm_type),
                pm.name,
                ", ".join(due) or "overdue",
                payload.get("trigger") or "-",
            ),
        }
        self._spine_raise("m46_service", pm, vals, label=pm.name)
        return True

    @api.model
    def consume_equipment_calibration_due(self, event):
        """equipment.calibration_due -> one calibration work order per
        equipment and due date (the 60/30/15/7-day alerts raise it once)."""
        equipment = self.env["fix.equipment"].sudo().browse(event.get("aggregate_id")).exists()
        payload = event.get("payload") or {}
        due = payload.get("due_date") or (
            fields.Date.to_string(equipment.next_calibration) if equipment else None
        )
        if not equipment or not due:
            return False
        vals = {
            "company_id": equipment.company_id.id,
            "operating_unit_id": equipment.operating_unit_id.id,
            "target": "work_order",
            "work_type": "inspection",
            "equipment_id": equipment.id,
            "branch_id": equipment.branch_id.id,
            "calibration_due": due,
            "scheduled_date": due,
            "technician_id": equipment.custodian_id.id,
            "description": "Calibration of %s (%s) due %s: calibrate and record the "
            "calibration with its certificate in M45." % (equipment.name, equipment.code, due),
        }
        self._spine_raise(
            "m45_calibration",
            equipment,
            vals,
            key=due,
            label="%s calibration due %s" % (equipment.code, due),
        )
        return True

    @api.model
    def consume_device_maintenance_due(self, event):
        """device.maintenance_due -> the DRAFT M01 preventive order for the
        owner's device, once per plan due date and never beside an open one."""
        payload = event.get("payload") or {}
        plan = self.env["fix.device.pm"].sudo().browse(payload.get("plan_id")).exists()
        if not plan:
            return False
        due = payload.get("due_date") or fields.Date.to_string(plan.next_due)
        if self._spine_find(plan, due):
            return True
        if any(
            d._spine_target_open() or d.state == "pending"
            for d in self.sudo().search([("device_pm_id", "=", plan.id)])
        ):
            return True  # the plan's earlier order is still open
        device = plan.device_id
        labels = dict(plan._fields["plan_type"].selection)
        vals = {
            "company_id": device.company_id.id or self.env.company.id,
            "target": "service_order",
            "device_id": device.id,
            "device_pm_id": plan.id,
            "partner_id": device.owner_id.id,
            "branch_id": device.branch_id.id,
            "scheduled_date": due,
            "description": "Preventive maintenance of %s under plan %s (%s), due %s."
            % (device.display_name, plan.name, labels.get(plan.plan_type), due),
        }
        if "operating_unit_id" in device._fields:
            vals["operating_unit_id"] = device.operating_unit_id.id
        self._spine_raise(
            "m17_device_pm", plan, vals, key=due, label="%s due %s" % (plan.name, due)
        )
        return True

    @api.model
    def consume_vehicle_assigned(self, event):
        """vehicle.assigned -> a vehicle booked for duty on a day its spine
        work order is scheduled, or while that work is in progress, is flagged
        on the work order and to the person who booked it (once per pair)."""
        Assignment = self.env["fix.vehicle.assignment"].sudo()
        assignment = Assignment.browse(event.get("aggregate_id")).exists()
        if not assignment:
            return False
        today = _today(self.env)
        orders = (
            self.env[WO_MODEL]
            .sudo()
            .search(
                [
                    ("vehicle_id", "=", assignment.vehicle_id.id),
                    ("state", "in", ("draft", "scheduled", "in_progress")),
                ]
            )
        )
        label = assignment.vehicle_id.name or assignment.vehicle_id.license_plate or ""
        for wo in orders:
            clash = wo.scheduled_date == assignment.date or (
                wo.state == "in_progress" and assignment.date <= today
            )
            if not clash or assignment in wo.spine_conflict_assignment_ids:
                continue
            wo._guarded().write({"spine_conflict_assignment_ids": [(4, assignment.id)]})
            text = "Vehicle %s is booked for duty on %s while maintenance work order %s is %s." % (
                label,
                assignment.date,
                wo.name,
                dict(wo._fields["state"].selection)[wo.state].lower(),
            )
            wo.message_post(body=text)
            assignment.message_post(body=text)
            booker = assignment.create_uid
            if booker and booker._is_internal() and not booker._is_superuser():
                assignment.activity_schedule(
                    "mail.mail_activity_data_todo",
                    user_id=booker.id,
                    summary="Vehicle under maintenance: rebook or reschedule",
                    note=text,
                )
        return True

    # ------------------------------------------------------------ cron
    @api.model
    def cron_maintenance_due(self):
        """Daily: each open M45 PM / corrective job that is due raises its
        work order once (M45 publishes no due event), and every demand still
        pending is retried (a site may have been set up for its branch)."""
        today = _today(self.env)
        for pm in (
            self.env["fix.equipment.pm"]
            .sudo()
            .search([("state", "=", "open"), ("scheduled_on", "<=", today)])
        ):
            equipment = pm.equipment_id
            labels = dict(pm._fields["pm_type"].selection)
            vals = {
                "company_id": pm.company_id.id or equipment.company_id.id,
                "operating_unit_id": (pm.operating_unit_id or equipment.operating_unit_id).id,
                "target": "work_order",
                "work_type": "repair" if pm.pm_type == "corrective" else "maintenance",
                "equipment_id": equipment.id,
                "equipment_pm_id": pm.id,
                "branch_id": equipment.branch_id.id,
                "technician_id": pm.technician_id.id,
                "estimated_cost": pm.cost,
                "currency_id": pm.currency_id.id,
                "scheduled_date": pm.scheduled_on,
                "description": "%s job %s on %s (%s), scheduled %s%s."
                % (
                    labels.get(pm.pm_type),
                    pm.name,
                    equipment.name,
                    equipment.code,
                    pm.scheduled_on,
                    ": %s" % pm.notes if pm.notes else "",
                ),
            }
            self._spine_raise("m45_pm", pm, vals, label=pm.name)
        self.sudo().search([("state", "=", "pending")])._spine_route()
        return True
