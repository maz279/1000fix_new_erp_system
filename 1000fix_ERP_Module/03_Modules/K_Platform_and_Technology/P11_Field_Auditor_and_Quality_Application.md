---
id: FIX-ERP2-P11
portal_id: P11
portal_code: FAQ
portal_name: Field Auditor & Quality Application
type: Native Mobile Application (offline-first)
category: Portal & Application Suite (filed under K — Platform & Technology)
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-13
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
business_owner: Quality Manager
system_owner: Field Platform Squad
priority: P2
wave: W5
---

# P11 — Field Auditor & Quality Application
### Portal Suite · Code `FAQ` · ★ New in v2.1

---

## 1. Portal Identity

| Attribute | Value |
|---|---|
| **Portal ID** | P11 |
| **Portal code** | `FAQ` |
| **Type** | Native mobile application — **offline-first** |
| **Status** | ★ New in v2.1 — audits were a paper process in v1.0 |
| **Priority** | **P2** |
| **Delivery wave** | **W5** (Months 19–22) |
| **Users** | Quality auditors, branch managers, regional and operations managers |
| **Volume** | **20–60 users** |
| **Business owner** | Quality Manager |
| **System owner** | Field Platform Squad |
| **Technology** | Flutter — reusing the P02 offline journal and sync engine |
| **Custom development** | `CD-212` |
| **Requirement range** | FR-POR-311 … FR-POR-334 |
| **Requirement count** | **24** *(measured — supersedes the 3 allocation in `05-01` §4)* |
| **Effort estimate** | **16 person-weeks** |
| **Backing modules** | M04, M12, M15, M17, M19, M21, M22, M23, M24, M25, M45, M47, M59, M60 |
| **Platform dependencies** | M29 Identity · M28 Integration Gateway · M30 Platform Admin · M65 Localisation |

---

## 2. Purpose

P11 is **how the Company checks itself**. It is the surface on which quality auditors and
managers verify, at 51+ physical locations, that what the system says is happening is actually
happening.

An ERP records what people enter. An audit establishes whether the entry was true. That
distinction is the whole purpose of this application: a cash balance the system shows, counted;
a stock quantity the ledger holds, verified on the shelf; a fire extinguisher the facility
register lists, found, in date, and where it should be; a calibration certificate the equipment
record claims, produced.

P11 holds no authoritative state. The audit programme belongs to M23, the finding and its CAPA
to M23, the stock count to M15, the equipment record to M45. What P11 owns is **the audit
execution** — offline, on site, with evidence, and with the auditee's acknowledgement captured
before the auditor leaves.

### Why It Exists

**ISO 9001 requires internal audit, and the Company's ISO status is a competitive asset.**
BR-QMS-004 requires internal audit management with findings and corrective action tracking.
1000FiX is the only ISO-certified IT service provider in Bangladesh and states it as a
competitive advantage; the audit programme is what keeps that true.

**Paper audits do not produce data.** `04-00` targets **100% of audits completed on mobile
rather than paper** and **100% of findings with evidence attached**. A paper audit produces a
signed form in a folder; a mobile audit produces a finding with a photograph, a clause
reference, an owner and a due date that M23 can track to closure.

**Finding-to-CAPA cycle time is the measure that matters.** `04-00` targets under 5 days. A
finding raised on paper, typed up a week later, assigned informally and chased by memory takes
far longer, and the interval is when the non-conformity persists.

**Four other modules need verification that only a person on site can perform.** M15's stock
accuracy, M45's equipment audit, M47's facility and safety inspection, and M19's cash spot
check are all physical verifications. Building four separate mobile capabilities for them would
be four times the cost and four times the maintenance.

**Marketplace sellers need auditing too.** `04-00` includes auditing marketplace sellers
against platform standards — the mechanism that makes P07's quality-parity commitment real
rather than declared.

### Evidence Basis

| Source | What It Establishes |
|---|---|
| ERP BRD BR-QMS-001 | "Maintain ISO 9001:2015 compliance documentation with version control" |
| ERP BRD BR-QMS-004 | "Support internal audit management with findings and corrective action tracking" |
| ERP BRD BR-QMS-002 | Complaint management with root cause analysis and CAPA tracking |
| ERP BRD BR-QMS-003 | Service quality KPIs: rework rate, complaints, SLA compliance, CSAT |
| ERP BRD BR-INV-013 | Cycle counting with variance reporting — executed on this application |
| ERP BRD BR-FIN-013 | Complete, immutable audit trail for financial transactions — cash spot checks feed it |
| `04-00` §P11 | Capability set across seven areas and four KPIs, adopted verbatim |
| `04-00` §3 PS-08 | Offline-capable with queued sync — binding on P02, P09 and **P11** |
| `02-01` §10 AS-13 | Append-only local journal with server-side conflict resolution |
| `05-04` §2 | P11 access held by R05, R06 and R32 only |
| `M15` §5.7 FR-INV-048 | Blind counting on a scanner or phone, capturing the counter's identity per line |
| `M45` §5.5 FR-EAM-038 | Physical equipment verification, counted by scan, blind to the expected list |
| `M47` §5.6 FR-FAC-040 | Safety equipment register with inspection evidence |
| Company Profile §Quality & Certification | "Only ISO-certified IT service provider in Bangladesh" — the asset this application protects |

---

## 3. Scope Boundary

### 3.1 In Scope

| # | Capability |
|---|---|
| 1 | The auditor's assigned audit list with scope, checklist and schedule |
| 2 | Audit execution offline against a versioned checklist |
| 3 | Observation recording against a clause, a process or a control |
| 4 | Photographic and document evidence capture with GPS and timestamp |
| 5 | Finding creation with classification, severity, clause linkage and owner assignment |
| 6 | Verification of previously raised CAPAs on site |
| 7 | **Cash spot check** at a branch against the system balance |
| 8 | **Inventory spot count** against the M15 ledger, blind |
| 9 | **Equipment and calibration check** against the M45 register |
| 10 | **Facility and safety check** against the M47 register — fire equipment, first aid, emergency lighting, housekeeping |
| 11 | 5S and housekeeping assessment |
| 12 | **Marketplace seller audit** against platform standards |
| 13 | On-device audit report generation |
| 14 | Auditee acknowledgement signature captured on site |
| 15 | Full offline operation with queued, ordered, idempotent sync |
| 16 | Bengali and English throughout |
| 17 | Instrumentation of audit completion, evidence attachment and CAPA cycle time |

### 3.2 Explicitly Out of Scope

