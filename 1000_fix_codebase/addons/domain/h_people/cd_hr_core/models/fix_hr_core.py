# fix_hr_core — M21 complete: contracts, statutory leave, org structure (P08-M01, R06-M01).
import base64
from datetime import UTC, date, datetime, timedelta

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError

from libs.py.fix_events import get_migration_manager, normalize_bus_event, publish

from .fix_hr_controls_common import mask

# Bangladesh Labour Act 2006 statutory leave entitlements (SC-008, DoD-17), in days.
# These are the figures in force UNTIL the owner approves the 2026 amendment (see
# statutory_leave_floors): read them through that function, never directly.
STATUTORY_LEAVE = {
    "casual": 10,  # s. 115 casual leave with full wages (non-cumulative)
    "annual": 20,  # s. 117 casual+earned composite floor as practised (1 day per 18 days worked)
    "sick": 14,  # s. 116 / 148 sick leave upon medical practitioner certificate
    "festival": 11,  # s. 118 / 146 festival holidays
    "maternity": 112,  # s. 46-48: 16 weeks (112 days: 8 weeks pre-natal, 8 weeks post-natal)
    "paternity": 10,  # policy floor (not statutory; recorded as corporate policy benefit)
}
# Bangladesh Labour (Amendment) Act 2026 (Act No. 43 of 2026, passed 10 Apr 2026;
# ordinance 17 Nov 2025): s.46 maternity benefit is 120 days (60 days before and
# 60 days after delivery); s.118(1) allows 13 festival holidays a year. Applying
# them on production is an owner decision: the figures are in force only once the
# parameter below is "approved" (the same opt-in switch as the module's migration
# and seed step), so an existing 112-day maternity type is not "below the floor"
# while the owner has not approved the change.
LABOUR_ACT_2026_PARAM = "cd_hr_core.apply_labour_act_2026_figures"
STATUTORY_LEAVE_2026 = {"maternity": 120, "festival": 13}


def _labour_act_2026_applied(env):
    """True once the owner approved the Labour (Amendment) Act 2026 figures."""
    value = env["ir.config_parameter"].sudo().get_param(LABOUR_ACT_2026_PARAM) or ""
    return str(value).strip() == "approved"


def statutory_leave_floors(env):
    """The statutory leave floors in force, in days (STATUTORY_LEAVE, or the 2026
    figures for maternity and festival once the owner approved them)."""
    floors = dict(STATUTORY_LEAVE)
    if _labour_act_2026_applied(env):
        floors.update(STATUTORY_LEAVE_2026)
    return floors


PROBATION_CAP_MONTHS = 6  # Labour Rules 2021 r.25: probation <= 6 months
KPI_090_ORPHAN_HOURS = 24  # KPI-090: no account may outlive the leaver event by 24 h
KPI_090_DEPROVISION_SLA_HOURS = 1.0  # KPI-090 deprovisioning target from the leaver event
# M29's identity-lifecycle service reports the IdP outcome of every leaver back (AS-08).
IDP_PROVISIONED = "identity.provisioned"
IDP_PROVISION_FAILED = "identity.provision_failed"
IDP_DEPROVISIONED = "identity.deprovisioned"
IDP_DEPROVISION_FAILED = "identity.deprovision_failed"
IDENTITY_TOPIC = "fix.events.identity"
IDENTITY_CONSUMER_GROUP = "hr-core-identity"
# A09 audit M21-1/M21-4: every employee could read (and, through the old
# cd_employee_core ACL, rewrite) a colleague's NID, bank account, wage and
# medical restrictions. These master fields are readable and writable only by
# the HR employee officer group; payroll and the attendance registers read
# them through sudo() inside their own group-checked runs.
HR_PRIVATE = "hr.group_hr_user"
# A direct write that CHANGES one of these moves the employee (employee.moved,
# which opens one mover access review). A department on its own does not: a
# re-organisation of departments is a master edit, not a move (A09 ERP audit
# X-F15: the November load announced about five "moves" per employee). An
# applied movement publishes its own, richer event.
MOVER_FIELDS = {
    "job_id",
    "work_location_id",
    "position_id",
    "operating_unit_id",
    "branch_id",
    "job_band",
}
# A bulk loader that writes every employee (an import, a migration) wraps its
# environment in hold_mover_event() so it does not publish thousands of "moves".
# An object, never a flag: a JSON-RPC caller can put any key it likes in the
# context, but it cannot put this object there, so no request can switch the
# mover access review off.
MOVER_EVENT_HOLD_KEY = "fix_mover_event_hold"
_MOVER_EVENT_HOLD = object()


def hold_mover_event(env):
    """An environment whose hr.employee writes do not publish employee.moved."""
    return env(context=dict(env.context, **{MOVER_EVENT_HOLD_KEY: _MOVER_EVENT_HOLD}))


