# fix_msp_engines — M05 iteration 2: the compliance engines the module
# charter names (runbooks, patching, SLA credits, on-call rota, maintenance
# windows, problem & change) plus the estate polish the workspace screens
# showed missing on 2026-10-26 (asset display names, health scoring, SLA %
# display, contract SLA target).
#
# FILE NAME IS LOAD-BEARING: fix_msp < fix_msp_engines < fix_msp_ext keeps
# the alphabetical import order in models/__init__.py correct.
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError

from libs.py.fix_events import publish

# ---------------------------------------------------------------- runbooks


class FixMspRunbook(models.Model):
    """A remediation runbook: the steps an operator (or a future automation
    agent) runs against an unhealthy asset. Executions are RECORDED —
    action_execute logs a run; it never pretends the platform itself ran
    a script on the device."""

    _name = "fix.msp.runbook"
    _description = "MSP Runbook"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True)
    trigger = fields.Selection(
        [
            ("manual", "Manual"),
            ("alert_major", "Major Alert"),
            ("asset_offline", "Asset Offline"),
            ("health_degraded", "Health Degraded"),
        ],
        default="manual",
        required=True,
        help="When this runbook applies; auto_run books it for the on-call "
        "technician when the condition fires",
    )
    scope_contract_id = fields.Many2one(
        "fix.msp.contract", string="Scoped To Contract", help="Empty = every contract"
    )
    script = fields.Text(required=True, string="Remediation Steps")
    auto_run = fields.Boolean(
        string="Auto-Run", default=False, help="Booked automatically when the trigger fires"
    )
    auto_resolve_alert = fields.Boolean(
        string="Resolve Alert on Success",
        default=False,
        help="A successful execution resolves the asset's open alert with a note",
    )
    active = fields.Boolean(default=True)
    run_ids = fields.One2many("fix.msp.runbook.run", "runbook_id", string="Executions")
    run_count = fields.Integer(compute="_compute_run_stats", string="Executions")
    last_run_at = fields.Datetime(compute="_compute_run_stats", string="Last Execution")

    @api.depends("run_ids.finished_at")
    def _compute_run_stats(self):
        for book in self:
            book.run_count = len(book.run_ids)
            book.last_run_at = max(
                (r.finished_at or r.started_at for r in book.run_ids), default=False
            )

    def action_execute(self, asset=None, alert_id=None):
        """Record an execution of this runbook against an asset. ``asset``
        accepts an asset id or an agent identifier (the workspace prompt
        sends free text). The run is created and finished in one call —
        the operator clicks AFTER performing the steps; optionally the
        asset's open alert is resolved with a note."""
        for book in self:
            if not book.active:
                raise UserError("Runbook %s is archived — reactivate it first" % book.name)
            Asset = self.env["fix.monitored.asset"]
            if isinstance(asset, str) and asset.strip():
                target = Asset.search(
                    ["|", ("agent_id", "=", asset.strip()), ("hostname", "=", asset.strip())],
                    limit=1,
                )
                if not target:
                    raise UserError("No monitored asset matches '%s'" % asset)
            elif isinstance(asset, int) and asset:
                target = Asset.browse(asset)
                if not target.exists():
                    raise UserError("Monitored asset %s does not exist" % asset)
            else:
                domain = (
                    [("msp_contract_id", "=", book.scope_contract_id.id)]
                    if book.scope_contract_id
                    else []
                )
                target = Asset.search(domain, limit=1)
                if not target:
                    raise UserError("No monitored asset in scope — name one explicitly")
            alert = None
            if alert_id:
                alert = self.env["fix.msp.alert"].browse(int(alert_id)).exists()
            run = self.env["fix.msp.runbook.run"].create(
                {
                    "runbook_id": book.id,
                    "asset_id": target.id,
                    "alert_id": alert.id if alert else False,
                    "state": "success",
                    "started_at": fields.Datetime.now(),
                    "finished_at": fields.Datetime.now(),
                    "output_note": "Executed via workspace/ops console",
                }
            )
            if book.auto_resolve_alert and not alert:
                alert = self.env["fix.msp.alert"].search(
                    [
                        ("asset_id", "=", target.id),
                        ("state", "in", ("new", "acked", "ticketed")),
                    ],
                    limit=1,
                )
            if book.auto_resolve_alert and alert and alert.state != "resolved":
                alert.action_resolve(note="Runbook '%s' executed (run #%s)" % (book.name, run.id))
            publish(
                self.env,
                "msp.runbook_executed",
                "fix.msp.runbook.run",
                run.id,
                {"runbook": book.name, "asset": target.agent_id},
            )
        return True


