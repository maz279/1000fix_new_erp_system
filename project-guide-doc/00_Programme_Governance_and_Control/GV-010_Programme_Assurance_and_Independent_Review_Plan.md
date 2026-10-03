---
id: GV-010
title: Programme Assurance & Independent Review Plan
category: 00 — Programme Governance & Control
code: GV
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-18
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Chair of the Audit Committee
approver: Board of Directors
standards_basis: ISO 21502:2020 §6.5 assurance · IIA Three Lines Model (2020) · UK IPA / OGC Gateway Review practice · ISO 19011:2018 auditing management systems · ISO 9001:2015 §9.2 internal audit · PRINCE2 7th Edition (2023) project assurance
traces_to: PGD-000 GV-010 · AUDIT-019 ("1 critical, against the auditor's own authoring") · PGD-AUDIT-001 §12 ("Not independent") and R-07 · AF-17 · GV-001 CC-08
depends_on: GV-001, GV-002
verified_on: 2026-08-18
enumerated_on: 2026-08-18 02:06 (+06)
priority: P1
needed_by: W1
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# GV-010 — Programme Assurance & Independent Review Plan
# 1000FiX ERP System & Portal Suite v2.0

### Category 00 · Code `GV` · IIA Three Lines Model · ISO 19011:2018 · IPA Gateway practice

---

> **Twenty-nine audit reports have been produced across this estate. Not one was independent.**
>
> `PGD-AUDIT-001` §12 declares it plainly: *"Not independent. This audit was performed by the
> function that authored the register, and `PGD-A1-13` records that it consequently missed its own
> arithmetic error twice."* `AUDIT-019` recorded *"1 critical, against the auditor's own
> authoring."* Recommendation `R-07` asks for this to be corrected.
>
> **The audit culture here is genuinely excellent — it is the reason this repository exists.** The
> problem is not diligence. It is that a function checking its own arithmetic missed the same error
> four times across four documents, which is what structural non-independence produces regardless
> of how careful anyone is.

---

## 1. Purpose

This plan establishes independent assurance for the 1000FiX ERP programme: what is assured, by
whom, at what points, to what standard, and to whom the result is reported.

It exists because the programme has extensive assurance *activity* and no assurance
*independence*. Nine repository and category audits in the module estate, nineteen in the content
estate and one in the guiding-document estate — twenty-nine reports, 69 findings in the four
repository-level audits alone — every one produced by the function that authored the material
being examined.

### 1.1 Scope

**In scope:**

| # | Covered |
|---|---|
| 1 | The assurance model — three lines, and where each sits in `GV-002` |
| 2 | The definition of independence, and the current position measured against it |
| 3 | Assurance types: delivery confidence, technical, security, data protection, financial, quality |
| 4 | The assurance schedule across the nine waves |
| 5 | Reviewer competency, appointment and independence declaration |
| 6 | Findings management: severity, ownership, ageing, closure authority, recurrence |
| 7 | The delivery-confidence assessment and its rating scale |
| 8 | Assurance coverage gaps — including six module categories never audited |
| 9 | Cost and resourcing |

**Explicitly out of scope:**

| Topic | Owned by | Why the boundary sits here |
|---|---|---|
| Governance body constitution | `GV-002` §4.3 | The Audit Committee is constituted there; resourced here |
| Wave gate criteria and evidence | `GV-009` | Assurance *reviews* the gate; it does not set the criteria |
| Testing and quality engineering | `QA-001`…`QA-011` | Testing is a **second-line** control; assurance is third-line |
| Security testing and penetration testing | `SC-009` | A specialist assurance activity commissioned under §4.3 |
| Financial audit of the Company | Statutory audit | This plan covers programme assurance only |
| The RAID register | `GV-005` | Assurance findings that are live problems become `ISS-nnn` there |

### 1.2 Intended audience

| Audience | What they use this plan for |
|---|---|
| **Board** | The assurance they receive, and the confidence rating it produces |
| **Audit Committee chair** | Their operating plan. This document's owner |
| **CTO / Programme Director** | What will be reviewed, when, and what they must make available |
| **External reviewers** | Their terms of engagement and independence obligations |
| **Steering Committee** | Which gates cannot be signed without an assurance opinion |

---

## 2. Basis and Inputs

### 2.1 Standards conformance

