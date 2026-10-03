---
id: CM-003
title: Communication Calendar by Wave
project: 1000FiX ERP System v2.0
content_type: Generic
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-20
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Change Lead
author: Change Lead with the Programme Management Office
reviewers: [Programme Manager, CTO, Operations Director, HR Director, Marketing Manager, Localisation Lead, Support Lead, Data Migration Lead, Programme Content Lead]
approver: Programme Content Lead
content_class: E
purpose: >
  Schedules every programme communication across W0–W9 against the delivery milestone it depends
  on, rather than against a date — so that a message never arrives before the thing it announces
  exists, and never arrives after the change it was meant to precede. Communications that arrive
  after the change are damage control rather than change management, and a calendar pinned to
  dates rather than to milestones produces exactly that on the first slip.
traces_to: [06-01, 06-02, CM-001, CM-002, CM-005, CM-006, CM-007, CM-009, CM-012, CM-013, DM-014, OP-002, OP-006, TR-002, TR-024]
priority: P2
wave: W0
bilingual: no
bn_counterpart: n/a
sources:
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-01 §3 — nine waves with months, modules, portals, geography and gate criteria; W1 M1–4, W2 M5–8, W3 M9–13, W4 M14–18, W5 M19–22, W6 M23–26, W7 M27–30, W8 M31–34, W9 M35–36
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-01 §6 — rollout pattern per location, T−4 weeks through T+4 weeks
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-01 §8 — milestone schedule with gate months, and the Month 42 benefits realisation review
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-02 §4 — wave gate acceptance criteria G1-01…G9-05
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-01 §5 — fortnightly sprints, monthly production release within a wave, four weeks hypercare after every wave go-live
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/00_Governance_and_Charter/00-04 §2 ASM-16 — go-live does not fall in Ramadan, Eid-ul-Fitr or Eid-ul-Adha peak periods
    verified: 2026-08-20
    class: P1
  - source: project_content/12_Data_Migration_Content/DM-014 §4.10 — the twelve-message cutover communication schedule this calendar consumes
    verified: 2026-08-20
    class: P1
supersedes: none
review_due: 2027-02-20
---

# CM-003 — Communication Calendar by Wave

> **Scope note.** This file owns **when**, and **what a message is allowed to depend on**. It does
> not own who (`CM-002`), what is said (`CM-001` and the kits), or the cutover freeze schedule
> (`DM-014` §4.10, which this calendar consumes rather than restates — `CP-01`).
>
> **Anchor note.** Every month figure in this file is taken from **`06-01` §3 and `06-02` §4**.
> The Master Index §1 *"Distribution by wave"* table carries a different set of month ranges; the
> divergence is recorded as `O-01` and is not resolved here.

---

## 1. Purpose

The register's justification is exact: *"Communications that arrive after the change are damage
control, not change management."*

A change communication has one property that distinguishes it from every other kind: **it is only
useful before the thing it describes happens.** A go-live announcement issued the day after
go-live is not a late announcement; it is a different, worse document — an apology.

**Consequence of absence (`CP-03`).**

| Failure | Consequence |
|---|---|
| No calendar | Communication is produced when someone remembers, which is after the milestone |
| A calendar pinned to dates | The first four-week slip makes every subsequent message wrong, and nobody knows which |
| No milestone dependency stated | A wave launch kit is issued for a wave whose gate has not passed |
| No lead time per audience | A Bengali translation is commissioned the week the message goes out |
| No quiet-period rule | Staff receive four programme communications in one week and none for the next two months |
| Cutover messages scheduled separately from wave messages | `DM-014`'s twelve-message freeze sequence collides with the wave launch kit |
| No calendar for W0 | The programme's first communication is the announcement that it has already started |

---

## 2. Scope

**In scope:** the wave and gate anchors; the standing cadence; the per-wave communication set with
its milestone dependency, lead time and owner; the per-location rollout communication pattern; the
translation lead time; the quiet-period and collision rules; the Islamic-calendar constraint; the
slip protocol; and rules `CA-01`…`CA-17`.

**Out of scope:**