class FixMspRunbookRun(models.Model):
    """One recorded execution of a runbook (accountability log)."""

    _name = "fix.msp.runbook.run"
    _description = "MSP Runbook Execution"
    _order = "started_at desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    runbook_id = fields.Many2one("fix.msp.runbook", required=True, ondelete="cascade")
    asset_id = fields.Many2one("fix.monitored.asset", required=True)
    alert_id = fields.Many2one("fix.msp.alert", string="Alert", ondelete="set null")
    state = fields.Selection(
        [("running", "Running"), ("success", "Success"), ("failed", "Failed")],
        default="running",
        required=True,
    )
    started_at = fields.Datetime(default=fields.Datetime.now, required=True)
    finished_at = fields.Datetime(readonly=True)
    output_note = fields.Char(string="Output / Note")

    def action_finish(self, note="", ok=True):
        """Close a running execution with the operator's outcome."""
        for run in self:
            if run.state != "running":
                raise UserError("Execution %s already finished (%s)" % (run.id, run.state))
            run.write(
                {
                    "state": (ok and "success") or "failed",
                    "finished_at": fields.Datetime.now(),
                    "output_note": note or run.output_note,
                }
            )


# -------------------------------------------------------------- patching


class FixMspPatchPolicy(models.Model):
    """How patches behave for a contract (or globally when no contract)."""

    _name = "fix.msp.patch.policy"
    _description = "MSP Patch Policy"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True)
    msp_contract_id = fields.Many2one(
        "fix.msp.contract", string="Scoped To Contract", help="Empty = estate-wide default"
    )
    category = fields.Selection(
        [("os", "OS"), ("third_party", "Third-Party"), ("firmware", "Firmware")],
        default="os",
        required=True,
    )
    auto_approve = fields.Boolean(
        default=False, help="Missing updates are pre-approved without a review step"
    )
    max_defer_days = fields.Integer(default=7, string="Max Defer Days")
    active = fields.Boolean(default=True)


