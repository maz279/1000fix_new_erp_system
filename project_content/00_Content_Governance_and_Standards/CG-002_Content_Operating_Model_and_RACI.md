---
id: CG-002
title: Content Operating Model and RACI
project: 1000FiX ERP System v2.0
content_type: Governance
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Programme Content Lead
author: Programme Content Lead
reviewers: [PMO, Enterprise Architecture, Legal & Compliance, Localisation Lead]
approver: ERP Steering Committee
purpose: >
  Names who authors, reviews, approves, translates, publishes and retires each class of content,
  and defines the escalation path. 452 files across 21 categories with no named accountability
  produces orphaned content; this is the ownership gap that caused register drift in the module
  repository (audit 00-07 finding H2-01).
traces_to: [00-04 §5, 02-02 §1, CG-001, CG-007]
priority: P0
wave: W0
bilingual: no
bn_counterpart: n/a
sources:
  - source: 1000fix_ERP_Module/00_Governance_and_Charter/00-04 §5 Governance structure, decision rights, cadence
    verified: 2026-08-15
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-04 Role register (R01–R38)
    verified: 2026-08-15
  - source: project_content/_AUDIT/AUDIT-001 findings AF-04, AF-09
    verified: 2026-08-15
supersedes: none
review_due: 2026-11-15
---

# CG-002 — Content Operating Model and RACI

> **This is the first file the programme must approve.** No content file may reach `Approved`
> status until this operating model is ratified by the ERP Steering Committee. Everything in
> `CG-003` through `CG-014` describes *how* content is made well; this file decides *who is
> accountable when it is not*.

---

## 1. The problem this solves

The module repository has been audited three times. The largest finding in each was the same
class of defect: **work existed that no register knew about, or a register described work that
did not exist.**

| Audit | Finding | Root cause |
|---|---|---|
| `00-06` C-02 | M31 had a specification file and no register entry | No one owned the register at the moment the specification was written |
| `00-07` H2-01 | 44 specifications existed while their register entries denied it | The register's Spec column was updated only for categories being actively worked |
| `AUDIT-001` AF-03 | M66 and M67 declared unwritten; both complete | The same gap, two modules later |

None of these is a writing failure. All three are **ownership** failures — nobody was
accountable for the register between the act of writing and the act of auditing.

At 452 content files across 21 categories, nine waves and 36 months, that gap does not shrink.
It multiplies. This file closes it before the first content file is written.

---

## 2. Where content sits in programme governance

Content is a **workstream**, not a task inside other workstreams. It reports to the PMO and
escalates through the same route as every other workstream (`00-04` §5).

```
                          ┌──────────────────────────────┐
                          │  ERP STEERING COMMITTEE      │
                          │  CEO (chair) · CTO · CFO ·   │
                          │  CCO · Ops Dir · HR Dir ·    │
                          │  Quality Manager             │
                          │  Monthly                     │
                          └──────────────┬───────────────┘
                                         │
        ┌────────────────────────────────┼────────────────────────────┐
        │                                │                            │
┌───────▼────────┐            ┌──────────▼────────┐        ┌──────────▼─────────┐
│ PROGRAMME      │            │ ARCHITECTURE      │        │ BUSINESS OWNERS    │
│ MANAGEMENT     │            │ REVIEW BOARD      │        │ FORUM              │
│ OFFICE         │            │ Fortnightly       │        │ Fortnightly        │
└───────┬────────┘            └───────────────────┘        └────────────────────┘
        │
┌───────▼──────────────────────────────────────────────────────────────────────┐
│  CONTENT WORKSTREAM  ◄── new; not present in 00-04 (audit finding AF-09, R-07)│
│  Programme Content Lead                                                       │
│  ├── Content Design            (UI copy, help, notifications, style)          │
│  ├── Localisation              (Bengali, terminology, linguistic QA)          │
│  ├── Master Data & Config      (the 48 MD files — with MDM and business SMEs) │
│  ├── Process & Training        (SOPs, courses, job aids — with L&D)           │
│  ├── Legal & Compliance Content(24 LG files, 26 statutory DT files)           │
│  └── Technical Content         (API, runbooks, knowledge — with engineering)  │
└──────────────────────────────────────────────────────────────────────────────┘
```

> **Constitutional gap.** `00-04` §5 does not contain a content workstream, and `06-01` does not
> schedule content work. Both must be amended. Until they are, the Content Lead has
> accountability without a governance seat — recorded as audit finding **AF-09**, recommendation
> **R-07**.

---

## 3. Roles

