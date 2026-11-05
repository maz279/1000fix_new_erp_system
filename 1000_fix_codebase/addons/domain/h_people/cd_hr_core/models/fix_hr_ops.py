# fix_hr_ops — M21: HR lifecycle documents and movement behind the 12 registry
# screens. Org positions and employment contracts live in fix_hr_core.py.
from odoo import api, fields, models
from odoo.exceptions import UserError

from libs.py.fix_events import publish


class FixHrTransfer(models.Model):
    """Transfer, promotion or demotion — the movement history's source."""

    _name = "fix.hr.transfer"
    _description = "HR Movement (Transfer / Promotion)"
    _order = "effective_date desc, id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    employee_id = fields.Many2one("hr.employee", required=True, ondelete="cascade", index=True)
    movement_type = fields.Selection(
        [("transfer", "Transfer"), ("promotion", "Promotion"), ("demotion", "Demotion")],
        required=True,
        default="transfer",
    )
    movement_category = fields.Selection(
        [
            ("branch_transfer", "Inter-Branch Transfer"),
            ("dept_transfer", "Departmental Transfer"),
            ("technical_promotion", "Technical Skill Promotion"),
            ("corporate_promotion", "Corporate / Management Promotion"),
            ("deputation", "Temporary Deputation"),
            ("demotion", "Role Realignment / Demotion"),
        ],
        string="Movement Category",
        default="branch_transfer",
    )
    movement_nature = fields.Selection(
        [
            ("permanent", "Permanent"),
            ("temporary_deputation", "Temporary Deputation"),
            ("probationary_promotion", "Promotion on Probation"),
        ],
        string="Movement Nature",
        default="permanent",
    )
    deputation_months = fields.Integer(string="Deputation Duration (Months)")
    initiator_user_id = fields.Many2one(
        "res.users", string="Requisition Initiated By", default=lambda self: self.env.user
    )
    requisition_date = fields.Date(string="Requisition Date", default=fields.Date.context_today)
    release_date = fields.Date(string="Proposed Release Date")
    effective_date = fields.Date(required=True, default=fields.Date.context_today)
    reason = fields.Text(string="Business Justification")
    state = fields.Selection(
        [
            ("draft", "Draft Requisition"),
            ("recommended", "Recommended"),
            ("concurred", "Destination Concurred"),
            ("tech_evaluated", "Technical Evaluated"),
            ("hr_audited", "HR Compliance Audited"),
            ("finance_approved", "Finance Cleared"),
            ("approved", "Executive Approved"),
            ("handover_cleared", "Handover Cleared"),
            ("applied", "Applied to Master"),
            ("cancelled", "Cancelled"),
            ("rejected", "Rejected"),
        ],
        required=True,
        default="draft",
    )

    # -------------------------------------------------------------------------
    # TAB 2: Org Realignment (Position, Grade & Reporting)
    # -------------------------------------------------------------------------
    from_operating_unit_id = fields.Many2one("operating.unit", string="Current Branch / Hub")
    to_operating_unit_id = fields.Many2one(
        "operating.unit", string="Destination Branch / Hub", ondelete="restrict"
    )
    from_department_id = fields.Many2one("hr.department", string="Current Department")
    to_department_id = fields.Many2one("hr.department", string="Destination Department")
    from_position_id = fields.Many2one("fix.org.position", string="Current Position")
    to_position_id = fields.Many2one(
        "fix.org.position", string="Destination Position", ondelete="restrict"
    )
    from_job_title = fields.Char(string="Current Job Title")
    to_job_title = fields.Char(string="Destination Job Title")
    from_grade_band = fields.Selection(
        [
            ("L1", "Level 1 - Junior Technician / Apprentice"),
            ("L2", "Level 2 - Technician / Associate Specialist"),
            ("L3", "Level 3 - Senior Technician / Lead Specialist"),
            ("L4", "Level 4 - Master Technician / Engineering Lead"),
            ("M1", "Management 1 - Assistant Branch Manager / Team Lead"),
            ("M2", "Management 2 - Branch Manager / Senior Manager"),
            ("EX", "Executive - Head of Department / Director"),
        ],
        string="Current Corporate Grade Band",
    )
    to_grade_band = fields.Selection(
        [
            ("L1", "Level 1 - Junior Technician / Apprentice"),
            ("L2", "Level 2 - Technician / Associate Specialist"),
            ("L3", "Level 3 - Senior Technician / Lead Specialist"),
            ("L4", "Level 4 - Master Technician / Engineering Lead"),
            ("M1", "Management 1 - Assistant Branch Manager / Team Lead"),
            ("M2", "Management 2 - Branch Manager / Senior Manager"),
            ("EX", "Executive - Head of Department / Director"),
        ],
        string="Destination Corporate Grade Band",
    )
    from_manager_id = fields.Many2one("hr.employee", string="Current Reporting Manager")
    to_manager_id = fields.Many2one("hr.employee", string="Destination Reporting Manager")

    # -------------------------------------------------------------------------
    # TAB 3: Compensation & Payroll Restructuring
    # -------------------------------------------------------------------------
    current_basic = fields.Float(string="Current Basic Salary")
    proposed_basic = fields.Float(string="Proposed Basic Salary")
    basic_increment_pct = fields.Float(string="Basic Salary Increment Percentage")
    current_gross = fields.Float(string="Current Monthly Gross Salary")
    proposed_gross = fields.Float(string="Proposed Monthly Gross Salary")
    proposed_house_rent = fields.Float(string="Proposed House Rent Allowance")
    proposed_medical = fields.Float(string="Proposed Medical Allowance")
    proposed_conveyance = fields.Float(string="Proposed Conveyance Allowance")
    proposed_skill_allowance = fields.Float(string="Proposed Technical Skill Allowance")
    deputation_allowance = fields.Float(string="Deputation Allowance")
    to_tax_location = fields.Selection(
        [
            ("dhaka_chittagong", "Dhaka / Chittagong City Corporation (Min BDT 5,000)"),
            ("other_city_corporation", "Other City Corporation (Min BDT 4,000)"),
            ("non_city_corporation", "Non-City Corporation / District / Upazila (Min BDT 3,000)"),
        ],
        string="Destination Tax Jurisdiction",
        default="dhaka_chittagong",
    )
    effective_payroll_month = fields.Char(string="Effective Payroll Month (YYYY-MM)")

    # -------------------------------------------------------------------------
    # TAB 4: Technical Competency & OEM Badges
    # -------------------------------------------------------------------------
    from_repair_tier = fields.Selection(
        [
            ("tier1_basic", "Tier 1 - Basic Assembly & Modular Replacement"),
            ("tier2_component", "Tier 2 - Component Level & SMD Soldering"),
            ("tier3_board", "Tier 3 - Multi-layer Logic Board Diagnosis"),
            ("tier4_bga_micro", "Tier 4 - Advanced BGA Rework & Micro-soldering"),
        ],
        string="Current Repair Tier",
    )
    to_repair_tier = fields.Selection(
        [
            ("tier1_basic", "Tier 1 - Basic Assembly & Modular Replacement"),
            ("tier2_component", "Tier 2 - Component Level & SMD Soldering"),
            ("tier3_board", "Tier 3 - Multi-layer Logic Board Diagnosis"),
            ("tier4_bga_micro", "Tier 4 - Advanced BGA Rework & Micro-soldering"),
        ],
        string="Assigned Technical Repair Tier",
    )
    oem_brand_authorizations = fields.Char(
        string="OEM Brand Authorizations (Apple, Samsung, Dell, HP)"
    )
    target_workbench_id = fields.Char(string="Destination Workbench Station ID")
    esd_certified = fields.Boolean(string="ESD Safety Certified & Calibrated")
    bga_license = fields.Boolean(string="BGA Rework Machine Operator License")
    target_dispatch_zone = fields.Char(string="GPS Field Dispatch Zone / Radius")
    technical_assessment_score = fields.Float(string="Technical Board Assessment Score (0-100)")
    technical_evaluator_id = fields.Many2one(
        "hr.employee", string="Technical Evaluator / Lead Architect"
    )
    nda_confirmed = fields.Boolean(string="Customer Data Privacy Undertaking Confirmed")

    # -------------------------------------------------------------------------
    # TAB 5: Operational Handover & Asset Custody Clearance
    # -------------------------------------------------------------------------
    open_jobs_audited = fields.Boolean(string="Open Customer Service Orders Audited")
    open_jobs_transferred_count = fields.Integer(string="Open RMA / Job Cards Transferred Count")
    open_jobs_reassignment_ref = fields.Char(string="Open Jobs Reassignment Docket Ref")
    toolkit_custody_ref = fields.Char(string="Tool Kit Custody Inventory Tag Ref")
    toolkit_returned = fields.Boolean(string="Micro-soldering Tool Kit Returned / Handed Over")
    toolkit_challan_no = fields.Char(string="Tool Kit Return Challan Number")
    spare_parts_reconciled = fields.Boolean(string="Transit Spare Parts Reconciled")
    spare_parts_variance_value = fields.Float(string="Transit Spare Parts Discrepancy Value")
    clearance_mrn_no = fields.Char(string="Material Return Note (MRN) Number")
    storekeeper_cleared = fields.Boolean(string="Branch Storekeeper Clearance Signed")
    storekeeper_id = fields.Many2one("hr.employee", string="Origin Branch Storekeeper")
    imprest_cash_settled = fields.Boolean(string="Branch Imprest Cash / Float Fully Settled")

    # -------------------------------------------------------------------------
    # TAB 6: Relocation Logistics & Transit Leave
    # -------------------------------------------------------------------------
    transfer_grant = fields.Float(string="Transfer Grant / Disturbance Allowance")
    luggage_allowance = fields.Float(string="Luggage & Packing Transport Allowance")
    travel_allowance = fields.Float(string="Travel Allowance TA/DA")
    transit_leave_days = fields.Integer(string="Paid Transit Leave Days (BLA Rule 22)", default=3)
    transit_start_date = fields.Date(string="Transit Leave Start Date")
    transit_end_date = fields.Date(string="Transit Leave End Date")
    shifting_vendor = fields.Char(string="Household Goods Moving Vendor Name")
    temporary_stay_provided = fields.Boolean(string="Company Transit Accommodation Provided")
    destination_joining_date = fields.Date(string="Actual Station Joining Date")

    # -------------------------------------------------------------------------
    # TAB 7: Authorization Workflow & Digital Signoff
    # -------------------------------------------------------------------------
    origin_manager_approval = fields.Selection(
        [("pending", "Pending"), ("approved", "Recommended"), ("rejected", "Rejected")],
        default="pending",
    )
    origin_manager_id = fields.Many2one("hr.employee", string="Origin Recommending Manager")
    origin_manager_date = fields.Date(string="Origin Manager Recommendation Date")
    destination_manager_approval = fields.Selection(
        [("pending", "Pending"), ("approved", "Concurred"), ("rejected", "Refused")],
        default="pending",
    )
    destination_manager_id = fields.Many2one("hr.employee", string="Destination Receiving Manager")
    destination_manager_date = fields.Date(string="Destination Manager Concurrence Date")
    tech_head_approval = fields.Selection(
        [("pending", "Pending"), ("approved", "Approved"), ("rejected", "Rejected")],
        default="pending",
    )
    tech_head_id = fields.Many2one("hr.employee", string="Technical Evaluation Head")
    tech_head_date = fields.Date(string="Technical Signoff Date")
    hr_head_approval = fields.Selection(
        [("pending", "Pending"), ("approved", "Audited & Verified"), ("rejected", "Rejected")],
        default="pending",
    )
    hr_head_id = fields.Many2one("hr.employee", string="HR Operations Lead")
    hr_head_date = fields.Date(string="HR Audit Date")
    finance_head_approval = fields.Selection(
        [("pending", "Pending"), ("approved", "Cleared"), ("rejected", "Rejected")],
        default="pending",
    )
    finance_head_id = fields.Many2one("hr.employee", string="Financial Controller")
    finance_head_date = fields.Date(string="Finance Clearance Date")
    executive_approval = fields.Selection(
        [("pending", "Pending"), ("approved", "Approved"), ("rejected", "Rejected")],
        default="pending",
    )
    executive_id = fields.Many2one("hr.employee", string="Managing Director / Executive Head")
    executive_date = fields.Date(string="Executive Signoff Date")
    rejection_reason = fields.Text(string="Rejection or Audit Discrepancy Remarks")

    # -------------------------------------------------------------------------
    # TAB 8: Movement Documentation & Scanned Evidence Vault
    # -------------------------------------------------------------------------
    transfer_letter_file = fields.Binary(
        string="Official Transfer / Promotion Order Scan", attachment=True
    )
    transfer_letter_filename = fields.Char(string="Transfer Order Filename")
    handover_challan_file = fields.Binary(
        string="Tool Kit Custody Return & Verification Challan", attachment=True
    )
    handover_challan_filename = fields.Char(string="Handover Challan Filename")
    clearance_mrn_file = fields.Binary(
        string="Spare Parts & Inventory Clearance MRN Scan", attachment=True
    )
    clearance_mrn_filename = fields.Char(string="Clearance MRN Filename")
    joining_report_file = fields.Binary(string="Station Joining Report Scan", attachment=True)
    joining_report_filename = fields.Char(string="Joining Report Filename")
    service_book_endorsement_file = fields.Binary(
        string="Form 7 Service Book Endorsement Scan", attachment=True
    )
    service_book_endorsement_filename = fields.Char(string="Service Book Filename")
    contract_addendum_file = fields.Binary(string="Amended Contract Addendum Scan", attachment=True)
    contract_addendum_filename = fields.Char(string="Contract Addendum Filename")
    open_jobs_docket_file = fields.Binary(
        string="Open Job Card Reassignment Docket Scan", attachment=True
    )
    open_jobs_docket_filename = fields.Char(string="Open Jobs Docket Filename")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                prefix = "PRM" if vals.get("movement_type") == "promotion" else "TRF"
                seq = self.env["ir.sequence"].next_by_code("fix.hr.transfer") or "HMV/New"
                vals["name"] = seq.replace("HMV", prefix) if "HMV" in seq else seq
        return super().create(vals_list)

    def _check_custody_gate(self):
        self.ensure_one()
        missing = []
        for flag_name, label in (
            ("open_jobs_audited", "Open Customer Service Orders Audited"),
            ("toolkit_returned", "Micro-soldering Tool Kit Returned"),
            ("spare_parts_reconciled", "Transit Spare Parts Reconciled"),
            ("storekeeper_cleared", "Branch Storekeeper Clearance Signed"),
            ("imprest_cash_settled", "Branch Imprest Cash / Float Settled"),
        ):
            if not getattr(self, flag_name, False):
                missing.append(label)
        if missing:
            raise UserError(
                "Custody & Handover Clearance Incomplete. Missing checks: %s" % ", ".join(missing)
            )
        if not (
            self.handover_challan_file
            or self.clearance_mrn_file
            or self.toolkit_challan_no
            or self.clearance_mrn_no
        ):
            raise UserError(
                "Custody evidence required: attach Handover Challan or Clearance MRN scan/reference before clearing handover."
            )

    def action_recommend(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only a draft movement requisition can be recommended.")
            emp = self.env.user.employee_id
            rec.write(
                {
                    "state": "recommended",
                    "origin_manager_approval": "approved",
                    "origin_manager_id": rec.origin_manager_id.id or (emp.id if emp else False),
                    "origin_manager_date": fields.Date.context_today(self),
                }
            )

    def action_concur(self):
        for rec in self:
            if rec.state != "recommended":
                raise UserError(
                    "Movement must be recommended by Origin Manager before Destination Concurrence."
                )
            emp = self.env.user.employee_id
            rec.write(
                {
                    "state": "concurred",
                    "destination_manager_approval": "approved",
                    "destination_manager_id": rec.destination_manager_id.id
                    or (emp.id if emp else False),
                    "destination_manager_date": fields.Date.context_today(self),
                }
            )

    def action_tech_eval(self):
        for rec in self:
            if rec.state not in ("recommended", "concurred"):
                raise UserError(
                    "Movement must be recommended or concurred before Technical Evaluation."
                )
            emp = self.env.user.employee_id
            rec.write(
                {
                    "state": "tech_evaluated",
                    "tech_head_approval": "approved",
                    "tech_head_id": rec.tech_head_id.id or (emp.id if emp else False),
                    "tech_head_date": fields.Date.context_today(self),
                }
            )

    def action_hr_audit(self):
        for rec in self:
            if rec.state not in ("concurred", "tech_evaluated"):
                raise UserError(
                    "Movement must pass Destination Concurrence or Technical Evaluation before HR Audit."
                )
            emp = self.env.user.employee_id
            rec.write(
                {
                    "state": "hr_audited",
                    "hr_head_approval": "approved",
                    "hr_head_id": rec.hr_head_id.id or (emp.id if emp else False),
                    "hr_head_date": fields.Date.context_today(self),
                }
            )

    def action_finance_approve(self):
        for rec in self:
            if rec.state != "hr_audited":
                raise UserError("Movement must pass HR Compliance Audit before Finance Clearance.")
            emp = self.env.user.employee_id
            rec.write(
                {
                    "state": "finance_approved",
                    "finance_head_approval": "approved",
                    "finance_head_id": rec.finance_head_id.id or (emp.id if emp else False),
                    "finance_head_date": fields.Date.context_today(self),
                }
            )

    def action_approve(self):
        for rec in self:
            if rec.state not in ("finance_approved", "hr_audited"):
                raise UserError(
                    "Movement must be Finance Cleared (or HR Audited) before Executive Approval."
                )
            emp = self.env.user.employee_id
            rec.write(
                {
                    "state": "approved",
                    "executive_approval": "approved",
                    "executive_id": rec.executive_id.id or (emp.id if emp else False),
                    "executive_date": fields.Date.context_today(self),
                }
            )

    def action_clear_handover(self):
        for rec in self:
            if rec.state != "approved":
                raise UserError(
                    "Movement must be Executive Approved before clearing handover custody."
                )
            rec._check_custody_gate()
            rec.write(
                {
                    "state": "handover_cleared",
                }
            )

    def action_apply(self):
        for rec in self:
            if rec.state != "handover_cleared":
                if rec.state == "approved":
                    rec._check_custody_gate()
                else:
                    raise UserError(
                        "Movement must be approved and handover cleared before applying to employee master."
                    )
            vals = {"form7_last_event_date": rec.effective_date or fields.Date.context_today(self)}
            if rec.to_position_id:
                vals["position_id"] = rec.to_position_id.id
            if rec.to_operating_unit_id:
                vals["operating_unit_id"] = rec.to_operating_unit_id.id
            if rec.to_department_id:
                vals["department_id"] = rec.to_department_id.id
            if rec.to_job_title:
                vals["job_title"] = rec.to_job_title
            if rec.to_grade_band:
                band_map = {
                    "L1": "band_2",
                    "L2": "band_3",
                    "L3": "band_4",
                    "L4": "band_5",
                    "M1": "band_6",
                    "M2": "band_6",
                    "EX": "band_8",
                    "band_1": "band_1",
                    "band_2": "band_2",
                    "band_3": "band_3",
                    "band_4": "band_4",
                    "band_5": "band_5",
                    "band_6": "band_6",
                    "band_7": "band_7",
                    "band_8": "band_8",
                }
                vals["job_band"] = band_map.get(rec.to_grade_band, rec.to_grade_band)
            if rec.to_repair_tier:
                tier_map = {
                    "tier1_basic": "l1_modular",
                    "tier2_component": "l2_subassembly",
                    "tier3_board": "l3_component",
                    "tier4_bga_micro": "l4_schematic",
                    "l1_modular": "l1_modular",
                    "l2_subassembly": "l2_subassembly",
                    "l3_component": "l3_component",
                    "l4_schematic": "l4_schematic",
                }
                vals["repair_tier"] = tier_map.get(rec.to_repair_tier, rec.to_repair_tier)
            if rec.proposed_gross:
                vals["wage"] = rec.proposed_gross
            if rec.proposed_basic:
                vals["basic_wage"] = rec.proposed_basic
            if rec.proposed_house_rent:
                vals["house_rent"] = rec.proposed_house_rent
            if rec.proposed_medical:
                vals["medical_allowance"] = rec.proposed_medical
            if rec.proposed_conveyance:
                vals["conveyance_allowance"] = rec.proposed_conveyance
            if rec.proposed_skill_allowance:
                vals["technical_allowance"] = rec.proposed_skill_allowance
            if rec.to_tax_location:
                tax_map = {
                    "dhaka_chittagong": "dhaka_chattogram",
                    "dhaka_chattogram": "dhaka_chattogram",
                    "other_city_corporation": "other_city_corporation",
                    "non_city_corporation": "non_city_corporation",
                }
                vals["minimum_tax_location"] = tax_map.get(rec.to_tax_location, rec.to_tax_location)
            if vals:
                rec.employee_id.write(vals)
            # Also sync active employment contract if compensation changed (RAP-M21-04)
            if (
                rec.proposed_basic
                or rec.proposed_house_rent
                or rec.proposed_medical
                or rec.proposed_conveyance
                or rec.proposed_skill_allowance
            ):
                active_contract = self.env["fix.employment.contract"].search(
                    [("employee_id", "=", rec.employee_id.id), ("state", "=", "active")],
                    order="joining_date desc, id desc",
                    limit=1,
                )
                if active_contract:
                    c_vals = {}
                    if rec.proposed_basic:
                        c_vals["basic_monthly"] = rec.proposed_basic
                    if rec.proposed_house_rent:
                        c_vals["house_rent"] = rec.proposed_house_rent
                    if rec.proposed_medical:
                        c_vals["medical_allowance"] = rec.proposed_medical
                    if rec.proposed_conveyance:
                        c_vals["conveyance_allowance"] = rec.proposed_conveyance
                    if rec.proposed_skill_allowance:
                        c_vals["technical_allowance"] = rec.proposed_skill_allowance
                    if c_vals:
                        active_contract.write(c_vals)
            rec.write({"state": "applied"})
            publish(
                self.env,
                "employee.moved",
                "fix.hr.transfer",
                rec.id,
                {
                    "employee_id": rec.employee_id.id,
                    "employee_code": rec.employee_id.employee_code or "",
                    "department": (
                        rec.to_department_id.name or rec.employee_id.department_id.name or ""
                    ),
                    "from_branch": rec.from_operating_unit_id.name or "",
                    "to_branch": rec.to_operating_unit_id.name or "",
                    "from_position": rec.from_position_id.name or "",
                    "to_position": rec.to_position_id.name or "",
                    "from_tier": rec.from_repair_tier or "",
                    "to_tier": rec.to_repair_tier or "",
                    "effective_date": str(rec.effective_date or ""),
                    "movement_type": rec.movement_type,
                },
            )

    def action_cancel(self):
        for rec in self:
            rec.state = "cancelled"

    def action_reset_draft(self):
        for rec in self:
            rec.state = "draft"


class FixHrExit(models.Model):
    """Exit clearance and settlement (Labour Act separation)."""

    _name = "fix.hr.exit"
    _description = "Employee Exit & Settlement"
    _order = "last_working_day desc, id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    employee_id = fields.Many2one("hr.employee", required=True, ondelete="cascade", index=True)
    exit_type = fields.Selection(
        [
            ("resignation", "Resignation"),
            ("termination", "Termination"),
            ("retirement", "Retirement"),
            ("contract_end", "Contract End"),
            ("abandonment", "Abandonment"),
        ],
        required=True,
        default="resignation",
    )
    notice_date = fields.Date()
    last_working_day = fields.Date(required=True, default=fields.Date.context_today)
    reason = fields.Text()
    # clearance checklist
    clearance_it = fields.Boolean(string="IT / Devices Returned")
    clearance_finance = fields.Boolean(string="Finance Dues Cleared")
    clearance_hr = fields.Boolean(string="HR Files Handed Over")
    clearance_assets = fields.Boolean(string="Company Assets Returned")
    asset_return_receipt_no = fields.Char(string="Asset Return Receipt / Challan No")
    asset_return_receipt_file = fields.Binary(string="Asset Return Receipt Scan", attachment=True)
    asset_return_receipt_filename = fields.Char(string="Asset Return Receipt Filename")
    settlement_amount = fields.Monetary(currency_field="currency_id", string="Final Settlement")
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("cleared", "Cleared"),
            ("settled", "Settled"),
            ("cancelled", "Cancelled"),
        ],
        required=True,
        default="draft",
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.hr.exit") or "HEX/New"
        return super().create(vals_list)

    def _all_cleared(self):
        return (
            self.clearance_it
            and self.clearance_finance
            and self.clearance_hr
            and self.clearance_assets
        )

    def action_clear(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError("Clear a draft exit")
            if not rec._all_cleared():
                raise UserError("Every clearance line must be ticked before clearing")
            if rec.employee_id.toolkit_custody_ref and not (
                rec.asset_return_receipt_no or rec.asset_return_receipt_file
            ):
                raise UserError(
                    "Employee holds assigned toolkit custody (%s): Asset Return Receipt reference or scan is required before clearing exit."
                    % rec.employee_id.toolkit_custody_ref
                )
            rec.employee_id.write(
                {"form7_last_event_date": rec.last_working_day or fields.Date.context_today(self)}
            )
            rec.state = "cleared"

    def action_settle(self):
        for rec in self:
            if rec.state != "cleared":
                raise UserError("Settle a cleared exit")
            rec.state = "settled"

    def action_cancel(self):
        for rec in self:
            rec.state = "cancelled"


class FixHrDocument(models.Model):
    """Statutory HR document: appointment letter, ID card, service book, certifications."""

    _name = "fix.hr.document"
    _description = "Employee Statutory Document"
    _order = "doc_type, employee_id"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    employee_id = fields.Many2one("hr.employee", required=True, ondelete="cascade", index=True)
    doc_type = fields.Selection(
        [
            ("appointment", "Appointment Letter"),
            ("id_card", "Employee ID Card (Form 11)"),
            ("service_book", "Form 7 Service Book"),
            ("experience", "Experience Certificate"),
            ("nda", "Confidentiality Undertaking (NDA)"),
            ("nid_smart", "National ID (Smart Card)"),
            ("birth_cert", "Birth Registration Certificate"),
            ("tin_cert", "12-digit e-TIN Certificate"),
            ("tax_psr", "Tax Return Submission Ack (PSR)"),
            ("passport", "International Passport"),
            ("driving_lic", "BRTA Driving License"),
            ("joining_report", "Formal Joining Report"),
            ("code_conduct", "Code of Conduct & Ethics"),
            ("ssc_cert", "SSC / Dakhil Certificate"),
            ("diploma_cert", "Polytechnic Diploma Certificate"),
            ("degree_cert", "University Degree Certificate"),
            ("oem_cert", "OEM Brand Accreditation"),
            ("vocational", "Technical Trade Certificate (NTVQ)"),
            ("payslip_prior", "Prior Employer Payslips"),
            ("police_pcc", "Police Clearance Certificate (PCC)"),
            ("ref_check", "Reference Check Summary"),
            ("medical_fit", "Medical Fitness Certificate"),
            ("blood_report", "Blood Group Lab Report"),
            ("vaccination", "Tetanus / Vaccination Card"),
            ("bank_cheque", "Void Bank Cheque Leaf"),
            ("nominee_nid", "Nominee NID & Photo"),
        ],
        required=True,
        default="appointment",
    )
    reference = fields.Char(string="Document Ref")
    issued_on = fields.Date(default=fields.Date.context_today)
    expiry_date = fields.Date(string="Document Expiry Date")
    verified = fields.Boolean(string="Verified by HR", default=True)
    acknowledged = fields.Boolean(string="Acknowledged by Employee")
    notes = fields.Char()
    file_data = fields.Binary(string="Physical Scanned Document", attachment=True)
    file_name = fields.Char(string="File Name")
    file_size = fields.Integer(string="File Size (Bytes)")
    file_mimetype = fields.Char(string="File MIME Type")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.hr.document") or "HDOC/New"
        return super().create(vals_list)


class FixHrDependant(models.Model):
    """Dependant & nominee register."""

    _name = "fix.hr.dependant"
    _description = "Employee Dependant / Nominee"
    _order = "employee_id, name"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    employee_id = fields.Many2one("hr.employee", required=True, ondelete="cascade", index=True)
    name = fields.Char(required=True)
    relation = fields.Selection(
        [
            ("spouse", "Spouse"),
            ("child", "Child"),
            ("parent", "Parent"),
            ("sibling", "Sibling"),
            ("other", "Other"),
        ],
        required=True,
        default="spouse",
    )
    date_of_birth = fields.Date()
    # nid: held in the Bangladesh-resident store (fix_hr_identity_residency.py)
    is_nominee = fields.Boolean(string="Nominee")
    nominee_pct = fields.Float(string="Nominee Share %")
    guardian_name = fields.Char(string="Legal Guardian Name (if Minor)")

    _pct_range = models.Constraint(
        "CHECK (nominee_pct >= 0 AND nominee_pct <= 100)", "Nominee share is a 0-100 percentage"
    )


class FixHrEducation(models.Model):
    """Employee Academic Qualifications Master Register."""

    _name = "fix.hr.education"
    _description = "Employee Academic Qualification"
    _order = "passing_year desc, employee_id"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    employee_id = fields.Many2one("hr.employee", required=True, ondelete="cascade", index=True)
    degree_level = fields.Selection(
        [
            ("ssc", "SSC / Dakhil / O-Level"),
            ("hsc", "HSC / Alim / A-Level"),
            ("diploma_engineering", "Diploma in Engineering (BTEB)"),
            ("bachelors", "Bachelor Degree / B.Sc Eng"),
            ("masters", "Master Degree / M.Sc / MBA"),
            ("doctorate", "Doctorate / Ph.D"),
            ("vocational_ntvq", "Vocational Trade (NTVQ)"),
        ],
        string="Education Level",
        required=True,
        default="diploma_engineering",
    )
    degree_title = fields.Char(string="Degree Title", required=True)
    major_group = fields.Char(string="Field / Major", required=True)
    board_university = fields.Char(string="Board / University", required=True)
    institute_name = fields.Char(string="School / College / Institute")
    passing_year = fields.Integer(string="Passing Year", required=True)
    duration_years = fields.Float(string="Duration (Years)", default=4.0)
    result_type = fields.Selection(
        [
            ("gpa_5", "GPA out of 5.0"),
            ("cgpa_4", "CGPA out of 4.0"),
            ("first_class", "First Class"),
            ("second_class", "Second Class"),
            ("division", "Division"),
        ],
        string="Grading System",
        default="cgpa_4",
    )
    gpa_score = fields.Float(string="GPA / Marks", required=True)
    roll_number = fields.Char(string="Roll Number")
    registration_no = fields.Char(string="Registration Number")
    is_verified = fields.Selection(
        [
            ("verified_online", "Verified Online"),
            ("verified_physical", "Verified Physical Certificate"),
            ("pending", "Verification Pending"),
            ("discrepancy", "Discrepancy Flagged"),
        ],
        string="Verification Status",
        default="verified_online",
    )
    certificate_file = fields.Binary(string="Academic Certificate Scan", attachment=True)
    certificate_filename = fields.Char(string="Certificate Filename")


class FixHrExperience(models.Model):
    """Employee Prior Professional Experience Register."""

    _name = "fix.hr.experience"
    _description = "Employee Work Experience"
    _order = "end_date desc, employee_id"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    employee_id = fields.Many2one("hr.employee", required=True, ondelete="cascade", index=True)
    company_name = fields.Char(string="Previous Employer", required=True)
    industry_type = fields.Selection(
        [
            ("after_sales_service", "After-Sales Repair & Warranty"),
            ("telecom", "Telecommunications"),
            ("it_hardware", "IT Hardware & Server Infrastructure"),
            ("consumer_electronics", "Consumer Electronics & TV"),
            ("hvac_appliances", "HVAC & Home Appliances"),
            ("corporate", "General Corporate"),
        ],
        string="Industry Sector",
        default="after_sales_service",
    )
    designation_held = fields.Char(string="Designation Held", required=True)
    start_date = fields.Date(string="Start Date", required=True)
    end_date = fields.Date(string="End Date", required=True)
    experience_years = fields.Float(
        string="Total Duration (Years)", compute="_compute_experience_years", store=True
    )
    last_drawn_salary = fields.Float(string="Last Drawn Salary (BDT)")
    reason_for_leaving = fields.Selection(
        [
            ("career_growth", "Career Growth"),
            ("relocation", "Relocation"),
            ("higher_studies", "Higher Studies"),
            ("compensation", "Compensation"),
            ("end_of_contract", "End of Contract"),
            ("mutual", "Mutual Separation"),
        ],
        string="Separation Reason",
        default="career_growth",
    )
    supervisor_name = fields.Char(string="Supervisor Name")
    supervisor_phone = fields.Char(string="Supervisor Mobile")
    reference_status = fields.Selection(
        [
            ("verified_positive", "Verified Positive"),
            ("verified_neutral", "Verified Neutral"),
            ("negative_flag", "Negative Flag"),
            ("unreachable", "Unreachable"),
        ],
        string="Reference Check",
        default="verified_positive",
    )
    experience_letter_file = fields.Binary(
        string="Experience / Release Letter Scan", attachment=True
    )
    experience_letter_filename = fields.Char(string="Experience Letter Filename")

    @api.depends("start_date", "end_date")
    def _compute_experience_years(self):
        for rec in self:
            if rec.start_date and rec.end_date and rec.end_date >= rec.start_date:
                days = (rec.end_date - rec.start_date).days
                rec.experience_years = round(days / 365.25, 2)
            else:
                rec.experience_years = 0.0
