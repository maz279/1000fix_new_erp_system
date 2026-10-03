---
id: FIX-ERP2-00-07
title: Category H Audit & Repository Integrity Report
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-13
status: ISSUED
classification: CONFIDENTIAL — Internal Use Only
auditor: Documentation Squad
scope: Category H module specifications + repository-wide identifier and register integrity
regulatory_verified: 2026-08-12
---

# Documentation Audit — Category H & Repository Integrity
### Second audit · Supersedes nothing in `00-06`; extends it

---

## 1. Scope and Method

This audit was mandated as a condition of the Category H work. It covers:

1. The **seven Category H module specifications** written in this cycle
2. The **register and cross-cutting documents** updated to reflect them
3. **Repository-wide integrity** — because Category H's identifier allocations could only be
   validated against the whole estate

### Method

Every finding below was produced by **direct verification against the files**, not by review
or inference. The checks run were:

| # | Check | How |
|---|---|---|
| 1 | Requirement ID contiguity and duplication, per module | Extract, sort, deduplicate, compare count to highest ID |
| 2 | Requirement counts against the register and `05-01` | Direct count of all 65 module files |
| 3 | KPI identifier collisions | Cross-file identifier index |
| 4 | Custom-development (CD) identifier collisions | Cross-file identifier index |
| 5 | Role identifier registration | Module usage against `05-04` |
| 6 | Segregation-of-duties identifier registration | Module usage against `05-04` |
| 7 | Cross-reference validity within Category H | Resolve every link and file reference |
| 8 | Module file existence against the register | Filesystem enumeration against `02-02` |
| 9 | Effort figures | Direct sum from every module identity table |
| 10 | Regulatory currency | Verification dates on every citation |

**Result: 14 findings — 3 critical, 5 high, 4 medium, 2 low.**

**Two of them concern edits made during this same session and have been corrected.** They are
reported rather than quietly fixed, because the cause matters more than the fix.

---

## 2. Findings Summary

| ID | Severity | Finding | Status |
|---|:--:|---|:--:|
| H2-01 | **CRITICAL** | The register and README understated repository completeness by 44 module specifications | **Fixed** |
| H2-02 | **CRITICAL** | M66 and M67 are registered modules with no specification file | **Open** |
| H2-03 | **CRITICAL** | 28 requirement IDs in Category A are allocated but unused; recorded counts were taken from the highest ID | **Fixed in register; open in modules** |
| H2-04 | High | 22 KPI identifiers are used by two or more different modules | **Open** |
| H2-05 | High | 70+ custom-development identifiers collide across modules | **Open** |
| H2-06 | High | 18 segregation-of-duties identifiers are used but never registered | **Open** |
| H2-07 | High | Roles R39–R46 are used but not registered; R54, R57 and R60 are used and undefined anywhere | **Open** |
| H2-08 | High | Programme effort is 1,513 PW measured against 834 PW in the approved business case | **Escalated (D-14)** |
| H2-09 | Medium | Category H overview cited retired v1.0 identifiers | **Fixed** |
| H2-10 | Medium | Category H overview carried an absolute KPI target with no baseline behind it | **Fixed** |
| H2-11 | Medium | M42 uses a four-character module code against a three-character convention | **Accepted, documented** |
| H2-12 | Medium | The "17+ brands" figure underpins an M22 control but is unverified | **Open** |
| H2-13 | Low | Statutory tax figures rest partly on press reporting rather than the enacted Finance Act | **Open, flagged in-module** |
| H2-14 | Low | Markdown table-style lint warnings across the repository | **Accepted** |

---

## 3. Critical Findings

### H2-01 — The register understated repository completeness by 44 module specifications

**What was found.** `02-02` recorded **21 of 67** module specifications written, and marked
Categories C, D, E, F, G, I, J and K as `0/N` with `—` in the Spec column. Direct enumeration
of `03_Modules/**/M*.md` returns **65 files**.

Every one of those files is a complete specification. Spot checks confirm they carry the full
19-section template, requirement tables, business rules, data entities, automations,
interfaces, KPIs and acceptance criteria — the same structure as Categories A, B and H.

| | Register said | Actually on disk |
|---|---:|---:|
| Module specifications written | 21 | **65** |
| Requirements | ~2,535 *(mixed measured/estimated)* | **2,930 (counted)** |
| Effort | ~1,333 PW *(mixed)* | **1,513 PW (counted)** |
| README completeness | 40% | **76%** |

