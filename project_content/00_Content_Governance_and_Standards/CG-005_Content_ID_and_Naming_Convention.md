---
id: CG-005
title: Content ID and Naming Convention
project: 1000FiX ERP System v2.0
content_type: Standard
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Programme Content Lead
author: Programme Content Lead with Enterprise Architecture
reviewers: [Enterprise Architecture, Localisation Lead, Platform Engineering]
approver: Programme Content Lead
purpose: >
  Defines how content identifiers are allocated, reserved, retired and never reused, and how
  files and their bilingual and data counterparts are named. Identifier collision has already
  cost this programme three audits — a specification with no allocation, 70+ colliding
  custom-development identifiers, 22 colliding KPI identifiers, and a portal suite whose entire
  CD range collided with fifteen module claims. The same failure mode applies to content.
traces_to: [02-02 §1 RG-01/RG-02, 02-02 §5, 05-01 §1.3, CP-02, CP-05, AF-12, AF-15]
priority: P0
wave: W0
bilingual: no
bn_counterpart: n/a
sources:
  - source: 1000fix_ERP_Module/02_Architecture/02-02 §1 register rules RG-01…RG-06
    verified: 2026-08-15
  - source: 1000fix_ERP_Module/00_Governance_and_Charter/00-07 findings H2-04, H2-05, H2-06, H2-07
    verified: 2026-08-15
  - source: 1000fix_ERP_Module/03_Modules/K_Platform_and_Technology/_PORTAL_SUITE_AUDIT_REPORT.md finding X-01
    verified: 2026-08-15
  - source: project_content/_AUDIT/AUDIT-001 findings AF-12, AF-15
    verified: 2026-08-15
supersedes: none
review_due: 2027-02-15
---

# CG-005 — Content ID and Naming Convention

> **Read the evidence before the rules.** This programme has recorded six distinct identifier
> failures across three audits. Every rule below exists because one of them happened.

---

## 1. The evidence

| Failure | Audit | What happened |
|---|---|---|
| Specification with no allocation | `00-06` C-02 | `M31` was written with no requirement-ID range allocated in `05-01`. Rule `RG-01` (register-first) was created in response |
| Code reused in drafting | `00-06` C-03 | `M04` used code `BFO` briefly, then reverted to `FRD`. `BFO` is permanently retired and will never be reissued |
| KPI identifier collision | `00-07` H2-04 | **22 KPI identifiers** used by two or more different modules with different meanings |
| Custom-development collision | `00-07` H2-05 | **70+ CD identifiers** colliding across modules |
| Unregistered identifiers in use | `00-07` H2-06, H2-07 | **18 segregation-of-duties identifiers** used but never registered; roles R39–R46 used but unregistered; R54, R57, R60 used and undefined anywhere |
| Whole-range collision | Portal audit X-01 | The twelve portal specifications were allocated `CD-174`…`CD-187` from a ceiling that moved while they were being written. **Fifteen module claims collided.** The whole suite was reallocated `+26` |
| Missing convention document | `AUDIT-001` AF-15 | `99-02_Identifier_Conventions.md` — the consolidated document that would have prevented all six — has never been written |

**The pattern.** Every failure occurred at a boundary: between authoring sessions, between
categories, between a document and the register that should have governed it. None was a
carelessness failure. All were **allocation-authority** failures.

This file is the content set's answer, written before the first content ID is used rather than
after the third audit.

---

## 2. Governing rules

Mirrors `RG-01` and `RG-02` from `02-02` §1, extended to content.

| # | Rule | Statement |
|---|---|---|
| **ID-01** | **Register-first** | No content file may be created until its ID exists as a row in the Content Master Index. This is `RG-01` applied to content and rule `CM-R1`. |
| **ID-02** | **Permanent identity** | A content ID is permanent. The file it names may be renamed, re-scoped or rewritten; its ID does not change (`CP-02`, rule `CM-R4`). |
| **ID-03** | **Never reused** | A retired ID is never reissued, even decades later. `BFO` is the precedent. |
| **ID-04** | **Single allocation authority** | Only the Programme Content Lead allocates content IDs. No author, vendor or category lead self-allocates. |
| **ID-05** | **Contiguous within a category** | IDs are allocated in sequence. A gap means a retirement, and the retirement log (§7) explains it. An unexplained gap is a defect. |
| **ID-06** | **One ID, one file** | An ID names exactly one governing markdown file. Its data, Bengali and asset counterparts share the stem, not a new ID (`CP-01`). |
| **ID-07** | **Cross-space citation only** | Content files cite programme-wide identifiers (`Mnn`, `Pnn`, `FR-`, `NFR-`, `Rnn`, `KPI-`, `CD-`, `BRU-`) — they **never allocate** them. This is the rule the portal suite breached in X-01. |
| **ID-08** | **No spaces, ampersands or non-ASCII in any path** | Finding `AF-12`. Applies to every folder and file name in the content repository, without exception. |
| **ID-09** | **Case is fixed** | Category codes upper case, sequence three digits with leading zeros, name in Title_Case_With_Underscores. |
| **ID-10** | **Allocation is logged** | Every allocation, reservation and retirement is recorded in `RF-006` at the moment it is made. |

