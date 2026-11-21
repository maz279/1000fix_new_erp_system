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
from odoo.exceptions import AccessError, UserError, ValidationError

from libs.py.fix_events import publish

WO_MODEL = "fix.facility.work.order"
WO_OPEN = ("draft", "scheduled", "in_progress", "completed")
SO_CLOSED = ("delivered", "closed", "cancelled")
# Where a work order may be raised (cd_facility: WO_SITE_STATES).
SITE_OPEN = ("active", "suspended")
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
    # A07 P1 wiring round 2 (2026-11-04): a failed pre-use check and a silent
    # telematics device of an M46 vehicle
    ("m46_defect", "M46 Vehicle Defect (Failed Check)"),
    ("m46_telematics", "M46 Telematics Device Silent"),
    ("m48_prediction", "M48 Predicted Failure"),
    ("m48_action", "M48 Dispatched Intervention"),
    ("m17_device_pm", "M17 Device Maintenance Plan"),
    # A07 ERP audit (2026-11-20) M48-15 / M48-13: a major or critical rule alert,
    # and a health index that fell a band, raise an inspection by the owner.
    ("m48_alert", "M48 Rule Alert (Inspection)"),
    ("m48_health", "M48 Health Degraded (Inspection)"),
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
    "entitlement_state",
    "commercial_route",
    "contract_ref_id",
}
NO_KEY = "-"
# M48-04: who pays for work on a customer's device.
ENTITLEMENT_STATES = [
    ("internal", "Company Asset"),
    ("entitled", "Entitled (Contract + Proactive Consent)"),
    ("no_contract", "No Contract Covers It"),
    ("no_consent", "No Proactive-Service Consent"),
    ("model_suspended", "Model Suspended From Customer Use"),
]


def _today(env):
    return fields.Date.context_today(env["res.users"].with_context(tz=DHAKA))


LOT_MODEL = "fix.stock.lot"