| Standard | Concept | How this plan conforms | Departure |
|---|---|---|---|
| **IIA Three Lines Model (2020)** | First line owns and manages risk; second line provides expertise and monitoring; third line provides independent assurance to the governing body | §3.1 places every existing assurance activity in a line, and shows that the **third line is empty** | The 2020 revision drops the "defence" framing; adopted as stated |
| **ISO 21502:2020** §6.5 | Assurance: independent of the delivery organisation; reports to the sponsor or governing body | §3.3 reporting line; §5 independence rules | None |
| **ISO 19011:2018** | Auditing management systems: audit programme, competence, objectivity, evidence-based approach | §5 competency and appointment; §6 evidence rules | Applied to programme assurance, not only to management-system audit |
| **ISO 9001:2015** §9.2 | Internal audit: *"auditors shall not audit their own work"* | §3.2 measures the current position against exactly this clause | **The Company is ISO 9001:2015 certified. §3.2 is therefore a certification exposure, not only a governance preference** |
| **UK IPA / OGC Gateway Review** | Independent panel review at prescribed lifecycle points; delivery-confidence assessment; a report to the SRO | §4.2 schedule; §7 delivery-confidence rating | Adapted: reviews are placed at wave gates rather than at the Gateway 0–5 lifecycle points |
| **PRINCE2 7th Edition (2023)** | Project assurance is a Project Board responsibility, independent of the Project Manager | §3.3 | None |

### 2.2 Source material relied on

| Source | Location | What it establishes |
|---|---|---|
| Documentation Audit Report | `../../1000fix_ERP_Module/00_Governance_and_Charter/00-06` | 24 findings — 5 critical, 6 high, 9 medium, 4 low |
| Category H & Repository Integrity Audit | `../../1000fix_ERP_Module/00_Governance_and_Charter/00-07` | 14 findings — 3 critical, 5 high, 4 medium, 2 low. **Reports two findings against edits made in its own session** |
| Content & Repository Integrity Audit | `../../project_content/_AUDIT/AUDIT-001` | 18 findings — 4 critical, 6 high, 5 medium, 3 low. `AF-17`: six of eleven module categories have never had a category audit |
| Register Integrity Audit | `../_AUDIT/PGD-AUDIT-001` | 13 findings — 2 critical, 4 high, 5 medium, 2 low. **§12 declares itself non-independent**; `R-07` |
| Category audits `AUDIT-002` … `AUDIT-019` | `../../project_content/_AUDIT/` | 18 category-level content audits |
| Category audits — module estate | `../../1000fix_ERP_Module/03_Modules/` | 7 category-level audits: `_MODULE_SET`, `_CATEGORY_E`, `_F`, `_G`, `_J`, `_K`, `_PORTAL_SUITE` |
| Recurring audit checklist | `../../project_content/_AUDIT/AUDIT_Checklist_Recurring.md` | An existing reusable checklist — a real asset (§8.3) |
| Governance Framework | [`GV-002`](GV-002_Governance_Framework_RACI_and_Terms_of_Reference.md) §4.3, §8 | Constitutes the Audit Committee and the independence rules `GV-002-R5`–`R8` |

### 2.3 Audit findings this document closes

| Finding | Source | How this document closes it |
|---|---|---|
| **`R-07`** | `PGD-AUDIT-001` | *"Commission independent assurance (`GV-010`). Four audits have now been produced by the same function that authored the material."* §4 schedules it; §5 defines independence; §9 costs it |
| `AUDIT-019` observation | `AUDIT-019` | *"1 critical, against the auditor's own authoring."* §5.2 makes self-audit a declared breach with a required disclosure |
| `AF-17` | `AUDIT-001` | §8.1 records the six unaudited module categories and schedules them |
| `R-06` | `PGD-AUDIT-001` | *"Audit this repository at every wave gate under `PG-M7`."* §4.2 |
| `R-09` | `AUDIT-001` | *"Run a category-level audit for Categories A, B, C, D, H and I, which have never had one — before the charter is approved."* §8.1 |
| `GV-001` `CC-08` | `GV-001` | The charter condition this document discharges |
| `RSK-042` | `GV-005` | Assurance is not independent — this plan is the treatment |

---

## 3. The Assurance Model

### 3.1 Three lines

| Line | Role | In this programme | Status |
|:--:|---|---|---|
| **First** | Owns and manages risk in the work itself | Delivery squads; module and content authors; business owners | ✅ Operating |
| **Second** | Expertise, monitoring, challenge — still management | PMO · Architecture Review Board · QA function · Security Lead · Data Protection Forum · Content Council | ◐ Partly constituted; **Security Lead and Service Manager are vacant** (`GV-009` §5.3) |
| **Third** | **Independent assurance to the governing body** | Audit Committee, with internal and external reviewers | ⛔ **Empty.** Twenty-nine reports, none from the third line |

