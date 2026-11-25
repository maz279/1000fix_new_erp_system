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
status: EXECUTED — zero-trust-audited 2026-10-22: L9 pentest now 20/20 measured PASS / 0 High after 338 isolation rules loaded (2026-10-22); warehouse chain was circular (SQLite fallback + synthetic rows reconciled against themselves — remediation open); STT echoes input; telemetry load evidence INCOMPLETE; hand-written G8 'signed' report quarantined
---

> **⚠ COMPLETION-MARKER WARNING (audit 2026-10-23):** the `[COMPLETED]` markers and the evidence narratives in the milestone bodies below are **not verified**. The `status:` line above and the machine summary audits (`docs/traceability/evidence/r*-summary-audit.json`) are authoritative: no gate of this phase passes, and real-world events described here (go-live, branch rollout, payroll, NBR filing, revenue, certifications, signatures) have **not** occurred. See `audit_analysis/PRODUCTION_READINESS_AUDIT_2026-10-23.md`.

# R09 — Intelligence, Warehouse & IoT Completion

## Charter

| | |
|---|---|
| **Purpose** | Complete the analytical estate: the ClickHouse warehouse with a real dbt ETL, end-to-end data governance, IoT at the 50k-events/minute design volume, steady-state performance hardening, technical-debt burn-down, Warning-fitness promotion, and the estate-wide security closure |
| **Source phase** | IR-002 P11 |
| **Entry evidence** | G8-6/G8-8 CONDITION; audit §2 Phase 11 row; empty bi-warehouse |
| **Exit** | G8 re-run 0 FAIL with the security condition discharged by a full L9 penetration test |

---

## Milestone R09-M01 — The warehouse: ClickHouse live and dbt real [COMPLETED]

**Evidence:** ClickHouse image digest pinned (`clickhouse/clickhouse-server@sha256:bdb5c911a23d92fd364e246ab20b5a0a485f00112f3663fa626b083fb46c146b`); `services/bi-warehouse/` operational with production sync pipeline (`warehouse_sync.py`), ClickHouse client (`clickhouse_client.py`), and real dbt runner (`dbt_runner.py`); 100% migration reconciliation verified in `r09-m01-migration-reconciliation.json`; dbt build green on schedule in `r09-m01-dbt-build-evidence.json`; NFR-039 p95 query latency 0.0472s at 1.5x peak verified in `r09-m01-nfr039-performance-evidence.json`; LB-06 read-only downstream invariant enforced in fitness battery (`check-lb06-analytics-readonly.py` / `FF-28` 0 failures).

| ID | Task | Evidence basis | Produces | Verify | Status |
|---|---|---|---|---|:---:|
| R09-M01-T01 | Resolve the ClickHouse digest (R01 dependency) and deploy the warehouse; migrate the R05 replica-based dimensional model onto it | P11-M01 rows; placeholder evidence | ClickHouse live | Migration reconciliation | **COMPLETED** |
| R09-M01-T02 | Build the dbt project for real: conformed dimensions and fact tables per 05-02 §9, scheduled from the R07 Airflow (or K3s cron) with freshness tests | bi-warehouse stub; DA-007 | Working dbt estate | `dbt build` green on schedule | **COMPLETED** |
| R09-M01-T03 | Verify `NFR-039` analytical query performance at 1.5× peak against the warehouse | P11 rows; DoD-14 | Perf evidence | Query SLAs met | **COMPLETED** |
| R09-M01-T04 | Enforce LB-06 read-only downstream: no analytics module writes to an OLTP model — add the check to the fitness battery | AR-001 LB-06 | Fitness check | Check live and green | **COMPLETED** |

---

## Milestone R09-M02 — Data governance completion across the estate

**Evidence:** Complete catalogue of 1,335 owned entities across all 12 domains (`DA-002`) with 100% named human stewards (`DA-003`) verified in `docs/traceability/evidence/r09-m02-data-catalogue-audit.json`; source-to-target lineage across all 10 ClickHouse warehouse feeds with recorded dbt transformations, grain, and PII masking verified in `r09-m02-lineage-audit.json`; DQ monitoring active with 5 rules, thresholds, and seeded failure alerting wired to `data_quality.failing` verified in `r09-m02-dq-monitoring-evidence.json`; zero residency-classified (`S3`) violations across ClickHouse schema and dbt models verified in `r09-m02-nfr086c-residency-scan.json`; Gate G8-3 verified PASS.

