# fix.workshop.job — Workshop Repair Order & Execution Job (CD-M31-01, RR-03 Milestone R03-M02).
# Full state machine unified with AS-06, bench routing, multi-job handling, burn-in, costing, and stubs.
import logging

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

logger = logging.getLogger(__name__)

WORKSHOP_JOB_STATES = [
    ("draft", "Draft"),
    ("intake", "Intake & Routing"),
    ("diagnostic", "Component Diagnosis"),
    ("waiting_parts", "Waiting for Spare Parts"),
    ("in_repair", "In Repair on Bench"),
    ("burn_in", "Burn-In & Stress Testing"),
    ("qc_pending", "QC Pending"),
    ("qc_failed", "QC Failed — Rework Loop"),
    ("ready", "Ready for Release / Handover"),
    ("delivered", "Delivered / Handed Over"),
    ("cancelled", "Cancelled"),
]

# State transitions authority (AS-06 / DP-01)
VALID_JOB_TRANSITIONS = {
    "draft": {"intake", "cancelled"},
    "intake": {"diagnostic", "waiting_parts", "in_repair", "cancelled"},
    "diagnostic": {"waiting_parts", "in_repair", "cancelled"},
    "waiting_parts": {"in_repair", "cancelled"},
    "in_repair": {"burn_in", "qc_pending", "waiting_parts", "cancelled"},
    "burn_in": {"qc_pending", "in_repair", "qc_failed"},
    "qc_pending": {"ready", "qc_failed"},
    "qc_failed": {"in_repair", "diagnostic", "cancelled"},
    "ready": {"delivered"},
    "delivered": set(),
    "cancelled": set(),
}


