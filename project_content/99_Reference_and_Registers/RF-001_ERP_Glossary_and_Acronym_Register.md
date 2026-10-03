---
id: RF-001
title: ERP Glossary and Acronym Register
project: 1000FiX ERP System v2.0
content_type: Generic
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-18
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Enterprise Architecture
author: Enterprise Architecture with Programme Content Lead and Localisation Lead
reviewers: [CTO, Programme Content Lead, Localisation Lead, Content Design Lead, QA Lead, Legal & Compliance, Finance, Business Process Lead]
approver: Programme Content Lead
content_class: E
purpose: >
  The one place a reader can resolve any acronym, abbreviation or identifier prefix used anywhere
  in the 1000FiX ERP programme — 891 files across two repositories, 21 identifier families and
  two languages. The module repository lists `99-01_Glossary_and_Acronyms.md` as planned and it
  does not exist, so a new joiner, an implementation vendor, a brand partner's integration
  engineer and an external auditor currently decode `BRU-SRM-09`, `SOD-31`, `G4-10`, `PS-08` and
  `Mushak 6.6` by asking someone. This file removes that dependency and, in doing so, exposes
  four identifier defects that no prior audit had found because no document had ever enumerated
  the prefix space.
traces_to: [99-01, CG-004, CG-005, BN-003, BN-004, 02-02, 05-01, 05-02, 05-04, 05-05, 05-06, 04-00, 06-02, 00-04, RF-002, RF-003, RF-006, RF-008]
priority: P1
wave: W0
bilingual: yes
bn_counterpart: RF-001_ERP_Glossary_and_Acronym_Register_BN.md
sources:
  - source: 1000fix_ERP_Module/README.md and FOLDER_STRUCTURE.md — 99_Reference/99-01_Glossary_and_Acronyms.md listed as planned; 99_Reference/ contains only _Superseded/ (audit AUDIT-001 finding AF-15)
    verified: 2026-08-18
    class: P1
  - source: project_content/00_Content_Governance_and_Standards/CG-004_Terminology_and_Controlled_Vocabulary_Standard.md — the controlled business vocabulary and banned-synonym register; this file does not duplicate it (CP-01)
    verified: 2026-08-18
    class: P1
  - source: project_content/11_Localisation_Bengali/BN-003_Bilingual_Terminology_Glossary.md — the approved Bengali equivalent for every controlled term; authoritative for Bengali wording
    verified: 2026-08-18
    class: P1
  - source: project_content/00_Content_Governance_and_Standards/CG-005_Content_ID_and_Naming_Convention.md — content ID allocation, ranges, reservation, retirement
    verified: 2026-08-18
    class: P1
  - source: Identifier enumeration by regex extraction over 1000fix_ERP_Module/ (123 files) and project_content/ (463 files), run 2026-08-18. Every count in §4.2 is produced by that extraction, never by reading a document's claim about itself (RG-06, CP-11)
    verified: 2026-08-18
    class: P1
  - source: National Board of Revenue (Bangladesh) — Mushak form series 6.1, 6.2, 6.3, 6.6 and 9.1 under the Value Added Tax and Supplementary Duty Act 2012 with the VAT and SD Rules 2016; currency and citation governed by RF-008
    verified: 2026-08-18
    class: P2
supersedes: none
review_due: 2026-11-18
---

# RF-001 — ERP Glossary and Acronym Register

> **What this file is not.** It is not the business vocabulary. `CG-004` decides which English
> word means which business object, and `BN-003` decides its Bengali equivalent. Both are
> authoritative and neither is reproduced here — principle `CP-01`. This file resolves
> **acronyms, abbreviations and identifier prefixes**: the codes a reader meets in a document
> and cannot look up in a dictionary.

---

## 1. Purpose

A reader opening `M09_Warranty_Protection_Plans_and_Claims.md` at random meets, inside two
pages, `FR-WTY-018`, `BRU-SRM-09`, `AC-06`, `CD-041`, `INT-021`, `NFR-064`, `SOD-24`, `KPI-037`
and `DoD-17`. Nine identifier families, seven of them defined in a different document, none of
them defined in the one they are reading.

The module repository anticipated this. `FOLDER_STRUCTURE.md` and `README.md` both list
`99_Reference/99-01_Glossary_and_Acronyms.md`. Audit `AUDIT-001` finding **AF-15** records what
is actually on disk: `99_Reference/` contains only `_Superseded/`, and **all four planned
reference documents are absent**. The glossary has been planned for the whole life of the
programme and written by nobody.

The consequence is not inconvenience. It is that:

- **Vendors price ambiguity.** An implementation vendor reading a statement of work that cites
  `BRU-SRM-11` and `SOD-31` either asks (delay) or assumes (rework).
- **Auditors are given tours instead of documents.** An ISO 9001 surveillance auditor asking
  "what is `SOD-31`?" should receive a register, not an explanation.
- **Identifier defects stay invisible.** Nobody had counted the prefix space until this file was
  written. Counting it found four defects, set out in §4.3 — including 30 requirements still
  registered in `05-01` under a code whose only other home is a **superseded** document.

---

## 2. Scope

**In scope**

