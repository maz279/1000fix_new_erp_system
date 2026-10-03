---
id: TS-015
title: Offline and Field Condition Test Scripts
project: 1000FiX ERP System v2.0
content_type: Test script
template: TPL_Test_Script.md
template_version: 1.0
version: 1.0
date: 2026-08-19
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: QA Lead with Mobile Engineering
author: QA Lead with Flutter engineering, Technical Services and Localisation
reviewers: [CTO, Solution Architect, Mobile lead, Technical Director, Operations Director, Logistics Manager, Quality Manager, Localisation Lead]
approver: CTO with QA Lead
content_class: E
purpose: >
  The field tests for the three offline-capable applications — technician, rider and field auditor —
  covering twenty-four-hour offline operation, sync, conflict resolution, degraded 3G, battery
  consumption and low-end devices. Every one of these targets is a field condition, and every one of
  them passes in an office: a lab test with aeroplane mode toggled for ten minutes does not reproduce
  a technician in Gazipur whose signal came and went four times across a nine-hour shift while the
  dispatcher reassigned the job he was already working on. The non-negotiable requirement is zero
  data loss, and the only place that can be proven is the field.
traces_to: [P02, P09, P11, M01, M02, M03, M15, M23, M28, M61, 05-06 §1, 05-06 §2, 05-06 §5, 05-06 §8, 05-06 §10, 05-06 §11, 05-06 §12, 06-02 §4, UI-009, UI-012, UI-019, UI-021, HC-004, HC-011, HC-013, TS-001, TS-002, TS-006, TS-008, TS-013, TS-014, TS-018]
priority: P0
wave: W2
bilingual: yes
bn_counterpart: TS-015_Offline_and_Field_Condition_Test_Scripts_BN.md
sources:
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00_Portal_Suite_Overview.md P02 Non-Negotiable Requirements 1–7 — full operation offline for 24 hours with no data loss; sync within 30 seconds of reconnection with 100% data integrity; complete Bengali interface including error messages; acceptable on a mid-range Android 11 device with 3 GB RAM; battery under 12% per 8-hour shift excluding navigation; every state-changing action queued locally and idempotent on the server; no feature requiring a connection a technician cannot complete offline. PS-08 offline-capable with queued sync for P02, P09, P11
    verified: 2026-08-19
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06_NonFunctional_Requirements_and_Standards.md NFR-036 technician app job list on 3G ≤ 8 s cold and ≤ 2 s warm (field test); NFR-037 offline sync completion after 24 h offline ≤ 30 s on 3G (field test); NFR-047 technician app functional without connectivity for 24 hours; NFR-082 battery ≤ 12% per 8-hour shift excluding navigation; NFR-017 Android 11+ with 3 GB RAM on intermittent 4G; NFR-020 low-bandwidth mode; §8 DI-04 offline sync guarantees zero data loss and zero double-application; §12 AS-13 offline apps use append-only journals with server-authoritative resolution; §11 Offline level — 24-hour offline operation with a scripted conflict scenario set, before each mobile release
    verified: 2026-08-19
    class: P1
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-02_KPI_Benefits_and_Acceptance_Criteria.md §4 Gate 2 G2-02 24-hour offline operation demonstrated with zero data loss, G2-03 sync completing within 30 seconds on 3G after 24 hours offline; §2.2 KPI-016 technician app daily active usage, KPI-017 offline sync failures zero
    verified: 2026-08-19
    class: P1
  - source: project_content/03_UI_Copy_and_Microcopy/03A_Cross_Cutting/UI-009_Offline_Sync_and_Conflict_Resolution_Copy.md — the copy this pack verifies in situ; its own traces_to names TS-015 as its verification
    verified: 2026-08-19
    class: P1
supersedes: none
review_due: 2027-02-19
---

# Offline and Field Condition Test Scripts

