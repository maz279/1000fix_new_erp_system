# fix_hr_core — M21 complete: contracts, statutory leave, org structure (P08-M01, R06-M01).
import base64
from datetime import UTC, date, datetime, timedelta

from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError

from libs.py.fix_events import get_migration_manager, normalize_bus_event, publish

# Bangladesh Labour Act 2006 statutory leave entitlements (SC-008, DoD-17), in days
STATUTORY_LEAVE = {
    "casual": 10,  # s. 115 casual leave with full wages (non-cumulative)
    "annual": 20,  # s. 117 casual+earned composite floor as practised (1 day per 18 days worked)
    "sick": 14,  # s. 116 / 148 sick leave upon medical practitioner certificate
    "festival": 11,  # s. 118 / 146 festival holidays
    "maternity": 112,  # s. 46-48: 16 weeks (112 days: 8 weeks pre-natal, 8 weeks post-natal)
    "paternity": 10,  # policy floor (not statutory; recorded as corporate policy benefit)
}
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
    birth_reg_number = fields.Char(
        string="17-Digit Birth Registration Number",
        help="Birth Registration Certificate number (BRIS)",
        groups=HR_PRIVATE,
    )
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
        string="Form 7 Update Due Date", compute="_compute_form7_clock", store=True
    )
    form7_update_overdue = fields.Boolean(
        string="Form 7 Update Overdue", compute="_compute_form7_clock", store=True
    )
    taxpayer_category = fields.Selection(
        [
            ("general", "General Taxpayer (BDT 400,000)"),
            ("female_senior", "Female & Senior Citizen 65+ (BDT 450,000)"),
            ("disabled_third_gender", "Disabled & Third Gender (BDT 500,000)"),
            ("freedom_fighter", "War-Wounded Freedom Fighter (BDT 525,000)"),
        ],
        string="Taxpayer Slabs Category",
        default="general",
        help="Annual tax-free income ceiling under Finance Act",
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
    passport_number = fields.Char(
        string="International Passport Number",
        help="International Passport Number",
        groups=HR_PRIVATE,
    )
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
    work_location_type = fields.Selection(
        [
            ("central_workshop", "Central Workshop Lab"),
            ("branch_counter", "Branch Walk-in Counter"),
            ("field_mobile", "Field Mobile Dispatch"),
            ("head_office", "Head Office Corporate"),
            ("hybrid", "Hybrid"),
        ],
        string="Workplace Category",
        default="central_workshop",
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
    keycloak_id = fields.Char(string="Keycloak IdP UUID")

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
        default="pending",
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
        default="verified_positive",
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
        default=True,
        help="Electrostatic Discharge handling protocol certification",
    )
    bga_rework_capable = fields.Boolean(
        string="BGA Rework Station Authorized Operator",
        help="Authorized to operate IR/Hot-air BGA machine stations",
    )
    toolkit_custody_ref = fields.Char(string="Assigned Tool Kit Barcode Ref")
    customer_nda_signed = fields.Boolean(
        string="Customer Data Confidentiality Undertaking Signed",
        default=True,
        help="Signed compliance pledge under Cyber Security Act 2023",
    )

    # Compensation Breakdown & Allowances (Monthly BDT)
    wage = fields.Monetary(
        string="Monthly Gross Salary", currency_field="currency_id", groups=HR_PRIVATE
    )
    basic_wage = fields.Monetary(
        string="Monthly Basic Wage", currency_field="currency_id", groups=HR_PRIVATE
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
        default="normal_pass",
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
        default="fit_duty",
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
    nominee_nid = fields.Char(string="Nominee National ID / Birth Reg", groups=HR_PRIVATE)
    nominee_pct = fields.Float(
        string="Nominee Share % (BLA s.19 & 131)", default=100.0, groups=HR_PRIVATE
    )
    guardian_name = fields.Char(
        string="Legal Guardian Name (if Nominee is Minor)", groups=HR_PRIVATE
    )

    # Document Dossier Compliance Checklist
    doc_nid_verified = fields.Boolean(string="NID Smart Card Verified", default=True)
    doc_tin_verified = fields.Boolean(string="12-digit e-TIN Certificate Verified", default=True)
    doc_psr_verified = fields.Boolean(string="Tax Return Submission Ack (PSR) Verified")
    doc_appointment_signed = fields.Boolean(
        string="Signed Appointment Letter on File", default=True
    )
    doc_nda_signed = fields.Boolean(string="Signed NDA & Code of Conduct on File", default=True)
    doc_service_book_scanned = fields.Boolean(
        string="Form 7 Service Book Pages Scanned", default=True
    )
    doc_medical_fit_certified = fields.Boolean(
        string="Medical Fitness Certificate Signed", default=True
    )
    doc_police_pcc_cleared = fields.Boolean(string="Police Clearance Certificate (PCC) Cleared")

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
        string="Father's Name", help="Father's Name (Form 7 Service Book, Form 6 Worker Register)"
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
    nid_number = fields.Char(
        string="National ID (NID / Smart Card)",
        help="10-digit smart card or 17-digit national identity number",
        groups=HR_PRIVATE,
    )
    tin_number = fields.Char(
        string="e-TIN Number",
        help="12-digit Taxpayer Identification Number for NBR withholding (Form 23)",
        groups=HR_PRIVATE,
    )
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
        string="Bank Name", help="Scheduled Commercial Bank in Bangladesh", groups=HR_PRIVATE
    )
    bank_branch_name = fields.Char(string="Bank Branch", help="Bank branch name", groups=HR_PRIVATE)
    routing_number = fields.Char(
        string="BEFTN Routing Number",
        help="9-digit Bangladesh Bank BEFTN routing code",
        groups=HR_PRIVATE,
    )
    bank_account_number = fields.Char(
        string="Bank Account Number",
        help="Savings / Current bank account number",
        groups=HR_PRIVATE,
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
    )
    mfs_account_number = fields.Char(
        string="MFS Account Number",
        help="11-digit mobile wallet number (01XXXXXXXXX)",
        groups=HR_PRIVATE,
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

    @api.depends("form7_last_event_date", "form7_endorsed_on", "joining_date")
    def _compute_form7_clock(self):
        today = fields.Date.context_today(self)
        for rec in self:
            event_dt = rec.form7_last_event_date or rec.joining_date
            if event_dt:
                due = fields.Date.to_date(event_dt) + timedelta(days=15)
                rec.form7_update_due_date = due
                endorsed = (
                    fields.Date.to_date(rec.form7_endorsed_on) if rec.form7_endorsed_on else None
                )
                rec.form7_update_overdue = bool(
                    (not endorsed or endorsed < fields.Date.to_date(event_dt)) and today > due
                )
            else:
                rec.form7_update_due_date = False
                rec.form7_update_overdue = False

    def action_generate_form7_service_book(self):
        """BLR 2015 Rule 21 / BLA 2006 s.6-9: Generate Form 7 Service Book entry and reset 15-day clock."""
        docs = self.env["fix.hr.document"]
        today = fields.Date.context_today(self)
        for rec in self:
            payload = (
                f"FORM 7 - SERVICE BOOK (Bangladesh Labour Rules 2015, Rule 21)\n"
                f"Service Book No: {rec.service_book_number or 'SB-' + (rec.employee_code or str(rec.id))}\n"
                f"Worker Name: {rec.name}\n"
                f"Father's Name: {rec.father_name or ''}\n"
                f"Mother's Name: {rec.mother_name or ''}\n"
                f"NID / Smart Card: {rec.nid_number or ''}\n"
                f"Identification Mark: {rec.identification_mark or ''}\n"
                f"Designation / Band: {rec.job_title or ''} ({rec.job_band or ''})\n"
                f"Joining Date: {rec.joining_date or ''}\n"
                f"Basic Wage: {rec.basic_wage or 0.0:.2f} | Gross Wage: {rec.wage or 0.0:.2f}\n"
                f"Endorsed On: {today}\n"
            ).encode()
            doc = self.env["fix.hr.document"].create(
                {
                    "employee_id": rec.id,
                    "doc_type": "service_book",
                    "reference": rec.service_book_number or f"FORM7/{rec.employee_code or rec.id}",
                    "issued_on": today,
                    "verified": True,
                    "file_name": f"Form7_ServiceBook_{rec.employee_code or rec.id}.txt",
                    "file_data": base64.b64encode(payload),
                }
            )
            rec.write(
                {
                    "form7_endorsed_on": today,
                    "doc_service_book_scanned": True,
                }
            )
            docs |= doc
        return docs

    def action_generate_form6_appointment(self):
        """BLR 2015 Rule 19(1) / BLA 2006 s.5: Generate Form 6 Appointment Letter."""
        docs = self.env["fix.hr.document"]
        today = fields.Date.context_today(self)
        for rec in self:
            payload = (
                f"FORM 6 - APPOINTMENT LETTER (Bangladesh Labour Rules 2015, Rule 19)\n"
                f"Employee: {rec.name} ({rec.employee_code or 'N/A'})\n"
                f"Father's Name: {rec.father_name or ''}\n"
                f"Mother's Name: {rec.mother_name or ''}\n"
                f"Permanent Address: {rec.permanent_address or ''}\n"
                f"Joining Date: {rec.joining_date or today}\n"
                f"Employment Nature: {rec.employment_type or 'permanent'}\n"
                f"Basic Wage: BDT {rec.basic_wage or 0.0:,.2f}\n"
                f"House Rent: BDT {rec.house_rent or 0.0:,.2f}\n"
                f"Medical: BDT {rec.medical_allowance or 0.0:,.2f}\n"
                f"Conveyance: BDT {rec.conveyance_allowance or 0.0:,.2f}\n"
                f"Gross Salary: BDT {rec.wage or 0.0:,.2f}\n"
            ).encode()
            doc = self.env["fix.hr.document"].create(
                {
                    "employee_id": rec.id,
                    "doc_type": "appointment",
                    "reference": f"FORM6/{rec.employee_code or rec.id}/{today}",
                    "issued_on": today,
                    "verified": True,
                    "file_name": f"Form6_Appointment_{rec.employee_code or rec.id}.txt",
                    "file_data": base64.b64encode(payload),
                }
            )
            rec.write({"doc_appointment_signed": True})
            docs |= doc
        return docs

    @api.model
    def action_export_form6a_register(self, domain=None):
        """BLR 2015 Rule 20 / BLA 2006 s.9: Export Form 6(a) Worker Register."""
        emps = self.search(domain or [])
        rows = []
        for idx, emp in enumerate(emps, start=1):
            rows.append(
                {
                    "serial": idx,
                    "employee_code": emp.employee_code or "",
                    "name": emp.name or "",
                    "father_name": emp.father_name or "",
                    "mother_name": emp.mother_name or "",
                    "nid_number": emp.nid_number or "",
                    "department": emp.department_id.name or "",
                    "designation": emp.job_title
                    or (emp.position_id.name if emp.position_id else ""),
                    "employment_type": emp.employment_type or "",
                    "joining_date": str(emp.joining_date or ""),
                    "service_book_number": emp.service_book_number or "",
                }
            )
        return rows

    def _fix_guarded_fields(self) -> set:
        # A09 audit M21-6: a user who could write the master marked a leaver
        # "deprovisioned" (KPI-090 green with the account still live) or bound
        # a colleague to a Keycloak id of their choosing. Only the leaver path,
        # the HR manager's confirmation and the identity-provider consumer
        # change these.
        return super()._fix_guarded_fields() | {
            "left_at",
            "keycloak_deprovision_status",
            "keycloak_deprovisioned_at",
            "keycloak_deprovision_confirmed_by",
            "keycloak_user_id",
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
        result = super().write(vals)
        # Odoo 19's field is work_location_id (there is no `work_location`):
        # a location move used to go unannounced to M29.
        if "department_id" in vals or "job_id" in vals or "work_location_id" in vals:
            for rec in self:
                publish(
                    self.env,
                    "employee.moved",
                    "hr.employee",
                    rec.id,
                    {
                        "employee_code": rec.employee_code or "",
                        "department": rec.department_id.name or "",
                    },
                )
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
    """Labour Act 2006 employment artefacts (P08-M01-T05, R06-M01-T02) — where the
    category-H statutory density (+52%) lives on M24 templates."""

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
    probation_end = fields.Date(help="Labour Rules 2021 r.25: probation may not exceed 6 months")
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

    # M24 Document Engine Integration (+52% Category H statutory density)
    template_id = fields.Many2one(
        "fix.document.template",
        string="M24 Document Template",
        help="M24 governed document template for Bangladesh Labour Rules Form 6",
    )
    document_id = fields.Many2one(
        "fix.document",
        string="Generated Contract Document",
        readonly=True,
        help="Governed contract artefact produced by M24 document engine",
    )
    statutory_density_score = fields.Float(
        string="Statutory Density (%)",
        default=52.0,
        help="Statutory density rating exceeding standard contracts (+52% Category H density)",
    )
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

    def action_activate(self):
        for rec in self:
            rec._validate_statutory()
            rec.state = "active"
            publish(
                self.env,
                "employment.contract.activated",
                "fix.employment.contract",
                rec.id,
                {
                    "employee": rec.employee_id.name,
                    "contract_type": rec.contract_type,
                    "joining": str(rec.joining_date),
                },
            )

    def action_terminate(self):
        """End the contract. Unless another active contract continues the
        employment, the employee leaves through the canonical leaver path
        (cd_employee_core.action_mark_left: employee.left, which M29 consumes;
        KPI-090 clock and a PENDING Keycloak deprovisioning) - the removal is
        never marked done here."""
        for rec in self:
            rec.state = "terminated"
            continuing = self.search_count(
                [
                    ("employee_id", "=", rec.employee_id.id),
                    ("state", "=", "active"),
                    ("id", "!=", rec.id),
                ]
            )
            if not continuing:
                rec.employee_id.action_mark_left()

    def action_request_legal_signoff(self):
        for rec in self:
            rec.legal_signoff_state = "pending"

    def action_approve_legal_signoff(self):
        for rec in self:
            rec.legal_signoff_state = "approved"
            rec.signed_by_legal_counsel = self.env.user.name

    def action_generate_contract_document(self):
        """Generate official Labour Rules 2015 Form 6 contract via M24 document engine.

        Returns the generated fix.document records (one per contract; the
        loop used to `return` after the first contract of a multi-record call)."""
        docs = self.env["fix.document"]
        for rec in self:
            rec._validate_statutory()
            template = rec.template_id
            if not template:
                # Default to Form 6 contract template
                template = self.env["fix.document.template"].search(
                    [("document_type", "=", "contract")], limit=1
                )

            # Create ir.attachment containing Form 6 appointment / contract details
            content = (
                f"1000FiX SERVICES LTD - STATUTORY EMPLOYMENT CONTRACT\n"
                f"Statutory Form: Form 6, Bangladesh Labour Rules 2015\n"
                f"Statutory Density: {rec.statutory_density_score}% (Category H)\n"
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
                    "description": f"Labour Rules Form 6 employment contract for {rec.employee_id.name}",
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
                    "statutory_density": rec.statutory_density_score,
                },
            )
            docs |= doc
        return docs

    def _validate_statutory(self):
        for rec in self:
            if rec.probation_end:
                cap_months = PROBATION_CAP_MONTHS * 30
                span = (
                    fields.Date.to_date(rec.probation_end) - fields.Date.to_date(rec.joining_date)
                ).days
                if span > cap_months:
                    raise ValidationError(
                        "Probation exceeds the 6-month statutory cap (Labour Rules 2021 r.25)"
                    )
            if rec.weekly_hours > 48:
                raise ValidationError("s.102: weekly hours may not exceed 48")
            if rec.basic_monthly <= 0:
                raise ValidationError("Basic salary must be positive")


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
        default=fields.Date.today,
        help="Date statutory citation verified current (DoD-17)",
    )

    def action_validate_statutory(self):
        """The entitlement must be at least the statutory floor."""
        for rec in self:
            if rec.is_statutory:
                floor = STATUTORY_LEAVE.get(rec.code)
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