> **All twenty-nine existing audit reports are second-line activity presented as third-line
> assurance.** They are good second-line activity — thorough, self-critical, evidence-based, and
> they found real defects including several against their own authors. But second-line work cannot
> discharge the governing body's need for independent assurance, and `PGD-A1-13` is the proof: the
> same arithmetic defect was raised, remediated, and then committed again *within the remediation*,
> because the only reviewer was the author.

### 3.2 Independence, measured

| ISO 9001:2015 §9.2 requirement | Current position |
|---|---|
| *"Auditors shall not audit their own work"* | **Breached on 29 of 29 reports** |
| Objectivity and impartiality of the audit process | Not evidenced; three reports disclose the breach, twenty-six do not |
| Audit programme defined, with frequency, methods, responsibilities and reporting | **Does not exist.** Audits have been commissioned ad hoc as a condition of issuing other documents |
| Results reported to relevant management | ✅ Reported |
| Results reported to a governing body independent of management | **No such body existed until `GV-002` §4.3** |

> **This is an ISO 9001:2015 certification exposure**, not only a governance weakness. `CON-11`
> requires the certification to be maintained throughout the programme, and `KPI-067` targets zero
> major non-conformances. An internal audit programme that does not satisfy §9.2 is a finding
> waiting for the next surveillance audit.

### 3.3 Reporting line

```
  BOARD OF DIRECTORS
        ▲
        │  assurance opinion · delivery confidence rating · escalation
        │
  AUDIT COMMITTEE  ◄── owns this plan; decides finding closure and reviewer independence
        ▲
        │  reports
        │
  ┌─────┴──────────────────────────────┬─────────────────────────────┐
  │                                    │                             │
  INTERNAL REVIEWER              EXTERNAL REVIEWER            SPECIALIST REVIEW
  (independent of the             (independent of              (security, tax,
   work reviewed)                  1000FiX)                     data protection)
        │                                │                             │
        └────────────────────────────────┴─────────────────────────────┘
                                    │
                         reviews, does not direct
                                    ▼
                    PROGRAMME DELIVERY (first and second line)
```

> **Rule `AS-01`.** Assurance **never** reports to the CTO, the Programme Director, or any function
> whose work it reviews. `GV-002` `GV-002-R6`.

---

## 4. The Assurance Programme

### 4.1 Assurance types

| Type | Question it answers | Reviewer | Frequency |
|---|---|---|---|
| **A1 Delivery confidence** | Will this programme deliver what it promised, in the time and money available? | Independent panel | Gates 1, 4, 6, 9 + on a tolerance breach |
| **A2 Technical** | Is it built to the architecture, and is it upgradable and maintainable? | Independent architect, external from Gate 4 | Gates 2, 4, 6, 8 |
| **A3 Security** | Is it safe? Threat model, controls, penetration test, vulnerability position | **External specialist** | Gates 1, 4, 7 + annually |
| **A4 Data protection** | Is it lawful under the PDPA 2026? | **External legal/privacy specialist** | **Before Wave 1 architecture is fixed**, then Gates 2, 4 + annually |
| **A5 Financial** | Is the cost baseline sound and is spend controlled? | Internal Audit / external accountant | Gate 4, Gate 7, and before any Board re-authorisation |
| **A6 Quality & documentation** | Do the documents describe the system that exists? | Internal reviewer independent of the authoring function | **Every wave gate** (`PG-M7`) |
| **A7 Commercial** | Is the contract sound, and is the vendor delivering to it? | Procurement / external counsel | Before contract award; Gate 4 |
| **A8 Benefits** | Were the benefits realised? | **External** | **Month 42** — `06-02` §6 already requires this |

### 4.2 The schedule