| Item | Value |
|---|---|
| Test level | **Offline** — `05-06` §11 level 12; before **every** mobile release |
| Roles executing | `R10` `R11` `R12` technicians · `R16` riders · `R32` auditors — **in the field** |
| Modules covered | `M01` `M02` `M03` `M15` `M23`, with `M28` and `M61` as sync and content mechanisms |
| Portals covered | **`P02`** `P09` `P11` — the three `PS-08` offline surfaces |
| Environment | **Real locations, real networks, real devices.** Not a lab |
| Test data set | `TS-002` — personas 2, 8, 10; offline packs pre-staged |
| Wave | W2 · `P0` — `G2-02` and `G2-03` |

> **Template conformance.** `TPL_Test_Script.md` at pack level. All six sections retained in order;
> §2 carries a field-logistics subsection that no other pack needs, and it is the addition.

---

## 1. Traceability

### 1.1 What "field test" means, and why `05-06` says it twice

`05-06` §1 gives the measurement method for each performance target. **Two of them say "Field
test"** where every other row says synthetic monitoring, gateway metrics, load test or
instrumentation: `NFR-036` (job list on 3G) and `NFR-037` (sync after 24 hours offline). That is a
deliberate instruction in the specification, and it is the basis of this pack.

| Lab test proves | Field test proves |
|---|---|
| The app functions with the network interface disabled | The app functions where the signal is **weak but present** — the condition that breaks sync logic, because requests start and do not finish |
| Sync completes when reconnection is clean | Sync completes when reconnection happens four times across a shift, mid-request |
| Battery drain over an hour of scripted use | Battery drain over a **nine-hour shift** with GPS, camera, navigation and screen-on time as they actually occur |
| The job list loads on a throttled connection | The job list loads on a Gazipur 3G cell at 18:00 |
| Conflict resolution when two edits are seconds apart | Conflict resolution when a dispatcher reassigned the job **six hours ago** and the technician has been working on it since |

**The last row is the one that matters most.** `AS-13` requires append-only journals with
server-authoritative resolution, and the interesting case is not a race but a **long divergence**:
hours of local work against a server state that moved. `UI-009` writes the copy for that moment;
this pack is where the copy is read by a technician who is actually in it.

### 1.2 The seven non-negotiables, mapped

`04-00` `P02` states seven non-negotiable requirements. Every one has scripts here.

| # | `P02` non-negotiable | Target | Scripts |
|---:|---|---|---|
| 1 | Full operation offline for **24 hours** with **no data loss** | `NFR-047`, `DI-04` | `OFF-001`…`OFF-006` |
| 2 | Sync within **30 seconds** of reconnection, 100% data integrity | `NFR-037` | `OFF-007`…`OFF-011` |
| 3 | **Bengali interface, complete — including error messages** | `NFR-016`, `PS-03`, `PS-09` | `OFF-030`…`OFF-033` |
| 4 | Runs acceptably on a **mid-range Android 11, 3 GB RAM** | `NFR-017` | `OFF-024`…`OFF-027` |
| 5 | Battery **under 12% per 8-hour shift** excluding navigation | `NFR-082` | `OFF-028`, `OFF-029` |
| 6 | Every state-changing action **queued locally and idempotent** on the server | `DI-04`, `AS-13`, `DI-05` | `OFF-012`…`OFF-018` |
| 7 | **No feature requires a connection** a technician cannot complete offline | `PS-08` | `OFF-019`…`OFF-023` |

### 1.3 Traceability obligation per script

| Field | Source |
|---|---|
| Non-negotiable | `04-00` `P02` 1–7, per §1.2 |
| Target | The `NFR-nnn` and its number, verbatim |
| Device class | Make, model, Android version, RAM, battery health — recorded per run (`OF-04`) |
| Location and network | The real place, the operator, the observed signal class, the time of day (`OF-03`) |
| Copy verified | The `UI-009` state or message the script encounters, in both languages |
| Gate | `06-02` §4 |

---

## 2. Preconditions

### 2.1 Rules