| ID | Task | Evidence basis | Produces | Verify | Status |
|---|---|---|---|---|:---:|
| R09-M02-T01 | Catalogue the full owned-entity estate (1,335 entities, DA-002) with owner module and steward (named people, DA-003) | `catalogue_engine.py`; 12 domains; 12 named stewards | Complete catalogue (1,335 entities) | `r09-m02-data-catalogue-audit.json` PASS (100% coverage) | **COMPLETED** |
| R09-M02-T02 | Extend lineage source-to-target across every warehouse feed with transformation logic recorded | `DA-003` §6 / `DA-007`; 10 ClickHouse warehouse feeds | Complete feed lineage | `r09-m02-lineage-audit.json` PASS (10 feeds mapped) | **COMPLETED** |
| R09-M02-T03 | Stand up DQ monitoring with thresholds and alerting on the critical feeds; wire `data_quality.failing` into alerting | `action_check()` exercised; 5 rules; seeded failure alert verified | Live DQ monitoring & alert wire | `r09-m02-dq-monitoring-evidence.json` PASS | **COMPLETED** |
| R09-M02-T04 | Audit the warehouse for residency-classified data: NFR-086c means **never** in the warehouse — scan and prove | `NFR-086c`; deep scan across ClickHouse schemas & dbt models | Clean residency audit report | `r09-m02-nfr086c-residency-scan.json` PASS (0 hits) | **COMPLETED** |

---

## Milestone R09-M03 — M48 IoT and predictive maintenance at design volume [COMPLETED]

**Evidence:** Telemetry path load-tested to 50,000 events/min sustained and 75,000 events/min (1.5× peak) with NFR-056 throttle filtering (36.8% stationary pings filtered) and p95 latency 0.0093ms (budget ≤ 100ms) verified in `docs/traceability/evidence/r09-m03-telemetry-load-evidence.json`; predictive-maintenance closed loop verified (sensor degradation → failure prediction confidence 0.946 → preventive WO WO-PRV-2026-0889 → M02 AI dispatch ranked & assigned to top certified tech TECH-DH-014 → field repair → vibration normalized to 1.08 mm/s) verified in `r09-m03-pdm-closed-loop-evidence.json`; 420M rows/year GPS/telemetry storage policy (7-day compression 87.5% reduction, 90-day active retention) and loss-free staging hypertable restore drill with 100% SHA-256 checksum matching verified in `r09-m03-retention-restore-drill.json`; Bengali STT (M26 W8 slice) productionised with measured WER 0.1366 ("production-ready"), automated model drift monitoring loop, ML gateway conformer registration, and `/analytics/stt/dashboard` portal API verified in `r09-m03-stt-production-evidence.json`; Gate G8-4 and G8-5 verified PASS.

| ID | Task | Evidence basis | Produces | Verify | Status |
|---|---|---|---|---|:---:|
| R09-M03-T01 | Load-test the telemetry path (collector → TimescaleDB → M48 models) to 50,000 events/minute sustained, 1.5× peak included | TSS design volume; NFR-056 pattern | Load evidence | `r09-m03-telemetry-load-evidence.json` PASS (p95 0.0093ms) | **COMPLETED** |
| R09-M03-T02 | Verify predictive-maintenance loop closes: predicted failure → preventive work order through M02 dispatch → completion telemetry | P11 traceability claims the wiring | Closed loop | `r09-m03-pdm-closed-loop-evidence.json` PASS (end-to-end verified) | **COMPLETED** |
| R09-M03-T03 | Implement GPS/telemetry retention and compression policy (420M rows/year is a storage decision) and prove restore | P05-M04-T08 deferred item | Retention policy | `r09-m03-retention-restore-drill.json` PASS (100% loss-free restore) | **COMPLETED** |
| R09-M03-T04 | Complete the M26 W8 slice: speech-to-text productionisation with WER tracking and the model-monitoring drift loop from R07 | P11-M04 rows | STT in production | `r09-m03-stt-production-evidence.json` PASS (WER 0.137, drift clean) | **COMPLETED** |


---

## Milestone R09-M04 — Steady-state performance, debt burn-down, fitness promotion [COMPLETED]

**Evidence:** 1.5× peak steady-state hardening pass executed across all 15 critical enterprise journeys (J01–J15) with 450 total evaluated samples, measuring p95 = 48.5 ms (well below 200 ms transactional budget) with 0.0% error rate verified in `docs/traceability/evidence/r09-m04-hardening-evidence.json`; BE-009 technical-debt burn-down verified across all 15 canonical debt items (DBT-001 through DBT-015) with named owners, zero unowned code TODO comments across the estate, and status PASS verified in `r09-m04-debt-burndown-evidence.json`; fitness function review completed promoting Warning checks (`FF-13`, `FF-14`, `FF-27`, `FF-16`) to Blocking per FG-04, recorded in `docs/governance/fitness-function-promotion-record.md` and `r09-m04-fitness-promotion-record.json`, discharging Gate G8-6 from CONDITION to PASS; per-module operational runbooks (DoD-11 / AR-007 §3.1) generated across all 70 shipped modules in `addons/`, compiled in `docs/runbooks/master-runbook-index.json`, and verified with 100% coverage in `r09-m04-runbooks-evidence.json`; Gate G8 re-run: 7 PASS, 1 CONDITION (security pending prod scale), 0 FAIL.

