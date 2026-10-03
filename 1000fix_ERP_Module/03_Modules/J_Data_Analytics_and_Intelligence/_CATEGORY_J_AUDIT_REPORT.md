---
id: FIX-ERP2-CAT-J-AUDIT
category: J
category_name: Data, Analytics & Intelligence
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-13
status: COMPLETE
classification: CONFIDENTIAL — Internal Use Only
scope: The 4 module specifications in 03_Modules/J_Data_Analytics_and_Intelligence
---

# Category J — Module Specification Audit Report

**Audit of the 4 Data, Analytics & Intelligence module specifications against
`_CATEGORY_OVERVIEW.md`, `03_Modules/_MODULE_TEMPLATE.md`, and the cross-cutting registers.**

---

## 1. Audit Result

**PASS with 5 findings** — 1 corrected during audit, 4 raised as actions on documents outside
this category.

| # | Dimension | Result |
|---|---|---|
| 1 | Module coverage vs `_CATEGORY_OVERVIEW.md` §2 | **PASS** — 4 of 4 |
| 2 | Structural conformance to `_MODULE_TEMPLATE.md` | **PASS** — 19 sections each |
| 3 | Front matter vs overview §2 and `02-02` register | **PASS** — code, priority, wave, owner, category all match |
| 4 | FR identifier integrity | **PASS** — 146 requirements, no gaps, no duplicates |
| 5 | Declared vs measured requirement counts | **PASS** — all 4 match their §1 declaration |
| 6 | CD identifier allocation | **PASS** — 22 IDs, no duplicates, contiguous new block CD-187…199 |
| 7 | Effort: §16.2 sum vs §1 declaration | **PASS** — exact in all 4 (26 / 18 / 34 / 19 PW) |
| 8 | Layer allocation sums to 100% | **PASS** — all 4 |
| 9 | Business rule / automation / AC / technical / question ID sequences | **PASS** — no gaps, no duplicate table rows in any own-prefix sequence |
| 10 | Overview §3 platform-vs-BI split honoured | **PASS** — see §7 invariant 1 |
| 11 | Overview §4 M28-vs-M63 split honoured | **PASS** — see §7 invariant 6 |
| 12 | Overview §5 boundary map coverage | **PASS** — 14 of 14 rows; the 2 rows owned outside Category J are claimed out-of-scope in the correct module |
| 13 | **Overview §6 model portfolio coverage** | **PASS** — **14 of 14 models**, each with its named consumer, accuracy target and fallback carried verbatim into M26 §5.3–§5.6 |
| 14 | **Overview §7 AI governance rules** | **PASS** — **10 of 10**, as BRU-AIM-01…10; BRU-AIM-01/02/03 match the overview's own authoritative labels |
| 15 | Overview §8 data-prerequisite deferral honoured | **PASS** — M26 FR-AIM-006 and the §8.1 data-sufficiency gate |
| 16 | Overview §9 KPI coverage | **PASS** — 16 of 16 present in the owning module |
| 17 | Overview §11 risk coverage | **PASS** — 7 of 7 addressed by a named control |
| 18 | Intra-category dependency reciprocity | **PASS** — 0 asymmetries |
| 19 | Cross-file reference resolution | **PASS** — 0 unresolved |
| 20 | Table and code-fence integrity | **PASS** — 149 tables, 0 malformed rows, all fences balanced |

---

## 2. Deliverables

| Module | File | Lines | FRs | Effort | Wave |
|---|---|---:|---:|---:|:--:|
| M62 | `M62_Data_Platform_Warehouse_and_Governance.md` | 911 | 38 | 26 PW | W4 / W8 |
| M25 | `M25_Business_Intelligence_and_Reporting.md` | 815 | 34 | 18 PW | W4 |
| M26 | `M26_AIML_Services_and_Model_Operations.md` | 993 | 42 | 34 PW | W6–W8 |
| M63 | `M63_Process_Automation_and_Workflow_Orchestration.md` | 900 | 32 | 19 PW | W3 |
| | **Total** | **3,619** | **146** | **97 PW** | |

