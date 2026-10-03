---
id: CG-007
title: Review, Approval and Sign-off Workflow
project: 1000FiX ERP System v2.0
content_type: Standard
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Legal & Compliance
author: Legal & Compliance with Programme Content Lead
reviewers: [Programme Content Lead, CFO delegate, DPO, Quality Manager, Localisation Lead]
approver: ERP Steering Committee
purpose: >
  Defines the review gates each class of content must pass, who signs statutory, legal and brand
  content, and what evidence of sign-off is retained. 61 files carry legal or statutory
  consequence. Sign-off must be recorded, not assumed — the company must be able to prove who
  approved a warranty exclusion, a tax narrative or a consent notice, and on what date.
traces_to: [CG-002 §4, CG-006, CG-008, LG-001, LG-009, M24, ISO 9001:2015 clause 7.5.2]
priority: P1
wave: W0
bilingual: no
bn_counterpart: n/a
sources:
  - source: ISO 9001:2015 clause 7.5.2 — review and approval for suitability and adequacy before release
    verified: 2026-08-15
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06 §6 regulatory obligations, NFR-092/093/100
    verified: 2026-08-15
  - source: 1000fix_ERP_Module/00_Governance_and_Charter/00-04 §5.2 decision rights
    verified: 2026-08-15
  - source: NBR Mushak 9.1 filing obligation — 05-06 NFR-100 (filed by the 15th of the following month)
    verified: 2026-08-15
supersedes: none
review_due: 2027-02-15
---

# CG-007 — Review, Approval and Sign-off Workflow

> **Sign-off is not a formality; it is the evidence.** When a customer disputes a warranty
> exclusion, when the NBR questions an invoice format, when a regulator asks who authorised a
> consent notice, the answer must be a record — a named person, a date, a version — not a
> recollection.

---

## 1. Scope

This file governs the transition from `Review` to `Approved` in `CG-006` §1. It does not govern
drafting quality (`CG-008`) or who does the work (`CG-002`).

| In scope | Out of scope |
|---|---|
| Review gates per content class | Whether the content is well written — `CG-008` |
| Who signs, and with what authority | Who authors — `CG-002` |
| Evidence retained, and where | Where evidence is stored technically — `M24` |
| Service levels for each gate | Escalation when a gate fails — `CG-013` |
| Re-approval triggers | Version numbering — `CG-006` |

---

## 2. Gates

Six gates exist. Which apply depends on the content class from `CG-002` §4.

| Gate | Question it answers | Performed by |
|---|---|---|
| **G1 — Editorial** | Is it clear, consistent, on-style, on-terminology, accessible? | Content Design |
| **G2 — Factual** | Is what it says about the business and the system true? | Domain Content Owner + SME |
| **G3 — Technical** | Does it match what the system actually does, at the pinned release? | Engineering / QA |
| **G4 — Linguistic** | Is the Bengali correct, in register, and correct **in context**? | Independent linguistic reviewer |
| **G5 — Legal** | Is it enforceable, accurate as to obligations, and consistent with our other legal positions? | Legal Counsel |
| **G6 — Statutory** | Does it conform to the enacted instrument, verified against a primary source? | Tax/Compliance + **external verification** |

### 2.1 Gate matrix by content class

| Class | G1 Editorial | G2 Factual | G3 Technical | G4 Linguistic | G5 Legal | G6 Statutory | Final approver |
|:--:|:--:|:--:|:--:|:--:|:--:|:--:|---|
| **A** Statutory | ● | ● | ○ | ◐ | ● | **●** | CFO **or** Legal Counsel |
| **B** Legal | ● | ● | ○ | ◐ | **●** | ○ | Legal Counsel |
| **C** Operational-critical | ● | **●** | ● | ◐ | ○ | ○ | Domain Content Owner |
| **D** User-facing | **●** | ● | ● | ◐ | ○ | ○ | Content Design Lead |
| **E** Internal governance | ● | ● | ○ | ○ | ○ | ○ | Programme Content Lead |

