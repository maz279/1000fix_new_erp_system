---
id: PGD-STRUCT
title: Folder Structure & Repository Map — Project Guiding Documents
project: 1000FiX ERP System v2.0
version: 1.3
date: 2026-08-18
status: ACTIVE
classification: CONFIDENTIAL
last_enumerated: 2026-08-18 19:48 (+06)
revision_note: >
  v1.3 — Category 07 authored (9 files) and audited (PGD-AUDIT-CAT-07). Tree and counts regenerated
  by enumeration at 19:48 (+06), not by arithmetic on the previous issue. Rule PG-M14 added:
  repository-level identifier spaces are category-keyed, closing the mechanism behind RQA-34 and
  PGD-A2-27. Categories 03, 04, 05 and 06 also hold authored documents; their counts are enumerated
  here and their PGD-000 status rows are the owning sessions' to set.
---

# Folder Structure & Repository Map
# `project-guide-doc/` — Project Guiding Document Repository

---

## 1. What this repository is, and what it is not

| This repository holds | It does **not** hold |
|---|---|
| The **register** of every document needed to build, develop and implement the system (`PGD-000`) | The documents themselves — those are written into these folders as they are produced |
| A **category overview** per folder stating purpose, contents, dependencies and completion criteria | Module or portal specifications — those live in `../1000fix_ERP_Module/` |
| **Authoring templates** for engineering document types | Operational content — that lives in `../project_content/` |
| **Audit reports** on the integrity of this repository | The BRD, RFP, URD or Technology Stack Specification — those live in `../primary-doc/` |

**Boundary rule.** `1000fix_ERP_Module` says *what the system must do*. `project_content` says
*what must be written so the system can be operated*. **`project-guide-doc` says how the system is
engineered, delivered and governed.** No content is duplicated between the three; each references
the others.

---

## 2. Design principles

| # | Principle | Consequence |
|---|---|---|
| **PG-01** | **Register-first** | No document is authored until it has an entry in `PGD-000`. Inherited from rule `RG-01` and audit finding `C-02` |
| **PG-02** | **One document, one purpose** | Each `PGD` document has exactly one owner and one question it answers. Overlap is resolved in the register, not in the files |
| **PG-03** | **Count, do not consult** | Every completeness figure is counted from the filesystem at the time of writing, with an enumeration date. Inherited from rule `RG-06` |
| **PG-04** | **Every folder has an overview** | No folder ships empty. `01_Research_and_Benchmarking/` in the module repository is empty and was raised as finding `AF-05`; that is not repeated here |
| **PG-05** | **Identifiers are permanent** | `GV-003` is `GV-003` forever. A withdrawn document's ID is retired, never reissued |
| **PG-06** | **Standards are cited, not invented** | Each document names the international standard it conforms to, with a verification date where regulatory |
| **PG-07** | **Status is evidence-based** | ✅ / ◐ / ⬜ / ⛔ / ⚠ are set by inspecting the filesystem, not by intent |
| **PG-08** | **No spaces or ampersands** in any folder or file name | Inherited from finding `AF-12` |

---

## 3. Complete tree — enumerated 2026-08-18

