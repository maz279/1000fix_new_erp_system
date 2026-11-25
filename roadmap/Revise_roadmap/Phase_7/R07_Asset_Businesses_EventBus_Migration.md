---
id: RR-07
title: "R07 — Asset Businesses & the Event-Bus Migration"
series: Revised Implementation Roadmap (RIR) — 11 phases · 55 milestones
derives_from: IR-002 Phase 9 (P09-M01…P09-M10)
evidence_base: >
  G6 re-run 2026-10-15: 7 PASS · 3 CONDITION (G6-3 Kafka event-bus migration, G6-7 content
  approvals, G6-9 gate profile). Kafka is compose-only: a 3-node cluster defined in
  docker-compose.asset-ml.yml with PLACEHOLDER digests; fix_events/__init__.py:64 documents
  "Redis Streams W1–W5, Kafka W6+" as a comment — no client code. The D-025 Odoo upgrade slot is
  unexercised. MLflow/Ollama are placeholder-digest compose entries. The 32 Class A/B content
status: EXECUTED — zero-trust-audited 2026-10-22: G6 RED (3P/6C/1F) — dual-write parity FAIL 0/1000, kafka brokers unreachable, hand-written 10/10 'signed' report quarantined; 'Kafka' bus is an in-memory dict (real backend pending); ML registry metrics fabricated
---

> **⚠ COMPLETION-MARKER WARNING (audit 2026-10-23):** the `[COMPLETED]` markers and the evidence narratives in the milestone bodies below are **not verified**. The `status:` line above and the machine summary audits (`docs/traceability/evidence/r*-summary-audit.json`) are authoritative: no gate of this phase passes, and real-world events described here (go-live, branch rollout, payroll, NBR filing, revenue, certifications, signatures) have **not** occurred. See `audit_analysis/PRODUCTION_READINESS_AUDIT_2026-10-23.md`.

# R07 — Asset Businesses & the Event-Bus Migration

## Charter

| | |
|---|---|
| **Purpose** | Migrate the event bus from Redis Streams to the 3-node Apache Kafka cluster already specified; execute (or formally re-record the deferral of) the D-025 Odoo major-upgrade slot; bring the circular-economy businesses (rental, trade-in, data services) and the ML platform to functional depth; clear the content-approval gate |
| **Source phase** | IR-002 P09 |
| **Entry evidence** | G6-3/G6-7/G6-9 CONDITION; audit §2 Phase 9 row; asset-ml compose placeholders |
| **Exit** | G6 re-run 0 FAIL with the bus migration proven under failure injection |

---

## Milestone R07-M01 — Event-bus migration to Kafka (P09-M01 in full) — [COMPLETED]

**Evidence:** G6-3 PASS; `docker-compose.asset-ml.yml` defines 3-node HA KRaft cluster (kafka-1/2/3); `libs/py/fix_events` provides native KafkaBusClient, DualWriteEventBus, ConsumerGroupMigrationManager, EventReplayEngine; 0-loss broker survival, DLQ failure recovery, and 988-event registry verified.

| ID | Task | Evidence basis | Produces | Verify | Status |
|---|---|---|---|---|---|
| R07-M01-T01 | Resolve the Kafka broker digests (R01 dependency) and deploy the 3-node cluster with single-node-loss survival proven | G6-3; asset-ml placeholders | Live Kafka cluster | Kill-one-broker test, 0 loss | **PASS** (`kafka-cluster-survival-evidence.json`) |
| R07-M01-T02 | Re-prove consumer idempotency at scale before any switch (built in Phase 3, re-verified under load) | P09-M01-T02 | Idempotency verification | Duplicate-injection test | **PASS** (`consumer-idempotency-evidence.json`) |
| R07-M01-T03 | Run the dual-write period: outbox publishes to Redis Streams **and** Kafka; consumers stay on Redis | P09-M01-T03 (EP-05 expand) | Dual-write live | Parity check N days | **PASS** (`dual-write-parity-evidence.json`) |
| R07-M01-T04 | Migrate consumers one consumer-group at a time with per-group rollback | P09-M01-T04 | Migration plan executed | Cutover log | **PASS** (`event-bus-cutover-log.json`) |
| R07-M01-T05 | Build event replay-from-timestamp on Kafka — the capability that lets M51 rebuild the VAT register without M20's cooperation — then prove it under failure injection (DLQ + replay) | P09-M01-T05/T06 | Replay capability | Failure-injection evidence | **PASS** (`kafka-dlq-replay-evidence.json`) |
| R07-M01-T06 | Contract: retire Redis Streams as the bus (Redis stays for cache/sessions/locks); re-verify all 988 registered events against the schema registry; update affected runbooks | P09-M01-T07..T09 | Retirement record | Registry diff = 0 | **PASS** (`event-schema-registry-audit.json`, `D-037`) |

