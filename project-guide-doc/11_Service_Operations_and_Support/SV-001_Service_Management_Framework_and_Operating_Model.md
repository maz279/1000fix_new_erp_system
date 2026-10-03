---
id: SV-001
title: Service Management Framework and Operating Model
category: 11 — Service Operations & Support
code: SV
project: 1000FiX ERP System v2.0
version: 1.2
date: 2026-08-19
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Head of IT Service Management
approver: Chief Technology Officer, endorsed by the ERP Steering Committee
standards_basis: >
  ISO/IEC 20000-1:2018 + Amd 1:2024 (climate action changes, published 2024-02-23) — service
  management system requirements, clauses 4–10, adopted as the conformance frame and not as a
  certification target · ITIL 4 practice model — twelve of thirty-four practices adopted, the
  remainder deferred by named decision · ISO 9001:2015 cl. 8.5.1 controlled provision of service
  and cl. 10.2 nonconformity and corrective action · Google SRE service-ownership and
  error-budget practice, adopted for the platform tier only
traces_to: >
  PGD-000 SV-001 row (◐ OP-001) · AUDIT-017 OP-06, OP-07, OP-09, OP-12, OP-16, OP-26 ·
  OP-001 §4.1–§4.12 (adopted by citation) · M66 §3.1, §5, §9, §16.3, §18 Q-02/Q-03/Q-04 ·
  05-06 §2 NFR-006/045, §7 NFR-091, OPS-01…08 · SP-031 §1–§12 · MD-028 · NT-021 §2.1
depends_on: >
  GV-002 (issued) · GV-007 (issued) · GV-009 (issued) · RL-001 (issued) · QA-010 (issued) ·
  SC-011 (issued) · PE-001…PE-009 (ALL NINE ISSUED — re-enumerated 2026-08-19 02:15 (+06);
  PE-007, PE-008 and PE-009 were issued by a concurrent session during this document's authoring
  window and this front matter is corrected accordingly — see §0) ·
  OP-001, OP-013, OP-016 (content, issued) · SP-031 (content, issued) ·
  SV-002, SV-003, SV-004, SV-005, SV-006 (this category)
verified_on: 2026-08-19
enumeration_timestamp: 2026-08-19 02:15 (+06) — supersedes the 01:53 enumeration used at first draft
rule_prefix: SMF — verified to return zero occurrences in identifier form across all 763 markdown files of the workspace before allocation, at 2026-08-19 02:15 (+06); re-verified against the 786-file baseline at 02:56 (+06). Conforms to RR-002 IDC-08
priority: P0
needed_by: W1
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# SV-001 — Service Management Framework and Operating Model

### Category 11 · Code `SV` · Rule space `SMF` · ISO/IEC 20000-1:2018 + Amd 1:2024 · ITIL 4 · ISO 9001:2015 cl. 8.5.1

---

> **`PGD-000` states the gap this document fills:** *"`OP-001` defines support **tiering and routing
> content**. `M66` (Internal ITSM) is the owning module and audit **OP-06** records it **arrives at
> W6 for a support model needed at W1**."*
>
> That is accurate and it stops one step short of the decision. Sixteen `OP-*` files describe a
> support service in 500 KB of detail. **Not one of them can commit the programme to anything**,
> because content states what a service will do and cannot state that the service exists, who is
> accountable for it, what it is funded to be, or which of two irreconcilable dates the platform
> underneath it will arrive on. `AUDIT-017` put the position in one sentence — *"the programme has
> operational content and no operational capability"* — and this document is where the programme
> either acquires the capability or records that it has decided not to.
>
> **This document makes one ruling that costs money and one that costs nothing**, and both are in
> §7. Everything else exists to make those two defensible.

---

## 0. Baseline Movement During Authoring — Read This First

> **⚠ The estate moved while this document was being written, for the ninth recorded time.**
>
> This document was drafted against an enumeration taken at **2026-08-19 01:53 (+06)**, at which
> `PE-007`, `PE-008` and `PE-009` did not exist on disk. Re-enumerating at **2026-08-19 02:15 (+06)**
> returns **all nine `PE` documents issued**, together with `RL-002`…`RL-005`, `CH-001`…`CH-005`,
> `PGD-AUDIT-009` and `PGD-AUDIT-CAT-13` — **nineteen files written by concurrent sessions inside a
> twenty-two-minute window.**
>
> **Every claim of absence in this document has been re-verified against the 02:15 enumeration and
> corrected where it was falsified.** The corrections are material and are listed here rather than
> made silently, because a document that quietly changes its findings is a document whose findings
> cannot be audited.

| Claim as drafted at 01:53 | State at 02:15 | Where corrected |
|---|---|---|
| `PE-007` Backup and DR Design — **absent ⛔** | **Issued.** Designs the 3-2-1-1-0 backup realisation, WAL archiving, the immutable copy, restore verification, failover, the `Z4` recovery routes and a drill programme | §4.2 cl. 8.7.3 · §6.2 · §10 · §12 · §17 |
| `PE-008` Observability and Monitoring Design — **absent ⛔** | **Issued.** Defines eight SLOs with windows and error budgets, multi-window multi-burn-rate alerting, routing, alert discipline and dashboards | §4.2 cl. 8.7.2 / 9.1 · §6.2 · §10 · §11.2 · §12 · §17 |
| `PE-009` Configuration and Secrets Standard — **absent ⛔** | **Issued.** Designs the break-glass procedure `AUDIT-017` `OP-08` records as non-existent | §12 item 6 · §17 |
| *(not drafted — new)* | **`PE-008` §8.5 asserts a three-level severity model** and claims ownership of the space `OP-013` §4.1 owns as four levels | **§6.7 — new section, and finding `SMF-F-06`** |

> **What did not change.** The `M66` ruling in §7, the establishment in §8.4, and the paging gap in
> §7.7 are untouched: **no `PE` document provides a paging platform, and `PE-008` §1.1 and `PE-009`
> §1.2 both explicitly hand the on-call rota and escalation to `SV-*`.** The category's central
> problem is exactly where it was.

---

## 1. Purpose

This framework states **how the 1000FiX ERP platform is operated as a service** rather than as a
project deliverable: what a service is, who owns each one, which management practices the
programme runs, who is accountable for each, what happens at W1 when the module that was supposed
to provide the tooling has not been built, and what the service management system must produce as
evidence that it is working.

It exists because a platform is handed over exactly once, and the handover either lands on an
operating model that was designed in advance or it lands on the delivery team, who then run
support out of the same capacity that is supposed to be building Wave 2. Every ERP programme that
has slipped a wave for "stabilisation" slipped it here.

### 1.1 Scope

**In scope:**

| # | Covered |
|---|---|
| 1 | The **service management system** (SMS) — its boundary, its owner, its governing body and its evidence set (§4) |
| 2 | The **service portfolio**: what counts as a service, and the 21 services this platform actually offers (§5) |
| 3 | **Service ownership** — a named accountable owner per service, and what ownership obliges (§5.3) |
| 4 | The **practice set**: twelve ITIL 4 practices adopted, twenty-two deferred, each with a reason and a review point (§6) |
| 5 | The **W1–W5 ruling** — the `M66` split, its cost, and the interim capability that covers what is not moved (§7) |
| 6 | The **operating model**: functions, tiers, roles and the service management RACI (§8) |
| 7 | **Configuration and knowledge** — the CMDB the programme can afford and the one it cannot (§9) |
| 8 | The **seams**: which document owns what, across eleven neighbouring artefacts (§10) |
| 9 | **Continual improvement and measurement** — the service report, its cadence and its audience (§11) |
| 10 | An honest statement of **what cannot be evidenced today**, carried forward rather than buried (§12) |

**Explicitly out of scope:**

| Topic | Owned by | Why the boundary sits here |
|---|---|---|
| Tiering, routing, channels, response commitments, the population enumeration | [`OP-001`](../../project_content/17_Operations_Support_and_Runbooks/OP-001_Support_Model_Tiering_and_Routing_Content.md) | Adopted here **by citation and never restated** (`SMF-02`). `OP-001` is good, it is issued, and a second copy of a routing table is a second copy to maintain |
| The service levels the platform commits, and the internal service catalogue | `SV-002` | A framework says *how* service is managed; a service level agreement says *what is promised*, and promises need a separate approval |
| Executable procedures per component | `SV-003` | The framework governs runbooks; it is not one |
| Rota, paging platform, acknowledgement SLAs, severity-to-page mapping | `SV-004` | Paging is a build with a procurement decision behind it and needs its own document |
| Hypercare posture, duration, exit criteria and transition to BAU | `SV-005` | Hypercare is a temporary operating model; this is the permanent one it hands over to |
| Major incident command, problem management and post-incident review | `SV-006` | The practices are named here (§6) and specified there |
| The **platform incident severity scale** `Sev1`–`Sev4` | [`OP-013`](../../project_content/17_Operations_Support_and_Runbooks/OP-013_On_Call_Escalation_and_Handover_Content.md) §4.1 | It is canonical there, it is correct, and `AUDIT-017` `OP-04` exists because three other documents claimed it. **This one does not** |
| Release and deployment practice, freeze windows, versioning | [`RL-001`](../12_Release_Deployment_and_Transition/RL-001_Release_Management_and_Versioning_Policy.md) | ITIL 4 separates release from deployment and Category 12 owns both |
| Security incident response and breach assessment | [`SC-011`](../05_Security_Privacy_and_Compliance/SC-011_Security_Incident_Response_Plan.md) | `M66` `BRU-ITS-21` is explicit: the ITSM process makes **no** security classification decision |
| Defect severity `S1`–`S4`, triage and quality gates | [`QA-010`](../08_Quality_Engineering_and_Test/QA-010_Defect_Management_and_Quality_Gate_Standard.md) | A defect is not an incident; §6.4 states the only three relationships |
| Metrics, logs, traces, dashboards, alert rules, SLI definitions | `PE-008` **(absent)** | Named as a dependency in §12, not absorbed |
| Internal IT support for laptops, printers, mailboxes and software licences | `M66` FR-ITS-025…030 | **This framework operates the ERP platform**, not the company's desktop estate. §7.3 draws the line precisely, because it is the line the `M66` split turns on |

### 1.2 Intended audience

| Audience | What they use this document for |
|---|---|
| Chief Technology Officer | The two rulings in §7, their cost, and the accountability they create |
| Head of IT Service Management | The whole document; this is the charter of the function |
| ERP Steering Committee | §7's decision, §12's unfunded list, and the four decisions in §14 |
| Platform Engineering | Which practices bind them, what service ownership obliges (§5.3) |
| Support Lead | How `OP-001`'s model is governed, resourced and measured |
| Programme Office | The `GV-007` resource lines this framework requires, and the `GV-009` gate evidence it produces |
| Internal Audit and the Quality Manager | The ISO/IEC 20000-1 clause map (§4.2) and the `ISO 9001` cl. 8.5.1 evidence set |
| Vendor / implementation partner | What the Company will operate itself and what it will not, before the Statement of Work is signed (`CO-003`) |

---

## 2. Basis and Inputs

### 2.1 Standards conformance

| Standard | Clause / section | How this document conforms | Departure and rationale |
|---|---|---|---|
| **ISO/IEC 20000-1:2018 + Amd 1:2024** | §4 context, §5 leadership, §6 planning, §8.2 service portfolio, §8.3 relationship, §8.4 supply, §8.5 service design/build/transition, §8.6 resolution and fulfilment, §8.7 service assurance | §4 maps every clause to the artefact that satisfies it and names the seven that **cannot** be satisfied at W1 | **Conformance frame, not a certification target.** No certification is sought; the clause map exists so the gaps are enumerated rather than discovered. Recorded as `SV-001-D-01` |
| **ISO/IEC 20000-1 Amd 1:2024** | §4.1 (climate change relevance), §4.2 (interested-party climate requirements) | §4.4 records the determination the amendment requires, rather than omitting it silently | None. The amendment was published **2024-02-23** and the determination is a one-line obligation; omitting it is the cheapest possible nonconformity |
| **ITIL 4** | Thirty-four practices | §6 adopts twelve, defers twenty-two, and gives each deferral an owner and a review wave | **The full practice set is rejected.** `M66` §4 already made this argument — *"four processes done properly beats thirty-four done nominally"* — and this document extends it from four to twelve with the reasoning stated |
| **ISO 9001:2015** | cl. 8.5.1 controlled provision of service; cl. 10.2 nonconformity and corrective action | §11.3 routes every corrective action into `M23`, which is the Company's certified QMS | None. 1000FiX is **ISO 9001:2015 certified**; support has been outside the certified scope and §11.3 brings it in |
| **Google SRE practice** | Service ownership; SLI/SLO/error budget; toil budget | Adopted for the **platform tier only** (§5.3, §11.2), with `SV-002` owning the SLO numbers | **Error budgets do not govern release freezes here.** `RL-001` §7 owns freeze authority and it is derived from statutory and financial cycles, not from burn rate. Recorded as `SV-001-D-05` |

### 2.2 Source material relied on