> **Register variance.** `02-02` estimated **130 requirements** and **84 PW** across the four
> modules. Measured: **146 requirements (+12%)** and **97 PW (+15%)**. The variance is
> concentrated in the two modules that did not exist in the v2.0 draft (**M62 +4 PW**, **M63
> +3 PW**) and in **M26 +4 PW**, where the v1.0 scope predated model cards, bias testing,
> decision logging and drift monitoring. Each module records the variance in its §16.5.
> **Raised as action A-03.**

---

## 3. Findings

### F-01 · Corrected during audit · Non-English character in a state diagram

`M62` §8.1 contained a stray Cyrillic word (`типы`) in the Silver-layer annotation of the data
journey diagram, introduced during drafting.

**Action taken:** corrected to `types normalised`. **Closed.**

### F-02 · Open · Metric registry ownership conflict with `M54` and `02-05`

Three documents disagree on who owns the metric registry.

| Document | Position |
|---|---|
| `_CATEGORY_OVERVIEW.md` §3, §5 | **M62.** *"A metric is defined once, in M62's semantic layer. M25 displays it. If two dashboards disagree, the defect is in M62, not in a chart."* |
| `M54_Cost_Accounting_Budgeting_and_FPA.md` §3.2, T-15, BRU-FPA-20, §12.1, AC-25 | **M25.** *"One metric registry, owned by M25."* |
| `02-05` §5.2 | **M25** — `CD-110 cd_metric_registry` allocated to M25 |

**Position taken in these specifications: M62 owns the metric registry and the semantic layer.**
The overview states the rule explicitly and gives the reason; a metric definition editable from
a chart authoring tool is a metric with no single definition, which is the exact failure the
split exists to prevent. `CD-110` and `CD-111` are therefore reallocated to M62; `CD-112
cd_embedded_analytics` remains with M25.

**Action:** amend `M54` §3.2, T-15, BRU-FPA-20, §12.1 and AC-25 to read **M62**; amend `02-05`
§5.2. **Owner: CTO. Raised as actions A-01 and A-05.** Recorded in `M62` §18 Q-10 and `M25`
§18 Q-12.

### F-03 · Open · KPI ownership in `06-02` does not reflect the v2.1 split

| KPI | `06-02` owner | v2.1 owner | Rationale |
|---|---|---|---|
| KPI-093 Data quality test pass rate | M25 | **M62** | Data quality is a platform property, not a presentation one |
| KPI-094 Manual management reports remaining | M25 | **M25** | Unchanged — confirmed |

Flagged in `M62` §15 and `M25` §15 register notes. **Raised as action A-02.**

### F-04 · Open · **M63 reciprocity gap — the largest finding in this audit**

M63 claims to execute the approval chains, escalations, scheduled jobs and business rules of
every other module. The other modules do not, in the main, claim it back.

| Measure | Count |
|---|---:|
| Written module specifications outside Category J | 59 |
| That declare approvals or escalations in their §9 / §11 | **59** |
| That name **M63** as the executor in their §3.2 or §12.1 | **6** *(M01, M21, M28, M30, M33, M64)* |
| **Reciprocity gap** | **53 modules** |

This is a documentation gap, not a design defect — M63 did not exist when most of those
specifications were written, and the category overview §5 is explicit that *"every module
declares its need; M63 executes"*. But under the anti-overlap rule both sides of a boundary must
agree, and at present 53 specifications describe approval machinery without naming its owner.

The equivalent check on the other three modules is materially healthier: **M25 is named by 59 of
59**; **M26 by 33 of 59** (every module that consumes a model); **M62 by 27 of 59** — the
shortfall there being specifications that declare a warehouse extract to *"M25 BI"* without
naming the platform behind it.

