---
id: SV-002
title: Platform SLA / OLA and Internal Service Catalogue
category: 11 — Service Operations & Support
code: SV
project: 1000FiX ERP System v2.0
version: 1.2
date: 2026-08-19
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Head of IT Service Management
approver: Chief Technology Officer, jointly with the Operations Director, endorsed by the ERP Steering Committee
standards_basis: >
  ISO/IEC 20000-1:2018 + Amd 1:2024 §8.2.1 service catalogue, §8.3.3 service level management,
  §8.7.2 service availability management · ITIL 4 service level management practice ·
  Google SRE — service level indicators, objectives and error budgets; multiwindow multi-burn-rate
  alerting · ISO/IEC 25010:2023 reliability and performance efficiency characteristics
traces_to: >
  PGD-000 SV-002 row (⬜) · SV-001 §5.2 (the 21-service index) · AUDIT-017 OP-03, OP-06, OP-14 ·
  05-06 §2 NFR-006, NFR-007, NFR-008, NFR-045…052, §1 NFR-001/002 · PE-001 §9.1 and PE-001-F-04 ·
  M66 §18 Q-03 · OP-001 §4.5, §4.6 · MD-028 · SP-031 §12 KPI-085…091
depends_on: >
  SV-001 (issued with this category) · PE-001…PE-009 (ALL NINE ISSUED — re-enumerated
  2026-08-19 02:15 (+06); PE-007 and PE-008 were issued by a concurrent session during this
  document's authoring window and this front matter is corrected accordingly — see §0) ·
  RL-001 (issued) · IN-007 (issued) · CO-003 (ISSUED 2026-08-19, during authoring) ·
  SV-004 (this category) · SV-006 (this category)
verified_on: 2026-08-19
enumeration_timestamp: 2026-08-19 02:15 (+06) — supersedes the 01:53 enumeration used at first draft
rule_prefix: PSL — verified to return zero occurrences in identifier form across all 763 markdown files of the workspace before allocation, at 2026-08-19 02:15 (+06); re-verified against the 786-file baseline at 02:56 (+06). Conforms to RR-002 IDC-08
priority: P1
needed_by: W2
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# SV-002 — Platform SLA / OLA and Internal Service Catalogue

### Category 11 · Code `SV` · Rule space `PSL` · ISO/IEC 20000-1:2018 §8.2.1, §8.3.3, §8.7.2 · SRE SLI/SLO practice

---

> **`PGD-000` states the gap this document fills:** *"The ERP defines SLAs it will **sell**
> (`MD-028`, `LG-015`). It defines no SLA it will **keep** to its own 500+ users across 51
> branches."*
>
> That is exactly right, and the position is a degree worse than it reads. The programme does not
> merely lack an internal SLA — **it holds four availability commitments it cannot currently
> measure, two of which are arithmetically incompatible with a third**, and it has never
> reconciled them. §5.6 shows that `NFR-045`'s 24×7 target of 99.7% permits **131.5 minutes** of
> monthly downtime while `NFR-049` permits **up to 240 minutes** of announced planned maintenance.
> Read together, the platform breaches its own 24×7 availability target **by doing planned
> maintenance**, before any incident occurs.
>
> Nobody has been wrong. Nobody has done the arithmetic.

---

## 0. Baseline Movement During Authoring — Read This First

> **⚠ `PE-008` Observability and Monitoring Design was issued while this document was being
> written**, and it defines **eight SLOs** where this document defines twenty-one. Both sets are
> now current. This section states what changed; **§5.8 reconciles the two sets and corrects three
> numbers in §5.2 and §5.3 that `PE-008` gets right and this document's first draft got wrong.**

Drafted against an enumeration at **2026-08-19 01:53 (+06)**; re-enumerated at **02:15 (+06)**.

| Claim as drafted at 01:53 | State at 02:15 | Where corrected |
|---|---|---|
| `PE-008` — **absent ⛔**; *"the single blocking dependency of this document"* | **Issued.** Defines eight SLOs with windows and error budgets, `VE-01`…`VE-05` valid-event rules, multi-window multi-burn-rate alerting, routing and alert discipline | §2.2 · §5.8 *(new)* · §6.4 · §11 |
| `PE-007` — absent ⛔ | **Issued.** `SLI-RPO` and `SLI-RESTORE` now have a design behind them | §5.2 · §11 |
| `SLI-DELIVER ≥ 99.5%` at 5 s | **Wrong.** `NFR-043` is *"≤ 5 s **p95**"*, which is 95%, not 99.5%. `PE-008` `SLO-05` reads it correctly | **§5.2, §5.3 — corrected to ≥ 95%** |
| `PSL-05`/`PSL-06`: availability **is** a synthetic-probe measure | **Incompatible with `PE-008` `VE-04`**, which excludes synthetic requests from SLIs | **§5.8.2 — both revised** |
| `S-12` at a proposed 99.9% | **`PE-008` `SLO-08` defers the `Z4` number to `SC-007` §9.5** and forbids folding it into any estate SLO | **§5.3 — deferred** |

> **Two independent convergences are worth recording, because they are evidence that the reasoning
> in both documents is sound.** `PE-008` `VE-05` excludes announced maintenance from SLIs — the same
> ruling as `SV-002-D-02`/`PSL-12`, reached separately. And `PE-008` §7.3 requires `SLO-04`'s SLI to
> exclude counterparty-attributable payment failures **and show them as a separate series** — which
> is `SV-002-D-03`'s three-way split arrived at by a different route.
>
> **`PSL-F-01` survives and gets sharper.** `PE-008` `VE-05` justifies the maintenance exclusion with
> *"the window is capped at 4 h/month, so this cannot be abused"*. **That cap is the problem, not
> the safeguard**: 4 h/month is 240 minutes against `SLO-02`'s 131.5-minute budget. The exclusion is
> right; the reason given for it is the reason it is **necessary**, not the reason it is safe.

---

## 1. Purpose

This document states **what the ERP platform promises the people who depend on it**: which services
exist, to whom, during which hours, at what availability and latency, what happens when a promise
is missed, and which of those promises rest on suppliers whose own commitments are weaker.

It exists because an availability number with no measurement window, no exclusion rule and no owner
is not a commitment — it is a sentence in a requirements register. Four such sentences exist
(`NFR-006`, `NFR-045`, `NFR-046`, `NFR-048`), they have different scopes, and `PE-001` `PE-001-F-04`
already recorded that two of them **do not state a measurement window at all**.

### 1.1 Scope

**In scope:**

| # | Covered |
|---|---|
| 1 | The **internal service catalogue** — the published form of `SV-001` §5.2's 21 services (§4) |
| 2 | **Service hours**, the maintenance window, and what "available" means (§4.4, §5.6) |
| 3 | **Service level indicators** — how each promise is actually measured, and from where (§5.2) |
| 4 | **Service level objectives** per service, derived from the NFR set and reconciled (§5.3) |
| 5 | The **composite-availability derivation** — why a 99.9% service needs 99.975% components (§5.5) |
| 6 | **Error budgets** in minutes, and the burn-rate policy that consumes them (§6) |
| 7 | **Operational level agreements** — what each internal function underpins the SLA with (§7) |
| 8 | **Underpinning contracts** — the eleven external dependencies and their exposure (§8) |
| 9 | **Breach handling** — what happens when a target is missed, and why there are no internal service credits (§9) |
| 10 | **Reporting and review** — the monthly service level report and its audience (§10) |

**Explicitly out of scope:**

| Topic | Owned by | Why the boundary sits here |
|---|---|---|
| Service **order** priority, severity bands and customer SLA clocks | [`MD-028`](../../project_content/02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-028_Priority_Severity_and_SLA_Definition_Register.md) | A customer's repair job and the platform are different things measured differently. `OP-001` §4.6 states the **only** relationship between them, and it is not restated here |
| Contractual SLAs and service credits **sold** to corporate clients | `M08`, `LG-003`, `LG-015` | Those are revenue instruments with legal remedies. This document commits nothing to a paying client |
| Client-facing managed services SLAs | `M05`, `SP-011` | A separate product with separate audits |
| Internal IT **ticket** SLA (laptop, printer, mailbox) | `M66` `FR-ITS-009` | Outside the SMS boundary (`SV-001` §4.1) |
| Metrics, logs, traces, dashboards, **SLI implementation and alert rules** | `PE-008` **(absent)** | §5.2 states what must be measured; `PE-008` states how. §11 carries the dependency rather than absorbing it |
| The paging that fires when a burn-rate threshold trips | `SV-004` §7 | §6.4 defines the thresholds; `SV-004` routes them |
| Capacity, scaling triggers, cost per transaction | [`PE-006`](../10_Infrastructure_DevOps_and_Environments/PE-006_Capacity_Plan_and_Performance_Engineering_Baseline.md) | Availability is a promise; capacity is what keeps it |
| Freeze windows and release authority | [`RL-001`](../12_Release_Deployment_and_Transition/RL-001_Release_Management_and_Versioning_Policy.md) §7, §8 | `SV-001-D-05`: **error budgets do not gate releases here** |

### 1.2 Intended audience

| Audience | What they use this document for |
|---|---|
| Operations Director and business owners | What the platform commits, in hours and minutes, and what it does not |
| Chief Technology Officer | The four unreconciled availability numbers, now reconciled (§5.6), and the four decisions in §13 |
| Head of IT Service Management | The catalogue to publish, the report to produce, the OLAs to negotiate |
| Platform / Security / Integration / Data Engineering | The OLA they are signing up to (§7) and the composite arithmetic that makes it necessary (§5.5) |
| Procurement and Legal (`CO-003`, `CO-004`) | The eleven underpinning contracts and the eight clauses each must carry (§8.4) |
| Branch managers and the Contact Centre | Service hours, what "degraded" means, and what to tell a customer |
| Internal Audit | The evidence set behind every reported number (§10.3) |

---

## 2. Basis and Inputs

### 2.1 Standards conformance

| Standard | Clause / section | How this document conforms | Departure and rationale |
|---|---|---|---|
| **ISO/IEC 20000-1:2018 + Amd 1:2024** | §8.2.1 service catalogue — services, their characteristics, dependencies, and availability to appropriate parties | §4 publishes the catalogue for all 21 services with audience, hours and dependencies | None |
| Same | §8.3.3 service level management — agreed targets, monitored, reviewed with the customer, with actions on missed targets | §5 sets targets, §10 reviews them, §9 acts on misses | **Departure: no service credit applies internally** (§9.2). ISO does not require a financial remedy; it requires an action. `SV-002-D-04` records the reasoning |
| Same | §8.7.2 service availability management — availability requirements derived from business needs, monitored, and recorded against targets | §5.3, §5.5, §10.2 | **Departure: monitoring does not exist at issue.** `PE-008` is absent; §11 states it as the blocking dependency rather than implying measurement |
| **ITIL 4** | Service level management practice — SLIs that reflect the user's experience, not the component's | §5.2 defines every SLI at the **journey** level where one exists, and at the component level only where no journey depends on it alone | None |
| **Google SRE** | SLI/SLO/error budget; multiwindow multi-burn-rate alerting; the 2% / 5% / 10% budget-consumption tiers over 1 h / 6 h / 72 h windows | §6.3 adopts the budget arithmetic; §6.4 adopts the alerting shape | **Departure: budget exhaustion does not freeze releases** (`SV-001-D-05`). `RL-001` §7 derives freeze authority from statutory and financial cycles |
| **ISO/IEC 25010:2023** | Reliability (availability, fault tolerance, recoverability); performance efficiency (time behaviour) | §5.3's SLO set covers availability, latency, correctness and recoverability rather than availability alone | None |

### 2.2 Source material relied on

| Source | Location | What it establishes |
|---|---|---|
| `SV-001` §5.2 | This category | **The 21 services.** Every SLO in this document is indexed by those identifiers and by nothing else (`SMF-05`) |
| `05-06` §2 Availability and Continuity | [`../../1000fix_ERP_Module/.../05-06`](../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06_NonFunctional_Requirements_and_Standards.md) | `NFR-006` ≥ 99.9% business hours · `NFR-045` ≥ 99.7% 24×7 · `NFR-046` portal ≥ 99.9% · `NFR-048` payment path ≥ 99.95% with multi-gateway failover · `NFR-007` RPO 15 min / RTO 2 h · `NFR-008` zero-downtime deployment · `NFR-049` maintenance window · `NFR-050`…`052` |
| `05-06` §1 Performance | Same | `NFR-001` ≤ 2 s p95 screens · `NFR-002` ≤ 400 ms p95 API · `NFR-031`…`044` — the per-journey latency set |
| **`PE-001` §9.1 and `PE-001-F-04`** | [`../10_.../PE-001`](../10_Infrastructure_DevOps_and_Environments/PE-001_Infrastructure_and_Network_Architecture_Design.md) | The four availability targets and their **scopes**; the finding that `NFR-046` and `NFR-048` state no measurement window, and that the difference is *"a factor of roughly 1.85 in permitted downtime"*; `HA-01`; §9.4's maintenance-window reconciliation |
| `PE-001` §9.2 | Same | HA by tier — which components are HA from W1 and which arrive at W2/W6 |
| `IN-007` §9.3 | [`../04_.../IN-007`](../04_Integration_and_API_Engineering/IN-007_Payment_and_Financial_Gateway_Integration_Design.md) | **`NFR-048` is unachievable for the card path at any infrastructure quality, because `INT-003` is the only card acquirer** |
| `PE-006` | [`../10_.../PE-006`](../10_Infrastructure_DevOps_and_Environments/PE-006_Capacity_Plan_and_Performance_Engineering_Baseline.md) | Volumetrics, scaling triggers, and the measurement that must happen first |
| `OP-001` §4.5, §4.6 | [`../../project_content/17_.../OP-001`](../../project_content/17_Operations_Support_and_Runbooks/OP-001_Support_Model_Tiering_and_Routing_Content.md) | **Support** response commitments per severity (adopted by citation, `PSL-02`) and the only sanctioned SLA-pause mechanism |
| `SP-031` §12 | [`../../project_content/06_.../SP-031`](../../project_content/06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-031_SOP_IT_Service_Desk_and_Change_Management.md) | `KPI-085`…`091`, each recorded as having **no baseline in `06-02`** |
| `M66` §18 Q-03 | [`../../1000fix_ERP_Module/.../M66`](../../1000fix_ERP_Module/03_Modules/K_Platform_and_Technology/M66_Internal_IT_Service_Management.md) | *"An SLA IT sets alone is a target, not an agreement"* — the question this document is written to answer |
| `AUDIT-017` `OP-03` | [`../../project_content/_AUDIT/AUDIT-017`](../../project_content/_AUDIT/AUDIT-017_Category_17_OP_Content_Audit.md) | `05-03`'s P0 count is wrong (**13, not 12**) and **`INT-013` email has no fallback entry**. Both bear directly on §8 |

**External sources, verified 2026-08-19:**

| Source | Class | What it establishes |
|---|:--:|---|
| Google SRE Workbook, *Alerting on SLOs* — https://sre.google/workbook/alerting-on-slos/ | P3 | Error budget = 1 − SLO. Burn rate = current error rate ÷ tolerable error rate. Multiwindow alerting pairs a long window with a short one (≈ 1/12 of it) so both must be true, which cuts false positives and shortens reset time |
| ISO/IEC 20000-1:2018/Amd 1:2024 — https://www.iso.org/standard/88434.html | P1 | The clause frame §8.2.1 / §8.3.3 / §8.7.2 conformed to above |

### 2.3 Audit findings this document closes or contributes to

| Finding | Source | How this document acts on it |
|---|---|---|
| **`PE-001-F-04`** — `NFR-046` and `NFR-048` state no measurement window | `PE-001` §9.1 | **Closed at the service-level layer.** §5.4 fixes a measurement window for every one of the 21 services. `PE-008` §4 still has to implement them |
| **`OP-06`** — no SLA clock before W6 | `AUDIT-017` | **Contributes.** §10.4 states what is reportable at W1 under each of the two `SV-001-D-04` outcomes, rather than assuming either |
| **`OP-03`** — `05-03`'s P0 integration count is wrong and `INT-013` has no fallback | `AUDIT-017` | **Contributes.** §8.2 enumerates **13** P0 integrations and treats email as one of them; §8.5 records that a `P0` dependency with no fallback cannot carry a service commitment |
| **`OP-14`** — the status page depends on the estate it reports on | `AUDIT-017` | **Contributes.** `PSL-18`: an availability figure published from inside the estate is not evidence during an outage of that estate |
| `M66` **Q-03** — *"are internal SLA targets agreed with the business?"* | `M66` §18 | **This document is the instrument that makes the agreement possible.** It is not agreed until the Operations Director co-signs (§13, `SV-002-D-01`) |
| `OP-001-OI-02` — response commitments unratified | `OP-001` §4.12 | **Contributes.** §7.2 carries `OP-001` §4.5's commitments into the OLA layer where they can be signed rather than asserted |

### 2.4 The rule space

This document allocates **`PSL`**, verified at **2026-08-19 01:53 (+06)** to return **zero
occurrences in identifier form** across all **763** markdown files of the workspace. The form
`SV-nn` is not used, for the reason given in `SV-001` §2.4.

---

## 3. Two Kinds of SLA, and Why Only One Exists

### 3.1 The distinction

| | **SLAs the programme sells** | **SLAs the programme keeps** |
|---|---|---|
| Instruments | `MD-028` service priority and SLA bands · `M08` contractual SLAs with service credits · `LG-003`, `LG-015` portal terms · `M05` managed-services SLAs | **None** |
| Subject | A customer's repair job, a corporate contract, a managed-services engagement | The ERP platform itself |
| Measured in | Response time to a job, turnaround, on-time completion | Availability, latency, correctness, recoverability |
| Remedy on breach | Service credits, contractual escalation | — |
| Audience | Paying customers | 500–1,000 internal staff across 51+ branches, and eleven external audiences (`OP-001` §4.1) |
| State | **Defined, priced and legally reviewed** | **Absent — this document** |

### 3.2 Why the absence is not an oversight

It is a predictable consequence of the estate's shape. The demand-side documentation is
exceptional (`PGD-000` §2.3) and it was written from the **customer's** point of view, because that
is where the revenue is. Nobody wrote the platform's own service commitment because the platform
had no users yet.

**The moment W1 goes live, the platform has 150 users and no stated commitment to any of them**, and
the first question at the first outage is *"how long is this supposed to take?"* — a question that
has no answer, and therefore gets one invented under pressure by whoever is in the room.

> **`PSL-01`. A platform with no stated service level does not have a relaxed service level. It has
> an implicit one, set by the most recent outage.**

### 3.3 What this document does and does not settle

| Settles | Does not settle |
|---|---|
| What is promised, per service, with a measurement window and an exclusion rule | Whether the promise is **funded** — the establishment is `SV-001` §8.4 and it is unfunded |
| What is measured and from where | Whether it **can** be measured — `PE-008` is absent (§11) |
| What underpins each promise internally and externally | Whether the eleven external suppliers have signed anything — `CO-003` is absent (§8.4) |
| What happens when a target is missed | Whether anyone is accountable for missing it — that is `SV-001` §5.3 and **no owner is named** |

---

## 4. The Internal Service Catalogue

### 4.1 What a catalogue entry is

> **`PSL-03`. A catalogue entry names one service, one audience, one owner, one set of hours and
> one place to go when it fails.** An entry that cannot state all five is not published; it is
> raised as a gap.

The catalogue is the **published** face of `SV-001` §5.2's register. `SV-001` decides what a service
is; this publishes what each one promises.

### 4.2 The catalogue — twenty-one services

Hours: **`BH`** = 09:00–22:00 BST, seven days (the `NFR-006` window and the `OP-001` §4.5 support
window). **`24×7`** = continuous. Route: where a fault is raised, per `OP-001` §4.3.

| Service | What it is, to the person using it | Audience | Hours | Route on failure | Owner (`SV-001` §5.3) |
|---|---|---|:--:|---|---|
| **`S-01`** ERP core | *"Creating, dispatching, closing and invoicing a job works."* | All internal, all portals | **24×7** | `Q-IT-INCIDENT` → T3 | Platform Engineering |
| **`S-02`** System of record | *"What was saved is still there and is correct."* | Everything | 24×7 | `Q-IT-INCIDENT` → T3 | Platform Engineering |
| **`S-03`** Identity | *"You can sign in, and only to what you should."* | Every population | 24×7 | `Q-IT-INCIDENT` → T3 · **`Q-SEC` if suspected compromise** | Security Engineering |
| **`S-04`** Gateway and ingress | *"Requests from outside reach the platform."* | Every external caller | 24×7 | `Q-INTEG` → T3 | Platform Engineering |
| **`S-05`** Filestore | *"Attachments, PDFs and job photographs open."* | All | 24×7 | `Q-IT-INCIDENT` → T3 | Platform Engineering |
| **`S-06`** Payment path | *"A customer can pay and the payment is recorded once."* | Consumers, branches, finance | 24×7 | `Q-FIN-APP` → T3, **page on `Sev1`** | Integration Engineering |
| **`S-07`** Customer portal `P01` | *"A customer can book, track and pay."* | 250,000+/month | 24×7 | `Q-EXT-PORTAL` | Platform Engineering |
| **`S-08`** Technician mobile `P02` | *"A technician can work a job and it syncs."* | 200–400 technicians | 24×7 | In-app *report a problem* → `Q-MOBILE` | Mobile Engineering |
| **`S-09`** Admin portal `P03` | *"Staff can do their job in the system."* | 500–1,000 staff | **BH** | `Q-IT-INCIDENT` | Platform Engineering |
| **`S-10`** Integration and events | *"The 47 integrations move data, and nothing is lost."* | All | 24×7 | `Q-INTEG` | Integration Engineering |
| **`S-11`** Notifications | *"The customer, the technician and the branch are told."* | All | 24×7 | `Q-INTEG` | Integration Engineering |
| **`S-12`** Resident data service | *"Residency-classified fields stay in Bangladesh and are readable."* | Statutory, compliance | 24×7 | `Q-SEC` **and** `Q-IT-INCIDENT` | Security Engineering |
| **`S-13`** Corporate portal `P04` | *"A corporate client can raise and track work."* | 550–2,200 | 24×7 | `Q-CORP` | Platform Engineering |
| **`S-14`** Vendor portal `P05` | *"A vendor can see POs and submit invoices."* | 200–600 | BH | `Q-VENDOR` | Platform Engineering |
| **`S-15`** Analytics and BI `P06` | *"Yesterday's numbers are there and are right."* | Management, finance | BH | `Q-DATA` | Data Engineering |
| **`S-16`** Marketplace `P07` (W7) | *"A seller can list, receive work and be paid."* | 500–2,000 sellers | 24×7 | `Q-SELLER` | Platform Engineering |
| **`S-17`** Brand portal `P08` | *"A brand partner can file and track a claim."* | 17+ | BH | `Q-BRAND` | Platform Engineering |
| **`S-18`** Logistics `P09` | *"Consignments sync with the courier."* | 3–6 couriers, warehouse | 24×7 | `Q-INTEG` | Integration Engineering |
| **`S-19`** Contact centre `P10` (W4) | *"An agent can take a call and see the customer."* | Agents, consumers | Per roster | `Q-IT-INCIDENT` | Contact Centre + Integration |
| **`S-20`** Quality `P11` (W5) | *"Quality records and audits are recorded."* | Quality function | BH | `Q-IT-INCIDENT` | Platform Engineering |
| **`S-21`** Partner `P12` (W7) | *"A partner can see attribution and payouts."* | 50–330 | BH | `Q-PARTNER` | Platform Engineering |

> **`PSL-04`. The "what it is" column is written in the user's words and is normative.** An SLI that
> measures something other than the sentence in that column is measuring the wrong thing. This is
> the ITIL 4 rule that an indicator must reflect the user's experience, and it is the reason §5.2
> measures **journeys** rather than uptime wherever a journey exists.

### 4.3 Hours, and the two-window problem

| Window | Defined by | Applies to |
|---|---|---|
| **`BH` 09:00–22:00 BST, 7 days** | `NFR-006`, `OP-001` §4.5 | The **support** commitment and the 99.9% availability target |
| **24×7** | `NFR-045` | The **platform** commitment, because managed services and the technician fleet do not stop at 22:00 |
| **Maintenance: 23:00–08:00 BST, ≤ 4 h/month, 72 h notice** | `NFR-049` | Changes that genuinely cannot be zero-downtime (`PE-001` §9.4) |

> **The nine-hour maintenance window and the thirteen-hour service window do not overlap** — 22:00
> to 23:00 and 08:00 to 09:00 are the buffers. That is deliberate and it is `PE-001` `MW-01`'s
> reason for calling the window *"a scarce resource"*.

### 4.4 What "available" means — the definition the numbers rest on

> **`PSL-05`. A service is available when a synthetic transaction exercising the sentence in §4.2's
> "what it is" column completes successfully within its latency objective.** Not when the process
> is running. Not when the health endpoint returns 200.

| Measured how | Not measured how |
|---|---|
| A synthetic probe performing a real, idempotent journey (sign in → load → read → write to a probe record) | Ping, TCP connect, or `GET /web/health` |
| From **outside** the estate, over the public path, from at least two vantage points | From inside the cluster |
| Every **60 seconds**, with a failure requiring **two consecutive** failed probes to count | A single failed probe |
| Availability = successful probe-minutes ÷ eligible probe-minutes | Uptime of a host |

> **`PSL-06`. Availability is measured from outside the estate.** `AUDIT-017` `OP-14` records that
> the status page has no independent hosting; the same objection applies with more force to the
> measurement itself. **A platform that measures its own availability from inside itself reports
> 100% during a total ingress failure.** This is a `PE-008` requirement and is raised there.

---

## 5. Service Level Objectives

### 5.1 Method

Three kinds of number appear below, and they are labelled, following `PE-006` §3.1's discipline:

| Label | Meaning |
|---|---|
| **Inherited** | Stated in `05-06` and adopted unchanged |
| **Derived** | Calculated here from an inherited number, with the calculation shown |
| **Proposed** | Set by this document because no upstream number exists. **Requires ratification** (`SV-002-D-01`) |

### 5.2 Service level indicators — what is actually measured

| SLI | Definition | Source system | Applies to |
|---|---|---|---|
| **`SLI-AVAIL`** | Successful synthetic journey probes ÷ eligible probes, per §4.4 | Synthetic monitoring, **outside the estate** | All 21 |
| **`SLI-LAT-UI`** | p95 wall-clock time for the service's primary screen | Real-user monitoring + synthetic | `S-01`, `S-07`, `S-08`, `S-09`, `S-13`…`S-21` |
| **`SLI-LAT-API`** | p95 gateway-observed response time, excluding client network | Kong metrics | `S-04`, `S-06`, `S-10`, `S-18` |
| **`SLI-CORRECT`** | Transactions completing without a data-integrity error (failed posting, orphaned record, reconciliation divergence) ÷ all | Nightly reconciliation (`DI-07`) | `S-01`, `S-02`, `S-06`, `S-15` |
| **`SLI-FRESH`** | Age of the newest record in the warehouse at 08:00 BST | Pipeline metadata | `S-15` |
| **`SLI-DELIVER`** | Events delivered to their consumer within 5 s ÷ all events (`NFR-043`, which is a **p95** — so the objective is **95%**, not 99.5%; corrected §0, per `PE-008` `SLO-05`) | Event platform metrics | `S-10`, `S-11` |
| **`SLI-SYNC`** | Technician devices whose queued work synced within 30 s of connectivity ÷ all reconnections (`NFR-037`) | Mobile telemetry | `S-08` |
| **`SLI-RPO`** | Replication lag, and WAL archive success | `pg_stat_replication`, `pg_stat_archiver` | `S-02`, `S-12` |
| **`SLI-RESTORE`** | Weekly automated restore test result (`NFR-052`) | Restore test job | `S-02`, `S-05`, `S-12` |

> **`PSL-07`. Every SLI in this table is a `PE-008` obligation.** Not one of them can be produced by
> the platform as designed today, because `PE-008` does not exist. §11 is the dependency statement;
> this rule exists so that no service report is published from a hand-assembled figure.

### 5.3 The objectives

**`P0` services**

| Service | Availability SLO | Window | Latency SLO | Other | Basis |
|---|:--:|:--:|---|---|---|
| `S-01` ERP core | **99.9%** | `BH` · **and 99.7% 24×7** | ≤ 2 s p95 screens (`NFR-001`) | `SLI-CORRECT` ≥ 99.99% | Inherited `NFR-006`, `NFR-045`, `NFR-001` |
| `S-02` System of record | **99.95%** | 24×7 | — | **`SLI-RPO` < 15 min always** (`NFR-007`); `SLI-RESTORE` = pass, weekly (`NFR-052`) | **Derived** — §5.5: `S-01`'s 99.9% is impossible on a 99.9% database |
| `S-03` Identity | **99.95%** | 24×7 | ≤ 1.5 s p95 sign-in | — | **Derived** — §5.5; `PE-001` §9.2 calls it *"a total-outage dependency"* |
| `S-04` Gateway and ingress | **99.95%** | 24×7 | ≤ 400 ms p95 API (`NFR-002`) | — | **Derived** — §5.5 |
| `S-05` Filestore | **99.9%** | 24×7 | ≤ 3 s p95 object fetch | Point-in-time consistency with `S-02` | **Proposed** |
| `S-06` Payment path | **99.95% platform-side** · **best-effort end-to-end** | 24×7 | ≤ 3 s p95 round trip (`NFR-042`) | Zero double-charges; `SLI-CORRECT` = 100% on money | Inherited `NFR-048`, **split** per §5.7 |
| `S-07` Customer portal | **99.9%** | **24×7** *(window fixed here — `PE-001-F-04`)* | ≤ 2 s p95 (`NFR-031`) | — | Inherited `NFR-046`; window **Derived** |
| `S-08` Technician mobile | **99.7%** service-side | 24×7 | ≤ 8 s cold / ≤ 2 s warm on 3G (`NFR-036`) | `SLI-SYNC` ≥ 99%; **24 h offline tolerance** (`NFR-047`) | Inherited `NFR-045`, `NFR-036`, `NFR-037` |
| `S-09` Admin portal | **99.9%** | `BH` | ≤ 2 s p95 | — | Inherited `NFR-006` |
| `S-10` Integration and events | **99.7%** | 24×7 | ≤ 400 ms p95 API | **`SLI-DELIVER` ≥ 95% at 5 s** (`NFR-043` p95; corrected §0); **zero dead-letter items older than 24 h** | Inherited `NFR-045`, `NFR-043` |
| `S-12` Resident data service | **Deferred to `SC-007` §9.5** *(corrected §0)* | 24×7 | ≤ 500 ms p95 | `SLI-RPO` < 15 min; **zero cross-border transfers** (`NFR-086b`) | **`PE-008` `SLO-08` / `Z4-02`: reported separately, never folded into an estate SLO.** This document proposes no number for `BD-R` |

**`P1` and `P2` services**

| Service | Availability SLO | Window | Latency SLO | Basis |
|---|:--:|:--:|---|---|
| `S-11` Notifications | 99.5% | 24×7 | Queued ≤ 60 s; delivered per channel SLA | **Proposed** |
| `S-13` Corporate portal | 99.9% | 24×7 | ≤ 2 s p95 | **Proposed** — contractual clients |
| `S-14` Vendor portal | 99.5% | `BH` | ≤ 3 s p95 | **Proposed** |
| `S-15` Analytics and BI | 99.0% | `BH` | ≤ 10 s p95 (`NFR-039`); dashboard ≤ 5 s (`NFR-038`) | Inherited `NFR-039`; availability **Proposed** · `SLI-FRESH` **≤ 8 h at 08:00** |
| `S-16` Marketplace (W7) | 99.5% | 24×7 | ≤ 2 s p95 | **Proposed** |
| `S-17` Brand portal | 99.0% | `BH` | ≤ 3 s p95 | **Proposed** |
| `S-18` Logistics | 99.5% | 24×7 | ≤ 400 ms p95 | **Proposed** |
| `S-19` Contact centre (W4) | 99.9% | Per roster | ≤ 2 s p95 customer lookup | **Proposed** — an agent with a slow screen is a queue |
| `S-20` Quality (W5) | 99.0% | `BH` | ≤ 3 s p95 | **Proposed** |
| `S-21` Partner (W7) | 99.0% | `BH` | ≤ 3 s p95 | **Proposed** |

> **Eleven of twenty-one objectives are `Proposed` and one (`S-12`) is deferred to `SC-007` §9.5** — counted by extraction from the table above at v1.1, correcting the first draft's "fourteen". `05-06` states
> four availability numbers for a platform with twenty-one separately-failing services. Proposing
> the other seventeen is the work; **ratifying them is `SV-002-D-01` and it belongs to the
> Operations Director, not to engineering** — `M66` Q-03's point exactly.

### 5.4 The measurement window, fixed

`PE-001-F-04` records that `NFR-046` and `NFR-048` state no window, and that the difference between
a business-hours and a 24×7 window is a factor of roughly **1.85** in permitted downtime. §5.3 fixes
a window for every service. The rule that produced them:

> **`PSL-08`. A service's measurement window is the window in which its audience uses it.** The
> customer portal and the technician app are used at 23:00 and at 06:00; they are measured 24×7. The
> vendor and quality portals are not; they are measured over business hours. **A window chosen for
> arithmetic convenience rather than for the audience is how a 99.9% report coexists with an
> unusable service.**

Confirming the 1.85 factor at 99.9%: business-hours month = 13 h × 30.44 d = **395.7 h**, of which
0.1% = **23.7 min**. A 24×7 month = **730.5 h**, of which 0.1% = **43.8 min**. 43.8 ÷ 23.7 = **1.85**. ✓

### 5.5 The composite-availability derivation — why components must beat the service

This is the calculation that turns four NFR sentences into a design constraint, and it is the reason
`S-02`, `S-03` and `S-04` carry a **higher** objective than the services that depend on them.

A user journey on `S-07` (customer portal) traverses, in series:

`S-04` ingress → `S-03` identity → `S-01` ERP core → `S-02` database

Serial dependencies multiply. For the composite to reach 99.9%, each of four independent components
must achieve:

> 0.999 ^ (1/4) = **0.99975 → 99.975%**

| Composite target | Serial components | Required per component | Monthly budget per component (24×7) |
|:--:|:--:|:--:|:--:|
| 99.9% | 2 | 99.95% | 21.9 min |
| **99.9%** | **4** | **99.975%** | **10.9 min** |
| 99.9% | 5 | 99.98% | 8.8 min |
| **99.95%** (payment) | **5** *(+ `S-06`)* | **99.99%** | **4.4 min** |

| # | Consequence |
|---|---|
| **`PSL-09`** | **No `P0` component may carry the same availability objective as the service that depends on it.** §5.3 sets `S-02`, `S-03` and `S-04` at 99.95% for exactly this reason, and even that is a rounding of 99.975% to a number a supplier can be held to |
| **`PSL-10`** | This is the arithmetic behind `PE-001` `HA-01` — *"no single-node critical component is acceptable in production"*. **A single-node PostgreSQL cannot deliver 10.9 minutes a month**; one planned restart consumes the whole budget |
| **`PSL-11`** | **A 99.95% end-to-end payment path over five serial dependencies requires 99.99% from each — 4.4 minutes a month, per component.** §5.7 is what follows from that being impossible |

### 5.6 The maintenance-window contradiction, resolved

**The arithmetic nobody had done.**

| Statement | Source | Monthly figure |
|---|---|---|
| `NFR-045` — 24×7 availability ≥ **99.7%** | `05-06` §2 | Permits **131.5 min** of unavailability (730.5 h × 0.3%) |
| `NFR-049` — planned maintenance **≤ 4 h per month**, outside 08:00–23:00, 72 h notice | `05-06` §2 | Consumes up to **240 min** |
| Difference | | **−108.5 min** |

> **`SMF-F`-class finding, raised here as `PSL-F-01`: if planned maintenance counts toward
> availability, `NFR-045` is breached by planned maintenance alone, in a month with no incident at
> all.** 240 minutes of permitted maintenance against a 131.5-minute budget is not a tight fit; it
> is a 1.8× overrun before anything goes wrong.

Three possible resolutions, and the ruling:

| Option | Assessment |
|---|---|
| (a) Reduce `NFR-049`'s maintenance allowance below 131.5 min/month | **Rejected.** `PE-001` §9.4 already calls the window *a scarce resource*, and the changes it exists for — a major PostgreSQL version upgrade, a network re-address — do not fit in two hours |
| (b) Raise `NFR-045` to accommodate maintenance | **Rejected.** It weakens a commitment to solve a definitional problem, and `NFR-045` exists because *"managed services requires it"* |
| **(c) Exclude announced planned maintenance from the availability measurement, and state the exclusion wherever the number is published** | **Chosen — `SV-002-D-02`** |

> **`PSL-12`. Planned maintenance is excluded from `SLI-AVAIL` if and only if all four hold:** it
> falls inside 23:00–08:00 BST; it was announced **≥ 72 h** ahead through `OP-005`; it is inside the
> 4 h monthly allowance; and it is recorded against an approved change (`SP-031` §5.3). **Fail any
> one and the whole window counts as unavailability.** A maintenance window that overruns is not
> maintenance after its stated end — it is an incident, and `SV-006` §4.1 declares it as one.
>
> **`PSL-13`. Every published availability figure states the exclusion in the same sentence.**
> *"99.74% (excludes 3 h 10 m announced maintenance)"* — never *"99.74%"* alone. An exclusion that
> is true and unstated is the most defensible way to mislead a business owner, and it is what turns
> a service report into something nobody believes at the third reading.

**`NFR-008` is what keeps the exclusion honest.** Zero-downtime deployment is the standard for
releases (`RL-001`, `PE-004` §8); the `NFR-049` window exists only for changes that cannot be done
live. `PE-001` `MW-01` already rules that *"using the `NFR-049` window for an ordinary release is a
defect, not a convenience"*, and `PSL-12` gives that rule a measurable consequence: every hour taken
in the window is an hour of excluded downtime that a user experienced anyway.

### 5.7 `NFR-048` — the payment path, split

`05-06` sets the payment path at **≥ 99.95% with multi-gateway failover**. `IN-007` §9.3 records
that for the **card** path this is unachievable at any infrastructure quality, because `INT-003` is
the only card acquirer. §5.5 `PSL-11` shows why: five serial dependencies at 99.95% composite
require 99.99% each — **4.4 minutes a month** — from a third party the Company does not operate.

> **`SV-002-D-03`. `NFR-048` is split into two objectives that are separately measurable and
> separately owned.**

| Objective | Target | Scope | Owner | Achievable? |
|---|:--:|---|---|:--:|
| **`S-06`-P — platform-side payment path** | **99.95%** 24×7 | Everything the Company operates: the payment service, the gateway abstraction, the failover logic, the reconciliation | Integration Engineering | **Yes**, with `PE-001` `HA-01` |
| **`S-06`-E — end-to-end payment success** | **Reported, not committed** | Includes the acquirer, the MFS providers and the customer's bank | — | **No** — single card acquirer |
| **`S-06`-F — failover effectiveness** | **≥ 99.5%** of card failures fail over to an MFS route within 30 s | The Company's own mitigation of the exposure | Integration Engineering | Yes |

> **`PSL-14`. Where a commitment depends on a supplier the Company cannot hold to it, the commitment
> is split into the part the Company controls and the part it reports.** Publishing a single
> end-to-end number the Company cannot influence is a commitment to something it cannot do, and the
> first time it is missed the whole SLA loses credibility, not just that line.

### 5.8 Reconciliation with `PE-008`'s eight SLOs

**Two SLO sets are now current.** `PE-008` §7.2 defines eight; §5.3 above defines twenty-one. They
are not competing — they are at **different altitudes** — but that has to be stated, or two teams
will report two different availability figures for the same month.

#### 5.8.1 The mapping

| `PE-008` SLO | Scope | Objective | Corresponds to | Relationship |
|---|---|:--:|---|---|
| **`SLO-01`** | System, business hours | 99.9% | `S-01` (`BH`) | **Identical.** `PE-008` measures the estate as one system; §5.3 attributes it to `S-01` |
| **`SLO-02`** | System, 24×7 | 99.7% | `S-01` (24×7), `S-08`, `S-10` | Identical objective, **decomposed** across three services |
| **`SLO-03`** | Customer portal, 24×7 *(window ruled)* | 99.9% | **`S-07`** | **Identical, including the window.** Both documents ruled 24×7 independently |
| **`SLO-04`** | Payment path, 24×7 *(window ruled)* | 99.95% | **`S-06`-P / -E / -F** | `PE-008` §7.3 excludes counterparty failures and shows them separately; §5.7 splits the same exposure into three named objectives. **Compatible; §5.7 is finer** |
| **`SLO-05`** | Event delivery within 5 s | 95% | `S-10` `SLI-DELIVER` | **`PE-008` is correct and this document's first draft was wrong** — §0 |
| **`SLO-06`** | ERP screen latency ≤ 2 s | 95% | `S-01`, `S-09` latency | Identical; `p95 ≤ 2 s` and `95% ≤ 2 s` are the same statement |
| **`SLO-07`** | API latency ≤ 400 ms | 95% | `S-04`, `S-06`, `S-10`, `S-18` latency | Identical |
| **`SLO-08`** | `Z4` availability | Per `SC-007` §9.5 | **`S-12`** | **`PE-008` governs.** §5.3 now defers rather than proposing |
| — | — | — | **The other thirteen services** | **No `PE-008` equivalent.** `PE-008` measures the estate; §5.3 measures what each audience depends on |

> **`SV-002-D-06`. `PE-008` §7.2's eight SLOs are the *measurement* SLOs. §5.3's twenty-one are the
> *commitment* SLOs. Where they overlap, `PE-008`'s definition of the indicator governs and this
> document's audience, window and route govern.**

| Layer | Owns | Why |
|---|---|---|
| **`PE-008`** | The SLI — what a good event is, what a valid event is (`VE-01`…`VE-05`), how it is collected, the burn-rate thresholds | Measurement is an observability design problem |
| **`SV-002`** | Which service, which audience, which hours, which route on failure, who signs it, what happens when it is missed | Commitment is a service management problem |

**Why twenty-one and not eight.** `PE-008` `SLO-01`/`SLO-02` measure *"the system"*. That is the
right unit for an error budget and the wrong unit for a promise: the vendor portal and the payment
path are both *"the system"*, and telling a vendor that the estate was 99.7% available in a month
when their portal was down for six hours is a true statement nobody will accept twice. **`SMF-04`'s
test — a named population, separately unavailable, one owner — is what produces twenty-one**, and it
is the same test that found the two missing runbooks in `SV-003` §5.3.

#### 5.8.2 The synthetic-monitoring conflict, resolved

`PE-008` `VE-04`: *"Synthetic monitoring requests are **excluded** from SLIs and reported
separately."* §4.4's `PSL-05` and `PSL-06` as first drafted made availability **a synthetic-probe
measure**. Both cannot be true.

| Approach | Strength | Failure mode |
|---|---|---|
| **Real-request ratio** (`PE-008`) | Measures what users actually experienced. Cannot be gamed by probe design | **At 03:00 with no traffic, a total outage produces zero requests, zero failures and a green SLO** |
| **Synthetic probe** (first draft) | Detects an outage with no traffic; exercises the **external** path, which is where `AUDIT-017` `OP-14`'s status-page problem lives | Measures a probe's experience, not a user's. A probe hitting a warm path can pass while real journeys fail |

> **`SV-002-D-07`. Both, with a stated precedence. The SLO of record is the real-request ratio
> (`PE-008`). Synthetic probes are the availability floor and the outside-in check, and they
> **override** the ratio in one specific case.**

| # | Rule *(revised)* |
|---|---|
| **`PSL-05`** *(revised)* | **A service is available when the real-request success ratio holds *and* the synthetic journey completes.** The SLO is computed from real requests per `PE-008` `VE-01`…`VE-05` |
| **`PSL-06`** *(revised)* | **Where real request volume in a measurement interval falls below the minimum-volume threshold, the synthetic probe result is authoritative for that interval.** A quiet hour is not an available hour by default — **that is the exact interval in which an unnoticed outage becomes a morning surprise** |
| **`PSL-06a`** *(new)* | **Synthetic probes run from outside the estate, from ≥ 2 vantage points**, and are reported as a separate series (`VE-04`). They are never added into the SLI numerator |
| **`PSL-06b`** *(new)* | **The minimum-volume threshold is set per service by the service owner and published**, because an unpublished threshold is a silent exclusion |

**Why `PSL-06` matters more than it looks.** `S-07` (customer portal) and `S-08` (technician mobile)
carry **24×7** windows precisely because they are used at 03:00 — but *thinly*. Those are the hours
in which a request-ratio SLI has the least data and the most opportunity to report success by
measuring nothing, and they are the hours with no service desk and, today, no page.

---

## 6. Error Budgets

### 6.1 The arithmetic

Error budget = 1 − SLO, expressed in time over the measurement window.

| SLO | Window | Budget / week | **Budget / month** | Budget / year |
|:--:|:--:|:--:|:--:|:--:|
| 99.0% | `BH` (91 h/wk · 395.7 h/mo) | 54.6 min | **3 h 58 m** | 47 h 29 m |
| 99.5% | `BH` | 27.3 min | **1 h 59 m** | 23 h 44 m |
| **99.9%** | **`BH`** | **5.5 min** | **23.7 min** | **4 h 45 m** |
| 99.0% | 24×7 (168 h/wk · 730.5 h/mo) | 1 h 41 m | 7 h 18 m | 87 h 39 m |
| 99.5% | 24×7 | 50.4 min | 3 h 39 m | 43 h 50 m |
| **99.7%** | **24×7** | **30.2 min** | **2 h 11 m** | **26 h 18 m** |
| **99.9%** | **24×7** | **10.1 min** | **43.8 min** | **8 h 46 m** |
| **99.95%** | **24×7** | **5.0 min** | **21.9 min** | **4 h 23 m** |
| 99.975% | 24×7 | 2.5 min | 11.0 min | 2 h 11 m |
| 99.99% | 24×7 | 1.0 min | 4.4 min | 52.6 min |

*(Month = 730.5 h, the mean calendar month; business-hours month = 13 h × 30.44 d = 395.7 h.)*

### 6.2 What a budget is for

| It is | It is not |
|---|---|
| A quantity of unreliability the business has agreed is acceptable | A target to be consumed |
| A shared unit of conversation between engineering and operations | A performance measure for an individual |
| An input to **prioritisation** — a service that burns its budget gets reliability work next sprint | A gate on releases (`SV-001-D-05`) |
| Evidence in the monthly report (§10.2) | A reason to hide an incident |

> **`PSL-15`. A service that ends a quarter with its budget untouched is over-engineered or its SLO
> is too loose, and the Service Management Board reviews it in the same agenda item as a service
> that exhausted its budget.** Both are miscalibrations; only one of them looks like one.

### 6.3 The `S-01` worked example

`S-01` carries **99.9% `BH`** and **99.7% 24×7** simultaneously (§5.3), which is not redundant —
they bind in different windows and the tighter one changes by time of day.

| Scenario | `BH` budget consumed | 24×7 budget consumed | Position |
|---|:--:|:--:|---|
| 20-minute outage at 14:00 on a Tuesday | 20 of **23.7 min** — **84%** | 20 of 131.5 min — 15% | **Business-hours budget nearly gone in one event.** One more such outage that month is a breach |
| 20-minute outage at 03:00 on a Sunday | **0** — outside the window | 20 of 131.5 min — 15% | Absorbed comfortably |
| 3 h announced maintenance at 01:00, inside allowance | 0 | **0** — excluded (`PSL-12`) | No consumption, **and the exclusion is printed** (`PSL-13`) |
| 3 h maintenance that overruns to 04:30 | 0 | **90 min counted** — 68% of the month | The 90-minute overrun is an incident (`SV-006` §4.1), not maintenance |

> **This is why `PSL-08` matters.** The same twenty-minute failure is a near-breach or a rounding
> error depending on the hour, and that is correct: it is exactly how the business experiences it.

### 6.4 Burn-rate alerting policy

**`PE-008` §8.2 is the authority for these thresholds** *(corrected §0 — this table was drafted
independently and arrived at the same three tiers, the same windows and the same budget
percentages)*. It is restated here only because the routing column is Category 11's, and it is
restated **unchanged**: a long window paired with a short window (≈ 1/12 of it), **both** of which
must exceed the threshold before an alert fires (`PE-008` `AL-01`).

| Tier | Budget consumed | Long window | Short window | Burn rate | Action | Routed to |
|:--:|:--:|:--:|:--:|:--:|---|---|
| **Fast** | **2% in 1 h** | 1 h | 5 min | **14.4×** | **Page** | `SV-004` — on-call primary, `Sev1`/`Sev2` by service criticality |
| **Medium** | **5% in 6 h** | 6 h | 30 min | 6× | **Page in hours; ticket out of hours** | `SV-004` |
| **Slow** | **10% in 3 days** | 72 h | 6 h | 1× | **Ticket + service owner** | `Q-IT-INCIDENT`, and the next Board agenda |

| # | Rule |
|---|---|
| **`PSL-16`** | **A burn-rate page is a `Sev2` by default, and a `Sev1` only for a `P0` service in its measurement window.** Burn rate measures *rate*, and a fast burn on `S-17` at 02:00 is not a `Sev1` |
| **`PSL-17`** | Every burn-rate alert names the service, the SLO, the budget consumed **and the budget remaining**. *"Error rate elevated"* is not actionable at 02:00; *"`S-01` has consumed 41% of its monthly budget in the last hour, 59% remains"* is |
| **`PSL-18`** | **The availability figure a burn-rate alert cites is the one measured from outside the estate** (`PSL-06`). During a total ingress failure, an internally-measured figure reports success and the alert never fires |
| **`PSL-19`** | Burn-rate alerts are **suppressed during an excluded maintenance window** and un-suppressed automatically at its stated end — never manually, and never open-ended (`OP-013` `HO-03`) |

---

## 7. Operational Level Agreements

### 7.1 What an OLA is here

An SLA is a promise to a user. An **OLA** is the internal commitment that makes it possible. If the
SLA says `S-01` restores in two hours and no internal function has committed to answering a page in
five minutes, the SLA is decoration.

> **`PSL-20`. Every SLO in §5.3 traces to at least one OLA row in §7.2. An SLO with no underpinning
> OLA is withdrawn, not published.**

### 7.2 The five internal OLAs

| Function | Commits to | Hours | Underpins | Signed? |
|---|---|:--:|---|:--:|
| **Platform Engineering** | Acknowledge a `Sev1` page in **5 min** · IC assigned at declaration · restore a `P0` service ≤ **2 h** (`NFR-007` RTO) · execute the runbook (`SV-003`) · maintain the 21-row dependency register (`SMF-18`) | **24×7 via rota** | `S-01`, `S-02`, `S-04`, `S-05`, `S-07`, `S-09`, `S-13`, `S-14`, `S-16`, `S-17`, `S-20`, `S-21` | ✗ **rota unstaffed** |
| **Security Engineering** | Acknowledge a suspected compromise in **15 min** · classify within 1 h · hand to `SC-011` · restore identity ≤ 2 h · operate break-glass | 24×7 via rota | `S-03`, `S-12` | ✗ **rota unstaffed** |
| **Integration Engineering** | Acknowledge `Sev1` in 5 min · dead-letter queue drained daily · **zero items older than 24 h** · fallback invoked within 30 min of a `P0` integration failure (`NFR-050`) | 24×7 for `S-06`, `S-10`; `BH` otherwise | `S-06`, `S-10`, `S-11`, `S-18`, `S-19` | ✗ |
| **Data Engineering** | Warehouse loaded and reconciled by **08:00 BST** · `SLI-FRESH` ≤ 8 h · data-quality failures block dependent refreshes (`DI-06`) · extended cover during month-end close | `BH`, extended at close | `S-15` | ✗ |
| **Contact Centre** (`P10`, from W4) | Answer per roster · reclassify a platform fault to `Q-EXT-PORTAL` within the same contact (`OP-001` §4.3) | Per roster | `S-19`, and the consumer route into every service | ✗ |

**Support-side commitments** — acknowledgement, first update, update cadence and restoration targets
per `Sev1`–`Sev4`, and the request-class targets — are `OP-001` §4.5's and are **adopted by
citation** (`PSL-02`). They are not restated. What this document adds is that they now sit inside a
signed OLA rather than being a support team's stated intention, which is what `OP-001-OI-02` asked
for.

### 7.3 The OLA that does not exist

> **`PSL-F-02`. All five OLAs are unsigned, because four of the five functions have no identified
> members** (`SV-001` §5.4, `AUDIT-017` `OP-09`). An OLA signed by a function with zero people is
> not an agreement; it is a note about an intention.
>
> This is not a reason to omit them. It is the reason to publish them: **an unsigned OLA is a
> visible gap, and an absent one is an invisible assumption.**

---

## 8. Underpinning Contracts

### 8.1 Why this section is short and consequential

Every `P0` integration is a dependency of a service commitment, and the Company's ability to keep
that commitment ends at the boundary of a third party's own SLA. `T4` in `OP-001` §4.2 names the
tier; this names the exposure.

### 8.2 The dependency set

`AUDIT-017` `OP-03` established by re-enumeration that `05-03` §2's priority summary is wrong:
**13 P0 integrations, not 12**, and the `05-03` §7 fallback register **has no entry for `INT-013`
(email)** while counting three non-`P0` fallbacks toward `P0` coverage.

> **`PSL-21`. This document treats the enumerated 13 as the P0 set**, following `OP-014` §4.4 and
> `OP-008` §7, and **not** `05-03` §2's summary. Where a specification and an enumeration disagree,
> the enumeration is the fact and the specification is the finding (`RG-06`).

| Class | Dependency | Underpins | Fallback exists? | Exposure |
|---|---|---|:--:|---|
| Payments | **`INT-003` card acquirer** — the only one | `S-06` | Multi-gateway failover to MFS | **Single supplier. `NFR-048` end-to-end unachievable** (`IN-007` §9.3) |
| Payments | bKash / Nagad MFS | `S-06` | Alternate MFS + cash | Concentration, lower than card |
| Messaging | **`INT-013` email** | `S-11`, ticket intake, invoice delivery | **✗ — no `05-03` §7 entry** (`OP-03`) | **A `P0` dependency with no registered fallback** |
| Messaging | SMS primary gateway | `S-11`, OTP, `OP-013` §4.10 tier 2 | `INT-011` failover gateway | Adequate — **and the out-of-band channel depends on it** |
| Messaging | WhatsApp `INT-012` | Consumer contact | Voice + SMS | Vendor policy risk |
| Telephony | `INT-015` (W4) | `S-19`, hotline 16743 | Manual logging | Adequate |
| Logistics | `INT-024`…`INT-026` couriers | `S-18` | Manual booking | Adequate |
| Identity/KYC | KYC and e-signature vendors | Onboarding journeys | Manual verification | Latency, not availability |
| Infrastructure | **Cloud provider, `RGN-P` / `RGN-S`** | Every service | **None** | **The floor under every SLO in §5.3** |
| Infrastructure | **`BD-R` colocation** | `S-12`, and residency compliance | **None** | Single facility; **climate-exposed** (`SV-001` §4.4) |
| AI | `INT-043` LLM inference | Assistant features (W6) | Degrade to non-AI | Low — feature-flagged |

### 8.3 The floor nobody has stated

> **`PSL-F-03`. No SLO in §5.3 can exceed the availability of the cloud provider and the `BD-R`
> facility beneath it, and neither figure appears anywhere in the estate.** `02-05` §8 sizes
> hardware; no document records what the hosting provider commits to, whether it is a single
> availability zone or several, or what its own maintenance regime is.
>
> A 99.95% objective on `S-02` is a statement about the Company's engineering **and** an assumption
> about a supplier that has never been written down. `CO-004` (licence and component register)
> is `◐` and **`CO-003` (Statement of Work) was issued during this category's authoring**; this
> belongs in both, and `CO-003` now exists to carry it.

### 8.4 The eight clauses every underpinning contract must carry

Handed to `CO-003` and `CO-004`, because a service commitment that is not flowed down to the
supplier is a commitment the Company absorbs alone.

| # | Clause | Why |
|---:|---|---|
| 1 | A stated availability target **with its measurement window** | `PE-001-F-04`'s defect, arriving from the supplier side |
| 2 | A stated **RTO** for the supplier's own restoration | `NFR-007`'s 2 h is meaningless if a `P0` supplier's is 24 h |
| 3 | An **incident notification obligation**, with a maximum notification delay | The Company cannot communicate (`OP-004`) what it has not been told |
| 4 | A **named technical escalation contact**, 24×7, verified quarterly | `OP-013` `OB-02` applies to suppliers too |
| 5 | **Planned maintenance notice ≥ 72 h**, aligned to `NFR-049`'s window | A supplier's maintenance inside the Company's service hours is the Company's outage |
| 6 | A **security incident and breach notification** obligation | `NFR-094`'s statutory clock runs from **detection**, including a supplier's |
| 7 | **Data residency and sub-processor disclosure** | `NFR-086`/`NFR-086b`; a sub-processor change can move residency-classified data |
| 8 | **Exit and data-return terms** | See §8.5 |

### 8.5 The supplier-continuity clause, and why it is not theoretical

> **`PSL-22`. Every underpinning contract states what happens to the Company's data and
> configuration when the product is withdrawn, not only when the contract is terminated.**

The programme has a live example in an adjacent domain, verified 2026-08-19: **Atlassian Opsgenie —
a widely-deployed on-call and alerting product — ended sale on 2025-06-04 and shuts down completely
on 2027-04-05, with all non-migrated data deleted thereafter.** That date falls **inside** this
programme's 36-month horizon. A tool procured in Wave 1 on a three-year assumption would have needed
replacing before Wave 8.

**Clause 8 is what turns that from an emergency into a migration.** `SV-004` §4 applies the same
test to the paging decision itself.

---

## 9. Breach Handling

### 9.1 What happens when a target is missed

| Miss | Trigger | Action | Owner | Deadline |
|---|---|---|---|:--:|
| **Single incident consuming > 25% of a monthly budget** | Automatic, on incident closure | Named in the next service report with its `OP-016` review reference | Service owner | Next report |
| **Monthly SLO missed** | Month-end calculation | **Written explanation** to the Service Management Board: what, why, what changes, by when | Service owner | Board + 5 working days |
| **Same SLO missed two consecutive months** | Automatic | **A problem record** (`SV-006` §5), not a second explanation | Head of ITSM | Immediately |
| **Same SLO missed three months in twelve** | Automatic | The **SLO itself is reviewed**: either the target is wrong or the service is under-invested, and the Board decides which | Board | Quarterly review |
| **An OLA missed while its SLA held** | Service owner observation | Recorded anyway — it is a near miss (`OP-016` `RV-02`) | Head of ITSM | Next Board |
| **A `P0` supplier misses its underpinning contract** | Integration Engineering | Contract escalation under `CO-003`; the exposure is re-rated in `GV-005` | Procurement + CTO | 10 working days |

### 9.2 Why there are no internal service credits

> **`SV-002-D-04`. No service credit, penalty or chargeback applies to an internal SLA breach.**

| Considered | Assessment |
|---|---|
| Financial credit between internal cost centres | **Rejected.** It converts a reliability conversation into an accounting one, and the accounting one is always won by whoever writes the definition of "outage" |
| Formal escalation to the Steering Committee on repeat breach | **Adopted** — §9.1 row 4 |
| Publication of every miss in the service report, unedited | **Adopted** — `PSL-23` |

> **`PSL-23`. Every missed target appears in the service report in the month it was missed, with no
> netting, no annualisation and no "excluding the migration weekend".** The single most reliable way
> to destroy an internal SLA is to allow the reporting to become negotiable, and the second most
> reliable is to attach money to it.

### 9.3 The SLA pause — the one mechanism that crosses into `MD-028`

`OP-001` §4.6 defines the **only** sanctioned relationship between a platform incident and a
customer's service SLA, and it is a bulk pause of affected job clocks on the Operations Director's
decision, evidenced by the incident record.

> **`PSL-24`. A pause with no incident record behind it is an unevidenced SLA adjustment**, will be
> found by `M23` audit, and is a control failure rather than an administrative correction. This
> document adds nothing to `OP-001` §4.6 and restates nothing from it — it exists in this list only
> so that a reader of the platform SLA knows where the customer-side mechanism lives.

---

## 10. Reporting and Review

### 10.1 Cadence

| Report | To | Frequency | Length |
|---|---|:--:|:--:|
| Service level report | Service Management Board (`SV-001` §8.2) | **Monthly** | Two pages |
| Quarterly summary | ERP Steering Committee | Quarterly | One page |
| Real-time position | Service owners, on-call | Continuous | Dashboard (`PE-008`) |
| SLO calibration review | Board | **Quarterly** | Per `PSL-15` |
| Full SLA review with the business | Operations Director + Board | **Annually**, and after every wave go-live | — |

### 10.2 What the monthly report contains

1. **Per `P0` service:** SLO, attained, budget consumed, budget remaining — **with the maintenance
   exclusion stated in the same line** (`PSL-13`).
2. **Every miss**, with its explanation (§9.1).
3. `Sev1`/`Sev2` count, time to acknowledge, time to restore.
4. **OLA attainment**, including the OLAs that are unsigned (§7.3).
5. Underpinning-contract incidents attributable to a supplier.
6. **The unfunded list**, reprinted in full (`SMF-25`).
7. One page maximum of narrative.

### 10.3 The evidence rule

> **`PSL-25`. Every number in the service report traces to a query a third party could re-run.** The
> report names the SLI, the window, the source system and the exclusion applied. A figure that
> cannot be reproduced is withdrawn from the report rather than footnoted — this is `RG-06`
> (*count, do not consult*) applied to operational reporting.

### 10.4 What is reportable at W1 — both cases

Because `SV-001-D-04` is undecided, the honest answer is conditional:

| | **If `CD-163` moves to W1** | **If `M66` stays whole at W6** |
|---|---|---|
| Ticket-derived measures (FCR, escalation accuracy, reopen rate) | ✅ From `CD-163` | ◐ From raw OCA `helpdesk`, by hand |
| **SLA attainment with holiday-calendar awareness** | ✅ **From W1** — `M30` holds the Bangladesh holiday set (`SMF-10`) | ⛔ **Not reportable until W6** (`OP-001` §4.9) |
| `SLI-AVAIL`, `SLI-LAT-*` | ⛔ **Blocked on `PE-008` either way** | ⛔ Same |
| `SLI-RPO`, `SLI-RESTORE` | ◐ Available by direct query; **`NFR-052`'s weekly restore test needs an environment** | ◐ Same |
| Error budgets | ⛔ Cannot be computed without `SLI-AVAIL` | ⛔ Same |

> **`PSL-F-04`. The `M66` decision changes the ticket half of the report and changes nothing about
> the availability half.** Availability reporting is blocked on `PE-008` in both branches, and
> `PE-008` is `⛔` `P0`/W1 in the register. **The service level report cannot be produced at W1 under
> any decision this category can make.**

---

## 11. Dependencies That Block This Document

| Dependency | State | What is blocked |
|---|:--:|---|
| **`PE-008` Observability and Monitoring Design** | ✅ **Issued** *(corrected §0)* | **No longer blocking as a specification.** Every SLI in §5.2 now has an owning design, and §5.8 reconciles the two SLO sets. **Blocking as an implementation**: nothing is instrumented, so no figure in §10 can be produced yet |
| `PE-007` Backup, DR and Continuity Design | ✅ **Issued** *(corrected §0)* | `SLI-RPO` and `SLI-RESTORE` have a design. **The `dr` environment is still unsized, uncosted and unprovisioned**, so `NFR-007` remains unevidenced |
| **Instrumentation of `PE-008`'s design** | Not built | §10's entire report. **This is now the single blocking dependency of this document**, and it is a build item rather than a specification gap |
| [`CO-003`](../14_Commercial_Vendor_and_Contract/CO-003_Statement_of_Work_and_Deliverable_Acceptance_Schedule.md) Statement of Work | ✅ **Issued** *(corrected — issued during authoring)* | §8.4's eight clauses **now have an instrument to be imposed in**. Whether they are in it is `PSL-Q-08` |
| `SV-004` On-Call, Paging and Escalation | This category | §6.4's burn-rate pages have nowhere to go |
| Synthetic monitoring **hosted outside the estate** | Not provisioned | `PSL-06`, `PSL-18` — the availability figure itself |
| Named service owners | **Zero named** | §7's OLAs cannot be signed; §9's explanations have no author |
| Operations Director ratification | Not sought | **Eleven** `Proposed` SLOs remain engineering's opinion (`M66` Q-03) |

---

## 12. Governing Rules — Consolidated

| # | Rule | § |
|---|---|:--:|
| **`PSL-01`** | A platform with no stated service level has an implicit one, set by the most recent outage | 3.2 |
| **`PSL-02`** | `OP-001` §4.5's support response commitments are **adopted by citation and never restated** | 7.2 |
| **`PSL-03`** | A catalogue entry names one service, one audience, one owner, one set of hours, one route | 4.1 |
| **`PSL-04`** | The catalogue's *"what it is"* sentence is **normative**; an SLI measuring something else measures the wrong thing | 4.2 |
| **`PSL-05`** *(revised §5.8.2)* | A service is available when the **real-request success ratio holds and the synthetic journey completes**. The SLO is computed from real requests per `PE-008` `VE-01`…`VE-05` | 4.4, 5.8.2 |
| **`PSL-06`** *(revised §5.8.2)* | **Below the minimum-volume threshold, the synthetic probe is authoritative.** A quiet hour is not an available hour by default | 4.4, 5.8.2 |
| **`PSL-06a`** | Synthetic probes run from outside the estate, ≥ 2 vantage points, reported as a **separate series** — never added to the SLI numerator (`PE-008` `VE-04`) | 5.8.2 |
| **`PSL-06b`** | The minimum-volume threshold is **set per service and published**; an unpublished threshold is a silent exclusion | 5.8.2 |
| **`PSL-07`** | Every SLI is a `PE-008` obligation; no service report is published from a hand-assembled figure | 5.2 |
| **`PSL-08`** | A measurement window is **the window in which the audience uses the service**, never the one that flatters the number | 5.4 |
| **`PSL-09`** | **No `P0` component carries the same availability objective as the service depending on it** | 5.5 |
| **`PSL-10`** | The composite arithmetic is the reason for `PE-001` `HA-01`: a single-node component cannot deliver 10.9 min/month | 5.5 |
| **`PSL-11`** | 99.95% over five serial dependencies demands 99.99% each — **4.4 minutes a month per component** | 5.5 |
| **`PSL-12`** | Planned maintenance is excluded from `SLI-AVAIL` only if **all four** conditions hold; an overrun is an incident | 5.6 |
| **`PSL-13`** | **Every published availability figure states its exclusion in the same sentence** | 5.6 |
| **`PSL-14`** | A commitment resting on an unmanageable supplier is **split** into the controlled part and the reported part | 5.7 |
| **`PSL-15`** | An untouched budget is reviewed in the same agenda item as an exhausted one | 6.2 |
| **`PSL-16`** | A burn-rate page is `Sev2` by default; `Sev1` only for a `P0` service in its window | 6.4 |
| **`PSL-17`** | A burn-rate alert names service, SLO, budget consumed **and budget remaining** | 6.4 |
| **`PSL-18`** | The figure a burn-rate alert cites is the externally-measured one | 6.4 |
| **`PSL-19`** | Burn-rate alerts un-suppress automatically at the maintenance window's stated end — never manually | 6.4 |
| **`PSL-20`** | **An SLO with no underpinning OLA is withdrawn, not published** | 7.1 |
| **`PSL-21`** | The **enumerated 13** P0 integrations are the P0 set, not `05-03` §2's summary of 12 | 8.2 |
| **`PSL-22`** | Every underpinning contract states what happens on **product withdrawal**, not only on termination | 8.5 |
| **`PSL-23`** | Every miss appears in the month it occurred — no netting, no annualisation, no exclusions invented after the fact | 9.2 |
| **`PSL-24`** | An SLA pause with no incident record behind it is a control failure | 9.3 |
| **`PSL-25`** | Every reported number traces to a query a third party could re-run | 10.3 |

**Findings raised by this document**

| # | Finding | Severity | Owner |
|---|---|:--:|---|
| **`PSL-F-01`** | **`NFR-049` permits up to 240 min/month of planned maintenance against `NFR-045`'s 131.5 min/month availability budget.** Without the `PSL-12` exclusion, the 24×7 target is breached by planned maintenance alone | **HIGH** | CTO + Enterprise Architecture |
| **`PSL-F-02`** | All five OLAs are unsigned because four of five functions have no identified members | HIGH | CTO + HR |
| **`PSL-F-03`** | **No SLO can exceed the availability of the cloud provider and the `BD-R` facility, and neither figure appears anywhere in the estate** | **HIGH** | CTO + Procurement |
| **`PSL-F-04`** *(revised)* | The service level report **cannot be produced at W1 under any decision this category can make** — not because `PE-008` is absent (it is now issued), but because **nothing it designs has been instrumented**. The blocker moved from specification to build | HIGH | CTO |
| **`PSL-F-05`** | **Eleven of twenty-one SLOs are `Proposed`** and one is deferred — `05-06` states four availability numbers, and `PE-008` derives eight, for a platform with **twenty-one separately-failing services** | MEDIUM | Enterprise Architecture |
| **`PSL-F-06`** | **`NFR-043` was misread as 99.5% in this document's first draft; it is a p95, so 95%.** Found by reconciling against `PE-008` `SLO-05`. A latency percentile read as an availability ratio is a defect class worth naming: **`p95` and `99.5%` differ by a factor of nine in permitted failures** | MEDIUM | This document *(corrected)* |
| **`PSL-F-07`** | **A real-request-ratio SLI reports success by measuring nothing during low-traffic hours** — precisely the 24×7 hours `S-07` and `S-08` commit to, with no service desk and no page. `PSL-06`'s minimum-volume rule is the countermeasure and it must be implemented in `PE-008`, not asserted here | **HIGH** | Head of Service + Platform Engineering |

---

## 13. Decisions Recorded

| # | Decision | Options considered | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| **`SV-002-D-01`** | Who ratifies the SLOs | (a) CTO alone; (b) CTO **with** the Operations Director; (c) Steering Committee | **(b)** | `M66` Q-03 is explicit: *"an SLA IT sets alone is a target, not an agreement."* The Operations Director owns the business consequence of every hour of downtime | Fourteen `Proposed` SLOs remain proposals until co-signed. The document is issuable; the commitment is not made |
| **`SV-002-D-02`** | Planned maintenance and availability | (a) Cut `NFR-049`'s allowance; (b) loosen `NFR-045`; (c) **exclude announced maintenance, and always state the exclusion** | **(c)** | (a) removes the only capacity for changes that cannot be done live; (b) weakens a commitment to fix a definition | `PSL-12` and `PSL-13`. Every published figure carries its exclusion. An overrun becomes an incident |
| **`SV-002-D-03`** | `NFR-048` payment path | (a) Publish 99.95% end-to-end; (b) abandon the target; (c) **split into platform-side committed, end-to-end reported, failover committed** | **(c)** | `IN-007` §9.3 makes (a) a commitment to something the Company cannot influence; (b) discards the part it can | Three objectives instead of one; `NFR-048` needs an `RQ-006` amendment to record the split |
| **`SV-002-D-04`** | Remedy for an internal breach | (a) Service credits between cost centres; (b) escalation and publication only | **(b)** | Money attached to an internal SLA turns reliability into a dispute about the definition of "outage" | §9.1's escalation ladder and `PSL-23`'s publication rule are the whole remedy |
| **`SV-002-D-05`** | Component objectives vs service objectives | (a) One number per service; (b) **components carry higher objectives, derived** | **(b)** | §5.5's arithmetic: four serial 99.9% components deliver 99.6%, not 99.9% | `S-02`, `S-03`, `S-04` carry 99.95%; this is a design constraint on `PE-001`, not a reporting choice |

---

## 14. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|:--:|---|
| `PSL-Q-01` | Will the Operations Director co-sign the **eleven** `Proposed` SLOs, and at what values? | Operations Director + CTO | **W2** | The entire commitment; `M66` Q-03 |
| `PSL-Q-02` | **What does the cloud provider commit to, and what does the `BD-R` facility commit to?** | Procurement + CTO | **W1** | `PSL-F-03`; every SLO in §5.3 rests on it |
| `PSL-Q-03` | Will synthetic monitoring be hosted **outside** the estate, and is it funded? | CTO | W1 | `PSL-06`, `PSL-18`, and `AUDIT-017` `OP-14`'s status-page problem, which has the same answer |
| `PSL-Q-04` | Does `RQ-006` accept the `NFR-048` split (`SV-002-D-03`) and the `NFR-049`/`NFR-045` exclusion (`SV-002-D-02`)? | Enterprise Architecture | W2 | Two NFR amendments |
| `PSL-Q-05` | **Is `INT-013` (email) given a documented, tested fallback**, or is its `P0` classification wrong? | Enterprise Architecture | **W1** | `IP-09` compliance; `AUDIT-017` `OP-03` |
| `PSL-Q-06` | What availability does `S-12` (`BD-R` resident service) commit to, given a single facility with no DR target? | CTO + Legal | W2 | The `S-12` SLO is `Proposed` against `AUDIT-017` `OP-01`, still CRITICAL and open |
| `PSL-Q-07` | Are the `KPI-085`…`091` baselines going to be measured before W1, or will the SLA start unbaselined? | BI Lead + `BM-002` | W1 | Every "improving" claim; `AUDIT-015` `RP-02` |
| **`PSL-Q-08`** | **Does `CO-003`, issued during this category's authoring, carry §8.4's eight underpinning-contract clauses?** If not, every supplier-dependent SLO in §5.3 rests on a commitment nobody flowed down | Procurement + Legal | **W1** | §8.4; `PSL-F-03` |

---

## 15. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| `AC-01` | Every one of `SV-001` §5.2's 21 services has a catalogue entry with all five `PSL-03` elements | §4.2 — 21 rows |
| `AC-02` | Every service has an availability SLO **and a stated measurement window** | §5.3; closes `PE-001-F-04` at this layer |
| `AC-03` | Every SLO is labelled Inherited, Derived or Proposed | §5.1, §5.3 — **counted by extraction: 7 Inherited, 4 Derived, 11 Proposed, 1 Deferred across 21 rows and 23 labels** (`S-07` and `S-15` carry two) |
| `AC-04` | The composite-availability constraint is derived, not asserted | §5.5, with the arithmetic shown |
| `AC-05` | The `NFR-045`/`NFR-049` contradiction is resolved by a recorded decision | §5.6; `SV-002-D-02`; `PSL-F-01` |
| `AC-06` | `NFR-048`'s unachievability is handled without either publishing or abandoning it | §5.7; `SV-002-D-03` |
| `AC-07` | Error budgets are stated in minutes per week, month and year for every SLO level used | §6.1 — 10 rows |
| `AC-08` | Every SLO traces to at least one OLA | §7.2; unsigned status stated per row |
| `AC-09` | The P0 integration set is the **enumerated 13**, not the summarised 12 | §8.2; `PSL-21` |
| `AC-10` | The document states what it cannot do at W1, in both `SV-001-D-04` branches | §10.4; `PSL-F-04` |
| `AC-11` | No metric identifier is invented (`SMF-21`) | `SLI-*` are indicator names within this document, not programme KPI identifiers; §11.1 of `SV-001` applies |
| `AC-12` | Every relative link resolves | Verified at issue |

**Definition of done.** Complete when every criterion is met, `PGD-000` is updated with a fresh
enumeration timestamp, and the approver has signed. **`AC-08` cannot be fully met** until the OLAs
have signatories, and no signatories exist (`PSL-F-02`).

---

## 16. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | `SV-001` §5.2, §5.3 | The 21-service index and the ownership obligations every OLA rests on |
| Upstream | [`PE-001`](../10_Infrastructure_DevOps_and_Environments/PE-001_Infrastructure_and_Network_Architecture_Design.md) §9 | Availability scopes, HA by tier, the maintenance-window reconciliation |
| Upstream | [`PE-006`](../10_Infrastructure_DevOps_and_Environments/PE-006_Capacity_Plan_and_Performance_Engineering_Baseline.md) | Volumetrics and scaling triggers that keep the objectives reachable |
| Upstream | [`IN-007`](../04_Integration_and_API_Engineering/IN-007_Payment_and_Financial_Gateway_Integration_Design.md) §9.3 | The single-acquirer constraint behind `SV-002-D-03` |
| Upstream ⛔ | `PE-007`, `PE-008` | **Absent — §11** |
| Downstream | `SV-003` | Runbooks state how a service is restored inside its RTO |
| Downstream | `SV-004` | §6.4's burn-rate thresholds are paging inputs |
| Downstream | `SV-006` | §5.6's maintenance overrun becomes an incident declaration; §9.1's repeat miss becomes a problem record |
| Downstream | `CO-003`, `CO-004` | §8.4's eight clauses |
| Downstream | `BM-002` | `PSL-Q-07`'s unbaselined KPIs |
| Lateral | [`MD-028`](../../project_content/02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-028_Priority_Severity_and_SLA_Definition_Register.md), [`OP-001`](../../project_content/17_Operations_Support_and_Runbooks/OP-001_Support_Model_Tiering_and_Routing_Content.md) §4.5/§4.6 | The sold-SLA boundary and the only sanctioned pause mechanism |
| Lateral | [`SP-031`](../../project_content/06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-031_SOP_IT_Service_Desk_and_Change_Management.md) §12 | `KPI-085`…`091`, all unbaselined |

---

## 17. References

**Within this repository**
[`PGD-000`](../PGD-000_Master_Register_of_Project_Guiding_Documents.md) ·
[`_CATEGORY_OVERVIEW.md`](_CATEGORY_OVERVIEW.md) ·
`SV-001`, `SV-003`, `SV-004`, `SV-005`, `SV-006` ·
[`PE-001`](../10_Infrastructure_DevOps_and_Environments/PE-001_Infrastructure_and_Network_Architecture_Design.md) ·
[`PE-006`](../10_Infrastructure_DevOps_and_Environments/PE-006_Capacity_Plan_and_Performance_Engineering_Baseline.md) ·
[`IN-007`](../04_Integration_and_API_Engineering/IN-007_Payment_and_Financial_Gateway_Integration_Design.md) ·
[`RL-001`](../12_Release_Deployment_and_Transition/RL-001_Release_Management_and_Versioning_Policy.md) ·
[`RQ-006`](../01_Requirements_Engineering/RQ-006_Non_Functional_Requirements_Specification.md) ·
[`GV-005`](../00_Programme_Governance_and_Control/GV-005_RAID_Register.md)

**Workspace**
[`05-06`](../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06_NonFunctional_Requirements_and_Standards.md) ·
[`M66`](../../1000fix_ERP_Module/03_Modules/K_Platform_and_Technology/M66_Internal_IT_Service_Management.md) ·
[`OP-001`](../../project_content/17_Operations_Support_and_Runbooks/OP-001_Support_Model_Tiering_and_Routing_Content.md) ·
[`OP-005`](../../project_content/17_Operations_Support_and_Runbooks/OP-005_Status_Page_and_Maintenance_Notice_Copy.md) ·
[`OP-014`](../../project_content/17_Operations_Support_and_Runbooks/OP-014_Manual_Fallback_Procedure_Set.md) ·
[`SP-031`](../../project_content/06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-031_SOP_IT_Service_Desk_and_Change_Management.md) ·
[`AUDIT-017`](../../project_content/_AUDIT/AUDIT-017_Category_17_OP_Content_Audit.md)

**External standards and sources** *(each verified 2026-08-19)*

| Source | Verified |
|---|:--:|
| ISO/IEC 20000-1:2018 §8.2.1, §8.3.3, §8.7.2 | 2026-08-19 |
| ISO/IEC 20000-1:2018/Amd 1:2024 · https://www.iso.org/standard/88434.html | 2026-08-19 |
| ISO/IEC 25010:2023 — product quality model | 2026-08-19 |
| Google SRE Workbook, *Alerting on SLOs* · https://sre.google/workbook/alerting-on-slos/ | 2026-08-19 |
| Atlassian Opsgenie lifecycle — end of sale 2025-06-04, shutdown **2027-04-05**, non-migrated data deleted | 2026-08-19 |

---

## 18. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-19 | Head of IT Service Management | Initial issue. Rule space `PSL` allocated after verification against 763 files. Twenty-one catalogue entries, twenty-one SLOs (7 inherited, 3 derived, 14 proposed), five OLAs, eleven underpinning contracts. Five decisions and five findings recorded, of which `PSL-F-01` (the maintenance/availability contradiction) requires an `RQ-006` amendment | CTO **jointly with the Operations Director** *(pending — `SV-002-D-01`)* |
| **1.1** | **2026-08-19** | Head of IT Service Management | **Reconciliation with `PE-008`, issued during authoring.** §0 added; new **§5.8** maps the two SLO sets, rules their precedence (`SV-002-D-06`) and resolves the synthetic-monitoring conflict (`SV-002-D-07`). **Three corrections to this document's own first draft**: `SLI-DELIVER` 99.5% → **95%** (`NFR-043` is a p95); `S-12`'s proposed number deferred to `SC-007` §9.5; `PSL-05`/`PSL-06` revised, `PSL-06a`/`PSL-06b` added. `PSL-F-04` revised; `PSL-F-06`, `PSL-F-07` added. Rule space re-verified against the 777-file baseline. **A fourth correction, found by this category's own audit**: the first draft asserted *"fourteen of twenty-one objectives are Proposed"* and *"7 inherited, 3 derived, 14 proposed"*; counted by extraction the table holds **7 Inherited, 4 Derived, 11 Proposed and 1 Deferred**. `PSL-F-05`, `SV-002-D-01`, `PSL-Q-01` and `AC-03` corrected | As above |
| **1.2** | **2026-08-19** | Head of IT Service Management | **Conformance to `RR-002` `IDC-08`** (timestamp and denominator in `rule_prefix:`). **`CO-003` was issued during authoring** — §8.3 and §11 corrected from ⛔, and **`PSL-Q-08` added**: does `CO-003` actually carry §8.4's eight clauses? Proposed-SLO count corrected to the measured 7/4/11/1. | As above |

---

*`SV-002` · Category 11 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