```
project-guide-doc/
│
├── README.md                                              ✅ Entry point and navigation
├── FOLDER_STRUCTURE.md                                    ✅ This file
├── PGD-000_Master_Register_of_Project_Guiding_Documents.md ✅ THE REGISTER — 140 documents
│
├── _AUDIT/
│   ├── PGD-AUDIT-001_Register_Integrity_Audit.md          ✅ 13 findings · 11 closed · 2 open
│   ├── PGD-AUDIT-002_Category_00_Governance_Audit.md      ✅ 26 findings · 13 closed · 13 open
│   ├── … PGD-AUDIT-003 … PGD-AUDIT-009, and PGD-AUDIT-CAT-07/-CAT-08/-CAT-09, authored concurrently
│   └── PGD-AUDIT-CAT-13_Category_13_Training_Change_and_Adoption_Audit.md  ✅ 15 findings · 1 critical · 4 fixed · 11 open
│       **Thirteen audits on disk, enumerated 2026-08-19 02:10 (+06).** Two identifier conventions
│       are in use: PGD-AUDIT-nnn holds 001–009 and PGD-AUDIT-CAT-nn holds 07, 08, 09, 13.
│       A `PGD-AUDIT-\d{3}` sweep misses four of thirteen. RR-002 is the fix (recommended 9×).
│
├── _templates/
│   └── TPL_Guiding_Document.md                            ✅ House template (v1.1 — PGD-A2-03)
│
├── 00_Programme_Governance_and_Control/          GV   11 documents   ◄── COMPLETE
│   ├── _CATEGORY_OVERVIEW.md                              ✅ v2.0
│   ├── GV-001_Programme_Charter_and_Mandate.md            ✅ 55 KB
│   ├── GV-002_Governance_Framework_RACI_and_Terms_of_Reference.md   ✅ 59 KB
│   ├── GV-003_Decision_Log_and_Change_Control_Procedure.md          ✅ 44 KB
│   ├── GV-004_Integrated_Programme_Plan_and_Master_Schedule.md      ✅ 43 KB
│   ├── GV-005_RAID_Register.md                            ✅ 41 KB
│   ├── GV-006_Scope_Management_and_Baseline_Control_Procedure.md    ✅ 33 KB
│   ├── GV-007_Estimation_Model_and_Resource_Plan.md       ✅ 44 KB
│   ├── GV-008_Programme_Budget_and_Cost_Baseline.md       ✅ 37 KB
│   ├── GV-009_Wave_Gate_and_Phase_Exit_Criteria_Handbook.md         ✅ 44 KB
│   ├── GV-010_Programme_Assurance_and_Independent_Review_Plan.md    ✅ 37 KB
│   └── GV-011_Documentation_Control_and_Configuration_Management_Plan.md ✅ 42 KB
├── 01_Requirements_Engineering/                  RQ   10 documents  ✅ ALL 10 AUTHORED
│   └── _CATEGORY_OVERVIEW.md                              ✅
├── 02_Architecture_and_Design/                   AR   13 documents  ✅ ALL 13 AUTHORED
│   └── _CATEGORY_OVERVIEW.md                              ✅
├── 03_Data_and_Information_Architecture/         DA    9 documents  ✅ ALL 9 AUTHORED
│   └── _CATEGORY_OVERVIEW.md                              ✅
├── 04_Integration_and_API_Engineering/           IN    8 documents  ✅ ALL 8 AUTHORED
│   ├── _CATEGORY_OVERVIEW.md                              ✅ v2.0
│   ├── IN-001_Integration_Architecture_Specification.md            ✅ 80 KB
│   ├── IN-002_API_Specification_OpenAPI_Contracts.md               ✅ 57 KB
│   ├── IN-002_artefacts/                     ★ 7 files — the estate's FIRST non-markdown artefacts
│   │   ├── _shared/{components,errors,security}.yaml       ✅ OpenAPI 3.1 component library
│   │   ├── service-delivery/openapi.yaml                   ✅ 16 operations
│   │   ├── commercial/openapi.yaml                         ✅  6 operations
│   │   ├── finance/openapi.yaml                            ✅  5 operations
│   │   └── platform/openapi.yaml                           ✅  8 operations
│   ├── IN-003_Domain_Event_Catalogue_and_Schema_Registry.md        ✅ 62 KB
│   ├── IN-003_artefacts/                     ★ 4 files
│   │   ├── reconciliation/portal-consumed-unpublished.csv  ✅ 69 measured rows
│   │   ├── schemas/*.v1.json                               ✅ JSON Schema 2020-12
│   │   └── service-delivery/asyncapi.yaml                  ✅ AsyncAPI 3.0
│   ├── IN-004_Interface_Control_Documents.md                       ✅ 55 KB · 14 ICDs
│   ├── IN-005_API_Governance_Versioning_and_Deprecation_Standard.md ✅ 45 KB · 58 scopes
│   ├── IN-006_Webhook_Callback_and_Partner_Push_Specification.md   ✅ 40 KB
│   ├── IN-007_Payment_and_Financial_Gateway_Integration_Design.md  ✅ 42 KB
│   └── IN-008_Integration_Test_Sandbox_and_Certification_Specification.md ✅ 43 KB
├── 05_Security_Privacy_and_Compliance/           SC   11 documents  ✅ ALL 11 AUTHORED
│   ├── SC-001_Security_Architecture_Document.md                ✅
│   ├── SC-002_Threat_Model_STRIDE_and_Abuse_Case_Register.md   ✅
│   ├── SC-003_Data_Protection_Impact_Assessment_PDPA_2026.md   ✅ ⚠ unsignable
│   ├── SC-004_Identity_Authentication_and_Authorisation_Design.md ✅
│   ├── SC-005_Secure_Development_Lifecycle_Standard.md         ✅
│   ├── SC-006_Cryptography_and_Key_Management_Standard.md      ✅
│   ├── SC-007_Data_Residency_and_Cross_Border_Transfer_Design.md ✅
│   ├── SC-008_Regulatory_Compliance_Obligations_Register.md    ✅
│   ├── SC-009_Vulnerability_Management_and_Penetration_Test_Plan.md ✅
│   ├── SC-010_Audit_Logging_and_Forensic_Readiness_Specification.md ✅
│   ├── SC-011_Security_Incident_Response_Plan.md               ✅
│   └── _CATEGORY_OVERVIEW.md                              ✅ v2.0
├── 06_Experience_and_Interface_Design/           UX    8 documents  ✅ ALL 8 AUTHORED
│   ├── _CATEGORY_OVERVIEW.md                              ✅ v2.0
│   ├── UX-001_Design_System_and_Component_Library_Specification.md  ✅ 70 KB
│   ├── UX-002_Information_Architecture_and_Navigation_Model.md      ✅ 42 KB
│   ├── UX-003_Wireframe_and_Screen_Inventory.md            ✅ 50 KB
│   ├── UX-004_Interaction_and_Prototype_Specification.md   ✅ 42 KB
│   ├── UX-005_Accessibility_Conformance_Design_WCAG_2_2_AA.md       ✅ 47 KB
│   ├── UX-006_Mobile_Application_UX_Specification_Offline_First.md  ✅ 49 KB
│   ├── UX-007_Bilingual_and_Bengali_Interface_Design_Standard.md    ✅ 39 KB
│   └── UX-008_Usability_Test_Plan_and_Findings_Log.md      ✅ 41 KB
├── 07_Build_Engineering_and_Development_Standards/ BE  9 documents  ✅ ALL 9 AUTHORED
│   ├── _CATEGORY_OVERVIEW.md                              ✅ v2.0
│   ├── BE-001_Development_Environment_Setup_Guide.md      ✅ 37 KB
│   ├── BE-002_Coding_Standards_and_Style_Guide.md         ✅ 46 KB
│   ├── BE-003_Git_Workflow_Branching_and_Code_Review_Standard.md    ✅ 39 KB
│   ├── BE-004_Repository_and_Monorepo_Structure_Standard.md         ✅ 45 KB
│   ├── BE-005_Custom_Development_CD_Master_Register.md    ✅ 110 KB — 331 items
│   ├── BE-006_Component_Build_Specification_Standard.md   ✅ 30 KB
│   ├── BE-007_Dependency_Licence_and_SBOM_Management_Standard.md    ✅ 40 KB
│   ├── BE-008_Sprint_Model_Estimation_and_Backlog_Management_Standard.md ✅ 37 KB
│   └── BE-009_Technical_Debt_Register_and_Refactoring_Policy.md     ✅ 35 KB
├── 08_Quality_Engineering_and_Test/              QA   11 documents  ✅ AUTHORED 2026-08-18
│   └── _CATEGORY_OVERVIEW.md                              ✅
├── 09_Data_Migration_and_Cutover/                MG    7 documents  ✅ ALL 7 AUTHORED
│   ├── _CATEGORY_OVERVIEW.md                              ✅ v2.0
│   ├── MG-001_Data_Migration_Strategy.md                  ✅ 65 KB — 31 rules
│   ├── MG-002_Legacy_System_Profiling_and_Extract_Specification.md   ✅ 60 KB — 43 rules
│   ├── MG-003_ETL_Design_and_Transformation_Rules_Specification.md   ✅ 58 KB — 50 rules
│   ├── MG-004_Reconciliation_and_Validation_Plan.md       ✅ 44 KB — 33 rules
│   ├── MG-005_Mock_Migration_and_Dress_Rehearsal_Plan.md  ✅ 38 KB — 31 rules
│   ├── MG-006_Cutover_Plan_and_Runbook.md                 ✅ 47 KB — 36 rules
│   └── MG-007_Rollback_and_Fallback_Plan.md               ✅ 43 KB — 33 rules
│   └── _CATEGORY_OVERVIEW.md                              ✅
├── 10_Infrastructure_DevOps_and_Environments/    PE    9 documents  ✅ ALL 9 AUTHORED
│   ├── _CATEGORY_OVERVIEW.md                              ✅ v2.0
│   ├── PE-001_Infrastructure_and_Network_Architecture_Design.md      ✅ 55 KB
│   ├── PE-002_Environment_Strategy_and_Specification.md              ✅ 48 KB · 12 environments
│   ├── PE-003_Infrastructure_as_Code_Standard.md                     ✅ 44 KB · OpenTofu
│   ├── PE-004_CI_CD_Pipeline_Design_Specification.md                 ✅ 47 KB
│   ├── PE-005_Containerisation_and_Orchestration_Design.md           ✅ 43 KB · K3s
│   ├── PE-006_Capacity_Plan_and_Performance_Engineering_Baseline.md ✅ 44 KB
│   ├── PE-007_Backup_Disaster_Recovery_and_Business_Continuity_Design.md ✅ 51 KB · OP-01/OP-02
│   ├── PE-008_Observability_and_Monitoring_Design.md                 ✅ 47 KB · 8 SLOs
│   └── PE-009_Configuration_and_Secrets_Management_Standard.md       ✅ 45 KB · break-glass
├── 11_Service_Operations_and_Support/            SV    6 documents  ✅ AUTHORED 2026-08-19
│   ├── _CATEGORY_OVERVIEW.md                                        ✅
│   ├── SV-001_Service_Management_Framework_and_Operating_Model.md   ✅ 105 KB · 27 SMF · the M66 split
│   ├── SV-002_Platform_SLA_OLA_and_Internal_Service_Catalogue.md    ✅  80 KB · 27 PSL · 21 services, 21 SLOs
│   ├── SV-003_Operational_Runbook_Master_Set.md                     ✅  70 KB · 33 RBS · NFR-091 sized
│   ├── SV-004_On_Call_Paging_and_Escalation_Design.md               ✅  79 KB · 41 OCP · the paging decision
│   ├── SV-005_Hypercare_and_Transition_to_Support_Plan.md           ✅  63 KB · 35 HCT · ~678 PW derived
│   └── SV-006_Problem_and_Major_Incident_Management_Procedure.md    ✅  81 KB · 58 MIM · the first BIA
├── 12_Release_Deployment_and_Transition/         RL    6 documents
│   └── _CATEGORY_OVERVIEW.md                              ✅
├── 13_Training_Change_and_Adoption/              CH    5 documents  ✅ ALL 5 AUTHORED
│   ├── _CATEGORY_OVERVIEW.md                              ✅ v2.0
│   ├── CH-001_Organisational_Change_Management_Plan.md               ✅ 78 KB · 33 rules · OCM-nn
│   ├── CH-002_Training_Plan_and_Delivery_Schedule.md                 ✅ 72 KB · 24 rules · TPD-nn
│   ├── CH-003_Stakeholder_Engagement_and_Communication_Plan.md       ✅ 42 KB · 24 rules · SEP-nn
│   ├── CH-004_Adoption_Measurement_and_Reinforcement_Plan.md         ✅ 46 KB · 24 rules · ADP-nn
│   └── CH-005_Super_User_and_Champion_Network_Charter.md             ✅ 38 KB · 23 rules · CNC-nn
├── 14_Commercial_Vendor_and_Contract/            CO    6 documents  ✅ COMPLETE
│   ├── _CATEGORY_OVERVIEW.md                                          ✅
│   ├── CO-002_Vendor_Evaluation_and_Selection_Report.md               ✅ 77 KB · 40 rules · VES-nn
│   ├── CO-003_Statement_of_Work_and_Deliverable_Acceptance_Schedule.md ✅ 76 KB · 74+7 rules · SOW-nn / PDoD-nn
│   ├── CO-004_Licence_and_Open_Source_Compliance_Register.md          ✅ 70 KB · 45 rules · LIC-nn
│   ├── CO-005_Total_Cost_of_Ownership_Model.md                        ✅ 116 KB · 15 rules · TCO-nn
│   └── CO-006_Procurement_and_Purchase_Plan.md                        ✅ 56 KB · 49 rules · PPP-nn
│       (`CO-001` is the issued RFP in ../primary-doc/ and carries ✅ from outside this repository)
├── 15_Benefits_Measurement_and_Assurance/        BM    5 documents
│   └── _CATEGORY_OVERVIEW.md                              ✅
└── 99_Reference_Registers_and_Glossary/          RR    6 documents
    └── _CATEGORY_OVERVIEW.md                              ✅
```