| Point | Review | Type | Reviewer | Mandatory? |
|---|---|:--:|---|:--:|
| **Now — before charter approval** | **Category audits for A, B, C, D, H, I** — six categories never audited | A6 | Internal, independent of the authoring function | **Yes — `R-09`** |
| **Before Wave 1 architecture is fixed** | **Data residency and PDPA lawful-basis opinion** | A4 | **External legal** | **Yes — `DEP-31`, `D-013`** |
| Before contract award | Commercial and SoW review | A7 | Procurement + counsel | Yes |
| **Gate 1** | Security baseline; documentation currency | A3, A6 | External security; internal reviewer | Yes |
| Gate 2 | Technical architecture conformance; documentation | A2, A6 | Independent architect | Yes |
| Gate 3 | Financial controls and migration reconciliation | A5, A6 | Internal Audit | Yes |
| **Gate 4 — tranche boundary** | **Full delivery-confidence review** + technical + security + data protection + financial + commercial | A1–A7 | **External panel** | **Yes — `GV-001` `CC-08`; `GV-009` `G4-12`** |
| Gate 5 | Documentation; payroll and statutory controls | A5, A6 | Internal Audit | Yes |
| **Gate 6** | Delivery confidence; technical; data-services controls | A1, A2, A3 | External | Yes |
| **Gate 7** | Marketplace VAT and liability validation | A5, A7 | **External tax and legal** | **Yes — `RSK-022`, `DEP-29`, `G7-05`** |
| Gate 8 | Technical; model governance | A2, A6 | Independent architect | Yes |
| **Gate 9** | Delivery confidence; closure readiness | A1, A6 | External | Yes |
| **Month 42** | **Independent benefits audit** | A8 | **External** | **Yes — `06-02` §6; `GV-001` §12.1** |
| Annually | Security and data protection | A3, A4 | External | Yes |
| On a tolerance breach | Delivery confidence | A1 | External | Yes |

**Count**: 13 scheduled review points plus two recurring annual reviews. Counted from the rows
above per `PG-M10`.

### 4.3 Specialist assurance already required elsewhere

These are commissioned by other documents. This plan consolidates them so they are visible as one
programme rather than five unrelated obligations.

| Requirement | Source | Type | Status |
|---|---|:--:|---|
| Legal opinion on split-residency data architecture | `DEP-31`, `D-013` | A4 | ⬜ **6–10 week lead; on the critical path** |
| External tax and legal opinion on the marketplace model | `DEP-29`, `RSK-022`, `G7-05` | A5/A7 | ⬜ W7 − 3 months |
| Significant data fiduciary classification | `DEP-32`, `D-015` | A4 | ⬜ W4 − 3 months |
| Penetration testing and vulnerability management | `SC-009` ⛔ | A3 | ⬜ No regime defined anywhere |
| Accessibility conformance review | `UX-005`, `QA-008` | A6 | ⬜ **No accessibility reviewer exists** — `TS-016` cannot be executed |
| Independent benefits audit at Month 42 | `06-02` §6 | A8 | ⬜ Not funded (`GV-008` `Q-04`) |
| Media sanitisation programme conformance to IEEE 2883 | `DEP-35`, `H-01` | A6 | ⬜ W6 − 2 months |

---

## 5. Reviewers

### 5.1 Independence classes

| Class | Definition | Sufficient for |
|:--:|---|---|
| **I0 — none** | The reviewer authored, managed or approved the work | **Nothing.** May be recorded as a self-review, never as assurance |
| **I1 — functional** | Independent of the specific work, inside the same function | A6 documentation reviews before Gate 4 |
| **I2 — organisational** | Independent of the delivery organisation; reports to the Audit Committee | A2, A5, A6 from Gate 4 |
| **I3 — external** | Outside 1000FiX, with no commercial interest in the outcome | **A1, A3, A4, A7, A8 — always** |

> All 29 existing reports are **I0**.

### 5.2 Appointment and declaration

| Rule | Provision |
|---|---|
| `AS-02` | The Audit Committee appoints every reviewer and records the independence class (`GV-002` §5.2 row 30) |
| `AS-03` | **Every report carries an independence statement** naming the class and any relationship to the work. `PGD-AUDIT-001` §12 does this correctly and is the template |
| `AS-04` | A reviewer at class **I0** may not issue an assurance opinion. They may issue a **self-review**, which must be labelled as such and which does not discharge a gate requirement |
| `AS-05` | The implementation vendor may not assure its own deliverables at any class |
| `AS-06` | A reviewer who becomes involved in remediation loses independence for that subject and is replaced |

### 5.3 Competency

Per ISO 19011:2018, competence is assessed against the subject and the audit method, not against
seniority.

| Review type | Required competence |
|---|---|
| A1 Delivery confidence | Programme delivery at comparable scale; benefits realisation; ERP implementation experience |
| A2 Technical | Odoo architecture; the five-stack estate; upgrade and extension patterns |
| A3 Security | Application and infrastructure security; threat modelling; penetration testing certification |
| A4 Data protection | **Bangladesh PDPA 2026**; cross-border transfer; DPIA practice |
| A5 Financial | Bangladesh NBR and VAT; ERP financial controls; migration reconciliation |
| A6 Quality & documentation | ISO 19011 audit method; the estate's identifier and register conventions |
| A7 Commercial | ERP procurement; software contracting; SoW and acceptance regimes |

> **`AS-07` — competence is declared, not assumed.** Each report states the reviewer's competence
> basis. The absence of an accessibility reviewer (`TS-016`) is what happens when competence is
> assumed to exist somewhere in the organisation.