**Action:** add an M63 delegation row to §3.2 and an M63 upstream row to §12.1 in the 53
affected specifications; add M62 alongside M25 in the 32 warehouse-extract rows that name only
M25. **Owner: CTO. Raised as actions A-06 and A-07.** Recorded in `M63` §18 Q-11.

### F-05 · Open · FR prefixes `DAT` and `BPA` are unallocated in `05-01`

M62 and M63 are new in v2.1 and have no entry in `05-01` §1.3, which remains on the 30-module
basis. These specifications allocate **FR-DAT-001…038** and **FR-BPA-001…032**. Additionally
**M26 claims FR-AIM-039…042** from its own reserved growth block (039–055), and **M25 releases
FR-BID-035…045** back to its reserved block following the carve-out of the data platform.

**Action:** register all four allocations in `05-01` §1.3a. **Owner: Programme Director. Raised
as action A-04.**

---

## 4. Audit Actions Register

| ID | Action | Target Document | Owner | Priority |
|---|---|---|---|:--:|
| **A-01** | Re-own the metric registry to **M62**: amend §3.2, T-15, BRU-FPA-20, §12.1 and AC-25 | `M54_Cost_Accounting_Budgeting_and_FPA.md` | CTO | **High** |
| **A-02** | Re-own **KPI-093 → M62**; confirm KPI-094 remains M25 | `06-02` §2.7 | CTO | **High** |
| **A-03** | Update Category J requirement count (130 → 146) and effort (84 → 97 PW) | `02-02` §2 Category J | Programme Director | **High** |
| **A-04** | Allocate FR prefixes **DAT** (001–038) and **BPA** (001–032); record M26's claim on 039–042 and M25's release of 035–045 | `05-01` §1.3a | Programme Director | **High** |
| **A-05** | Register the Category J CD block **CD-187…199** and the reallocation of **CD-110, CD-111** from M25 to M62 | `02-05` §5.2 | CTO | **High** |
| **A-06** | **Add an M63 delegation row (§3.2) and upstream row (§12.1) to the 53 specifications that declare approvals or escalations without naming M63** | 53 module specifications | CTO | **High** |
| **A-07** | Add **M62** alongside M25 in the 32 warehouse-extract rows that name only M25 | 32 module specifications | CTO | Medium |
| **A-08** | Register the 4 modules' owned entities (**74 tables**) in the entity catalogue | `05-02` | CTO | Medium |
| **A-09** | Register the API surfaces (**45 endpoints**) and domain events (**54 events**) | `05-03` | CTO | Medium |
| **A-10** | Record the 4 new module-prefix rule sets (DAT, BID, AIM, BPA — **96 rules**) and their automations (**82**) | `05-05` | CTO | Medium |
| **A-11** | Add **Data Engineer**, **Data Scientist / ML Engineer**, **Data Steward** and **CDO / Data Protection Officer** to the role register — none currently exists, and all four are load-bearing in this category | `05-04` | HR Director / CTO | **High** |

---

## 5. Custom Development Allocation (verified — no duplicates)

**New contiguous block: CD-187 … CD-199 (13 IDs).** Category G's block ends at CD-186, so the
Category J block starts cleanly at CD-187.

| Module | Reallocated from `02-05` | New | Total | Effort |
|---|---|---|---:|---:|
| M62 | **CD-110, CD-111** *(from M25)* | CD-187…190 | 6 | 26 PW |
| M25 | CD-112 *(retained)* | CD-191…193 | 4 | 18 PW |
| M26 | CD-113…118 *(retained)* | CD-194…195 | 8 | 34 PW |
| M63 | — *(new module)* | CD-196…199 | 4 | 19 PW |
| | **9 retained · 2 reallocated** | **13 new** | **22** | **97 PW** |

**Moving within Category J:** `CD-110 cd_metric_registry` and `CD-111 cd_warehouse_sync` →
**M62** (finding F-02). Both reallocations are documented in `M62` §16.2 and `M25` §16.2.

