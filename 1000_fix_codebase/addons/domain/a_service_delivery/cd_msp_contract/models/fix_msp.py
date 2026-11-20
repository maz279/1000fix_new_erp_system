# fix_msp — M05: MSP contracts, alerts, sessions, service reports (P08-M07).
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish

from .msp_periods import dhaka_month, dhaka_previous_month, month_dates


class FixMspContract(models.Model):
    """The MSP service model ON M08's contract engine (never beside it)."""

    _name = "fix.msp.contract"
    _description = "MSP Contract"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True)
    contract_id = fields.Many2one(
        "fix.contract", string="Contract (M08)", required=True, ondelete="cascade"
    )
    device_count = fields.Integer(string="Covered Devices")
    monitoring_scope = fields.Selection(
        [
            ("endpoints", "Endpoints Only"),
            ("endpoints_network", "Endpoints + Network"),
            ("full", "Full Stack"),
        ],
        default="endpoints",
        required=True,
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    per_device_monthly = fields.Monetary(string="Per-Device Monthly", currency_field="currency_id")
    asset_ids = fields.One2many("fix.monitored.asset", "msp_contract_id", string="Monitored Assets")
    report_ids = fields.One2many(
        "fix.msp.service.report", "msp_contract_id", string="Service Reports"
    )

    def action_generate_monthly_report(self, period=None):
        """The contract form's "Generate Report" button: the report of the
        month named (YYYY-MM; default: the previous Dhaka calendar month),
        opened in a form. (The button used to call action_monthly_report,
        which REQUIRES ``period`` - every click raised.)

        A02 ERP pass 2 (M05-S14): the button takes the month, so a month the
        nightly run could not report (alerts still open then) is reported
        once it can be; only a finished month is reported."""
        self.ensure_one()
        # A02 ERP audit M05-F15: the Dhaka calendar month, not naive UTC days
        bounds = self._msp_period_bounds(period) if period else dhaka_previous_month()
        report = self.action_monthly_report(bounds)
        return {
            "type": "ir.actions.act_window",
            "res_model": "fix.msp.service.report",
            "res_id": report.id,
            "view_mode": "form",
        }

    def _msp_period_bounds(self, period):
        """(utc_start, utc_end, label) of a 'YYYY-MM' month, or of the bounds
        given. Refuses a month not yet finished in Dhaka."""
        if isinstance(period, tuple | list):
            return tuple(period)
        first, _last = month_dates(period)
        if not first:
            raise UserError("Name the month as YYYY-MM (e.g. 2026-10).")
        bounds = dhaka_month(first)
        if bounds[1] >= fields.Datetime.now():
            raise UserError(
                "%s is not finished yet: a month is reported once it is over." % bounds[2]
            )
        return bounds

    def _msp_period_figures(self, period, alerts, measure):
        """The A02 ERP pass 2 figures of a month: response and MTTA / MTTR
        (M05-S18), the remote hours and their overage (M05-S17), patch
        compliance and estate health for the client report (M05-S15)."""
        self.ensure_one()
        terms = self._msp_terms_at(period[1])
        minutes = self._msp_remote_minutes(period[0], period[1])
        entitled = terms.remote_hours_monthly or 0.0
        over = round(max(minutes / 60.0 - entitled, 0.0), 2) if entitled else 0.0
        rate = terms.overage_hourly_rate or 0.0
        Patch = self.env["fix.msp.patch.update"].sudo()
        tracked = Patch.search_count([("msp_contract_id", "=", self.id)])
        installed = Patch.search_count(
            [("msp_contract_id", "=", self.id), ("state", "=", "installed")]
        )
        scores = self.asset_ids.mapped("health_score")
        return {
            "response_breached_count": measure.get("response_breached", 0),
            "mtta_minutes": measure.get("mtta_minutes", 0.0),
            "mttr_minutes": measure.get("mttr_minutes", 0.0),
            "remote_minutes": minutes,
            "remote_hours_entitled": entitled,
            "overage_hours": over,
            "overage_rate": rate,
            "overage_amount": round(over * rate, 2),
            "overage_flagged": bool(over and not rate),
            "patch_compliance_pct": round(100.0 * installed / tracked, 1) if tracked else 0.0,
            "health_score_avg": round(sum(scores) / len(scores), 1) if scores else 0.0,
        }

    def action_monthly_report(self, period):
        """Journey 6's ending: the client-facing monthly report."""
        self.ensure_one()
        period = self._msp_period_bounds(period)
        # A02 ERP pass 2 (M05-S07): a month that began after the offboarding
        # completed is not a service month
        if self.offboarded_at and self.offboarded_at < period[0]:
            raise UserError(
                "%s was offboarded on %s: %s is not a service month."
                % (self.name, self.offboarded_at.date(), period[2])
            )
        Report = self.env["fix.msp.service.report"].sudo()
        existing = Report.search(
            [("msp_contract_id", "=", self.id), ("period_label", "=", period[2])], limit=1
        )
        # A02 ERP pass 2 (M05-S01): a report with no attainment figure (and
        # not merely "not yet binding") is recomputed in place; one with its
        # figure stays the month's report
        if existing and not existing._msp_needs_figure():
            raise UserError(
                "The %s service report of %s already exists - open it on Client Service "
                "Reviews (Regenerate Summary rewrites its text)." % (period[2], self.name)
            )
        alerts = (
            self.env["fix.msp.alert"]
            .sudo()
            .search(
                [
                    ("msp_contract_id", "=", self.id),
                    ("create_date", ">=", period[0]),
                    ("create_date", "<=", period[1]),
                ]
            )
        )
        # A02 audit M05-P2: "within SLA" was resolved / total, with no time
        # measure. It is now measured from each alert's resolution time against
        # the contract's resolution target for its severity (_msp_period_sla).
        measure = self._msp_period_sla(alerts)
        # A02 ERP audit M05-F8: an alert still inside its target when the
        # report was made was frozen as "pending" and never judged. The
        # report waits until every alert of the period is resolved or past
        # its deadline (the nightly run retries each day).
        if measure["pending"]:
            raise UserError(
                "The %s report of %s cannot be made yet: %d alert(s) of the period are still "
                "open inside their resolution target. Generate it once they are resolved or "
                "their deadlines pass, so every alert is judged."
                % (period[2], self.name, measure["pending"])
            )
        resolved = alerts.filtered(lambda a: a.state == "resolved")
        within = measure["within"]
        sla_pct = measure["attainment"]
        device_cnt = self.device_count or len(self.asset_ids)
        # A02 ERP pass 2 (M05-S08): a month wholly before the SLA binds is
        # "not yet binding": no attainment (never a free 100 %), no credit
        binds = self._msp_sla_binds_at()
        not_binding = bool(binds and binds > period[1])
        figures = self._msp_period_figures(period, alerts, measure)
        if not_binding:
            text_en = (
                "Monthly Managed Services Operations Report for %s: %d alerts processed. The "
                "SLA is not yet binding (onboarding; it binds from %s UTC), so no attainment "
                "is measured for this month." % (period[2], len(alerts), binds)
            )
            text_bn = (
                "%s মাসের পরিচালিত সেবাসমূহ (MSP) কার্যক্রম প্রতিবেদন: মোট %dটি সতর্কতা প্রক্রিয়া "
                "করা হয়েছে। অনবোর্ডিং চলছে, এসএলএ এখনও বাধ্যতামূলক হয়নি (%s UTC থেকে হবে), তাই "
                "এই মাসের এসএলএ অর্জন পরিমাপ করা হয়নি।" % (period[2], len(alerts), binds)
            )
        else:
            text_en = (
                f"Monthly Managed Services Operations Report for {period[2]}: "
                f"{len(alerts)} alerts processed, {within} incidents resolved within SLA. "
                f"SLA attainment achieved: {sla_pct * 100:.1f}% across {device_cnt} covered "
                f"endpoints."
            )
            text_bn = (
                f"{period[2]} মাসের পরিচালিত সেবাসমূহ (MSP) কার্যক্রম প্রতিবেদন: "
                f"মোট {len(alerts)}টি সতর্কতা প্রক্রিয়া করা হয়েছে, {within}টি ঘটনা নির্ধারিত এসএলএ সীমার মধ্যে সমাধান করা হয়েছে। "
                f"এসএলএ অর্জনের হার {sla_pct * 100:.1f}%, আওতাভুক্ত সচল ডিভাইস সংখ্যা {device_cnt}টি।"
            )
        vals = dict(
            figures,
            msp_contract_id=self.id,
            period_label=period[2],
            alert_count=len(alerts),
            resolved_count=within,
            resolved_total_count=len(resolved),
            breached_count=measure["breached"],
            pending_count=measure["pending"],
            sla_not_binding=not_binding,
            sla_binds_at=binds or False,
            summary_en=text_en,
            summary_bn=text_bn,
            attainment_flagged=False,
        )
        if not not_binding:
            vals["sla_attainment"] = sla_pct
        # The figures are guarded on the report (A02 audit M05-2): they drive
        # the SLA credit, so only this computation may write them. The report
        # is the system's (A02 ERP pass 2, M05-S01): nobody creates one by hand.
        if existing:
            existing._guarded().write(vals)
            report = existing
        else:
            report = Report._guarded().create(
                dict(
                    vals,
                    company_id=self.company_id.id,
                    operating_unit_id=self.operating_unit_id.id or False,
                )
            )
        publish(
            self.env,
            "msp.service_report_published",
            "fix.msp.service.report",
            report.id,
            {"contract": self.name, "period": period[2]},
        )
        if report.overage_amount > 0.005 and not report.overage_published_at:
            # M05-S17 (D11): the hours above the entitlement are billed
            report._guarded().write({"overage_published_at": fields.Datetime.now()})
            publish(
                self.env,
                "msp.remote_hours_overage",
                "fix.msp.service.report",
                report.id,
                {
                    "msp_contract_id": self.id,
                    "period": period[2],
                    "hours": report.overage_hours,
                    "rate": report.overage_rate,
                    "amount": report.overage_amount,
                },
            )
        elif report.overage_flagged:
            self.message_post(
                body="%s: %.2f remote-support hours above the entitlement were NOT billed - "
                "the contract has no overage rate (flagged)." % (period[2], report.overage_hours)
            )
        return report.with_env(self.env)


class FixMonitoredAsset(models.Model):
    """A client endpoint under management (fed by rmm-collector)."""

    _name = "fix.monitored.asset"
    _description = "Monitored Asset"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    msp_contract_id = fields.Many2one(
        "fix.msp.contract", required=True, ondelete="cascade", index=True
    )
    agent_id = fields.Char(required=True, help="RMM agent identifier")
    hostname = fields.Char()
    device_id = fields.Many2one(
        "fix.device",
        string="Registered Device",
        ondelete="restrict",
        help="The M17 registry device this endpoint is: an alert ticket is a service order "
        "on this device, at the branch the device is registered at",
    )
    last_seen = fields.Datetime(readonly=True)
    health = fields.Selection(
        [("healthy", "Healthy"), ("degraded", "Degraded"), ("offline", "Offline")],
        default="healthy",
        required=True,
    )

    # --- A02 Enterprise Data Capture (M05 Monitored Asset Telemetry Specification) ---
    ip_address = fields.Char(string="IPv4 / IPv6 Endpoint Address")
    mac_address = fields.Char(string="Hardware MAC Address")
    os_version = fields.Char(string="Operating System & Build Version")
    cpu_utilization_pct = fields.Float(string="CPU Load (%)", default=0.0)
    ram_utilization_pct = fields.Float(string="Memory Utilization (%)", default=0.0)
    disk_free_gb = fields.Float(string="Free Storage Capacity (GB)", default=0.0)
    uptime_hours = fields.Float(string="Continuous Uptime (Hours)", default=0.0)
    patch_baseline_compliant = fields.Boolean(
        string="OS & Security Patch Baseline Compliant",
        default=True,
    )

    @api.model
    def ingest_telemetry(self, agent_id, health, seen_at):
        """The collector's ingestion path (INT-029): last_seen and health
        update; the FIRST unhealthy transition raises an ALERT — unless an
        ACTIVE maintenance window suppresses alerting for the asset's
        contract (planned work must not page the on-call)."""
        asset = self.search([("agent_id", "=", agent_id)], limit=1)
        if not asset:
            raise UserError("Unknown RMM agent %s" % agent_id)
        became_unhealthy = health != "healthy" and asset.health == "healthy"
        asset.write({"health": health, "last_seen": seen_at})
        if became_unhealthy:
            if self.env["fix.msp.maintenance.window"].alerting_suppressed(asset):
                publish(
                    self.env,
                    "msp.alert_suppressed_window",
                    "fix.monitored.asset",
                    asset.id,
                    {"agent": agent_id, "health": health},
                )
                return
            alert = self.env["fix.msp.alert"].create(
                {
                    "msp_contract_id": asset.msp_contract_id.id,
                    "asset_id": asset.id,
                    "severity": "major" if health == "offline" else "minor",
                    "message": "%s became %s" % (asset.hostname or agent_id, health),
                }
            )
            publish(
                self.env,
                "msp.alert_raised",
                "fix.msp.alert",
                alert.id,
                {"agent": agent_id, "health": health},
            )


class FixMspAlert(models.Model):
    """An alert from the RMM collector; ticketing is a service order."""

    _name = "fix.msp.alert"
    _description = "MSP Alert"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "create_date desc"

    def _fix_guarded_fields(self) -> set:
        # A02 audit M05-3: /p03/model/write set state='resolved' on an untouched
        # alert, which lifts SLA attainment and so removes the credit owed.
        return super()._fix_guarded_fields() | {"state", "order_id"}

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    msp_contract_id = fields.Many2one("fix.msp.contract", required=True, index=True)
    asset_id = fields.Many2one("fix.monitored.asset", required=True)
    severity = fields.Selection(
        [("minor", "Minor"), ("major", "Major")], default="minor", required=True
    )
    message = fields.Char(required=True)
    state = fields.Selection(
        [
            ("new", "New"),
            ("acked", "Acknowledged"),
            ("ticketed", "Ticketed"),
            ("resolved", "Resolved"),
        ],
        default="new",
        required=True,
        tracking=True,
    )
    order_id = fields.Many2one("fix.service.order", string="Service Order", ondelete="set null")

    def action_acknowledge(self):
        for rec in self:
            if rec.state != "new":
                raise UserError("Only NEW alerts acknowledge")
            rec._guarded().write({"state": "acked"})

    def action_to_ticket(self):
        """Journey 6: alert -> ticket. The ticket IS a service order with
        the MSP contract's customer on the alerting asset's registered device
        (at the branch the device is registered at); SLA flows from M08's terms.

        A service order requires a device, a customer and a branch: the
        previous body passed none of the first and ``branch_id: False``, so no
        alert could ever be ticketed (R01 re-audit 2026-10-22)."""
        for rec in self:
            if rec.state not in ("new", "acked"):
                raise UserError("Alert already ticketed or resolved")
            # A02 audit M05-P2 (probe A2): an alert was ticketed on a draft
            # contract. The ticket is entitlement work, so the M08 term must be
            # in force, and the order carries the contract it is delivered under.
            rec.msp_contract_id._msp_assert_entitled("Ticketing an MSP alert")
            device = rec.asset_id.device_id
            if not device or not device.branch_id:
                raise UserError(
                    "Asset %s is not linked to a registered device with a branch - "
                    "link it before ticketing the alert"
                    % (rec.asset_id.hostname or rec.asset_id.agent_id)
                )
            order = self.env["fix.service.order"].create(
                {
                    "device_id": device.id,
                    "customer_id": rec.msp_contract_id.contract_id.customer_id.id,
                    "branch_id": device.branch_id.id,
                    "fault_description": "MSP alert: %s" % rec.message,
                    # A02 ERP pass 2 (M05-S09): the order's true channel; the
                    # fee covers labour and remote work only (owner decision
                    # D10), so parts and out-of-scope work are priced on an
                    # estimate the client approves (cd_contract_core
                    # _fix_msp_covers) unless the contract includes parts
                    "service_type": "msp_alert",
                    "order_category": "amc",
                    "contract_id": rec.msp_contract_id.contract_id.id,
                }
            )
            rec._guarded().write({"state": "ticketed", "order_id": order.id})
            publish(self.env, "msp.alert_ticketed", "fix.msp.alert", rec.id, {"order": order.name})


class FixRemoteSession(models.Model):
    """A remote support session (INT-028 MeshCentral/RustDesk) with PDPA
    consent capture — the session is lawful, or it does not start."""

    _name = "fix.remote.session"
    _description = "Remote Session"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "started_at desc"

    def _fix_guarded_fields(self) -> set:
        # A02 audit M05-4: consent was a tickbox anyone ticked, and started /
        # ended_at could be forged by an ORM write. Consent, timing and the
        # recording are evidence; only the consent capture and the start / end
        # actions write them.
        return super()._fix_guarded_fields() | {
            "consent_captured",
            "consent_token_ref",
            "started_at",
            "ended_at",
            "recording_url",
        }

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    msp_contract_id = fields.Many2one("fix.msp.contract", required=True)
    asset_id = fields.Many2one("fix.monitored.asset", required=True)
    technician_id = fields.Many2one("hr.employee", string="Technician", required=True)
    tool = fields.Selection(
        [("meshcentral", "MeshCentral"), ("rustdesk", "RustDesk")],
        default="meshcentral",
        required=True,
    )
    consent_captured = fields.Boolean(
        required=True,
        default=False,
        readonly=True,
        copy=False,
        help="PDPA: the client user's consent to the remote session - "
        "without it the session does not start. Set only by verifying the "
        "client's consent code (action_verify_consent), never ticked by hand.",
    )
    started_at = fields.Datetime(default=fields.Datetime.now, required=True)
    ended_at = fields.Datetime(readonly=True)

    # --- A02 Enterprise Data Capture (M05 Remote Session PDPA Audit Specification) ---
    session_protocol = fields.Selection(
        [
            ("meshcentral_webrtc", "MeshCentral WebRTC TLS 1.3"),
            ("rustdesk_encrypted", "RustDesk End-to-End Encrypted"),
            ("ssh_bastion", "Zero-Trust SSH Bastion Tunnel"),
        ],
        string="Transport Encryption Protocol",
        default="meshcentral_webrtc",
    )
    consent_token_ref = fields.Char(
        string="PDPA Client Consent Token / OTP Ref",
        readonly=True,
        copy=False,
        help="The reference of the verified client consent (the M33 OTP "
        "verification log row). Stamped by action_verify_consent.",
    )
    recording_url = fields.Char(
        string="Immutable Session Audit Recording URI",
        readonly=True,
        copy=False,
        help="Given when the session is ended (action_end); required unless the "
        "recording switch is off.",
    )
    session_summary = fields.Text(
        string="Remote Remediation Actions Summary",
    )
    order_id = fields.Many2one(
        "fix.service.order",
        string="Linked Service Order",
        ondelete="set null",
    )

    @api.constrains("asset_id", "msp_contract_id")
    def _check_asset_on_contract(self):
        # A02 audit M05-4 (probe R5): a session started on an asset of another
        # contract, so one client's consent opened another client's endpoint.
        for rec in self:
            if rec.asset_id and rec.asset_id.msp_contract_id != rec.msp_contract_id:
                raise ValidationError(
                    "Asset %s is not covered by MSP contract %s - a remote session "
                    "may only open an endpoint of its own contract."
                    % (rec.asset_id.hostname or rec.asset_id.agent_id, rec.msp_contract_id.name)
                )

    def action_start(self):
        for rec in self:
            # PDPA: the tickbox alone is not consent (A02 audit M05-4). The
            # client's consent code must have been verified, which stamps the
            # token reference.
            if not (rec.consent_captured and rec.consent_token_ref):
                raise UserError(
                    "PDPA: remote sessions require captured consent - this one did not "
                    "start. Send the client the consent code (Request Consent) and "
                    "verify the code they read back (Verify Consent)."
                )
            if rec.asset_id.msp_contract_id != rec.msp_contract_id:
                raise UserError(
                    "Asset %s is not covered by this session's contract - the session "
                    "did not start." % (rec.asset_id.hostname or rec.asset_id.agent_id)
                )
            publish(
                self.env,
                "msp.remote_session_started",
                "fix.remote.session",
                rec.id,
                {"asset": rec.asset_id.hostname or rec.asset_id.agent_id},
            )

    def action_end(self):
        for rec in self:
            rec._guarded().write({"ended_at": fields.Datetime.now()})
            publish(self.env, "msp.remote_session_ended", "fix.remote.session", rec.id, {})


class FixMspServiceReport(models.Model):
    """The monthly client-facing service report (bilingual fields, DE-17)."""

    _name = "fix.msp.service.report"
    _description = "MSP Service Report"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]

    def _fix_guarded_fields(self) -> set:
        # A02 audit M05-2: the report's figures decide the SLA credit owed, so
        # a typed attainment would be a typed credit. action_monthly_report
        # computes them; the credit run flags a report with no figure.
        return super()._fix_guarded_fields() | {
            "alert_count",
            "resolved_count",
            "sla_attainment",
            "attainment_flagged",
        }

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    msp_contract_id = fields.Many2one("fix.msp.contract", required=True, ondelete="cascade")
    period_label = fields.Char(string="Period", required=True)
    alert_count = fields.Integer()
    resolved_count = fields.Integer()
    sla_attainment = fields.Float(string="SLA Attainment (0-1)")

    _FIGURES = ("alert_count", "resolved_count", "sla_attainment")

    def write(self, vals):
        # The guard lets an unchanged value through, and an EMPTY attainment
        # reads as 0.0: writing 0.0 onto a report with no figure would turn
        # "no credit, flagged" into a full credit (A02 audit M05-11). No form
        # edits these figures, so outside a transition any write of them is
        # refused.
        if self.filtered("id") and not self._fix_guard_open():
            touched = [k for k in self._FIGURES if k in vals]
            if touched:
                self._fix_guard_refuse(touched)
        return super().write(vals)

    attainment_flagged = fields.Boolean(
        string="Attainment Missing (Flagged)",
        readonly=True,
        copy=False,
        help="Set by the SLA credit run when the report carries no attainment "
        "figure: such a report produces no credit until it is regenerated "
        "(A02 audit M05-11).",
    )
    summary_bn = fields.Text(string="সারসংক্ষেপ (Bengali)", help="DE-17")
    summary_en = fields.Text(string="Summary (English)")

    def action_generate_bilingual_report(self):
        for rec in self:
            sla_pct = rec.sla_attainment or 0.0
            device_cnt = rec.msp_contract_id.device_count or len(rec.msp_contract_id.asset_ids)
            rec.summary_en = (
                f"Monthly Managed Services Operations Report for {rec.period_label}: "
                f"{rec.alert_count} alerts processed, {rec.resolved_count} incidents resolved within SLA. "
                f"SLA attainment achieved: {sla_pct * 100:.1f}% across {device_cnt} covered endpoints."
            )
            rec.summary_bn = (
                f"{rec.period_label} মাসের পরিচালিত সেবাসমূহ (MSP) কার্যক্রম প্রতিবেদন: "
                f"মোট {rec.alert_count}টি সতর্কতা প্রক্রিয়া করা হয়েছে, {rec.resolved_count}টি ঘটনা নির্ধারিত এসএলএ সীমার মধ্যে সমাধান করা হয়েছে। "
                f"এসএলএ অর্জনের হার {sla_pct * 100:.1f}%, আওতাভুক্ত সচল ডিভাইস সংখ্যা {device_cnt}টি।"
            )
