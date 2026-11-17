# M58 Candidate Biodata: data-capture standard

Date: 18 Nov 2026. Module: M58 Talent Acquisition (`cd_talent`), screen "Candidate Biodata" (`M58-form-candidate`).

## 1. What was wrong

The Candidate Biodata form had **12 fields** on 2 tabs:

- name, email, phone, branch, source, posting, agency;
- date of birth, NID;
- consent, consent date, retention date.

The form could not record any of these:

- the candidate's education, training, work history, skills, languages, referees or family;
- any document: CV, certificates, transcripts, testimonials, release letters, police clearance, and so on.

Screening and background verification therefore ran on paper. When a candidate was hired, the employee master's education, experience, document and dependant registers started empty.

## 2. Research basis

| Topic | Source |
|---|---|
| Bangladesh CV structure | bdjobs-format CV: Exam Title, Concentration/Major, Institute, Result, Passing Year, Duration, Achievement; training: title, topic, institute, country, location, year, duration |
| Bangladesh education | SSC/Dakhil/O-Level → HSC/Alim/A-Level → Diploma (BTEB) → Bachelor (Pass/Hons) → Masters → MPhil/PhD; NTVQF/BNQF levels 1–6; 11 boards (Dhaka, Rajshahi, Cumilla, Jashore, Chattogram, Barishal, Sylhet, Dinajpur, Mymensingh, Madrasah, Technical); GPA out of 5 (SSC/HSC), CGPA out of 4 (UGC), Division/Class for older results |
| ATS data models | Odoo 18 `hr.candidate` / `hr.applicant` / `hr.resume.line` / `hr.employee.skill`; Workday education and language; Oracle Recruiting "Licenses and Certifications"; Dynamics 365 certificate types |
| Bangladesh Labour Act 2006 | s.5 appointment letter and ID card; s.6–8 service book (s.7(2) items include parents, identification mark and previous employer); s.9 register of workers; s.19 death benefit to the nominee; s.34–37 adolescent age and fitness certificate |
| Privacy | Personal Data Protection Ordinance 2025: religion and health are sensitive data and need explicit consent; data unrelated to the purpose must not be collected. Consent is recorded per purpose. Unsuccessful candidates are kept about 6 months (12 months with talent-pool consent) |

Not confirmed: the exact field list of Labour Rules Form 41 (provident-fund nomination), and the gazette date of the 2025 Ordinance.

## 3. The standard: header fields by stage

| Stage | Fields |
|---|---|
| **Application** | English name, Bangla name, photograph, mobile, alternative mobile, email; present address (house/road, upazila, district, division, post code); requisition, branch, source, posting, agency, applied on; current employer and designation; career summary, key skills; **CV upload**; highest qualification and total experience (both computed from the grids) |
| **Screening** | current and expected salary (visible to Recruitment only); notice period, earliest joining date, preferred locations; willing to relocate, travel or work shifts; owns a motorcycle; driving licence (held, number, class, expiry); applied or worked here before (with previous employee ID); relative in the company (conflict of interest); accommodation needs (voluntary) |
| **Pre-offer (shortlisted)** | date of birth, nationality, NID, or birth registration number (17 digits) if no NID, passport; father's and mother's names; permanent address (with "same as present"); criminal-record declaration (Recruitment only) |
| **Joining (offer stage onward)** | gender, marital status, spouse, religion, blood group, identification mark (Form 7) |
| **Consent** | consent to processing, talent-pool consent (separate), declaration of truth; the system stamps the date and time of each |

Data minimisation is enforced on the server, not only on the screen:

- The server refuses religion, blood group, marital status, spouse, family and nominees, and bank, nominee, TIN and medical documents before the offer stage.
- The form shows those inputs locked until the candidate reaches that stage.

## 4. The repeating registers (add-more-lines grids)

| Tab | Register | Columns | Upload per row |
|---|---|---|---|
| Education | `fix.candidate.education` | level, exam/degree, group/major, board, institute, year, result type, result, duration, roll no., registration no., achievement | certificate **and** transcript/mark sheet |
| Training & Certifications | `fix.candidate.training` | type (training / NTVQF / professional / OEM / licence), title, topics, issuer, country, location, from, to, duration, NTVQF level, certificate no., valid until | certificate |
| Employment History | `fix.candidate.experience` | employer, business type, address, designation, department, from, to, current, years (computed), responsibilities, last salary, reason for leaving, supervisor, phone, may contact | experience / release letter |
| Skills, Languages & Referees | `fix.candidate.skill` | category (mobile, computer, appliance…), skill, level, years, brands | — |
| | `fix.candidate.language` | language, reading, writing, speaking | — |
| | `fix.candidate.reference` | name, designation, organisation, relation (no relatives), phone, email, address, years known, may contact | — |
| Documents & Attachments | `fix.candidate.document` | document type (22 types), description, issued by, document no., issued on, valid until, original seen | the file (required) |
| Joining Particulars & Family | `fix.candidate.family` | name, relation, date of birth, occupation, phone, address, emergency contact, nominee, share %, guardian (minor nominee) | — |

