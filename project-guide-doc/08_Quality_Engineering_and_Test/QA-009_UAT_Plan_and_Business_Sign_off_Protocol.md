---
id: QA-009
title: UAT Plan and Business Sign-off Protocol
category: 08 — Quality Engineering & Test
code: QA
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-18
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Business Owners Forum with the QA Lead
approver: Chief Executive Officer as Executive Sponsor, with the Chief Technology Officer
standards_basis: >
  ISO/IEC/IEEE 29119-3:2021 §8 (test plan) · ISO/IEC/IEEE 29148:2018 §5.2.8 (verifiability) ·
  ISO 21502:2020 (acceptance) · PRINCE2 7 (product acceptance) · ISO 9001:2015 §8.6 (release of
  products and services)
traces_to: >
  PGD-000 QA-009 · 06-02 §4 G1-11 (UAT signed off by named super-users) · G4-10 · G5-01 ·
  TS-006…TS-011 (352 scripts) · AUDIT-014 TS-06 (TS-008 no staged stock; TS-015 no field logistics) ·
  TS-10 (nine roles with no course pack or SOP) · 06-01 §4 (business availability — the binding constraint)
depends_on: QA-001 (levels, sign-off authority) · QA-002 LP-5 (window, schedule) · QA-004 (frozen data, role accounts) · QA-010 (defect thresholds) · GV-009 (gate outcomes)
verified_on: 2026-08-18
enumeration_timestamp: 2026-08-18 22:01 (+06)
priority: P0
needed_by: W1
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# QA-009 — UAT Plan and Business Sign-off Protocol

### Category 08 · Code `QA` · ISO/IEC/IEEE 29119-3:2021 §8 · ISO 21502:2020 · ISO 9001:2015 §8.6

---

> **Before writing, read this.**
>
> 1. **`PG-01` Register-first.** Row `QA-009` exists in `PGD-000` Category 08, status ◐ `P0` `W2`.
>    **Issued at `Now`** — `G1-11` consumes it at Month 4.
> 2. **`PG-03` Count, do not consult.** Script, role and headcount figures counted at
>    **2026-08-18 22:01 (+06)** from the six UAT packs and `05-04`.
> 3. **`PG-06` Cite standards.** §2.1.
> 4. **`PG-M4` Verify citations.** Standard editions inherited from `QA-001` §18.

---

## 1. Purpose

UAT is the acceptance gate for a 67-module system, and **`G1-11` — *"UAT signed off by named
super-users"* — is the criterion on which the first go-live turns.** `TS-006`…`TS-011` supply
**352 excellent scripts** across six role families. What has never existed is the protocol: who
executes, who may sign, what a signature means, what happens when a script fails, and what a
**conditional** acceptance commits the business to.

Three counted facts define the work:

| # | Fact | Source | Consequence |
|:--:|---|---|---|
| 1 | **Three packs cannot be executed at all**, for want of physical resources — not for technical reasons | `AUDIT-014` `TS-06` | Five gate criteria are unevidenceable; the failure mode is that the packs are marked passed by being skipped |
| 2 | **Nine roles cannot satisfy `UA-03`** — no course pack, or no SOP, and two of them carry 51+ headcount | `AUDIT-014` `TS-10` | An untrained executor measures training, not the system |
| 3 | **Business availability is *"the binding constraint on the programme"*** — the programme's own words | `06-01` §4 | UAT is the only level whose capacity the QA budget cannot buy |

> **A UAT script written in tester language is signed without being read**: the signature is
> obtained, the defect is not found, and 150–250 agents discover it on the counter in front of a
> customer. `TS-006` says this, and it is the reason this protocol makes the *signature statement*
> — not the document — the object of accountability.

### 1.1 Scope

**In scope**

| # | Covered |
|---|---|
| 1 | **What UAT is and is not** — the three things it is routinely confused with (§3) |
| 2 | **Participant selection** — super-users, their number, their release, their authority (§4) |
| 3 | **The training precondition `UA-03`, and the nine roles that cannot meet it** (§5) |
| 4 | **The execution dependencies** — `TS-006`, `TS-008`, `TS-015` — resourced, costed and owned (§6) |
| 5 | **Execution protocol** — how a script is run, evidenced and recorded (§7) |
| 6 | **Defect triage authority during UAT** (§8) |
| 7 | **The sign-off protocol** — what is signed, by whom, and what it commits (§9) |
| 8 | **Conditional acceptance** — the rules, and the two things that may never be conditional (§10) |
| 9 | **The payroll parallel run** — the one UAT that is not a script pack (§11) |
| 10 | **Schedule and gate evidence** (§12) |

**Explicitly out of scope**

