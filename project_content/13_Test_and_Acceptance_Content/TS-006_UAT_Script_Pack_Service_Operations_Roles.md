---
id: TS-006
title: UAT Script Pack — Service Operations Roles
project: 1000FiX ERP System v2.0
content_type: Test script
template: TPL_Test_Script.md
template_version: 1.0
version: 1.0
date: 2026-08-19
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Business Owners Forum with QA Lead
author: QA Lead with Operations Director, branch managers and Content Design
reviewers: [Operations Director, Branch Manager representatives, Dispatch Manager, Workshop Supervisor representatives, Technical Director, Content Design Lead, Localisation Lead]
approver: Content Design Lead with Operations Director
content_class: D
purpose: >
  The step-by-step acceptance scripts that the people who run service operations execute themselves,
  in their own language, and sign — agents, dispatchers, technicians, workshop supervisors, branch
  managers, remote support and data-services staff. It also carries the shared UAT method the other
  five packs reuse. UAT is the acceptance gate for a 67-module system, and a UAT script written in
  tester language is signed without being read: the signature is obtained, the defect is not found,
  and 150–250 agents discover it on the counter in front of a customer.
traces_to: [M01, M02, M03, M04, M05, M06, M31, M15, M17, M20, M23, 05-04, 05-04 §7, 05-05, 05-06 §11, 06-01 §4, 06-02 §4, SP-005, SP-007, SP-008, SP-010, SP-011, SP-012, SP-016, SP-019, SP-028, SP-030, SP-032, TR-002, TR-007, TR-008, TR-009, TR-010, TR-011, TR-023, UI-004, UI-011, UI-012, UI-013, UI-023, UI-024, UI-025, UI-026, UI-035, UI-037, UI-038, DT-002, MD-013, MD-024, MD-026, TS-001, TS-002, TS-003, TS-007, TS-008, TS-009, TS-010, TS-011, TS-012, TS-015, TS-018]
priority: P0
wave: W1
bilingual: yes
bn_counterpart: TS-006_UAT_Script_Pack_Service_Operations_Roles_BN.md
sources:
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-04_Role_Permission_and_Access_Matrix.md §1.2 Service Operations (9 roles with headcounts R06 51+, R08 150–250, R09 20–40, R10 80–150, R11 120–250, R12 15–30, R13 15–40, R14 5–12); §3.1 Pillar A permission matrix; §10 Role Definition-of-Done criterion 6 negative tests; §7 Approval Authority Matrix
    verified: 2026-08-19
    class: P1
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-01_Implementation_Roadmap_and_Phasing.md §4 Business-Side Commitment — super-users 2–3 per module at 30% of time during UAT; branch champions one per branch at 4 hours a week during rollout; "this is the binding constraint on the programme"
    verified: 2026-08-19
    class: P1
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-02_KPI_Benefits_and_Acceptance_Criteria.md §4 Gate 1 G1-03 (walk-in intake under 3 minutes by branch staff, timed observation, 20 samples), G1-11 (UAT signed off by named super-users); Gate 2 G2-01, G2-09
    verified: 2026-08-19
    class: P1
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00_Portal_Suite_Overview.md P03 Design Requirements (one click to any workspace, any record in ≤ 4 clicks, keyboard-first for intake, dispatch and finance, 1366×768 branch hardware) and P03 KPIs (walk-in intake < 3 minutes, morning queue dispatch < 10 minutes, training to competence < 4 hours)
    verified: 2026-08-19
    class: P1
supersedes: none
review_due: 2027-02-19
---

# UAT Script Pack — Service Operations Roles

| Item | Value |
|---|---|
| Test level | **UAT** — executed by the business, not demonstrated to it (`TX-14`) |
| Roles executing | `R05` `R06` `R07` `R08` `R09` `R10` `R11` `R12` `R13` `R14` — **10 roles, 526–1,022 people** |
| Modules covered | `M01` `M02` `M03` `M04` `M05` `M06` `M31`, with `M15` `M17` `M20` `M23` as touchpoints |
| Portals covered | `P03` (Service Intake, Dispatch, Branch, Workshop consoles), `P02` |
| Environment | `UAT` — **frozen for the cycle** (`TS-001` §4.7, `TS-002` `TD-14`) |
| Test data set | `TS-002` — personas 1, 2, 3; sets `A-01`…`A-08`, `D-01`…`D-06`, `M-01` |
| Wave | W1 · `P0` — the `G1` acceptance gate at Month 4 depends on it |

> **Template conformance.** `TPL_Test_Script.md` applied at **pack level**: this file specifies the
> method and enumerates 80 scripts; each script's per-step grid is completed at execution using the
> §3.2 pattern. All six template sections retained in order.

> **This file carries the shared UAT method.** `TS-007`, `TS-008`, `TS-009`, `TS-010` and `TS-011`
> reference §2.1 and §3.2 rather than restating them (`CP-01`). It is the reason this pack is `W1`
> even though four of the five siblings are later.