| Subject | Owned by |
|---|---|
| Who receives each message | [`CM-002_Stakeholder_Map_and_Communication_Plan.md`](CM-002_Stakeholder_Map_and_Communication_Plan.md) |
| What each message says | [`CM-001_Programme_Narrative_and_Change_Story.md`](CM-001_Programme_Narrative_and_Change_Story.md) and the kits `CM-005`…`CM-017` |
| Freeze windows, last-transaction rules and the twelve cutover messages | [`../12_Data_Migration_Content/DM-014_Cutover_Data_Checklist_and_Freeze_Communication.md`](../12_Data_Migration_Content/DM-014_Cutover_Data_Checklist_and_Freeze_Communication.md) §4.10 |
| Training delivery scheduling | `TR-002` §curriculum calendar |
| Release note cadence | [`../17_Operations_Support_and_Runbooks/OP-006_Release_Notes_Standard_and_Wave_Note_Set.md`](../17_Operations_Support_and_Runbooks/OP-006_Release_Notes_Standard_and_Wave_Note_Set.md) |
| Hypercare duration and exit criteria | [`../17_Operations_Support_and_Runbooks/OP-002_Hypercare_Plan_and_Exit_Criteria.md`](../17_Operations_Support_and_Runbooks/OP-002_Hypercare_Plan_and_Exit_Criteria.md) §4.3, §4.8 |
| Notification and transactional message timing | Category 04 `NT` |
| The delivery plan itself | `06-01` — this calendar depends on it and never amends it |

---

## 3. Audience

| Audience | Uses this file to… |
|---|---|
| **Change Lead** | Run the year; commission translation with lead time |
| **PMO** | See which communications are blocked by which milestone |
| **Localisation Lead** | Plan translation capacity against a known forward load |
| **Branch managers and champions** | Know what is coming to their site and when |
| **Data Migration Lead** | Confirm the cutover sequence in `DM-014` is scheduled, not assumed |
| **Marketing** | Know when customer-facing communication is permitted |
| **Support Lead** | Anticipate hotline volume against announcement dates |

---

## 4. Content

### 4.1 The anchors

**`CA-01`: every scheduled item is anchored to a milestone, expressed as an offset from it.**
Nothing in this calendar is expressed as an absolute date.

| Wave | Months (`06-01` §3) | Gate | Gate month (`06-01` §8) | Geography |
|:--:|---|:--:|:--:|---|
| **W0** | 0 (mobilisation) | Charter approved | 0 | HQ |
| **W1** | 1–4 | **G1** | **4** | Dhaka HQ + 5 pilot centres |
| **W2** | 5–8 | **G2** | **8** | All Dhaka centres (~20) |
| **W3** | 9–13 | **G3** | **13** | All Dhaka + Chittagong |
| **W4** | 14–18 | **G4 — v1.0 complete** | **18** | All active service centres |
| **W5** | 19–22 | **G5** | **22** | **All 51+ centres** |
| **W6** | 23–26 | **G6** | **26** | Per module |
| **W7** | 27–30 | **G7** | **30** | Marketplace, national |
| **W8** | 31–34 | **G8** | **34** | National |
| **W9** | 35–36 | **G9 — closure** | **36** | Multi-entity |
| — | 42 | Post-implementation review | 42 | Board |

> **`CA-02` — the gate month is the anchor, not the wave month.** A wave that runs long moves its
> gate; every communication offset from that gate moves with it automatically. This is the single
> property that makes the calendar survive a slip.

### 4.2 Standing cadence — independent of wave

**`CA-03`: these items run whether or not there is news.** They are the baseline against which
silence becomes visible.