| Included | Why |
|---|---|
| Every identifier prefix in use across `1000fix_ERP_Module/` and `project_content/` | The reason the file exists |
| Programme, organisational and delivery acronyms | `CTO`, `PW`, `UAT`, `MDM`, `RACI`, `DoD`, `TCO` |
| Bangladesh statutory and tax abbreviations | `BIN`, `TIN`, `VDS`, `AIT`, `NBR`, `RJSC`, `Mushak 6.3` |
| Technology and standards acronyms | `OWL`, `OCA`, `WCAG`, `RPO`, `RTO`, `OTP`, `IVR`, `NEIR` |
| Bengali rendering guidance for acronyms | Which acronyms are transliterated, which stay Latin (`BN-004`) |
| Where each identifier family is **defined**, and how many members are **in use** | Enables the defect analysis in §4.3 |

**Out of scope** — and who owns it

| Excluded | Owner |
|---|---|
| Business terms and their approved English wording | `CG-004` |
| Bengali equivalents of business terms | `BN-003` |
| Do-not-translate and transliteration rules for brand and product names | `BN-004` |
| Content ID allocation, reservation and retirement mechanics | `CG-005` |
| The meaning of an individual requirement, rule or KPI | Its owning register — `05-01`, `05-05`, `06-02` |
| Whether an external standard cited here is current | `RF-008` |

---

## 3. Audience

| Reader | Uses this file to |
|---|---|
| **A new joiner** | Read any programme document in week one without a mentor |
| **An implementation vendor** | Price and plan against identifiers rather than against explanations |
| **A brand partner or corporate integration engineer** | Decode `INT-`, `FR-POR-` and event names in `AP-003` |
| **An external auditor** | Resolve a control identifier to its register without an interview |
| **A translator** | Know which codes are never translated (`BN-004`) and which acronyms are read aloud |
| **The Programme Content Lead** | Detect identifier-space exhaustion and collision before it costs an audit |

---

## 4. Content

### 4.1 How to read this register

| Column | Meaning |
|---|---|
| **Prefix** | The literal token as it appears in text, with its numeric form |
| **Expansion** | What the letters stand for |
| **Defined in** | The single document that is authoritative for allocating members of this family |
| **In use** | Distinct members found by extraction on **2026-08-18**. A *floor*, not a ceiling — see §4.9 |
| **Registered** | How many the defining document actually registers, where that differs |
| **Notes** | Collisions, exhaustion, non-conformance |

**Three reading rules.**

1. **A prefix is not a namespace unless one document owns it.** Where two documents allocate the
   same prefix, that is recorded as a collision, not as a style difference.
2. **Two digits and three digits are different families.** `DM-01` is a data-model standard in
   `05-02`; `DM-001` is a content file in Category 12. `LG-01` is an audit finding; `LG-001` is a
   content file. This is a genuine hazard and is called out at every affected row.
3. **Counts carry an enumeration instant.** Any figure in §4.2 quoted elsewhere must be
   re-generated, not copied (`CP-11`, `CM-R2`).

---

### 4.2 Identifier prefix register

#### 4.2.1 Requirement and specification families

| Prefix | Expansion | Defined in | In use | Registered | Notes |
|---|---|---|---:|---:|---|
| `FR-<CODE>-nnn` | Functional Requirement | `05-01_Feature_and_Function_Register.md` | **3,350** (M ∪ P) | 200 | See §4.3 defect **GL-01**. `<CODE>` is the owning module's three-letter code |
| `NFR-nnn` | Non-Functional Requirement | `05-06_NonFunctional_Requirements_and_Standards.md` | 104 | 104 | Suffixed variants `NFR-086a/b/c` are in use. **`NFR-088`…`NFR-092` are each used for two different requirements** — `AUDIT-016` **AP-02** |
| `AC-nn` | Acceptance Criterion | Each module file §15 | file-local | — | Not a programme-wide namespace. `AC-06` in `M09` and `AC-06` in `M16` are unrelated |
| `BRU-<CODE>-nn` | Business RUle | `05-05_Business_Rules_and_Automation_Catalogue.md` | **1,358** | — | 72 family codes. `05-05` carries **no rule for `M40` or `M42`** — `AUDIT-018` **EO-02** |
| `BR-STD-nn` | Business Rule, STanDard (cross-cutting) | `05-05` §1 | 6 | 6 | Applies to every module; `BR-STD-04` and `BR-STD-06` are the two most cited in this content set |
| `AUT-<CODE>-nn` | AUTomation rule | `05-05` and module §11 | 396 refs | — | Trigger–action–exception triples |
| `CD-nnn` | Component / Custom Development | `02-02_Module_Catalogue_Master_Register.md` | **199** | 199 | Space was exhausted once already — the twelve portals were reallocated `+26` after a whole-range collision (portal audit `X-01`, cited in `CG-005`) |
| `INT-nnn` | INTegration | `05-03_Integration_and_API_Catalogue.md` | **47** | 47 | `INT-013` email is omitted from the `05-03` §7 P0 fallback register — `AUDIT-017` **OP-03** |
| `IP-nn` | Integration Principle | `05-03` §1 | 10 | 10 | `IP-04` idempotency, `IP-08` OpenAPI 3.1 / JSON Schema, `IP-09` manual fallback, `IP-10` minimisation |
| `PS-nn` | Portal Standard | `04-00_Portal_Suite_Overview.md` §3 | 12 | 12 | `PS-03` bilingual, `PS-04` WCAG, `PS-06` one component library, `PS-08` offline, `PS-09` actionable errors |
| `DM-nn` | Data-Model standard | `05-02_Data_Model_and_Entity_Catalogue.md` | 15 | 15 | **Collides visually with `DM-nnn` content files.** Always cite as `05-02` `DM-nn` |
| `SOD-nn` | Segregation Of Duties | `SP-006_Segregation_of_Duties_Register.md` | **61** | 61 | `05-04` §6 registers only `SOD-01`…`SOD-12`; `SP-006` closed `00-07` **H2-06** by registering `SOD-13`…`SOD-60` |
| `KPI-nnn` | Key Performance Indicator | `06-02_KPI_Benefits_and_Acceptance_Criteria.md` | **291** | 95 | `AUDIT-015` **RP-01** re-diagnosed `00-07` H2-04 as **an exhausted register**, not 22 collisions |
| `Gn-nn` | Gate criterion | `06-02` §4 | `G1`…`G4` | — | `G4-10` is unanswerable today — `AUDIT-014` **TS-01** |
| `DoD-nn` | Definition of Done (module) | `02-02` §DoD | 17 | 17 | `DoD-17` requires a verified-on date on every regulatory citation |
| `TD-nn` | Technology Decision | `02-05_Technology_Stack_and_Build_vs_Buy.md` | 15+ | — | `TD-01` Odoo 19 CE as ERP core |