---

## 3. Content ID format

```
<CODE>-<nnn>
   │      └── three-digit sequence, 001–999, leading zeros always
   └───────── two-letter category code, upper case
```

Examples: `CG-005` · `MD-021` · `UI-011` · `DT-010` · `BN-014` · `RF-003`

**Never**: `CG-5`, `cg-005`, `CG005`, `CG-0005`, `CG-005a`

### 3.1 Category codes — the complete allocation

Twenty-one codes are allocated. **The remaining two-letter combinations are not free** — they
are unallocated, and allocating a new category requires Steering Committee approval under
`CG-002` §7.1.

| Code | Category | Folder | Registered | Allocated | Reserved for growth |
|---|---|---|:--:|---:|---|
| `CG` | Content Governance & Standards | `00_Content_Governance_and_Standards/` | ✅ | 001–014 | 015–050 |
| `VB` | Voice, Brand & Design-System Content | `01_Voice_Brand_and_Design_Content/` | ✅ | 001–010 | 011–050 |
| `MD` | Master Data & Configuration Seed Content | `02_Master_Data_and_Configuration/` | ✅ | 001–048 | 049–150 |
| `UI` | UI Copy & Microcopy | `03_UI_Copy_and_Microcopy/` | ✅ | 001–042 | 043–200 |
| `NT` | Notification & Messaging Content | `04_Notification_and_Messaging/` | ✅ | 001–026 | 027–100 |
| `DT` | Document, Print & Statutory Output Templates | `05_Document_and_Print_Templates/` | ✅ | 001–044 | 045–150 |
| `SP` | Process, SOP & Workflow Content | `06_Process_SOP_and_Workflow/` | ✅ | 001–034 | 035–150 |
| `KB` | Knowledge Base & Technical Library | `07_Knowledge_Base_and_Technical_Library/` | ✅ | 001–016 | 017–200 |
| `TR` | Training & Enablement | `08_Training_and_Enablement/` | ✅ | 001–024 | 025–100 |
| `HC` | Help Centre & Self-Service | `09_Help_Centre_and_Self_Service/` | ✅ | 001–020 | 021–200 |
| `LG` | Legal, Policy & Compliance | `10_Legal_Policy_and_Compliance/` | ✅ | 001–024 | 025–075 |
| `BN` | Localisation & Bilingual Content | `11_Localisation_Bengali/` | ✅ | 001–018 | 019–075 |
| `DM` | Data Migration Content | `12_Data_Migration_Content/` | ✅ | 001–014 | 015–060 |
| `TS` | Test & Acceptance Content | `13_Test_and_Acceptance_Content/` | ✅ | 001–018 | 019–100 |
| `RP` | Reporting, Analytics & KPI Content | `14_Reporting_Analytics_and_KPI/` | ✅ | 001–016 | 017–075 |
| `AP` | Integration & Developer Content | `15_Integration_and_Developer_Content/` | ✅ | 001–012 | 013–050 |
| `CM` | Change Management & Communications | `16_Change_Management_and_Comms/` | ✅ | 001–018 | 019–075 |
| `OP` | Operations, Support & Runbooks | `17_Operations_Support_and_Runbooks/` | ✅ | 001–016 | 017–075 |
| `EO` | Ecosystem Onboarding Content | `18_Ecosystem_Onboarding_Content/` | ✅ | 001–014 | 015–060 |
| `MM` | Multimedia & Asset Specifications | `19_Multimedia_and_Asset_Specs/` | ✅ | 001–012 | 013–050 |
| `RF` | Reference & Registers | `99_Reference_and_Registers/` | ✅ | 001–012 | 013–050 |
| | | | | **452 allocated** | |

**Reserved growth ranges are generous by design.** The portal audit finding X-01 happened
because an allocation was made from a ceiling that then moved. Wide reservations mean a
category can grow without ever approaching the next category's space — because there is no
"next category's space"; codes are alphabetic, not numeric-contiguous.

### 3.2 Codes that must never be allocated