**Why it happened.** The register's Spec column was updated only for the categories being
actively worked. Specifications written in other cycles never triggered a register update. This
is the **inverse of the RG-01 register-first failure found in the first audit**: there, a
specification existed with no register entry (M31); here, 44 specifications exist with register
entries that deny they were written.

**Compounding factor — reported openly.** Earlier in this same session I edited `02-02` and the
README to record "21 of 67", "~2,535 requirements" and "40% complete". Those edits **propagated
the error and made it worse**, because they restated it with more authority and more precision
than before. The cause was that I accepted the register's own account of what existed instead
of checking the filesystem — the same mistake the register had made. The audit checks are what
caught it. Both files have been corrected to the counted figures.

**Fixed.** `02-02` §3 rewritten with counted figures for all eleven categories and a per-module
Spec column. README completeness table and category breakdown rewritten. The correction-factor
mechanism is retired — with 65 of 67 written there is nothing left to project.

**Governance consequence — new rule RG-06.**

> **RG-06 — Count, do not consult.** Any figure describing what the repository contains
> (specification counts, requirement totals, effort totals, completeness percentages) must be
> **derived by direct enumeration of the files at the time of writing**. A prior statement of
> the same figure — including one in the authoritative register — is not evidence. Every such
> figure carries the date it was counted.

---

### H2-02 — M66 and M67 have no specification file

**What was found.** Category K registers seven modules. Five specification files exist.

| Module | Code | Priority | Wave | Status |
|---|---|:--:|:--:|---|
| **M66 — Internal IT Service Management** | `ITS` | P2 | W6 | ⬜ **No specification** |
| **M67 — Project, Program & Portfolio Management** | `PPM` | P2 | W7 | ⬜ **No specification** |

These are the **only two outstanding specifications in the entire programme**. Both are P2 and
land in later waves, so neither is on a near-term critical path — but the register showed
Category K as `0/7` written, which masked the fact that it was actually `5/7` with a specific,
nameable gap.

**Why it matters beyond the gap itself.** M66 (Internal ITSM) is the module that would own
internal support ticketing, change management and IT asset lifecycle. Several written modules
raise service requests against IT — M58 onboarding provisioning, M29 access requests, M59
equipment findings. Those interfaces currently point at a module that does not exist as a
specification, so their contracts are unverifiable.

**Open.** Recommend writing both to close the programme specification set. Estimated at 22 and
26 requirements respectively.

---

### H2-03 — 28 requirement IDs in Category A are allocated but unused

**What was found.** Three Category A modules have **non-contiguous requirement sequences** —
IDs are allocated up to a maximum, but numbers within the range are missing entirely.

| Module | Code | IDs present | Highest ID | Missing |
|---|---|---:|---:|---:|
| M01 Service Request & Order Management | `SRM` | 72 | 088 | **16** |
| M02 Field Service & Dispatch | `FSM` | 65 | 074 | **9** |
| M31 Workshop & Depot Repair | `WSR` | 55 | 058 | **3** |

Missing IDs, verified individually (these are true gaps — no `020a`-style sub-identifiers
account for them):

- **`FR-SRM-`** 026, 032, 035, 037, 038, 059, 060, 061, 062, 064, 067, 071, 074, 075, 079, 081
- **`FR-FSM-`** 048, 049, 050, 051, 054, 065, 069, 070, 073
- **`FR-WSR-`** 055, 056, 057

**The consequence.** The register recorded M01 as **88** requirements, M02 as **74** and M31 as
**58** — the highest ID in each case, not the count. Category A's registered total of 388 was
therefore **26 requirements overstated** (that figure also missed the M04 correction from 31 to
32 made in the first audit). The measured total is **362**.

This matters because requirement counts drive effort estimation, wave sizing and the business
case. A category that reports 7% more requirements than it has distorts every downstream figure.

**Every other category is clean.** All 62 remaining module files have contiguous sequences with
count equal to highest ID. Category H specifically: all seven modules verified contiguous, no
duplicates.