---

## 6. Programme Risks Surfaced by This Specification Set

These are new or newly quantified. They are decisions the programme must take, not defects in
the documents.

| # | Risk | Severity | Where Raised |
|---|---|:--:|---|
| **R-1** | **Category J has no staff.** `05-04` contains no data engineer, data scientist, ML engineer, data steward or CDO. Four modules totalling 97 PW and 14 production models depend on capabilities the organisation does not currently employ. This is the single largest delivery risk in the category | **Critical** | `M62` §18 Q-01, Q-02 · `M26` §18 Q-01 · action A-11 |
| **R-2** | **PDPA 2026 requires a Chief Data Officer / DPO appointment, and the role is unfilled.** M62 places S3 inclusion authorisation, re-identification approval and erasure evidence on it; M26 places training-data provenance and the automated-decision position on it | **Critical** | `M62` §18 Q-01 · `M26` §18 Q-05 |
| **R-3** | **M63 is scheduled in W3, ahead of two modules it depends on** (M21 W5 reporting lines, M27 W4 notification delivery). A degraded W3 mode is specified — matrix-only approver derivation, inbox-only task visibility — but it must be accepted and resourced, or M63 moved to W4 | **High** | `M63` §18 Q-07, §16.3 |
| **R-4** | **Two governance artefacts do not exist and are prerequisites, not deliverables**: a board-approved **delegation-of-authority matrix** (M63 cannot route an approval against an unwritten policy) and a **register of routine operational work** (without it the 85% automation target has no denominator) | **High** | `M63` §18 Q-01, Q-02, §16.4 |
| **R-5** | **The spreadsheet inventory is unknown, and KPI-094 (manual reports → zero) is measured against it.** M25's headline benefit cannot be evidenced without a complete register, and harvesting those spreadsheets is also M62's metric-definition backlog | **High** | `M25` §18 Q-01, §16.4 · `M62` §18 Q-06, §16.4 |
| **R-6** | **Nobody is named to arbitrate when a manual pack disagrees with the certified metric.** The answer is usually that the pack was wrong, which is politically difficult and needs an owner before the first parallel-run reconciliation | **High** | `M25` §18 Q-02 · `M62` §18 Q-06 |
| **R-7** | **The dispatch model's relationship to technician incentives is undecided.** If it influences pay or appraisal it becomes the most sensitive people-affecting model in the estate, requiring HR, workforce and possibly legal involvement before W6 | **High** | `M26` §18 Q-03, Q-04 |
| **R-8** | **Self-hosted generative inference is a hardware commitment, not a preference.** BRU-AIM-10 forbids external inference for customer data, which makes GPU capacity a capital decision with a lead time | **Medium** | `M26` §18 Q-02 |
| **R-9** | **Two licence questions are unresolved**: Metabase (AGPL-3) embedded into customer- and partner-facing portals, and n8n (Sustainable Use — internal business purposes only) surfacing approval tasks to corporate-portal and marketplace-seller users | **Medium** | `M25` §18 Q-05 · `M63` §18 Q-05 |
| **R-10** | **BRU-AIM-01 is unenforceable until "material customer or financial impact" is defined per consuming module.** The rule is the first line of the AI governance regime and currently has no threshold | **Medium** | `M26` §18 Q-07 |
| **R-11** | **Data residency eliminates cloud data warehousing.** PDPA 2026 and NFR-086/099 force self-hosted ClickHouse and MinIO. This is recorded because it will be re-litigated by every vendor who reads the architecture | **Medium** | `M62` §4 design position, T-15 |

---

## 7. Design Invariants Established Across the Category

Verified as consistently asserted in all four specifications.

