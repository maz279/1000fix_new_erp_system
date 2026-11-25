# fix_candidate_biodata — M58: the full candidate biodata (18 Nov 2026).
#
# The Candidate Biodata form held twelve fields: a name, an email, a phone, a
# branch, a source, a date of birth, an NID and consent. A candidate's
# education, training, work history, languages, referees, family and the
# documents that evidence them (CV, certificates, transcripts, testimonials,
# release letters...) could not be recorded anywhere, so screening and
# background verification ran on paper. Here:
#   * header fields grouped by the stage at which they may be asked
#     (application, screening, pre-offer, joining). Sensitive data (religion,
#     blood group, marital status, spouse, family and nominees) is refused
#     before the offer stage: data minimisation under the Bangladesh Personal
#     Data Protection Ordinance 2025, which treats religion and health as
#     sensitive and forbids collecting data unrelated to the purpose;
#   * eight repeating registers, each an add-more-lines grid on the form;
#   * evidence rows (education, training, experience, documents) carry their
#     own scanned file, SHA-256 and a verification decided by a Background
#     Verifier who did not key or upload the row (FR-TAO-024 pattern);
#   * a discrepancy or a rejected document blocks the offer stage and the hire;
#   * the hire carries everything into the M21 employee registers
#     (fix.hr.education / experience / document / dependant) with the
#     verifier's decision, and pre-fills the pre-boarding checklist;
#   * the retention cron erases every line and file with the candidate.
import base64
import hashlib
import re

from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError

from .fix_talent import _is_recruiter, _require_recruiter_or_hiring_manager

VERIFIER = "cd_talent.group_background_verifier"

DIVISIONS = [
    ("dhaka", "Dhaka"),
    ("chattogram", "Chattogram"),
    ("rajshahi", "Rajshahi"),
    ("khulna", "Khulna"),
    ("barishal", "Barishal"),
    ("sylhet", "Sylhet"),
    ("rangpur", "Rangpur"),
    ("mymensingh", "Mymensingh"),
]

# Bangladesh qualification levels, ordered (the rank picks the highest).
EDUCATION_LEVELS = [
    ("below_ssc", "Below SSC (JSC / JDC / Class 8)"),
    ("ssc", "SSC / Dakhil / O-Level"),
    ("ssc_voc", "SSC (Vocational) / Dakhil (Vocational)"),
    ("ntvqf", "NTVQF / BNQF Skills Certificate (Level 1-6)"),
    ("hsc", "HSC / Alim / A-Level"),
    ("hsc_voc", "HSC (Vocational) / HSC (BM) / Diploma in Commerce"),
    ("diploma", "Diploma (Engineering / Textile / Agriculture / Medical Tech)"),
    ("bachelor_pass", "Bachelor (Pass) / Degree / Fazil"),
    ("bachelor_hons", "Bachelor (Honours) / B.Sc. Engineering / BBA"),
    ("masters", "Masters / MBA / Kamil"),
    ("mphil", "M.Phil."),
    ("phd", "Ph.D. / Doctorate"),
    ("other", "Other / Foreign Equivalent"),
]
LEVEL_RANK = {key: i for i, (key, _l) in enumerate(EDUCATION_LEVELS)}
LEVEL_RANK["other"] = -1

BOARDS = [
    ("dhaka", "Dhaka Board"),
    ("rajshahi", "Rajshahi Board"),
    ("cumilla", "Cumilla Board"),
    ("jashore", "Jashore Board"),
    ("chattogram", "Chattogram Board"),
    ("barishal", "Barishal Board"),
    ("sylhet", "Sylhet Board"),
    ("dinajpur", "Dinajpur Board"),
    ("mymensingh", "Mymensingh Board"),
    ("madrasah", "Madrasah Board"),
    ("technical", "Technical Board (BTEB)"),
    ("university", "University (public / private / National University)"),
    ("foreign", "Foreign Board / University"),
    ("other", "Other"),
]

RESULT_TYPES = [
    ("gpa5", "GPA (out of 5.00)"),
    ("cgpa4", "CGPA (out of 4.00)"),
    ("first_division", "First Division"),
    ("second_division", "Second Division"),
    ("third_division", "Third Division"),
    ("first_class", "First Class"),
    ("second_class", "Second Class"),
    ("third_class", "Third Class"),
    ("grade", "Grade / Marks (%)"),
    ("pass", "Pass"),
    ("appeared", "Appeared (result awaited)"),
]
# the scale a numeric result is read against; the others carry no number
RESULT_SCALE = {"gpa5": 5.0, "cgpa4": 4.0, "grade": 100.0}

PROFICIENCY = [
    ("basic", "Basic"),
    ("working", "Working"),
    ("fluent", "Fluent"),
    ("native", "Native"),
]

VERIFICATION = [
    ("pending", "Pending Verification"),
    ("verified", "Verified"),
    ("discrepancy", "Discrepancy"),
]

CANDIDATE_DOCUMENT_TYPES = [
    ("cv", "CV / Resume"),
    ("cover_letter", "Cover Letter"),
    ("photo", "Photograph (passport size)"),
    ("nid", "National ID (NID)"),
    ("birth_cert", "Birth Registration Certificate"),
    ("passport", "Passport"),
    ("academic_cert", "Academic Certificate"),
    ("transcript", "Transcript / Mark Sheet"),
    ("testimonial", "Testimonial"),
    ("character_cert", "Character Certificate"),
    ("training_cert", "Training / NTVQF Certificate"),
    ("professional_cert", "Professional / OEM Certification"),
    ("experience_letter", "Experience Letter"),
    ("release_letter", "Release / Clearance Letter"),
    ("payslip", "Last Payslip / Salary Certificate"),
    ("driving_licence", "BRTA Driving Licence"),
    ("police_clearance", "Police Clearance Certificate (PCC)"),
    ("medical_fitness", "Medical Fitness Certificate (BLA s.37)"),
    ("tin_cert", "e-TIN Certificate"),
    ("bank_proof", "Bank Cheque Leaf / MFS Statement"),
    ("nominee_nid", "Nominee NID & Photo"),
    ("other", "Other"),
]
# documents that may only be asked once the candidate reached the offer stage
JOINING_DOCUMENTS = {"bank_proof", "nominee_nid", "tin_cert", "medical_fitness"}

# candidate document -> M21 employee dossier type (fix.hr.document.doc_type)
HR_DOCUMENT_TYPE = {
    "cv": "cv",
    "cover_letter": "other_candidate",
    "photo": "photo",
    "nid": "nid_smart",
    "birth_cert": "birth_cert",
    "passport": "passport",
    "academic_cert": "degree_cert",
    "transcript": "transcript",
    "testimonial": "testimonial",
    "character_cert": "character_cert",
    "training_cert": "vocational",
    "professional_cert": "oem_cert",
    "experience_letter": "experience",
    "release_letter": "release_letter",
    "payslip": "payslip_prior",
    "driving_licence": "driving_lic",
    "police_clearance": "police_pcc",
    "medical_fitness": "medical_fit",
    "tin_cert": "tin_cert",
    "bank_proof": "bank_cheque",
    "nominee_nid": "nominee_nid",
    "other": "other_candidate",
}
# candidate document -> pre-boarding checklist item (fix.preboarding.document)
PREBOARDING_TYPE = {
    "nid": "nid",
    "photo": "photo",
    "academic_cert": "academic",
    "experience_letter": "experience",
    "release_letter": "experience",
    "bank_proof": "bank",
    "birth_cert": "age_proof",
    "medical_fitness": "medical",
}