Roles are **functions, not headcount**. One person may hold several on a small category; no
function may be unassigned on any category.

| Role | Accountable for | Maps to `05-04` role |
|---|---|---|
| **Programme Content Lead** | The register, the operating model, the schedule, the effort forecast, escalation | New — to be registered |
| **Content Design Lead** | `CG-003` style, `VB` voice, `UI` copy, `NT` notifications, `HC` help | New — to be registered |
| **Localisation Lead** | `CG-010` bilingual policy, all `BN` content, linguistic sign-off on 266 bilingual files | New — to be registered |
| **Master Data Owner** | The 48 `MD` files, load sequencing, `MD-001` stewardship charter | `M64` MDM Lead |
| **Domain Content Owner** | One per business category: the SOPs, training, documents and rules for their domain | Business Owners Forum member (17 module owners) |
| **Author** | Producing a file to template, on schedule, with evidence | Varies |
| **Reviewer** | Technical, business, linguistic or legal correctness within their competence | Varies |
| **Approver** | Signing that the file may be used. Carries the consequence if it is wrong | Per content class — see §5 |
| **Translator** | Producing the Bengali counterpart. Professional translator; never machine translation on customer- or field-facing content | External or in-house, per `CG-010` |
| **Linguistic Reviewer** | In-context Bengali review and sign-off (`BN-018`) | Independent of the translator |
| **Publisher** | Moving `Approved` content into the build, the LMS, the print engine or the portal | Platform Engineering / L&D |
| **Content Steward** | Keeping a category current after go-live: review dates, retirement, currency | Domain Content Owner |

> **Rule CO-01 — no unassigned function.** A category with no named Domain Content Owner does
> not enter production. The register row's "Owner" column names the accountable *function*;
> `RF-010` names the accountable *person*. Both must be populated.

---

## 4. Content classes

Accountability scales with consequence. Every content file is assigned exactly one class, and
the class determines its review path, its approver and its audit treatment.

| Class | Name | Consequence if wrong | Files | Approver |
|:--:|---|---|---:|---|
| **A** | **Statutory** | Regulatory penalty, invalid filing, unlawful invoice | 41 | CFO or Legal Counsel + external verification |
| **B** | **Legal / contractual** | Unenforceable term, liability exposure, contractual dispute | 34 | Legal Counsel |
| **C** | **Operational-critical** | Wrong transaction, wrong dispatch, wrong stock, wrong pay | 118 | Domain Content Owner + Business Owners Forum |
| **D** | **User-facing** | Confusion, support load, abandonment, poor adoption | 174 | Content Design Lead |
| **E** | **Internal governance** | Inconsistency, rework, unmaintainable content | 85 | Programme Content Lead |
| | | **Total** | **452** | |

> Counts are derived from §4.1, which is the authoritative allocation. If the two ever diverge,
> §4.1 governs and this summary is corrected — never the reverse.

### 4.1 Class assignment by category

| Category | A | B | C | D | E | Total |
|---|---:|---:|---:|---:|---:|---:|
| `CG` Governance | 0 | 0 | 0 | 0 | 14 | 14 |
| `VB` Voice & brand | 0 | 0 | 0 | 6 | 4 | 10 |
| `MD` Master data | 3 | 2 | 40 | 0 | 3 | 48 |
| `UI` UI copy | 1 | 1 | 6 | 34 | 0 | 42 |
| `NT` Notifications | 1 | 2 | 5 | 15 | 3 | 26 |
| `DT` Documents | 26 | 6 | 10 | 1 | 1 | 44 |
| `SP` Process & SOP | 2 | 1 | 28 | 0 | 3 | 34 |
| `KB` Knowledge | 1 | 0 | 12 | 1 | 2 | 16 |
| `TR` Training | 0 | 0 | 4 | 16 | 4 | 24 |
| `HC` Help centre | 0 | 1 | 0 | 17 | 2 | 20 |
| `LG` Legal | 6 | 18 | 0 | 0 | 0 | 24 |
| `BN` Localisation | 0 | 0 | 2 | 12 | 4 | 18 |
| `DM` Data migration | 0 | 0 | 11 | 0 | 3 | 14 |
| `TS` Test & acceptance | 0 | 0 | 0 | 4 | 14 | 18 |
| `RP` Reporting & KPI | 1 | 0 | 0 | 10 | 5 | 16 |
| `AP` Integration | 0 | 1 | 0 | 9 | 2 | 12 |
| `CM` Change & comms | 0 | 0 | 0 | 16 | 2 | 18 |
| `OP` Operations | 0 | 0 | 0 | 11 | 5 | 16 |
| `EO` Ecosystem | 0 | 2 | 0 | 10 | 2 | 14 |
| `MM` Multimedia specs | 0 | 0 | 0 | 12 | 0 | 12 |
| `RF` Reference | 0 | 0 | 0 | 0 | 12 | 12 |
| **Total** | **41** | **34** | **118** | **174** | **85** | **452** |