**Fixed in the register; open in the modules.** `02-02` now carries the counted figure of 362.
The gaps themselves remain: either the missing requirements were dropped during drafting and
should be reinstated, or the sequences should be closed up. **Closing them up would violate
RG-02 (permanent identity)** if any of those IDs have been referenced elsewhere. Recommend
leaving the IDs retired and recording them as such, which is the lower-risk option.

---

## 4. High Findings

### H2-04 — 22 KPI identifiers are used by two or more different modules

`KPI-nnn` is a programme-wide identifier space. It is being allocated locally, and the
collisions are extensive.

| KPI | Claimed by |
|---|---|
| KPI-049 | M16, M41, M44, M52, M28, M29, M30, M64 — **8 modules** |
| KPI-050 | M15, M19, M20, M49, M50, M51, M52, M29, M30 — **9 modules** |
| KPI-004 | M01, M02, M31, M15, M43, M17, M45, M48 — **8 modules** |
| KPI-011 | M02, M15, M46, M47, M48 — 5 modules |
| KPI-002 | M01, M15, M41, M47 — 4 modules |
| KPI-041, 043–046, 048, 051, 052, 056–058, 093, 094, 005, 007, 009, 013 | 2–3 modules each |

**Category H is clean.** KPI-212 … KPI-305 are used by Category H alone and collide with
nothing. The allocation discipline applied during this cycle worked; it simply was not applied
in earlier cycles.

**Why it matters.** A KPI identifier that resolves to nine different metrics cannot be used in
a dashboard specification, a benefits-realisation report or a board pack. `06-02` reports
benefits by KPI ID; those references are currently ambiguous.

**Open.** Requires a programme-wide KPI register (`05-05` or a new reference document) with
single allocation, then a reconciliation pass across the colliding modules. This is a
mechanical but non-trivial exercise — roughly 60 identifiers to reassign.

---

### H2-05 — 70+ custom-development identifiers collide across modules

The same failure in the `CD-nnn` space, and worse. Examples:

| CD | Claimed by |
|---|---|
| CD-157 | M17, M45, M46, M47, M48, M19, M28, M29 — **8 modules** |
| CD-159 | M17, M45, M46, M47, M48, M19, M28, M30 — **8 modules** |
| CD-163 | M17, M45, M46, M47, M48, M20, M28 — 7 modules |
| CD-075 | M17, M45, M46, M47, M48, **M55** — 6 modules |
| CD-066 … CD-091 | Category H's allocations collide with modules in D, E, F and G |

**Category H marked its CD identifiers provisional, which was correct.** Every Category H
module file carries the note *"CD identifiers are provisional pending the unified register in
`02-05`"*, and that caveat has now been vindicated. But provisional identifiers in 65 modules
are not a workable position: `02-05` cannot be assembled from them without a full reassignment.

**Why it matters more than the KPI collisions.** CD identifiers name **deliverable software
modules**. They will appear in the build backlog, the repository structure, the deployment
manifest and the vendor statement of work. A collision here becomes a real conflict at build
time, not just a documentation defect.

**Open.** `02-05` must become the single allocating authority, with every module's CD block
reassigned from it. Recommend doing this **before** any build contract is issued.

---

### H2-06 — 18 segregation-of-duties identifiers are used but never registered

`05-04_Role_Permission_and_Access_Matrix.md` registers **SOD-01 … SOD-12**.

Module files use **SOD-01 … SOD-30**. Everything from **SOD-13 to SOD-30 is unregistered** —
invented in a module file and never added to the matrix.

Category H uses SOD-03 (registered), and **SOD-25, 26, 27, 28, 29, 30 (all unregistered)**.
Specifically:

- **SOD-03** — payroll preparer cannot approve *(registered, correct)*
- **SOD-29** — payroll approver cannot release the bank file *(unregistered)*
- **SOD-30** — M57 calculates the incentive; only M56 can pay it *(unregistered)*

**Why it matters.** Segregation of duties is an **audit control**, not documentation. An
external auditor or a GRC reviewer will ask for the SoD matrix. If the matrix omits 18 of the
30 controls the system actually implements, the controls cannot be evidenced — and controls
that cannot be evidenced are, for audit purposes, controls that do not exist.

This is a **direct RG-01 (register-first) violation**, the same rule adopted after the first
audit found M31 orphaned. The rule was adopted for requirements and modules; it was never
extended to roles and SoD controls.

