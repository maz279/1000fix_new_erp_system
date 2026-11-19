# fix.workshop.job — Workshop Repair Order & Execution Job (CD-M31-01, RR-03 Milestone R03-M02).
# Full state machine unified with AS-06, bench routing, multi-job handling, burn-in, costing, and stubs.
#
# A02 workflow audit (2026-11-03), M31-1 … M31-12: every gate in this file lived
# in an action method while the fields those gates protect (state, qc_passed,
# burn_in_passed, the burn-in minutes, certification_waiver, qc_inspector_id)
# were writable by the technician through the ORM and /p03/model/write. A draft
# L2 job was written straight to "delivered" with QC and burn-in "passed", and a
# technician passed his own QC by typing a colleague into qc_inspector_id. The
# job is now guarded (fix.guarded.mixin): those fields change only through the
# transition methods below, which write through `_guarded()`.
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
    ("unrepairable", "Unrepairable / BER — Written Off"),
    ("cancelled", "Cancelled"),
]

# State transitions authority (AS-06 / DP-01)
VALID_JOB_TRANSITIONS = {
    "draft": {"intake", "cancelled"},
    "intake": {"diagnostic", "waiting_parts", "in_repair", "cancelled"},
    "diagnostic": {"waiting_parts", "in_repair", "unrepairable", "cancelled"},
    "waiting_parts": {"in_repair", "unrepairable", "cancelled"},
    "in_repair": {"burn_in", "qc_pending", "waiting_parts", "unrepairable", "cancelled"},
    # A02 ERP audit M31-F19: no burn_in -> qc_failed edge. The order is
    # still in repair during burn-in and M01 has no repair -> QC-failed move,
    # so that edge raised against M01; a failed burn-in goes back to the bench.
    "burn_in": {"qc_pending", "in_repair"},
    "qc_pending": {"ready", "qc_failed"},
    "qc_failed": {"in_repair", "diagnostic", "unrepairable", "cancelled"},
    "ready": {"delivered"},
    "delivered": set(),
    "unrepairable": set(),
    "cancelled": set(),
}

# A02 audit M31-1: the workflow, approval and evidence fields. Only a
# transition method below may change them (fix.guarded.mixin).
GUARDED_JOB_FIELDS = frozenset(
    {
        "state",
        # QC (BRU-SRM-18 / WSR-04): stamped from the acting inspector
        "qc_passed",
        "qc_notes",
        "qc_inspector_id",
        "qc_inspector_user_id",
        "qc_inspected_at",
        "ncr_id",
        # burn-in (FLAW-31.3): stamped by the burn-in actions, never typed
        "burn_in_started_at",
        "burn_in_completed_at",
        "burn_in_actual_minutes",
        "thermal_crash_count",
        "burn_in_passed",
        # M22 certification waiver: a supervisor action
        "certification_waiver",
        "certification_waiver_reason",
        "certification_waiver_by_id",
        "certification_waiver_at",
        "certification_waiver_technician_id",
        # A02 ERP audit M31-F14: the typed labour figure defeated the BRU-WSR-11
        # cost gate. Labour comes from the work clock at the workshop rate;
        # the typed figure is used only where no rate is set, and is recorded
        # by a supervisor through action_record_labour.
        "labour_total",
        # release / rework / write-off stamps
        "completed_at",
        "dofa_writeoff_tier",
        "rework_of_id",
        "is_rework",
        "rework_count",
        "rework_reason",
        "ber_reason",
        "ber_writeoff_amount",
        "ber_proposed_by_id",
        "ber_proposed_at",
        "ber_confirmed_by_id",
        "ber_confirmed_at",
    }
)

# A02 audit M31-4 / P31-10: once a job is closed its cost and routing are the
# record of what was done; a delivered job's labour went from 500 to 140,000.
CLOSED_JOB_STATES = ("delivered", "unrepairable", "cancelled")
JOB_FROZEN_WHEN_CLOSED = frozenset(
    {
        "labour_total",
        "repair_level",
        "order_id",
        "workshop_id",
        "technician_id",
        "bench_id",
        "device_id",
        "device_serial",
        "customer_id",
        "equipment_id",
        "sam_standard_minutes",
        "actual_logged_minutes",
        "diagnostic_findings",
        "repair_action_summary",
        "pre_rework_photo_attachment_id",
        "post_rework_photo_attachment_id",
    }
)
# The repairing technician is what QC's segregation of duties compares
# against, and the repair level decides the certification, burn-in and
# evidence gates: while the job is on the bench or in test neither changes
# (a downgrade from L2 to L1 would skip the burn-in).
TECHNICIAN_LOCKED_STATES = ("in_repair", "burn_in", "qc_pending", "ready", *CLOSED_JOB_STATES)
ROUTING_LOCKED_FIELDS = frozenset({"technician_id", "repair_level"})

# A02 audit M31-3: the parent-order states in which repair may proceed.
ORDER_CLEARED_FOR_REPAIR = ("approved", "in_repair", "qc_failed")