#### 4.2.2 Governance, risk and delivery families

| Prefix | Expansion | Defined in | In use | Notes |
|---|---|---|---:|---|
| `RSK-nnn` | RiSK | `00-04_Risks_Assumptions_Dependencies_and_Governance.md` | **36** | Programme risks. Content risks are `CR-nn` in `RF-011` — deliberately a separate space |
| `AS-nn` | ASsumption | `00-04` | 15 | |
| `DEP-nn` | DEPendency | `00-04` | 35 | `DEP-31` is the split-residency legal opinion that gates `D-13` |
| `D-nn` | Decision | `00-04` §6 | 15 | **Collision — see §4.3 defect `GL-03`** |
| `Q-nn` | Question to the business | Module file §17 | file-local | Not a programme namespace |
| `RG-nn` | Register Governance rule | `00-07` and `02-02` | 7 (+`RG-08` proposed) | `RG-01` register-first; `RG-06` enumerate, never project |
| `CP-nn` | Content Principle | Content Master Index §2 | 11 | `CP-01`…`CP-11` |
| `CM-Rn` | Content Maintenance Rule | Content Master Index §9 | 10 | `CM-R1`…`CM-R10` |
| `AF-nn` | Audit Finding (repository) | `AUDIT-001` | 18 | The only cross-repository finding series |
| `<CC>-nn` | Audit finding, category audit | `AUDIT-002`…`AUDIT-018` | 232 | **Two digits.** `LG-01` is a finding; `LG-001` is a file. See `RF-012` §4.4 |
| `O-nn` | Open item, file-local | Each content file | **1,185** distinct across 187 files | Not a namespace. `RF-006` §4.6 is where they are consolidated |
| `OP-nnn-OI-nn` | Open Item, qualified | Category 17 `OP` files | **109** | The only category that qualified its open items with the owning file. Recommended as the standard — `RF-006` `CD-07` |

#### 4.2.3 Content families — the 21 category codes

Allocation, ranges and retirement are governed by `CG-005`; this table exists so a reader who
meets `EO-011` in a sentence can resolve it without opening the Master Index.

| Code | Category | Range | Folder |
|---|---|---|---|
| `CG` | Content Governance & Standards | `CG-001`–`CG-014` | `00_Content_Governance_and_Standards/` |
| `VB` | Voice, Brand & Design-System Content | `VB-001`–`VB-010` | `01_Voice_Brand_and_Design_Content/` |
| `MD` | Master Data & Configuration Seed Content | `MD-001`–`MD-048` | `02_Master_Data_and_Configuration/` |
| `UI` | UI Copy & Microcopy | `UI-001`–`UI-042` | `03_UI_Copy_and_Microcopy/` |
| `NT` | Notification & Messaging Content | `NT-001`–`NT-026` | `04_Notification_and_Messaging/` |
| `DT` | Document, Print & Statutory Output Templates | `DT-001`–`DT-044` | `05_Document_and_Print_Templates/` |
| `SP` | Process, SOP & Workflow Content | `SP-001`–`SP-034` | `06_Process_SOP_and_Workflow/` |
| `KB` | Knowledge Base & Technical Library | `KB-001`–`KB-016` | `07_Knowledge_Base_and_Technical_Library/` |
| `TR` | Training & Enablement | `TR-001`–`TR-024` | `08_Training_and_Enablement/` |
| `HC` | Help Centre & Self-Service | `HC-001`–`HC-020` | `09_Help_Centre_and_Self_Service/` |
| `LG` | Legal, Policy & Compliance | `LG-001`–`LG-024` | `10_Legal_Policy_and_Compliance/` |
| `BN` | Localisation & Bilingual Content | `BN-001`–`BN-018` | `11_Localisation_Bengali/` |
| `DM` | Data Migration Content | `DM-001`–`DM-014` | `12_Data_Migration_Content/` |
| `TS` | Test & Acceptance Content | `TS-001`–`TS-018` | `13_Test_and_Acceptance_Content/` |
| `RP` | Reporting, Analytics & KPI Content | `RP-001`–`RP-016` | `14_Reporting_Analytics_and_KPI/` |
| `AP` | Integration & Developer Content | `AP-001`–`AP-012` | `15_Integration_and_Developer_Content/` |
| `CM` | Change Management & Communications | `CM-001`–`CM-018` | `16_Change_Management_and_Comms/` |
| `OP` | Operations, Support & Runbooks | `OP-001`–`OP-016` | `17_Operations_Support_and_Runbooks/` |
| `EO` | Ecosystem Onboarding Content | `EO-001`–`EO-014` | `18_Ecosystem_Onboarding_Content/` |
| `MM` | Multimedia & Asset Specifications | `MM-001`–`MM-012` | `19_Multimedia_and_Asset_Specs/` |
| `RF` | Reference & Registers | `RF-001`–`RF-012` | `99_Reference_and_Registers/` |