**Files on disk at 2026-08-18 22:00 (+06): 119.** Enumerated, not carried forward — the count moved from 59 (03:12) to 110 (21:39) to 119 during a single day of concurrent authoring, which is why `PG-M11` requires an hour and a minute rather than a date.

| Category | Registered | On disk | Reflected in `PGD-000`? |
|---|---:|---:|---|
| `00` Programme Governance & Control | 11 | **11** | ✔ |
| `01` Requirements Engineering | 10 | **10** | ✔ |
| `02` Architecture & Design | 13 | **13** | ✔ |
| `03` Data & Information Architecture | 9 | **9** | ✔ |
| `04` Integration & API Engineering | 8 | **8** *(+2 artefact folders)* | ✘ **register shows 0 ✅** |
| `05` Security, Privacy & Compliance | 11 | **9** | ✘ **register shows 0 ✅** |
| `06` Experience & Interface Design | 8 | **8** | ✔ 21:56 |
| **`07` Build Engineering & Dev Standards** | **9** | **9** | ✔ **19:48** |
| `08`–`15`, `99` | 55 | 0 | — |
| **Total authored** | **140** | **77** | |

Plus 1 register · 1 README · 1 folder map · **5 audits** · 1 template · 17 category overviews.
`CO-001` and `BM-001` carry ✅ from outside this repository, giving the **54** in `PGD-000` §0.5.

