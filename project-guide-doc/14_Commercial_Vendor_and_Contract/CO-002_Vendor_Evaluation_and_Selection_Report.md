---
id: CO-002
title: Vendor Evaluation & Selection Report
category: 14 — Commercial, Vendor & Contract
code: CO
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-19
status: DRAFT FOR APPROVAL — Part A baselined before bid opening; Part B completed per stage
classification: CONFIDENTIAL — Internal Use Only
owner: Head of Procurement
approver: ERP Steering Committee, with Board ratification of the award recommendation
standards_basis: >
  ISO 37500:2014 (guidance on outsourcing — §5 outsourcing strategy, §6 supplier selection) ·
  ISO 44001:2017 (collaborative business relationship management systems — stages 1–4; noting
  ISO/DIS 44001 is in the enquiry phase) · ISO 21502:2020 §7.14 (procurement) · PMBOK 7
  (Stakeholder and Uncertainty performance domains) · ISO 31000:2018 (risk in the selection
  decision) · ISO 19011:2018 §6.4 (evidence collection, and the competence and impartiality of
  those who collect it) · ISO/IEC 27001:2022 (the certification MQ-05 requires, verified not
  asserted) · UNCITRAL Model Law on Public Procurement 2011 — adopted as **practice**, not as law
traces_to: >
  PGD-000 CO-002 · RFP §15 (MQ-01…MQ-12, VQ-01…VQ-42), §16.1, §16.3, §16.5, §17.1–§17.5, §18,
  §19, §20 · GV-007 §4.1, §7.1, §7.4 · GV-008 §9 · CO-005 §7, §9.4 · D-014 · D-016 · CVA-02
depends_on: CO-005 · CO-003 · GV-007 · GV-008 · GV-002 · GV-003 · GV-005 · GV-010 · SC-008 · RQ-003
verified_on: 2026-08-19
priority: P1
needed_by: W1
enumeration_timestamp: 2026-08-19 10:40 (+06)
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# CO-002 — Vendor Evaluation & Selection Report

### Category 14 · Code `CO` · ISO 37500:2014 §6 · ISO 44001:2017 · ISO 21502:2020 §7.14 · ISO 19011:2018 §6.4

---

> **Local rule prefix: `VES-nn`.** Verified to return **zero** occurrences workspace-wide before
> allocation, at 2026-08-19 10:40 (+06), by
> `grep -rho "VES-[0-9]\{1,3\}" --include=*.md .` across all six repositories.
>
> **⚠ The category code `CO` is already a rule prefix in three unrelated namespaces** — cost
> controls in `PE-006` §8.4, content-operating-model rules in `CG-002`, and callback-ordering rules
> in `IN-006`; **108 occurrences across 30 files and 3 repositories**. No document in Category 14
> uses `CO-nn` as a local rule prefix. Recorded as `CVA-01`; see `CO-005`'s header note for the
> enumeration.

---

## 1. Purpose

The RFP defines a six-stage evaluation process, thirteen weighted criteria, twelve mandatory
pass/fail gates, twelve scripted demonstration scenarios and a scoring scale. **What it does not
define is the record that applies them.** `PGD-000` states the consequence precisely: *"The record
that applies it — and defends the award if challenged — does not exist."*

This document is that record. It exists so that, on the day the Company notifies a preferred
respondent, four questions have documented answers:

| # | Question | Where it is answered |
|:--:|---|---|
| 1 | **What were we measuring, and did we decide it before we saw the bids?** | Part A — §4 through §8, baselined before 30 October 2026 |
| 2 | **Who scored, independently, and how were differences resolved?** | §9 — the moderation record |
| 3 | **What did we verify rather than accept?** | §10 due diligence, §11 references |
| 4 | **Why this respondent and not the runner-up?** | §12 — the award recommendation |

### 1.1 The structural decision that makes this document work

Bids are due **30 October 2026**. This document is issued on **19 August 2026**. It therefore
contains **no scores**, and that is deliberate.

| Part | Content | Baselined | Changeable after bid opening? |
|:--:|---|---|---|
| **A** *(§4–§8, §13)* | The **instrument** — thresholds, evidence tests, normalisation rules, scoring discipline, the questions to be asked | **Before 30 October 2026**, under `GV-003` change control | **No.** `VES-01` |
| **B** *(§9–§12)* | The **record** — score sheets, moderation minutes, due-diligence findings, reference notes, the award recommendation | Progressively, per stage | It *is* the record; it grows |

> **`VES-01` — the instrument is frozen before the first envelope is opened, and any change to it
> after that point is a `GV-003` decision with a written justification circulated to all
> respondents.** An evaluation methodology finalised after the bids are visible is not a
> methodology; it is a rationalisation, and it is the single easiest thing for a disappointed
> respondent to attack. `CO-002-D-01` records why this document is issued eleven weeks before it
> can contain a score.

### 1.2 Scope

**In scope:**

| # | Covered |
|:--:|---|
| 1 | The evaluation **instrument**: how each of RFP §17.1's six stages is conducted, by whom, against what evidence |
| 2 | **Stage 1** — the twelve mandatory pass/fail gates, each with the evidence that satisfies it and the test that does not |
| 3 | **Stage 2** — the thirteen weighted criteria, the scoring scale, the elimination thresholds, and the moderation procedure |
| 4 | **Three criteria whose benchmarks are superseded**, and what to do about them before bids arrive |
| 5 | **Stages 3–5** — demonstration, deep-dive, references and site visit, each with a scoring rubric and an evidence rule |
| 6 | **Stage 6** — the commercial evaluation, and the **normalisation rules** that make heterogeneous bids comparable against `CO-005` |
| 7 | **Due diligence** — financial, security-certification, insurance, litigation and disclosure verification |
| 8 | Panel composition, **conflict of interest** and confidentiality |
| 9 | The **award recommendation** structure, and the runner-up position the Company must preserve |
| 10 | The **challenge-defence** analysis — what a disappointed respondent could allege, and which record answers it |
| 11 | The **record templates** that Part B is completed into |

**Explicitly out of scope:**

| Topic | Owned by | Why the boundary sits here |
|---|---|---|
| The **cost model** bids are evaluated against | `CO-005` | This document applies it; it does not derive it. §8.2's normalisation rules are the interface |
| The **contract** the winner signs | `CO-003` | Selection ends at the award recommendation. `CO-003` §4 turns it into deliverables and milestones |
| Amending the **RFP** itself | Head of Procurement, under `GV-003` | §5.4 recommends the addendum; issuing it is a procurement act, not an evaluation one |
| **Requirement-level fit assessment** of Appendix A responses | `RQ-003` fit-gap | Criterion 1 and 2 scores rest on it; the analysis itself is a requirements activity |
| The **security assessment** of the respondent's own estate | `SC-008`, `SC-009` | §10.3 verifies the certificate; assessing the respondent as a processor is `SC-003`'s DPIA and the DPA under `CO-003` |
| **Post-award relationship management** and performance review | `CO-003` §9, `SV-002` | ISO 44001 stages 5–8. This document covers stages 1–4 only, and says so in §2.1 |

### 1.3 Intended audience

| Audience | What they use this document for |
|---|---|
| **Evaluation panel** | §4–§8 are their working instructions. §9's score sheet is what they complete |
| **Head of Procurement** | The owner. §5.4's addendum recommendation is theirs to execute |
| **ERP Steering Committee** | Approves Part A before bid opening; receives the award recommendation |
| **Board of Directors** | Ratifies the award. §12.3 is written for this reader |
| **Legal Counsel** | §3's conflict analysis, §10's disclosure verification, §14's challenge-defence table |
| **Audit Committee / `GV-010` independent review** | The evidence trail. Every score in Part B traces to a numbered evidence item |
| Respondents *(the parts disclosed to them)* | §5.2's elimination thresholds and §8.2's normalisation rules are disclosed in the addendum so that the basis of assessment is known before submission |

---

## 2. Basis and Inputs

### 2.1 Standards conformance

| Standard | Clause | How this document conforms | Departure and rationale |
|---|---|---|---|
| **ISO 37500:2014** | §6 (supplier selection), §5 (outsourcing strategy) | §4's stage structure, §10's due diligence and §12's award decision follow the selection phase. The strategy phase is `GV-001` and `02-05` §7's build-vs-buy set | ISO 37500 assumes an outsourcing decision is being taken. **Here it is already taken** — `02-05` §7's twenty decisions and `AR-013` §5 fix build-vs-buy — so §5's strategy phase is inherited, not repeated |
| **ISO 44001:2017** | Stages 1–4 (awareness, internal assessment, partner selection, working together) | §3's panel and conflict rules, §10's due diligence, §11's references, §12's award | **Stages 5–8 (value creation, staying together, exit) are out of scope** and belong to `CO-003` §9 and `SV-002`. Claiming full conformance would be false. Noted also that **ISO/DIS 44001 is in the enquiry phase** and may supersede the 2017 edition during this procurement — `VES-Q-06` |
| **ISO 21502:2020** | §7.14 procurement | Requirements defined, suppliers selected, agreements administered | Agreement administration is `CO-003` |
| **ISO 19011:2018** | §6.4 (collecting and verifying information); §7 (auditor competence and impartiality) | §9.2's independent-scoring rule, §10's verification-not-assertion rule, §3.2's impartiality declarations | ISO 19011 governs management-system audits. **Adopted by analogy** for evidence discipline, because the evidence problem in a bid evaluation is identical and no procurement standard states it as well |
| **ISO 31000:2018** | §6.4 risk evaluation | §12.2 records the residual risk of the recommended award, not only its merits | None |
| **ISO/IEC 27001:2022** | — | MQ-05's certificate is **verified against the certification body's register**, not accepted as a PDF | §10.3 |
| **UNCITRAL Model Law on Public Procurement 2011** | Arts. 9, 11, 22, 24, 25 | Objective and disclosed criteria; no post-opening change to criteria or weights; a written record; debriefing | **Adopted as practice, not as law.** 1000FiX is a private company and is not subject to it. It is adopted because it is the most widely-tested articulation of what makes an award defensible, and because corporate clients and brand partners increasingly ask suppliers to demonstrate equivalent discipline |