# Sensitive personal data asked only from a candidate at the offer stage.
SENSITIVE_FIELDS = ("religion", "blood_group", "marital_status", "spouse_name")
LATE_STATES = ("offered", "hired")
DIGITS = re.compile(r"^\d+$")
_ADDRESS_PARTS = ("address", "upazila", "district", "division", "post_code")
_PRESENT = tuple("present_%s" % p for p in _ADDRESS_PARTS)


def _sha256(b64):
    if not b64:
        return False
    raw = base64.b64decode(b64 if isinstance(b64, bytes | str) else b"")
    return hashlib.sha256(raw).hexdigest()


# ===================================================================== header
class FixCandidateBiodata(models.Model):
    _inherit = "fix.candidate"

    # ---- application --------------------------------------------------------
    name_bn = fields.Char(string="Full Name (Bangla)")
    photo = fields.Image(string="Photograph", max_width=512, max_height=512, attachment=True)
    alt_phone = fields.Char(string="Alternative Mobile")
    applied_on = fields.Date(string="Applied On", default=fields.Date.context_today)
    present_address = fields.Char(string="Present Address (house / road / village)")
    present_upazila = fields.Char(string="Present Upazila / Thana")
    present_district = fields.Char(string="Present District")
    present_division = fields.Selection(DIVISIONS, string="Present Division")
    present_post_code = fields.Char(string="Present Post Code")
    current_employer = fields.Char(string="Current / Last Employer")
    current_designation = fields.Char(string="Current / Last Designation")
    career_summary = fields.Text(string="Career Objective / Summary")
    key_skills = fields.Text(string="Key Skills (summary)")
    cv_file = fields.Binary(string="CV / Resume", attachment=True, copy=False)
    cv_filename = fields.Char(string="CV File Name", copy=False)
    declaration_accepted = fields.Boolean(
        string="Declaration of Truth Accepted",
        help="The candidate declares that the information and documents given are true "
        "and complete, and that a false statement ends the application or employment.",
    )
    declaration_on = fields.Datetime(string="Declaration Recorded On", readonly=True, copy=False)
    talent_pool_consent = fields.Boolean(
        string="Consent to Keep in Talent Pool",
        help="A separate consent from processing for this application: an unsuccessful "
        "candidate's record is then kept for the longer talent-pool period.",
    )
    highest_education_level = fields.Selection(
        EDUCATION_LEVELS,
        string="Highest Qualification",
        compute="_compute_education_summary",
        store=True,
    )
    total_experience_years = fields.Float(
        string="Total Experience (years)",
        compute="_compute_experience_summary",
        store=True,
        digits=(6, 1),
    )

    # ---- screening ----------------------------------------------------------
    currency_id = fields.Many2one(
        "res.currency",
        default=lambda self: self.env.ref("base.BDT", raise_if_not_found=False)
        or self.env.company.currency_id,
    )
    current_salary = fields.Monetary(
        string="Current Gross Salary (monthly)", groups="cd_talent.group_talent"
    )
    expected_salary = fields.Monetary(
        string="Expected Gross Salary (monthly)", groups="cd_talent.group_talent"
    )
    notice_period_days = fields.Integer(string="Notice Period (days)")
    earliest_joining_date = fields.Date(string="Earliest Joining Date")
    preferred_locations = fields.Char(string="Preferred Work Locations")
    willing_to_relocate = fields.Boolean(string="Willing to Relocate")
    willing_to_travel = fields.Boolean(string="Willing to Travel / Field Work")
    shift_work_ok = fields.Boolean(string="Can Work Shifts / Nights")
    owns_motorcycle = fields.Boolean(string="Owns a Motorcycle / Bicycle")
    driving_licence_held = fields.Boolean(string="Holds a Driving Licence")
    driving_licence_no = fields.Char(string="Driving Licence No.")
    driving_licence_class = fields.Selection(
        [
            ("motorcycle", "Motorcycle"),
            ("light", "Light Vehicle"),
            ("medium", "Medium Vehicle"),
            ("heavy", "Heavy Vehicle"),
            ("professional", "Professional"),
        ],
        string="Driving Licence Class",
    )
    driving_licence_expiry = fields.Date(string="Driving Licence Expiry")
    previously_applied = fields.Boolean(string="Applied to 1000 FiX Before")
    previously_employed = fields.Boolean(string="Worked at 1000 FiX Before")
    previous_employee_code = fields.Char(string="Previous Employee ID")
    relative_in_company = fields.Boolean(string="Relative Works at 1000 FiX")
    relative_details = fields.Char(
        string="Relative's Name, Relation and Branch", help="Declared for conflict of interest."
    )
    accommodation_needs = fields.Text(
        string="Accommodation Needs (voluntary)",
        help="Any adjustment the candidate asks for at interview or at work. Voluntary.",
    )

    # ---- pre-offer (shortlisted) ---------------------------------------------
    father_name = fields.Char(string="Father's Name")
    mother_name = fields.Char(string="Mother's Name")
    nationality_id = fields.Many2one(
        "res.country",
        string="Nationality",
        default=lambda self: self.env.ref("base.bd", raise_if_not_found=False),
    )
    # M58-F4: birth_reg_number / passport_number are declared in
    # fix_candidate_identity.py - the Bangladesh-resident store holds them.
    permanent_same_as_present = fields.Boolean(string="Permanent Address Same as Present")
    permanent_address = fields.Char(string="Permanent Address (village / road / post office)")
    permanent_upazila = fields.Char(string="Permanent Upazila / Thana")
    permanent_district = fields.Char(string="Permanent District")
    permanent_division = fields.Selection(DIVISIONS, string="Permanent Division")
    permanent_post_code = fields.Char(string="Permanent Post Code")
    criminal_record = fields.Selection(
        [("none", "No conviction declared"), ("declared", "Conviction declared")],
        string="Criminal Record Declaration",
        groups="cd_talent.group_talent",
    )
    criminal_record_details = fields.Text(
        string="Conviction Details", groups="cd_talent.group_talent"
    )

    # ---- joining particulars (offer stage onward; sensitive) ------------------
    sex = fields.Selection(
        [("male", "Male"), ("female", "Female"), ("third_gender", "Third Gender (Hijra)")],
        string="Gender",
    )
    marital_status = fields.Selection(
        [
            ("single", "Single"),
            ("married", "Married"),
            ("widower", "Widowed"),
            ("divorced", "Divorced"),
            ("separated", "Separated"),
        ],
        string="Marital Status",
    )
    spouse_name = fields.Char(string="Spouse's Name")
    religion = fields.Selection(
        [
            ("islam", "Islam"),
            ("hinduism", "Hinduism"),
            ("buddhism", "Buddhism"),
            ("christianity", "Christianity"),
            ("other", "Other"),
            ("undisclosed", "Prefer not to say"),
        ],
        string="Religion",
    )
    blood_group = fields.Selection(
        [
            ("a_pos", "A+"),
            ("a_neg", "A-"),
            ("b_pos", "B+"),
            ("b_neg", "B-"),
            ("ab_pos", "AB+"),
            ("ab_neg", "AB-"),
            ("o_pos", "O+"),
            ("o_neg", "O-"),
        ],
        string="Blood Group",
    )
    identification_mark = fields.Char(
        string="Identification Mark", help="Form 7 service book item (BLA 2006 s.7)."
    )

    # ---- the repeating registers ---------------------------------------------
    education_ids = fields.One2many(
        "fix.candidate.education", "candidate_id", string="Academic Qualifications"
    )
    training_ids = fields.One2many(
        "fix.candidate.training", "candidate_id", string="Training & Certifications"
    )
    experience_ids = fields.One2many(
        "fix.candidate.experience", "candidate_id", string="Employment History"
    )
    language_ids = fields.One2many("fix.candidate.language", "candidate_id", string="Languages")
    skill_ids = fields.One2many("fix.candidate.skill", "candidate_id", string="Skills")
    reference_ids = fields.One2many("fix.candidate.reference", "candidate_id", string="Referees")
    family_ids = fields.One2many(
        "fix.candidate.family", "candidate_id", string="Family, Emergency Contacts & Nominees"
    )
    document_ids = fields.One2many(
        "fix.candidate.document", "candidate_id", string="Documents & Attachments"
    )
    evidence_pending = fields.Integer(
        string="Evidence Awaiting Verification", compute="_compute_evidence_counts"
    )
    evidence_discrepancies = fields.Integer(
        string="Evidence Discrepancies", compute="_compute_evidence_counts"
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"declaration_on"}

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if any(r.state not in LATE_STATES for r in self) or not self:
            # asked only from a candidate who reached the offer stage
            locked |= set(SENSITIVE_FIELDS)
        if any(r.state == "hired" or r.erased for r in self):
            locked |= {"birth_reg_number", "passport_number"}
        return locked

    # ---- computes -------------------------------------------------------------
    @api.depends("education_ids.level")
    def _compute_education_summary(self):
        for rec in self:
            levels = [e.level for e in rec.education_ids if e.level]
            rec.highest_education_level = (
                max(levels, key=lambda k: LEVEL_RANK.get(k, -1)) if levels else False
            )

    @api.depends("experience_ids.duration_years")
    def _compute_experience_summary(self):
        for rec in self:
            rec.total_experience_years = round(sum(rec.experience_ids.mapped("duration_years")), 1)

    def _fix_evidence_lines(self):
        self.ensure_one()
        rec = self.sudo()
        return rec.education_ids, rec.training_ids, rec.experience_ids, rec.document_ids

    def _compute_evidence_counts(self):
        for rec in self:
            pending = discrepancy = 0
            for lines in rec._fix_evidence_lines():
                pending += len(
                    lines.filtered(
                        lambda r: r.verification_state == "pending" and r._fix_has_evidence()
                    )
                )
                discrepancy += len(lines.filtered(lambda r: r.verification_state == "discrepancy"))
            rec.evidence_pending = pending
            rec.evidence_discrepancies = discrepancy

    # ---- validation -----------------------------------------------------------
    @api.constrains("birth_reg_number")
    def _check_birth_reg(self):
        for rec in self:
            value = (rec.birth_reg_number or "").strip()
            if value and (not DIGITS.match(value) or len(value) != 17):
                raise ValidationError("A birth registration number is 17 digits.")

    @api.constrains("expected_salary", "current_salary", "notice_period_days")
    def _check_amounts(self):
        for rec in self.sudo():
            if (rec.expected_salary or 0) < 0 or (rec.current_salary or 0) < 0:
                raise ValidationError("A salary cannot be negative.")
            if (rec.notice_period_days or 0) < 0:
                raise ValidationError("A notice period cannot be negative.")

    @api.constrains("driving_licence_held", "driving_licence_no")
    def _check_licence(self):
        for rec in self:
            if rec.driving_licence_held and not (rec.driving_licence_no or "").strip():
                raise ValidationError("%s holds a driving licence: record its number." % rec.name)

    @api.constrains("relative_in_company", "relative_details")
    def _check_relative(self):
        for rec in self:
            if rec.relative_in_company and not (rec.relative_details or "").strip():
                raise ValidationError(
                    "Name the relative working at 1000 FiX, the relation and the branch "
                    "(conflict of interest)."
                )

    def _fix_check_sensitive(self, vals):
        """PDPO 2025 data minimisation: sensitive joining particulars are asked
        only from a candidate at the offer stage (or hired)."""
        asked = [n for n in SENSITIVE_FIELDS if vals.get(n)]
        if not asked or self._fix_guard_open():
            return
        for rec in self:
            if rec.state not in LATE_STATES:
                labels = ", ".join(self._fields[n].string for n in asked)
                raise UserError(
                    "%s is collected only once a candidate reaches the offer stage "
                    "(data minimisation); %s is %s."
                    % (labels, rec.name or "this candidate", rec.state)
                )

    @staticmethod
    def _fix_copy_address(vals):
        if vals.get("permanent_same_as_present"):
            for part in _ADDRESS_PARTS:
                vals["permanent_%s" % part] = vals.get("present_%s" % part) or False
        return vals

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if any(vals.get(n) for n in SENSITIVE_FIELDS) and not self._fix_guard_open():
                labels = ", ".join(self._fields[n].string for n in SENSITIVE_FIELDS if vals.get(n))
                raise UserError(
                    "%s is collected only once a candidate reaches the offer stage "
                    "(data minimisation), not with the application." % labels
                )
            self._fix_copy_address(vals)
        recs = super().create(vals_list)
        recs.filtered("declaration_accepted")._guarded().write(
            {"declaration_on": fields.Datetime.now()}
        )
        return recs

    def write(self, vals):
        self._fix_check_sensitive(vals)
        result = super().write(vals)
        if "permanent_same_as_present" in vals or any(k in vals for k in _PRESENT):
            for rec in self.filtered("permanent_same_as_present"):
                same = {"permanent_%s" % p: rec["present_%s" % p] for p in _ADDRESS_PARTS}
                if any(rec[k] != v for k, v in same.items()):
                    super(FixCandidateBiodata, rec).write(same)
        if "declaration_accepted" in vals:
            for rec in self:
                stamp = fields.Datetime.now() if rec.declaration_accepted else False
                if bool(rec.declaration_on) != bool(stamp):
                    rec._guarded().write({"declaration_on": stamp})
        return result

    # ---- the gates ---------------------------------------------------------------
    def _fix_evidence_problems(self):
        self.ensure_one()
        problems = []
        for lines in self._fix_evidence_lines():
            bad = lines.filtered(lambda r: r.verification_state == "discrepancy")
            if bad:
                problems.append(
                    "%s shows a verification discrepancy: %s"
                    % (bad._description, ", ".join(bad.mapped("display_name")))
                )
        return problems

    def action_offer(self):
        for rec in self:
            problems = rec._fix_evidence_problems()
            if problems:
                raise UserError(
                    "%s cannot move to the offer stage: %s." % (rec.name, "; ".join(problems))
                )
        return super().action_offer()

    def _fix_hire_problems(self, offer):
        problems = super()._fix_hire_problems(offer)
        if self.state not in ("hired", "rejected"):
            problems += self._fix_evidence_problems()
            if not self.declaration_accepted:
                problems.append("the candidate's declaration of truth is not recorded")
        return problems

    # ---- the hand-off to M21 --------------------------------------------------------
    def _fix_create_employee(self, offer):
        emp = super()._fix_create_employee(offer)
        self._fix_carry_biodata(emp)
        return emp

    def _fix_carry_biodata(self, emp):
        """Copy the verified biodata onto the employee master and its registers.
        sudo: the hire gate has run, and the master is HR's (see super)."""
        self.ensure_one()
        cand = self.sudo()
        emp = emp.sudo()
        Employee = emp._fields
        vals = {}
        simple = {
            "father_name": cand.father_name,
            "mother_name": cand.mother_name,
            "spouse_name": cand.spouse_name,
            "sex": cand.sex,
            "religion": cand.religion if cand.religion != "undisclosed" else False,
            "blood_group": cand.blood_group,
            "identification_mark": cand.identification_mark,
            "private_email": cand.email,
            "private_phone": cand.phone,
            "private_street": cand.present_address,
            "private_city": cand.present_upazila,
            "private_district": cand.present_district,
            "permanent_district": cand.permanent_district,
            "permanent_division": cand.permanent_division,
            "driving_license_no": cand.driving_licence_no,
            "driving_license_exp": cand.driving_licence_expiry,
            "image_1920": cand.photo,
        }
        # The identifiers (NID, birth registration, passport) are copied to the
        # employee by _fix_release_identity, from the resident store, when the
        # hire completes (M58-F4): they are not part of this clear write.
        if cand.permanent_address or cand.permanent_upazila or cand.permanent_post_code:
            simple["permanent_address"] = ", ".join(
                p
                for p in (cand.permanent_address, cand.permanent_upazila, cand.permanent_post_code)
                if p
            )
        if cand.marital_status:
            # M58-F18: carried as recorded; hr.version holds "Separated" too
            simple["marital"] = cand.marital_status
        if cand.nationality_id:
            simple["country_id"] = cand.nationality_id.id
        emergency = cand.family_ids.filtered("is_emergency_contact")[:2]
        if emergency:
            simple["emergency_contact"] = emergency[0].name
            simple["emergency_phone"] = emergency[0].phone
        for name, value in simple.items():
            if value and name in Employee:
                vals[name] = value
        if vals:
            emp.write(vals)
        self._fix_carry_registers(emp)

    def _fix_carry_registers(self, emp):
        cand = self.sudo()
        env = self.env
        company = emp.company_id.id
        if "fix.hr.education" in env:
            Edu = env["fix.hr.education"].sudo()
            for row in cand.education_ids:
                Edu._guarded().create(row._fix_hr_education_vals(emp, company))
        if "fix.hr.experience" in env:
            Exp = env["fix.hr.experience"].sudo()
            for row in cand.experience_ids:
                Exp._guarded().create(row._fix_hr_experience_vals(emp, company))
        if "fix.hr.dependant" in env:
            Dep = env["fix.hr.dependant"].sudo()
            for row in cand.family_ids.filtered(
                lambda r: r.relation in FAMILY_TO_DEPENDANT or r.is_nominee
            ):
                Dep.create(row._fix_hr_dependant_vals(emp, company))
        if "fix.hr.document" in env:
            Doc = env["fix.hr.document"].sudo()
            for row in cand.document_ids.filtered("document_file"):
                Doc.create(row._fix_hr_document_vals(emp, company))
            for row in cand.training_ids.filtered("certificate_file"):
                Doc.create(row._fix_hr_document_vals(emp, company))

    def action_hire(self, offer=None):
        result = super().action_hire(offer=offer)
        for rec in self.filtered(lambda r: r.state == "hired"):
            # M58-F4: the identifiers are copied to the employee and released by
            # _fix_release_identity (called by action_hire); clearing them here
            # would erase a value the store could not serve back that moment.
            rec._fix_prefill_preboarding()
        return result

    def _fix_prefill_preboarding(self):
        """The pre-boarding checklist starts from what the candidate already
        gave: a verified document arrives verified (by its own verifier), a
        submitted one arrives submitted, so nothing is uploaded twice."""
        self.ensure_one()
        plan = (
            self.env["fix.onboarding.plan"].sudo().search([("candidate_id", "=", self.id)], limit=1)
        )
        if not plan:
            return
        docs = self.sudo().document_ids.filtered("document_file")
        for item in plan.document_ids.filtered(lambda d: d.state == "requested"):
            matches = docs.filtered(
                lambda d, kind=item.document_type: PREBOARDING_TYPE.get(d.document_type) == kind
                and d.verification_state != "discrepancy"
            )
            if not matches:
                continue
            best = matches.filtered(lambda d: d.verification_state == "verified")[:1] or matches[:1]
            item._guarded().write(
                {
                    "document_file": best.with_context(bin_size=False).document_file,
                    "document_filename": best.document_filename,
                    "notes": "Carried from candidate document %s." % best.display_name,
                }
            )
            item._fix_stamp_upload()
            stamp = {"uploaded_by_id": best.uploaded_by_id.id or False}
            if best.verification_state == "verified":
                stamp.update(
                    state="verified",
                    verified_by_id=best.verified_by_id.id,
                    verified_on=best.verified_on,
                )
            item._guarded().write(stamp)

    # ---- retention (BRU-TAO-14) ---------------------------------------------------
    _ERASE_FIELDS = (
        "name_bn",
        "photo",
        "alt_phone",
        "present_address",
        "present_upazila",
        "present_district",
        "present_division",
        "present_post_code",
        "permanent_address",
        "permanent_upazila",
        "permanent_district",
        "permanent_division",
        "permanent_post_code",
        "current_employer",
        "current_designation",
        "career_summary",
        "key_skills",
        "cv_file",
        "cv_filename",
        "current_salary",
        "expected_salary",
        "preferred_locations",
        "driving_licence_no",
        "driving_licence_class",
        "driving_licence_expiry",
        "previous_employee_code",
        "relative_details",
        "accommodation_needs",
        "father_name",
        "mother_name",
        "birth_reg_number",
        "passport_number",
        "criminal_record",
        "criminal_record_details",
        "sex",
        "marital_status",
        "spouse_name",
        "religion",
        "blood_group",
        "identification_mark",
    )

    @api.model
    def cron_erase_expired_candidates(self):
        today = fields.Date.context_today(self)
        due = (
            self.sudo()
            .with_context(active_test=False)
            .search(
                [
                    ("retention_until", "!=", False),
                    ("retention_until", "<", today),
                    ("erased", "=", False),
                    ("state", "!=", "hired"),
                ]
            )
        )
        count = super().cron_erase_expired_candidates()
        for rec in due.exists():
            rec._fix_erase_biodata()
        return count

    def _fix_erase_biodata(self):
        for rec in self.sudo():
            for lines in (
                rec.education_ids,
                rec.training_ids,
                rec.experience_ids,
                rec.language_ids,
                rec.skill_ids,
                rec.reference_ids,
                rec.family_ids,
                rec.document_ids,
            ):
                lines._guarded().unlink()
            rec._guarded().write(
                dict.fromkeys(self._ERASE_FIELDS, False)
                | {"declaration_accepted": False, "declaration_on": False}
            )