| Topic | Owned by | Why |
|---|---|---|
| The UAT window, environment and level scheduling | `QA-002` `LP-5` | Consumed |
| Script content | `TS-006`…`TS-011` | Governed here, authored there |
| Defect severity definitions and triage rules | `TS-018`, `QA-010` | Consumed; §8 adds only the UAT-window authority |
| Gate outcomes and consequences | `GV-009` §6.3 | A UAT sign-off is an input to a gate, not the gate |
| Frozen data and role accounts | `QA-004` | Preconditions |
| Training content and delivery | `TR-*`, `CH-*` | §5 states the dependency; it does not build the courses |
| Usability research | `UX-008` | UAT is acceptance, not research — §3.2 |

### 1.2 Intended audience

| Audience | Use |
|---|---|
| **Super-users** | §7, §9 — what they are being asked to do and what their signature means |
| **Module business owners** | §9, §10 — the acceptance they are accountable for |
| Business Owners Forum | The protocol they own |
| QA Lead | §7, §8, §12 — running the cycle |
| Programme Manager | §4.3, §6 — the business release and the physical dependencies |
| CFO and Executive Sponsor | §6.4, §10 — the cost of the dependencies, and what a conditional acceptance commits |

---

## 2. Basis and Inputs

### 2.1 Standards conformance

| Standard | Conformance | Departure |
|---|---|---|
| **ISO/IEC/IEEE 29119-3:2021 §8** | A level plan under `QA-002` `LP-5`; elements not restated are inherited from `QA-002` §2.1 | None |
| **ISO/IEC/IEEE 29148:2018 §5.2.8** | Every accepted requirement was verifiable and was verified | None |
| **ISO 21502:2020** | Acceptance as a defined project practice with a named accepter | None |
| **PRINCE2 7** | Product acceptance and the quality register | **Departure:** no separate quality register; `TS-018` and `QA-010` hold it |
| **ISO 9001:2015 §8.6** | *Release of products and services* — release only on evidence of conformity, with **traceability to the person authorising release** | Adopted directly. §9.2's signature record **is** the §8.6 record, and `M23` will be audited against it |

### 2.2 Source material relied on

| Source | What it establishes |
|---|---|
| `TS-006` | **80 scripts**, service operations roles; **the shared UAT method the other five packs reuse**; `UA-01`…`UA-23` |
| `TS-007` | **60 scripts**, commercial and contract roles |
| `TS-008` | **58 scripts**, supply chain; `UA-23`'s physical-stock requirement |
| `TS-009` | **46 scripts**, finance; the statutory-output position — *"only the function that files can make it"* |
| `TS-010` | **36 scripts**, people and workforce; the payroll parallel run |
| `TS-011` | **72 scripts**, customer and partner portals; executed **as the external party** |
| | **Total: 352 scripts** counted at 22:01 (+06) |
| `05-04` §1, §7 | Role headcounts and the **Approval Authority Matrix** |
| `06-01` §4 | Super-users **2–3 per module at 30% during UAT**; *"the binding constraint on the programme"* |
| `06-02` §4 | `G1-11`, `G4-10`, `G5-01` and the conditional-pass rule |
| `GV-009` §6.3, §9.2 | Gate outcomes; `EN-04` super-users named and released |
| `AUDIT-014` `TS-06`, `TS-10` | The three unexecutable packs; the nine untrainable roles |
| `TS-018` | Severity, priority, triage rules `TR-01`…`TR-09` |

### 2.3 What this document closes

| Finding | Source | How | Residual |
|---|---|---|---|
| `TS-06` (`TS-006`, `TS-008`, `TS-015` halves) | `AUDIT-014` | §6 resources each as a **named, costed line with an owner and a date**, and makes their absence a gate-entry failure at T−6 rather than a discovery at T−0 | Funding — `Q-01` |
| `TS-10` | `AUDIT-014` | §5.3 requires, per role, either the course registered or a **recorded interim briefing route** — and names the nine | L&D authoring — `Q-02` |
| `G1-11` unevidenced | `06-02` | §9 defines the signature, its statement, its record and its `E4` evidence | — |
| `QA-009` register row ◐ | `PGD-000` | *"The plan is where those dependencies get resourced"* — §6 | — |

---

## 3. What UAT Is, and What It Is Not

### 3.1 The definition

> **UAT is the business owner's answer to one question: *does this system let my function do its
> work correctly?*** It is not a re-run of system testing with business people at the keyboard, and
> it is not the last chance to find defects.

| # | Rule |
|---|---|
| `UAP-01` | **UAT does not begin until L5 and L6 have exited** (`QA-001` §8.2). UAT used as system testing consumes the scarcest resource on the programme — business time — on defects a cheaper level should have found |
| `UAP-02` | **A super-user executes their own scripts.** A delegate's signature is not acceptance |
| `UAP-03` | **A defect from a super-user's business judgement is a requirement defect**, routed to the requirement owner, **not** logged as a test error (`TS-006` `UA-06`; `TS-018` `TR-04`) |
| `UAP-04` | **UAT is executed in the executor's language** (`TDS-14`). Five of `TS-006`'s ten roles are Bengali-first, and `TS-002`, `TS-006`, `TS-008`, `TS-009`, `TS-011` and `TS-015` all carry Bengali counterparts |

### 3.2 The three confusions