| # | Rule |
|---|---|
| **OF-01** | **A field condition is tested in the field.** A lab result is recorded as a lab result and does not satisfy exit for `NFR-036`, `NFR-037`, `NFR-047` or `NFR-082` (`TX-19`; `05-06` §1 "Field test") |
| **OF-02** | **Twenty-four hours means twenty-four hours.** The offline window is continuous and spans a real shift boundary, including an overnight period and a device restart |
| **OF-03** | **Location, operator, observed signal class and time of day are recorded for every run.** A pass at a Dhaka office window is not a pass for the estate |
| **OF-04** | **The device is the audience's device class**, at the specification floor: Android 11, 3 GB RAM, 32 GB storage. A result on a flagship is void (`NFR-017`, `05-06` §10) |
| **OF-05** | **Zero data loss is asserted item by item**, not in aggregate. Every offline action is enumerated before sync and reconciled after; a count that matches is not sufficient if the contents differ (`DI-04`) |
| **OF-06** | **Zero double-application is asserted separately from zero loss.** They are different failures with different causes and `DI-04` names both |
| **OF-07** | **Every conflict scenario is scripted before it is run** (`05-06` §11 requires "a scripted conflict scenario set"), and the **expected resolution** is stated in advance, including what the user is told |
| **OF-08** | **The copy is verified in situ.** `UI-009`'s offline, sync and conflict strings are read on the device in the state they describe, in Bengali, by a Bengali-reading executor |
| **OF-09** | **Interrupted sync is the default case, not an edge case.** Every sync script has a variant in which the connection drops mid-sync |
| **OF-10** | **Battery is measured across a full shift** with the real duty cycle — GPS on, camera used, screen on as it actually is — and navigation is excluded as `NFR-082` specifies, with the exclusion method stated |
| **OF-11** | **Storage exhaustion is tested**, because a 32 GB device holding 24 hours of photographs and an offline knowledge pack will reach it |
| **OF-12** | **Every offline script runs on all three applications where the capability exists.** `PS-08` names `P02`, `P09` and `P11`; a fix in one Flutter app is not a fix in the others unless the code is shared, and that is an assumption to verify |
| **OF-13** | **Field runs are safety-governed.** Testers travel, ride and enter customer premises; `SP-030` applies to them as it applies to technicians |

### 2.2 Field logistics — the part that is usually missing

| # | Requirement | Detail |
|---|---|---|
| L-01 | **Locations** | At least 6: a Dhaka dense-urban site, a Dhaka basement or lift lobby (no signal), a peri-urban site (Gazipur or Savar), a rural upazila site, a moving vehicle on a highway, and a customer premises interior |
| L-02 | **Operators** | All 7 prefixes in `TS-002` §4.5 across at least 3 operators — coverage differs by operator and a single-SIM test finds one operator's failures |
| L-03 | **Devices** | ≥ 3 units at the `NFR-017` floor, ≥ 1 with degraded battery health, ≥ 1 iOS 15 for the secondary platform |
| L-04 | **Duration** | A full shift per run for `OFF-028`/`029`; a 24-hour continuous window for `OFF-001`…`006` |
| L-05 | **Instrumentation** | Battery telemetry, network-condition logging, sync-timing capture, and crash reporting on the device |
| L-06 | **People** | A Bengali-reading executor from the audience — a real technician, rider and auditor — plus one observer |
| L-07 | **Server-side visibility** | Someone with `M28` observability watching the sync as it arrives, correlating by trace id (`NFR-092`) |
| L-08 | **Safety** | `SP-030` briefing, travel arrangements, and a means of contact when the test device is deliberately offline (`OF-13`) |

**Nothing in the programme allocates any of L-01 to L-08.** Recorded as `O-02`.

### 2.3 Preconditions

| # | Precondition | How to establish |
|---|---|---|
| 1 | Mobile release built for the target device class | Build manifest with the Flutter version and the target SDK |
| 2 | `TS-002` data staged on the server **and** the offline pack pre-downloaded | `TD-14`; the pack contents are themselves a variable (`OFF-020`) |
| 3 | `UI-009`, `UI-012`, `UI-019`, `UI-021` copy packs published in both languages | `OF-08` |
| 4 | Server-side conflict resolution configured and observable | `AS-13` |
| 5 | Jobs, manifests and audit checklists assigned to the test executors | `TS-002` `O-04` |
| 6 | `M61` offline knowledge pack available for `OFF-020` | **`M61` offline mechanism is W6** — `O-03` |
| 7 | Field logistics L-01…L-08 arranged | **Not arranged** — `O-02` |
| 8 | Baseline battery measurement on each device before the run | `OF-10` |