| Item | Frequency | Audience (`CM-002`) | Owner | Owning content |
|---|---|---|---|---|
| Programme newsletter | **Monthly, unconditional** | `S17` wider workforce | Change Lead | [`CM-009`](CM-009_Internal_Newsletter_and_Update_Template.md) |
| Champion forum | **Monthly** | `S06` | Change Lead | [`CM-008`](CM-008_Champion_and_Super_User_Network_Kit.md) |
| Steering pack | **Monthly**, 5 working days before the meeting | `S02` | Programme Office | [`CM-004`](CM-004_Executive_Briefing_and_Steering_Pack_Template.md) |
| Business Owners Forum brief | Fortnightly | `S03` | PMO | — |
| Branch manager briefing | Monthly; weekly in their wave | `S05` | Operations Director | [`CM-010`](CM-010_Town_Hall_and_Roadshow_Content.md) |
| Board pack extract | Quarterly | `S01` | CEO | `CM-004` extract |
| Adoption report | **Monthly during rollout** (`00-04` §5.5) | `S02` | Change Lead | [`CM-016`](CM-016_Adoption_Campaign_Content.md) |
| All-staff town hall | **Quarterly**, plus one per wave gate | All internal | CEO / Change Lead | `CM-010` |

### 4.3 The per-wave communication set

**`CA-04`: every wave receives the same eight-message set.** Nine improvised sequences is the
failure `CM-005` exists to prevent; this calendar is where the repetition is scheduled.

| # | Message | Anchor | Lead time | Blocking dependency | Owner | Owning content |
|:--:|---|---|---|---|---|---|
| **M1** | Wave scope announcement | Gate−1 passed + 2 weeks | — | Prior gate passed | Change Lead | `CM-005` |
| **M2** | Impacted-role notice | Wave start + 2 weeks | — | `CM-018` statements drafted for the roles in scope | Change Lead | `CM-018` |
| **M3** | Site readiness notice | **T−4 weeks** per location | 3 weeks | Site readiness assessment scheduled (`06-01` §6) | Operations | `CM-012` |
| **M4** | Training invitation | **T−2 weeks** (champion), **T−1 week** (all staff) | 3 weeks | Course pack approved; training environment loaded | L&D | `TR-002` |
| **M5** | **Cutover freeze sequence — twelve messages** | **T−21 days → P4** | **4 weeks** | Freeze instant confirmed (`DM-014` `CV-06`) | Data Migration + Change | **`DM-014` §4.10**, delivered through `CM-012` |
| **M6** | Go-live announcement | **T−0**, released on the go decision (`DM-014` `C7`) | 3 weeks | **Gate passed; go decision taken** | Change + Marketing | `CM-006` |
| **M7** | Hypercare guidance | **T−0 and T+1 day** | 2 weeks | Support routes confirmed (`OP-001`) | Change + Support | `CM-007` |
| **M8** | Adoption and benefits statement | **Gate + 4 weeks**, after hypercare exit | 2 weeks | **Gate criterion measured** (`NR-08`) | Change Lead | `CM-016` |

> **`CA-05` — M6 is released by the go decision, never by the calendar.** `DM-014` `C7` is held by
> the CTO with the Programme Director and is not delegable. A go-live announcement pre-scheduled to
> send at 09:00 on a Monday will send on a Monday when the go decision was *no*.

> **`CA-06` — M8 cannot be issued before its gate criterion is measured.** `NR-08` binds the claim;
> this rule binds the date. Together they mean an adoption statement is written after the
> measurement exists, not drafted alongside it.

### 4.4 Per-location rollout pattern

`06-01` §6 defines the pattern per location. The communication obligations attached to it:

| Offset | Delivery activity (`06-01` §6) | Communication | Language | Confirmation required |
|---|---|---|---|:--:|
| **T−4 weeks** | Site readiness assessment | M3 readiness notice to branch manager | EN + BN | **Yes** — `CM-012` |
| **T−3 weeks** | Data preparation with the branch | Data owner instruction; legacy hygiene notice | EN + BN | Yes |
| **T−2 weeks** | Branch champion training | M4 champion invitation; champion briefing pack | EN + BN | Yes |
| **T−1 week** | All-staff training in Bengali; access provisioned | M4 all-staff invitation; access notice | **BN-first** | Yes — attendance |
| **T−3 days** | Data cutover; parallel run begins | `DM-014` T−3 readiness confirmation (`C2`) | **BN-first** | **Yes** |
| **T−0** | Go-live with on-site support | M6 + M7 | **BN-first** | Yes — start acknowledgement |
| **T+2 weeks** | Parallel run ends; legacy withdrawn | Parallel-run exit notice; legacy withdrawal confirmation | EN + BN | **Yes** — `DM-014` `C9` |
| **T+4 weeks** | Hypercare ends; adoption review | Hypercare exit notice; M8 | EN + BN | No |

