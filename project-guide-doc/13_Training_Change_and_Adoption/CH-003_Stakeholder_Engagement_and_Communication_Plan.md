---
id: CH-003
title: Stakeholder Engagement and Communication Plan
category: 13 — Training, Change & Adoption
code: CH
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-19
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Change Lead
approver: Programme Director with the ERP Steering Committee
standards_basis: >
  ISO 21502:2020 §7.5 (stakeholder engagement) and §7.4 (communication) · ISO 21500:2021
  (project, programme and portfolio management — context and concepts) · ACMP Standard for Change
  Management Version 2 (26 August 2025), process group 2 — Formulate change management strategy,
  including 5.1.4 roles and responsibilities · PMBOK Guide 7th Edition, Stakeholder performance
  domain · ISO 10018:2020 (people engagement)
traces_to: >
  PGD-000 CH-003 · AUDIT-019 CM-03 (two current wave calendars), CM-08 (divergent external
  enumerations), CM-09 (CM/EO boundary stated on one side only), CM-11, CM-14 · AUDIT-018 R-07 ·
  CM-002 SK-01…SK-18 · CM-003 CA-01…CA-18 · OP-001 §4.1 · 06-01 §3, §7, §8 · 06-02 §4
depends_on: CH-001 · GV-002 · GV-004 · CH-004 (lateral)
verified_on: 2026-08-19
priority: P1
needed_by: W1
enumeration_timestamp: 2026-08-19 01:20 (+06)
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# CH-003 — Stakeholder Engagement and Communication Plan

### Category 13 · Code `CH` · ISO 21502:2020 §7.4–§7.5 · ISO 21500:2021 · ACMP v2 process group 2 · PMBOK 7 Stakeholder domain

---

> **Local rule prefix: `SEP-nn`.** Verified to return **zero** occurrences workspace-wide before
> allocation, at 2026-08-19 01:20 (+06).

---

## 1. Purpose

`CM-002` supplies a stakeholder register and a standing communication plan. `CM-003` supplies a
milestone-anchored calendar. Both are strong content files, and between them they hold **27
stakeholder groups, 18 channel and cadence rules, and 18 calendar rules**.

**Three things are nonetheless broken, and none of them can be fixed inside a content file.**

| # | Defect | Finding | Why a content file cannot fix it |
|:--:|---|---|---|
| 1 | **Two wave calendars are current across the repository**, and two `Draft` content files in two categories now schedule against different ones, each believing it follows `06-01` | `AUDIT-019` **`CM-03`**, High, open | Correcting one file at a time is the failure mode `AUDIT-014` `TS-02` warned about. One calendar must be **declared**, register-wide, once |
| 2 | **Two enumerations of the external populations exist and disagree**, one of them missing a **1,000–4,000-person population** | `AUDIT-019` **`CM-08`**, Medium, open | Two files each declaring themselves definitive is one too many; a third file restating either makes it worse |
| 3 | **The `CM`-transition / `EO`-onboarding boundary is stated on one side only**, in prose, across three files | `AUDIT-019` **`CM-09`** and `AUDIT-018` **`R-07`**, both open | Prose boundaries decay; a boundary needs an owning table in a governing document |

**This document declares the calendar, adopts the single external enumeration, and fixes the
boundary in a table.** It does not restate `CM-002`'s register or `CM-003`'s calendar content
(`CP-01`); it governs them.

### 1.1 Scope

**In scope:**

| # | Covered |
|:--:|---|
| 1 | **The declaration of one wave calendar** for the entire estate, and the retirement of the other |
| 2 | The adoption of `OP-001` §4.1 as the single external-population enumeration, and the reconciliation of `CM-002` §4.3 to it |
| 3 | The stakeholder governance model: assessment axes, treatment classes, decision rights, owning communicator |
| 4 | The **`CM`/`EO` boundary table** — transition versus onboarding |
| 5 | The engineering-side stakeholders the content estate cannot see |
| 6 | Escalation, feedback loop and the communication log as a controlled record |
| 7 | The bilingual delivery obligation, its lead times, and the one cadence that is currently unachievable |
| 8 | Measurement of engagement — coverage, reach, reply and silence |

**Explicitly out of scope:**

| Topic | Owned by | Why the boundary sits here |
|---|---|---|
| The stakeholder register rows themselves | `CM-002` §4.2–4.3 | 27 groups, authored and audited. This plan governs them and does not duplicate them |
| The calendar's message set and offsets | `CM-003` §4.1–4.11 | `CA-01`…`CA-18` are sound. What was wrong was the anchor, and the anchor is declared here |
| Message wording, narrative, claim schedule, objection answers | `CM-001`, `CM-011`, `CM-005`…`CM-017` | Content, governed by `CG-*` |
| Change impact, sponsorship, resistance response | [`CH-001`](CH-001_Organisational_Change_Management_Plan.md) | Engagement executes the change strategy |
| Adoption campaigns and their consent rules | [`CH-004`](CH-004_Adoption_Measurement_and_Reinforcement_Plan.md) · `CM-016` | A campaign is marketing; a transition notice is not (`MG-03`) |
| External-party onboarding content | Category 18 `EO` | §5 fixes the boundary; it does not cross it |
| Statutory and regulatory correspondence | Legal and Finance | `SK-05`: regulators are communicated to on trigger, by Legal or Finance |

### 1.2 Intended audience