### 2.2 Source material relied on

| Source | Location | What it establishes |
|---|---|---|
| RFP §15.1–§15.5 | `../../primary-doc/1000FiX_ERP_System_Comprehensive_RFP.md` | **MQ-01…MQ-12** mandatory gates; **VQ-01…VQ-42** information requirements |
| RFP §16.1–§16.5 | as above | The envelope, the pricing response structure, `OPT-01`…`OPT-12`, the payment structure, `CR-01`…`CR-09` |
| RFP §17.1–§17.5 | as above | The six stages, the thirteen weighted criteria, the scoring scale, `D-01`…`D-12` demonstrations, and the ten marked-down behaviours |
| RFP §12.7 | as above | The indicative team model — **peaking at 19 FTE** — and the business-side commitment |
| RFP §18.1, §18.5 | as above | The timetable; the reservation of the right to **amend the timetable** |
| RFP §19.1–§19.4 | as above | Contractual terms the respondent must accept, including IP, source-code delivery and the DPA |
| RFP §20.1–§20.10 | as above | The disclosed open items — and §17.5 item 8's rule that **silence on them is marked down** |
| `CO-005` §7, §9.1, §9.4 | `./CO-005_Total_Cost_of_Ownership_Model.md` | The cost model bids are normalised against; `CVA-02` |
| `GV-007` §4.1, §4.3, §7.1, §7.4 | `../00_Programme_Governance_and_Control/GV-007_*.md` | **1,842 PW build / 3,022 PW programme**; the +6.2 build FTE and +15.8 programme FTE shortfalls |
| `GV-008` §9 | `../00_Programme_Governance_and_Control/GV-008_*.md` | The four options, and the recommendation of option B — which shapes what is being bought |
| `GV-002` §4, §5.2 | `../00_Programme_Governance_and_Control/GV-002_*.md` | Governance bodies, decision rights and the RACI the panel sits inside |
| `GV-010` | `../00_Programme_Governance_and_Control/GV-010_*.md` | Independent assurance — §3.3's observer role |
| `RQ-003` | `../01_Requirements_Engineering/RQ-003_*.md` | The fit-gap that criterion 1 and 2 scores depend on |
| `SC-008` | `../05_Security_Privacy_and_Compliance/SC-008_*.md` | The regulatory obligations criterion 5 tests against |

### 2.3 Audit findings and open items this document addresses

| Finding | Source | How this document addresses it |
|---|---|---|
| *"The record that applies the scoring methodology does not exist"* | `PGD-000` Category 14 | **Closed in specification.** This document is the record; Part B completes it |
| **`CVA-02`** | `CO-005` §9.4 | **Carried and extended.** §5.4 shows the stale envelope breaks the evaluation in **three** places, not one, and §5.5 adds a fourth that `CO-005` did not reach: MQ-06 |
| **`CVA-07`** *(raised here)* | This document | **MQ-06 — a mandatory pass/fail gate — is calibrated to a superseded scope.** §5.5 |
| **`CVA-08`** *(raised here)* | This document | **The RFP asks respondents to price disciplines its own indicative team model does not staff.** §5.6 |
| **`CVA-09`** *(raised here)* | This document | **The two mechanisms that would detect an under-scoped bid are broken by the same stale figure.** §5.4 |
| `D-014` | `GV-003` | The evaluation cannot be concluded until `D-014` is taken: §8.4 records that the Company must know what it is buying before it can score what it is offered |
| `D-016` | `GV-003` | Portal effort is **outside** the module figure. Criterion 3 (portal and mobile capability, 10%) must be scored knowing the 298 PW is additive |
| RFP §20.3.1 | RFP Part E | The Company disclosed the 1,513 PW variance. **It must now disclose the 3,022 PW restatement**, or the disclosure it made becomes a partial one |

---

## 3. The Evaluation Panel

### 3.1 Composition

Derived from the thirteen criteria: every criterion has a named assessor with the competence to
score it, per ISO 19011 §7.

| Role | Scores criteria | Basis |
|---|---|---|
| **Head of Procurement** *(chair, non-scoring)* | — | Runs the process; owns the record; does not score, so that process integrity and outcome preference are separated |
| Chief Technology Officer | 4, 7, 12 | `GV-002` §5.2 |
| Solution Architect / Chief Architect | 4, 6, 8 | Architecture Review Board chair |
| Head of Service Operations | 1, 11, 12 | The operational core is Categories A, C, E |
| Chief Financial Officer | 13, and Stage 6 | `CO-005`'s owner |
| Chief Data Officer | 5, 8 | Residency, PDPA, migration |
| Chief Information Security Officer *(or Security Lead)* | 5 | `RSO-01`…`RSO-11` |
| Head of Customer Experience | 3 | `P01` conversion, `P02` offline |
| HR Director / Change Lead | 11 | Training, change, knowledge transfer |
| PMO Lead | 7, 9, 10 | Delivery approach, team quality, references |
| **Legal Counsel** *(non-scoring adviser)* | — | §19 acceptance, disclosure verification, the DPA |
| **`GV-010` independent reviewer** *(observer, non-scoring)* | — | §3.3 |

**Verification that every criterion has at least two independent scorers** *(regenerated per
`PG-M10`)*: criteria 1 (Ops, PMO), 2 (Ops, CFO — see note), 3 (CX, CTO), 4 (CTO, Architect),
5 (CDO, CISO), 6 (Architect, CTO), 7 (CTO, PMO), 8 (CDO, Architect), 9 (PMO, HR), 10 (PMO,
Procurement chair as recorder), 11 (HR, Ops), 12 (Ops, CTO), 13 (CFO, PMO).

> **`VES-02` — no criterion is scored by one person.** A single scorer's judgement is not a
> weakness of character; it is an unverifiable input, and §9.2's moderation cannot function without
> at least two independent scores to reconcile. **Criterion 2 covers eight module categories and
> needs a third assessor drawn from the category business owners** — `VES-Q-01`.

### 3.2 Conflict of interest and impartiality

| # | Rule |
|---|---|
| **`VES-03`** | Every panel member, adviser and observer signs a **conflict-of-interest declaration before the respondent list is disclosed to them**, not after. A declaration made after the names are known is a different instrument |
| **`VES-04`** | A declared interest — prior employment, family relationship, shareholding, or any personal benefit from a respondent — **removes the member from scoring that respondent**, not from the panel. The chair records the substitution |
| **`VES-05`** | **No panel member accepts hospitality, travel, equipment or gifts** from a respondent between RFP issue and contract signature. This is stated because it is customary in the market and because §17.5's marked-down behaviours are silent on it |
| **`VES-06`** | All respondent contact runs through the Head of Procurement. **A respondent who approaches a panel member directly is recorded, and the approach is disclosed to all respondents** |
| **`VES-07`** | RFP §15.1 MQ-10 requires respondents to declare conflicts. **The Company verifies the declaration** against its own supplier and shareholder records rather than accepting it — `VES-14` applies |

### 3.3 The independence problem this panel inherits

`GV-009` §5.2 records an independence problem in wave-gate assessment: the people who build are
close to the people who assess. **The same problem exists here in a sharper form**, because the
panel members who score technical fit are the people who will spend three years working alongside
the winner, and who may already have a working preference.

| Mitigation | Mechanism |
|---|---|
| Independent scoring **before** any panel discussion | `VES-08` |
| The `GV-010` independent reviewer **observes Stages 2, 3 and 6 and may record a dissent** in the award recommendation | `VES-09` |
| Reference checks conducted **without the respondent present** (RFP §17.1 Stage 5) and by a member who did not score that respondent's technical criteria | `VES-10` |
| The **runner-up position is documented and preserved** (§12.4), so that a failed negotiation does not force a re-run | `VES-11` |

---

## 4. The Six Stages

### 4.1 Structure, dates and outputs

From RFP §17.1 and §18.1. Every stage produces a numbered artefact that becomes Part B.

| Stage | Activity | Dates (RFP §18.1) | Output artefact | Decision |
|:--:|---|---|---|---|
| **0** | **Instrument baselined**; panel appointed; declarations signed | **By 30 October 2026** | This document, Part A, approved | Steering Committee |
| **1** | **Compliance review** — MQ-01…MQ-12, pass/fail | 2–6 Nov 2026 | `CO-002-B1` compliance matrix | Chair, with Legal |
| **2** | **Technical evaluation** — 13 weighted criteria | 9 Nov – 4 Dec 2026 | `CO-002-B2` score sheets + moderation record | Panel consensus |
| — | **Shortlist notification** — 3–4 respondents | 8 Dec 2026 | `CO-002-B3` shortlist rationale | Steering Committee |
| **3** | **Scripted demonstration** — `D-01`…`D-12` | 14 Dec 2026 – 8 Jan 2027 | `CO-002-B4` demonstration record | Panel |
| **4** | **Technical deep-dive and team interview** | 12–22 Jan 2027 | `CO-002-B5` interview record | Panel |
| **5** | **Reference checks and site visit** — 2 finalists | 25 Jan – 12 Feb 2027 | `CO-002-B6` reference record | Chair + one non-scoring member |
| **6** | **Commercial evaluation** — 3-year and 5-year TCO, rate card, descope flexibility | 15–26 Feb 2027 | `CO-002-B7` normalised commercial comparison | CFO |
| **7** | **Final scoring, due diligence, award recommendation** | By 3 Mar 2027 | `CO-002-B8` award recommendation | **Steering Committee → Board** |
| — | Contract negotiation | 8 Mar – 9 Apr 2027 | Handover to `CO-003` | — |