| Confused with | Difference | Consequence of confusing them |
|---|---|---|
| **System testing** | System testing asks *does it meet the specification*; UAT asks *does it let me work* | Business time spent on defects L5 should have caught; UAT slips; the gate slips |
| **Usability research** (`UX-008`) | Research asks *is this design good*; UAT asks *can my function operate* | A design finding logged as an acceptance failure blocks a gate on a preference — or worse, an acceptance failure is dismissed as a preference |
| **Training** | Training teaches the system; UAT tests it | `UA-03`: an untrained executor measures training. §5 |

### 3.3 What UAT alone can prove

| Only UAT proves | Why |
|---|---|
| That a role's real work can be completed end to end, in its own language, at its own pace | No specification captures the whole of a role's work |
| That a commercial number is right | *"They are found by the person whose number they are"* — `TS-007` |
| That a statutory output complies | *"Mushak correctness is not a developer's judgement and it is not QA's"* — `TS-009` |
| That an external party can complete their task | *"The company must find them first, by being them"* — `TS-011` |
| That custody and stock behave as the people holding them expect | `TS-008` |

---

## 4. Participants

### 4.1 Who is a super-user

| Criterion | Requirement |
|---|---|
| Does the role's real work | A super-user who does not perform the role cannot judge whether the system lets it be performed |
| Named individually | `G1-11` requires *"named super-users"*; a function is not a name |
| Released for the window | `EN-04`; §4.3 |
| Trained (`UA-03`) | §5 |
| Speaks the language the role speaks | `UAP-04` |
| Authorised to raise a defect | Without this a super-user reports problems to a manager who filters them |

### 4.2 Coverage

`06-01` §4 commits **2–3 super-users per module** at 30% during UAT.

| Pack | Scripts | Role families | Super-users needed | Headcount context |
|---|---:|---:|---:|---|
| `TS-006` service operations | 80 | 10 | **12–18** | Covers **526–1,022 people**; `R06` alone is **51+** |
| `TS-007` commercial | 60 | 6 | 8–12 | Small populations, high value |
| `TS-008` supply chain | 58 | 6 | **8–12** | Covers 135–274 people |
| `TS-009` finance | 46 | 5 | 6–10 | **`R29` cashier is 51+** |
| `TS-010` people and workforce | 36 | 5 | 6–8 | |
| `TS-011` portals | 72 | 7 external | **10–14** | **External parties — §4.4** |
| **Total** | **352** | **39** | **50–74** | |

> **`UAP-05`.** **50–74 named individuals at 30% for a 4–6 week window is the largest single business
> commitment in the programme**, and it recurs at every wave. It is stated here as a number because
> `06-01` §4 states the constraint in words and no document has yet stated its size.

### 4.3 Release

| # | Rule |
|---|---|
| `UAP-06` | **Super-users are named at T−10 weeks and released at T−6** (`EN-04`), and the release is a line manager's commitment recorded in writing, not an intention |
| `UAP-07` | **A released super-user's operational work is backfilled or deferred.** A super-user doing both jobs does neither, and the one that suffers is UAT |
| `UAP-08` | **Non-release is escalated at T−4**, not at the window's start. `GA-11`: a gate that discovers at T−0 that its evidence cannot be produced has already failed |
| `UAP-09` | **The same individuals wherever possible across waves.** Continuity is worth more than breadth; a super-user who tested W1 finds W2 regressions nobody scripted |

### 4.4 External participants — `TS-011`

`TS-011`'s scripts are executed **as the external party**: a customer, a corporate administrator, a
vendor, a marketplace seller, a brand partner, a courier, a referral partner.

| # | Rule |
|---|---|
| `UAP-10` | **Where a real external party can be engaged, they are** — a pilot corporate client, a pilot seller, a pilot courier. An employee role-playing a customer knows too much |
| `UAP-11` | **Where they cannot, an employee executes as the party and the substitution is recorded**, because it materially weakens the result and the ACR-equivalent claim must say so |
| `UAP-12` | **External participants sign a confidentiality undertaking** and use only synthetic data (`QA-004` `TDM-01`) |
| `UAP-13` | **`P07` seller-isolation scripts require two distinct seller accounts, executed by two people.** One person switching accounts will not detect a cross-seller leak the way two simultaneous sessions will — and *"a seller who can see another seller's payout"* is `TS-011`'s and `TS-018`'s named `S1` |

---

## 5. The Training Precondition

### 5.1 `UA-03`

> `TS-006` `UA-03`: **an executor is trained before execution**; `UA-15`: **each script names the
> `SP` procedure it performs**, so a failure can be diagnosed to the system, the procedure or the
> training.

Together these make a UAT failure diagnosable. **Without them, every failure is ambiguous** — and an
ambiguous failure in an acceptance window is resolved by whoever is most confident, not by whoever is
right.

### 5.2 The rules