| Capability | Owned By | Why the Boundary Sits Here |
|---|---|---|
| **The audit programme, checklist definition, finding taxonomy and CAPA lifecycle** | **M23** Quality Management System | P11 executes an audit M23 defines and raises findings M23 tracks |
| **CAPA execution and closure** | **M23** | P11 verifies on site; the corrective action is performed by its owner |
| **Root cause analysis and quality investigation** | **M23** | An auditor observes; the investigation is a separate process |
| **The stock ledger, adjustment and approval** | **M15** Inventory | P11 submits a count; M15 computes variance and governs the adjustment. **The auditor never adjusts stock** |
| **The equipment register, calibration and fitness decision** | **M45** Enterprise Assets | P11 verifies presence and status; M45 owns the record |
| **The facility register, compliance and work orders** | **M47** Facility | P11 inspects; M47 owns the register and raises the work |
| **The cash book, reconciliation and posting** | **M19 / M04** | P11 records a count; Finance reconciles and posts. **The auditor never adjusts cash** |
| **Marketplace seller approval, scoring and suspension** | **M12** (surface **P07**, governance **P03**) | P11 audits against standards; consequence is M12's |
| **HSE incident investigation and safety management** | **M59** Health, Safety & Wellbeing | P11 checks that safety equipment exists and is in date; M59 owns the regime |
| **Compliance register and risk management** | **M60** GRC | P11 findings feed the register; M60 owns it |
| **Technician competency assessment** | **M22** | An audit may observe practice; certification is M22's |
| **Routine operational work at a branch** | **P03** | An auditor observes; they do not operate |
| **Identity, session policy and MFA** | **M29** | **PS-01** |

### 3.3 Shared Concepts

| Concept | P11's Role | Owning Module |
|---|---|---|
| Audit execution on site | **Owns** — the defining concern of this application | P11 |
| **The offline journal** | **Owns** locally; reuses the P02 implementation | P11 |
| Audit programme and checklist | Executes a version M23 defines | M23 |
| Finding and CAPA | Raises and verifies; M23 tracks to closure | M23 |
| Stock count | Submits; M15 computes variance and governs adjustment | M15 |
| Equipment verification | Submits; M45 owns the register and the loss record | M45 |
| Facility and safety inspection | Submits; M47 owns the register and the work order | M47 |
| Cash count | Submits; M19 and M04 reconcile | M19 / M04 |
| Marketplace seller standard | Audits against; M12 applies consequence | M12 |
| Evidence media | Captures; M24 stores under retention | M24 |

---

## 4. Benchmark Basis

| Reference System | Equivalent Capability | What We Adopted | What We Rejected |
|---|---|---|---|
| **Mobile audit and inspection platforms (GoAudits, Teammate, Inspectly360, flowdit)** | On-site data collection on phone or tablet **even without connectivity**, with entries, photographs and notes stored locally and syncing automatically; the full internal audit cycle from scheduling and checklist creation to finding capture, corrective action generation and close-out reporting; automatic CAPA records meeting ISO 9001 documentation requirements | **The full offline audit cycle is the single most influential external reference for P11**, and specifically **automatic CAPA generation from a finding**. The gap between observing a non-conformity and having an owned, dated corrective action is where audit value is lost, and closing it in the app is what makes the 5-day cycle-time target achievable | Their generic checklist-builder marketplaces; checklists here are M23-owned, versioned quality documents, not user-authored forms |
| **ISO 9001 audit software practice** | Geo-stamped photo and video evidence embedded directly in the audit report; findings linked to clauses; audit trail for certification | **Geo-stamped evidence embedded at the point of observation**, which is what makes a finding defensible weeks later when the auditee disputes it. Also adopted: **clause linkage on every finding**, so an external certification auditor can trace the internal programme's coverage | Full ISO document-control capability; that is M23 with OCA `management-system` |
| **Retail and multi-site inspection practice** | Standard checklists across sites so results are comparable; spot checks on cash and stock; housekeeping and 5S scoring | **Comparability across 51+ branches.** An audit whose questions differ by site produces observations, not data. The checklist is standard, versioned, and its version is recorded on every audit | Mystery-shopper methodology; a different discipline belonging to M34 |
| **Blind-count practice (M15, M45)** *(the internal benchmark)* | Counts executed without displaying the expected quantity, capturing the counter's identity per line | **Blind counting, adopted from the module specifications rather than invented here.** M15 FR-INV-048 and M45 FR-EAM-038 both require it, and P11 is the surface that delivers it. Showing the expected figure to a counter produces confirmation, not verification | — |
| **P02 Technician Mobile Application** *(the internal benchmark)* | Append-only offline journal, idempotent ordered replay, conflict surfacing, sync reporting | **The journal and sync engine are reused, not rebuilt** — the third reuse of the same component after P09 | — |
| **Auditor independence practice** | The person performing a check does not approve the consequence arising from it | **Segregation enforced in the application**: an auditor counting stock cannot approve the adjustment (SOD-05); an auditor counting cash cannot reconcile the cash book (SOD-12). The app surfaces the count and stops | — |

**Design position.** Five deliberate differences from the benchmark.

First, **the auditor observes and records; they never correct.** A count is submitted, not
applied. A finding is raised, not resolved. This preserves the segregation of duties in
`05-04` §6 — notably SOD-05 (count versus adjustment) and SOD-12 (cash handling versus
reconciliation) — and it is what makes the audit evidence admissible in the Company's own
governance.

Second, **counts are blind.** The expected quantity, balance or equipment list is never
displayed before the count is entered. This is required by M15 and M45 and it is the difference
between verification and confirmation.

Third, **a finding produces a CAPA before the auditor leaves the site.** Classification,
severity, clause, owner and due date are captured on device, and M23 receives a complete
corrective action on sync. The 5-day finding-to-CAPA target is met by removing the transcription
step entirely.

Fourth, **the auditee acknowledges on site.** The report is generated on the device and signed
by the branch manager or seller before the auditor leaves. A finding disputed three weeks later,
against a report the auditee never saw, is an argument nobody wins.

Fifth, **one application, five check types.** Quality audit, cash spot check, inventory spot
count, equipment verification and facility inspection are one application because they are one
activity — a person at a site verifying reality against a record. Building them separately would
be four times the cost for the same 20–60 users.

---

## 5. Capability Areas & Functions

### 5.1 Audit Programme & Execution

| FR ID | Feature | Function — "The application shall…" | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-POR-311 | Assigned audits | Present the auditor's assigned audits with site, type, scope, scheduled date and the checklist version to be used, available offline | **P0** | L5 |
| FR-POR-312 | Audit scope and checklist | Present the versioned checklist M23 defines, recording the version used on the audit so results remain comparable and traceable | **P0** | L5 |
| FR-POR-313 | Offline execution | Execute a complete audit with no connectivity — every question, every capture, every finding — with nothing deferred to a connected step (**PS-08**) | **P0** | L5 |
| FR-POR-314 | Observation recording | Record an observation against a checklist item, a clause, a process or a control, with conformity, non-conformity, observation or not-applicable and a mandatory note where non-conforming | **P0** | L5 |
| FR-POR-315 | Evidence capture | Capture photographs and documents with GPS coordinates and timestamp embedded, attached to the specific observation rather than to the audit as a whole | **P0** | L5 |
| FR-POR-316 | Audit continuation | Allow an audit to be paused and resumed across sessions and days without loss, and prevent two auditors editing the same audit concurrently | P1 | L5 |