# A02 audit M31-8: the evidence pack a release needs.
RELEASE_EVIDENCE = ("post_repair_photo", "test_log")
RELEASE_EVIDENCE_L2_L3 = ("burn_in_log",)

GROUP_TECHNICIAN = "cd_workshop.group_fix_workshop_user"
GROUP_SUPERVISOR = "cd_workshop.group_fix_workshop_manager"
GROUP_QC_INSPECTOR = "cd_workshop.group_fix_workshop_qc_inspector"

# FLAW-31.3 default; a policy number, so it is a config parameter.
BURN_IN_MIN_MINUTES_PARAM = "cd_workshop.burn_in_min_minutes"
BURN_IN_MIN_MINUTES_DEFAULT = 240.0

# A07 audit (2026-11-03) M45-4 / BRU-EAM-15: every QC pass names the test
# instrument it was measured with. Live, 0 of 65 QC'd jobs name one and 7 of 13
# instruments have never been calibrated, so enforcing it on deploy would stop
# every QC pass: it is a business switch, off by default ("1"/"true" = on).
QC_REQUIRES_INSTRUMENT_PARAM = "cd_workshop.qc_requires_instrument"

# BER / scrap write-off ladder, from the tier labels already on the job
# (Tier 2 ≤ 10,000 BDT, Tier 3 ≤ 50,000 BDT, Tier 4 above).
BER_DOFA_THRESHOLDS = [
    (10000.0, "tier_2"),
    (50000.0, "tier_3"),
    (float("inf"), "tier_4"),
]


