---
id: RR-09
title: "R09 — Intelligence, Warehouse & IoT Completion"
series: Revised Implementation Roadmap (RIR) — 11 phases · 55 milestones
derives_from: IR-002 Phase 11 (P11-M01…P11-M10)
evidence_base: >
  G8 re-run 2026-10-15: 6 PASS · 2 CONDITION (G8-6 Warning fitness functions blocking, G8-8
  zero high/critical security — "needs the full production estate"). services/bi-warehouse is a
  README + dbt stub (0 py); ClickHouse compose carries a PLACEHOLDER digest; cd_metric_registry
  delivers data governance (NFR-086c enforced in code — verified); cd_stream_registry covers M48
  IoT; telemetry-collector is EMPTY (built in R03).
status: PLANNED — evidence-derived
---

# R09 — Intelligence, Warehouse & IoT Completion

## Charter

| | |
|---|---|
| **Purpose** | Complete the analytical estate: the ClickHouse warehouse with a real dbt ETL, end-to-end data governance, IoT at the 50k-events/minute design volume, steady-state performance hardening, technical-debt burn-down, Warning-fitness promotion, and the estate-wide security closure |
| **Source phase** | IR-002 P11 |
| **Entry evidence** | G8-6/G8-8 CONDITION; audit §2 Phase 11 row; empty bi-warehouse |
| **Exit** | G8 re-run 0 FAIL with the security condition discharged by a full L9 penetration test |

---

## Milestone R09-M01 — The warehouse: ClickHouse live and dbt real

**Evidence:** `docker-compose.intelligence.yml` ClickHouse image = `PLACEHOLDER-RESOLVE-AT-FIRST-PULL`; `services/bi-warehouse/` contains only README.md + dbt/ skeleton + kpi-register.json (0 Python).

| ID | Task | Evidence basis | Produces | Verify |
|---|---|---|---|---|
| R09-M01-T01 | Resolve the ClickHouse digest (R01 dependency) and deploy the warehouse; migrate the R05 replica-based dimensional model onto it | P11-M01 rows; placeholder evidence | ClickHouse live | Migration reconciliation |
| R09-M01-T02 | Build the dbt project for real: conformed dimensions and fact tables per 05-02 §9, scheduled from the R07 Airflow (or K3s cron) with freshness tests | bi-warehouse stub; DA-007 | Working dbt estate | `dbt build` green on schedule |
| R09-M01-T03 | Verify `NFR-039` analytical query performance at 1.5× peak against the warehouse | P11 rows; DoD-14 | Perf evidence | Query SLAs met |
| R09-M01-T04 | Enforce LB-06 read-only downstream: no analytics module writes to an OLTP model — add the check to the fitness battery | AR-001 LB-06 | Fitness check | Check live and green |

---

## Milestone R09-M02 — Data governance completion across the estate

**Evidence:** `cd_metric_registry` ships `fix.data.entity` (catalogue with NFR-086c), `fix.data.lineage`, `fix.data.quality.rule` with `action_check()` firing `data_quality.failing` events — verified in the P11 traceability; coverage of the full 1,335-entity estate is ahead.

| ID | Task | Evidence basis | Produces | Verify |
|---|---|---|---|---|
| R09-M02-T01 | Catalogue the full owned-entity estate (1,335 entities, DA-002) with owner module and steward (named people, DA-003) | Governance models exist; estate coverage partial | Complete catalogue | FF-27 green at 100% |
| R09-M02-T02 | Extend lineage source-to-target across every warehouse feed with transformation logic recorded | DA-003 | Lineage complete | Lineage audit |
| R09-M02-T03 | Stand up DQ monitoring with thresholds and alerting on the critical feeds; wire `data_quality.failing` into the R04 observability alerting | `action_check()` exists unexercised | Live DQ | Alert on seeded failure |
| R09-M02-T04 | Audit the warehouse for residency-classified data: NFR-086c means **never** in the warehouse — scan and prove | NFR-086c; code comment verified | Clean audit | Scan report 0 hits |