---

## 1. Traceability

### 1.1 Why the scripts are written in business language

The register's justification for this file states the failure mode directly: *"UAT signed by
business users is the acceptance gate; scripts written by testers rather than in business language
are signed without being read."*

That is a **content** failure, not a test-process failure, which is why this pack is content class
`D` and approved by the Content Design Lead. Three consequences follow:

| Discipline | Rule |
|---|---|
| The script says what the **job** is, not what the **system** is | "Take in a laptop for a paid repair and give the customer a receipt", not "create record in `fix.service.order` with `type=paid`" |
| Labels are **quoted from the `UI` pack**, not paraphrased | `UI-012` for `P02`, `UI-013` for `P03` as a whole, and the **workspace pack for the console the role actually opens** — `UI-023` Service Intake, `UI-024` Dispatch, `UI-025` Branch, `UI-026` Workshop, `UI-035` Managed Services. A script that invents a label teaches the wrong label and fails on a real screen |
| Bengali is the **execution** language for Bengali-reading roles | `R08`, `R10`, `R11`, `R12`, `R18`, `R29` and branch staff generally. An English-only script executed by a Bengali-reading agent tests the agent's English |

### 1.2 Traceability obligation per script

| Field | Source |
|---|---|
| Requirement | `FR-SRM-*`, `FR-FSM-*`, `FR-LOG-*`, `FR-FRD-*`, `FR-RMS-*`, `FR-DTS-*`, `FR-WSR-*` in the module §5 tables |
| Acceptance criterion | `Mnn` §17 |
| Business rules | `05-05` §2, §3, §4 with class |
| Role | `Rnn` from `05-04` — encoded in the script identifier (`TS-001` §4.3) |
| SOP | The `SP` procedure the script performs, so the SOP and the script cannot diverge |
| Training | The `TR` pack that trained the executor, so an execution failure can be attributed to training or to the system |
| Gate criterion | `06-02` §4 |
| UI copy | The `UI` pack the labels are quoted from |

**The `SP` and `TR` columns are the additions this pack makes to `TS-001` §4.4**, and they are the
reason a UAT failure is diagnosable. A script that fails can fail three ways — the system is wrong,
the procedure is wrong, or the person was not trained — and without those two columns every failure
is logged as the first.

### 1.3 Role coverage

| Role | Headcount | Scripts | `P0` | Language | Portal |
|---|---:|---:|---:|---|---|
| `R08` Service Centre Agent | 150–250 | **16** | 9 | **Bengali** | `P03` Service Intake |
| `R07` Dispatch Manager | 3–8 | 10 | 5 | English or Bengali | `P03` Dispatch Console |
| `R09` Workshop Supervisor | 20–40 | 9 | 5 | **Bengali** | `P03` Workshop Console |
| `R10` `R11` `R12` Technicians | 215–430 | **14** | 8 | **Bengali** | `P02` |
| `R06` Branch Manager | 51+ | 12 | 5 | Bengali or English | `P03` Branch Console |
| `R05` Operations Director | 1–2 | 6 | 2 | English | `P03`, `P06` |
| `R13` Remote Support Engineer | 15–40 | 6 | 2 | English | `P03`, `P10` |
| `R14` Data Services Technician | 5–12 | 7 | 4 | English | `P03` |
| **Total** | **526–1,022** | **80** | **40** | | |

---

## 2. Preconditions

### 2.1 Shared UAT rules — referenced by `TS-007` … `TS-011`

| # | Rule |
|---|---|
| **UA-01** | **The business executes; QA facilitates.** A script performed by a tester with a business user watching is a demonstration, is recorded as a demonstration, and does not count towards exit (`TX-14`) |
| **UA-02** | Every script is executed by a **named** person holding the `Rnn` the script names, using their own account, with only the permissions that role holds |
| **UA-03** | The executor is **trained before execution** — the relevant `TR` pack delivered — and the pack identifier is recorded. Untrained execution measures training, not the system |
| **UA-04** | Scripts are **reviewed and accepted by the business owner before the cycle opens**, in the execution language. A script first read on the day it is executed is signed, not read |
| **UA-05** | Expected results are stated before execution (`TX-08`). The executor records what happened, never what should have happened |
| **UA-06** | **Pass/fail is the executor's judgement, not QA's.** If the executor says the outcome is wrong for the business, it is a fail even where the system matches the specification — and that is a requirement defect, not a test error (`TS-018` §4) |
| **UA-07** | "Pass with comment" does not exist. A qualifying comment is a defect (`TX-11`) |
| **UA-08** | Labels quoted in the script must match the build. A label mismatch is a defect against the `UI` pack or the build, raised either way |
| **UA-09** | On a bilingual surface, the script is executed in **both** languages for at least the `P0` set; the Bengali execution is by a Bengali-reading executor (`TX-10`) |
| **UA-10** | Every script that performs an approval exercises the **authority boundary**: at the executor's limit, and one step beyond it refused (`05-04` §7) |
| **UA-11** | Every script that a hard rule can block includes the **blocked attempt** as a numbered step (`TX-06`) |
| **UA-12** | Timed criteria are **timed with a stopwatch on the specified sample size** — `G1-03` requires 20 timed samples of walk-in intake, not one |
| **UA-13** | The `UAT` environment and its data are **frozen for the cycle**. A data or configuration change mid-cycle voids every expected result already accepted (`TS-002` `TD-14`) |
| **UA-14** | A script is not re-executed to convert a fail into a pass. The defect is raised, fixed, and the script re-executed against a new release identifier (`SL-14`, `TX-15`) |
| **UA-15** | Every script records the **`SP` procedure** it performs and the **`TR` pack** that trained the executor (§1.2) |
| **UA-16** | Sign-off is **per pack and per role**, by a named super-user, with the release identifier and the pack version (`06-02` `G1-11`) |
| **UA-17** | A role with no executed scripts is **not accepted**, and its release is blocked — `05-04` §10 makes negative testing and business sign-off role-release conditions |
| **UA-18** | Accessibility is not deferred to `TS-016`: any executor who uses assistive technology or magnification executes their scripts with it, and the observation is recorded |