### 5.2 Findings & CAPA

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-POR-317 | **Finding creation** | Raise a finding with classification, severity, the clause or control breached, a description, the evidence attached, a named owner and a due date — **on device, before leaving the site** | **P0** | L5 |
| FR-POR-318 | Finding linkage | Link a finding to the process, person, record, asset or location it concerns, so M23 can aggregate by cause rather than by site alone | **P0** | L5 |
| FR-POR-319 | Automatic CAPA | Generate the corrective action record from the finding, complete with owner and due date, submitted to M23 on sync (BR-QMS-004) | **P0** | L5 |
| FR-POR-320 | **CAPA verification** | Present previously raised CAPAs due for verification at this site, and record verification, partial verification or failure with fresh evidence | **P0** | L5 |
| FR-POR-321 | Repeat-finding detection | Surface, at the point of raising, whether the same finding has been raised at this site before, and flag a repeat as an escalated severity | P1 | L5 |

### 5.3 Branch Checks

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-POR-322 | **Cash spot check** | Count branch cash **blind**, submit it, and receive the variance against the system balance **after** submission — never before (BR-FIN-013) | **P0** | L5 |
| FR-POR-323 | **Inventory spot count** | Count stock by scan **blind**, capturing the counter's identity per line, and submit to M15 for variance computation (M15 FR-INV-048, BR-INV-013) | **P0** | L5 |
| FR-POR-324 | **Equipment verification** | Verify equipment presence by scan against the M45 register **blind**, record condition, holder and location, and flag items not found (M45 FR-EAM-038) | **P0** | L5 |
| FR-POR-325 | **Calibration check** | Verify that measurement-critical instruments present at the site are within calibration, and record any out-of-service instrument found in use as a finding (M45) | **P0** | L5 |
| FR-POR-326 | **Facility and safety check** | Verify fire extinguishers, alarms, emergency lighting, exit signage and first-aid kits against the M47 register, with location, condition and next-due date, raising a finding on any lapse (M47 FR-FAC-040) | **P0** | L5 |
| FR-POR-327 | Statutory document check | Verify that the site's trade licence, fire licence and other displayed statutory documents are present and current against the M47 register | P1 | L5 |
| FR-POR-328 | 5S and housekeeping | Score housekeeping and 5S against a standard rubric with photographic evidence, comparable across sites and periods | P2 | L5 |
| FR-POR-329 | Process observation | Observe a live process — intake, QC, handover, cash handling — against its defined standard and record conformity with evidence | P1 | L5 |

### 5.4 Marketplace, Reporting & Sync

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-POR-330 | **Marketplace seller audit** | Audit a marketplace seller against platform standards — premises where applicable, equipment, competence evidence, process and record-keeping — using the same finding and CAPA mechanism | P2 | L5 |
| FR-POR-331 | **On-device report** | Generate the audit report on the device at the end of the audit, showing every observation, finding, severity, owner and due date, in Bengali or English | **P0** | L5 |
| FR-POR-332 | **Auditee acknowledgement** | Present the report to the auditee, capture their signature and any comment, and prevent the audit closing without acknowledgement or a recorded refusal | **P0** | L5 |
| FR-POR-333 | Sync to M23 | Submit the completed audit, its observations, findings, CAPAs, counts and evidence through the append-only journal with idempotent ordered replay (AS-13) | **P0** | L5 |
| FR-POR-334 | Auditor history | Present the auditor their own completed audits, open findings and CAPAs awaiting verification, offline | P1 | L5 |

---

## 6. Technical Functions

| # | Technical Function | Requirement |
|---|---|---|
| T-01 | **Full offline execution** | A complete audit executes offline with no feature unavailable and no data loss (**PS-08**) |
| T-02 | **Journal reuse** | The append-only journal, idempotent replay and ordered per-aggregate sequencing are **the P02 implementation** — the third reuse after P09 (AS-13) |
| T-03 | **Durability before acknowledgement** | Every observation, finding, count and evidence capture is written to the journal before the UI acknowledges it |
| T-04 | **Blind-count enforcement** | Expected quantities, balances and equipment lists are **not present in the device payload** before submission. Blindness is enforced by not shipping the data, not by hiding it in the interface |
| T-05 | **Evidence binding** | Photographs bind to the specific observation, EXIF-stamped with GPS and time on device, queued with resumable upload |
| T-06 | **Checklist version integrity** | The checklist version is recorded on the audit and cannot change mid-audit; a version change mid-programme applies to audits started after it |
| T-07 | **Report determinism** | The on-device report renders identically to the server-side record after sync; the auditee signs what M23 receives |
| T-08 | **Signature binding** | The auditee's signature binds to the report content hash, so the acknowledged version is provable |
| T-09 | **Segregation enforcement** | The application offers no path to adjust stock, adjust cash, close a CAPA or alter a register. Submission is the only action (SOD-05, SOD-12) |
| T-10 | **Concurrent-edit prevention** | Two auditors cannot edit one audit; an audit is locked to its assigned auditor with a supervised reassignment path |
| T-11 | **Device envelope** | Acceptable operation on a mid-range Android device; a full-day audit within a normal battery budget |
| T-12 | **Local data protection** | The local store is encrypted at rest; audit data and evidence purge after sync plus a bounded window, and immediately on logout or remote wipe (AS-14) |
| T-13 | **All traffic through the gateway** | Every call routes through M28 (**PS-02**) |
| T-14 | **No client-side business logic** | Variance, severity escalation and CAPA due-date rules are computed by their owning module (**PS-11**) |
| T-15 | **Bengali and English** | Complete in both; checklists render in the language the auditee reads (**PS-03**) |
| T-16 | **Sync reporting** | Sync success, pending count and failures visible to the auditor and to the Quality Manager in P03 |
| T-17 | **Instrumentation** | Audit completion, evidence attachment, CAPA cycle time and repeat findings instrumented to M25 (**PS-10**) |

---

## 7. Business Functions & Benefits to 1000FiX

### 7.1 What Changes for Each Actor

| Actor | Today | With P11 |
|---|---|---|
| **Quality auditor** | Carries a clipboard; types the audit up days later | Executes on device, raises findings with photographs, leaves with an acknowledged report |
| **Branch manager (as auditee)** | Learns of findings weeks later, sometimes second-hand | Sees and signs the report before the auditor leaves |
| **Branch manager (as auditor)** | Has no structured way to check their own branch | Runs the same standard checks between formal audits |
| **Quality manager** | Compiles audit results from forms and memory | Sees findings, CAPA status and repeat patterns across 51+ sites |
| **Finance** | Cash spot checks are ad hoc and unrecorded | Blind counts recorded with variance computed centrally |
| **Inventory manager** | Cycle counts depend on branch discipline | Independent spot counts, blind, with the counter named |
| **Quality Manager (M45)** | Calibration compliance is asserted | Verified physically at each site, with out-of-service instruments found in use raised as findings |
| **Branch Operations Lead (M47)** | Safety equipment status is a register entry | Verified on site with evidence, lapses raised as findings |
| **External ISO auditor** | Receives a folder of forms | Receives a traceable programme with clause coverage, evidence and closure records |
| **CAPA owner** | Receives a finding informally | Receives an owned, dated corrective action within a day |