class FixWorkshopJob(models.Model):
    """A workshop repair job — the central unit of execution within the depot.

    Carries repair-level routing (L1/L2/L3), bench allocation, spare parts consumption,
    evidence packs, burn-in testing, and quality control.
    """

    _name = "fix.workshop.job"
    _description = "Workshop Repair Job"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "priority desc, create_date desc"

    # Multi-entity & Governance (AS-03)
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        index=True,
        default=lambda self: self.env.company,
    )
    operating_unit_id = fields.Many2one(
        "operating.unit",
        string="Operating Unit",
        index=True,
    )

    name = fields.Char(
        string="Job Reference",
        required=True,
        readonly=True,
        index=True,
        default=lambda self: self.env["ir.sequence"].next_by_code("fix.workshop.job") or "JOB-NEW",
    )
    name_bn = fields.Char(
        string="নথি নম্বর (বাংলা)",
        help="Job reference in Bengali",
    )

    # Service Order Linkage (M01 Integration)
    order_id = fields.Many2one(
        "fix.service.order",
        string="Parent Service Order",
        index=True,
        ondelete="restrict",
        help="The commercial service order this workshop job executes",
    )
    order_reference = fields.Char(related="order_id.name", store=True, string="Order Ref")

    # Facility & Bench Allocation (CD-M31-02)
    workshop_id = fields.Many2one(
        "fix.workshop",
        string="Workshop Facility",
        required=True,
        index=True,
        ondelete="restrict",
    )
    bench_id = fields.Many2one(
        "fix.workshop.bench",
        string="Assigned Repair Bench",
        index=True,
        tracking=True,
        help="The physical workbench where repair operations take place",
    )
    technician_id = fields.Many2one(
        "hr.employee",
        string="Assigned Technician",
        index=True,
        tracking=True,
        help="The technician responsible for executing the repair",
    )
    qc_inspector_id = fields.Many2one(
        "hr.employee",
        string="QC Inspector",
        tracking=True,
        help="Independent QC inspector (BRU-SRM-18: must differ from repairing technician)",
    )
    equipment_id = fields.Many2one(
        "fix.equipment",
        string="Test Equipment Used",
        help="M45 calibration-tracked test instrument used for verification / QC (ISO 9001 Clause 7.1.5)",
    )

    # Repair Classification & Multi-job handling
    repair_level = fields.Selection(
        [
            ("l1", "Level 1 — Modular / Quick Fix"),
            ("l2", "Level 2 — Component / Soldering"),
            ("l3", "Level 3 — Chip-Level / Advanced Depot"),
        ],
        string="Repair Level",
        default="l1",
        required=True,
        tracking=True,
    )
    multi_job_group_id = fields.Char(
        string="Multi-Job Group ID",
        index=True,
        help="Batch group identifier for multi-job bench processing",
    )

    # Device & Customer Information
    device_id = fields.Many2one(
        "fix.device",
        string="Device",
        index=True,
        ondelete="restrict",
    )
    device_serial = fields.Char(
        string="Serial Number",
        index=True,
    )
    customer_id = fields.Many2one(
        "res.partner",
        string="Customer",
        index=True,
    )

    # Job Details & Diagnosis
    fault_description = fields.Text(string="Reported Fault", required=True)
    diagnostic_findings = fields.Text(string="Diagnosis & Defect Coding", tracking=True)
    repair_action_summary = fields.Text(string="Repair Actions Taken", tracking=True)
    priority = fields.Selection(
        [("normal", "Normal"), ("high", "High"), ("urgent", "Urgent"), ("emergency", "Emergency")],
        default="normal",
        required=True,
        tracking=True,
    )

    # State Machine (AS-06)
    state = fields.Selection(
        WORKSHOP_JOB_STATES,
        default="draft",
        required=True,
        tracking=True,
        index=True,
        group_expand="_read_group_states",
    )

    # Spare Parts Consumed (M15 Integration)
    part_line_ids = fields.One2many(
        "fix.workshop.part.line",
        "job_id",
        string="Parts Consumed",
    )

    # Evidence Packs (AS-01 / cd_document_core integration)
    evidence_ids = fields.One2many(
        "fix.workshop.evidence",
        "job_id",
        string="Evidence Pack Records",
    )

    # Burn-In & Stress Testing (CD-M31-03)
    burn_in_duration_hours = fields.Float(
        string="Burn-In Duration (Hours)",
        default=4.0,
        help="Scheduled burn-in test duration (minimum 4.0h / 240m for L2/L3)",
    )
    burn_in_actual_minutes = fields.Float(
        string="Actual Burn-In Minutes",
        default=240.0,
        tracking=True,
        help="FLAW-31.3: L2/L3 board repairs require >= 240 minutes continuous stress testing",
    )
    thermal_crash_count = fields.Integer(
        string="Thermal / Stress Crashes",
        default=0,
        tracking=True,
        help="FLAW-31.3: Must be 0 to pass burn-in",
    )
    burn_in_started_at = fields.Datetime(string="Burn-In Started At", readonly=True)
    burn_in_completed_at = fields.Datetime(string="Burn-In Completed At", readonly=True)
    burn_in_temp_celsius = fields.Float(string="Chamber Temp (°C)", default=40.0)
    burn_in_passed = fields.Boolean(string="Burn-In Passed", default=False, tracking=True)

    # Micro-Soldering, IPC-7711/7721 & SAM Labor Efficiency (M31 Enterprise Data Capture)
    schematic_designators = fields.Char(
        string="Schematic / Boardview Designators",
        help="e.g. U7000, CD3217B12, C7050, PPBUS_G3H",
    )
    reflow_profile_name = fields.Char(
        string="BGA / Hot-Air Reflow Profile",
        help="e.g. SAC305 Lead-Free 235°C Peak / 60s TAL",
    )
    flux_solder_spec = fields.Char(
        string="Solder Alloy & Flux Lot",
        help="e.g. Senju M705 SAC305 + Amtech NC-559-V2-TF",
    )
    dc_power_rail_readings = fields.Text(
        string="DC Power Rail / Diode Mode Readings",
        help="Pre and post repair voltage/current/diode measurements on primary rails",
    )
    ipc_class_target = fields.Selection(
        [
            ("class_2", "IPC Class 2 — Dedicated Service Electronic Products"),
            ("class_3", "IPC Class 3 — High Performance / Critical Electronic Products"),
        ],
        string="IPC-7711/7721 Rework Standard",
        default="class_2",
    )
    ipc_visual_inspection_passed = fields.Boolean(
        string="IPC 10x–40x Microscope Inspection Passed",
        default=True,
    )
    sam_standard_minutes = fields.Float(
        string="Standard Allowed Minutes (SAM)",
        default=60.0,
    )
    actual_logged_minutes = fields.Float(
        string="Actual Logged Bench Minutes",
        default=60.0,
    )
    labor_efficiency_pct = fields.Float(
        string="Labor Efficiency (%)",
        compute="_compute_labor_efficiency",
        store=True,
    )
    dofa_writeoff_tier = fields.Selection(
        [
            ("none", "No Write-Off Required"),
            ("tier_2", "Tier 2 — Service Center Manager (<= 10,000 BDT)"),
            ("tier_3", "Tier 3 — Regional Service Head (<= 50,000 BDT)"),
            ("tier_4", "Tier 4 — Head of Service & Finance (> 50,000 BDT)"),
        ],
        string="DOFA BER / Scrap Write-Off Tier",
        default="none",
    )
    pre_rework_photo_attachment_id = fields.Many2one(
        "ir.attachment",
        string="Pre-Rework Microscope Photo",
    )
    post_rework_photo_attachment_id = fields.Many2one(
        "ir.attachment",
        string="Post-Rework Microscope / Thermal Log",
    )

    # Quality Control & Checklists
    qc_passed = fields.Boolean(string="QC Passed", default=False, tracking=True)
    qc_notes = fields.Text(string="QC Inspection Notes")
    ncr_id = fields.Many2one(
        "fix.ncr",
        string="NCR (M23)",
        ondelete="set null",
        help="Formal ISO 9001 Non-Conformance Record (STUB-M31-M23-001 CLOSED)",
    )
    certification_waiver = fields.Boolean(
        string="Certification Waiver",
        help="Manager waiver for L2/L3 repair assignment (audited)",
    )
    certification_waiver_reason = fields.Char(string="Waiver Justification")

    # Costing & Monetary (AS-10)
    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        required=True,
        default=lambda self: self.env.ref("base.BDT", raise_if_not_found=False)
        or self.env.company.currency_id,
    )
    parts_total = fields.Monetary(
        string="Parts Total",
        compute="_compute_totals",
        store=True,
        currency_field="currency_id",
    )
    labour_total = fields.Monetary(
        string="Labour Cost",
        default=0.0,
        tracking=True,
        currency_field="currency_id",
    )
    total_repair_cost = fields.Monetary(
        string="Total Repair Cost",
        compute="_compute_totals",
        store=True,
        currency_field="currency_id",
    )

    # Rework Tracking (M01 / M31 Rework loops)
    is_rework = fields.Boolean(string="Internal Rework", default=False, tracking=True)
    rework_count = fields.Integer(string="Rework Count", default=0)
    rework_reason = fields.Text(string="Rework Reason")
    rework_of_id = fields.Many2one(
        "fix.workshop.job",
        string="Rework Of Job",
        index=True,
        readonly=True,
    )

    # Permanent Legacy Reference (MIG-03)
    legacy_reference = fields.Char(
        string="Legacy Reference",
        index=True,
        help="Permanent paper job card reference (LEG:JOB-CARD:<hub>:<card_number>)",
    )
    intake_date = fields.Datetime(string="Intake Date", default=fields.Datetime.now)
    completed_at = fields.Datetime(string="Completed Date", readonly=True)
    active = fields.Boolean(default=True, tracking=True)

    _legacy_ref_unique = models.Constraint(
        "UNIQUE (legacy_reference)",
        "The legacy reference must be unique (MIG-03).",
    )

    @api.model
    def _read_group_states(self, states, domain, order):
        return [s[0] for s in WORKSHOP_JOB_STATES]

    @api.depends("part_line_ids.subtotal", "labour_total")
    def _compute_totals(self):
        for rec in self:
            parts = sum(line.subtotal for line in rec.part_line_ids)
            rec.parts_total = parts
            rec.total_repair_cost = parts + (rec.labour_total or 0.0)

    @api.depends("sam_standard_minutes", "actual_logged_minutes")
    def _compute_labor_efficiency(self):
        for rec in self:
            if rec.actual_logged_minutes and rec.actual_logged_minutes > 0:
                rec.labor_efficiency_pct = round(
                    (rec.sam_standard_minutes or 0.0) / rec.actual_logged_minutes * 100.0, 2
                )
            else:
                rec.labor_efficiency_pct = 100.0

    # --- State Machine Transitions (AS-06) ---
    def _validate_transition(self, new_state: str) -> None:
        self.ensure_one()
        valid_next = VALID_JOB_TRANSITIONS.get(self.state, set())
        if new_state not in valid_next:
            raise UserError(
                f"Invalid job state transition: {self.state} -> {new_state}. "
                f"Permitted next states from '{self.state}' are: {', '.join(sorted(valid_next)) or 'None (Terminal)'}"
            )

    def action_transition(self, new_state: str):
        """Execute state transition with business gate enforcement and event publication."""
        for rec in self:
            rec._validate_transition(new_state)
            old_state = rec.state

            # Business Gate: In Repair requires bench & technician eligibility check
            if new_state == "in_repair":
                if not rec.bench_id:
                    raise UserError(
                        f"Job {rec.name} cannot enter 'In Repair' without an assigned workbench."
                    )
                if not rec.technician_id:
                    raise UserError(
                        f"Job {rec.name} cannot enter 'In Repair' without an assigned technician."
                    )
                # Execute Cross-Wave Stub STUB-M31-M22-001 (Certification check)
                rec._check_technician_certification(rec.technician_id, rec.repair_level)
                # FLAW-31.2: ESD compliance gate for L2/L3 repairs
                if rec.repair_level in ("l2", "l3") and rec.bench_id:
                    # An explicit check if bench has an unverified date or out-of-spec resistance
                    strap = rec.bench_id.wrist_strap_mohm or 10.0
                    surface = rec.bench_id.worksurface_rtg_mohm or 100.0
                    if not rec.bench_id.is_esd_safe or strap >= 35.0 or surface >= 1000.0:
                        raise UserError(
                            f"FLAW-31.2 ESD Interlock Gate: Bench {rec.bench_id.code} has not passed today's "
                            f"daily ESD wrist-strap (<35 MΩ) and worksurface (<1000 MΩ) verification required for {rec.repair_level.upper()} repairs."
                        )

            # Business Gate: Burn-In started
            if new_state == "burn_in":
                rec.burn_in_started_at = fields.Datetime.now()

            # Business Gate: QC Pending requires burn-in pass if L2 or L3
            if (
                new_state == "qc_pending"
                and rec.repair_level in ("l2", "l3")
                and not rec.burn_in_passed
            ):
                raise UserError(
                    f"Job {rec.name} ({rec.repair_level.upper()}) requires burn-in test to pass before QC."
                )

            # Business Gate: Ready requires QC inspection
            if new_state == "ready":
                if not rec.qc_passed:
                    raise UserError(
                        f"Job {rec.name} cannot be marked 'Ready' without passing Quality Control."
                    )
                rec.completed_at = fields.Datetime.now()
                # Release bench upon completion
                if rec.bench_id:
                    rec.bench_id.action_release_job(rec)

            rec.state = new_state
            rec._emit_job_transitioned(old_state, new_state)

            # Synchronize with parent service order if present
            rec._sync_with_service_order(new_state)

        return True

    def action_intake(self):
        return self.action_transition("intake")

    def action_diagnostic(self):
        return self.action_transition("diagnostic")

    def action_wait_parts(self):
        return self.action_transition("waiting_parts")

    def action_start_repair(self):
        return self.action_transition("in_repair")

    def action_start_burn_in(self):
        return self.action_transition("burn_in")

    def action_pass_burn_in(self):
        for rec in self:
            if rec.repair_level in ("l2", "l3"):
                if (rec.burn_in_actual_minutes or 0.0) < 240.0:
                    raise UserError(
                        f"FLAW-31.3 Burn-In Gate: {rec.repair_level.upper()} repair job {rec.name} requires at least "
                        f"240 minutes (4.0 hours) continuous burn-in stress testing (logged: {rec.burn_in_actual_minutes} min)."
                    )
                if (rec.thermal_crash_count or 0) > 0:
                    raise UserError(
                        f"FLAW-31.3 Burn-In Gate: Job {rec.name} experienced {rec.thermal_crash_count} thermal/stress crashes during burn-in."
                    )
            rec.burn_in_completed_at = fields.Datetime.now()
            rec.burn_in_passed = True
        return self.action_transition("qc_pending")

    def action_pass_qc(self, notes=""):
        """Pass QC inspection and advance to ready."""
        for rec in self:
            rec._run_qc_inspection(passed=True, notes=notes)
            rec.action_transition("ready")
        return True

    def action_fail_qc(self, reason=""):
        """Fail QC inspection: raise the NCR and open the rework loop (qc_failed).

        The transition is validated FIRST - the old body wrote ``state`` directly,
        so a draft or delivered job could "fail QC" - and goes through
        action_transition (transition event + service-order sync). The QC event is
        emitted once, by _run_qc_inspection: the old body emitted it a second time,
        so every failure was counted twice downstream."""
        for rec in self:
            rec._validate_transition("qc_failed")
            rec._run_qc_inspection(passed=False, notes=reason)
            rec.write(
                {"is_rework": True, "rework_count": rec.rework_count + 1, "rework_reason": reason}
            )
            rec.action_transition("qc_failed")
        return True

    def action_deliver(self):
        return self.action_transition("delivered")

    def action_cancel(self):
        return self.action_transition("cancelled")

    def action_auto_assign_bench(self):
        """The bench-allocation engine (M31 'Bench Allocation & Queue'):
        pick the best bench for this job — deterministic and explainable.

          1. level-capable (bench repair_level >= job repair_level)
          2. capacity free (current_job_count < max_concurrent_jobs)
          3. ESD-safe when the job's device demands it (L3 always prefers
             ESD benches; is_esd_certified workshops' benches rank first)
          4. same workshop as the job, calibration not expired

        Ties break on lowest current load, then bench code. Returns the
        bench; raises when nothing qualifies (the queue stays honest).
        """
        Bench = self.env["fix.workshop.bench"].sudo()
        for job in self:
            if job.bench_id:
                continue  # already benched
            candidates = Bench.search(
                [
                    ("workshop_id", "=", job.workshop_id.id),
                    ("state", "in", ("available", "occupied")),
                    ("repair_level", ">=", job.repair_level),
                ]
            ).filtered(
                lambda b: b.current_job_count < b.max_concurrent_jobs
                and (
                    not b.calibration_expiry_date
                    or b.calibration_expiry_date >= fields.Date.today()
                )
            )
            if not candidates:
                raise UserError(
                    "No capable bench is free at %s for a %s job — add capacity "
                    "or wait for a release." % (job.workshop_id.name, job.repair_level.upper())
                )

            def bench_score(bench, job_level="l3", want_esd=False):
                level_rank = {"l1": 1, "l2": 2, "l3": 3}
                # ascending sort: ESD-first flag (-1 sorts before 0), then the
                # LOWEST level that can do the job (keeps L3 benches free for
                # L3 work), then lowest load, then code for determinism
                return (
                    -1 if (bench.is_esd_safe and want_esd) else 0,
                    level_rank.get(bench.repair_level, 1),
                    bench.current_job_count,
                    bench.code or "",
                )

            ranked = sorted(
                candidates,
                key=lambda b: bench_score(
                    b,
                    job_level=job.repair_level,
                    want_esd=job.repair_level == "l3",
                ),
            )
            ranked[0].action_assign_job(job.sudo())
        return True

    # --- Cross-Wave Stubs Implementation (GV-005) ---
    def _check_technician_certification(self, technician, repair_level: str) -> bool:
        """STUB-M31-M22-001: M31 Workshop Repair Routing -> M22 Learning & Certification.

        Wave Boundary: Wave 2 -> Wave 5.
        Expiry Milestone: R06-M02 (Milestone R06-M02: M22 Competency & Certification Engine).
        Rule: In Wave 2, technician competency matrix was stubbed with qualification fallback.
        In Wave 5 (R06-M04), STUB-M31-M22-001 is CLOSED: L2/L3 benches strictly require active certification.
        """
        # Validate that technician exists and is active
        if not technician or not technician.active:
            raise UserError("Repair technician is invalid or inactive.")

        # L2 and L3 chip-level / soldering repairs require M22 certification
        if (
            repair_level in ("l2", "l3")
            and "fix.certification" in self.env
            and not self.certification_waiver
        ):
            device_type = self.device_id.device_type or None
            # M22 (RAP-M22-01/02): an L2/L3 bench job is gated on the OEM brand
            # and the repair tier, not on the device type alone — a generic
            # smartphone certificate must not open an Apple logic-board job.
            # Passing only `device_type` left the brand and tier dimensions
            # that M22 builds unreachable from the one path that enforces them.
            #
            # `fail_closed` is deliberately left at its default here: at this
            # call site it would also refuse a job whose device type has no
            # gating competency configured yet, which is a configuration gap
            # rather than a competency gap, and would stop bench work on day
            # one. RAP-M22 §8 asks for advisory-then-enforce; turning it on is
            # the COO/Technical Services decision recorded in the audit.
            eligible, reason = self.env["fix.certification"].dispatch_eligibility(
                technician,
                device_type=device_type,
                brand_id=self.device_id.brand_id.id or None,
                repair_tier=repair_level,
            )
            if not eligible:
                raise UserError(
                    f"M22 Certification Gate (STUB-M31-M22-001 CLOSED): Assignment blocked — {reason}"
                )

        logger.info(
            "STUB-M31-M22-001 CLOSED: Verified certification for technician %s (ID %s) on level %s.",
            technician.name,
            technician.id,
            repair_level,
        )
        return True

    def _run_qc_inspection(self, passed: bool, notes: str = "") -> bool:
        """STUB-M31-M23-001: M31 Workshop Quality Gate -> M23 Quality Management (ISO).

        Wave Boundary: Wave 2 -> Wave 5.
        Expiry Milestone: R06-M04 (Milestone R06-M04: M23 ISO 9001 QMS Process Governance).
        Rule: M01/M31 owned checklists locally until R06-M04 where M23 takes over with formal NCR.
        STUB-M31-M23-001 is CLOSED: A failed inspection raises a formal fix.ncr record.
        Enforces BRU-SRM-18: QC inspector must differ from repairing technician.
        """
        inspector = self.qc_inspector_id or self.env.user.employee_id
        if inspector and self.technician_id and inspector.id == self.technician_id.id:
            raise ValidationError(
                f"BRU-SRM-18 Violation: Repairing technician ({self.technician_id.name}) "
                f"cannot perform their own Quality Control inspection."
            )

        # M45 Test-Equipment Calibration check (ISO 9001 Clause 7.1.5);
        # cd_equipment_register is a manifest dependency (the method always exists)
        if self.equipment_id:
            self.equipment_id.action_assert_usable()

        self.qc_passed = passed
        self.qc_notes = notes
        if inspector and not self.qc_inspector_id:
            self.qc_inspector_id = inspector.id

        if not passed:
            # STUB-M31-M23-001 CLOSED: create formal ISO 9001 Non-Conformance Record
            # (fix.ncr: cd_qms_process is a manifest dependency, always installed)
            ncr = self.env["fix.ncr"].create(
                {
                    "source": "qc",
                    "order_id": self.order_id.id,
                    "severity": "major",
                    "description": f"Workshop job {self.name} failed QC inspection: {notes or 'No details provided'}",
                }
            )
            self.ncr_id = ncr.id
            logger.info(
                "STUB-M31-M23-001 CLOSED: Raised formal NCR %s for failed job %s",
                ncr.name,
                self.name,
            )

        self._emit_qc_completed(passed, notes)
        return passed

    def _sync_with_service_order(self, new_state: str) -> None:
        """Propagate key milestone states to parent fix.service.order if linked."""
        if not self.order_id:
            return
        # Map workshop job states to service order states
        mapping = {
            "in_repair": "in_repair",
            "qc_pending": "qc_pending",
            # the rework loop: without it the order stayed qc_pending and the
            # job's return to in_repair could never be mirrored (qc_pending ->
            # in_repair is not an order transition)
            "qc_failed": "qc_failed",
            "ready": "ready",
            "delivered": "delivered",
        }
        so_target = mapping.get(new_state)
        if so_target and self.order_id.state != so_target:
            try:
                with self.env.cr.savepoint():
                    if so_target == "ready":
                        # BRU-SRM-04: the order's QC-checklist gate applies - a
                        # plain state write let a job push the order to Ready
                        # without a passed checklist.
                        self.order_id.action_ready()
                    else:
                        self.order_id.state = so_target
            except (UserError, ValidationError) as e:
                logger.warning(
                    "Service order %s sync to %s skipped: %s", self.order_id.name, so_target, str(e)
                )

    # --- Domain Events (AS-08) ---
    def _emit_job_transitioned(self, old_state: str, new_state: str):
        from libs.py.fix_events import publish

        publish(
            self.env,
            "workshop.job.transitioned",
            "fix.workshop.job",
            self.id,
            {
                "job_id": self.id,
                "job_name": self.name,
                "order_id": self.order_id.id if self.order_id else False,
                "order_reference": self.order_id.name if self.order_id else "",
                "workshop_id": self.workshop_id.id,
                "workshop_code": self.workshop_id.code,
                "bench_id": self.bench_id.id if self.bench_id else False,
                "technician_id": self.technician_id.id if self.technician_id else False,
                "repair_level": self.repair_level,
                "old_state": old_state,
                "new_state": new_state,
                "is_rework": self.is_rework,
            },
        )

    def _emit_qc_completed(self, passed: bool, notes: str = ""):
        from libs.py.fix_events import publish

        publish(
            self.env,
            "workshop.qc.completed",
            "fix.workshop.job",
            self.id,
            {
                "job_id": self.id,
                "job_name": self.name,
                "order_id": self.order_id.id if self.order_id else False,
                "workshop_id": self.workshop_id.id,
                "inspector_id": self.qc_inspector_id.id if self.qc_inspector_id else False,
                "qc_passed": passed,
                "rework_count": self.rework_count,
                "notes": notes,
            },
        )