> **⚠ Sixth baseline movement, same day.** This repository held 22 files at 01:45, 34 at 02:55,
> 58 at 03:05, **69 at 13:06** and **115 at 19:48 (+06)** — while the workspace as a whole moved
> 595 → 601 → 610 → 681 → 699 → **736**. Rule `PG-M11` exists precisely so that a completeness
> figure carries the hour and minute it was counted. **Do not carry this number forward — recount,
> and stamp the recount.**

**Three categories are complete:** Category 00 (11 of 11), **Category 01 (10 of 10)** and
Category 02 (13 of 13). Register-wide, **36 of 140 carry ✅** — the 34 above plus `CO-001` and
`BM-001`, which pre-date this repository. See `PGD-000` §0.5.

> **Audit identifier space — clean at 03:14 (+06), after a collision.** Two files briefly carried
> `id: PGD-AUDIT-002` — the Category 00 and Category 02 audits, authored concurrently. Observed at
> 03:05; the Category 01 audit took **`PGD-AUDIT-004`** rather than become a third claimant on the
> adjacent numbers; the Category 02 session renamed to `003` at ~03:10. Recorded as finding
> **`RQA-34`**, closed
> ([`PGD-AUDIT-004`](_AUDIT/PGD-AUDIT-004_Category_01_Requirements_Engineering_Audit.md) §4).
>
> **The mechanism is unchanged.** `PGD-AUDIT-nnn` is a **sequential** space with no allocating
> authority, and sequential allocation is unsafe under concurrent authoring by construction — the
> next free number is a function of a baseline that is moving. `RR-002` is asked to re-base it to a
> **category-keyed** form (`PGD-AUDIT-CAT-nn`), computable without reference to any other session's
> work.