| Code | Why |
|---|---|
| `MD` as a suffix on any other code | Confusable with the master-data category |
| Any code matching a module code from `02-02` §5 — `SRM`, `FSM`, `LOG`, `FRD`, `WTY`, `CTR`, `CRM`, `DTS`, `RMS`, `WSR`, `SRM2` and the other 56 | A three-letter module code and a two-letter content code are distinguishable, but a reader scanning `FR-SRM-001` and a hypothetical `SR-001` is not helped by the similarity |
| `FR`, `NFR`, `BRU`, `AUT`, `CD`, `KPI`, `SOD`, `RSK`, `DEP`, `INT`, `DoD`, `PS`, `IP`, `DM` as a *content* prefix | These are programme-wide identifier spaces owned by other registers (`ID-07`). **Note the collision risk: `DM` is used here as the Data Migration content code and in `05-02` as the data-model standard prefix `DM-01`…`DM-15`.** See §3.3 |

### 3.3 Registered collision — `DM`

**This is a real, known collision and it is registered rather than hidden.**

| Space | Form | Meaning | Owner |
|---|---|---|---|
| Content | `DM-001` … `DM-014` | Data Migration content files | This register |
| Data model standards | `DM-01` … `DM-15` | Modelling standards in `05-02` §1 | `05-02` |

They are distinguishable by digit count — content uses **three** digits, `05-02` uses **two** —
but that is a weak distinction for a human reader.

**Rule.** Every citation of either space must be qualified on first use in a file:
- Content: "`DM-004` (content — Field Mapping Workbook, Party and Customer)"
- Standard: "`05-02` DM-07 (modelling standard — monetary fields)"

The collision is not resolved by renaming, because `05-02` is an approved document with 15
standards cited across 67 module files. **The content space yields the qualification burden.**
Logged as a decision in `RF-006`.

---

## 4. File naming

```
<CODE>-<nnn>_<Descriptive_Name_In_Title_Case_With_Underscores>.<ext>
```

| Element | Rule |
|---|---|
| `CODE-nnn` | Exactly as allocated. No variation |
| Separator after the ID | A single underscore |
| Name | Title Case, words separated by underscores. Describes the content, not the category |
| Length | The full file name should not exceed 80 characters; Windows path limits bite on deep trees |
| Characters | `A–Z a–z 0–9 _` only. **No spaces, ampersands, hyphens inside the name, apostrophes, brackets or non-ASCII** (`ID-08`) |
| Extension | `.md` for the governing specification. Data and asset counterparts per §5 |

### 4.1 Naming the descriptive part

| Do | Do not | Why |
|---|---|---|
| `MD-021_Device_Category_Make_and_Model_Catalogue.md` | `MD-021_Devices.md` | Too terse to distinguish from `MD-017` asset registry content |
| `UI-011_P01_Customer_Portal_and_App_UI_Copy_Pack.md` | `UI-011_Customer_UI.md` | Portal ID in the name makes the binding visible in a file listing |
| `DT-010_Tax_Invoice_Mushak_6_3.md` | `DT-010_Mushak_6.3_Invoice.md` | Full stops in file names break tooling; write `6_3` |
| `LG-008_Privacy_Notice_and_Consent_Copy.md` | `LG-008_Privacy_&_Consent.md` | Ampersand banned (`ID-08`, finding `AF-12`) |
| `SP-019_SOP_Cash_Collection_and_Banking.md` | `SP-019_Cash_SOP.md` | Type prefix `SOP_` inside the name aids scanning within a large folder |

### 4.2 Reserved prefixes

| Prefix | Meaning | Where |
|---|---|---|
| `_` | Non-content directory or file: `_templates/`, `_AUDIT/`, `_ARCHIVE/` | Sorts to the top |
| `TPL_` | An authoring template | `_templates/` only |
| `SUPERSEDED_` | Retained for traceability; not authoritative | `_ARCHIVE/` only |
| `DRAFT_` | Work in progress, not approved. **Removed when status reaches `Approved`** | Anywhere, temporarily |

> A `DRAFT_` prefix and a `status: Approved` front matter cannot both be true. `CG-008` checks
> for this.

---

## 5. Counterpart files

An ID names one governing markdown file. Everything that belongs to it shares the stem.

| Counterpart | Naming | Example |
|---|---|---|
| **Bengali version** | `_BN` suffix before the extension | `UI-011_P01_Customer_Portal_and_App_UI_Copy_Pack_BN.md` |
| **Loadable data** | Same stem, data extension | `MD-035_Chart_of_Accounts_Bangladesh.csv` |
| **Structured data** | Same stem | `NT-008_WhatsApp_Business_Template_Library.json` |
| **Spreadsheet workbook** | Same stem | `DM-004_Field_Mapping_Workbook_Party_and_Customer.xlsx` |
| **Rendered asset** | Same stem in an `assets/` subfolder beside the file | `assets/DT-010_Tax_Invoice_Mushak_6_3_specimen.pdf` |
| **Multi-part data** | Same stem, `__part` suffix, two underscores | `MD-006_Bangladesh_Geographic_Hierarchy__districts.csv` |