> **`CA-07` — four of the eight require a reply.** `DM-014` `CV-21` establishes the same rule for
> the cutover set: a communication with no confirmation is not a communication. Readiness,
> stop-confirmation, start-acknowledgement and legacy-withdrawal are replies, not broadcasts.

### 4.5 Translation lead time

**`CA-08`: the Bengali version is commissioned when the English is drafted, not when it is
approved.**

| Content size | Translation | In-context review (`BN-018`) | Total lead time |
|---|---|---|---|
| Short notice (< 250 words) | 1 working day | 1 working day | **3 working days** |
| Standard message or kit item | 2–3 working days | 2 working days | **1 week** |
| Full kit, roadshow deck, transition pack | 5 working days | **5 working days after English approval** (`CG-007` §3.4) | **3 weeks** |
| Video or recorded audio | Script 1 week + recording | Re-record on any change | **4 weeks** |

> **`CA-09` — no Bengali-first communication is scheduled with less than its stated lead time.**
> The calendar is the enforcement point. A message scheduled with two days' notice to a Bengali-first
> audience will be sent in English, which `SK-08` says does not count as having communicated.

### 4.6 Quiet periods and collisions

| # | Rule |
|---|---|
| **`CA-10`** | **No more than two programme communications reach the same audience in one week**, excluding transactional notifications and the cutover sequence |
| **`CA-11`** | **The cutover sequence overrides everything.** From T−21 days to the go decision, no non-cutover programme communication is sent to the affected sites |
| **`CA-12`** | **No go-live falls in Ramadan, Eid-ul-Fitr or Eid-ul-Adha peak periods** (`ASM-16`); consequently no wave launch or transition communication is scheduled into those windows either |
| **`CA-13`** | **Month-end (last 3 and first 5 working days) is a quiet period for finance audiences** (`S11`) except for cutover messages |
| **`CA-14`** | **Payroll week is a quiet period for all staff audiences** on any topic touching pay, incentives or recognition (`CM-017`) |
| **`CA-15`** | Two waves running concurrently do not produce two full communication sets to the same audience; the sets are merged and the merge is recorded |

### 4.7 W0 — the mobilisation calendar

The one wave with no gate behind it. `CA-16`: **W0 communication precedes W1 build, not W1
go-live.**

| Offset | Item | Audience | Blocking dependency | Owning content |
|---|---|---|---|---|
| **Kickoff −4 weeks** | Steering approval of the narrative and claim schedule | `S02` | `CM-001` approved | `CM-004` |
| **Kickoff −2 weeks** | Branch manager and champion pre-brief | `S05`, `S06` | Champion selection complete | `CM-008` |
| **Kickoff** | **All-staff town hall — the programme's first communication** | All internal | **Charter approved (`D-01`)** | `CM-010` |
| Kickoff + 1 week | Manager cascade to every branch | `S07`–`S10` | Town hall delivered; BN pack ready | `CM-010` |
| Kickoff + 2 weeks | First monthly newsletter | `S17` | — | `CM-009` |
| Kickoff + 2 weeks | Objection capture opens | All | `CM-011` published | `CM-011` |
| Kickoff + 4 weeks | Per-role change impact statements issued for W1 roles | W1 roles | `CM-018` approved | `CM-018` |
| Monthly from kickoff | Steering pack | `S02` | — | `CM-004` |

> **`CA-17` — the first communication cannot precede charter approval.** `00-02` is
> `DRAFT FOR APPROVAL` and `D-01` is open. Announcing a programme the Board has not approved is
> the single most expensive communication error available at W0. Recorded as `O-02`.

### 4.8 Wave-by-wave summary

Derived from `06-01` §3. Each wave runs the M1–M8 set; this table records what is *distinctive*
about each and which external audiences enter.

