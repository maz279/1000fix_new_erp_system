---
id: CG-008
title: Content Definition of Done and QA Checklist
project: 1000FiX ERP System v2.0
content_type: Standard
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Content Design Lead
author: Content Design with Programme Content Lead
reviewers: [Programme Content Lead, QA Lead, Localisation Lead, Enterprise Architecture]
approver: Programme Content Lead
purpose: >
  Defines the checklist a content file must pass to become Approved. Prevents the "written but
  unusable" state — a file that exists, looks finished, and cannot be built from, translated,
  tested or trusted. Mirrors the _MODULE_TEMPLATE.md enforcement that already works in the
  specification repository, where a module file that does not conform fails the documentation
  gate.
traces_to: [03_Modules/_MODULE_TEMPLATE.md, CG-003, CG-004, CG-005, CG-006, CG-007, CG-011, CG-012, CP-03, CP-04, CP-09]
priority: P1
wave: W0
bilingual: no
bn_counterpart: n/a
sources:
  - source: 1000fix_ERP_Module/03_Modules/_MODULE_TEMPLATE.md — house 19-section structure and §0 identifier rules
    verified: 2026-08-15
  - source: 1000fix_ERP_Module/02_Architecture/02-02 §DoD-01…DoD-17 module definition of done
    verified: 2026-08-15
  - source: project_content/_AUDIT/AUDIT_Checklist_Recurring.md §A–G
    verified: 2026-08-15
supersedes: none
review_due: 2027-02-15
---

# CG-008 — Content Definition of Done and QA Checklist

> **The specification repository already proves this works.** `_MODULE_TEMPLATE.md` states that
> "a new module that does not conform will fail the documentation gate", and 67 module
> specifications conform. `02-02` carries `DoD-01`…`DoD-17` for modules. This file is the same
> mechanism for the 452 content files.

---

## 1. How to use this file

| You are… | Use |
|---|---|
| An author, before submitting to `Review` | §3 — the universal checklist |
| An author of a specific content type | §3 **and** the relevant block in §4 |
| A reviewer at gate G1 (`CG-007`) | §3 and §4 as the review script |
| A Content Lead deciding whether to approve | §5 — the blocking items |
| An auditor | `_AUDIT/AUDIT_Checklist_Recurring.md`, which tests conformance to this file |

**A file is submitted to `Review` only when every applicable box is ticked.** Submitting an
incomplete file consumes reviewer capacity that `CG-007` §10 shows the programme does not have.

---

## 2. Rules

| # | Rule |
|---|---|
| **DoD-01** | The checklist is ticked by the **author**, verified by the **reviewer**, and confirmed by the **approver**. Three people, one list |
| **DoD-02** | An unticked box is not an opinion. Either the item is done, or the file is not ready |
| **DoD-03** | An item that genuinely does not apply is marked `n/a` **with a reason on the same line**. A bare `n/a` fails |
| **DoD-04** | The completed checklist stays in the file, at the bottom, as the record |
| **DoD-05** | Blocking items (§5) cannot be waived by anyone below the Programme Content Lead, and three of them cannot be waived at all |
| **DoD-06** | The checklist is re-run in full on every MAJOR version (`CG-006` §2) |
| **DoD-07** | Automated checks (§6) run before human review. A file failing an automated check does not enter the review queue |

---

## 3. Universal checklist — every content file

### 3.1 Identity and registration

- [ ] **U-01** The file has a content ID allocated by the Programme Content Lead (`CG-005` §2 `ID-04`)
- [ ] **U-02** A register row exists in the Content Master Index, created **before** this file (`CM-R1`, `ID-01`)
- [ ] **U-03** The file name matches its ID and follows `CG-005` §4 exactly
- [ ] **U-04** No spaces, ampersands or non-ASCII characters anywhere in the path (`ID-08`)
- [ ] **U-05** The file is in the folder its category declares (`CG-005` §3.1)
- [ ] **U-06** No `DRAFT_` prefix remains if status is `Approved`

### 3.2 Front matter

- [ ] **U-07** All required front-matter keys are present and populated — none left as `<placeholder>`
- [ ] **U-08** `purpose:` states the **consequence of the file's absence**, not a restatement of the title (`CP-03`)
- [ ] **U-09** `traces_to:` names at least one module, portal or specification, and every entry resolves (`CP-04`)
- [ ] **U-10** `priority:` and `wave:` match the Content Master Index row
- [ ] **U-11** `owner:` names an accountable function that exists in `CG-002` §6
- [ ] **U-12** `bilingual:` is set, and matches the `CG-010` policy for this content type
- [ ] **U-13** `status:` and `version:` are consistent — any `0.x` version is `Draft` or `Review` (`CG-006` §2)
- [ ] **U-14** `review_due:` is set per the cycle for this content class (`CG-006` §5)
- [ ] **U-15** `pinned_to:` is present if this content type requires a pin (`CG-006` §3.2)
- [ ] **U-16** `statutory_pin:` is present and complete if this is Class A content (`CG-006` §4.1)