**Rules**

| # | Rule |
|---|---|
| **CF-01** | The markdown governs; the data loads. Where they disagree, the markdown is the specification and the data file is defective |
| **CF-02** | A data file with no governing markdown is unmanaged and is rejected at review |
| **CF-03** | The Bengali counterpart carries the **same ID**, not a `BN` category ID. `BN-009` … `BN-017` are *bundles* that aggregate and govern translation; they are not per-file translations |
| **CF-04** | Assets referenced by a file live in an `assets/` folder in the same directory, prefixed with the owning file's ID |

---

## 6. Reservation

Reservation prevents the X-01 failure — an allocation made from a ceiling that then moves.

| Situation | Procedure |
|---|---|
| A category is about to be authored in bulk (e.g. all 42 `UI` files) | The Content Lead reserves the whole block in the register **before** authoring starts, with placeholder rows carrying `status: Reserved` |
| A vendor will author a set | The block is reserved and the vendor is given the exact IDs. **A vendor never allocates** |
| A file is planned but not scheduled | The row exists with `status: Backlog` in `RF-007`. The ID is consumed |
| Work is abandoned before the file is written | The reserved ID is **retired**, not released (`ID-03`) |

**Reservations expire.** A reservation unused for two waves is reviewed; if the work is
abandoned, the ID retires. If it is still intended, the reservation is renewed with a date.
An indefinite reservation is how ranges silently fill.

---

## 7. Retirement log

Every retired ID is recorded here permanently. **This table only grows.**

| ID | Title at retirement | Retired | Reason | Replacement |
|---|---|---|---|---|
| — | *(none yet)* | — | — | — |

**Retirement procedure**

1. Mark the Content Master Index row `WITHDRAWN` with date and reason. **Do not delete the row**
   — a deleted row makes the ID look free.
2. Move any written file to `_ARCHIVE/` with a `SUPERSEDED_` prefix and a header note
   (`CP-10`, `CM-R5`).
3. Add a row to this table.
4. Log in `RF-006`.
5. Add the retired ID to the automated lint list so a future citation fails the build.

---

## 8. Citing identifiers from other spaces

Content cites; content never allocates (`ID-07`). This table is the complete list of what may be
cited and where it is owned.

| Space | Form | Owning register | Content may |
|---|---|---|---|
| Module | `M01`–`M67` | `02-02` §5 | Cite |
| Portal | `P01`–`P12` | `04-00` §2 | Cite |
| Functional requirement | `FR-<CODE>-nnn` | `05-01` §1.3 | Cite |
| Non-functional requirement | `NFR-001`–`NFR-100` | `05-06` | Cite |
| Business rule | `BRU-<CODE>-nn` | The owning module file | Cite |
| Automation | `AUT-<CODE>-nn` | The owning module file | Cite |
| Role | `R01`–`R38` (+ unregistered R39–R46, R54, R57, R60) | `05-04` | Cite registered roles only |
| Segregation of duties | `SOD-nn` | `05-04` | Cite registered only |
| KPI | `KPI-nnn` | Programme KPI register | Cite. `RP-001` **defines** metrics but does not allocate `KPI-` IDs |
| Custom development | `CD-nnn` | `02-05` | Cite |
| Integration | `INT-001`–`INT-047` | `05-03` §2 | Cite |
| Risk | `RSK-nnn` | `00-04` | Cite |
| Dependency | `DEP-nn` | `00-04` | Cite |
| Decision | `D-nn` | `00-05` — **does not exist**, finding `AF-04` | Cite with a caveat until `00-05` is written |
| Wave | `W1`–`W9` | `06-01` | Cite |
| Delivery layer | `L1`–`L6` | `02-05` | Cite |
| Content principle | `CP-01`–`CP-11` | Content Master Index §2 | Cite |
| Content maintenance rule | `CM-R1`–`CM-R10` | Content Master Index §9 | Cite |
| Audit finding | `AF-nn` | `AUDIT-001` | Cite |

> ⚠ **`D-nn` caveat.** Two audits cite decision `D-14`, and `00-05_Decision_Log_and_Change_Control.md`
> does not exist (`AF-04`). Until it is written, any content citing a `D-` identifier must state
> that the decision log is absent. Content decisions go in `RF-006`, which does exist.

---