### 2.2 Environment, data and people preconditions

| # | Precondition | How to establish |
|---|---|---|
| 1 | `TS-003` SIT exit met on the same release (`TX-13`) | SIT exit record |
| 2 | `UAT` environment at the declared release; **frozen** | Release manifest; change freeze notice (`UA-13`) |
| 3 | `TS-002` `UAT` profile loaded: 2,000 parties, 3,000 devices, 10,000 historical jobs, 500 open | Load log with control totals |
| 4 | All `MD` masters configured for the branches under test, including their zones, price lists and SLA definitions | `MD-048` |
| 5 | **Named super-users identified per role**, released at 30% of their time | `06-01` §4 commitment — **no register exists**, `O-02` |
| 6 | `TR-007`, `TR-008` and `TR-009` delivered to the executors | Training records (`UA-03`) |
| 7 | Role accounts for all 10 roles with correct record rules and field-level restrictions | **Does not exist** — `TS-002` `O-04` |
| 8 | `UI-011`, `UI-012`, `UI-013` copy packs published, so labels can be quoted (`UA-08`) | Copy pack version |
| 9 | Bengali interface complete on every screen under test | `KPI-092` at 100%; `G1-08` |
| 10 | Physical conditions replicated: a 1366×768 laptop, a thermal receipt printer, a barcode scanner, a signature pad, and a mid-range Android 11 device with 3 GB RAM | `05-06` §10; without them `R08` and technician scripts test the wrong hardware |
| 11 | Notification channels in sandbox | `TS-002` `O-03` |
| 12 | Stopwatch and observation sheet for the timed scripts | `UA-12` |

---

## 3. Scripts

### 3.1 Blocks

| Block | Content | Scripts |
|---|---|---:|
| **A** | `R08` Service Centre Agent — the counter | 16 |
| **B** | `R07` Dispatch Manager — the board | 10 |
| **C** | `R09` Workshop Supervisor — the bench | 9 |
| **D** | `R10` `R11` `R12` Technicians — the job | 14 |
| **E** | `R06` Branch Manager — the branch | 12 |
| **F** | `R05` Operations Director — the network | 6 |
| **G** | `R13` Remote Support Engineer | 6 |
| **H** | `R14` Data Services Technician | 7 |

### 3.2 The script step pattern — referenced by `TS-007` … `TS-011`

| Phase | Step content |
|---|---|
| **U1 Situation** | One or two sentences of business situation, in the executor's language. *"A customer brings in a laptop that will not switch on. It is out of warranty."* |
| **U2 Do the job** | The numbered steps as the role performs them, with labels quoted from the `UI` pack |
| **U3 Check the outcome** | What the executor should see and what the customer or the next person should receive — stated as a business outcome, never a database state |
| **U4 Try what must not work** | The blocked attempt (`UA-11`) |
| **U5 Authority boundary** | Where applicable, at the limit and one step beyond (`UA-10`) |
| **U6 Bengali** | The same job in Bengali, by a Bengali-reading executor (`UA-09`) |
| **U7 Record** | Pass/fail in the executor's judgement, evidence, and any comment — which becomes a defect if it qualifies the pass (`UA-06`, `UA-07`) |

### 3.3 Block A — `R08` Service Centre Agent · 16 scripts

`P03` Service Intake · 150–250 people · Bengali · `SP-007` · `TR-007`, `TR-008`