| Source | Location | What it establishes |
|---|---|---|
| `OP-001` Support Model, Tiering and Routing | [`../../project_content/17_.../OP-001`](../../project_content/17_Operations_Support_and_Runbooks/OP-001_Support_Model_Tiering_and_Routing_Content.md) | Five tiers `T0`–`T4`, eight tier rules `TR-01`…`TR-08`, eighteen routing rows, the channel register, response commitments, the eleven external audiences, the §4.9 interim table |
| `OP-013` On-Call, Escalation and Handover | [`../../project_content/17_.../OP-013`](../../project_content/17_Operations_Support_and_Runbooks/OP-013_On_Call_Escalation_and_Handover_Content.md) | The canonical `Sev1`–`Sev4` scale (§4.1), the four-scale reconciliation (§4.2), the authority table (§4.8) |
| `OP-002`, `OP-016` | Same folder | Hypercare entry/exit and the post-incident review method — consumed by `SV-005` and `SV-006`, referenced here for the practice map |
| `M66` Internal IT Service Management | [`../../1000fix_ERP_Module/.../M66`](../../1000fix_ERP_Module/03_Modules/K_Platform_and_Technology/M66_Internal_IT_Service_Management.md) | §1 P2/W6 (Months 23–26); §3.1 twenty-six in-scope capabilities; §5 `FR-ITS-001`…`030`; §9 `BRU-ITS-01`…`22`; §15 sixteen KPIs; **§16.2 `CD-163` 9 PW / `CD-164` 5 PW**; **§16.3 the sequencing table and the "Why Wave 6 and not earlier" note** — the single most important input to §7; §18 Q-02, Q-03, Q-04 |
| `05-06` NFR set | [`../../1000fix_ERP_Module/.../05-06`](../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06_NonFunctional_Requirements_and_Standards.md) | §2 `NFR-006` 99.9% business hours, `NFR-045` 99.7% 24×7, `NFR-007` RPO 15 min / RTO 2 h, `NFR-050`…`052`; §7 `NFR-091` per-module runbook, `OPS-01`…`OPS-08` |
| `SP-031` SOP — IT Service Desk and Change Management | [`../../project_content/06_.../SP-031`](../../project_content/06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-031_SOP_IT_Service_Desk_and_Change_Management.md) | Three change classes, the CAB, §5.5 problem management, §7 authority limits, §10 fourteen controls, §12 `KPI-085`…`091` |
| `AUDIT-017` | [`../../project_content/_AUDIT/AUDIT-017`](../../project_content/_AUDIT/AUDIT-017_Category_17_OP_Content_Audit.md) | 26 findings, 22 open, 1 critical; §4 "what this category cannot evidence"; `R-01`…`R-10` |
| `PE-001`, `PE-002`, `PE-005`, `PE-006` | [`../10_Infrastructure_.../`](../10_Infrastructure_DevOps_and_Environments/) | The estate this framework operates: four availability targets and their scopes, twelve environments, the component inventory, the two operational models (cluster workloads and data hosts) |
| `GV-002`, `GV-007`, `GV-009` | [`../00_Programme_Governance_and_Control/`](../00_Programme_Governance_and_Control/) | The governance body this framework reports to, the resource plan its staffing lines belong in, the gate evidence it must produce |

**External sources, verified 2026-08-19:**

| Source | Class | What it establishes |
|---|:--:|---|
| ISO/IEC 20000-1:2018/Amd 1:2024, *Amendment 1: Climate action changes*, published 2024-02-23 — https://www.iso.org/standard/88434.html | P1 | The amendment adds a climate-change determination to §4.1 and an interested-party note to §4.2 of the SMS requirements |
| ISO 22301:2019/Amd 1:2024, published February 2024 — https://www.iso.org/standard/88412.html | P1 | The equivalent amendment to the business continuity standard `SV-006` §9 and `PE-007` will rely on |
| Google SRE Workbook, *Alerting on SLOs* — https://sre.google/workbook/alerting-on-slos/ | P3 | Multiwindow, multi-burn-rate alerting; error budget = 1 − SLO; the 2% / 5% / 10% budget-consumption tiers over 1 h / 6 h / 72 h windows |
| Atlassian Opsgenie end-of-life: end of sale 2025-06-04, full shutdown **2027-04-05**, non-migrated data deleted thereafter | P2 | Recorded here because it constrains `SV-004`'s procurement and falls **inside** this programme's 36-month horizon |

### 2.3 Audit findings this document closes or contributes to

| Finding | Source | Severity | How this document acts on it |
|---|---|:--:|---|
| **`OP-06`** — support model `P0` at W1, platform at W6 | `AUDIT-017` | HIGH | **Closed in specification.** §7.1 rules the `M66` split by dependency; §7.2 prices it at 9 PW; §7.4 specifies the interim for what is not moved. The finding closes on the Steering decision recorded in `GV-003`, not on this issue |
| **`OP-07`** — `NFR-091` requires 67 module runbooks and the register contains none | `AUDIT-017` | HIGH | **Ruled.** §6.5 and `SMF-14` choose the second of the two readings and hand the consequence to `SV-003` §5, which sizes it. `NFR-091` is *not* amended away |
| **`OP-09`** — the on-call rota needs ten people and has none | `AUDIT-017` | HIGH | **Contributes.** §8.4 places the ten rota positions and the T1 line into a single funded establishment table so `GV-007` can carry one number, not four. `SV-004` §5 owns the rota itself |
| **`OP-12`** — 94 open decisions and no `RF-006` to record them in | `AUDIT-017` | MEDIUM | **Contributes.** §14 and `SMF-24` route this category's decisions to `GV-003`, which **exists**, rather than to `RF-006`, which does not. The content estate's 94 remain blocked |
| **`OP-16`** — gate `G3` unachievable; no file can leave Draft | `AUDIT-017` | MEDIUM | **Contributes.** §6.6 adopts the `G3-on-build` convention `AUDIT-017` `R-06` recommends and makes it a rule (`SMF-19`), so runbooks are approved procedure by procedure |
| **`OP-26`** — "eleven external audiences" enumerated nowhere upstream | `AUDIT-017` | LOW | **Closed.** `SMF-03` adopts `OP-001` §4.1's derived enumeration as the programme's definitive one, which is the ratification `OP-001-OI-01` asked for |
| `M66` **Q-02**, **Q-03**, **Q-04** | `M66` §18 | — | Q-04 is answered by §7. Q-02 is converted from a question into a costed establishment (§8.4). Q-03 is handed to `SV-002`, which is the document that can answer it |
| **`QAA-10`** class — register wave assigned by traced module, not by consuming wave | `PGD-000` §0.5 | — | §7.1 is an instance of the same defect found in the *module* register rather than the document register, and §13 `SMF-F-01` records it as such |

### 2.4 The rule space

This document allocates the rule prefix **`SMF`**. It was verified at **2026-08-19 01:53 (+06)** to
return **zero occurrences in identifier form** (`SMF-nn`) across all **763** markdown files of the
workspace before allocation.

> **Why this paragraph exists at all.** The obvious prefix for this category is `SV`, and it is
> **already taken**: [`OP-013`](../../project_content/17_Operations_Support_and_Runbooks/OP-013_On_Call_Escalation_and_Handover_Content.md) §4.1 defines the severity rules `SV-01`…`SV-07`, and they are cited
> eleven times across the estate. A `SV-nn` rule in this category would collide with them **by digit
> count** — the identical failure mode the register records for `MG-nn`/`MG-001`, `MIG-nn`/`MIG-nnn`
> and `DM-nn`/`DM-nnn` (`MGA-04`). The candidate `RBK` was also rejected during allocation: it is
> [`MG-007`](../09_Data_Migration_and_Cutover/MG-007_Rollback_and_Fallback_Plan.md)'s rollback prefix, with 101 occurrences.
>
> **No document in Category 11 uses the form `SV-nn` for a rule.** Six distinct prefixes are
> allocated, one per document, each verified the same way: `SMF`, `PSL`, `RBS`, `OCP`, `HCT`, `MIM`.
> This is `RG-01` extended — register-first for every programme-wide identifier space — applied
> before the fact for once, rather than by an audit afterwards.

---

## 3. The Position, Enumerated

A framework that opens by describing an ideal operating model is a framework nobody checks against
reality. This one opens with the enumeration.

### 3.1 What the programme has

| Asset | Count | Enumerated |
|---|---:|---|
| `OP-*` operational content files | **16** | 2026-08-19 01:53 (+06) |
| Bytes of operational content | **~500 KB** | `AUDIT-017` §7, re-verified |
| Component runbooks (`OP-007`…`OP-011`) | **5** | §5 of each |
| Disaster recovery playbooks (`OP-012`) | **1** | — |
| Manual fallback procedures (`OP-014`) | **17** (13 P0 integration + 4 non-P0) | `OP-014` §4.4, §4.5 |
| Service desk macros (`OP-003`) | **68** | `AUDIT-017` `OP-17` |
| Incident communication templates (`OP-004`) | **26** | `AUDIT-017` `OP-17` |
| Distinct severity scales in the programme | **4** | `OP-013` §4.2 |
| Open decisions carried by the content (`OP-nnn-OI-nn`) | **94** | `AUDIT-017` `OP-12` |

### 3.2 What the programme does not have

| Capability the content assumes | Exists? | Recorded in |
|---|:--:|---|
| A paging platform of any kind | ✗ | `AUDIT-017` `OP-06`; `OP-013` OI-05 |
| A staffed on-call rota (needs 6 platform + 4 security) | ✗ — **zero identified members** | `AUDIT-017` `OP-09`; `OP-013` §4.3 |
| A break-glass path — vault route, sealed envelope, signatories, quarterly test | ✗ — **none of the five components** | `AUDIT-017` `OP-08`; `OP-009` OI-01 |
| The 38 standard access profiles | ✗ | `AUDIT-017` `OP-10`; `OP-015` §4.2 |
| A `dr` environment sized, costed or provisioned | ✗ | `AUDIT-017` `OP-02`; `PE-006` §5.4 |
| A T1 service desk (2 FTE at W1 rising to 6–8) | ✗ — unfunded | `OP-001` §4.7, OI-03 |
| An ITSM platform | ✗ until **W6**, twenty months after the model is needed | `M66` §1 |
| A CMDB, or any asset register | ✗ | `M66` §16.4 — *"there is no reliable IT asset register today"* |
| Printed fallback packs at 51+ branches | ✗ | `AUDIT-017` §4; `OP-014` OI-01 |
| Bengali counterparts for the four bilingual `OP` files | ✗ — **`OP-014` is `P0` and its Bengali version is the operational one** | `AUDIT-017` `OP-17` |

### 3.3 The sentence, and why it is not rhetoric

> *"The 1000FiX programme currently has operational content and no operational capability."*
> — `AUDIT-017` §7

Read as criticism it is unfair; the content is very good and was written to make exactly this
visible. Read as a **specification input** it is the most useful sentence in the estate, because it
separates two kinds of work that programmes routinely conflate:

| Kind of work | Who can do it | State |
|---|---|---|
| Describing the service | Content Design | **Done — 16 files, 500 KB** |
| **Establishing the service** | CTO, HR, Finance, Platform Engineering | **Not started** |

**Every one of the ten absences in §3.2 is in the second column.** No further content closes any of
them. What closes them is an establishment, a budget line, a procurement and a date — which is what
this category, and `SV-004` in particular, exists to produce.

> **`SMF-01`. No document in this category may assert that a control operates.** It may state that a
> control is *specified*, *designed*, *funded* or *operating*, and those are four different words
> with four different evidence tests (§4.3). A specification that reads as an operation is how
> `AUDIT-017` `OP-08` went unnoticed until an audit enumerated it.

---

## 4. The Service Management System

### 4.1 What the SMS is, and what it is not

The **service management system** is the set of policies, practices, people and records by which
the 1000FiX ERP platform is planned, delivered, operated and improved as a service. It is not a
piece of software. `M66` is the software that will *support* it from W6; the SMS exists from W1
regardless, on paper if necessary, because a service with no management system is a service whose
failures are discovered by its users.

| Attribute | Value |
|---|---|
| **SMS scope** | The 1000FiX ERP platform, its twelve portals, its four mobile surfaces, its integrations and the infrastructure `PE-001`…`PE-009` designs — **operated for internal users, corporate clients and consumers** |
| **SMS boundary — excluded** | The Company's desktop, mobile-device and software-licence estate (`M66` `FR-ITS-025`…`030`); client-facing managed services (`M05`, a revenue product); workshop test equipment (`M45`) |
| **SMS owner (accountable)** | **Chief Technology Officer** |
| **SMS manager (responsible)** | **Head of IT Service Management** — a role that does not currently exist (§8.4, `SMF-Q-01`) |
| **Governing body** | The **Service Management Board** (§8.2), reporting into the ERP Steering Committee constituted by [`GV-002`](../00_Programme_Governance_and_Control/GV-002_Governance_Framework_RACI_and_Terms_of_Reference.md) |
| **Policy of record** | This document |
| **Review cadence** | Quarterly by the Board; annually by the Steering Committee; out of cycle on any trigger in §11.5 |

### 4.2 ISO/IEC 20000-1:2018 + Amd 1:2024 — the clause map

The value of a clause map is not the rows that pass. It is the rows that cannot.

