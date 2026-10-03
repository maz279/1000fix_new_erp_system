---
id: GV-002
title: Governance Framework, RACI & Terms of Reference
category: 00 — Programme Governance & Control
code: GV
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-18
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Programme Director
approver: Chief Executive Officer, on authority of GV-001
standards_basis: ISO/IEC 38500:2024 · ISO 21503:2022 §governance · ISO 21502:2020 §6 · PMBOK Guide 7th Edition · PRINCE2 7th Edition (2023) · COBIT 2019 (governance/management split)
traces_to: PGD-000 GV-002 · findings PGD-A1-09, AF-09/R-07, OP-04, R-05 · 00-04 §5 · GV-001 §3.2
depends_on: GV-001
verified_on: 2026-08-18
enumerated_on: 2026-08-18 02:06 (+06)
priority: P0
needed_by: Now
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# GV-002 — Governance Framework, RACI & Terms of Reference
# 1000FiX ERP System & Portal Suite v2.0

### Category 00 · Code `GV` · ISO/IEC 38500:2024 · ISO 21503:2022 · PRINCE2 7

---

> **This document closes the lower half of the governance circularity.** `PGD-A1-09` records that
> `PGD-000` nominates the ERP Steering Committee as its approver, that the Committee's terms of
> reference do not exist, and that this is true of **all 610 files in the workspace**. `GV-001`
> gives the Board's authorisation; this document constitutes the bodies that authorisation creates.
> Neither closes the finding alone.

---

## 1. Purpose

This document constitutes the governance of the 1000FiX ERP programme. It names every decision-
making body, states who sits on it, what it may decide, what it may not decide, how many people
must be present for a decision to stand, how often it meets, what it must be given before it
meets, and what it must produce afterwards.

It exists because the programme currently has a governance **diagram** (`00-04` §5.1) and no
governance **instrument**. A diagram tells you a Steering Committee exists. It does not tell you
whether four members constitute a quorum, whether the CTO may approve a Critical risk in the
CEO's absence, or what happens when two bodies both believe they own a decision — which has
already occurred: audit `OP-04` found **severity classification had three claimed owners**.

### 1.1 Scope

**In scope:**

| # | Covered |
|---|---|
| 1 | The governance model and its standards basis (ISO/IEC 38500:2024 EDM) |
| 2 | The organisation chart of decision-making bodies, and what changed from `00-04` §5.1 |
| 3 | Terms of reference for each of the nine bodies — purpose, membership, chair, quorum, cadence, inputs, outputs, decision rights, escalation |
| 4 | The programme decision-rights matrix: every decision class and the single body that owns it |
| 5 | The programme RACI across 24 activity classes |
| 6 | Allocation of the fifteen open decisions `D-01`…`D-15` to an empowered body |
| 7 | Delegation, deputisation and absence |
| 8 | Independence, conflict of interest, and the separation of assurance from delivery |
| 9 | Governance of the governance: how this document is changed, and the review cadence |

**Explicitly out of scope:**

| Topic | Owned by | Why the boundary sits here |
|---|---|---|
| The authority the Board confers on the programme | `GV-001` | A body cannot constitute itself; it is constituted by the charter |
| The decision **log** and the change-control **procedure** | `GV-003` | This document says *who decides*; `GV-003` says *how a decision is recorded and how a baseline is changed* |
| Wave gate criteria and the evidence standard | `GV-009` | This document constitutes the assessor; `GV-009` defines what they assess against |
| The assurance and independent review **plan** | `GV-010` | This document establishes independence as a principle; `GV-010` schedules and resources it |
| System role and permission model (`R01`–`R46`) | `SC-004`, `05-04` | Programme governance roles are organisational; system roles are technical. **They are different identifier spaces and must not be conflated** |
| Content review gates `G1`–`G6` | `CG-007` | Content approval is a subordinate workflow inside workstream 5 |

### 1.2 Intended audience

| Audience | What they use this document for |
|---|---|
| **CEO** | The instrument under which they constitute and chair the Steering Committee |
| **Steering Committee members** | Their own terms of reference: what they are being asked to decide, and what they may not decide |
| **Programme Director / PMO** | The escalation routes, the meeting calendar, the secretariat obligations |
| **CTO and Architecture Review Board** | The boundary between architectural authority and Steering Committee authority |
| **Chair of the Audit Committee** | The independence provisions in §8, and the reporting line for assurance |
| **Every document author in the estate** | The answer to "who approves this?" — §5 gives it per artefact class |
| **Implementation vendor** | Who they escalate to, and who can and cannot commit the Company |

---

## 2. Basis and Inputs

### 2.1 Standards conformance

| Standard | Clause / concept | How this document conforms | Departure and rationale |
|---|---|---|---|
| **ISO/IEC 38500:2024** *(edition 3, February 2024)* | Six principles; the governance model **Engage stakeholders → Evaluate → Direct → Monitor**; the governance framework (direction, capability, policy, delegation, performance measurement, accountability) | §3 expresses the Board and Steering Committee roles in EDM terms. §4 terms of reference state each body's Evaluate / Direct / Monitor duties explicitly. §8 realises the *accountability* framework element | The standard addresses governance of IT for the whole organisation; this document applies it to one programme. That is a narrowing, stated here |
| **COBIT 2019** | The governance/management separation — *governing bodies evaluate, direct and monitor; management plans, builds, runs and monitors* | The Board and Steering Committee govern; the PMO, ARB and squads manage. No body does both | Not adopted as a control framework, only as the separation principle |
| **ISO 21503:2022** | Programme governance; programme board; programme manager; benefits ownership | §4.2 Steering Committee is the programme board; §4.6 PMO is the programme management function | None |
| **ISO 21502:2020** §6 | Project governance; sponsor; project board; assurance separate from delivery | §4.9 Delivery Squads and §8 independence | None |
| **PRINCE2 7th Edition (2023)** | Project Board roles — Executive, Senior User, Senior Supplier; **management by exception**; assurance independent of the Project Manager | §4.2 maps Executive → CEO, Senior User → Business Owners Council chair, Senior Supplier → CTO. §8.3 separates assurance from delivery, which PRINCE2 requires and the programme currently breaches | The three PRINCE2 Project Board roles are mapped onto an existing seven-member committee rather than replacing it, because the committee is already named in `00-04` and in eleven downstream documents |
| **ISO 9001:2015** clauses 5.1, 5.3 | Leadership commitment; organisational roles, responsibilities and authorities | §5 RACI; §4 accountability statements | None — the Company's ISO 9001 certification requires this to exist anyway |

### 2.2 Source material relied on