| Script | The job | Rules and criteria | Pri |
|---|---|---|:--:|
| `UAT-R08-001` | **Take in a walk-in device for a paid repair and give the customer a receipt** — timed, 20 samples | `BRU-SRM-01`(H); **`G1-03` under 3 minutes**; `NFR-076`; `UA-12` | **P0** |
| `UAT-R08-002` | Take in a device whose serial is missing or illegible | `BRU-SRM-01`(H) exception path; `TS-002` `D-03` | **P0** |
| `UAT-R08-003` | Find an existing customer three ways — phone, name in Bengali, device serial — and not create a duplicate | `MD-013`; `TS-002` `N-01`, `N-02` | **P0** |
| `UAT-R08-004` | Register a new customer with a Dhaka address that has no holding number | `MD-007`; `TS-002` `A-04` | P1 |
| `UAT-R08-005` | **Take in a warranty job, and be refused when the warranty has expired** | `BRU-SRM-02`(H) | **P0** |
| `UAT-R08-006` | Take in an AMC job, and **be refused for a device not on the contract** | `BRU-SRM-03`(H) | **P0** |
| `UAT-R08-007` | Book an on-site visit with a slot the customer accepts, and see it reach dispatch | `AUT-001`; `SP-008` | **P0** |
| `UAT-R08-008` | Build and send an estimate; the customer approves it on their phone | `AUT-004` `AUT-005`; `BRU-SRM-07`(H) | **P0** |
| `UAT-R08-009` | **Apply a 12% discount and be refused; get it approved by the branch manager** | `05-04` §7 (agent limit 10%); `UA-10` | **P0** |
| `UAT-R08-010` | Take a payment at the counter and issue a compliant receipt on the thermal printer, in Bengali | `BRU-FIN-01`(H); `DT-002`; `05-06` §10 | **P0** |
| `UAT-R08-011` | **Take a cash receipt above `BDT 50,000` and be required to record the customer's NID** | `BRU-FIN-02`(H); `TS-002` `M-01` | P1 |
| `UAT-R08-012` | Hand a repaired device back to a customer who is not the person who dropped it off | `SP-007`; identity verification | P1 |
| `UAT-R08-013` | Tell a customer the status of their job without phoning the workshop | `NFR-077` any record in ≤ 4 clicks | P1 |
| `UAT-R08-014` | Record a complaint and see it become trackable | `BRU-QMS-04`(H); `SP-028` | P1 |
| `UAT-R08-015` | Handle a device the customer wants back unrepaired, and a device abandoned past 30 days | `BRU-SRM-16`(C); `AUT-012` | P2 |
| `UAT-R08-016` | Work a full morning queue of 25 intakes without leaving the keyboard | `P03` keyboard-first design requirement | P1 |

### 3.4 Block B — `R07` Dispatch Manager · 10 scripts

`P03` Dispatch Console · 3–8 people · `SP-008` · `TR-008`

| Script | The job | Rules and criteria | Pri |
|---|---|---|:--:|
| `UAT-R07-001` | **Dispatch a full morning queue** — timed against the under-10-minute target | `P03` KPI; `AUT-002` | **P0** |
| `UAT-R07-002` | Accept the system's recommended technician, and see why it recommended them | `BRU-FSM-03`(C) | **P0** |
| `UAT-R07-003` | **Override a recommendation and be required to give a reason code** | `BRU-FSM-04`(H) | **P0** |
| `UAT-R07-004` | **Try to assign a technician who is on leave, off-shift or at capacity, and be refused** | `BRU-FSM-01`(H) | **P0** |
| `UAT-R07-005` | **Try to assign brand warranty work to a technician whose certification lapsed, and be refused** | `BRU-SRM-09`(H) `BRU-HRM-01`(H) | **P0** |
| `UAT-R07-006` | Insert an emergency job; watch it displace a lower-priority job and **not** an at-risk SLA job | `BRU-FSM-11`(C) | P1 |
| `UAT-R07-007` | See an SLA escalate at 50/75/90/100% and acknowledge it | `AUT-009`; `SP-005` | P1 |
| `UAT-R07-008` | Suspend an SLA clock with an approved hold reason and see it resume | `BRU-SRM-15`(C) | P1 |
| `UAT-R07-009` | See 500 open jobs on the board and still find one customer's job | `NFR-033` ≤ 1 s for 500 open jobs | P1 |
| `UAT-R07-010` | Reassign a job after a technician reports a vehicle breakdown | `SP-005` escalation | P2 |

### 3.5 Block C — `R09` Workshop Supervisor · 9 scripts

`P03` Workshop Console · 20–40 people · Bengali · `SP-010` Workshop and Depot Repair · `TR-010`