---

## 3. Scripts

### 3.1 Block A — Twenty-four hours offline · 6 scripts

| Script | Condition | Expected | Pri |
|---|---|---|:--:|
| `OFF-001` | **Complete a full shift's work with no connectivity for 24 continuous hours**, spanning a shift boundary and an overnight period | Every capability in `04-00` `P02` available; nothing blocked (`NFR-047`, non-negotiable 1) | **P0** |
| `OFF-002` | **Restart the device mid-window**; continue working | No queued work lost; local journal intact (`AS-13`) | **P0** |
| `OFF-003` | Force-close and reopen the app repeatedly during the window | State preserved; no duplicate local records | **P0** |
| `OFF-004` | Work 4 jobs to completion offline, with photos, parts, signature and payment | All four fully recorded locally; `OF-05` enumeration taken | **P0** |
| `OFF-005` | **Fill device storage with photographs and an offline pack** | Clear warning before exhaustion; work not lost; degraded capture explained (`OF-11`) | **P0** |
| `OFF-006` | Battery reaches 10% during the offline window | Queued work protected; the user warned in Bengali | P1 |

### 3.2 Block B — Sync · 5 scripts

| Script | Condition | Expected | Pri |
|---|---|---|:--:|
| `OFF-007` | **Reconnect on 3G after 24 hours offline with a full day's work queued** | **Sync completes in ≤ 30 s**; 100% data integrity (`NFR-037`; `G2-03`) | **P0** |
| `OFF-008` | **Item-by-item reconciliation after `OFF-007`** | Every enumerated offline action present, once (`OF-05`, `OF-06`) | **P0** |
| `OFF-009` | **Connection drops mid-sync, twice** | Resumes; no partial application; no duplicate (`OF-09`, `DI-05`) | **P0** |
| `OFF-010` | Reconnect on a weak-but-present cell where requests start and time out | Sync progresses or fails **visibly**; never appears complete when it is not (`PS-09`) | **P0** |
| `OFF-011` | Two devices sync overlapping work for the same job | Server-authoritative; both users told the outcome (`AS-13`) | P1 |

### 3.3 Block C — Conflict set · 7 scripts

**Scripted in advance with expected resolutions** (`OF-07`). This is the `05-06` §11 "scripted
conflict scenario set".

| Script | Divergence | Expected resolution and message | Pri |
|---|---|---|:--:|
| `OFF-012` | Dispatcher **reassigned the job 6 hours ago**; technician has been working on it offline since | Server wins the assignment; **the technician's work is preserved and attributed**, and they are told clearly what happened (`UI-009`) | **P0** |
| `OFF-013` | Job **cancelled by the customer** while the technician completed it offline | Work preserved; cancellation surfaced; a decision path offered, not a silent discard | **P0** |
| `OFF-014` | Part consumed offline that was **issued to another technician** in the interim | Reconciled per `AUT-014`; the variance flagged, not absorbed | **P0** |
| `OFF-015` | **Estimate approved by the customer online** while the technician revised it offline | Both versions retained; the approved version governs; the technician informed | **P0** |
| `OFF-016` | Payment taken offline for an invoice **already paid online** | One payment recorded; the duplicate detected and refunded or voided with a trail (`BRU-FIN-03`) | **P0** |
| `OFF-017` | **Certification expired** during the offline window; a warranty job was completed after expiry | Flagged on sync; the claim path blocked per `BRU-HRM-01`; the technician told why | P1 |
| `OFF-018` | Offline knowledge pack **stale**; the technician followed a superseded procedure | Staleness was visible offline (`M61` T-03); the completed work flagged for review | P1 |

