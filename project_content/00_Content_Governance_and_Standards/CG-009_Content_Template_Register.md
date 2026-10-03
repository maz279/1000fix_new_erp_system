---
id: CG-009
title: Content Template Register
project: 1000FiX ERP System v2.0
content_type: Governance
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Content Design Lead
author: Content Design
reviewers: [Programme Content Lead, Enterprise Architecture, Localisation Lead]
approver: Programme Content Lead
purpose: >
  Indexes the twelve authoring templates, states what each governs, and decides which template
  applies to each of the 21 content categories. Without it, authors invent structure per file
  and reviewers have nothing to review against — which makes the CG-008 Definition of Done
  unenforceable, because "conforms to its template" has no referent.
traces_to: [CP-09, CG-008 U-17, _templates/, 03_Modules/_MODULE_TEMPLATE.md]
priority: P1
wave: W0
bilingual: no
bn_counterpart: n/a
sources:
  - source: project_content/_templates/ — twelve templates, enumerated 2026-08-15
    verified: 2026-08-15
  - source: 1000fix_ERP_Module/03_Modules/_MODULE_TEMPLATE.md — the enforced house structure precedent
    verified: 2026-08-15
  - source: project_content/1000FiX_ERP_Content_Master_Index.md §3.2 folder tree
    verified: 2026-08-15
supersedes: none
review_due: 2027-02-15
---

# CG-009 — Content Template Register

> **Principle `CP-09`: templates are enforced.** The specification repository proves the
> mechanism works — `_MODULE_TEMPLATE.md` defines a 19-section house structure and all 67 module
> files conform. A file that does not conform fails the documentation gate. This register is
> the content-side equivalent.

---

## 1. Why templates, not guidance

A template does four things that a style guide cannot.

| It does | Consequence |
|---|---|
| **Makes omission visible** | An empty section is obvious. A missing paragraph in free-form prose is not |
| **Gives the reviewer a script** | `CG-008` U-17 and U-18 become mechanically checkable |
| **Makes content comparable** | A reviewer moving between 34 SOPs finds approvals in the same place each time |
| **Survives author turnover** | Over 36 months, content will be written by staff, contractors and vendors who never meet |

**The failure it prevents** is the one the module repository already avoided by enforcing its
template: 67 specifications by different authors across many months that a reader can navigate
identically. Content has 452 files and more authors. The need is larger, not smaller.

---

## 2. The twelve templates

All live in [`../_templates/`](../_templates/). Every template carries the standard front-matter
block and the `CG-008` Definition of Done footer.

| # | Template | Governs | Categories | Distinctive sections |
|---:|---|---|---|---|
| 1 | `TPL_Content_File_Front_Matter.md` | Generic fallback for content types with no dedicated template | `CG`, `VB`, `RF`, parts of `CM`, `MM` | Purpose, scope, audience, content, dependencies, maintenance |
| 2 | `TPL_Master_Data_Specification.md` | A dataset and its loadable counterpart | `MD` (all 48) | Record structure, keys, validation rules, load dependencies, golden source, volumes, sample rows |
| 3 | `TPL_UI_Copy_Pack.md` | Screen-by-screen interface copy | `UI` (all 42) | Terminology bindings, screen copy, field labels, validation messages, character budget, accessibility text |
| 4 | `TPL_Notification_Template.md` | Message templates across channels | `NT` (all 26) | Trigger, channel, variables, EN/BN pair, segment count, failure and fallback, change log |
| 5 | `TPL_Document_Print_Template.md` | Printed and PDF output | `DT` (all 44) | Statutory requirements, layout zones, field mapping, variants, worked example, approval |
| 6 | `TPL_SOP.md` | Standard operating procedures | `SP` (all 34) | Procedure steps, decision points, approval limits, exceptions, manual fallback, controls, SoD, KPIs |
| 7 | `TPL_Knowledge_Article.md` | Technical repair and reference knowledge | `KB` (all 16) | Safety, symptoms, causes, diagnostic procedure, repair procedure, parts, verification, escalation |
| 8 | `TPL_Training_Course_Pack.md` | Role-based course packs | `TR` (all 24) | Learning objectives, module outline, facilitator guide, exercises, assessment, job aids, evaluation |
| 9 | `TPL_Help_Article.md` | Self-service help | `HC` (all 20) | Prerequisites, steps, what happens next, troubleshooting, related |
| 10 | `TPL_Legal_Document.md` | Binding terms, policies and notices | `LG` (all 24) | Approval record, scope and parties, definitions, numbered clauses, liability, data protection, change control |
| 11 | `TPL_Test_Script.md` | Test packs and scripts | `TS` (all 18) | Traceability, preconditions, scripts with expected results, negative cases, bilingual check, exit criteria, sign-off |
| 12 | `TPL_Runbook.md` | Operational procedures for systems | `OP` (all 16) | Health checks, routine operations, failure modes, incident response, manual fallback, backup and recovery, break-glass |