### 4.2 Two structural observations about the timetable

| # | Observation | Consequence |
|:--:|---|---|
| 1 | **Stage 2 runs for four weeks over 2,930 requirement-level responses per respondent.** At four respondents that is roughly 11,700 requirement responses to assess in twenty working days | The panel cannot read them all. `VES-12` sets a sampling rule with a stated confidence, rather than pretending to completeness — see §6.3 |
| 2 | **`D-014` is scheduled to be decided by the Board, and the timetable does not contain it.** Stage 6 compares bids against a scope the Company may still descope | `VES-13`: **the Company must take `D-014` before Stage 6 opens**, or Stage 6 scores a bid for a scope it may not buy. §8.4 |

---

## 5. Stage 1 — The Mandatory Gates

### 5.1 The twelve gates and their evidence tests

RFP §15.1: *"A submission failing any of the following is eliminated at Stage 1 regardless of
overall score."* For each, the column that matters is the third: **what does not satisfy it.**

| ID | Requirement | Evidence that satisfies | **What does not satisfy it** |
|---|---|---|---|
| `MQ-01` | Registered ≥ 5 years; audited accounts for 3 fiscal years | Registration certificate + **three** sets of audited accounts | Management accounts; two years plus a projection; unaudited statements |
| `MQ-02` | ≥ 3 completed ERP implementations of ≥ 500 functional requirements in 5 years, ≥ 1 on the proposed platform | Named clients, **contactable**, with requirement counts stated | A count the respondent asserts without a client who will confirm it. `VES-14` |
| `MQ-03` | Odoo capability — ≥ 5 developers with production Odoo experience, ≥ 1 completed **v17+** implementation | CVs + project evidence + OCA contribution history | v15/v16 experience presented as v17+; a partner's developers counted as the respondent's without a contract |
| `MQ-04` | **Bengali language capability** | Team CVs, or a **signed** local partner agreement | An intention to recruit; a letter of intent; machine translation capability |
| `MQ-05` | **ISO 27001** certification or audited equivalent, **current at submission** | Certificate **verified against the certification body's public register** — §10.3 | A PDF certificate. An expired certificate. A certificate whose scope excludes the delivery entity |
| `MQ-06` | Capacity to field a **peak team of 19 FTE** without displacing another engagement | Resource plan + a **current commitments statement** | A headcount total. See **§5.5 — this gate is calibrated to a superseded scope** |
| `MQ-07` | ≥ 1 production **offline-first** field application | App store listing + project evidence + a demonstrable offline mode | An app that caches; "offline support on the roadmap". `D-03` tests it for real at Stage 3 |
| `MQ-08` | Acceptance that **all source, configuration and documentation is 1000FiX property**, delivered continuously | Signed acknowledgement, unqualified | An acknowledgement with an Exceptions schedule that reserves the framework the system depends on |
| `MQ-09` | Acceptance of **milestone payment tied to wave gate passage** | Signed acknowledgement | Acceptance "in principle"; acceptance conditional on renegotiating the gates |
| `MQ-10` | No conflict of interest; no debarment or impairing litigation | Declaration, **verified** under `VES-07` and §10.5 | The declaration alone |
| `MQ-11` | Proposal validity **180 days** | Signed cover letter | 90 days; validity "subject to market conditions" |
| `MQ-12` | Complete **Appendix A at requirement level** for all Annex 1 requirements | The completed workbook, all 2,930 rows | Module-level responses — which §17.5 item 1 independently marks down |

> **`VES-14` — a mandatory gate is verified, not read.** Six of the twelve (`MQ-02`, `MQ-03`,
> `MQ-04`, `MQ-05`, `MQ-07`, `MQ-10`) can be satisfied on paper by a respondent that cannot satisfy
> them in fact. Each is verified at §10 before the shortlist is notified, **not after the preferred
> respondent is chosen**, because a gate failure discovered at Stage 7 costs the timetable.

### 5.2 Elimination thresholds beyond Stage 1

RFP §17.3: *"A score below **50** on criteria **1, 3, 4, 5 or 7** may result in elimination
irrespective of the weighted total."*

| # | Criterion | Weight | Why this one carries a floor |
|:--:|---|---:|---|
| 1 | Functional fit — Categories A, C, E | 18% | The operational core. A respondent who cannot do service, commercial and supply chain cannot do this programme |
| 3 | Portal and mobile capability | 10% | `P02` offline is not recoverable by effort later; `RSK-008` is Critical on technician adoption |
| 4 | Technical architecture and platform engineering | 10% | `AS-01`…`AS-15` are non-negotiable; a respondent who proposes business logic in portals has misread the architecture |
| 5 | Bangladesh regulatory and data-protection competence | 8% | PDPA 2026 and split residency are statutory. There is no partial compliance |
| 7 | Delivery approach, wave plan and capacity realism | 8% | **The bid-realism detector** — see §5.4 |

> **`VES-15` — "may result in elimination" is converted to a decision, not left as a discretion.**
> A sub-50 score on any of the five triggers a **recorded Steering Committee decision** to eliminate
> or to proceed with a stated reason. An unexercised discretion is the weakest position in a
> challenge: it lets a disappointed respondent argue the rule was applied to them and waived for the
> winner.

### 5.3 The weights, verified

| # | Criterion | Weight |
|:--:|---|---:|
| 1 | Functional fit — Categories A, C, E | 18% |
| 2 | Functional fit — Categories B, D, F, G, H, I, J, K | 12% |
| 3 | Portal and mobile capability | 10% |
| 4 | Technical architecture and platform engineering | 10% |
| 5 | Bangladesh regulatory and data-protection competence | 8% |
| 6 | Integration capability — 47 integrations | 7% |
| 7 | Delivery approach, wave plan and capacity realism | 8% |
| 8 | Data migration approach | 5% |
| 9 | Team quality and key-personnel commitment | 7% |
| 10 | Relevant experience and references | 6% |
| 11 | Change management, training and knowledge transfer | 4% |
| 12 | Support, maintenance and warranty | 3% |
| 13 | **Total cost of ownership (3-year and 5-year)** | **2%** |
| | **Total** | **100%** |

**Verification** *(regenerated from the rows per `PG-M10`)*: 18 + 12 + 10 + 10 + 8 + 7 + 8 + 5 + 7 +
6 + 4 + 3 + 2 = **100** ✓. Functional and technical fit (criteria 1–4): 18 + 12 + 10 + 10 = **50%**
✓, matching RFP §17.2's stated *"Functional and technical fit together carry 50%."*

### 5.4 `CVA-09` — the two mechanisms that detect an under-scoped bid are broken by the same figure

`CO-005` §9.4 records that the RFP's published envelope and effort basis were superseded five and
six days after issue. **This section states the consequence specific to evaluation**, which is
sharper than the cost consequence.

An evaluation of a fixed-price bid has exactly **two** mechanisms for detecting a respondent who has
under-scoped the work. The RFP has both. **Both are keyed to the superseded 1,513 PW figure.**

| Mechanism | RFP text | What it is keyed to | Effect |
|---|---|---|---|
| **Criterion 7 — capacity realism, 8%, with a sub-50 elimination floor** | *"An **independent capacity analysis against 1,513 PW**; an honest view of whether 9 waves in 36 months is achievable"* | **1,513 PW** | A respondent who correctly analyses against **3,022 PW** produces an answer the rubric does not reward. A respondent who analyses against 1,513 PW and concludes it is achievable scores **well** — and is wrong |
| **§16.1's envelope test** | *"A bid that is **materially below the envelope** will be scrutinised for scope understanding, not rewarded for price"* | **$690K–$1,150K** | `CO-005` §7.1 puts the three-year expected cost at **$2,501K**. The envelope's **upper** bound is less than half of it. **A correctly-priced bid is now "materially above" the envelope and must justify a variance; an under-priced bid sits comfortably inside and triggers no scrutiny at all** |

> **The instrument inverts.** Both safeguards were designed to catch the optimistic bidder, and as
> currently published both catch the accurate one instead. §17.5 item 3 marks down *"accepting the
> published wave plan without an independent capacity analysis"* — so the RFP simultaneously demands
> independent analysis and fixes its benchmark at a figure the Company has withdrawn.
>
> **This is not a scoring nuance.** Criterion 7 carries a sub-50 elimination floor under §17.3. It
> is arithmetically possible for the RFP as published to **eliminate the only respondent who
> understood the scope**.

**Recommended action — carried from `CO-005-D-05` and extended:**

| # | Action | By |
|:--:|---|---|
| 1 | RFP **Addendum 1** restates §16.1's envelope on the `CO-005` basis | **Before 17 September 2026** |
| 2 | Addendum 1 restates **§17.2 criterion 7's benchmark** from 1,513 PW to `GV-007` §7.1's 1,842 PW build / 3,022 PW programme, and states which of the four work streams are in the respondent's scope | Before 17 Sept 2026 |
| 3 | Addendum 1 restates **§16.2.1's effort basis** and **§20.3.1's disclosure** | Before 17 Sept 2026 |
| 4 | Addendum 1 restates **MQ-06** — §5.5 | Before 17 Sept 2026 |
| 5 | Extend the submission deadline by the notice §18.1 requires; §18.5 expressly reserves the right | With Addendum 1 |