| # | Rule |
|---|---|
| `UAP-14` | **An untrained executor's scripts are suspended** (`MTS-U6`), not executed and discounted |
| `UAP-15` | **Training is delivered before the window opens**, not inside it. Training inside the window consumes the 30% twice |
| `UAP-16` | **A script whose `SP` does not exist is executed with the gap recorded on the script**, so a failure is attributed correctly rather than to the system by default |

### 5.3 The nine roles that cannot meet it

`AUDIT-014` `TS-10`, confirmed at 22:01 (+06):

| Role | Headcount | Missing | Pack | Route required by T−6 |
|---|---:|---|---|---|
| **`R06` Branch Manager** | **51+** | **No SOP** — 11 of 12 `R06` scripts have no `SP` to diagnose against | `TS-006` | Register `SP-035`, **or** record the gap as accepted (`TS-13`) |
| **`R29` Cashier** | **51+** | No course pack | `TS-009` | Course, or interim briefing route |
| `R28` Warranty Claims Officer | 4–10 | No course pack — **runs the whole claim pipeline against a `KPI-038` leakage target** | `TS-007` | Course |
| `R14` Data Services Technician | 5–12 | No course pack — **the only role with `T5` restricted-data access** | `TS-006` | **Course — not an interim route.** `T5` access without training is a `SC-002` insider exposure |
| `R13` Remote Support Engineer | 15–40 | No course pack | `TS-006` | Course or interim route |
| `R25` Retail / Refurbishment Officer | 5–15 | No course pack | `TS-007` | Course or interim route |
| `R23` Marketing Manager | 2–4 | No course pack **and no SOP** | `TS-007` | Both |
| `R05` Operations Director | 1–2 | No course pack | `TS-006` | Interim briefing acceptable |
| `R03` CFO | 1 | No course pack | `TS-009` | Interim briefing acceptable |

> **`UAP-17`.** For each of the nine, by **T−6 weeks**, either the course pack is registered and
> delivered, **or** an interim briefing route is recorded naming who briefs the executor and on what.
> **`R14` is excluded from the interim option** — it is the only role with `T5` restricted-data
> access, and an untrained holder of the estate's most sensitive access is a security exposure before
> it is a test-quality one.
>
> **Two of the nine carry 51+ headcount**, which means the gap is not a small-population edge case.
> Raised as `Q-02`.

---

## 6. Execution Dependencies

### 6.1 Why this section exists

`AUDIT-014` `TS-06`: **three packs require physical conditions that no programme document
allocates**, and *"these are not preferences"* — five gate criteria are physical activities written
into an acceptance gate. `QA-001` §10.4 names them `MTS-D3`, `MTS-D4`, `MTS-D5`; `QA-002` §12.5
attaches them to a plan and a wave. **This section resources them.**

### 6.2 `TS-006` — the branch kit (`MTS-D3`)

| Item | Specification | Quantity | Why this exactly |
|---|---|---:|---|
| Laptop | **1366×768** | 2 | The real branch screen. A test on a 1920×1080 monitor does not reproduce the layout branch agents see |
| Thermal receipt printer | Branch model | 2 | `G1-03`'s 3-minute intake includes printing |
| Barcode scanner | Branch model | 2 | |
| Signature pad | Branch model | 2 | Custody and handover evidence |
| Android device | **Mid-range, Android 11, 3 GB RAM** | 3 | The floor spec; `NFR-036` is stated against it |

**Owner: Operations Director. Needed: W1 UAT window. Blocks: `G1-03`.**

### 6.3 `TS-008` — staged stock (`MTS-D4`)

| Item | Specification | Why |
|---|---|---|
| **40 labelled real parts** across **3 locations** | Including **one serialised**, **one expired-shelf-life**, **one hazardous** | `UA-23`: *"a stock script that does not touch stock proves the system will record whatever it is told"* |
| The branch's own scanner and label printer | Not a lab substitute | Label format and scan behaviour are branch-specific |
| A vehicle | For the custody scripts | Custody transfer is a physical act |

**Owner: Inventory Manager. Needed: W2 UAT window. Blocks: `G2-06` (inventory accuracy **verified by
count**), `G2-07`.**

> **`UAP-18`.** The stock is **withdrawn from live inventory and returned**, under a recorded
> movement. It is not purchased for the test, and it is not notionally allocated. `G2-06` is verified
> **by count**, and a count needs something to count.

### 6.4 `TS-015` — field logistics (`MTS-D5`)

| Element | Requirement |
|---|---|
| Locations | **Six named**, including a **no-signal basement** and a **moving vehicle** |
| Networks | **Three mobile operators** |
| Devices | Three floor-spec devices |
| Duration | **Full shifts** — a 10-minute aeroplane-mode toggle does not reproduce a technician whose signal came and went four times across a nine-hour shift |
| Executors | **Real technicians**, not testers |
| Observation | **A server-side observer**, because *"sync reported complete while queued"* is an automatic `S1` and only the server can see it |
| Instrumentation | On-device |
| **Safety** | **An `SP-030`-equivalent briefing that covers test personnel** |

