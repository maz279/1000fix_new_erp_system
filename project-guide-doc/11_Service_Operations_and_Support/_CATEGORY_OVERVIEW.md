---
id: PGD-CAT-11
category: 11 — Service Operations & Support
code: SV
project: 1000FiX ERP System v2.0
version: 2.0
date: 2026-08-19
status: AUTHORED — 6 of 6 issued, audited in PGD-AUDIT-CAT-11
owner: Head of IT Service Management
enumeration_timestamp: 2026-08-19 03:05 (+06)
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
audit: ../_AUDIT/PGD-AUDIT-CAT-11_Category_11_Service_Operations_and_Support_Audit.md
---

# Category 11 — Service Operations & Support (`SV`)

## Purpose

`AUDIT-017` delivered the sharpest sentence in the entire workspace:

> **"The programme has operational content and no operational capability."**

Sixteen `OP-*` files describe how support will work — tiering, routing, macros, runbooks,
incident templates, DR playbooks, on-call handover. This category holds the documents that make
those descriptions **exist as a service**.

**It is now authored.** What follows records what was found in doing so.

## Documents

| ID | Document | Status | Pri | Needed by | Rules |
|---|---|:--:|:--:|:--:|--:|
| [`SV-001`](SV-001_Service_Management_Framework_and_Operating_Model.md) | Service Management Framework & Operating Model | ✅ | **P0** | **W1** | 27 `SMF` |
| [`SV-002`](SV-002_Platform_SLA_OLA_and_Internal_Service_Catalogue.md) | Platform SLA / OLA & Internal Service Catalogue | ✅ | P1 | W2 | 27 `PSL` |
| [`SV-003`](SV-003_Operational_Runbook_Master_Set.md) | Operational Runbook Master Set | ✅ | P1 | W2 | 33 `RBS` |
| [`SV-004`](SV-004_On_Call_Paging_and_Escalation_Design.md) | **On-Call, Paging & Escalation Design** | ✅ | **P0** | **W1** | 41 `OCP` |
| [`SV-005`](SV-005_Hypercare_and_Transition_to_Support_Plan.md) | Hypercare & Transition-to-Support Plan | ✅ | P1 | W2 | 35 `HCT` |
| [`SV-006`](SV-006_Problem_and_Major_Incident_Management_Procedure.md) | Problem & Major Incident Management Procedure | ✅ | P1 | W2 | 58 `MIM` |

**6 documents · 490 KB · 74,595 words · 221 governing rules · 34 decisions · 37 findings ·
49 open questions.** Enumerated 2026-08-19 03:06 (+06), after audit remediation.

**None can reach `Approved`.** `PGD-000` §0.3 test (d) requires an approval record, and no
constituted body can create one until `GV-001` `CC-01` completes (`PGD-A2-25`). `SV-004` and
`SV-005` additionally require HR Director and CFO co-approval, for which no holder exists.

---

## What the category found

### The gap is now arithmetic, not rhetorical

`AUDIT-017` could say the capability was missing. This category can say what it costs — and that
is a set of numbers a Steering Committee can approve or decline, which an assertion never was.

| Measurement | Where |
|---|---|
| **`NFR-049` permits 240 min/month of planned maintenance against `NFR-045`'s 131.5 min error budget.** The 24×7 availability target is breached **by planned maintenance alone**, before any incident | `SV-002` §5.6, `PSL-F-01` |
| **The on-call rota needs eleven people, not ten.** `OP-013` §4.3's six is right for the primary rotation and one short once its own secondary rota and annual leave are counted against its own `RT-04` ceiling — 1 in 2.7 against a 1 in 3 cap | `SV-004` §6.3, `OCP-F-01` |
| **Hypercare is ≈ 678 PW — ≈ 45% of the build estimate** — across 56 of the programme's 156 weeks, in three cost pools. The largest, **≈ 140 PW of branch-staff time**, is in no estimate at all | `SV-005` §5, `HCT-F-03`/`F-04` |
| **Two `P0` services have no runbook** — the payment path and the resident data service. The five existing runbooks are scoped by **infrastructure component**, and neither payments nor residency is a component | `SV-003` §5.3, `RBS-F-01` |
| **`NFR-091`'s 67 module runbooks weigh 17–26 PW** as templated appendices, or 77–115 PW done standalone. Neither figure is in any estimate | `SV-003` §5.4, `RBS-F-02` |
| **`S-12`'s MTPD is ≈ 2 hours and its achievable recovery time is unbounded** — the business-impact statement `PE-007` §7.5's forced decision needs and does not have | `SV-006` §9.4, `MIM-F-02` |

### The ruling that costs money

> **`SV-001-D-04`. `M66` is split by dependency, not deferred whole. `CD-163` (`cd_itsm`, 9 PW)
> moves to W1; `CD-164` (`cd_it_asset`, 5 PW) stays at W6.**

`M66` §16.3 justifies its W6 placement entirely on `M21` (W5) and `M06` (W6) — **both prerequisites
of `CD-164` alone**. `CD-163` has no dependency later than Wave 1. The move is 0.6% of the build
estimate and replaces twenty months of manual, unmeasurable service.

**It does not close the paging gap.** `CD-163` is an ITSM module; it does not page anybody.

### The ruling that costs almost nothing

> **`SV-004-D-01`. GoAlert, self-hosted in a separate cloud provider account, driving the local
> SMS gateway.**

Searching all 786 workspace files for any on-call product returns **two hits, neither a
procurement**. Of seven candidates assessed, **two were disqualified on verified lifecycle
grounds**:

| Product | Position, verified 2026-08-19 |
|---|---|
| Atlassian Opsgenie | **Shuts down 2027-04-05** — inside this programme's 36-month horizon |
| Grafana OnCall (OSS) | **Archived 2026-03-24**; its notification relay deprecated with it — and it is the option this estate would most naturally have reached for |

Neither fact is discoverable from the estate, because **`RR-005` remains unwritten**.

### The conflict adjudicated rather than absorbed

`PE-008` §8.5, issued mid-authoring, rules *"one severity model, defined here"* — a **three-level**
model over the space `OP-013` §4.1 owns as **four**. That is a **fourth** claimant against
`AUDIT-017` `OP-04`'s three, **whose corrections remain unmade**.

`SV-001` §6.7 rules for this category — `OP-013` §4.1 governs, `PE-008`'s model is mapped as an
alerting classification — and `SV-006` §4.2 lists all four outstanding one-line edits with the cost
of each while unmade. **Every other rule in `PE-008` §8 is adopted unchanged.**

---

## What is still absent, and none of it is designable

Category 10 has closed every observability, continuity and secrets gap a **design** could close.
What remains needs an establishment, a signature and a purchase order.

| # | Absent | Owner | By |
|---:|---|---|:--:|
| 1 | **A paging platform.** Named nowhere in 786 files | CTO | **W1** |
| 2 | **A staffed rota** — eleven positions, zero named people in five owning functions | CTO + HR | **W1** |
| 3 | **A Head of IT Service Management** — the SMS has an accountable owner and no responsible manager | CTO + HR | W1 |
| 4 | **On-call terms** — `OP-013` OI-03, open since 2026-08-20 | HR Director | **Before the first shift** |
| 5 | **Break-glass** — `PE-009` §8 designs it; none of the five physical components exists | Security Lead | **Before W1** |
| 6 | **The `dr` environment** — `PE-007` designs it; it is unsized, uncosted, unprovisioned | CTO | W2 |
| 7 | **A lawful DR path for resident data** — `AUDIT-017` `OP-01`, still CRITICAL; `PE-007` §7.5 calls the decision *forced and unmade* | CTO + Legal + DPO | **W2** |
| 8 | **≈ 678 PW of hypercare funding** | CFO | Before W1 cutover |
| 9 | **21 named service owners** | CTO | W1 |
| 10 | **Emergency spend delegation** — `OP-013` §4.8's limits are proposed | CFO | W1 |

**One account buys four of the outstanding requirements**: independent status-page hosting
(`AUDIT-017` `OP-14`), external synthetic monitoring (`SV-002` `PSL-Q-03`), the paging platform
(`SV-004` `OCP-Q-04`) and `PE-007`'s out-of-account immutable backup. `PGD-AUDIT-CAT-11` `R-08`.

---

## Dependencies

| Direction | Category | Relationship |
|---|---|---|
| Upstream | [`10_Infrastructure`](../10_Infrastructure_DevOps_and_Environments/) | **All nine `PE` documents issued.** `PE-008` produces the alert this category delivers; `PE-007` designs the continuity it governs; `PE-009` designs break-glass |
| Upstream | [`05_Security`](../05_Security_Privacy_and_Compliance/) | `SV-006` §7.1 hands major incidents involving personal data to `SC-011`; `M66` `BRU-ITS-21` is absolute |
| Upstream | [`00_Governance`](../00_Programme_Governance_and_Control/) | `SV-001` §8.4's establishment is a `GV-007` line; `SV-005` §5 belongs in `GV-004` |
| Upstream | [`99_Reference`](../99_Reference_Registers_and_Glossary/) | **`RR-002` now exists** and §5.9 cites `SV-003`'s rule-prefix allocation as its model protocol |
| Downstream | [`12_Release`](../12_Release_Deployment_and_Transition/) | `RL-003` go-live readiness requires operational capability to **exist**, and `SV-003`'s execution ledger is its evidence |
| Downstream | [`13_Training`](../13_Training_Change_and_Adoption/) | **`CH-005`'s champion charter is what releases `SV-005`'s largest cost pool** |
| Peer | `M66` Internal ITSM | This category specifies what `M66` must deliver, and **`SV-001-D-04` rules when** |

## Audience and change frequency

| Attribute | Value |
|---|---|
| Primary audience | CTO, HR Director, CFO, Head of IT Service Management, service desk, SREs, on-call engineers, branch IT, business owners |
| Change frequency | **Medium** — framework stable, runbooks continuous, rota quarterly |
| Standards basis | ISO/IEC 20000-1:2018 + Amd 1:2024 · ITIL 4 (12 of 34 practices adopted) · ISO 22301:2019 + Amd 1:2024 with ISO/TS 22317:2021 · ISO 9001:2015 cl. 8.5.1 / 10.2 · Google SRE (SLI/SLO/error budgets, multi-window burn rate) |
| Rule spaces | `SMF`, `PSL`, `RBS`, `OCP`, `HCT`, `MIM` — six, each collision-checked per `RR-002` `IDC-08`. **No rule in this category uses the form `SV-nn`**, which `OP-013` §4.1 already owns |

## Material built from

`project_content/17_Operations_Support_and_Runbooks/OP-001…016` — all 16 files, adopted by citation
and never restated ·
`project_content/_AUDIT/AUDIT-017` — 26 findings, 22 open, 1 critical ·
`1000fix_ERP_Module/03_Modules/K_Platform_and_Technology/M66` ·
`1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06` ·
`project_content/06_Process_SOP_and_Workflow/SP-031` ·
`project-guide-doc/10_Infrastructure_DevOps_and_Environments/PE-001…009`

---

*Category 11 · `SV` · 1000FiX ERP System v2.0 · CONFIDENTIAL*