### 7.2 Quantified Business Benefit

| Benefit | Mechanism | Value |
|---|---|---|
| **ISO 9001 certification protection** | A traceable internal audit programme with clause coverage, evidence and CAPA closure | The dominant benefit. 1000FiX's ISO status is a stated competitive advantage and a corporate-tender qualifier; its loss would close the corporate segment |
| **Finding-to-CAPA cycle time** | CAPA generated on device with owner and due date, no transcription step | `04-00` target: **under 5 days**. The interval is when the non-conformity persists |
| **Audit programme completion** | Scheduled, assigned, tracked and measured | `04-00` target: **100% audit plan completion**, against a paper process where slippage is invisible |
| **Inventory accuracy verification** | Independent blind counts alongside M15's own cycle counts | Supports M15's 75% → 98% accuracy target by making the measurement independent |
| **Cash control** | Blind spot checks with variance computed centrally | Supports SOD-12 and the cash controls in M04 and M19 |
| **Calibration compliance verification** | Physical verification that the register matches reality at each site | Supports M45's **100% calibration compliance Wave 5 gate**, which no register alone can prove |
| **Facility and safety compliance** | Physical verification of fire and safety equipment | Supports M47's 100% statutory compliance target and the Company's duty of care |
| **Marketplace quality parity** | Sellers audited against the same standards as owned operations | Makes P07's quality-parity commitment enforceable rather than declared |
| **Repeat-finding reduction** | Repeat findings detected and escalated at the point of raising | Converts audit from a recurring cost into an improvement mechanism |
| **Administrative labour** | No transcription, no compilation, no chasing | Contributes to the **BDT 62 lac/year** administrative saving |

### 7.3 Non-Business (Institutional) Benefits

| Benefit | Why It Matters |
|---|---|
| **Verification independent of the system** | An ERP records what people enter. P11 is the only mechanism that tests whether the entry was true — the difference between a controlled organisation and a well-documented one |
| **Segregation of duties made physical** | An auditor who counts but cannot adjust is what makes SOD-05 and SOD-12 real rather than configured |
| **Evidence that survives dispute** | Geo- and time-stamped photographs bound to observations, with an acknowledged report, settle disputes that would otherwise be one word against another |
| **Auditee fairness** | The auditee sees and signs the report on site; findings are not raised behind their back |
| **Comparability across 51+ sites** | Standard versioned checklists produce data, not anecdote — the basis for improving the network rather than individual branches |
| **Certification audit readiness** | An external auditor can be shown clause coverage, evidence and closure without a compilation exercise |
| **Bengali working language** | Branch staff read the report they sign; an English-only audit report signed by a Bengali-speaking manager is not an acknowledgement |

---

## 8. Journeys & State Models

### 8.1 The Audit — from assignment to acknowledged closure

```
   M23 SCHEDULES AND ASSIGNS THE AUDIT
        │  site · type · scope · checklist version
   ┌────▼──────────────────────────────────────┐
   │  PRIMED TO DEVICE                          │
   │   ▸ checklist (versioned)                  │
   │   ▸ open CAPAs due for verification        │
   │   ▸ registers to verify AGAINST — but      │
   │     ✖ NOT expected quantities or balances  │
   └────┬──────────────────────────────────────┘
        │ auditor travels; connectivity irrelevant from here
   ┌────▼──────────────────────────────────────┐
   │  EXECUTE OFFLINE                           │
   │   ▸ observations against clauses           │
   │   ▸ evidence: photo + GPS + timestamp      │
   │   ▸ BLIND counts: cash · stock · equipment │
   │   ▸ facility and safety verification       │
   │   ▸ CAPA verification from prior audits    │
   └────┬──────────────────────────────────────┘
        │ non-conformity observed
   ┌────▼──────────────────────────────────────┐
   │  FINDING RAISED ON DEVICE                  │
   │   classification · severity · clause ·     │
   │   evidence · OWNER · DUE DATE              │
   │   ▸ repeat finding? → severity escalated   │
   └────┬──────────────────────────────────────┘
        │
   ┌────▼──────────────────────────────────────┐
   │  REPORT GENERATED ON DEVICE                │
   └────┬──────────────────────────────────────┘
        │
   ┌────▼──────────────────────────────────────┐
   │  AUDITEE ACKNOWLEDGEMENT — signed on site  │
   │   signature bound to the report hash       │
   │   refusal recorded with reason if withheld │
   └────┬──────────────────────────────────────┘
        │ audit cannot close without this
   ┌────▼──────────────────────────────────────┐
   │  SYNC → M23                                │
   │   ▸ audit + observations + evidence        │
   │   ▸ findings → CAPAs with owners and dates │
   │   ▸ counts → M15 · M45 · M47 · M19         │
   │     for VARIANCE COMPUTATION there          │
   └────┬──────────────────────────────────────┘
        │
   ┌────▼──────────────────────────────────────┐
   │  CAPA WORKED BY ITS OWNER (M23)            │
   │  → verified at the next audit (FR-POR-320) │
   └───────────────────────────────────────────┘
```

### 8.2 The Blind Count — verification, not confirmation

```
   AUDITOR ARRIVES AT THE SITE
        │
   ┌────▼──────────────────────────────────────────┐
   │  DEVICE HOLDS: what to count                   │
   │  DEVICE DOES NOT HOLD: what it should be       │
   │  ✖ expected quantity ✖ system cash balance     │
   │  ✖ expected equipment list                     │
   │  (enforced by NOT SHIPPING the data — T-04)    │
   └────┬──────────────────────────────────────────┘
        │
   ┌────▼──────────────┐
   │  COUNT ENTERED     │   by scan where possible; counter identity per line
   └────┬──────────────┘
        │ submitted — irreversible
   ┌────▼──────────────────────────────────────────┐
   │  VARIANCE COMPUTED BY THE OWNING MODULE        │
   │   stock → M15 · cash → M19/M04 ·               │
   │   equipment → M45 · safety → M47               │
   └────┬──────────────────────────────────────────┘
        │
   ┌────▼──────────────────────────────────────────┐
   │  VARIANCE RETURNED TO THE AUDITOR              │
   │  (after submission, on sync)                   │
   └────┬──────────────────────────────────────────┘
        │ variance above threshold
   ┌────▼──────────────────────────────────────────┐
   │  FINDING RAISED · ADJUSTMENT APPROVED          │
   │  ELSEWHERE — by someone who did not count      │
   │  (SOD-05 · SOD-12)                              │
   └───────────────────────────────────────────────┘

   ✖ THE AUDITOR NEVER ADJUSTS ANYTHING
```