---

## 3. Template selection by category

**Every one of the 452 files has exactly one template.** Where a category has no dedicated
template, the generic template is used with the additions listed.

| Category | Files | Template | Additions required |
|---|---:|---|---|
| `CG` Content Governance | 14 | 1 Generic | Rules table; enforcement section |
| `VB` Voice & brand | 10 | 1 Generic | Examples table (do/do not); application-by-surface table |
| `MD` Master data | 48 | **2 Master Data Specification** | — |
| `UI` UI copy | 42 | **3 UI Copy Pack** | — |
| `NT` Notifications | 26 | **4 Notification Template** | `NT-001`, `NT-003`, `NT-026` use template 1 — they are governance, not templates |
| `DT` Documents & print | 44 | **5 Document Print Template** | `DT-001` uses template 1 — it is the standard, not a document |
| `SP` Process & SOP | 34 | **6 SOP** | `SP-001`–`SP-006` use template 1 — architecture and matrices, not procedures |
| `KB` Knowledge | 16 | **7 Knowledge Article** | `KB-001`, `KB-002`, `KB-015` use template 1 — governance |
| `TR` Training | 24 | **8 Training Course Pack** | `TR-001`–`TR-004` use template 1 — framework, not courses |
| `HC` Help centre | 20 | **9 Help Article** | `HC-001`, `HC-002` use template 1; `HC-017`–`HC-019` use template 1 with an intent-schema section |
| `LG` Legal & compliance | 24 | **10 Legal Document** | `LG-001` uses template 1 — it is a register |
| `BN` Localisation | 18 | Mixed | `BN-001`–`BN-008`, `BN-016`, `BN-018` → template 1. `BN-009`–`BN-013` → template 3. `BN-014` → template 4. `BN-015` → template 5. `BN-017` → template 4 with a recording-direction section |
| `DM` Data migration | 14 | **2 Master Data Specification** | Mapping workbooks add a source-to-target column set. `DM-001`, `DM-003`, `DM-014` → template 1 |
| `TS` Test & acceptance | 18 | **11 Test Script** | `TS-001`, `TS-002`, `TS-018` → template 1 |
| `RP` Reporting & KPI | 16 | 1 Generic | Metric definition table (formula, numerator, denominator, grain, source, owner, baseline, target) |
| `AP` Integration & developer | 12 | 1 Generic | Endpoint/event reference table; error catalogue table |
| `CM` Change & comms | 18 | 1 Generic | Audience, channel, timing, message, call-to-action table |
| `OP` Operations & runbooks | 16 | **12 Runbook** | `OP-001`–`OP-006`, `OP-015`, `OP-016` → template 1 |
| `EO` Ecosystem onboarding | 14 | 1 Generic | Onboarding journey table; document checklist; first-90-days section |
| `MM` Multimedia specs | 12 | 1 Generic | Deliverable specification table (format, dimensions, colour, naming, metadata) |
| `RF` Reference & registers | 12 | 1 Generic | Register table; maintenance procedure |

### 3.1 Coverage reconciliation

| Template | Files governed |
|---|---:|
| 1 Generic | 155 |
| 2 Master Data Specification | 59 |
| 3 UI Copy Pack | 47 |
| 4 Notification Template | 25 |
| 5 Document Print Template | 44 |
| 6 SOP | 28 |
| 7 Knowledge Article | 13 |
| 8 Training Course Pack | 20 |
| 9 Help Article | 15 |
| 10 Legal Document | 23 |
| 11 Test Script | 15 |
| 12 Runbook | 8 |
| **Total** | **452** |

**Observation worth acting on: the generic template governs 155 files — 34% of the set.** That
is more than intended. Five of the additions in §3 are recurring and structured enough to
justify dedicated templates. See §6.

---

## 4. Rules

| # | Rule |
|---|---|
| **TR-01** | Every content file is authored from a template. There is no "no template" option (`CP-09`) |
| **TR-02** | Sections are not removed. A section that does not apply keeps its heading with a one-line reason (`CG-008` U-18) |
| **TR-03** | Sections may be **added** where the content genuinely needs them, and the addition is noted in the file's revision history |
| **TR-04** | Section **order** is fixed. A reviewer moving between files must find the same thing in the same place |
| **TR-05** | Every template carries the standard front-matter block and the `CG-008` Definition of Done footer |
| **TR-06** | Changing a template is a MAJOR change to this register and requires an impact assessment on every file authored from it (`CG-006` §6.2) |
| **TR-07** | A template change does **not** retrospectively invalidate approved files. They conform to the version they were authored against, recorded in their front matter |
| **TR-08** | New templates are added to this register before use, with a category assignment |
| **TR-09** | Templates are not content. They carry the `TPL_` prefix, live only in `_templates/`, and have no content ID |

---

## 5. Template versioning

Templates version with `CG-006` §2 rules.