**Open.** `05-04` must be extended to SOD-30, with each control's definition taken from the
module that introduced it.

**Governance consequence — RG-01 extended.**

> **RG-01 (extended).** Register-first applies to **every programme-wide identifier space**, not
> only modules and requirements: `KPI-`, `CD-`, `SOD-`, `R`, `RSK-`, `DEP-`, `D-`, `NFR-`. No
> module file may introduce an identifier in a shared space that does not already exist in its
> owning register.

---

### H2-07 — Roles R39–R46 used but unregistered; R54, R57, R60 undefined anywhere

`05-04` registers **R01 … R38**. Module files use up to **R46**, plus three orphans.

**Introduced but unregistered (definitions exist in module files):**

| Role | Introduced in | Definition given |
|---|---|---|
| R39 Data Steward | M33 | Yes — but **contested**: M43 and M64 both raise it as an open question |
| R40 Chief Data Officer | M33 and 8 others | Yes, used consistently across 9 modules |
| **R41 Payroll Officer** | **M56** | Yes — prepare only, cannot approve or release |
| **R42 Training Coordinator** | **M22** | Yes |
| **R43 Competency Assessor** | **M22** | Yes — scoped assessment authority |
| **R44 HSE Officer** | **M59** | Yes |
| **R45 Recruiter** | **M58** | Yes — cannot approve an offer |
| **R46 Occupational Health** | **M59** | Yes — sole access to medical detail |

**Used with no definition anywhere:**

| Role | Used in | Problem |
|---|---|---|
| **R54** | M39 | Referenced as "R54-scope FP&A users"; no definition exists |
| **R57** | M46 | Referenced in a data-restriction rule; no definition exists |
| **R60** | M10, M63 | Labelled "GRC / Internal Audit" in M63 — **but that is R32's role**, so R60 is a duplicate identity for an existing role |

**R60 is the serious one.** Two identifiers for the same role means an access-control rule
written against R32 does not apply to a user granted R60, and vice versa. In a permission
model, a duplicate role identity is a live security defect, not a documentation defect.

**Open.** Extend `05-04` to R46 with the definitions already written in the module files; then
resolve R54 and R57 (define or remove), and **eliminate R60 in favour of R32**.

---

### H2-08 — Programme effort is 1,513 PW against 834 PW in the approved business case

Now that every category is counted rather than estimated:

| | Approved plan (30 modules) | **Measured (65 of 67 specs)** | Change |
|---|---:|---:|---:|
| Requirements | 1,180 | **2,930** | **+148%** |
| Build effort | 834 PW | **1,513 PW** | **+81%** |

`00-02` §6 and `06-02` §3.3 model **$290K–$470K** of implementation and custom development
against 834 PW. At 1,513 PW the same unit rates give approximately **$525K–$855K**, moving the
3-year TCO from **$455K–$780K** to approximately **$690K–$1,150K**.

**The estimating model failed in a specific, explicable way.** Requirement count was
under-estimated wherever a category carries statutory, contractual or master-data obligations —
F **+73%**, H **+52%**, I **+44%**, C **+39%**, G **+29%** — and estimated accurately where the
category is purely operational — D **0%**, J **+12%**. Effort tracked closer than count (+15%
aggregate), because statutory requirements are numerous but individually small: most resolve to
configuration in a versioned rule pack rather than new code.

**Escalated as decision D-14.** This is a Steering Committee decision. The programme as
specified is roughly **1.8× the effort of the approved plan**. Funding it, phasing it across
more waves, or cutting scope are all legitimate answers — but the choice must be made with the
counted figure in front of the Committee, not absorbed silently across waves.

---

## 5. Medium and Low Findings

### H2-09 — Category H overview cited retired v1.0 identifiers *(Fixed)*

`_CATEGORY_OVERVIEW.md` §4 — the brand-certification control table, which is the strongest
argument in the category for HR capability protecting revenue — cited **`BRU-HRM-01`** and
**`AUT-041`**. Neither exists in the v2.1 scheme. Now restated against the real identifiers:
`FR-LMS-009`, `AUT-LMS-01`, `FR-LMS-012`, `BRU-LMS-03`, `AUT-LMS-02`, `FR-LMS-013`,
`BRU-LMS-02`, `FR-LMS-040`, `FR-LMS-038`, `KPI-265`.