---

## Milestone R09-M03 — M48 IoT and predictive maintenance at design volume

**Evidence:** `cd_stream_registry` (M48: device/telemetry/alert + predictive maintenance creating preventive work orders) exists; the telemetry-collector Go service was empty and is built in R03-M03-T03; the 50k/minute design volume is untested.

| ID | Task | Evidence basis | Produces | Verify |
|---|---|---|---|---|
| R09-M03-T01 | Load-test the telemetry path (collector → TimescaleDB → M48 models) to 50,000 events/minute sustained, 1.5× peak included | TSS design volume; NFR-056 pattern | Load evidence | Sustained ingest green |
| R09-M03-T02 | Verify predictive-maintenance loop closes: predicted failure → preventive work order through M02 dispatch → completion telemetry | P11 traceability claims the wiring | Closed loop | End-to-end demo |
| R09-M03-T03 | Implement GPS/telemetry retention and compression policy (420M rows/year is a storage decision) and prove restore | P05-M04-T08 deferred item | Retention policy | Restore drill |
| R09-M03-T04 | Complete the M26 W8 slice: speech-to-text productionisation with WER tracking and the model-monitoring drift loop from R07 | P11-M04 rows | STT in production | WER dashboard |

---

## Milestone R09-M04 — Steady-state performance, debt burn-down, fitness promotion

**Evidence:** G8-6 CONDITION "Warning fitness functions blocking — requires the full fitness function review (P11-M08)"; the estate carries Warning-class FFs (FF-13/14/27 promoted patterns) and the audit's V-3 SKIP set; `docs/runbooks/` is empty (DoD-11).

| ID | Task | Evidence basis | Produces | Verify |
|---|---|---|---|---|
| R09-M04-T01 | Run the steady-state performance hardening pass: 1.5× peak across all critical journeys with the k6 scenarios; fix what breaks | P11-M07 rows | Hardening evidence | All journeys under NFR |
| R09-M04-T02 | Execute the technical-debt burn-down against the BE-009 register (every TODO resolves to a DBT-nnn) | P11-M08; Todo Tree convention | Debt register burned | 0 unowned TODOs |
| R09-M04-T03 | Run the fitness-function review: promote Warning checks to Blocking per the FG-04 one-wave rule; record the promotion set | G8-6 CONDITION | Promotion record | Fitness register updated |
| R09-M04-T04 | Write the per-module runbooks (DoD-11: `runbook.md` per module — currently **zero** across 66 modules) and consolidate the regression core | Audit V-7; P11-M09 | 66 runbooks | Directory non-empty; review sign-off |

---

## Milestone R09-M05 — Security closure and G8

**Evidence:** G8-8 CONDITION "Zero high/critical security — L9 penetration test needs the full production estate"; prior gates passed security only on code-path review.

| ID | Task | Evidence basis | Produces | Verify |
|---|---|---|---|---|
| R09-M05-T01 | Commission the full L9 penetration test across the complete estate (portals, APIs, mobile apps, infra) per SC-009 | G8-8 CONDITION | Pen-test report | 0 high/critical open |
| R09-M05-T02 | Remediate every high/critical finding and re-test; mediums get owners and dates | DoD-15 | Remediation record | Re-test clean |
| R09-M05-T03 | Run the DR drill at full-estate scope (RPO ≤15 min, RTO ≤2 h, Bangladesh-resident standby for Z4) and file the PE-007 record | PE-007; environment #12 | DR evidence | Drill passes |
| R09-M05-T04 | Re-run `verify-gate-g8.ps1` to 0 FAIL; publish the gate report — the full intelligence estate is live | G8 discipline | Signed G8 record | G8 JSON green |

---

**Sequence:** M01 → M02 → M03 → M04 → M05 (M02 parallel after M01; M05 requires all).