> **⚠ This count is a measurement of a moment, not a claim about the present.** The repository is
> being written by more than one session; it held 22 files at 01:45, 34 at 02:55 and 58 at 03:05.
> Rule `PG-M11` exists precisely so that a completeness figure carries the hour and minute it was
> counted. **Do not carry this number forward — recount, and stamp the recount.** Four independent
> occurrences of baseline movement are recorded in `PGD-AUDIT-002` §8 and §8.1.

---

## 4. Folder purpose reference

| Folder | Code | Answers | Primary audience | Change frequency |
|---|:--:|---|---|---|
| `00_Programme_Governance_and_Control` | `GV` | Who decides, what "done" means, what it costs | Board, CTO, PMO | Low |
| `01_Requirements_Engineering` | `RQ` | What exactly shall the system do, testably | Vendor, developers, QA | High→controlled |
| `02_Architecture_and_Design` | `AR` | How is it structured so it works and stays changeable | Architects, lead developers | Medium |
| `03_Data_and_Information_Architecture` | `DA` | What is the data, who owns it, how is it protected | Data architects, DBAs, DPO | High→controlled |
| `04_Integration_and_API_Engineering` | `IN` | What are the contracts between systems | Integration & portal engineers, partners | High |
| `05_Security_Privacy_and_Compliance` | `SC` | Is it safe, and is it lawful | CISO, DPO, legal, auditors | Medium, wave-gate reverified |
| `06_Experience_and_Interface_Design` | `UX` | What does the user actually see and do | Designers, front-end, business owners | High→per-portal |
| `07_Build_Engineering_and_Development_Standards` | `BE` | How do developers work, consistently | Every developer | Low once set |
| `08_Quality_Engineering_and_Test` | `QA` | How do we know it works | QA, developers, business UAT | Medium |
| `09_Data_Migration_and_Cutover` ✅ | `MG` | How does the old data become the new data, safely | Migration team, finance, branches | High→per-wave |
| `10_Infrastructure_DevOps_and_Environments` | `PE` | What does it run on, and how is it deployed | Platform engineers, SREs | High in W1 |
| `11_Service_Operations_and_Support` | `SV` | How is it kept alive | Service desk, SREs, on-call | Medium |
| `12_Release_Deployment_and_Transition` | `RL` | How does it go live, nine times | Release manager, PMO, branch managers | High during rollout |
| `13_Training_Change_and_Adoption` ✅ | `CH` | How do people actually use it | CEO, Steering, change lead, L&D, HR, branch managers | High during rollout |
| `14_Commercial_Vendor_and_Contract` | `CO` | What is bought, from whom, for how much | CFO, procurement, legal | Low |
| `15_Benefits_Measurement_and_Assurance` | `BM` | Did it deliver what it promised | Board, CFO, benefit owners | Low model, continuous measurement |
| `99_Reference_Registers_and_Glossary` | `RR` | What does this term / identifier / citation mean | Everyone | Low standards, continuous registers |