| Audience | What they use this document for |
|---|---|
| Programme Director / PMO | The declared calendar, and the escalation route when a group is under-communicated |
| **Change Lead** | The operating instrument |
| Enterprise Architecture | The register-wide correction §3 requires |
| Support Lead | The external enumeration this plan adopts from `OP-001` |
| Account Management, Procurement, Marketplace Ops | The `CM`/`EO` boundary that determines who owns which counterparty |
| Localisation Lead | The lead times, and the one cadence that cannot be met |
| Content Design | Which files must change, and in which direction |

---

## 2. Basis and Inputs

### 2.1 Standards conformance

| Standard | Clause | How this document conforms | Departure and rationale |
|---|---|---|---|
| **ISO 21502:2020** | **§7.5 Stakeholder engagement** — identify, analyse, plan, engage, monitor | §4 identification and analysis; §6 engagement model; §8 monitoring | None |
| " | §7.4 Communication — plan, distribute, monitor | §6 and §7 | None |
| **ISO 21500:2021** | Context, governance and the organisational environment of projects | §4.5's engineering-side stakeholder set derives from it | None |
| **ACMP Standard for Change Management v2** (26 Aug 2025) | Process group 2 — *Formulate change management strategy*, including **5.1.4 Determine change management roles and responsibilities** (new in v2) | §6.4 owning-communicator model; §5 boundary table | None |
| **PMBOK Guide 7th Edition** | Stakeholder performance domain — *"productive working relationships… stakeholder agreement with project objectives"* | §4.4 decision rights: a group is consulted only on what it can decide or shape | None |
| ISO 10018:2020 | People engagement | §6.2 two-way channel obligation | None |

### 2.2 Source material relied on

| Source | Location | What it establishes |
|---|---|---|
| `CM-002` | `../../project_content/16_Change_Management_and_Comms/CM-002_Stakeholder_Map_and_Communication_Plan.md` | 27 groups (`S01`–`S27`), the influence/impact matrix, decision rights, channel rules `SK-01`…`SK-18`, resistance tracking, escalation |
| `CM-003` | `.../CM-003_Communication_Calendar_by_Wave.md` | Milestone anchoring, the eight-message per-wave set `M1`–`M8`, per-location pattern, translation lead times, quiet periods, slip protocol, `CA-01`…`CA-18` |
| **`OP-001` §4.1** | `../../project_content/17_Operations_Support_and_Runbooks/OP-001_Support_Model_Tiering_and_Routing_Content.md` | **Eleven external populations, enumerated and declared definitive**, with size, portal, language and owning function |
| `OP-002` §4.3 | `.../OP-002_Hypercare_Plan_and_Exit_Criteria.md` | Hypercare duration by wave — **and the second wave calendar, mis-attributed to `06-01`** |
| Master Index §1 | `../../project_content/1000FiX_ERP_Content_Master_Index.md` | *"Distribution by wave"* — the second calendar, which states *"Waves are taken from `06-01`"* |
| `06-01` §3, §8 | `../../1000fix_ERP_Module/06_Delivery_and_Implementation/06-01_Implementation_Roadmap_and_Phasing.md` | Wave months and the milestone schedule |
| `06-02` §4 | `.../06-02_KPI_Benefits_and_Acceptance_Criteria.md` | Gate months `G1`…`G9` |
| `AUDIT-019`, `AUDIT-018` | `../../project_content/_AUDIT/` | `CM-03`, `CM-08`, `CM-09`, `CM-11`, `CM-14`; `AUDIT-018` `R-07` |

**Enumeration.** Every count in this document was taken from the filesystem and from the primary
tables named above at **2026-08-19 01:20 (+06)**, per `OCM-02`.

---

## 3. The Wave Calendar — Declared

**This section exists to close `AUDIT-019` `CM-03`.** `AUDIT-019` `R-02` requires that one calendar
be declared *"and the loser corrected register-wide, once. Do not correct it file by file."*

### 3.1 The divergence, stated in full

| Wave | **`06-01` §3 / §8 and `06-02` §4** *(they agree)* | **Master Index §1** *"Distribution by wave"* | Divergence |
|:--:|---|---|---:|
| W0 | 0 (mobilisation) | 0–3 | — |
| **W1** | **Months 1–4**, gate `G1` at month **4** | Months **3–8** | **+4 months** |
| **W2** | Months 5–8, gate `G2` at **8** | Months **8–14** | **+6 months** |
| **W3** | Months 9–13, gate `G3` at **13** | Months **14–18** | **+5 months** |
| **W4** | Months 14–18, gate `G4` at **18** — *v1.0 complete* | Months **18–23** | **+5 months** |
| **W5** | Months 19–22, gate `G5` at **22** | Months **23–27** | **+5 months** |
| W6 | Months 23–26, `G6` at 26 | 27–30 | +4 months |
| W7 | Months 27–30, `G7` at 30 | 30–33 | +3 months |
| W8 | Months 31–34, `G8` at 34 | 33–36 *(W8–W9 combined)* | +2 months |
| W9 | Months 35–36, `G9` at 36 — closure | 33–36 | — |

> **The Master Index calendar runs two to six months later than `06-01` for the same wave, and it
> states that its waves *"are taken from `06-01`"*.** They are not. The divergence peaks at W2 —
> the wave carrying `P02`, the technician application, and the programme's Critical adoption risk.

### 3.2 Who has taken which side

| File | Anchored to | Consequence |
|---|---|---|
| `CM-003` §4.1 | **`06-01` / `06-02`** | Correct; records the divergence as its own `O-01` |
| **`OP-002` §4.3** | **Master Index** — with its column headed *"Months (`06-01`)"* | **A hypercare plan whose W1 window is stated as months 3–8 when the wave runs 1–4.** `AUDIT-019` `CM-03` |
| Master Index §1 | Itself, citing `06-01` | The source of the second calendar |
| **This document, and all of Category 13** | **`06-01` §3 / §8 and `06-02` §4** | §3.3 |