| Change | Version | Effect on existing files |
|---|---|---|
| A new section is added | MAJOR | Existing approved files continue to conform to their authored version. New files use the new template. Files entering MAJOR revision adopt it |
| A section is removed or reordered | MAJOR | Impact assessment required across every file authored from it |
| Guidance text inside a section is clarified | MINOR | No effect |
| A typo is fixed | MINOR | No effect |

Files record which template version they were authored against:

```yaml
template: TPL_SOP.md
template_version: 1.0
```

> **`TR-07` matters more than it looks.** Without it, every template improvement would invalidate
> hundreds of approved files and the templates would ossify. With it, templates can improve
> continuously and files adopt improvements at their next MAJOR revision.

---

## 6. Gaps and planned additions

| # | Proposed template | Would govern | Currently uses | Priority |
|---|---|---|---|:--:|
| 13 | `TPL_Metric_Definition.md` | The 16 `RP` files | Generic + additions | P1 |
| 14 | `TPL_Terminology_Register.md` | `CG-004`, `BN-003`, `BN-004`, `RF-001` — 4 files currently generic | Generic | P2 |
| 15 | `TPL_Onboarding_Kit.md` | The 14 `EO` files | Generic + additions | P2 |
| 16 | `TPL_Communication_Kit.md` | The 18 `CM` files | Generic + additions | P2 |
| 17 | `TPL_Asset_Specification.md` | The 12 `MM` files | Generic + additions | P3 |

Adding these five would move **64 files** off the generic template, reducing its coverage from
155 files (34%) to **91 files (20%)** — a reasonable share for genuinely one-off governance
documents.

> `MD-026` and `MD-027` are also terminology registers in substance, but they are governed by
> template 2 because their loadable data counterpart matters more than their register shape.
> They are not counted in the 64.

**Recommendation:** add template 13 before `RP` authoring begins in W4, and templates 14–17
before their categories are authored. Tracked in `RF-007` Content Backlog.

---

## 7. Template maintenance

| Activity | Frequency | Owner |
|---|---|---|
| Review template fitness against defects found in review | Every wave boundary | Content Design Lead |
| Add sections that reviewers repeatedly ask for | As identified | Content Design Lead |
| Retire a template with no files | On the category's retirement | Programme Content Lead |
| Verify every category has a template assignment | Every wave audit | Programme Content Lead |
| Verify `_templates/` contents match this register | Every wave audit | Programme Content Lead |

**Feedback loop.** When a gate reviewer (`CG-007`) rejects a file for a structural reason that
the template did not prompt, that is a template defect, not only a file defect. It is logged and
the template is amended.

---

## 8. Enforcement

| Check | Mechanism |
|---|---|
| A file declares a template and it exists | Automated — front matter `template:` resolves to a file in `_templates/` |
| Section headings match the declared template | Automated — heading extraction and comparison (`CG-008` §6) |
| No section removed | Automated |
| Section order preserved | Automated |
| Added sections noted in revision history | Manual, at gate G1 |
| The register matches `_templates/` on disk | Wave audit, `AUDIT_Checklist_Recurring.md` §D |
| Every category has a template assignment | Wave audit |

---

## 9. Related documents

| Document | Relationship |
|---|---|
| [`../_templates/`](../_templates/) | The templates themselves |
| [`CG-008_Content_Definition_of_Done_and_QA_Checklist.md`](CG-008_Content_Definition_of_Done_and_QA_Checklist.md) | U-17 and U-18, which this register makes checkable |
| [`CG-003_ERP_Product_Content_Style_Guide.md`](CG-003_ERP_Product_Content_Style_Guide.md) | Mechanics inside the structure templates provide |
| [`CG-006_Content_Lifecycle_and_Versioning_Policy.md`](CG-006_Content_Lifecycle_and_Versioning_Policy.md) | Template versioning follows the same rules |
| [`CG-005_Content_ID_and_Naming_Convention.md`](CG-005_Content_ID_and_Naming_Convention.md) | The `TPL_` reserved prefix |
| `RF-007` Content Backlog Register | Where the five proposed templates are tracked |
| `03_Modules/_MODULE_TEMPLATE.md` | The precedent |

---

## 10. Revision history

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue. Twelve templates registered, template assignment for all 21 categories reconciling to 452 files, nine rules, versioning with the `TR-07` non-retrospection rule, five proposed additional templates | Programme Content Lead (pending) |

---

## Definition of Done

- [x] Front matter complete
- [x] All twelve templates on disk are registered, verified by enumeration 2026-08-15
- [x] Every one of the 21 categories has a template assignment
- [x] Coverage reconciles to 452
- [x] The 32% generic-template coverage is identified as a gap rather than accepted silently
- [x] Template versioning does not retrospectively invalidate approved files
- [x] All internal links resolve
- [x] Bengali counterpart — n/a
- [ ] Named approver recorded — **pending**
- [x] Registered in the Content Master Index

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