# ================================================================ line registers
class FixCandidateLineMixin(models.AbstractModel):
    """A row of a candidate's biodata: written by Recruitment (or the
    requisition's own Hiring Manager) while the candidate is still a candidate;
    a hire or an erasure freezes it."""

    _name = "fix.candidate.line.mixin"
    _description = "Candidate Biodata Line"

    def _fix_line_candidates(self, vals_list=None):
        cands = self.mapped("candidate_id")
        ids = [v.get("candidate_id") for v in (vals_list or []) if v.get("candidate_id")]
        return (cands | self.env["fix.candidate"].browse(ids)).sudo()

    def _fix_line_gate(self, vals_list=None, what="change a candidate's biodata"):
        if self._fix_guard_open():
            return
        cands = self._fix_line_candidates(vals_list)
        _require_recruiter_or_hiring_manager(self.env, cands.mapped("requisition_id"), what)
        if not _is_recruiter(self.env) and not all(cands.mapped("requisition_id")):
            raise AccessError("Only Recruitment works a candidate with no requisition.")
        for cand in cands:
            if cand.erased:
                raise UserError("%s was erased; nothing is added back." % cand.name)
            if cand.state == "hired":
                raise UserError(
                    "%s is hired: the biodata now lives on the employee master." % cand.name
                )

    @api.model_create_multi
    def create(self, vals_list):
        self._fix_line_gate(vals_list)
        return super().create(vals_list)

    def write(self, vals):
        if not self._fix_guard_open():
            guarded = self._fix_guarded_fields() & set(vals)
            changed = {n for r in self for n in guarded if r._fix_guard_differs(n, vals[n], r[n])}
            if changed:
                self._fix_guard_refuse(changed)
            self._fix_line_gate(
                [{"candidate_id": vals["candidate_id"]}] if vals.get("candidate_id") else None
            )
        return super().write(vals)

    def unlink(self):
        self._fix_line_gate(what="remove a line of a candidate's biodata")
        if not self._fix_guard_open():
            done = self.filtered(
                lambda r: "verification_state" in r._fields and r.verification_state == "verified"
            )
            if done:
                raise UserError(
                    "%s is verified; a verified record is kept."
                    % ", ".join(done.mapped("display_name"))
                )
        return super().unlink()