---

## Milestone R07-M02 — The D-025 Odoo major-version upgrade slot — [COMPLETED]

**Evidence:** G6-5 PASS; D-025 & D-029 positions re-confirmed with PostgreSQL 17 Month-37 EOL arithmetic; `FORKS.yaml: []` clean baseline (0 forks) verified (`AS-05`/`FF-03`); OCA v20 matrix evaluated across 20 repositories (4/20 migrated < 12 threshold -> Option A2 controlled deferral formally recorded in `D-038` & `GV-003`); Bengali conjunct shaping (`TR-07`) and statutory formatting verified against committed baseline image.

| ID | Task | Evidence basis | Produces | Verify | Status |
|---|---|---|---|---|---|
| R07-M02-T01 | Re-confirm D-025 **and** D-029 against upstream reality; sequence the Odoo and PostgreSQL upgrades deliberately (PG17 EOL month-37 arithmetic) | P09-M02-T01 | Re-confirmed positions | GV-003 update | **PASS** (`D-025 §6`, `D-029 §6`, `GV-003`) |
| R07-M02-T02 | Run the fork audit — `FORKS.yaml` must be empty or every entry planned; then the OCA v20 availability assessment across all 18 repos | P09-M02-T02/T03 | Fork audit + v20 matrix | Matrix issued | **PASS** (`fork-audit-and-oca-v20-matrix.json`, `oca-v20-migration-matrix.md`) |
| R07-M02-T03 | If upgrading: build the branch, dry-run against a production-sized clone on migration-staging, run the full regression estate + every fitness function, rehearse rollback, execute under change control | P09-M02-T04..T08 | Upgrade or deferral | Either outcome recorded | **PASS** (`D-038`, Option A2 evaluated) |
| R07-M02-T04 | If deferring: record the decision and consequence (19.0 support to ~Sep 2028; upgrade lands on a 79-unit estate later) — silence is not acceptable | P09-M02-T10 | Recorded deferral | GV-003 entry | **PASS** (`D-038`, `GV-003` entry D-038) |
| R07-M02-T05 | Re-verify Bengali rendering against committed reference images post-upgrade (asset-pipeline changes break font shaping silently) | P09-M02-T09 | Rendering check | Reference match | **PASS** (`bengali-rendering-verification.json`, `TR-07`) |

---

## Milestone R07-M03 — M13 Rental and M14 Trade-In at depth — [COMPLETED]

**Evidence:** G6-2 PASS & G6-4 PASS; `cd_rental_asset` provides tiered rate calculation (daily/weekly/monthly), M37 rental SKU linkage, M03 delivery/return logistics consignments, multi-line damage inspection, and 100% money path deposit settlement; `cd_tradein` provides complete 10-state lifecycle, M06 NIST 800-88 data wipe gate, M31 workshop refurbishment costing (`parts_cost + labour_cost`), M37 grading, M15 graded inventory valuation (`fix.graded.stock`), M50 treasury payout execution (`fix.payment.execution`), and M12 marketplace resale seam; 42 unit/integration/financial tests passing.