class FixMspPatchUpdate(models.Model):
    """A patch an asset needs — the compliance register's atom."""

    _name = "fix.msp.patch.update"
    _description = "MSP Patch Update"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    msp_contract_id = fields.Many2one("fix.msp.contract", required=True, index=True)
    asset_id = fields.Many2one("fix.monitored.asset", required=True, index=True)
    identifier = fields.Char(string="Patch ID", help="e.g. KB5034441, chrome-128")
    title = fields.Char(required=True)
    severity = fields.Selection(
        [("critical", "Critical"), ("high", "High"), ("medium", "Medium"), ("low", "Low")],
        default="medium",
        required=True,
    )
    category = fields.Selection(
        [("os", "OS"), ("third_party", "Third-Party"), ("firmware", "Firmware")],
        default="os",
        required=True,
    )
    state = fields.Selection(
        [
            ("missing", "Missing"),
            ("approved", "Approved"),
            ("installed", "Installed"),
            ("failed", "Failed"),
            ("deferred", "Deferred"),
        ],
        default="missing",
        required=True,
        tracking=True,
    )
    approved_date = fields.Date(readonly=True)
    installed_at = fields.Datetime(readonly=True)
    deferred_until = fields.Date()
    fail_note = fields.Char(string="Failure Note", copy=False)

    # Odoo 19: models.Constraint replaces the legacy _sql_constraints list
    _asset_patch_unique = models.Constraint(
        "UNIQUE (asset_id, identifier)", "This patch is already tracked for the asset"
    )

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        auto = records.filtered(
            lambda u: u.state == "missing"
            and self.env["fix.msp.patch.policy"].search(
                [
                    "|",
                    ("msp_contract_id", "=", False),
                    ("msp_contract_id", "=", u.msp_contract_id.id),
                    ("category", "=", u.category),
                    ("auto_approve", "=", True),
                ],
                limit=1,
            )
        )
        if auto:
            auto.write({"state": "approved", "approved_date": fields.Date.today()})
        return records

    def action_approve(self):
        for upd in self:
            if upd.state not in ("missing", "deferred"):
                raise UserError("Patch %s cannot be approved from state '%s'" % (upd.id, upd.state))
            upd.write({"state": "approved", "approved_date": fields.Date.today()})

    def action_install(self):
        for upd in self:
            if upd.state not in ("approved", "missing", "deferred", "failed"):
                raise UserError("Patch %s already installed" % upd.id)
            upd.write({"state": "installed", "installed_at": fields.Datetime.now()})
            publish(
                self.env,
                "msp.patch_installed",
                "fix.msp.patch.update",
                upd.id,
                {"patch": upd.identifier or upd.title, "asset": upd.asset_id.agent_id},
            )

    def action_defer(self, days=7):
        for upd in self:
            if upd.state == "installed":
                raise UserError("Patch %s is installed — nothing to defer" % upd.id)
            upd.write(
                {
                    "state": "deferred",
                    "deferred_until": fields.Date.today() + timedelta(days=int(days or 7)),
                }
            )

    def action_fail(self, note=""):
        for upd in self:
            if upd.state == "installed":
                raise UserError("Patch %s is installed — cannot mark failed" % upd.id)
            upd.write({"state": "failed", "fail_note": note or None})


# ------------------------------------------------------------- SLA credits


class FixMspSlaCredit(models.Model):
    """An SLA credit owed to a client when attainment misses the contract
    target (FluxBilling-style: measurable, table-driven, claim or automatic).
    The credit becomes money through the M20 billing seam
    (msp.sla_credit_applied)."""

    _name = "fix.msp.sla.credit"
    _description = "MSP SLA Credit"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    msp_contract_id = fields.Many2one("fix.msp.contract", required=True, index=True)
    service_report_id = fields.Many2one(
        "fix.msp.service.report", string="Service Report", ondelete="set null"
    )
    period_label = fields.Char(string="Period", required=True)
    attainment_pct = fields.Float(string="Attainment %")
    target_pct = fields.Float(string="Target %")
    breach_count = fields.Integer(string="Breaches", help="Unresolved alerts in the period")
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    credit_amount = fields.Monetary(string="Credit Amount", currency_field="currency_id")
    reason = fields.Char()
    state = fields.Selection(
        [("draft", "Draft"), ("approved", "Approved"), ("applied", "Applied to Billing")],
        default="draft",
        required=True,
        tracking=True,
    )

    _contract_period_unique = models.Constraint(
        "UNIQUE (msp_contract_id, period_label)",
        "A credit already exists for this contract and period",
    )

    def action_approve(self):
        for credit in self:
            if credit.state != "draft":
                raise UserError("Credit %s is not draft" % credit.id)
            credit.state = "approved"

    def action_apply(self):
        """Hand the credit to billing (M20 seam). The event carries
        everything the invoice leg needs; no invoice is fabricated here."""
        for credit in self:
            if credit.state != "approved":
                raise UserError("Credit %s must be approved before applying" % credit.id)
            credit.state = "applied"
            publish(
                self.env,
                "msp.sla_credit_applied",
                "fix.msp.sla.credit",
                credit.id,
                {
                    "contract": credit.msp_contract_id.name,
                    "period": credit.period_label,
                    "amount": credit.credit_amount,
                },
            )