### 3.4 Block D — No feature requires a connection · 5 scripts

Non-negotiable 7 (`PS-08`).

| Script | Capability attempted offline | Expected | Pri |
|---|---|---|:--:|
| `OFF-019` | **Every `04-00` `P02` capability area in turn**, offline: day, navigation, job execution, parts, evidence, customer, quality, workshop, logistics, remote, communication, knowledge, personal | Each either works offline or is **explicitly declared** as connection-requiring, with the declaration itself under `PS-08` review | **P0** |
| `OFF-020` | Open a repair manual, a wiring diagram and past repair notes offline | Available from the offline pack (`FR-KMS-017`/`-018`) — **`O-03`** | **P0** |
| `OFF-021` | Read the `HC-004` help set offline, mid-job | Available on the device — **`HC-004` `O-01` records that the delivery path does not exist** | P1 |
| `OFF-022` | Complete a `P11` audit checklist with evidence, offline | Full offline execution (`04-00` `P11`) | P1 |
| `OFF-023` | Complete a `P09` manifest, handover and cash record, offline | Full offline execution (`04-00` `P09`) | **P0** |

### 3.5 Block E — Device, network and battery · 6 scripts

| Script | Condition | Target | Pri |
|---|---|---|:--:|
| `OFF-024` | **Job list load on 3G, cold cache** | **≤ 8 s** (`NFR-036`) | **P0** |
| `OFF-025` | **Job list load on 3G, warm cache** | **≤ 2 s** (`NFR-036`) | **P0** |
| `OFF-026` | Full shift on the `NFR-017` device floor: Android 11, 3 GB RAM | Acceptable performance; **crash-free sessions > 99.5%** (`04-00` `P02` KPI) | **P0** |
| `OFF-027` | Low-bandwidth mode on a rural cell | Functional (`NFR-020`) | P1 |
| `OFF-028` | **Battery across an 8-hour shift, navigation excluded** | **≤ 12%** (`NFR-082`) | **P0** |
| `OFF-029` | Battery across a 9-hour shift **including** navigation, reported separately | Recorded as a companion figure, not against `NFR-082` | P1 |

> **`OFF-028` needs its exclusion method stated, not assumed.** `NFR-082` excludes navigation from a
> 12% budget, and navigation is the single largest consumer on the device. Measuring "excluding
> navigation" means either running the shift without navigation — which is not the real duty cycle —
> or attributing consumption per process. **The two methods give different answers**, and no document
> chooses. `O-04`.

### 3.6 Block F — Bengali in the field · 4 scripts

Non-negotiable 3: *Bengali interface, complete — including error messages*.

| Script | Condition | Expected | Pri |
|---|---|---|:--:|
| `OFF-030` | **Every offline, syncing, sync-failed, conflict and queued state read in Bengali on the device**, in the state it describes | `UI-009` strings correct, legible and untruncated at the device's real width (`OF-08`) | **P0** |
| `OFF-031` | **Every error message reachable offline, in Bengali** | Each says what happened and what to do next, in Bengali (`PS-09`, non-negotiable 3) | **P0** |
| `OFF-032` | Bengali voice note recorded offline and synced | Captured, queued, synced, playable | P1 |
| `OFF-033` | Bengali text entry offline with phonetic input | Functional (`NFR-074`); conjuncts render (`TS-002` `B-01`) | P1 |

**Pack total: 33 scripts · 22 at `P0` · 11 at `P1` · 0 at `P2`.**

### 3.7 Negative and edge cases