---

## 6. Findings Management

### 6.1 Severity

| Severity | Definition | Closure authority | Target |
|---|---|---|---|
| **Critical** | Would cause an incorrect decision, a legal exposure, or a build against the wrong specification | **Audit Committee** | 2 weeks |
| **High** | Materially misleading or missing; would be caught in build but at cost | Audit Committee | 6 weeks |
| **Medium** | Inaccurate or incomplete; degrades trust in the artefact set | Steering Committee | Next wave gate |
| **Low** | Cosmetic or precision improvement | PMO | Next wave gate, or accept |

*(Definitions carried from `00-06` §2, which already states them well.)*

### 6.2 Rules

| Rule | Provision |
|---|---|
| `AS-08` | **A finding is closed by the Audit Committee, never by its owner.** `GV-002` §5.2 row 29 |
| `AS-09` | A finding closed by **acceptance** records who accepted it and why. `PGD-A1-12` does this correctly |
| `AS-10` | A finding **referred** rather than fixed names the recipient and the required action. `PGD-A1-10` does this correctly |
| `AS-11` | **Recurrence is tracked.** A finding of the same class recurring across audits is escalated as a *control* failure, not re-raised as an instance |
| `AS-12` | Findings ageing is reported to the Audit Committee quarterly and to the Steering Committee monthly |
| `AS-13` | **An audit's own findings arithmetic is regenerated from its finding sections before issue** (`PG-M10`). `PGD-A1-13` exists because this was not done |

### 6.3 The current findings position

Counted from the four repository-level audits at 2026-08-18 02:06, per `PG-M10`.

| Audit | Critical | High | Medium | Low | Total | Closed | Open |
|---|---:|---:|---:|---:|---:|---:|---:|
| `00-06` Documentation Audit | 5 | 6 | 9 | 4 | **24** | *in progress* | *not stated* |
| `00-07` Category H & Repository Integrity | 3 | 5 | 4 | 2 | **14** | 3 | 11 |
| `AUDIT-001` Content & Repository Integrity | 4 | 6 | 5 | 3 | **18** | 9 | 9 |
| `PGD-AUDIT-001` Register Integrity | 2 | 4 | 5 | 2 | **13** | 11 | 2 |
| **Total** | **14** | **21** | **23** | **11** | **69** | | |

**Verification**: 14 + 21 + 23 + 11 = **69** ✓; 24 + 14 + 18 + 13 = **69** ✓.

Plus **25 category-level audits** — 7 in the module estate, 18 in the content estate — whose
findings are not consolidated anywhere.

> **`00-06` does not state a closed/open split.** Its §8 remediation plan marks items *"In
> progress"* or *"Planned"* against eleven groups, which is not a per-finding status. **Twenty-four
> findings, including five critical, have no individual closure status six days after issue.**
> Recorded as finding `PGD-A2-14`.

### 6.4 Recurrence — the control that matters most

`AS-11` exists because of this pattern:

| Defect class | Occurrences | Where |
|---|---:|---|
| **A summary written before the thing it summarises was finished, then never recounted** | **4** | `H2-01` · `AF-02`/`AF-03` · `PGD-A1-02` · `PGD-A1-13` |
| **A register denying work that exists** | **3** | `C-02` (M31) · `H2-01` (44 specs) · `AF-03` (M66, M67) |
| **Identifier collision in a shared space** | **5** | `C-03` · `H-03` · `H2-04` · `H2-05` · `PGD-A1-01` |
| **Baseline movement during authoring** | **3** | `AUDIT-016` `AP-17` · `PGD-A1-03` · **this session, 2026-08-18 02:06** |
| **A stale statutory or standards citation** | **3** | `C-04` · `H-01` · `M-01` |

> **Five defect classes, eighteen instances, four repositories, five months.** Each was remediated
> as an instance; none was closed as a class until mechanical controls were published (`RG-06`,
> `RG-07`, `PG-M9`, `PG-M10`, `PG-M11`). **The recurrence table is the single most useful thing
> this plan produces**, because it identifies which controls to test rather than which documents to
> re-read.

---

## 7. Delivery Confidence

Adapted from IPA Gateway practice. Issued at Gates 1, 4, 6 and 9 and on any tolerance breach.

| Rating | Definition |
|:--:|---|
| 🟢 **Green** | Successful delivery appears highly likely. No major outstanding issues threaten delivery |
| 🟡 **Amber/Green** | Successful delivery probable. Constructive action will address the issues |
| 🟠 **Amber** | Successful delivery feasible. Significant issues exist requiring management attention |
| 🔴 **Amber/Red** | Successful delivery in doubt. Major risks or issues need urgent action |
| ⚫ **Red** | Successful delivery appears unachievable. Issues are not being managed |

