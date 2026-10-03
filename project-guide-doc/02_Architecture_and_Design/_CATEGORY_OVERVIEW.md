---
id: PGD-CAT-02
category: 02 — Architecture & Design
code: AR
project: 1000FiX ERP System v2.0
version: 2.0
date: 2026-08-18
status: AUTHORED — 13 of 13 issued, awaiting approval
owner: Chief Architect
last_enumerated: 2026-08-18 03:10 (+06)
audit: ../_AUDIT/PGD-AUDIT-003_Category_02_Architecture_and_Design_Audit.md
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# Category 02 — Architecture & Design (`AR`)

**13 of 13 documents issued 2026-08-18 · audited · 17 findings, 6 closed, 11 open**

---

## Purpose

Requirements say **what**. Architecture says **how the system is structured so that the what is
achievable, changeable and operable**.

This was the category the programme was thinnest in — 3 of 13 partially covered, 10 absent — and it
is the category from which build defects are most expensive to recover. An architecture error found
in Wave 6 costs 50–100× what it costs in Wave 1.

---

## Documents

| ID | Document | Standard | Status | Pri | Needed by |
|---|---|---|:--:|:--:|:--:|
| `AR-001` | **Software Architecture Document (SAD)** | ISO/IEC/IEEE 42010:2022 | ✅ | **P0** | **Now** |
| `AR-002` | Enterprise & Solution Architecture Blueprint | TOGAF 10 ADM A–B | ✅ | P0 | W1 |
| `AR-003` | **Software Design Description (SDD)** — method, viewpoints, exemplar | IEEE 1016-2009 | ✅ ◐* | **P0** | **W1** |
| `AR-004` | Architecture Decision Record Library | Nygard ADR · MADR 4.0 | ✅ | P0 | Now |
| `AR-005` | Module Boundary & Overlap Rules Register | DDD bounded contexts | ✅ | P0 | W1 |
| `AR-006` | Module Dependency Map & Build Sequence | Acyclic Dependencies Principle | ✅ | P0 | W1 |
| `AR-007` | Odoo Module Architecture & Code Structure Standard | Odoo 19 · OCA guidelines | ✅ | **P0** | **W1** |
| `AR-008` | Domain Model & Bounded Context Map | DDD aggregates & invariants | ✅ | P1 | W1 |
| `AR-009` | Event-Driven Architecture & Messaging Design | Outbox · EIP · CloudEvents | ✅ | **P0** | **W1** |
| `AR-010` | Offline-First Synchronisation Architecture | Command journal · idempotent receiver | ✅ | P0 | W2 |
| `AR-011` | AI/ML Architecture & Model Specification | ISO/IEC 23894 · 42001 · Model Cards | ✅ | P1 | W5 |
| `AR-012` | Architecture Compliance & Fitness Function Standard | Evolutionary architecture | ✅ | P2 | W2 |
| `AR-013` | Technology Radar & Build-vs-Buy Register | Radar practice · ISO/IEC 5230 | ✅ | P2 | W2 |

\* **`AR-003` is inherently incremental.** It issues the method, ten estate design patterns and one
worked exemplar (`SDD-M01`). **Design coverage is 1 of 93 units (1.1%)**; the remaining 92 are
scheduled in its §3.2 against the wave plan. Its status is ✅ **as a standard** and ◐ **as a set**,
and it says so rather than claiming a binary.

> **On the ✅ status.** `PGD-000` §0.3 requires four tests. Tests (a) named file at a stated path,
> (b) complete front matter, and (c) ≥90% of the governing standard's section set are met by all 13
> and verified in `PGD-AUDIT-002` §7.2. Test (d) requires **a named owner *and* an approval record**.
> Owners are named in every front matter; **no approval record exists, because no constituted body
> can create one** — finding `PGD-A1-09`, which is true of all 609 workspace files. This is stated
> rather than quietly assumed away.

---

## The three altitudes, now covered

| Altitude | Document | Question it answers | Consumer |
|---|---|---|---|
| **System** | `AR-001` SAD | How do 67 modules, 12 surfaces, 16 services, 24 OSS systems and 6 environments form one system? | Architects, vendor, CTO |
| **Module** | `AR-003` SDD | What models, methods, states and events realise `M01`? | Developers |
| **Decision** | `AR-004` ADRs | Why is it this way, and what did we reject? | Every future maintainer |

`02-01_ERP_Module_Architecture_and_System_Map.md` sat between the first two and satisfied neither.
It is now **superseded as an architecture description** by `AR-001` and retained as a catalogue and
layer-model reference.

---

## What this category measured

Every figure counted from the filesystem at **2026-08-18 02:05 (+06)**. Reproducible commands in
`AR-006` §9 and `PGD-AUDIT-002` §7.3.

| Measurement | Result | Where |
|---|---:|---|
| Module specifications on disk | **67 of 67** *(published figure: 65)* | `AR-001` §2.4 |
| Declared dependency edges | **447** | `AR-006` §3.1 |
| **Wave-order violations** (`_MODULE_TEMPLATE` §16.3) | **32** | `AR-006` §5 |
| Mutual dependency pairs | **18** — 6 legitimate, 11 to break | `AR-006` §4 |
| `RG-04` reciprocity failures | **55** | `AR-006` §7 |
| Boundary assertions across §3.1/3.2/3.3 | **3,040** | `AR-005` §2.2 |
| Distinct entities declared owned | **1,335** *(catalogued: 225)* | `AR-008` §2.2 |
| Entities owned by more than one module | **34** | `AR-008` §7 |
| §10.2 references whose owner does not define them | **0** ✅ *(the 255-defect is remediated)* | `AR-008` §2.3 |
| **Distinct domain events declared published** | **988** *(registered: 64)* | `AR-009` §10.1 |
| Events consumed with no producer | **8** | `AR-009` §10.4 |

