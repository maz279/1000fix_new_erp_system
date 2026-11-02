# fix_competency — M22: certification register + FR-LMS-039 (P08-M05).
from odoo import api, fields, models
from odoo.exceptions import UserError

from libs.py.fix_events import publish

EXPIRING_WINDOW_DAYS = 30
TIER_RANK = {"l1": 1, "l2": 2, "l3": 3, "l4": 4}


class FixDeviceCategory(models.Model):
    """Structured Device Taxonomy for M22 Competency & Certification Matrix (RAP-M22-01)."""

    _name = "fix.device.category"
    _description = "Device Category Taxonomy"
    _order = "code, name"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    code = fields.Char(required=True, index=True)
    name = fields.Char(required=True)
    name_bn = fields.Char(string="Category Name (Bengali)")
    parent_id = fields.Many2one(
        "fix.device.category", string="Parent Category", ondelete="restrict"
    )
    repair_tier_floor = fields.Selection(
        [
            ("l1", "L1 - Modular Replacement"),
            ("l2", "L2 - Sub-Assembly Diagnostics"),
            ("l3", "L3 - Component / BGA Micro-Soldering"),
            ("l4", "L4 - Schematic & Firmware Engineering"),
        ],
        string="Minimum Repair Tier",
        default="l1",
    )
    active = fields.Boolean(default=True)


class FixCompetency(models.Model):
    _name = "fix.competency"
    _description = "Competency"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "code"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    code = fields.Char(required=True)
    name = fields.Char(required=True)
    name_bn = fields.Char(string="Competency (Bengali)", help="DE-17")
    device_type = fields.Char(
        string="Device Type Scope",
        help="e.g. smartphone, laptop, home_appliance — the dispatch "
        "eligibility match key (FR-LMS-039)",
    )
    device_category_id = fields.Many2one(
        "fix.device.category", string="Device Category", ondelete="set null"
    )
    brand_id = fields.Many2one("fix.brand", string="OEM Brand Scope", ondelete="set null")
    repair_tier = fields.Selection(
        [
            ("l1", "L1 - Modular Replacement"),
            ("l2", "L2 - Sub-Assembly Diagnostics"),
            ("l3", "L3 - Component / BGA Micro-Soldering"),
            ("l4", "L4 - Schematic & Firmware Engineering"),
        ],
        string="Minimum Repair Tier",
    )
    required_for_dispatch = fields.Boolean(
        default=True, help="Unchecked for developmental competencies that do not gate " "assignment"
    )

    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")