The 22 document types are:

- identity and personal: CV, cover letter, photograph, NID, birth certificate, passport;
- education and training: academic certificate, transcript, training/NTVQF certificate, professional/OEM certificate;
- character and work history: testimonial, character certificate, experience letter, release letter, last payslip;
- checks and compliance: driving licence, police clearance certificate (PCC), medical fitness (BLA s.37), e-TIN certificate;
- joining: bank/MFS proof, nominee NID;
- other.

Files may be PDF, JPG, PNG or DOCX, up to 10 MB each.

## 5. Controls

- **Evidence integrity.** Every uploaded file is hashed with SHA-256 and stamped with who uploaded it. A replaced file sends the row back to "Pending".
- **Verification.** A Background Verifier decides each evidence row on four new **Candidate Evidence** lists: Documents, Academic Qualifications, Employment History, Training & Certificates. The verifier records "Verify" or "Flag Discrepancy" with a reason. They cannot verify a row they keyed or uploaded. A verified row can be neither edited nor deleted.
- **Gates.**
  - A discrepancy blocks the offer stage and the hire.
  - The hire needs the declaration of truth.
  - Nominee shares cannot exceed 100%.
  - An emergency contact needs a phone number.
  - Results are checked against their scale: GPA ≤ 5, CGPA ≤ 4.
  - A current job has no end date.
  - A birth registration number has 17 digits.
- **Access.**
  - Recruitment and the requisition's own Hiring Manager can edit.
  - Verifiers and approvers can read.
  - Salary and criminal-record fields are visible to Recruitment only.
  - Records are isolated by company and branch.
- **Hire hand-off.** The hire copies the data to the M21 employee master:
  - parents, spouse, gender, blood group, religion, marital status, addresses, licence, passport, birth registration, photograph and emergency contact;
  - education into `fix.hr.education`, carrying the verifier's decision;
  - experience into `fix.hr.experience`;
  - documents and certificates into `fix.hr.document`, which gains 7 new types;
  - family and nominees into `fix.hr.dependant`;
  - the passport and birth registration numbers are then cleared from the candidate;
  - the pre-boarding checklist (NID, photo, academic, experience, bank, age proof, medical) is pre-filled from the candidate's documents. A verified document arrives verified by its original verifier, so nothing is uploaded twice.
- **Retention.** When a candidate's retention date passes, the erase job deletes every line and file and clears the personal fields.

## 6. Engine change (estate-wide, backward compatible)

The P03 form engine supported **one** child grid per form. It now also takes `grids: [{field, title, tab, fields, note, empty, addLabel}]`:

- several add-more-lines tables per form, each on its own tab;
- each row has a file-upload cell;
- every table saves with the header in **one** write, and a refusal leaves nothing behind;
- a stored file is served as a download link and is never re-sent on save.

The change touches these files:

- `p03_workspace.js`, `p03_workspace.xml`;
- `p03_generic_api.py` (`model_form` / `model_write` take `grids`);
- `form_fields.py`, which generates the write whitelist and now includes grid fields.

Existing `lines:` forms are unchanged.

## 7. Evidence

The tests ran on a private clone, `fix_test_m58bio`, after `-u all` completed with 0 errors.

- `cd_talent/tests/test_m58_candidate_biodata.py`: **23/23 pass**. They run as non-admin users on the ORM and through the real `/p03` controller.
- Mutation check: **6/6 mutants caught**. Each one was killed by a red test:
  - verifier self-check removed;
  - data-minimisation check removed;
  - hire discrepancy gate removed;
  - "document needs a file" check removed;
  - stored-file echo filter removed;
  - hire register carry-over removed.
- Regression over M58, A09 and the form engine: **614/614 pass**, and the static guards (`test_m58_capture_buttons`, A09 whitelist) **53/53 pass**.
- Wider portal sweep: 1,383 tests with 1 failure, `test_a08_m50_registry` ("Cheque" chip unmapped). That test fails identically on the unmodified base, so it is unrelated to this change.
- UI walk on a private server (port 8094), driven through the real Save button:
  - all 10 tabs render;
  - two education lines were added and a certificate uploaded, then saved;
  - the database holds both rows, the file and its SHA-256;
  - after a reload, the stored file comes back as a download link that serves the original bytes under the uploaded file name;
  - the Joining particulars are read-only for an applied candidate;
  - the Candidate Evidence list shows Verify and Flag Discrepancy.

## 8. Deployment

Not deployed yet. Deploying needs:

1. landing the commits on the shared branch;
2. `-u cd_talent,cd_p03_portal` on fix_real;
3. one restart of 8069, because the controllers changed.