> **Reconciliation note.** Class A+B = **75** files touching statutory or legal ground. The
> Master Index §1 states **61 files requiring legal or statutory sign-off** — that figure counts
> files where sign-off is the *gating* control. The additional 14 are files that are legally
> *informed* but signed by their domain owner (for example `MD-028` SLA definitions, which Legal
> reviews but Service Operations approves). Both figures are correct against their own
> definition; the difference is stated here so it is not read as a contradiction.

---

## 5. RACI by content class

**R** = Responsible (does the work) · **A** = Accountable (one only; carries the consequence) ·
**C** = Consulted (before) · **I** = Informed (after)

### 5.1 Class A — Statutory

| Activity | Author | Domain Owner | Content Lead | Legal | CFO / Tax | External verifier | Steering |
|---|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| Draft | **R** | C | I | C | C | — | — |
| Verify against the instrument | R | — | — | C | C | **R** | — |
| Legal review | — | — | I | **R** | C | — | — |
| Approve | — | C | I | **A** | **A** | — | I |
| Translate | R | — | C | C | — | — | — |
| Publish | R | I | **A** | I | I | — | — |
| Currency review (annual, or on statutory change) | R | — | C | **A** | C | R | I |
| Retire | — | C | R | **A** | C | — | I |

> Class A files cite the enacted instrument, not commentary on it (`CG-012`). A Finance Act
> change re-opens every Class A tax file automatically — see `CG-006` §5 statutory pinning.

### 5.2 Class B — Legal / contractual

| Activity | Author | Domain Owner | Content Lead | Legal | Steering |
|---|:--:|:--:|:--:|:--:|:--:|
| Draft | **R** | C | I | C | — |
| Legal review | — | — | I | **R** | — |
| Approve | — | C | I | **A** | I |
| Acceptance-capture design (click-wrap, e-signature) | R | — | C | **A** | — |
| Publish + record version in `LG-001` | R | I | **A** | C | — |
| Change with user notice | R | C | R | **A** | I |

### 5.3 Class C — Operational-critical

| Activity | Author | Domain Owner | Content Lead | SME | QA | Business Owners Forum |
|---|:--:|:--:|:--:|:--:|:--:|:--:|
| Draft | **R** | C | I | C | — | — |
| Technical / business review | — | **R** | I | **R** | — | — |
| Test against the system | — | C | I | — | **R** | — |
| Approve | — | **A** | C | — | C | C |
| Publish | R | I | **A** | — | I | I |
| Post-go-live review | R | **A** | C | C | C | I |

### 5.4 Class D — User-facing

| Activity | Author | Content Design Lead | Domain Owner | Localisation | Accessibility reviewer |
|---|:--:|:--:|:--:|:--:|:--:|
| Draft | **R** | C | C | I | — |
| Style and clarity review | — | **R** | — | — | — |
| Factual review | — | C | **R** | — | — |
| Accessibility review (`CG-011`) | — | C | — | — | **R** |
| Approve | — | **A** | C | C | C |
| Translate | — | C | — | **R** | — |
| Linguistic sign-off (`BN-018`) | — | I | — | **A** | — |
| Publish | R | **A** | I | I | I |

### 5.5 Class E — Internal governance

| Activity | Author | Content Lead | Affected function | PMO |
|---|:--:|:--:|:--:|:--:|
| Draft | **R** | C | C | — |
| Review | — | **R** | C | — |
| Approve | — | **A** | C | I |
| Publish | R | **A** | I | I |

---

## 6. RACI by category

One accountable function per category. This table is the answer to "who owns this?" for any of
the 452 files.