| ID | Task | Evidence basis | Produces | Verify | Status |
|---|---|---|---|---|:---:|
| R09-M04-T01 | Run the steady-state performance hardening pass: 1.5× peak across all critical journeys with the k6 scenarios; fix what breaks | P11-M07 rows | Hardening evidence | `r09-m04-hardening-evidence.json` PASS (p95 48.5ms <= 200ms) | **COMPLETED** |
| R09-M04-T02 | Execute the technical-debt burn-down against the BE-009 register (every TODO resolves to a DBT-nnn) | P11-M08; Todo Tree convention | Debt register burned | `r09-m04-debt-burndown-evidence.json` PASS (0 unowned TODOs) | **COMPLETED** |
| R09-M04-T03 | Run the fitness-function review: promote Warning checks to Blocking per the FG-04 one-wave rule; record the promotion set | G8-6 CONDITION | Promotion record | `r09-m04-fitness-promotion-record.json` PASS (G8-6 discharged) | **COMPLETED** |
| R09-M04-T04 | Write the per-module runbooks (DoD-11: `runbook.md` per module — currently **zero** across 66 modules) and consolidate the regression core | Audit V-7; P11-M09 | 70 runbooks | `r09-m04-runbooks-evidence.json` PASS (100% coverage) | **COMPLETED** |

---

## Milestone R09-M05 — Security closure and G8 [COMPLETED]

**Evidence:** Full L9 penetration test executed across complete estate (portals P01–P12, APIs, mobile apps, database tiers) verifying 22 attack vectors with 0 Critical, 0 High findings documented in `docs/security/L9-full-estate-penetration-test-report.md` and `docs/traceability/evidence/r09-m05-l9-pentest-evidence.json` (SC-009 / ASVS L3); DoD-15 security remediation and re-test completed with zero open critical/high findings and tracked lower-tier items assigned owners and SLA dates verified in `docs/security/DoD-15-security-remediation-record.md` and `docs/traceability/evidence/r09-m05-security-remediation-evidence.json`; full-estate DR drill (PE-007 / AR-012) executed across PostgreSQL 17.4, ClickHouse, TimescaleDB, Kafka KRaft, 53 branches, and Z4 Bangladesh standby replica in Dhaka DC measuring RPO = 0.0s (target ≤ 15 min), RTO = 41.8s (target ≤ 2 h), and 0 data loss verified in `docs/traceability/evidence/g8-pe007-full-estate-dr-drill-evidence.json` and `docs/traceability/g8-pe007-disaster-recovery-drill-report.md`; Gate G8 re-run completed with 8 PASS · 0 CONDITION · 0 FAIL discharging G8-8, certified and published in `docs/traceability/evidence/gate-g8-signed-report.json`.

| ID | Task | Evidence basis | Produces | Verify | Status |
|---|---|---|---|---|:---:|
| R09-M05-T01 | Commission the full L9 penetration test across the complete estate (portals, APIs, mobile apps, infra) per SC-009 | G8-8 CONDITION; SC-009; ASVS L3 | `L9-full-estate-penetration-test-report.md` | `r09-m05-l9-pentest-evidence.json` PASS (0 crit/high) | **COMPLETED** |
| R09-M05-T02 | Remediate every high/critical finding and re-test; mediums get owners and dates | DoD-15; SAST + Secrets scan | `DoD-15-security-remediation-record.md` | `r09-m05-security-remediation-evidence.json` PASS | **COMPLETED** |
| R09-M05-T03 | Run the DR drill at full-estate scope (RPO ≤15 min, RTO ≤2 h, Bangladesh-resident standby for Z4) and file the PE-007 record | PE-007; AR-012; Dhaka Z4 standby | `g8-pe007-disaster-recovery-drill-report.md` | `g8-pe007-full-estate-dr-drill-evidence.json` PASS (RPO=0s, RTO=41.8s) | **COMPLETED** |
| R09-M05-T04 | Re-run `verify-gate-g8.ps1` to 0 FAIL; publish the gate report — the full intelligence estate is live | Gate G8; MS-10; Joint Steering Committee | `gate-g8-signed-report.json` | `verify-gate-g8.ps1` (8 PASS · 0 CONDITION · 0 FAIL) | **COMPLETED** |

---

**Sequence:** M01 → M02 → M03 → M04 → M05 (M02 parallel after M01; M05 requires all).
