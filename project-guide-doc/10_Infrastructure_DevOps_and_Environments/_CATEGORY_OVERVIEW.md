---
id: PGD-CAT-10
category: 10 — Infrastructure, DevOps & Environments
code: PE
project: 1000FiX ERP System v2.0
version: 2.0
date: 2026-08-19
status: DRAFT FOR APPROVAL
owner: Platform Engineering Lead
enumeration_timestamp: 2026-08-19 02:00 (+06)
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
audit: ../_AUDIT/PGD-AUDIT-009_Category_10_Infrastructure_DevOps_and_Environments_Audit.md
---

# Category 10 — Infrastructure, DevOps & Environments (`PE`)

## Purpose

`02-05` §8 sizes production hardware in a table. **That is a shopping list, not an infrastructure
design.** This category supplies the design: where the system runs, how its parts reach each other,
which environments exist and what they may hold, how infrastructure is built and changed, how code
reaches production, how the estate is observed, how it recovers, and how its configuration and
secrets are governed.

---

## ✅ Authored — 9 of 9 issued 2026-08-19

| ID | Document | Status | Pri | Needed by |
|---|---|:--:|:--:|:--:|
| [`PE-001`](PE-001_Infrastructure_and_Network_Architecture_Design.md) | Infrastructure & Network Architecture Design | ✅ | **P0** | **W1** |
| [`PE-002`](PE-002_Environment_Strategy_and_Specification.md) | Environment Strategy & Specification | ✅ | **P0** | **W1** |
| [`PE-003`](PE-003_Infrastructure_as_Code_Standard.md) | Infrastructure-as-Code Standard | ✅ | **P0** | **W1** |
| [`PE-004`](PE-004_CI_CD_Pipeline_Design_Specification.md) | CI/CD Pipeline Design Specification | ✅ | **P0** | **W1** |
| [`PE-005`](PE-005_Containerisation_and_Orchestration_Design.md) | Containerisation & Orchestration Design | ✅ | **P0** | W1 |
| [`PE-006`](PE-006_Capacity_Plan_and_Performance_Engineering_Baseline.md) | Capacity Plan & Performance Engineering Baseline | ✅ | P1 | W2 |
| [`PE-007`](PE-007_Backup_Disaster_Recovery_and_Business_Continuity_Design.md) | **Backup, Disaster Recovery & Business Continuity Design** | ✅ | **P0** | **W1** |
| [`PE-008`](PE-008_Observability_and_Monitoring_Design.md) | Observability & Monitoring Design | ✅ | **P0** | W1 |
| [`PE-009`](PE-009_Configuration_and_Secrets_Management_Standard.md) | Configuration & Secrets Management Standard | ✅ | **P0** | W1 |

**Nine documents · 71 recorded decisions · 35 per-document findings + 6 cross-cutting (`PE-A-01`…
`PE-A-06`) · 84 fitness functions (`FF-101`…`FF-184`) · 63 open questions, of which 10 are marked
W0-blocking.**

> Counted by parsing the nine files at **2026-08-19 02:05 (+06)**, not composed while drafting. The
> first issue of this line stated 62 decisions and 62 questions; **both were wrong, and the check
> that caught them is the same one `AUDIT-016` `AP-18` and `PGD-AUDIT-007` `PGD-A7-05` recorded** —
> a summary written before the derivation it summarises. Recorded as `PGD-A9-04`.

---

## What the category measured

Extraction across the four source repositories at **2026-08-19 01:15 (+06)**:

| # | Measure | Result |
|---|---|---:|
| M-01 | Files in the four source repositories | **621** |
| M-02 | Of those, containing a network diagram, address plan, subnet or security-group design | **0** |
| M-03 | Occurrences of "Terraform" or "OpenTofu" | **0** |
| M-04 | Dockerfiles, Helm charts, Kubernetes manifests, Compose files | **0** |
| M-05 | **Distinct environments the estate requires** | **12** |
| M-06 | **Of those, provisioned** | **0** |
| M-07 | Environments named by `02-05` §9 · by `TS-001` §4.7 · **members common to both** | 6 · 6 · **2** |
| M-08 | **Fitness functions specified estate-wide with no pipeline to run them** | **127** |
| M-09 | `NFR-055` telemetry ÷ `NFR-056` GPS, annual data points | **62.6×** |
| M-10 | Kubernetes minor upgrades required across 36 months | **~9**, first inside W1 |
| M-11 | Database connections derived against the primary | **~264** — no pooler in any sizing table |
| M-12 | P0 integrations with a **tested** manual fallback (`NFR-050`) | **0 of 13** |
| M-13 | `OP-02`'s three named preconditions of `NFR-007` | **0 of 3 provisioned** |