**Owner: Programme Manager. Needed: W2, at T−4. Blocks: `G2-02`, `G2-03`; `NFR-036`, `NFR-037`.**

> **The safety question is unanswered.** Testers will work at six locations, in a moving vehicle and
> on customer premises, **deliberately without connectivity and therefore without a means of
> contact**. `SP-030` governs technicians and does not mention test personnel (`TS-015` `O-06`).
> **This is a duty-of-care matter before it is a test-logistics matter** — `QA-001` `QAA-07`, `Q-03`.

### 6.5 The gate consequence

> **`UAP-19`.** Each of §6.2–§6.4 is checked at **T−6 weeks** under `EN-03`. **A pack whose physical
> dependency is absent is recorded as *not executable*, and its gate criteria as *not evidenced*
> (`MTS-R2`) — never as passed.** A criterion requiring a count, a print or a field measurement is
> not discharged by a demonstration that the software would have handled it.

---

## 7. Execution Protocol

| # | Rule |
|---|---|
| `UAP-20` | **Scripts are executed in the order the role would work**, not in identifier order. A day's work has a shape and defects live in the transitions |
| `UAP-21` | **Every step records pass, fail or blocked**, with a comment where it is not a clean pass. *"Blocked"* is a distinct outcome and is never recorded as a fail — it hides the dependency |
| `UAP-22` | **Evidence is captured per `TS-001` §4.6** — screenshots, references, outputs. A printed Mushak, a scanned label, a signed handover are physical evidence and are retained |
| `UAP-23` | **The executor writes the failure in their own words** before anyone reclassifies it. A defect rewritten by QA before triage loses the business meaning that made it worth raising |
| `UAP-24` | **A script is not re-run to obtain a pass** without the fix being deployed and the re-run recorded as a re-run. A quietly repeated script is how a failure disappears |
| `UAP-25` | **The dataset version and the build version are recorded on every script set** (`TDM-23`, `TAF-35`), so a signature attaches to a known state |
| `UAP-26` | **Daily stand-up during the window**: executed, passed, failed, blocked, and what is stopping anyone. UAT failure is usually a blockage, not a defect |

---

## 8. Defect Triage During UAT

`TS-018` `TR-01`…`TR-09` own the rules. Three additions apply **only inside a UAT window**, where the
cost of a wrong routing decision is a super-user's day.

| # | Addition |
|---|---|
| `UAP-27` | **Triage runs daily inside the window** (`TR-01`), and **`S1` defects are triaged on discovery**, because an `S1` usually blocks other scripts |
| `UAP-28` | **The module business owner is present.** `TR-02` requires it; inside a window it is not waivable, because priority set without the person carrying the consequence is priority set wrongly |
| `UAP-29` | **A business-judgement defect is escalated, not fixed** (`TR-06`, `UAP-03`). It goes to the requirement owner and, where statutory or legal, into `CG-013` escalation |
| `UAP-30` | **A defect found in a shadow process — a spreadsheet, an out-of-system workaround — is a scope gap, not a defect** (`TS-012` `EE-05`), routed to the Programme Manager. Logging it as a defect hides it inside a defect count |
| `UAP-31` | **Severity is never adjusted to affect the sign-off** (`TS-018` `DF-04`, `TR-09`; `QA-001` `MTS-R3`). Where contested, the disagreement is recorded and escalated |

---

## 9. The Sign-off Protocol

### 9.1 Three signatures, three different statements

> **`UAP-32`. A signature is on a *statement*, not on a document** (`QA-001` `MTS-S1`). The signatory
> is accountable for the statement being true, and `GA-01` requires the evidence behind it to be
> dated, attributable and reproducible.

| Level | Statement signed | Signatory | Class |
|---|---|---|:--:|
| **Script set** | *"I executed these scripts myself, and the system does what my role requires."* | **The super-user, by name** | `E4` |
| **Function** | *"My function accepts this wave's scope, including the conditional acceptances listed."* | **The module business owner** | `E4` |
| **Wave** | *"Business acceptance is complete for this wave, on the evidence and exceptions recorded."* | **Business Owners Forum chair**, countersigned by the **Head of Quality Engineering** | `E4` + `E6` |

### 9.2 The record — and its ISO 9001 role

ISO 9001:2015 §8.6 requires release on evidence of conformity **with traceability to the person
authorising release**. §9.1's record is that record, and `M23`'s internal audit (`G5-04`) will be run
against it.

| Field | Content |
|---|---|
| Wave, scope, pack, script identifiers | With counts |
| Executor | **Name and role** — never a function |
| Dates | Execution window, signature date |
| Build and dataset version | `UAP-25` |
| Results | Passed / failed / **blocked**, per script |
| **Not executed** | Named, with the reason (`MTS-R2`) |
| Defects raised | With severity and current state |
| **Conditional acceptances** | §10, each with accepter and remediation date |
| Signature | Per §9.1, with the statement reproduced above it |
| Retention | Programme life + 5 years (`GA-08`) |

### 9.3 Statutory outputs are signed by the function that files

