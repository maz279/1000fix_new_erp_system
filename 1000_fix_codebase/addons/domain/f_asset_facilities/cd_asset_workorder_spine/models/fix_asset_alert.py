# A07: an alert that reaches a person. The crons announced expiring documents,
# licences, warranties and consents as events, and no consumer read them: the workspace
# text said "alerts at 60/30/15/7/1 days" and nobody was told. Each event below becomes
# one open row on the owning module's Alerts screen, with a to-do for each holder of the
# role that must act. A repeat raises the count on the open row, not a new row.
from odoo import api, fields, models
from odoo.exceptions import UserError

MODULES = [
    ("M17", "M17 Device Registry"),
    ("M45", "M45 Test Equipment"),
    ("M46", "M46 Fleet"),
    ("M47", "M47 Facilities"),
    ("M48", "M48 IoT"),
]

FLEET = "fleet.fleet_group_user"
LOGISTICS = "cd_vehicle_ext.group_logistics_manager"
FACILITY = "cd_facility.group_facility_manager"
BRANCH_LEAD = "cd_facility.group_branch_operations_lead"
OPS_DIRECTOR = "cd_facility.group_operations_director"
QUALITY = "cd_equipment_register.group_quality_manager"
CUSTODIAN = "cd_equipment_register.group_equipment_custodian"
WARRANTY = "cd_device_registry.group_warranty_officer"
DEVICE_AGENT = "cd_device_registry.group_device_registry_user"
IOT_OPERATOR = "cd_stream_registry.group_iot_operator"
IOT_ADMIN = "cd_stream_registry.group_iot_admin"
CONSENT = "cd_stream_registry.group_iot_consent_officer"

# event -> (module, the role that must act, what it tells them)
ROUTES = {
    "device.warranty_expiring": ("M17", WARRANTY, "Warranty cover is about to end"),
    "device.warranty_expired": ("M17", WARRANTY, "Warranty cover has ended"),
    "device.neir_deregistration_required": (
        "M17",
        DEVICE_AGENT,
        "This transfer needs NEIR de-registration",
    ),
    "equipment.calibration.overdue": ("M45", QUALITY, "Calibration is overdue"),
    "equipment.custody_overdue": ("M45", CUSTODIAN, "Issued equipment has not come back"),
    "equipment.out_of_tolerance": ("M45", QUALITY, "A calibration found out-of-tolerance readings"),
    "vehicle.document_expiring": ("M46", FLEET, "A statutory document is about to expire"),
    "vehicle.document_expired": ("M46", FLEET, "A statutory document has expired"),
    "driver.licence_expiring": ("M46", FLEET, "A driver's licence is about to expire"),
    "driver.licence_expired": ("M46", FLEET, "A driver's licence has expired"),
    "vehicle.fuel_exception": ("M46", LOGISTICS, "A fuel entry is held for review"),
    "site.compliance_expiring": ("M47", FACILITY, "A statutory licence is about to expire"),
    "site.compliance_expired": ("M47", BRANCH_LEAD, "A statutory licence has lapsed"),
    "site.risk_exception_raised": ("M47", BRANCH_LEAD, "An operating-risk decision is needed"),
    "site.utility_anomaly": ("M47", FACILITY, "A utility bill is held as an anomaly"),
    "lease.critical_date_due": ("M47", FACILITY, "A lease critical date is due"),
    "lease.renewal_decision_required": ("M47", FACILITY, "A lease renewal decision is needed"),
    "site.power_test_overdue": (
        "M47",
        OPS_DIRECTOR,
        "A generator or UPS test was missed (BRU-FAC-10)",
    ),
    "iot.rule_alert_raised": ("M48", IOT_OPERATOR, "A sensor rule raised an alert"),
    "telemetry.stream_suspended": ("M48", IOT_ADMIN, "A telemetry stream was suspended"),
    "telemetry.consent_revoked": ("M48", CONSENT, "Telemetry consent was revoked"),
}