### 7.1 Assessment against the current position

A provisional assessment, issued so the first independent review has a baseline to test rather
than a blank page. **This is a self-assessment at class I0 and is labelled as such under `AS-04`.**

| Dimension | Position | Rating |
|---|---|:--:|
| **Governance** | No constituted body; 24 decisions open, **0 taken** | 🔴 |
| **Scope** | Baselined for the first time today; 56 modules of uncontrolled change | 🟠 |
| **Schedule** | Capacity check failed: W1 at 5.33×; 763 PW unscheduled | 🔴 |
| **Cost** | Restated at 2.2×–3.3× the held figure; `D-014` open | 🔴 |
| **Requirements** | 2,996 requirements, **zero** design specifications | 🔴 |
| **Technical** | No SAD, no schema, no API contracts, no machine-readable artefact of any kind | 🔴 |
| **Security & privacy** | Zero occurrences of "threat model"; no DPIA; enforcement inside W4 | 🔴 |
| **Data** | 48 legacy sources, **all unprofiled** | 🔴 |
| **Content** | 477 files, strong quality, unbudgeted | 🟡 |
| **Specification depth** | 67 modules + 12 portals to a consistent 19-section template | 🟢 |
| **Assurance** | 29 reports, 0 independent | 🔴 |
| **Overall** | | **🔴 Amber/Red** |

> **Amber/Red, not Red.** *"Successful delivery in doubt; major risks need urgent action"* is the
> accurate reading. It is not Red because the issues **are** being managed — the audit culture
> found nearly all of them, the specification depth is genuinely strong, and every red dimension
> has a named remediation with an owner in Category 00. It is not Amber because eight of eleven
> dimensions are red and four of them block Wave 1.
>
> **The rating is expected to improve sharply once `D-001`, `D-013` and `D-014` are taken.** Three
> decisions move governance, cost and technical simultaneously.

---

## 8. Coverage Gaps

### 8.1 Never audited

| Subject | Status | Action |
|---|---|---|
| **Module categories A, B, C, D, H, I** | **Never had a category-level audit** (`AF-17`) | `R-09`: audit before charter approval. Six categories, 37 modules |
| Portal suite `P01`–`P12` | One audit (`_PORTAL_SUITE_AUDIT_REPORT`) | Re-audit at Gate 2 |
| `primary-doc/` — BRD, RFP, URD, Technology Stack | **Never audited** — 1.26 MB, the top of the traceability chain | Audit before the SRS is derived from them |
| `old-primary-doc/` | Never audited | Low priority; historical |
| **This repository's Category 00** | Audited at issue by `PGD-AUDIT-002` — **at class I0** | Independent re-review at Gate 1 |
| Infrastructure and environments | Nothing exists to audit | After `PE-001`–`PE-009` |

### 8.2 Never assured, by type

| Type | Coverage |
|---|---|
| A1 Delivery confidence | **Never performed.** §7.1 is the first, and it is a self-assessment |
| A2 Technical | **Never performed** |
| A3 Security | **Never performed.** Zero occurrences of "threat model" or "STRIDE" in 610 files |
| A4 Data protection | **Never performed.** No DPIA exists |
| A5 Financial | **Never performed.** Three audits have commented on cost; none has assured it |
| A6 Quality & documentation | ✅ Extensively — 29 reports, all at class I0 |
| A7 Commercial | **Never performed** |
| A8 Benefits | Scheduled for Month 42; unfunded |

> **One of eight assurance types has ever been performed, and it has been performed without
> independence.** That is the position this plan changes.

### 8.3 What is already strong

| Asset | Assessment |
|---|---|
| **The audit culture** | Self-critical to the point of recording findings against its own authors in the same session. `00-07` §2 reports two findings against edits made minutes earlier. This is rare and valuable |
| **`AUDIT_Checklist_Recurring.md`** | A reusable checklist already exists. Independent reviewers should adopt it rather than invent one |
| **Method discipline** | Every audit states its method — structural, arithmetic, external verification, temporal — and `PGD-AUDIT-001` §11 publishes its verification **commands** so the audit is reproducible. That is better than most external assurance |
| **Disclosure** | Three of the four repository audits disclose their own limitations, including non-independence |
| **Balance** | Every audit carries a "what the audit did not find" section. `00-06` §7: *"an audit that reports only faults is not credible"* |

