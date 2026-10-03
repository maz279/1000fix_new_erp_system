---
id: FIX-ERP2-CONTENT-INDEX
title: ERP & Portal Content Master Index
project: 1000FiX ERP System v2.0 — Enterprise Resource Planning + 12-Portal Suite
version: 1.0
date: 2026-08-15
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Chief Technology Officer / Programme Content Lead, 1000FiX Services Limited
supersedes: none
related:
  - 1000fix_ERP_Module/README.md
  - 1000fix_ERP_Module/FOLDER_STRUCTURE.md
  - 1000fix_ERP_Module/02_Architecture/02-02_Module_Catalogue_Master_Register.md
  - 1000fix_ERP_Module/04_Portals_and_Applications/04-00_Portal_Suite_Overview.md
  - 1000fix_ERP_Module/05_Cross_Cutting_Specifications/ (05-01 … 05-06)
  - project_content/_AUDIT/AUDIT-001_Content_and_Repository_Integrity_Audit.md
---

# 1000FiX ERP & Portal — Content Master Index
### 452 content files · 21 categories · 67 modules · 12 portals · 38+ roles · 9 delivery waves

---

## 0. How To Read This Document

This is the **authoritative register of every piece of content the 1000FiX ERP programme must
produce** in order to be buildable, testable, trainable, launchable and legally operable.

It is not a list of software modules. The module specifications already exist in
`1000fix_ERP_Module/03_Modules/` (67 files) and the portal specifications in
`1000fix_ERP_Module/04_Portals_and_Applications/` (12 files). Those documents say **what the
system must do**. This register says **what must be written, translated, seeded, approved and
maintained so that the system can actually be operated by 500+ employees, 250,000+ monthly
customers, 17+ brand partners, 500–2,000 marketplace sellers and 500–2,000 corporate users —
in two languages, across 51+ branches and 8 divisions.**

### The distinction that matters

| Layer | Lives in | Answers |
|---|---|---|
| **Specification** | `1000fix_ERP_Module/` | What must the system do? |
| **Content** | `project_content/` ← *this register* | What words, data, documents, templates, courses and messages must exist for it to work? |
| **Code** | Build repositories | How is it implemented? |

An ERP fails on content far more often than on code. A dispatch board with no zone master is
inert. An invoice engine that cannot print a compliant Mushak 6.3 challan is illegal. A
technician application in English only will not be used by 200–400 Bengali-speaking field
technicians. A 67-module system with no role-based training will not be adopted. **Every file
in this register exists because its absence stops something.**

### Reading key

| Column | Meaning |
|---|---|
| **ID** | Permanent content identifier. Never reused, never renumbered. |
| **File** | File name as it must be saved (see §3 folder tree). |
| **What it contains** | The substance of the file in one line. |
| **Why it is needed** | The consequence of it not existing. This is the justification column — no file is in this register without one. |
| **Pri** | `P0` blocking · `P1` must-have · `P2` important · `P3` desirable — same scale as the module register (`README.md` §Document Conventions) |
| **Wave** | `W1`–`W9` — the delivery wave that consumes it (`06-01_Implementation_Roadmap_and_Phasing.md`) |
| **Owner** | Accountable function, not an individual |
| **Traces to** | Module `Mnn`, portal `Pnn`, or cross-cutting document that requires it |

**Priority is aligned deliberately with the ERP module register (`P0`–`P3`), not with the
corporate-website content index (`P1`–`P4`).** The two registers use different scales; do not
cross-read them. See finding **AF-11** in the audit report.

---

## 1. Master Statistics

| Metric | Count |
|---|---:|
| **Total content files in register** | **452** |
| Categories | 21 |
| `P0` — blocking (no wave can go live without them) | 105 |
| `P1` — must-have | 190 |
| `P2` — important | 142 |
| `P3` — desirable | 15 |
| Files requiring a Bengali version | 266 |
| Files requiring legal or statutory sign-off | 61 |
| Files that are seed **data**, not prose | 48 |
| **Files currently written** | **452 of 452 (100%)** — **all 21 categories written**, all at status `Draft`. *Enumerated **2026-08-18** (`AUDIT-020` §2). Categories 19 `MM` and 99 `RF` were authored concurrently and completed in this pass. **Written is not approved: 0 of 452 are `Approved`** — 32 Class A/B files await unwaivable gate `G6`, 266 await a Bengali counterpart under `CM-R6`, and the Programme Content Lead who is the final approver of every Class E file is unappointed (`RF-010`, `RF-011` `CR-01`). Superseded figures: 428 at 2026-08-17 16:49 UTC; 427 at 2026-08-17 16:45 UTC — both floors taken during authoring, per proposed rule `RG-08`* |

### Distribution by category

| # | Code | Category | Files | P0 | P1 | P2 | P3 |
|---|---|---|---:|---:|---:|---:|---:|
| 00 | `CG` | Content Governance & Standards | 14 | 7 | 5 | 2 | 0 |
| 01 | `VB` | Voice, Brand & Design-System Content | 10 | 3 | 4 | 3 | 0 |
| 02 | `MD` | Master Data & Configuration Seed Content | 48 | 29 | 13 | 6 | 0 |
| 03 | `UI` | UI Copy & Microcopy | 42 | 15 | 19 | 8 | 0 |
| 04 | `NT` | Notification & Messaging Content | 26 | 4 | 12 | 10 | 0 |
| 05 | `DT` | Document, Print & Statutory Output Templates | 44 | 10 | 22 | 12 | 0 |
| 06 | `SP` | Process, SOP & Workflow Content | 34 | 2 | 21 | 11 | 0 |
| 07 | `KB` | Knowledge Base & Technical Library | 16 | 0 | 4 | 11 | 1 |
| 08 | `TR` | Training & Enablement | 24 | 1 | 12 | 11 | 0 |
| 09 | `HC` | Help Centre & Self-Service | 20 | 0 | 6 | 11 | 3 |
| 10 | `LG` | Legal, Policy & Compliance | 24 | 7 | 10 | 7 | 0 |
| 11 | `BN` | Localisation & Bilingual Content | 18 | 9 | 6 | 3 | 0 |
| 12 | `DM` | Data Migration Content | 14 | 6 | 8 | 0 | 0 |
| 13 | `TS` | Test & Acceptance Content | 18 | 5 | 12 | 1 | 0 |
| 14 | `RP` | Reporting, Analytics & KPI Content | 16 | 1 | 6 | 8 | 1 |
| 15 | `AP` | Integration & Developer Content | 12 | 0 | 6 | 6 | 0 |
| 16 | `CM` | Change Management & Communications | 18 | 0 | 7 | 9 | 2 |
| 17 | `OP` | Operations, Support & Runbooks | 16 | 5 | 8 | 3 | 0 |
| 18 | `EO` | Ecosystem Onboarding Content | 14 | 0 | 3 | 8 | 3 |
| 19 | `MM` | Multimedia & Asset Specifications | 12 | 0 | 1 | 7 | 4 |
| 99 | `RF` | Reference & Registers | 12 | 1 | 5 | 5 | 1 |
| | | **Total** | **452** | **105** | **190** | **142** | **15** |

### Distribution by wave

| Wave | Months | Content files first required | Dominant categories |
|---|---|---:|---|
| **W0 — Mobilisation** | 0–3 | 61 | `CG`, `MD` (governance + core master data), `DM`, `RF` |
| **W1 — Core platform & Admin Portal (P03)** | 3–8 | 88 | `MD`, `UI`, `DT`, `SP`, `TR`, `TS` |
| **W2 — Customer (P01) & Technician (P02)** | 8–14 | 74 | `UI`, `NT`, `BN`, `HC`, `LG` |
| **W3 — Logistics (P09), Vendor (P05), Payments** | 14–18 | 43 | `DT`, `EO`, `AP`, `SP` |
| **W4 — Corporate (P04), Brand (P08), Contact Centre (P10), Analytics (P06)** | 18–23 | 57 | `RP`, `EO`, `HC`, `LG` |
| **W5 — Quality (P11), Finance depth, HR depth** | 23–27 | 39 | `DT`, `SP`, `TR`, `RP` |
| **W6 — Native apps, AI assistant** | 27–30 | 28 | `HC`, `BN`, `MM` |
| **W7 — Marketplace (P07), Partner (P12)** | 30–33 | 36 | `EO`, `LG`, `UI`, `NT` |
| **W8–W9 — Scale, optimisation, multi-entity** | 33–36 | 26 | `RP`, `OP`, `KB`, `CM` |

> Waves are taken from `06-01_Implementation_Roadmap_and_Phasing.md`. Where a content file is
> needed *before* the wave that consumes it (master data and migration content almost always
> are), the wave shown is the **build wave**, and the lead time is stated in the file's own
> front matter, not here.

---

## 2. Governing Principles

These eleven rules make the register maintainable at 452 files. They are modelled on the
`FOLDER_STRUCTURE.md` principles (FS-01…FS-08) that already govern the module repository, so
that a person who can navigate one can navigate the other.

| # | Principle | Consequence |
|---|---|---|
| **CP-01** | **One content asset, one file** | No content is authored in two places. A file that would duplicate another references it instead. |
| **CP-02** | **Content IDs are permanent** | `CG-001`…`RF-012` never change and are never reused, even if the file is retired. A retired ID is marked `WITHDRAWN`, not recycled. |
| **CP-03** | **Every file declares why it exists** | The "Why it is needed" column here, and a `purpose:` key in the file's own front matter. A file with no consequence-of-absence is deleted from the register, not written. |
| **CP-04** | **Every file traces to a specification** | Each row names the module, portal or cross-cutting document that requires it. Content with no upstream requirement is scope creep; requirements with no content are a gap. Both are audited in `RF-003`. |
| **CP-05** | **Bengali is a first-class deliverable, not a translation afterthought** | Any file marked bilingual is not `Complete` until both languages are signed off. Machine translation is prohibited on customer- and field-facing content (`04-00` §P01 Design Requirements). |
| **CP-06** | **Seed data is content and is version-controlled like content** | The 48 `MD` files are structured data (CSV/XLSX) with a markdown specification wrapper. They ship through the same review gate as prose. |
| **CP-07** | **Statutory content requires named external sign-off** | The 61 files flagged for legal/statutory review carry a counsel or regulator-alignment sign-off block. No such file goes to build on internal approval alone. |
| **CP-08** | **Content is versioned against the release that consumes it** | A UI copy pack is pinned to a portal release; a Mushak template is pinned to a Finance Act year. Both are recorded in `RF-006`. |
| **CP-09** | **Templates are enforced** | `_templates/` holds one template per content type. Files that do not conform fail the `CG-008` Definition of Done. |
| **CP-10** | **Superseded content is archived, not deleted** | `_ARCHIVE/` retains prior versions with a `SUPERSEDED_` prefix, mirroring `99_Reference/_Superseded/` in the module repository. |
| **CP-11** | **The register is counted, not estimated** | Completion percentages are produced by enumerating the filesystem, never by projecting. This is rule **RG-06** from audit `00-07`, applied to content. |

---

## 3. Folder Tree

