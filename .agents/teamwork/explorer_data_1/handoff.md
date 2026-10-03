# Handoff Report: Data Architecture, PDPA Split-Residency & Mobile Offline Sync Audit

**Agent Identity:** Explorer 3 (teamwork_preview_explorer)  
**Parent Agent:** `parent` (Conversation ID: `b67de09a-c664-4a41-80b7-160c11264b01`)  
**Target Document:** `roadmap/IR-002_Final_Production_Implementation_Roadmap.md` (4,361 lines)  
**Deliverable Path:** `d:\software_project_development\software_project\Software_Project_14\1000 fix\1000fix_new_erp_system\.agents\teamwork\explorer_data_1\findings_data.md`  
**Handoff Type:** Hard (Audit Investigation Complete)

---

## 1. Observation

Direct observations gathered during the deep-dive audit via exact file reads and ripgrep searches:

1. **PostgreSQL EOL Date Contradiction in IR-002:**
   - In `IR-002` Line 483: `**PostgreSQL 17 reaches end of life on 9 November 2028.** PostgreSQL supports a major version for five years; 16 was released 14 September 2023.`
   - In `IR-002` Lines 373, 489, 760, 4108, 4186: Stated as `PostgreSQL 17 reaches EOL 8 November 2029`. PostgreSQL 16 was released 14 September 2023 (EOL 9 Nov 2028); PostgreSQL 17 was released 26 September 2024 (EOL 8 Nov 2029). Line 483 accidentally conflates 16 and 17.
2. **pgvector Extension Omission:**
   - In `IR-002` Line 66 & Line 1102 (`P02-M05-T02`): Pinned image is vanilla `postgres:17.0`.
   - In `primary-doc/1000FiX_ERP_Technology_Stack_Specification.md` Lines 1940 & 2855: Mandates `Ollama embeddings + vector index (CD-224)` for M61 (Knowledge Management) and M32 (Conversational AI).
   - Upstream official `postgres:17.0` container does NOT bundle `pgvector`; executing `CREATE EXTENSION vector;` will fail without `pgvector/pgvector:0.8.0-pg17` or compiling the extension.
3. **Partitioning Strategy Omission:**
   - In `IR-002`, table partitioning is mentioned only once at Line 3106 (`P11-M03-T03`, TimescaleDB partitioning in Phase 11).
   - In `project-guide-doc/03_Data_and_Information_Architecture/DA-001_Logical_and_Physical_Data_Model_and_Database_Schema_Specification.md` Section 9 (Lines 564–578), 12 tables are mandated to be partitioned with immutable partition keys (`fix_domain_event` weekly, `fix_notification_log` monthly, `fix_audit_entry` yearly, `account_move` yearly, etc.), and rule `P-05` mandates automated create-ahead maintenance with alerting. Neither DDL creation nor maintenance automation exists in Phase 2 or Phase 3 of `IR-002`.
4. **Port Allocation Check Missing 5433:**
   - In `IR-002` Line 956 (`P02-M01-T10`): Verification command is `ss -ltnp | grep -E ':(5432|6379|9000)'`.
   - In `.agents/skills/erp-database/SKILL.md` Line 12: `Sensitive data (NID, TIN, Biometrics) MUST reside physically on the postgres-resident cluster (Port 5433)`. Port 5433 is omitted from the verification script.
5. **Unresolved CD Placeholders for PDPA:**
   - In `IR-002` Line 1575 (`P03-M09-T03`): Text reads `Build the residency service (CD-M29-nn) — the sole client of Z4`.
   - In `TSS` Line 1625 and `DA-001` Line 632: The residency service is officially designated as `CD-233`.
   - In `IR-002` Line 1581 (`P03-M09-T09`): PDPA DSR skeleton omits the official DSR orchestrator identifier `CD-248` (TSS Line 1683).
6. **Mobile Offline Local Storage & Conflict Resolution:**
   - In `IR-002` Line 1921 (`P05-M05-T03`): Names `encrypted SQLite (SQLCipher)`, but omits the Flutter ORM binding framework.
   - In `AR-010` Line 140: CRDTs are explicitly rejected (`"Rejected. CRDTs are excellent for text and sets. They cannot express 'a part may only be consumed if stock is reserved' — business invariants are not mergeable"`). The architecture adopts the Command Journal pattern (`AS-13`) with opaque high-watermark sync tokens and a 3-tier server-authoritative authority matrix.