### 3.3 Structure

- [ ] **U-17** Authored from the correct template in `_templates/` (`CP-09`, `CG-009`)
- [ ] **U-18** No template section removed; sections that do not apply keep their heading with a one-line reason
- [ ] **U-19** Heading levels increment by one; none skipped (`CG-003` L-08)
- [ ] **U-20** A revision history table is present and the current version has a row
- [ ] **U-21** A related-documents table is present

### 3.4 Content quality

- [ ] **U-22** Style conforms to `CG-003` — en-GB, sentence case, second person, active voice, punctuation, numbers
- [ ] **U-23** Terminology conforms to `CG-004` — approved terms only, no banned synonyms
- [ ] **U-24** Every business object named binds to the entity `CG-004` assigns it
- [ ] **U-25** Nothing here duplicates content owned by another file; it references instead (`CP-01`)
- [ ] **U-26** Cross-surface facts use the canonical wording from their owning file (`CG-003` §10)
- [ ] **U-27** The content is complete for its stated scope — a reader in the target role can act without asking a question

### 3.5 Evidence

- [ ] **U-28** Every factual, statutory, pricing or capability claim names a source in `sources:` (`CG-012`, `CM-R8`)
- [ ] **U-29** Every source carries a `verified:` date
- [ ] **U-30** No claim rests on commentary, press reporting or a vendor summary where a primary source exists (`00-07` H2-13 precedent)
- [ ] **U-31** Figures describing what the repository contains are **counted at the time of writing**, with the count date beside them (`RG-06`, `CP-11`)

### 3.6 Identifiers and links

- [ ] **U-32** Every cited `Mnn`, `Pnn`, `FR-`, `NFR-`, `BRU-`, `Rnn`, `INT-`, `CD-`, `KPI-` exists in its owning register
- [ ] **U-33** No programme-wide identifier is **allocated** by this file — only cited (`ID-07`)
- [ ] **U-34** Every relative link resolves against the filesystem
- [ ] **U-35** Link text describes the destination; no "click here" or "read more" (`CG-011`, WCAG SC 2.4.4)
- [ ] **U-36** The `DM` space is qualified on first use — content `DM-nnn` versus `05-02` `DM-nn` (`CG-005` §3.3)

### 3.7 Accessibility

- [ ] **U-37** Reading level meets the target for the audience (`CG-011` §3)
- [ ] **U-38** Every image, diagram and screenshot has a text alternative (`CG-011` §4)
- [ ] **U-39** Tables carry data, not layout; every table has a header row (`CG-011` §6)
- [ ] **U-40** Colour is never the only signal (`CG-011` §7)
- [ ] **U-41** Screenshots use sample data with personal data redacted (`MM-002`)

### 3.8 Bilingual

Applies where `bilingual: yes`.

- [ ] **U-42** The Bengali counterpart exists and shares the stem with a `_BN` suffix (`CG-005` §5)
- [ ] **U-43** The Bengali is a professional translation, not machine output (`CG-010`, `CP-05`)
- [ ] **U-44** Bengali terms match `BN-003`; do-not-translate items are untranslated (`BN-004`)
- [ ] **U-45** Dates, numbers, currency and addresses follow `BN-007`
- [ ] **U-46** Linguistic sign-off was performed **in context**, not on a string list (`BN-018`, `CG-007` G4)
- [ ] **U-47** No truncation or layout break at the target size (`BN-006`)
- [ ] **U-48** The English and Bengali versions carry the same version number (`LC-08`)

### 3.9 Approval

- [ ] **U-49** Every gate required for this content class has been passed (`CG-007` §2.1)
- [ ] **U-50** The approver is named, is not the author, and is registered in `RF-010` (`CO-04`, `SO-01`, `SO-02`)
- [ ] **U-51** For Class A and B: the approval is recorded in `LG-001` with version and date (`SO-05`)
- [ ] **U-52** For Class A: external verification is recorded with adviser, date and scope (`CG-007` §3.6)
- [ ] **U-53** Any decision taken while authoring is logged in `RF-006` (`CO-10`)
- [ ] **U-54** Any waived item is logged with a named remediation date (`WV-01`)

---

## 4. Additional checks by content type

