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
  files await G6 approval; the Programme Content Lead is unappointed.
status: PLANNED — evidence-derived
---

# R07 — Asset Businesses & the Event-Bus Migration

## Charter

| | |
|---|---|
| **Purpose** | Migrate the event bus from Redis Streams to the 3-node Apache Kafka cluster already specified; execute (or formally re-record the deferral of) the D-025 Odoo major-upgrade slot; bring the circular-economy businesses (rental, trade-in, data services) and the ML platform to functional depth; clear the content-approval gate |
| **Source phase** | IR-002 P09 |
| **Entry evidence** | G6-3/G6-7/G6-9 CONDITION; audit §2 Phase 9 row; asset-ml compose placeholders |
| **Exit** | G6 re-run 0 FAIL with the bus migration proven under failure injection |

---

## Milestone R07-M01 — Event-bus migration to Kafka (P09-M01 in full)

**Evidence:** G6-3 CONDITION; `docker-compose.asset-ml.yml` defines kafka-1/2/3 with `PLACEHOLDER-RESOLVE` digests; `libs/py/fix_events` has no Kafka client path.

| ID | Task | Evidence basis | Produces | Verify |
|---|---|---|---|---|
| R07-M01-T01 | Resolve the Kafka broker digests (R01 dependency) and deploy the 3-node cluster with single-node-loss survival proven | G6-3; asset-ml placeholders | Live Kafka cluster | Kill-one-broker test, 0 loss |
| R07-M01-T02 | Re-prove consumer idempotency at scale before any switch (built in Phase 3, re-verified under load) | P09-M01-T02 | Idempotency verification | Duplicate-injection test |
| R07-M01-T03 | Run the dual-write period: outbox publishes to Redis Streams **and** Kafka; consumers stay on Redis | P09-M01-T03 (EP-05 expand) | Dual-write live | Parity check N days |
| R07-M01-T04 | Migrate consumers one consumer-group at a time with per-group rollback | P09-M01-T04 | Migration plan executed | Cutover log |
| R07-M01-T05 | Build event replay-from-timestamp on Kafka — the capability that lets M51 rebuild the VAT register without M20's cooperation — then prove it under failure injection (DLQ + replay) | P09-M01-T05/T06 | Replay capability | Failure-injection evidence |
| R07-M01-T06 | Contract: retire Redis Streams as the bus (Redis stays for cache/sessions/locks); re-verify all 988 registered events against the schema registry; update affected runbooks | P09-M01-T07..T09 | Retirement record | Registry diff = 0 |

---

## Milestone R07-M02 — The D-025 Odoo major-version upgrade slot

**Evidence:** D-025 ADR exists (accepted, Odoo 19 + W6 slot) but the slot itself was never executed or formally re-recorded; G6-5 passes on "position" only.

| ID | Task | Evidence basis | Produces | Verify |
|---|---|---|---|---|
| R07-M02-T01 | Re-confirm D-025 **and** D-029 against upstream reality; sequence the Odoo and PostgreSQL upgrades deliberately (PG17 EOL month-37 arithmetic) | P09-M02-T01 | Re-confirmed positions | GV-003 update |
| R07-M02-T02 | Run the fork audit — `FORKS.yaml` must be empty or every entry planned; then the OCA v20 availability assessment across all 18 repos | P09-M02-T02/T03 | Fork audit + v20 matrix | Matrix issued |
| R07-M02-T03 | If upgrading: build the branch, dry-run against a production-sized clone on migration-staging, run the full regression estate + every fitness function, rehearse rollback, execute under change control | P09-M02-T04..T08 | Upgrade or deferral | Either outcome recorded |
| R07-M02-T04 | If deferring: record the decision and consequence (19.0 support to ~Sep 2028; upgrade lands on a 79-unit estate later) — silence is not acceptable | P09-M02-T10 | Recorded deferral | GV-003 entry |
| R07-M02-T05 | Re-verify Bengali rendering against committed reference images post-upgrade (asset-pipeline changes break font shaping silently) | P09-M02-T09 | Rendering check | Reference match |

---

## Milestone R07-M03 — M13 Rental and M14 Trade-In at depth

**Evidence:** `cd_rental_asset`/`cd_tradein` scaffolds exist; Odoo `sale_renting` not depended on; the M01 rental-intake wiring (FR-SRM-063/064) landed in R03-M05-T02; graded inventory valuation is a financial path.