> `TS-009`: *"Mushak correctness is not a developer's judgement and it is not QA's… Gate 3 requires
> Mushak invoices accepted with zero NBR exceptions — that is a claim about a regulator's behaviour,
> and only the function that files can make it."*

| # | Rule |
|---|---|
| `UAP-33` | **The CFO signs statutory-output acceptance** — Mushak 6.1/6.2/6.3/6.6/9.1, BEFTN, income tax — and no delegate signs it |
| `UAP-34` | **`G3-04` additionally requires `E8` third-party confirmation.** *"Accepted with zero NBR exceptions"* is a statement about NBR, and only NBR's acceptance evidences it. A successful internal validation is not acceptance |

### 9.4 What a signature does not do

| # | Rule |
|---|---|
| `UAP-35` | **A signature does not close a defect.** Defects close on a verified fix (`LVP-06`) |
| `UAP-36` | **A signature does not pass a gate.** It is one input; `GV-009` §6.3 owns the outcome |
| `UAP-37` | **A signature is not transferable.** If the named super-user leaves, the scripts are re-executed by their successor at the next window — the signature is not reassigned |

---

## 10. Conditional Acceptance

### 10.1 The rules

`06-02` §4: *"All criteria must be met; partial passes are recorded as conditional with a dated
remediation plan."*

| # | Rule |
|---|---|
| `UAP-38` | A conditional acceptance names: **the scripts not passed, the defect, the business risk accepted, the remediation date, and the business owner accepting it** |
| `UAP-39` | **It is carried into every subsequent gate report until closed** — the same treatment as a truncation (`QA-001` §12.3) |
| `UAP-40` | **It is accepted by the business owner who carries the consequence**, never by QA, never by the Programme Manager, never by the delivery vendor |
| `UAP-41` | **A remediation date that passes without closure escalates to the Steering Committee automatically**, not on someone remembering |
| `UAP-42` | **The count of open conditional acceptances is a published gate metric.** A wave gate passed with fourteen open conditionals is a different position from one passed with two, and only the count makes that visible |

### 10.2 The two things that may never be conditional

| # | Never conditional | Why |
|---|---|---|
| `UAP-43` | **A `P0` requirement** | `CV-04` makes an *untested* `P0` a gate failure; an *un-passed* `P0` is a stronger case. `P0`s are 22.7% of the baseline and 100% of the regulatory exposure |
| `UAP-44` | **Anything in an `RC-A` population** (`QA-001` §5.4) — statutory outputs, financial and tax paths, denied access cells, class `H` hard rules, residency-classified fields, offline conflict paths, custody and destruction chains | Their failure mode is unlawful or irreversible. `MTS-R9` prohibits truncating them, and a conditional acceptance is a truncation with a date on it |

---

## 11. The Payroll Parallel Run

`TS-010` requires it and `G5-01` states the criterion: *"First payroll run processed, validated and
paid with zero errors."*

> **Payroll is the one process on this programme with no tolerance and no recovery**: a wrong net pay
> is an employment-law matter under the Bangladesh Labour Act, a wrong statutory deduction misstates
> an employee's tax position for the year, and neither is correctable by a later run without the
> employee having already been paid the wrong amount.

| Element | Provision |
|---|---|
| Method | **Two complete parallel cycles** before the first live run. Correctness is *proven against two cycles*, not asserted from a calculation |
| Population | **The real employee population**, because a synthetic population cannot reproduce the edge cases that produce wrong pay |
| Boundary | **Not a test-data extract.** Both calculations run **inside the HR system's own controls**, by HR; **only the variance report leaves that boundary** (`QA-004` `TDM-05`, `TDM-A2`) |
| Acceptance | **Zero variance**, or every variance explained and accepted by the HR Director **and** the CFO |
| Signatories | HR Director and CFO jointly |
| Evidence | `E7` reconciliation + `E4` signature |
| Conditional acceptance | **Not permitted** — `UAP-43`; `G5-01` says *zero errors* |

> **`UAP-45`.** The parallel run is the reason `QA-004` `TDM-A2` (*no employee personal data used for
> testing*) does not block `G5-01`. **The design is what makes both rules hold at once**, and it is
> recorded here so a later reader does not resolve the apparent conflict by weakening `TDM-A2`.

---

## 12. Schedule and Gate Evidence

### 12.1 Windows

Per `QA-002` `LVP-A6`: **6 weeks at W1 and W4, 4 weeks otherwise, ending at T−2** so defects have a
fix window before the gate.