| # | Condition | Expected behaviour |
|---|---|---|
| N-01 | App reports sync complete while items remain queued | **Critical** — the failure that destroys trust in the app and is invisible to every server-side measure |
| N-02 | Server rejects a synced item as invalid | The technician is told, the item is not silently dropped, and the work is recoverable |
| N-03 | Device clock wrong or timezone changed offline | Server timestamps govern (`AS-11` UTC); local ordering preserved from the journal, not from the clock |
| N-04 | Two offline actions on the same record in the wrong local order | Append-only journal preserves order (`AS-13`) |
| N-05 | Photograph captured offline exceeds the upload size limit | Compressed or queued; **never discarded** — `BRU-SRM-17` makes it claim-critical |
| N-06 | Offline pack updated server-side during the offline window | Applied on sync; the technician told the procedure changed (`OFF-018`) |
| N-07 | User logs out while items are queued | **Prevented, or the queue survives the session** — a logout that discards a shift's work is a `DI-04` failure |
| N-08 | App upgraded with items still queued | Queue migrated; `OPS-07` forward-only with a documented procedure |
| N-09 | Technician uses a paper notebook instead | **Not a system defect but the most important observation in the pack** — record it; `HC-004` names the paper notebook as invisible to every measure the programme has |

---

## 4. Exit Criteria

| Criterion | Threshold |
|---|---|
| `P0` scripts passed | **100% — no tolerance** |
| `P1` scripts passed | ≥ 95% |
| Scripts executed **in the field** where `OF-01` requires it | **100%**; lab results recorded separately and excluded |
| **`G2-02` 24-hour offline** | **Demonstrated with zero data loss**, item-by-item (`OF-05`) |
| **`G2-03` sync after 24 hours offline on 3G** | **≤ 30 seconds** |
| Zero double-application | Asserted separately and met (`OF-06`) |
| Conflict set executed with pre-stated resolutions | **7 of 7** (`OF-07`) |
| Interrupted-sync variants executed | 100% of sync scripts (`OF-09`) |
| `NFR-036` cold and warm on 3G | ≤ 8 s and ≤ 2 s |
| **`NFR-082` battery** | **≤ 12% per 8-hour shift, navigation excluded by a stated method** |
| Device class at the `NFR-017` floor | 100% (`OF-04`) |
| Locations and operators covered | **≥ 6 locations, ≥ 3 operators** (L-01, L-02) |
| Bengali verification of every offline state and error | **100%** (`OF-08`) |
| Crash-free sessions | > 99.5% |
| All three applications covered where the capability exists | `P02`, `P09`, `P11` (`OF-12`) |
| **`KPI-017` offline sync failures** | **Zero** |
| Open Critical defects | Zero |

---

## 5. Defects Raised

| Defect ID | Script | Severity (`TS-018`) | Status |
|---|---|---|---|
| *(populated at execution)* | | | |

**Three automatic escalations, and a non-deferral:**

| Trigger | Escalation |
|---|---|
| **Any data loss, at any volume** | **Critical** to CTO; **not deferrable**. `DI-04` and `04-00` `P02` non-negotiable 1 admit no tolerance, and a technician who loses one job's work stops trusting the app permanently |
| **Any double-application** | **Critical** to CTO. A duplicate part issue or a duplicate payment has a financial consequence and a customer consequence |
| **Sync reported complete while items remain queued** (`N-01`) | **Critical** to CTO. It is worse than a visible failure because no server-side measure detects it |

---

## 6. Sign-off

| Role | Executor | Location and network | Device | Release | Date | Signature |
|---|---|---|---|---|---|---|
| `R10` Senior Technician | | | | | | |
| `R11` Junior Technician | | | | | | |
| `R16` Rider | | | | | | |
| `R32` Field Auditor | | | | | | |
| **Mobile lead** — device and battery results | | | | | | |
| **Pack acceptance** — CTO with Technical Director | | | | | | |

> Location, network and device are **sign-off fields, not annotations** (`OF-03`, `OF-04`). A
> signature without them does not identify what was tested.

---

## Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **`P02` and the `P09` capability both go live at W2 and W3, and this pack is `P0`/W2 — which is correct.** But `TS-013` requires an offline canary in the `P02` and `P09` smoke checklists from the first production deployment, and `TS-013` is W2 while `P03` deploys from W1. **This pack's timing is right; its consumers' is not** — recorded here so the one correctly sequenced file in the category is not changed to match the others | Programme Content Lead | W2 |
| **O-02** | **Field logistics L-01…L-08 are entirely unallocated** (§2.2): six locations, three operators, three floor-spec devices, full-shift durations, on-device instrumentation, real technicians as executors, server-side observers, and a safety briefing under `SP-030`. **This pack cannot be executed at all without them**, and it gates `G2-02` and `G2-03`. `TS-006` `O-04` and `TS-008` `O-02` record the same class of gap for counter and warehouse hardware; **this is the third and largest** | Programme Manager with CTO | **W2 — before `G2`** |
| **O-03** | **`M61`'s offline knowledge mechanism arrives at W6** (`FR-KMS-017`/`-018`, T-01, T-03) and `OFF-020`, `OFF-021` and `OFF-018` are W2 scripts that require it. `AUDIT-008` KB-05, `AUDIT-010` HC-05, `HC-004` `O-01` and `TS-005` `O-03` all record the same exposure. **`04-00` `P02` non-negotiable 7 says no feature may require a connection, and offline knowledge is a listed `P02` capability** — so the W6 date makes a W2 non-negotiable unmeetable | Quality Manager with CTO | **Next Steering Committee — fold into `AUDIT-008` R-03** |
| **O-04** | **`NFR-082`'s "excluding navigation" has no measurement method** (§3.5). Running a shift without navigation is not the real duty cycle; per-process attribution needs instrumentation that may not exist on the device class. **The two methods give materially different answers** and the target is a `P1` NFR with a `04-00` non-negotiable behind it | Mobile lead with Solution Architect | **W2 — before `OFF-028`** |
| **O-05** | **`OF-12` assumes the three Flutter applications share their offline code, and nothing states that they do.** If they do not, 33 scripts become up to 99 executions, and the effort in this pack triples | Solution Architect with Mobile lead | **W2 — scoping decision** |
| **O-06** | **`OF-13` safety governance for testers is undefined.** Testers will travel to six locations including a moving vehicle and customer premises, deliberately without connectivity — which means without a means of contact. `SP-030` covers technicians; **it does not mention test personnel** | HSE with Programme Manager | **W2 — before the first field run** |
| **O-07** | **`N-09` requires the paper-notebook observation to be recorded, and there is no place to record it.** It is not a defect, not an incident and not a non-conformance; it is the single most diagnostic observation about whether the app is trusted, and `KPI-016` daily active usage will not show it | QA Lead with Technical Director | W2 |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Test_Script.md` at pack level; the field-logistics subsection justified
- [x] **`05-06` §1's own "Field test" measurement method identified as the basis, and the lab-versus-field distinction stated row by row**
- [x] All seven `04-00` `P02` non-negotiables mapped to scripts, with none unmapped
- [x] Thirteen rules stated, including item-by-item loss assertion and interrupted sync as the default case
- [x] **Field logistics enumerated as eight named requirements rather than assumed**
- [x] 33 scripts enumerated across 6 blocks, with condition, expected result and priority
- [x] The `05-06` §11 "scripted conflict scenario set" written as 7 scripts with pre-stated resolutions
- [x] **The long-divergence conflict — a six-hour-old reassignment — treated as the primary case rather than a race**
- [x] Battery measurement ambiguity identified rather than resolved by assumption
- [x] Nine edge cases stated, including sync-reported-complete-while-queued and the paper notebook
- [x] Three automatic Critical escalations, and data loss made non-deferrable
- [x] Location, network and device made sign-off fields rather than annotations
- [x] All internal links resolve
- [x] Seven open items recorded, including the one noting this pack is correctly sequenced and its consumers are not
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **The 33 per-step grids and the conflict-set expected resolutions — outstanding**
- [ ] **`O-02` field logistics unallocated — outstanding; the pack is unexecutable and it gates `G2-02`/`G2-03`**
- [ ] **`O-03` `M61` offline mechanism at W6 against W2 non-negotiables — outstanding**
- [ ] **`O-04` battery exclusion method undefined — outstanding**
- [ ] Bengali counterpart complete and signed off in context (`BN-018`) — **outstanding**
- [ ] Named approvers recorded — **pending CTO and QA Lead**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