### 5.5 `CVA-07` — MQ-06's 19-FTE threshold is calibrated to a superseded scope

**MQ-06 is a mandatory pass/fail gate**, and its threshold comes from RFP §12.7's indicative team
model, which peaks at 19 FTE in Waves 6 and 7. §12.7 states its own basis explicitly: *"a materially
smaller team must be justified against the measured **1,513 PW**."*

**What the §12.7 model actually delivers**, computed from its own rows against the RFP §18.1 wave
durations:

| Wave | FTE (§12.7) | Months | FTE-months |
|:--:|---:|---:|---:|
| W1 | 7.0 | 4 | 28.0 |
| W2 | 11.5 | 4 | 46.0 |
| W3 | 16.0 | 5 | 80.0 |
| W4 | 17.0 | 5 | 85.0 |
| W5 | 17.0 | 4 | 68.0 |
| W6 | 19.0 | 4 | 76.0 |
| W7 | 19.0 | 4 | 76.0 |
| W8 | 16.0 | 4 | 64.0 |
| W9 | 10.0 | 2 | 20.0 |
| **Total** | | **36** | **543.0** |

**Verification** *(regenerated per `PG-M10`)*: 28 + 46 + 80 + 85 + 68 + 76 + 76 + 64 + 20 = **543**
✓; wave months 4+4+5+5+4+4+4+4+2 = **36** ✓.

| Step | Working | Result |
|:--:|---|---:|
| 1 | 543 FTE-months × 4.33 weeks/month | **2,351 FTE-weeks** |
| 2 | × `GV-007`'s delivery factor of **0.78** | **1,834 effective PW** |
| 3 | Against `GV-007` §4.1's **build** requirement of 1,842 PW | **99.6%** |
| 4 | Against `GV-007` §7.1's **programme** requirement of 3,022 PW | **60.7%** |

> **The RFP's indicative team is sized, to within half a percent, for the build and for nothing
> else.** That is a defensible position **if** content, engineering definition and screen design are
> the Company's scope — and `GV-001` §6.3 does charter content as a Company workstream. **But the
> RFP does not say so**, and §5.6 shows it asks respondents to price those disciplines anyway.
>
> **Two consequences for MQ-06 as a mandatory gate:**
>
> | # | Consequence |
> |:--:|---|
> | 1 | A respondent fielding **19 FTE at peak passes a mandatory gate while being sized for 61% of the programme**. The gate does not do the job a mandatory gate exists to do |
> | 2 | The gate is expressed as a **peak** but the arithmetic above is a **sustained average**. A 36-month programme needing 3,022 PW at a 0.78 delivery factor requires **24.8 FTE sustained** — 3,022 ÷ 156.5 ÷ 0.78 = 24.8 — with a peak materially above that. **MQ-06 sets a peak threshold below the required average** |
>
> **Verification**: 3,022 ÷ 156.5 = 19.31 team-weeks per week; 19.31 ÷ 0.78 = **24.8 FTE** ✓.
>
> **Addendum 1 must restate MQ-06**, stating the scope split explicitly and setting the threshold
> against whichever side of the split the respondent is bidding for. Until it does, `VES-16`
> applies: **MQ-06 is assessed but not used to eliminate**, and the capacity question is carried
> into criterion 7 where it can be scored rather than gated.

### 5.6 `CVA-08` — the RFP prices disciplines its own team model does not staff

| Discipline the respondent must price (RFP §16.2.2) | In the §12.7 team model? |
|---|:--:|
| Programme management · Solution architecture · Business analysis · Odoo configuration · Custom Odoo development · Standalone service development · Mobile (Flutter) · Frontend (Next.js) · Data platform & BI · AI/ML · DevOps · Testing | ✅ |
| **Integration development (47 integrations)** | ⚠ Not a named role; presumably inside Odoo/service development |
| **Data migration** | ❌ **No migration specialist in §12.7**, although `VQ-31` requires one to be named |
| **Bengali translation and localisation** | ❌ No translator, no localisation role |
| **Documentation and runbooks** | ❌ No technical author |

> **Four disciplines are priced and three are unstaffed in the Company's own model.** A respondent
> reading §12.7 as guidance will under-staff exactly the three work streams `GV-007` §7.1 identifies
> as never having been in any estimate — content, engineering definition, and the localisation that
> `CON-05` makes a definition-of-done item.
>
> This is the **same defect as `CVA-07`, expressed as a staffing omission rather than a headcount
> one**, and it has the same cause: a team model built for a 30-module, 834 PW scope and carried
> forward unchanged. Addendum 1 should restate §12.7 or mark it withdrawn. `VES-Q-02`.

---

## 6. Stage 2 — Technical Evaluation

### 6.1 The scoring scale, and what each band must mean in practice

RFP §17.3 gives five bands. They are restated here with the **evidence test** that separates
adjacent bands, because a scale without one produces scores clustered at 70 and a moderation session
that cannot resolve anything.

| Score | RFP description | **The evidence test that earns it** |
|---|---|---|
| **90–100** | Excellent — meets and demonstrably exceeds, with evidence | The respondent shows a **named prior instance** of doing this specific thing, with an outcome a reference will confirm. Not a capability statement — an instance |
| **70–89** | Good — meets with minor, clearly stated gaps | Meets the requirement, and **the respondent itself names the gaps**. A response with no stated gaps across 2,930 requirements is not a 70–89; it is unexamined |
| **50–69** | Adequate — meets most; some gaps need remediation planning | Meets, but the evidence is generic or the gaps are found by the panel rather than declared |
| **30–49** | Below average — significant gaps; substantial custom work or capability building | The respondent would be learning on this programme. `CR-06`: *"The Company will not pay for respondent learning of the Odoo platform or the Bengali language"* |
| **0–29** | Poor — does not meet | — |

> **`VES-17` — a score of 90 or above requires a named, contactable instance.** Without this rule
> the top band is awarded for confidence, and confidence is exactly what §17.5 item 6 marks down as
> *"generic marketing content in place of specific, evidenced answers."*

### 6.2 The ten marked-down behaviours, as a scoring instrument

RFP §17.5 lists ten behaviours the Company will mark down. They are converted here from a warning
into a **deduction schedule**, so that "marked down" is a defined act rather than a sentiment.

| # | Behaviour (RFP §17.5) | Applies to criterion | Treatment |
|:--:|---|---|---|
| 1 | Module-level rather than requirement-level responses | 1, 2 | **Caps criteria 1 and 2 at 49** — and independently fails `MQ-12` |
| 2 | Over-classification to L5 custom development without justification | 1, 2, 4 | −10 on criterion 4. It inflates price and understates platform knowledge |
| 3 | Accepting the published wave plan without independent capacity analysis | **7** | **Caps criterion 7 at 49**, which triggers the §17.3 elimination floor |
| 4 | Business logic in portals, or portal-held authoritative state | 4 | −20 on criterion 4. `AS-01`…`AS-15` are non-negotiable |
| 5 | Bengali or offline treated as phase two | 3, 5, 11 | −15 on criterion 3. `CON-05`; `DoD-08` |
| 6 | Generic marketing content | All | Scored on evidence; a criterion with no evidence cannot exceed 69 (`VES-17`) |
| 7 | Bench-and-swap staffing with unnamed personnel | **9** | **Caps criterion 9 at 49.** `VQ-35`, `VQ-36` |
| 8 | Silence on the disclosed open items in §20 | 7, 13 | −10 on criterion 7. **The disclosure is a test**, and this is the answer sheet |
| 9 | Pricing that cannot be cleanly descoped | **13**, and Stage 6 | −20 on criterion 13; recorded against `OPT-01`…`OPT-12` |
| 10 | Machine-translated Bengali **in any deliverable, including the proposal** | 3, 5, 11 | **Caps criterion 11 at 49.** `CG-010` forbids it on field-facing content; a machine-translated proposal predicts machine-translated deliverables |

> **`VES-18` — item 8 is the most informative item on the list and should be scored as such.**
> RFP Part E discloses 27 open items, 12 Critical risks, five open decisions and nine constraints.
> **A respondent's treatment of §20 is the single best available predictor of how it will behave
> when it meets the twenty-eighth problem**, which it will, in Wave 2, and which will not be on any
> list. Silence scores −10; a respondent that engages with `H2-05`'s 70 colliding CD identifiers,
> `RSK-008`'s technician adoption risk and `DEP-31`'s residency opinion has told the panel more than
> its case studies have.

### 6.3 `VES-12` — the sampling rule for requirement-level assessment

Stage 2 runs 9 November to 4 December 2026 — twenty working days — across up to four respondents,
each answering **2,930** requirements. Reading every response is not possible, and a methodology
that implies otherwise will not survive scrutiny.

| # | Rule |
|---|---|
| **`VES-12a`** | **100% assessment** of every requirement classified **P0** in Categories A, C and E — the criterion 1 population |
| **`VES-12b`** | **Stratified sample** elsewhere: a minimum of **10% per module**, stratified by priority, with a floor of **five requirements per module** so no module is unsampled |
| **`VES-12c`** | **100% assessment** of every requirement carrying a **statutory** citation (`SC-008`), regardless of category or priority. A sampling miss on Mushak, TDS, PDPA or the Labour Act is not recoverable |
| **`VES-12d`** | **The sample is drawn and fixed before the responses are opened**, and is **identical across respondents**. A per-respondent sample is not a comparison |
| **`VES-12e`** | Any requirement where two respondents' answers diverge materially is **escalated to full assessment** for all respondents |
| **`VES-12f`** | The sample, its size, its method and its coverage are **stated in the award recommendation**. `CO-005` `TCO-09`'s principle applies here too: an assessment that bounds its own coverage says so |