| ID | Task | Evidence basis | Produces | Verify |
|---|---|---|---|---|
| R07-M03-T01 | Build rental reservation/availability on Odoo `sale_renting` + M37 rental SKUs; delivery/return through M03 logistics (journey 8) | P09-M03 rows | Rental module | Journey 8 nightly |
| R07-M03-T02 | Build damage assessment and deposit handling with 100% coverage (money path) and rental billing on M39's engine | P09-M03-T04/T05 | Damage + billing | CI financial job |
| R07-M03-T03 | Build the trade-in → wipe → refurbishment → grading → resale chain on the M31 workshop model and M37 grades; graded inventory valuation in M15 | P09-M04 rows; journey 9 | Trade-in chain | Journey 9 nightly |
| R07-M03-T04 | Build trade-in payout through M50 and the resale seam into M12 (channel lands R08) | P09-M04-T06/T07 | Payout + seam | Seam test |

---

## Milestone R07-M04 — M06 Data Services and the M26 ML platform live

**Evidence:** `cd_data_case` exists (the Z4 journey-11 module); MLflow/Ollama are placeholder compose entries; `services/ml-gateway` is 2 py; the audit verified STT's PDPA legal-basis gate as real code.

| ID | Task | Evidence basis | Produces | Verify |
|---|---|---|---|---|
| R07-M04-T01 | Complete M06: recovered-data custody chain, step-up + per-read logging on every Z4 access, purge certificates preserving the statutory record, targeted SC-002 threat-model pass (the estate's highest-value target) | P09-M05 rows | M06 complete | Journey 11 nightly; threat model |
| R07-M04-T02 | Deploy MLflow (model registry with version/lineage/rollback) and Ollama with the measured GPU decision | P09-M06-T02/T03 | ML platform live | Registry in use |
| R07-M04-T03 | Build the dispatch-scoring and demand-forecast models on operational data; wire through `ml-gateway` (one gateway, not per-model endpoints); drift detection + retraining triggers | P09-M06-T05..T09 | 2 models in production | Model governance evidence |
| R07-M04-T04 | Upgrade the M32 assistant beyond transactional intents using the M61 knowledge base (closes the Q-01 scope reduction) | P09-M06-T07 | Expanded intents | Intent suite growth |
| R07-M04-T05 | Apply the PDPA transfer rule: external LLM use (INT-036/043) only where genuinely required — customer conversation data never leaves the Company by default | P09-M06-T08 | Transfer register | DP Forum review |

---

## Milestone R07-M05 — Remaining Category H/I/K depth, content approvals, and G6

**Evidence:** G6-7 content approvals CONDITION — "32 Class A/B content files await" and the Content Lead is unappointed; `cd_talent`/`cd_hse`/`cd_grc`/`cd_knowledge`/`cd_itsm` scaffolds; the M24↔M60 pair is recorded "under review".

| ID | Task | Evidence basis | Produces | Verify |
|---|---|---|---|---|
| R07-M05-T01 | Appoint the Programme Content Lead (if not done at R01-M01-T02) and approve the 32 Class A/B files; load the 24 TR-* and 16 KB-* content sets | G6-7 CONDITION; P09-M10-T07 | Approved content | Master index 0 pending |
| R07-M05-T02 | Build M58 talent wired to the joiner event; the remaining 40 M59 HSE requirements with Labour Rules safety registers; M60 GRC resolving the M24↔M60 direction ruling | P09-M08 rows | 3 modules at depth | Ruling minuted |
| R07-M05-T03 | Build M61 knowledge/technical library (M22's moved technical content) feeding M32 and the P02 offline manuals | P09-M08-T07/T08 | Knowledge base | Offline manual sync test |
| R07-M05-T04 | Build APP-04 customer mobile at capability parity with P01 (account→feedback) with the cross-runtime conformance run (Flutter @@R04@@ realisation vs Next.js @@R03@@ realisation, per UX-001); integrate **INT-046 corporate SSO federation** (per-client SAML/OIDC through Keycloak) for P04 users | P09-M09 rows incl. T08 | Customer app + SSO | Parity + CFM-05 evidence; SSO login demo |
| R07-M05-T05 | Run the G6 gate profile (1.5× peak + DR) and re-run `verify-gate-g6.ps1` to 0 FAIL; publish | G6-9 CONDITION | Signed G6 record | G6 JSON green |

---

**Sequence:** M01 → M02 → M03 → M04 → M05 (M02 independent of M01 may parallel; M05 requires all).