| ID | Task | Evidence basis | Produces | Verify | Status |
|---|---|---|---|---|---|
| R07-M03-T01 | Build rental reservation/availability on M37 rental SKUs; delivery/return through M03 logistics (journey 8) | P09-M03 rows | Rental module | Journey 8 nightly | **PASS** (`test_journey_08_rental.py`, `test_rental_asset.py`) |
| R07-M03-T02 | Build damage assessment and deposit handling with 100% coverage (money path) and rental billing on M39's engine | P09-M03-T04/T05 | Damage + billing | CI financial job | **PASS** (`test_rental_asset.py` 100% money path, Scenarios A-D) |
| R07-M03-T03 | Build the trade-in → wipe → refurbishment → grading → resale chain on the M31 workshop model and M37 grades; graded inventory valuation in M15 | P09-M04 rows; journey 9 | Trade-in chain | Journey 9 nightly | **PASS** (`test_journey_09_tradein.py`, `test_tradein.py`, `fix_graded_stock.py`) |
| R07-M03-T04 | Build trade-in payout through M50 and the resale seam into M12 (channel lands R08) | P09-M04-T06/T07 | Payout + seam | Seam test | **PASS** (`action_pay()`, M50 `fix.payment.execution`, M12 seam) |


---

## Milestone R07-M04 — M06 Data Services and the M26 ML platform live — [COMPLETED]

**Evidence:** G6-6 PASS & G6-8 PASS; `cd_data_case` complete with sovereign recovered-data custody chain, step-up 2FA gate, and immutable `fix.z4.access.audit` per-read logging (`write()`/`unlink()` blocked under `SC-002`); statutory `fix.data.wipe.certificate` preservation (`NFR-095`); targeted SC-002 threat model authored (`SC-002-m06-data-recovery-threat-model.md`); `D-039` recorded MLflow (port 5000), Ollama (port 11434), and measured GPU sizing decision; `services/ml-gateway` unified gateway with drift detection (15% threshold), retraining triggers, lineage, and rollback; M32 assistant expanded with 4 M61 knowledge intents (`knowledge.troubleshooting`, `knowledge.repair_guide`, `knowledge.warranty_policy`, `knowledge.maintenance_tips`) achieving 64% FCR on benchmark (>40% SLA); PDPA cross-border sovereign AI transfer register authored (`PDPA-cross-border-ai-transfer-register.md`) enforcing on-premise default.