---

## 9. Portal Rules

| ID | Rule | Class | Owner |
|---|---|:--:|---|
| PRU-P11-01 | The application offers no path to adjust stock, adjust cash, close a CAPA or alter any register; submission is the only action | **H** | Quality Manager |
| PRU-P11-02 | **SOD-05 enforced:** the auditor who performs a count does not approve the adjustment arising from it | **H** | CFO |
| PRU-P11-03 | **SOD-12 enforced:** the auditor who counts cash does not reconcile the cash book | **H** | CFO |
| PRU-P11-04 | Counts are blind — expected quantities and balances are not present in the device payload before submission | **H** | Quality Manager |
| PRU-P11-05 | A count, once submitted, cannot be edited; a correction is a new count with a reason | **H** | Quality Manager |
| PRU-P11-06 | A non-conforming observation requires a note and evidence | **H** | Quality Manager |
| PRU-P11-07 | A finding requires classification, severity, clause linkage, owner and due date before the audit can close | **H** | Quality Manager |
| PRU-P11-08 | An audit cannot close without the auditee's acknowledgement, or a recorded refusal with a reason | **H** | Quality Manager |
| PRU-P11-09 | The auditee's signature binds to the report content hash | **H** | Quality Manager |
| PRU-P11-10 | The checklist version is recorded on every audit and cannot change mid-audit | **H** | Quality Manager |
| PRU-P11-11 | No feature requires connectivity that an auditor cannot complete offline (**PS-08**) | **H** | CTO |
| PRU-P11-12 | Every observation, finding, count and evidence capture is written to the journal before the UI acknowledges it (AS-13) | **H** | CTO |
| PRU-P11-13 | An auditor cannot audit a site or a function where they hold operational responsibility | **H** | Quality Manager |
| PRU-P11-14 | A repeat finding at the same site is escalated in severity automatically | **C** | Quality Manager |
| PRU-P11-15 | An out-of-service instrument found in use is raised as a finding and notified to M45 and M23 immediately on sync | **H** | Quality Manager |
| PRU-P11-16 | Audit data and evidence purge from the device after sync plus the retention window, and immediately on logout | **H** | CTO |
| PRU-P11-17 | Variance, severity escalation and CAPA due-date rules are computed by their owning module (**PS-11**) | **H** | CTO |
| PRU-P11-18 | The report the auditee signs renders in the language the auditee reads | **H** | Quality Manager |

---

## 10. Data, Caching & State Model

### 10.1 Local Store — permitted, bounded, purged

| Object | Purpose | Retention | Reconstructible From |
|---|---|---|---|
| **Journal entries (pending)** | Durability of unsynced observations, findings, counts and evidence — **the only locally authoritative data** | Until synced and acknowledged | Nothing |
| Assigned audits and scope | Offline execution | Audit period + 7 days | M23 |
| Checklist (versioned) | Offline execution | Until version change | M23 |
| Open CAPAs for verification | On-site verification | Audit period | M23 |
| Register lists to verify against | What to count — **never the expected values** | Audit period | M15, M45, M47 |
| Media queue | Evidence pending upload | Until uploaded, bounded | — |
| Generated report and signature | Acknowledgement evidence | Until synced + window | M23 / M24 |
| Session context | Time-boxed offline session | Per M29 policy | M29 |

### 10.2 Never Held Locally

| Item | Reason |
|---|---|
| **Expected stock quantities, cash balances or equipment counts** | PRU-P11-04 — blindness is enforced by absence, not by hiding |
| Another auditor's audits | Assignment scope |
| Customer personal data | Not required for an operational audit |
| Adjustment, approval or closure capability | PRU-P11-01 |
| Variance, severity or due-date logic | PRU-P11-17 |

### 10.3 Referenced Entities

| Entity | Owned By | Access |
|---|---|---|
| `fix.audit`, `fix.audit.checklist`, `fix.finding`, `fix.capa` | **M23** | Read programme and checklist; submit audit, findings and CAPAs |
| `fix.stock.count`, `fix.stock.count.line` | **M15** | Submit count; receive variance after submission |
| `fix.equipment.audit`, `fix.equipment.audit.line` | **M45** | Submit verification; receive variance |
| `fix.calibration.record`, fitness state | **M45** | Read status for verification |
| `fix.site.safety.equipment`, `fix.site.compliance` | **M47** | Read register; submit inspection |
| `fix.site`, `fix.site.condition.assessment` | **M47** | Submit condition assessment |
| Cash position and count | **M19 / M04** | Submit count; receive variance |
| `fix.marketplace.seller`, platform standards | **M12** | Read standards; submit audit |
| `fix.employee` | M21 | Read for finding ownership assignment |
| `fix.document` | M24 | Upload evidence and report under retention |
| `fix.risk`, compliance register | M60 | Findings feed the register |
| `fix.hse.inspection` | M59 | Safety findings routed |

---

## 11. Automations & Notifications

| ID | Trigger | Action | Failure Behaviour |
|---|---|---|---|
| AUT-P11-01 | Audit assigned by M23 | Push to the auditor and prime checklist, scope, open CAPAs and register lists — **without expected values** | Appears on next sync; priming retried |
| AUT-P11-02 | Non-conforming observation recorded without a note or evidence | Block progression and name what is required | Hard block |
| AUT-P11-03 | Finding raised | Check the site's history and, where the same finding exists, flag it as a repeat and escalate severity | Raise without the flag; log the evaluation failure |
| AUT-P11-04 | Audit closure attempted | Evaluate the closure gate — all items answered, findings complete with owner and due date, auditee acknowledgement captured — and name what is missing | Audit stays open |
| AUT-P11-05 | Auditee declines to acknowledge | Record the refusal with a reason and notify the Quality Manager; allow closure with the refusal recorded | Refusal recorded; audit closes |
| AUT-P11-06 | Audit synced | Create findings and CAPAs in M23 with owners and due dates; route counts to M15, M45, M47 and M19 for variance computation | Queued; replayed on sync; nothing discarded |
| AUT-P11-07 | Variance computed by an owning module | Return it to the auditor and, above threshold, raise a finding automatically | Variance visible on next sync |
| AUT-P11-08 | Out-of-service instrument found in use | Raise a finding, notify M45 and M23 immediately on sync, and flag the affected QC records for M45's retrospective assessment | Escalate; never suppressed |
| AUT-P11-09 | Safety equipment found lapsed or missing | Raise a finding and notify M47 and M59 | Escalate |
| AUT-P11-10 | Statutory document found expired | Raise a finding and notify M47, which raises its operating-risk exception (M47 AUT-FAC-03) | Escalate |
| AUT-P11-11 | CAPA verification recorded as failed | Reopen the CAPA in M23 with the fresh evidence and escalate to the CAPA owner's manager | Escalate |
| AUT-P11-12 | Connectivity restored | Replay the journal in order, upload evidence resumably, present the sync report | Retry with backoff; pending count visible |
| AUT-P11-13 | Journal pending beyond threshold | Warn the auditor and notify the Quality Manager that a device holds unsynced audit records | Escalate; never discard |
| AUT-P11-14 | Audit plan date approaches with the audit unstarted | Notify the auditor and the Quality Manager | Notify only |