**Five identifiers are proposed and unallocated:** `TR-025`, `BN-019`, `DM-015`, `DM-016`,
`SP-035`. They are cited in existing files as though registered. `RF-007` §4.3 holds them; the
register total does not move until the Steering Committee acts.

#### 4.2.4 Module and portal identifiers

| Prefix | Meaning | Range | Defined in |
|---|---|---|---|
| `Mnn` | Module specification | `M01`–`M67` | `02-02` |
| `Pnn` | Portal or application specification | `P01`–`P12` | `04-00` |
| `A`…`K` | Module category letter | 11 categories | `02-01`, `03_Modules/` |

> **Filing caveat.** All twelve `P*` files are on disk in
> `03_Modules/K_Platform_and_Technology/`, not in `04_Portals_and_Applications/` as the approved
> structure requires. This is audit finding **AF-01**, open and awaiting a CTO decision. A path
> quoted for a portal specification is wrong in one of the two documents whichever you choose;
> cite the identifier, not the path.

#### 4.2.5 The three-letter module code vocabulary

Sixty-eight codes are in use as the `<CODE>` element of `FR-` identifiers, and seventy-two as the
`<CODE>` element of `BRU-` identifiers. The two vocabularies are **not the same set** — see §4.3
defect `GL-02`.

`ADM` `AIM` `APE` `ARB` `AST` `BFO` `BID` `BIL` `BPA` `CAI` `CAT` `CCE` `CPM` `CRM` `CTR` `CWM`
`CXM` `DAT` `DMS` `DPL` `DTS` `EAM` `ECM` `ESG` `FAC` `FIN` `FLT` `FPA` `FRD` `FSM` `FXA` `GLO`
`GRC` `HCM` `HRM` `HSE` `INV` `IOT` `IPF` `ITC` `ITS` `KMS` `LMS` `LOG` `LOY` `MDM` `MKP` `MKT`
`PAY` `PCM` `PIC` `POR` `PPM` `PRC` `PRO` `PRT` `QMS` `QTE` `REV` `RMS` `RNT` `SCM` `SEC` `SLS`
`SRM` `SRM2` `SUB` `TAO` `TAX` `TRE` `TRF` `WFM` `WMS` `WSR` `WTY`

Six that a reader will misread without help:

| Code | Reads as | Actually means |
|---|---|---|
| `SRM` | Supplier Relationship Management | **Service Request Management** (`M01`) |
| `SRM2` | A version | **Supplier Relationship Management** (`M42`) — a collision workaround, defect `GL-02` |
| `FRD` | Fraud | **FRont Desk** (`M04`) |
| `POR` | Portfolio | **PORtal** — the portal requirement space, 358 requirements across `P01`–`P12` |
| `DTS` | Date/Time Standard | **Data & Technology Services** (`M06` data services) |
| `WSR` | Web Service Request | **WorkShop Repair** (`M31`) |

---

### 4.3 Four identifier defects found by enumerating the prefix space

No prior audit examined the prefix space as a space. Extraction on 2026-08-18 found four defects.
All four are reported here and carried to `RF-006` as decisions and to `RF-012` as findings.

#### `GL-01` — the functional-requirement denominator is one of four numbers, and none of them is 2,930

**What was found.**

| Enumeration | Distinct `FR-` identifiers |
|---|---:|
| The 67 module files `M*.md` | **2,992** |
| The 12 portal files `P*.md` | **376** (of which 358 are `FR-POR-`) |
| Modules ∪ portals | **3,350** |
| The whole module repository, including cross-cutting specs and superseded pillars | **3,537** |
| Registered in `05-01_Feature_and_Function_Register.md` | **200** |
| `05-01`'s own title claim | "~2,352" |
| `README.md` §Total claim | "2,930 ⚠" |
| `AUDIT-014` **TS-01**, the three denominators it found | 2,930 / ~2,352 / 3,343 |

**Why it matters.** `AUDIT-014` established that requirement-to-script coverage is unanswerable
because the denominator is contested, and instructed that no percentage may be quoted. That
instruction stands, but the cause is now precisely located: **`05-01` is not a register of the
requirements, it is a summary of them.** It carries 200 identifiers and describes ~2,352.
`README.md`'s 2,930 is close to the module-only figure of 2,992 and is best explained as a count
taken before the last module edits. The correct programme figure, stated with its scope, is
**3,350 across modules and portals, enumerated 2026-08-18**.