| Script | The job | Rules and criteria | Pri |
|---|---|---|:--:|
| `UAT-R09-001` | Assign a job to a bench and a technician at the right repair level | `BRU-SRM-14`(H) | **P0** |
| `UAT-R09-002` | **Try to accept an L3 board-level job at a workshop without the equipment or a certified specialist, and be refused** | `BRU-SRM-14`(H) | **P0** |
| `UAT-R09-003` | Run the WIP board through a shift and see ageing by state | `P03` Workshop Console | **P0** |
| `UAT-R09-004` | **Complete a job and be refused because the quality checklist is incomplete** | `BRU-SRM-04`(H) `BRU-QMS-01`(H) | **P0** |
| `UAT-R09-005` | **Perform independent QC on a repair above `BDT 25,000` — and be refused when you were the repairer** | `BRU-SRM-18`(H) `SOD-07` | **P0** |
| `UAT-R09-006` | Put a job on parts hold and see the customer informed with a revised ETA | `AUT-007` | P1 |
| `UAT-R09-007` | Declare a device beyond economic repair with photographs and a second technician's confirmation | `BRU-SRM-12`(H) | P1 |
| `UAT-R09-008` | Reopen a closed job inside the repair warranty period and see it linked as rework | `BRU-SRM-19`(A) | P1 |
| `UAT-R09-009` | See a rework flag on a device returning within 30 days for the same fault | `BRU-SRM-06`(C) `AUT-011` | P2 |

### 3.6 Block D — `R10` `R11` `R12` Technicians · 14 scripts

`P02` · 215–430 people · **Bengali** · `SP-008` On-Site Field Service Visit, `SP-016` Spare Parts Issue, Return and Van Stock, `SP-030` Health, Safety and Incident Reporting · `TR-009`

> **`R11` Junior Technician executes a restricted subset.** `05-04` §3.1 grants `R11` `RU(o)` on
> `M01`/`M02` and `R(o)` on `M03` with no `M06` access. Scripts marked `R10/R12 only` are executed
> by a `R11` account as a **refusal** check, which is `UA-17` and `05-04` §10 criterion 6 combined.

| Script | The job | Rules and criteria | Pri |
|---|---|---|:--:|
| `UAT-R10-001` | Accept a job, travel, arrive, and have arrival recognised | `BRU-FSM-06`(A) geofence | **P0** |
| `UAT-R10-002` | **Mark arrived outside the geofence and be required to give an exception reason** | `BRU-FSM-06`(A) | P1 |
| `UAT-R10-003` | Read the device's history and past repair notes **before** touching it | `P02` job context | **P0** |
| `UAT-R10-004` | Code the fault, and use "cannot determine" honestly | `MD-024`; `HC-004` article 4 | **P0** |
| `UAT-R10-005` | Build an estimate on site, present it, take approval and a signature | `BRU-SRM-07`(H); `AUT-004` | **P0** |
| `UAT-R10-006` | Consume a part from van stock by scanning it | `BRU-FSM-08`(H) | **P0** |
| `UAT-R10-007` | **Try to issue a part against an unapproved paid repair and be refused** | `BRU-SRM-11`(H) `BRU-INV-01`(H) | **P0** |
| `UAT-R10-008` | Take the before and after photographs a warranty claim needs | `BRU-SRM-17`(H) `BRU-WTY-01`(H) | **P0** |
| `UAT-R10-009` | Take a payment at the customer's door and issue a receipt | `BRU-FSM-07`(H) | **P0** |
| `UAT-R10-010` | Record a failed visit with geotagged evidence | `BRU-FSM-09`(H) | P1 |
| `UAT-R10-011` | Close the job, generate the service report, and reconcile van stock at shift end | `AUT-035` | P1 |
| `UAT-R10-012` | Report a safety incident, and refuse to work where it is not safe | `SP-030`; `NFR-083`; `HC-004` article 33 | P1 |
| `UAT-R10-013` | Escalate a job above your level and get help without abandoning the customer | `SP-005` | P1 |
| `UAT-R10-014` | *(`R10`/`R12` only)* Handle a data-services device with custody capture — **and a `R11` account is refused** | `BRU-SEC-03`(H); `05-04` §3.1 | P1 |

> **Offline execution is not in this pack.** Every offline, sync, conflict, battery and 3G condition
> for these roles is in [`TS-015_Offline_and_Field_Condition_Test_Scripts.md`](TS-015_Offline_and_Field_Condition_Test_Scripts.md).
> Splitting them keeps this pack executable in a branch and keeps `TS-015` executable in Gazipur
> (`CP-01`).

### 3.7 Block E — `R06` Branch Manager · 12 scripts

`P03` Branch Console · 51+ people · `SP-019` Cash Collection and Banking, `SP-032` Operational Checklist Library · `TR-011`

> **There is no branch-management SOP.** Category 06 holds 28 SOPs (`SP-007`…`SP-034`) and none of
> them is the branch manager's own procedure; the closest are `SP-019` for cash and `SP-032` for the
> checklist library. Eleven of these twelve scripts therefore have no `SP` to diagnose against
> (`UA-15`), which is recorded as `O-05` rather than papered over with the nearest-fitting identifier.