# ------------------------------------------------------------- on-call rota


class FixMspOncallShift(models.Model):
    """The NOC on-call rota: who carries the pager, at which escalation
    level, and when (PagerDuty-style levels; the rotation is data, not
    code)."""

    _name = "fix.msp.oncall.shift"
    _description = "MSP On-Call Shift"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "start_at desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True)
    technician_id = fields.Many2one("hr.employee", string="Technician", required=True)
    level = fields.Selection(
        [("primary", "Primary"), ("secondary", "Secondary"), ("manager", "Manager")],
        default="primary",
        required=True,
    )
    start_at = fields.Datetime(required=True)
    end_at = fields.Datetime(required=True)
    state = fields.Selection(
        [("planned", "Planned"), ("active", "Active"), ("closed", "Closed")],
        default="planned",
        required=True,
        tracking=True,
    )

    @api.constrains("start_at", "end_at")
    def _check_window(self):
        for shift in self:
            if shift.end_at <= shift.start_at:
                raise UserError("On-call shift %s must end after it starts" % shift.name)

    @api.model
    def current_primary(self):
        """The active primary on-call employee right now (None outside cover)."""
        shift = self.search([("state", "=", "active"), ("level", "=", "primary")], limit=1)
        return shift.technician_id or None

    def action_activate(self):
        for shift in self:
            if shift.state != "planned":
                raise UserError("Shift %s is not planned" % shift.name)
            shift.state = "active"
            publish(
                self.env,
                "msp.oncall_shift_active",
                "fix.msp.oncall.shift",
                shift.id,
                {"technician": shift.technician_id.name, "level": shift.level},
            )

    def action_close(self):
        for shift in self:
            if shift.state != "active":
                raise UserError("Shift %s is not active" % shift.name)
            shift.state = "closed"


# ------------------------------------------------------ maintenance windows


class FixMspMaintenanceWindow(models.Model):
    """A scheduled change window: alerting is suppressed for the covered
    contract(s) while the window is open, so planned work does not page
    the on-call (the classic RMM maintenance-window behaviour)."""

    _name = "fix.msp.maintenance.window"
    _description = "MSP Maintenance Window"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "start_at desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True)
    msp_contract_id = fields.Many2one(
        "fix.msp.contract", string="Scoped To Contract", help="Empty = every contract"
    )
    suppress_alerts = fields.Boolean(default=True, string="Suppress Alerting")
    purpose = fields.Char()
    start_at = fields.Datetime(required=True)
    end_at = fields.Datetime(required=True)
    state = fields.Selection(
        [("planned", "Planned"), ("active", "Active"), ("closed", "Closed")],
        default="planned",
        required=True,
        tracking=True,
    )

    @api.constrains("start_at", "end_at")
    def _check_window(self):
        for window in self:
            if window.end_at <= window.start_at:
                raise UserError("Maintenance window %s must end after it starts" % window.name)

    @api.model
    def alerting_suppressed(self, asset):
        """True when ``asset`` sits under an ACTIVE window that suppresses
        alerting (used by ingest_telemetry before raising an alert)."""
        now = fields.Datetime.now()
        windows = self.search([("state", "=", "active"), ("suppress_alerts", "=", True)])
        contract = asset.msp_contract_id
        for window in windows:
            if window.start_at <= now <= window.end_at and (
                not window.msp_contract_id or window.msp_contract_id == contract
            ):
                return True
        return False

    def action_open(self):
        for window in self:
            if window.state != "planned":
                raise UserError("Window %s is not planned" % window.name)
            window.state = "active"
            publish(
                self.env,
                "msp.maintenance_window_open",
                "fix.msp.maintenance.window",
                window.id,
                {"window": window.name},
            )

    def action_close(self):
        for window in self:
            if window.state != "active":
                raise UserError("Window %s is not active" % window.name)
            window.state = "closed"