| Clause | Requirement, in short | Satisfied by | State at W1 |
|---|---|---|:--:|
| **4.1** | Context, **including whether climate change is a relevant issue** (Amd 1:2024) | §4.4 | ✅ Determined |
| **4.2** | Interested parties and their requirements, **including climate-related ones** (Amd 1:2024) | `OP-001` §4.1 (eleven external audiences + internal), §4.4 | ✅ |
| **4.3 / 4.4** | SMS scope; the SMS itself | §4.1 | ✅ |
| **5.1 / 5.2** | Leadership, commitment, service management policy | §4.1 owner row; this document as policy | ⚠ **Qualified** — no constituted body can approve it (`PGD-A2-25`) |
| **5.3** | Roles, responsibilities and authorities | §8.3 RACI; `OP-013` §4.8 authority table | ⚠ Specified, **unstaffed** |
| **6.1** | Risks and opportunities | [`GV-005`](../00_Programme_Governance_and_Control/GV-005_RAID_Register.md) RAID; §12's eight unfunded items are raised there | ✅ Route exists |
| **6.2** | Service management objectives | §11.2 measures; `SV-002` targets | ◐ **Depends on `SV-002`** |
| **6.3** | Planning the SMS | §7's ruling; `GV-004` schedule | ◐ Pending Steering decision |
| **7.1** | Resources | §8.4 establishment; **`GV-007` lines do not exist** | ⛔ **Unfunded** |
| **7.2** | Competence | §8.5 | ◐ Specified, untrained |
| **7.3 / 7.4** | Awareness; communication | `CH-003`, `OP-004`, `OP-005` | ✅ |
| **7.5** | Documented information | [`GV-011`](../00_Programme_Governance_and_Control/GV-011_Documentation_Control_and_Configuration_Management_Plan.md) | ⚠ `PGD-A2-15`: 644+ files outside version control |
| **7.6** | **Knowledge** | §9.3; `M66` `FR-ITS-030` from W6 | ◐ `KB` articles as the interim |
| **8.1** | Operational planning and control | §6 practice set | ✅ Specified |
| **8.2.1** | **Service portfolio / service catalogue** | §5 (21 services); `SV-002` §4 publishes it | ◐ **`SV-002` owns publication** |
| **8.2.2** | Asset management | `M66` `FR-ITS-025`…`027` | ⛔ **W6, and the physical audit is unapproved** (`M66` Q-01) |
| **8.2.3** | **Configuration management** | §9; `M66` `FR-ITS-029` | ⛔ **No CMDB. §9.2 states the substitute and its cost** |
| **8.3** | Relationship and agreement — service level management | `SV-002` | ⛔ **No SLA the platform keeps exists** |
| **8.4** | Supply and demand — budgeting, capacity | `PE-006`; `GV-008` | ◐ Capacity designed; **operations budget absent** |
| **8.5.1** | **Change control** | `SP-031` §5.3/§5.4; `RL-001` §8; `M66` `FR-ITS-018`…`024` | ✅ Specified, **manual until W1 tooling** |
| **8.5.2** | Service design and transition | `SV-005`; [`RL-001`](../12_Release_Deployment_and_Transition/RL-001_Release_Management_and_Versioning_Policy.md) | ✅ |
| **8.5.3** | Release and deployment | `RL-001`, **`RL-002` (issued)** | ✅ *(corrected §0 — `RL-002` was absent at 01:53)* |
| **8.6.1** | **Incident management** | `OP-013`; `SV-006` | ✅ Specified · ⛔ **unpaged** |
| **8.6.2** | **Service request management** | `OP-001` §4.5; `OP-015` | ✅ Specified |
| **8.7.1** | **Problem management** | `SP-031` §5.5; `SV-006` §5 | ◐ Thin upstream — three steps in `SP-031`; `SV-006` supplies the practice |
| **8.7.2** | **Service availability management** | `PE-001` §9; **`PE-008` §7 (eight SLOs, windows, error budgets)**; `SV-002` §5 | ✅ **Designed and measurable by design** *(corrected §0)* — ⚠ **unbuilt**: no instrumentation exists yet |
| **8.7.3** | **Service continuity management** | `OP-012`; **`PE-007` §3–§10** | ◐ **Designed** *(corrected §0)*. `AUDIT-017` `OP-01` moves from *no design* to **a forced decision** — `PE-007` §7.5 |
| **8.7.4** | Information security management | `SC-001`…`SC-011` | ✅ |
| **9.1 / 9.2 / 9.3** | Monitoring, measurement, analysis; internal audit; management review | §11; **`PE-008` §7, §9**; `GV-010` assurance | ◐ **Designed** *(corrected §0)*; **not yet instrumented** |
| **10.1 / 10.2** | Nonconformity, corrective action, continual improvement | §11.3 → `M23` CAPA; `SV-006` §7 | ✅ Route exists |

**Counted from the corrected table above, row by row, at 2026-08-19 02:15 (+06):
30 clause rows · 13 ✅ · 3 ⚠ · 9 ◐ · 4 ⛔ · 1 mixed (§8.6.1). Check: 13 + 3 + 9 + 4 + 1 = 30 ✓
against a counted row total of 30.**

> **A correction to this document's own first draft, recorded rather than silently fixed.** The
> 01:53 draft asserted *"33 clause rows · 13 ✅ · 12 ◐ or ⚠ · 8 ⛔"*. **The row count was wrong** —
> the table has always had 30 rows — and the ⛔ count was taken before `PE-007`, `PE-008`, `PE-009`
> and `RL-002` were issued. This is the `PGD-A2-24` defect class (*a total that conceals wrong
> components*) committed in the document that cites it, which is worth recording plainly: the
> figures above were regenerated by extraction from the table, not by adjusting the previous ones,
> per `PG-M10` and `RG-06`.

> **`SMF-F-02` (revised). Four ⛔ rows remain, and every one of them is a resource, an agreement or a
> procurement rather than a design:** §7.1 resources (unfunded), §8.2.2 asset management (deferred
> to W6 by `SV-001-D-04`), §8.2.3 configuration management (no CMDB before W6), §8.3 service level
> management (no agreed SLA). The single mixed row, §8.6.1, is **specified and unpaged**.
>
> **Category 10 has now removed every ⛔ that a design could remove.** What remains cannot be
> designed away — it needs an establishment, a signature and a procurement, which is exactly the
> distinction §4.3 exists to keep visible, and exactly what `AUDIT-017` meant by *"operational
> content and no operational capability"*.

### 4.3 The four words, and their evidence tests

`SMF-01` forbids asserting that a control operates. These are the four permitted assertions and
what each one costs to make.

| Word | Means | Evidence required | Who may assert it |
|---|---|---|---|
| **Specified** | A controlled document describes it | The document exists at a named path with front matter | Content / Engineering |
| **Designed** | The technical means is chosen and sized | A design document names the component, its topology and its cost | Engineering |
| **Funded** | A budget line exists against a named owner | A `GV-008` line and a `GV-007` resource row | CFO |
| **Operating** | It has been executed and evidenced at least once | A dated execution record — a page acknowledged, a restore verified, a rota shift worked | The service owner (§5.3) |

> **The distance between *specified* and *operating* is this entire category.** `AUDIT-017` found
> sixteen files at *specified*, four items at *designed*, and **zero at *operating***.

### 4.4 The climate-change determination (Amd 1:2024, §4.1 / §4.2)

The amendment requires a determination, not an essay. It is made here so it exists.

| Question | Determination | Basis |
|---|---|---|
| Is climate change a relevant issue to this SMS? | **Yes** | Bangladesh is among the most flood- and cyclone-exposed operating environments in the world. The platform's continuity design (`PE-007`, `OP-012`) rests on a **Bangladesh-resident** data site `BD-R` (`PE-001` §3.3) whose availability is exposed to flood, cyclone and grid failure — and `NFR-086`'s residency rule means that exposure **cannot be engineered away by moving the data** |
| Do interested parties have climate-related requirements? | **Yes, two.** (a) Regulated counterparties flow down continuity obligations by contract (`PE-001` §12); (b) 51+ branches are the service delivery points, and branch-level flood closure is a **service continuity event**, not only a facilities one | `PE-001` §12.1; `OP-012` §5 |
| Consequence carried forward | The `SV-006` §9 business impact analysis and `PE-007` must both treat **site-level climate events** as a named scenario class, and the out-of-band communication tree (`OP-013` §4.10) must be exercised against a **branch unreachable for days**, not only a system outage of hours | `SV-006` §9.2 |

---

## 5. The Service Portfolio

### 5.1 What counts as a service

> **`SMF-04`. A service is something a named population depends on, that can be separately
> unavailable, and that has one accountable owner.** A component is not a service; a module is not a
> service; a project is never a service.

The test matters because the estate contains 67 modules, 12 portals and 16 domain services, and a
catalogue with 95 entries is a catalogue nobody reads. Applying the three-part test to
`PE-005` §5.1's component inventory and `04-00`'s portal set yields **21 services**.

### 5.2 The twenty-one services

| # | Service | Population | Separately unavailable? | Owning function | Criticality |
|---:|---|---|:--:|---|:--:|
| `S-01` | **ERP core transaction service** (Odoo application + cron) | All internal, all portals | Yes | Platform Engineering | **P0** |
| `S-02` | **System of record — primary data** (PostgreSQL primary + replicas + PgBouncer) | Everything | Yes | Platform Engineering | **P0** |
| `S-03` | **Identity service** (Keycloak) | Every population | Yes — *"a total-outage dependency"* (`PE-001` §9.2) | Security Engineering | **P0** |
| `S-04` | **API gateway and ingress** (Kong, Nginx) | Every external caller | Yes | Platform Engineering | **P0** |
| `S-05` | **Filestore / object storage** (MinIO) | Attachments, documents, evidence photographs | Yes | Platform Engineering | **P0** |
| `S-06` | **Payment path** (`INT-003` and gateway failover) | Consumers, branches, finance | Yes | Integration Engineering | **P0** — `NFR-048` 99.95% |
| `S-07` | **Customer portal** `P01` | 250,000+ consumers/month | Yes | Platform Engineering | **P0** — `NFR-046` |
| `S-08` | **Technician mobile service** `P02` (sync, offline) | 200–400 field technicians | Yes | Mobile Engineering | **P0** |
| `S-09` | **Admin / internal portal** `P03` | 500–1,000 staff | Yes | Platform Engineering | **P0** |
| `S-10` | **Integration and event platform** (n8n, Redpanda from W6, dead-letter handling) | 47 integrations | Yes | Integration Engineering | **P0** |
| `S-11` | **Notification service** (Novu; SMS, email, WhatsApp, push) | Every population | Yes | Integration Engineering | P1 |
| `S-12` | **Resident data service** `CD-233` in `BD-R` | Statutory / residency-classified fields | Yes | Security Engineering | **P0** |
| `S-13` | **Corporate portal** `P04` | 550–2,200 corporate users and admins | Yes | Platform Engineering | P1 |
| `S-14` | **Vendor portal** `P05` | 200–600 vendors | Yes | Platform Engineering | P2 |
| `S-15` | **Analytics and BI** `P06` (Metabase, ClickHouse, warehouse loads) | Management, finance | Yes | Data Engineering | P1 |
| `S-16` | **Marketplace portal** `P07` (from W7) | 500–2,000 sellers, 1,000–4,000 seller technicians | Yes | Platform Engineering | P1 |
| `S-17` | **Brand partner portal** `P08` | 17+ brand partners | Yes | Platform Engineering | P2 |
| `S-18` | **Logistics portal and courier integration** `P09` | 3–6 courier organisations, warehouse | Yes | Integration Engineering | P1 |
| `S-19` | **Contact centre platform** `P10` (from W4, telephony `INT-015`) | Contact Centre agents, consumers | Yes | Contact Centre + Integration | P1 |
| `S-20` | **Quality portal** `P11` (from W5) | Quality function, `M23` | Yes | Platform Engineering | P2 |
| `S-21` | **Partner portal** `P12` (from W7) | 50–330 referral, franchise and channel partners | Yes | Platform Engineering | P2 |

**Twelve are `P0` or `P1` at or before W4.** Time-series (Traccar/TimescaleDB), routing
(VROOM/OSRM), document management (Mayan), workflow (n8n), ML inference (Ollama/MLflow) and
intrusion detection (Wazuh) are **components of** the services above, not services in their own
right, because no population depends on them independently — they fail *as* `S-01`, `S-08`, `S-10`
or `S-15`.

> **`SMF-05`. The service list is the unit of everything downstream.** `SV-002`'s SLOs, `SV-003`'s
> runbooks, `SV-004`'s escalation targets, `SV-006`'s impact assessment and `PE-008`'s dashboards
> are all indexed by these 21 identifiers and by nothing else. A component that is not inside one
> of them has no owner, and that is the finding, not an omission in the list.

### 5.3 Service ownership — what it obliges

> **`SMF-06`. Every service in §5.2 has one named individual as its owner, recorded by name in the
> service register and not by team.** *"Platform Engineering"* is a column in the table above; it is
> not an owner. `OP-016` `AC-01` makes the same rule for actions and gives the reason: a team owner
> is an unowned item with a plausible label.

| Obligation | What it means in practice | Evidence |
|---|---|---|
| **Know the service** | Its dependencies, its failure modes, its blast radius, and what breaks downstream | `SV-003` runbook §2 exists and is current |
| **Own the SLO** | Propose it, defend it, report against it monthly | `SV-002` §5 |
| **Own the runbook** | Its accuracy is the owner's; an incident that finds a wrong step is the owner's finding | `SV-003` `RBS-11` |
| **Own the alerts** | Every alert on the service names a runbook and has a defined action (`OPS-03`); a noisy alert is the owner's defect | `SV-004` §7.3 |
| **Attend the review** | Any `Sev1` or `Sev2` on the service (`SV-006` §10) | PIR attendance |
| **Approve the change** | Or name a delegate; a change to the service with no owner sign-off is a control failure | `SP-031` §5.3 step 16 |
| **Report** | One page, monthly, to the Service Management Board (§11.4) | Service report |

> **`SMF-07`. Service ownership is not a job.** It is an accountability held **alongside** an
> engineering role, and it is time-boxed at roughly half a day per month per service in steady
> state. Stating that here is deliberate: unnamed effort is how ownership becomes nominal, and a
> nominal owner is worse than none because their existence stops anyone asking.