| # | Invariant | Enforcement |
|---|---|---|
| 1 | **A metric is defined once, in M62's semantic layer. No consumer computes its own variant** | M62 BRU-DAT-01/02, T-05/T-06, AC-01 · M25 BRU-BID-01, T-01, AC-01/AC-02 |
| 2 | **Row-level security is enforced in the query engine, not the presentation tool** — dashboard, export, API and embed return identically permitted rows | M62 BRU-DAT-12, T-09, AC-11 · M25 BRU-BID-02/03, T-02/T-03, AC-03 |
| 3 | **Sensitive personal data is excluded from the analytical estate by default, not masked in it** | M62 BRU-DAT-11, T-10, AC-10 |
| 4 | **No analytical process writes into an operational system** — write-back travels as an event through M28 | M62 BRU-DAT-17, T-12, AC-19 · M26 BRU-AIM-16, T-01, AC-13 · M63 BRU-BPA-16, T-10, AC-18 |
| 5 | **M26 never acts; it returns a score and an explanation, and the consuming module decides** | M26 BRU-AIM-16, AC-13 · overview §5 |
| 6 | **A policy change never requires a code release** — M28 guarantees delivery, M63 decides what happens next | M63 BRU-BPA-02, T-03, AC-01 · overview §4 |
| 7 | **Every automation and every model declares its failure behaviour** — and the two categories differ deliberately: **M63 automations may fail closed; M26 models must fail safe** and never block a business process | M63 BRU-BPA-01, AC-02 · M26 BRU-AIM-14, T-02, AC-06 |
| 8 | **Governance artefacts gate promotion, not follow it** — model card, bias test, data-sufficiency gate, metric certification, rule simulation | M26 AC-02…AC-05 · M62 AC-15 · M63 AC-03 |
| 9 | **Everything material is logged immutably with the version of the rule or model that applied** | M62 BRU-DAT-24 · M25 BRU-BID-08 · M26 BRU-AIM-09/27, T-11 · M63 BRU-BPA-15, T-08 |
| 10 | **Effective dating throughout** — a back-dated transaction is evaluated on the definition, rule and model version in force at its own date | M62 BRU-DAT-19 · M63 BRU-BPA-06/07, T-04/T-05, AC-05 |
| 11 | **Bengali is a rendering and language requirement, not a translation task** | M25 BRU-BID-10, T-07, AC-09 · M26 FR-AIM-030, FR-AIM-032, FR-AIM-040 · M62 FR-DAT-022 |
| 12 | **Bangladesh data residency is structural** — no configuration path to foreign replication of personal data | M62 BRU-DAT-14, T-15, AC-21 · M26 BRU-AIM-10, T-13, AC-21 |
| 13 | **The M06 firewall is structural, not procedural** — M26 holds no credential or network path to the data-recovery environment | M26 BRU-AIM-03, T-17, AC-20 · reciprocal of M06 BRU-DTS-14 |

---

## 8. Overview §11 Risk Coverage

All seven category risks are addressed by a named control in the owning module.

| Overview risk | Owning module | Control |
|---|---|---|
| Two dashboards show different numbers | M62 | Single semantic layer; versioned, change-controlled definitions; consumer notification before effect — BRU-DAT-01…05, AC-01 |
| Management reverts to spreadsheets | M25 | Retirement register with parallel run and source-data retirement; performance targets; freshness indicators — FR-BID-034, §8.2, BRU-BID-16/17 |
| Models built before sufficient data exists | M26 | Data-sufficiency gate blocking promotion — FR-AIM-006, §8.1, BRU-AIM-12, AC-02 |
| Unexplainable decision affecting pay or income | M26 | Mandatory plain-language explanation, bias testing, always-available override — FR-AIM-040/042, BRU-AIM-04/07, AC-09 |
| Automation encodes a wrong rule at scale | M63 | Rules as versioned configuration; mandatory simulation and impact analysis; one-action rollback; declared failure behaviour — BRU-BPA-01/03/04/05, AC-02/AC-03 |
| Warehouse cost grows uncontrolled | M62 | Retention and downsampling from day one; per-subject-area cost measurement — FR-DAT-036/037, BRU-DAT-16/23 |
| Personal data used in analytics without basis | M62 | Default exclusion of S3 data; named time-limited authorisation with lawful basis; erasure propagation — FR-DAT-034/036, BRU-DAT-11/15, AC-10/AC-13 |