### H2-10 — An absolute KPI target with no baseline *(Fixed)*

The overview carried *"new technician time to productivity < 21 days"*. No baseline exists —
the metric has never been measured. An absolute target against an unmeasured baseline cannot be
assessed as met or missed. Restated in M58 (KPI-279) and M22 (KPI-271) as a **35% reduction
against a baseline to be established**, with the reconciliation noted in the overview.

### H2-11 — M42 uses a four-character module code *(Accepted)*

Every module code in the estate is three characters. **M42 uses `SRM2`**, because `SRM` is
permanently allocated to M01 under RG-02. The file documents this explicitly and the reasoning
is correct — RG-02 forbids reusing a retired or allocated code. Accepted as a deliberate
exception; it should be recorded in the identifier conventions document when written.

### H2-12 — The "17+ brands" figure is unverified *(Open)*

The Category H overview builds its brand-certification argument on *"1000FiX is an authorised
service partner for 17+ brands"*, carried from the v1.0 BRD. This figure underpins M22's
coverage reporting (FR-LMS-014) and the KPI-264 target. It has not been verified against the
current principal agreement list. Marked provisional under RG-05; **M22 Q-02** requires written
confirmation from each principal of its certification requirement.

### H2-13 — Statutory tax figures rest partly on press reporting *(Open, flagged in-module)*

The AY 2026–27 tax parameters used in M56 — thresholds, minimum tax, rebate rate and cap —
were verified on 2026-08-12, but **sources conflict on whether the 5% introductory slab
survives**. This is flagged as **M56 Q-01** with a hard warning that *"the statutory pack must
be built from the enacted Finance Act, not from press reporting"*, and every figure is marked
provisional under RG-05.

This is the correct handling and no correction is required — but it is recorded here because
it is the single most consequential open uncertainty in Category H. Building a payroll tax pack
from press reporting is how payroll goes wrong for every employee simultaneously.

### H2-14 — Markdown table-style lint warnings *(Accepted)*

The editor reports `MD060/table-column-style` warnings on alignment markers (`|:--:|`) and
`MD025` on multiple H1s. These are consistent across all 65 module files and every governance
document; the style is uniform and renders correctly. No change — enforcing the linter's
preference would touch every file in the repository for no reader benefit.

---

## 6. What the Category H Specifications Got Right

The audit found no defects in the seven Category H files themselves beyond the shared
identifier-space problems (H2-04 through H2-07), which are repository-wide and predate them.
Verified clean:

| Check | Result |
|---|---|
| Requirement ID contiguity, all 7 modules | **Clean** — count equals highest ID in every case |
| Requirement duplication | **None** |
| Requirement counts against `05-01` §1.3d | **Exact match** — 46, 52, 54, 42, 40, 34, 42 = 310 |
| KPI identifiers | **No collisions** anywhere in the repository |
| Role identifiers R41–R46 | **No collisions**; each defined once, in the module that introduces it |
| Cross-file references | **All resolve** — 7 of 7 targets exist |
| Scope boundary sections | Present in all 7, with explicit out-of-scope ownership tables |
| Boundary symmetry (RG-04) | Each module referenced by 5–7 of the other 6 |
| Regulatory citations | All carry `verified 2026-08-12` per DoD-17 |

---

## 7. Remediation Plan

| # | Action | Owner | Priority | Status |
|---|---|---|:--:|:--:|
| 1 | Correct `02-02` and README to counted figures | Documentation Squad | **Now** | ✅ **Done** |
| 2 | Adopt **RG-06** (count, do not consult) | Documentation Squad | **Now** | ✅ **Done** |
| 3 | Extend **RG-01** to all shared identifier spaces | Documentation Squad | **Now** | ✅ **Done** |
| 4 | Escalate the 1,513 PW figure to Steering as **D-14** | Programme Director | **Now** | ⬜ Open |
| 5 | **Eliminate R60 in favour of R32** — duplicate role identity | Security / IAM | **Now** | ⬜ Open |
| 6 | Extend `05-04` to **R46** and **SOD-30** | GRC | **Before W1 build** | ⬜ Open |
| 7 | Resolve or remove **R54** and **R57** | GRC | Before W1 build | ⬜ Open |
| 8 | Build the programme **KPI register**; reassign ~60 colliding IDs | Documentation Squad | Before `06-02` reissue | ⬜ Open |
| 9 | Make `02-05` the sole **CD allocator**; reassign all colliding IDs | Architecture | **Before any build contract** | ⬜ Open |
| 10 | Write **M66** and **M67** specifications | Documentation Squad | Before W6 | ⬜ Open |
| 11 | Resolve Category A's 28 unused requirement IDs — retire, do not renumber | Documentation Squad | Before W1 gate | ⬜ Open |
| 12 | Verify the **"17+ brands"** figure against principal agreements | Service Head | Before W5 | ⬜ Open |
| 13 | Verify AY 2026–27 tax parameters against the **enacted Finance Act** | CFO / tax advisor | **W5 minus 3 months** | ⬜ Open |