---

## 5. Naming convention

### Document files

```
<CODE>-<nnn>_<Descriptive_Name_In_Title_Case_With_Underscores>.md
```

- `CODE` is the two-or-three-letter category code from §4 (`GV`, `RQ`, `AR`, `DA`, `IN`, `SC`,
  `UX`, `BE`, `QA`, `MG`, `PE`, `SV`, `RL`, `CH`, `CO`, `BM`, `RR`).
- `nnn` is the permanent three-digit sequence within the category. Never reused, never renumbered.
- Example: `01_Requirements_Engineering/RQ-001_Software_Requirements_Specification.md`

### Reserved prefixes

| Prefix | Meaning |
|---|---|
| `_` | Non-content file: template, category overview, audit folder |
| `PGD-` | Repository-level artefact (register, structure map, audit) |
| `TPL_` | Authoring template |
| `SUPERSEDED_` | Retained for traceability; not authoritative |
| `DRAFT_` | Work in progress; not approved |

### Supporting artefacts

A document may own non-markdown artefacts (an OpenAPI file, a DDL script, a diagram source, a
Terraform module). These sit in a subfolder sharing the document's ID stem:

```
04_Integration_and_API_Engineering/
├── IN-002_API_Specification_OpenAPI_Contracts.md
└── IN-002_artefacts/
    ├── README.md                      how to lint, bundle and generate
    ├── _shared/components.yaml        shared schemas, parameters, headers
    ├── _shared/errors.yaml            RFC 9457 Problem Details + the 90 codes
    ├── _shared/security.yaml          the three securitySchemes
    └── <bounded-context>/openapi.yaml one per AR-008 context — eleven when complete
```

> **This convention was reserved by `GV-011` `CM-20` and is first exercised by Category 04.**
> Enumeration at 2026-08-18 14:40 (+06) returned **0 files of any non-`.md` type** across
> `1000fix_ERP_Module`, `project_content`, `primary-doc` and `old-primary-doc`. Every OpenAPI file,
> JSON Schema, AsyncAPI document, DDL script and Terraform module in the programme is written from
> nothing — which is why `IN-002` is sized at 109–356 PW and `DA-001` at comparable scale.