> **`RQ-003`'s fit-gap is the precondition for scoring criteria 1 and 2 well, and it does not exist
> yet.** Nobody has determined what Odoo 19 CE and OCA already deliver. Without it the panel cannot
> distinguish a respondent who has correctly classified a requirement as L1 configuration from one
> who has over-classified it to L5 — which is §17.5 item 2, worth −10. **`VES-Q-03`: `RQ-003` must
> be complete before Stage 2 opens on 9 November 2026.**

---

## 7. Stages 3, 4 and 5

### 7.1 Stage 3 — the scripted demonstrations

RFP §17.4: twelve scenarios, *"on a working system — configured, not mocked. Slides are not
accepted."*

| # | Scenario | Assesses | The thing to watch |
|---|---|---|---|
| `D-01` | Walk-in intake → dispatched service order, **timed, in Bengali** | M01, M04, M33, NFR-076 | The **clock**. `G1-03` sets a three-minute intake bar and `CH-002` puts the largest learner population behind it |
| `D-02` | Morning queue dispatch with skill, certification, location and van-stock constraints, then emergency insertion with re-optimisation | M02, M22 | Whether the constraints are **real** or a filtered list |
| `D-03` | Technician app: full job execution **in airplane mode**, then sync | P02, NFR-037, NFR-047 | **Conflict resolution on sync**, not the offline mode itself. `AR-010` is where this is hard |
| `D-04` | Estimate → approval → parts → QC → invoice → payment | M01, M15, M36, M20 | Whether stock and ledger move in the same transaction |
| `D-05` | Warranty job → claim with evidence pack → brand portal → reconciliation | M09, P08 | The **reconciliation**, which is where claims die |
| `D-06` | Mushak 6.3 invoice and Mushak 9.1 return preparation | M51 | Statutory form fidelity. `CO-005` §6.1 makes this a **tax-rebate dependency**, not only a compliance one |
| `D-07` | PDPA access and erasure request end to end, showing residency handling | M33, M29, NFR-093, NFR-086 | Whether erasure reaches **backups** — `PE-007` §4.6's tension |
| `D-08` | Marketplace: seller KYC → broadcast → bid → award → completion → commission → payout | M12, M53, P07 | Settlement **in the ledger**, per build-vs-buy decision 5 |
| `D-09` | An SoD violation attempted and blocked, **through both UI and API** | M29, DoD-04 | The **API** half. Most systems block the UI only |
| `D-10` | Executive dashboard drill from group revenue to a single job | M25, P06 | Whether the drill is real or two disconnected reports |
| `D-11` | Integration failure with graceful degradation and documented fallback | M28, NFR-050 | What the **user** sees, not what the log says |
| `D-12` | New contract product family configured **without code change** | M08 | The single best test of whether the respondent has built a platform or a bespoke system |

| # | Rule |
|---|---|
| **`VES-19`** | The demonstration environment is **the respondent's**, but the **data is the Company's** — a supplied anonymised fixture set, identical for all respondents, issued 10 working days before the first demonstration |
| **`VES-20`** | Each scenario is scored **immediately after it runs**, by each assessor independently, before discussion. A scenario re-run after coaching is recorded as a re-run |
| **`VES-21`** | **`D-03` and `D-09` are pass/fail, not scored.** Offline job execution and API-layer SoD enforcement are architectural properties: a system either has them or is being modified to appear to. `RSK-008` is Critical on the first; `DoD-04` is a contractual acceptance criterion on the second |

### 7.2 Stage 4 — technical deep-dive and team interview

| # | Rule |
|---|---|
| **`VES-22`** | **The named key personnel are interviewed** — `VQ-23`…`VQ-34` — not a presales team. A respondent who substitutes at interview has demonstrated `VQ-36`'s risk before the contract starts |
| **`VES-23`** | Each interviewee is asked **what percentage of their time is committed** (`VQ-35`) and what else they are committed to. Answers are recorded and become a schedule to the contract under `CO-003` `SOW-56` |
| **`VES-24`** | The architecture is **challenged**, not presented. Three challenges are fixed in advance and identical across respondents: the **`Z4` residency boundary** (`SC-007`), the **outbox as the hottest table** (`PE-006` §4.6), and the **offline conflict-resolution model** (`AR-010`) |
| **`VES-25`** | **The Bengali interview is conducted in Bengali** for the roles `MQ-04` covers. `CG-010` forbids machine translation on field-facing content; an interview is the cheapest place to find out whether the capability exists |

### 7.3 Stage 5 — references and site visit

RFP §17.1 Stage 5: *"Direct contact with references, without the respondent present."*
`VQ-37`…`VQ-42` set the population: ≥ 3 from field service / after-sales / multi-location service,
≥ 2 from South Asia, ≥ 1 from a programme of ≥ 24 months.

| # | Rule |
|---|---|
| **`VES-26`** | **A reference the Company cannot reach without the respondent's assistance is not a reference.** `VQ-41` requires written permission to contact references **directly and without the respondent present**. A contact reachable only through the respondent has not been independently verified, and is recorded as unverified rather than counted toward the `VQ-37`…`VQ-39` minimums |
| **`VES-27`** | The **same seven questions** are asked of every reference, recorded verbatim, and attached to `CO-002-B6`. A reference call without a fixed question set produces an impression, not evidence |
| **`VES-28`** | **`VQ-22` is verified at the reference call.** `VQ-22` requires disclosure of any implementation that failed, was terminated early or was materially re-baselined, and states that *"non-disclosure discovered at reference check is grounds for elimination."* **It is therefore asked directly, of every reference: "was this project re-baselined, and if so why?"** |
| **`VES-29`** | The **site visit** (`VQ-42`) observes the reference client's **live system**, not a presentation about it. What is being tested is whether the system is in daily operational use |

**The seven questions, fixed:**

| # | Question |
|:--:|---|
| 1 | What was the original scope, duration and value band, and what were they at completion? |
| 2 | **Was the programme re-baselined? If so, when, why, and at whose instigation?** (`VQ-22`) |
| 3 | Were the named key personnel the people who actually delivered, for the whole engagement? |
| 4 | What did the respondent do when it discovered it had under-estimated something? |
| 5 | How were change requests priced, and did the rate card hold? |
| 6 | Is the system in daily operational use today, and by how many users? |
| 7 | **Would you buy from them again, for a programme of this size, and what would you do differently in the contract?** |

> **Question 7's second clause is the one that produces the useful answer.** *"Would you buy again"*
> is almost always yes. *"What would you change in the contract"* is where a reference tells you what
> went wrong, and it feeds directly into `CO-003`.

---

## 8. Stage 6 — Commercial Evaluation

### 8.1 What is being compared

RFP §17.1 Stage 6: *"3-year and 5-year TCO analysis, rate-card benchmarking, descope flexibility."*
Criterion 13 carries **2%**.

> **The 2% weight is correct and should be defended**, for the reason RFP §17.2 gives: the reference
> architecture removes licence cost from the comparison, and a 36-month programme fails on
> capability and capacity, not on price. **But 2% only works if the bid-realism safeguards work**,
> and §5.4 shows both are currently broken. A 2% cost weight combined with a stale envelope and a
> stale capacity benchmark means **the evaluation has almost no mechanism left for detecting a bid
> that has misunderstood the scale of the work.** Restoring criterion 7 and §16.1 is what allows
> criterion 13 to stay at 2%.

### 8.2 Normalisation rules — `VES-30`

Bids will not be comparable as submitted. Six differences are known in advance, and each is
normalised before comparison, against `CO-005`'s model.

| # | Difference | Normalisation |
|:--:|---|---|
| 1 | **Hypercare boundary.** RFP §16.2.8 places hypercare inside support and maintenance; `CO-005` §5.6 and §6.4 separate them | Restate every bid with hypercare **separated**, per `CO-005` §6.4's 4–8 week × 9 wave basis. `CVA-06` |
| 2 | **VAT.** RFP §16.2 requires prices exclusive of Bangladesh VAT, with treatment stated separately | Compare **VAT-exclusive**, and record each respondent's residency status separately because it changes `CO-005` §6.1's treatment and §6.2's withholding |
| 3 | **Withholding tax.** A respondent may price net or gross of Bangladesh withholding | **Normalise to gross-of-withholding, borne by the respondent** — the `CO-003` `SOW-42` position. A bid priced net is restated upward by 11.1% on its offshore portion. `CO-005` §6.2 |
| 4 | **FX.** All bids are in USD; the Company's benefit is in BDT | Compare in USD. **Record the FX exposure separately** at `CO-005` §6.7's verified 122.70, and score `SOW-44` risk-sharing proposals under criterion 13 |
| 5 | **Onshore/offshore mix.** RFP §16.2.11 requires both rate cards | Record the mix. It drives §6.2's withholding, `MQ-04`'s Bengali capability and criterion 9's bench-swap risk |
| 6 | **Escalation.** RFP §16.2.11 fixes rates for 24 months, then caps at CPI or 5%, whichever is lower | Restate every bid on the **same escalation assumption** — `CO-005` §6.8's +7% expected. A bid quoting 2026 rates with no escalation has either mispriced its cost base or intends to recover it through change requests |

### 8.3 Rate-card benchmarking