7. **Observability Sequencing Defect & `NFR-092` Collision:**
   - In `IR-002` Lines 2177–2178 (`P06-M08-T05` and `T06`): Full OpenTelemetry stack deployment and service instrumentation are scheduled in Phase 6 (Wave 3).
   - In `PE-008_Observability_and_Monitoring_Design.md` Lines 24 and 44: Observability is marked `priority: P0 | needed_by: W1`, and `AP-02` records a critical collision where `NFR-092` represents distributed tracing in §7 and PDPA transparency notice in §6.3.
   - In `PE-008` §12.3: Seven mandatory signals are required by name (Outbox depth & age, WAL archive lag, `CD-233` latency, etc.) and are completely absent from `IR-002`.
   - In `PE-008` §11 (`RB-01` to `RB-06`): Mandates an in-country OpenTelemetry collector (`CP-03` / `BD-R`) so that Z4 logs and traces containing PII do not cross the Bangladesh border.

---

## 2. Logic Chain

1. **Technical Consistency in EOL Planning:**
   - *Observation:* Line 483 states PostgreSQL 17 reaches EOL on 9 Nov 2028, while lines 373, 489, 760, and 4186 state 8 Nov 2029.
   - *Reasoning:* PostgreSQL releases occur in September/October with 5-year support windows. Version 16 was released in Sep 2023 (EOL Nov 2028). Version 17 was released in Sep 2024 (EOL Nov 2029).
   - *Conclusion:* Line 483 contains an errant typo that creates an internal contradiction within Section 0.7.3. It must be surgically corrected to prevent downstream confusion regarding the 36-month timeline.

2. **Container Image & Semantic Search Viability:**
   - *Observation:* Baseline container is standard `postgres:17.0`; M61 and M32 require vector indexing for Ollama embeddings.
   - *Reasoning:* Upstream PostgreSQL does not include `vector` data types or HNSW index operators. Attempting `CREATE EXTENSION vector` will abort migration scripts in Phase 9.
   - *Conclusion:* Pinned image must be updated to a pgvector-enabled image (`pgvector/pgvector:0.8.0-pg17`), and index parameters (`m=16, ef_construction=64, vector_cosine_ops`) must be explicitly declared in Phase 2/3.

3. **High-Churn Scalability via Partitioning:**
   - *Observation:* `DA-001` specifies 12 partitioned tables, but `IR-002` only mentions TimescaleDB partitioning in Phase 11.
   - *Reasoning:* Odoo ORM does not generate native partitioned tables. In W1, tables like `fix_domain_event` (weekly) and `fix_notification_log` (monthly) accumulate millions of records. Without declarative partition scripts and automated create-ahead maintenance, inserts fail when new date ranges occur (`DA-001` rule `P-05`).
   - *Conclusion:* Forward-only DDL for partitioning and automated partition maintenance jobs (via pg_partman or Airflow DAG) must be added to Phase 2/3.

4. **Residency Traceability & Distributed ACID Boundaries:**
   - *Observation:* `P03-M09-T03` contains placeholder `(CD-M29-nn)`; `P03-M09-T09` omits `CD-248`; dual-writes between Odoo (5432) and `CD-233` (5433) have no explicit rollback protocol.
   - *Reasoning:* Undefined CD items violate traceability. Furthermore, cross-database joins are banned by `erp-database/SKILL.md`. If a dual-write fails mid-flight, orphan records or missing PII occurs unless a Saga pattern with compensating rollbacks and `RR-03` reconciliation is enforced.
   - *Conclusion:* Replace placeholders with `CD-233` and `CD-248`, and specify the two-phase reservation Saga pattern.

5. **Observability Readiness for Production:**
   - *Observation:* Full observability stack is scheduled in Phase 6 (Wave 3), but Phase 4 deploys the transacting core to production.
   - *Reasoning:* Running production systems for two waves without tracing, RED/USE metrics, outbox monitoring, or WAL archive lag measurement violates `DoD-05`, `DoD-14`, and `PE-008` (`needed_by: W1`).
   - *Conclusion:* Move observability deployment to Phase 3 (`P03-M01`/`P03-M03`), incorporate the seven missing signals from `PE-008` §12.3, establish the in-country collector (`CP-03`), and resolve the `NFR-092` collision by renumbering PDPA transparency to `NFR-102`.