---

## The two findings this category was written to close

| Finding | Severity | State |
|---|---|---|
| **`OP-01`** — *"there is no lawful DR path for Bangladesh-resident personal data"* | **Critical** | **Designed, not closed.** `PE-007` §7 designs route 2 against `PE-001` §3.3's **three named, verified in-country facilities**, and makes `SC-007`'s degraded mode drillable. **Closes on a CTO/CFO/Legal decision that has been available since `OP-01` was raised** |
| **`OP-02`** — *"the `dr` environment is named in the architecture and provisioned nowhere"* | High | **All three preconditions designed** — WAL archiving, the `BKP-3` immutable copy, the drill programme. **Closes on provisioning plus the first drill** |

> **`OP-01`'s remedy was never a technical unknown.** `SC-007` §9.4 recommended provisioning an
> in-country DR target and recorded that it *"cannot choose; it can only make the choice explicit."*
> `PE-001` §3.3 names a **Tier IV** facility with Uptime Institute certification of operational
> sustainability and two **Tier III** facilities, one PCI-DSS certified — all verified 2026-08-19.
> **The gap is an untaken procurement decision, not an unavailable capability.**

---

## Rulings that change other documents

| Ruling | Effect |
|---|---|
| **`PE-003-D-01`** — OpenTofu, with Terraform as the named fallback | **Corrects `PGD-000`'s own `PE-003` row**, which names Terraform. Terraform has been **BUSL 1.1 since v1.6.0**; `AR-013` `LW-01` would require an exception the estate's policy makes avoidable |
| **`PE-002-D-01`** — one inventory of twelve environments | **Supersedes `TS-001` §4.7 and `02-05` §9**, and extends `AR-001` §8.5 from six rows to twelve (`RC-01`…`RC-04`) |
| **`PE-008-D-03`** — eight SLOs with SLI, window and error budget | Rules the two undefined measurement windows in `NFR-046` and `NFR-048`; referred to `RQ-006` for correction at source |
| **`PE-008-F-01`** — named fallbacks for Grafana, Loki and Tempo | **Closes `AR-013`'s own `LW-01` violation** — Grafana was `Adopt` with no named fallback, and Loki and Tempo were absent from the radar entirely |
| **`PE-005` `VL-05`** — Kubernetes and K3s added to `AR-013` §7's currency table | The component with the **shortest support window in the estate** was not on it |
| **`PE-A-01`** — 13 P0 integrations, not 12 | **Corrects Category 04**, which repeated `05-03` §2's summary rather than counting its rows — confirming `AUDIT-017` `OP-03`. Applied to `IN-001`, `IN-004` and `IN-008` at this issue |

---

## What "done" looks like for this category

| # | Criterion | Position at issue |
|---|---|---|
| 1 | A network exists, zoned, addressed and segmented | **Designed. Provisioned: none** |
| 2 | Twelve environments exist, each with a stated data class and owner | **Specified. Provisioned: 0 of 12** |
| 3 | Every resource is built from code, and drift is detected and reverted | **Standard issued. Engine ratification pending** |
| 4 | The pipeline runs, and the estate's **184** fitness functions execute in it | **Designed. Running: 0** |
| 5 | `NFR-007` is evidenced by a drill, not asserted | **Designed. Drills run: 0**, and DR RAG is **red** |
| 6 | Every alert fires on user-visible harm and links to a runbook | **Designed. Instrumented: 0 of 8 SLOs** |
| 7 | Break-glass exists and has been rehearsed | **Designed. `OP-08` remains open** |

**None of the seven is complete, and none was going to be completed by a document.** What the
category delivers is the design, the measurement, the rulings, and a costed, sequenced plan — with
an honest statement of the distance to done.

---

## Blocking dependencies this category surfaced and cannot resolve

