# fix.workshop.bench — Repair Bench Master (CD-M31-02, RR-03 Milestone R03-M02).
import logging

from odoo import api, fields, models
from odoo.exceptions import UserError

logger = logging.getLogger(__name__)


class FixWorkshopBench(models.Model):
    """A physical workstation or repair bench inside a workshop or depot.

    Benches are classified into L1 (modular), L2 (board/component), and L3 (chip-level/cleanroom),
    equipped with calibrated tools and assigned to qualified technicians.
    """

    _name = "fix.workshop.bench"
    _description = "Workshop Repair Bench"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "workshop_id, repair_level, code"

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

    workshop_id = fields.Many2one(
        "fix.workshop",
        string="Workshop Facility",
        required=True,
        ondelete="cascade",
        index=True,
    )

    code = fields.Char(
        string="Bench Code",
        required=True,
        index=True,
        tracking=True,
        help="Unique bench identifier (e.g., BENCH-TEJ-L1-01, BENCH-TEJ-L3-01)",
    )
    name = fields.Char(
        string="Bench Name",
        required=True,
        tracking=True,
    )
    name_bn = fields.Char(
        string="নাম (বাংলা)",
        required=True,
        help="Bench name in Bengali script",
    )

    # Repair level classification (M31 core routing)
    repair_level = fields.Selection(
        [
            ("l1", "Level 1 — Modular / Quick Fix (Screen, Battery, Housing)"),
            ("l2", "Level 2 — Component / Soldering (Power IC, Sub-PCB, Charging Port)"),
            ("l3", "Level 3 — Chip-Level / Advanced Depot (BGA Reballing, Cleanroom, Motherboard)"),
        ],
        string="Repair Level Capability",
        default="l1",
        required=True,
        tracking=True,
        help="Determines the complexity of repair jobs routed to this bench",
    )

    technician_id = fields.Many2one(
        "hr.employee",
        string="Assigned Bench Technician",
        tracking=True,
        help="Primary technician currently stationed at this bench",
    )

    state = fields.Selection(
        [
            ("available", "Available"),
            ("occupied", "Occupied"),
            ("maintenance", "Under Maintenance / Tool Calibration"),
            ("offline", "Offline / Closed"),
        ],
        string="Bench Status",
        default="available",
        required=True,
        tracking=True,
    )

    max_concurrent_jobs = fields.Integer(
        string="Max Concurrent Jobs",
        default=1,
        help="Multi-job handling capability for homogeneous batch repairs",
    )

    active_job_ids = fields.One2many(
        "fix.workshop.job",
        "bench_id",
        string="Active Bench Jobs",
        domain=[
            (
                "state",
                "in",
                ["intake", "diagnostic", "waiting_parts", "in_repair", "burn_in", "qc_pending"],
            )
        ],
    )
    current_job_count = fields.Integer(
        string="Current Active Jobs",
        compute="_compute_job_count",
        store=True,
    )

    is_esd_safe = fields.Boolean(
        string="ESD Safe Station",
        default=True,
        help="Verified grounding mat, wrist strap, and ESD dissipation monitoring",
    )
    wrist_strap_mohm = fields.Float(
        string="Wrist Strap Resistance (MΩ)",
        default=10.0,
        tracking=True,
        help="FLAW-31.2: ANSI/ESD S20.20 requires < 35.0 MΩ (typical 1.0 - 10.0 MΩ)",
    )
    worksurface_rtg_mohm = fields.Float(
        string="Worksurface Mat Resistance Rtg (MΩ)",
        default=100.0,
        tracking=True,
        help="FLAW-31.2: IEC 61340-5-1 requires < 1000.0 MΩ (< 1x10^9 Ω)",
    )
    esd_last_verified_date = fields.Date(
        string="Daily ESD Log Date",
        default=fields.Date.context_today,
        tracking=True,
    )
    esd_compliant_today = fields.Boolean(
        string="Daily ESD Verification Passed",
        compute="_compute_esd_compliant_today",
        help="True when wrist strap < 35 MΩ, worksurface < 1000 MΩ, and verified today",
    )
    calibration_expiry_date = fields.Date(
        string="Calibration Expiry",
        help="Calibration due date for bench multimeter, oscilloscope, and DC power supply",
    )
    calibration_cert_attachment_id = fields.Many2one(
        "ir.attachment",
        string="Bench Calibration & ESD Log Sheet",
    )
    equipment_specs = fields.Text(
        string="Station Equipment Specs",
        help="Installed tools (e.g., QUICK 861DW hot air, Hakko soldering station, Trinocular microscope)",
    )
    notes = fields.Text(string="Notes")
    active = fields.Boolean(default=True, tracking=True)

    _code_unique = models.Constraint(
        "UNIQUE (code)",
        "The bench code must be unique across all workshops.",
    )

    @api.depends(
        "is_esd_safe", "wrist_strap_mohm", "worksurface_rtg_mohm", "esd_last_verified_date"
    )
    def _compute_esd_compliant_today(self):
        today = fields.Date.today()
        for rec in self:
            rec.esd_compliant_today = bool(
                rec.is_esd_safe
                and 0.1 <= (rec.wrist_strap_mohm or 10.0) < 35.0
                and 0.1 <= (rec.worksurface_rtg_mohm or 100.0) < 1000.0
                and rec.esd_last_verified_date == today
            )

    def action_log_daily_esd(self, wrist_mohm=10.0, surface_mohm=100.0):
        """Record the daily pre-shift ESD wrist-strap and mat grounding check (FLAW-31.2)."""
        for rec in self:
            if wrist_mohm >= 35.0 or wrist_mohm <= 0.0:
                raise UserError(
                    f"FLAW-31.2 ESD Interlock: Wrist strap resistance ({wrist_mohm} MΩ) on bench {rec.code} "
                    f"exceeds ANSI/ESD S20.20 limit (< 35.0 MΩ)."
                )
            if surface_mohm >= 1000.0 or surface_mohm <= 0.0:
                raise UserError(
                    f"FLAW-31.2 ESD Interlock: Worksurface resistance ({surface_mohm} MΩ) on bench {rec.code} "
                    f"exceeds IEC 61340-5-1 limit (< 1000.0 MΩ)."
                )
            rec.write(
                {
                    "wrist_strap_mohm": wrist_mohm,
                    "worksurface_rtg_mohm": surface_mohm,
                    "esd_last_verified_date": fields.Date.today(),
                    "is_esd_safe": True,
                }
            )
        return True

    @api.depends("active_job_ids")
    def _compute_job_count(self):
        for rec in self:
            count = len(rec.active_job_ids)
            rec.current_job_count = count
            # Auto-update status if occupied or available (unless in maintenance/offline)
            if rec.state in ("available", "occupied"):
                if count >= rec.max_concurrent_jobs:
                    rec.state = "occupied"
                else:
                    rec.state = "available"

    def action_assign_job(self, job):
        """Assign a workshop job to this bench, validating capacity and routing level."""
        self.ensure_one()
        if self.state in ("maintenance", "offline"):
            raise UserError(
                f"Cannot assign job {job.name} to bench {self.code}: Bench is currently {self.state}."
            )
        if self.current_job_count >= self.max_concurrent_jobs:
            raise UserError(
                f"Bench {self.code} has reached its maximum concurrent job capacity ({self.max_concurrent_jobs})."
            )

        # Routing validation: bench must support the job's repair level
        level_order = {"l1": 1, "l2": 2, "l3": 3}
        if level_order.get(self.repair_level, 0) < level_order.get(job.repair_level, 0):
            raise UserError(
                f"Job {job.name} requires {job.repair_level.upper()} capability, but bench {self.code} is only {self.repair_level.upper()}."
            )

        job.write(
            {
                "bench_id": self.id,
                "technician_id": self.technician_id.id
                if self.technician_id
                else job.technician_id.id,
            }
        )
        self._compute_job_count()
        self._emit_bench_assigned(job)
        return True

    def action_release_job(self, job):
        """Release a job from this bench upon completion or transfer."""
        self.ensure_one()
        if job.bench_id.id == self.id:
            job.write({"bench_id": False})
        self._compute_job_count()
        return True

    def _emit_bench_assigned(self, job):
        """Emit workshop.bench.assigned event via outbox."""
        from libs.py.fix_events import publish

        publish(
            self.env,
            "workshop.bench.assigned",
            "fix.workshop.bench",
            self.id,
            {
                "bench_id": self.id,
                "bench_code": self.code,
                "workshop_id": self.workshop_id.id,
                "workshop_code": self.workshop_id.code,
                "job_id": job.id,
                "job_name": job.name,
                "repair_level": job.repair_level,
                "technician_id": self.technician_id.id if self.technician_id else False,
                "technician_name": self.technician_id.name if self.technician_id else "Unassigned",
            },
        )