---

## 3. Caveats

1. **Statutory Interpretation Dependency (`DEP-31` / `D-013`):**
   - The analysis notes `DA-001` §10.4 reporting that Bangladesh's February 2026 Amendment Ordinance requires a synchronised local copy rather than exclusive residency. Until legal opinion `DEP-31` is formally delivered, the architecture assumes Option A (exclusive resident store Z4) as the safe baseline.
2. **Third-Party Vendor Availability:**
   - Assessment assumes that `pgvector/pgvector:0.8.0-pg17` and `sqlcipher_flutter_libs` remain available under open-source permissive licensing (Apache-2.0 / MIT / BSD) without restricted license triggers.
3. **No Direct Code Modifications in Investigation Phase:**
   - In accordance with the Explorer role instructions, no changes have been committed directly to `IR-002_Final_Production_Implementation_Roadmap.md` in this turn. All changes are provided as exact line-by-line replacement candidates in `findings_data.md`.

---

## 4. Conclusion

The audit of `IR-002_Final_Production_Implementation_Roadmap.md` revealed 15 concrete, high-impact discrepancies across database architecture, PDPA compliance, mobile offline synchronization, and observability:
- **1 Blatant Contradiction:** PostgreSQL 17 EOL in Line 483 (confusing PG 16 with PG 17).
- **4 Architecture & Database Omissions:** Missing `pgvector` container extension, omission of 12 declarative partitioned tables and maintenance automation, PgBouncer misplacement in `auth` profile, and omitted port 5433 in port-check scripts.
- **3 PDPA & Data Governance Gaps:** Unresolved placeholders `(CD-M29-nn)` and missing `CD-248`, lack of distributed dual-write Saga transaction boundaries between regional primary and resident store, and jurisdictional clarification of Bangladesh PDPA 2026 vs "Thai PDPA".
- **2 Mobile Offline Sync Clarifications:** Specification of Drift ORM with SQLCipher (rejecting Isar/Hive) and explicit documentation of why CRDTs were rejected in favor of the Command Journaling pattern (`AS-13`).
- **5 Observability & Operational Continuity Defects:** Sequencing misalignment delaying observability to Phase 6, unresolved `NFR-092` identifier collision, omission of seven mandatory operational signals (including WAL archive lag and outbox age), absence of in-country OpenTelemetry collector architecture for Z4, and deferral of DR drills to Phase 11.

All findings have been fully documented with exact line numbers, discrepancy descriptions, and surgical text replacements in `findings_data.md`.

---

## 5. Verification Method

Independent verification of the claims in this report can be conducted using the following steps:

1. **Verify Line 483 Contradiction:**
   - Execute: `grep_search` with Query `reaches end of life on 9 November 2028` on `IR-002`.
   - Cross-check against Line 373 (`8 November 2029`) and Line 4186.
2. **Verify pgvector Omission:**
   - Execute: `grep_search` with Query `pgvector` across the entire workspace. Confirm 0 matches.
   - Inspect `IR-002` Line 1102 to confirm vanilla `postgres:17.0` is specified without vector extensions.
3. **Verify Partitioning Omission:**
   - Execute: `grep_search` with Query `partition` on `IR-002`. Confirm only 1 match (Line 3106, TimescaleDB).
   - Inspect `DA-001` Section 9 (Lines 564–578) to verify the 12 mandated tables and rule `P-05`.
4. **Verify Placeholder `(CD-M29-nn)`:**
   - Inspect `IR-002` Line 1575. Verify presence of `(CD-M29-nn)`.
   - Inspect `TSS` Line 1625 and `DA-001` Line 632 to verify `CD-233`.
5. **Verify CRDT Rejection:**
   - Inspect `project-guide-doc/02_Architecture_and_Design/AR-010_Offline_First_Synchronisation_Architecture.md` Line 140.
6. **Verify Observability Phase Misalignment:**
   - Inspect `IR-002` Lines 2177–2178 (`P06-M08-T05` and `T06`). Confirm placement in Phase 6.
   - Inspect `PE-008` Line 24. Confirm `needed_by: W1`.