> **This plan adds independence to an assurance practice that is otherwise better than the
> standard it is being measured against.** That should be said plainly, because the recommendation
> to commission external review could otherwise read as a judgement on the people who have been
> doing this work.

---

## 9. Resourcing and Cost

| Review | Frequency | Estimated cost | Funded? |
|---|---|---:|:--:|
| A4 Data protection — legal opinion (`DEP-31`) | Once, urgent | $8K – $15K | `GV-008` §6.3 risk budget |
| A7 Marketplace tax and legal (`DEP-29`) | Once, W7 | $10K – $20K | Risk budget |
| A3 Security — penetration test + review | Gates 1, 4, 7 + annual | $12K – $25K each | ⬜ **Not funded** |
| A1 Delivery confidence — external panel | Gates 1, 4, 6, 9 | $8K – $15K each | ⬜ Not funded |
| A2 Technical — independent architect | Gates 2, 4, 6, 8 | $5K – $10K each | ⬜ Not funded |
| A5 Financial — internal audit | Gates 3, 4, 5, 7 | Internal | ⬜ |
| A6 Quality & documentation | Every gate | Internal, ~10 PD each | ⬜ |
| A8 Benefits audit | Month 42 | $10K – $20K | ⬜ `GV-008` `Q-04` |
| **Total external assurance, 36 months** | | **$110K – $220K** | **~7% of the expected programme cost** |

> **Seven per cent is the price of knowing whether the other 93% is true.** `GV-008` §6.3 funds
> the two urgent opinions from the risk budget; the remainder requires a Board decision under
> `D-022`.

---

## 10. Decisions Recorded

| # | Decision | Options considered | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| `GV-010-D-01` | Whether the existing audits count as assurance | Count them · Reclassify them | **Reclassify as second-line** | ISO 9001:2015 §9.2 and the IIA model are unambiguous. The reports remain valuable and their findings stand | The third line is declared empty, which is the honest position |
| `GV-010-D-02` | When external review becomes mandatory | Every gate · From Gate 4 · Never | **From Gate 4, with A3 and A4 earlier** | Gate 4 is the tranche boundary. Security and data protection cannot wait — enforcement lands inside Wave 4 | `GV-009` `G4-12`; `GV-001` `CC-08` |
| `GV-010-D-03` | Whether to publish a self-assessed delivery confidence rating | Wait for an independent one · Publish, labelled | **Publish at class I0, labelled** | A first independent review with no baseline spends its budget establishing what is already known | §7.1; the first external panel tests a position rather than building one |
| `GV-010-D-04` | Whether to track recurrence as well as instances | Instances only · Both | **Both** | Five defect classes account for eighteen instances. Fixing instances has not stopped recurrence | §6.4; `AS-11` |
| `GV-010-D-05` | Whether to say the existing audit practice is good | Report only the gap · Say both | **Say both** | The recommendation is structural, not personal, and a plan that reads as a rebuke will be resisted by the people it needs | §8.3 |

---

## 11. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| `Q-01` | Is there a non-executive director to chair the Audit Committee? Without one, independence is weakened at the top of the chain | Company Secretary | Week 3 | `GV-002` §4.3; every I2 review |
| `Q-02` | Does 1000FiX have an internal audit function, or is A5 wholly external? | CFO | Week 4 | §4.2 Gates 3, 5 |
| `Q-03` | Who audits the six never-audited module categories before charter approval, given that every available reviewer authored some of them? | Audit Cttee chair | **Week 2** | `R-09`; charter approval |
| `Q-04` | Is `$110K–$220K` of external assurance acceptable, or should scope be reduced? | Board | Week 6 | `D-022`; §9 |
| `Q-05` | Who provides accessibility review competence? `TS-016` cannot be executed and `UX-005` and `QA-008` both depend on it | CTO | W2 − 4 wk | Accessibility conformance at every gate |
| `Q-06` | Should the 25 category-level audit reports be consolidated into a single findings register? Their findings are currently unaggregated | PMO | Week 8 | Recurrence analysis; §6.3 |

---

## 12. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| `AC-01` | Independence is defined with classes and the current position is measured against it | §5.1, §3.2 — 29 of 29 at I0 |
| `AC-02` | Every assurance type has a reviewer, a frequency and a competence definition | §4.1, §5.3 — eight types |
| `AC-03` | A schedule exists mapped to the wave gates | §4.2 — 13 points + 2 recurring |
| `AC-04` | Findings closure authority is separated from finding ownership | `AS-08` |
| `AC-05` | Recurrence is tracked as a class, not only as instances | §6.4 — five classes, eighteen instances |
| `AC-06` | The findings position is counted, not quoted | §6.3 verification note |
| `AC-07` | Coverage gaps are stated, including what has never been assured | §8.1, §8.2 |
| `AC-08` | A delivery-confidence rating exists, with its independence class declared | §7.1 — class I0, labelled |
| `AC-09` | Assurance is costed | §9 — $110K–$220K |
| `AC-10` | The strengths of the existing practice are stated, not only the gap | §8.3 |