## 9. Folder naming

| Rule | Detail |
|---|---|
| Numeric prefix | `00_` … `19_`, `99_`. Two digits, underscore separator |
| Name | `Title_Case_With_Underscores`, describing the category |
| Subfolders | Parent number plus a letter: `02A_`, `02B_` … Sorts predictably within the parent |
| Depth | Maximum three levels below `project_content/`. Deeper trees break Windows path limits and make links fragile |
| Characters | `A–Z a–z 0–9 _` only (`ID-08`) |

**The `AF-12` precedent.** The corporate website content set uses folder names such as
`BLOG & EDUCATIONAL`, `SUPPORT & HELP` and `SEO & TECHNICAL`. Every one requires shell quoting,
breaks unquoted CI paths and needs URL encoding. That set is not being renamed — 431 files would
lose their path references for no functional gain to that programme. **This set does not repeat
it.**

---

## 10. Enforcement

| Check | Mechanism | Failure action |
|---|---|---|
| File name matches its ID | Regex on every file in the repository | Build fails |
| No spaces, ampersands or non-ASCII in any path | Path scan | Build fails |
| Every file on disk has a register row | Filesystem diff against the Content Master Index | Build fails — `ID-01` breached |
| No duplicate IDs | Extract, sort, deduplicate | Build fails |
| Contiguity | Compare count to highest ID per category | Warning; must be explained by a retirement-log row |
| No retired ID in use | Lint against §7 | Build fails |
| Bengali counterpart shares the stem | Match `_BN.md` files to their source | Warning |
| Reserved prefix used correctly | Scan for `_`, `TPL_`, `SUPERSEDED_`, `DRAFT_` | Warning; `DRAFT_` plus `status: Approved` fails |
| Programme-wide identifier cited, not allocated | Scan for `FR-`, `CD-`, `KPI-`, `SOD-`, `R` allocations in content files | Build fails — `ID-07` breached |

These are checks A1–A6, B1–B5 and D2–D4 of `_AUDIT/AUDIT_Checklist_Recurring.md`, run per
commit rather than per wave.

---

## 11. Relationship to the missing `99-02`

`AUDIT-001` finding **AF-15** records that `99_Reference/99-02_Identifier_Conventions.md` — the
consolidated document that would have prevented all six identifier failures in §1 — has never
been written.

**This file does not replace it.** `99-02` must cover the programme-wide spaces (`FR-`, `CD-`,
`KPI-`, `SOD-`, `Rnn`, `NFR-`), which content only cites. `CG-005` covers the content space,
which `99-02` will not.

The two are complementary and both are needed. `RF-001` and this file mitigate the content half;
audit recommendation **R-08** owns the other half, assigned to Enterprise Architecture within
four weeks.

---

## 12. Related documents

| Document | Relationship |
|---|---|
| [`CG-001_Content_Master_Index.md`](CG-001_Content_Master_Index.md) | Where IDs are registered; the allocation procedure |
| [`CG-006_Content_Lifecycle_and_Versioning_Policy.md`](CG-006_Content_Lifecycle_and_Versioning_Policy.md) | The status values a registered ID may hold |
| [`CG-004_Terminology_and_Controlled_Vocabulary_Standard.md`](CG-004_Terminology_and_Controlled_Vocabulary_Standard.md) | The same register-first discipline applied to words |
| [`CG-009_Content_Template_Register.md`](CG-009_Content_Template_Register.md) | `TPL_` prefixed files |
| `RF-006` Content Decision Log | Where every allocation and retirement is logged |
| `RF-007` Content Backlog Register | Where reserved-but-unscheduled IDs live |
| `02-02` §1 | Rules `RG-01` and `RG-02`, which `ID-01` and `ID-02` mirror |
| `99-02` Identifier Conventions | **Planned, not written** — the programme-wide counterpart (`AF-15`, R-08) |

---

## 13. Revision history

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue. Ten rules, complete 21-code allocation with growth reservations, `DM` collision registered, counterpart naming, reservation and retirement procedures, enforcement checks | Programme Content Lead (pending) |

---

## Definition of Done

- [x] Front matter complete
- [x] Every rule traced to a recorded audit failure
- [x] All 21 category codes allocated with explicit growth reservations
- [x] The `DM` collision registered and a qualification rule stated, not hidden
- [x] Retirement log created, empty, with procedure
- [x] Complete list of citable programme-wide spaces, with the `D-nn` caveat stated
- [x] All internal links resolve
- [x] Bengali counterpart — n/a
- [ ] Named approver recorded — **pending**
- [x] Registered in the Content Master Index
- [x] Relationship to the missing `99-02` stated rather than implied

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