### 3.3 The declaration

> **`SEP-01` — `06-01` §3 and §8, reconciled with `06-02` §4's gate months, are the single
> authoritative wave calendar for the 1000FiX ERP programme. Every other statement of wave months
> in the estate is superseded and is corrected to it.**

| Wave | Months | **Gate** | Gate month | Geography (`06-01` §6) |
|:--:|---|:--:|:--:|---|
| W0 | 0 | Charter approved | 0 | HQ |
| **W1** | **1–4** | **G1** | **4** | Dhaka HQ + 5 pilot centres |
| **W2** | **5–8** | **G2** | **8** | All Dhaka centres (~20) |
| W3 | 9–13 | G3 | 13 | + Chittagong, Sylhet, Khulna, Rajshahi |
| W4 | 14–18 | **G4 — v1.0 complete** | **18** | All active service centres |
| W5 | 19–22 | G5 | 22 | **All 51+ centres** |
| W6 | 23–26 | G6 | 26 | Per module |
| W7 | 27–30 | G7 | 30 | Marketplace, national |
| W8 | 31–34 | G8 | 34 | National |
| W9 | 35–36 | **G9 — closure** | **36** | Multi-entity |
| — | 42 | Post-implementation benefits review | 42 | Board |

**Why `06-01` wins, stated so the decision is reviewable rather than assumed:**

| # | Reason |
|:--:|---|
| 1 | `06-01` is the **delivery** document; the Master Index is a **content** register. A content register may not re-time delivery |
| 2 | `06-02` §4's gate months **independently agree** with `06-01` §8. Two delivery documents against one content register |
| 3 | The Master Index **cites `06-01` as its source** and does not match it, which makes it a transcription error rather than a competing position |
| 4 | Every gate criterion, every `KPI` target date and every `00-04` risk trigger is expressed against `06-01`'s months |

### 3.4 The corrections this declaration requires

**`SEP-02`: the correction is executed once, register-wide, by a named owner — never file by file.**

| # | Artefact | Correction | Owner | By |
|:--:|---|---|---|---|
| 1 | **Master Index §1 "Distribution by wave"** | Re-state months from `06-01` §3, or **re-label the column as "content production window"** and remove the claim that the waves are taken from `06-01` | Programme Content Lead | **W0** |
| 2 | **`OP-002` §4.3** | Re-anchor the duration table to `06-01` months; the **durations themselves are unaffected** | Support Lead | **W0** |
| 3 | `CM-003` `O-01` | Closed on execution of 1 and 2 | Change Lead | W0 |
| 4 | Any `TS`, `RP`, `EO` or `AP` file scheduling against the Master Index months | Swept and corrected in the same change | Programme Content Lead | W0 |
| 5 | This register's `PGD-000` §2.2 tranche table | Already expressed in weeks, not wave months; no correction required — **verified** | — | Done |

> **`SEP-03` — the hypercare *duration* question is separate from the calendar question and is not
> closed by this declaration.** `AUDIT-019` `CM-04` records that `06-01` §5, `06-01` §6 and BRD
> §21.5–21.6 all state **four weeks** of hypercare while `OP-002` §4.3 states **4–8 weeks, minimum
> not target**, with 8 weeks at W1, W3 and W5. `OP-002`'s reasoning is sound — `HD-02` requires a
> full business cycle inside the window and a month-end does not fit in four weeks — **but the three
> upstream documents have not been corrected**, and `CM-003` §4.4 anchors the per-location pattern
> to `06-01` §6's `T+4 weeks`. That reconciliation is `AUDIT-019` `R-03`, owned by the Programme
> Manager, needed at **W1 − 6 weeks**. Carried here as `SEP-Q-01`.

---

## 4. Stakeholders

### 4.1 The single external enumeration — closing `CM-08`

`AUDIT-019` `R-07` requires that `OP-001` §4.1 be adopted as the single external enumeration and
`CM-002` §4.3 re-derived from it.

> **`SEP-04` — `OP-001` §4.1 is the definitive enumeration of external populations. `CM-002` §4.3
> is re-derived from it, and no third enumeration is created.**

| # | Population | Size (`OP-001` §4.1) | Portal | Language | Owning function | `CM-002` position |
|---:|---|---|---|---|---|---|
| 1 | Consumer customers | 250,000+/month | `P01`, hotline 16743, WhatsApp | **Bengali first** | Contact Centre | `S18` ✔ |
| 2 | Corporate client **end users** | 500 – 2,000 | `P04` | EN + BN | Account Management | `S19` — **merged with row 3** |
| 3 | Corporate client **administrators** | **50 – 200** | `P04` admin surfaces | EN | Account Management | **Absent as a distinct group** |
| 4 | Marketplace sellers | 500 – 2,000 | `P07` | **Bengali first** | Marketplace Ops | `S22` ✔ |
| 5 | **Marketplace seller technicians** | **1,000 – 4,000** | `P07` app surfaces | **Bengali first** | Marketplace Ops | **⚠ ABSENT** |
| 6 | Brand partners | 17+ | `P08` | EN | Commercial / Warranty | `S20` ✔ |
| 7 | Vendors and suppliers | **200 – 600** | `P05` | EN | Procurement | `S21` — states 200–500 |
| 8 | Referral and alliance partners | **50 – 300** | `P12` | EN + BN | Partnerships | `S24` — states 100–500 |
| 9 | **Franchise and channel partners** | **0 – 30 from W8** | `P12` | EN + BN | Commercial | **⚠ ABSENT** |
| 10 | Courier partners (`INT-024`…`INT-026`) | 3 – 6 organisations | `P09` integration | EN | Logistics | `S23` — states 10–40 firms |
| 11 | Regulators, auditors and external verifiers | occasional | Named contact, no portal | EN | Compliance / Legal | `S26` ✔ |
| — | Recycling and disposal partners | 3 – 10 | Direct | — | Quality Manager | `S25` — **in `CM-002`, absent from `OP-001`** |