---

## What "done" looked like for this category — and whether it was achieved

| # | Criterion (from v1.0 of this overview) | Outcome |
|---|---|---|
| 1 | `AR-001` defines stakeholders, concerns and ≥ 6 views with rationale | ✅ **7 viewpoints, 7 views, 14 concerns, 11 quality-attribute scenarios** |
| 2 | `AR-007` makes *"extensions are separate modules"* mechanically enforceable | ✅ **§5.1 decision tree, §5.4 fork register, `FF-03` CI gate** |
| 3 | `AR-009` closes `AP-01`: the 14 missing events exist | ◐ **Ruled and scheduled, not closed.** The true gap is **953**, not 21. Closes with `IN-003` |
| 4 | `AR-005` / `AR-006` make the §16.3 wave rule verifiable across all 67 | ✅ **Verified — and it fails 32 times** |
| 5 | Every decision in `02-05` §10 has a full ADR with rejected options | ✅ **30 ADRs**, 2 Proposed pending ratification |

---

## Findings this category raised

`PGD-AUDIT-002` — **17 findings · 3 critical · 6 closed · 11 open.** The three critical:

| ID | Finding |
|---|---|
| **`PGD-A3-04`** | **The unregistered-event gap is 953, not 21** — `05-03` §4.2 covers 6.5% of the event surface |
| **`PGD-A3-09`** | **32 wave-order violations**, including M29 (W1, in-degree 53) depending on M21 (W5) |
| **`PGD-A3-13`** | **The entity catalogue is stale ~6×** — 225 catalogued, 1,335 declared. `DA-001` is sized against the wrong number |

**Two findings are against this authoring session's own work** (`PGD-A3-16`, `PGD-A3-17`) — a count stated
before its rows were finished, and a stale figure carried forward instead of counted. Both are the
estate's recurring defect class, both are closed, and both are recorded rather than smoothed over.

---

## Blocking dependencies this category cannot resolve

| # | Blocker | Owner | Consequence |
|---|---|---|---|
| 1 | **`BE-005` (CD master register) does not exist** | CTO | **No SDD can be design-gated; no manifest can pass `FF-16`.** All 93 design units blocked |
| 2 | **Role register incomplete** — R39–R46 unregistered, R60 duplicates R32 | CTO / `SC-004` | `FF-26` unsatisfiable; **18 SoD conflicts unenforced** |
| 3 | **ADR-017 (event naming) unratified** | Design Authority | ~245 renames are free now and a dual-publish migration later |
| 4 | **Five Wave 1/W3 scope movements undecided** | Steering / `GV-004` | 19 of 32 wave violations stay open |
| 5 | **`D-13` split-residency legal opinion; `D-025`, `D-026`, `D-027` undecided** | CFO / CTO | See `AR-004` §6 |
| 6 | **`UX-006` (Mobile UX) not written** | `UX-006` owner | Blocks APP-01 in W2 (`AR-010` Q-02) |

---

## Dependencies

| Direction | Category | Relationship |
|---|---|---|
| Upstream | `01_Requirements` | `AR-001` §10 derives quality-attribute scenarios from `RQ-006` — **using `05-06` directly, as `RQ-001` is unwritten** |
| Upstream | `00_Governance` | `GV-002` Design Authority must exist to approve; `GV-003` mirrors every ADR |
| Downstream | `03_Data` | `DA-001` realises `AR-008` — **and must be sized from 1,335, not 225** |
| Downstream | `04_Integration` | `IN-002` realises `AR-001` §7.1; **`IN-003` carries 988 registrations** |
| Downstream | `05_Security` | `SC-002` threat model requires `AR-001` §8.1 trust zones — **now available** |
| Downstream | `07_Build` | `BE-004` realises the development view; `BE-005` is a **blocking prerequisite in the other direction** |
| Downstream | `08_Quality` | `QA-003` derives from `AR-003` state machines and invariants |
| Downstream | `10_Infrastructure` | `PE-001`/`PE-002` realise `AR-001` §8; `PE-004` implements `AR-012`'s 35 gates |

---

## Audience and change frequency

| Attribute | Value |
|---|---|
| Primary audience | Architects, lead developers, implementation vendor |
| Change frequency | **Medium** — `AR-001`/`AR-002` low · `AR-003` grows per wave (92 units outstanding) · `AR-004` append-only · `AR-006`/`AR-013` regenerated at every wave gate |
| Standards basis | ISO/IEC/IEEE 42010:2022 · IEEE 1016-2009 · ISO/IEC 25010:2023 · ISO/IEC 23894:2023 · ISO/IEC 42001:2023 · ISO/IEC 5230 · arc42 7.0 · C4 · TOGAF 10 ADM · DDD |
| Re-audit | **At the Wave 1 gate** (`PG-M7`), with §"What this category measured" regenerated |

---

*Category 02 · `AR` · 1000FiX ERP System v2.0 · CONFIDENTIAL*