| Source | Location | What it establishes |
|---|---|---|
| Risks, Assumptions, Dependencies & Governance | `../../1000fix_ERP_Module/00_Governance_and_Charter/00-04` §5 | The existing governance diagram, decision rights, cadence, change-control flow and reporting matrix — the baseline this document formalises |
| Programme Charter & Mandate | [`GV-001`](GV-001_Programme_Charter_and_Mandate.md) §3.2, §8 | The authority conferred, and the tolerance model these bodies operate within |
| Content Operating Model and RACI | `../../project_content/00_Content_Governance_and_Standards/CG-002` §2, §3, §7 | The content workstream's roles, classes and escalation path — incorporated here as workstream 5's governance |
| Review, Approval and Sign-off Workflow | `../../project_content/00_Content_Governance_and_Standards/CG-007` | The `G1`–`G6` content gate model, referenced not restated |
| Register Integrity Audit | `../_AUDIT/PGD-AUDIT-001` | `PGD-A1-09` — no constituted body can baseline anything |
| Content & Repository Integrity Audit | `../../project_content/_AUDIT/AUDIT-001` | `AF-09` and recommendation `R-07` — content has no governance seat |
| Category 17 OP Content Audit | `../../project_content/_AUDIT/AUDIT-017` | `OP-04` — severity classification had three claimed owners |
| Category 16 CM Content Audit | `../../project_content/_AUDIT/AUDIT-019` | *"1 critical, against the auditor's own authoring"* — the independence problem |

### 2.3 Audit findings this document closes

| Finding | Source | How this document closes it |
|---|---|---|
| `PGD-A1-09` | `PGD-AUDIT-001` | §4.2 gives the Steering Committee written terms of reference, a quorum and a defined authority to baseline. **Closed jointly with `GV-001`; neither closes alone** |
| `R-05` | `PGD-AUDIT-001` | *"Constitute the Steering Committee before any further document claims it as approver."* §4.2 and the constitution schedule in §9.1 |
| `AF-09` / `R-07` | `AUDIT-001` | §4.7 constitutes the **Content Council** and gives the Programme Content Lead a governance seat. Previously accountable with no seat — `CG-002` §2 records this as a "constitutional gap" |
| `OP-04` | `AUDIT-017` | §5.2 allocates incident severity classification to exactly one owner. Three claimed owners is a decision-rights defect, not an operational one |
| `H2-07`, `H2-06` | `00-07` | §6 rules that programme governance roles and system roles (`R01`–`R46`, `SOD-01`–`SOD-30`) are separate identifier spaces with separate allocating authorities, preventing the class of collision found there |
| `AUDIT-019` observation | `AUDIT-019` | §8 makes assurance independent of delivery and reports it to the Audit Committee, not the CTO. **Partially** — `GV-010` resources it |

---

## 3. The Governance Model

### 3.1 Governance is not management

```
  ┌──────────────────────────────────────────────────────────────────────────┐
  │  GOVERN            ENGAGE STAKEHOLDERS → EVALUATE → DIRECT → MONITOR     │
  │  (ISO/IEC 38500:2024)                                                    │
  │                                                                          │
  │  Board of Directors ─────────── authorises, sets tolerance, monitors     │
  │  Audit Committee ────────────── independent assurance, receives findings │
  │  ERP Steering Committee ─────── directs the programme within tolerance   │
  └────────────────────────────────────┬─────────────────────────────────────┘
                                       │  direction · tolerance · decisions
                                       ▼
  ┌──────────────────────────────────────────────────────────────────────────┐
  │  MANAGE            PLAN → BUILD → RUN → MONITOR                          │
  │                                                                          │
  │  PMO · Architecture Review Board · Change Advisory Board ·               │
  │  Business Owners Council · Content Council · Data Protection Forum ·     │
  │  Delivery Squads                                                         │
  └──────────────────────────────────────────────────────────────────────────┘
                                       │  evidence · escalation · reporting
                                       └──────────────► back to GOVERN
```

**The rule this enforces:** *no body both directs work and assures it.* The Architecture Review
Board sets standards and reviews compliance with them, which is a management activity. Independent
assurance that the standards are adequate is a governance activity and sits with the Audit
Committee. Four audits to date have been produced by the function that authored the material
(`AUDIT-019`, `PGD-AUDIT-001` §12), which is the breach this separation corrects.

### 3.2 The structure

```
                        ┌────────────────────────────────────┐
                        │  BOARD OF DIRECTORS                │
                        │  Investment · tolerance · closure  │
                        │  Quarterly                         │
                        └──────┬──────────────────────┬──────┘
                               │                      │
              ┌────────────────▼──────────┐   ┌───────▼─────────────────────┐
              │  ERP STEERING COMMITTEE   │   │  AUDIT COMMITTEE            │
              │  CEO (chair) · CTO · CFO  │   │  ◄── NEW at this document   │
              │  CCO · Ops Dir · HR Dir   │   │  Independent assurance      │
              │  Quality Mgr · Prog Dir   │   │  Receives every audit       │
              │  Monthly                  │◄──┤  Quarterly · GV-010         │
              └──────┬────────────────────┘   └─────────────────────────────┘
                     │
   ┌─────────────────┼───────────────┬────────────────┬───────────────────┐
   │                 │               │                │                   │
┌──▼──────────┐ ┌────▼─────────┐ ┌───▼──────────┐ ┌───▼───────────┐ ┌─────▼────────┐
│ PROGRAMME   │ │ ARCHITECTURE │ │ CHANGE       │ │ BUSINESS      │ │ DATA         │
│ MANAGEMENT  │ │ REVIEW BOARD │ │ ADVISORY     │ │ OWNERS        │ │ PROTECTION   │
│ OFFICE      │ │ (Design      │ │ BOARD        │ │ COUNCIL       │ │ FORUM        │
│ Weekly      │ │  Authority)  │ │ ◄── NEW      │ │ 11 category   │ │ ◄── NEW      │
│ Plan · Risk │ │ Fortnightly  │ │ Fortnightly  │ │ owners        │ │ Monthly      │
│ Report · CR │ │ Standards    │ │ CRs · impact │ │ Fortnightly   │ │ PDPA · DPIA  │
└──┬──────────┘ └──────────────┘ └──────────────┘ └───────────────┘ └──────────────┘
   │
   ├────────────────────────────┐
   │                            │
┌──▼────────────────────┐  ┌────▼─────────────────────────────────────────────────┐
│ CONTENT COUNCIL       │  │ DELIVERY SQUADS                                      │
│ ◄── NEW (AF-09 R-07)  │  │ Service · Commercial · Supply · Finance · People ·   │
│ Programme Content Lead│  │ Platform · Data · Portals & Apps                     │
│ Fortnightly           │  │ Daily stand-up · Fortnightly sprint                  │
└───────────────────────┘  └──────────────────────────────────────────────────────┘
```

### 3.3 What changed from `00-04` §5.1, and why

