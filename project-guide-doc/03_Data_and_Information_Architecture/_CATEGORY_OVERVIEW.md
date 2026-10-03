---
id: PGD-CAT-03
category: 03 — Data & Information Architecture
code: DA
project: 1000FiX ERP System v2.0
version: 2.0
date: 2026-08-18
status: AUTHORED — 9 of 9 issued, awaiting approval
owner: Data Architect / Chief Data Officer (unappointed — see DA-003 §5)
last_enumerated: 2026-08-18 16:05 (+06)
audit: ../_AUDIT/PGD-AUDIT-005_Category_03_Data_and_Information_Architecture_Audit.md
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# Category 03 — Data & Information Architecture (`DA`)

**9 of 9 documents issued 2026-08-18 · audited · 18 findings, 5 closed, 13 open**

---

## Purpose

**In an ERP the data model *is* the system.** A service order, an invoice, a warranty claim and a
marketplace payout are the same underlying facts seen from different angles — and if the model is
wrong, no amount of good code recovers it.

This category also carries the artefacts that make the **Personal Data Protection Act 2026**
satisfiable in practice rather than in policy.

---

## Documents

| ID | Document | Standard | Status | Pri | Needed by |
|---|---|---|:--:|:--:|:--:|
| `DA-001` | **Logical & Physical Data Model / Database Schema Specification** | ISO/IEC 11179-1:2023 · 3NF · PostgreSQL 16 | ✅ ◐* | **P0** | **W1** |
| `DA-002` | **Data Dictionary** | ISO/IEC 11179-1/-6/-31:2023 | ✅ ◐* | **P0** | **W1** |
| `DA-003` | Data Governance Framework & Stewardship Model | DAMA-DMBOK 2.0 · ISO/IEC 38505-1 | ✅ | P0 | W1 |
| `DA-004` | Master Data Management Design | DAMA-DMBOK 2.0 Reference & Master Data | ✅ | P1 | W2 |
| `DA-005` | Data Classification & Handling Standard | ISO/IEC 27001:2022 A.5.12–A.5.14 | ✅ | **P0** | **W1** |
| `DA-006` | Data Retention, Archival & Deletion Design | ISO 15489-1:2016 · saga pattern | ✅ | P0 | W2 |
| `DA-007` | Analytical & Dimensional Model Specification | Kimball · ClickHouse | ✅ | P1 | W4 |
| `DA-008` | Data Quality Management Plan | ISO/IEC 25012 · ISO 8000-61:2016 | ✅ | P2 | W3 |
| `DA-009` | Reference Data & Code List Register | ISO/IEC 11179-32:2023 | ✅ | P1 | W1 |

\* **`DA-001` and `DA-002` are inherently incremental.** `DA-001` is ✅ as a **standard** on issue;
as a **complete DDL set** it tracks `AR-003`'s per-module schedule. `DA-002` is ✅ as a **registry
design**; as a **populated registry** it is **0 of ~17,000–19,000 elements**. Both say so rather than
claiming a binary.

> **On the ✅ status.** `PGD-000` §0.3 tests (a) named file, (b) complete front matter and (c) ≥90% of
> the governing standard's section set are met by all nine and verified in `PGD-AUDIT-005` §6.2.
> Test (d) requires a named owner **and an approval record**. Owners are named; **no approval record
> exists, and for this category the approver — the Chief Data Officer — does not exist either**
> (`PGD-A5-07`). Stated rather than assumed away.

---

## What this category measured

Every figure counted from the filesystem at **2026-08-18 14:30 (+06)**. Commands in `DA-001` §15 and
`PGD-AUDIT-005` §6.3.

| Measurement | Result | Where |
|---|---:|---|
| Entity rows declared in module §10.1 tables | **1,370** | `DA-001` §2.2 |
| **Distinct tables** | **1,335** *(catalogued in `05-02`: 225)* | `DA-001` §2.2 |
| Declared key attributes | **11,622** | `DA-001` §2.2 |
| **Distinct field names** | **5,301** | `DA-001` §2.2 |
| Field names appearing exactly once | **4,020** (76%) | `DA-002` §2.2 |
| **Estimated total data elements** | **~17,000–19,000** | `DA-002` §2.2 |
| Entities declaring a `state` field | **348** | `DA-001` §2.2 |
| `company_id` declared *(rule requires it on every transactional model)* | **12** (0.9%) | `DA-001` §2.4 |
| `operating_unit_id` declared | **18** (1.3%) | `DA-001` §2.4 |
| **Bare `currency` vs `currency_id`** | **54 / 8** | `DA-001` §2.4 |
| `MD-*` files vs assigned a data owner | **48 / 45** | `DA-003` §2.3 |
| Enumeration candidates vs registered code lists | **~470 / 0** | `DA-009` §3 |
| Dimensional objects — `05-02` §9 vs `RP-006` §4.3 | **30 / 18**, no cross-reference | `DA-007` §2 |

---

## What "done" looked like — and whether it was achieved