**Remediation.** `RF-003` §4.2 adopts 3,350 as the traceability denominator, with the scope
statement attached. `05-01` must be restated (`AF-06`, open). This closes the *diagnosis* of
`AF-06` and `TS-01`; it does not close the restatement, which is the CTO's.

#### `GL-02` — the module code vocabulary is two vocabularies, and one code is a collision workaround

`FR-` uses 68 codes; `BRU-` uses 72. The set difference:

| Direction | Codes | Consequence |
|---|---|---|
| In `FR-`, not in `BRU-` | `POR` | The 358 portal requirements have **no business rules at all**. Portals inherit module rules implicitly and nothing states that |
| In `BRU-`, not in `FR-` | `BIL`, `CWM`, `HRM`, `PRT`, `SCM` | Five rule families govern behaviour with no requirement family behind them |

**`SRM2` is the visible symptom.** `M42 Supplier Relationship and Performance` needed `SRM`; `M01
Service Request Management` already held it. Rather than allocate a fresh code, the author
appended a digit, producing **34 requirements** whose identifier does not match the stated
`FR-<three letters>-<nnn>` pattern. Any regular expression written to the stated pattern silently
drops all 34. Mine did, on the first pass, and that is how the defect was found.

**Remediation.** `CG-005` must state the module-code allocation rule and reserve the space.
Carried to `RF-006` as decision `CD-11`.

#### `GL-03` — `D-nn` means two different things in two governance documents

| Document | `D-01` means |
|---|---|
| `00-04` §6 | *Approve the expanded scope, budget and 36-month horizon* — Board / CEO |
| `03_Modules/E_Supply_Chain_and_Inventory/_CATEGORY_E_AUDIT_REPORT.md` §Decisions | *Ownership class is a mandatory, non-nullable dimension on every stock quant and move* — `M15` |

Both documents number from `D-01`. `D-03` is the single most-cited decision in the whole
workspace (81 references) and resolves to the marketplace principal-or-agent determination in one
document and to opening-balance methodology in the other. **`RF-006` cannot be a decision log
until this is resolved.** `RF-006` §4.2 allocates `PD-nn` for programme decisions and `CD-nn` for
content decisions, and maps the legacy `D-nn` space explicitly.

#### `GL-04` — `FR-SLS-` registers 30 requirements whose only other home is superseded

`FR-SLS-001`…`FR-SLS-030` appear in exactly two places: `05-01_Feature_and_Function_Register.md`
and `99_Reference/_Superseded/SUPERSEDED_Pillar_B_Customer_Commercial_Revenue.md`. No module file
uses the code. `05-01` therefore carries thirty requirements inherited from the v1.0 pillar
architecture that the v2.0 module architecture replaced.

`FR-BFO-` is the same failure in miniature: three identifiers surviving in `M04`, `00-06` and
`05-01` after audit `C-03` reverted `M04` to the code `FRD`.

**Remediation.** Both belong in the `05-01` restatement. Carried to `RF-007` as backlog item
`BL-14` and to `RF-012` as a finding against `05-01`.

---

### 4.4 Programme and organisational acronyms

Bengali column: **T** = transliterate into Bengali script; **L** = keep Latin, per `BN-004`.
Where a Bengali form is given it is the form `BN-003` binds or, where `BN-003` is silent, the
form proposed here for `BN-003` adoption — marked *(proposed)*.