| Change | Reason |
|---|---|
| **Audit Committee added** as a Board sub-committee | Four audits have been produced by the authoring function. `AUDIT-019` recorded *"1 critical, against the auditor's own authoring"*. Assurance reporting into the CTO is not assurance. Recommendation `R-07` |
| **Change Advisory Board split out of the Steering Committee** | `00-04` §5.4 routes every P0/P1 or cross-module change to a body that meets **monthly**. Scope has already moved 11 → 30 → 67; a monthly change body on a 36-month programme is a queue, not a control |
| **Content Council added** | `CG-002` §2 records a *"constitutional gap"* — the Content Lead has accountability for 520–775 PW with no governance seat. `AF-09`, `R-07` |
| **Data Protection Forum added** | The PDPA 2026 reaches enforcement inside Wave 4. `RSK-032`–`RSK-035`, `D-13`, `D-15`, `DEP-31`…`DEP-35` are spread across the CTO, CFO, CEO and Legal with no body that convenes them |
| **Business Owners Forum → Business Owners Council, 11 seats not 17** | `00-04` §5.1 and `CG-002` §3 both constitute *"17 module owners"* — a figure from the **30-module** architecture. With 67 modules in 11 categories, 17 seats leaves 50 modules unrepresented. Recorded as finding `PGD-A2-02` |
| **Programme Director added to the Steering Committee** | `00-04` §5.1 lists seven executive members and no delivery accountable. A committee that receives a report with no author present cannot interrogate it |
| **"Architecture Review Board" designated the Design Authority** | The register (`AR-004`, `AR-012`) assumes a standing design authority. The ARB is it; naming it prevents a tenth body being invented |

---

## 4. Terms of Reference

Each body below is constituted by this document. **A body may not act until its terms of
reference are approved and its first meeting is minuted** — rule `GV-002-R1`.

### 4.1 Board of Directors

| Attribute | Provision |
|---|---|
| **Purpose** | To authorise the programme, set its tolerance, monitor delivery against the charter, and close or stop it |
| **Chair** | Chair of the Board |
| **Membership** | Board members; CEO in attendance; CTO and CFO in attendance for programme items; Programme Director presenting |
| **Quorum** | Per the Company's articles of association |
| **Cadence** | Quarterly for programme review; ad hoc on a tolerance breach |
| **Evaluate** | The business case (`BM-003`), the cost baseline (`GV-008`), benefit realisation (`BM-004`), the independent assurance report (`GV-010`) |
| **Direct** | Approves `GV-001`; sets programme tolerance (`GV-001` §8.1); authorises Waves 5–9 at the Wave 4 gate; directs descope on a tolerance breach |
| **Monitor** | Quarterly Board pack; the Month 42 independent benefits audit |
| **Decides** | Programme investment and continuation · programme closure · any change to a chartered objective (`GV-001` §4.1 tier 1) · acceptance of a Critical risk · a breach of programme tolerance |
| **Must not decide** | Anything inside tolerance. A Board that takes wave-level decisions destroys the exception model and the accountability that goes with it |
| **Inputs required 5 working days before** | Board pack; the Steering Committee minute recommending the item; the assurance opinion where one exists |
| **Outputs** | Minuted resolution, recorded in `GV-003` within 2 working days |
| **Escalates to** | — |

### 4.2 ERP Steering Committee