**Items 5 and 9 are the ones that become expensive if deferred.** A duplicate role identity is a
live permission defect. Colliding CD identifiers become real conflicts the moment a build
backlog is created from these documents.

---

## 8. Governance Rules Added

| Rule | Statement |
|---|---|
| **RG-06** | **Count, do not consult.** Any figure describing repository contents must be derived by direct enumeration of the files at the time of writing. A prior statement of the same figure — including one in the authoritative register — is not evidence. Every such figure carries the date it was counted. |
| **RG-01 (extended)** | Register-first applies to **every programme-wide identifier space**: `KPI-`, `CD-`, `SOD-`, `R`, `RSK-`, `DEP-`, `D-`, `NFR-`. No module file may introduce an identifier in a shared space that does not already exist in its owning register. |

Both are added to `02-02` §2 alongside RG-02 through RG-05.

---

## 9. Sources

**Regulatory, verified 2026-08-12**
Bangladesh Labour Act 2006 (as amended) — gratuity at wages of not less than 30 days per
completed year at the last-drawn rate; Provident Fund formation on written demand by
three-quarters of workers; appointment letter and identity card mandatory at appointment;
service book; probation limits; Chapters V–VIII safety, health, hygiene, first aid, safety
committees, accident notification and compensation ·
Bangladesh Labour Rules 2015 — safety committee constitution, safety officer, first-aid
provision, accident reporting ·
NBR income tax AY 2026–27 — category thresholds BDT 375,000 / 425,000 / 500,000 / 525,000;
minimum tax BDT 5,000 (BDT 1,000 first-time); investment rebate 10% capped at BDT 750,000
eligible investment; **contested: the survival of the 5% introductory slab** ·
NBR withholding returns — frequency moved monthly → quarterly, deadlines 25 October,
25 January, 25 April, 25 July ·
Bangladesh Personal Data Protection Act 2026 — employees, candidates and health data as data
subjects; sensitive personal data residency restriction ·
ISO 9001:2015 clause 7.2 (competence evidence) and 7.1.4 · ISO 45001:2018

**Enterprise benchmark**
SAP SuccessFactors — Employee Central, Payroll, Time Tracking, Performance & Goals,
Compensation, Learning, Recruiting & Onboarding · SAP EHS Management ·
Oracle HCM — Global Payroll, Workforce Rewards, Talent Profile, Recruiting Cloud ·
Workday — Payroll, Talent, Learning, Recruiting · Microsoft Dynamics 365 Human Resources ·
Field-service practice: ServiceMax, Salesforce Field Service, IFS — technician scorecards and
skill-matrix-driven scheduling · Enablon, Intelex, Cority — mobile HSE reporting ·
OCA `hr_payroll_community`, `hr_appraisal`, `hr_skills`, `hr_attendance`, `hr_holidays` ·
Odoo 19 Community HR and Recruitment · Moodle

**Internal**
`00-06_Documentation_Audit_Report.md` (first audit) ·
`02-02_Module_Catalogue_Master_Register.md` ·
`05-01_Feature_and_Function_Register.md` §1.3d ·
`05-04_Role_Permission_and_Access_Matrix.md` ·
`05-06_NonFunctional_Requirements_and_Standards.md` §6 ·
`03_Modules/H_People_and_Workforce/` — all seven module specifications ·
Direct enumeration of `03_Modules/**/M*.md` (65 files)

---

*Audit 2 · 1000FiX ERP System v2.0 · Issued 2026-08-13 · CONFIDENTIAL*