| Script | The job | Rules and criteria | Pri |
|---|---|---|:--:|
| `UAT-R06-001` | Open the branch console and know, in one screen, whether today is going well | `P03` Branch Console; `RP-004` | **P0** |
| `UAT-R06-002` | Approve an estimate above `BDT 25,000` and a discount up to 20% | `BRU-SRM-08`(H); `05-04` §7 | **P0** |
| `UAT-R06-003` | **Try to approve a 30% discount and be refused; escalate to the Sales Manager** | `05-04` §7; `UA-10` | **P0** |
| `UAT-R06-004` | Close the branch cash for the day, and **be blocked from opening tomorrow with today unclosed** | `BRU-FIN-10`(H) | **P0** |
| `UAT-R06-005` | See WIP ageing and uncollected devices, and act on the oldest | `AUT-012`; `KPI-009` | **P0** |
| `UAT-R06-006` | Approve an inter-branch transfer out of your stock | `BRU-INV-02`(H) | P1 |
| `UAT-R06-007` | See only your own branch's data — **and confirm you cannot see another branch's** | `05-04` §4 `T2`; `NFR-015` | P1 |
| `UAT-R06-008` | Approve leave and be warned when coverage would fall below minimum | `BRU-HRM-04`(A) | P1 |
| `UAT-R06-009` | Review your branch's rework and QC first-pass rates | `KPI-005`, `KPI-007` | P1 |
| `UAT-R06-010` | Raise and own a non-conformance for your branch | `BRU-QMS-02`(H) | P1 |
| `UAT-R06-011` | Handle the abandonment process for a device uncollected past 30 days | `BRU-SRM-16`(C) | P2 |
| `UAT-R06-012` | Do all of the above on a 1366×768 laptop without horizontal scrolling | `04-00` `P03`; `PS-05` | P2 |

### 3.8 Block F — `R05` Operations Director · 6 scripts

| Script | The job | Rules and criteria | Pri |
|---|---|---|:--:|
| `UAT-R05-001` | Compare all live branches on TAT, first-time fix and SLA compliance | `KPI-002`…`006`; `P06` branch league | **P0** |
| `UAT-R05-002` | Approve an estimate above `BDT 100,000` | `05-04` §7 | **P0** |
| `UAT-R05-003` | See the live operations board — open jobs, technicians, SLA countdowns | `P06` real-time | P1 |
| `UAT-R05-004` | Drill from a network figure to a single job | `SL-26`; `NFR-077` | P1 |
| `UAT-R05-005` | See all branches' data and confirm the scope is network-wide, not branch-limited | `05-04` §1.1 | P1 |
| `UAT-R05-006` | Act on an SLA breach escalation that reached you | `SP-005`; `AUT-009` | P2 |

### 3.9 Block G — `R13` Remote Support Engineer · 6 scripts

`P03`, `P10` · 15–40 people · `SP-011` Remote Support and Managed Services · **no course pack** — see `O-07`

| Script | The job | Rules and criteria | Pri |
|---|---|---|:--:|
| `UAT-R13-001` | Take an MSP alert to a ticket and resolve it without a site visit | `M05`; `KPI-071` | **P0** |
| `UAT-R13-002` | Launch a remote session with the customer's consent captured | `M05`; consent record | **P0** |
| `UAT-R13-003` | Escalate a remote case to a site visit and hand over full context | `SP-005` | P1 |
| `UAT-R13-004` | Measure and report SLA attainment for one MSP client | `KPI-070` | P1 |
| `UAT-R13-005` | See only your assigned clients' estates | `05-04` §1.2 scope | P1 |
| `UAT-R13-006` | Produce a monthly service report a client will accept | `M05`; `P04` | P2 |

### 3.10 Block H — `R14` Data Services Technician · 7 scripts

`P03` · 5–12 people · `SP-012` Data Recovery and Secure Data Handling · **no course pack** — see `O-07`

| Script | The job | Rules and criteria | Pri |
|---|---|---|:--:|
| `UAT-R14-001` | Take custody of a data-recovery device with the chain recorded at every handover | `BRU-SEC-03`(H) | **P0** |
| `UAT-R14-002` | **Confirm nobody outside the assigned team can open the case, and that every access is logged** | `BRU-SEC-03`(H); `05-04` `T5`; `NFR-070` | **P0** |
| `UAT-R14-003` | Complete a recovery, hand over, and issue the certificate | `M06` | **P0** |
| `UAT-R14-004` | **Purge recovered data at the agreed date, and be blocked from purging under a documented hold** | `BRU-SEC-04`(H) | **P0** |
| `UAT-R14-005` | Capture a customer's access credential with explicit consent, and see it purged at handover | `BRU-SRM-20`(H) | P1 |
| `UAT-R14-006` | Perform a certified destruction with a witness | `05-04` §7 data destruction | P1 |
| `UAT-R14-007` | Confirm recovered customer data is never available as model training data | `BRU-AIM-03`(H) | P1 |