### 4.1 Master data (`MD`)

- [ ] **MD-a** The record structure table names column, type, required flag, constraint and Bengali requirement
- [ ] **MD-b** Natural key, surrogate key and code format are stated; code reuse is forbidden explicitly
- [ ] **MD-c** Every validation rule names its class (H/A/S/C) and its error message ID in `UI-004`
- [ ] **MD-d** Load dependencies are stated and reconcile with `MD-048`
- [ ] **MD-e** The golden source and acquisition method are named
- [ ] **MD-f** Expected volumes are stated per environment
- [ ] **MD-g** The data counterpart file exists, shares the stem, and matches the specified structure (`CF-01`)
- [ ] **MD-h** Sample rows are included and parse correctly
- [ ] **MD-i** Effective dating is specified where the data is time-sensitive (`CG-006` §3.4)
- [ ] **MD-j** Archive rule states records are archived, never deleted (`05-02` DM-06)

### 4.2 UI copy (`UI`)

- [ ] **UI-a** Every string has an i18n key conforming to `UI-001`
- [ ] **UI-b** No string is concatenated across a translatable boundary (`CG-003` S-05, `BN-005`)
- [ ] **UI-c** Every error message follows the three-part structure and states a remedy (`CG-003` §3, `BR-STD-04`, `PS-09`)
- [ ] **UI-d** Error messages expose no internal detail — no table names, stack traces, model names or internal IDs
- [ ] **UI-e** Message class matches the rule class in `05-05` — hard rules block, approved-override rules name the authoriser, soft rules warn
- [ ] **UI-f** Empty states, loading states and offline states are covered, not only the happy path
- [ ] **UI-g** Destructive actions state the consequence; buttons are verbs, not OK/Cancel
- [ ] **UI-h** Character budget is recorded per string, with Bengali expansion assessed
- [ ] **UI-i** Status labels come from `MD-027`, not invented locally (`T-06`)
- [ ] **UI-j** The pack is pinned to a release and verified against the build (`CG-006` §3)

### 4.3 Notifications (`NT`)

- [ ] **NT-a** Every template names its trigger event, channel, audience and suppression rules
- [ ] **NT-b** The event exists in the `NT-001` channel matrix
- [ ] **NT-c** Variables are declared with their source field
- [ ] **NT-d** Consent class is stated — transactional or marketing (`NT-002`, `LG-008`)
- [ ] **NT-e** For SMS: character count and segment count are recorded **for both languages**. Bengali is UCS-2 and segments at 70 characters, not 160
- [ ] **NT-f** For WhatsApp: category, submission and approval status are recorded (`NT-008`)
- [ ] **NT-g** A fallback is defined for channel failure (`NT-025`, `IP-09`)
- [ ] **NT-h** Quiet-hours and frequency treatment are stated (`NT-003`)

### 4.4 Documents and print (`DT`)

- [ ] **DT-a** Layout zones are specified with bilingual treatment (`DT-001`, `VB-004`)
- [ ] **DT-b** Every field maps to a source field; nothing is typed that the system holds
- [ ] **DT-c** Numbering mask references `MD-040`
- [ ] **DT-d** Retention period references `LG-009`
- [ ] **DT-e** For statutory documents: every mandated element is listed with its source and verification date
- [ ] **DT-f** For statutory documents: `statutory_pin` names the instrument and fiscal year (`CG-006` §4.1)
- [ ] **DT-g** For statutory documents: G6 external verification is recorded (`CG-007` §3.6)
- [ ] **DT-h** The rendered output has been checked, not only the specification (`CG-007` G3)
- [ ] **DT-i** A worked specimen is linked in `RF-009`
- [ ] **DT-j** Bengali rendering is verified on the target printers (`05-06` §9)

### 4.5 Process and SOP (`SP`)

- [ ] **SP-a** One action per numbered step; a step containing "and then" is split
- [ ] **SP-b** Every step names who performs it and in which system or screen
- [ ] **SP-c** Approval limits reconcile **exactly** with `SP-004`
- [ ] **SP-d** Escalation paths reconcile with `SP-005`
- [ ] **SP-e** Exceptions and failure handling are covered, not only the happy path
- [ ] **SP-f** A manual fallback is stated where the process depends on a P0 integration (`IP-09`, `OP-014`)
- [ ] **SP-g** Segregation of duties is stated and reconciles with `SP-006`
- [ ] **SP-h** Evidence produced at each step is named — this is what an ISO auditor asks for
- [ ] **SP-i** KPIs cite `RP-001` definitions, not local ones

### 4.6 Training (`TR`)