| # | Test | What it detects |
|:--:|---|---|
| 1 | Rate card against `GV-008` §3.2's implied **$348–$564/PW** ($70–$113/day at 5 days) | A rate card far below it is a bid that has not understood the seniority the work needs; far above it, and the effort estimate must justify itself |
| 2 | **Blended rate implied by the total ÷ the effort offered** | The single most useful derived figure. It exposes a bid that has quoted a low rate card and then loaded the effort, or vice versa |
| 3 | **Change-request rate versus the base rate** (`CR-03`) | A change rate materially above the base rate is a bid that plans to make its margin on change |
| 4 | Escalation beyond Month 24 against the **5% cap** and CPI at **8.32%** | Whether the respondent has priced the cap into its initial rate — `CO-005` §6.8 |
| 5 | **Effort offered against `GV-007` §7.1's 1,842 PW build** | The criterion 7 question, expressed commercially |

### 8.4 `VES-13` — Stage 6 cannot open before `D-014`

`GV-008` §9 puts four options to the Board and recommends **option B** — fund Tranche 0 and Tranche
1, re-decide at the Wave 4 gate. `CO-005` §11 re-prices them over five years and adds a fifth.

**Until `D-014` is taken, the Company does not know what it is buying**, and Stage 6 would be
comparing bids for a scope that may be reduced under `CR-08` (*"the Company may award the whole
programme, a subset of waves, or a subset of categories"*).

| # | Rule |
|---|---|
| **`VES-13`** | **`D-014` is taken before Stage 6 opens on 15 February 2027.** If it is not, Stage 6 is conducted against **both** the full scope and the option-B scope, and the award recommendation states both |
| **`VES-31`** | `OPT-01`…`OPT-12` are evaluated as **priced options, not as discounts.** §17.5 item 9 marks down *"pricing that cannot be cleanly descoped"*; the test is whether removing `OPT-01` removes its cost without stranding anything |
| **`VES-32`** | **`OPT-05` (M66 and M67, specifications outstanding) is priced but not awarded** until the specifications exist. Awarding an unspecified module at a fixed price is how a fixed price becomes a change request |

---

## 9. Part B — The Record

### 9.1 Score sheet structure — `CO-002-B2`

One per respondent per assessor. **Completed independently, before any panel discussion**
(`VES-08`).

| Field | Content |
|---|---|
| Respondent · Assessor · Date · Criterion | Identification |
| **Raw score, 0–100** | Against §6.1's bands |
| **Evidence references** | Numbered items from the submission. **A score with no evidence reference is not accepted by the chair** |
| **Deductions applied** | From §6.2's schedule, with the item number |
| **Sample coverage** | For criteria 1 and 2 — which requirements were assessed, per `VES-12f` |
| **Confidence** | High / Medium / Low. A Low-confidence score is escalated to a third assessor rather than averaged |
| **Narrative** | Two to five sentences. The sentence that would be read aloud in a challenge |

### 9.2 Moderation — `VES-08`

| # | Rule |
|---|---|
| **`VES-08`** | Every assessor scores **independently and submits before seeing any other score**. Submitted scores are locked by the chair |
| **`VES-33`** | Moderation reconciles **differences greater than 20 points** on any criterion. Differences below 20 are averaged and the spread is recorded |
| **`VES-34`** | A score changed at moderation is recorded with **the original score, the new score, and the evidence that changed it**. A score changed without new evidence is not a moderation; it is a negotiation |
| **`VES-35`** | The `GV-010` independent observer attends moderation and **may record a dissent** that travels with the award recommendation to the Board (`VES-09`) |
| **`VES-36`** | **Weights are never revisited after bid opening** (`VES-01`). If a weight is discovered to be wrong, that is a `GV-003` decision to amend the RFP by addendum and re-invite, not an adjustment |

### 9.3 The artefacts Part B must contain at award

| ID | Artefact | Produced at | Retention |
|---|---|---|---|
| `CO-002-B1` | Compliance matrix — MQ-01…MQ-12 per respondent, with the verification evidence | Stage 1 | Contract term + 7 years |
| `CO-002-B2` | Score sheets — every assessor, every criterion, every respondent | Stage 2 | As above |
| `CO-002-B3` | Shortlist rationale, including why each eliminated respondent was eliminated | Post-Stage 2 | As above |
| `CO-002-B4` | Demonstration record — `D-01`…`D-12`, with the pass/fail results for `D-03` and `D-09` | Stage 3 | As above |
| `CO-002-B5` | Interview record, including the `VQ-35` time-commitment answers | Stage 4 | As above |
| `CO-002-B6` | Reference record — seven questions, verbatim, per reference; site-visit note | Stage 5 | As above |
| `CO-002-B7` | Normalised commercial comparison against `CO-005` | Stage 6 | As above |
| `CO-002-B8` | **Award recommendation** — §12 | Stage 7 | Permanent |
| `CO-002-B9` | Conflict-of-interest declarations; observer dissents; all respondent correspondence | Throughout | As above |

> **`VES-37` — the record is complete before the award is notified, not after.** A record assembled
> after a challenge arrives is worth less than no record, because its assembly date is discoverable.

---

## 10. Due Diligence

`VES-14` requires verification rather than acceptance. This section says how, for each of the six
gates that can be satisfied on paper by a respondent that cannot satisfy them in fact.

| # | Area | Verification method | Owner |
|:--:|---|---|---|
| 1 | **Financial standing** (`MQ-01`, `VQ-05`, `VQ-06`) | Three years of audited accounts read for: revenue trend, working capital, and **whether this contract would exceed a prudent share of the respondent's revenue**. A contract worth more than roughly a third of annual revenue makes the Company a systemic risk to its own supplier | CFO |
| 2 | **Insurance** (`VQ-10`) | Professional indemnity and cyber liability **certificates of currency**, with cover levels tested against the contract value and against the PDPA 2026 exposure a processor carries | CFO with Legal |
| 3 | **ISO 27001** (`MQ-05`) | **Verified against the certification body's public register**, checking: currency, the certification body's accreditation, and that the **scope statement covers the delivering entity and the delivery location** | CISO |
| 4 | **Reference-project reality** (`MQ-02`) | Requirement counts confirmed **by the client**, not by the respondent. `VES-27`'s question 1 | PMO Lead |
| 5 | **Disclosure honesty** (`VQ-22`, `MQ-10`) | Reference question 2 asked of **every** reference; public litigation and debarment search; cross-check of the respondent's own case-study claims against the references given | Legal Counsel |
| 6 | **Sub-processors and data protection** | The DPA under RFP §19.2 requires sub-processor control. **The sub-processor list is obtained at Stage 6, not at contract**, because a sub-processor in a jurisdiction incompatible with `SC-007`'s residency design is an architectural problem, not a contractual one | CDO with DPO |
| 7 | **Key-personnel availability** (`VQ-36`) | The `VQ-35` percentages from Stage 4, cross-checked against the respondent's **current commitments statement** under `MQ-06`. Two engagements claiming the same architect at 60% is a finding | PMO Lead |

> **`VES-38` — a due-diligence finding is recorded even when it does not change the recommendation.**
> The Board is entitled to know that the recommended respondent's ISO 27001 scope excludes its Dhaka
> delivery centre, even if the panel judges the risk acceptable. Suppressing it converts a managed
> risk into a surprise.

---

## 11. Risk in the Selection Decision

Per ISO 31000 §6.4, the award recommendation records the **residual risk of the recommended
respondent**, not only its merits. Five risks are known before any bid arrives.

| # | Risk | Why it exists before bids are seen | Mitigation available in `CO-003` |
|:--:|---|---|---|
| 1 | **The respondent is too small for the restated scope** | `CVA-07`: MQ-06's gate passes a vendor sized for 61% of the programme | `SOW-56` key-personnel schedule; `SOW-48` capacity re-baseline at each wave start |
| 2 | **Bench-and-swap after award** | §17.5 item 7; `VQ-36` requires approval for substitution but does not price it | `SOW-40`: substitution without approval attracts a defined remedy, not a conversation |
| 3 | **The Company's own capacity, not the vendor's, causes the slippage** | `GV-007` §7.5: 134–201 super-users, none named; `RSK-001` Critical | `SOW-28`: the Company's obligations are **in the contract**, so a delay caused by the Company is identified as such rather than argued about |
| 4 | **Scope reduction after award** (`CR-08`, `D-014`, option B) | The Board may authorise less than the full programme | `SOW-53`: clean descope at wave and category boundaries, priced in advance via `OPT-01`…`OPT-12` |
| 5 | **A single vendor for all 67 modules and 12 portals** | `CR-09` permits multiple awards; concentration risk is real either way | `SOW-36`: step-in rights, source-code escrow, continuous source delivery (`MQ-08`), and the 90-day transition assistance in §19.2 |

---

## 12. The Award Recommendation

### 12.1 Structure — `CO-002-B8`

| § | Content |
|:--:|---|
| 1 | The **instrument**, as baselined, with the date it was frozen and the `GV-003` reference for any change |
| 2 | Respondents received; those eliminated at Stage 1 **and the specific gate each failed** |
| 3 | Stage 2 weighted scores, all respondents, all criteria, with the moderation spread |
| 4 | Stage 3–5 findings, including the `D-03` and `D-09` pass/fail results |
| 5 | The **normalised** commercial comparison against `CO-005` (§8.2) |
| 6 | Due-diligence findings — **including those that did not change the recommendation** (`VES-38`) |
| 7 | The **recommendation**, with the margin over the runner-up |
| 8 | **The residual risk of this award** (§11) and the `CO-003` clauses that mitigate each |
| 9 | The **runner-up position** (§12.4) |
| 10 | The `GV-010` observer's opinion, and any dissent (`VES-35`) |
| 11 | Sample coverage and its limits (`VES-12f`) |

### 12.2 What makes a recommendation defensible

| # | Property |
|:--:|---|
| 1 | The instrument was **fixed before the bids were opened**, and the date is provable |
| 2 | Every score traces to **numbered evidence** in a submission |
| 3 | Every mandatory gate was **verified**, and the verification is attached |
| 4 | The **margin** over the runner-up is stated — and if it is small, that is said rather than concealed |
| 5 | Findings that **weaken** the recommendation are in it |
| 6 | The panel's composition, its declarations, and its independent observer are on the record |

### 12.3 What the Board is being asked to ratify

The Board ratifies an **award**, and an award is not a scoring exercise. `GV-008` §5.3 makes the
funding gates explicit and `GV-001` §7.3 authorises in tranches. The recommendation must therefore
state, in the Board's terms:

| Question | Where it is answered |
|---|---|
| What are we buying, at what price, on what basis? | §5 of the recommendation, normalised per §8.2 |
| Does that price sit inside the authority the Board has given? | Against `GV-008` §5.1's tranches and `CO-005` §7.1 |
| What happens at the Wave 4 gate if we exercise option B? | `CO-003` `SOW-53`; `D-017` |
| What is the exit if this goes wrong, and what does it cost? | §11 risk 5; RFP §19.2; `CO-005` §7.4 |
| What did we not verify? | §11 of the recommendation, per `VES-12f` and `TCO-09`'s principle |

### 12.4 The runner-up position — `VES-11`

| # | Rule |
|---|---|
| **`VES-11`** | The award recommendation names a **runner-up** and states the conditions under which the Company would move to them |
| **`VES-39`** | Proposal validity is **180 days** from 30 October 2026 under `MQ-11` — expiring approximately **28 April 2027**, which is **twelve days after** the 16 April 2027 contract-signature target. **The margin is twelve days.** If negotiation with the preferred respondent fails after 9 April 2027, the runner-up's proposal expires before it can be accepted |
| **`VES-40`** | The Company therefore **requests a validity extension from the runner-up at preferred-respondent notification on 3 March 2027**, not when negotiation fails |

> **`VES-39` is an arithmetic finding, not a judgement.** 30 October 2026 + 180 days = 28 April
> 2027. Negotiation is scheduled 8 March – 9 April 2027 with signature on 16 April. **A negotiation
> that overruns by three weeks leaves the Company with no valid alternative proposal and no leverage
> at all** — which is precisely the position in which the terms in `CO-003` get conceded.

---

## 13. Challenge Defence

1000FiX is a private company and is not subject to public-procurement law. Nonetheless a
disappointed respondent can cause real damage — through the brand partners it shares with 1000FiX,
through the corporate clients whose tenders 1000FiX itself bids for, and through the market's
willingness to bid next time. This table exists so that the answer to each allegation is a document
reference rather than a recollection.

| # | Allegation a disappointed respondent could make | The record that answers it |
|:--:|---|---|
| 1 | *"The criteria were changed after you saw the bids"* | `VES-01`, `VES-36`; Part A's approval date and `GV-003` reference |
| 2 | *"You evaluated against a basis you had already superseded and did not tell us"* | ⚠ **Currently unanswerable.** This is `CVA-02` / `CVA-09`. **Addendum 1 is the answer, and only if it is issued before 17 September 2026** |
| 3 | *"A panel member had a relationship with the winner"* | `VES-03`, `VES-04`; the declarations in `CO-002-B9`, signed before names were disclosed |
| 4 | *"The scores were invented to justify a decision already taken"* | `VES-08`'s locked independent scores; `VES-34`'s moderation trail; `VES-35`'s independent observer |
| 5 | *"You never checked whether the winner's claims were true"* | §10's verification record |
| 6 | *"You eliminated us on a gate you waived for the winner"* | `VES-15`'s recorded Steering Committee decision on every sub-50 score |
| 7 | *"You only read part of our response"* | `VES-12d`'s pre-drawn identical sample; `VES-12f`'s disclosure of coverage |
| 8 | *"The winner was cheapest and you said price was not the driver"* | Criterion 13's 2% weight, disclosed in the RFP; §8's normalised comparison showing what actually drove the margin |

> **Row 2 is the only row in this table with no answer today, and it is the row a competent
> respondent would use.** It is also the only one that can be fixed for the cost of a two-page
> addendum, and only for the next twenty-nine days.

---

## 14. Governing Rules

| # | Rule |
|---|---|
| `VES-01` | The instrument is **frozen before the first envelope is opened**; any later change is a `GV-003` decision circulated to all respondents |
| `VES-02` | **No criterion is scored by one person** |
| `VES-03` | Declarations are signed **before** the respondent list is disclosed to the panel |
| `VES-04` | A declared interest removes the member from **that respondent**, not from the panel |
| `VES-05` | **No hospitality, travel, equipment or gifts** from a respondent between issue and signature |
| `VES-06` | All respondent contact runs through the Head of Procurement; direct approaches are recorded and disclosed to all |
| `VES-07` | `MQ-10` conflict declarations are **verified** against the Company's own records |
| `VES-08` | Independent scoring **before** discussion; scores locked by the chair |
| `VES-09` | The `GV-010` independent reviewer observes Stages 2, 3 and 6 and may record a dissent |
| `VES-10` | References are checked by a member who did **not** score that respondent's technical criteria |
| `VES-11` | A **runner-up** is named, with the conditions for moving to them |
| `VES-12` | Requirement assessment is **sampled to a stated rule**, with statutory and P0-core requirements at 100% |
| `VES-13` | **`D-014` is taken before Stage 6 opens**, or Stage 6 runs both scopes |
| `VES-14` | A mandatory gate is **verified, not read** |
| `VES-15` | A sub-50 score on criteria 1, 3, 4, 5 or 7 triggers a **recorded** eliminate-or-proceed decision |
| `VES-16` | Until Addendum 1 restates it, **`MQ-06` is assessed but not used to eliminate** |
| `VES-17` | A score of **90+ requires a named, contactable instance** |
| `VES-18` | Treatment of RFP §20's disclosures is **scored**, not noted |
| `VES-19` | Demonstration data is **the Company's**, identical for all respondents |
| `VES-20` | Scenarios are scored **immediately**, independently, before discussion |
| `VES-21` | **`D-03` and `D-09` are pass/fail** |
| `VES-22` | **Named key personnel are interviewed**, not a presales team |
| `VES-23` | `VQ-35` time commitments are recorded and become a **contract schedule** |
| `VES-24` | The architecture is **challenged** on three fixed, identical points |
| `VES-25` | The Bengali interview is **conducted in Bengali** |
| `VES-26` | A reference reachable **only through the respondent** is recorded as unverified and does not count toward the `VQ-37`…`VQ-39` minimums |
| `VES-27` | **Seven fixed questions**, recorded verbatim |
| `VES-28` | **`VQ-22` is verified at the reference call** |
| `VES-29` | The site visit observes a **live system in daily use** |
| `VES-30` | Bids are **normalised on six named dimensions** before comparison |
| `VES-31` | `OPT-01`…`OPT-12` are evaluated as **priced options, not discounts** |
| `VES-32` | **`OPT-05` is priced but not awarded** until M66 and M67 are specified |
| `VES-33` | Differences **> 20 points** are moderated; smaller ones are averaged and the spread recorded |
| `VES-34` | A score changed at moderation records **the old score, the new score and the new evidence** |
| `VES-35` | The observer's dissent travels with the recommendation to the Board |
| `VES-36` | **Weights are never revisited after bid opening** |
| `VES-37` | The record is **complete before the award is notified** |
| `VES-38` | A due-diligence finding is **recorded even when it does not change the recommendation** |
| `VES-39` | Proposal validity expires **28 April 2027** — twelve days after the signature target |
| `VES-40` | A **validity extension is requested from the runner-up at notification**, not at failure |

---

## 15. Decisions Recorded

| # | Decision | Options considered | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| `CO-002-D-01` | When to issue this document | After bid opening, containing scores · **Before bid opening, containing the instrument** | **Before, as Part A** | A methodology finalised after the bids are visible is a rationalisation. The date this document was frozen is itself the primary evidence in a challenge | The document carries no scores at v1.0 and is complete only at v2.0, after Stage 7 |
| `CO-002-D-02` | Whether to adopt public-procurement discipline | It does not apply to a private company · **Adopt UNCITRAL principles as practice** | **Adopt as practice** | It is the most widely-tested articulation of a defensible award, and corporate clients increasingly ask suppliers to demonstrate the equivalent | §13's challenge-defence table becomes answerable; the process costs slightly more time |
| `CO-002-D-03` | How to handle the superseded criterion 7 benchmark | Score as published · Ignore the benchmark and score judgement · **Restate it by addendum** | **Addendum** | Scoring as published can eliminate the only respondent who understood the scope. Ignoring it silently is an undisclosed criterion change, which is allegation 1 in §13 | `CVA-09`; §5.4; carried with `CO-005-D-05` |
| `CO-002-D-04` | What to do about MQ-06 | Eliminate on it as written · Delete it · **Assess but do not eliminate, pending Addendum 1** | **Assess, do not eliminate** | The gate is calibrated to a superseded scope and would pass a vendor sized for 61% of the programme while eliminating nobody usefully | `VES-16`; the capacity question moves to criterion 7 where it can be scored |
| `CO-002-D-05` | Whether to sample requirement responses | Assess all 2,930 × 4 · **Sample to a stated rule** | **Sample, and disclose the rule** | 11,700 responses in twenty working days is not assessable. A methodology implying otherwise fails on contact | `VES-12`; statutory and P0-core requirements at 100%; coverage stated in the award recommendation |
| `CO-002-D-06` | Whether `D-03` and `D-09` are scored or pass/fail | Scored, like the other ten · **Pass/fail** | **Pass/fail** | Offline execution and API-layer SoD are architectural properties, not degrees of quality. A 60 on `D-03` means the system does not work offline | `VES-21` |
| `CO-002-D-07` | Whether to record due-diligence findings that do not change the recommendation | Report only material findings · **Record all** | **Record all** | Suppressing an immaterial finding converts a managed risk into a surprise, and the Board is entitled to the same information the panel had | `VES-38` |

---

## 16. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| `VES-Q-01` | Who is the **third assessor for criterion 2**, which covers eight module categories? | Head of Procurement | **Stage 0** | `VES-02` |
| `VES-Q-02` | Is **RFP §12.7's team model restated or withdrawn** in Addendum 1 (`CVA-08`)? | Head of Procurement | **17 Sept 2026** | `MQ-06`; criterion 7; criterion 9 |
| `VES-Q-03` | Will **`RQ-003`'s fit-gap** be complete before Stage 2 opens on 9 November 2026? | Solution Architect | **9 Nov 2026** | Criteria 1, 2; §17.5 item 2's over-classification test |
| `VES-Q-04` | **Which work streams are in the respondent's scope** — build only, or build plus content, definition and design? | Programme Director | **17 Sept 2026** | `MQ-06`; §16.2.2's discipline list; the whole commercial comparison |
| `VES-Q-05` | Will the Company exercise **`CR-09`** and award to more than one respondent? | Steering Committee | Stage 6 | §11 risk 5; `CO-003`'s structure |
| `VES-Q-06` | Does **ISO/DIS 44001** supersede the 2017 edition during this procurement, and does it change anything relied on here? | Head of Procurement | Stage 6 | §2.1; `PG-M4` currency |
| `VES-Q-07` | Has the **runner-up validity extension** been requested (`VES-40`)? | Head of Procurement | **3 Mar 2027** | `VES-39`'s twelve-day margin |
| `VES-Q-08` | Has **`D-014`** been taken? | Board | **15 Feb 2027** | `VES-13`; the entire commercial comparison |

> An open question with no owner and no needed-by date is not an open question — it is an unrecorded
> risk. All eight are escalated to `GV-005` RAID at issue.

---

## 17. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| `AC-01` | Part A is **approved and frozen before 30 October 2026**, with a provable date | Steering Committee minute; `GV-011` configuration record |
| `AC-02` | Every one of RFP §15.1's **twelve mandatory gates** has a stated evidence test **and a stated non-satisfying case** | §5.1 |
| `AC-03` | The **thirteen weights are verified to sum to 100** and the 50% functional/technical claim is checked | §5.3 |
| `AC-04` | The **ten §17.5 marked-down behaviours** are converted into a deduction schedule with named criteria | §6.2 |
| `AC-05` | A **sampling rule** exists, with statutory and P0-core coverage at 100%, and coverage is disclosed | §6.3; `VES-12` |
| `AC-06` | **Six normalisation rules** exist so bids are comparable against `CO-005` | §8.2 |
| `AC-07` | Every mandatory gate that can be satisfied on paper has a **verification method and an owner** | §10 |
| `AC-08` | The **challenge-defence table** exists, and every row has a named record — or is explicitly marked unanswerable | §13 |
| `AC-09` | **`CVA-07`, `CVA-08` and `CVA-09`** are raised with dated, owned actions | §5.4, §5.5, §5.6 |
| `AC-10` | The **runner-up validity arithmetic** is computed, not assumed | §12.4; `VES-39` |
| `AC-11` | Panel composition gives **every criterion at least two independent assessors**, verified by enumeration | §3.1 |
| `AC-12` | The local rule prefix `VES-nn` was **verified to zero occurrences** workspace-wide before allocation | Header note |
| `AC-13` | *(v2.0)* Part B is complete — `CO-002-B1` through `CO-002-B9` — before the award is notified | §9.3; `VES-37` |

**Definition of done.** Version 1.0 is complete when Part A is approved and frozen. **Version 2.0 is
complete when Part B is populated, the award recommendation is ratified by the Board, and `PGD-000`
records `CO-002` as ✅ with a fresh enumeration date.**

---

## 18. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | `CO-001` — the RFP | The instrument this document applies. §15, §16, §17, §18, §19, §20 |
| Upstream | `CO-005` | The cost model Stage 6 normalises against; `CVA-02` |
| Upstream | `GV-007`, `GV-008` | The effort and cost bases that supersede the RFP's published figures |
| Upstream | `GV-002` | Panel authority and decision rights |
| Upstream | `RQ-003` | The fit-gap criteria 1 and 2 depend on — `VES-Q-03` |
| Upstream | `SC-008` | The statutory obligations criterion 5 tests, and `VES-12c`'s 100% sampling population |
| Downstream | `CO-003` | Receives the award. §11's five risks map to named `SOW-nn` clauses |
| Downstream | `CO-004` | The respondent's licence obligations under RFP §19.1(4) enter `CO-004`'s register at award |
| Downstream | `CO-006` | The rate card and the L6 positions inform the procurement plan |
| Downstream | `GV-008` | The contract price becomes committed money under `CB-09` |
| Lateral | `GV-003` | `D-014` gates Stage 6; `CO-002-D-03` requires a new `D-nnn` for the addendum |
| Lateral | `GV-005` | Eight open questions and three findings escalated at issue |
| Lateral | `GV-010` | Supplies the independent observer (`VES-09`, `VES-35`) |
| Lateral | `GV-011` | Holds Part A's frozen version and its approval date — the primary challenge-defence evidence |

---

## 19. References

**Within this repository**
`../PGD-000_Master_Register_of_Project_Guiding_Documents.md` ·
`./_CATEGORY_OVERVIEW.md` · `./CO-003_Statement_of_Work_and_Deliverable_Acceptance_Schedule.md` ·
`./CO-004_Licence_and_Open_Source_Compliance_Register.md` ·
`./CO-005_Total_Cost_of_Ownership_Model.md` · `./CO-006_Procurement_and_Purchase_Plan.md` ·
`../00_Programme_Governance_and_Control/GV-002_Governance_Framework_RACI_and_Terms_of_Reference.md` ·
`../00_Programme_Governance_and_Control/GV-003_Decision_Log_and_Change_Control_Procedure.md` ·
`../00_Programme_Governance_and_Control/GV-005_RAID_Register.md` ·
`../00_Programme_Governance_and_Control/GV-007_Estimation_Model_and_Resource_Plan.md` ·
`../00_Programme_Governance_and_Control/GV-008_Programme_Budget_and_Cost_Baseline.md` ·
`../00_Programme_Governance_and_Control/GV-010_Programme_Assurance_and_Independent_Review_Plan.md` ·
`../00_Programme_Governance_and_Control/GV-011_Documentation_Control_and_Configuration_Management_Plan.md` ·
`../01_Requirements_Engineering/RQ-003_*.md` ·
`../05_Security_Privacy_and_Compliance/SC-008_Regulatory_Compliance_Obligations_Register.md`

**Workspace**
`../../primary-doc/1000FiX_ERP_System_Comprehensive_RFP.md` — §12.7, §15, §16, §17, §18, §19, §20 ·
`../../1000fix_ERP_Module/06_Delivery_and_Implementation/06-01_Implementation_Roadmap_and_Phasing.md`

**External standards** *(all verified 2026-08-19)*

| Source | Used for |
|---|---|
| **ISO 37500:2014**, *Guidance on outsourcing* — §5 strategy, §6 supplier selection | §4's stage structure; §10's due diligence |
| **ISO 44001:2017**, *Collaborative business relationship management systems — Requirements and framework*, stages 1–4. **Note: ISO/DIS 44001 is in the enquiry phase** and may supersede the 2017 edition — `VES-Q-06` | §3, §10, §11, §12 |
| **ISO 21502:2020** §7.14, *Project, programme and portfolio management — Guidance on project management* | The procurement practice |
| **ISO 19011:2018** §6.4, §7, *Guidelines for auditing management systems* | `VES-08`'s independence, `VES-14`'s verification-not-acceptance rule |
| **ISO 31000:2018** §6.4 | §11's residual-risk record |
| **ISO/IEC 27001:2022** | `MQ-05`; §10.3's register verification |
| **UNCITRAL Model Law on Public Procurement (2011)**, Arts. 9, 11, 22, 24, 25 | Adopted as practice, not law — `CO-002-D-02`; §13 |

> Verify every path resolves before issuing. Nine module files carried references to superseded
> filenames until the August 2026 audits corrected them.

---

## 20. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-19 | Head of Procurement, with Enterprise Architecture | **Initial issue — Part A, the evaluation instrument.** Contains no scores by design (`CO-002-D-01`). Raises `CVA-07` (MQ-06 calibrated to a superseded scope), `CVA-08` (disciplines priced but unstaffed in §12.7) and `CVA-09` (both bid-realism safeguards broken by the same stale figure). Computes the `VES-39` twelve-day validity margin | ERP Steering Committee |
| *2.0 (planned)* | *Post-Stage 7, by 3 Mar 2027* | *Head of Procurement* | *Part B — the record, and the award recommendation* | *Steering Committee → Board* |

---

*`CO-002` · Category 14 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