class FixDeviceComponentPickers(models.Model):
    """A07 operability (2026-11-07): the causing job and stock lot of a fitted
    part are references by id, because the registry loads before M01 and M15, and
    a person knows neither id. These pick the record and write the reference.

    A07 ERP audit (2026-11-20) LEAD-01: the lot picker offered Odoo's stock.lot,
    which the estate does not use (0 rows on fix_real): M15 lots are
    fix.stock.lot of a fix.spare.part, so a recalled lot could never be traced to
    the devices it went into. The picker now offers M15 lots of the component's
    part, and writes the reference as a fix.stock.lot."""

    _inherit = "fix.device.component"

    causing_order_id = fields.Many2one(
        "fix.service.order",
        string="Causing Job",
        compute="_compute_reference_pickers",
        inverse="_inverse_causing_order",
    )
    stock_lot_ref_id = fields.Many2one(
        LOT_MODEL,
        string="Stock Lot (M15)",
        compute="_compute_reference_pickers",
        inverse="_inverse_stock_lot",
        domain="[('part_id.part_number', '=', part_number)]",
        help="The M15 serial or lot of the part fitted: a lot of the same part number.",
    )

    @api.depends("service_order_id", "lot_id", "lot_model")
    def _compute_reference_pickers(self):
        Order = self.env["fix.service.order"].sudo()
        Lot = self.env[LOT_MODEL].sudo()
        for rec in self:
            rec.causing_order_id = Order.browse(rec.service_order_id or 0).exists().id
            rec.stock_lot_ref_id = (
                Lot.browse(rec.lot_id or 0).exists().id if rec.lot_model == LOT_MODEL else False
            )

    def _inverse_causing_order(self):
        for rec in self:
            rec.service_order_id = rec.causing_order_id.id or False

    def _inverse_stock_lot(self):
        for rec in self:
            lot = rec.stock_lot_ref_id.sudo()
            if (
                lot
                and rec.part_number
                and (lot.part_id.part_number or "").strip().upper()
                != (rec.part_number or "").strip().upper()
            ):
                raise ValidationError(
                    "Lot %s is of part %s, not of the fitted part %s."
                    % (lot.name, lot.part_id.part_number, rec.part_number)
                )
            rec.lot_model = LOT_MODEL
            rec.lot_id = lot.id or False

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if len(self) == 1 and self.state == "removed":
            locked |= {"causing_order_id", "stock_lot_ref_id"}
        return locked


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
    # M48-04: who pays for work on a customer's device, decided before an order.
    entitlement_state = fields.Selection(
        ENTITLEMENT_STATES, string="Entitlement", readonly=True, copy=False
    )
    commercial_route = fields.Selection(
        [
            ("internal", "Internal (company asset)"),
            ("contract", "Under Contract"),
            ("opportunity", "M07 Opportunity (no order raised)"),
        ],
        string="Commercial Route",
        readonly=True,
        copy=False,
    )
    contract_ref_id = fields.Many2one(
        "fix.contract", string="Contract (M08)", readonly=True, copy=False
    )
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
        if site.state not in SITE_OPEN:
            return None, [
                "site %s is %s: choose an operational or a suspended site"
                % (site.name, dict(site._fields["state"].selection)[site.state])
            ]
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
        vals = {
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
        }
        if self.commercial_route == "contract" and self.contract_ref_id:
            # M48-04 / AUT-IOT-14: entitled proactive work is delivered under the
            # contract, not as a standard chargeable order.
            vals["order_category"] = "amc"
            if "contract_id" in self.env["fix.service.order"]._fields:
                vals["contract_id"] = self.contract_ref_id.id
        return vals, []

    def _spine_route(self, manual=False):
        """Route each pending demand to its target. Automatic routing (the
        consumers, the cron) runs as superuser and leaves a demand it cannot
        route pending with what it needs; a person's routing raises it."""
        for rec in self:
            if rec.state != "pending":
                continue
            if (
                not manual
                and rec.target == "service_order"
                and rec.commercial_route == "opportunity"
            ):
                # M48-04: never auto-create customer-chargeable work without an
                # entitlement and the customer's proactive-service consent. A
                # person may route it once the customer has accepted the work.
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
            rec._spine_release_prediction(reason)
        return True

    def _spine_release_prediction(self, reason):
        """A07 (2026-11-07): the prediction's "requested" flag stayed set after its
        only demand was dismissed, so no preventive order could ever be asked for
        again. With no demand of the prediction left alive, the request is over."""
        self.ensure_one()
        prediction = self.prediction_id.sudo()
        if not prediction.work_order_created:
            return
        if self.sudo().search_count(
            [("prediction_id", "=", prediction.id), ("state", "!=", "dismissed")], limit=1
        ):
            return
        # A07 ERP audit (2026-11-20) M48-03: the approved request (an action) is
        # over too, or a new request would find it "under way".
        request = prediction.preventive_action_id.sudo()
        if request and request.state in ("proposed", "approved"):
            request._approval_void("demand %s dismissed: %s" % (self.name, reason))
            request._guarded().write(
                {
                    "state": "cancelled",
                    "cancelled_by": self.env.uid,
                    "cancelled_on": fields.Datetime.now(),
                    "cancel_reason": "demand %s dismissed: %s" % (self.name, reason),
                }
            )
        prediction._guarded().write({"work_order_created": False, "preventive_action_id": False})
        prediction.message_post(
            body="The preventive work order request was withdrawn: demand %s was dismissed "
            "(%s). It can be requested again." % (self.name, reason)
        )

    @api.model
    def _spine_order_closed(self, orders):
        """A07 operability (2026-11-07) M17: an M17 plan's preventive order closed
        and the plan stayed due, with Mark Done the only way on. Closing the order
        is that visit: the demand is done and the plan rolls. A plan paused since
        keeps its date; the demand is still done, as its work was."""
        demands = self.sudo().search(
            [
                ("service_order_id", "in", orders.ids),
                ("device_pm_id", "!=", False),
                ("state", "=", "routed"),
            ]
        )
        for rec in demands:
            plan = rec.device_pm_id
            rolled = plan.state == "active"
            if rolled:
                plan.action_complete()
            rec._guarded().write({"state": "done"})
            rec.message_post(
                body="Service order %s closed. %s"
                % (
                    rec.service_order_id.name,
                    "Plan %s rolled on to %s." % (plan.name, plan.next_due)
                    if rolled
                    else "Plan %s is paused and keeps its date." % plan.name,
                )
            )

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
    def _spine_m48_devices(self, prediction):
        """The M48 devices on the prediction's asset."""
        prediction = prediction.sudo()
        Device = self.env["fix.iot.device"].sudo()
        if prediction.equipment_id:
            return Device.search([("equipment_id", "=", prediction.equipment_id.id)])
        if prediction.vehicle_id:
            return Device.search([("vehicle_id", "=", prediction.vehicle_id.id)])
        if prediction.customer_device_id:
            return Device.search([("customer_device_id", "=", prediction.customer_device_id.id)])
        return Device

    @api.model
    def _spine_m48_customer_device(self, prediction):
        """The customer's M17 device the work is done on, or an empty set."""
        prediction = prediction.sudo()
        if prediction.customer_device_id:
            return prediction.customer_device_id
        if prediction.vehicle_id:
            return self.env["fix.device"]
        found = self.env["fix.device"]
        for device in self._spine_m48_devices(prediction):
            found |= device._fix_customer_device()
        return found if len(found) == 1 else self.env["fix.device"]

    @api.model
    def _spine_m48_vals(self, prediction, action=None):
        """A07 ERP audit (2026-11-20) M48-05: the asset decides the route. A
        vehicle goes to its M46 work order on the spine; a customer's M17 device
        to an M01 order - only when entitled (M48-04); company equipment to the
        M47 work order."""
        prediction = prediction.sudo()
        equipment = prediction.equipment_id
        vehicle = prediction.vehicle_id
        devices = self._spine_m48_devices(prediction)
        device = self._spine_m48_customer_device(prediction)
        customers = devices.mapped("partner_id") | device.owner_id
        sites = devices.mapped("site_id")
        vals = {
            "company_id": prediction.company_id.id,
            "operating_unit_id": prediction.operating_unit_id.id,
            "equipment_id": equipment.id,
            "vehicle_id": vehicle.id,
            "prediction_id": prediction.id,
            "iot_device_id": devices.id if len(devices) == 1 else False,
            "site_id": sites.id if len(sites) == 1 else False,
            "work_type": "maintenance",
            "target": "service_order" if (customers or device) and not vehicle else "work_order",
            "partner_id": customers.id if len(customers) == 1 else False,
            "device_id": device.id,
            "entitlement_state": "internal",
            "commercial_route": "internal",
        }
        if vehicle:
            vals["branch_id"] = vehicle.branch_id.id
        if vals["target"] == "service_order":
            vals.update(self._spine_m48_commercial(prediction, device))
        asset = prediction._fix_prediction_asset()
        what = "Predicted failure of %s on prediction %s, model %s, %s day(s) to failure" % (
            "%s (%s)" % (equipment.name, equipment.code or "") if equipment else asset.display_name,
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
            what += ": dispatched action %s (%s, %s priority)%s" % (
                action.name,
                dict(action._fields["action_type"].selection).get(action.action_type),
                action.priority,
                self._spine_m48_needs(action),
            )
        vals["description"] = what + "."
        return vals, customers

    @api.model
    def _spine_m48_needs(self, action):
        """M48-07: the parts and skill the intervention needs ride on the order."""
        parts = [
            "%s x %s (%s)" % (p.quantity, p.product_id.display_name, p.availability)
            for p in action.part_ids
        ]
        text = ""
        if parts:
            text += "; parts: %s" % ", ".join(parts)
        if (action.skill_code or "").strip():
            text += "; skill: %s%s" % (
                action.skill_code.strip(),
                " (dispatched without it: %s)" % action.skill_override_reason
                if (action.skill_override_reason or "").strip()
                else "",
            )
        return text

    @api.model
    def _spine_m48_commercial(self, prediction, device):
        """M48-04: entitlement before any customer work."""
        if not device:
            return {"entitlement_state": "no_contract", "commercial_route": "opportunity"}
        suspended = prediction._fix_customer_use_problem()
        if suspended:
            return {"entitlement_state": "model_suspended", "commercial_route": "opportunity"}
        state, contract, _why = self._spine_entitlement(device)
        return {
            "entitlement_state": state,
            "commercial_route": "contract" if state == "entitled" else "opportunity",
            "contract_ref_id": contract.id if contract else False,
        }

    def _spine_m48_opportunity(self):
        """A demand the customer is not entitled to: no order; the account owner
        is offered the work as an M07 opportunity (once per demand)."""
        for rec in self.filtered(
            lambda d: d.commercial_route == "opportunity" and d.state == "pending"
        ):
            reason = dict(ENTITLEMENT_STATES).get(rec.entitlement_state) or "not entitled"
            text = (
                "no order is raised for the customer's device: %s. The work is offered to the "
                "customer as an M07 opportunity; route it once they accept" % reason.lower()
            )
            if rec._spine_log(
                "opportunity:%s" % rec.id, "M07 opportunity published (%s)." % reason
            ):
                rec.sudo()._guarded().write({"blocker": text})
                publish(
                    rec.env,
                    "iot.proactive_opportunity",
                    "fix.maintenance.demand",
                    rec.id,
                    {
                        "demand": rec.name,
                        "partner_id": rec.partner_id.id or False,
                        "device_id": rec.device_id.id or False,
                        "prediction": rec.prediction_id.name or "",
                        "entitlement_state": rec.entitlement_state or "",
                        "description": rec.description or "",
                    },
                )

    @api.model
    def consume_iot_proactive_opportunity(self, event):
        """iot.proactive_opportunity -> one M07 opportunity (crm.lead) for the
        account, idempotent per demand. Read softly: M07 (crm) may be absent."""
        demand = self.sudo().browse(event.get("aggregate_id")).exists()
        Lead = self.env.get("crm.lead")
        if not demand or Lead is None:
            return False
        marker = "[M48 demand %s]" % demand.id
        if (
            Lead.sudo()
            .with_context(active_test=False)
            .search_count([("description", "ilike", marker)], limit=1)
        ):
            return True
        lead = Lead.sudo().create(
            {
                "name": "Proactive service: %s" % (demand.device_id.display_name or demand.name),
                "type": "opportunity",
                "partner_id": demand.partner_id.id or False,
                "company_id": demand.company_id.id,
                "description": "%s %s\nEntitlement: %s."
                % (marker, demand.description or "", demand.entitlement_state or "-"),
            }
        )
        demand._spine_log("lead:%s" % lead.id, "M07 opportunity %s opened." % lead.display_name)
        return True

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
        demand._spine_m48_opportunity()
        return True

    @api.model
    def consume_predictive_wo_created(self, event):
        """predictive_maintenance.wo_created -> the prediction's preventive
        work order (internal) or DRAFT M01 order (customer premises)."""
        Pred = self.env["fix.predictive.maintenance"].sudo()
        prediction = Pred.browse(event.get("aggregate_id")).exists()
        if not prediction or prediction.prediction != "failure_predicted":
            return False
        if not prediction.work_order_created:
            return True  # redelivered after the request was withdrawn by a dismissal
        # A07 ERP audit (2026-11-20) M48-03: only an APPROVED preventive request
        # raises work (the event is published by the approval).
        request = prediction.preventive_action_id
        if not request or request.state not in ("approved", "dispatched", "done"):
            return False
        if self._spine_m48_host(prediction):
            return True  # an action's order already covers it
        earlier = (
            self.sudo()
            .with_context(active_test=False)
            .search(
                [("source_model", "=", prediction._name), ("source_res_id", "=", prediction.id)]
            )
        )
        if earlier.filtered(lambda d: d.state != "dismissed"):
            return True  # redelivery
        # One demand per request: a request made again after a dismissal is a new
        # source item, or the UNIQUE key would hand back the dismissed demand.
        key = "request-%d" % (len(earlier) + 1) if earlier else NO_KEY
        vals, customers = self._spine_m48_vals(prediction)
        # D17(c): the approval pinned the date; the order is scheduled on it.
        vals["scheduled_date"] = request.scheduled_on
        vals["description"] += " Preventive request %s approved by %s for %s." % (
            request.name,
            request.approved_by.name or "-",
            request.scheduled_on,
        )
        demand = self._spine_raise(
            "m48_prediction", prediction, vals, key=key, label=prediction.name
        )
        demand._spine_m48_customer_problem(customers)
        demand._spine_m48_opportunity()
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