| Acronym | Expansion | Bengali | Note |
|---|---|---|---|
| **AMC** | Annual Maintenance Contract | L | Product name; never translated (`BN-004`, `VB-010`) |
| **BA** | Business Analyst | L | |
| **BI** | Business Intelligence | L | |
| **BRD** | Business Requirements Document | L | `primary-doc/1000FiX_ERP_System_Comprehensive_BRD.md` |
| **CAB** | Change Advisory Board | L | `SP-031` |
| **CAPA** | Corrective And Preventive Action | L | ISO 9001 vocabulary; never paraphrased (`UI-031`) |
| **CDO** | Chief Data Officer | L | **Unappointed.** Decision `D-15` |
| **CFO / CEO / CTO** | Chief Financial / Executive / Technology Officer | L | |
| **CSAT** | Customer SATisfaction | L | `06-02` KPI family |
| **DoA** | Delegation of Authority | L | `SP-004` |
| **DoD** | Definition of Done | L | `CG-008` for content; `02-02` for modules |
| **DPIA** | Data Protection Impact Assessment | L | **None exists.** `AUDIT-016` **AP-08** |
| **DPO** | Data Protection Officer | L | **Unappointed.** `AP-012` `RF-001-OI-06` |
| **EAM** | Enterprise Asset Management | L | `M45` |
| **EPR** | Extended Producer Responsibility | L | `LG-018`, `MD-047` — see `RF-008` `ST-14` |
| **ESG** | Environmental, Social and Governance | L | |
| **FTE** | Full-Time Equivalent | L | |
| **HSE** | Health, Safety and Environment | L | `M59`, `SP-030` |
| **ISMS** | Information Security Management System | L | `LG-021` |
| **KPI** | Key Performance Indicator | L | `RP-001`, `06-02` |
| **L&D** | Learning and Development | L | Owner of Category 08 `TR` |
| **MDM** | Master Data Management | L | `M64`, `MD-001`. **Never** Mobile Device Management |
| **MSP** | Managed Service Provider | L | `M05`, `MD-032` |
| **NCR** | Non-Conformance Report | L | ISO 9001 vocabulary (`DT-043`) |
| **NPS** | Net Promoter Score | L | `NT-024` |
| **PDPA** | Personal Data Protection Act 2026 | L | Statute; see `RF-008` `ST-05` and §4.6 below |
| **PMO** | Programme Management Office | L | |
| **POD** | Proof Of Delivery | L | `DT-028` |
| **PW** | Person-Week | L | The programme's effort unit. 1,513 PW build, 520–775 PW content |
| **RACI** | Responsible, Accountable, Consulted, Informed | L | `CG-002` |
| **RAMC** | Renewable Annual Maintenance Contract | L | Product name (`VB-010`) |
| **RFQ** | Request For Quotation | L | `DT-022` |
| **RMM** | Remote Monitoring and Management | L | Decision `D-07` |
| **RPO / RTO** | Recovery Point / Time Objective | L | `NFR-007`: 15 min / 2 h |
| **SIT / UAT** | System Integration Testing / User Acceptance Testing | L | `TS-003`–`TS-011` |
| **SLA** | Service Level Agreement | L | `MD-028`, `DT-031`, `LG-015` — must reconcile exactly |
| **SME** | Subject Matter Expert | L | Not *small and medium enterprise*; that is spelled out |
| **SoD** | Segregation of Duties | L | `SP-006`. Written `SOD-nn` as an identifier, `SoD` in prose |
| **TCO** | Total Cost of Ownership | L | $620K–$1,050K provisional, decision `D-14` |
| **TM / TB** | Translation Memory / Term Base | L | `BN-008` |
| **VDS** | VAT Deducted at Source | T — **ভিডিএস** *(proposed)* | `DT-013`, `MD-037` |
| **WIP** | Work In Progress | L | Workshop vocabulary (`SP-010`, `UI-026`) |

---

### 4.5 Bangladesh statutory, tax and regulatory abbreviations

Currency of every instrument named here is `RF-008`'s responsibility, not this file's. The
verified-on date shown is the date the **name and meaning** were checked, not the date the
instrument's content was verified.

| Abbreviation | Expansion | Bengali | What it is for | Verified |
|---|---|---|---|---|
| **AIT** | Advance Income Tax | L | Advance tax collected/deducted at source; excluded from landed cost per decision `D-04` (Category E) | 2026-08-18 |
| **BIN** | Business Identification Number | L | The VAT registration number. Mandatory on `DT-010` Mushak 6.3 | 2026-08-18 |
| **BSTI** | Bangladesh Standards and Testing Institution | L | Standards body | 2026-08-18 |
| **BTRC** | Bangladesh Telecommunication Regulatory Commission | L | Owns the DND register (`NT-003`) and NEIR (`MD-021`) | 2026-08-18 |
| **CD / RD / SD** | Customs Duty / Regulatory Duty / Supplementary Duty | L | Inventoriable import duties (`M44`, `MD-037`) | 2026-08-18 |
| **DND** | Do Not Disturb | L | BTRC register; promotional SMS is prohibited to registered numbers (`NT-003`) | 2026-08-18 |
| **DoE** | Department of Environment | L | E-waste EPR registration authority (`LG-018`) | 2026-08-18 |
| **DNCRP** | Directorate of National Consumer Rights Protection | L | Complaint authority under the Consumer Rights Protection Act 2009 | 2026-08-18 |
| **Mushak 6.1** | মূসক ৬.১ — Purchase register | T | Statutory purchase book (`DT-012`) | 2026-08-18 |
| **Mushak 6.2** | মূসক ৬.২ — Sales register | T | Statutory sales book (`DT-011`) | 2026-08-18 |
| **Mushak 6.3** | মূসক ৬.৩ — Tax invoice | T | **The** statutory VAT invoice (`DT-010`). Never translated as "invoice" alone | 2026-08-18 |
| **Mushak 6.6** | মূসক ৬.৬ — VDS certificate | T | Issued to a supplier when VAT is deducted at source (`DT-013`) | 2026-08-18 |
| **Mushak 9.1** | মূসক ৯.১ — VAT return | T | The monthly return (`DT-014`). Filing basis: `RF-008` `ST-03` | 2026-08-18 |
| **NBR** | National Board of Revenue | L | Tax authority. `M51` files to it | 2026-08-18 |
| **NDMA** | National Data Management Authority | L | The PDPA 2026 supervisory authority (`LG-012`, `AP-012`) | 2026-08-18 |
| **NEIR** | National Equipment Identity Register | L | BTRC IMEI register (`MD-021`) | 2026-08-18 |
| **NID** | National Identity (card / number) | L | Sensitive personal data, S3 class (`MD-012`, `05-02` §10) | 2026-08-18 |
| **PDPA** | Personal Data Protection Act 2026 | L | See §4.6 | 2026-08-18 |
| **PDPO** | Personal Data Protection Ordinance 2025 | L | **Superseded.** See §4.6 | 2026-08-18 |
| **PF** | Provident Fund | L | Statutory deduction (`MD-043`) | 2026-08-18 |
| **RJSC** | Registrar of Joint Stock Companies and Firms | L | Companies Act 1994 filings (`RP-009`) | 2026-08-18 |
| **TIN** | Taxpayer Identification Number | L | Income-tax identifier, distinct from BIN | 2026-08-18 |
| **VAT / SD** | Value Added Tax / Supplementary Duty | T — **মূসক** | Act 2012, Rules 2016 (`RF-008` `ST-02`) | 2026-08-18 |