**Five reconciliations follow, and they are not symmetric.**

| # | Reconciliation | Direction | Why |
|:--:|---|---|---|
| 1 | **Add marketplace seller technicians (1,000–4,000)** to `CM-002` | `OP-001` → `CM-002` | The largest external population in the estate, and the one that will actually use `P07` on a job. `CM-015` `O-06` records the same gap from the transition side |
| 2 | **Split corporate end users from corporate administrators** | `OP-001` → `CM-002` | Different content, different cadence, different language. An administrator configures approval chains; an end user raises a request |
| 3 | **Add franchise and channel partners (0–30 from W8)** | `OP-001` → `CM-002` | A W8 population with no communication owner today |
| 4 | Adopt `OP-001`'s sizes for vendors (200–600), referral partners (50–300) and couriers (3–6 organisations) | `OP-001` → `CM-002` | Single source; `OP-001` derived its from `04-00` and the integration catalogue |
| 5 | **Add recycling and disposal partners to `OP-001`** | `CM-002` → `OP-001` | `S25` exists, has a certificate-submission obligation and a W8 wave. `OP-001` §4.1's own `OP-001-OI-01` invites exactly this correction |

> **`SEP-05` — adopting a single enumeration is not adopting one file's list; it is adopting one
> file's *authority*, and correcting it where another file is right.** Reconciliation 5 runs the
> other way and is stated so that "adopt `OP-001`" is not read as "delete `S25`".

### 4.2 The internal register

`CM-002` §4.2's seventeen internal groups `S01`–`S17` are adopted without change. **`SEP-06`: no
internal group is invented here; `05-04` and `MD-009` govern** (`SK-02`).

Two observations this plan adds:

| Observation | Consequence |
|---|---|
| **`S17` "wider workforce not otherwise listed"** is the group whose communication requirement is unconditional (`SK-04`) | It is also the only group with **no ceiling on its population**, and §4.3's arithmetic depends on that ceiling. See `CH-001` `OCM-Q-02` |
| **`S04` super-users (40–60) and `S06` champions (51+)** are registered as stakeholder groups and are also the programme's delivery mechanism | They are stakeholders *and* resources. [`CH-005`](CH-005_Super_User_and_Champion_Network_Charter.md) owns the resource half; this plan owns the stakeholder half. The two must not double-count their time |

### 4.3 The population arithmetic

| Set | Population | Source |
|---|---:|---|
| Internal, registered roles | **732 – 1,368** | `05-04`, summed — `CH-001` §4.2 |
| **External, `OP-001` §4.1 as adopted** | **2,271 – 8,556**, plus 250,000+ consumers/month | Summed from §4.1 rows 2–10 |
| Consumer customers | 250,000+ / month | Row 1 |
| **Total audiences under this plan** | **27 groups** *(`CM-002`)*, **31 after the §4.1 reconciliations** | |

> **The reconciliations add roughly 1,050–4,230 external people to the programme's stakeholder
> map** — a population larger than the entire internal workforce, previously invisible to the
> communication plan.

### 4.4 Decision rights

`CM-002` §4.4 governs and is adopted. **`SEP-07`: a group is consulted only on what it can decide
or materially shape** (`SK-06`). The one designed exposure is restated here because it is
load-bearing:

> **`SK-07` — technicians hold no formal decision right and carry the highest impact.** The field
> pilot in `RSK-008`'s mitigation is the *only* mechanism that gives them influence, which makes it
> a **communication obligation, not an engineering nicety.** [`CH-001`](CH-001_Organisational_Change_Management_Plan.md)
> §9.2 schedules it; this plan makes the pilot's findings a published communication to the
> population that produced them. **`SEP-08`: what the field pilot finds is reported back to
> technicians in Bengali, including what will not be changed.**

### 4.5 The stakeholders the content estate cannot see

`CM-002` was authored from `05-04` and `04-00` — the *operational* role and portal registers. Five
groups material to the engineering programme appear in neither:

| Group | Population | Why they are a stakeholder | Owning communicator | Cadence |
|---|---|---|---|---|
| **Implementation vendor delivery team** | 7 – 19 FTE (`06-01` §4) | Requirement stability and UAT availability are the two things that stop them; `S27` covers them thinly | Programme Manager | Sprint ceremonies |
| **Data owners** | 20% of time during migration, W1–W5 (`06-01` §4) | `MG-004` reconciliation cannot be signed by anyone else; `PR-6` is a readiness criterion | Data Migration Lead | Per site, T−3 weeks |
| **The DP Forum / Legal** | — | `RSK-032` PDPA enforcement ~13 May 2027, inside W4; the `P02` monitoring disclosure blocks a go-live | DP Officer | Per wave, and on trigger |
| **Brand partners' own auditors** | Per brand | `MD-011` certification lapse suspends assignment; a brand audit tests our competence records | Warranty + Quality | On brand trigger |
| **The ISO 9001 certification body** | 1 | Surveillance during a 36-month QMS change; `KPI-067` targets zero major non-conformances | Quality Manager | Per surveillance visit |