class FixCertification(models.Model):
    """The certification register with expiry tracking (P08-M05-T02)."""

    _name = "fix.certification"
    _description = "Certification"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "employee_id, expires_on"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    employee_id = fields.Many2one("hr.employee", required=True, index=True)
    competency_id = fields.Many2one("fix.competency", required=True, ondelete="restrict")
    brand_id = fields.Many2one("fix.brand", string="Certified OEM Brand", ondelete="set null")
    device_category_id = fields.Many2one(
        "fix.device.category", string="Device Category", ondelete="set null"
    )
    repair_tier = fields.Selection(
        [
            ("l1", "L1 - Modular Replacement"),
            ("l2", "L2 - Sub-Assembly Diagnostics"),
            ("l3", "L3 - Component / BGA Micro-Soldering"),
            ("l4", "L4 - Schematic & Firmware Engineering"),
        ],
        string="Certified Repair Tier",
    )
    certificate_file = fields.Binary(string="Certificate Scan", attachment=True)
    certificate_filename = fields.Char(string="Certificate Filename")
    issued_on = fields.Date(required=True, default=fields.Date.today)
    expires_on = fields.Date(help="Empty means non-expiring (e.g. internal licences)")
    evidence_ref = fields.Char(
        string="Evidence Reference", help="Pointer into M24 documents — the certificate artefact"
    )
    status = fields.Selection(
        [("active", "Active"), ("expiring", "Expiring Soon"), ("expired", "Expired")],
        compute="_compute_status",
        store=True,
    )

    @api.depends("expires_on")
    def _compute_status(self):
        today = fields.Date.today()
        for rec in self:
            if not rec.expires_on:
                rec.status = "active"
            elif rec.expires_on < today:
                rec.status = "expired"
            elif (rec.expires_on - today).days <= EXPIRING_WINDOW_DAYS:
                rec.status = "expiring"
            else:
                rec.status = "active"

    def action_grant(self):
        for rec in self:
            publish(
                self.env,
                "certification.granted",
                "fix.certification",
                rec.id,
                {"employee": rec.employee_id.name, "competency": rec.competency_id.code},
            )

    def action_mark_expired(self):
        """Manual sweep for certifications whose expiry passed in place.

        The stored status is computed from expires_on against the day it was
        last computed, so it goes stale as time passes: refresh it to TODAY
        first (otherwise the sweep never found the certifications it is for)."""
        self._compute_status()
        for rec in self:
            if rec.status == "expired":
                publish(
                    self.env,
                    "certification.expired",
                    "fix.certification",
                    rec.id,
                    {"employee": rec.employee_id.name, "competency": rec.competency_id.code},
                )

    @api.model
    def dispatch_eligibility(
        self,
        employee,
        device_type=None,
        brand_id=None,
        repair_tier=None,
        fail_closed=False,
    ):
        """FR-LMS-039 — the dispatch eligibility check (brand + device + tier aware).

        Returns (eligible: bool, reason: str). A technician is eligible for
        a device type, OEM brand, and repair tier when they hold an ACTIVE
        certification in a dispatch-gating competency whose scope matches.
        """
        if not employee:
            return False, "no technician assigned"
        today = fields.Date.today()
        certs = self.search(
            [
                ("employee_id", "=", employee.id),
                ("issued_on", "<=", today),
                "|",
                ("expires_on", "=", False),
                ("expires_on", ">=", today),
            ]
        )
        brand_id_int = (
            brand_id.id if hasattr(brand_id, "id") else (int(brand_id) if brand_id else None)
        )
        req_rank = TIER_RANK.get(repair_tier, 0) if repair_tier else 0

        valid_certs = self.browse()
        # Track WHY a certificate was filtered out. Reporting a tier shortfall
        # as a missing brand certification sends the operator after the wrong
        # certificate, which is worse than no reason at all.
        tier_blocked = self.browse()
        for cert in certs:
            c_brand = cert.brand_id.id or cert.competency_id.brand_id.id or None
            if brand_id_int and c_brand and c_brand != brand_id_int:
                continue
            c_tier = cert.repair_tier or cert.competency_id.repair_tier or None
            if req_rank and c_tier and TIER_RANK.get(c_tier, 0) < req_rank:
                tier_blocked |= cert
                continue
            valid_certs |= cert

        gating = self.env["fix.competency"].search([("required_for_dispatch", "=", True)])
        gating_by_id = {c.id: c for c in gating}
        held = set(valid_certs.competency_id.ids)

        if brand_id_int:
            brand_gating = [c for c in gating if c.brand_id.id == brand_id_int]
            if brand_gating and not any(
                (cert.brand_id.id == brand_id_int or cert.competency_id.brand_id.id == brand_id_int)
                for cert in valid_certs
            ):
                brand_rec = self.env["fix.brand"].browse(brand_id_int)
                tier_hit = tier_blocked.filtered(
                    lambda c: (c.brand_id.id or c.competency_id.brand_id.id) == brand_id_int
                )
                if tier_hit:
                    held_tier = tier_hit[0].repair_tier or tier_hit[0].competency_id.repair_tier
                    return False, (
                        "FR-LMS-039: %s is certified for %s at tier %s, below the %s "
                        "required by this job"
                        % (
                            employee.name,
                            brand_rec.name or brand_id_int,
                            (held_tier or "?").upper(),
                            (repair_tier or "?").upper(),
                        )
                    )
                return False, (
                    "FR-LMS-039: %s holds no ACTIVE brand certification for %s"
                    % (employee.name, brand_rec.name or brand_id_int)
                )

        if device_type:
            scoped = [
                c
                for c in gating
                if (c.device_type and device_type in [t.strip() for t in c.device_type.split(",")])
                or (c.device_category_id and c.device_category_id.code == device_type)
            ]
            if scoped:
                for comp in scoped:
                    if comp.id in held:
                        return True, "certified for %s" % device_type
                return False, (
                    "FR-LMS-039: %s holds no ACTIVE certification for %s"
                    % (employee.name, device_type)
                )
            if fail_closed:
                return False, (
                    "FR-LMS-039: no dispatch-gating competency configured for %s (fail-closed)"
                    % device_type
                )
        # No device scope demanded: at least one gating competency held
        if held & set(gating_by_id):
            return True, "holds dispatch-gating certification"
        if brand_id_int and certs and not valid_certs:
            brand_rec = self.env["fix.brand"].browse(brand_id_int)
            return False, (
                "FR-LMS-039: %s holds no ACTIVE certification for brand %s"
                % (employee.name, brand_rec.name or brand_id_int)
            )
        return False, ("FR-LMS-039: %s holds no dispatch-gating certification" % employee.name)

    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")