| # | Blocker | Owner | Consequence |
|---|---|---|---|
| 1 | **`Z4` DR target — option A, B or C** | **CTO + CFO + Legal** | `NFR-007` does not apply to residency-classified data; **option C is the current position by default, not by decision** |
| 2 | **`RGN-S`, `BKP-3`, WAL archiving funded** | CTO + CFO | *"The largest unfunded operational obligation the content register has surfaced"* |
| 3 | **Wave 0 provisioning and pipeline funded** | Programme Director | 8 of 12 environments and 13 of 15 pipeline deliverables at W0/W1, into a **5.33×** over-committed wave |
| 4 | **Regional provider selection** | CTO | Every IaC module and cost figure depends on it |
| 5 | **Break-glass authority named** | CTO + Security Lead | Three documents forbid standing access assuming a path that does not exist |
| 6 | **`SC-004`'s 38 access profiles** | `SC-004` owner | Break-glass cannot be implemented against an absent identity model |
| 7 | **Connection pooler** | Chief Architect | ~264 connections; portal autoscaling without one converts a spike into a database outage |
| 8 | **`DA-001` partition key, outbox indexing, time-series retention** | `DA-001` owner | The 2 TB and 4 TB allocations are undefensible without them |
| 9 | **Kubernetes upgrade treadmill in a plan** | Platform + `GV-004` | ~9 upgrades, the first inside W1 |
| 10 | **`AP-02` renumbering** — `NFR-092` means two different things | Enterprise Architecture | `PE-008` implements one of the two senses and must qualify every citation |

---

## Dependencies

| Direction | Category | Relationship |
|---|---|---|
| Upstream | `02_Architecture` | `AR-001` §8 trust zones, isolation tiers, split residency, DR constraints, environment ladder, sizing basis; `AR-013` licence rules |
| Upstream | `03_Data` | `DA-001` schema and partitioning; `DA-005` classification; `DA-006` retention |
| Upstream | `05_Security` | `SC-001` control set; **`SC-007` §9's three DR routes**; `SC-004` identity; `SC-006` cryptography |
| Upstream | `04_Integration` | `IN-001` `Z6` egress; `IN-004` counterparty timings; `IN-008` sandbox and drills |
| Upstream | `08_Quality` | **`QA-005` §11.1's eight explicit requirements on `PE-004`** |
| Upstream | `09_Data_Migration` | `MG-005`'s `migration-staging` |
| Downstream | `11_Service_Operations` | Alerts, severity, break-glass and failover feed incident response; **`OP-012` becomes executable** |
| Downstream | `12_Release` | The promotion path and rollback |
| Downstream | `14_Commercial` | `CO-005` must re-derive the three excluded cost lines |
| Downstream | `15_Benefits` | Cost per transaction |

---

## Audience and change frequency

| Attribute | Value |
|---|---|
| Primary audience | Platform engineers, SREs, every developer, Release Management |
| Change frequency | **High in W1**, then controlled — `PE-003` makes every change a reviewed plan |
| Standards basis | ISO/IEC/IEEE 42010:2022 · NIST SP 800-207, SP 800-190, SP 800-34, SP 800-57, SP 800-218 · ISO 22301:2019 · ISO/IEC 27031:2011 · ISO/IEC 27001:2022 · ISO/IEC 25010/25023 · OCI · Kubernetes · OpenTelemetry · W3C Trace Context · Google SRE · Twelve-Factor · CIS Benchmarks · SLSA · 3-2-1-1-0 · Bangladesh Bank ICT Security Guideline v4.0 |

> **Two version-currency positions are recorded rather than assumed.** **Terraform is BUSL 1.1**
> from v1.6.0, so the estate uses **OpenTofu** (MPL-2.0, Linux Foundation, CNCF). **Kubernetes 1.34
> reaches end of support on 27 October 2026** — inside Wave 1 — and the platform carries the
> shortest support window of any component in the estate.

---

## Existing material this category built from

`1000fix_ERP_Module/02_Architecture/02-05` §8, §9 ·
`primary-doc/…Technology_Stack_Specification.md` §17, §18, §21, §22 ·
`1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06` ·
`project_content/17_Operations_Support_and_Runbooks/OP-007…OP-016` ·
`project_content/13_Test_and_Acceptance_Content/TS-001` §4.7 ·
`project_content/_AUDIT/AUDIT-017` `OP-01`…`OP-26`

---

*Category 10 · `PE` · 1000FiX ERP System v2.0 · CONFIDENTIAL*