> **`SEP-09` — a stakeholder group with a decision right over a go-live is registered whether or
> not it appears in an operational role register.** Three of the five above can stop a wave.

---

## 5. The `CM` / `EO` Boundary — Closing `CM-09` and `AUDIT-018` `R-07`

`AUDIT-018` raised it from the `EO` side with recommendation `R-07`: *"neither register row
acknowledges the other"*, listing **eleven `EO`↔`CM` overlaps** concentrated in `CM-013`, `CM-014`,
`CM-015` and `CM-002`. `AUDIT-019` `CM-09` reached the same conclusion independently from the `CM`
side. **Both findings are open, and both note that prose boundaries decay while tables do not.**

> **`SEP-10` — the boundary is *whether a commercial relationship already exists*** (`CM-015`
> `VT-02`). An existing counterparty is **transitioned** (`CM`); a new counterparty is **onboarded**
> (`EO`).

| Subject | Owned by `CM` (Category 16, transition) | Owned by `EO` (Category 18, onboarding) |
|---|:--:|:--:|
| Telling an **existing** customer their reference still works | **●** `CM-013` | ○ |
| Registering a **new** customer on `P01` | ○ | **●** |
| Telling an **existing** corporate client their invoice format changes | **●** `CM-014` | ○ |
| **Configuring** a corporate client's approval chains and users | ○ | **●** `EO-008` |
| Telling an **existing** vendor the PO route changes | **●** `CM-015` | ○ |
| Vendor registration, bank details, tax documents | ○ | **●** |
| Telling an **existing** brand partner the claim format changes | **●** `CM-015` | ○ |
| Brand rate-card and evidence-standard configuration | ○ | **●** `EO-003` |
| **Seller recruitment and qualification** | ○ | **●** |
| Telling an **already-recruited** seller cohort about a transition | **●** `CM-015` | ○ |
| **Marketplace seller technician qualification** (`BRU-LMS-02`) | ○ | **●** — **and no `EO` file specifies it** (`CH-002` `TPD-Q-06`) |
| The counterparty's **stakeholder register row and cadence** | **●** `CM-002`, governed by this plan | ○ |

**`SEP-11`: the register rows on both sides state the boundary reciprocally.** Executing
`AUDIT-018` `R-07` requires:

| # | Action | Owner | By |
|:--:|---|---|---|
| 1 | Add the reciprocal statement to the `CM-013`, `CM-014` and `CM-015` register rows and to Master Index §5's Onboarding column | Programme Content Lead | **W3** |
| 2 | Mirror `CM-008` §4.2's twelve-row ownership-table **form** into the `EO` files | Programme Content Lead | W3 |
| 3 | Assign an owner to the seller-technician qualification gap | CCO with Marketplace Ops | W7 − 20 weeks |

---

## 6. The Engagement Model

### 6.1 Assessment and treatment

`CM-002` §4.1's two axes — **influence** and **impact felt** — are adopted unchanged (`SK-01`), as
is the treatment matrix. **`SEP-12`: high impact with low influence receives the heaviest support,
not the lightest** (`SK-03`). Field technicians sit in that cell; they cannot stop the programme in
a committee, and they stop it by not using the app.

### 6.2 Channel obligations

`CM-002` §4.5's `SK-08`…`SK-14` govern and are not restated. Three are elevated here because a
guiding document is where a breach becomes reportable:

| Rule | Elevated obligation |
|---|---|
| `SK-08` — Bengali-first for field, branch, workshop, store and rider audiences | **`SEP-13`: an English-only communication to `S07`–`S10` is recorded as a missed communication in the log, not as a communication delivered** |
| `SK-11` — WhatsApp notifies, never instructs | **`SEP-14`: the programme is removing WhatsApp-based dispatch (BRD §6.2); a programme communication that institutionalises WhatsApp as a system of record is a `GV-003` change, not a channel choice** |
| `SK-13` — two-way channels mandatory for `Partner` and `Support` groups | **`SEP-15`: a two-way channel with no answer route is one-way. `NW-10`'s one-working-day commitment is the answer route, and it is a resourced obligation** |

### 6.3 The communication log

`SK-14` requires every communication to record what was sent, to whom, by whom, in which language
and on what date.

> **`SEP-16` — the communication log is a controlled record under `GV-011`, not a spreadsheet.**
> It is the evidence base for §8's coverage measure, for `CH-001` §6's objection log, and for any
> later question about whether a population was told. `GV-011` governs retention and control.

### 6.4 Owning communicator

ACMP v2 5.1.4. **`SEP-17`: every group has exactly one owning communicator, and external groups
are communicated to by the person who already owns the relationship** (`SK-12`).

| Constraint | Consequence |
|---|---|
| One owner per group | Two owners means a group hears two versions and believes the worse one |
| External via the relationship owner | An account manager, procurement officer or warranty officer, never the programme directly |
| **The Change Lead post is vacant** | Twelve of eighteen `CM` files name it as owner (`AUDIT-019` `R-11`). **Every cadence in this plan currently has no accountable person.** `CH-001` `OCM-Q-01` |

---

## 7. Bilingual Delivery

### 7.1 Lead times

`CM-003` §4.5's `CA-08` and `CA-09` govern: Bengali is commissioned at English **draft**, not at
English approval, and nothing is scheduled inside its stated lead time.