| # | Criterion (from v1.0) | Outcome |
|---|---|---|
| 1 | `DA-001` produces executable DDL, and PostgreSQL partitioning **names an actual partition key** | ✅ **12 partitioned tables, each with a named key.** `fix_service_order` by `create_date`, not `state` — a partition key must be immutable |
| 2 | `DA-002` is the single field lookup, with a **PII flag and PDPA sensitivity class** on each, so `SC-003` and `SC-007` can be built from data rather than opinion | ✅ **24 mandatory attributes; §8.4 specifies the exact `SC-003` extract.** ◐ as a populated registry — 0% |
| 3 | `DA-005` reflects audit `C-05` — NID, TIN, biometric templates and KYC are statutorily sensitive | ✅ **and it goes further**: `PGD-A5-03` records that the statutory basis may be a mirror, not an exclusion |
| 4 | `DA-007` closes audit `RP-01`: 250 KPI identifiers reconcile to a registered set | ◐ **Position taken, not closed.** `KP-02` refuses to physicalise a measure for an unregistered metric, so the ambiguity is not baked into schema. Closes with `RP-001`'s ratification of the 196 |

---

## Findings this category raised

`PGD-AUDIT-005` — **18 findings · 3 critical · 5 closed · 13 open.** The three critical:

| ID | Finding |
|---|---|
| **`PGD-A5-01`** | **Entity catalogue stale ~6×** — `05-02` covers 225 of 1,335 tables. `DA-001` and `DA-002` are sized against the corrected number |
| **`PGD-A5-03`** | **Residency may be a synchronised mirror, not an exclusion.** The Feb 2026 amendment narrowed the scope and defines "restricted" by **impact**, not field type. The estate may be paying the higher price |
| **`PGD-A5-13`** | **No `LG-009` class → table mapping exists.** Without it the disposal engine selects nothing and 44 KB of retention policy is inert |

**One finding is against this authoring session's own work.** `PGD-A5-17`: Category 03 cited
`FF-36` and `FF-37` six times before they existed in `AR-012` — **precisely the `F3` defect class
`DA-002` was written to close.** `AR-012` is reissued at v1.1 with 37 checks.

---

## Blocking dependencies this category cannot resolve

| # | Blocker | Owner | Consequence |
|---|---|---|---|
| 1 | **No Chief Data Officer** (`PGD-A5-07`) | CTO / Board | Five documents depend on the role; `DA-005` `AS-01` blocks production without classification approval |
| 2 | **`MD-043` and `MD-048` unowned** (`PGD-A5-06`) | MDM Lead / HR Director | `GOV-01` blocks the seed load; `MD-048` sequences all 47 others |
| 3 | **`LG-009` class → table mapping** (`PGD-A5-13`) | Data Architect | The disposal engine cannot select a row |
| 4 | **`DEP-31` / `D-13` residency opinion** (`PGD-A5-03`) | CFO / Legal / DPO | The physical schema, `SC-007` and `PE-001` all follow from it |
| 5 | **`BE-005` does not exist** | CTO | No table can cite an issued CD identifier |
| 6 | **196 unregistered KPIs** (`RP-01`) | Enterprise Architecture | `RP-006` cannot declare `metrics_served`; `DA-007` will not physicalise them |

---

## Dependencies

| Direction | Category | Relationship |
|---|---|---|
| Upstream | `02_Architecture` | `DA-001` realises the `AR-008` domain model; `DA-005` sits orthogonal to `AR-001`'s zones and tiers |
| Upstream | `00_Governance` | `DA-003` specialises `GV-002`; Council rulings minute to `GV-003` |
| Downstream | `04_Integration` | Event and API payload schemas derive from `DA-002` registered elements |
| Downstream | `05_Security` | **`SC-003` DPIA and `SC-007` residency both require `DA-002` attributes 21–23** — currently 0% populated |
| Downstream | `09_Migration` | Every `DM-*` workbook targets `DA-001`, and now needs a `legacy_source`/`legacy_id` column added |
| Downstream | `08_Quality` | `QA-004` test-data masking derives from `DA-005` §6.5 |
| Downstream | `10_Infrastructure` | `PE-006` sizing from `DA-001` §7; `PE-007` must build `DA-006` BK-02 post-restore suppression |

---

## Audience and change frequency

| Attribute | Value |
|---|---|
| Primary audience | Data architects, developers, DBAs, migration team, DPO |
| Change frequency | **High during W1–W3, then controlled.** `DA-001`/`DA-002` grow per wave; `DA-005`/`DA-009` are reviewed at every wave gate |
| Standards basis | ISO/IEC 11179-1/-6/-31/-32:2023 · DAMA-DMBOK 2.0 (2024 revision) · ISO/IEC 27001:2022 · ISO 15489-1:2016 · ISO/IEC 25012 · ISO 8000-61:2016 · Kimball · PDPA 2026 |
| Re-audit | **At the Wave 1 gate** (`PG-M7`), with the measurement table regenerated |

---

*Category 03 · `DA` · 1000FiX ERP System v2.0 · CONFIDENTIAL*