class HrEmployeeCdCoreExt(models.Model):
    """M21 completion fields on the W1 master slice.

    PII routing (SC-007/FF-09): NID/TIN/biometric templates NEVER land on
    hr.employee — they live in fix.identity.document (cd_party_master),
    which the residency service classifies. This extension references the
    identity store only.
    """

    # two parents: _name keeps this an extension of hr.employee
    _name = "hr.employee"
    _inherit = ["hr.employee", "fix.guarded.mixin"]

    employee_code = fields.Char(
        string="Employee Code",
        index=True,
        help="Payroll reference (M56); the identity documents carry the PII, not this model",
    )
    position_id = fields.Many2one("fix.org.position", string="Position")
    contract_count = fields.Integer(compute="_compute_contract_count", string="Contracts")
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")

    # Bangladesh Statutory Master & Identity Fields (BLA 2006, Labour Rules 2015, NBR)
    identification_mark = fields.Char(
        string="Physical Identification Mark",
        help="Distinct physical identification mark for Form 7 Service Book",
    )
    biometric_id = fields.Char(
        string="Biometric Device ID", help="Punch device PIN for branch attendance machine"
    )
    spouse_name = fields.Char(
        string="Spouse Legal Name", help="Spouse legal name if married", groups=HR_PRIVATE
    )
    private_district = fields.Char(
        string="Present District", help="Present Residential District", groups=HR_PRIVATE
    )

    # Statutory Identifiers & Tax Compliance (ITA 2023 Sections 261 & 264 PSR)
    # birth_reg_number, nid_number and tin_number are held in the
    # Bangladesh-resident store (A09 M21-A6, BRU-HCM-06): see
    # fix_hr_identity_residency.py. hr_employee keeps a pointer and a keyed hash.
    psr_ack_number = fields.Char(
        string="Tax Return Ack No (PSR)",
        help="Proof of Submission of Return (Section 264, Income Tax Act 2023)",
        groups=HR_PRIVATE,
    )
    psr_status = fields.Selection(
        [
            ("not_submitted", "Not Submitted"),
            ("submitted", "Submitted (Pending Verification)"),
            ("verified", "Verified by HR / Tax"),
            ("exempt", "Exempt"),
        ],
        string="PSR Compliance Status",
        default="not_submitted",
        help="ITA 2023 s.264 Proof of Submission of Return verification state",
        groups=HR_PRIVATE,
    )
    psr_tax_year = fields.Char(
        string="PSR Assessment Year", help="e.g. 2026-2027", groups=HR_PRIVATE
    )
    psr_verified_on = fields.Date(string="PSR Verified On", groups=HR_PRIVATE)
    psr_qr_payload = fields.Char(
        string="PSR NBR Verification Reference",
        help="NBR online verification reference or QR payload",
        groups=HR_PRIVATE,
    )
    form7_last_event_date = fields.Date(
        string="Form 7 Last Event Date",
        help="BLR 2015 r.21: Service Book must be updated within 15 days of any event",
    )
    form7_endorsed_on = fields.Date(string="Form 7 Last Endorsed Date")
    form7_update_due_date = fields.Date(
        string="Form 7 Entry Due Date", compute="_compute_form7_clock", store=True
    )
    form7_update_overdue = fields.Boolean(
        string="Form 7 Update Overdue", compute="_compute_form7_clock", store=True
    )
    # which clock set the due date (shown on the form: a month is not 15 days)
    form7_clock_rule = fields.Selection(
        [
            ("event", "Event to be entered (15 days)"),
            ("permanence", "Opening entry after becoming permanent (one month)"),
            ("appointment", "Book to be opened after appointment (15 days)"),
        ],
        string="Form 7 Clock",
        compute="_compute_form7_clock",
        store=True,
    )
    # the employee's contracts, for the Form 7 clock's dependency on a probation end
    fix_contract_ids = fields.One2many(
        "fix.employment.contract", "employee_id", string="Employment Contracts"
    )
    taxpayer_category = fields.Selection(
        [
            # A09 probe M12: the labels carried tax-free ceilings (400k/450k/
            # 500k/525k) that contradicted the payroll engine's table. The
            # ceilings are the engine's (libs/py/payroll_engine
            # TAX_FREE_THRESHOLDS), pending the tax adviser's sign-off (A09
            # report §7.3); the category carries no figure of its own.
            ("general", "General Taxpayer"),
            ("female_senior", "Female & Senior Citizen 65+"),
            ("disabled_third_gender", "Disabled & Third Gender"),
            ("freedom_fighter", "War-Wounded / Gazetted Freedom Fighter"),
        ],
        string="Taxpayer Slabs Category",
        default="general",
        help="Category for the annual tax-free threshold; the figure is the payroll "
        "engine's table (tax adviser decision, A09 §7.3)",
        groups=HR_PRIVATE,
    )
    minimum_tax_location = fields.Selection(
        [
            ("dhaka_chattogram", "Dhaka & Chattogram City Corp (BDT 5,000)"),
            ("other_city_corporation", "Other City Corporations (BDT 4,000)"),
            ("non_city_corporation", "Non-City / District / Rural (BDT 3,000)"),
        ],
        string="Minimum Tax Area",
        default="dhaka_chattogram",
        help="Statutory minimum annual tax floor",
        groups=HR_PRIVATE,
    )
    has_disabled_child = fields.Boolean(
        string="Parent of Disabled Child",
        help="Additional BDT 50,000 exemption per disabled child under Finance Act",
        groups=HR_PRIVATE,
    )
    # passport_number: held in the Bangladesh-resident store
    # (fix_hr_identity_residency.py)
    driving_license_no = fields.Char(
        string="BRTA Driving License Number",
        help="Driving license number for field mobility",
        groups=HR_PRIVATE,
    )
    driving_license_type = fields.Selection(
        [
            ("motorcycle", "Motorcycle Only"),
            ("light", "Light Motor Vehicle (Car/Van)"),
            ("heavy", "Heavy Commercial Vehicle"),
            ("special", "Special Vehicle"),
        ],
        string="Driving License Class",
        help="Governs field service van/motorcycle dispatch",
    )
    driving_license_exp = fields.Date(string="Driving License Expiration Date")
    police_clearance_ref = fields.Char(
        string="Police Clearance Ref (PCC)",
        help="Police clearance certificate reference for in-home service safety",
        groups=HR_PRIVATE,
    )

    # Organizational Hierarchy, Classification & Job Band
    job_band = fields.Selection(
        [
            ("band_1", "Band 1 - Support Staff"),
            ("band_2", "Band 2 - Technician L1"),
            ("band_3", "Band 3 - Technician L2"),
            ("band_4", "Band 4 - Senior Tech L3"),
            ("band_5", "Band 5 - Master Tech L4 / Specialist"),
            ("band_6", "Band 6 - Supervisor / Manager"),
            ("band_7", "Band 7 - Head of Dept"),
            ("band_8", "Band 8 - Director / Executive"),
        ],
        string="Corporate Grade / Band",
        default="band_2",
        help="Standard job band for salary scale & approval limits",
    )
    # M21 audit: this was declared as an override of hr's work_location_type,
    # which kept hr's compute (home/office/other from the work location): the
    # form offered it, the server refused it as read-only, and nothing was ever
    # stored. The workplace category is its own stored field.
    workplace_category = fields.Selection(
        [
            ("central_workshop", "Central Workshop Lab"),
            ("branch_counter", "Branch Walk-in Counter"),
            ("field_mobile", "Field Mobile Dispatch"),
            ("head_office", "Head Office Corporate"),
            ("hybrid", "Hybrid"),
        ],
        string="Workplace Category",
        help="Controls GPS tracking and mobile app permissions",
    )
    employment_type = fields.Selection(
        [
            ("permanent", "Permanent Confirmed"),
            ("probationary", "Probationary"),
            ("contractual", "Contractual Fixed-Term"),
            ("trainee_apprentice", "Trainee / Apprentice"),
            ("casual", "Casual / Daily"),
        ],
        string="Employment Nature",
        default="probationary",
        help="BLA Section 4 worker classification",
    )
    probation_months = fields.Integer(string="Probation Duration (Months)", default=3)
    joining_date = fields.Date(string="Date of Joining")
    confirmation_date = fields.Date(string="Permanent Confirmation Date")
    # A09 ERP audit M21-F9: a second Keycloak field (keycloak_id) stood here,
    # outside the guard, offered on the workspace form and consumed by nothing:
    # an HR user could write any value and the record then showed it as the
    # IdP id. The identity provider's id lives in keycloak_user_id alone
    # (cd_employee_core, guarded; set by the identity consumer).

    # Academic Summary Fields (Primary Degree)
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
        string="Highest Education Level",
    )
    degree_title = fields.Char(string="Highest Degree Title")
    major_group = fields.Char(string="Field of Study / Major")
    board_university = fields.Char(string="Education Board / University")
    institute_name = fields.Char(string="Academic Institution Name")
    passing_year = fields.Integer(string="Passing Year")
    result_type = fields.Selection(
        [
            ("gpa_5", "GPA out of 5.0"),
            ("cgpa_4", "CGPA out of 4.0"),
            ("first_class", "First Class"),
            ("second_class", "Second Class"),
            ("division", "Division"),
        ],
        string="Grading System",
    )
    gpa_score = fields.Float(string="Secured GPA / Score")
    roll_number = fields.Char(string="Academic Roll Number")
    registration_no = fields.Char(string="Board Registration Number")
    academic_verified = fields.Selection(
        [
            ("verified_online", "Verified Online"),
            ("verified_physical", "Verified Physical Certificate"),
            ("pending", "Verification Pending"),
            ("discrepancy", "Discrepancy Flagged"),
        ],
        string="Academic Verification Status",
        # A09 audit M21-10: summarised from the education lines, each verified
        # by a second person against its certificate (fix.hr.education).
        compute="_compute_academic_verified",
        store=True,
    )

    # Career Summary Fields (Prior Experience)
    prev_company_name = fields.Char(string="Previous Employer Name")
    prev_industry_type = fields.Selection(
        [
            ("after_sales_service", "After-Sales Repair & Warranty"),
            ("telecom", "Telecommunications"),
            ("it_hardware", "IT Hardware & Server Infrastructure"),
            ("consumer_electronics", "Consumer Electronics & TV"),
            ("hvac_appliances", "HVAC & Home Appliances"),
            ("corporate", "General Corporate"),
        ],
        string="Previous Industry Sector",
    )
    prev_designation = fields.Char(string="Previous Designation Held")
    prev_start_date = fields.Date(string="Previous Employment Start")
    prev_end_date = fields.Date(string="Previous Employment End")
    prev_experience_years = fields.Float(string="Total Prior Experience (Years)")
    prev_last_salary = fields.Float(string="Last Drawn Gross Salary (BDT)", groups=HR_PRIVATE)
    prev_reason_leaving = fields.Selection(
        [
            ("career_growth", "Career Growth"),
            ("relocation", "Relocation"),
            ("higher_studies", "Higher Studies"),
            ("compensation", "Compensation"),
            ("end_of_contract", "End of Contract"),
            ("mutual", "Mutual Separation"),
        ],
        string="Separation Reason",
    )
    prev_supervisor_name = fields.Char(string="Previous Supervisor Name")
    prev_supervisor_phone = fields.Char(string="Supervisor Contact Mobile", groups=HR_PRIVATE)
    prev_reference_status = fields.Selection(
        [
            ("verified_positive", "Verified Positive"),
            ("verified_neutral", "Verified Neutral"),
            ("negative_flag", "Negative Flag"),
            ("unreachable", "Unreachable"),
        ],
        string="Reference Check Signoff",
        # A09 audit M21-10: defaulted to "verified_positive" with no check made.
        # Summarised from the reference checks recorded on the experience lines.
        compute="_compute_prev_reference_status",
        store=True,
    )

    # Technical Competencies & After-Sales Repair Matrix
    repair_tier = fields.Selection(
        [
            ("l1_modular", "Tier L1 - Modular Replacement (Screens, Batteries, Ports)"),
            ("l2_subassembly", "Tier L2 - Sub-Assembly Diagnostics & Calibration"),
            ("l3_component", "Tier L3 - Component-Level SMT/BGA IC Repair"),
            ("l4_schematic", "Tier L4 - Schematic Reverse-Engineering & Firmware Tracing"),
        ],
        string="Technical Repair Capability Tier",
        default="l2_subassembly",
        help="Gates work order auto-dispatch and complex repair authorizations",
    )
    device_competencies = fields.Char(
        string="Supported Device Specializations",
        help="e.g. Laptops, Smartphones, Smart TVs, Inverter ACs, Enterprise Servers",
    )
    oem_brand_certs = fields.Char(
        string="OEM Brand Accreditations",
        help="e.g. Apple ACMT/ACiT, Samsung Master, HP Commercial, Daikin Inverter",
    )
    certification_no = fields.Char(string="Primary Technical Certificate No")
    cert_issue_date = fields.Date(string="Certificate Issue Date")
    cert_expiry_date = fields.Date(string="Certificate Expiry Date")
    esd_certified = fields.Boolean(
        string="ESD Safe Handling Certified",
        default=False,
        help="Electrostatic Discharge handling protocol certification",
    )
    bga_rework_capable = fields.Boolean(
        string="BGA Rework Station Authorized Operator",
        help="Authorized to operate IR/Hot-air BGA machine stations",
    )
    toolkit_custody_ref = fields.Char(string="Assigned Tool Kit Barcode Ref")
    customer_nda_signed = fields.Boolean(
        string="Customer Data Confidentiality Undertaking Signed",
        # A09 audit M21-10: True by default with no undertaking on file. It is
        # the verified NDA document, nothing typed.
        compute="_compute_dossier_flags",
        store=True,
        help="Signed compliance pledge under Cyber Security Act 2023",
    )

    # Compensation Breakdown & Allowances (Monthly BDT)
    wage = fields.Monetary(
        string="Monthly Gross Salary",
        currency_field="currency_id",
        groups=HR_PRIVATE,
        tracking=True,
    )
    basic_wage = fields.Monetary(
        string="Monthly Basic Wage",
        currency_field="currency_id",
        groups=HR_PRIVATE,
        tracking=True,
    )
    house_rent = fields.Monetary(
        string="House Rent Allowance", currency_field="currency_id", groups=HR_PRIVATE
    )
    medical_allowance = fields.Monetary(
        string="Medical Allowance", currency_field="currency_id", groups=HR_PRIVATE
    )
    conveyance_allowance = fields.Monetary(
        string="Conveyance Allowance", currency_field="currency_id", groups=HR_PRIVATE
    )
    technical_allowance = fields.Monetary(
        string="Technical Skill / OEM Allowance", currency_field="currency_id", groups=HR_PRIVATE
    )
    pf_member = fields.Boolean(
        string="Recognized Provident Fund (RPF) Member", default=True, groups=HR_PRIVATE
    )

    # Occupational Health & Medical Fitness (Workshop & Field Safety)
    color_blindness = fields.Selection(
        [
            ("normal_pass", "Normal Trichromat (Passed Ishihara Test)"),
            ("partial_deficiency", "Partial Color Deficiency"),
            ("red_green_blind", "Red-Green Color Blind (Restricted from Resistor Decoding)"),
            ("untested", "Untested"),
        ],
        string="Color Vision Test Status",
        default="untested",
        groups=HR_PRIVATE,
    )
    medical_fitness = fields.Selection(
        [
            ("fit_duty", "Fit for Full Technical / Field Duty"),
            ("fit_restricted", "Fit with Work Restrictions"),
            ("unfit_temporary", "Temporarily Unfit"),
            ("unfit_permanent", "Permanently Unfit"),
        ],
        string="Medical Fitness Verdict",
        groups=HR_PRIVATE,
    )
    work_restrictions = fields.Char(
        string="Physical Work Restrictions",
        help="e.g. No outdoor ladder work above 3m",
        groups=HR_PRIVATE,
    )
    tetanus_vaccine_date = fields.Date(
        string="Tetanus Toxoid (TT) Vaccination Date", groups=HR_PRIVATE
    )
    tetanus_expiry_date = fields.Date(string="Tetanus Booster Expiration Date", groups=HR_PRIVATE)
    chemical_allergies = fields.Char(
        string="Chemical / Solvent Allergies",
        help="e.g. IPA alcohol, rosin flux, R32 refrigerant",
        groups=HR_PRIVATE,
    )
    insurance_policy_no = fields.Char(
        string="Corporate Group Insurance Policy No", groups=HR_PRIVATE
    )

    # Secondary Emergency Contact & Nominee Allocation
    emergency_contact_sec = fields.Char(string="Secondary Emergency Contact Person")
    emergency_relation_sec = fields.Selection(
        [
            ("spouse", "Spouse"),
            ("father", "Father"),
            ("mother", "Mother"),
            ("brother", "Brother"),
            ("sister", "Sister"),
            ("son", "Son"),
            ("daughter", "Daughter"),
            ("other", "Other"),
        ],
        string="Secondary Contact Relationship",
    )
    emergency_phone_sec = fields.Char(string="Secondary Emergency Phone")
    nominee_name = fields.Char(string="Primary Statutory Nominee Name", groups=HR_PRIVATE)
    nominee_relation = fields.Selection(
        [
            ("spouse", "Spouse"),
            ("child", "Child"),
            ("parent", "Parent"),
            ("sibling", "Sibling"),
            ("other", "Other"),
        ],
        string="Nominee Relationship",
        default="spouse",
        groups=HR_PRIVATE,
    )
    # nominee_nid: held in the Bangladesh-resident store (fix_hr_identity_residency.py)
    nominee_pct = fields.Float(
        string="Nominee Share % (BLA s.19 & 131)", default=100.0, groups=HR_PRIVATE
    )
    guardian_name = fields.Char(
        string="Legal Guardian Name (if Nominee is Minor)", groups=HR_PRIVATE
    )

    # Document Dossier Compliance Checklist.
    # A09 audit M21-10: these defaulted to True for a new employee with no
    # file (51/51 live employees "had" an appointment letter, 42 had none).
    # Each flag is now the existence of a fix.hr.document of that type that a
    # second person verified (fix.hr.document.action_verify) - never typed.
    doc_nid_verified = fields.Boolean(
        string="NID Smart Card Verified", compute="_compute_dossier_flags", store=True
    )
    doc_tin_verified = fields.Boolean(
        string="12-digit e-TIN Certificate Verified", compute="_compute_dossier_flags", store=True
    )
    doc_psr_verified = fields.Boolean(
        string="Tax Return Submission Ack (PSR) Verified",
        compute="_compute_dossier_flags",
        store=True,
    )
    doc_appointment_signed = fields.Boolean(
        string="Signed Appointment Letter on File",
        compute="_compute_dossier_flags",
        store=True,
        help="A verified appointment letter the employee acknowledged",
    )
    doc_nda_signed = fields.Boolean(
        string="Signed NDA & Code of Conduct on File", compute="_compute_dossier_flags", store=True
    )
    doc_service_book_scanned = fields.Boolean(
        string="Form 7 Service Book Pages Scanned", compute="_compute_dossier_flags", store=True
    )
    doc_medical_fit_certified = fields.Boolean(
        string="Medical Fitness Certificate Signed", compute="_compute_dossier_flags", store=True
    )
    doc_police_pcc_cleared = fields.Boolean(
        string="Police Clearance Certificate (PCC) Cleared",
        compute="_compute_dossier_flags",
        store=True,
    )

    # Physical Scanned Document File Attachments (BLA 2006, ISO 9001:2015 Audit Vault)
    doc_nid_file = fields.Binary(
        string="National ID Smart Card Scan", attachment=True, groups=HR_PRIVATE
    )
    doc_nid_filename = fields.Char(string="NID File Name", groups=HR_PRIVATE)
    doc_tin_file = fields.Binary(
        string="12-digit e-TIN Certificate Scan", attachment=True, groups=HR_PRIVATE
    )
    doc_tin_filename = fields.Char(string="TIN File Name", groups=HR_PRIVATE)
    doc_psr_file = fields.Binary(
        string="Tax Return Acknowledgement (PSR) Scan", attachment=True, groups=HR_PRIVATE
    )
    doc_psr_filename = fields.Char(string="PSR File Name", groups=HR_PRIVATE)
    doc_appointment_file = fields.Binary(
        string="Signed Appointment Letter Scan", attachment=True, groups=HR_PRIVATE
    )
    doc_appointment_filename = fields.Char(string="Appointment File Name", groups=HR_PRIVATE)
    doc_service_book_file = fields.Binary(
        string="Form 7 Service Book Pages Scan", attachment=True, groups=HR_PRIVATE
    )
    doc_service_book_filename = fields.Char(string="Service Book File Name", groups=HR_PRIVATE)
    doc_nda_file = fields.Binary(
        string="Signed NDA & Code of Conduct Scan", attachment=True, groups=HR_PRIVATE
    )
    doc_nda_filename = fields.Char(string="NDA File Name", groups=HR_PRIVATE)
    doc_medical_file = fields.Binary(
        string="Medical Fitness Certificate Scan", attachment=True, groups=HR_PRIVATE
    )
    doc_medical_filename = fields.Char(string="Medical File Name", groups=HR_PRIVATE)
    doc_police_pcc_file = fields.Binary(
        string="Police Clearance Certificate (PCC) Scan", attachment=True, groups=HR_PRIVATE
    )
    doc_police_pcc_filename = fields.Char(string="PCC File Name", groups=HR_PRIVATE)
    doc_academic_file = fields.Binary(
        string="Highest Academic Certificate Scan", attachment=True, groups=HR_PRIVATE
    )
    doc_academic_filename = fields.Char(string="Academic File Name", groups=HR_PRIVATE)
    doc_nominee_nid_file = fields.Binary(
        string="Nominee NID & Photo Scan", attachment=True, groups=HR_PRIVATE
    )
    doc_nominee_nid_filename = fields.Char(string="Nominee File Name", groups=HR_PRIVATE)

    # Sub-record Relational Links
    education_line_ids = fields.One2many(
        "fix.hr.education", "employee_id", string="Academic Qualifications"
    )
    experience_line_ids = fields.One2many(
        "fix.hr.experience", "employee_id", string="Work Experience"
    )
    document_ids = fields.One2many("fix.hr.document", "employee_id", string="Document Dossier")
    dependant_ids = fields.One2many(
        "fix.hr.dependant", "employee_id", string="Dependants & Nominees"
    )

    # Bangladesh Statutory Master & Identity Fields (BLA 2006, Labour Rules 2015, NBR)
    father_name = fields.Char(
        string="Father's Name",
        help="Father's Name (Form 7 Service Book; Form 8 register of workers)",
    )
    mother_name = fields.Char(string="Mother's Name", help="Mother's Name (Form 7 Service Book)")
    blood_group = fields.Selection(
        [
            ("a_pos", "A+ (Positive)"),
            ("a_neg", "A- (Negative)"),
            ("b_pos", "B+ (Positive)"),
            ("b_neg", "B- (Negative)"),
            ("ab_pos", "AB+ (Positive)"),
            ("ab_neg", "AB- (Negative)"),
            ("o_pos", "O+ (Positive)"),
            ("o_neg", "O- (Negative)"),
        ],
        string="Blood Group",
        help="Blood Group (Mandatory for field technicians and occupational health)",
        groups=HR_PRIVATE,
    )
    religion = fields.Selection(
        [
            ("islam", "Islam"),
            ("hinduism", "Hinduism"),
            ("buddhism", "Buddhism"),
            ("christianity", "Christianity"),
            ("other", "Other"),
        ],
        string="Religion",
        help="Religion (Required for statutory festival holiday bonus entitlement rules)",
        groups=HR_PRIVATE,
    )
    # EMP-MIG-RPT-001 R7: the two fields the 2026-11-09 capability audit measured
    # absent from the live master. `sex` matches the AGENTS.md statutory naming
    # (Gender (`sex`)); third_gender is the recognised BD census category.
    sex = fields.Selection(
        [
            ("male", "Male"),
            ("female", "Female"),
            ("third_gender", "Third Gender (Hijra)"),
            ("unspecified", "Unrecorded"),
        ],
        string="Gender",
        default="unspecified",
        help="Gender (Form 7 Service Book; BLA 2006 worker register)",
        groups=HR_PRIVATE,
    )
    passport_no = fields.Char(
        string="Passport Number",
        help="Machine-readable passport number (MRP/e-Passport), e.g. BR0934567",
        groups=HR_PRIVATE,
    )
    # EMP-MIG-RPT-001 §3.5: marital is required but legacy extracts (the 504-row
    # real-employee load) carry no marital data — an honest 'unrecorded' value
    # replaces fabricating single/married during migration. Odoo 19 owns the
    # selection on hr.version (hr.employee delegates via _inherits) — extended
    # in HrVersionCdCoreExt at the end of this file.
    tax_zone = fields.Char(
        string="NBR Tax Zone",
        help="National Board of Revenue tax circle zone (e.g. Zone-01, Dhaka)",
        groups=HR_PRIVATE,
    )
    tax_circle = fields.Char(
        string="NBR Tax Circle",
        help="National Board of Revenue tax circle (e.g. Circle-15)",
        groups=HR_PRIVATE,
    )
    service_book_number = fields.Char(
        string="Service Book Ref",
        help="Bangladesh Labour Rules 2015 Form 7 Service Book registered number (s. 11)",
    )

    # Address & Residence (Present vs Permanent)
    permanent_address = fields.Text(
        string="Permanent Address",
        help="Permanent Address (Village/Road, Post Office, Thana)",
        groups=HR_PRIVATE,
    )
    permanent_district = fields.Char(
        string="Permanent District", help="Permanent District", groups=HR_PRIVATE
    )
    permanent_division = fields.Selection(
        [
            ("dhaka", "Dhaka"),
            ("chattogram", "Chattogram"),
            ("rajshahi", "Rajshahi"),
            ("khulna", "Khulna"),
            ("barishal", "Barishal"),
            ("sylhet", "Sylhet"),
            ("rangpur", "Rangpur"),
            ("mymensingh", "Mymensingh"),
        ],
        string="Permanent Division",
        help="Permanent Division",
        groups=HR_PRIVATE,
    )

    # Emergency Contact Details (BLA Form 7 next-of-kin)
    emergency_contact_relation = fields.Selection(
        [
            ("spouse", "Spouse"),
            ("father", "Father"),
            ("mother", "Mother"),
            ("brother", "Brother"),
            ("sister", "Sister"),
            ("son", "Son"),
            ("daughter", "Daughter"),
            ("other", "Other"),
        ],
        string="Emergency Contact Relation",
        help="Emergency Contact Relationship",
    )
    emergency_contact_address = fields.Text(
        string="Emergency Contact Address", help="Emergency Contact Address", groups=HR_PRIVATE
    )
    emergency_phone_alt = fields.Char(
        string="Emergency Alternative Phone", help="Alternative Emergency Phone"
    )

    # Payroll, Banking & MFS (Bangladesh Electronic Fund Transfer Network & Mobile Wallets)
    bank_name = fields.Char(
        string="Bank Name",
        help="Scheduled Commercial Bank in Bangladesh",
        groups=HR_PRIVATE,
        tracking=True,
    )
    bank_branch_name = fields.Char(string="Bank Branch", help="Bank branch name", groups=HR_PRIVATE)
    routing_number = fields.Char(
        string="BEFTN Routing Number",
        help="9-digit Bangladesh Bank BEFTN routing code",
        groups=HR_PRIVATE,
        tracking=True,
    )
    bank_account_number = fields.Char(
        string="Bank Account Number",
        help="Savings / Current bank account number",
        groups=HR_PRIVATE,
        tracking=True,
    )
    mfs_provider = fields.Selection(
        [
            ("bkash", "bKash"),
            ("nagad", "Nagad"),
            ("rocket", "DBBL Rocket"),
            ("upay", "UCB Upay"),
            ("other", "Other MFS"),
        ],
        string="MFS Provider",
        help="Mobile Financial Services wallet provider for daily allowances & field expenses",
        groups=HR_PRIVATE,
        tracking=True,
    )
    mfs_account_number = fields.Char(
        string="MFS Account Number",
        help="11-digit mobile wallet number (01XXXXXXXXX)",
        groups=HR_PRIVATE,
        tracking=True,
    )
    overtime_eligible = fields.Boolean(
        string="Overtime Eligible",
        default=True,
        help="Bangladesh Labour Act 2006 s. 108: eligible for double ordinary rate overtime wages",
    )

    # KPI-090 (BRD 2712; 06-02 KPI register): zero orphaned accounts beyond
    # 24 h AFTER A LEAVER EVENT; deprovisioning target <= 1 h. The clock starts
    # at the leaver event (left_at), never at the hire date. "deprovisioned" is
    # set only when the removal is CONFIRMED - the module never claims it
    # itself (GV-009: no self-reported compliance).
    keycloak_deprovision_status = fields.Selection(
        [
            ("active", "Active"),
            ("pending", "Pending Deprovision"),
            ("deprovisioned", "Deprovisioned"),
            ("failed", "Failed"),
        ],
        default="active",
        tracking=True,
        help="KPI-090: 'pending' from the leaver event (employee.left, consumed by "
        "M29) until the Keycloak removal is confirmed",
    )
    left_at = fields.Datetime(
        string="Left At (Leaver Event)",
        readonly=True,
        copy=False,
        tracking=True,
        help="When employee.left was emitted - the KPI-090 clock start",
    )
    keycloak_deprovisioned_at = fields.Datetime(
        string="Keycloak Deprovisioned At",
        readonly=True,
        copy=False,
        help="When the Keycloak removal was confirmed (target <= 1 h after the leaver event)",
    )
    keycloak_deprovision_confirmed_by = fields.Many2one(
        "res.users",
        string="Deprovisioning Confirmed By",
        readonly=True,
        copy=False,
        tracking=True,
        help="The HR manager who confirmed the Keycloak removal (manual control)",
    )
    keycloak_deprovision_hours = fields.Float(
        string="Deprovisioning Time (Hours)",
        compute="_compute_keycloak_deprovision_hours",
        store=True,
        help="Hours from the leaver event to the confirmed removal (KPI-090 target <= 1 h)",
    )

    @api.depends(
        "form7_last_event_date",
        "form7_endorsed_on",
        "joining_date",
        "confirmation_date",
        "employment_type",
        "probation_months",
        "fix_contract_ids.state",
        "fix_contract_ids.contract_type",
        "fix_contract_ids.probation_end",
    )
    def _compute_form7_clock(self):
        """When the next service-book entry falls due, and whether it is late.

        A09 ERP audit M21-F22: the clock ran from the last event, or from the
        joining date plus 15 days, for every employee. Bangladesh Labour Rules
        2015 keep two clocks for the opening entry: r.21(1) puts it within one
        month of becoming permanent (the confirmation date, or the end of the
        probation for a worker not yet decided); r.22(1) has the book opened
        within 15 days of the appointment when no probation applies. An event
        still has to be entered (the module's event clock, unchanged). The
        overdue flag depends on today's date, which is no field dependency: the
        daily cron (_cron_form7_clock) re-derives it."""
        today = fields.Date.context_today(self)
        for rec in self:
            base, rule = rec._fix_form7_base()
            if not base:
                rec.form7_update_due_date = False
                rec.form7_update_overdue = False
                rec.form7_clock_rule = False
                continue
            due = base + (relativedelta(months=1) if rule == "permanence" else timedelta(days=15))
            endorsed = rec.form7_endorsed_on or False
            # an event is entered by an endorsement on or after it; an opening
            # entry by any verified entry (the book is open)
            entered = bool(endorsed) and (rule != "event" or endorsed >= base)
            rec.form7_update_due_date = due
            rec.form7_clock_rule = rule
            rec.form7_update_overdue = bool(not entered and today > due)

    def _fix_probation_permanence_date(self):
        """The day a worker still on probation becomes permanent: the day after
        the earliest running probation ends, else the day after the master's own
        probation length. False when no probation is on record."""
        self.ensure_one()
        srec = self.sudo()
        ends = srec.fix_contract_ids.filtered(
            lambda c: c.state == "active" and c.contract_type == "probation" and c.probation_end
        ).mapped("probation_end")
        if ends:
            return min(ends) + timedelta(days=1)
        if srec.employment_type == "probationary" and srec.joining_date and srec.probation_months:
            return (
                srec.joining_date + relativedelta(months=srec.probation_months) + timedelta(days=1)
            )
        return False

    def _fix_form7_base(self):
        """(date the clock runs from, rule) for one employee: an event that was
        recorded, else becoming permanent, else the appointment."""
        self.ensure_one()
        event = self.form7_last_event_date or False
        if event:
            return event, "event"
        permanence = self.confirmation_date or self._fix_probation_permanence_date()
        if permanence:
            return permanence, "permanence"
        return self.joining_date or False, "appointment"

    @api.model
    def _fix_recompute_form7_clock(self):
        """Upgrade step: the stored clock of every employee is re-derived under
        the rules above (rows saved earlier carry the old joining-plus-15-days
        due date). Idempotent; superuser only (run from the module's data file)."""
        if not self.env.su:
            raise AccessError("Run by the module upgrade only.")
        employees = self.with_context(active_test=False).search([])
        for name in ("form7_update_due_date", "form7_update_overdue", "form7_clock_rule"):
            self.env.add_to_compute(self._fields[name], employees)
        self.env.flush_all()
        return len(employees)

    @api.model
    def _cron_form7_clock(self):
        """Daily: a due date that passed overnight turns the overdue flag on
        (the flag is stored, and today is not one of its dependencies)."""
        today = fields.Date.context_today(self.with_context(tz="Asia/Dhaka"))
        employees = (
            self.sudo()
            .with_context(active_test=False, tz="Asia/Dhaka")
            .search(
                [("form7_update_due_date", "!=", False), ("form7_update_due_date", "<=", today)]
            )
        )
        self.env.add_to_compute(self._fields["form7_update_overdue"], employees)
        self.env.flush_all()
        return len(employees)

    def action_generate_form7_service_book(self):
        """BLR 2015 r.20 / BLA 2006 s.6-9: a Form 7 Service Book entry (a
        generated, unsigned text: the book is endorsed when the signed scan of
        the entry is verified, never by generating it)."""
        docs = self.env["fix.hr.document"]
        today = fields.Date.context_today(self)
        for rec in self.with_context(fix_identity_read_purpose="Form 7 service book (masked)"):
            payload = (
                f"FORM 7 - SERVICE BOOK (Bangladesh Labour Rules 2015, Rule 20)\n"
                f"Service Book No: {rec.service_book_number or 'SB-' + (rec.employee_code or str(rec.id))}\n"
                f"Worker Name: {rec.name}\n"
                f"Father's Name: {rec.father_name or ''}\n"
                f"Mother's Name: {rec.mother_name or ''}\n"
                # an unsigned generated draft carries the last four digits only;
                # the signed service book is the record (fix.hr.document)
                f"NID / Smart Card: {mask(rec.nid_number)}\n"
                f"Identification Mark: {rec.identification_mark or ''}\n"
                f"Designation / Band: {rec.job_title or ''} ({rec.job_band or ''})\n"
                f"Joining Date: {rec.joining_date or ''}\n"
                f"Basic Wage: {rec.basic_wage or 0.0:.2f} | Gross Wage: {rec.wage or 0.0:.2f}\n"
                f"Endorsed On: {today}\n"
            ).encode()
            doc = (
                self.env["fix.hr.document"]
                ._guarded()
                .create(
                    {
                        "employee_id": rec.id,
                        "doc_type": "service_book",
                        "reference": rec.service_book_number
                        or f"FORM7/{rec.employee_code or rec.id}",
                        "issued_on": today,
                        # A09 audit M21-10: a generated text entry is not a signed,
                        # scanned service book. It is unverified until a second
                        # person verifies the signed scan (fix.hr.document).
                        "generated": True,
                        "file_name": f"Form7_ServiceBook_{rec.employee_code or rec.id}.txt",
                        "file_data": base64.b64encode(payload),
                    }
                )
            )
            # A generated, unsigned text is not an endorsement: stamping it
            # cleared the BLR r.21 15-day overdue flag with nothing signed (M21
            # audit F3). The entry is endorsed when its signed scan is verified.
            docs |= doc
        return docs

    # A09 ERP audit M21-F2: the letter of appointment is NOT a numbered form
    # (Form 6 is the identity card, BLR 2015 r.19(5)). r.19(4) names the ten
    # particulars it must carry; the method keeps its name (the workspace
    # actions and the callers know it by it).
    NOT_RECORDED = "NOT RECORDED"
    R194_COMPLIANCE = (
        "The terms and conditions of this appointment are in accordance with the "
        "Bangladesh Labour Act 2006 and the Bangladesh Labour Rules 2015."
    )

    def _fix_letter_particulars(self, contract):
        """The r.19(4) particulars of one employee's letter of appointment as
        (label, text), in the Rule's order, and the labels not on record. A
        particular that is not on record reads NOT RECORDED, never a blank
        line: a letter with a silent blank could be signed and issued."""
        self.ensure_one()
        division = dict(self._fields["permanent_division"].selection)
        nature = dict(self._fields["employment_type"].selection)

        def address(*parts):
            return ", ".join(p for p in parts if p)

        def work():
            if self.job_title:
                return self.job_title
            return self.position_id.name if self.position_id else ""

        particulars = [
            ("Name", self.name or ""),
            ("Father's Name", self.father_name or ""),
            ("Mother's Name", self.mother_name or ""),
            ("Spouse's Name", self.spouse_name or ""),
            (
                "Present Address",
                address(self.private_street, self.private_city, self.private_district),
            ),
            (
                "Permanent Address",
                address(
                    self.permanent_address,
                    self.permanent_district,
                    division.get(self.permanent_division, self.permanent_division),
                ),
            ),
            ("Designation and Type of Work", work()),
            ("Joining Date", str(contract.joining_date or "")),
            (
                "Class of Worker",
                nature.get(self.employment_type, self.employment_type or ""),
            ),
            ("Wage Scale", contract.wage_scale or ""),
            ("Increment Rate", contract.increment_rate or ""),
            ("Other Financial Facilities", contract.other_facilities or ""),
        ]
        lines = ["%s: %s" % (label, text or self.NOT_RECORDED) for label, text in particulars]
        # the tenth particular: the statement that the terms comply with the Act
        lines.append("Compliance Statement: %s" % self.R194_COMPLIANCE)
        missing = [label for label, text in particulars if not text]
        return lines, missing

    def action_generate_form6_appointment(self):
        """The letter of appointment of BLR 2015 r.19(4) (BLA 2006 s.5): a
        generated, unsigned text carrying the particulars the Rule names. It
        is unverified until a second HR person verifies the signed scan."""
        docs = self.env["fix.hr.document"]
        today = fields.Date.context_today(self)
        for rec in self:
            # The letter states the CONTRACT's terms. It printed the employee
            # master's wage fields, which nothing maintained ("Basic Wage: BDT
            # 0.00" on a signed-off contract) and a blank nature as "permanent".
            contract = (
                self.env["fix.employment.contract"]
                .sudo()
                .search(
                    [("employee_id", "=", rec.id), ("state", "in", ("active", "draft"))],
                    order="state, id desc",
                    limit=1,
                )
            )
            if not contract:
                raise UserError(
                    "%s has no employment contract: the letter of appointment states the "
                    "contract's terms, so record the contract (Hire / Onboard) first." % rec.name
                )
            nature = dict(
                self.env["fix.employment.contract"]._fields["contract_type"].selection
            ).get(contract.contract_type, contract.contract_type)
            gross = sum(
                contract[f] or 0.0
                for f in (
                    "basic_monthly",
                    "house_rent",
                    "medical_allowance",
                    "conveyance_allowance",
                    "technical_allowance",
                    "other_allowance",
                )
                if f in contract._fields
            )
            particulars, missing = rec._fix_letter_particulars(contract)
            payload = "\n".join(
                [
                    "APPOINTMENT LETTER (Bangladesh Labour Rules 2015, Rule 19(4))",
                    "Employer: %s" % (rec.company_id.name or ""),
                    "Employee Code: %s" % (rec.employee_code or self.NOT_RECORDED),
                    *particulars,
                    "",
                    "Employment Nature (contract): %s" % nature,
                    "Probation Ends: %s" % (contract.probation_end or "not applicable"),
                    f"Basic Wage: BDT {contract.basic_monthly or 0.0:,.2f}",
                    f"House Rent: BDT {contract.house_rent or 0.0:,.2f}",
                    f"Medical: BDT {contract.medical_allowance or 0.0:,.2f}",
                    f"Conveyance: BDT {contract.conveyance_allowance or 0.0:,.2f}",
                    f"Gross Salary: BDT {gross:,.2f}",
                    "Contract: %s" % contract.name,
                    "Generated: %s (unsigned: the signed scan is verified before issue)" % today,
                ]
            ).encode()
            doc = (
                self.env["fix.hr.document"]
                ._guarded()
                .create(
                    {
                        "employee_id": rec.id,
                        "doc_type": "appointment",
                        "reference": f"APPT/{rec.employee_code or rec.id}/{today}",
                        "issued_on": today,
                        "generated": True,
                        "file_name": f"AppointmentLetter_{rec.employee_code or rec.id}.txt",
                        "file_data": base64.b64encode(payload),
                        "notes": (
                            "Not on record at generation (BLR r.19(4)): %s" % "; ".join(missing)
                            if missing
                            else False
                        ),
                    }
                )
            )
            docs |= doc
        return docs

    # ---- the statutory registers (HR only) ----------------------------------
    # BLR 2015 r.19(7): Form 6(A) is the register of the issue of the letter of
    # appointment, the identity card (Form 6, r.19(5)) and the service book
    # (Form 7, r.20). BLR r.23: the register of workers is Form 8. Neither
    # carries a national ID (A09 ERP audit M21-F1): the NID stays in the
    # Bangladesh-resident store, and these exports read none of it.
    FORM6A_DOCUMENTS = (
        ("appointment", "appointment letter"),
        ("id_card", "identity card"),
        ("service_book", "service book"),
    )

    def _fix_require_hr_register(self, what):
        """The statutory registers are HR's (Employee Officer or Manager).

        The record rules on hr.employee already keep a plain employee out; this
        is the explicit gate, so a later loosening of those rules cannot widen
        the registers with it (A09 ERP audit M21-F3)."""
        if not (self.env.su or self.env.user.has_group(HR_PRIVATE)):
            raise AccessError("Only HR may export the %s." % what)

    def _fix_register_rows(self, domain):
        """The workers on the books, in register order (joining date, then the
        record): the serial of a worker is the same in the Register of Workers
        and in Form 6(A). Read as the caller."""
        return self.search(
            [("left_date", "=", False), *(domain or [])], order="joining_date asc, id asc"
        )

    def _fix_designation(self):
        self.ensure_one()
        return self.job_title or (self.position_id.name if self.position_id else "")

    @api.model
    def action_export_workers_register(self, domain=None):
        """BLR 2015 r.23: the register of workers, in the shape of Form 8."""
        self._fix_require_hr_register("Register of Workers")
        nature = dict(self._fields["employment_type"].selection)
        rows = []
        for idx, emp in enumerate(self._fix_register_rows(domain), start=1):
            rows.append(
                {
                    "serial": idx,
                    "employee_code": emp.employee_code or "",
                    "name": emp.name or "",
                    "father_name": emp.father_name or "",
                    "mother_name": emp.mother_name or "",
                    "department": emp.department_id.name or "",
                    "designation": emp._fix_designation(),
                    "employment_type": nature.get(emp.employment_type, emp.employment_type or ""),
                    "joining_date": str(emp.joining_date or ""),
                    "service_book_number": emp.service_book_number or "",
                }
            )
        return rows

    @api.model
    def action_export_form6a_register(self, domain=None):
        """BLR 2015 r.19(7): Form 6(A), the register of the issue of the letter
        of appointment, the identity card and the service book, from the
        employee's statutory documents (fix.hr.document).

        The issue date of a document is the date of its first verified copy (the
        signed scan a second HR person verified). A document that was only
        generated is shown with its generation date and said so in the remarks."""
        self._fix_require_hr_register("Form 6(A) register")
        emps = self._fix_register_rows(domain)
        today = fields.Date.context_today(self)
        documents = self.env["fix.hr.document"].search(
            [
                ("employee_id", "in", emps.ids),
                ("doc_type", "in", [t for t, _l in self.FORM6A_DOCUMENTS]),
            ]
        )
        # (employee id, doc type) -> {"verified": date, "generated": date}
        issued = {}
        for doc in documents.sorted(lambda d: (d.issued_on or date.min, d.id)):
            entry = issued.setdefault((doc.employee_id.id, doc.doc_type), {})
            kind = "verified" if doc.verified else "generated"
            if kind == "verified" or "verified" not in entry:
                entry.setdefault(kind, doc.issued_on)
        rows = []
        for idx, emp in enumerate(emps, start=1):
            remarks = []
            cells = {}
            for doc_type, label in self.FORM6A_DOCUMENTS:
                entry = issued.get((emp.id, doc_type), {})
                if "verified" in entry:
                    cells[doc_type] = entry["verified"]
                elif "generated" in entry:
                    cells[doc_type] = entry["generated"]
                    remarks.append(
                        "%s generated %s, signed copy not verified" % (label, entry["generated"])
                    )
                else:
                    cells[doc_type] = False
                    remarks.append("%s not on record" % label)
            age = relativedelta(today, emp.birthday).years if emp.birthday else False
            rows.append(
                {
                    "serial": idx,
                    # the worker's line in the Register of Workers (same order)
                    "register_serial": idx,
                    "name": emp.name or "",
                    "age": age,
                    "nature_of_work": emp._fix_designation(),
                    "appointment_letter_on": cells["appointment"],
                    "identity_card_on": cells["id_card"],
                    "service_book_on": cells["service_book"],
                    # signed by the worker on the printed register
                    "signature": "",
                    "remarks": "; ".join(remarks),
                }
            )
        return rows

    def _fix_guarded_fields(self) -> set:
        # A09 audit M21-6: a user who could write the master marked a leaver
        # "deprovisioned" (KPI-090 green with the account still live) or bound
        # a colleague to a Keycloak id of their choosing. Only the leaver path,
        # the HR manager's confirmation and the identity-provider consumer
        # change these.
        # A09 P0-b (M21-10): the PSR verification and the Form 7 endorsement
        # date are stamped by their actions, never typed; the Odoo access
        # revocation is stamped by the leaver consumer.
        return super()._fix_guarded_fields() | {
            "left_at",
            "keycloak_deprovision_status",
            "keycloak_deprovisioned_at",
            "keycloak_deprovision_confirmed_by",
            "keycloak_user_id",
            "psr_status",
            "psr_verified_on",
            "psr_submitted_by_id",
            "psr_verified_by_id",
            "form7_endorsed_on",
            "odoo_access_revoked_at",
        }

    def _compute_contract_count(self):
        for rec in self:
            rec.contract_count = self.env["fix.employment.contract"].search_count(
                [("employee_id", "=", rec.id)]
            )

    @api.depends("left_at", "keycloak_deprovisioned_at")
    def _compute_keycloak_deprovision_hours(self):
        for rec in self:
            if rec.left_at and rec.keycloak_deprovisioned_at:
                span = rec.keycloak_deprovisioned_at - rec.left_at
                rec.keycloak_deprovision_hours = round(span.total_seconds() / 3600, 2)
            else:
                rec.keycloak_deprovision_hours = 0.0

    def _emit_leaver(self):
        """The leaver event (cd_employee_core: employee.left, which M29
        consumes to remove the Keycloak account) starts the KPI-090 clock:
        the time is recorded and deprovisioning is REQUESTED (pending)."""
        super()._emit_leaver()
        self._guarded().write(
            {
                "left_at": fields.Datetime.now(),
                "keycloak_deprovision_status": "pending",
                "keycloak_deprovisioned_at": False,
                "keycloak_deprovision_confirmed_by": False,
            }
        )

    def action_confirm_keycloak_deprovisioned(self):
        """Manual control: an HR manager confirms that the leaver's Keycloak
        account was verified as removed.

        The normal path is the identity provider's own confirmation
        (consume_identity_lifecycle_event, "confirmation": "idp"); this named
        person's confirmation - recorded with the time - is the fallback when the
        IdP reported a failure or did not answer."""
        if not (self.env.su or self.env.user.has_group("hr.group_hr_manager")):
            raise AccessError(
                "Only an HR manager may confirm a Keycloak deprovisioning (KPI-090 control)"
            )
        now = fields.Datetime.now()
        for rec in self:
            if rec.keycloak_deprovision_status not in ("pending", "failed"):
                raise UserError(
                    "%s has no Keycloak deprovisioning to confirm (status: %s) - it is "
                    "requested by the leaver event" % (rec.name, rec.keycloak_deprovision_status)
                )
            rec._guarded().write(
                {
                    "keycloak_deprovision_status": "deprovisioned",
                    "keycloak_deprovisioned_at": now,
                    "keycloak_deprovision_confirmed_by": self.env.uid,
                }
            )
            publish(
                self.env,
                "employee.keycloak.deprovisioned",
                "hr.employee",
                rec.id,
                {
                    "employee_code": rec.employee_code or "",
                    "left_at": str(rec.left_at),
                    "deprovisioned_at": str(now),
                    "hours": rec.keycloak_deprovision_hours,
                    "within_sla": rec.keycloak_deprovision_hours <= KPI_090_DEPROVISION_SLA_HOURS,
                    "confirmed_by": self.env.user.name,
                    "confirmation": "manual",
                    "kpi": "KPI-090",
                },
            )

    @api.model
    def consume_identity_lifecycle_event(self, raw_event):
        """M29 -> M21: apply the identity provider's joiner / leaver outcome.

        ``identity.provisioned`` (or a provisioning failure that still created the
        account) stores the Keycloak user id on the employee, so the leaver event
        later deprovisions by id. ``identity.deprovisioned`` is the IdP-confirmed removal (the account verified
        disabled with no session left): the leaver is marked deprovisioned with
        ``"confirmation": "idp"``. ``identity.deprovision_failed`` marks it failed and
        records the reason - the HR manager's manual confirmation stays the fallback
        control. Idempotent: a re-delivered or late event never changes a confirmed
        removal. Returns the employee updated (empty when nothing applied).
        """
        # A09 audit M21-6: public, so any user could call it over JSON-RPC and
        # mark a leaver deprovisioned. Only the identity consumer (the cron,
        # superuser) applies the provider's outcome.
        if not self.env.su:
            raise AccessError(
                "Identity-provider outcomes are applied by the identity consumer only"
            )
        event = normalize_bus_event(raw_event)
        if event["event_type"] not in (
            IDP_PROVISIONED,
            IDP_PROVISION_FAILED,
            IDP_DEPROVISIONED,
            IDP_DEPROVISION_FAILED,
        ):
            return self.browse()
        payload = event["payload"]
        employee = (
            self.with_context(active_test=False)
            .browse(int(payload.get("employee_id") or event["aggregate_id"] or 0))
            .exists()
        )
        if employee and event["event_type"] in (IDP_PROVISIONED, IDP_PROVISION_FAILED):
            return employee._apply_identity_provisioning(event["event_type"], payload)
        # only a leaver with a running KPI-090 clock; a confirmed removal is final
        if not employee or employee.keycloak_deprovision_status not in ("pending", "failed"):
            return self.browse()
        if event["event_type"] == IDP_DEPROVISION_FAILED:
            employee.keycloak_deprovision_status = "failed"
            employee.message_post(
                body="Keycloak deprovisioning failed (%s): %s - confirm manually once removed."
                % (payload.get("reason_code"), payload.get("reason"))
            )
            return employee
        stamp = datetime.fromisoformat(str(payload["deprovisioned_at"]).replace("Z", "+00:00"))
        deprovisioned_at = stamp.astimezone(UTC).replace(tzinfo=None)
        employee.write(
            {
                "keycloak_deprovision_status": "deprovisioned",
                "keycloak_deprovisioned_at": deprovisioned_at,
                "keycloak_deprovision_confirmed_by": False,
                "keycloak_user_id": payload.get("keycloak_user_id") or employee.keycloak_user_id,
            }
        )
        publish(
            self.env,
            "employee.keycloak.deprovisioned",
            "hr.employee",
            employee.id,
            {
                "employee_code": employee.employee_code or "",
                "left_at": str(employee.left_at),
                "deprovisioned_at": str(deprovisioned_at),
                "hours": employee.keycloak_deprovision_hours,
                "within_sla": employee.keycloak_deprovision_hours <= KPI_090_DEPROVISION_SLA_HOURS,
                "confirmed_by": "identity-lifecycle (Keycloak)",
                "confirmation": "idp",
                "kpi": "KPI-090",
            },
            {"correlation_id": event["correlation_id"], "causation_id": event["event_id"]},
        )
        return employee

    def _apply_identity_provisioning(self, event_type, payload):
        """Store the joiner's Keycloak user id (never silently replace another one)."""
        self.ensure_one()
        kc_id = payload.get("keycloak_user_id")
        if event_type == IDP_PROVISION_FAILED:
            self.message_post(
                body="Keycloak provisioning failed (%s): %s"
                % (payload.get("reason_code"), payload.get("reason"))
            )
        if not kc_id or kc_id == self.keycloak_user_id:
            return self if event_type == IDP_PROVISION_FAILED else self.browse()
        if self.keycloak_user_id:
            self.message_post(
                body="Keycloak reported account %s for this employee, but %s is on record - "
                "kept the recorded one; check for a duplicate identity."
                % (kc_id, self.keycloak_user_id)
            )
            return self.browse()
        self.keycloak_user_id = kc_id
        return self

    @api.model
    def drain_identity_lifecycle_events(self, limit=50):
        """Consume M29's identity outcomes through fix_events (FF-28) - the cron's job."""
        if not self.env.su:
            raise AccessError(
                "Identity-provider outcomes are applied by the identity consumer only"
            )
        manager = get_migration_manager()
        manager.register_group(IDENTITY_CONSUMER_GROUP)
        applied = []
        manager.consume_event(
            IDENTITY_CONSUMER_GROUP,
            IDENTITY_TOPIC,
            lambda raw: applied.append(self.consume_identity_lifecycle_event(raw)),
            limit,
        )
        return self.browse([e.id for e in applied if e])

    @api.model
    def measure_kpi_090_orphaned_accounts(self):
        """KPI-090: leavers whose leaver event is more than 24 h old and whose
        Keycloak removal is not confirmed - archived or not (a leaver may
        still be an active record)."""
        cutoff = fields.Datetime.now() - timedelta(hours=KPI_090_ORPHAN_HOURS)
        return self.with_context(active_test=False).search_count(
            [
                ("left_at", "!=", False),
                ("left_at", "<=", cutoff),
                ("keycloak_deprovision_status", "!=", "deprovisioned"),
            ]
        )

    # P08-M01-T06 / R06-M01-T03: joiner/mover/leaver event set drives M29 provisioning
    def write(self, vals):
        # The workspace form posts every field it shows. An unchanged position
        # re-ran the seat constraint (BRU-HCM-10), so an employee of a
        # position already over its sanctioned headcount could not be saved at
        # all; and every save announced a move to M29 (M21 audit F6/F7).
        if "position_id" in vals and self:
            new_pos = vals["position_id"] or False
            if isinstance(new_pos, models.BaseModel):
                new_pos = new_pos.id
            if all(rec.position_id.id == new_pos for rec in self.sudo()):
                vals = {k: v for k, v in vals.items() if k != "position_id"}
        movers = [f for f in MOVER_FIELDS & set(vals) if f in self._fields]
        before = {rec.id: {f: rec[f] for f in movers} for rec in self.sudo()} if movers else {}
        result = super().write(vals)
        # Odoo 19's field is work_location_id (there is no `work_location`):
        # a location move used to go unannounced to M29.
        # A09 audit M21-13 (E11): a direct position, branch, operating-unit or
        # band change moved the employee without telling M29.
        # An applied movement publishes its own, richer employee.moved.
        # A09 ERP audit X-F15: a department on its own is no longer a move, and
        # a bulk loader holds the event (hold_mover_event).
        if (
            movers
            and not self.env.context.get("fix_movement_event")
            and self.env.context.get(MOVER_EVENT_HOLD_KEY) is not _MOVER_EVENT_HOLD
        ):
            for rec in self:
                old = before.get(rec.id, {})
                srec = rec.sudo()
                changed = [f for f in movers if srec[f] != old.get(f)]
                if not changed:
                    continue
                payload = {
                    "employee_code": srec.employee_code or "",
                    "department": srec.department_id.name or "",
                    "changed_fields": changed,
                }
                # what the mover access review names (consume_employee_moved)
                for field, key in (("operating_unit_id", "branch"), ("position_id", "position")):
                    if field in changed:
                        payload["from_%s" % key] = old[field].name if old[field] else ""
                        payload["to_%s" % key] = srec[field].name if srec[field] else ""
                publish(self.env, "employee.moved", "hr.employee", rec.id, payload)
        return result