| Content size | Total lead time |
|---|---|
| Short notice (< 250 words) | **3 working days** |
| Standard message or kit item | 1 week |
| Full kit, roadshow deck, transition pack | **3 weeks** |
| Video or recorded audio | **4 weeks** |

### 7.2 The cadence that cannot be met

`AUDIT-019` `CM-11`: **zero `_BN.md` counterparts exist for the twelve bilingual `CM` files**, and
one obligation is not merely unstarted but **internally contradictory**:

> **`CM-007`'s known-issue bulletin refreshes at every evening triage — nightly, in Bengali —
> against `CM-003` §4.5's three-working-day minimum for a short notice. The cadence and the lead
> time are in direct conflict.**

**`SEP-18`: an obligation whose cadence is shorter than its own translation lead time is escalated
as a decision, never absorbed as an unstated default.** Two acceptable outcomes:

| Option | What it requires |
|:--:|---|
| **A** | A **same-day Bengali route** for operational bulletins: a named bilingual operator on the hypercare rota, with a 250-word cap and a fixed template, translating at triage rather than through the standard route |
| **B** | An explicit, recorded decision that **the bulletin is English at the sites that need it most** — with the consequence stated in the decision |

Owner: Localisation Lead with the Support Lead. Needed by **W1 − 3 weeks** (`AUDIT-019` `R-08`).
Carried as `SEP-Q-02`. **Option A is recommended**; option B contradicts `SK-08` and would be the
first recorded exception to it.

### 7.3 The standing translation load

| Obligation | Volume | Status |
|---|---|---|
| Twelve bilingual `CM` files | 12 counterparts | **Zero on disk** |
| `CM-009` internal newsletter | **36 monthly bilingual issues over three years** | In no capacity plan |
| `CM-005` wave launch kit | Four of six assets Bengali-first, **reprinted per wave to 51+ sites** | Print and distribution unfunded (`CM-005` `O-04`) |
| `CM-018` change impact statements | **38 roles**, 3–4 bilingual (`CM-018` §4.7) | Unfunded |
| Layer 1 statutory training | Bilingual, 752–1,428 learners | `CH-002` §5.3 |

---

## 8. Measuring Engagement

**`SEP-19`: engagement is measured on coverage, reach, reply and silence — never on volume sent.**

| Measure | Definition | Target | Response when missed |
|---|---|---|---|
| **Group coverage** | Groups meeting their minimum frequency ÷ 31 groups | **100%** | Two consecutive misses → PMO in the next weekly report (`CM-002` §4.8) |
| **Reply rate** on the four confirming communications | Readiness, stop-confirmation, start-acknowledgement, legacy-withdrawal (`CA-07`) | **100%** | A site with no reply is **not ready** (`CH-001` `PR-5`) |
| **Bengali delivery rate** to `S07`–`S10` | BN communications ÷ all communications to those groups | **100%** | `SEP-13` — logged as a missed communication |
| **Objection flow** | Objection instances logged per group per wave | **> 0** for every `Support` and `Partner` group | `SK-16` — two waves of silence is a coverage failure, investigated |
| Champion cascade | Champions cascading within 5 working days ÷ confirmed champions | > 90% | `CH-005` §7 network health |
| Forum attendance, Bengali track | Share of champion-forum attendance on the Bengali track | Tracked, not targeted | A collapsing Bengali track means the network is drifting to head office (`NW-15`) |
| **Escalation latency** | Time from `Interest` objection logged to Steering agenda | ≤ one meeting cycle | `CH-001` `OCM-18` |

> **`SEP-20` — "messages sent" is not a measure and is not reported.** It is the number most easily
> improved and least connected to whether anybody was reached. `CM-016` `UP-05` makes the same point
> about redefining "active"; this is its communication equivalent.

---

## 9. Governing Rules

| # | Rule | Class |
|---|---|:--:|
| `SEP-01` | `06-01` §3/§8 with `06-02` §4 is the single authoritative wave calendar; every other statement of wave months is superseded | **H** |
| `SEP-02` | The calendar correction is executed once, register-wide, by a named owner — never file by file | **H** |
| `SEP-03` | The hypercare-duration reconciliation is a separate open question and is not closed by the calendar declaration | **H** |
| `SEP-04` | `OP-001` §4.1 is the definitive external-population enumeration; `CM-002` §4.3 is re-derived from it and no third enumeration is created | **H** |
| `SEP-05` | Adopting a single enumeration means adopting one file's authority, and correcting it where another file is right | **H** |
| `SEP-06` | No internal group is invented here; `05-04` and `MD-009` govern | **H** |
| `SEP-07` | A group is consulted only on what it can decide or materially shape | **H** |
| `SEP-08` | The field pilot's findings are reported back to technicians in Bengali, including what will not be changed | **H** |
| `SEP-09` | A group with a decision right over a go-live is registered whether or not it appears in an operational role register | **H** |
| `SEP-10` | The `CM`/`EO` boundary is whether a commercial relationship already exists | **H** |
| `SEP-11` | The register rows on both sides of the boundary state it reciprocally | **H** |
| `SEP-12` | High impact with low influence receives the heaviest support, not the lightest | **H** |
| `SEP-13` | An English-only communication to `S07`–`S10` is logged as a missed communication | **H** |
| `SEP-14` | Institutionalising WhatsApp as a system of record is a `GV-003` change, not a channel choice | **H** |
| `SEP-15` | A two-way channel with no answer route is one-way; the answer route is a resourced obligation | **H** |
| `SEP-16` | The communication log is a controlled record under `GV-011` | **H** |
| `SEP-17` | Every group has exactly one owning communicator; external groups are reached through their existing relationship owner | **H** |
| `SEP-18` | An obligation whose cadence is shorter than its translation lead time is escalated as a decision, never absorbed | **H** |
| `SEP-19` | Engagement is measured on coverage, reach, reply and silence | **H** |
| `SEP-20` | "Messages sent" is not a measure and is not reported | **H** |
| `SEP-21` | Every scheduled item is anchored to a gate month and expressed as an offset, never as an absolute date (`CA-01`, `CA-02`) | **H** |
| `SEP-22` | No programme communication precedes charter approval (`CA-17`) | **H** |
| `SEP-23` | A visible slip requires a holding communication within 5 working days (`CA-18`) | **H** |
| `SEP-24` | Stakeholder populations are re-counted at every wave boundary, never carried forward (`SK-17`) | **H** |