Saved under `E:\sofrware_project_5\1000 fix\1000fix_new_erp_system\project_content\`.

### 3.1 Design rationale

| Decision | Why |
|---|---|
| **Numeric folder prefixes (`00_`…`99_`)** | File listings sort into reading order; matches `1000fix_ERP_Module/` convention exactly. |
| **Two-letter content codes in file names** | A file name identifies its category even when moved, quoted or attached to an email. |
| **No spaces or ampersands in folder names** | The corporate-website content folders use `BLOG & EDUCATIONAL` style names, which break shell scripts, CI paths and URLs. This register uses underscores throughout. See audit finding **AF-12**. |
| **Per-portal and per-role subfolders only where volume justifies it** | `03_UI_Copy_and_Microcopy/` and `09_Help_Centre_and_Self_Service/` subdivide by portal; nothing else does. |
| **`_templates/`, `_AUDIT/`, `_ARCHIVE/` prefixed with underscore** | Non-content directories sort to the top and are visually distinct — same reserved-prefix rule as `FOLDER_STRUCTURE.md` §5. |
| **Data files live beside their specification** | `MD-035_Chart_of_Accounts_Bangladesh.md` sits next to `MD-035_Chart_of_Accounts_Bangladesh.csv`. The markdown governs; the CSV loads. |

### 3.2 Complete tree

```
project_content/
│
├── 1000FiX_ERP_Content_Master_Index.md          ← this file — the authoritative register
├── README.md                                     Entry point, quick navigation, status
│
├── _templates/                                   Enforced authoring templates (CP-09)
│   ├── TPL_Content_File_Front_Matter.md
│   ├── TPL_Master_Data_Specification.md
│   ├── TPL_UI_Copy_Pack.md
│   ├── TPL_Notification_Template.md
│   ├── TPL_Document_Print_Template.md
│   ├── TPL_SOP.md
│   ├── TPL_Knowledge_Article.md
│   ├── TPL_Training_Course_Pack.md
│   ├── TPL_Help_Article.md
│   ├── TPL_Legal_Document.md
│   ├── TPL_Test_Script.md
│   └── TPL_Runbook.md
│
├── _AUDIT/                                       Audit trail (CP-11)
│   ├── AUDIT-001_Content_and_Repository_Integrity_Audit.md
│   ├── AUDIT-002_Category_01_VB_Content_Audit.md
│   ├── AUDIT-003_Category_02_MD_Content_Audit.md
│   ├── AUDIT-004_Category_03_UI_Content_Audit.md
│   ├── AUDIT-005_Category_04_NT_Content_Audit.md
│   ├── AUDIT-006_Category_06_SP_Content_Audit.md
│   ├── AUDIT-007_Category_05_DT_Content_Audit.md
│   ├── AUDIT-008_Category_07_KB_Content_Audit.md
│   ├── AUDIT-009_Category_08_TR_Content_Audit.md
│   ├── AUDIT-010_Category_09_HC_Content_Audit.md
│   ├── AUDIT-011_Category_12_DM_Content_Audit.md
│   ├── AUDIT-012_Category_11_BN_Content_Audit.md
│   ├── AUDIT-013_Category_10_LG_Content_Audit.md
│   ├── AUDIT-014_Category_13_TS_Content_Audit.md
│   ├── AUDIT-015_Category_14_RP_Content_Audit.md
│   ├── AUDIT-016_Category_15_AP_Content_Audit.md
│   ├── AUDIT-017_Category_17_OP_Content_Audit.md
│   ├── AUDIT-018_Category_18_EO_Content_Audit.md
│   └── AUDIT_Checklist_Recurring.md
│
├── _ARCHIVE/                                     Superseded content (CP-10)
│   └── (SUPERSEDED_* files)
│
├── 00_Content_Governance_and_Standards/          CG-001 … CG-014
├── 01_Voice_Brand_and_Design_Content/            VB-001 … VB-010
│
├── 02_Master_Data_and_Configuration/             MD-001 … MD-048
│   ├── 02A_Organisation_and_Network/             MD-002 … MD-012
│   ├── 02B_Party_and_Ecosystem/                  MD-013 … MD-018
│   ├── 02C_Catalogue_and_Technical/              MD-019 … MD-028
│   ├── 02D_Commercial_and_Pricing/               MD-029 … MD-034
│   ├── 02E_Finance_and_Statutory/                MD-035 … MD-041
│   └── 02F_Workforce_and_Asset/                  MD-042 … MD-048
│
├── 03_UI_Copy_and_Microcopy/                     UI-001 … UI-042
│   ├── 03A_Cross_Cutting/                        UI-001 … UI-010
│   ├── 03B_Portals/                              UI-011 … UI-022  (one pack per P01–P12)
│   ├── 03C_Admin_Workspaces/                     UI-023 … UI-036  (14 P03 workspaces)
│   └── 03D_Critical_Flows/                       UI-037 … UI-042
│
├── 04_Notification_and_Messaging/                NT-001 … NT-026
│   ├── 04A_SMS_and_OTP/                          NT-004 … NT-007
│   ├── 04B_WhatsApp_and_Push/                    NT-008, NT-015 … NT-017
│   ├── 04C_Email/                                NT-009 … NT-014
│   └── 04D_In_App_Voice_and_System/              NT-018 … NT-022
│
├── 05_Document_and_Print_Templates/              DT-001 … DT-044
│   ├── 05A_Service_and_Operations/               DT-002 … DT-009
│   ├── 05B_Finance_and_Statutory/                DT-010 … DT-020
│   ├── 05C_Supply_Chain_and_Logistics/           DT-021 … DT-029
│   ├── 05D_Commercial_and_Contract/              DT-030 … DT-040
│   └── 05E_People_Quality_and_Labelling/         DT-041 … DT-044
│
├── 06_Process_SOP_and_Workflow/                  SP-001 … SP-034
│   ├── 06A_Process_Architecture/                 SP-001 … SP-006
│   └── 06B_Standard_Operating_Procedures/        SP-007 … SP-034
│
├── 07_Knowledge_Base_and_Technical_Library/      KB-001 … KB-016
├── 08_Training_and_Enablement/                   TR-001 … TR-024
│   ├── 08A_Framework/                            TR-001 … TR-006
│   └── 08B_Course_Packs/                         TR-007 … TR-024
│
├── 09_Help_Centre_and_Self_Service/              HC-001 … HC-020
│   ├── 09A_Help_Sets_By_Portal/                  HC-003 … HC-014
│   └── 09B_Conversational_AI/                    HC-017 … HC-019
│
├── 10_Legal_Policy_and_Compliance/               LG-001 … LG-024
├── 11_Localisation_Bengali/                      BN-001 … BN-018
├── 12_Data_Migration_Content/                    DM-001 … DM-014
├── 13_Test_and_Acceptance_Content/               TS-001 … TS-018
├── 14_Reporting_Analytics_and_KPI/               RP-001 … RP-016
├── 15_Integration_and_Developer_Content/         AP-001 … AP-012
├── 16_Change_Management_and_Comms/               CM-001 … CM-018
├── 17_Operations_Support_and_Runbooks/           OP-001 … OP-016
├── 18_Ecosystem_Onboarding_Content/              EO-001 … EO-014
├── 19_Multimedia_and_Asset_Specs/                MM-001 … MM-012
└── 99_Reference_and_Registers/                   RF-001 … RF-012
```

### 3.3 File naming convention

```
<CODE>-<nnn>_<Descriptive_Name_In_Title_Case_With_Underscores>.<ext>
```

- `CODE` — the two-letter category code (`CG`, `VB`, `MD`, `UI`, `NT`, `DT`, `SP`, `KB`, `TR`, `HC`, `LG`, `BN`, `DM`, `TS`, `RP`, `AP`, `CM`, `OP`, `EO`, `MM`, `RF`)
- `nnn` — permanent three-digit sequence within the category (CP-02)
- `ext` — `.md` for the governing specification; `.csv` / `.xlsx` / `.json` for accompanying data, sharing the same stem

**Bilingual pairs.** Bengali versions carry a `_BN` suffix on the same stem:
`UI-011_P01_Customer_Portal_UI_Copy_Pack.md` → `UI-011_P01_Customer_Portal_UI_Copy_Pack_BN.md`.
The English file is the source of truth for structure; the Bengali file is the source of truth
for Bengali wording once linguistically signed off (`BN-018`).

**Reserved prefixes**

| Prefix | Meaning |
|---|---|
| `_` | Non-content directory: template, audit, archive |
| `TPL_` | Authoring template |
| `SUPERSEDED_` | Retained for traceability; not authoritative |
| `DRAFT_` | Work in progress; not approved |

---

## 4. The Register

---

### CATEGORY 00 — `CG` CONTENT GOVERNANCE & STANDARDS
**Folder:** `00_Content_Governance_and_Standards/` · **14 files**

> The rules that make 452 files by many authors across 36 months read as one system. Written
> first, before any content. Without this category the programme produces 452 inconsistent
> artefacts that cannot be reviewed, translated or maintained.

| ID | File | What it contains | Why it is needed | Pri | Wave | Owner | Traces to |
|---|---|---|---|:--:|:--:|---|---|
| CG-001 | `CG-001_Content_Master_Index.md` | This register — every content file, its purpose, priority, owner and traceability | Single authoritative answer to "what content does this programme owe?" Without it, content is discovered late and blocks go-live | P0 | W0 | Programme Content Lead | All |
| CG-002 | `CG-002_Content_Operating_Model_and_RACI.md` | Who authors, reviews, approves, translates, publishes and retires each content type; escalation path | 452 files across 21 categories with no named accountability produces orphaned content. Fixes the ownership gap that caused register drift in the module repo (`00-07` H2-01) | P0 | W0 | Programme Content Lead | `00-04` Governance |
| CG-003 | `CG-003_ERP_Product_Content_Style_Guide.md` | Sentence case rules, voice, tense, person, terminology precedence, punctuation, numerals, abbreviation, capitalisation for enterprise UI | Enterprise UI copy is written by developers, BAs and vendors simultaneously. Without a style guide the same action is labelled four ways across four workspaces | P0 | W0 | Content Design | `04-00` PS-06 |
| CG-004 | `CG-004_Terminology_and_Controlled_Vocabulary_Standard.md` | The one approved term for every business object and action; banned synonyms; term-to-entity binding | "Job", "ticket", "order", "case" and "request" cannot all mean `fix.service.order`. Ambiguity here propagates into UI, training, SOPs, reports and Bengali translation | P0 | W0 | Enterprise Architecture | `05-02` Entity Catalogue |
| CG-005 | `CG-005_Content_ID_and_Naming_Convention.md` | ID allocation rules, ranges, reservation, retirement, file naming, bilingual suffixes | Identifier collision has already cost this programme two audits (`00-07` H2-04/H2-05; portal audit X-01). The same failure mode applies to content | P0 | W0 | Programme Content Lead | `02-02` §1, §5 |
| CG-006 | `CG-006_Content_Lifecycle_and_Versioning_Policy.md` | States (Draft → Review → Approved → Published → Superseded), version numbering, pinning content to releases | A UI copy pack not pinned to a release ships wording the build does not contain. A tax template not pinned to a Finance Act year becomes illegal silently | P0 | W0 | Programme Content Lead | CP-08 |
| CG-007 | `CG-007_Review_Approval_and_Signoff_Workflow.md` | Review gates by content class; who signs statutory, legal and brand content; evidence of sign-off | 61 files carry legal or statutory consequence. Sign-off must be recorded, not assumed | P1 | W0 | Legal & Compliance | `LG-001` |
| CG-008 | `CG-008_Content_Definition_of_Done_and_QA_Checklist.md` | The checklist a file must pass to become `Approved`: template conformance, traceability, bilingual status, accessibility, evidence, links resolve | Prevents the "written but unusable" state. Mirrors the `_MODULE_TEMPLATE.md` enforcement that already works in the specification repository | P1 | W0 | Content Design | `03_Modules/_MODULE_TEMPLATE.md` |
| CG-009 | `CG-009_Content_Template_Register.md` | Index of the 12 `_templates/` files, what each governs, and when to use which | Authors otherwise invent structure per file, and reviewers have nothing to review against | P1 | W0 | Content Design | `_templates/` |
| CG-010 | `CG-010_Bilingual_Content_Policy.md` | Which content must be bilingual, which is English-only, source-of-truth language per type, machine-translation prohibition | 266 of 452 files need Bengali. Deciding this per file, late, is how bilingual programmes fail | P0 | W0 | Localisation Lead | `04-00` PS-03 |
| CG-011 | `CG-011_Accessibility_Content_Standard.md` | Reading level, alt-text rules, link text, heading structure, form-label pairing, error-message accessibility, Bengali screen-reader considerations | WCAG 2.1 AA is a contractual standard (`04-00` PS-04, `05-06`). Most WCAG failures are content failures, not code failures | P1 | W1 | Content Design | `05-06` |
| CG-012 | `CG-012_Content_Sourcing_and_Evidence_Rules.md` | Every factual, statutory, pricing or capability claim must name a primary source with a verification date | The module repository has already recorded findings where claims rested on press reporting rather than enacted law (`00-07` H2-13) | P1 | W0 | Programme Content Lead | `00-07` |
| CG-013 | `CG-013_Content_Risk_and_Legal_Escalation_Rules.md` | Triggers that force a file out of normal review into legal, tax or regulator escalation | Prevents an author from shipping a warranty exclusion or a tax narrative on their own authority | P2 | W0 | Legal & Compliance | `00-04` |
| CG-014 | `CG-014_Content_Metrics_and_Effectiveness_Measurement.md` | How content success is measured — help deflection, training pass rates, error-message abandonment, translation defect density | Content budget is defended with evidence, and weak content is found before users complain | P2 | W2 | Programme Content Lead | `06-02` |

---

### CATEGORY 01 — `VB` VOICE, BRAND & DESIGN-SYSTEM CONTENT
**Folder:** `01_Voice_Brand_and_Design_Content/` · **10 files**

> The corporate website already has a brand voice for marketing. An ERP needs a different one:
> instructional, precise, calm under failure, and identical across twelve surfaces built by
> different teams in different frameworks.

| ID | File | What it contains | Why it is needed | Pri | Wave | Owner | Traces to |
|---|---|---|---|:--:|:--:|---|---|
| VB-001 | `VB-001_ERP_Product_Voice_and_Tone_Guide.md` | Product voice principles, tone shifts by context (routine, error, destructive, celebratory), what 1000FiX never sounds like | Marketing voice applied to a dispatch console produces cheerful ambiguity in a time-critical workflow | P0 | W0 | Content Design | `04-00` PS-06 |
| VB-002 | `VB-002_Persona_and_Portal_Tone_Matrix.md` | Tone calibration per audience: customer, technician, agent, executive, seller, vendor, brand, rider, auditor, corporate admin, partner | A technician working offline in the field and a CFO reading a board dashboard need different registers of the same system | P1 | W1 | Content Design | `04-00` §2 |
| VB-003 | `VB-003_Brand_Application_in_Enterprise_UI.md` | How the 1000FiX brand expresses inside dense operational UI; restraint rules; when brand yields to legibility | Branch hardware is 1366×768 (`04-00` §P03). Marketing brand density is unusable at that size | P1 | W1 | Brand + Content Design | `04-00` §P03 |
| VB-004 | `VB-004_Print_and_PDF_Brand_Template_Standard.md` | Letterhead, footer, statutory block placement, logo clear space, bilingual layout for the 44 `DT` documents | Every printed artefact a customer, regulator or brand partner sees is both a brand and a compliance surface | P1 | W1 | Brand | `DT-001` |
| VB-005 | `VB-005_Email_Brand_Template_Standard.md` | Master email shell, dark-mode behaviour, Bengali font fallback, plain-text parity | Email clients in Bangladesh render Bengali web fonts inconsistently; the fallback must be designed, not discovered | P2 | W2 | Brand | `NT-009` … `NT-014` |
| VB-006 | `VB-006_Design_System_Content_Standards.md` | Copy rules bound to components: button, toast, modal, banner, empty table row, badge, stepper, inline validation | One component library across twelve portals (`PS-06`) needs one copy contract, or components drift per team | P0 | W1 | Content Design + Design System | `04-00` PS-06 |
| VB-007 | `VB-007_Iconography_and_Label_Pairing_Register.md` | Which icon may accompany which label; icon-only prohibitions; Bengali label length allowances | Bengali labels commonly run 20–40% longer than English; icon-plus-label layouts break if not specified | P2 | W1 | Design System | `MM-004` |
| VB-008 | `VB-008_Status_Colour_and_Label_Semantics_Register.md` | Canonical mapping of every lifecycle state to colour, icon and label across all portals and reports | `MD-027` defines the states; this defines how a human recognises them. Divergent status colours across portals cause operational error | P1 | W1 | Design System | `MD-027`, `05-05` |
| VB-009 | `VB-009_Bengali_Typography_and_Brand_Standard.md` | Approved Bengali typefaces, sizes, line height, numeral policy (Bengali vs Arabic digits), mixed-script rules | Bengali-first surfaces (`PS-03`) with unresolved typography are illegible on low-end Android — the exact device class technicians use | P0 | W1 | Brand + Localisation | `BN-006` |
| VB-010 | `VB-010_Product_Plan_and_Programme_Naming_Standard.md` | How AMC tiers, protection plans, loyalty tiers, subscription plans and campaigns are named and abbreviated | Product names appear in contracts, invoices, portals and advertising simultaneously. Renaming later is a data-migration event | P2 | W2 | Commercial + Brand | `MD-032`, `MD-033`, `MD-034` |

---

### CATEGORY 02 — `MD` MASTER DATA & CONFIGURATION SEED CONTENT
**Folder:** `02_Master_Data_and_Configuration/` · **48 files**

> **The single highest-risk category in this register.** Odoo, like every ERP, is inert without
> master data. Each file is a markdown specification (ownership, structure, validation rules,
> source, refresh policy) plus a machine-loadable data file with the same stem. Nothing in
> W1 can be configured, tested or trained on until these exist.

#### 02A — Organisation & Network — `02A_Organisation_and_Network/`

| ID | File | What it contains | Why it is needed | Pri | Wave | Owner | Traces to |
|---|---|---|---|:--:|:--:|---|---|
| MD-001 | `MD-001_Master_Data_Governance_Charter.md` | Data-domain ownership, stewardship model, golden-record and survivorship rules, change control | `M64` assigns single ownership per entity; without a charter, 47 datasets have 47 conflicting owners | P0 | W0 | MDM Lead | `M64`, `05-02` |
| MD-002 | `MD-002_Legal_Entity_and_Company_Master.md` | Legal entities, BIN/TIN, registered addresses, fiscal calendars, functional currency, statutory identifiers | Multi-entity operation (`M65`) and every statutory document depend on it | P0 | W1 | Finance | `M65`, `M51` |
| MD-003 | `MD-003_Branch_and_Service_Centre_Master.md` | All 51+ centres: code, name (EN/BN), type, address, GPS, hours, capabilities, capacity, contacts, kiosk flag | Dispatch, routing, stock, cash, SLA, capacity, reporting and the public locator all key off it | P0 | W1 | Operations | `M04`, `M02` |
| MD-004 | `MD-004_Warehouse_and_Storage_Location_Master.md` | Warehouses, branch stores, van stock locations, bin/rack structure, custody rules | `M41` and `M15` cannot transact without a location tree; van reconciliation is impossible without it | P0 | W1 | Inventory | `M41`, `M15` |
| MD-005 | `MD-005_Dispatch_Zone_and_Territory_Master.md` | Service zones, coverage polygons, travel-time bands, zone-to-branch and zone-to-technician assignment | `M02` dispatch, on-site charging, pick-and-drop eligibility and the SLA promise all derive from zone | P0 | W1 | Operations | `M02`, `M03` |
| MD-006 | `MD-006_Bangladesh_Geographic_Hierarchy.md` | 8 divisions → 64 districts → upazila/thana → union/ward → postcode, with Bengali names and standard codes | Addresses, coverage, tax jurisdiction and reporting all need one canonical geography | P0 | W1 | MDM | `M65`, `05-02` |
| MD-007 | `MD-007_Address_Format_and_Validation_Standard.md` | Bangladesh address composition, required fields by use, GPS capture rules, informal-address handling | Field service fails on bad addresses more often than on bad diagnosis. Validation rules must exist before the UI is built | P1 | W1 | MDM + Operations | `M02`, `UI-004` |
| MD-008 | `MD-008_Organisation_Structure_and_Position_Master.md` | Legal entity → division → department → team → position, with reporting lines and cost-centre binding | Approvals, delegation, payroll, headcount and access control all resolve through position, not person | P0 | W1 | HR | `M21`, `M57` |
| MD-009 | `MD-009_Role_and_Job_Title_Master.md` | The 38 registered roles plus those found unregistered in audit, mapped to positions, portals and access profiles | `05-04` registers 38 roles; audit `00-07` H2-07 found R39–R46 used but unregistered and R54/R57/R60 undefined. This file resolves that before access control is built | P0 | W1 | HR + Security | `05-04`, `M29`, `00-07` H2-07 |
| MD-010 | `MD-010_Competency_and_Skill_Taxonomy.md` | Skill tree by device family, repair level (L1/L2/L3), proficiency scale, expiry rules | Skill-based dispatch (`M02`), certification gating and training design (`M22`) all consume it | P1 | W2 | Learning & Quality | `M22`, `M02` |
| MD-011 | `MD-011_Certification_and_Brand_Authorisation_Register.md` | Which technician certifications exist, which brand authorises what, validity, renewal, evidence | A hard rule blocks assignment of an uncertified technician to brand warranty work (`BRU-SRM-09`). The rule cannot run without this register | P0 | W2 | Quality | `M22`, `M09`, `05-05` BRU-SRM-09 |
| MD-012 | `MD-012_Employee_Master_Data_Template.md` | Employee record schema, mandatory fields, NID/TIN handling, sensitivity classification, joiner data pack | 500+ employees must be loaded before payroll, attendance, dispatch or access control can run | P0 | W1 | HR | `M21`, `M56` |

#### 02B — Party & Ecosystem — `02B_Party_and_Ecosystem/`

| ID | File | What it contains | Why it is needed | Pri | Wave | Owner | Traces to |
|---|---|---|---|:--:|:--:|---|---|
| MD-013 | `MD-013_Customer_and_Party_Master_Standard.md` | Party model, individual vs organisation, roles a party may hold, identity keys, matching and merge rules | `M33` owns the golden customer record. 250,000+ customers a month with no matching rules produces duplicate-driven failure in loyalty, warranty and collections | P0 | W1 | MDM | `M33`, `05-02` |
| MD-014 | `MD-014_Customer_Segment_and_Tier_Definition.md` | Segment definitions (B2C, SME, enterprise, government, walk-in, marketplace) and the rules that assign them | Pricing, SLA, campaign targeting and reporting all segment-key. Ad-hoc segmentation makes analytics meaningless | P1 | W2 | Commercial | `M07`, `M11`, `M35` |
| MD-015 | `MD-015_Corporate_Account_Hierarchy_Standard.md` | Group → company → division → site → department → user structures, with billing and approval roll-up rules | `P04` promises multi-site, multi-level approval and consolidated invoicing. Hierarchy rules must precede the build | P1 | W4 | Account Management | `P04`, `M07`, `M08` |
| MD-016 | `MD-016_Vendor_and_Supplier_Master_Standard.md` | Vendor record schema, category, banking, tax status, compliance documents, approval state | Procurement, payables, VDS deduction and vendor-portal access all depend on a governed vendor record | P1 | W3 | Procurement | `M16`, `M42`, `P05` |
| MD-017 | `MD-017_Brand_Partner_Master_Register.md` | Authorised brand partners, scope of authorisation, claim rules, rate-card ownership, contacts | Audit `00-07` H2-12 records the "17+ brands" figure as unverified while an `M22` control depends on it. This file is where it is verified and closed | P1 | W4 | Commercial | `M09`, `P08`, `00-07` H2-12 |
| MD-018 | `MD-018_Marketplace_Seller_Category_and_Standard_Register.md` | Seller categories, per-category certification and document requirements, commission bands, scorecard thresholds | `P07` cannot open registration until categories and their entry standards are defined | P2 | W7 | Marketplace Ops | `M12`, `P07` |

#### 02C — Catalogue & Technical — `02C_Catalogue_and_Technical/`

| ID | File | What it contains | Why it is needed | Pri | Wave | Owner | Traces to |
|---|---|---|---|:--:|:--:|---|---|
| MD-019 | `MD-019_Product_and_Service_Catalogue_Seed.md` | Every sellable service and product: code, name (EN/BN), category, attributes, tax class, revenue-stream binding | Nothing can be booked, quoted, priced, invoiced or reported without the catalogue. It is the spine of all 14 revenue streams | P0 | W1 | Commercial | `M37`, `M11` |
| MD-020 | `MD-020_Service_Type_and_Delivery_Mode_Register.md` | Walk-in, on-site, pick & drop, remote, workshop and kiosk modes with eligibility, charging and SLA implications | Delivery mode changes price, promise, routing and staffing. Encoding it in the catalogue alone is insufficient | P0 | W1 | Operations | `M01`, `M02`, `M03` |
| MD-021 | `MD-021_Device_Category_Make_and_Model_Catalogue.md` | Device taxonomy to model level with brand, category, typical faults, parts family, service applicability | Device identity is mandatory at intake (`BRU-SRM-01`). Free-text device entry destroys analytics, warranty matching and parts planning | P0 | W1 | MDM + Technical | `M17`, `05-05` BRU-SRM-01 |
| MD-022 | `MD-022_Spare_Part_Catalogue_and_Compatibility_Matrix.md` | Part master, OEM/compatible flag, model compatibility, substitution rules, warranty class, hazard class | Parts issue, van stock, procurement, claim reimbursement and estimating all break on an ungoverned part master | P0 | W1 | Inventory | `M15`, `M43` |
| MD-023 | `MD-023_Unit_of_Measure_and_Packaging_Register.md` | UoM set, conversions, packaging levels, weight and volume for logistics | Stock accuracy, landed cost and courier rating all require consistent UoM | P1 | W1 | Inventory | `M15`, `M44` |
| MD-024 | `MD-024_Fault_Symptom_and_Diagnostic_Code_Taxonomy.md` | Structured customer-reported symptom codes and technician-confirmed fault codes, by device family | Free-text fault capture makes first-time-fix measurement, failure-pattern analytics, brand quality reporting and AI triage impossible | P0 | W1 | Technical + Quality | `M01`, `M31`, `M26` |
| MD-025 | `MD-025_Repair_Action_and_Resolution_Code_Taxonomy.md` | What was actually done: action codes, parts-versus-labour resolution, rework classification | Warranty claims are rejected without standard resolution coding; repair-time norms and job costing depend on it | P0 | W1 | Technical + Quality | `M31`, `M09` |
| MD-026 | `MD-026_Reason_Code_Register.md` | Cancellation, rejection, return, exception, delay, override and refund reasons across all modules | Every override must record a reason (`BR-STD-06`). Ad-hoc per-module reason lists make root-cause analysis impossible | P1 | W1 | Operations + Quality | `05-05` BR-STD-06 |
| MD-027 | `MD-027_Status_and_Lifecycle_State_Label_Register.md` | Canonical state names and customer-facing labels for every state machine in the system, bilingual | `05-02` DM-10 requires one declared transition map per model. Customer, technician and agent must see the same state named the same way | P0 | W1 | Enterprise Architecture | `05-02` DM-10, `VB-008` |
| MD-028 | `MD-028_Priority_Severity_and_SLA_Definition_Register.md` | Priority and severity scales, response and resolution targets by contract class, business-hour calendars, pause rules | SLA is a contractual and financial obligation carrying service credits. It cannot be configured from prose scattered across module files | P0 | W1 | Service Ops + Legal | `M08`, `M05`, `LG-015` |

#### 02D — Commercial & Pricing — `02D_Commercial_and_Pricing/`

| ID | File | What it contains | Why it is needed | Pri | Wave | Owner | Traces to |
|---|---|---|---|:--:|:--:|---|---|
| MD-029 | `MD-029_Price_List_and_Rate_Card_Seed.md` | Standard, corporate, brand-warranty, marketplace and refurbished price lists; labour rates; call-out charges; zone surcharges | Pricing is the most-changed and most-disputed data in the system. It must be governed, versioned and effective-dated from day one | P0 | W1 | Commercial | `M11`, `M36` |
| MD-030 | `MD-030_Discount_Promotion_and_Voucher_Rule_Register.md` | Discount ceilings by role, stacking rules, voucher types, campaign codes, approval thresholds | Uncontrolled discounting is the fastest margin leak in a service business; rules must exist before the UI exposes a discount field | P1 | W2 | Commercial + Finance | `M11`, `M35` |
| MD-031 | `MD-031_Warranty_Type_and_Coverage_Term_Catalogue.md` | Manufacturer, service, extended and protection-plan warranty types with coverage, exclusions, duration and claim rules | Warranty eligibility is a hard rule at order creation (`BRU-SRM-02`). The rule needs a catalogue to evaluate against | P0 | W2 | Warranty | `M09`, `05-05` BRU-SRM-02 |
| MD-032 | `MD-032_Contract_and_AMC_Template_Catalogue.md` | AMC/RAMC/MSP contract templates, entitlement structures, visit schedules, coverage matrices, renewal terms | Contract-type orders are blocked unless the device is on an active contract's covered-asset list (`BRU-SRM-03`) | P1 | W2 | Account Management | `M08`, `05-05` BRU-SRM-03 |
| MD-033 | `MD-033_Subscription_Plan_and_Billing_Cycle_Register.md` | Subscription products, cycles, proration, dunning ladders, pause and resume rules | `M39` recurring revenue cannot be configured or revenue-recognised without plan definitions | P2 | W4 | Commercial + Finance | `M39`, `M53` |
| MD-034 | `MD-034_Loyalty_Tier_Point_and_Benefit_Register.md` | Privilege tiers, earn and burn rates, benefit schedules, expiry, tier-movement rules | A computed rule grants Gold and Diamond members priority-1 SLA (`BRU-SRM-10`); the tiers must be defined for it to fire | P2 | W2 | Commercial | `M10`, `05-05` BRU-SRM-10 |

#### 02E — Finance & Statutory — `02E_Finance_and_Statutory/`

| ID | File | What it contains | Why it is needed | Pri | Wave | Owner | Traces to |
|---|---|---|---|:--:|:--:|---|---|
| MD-035 | `MD-035_Chart_of_Accounts_Bangladesh.md` | Full chart of accounts aligned to Bangladesh statutory reporting, with account types, control accounts and posting rules | No transaction can post until the CoA exists. It is the first configuration object of any ERP finance go-live | P0 | W1 | Finance | `M19` |
| MD-036 | `MD-036_Cost_Centre_Business_Line_and_Dimension_Register.md` | Cost centres, the 14 revenue-stream business lines, zone and branch analytic dimensions | `05-02` DM-03 requires every transactional model to carry these dimensions. Profitability by revenue stream is a board-level commitment | P0 | W1 | Finance | `05-02` DM-03, `M54` |
| MD-037 | `MD-037_Tax_Code_VAT_Rate_and_Mushak_Mapping_Register.md` | VAT rates by supply type, VDS rates, exemptions, supplementary duty and AIT where applicable, and the mapping of each to Mushak 6.1 / 6.2 / 6.3 / 6.6 / 9.1 output | NBR-compliant Mushak generation is mandatory for VAT-registered businesses. The ERP must derive the correct form and rate per transaction automatically, and records must be retained for at least five years | P0 | W1 | Tax + Finance | `M51`, `DT-010` … `DT-014` |
| MD-038 | `MD-038_Payment_Method_Term_and_Bank_Master.md` | Payment methods (bKash, Nagad, Rocket, card, BEFTN, cash), terms, bank accounts, settlement and reconciliation keys | Nine payment integrations (`05-03` §2.1) settle into accounts that must be pre-defined for automated reconciliation | P0 | W3 | Treasury | `M50`, `05-03` INT-001…009 |
| MD-039 | `MD-039_Currency_FX_and_Rounding_Standard.md` | BDT as functional currency, foreign-currency handling for imports, FX source, revaluation and rounding policy | `05-02` DM-07 mandates monetary fields with an explicit currency; import landed cost (`M44`) requires an FX policy | P1 | W1 | Finance | `05-02` DM-07, `M44` |
| MD-040 | `MD-040_Document_Sequence_and_Numbering_Mask_Register.md` | Numbering masks for every document type, branch- and business-line-aware, with reset policy and statutory continuity rules | `05-02` DM-11 requires branch-aware sequences. Statutory documents must be gap-free and auditable; numbering cannot be retrofitted after go-live | P0 | W1 | Finance + Enterprise Architecture | `05-02` DM-11 |
| MD-041 | `MD-041_Fiscal_and_Bangladesh_Holiday_Calendar.md` | Fiscal periods, Bangladesh public and religious holidays, branch-specific closures, working calendars | SLA clocks, payroll, attendance, dispatch capacity and financial close all read the calendar | P0 | W1 | Finance + HR | `M55`, `MD-028` |

#### 02F — Workforce & Asset — `02F_Workforce_and_Asset/`

| ID | File | What it contains | Why it is needed | Pri | Wave | Owner | Traces to |
|---|---|---|---|:--:|:--:|---|---|
| MD-042 | `MD-042_Shift_Roster_and_Working_Pattern_Master.md` | Shift definitions, roster patterns, overtime rules, geofence parameters, break policy | `M55` scheduling and technician clock-in with geofence (`P02`) both consume it | P1 | W2 | HR + Operations | `M55`, `P02` |
| MD-043 | `MD-043_Payroll_Element_and_Statutory_Deduction_Register.md` | Earnings, deductions, allowances, incentive elements, tax slabs, provident fund and statutory contributions | Payroll cannot be run or filed without the element structure; technician incentive schemes depend on it | P0 | W5 | HR + Finance | `M56`, `M57` |
| MD-044 | `MD-044_Asset_Class_and_Depreciation_Schedule_Register.md` | Fixed-asset classes, useful lives, depreciation methods, capitalisation thresholds | `M49` cannot post depreciation and `M45` cannot value test equipment without it | P2 | W5 | Finance | `M49`, `M45` |
| MD-045 | `MD-045_Fleet_and_Vehicle_Master.md` | Vehicles, assignment, fuel policy, service schedule, telematics device binding | `M46` fleet management and `P09` rider assignment require a vehicle register | P2 | W3 | Facilities | `M46`, `P09` |
| MD-046 | `MD-046_Test_Equipment_and_Calibration_Master.md` | Test and repair equipment, calibration intervals, certificates, custody, ISO 9001 traceability | ISO 9001:2015 requires calibration control of measuring equipment; audit evidence depends on the register | P1 | W5 | Quality + Facilities | `M45`, `M23` |
| MD-047 | `MD-047_EWaste_Material_and_Disposal_Route_Register.md` | Material categories, hazard class, approved disposal partners, recovery rates, certificate requirements | `M18` must issue defensible disposal certificates and report material recovery to regulators and corporate clients | P2 | W5 | Sustainability | `M18`, `DT-035` |
| MD-048 | `MD-048_Master_Data_Seed_Load_Workbook_Index.md` | Index of all loadable data files, load order, dependency graph, environment targets, reload policy | Forty-seven datasets loaded in the wrong order fail on foreign keys. Load sequence is itself a deliverable | P0 | W1 | MDM + Data Migration | `DM-003`, `DM-012` |

---

### CATEGORY 03 — `UI` UI COPY & MICROCOPY
**Folder:** `03_UI_Copy_and_Microcopy/` · **42 files**

> Twelve portals, fourteen admin workspaces, two languages, five frameworks (Odoo OWL, Next.js,
> React Native, Flutter, Metabase). Every string a user reads is content, and every string
> exists twice. `PS-09` makes this contractual: *every user-visible error states what happened
> and what to do next, in the user's language.* That obligation cannot be met by developers
> writing strings inline.

#### 03A — Cross-Cutting Libraries — `03A_Cross_Cutting/`

| ID | File | What it contains | Why it is needed | Pri | Wave | Owner | Traces to |
|---|---|---|---|:--:|:--:|---|---|
| UI-001 | `UI-001_UI_String_Architecture_and_i18n_Key_Standard.md` | Key naming, namespacing by portal and module, placeholder and interpolation rules, plural forms, string reuse policy, extraction pipeline | Five frameworks with no shared key standard means the same string is translated five times and drifts four ways | P0 | W1 | Content Design + Platform | `M65`, `PS-03` |
| UI-002 | `UI-002_Global_Navigation_and_Label_Register.md` | Every menu, tab, breadcrumb, section and page title across all surfaces, bilingual | Navigation labels are the vocabulary users learn first; inconsistency here undermines all training | P0 | W1 | Content Design | `CG-004` |
| UI-003 | `UI-003_Field_Label_Placeholder_and_Help_Text_Library.md` | Label, placeholder, hint, unit and inline-help text for every field of every governed entity | 225+ entities with unlabelled or inconsistently labelled fields makes data entry the largest source of data-quality defects | P0 | W1 | Content Design + BA | `05-02` |
| UI-004 | `UI-004_Validation_and_Error_Message_Library.md` | Every field-level, form-level and business-rule violation message, with cause and remedy, bilingual | `BR-STD-04` requires every rule violation to state what is wrong and what to do, in the user's language. This library is where that obligation is discharged | P0 | W1 | Content Design + BA | `05-05` BR-STD-04, `PS-09` |
| UI-005 | `UI-005_System_Permission_and_Session_Message_Library.md` | Access denied, session expiry, MFA prompts, rate limit, maintenance, version-mismatch and service-unavailable copy | Security messages that leak internals are a vulnerability; messages that explain nothing generate hotline calls | P1 | W1 | Content Design + Security | `M29`, `PS-12` |
| UI-006 | `UI-006_Empty_State_and_First_Run_Copy_Library.md` | Zero-data, no-results, filtered-to-nothing, not-yet-configured and first-login copy for every list and dashboard | On day one of every wave, every screen is empty. Empty states are the first thing 800+ internal users ever see | P1 | W1 | Content Design | `UI-002` |
| UI-007 | `UI-007_Confirmation_Warning_and_Destructive_Action_Library.md` | Confirmation dialogs, irreversible-action warnings, override-with-reason prompts, approval confirmations | `BR-STD-06` permits overrides only where designed and always logged with a reason. The prompt that captures that reason is content | P0 | W1 | Content Design + Risk | `05-05` BR-STD-06 |
| UI-008 | `UI-008_Loading_Progress_and_Long_Running_Job_Copy.md` | Skeleton, spinner, progress, queued, retrying and partial-result copy, including bulk operations | `NFR-041` requires bulk operations on 1,000 records to give progress feedback. The feedback is words | P2 | W1 | Content Design | `05-06` NFR-041 |
| UI-009 | `UI-009_Offline_Sync_and_Conflict_Resolution_Copy.md` | Offline banner, queued-action, sync-in-progress, sync-failed, conflict-choice and data-loss-prevention copy | `PS-08` and `NFR-047` require 24-hour offline operation on `P02`, `P09` and `P11`. A technician who cannot tell whether work is saved will re-enter it or lose it | P0 | W2 | Content Design + Mobile | `PS-08`, `P02`, `P09`, `P11` |
| UI-010 | `UI-010_Accessibility_Text_Library.md` | Alt text, ARIA labels, live-region announcements, focus-order narration, screen-reader-only text, Bengali equivalents | WCAG 2.1 AA (`PS-04`) is contractual; assistive-technology text is content and must be authored, not generated | P1 | W1 | Content Design | `PS-04`, `CG-011` |

#### 03B — Portal Copy Packs — `03B_Portals/`

> One pack per portal. Each contains screen-by-screen copy, flow-specific microcopy, portal-specific
> terminology bindings, and the Bengali counterpart reference.

| ID | File | Portal | Why it is needed | Pri | Wave | Owner | Traces to |
|---|---|---|---|:--:|:--:|---|---|
| UI-011 | `UI-011_P01_Customer_Portal_and_App_UI_Copy_Pack.md` | P01 Customer Self-Service | Highest-volume surface: 250,000+ customers a month, Bengali-first, booking-funnel conversion is the primary design KPI (target > 72%). Copy is the conversion lever | P0 | W2 | Content Design | `P01` |
| UI-012 | `UI-012_P02_Technician_App_UI_Copy_Pack.md` | P02 Technician Mobile | 200–400 field technicians; complete Bengali UI *including error messages* is a non-negotiable requirement (`P02` §Non-Negotiable #3) | P0 | W2 | Content Design | `P02` |
| UI-013 | `UI-013_P03_Admin_Operations_Portal_UI_Copy_Pack.md` | P03 Admin Operations | 150–250 back-office users, fourteen workspaces, target training-time-to-competence under 4 hours. That target is met by copy, not features | P0 | W1 | Content Design | `P03` |
| UI-014 | `UI-014_P04_Corporate_B2B_Portal_UI_Copy_Pack.md` | P04 Corporate B2B | 500–2,000 corporate users with delegated approval chains and consolidated billing; ambiguity here creates invoice disputes (target < 3%) | P1 | W4 | Content Design | `P04` |
| UI-015 | `UI-015_P05_Vendor_and_Supplier_Portal_UI_Copy_Pack.md` | P05 Vendor & Supplier | Target: > 90% of POs acknowledged and > 85% of invoices submitted through the portal, with a 60% cut in vendor phone queries. Self-explanatory copy is the mechanism | P1 | W3 | Content Design | `P05` |
| UI-016 | `UI-016_P06_Analytics_and_Executive_Dashboard_Copy_Pack.md` | P06 Analytics & Executive | Metric names, filter labels, drill-path labels and definitional tooltips. An unlabelled executive dashboard produces confidently wrong decisions | P1 | W4 | Content Design + BI | `P06`, `RP-001` |
| UI-017 | `UI-017_P07_Marketplace_Seller_Portal_UI_Copy_Pack.md` | P07 Marketplace Seller | 500–2,000 external sellers, many low-literacy in English; onboarding completion target > 60% depends heavily on registration copy | P2 | W7 | Content Design | `P07` |
| UI-018 | `UI-018_P08_Brand_Partner_Portal_UI_Copy_Pack.md` | P08 Brand Partner | 17+ international brand partners reviewing claims. Copy quality here is a reputational surface with commercial consequence | P2 | W4 | Content Design | `P08` |
| UI-019 | `UI-019_P09_Logistics_and_Rider_App_UI_Copy_Pack.md` | P09 Logistics & Rider | Riders operate one-handed, outdoors, offline, in Bengali. Custody-break prevention depends on unambiguous scan and handover copy | P1 | W3 | Content Design | `P09` |
| UI-020 | `UI-020_P10_Contact_Centre_Console_UI_Copy_Pack.md` | P10 Contact Centre | Target: fewer than 3 screen switches per contact and 100% disposition-coding completeness. Both are copy and labelling outcomes | P1 | W4 | Content Design | `P10` |
| UI-021 | `UI-021_P11_Field_Auditor_App_UI_Copy_Pack.md` | P11 Field Auditor | Audit findings must be classified consistently by 20–60 auditors; the classification copy *is* the standard | P2 | W5 | Content Design + Quality | `P11` |
| UI-022 | `UI-022_P12_Partner_and_Referral_Portal_UI_Copy_Pack.md` | P12 Partner & Referral | Commission and attribution copy must be unambiguous — partner commission accuracy target is 100% and disputes start with wording | P2 | W7 | Content Design | `P12` |

#### 03C — Admin Workspace Copy — `03C_Admin_Workspaces/`

> `P03` is delivered as fourteen role-scoped workspaces (`04-00` §P03). Each has a distinct
> vocabulary, a distinct opening view and a distinct set of bulk actions.

| ID | File | Workspace | Why it is needed | Pri | Wave | Owner | Traces to |
|---|---|---|---|:--:|:--:|---|---|
| UI-023 | `UI-023_Workspace_Service_Intake_Copy.md` | Service Intake | Walk-in intake target is under 3 minutes; the copy drives keyboard-first speed for 150–250 agents | P0 | W1 | Content Design | `M04`, `P03` |
| UI-024 | `UI-024_Workspace_Dispatch_Console_Copy.md` | Dispatch Console | Dispatching a full morning queue in under 10 minutes requires unambiguous SLA-risk and load labelling | P0 | W1 | Content Design | `M02`, `P03` |
| UI-025 | `UI-025_Workspace_Branch_Console_Copy.md` | Branch Console | 51+ branch managers reading the same numbers must read them identically | P1 | W1 | Content Design | `M04`, `P03` |
| UI-026 | `UI-026_Workspace_Workshop_Console_Copy.md` | Workshop Console | Bench board, WIP state and parts-hold labels drive throughput in the depot repair flow | P1 | W1 | Content Design | `M31`, `P03` |
| UI-027 | `UI-027_Workspace_Inventory_Console_Copy.md` | Inventory Console | Network stock, alert and transfer labels prevent the most common inventory error: acting on the wrong location | P1 | W1 | Content Design | `M15`, `M41` |
| UI-028 | `UI-028_Workspace_Procurement_Console_Copy.md` | Procurement Console | Requisition-to-PO state language must match what vendors see in `P05`, or every handoff generates a query | P1 | W3 | Content Design | `M16`, `P05` |
| UI-029 | `UI-029_Workspace_Finance_Console_Copy.md` | Finance Console | Reconciliation, ageing and close-checklist copy carries statutory consequence when misread | P1 | W1 | Content Design + Finance | `M19`, `M20` |
| UI-030 | `UI-030_Workspace_HR_Console_Copy.md` | HR Console | Attendance exception, leave and payroll-run language affects pay accuracy for 500+ employees | P1 | W5 | Content Design + HR | `M21`, `M55`, `M56` |
| UI-031 | `UI-031_Workspace_Quality_Console_Copy.md` | Quality Console | NCR, CAPA and audit terminology is ISO 9001 vocabulary and must not be paraphrased | P1 | W5 | Content Design + Quality | `M23` |
| UI-032 | `UI-032_Workspace_Contract_Console_Copy.md` | Contract Console | Entitlement and renewal wording directly affects revenue recognition and customer disputes | P1 | W2 | Content Design | `M08` |
| UI-033 | `UI-033_Workspace_Warranty_Console_Copy.md` | Warranty Console | Claim pipeline and rejection-reason copy is reused verbatim in brand-facing evidence packs | P1 | W4 | Content Design | `M09`, `P08` |
| UI-034 | `UI-034_Workspace_Marketplace_Console_Copy.md` | Marketplace Console | Seller approval, dispute and payout language has contractual force under the seller agreement | P2 | W7 | Content Design | `M12`, `P07` |
| UI-035 | `UI-035_Workspace_Managed_Services_Console_Copy.md` | Managed Services Console | Estate health, alert and patch-compliance language is repeated to corporate clients in `P04` and in service reviews | P2 | W4 | Content Design | `M05`, `P04` |
| UI-036 | `UI-036_Workspace_System_Console_Copy.md` | System Console | Administrator actions are the most destructive in the system; their confirmation copy is a safety control | P1 | W1 | Content Design + Security | `M30`, `M29` |

#### 03D — Critical Flow Copy — `03D_Critical_Flows/`

| ID | File | What it contains | Why it is needed | Pri | Wave | Owner | Traces to |
|---|---|---|---|:--:|:--:|---|---|
| UI-037 | `UI-037_Booking_and_Order_Creation_Flow_Copy.md` | End-to-end booking copy across P01, P03, P10 and the corporate bulk path | The same booking exists on four surfaces. Divergent copy produces four different customer promises for one transaction | P0 | W2 | Content Design | `M01`, `P01`, `P03`, `P10` |
| UI-038 | `UI-038_Estimate_and_Approval_Flow_Copy.md` | Estimate presentation, part-approval, decline, revision, expiry and e-signature copy | Estimates above BDT 5,000 require documented customer approval (`BRU-SRM-07`). The wording of that approval is the evidence | P0 | W2 | Content Design + Legal | `05-05` BRU-SRM-07/08 |
| UI-039 | `UI-039_Payment_and_Checkout_Flow_Copy.md` | Payment method selection, authorisation, failure, retry, partial payment, refund and receipt copy | Payment-path availability is 99.95% with multi-gateway failover (`NFR-048`); the failover must be explained to the customer in the moment | P0 | W3 | Content Design | `M20`, `05-03` §2.1 |
| UI-040 | `UI-040_Registration_and_Onboarding_Flow_Copy.md` | Registration, OTP, verification, document upload and approval-status copy for customers, sellers, vendors, partners and employees | Five audiences onboard through five flows with one identity platform (`M29`). Inconsistent onboarding copy creates five support burdens | P1 | W2 | Content Design | `M29`, `M33` |
| UI-041 | `UI-041_Search_Filter_and_Bulk_Action_Copy.md` | Search scope, filter, saved-view, selection-count, bulk-action and undo copy | Bulk actions on every list view are a `P03` design requirement; unclear selection scope in bulk actions causes mass data damage | P2 | W1 | Content Design | `P03` |
| UI-042 | `UI-042_Consent_Privacy_and_Preference_Centre_Copy.md` | Consent capture, purpose statements, withdrawal, preference centre and data-request copy | Consent copy is the operative legal text under the Bangladesh Personal Data Protection Act 2026 regime referenced in `05-06` NFR-086 | P0 | W2 | Content Design + Legal | `LG-008`, `05-06` NFR-086 |

---

### CATEGORY 04 — `NT` NOTIFICATION & MESSAGING CONTENT
**Folder:** `04_Notification_and_Messaging/` · **26 files**

> The ERP will emit millions of messages a month across SMS, WhatsApp, email, push, in-app and
> voice, to eleven audience types, in two languages. Every one is a cost, a legal act, a brand
> impression and — for OTP and payment — a security control.

| ID | File | What it contains | Why it is needed | Pri | Wave | Owner | Traces to |
|---|---|---|---|:--:|:--:|---|---|
| NT-001 | `NT-001_Notification_Strategy_and_Event_Channel_Matrix.md` | Every notifiable domain event mapped to audience, channel, priority, language, template ID and suppression rule | Without one matrix, each module invents its own notifications; customers receive duplicates from three modules for one event | P0 | W1 | Content Design + Platform | `M27`, `05-03` events |
| NT-002 | `NT-002_Notification_Preference_and_Consent_Copy.md` | Opt-in/opt-out copy per channel and event class, marketing-versus-transactional distinction, consent records | Marketing consent and transactional necessity are legally distinct. Conflating them exposes the company under the data-protection regime | P0 | W2 | Content Design + Legal | `LG-008`, `P01` |
| NT-003 | `NT-003_Quiet_Hours_Throttling_and_Frequency_Policy.md` | Send windows, per-customer frequency caps, batching, escalation exemptions, religious and public-holiday sensitivity | Messaging a customer at 03:00 or eleven times in a day destroys channel trust and triggers opt-outs the business cannot afford | P1 | W2 | Content Design + Ops | `M27` |
| NT-004 | `NT-004_SMS_Template_Library_Customer.md` | Booking, assignment, arrival, estimate, completion, ready-for-collection, delivery and feedback SMS, bilingual, with character-count and segment-cost analysis | SMS remains the highest-reach channel in Bangladesh. Bengali Unicode SMS segments at 70 characters, not 160 — an unmanaged template library triples send cost | P0 | W2 | Content Design | `M27`, `M01` |
| NT-005 | `NT-005_SMS_Template_Library_Technician_and_Field.md` | Job assignment, reassignment, escalation, roster, safety and payout SMS for field staff | Technicians without data connectivity still receive SMS; it is the fallback channel for dispatch | P1 | W2 | Content Design | `M02`, `P02` |
| NT-006 | `NT-006_SMS_Template_Library_Finance_and_Collections.md` | Payment reminder, overdue, receipt confirmation, refund and dunning-ladder SMS | Collections messaging carries legal tone constraints; ad-hoc wording creates harassment exposure | P1 | W3 | Content Design + Finance | `M20` |
| NT-007 | `NT-007_OTP_and_Security_Message_Library.md` | OTP, login alert, password change, new-device, MFA and suspicious-activity messages | OTP wording is an anti-phishing control; inconsistent OTP messages train customers to trust forgeries | P0 | W1 | Content Design + Security | `M29` |
| NT-008 | `NT-008_WhatsApp_Business_Template_Library.md` | Every WhatsApp template in the format required for Meta pre-approval, with variables, categories and Bengali versions | WhatsApp templates must be submitted and approved *before* use; approval lead time makes this a schedule dependency, not a content nicety | P1 | W2 | Content Design + Ops | `M27`, `05-03` |
| NT-009 | `NT-009_Email_Template_Library_Customer_Transactional.md` | Welcome, confirmation, status, estimate, invoice, receipt, completion, feedback, cancellation, refund emails | The transactional email set is the customer's written record of the transaction and the reference in any dispute | P1 | W2 | Content Design | `M01`, `M20` |
| NT-010 | `NT-010_Email_Template_Library_Corporate_and_B2B.md` | Consolidated invoice, approval request, SLA breach, service review, contract renewal and estate report emails | Corporate recipients forward these internally; they are read by people who never log into `P04` | P1 | W4 | Content Design | `P04`, `M08` |
| NT-011 | `NT-011_Email_Template_Library_Vendor_and_Supplier.md` | RFQ, PO, delivery, rejection, invoice-matching, remittance and scorecard emails | Vendor adoption targets (> 90% PO acknowledgement) depend on emails that make the required action obvious | P2 | W3 | Content Design | `P05`, `M16` |
| NT-012 | `NT-012_Email_Template_Library_Seller_and_Partner.md` | Approval, job broadcast, payout, dispute, policy-update and performance-warning emails | Performance warnings and suspensions have contractual effect under the seller agreement and must be worded to it | P2 | W7 | Content Design + Legal | `P07`, `P12`, `LG-004` |
| NT-013 | `NT-013_Email_Template_Library_Brand_Partner_Claims.md` | Claim submission, additional-information request, decision, reconciliation and remittance emails | Brand claim decision cycle target is under 10 days; unclear information requests are the main cause of delay | P2 | W4 | Content Design | `P08`, `M09` |
| NT-014 | `NT-014_Email_Template_Library_Internal_and_HR.md` | Approval requests, roster, payroll, leave, certification expiry, training assignment and incident emails | 500+ employees receive system email; poor internal messaging is the fastest route to shadow processes | P2 | W5 | Content Design + HR | `M21`, `M22` |
| NT-015 | `NT-015_Push_Notification_Library_P01_Customer_App.md` | Push copy for every customer-relevant event, with deep links and Bengali versions | Push has a hard character budget and one chance; poorly written push drives permission revocation | P2 | W6 | Content Design | `P01` |
| NT-016 | `NT-016_Push_Notification_Library_P02_Technician_App.md` | Job, reassignment, escalation, safety, sync and shift push copy | Technicians act on push; ambiguity costs a wasted journey | P1 | W2 | Content Design | `P02` |
| NT-017 | `NT-017_Push_Notification_Library_P09_Rider_App.md` | Manifest, pickup, exception, reschedule and cash-reconciliation push copy | Riders operate hands-busy; push is often the only message read | P2 | W3 | Content Design | `P09` |
| NT-018 | `NT-018_In_App_Notification_and_Inbox_Copy.md` | In-app inbox entries, grouping, read/unread, expiry and archive copy across all portals | `P01` promises an in-app inbox of all notifications; it becomes a second unmanaged content surface if unspecified | P2 | W2 | Content Design | `P01`, `M27` |
| NT-019 | `NT-019_IVR_and_Voice_Prompt_Scripts.md` | Hotline 16743 IVR tree, prompts, menus, hold, callback and after-hours messages, bilingual, with recording direction | The hotline is the highest-trust channel for a large share of 250,000+ monthly customers and predates the portal | P1 | W4 | Content Design + Contact Centre | `M27`, `P10` |
| NT-020 | `NT-020_Escalation_and_SLA_Breach_Notification_Library.md` | Warning, imminent-breach, breach and service-credit notifications to internal and customer audiences | SLA breach notifications carry financial consequence (service credits) and must be precise and timely | P1 | W2 | Content Design + Service Ops | `M08`, `MD-028` |
| NT-021 | `NT-021_System_Integration_and_Job_Failure_Alert_Library.md` | Integration failure, batch failure, queue backlog, reconciliation mismatch and health alerts, with severity and runbook links | `IP-06` requires every integration to be observable and alerting on failure. An alert with no remedy text wastes the on-call engineer's first ten minutes | P1 | W1 | Platform Engineering | `05-03` IP-06, `OP-008` |
| NT-022 | `NT-022_Approval_Request_and_Reminder_Library.md` | Approval requests, delegation, reminders, escalation-on-timeout and expiry notices across all approval chains | Approval chains span estimates, discounts, purchases, payroll, leave and corporate delegation. Unclear requests stall the whole flow | P1 | W2 | Content Design | `SP-004` |
| NT-023 | `NT-023_Marketing_and_Lifecycle_Campaign_Message_Library.md` | Lifecycle journeys — onboarding, reactivation, AMC renewal, seasonal, cross-sell — across email, SMS and push | `M35` demand generation needs a governed message set that respects `NT-002` consent and `NT-003` frequency limits | P2 | W4 | Marketing | `M35`, `M10` |
| NT-024 | `NT-024_Survey_Feedback_and_NPS_Invitation_Library.md` | Post-service rating, NPS, technician rating, complaint-follow-up and closure-confirmation messages | CSAT and NPS are board-level KPIs; response rate is driven almost entirely by invitation wording and timing | P2 | W2 | Content Design + CX | `M34`, `06-02` |
| NT-025 | `NT-025_Notification_Failure_and_Fallback_Copy.md` | What the user sees when a channel fails, channel-downgrade messaging, and undeliverable handling | `IP-09` requires a defined manual fallback for every P0 integration. The fallback is invisible unless it is written | P2 | W2 | Content Design | `05-03` IP-09 |
| NT-026 | `NT-026_Message_Template_Governance_and_Change_Log.md` | Template ownership, version history, approval record, WhatsApp re-approval triggers, retirement | Templates are edited by many hands under commercial pressure; an unlogged change to an OTP or invoice message is a security and audit incident | P1 | W2 | Programme Content Lead | `CG-006` |

---

### CATEGORY 05 — `DT` DOCUMENT, PRINT & STATUTORY OUTPUT TEMPLATES
**Folder:** `05_Document_and_Print_Templates/` · **44 files**

> Everything the system prints, emails as PDF, or hands to a customer, regulator, brand partner
> or auditor. Fourteen of these carry statutory force in Bangladesh. All are bilingual where a
> customer or employee is the recipient.

#### 05A — Service & Operations — `05A_Service_and_Operations/`

| ID | File | What it contains | Why it is needed | Pri | Wave | Owner | Traces to |
|---|---|---|---|:--:|:--:|---|---|
| DT-001 | `DT-001_Document_Template_Standard_and_Branding_Rules.md` | Page geometry, header/footer, statutory blocks, QR and barcode placement, bilingual layout, signature and stamp zones, print and PDF output rules | Forty-three templates authored to no standard produce forty-three inconsistent legal documents | P0 | W1 | Brand + Enterprise Architecture | `VB-004` |
| DT-002 | `DT-002_Service_Intake_Receipt_and_Device_Handover_Form.md` | Device identification, declared condition, accessories, customer declarations, data-backup warning, liability terms, signatures | This is the custody document. Disputes about device condition at intake are the most common customer conflict in device service | P0 | W1 | Operations + Legal | `M04`, `M17` |
| DT-003 | `DT-003_Job_Card_and_Work_Order_Print.md` | Work order for bench and field use: job context, device history, assigned parts, checklist, time record | The physical artefact that travels with a device through the workshop; required even in a digital-first design for offline and audit reasons | P1 | W1 | Operations | `M01`, `M31` |
| DT-004 | `DT-004_Diagnostic_and_Condition_Report.md` | Structured findings, fault codes, photographic evidence, recommendation, out-of-scope observations | Justifies the estimate to the customer, the claim to the brand, and the decision to the auditor | P1 | W1 | Technical | `MD-024`, `M31` |
| DT-005 | `DT-005_Repair_Estimate_and_Quotation.md` | Itemised parts and labour, taxes, validity, terms, approval block, bilingual | Estimates over BDT 5,000 need documented approval (`BRU-SRM-07`); the document is the evidence | P0 | W1 | Commercial + Operations | `M36`, `05-05` BRU-SRM-07 |
| DT-006 | `DT-006_Revised_Estimate_and_Approval_Record.md` | Variation from original, reason, delta, re-approval capture, cumulative-total display | Scope growth mid-repair is the second most common dispute; an unlogged revision is unrecoverable | P1 | W2 | Operations | `M36`, `M01` |
| DT-007 | `DT-007_Service_Completion_Report.md` | Work performed, parts replaced, tests passed, warranty granted, technician identity and certification | Given to the customer, submitted to the brand, and cited in any warranty claim on the repair itself | P1 | W1 | Operations + Quality | `M01`, `M23` |
| DT-008 | `DT-008_Quality_Checklist_Record.md` | The QC checklist per service category, pass/fail evidence, inspector identity | A service order cannot reach Completed unless the quality checklist is recorded as passed (`BRU-SRM-04`) | P1 | W1 | Quality | `05-05` BRU-SRM-04, `M23` |
| DT-009 | `DT-009_Device_Release_and_Collection_Receipt.md` | Identity verification, accessories returned, condition acknowledgement, payment status, signature or OTP | Closes the custody chain opened by `DT-002`. Uncollected-device liability turns on this document | P1 | W1 | Operations + Legal | `M04`, `M03` |

#### 05B — Finance & Statutory — `05B_Finance_and_Statutory/`

| ID | File | What it contains | Why it is needed | Pri | Wave | Owner | Traces to |
|---|---|---|---|:--:|:--:|---|---|
| DT-010 | `DT-010_Tax_Invoice_Mushak_6_3.md` | NBR-prescribed VAT invoice: supplier and buyer identity with BIN, description, quantity, unit price, value, VAT, in the mandated layout | Mushak 6.3 is the statutory tax invoice for VAT-registered businesses in Bangladesh. Issuing a non-conforming invoice is a compliance failure with penalty exposure; it must be generated automatically at the point of sale | P0 | W1 | Tax + Finance | `M51`, `M20`, `MD-037` |
| DT-011 | `DT-011_Sales_Register_Mushak_6_2.md` | Statutory sales register derived from issued Mushak 6.3 challans | Required as the summarisation basis for the Mushak 9.1 return; cannot be reconstructed reliably after the fact | P0 | W1 | Tax + Finance | `M51` |
| DT-012 | `DT-012_Purchase_Register_Mushak_6_1.md` | Statutory purchase register derived from received Mushak 6.3 challans | Input-VAT credit depends on it; missing entries are lost money as well as a compliance defect | P0 | W1 | Tax + Finance | `M51`, `M52` |
| DT-013 | `DT-013_VDS_Certificate_Mushak_6_6.md` | VAT deducted at source certificate issued to suppliers | Required whenever the company deducts VAT at source; suppliers cannot claim without it and will withhold service | P0 | W1 | Tax + Finance | `M51`, `M52` |
| DT-014 | `DT-014_VAT_Return_Pack_Mushak_9_1.md` | Periodic VAT return format and the supporting schedules that must accompany it | The statutory filing itself. Late or unsupported filing carries penalty and audit consequence | P0 | W1 | Tax + Finance | `M51` |
| DT-015 | `DT-015_Credit_Note_and_Debit_Note.md` | Adjustment documents with statutory reference to the original invoice, reason coding and VAT treatment | Refunds, rework and disputes all require a compliant adjustment document, not an edited invoice | P0 | W2 | Finance | `M20`, `M51` |
| DT-016 | `DT-016_Payment_Receipt_and_Money_Receipt.md` | Cash, mobile-money, card and bank receipt formats, bilingual, with branch and collector identity | Cash handling across 51+ branches is a fraud-exposed process; the receipt is the primary control | P0 | W1 | Finance | `M20`, `M50` |
| DT-017 | `DT-017_Customer_Statement_of_Account.md` | Period statement with opening balance, transactions, ageing and dispute instructions | Corporate collections and reconciliation are impossible without a statement customers accept as authoritative | P1 | W3 | Finance | `M20` |
| DT-018 | `DT-018_Dunning_and_Collection_Letter_Series.md` | Escalating reminder series with legally reviewed tone, and final-demand format | Collections language carries legal constraint; the escalation ladder must be pre-approved rather than improvised per case | P1 | W3 | Finance + Legal | `M20` |
| DT-019 | `DT-019_Proforma_Invoice_and_Advance_Request.md` | Pre-payment document for corporate procurement and advance-payment flows | Many corporate and government buyers cannot raise a payment without a proforma; its absence blocks revenue | P2 | W3 | Finance | `M20`, `M36` |
| DT-020 | `DT-020_Consolidated_Corporate_Invoice.md` | Multi-site, multi-department, multi-asset billing with itemised breakdown and approval trail | `P04` commits to consolidated invoices with itemised breakdown by site, department and asset, and an invoice-dispute rate below 3% | P1 | W4 | Finance + Account Management | `P04`, `M20` |

#### 05C — Supply Chain & Logistics — `05C_Supply_Chain_and_Logistics/`

| ID | File | What it contains | Why it is needed | Pri | Wave | Owner | Traces to |
|---|---|---|---|:--:|:--:|---|---|
| DT-021 | `DT-021_Purchase_Requisition.md` | Internal request format with justification, budget reference and approval chain | The audit trail for spend authorisation begins here, not at the PO | P2 | W3 | Procurement | `M16` |
| DT-022 | `DT-022_Request_for_Quotation.md` | RFQ format issued through `P05` with specification, quantity, terms and response deadline | RFQ response-rate target is > 75%; response quality depends on request clarity | P2 | W3 | Procurement | `M16`, `P05` |
| DT-023 | `DT-023_Purchase_Order.md` | Legally binding order with terms, delivery, tax treatment and acceptance conditions | The contract with the supplier. Ambiguity here is settled at the company's expense | P1 | W3 | Procurement + Legal | `M16` |
| DT-024 | `DT-024_Goods_Receipt_Note_and_Inspection_Record.md` | Received quantity, condition, inspection outcome, acceptance or rejection with reason | Three-way matching and vendor performance scoring both depend on a consistent GRN | P1 | W3 | Inventory | `M41`, `M42` |
| DT-025 | `DT-025_Return_to_Vendor_and_Debit_Advice.md` | Return authorisation, reason, credit expectation and logistics reference | Defective parts returned without documentation become an unrecoverable write-off | P2 | W3 | Inventory + Finance | `M15`, `M52` |
| DT-026 | `DT-026_Stock_Transfer_Note_and_Gate_Pass.md` | Inter-branch and warehouse transfer with custody signatures and security gate pass | Stock moving between 51+ locations without documented custody is stock that disappears | P1 | W1 | Inventory | `M15`, `M41` |
| DT-027 | `DT-027_Delivery_Challan_and_Logistics_Manifest.md` | Consignment contents, route, handling instruction, seal number, statutory movement documentation | Goods in transit in Bangladesh require accompanying documentation; the manifest also drives `P09` | P1 | W3 | Logistics | `M03`, `P09` |
| DT-028 | `DT-028_Proof_of_Delivery_and_Custody_Record.md` | Recipient identity, photo, OTP, signature, GPS and timestamp | Custody-break target is zero and POD completeness target is 100%; this template is how both are evidenced | P1 | W3 | Logistics | `P09`, `M03` |
| DT-029 | `DT-029_Physical_Count_and_Stock_Adjustment_Sheet.md` | Count sheet, variance record, adjustment authorisation and reason coding | Inventory adjustments without an authorised document are indistinguishable from theft | P2 | W3 | Inventory + Finance | `M15`, `M41` |

#### 05D — Commercial & Contract — `05D_Commercial_and_Contract/`

| ID | File | What it contains | Why it is needed | Pri | Wave | Owner | Traces to |
|---|---|---|---|:--:|:--:|---|---|
| DT-030 | `DT-030_Contract_and_AMC_Agreement_Template_Set.md` | AMC, RAMC, MSP and enterprise agreement templates with schedules and variable clauses | Contracts are generated at volume by account managers; a template set with controlled variables prevents unreviewed bespoke terms | P1 | W2 | Legal + Account Management | `M08`, `LG-015` |
| DT-031 | `DT-031_SLA_Schedule_and_Service_Credit_Annex.md` | Response and resolution commitments, measurement method, exclusions, credit calculation | Service credits are a direct financial liability; the calculation must be unambiguous and match `MD-028` exactly | P1 | W2 | Legal + Service Ops | `MD-028`, `M08` |
| DT-032 | `DT-032_Warranty_Certificate_and_Extension_Document.md` | Repair warranty and purchased-extension certificates with coverage, exclusions and claim instructions | The customer's proof of entitlement and the company's limit of liability, in one document | P1 | W2 | Warranty + Legal | `M09`, `LG-013` |
| DT-033 | `DT-033_Warranty_Claim_Evidence_Pack.md` | The assembled pack submitted to a brand: diagnosis, photos, parts, technician certification, purchase proof | Claim approval-rate target is > 92% and decision time under 10 days; both depend on evidence completeness at submission | P1 | W4 | Warranty | `M09`, `P08` |
| DT-034 | `DT-034_Data_Destruction_Certificate.md` | Device identity, method, standard applied, operator, witness, date, certificate number | Corporate and government clients require destruction certificates for audit and regulatory purposes; `P01` and `P04` both promise download | P1 | W2 | Data Services + Legal | `M06`, `P04` |
| DT-035 | `DT-035_EWaste_Disposal_and_Material_Recovery_Certificate.md` | Batch composition, disposal route, partner identity, recovery outcome, environmental declaration | Environmental compliance evidence for regulators and for corporate clients' own ESG reporting | P2 | W5 | Sustainability | `M18`, `MD-047` |
| DT-036 | `DT-036_Refurbishment_Grading_and_Certification_Record.md` | Grade definition applied, tests performed, parts replaced, warranty granted, disclosure statement | Refurbished resale without a defensible grading record produces returns, disputes and consumer-protection exposure | P2 | W5 | Refurbishment | `M14` |
| DT-037 | `DT-037_Rental_Agreement_and_Asset_Handover_Record.md` | Rental terms, asset identity and condition, deposit, liability, return condition standard | Equipment-as-a-Service places company assets in customer hands; the handover record is the recovery basis | P2 | W5 | Rental + Legal | `M13` |
| DT-038 | `DT-038_TradeIn_Offer_and_Acceptance_Record.md` | Device assessment, offer, deduction applied, ownership transfer declaration, data-erasure confirmation | Trade-in transfers ownership of a data-bearing device; the declaration protects both parties | P2 | W5 | Refurbishment + Legal | `M14`, `M06` |
| DT-039 | `DT-039_Marketplace_Seller_Payout_Statement.md` | Jobs, gross value, commission, fees, adjustments, holds, net payout and period | Seller trust in the platform rests almost entirely on payout transparency; disputes here are existential for `P07` | P2 | W7 | Marketplace Ops + Finance | `P07`, `M53` |
| DT-040 | `DT-040_Partner_Commission_Statement.md` | Referrals, conversions, attribution basis, commission rate, adjustments, payment schedule | Partner commission accuracy target is 100%; the statement is where accuracy is demonstrated | P2 | W7 | Finance + Partnerships | `P12`, `M53` |

#### 05E — People, Quality & Labelling — `05E_People_Quality_and_Labelling/`

| ID | File | What it contains | Why it is needed | Pri | Wave | Owner | Traces to |
|---|---|---|---|:--:|:--:|---|---|
| DT-041 | `DT-041_Payslip_and_Salary_Certificate.md` | Statutory payslip layout with earnings, deductions, employer contributions and YTD, plus salary certificate format | Payslips are a statutory entitlement for 500+ employees and the most scrutinised document HR issues | P1 | W5 | HR + Finance | `M56` |
| DT-042 | `DT-042_HR_Letter_Template_Set.md` | Offer, appointment, confirmation, transfer, promotion, warning, and exit/clearance letters | HR letters carry employment-law consequence; improvised wording creates dispute exposure across a 500-person workforce | P2 | W5 | HR + Legal | `M21`, `M58` |
| DT-043 | `DT-043_NCR_CAPA_and_Internal_Audit_Report_Forms.md` | Non-conformance report, corrective/preventive action record, internal audit report and finding classification | ISO 9001:2015 certification is the company's core differentiator; these are the forms the certification body inspects | P1 | W5 | Quality | `M23`, `P11` |
| DT-044 | `DT-044_Label_Barcode_and_QR_Format_Specification.md` | Device tag, part label, bin label, consignment label, asset tag: symbology, data payload, size, durability | Every scan-based workflow across `P02`, `P09`, `P11` and the warehouse depends on one label data contract | P1 | W1 | Enterprise Architecture + Inventory | `M15`, `M17`, `M41` |

---

### CATEGORY 06 — `SP` PROCESS, SOP & WORKFLOW CONTENT
**Folder:** `06_Process_SOP_and_Workflow/` · **34 files**

> Module specifications describe what the system permits. SOPs describe what a person must
> actually do, in what order, with what authority, and what to do when the exception occurs.
> An ISO 9001:2015 certified company is audited against these, not against its source code.

#### 06A — Process Architecture — `06A_Process_Architecture/`

| ID | File | What it contains | Why it is needed | Pri | Wave | Owner | Traces to |
|---|---|---|---|:--:|:--:|---|---|
| SP-001 | `SP-001_Process_Architecture_and_Value_Stream_Map.md` | The end-to-end value streams (request-to-cash, procure-to-pay, hire-to-retire, claim-to-reimbursement, lead-to-contract) and how the 67 modules serve them | Modules are organised by capability; the business runs by value stream. Without the mapping, no one can see where a stream breaks | P1 | W0 | Business Process Lead | `02-01` |
| SP-002 | `SP-002_As_Is_Process_Baseline_Register.md` | Documented current-state processes across branches, with variation, workarounds and known pain points | Change impact, migration scope and training design all need a baseline. Baselines cannot be reconstructed after cutover | P1 | W0 | Business Process Lead | `06-01` |
| SP-003 | `SP-003_To_Be_Process_Design_Standard_and_Notation.md` | Notation, level of decomposition, naming, swimlane conventions, RACI embedding, versioning | Sixty-seven modules' worth of process design authored to different conventions cannot be compared or reviewed | P2 | W0 | Business Process Lead | `SP-001` |
| SP-004 | `SP-004_Approval_Matrix_and_Delegation_of_Authority.md` | Who may approve what, to what value, with what delegation and escalation on absence | Estimates, discounts, purchases, write-offs, payroll and refunds all need authority limits before the workflow engine is configured | P0 | W1 | Finance + Governance | `05-05`, `M60` |
| SP-005 | `SP-005_Escalation_Matrix.md` | Operational, commercial, technical and safety escalation paths with timers, roles and out-of-hours cover | `NT-020` sends the escalation; this file decides to whom and when. Without it, escalation notifications have no destination | P1 | W1 | Service Ops | `M27`, `MD-028` |
| SP-006 | `SP-006_Segregation_of_Duties_Register.md` | Incompatible duty pairs, enforcement point, compensating controls where separation is impossible | Audit `00-07` H2-06 found 18 segregation-of-duties identifiers used in modules but never registered. This file is the register that closes that finding | P0 | W1 | Governance + Security | `00-07` H2-06, `05-04` |

#### 06B — Standard Operating Procedures — `06B_Standard_Operating_Procedures/`

| ID | File | What it contains | Why it is needed | Pri | Wave | Owner | Traces to |
|---|---|---|---|:--:|:--:|---|---|
| SP-007 | `SP-007_SOP_Walk_In_Intake_and_Front_Desk.md` | Greeting, identification, device receipt, condition capture, expectation setting, token, handover | The single most-repeated process in the company, executed by 150–250 agents across 51+ branches against a 3-minute target | P1 | W1 | Operations | `M04`, `P03` |
| SP-008 | `SP-008_SOP_On_Site_Field_Service_Visit.md` | Pre-visit checks, arrival, customer briefing, diagnosis, estimate, execution, evidence, sign-off, payment | Field visits happen unsupervised in customers' homes and offices; the SOP is the only control | P1 | W2 | Field Operations | `M02`, `P02` |
| SP-009 | `SP-009_SOP_Pick_and_Drop_and_Reverse_Logistics.md` | Booking, packing standard, seal, custody transfer, transit exception handling, return | Devices in transit are the company's highest-value uninsured exposure | P1 | W3 | Logistics | `M03`, `P09` |
| SP-010 | `SP-010_SOP_Workshop_and_Depot_Repair.md` | Bench assignment, WIP control, L1/L2/L3 escalation, parts hold, QC gate, release | Workshop throughput and rework rate are the largest determinants of service margin | P1 | W1 | Workshop | `M31` |
| SP-011 | `SP-011_SOP_Remote_Support_and_Managed_Services.md` | Consent capture, session control, evidence, patch and alert handling, escalation to on-site | Remote access to corporate estates has security and legal consequence; consent and logging are mandatory | P2 | W4 | MSP Operations | `M05`, `LG-016` |
| SP-012 | `SP-012_SOP_Data_Recovery_and_Secure_Data_Handling.md` | Chain of custody, isolated environment, access restriction, evidence, destruction, certificate issue | Data services touch the most sensitive data the company handles; `05-04` restricts access to assigned cases only | P1 | W2 | Data Services + Security | `M06`, `DT-034` |
| SP-013 | `SP-013_SOP_Estimate_Approval_and_Rework_Control.md` | Estimate construction, approval thresholds, revision, decline handling, rework classification and cost attribution | A repeat order for the same device and fault within 30 days is auto-flagged as rework (`BRU-SRM-06`); the SOP defines what happens next | P1 | W2 | Operations + Quality | `05-05` BRU-SRM-06/07/08 |
| SP-014 | `SP-014_SOP_Warranty_Claim_Submission_and_Reconciliation.md` | Eligibility check, evidence assembly, submission, query response, decision handling, financial reconciliation | Days-from-service-to-reimbursement target is under 45; the process, not the portal, determines whether that is met | P1 | W4 | Warranty | `M09`, `P08` |
| SP-015 | `SP-015_SOP_Contract_and_AMC_Lifecycle.md` | Qualification, quotation, approval, activation, entitlement management, amendment, renewal, termination | Contract revenue is recurring and compounding; leakage at any lifecycle stage is permanent | P1 | W2 | Account Management | `M08` |
| SP-016 | `SP-016_SOP_Spare_Parts_Issue_Return_and_Van_Stock.md` | Requisition, issue, consumption recording, unused return, van reconciliation, discrepancy handling | Parts cannot be issued against an unapproved paid repair (`BRU-SRM-11`); van stock is the least-controlled inventory in field service | P1 | W1 | Inventory | `M15`, `05-05` BRU-SRM-11 |
| SP-017 | `SP-017_SOP_Procurement_to_Payment.md` | Requisition, sourcing, PO, receipt, three-way match, payment, exception handling | The company's principal cash-outflow control chain | P1 | W3 | Procurement + Finance | `M16`, `M52` |
| SP-018 | `SP-018_SOP_Warehouse_Receipt_PutAway_and_Count.md` | Receiving, inspection, put-away, picking, cycle count, variance escalation | Stock accuracy underpins parts availability, which underpins first-time fix and turnaround time | P2 | W3 | Warehouse | `M41` |
| SP-019 | `SP-019_SOP_Cash_Collection_and_Banking.md` | Collection at branch and in field, custody, daily reconciliation, banking, shortfall handling | Cash across 51+ branches and 50–150 riders is the highest fraud-risk process in the business | P1 | W1 | Finance | `M20`, `M50` |
| SP-020 | `SP-020_SOP_Month_End_and_Year_End_Close.md` | Close calendar, cut-off rules, accrual and provision policy, reconciliation checklist, sign-off | Statutory reporting and audit readiness depend on a repeatable close; ad-hoc close is where restatements originate | P1 | W5 | Finance | `M19`, `M54` |
| SP-021 | `SP-021_SOP_Payroll_Run_and_Statutory_Filing.md` | Input cut-off, validation, approval, disbursement, statutory deduction, filing, exception handling | Payroll errors for 500+ employees are visible, urgent and legally consequential | P1 | W5 | HR + Finance | `M56` |
| SP-022 | `SP-022_SOP_Time_Attendance_and_Roster.md` | Roster publication, clock-in rules, geofence exceptions, overtime approval, leave interaction | Field technician attendance is geofenced (`P02`); exception handling must be defined before disputes arise | P2 | W2 | HR + Operations | `M55`, `P02` |
| SP-023 | `SP-023_SOP_Recruitment_and_Onboarding.md` | Requisition, sourcing, assessment, offer, joining, provisioning, induction, probation | Technician attrition and rapid network growth make onboarding a continuous, high-volume process | P2 | W5 | HR | `M58`, `M21` |
| SP-024 | `SP-024_SOP_Marketplace_Seller_Onboarding_and_Governance.md` | Verification, agreement, approval, monitoring, warning, suspension, removal | A seller cannot transact until documents are verified, the agreement is signed and admin approval is granted (`P07` governance requirements) | P2 | W7 | Marketplace Ops | `M12`, `P07` |
| SP-025 | `SP-025_SOP_TradeIn_Refurbishment_and_Resale.md` | Assessment, offer, acquisition, data erasure, refurbishment, grading, listing, sale, warranty | Combines a data-protection obligation with an inventory and consumer-sales process; neither can be improvised | P2 | W5 | Refurbishment | `M14`, `M06` |
| SP-026 | `SP-026_SOP_EWaste_Collection_and_Disposal.md` | Collection, segregation, hazardous handling, partner transfer, certification, material-recovery reporting | Environmental non-compliance is a regulatory and reputational risk that corporate clients audit | P2 | W5 | Sustainability | `M18` |
| SP-027 | `SP-027_SOP_Rental_and_Equipment_as_a_Service.md` | Availability, contracting, handover, in-life support, swap, recovery, damage assessment | Company assets in customer possession require an explicit recovery and damage process | P2 | W5 | Rental Operations | `M13` |
| SP-028 | `SP-028_SOP_Complaint_Escalation_and_Compensation.md` | Intake, classification, investigation, resolution authority, compensation limits, closure, learning loop | Complaint handling is the most reputationally sensitive process and the one most often improvised | P1 | W2 | Customer Experience | `M34`, `P10` |
| SP-029 | `SP-029_SOP_Internal_Quality_Audit_and_CAPA.md` | Audit programme, execution, finding classification, CAPA assignment, verification, closure | Finding-to-CAPA cycle-time target is under 5 days; ISO surveillance audits test this process directly | P1 | W5 | Quality | `M23`, `P11` |
| SP-030 | `SP-030_SOP_Health_Safety_and_Incident_Reporting.md` | Hazard reporting, incident response, investigation, RIDDOR-equivalent notification, corrective action | Field technicians work with electricity, refrigerants, batteries and vehicles. Safety process is a duty of care, not documentation | P1 | W5 | HSE | `M59` |
| SP-031 | `SP-031_SOP_IT_Service_Desk_and_Change_Management.md` | Internal ticket handling, priority, change request, CAB, release, rollback, emergency change | With 800+ internal users on a 67-module system, internal IT process failure stops the business | P2 | W5 | Internal IT | `M66` |
| SP-032 | `SP-032_Operational_Checklist_Library.md` | Branch opening and closing, shift handover, safety, 5S, cash count, equipment check, vehicle check | Checklists are the cheapest control available and the one auditors ask for first | P2 | W1 | Operations + Quality | `M04`, `P11` |
| SP-033 | `SP-033_Diagnostic_and_Triage_Decision_Tree_Library.md` | Structured decision trees by device family for intake triage, remote triage and bench diagnosis | Drives the guided diagnostic tree in `P02`, the AI triage in `M26`, and consistent fault coding by 200–400 technicians | P1 | W2 | Technical | `P02`, `M26`, `MD-024` |
| SP-034 | `SP-034_Call_and_Conversation_Script_Library.md` | Contact-centre scripts for enquiry, booking, status, complaint, retention, collection and escalation, bilingual | First-contact-resolution target is > 78% and average handling time is to fall 25%; scripts are the primary lever | P1 | W4 | Contact Centre | `P10`, `M27` |

---

### CATEGORY 07 — `KB` KNOWLEDGE BASE & TECHNICAL LIBRARY
**Folder:** `07_Knowledge_Base_and_Technical_Library/` · **16 files**

> `M61` gives the company a technical library; this category is what goes in it. It is also the
> offline knowledge pack that `P02` promises technicians in the field, and the grounding corpus
> the `M32` AI assistant answers from.

| ID | File | What it contains | Why it is needed | Pri | Wave | Owner | Traces to |
|---|---|---|---|:--:|:--:|---|---|
| KB-001 | `KB-001_Knowledge_Architecture_and_Tagging_Standard.md` | Taxonomy, tagging by device/fault/brand/skill-level, article types, findability rules, review cadence | An untagged knowledge base is unsearchable at scale and unusable as AI grounding | P1 | W2 | Knowledge Manager | `M61`, `M32` |
| KB-002 | `KB-002_Article_Template_and_Authoring_Standard.md` | Structure for procedure, reference, troubleshooting and bulletin article types; evidence and safety-warning rules | Knowledge authored by 80–150 senior technicians needs one shape to be reviewable and translatable | P2 | W2 | Knowledge Manager | `M61` |
| KB-003 | `KB-003_Repair_Manual_Index_and_Source_Register.md` | Index of OEM and third-party manuals held, licensing status, coverage gaps, access rules | Manuals carry copyright and brand-agreement constraints; an unmanaged library is a legal exposure | P2 | W2 | Knowledge Manager + Legal | `M61` |
| KB-004 | `KB-004_Troubleshooting_Guide_Set_IT_and_Computing.md` | Laptop, desktop, printer, server, storage and peripheral diagnostic and repair guidance | Largest service category by volume; consistency here drives first-time-fix rate | P2 | W2 | Technical | `M31`, `MD-021` |
| KB-005 | `KB-005_Troubleshooting_Guide_Set_Home_Appliance.md` | AC, refrigeration, laundry, cooking, water heating and display appliance guidance | Seasonal demand spikes are staffed by newly trained technicians who need reference, not tribal knowledge | P2 | W2 | Technical | `M31` |
| KB-006 | `KB-006_Troubleshooting_Guide_Set_Mobile_and_Tablet.md` | Board-level, display, battery, charging, water-damage and software-recovery guidance | High-value, high-risk repairs where the difference between L2 and L3 escalation is knowledge | P2 | W2 | Technical | `M31` |
| KB-007 | `KB-007_Troubleshooting_Guide_Set_Server_Network_and_CCTV.md` | Rack server, RAID/NAS, networking, UPS and surveillance system guidance | Corporate and MSP work; errors here take down a client's business, not one device | P2 | W4 | Technical | `M05`, `M31` |
| KB-008 | `KB-008_Fault_Code_Library_and_Interpretation_Guide.md` | Manufacturer fault codes mapped to the internal taxonomy in `MD-024`, with interpretation and next action | Bridges what the device reports to what the company records — without it, diagnostic data cannot be aggregated | P1 | W2 | Technical | `MD-024` |
| KB-009 | `KB-009_Parts_Compatibility_and_Substitution_Notes.md` | Cross-reference, approved substitutes, prohibited substitutions, quality tiers | Wrong-part fitting is a leading cause of rework and of brand-warranty claim rejection | P2 | W2 | Technical + Inventory | `MD-022` |
| KB-010 | `KB-010_Brand_Technical_Bulletin_and_Recall_Archive.md` | Received brand bulletins, technical notices and recall notifications, with acknowledgement and distribution record | `P08` allows brands to push bulletins and recalls; failing to act on a recall notice is a serious liability | P1 | W4 | Quality + Technical | `P08`, `M09` |
| KB-011 | `KB-011_Known_Issue_and_Workaround_Register.md` | Recurring defects by model, interim workarounds, permanent fix status, customer messaging | Prevents 200–400 technicians independently rediscovering the same fault, and gives the contact centre a consistent answer | P2 | W2 | Technical + Quality | `M23`, `M61` |
| KB-012 | `KB-012_Tool_Jig_and_Test_Equipment_Operating_Guides.md` | Operating, safety and calibration-check guidance for test and repair equipment | Misused test equipment produces false diagnoses and injures people | P3 | W5 | Technical + HSE | `MD-046`, `M45` |
| KB-013 | `KB-013_ESD_Chemical_and_Battery_Safety_Data.md` | Electrostatic discharge control, refrigerant handling, lithium battery storage, transport and incident response | Lithium and refrigerant handling carry statutory duties and genuine physical risk across 51+ sites | P1 | W5 | HSE | `M59`, `M18` |
| KB-014 | `KB-014_Repair_Time_Standards_and_Labour_Norms.md` | Standard times by repair type and device family, with basis and review cycle | Capacity planning, technician incentive schemes, job costing and quoted turnaround all read from these norms | P2 | W5 | Operations + Finance | `M54`, `M57` |
| KB-015 | `KB-015_Knowledge_Review_Currency_and_Retirement_Policy.md` | Review intervals, ownership, staleness flags, retirement, evidence of currency | Stale repair guidance is worse than none; it is confidently wrong and it is what the AI assistant will cite | P2 | W2 | Knowledge Manager | `M61`, `M32` |
| KB-016 | `KB-016_Technician_Field_Reference_Card_Set.md` | The offline-packaged quick-reference set shipped inside `P02`: safety, escalation, codes, common procedures | `P02` requires offline repair manuals and past repair notes; the offline pack must be curated, not the whole library | P2 | W2 | Technical + Content Design | `P02`, `PS-08` |

---

### CATEGORY 08 — `TR` TRAINING & ENABLEMENT
**Folder:** `08_Training_and_Enablement/` · **24 files**

> 800+ internal users, 38+ roles, 67 modules, 12 portals, 36 months, two languages. `P03`
> targets training-time-to-competence under four hours for a new agent. That target is a content
> deliverable, not a software feature.

#### 08A — Framework — `08A_Framework/`

| ID | File | What it contains | Why it is needed | Pri | Wave | Owner | Traces to |
|---|---|---|---|:--:|:--:|---|---|
| TR-001 | `TR-001_Training_Strategy_and_Competency_Framework.md` | Learning model, delivery mix, competency levels, assessment philosophy, refresh cadence, budget basis | Without a strategy, training becomes a pre-go-live scramble that the business absorbs as post-go-live error | P1 | W0 | Learning & Development | `M22` |
| TR-002 | `TR-002_Role_Based_Curriculum_Map.md` | Every registered role mapped to required courses, sequence, duration, prerequisite and certification | 38+ roles cannot each receive a bespoke plan invented at the time; the map is the plan | P1 | W1 | Learning & Development | `05-04`, `MD-009` |
| TR-003 | `TR-003_Course_Design_Standard_and_Storyboard_Template.md` | Learning-objective format, module length, interaction types, assessment design, bilingual scripting rules | Courses authored by different vendors and trainers must be interchangeable and maintainable | P2 | W1 | Learning & Development | `CG-008` |
| TR-004 | `TR-004_Assessment_and_Certification_Policy.md` | Pass marks, attempts, re-certification intervals, evidence, consequences of failure, appeal | Technician certification gates warranty work through a hard business rule; the policy must be defensible to brands and auditors | P1 | W2 | Quality + L&D | `M22`, `MD-011` |
| TR-005 | `TR-005_Question_Bank_Technician_Certification.md` | Item bank for L1/L2/L3 certification by device family, with difficulty calibration and rotation | Certification with a small static question set is certification in name only | P2 | W2 | Technical + L&D | `M22` |
| TR-006 | `TR-006_Question_Bank_Functional_Roles.md` | Item bank for agent, dispatcher, finance, inventory, HR, quality and administrator competency checks | Establishes that a user is competent before granting production access to a system that touches money | P2 | W2 | L&D | `M22` |

#### 08B — Course Packs — `08B_Course_Packs/`

> Each pack contains: facilitator guide, participant workbook, slide content, exercise data,
> job aid, assessment and a Bengali edition where the audience requires it.

| ID | File | Audience | Why it is needed | Pri | Wave | Owner | Traces to |
|---|---|---|---|:--:|:--:|---|---|
| TR-007 | `TR-007_Course_Pack_Service_Centre_Agent.md` | 150–250 agents | Largest single user population; the four-hour competence target applies to this role specifically | P1 | W1 | L&D | `P03`, `M04` |
| TR-008 | `TR-008_Course_Pack_Dispatch_Manager.md` | 3–8 dispatchers | Small population, disproportionate impact: dispatch decisions determine SLA attainment network-wide | P1 | W1 | L&D | `M02`, `P03` |
| TR-009 | `TR-009_Course_Pack_Field_Technician.md` | 200–400 technicians | Delivered in Bengali, on-device, to a workforce with mixed literacy and high turnover. Daily active usage target is > 95% | P0 | W2 | L&D | `P02`, `M22` |
| TR-010 | `TR-010_Course_Pack_Workshop_Supervisor.md` | 20–40 supervisors | Controls WIP, escalation and QC gating — the three levers of workshop margin | P1 | W1 | L&D | `M31` |
| TR-011 | `TR-011_Course_Pack_Branch_Manager.md` | 51+ managers | Accountable for cash, stock, staff, SLA and customer outcomes at their site; the broadest single curriculum | P1 | W1 | L&D | `M04`, `P03`, `P06` |
| TR-012 | `TR-012_Course_Pack_Inventory_and_Store_Keeper.md` | 51+ store keepers, 5–10 managers | Stock accuracy is a prerequisite for every downstream promise the company makes | P1 | W1 | L&D | `M15`, `M41` |
| TR-013 | `TR-013_Course_Pack_Procurement_Officer.md` | 4–8 officers | Small team operating the principal cash-outflow control with vendor-facing consequence | P2 | W3 | L&D | `M16`, `P05` |
| TR-014 | `TR-014_Course_Pack_Finance_Officer_and_Manager.md` | 12–24 finance staff | Statutory posting, VAT treatment and reconciliation errors are expensive and slow to detect | P1 | W1 | L&D + Finance | `M19`, `M20`, `M51` |
| TR-015 | `TR-015_Course_Pack_HR_and_Payroll.md` | HR team | Payroll and statutory filing errors affect every employee and carry legal consequence | P2 | W5 | L&D + HR | `M21`, `M56` |
| TR-016 | `TR-016_Course_Pack_Quality_and_Field_Auditor.md` | 20–60 auditors | Consistent finding classification across auditors is what makes audit data usable | P2 | W5 | L&D + Quality | `M23`, `P11` |
| TR-017 | `TR-017_Course_Pack_Contact_Centre_Agent.md` | 30–80 agents | Handles the unified queue across six channels with a screen-switch target below three per contact | P1 | W4 | L&D | `P10`, `M27` |
| TR-018 | `TR-018_Course_Pack_Account_and_Contract_Manager.md` | 11–26 managers | Owns contract value, renewal and corporate relationships — the highest-value customer segment | P2 | W2 | L&D | `M07`, `M08` |
| TR-019 | `TR-019_Course_Pack_Marketplace_and_Seller_Operations.md` | 4–10 officers | Governs an external workforce of 500–2,000 sellers under contractual standards | P2 | W7 | L&D | `M12`, `P07` |
| TR-020 | `TR-020_Course_Pack_Rider_and_Logistics.md` | 60–175 riders and coordinators | Custody, POD and cash handling by a mobile, high-turnover, Bengali-speaking workforce | P2 | W3 | L&D | `P09`, `M03` |
| TR-021 | `TR-021_Course_Pack_System_Administrator.md` | Internal IT | Administrators hold the most destructive permissions in the platform | P1 | W1 | L&D + Internal IT | `M30`, `M29` |
| TR-022 | `TR-022_Job_Aid_and_Quick_Reference_Library.md` | All roles | One-page task references for the twenty most frequent tasks per role. Learning decays; job aids at the point of work are what sustain competence after go-live | P1 | W1 | L&D | `TR-002` |
| TR-023 | `TR-023_Train_the_Trainer_and_Super_User_Kit.md` | Champions | A programme this size cannot be trained centrally; it is trained by a branch-level champion network | P2 | W1 | L&D | `CM-008` |
| TR-024 | `TR-024_Release_Training_and_Refresher_Standard.md` | All roles | Nine waves over 36 months means users are retrained repeatedly; the standard makes that repeatable and cheap | P2 | W2 | L&D | `06-01`, `OP-006` |

---

### CATEGORY 09 — `HC` HELP CENTRE & SELF-SERVICE
**Folder:** `09_Help_Centre_and_Self_Service/` · **20 files**

> `P01` targets more than 80% of status enquiries handled without a hotline call. That deflection
> is achieved by help content and a grounded AI assistant — not by the booking engine.

| ID | File | What it contains | Why it is needed | Pri | Wave | Owner | Traces to |
|---|---|---|---|:--:|:--:|---|---|
| HC-001 | `HC-001_Help_Centre_Information_Architecture.md` | Per-audience help structure, category tree, search behaviour, article-type taxonomy, cross-linking rules | Eleven audiences cannot share one help tree; nor can they each have an unplanned one | P1 | W2 | Content Design | `M61`, `P01` |
| HC-002 | `HC-002_Help_Article_Template_and_Style_Rules.md` | Task-article structure, screenshot rules, step numbering, prerequisite and outcome statements, bilingual pairing | Help written to no template cannot be maintained across nine waves of UI change | P2 | W2 | Content Design | `CG-003` |
| HC-003 | `HC-003_Help_Set_P01_Customer_Portal_and_App.md` | Booking, tracking, approving, paying, warranty, contracts, loyalty, shop, trade-in, recycling, complaints | The deflection engine for 250,000+ monthly customers; the single highest-ROI help set in the register | P1 | W2 | Content Design | `P01` |
| HC-004 | `HC-004_Help_Set_P02_Technician_App.md` | Job execution, parts, evidence, offline, sync, payments, safety, escalation | Delivered offline and in Bengali; a technician cannot browse a website mid-job | P1 | W2 | Content Design | `P02` |
| HC-005 | `HC-005_Help_Set_P03_Admin_Operations_Portal.md` | Fourteen workspaces, bulk actions, exception handling, permissions | 150–250 users doing varied work; help is the sustaining layer after the four-hour induction | P1 | W1 | Content Design | `P03` |
| HC-006 | `HC-006_Help_Set_P04_Corporate_B2B_Portal.md` | Estate management, bulk requests, approvals, SLA, billing, reporting, compliance downloads | Corporate admins are unpaid users of the company's system; friction here loses contracts | P2 | W4 | Content Design | `P04` |
| HC-007 | `HC-007_Help_Set_P05_Vendor_and_Supplier_Portal.md` | Onboarding, RFQ, PO, delivery, invoicing, returns, scorecard | Directly serves the 60% reduction target in vendor phone and email queries | P2 | W3 | Content Design | `P05` |
| HC-008 | `HC-008_Help_Set_P06_Analytics_and_Executive_Dashboard.md` | Metric definitions, drill paths, self-service analysis, subscriptions, row-level security | Self-service BI without definitional help produces confident misreporting to the board | P2 | W4 | Content Design + BI | `P06`, `RP-001` |
| HC-009 | `HC-009_Help_Set_P07_Marketplace_Seller_Portal.md` | Registration, listings, bidding, job execution, earnings, performance, disputes, boost | Seller onboarding completion target is > 60% of started registrations; help is the completion lever | P2 | W7 | Content Design | `P07` |
| HC-010 | `HC-010_Help_Set_P08_Brand_Partner_Portal.md` | Claim review, evidence, reconciliation, consignment, rate cards, performance, audits | Reduces claim decision time toward the sub-10-day target by removing process ambiguity | P2 | W4 | Content Design | `P08` |
| HC-011 | `HC-011_Help_Set_P09_Logistics_and_Rider_App.md` | Manifest, scanning, exceptions, POD, cash, offline | Riders need short, visual, Bengali guidance available without connectivity | P2 | W3 | Content Design | `P09` |
| HC-012 | `HC-012_Help_Set_P10_Contact_Centre_Console.md` | Queue, screen pop, actions, transfers, AI assist, wrap-up, quality | Agent help must be readable inside a live call, which constrains format severely | P2 | W4 | Content Design | `P10` |
| HC-013 | `HC-013_Help_Set_P11_Field_Auditor_App.md` | Audit programme, offline execution, findings, verification, reporting | Auditors work at branches with poor connectivity against clause-referenced checklists | P3 | W5 | Content Design | `P11` |
| HC-014 | `HC-014_Help_Set_P12_Partner_and_Referral_Portal.md` | Onboarding, referral links, lead tracking, earnings, co-marketing, reseller allocation | Partner adoption target is > 75% of approved partners; self-service is the only scalable support model | P3 | W7 | Content Design | `P12` |
| HC-015 | `HC-015_FAQ_Bank_by_Audience.md` | Curated question-and-answer sets per audience, sourced from real contact-centre and support volume | FAQs are the highest-traffic help asset and the primary AI-assistant training source | P1 | W2 | Content Design + CX | `M27`, `M32` |
| HC-016 | `HC-016_In_Product_Help_Tour_and_Coach_Mark_Copy.md` | First-run tours, contextual tips, coach marks, feature-announcement copy, dismissal rules | Help that requires leaving the task is help that is not read | P2 | W2 | Content Design | `UI-006` |
| HC-017 | `HC-017_Conversational_AI_Intent_and_Utterance_Library.md` | Intent taxonomy, training utterances in Bengali and English, entity slots, disambiguation prompts | `M32` cannot be trained or evaluated without a governed intent set; ad-hoc intents make regression testing impossible | P2 | W6 | Content Design + AI | `M32`, `P01` |
| HC-018 | `HC-018_Conversational_AI_Response_and_Fallback_Copy.md` | Response templates, grounding citations, clarification, fallback and no-answer copy, bilingual | An assistant that answers confidently from nothing is worse than one that hands over cleanly | P2 | W6 | Content Design + AI | `M32` |
| HC-019 | `HC-019_AI_Guardrail_Disclosure_and_Handover_Copy.md` | AI disclosure statements, refusal copy, out-of-scope handling, human-handover wording, data-use notice | Customers must know they are talking to a machine, and the assistant must not commit the company to prices, promises or legal positions | P1 | W6 | Legal + Content Design | `M32`, `LG-008` |
| HC-020 | `HC-020_Video_Tutorial_Script_Library.md` | Scripts for the short how-to videos embedded in help and used by the contact centre | Video is the most effective format for low-literacy and first-time users, and the most expensive to reshoot — scripts must be right first | P3 | W6 | Content Design | `MM-007` |

---

### CATEGORY 10 — `LG` LEGAL, POLICY & COMPLIANCE
**Folder:** `10_Legal_Policy_and_Compliance/` · **24 files**

> Twelve portals serving eleven distinct counterparty types, each needing its own binding terms.
> A data-protection regime the architecture already responds to (`05-06` NFR-086 mandates
> split residency with sensitive personal data held in Bangladesh). An ISO 9001:2015
> certification that is the company's principal differentiator. Every file here requires named
> legal sign-off under `CG-007`.

| ID | File | What it contains | Why it is needed | Pri | Wave | Owner | Traces to |
|---|---|---|---|:--:|:--:|---|---|
| LG-001 | `LG-001_Legal_Content_Register_and_Signoff_Log.md` | Every legally binding text, its version, effective date, approver, jurisdiction and acceptance-capture method | The company must be able to prove which terms a specific user accepted on a specific date. That is a register problem, not a document problem | P0 | W1 | Legal | `CG-007`, `M24` |
| LG-002 | `LG-002_Portal_Terms_of_Use_Customer.md` | Binding terms for `P01` account holders: eligibility, acceptable use, liability, suspension, governing law | 250,000+ monthly customers transacting without accepted terms is unmanaged liability | P0 | W2 | Legal | `P01` |
| LG-003 | `LG-003_Portal_Terms_of_Use_Corporate.md` | Terms for `P04` corporate users, distinct from the master service contract | Corporate portal users act under delegated authority; the portal terms and the contract must interlock without contradiction | P1 | W4 | Legal | `P04`, `M08` |
| LG-004 | `LG-004_Marketplace_Seller_Agreement_and_Policy_Handbook.md` | Seller contract, platform standards, commission, payout, holds, performance thresholds, suspension and removal | Automatic visibility reduction and suspension on performance failure (`P07` governance) is only enforceable if the agreement says so | P1 | W7 | Legal + Marketplace | `P07`, `M12` |
| LG-005 | `LG-005_Brand_Partner_Portal_Terms.md` | Access, confidentiality, data use, evidence handling and audit rights for brand partners | Brands receive customer and technician data through `P08`; the boundaries must be contractual | P2 | W4 | Legal | `P08` |
| LG-006 | `LG-006_Vendor_Portal_Terms_and_Supplier_Code_of_Conduct.md` | Portal terms plus ethical, labour, environmental and anti-bribery expectations of suppliers | Corporate and international brand clients increasingly audit their providers' supply chains | P2 | W3 | Legal + Procurement | `P05`, `M42` |
| LG-007 | `LG-007_Referral_and_Alliance_Partner_Agreement.md` | Referral terms, attribution rules, commission, marketing restrictions, termination | Attribution disputes are the normal failure mode of referral programmes; the rules must pre-date the first referral | P2 | W7 | Legal | `P12`, `M40` |
| LG-008 | `LG-008_Privacy_Notice_and_Consent_Copy.md` | What data is collected, purposes, lawful basis, retention, sharing, rights, contact — with the consent strings used in-product | The Bangladesh personal-data regime that drives the `05-06` NFR-086 residency requirement also drives notice and consent obligations. Notice text is operative legal content, not marketing copy | P0 | W2 | Legal + DPO | `05-06` NFR-086, `UI-042` |
| LG-009 | `LG-009_Data_Retention_and_Deletion_Schedule.md` | Retention period, legal basis and deletion method for every data class held | VAT records must be retained for at least five years; personal data must not be kept longer than its purpose requires. Both obligations meet in this one schedule | P0 | W2 | Legal + DPO | `M24`, `M51` |
| LG-010 | `LG-010_Data_Subject_Request_Handling_Content.md` | Request intake, identity verification, response templates, refusal grounds, timelines | A rights request arriving with no process becomes a regulatory incident within days | P1 | W2 | DPO | `M24`, `M33` |
| LG-011 | `LG-011_Cookie_and_Tracking_Policy.md` | Cookie inventory, purpose, duration, consent categories, banner and preference copy | Applies to all six web portals; an inaccurate cookie inventory is a common and easily-evidenced breach | P2 | W2 | Legal | `P01`, `P04` |
| LG-012 | `LG-012_Cross_Border_Data_Transfer_and_Residency_Statement.md` | Which data is Bangladesh-resident, which may leave, safeguards applied, sub-processor register | `05-06` NFR-086 replaced the single-region Singapore topology with split residency precisely because of this obligation. The statement is how it is demonstrated | P0 | W2 | Legal + DPO | `05-06` NFR-086, `02-05` |
| LG-013 | `LG-013_Service_Terms_Warranty_Terms_and_Exclusions.md` | Repair warranty scope, duration, exclusions, liability caps, data-loss disclaimers, unclaimed-device terms | The company's principal consumer-facing liability limit; must be presented at intake and reproduced on `DT-002` and `DT-032` | P0 | W1 | Legal | `M09`, `DT-002`, `DT-032` |
| LG-014 | `LG-014_Refund_Cancellation_and_Compensation_Policy.md` | Eligibility, timelines, method, deductions, goodwill limits and approval authority | Refund decisions are made daily by branch staff; without a policy they are made inconsistently and expensively | P1 | W2 | Legal + Finance | `M20`, `SP-028` |
| LG-015 | `LG-015_AMC_SLA_Master_Terms_and_Service_Credit_Rules.md` | Master service terms, SLA definitions, measurement, exclusions, service-credit calculation and cap | Service credits are a quantified liability that must reconcile exactly with `MD-028` and `DT-031` | P0 | W2 | Legal + Service Ops | `MD-028`, `DT-031`, `M08` |
| LG-016 | `LG-016_Managed_Services_and_Remote_Access_Consent_Terms.md` | Scope of remote access, consent capture, session recording, data handling, client responsibilities | Remote access to a client's estate without documented consent is both a legal and an insurance problem | P1 | W4 | Legal + MSP | `M05`, `SP-011` |
| LG-017 | `LG-017_Data_Recovery_and_Secure_Destruction_Terms.md` | Success-dependent fees, no-recovery outcomes, confidentiality, illegal-content handling, destruction standard | Data services involve discovering the customer's data; the terms must address confidentiality and unlawful content explicitly | P1 | W2 | Legal + Data Services | `M06`, `DT-034` |
| LG-018 | `LG-018_EWaste_EPR_and_Environmental_Compliance_Statements.md` | Regulatory position, producer-responsibility claims, disposal declarations, customer-facing environmental statements | Environmental claims are increasingly regulated; unsubstantiated recycling claims are a greenwashing exposure | P2 | W5 | Legal + Sustainability | `M18` |
| LG-019 | `LG-019_ESignature_Legal_Notice_and_Evidence_Statement.md` | What constitutes valid electronic consent, evidence retained, non-repudiation, dispute handling | E-signature is used for estimates, contracts, seller agreements and handovers. Its evidentiary basis must be stated once, authoritatively | P1 | W2 | Legal | `M24`, `UI-038` |
| LG-020 | `LG-020_Acceptable_Use_and_Internal_Access_Policy.md` | Internal system use, monitoring notice, prohibited actions, consequences | 800+ internal users with access to customer data need a stated boundary and a stated consequence | P1 | W1 | Legal + Security | `M29`, `M60` |
| LG-021 | `LG-021_ISMS_Policy_Set.md` | Information security policy suite: access, cryptography, supplier security, incident, continuity, classification | `05-06` sets security NFRs; the ISMS policy set is the human-facing counterpart and the artefact certification bodies audit | P1 | W2 | Security | `05-06`, `M29`, `M60` |
| LG-022 | `LG-022_Quality_Policy_and_ISO_9001_Statement_Set.md` | Quality policy, scope, objectives, process interaction, management-review commitments | The company's ISO 9001:2015 certification is its stated market differentiator; the policy set is inspected at every surveillance audit | P1 | W1 | Quality | `M23` |
| LG-023 | `LG-023_Anti_Bribery_Ethics_and_Whistleblowing_Content.md` | Ethical standards, gift and hospitality limits, conflict declaration, reporting channel, protection undertaking | Procurement, tendering and government contracting expose the company to bribery risk that must be visibly controlled | P2 | W3 | Legal + Governance | `M60`, `M16` |
| LG-024 | `LG-024_Regulatory_Disclosure_and_Statutory_Notice_Register.md` | The register of regulator-facing obligations and the notices, filings and disclosures each requires | Obligations to NBR, and to the sectoral and standards regulators relevant to the company's operations, are otherwise tracked in individuals' memory | P2 | W3 | Legal + Compliance | `M51`, `M60` |

---

### CATEGORY 11 — `BN` LOCALISATION & BILINGUAL CONTENT
**Folder:** `11_Localisation_Bengali/` · **18 files**

> `PS-03` requires Bengali and English throughout, with **Bengali default** on customer and
> field surfaces. `P01` requires professional translation, explicitly not machine translation.
> `P02` requires a complete Bengali interface *including error messages*. This category is how
> those three commitments are met and evidenced.

| ID | File | What it contains | Why it is needed | Pri | Wave | Owner | Traces to |
|---|---|---|---|:--:|:--:|---|---|
| BN-001 | `BN-001_Localisation_Strategy_and_Language_Coverage_Matrix.md` | Which surfaces, content types and audiences require which languages, and the default per surface | 452 content files with per-file language decisions made ad hoc will produce partial bilingualism, which is worse than none | P0 | W1 | Localisation Lead | `M65`, `PS-03` |
| BN-002 | `BN-002_Bengali_Translation_Standard.md` | Register (formal vs colloquial), technical-term policy, English-loanword rules, honorifics, sentence length | Bengali technical writing has genuine register choices; making them inconsistently makes the product feel foreign to its own users | P0 | W1 | Localisation Lead | `CG-010` |
| BN-003 | `BN-003_Bilingual_Terminology_Glossary.md` | The approved Bengali equivalent for every controlled term in `CG-004`, plus commercial and statutory vocabulary | Without a bound glossary, `fix.service.order` acquires five Bengali names across five portals | P0 | W1 | Localisation + Enterprise Architecture | `CG-004` |
| BN-004 | `BN-004_Do_Not_Translate_and_Transliteration_Register.md` | Brand names, product names, technical identifiers, statutory form names and person/place transliteration rules | "Mushak 6.3", "bKash" and model numbers must never be translated; customer names must be transliterated consistently for search to work | P1 | W1 | Localisation | `MD-006`, `MD-021` |
| BN-005 | `BN-005_i18n_Key_Placeholder_and_Pluralisation_Rules.md` | Placeholder syntax, ordering, gender and plural handling, string concatenation prohibition, context notes for translators | Concatenated strings are untranslatable into Bengali word order; the prohibition must reach developers before the first sprint | P0 | W1 | Localisation + Platform | `UI-001` |
| BN-006 | `BN-006_Bengali_Typography_Font_and_Numeral_Standard.md` | Approved fonts and fallbacks, conjunct rendering, minimum sizes, line height, Bengali versus Arabic numeral policy | Bengali conjuncts break at small sizes on low-end Android — the device class 200–400 technicians use daily | P0 | W1 | Localisation + Design | `VB-009`, `05-02` DM-09 |
| BN-007 | `BN-007_Date_Time_Number_Currency_and_Address_Formats.md` | `bn-BD` formatting rules, BDT presentation, lakh/crore grouping, Asia/Dhaka presentation of UTC-stored time | `05-02` DM-08 stores UTC and presents Asia/Dhaka. Number grouping in lakh and crore is expected by Bangladeshi users and absent from default locales | P0 | W1 | Localisation + Platform | `05-02` DM-08 |
| BN-008 | `BN-008_Translation_Memory_and_Term_Base_Management.md` | TM and term-base ownership, update cycle, vendor access, leverage measurement, quality thresholds | Nine waves of translation without a shared memory means paying repeatedly for the same strings and getting different answers | P1 | W1 | Localisation | `CG-006` |
| BN-009 | `BN-009_Bengali_String_Bundle_P01_Customer.md` | Full Bengali counterpart of `UI-011` plus customer-facing flow copy | Bengali is the default on `P01`; the English bundle is the exception, not the baseline | P0 | W2 | Localisation | `UI-011` |
| BN-010 | `BN-010_Bengali_String_Bundle_P02_Technician.md` | Full Bengali counterpart of `UI-012`, including every error and offline message | `P02` non-negotiable requirement #3: the Bengali interface must be complete, including error messages | P0 | W2 | Localisation | `UI-012`, `P02` |
| BN-011 | `BN-011_Bengali_String_Bundle_P03_Admin.md` | Bengali counterpart of `UI-013` and the fourteen workspace packs | Branch and back-office staff across 51+ sites are not uniformly comfortable working in English | P1 | W1 | Localisation | `UI-013`, `UI-023` … `UI-036` |
| BN-012 | `BN-012_Bengali_String_Bundle_P04_to_P06.md` | Bengali counterparts for corporate, vendor and analytics surfaces | Corporate users are more English-comfortable, but vendor and branch-manager users are not | P2 | W4 | Localisation | `UI-014` … `UI-016` |
| BN-013 | `BN-013_Bengali_String_Bundle_P07_to_P12.md` | Bengali counterparts for seller, brand, rider, contact-centre, auditor and partner surfaces | Riders and marketplace sellers are predominantly Bengali-first; brand partners are not — the bundle records which is which | P2 | W7 | Localisation | `UI-017` … `UI-022` |
| BN-014 | `BN-014_Bengali_Notification_and_SMS_Pack.md` | Bengali versions of all `NT` templates, with Unicode segment-count and cost analysis | Bengali SMS segments at 70 characters; a template that fits in English may cost three segments in Bengali | P0 | W2 | Localisation | `NT-004` … `NT-019` |
| BN-015 | `BN-015_Bengali_Document_and_Print_Template_Pack.md` | Bengali layouts for customer- and employee-facing `DT` documents, including statutory bilingual requirements | Intake receipts, estimates, warranties and payslips are read by people who will not read English | P1 | W2 | Localisation + Legal | `DT-002`, `DT-005`, `DT-041` |
| BN-016 | `BN-016_Bengali_Help_and_Training_Content_Plan.md` | Which help and training content is translated, which is authored natively in Bengali, and in what order | Field technician training (`TR-009`) must be Bengali-native, not translated, to be effective | P1 | W2 | Localisation + L&D | `TR-009`, `HC-004` |
| BN-017 | `BN-017_Bengali_Voice_IVR_and_Speech_Prompt_Pack.md` | Bengali IVR prompts, recording direction, pronunciation guidance, voice-note handling for `P02` | Hotline 16743 is answered in Bengali; `P02` captures technician voice notes in Bengali | P2 | W4 | Localisation + Contact Centre | `NT-019`, `P02` |
| BN-018 | `BN-018_Localisation_QA_and_Linguistic_Signoff_Checklist.md` | Linguistic review criteria, in-context review requirement, truncation and layout checks, sign-off record | Translation reviewed out of context passes review and fails in production; sign-off must be in-context and recorded | P1 | W2 | Localisation | `CG-008` |

---

### CATEGORY 12 — `DM` DATA MIGRATION CONTENT
**Folder:** `12_Data_Migration_Content/` · **14 files**

> `06-03_Data_Migration_Strategy.md` is listed as planned in the module repository and does not
> yet exist. This category is the content half of that gap: the mappings, rules, templates and
> reconciliations without which migration is an untestable one-way operation.

| ID | File | What it contains | Why it is needed | Pri | Wave | Owner | Traces to |
|---|---|---|---|:--:|:--:|---|---|
| DM-001 | `DM-001_Data_Migration_Strategy_and_Scope_Register.md` | What migrates, what is archived, what starts clean, cut-off dates, historical depth, rationale per decision | Migration scope decided late is migration scope decided expensively. This register is also the content counterpart of the planned `06-03` | P0 | W0 | Data Migration Lead | `06-03` (planned) |
| DM-002 | `DM-002_Legacy_Source_System_Inventory_and_Extract_Catalogue.md` | Every source system, owner, extract method, refresh window, known quality issues, access constraints | Sources discovered mid-migration are the most common cause of cutover slippage | P0 | W0 | Data Migration Lead | `01-05` (planned) |
| DM-003 | `DM-003_Entity_Migration_Priority_and_Sequencing_Plan.md` | Load order across all migrated entities with dependency graph and wave alignment | Foreign-key dependencies mean sequence is not a preference; loading in the wrong order simply fails | P0 | W1 | Data Migration Lead | `MD-048` |
| DM-004 | `DM-004_Field_Mapping_Workbook_Party_and_Customer.md` | Source-to-target field mapping, transformation rules, default values, unmapped-field disposition | Customer data is the most duplicated, least structured legacy data and the one users notice immediately | P0 | W1 | Data Migration + MDM | `M33`, `MD-013` |
| DM-005 | `DM-005_Field_Mapping_Workbook_Device_and_Asset.md` | Device, serial, IMEI, ownership, warranty status and service-history linkage mapping | Device identity is mandatory at intake; unmigrated device history destroys warranty and rework detection | P1 | W1 | Data Migration | `M17`, `MD-021` |
| DM-006 | `DM-006_Field_Mapping_Workbook_Service_History_and_Jobs.md` | Historical job mapping, status normalisation, fault and resolution code back-mapping, evidence handling | Service history drives repeat-fault detection, loyalty and customer trust in the new system on day one | P1 | W2 | Data Migration | `M01`, `MD-024` |
| DM-007 | `DM-007_Field_Mapping_Workbook_Inventory_and_Parts.md` | Part master, stock on hand by location, valuation basis, in-transit and reserved stock | Opening stock that does not reconcile to the general ledger blocks financial go-live | P1 | W1 | Data Migration + Inventory | `M15`, `M41` |
| DM-008 | `DM-008_Field_Mapping_Workbook_Finance_and_Open_Items.md` | Opening balances, open receivables and payables, ageing, unapplied receipts, tax history | Financial migration is the least forgiving: it must balance exactly and be auditable | P0 | W1 | Data Migration + Finance | `M19`, `M20` |
| DM-009 | `DM-009_Field_Mapping_Workbook_HR_and_Payroll.md` | Employee records, service dates, leave balances, YTD payroll, statutory histories | YTD payroll figures cannot be recomputed after the fact; migrating them wrongly misstates every employee's tax position | P1 | W5 | Data Migration + HR | `M21`, `M56` |
| DM-010 | `DM-010_Field_Mapping_Workbook_Contracts_Warranty_and_Claims.md` | Active contracts, entitlement consumption, covered assets, warranty registrations, in-flight claims | Contract-type and warranty-type orders are blocked by hard rules unless this data is correct and complete | P1 | W2 | Data Migration + Commercial | `M08`, `M09` |
| DM-011 | `DM-011_Data_Quality_Rules_Cleansing_and_Deduplication_Standard.md` | Validation rules, cleansing transformations, match and merge logic, survivorship, manual-review thresholds | Migrating dirty data into a system with hard business rules produces mass transaction failure on day one | P0 | W1 | Data Migration + MDM | `MD-013`, `M64` |
| DM-012 | `DM-012_Migration_Load_Template_Pack.md` | The machine-readable load templates with column definitions, types, required flags and examples | Business owners provide data; they can only do so against a template they understand | P1 | W1 | Data Migration | `MD-048` |
| DM-013 | `DM-013_Reconciliation_and_Validation_Report_Specification.md` | Row counts, control totals, balance reconciliation, exception categories, acceptance thresholds | Migration is not "done" when it loads; it is done when it reconciles and someone signs the reconciliation | P1 | W1 | Data Migration + Finance | `TS-018` |
| DM-014 | `DM-014_Cutover_Data_Checklist_and_Freeze_Communication.md` | Freeze windows, last-transaction rules, parallel-run instructions, branch communication, fallback trigger | Fifty-one branches must stop and start together; the communication is as important as the technical plan | P1 | W1 | Data Migration + Change | `CM-012`, `OP-002` |

---

### CATEGORY 13 — `TS` TEST & ACCEPTANCE CONTENT
**Folder:** `13_Test_and_Acceptance_Content/` · **18 files**

> Every module file ends with §15 Acceptance Criteria. This category turns 67 sets of acceptance
> criteria and 2,900+ requirements into scripts a business user can actually execute and sign.

| ID | File | What it contains | Why it is needed | Pri | Wave | Owner | Traces to |
|---|---|---|---|:--:|:--:|---|---|
| TS-001 | `TS-001_Test_Strategy_and_Content_Traceability_Standard.md` | Test levels, entry and exit criteria, requirement-to-script traceability rules, evidence retention | Content counterpart to the planned `06-04_Testing_and_Quality_Strategy.md`; without traceability, "tested" is an assertion | P1 | W1 | QA Lead | `06-04` (planned) |
| TS-002 | `TS-002_Test_Data_Pack_and_Persona_Set.md` | Realistic Bangladeshi names, addresses, phone numbers, BINs, device serials, and eleven audience personas, bilingual | Testing with `test1@test.com` never surfaces Bengali rendering, address-validation or name-matching defects | P0 | W1 | QA + Data Migration | `MD-006`, `BN-006` |
| TS-003 | `TS-003_SIT_Scenario_Library_Categories_A_to_D.md` | Integration scenarios across service delivery, customer engagement, commercial and circular-business modules | Category boundaries are where integration defects live; module-level testing cannot find them | P1 | W2 | QA | `03_Modules` A–D |
| TS-004 | `TS-004_SIT_Scenario_Library_Categories_E_to_G.md` | Integration scenarios across supply chain, asset and finance modules | Stock-to-ledger and procurement-to-payment chains fail silently unless tested end to end | P1 | W3 | QA | `03_Modules` E–G |
| TS-005 | `TS-005_SIT_Scenario_Library_Categories_H_to_K.md` | Integration scenarios across people, governance, analytics and platform modules | Identity, master data and event-platform defects surface as inexplicable failures elsewhere | P1 | W4 | QA | `03_Modules` H–K |
| TS-006 | `TS-006_UAT_Script_Pack_Service_Operations_Roles.md` | Step-by-step business scripts for agents, dispatchers, technicians, supervisors and branch managers | UAT signed by business users is the acceptance gate; scripts written by testers rather than in business language are signed without being read | P0 | W1 | Business Owners + QA | `05-04`, `TR-002` |
| TS-007 | `TS-007_UAT_Script_Pack_Commercial_and_Contract_Roles.md` | Scripts for account managers, warranty officers, pricing and marketplace operations | Commercial configuration errors are invisible in testing and expensive in production | P1 | W2 | Business Owners + QA | `M08`, `M09`, `M11` |
| TS-008 | `TS-008_UAT_Script_Pack_Supply_Chain_Roles.md` | Scripts for inventory, warehouse, procurement and logistics roles | Stock and custody errors compound daily until detected | P1 | W3 | Business Owners + QA | `M15`, `M16`, `M41` |
| TS-009 | `TS-009_UAT_Script_Pack_Finance_Roles.md` | Scripts for finance officers and managers, including statutory output verification | Mushak output correctness must be verified by finance, not inferred by developers | P0 | W1 | Finance + QA | `M19`, `M51`, `DT-010` |
| TS-010 | `TS-010_UAT_Script_Pack_People_and_Workforce_Roles.md` | Scripts for HR, payroll, learning and safety roles | Payroll correctness must be proven against parallel-run results before the first live run | P1 | W5 | HR + QA | `M56`, `M55` |
| TS-011 | `TS-011_UAT_Script_Pack_Customer_and_Partner_Portals.md` | Scripts executed as a customer, corporate admin, vendor, seller, brand and partner | External-facing defects are found by external users; the company must find them first | P1 | W2 | Business Owners + QA | `P01`, `P04`, `P05`, `P07`, `P08`, `P12` |
| TS-012 | `TS-012_End_to_End_Business_Scenario_Pack.md` | One end-to-end scenario per revenue stream, from demand through delivery to cash and reporting | The system exists to run fourteen revenue streams. Each must be demonstrated end to end before acceptance | P0 | W2 | Programme + QA | `README` §Fourteen Revenue Streams |
| TS-013 | `TS-013_Regression_Pack_and_Smoke_Test_Checklist.md` | The regression suite content and the post-deployment smoke checklist per portal | Nine waves of change into a live 67-module system without a regression pack guarantees reintroduced defects | P1 | W2 | QA | `06-01` |
| TS-014 | `TS-014_Performance_and_Load_Test_Scenario_Pack.md` | Scenarios and data volumes for each measurable NFR target | `05-06` sets specific numeric targets; each needs a defined scenario or the target is unverifiable | P1 | W2 | QA + Platform | `05-06` NFR-001…044 |
| TS-015 | `TS-015_Offline_and_Field_Condition_Test_Scripts.md` | 24-hour offline, degraded 3G, sync-conflict, battery-consumption and low-end-device scripts | `P02` non-negotiables include 24-hour offline with no data loss, sync within 30 seconds, and battery under 12% per shift. Each is a field test, not a lab test | P0 | W2 | QA + Mobile | `P02`, `P09`, `P11`, `05-06` NFR-036/037/047 |
| TS-016 | `TS-016_Accessibility_Test_Script_Pack.md` | WCAG 2.1 AA test procedures per portal, including Bengali screen-reader verification | `PS-04` is contractual; accessibility conformance claimed without test evidence is a claim, not a fact | P2 | W2 | QA + Content Design | `PS-04`, `CG-011` |
| TS-017 | `TS-017_Security_and_Privacy_Test_Case_Pack.md` | Access-control matrix verification, data-scope isolation, consent enforcement, residency verification, audit-log completeness | `05-04` defines data scope per role; unverified row-level security is the most damaging silent defect in a multi-tenant portal estate | P1 | W2 | Security + QA | `05-04`, `M29`, `LG-012` |
| TS-018 | `TS-018_Defect_Taxonomy_Triage_and_Signoff_Forms.md` | Severity and priority definitions, triage rules, deferral criteria, acceptance sign-off forms | Go-live decisions are made against open-defect profiles; without agreed severity definitions those decisions are arguments | P1 | W1 | QA + Programme | `06-02` |

---

### CATEGORY 14 — `RP` REPORTING, ANALYTICS & KPI CONTENT
**Folder:** `14_Reporting_Analytics_and_KPI/` · **16 files**

> `P06` commits management to making 100% of decisions on live data rather than compiled
> spreadsheets, and to cutting manual management reporting effort by 90%. Both promises are
> broken by ambiguous metric definitions, not by slow queries.

| ID | File | What it contains | Why it is needed | Pri | Wave | Owner | Traces to |
|---|---|---|---|:--:|:--:|---|---|
| RP-001 | `RP-001_KPI_Dictionary_and_Metric_Definition_Standard.md` | Every KPI: formula, numerator, denominator, inclusions, exclusions, grain, source, owner, baseline, target | Audit `00-07` H2-04 found 22 KPI identifiers used by two or more modules with different meanings. This dictionary is the resolution and the prevention | P0 | W1 | BI Lead + Enterprise Architecture | `00-07` H2-04, `06-02` |
| RP-002 | `RP-002_Report_Catalogue_by_Role_and_Module.md` | Every operational and management report, its audience, frequency, distribution and retention | 67 modules each specifying reports independently produces hundreds of near-duplicate reports nobody owns | P1 | W2 | BI Lead | `03_Modules` §12 |
| RP-003 | `RP-003_Dashboard_Specification_Pack_Executive.md` | `P06` executive dashboards: metric selection, layout, drill paths, commentary slots, mobile behaviour | Board-level performance across 14 revenue streams must be one agreed view, not per-director interpretations | P1 | W4 | BI Lead + Executive | `P06` |
| RP-004 | `RP-004_Dashboard_Specification_Pack_Operational_Consoles.md` | The opening dashboard for each of the fourteen `P03` workspaces plus the live operations board | Each console "opens on the work its role actually does" (`04-00` §P03). Deciding what that means is a content decision | P1 | W1 | BI Lead + Operations | `P03`, `P06` |
| RP-005 | `RP-005_Dashboard_Specification_Pack_External_Audiences.md` | Scoped analytics for corporate clients, brand partners, sellers and referral partners | External parties see their own data only; scope errors here are data breaches, not reporting defects | P2 | W4 | BI Lead + Security | `P04`, `P07`, `P08`, `P12` |
| RP-006 | `RP-006_BI_Semantic_Layer_Data_Dictionary.md` | Certified datasets, field descriptions, business meaning, joins, grain and row-level-security bindings | `P06` promises self-service analysis on certified datasets without SQL. Certification is a documentation act | P1 | W4 | BI Lead | `M62`, `P06` |
| RP-007 | `RP-007_Chart_Label_and_Visualisation_Standard.md` | Chart-type selection rules, axis and unit labelling, colour semantics, Bengali label handling, accessibility of charts | Inconsistent visual encoding across 51 branch league tables and a dozen dashboards produces misreading at management level | P2 | W4 | BI + Design System | `VB-008` |
| RP-008 | `RP-008_Report_Narrative_and_Commentary_Template_Set.md` | Structures for monthly operations, financial, quality and executive commentary | Numbers without narrative are re-interpreted by every reader; templates make commentary comparable month to month | P2 | W5 | Finance + Operations | `RP-010` |
| RP-009 | `RP-009_Statutory_and_Regulatory_Report_Format_Register.md` | Every externally mandated report, its format, deadline, submission route and owner | Statutory deadlines do not move; a missed format requirement is discovered at filing time | P1 | W3 | Finance + Compliance | `M51`, `LG-024` |
| RP-010 | `RP-010_Board_and_Management_Pack_Template.md` | The standing monthly and quarterly management pack contents and order | Management packs assembled ad hoc consume days of effort and vary in ways that hide trends | P2 | W5 | Finance | `06-02` |
| RP-011 | `RP-011_Branch_League_Table_Definition_and_Scoring_Rules.md` | Metrics, weightings, normalisation for branch size, exclusions, publication rules | `P06` ranks all 51+ branches. An unfair or opaque ranking is gamed within one quarter | P2 | W4 | Operations + BI | `P06` |
| RP-012 | `RP-012_Alert_Threshold_and_Anomaly_Rule_Register.md` | Thresholds, anomaly definitions, recipients, suppression and escalation for analytic alerts | `P06` promises threshold and anomaly alerts "to the right role"; the thresholds are business decisions, not defaults | P2 | W4 | BI + Operations | `P06`, `NT-021` |
| RP-013 | `RP-013_Scheduled_Report_and_Subscription_Catalogue.md` | Standing subscriptions, schedules, formats, recipients and review cadence | Unreviewed subscriptions accumulate until nobody reads them and the system spends its capacity generating them | P3 | W4 | BI Lead | `P06` |
| RP-014 | `RP-014_Export_Watermark_and_Confidentiality_Marking_Rules.md` | Classification marking, watermarking, export permission by role, redaction rules | Every dashboard export leaves the controlled environment; marking is the only remaining control | P2 | W4 | Security + BI | `05-02` §10, `M29` |
| RP-015 | `RP-015_Benefits_Realisation_and_KPI_Baseline_Register.md` | The pre-programme baseline for every target KPI, its measurement basis and evidence | `06-02` states targets against baselines. Audit `00-07` H2-10 already found an absolute KPI target with no baseline behind it | P1 | W0 | Programme + Finance | `06-02`, `00-07` H2-10 |
| RP-016 | `RP-016_Data_Quality_Scorecard_Definition.md` | Completeness, validity, uniqueness and timeliness measures per master-data domain, with thresholds | Master data degrades silently after migration; the scorecard is what makes degradation visible before it causes failure | P2 | W3 | MDM + BI | `M64`, `DM-011` |

---

### CATEGORY 15 — `AP` INTEGRATION & DEVELOPER CONTENT
**Folder:** `15_Integration_and_Developer_Content/` · **12 files**

> `05-03` catalogues 47 external integrations and requires OpenAPI 3.1 for REST and JSON Schema
> for events (`IP-08`). Specifications are machine-readable; the words that make them usable by
> a brand partner's or corporate client's development team are content.

| ID | File | What it contains | Why it is needed | Pri | Wave | Owner | Traces to |
|---|---|---|---|:--:|:--:|---|---|
| AP-001 | `AP-001_Developer_Portal_Information_Architecture.md` | Structure of the external developer surface: getting started, reference, guides, changelog, support | Partners integrating without a coherent developer surface generate integration support load the company cannot staff | P2 | W4 | Platform + Content Design | `M28` |
| AP-002 | `AP-002_API_Reference_Content_Standard.md` | Description conventions for endpoints, parameters, examples, error responses, pagination and idempotency notes | OpenAPI generated from code with no authored descriptions is technically complete and practically unusable | P1 | W3 | Platform | `05-03` IP-08 |
| AP-003 | `AP-003_Domain_Event_Catalogue_Descriptions.md` | Business meaning, emission conditions, ordering guarantees and consumer guidance for every domain event | `05-02` DM-15 writes every state change to an outbox. Consumers need to know what each event means, not just its shape | P1 | W3 | Platform + Enterprise Architecture | `05-02` DM-15, `05-03` |
| AP-004 | `AP-004_Webhook_and_Callback_Integration_Guide.md` | Subscription, delivery guarantees, retry, signature verification, replay and idempotency guidance | `IP-04` requires every integration to be idempotent; consumers must be told how to hold up their end | P2 | W3 | Platform | `05-03` IP-04 |
| AP-005 | `AP-005_Authentication_Scopes_and_Rate_Limit_Guide.md` | Credential issue, rotation, scope model, per-portal limits, throttling behaviour and remediation | `PS-02` routes all portal traffic through the gateway with per-portal credentials and limits. Undocumented limits are discovered under load | P1 | W3 | Platform + Security | `PS-02`, `M29` |
| AP-006 | `AP-006_Error_Code_Catalogue_and_Remediation_Copy.md` | Every API error code with cause, remedy and whether retry is appropriate | Integration partners escalate to the company for errors they could resolve themselves if the catalogue existed | P1 | W3 | Platform | `UI-004` |
| AP-007 | `AP-007_Partner_Integration_Guide_Brands.md` | How a brand partner integrates claims, rate cards, parts consignment and bulletins | Brand partners have their own warranty systems; the integration guide determines whether they use `P08` or email | P2 | W4 | Platform + Commercial | `P08`, `M09` |
| AP-008 | `AP-008_Partner_Integration_Guide_Corporate.md` | How a corporate client integrates their ITSM, asset or procurement system with 1000FiX | Enterprise clients increasingly require ticket and asset integration as a condition of contract | P2 | W4 | Platform + Account Management | `P04`, `M05` |
| AP-009 | `AP-009_Payment_Gateway_Integration_Runbook_Content.md` | Per-gateway behaviour, reconciliation, failure modes, refund and reversal handling, manual fallback | Nine payment integrations with a 99.95% availability target and multi-gateway failover need documented, drilled fallbacks | P1 | W3 | Platform + Finance | `05-03` §2.1, `05-06` NFR-048 |
| AP-010 | `AP-010_Sandbox_Onboarding_and_Test_Credential_Guide.md` | Sandbox access, test data, simulated events, limitations and promotion to production | Partners testing against production is how production incidents originate | P2 | W4 | Platform | `AP-001` |
| AP-011 | `AP-011_Integration_Change_Deprecation_and_Notice_Content.md` | Versioning policy, deprecation timelines, breaking-change notices, migration guides | `IP-08` requires versioned, documented external contracts; notice content is how versioning is honoured in practice | P2 | W4 | Platform | `05-03` IP-08 |
| AP-012 | `AP-012_Data_Sharing_and_Field_Level_Disclosure_Register.md` | Exactly which fields each external counterparty receives, and the lawful basis for each | `IP-10` minimises and logs data leaving the company. The register is what makes minimisation auditable | P1 | W3 | Security + Legal | `05-03` IP-10, `LG-012` |

---

### CATEGORY 16 — `CM` CHANGE MANAGEMENT & COMMUNICATIONS
**Folder:** `16_Change_Management_and_Comms/` · **18 files**

> A 36-month, nine-wave programme replacing how 500+ employees, 51+ branches and every external
> counterparty works. `06-05_Change_Management_and_Training_Plan.md` is listed as planned in the
> module repository; this category is the content it will call for.

| ID | File | What it contains | Why it is needed | Pri | Wave | Owner | Traces to |
|---|---|---|---|:--:|:--:|---|---|
| CM-001 | `CM-001_Programme_Narrative_and_Change_Story.md` | Why the programme exists, what changes, what does not, what it means for each audience | Nine waves of change with no consistent story becomes nine unrelated disruptions in staff perception | P1 | W0 | Change Lead | `00-02` |
| CM-002 | `CM-002_Stakeholder_Map_and_Communication_Plan.md` | Every internal and external stakeholder group, influence, concerns, channel, frequency and owner | Communication planned per wave rather than per stakeholder leaves groups repeatedly surprised | P1 | W0 | Change Lead | `00-04` |
| CM-003 | `CM-003_Communication_Calendar_by_Wave.md` | Message calendar across W1–W9 with dependency on delivery milestones | Communications that arrive after the change are damage control, not change management | P2 | W0 | Change Lead | `06-01` |
| CM-004 | `CM-004_Executive_Briefing_and_Steering_Pack_Template.md` | Standing steering-committee pack: status, decisions required, risks, benefits tracking | The charter awaits Steering Committee approval; the committee needs a consistent decision surface | P2 | W0 | Programme Office | `00-02`, `00-04` |
| CM-005 | `CM-005_Wave_Launch_Communication_Kit.md` | Reusable kit: announcement, what changes, what to do, where to get help, in both languages | Nine launches need one repeatable kit, not nine improvised ones | P1 | W1 | Change Lead | `06-01` |
| CM-006 | `CM-006_Go_Live_Announcement_Pack.md` | Internal and external go-live messaging, including customer-facing notice of new portals | Customers discovering a new portal without notice generates hotline volume at the worst possible moment | P1 | W1 | Change + Marketing | `P01` |
| CM-007 | `CM-007_Hypercare_Communication_Pack.md` | How to get help during hypercare, known issues, expected disruption, escalation route | Hypercare succeeds or fails on whether users know where to go in the first 48 hours | P1 | W1 | Change + Support | `OP-002` |
| CM-008 | `CM-008_Champion_and_Super_User_Network_Kit.md` | Champion role definition, selection, briefing cadence, escalation route, recognition | 51+ branches cannot be supported centrally; the champion network is the delivery mechanism for adoption | P2 | W1 | Change Lead | `TR-023` |
| CM-009 | `CM-009_Internal_Newsletter_and_Update_Template.md` | Regular programme update format for the wider workforce | Silence between waves is filled with rumour; a predictable cadence prevents it | P3 | W1 | Change Lead | `CM-003` |
| CM-010 | `CM-010_Town_Hall_and_Roadshow_Content.md` | Presentation content for divisional and branch roadshows, adapted per audience | Field and branch staff will not read documents; they attend briefings | P2 | W1 | Change Lead | `CM-002` |
| CM-011 | `CM-011_Resistance_Objection_and_FAQ_Handling_Pack.md` | The real objections — job security, monitoring, workload, incentive impact — and honest responses | Unaddressed objections become quiet non-adoption, which is far harder to detect and reverse | P2 | W1 | Change + HR | `CM-002` |
| CM-012 | `CM-012_Branch_Readiness_Communication_Checklist.md` | What each branch must confirm before cutover: data, devices, connectivity, training, champion | Fifty-one branches going live in waves need a single readiness definition, not fifty-one interpretations | P1 | W1 | Change + Operations | `DM-014` |
| CM-013 | `CM-013_Customer_Migration_and_Transition_Pack.md` | Customer-facing communications for account migration, new portal, changed references and processes | Existing customers with legacy reference numbers must be transitioned without losing their service history in their own eyes | P1 | W2 | Marketing + Change | `P01`, `DM-004` |
| CM-014 | `CM-014_Corporate_Client_Transition_Pack.md` | Account-manager-led transition materials for contracted corporate clients | Corporate clients have contractual expectations; unmanaged transition risks renewal | P2 | W4 | Account Management | `P04` |
| CM-015 | `CM-015_Vendor_and_Seller_Transition_Pack.md` | Onboarding communications for vendors and sellers moving to portal-based interaction | Vendor portal adoption targets above 85% require active transition, not passive availability | P2 | W3 | Procurement + Marketplace | `P05`, `P07` |
| CM-016 | `CM-016_Adoption_Campaign_Content.md` | Campaigns driving portal uptake against the stated adoption targets per portal | `P01` targets 88% online booking and `P04` targets 85% active corporate clients. Adoption is marketed, not assumed | P2 | W2 | Marketing + Change | `04-00` KPIs |
| CM-017 | `CM-017_Recognition_Incentive_and_Gamification_Copy.md` | Copy for adoption recognition, leaderboards, milestones and incentive announcements | Behaviour change in a 500-person workforce responds to recognition more reliably than to mandate | P3 | W2 | Change + HR | `M57` |
| CM-018 | `CM-018_Change_Impact_Statement_Template.md` | Per-role statement of what changes, what stops, what starts, and what support is available | 38+ roles each need to see their own change, not the programme's | P2 | W1 | Change Lead | `05-04`, `TR-002` |

---

### CATEGORY 17 — `OP` OPERATIONS, SUPPORT & RUNBOOKS
**Folder:** `17_Operations_Support_and_Runbooks/` · **16 files**

> `06-06_Deployment_and_Operations_Plan.md` is listed as planned. This category is the operational
> content that plan will depend on — written before go-live, because the first incident will not
> wait for it.

| ID | File | What it contains | Why it is needed | Pri | Wave | Owner | Traces to |
|---|---|---|---|:--:|:--:|---|---|
| OP-001 | `OP-001_Support_Model_Tiering_and_Routing_Content.md` | Support tiers, scope per tier, routing rules, response commitments, out-of-hours cover | 800+ internal users and eleven external audiences need one stated route to help | P0 | W1 | Support Lead | `M66` |
| OP-002 | `OP-002_Hypercare_Plan_and_Exit_Criteria.md` | Hypercare duration, staffing, floor-walking, triage cadence, exit criteria per wave | Hypercare that ends by exhaustion rather than by criteria leaves unresolved adoption problems | P0 | W1 | Support + Programme | `06-06` (planned) |
| OP-003 | `OP-003_Service_Desk_Macro_and_Canned_Response_Library.md` | Canned responses for the most frequent internal and external support requests, bilingual | Consistency and speed in support responses; also the raw material for later self-service content | P1 | W1 | Support Lead | `M66`, `HC-015` |
| OP-004 | `OP-004_Incident_Communication_Template_Set.md` | Sev1–Sev4 notification, update cadence, resolution and post-incident messaging, internal and customer versions | During an outage there is no time to compose. Templates are written when calm | P1 | W1 | Support + Comms | `OP-016` |
| OP-005 | `OP-005_Status_Page_and_Maintenance_Notice_Copy.md` | Status page component names, incident states and planned-maintenance notices | `NFR-049` constrains planned maintenance to defined windows; customers and branches must be told in advance, consistently | P2 | W2 | Support | `05-06` NFR-049 |
| OP-006 | `OP-006_Release_Notes_Standard_and_Wave_Note_Set.md` | Release note structure, audience segmentation, and the note set per wave | Nine waves of change into a live system; users who cannot see what changed assume the system broke | P1 | W1 | Programme + Content Design | `06-01`, `TR-024` |
| OP-007 | `OP-007_Runbook_Core_ERP_Platform.md` | Start, stop, scale, backup, restore, job monitoring, common failure modes for the Odoo core | Restoring service without a runbook depends on one person being reachable | P1 | W1 | Platform Engineering | `02-05` |
| OP-008 | `OP-008_Runbook_Integration_and_Event_Platform.md` | Gateway, broker, outbox, replay, dead-letter, backlog and circuit-breaker procedures | `IP-05` and `IP-06` require safe failure and observability; the procedures make that operational | P1 | W3 | Platform Engineering | `M28`, `05-03` |
| OP-009 | `OP-009_Runbook_Identity_and_Access.md` | Identity provider operations, session policy, MFA reset, lockout, break-glass and audit procedures | Identity failure locks out every portal simultaneously; break-glass must be pre-authorised and documented | P0 | W1 | Security | `M29`, `PS-01` |
| OP-010 | `OP-010_Runbook_Data_Platform_and_Warehouse.md` | Pipeline monitoring, reload, backfill, schema change and certification procedures | Silent pipeline failure produces confidently wrong dashboards, which is worse than an outage | P2 | W4 | Data Engineering | `M62` |
| OP-011 | `OP-011_Runbook_Portal_and_Mobile_App_Operations.md` | Release channels, staged rollout, forced-upgrade policy, store submission, rollback | A bad forced upgrade can take 200–400 technicians offline mid-shift | P1 | W2 | Mobile Engineering | `P01`, `P02`, `P09` |
| OP-012 | `OP-012_Disaster_Recovery_and_Continuity_Playbook.md` | Failover decision authority, procedures, communication, data-loss assessment, return to normal | `NFR-007` sets RPO of 15 minutes and RTO of 2 hours. Those are only achievable with a rehearsed playbook | P0 | W2 | Platform + Risk | `05-06` NFR-007 |
| OP-013 | `OP-013_On_Call_Escalation_and_Handover_Content.md` | Rotas, escalation ladder, handover format, severity definitions, authority to act | Escalation ambiguity at 02:00 is the difference between a 20-minute and a 4-hour incident | P1 | W1 | Platform Engineering | `SP-005` |
| OP-014 | `OP-014_Manual_Fallback_Procedure_Set.md` | The paper or degraded-mode procedure for every P0 integration and for total system unavailability | `IP-09` requires a defined manual fallback for every P0 integration. 51+ branches must be able to keep trading | P0 | W1 | Operations + Platform | `05-03` IP-09 |
| OP-015 | `OP-015_Access_Request_and_Joiner_Mover_Leaver_Content.md` | Request forms, approval routing, standard access profiles per role, revocation on exit | High technician turnover with unrevoked access is the most common insider-risk finding in service businesses | P1 | W1 | Security + HR | `M29`, `MD-009` |
| OP-016 | `OP-016_Post_Incident_Review_Template_and_Register.md` | Blameless review structure, timeline, contributing factors, actions, and the register of reviews | Incidents that are not reviewed recur; reviews that are not registered are not actioned | P2 | W2 | Support + Quality | `M23` |

---

### CATEGORY 18 — `EO` ECOSYSTEM ONBOARDING CONTENT
**Folder:** `18_Ecosystem_Onboarding_Content/` · **14 files**

> Six external populations are onboarded through six portals: sellers, brands, vendors, corporate
> clients, referral partners and franchisees. Each has a documented adoption target. Each target
> is met or missed principally on the quality of its onboarding content.

| ID | File | What it contains | Why it is needed | Pri | Wave | Owner | Traces to |
|---|---|---|---|:--:|:--:|---|---|
| EO-001 | `EO-001_Marketplace_Seller_Onboarding_Kit.md` | Registration walkthrough, document requirements, verification expectations, first-listing and first-job guidance | Seller onboarding completion target is > 60% of started registrations. Drop-off in registration is a content problem before it is a product problem | P1 | W7 | Marketplace Ops | `P07`, `M12` |
| EO-002 | `EO-002_Seller_Standards_Scoring_and_Sanctions_Handbook.md` | Quality and evidence standards, scorecard mechanics, thresholds, visibility reduction, suspension | Marketplace job standards are identical to owned jobs (`P07` governance). Sellers must be told precisely what that means | P2 | W7 | Marketplace Ops + Quality | `P07`, `M23` |
| EO-003 | `EO-003_Brand_Partner_Onboarding_Pack.md` | Portal access, claim workflow, evidence expectations, reconciliation cycle, escalation contacts | Moving 17+ brands from email to portal claims (target > 80%) requires a guided transition per brand | P2 | W4 | Commercial | `P08`, `M09` |
| EO-004 | `EO-004_Brand_Claim_Rules_and_Evidence_Standard_Guide.md` | Per-brand claim rules, required evidence, common rejection reasons and how to avoid them | Claim approval-rate target is > 92%; most rejections are evidence defects that a standard guide prevents | P1 | W4 | Warranty | `M09`, `DT-033` |
| EO-005 | `EO-005_Vendor_and_Supplier_Onboarding_Pack.md` | Registration, document submission, catalogue and banking setup, RFQ and PO workflow orientation | Vendor portal targets (> 90% PO acknowledgement, > 85% portal invoicing) require active onboarding of every supplier | P2 | W3 | Procurement | `P05`, `M42` |
| EO-006 | `EO-006_Supplier_Performance_Scorecard_Explanation.md` | How on-time delivery, quality and responsiveness are measured, and how a supplier improves a score | A scorecard a supplier does not understand is a scorecard they dispute rather than respond to | P3 | W3 | Procurement | `M42`, `P05` |
| EO-007 | `EO-007_Corporate_Client_Onboarding_and_Welcome_Kit.md` | Account setup, estate upload, user and approval configuration, service catalogue, escalation contacts | Corporate portal adoption target is > 85% of contracted clients; onboarding quality determines it | P1 | W4 | Account Management | `P04`, `M08` |
| EO-008 | `EO-008_Corporate_Admin_Setup_and_Delegation_Guide.md` | Multi-user, multi-site, multi-level approval configuration for the client's own administrator | Corporate admins configure their own delegation chains; errors here produce approval deadlocks the company gets blamed for | P2 | W4 | Account Management | `P04`, `MD-015` |
| EO-009 | `EO-009_Referral_and_Alliance_Partner_Kit.md` | Enrolment, referral link mechanics, lead submission, attribution rules, commission and payout | Referral-attributed customers are targeted at > 12% of new customers; partners must understand attribution to trust it | P2 | W7 | Partnerships | `P12`, `M40` |
| EO-010 | `EO-010_Franchise_and_Channel_Partner_Pack.md` | Franchise model, standards, brand use, systems access, reporting and audit obligations | `M40` extends the network through franchise and channel partners operating under the 1000FiX name | P3 | W8 | Commercial | `M40` |
| EO-011 | `EO-011_Rate_Card_and_Pricing_Communication_Pack.md` | How pricing and rate-card changes are communicated to sellers, vendors, brands and corporate clients | Price changes communicated inconsistently across four ecosystems generate simultaneous disputes | P2 | W4 | Commercial | `MD-029`, `M11` |
| EO-012 | `EO-012_Co_Marketing_and_Co_Branding_Asset_Guide.md` | Approved logos, claims, templates and approval route for partner co-marketing | Partners will use the 1000FiX name; the only choice is whether they do it correctly | P3 | W7 | Brand + Partnerships | `P12`, `M40` |
| EO-013 | `EO-013_Ecosystem_Dispute_Resolution_Content.md` | Dispute intake, evidence, timelines, decision authority and appeal, for sellers, vendors and partners | Payouts are held while a dispute is open (`P07`); the process must be fast, documented and even-handed | P2 | W7 | Marketplace + Legal | `P07`, `LG-004` |
| EO-014 | `EO-014_Ecosystem_Offboarding_and_Exit_Content.md` | Termination notice, final settlement, data handling, listing removal and reinstatement terms | Exit is the point at which ecosystem relationships become legal disputes; the content must pre-exist the exit | P2 | W8 | Legal + Marketplace | `LG-004`, `LG-007` |

---

### CATEGORY 19 — `MM` MULTIMEDIA & ASSET SPECIFICATIONS
**Folder:** `19_Multimedia_and_Asset_Specs/` · **12 files**

> Specifications, not the assets themselves. These briefs are what design, video and photography
> suppliers are commissioned against, and what their output is accepted against.

| ID | File | What it contains | Why it is needed | Pri | Wave | Owner | Traces to |
|---|---|---|---|:--:|:--:|---|---|
| MM-001 | `MM-001_Multimedia_Asset_Standard_and_Delivery_Specification.md` | Formats, resolutions, colour, compression, naming, metadata and delivery requirements for all asset types | Assets delivered to no standard are re-commissioned; the cost falls on the programme, not the supplier | P2 | W1 | Brand | `VB-003` |
| MM-002 | `MM-002_Screenshot_Annotation_and_Redaction_Standard.md` | Capture resolution, chrome, sample-data rules, annotation style, personal-data redaction | Hundreds of screenshots across help and training will show real data unless the standard forbids it | P1 | W1 | Content Design + Security | `HC-002`, `TR-003` |
| MM-003 | `MM-003_Diagram_and_Process_Map_Visual_Standard.md` | Notation, shape and colour semantics, labelling, export formats, accessibility of diagrams | Process maps and architecture diagrams authored inconsistently cannot be compared or maintained | P2 | W1 | Business Process + Design | `SP-003` |
| MM-004 | `MM-004_Icon_Set_Requirements.md` | Icon inventory across all portals, style, grid, states, Bengali-label pairing, accessibility | Twelve portals on one component library need one icon set with agreed meanings | P2 | W1 | Design System | `VB-007` |
| MM-005 | `MM-005_Illustration_and_Empty_State_Artwork_Brief.md` | Illustration style, cultural appropriateness for Bangladesh, empty-state artwork inventory | Empty states are the most-seen screens at every wave launch; generic stock illustration undermines credibility | P3 | W2 | Design System | `UI-006` |
| MM-006 | `MM-006_Video_Production_Brief_Training_Series.md` | Format, duration, language, on-screen text, accessibility, recording conditions for training video | Video training for 200–400 technicians must be Bengali, short, and viewable on a mid-range phone over 3G | P2 | W2 | L&D + Brand | `TR-009` |
| MM-007 | `MM-007_Video_Production_Brief_Customer_How_To_Series.md` | Format and content brief for customer-facing how-to video used in help and the contact centre | Video deflects support contacts from customers who will not read a help article | P3 | W6 | Content Design | `HC-020` |
| MM-008 | `MM-008_Animated_Explainer_Brief_Portal_Onboarding.md` | Brief for short onboarding animations per external portal | First-run explanation is the highest-leverage moment for adoption in every external portal | P3 | W6 | Content Design + Brand | `HC-016` |
| MM-009 | `MM-009_Photography_Brief_Branches_Workshop_and_Field.md` | Shot list, consent requirements, safety, brand compliance, usage rights | Real photography of real branches and technicians is a trust asset; it is also a consent and safety obligation | P3 | W4 | Brand + HR | `LG-008` |
| MM-010 | `MM-010_PDF_and_Print_Template_Design_Specification.md` | Design specification implementing `DT-001` and `VB-004` for the print engine | The design intent must reach the rendering engine as a specification, not as a reference PDF | P2 | W1 | Brand + Platform | `DT-001`, `VB-004` |
| MM-011 | `MM-011_Email_and_HTML_Asset_Specification.md` | Email-safe markup, image dimensions, dark-mode assets, Bengali font strategy, size limits | Email rendering is the least forgiving surface and the one most often tested last | P2 | W2 | Brand + Platform | `VB-005` |
| MM-012 | `MM-012_Digital_Asset_Management_and_Naming_Standard.md` | Asset repository structure, naming, versioning, rights metadata, retention and retirement | Thousands of assets across nine waves become unfindable within a year without a naming and rights standard | P2 | W1 | Brand | `CG-005` |

---

### CATEGORY 99 — `RF` REFERENCE & REGISTERS
**Folder:** `99_Reference_and_Registers/` · **12 files**

> The connective tissue. These files are what make the other 440 auditable rather than merely
> present.

| ID | File | What it contains | Why it is needed | Pri | Wave | Owner | Traces to |
|---|---|---|---|:--:|:--:|---|---|
| RF-001 | `RF-001_ERP_Glossary_and_Acronym_Register.md` | Every term, acronym and identifier prefix used across the programme, in English and Bengali | The module repository lists `99-01_Glossary_and_Acronyms.md` as planned and not yet written. New joiners, vendors and auditors all need it | P1 | W0 | Enterprise Architecture | `99-01` (planned), `CG-004` |
| RF-002 | `RF-002_Source_Document_and_Evidence_Index.md` | Every business plan, SOW, company profile, contract and regulation the content set draws on, with location and date | `CG-012` requires claims to name a primary source; this is where sources are registered once | P1 | W0 | Programme Content Lead | `99-04` (planned), `CG-012` |
| RF-003 | `RF-003_Content_to_Requirement_Traceability_Matrix.md` | Every content file mapped to the `FR-` requirements and acceptance criteria it serves | `CP-04` makes traceability a rule; this matrix is where content without a requirement, and requirements without content, become visible | P0 | W1 | Programme Content Lead + QA | `05-01`, `CP-04` |
| RF-004 | `RF-004_Content_to_Module_Coverage_Map.md` | All 67 modules mapped to the content files they require, with gaps highlighted | Answers "is M43 ready to build?" as a content question, not only an engineering one | P1 | W1 | Programme Content Lead | `02-02` |
| RF-005 | `RF-005_Content_to_Portal_Coverage_Map.md` | All 12 portals mapped to their UI, help, notification, legal and training content | A portal cannot go live with 90% of its content; this map is the go-live gate | P1 | W1 | Programme Content Lead | `04-00` |
| RF-006 | `RF-006_Content_Decision_Log_and_Change_Control.md` | Every content decision, its rationale, date, decision-maker and consequences | `00-05_Decision_Log_and_Change_Control.md` is missing from the module repository (audit finding **AF-04**). Content will not repeat that omission | P1 | W0 | Programme Content Lead | `00-05` (missing), `CG-006` |
| RF-007 | `RF-007_Content_Backlog_and_Prioritisation_Register.md` | Requested but unscheduled content, with sizing, requester, justification and priority | New content demand arrives continuously across 36 months; without a backlog it is either absorbed silently or refused arbitrarily | P2 | W1 | Programme Content Lead | `06-01` |
| RF-008 | `RF-008_External_Standards_and_Regulatory_Reference_Register.md` | The external standards and regulations the content set must conform to, with version and verification date | Statutory and standards references go stale; audit `00-07` H2-13 already flagged tax figures resting on press reporting | P2 | W1 | Compliance | `00-07` H2-13, `LG-024` |
| RF-009 | `RF-009_Sample_and_Reference_Data_Pack.md` | Worked examples: a completed job card, a compliant Mushak 6.3, a filled audit report, a sample payout statement | Worked examples resolve ambiguity that prose specifications cannot; they are also the fastest onboarding tool for a new vendor | P2 | W1 | Programme Content Lead | `DT-*`, `TS-002` |
| RF-010 | `RF-010_Content_Ownership_and_Contact_Directory.md` | Named owner and deputy per content file or family, with review dates | Ownership stated only in a table column decays; a directory with review dates is what survives staff change over 36 months | P2 | W0 | Programme Content Lead | `CG-002` |
| RF-011 | `RF-011_Content_Risk_Register.md` | Content-specific risks: translation capacity, legal review bottleneck, master-data readiness, SME availability | Content risk is not represented in `00-04`, yet master-data readiness is a credible cause of wave slippage | P2 | W0 | Programme Content Lead | `00-04` |
| RF-012 | `RF-012_Content_Audit_Report_Archive_Index.md` | Index of all content audits performed, findings, status and remediation evidence | `CP-11` requires counted verification; the archive is how repeated audits become a trend rather than isolated events | P3 | W1 | Programme Content Lead | `_AUDIT/` |

---

## 5. Cross-Reference: Content Coverage by Portal

| Portal | UI copy | Help | Notifications | Legal | Training | Onboarding | Total direct |
|---|---|---|---|---|---|---|---:|
| **P01** Customer | `UI-011`, `BN-009` | `HC-003` | `NT-004`, `NT-009`, `NT-015` | `LG-002`, `LG-008`, `LG-013` | — | `CM-013` | 11 |
| **P02** Technician | `UI-012`, `BN-010` | `HC-004`, `KB-016` | `NT-005`, `NT-016` | `LG-020` | `TR-009` | — | 8 |
| **P03** Admin | `UI-013`, `UI-023`…`UI-036`, `BN-011` | `HC-005` | `NT-022` | `LG-020` | `TR-007`, `TR-008`, `TR-010`…`TR-014`, `TR-021` | — | 27 |
| **P04** Corporate | `UI-014`, `BN-012` | `HC-006` | `NT-010` | `LG-003`, `LG-016` | — | `EO-007`, `EO-008`, `CM-014` | 9 |
| **P05** Vendor | `UI-015`, `BN-012` | `HC-007` | `NT-011` | `LG-006` | `TR-013` | `EO-005`, `EO-006` | 8 |
| **P06** Analytics | `UI-016`, `BN-012` | `HC-008` | `NT-021` | `LG-020` | — | — | 5 |
| **P07** Seller | `UI-017`, `BN-013` | `HC-009` | `NT-012` | `LG-004` | `TR-019` | `EO-001`, `EO-002`, `EO-013` | 9 |
| **P08** Brand | `UI-018`, `BN-013` | `HC-010` | `NT-013` | `LG-005` | — | `EO-003`, `EO-004` | 7 |
| **P09** Rider | `UI-019`, `BN-013` | `HC-011` | `NT-017` | `LG-020` | `TR-020` | — | 6 |
| **P10** Contact Centre | `UI-020`, `BN-013` | `HC-012` | `NT-019` | `LG-020` | `TR-017` | — | 6 |
| **P11** Auditor | `UI-021`, `BN-013` | `HC-013` | `NT-020` | `LG-022` | `TR-016` | — | 6 |
| **P12** Partner | `UI-022`, `BN-013` | `HC-014` | `NT-012` | `LG-007` | — | `EO-009`, `EO-012` | 7 |

> Cross-cutting content (`CG`, `VB`, `MD`, `SP`, `DT`, `RP`, `TS`, `OP`, `RF`) serves all twelve
> and is not repeated per portal — principle `CP-01`.

---

## 6. Production Roadmap

| Phase | Window | Content produced | Gate |
|---|---|---|---|
| **Phase 0 — Foundations** | Months 0–3 (W0) | All 14 `CG`, 6 `VB` foundations, `MD-001`, `SP-001`…`SP-006`, `DM-001`, `DM-002`, `RF-001`, `RF-002`, `RF-006`, `RF-010`, `RF-011`, `RP-015`, `CM-001`…`CM-004`, `TR-001` | Content operating model approved by Steering Committee |
| **Phase 1 — Configuration content** | Months 2–8 (W1) | All 48 `MD` files, `DM-003`…`DM-014`, `DT-001`…`DT-016`, `DT-021`…`DT-029`, `MD` load workbooks, `UI-001`…`UI-010`, `UI-013`, `UI-023`…`UI-036` | No W1 configuration begins on unapproved master data |
| **Phase 2 — Launch content** | Months 6–14 (W2) | `UI-011`, `UI-012`, `BN-009`…`BN-011`, `NT` customer and technician sets, `HC-003`…`HC-005`, `LG-002`, `LG-008`, `LG-013`, `TR-007`…`TR-012`, `TS-002`, `TS-006`, `TS-012`, `OP-001`…`OP-004`, `CM-005`…`CM-013` | No portal goes live below 100% of its `P0` and `P1` content |
| **Phase 3 — Ecosystem content** | Months 14–23 (W3–W4) | Vendor, corporate, brand and contact-centre content; `RP` dashboards; `AP` developer content; `EO` onboarding kits | External audiences onboarded only against completed kits |
| **Phase 4 — Depth content** | Months 23–30 (W5–W6) | Quality, HR, finance depth; `KB` library; AI assistant content; multimedia | ISO surveillance readiness confirmed |
| **Phase 5 — Marketplace & scale** | Months 30–36 (W7–W9) | `P07`/`P12` content, `LG-004`, `LG-007`, franchise and scale content, optimisation | Marketplace opens only on completed seller agreement and standards |

---

## 7. Content Effort Estimate

Stated as a **range with an explicit basis**, per audit rule RG-05 (estimates must not be used
for contractual commitment until measured). These are **estimates, not counted figures.**

| Category | Files | Est. person-days | Basis |
|---|---:|---:|---|
| `CG` Governance | 14 | 55–75 | Policy documents, 4–5 days each including review |
| `VB` Voice & brand | 10 | 40–55 | Design-adjacent, requires workshops |
| `MD` Master data | 48 | 320–480 | Data gathering dominates; several files are multi-week (`MD-021`, `MD-022`, `MD-035`) |
| `UI` UI copy | 42 | 210–300 | Per-screen inventory plus review cycles |
| `NT` Notifications | 26 | 90–130 | Template libraries with legal and cost review |
| `DT` Documents | 44 | 200–290 | Statutory templates require external verification |
| `SP` Process & SOP | 34 | 190–270 | Requires SME workshops across 51+ branches |
| `KB` Knowledge | 16 | 130–210 | Technical authoring by scarce senior technicians |
| `TR` Training | 24 | 220–330 | Course development is the most effort-intensive content type |
| `HC` Help centre | 20 | 130–190 | Article volume is high within each set |
| `LG` Legal | 24 | 110–170 | Drafting is fast; external legal review is the constraint |
| `BN` Localisation | 18 | 180–280 | Volume-driven; scales with `UI`, `NT`, `DT` output |
| `DM` Data migration | 14 | 90–140 | Mapping workbooks require source-system access |
| `TS` Test content | 18 | 150–220 | Script volume tracks requirement count (2,900+) |
| `RP` Reporting | 16 | 80–120 | Definitional work with heavy stakeholder alignment |
| `AP` Integration | 12 | 55–85 | Engineering-authored, content-reviewed |
| `CM` Change & comms | 18 | 90–140 | Recurring production across nine waves |
| `OP` Operations | 16 | 85–130 | Runbooks require operational rehearsal |
| `EO` Ecosystem | 14 | 70–105 | Per-audience kits with commercial review |
| `MM` Multimedia specs | 12 | 45–70 | Specification only; production cost is separate |
| `RF` Reference | 12 | 55–85 | Registers require continuous maintenance, not one-off writing |
| **Total** | **452** | **2,595–3,875 person-days** | **≈ 520–775 person-weeks** |

**Read this against the programme's own numbers.** The measured build effort in `README.md` is
1,513 person-weeks across 65 counted module specifications. A content estimate of 520–775 PW is
roughly **34–51% of measured build effort** — which is consistent with published experience on
ERP programmes, where content, training, data and change routinely consume a third to a half of
total programme effort. It is also the portion most often omitted from the business case.

> **This estimate is not in the approved business case.** Audit `00-07` H2-08 already escalated
> a 1,513 PW versus 834 PW variance (decision D-14). The content estimate above compounds that
> variance and must be raised at the same Steering Committee item, not separately. See audit
> finding **AF-09**.

---

## 8. Mandatory Audit — Summary of Findings

A mandatory audit was run over the whole workspace as a condition of issuing this register.
It examined 1,009 files across four project areas against the repository's own governance rules.

**Result: 18 findings — 4 critical, 6 high, 5 medium, 3 low.** Nine were remediated during the
audit; nine require decisions the Content Lead cannot take alone.

The full report, with evidence and remediation instructions for every finding, is
[`_AUDIT/AUDIT-001_Content_and_Repository_Integrity_Audit.md`](_AUDIT/AUDIT-001_Content_and_Repository_Integrity_Audit.md).

| ID | Sev | Finding | Status |
|---|:--:|---|:--:|
| AF-01 | **CRITICAL** | The twelve portal specifications are filed in `03_Modules/K_Platform_and_Technology/`, not in `04_Portals_and_Applications/` as the approved structure requires | **Open — CTO decision** |
| AF-02 | **CRITICAL** | `README.md` and `FOLDER_STRUCTURE.md` state contradictory completeness figures on the same date: 76% (93 of 123) versus 28% (35 of 123) | **Fixed** |
| AF-03 | **CRITICAL** | `README.md` states `M66` and `M67` are unwritten; both exist and are complete (86 KB and 82 KB) | **Fixed** |
| AF-04 | **CRITICAL** | `00-05_Decision_Log_and_Change_Control.md` does not exist, while two audits record decisions (D-14) as though it does | **Open — must be created** |
| AF-05 | High | `README.md` §Status claims the benchmark study and gap analysis are "Complete"; `01_Research_and_Benchmarking/` contains zero files | **Fixed** |
| AF-06 | High | `05-01` is titled "~2,352 Functional Requirements"; `README.md` states 2,930 counted | **Open — restate 05-01** |
| AF-07 | High | `05-02` is titled "225 Entities Across 30 Modules" and `05-04` "38 Roles Across 30 Modules"; the architecture has 67 modules | **Open — restate 05-02, 05-04** |
| AF-08 | High | `02-05` restates effort as ~1,302 PW; `README.md` states 1,513 PW counted | **Open — reconcile** |
| AF-09 | High | Content effort of 520–775 PW is absent from the business case, compounding the open D-14 variance | **Escalated** |
| AF-10 | High | `project_content/` contained no content and one empty stray folder copied from the website project | **Fixed** — one residual empty directory locked by another process; delete manually |
| AF-11 | Medium | The website content index uses a `P1`–`P4` priority scale; the ERP register uses `P0`–`P3`. Cross-reading them silently misranks work | **Documented** |
| AF-12 | Medium | Website content folders use spaces and ampersands (`BLOG & EDUCATIONAL`), which break tooling paths | **Documented — not repeated here** |
| AF-13 | Medium | `FOLDER_STRUCTURE.md` names three portal and module files that differ from the files on disk | **Fixed** |
| AF-14 | Medium | Four module files reference portal specifications by their misfiled `03_Modules/` path | **Open — depends on AF-01** |
| AF-15 | Medium | `99_Reference/` contains only `_Superseded/`; all four planned reference documents are absent | **Open** |
| AF-16 | Low | The website content index claims "427 files, 0 new" while 431 markdown files exist on disk | **Documented** |
| AF-17 | Low | Two `_CATEGORY_OVERVIEW.md` conventions coexist with category audit reports in the same folders | **Accepted** |
| AF-18 | Low | `M26` is named `M26_AIML_...` on disk and `M26_AI_ML_...` in the folder map | **Fixed** |

**The three findings that most affect this register:**

1. **AF-04** — content decisions will accumulate from month zero. `RF-006` exists in this
   register specifically so that content does not repeat the module repository's missing
   decision log.
2. **AF-09** — the content effort in §7 is real work that no one has yet budgeted. Raising it
   late is how content quality gets sacrificed at wave boundaries.
3. **AF-01** — until the portal specifications sit where the structure says they sit, `RF-005`
   (portal content coverage) cannot be maintained mechanically.

---

## 9. Maintenance Rules

| Rule | Detail |
|---|---|
| **CM-R1** | A new content file requires an entry in this register *before* the file is created. Register-first, always — this is `RG-01` from the module repository applied to content. |
| **CM-R2** | Completion figures in §1 are regenerated by enumerating the filesystem, never by projection (`CP-11`, `RG-06`). |
| **CM-R3** | A content file is never edited to carry content that belongs to another file; the owning file is updated and referenced instead (`CP-01`). |
| **CM-R4** | Renaming a content file updates the file name and every reference, but never the ID (`CP-02`). |
| **CM-R5** | Superseded content moves to `_ARCHIVE/` with a `SUPERSEDED_` prefix and a header note; it is not deleted (`CP-10`). |
| **CM-R6** | A bilingual file is not `Approved` until the Bengali counterpart has passed in-context linguistic sign-off (`BN-018`). |
| **CM-R7** | A statutory or legal file is not `Approved` without a recorded named sign-off (`CG-007`, `LG-001`). |
| **CM-R8** | Every claim of fact carries a source and a verification date (`CG-012`). |
| **CM-R9** | This register is audited at every wave boundary; findings are recorded in `_AUDIT/` and indexed in `RF-012`. |
| **CM-R10** | Changes to the folder structure in §3 require CTO approval, mirroring `FOLDER_STRUCTURE.md` §8. |

---

## 10. Reading Paths

| If you are… | Read in this order |
|---|---|
| **The CTO or Programme Director** | §1 statistics → §7 effort → §8 audit → `_AUDIT/AUDIT-001` in full |
| **The Content Lead** | §2 principles → §3 tree → §4 in full → §9 maintenance rules |
| **A module business owner** | §4, your module's category rows → `RF-004` coverage map → your `SP` SOP → your `TR` course pack |
| **A portal owner** | §5 portal coverage table → your `UI`, `HC`, `NT`, `LG` rows → `RF-005` |
| **The MDM or data lead** | Category 02 in full → `MD-048` load index → Category 12 (`DM`) |
| **Finance or tax** | `MD-035`, `MD-037`, `MD-040` → `DT-010`…`DT-020` → `RP-009` → `LG-009` |
| **Legal counsel** | Category 10 in full → `CG-007` → `LG-001` sign-off log |
| **The localisation lead** | `CG-010` → Category 11 in full → the bilingual flags across Categories 03, 04, 05 |
| **An implementation vendor** | §0 → §2 → §3 → §4 → §6 roadmap → `RF-003` traceability |
| **A new joiner** | §0 → `RF-001` glossary → §3 tree → the category you will work in |

---

## 11. Relationship to the Corporate Website Content Set

The corporate website programme maintains a separate, complete content set of 427 registered
files (431 on disk) at
`1000_fix_corporate_website/1000 fix/1000 fix corporate website/project_content/`.

**The two sets are deliberately separate and must not be merged.** They differ in audience,
lifecycle, priority scale and governance.

| | Website content set | ERP content set (this register) |
|---|---|---|
| Purpose | Acquire and inform the market | Operate the business |
| Audience | Prospects, search engines, the public | Employees, customers under service, partners, regulators |
| Priority scale | `P1`–`P4` | `P0`–`P3` (`README.md` convention) |
| Lifecycle | Continuous marketing cadence | Wave-gated, 36-month programme |
| Approval | Digital Strategy | CTO, Legal, Finance, Quality by content class |
| Statutory exposure | Low, except legal pages | High — 61 files carry statutory or legal consequence |

**Four defined interfaces exist between them**, and each is owned on the ERP side:

| Interface | Website side | ERP side | Rule |
|---|---|---|---|
| Booking entry point | Website service and city pages | `UI-037` booking flow copy | Website may describe; only `UI-037` defines the transactional wording |
| Service catalogue | Website service pages | `MD-019` catalogue seed | `MD-019` is authoritative for what is sellable; the website reflects it |
| Pricing statements | Website pricing content | `MD-029` rate cards | Published price ranges must be reconciled to `MD-029` at each change |
| Legal terms | Website legal pages | Category 10 | Where both publish the same terms, the ERP version governs and the website links to it |

Audit finding **AF-11** applies to anyone reading both registers: the priority letters look
identical and mean different things.

---

## 12. Status

| Item | State |
|---|---|
| Content taxonomy and folder structure | **Defined** — 21 categories, 452 files |
| Content register | **This document, v1.0 — DRAFT FOR APPROVAL** |
| Content files written | **452 of 452 (100%)** — counted, not estimated (`CP-11`). *Enumerated **2026-08-18** (`AUDIT-020` §2). All 21 categories written. **Written is not approved — 0 of 452 are `Approved`.** Superseded figures: 428 at 2026-08-17 16:49 UTC; 427 at 2026-08-17 16:45 UTC — both floors taken while authoring was in flight (proposed rule `RG-08`)* |
| **Content files approved** | **0 of 452.** 32 Class A/B files await unwaivable gate `G6`; 266 await a Bengali counterpart under `CM-R6`; the Programme Content Lead who is final approver of all 12 Class E `RF` files and 85 further Class E files **is unappointed** (`RF-010`, `RF-011` `CR-01`) |
| Category 00 `CG` — Content Governance & Standards | **Complete — 14 of 14 written, all at `Draft`** |
| Category 01 `VB` — Voice, Brand & Design-System Content | **Complete — 10 of 10 written, all at `Draft`** |
| Category 02 `MD` — Master Data & Configuration Seed Content | **Complete — 48 of 48 written, all at `Draft`** |
| Category 03 `UI` — UI Copy & Microcopy | **Complete — 42 of 42 written, all at `Draft`** |
| Category 04 `NT` — Notification & Messaging Content | **Complete — 26 of 26 written, all at `Draft`** |
| Category 05 `DT` — Document, Print & Statutory Output Templates | **Complete — 44 of 44 written, all at `Draft`** — audited, `AUDIT-007`. **None can reach `Approved`:** 26 await gate G6 external verification, 34 await a Bengali counterpart |
| Category 06 `SP` — Process, SOP & Workflow Content | **Complete — 34 of 34 written, all at `Draft`** — audited, `AUDIT-006` |
| Category 07 `KB` — Knowledge Base & Technical Library | **Complete as specified — 16 of 16 written, all at `Draft`** — audited, `AUDIT-008`. **Every file is a specification for content that does not exist:** 160 articles, 22 tool guides and 48 reference cards are enumerated and unwritten, estimated at **775–1,545 specialist hours, unresourced** (`AUDIT-008` R-07). Three files are scheduled after the waves that cite them (`AUDIT-008` KB-04, KB-07, KB-08) |
| Category 08 `TR` — Training & Enablement | **Complete as specified — 24 of 24 written, all at `Draft`** — audited, `AUDIT-009`. **CRITICAL: the Layer 1 statutory induction curriculum for 800+ employees has no owning file** — `TR-025` must be registered, taking this category to 25 files and the total to 453 (finding TR-01). Four roles carry declared interim routes; three roles are unregistered in `MD-009` |
| Category 09 `HC` — Help Centre & Self-Service | **Complete as specified — 20 of 20 written, all at `Draft`** — audited, `AUDIT-010`. **CRITICAL: transcript-derived work at W2 has no confirmed basis under the Personal Data Protection Act 2026** (finding HC-01). Two further wave-sequencing errors; the register-wide sequencing basis is now questioned (`AUDIT-010` §7) |
| Category 10 `LG` — Legal, Policy & Compliance | **Complete — 24 of 24 written, all at `Draft`** — audited, `AUDIT-013`. **None can reach `Approved`:** all 24 await gate G5 legal review, **6 await G6 external statutory verification which `WV-02` makes unwaivable**, and 16 await a Bengali counterpart. **CRITICAL: audit check F3 fails today** — `DT-031` maps nine `MD-028` fields that do not exist, and `MD-028` has no clock start/stop event field at all (finding LG-01). **Four upstream decisions block the category**: the split-residency legal opinion (`D-13`), the marketplace principal-or-agent determination (`D-03`), the e-waste regulated-entity question, and the limitation period more than twenty `DT` retention rows depend on |
| Category 11 `BN` — Localisation & Bilingual Content | **Complete — 18 of 18 written, all at `Draft`** — audited, `AUDIT-012`. **CRITICAL: the `common.*` namespace — 154 shared strings loading on every portal — has no registered Bengali owner**, so `P02`'s non-negotiable Bengali-completeness commitment is unmet at a counted 44% (finding BN-01). `BN-019` must be registered, taking this category to 19 files. Two further wave inversions; the `UI` packs are representative rather than complete, leaving 289 Bengali strings with no English source row (BN-18). **`BN-003` clears the `T-07` block that has held `CG-004` since 2026-08-15** |
| Category 12 `DM` — Data Migration Content | **Complete — 14 of 14 written, all at `Draft`** — audited, `AUDIT-011`. **CRITICAL: `06-03_Data_Migration_Strategy.md` does not exist**, so migration tooling, staging architecture and rollback mechanics have no owning specification (finding DM-01). **Two migration domains have no workbook** — `M24` documents (500,000+ records) and `M37`/`M11` catalogue and pricing (finding DM-02). All 48 registered legacy sources are unprofiled, which blocks every load |
| Category 13 `TS` — Test & Acceptance Content | **Complete — 18 of 18 written, all at `Draft`** — audited, `AUDIT-014`. **CRITICAL: the category cannot report what it exists to report** — requirement-to-script coverage has **three current denominators** (2,930 / ~2,352 / 3,343), so `G4-10` is unanswerable and no percentage may be quoted (finding TS-01, closes `AF-06`). **Nine of eighteen files are consumed a wave before they exist**, seven of them at `G1` — the fourth consecutive category and the twentieth instance of the same sequencing defect (TS-02). **Three packs cannot be executed at all**: `TS-017` has no role accounts, `TS-015` no field logistics, `TS-008` no stock or hardware, `TS-016` no reviewer — leaving `G1` and `G2` unevidenceable for resourcing rather than content reasons. **`AUDIT-011` is cited in four places and does not exist** (TS-03) |
| Category 14 `RP` — Reporting, Analytics & KPI Content | **Complete — 16 of 16 written, all at `Draft`** — audited, `AUDIT-015`. **CRITICAL: the KPI identifier space is 250 in use against 95 registered** — 196 unregistered, 41 unused, and `00-07` H2-04's "22 collisions" re-diagnosed as an exhausted register with only two genuine defects (finding RP-01). **CRITICAL: 44 of 95 KPI baselines are absent**, and `06-02` §6 states a KPI without a baseline cannot claim a benefit — roughly **BDT 396 lac of the 876 lac base case** rests on improvement benefits whose baselines are weak or absent (RP-02). **1,063 reports are specified across 79 specifications** and no document had ever counted them (RP-03). Five more wave inversions, taking the register-wide total to **31 across five categories** (RP-05) |
| Category 15 `AP` — Integration & Developer Content | **Complete — 12 of 12 written, all at `Draft`** — audited, `AUDIT-016`. **CRITICAL: 21 event names are consumed by `05-03` §3.3, `P04` §12.3 and `P08` §12.3 and do not exist in the `05-03` §4.2 inventory** — 5 are the same fact under two names, 2 are undeclared projections, and **14 are genuinely missing**, including `claim.evidence_incomplete` (the control that suppresses incomplete claim submission), `recall.execution_updated` (product safety) and `credit_note.issued` (the SLA remedy `P04` `AC-10` publishes) (AP-01). **CRITICAL: `05-06` uses `NFR-090`, `NFR-091` and `NFR-092` for two different requirements each** — §6.3 PDPA 2026 and §7 maintainability — so an instruction to satisfy `NFR-092` resolves either to distributed tracing or to a statutory transparency notice, and `NFR-088`/`NFR-089` are additionally duplicated as stray rows in §6.4 (AP-02). **Eight of twelve files are consumed a wave before they exist and six are needed at W1**, taking the register-wide wave-inversion total to **39 across six categories**. **Three W1 platform decisions are unmade** — no webhook signature scheme exists anywhere (AP-04), no scope vocabulary exists so every credential is scoped by the issuer’s judgement (AP-05), and the `API-04` error envelope diverges from RFC 9457 with no ruling. **Three payment availability commitments do not reconcile** (AP-06). **The Class `B` disclosure register cannot be completed**: 38 of 53 counterparties are `Undetermined`, the three W3 courier integrations carrying customer name, phone and address among them, and no DPIA, processor-contract inventory or DPO exists (AP-08) |
| Category 16 `CM` — Change Management & Communications | **Complete — 18 of 18 written, all at `Draft`** *(enumerated 2026-08-20)* — audited, `AUDIT-019`. **CRITICAL: the category was authored against this table while it was stale**, asserting 24 times that Categories 14, 15, 17 and 18 held zero files when 58 were on disk; all 24 corrected during the audit, and rule `R-01` proposed so it does not recur (finding CM-01). **Three findings are for the Steering Committee, not the content function**: two wave calendars are current and `OP-002` §4.3 has taken the other side (CM-03); the `CM-017` register row commissions a **leaderboard that `M57` `BRU-PIC-16` prohibits as a Class `H` block with no waiver route** (CM-05); and `CM-017` delivers the named mitigation for **`RSK-008`, a Critical risk arriving at W2, three waves late at W5** (CM-06) — the twenty-first instance of the wave-sequencing defect and the first to strand a Critical-risk mitigation. **`CM-018` alone derives 95–140 person-days against a §7 allocation of 90–140 for all eighteen files** (CM-07). Zero of twelve bilingual files have a Bengali counterpart, and `CM-007`'s nightly bulletin cadence is unachievable within the stated translation lead time (CM-11) |
| Category 18 `EO` — Ecosystem Onboarding Content | **Complete — 14 of 14 written, all at `Draft`** — audited, `AUDIT-018`. **CRITICAL: the marketplace may not be able to pay its participants lawfully** — a configurable payout hold, an unbounded dispute block and an unbounded appeal are set against the Digital Commerce Operation Guidelines 2021's **ten-day settlement obligation** and **72-hour complaint obligation**, and the Consumers' Right Protection Act 2009 §60's **30-day** consumer window; **no stage SLA exists anywhere, no 72-hour path exists, and no compliance officer is named in any programme document**, while all four external facts rest on secondary sources (EO-01). **`05-05` carries no business rule for `M40` or `M42`** — 40 rules governing partners, franchisees, resellers and the whole supply base — **and its `BRU-ECM` family duplicates six of `M12`'s `BRU-MKP` rules under different identifiers, two under a different owner**, including the hard block on a seller transacting (EO-02). **The Master Index's own §1 wave windows disagree with `06-01` §3 and `02-02` in all nine rows**, by two to six months, while stating they are taken from `06-01` — never audited in seventeen prior reports (EO-04). Six more wave inversions, taking the register-wide total to **45 across seven categories**, with **`EO-014` exit content registered up to twenty-two months after the first exit it governs becomes possible** (EO-03). **`SP-024` names `LG-018` — the e-waste statement — as the Marketplace Seller Agreement in five places** (EO-08) |
| Category 17 `OP` — Operations, Support & Runbooks | **Complete — 16 of 16 written, all at `Draft`** — audited, `AUDIT-017`. **CRITICAL: the lawful DR path for Bangladesh-resident personal data does not exist** — `NFR-086` requires a resident store, no resident DR target is provisioned, and the only remaining route is a cross-border transfer that `NFR-086b` makes a regulatory act requiring Authority notification *before* execution (OP-01). **The `dr` environment itself is named in `02-05` §9 and sized nowhere**, with no out-of-account immutable backup and no separate-domain WAL archiving, so `NFR-007` (RPO 15 min / RTO 2 h) has no infrastructure behind it (OP-02). **`05-03` §7 omits `INT-013` email from the P0 fallback register and its priority summary is wrong** — 12/17/12/6 stated against 13/14/12/8 enumerated, so every claim of `IP-09` coverage is wrong in both numerator and denominator (OP-03). **Platform severity had three claimed owners and no owner**; `OP-013` §4.1 now holds it and `SP-005`, `SP-031` and `TS-018` each need a one-line correction (OP-04). **Four more wave inversions**, taking the register-wide total to **43 across seven categories** (OP-05). **`M66` lands at W6 while the `P0` support model it traces to is needed at W1** and no paging platform exists at all (OP-06). **`NFR-091` requires 67 module runbooks and the register contains none** (OP-07). **Break-glass, the compensating control for the single-identity-provider architecture, is documented and does not exist** (OP-08). **The on-call rota needs ten people and has none** (OP-09). **The 38 access profiles do not exist and the `SOD-` space they would check against is unharmonised** (OP-10). **94 open decisions have nowhere to be logged — `RF-006` is unwritten and now blocks Definition of Done in five categories** (OP-12) |
| Category 19 `MM` — Multimedia & Asset Specifications | **Complete — 12 of 12 written, all at `Draft`** *(enumerated 2026-08-18)*. **Not yet audited** — authored concurrently with Category 99 |
| Category 99 `RF` — Reference & Registers | **Complete — 12 of 12 written, all at `Draft`** *(enumerated 2026-08-18)* — audited, `AUDIT-020`. **`RF-006` is written, closing `AUDIT-017` `OP-12` and unblocking Definition of Done in five categories.** **`RF-003` closes the diagnosis of `AF-06` and `TS-01`: the requirement denominator is `3,350`** — distinct `FR-` identifiers across 67 modules and 12 portals — and the three figures in circulation were never three counts of the same thing. **`RF-012` runs check `G1` for the first time and it fails**: **eight `AUDIT-001` findings are open across all nineteen subsequent audits** — five fully open, three partially discharged by this category — without the escalation `G1` requires (`AUDIT-020` `RF-020-03`). **`RF-010` runs check `G4` and it fails**: every file names an owner, and no file names a person. **CRITICAL, new and previously unrecorded anywhere: ISO 9001:2015 is replaced by ISO 9001:2026 on 16 September 2026**, with transition to September 2029 — **inside the delivery window** — re-opening the 38 content files that cite its clauses (`RF-008`, `RF-011` `CR-04`). **331 `verified:` dates across 68 files are in the future**, and no check compares a date to the present (`RF-002`) |
| Folder structure | **Created** — 21 category folders and 25 subfolders on disk |
| Authoring templates | **Created** — 12 templates in `_templates/`, enforced by `CP-09` |
| Content operating model | **Written** (`CG-002`) — awaiting Steering Committee ratification |
| Effort and budget | **Not in the approved business case** — see audit finding **AF-09** |
| Mandatory audit | **Complete** — 18 findings, 9 remediated, 9 open |

**Nothing in this register is authorised for production until the ERP Steering Committee
approves the content operating model (`CG-002`) and the effort variance raised in AF-09.**
This mirrors the module repository's own position: the charter in `00-02` is itself still
draft awaiting approval.

---

*1000FiX Services Limited · ERP Programme · Hotline 16743 · info@1000fix.com · ISO 9001:2015 Certified*
*Maintained by: Programme Content Lead, Enterprise Architecture*
*Next review: at the W1 wave boundary, or on approval of `CG-002`, whichever is earlier*