#### 4.6 `PDPA` and `PDPO` — the one abbreviation this content set gets wrong in six places

Extraction found **two names for the data-protection statute** across `project_content/`:

| Name used | Occurrences |
|---|---:|
| Personal Data Protection **Act 2026** | 50 |
| Personal Data Protection **Ordinance 2025** | 6 |

Both were correct when written. The verified sequence is:

| Date | Event |
|---|---|
| 6 November 2025 | Personal Data Protection **Ordinance** 2025 issued by the President |
| 5 February 2026 | Personal Data Protection (Amendment) Ordinance 2026 (Ordinance 23 of 2026) — amends the residency requirement for critical information infrastructure and restricted data |
| April 2026 | Parliament **repeals the Ordinance** and passes the permanent Personal Data Protection **Act 2026** (Law 63 of 2026) |
| ~May 2027 | End of the 18-month compliance window measured from gazette publication |

**Ruling.** The correct citation across the whole content set is **Personal Data Protection Act
2026 (Act 63 of 2026)**, noting the Ordinance lineage where the residency amendment is relied on
— which is precisely where `NFR-086a/b/c` and `LG-012` rely on it. The six `Ordinance 2025`
citations are not wrong about the law; they are **stale about its instrument**, which is exactly
the failure `RSK-035` and `DoD-17` exist to prevent.

**Remediation.** Six files to correct; listed with paths in `RF-008` `ST-05`. Carried to
`RF-012` as finding `RF-05`.

---

### 4.7 Technology, standards and channel acronyms

| Acronym | Expansion | Note |
|---|---|---|
| **A2P** | Application-to-Person (SMS) | The company's SMS class; masking rules in `NT-004` |
| **BEFTN** | Bangladesh Electronic Funds Transfer Network | `MD-038`, `M50` |
| **CLDR** | Common Locale Data Repository (Unicode) | Authority for `bn` formats (`BN-007`) |
| **GSM-7 / UCS-2** | SMS character encodings | Latin SMS segments at 160 chars; **Bengali at 70** (`NT-004`, `BN-014`) |
| **IVR** | Interactive Voice Response | Hotline 16743 (`NT-019`, `BN-017`) |
| **MFA** | Multi-Factor Authentication | `M29`, `UI-005` |
| **OCA** | Odoo Community Association | Module source for `TD-01` |
| **OTP** | One-Time Password | An anti-phishing control, not a convenience (`NT-007`) |
| **OWL** | Odoo Web Library | The Odoo 19 front-end framework — one of five in the estate |
| **PGW** | Payment Gateway | bKash PGW tokenised checkout (`AP-009`) |
| **RFC 9457** | Problem Details for HTTP APIs | The error-envelope standard `API-04` diverges from (`AUDIT-016`) |
| **SLA / SLO** | Service Level Agreement / Objective | SLA is contractual; SLO is internal |
| **WCAG** | Web Content Accessibility Guidelines | Contractual level: **2.1 AA** (`PS-04`). Current W3C Recommendation: **2.2** — `RF-008` `ST-11` |
| **XLIFF / TMX / TBX** | Localisation interchange formats | `BN-008` |

---

### 4.8 Bengali handling of acronyms

Governed by `BN-004`; summarised here because acronym rendering is the single most common
localisation query.

| Class | Rule | Example |
|---|---|---|
| Statutory form names | **Never translated, never transliterated in a document title.** Latin form retained, Bengali gloss permitted once | `Mushak 6.3` stays `Mushak 6.3`; মূসক ৬.৩ may appear as a gloss |
| Brand and product names | Never translated | `bKash`, `Nagad`, `AMC`, `RAMC` |
| Technical identifiers | Never translated, never transliterated | `FR-WTY-018`, `fix.service.order`, IMEI, model numbers |
| Organisational acronyms | Latin retained on internal surfaces | `RACI`, `CAPA`, `NCR` |
| Customer-facing acronyms | Expanded in Bengali on first use, then Latin | `OTP` → ওয়ান-টাইম পাসওয়ার্ড (OTP) |
| Bengali numerals | Bengali digits on customer and field surfaces; Latin digits inside identifiers, always | `BN-006`, `BN-007` |

> **The rule that catches people.** An identifier never takes Bengali digits. `মূসক ৬.৩` is
> acceptable prose; `Mushak ৬.৩` in a `traces_to:` field or a file name is a defect, because the
> string is then unsearchable.

---

### 4.9 What this enumeration is, and what it is not

Every count in §4.2 is a **floor taken at a moment**, not a ceiling.