- [ ] **TR-a** Learning objectives are observable and assessable
- [ ] **TR-b** Every objective maps to at least one assessment item
- [ ] **TR-c** Exercises use `TS-002` test data, never production data
- [ ] **TR-d** UI labels are cited verbatim from the pinned `UI` pack (`CG-003` X-03)
- [ ] **TR-e** Duration is realistic against the role's stated target — `P03` targets four hours to competence
- [ ] **TR-f** Job aids are produced, not only slides
- [ ] **TR-g** For field roles: the material is Bengali-native, not translated (`BN-016`)

### 4.7 Help (`HC`)

- [ ] **HC-a** Task articles state prerequisites and outcome
- [ ] **HC-b** UI labels are cited verbatim in bold from the pinned `UI` pack
- [ ] **HC-c** Screenshots follow `MM-002` — sample data, redacted, current release
- [ ] **HC-d** A troubleshooting block covers what to do when the steps do not work
- [ ] **HC-e** The article is reachable from the IA in `HC-001`

### 4.8 Legal (`LG`)

- [ ] **LG-a** Clauses are numbered and independently referenceable
- [ ] **LG-b** Defined terms are defined in the document, and capitalised only where defined (`CG-003` §6)
- [ ] **LG-c** No contradiction with `LG-008`, `LG-009` or `LG-012` — checked, not assumed
- [ ] **LG-d** The acceptance-capture mechanism is specified (`LG-019`)
- [ ] **LG-e** Governing law and dispute resolution are stated
- [ ] **LG-f** External counsel review is recorded with name and date
- [ ] **LG-g** The version and effective date are registered in `LG-001`

### 4.9 Test content (`TS`)

- [ ] **TS-a** Every script traces to a requirement and to a module §15 acceptance criterion
- [ ] **TS-b** Expected results are stated before execution, not inferred after
- [ ] **TS-c** Negative and edge cases are included
- [ ] **TS-d** Bilingual checks are included for bilingual surfaces
- [ ] **TS-e** Test data is `TS-002`, realistic for Bangladesh, and contains no production personal data
- [ ] **TS-f** Exit criteria and sign-off are specified

### 4.10 Runbooks (`OP`)

- [ ] **OP-a** Health checks state what "healthy" looks like, not only how to check
- [ ] **OP-b** Common failure modes give symptom, diagnosis, fix and escalation threshold
- [ ] **OP-c** A manual fallback exists for every P0 integration (`IP-09`)
- [ ] **OP-d** Backup and recovery state RPO, RTO and the last test date (`NFR-007`)
- [ ] **OP-e** Break-glass access states who authorises and where it is audited
- [ ] **OP-f** The runbook has been **executed** at least once, not only written

---

## 5. Blocking items

Most checklist items can be waived by the Programme Content Lead with a remediation date
(`WV-01`). **These cannot.**

| # | Item | Why it cannot be waived |
|---|---|---|
| **B-01** | `U-02` — a register row exists, created before the file | `CM-R1`. The failure it prevents has occurred three times in this programme |
| **B-02** | `U-08` — `purpose:` states the consequence of absence | A file with no consequence is scope creep, not content |
| **B-03** | `U-09` — `traces_to:` resolves | Content with no upstream requirement cannot be prioritised or retired rationally |
| **B-04** | `U-28`–`U-30` — claims carry primary sources with verification dates | `00-07` H2-13 |
| **B-05** | `U-49` — required gates passed | The gates are the control |
| **B-06** | `U-50` — the approver is named and is not the author | `CO-04` |
| **B-07** | **Class A: `U-52` external verification** | **Never waivable** — `WV-02` |
| **B-08** | **Class B: G5 legal review** | **Never waivable** — `WV-02` |
| **B-09** | **Customer- and field-facing bilingual: `U-46` in-context linguistic sign-off** | **Never waivable** — `WV-03`, `PS-03`, `P02` non-negotiable #3 |
| **B-10** | `UI-c` — every error message states a remedy | `BR-STD-04` and `PS-09` are contractual, not stylistic |
| **B-11** | `DT-e`–`DT-g` — statutory documents verified against the instrument | A non-conforming Mushak 6.3 is an unlawful invoice |
| **B-12** | `TS-e` / `HC-c` / `TR-c` — no production personal data in test data, screenshots or exercises | Data-protection obligation under the residency and notice requirements in `05-06` §6 |

---

## 6. Automated checks

These run in CI before human review (`DoD-07`). A failure returns the file to the author
without consuming reviewer capacity.