### 5.4 The ownership gap, stated

**Twenty-one services require twenty-one named owners.** The programme currently has:

| Function named in §5.2 | Identified people | Source |
|---|:--:|---|
| Platform Engineering | **0 named**; the Platform Squad exists as a delivery construct | `M66` §18 Q-02 |
| Security Engineering | 0 named | `OP-013` §4.3 — the four-member security rota is unstaffed |
| Integration Engineering | 0 named | — |
| Data Engineering | 0 named | `OP-013` §4.3 — business-hours rota of 2, unstaffed |
| Mobile Engineering | 0 named | — |

This is not a separate finding from `AUDIT-017` `OP-09`; it is the same finding counted a different
way. **The rota needs ten people; the service register needs twenty-one owner names, drawn from the
same pool.** §8.4 sizes both against one establishment so the programme funds it once.

---

## 6. The Practice Set

### 6.1 The choice

ITIL 4 defines thirty-four practices. `M66` §4 already rejected the full set for the internal IT
function — *"four processes done properly beats thirty-four done nominally"* — and that judgement is
right and is extended here. The platform is larger than the internal IT estate and needs more than
four; it does not need thirty-four.

> **`SV-001-D-02`. Twelve practices are adopted for the platform SMS. Twenty-two are deferred, each
> with a named reason and a review wave.**

### 6.2 Adopted — twelve

| # | ITIL 4 practice | Why it is adopted | Specified in | Live from |
|---:|---|---|---|:--:|
| 1 | **Incident management** | The platform will fail; the only question is whether the failure is governed | `OP-013`, `SV-006` §4 | **W1** |
| 2 | **Service request management** | 800+ users and 38 roles generate a continuous request load; unrouted, it lands on engineers | `OP-001` §4.5, `OP-015` | **W1** |
| 3 | **Change enablement** | `BRU-ADM-02` makes an unrecorded production change a control failure; ISO 9001 cl. 8.5.1 requires control of provision | `SP-031` §5.3/§5.4, `RL-001` §8 | **W1** |
| 4 | **Service desk** | The single route to help; without it, help is the branch manager's mobile | `OP-001` §4.2–§4.4 | **W1** |
| 5 | **Monitoring and event management** | An incident detected by a customer is an incident detected too late; `KPI-088` targets **zero** integration failures undetected beyond 5 minutes | `NT-021`, **`PE-008` §3–§9 (issued)** | **W1** |
| 6 | **Problem management** | `M66` `BRU-ITS-03`: an incident closes on restoration, a problem stays open until the cause is gone. Without it the eleventh occurrence is experienced as the first | `SV-006` §5 | **W1** |
| 7 | **Service level management** | The platform currently commits nothing to its own users | `SV-002` | W2 |
| 8 | **Service continuity management** | `NFR-007` RPO 15 min / RTO 2 h is a commitment with, today, **a design and no provisioned infrastructure** | `OP-012`, **`PE-007` (issued)**, `SV-006` §9 | W2 ⚠ |
| 9 | **Availability management** | Four availability targets exist with four different scopes (`PE-001` §9.1); **`PE-008` §7 now turns them into eight SLOs with windows and budgets** | `SV-002` §5, **`PE-008` §7 (issued)** | W2 |
| 10 | **Knowledge management** | Deflection is the only mechanism that stops the second occurrence reaching a human | §9.3, `OP-003`, `HC` set | W2 |
| 11 | **Service configuration management** | Impact assessment during an incident is otherwise a conversation | §9.2 (shallow), `M66` `FR-ITS-029` (full, W6) | W2 (shallow) |
| 12 | **Continual improvement** | ISO 9001 cl. 10.2 already binds the Company; support has been outside the certified scope | §11.3 → `M23` | W2 |

> **One of the twelve now carries ⚠** *(corrected §0 — three did at 01:53)*. Continuity is adopted
> against `PE-007`'s design, which is complete and **unprovisioned**: `PE-007` §7.5 records that the
> `Z4` recovery decision is *forced* and unmade, and no `dr` environment has been sized or costed.
> Monitoring and availability lost their ⚠ when `PE-008` was issued — **they are designed and
> unbuilt, which is a schedule position rather than a specification gap.**

### 6.3 Deferred — twenty-two, with reasons

| Practice | Deferred to | Reason |
|---|:--:|---|
| IT asset management | **W6** | `M66` `FR-ITS-025`…`027`; depends on `M21` joiner/leaver (W5) and `M06` destruction certificate (W6). **This is the dependency §7 turns on** |
| Software asset management | W6 | `M66` `FR-ITS-028`; same module, same wave |
| Capacity and performance management | W2 | `PE-006` designs it; the *practice* (monthly review per `OPS-08`) starts when there is production load to review |
| Deployment management | W1 | Adopted, but by `RL-001`/`RL-002` in Category 12 — not deferred, **relocated**. Listed here so the map is complete |
| Release management | W1 | As above — `RL-001` |
| Information security management | W1 | Adopted, by `SC-001`…`SC-011` — relocated, not deferred |
| Supplier management | W1 | Relocated to `CO-003`/`CO-004`; the vendor-facing half of `T4` (`OP-001` §4.2) |
| Relationship management | W2 | Relocated to `CH-003` stakeholder engagement |
| Service financial management | W3 | No IT cost model exists; `M66` `FR-ITS-030` cost transparency is W6. Interim: `GV-008` programme budget only |
| Workforce and talent management | — | HR practice; out of the SMS boundary |
| Strategy · portfolio · project · architecture · risk · measurement and reporting · organisational change · service design · business analysis · infrastructure and platform · software development · service validation and testing | — | **Owned by other categories of this register** (`GV-*`, `AR-*`, `BM-*`, `CH-*`, `PE-*`, `BE-*`, `QA-*`). Naming them as "deferred" would be false; they are **adopted elsewhere** |

> **`SMF-08`. A practice adopted in another category is not adopted twice here.** The single most
> common failure of an ITSM framework document is that it restates the change process, the security
> process and the test process in its own words, producing three parallel authorities. **This
> document names the owner and stops.**

### 6.4 The three relationships between incident, defect and problem

Four scales exist (`OP-013` §4.2) and four record types exist. These are the **only** sanctioned
conversions, and they are stated here because `SV-006`, `QA-010` and `SP-031` each own one end.

| From | To | Rule |
|---|---|---|
| Incident | **Defect** | An incident *may* produce a defect record. **The defect keeps its own `S1`–`S4` severity** (`QA-010`); it does not inherit `Sev1`. Two records, linked |
| Incident(s) | **Problem** | Recurrence above threshold, or an unknown cause, raises a problem. **The problem has no severity of its own** (`OP-013` §4.2); it has an impact estimate |
| Problem | **Change** | The permanent fix is a change, and the problem closes only on **verified absence of recurrence** (`M66` `BRU-ITS-05`), never on the change being deployed |

> **`SMF-09`. A ticket never changes type.** An internal IT ticket that turns out to be a platform
> fault does not become an incident; **a second record is created and linked** (`M66` §4.2). Type
> mutation destroys the measurement of both.

### 6.5 `NFR-091` — the sixty-seven runbooks, ruled

`AUDIT-017` `OP-07` found `NFR-091` (*"every module ships with an operational runbook"*, `P0`)
against a register containing five component runbooks and zero module runbooks, offered two
readings, and recorded that the programme had chosen neither.

> **`SV-001-D-03`. The second reading is taken: `NFR-091` means what it says.** Component runbooks
> do **not** discharge it. `NFR-091` is not amended.

