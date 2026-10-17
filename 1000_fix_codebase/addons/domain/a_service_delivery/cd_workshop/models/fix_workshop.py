# fix.workshop — Workshop & Depot Facility Master (CD-M31-02, RR-03 Milestone R03-M02).
from odoo import api, fields, models
from odoo.exceptions import ValidationError

import logging

logger = logging.getLogger(__name__)


class FixWorkshop(models.Model):
    """A physical workshop or depot repair facility operated by 1000FiX.

    Houses physical repair benches (L1/L2/L3), dedicated equipment, and technicians.
    """
    _name = "fix.workshop"
    _description = "Workshop & Depot Facility"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "code, name"

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

    # Identifiers & Bilingual naming (FF-25 / DoD-08)
    code = fields.Char(
        string="Workshop Code",
        required=True,
        index=True,
        tracking=True,
        help="Unique identifier (e.g., WS-TEJGAON-01, WS-CTG-01)",
    )
    name = fields.Char(
        string="Workshop Name",
        required=True,
        tracking=True,
    )
    name_bn = fields.Char(
        string="নাম (বাংলা)",
        required=True,
        help="Workshop name in Bengali script",
    )

    # Classification & Hierarchy
    workshop_type = fields.Selection(
        [
            ("central", "Central Depot (L1/L2/L3 Advanced Cleanroom)"),
            ("regional", "Regional Hub Workshop (L1/L2 Board Repair)"),
            ("express", "Express Branch Workshop (L1 Modular Quick-Fix)"),
        ],
        string="Facility Type",
        default="regional",
        required=True,
        tracking=True,
    )
    branch_id = fields.Many2one(
        "fix.branch",
        string="Associated Branch Hub",
        required=False,
        index=True,
        help="The physical branch hub this workshop belongs to",
    )
    manager_id = fields.Many2one(
        "hr.employee",
        string="Workshop Supervisor / Manager",
        tracking=True,
    )

    # Benches & Capacity
    bench_ids = fields.One2many(
        "fix.workshop.bench",
        "workshop_id",
        string="Repair Benches",
    )
    bench_count = fields.Integer(
        string="Total Benches",
        compute="_compute_bench_stats",
        store=True,
    )
    available_bench_count = fields.Integer(
        string="Available Benches",
        compute="_compute_bench_stats",
        store=True,
    )
    bench_utilization = fields.Float(
        string="Bench Utilization (%)",
        compute="_compute_bench_stats",
        store=True,
    )

    # Jobs
    job_ids = fields.One2many(
        "fix.workshop.job",
        "workshop_id",
        string="Workshop Jobs",
    )
    active_job_count = fields.Integer(
        string="Active WIP Jobs",
        compute="_compute_job_stats",
    )

    # Facility details
    street = fields.Char(string="Street Address")
    city = fields.Char(string="City", default="Dhaka")
    phone = fields.Char(string="Direct Phone")
    email = fields.Char(string="Workshop Email")
    is_esd_certified = fields.Boolean(
        string="ESD Protected Area (EPA)",
        default=True,
        help="ISO 9001 / IEC 61340-5-1 ESD protected area compliance",
    )
    notes = fields.Text(string="Operational Notes")
    active = fields.Boolean(default=True, tracking=True)

    # Odoo 19 Constraint specification
    _code_unique = models.Constraint(
        "UNIQUE (code)",
        "The workshop facility code must be unique across 1000FiX.",
    )

    @api.depends("bench_ids", "bench_ids.state")
    def _compute_bench_stats(self):
        for rec in self:
            total = len(rec.bench_ids)
            available = len(rec.bench_ids.filtered(lambda b: b.state == "available"))
            rec.bench_count = total
            rec.available_bench_count = available
            rec.bench_utilization = round(((total - available) / total * 100.0), 2) if total > 0 else 0.0

    def _compute_job_stats(self):
        for rec in self:
            rec.active_job_count = len(
                rec.job_ids.filtered(
                    lambda j: j.state not in ("delivered", "closed", "cancelled")
                )
            )