---

## 6. Mandatory front matter

Every document in this repository carries the schema in `_templates/TPL_Guiding_Document.md`:

| Field | Required | Purpose |
|---|:--:|---|
| `id` | ✓ | Permanent identifier, e.g. `RQ-001` |
| `title` | ✓ | Full document name |
| `category` / `code` | ✓ | Owning category and its code |
| `project` | ✓ | Always `1000FiX ERP System v2.0` |
| `version` · `date` · `status` | ✓ | Version control triple |
| `classification` | ✓ | `CONFIDENTIAL — Internal Use Only` unless stated otherwise |
| `owner` | ✓ | The **role** accountable, never a personal name |
| `standards_basis` | ✓ | The international standards this document conforms to |
| `traces_to` | ✓ | The requirement, module, portal or finding that requires this document |
| `depends_on` | ✓ | Documents that must exist first |
| `verified_on` | conditional | **Mandatory** where the document cites a statute, standard or vendor version |
| `priority` · `needed_by` | ✓ | `P0`–`P3` and the wave |

---

## 7. Maintenance rules

| Rule | Detail |
|---|---|
| **PG-M1** | A document may not be authored before its `PGD-000` entry exists (`PG-01`) |
| **PG-M2** | Changing a document's status in `PGD-000` requires re-enumeration from the filesystem and an updated `last_enumerated` date |
| **PG-M3** | Adding, removing or re-prioritising a registered document requires a Change Request approved by the ERP Steering Committee |
| **PG-M4** | A document citing a statute, standard or vendor version carries a `verified_on` date and is re-verified at every wave gate |
| **PG-M5** | Identifiers are permanent. A withdrawn document's ID is retired with a tombstone row in `PGD-000`, never reissued |
| **PG-M6** | Category overviews are updated whenever their category's status counts change |
| **PG-M7** | This repository is audited at every wave gate; findings are recorded in `_AUDIT/` |
| **PG-M8** | The folder structure itself is versioned in this file; changes require CTO approval |
| **PG-M9** | **Link verification before issue.** Every relative link in a changed file is resolved against the filesystem before the file is issued. Closes finding `PGD-A1-11`; prevents recurrence of `H-06` |
| **PG-M10** | **Arithmetic verification before issue.** Every summary or roll-up table is regenerated by counting the rows it summarises, immediately before issue — never written from intent and never carried forward. Closes findings `PGD-A1-02` and `PGD-A1-13` |
| **PG-M11** | **Enumeration carries a timestamp, not a date.** Any completeness figure records the hour and minute it was counted. **Four** independent occurrences of baseline movement during authoring — `AUDIT-016` `AP-17`, `PGD-A1-03`, and `PGD-AUDIT-002` §8 and §8.1 — make the date alone insufficient. Implements proposed rule `RG-08`, which remains unratified after all four |
| **PG-M12** | **Every artefact is under version control.** Verified 2026-08-18 03:05: **no `.git`, `.hg` or `.svn` exists anywhere in the workspace, across 621+ files.** Four of the estate's five recurring defect classes — stale roll-ups, registers denying work that exists, baseline movement, broken links — are mechanically detectable by a pre-commit hook and by nothing else. Finding `PGD-A2-15`; remediation in `GV-011` §10.2 |
| **PG-M13** | **A repository-level identifier is allocated by one authority.** Two concurrent sessions allocated `PGD-AUDIT-002` within eight minutes, producing two files with one identifier. Until `RR-002` is issued, cite repository-level artefacts by **full filename**. Finding `PGD-A2-27` |
| **PG-M14** | **A repository-level identifier space is keyed, not sequential.** `PG-M13` asked for a single allocating authority; no authority was constituted, and by 19:48 four categories were being authored concurrently against a space whose next free value is a function of a moving baseline. The Category 07 audit therefore adopts **`PGD-AUDIT-CAT-nn`**, derivable from the category alone. Existing `PGD-AUDIT-001`…`005` are permanent and are **not** renumbered (`RG-02`); both forms coexist until `RR-002` rules. This is the same fix `BE-005` applied to the `CD` space — see `BE-005` §4 for why a scheme needing no allocator is the only one that survives concurrent authoring |

### Issue checklist