---

## 10. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| `SEP-Q-01` | **Reconcile the hypercare window** across `06-01` §5, `06-01` §6, BRD §21.5–21.6 and `OP-002` §4.3, and correct the three upstream documents | **Programme Manager with the Support Lead** | **W1 − 6 weeks** | `CM-003` §4.4's `T+4 weeks` anchor; `M7`/`M8` timing; `AUDIT-019` `R-03` |
| `SEP-Q-02` | **`CM-007`'s nightly bilingual bulletin** — same-day Bengali route, or an explicit decision that it is English at the sites that need it most? | Localisation Lead with Support Lead | **W1 − 3 weeks** | Hypercare communication at every wave; `AUDIT-019` `R-08` |
| `SEP-Q-03` | Who executes the register-wide calendar correction (§3.4), and when? | **PMO with Enterprise Architecture** | **W0** | `AUDIT-019` `R-02`, open since 2026-08-20 |
| `SEP-Q-04` | Who owns communication to **franchise and channel partners (0–30 from W8)** and to **corporate client administrators (50–200)**, both newly registered by §4.1? | CCO with Account Management | W4 − 12 weeks | Two populations with no communicator |
| `SEP-Q-05` | **Who owns the 1,000–4,000 marketplace seller technicians** as a stakeholder group, and through which channel? | CCO with Marketplace Ops | **W7 − 20 weeks** | The largest external population; `CM-015` `O-06`; `CH-002` `TPD-Q-06` |
| `SEP-Q-06` | Is the standing translation load (§7.3) funded, including 36 bilingual newsletter issues and per-wave reprints to 51+ sites? | Localisation Lead with CFO | W0 | `CM-005` `O-04`; every bilingual obligation |
| `SEP-Q-07` | Who is the Change Lead? Every cadence in this plan is owned by a vacant post | **CEO with HR Director** | **W0** | `CH-001` `OCM-Q-01`; `AUDIT-019` `R-11` |

---

## 11. Decisions Recorded

| # | Decision | Options considered | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| `CH-003-D-01` | Which wave calendar is authoritative | `06-01`/`06-02` · Master Index · publish both with a mapping | **`06-01` §3/§8 with `06-02` §4** | `06-01` is the delivery document; `06-02` independently agrees with it; the Master Index cites `06-01` and does not match it, which makes it a transcription error rather than a competing position | Four artefacts require correction (§3.4). `AUDIT-019` `CM-03` closes on execution, not on this declaration |
| `CH-003-D-02` | Which external enumeration is definitive | `CM-002` §4.3 · **`OP-001` §4.1** · author a third here | **`OP-001` §4.1**, corrected by one row from `CM-002` | `OP-001` derived its enumeration from `04-00` and the integration catalogue and declared it definitive; `CM-002` omits a 1,000–4,000-person population. Authoring a third would be the defect both findings describe | Five reconciliations, one of them running the other way (`SEP-05`) |
| `CH-003-D-03` | How to fix the `CM`/`EO` boundary | Prose in each file · **an owning table in this document** · a new content file | **A table here, mirrored into the register rows** | `AUDIT-019` `CM-09` and `AUDIT-018` `R-07` both observe that prose boundaries decay and tables do not. `CM-008` §4.2's twelve-row table is the precedent that worked | §5's twelve-row table; three actions with owners |
| `CH-003-D-04` | Whether to restate `CM-002`'s 27 rows and `CM-003`'s 18 rules | Restate · **govern and cite** | **Govern and cite** | `CP-01`. Three files in this category already risk duplicating Category 16; the boundary is what this plan adds, not the content | This document is short in content terms and load-bearing in governance terms |
| `CH-003-D-05` | Recommend option A or present neutrally for the bilingual bulletin | **Recommend A** · neutral | **Recommend A** | Option B is the first recorded exception to `SK-08`, a Class `H` rule. A plan that presents breaking its own hard rule as an equal option has not planned | `SEP-Q-02` carries the recommendation; the decision stays with the Localisation and Support Leads |

---

## 12. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| `AC-01` | One wave calendar is declared, with the divergence quantified wave by wave | §3.1, §3.3 — ten rows, divergence stated in months |
| `AC-02` | The correction is assigned to named owners with dates | §3.4 — five rows |
| `AC-03` | A single external enumeration is adopted and reconciled in both directions | §4.1 — eleven rows plus five reconciliations |
| `AC-04` | The `CM`/`EO` boundary exists as a table | §5 — twelve rows |
| `AC-05` | Stakeholders invisible to the content estate are registered | §4.5 — five groups, three of which can stop a wave |
| `AC-06` | Engagement measures are outcome measures, not volume measures | §8 — seven measures, none of them "messages sent" |
| `AC-07` | Every open question has an owner and a needed-by date | §10 — seven of seven |
| `AC-08` | No content from `CM-002` or `CM-003` is restated | §1.1 out-of-scope; `CH-003-D-04` |
| `AC-09` | Standards carry editions and verification dates | §2.1, §14 |
| `AC-10` | Approval record | ⬜ **Cannot be met** — `PGD-A2-25` |