class FixOrgPosition(models.Model):
    """Organisation structure: reporting lines and position management."""

    _name = "fix.org.position"
    _description = "Organisation Position"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "name"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True, tracking=True)
    parent_id = fields.Many2one(
        "fix.org.position", string="Reports To", ondelete="restrict", index=True
    )
    employee_ids = fields.One2many("hr.employee", "position_id", string="Holders")
    grade = fields.Char(string="Grade", help="M57 compensation band reference")

    @api.constrains("parent_id")
    def _check_hierarchy(self):
        # Wired as a constraint (it was a plain method nobody called, so a
        # reporting-line loop could be saved).
        for rec in self:
            seen, node = {rec.id}, rec.parent_id
            while node:
                if node.id in seen:
                    raise ValidationError("Reporting line loop at %s" % rec.name)
                seen.add(node.id)
                node = node.parent_id


class FixEmploymentContract(models.Model):
    """Labour Act 2006 employment artefacts (P08-M01-T05, R06-M01-T02), rendered
    through the M24 document templates."""

    _name = "fix.employment.contract"
    _description = "Employment Contract"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "employee_id, joining_date desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(string="Contract Ref", compute="_compute_name", store=True)
    employee_id = fields.Many2one(
        "hr.employee", string="Employee", required=True, ondelete="cascade", index=True
    )
    contract_type = fields.Selection(
        [
            ("permanent", "Permanent"),
            ("probation", "Probation"),
            ("fixed_term", "Fixed Term"),
            ("part_time", "Part Time"),
        ],
        required=True,
        default="probation",
        tracking=True,
    )
    joining_date = fields.Date(required=True)
    probation_end = fields.Date(
        help="BLA s.4(8): probation is 6 months for clerical work and 3 months for others "
        "(a skilled worker's may be extended by 3 months)"
    )
    weekly_hours = fields.Float(
        string="Statutory Weekly Hours",
        default=48,
        required=True,
        help="s. 102: 48 hours/week ceiling",
    )
    basic_monthly = fields.Monetary(
        string="Basic Salary (Monthly)", currency_field="currency_id", required=True
    )
    house_rent = fields.Monetary(string="House Rent Allowance", currency_field="currency_id")
    medical_allowance = fields.Monetary(string="Medical Allowance", currency_field="currency_id")
    conveyance_allowance = fields.Monetary(
        string="Conveyance Allowance", currency_field="currency_id"
    )
    technical_allowance = fields.Monetary(
        string="Technical Skill / OEM Allowance", currency_field="currency_id"
    )
    other_allowance = fields.Monetary(string="Other Allowance", currency_field="currency_id")
    dearness_allowance = fields.Monetary(string="Dearness Allowance", currency_field="currency_id")
    adhoc_allowance = fields.Monetary(
        string="Ad-hoc / Interim Allowance", currency_field="currency_id"
    )
    # BLR 2015 r.19(4): the letter of appointment also states the wage scale
    # and the increment rate, and the other financial facilities. They are
    # terms of the contract (frozen with the others once it leaves draft) and
    # optional; the letter says NOT RECORDED for one left blank rather than
    # printing a blank line (A09 ERP audit M21-F2).
    wage_scale = fields.Char(
        string="Wage Scale",
        help="BLR 2015 r.19(4): the wage scale (pay grade and range) of the appointment",
    )
    increment_rate = fields.Char(
        string="Increment Rate",
        help="BLR 2015 r.19(4): the increment the wage scale carries, e.g. '5% of basic a year'",
    )
    other_facilities = fields.Text(
        string="Other Financial Facilities",
        help="BLR 2015 r.19(4): festival bonus, attendance allowance, gratuity and the like",
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("active", "Active"),
            ("expired", "Expired"),
            ("terminated", "Terminated"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )
    identity_document_note = fields.Char(
        string="Identity Store Ref",
        help="PII pointer: the NID/passport/biometric artefact lives in "
        "fix.identity.document (Z4 residency), referenced, never copied",
    )

    # M24 Document Engine Integration
    template_id = fields.Many2one(
        "fix.document.template",
        string="M24 Document Template",
        help="M24 governed document template for the employment contract (the letter of "
        "appointment of BLR 2015 r.19(4) is not a numbered form)",
    )
    document_id = fields.Many2one(
        "fix.document",
        string="Generated Contract Document",
        readonly=True,
        help="Governed contract artefact produced by M24 document engine",
    )
    # A09 ERP audit M21-F11: a "statutory density score" (a constant 52%) stood
    # here as a writable field and was printed on the contract. It measured
    # nothing: it is removed from the model, the form and the document.
    legal_signoff_state = fields.Selection(
        [
            ("pending", "Pending Signoff"),
            ("approved", "Approved by Legal"),
            ("rejected", "Changes Required"),
        ],
        default="pending",
        tracking=True,
        string="Legal Signoff",
    )
    signed_by_legal_counsel = fields.Char(string="Legal Counsel Signoff", tracking=True)

    @api.depends("employee_id.employee_code", "employee_id.name", "contract_type", "joining_date")
    def _compute_name(self):
        for rec in self:
            code = rec.employee_id.employee_code or (rec.employee_id.name or "EMP")
            year = rec.joining_date.year if rec.joining_date else fields.Date.today().year
            rec.name = f"CNT/{code}/{rec.contract_type.upper()}/{year}"

    # action_activate, action_terminate and the legal sign-off live in
    # fix_hr_contract_controls.py (A09 P0-b: guarded, routed, versioned).

    def action_generate_contract_document(self):
        """Generate the statutory employment contract through the M24 document
        engine (BLA 2006 s.5; the letter of appointment of BLR 2015 r.19(4) is
        not a numbered form - Form 6 is the identity card).

        Returns the generated fix.document records (one per contract; the
        loop used to `return` after the first contract of a multi-record call)."""
        docs = self.env["fix.document"]
        for rec in self:
            rec._validate_statutory()
            template = rec.template_id
            if not template:
                # Default to the employment contract template
                template = self.env["fix.document.template"].search(
                    [("document_type", "=", "contract")], limit=1
                )

            # Create ir.attachment containing the employment contract details
            content = (
                f"1000FiX SERVICES LTD - STATUTORY EMPLOYMENT CONTRACT\n"
                f"Statutory Basis: Bangladesh Labour Act 2006 (Act XLII of 2006) s.5 and "
                f"Bangladesh Labour Rules 2015 r.19(4) - the letter of appointment is not a "
                f"numbered form\n"
                f"Contract Ref: {rec.name}\n"
                f"Employee: {rec.employee_id.name} (Code: {rec.employee_id.employee_code or 'N/A'})\n"
                f"Type: {rec.contract_type}\n"
                f"Joining Date: {rec.joining_date}\n"
                f"Statutory Weekly Hours: {rec.weekly_hours} (s.102 cap)\n"
                f"Basic Monthly Salary: BDT {rec.basic_monthly:,.2f}\n"
                f"Statutory Citations: Bangladesh Labour Act 2006 (Act XLII of 2006) as amended 2026\n"
            ).encode()

            attachment = self.env["ir.attachment"].create(
                {
                    "name": f"Employment_Contract_{rec.name.replace('/', '_')}.txt",
                    "type": "binary",
                    "datas": base64.b64encode(content),
                    "res_model": "fix.employment.contract",
                    "res_id": rec.id,
                    "mimetype": "text/plain",
                }
            )

            doc = self.env["fix.document"].create(
                {
                    "name": f"Contract - {rec.employee_id.name} ({rec.contract_type})",
                    "name_bn": f"নিয়োগ চুক্তি - {rec.employee_id.name}",
                    "document_type": "contract",
                    "template_id": template.id if template else False,
                    "attachment_id": attachment.id,
                    "res_model": "fix.employment.contract",
                    "res_id": rec.id,
                    "isolation_tier": "T1",
                    "description": "Employment contract for %s (BLA 2006 s.5; BLR 2015 r.19(4))"
                    % rec.employee_id.name,
                }
            )
            rec.document_id = doc.id
            publish(
                self.env,
                "employment.contract.generated",
                "fix.employment.contract",
                rec.id,
                {
                    "contract": rec.name,
                    "document_id": doc.id,
                },
            )
            docs |= doc
        return docs


class FixLeaveType(models.Model):
    """Statutory leave catalogue (Bangladesh Labour Act 2006, SC-008, DoD-17)."""

    _name = "fix.leave.type"
    _description = "Leave Type"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "code"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    code = fields.Char(required=True, index=True)
    name = fields.Char(required=True)
    name_bn = fields.Char(string="Leave Name (Bengali)", help="DE-17")
    entitlement_days = fields.Integer(required=True)
    encashable = fields.Boolean(help="Annual leave is encashable at separation (s.118)")
    maternity = fields.Boolean()

    # DoD-17 statutory citation fields verified current
    is_statutory = fields.Boolean(
        string="Is Statutory",
        default=True,
        help="Whether this leave is an obligatory statutory entitlement under Bangladesh Labour Act",
    )
    carry_forward_limit = fields.Integer(
        string="Carry Forward Limit (Days)",
        default=0,
        help="Maximum days that can be carried forward (s. 117(7): 40 days for annual leave)",
    )
    labour_act_section = fields.Char(
        string="Labour Act Section",
        help="Governing statutory section (e.g. Section 115, Section 116, Section 117)",
    )
    legal_citation = fields.Text(
        string="Legal Citation",
        help="Explicit statutory citation and formula under Bangladesh Labour Act 2006",
    )
    amendment_ref = fields.Char(
        string="Amendment Reference",
        default="Labour (Amendment) Act 2013, 2018, 2026",
        help="Latest amendments verified applicable",
    )
    verified_on = fields.Date(
        string="Verified On",
        # A09 ERP audit M21-F12: a default of today stamped every new type
        # "verified" with nobody recorded as the verifier. The date is set by
        # Verify Citation, which records who verified.
        default=False,
        help="Date statutory citation verified current (DoD-17). Set by Verify Citation, "
        "which records who verified it.",
    )
    # B2b seeds an unpaid leave type and payroll reads this flag: an approved
    # day of an unpaid type reduces pay.
    is_unpaid = fields.Boolean(
        string="Unpaid Leave",
        default=False,
        help="Approved days of this type reduce pay",
    )

    def action_validate_statutory(self):
        """The entitlement must be at least the statutory floor in force."""
        floors = statutory_leave_floors(self.env)
        for rec in self:
            if rec.is_statutory:
                floor = floors.get(rec.code)
                if floor and rec.entitlement_days < floor:
                    raise ValidationError(
                        "%s entitlement below the statutory floor (%d days)" % (rec.code, floor)
                    )


class FixLeaveRequest(models.Model):
    """Leave and absence management on the statutory floors."""

    _name = "fix.leave.request"
    _description = "Leave Request"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date_from desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    employee_id = fields.Many2one("hr.employee", required=True, index=True)
    leave_type_id = fields.Many2one("fix.leave.type", required=True)
    date_from = fields.Date(required=True)
    date_to = fields.Date(required=True)
    days = fields.Integer(compute="_compute_days", store=True)
    reason = fields.Text()
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("submitted", "Submitted"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )

    # No name field: without this, chatter, notifications and pickers showed
    # the raw "fix.leave.request,124" (sweep audit D-A09-04).
    @api.depends("employee_id", "leave_type_id", "date_from", "date_to")
    def _compute_display_name(self):
        for rec in self:
            label = " · ".join(
                part for part in (rec.employee_id.name, rec.leave_type_id.name) if part
            ) or self.env._("Leave Request")
            if rec.date_from and rec.date_to:
                label = "%s (%s – %s)" % (label, rec.date_from, rec.date_to)
            rec.display_name = label

    @api.depends("date_from", "date_to")
    def _compute_days(self):
        for rec in self:
            if rec.date_from and rec.date_to and rec.date_to >= rec.date_from:
                rec.days = (
                    fields.Date.to_date(rec.date_to) - fields.Date.to_date(rec.date_from)
                ).days + 1
            else:
                rec.days = 0

    def action_approve(self):
        for rec in self:
            rec.leave_type_id.action_validate_statutory()
            # Entitlements are DAYS per calendar year (BLA s.115/116: "in a
            # calendar year"). The former search_count counted approved
            # REQUESTS across all years, so 3 x 5-day casual leaves (15 days)
            # passed a 10-day entitlement, and a second year was over-blocked.
            year = rec.date_from.year
            taken = sum(
                self.search(
                    [
                        ("id", "!=", rec.id),
                        ("employee_id", "=", rec.employee_id.id),
                        ("leave_type_id", "=", rec.leave_type_id.id),
                        ("state", "=", "approved"),
                        ("date_from", ">=", date(year, 1, 1)),
                        ("date_from", "<=", date(year, 12, 31)),
                    ]
                ).mapped("days")
            )
            if taken + rec.days > rec.leave_type_id.entitlement_days:
                raise UserError(
                    "Entitlement exhausted: %d approved + %d requested > %d days in %d"
                    % (taken, rec.days, rec.leave_type_id.entitlement_days, year)
                )
            rec.state = "approved"
            publish(
                self.env,
                "leave.approved",
                "fix.leave.request",
                rec.id,
                {"employee": rec.employee_id.name, "days": rec.days},
            )


class HrVersionCdCoreExt(models.Model):
    """hr.version extension — marital selection extension point.

    EMP-MIG-RPT-001 §3.5: marital is required but legacy extracts (the 504-row
    real-employee load of 2026-11) carry no marital data. Odoo 19 owns the
    selection on hr.version (hr.employee delegates via _inherits), so the
    honest 'unrecorded' value is added here; Wave-4 enrichment replaces it
    with the sourced value.
    """

    _inherit = "hr.version"

    @api.model
    def _get_marital_status_selection(self):
        return [
            *super()._get_marital_status_selection(),
            ("unspecified", "Unrecorded (migration default)"),
        ]