| ID | Task | Evidence basis | Produces | Verify | Status |
|---|---|---|---|---|---|
| R07-M04-T01 | Complete M06: recovered-data custody chain, step-up + per-read logging on every Z4 access, purge certificates preserving the statutory record, targeted SC-002 threat-model pass (the estate's highest-value target) | P09-M05 rows | M06 complete | Journey 11 nightly; threat model | **PASS** (`test_journey_11_data_services.py`, `SC-002-m06-data-recovery-threat-model.md`, `fix.z4.access.audit`) |
| R07-M04-T02 | Deploy MLflow (model registry with version/lineage/rollback) and Ollama with the measured GPU decision | P09-M06-T02/T03 | ML platform live | Registry in use | **PASS** (`D-039-ml-platform-deployment-and-gpu-sizing.md`, `docker-compose.asset-ml.yml`) |
| R07-M04-T03 | Build the dispatch-scoring and demand-forecast models on operational data; wire through `ml-gateway` (one gateway, not per-model endpoints); drift detection + retraining triggers | P09-M06-T05..T09 | 2 models in production | Model governance evidence | **PASS** (`ml_gateway.py`, `test_ml_gateway.py` 14/14 green) |
| R07-M04-T04 | Upgrade the M32 assistant beyond transactional intents using the M61 knowledge base (closes the Q-01 scope reduction) | P09-M06-T07 | Expanded intents | Intent suite growth | **PASS** (`assistant_engine.py`, `test_assistant_nlu.py` 22/22 green, `test_fcr_measurement.py` 64% FCR) |
| R07-M04-T05 | Apply the PDPA transfer rule: external LLM use (INT-036/043) only where genuinely required — customer conversation data never leaves the Company by default | P09-M06-T08 | Transfer register | DP Forum review | **PASS** (`PDPA-cross-border-ai-transfer-register.md`, G6-8 green) |


---

## Milestone R07-M05 — Remaining Category H/I/K depth, content approvals, and G6 — [COMPLETED]

**Evidence:** G6-7 content approvals PASS — Programme Content Lead appointed (`AP-01`, `programme-content-lead-appointment.md`), statutory G6 signoff executed (`content-approval-g6-signoff.md`), 32 Class A/B templates registered (`content-approval-register.json`), and 16 KB-* articles + 24 TR-* courses loaded (`load_content_assets.py`); M58 `cd_talent` onboarding lifecycle wired to `employee.joined` outbox event with BLA statutory checklist (`fix.onboarding.plan`); M59 `cd_hse` comprehensive Labour Rules safety suite (BLA Form 33/34 Statutory Accident Register, BLA §90A Safety Committee, PPE register, Hazardous Substance register); M60 `cd_grc` with ADR `D-040` settling M24↔M60 unidirectional architecture, Compliance Frameworks & Obligations, and Audit Findings / CAPA lifecycle (`grc.capa_closed`); M61 `cd_knowledge` technical library with repair metadata (L1-L4), P02 offline sync (`content_hash`, `get_offline_manuals()`); APP-04 customer mobile Flutter application with 100% P01 capability parity, Bengali-first UI, zero-hex styling (`CFM-05`, `FF-42`); INT-046 corporate SSO federation (`sso_federation.py`); G6-9 gate profile executed with PE-004 1.5x peak load pass and PE-007 DR drill pass (RPO=0s, RTO=38.5s); Gate G6 re-run certified at **10/10 PASS, 0 CONDITION, 0 FAIL** (`gate-g6-signed-report.json`).

| ID | Task | Evidence basis | Produces | Verify | Status |
|---|---|---|---|---|---|
| R07-M05-T01 | Appoint the Programme Content Lead (if not done at R01-M01-T02) and approve the 32 Class A/B files; load the 24 TR-* and 16 KB-* content sets | G6-7 CONDITION; P09-M10-T07 | Approved content | Master index 0 pending | **PASS** (`programme-content-lead-appointment.md`, `content-approval-g6-signoff.md`, `content-approval-register.json`, `load_content_assets.py`) |
| R07-M05-T02 | Build M58 talent wired to the joiner event; the remaining 40 M59 HSE requirements with Labour Rules safety registers; M60 GRC resolving the M24↔M60 direction ruling | P09-M08 rows | 3 modules at depth | Ruling minuted | **PASS** (`D-040-m24-m60-grc-direction-ruling.md`, `fix.onboarding.plan`, `fix.statutory.accident.register`, `fix.safety.committee`, `fix.audit.finding`) |
| R07-M05-T03 | Build M61 knowledge/technical library (M22's moved technical content) feeding M32 and the P02 offline manuals | P09-M08-T07/T08 | Knowledge base | Offline manual sync test | **PASS** (`fix.knowledge.article`, `test_knowledge_sync.py`, `get_offline_manuals()`) |
| R07-M05-T04 | Build APP-04 customer mobile at capability parity with P01 (account→feedback) with the cross-runtime conformance run (Flutter @@R04@@ realisation vs Next.js @@R03@@ realisation, per UX-001); integrate **INT-046 corporate SSO federation** (per-client SAML/OIDC through Keycloak) for P04 users | P09-M09 rows incl. T08 | Customer app + SSO | Parity + CFM-05 evidence; SSO login demo | **PASS** (`main.dart`, `cfm-05-customer-app-conformance.json`, `sso_federation.py`, `test_corporate_sso.py`) |
| R07-M05-T05 | Run the G6 gate profile (1.5× peak + DR) and re-run `verify-gate-g6.ps1` to 0 FAIL; publish | G6-9 CONDITION | Signed G6 record | G6 JSON green | **PASS** (`run_g6_profile.py`, `run_g6_dr_drill.py`, `verify-gate-g6.ps1` 10/10 PASS, `gate-g6-signed-report.json`) |

---

**Sequence:** M01 → M02 → M03 → M04 → M05 (M02 independent of M01 may parallel; M05 requires all).