---

## 12. Module Interfaces

### 12.1 Modules P11 Consumes

| Module | What | Mechanism |
|---|---|---|
| M29 Identity & Security | Authentication, offline session, device binding, remote wipe | OIDC via gateway |
| M28 Integration Platform | Sync endpoint, gateway | Gateway |
| **M23 Quality Management** | **Audit programme, versioned checklists, finding taxonomy, CAPA model, open CAPAs for verification** | REST, primed |
| **M15 Inventory** | What to count — **never expected quantities**; variance returned after submission | REST |
| **M45 Enterprise Assets** | Equipment register to verify against, calibration and fitness status | REST |
| **M47 Facility** | Safety equipment register, statutory documents, site condition rubric | REST |
| M19 / M04 | Cash count scope; variance returned after submission | REST |
| M12 Marketplace | Seller platform standards for seller audits | REST |
| M21 Core HR | Employee records for finding ownership | REST |
| M24 Documents | Evidence and report storage under retention | REST (resumable) |
| M59 Health & Safety | Safety inspection requirements | REST |
| M60 GRC | Compliance register linkage | REST |
| M65 Localisation | Bengali and English bundles | Build-time + REST |

### 12.2 What P11 Writes Back

| Target | What | Mechanism |
|---|---|---|
| **M23** | Completed audit, observations, evidence, **findings and generated CAPAs**, auditee acknowledgement | Journal replay (idempotent) |
| **M15** | Blind stock counts with counter identity per line | Journal replay |
| **M45** | Equipment verification, items not found, calibration exceptions | Journal replay |
| **M47** | Safety equipment inspection, statutory document verification, site condition assessment | Journal replay |
| M19 / M04 | Blind cash counts | Journal replay |
| M12 | Marketplace seller audit results | Journal replay |
| M59 | Safety findings requiring HSE attention | Journal replay |
| M60 | Findings feeding the compliance and risk register | Journal replay |
| M24 | Evidence media, generated reports, signatures | Resumable upload |
| M25 / M62 | Audit completion, evidence attachment, CAPA cycle time, repeat findings | Event stream (queued) |

### 12.3 Events P11 Consumes

| Event | Source | Effect in P11 |
|---|---|---|
| `audit.assigned` / `audit.rescheduled` | M23 | Add or update the auditor's list; prime scope |
| `audit.checklist_version_published` | M23 | Update the checklist for audits not yet started |
| `capa.due_for_verification` | M23 | Add to the site's verification list |
| `stock.count_variance_computed` | M15 | Return variance to the auditor; raise a finding above threshold |
| `equipment.audit_variance_computed` | M45 | Return variance; raise a finding |
| `equipment.out_of_service` | M45 | Flag the instrument for verification attention at the site |
| `site.compliance_expired` | M47 | Add to the site's verification list |

### 12.4 External Integrations

| INT ID | System | Direction | Purpose |
|---|---|---|---|
| INT-P11-01 | Device camera and GPS | Local | Evidence capture with EXIF GPS and timestamp |
| INT-P11-02 | Bluetooth barcode scanners | Local | Blind stock and equipment counting at volume |
| INT-P11-03 | Firebase Cloud Messaging | Inbound | Audit assignment and CAPA verification prompts |
| INT-P11-04 | Mobile printers, where deployed | Outbound | On-site printed audit report for the auditee |

### 12.5 API Surface Consumed

| Endpoint | Method | Purpose | Owner |
|---|---|---|---|
| `/api/v1/sync/pull` | GET | Prime audits, checklists, CAPAs and register lists | M28 orchestrated |
| `/api/v1/sync/push` | POST | **Ordered, idempotent journal replay** — the P02 endpoint | M28 orchestrated |
| `/api/v1/audits` | GET | Assigned audits with scope and checklist version | M23 |
| `/api/v1/audits/{id}` | POST | Submit the completed audit with observations and acknowledgement | M23 |
| `/api/v1/findings` | POST | Raise findings with classification, clause, owner and due date | M23 |
| `/api/v1/capa/{id}/verify` | POST | Record CAPA verification with fresh evidence | M23 |
| `/api/v1/stock/counts` | POST | **Blind stock count submission** | M15 |
| `/api/v1/equipment/audits` | POST | **Blind equipment verification** | M45 |
| `/api/v1/equipment/{id}/fitness` | GET | Calibration status for on-site verification | M45 |
| `/api/v1/sites/{id}/safety-equipment` | GET/POST | Safety register and inspection submission | M47 |
| `/api/v1/sites/{id}/compliance` | GET | Statutory documents to verify | M47 |
| `/api/v1/cash/counts` | POST | **Blind cash count submission** | M19 / M04 |
| `/api/v1/mp/sellers/{id}/audit` | POST | Marketplace seller audit result | M12 |
| `/api/v1/documents/upload` | POST | Resumable evidence and report upload | M24 |

---

## 13. Roles & Permissions

| Role | Access | Scope |
|---|---|---|
| **R32 Quality Manager / ISO Coordinator** | C R U D A | **All branches** — the audit programme owner; executes, reviews and manages findings |
| **R05 Operations Director** | C R U A | **All branches** — executes and reviews audits; operational oversight |
| **R06 Branch Manager** | C R U | **Own branch** — self-checks between formal audits; **cannot audit their own branch as an independent auditor** (PRU-P11-13) |

> **Per `05-04` §2, P11 access is held by R05, R06 and R32 only.** No external party has access.
> A branch manager may run standard checks at their own branch as a self-check; those results are
> marked as self-assessment and do not satisfy the independent audit programme.

**Independence rule.** PRU-P11-13 prevents an auditor auditing a site or function where they
hold operational responsibility. The application evaluates this at assignment and at execution,
and a self-assessment is labelled as such throughout — in the report, in M23 and in every
analytic.

**Field-level restrictions.** Expected quantities, cash balances and equipment counts are
**absent from the device payload** before submission (T-04). Customer personal data is not
present at all. `unit_cost` and `margin` appear only where a finding's materiality requires a
value, and only for roles permitted them under `05-04` §5.

**Segregation of duties.** **SOD-05** (adjust inventory + perform the count justifying it) and
**SOD-12** (handle cash + reconcile the cash book) are enforced structurally: P11 offers no
adjustment or reconciliation capability at all.

---

## 14. Analytics & Instrumentation