| Wave | Window | Packs | Super-users | Physical dependency | Gate criteria |
|:--:|:--:|---|---:|---|---|
| **W1** | **6 wk** | `TS-006`, `TS-011` | ~26 | **`MTS-D3` branch kit** | `G1-03`, `G1-11` |
| **W2** | 4 wk | `TS-006`, `TS-008` | ~26 | **`MTS-D4` stock**, **`MTS-D5` field** | `G2-01`, `G2-02`, `G2-03`, `G2-06`, `G2-07` |
| **W3** | 4 wk | `TS-008`, `TS-009` | ~20 | — | `G3-01`…`G3-09` |
| **W4** | **6 wk** | `TS-007`, `TS-009`, `TS-011` | ~34 | — | **`G4-10` v1.0 scope complete** |
| **W5** | 4 wk | `TS-010` | ~10 | — | **`G5-01` payroll parallel run** |
| **W6** | 4 wk | `TS-006`, `TS-011` | ~26 | — | `G6-01`, `G6-02`, `G6-03` |
| **W7** | 4 wk | `TS-007`, `TS-011` | ~24 | — | `G7-01`…`G7-04` |
| **W8** | 4 wk | `TS-011` | ~12 | — | `G8-01` |
| **W9** | 4 wk | all | ~50 | — | `G9-04`, `G9-05` |

### 12.2 Gate evidence

| Element | Class |
|---|:--:|
| Signed script sets, per pack per role | **`E4`** |
| Function acceptance, per module business owner | **`E4`** |
| Wave acceptance, Forum chair + Head of QE | `E4` + `E6` |
| Timed-observation records where a criterion requires one — `G1-03`, 20 samples with the **distribution** | **`E3`** |
| Counted records where a criterion requires one — `G2-06` inventory by count | **`E7`** |
| Third-party confirmations — `G3-04` NBR, `G5-02` bank | **`E8`** |
| Conditional-acceptance register, cumulative | `E2` |
| **Not executed / not executable**, named with reasons | `E2` |

---

## 13. Decisions Recorded

| # | Decision | Options considered | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| `QA-009-D-01` | What is signed | (a) the script pack document; (b) **a stated statement, by a named individual** | **(b)** | ISO 9001 §8.6 requires traceability to the person authorising release; a signature on a document is a signature on nothing in particular | §9.1; three statements |
| `QA-009-D-02` | Delegation | (a) permit a delegate; (b) **the named super-user only** | **(b)** | `G1-11` requires *named* super-users, and a delegate did not do the work the script tests | `UAP-02`, `UAP-37` |
| `QA-009-D-03` | External participants | (a) employees role-play all seven external parties; (b) **real parties where engageable, substitution recorded where not** | **(b)** | An employee role-playing a customer knows too much; but recording the substitution keeps the weaker result honest | `UAP-10`…`UAP-13` |
| `QA-009-D-04` | The nine untrainable roles | (a) proceed and discount failures; (b) **course or recorded interim route by T−6, `R14` excluded from the interim option** | **(b)** | An untrained executor measures training. `R14` holds the only `T5` restricted-data access, which makes it a security question | `UAP-17`; `Q-02` |
| `QA-009-D-05` | Physical dependencies | (a) simulate; (b) **resource them, and record a pack as not executable if absent** | **(b)** | `G1-03` needs a print and a timing, `G2-06` needs a count, `G2-02`/`G2-03` need a field. A simulated count is not a count | §6; `UAP-19` |
| `QA-009-D-06` | Payroll parallel run | (a) synthetic employees; (b) **real population inside HR's controls, variance report only** | **(b)** | A synthetic population cannot reproduce the edge cases that produce wrong pay; keeping both calculations inside HR's boundary preserves `TDM-A2` | §11; `UAP-45` |
| `QA-009-D-07` | Conditional acceptance limits | (a) any criterion may be conditional; (b) **never `P0`, never `RC-A`** | **(b)** | `CV-04` and `MTS-R9`. A conditional acceptance is a truncation with a date, and `RC-A` populations may not be truncated | `UAP-43`, `UAP-44` |

---

## 14. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| `Q-01` | **Are `MTS-D3`, `MTS-D4` and `MTS-D5` funded as named lines in the wave plan?** | Programme Manager with CFO | **T−6 of `G1`** and **T−6 of `G2`** | `G1-03`, `G2-02`, `G2-03`, `G2-06`, `G2-07` |
| `Q-02` | For the nine roles, is the course registered or the interim route recorded — and is `SP-035` allocated for `R06`? | L&D Lead with Business Process Analysts | **T−6 of each wave** | `UA-03`; `G1-11`; `TS-13`'s `SP-035` question |
| `Q-03` | Who owns duty of care for test personnel working off-site without connectivity? | HSE Lead with Programme Manager | **before W2 field execution** | `MTS-D5`; `QAA-07` |
| `Q-04` | Are 50–74 super-users named and released at 30%, with backfill, for every wave? | Business Owners Forum with line managers | **T−10 / T−6 of each wave** | `EN-04`; the whole level |
| `Q-05` | Can pilot external parties be engaged for `TS-011`, or is substitution recorded? | CCO with Programme Manager | **T−6 of `G1`** | `UAP-10`, `UAP-11`; the strength of the `P01`/`P07` result |
| `Q-06` | Who obtains the `E8` confirmations — NBR for `G3-04`, the bank for `G5-02`? | CFO | **W3 / W5** | `UAP-34`; two gate criteria that cannot be self-evidenced |