# ------------------------------------------------------- problem & change


class FixMspChangeRecord(models.Model):
    """ITIL-style problem & change records for the managed estate, with a
    lightweight CAB: draft → approved → implemented → closed (or rejected)."""

    _name = "fix.msp.change.record"
    _description = "MSP Problem & Change Record"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(string="Title", required=True)
    kind = fields.Selection(
        [("change", "Change"), ("problem", "Problem")], default="change", required=True
    )
    msp_contract_id = fields.Many2one("fix.msp.contract", string="Contract", index=True)
    asset_id = fields.Many2one("fix.monitored.asset", string="Asset")
    description = fields.Text()
    risk = fields.Selection(
        [("low", "Low"), ("medium", "Medium"), ("high", "High")], default="medium", required=True
    )
    change_type = fields.Selection(
        [("standard", "Standard"), ("normal", "Normal"), ("emergency", "Emergency")],
        default="normal",
        required=True,
    )
    requested_by = fields.Many2one("hr.employee", string="Requested By")
    implemented_at = fields.Datetime(readonly=True)
    resolution_note = fields.Char(readonly=True, copy=False)

    # --- A02 Enterprise Data Capture (M05 CAB & Rollback Specification) ---
    cab_approver_id = fields.Many2one(
        "res.users",
        string="CAB Approving Authority",
        tracking=True,
    )
    rollback_plan = fields.Text(
        string="Documented Backout & Rollback Plan",
    )
    maintenance_window_id = fields.Many2one(
        "fix.msp.maintenance.window",
        string="Scheduled Maintenance Window",
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("approved", "Approved"),
            ("implemented", "Implemented"),
            ("closed", "Closed"),
            ("rejected", "Rejected"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )

    def action_approve(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError("Record %s is not draft" % rec.id)
            rec.state = "approved"
            publish(
                self.env,
                "msp.change_approved",
                "fix.msp.change.record",
                rec.id,
                {"title": rec.name},
            )

    def action_reject(self, note=""):
        for rec in self:
            if rec.state not in ("draft", "approved"):
                raise UserError("Record %s cannot be rejected from '%s'" % (rec.id, rec.state))
            rec.write({"state": "rejected", "resolution_note": note or None})

    def action_implement(self, note=""):
        for rec in self:
            if rec.state != "approved":
                raise UserError("Record %s must be approved before implementation" % rec.id)
            rec.write(
                {
                    "state": "implemented",
                    "implemented_at": fields.Datetime.now(),
                    "resolution_note": note or rec.resolution_note,
                }
            )
            publish(
                self.env,
                "msp.change_implemented",
                "fix.msp.change.record",
                rec.id,
                {"title": rec.name},
            )

    def action_close(self, note=""):
        for rec in self:
            if rec.state not in ("implemented", "rejected"):
                raise UserError(
                    "Record %s must be implemented (or rejected) before closing" % rec.id
                )
            rec.write({"state": "closed", "resolution_note": note or rec.resolution_note})


# ------------------------------------------- estate & contract polish exts


class FixMonitoredAssetEngines(models.Model):
    """Estate polish: real display names and a live health score."""

    _inherit = "fix.monitored.asset"

    alert_ids = fields.One2many("fix.msp.alert", "asset_id", string="Alerts")
    open_alert_count = fields.Integer(compute="_compute_open_alerts", string="Open Alerts")
    health_score = fields.Integer(
        compute="_compute_health_score",
        store=True,
        string="Health Score",
        help="100 healthy; 50 degraded; 0 offline — minus 5 per open alert, floored at 0",
    )

    @api.depends("alert_ids.state")
    def _compute_open_alerts(self):
        for asset in self:
            asset.open_alert_count = len(asset.alert_ids.filtered(lambda a: a.state != "resolved"))

    @api.depends("health", "alert_ids.state")
    def _compute_health_score(self):
        for asset in self:
            open_alerts = len(asset.alert_ids.filtered(lambda a: a.state != "resolved"))
            base = {"healthy": 100, "degraded": 50, "offline": 0}.get(asset.health, 0)
            asset.health_score = max(0, base - 5 * open_alerts)

    @api.depends("hostname", "agent_id")
    def _compute_display_name(self) -> None:
        for asset in self:
            asset.display_name = asset.hostname or asset.agent_id or "asset %s" % asset.id


class FixMspContractEngines(models.Model):
    """Contract polish: the SLA target the credits engine measures against
    and the computed monthly value."""

    _inherit = "fix.msp.contract"

    sla_target_pct = fields.Float(
        string="SLA Target %", default=90.0, help="Monthly attainment target (percentage)"
    )
    monthly_value = fields.Monetary(
        compute="_compute_monthly_value",
        store=True,
        currency_field="currency_id",
        string="Monthly Value",
        help="Per-device monthly × covered devices",
    )
    credit_ids = fields.One2many("fix.msp.sla.credit", "msp_contract_id", string="SLA Credits")

    @api.depends("per_device_monthly", "device_count", "asset_ids")
    def _compute_monthly_value(self):
        for contract in self:
            devices = contract.device_count or len(contract.asset_ids)
            contract.monthly_value = (contract.per_device_monthly or 0.0) * devices

    def action_compute_sla_credits(self):
        """Draft a credit for every period whose report attainment missed the
        target: shortfall % of the monthly value (capped at the monthly
        value). Idempotent per (contract, period)."""
        Credit = self.env["fix.msp.sla.credit"]
        for contract in self:
            for report in contract.report_ids:
                attainment = round((report.sla_attainment or 0.0) * 100.0, 1)
                if attainment >= contract.sla_target_pct:
                    continue
                if Credit.search_count(
                    [
                        ("msp_contract_id", "=", contract.id),
                        ("period_label", "=", report.period_label),
                    ]
                ):
                    continue
                shortfall = min(contract.sla_target_pct - attainment, 100.0)
                amount = round(contract.monthly_value * shortfall / 100.0, 2)
                Credit.create(
                    {
                        "msp_contract_id": contract.id,
                        "service_report_id": report.id,
                        "period_label": report.period_label,
                        "attainment_pct": attainment,
                        "target_pct": contract.sla_target_pct,
                        "breach_count": report.alert_count - report.resolved_count,
                        "credit_amount": min(amount, contract.monthly_value),
                        "reason": "Attainment %.1f%% below target %.1f%%"
                        % (attainment, contract.sla_target_pct),
                        "state": "draft",
                    }
                )
        return True


class FixMspAlertEngines(models.Model):
    """The on-call escalation flag on alerts."""

    _inherit = "fix.msp.alert"

    escalated = fields.Boolean(
        copy=False, help="Escalated beyond first response (pages the next rota level)"
    )
    escalated_at = fields.Datetime(readonly=True, copy=False)

    def action_escalate(self):
        for alert in self:
            if alert.state == "resolved":
                raise UserError("Alert %s is resolved — nothing to escalate" % alert.id)
            if alert.escalated:
                raise UserError("Alert %s is already escalated" % alert.id)
            alert.write({"escalated": True, "escalated_at": fields.Datetime.now()})
            publish(
                self.env,
                "msp.alert_escalated",
                "fix.msp.alert",
                alert.id,
                {"asset": alert.asset_id.agent_id, "severity": alert.severity},
            )


class FixMspServiceReportEngines(models.Model):
    """Report polish: the percentage column the workspace grid shows."""

    _inherit = "fix.msp.service.report"

    sla_attainment_pct = fields.Float(
        compute="_compute_attainment_pct",
        store=True,
        string="SLA Attainment %",
        help="sla_attainment (0-1) rendered as a percentage",
    )

    @api.depends("sla_attainment")
    def _compute_attainment_pct(self):
        for report in self:
            report.sla_attainment_pct = round((report.sla_attainment or 0.0) * 100.0, 1)