| Check | Tests | Items |
|---|---|---|
| Front-matter schema | Required keys present, no placeholders, valid values | U-07…U-16 |
| File naming | Regex against `CG-005` §4 | U-03, U-04 |
| Path hygiene | No spaces, ampersands, non-ASCII | U-04 |
| Register presence | Every file on disk has a register row; every non-`Planned` row has a file | U-02 |
| ID uniqueness and contiguity | Extract, sort, deduplicate, compare to retirement log | `CG-005` §10 |
| Link resolution | Every relative link resolves | U-34 |
| Banned terminology | `CG-004` §4 banned lists and `CG-003` §8.1 banned words | U-22, U-23 |
| Spelling | en-GB dictionary | U-22 |
| Heading increment | No skipped levels | U-19 |
| Link text | No "click here", "read more", "this link" | U-35 |
| Sentence length | Warns above the `CG-003` S-01 limits | U-22 |
| Template conformance | Section headings match the declared template | U-17, U-18 |
| Bilingual pairing | Every `bilingual: yes` file has a `_BN` counterpart at the same version | U-42, U-48 |
| Identifier citation | No allocation of programme-wide spaces in content files | U-33 |
| `DM` qualification | First use of a `DM` identifier is qualified | U-36 |

---

## 7. Sampling and audit

| Level | Coverage | When | Owner |
|---|---|---|---|
| Automated | 100% of files, every commit | Continuous | Platform Engineering |
| Author self-check | 100% of files | Before submission | Author |
| Reviewer verification | 100% of files in `Review` | At each gate | Gate reviewer |
| Content Lead confirmation | Blocking items on 100%; full list on a 20% sample | At approval | Programme Content Lead |
| Wave audit | Per `_AUDIT/AUDIT_Checklist_Recurring.md` §E | Every wave boundary | Programme Content Lead |

**Target defect rates**, measured at wave audit:

| Measure | Target |
|---|---|
| Files reaching `Approved` with an unremediated blocking item | **Zero** |
| Terminology defect rate (`CG-004` conformance) | Under 2% |
| Evidence defect rate on Class A and B files | **Zero** |
| Evidence defect rate on other classes, sampled | Under 5% |
| Broken internal links | **Zero** |
| Bilingual files approved without in-context sign-off | **Zero** |

---

## 8. Related documents

| Document | Relationship |
|---|---|
| [`CG-003_ERP_Product_Content_Style_Guide.md`](CG-003_ERP_Product_Content_Style_Guide.md) | What U-22 tests |
| [`CG-004_Terminology_and_Controlled_Vocabulary_Standard.md`](CG-004_Terminology_and_Controlled_Vocabulary_Standard.md) | What U-23 and U-24 test |
| [`CG-005_Content_ID_and_Naming_Convention.md`](CG-005_Content_ID_and_Naming_Convention.md) | What U-01 to U-06 test |
| [`CG-006_Content_Lifecycle_and_Versioning_Policy.md`](CG-006_Content_Lifecycle_and_Versioning_Policy.md) | Status, version and pin fields |
| [`CG-007_Review_Approval_and_Signoff_Workflow.md`](CG-007_Review_Approval_and_Signoff_Workflow.md) | The gates U-49 requires |
| [`CG-009_Content_Template_Register.md`](CG-009_Content_Template_Register.md) | The templates U-17 requires |
| [`CG-011_Accessibility_Content_Standard.md`](CG-011_Accessibility_Content_Standard.md) | What U-37 to U-41 test |
| [`CG-012_Content_Sourcing_and_Evidence_Rules.md`](CG-012_Content_Sourcing_and_Evidence_Rules.md) | What U-28 to U-31 test |
| `_AUDIT/AUDIT_Checklist_Recurring.md` | The audit that tests conformance to this file |
| `03_Modules/_MODULE_TEMPLATE.md` | The precedent this file mirrors |
| `02-02` DoD-01…DoD-17 | The module definition of done |

---

## 9. Revision history

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue. 54 universal items in nine groups, type-specific blocks for ten content types, twelve blocking items of which six are unwaivable, fifteen automated checks, sampling and target defect rates | Programme Content Lead (pending) |

---

## Definition of Done

- [x] Front matter complete
- [x] Universal checklist covers identity, front matter, structure, quality, evidence, identifiers, accessibility, bilingual and approval
- [x] Type-specific checks exist for the ten content types with distinct failure modes
- [x] Blocking items are separated from waivable ones, and the unwaivable subset is stated
- [x] Automated checks are specified concretely enough to implement
- [x] Target defect rates are numeric
- [x] All internal links resolve
- [x] Bengali counterpart — n/a
- [ ] Named approver recorded — **pending**
- [x] Registered in the Content Master Index

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