**Pack total: 80 scripts · 40 at `P0` · 32 at `P1` · 8 at `P2`.**

### 3.11 Negative and edge cases

Beyond the 22 refusals embedded above (`UA-11`), the pack exercises these at role level:

| # | Condition | Expected system behaviour |
|---|---|---|
| N-01 | `R08` attempts to open the Finance Console | Refused; not merely hidden (`05-04` §2) |
| N-02 | `R11` attempts a `R10`-only action | Refused with a message that says what to do next (`PS-09`) |
| N-03 | `R06` attempts to view another branch's job by direct URL | Refused at the record rule, not the view (`NFR-015`, `BR-STD-01`) |
| N-04 | `R08` attempts to see `unit_cost` and `margin` on an estimate | Field not present in the payload, not hidden in the UI (`05-04` §5) |
| N-05 | Any role attempts a bulk export of personal data | Blocked without approval; every export logged (`BRU-SEC-05`) |
| N-06 | Executor's session idles past 60 minutes mid-script | Re-authentication required; **unsaved work not silently lost** (`NFR-069`) |
| N-07 | Thermal printer offline when a receipt is due | Clear recovery path; the payment is not lost (`NFR-050`) |
| N-08 | Barcode scanner reads a part not compatible with the device | Warned per `MD-022`; the technician can proceed with a reason or stop |

### 3.12 Bilingual check

**This pack is bilingual (`CG-010` §3.2) and Bengali is the execution language for five of the ten
roles.** All 40 `P0` scripts are executed in Bengali by a Bengali-reading executor (`UA-09`).

| Element | EN correct | BN correct | Truncation |
|---|:--:|:--:|:--:|
| Every quoted `P03` and `P02` label (`UI-012`, `UI-013`) | ● | ● | ● at 1366×768 and on a 5-inch device |
| Every validation and error message encountered (`UI-004`) | ● | ● | ● |
| Counter receipt on the thermal printer (`DT-002`) | ● | ● | ● |
| Customer notification triggered by the script (`NT` set) | ● | ● | ● |
| Amount grouping — `12,34,567` in Bengali (`TS-002` `M-04`) | ● | ● | ● |
| Bengali fault-code and reason-code names (`MD-024`, `MD-026`) | ● | ● | ● |

---

## 4. Exit Criteria

| Criterion | Threshold |
|---|---|
| `P0` scripts passed | **100% — no tolerance** |
| `P1` scripts passed | ≥ 98% |
| `P2` scripts passed | ≥ 90% |
| Scripts executed **by the business** rather than demonstrated | 100% (`UA-01`) |
| Roles with at least one executed script and a signature | **10 of 10** (`UA-17`) |
| Refusal steps exercised | 100% of the 22 embedded refusals plus `N-01`…`N-05` |
| Authority-boundary steps exercised | 100% of scripts that approve (`UA-10`) |
| Bengali execution of the `P0` set | **100%** (`UA-09`) |
| **`G1-03` walk-in intake** | **Under 3 minutes on 20 timed samples** (`UA-12`) |
| Dispatch of a full morning queue | Under 10 minutes |
| Open Critical defects | **Zero** |
| Open High defects | Zero, or deferred by named decision (`TX-16`) |
| Executor-judgement fails reclassified as requirement defects, not test errors | 100% (`UA-06`) |

---

## 5. Defects Raised

| Defect ID | Script | Severity (`TS-018`) | Status |
|---|---|---|---|
| *(populated at execution)* | | | |

**Three routing rules specific to UAT:**

| Trigger | Route |
|---|---|
| Executor judges the outcome wrong for the business although the system matches the specification | **Requirement defect** to the module business owner, not a test error (`UA-06`, `TS-018` §4) |
| A quoted label does not match the build | To the `UI` pack owner **and** the build team; one of them is wrong (`UA-08`) |
| The script cannot be performed as written because the procedure is different in practice | To the `SP` owner — the SOP and the system have diverged, and the script found it (`UA-15`) |

---

## 6. Sign-off

Per `UA-16`: **one signature per role**, by a named super-user, against a release identifier and a
pack version.

| Role | Super-user name | Release | Pack version | Date | Signature |
|---|---|---|---|---|---|
| `R08` Service Centre Agent | | | | | |
| `R07` Dispatch Manager | | | | | |
| `R09` Workshop Supervisor | | | | | |
| `R10` Senior Technician | | | | | |
| `R11` Junior Technician | | | | | |
| `R12` Specialist Technician | | | | | |
| `R06` Branch Manager | | | | | |
| `R05` Operations Director | | | | | |
| `R13` Remote Support Engineer | | | | | |
| `R14` Data Services Technician | | | | | |
| **Pack acceptance** — Operations Director | | | | | |

---

## Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **This pack is `P0`/W1 and `TS-003` — the SIT library whose exit is its entry (`UA-02`, precondition 1) — is registered at W2.** UAT cannot start on an unproven build, so either `TS-003` moves to W1 or this pack starts without a SIT gate. Recorded in `TS-003` `O-01` from the other side | Programme Content Lead with QA Lead | **W1** |
| **O-02** | **`TR-023` Train-the-Trainer and Super-User Kit exists; a register of named super-users does not.** `06-01` §4 commits 2–3 per module at 30% of time and calls business availability *"the binding constraint on the programme"*; `G1-11` requires signatures from *named* super-users; `UA-02` and `UA-16` require a named person per role. This pack needs at least 10 named people drawn from 526–1,022 staff and **cannot name one**. The kit trains them; nothing identifies them. `TS-001` `O-09` | Business Owners Forum with Programme Manager | **W1 — before the cycle opens** |
| **O-03** | **`UA-04` requires business-owner acceptance of the scripts in the execution language before the cycle opens** — which means the Bengali counterpart of this pack must exist *before* UAT, not alongside it. Bengali authoring capability is unresourced (`TS-002` `O-06`, `TR-001` `O-05`) | Localisation Lead with QA Lead | **W1 — six weeks before the cycle** |
| **O-04** | **Physical UAT conditions are unspecified** (precondition 10). A 1366×768 laptop, a thermal printer, a scanner, a signature pad and a mid-range Android 11 device are required, and no document allocates them. `R08` scripts executed on a developer's 27-inch monitor will pass and then fail on the counter | Programme Manager with IT Administrator (`R33`) | **W1** |
| **O-05** | **There is no branch-management SOP** (§3.7). `06B` holds 28 SOPs and none covers the branch manager's own procedure, so eleven of the twelve `R06` scripts cannot name the `SP` that `UA-15` requires for diagnosis. `R06` is a **51+-headcount role** and the only role in this pack in that position; every other role maps cleanly (`R08`→`SP-007`, `R07`/`R10`→`SP-008`+`SP-016`, `R09`→`SP-010`, `R13`→`SP-011`, `R14`→`SP-012`). Either `SP-035` is registered or the register records the gap deliberately | Business Process Analysts with Programme Content Lead | **W1 — before execution** |
| **O-06** | **`RP-004` operational-console dashboard specification is unwritten** (Category 14 unstarted), and `UAT-R06-001` accepts "the branch console tells me whether today is going well". Without `RP-004` the executor is judging an undesigned screen | BI Lead | **W1** |
| **O-07** | **Three of the ten roles in this pack have no course pack**, so `UA-03` cannot be satisfied for them: `R05` Operations Director, `R13` Remote Support Engineer (15–40 people) and `R14` Data Services Technician (5–12 people, the only role with `T5` restricted-data access). `08B` holds 18 packs (`TR-007`…`TR-024`) and none covers them. `AUDIT-009` already recorded four roles on declared interim routes and three roles unregistered; **this is the test-side consequence of the same gap** | L&D Lead with Technical Director | **W1 — before execution of blocks F, G, H** |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Test_Script.md` at pack level; interpretation declared
- [x] **The business-language failure mode named as a content failure, which is why this pack is class `D`**
- [x] **Eighteen shared UAT rules stated once here for reuse by the five sibling packs (`CP-01`)**
- [x] Seven-phase script pattern defined, including the refusal step and the authority boundary
- [x] 80 scripts enumerated across 10 roles, with rules, criteria and priority
- [x] Role coverage table reconciles to the `05-04` §1.2 headcounts
- [x] **`SP` and `TR` columns added so a UAT failure can be diagnosed to system, procedure or training**
- [x] Every `SP` identifier verified against the 28 files in `06B`; the one role with no owning SOP is named rather than mapped to the nearest fit
- [x] `R11` restriction handled as a refusal check rather than an omission
- [x] Offline conditions deliberately excluded and delegated to `TS-015` (`CP-01`)
- [x] Physical hardware conditions stated as preconditions, not assumed
- [x] Timed criteria carry their sample size (`G1-03`, 20 samples)
- [x] Bilingual obligation stated as an execution requirement, not a review step
- [x] Three UAT-specific defect routing rules recorded, including executor-judgement requirement defects
- [x] All internal links resolve
- [x] Seven open items recorded with owners and blocking consequences
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **The 80 per-step grids written in business language — outstanding; this file specifies and enumerates**
- [ ] **`O-07` three roles with no course pack — outstanding; blocks `UA-03` for blocks F, G, H**
- [ ] **`O-02` no named super-users — outstanding; blocks `G1-11`**
- [ ] **`O-03` Bengali pack required before the cycle — outstanding**
- [ ] **`O-05` no branch-management SOP for a 51+-headcount role — outstanding; must precede execution**
- [ ] Bengali counterpart complete and signed off in context (`BN-018`) — **outstanding**
- [ ] Named approvers recorded — **pending Content Design Lead and Operations Director**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