---

## 13. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | [`CH-001`](CH-001_Organisational_Change_Management_Plan.md) | Engagement executes the change strategy; §6.3's resistance response consumes this plan's detection |
| Upstream | `GV-002` Governance, RACI & ToR | The bodies that receive escalations |
| Upstream | `GV-004` Integrated Programme Plan | The gate months this plan anchors to |
| Upstream | `GV-011` Documentation Control | Controls the communication log |
| Lateral | [`CH-004`](CH-004_Adoption_Measurement_and_Reinforcement_Plan.md) | Campaign consent and channel rules; the campaign/transition distinction |
| Lateral | [`CH-005`](CH-005_Super_User_and_Champion_Network_Charter.md) | Champions are a stakeholder group **and** a channel |
| Lateral | `../../project_content/16_Change_Management_and_Comms/CM-002...`, `CM-003...` | The register and calendar this plan governs |
| Lateral | `../../project_content/17_Operations_Support_and_Runbooks/OP-001...`, `OP-002...` | The adopted external enumeration; the mis-anchored duration table |
| Downstream | [`RL-002`](../12_Release_Deployment_and_Transition/RL-002_Deployment_Plan_and_Go_Live_Checklist.md) · [`RL-004`](../12_Release_Deployment_and_Transition/RL-004_Rollout_and_Branch_Wave_Deployment_Plan.md) *(both issued 2026-08-19)* | Consume the declared calendar — **and must be checked against §3.3, because they were written in the same window as this declaration**; audit finding `CHA-12` |
| Downstream | `SV-005` Hypercare Plan ⛔ | Consumes `SEP-Q-01`'s reconciliation |
| Downstream | Category 18 `EO` | The boundary in §5 |

---

## 14. References

**Within this repository**
[`../PGD-000_Master_Register_of_Project_Guiding_Documents.md`](../PGD-000_Master_Register_of_Project_Guiding_Documents.md) ·
[`./_CATEGORY_OVERVIEW.md`](_CATEGORY_OVERVIEW.md) ·
[`CH-001`](CH-001_Organisational_Change_Management_Plan.md) ·
[`CH-002`](CH-002_Training_Plan_and_Delivery_Schedule.md) ·
[`CH-004`](CH-004_Adoption_Measurement_and_Reinforcement_Plan.md) ·
[`CH-005`](CH-005_Super_User_and_Champion_Network_Charter.md)

**Workspace**
[`../../project_content/16_Change_Management_and_Comms/CM-002_Stakeholder_Map_and_Communication_Plan.md`](../../project_content/16_Change_Management_and_Comms/CM-002_Stakeholder_Map_and_Communication_Plan.md) ·
[`../../project_content/16_Change_Management_and_Comms/CM-003_Communication_Calendar_by_Wave.md`](../../project_content/16_Change_Management_and_Comms/CM-003_Communication_Calendar_by_Wave.md) ·
[`../../project_content/17_Operations_Support_and_Runbooks/OP-001_Support_Model_Tiering_and_Routing_Content.md`](../../project_content/17_Operations_Support_and_Runbooks/OP-001_Support_Model_Tiering_and_Routing_Content.md) ·
[`../../project_content/1000FiX_ERP_Content_Master_Index.md`](../../project_content/1000FiX_ERP_Content_Master_Index.md) ·
[`../../project_content/_AUDIT/AUDIT-019_Category_16_CM_Content_Audit.md`](../../project_content/_AUDIT/AUDIT-019_Category_16_CM_Content_Audit.md) ·
[`../../1000fix_ERP_Module/06_Delivery_and_Implementation/06-01_Implementation_Roadmap_and_Phasing.md`](../../1000fix_ERP_Module/06_Delivery_and_Implementation/06-01_Implementation_Roadmap_and_Phasing.md) ·
[`../../1000fix_ERP_Module/06_Delivery_and_Implementation/06-02_KPI_Benefits_and_Acceptance_Criteria.md`](../../1000fix_ERP_Module/06_Delivery_and_Implementation/06-02_KPI_Benefits_and_Acceptance_Criteria.md)

**External standards** *(all verified 2026-08-19)*

| Source | Edition | Verified |
|---|---|---|
| ISO 21502:2020 | §7.4 communication; §7.5 stakeholder engagement | 2026-08-19 |
| ISO 21500:2021 | Project, programme and portfolio management — context and concepts | 2026-08-19 |
| ACMP *Standard for Change Management* | **Version 2**, 26 August 2025 — process group 2, including 5.1.4 | 2026-08-19 |
| PMBOK Guide | **7th Edition** — Stakeholder performance domain | 2026-08-19 |
| ISO 10018:2020 | People engagement | 2026-08-19 |

---

## 15. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-19 | Enterprise Architecture with Change Management | Initial issue. Declares the single wave calendar (`CM-03`), adopts the single external enumeration (`CM-08`), and fixes the `CM`/`EO` boundary in a table (`CM-09`, `AUDIT-018` `R-07`) | ⬜ Blocked — `GV-001` `CC-01` |

---

*`CH-003` · Category 13 · 1000FiX ERP System v2.0 · CONFIDENTIAL — Internal Use Only*