---

## 15. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| `AC-01` | UAT is distinguished from the three things it is confused with | §3.2 |
| `AC-02` | Participant coverage is counted against the six packs and their headcounts | §4.2 — **50–74 named individuals** |
| `AC-03` | The training precondition names every role that cannot meet it, with a route | §5.3 — 9 roles, `R14` excluded from the interim option |
| `AC-04` | Every physical execution dependency is specified, owned, dated and tied to its criteria | §6 — 3 dependencies, 5 criteria |
| `AC-05` | An absent dependency produces *not executable*, never *passed* | `UAP-19` |
| `AC-06` | Three signature levels, each with the statement being signed | §9.1 |
| `AC-07` | The sign-off record satisfies ISO 9001:2015 §8.6 traceability | §9.2 |
| `AC-08` | Statutory acceptance is signed by the filing function, with `E8` where a regulator is named | §9.3 |
| `AC-09` | Conditional acceptance has rules, an escalation and two absolute exclusions | §10 |
| `AC-10` | The payroll parallel run preserves `TDM-A2` while evidencing `G5-01` | §11; `UAP-45` |
| `AC-11` | Every wave has a window, packs, participant count and gate criteria | §12.1 — 9 waves |

**Definition of done.** Complete when every criterion is met, W1's super-users are named and
released, `MTS-D3` is present, and the approver has signed. Approval carries the `PGD-A1-09`
qualification.

---

## 16. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | `QA-001` §8, §9 | L7 entry/exit and sign-off authority |
| Upstream | `QA-002` `LP-5` | The window, schedule and staffing |
| Upstream | `QA-004` §7.3, §9 | Frozen `UAT` data and the 38 role accounts |
| Upstream | `TS-006`…`TS-011` | The 352 scripts and the shared UAT method |
| Upstream | `05-04` §1, §7 | Role headcounts and the Approval Authority Matrix |
| Upstream | `GV-009` §6, §9 | Gate window, outcomes, `EN-04` |
| Downstream | `QA-010` | UAT defects and the thresholds that block a gate |
| Downstream | `QA-011` | Requirement coverage evidenced by signed UAT |
| Downstream | `RL-003` | Go-live readiness consumes the wave acceptance record |
| Downstream | `CH-*`, `TR-*` | §5.3's nine roles are a training backlog |
| Lateral | `M23` | The `G5-04` ISO 9001 internal audit runs against §9.2's record |

---

## 17. References

**Within this repository**
`../PGD-000_Master_Register_of_Project_Guiding_Documents.md` · `./_CATEGORY_OVERVIEW.md` ·
`./QA-001_Master_Test_Strategy.md` · `./QA-002_Test_Plans_per_Level.md` ·
`./QA-004_Test_Data_Management_and_Anonymisation_Plan.md` · `./QA-010_Defect_Management_and_Quality_Gate_Standard.md` ·
`./QA-011_Requirements_to_Test_Coverage_Standard_and_Report.md` ·
`../00_Programme_Governance_and_Control/GV-009_Wave_Gate_and_Phase_Exit_Criteria_Handbook.md`

**Workspace**
`../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-04_Role_Permission_and_Access_Matrix.md` §1, §7 ·
`../../1000fix_ERP_Module/06_Delivery_and_Implementation/06-01_Implementation_Roadmap_and_Phasing.md` §4 ·
`../../1000fix_ERP_Module/06_Delivery_and_Implementation/06-02_KPI_Benefits_and_Acceptance_Criteria.md` §4 ·
`../../project_content/13_Test_and_Acceptance_Content/TS-006`…`TS-011`, `TS-015`, `TS-018` ·
`../../project_content/_AUDIT/AUDIT-014_Category_13_TS_Content_Audit.md`

**External — verified 2026-08-18**
ISO/IEC/IEEE 29119-3:2021 §8 · ISO/IEC/IEEE 29148:2018 §5.2.8 · ISO 21502:2020 ·
PRINCE2 7th Edition (2023) · **ISO 9001:2015 §8.6** · Bangladesh Labour Act (payroll, §11)

---

## 18. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-18 | Business Owners Forum with Quality Engineering | Initial issue. Distinguishes UAT from system testing, usability research and training; counts the participant commitment at **50–74 named individuals at 30% per wave** — the programme's largest business commitment, previously stated only in words; names **all nine roles that cannot satisfy `UA-03`**, with a route each and `R14` excluded from the interim option on security grounds; **resources the three physical execution dependencies** with specification, owner, date and blocked criteria, closing `TS-06`'s UAT half; three signature levels each with the **statement** being signed, satisfying **ISO 9001:2015 §8.6** traceability; statutory acceptance signed by the filing function with `E8` where a regulator is named; conditional acceptance with escalation and **two absolute exclusions — `P0` and `RC-A`**; and the payroll parallel-run design that evidences `G5-01` **without breaching `QA-004` `TDM-A2`** | *Pending — `GV-002`* |

---

*`QA-009` · Category 08 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