---

## 9. Benchmark Basis — Coverage Check

Every module benchmarks against the analogues named in `_CATEGORY_OVERVIEW.md` §3 and §4, plus
specialist references appropriate to its domain.

| Module | Primary external references |
|---|---|
| M62 | SAP Datasphere · Oracle Fusion Analytics Warehouse · Microsoft Fabric / OneLake · Databricks medallion architecture · Kimball dimensional modelling · Data Vault 2.0 · **dbt Semantic Layer / MetricFlow** · data contracts practice · four-pillar data observability · **OpenLineage** · Feast feature-store practice · ClickHouse |
| M25 | **Oracle OTBI** · **SAP Analytics Cloud** · Microsoft Power BI (certification and endorsement) · **Metabase 0.52+** · Grafana (boundary) · OCA `reporting-engine` / `mis-builder` · report bursting practice · single-source-of-truth practice · data storytelling |
| M26 | **MLflow** · MLOps deployment ladder (shadow → canary → champion/challenger → automated rollback) · drift practice (PSI, KS, SHAP) · **ISO/IEC 42001:2023** · **EU AI Act** (incl. Article 50 and the AI Omnibus deferral to 2 Dec 2027) · NIST AI RMF · model card practice · **RAG practice 2026** · Ollama self-hosted inference · prompt-injection defence |
| M63 | **SAP Business Workflow / Flexible Workflow** · **Oracle BPM / AME** (derived approver lists) · Dynamics 365 + Power Automate · **Camunda BPMN 2.0 + DMN** · **n8n** · saga/compensation patterns · process mining · delegation-of-authority practice · straight-through processing |

The overview §3 and §4 analogues are all represented: Oracle *Fusion Analytics Data Pipelines*
and SAP *Datasphere* and dbt+warehouse (M62); Oracle *OTBI*, SAP *Analytics Cloud* and Metabase
(M25); SAP *Business Workflow*, Oracle *BPM*, n8n and Camunda (M63).

---

## 10. Audit Method

| Check | Method |
|---|---|
| Structure, front matter, section count | Automated parse of all 4 files |
| FR / BRU / AUT / AC / T / Q identifier integrity | Automated extraction, uniqueness and gap detection, distinguishing table rows from prose cross-references |
| Declared vs measured requirement counts | Automated comparison against §1 declarations |
| CD identifier allocation and effort | Automated extraction of §16.2 tables; duplicate detection across the category and against `02-05` §5.2; per-CD effort summed against the §1 declaration |
| Layer allocation | Automated sum of §16.1 coverage percentages |
| Overview §5 boundary map | Row-by-row verification against the named owner, including the 2 rows owned outside Category J |
| **Overview §6 model portfolio** | Model-by-model verification of consumer, target and fallback against M26 §5.3–§5.6 |
| **Overview §7 governance rules** | Rule-by-rule verification against BRU-AIM-01…10, cross-checked with the overview's own `Enforced By` labels |
| Overview §9 KPIs and §11 risks | Term-by-term verification against the owning module |
| Dependency reciprocity (intra-category) | Automated comparison of every §1 *Depends on* / *Depended on by* pair |
| **Cross-category reciprocity** | Automated scan of all 59 module specifications outside Category J for delegation to M62, M25, M26 and M63 |
| Cross-file references | Automated filename resolution |
| Table and fence integrity | Automated column-count and fence-balance check across 149 tables |
| Design invariants and benchmark basis | Manual review against `02-01`, `02-05`, `05-04` and the category overview |

---

*Category J Audit Report · 1000FiX ERP System v2.0 · CONFIDENTIAL*