| Wave | Distinctive communication load | External audiences entering | Peak translation demand |
|:--:|---|---|---|
| **W1** | First everything. Pilot sites only, but the whole workforce is watching | None | Moderate — 6 sites |
| **W2** | **The heaviest wave.** Technician app (`RSK-008`), customer portal launch, 20 Dhaka sites, van stock recall | **Customers** (`CM-013`) | **Highest — BN-first to 200–400 technicians and 250,000+ customers** |
| **W3** | Finance controls, month-end alignment, vendor route change | **Vendors, couriers** (`CM-015`) | Moderate |
| **W4** | **v1.0 complete.** Corporate, brand, contact centre; the milestone the Board tracks | **Corporate clients, brand partners** (`CM-014`) | High |
| **W5** | **All 51+ centres.** Payroll — the least forgiving communication in the programme | None | High — national |
| **W6** | New business lines; native apps | None | Low |
| **W7** | **Marketplace.** 500–2,000 sellers, external, low switching cost (`RSK-010`) | **Sellers, referral partners** (`CM-015`) | High — seller-facing |
| **W8** | Intelligence, e-waste; management reporting withdrawal of manual packs (`RSK-012`) | Recycling partners | Low |
| **W9** | **Closure.** Handover, support transition, benefits baseline | None | Low |
| **M42** | Post-implementation benefits review to the Board | None | None |

### 4.9 Slip protocol

**`CA-18` (recorded as a rule below): a slip re-anchors the calendar; it does not delete
communication.**

| Slip size (`00-04` §9) | Communication response |
|---|---|
| ≤ 4 weeks, absorbed in buffer | Offsets recalculate automatically from the gate. **One notice to `S05`, `S06` and `S17`** stating the new gate month |
| > 4 weeks, Steering decision pending | **A holding communication within 5 working days**, stating that a decision is being taken and when it will be known. Silence during a visible slip is how `RSK-003` fatigue starts |
| Descope decision taken | `CM-005` M1 re-issued for the revised scope; `CM-018` statements re-issued for affected roles |
| Wave gate fails | **No M6, no M8.** M7 hypercare guidance is replaced by a continuation notice |
| Cutover fallback triggered (`DM-014` T1–T7) | `DM-014` `CV-16`–`CV-18` govern; the communication is a fallback notice, and the post-mortem within five working days is announced with it |

### 4.10 Audience · channel · timing · message · call-to-action

The category-standard table (`CG-009` §3), expressed here as the **scheduling contract**.

| Audience | Channel | Timing (anchor) | Message | Call to action |
|---|---|---|---|---|
| All internal | Town hall | W0 kickoff; each gate + 1 week | Narrative; wave result | Attend |
| `S17` | Newsletter | Monthly, unconditional | Position update | None |
| `S06` champions | Forum | Monthly | Everything, first | Cascade in 5 working days |
| `S05` branch managers | Briefing | T−4 weeks per site | Readiness | **Confirm readiness** |
| Branch staff | Huddle + BN pack | T−1 week | Training and access | Attend training |
| All affected staff | BN notice + SMS | **T−7 days, T−1 day, freeze instant** | Freeze instant and last-transaction rule | **Confirm your last transaction number** |
| All affected staff | BN notice | **On go decision** | Start now; support routes | **Acknowledge** |
| Customers | SMS, portal, hotline | W2, T−7 days and go + 1 day | Transition, reference continuity | Register |
| Corporate clients | Account manager | Per account, pre-W4 | Transition | Book the session |
| Vendors, sellers | Relationship owner + portal | Per cohort, pre-wave | Route change | Register on the portal |
| `S02` Steering | Pack | Monthly, −5 working days | Status, decisions, claims | Approve the claims |

### 4.11 Governing rules