| Instrumentation | What Is Captured | Consumer |
|---|---|---|
| **Audit plan completion** | Scheduled versus completed audits, by site, type and period — the `04-00` 100% KPI | M23, M25 |
| **Mobile versus paper** | Audits completed on device — the `04-00` 100% KPI | M23 |
| **Finding-to-CAPA cycle time** | Finding raised to CAPA created, owned and dated — the `04-00` < 5 day KPI | M23, M25 |
| **Evidence attachment** | Findings with evidence attached — the `04-00` 100% KPI | M23 |
| Finding distribution | Findings by clause, severity, site, process and repeat status | M23, M60 |
| **Repeat findings** | The same finding recurring at a site — the measure of whether CAPA works | M23 — **the improvement signal** |
| Count variance | Stock, cash and equipment variance found by independent audit versus by self-count | M15, M45, M19 |
| Calibration exceptions found in the field | Out-of-service instruments found in use | **M45**, M23 |
| Safety lapses found | Safety equipment and statutory document lapses by site | **M47**, M59 |
| Audit duration | Time per audit type; time per section — identifies checklist bloat | M23 |
| Acknowledgement rate | Reports acknowledged on site versus refused | M23 |
| Sync health | Success, pending, failures per auditor per audit | M30 |
| Marketplace seller audits | Sellers audited, findings raised, standards parity with owned operations | M12, M23 |

---

## 15. KPIs

| KPI ID | Metric | Baseline | W6 Target | W8 Target |
|---|---|---|---|---|
| — | **Audit plan completion** | unmeasured | 95% | **100%** |
| — | **Audits completed on mobile (vs paper)** | 0% | 95% | **100%** |
| — | **Finding-to-CAPA cycle time** | unmeasured | < 8 days | **< 5 days** |
| — | **Evidence attached to findings** | ~0% | 95% | **100%** |
| — | Audits closed with auditee acknowledgement on site | 0% | 92% | **> 98%** |
| — | Repeat findings as a share of total findings | unmeasured | baselined | **falling trend** |
| — | CAPAs verified at the next audit | 0% | 85% | **> 95%** |
| — | Blind counts submitted without prior sight of expected values | n/a | **100%** | **100%** |
| — | Out-of-service instruments found in use | unknown | baselined | **0** |
| — | Safety equipment lapses found per site visit | unknown | baselined | **falling trend** |
| — | Audits completed fully offline without data loss | n/a | **100%** | **100%** |
| — | Independent audits performed by a party with operational responsibility for the site | n/a | **0** | **0** |
| — | Bengali and English report completeness | n/a | **100%** | **100%** |
| **KPI-042** *(supported)* | Inventory accuracy — independently verified | 75% | 96% | **98%** |

> **Register note.** The first four metrics are adopted verbatim from `04-00` §P11. P11 has
> **no KPI-0nn identifiers allocated**; all thirteen unnumbered metrics require allocation in
> `06-02` (not yet issued). Recorded as an audit action. KPI-042 is owned by M15 and is shown as
> *supported*.

---

## 16. Delivery

### 16.1 Technology & Layer Allocation

| Layer | Component | Coverage |
|---|---|---|
| L5 | **Flutter application** — audit execution, observations, evidence, findings and CAPA, the five check types, report generation and acknowledgement | 74% |
| L5 | Offline journal and sync — **the P02 implementation, reused (third reuse)** | 12% |
| L2 | OCA `management-system` audit and CAPA models on the server side (M23-owned) | 8% |
| L4 | Local encrypted store, resumable media transfer, scanner and camera integration | 6% |

> **Reuse position.** This is the **third reuse** of the P02 offline journal, after P09. The
> 12% shown is integration, not reconstruction. Three offline applications on one engine is the
> single clearest structural efficiency in the portal suite, and it is why P11 costs 16 PW rather
> than 30.

### 16.2 Custom Development

| CD ID | Component | Type | Effort |
|---|---|---|---|
| **CD-212** | `p11_auditor_app` — assigned audits and versioned checklist execution, observation and evidence capture, finding creation with automatic CAPA and repeat detection, CAPA verification, **blind cash, stock, equipment and facility checks**, calibration verification, 5S and process observation, marketplace seller audit, on-device report generation and auditee acknowledgement with hash binding, offline journal integration reusing P02 | Flutter application | 16 PW |

> **CD register.** One ID, **CD-212**, claimed following CD-211 (P10). All CD IDs remain
> provisional pending the unified CD register required by audit finding M-01 in `02-05`.

### 16.3 Sequencing

| Prerequisite | Reason |
|---|---|
| **M23 Quality Management System** | The audit programme, checklists, finding taxonomy and CAPA model. **W5 — P11 and M23 are delivered together** |
| **P02** | The offline journal and sync engine, reused. W2 — proven twice before P11 uses it |
| M29 Identity & Security | Auditor identity, offline session, device binding, remote wipe |
| M28 Integration Platform | The sync endpoint |
| **M15 Inventory** | Blind stock counts (W2) — the count model already exists |
| **M45 Enterprise Assets** | Equipment verification and calibration status. **W5 — same wave; P11 is the surface for M45's FR-EAM-038** |
| M19 / M04 | Cash count scope (W1–W3) |
| M24 Documents | Evidence and report storage under retention |
| M21 Core HR | Employee records for finding ownership (W5) |
| **M47 Facility** | Safety equipment and statutory document registers. **W7 — facility checks are added in W7** |
| M12 Marketplace | Seller platform standards. **W7 — seller audits added in W7** |
| M59 / M60 | HSE and compliance register linkage (W6) |

**Phasing within the application.** W5 ships audit execution, findings and CAPA, cash spot
checks, inventory spot counts and equipment verification with calibration. W7 adds facility and
safety checks and marketplace seller audits.

### 16.4 Rollout

| Stage | Scope | Wave |
|---|---|---|
| Pilot | 4 auditors across 6 branches, including one district branch on poor connectivity | W5, month 20 |
| Quality team | All quality auditors | W5, months 21–22 |
| Branch self-check | Branch managers, for self-assessment between formal audits | W6 |
| Facility and marketplace | Added with M47 and M12 | W7 |

> **Rollout position.** The pilot must include a district branch on poor connectivity, for the
> same reason as P02: the offline requirement is the one that determines whether the application
> is used or worked around. **Paper audits stop at cutover** — running both produces neither the
> data nor the discipline.

---