| Attribute | Provision |
|---|---|
| **Purpose** | To direct the programme within the tolerance the Board has set; to take every decision the Board has not reserved and no subordinate body owns |
| **Chair** | **Chief Executive Officer** — also the Executive Sponsor, and the PRINCE2 *Executive* role |
| **Membership** | CEO (chair) · CTO *(Senior Responsible Owner; PRINCE2 Senior Supplier)* · CFO · CCO · Service Operations Director · HR Director · Quality Manager · **Programme Director** *(secretary, non-voting)* · Chair of the Business Owners Council *(PRINCE2 Senior User)* |
| **Quorum** | **Five voting members, of whom the CEO or a written delegate must be one, and at least one of the CFO or CTO** |
| **Cadence** | Monthly, and at every wave gate |
| **Evaluate** | PMO report; risk heat; benefit variance; change requests above PMO authority; gate evidence packs |
| **Direct** | Wave Go/No-Go; scope change on P0/P1; acceptance of High risks; approval of every baselined document in `PGD-000`; release of wave funding |
| **Monitor** | Monthly programme dashboard; monthly KPI dashboard; adoption report during rollout; open audit findings |
| **Decides** | See §5.2. In summary: wave gates, P0/P1 scope, High-risk acceptance, cost within programme tolerance, document baselining, and the arbitration of any dispute between two subordinate bodies |
| **Must not decide** | Architecture standards (`ARB`) · technical severity classification (`ARB` on the CTO's authority) · content approval within class (`Content Council`) · anything the Board has reserved |
| **Inputs required 3 working days before** | PMO pack: progress, risk, issues, decisions requested, each with a recommendation and an option set |
| **Outputs** | Minute; every decision written to `GV-003` within **2 working days** with a `D-nnn` identifier |
| **Escalates to** | Board, on tolerance breach or a reserved matter |

> **`PGD-A1-09` is closed by this clause.** From the date of its first minuted meeting, the ERP
> Steering Committee is a constituted body with written terms of reference, a defined quorum and
> an explicit authority to baseline documents in `PGD-000`. Until that meeting, **no document in
> the workspace may state that it is approved**, and `PGD-000` §3 change control is inoperative.

### 4.3 Audit Committee *(new)*

| Attribute | Provision |
|---|---|
| **Purpose** | To obtain independent assurance that the programme is what it is reported to be |
| **Chair** | A non-executive director, or the Board Chair where no non-executive is appointed |
| **Membership** | Chair · one further Board member · Quality Manager *(ISO 9001 interface, non-voting)* · external reviewer where engaged. **The CTO and the Programme Director attend by invitation only and do not vote** |
| **Quorum** | Two, of whom the chair must be one |
| **Cadence** | Quarterly, and before every wave gate from Wave 4 onward |
| **Evaluate** | All audit reports; the assurance plan (`GV-010`); management responses; the open-findings register |
| **Direct** | Commissions independent review; sets the assurance scope; may require a finding to be reopened |
| **Monitor** | Findings ageing; recurrence — the estate has now recorded the *same* arithmetic defect four times |
| **Decides** | Whether an audit finding is closed · whether a reviewer is independent · whether a gate may be signed where an open Critical finding exists |
| **Must not decide** | Anything about delivery. An assurance body that directs the work it assures is not independent |
| **Escalates to** | Board directly, without passing through the Steering Committee |

> **Why the reporting line matters.** `PGD-AUDIT-001` §12 records its own independence as
> *"Not independent"* and notes that it consequently missed its own arithmetic error twice.
> Assurance that reports to the function it assures will find what that function already knows.

### 4.4 Architecture Review Board *(Design Authority)*

| Attribute | Provision |
|---|---|
| **Purpose** | To set, publish and enforce the architecture standards, and to be the single authority on technical design decisions |
| **Chair** | Chief Technology Officer |
| **Membership** | CTO (chair) · Solution Architect · Data Architect · Security Lead · Integration Lead · squad tech leads · Platform Engineering Lead |
| **Quorum** | Four, including the CTO or the Solution Architect, and the Security Lead for any security-affecting decision |
| **Cadence** | Fortnightly; ad hoc for a blocking decision with a 48-hour turnaround |
| **Evaluate** | Design proposals; deviations from standard; new technology requests; fitness-function results (`AR-012`) |
| **Direct** | Publishes `AR-004` Architecture Decision Records; approves L4/L5 technology selection; approves module boundary adjudications (`AR-005`) |
| **Monitor** | Architecture compliance; technical debt (`BE-009`); dependency and licence obligations (`BE-007`) |
| **Decides** | Architecture standard change · technology selection at L4/L5 · module boundary disputes · schema change affecting more than one module · API contract breaking change · incident **severity taxonomy** *(closing `OP-04`)* |
| **Must not decide** | Commercial components at L6 — that is the CFO on ARB recommendation · scope · schedule · anything with a cost impact above the PMO threshold |
| **Outputs** | An ADR per significant decision, in `AR-004`, within 5 working days. **A decision with no ADR is not a decision** — `GV-002-R2` |
| **Escalates to** | Steering Committee where a standard change has cost, schedule or scope impact |

### 4.5 Change Advisory Board *(new)*

| Attribute | Provision |
|---|---|
| **Purpose** | To assess and dispose of change requests below Steering Committee reservation, at a cadence a 36-month programme can absorb |
| **Chair** | Programme Director |
| **Membership** | Programme Director (chair) · Solution Architect · QA Lead · the affected Business Owner · Content Lead where content is affected · Finance Business Partner for any cost impact |
| **Quorum** | Three, including the chair and the affected Business Owner |
| **Cadence** | Fortnightly; emergency change by written procedure within 24 hours |
| **Decides** | P2/P3 change within a module · cross-module change with **no** cost impact and **no** wave impact · reallocation of scope between waves inside the same tranche · rejection or deferral of any change |
| **Must not decide** | P0/P1 change · anything with a cost impact · anything that moves a wave gate date · anything touching a chartered objective |
| **Outputs** | Change request disposition recorded in `GV-003` §6 change log within 2 working days |
| **Escalates to** | Steering Committee |

### 4.6 Programme Management Office

| Attribute | Provision |
|---|---|
| **Purpose** | To plan, track, report and control; to be the secretariat of the Steering Committee; to own the registers |
| **Head** | Programme Director |
| **Membership** | Programme Director · planners · risk and issue manager · reporting analyst · configuration librarian *(owner of `GV-011`)* |
| **Cadence** | Weekly internal; weekly report to the Steering Committee chair |
| **Owns** | `GV-003` decision log · `GV-004` plan and schedule · `GV-005` RAID · `GV-006` scope baselines · `GV-011` configuration register · the meeting calendar |
| **Decides** | Medium and low risk acceptance · P2/P3 scope inside a module with the business owner · schedule adjustment inside wave tolerance · document status transitions in `PGD-000` (without a change request, per `PGD-000` §3) |
| **Must not decide** | Anything with cost impact · anything a named body above owns |
| **Escalates to** | Steering Committee weekly; immediately on a forecast tolerance breach |

### 4.7 Content Council *(new — closes `AF-09` / `R-07`)*

| Attribute | Provision |
|---|---|
| **Purpose** | To govern workstream 5: the 477-file content estate on which configuration, training, statutory compliance and field adoption depend |
| **Chair** | Programme Content Lead |
| **Membership** | Programme Content Lead (chair) · Content Design Lead · Localisation Lead · Master Data Owner · Legal & Compliance Content Owner · one Domain Content Owner per active category · L&D representative |
| **Quorum** | Three, including the chair and the owner of the affected content class |
| **Cadence** | Fortnightly |
| **Decides** | Content approval within classes **C**, **D** and **E** per `CG-002` §5 · content schedule and sequencing · translation and linguistic sign-off (`CG-010`, `BN-018`) · retirement of content |
| **Must not decide** | Class **A** statutory content — CFO or Legal Counsel with external verification · Class **B** legal/contractual — Legal Counsel · anything with a cost impact |
| **Escalates to** | PMO, then Steering Committee. For statutory content, directly to the Data Protection Forum or Legal |
| **Reports** | Content burn-up, bilingual pair completeness, and the class A/B approval queue to the PMO weekly |

> **`CG-002` §2 records this as a "constitutional gap": the Content Lead has accountability
> without a governance seat.** This clause is that seat. It does not fund the workstream —
> `GV-007` sizes it and `GV-008` funds it.

### 4.8 Data Protection Forum *(new)*

| Attribute | Provision |
|---|---|
| **Purpose** | To hold the programme's obligations under the Personal Data Protection Act 2026 and to convene the decisions that are currently spread across four executives with no meeting |
| **Chair** | Chief Data Officer where appointed; otherwise the CFO *(interim, per `RSK-034`)* |
| **Membership** | Chair · Legal Counsel · CTO · Security Lead · Quality Manager · Programme Content Lead *(transparency notices, consent copy)* |
| **Quorum** | Three, including Legal Counsel and the CTO or Security Lead |
| **Cadence** | Monthly to Wave 4; fortnightly from Wave 4 *(enforcement activates ~13 May 2027)* |
| **Evaluate** | `SC-003` DPIA · `SC-007` residency design · `DA-005` classification · `DA-006` retention · breach reports · the `DEP-31`…`DEP-35` regulatory dependencies |
| **Direct** | Approves the lawful basis for each processing purpose; approves cross-border transfer safeguards; approves the breach notification procedure to the National Data Management Authority |
| **Decides** | Whether a processing activity may proceed · whether a DPIA is required · whether a breach is notifiable |
| **Must not decide** | The architecture that realises its decisions — that is the ARB · the appointment of a Chief Data Officer — that is the CEO (`D-15`) |
| **Escalates to** | Steering Committee, and directly to the Board where a statutory obligation is at risk |

> **Why this body exists.** `RSK-032`–`RSK-035` name the CFO, CTO, CEO and Legal as owners of five
> interlocking data-protection risks. `D-13` (residency) needs the CTO, CFO and Legal in one room
> and is described as *"the most urgent open decision in the programme"*. There is currently no
> room. Penalties reach **BDT 25 lakh**, or **BDT 50 lakh** for a significant data fiduciary.

### 4.9 Business Owners Council

| Attribute | Provision |
|---|---|
| **Purpose** | To represent the business in requirement decisions, UAT acceptance and adoption |
| **Chair** | Elected annually from the membership; the chair holds the PRINCE2 *Senior User* seat on the Steering Committee |
| **Membership** | **Eleven category owners** — one per module category A–K, per `00-02` §4 — plus the Branch Operations representative and the Marketplace/Partner representative from Wave 6 |
| **Quorum** | Six category owners |
| **Cadence** | Fortnightly |
| **Decides** | Requirement acceptance at UAT *(the named business owner decides, not the Council)* · UAT scheduling · prioritisation within a category · adoption interventions |
| **Must not decide** | Cross-category priority — that is the Steering Committee · anything with a cost impact |
| **Escalates to** | PMO, then Steering Committee |

> **Membership corrected from 17 to 11.** `00-04` §5.1 and `CG-002` §3 both constitute *"17 module
> owners"*, a figure carried from the 30-module architecture. The current architecture is **67
> modules in 11 categories** with an accountable executive per category (`00-02` §4). Seventeen
> seats would leave 50 modules unrepresented, or make each seat responsible for four modules
> without saying which. Finding `PGD-A2-02`.

### 4.10 Delivery Squads

| Attribute | Provision |
|---|---|
| **Purpose** | To build, test and deliver |
| **Squads** | Service · Commercial · Supply Chain · Finance · People · Platform · Data · **Portals & Applications** |
| **Cadence** | Daily stand-up; fortnightly sprint; sprint review with the business owner — *working software, never slides* (`06-01` §5) |
| **Decides** | Implementation approach within the published architecture standards · sprint content within the wave scope |
| **Must not decide** | Anything that changes a contract, a schema shared with another squad, or a requirement |
| **Escalates to** | PMO daily; ARB for a technical decision |

> **A "Portals & Applications" squad is named explicitly** because the twelve portal
> specifications carry **298 PW** of Flutter and Next.js build that has never appeared in a
> programme effort figure (`GV-001` §7.2). Work with no squad is work with no capacity.

---

## 5. Decision Rights and RACI

### 5.1 The single-owner rule

> **Rule `GV-002-R3` — one decision, one owner.** Every decision class in §5.2 has exactly one
> accountable body. Where two bodies believe they own a decision, the Steering Committee
> adjudicates and the outcome is written back into this document as a version change. Audit
> `OP-04` found incident severity with **three claimed owners**; that is the failure this rule
> prevents.

### 5.2 Decision-rights matrix

Extends `00-04` §5.2. Rows marked **new** did not previously have a named owner.

| # | Decision class | Accountable body | Consulted | Escalates on |
|---|---|---|---|---|
| 1 | Programme investment and continuation | **Board** | Steering Committee, CFO | — |
| 2 | Programme closure or stop | **Board** | Steering Committee | — |
| 3 | Change to a chartered objective | **Board** | Steering Committee, benefit owner | — |
| 4 | Acceptance of a **Critical** risk | **Board** | Steering Committee, risk owner | — |
| 5 | Programme tolerance breach (`GV-001` §8.1) | **Board** | Steering Committee | — |
| 6 | Wave Go/No-Go | **Steering Committee** | ARB, Business Owners Council, QA Lead, Audit Committee from W4 | Board if the gate fails twice |
| 7 | Scope change affecting a P0 or P1 requirement | **Steering Committee** | CAB, affected business owner, Solution Architect | Board if a chartered objective is touched |
| 8 | Acceptance of a **High** risk | **Steering Committee** | Risk owner, PMO | Board if it becomes Critical |
| 9 | Cost variance within programme tolerance | **Steering Committee** | CFO | Board on breach |
| 10 | Baselining any document in `PGD-000` | **Steering Committee** | Document owner, ARB for technical documents | — |
| 11 | Dispute between two subordinate bodies | **Steering Committee** | Both bodies | — |
| 12 | Architecture standard change | **Architecture Review Board** | Security Lead, squad leads | Steering Committee on cost/schedule impact |
| 13 | Technology selection at L4 or L5 | **Architecture Review Board** | CTO, Platform Engineering | Steering Committee |
| 14 | New **L6** commercial component | **CFO**, on ARB recommendation | CTO, Procurement | Board above the procurement threshold |
| 15 | Module boundary adjudication (`AR-005`) | **Architecture Review Board** | Both module owners | Steering Committee |
| 16 | Breaking change to a published API contract | **Architecture Review Board** | Every registered consumer | Steering Committee |
| 17 | **Incident severity taxonomy and classification** — *new; closes `OP-04`* | **Architecture Review Board** *(taxonomy)* · **Major Incident Manager** *(classification of a live incident)* | Service Desk Lead, Security Lead | CTO for a Sev-1 |
| 18 | P2/P3 change within a module | **Change Advisory Board** | Business owner, squad lead | Steering Committee |
| 19 | Emergency production change | **CTO**, with retrospective Steering review | Security Lead, on-call | Steering Committee at the next meeting |
| 20 | Requirement acceptance at UAT | **Named business owner** | QA Lead | Business Owners Council, then Steering Committee |
| 21 | Segregation-of-duties exception | **CFO or CTO**, time-boxed and recorded | GRC | Audit Committee if repeated |
| 22 | Risk acceptance, Medium and below | **PMO** | Risk owner | Steering Committee |
| 23 | Document status transition in `PGD-000` (⬜ → ◐ → ✅) | **PMO** | Document owner | — |
| 24 | **Content approval, class A (statutory)** — *new* | **CFO or Legal Counsel**, with external verification | Content Council, Data Protection Forum | Steering Committee |
| 25 | **Content approval, class B (legal/contractual)** — *new* | **Legal Counsel** | Content Council | Steering Committee |
| 26 | **Content approval, classes C, D, E** — *new* | **Content Council** | Domain Content Owner | PMO |
| 27 | **Whether a processing activity has a lawful basis** — *new* | **Data Protection Forum** | Legal Counsel, CTO | Board where a statutory obligation is at risk |
| 28 | **Whether a personal-data breach is notifiable** to the National Data Management Authority — *new* | **Data Protection Forum** | Legal Counsel, Security Lead | Board immediately |
| 29 | **Whether an audit finding is closed** — *new* | **Audit Committee** | Finding owner, auditor | Board |
| 30 | **Whether a reviewer is independent** — *new* | **Audit Committee** | — | Board |
| 31 | **Appointment of a Chief Data Officer** (`D-15`) | **CEO** | Legal, Board | Board |
| 32 | **Whether a benefit may be claimed without a measured baseline** — *new* | **Board** | CFO, benefit owner, Audit Committee | — |

> Decision 32 exists because `06-02` §6 states the rule (*"a KPI without a baseline cannot claim a
> benefit"*) and `RP-02` establishes that **44 of 95 baselines are absent**. A rule with no named
> enforcer is a preference. Roughly **BDT 396 lac** of the claimed case depends on this decision.

### 5.3 Programme RACI

**R** responsible (does it) · **A** accountable (answers for it — exactly one per row) ·
**C** consulted · **I** informed.

| # | Activity | Board | Audit Cttee | Steering | ARB | CAB | PMO | Content Council | DP Forum | Bus Owners | Squads |
|---|---|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| 1 | Approve the charter | **A/R** | C | C | I | — | R | I | C | C | I |
| 2 | Constitute governance bodies | I | C | **A** | I | I | R | I | I | I | I |
| 3 | Maintain the decision log | I | C | C | I | C | **A/R** | C | C | I | I |
| 4 | Maintain the RAID register | I | C | C | C | C | **A/R** | C | C | C | R |
| 5 | Produce and maintain the master schedule | I | I | C | C | C | **A/R** | C | I | C | R |
| 6 | Estimate and re-estimate effort | I | C | C | C | C | **A/R** | R | I | C | R |
| 7 | Baseline the budget | **A** | C | R | I | I | R | C | I | I | I |
| 8 | Control scope baselines | I | C | **A** | C | R | R | C | I | C | I |
| 9 | Assess and dispose of change requests | I | I | A *(P0/P1)* | C | **A/R** *(P2/P3)* | R | C | C | C | C |
| 10 | Set architecture standards | I | I | I | **A/R** | I | I | I | C | I | C |
| 11 | Approve technology selection | I | I | C | **A/R** | I | I | I | C | I | C |
| 12 | Author requirement specifications | I | I | C | C | I | C | C | C | **A** | R |
| 13 | Author design specifications | I | I | I | **A** | I | I | I | C | C | R |
| 14 | Author guiding documents (`PGD-000`) | I | C | C | **A** *(technical)* | I | **A** *(governance)* | A *(content)* | C | C | R |
| 15 | Produce content (477 files) | I | I | I | C | C | C | **A/R** | C | C | R |
| 16 | Approve statutory content | I | C | I | I | I | I | R | C | I | I |
| 17 | Conduct the DPIA | I | C | I | C | I | I | C | **A/R** | C | C |
| 18 | Execute data migration | I | I | C | C | C | C | R | C | **A** | R |
| 19 | Execute testing | I | C | I | C | I | C | C | I | C | **A/R** |
| 20 | Accept at UAT | I | I | C | I | I | C | I | I | **A/R** | C |
| 21 | Assess a wave gate | I | C *(from W4)* | **A** | R | I | R | R | R | R | R |
| 22 | Conduct audit and independent review | I | **A/R** | I | C | I | C | C | C | C | C |
| 23 | Track and report benefits | **A** | C | R | I | I | R | I | I | R | I |
| 24 | Decommission legacy systems | I | C | C | C | C | R | I | C | **A** | R |

**Verification.** Column check performed at issue per rule `PG-M10`: exactly one **A** appears in
every row except rows 9 and 14, where accountability is split by an explicit, stated criterion
(change class; document class). No row has zero **A**.

---

## 6. Identifier Discipline for Governance Roles

> **Rule `GV-002-R4` — governance roles and system roles are different identifier spaces.**
>
> | Space | Meaning | Allocating authority |
> |---|---|---|
> | Body and role names in this document | Organisational accountability | `GV-002` |
> | `R01`–`R46` | System access roles | `05-04` / `SC-004` |
> | `SOD-01`–`SOD-30` | Segregation-of-duties controls | `05-04` / `SC-004` |
> | `D-nnn` | Programme decisions | **`GV-003` only** |
> | `RSK-nnn`, `ASM-nn`, `DEP-nn`, `CON-nn` | RAID entries | `GV-005` |
>
> A body named here does **not** imply a system role, and a system role does **not** imply a seat.
> Audit `H2-07` found `R60` duplicating `R32` — *"in a permission model, a duplicate role identity
> is a live security defect, not a documentation defect."* Conflating these spaces is how that
> happens. Final adjudication rests with `RR-002` when it is issued.

---

## 7. Cadence, Reporting and the Meeting Calendar

### 7.1 Cadence

| Forum | Frequency | Output | Owner |
|---|---|---|---|
| Squad stand-up | Daily | Impediments raised | Squad lead |
| Sprint review | Fortnightly | Working software demonstrated to the business owner | Squad lead |
| Change Advisory Board | Fortnightly | CR dispositions | Programme Director |
| Architecture Review Board | Fortnightly | ADRs in `AR-004` | CTO |
| Business Owners Council | Fortnightly | Requirement decisions, UAT scheduling, adoption issues | Council chair |
| Content Council | Fortnightly | Content approvals, schedule, translation sign-off | Content Lead |
| PMO report | Weekly | Progress, risk, issues, decisions needed | Programme Director |
| Data Protection Forum | Monthly → fortnightly from W4 | Lawful-basis decisions, DPIA status, breach determinations | CDO / CFO interim |
| ERP Steering Committee | Monthly + every wave gate | Escalations, change control, risk review, benefit tracking | CEO |
| Audit Committee | Quarterly + before every gate from W4 | Findings disposition, assurance opinion | Audit Committee chair |
| Board review | Quarterly | Investment, benefits, risks, strategic alignment | Board Chair |
| Wave gate review | Per wave | Formal Go/No-Go with evidence (`GV-009`) | Steering Committee |
| Post-implementation review | Month 42 | Independent benefits audit | Audit Committee |

### 7.2 Reporting matrix

| Report | Produced by | Audience | Frequency | Must contain |
|---|---|---|---|---|
| Squad status | Squad lead | PMO | Weekly | Sprint progress, impediments, defect counts |
| Programme dashboard | PMO | Steering Committee | Monthly | Wave progress, requirement burn-up, risk heat, budget, benefit tracking, **open audit findings by age** |
| KPI dashboard | PMO | Benefit owners | Monthly | Every KPI against baseline and target with variance commentary — **and, for the 44 KPIs with no baseline, an explicit "no baseline" marker rather than a blank** |
| Content burn-up | Content Lead | PMO | Weekly | Files by state; bilingual pair completeness; class A/B approval queue |
| Data protection status | DP Forum chair | Steering Committee | Monthly | DPIA status, `DEP-31`…`DEP-35`, days to enforcement |
| Gate report | PMO | Steering Committee | Per wave | Evidence against every gate criterion (`GV-009`) |
| Assurance opinion | Independent reviewer | Audit Committee → Board | Per review | Scope, method, findings, opinion, reviewer independence statement |
| Board pack | Programme Director | Board | Quarterly | Investment, benefits, risks, tolerance position, decisions requested |
| Adoption report | Change lead | Steering Committee | Monthly during rollout | Usage by role and branch; intervention where lagging |

---

## 8. Independence, Conflict and Delegation

### 8.1 Independence of assurance

| Rule | Provision |
|---|---|
| `GV-002-R5` | **A person may not assure work they authored, managed or approved.** This is currently breached by every audit in the estate |
| `GV-002-R6` | The assurance function reports to the **Audit Committee**, not to the CTO or the Programme Director |
| `GV-002-R7` | An audit report must carry an **independence statement**. `PGD-AUDIT-001` §12 does this correctly and states *"Not independent"* — that is the standard, and it must be a declaration, not an omission |
| `GV-002-R8` | From the **Wave 4 gate**, at least one review per year must be conducted by a reviewer external to 1000FiX. `GV-001` condition `CC-08` |

### 8.2 Conflict of interest

| Situation | Provision |
|---|---|
| A member has a personal or financial interest in a decision | Declared at the start of the meeting, minuted, and the member withdraws from the vote |
| The CEO chairs the Steering Committee and is also Executive Sponsor | Accepted, and disclosed here. The mitigation is the Audit Committee's direct line to the Board (§4.3) |
| The CTO is Senior Responsible Owner and chairs the ARB | Accepted. The mitigation is `GV-002-R6`: assurance does not report to the CTO |
| A vendor representative attends a body | Attends by invitation, never as a member, and withdraws before any decision affecting their contract |

### 8.3 Delegation and absence

| Rule | Provision |
|---|---|
| `GV-002-R9` | Delegation is **written, named and time-boxed**. "The CFO's office" is not a delegate; a named individual for a named period is |
| `GV-002-R10` | A delegate carries the delegator's vote but **not** their reserved authority. The CEO's delegate may not accept a Critical risk |
| `GV-002-R11` | If quorum fails twice consecutively, the chair escalates to the next body up. A body that cannot meet is a body that is not governing |
| `GV-002-R12` | Decisions taken outside a meeting (by written procedure) are valid only if circulated to all members, held open ≥ 48 hours, and minuted at the next meeting |

---

## 9. Constituting the Governance — the Actions Required

### 9.1 Constitution schedule

| # | Action | Owner | By | Status |
|---|---|---|---|---|
| 1 | Board approves `GV-001` | Board Chair | Week 1 | ⬜ |
| 2 | CEO issues the Steering Committee terms of reference from §4.2 and names members | CEO | Week 2 | ⬜ |
| 3 | Steering Committee holds its **first minuted meeting** | CEO | Week 2 | ⬜ **Closes `PGD-A1-09`** |
| 4 | Programme Director appointed | CEO | Week 2 | ⬜ `GV-001` `CC-02` |
| 5 | Audit Committee constituted; assurance reporting line established | Board Chair | Week 3 | ⬜ `GV-001` `CC-08` |
| 6 | ARB constituted; first ADR issued | CTO | Week 3 | ⬜ |
| 7 | Business Owners Council constituted with **11** category owners named | CEO + category executives | Week 3 | ⬜ Closes `PGD-A2-02` |
| 8 | Content Council constituted; Programme Content Lead appointed | Programme Director | Week 3 | ⬜ Closes `AF-09` `R-07` |
| 9 | Data Protection Forum constituted | CFO *(interim chair)* | Week 3 | ⬜ |
| 10 | Change Advisory Board constituted | Programme Director | Week 4 | ⬜ |
| 11 | `00-04` §5 amended to reference this document as authoritative | Enterprise Architecture | Week 4 | ⬜ |
| 12 | `CG-002` §2 "constitutional gap" note closed | Programme Content Lead | Week 4 | ⬜ |

### 9.2 Allocation of the fifteen open decisions

Every decision in `00-04` §6 now has an empowered body. **This is the substantive output of this
document**: fifteen decisions previously had owners but no forum.

| Decision | Subject | Owning body | Needed by |
|---|---|---|---|
| `D-01` | Approve scope, budget and horizon | **Board** | Before kickoff |
| `D-02` | Confirm and protect super-user availability | **Board** *(instructs)* → Steering Committee *(monitors)* | Before kickoff |
| `D-03` | Marketplace commercial model — principal vs agent | **Board**, on Steering Committee recommendation with external tax advice | W7 − 3 months |
| `D-04` | Legal-entity structure for rental and resale | **Board**, on CFO recommendation | W6 − 3 months |
| `D-05` | Multi-country target markets and sequence | **Board** | W9 − 3 months |
| `D-06` | Telephony vendor for hotline 16743 | **ARB** *(technical)* → CFO *(L6 commercial)* | W4 − 2 months |
| `D-07` | Commercial RMM agent at L6 | **CFO**, on ARB recommendation | W5 |
| `D-08` | Residency posture for recovered customer data | **Data Protection Forum** | W6 − 2 months |
| `D-09` | Whether 1000FiX guarantees marketplace work | **Board** | W7 − 3 months |
| `D-10` | Seller insurance requirement and liability caps | **Steering Committee**, on Legal recommendation | W7 − 3 months |
| `D-11` | Technician device procurement model | **Steering Committee** | W2 − 2 months |
| `D-12` | Refurbished warranty terms and reserve policy | **Steering Committee**, on CFO recommendation | W6 |
| `D-13` | **Approve the split-residency data architecture** | **Data Protection Forum** *(recommends)* → **Board** *(approves)* | **Before Wave 1 architecture is fixed** |
| `D-14` | **Accept the restated effort and cost position, or direct a descope** | **Board** | Before the next Board review |
| `D-15` | Significant data fiduciary classification and CDO appointment | **CEO**, on Legal advice; Board informed | W4 − 3 months |

---

## 10. Decisions Recorded

| # | Decision | Options considered | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| `GV-002-D-01` | Where assurance reports | To the CTO *(status quo)* · To the Programme Director · To an Audit Committee reporting to the Board | **Audit Committee → Board** | Four audits produced by the authoring function; `AUDIT-019` recorded a critical finding against the auditor's own work; `PGD-AUDIT-001` §12 declares itself non-independent | A new Board sub-committee must be constituted. Cost: modest. Alternative: assurance that finds what the authoring function already knows |
| `GV-002-D-02` | Whether to split change control from the Steering Committee | Keep monthly at Steering · Split a fortnightly CAB | **Split** | A monthly change body on a 36-month programme with a scope that has already tripled is a queue | Two bodies to run; a clear reservation boundary in §4.5 |
| `GV-002-D-03` | Business Owners Council size | Retain 17 *(as written)* · Move to 11 category owners · One per module (67) | **11 category owners** | 17 is a 30-module artefact; 67 seats is not a decision-making body | Each category executive carries their category. `00-04` and `CG-002` must be amended |
| `GV-002-D-04` | Whether to create a Data Protection Forum | Handle inside Steering Committee · Create a forum | **Create** | Five interlocking risks across four executive owners with no shared forum, and a statutory deadline inside Wave 4 | A ninth body. Justified by `RSK-032`–`RSK-035` and the BDT 50 lakh penalty tier |
| `GV-002-D-05` | Whether incident severity sits with ARB or Operations | ARB owns taxonomy and classification · Split | **ARB owns the taxonomy; the Major Incident Manager classifies a live incident** | `OP-04` found three claimed owners. A standing taxonomy is an architecture matter; a live call is an operational one | Closes `OP-04`. `SV-006` inherits the split |

---

## 11. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| `Q-01` | Does 1000FiX have a non-executive director available to chair the Audit Committee? If not, is Board-Chair chairing sufficient for independence? | Company Secretary | Week 3 | §4.3; `GV-010` |
| `Q-02` | Who are the eleven category owners by name? `00-02` §4 names roles; two roles (*Corporate Services / Retail Operations Head*, *Technical Services Head*) appear in `00-04` but in no organisation chart in the estate | CEO | Week 3 | §4.9 constitution |
| `Q-03` | Is the Programme Content Lead an appointment or a re-designation? `CG-002` §3 marks the role *"New — to be registered"* against `05-04` | Programme Director | Week 3 | §4.7; `AF-09` |
| `Q-04` | Does the Steering Committee's authority to baseline extend to documents owned by another programme — e.g. the portal platform's API contract? | Steering Committee | Week 6 | `CON-03`; `IN-004` |
| `Q-05` | What is the quorum for the Board on programme matters? This document defers to the articles of association, which have not been checked against the programme's decision load | Company Secretary | Week 2 | §4.1 |

---

## 12. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| `AC-01` | Every body has a stated purpose, chair, membership, quorum, cadence, decision set and escalation route | §4 — nine bodies, nine complete term sets |
| `AC-02` | Every decision class has exactly one accountable body | §5.2 — 32 rows, single owner each; rule `GV-002-R3` |
| `AC-03` | The RACI has exactly one **A** per row, or an explicit stated split | §5.3 verification note |
| `AC-04` | Every one of the fifteen open decisions has an owning body | §9.2 — 15 of 15 allocated |
| `AC-05` | Assurance does not report to a function it assures | §8.1 rules `GV-002-R5`–`R8` |
| `AC-06` | Governance roles are separated from system roles | §6 rule `GV-002-R4` |
| `AC-07` | Every departure from `00-04` §5 is stated and justified | §3.3 — seven changes |
| `AC-08` | Every standards citation carries an edition and a verification date | §2.1; front matter `verified_on: 2026-08-18` |
| `AC-09` | The document states what each body may **not** decide | §4 — every body carries a "Must not decide" row |

**Definition of done.** Complete when every criterion above is met, the Steering Committee has
held its first minuted meeting under §4.2, `PGD-000` records `GV-002` as ✅ with a fresh
enumeration timestamp, and the CEO has approved.

---

## 13. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | [`GV-001`](GV-001_Programme_Charter_and_Mandate.md) | Confers the authority these bodies exercise |
| Downstream | [`GV-003`](GV-003_Decision_Log_and_Change_Control_Procedure.md) | Records what these bodies decide; `D-nnn` allocated only there |
| Downstream | [`GV-005`](GV-005_RAID_Register.md) | Risk acceptance thresholds in §5.2 rows 4, 8, 22 |
| Downstream | [`GV-006`](GV-006_Scope_Management_and_Baseline_Control_Procedure.md) | Scope authority in §5.2 rows 7, 8, 18 |
| Downstream | [`GV-009`](GV-009_Wave_Gate_and_Phase_Exit_Criteria_Handbook.md) | Constitutes the gate assessor |
| Downstream | [`GV-010`](GV-010_Programme_Assurance_and_Independent_Review_Plan.md) | Resources the independence established in §8 |
| Downstream | [`GV-011`](GV-011_Documentation_Control_and_Configuration_Management_Plan.md) | Approval authority per document class |
| Downstream | `AR-004` | ADR obligation, rule `GV-002-R2` |
| Downstream | `SC-003`, `SC-007`, `SC-011` | Data Protection Forum decision rights |
| Downstream | `SV-006` | Incident severity split, closing `OP-04` |
| Lateral | `../../1000fix_ERP_Module/00_Governance_and_Charter/00-04` §5 | The baseline this document formalises and, in seven respects, corrects |
| Lateral | `../../project_content/00_Content_Governance_and_Standards/CG-002` | Content operating model — its governance seat is constituted here at §4.7 |
| Lateral | `../../project_content/00_Content_Governance_and_Standards/CG-007` | Content gates `G1`–`G6` referenced, not restated |

---

## 14. References

**Within this repository**
[`PGD-000`](../PGD-000_Master_Register_of_Project_Guiding_Documents.md) ·
[`PGD-AUDIT-001`](../_AUDIT/PGD-AUDIT-001_Register_Integrity_Audit.md) ·
[`PGD-AUDIT-002`](../_AUDIT/PGD-AUDIT-002_Category_00_Governance_Audit.md) ·
[Category 00 overview](_CATEGORY_OVERVIEW.md) ·
[`GV-001`](GV-001_Programme_Charter_and_Mandate.md) …
[`GV-011`](GV-011_Documentation_Control_and_Configuration_Management_Plan.md)

**Workspace**
`../../1000fix_ERP_Module/00_Governance_and_Charter/00-04` §5 ·
`../../project_content/00_Content_Governance_and_Standards/CG-002`, `CG-007` ·
`../../project_content/_AUDIT/AUDIT-001`, `AUDIT-017`, `AUDIT-019`

**External standards** *(all verified 2026-08-18)*

| Source | Used for |
|---|---|
| ISO/IEC 38500:2024, edition 3 (February 2024) — six principles; Engage → Evaluate → Direct → Monitor; the governance framework | §3, §4 body structure |
| ISO 21503:2022 — programme governance, programme board | §4.2 |
| ISO 21502:2020 §6 — project governance; assurance separate from delivery | §8.1 |
| PRINCE2 7th Edition (2023) — Executive / Senior User / Senior Supplier; management by exception | §4.2 membership mapping |
| COBIT 2019 — governance/management separation | §3.1 |
| ISO 9001:2015 clauses 5.1, 5.3 | §5.3 RACI |
| Bangladesh Personal Data Protection Act 2026; National Data Management Authority (reports to the Prime Minister's Office; may warn, fine, and order suspension of cross-border transfers) | §4.8 |

---

## 15. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-18 | Enterprise Architecture | Initial issue. Constitutes nine bodies; adds Audit Committee, Change Advisory Board, Content Council and Data Protection Forum; corrects Business Owners membership from 17 to 11; allocates all fifteen open decisions to an empowered body; separates assurance from delivery | *pending CEO* |

---

*`GV-002` · Category 00 · 1000FiX ERP System v2.0 · CONFIDENTIAL — Internal Use Only*
*1000FiX Services Limited · Hotline 16743 · info@1000fix.com · ISO 9001:2015 Certified*