class FixCandidateEvidenceMixin(models.AbstractModel):
    """A row that claims something a document proves (a degree, a job, a
    training, an ID): its files are hashed on upload and a Background Verifier
    who neither keyed nor uploaded it decides it."""

    _name = "fix.candidate.evidence.mixin"
    _description = "Candidate Evidence Line"
    _fix_evidence_files: tuple = ()

    verification_state = fields.Selection(
        VERIFICATION, string="Verification", default="pending", required=True, copy=False
    )
    verified_by_id = fields.Many2one("res.users", string="Verified By", readonly=True, copy=False)
    verified_on = fields.Datetime(string="Verified On", readonly=True, copy=False)
    verification_note = fields.Char(string="Verification Note", readonly=True, copy=False)
    evidence_sha256 = fields.Char(string="Evidence SHA-256", readonly=True, copy=False)
    uploaded_by_id = fields.Many2one("res.users", string="Uploaded By", readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "verification_state",
            "verified_by_id",
            "verified_on",
            "verification_note",
            "evidence_sha256",
            "uploaded_by_id",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if any(r.verification_state == "verified" for r in self):
            locked |= set(self._fix_evidence_files) | {
                n for n in self._fields if n not in ("notes",) and not n.startswith("verif")
            }
        return locked

    def _fix_has_evidence(self):
        self.ensure_one()
        return any(self[f] for f in self._fix_evidence_files)

    def _fix_stamp_evidence(self):
        for rec in self:
            digests = [
                _sha256(rec.with_context(bin_size=False)[f])
                for f in rec._fix_evidence_files
                if rec[f]
            ]
            rec._guarded().write(
                {
                    "evidence_sha256": ",".join(d for d in digests if d) or False,
                    "uploaded_by_id": self.env.uid if digests else False,
                    # a changed file is a new claim: decided again
                    "verification_state": "pending",
                    "verified_by_id": False,
                    "verified_on": False,
                    "verification_note": False,
                }
            )

    @api.model_create_multi
    def create(self, vals_list):
        recs = super().create(vals_list)
        recs.filtered(lambda r: r._fix_has_evidence())._fix_stamp_evidence()
        return recs

    def write(self, vals):
        files = set(self._fix_evidence_files) & set(vals)
        if files and not self._fix_guard_open():
            for rec in self:
                if rec.verification_state == "verified" and any(
                    rec._fix_guard_differs(f, vals[f], rec[f]) for f in files
                ):
                    raise UserError("%s is verified; its evidence is a record." % rec.display_name)
        changed = self.browse()
        if files and not self._fix_guard_open():
            changed = self.filtered(
                lambda r: any(r._fix_guard_differs(f, vals[f], r[f]) for f in files)
            )
        result = super().write(vals)
        changed._fix_stamp_evidence()
        return result

    def _fix_verifier_checks(self, need_file=True):
        if not (self.env.su or self.env.user.has_group(VERIFIER)):
            raise AccessError("Only a Background Verifier decides candidate evidence.")
        for rec in self:
            cand = rec.candidate_id.sudo()
            if cand.erased or cand.state in ("hired", "rejected"):
                raise UserError("%s is %s; its evidence is closed." % (cand.name, cand.state))
            if need_file and not rec._fix_has_evidence():
                raise UserError("Attach the evidence of %s before verifying it." % rec.display_name)
            if self.env.su:
                continue
            if self.env.user in (rec.create_uid, rec.uploaded_by_id):
                raise UserError(
                    "You keyed or uploaded %s; another verifier decides it." % rec.display_name
                )

    def action_verify(self):
        self._fix_verifier_checks()
        for rec in self:
            rec._guarded().write(
                {
                    "verification_state": "verified",
                    "verified_by_id": self.env.uid,
                    "verified_on": fields.Datetime.now(),
                    "verification_note": False,
                }
            )
            rec.candidate_id.sudo().message_post(
                body="Verified: %s (%s)." % (rec.display_name, rec._description)
            )
        return True

    def action_flag_discrepancy(self, reason=None):
        self._fix_verifier_checks(need_file=False)
        if not (reason or "").strip():
            raise UserError("Say what the evidence does not support.")
        for rec in self:
            rec._guarded().write(
                {
                    "verification_state": "discrepancy",
                    "verified_by_id": self.env.uid,
                    "verified_on": fields.Datetime.now(),
                    "verification_note": reason.strip()[:250],
                }
            )
            rec.candidate_id.sudo().message_post(
                body="Discrepancy on %s (%s): %s" % (rec.display_name, rec._description, reason)
            )
        return True


class FixCandidateEducation(models.Model):
    _name = "fix.candidate.education"
    _description = "Candidate Academic Qualification"
    _inherit = ["fix.candidate.evidence.mixin", "fix.candidate.line.mixin", "fix.guarded.mixin"]
    _order = "candidate_id, passing_year desc, id"
    _fix_evidence_files = ("certificate_file", "transcript_file")

    candidate_id = fields.Many2one(
        "fix.candidate", required=True, index=True, ondelete="cascade", string="Candidate"
    )
    sequence = fields.Integer(default=10)
    company_id = fields.Many2one(
        related="candidate_id.company_id", store=True, index=True, string="Company"
    )
    operating_unit_id = fields.Many2one(
        related="candidate_id.operating_unit_id", store=True, string="Operating Unit"
    )
    level = fields.Selection(EDUCATION_LEVELS, string="Level", required=True)
    exam_title = fields.Char(string="Exam / Degree Title", required=True)
    major = fields.Char(string="Group / Major / Subject")
    institute = fields.Char(string="Institute / University", required=True)
    board = fields.Selection(BOARDS, string="Board / Awarding Body")
    roll_number = fields.Char(string="Roll No.")
    registration_number = fields.Char(string="Registration No.")
    passing_year = fields.Integer(string="Passing Year")
    duration_years = fields.Float(string="Duration (years)", digits=(4, 1))
    result_type = fields.Selection(RESULT_TYPES, string="Result Type", required=True)
    result = fields.Float(string="Result (GPA / CGPA / %)", digits=(6, 2))
    achievement = fields.Char(string="Achievement / Distinction")
    certificate_file = fields.Binary(string="Certificate", attachment=True, copy=False)
    certificate_filename = fields.Char(string="Certificate File Name", copy=False)
    transcript_file = fields.Binary(string="Transcript / Mark Sheet", attachment=True, copy=False)
    transcript_filename = fields.Char(string="Transcript File Name", copy=False)

    @api.depends("exam_title", "institute", "passing_year")
    def _compute_display_name(self):
        for rec in self:
            year = " %s" % rec.passing_year if rec.passing_year else ""
            rec.display_name = "%s, %s%s" % (rec.exam_title or "?", rec.institute or "?", year)

    @api.constrains("result_type", "result", "passing_year")
    def _check_result(self):
        this_year = fields.Date.context_today(self).year
        for rec in self:
            scale = RESULT_SCALE.get(rec.result_type)
            if scale and not (0 < (rec.result or 0) <= scale):
                raise ValidationError(
                    "%s: a %s result is above 0 and at most %s."
                    % (rec.exam_title, dict(RESULT_TYPES)[rec.result_type], scale)
                )
            if rec.passing_year and not (1950 <= rec.passing_year <= this_year + 1):
                raise ValidationError("%s: the passing year is not plausible." % rec.exam_title)

    _HR_LEVEL = {
        "below_ssc": "ssc",
        "ssc": "ssc",
        "ssc_voc": "ssc",
        "ntvqf": "vocational_ntvq",
        "hsc": "hsc",
        "hsc_voc": "hsc",
        "diploma": "diploma_engineering",
        "bachelor_pass": "bachelors",
        "bachelor_hons": "bachelors",
        "masters": "masters",
        "mphil": "masters",
        "phd": "doctorate",
        "other": "vocational_ntvq",
    }
    _HR_RESULT = {
        "gpa5": "gpa_5",
        "cgpa4": "cgpa_4",
        "first_class": "first_class",
        "second_class": "second_class",
    }

    def _fix_hr_education_vals(self, emp, company):
        self.ensure_one()
        verified = self.verification_state == "verified"
        vals = {
            "employee_id": emp.id,
            "company_id": company,
            "degree_level": self._HR_LEVEL.get(self.level, "vocational_ntvq"),
            "degree_title": self.exam_title,
            "major_group": self.major or "-",
            "board_university": (dict(BOARDS).get(self.board) if self.board else False)
            or self.institute,
            "institute_name": self.institute,
            "passing_year": self.passing_year or 0,
            "duration_years": self.duration_years or 0.0,
            "result_type": self._HR_RESULT.get(self.result_type, "division"),
            "gpa_score": self.result or 0.0,
            "roll_number": self.roll_number,
            "registration_no": self.registration_number,
            "is_verified": "verified_physical"
            if verified
            else ("discrepancy" if self.verification_state == "discrepancy" else "pending"),
            "certificate_file": self.with_context(bin_size=False).certificate_file,
            "certificate_filename": self.certificate_filename,
        }
        if verified and "verified_by_id" in self.env["fix.hr.education"]._fields:
            vals["verified_by_id"] = self.verified_by_id.id
        return vals


class FixCandidateTraining(models.Model):
    _name = "fix.candidate.training"
    _description = "Candidate Training / Certification"
    _inherit = ["fix.candidate.evidence.mixin", "fix.candidate.line.mixin", "fix.guarded.mixin"]
    _order = "candidate_id, end_date desc, id"
    _fix_evidence_files = ("certificate_file",)

    candidate_id = fields.Many2one(
        "fix.candidate", required=True, index=True, ondelete="cascade", string="Candidate"
    )
    sequence = fields.Integer(default=10)
    company_id = fields.Many2one(
        related="candidate_id.company_id", store=True, index=True, string="Company"
    )
    operating_unit_id = fields.Many2one(
        related="candidate_id.operating_unit_id", store=True, string="Operating Unit"
    )
    kind = fields.Selection(
        [
            ("training", "Training Course"),
            ("vocational", "NTVQF / BNQF Skills Certificate"),
            ("professional", "Professional Certification"),
            ("oem", "OEM / Brand Accreditation"),
            ("licence", "Licence"),
        ],
        string="Type",
        required=True,
        default="training",
    )
    title = fields.Char(string="Training / Certificate Title", required=True)
    topic = fields.Char(string="Topics Covered")
    institute = fields.Char(string="Institute / Issuing Body", required=True)
    country_id = fields.Many2one("res.country", string="Country")
    location = fields.Char(string="Location")
    start_date = fields.Date(string="From")
    end_date = fields.Date(string="To / Issued On")
    duration = fields.Char(string="Duration (e.g. 3 months, 40 hours)")
    level = fields.Selection([(str(n), "Level %d" % n) for n in range(1, 7)], string="NTVQF Level")
    certificate_no = fields.Char(string="Certificate / Licence No.")
    expiry_date = fields.Date(string="Valid Until")
    certificate_file = fields.Binary(string="Certificate", attachment=True, copy=False)
    certificate_filename = fields.Char(string="Certificate File Name", copy=False)

    @api.depends("title", "institute")
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = "%s, %s" % (rec.title or "?", rec.institute or "?")

    @api.constrains("start_date", "end_date", "expiry_date")
    def _check_dates(self):
        for rec in self:
            if rec.start_date and rec.end_date and rec.end_date < rec.start_date:
                raise ValidationError("%s ends before it starts." % rec.title)
            if rec.expiry_date and rec.end_date and rec.expiry_date < rec.end_date:
                raise ValidationError("%s expires before it was issued." % rec.title)

    def _fix_hr_document_vals(self, emp, company):
        self.ensure_one()
        return {
            "employee_id": emp.id,
            "company_id": company,
            "name": self.title,
            "doc_type": "vocational" if self.kind in ("training", "vocational") else "oem_cert",
            "reference": self.certificate_no,
            "issued_on": self.end_date,
            "expiry_date": self.expiry_date,
            "verified": self.verification_state == "verified",
            "notes": "From candidate training: %s" % self.display_name,
            "file_data": self.with_context(bin_size=False).certificate_file,
            "file_name": self.certificate_filename,
        }


class FixCandidateExperience(models.Model):
    _name = "fix.candidate.experience"
    _description = "Candidate Employment History"
    _inherit = ["fix.candidate.evidence.mixin", "fix.candidate.line.mixin", "fix.guarded.mixin"]
    _order = "candidate_id, start_date desc, id"
    _fix_evidence_files = ("experience_letter_file",)

    candidate_id = fields.Many2one(
        "fix.candidate", required=True, index=True, ondelete="cascade", string="Candidate"
    )
    sequence = fields.Integer(default=10)
    company_id = fields.Many2one(
        related="candidate_id.company_id", store=True, index=True, string="Company"
    )
    operating_unit_id = fields.Many2one(
        related="candidate_id.operating_unit_id", store=True, string="Operating Unit"
    )
    employer = fields.Char(string="Employer", required=True)
    business_type = fields.Char(string="Business Type")
    employer_address = fields.Char(string="Employer Address")
    designation = fields.Char(string="Designation", required=True)
    department = fields.Char(string="Department")
    start_date = fields.Date(string="From", required=True)
    end_date = fields.Date(string="To")
    currently_working = fields.Boolean(string="Currently Working")
    duration_years = fields.Float(
        string="Years", compute="_compute_duration", store=True, digits=(6, 1)
    )
    responsibilities = fields.Text(string="Responsibilities")
    last_salary = fields.Float(string="Last Gross Salary (BDT)", groups="cd_talent.group_talent")
    reason_for_leaving = fields.Selection(
        [
            ("career_growth", "Career Growth"),
            ("compensation", "Compensation"),
            ("relocation", "Relocation"),
            ("higher_studies", "Higher Studies"),
            ("end_of_contract", "End of Contract"),
            ("redundancy", "Redundancy / Closure"),
            ("mutual", "Mutual Separation"),
            ("terminated", "Terminated / Dismissed"),
            ("other", "Other"),
        ],
        string="Reason for Leaving",
    )
    supervisor_name = fields.Char(string="Supervisor Name")
    supervisor_phone = fields.Char(string="Supervisor Phone")
    may_contact = fields.Boolean(string="May Contact Employer", default=True)
    experience_letter_file = fields.Binary(
        string="Experience / Release Letter", attachment=True, copy=False
    )
    experience_letter_filename = fields.Char(string="Letter File Name", copy=False)

    @api.depends("employer", "designation")
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = "%s at %s" % (rec.designation or "?", rec.employer or "?")

    @api.depends("start_date", "end_date", "currently_working")
    def _compute_duration(self):
        today = fields.Date.context_today(self)
        for rec in self:
            end = today if rec.currently_working or not rec.end_date else rec.end_date
            if rec.start_date and end >= rec.start_date:
                rec.duration_years = round((end - rec.start_date).days / 365.25, 1)
            else:
                rec.duration_years = 0.0

    @api.constrains("start_date", "end_date", "currently_working")
    def _check_dates(self):
        today = fields.Date.context_today(self)
        for rec in self:
            if rec.start_date and rec.start_date > today:
                raise ValidationError("%s starts in the future." % rec.display_name)
            if rec.end_date and rec.start_date and rec.end_date < rec.start_date:
                raise ValidationError("%s ends before it starts." % rec.display_name)
            if rec.currently_working and rec.end_date:
                raise ValidationError("%s is current: leave its end date empty." % rec.display_name)

    _HR_REASON = {
        "career_growth": "career_growth",
        "compensation": "compensation",
        "relocation": "relocation",
        "higher_studies": "higher_studies",
        "end_of_contract": "end_of_contract",
        "mutual": "mutual",
    }

    def _fix_hr_experience_vals(self, emp, company):
        self.ensure_one()
        rec = self.sudo()
        joining = emp.joining_date or fields.Date.context_today(self)
        vals = {
            "employee_id": emp.id,
            "company_id": company,
            "company_name": rec.employer,
            "designation_held": rec.designation,
            "start_date": rec.start_date,
            "end_date": rec.end_date or joining,
            "last_drawn_salary": rec.last_salary or 0.0,
            "reason_for_leaving": self._HR_REASON.get(rec.reason_for_leaving, "career_growth"),
            "supervisor_name": rec.supervisor_name,
            "supervisor_phone": rec.supervisor_phone,
            "experience_letter_file": rec.with_context(bin_size=False).experience_letter_file,
            "experience_letter_filename": rec.experience_letter_filename,
        }
        if rec.verification_state == "verified":
            vals["reference_status"] = "verified_positive"
            if "reference_checked_by_id" in self.env["fix.hr.experience"]._fields:
                vals["reference_checked_by_id"] = rec.verified_by_id.id
        elif rec.verification_state == "discrepancy":
            vals["reference_status"] = "negative_flag"
        else:
            vals["reference_status"] = False
        return vals


class FixCandidateLanguage(models.Model):
    _name = "fix.candidate.language"
    _description = "Candidate Language Proficiency"
    _inherit = ["fix.candidate.line.mixin", "fix.guarded.mixin"]
    _order = "candidate_id, sequence, id"

    candidate_id = fields.Many2one(
        "fix.candidate", required=True, index=True, ondelete="cascade", string="Candidate"
    )
    sequence = fields.Integer(default=10)
    company_id = fields.Many2one(
        related="candidate_id.company_id", store=True, index=True, string="Company"
    )
    operating_unit_id = fields.Many2one(
        related="candidate_id.operating_unit_id", store=True, string="Operating Unit"
    )
    language = fields.Selection(
        [
            ("bangla", "Bangla"),
            ("english", "English"),
            ("hindi", "Hindi / Urdu"),
            ("arabic", "Arabic"),
            ("chinese", "Chinese"),
            ("other", "Other"),
        ],
        string="Language",
        required=True,
    )
    other_language = fields.Char(string="Other Language")
    reading = fields.Selection(PROFICIENCY, string="Reading")
    writing = fields.Selection(PROFICIENCY, string="Writing")
    speaking = fields.Selection(PROFICIENCY, string="Speaking")


class FixCandidateSkill(models.Model):
    _name = "fix.candidate.skill"
    _description = "Candidate Skill"
    _inherit = ["fix.candidate.line.mixin", "fix.guarded.mixin"]
    _order = "candidate_id, sequence, id"

    candidate_id = fields.Many2one(
        "fix.candidate", required=True, index=True, ondelete="cascade", string="Candidate"
    )
    sequence = fields.Integer(default=10)
    company_id = fields.Many2one(
        related="candidate_id.company_id", store=True, index=True, string="Company"
    )
    operating_unit_id = fields.Many2one(
        related="candidate_id.operating_unit_id", store=True, string="Operating Unit"
    )
    category = fields.Selection(
        [
            ("mobile", "Mobile / Tablet Repair"),
            ("computer", "Laptop / Desktop / Printer"),
            ("appliance", "Home Appliance (AC / Fridge / Washer)"),
            ("electronics", "TV / Consumer Electronics"),
            ("network", "Network / IT Infrastructure"),
            ("software", "Software / Office Tools"),
            ("customer", "Customer Service / Call Centre"),
            ("sales", "Sales / Retail"),
            ("finance", "Finance / Accounts"),
            ("logistics", "Logistics / Inventory"),
            ("management", "Supervision / Management"),
            ("other", "Other"),
        ],
        string="Category",
        required=True,
    )
    skill = fields.Char(string="Skill (e.g. chip-level repair, BGA rework)", required=True)
    level = fields.Selection(
        [
            ("basic", "Basic"),
            ("intermediate", "Intermediate"),
            ("advanced", "Advanced"),
            ("expert", "Expert"),
        ],
        string="Level",
    )
    years = fields.Float(string="Years Used", digits=(4, 1))
    brands = fields.Char(string="Brands / Products")


class FixCandidateReference(models.Model):
    _name = "fix.candidate.reference"
    _description = "Candidate Referee"
    _inherit = ["fix.candidate.line.mixin", "fix.guarded.mixin"]
    _order = "candidate_id, sequence, id"

    candidate_id = fields.Many2one(
        "fix.candidate", required=True, index=True, ondelete="cascade", string="Candidate"
    )
    sequence = fields.Integer(default=10)
    company_id = fields.Many2one(
        related="candidate_id.company_id", store=True, index=True, string="Company"
    )
    operating_unit_id = fields.Many2one(
        related="candidate_id.operating_unit_id", store=True, string="Operating Unit"
    )
    name = fields.Char(string="Referee Name", required=True)
    designation = fields.Char(string="Designation")
    organisation = fields.Char(string="Organisation")
    relation = fields.Selection(
        [
            ("supervisor", "Former Supervisor"),
            ("colleague", "Colleague"),
            ("teacher", "Teacher / Academic"),
            ("client", "Client"),
            ("community", "Community / Character Referee"),
        ],
        string="Relation",
        required=True,
    )
    phone = fields.Char(string="Phone", required=True)
    email = fields.Char(string="Email")
    address = fields.Char(string="Address")
    years_known = fields.Integer(string="Years Known")
    consent_to_contact = fields.Boolean(string="Candidate Allows Contact", default=True)


FAMILY_TO_DEPENDANT = {
    "spouse": "spouse",
    "son": "child",
    "daughter": "child",
    "father": "parent",
    "mother": "parent",
    "brother": "sibling",
    "sister": "sibling",
}


class FixCandidateFamily(models.Model):
    """Family, emergency contacts and statutory nominees (BLA 2006 s.19 death
    benefit, provident fund and gratuity nominations). Asked at the offer
    stage: nobody's family is collected with a mere application."""

    _name = "fix.candidate.family"
    _description = "Candidate Family / Emergency Contact / Nominee"
    _inherit = ["fix.candidate.line.mixin", "fix.guarded.mixin"]
    _order = "candidate_id, sequence, id"

    candidate_id = fields.Many2one(
        "fix.candidate", required=True, index=True, ondelete="cascade", string="Candidate"
    )
    sequence = fields.Integer(default=10)
    company_id = fields.Many2one(
        related="candidate_id.company_id", store=True, index=True, string="Company"
    )
    operating_unit_id = fields.Many2one(
        related="candidate_id.operating_unit_id", store=True, string="Operating Unit"
    )
    name = fields.Char(string="Name", required=True)
    relation = fields.Selection(
        [
            ("spouse", "Spouse"),
            ("father", "Father"),
            ("mother", "Mother"),
            ("son", "Son"),
            ("daughter", "Daughter"),
            ("brother", "Brother"),
            ("sister", "Sister"),
            ("guardian", "Guardian"),
            ("other", "Other"),
        ],
        string="Relation",
        required=True,
    )
    date_of_birth = fields.Date(string="Date of Birth")
    occupation = fields.Char(string="Occupation")
    phone = fields.Char(string="Phone")
    address = fields.Char(string="Address")
    is_emergency_contact = fields.Boolean(string="Emergency Contact")
    is_nominee = fields.Boolean(string="Nominee")
    nominee_pct = fields.Float(string="Nominee Share %", digits=(5, 2))
    guardian_name = fields.Char(string="Guardian (if minor nominee)")

    _pct_range = models.Constraint(
        "CHECK (nominee_pct >= 0 AND nominee_pct <= 100)", "A nominee share is 0 to 100 percent."
    )

    @api.model_create_multi
    def create(self, vals_list):
        if not self._fix_guard_open():
            cands = (
                self.env["fix.candidate"]
                .sudo()
                .browse([v.get("candidate_id") for v in vals_list if v.get("candidate_id")])
            )
            early = cands.filtered(lambda c: c.state not in LATE_STATES)
            if early:
                raise UserError(
                    "Family, emergency contacts and nominees are collected once a candidate "
                    "reaches the offer stage (data minimisation); %s is %s."
                    % (early[0].name, early[0].state)
                )
        return super().create(vals_list)

    @api.constrains("is_nominee", "nominee_pct", "candidate_id")
    def _check_nominees(self):
        for cand in self.mapped("candidate_id"):
            nominees = cand.sudo().family_ids.filtered("is_nominee")
            if nominees and sum(nominees.mapped("nominee_pct")) > 100.0001:
                raise ValidationError("%s's nominee shares add up to more than 100%%." % cand.name)
        for rec in self:
            if rec.is_emergency_contact and not (rec.phone or "").strip():
                raise ValidationError("Emergency contact %s needs a phone number." % rec.name)

    def _fix_hr_dependant_vals(self, emp, company):
        self.ensure_one()
        return {
            "employee_id": emp.id,
            "company_id": company,
            "name": self.name,
            "relation": FAMILY_TO_DEPENDANT.get(self.relation, "other"),
            "date_of_birth": self.date_of_birth,
            "is_nominee": self.is_nominee,
            "nominee_pct": self.nominee_pct if self.is_nominee else 0.0,
            "guardian_name": self.guardian_name,
        }


class FixCandidateDocument(models.Model):
    """A document the candidate handed in, scanned or photographed: CV,
    certificates, transcripts, testimonials, release letters, PCC..."""

    _name = "fix.candidate.document"
    _description = "Candidate Document"
    _inherit = [
        "fix.candidate.evidence.mixin",
        "fix.candidate.line.mixin",
        "fix.guarded.mixin",
    ]
    _order = "candidate_id, sequence, id"
    _fix_evidence_files = ("document_file",)

    candidate_id = fields.Many2one(
        "fix.candidate", required=True, index=True, ondelete="cascade", string="Candidate"
    )
    sequence = fields.Integer(default=10)
    company_id = fields.Many2one(
        related="candidate_id.company_id", store=True, index=True, string="Company"
    )
    operating_unit_id = fields.Many2one(
        related="candidate_id.operating_unit_id", store=True, string="Operating Unit"
    )
    candidate_state = fields.Selection(related="candidate_id.state", string="Candidate Stage")
    document_type = fields.Selection(
        CANDIDATE_DOCUMENT_TYPES, string="Document Type", required=True
    )
    description = fields.Char(string="Description (e.g. HSC 2018 certificate)")
    issued_by = fields.Char(string="Issued By")
    reference = fields.Char(string="Document No. / Reference")
    issued_on = fields.Date(string="Issued On")
    expiry_date = fields.Date(string="Valid Until")
    original_seen = fields.Boolean(
        string="Original Seen", help="The original was seen and matched to this copy."
    )
    document_file = fields.Binary(string="File", attachment=True, copy=False)
    document_filename = fields.Char(string="File Name", copy=False)

    @api.depends("document_type", "description")
    def _compute_display_name(self):
        labels = dict(CANDIDATE_DOCUMENT_TYPES)
        for rec in self:
            label = labels.get(rec.document_type, "Document")
            rec.display_name = "%s: %s" % (label, rec.description) if rec.description else label

    @api.model_create_multi
    def create(self, vals_list):
        if not self._fix_guard_open():
            for vals in vals_list:
                if not vals.get("document_file"):
                    raise UserError("Attach the scanned or photographed document.")
            late = [v for v in vals_list if v.get("document_type") in JOINING_DOCUMENTS]
            if late:
                cands = (
                    self.env["fix.candidate"]
                    .sudo()
                    .browse([v.get("candidate_id") for v in late if v.get("candidate_id")])
                )
                early = cands.filtered(lambda c: c.state not in LATE_STATES)
                if early:
                    raise UserError(
                        "Bank, nominee, TIN and medical documents are collected once a "
                        "candidate reaches the offer stage; %s is %s."
                        % (early[0].name, early[0].state)
                    )
        return super().create(vals_list)

    @api.constrains("issued_on", "expiry_date")
    def _check_dates(self):
        for rec in self:
            if rec.issued_on and rec.expiry_date and rec.expiry_date < rec.issued_on:
                raise ValidationError("%s expires before it was issued." % rec.display_name)

    def _fix_hr_document_vals(self, emp, company):
        self.ensure_one()
        return {
            "employee_id": emp.id,
            "company_id": company,
            "name": self.display_name,
            "doc_type": HR_DOCUMENT_TYPE.get(self.document_type, "other_candidate"),
            "reference": self.reference,
            "issued_on": self.issued_on,
            "expiry_date": self.expiry_date,
            "verified": self.verification_state == "verified",
            "notes": "From candidate document (SHA-256 %s)" % (self.evidence_sha256 or "-")[:64],
            "file_data": self.with_context(bin_size=False).document_file,
            "file_name": self.document_filename,
        }


class FixHrDocumentCandidateTypes(models.Model):
    """The employee dossier receives the candidate's documents at hire; these
    kinds had no type there."""

    _inherit = "fix.hr.document"

    doc_type = fields.Selection(
        selection_add=[
            ("cv", "CV / Resume"),
            ("photo", "Photograph"),
            ("transcript", "Transcript / Mark Sheet"),
            ("testimonial", "Testimonial"),
            ("character_cert", "Character Certificate"),
            ("release_letter", "Release / Clearance Letter"),
            ("other_candidate", "Other Candidate Document"),
        ],
        ondelete={
            "cv": "set default",
            "photo": "set default",
            "transcript": "set default",
            "testimonial": "set default",
            "character_cert": "set default",
            "release_letter": "set default",
            "other_candidate": "set default",
        },
    )