A file is not issued until all five pass:

| # | Check | Command or method |
|---|---|---|
| 1 | Links resolve | `PG-M9` — resolve every `](...)` target |
| 2 | Roll-ups recount | `PG-M10` — regenerate every summary table from its source rows |
| 3 | Identifiers are unique and non-colliding | Check against `RR-002`; until it exists, check all four repository code spaces by hand |
| 4 | Enumeration is timestamped | `PG-M11` |
| 5 | Citations carry `verified_on` | `PG-M4` |

---

## 8. Reading paths

| If you are… | Read in this order |
|---|---|
| **A board member or the CFO** | `PGD-000` §0.2 → §0.5 → §2.4 → `14_Commercial/_CATEGORY_OVERVIEW.md` |
| **The CTO or Programme Director** | `PGD-000` in full → `_AUDIT/PGD-AUDIT-001` → `PGD-000` §2.2 sequencing |
| **An architect** | `02_Architecture` → `03_Data` → `04_Integration` → `05_Security` overviews |
| **A developer joining the build** | `07_Build` overview → `PGD-000` §2.1 → your module's spec in `../1000fix_ERP_Module/` |
| **A QA engineer** | `08_Quality` overview → `PGD-000` `RQ-004`, `QA-001`, `QA-011` rows |
| **An implementation vendor** | `PGD-000` §0.2 → §2.1 → §2.2 → `14_Commercial/_CATEGORY_OVERVIEW.md` §`CO-003` |
| **An auditor or assurance reviewer** | `_AUDIT/PGD-AUDIT-001` → `PGD-000` §0.5 → the ⛔ rows in every category |
| **Anyone writing a PGD document** | `_templates/TPL_Guiding_Document.md` → your `_CATEGORY_OVERVIEW.md` → `PGD-000` your row |

---

## 9. Relationship to the other repositories

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                   1000fix_new_erp_system/                                    │
│                                                                              │
│  ┌────────────────────┐   ┌────────────────────┐   ┌──────────────────────┐  │
│  │  primary-doc/      │   │ 1000fix_ERP_Module/│   │  project_content/    │  │
│  │  4 files · 1.23 MB │   │  123 files         │   │  468 files           │  │
│  │                    │   │                    │   │                      │  │
│  │  BRD · RFP · URD   │──▶│  67 modules        │──▶│  Master data · UI    │  │
│  │  Technology Stack  │   │  12 portals        │   │  copy · SOPs · legal │  │
│  │                    │   │  6 cross-cutting   │   │  training · migration│  │
│  │  WHY & WHAT        │   │  WHAT, in detail   │   │  WHAT TO WRITE       │  │
│  └────────────────────┘   └─────────┬──────────┘   └──────────┬───────────┘  │
│                                     │                         │              │
│                                     ▼                         ▼              │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │              project-guide-doc/   ◀── THIS REPOSITORY                  │  │
│  │              140 registered documents · 115 files on disk              │  │
│  │                                                                        │  │
│  │              HOW IT IS ENGINEERED, DELIVERED AND GOVERNED              │  │
│  │   SRS · SAD · SDD · schema · API contracts · threat model · DPIA ·     │  │
│  │   test strategy · migration strategy · CI/CD · IaC · runbooks ·        │  │
│  │   release plans · cost baseline · registers                           │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  ┌────────────────────┐   ┌────────────────────┐   ┌──────────────────────┐  │
│  │  old-primary-doc/  │   │  audit_analysis/   │   │  (other programmes)  │  │
│  │  6 files · v1.0    │   │  EMPTY             │   │                      │  │
│  │  baseline + the    │   │                    │   │                      │  │
│  │  March 2026        │   │                    │   │                      │  │
│  │  missing-docs list │   │                    │   │                      │  │
│  └────────────────────┘   └────────────────────┘   └──────────────────────┘  │
└──────────────────────────────────────────────────────────────────────────────┘
```

**Cross-repository rule.** A `PGD` document **references** module specifications, content files and
primary documents; it never restates them. Where a `PGD` document and a module specification
disagree on *what the system does*, the module specification wins. Where they disagree on *how it
is built*, the `PGD` document wins.

---

*Maintained by: Enterprise Architecture, 1000FiX Services Limited*
*Hotline 16743 · info@1000fix.com · ISO 9001:2015 Certified*