| Category | Accountable (A) | Principal author (R) | Consulted (C) | Approver class |
|---|---|---|---|---|
| `CG` Governance & standards | Programme Content Lead | Content Lead | PMO, EA, Legal | E |
| `VB` Voice & brand | Content Design Lead | Content Design + Brand | Design System, Localisation | D / E |
| `MD` Master data | Master Data Owner (`M64`) | Business SMEs per domain | Finance, Ops, EA, Data Migration | C (A/B where statutory) |
| `UI` UI copy | Content Design Lead | Content designers + BAs | Portal owners, Localisation, Design System | D |
| `NT` Notifications | Content Design Lead | Content designers | Ops, Finance, Legal, Platform | D (A/B for OTP, consent, collections) |
| `DT` Documents & print | Domain Content Owner per document | Finance, Ops, HR, Quality | Legal, Tax, Brand, Platform | A / B / C |
| `SP` Process & SOP | Domain Content Owner | Business Process Analysts | Ops, Quality, Finance, HSE | C |
| `KB` Knowledge | Knowledge Manager (`M61`) | Senior technicians (L2/L3) | Quality, Brand partners | C |
| `TR` Training | Learning & Development Lead | Instructional designers | Domain owners, Localisation | D |
| `HC` Help centre | Content Design Lead | Content designers | Support, portal owners | D |
| `LG` Legal & compliance | Legal Counsel | Legal + external counsel | DPO, Finance, Commercial | A / B |
| `BN` Localisation | Localisation Lead | Translators + linguistic reviewers | Content Design, EA, Brand | D |
| `DM` Data migration | Data Migration Lead | Migration analysts | MDM, Finance, source-system owners | C |
| `TS` Test & acceptance | QA Lead | Test analysts + business users | Domain owners, Security | E / D |
| `RP` Reporting & KPI | BI Lead | BI analysts | Finance, Ops, EA | D (A for statutory reports) |
| `AP` Integration & developer | Platform Engineering Lead | Engineers | Security, Commercial, Legal | D |
| `CM` Change & comms | Change Lead | Comms specialists | HR, Marketing, Ops | D |
| `OP` Operations & runbooks | Support Lead | Platform engineers | Security, Ops | D |
| `EO` Ecosystem onboarding | Commercial content owner per audience | Account/Marketplace/Procurement teams | Legal, Finance | D (B for agreements) |
| `MM` Multimedia specs | Brand Lead | Designers | Content Design, Platform | D |
| `RF` Reference & registers | Programme Content Lead | Content Lead + EA | All | E |

---

## 7. Escalation path

| Trigger | First escalation | Then | Timebox |
|---|---|---|---|
| Author blocked on SME availability | Domain Content Owner | Business Owners Forum | 5 working days |
| Reviewer and author disagree on substance | Domain Content Owner | Content Lead | 3 working days |
| Content Lead and Domain Owner disagree | PMO | Steering Committee | 10 working days |
| Legal review exceeds its SLA (`CG-007`) | Legal Counsel | CFO | 10 working days |
| A Class A statutory position is uncertain | Legal Counsel + external adviser | CFO, then Steering Committee | Immediate; the file does not ship |
| Translation capacity cannot meet a wave gate | Localisation Lead | Content Lead → PMO | At wave gate minus 6 weeks |
| Master data is not ready for a wave | Master Data Owner | PMO | At wave gate minus 8 weeks |
| Content effort exceeds forecast by >20% | Content Lead | PMO → Steering Committee | At the monthly report |
| A content risk becomes Critical or High | Content Lead | Steering Committee (`00-04` decision rights) | At the next Steering meeting |

> **Escalation rule CO-02.** An escalation that is not resolved within its timebox is
> automatically raised to the next level by the Content Lead without further request. Silence is
> not agreement.

### 7.1 Decision rights for content

Extends `00-04` §5.2. Where a content decision affects a `P0` or `P1` requirement, the existing
decision rights apply unchanged.

| Decision | Authority |
|---|---|
| Content operating model, style guide, terminology standard | Steering Committee (this file) |
| Adding or retiring a content file in the register | Programme Content Lead |
| Content priority or wave change within an approved scope | Programme Content Lead with the Domain Owner |
| Content scope change affecting a `P0`/`P1` requirement | Steering Committee |
| Approval of Class A statutory content | CFO or Legal Counsel, with external verification |
| Approval of Class B legal content | Legal Counsel |
| Bengali register and terminology decisions | Localisation Lead, ratified by Enterprise Architecture for `CG-004` bindings |
| Accepting a machine-translation exception (`CG-010`) | Localisation Lead + Content Lead, both required |
| Waiving a Definition-of-Done item (`CG-008`) | Programme Content Lead, time-boxed, logged in `RF-006` |
| Content risk acceptance (Critical or High) | Steering Committee |
| Content risk acceptance (Medium or below) | Programme Content Lead |

---

## 8. Cadence