class FixTrainingCourse(models.Model):
    _name = "fix.training.course"
    _description = "Training Course"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "code"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    code = fields.Char(required=True)
    name = fields.Char(required=True)
    name_bn = fields.Char(string="Course (Bengali)", help="DE-17")
    content_ref = fields.Char(
        string="Content Pack",
        help="project_content 08 pack (the 24 TR-* files) — loaded content "
        "pointer; authoring degrades without M61 (accepted)",
    )
    competency_id = fields.Many2one("fix.competency", string="Certifies Towards")
    enrollment_ids = fields.One2many("fix.training.enrollment", "course_id", string="Enrollments")

    def action_enroll(self, employees):
        for rec in self:
            for emp in employees:
                self.env["fix.training.enrollment"].create(
                    {"course_id": rec.id, "employee_id": emp.id}
                )

    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")


class FixTrainingEnrollment(models.Model):
    _name = "fix.training.enrollment"
    _description = "Training Enrollment"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    course_id = fields.Many2one("fix.training.course", required=True, ondelete="cascade")
    employee_id = fields.Many2one("hr.employee", required=True)
    state = fields.Selection(
        [("enrolled", "Enrolled"), ("passed", "Passed"), ("failed", "Failed")],
        default="enrolled",
        required=True,
    )
    completed_on = fields.Date()

    def action_pass(self):
        for rec in self:
            rec.state = "passed"
            rec.completed_on = fields.Date.today()
            if rec.course_id.competency_id:
                self.env["fix.certification"].create(
                    {
                        "employee_id": rec.employee_id.id,
                        "competency_id": rec.course_id.competency_id.id,
                        "issued_on": fields.Date.today(),
                    }
                ).action_grant()
            publish(
                self.env,
                "training.passed",
                "fix.training.enrollment",
                rec.id,
                {"employee": rec.employee_id.name, "course": rec.course_id.code},
            )

    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")


class FixWorkOrderEligibilityExt(models.Model):
    """P08-M05-T04/T05: the M02 -> M22 AND M31 -> M22 stubs CLOSED —
    certification eligibility is now a BLOCKING check on the live
    assignment path (both field service and workshop share
    fix.work.order)."""

    _inherit = "fix.work.order"

    certification_waiver = fields.Boolean(
        string="Certification Waiver",
        help="Emergency supervisor override for dispatch when certified staff are unavailable (audited)",
    )
    certification_waiver_reason = fields.Char(string="Waiver Justification")
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")

    def action_check_certification(self):
        # Every record is checked (the loop used to `return True` after the
        # first one, waving the rest of a multi-record call through).
        for rec in self:
            if not rec.technician_id or rec.certification_waiver:
                continue
            # order_id is required on fix.work.order, so the device is reachable
            device_type = rec.order_id.device_id.device_type or None
            brand = (
                rec.order_id.device_id.device_model_id.brand_id
                if rec.order_id.device_id and rec.order_id.device_id.device_model_id
                else None
            )
            eligible, reason = self.env["fix.certification"].dispatch_eligibility(
                rec.technician_id, device_type=device_type, brand_id=brand
            )
            if not eligible:
                raise UserError("M22 eligibility: assignment blocked — %s" % reason)
        return True

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            if rec.technician_id:
                rec.action_check_certification()
        return records

    def write(self, vals):
        result = super().write(vals)
        if vals.get("technician_id"):
            for rec in self:
                rec.action_check_certification()
        return result