**●** mandatory · **◐** mandatory if `bilingual: yes` · **○** not required, but may be requested

> **G3 applies to Class A and B where the content is system-generated.** A Mushak 6.3 template
> is Class A and statutory, but it is also rendered by the print engine — so it must be verified
> both against the instrument (G6) and against the actual output (G3). Where a Class A or B file
> is pinned under `CG-006` §3, G3 becomes mandatory.

---

## 3. Gate detail

### 3.1 G1 — Editorial

| Item | Check |
|---|---|
| Style | `CG-003` — en-GB, sentence case, second person, active voice, punctuation, numbers |
| Terminology | `CG-004` — approved terms only; no banned synonyms; entity bindings correct |
| Structure | Conforms to its `_templates/` template (`CP-09`) |
| Accessibility | `CG-011` — reading level, link text, alt text, heading hierarchy, error-message structure |
| Clarity | A reader in the target role can act on it without asking a question |

**Service level: 3 working days.** Reviewer: Content Design (not the author).

### 3.2 G2 — Factual

| Item | Check |
|---|---|
| Business accuracy | Every statement about how the business works is true today |
| Evidence | Every factual, statutory, pricing or capability claim names a primary source with a verification date (`CG-012`) |
| Completeness | Nothing material to the reader's task is missing |
| Boundary | Nothing here belongs to another file (`CP-01`) |
| Traceability | `traces_to:` resolves, and the upstream requirement genuinely needs this content (`CP-04`) |

**Service level: 5 working days.** Reviewer: Domain Content Owner, with the SME who holds the
knowledge.

### 3.3 G3 — Technical

| Item | Check |
|---|---|
| Pin | `pinned_to:` names a real release, verified against the build (`CG-006` §3) |
| Fidelity | Every screen, label, field, button and message quoted exists and is spelled identically |
| Behaviour | Described system behaviour matches actual behaviour, including failure paths |
| Identifiers | Every cited `Mnn`, `Pnn`, `FR-`, `NFR-`, `BRU-`, `INT-` exists in its owning register |
| Output | For document templates: the rendered output matches the specification |

**Service level: 5 working days.** Reviewer: the engineering squad owning the surface, or QA.

### 3.4 G4 — Linguistic

Applies to all 266 bilingual files (`CG-010`).

| Item | Check |
|---|---|
| Accuracy | The Bengali says what the English says — no addition, no omission, no softening |
| Register | Matches the register decided in `BN-002` for that surface |
| Terminology | Bengali terms match `BN-003`; do-not-translate items are untranslated (`BN-004`) |
| **In context** | Reviewed **in the actual interface, document or message**, not in a spreadsheet of strings |
| Layout | No truncation, no overflow, no broken conjuncts at the target size (`BN-006`) |
| Formatting | Dates, numbers, currency and addresses follow `BN-007` |

**Service level: 5 working days after the English is approved.** Reviewer: a linguistic reviewer
**independent of the translator** (`CO-05`).

> **In-context review is not optional.** Translation reviewed as a list of strings passes review
> and fails in production — the reviewer cannot see truncation, cannot see which button the
> label sits on, and cannot see that two different English strings were given the same Bengali.
> `BN-018` defines the mechanics.

### 3.5 G5 — Legal

| Item | Check |
|---|---|
| Enforceability | Terms are capable of being enforced under Bangladesh law |
| Accuracy of obligation | What we promise is what we can deliver, and what we disclaim is disclaimable |
| Consistency | No contradiction with other legal content — particularly `LG-008` privacy, `LG-009` retention and `LG-012` residency, which must agree |
| Acceptance | The acceptance-capture mechanism is adequate for the class of term (`LG-019`) |
| Data protection | Any personal-data processing described is lawful, notified and retained per `LG-009` |
| Version control | The version and effective date are recorded in `LG-001` |