| Forum | Frequency | Attendees | Output |
|---|---|---|---|
| Content stand-up | Weekly | Content Lead + category leads | Blockers, schedule, review queue depth |
| Terminology board | Fortnightly | EA, Content Design, Localisation, domain SMEs | `CG-004` and `BN-003` decisions |
| Legal content review | Fortnightly | Legal, Content Lead, affected domain owners | Class A and B approvals |
| Localisation review | Fortnightly | Localisation Lead, translators, linguistic reviewers | Sign-offs, terminology escalations |
| Content in Business Owners Forum | Fortnightly (standing item) | 17 module owners | Class C approvals, SME commitments |
| Content report to PMO | Weekly | Content Lead | Progress, forecast, risks, decisions needed |
| Content report to Steering | Monthly (standing item) | Content Lead | Wave readiness, effort variance, escalations |
| Wave-boundary content audit | Per wave | Content Lead | `AUDIT-nnn` filed and indexed in `RF-012` |

---

## 9. Capacity and the funding gap

| Item | Position |
|---|---|
| Estimated content effort | **2,595–3,875 person-days (520–775 person-weeks)** — Master Index §7 |
| Measured build effort for comparison | 1,513 PW across 65 counted module specifications |
| Content as a share of build | **34–51%** — consistent with published ERP implementation experience |
| Funded in the approved business case | **None** |
| Already on the critical path | Phase 0 (`CG`, `MD-001`, `SP-001`…`SP-006`, `DM-001`, `RF` foundations) blocks W1 configuration |

**This is audit finding AF-09.** It must be taken to the Steering Committee in the same paper as
**AF-08** — the build effort variance of 1,513 PW against 834 PW approved (risk `RSK-036`,
decision `D-14`). Presented separately, each reads as an overrun. Presented together, they are
one consequence of the scope expansion from 11 modules to 67 that the business case has not
absorbed.

---

## 10. Operating rules

| # | Rule |
|---|---|
| **CO-01** | No unassigned function. A category with no named Domain Content Owner does not enter production. |
| **CO-02** | An escalation unresolved within its timebox rises automatically. Silence is not agreement. |
| **CO-03** | One accountable per file. Where two functions both claim accountability, the Content Lead assigns it and logs the decision in `RF-006`. |
| **CO-04** | The approver is never the author. On a file where the same person holds both roles, a second approver from the same class is appointed. |
| **CO-05** | A reviewer reviews only within their competence. A business owner does not sign off Bengali; a translator does not sign off tax treatment. |
| **CO-06** | Class A and B content never ships on internal approval alone (`CG-007`). |
| **CO-07** | Every content file carries a review date. A file past its review date is flagged non-current and may not be cited as evidence. |
| **CO-08** | The Content Lead reports the register position by enumeration, never by projection (`CP-11`, `CM-R2`). |
| **CO-09** | Vendor-authored content is subject to the same operating model. A vendor may be Responsible; a 1000FiX function is always Accountable. |
| **CO-10** | Content decisions are logged in `RF-006` at the moment they are taken. `AUDIT-001` finding **AF-04** — the module repository's missing decision log, cited by two audits as `D-14` — is the failure this rule prevents. |

---

## 11. Related documents

| Document | Relationship |
|---|---|
| [`CG-001_Content_Master_Index.md`](CG-001_Content_Master_Index.md) | The register this model operates |
| [`CG-007_Review_Approval_and_Signoff_Workflow.md`](CG-007_Review_Approval_and_Signoff_Workflow.md) | The mechanics of the gates named here |
| [`CG-008_Content_Definition_of_Done_and_QA_Checklist.md`](CG-008_Content_Definition_of_Done_and_QA_Checklist.md) | What "Approved" requires |
| [`CG-013_Content_Risk_and_Legal_Escalation_Rules.md`](CG-013_Content_Risk_and_Legal_Escalation_Rules.md) | Triggers that force escalation |
| `RF-010` Content Ownership & Contact Directory | Names the people behind these functions |
| `RF-006` Content Decision Log | Where every decision under this model is recorded |
| `00-04` §5 | The programme governance this model attaches to |
| `05-04` Role register | Where the new content roles must be registered |

---

## 12. Revision history

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue. Five content classes, RACI per class and per category, escalation path, decision rights, cadence, ten operating rules | Steering Committee (pending) |

---

## Definition of Done

- [x] Front matter complete
- [x] Conforms to the governance template
- [x] Every factual claim carries a source and a verification date
- [x] Class totals reconcile to 452; the 61/75 difference is stated explicitly
- [x] All internal links resolve
- [x] Bengali counterpart — n/a, `bilingual: no`
- [ ] Named approver recorded — **pending Steering Committee ratification**
- [x] Registered in the Content Master Index
- [ ] New roles registered in `05-04` — **open, depends on AF-09 / R-07**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