| # | Rule | Class |
|---|---|:--:|
| `CA-01` | Every item is anchored to a milestone and expressed as an offset, never as an absolute date | **H** |
| `CA-02` | The gate month is the anchor; a moved gate moves its communications automatically | **H** |
| `CA-03` | Standing cadence items run whether or not there is news | **H** |
| `CA-04` | Every wave runs the same eight-message set | **H** |
| `CA-05` | The go-live announcement is released by the go decision, never pre-scheduled | **H** |
| `CA-06` | The adoption statement is issued only after its gate criterion is measured | **H** |
| `CA-07` | Four of the eight per-location communications require a reply | **H** |
| `CA-08` | Bengali is commissioned at English draft, not at English approval | **H** |
| `CA-09` | No Bengali-first communication is scheduled inside its stated lead time | **H** |
| `CA-10` | No more than two programme communications per audience per week | **S** |
| `CA-11` | The cutover sequence overrides all non-cutover communication to affected sites | **H** |
| `CA-12` | No go-live or launch communication in Ramadan or Eid peak periods (`ASM-16`) | **H** |
| `CA-13` | Month-end is a quiet period for finance audiences | **S** |
| `CA-14` | Payroll week is a quiet period for pay, incentive and recognition topics | **H** |
| `CA-15` | Concurrent waves merge their communication sets; the merge is recorded | **H** |
| `CA-16` | W0 communication precedes W1 build, and follows charter approval | **H** |
| `CA-17` | No programme communication precedes `D-01` charter approval | **H** |
| `CA-18` | A slip re-anchors the calendar; a visible slip requires a holding communication within 5 working days | **H** |

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| `06-01` §3, §6, §8 | Waves, months, rollout pattern, milestones — every anchor in §4.1 and §4.4 |
| `06-02` §4 | Gate criteria; `CA-06` will not release M8 without a measured one |
| [`CM-002_Stakeholder_Map_and_Communication_Plan.md`](CM-002_Stakeholder_Map_and_Communication_Plan.md) | The audiences each scheduled item reaches (`SK-18` reconciles both ways) |
| [`../12_Data_Migration_Content/DM-014_Cutover_Data_Checklist_and_Freeze_Communication.md`](../12_Data_Migration_Content/DM-014_Cutover_Data_Checklist_and_Freeze_Communication.md) §4.10 | M5 — the twelve cutover messages and their confirmation obligations |
| `CG-007` §3.4 | The G4 linguistic service level that sets the lead times in §4.5 |
| `ASM-16` | The Islamic-calendar constraint in `CA-12` |
| `00-04` §9 | The slip categories `CA-18` responds to |
| [`../17_Operations_Support_and_Runbooks/OP-002_Hypercare_Plan_and_Exit_Criteria.md`](../17_Operations_Support_and_Runbooks/OP-002_Hypercare_Plan_and_Exit_Criteria.md) · [`../17_Operations_Support_and_Runbooks/OP-006_Release_Notes_Standard_and_Wave_Note_Set.md`](../17_Operations_Support_and_Runbooks/OP-006_Release_Notes_Standard_and_Wave_Note_Set.md) | Hypercare duration and exit; release-note cadence — **both set durations this calendar must anchor to** (`O-04`) |
| **`06-05`** | **Does not exist** — the change plan this calendar should implement |

| Depended on by |
|---|
| `CM-005` kit issue dates · `CM-006` release trigger · `CM-009` newsletter cadence · `CM-012` readiness deadlines · `CM-013` customer transition timing · `CM-016` campaign windows · Localisation capacity planning (`BN-001`) |

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | **At every wave gate**, and on any change to `06-01` §3 |
| Trigger for out-of-cycle review | A gate slip · a descope · a cutover fallback · a change to the Islamic calendar dates for the year · a new external audience |
| Owner | Change Lead, with the PMO holding the milestone data |
| Change log | `RF-006`; anchor changes are MAJOR (`CG-006`) |
| Enforcement | `CA-01`…`CA-18`; monthly reconciliation against `CM-002` under `SK-18` |
| Improvement loop | Each wave's post-gate review records which messages arrived late and why; lead times in §4.5 are corrected from actuals, not from estimates |

---