| Consideration | Weight |
|---|---|
| `02-05` §9 repeats the obligation as a **per-module** definition-of-done item — *"every module ships with a README, a runbook and its OpenAPI specification"*. Two independent statements of the same rule | **Decisive** |
| Amending `NFR-091` to mean "component runbooks" would silently delete a `P0` requirement to make a register look complete. That is the `PGD-A2-24` defect class — a correct total concealing a wrong component | Decisive |
| The cost is real: at the observed 20–35 KB per runbook, 67 module runbooks are a body of work comparable to two content categories | Accepted, and **sized in `SV-003` §5** rather than assumed away |
| Component runbooks remain necessary and are not superseded — they cover what no single module owns (§5.2's `S-02`, `S-03`, `S-04`, `S-05`) | — |

**Consequence:** `SV-003` §5 carries the module-runbook obligation, its sizing, and the **only**
mechanism that makes it affordable — a module runbook is a **short, templated appendix** to the
component runbook that already covers its substrate, not a 30 KB standalone document.
`SMF-14` binds it.

### 6.6 `G3-on-build` — how a runbook is ever approved

`AUDIT-017` `OP-16` records that all sixteen `OP` files are `Draft` and none can be approved,
because gate `G3` ("does it match what the system actually does, at the pinned release?") requires
a system that is delivered from W1 to W8. Six runbooks will still be `Draft` at go-live.

> **`SMF-19`. `G3` is granted per procedure, not per file.** Every procedure in a runbook carries an
> **execution date**, set the first time the procedure is actually run against the built
> environment. A runbook is `Approved` when every `P0` procedure in it carries an execution date; a
> procedure with no execution date is displayed as **unverified** to the engineer reading it at
> 02:00, which is the honest and the useful state.

This adopts `AUDIT-017` `R-06` and is specified mechanically in `SV-003` §7.

### 6.7 The severity model — a conflict that arose during authoring

**This section did not exist in the 01:53 draft.** It exists because `PE-008` was issued at
approximately 02:00 and its §8.5 makes a claim this category cannot leave unadjudicated.

**What `PE-008` §8.5 states.** Under the heading *"Severity — closing `OP-04`"*, ruling
`PE-008-D-05`: *"One severity model, defined here, owned by the Head of Service"* — a **three-level**
scale, `Sev1` / `Sev2` / `Sev3`, with rule `SV-01`: *"The model is defined once, here, and referenced
by `SV-*` and `OP-*` — not redefined."*

**What is already true.**

| Fact | Evidence |
|---|---|
| The canonical scale is `Sev1`–`Sev4`, **four levels** | `OP-013` §4.1, carried forward in intent from `NT-021` §2.1, published **2026-08-15** |
| `AUDIT-017` `OP-04` **adjudicated ownership to `OP-013` §4.1** and required three upstream corrections *to point at it* | `AUDIT-017` `OP-04`, `OP-013` OI-02 |
| Four levels are consumed across the estate | `NT-021` alert routing · `OP-004` communication triggers · `OP-007`…`OP-012` §6 of every runbook · `OP-016` §4.1 · `OP-002` `HX-04`/`HX-05` |
| `Sev3` and `Sev4` are **operationally different**: `Sev3` is a ticket with a 5-working-day restoration target; `Sev4` is dashboard-only, *"a threshold approached"* | `OP-013` §4.1 |

> **`SV-001-D-07`. Category 11 operates to `OP-013` §4.1's four-level scale.** `PE-008` §8.5's
> three-level model is read as an **alerting classification**, not as the severity scale, and is
> mapped rather than adopted.

| `PE-008` §8.5 | `OP-013` §4.1 | Note |
|---|---|---|
| `Sev1` — business-stopping, pages 24×7 | **`Sev1`** | Equivalent |
| `Sev2` — degraded, pages in hours | **`Sev2`** | Equivalent |
| `Sev3` — informational, a ticket | **`Sev3` *and* `Sev4`** | **The merge loses a distinction the estate uses.** A capacity threshold approached (`Sev4`, dashboard-only) becomes a ticket with a restoration target it does not need |

**Why this document rules rather than defers.** `SMF-11` requires operating to the stricter of two
current statements and recording the conflict. The stricter is the four-level scale, because it
makes the finer distinction and because it is the one already cited by nine other files. Reducing it
would require editing every runbook §6, `OP-004`'s trigger table and `OP-016` §4.1 — and would
reopen `AUDIT-017` `OP-04`, the finding `PE-008` §8.5 is written to close.

**Three further collisions, recorded not litigated.** `PE-008` §8 allocates three rule prefixes that
are already in use elsewhere with different meanings:

| Prefix | `PE-008` §8 meaning | Existing meaning | Owner of the existing |
|---|---|---|---|
| **`SV-01`…`SV-03`** | Severity model ownership | **`SV-01`…`SV-07`, the severity rules** — *"anyone may declare any severity"* | `OP-013` §4.1 |
| **`RT-01`…`RT-04`** | Alert routing | **`RT-01`…`RT-08`, the rota rules** — `RT-04` is *"nobody is on call more than one week in three"* | `OP-013` §4.3 |
| **`AL-01`…`AL-04`** | Burn-rate alerting | **`AL-01`…`AL-07`, the alert rules** — `AL-03` is *"alerts never contain customer personal data"* | `NT-021` §2.3 |

> **`SMF-26`. A rule identifier cited outside the document that defines it is always written with its
> owning document.** `` `OP-013` `RT-04` `` and `` `PE-008` `RT-04` `` are different rules and both
> are current; an unqualified `RT-04` in an incident is ambiguous in the worst possible moment. The
> estate's convention is that rule prefixes are **document-local**, which is workable — but only
> under this rule, and `AUDIT-017` `OP-23` is what happens when it is not followed.
>
> **`SMF-26` is now ratified upstream and is retained as a local restatement of it.** [`RR-002`](../99_Reference_Registers_and_Glossary/RR-002_Identifier_Convention_Standard.md)
> `IDC-07` — *"a document-local identifier cited outside its document is qualified — `<document-id>
> <identifier>`, never bare"* — is the programme rule. Where the two differ, `IDC-07` governs.
>
> **`SMF-F-06`.** `PE-008` §8.5's `SV-01` is not document-local by its own terms: it asserts
> programme-wide scope (*"referenced by `SV-*` and `OP-*`"*) over an identifier space `OP-013` §4.1
> already owns, in a category whose **document code is also `SV`**. This is the collision `SV-001`
> §2.4 was written to avoid and it occurred anyway, from an adjacent category, twenty-two minutes
> later.
>
> **Correction at v1.2.** The v1.1 text of this paragraph ended *"`RR-002` is now recommended for the
> eighth time."* **`RR-002` was issued at approximately 02:41 (+06) on 2026-08-19**, between this
> category's authoring and its audit — the tenth baseline movement of the session. It exists, it
> registers the identifier spaces, and its `IDC-07`, `IDC-08` and `IDC-13` are precisely the three
> controls this finding asked for. **`SMF-F-06` therefore now has a register to be corrected in**,
> which is a materially better position than the one this paragraph originally described.

**Everything else in `PE-008` §8 is adopted without qualification** — the burn-rate tiers, the
both-windows rule, alert discipline `AD-01`…`AD-05`, and `RT-04`'s requirement that alert delivery is
itself monitored. `SV-004` §7 implements them. The disagreement is confined to §8.5.

---

## 7. The W1–W5 Ruling

**This is the section the category exists for.**

### 7.1 The finding restated precisely

| Fact | Source | Verified |
|---|---|---|
| `OP-001` (support model) is `P0` at **W1** | `OP-001` front matter; `AUDIT-017` §2.2 | 2026-08-19 |
| `OP-003` (68 macros) is `P1` at **W1**, tracing to the same module | `AUDIT-017` `OP-06` | 2026-08-19 |
| `M66` is `P2`, delivery wave **W6 (Months 23–26)** | `M66` §1 | 2026-08-19 |
| The register carries **no lead-time note** on either row | `AUDIT-017` `OP-06` | 2026-08-19 |
| Gap | **Five waves ≈ twenty months** | — |

`M66` §16.3 gives its own reasoning, and it is worth quoting exactly because the ruling turns on it:

> *"**Why Wave 6 and not earlier.** M66 depends on M21 (W5) for the joiner and leaver events that
> make asset tracking enforceable, and on M06 (W6) for the destruction gate. Delivering M66 earlier
> would produce a ticketing system without the asset control that is half its value. **The cost of
> the W6 placement is that internal IT runs on WhatsApp for five waves.**"*

**That reasoning is correct, and it justifies the wave for exactly half the module.**

### 7.2 The ruling

> **`SV-001-D-04`. `M66` is split by dependency, not deferred as a whole. `CD-163` (`cd_itsm`,
> 9 PW) moves to W1. `CD-164` (`cd_it_asset`, 5 PW) remains at W6.**

The split is not invented; it is **already the module's own build decomposition** (`M66` §16.2), and
the dependency analysis falls cleanly along the same line:

| Half | Requirements | Custom module | Effort | Prerequisites | Earliest wave those exist |
|---|---|---|---:|---|:--:|
| **Service management** — catalogue, self-service portal, incident, problem, change, review, knowledge, SLA engine | `FR-ITS-001`…`024`, `030` (knowledge/reporting portion) | **`CD-163`** | **9 PW** | `M29` Identity, `M30` Platform Admin, `M28` Integration | **W1 — all three** |
| **Asset management** — IT asset register, lifecycle, JML workflows, SAM, CMDB, vendor contracts, cost attribution | `FR-ITS-025`…`029`, `030` (asset/cost portion) | **`CD-164`** | **5 PW** | `M21` Core HR (**W5**), `M06` Data Services (**W6**), `M16` Procurement (W3), `M18` E-Waste (W8), `M49` (W5) | **W6** |

**Every prerequisite `M66` §16.3 cites as the reason for W6 — `M21`, `M06`, `M18`, `M49` — is a
prerequisite of `CD-164` only.** `CD-163` has no dependency later than Wave 1.

| Objection | Response |
|---|---|
| *"`M27` Contact Centre is W4 and `FR-ITS-010` needs it for major-incident communication"* | `FR-ITS-010` needs **a** communication channel, and `OP-004`'s 26 templates plus `OP-005`'s status page plus the `OP-013` §4.10 out-of-band tiers supply four. `M27` improves the channel; it does not gate the practice. Degrade gracefully, do not defer |
| *"`M65` Localisation is W9 and SLA clocks need holiday sets"* | `M66` §16.3 answers its own objection: *"until W9 the Bangladesh holiday set is held in `M30`"* — and `M30` is **W1**. See §7.5, which corrects `OP-001` §4.9 on exactly this point |
| *"The module is `P2`; moving it competes with `P0` work"* | The module is `P2`; **`OP-001`, which cannot function without it, is `P0` at W1**. A `P2` prerequisite of a `P0` deliverable is a mis-prioritisation, not a sequencing preference. This is `AUDIT-017` `OP-05`'s defect — *the register assigns a wave by the module a file traces to, not by the wave of the file that consumes it* — appearing in the **module** register rather than the content register |
| *"9 PW is real money"* | Yes. §7.3 states it as a number, against the cost of not spending it |

### 7.3 What the ruling costs, and what not ruling costs

| | **Move `CD-163` to W1** | **Leave `M66` whole at W6** |
|---|---|---|
| Effort brought forward | **9 PW** (`M66` §16.2) | 0 |
| Effort deferred | 5 PW stays at W6 | 14 PW stays at W6 |
| W1 capacity impact | 9 PW against a 1,513 PW build estimate — **0.6%** | — |
| Ticketing at W1 | `CD-163` on the OCA `helpdesk` substrate — the same substrate the interim would use anyway (`M66` §16.1) | OCA `helpdesk` raw, configured by hand, **thrown away at W6** |
| SLA measurement | **Calendar-aware from W1** (`M30` holiday set) | **Unreportable until W6** (`OP-001` §4.9) |
| Escalation on breach | Automatic (`FR-ITS-008`) | **Manual, one supervisor, one daily review — a named single point of failure** |
| Problem management | `FR-ITS-013`…`017` from W1 | None until W6. **Twenty months of incidents with no recurrence detection**, which is exactly the state `M66` §2 was written to end |
| Change records | `FR-ITS-018`…`024` with calendar, collision detection and freeze enforcement | `SP-031` executed manually — *"works, but audit evidence is weaker"* (`OP-001` §4.9) |
| Rework | None — `CD-163` is built once | **Configuration of the interim `helpdesk` queues, SLA policies and macros is discarded** |
| KPI position | `M66` §15's sixteen metrics measurable from W1 | Baseline `unmeasured` for twenty months; `BM-002` inherits another 16 absent baselines |

> **`SMF-F-03`. The 9 PW is not additional work. It is the same work, done once instead of twice.**
> The interim model in `OP-001` §4.9 requires configuring `helpdesk` teams named as the `Q-*` codes,
> SLA policies, a daily breach-risk view and a `KB` known-error convention — **all of which
> `CD-163` replaces at W6**. The honest comparison is 9 PW at W1 against *(interim configuration
> effort + 9 PW at W6 + twenty months of unmeasured service)*.

### 7.4 What the interim still has to cover

The ruling does not remove the need for an interim; it shrinks it to what actually depends on W5
and W6 modules. **Even if `SV-001-D-04` is approved**, these remain absent until W6 and W8:

| Capability | Until | Interim | Accepted consequence |
|---|:--:|---|---|
| IT asset register | **W6** | Spreadsheet held by Internal IT | **The `100% of company IT assets tracked` KPI cannot be evidenced before W6** (`OP-001` §4.9) |
| Joiner/mover/leaver automation | **W6** (needs `M21` at W5) | `OP-015` executed manually; `SP-031` §5.2 approvals | `KPI-090` (zero orphaned accounts) depends on a manual revocation inside one hour (`BRU-SEC-06`) — see §7.6 |
| CMDB | **W6** | §9.2's service-dependency table, maintained by hand | Impact assessment during an incident is manual |
| Software asset management | W6 | Purchase records; no reconciliation | Licence compliance position unknown |
| Certified disposal route | **W8** (`M18`) | Retired assets held in *retired-pending-disposal* | **Liability for stored end-of-life devices holding customer data is unassigned** — `M66` Q-10, still open |
| **Paging** | **See `SV-004`** | **Nothing exists.** `CD-163` is an ITSM module, **not a paging platform** | §7.7 |

### 7.5 A correction to `OP-001` §4.9

`OP-001` §4.9 states that the W1–W5 interim runs *"`helpdesk` SLA policies, **without**
holiday-calendar awareness"*, and concludes: *"SLA attainment over public holidays will be wrong.
Do not report it as a KPI before W6."*

**That is right about raw OCA `helpdesk` and wrong about the programme's position**, because
`M66` §16.3 records that the Bangladesh holiday set is held in **`M30`, delivered at W1**, and
`M66` `T-04` requires SLA clocks to respect working calendars from `M30` and holiday sets from
`M65`. The calendar source exists at W1; only the *consumer* of it was deferred.

> **`SMF-10`. With `SV-001-D-04` approved, SLA attainment is reportable from W1** and `OP-001`
> §4.9's row is superseded. **Without it approved, `OP-001` §4.9 stands unchanged** and the
> non-reportability is real. The correction is therefore *conditional*, and it is stated
> conditionally rather than applied, because a content file may not be edited on the strength of a
> decision that has not been taken. Raised to Content Design as `SMF-Q-04`.

### 7.6 The one-hour / twenty-four-hour conflict, carried

`AUDIT-017` `OP-15` records that `SP-031` §1 requires leaver access revoked **within one hour**
(`BRU-SEC-06`) while `KPI-090` measures orphaned accounts **beyond 24 hours** — a factor of
twenty-four, both current, both cited.

This framework **operates to the one-hour rule** and treats anything beyond it as a control failure,
following `OP-015` §4.6. It does not average them and it does not resolve them: the resolution is
either a `KPI-090` tolerance change or a documented risk acceptance, and both belong to the CFO and
Internal Audit. Carried as `SMF-Q-05`.

> **`SMF-11`. Where two current programme statements conflict, this category operates to the
> stricter and records the conflict.** It never operates to the average, and it never silently
> selects the more convenient one.

### 7.7 What the ruling explicitly does **not** solve

> **`SMF-12`. `CD-163` is an ITSM module. It is not a paging platform, and moving it to W1 does not
> page anybody.**

`M66` §5.2 `FR-ITS-008` provides *tiered assignment and escalation on SLA threshold breach* — a
ticket-system escalation, measured in the SLA clock's units. `OP-013` §4.4 requires a `Sev1` page
**acknowledged within five minutes at 02:00**, with auto-escalation to secondary at 5, lead at 10
and CTO at 15. Those are different mechanisms with different failure modes, and no ITSM SLA engine
performs the second.

**The paging gap is `AUDIT-017`'s sharper half of `OP-06` and it survives this ruling intact.**
`SV-004` is the document that closes it, and it is `P0`/W1 for that reason.

---

## 8. The Operating Model

### 8.1 Structure

| Layer | Body / function | Membership | Cadence | Decides |
|---|---|---|---|---|
| Governance | **ERP Steering Committee** (`GV-002`) | Per `GV-002` | Monthly | Funding, `SV-001-D-04`, unfunded-item acceptance |
| Direction | **Service Management Board** (§8.2) | CTO (chair), Head of ITSM, Support Lead, Platform lead, Security lead, Operations Director, Quality Manager | **Monthly** | SLO changes, practice adoption, service ownership, problem prioritisation |
| Operational control | **Daily service review** | Head of ITSM or Support Lead, T1 supervisor, on-call primary | **Daily, 09:30 BST, 15 min** | Today's risk: open incidents, breach-risk queue, overnight handover, change calendar |
| Incident | **Incident command** | Per `OP-013` §4.6 | On declaration | `SV-006` §4 |
| Change | **CAB** | Per `RL-001` §8.2 | Per `RL-001` | Normal changes |
| Improvement | **Problem review** | Head of ITSM, service owners, Quality Manager | **Fortnightly** | Problem records, known errors, permanent-fix priority (`SV-006` §5.5) |

> **`SMF-13`. The daily service review is fifteen minutes and it is not optional.** It is the only
> control that makes the manual half of the interim model (§7.4) visible on the day it fails rather
> than in the monthly report. `OP-001` §4.11 already measures it — *"Breach-risk review completed:
> daily during W1–W5 interim, target 100%"* — and this framework makes it permanent rather than
> interim, because the reason it works does not expire at W6.

### 8.2 The Service Management Board — terms of reference

| Attribute | Value |
|---|---|
| Purpose | To direct the SMS: to own the service portfolio, approve service levels, hold service owners to account, and decide what improves next |
| Chair | Chief Technology Officer |
| Secretary | Head of IT Service Management |
| Quorum | Chair or deputy, Head of ITSM, and at least one of Support Lead / Platform lead |
| Standing agenda | 1. Service report (§11.4) · 2. `Sev1`/`Sev2` since last · 3. Problems and their age · 4. SLO attainment and error budget · 5. Changes: success rate and emergency proportion · 6. Risks and unfunded items (§12) · 7. Decisions |
| Escalates to | ERP Steering Committee, monthly, on one page |
| Minutes | Recorded in [`GV-003`](../00_Programme_Governance_and_Control/GV-003_Decision_Log_and_Change_Control_Procedure.md); decisions of programme effect become `D-nnn` there |

### 8.3 Service management RACI

Roles are those in `GV-002`. **A** = accountable (exactly one), **R** = responsible, **C** =
consulted, **I** = informed.

| Activity | CTO | Head of ITSM | Support Lead | Service owner | Platform lead | Security lead | Ops Director | Quality Mgr | CFO |
|---|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| SMS policy (this document) | **A** | R | C | C | C | C | C | C | I |
| Service portfolio (§5.2) | A | **R** | C | C | C | C | C | I | I |
| Service level agreement (`SV-002`) | A | R | C | R | C | I | **C** | I | C |
| Incident management (day to day) | I | A | R | R | R | C | I | I | — |
| **Major incident command** (`SV-006`) | **A** | C | R | R | R | C | R | I | C |
| Problem management | I | **A** | C | R | R | C | I | R | — |
| Change enablement | A | R | C | R | R | C | C | C | — |
| Emergency change during an incident | C | I | I | R | C | C | I | I | — |
| On-call rota and paging (`SV-004`) | **A** | R | C | R | R | R | I | I | C |
| Runbook currency (`SV-003`) | I | A | I | **R** | R | R | — | C | — |
| Hypercare entry and exit (`SV-005`) | C | R | R | C | C | I | **C** | C | C |
| Service continuity and DR exercise | **A** | R | I | R | R | C | C | R | C |
| Service report and improvement | I | **A** | R | R | C | C | C | R | I |
| Funding the establishment (§8.4) | R | C | C | I | I | I | C | I | **A** |

### 8.4 The establishment — one table, one number

`OP-001` §4.7 sizes the tiers. `OP-013` §4.3 sizes the rotas. `M66` §18 Q-02 asks the question. §5.4
adds twenty-one owner names. **Four documents, four fragments, no single figure a CFO can act on.**
This is that figure.

| Role | W1 | W4 | W8 | Source | Funded? |
|---|:--:|:--:|:--:|---|:--:|
| **Head of IT Service Management** | **1.0** | 1.0 | 1.0 | §4.1 — the SMS manager. **Does not exist today** | ✗ |
| T1 service desk analysts | **2.0** | 4.0 | 6–8 | `OP-001` §4.7 | ✗ |
| T2 domain specialists (finance, ops, data) | 1.5 | 3.0 | 4–5 | `OP-001` §4.7 | ✗ |
| T3 platform engineers — **dedicated** | 0 | 2.0 | 3–4 | `OP-001` §4.7 | ✗ |
| **Platform on-call rota members** | **6** headcount | 6 | 6 | `OP-013` §4.3 — *"at four it is one-in-four, at which point people leave"* | ✗ |
| **Security on-call rota members** | **4** headcount | 4 | 4 | `OP-013` §4.3 | ✗ |
| Data engineering rota (business hours) | 2 | 2 | 2 | `OP-013` §4.3 | ✗ |
| Business escalation duty managers | 4 | 4 | 4 | `OP-013` §4.3 | ✗ |
| Executive escalation (CTO + named deputy) | 2 | 2 | 2 | `OP-013` §4.3 | ✓ (existing roles) |
| Champion network | 1 per pilot branch | 1 per branch | 1 per branch, **51+** | `OP-001` §4.7, `CM-008` | ✗ |
| **Named service owners** | **21** accountabilities | 21 | 21 | §5.2, §5.3 — **held alongside engineering roles, ~0.5 day/month each** | ✗ |

> **`SMF-15`. The rota headcounts and the T3 line are the same people.** Six platform rota members
> at W1 are drawn from the delivery squad, not added to it — which is precisely why `OP-002`'s
> hypercare ring-fencing (`OP-002-OI-01`) and this rota compete for one pool, and why `SV-005` §6
> has to state the collision rather than assume both.
>
> **`SMF-16`. The additive W1 asks are three: the Head of ITSM (1.0 FTE), two T1 analysts, and the
> on-call allowance terms.** Everything else at W1 is an *allocation* of existing delivery capacity,
> and stating that distinction is what lets the CFO price a decision instead of a wish list.

### 8.5 Competence (ISO/IEC 20000-1 §7.2)

| Role | Must be able to | Evidence | Refresher |
|---|---|---|---|
| T1 analyst | Classify, route, use the macro library, know what never to do (`OP-001` §4.10) | `TR-*` induction + 5 supervised shifts | Annual |
| On-call primary | Execute every `P0` procedure in the runbooks for the services they cover; declare; command a `Sev2` | **Two shadowed shifts** (`OP-013` `RT-06`) + one drilled `Sev1` | Per rota cycle |
| Incident Commander | Command without troubleshooting (`OP-013` §4.6) | One observed exercise, one real incident as deputy IC | Annual |
| Service owner | The seven obligations in §5.3 | Signed acceptance; first service report delivered | On appointment |
| Review facilitator | Run a blameless review (`OP-016` §4.2) | Two co-facilitated reviews | Annual |

> **`SMF-17`. Nobody holds a rota position on the strength of a job title.** `OP-013` `RT-06` sets
> the shadowing rule and `RT-07` sets the access rule — *"an on-call engineer without production
> authority is a pager with no hands"*. Both are competence controls and both are unenforceable
> until the 38 access profiles exist (`AUDIT-017` `OP-10`).

---

## 9. Configuration and Knowledge

### 9.1 The problem

`M66` `FR-ITS-029` specifies a CMDB with service mapping that answers *"what breaks if this
fails"*, deliberately shallow, populated by discovery, two relationship levels maximum
(`M66` `T-06`). **It arrives at W6 inside `CD-164`, and `CD-164` does not move** (§7.2).

So from W1 to W6 there is no CMDB, and impact assessment during an incident is a conversation
between whoever is awake. `OP-001` §4.9 names the substitute — *"`OP-007`…`OP-011` runbooks"* — and
that is right for *how to fix it* and wrong for *what else breaks*, because a runbook describes its
own component's dependencies downward and never upward.

### 9.2 The shallow configuration register — what the programme can afford

> **`SMF-18`. A service-dependency register of exactly two relationship levels is maintained from
> W1, by hand, as a single table in `SV-003`.** It is not a CMDB and is not called one.

| Property | Value |
|---|---|
| Rows | **21** — one per service in §5.2 |
| Columns | Service · owner · depends-on (services) · depended-on-by (services) · environment · criticality · runbook · SLO ref |
| Depth | **Two levels.** `M66` `T-06` gives the reason and it applies more strongly to a hand-maintained register: *"deeper modelling is not maintained and therefore not trusted"* |
| Maintenance | Updated **in the change record** (`SP-031` §5.3 step 21) — never as a separate task, because a separate task is the task that stops |
| Review | Quarterly by the Service Management Board; any row untouched for two quarters is marked **unverified**, following `M66` `BRU-ITS-18` |
| Superseded by | `M66` `FR-ITS-029` at W6; the 21 rows become the seed of the CMDB's service mapping |
| Cost | Roughly **half a day to create, one hour a month to maintain** |

> **Why this is worth stating as a rule.** The alternative to a 21-row table is not a better CMDB;
> it is nothing, followed at W6 by a discovery run against an estate nobody has ever mapped. **A
> register that is trivially cheap and known to be shallow beats an absent one and beats a deep one
> that decays** — which is the same argument `M66` §4 makes, applied twenty months earlier and with
> a smaller budget.

### 9.3 Knowledge

| Layer | Instrument | Owner | From |
|---|---|---|:--:|
| User-facing self-help | `HC` help centre set, `UI-005` system messages | Content Design | W1 |
| Agent-facing responses | `OP-003` — **68 macros** | Support Lead | W1 |
| **Known errors** | `KB` articles tagged `known-error` (interim) → `M66` `FR-ITS-016` known-error database | Head of ITSM | W1 → W6 |
| Engineer-facing procedures | `SV-003` runbook set | Service owners | W1 |
| Post-incident learning | `OP-016` reports, published internally without names | Review facilitator | W1 |

> **`SMF-20`. A known error is published when a fault has occurred a second time, not when it is
> understood.** `OP-001` `DF-01` sets the volume trigger (20 contacts/month → a macro and a help
> article within one month); this rule sets the recurrence trigger. Waiting for root cause before
> publishing a workaround is how the third occurrence reaches a human.

---

## 10. The Seams

Eleven documents touch this one. A seam that is not stated is a seam two people will each assume
the other owns.

| Neighbour | This document owns | The neighbour owns | The seam |
|---|---|---|---|
| [`OP-001`](../../project_content/17_Operations_Support_and_Runbooks/OP-001_Support_Model_Tiering_and_Routing_Content.md) | Governance, ownership, practice set, establishment, the `M66` ruling | Tiers, routing, channels, response commitments, populations | **Adopted by citation.** `SMF-02` forbids restating any of it |
| `OP-013` | Nothing of severity | **The `Sev1`–`Sev4` scale, authority table, handover format** | This document names `OP-013` §4.1 as canonical, in one place, and stops (`AUDIT-017` `OP-04`) |
| `SV-002` | The service list (§5.2) that SLOs are indexed by | Every number: SLI, SLO, error budget, OLA, service catalogue publication | §5.2 is the index; §11.2 is the measurement frame; the targets are not here |
| `SV-003` | `NFR-091`'s ruling (§6.5), `G3-on-build` (§6.6), the 21-row dependency register (§9.2) | The runbook standard, the master set, the module-runbook mechanism | This document decides *that* they exist; `SV-003` decides *what one is* |
| `SV-004` | That the rota is an establishment line (§8.4) | Rota structure, **paging platform**, severity-to-page mapping, acknowledgement SLAs | §7.7 states explicitly that the `M66` ruling does not close the paging gap |
| `SV-005` | The permanent operating model hypercare hands over to | Hypercare posture, per-wave duration, exit criteria, transition | `SV-005`'s exit criterion `HX-15` is *this* model being staffed and briefed |
| `SV-006` | The practice map (§6.2) and the three record relationships (§6.4) | Major incident command, problem practice, PIR procedure, BIA | `SV-006` §4 begins where `OP-013` §4.5 declaration ends |
| [`RL-001`](../12_Release_Deployment_and_Transition/RL-001_Release_Management_and_Versioning_Policy.md) | Change **enablement** as an SMS practice | Release taxonomy, cadence, freeze windows, CAB constitution, versioning | A production change is governed by `RL-001`; **an emergency change during an incident is governed by `SV-006` §5.4 and reviewed by `RL-001`'s CAB** |
| [`SC-011`](../05_Security_Privacy_and_Compliance/SC-011_Security_Incident_Response_Plan.md) | The route in (`Q-SEC` + page, `OP-001` §4.3) | Security classification, breach assessment, notification decision | **`M66` `BRU-ITS-21` is absolute**: the service management process makes no security judgement. `SV-006` §7.1 states the handover point |
| [`QA-010`](../08_Quality_Engineering_and_Test/QA-010_Defect_Management_and_Quality_Gate_Standard.md) | That an incident may **produce** a defect | `S1`–`S4`, triage, deferral, quality gates | §6.4: two records, linked, each keeping its own scale |
| [`PE-007`](../10_Infrastructure_DevOps_and_Environments/PE-007_Backup_Disaster_Recovery_and_Business_Continuity_Design.md) **(issued)** | The continuity **practice** (§6.2 row 8) and its exercise obligations | Backup design, restore verification, failover sequence, `Z4` recovery routes, the drill programme | `PE-007` designs; **`SV-006` §9 governs the business-impact and declaration side**. The `dr` environment is designed and **not provisioned** |
| [`PE-008`](../10_Infrastructure_DevOps_and_Environments/PE-008_Observability_and_Monitoring_Design.md) **(issued)** | The monitoring and availability practices (§6.2 rows 5, 9); **the severity ruling in §6.7** | Signals, correlation, sampling, **eight SLOs**, burn-rate alerting, routing, alert discipline, dashboards | **`PE-008` produces the alert; this category responds to it** — `PE-008` §1.1 says so. §6.7 records the one disagreement, on severity |
| [`PE-009`](../10_Infrastructure_DevOps_and_Environments/PE-009_Configuration_and_Secrets_Management_Standard.md) **(issued)** | Nothing of secrets | Configuration hierarchy, feature flags, secret classes and rotation, **the break-glass procedure** | `PE-009` §8 designs break-glass, closing the design half of `AUDIT-017` `OP-08`; **`SV-004` owns the rota half `OP-08` bundles with it** |

---

## 11. Measurement and Continual Improvement

### 11.1 What is measured, and the honest position

`SP-031` §12 already registers seven KPIs (`KPI-085`…`091`) — and records for **every one of them**
that `06-02` states no baseline. `M66` §15 adds sixteen metrics, none of which carries a canonical
`KPI-0nn` identifier (`M66` §15 register note). `OP-001` §4.11 and `OP-013` §4.12 add sixteen more.

> **`SMF-21`. This framework registers no new metric identifier.** It adopts the existing sets and
> states, once, which of them can actually be produced at W1 and which cannot. Inventing a
> twenty-fourth identifier space into an estate with `RR-002` unwritten would be the eighth
> identifier event, not a measurement improvement.

### 11.2 The measurement frame

| Layer | Question | Instrument | Available at W1? |
|---|---|---|:--:|
| **Service level** | Are we keeping the promises we made? | `PE-008` §7's eight SLOs; `SV-002` §5's twenty-one; error budgets | ◐ **Designed, unbuilt** *(corrected §0)* — and the two SLO sets must be reconciled, `SV-002` §5.8 |
| **Practice health** | Are the practices working? | `KPI-085`…`091`, first-contact resolution, escalation accuracy, reopen rate | ◐ **Partly** — ticket-system metrics depend on `SV-001-D-04`; uptime and latency on `PE-008` being instrumented |
| **Response** | When it breaks, how fast? | `OP-013` §4.12 — time to acknowledge, declare, communicate, restore | ⛔ **No paging system to measure acknowledgement against** (`SV-004`) |
| **Learning** | Does anything change? | `OP-016` §4.10 — action closure rate, recurrence count, contributing-factor tag distribution | ✅ **Yes** — this one needs no tooling |
| **Load** | Is the rota sustainable? | `OP-013` §4.11 — pages/shift, out-of-hours pages, consecutive weeks | ⛔ No paging system |

> **`SMF-F-04` (revised). Two of five measurement layers remain hard-blocked, and both are blocked on
> the same missing thing: a paging platform.** *(At 01:53 this read four of five, blocked on
> `PE-007`, `PE-008` and an unprocured platform. `PE-007` and `PE-008` were issued at approximately
> 02:00 — §0.)* Service level and practice health moved from ⛔ to ◐: **designed, and not yet
> instrumented**. Response and load did not move, because no design in Category 10 pages anyone.
>
> **That is the finding of this category in one line.** The estate's designers have now closed every
> observability and continuity gap a design could close, and the two things still unmeasurable are
> the two that require an establishment and a purchase order.

### 11.3 Corrective action

Every corrective action arising from a review, a problem, an audit finding or a missed SLO is
raised in **`M23`** as a corrective action, not in a private list.

| Rule | Detail |
|---|---|
| `SMF-22` | `M23` `BRU-QMS-02` requires root cause and CAPA before a non-conformance closes; the SMS uses that mechanism rather than a parallel one. **1000FiX is ISO 9001:2015 certified and support has been outside the certified scope; this brings it in** |
| `SMF-23` | An action open at its due date is escalated to the CTO, never silently extended (`OP-016` `AC-06`) |
| `SMF-24` | **Decisions taken by this category are recorded in [`GV-003`](../00_Programme_Governance_and_Control/GV-003_Decision_Log_and_Change_Control_Procedure.md), not in `RF-006`.** `RF-006` does not exist and is blocking five content categories and 94 decisions (`AUDIT-017` `OP-12`). Category 11 does not add to that queue |

### 11.4 The service report

| Attribute | Value |
|---|---|
| Frequency | **Monthly**, to the Service Management Board; **quarterly** summary to the Steering Committee |
| Length | **Two pages.** A report nobody finishes is a report that changes nothing |
| Contents | SLO attainment per `P0` service · `Sev1`/`Sev2` count and time-to-restore · top three contributing-factor tags (`OP-016` §4.9) · problems opened/closed and their age · change success rate and emergency proportion · rota health · **the unfunded list from §12, unchanged until it changes** |
| Rule `SMF-25` | **The unfunded list is reprinted in full every month.** An unfunded control that stops being mentioned has been silently accepted, and `TG-01`'s `deferred-work` tag exists because that is the organisational cause reviews find most often |

### 11.5 Review triggers

Out-of-cycle review of this framework is triggered by: the Steering decision on `SV-001-D-04`
(either way) · `M66` go-live · any `Sev1` where authority, ownership or practice was disputed ·
publication of `PE-007` or `PE-008` · a rota breach · the first missed page · any change to
`NFR-006`, `NFR-007` or `NFR-045` · a wave gate that fails on operational readiness (`RL-003`).

---

## 12. What Cannot Be Evidenced Today

Carried from `AUDIT-017` §4 and extended. **No content action closes any of these.** They are
reprinted here, and monthly under `SMF-25`, because the alternative is that they are discovered
during the incident that needed them.

| # | Assertion the programme makes | Why it cannot be evidenced | Owner | Needed by |
|---:|---|---|---|:--:|
| 1 | `NFR-007` — RPO ≤ 15 min, RTO ≤ 2 h | **`PE-007` now designs all of it** — WAL archiving, the immutable copy, restore verification, failover. **None of it is provisioned**, and the `dr` environment is still unsized and uncosted. *"Designed"* and *"operating"* are two of §4.3's four words apart | CTO | **W2** |
| 2 | **A lawful DR path exists for Bangladesh-resident personal data** | `AUDIT-017` `OP-01`, **CRITICAL**. **`PE-007` §7 designs two routes and §7.5 records the decision as *forced and unmade*.** The finding moves from *no design* to *no decision*, which is progress and is not closure | CTO + Legal + DPO | **W2** |
| 3 | `NFR-045` — 24×7 availability ≥ 99.7% | No staffed rota (§8.4), **no paging platform at all** | CTO + HR | **W1** |
| 4 | `NFR-050` — every `P0` integration has a **tested** manual fallback | 13 procedures exist; the printed forms, the reserved Mushak ranges and the drills do not | Operations + Tax | **W1** |
| 5 | `KPI-090` — zero orphaned accounts beyond 24 h (and `BRU-SEC-06`'s one hour) | No JML automation before W6; **no access profiles**; no recertification tooling | Security Lead | W1 |
| 6 | Break-glass access is available | **`PE-009` §8 now designs it** — trigger, issue, announce-at-issue, rotation, `BG-01`…`BG-06`, and `BF-01`'s rule that it must not depend on the system being available. **None of the five physical components exists yet**: no vault path provisioned, no sealed envelope, no safe procedure, no named signatories, no test. `AUDIT-017` `R-07` still holds — *the cheapest high-severity remediation available* | Security Lead | **Before W1 go-live** |
| 7 | The status page is independent of the estate it reports on | `OP-005` `SP-10` requires independent hosting; `02-05` §8 provisions none. In a `Sev1` the single source of truth may be unavailable | Platform Engineering | W2 |
| 8 | Emergency spend can be authorised during an incident | No delegated authority exists; `OP-013` §4.8's limits are **proposed**. The CTO is the only spend authority at 02:00 | **CFO** | W1 |
| 9 | The `P0` bilingual fallback pack is usable by its audience | `OP-014` is written to be printed in Bengali and held at 51+ counters; **the Bengali counterpart file does not exist** | Localisation Lead | **Before W1** |
| 10 | 67 module runbooks exist per `NFR-091` §7 | **Zero.** Ruled in §6.5, sized in `SV-003` §5 | CTO + Programme Office | W1 onward |

---

## 13. Governing Rules — Consolidated

| # | Rule | §  |
|---|---|:--:|
| **`SMF-01`** | No document in this category may assert that a control **operates**. Four permitted assertions, four evidence tests | 3.3, 4.3 |
| **`SMF-02`** | `OP-001`'s tier model, routing, channels and response commitments are **adopted by citation and never restated** | 1.1 |
| **`SMF-03`** | `OP-001` §4.1's derived enumeration of eleven external audiences is **the programme's definitive one** until the Steering Committee states otherwise | 2.3 |
| **`SMF-04`** | A service is something a named population depends on, that can be separately unavailable, with **one accountable owner** | 5.1 |
| **`SMF-05`** | The 21 service identifiers are the index for every SLO, runbook, escalation target and dashboard downstream | 5.2 |
| **`SMF-06`** | Every service has **one named individual** as owner. A team is not an owner | 5.3 |
| **`SMF-07`** | Service ownership is an accountability held alongside an engineering role, budgeted at ~0.5 day/month | 5.3 |
| **`SMF-08`** | A practice adopted in another category is **not adopted twice** here. Name the owner and stop | 6.3 |
| **`SMF-09`** | A ticket never changes type. A second record is created and linked | 6.4 |
| **`SMF-10`** | With `SV-001-D-04` approved, SLA attainment is reportable from W1 (`M30` holds the holiday set). **Stated conditionally; `OP-001` §4.9 is not edited on an untaken decision** | 7.5 |
| **`SMF-11`** | Where two current programme statements conflict, operate to the **stricter** and record the conflict. Never average | 7.6 |
| **`SMF-12`** | `CD-163` is an ITSM module, not a paging platform. Moving it to W1 **does not page anybody** | 7.7 |
| **`SMF-13`** | The daily fifteen-minute service review is permanent, not interim | 8.1 |
| **`SMF-14`** | `NFR-091` means what it says: **67 module runbooks**, delivered as templated appendices to the component runbook that covers their substrate | 6.5 |
| **`SMF-15`** | The rota headcounts and the T3 line are **the same people**; hypercare ring-fencing competes with them | 8.4 |
| **`SMF-16`** | The additive W1 asks are three: Head of ITSM, two T1 analysts, on-call allowance terms. The rest is allocation | 8.4 |
| **`SMF-17`** | Nobody holds a rota position on a job title. Shadowing (`RT-06`) and access (`RT-07`) are competence controls | 8.5 |
| **`SMF-18`** | A **two-level, 21-row service-dependency register** is maintained from W1, updated inside the change record, and is not called a CMDB | 9.2 |
| **`SMF-19`** | **`G3` is granted per procedure, not per file.** A procedure with no execution date displays as *unverified* | 6.6 |
| **`SMF-20`** | A known error is published on the **second occurrence**, not on root cause | 9.3 |
| **`SMF-21`** | This framework registers **no new metric identifier**; it adopts the existing sets and states what is producible | 11.1 |
| **`SMF-22`** | Corrective actions run through `M23` CAPA, bringing support inside the ISO 9001 certified scope | 11.3 |
| **`SMF-23`** | An action open at its due date escalates to the CTO; it is never silently extended | 11.3 |
| **`SMF-24`** | Category 11 decisions are recorded in **`GV-003`**, not in the non-existent `RF-006` | 11.3 |
| **`SMF-25`** | **The unfunded list (§12) is reprinted in full in every monthly service report**, unchanged until it changes | 11.4 |
| **`SMF-26`** | **A rule identifier cited outside its defining document is always written with that document's name.** `` `OP-013` `RT-04` `` and `` `PE-008` `RT-04` `` are different current rules | 6.7 |
| **`SMF-27`** | **Category 11 operates to `OP-013` §4.1's four-level severity scale.** `PE-008` §8.5's three-level model is mapped as an alerting classification, not adopted as the scale | 6.7 |

**Findings raised by this document**

| # | Finding | Severity | Owner |
|---|---|:--:|---|
| **`SMF-F-01`** | The **module** register assigns `M66` a wave by the module's own priority rather than by the wave of the `P0` content that consumes it — the same defect class as `AUDIT-017` `OP-05` and `QAA-10`, found for the first time in the module register rather than a content or document register | **HIGH** | Enterprise Architecture |
| **`SMF-F-02`** | Eight of thirty-three ISO/IEC 20000-1 clause rows are ⛔, and seven are owned outside this category | HIGH | CTO |
| **`SMF-F-03`** | The 9 PW to move `CD-163` is not additional work; it is the same work done once instead of twice, plus twenty months of measurable service | MEDIUM | CTO + CFO |
| **`SMF-F-04`** *(revised)* | **Two of five measurement layers remain hard-blocked, both on the absence of a paging platform.** Two moved to *designed and unbuilt* when `PE-007` and `PE-008` were issued | HIGH | CTO |
| **`SMF-F-05`** | **Twenty-one services require twenty-one named owners and zero people are named in any of the five owning functions.** This is `AUDIT-017` `OP-09` counted a second way, and it is why §8.4 sizes both against one establishment | HIGH | CTO + HR |
| **`SMF-F-06`** | **`PE-008` §8.5 asserts a three-level severity model owning a space `OP-013` §4.1 owns as four levels**, and allocates three rule prefixes (`SV-`, `RT-`, `AL-`) already in use with different meanings. §6.7 adjudicates for this category and recommends the correction | **HIGH** | Enterprise Architecture + Head of Service |
| **`SMF-F-07`** | **The estate moved nineteen files in a twenty-two-minute window during this document's authoring**, falsifying four absence claims in its first draft. Ninth recorded occurrence; `RG-08` and `RR-002` remain unratified | MEDIUM | Programme Office |

---

## 14. Decisions Recorded

| # | Decision | Options considered | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| **`SV-001-D-01`** | Conformance posture to ISO/IEC 20000-1 | (a) Seek certification; (b) conform without certifying; (c) ignore the standard | **(b)** | Certification costs an audit programme the Company is not funded for; the clause map delivers the value — an enumerated gap list — at the cost of one table | §4.2 must be re-run at each annual review; a future certification decision starts from a known position |
| **`SV-001-D-02`** | Practice scope | (a) All 34 ITIL 4 practices; (b) `M66`'s four; (c) twelve | **(c)** | Four is right for an internal IT desk and insufficient for a platform with 21 services and a 99.95% payment path. Thirty-four is nominal adoption, which `M66` §4 already rejected | Twenty-two practices carry a named reason and a review wave (§6.3) |
| **`SV-001-D-03`** | `NFR-091` — 67 module runbooks | (a) Component runbooks discharge it; (b) it means what it says | **(b)** | Two independent statements of the obligation exist (`05-06` §7, `02-05` §9). Amending a `P0` requirement to make a register look complete is the `PGD-A2-24` defect class | 67 module runbooks become a registered obligation, sized in `SV-003` §5 |
| **`SV-001-D-04`** | The `M66` W1/W6 problem | (a) Accept the interim as stated in `OP-001` §4.9; (b) move all of `M66` to W1; (c) **split by dependency: `CD-163` → W1, `CD-164` → W6** | **(c)** | Every prerequisite `M66` §16.3 cites for W6 (`M21`, `M06`, `M18`, `M49`) belongs to `CD-164` alone. `CD-163` has no dependency later than W1 | **9 PW moves forward (0.6% of the build estimate).** Requires a Steering decision and a `06-01` change. **Does not close the paging gap** (§7.7) |
| **`SV-001-D-05`** | Error budgets and release freezes | (a) Error-budget exhaustion freezes releases (Google SRE default); (b) it does not | **(b)** | `RL-001` §7 derives freeze authority from statutory and financial cycles — VAT, payroll, close, cutover. A burn-rate freeze would compete with a statutory one and lose, publicly | Error budgets inform prioritisation and the Service Management Board agenda; they do not gate a release. `SV-002` §6 implements this |
| **`SV-001-D-06`** | Where Category 11 decisions are logged | (a) `RF-006`; (b) `GV-003` | **(b)** | `RF-006` does not exist and blocks 94 decisions across five categories (`AUDIT-017` `OP-12`). `GV-003` is issued | This category's Definition of Done is completable; the content estate's remains blocked, which is the correct place for the pressure |

---

## 15. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|:--:|---|
| **`SMF-Q-01`** | **Is the Head of IT Service Management role created and filled?** The SMS has an accountable owner (CTO) and no responsible manager | CTO + HR Director | **W1** | Every clause of §4.2 that requires an operating manager; the daily review; the service report |
| **`SMF-Q-02`** | **Is `SV-001-D-04` approved** — does `CD-163` move to W1? | ERP Steering Committee | **W1 minus 8 weeks** | `SV-002` measurability, `SV-005` hypercare tooling, `SV-006` problem practice, `M66` §18 Q-04 |
| **`SMF-Q-03`** | Are the twenty-one service owners named? | CTO | W1 | `SV-002` SLO proposal, `SV-003` runbook ownership, `SV-004` escalation targets |
| **`SMF-Q-04`** | Does Content Design accept the conditional correction to `OP-001` §4.9 (§7.5), to be applied only if `SMF-Q-02` resolves affirmatively? | Programme Content Lead | W1 | `OP-001`'s KPI reporting statement |
| **`SMF-Q-05`** | Is leaver revocation one hour (`BRU-SEC-06`) or 24 hours (`KPI-090`)? | CFO + Internal Audit | W1 | `OP-015` §4.6; `AUDIT-017` `OP-15` |
| **`SMF-Q-06`** | Is support brought inside the ISO 9001 certified scope at the next surveillance audit? | Quality Manager | W2 | `SMF-22`; `M23` CAPA routing |
| **`SMF-Q-07`** | Does the Steering Committee confirm `OP-001` §4.1's eleven external audiences (`SMF-03`)? | Programme Office | W1 | `HC-015` contact routes; `SV-002` catalogue audiences |
| **`SMF-Q-08`** | Who holds liability for retired end-of-life devices containing customer data between W6 and `M18` at W8? | Quality Manager + CTO | W6 | `M66` Q-10, unresolved; a PDPA exposure with no owner |

> An open question with no owner and no needed-by date is not an open question — it is an unrecorded
> risk. All eight are raised in [`GV-005`](../00_Programme_Governance_and_Control/GV-005_RAID_Register.md) RAID.

---

## 16. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| `AC-01` | The SMS has a named accountable owner and a named responsible manager | §4.1; **`SMF-Q-01` open** |
| `AC-02` | Every ISO/IEC 20000-1 clause is mapped to an artefact or recorded as ⛔ with an owner | §4.2 — 33 rows, 13 ✅ / 12 ◐⚠ / 8 ⛔ |
| `AC-03` | The climate-change determination required by Amd 1:2024 §4.1/§4.2 is recorded | §4.4 |
| `AC-04` | Every service has one accountable owner recorded by name | §5.2 lists 21; **`SMF-Q-03` open — zero named** |
| `AC-05` | Every adopted practice names its specifying document and its live-from wave | §6.2 — twelve rows |
| `AC-06` | Every deferred practice names a reason and a review wave or its owning category | §6.3 |
| `AC-07` | The `M66` W1/W6 conflict is ruled, priced, and the residual gap named | §7; `SV-001-D-04`; §7.7 |
| `AC-08` | The establishment is expressed as **one** table a CFO can price | §8.4 |
| `AC-09` | No rule in this category uses the identifier form `SV-nn` | §2.4; verified by extraction |
| `AC-10` | Nothing that cannot be evidenced is asserted as operating | §12; `SMF-01` |
| `AC-11` | Every relative link resolves | Verified at issue |
| `AC-12` | No metric identifier is invented | §11.1; `SMF-21` |

**Definition of done.** Complete when every criterion above is met, its `PGD-000` status is updated
with a fresh enumeration timestamp, and its approver has signed. **`AC-01` and `AC-04` cannot be met
by this document** — they are met by an appointment and a set of names, which is precisely the
distinction §4.3 exists to preserve.

---

## 17. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | [`GV-002`](../00_Programme_Governance_and_Control/GV-002_Governance_Framework_RACI_and_Terms_of_Reference.md) | The Service Management Board reports into the body `GV-002` constitutes |
| Upstream | [`GV-007`](../00_Programme_Governance_and_Control/GV-007_Estimation_Model_and_Resource_Plan.md) | §8.4's establishment belongs in its resource plan |
| Upstream | [`GV-009`](../00_Programme_Governance_and_Control/GV-009_Wave_Gate_and_Phase_Exit_Criteria_Handbook.md) | Operational readiness is gate evidence |
| Upstream | [`PE-001`](../10_Infrastructure_DevOps_and_Environments/PE-001_Infrastructure_and_Network_Architecture_Design.md), [`PE-005`](../10_Infrastructure_DevOps_and_Environments/PE-005_Containerisation_and_Orchestration_Design.md), [`PE-006`](../10_Infrastructure_DevOps_and_Environments/PE-006_Capacity_Plan_and_Performance_Engineering_Baseline.md) | The estate operated: availability scopes, component inventory, capacity triggers |
| Upstream ✅ | [`PE-007`](../10_Infrastructure_DevOps_and_Environments/PE-007_Backup_Disaster_Recovery_and_Business_Continuity_Design.md), [`PE-008`](../10_Infrastructure_DevOps_and_Environments/PE-008_Observability_and_Monitoring_Design.md), [`PE-009`](../10_Infrastructure_DevOps_and_Environments/PE-009_Configuration_and_Secrets_Management_Standard.md) | **Issued during this document's authoring window (§0).** Continuity, observability and break-glass are designed. §6.7 records the one disagreement |
| Downstream | `SV-002` | Takes the 21-service index and sets the numbers |
| Downstream | `SV-003` | Takes `SMF-14`, `SMF-19` and the §9.2 register |
| Downstream | `SV-004` | Takes §8.4's rota lines and §7.7's unresolved paging gap |
| Downstream | `SV-005` | Hands hypercare over to this operating model (`HX-15`) |
| Downstream | `SV-006` | Takes §6.2's practices 1, 6, 8 and §6.4's relationships |
| Lateral | [`RL-001`](../12_Release_Deployment_and_Transition/RL-001_Release_Management_and_Versioning_Policy.md), [`SC-011`](../05_Security_Privacy_and_Compliance/SC-011_Security_Incident_Response_Plan.md), [`QA-010`](../08_Quality_Engineering_and_Test/QA-010_Defect_Management_and_Quality_Gate_Standard.md) | §10's seams |
| Lateral | [`M66`](../../1000fix_ERP_Module/03_Modules/K_Platform_and_Technology/M66_Internal_IT_Service_Management.md) | The module this framework splits, and the module that will support it |
| Lateral | [`OP-001`](../../project_content/17_Operations_Support_and_Runbooks/OP-001_Support_Model_Tiering_and_Routing_Content.md), [`OP-013`](../../project_content/17_Operations_Support_and_Runbooks/OP-013_On_Call_Escalation_and_Handover_Content.md), [`OP-016`](../../project_content/17_Operations_Support_and_Runbooks/OP-016_Post_Incident_Review_Template_and_Register.md), [`SP-031`](../../project_content/06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-031_SOP_IT_Service_Desk_and_Change_Management.md) | Content adopted by citation |

---

## 18. References

**Within this repository**
[`PGD-000`](../PGD-000_Master_Register_of_Project_Guiding_Documents.md) ·
[`_CATEGORY_OVERVIEW.md`](_CATEGORY_OVERVIEW.md) ·
`SV-002`, `SV-003`, `SV-004`, `SV-005`, `SV-006` ·
[`GV-002`](../00_Programme_Governance_and_Control/GV-002_Governance_Framework_RACI_and_Terms_of_Reference.md) ·
[`GV-003`](../00_Programme_Governance_and_Control/GV-003_Decision_Log_and_Change_Control_Procedure.md) ·
[`GV-005`](../00_Programme_Governance_and_Control/GV-005_RAID_Register.md) ·
[`GV-007`](../00_Programme_Governance_and_Control/GV-007_Estimation_Model_and_Resource_Plan.md) ·
[`GV-009`](../00_Programme_Governance_and_Control/GV-009_Wave_Gate_and_Phase_Exit_Criteria_Handbook.md) ·
[`GV-011`](../00_Programme_Governance_and_Control/GV-011_Documentation_Control_and_Configuration_Management_Plan.md) ·
[`PE-001`](../10_Infrastructure_DevOps_and_Environments/PE-001_Infrastructure_and_Network_Architecture_Design.md) ·
[`PE-002`](../10_Infrastructure_DevOps_and_Environments/PE-002_Environment_Strategy_and_Specification.md) ·
[`PE-005`](../10_Infrastructure_DevOps_and_Environments/PE-005_Containerisation_and_Orchestration_Design.md) ·
[`PE-006`](../10_Infrastructure_DevOps_and_Environments/PE-006_Capacity_Plan_and_Performance_Engineering_Baseline.md) ·
[`RL-001`](../12_Release_Deployment_and_Transition/RL-001_Release_Management_and_Versioning_Policy.md) ·
[`SC-011`](../05_Security_Privacy_and_Compliance/SC-011_Security_Incident_Response_Plan.md) ·
[`QA-010`](../08_Quality_Engineering_and_Test/QA-010_Defect_Management_and_Quality_Gate_Standard.md) ·
[`MG-007`](../09_Data_Migration_and_Cutover/MG-007_Rollback_and_Fallback_Plan.md) *(rule-space collision check)*

**Workspace**
[`M66`](../../1000fix_ERP_Module/03_Modules/K_Platform_and_Technology/M66_Internal_IT_Service_Management.md) ·
[`05-06`](../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06_NonFunctional_Requirements_and_Standards.md) ·
[`OP-001`](../../project_content/17_Operations_Support_and_Runbooks/OP-001_Support_Model_Tiering_and_Routing_Content.md) ·
[`OP-002`](../../project_content/17_Operations_Support_and_Runbooks/OP-002_Hypercare_Plan_and_Exit_Criteria.md) ·
[`OP-013`](../../project_content/17_Operations_Support_and_Runbooks/OP-013_On_Call_Escalation_and_Handover_Content.md) ·
[`OP-016`](../../project_content/17_Operations_Support_and_Runbooks/OP-016_Post_Incident_Review_Template_and_Register.md) ·
[`SP-031`](../../project_content/06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-031_SOP_IT_Service_Desk_and_Change_Management.md) ·
[`AUDIT-017`](../../project_content/_AUDIT/AUDIT-017_Category_17_OP_Content_Audit.md)

**External standards and sources** *(each verified 2026-08-19)*

| Source | Verified |
|---|:--:|
| ISO/IEC 20000-1:2018 — Service management system requirements | 2026-08-19 |
| ISO/IEC 20000-1:2018/**Amd 1:2024** — Climate action changes, published 2024-02-23 · https://www.iso.org/standard/88434.html | 2026-08-19 |
| ISO 22301:2019/**Amd 1:2024** — Climate action changes, published February 2024 · https://www.iso.org/standard/88412.html | 2026-08-19 |
| ISO 9001:2015 cl. 8.5.1, cl. 10.2 | 2026-08-19 |
| ITIL 4 practice model — 34 practices across three categories | 2026-08-19 |
| Google SRE Workbook, *Alerting on SLOs* · https://sre.google/workbook/alerting-on-slos/ | 2026-08-19 |
| Atlassian Opsgenie end of life — end of sale 2025-06-04, shutdown **2027-04-05** | 2026-08-19 |

---

## 19. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-19 | Head of IT Service Management | Initial issue. Rule space `SMF` allocated after verification against 763 files. Six decisions recorded, of which `SV-001-D-04` (the `M66` split) requires a Steering Committee resolution and a `06-01` change | Chief Technology Officer *(pending — no constituted body exists, `PGD-A2-25`)* |
| **1.1** | **2026-08-19** | Head of IT Service Management | **Baseline correction, re-enumerated 02:15 (+06).** `PE-007`, `PE-008`, `PE-009` and `RL-002`…`RL-005` were issued by concurrent sessions during authoring; four absence claims corrected and §0 added. **Clause-map figures regenerated by extraction — the first draft's "33 rows" was wrong; the table has 30.** New §6.7 adjudicates the severity-model conflict `PE-008` §8.5 introduces. Rules `SMF-26`, `SMF-27`, decision `SV-001-D-07` and findings `SMF-F-06`, `SMF-F-07` added; `SMF-F-02` and `SMF-F-04` revised | As above |
| **1.2** | **2026-08-19** | Head of IT Service Management | **Conformance to `RR-002`, issued 02:41 (+06) during this category's audit.** `rule_prefix:` gains the timestamp and denominator `IDC-08` requires. `SMF-26` recorded as a local restatement of `RR-002` `IDC-07`, which now governs. **The v1.1 claim that *"`RR-002` is now recommended for the eighth time"* is corrected — it exists.** Clause-map ISO references made precise (§8.6 → §8.6.1). | As above |

---

*`SV-001` · Category 11 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