class FixWorkshopJob(models.Model):
    """A workshop repair job — the central unit of execution within the depot.

    Carries repair-level routing (L1/L2/L3), bench allocation, spare parts consumption,
    evidence packs, burn-in testing, and quality control.
    """

    _name = "fix.workshop.job"
    _description = "Workshop Repair Job"
    # fix.dofa.mixin brings fix.guarded.mixin (A1) and the DOFA approval used
    # by the BER / scrap write-off (A02 audit M31-9).
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.dofa.mixin"]
    _order = "priority desc, create_date desc"

    # A02 audit B1: the BER write-off is decided from the approver's M63
    # inbox (the apply method is action_dofa_approve, which closes the job).
    # Confirm BER requests it; a direct press of Approve is refused.
    _approval_domain = "workshop_ber"
    _approval_routed = True

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | GUARDED_JOB_FIELDS

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if len(self) != 1:
            return locked
        if self.state != "draft":
            locked |= {"order_id"}
        if self.state in TECHNICIAN_LOCKED_STATES:
            locked |= ROUTING_LOCKED_FIELDS
        if self.state in CLOSED_JOB_STATES:
            locked |= JOB_FROZEN_WHEN_CLOSED
        return locked

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
        readonly=True,
        tracking=True,
        help="Independent QC inspector (BRU-SRM-18: must differ from repairing technician). "
        "Stamped from the user who ran the inspection, never typed.",
    )
    qc_inspector_user_id = fields.Many2one(
        "res.users",
        string="QC Inspected By",
        readonly=True,
        copy=False,
        tracking=True,
        help="The user who ran the QC inspection (A02 audit M31-2).",
    )
    qc_inspected_at = fields.Datetime(string="QC Inspected At", readonly=True, copy=False)
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
        readonly=True,
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
        default=0.0,
        readonly=True,
        tracking=True,
        help="FLAW-31.3: L2/L3 board repairs require >= 240 minutes continuous stress testing. "
        "Measured from the burn-in start and end stamps (A02 audit M31-6), never typed.",
    )
    thermal_crash_count = fields.Integer(
        string="Thermal / Stress Crashes",
        default=0,
        readonly=True,
        tracking=True,
        help="FLAW-31.3: Must be 0 to pass burn-in. Counted by Log Thermal Crash.",
    )
    burn_in_started_at = fields.Datetime(string="Burn-In Started At", readonly=True)
    burn_in_completed_at = fields.Datetime(string="Burn-In Completed At", readonly=True)
    burn_in_temp_celsius = fields.Float(string="Chamber Temp (°C)", default=40.0)
    burn_in_passed = fields.Boolean(
        string="Burn-In Passed", default=False, readonly=True, tracking=True
    )

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
    # A02 audit M31-9 / P31-11: the tier was a free Selection the technician
    # set himself and nothing read. It is now derived from the write-off amount.
    dofa_writeoff_tier = fields.Selection(
        [
            ("none", "No Write-Off Required"),
            ("tier_2", "Tier 2 — Service Center Manager (<= 10,000 BDT)"),
            ("tier_3", "Tier 3 — Regional Service Head (<= 50,000 BDT)"),
            ("tier_4", "Tier 4 — Head of Service & Finance (> 50,000 BDT)"),
        ],
        string="DOFA BER / Scrap Write-Off Tier",
        compute="_compute_dofa_writeoff_tier",
        store=True,
        help="Derived from the BER write-off amount. Never set by hand.",
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
    qc_passed = fields.Boolean(string="QC Passed", default=False, readonly=True, tracking=True)
    qc_notes = fields.Text(string="QC Inspection Notes", readonly=True)
    ncr_id = fields.Many2one(
        "fix.ncr",
        string="NCR (M23)",
        ondelete="set null",
        readonly=True,
        help="Formal ISO 9001 Non-Conformance Record (STUB-M31-M23-001 CLOSED)",
    )
    # A02 audit M31-5 / P31-07: the technician ticked this on his own job.
    # It is now granted by a supervisor (action_grant_certification_waiver),
    # stamped with who and when, and covers only the technician it was
    # granted for.
    certification_waiver = fields.Boolean(
        string="Certification Waiver",
        readonly=True,
        copy=False,
        help="Supervisor waiver for L2/L3 repair assignment (audited)",
    )
    certification_waiver_reason = fields.Char(
        string="Waiver Justification", readonly=True, copy=False
    )
    certification_waiver_by_id = fields.Many2one(
        "res.users", string="Waiver Granted By", readonly=True, copy=False
    )
    certification_waiver_at = fields.Datetime(string="Waiver Granted At", readonly=True, copy=False)
    certification_waiver_technician_id = fields.Many2one(
        "hr.employee",
        string="Waiver Covers Technician",
        readonly=True,
        copy=False,
        help="A waiver is granted for one technician; reassigning the job voids it.",
    )

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
    is_rework = fields.Boolean(
        string="Internal Rework", default=False, readonly=True, tracking=True
    )
    rework_count = fields.Integer(string="Rework Count", default=0, readonly=True)
    rework_reason = fields.Text(string="Rework Reason", readonly=True)
    rework_of_id = fields.Many2one(
        "fix.workshop.job",
        string="Rework Of Job",
        index=True,
        readonly=True,
    )

    # BER / scrap (A02 audit M31-9): proposed by the bench, approved under
    # DOFA on the write-off amount, confirmed by a second technician.
    ber_reason = fields.Text(string="BER / Scrap Reason", readonly=True, copy=False)
    ber_writeoff_amount = fields.Monetary(
        string="Write-Off Amount",
        readonly=True,
        copy=False,
        currency_field="currency_id",
        help="The value written off. Never below the cost already sunk into the job.",
    )
    ber_proposed_by_id = fields.Many2one(
        "res.users", string="BER Proposed By", readonly=True, copy=False
    )
    ber_proposed_at = fields.Datetime(string="BER Proposed At", readonly=True, copy=False)
    ber_confirmed_by_id = fields.Many2one(
        "res.users", string="BER Confirmed By (Second Technician)", readonly=True, copy=False
    )
    ber_confirmed_at = fields.Datetime(string="BER Confirmed At", readonly=True, copy=False)

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

    def _m31_fitted_parts_cost(self) -> float:
        """A02 ERP audit M31-F12: only parts consumed on the bench cost the
        job. A draft, reserved or released line was counted, so a reserved
        part that went back to stores still sat in the cost and the BER
        write-off."""
        self.ensure_one()
        return sum(
            line.subtotal for line in self.part_line_ids if line.reservation_state == "consumed"
        )

    @api.depends("part_line_ids.subtotal", "part_line_ids.reservation_state", "labour_total")
    def _compute_totals(self):
        # labour and consumables are added by the work clock (capture2)
        for rec in self:
            parts = rec._m31_fitted_parts_cost()
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

    # --- DOFA on the BER write-off (A02 audit M31-9) ---
    def _dofa_amount(self) -> float:
        self.ensure_one()
        if not self.ber_proposed_at:
            return 0.0
        # the sunk cost cannot be understated to reach a lower tier
        return max(self.ber_writeoff_amount or 0.0, self.total_repair_cost or 0.0)

    def _dofa_thresholds(self):
        return BER_DOFA_THRESHOLDS

    def _dofa_amount_label(self) -> str:
        self.ensure_one()
        return "the BER write-off of BDT %.2f on %s" % (self._dofa_amount(), self.name)

    @api.depends("ber_writeoff_amount", "ber_proposed_at", "total_repair_cost")
    def _compute_dofa_tier_required(self):
        return super()._compute_dofa_tier_required()

    @api.depends("ber_writeoff_amount", "ber_proposed_at", "total_repair_cost")
    def _compute_dofa_writeoff_tier(self):
        for rec in self:
            tier = rec._dofa_current_tier()
            rec.dofa_writeoff_tier = tier if tier in ("tier_2", "tier_3", "tier_4") else "none"

    # --- Frozen records (A02 audit M31-1 / M31-4) ---
    def write(self, vals):
        # --- A07 P1 (2026-11-04) M45 probe 22 --------------------------------
        # The QC instrument is measurement evidence for EVERY caller, the
        # superuser included (sudo service code and imports too): once QC has
        # passed it changes only inside a guarded transition.
        if self and "equipment_id" in vals and not self._fix_guard_has_token():
            for rec in self.filtered("qc_passed"):
                if rec._fix_guard_differs("equipment_id", vals["equipment_id"], rec.equipment_id):
                    raise UserError(
                        "Test Equipment Used cannot be changed on job %s while it is %s: "
                        "it is the measurement evidence of the QC pass."
                        % (rec.name, dict(WORKSHOP_JOB_STATES).get(rec.state, rec.state))
                    )
        # --- end A07 P1 M45 ----------------------------------------------------
        if self and not self._fix_guard_open():
            for rec in self:
                frozen = set()
                if rec.state != "draft":
                    frozen |= {"order_id"}
                if rec.state in TECHNICIAN_LOCKED_STATES:
                    frozen |= ROUTING_LOCKED_FIELDS
                if rec.state in CLOSED_JOB_STATES:
                    frozen |= JOB_FROZEN_WHEN_CLOSED
                # A07 audit (2026-11-03) M45-4: the instrument is the QC
                # measurement evidence; it was frozen only once the job closed,
                # so it could be cleared or swapped right after QC passed
                if rec.qc_passed:
                    frozen |= {"equipment_id"}
                changed = sorted(
                    name
                    for name in frozen & set(vals)
                    if rec._fix_guard_differs(name, vals[name], rec[name])
                )
                if changed:
                    labels = ", ".join(rec._fields[n].string or n for n in changed)
                    raise UserError(
                        "%s cannot be changed on job %s while it is %s: %s"
                        % (
                            labels,
                            rec.name,
                            dict(WORKSHOP_JOB_STATES).get(rec.state, rec.state),
                            "a closed job is the record of the repair."
                            if rec.state in CLOSED_JOB_STATES
                            else "the parent order and the repairing technician are fixed "
                            "once the job is under way (QC independence and the approved "
                            "estimate are checked against them).",
                        )
                    )
        return super().write(vals)

    # --- Roles and segregation of duties (A02 audit M31-2 / M31-5) ---
    def _m31_require_group(self, xmlids, what):
        """The acting user must hold one of these groups. Superuser code
        (crons, seeds, sudo service calls) is trusted, as by the guard."""
        if self.env.su:
            return
        if any(self.env.user.has_group(x) for x in xmlids):
            return
        names = []
        for xmlid in xmlids:
            group = self.env.ref(xmlid, raise_if_not_found=False)
            names.append(group.sudo().name if group else xmlid)
        raise UserError(
            "%s needs the %s role. You do not hold it; ask a workshop supervisor."
            % (what, " or ".join("'%s'" % n for n in names))
        )

    def _m31_actor_is_technician(self) -> bool:
        """Is the acting user the job's repairing technician? Compared on the
        user who acts, never on a field the technician can type."""
        self.ensure_one()
        # sudo: a technician may not read other employees' HR fields, and the
        # comparison must not depend on what the actor is allowed to see
        tech = self.sudo().technician_id
        if not tech:
            return False
        user = self.env.user.sudo()
        if tech.user_id and tech.user_id.id == user.id:
            return True
        return tech.id in user.employee_ids.ids

    # --- State Machine Transitions (AS-06) ---
    def _validate_transition(self, new_state: str) -> None:
        self.ensure_one()
        valid_next = VALID_JOB_TRANSITIONS.get(self.state, set())
        if new_state not in valid_next:
            raise UserError(
                f"Invalid job state transition: {self.state} -> {new_state}. "
                f"Permitted next states from '{self.state}' are: {', '.join(sorted(valid_next)) or 'None (Terminal)'}"
            )

    # A02 audit M31-7 / P31-06: the generic transition was whitelisted in P03,
    # so a QC fail reached qc_failed with no NCR and no rework count, and the
    # burn-in state was skippable. The public entry point now dispatches to the
    # target's dedicated method, so every target carries its side-effects;
    # targets whose method needs a decision (QC verdict, BER) are refused.
    _TRANSITION_METHODS = {
        "intake": "action_intake",
        "diagnostic": "action_diagnostic",
        "waiting_parts": "action_wait_parts",
        "in_repair": "action_start_repair",
        "burn_in": "action_start_burn_in",
        "qc_pending": "action_submit_qc",
        "delivered": "action_deliver",
        "cancelled": "action_cancel",
    }

    def action_transition(self, new_state: str):
        """Move the job to `new_state` through that state's own action."""
        method = self._TRANSITION_METHODS.get(new_state)
        if not method:
            raise UserError(
                "'%s' is reached only through its own action (Pass QC, Fail QC, Pass "
                "Burn-In, Confirm BER), which records the inspector, the NCR or the "
                "approval. It cannot be set as a plain transition."
                % dict(WORKSHOP_JOB_STATES).get(new_state, new_state)
            )
        return getattr(self, method)()

    def _transition(self, new_state: str):
        """Execute state transition with business gate enforcement and event publication."""
        for rec in self:
            rec._validate_transition(new_state)
            old_state = rec.state

            # Business Gate: In Repair requires bench & technician eligibility check
            if new_state == "in_repair":
                rec._m31_check_order_cleared_for_repair(old_state)
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
                # A repair (or a rework) is a new build: the burn-in that
                # covered the previous build does not cover this one.
                if rec.burn_in_passed:
                    rec._guarded().write({"burn_in_passed": False})

            # Business Gate: QC Pending requires burn-in pass if L2 or L3
            if (
                new_state == "qc_pending"
                and rec.repair_level in ("l2", "l3")
                and not rec.burn_in_passed
            ):
                raise UserError(
                    f"Job {rec.name} ({rec.repair_level.upper()}) requires burn-in test to pass before QC."
                )

            # Business Gate: Ready requires QC inspection and the evidence pack
            if new_state == "ready":
                if not rec.qc_passed:
                    raise UserError(
                        f"Job {rec.name} cannot be marked 'Ready' without passing Quality Control."
                    )
                rec._m31_check_release_evidence()
                rec._guarded().write({"completed_at": fields.Datetime.now()})

            # Release the bench when the job leaves the bench for good
            if new_state in ("ready", "unrepairable", "cancelled") and rec.bench_id:
                rec.bench_id.action_release_job(rec)

            rec._guarded().write({"state": new_state})
            rec._emit_job_transitioned(old_state, new_state)

            # Synchronize with parent service order if present. Raises: a job
            # cannot move where its order cannot legally follow (M31-3).
            rec._sync_with_service_order(new_state, old_state)

        return True

    def action_intake(self):
        return self._transition("intake")

    def action_diagnostic(self):
        return self._transition("diagnostic")

    def action_wait_parts(self):
        return self._transition("waiting_parts")

    def action_start_repair(self):
        return self._transition("in_repair")

    def action_submit_qc(self):
        """Bench work done: hand the job to QC (in_repair -> qc_pending). L2/L3
        jobs reach QC only through Pass Burn-In."""
        return self._transition("qc_pending")

    def action_start_burn_in(self):
        """A02 audit M31-6: burn-in is a real state with a server start stamp.
        Each run starts clean: a re-run after rework does not inherit the old
        run's minutes or crash count."""
        for rec in self:
            rec._validate_transition("burn_in")
            rec._guarded().write(
                {
                    "burn_in_started_at": fields.Datetime.now(),
                    "burn_in_completed_at": False,
                    "burn_in_actual_minutes": 0.0,
                    "thermal_crash_count": 0,
                    "burn_in_passed": False,
                }
            )
            rec._transition("burn_in")
        return True

    def action_log_thermal_crash(self, note=""):
        """Record one thermal / stress crash during the running burn-in. The
        count only rises; a run with a crash cannot pass (FLAW-31.3)."""
        for rec in self:
            if rec.state != "burn_in":
                raise UserError("A thermal crash is logged only while the job is in burn-in.")
            rec._guarded().write({"thermal_crash_count": (rec.thermal_crash_count or 0) + 1})
            rec.message_post(
                body="Thermal / stress crash #%d logged by %s%s"
                % (rec.thermal_crash_count, self.env.user.name, (": %s" % note) if note else ".")
            )
        return True

    def _m31_burn_in_min_minutes(self) -> float:
        raw = self.env["ir.config_parameter"].sudo().get_param(BURN_IN_MIN_MINUTES_PARAM)
        try:
            return float(raw) if raw not in (None, False, "") else BURN_IN_MIN_MINUTES_DEFAULT
        except (TypeError, ValueError):
            return BURN_IN_MIN_MINUTES_DEFAULT

    def _m31_close_burn_in_run(self):
        """Stamp the end of the run; the minutes come from the two stamps."""
        self.ensure_one()
        if not self.burn_in_started_at:
            raise UserError(
                f"FLAW-31.3 Burn-In Gate: job {self.name} has no burn-in start stamp. "
                "Start the burn-in run first."
            )
        now = fields.Datetime.now()
        minutes = round(max(0.0, (now - self.burn_in_started_at).total_seconds() / 60.0), 2)
        self._guarded().write({"burn_in_completed_at": now, "burn_in_actual_minutes": minutes})
        return minutes

    def action_pass_burn_in(self):
        """A02 audit M31-6 / P31-05: runs only from the burn_in state, and the
        minutes are measured from the start and end stamps, not typed."""
        for rec in self:
            if rec.state != "burn_in":
                raise UserError(
                    f"FLAW-31.3 Burn-In Gate: job {rec.name} is not in burn-in "
                    f"(state: {rec.state}). Start the burn-in run first."
                )
            if rec.repair_level in ("l2", "l3"):
                if not rec.burn_in_started_at:
                    raise UserError(
                        f"FLAW-31.3 Burn-In Gate: job {rec.name} has no burn-in start stamp."
                    )
                elapsed = (fields.Datetime.now() - rec.burn_in_started_at).total_seconds() / 60.0
                required = rec._m31_burn_in_min_minutes()
                if elapsed < required:
                    raise UserError(
                        f"FLAW-31.3 Burn-In Gate: {rec.repair_level.upper()} repair job {rec.name} requires at least "
                        f"{required:.0f} minutes continuous burn-in stress testing (running: {elapsed:.0f} min)."
                    )
                if (rec.thermal_crash_count or 0) > 0:
                    raise UserError(
                        f"FLAW-31.3 Burn-In Gate: Job {rec.name} experienced {rec.thermal_crash_count} thermal/stress crashes during burn-in."
                    )
            rec._m31_close_burn_in_run()
            rec._guarded().write({"burn_in_passed": True})
            rec._transition("qc_pending")
        return True

    def action_fail_burn_in(self, reason=""):
        """End a failed burn-in run and return the job to the bench."""
        for rec in self:
            if rec.state != "burn_in":
                raise UserError(f"Job {rec.name} is not in burn-in.")
            rec._m31_close_burn_in_run()
            rec._guarded().write({"burn_in_passed": False})
            rec.message_post(
                body="Burn-in failed after %.0f min (%d crashes)%s"
                % (
                    rec.burn_in_actual_minutes,
                    rec.thermal_crash_count,
                    (": %s" % reason) if reason else ".",
                )
            )
            rec._transition("in_repair")
        return True

    def _m31_assert_qc_inspector(self):
        """A02 audit M31-2 / P31-03 (BRU-SRM-18): the inspector is the user who
        acts. He must hold the QC inspector or supervisor role and must not be
        the repairing technician; a typed qc_inspector_id no longer counts."""
        self.ensure_one()
        self._m31_require_group((GROUP_QC_INSPECTOR, GROUP_SUPERVISOR), "A QC inspection")
        if self._m31_actor_is_technician():
            raise ValidationError(
                f"BRU-SRM-18 Violation: Repairing technician ({self.technician_id.name}) "
                f"cannot perform their own Quality Control inspection."
            )

    def action_pass_qc(self, notes=""):
        """Pass QC inspection and advance to ready."""
        for rec in self:
            rec._validate_transition("ready")
            rec._run_qc_inspection(passed=True, notes=notes)
            rec._transition("ready")
        return True

    def action_fail_qc(self, reason=""):
        """Fail QC inspection: raise the NCR and open the rework loop (qc_failed).

        The transition is validated FIRST - the old body wrote ``state`` directly,
        so a draft or delivered job could "fail QC" - and goes through
        _transition (transition event + service-order sync). The QC event is
        emitted once, by _run_qc_inspection: the old body emitted it a second time,
        so every failure was counted twice downstream."""
        for rec in self:
            rec._validate_transition("qc_failed")
            rec._run_qc_inspection(passed=False, notes=reason)
            rec._guarded().write(
                {"is_rework": True, "rework_count": rec.rework_count + 1, "rework_reason": reason}
            )
            rec._transition("qc_failed")
        return True

    def _m31_release_evidence_types(self):
        self.ensure_one()
        needed = list(RELEASE_EVIDENCE)
        if self.repair_level in ("l2", "l3"):
            needed += list(RELEASE_EVIDENCE_L2_L3)
        return needed

    def _m31_check_release_evidence(self):
        """A02 audit M31-8 / P31-13: a release needs its evidence pack — a
        post-repair photo and a test log, plus the burn-in log for L2/L3.
        37 of 37 live deliveries carried none (warranty defensibility)."""
        self.ensure_one()
        # only evidence whose governed document was filed against THIS job
        # counts: a row pointing at another job's photo proves nothing here
        evidence = self.sudo().evidence_ids.filtered(
            lambda ev: ev.document_id.res_model == self._name and ev.document_id.res_id == self.id
        )
        have = set(evidence.mapped("evidence_type"))
        missing = [t for t in self._m31_release_evidence_types() if t not in have]
        if missing:
            labels = dict(self.env["fix.workshop.evidence"]._fields["evidence_type"].selection)
            raise UserError(
                "Job %s cannot be released without its evidence pack. Missing: %s."
                % (self.name, "; ".join(labels.get(t, t) for t in missing))
            )

    def action_deliver(self):
        return self._transition("delivered")

    def action_cancel(self):
        return self._transition("cancelled")

    # --- M22 certification waiver (A02 audit M31-5, B1) ---
    def action_grant_certification_waiver(self, reason=""):
        """A02 audit B1: a waiver is no longer granted by pressing a button on
        the job. This (the old button's name) now raises the routed request,
        which a Workshop Supervisor other than the requester and the
        repairing technician grants from his M63 inbox
        (fix.workshop.waiver.request.action_grant)."""
        return self.action_request_certification_waiver(reason)

    def _m31_waiver_covers(self, technician) -> bool:
        self.ensure_one()
        if not self.certification_waiver:
            return False
        # rows waived before the waiver named its technician keep their waiver
        covered = self.certification_waiver_technician_id
        return not covered or covered == technician

    # --- BER / scrap write-off (A02 audit M31-9) ---
    def action_propose_ber(self, reason="", writeoff_amount=0.0):
        """The bench declares the device beyond economic repair. The write-off
        amount (never below the cost already sunk) sets the DOFA tier; the
        approval and a second technician's confirmation follow."""
        for rec in self:
            rec._m31_require_group((GROUP_TECHNICIAN,), "Proposing a BER write-off")
            if "unrepairable" not in VALID_JOB_TRANSITIONS.get(rec.state, set()):
                raise UserError(f"Job {rec.name} cannot be declared BER from state {rec.state}.")
            if not (reason or "").strip():
                raise UserError("A BER / scrap proposal needs the reason and the evidence seen.")
            if rec.approval_state == "pending":
                raise UserError(
                    f"The BER write-off on job {rec.name} is already awaiting approval."
                )
            # A02 audit M31 steps 11-12: the evidence seen is on the job
            rec._m31_check_ber_evidence()
            amount = max(float(writeoff_amount or 0.0), rec.total_repair_cost or 0.0)
            rec._guarded().write(
                {
                    "ber_reason": reason.strip(),
                    "ber_writeoff_amount": amount,
                    "ber_proposed_by_id": self.env.user.id,
                    "ber_proposed_at": fields.Datetime.now(),
                    # a new proposal needs a new confirmation
                    "ber_confirmed_by_id": False,
                    "ber_confirmed_at": False,
                }
            )
            rec.message_post(
                body="BER proposed by %s (write-off BDT %.2f): %s"
                % (self.env.user.name, rec._dofa_amount(), reason.strip())
            )
        return True

    def action_dofa_approve(self):
        """The BER write-off approval, and the engine's apply method (A02
        audit B1): it runs only from the approver's M63 inbox, and it does the
        real state change, closing the job as unrepairable (and its order with
        it). On top of the DOFA tier, the job's creator check and the
        justification (fix.dofa.mixin), the approver is neither the proposer,
        the confirming technician nor the repairing technician."""
        self._approval_assert_routed()
        for rec in self:
            if not rec.ber_proposed_at:
                raise UserError(f"Job {rec.name} has no BER write-off proposal to approve.")
            if not rec.ber_confirmed_at:
                raise UserError(
                    f"The BER on job {rec.name} is confirmed by a second technician before "
                    "its write-off is approved."
                )
            if (
                self.env.user in (rec.ber_proposed_by_id | rec.ber_confirmed_by_id)
                or rec._m31_actor_is_technician()
            ):
                raise UserError(
                    "Segregation of duties: the BER write-off on %s must be approved by "
                    "someone other than its proposer, its confirming technician and the "
                    "repairing technician." % rec.name
                )
        # The checks above ran in the approver's environment, and the DOFA
        # rules below test the approver's (or the absent approver's) tier
        # group and the creator on users, not on env.su. The approver holds a
        # DOFA tier and usually no workshop role, so the stamp, the job's
        # transition and M01's cancellation then run as the system.
        super(FixWorkshopJob, self.sudo()).action_dofa_approve()
        self.sudo()._m31_close_ber()
        return True

    def action_confirm_ber(self):
        """A second technician confirms the BER (FR-WSR-030). A02 audit B1:
        confirming routes the write-off to the DOFA tier holders' M63 inboxes;
        the approval closes the job. A write-off below every DOFA threshold
        needs no approval and closes the job now."""
        for rec in self:
            rec._m31_require_group((GROUP_TECHNICIAN,), "Confirming a BER write-off")
            if not rec.ber_proposed_at:
                raise UserError(f"Job {rec.name} has no BER proposal to confirm.")
            if rec._m31_actor_is_technician() or rec.ber_proposed_by_id == self.env.user:
                raise UserError(
                    "Segregation of duties: a BER is confirmed by a second technician, "
                    "not by the repairing technician or the proposer."
                )
            if rec.approval_state == "pending":
                raise UserError(f"The BER on job {rec.name} is already awaiting approval.")
            if "unrepairable" not in VALID_JOB_TRANSITIONS.get(rec.state, set()):
                raise UserError(f"Job {rec.name} cannot close as BER from state {rec.state}.")
            rec._m31_check_ber_order_can_follow()
            rec._guarded().write(
                {"ber_confirmed_by_id": self.env.user.id, "ber_confirmed_at": fields.Datetime.now()}
            )
            if rec._approval_needed():
                rec.action_request_approval(justification=rec.dofa_justification or rec.ber_reason)
            else:
                rec._m31_close_ber()
        return True

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
            and not self._m31_waiver_covers(technician)
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

    def _m31_qc_requires_instrument(self) -> bool:
        raw = self.env["ir.config_parameter"].sudo().get_param(QC_REQUIRES_INSTRUMENT_PARAM)
        return str(raw or "").strip().lower() in ("1", "true", "yes")

    def _run_qc_inspection(self, passed: bool, notes: str = "") -> bool:
        """STUB-M31-M23-001: M31 Workshop Quality Gate -> M23 Quality Management (ISO).

        Wave Boundary: Wave 2 -> Wave 5.
        Expiry Milestone: R06-M04 (Milestone R06-M04: M23 ISO 9001 QMS Process Governance).
        Rule: M01/M31 owned checklists locally until R06-M04 where M23 takes over with formal NCR.
        STUB-M31-M23-001 is CLOSED: A failed inspection raises a formal fix.ncr record.
        Enforces BRU-SRM-18: QC inspector must differ from repairing technician —
        compared on the acting user (A02 audit M31-2).
        """
        self._m31_assert_qc_inspector()

        # M45 Test-Equipment Calibration check (ISO 9001 Clause 7.1.5);
        # cd_equipment_register is a manifest dependency (the method always exists).
        # A07 audit (2026-11-03) M45-1/M45-4: the gate now refuses failed,
        # never-calibrated, out-of-service and retired instruments, not only
        # overdue ones. An instrument issued to the inspector or to this job's
        # repairing technician is on this bench and counts as in service.
        if (
            passed
            and not self.equipment_id
            and not self.env.su
            and self._m31_qc_requires_instrument()
        ):
            raise UserError(
                "BRU-EAM-15: name the test instrument used for this QC inspection "
                "before passing job %s." % self.name
            )
        if self.equipment_id:
            holder = self.env.user.sudo().employee_ids | self.sudo().technician_id
            self.equipment_id.action_assert_usable(holder=holder)
            # --- A07 P1 (2026-11-04) M45 probe 16, FR-EAM-045 -----------------
            # QC wrote no usage row, so the retrospective impact assessment saw
            # only hand-typed usage. Each inspection made with an instrument is
            # now a use of it, stamped with the calibration at use (M45 service).
            self.env["fix.equipment.usage"].m45_record_qc_use(
                self.equipment_id,
                self.name,
                "pass" if passed else "fail",
                source=self,
                service_order_ref=self.sudo().order_id.name or None,
            )
            # --- end A07 P1 M45 ------------------------------------------------

        self._guarded().write(
            {
                "qc_passed": passed,
                "qc_notes": notes,
                "qc_inspector_id": self.env.user.sudo().employee_id.id or False,
                "qc_inspector_user_id": self.env.user.id,
                "qc_inspected_at": fields.Datetime.now(),
            }
        )

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
            self._guarded().write({"ncr_id": ncr.id})
            logger.info(
                "STUB-M31-M23-001 CLOSED: Raised formal NCR %s for failed job %s",
                ncr.name,
                self.name,
            )

        self._emit_qc_completed(passed, notes)
        return passed

    # --- The M01 hand-back (A02 audit M31-3) ---
    def _m31_check_order_cleared_for_repair(self, old_state: str) -> None:
        """A job leaves diagnosis for repair only once its parent order is
        approved. M01 decides approval (an approved estimate, or a warranty /
        AMC entitlement); the workshop reads the order's state, it does not
        re-decide it. P31-08: a job went to in_repair and on to delivered
        while its order was still a draft."""
        self.ensure_one()
        order = self.order_id
        if not order:
            return
        cleared = set(ORDER_CLEARED_FOR_REPAIR)
        if old_state == "qc_failed":
            # the rework loop: M01 has no QC-fail transition the job can call,
            # so the order is still qc_pending when the job goes back on the bench
            cleared.add("qc_pending")
        if order.state not in cleared:
            raise UserError(
                "Job %s cannot start repair: its service order %s is '%s'. Repair starts "
                "only once the order is approved (an approved estimate, or a verified "
                "warranty / AMC entitlement)."
                % (
                    self.name,
                    order.name,
                    dict(order._fields["state"]._description_selection(self.env)).get(
                        order.state, order.state
                    ),
                )
            )

    # job state -> the fix.service.order method that moves the order there
    _ORDER_SYNC_METHODS = {
        "in_repair": ("in_repair", "action_start_repair"),
        "qc_pending": ("qc_pending", "action_submit_qc"),
        "qc_failed": ("qc_failed", "action_fail_qc"),
        "ready": ("ready", "action_ready"),
        "delivered": ("delivered", "action_deliver"),
    }

    def _sync_with_service_order(self, new_state: str, old_state: str | None = None) -> None:
        """Move the parent order with the job, through the order's OWN
        transition methods (A02 audit M31-3). The old body wrote the order's
        state directly and swallowed every refusal, so 37 of 37 live jobs were
        delivered while their orders sat in draft..qc_pending, all unpaid. A
        refusal now stops the job transition: a job is not delivered when its
        order cannot legally be."""
        if not self.order_id:
            return
        if new_state == "unrepairable":
            # A02 audit B2: a BER reaches M01 (the order stayed in_repair)
            self._m31_order_unrepairable()
            return
        target = self._ORDER_SYNC_METHODS.get(new_state)
        if not target:
            return
        so_state, method = target
        order = self.order_id
        if order.state == so_state:
            return
        if new_state == "in_repair" and old_state == "qc_failed" and order.state == "qc_pending":
            # rework loop while M01 offers no QC-fail transition (see below)
            return
        action = getattr(order, method, None)
        if action is None:
            # M01 has no method for this transition (today: QC failed). The job
            # does not write the order's state itself; the order stays where
            # it is and the gap is recorded on it.
            order.message_post(
                body="Workshop job %s moved to %s; the order has no '%s' transition, so "
                "it stays %s." % (self.name, new_state, method, order.state)
            )
            logger.warning(
                "Service order %s has no %s(); workshop job %s -> %s not mirrored",
                order.name,
                method,
                self.name,
                new_state,
            )
            return
        action()

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