**Service level: 10 working days.** Reviewer: Legal Counsel. Escalates to CFO if exceeded
(`CG-002` §7).

### 3.6 G6 — Statutory

The strictest gate. Applies to 41 Class A files.

| Item | Check |
|---|---|
| **Primary source** | The content is verified against the **enacted instrument or the regulator's published form** — never against commentary, press reporting or a vendor's summary |
| Currency | The instrument version cited is the one in force, and the `statutory_pin` records the fiscal year (`CG-006` §4) |
| Completeness | Every mandated element is present and in the mandated position |
| External verification | A named external adviser (tax adviser, legal counsel, or the regulator's own guidance) has confirmed conformance |
| Filing consequence | Where the content feeds a filing, the filing deadline and route are stated — e.g. Mushak 9.1 is filed by the 15th of the following month through the NBR VAT Online portal (`05-06` NFR-100) |
| Retention | The retention period is stated and reconciles to `LG-009` — VAT records are preserved for at least five years |

**Service level: 15 working days**, driven by external adviser availability. Statutory content
is scheduled with this lead time; it is not requested at a wave gate.

> **`00-07` finding H2-13 is the precedent.** Statutory tax figures in the module repository
> rested partly on press reporting rather than the enacted Finance Act. G6 exists so that never
> happens in content.

---

## 4. Sign-off evidence

### 4.1 What is recorded

Every approval records, at minimum:

```yaml
approval:
  version: 1.0
  approver_name: <full name>
  approver_role: <registered role or office>
  date: YYYY-MM-DD
  gates_passed: [G1, G2, G5]
  evidence_ref: <LG-001 row, or M24 document reference>
  external_verification:              # G6 only
    adviser: <firm or named adviser>
    date: YYYY-MM-DD
    scope: <what was verified>
```

### 4.2 Where evidence lives

| Content class | Evidence location | Retention |
|---|---|---|
| **A** Statutory | `LG-001` Legal Content Register **and** `M24` Document, Records & E-Signature | Longer of 5 years or `LG-009` |
| **B** Legal | `LG-001` **and** `M24` | Per `LG-009`; longer where a counterparty accepted the terms |
| **C** Operational-critical | File front matter + `RF-006` decision log | Life of the content plus one wave |
| **D** User-facing | File front matter | Life of the content |
| **E** Internal governance | File front matter | Life of the content |

### 4.3 Evidence rules

| # | Rule |
|---|---|
| **SO-01** | The approver is a **named person**, never a function or a committee alone. Where a committee approves, the record names the chair and the meeting date |
| **SO-02** | The approver is never the author (`CO-04`) |
| **SO-03** | An approval is version-specific. Approving `1.0` approves nothing about `2.0` |
| **SO-04** | An approval that cannot be evidenced did not happen. Content with an unevidenced approval reverts to `Review` |
| **SO-05** | For Class A and B, `LG-001` records **which version each counterparty accepted and when** — this is the record the company relies on in a dispute |
| **SO-06** | Electronic approval is acceptable and preferred. Its evidentiary basis is stated once in `LG-019`, not per file |
| **SO-07** | Verbal approval is not approval |

---

## 5. Bilingual approval

`CM-R6` and `LC-08`: **the pair moves together.**

```
English Draft ──► English Review (G1,G2,G3,G5,G6 as applicable) ──► English Approved
                                                                          │
                                                    translation begins ◄──┘
                                                                          │
                                                                          ▼
                                              Bengali Draft ──► G4 in-context ──► Bengali Approved
                                                                          │
                                                                          ▼
                                                            ┌─────────────────────────┐
                                                            │  PAIR APPROVED          │
                                                            │  Only now may either    │
                                                            │  be published           │
                                                            └─────────────────────────┘
```

| # | Rule |
|---|---|
| **BL-01** | Translation begins only after the English source is `Approved`. Translating a draft wastes the translation twice |
| **BL-02** | Neither file may be `Published` until both are `Approved` |
| **BL-03** | A MAJOR change to the English source returns **both** files to `Review` |
| **BL-04** | A MINOR change to the English source requires the Bengali to be assessed; "assessed, no change required" is recorded |
| **BL-05** | The linguistic reviewer is independent of the translator |

**The practical consequence:** for any bilingual `P0` content, the wave gate is set by the
Bengali sign-off date, not the English one. Plan backwards from the gate by the G4 service level
plus translation time. `CG-002` §7 escalates translation capacity at wave gate minus six weeks
for exactly this reason.

---

## 6. Service levels and queue management

| Gate | Service level | Measured from | Escalates to |
|---|---|---|---|
| G1 Editorial | 3 working days | Submission to `Review` | Content Design Lead |
| G2 Factual | 5 working days | Submission | Domain Content Owner → Business Owners Forum |
| G3 Technical | 5 working days | Submission | Engineering lead → PMO |
| G4 Linguistic | 5 working days | English approval | Localisation Lead → Content Lead |
| G5 Legal | 10 working days | Submission | Legal Counsel → CFO |
| G6 Statutory | 15 working days | Submission | Tax Manager → CFO → Steering |

| # | Rule |
|---|---|
| **SL-01** | Gates run **in parallel where they are independent**. G1 and G2 do not wait for each other |
| **SL-02** | G3 requires a build; it cannot start before the surface exists |
| **SL-03** | G5 and G6 are the constraint on the whole content schedule. **Legal review capacity, not drafting capacity, determines when 61 files can ship** |
| **SL-04** | A gate exceeding its service level escalates automatically (`CO-02`) |
| **SL-05** | Queue depth per gate is reported weekly to the PMO (`CG-002` §8) |
| **SL-06** | A reviewer may reject with reasons; rejection returns the file to `Draft` and restarts the clock on resubmission |

---

## 7. Re-approval triggers

Content that was correctly approved can stop being correct. These triggers return a file to
`Review` regardless of its review date.

| Trigger | Files affected | Gates re-run |
|---|---|---|
| MAJOR version change (`CG-006` §2) | The file | All applicable |
| Statutory instrument change | Every Class A file citing it | G2, G5, G6 |
| A term changes in `CG-004` | Every file citing the term (impact list, `CG-006` §6.2) | G1 |
| A release changes a pinned surface | Every file pinned to it | G3, then G1 if wording changed |
| A legal position changes in `LG-008`, `LG-009` or `LG-012` | Every file that must not contradict them | G5 |
| A business rule changes in `05-05` | Content implementing or explaining it | G2, G3 |
| An audit finding names the file | The named file | As directed by the finding |
| A regulator, brand partner or counterparty challenges the content | The challenged file | G5, and G6 if statutory |
| An incident traces to the content | The implicated file | G2, G3 |
| 12 months pass with no trigger | Class A and B files | G6 or G5 respectively (`CG-006` §4.2) |

---

## 8. Delegation and absence

| Situation | Rule |
|---|---|
| The named approver is unavailable | A pre-registered deputy in `RF-010` may approve. Deputies are registered in advance, never appointed at the moment of need |
| No deputy is registered | The approval waits. **Class A and B never proceed on an unregistered approver** |
| Urgent operational need | Class C and D may be published as `Approved — provisional` with a Content Lead sign-off and a 10-working-day deadline for the full gate. Recorded in `RF-006`. **Classes A and B have no provisional route** |
| The approver is also the author | A second approver of the same class is appointed (`CO-04`) |
| External adviser unavailable within the G6 service level | The statutory file does not ship. The wave gate moves, or the scope moves — the content does not ship unverified |

---

## 9. Waivers

| # | Rule |
|---|---|
| **WV-01** | A gate may be waived only by the Programme Content Lead, time-boxed, with a named remediation date, logged in `RF-006` |
| **WV-02** | **G5 and G6 can never be waived.** There is no authority in this programme to publish unreviewed legal or statutory content |
| **WV-03** | **G4 can never be waived** for customer-facing or field-facing content. `PS-03` and `P02` non-negotiable #3 are contractual |
| **WV-04** | A waived gate is re-run before the next wave gate. An unremediated waiver blocks the wave |
| **WV-05** | Open waivers are reported to the Steering Committee monthly |

---

## 10. The capacity problem, stated plainly

| Class | Files | Gate that constrains | External dependency |
|---|---:|---|---|
| A Statutory | 41 | G6 — 15 working days | External tax/legal adviser |
| B Legal | 34 | G5 — 10 working days | Legal Counsel |
| Bilingual (all classes) | 266 | G4 — 5 working days after English approval | Independent linguistic reviewers |

At one adviser and one counsel working sequentially, 75 Class A and B files consume roughly
**1,000 adviser-days of elapsed time** if serialised — which is not achievable inside a 36-month
programme alongside everything else Legal does.

**Therefore:**

1. Class A and B content is **batched by instrument and by counterparty**, not reviewed
   file-by-file. All Mushak templates go to G6 together; all portal terms go to G5 together.
2. External adviser capacity is **contracted in advance**, per wave, not requested per file.
3. Legal and statutory content is scheduled **first** in every wave, because it has the longest
   lead time and the least tolerance for compression.
4. `CG-002` §9 records this as part of the unfunded content effort (audit finding **AF-09**).

---

## 11. Related documents

| Document | Relationship |
|---|---|
| [`CG-002_Content_Operating_Model_and_RACI.md`](CG-002_Content_Operating_Model_and_RACI.md) | Content classes and RACI per class |
| [`CG-006_Content_Lifecycle_and_Versioning_Policy.md`](CG-006_Content_Lifecycle_and_Versioning_Policy.md) | The states this workflow moves content between |
| [`CG-008_Content_Definition_of_Done_and_QA_Checklist.md`](CG-008_Content_Definition_of_Done_and_QA_Checklist.md) | What must be true before a file enters `Review` |
| [`CG-012_Content_Sourcing_and_Evidence_Rules.md`](CG-012_Content_Sourcing_and_Evidence_Rules.md) | The evidence G2 and G6 test |
| [`CG-013_Content_Risk_and_Legal_Escalation_Rules.md`](CG-013_Content_Risk_and_Legal_Escalation_Rules.md) | What forces content into G5 or G6 unexpectedly |
| `LG-001` Legal Content Register and Sign-off Log | Where Class A and B evidence lives |
| `LG-019` E-Signature Legal Notice and Evidence Statement | The evidentiary basis for electronic approval |
| `BN-018` Localisation QA and Linguistic Sign-off Checklist | The mechanics of G4 |
| `RF-010` Content Ownership and Contact Directory | Registered approvers and deputies |
| `M24` Document, Records & E-Signature | The system that stores approval evidence |

---

## 12. Revision history

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue. Six gates, gate matrix by content class, evidence requirements, bilingual pair approval, service levels, ten re-approval triggers, delegation rules, waiver limits, and the capacity constraint stated | Steering Committee (pending) |

---

## Definition of Done

- [x] Front matter complete
- [x] Six gates defined with checks, reviewers and service levels
- [x] Gate matrix covers all five content classes
- [x] Evidence requirements reconcile to ISO 9001 clause 7.5.2 and to `LG-001`
- [x] Bilingual pair rule stated and its schedule consequence made explicit
- [x] G5 and G6 declared unwaivable
- [x] The capacity constraint stated rather than assumed away
- [x] All internal links resolve
- [x] Bengali counterpart — n/a
- [ ] Named approver recorded — **pending Steering Committee**
- [x] Registered in the Content Master Index

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