class FixAssetAlert(models.Model):
    _name = "fix.asset.alert"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Asset & Facility Alert"
    _order = "state desc, last_raised_on desc, id desc"

    name = fields.Char(string="Alert", required=True, readonly=True)
    module = fields.Selection(MODULES, required=True, readonly=True, index=True)
    event_type = fields.Char(string="Event", required=True, readonly=True, index=True)
    res_model = fields.Char(string="Record Type", readonly=True)
    res_id = fields.Integer(string="Record ID", readonly=True)
    record_label = fields.Char(string="Record", readonly=True)
    role_group = fields.Char(string="Role", readonly=True, help="The role asked to act.")
    no_holder = fields.Boolean(
        string="No One Holds the Role",
        readonly=True,
        help="Nobody holds the role that must act, so no one has been given a to-do. "
        "Appoint someone: the alert stays open here until then.",
    )
    raise_count = fields.Integer(string="Times Raised", default=1, readonly=True)
    last_raised_on = fields.Datetime(string="Last Raised", readonly=True)
    state = fields.Selection(
        [("open", "Open"), ("acknowledged", "Acknowledged")],
        default="open",
        required=True,
        readonly=True,
        index=True,
    )
    acknowledged_by_id = fields.Many2one("res.users", string="Acknowledged By", readonly=True)
    acknowledged_on = fields.Datetime(string="Acknowledged On", readonly=True)
    company_id = fields.Many2one(
        "res.company", required=True, readonly=True, default=lambda self: self.env.company
    )

    @api.model
    def consume_asset_alert(self, event):
        """Every routed event. Idempotent per event: its id is kept on the row's log."""
        route = ROUTES.get(event.get("event_type"))
        if not route:
            return False
        module, group_xmlid, text = route
        res_model = event.get("aggregate") or False
        res_id = event.get("aggregate_id") or 0
        now = fields.Datetime.now()
        Alert = self.sudo()
        record = False
        if res_model in self.env and res_id:
            record = self.env[res_model].sudo().browse(res_id).exists()
        label = record.display_name if record else "%s #%s" % (res_model or "", res_id)
        company = (
            event.get("company_id")
            or (record and "company_id" in record._fields and record.company_id.id)
            or self.env.company.id
        )
        existing = Alert.search(
            [
                ("event_type", "=", event["event_type"]),
                ("res_model", "=", res_model),
                ("res_id", "=", res_id),
                ("state", "=", "open"),
            ],
            limit=1,
        )
        if existing:
            existing.write({"raise_count": existing.raise_count + 1, "last_raised_on": now})
            return True
        group = self.env.ref(group_xmlid, raise_if_not_found=False)
        holders = group.sudo().all_user_ids.filtered("active") if group else self.env["res.users"]
        holders = holders.filtered(lambda u: not u.share)
        alert = Alert.create(
            {
                "name": "%s: %s" % (text, label),
                "module": module,
                "event_type": event["event_type"],
                "res_model": res_model,
                "res_id": res_id,
                "record_label": label,
                "role_group": group.display_name if group else group_xmlid,
                "no_holder": not holders,
                "last_raised_on": now,
                "company_id": company,
            }
        )
        todo = self.env.ref("mail.mail_activity_data_todo", raise_if_not_found=False)
        if todo:
            for user in holders:
                alert.activity_schedule(
                    activity_type_id=todo.id,
                    summary=alert.name[:200],
                    user_id=user.id,
                )
        return True

    def action_acknowledge(self):
        """Someone holding the role has seen it. It does not fix the cause."""
        for rec in self.sudo():
            if rec.state != "open":
                raise UserError(self.env._("%s is already acknowledged.", rec.name))
            route = ROUTES.get(rec.event_type)
            group_xmlid = route and route[1]
            if group_xmlid and not self.env.user.has_group(group_xmlid):
                raise UserError(
                    self.env._("Acknowledging this alert needs the %s role.", rec.role_group)
                )
            rec.write(
                {
                    "state": "acknowledged",
                    "acknowledged_by_id": self.env.user.id,
                    "acknowledged_on": fields.Datetime.now(),
                }
            )
            rec.activity_ids.action_feedback(feedback="Acknowledged")
        return True