## 7. Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **`O-01`** | **The repository states two different wave calendars.** `06-01` §3 and §8, and `06-02` §4, agree: W1 M1–4 gating at M4, through W9 M35–36 gating at M36. The **Master Index §1 "Distribution by wave" table** states W1 3–8, W2 8–14, W3 14–18, W4 18–23, W5 23–27, W6 27–30, W7 30–33, W8–W9 33–36 — a different set, overlapping at the boundaries. This file anchors to `06-01`/`06-02` because they are the delivery source and they agree with each other, but **a content calendar and a delivery plan running on different month numbers is exactly the defect this file exists to prevent**. **The divergence is already live in authored content:** `OP-002` §4.3 tabulates hypercare duration against *"Months (`06-01`)"* and then lists W1 as **3–8** — the Master Index figures, cited to `06-01`, which says 1–4. Two `Draft` content files in two categories now anchor to two different calendars | Programme Content Lead with the PMO | **W0 — before the first anchored communication** |
| **`O-02`** | **The programme cannot announce itself.** `CA-17` blocks all communication before `D-01` charter approval; `00-02` remains `DRAFT FOR APPROVAL` and `D-01`, `D-13` and `D-14` are open. The W0 calendar in §4.7 has no start date | CEO with the Board | **W0** |
| **`O-03`** | **No wave has a calendar date.** Every offset in this file is relative because no absolute programme start date exists in the repository. The Islamic-calendar constraint (`CA-12`) and the payroll and month-end quiet periods (`CA-13`, `CA-14`) cannot be applied to relative offsets — they need real dates to collide with | Programme Manager | **W0 — with `D-01`** |
| **`O-04`** | **The M7 and M8 anchors are wrong.** §4.4 ends the per-location pattern at `T+4 weeks` from `06-01` §6; **`OP-002` §4.3 sets hypercare at 4–8 weeks per wave as a minimum**, 8 weeks for W1, W3 and W5. `OP-006` sets its own release-note cadence. Three of the eight per-wave messages — M7 hypercare, M8 adoption, and the parallel-run reminder — are anchored to a window shorter than the one that will actually run. **`CA-02` says a moved gate moves its communications; it does not help when the anchor itself is wrong** | Change Lead with the Support Lead | **W1 minus 6 weeks** |
| **`O-05`** | **Translation capacity is not planned against this forward load.** §4.5 states lead times; §4.8 shows W2, W4, W5 and W7 as high-demand. No localisation capacity plan exists against a communication calendar, and `CA-09` blocks scheduling inside the lead time — so a capacity shortfall becomes a communication that does not go out | Localisation Lead with Change Lead | **W1** |
| **`O-06`** | **There is no scheduling system.** A milestone-anchored calendar with 27 audiences, nine waves, 51+ sites and a four-week translation lead is not maintainable in a document. `M27` omnichannel is W4; the calendar is W0 | Change Lead with PMO | **W0** |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Content_File_Front_Matter.md`; §7 Open Items added per category convention
- [x] Category-standard audience · channel · timing · message · call-to-action table present (`CG-009` §3)
- [x] **Every item anchored to a milestone rather than a date**, so a slip re-anchors automatically
- [x] Anchors taken from `06-01` §3/§8 and `06-02` §4, with the Master Index divergence recorded rather than silently reconciled
- [x] Standing cadence separated from wave-driven communication
- [x] Eight-message per-wave set defined once and reused across nine waves
- [x] Per-location pattern mapped onto `06-01` §6, with the four reply-requiring messages identified
- [x] **Cutover messages consumed from `DM-014` §4.10, not restated** (`CP-01`)
- [x] Translation lead times stated and made blocking
- [x] Quiet periods, Islamic-calendar constraint and collision rules defined
- [x] Slip protocol covers absorb, decide, descope, gate failure and fallback
- [x] Eighteen governing rules with enforcement classes
- [x] All internal links resolve
- [x] Bengali counterpart — n/a for this file, `bilingual: no` per `CG-010` §3.2 (PMO planning instrument); the **messages it schedules** carry the Bengali obligation through `CA-08` and `CA-09`
- [ ] **`O-01` two wave calendars in the repository — unresolved**
- [ ] **`O-02` no charter approval, so no start**
- [ ] **`O-03` no absolute dates, so the calendar constraints cannot yet be applied**
- [ ] **`O-04` M7 and M8 anchored to a four-week hypercare window that `OP-002` §4.3 doubles for three waves**
- [ ] **`O-05` translation capacity unplanned against this load**
- [ ] Named approver recorded — **pending Programme Content Lead**
- [x] Registered in the Content Master Index (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