| Property | Value |
|---|---|
| Enumeration instant | **2026-08-18** |
| Method | Regex extraction over 123 files in `1000fix_ERP_Module/` and 463 files in `project_content/` |
| Known in-flight authoring at the instant | **Category 19 `MM`.** `MM-001` did not exist at 01:07 and existed at 01:18 on 2026-08-18 |
| Rule invoked | `RG-06` (enumerate, never project) and proposed `RG-08` (an enumeration taken during authoring is a floor) |

This is the same condition `AUDIT-016` **AP-17** reported when the 427 figure was superseded by
428 four minutes later. It is recorded here rather than smoothed over, because a register that
quietly rounds its own uncertainty teaches every reader to distrust the next figure.

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| `CG-004` | Owns business terminology; this file must not contradict it |
| `BN-003` | Owns Bengali wording; the Bengali column here is bound to it |
| `BN-004` | Owns do-not-translate and transliteration rules |
| `CG-005` | Owns content ID allocation; §4.2.3 restates its ranges only |
| `05-01`, `05-05`, `05-06`, `06-02`, `02-02`, `05-03`, `05-04` | Own their identifier families; this file records where they are, not what they say |
| `RF-008` | Owns currency of every external standard and statute named in §4.5 and §4.7 |
| `RF-006` | Receives the four decisions raised in §4.3 |
| `RF-012` | Receives the findings raised in §4.3 and §4.6 |

| Depended on by | Why |
|---|---|
| `RF-002`, `RF-003`, `RF-004`, `RF-005` | All four cite identifier families this file defines |
| `TR-022`, `CM-018`, `EO-001`, `AP-001` | Onboarding and developer content that must expand codes for external readers |
| `BN-016` | Decides what of this file is translated |

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | **Every wave boundary**, with `RF-012` |
| Trigger for out-of-cycle review | A new identifier family; a collision; an identifier space reaching 90% of its allocated range; a statute renamed |
| Enumeration rule | §4.2 counts are **regenerated by extraction**, never edited by hand (`CP-11`, `CM-R2`). The enumeration instant in §4.9 is updated in the same commit |
| Bengali counterpart | `RF-001_..._BN.md` — **not yet written.** §4.4–§4.7 Bengali columns are the source rows |
| Owner | Enterprise Architecture |
| Escalation | A collision between two owning documents goes to the CTO, not to the Content Lead — the Content Lead cannot renumber a specification |

---

## Approval Record

| Gate | Required for Class E | Reviewer | Status |
|---|:--:|---|---|
| G1 Editorial | ● | Content Design | **Not started** |
| G2 Factual | ● | Enterprise Architecture with CTO | **Not started** |
| G3 Technical | ○ | — | Not required |
| G4 Linguistic | ◐ | Localisation Lead — **required**, `bilingual: yes` | **Not started** |
| G5 Legal | ○ | — | Not required |
| G6 Statutory | ○ | — | Not required. §4.5 currency is `RF-008`'s gate, not this file's |
| Final approver | — | Programme Content Lead | **Unappointed** — `AUDIT-001` `R-07` |

---

## Open Items

| # | Item | Owner | Blocks |
|---|---|---|---|
| `RF-001-OI-01` | **`GL-03` — the `D-nn` collision.** Two documents number decisions from `D-01`. `RF-006` cannot be authoritative until the CTO rules | CTO | `RF-006` reaching `Approved` |
| `RF-001-OI-02` | **`GL-01` — `05-01` restatement.** `AF-06` remains open; this file supplies the counted answer but cannot restate another repository's document | CTO | `AF-06`, `TS-01`, `G4-10` |
| `RF-001-OI-03` | **`GL-02` — module-code allocation rule absent from `CG-005`**, and `SRM2` non-conformant | Enterprise Architecture | `CG-005` v1.1 |
| `RF-001-OI-04` | **`GL-04` — `FR-SLS-` and `FR-BFO-` orphans in `05-01`** | CTO | `05-01` restatement |
| `RF-001-OI-05` | **Six `Personal Data Protection Ordinance 2025` citations to correct** | Legal & Compliance with Programme Content Lead | Nothing; low effort, high currency value |
| `RF-001-OI-06` | **Bengali counterpart not written.** `bilingual: yes` under `CG-010` §3.2 | Localisation Lead | This file reaching `Approved` (`CM-R6`) |
| `RF-001-OI-07` | **No Programme Content Lead appointed** to be the final approver | CEO | Every Class E file in the register |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Content_File_Front_Matter.md` — six sections plus DoD, none removed; register table and maintenance procedure added per `CG-009` §3
- [x] Every count in §4.2 produced by extraction with a stated enumeration instant (`CP-11`, `RG-06`)
- [x] Business terminology **not** duplicated from `CG-004` / `BN-003` (`CP-01`)
- [x] Four identifier defects reported rather than silently worked around (`AUDIT_Checklist_Recurring` reporting convention)
- [x] Statutory abbreviations carry a verified-on date and defer currency to `RF-008`
- [x] All internal links resolve
- [x] Registered in `1000FiX_ERP_Content_Master_Index.md` (rule `CM-R1`)
- [ ] **Bengali counterpart complete and signed off in context (`BN-018`)** — outstanding, `RF-001-OI-06`
- [ ] **Decisions in §4.3 transferred to `RF-006`** — done on `RF-006` authoring; `RF-001-OI-01` blocks its approval
- [ ] **Named approver recorded** — outstanding, `RF-001-OI-07`

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