## 17. Acceptance Criteria

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | A complete audit — observations, evidence, findings, counts, report and acknowledgement — executes fully offline with no data loss | Scripted full-day offline audit at three sites |
| AC-02 | Expected quantities, cash balances and equipment counts are **absent from the device payload** before submission | Payload inspection on a primed device |
| AC-03 | A submitted count cannot be edited; a correction is a new count with a reason | Negative test |
| AC-04 | The application offers no path to adjust stock, adjust cash, close a CAPA or alter any register | Negative test across all four, including direct API attempts |
| AC-05 | A non-conforming observation cannot be recorded without a note and evidence | Negative test |
| AC-06 | A finding cannot be created without classification, severity, clause, owner and due date | Negative test |
| AC-07 | A CAPA is created in M23 from a finding, with owner and due date, within one sync | Scripted scenario with M23 |
| AC-08 | An audit cannot close without auditee acknowledgement or a recorded refusal with a reason | Negative test |
| AC-09 | The auditee's signature binds to the report content hash, and the on-device report matches the M23 record after sync | Hash verification test |
| AC-10 | A repeat finding at the same site is detected and escalated in severity automatically | Scripted repeat scenario |
| AC-11 | An out-of-service instrument found in use raises a finding and notifies M45 and M23 on sync | Scripted scenario with M45 |
| AC-12 | A lapsed safety item or expired statutory document raises a finding and notifies M47 | Scripted scenario with M47 |
| AC-13 | An auditor cannot conduct an independent audit of a site where they hold operational responsibility; a branch manager's own-branch check is labelled self-assessment throughout | Negative test and label audit |
| AC-14 | No journal entry is lost across app termination, device restart, storage pressure or forced update | Fault-injection suite |
| AC-15 | Replay after partial failure produces exactly one audit, one set of findings and one count | Idempotency test |
| AC-16 | Evidence photographs carry correct GPS and timestamps, bind to the specific observation, and upload resumably | Evidence-integrity test |
| AC-17 | The checklist version is recorded on every audit and cannot change mid-audit | Scripted version-change scenario |
| AC-18 | Audit data and evidence purge from the device after sync plus the retention window, and immediately on logout | Storage audit |
| AC-19 | Every screen, checklist and report renders in Bengali and English, and the auditee's report is in their language | Translation coverage report |
| AC-20 | Audit plan completion reaches 100% and finding-to-CAPA cycle time falls below 5 days | Six consecutive monthly reports |
| AC-21 | An external ISO surveillance audit accepts the internal audit programme evidence produced from P11 and M23 | Certification body report |
| AC-22 | Quality Manager, Operations Director and two branch managers sign off UAT, conducted in Bengali at a live branch | Signed UAT record |

**Definition of done:** the twelve cross-portal standards in `04-00` §3, PS-08 offline
capability, plus the 22 criteria above.

---

## 18. Open Questions

| # | Question | Owner | Needed By |
|---|---|---|---|
| Q-01 | What is the audit programme — how many audits per site per year, of what types, performed by whom? | Quality Manager | **W5 minus 4 months** |
| Q-02 | How many independent auditors exist, and is the function resourced for 51+ sites at the planned frequency? A programme that cannot be executed is worse than none | Quality Manager / Operations Director | **W5 minus 4 months** |
| Q-03 | Do the ISO 9001 checklists exist today, and in what form? They must be versioned quality documents in M23 before P11 can execute them | Quality Manager | **W5 design** |
| Q-04 | Is a branch manager's own-branch check acceptable as evidence for any purpose, or is it purely developmental? | Quality Manager | W5 design |
| Q-05 | What variance thresholds trigger an automatic finding on cash, stock and equipment counts? | CFO / Quality Manager / Inventory Manager | W5 design |
| Q-06 | Is the auditor device company-issued? Blind counting and remote wipe are unenforceable on BYOD | Quality Manager / CTO | W5 minus 3 months |
| Q-07 | Who owns a finding by default where the auditor cannot identify an owner on site? | Quality Manager / Operations Director | W5 design |
| Q-08 | Is a printed report required for the auditee, or is a signed digital report with an emailed copy sufficient? | Quality Manager | W5 build |
| Q-09 | What retention applies to audit evidence, given ISO and brand-audit requirements? | Quality Manager / Legal | W5 design |
| Q-10 | Are marketplace seller audits conducted at the seller's premises, and what access rights does the seller agreement grant? *(Depends on P07 Q-...)* | CCO / Legal / Quality Manager | W7 design |
| Q-11 | Does the certification body accept mobile-captured evidence and digital acknowledgement signatures? | Quality Manager / certification body | **W5 minus 3 months** |
| Q-12 | Are facility and safety checks performed by quality auditors, or by a facilities function with its own users? | Quality Manager / Branch Operations Lead | W7 design |

---

## 19. References

**Internal**
`04_Portals_and_Applications/04-00_Portal_Suite_Overview.md` §P11, §1, §3 PS-01…PS-12
(**PS-08**), §4 ·
`P02_Technician_Mobile_Application.md` §6 (**the journal and sync engine, third reuse**) ·
`P03_Admin_Operations_Portal.md` (Quality Console — findings and CAPA management) ·
`P07_Marketplace_Seller_Portal_and_Application.md` (seller standards audited here) ·
`P09_Logistics_and_Rider_Application.md` (second reuse of the journal) ·
`03_Modules/E_Supply_Chain_and_Inventory/M15_Spare_Parts_and_Inventory_Management.md`
§5.7 FR-INV-048 (blind counting), §9 BRU-INV-10 (SOD-05) ·
`03_Modules/F_Asset_Equipment_and_Facilities/M45_Enterprise_Asset_and_Test_Equipment.md`
§5.5 FR-EAM-038 (physical verification), §5.3 (calibration and fitness), §13 (SoD) ·
`03_Modules/F_Asset_Equipment_and_Facilities/M47_Facility_Branch_Infrastructure_and_Workplace.md`
§5.6 FR-FAC-040 (safety equipment), §5.3 (statutory documents), §11 AUT-FAC-03 ·
`02_Architecture/02-01_ERP_Module_Architecture_and_System_Map.md` §10 (**AS-13**, AS-14) ·
`05_Cross_Cutting_Specifications/05-01_Feature_and_Function_Register.md` §4 ·
`05_Cross_Cutting_Specifications/05-04_Role_Permission_and_Access_Matrix.md`
§1 (R05, R06, R32), §2, §5, §6 **SOD-05** and **SOD-12**

**Workspace evidence**
`ERP system for 1000 fix/1000FiX_ERP_System_Comprehensive_BRD.md` BR-QMS-001, BR-QMS-002,
BR-QMS-003, **BR-QMS-004**, BR-INV-013, BR-FIN-013 ·
`1000FiX_Services_Company_Profile.md` §Quality & Certification (only ISO-certified IT service
provider in Bangladesh), §Quality Assurance Process

**External benchmark**
[ISO 9001 audit and compliance software — on-site collection on phone or tablet without connectivity, syncing automatically](https://goaudits.com/blog/iso-9001-software/) ·
[Mobile audit and inspection — full internal audit cycle from scheduling to finding capture, corrective action generation and close-out](https://teammateapp.com/features/audit-inspection/) ·
[Quality control inspection software — offline checklists with photos and notes stored locally](https://goaudits.com/quality/) ·
[ISO 9001 QMS internal audit checklist and app — offline access and photo evidence](https://www.inspectly360.com/checklists/professional-services/iso-9001-qms-internal-audit-checklist/) ·
[ISO 9001 audit checklist app](https://www.inspectly360.com/checklists/iso-standards/iso-9001-audit-checklist/) ·
[Audit management software — mobile, offline and corrective action tracking](https://digital-checklist.com/audit-app) ·
ISO 9001:2015 clause 9.2 — internal audit

---

*Portal P11 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