**Definition of done.** Complete when every criterion is met, the Audit Committee is constituted
and has appointed its first independent reviewer, the six never-audited module categories have been
audited (`R-09`), the `DEP-31` legal opinion is received, and `PGD-000` records `GV-010` as ✅ with
a fresh enumeration timestamp.

---

## 13. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | [`GV-001`](GV-001_Programme_Charter_and_Mandate.md) `CC-08` | The charter condition this plan discharges |
| Upstream | [`GV-002`](GV-002_Governance_Framework_RACI_and_Terms_of_Reference.md) §4.3, §8 | Constitutes the Audit Committee and the independence rules |
| Downstream | [`GV-009`](GV-009_Wave_Gate_and_Phase_Exit_Criteria_Handbook.md) `GA-09`, `G4-12` | Assurance opinions are gate evidence from Gate 4 |
| Downstream | [`GV-005`](GV-005_RAID_Register.md) | Findings that are live problems become `ISS-nnn`; `RSK-042` |
| Downstream | [`GV-008`](GV-008_Programme_Budget_and_Cost_Baseline.md) §6.3 | Funds the two urgent opinions |
| Downstream | `SC-009` | Vulnerability management and penetration testing — the A3 regime |
| Downstream | `SC-003` | DPIA — the A4 subject |
| Downstream | `BM-004` | The Month 42 benefits audit |
| Downstream | `RR-005` | Regulatory currency register — the control behind `SG-10` |
| Lateral | `../../project_content/_AUDIT/AUDIT_Checklist_Recurring.md` | An existing reusable checklist to be adopted, not replaced |

---

## 14. References

**Within this repository**
[`PGD-000`](../PGD-000_Master_Register_of_Project_Guiding_Documents.md) ·
[`PGD-AUDIT-001`](../_AUDIT/PGD-AUDIT-001_Register_Integrity_Audit.md) §12, `R-07` ·
[`PGD-AUDIT-002`](../_AUDIT/PGD-AUDIT-002_Category_00_Governance_Audit.md) ·
[`GV-002`](GV-002_Governance_Framework_RACI_and_Terms_of_Reference.md) · [`GV-009`](GV-009_Wave_Gate_and_Phase_Exit_Criteria_Handbook.md)

**Workspace**
`../../1000fix_ERP_Module/00_Governance_and_Charter/00-06`, `00-07` ·
`../../1000fix_ERP_Module/03_Modules/` — 7 category audit reports ·
`../../project_content/_AUDIT/` — `AUDIT-001` … `AUDIT-019` and `AUDIT_Checklist_Recurring.md`

**External standards** *(all verified 2026-08-18)*

| Source | Used for |
|---|---|
| IIA Three Lines Model (2020) — first line owns risk, second line provides expertise, third line provides independent assurance to the governing body | §3.1 |
| ISO 19011:2018 — audit programme, competence, objectivity, evidence-based approach | §5, §6 |
| ISO 9001:2015 §9.2 — internal audit; auditors shall not audit their own work | §3.2 |
| ISO 21502:2020 §6.5 — assurance independent of the delivery organisation | §3.3 |
| UK IPA / OGC Gateway Review — independent panel review; delivery-confidence rating (Green → Red) | §4.2, §7 |
| PRINCE2 7th Edition (2023) — project assurance is a Project Board responsibility, independent of the Project Manager | §3.3 |

---

## 15. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-18 | Chair of the Audit Committee *(designate)* | Initial issue. **Closes `R-07`.** Establishes the three-lines model and records that the third line is empty — 29 of 29 audit reports at independence class I0. Defines eight assurance types, four independence classes and a 13-point schedule. Counts the findings position at 69 across four repository audits. Identifies five recurring defect classes accounting for eighteen instances. Issues a first delivery-confidence rating of **Amber/Red**, labelled as a class I0 self-assessment. Costs external assurance at $110K–$220K | *pending Board* |

---

*`GV-010` · Category 00 · 1000FiX ERP System v2.0 · CONFIDENTIAL — Internal Use Only*
*1000FiX Services Limited · Hotline 16743 · info@1000fix.com · ISO 9001:2015 Certified*
