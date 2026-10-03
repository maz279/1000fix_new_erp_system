# Exhaustive Audit Findings: Data Architecture, PDPA & Offline Sync

**Document Audited:** `roadmap/IR-002_Final_Production_Implementation_Roadmap.md` (4,361 lines)  
**Auditor:** Explorer 3 (Data Architecture, PDPA Split-Residency & Mobile Offline Sync Auditor)  
**Evaluation Standard:** PostgreSQL 17 Architecture, Bangladesh PDPA 2026 (Law 63 of 2026), Flutter Mobile Offline-First Sync (`AR-010`), OpenTelemetry & Observability (`PE-008`), and Workspace Specifications (`primary-doc/`, `project-guide-doc/`, `.agents/skills/`).

---

## Executive Summary of Findings

| ID | Domain | Severity | IR-002 Location | Description Summary |
|---|---|:---:|---|---|
| **FIND-DATA-01** | PostgreSQL 17 Architecture | **HIGH** | Line 483 | **PostgreSQL EOL Date Contradiction**: Line 483 states PostgreSQL 17 reaches EOL on 9 November 2028 (confusing it with PG 16), contradicting Lines 373, 489, 760, 4108, and 4186 (8 November 2029). |
| **FIND-DATA-02** | PostgreSQL 17 Architecture | **HIGH** | Lines 66, 1102 | **Missing `pgvector` Extension in PostgreSQL 17 Container**: Off-the-shelf `postgres:17.0` container does not bundle `pgvector`. Semantic search embeddings for M61 (KMS) and M32 (Conversational AI) will fail at runtime without a custom image or build. |
| **FIND-DATA-03** | PostgreSQL 17 Architecture | **HIGH** | Lines 1102–1106, 3106 | **Omission of Native Partitioning Implementation**: IR-002 omits the 12 declarative partitioned tables mandated by `DA-001` §9 and lacks partition automation (`pg_partman` or automated create-ahead scripts with alerting per rule `P-05`). |
| **FIND-DATA-04** | PostgreSQL 17 Architecture | **MEDIUM** | Lines 1103, 3507 | **PgBouncer Placement & Pool Mode Misconfiguration**: PgBouncer is placed in the `auth` profile rather than `core`/database layer; no explicit specification of `pool_mode = transaction` with `server_reset_query = DISCARD ALL` and prepared statement handling for Odoo 19. |
| **FIND-DATA-05** | PostgreSQL 17 Architecture | **MEDIUM** | Line 956 | **Port Allocation Verification Omission**: `P02-M01-T10` port-check command checks ports 5432, 6379, 9000, but omits port 5433, which is the dedicated port for `postgres-resident` mandated by `erp-database/SKILL.md`. |
| **FIND-DATA-06** | PDPA Split-Residency | **HIGH** | Lines 1575, 1581 | **Unresolved Placeholder & Omitted CD Identifiers**: `P03-M09-T03` uses placeholder `(CD-M29-nn)` instead of baselined identifier `CD-233` (Residency Service); `P03-M09-T09` omits `CD-248` (DSR Orchestrator). |
| **FIND-DATA-07** | PDPA Split-Residency | **MEDIUM** | Contextual / Dispatch | **Statutory Jurisdiction Clarification**: Clarification of Bangladesh Personal Data Protection Act 2026 (Law 63 of 2026) vs "Thai PDPA" conflation; analysis of `D-013` / `DEP-31` (synchronised mirror vs exclusive residency) and NDMA compliance. |
| **FIND-DATA-08** | PDPA Split-Residency | **HIGH** | Lines 835, 1500–1581 | **Missing Distributed Transaction & ACID Boundary Specification**: Odoo writes to regional primary while PII is written to `CD-233` (port 5433); roadmap lacks explicit specification of Saga orchestration, compensating rollbacks, and reconciliation (`RR-03`) during dual-write partial failures. |
| **FIND-DATA-09** | Mobile Offline Sync | **HIGH** | Line 1921 | **Flutter Local Storage Engine Incompleteness**: `P05-M05-T03` specifies encrypted SQLite (SQLCipher) but fails to declare the Drift ORM reactive binding, migration contract, and explicit rejection rationale for Isar/Hive. |
| **FIND-DATA-10** | Mobile Offline Sync | **HIGH** | Lines 1919–1925 | **Conflict Resolution Specification Gap**: IR-002 mentions an "authority matrix" but fails to document why CRDTs were rejected (`AR-010` §3.1) and how monotonic sequence numbers, opaque sync tokens (watermarking), and server-authoritative command evaluation prevent silent data corruption. |
| **FIND-DATA-11** | Telemetry & Observability | **HIGH** | Lines 2177–2178 | **Observability Phase Misalignment**: Full observability deployment (`P06-M08-T05`) and instrumentation (`T06`) are deferred to Phase 6 (Wave 3), directly violating `PE-008` requirement `needed_by: W1`. |
| **FIND-DATA-12** | Telemetry & Observability | **HIGH** | Lines 1228, 2177–2178 | **Unresolved `NFR-092` Identifier Collision**: IR-002 cites `NFR-092` as distributed tracing without resolving the critical audit finding `AP-02` in `PE-008` (collision with PDPA transparency notice in `05-06` §6.3, which requires renumbering PDPA to `NFR-102`). |
| **FIND-DATA-13** | Telemetry & Observability | **HIGH** | Phase 2, 3, 6 | **Omission of Seven Specified Critical Telemetry Signals**: IR-002 completely omits the seven mandatory operational signals defined in `PE-008` §12.3 (Outbox depth & age, WAL archive lag, `CD-233` latency, etc.). |
| **FIND-DATA-14** | Telemetry & Observability | **MEDIUM** | Lines 1573–1575 | **Missing In-Country Telemetry Architecture for Resident Store**: IR-002 fails to specify the in-country OpenTelemetry collector (`CP-03` / `BD-R`) required by `PE-008` §11 (`RB-01` to `RB-06`) to prevent telemetry payloads containing PII from crossing borders. |
| **FIND-DATA-15** | Disaster Recovery | **MEDIUM** | Lines 1328, 3179 | **Disaster Recovery Drill Postponement**: DR drill (`P11-M07-T08`, RPO <= 15m, RTO <= 2h) is scheduled only in Phase 11 (Wave 8), leaving Waves 1–7 production without verified recovery drills. |

---

## Detailed Audit Findings & Remediation

---

### FIND-DATA-01: PostgreSQL 17 Major Version End-of-Life (EOL) Date Contradiction

- **Target File:** `roadmap/IR-002_Final_Production_Implementation_Roadmap.md`
- **Location:** Line 483 (Section 0.7.3, subsection `D-029`)
- **Severity:** HIGH (Technical Accuracy & Roadmap Currency)

#### Observation
Line 483 reads:
```markdown
483: **PostgreSQL 17 reaches end of life on 9 November 2028.** PostgreSQL supports a major version for
484: five years; 16 was released 14 September 2023. On a Q4-2026 kickoff, **9 Nov 2028 is roughly month
485: 25 — inside Wave 6**, the same wave that already holds the Odoo major-version upgrade slot.
```

In contrast, other sections of IR-002 state:
- Line 373: `| **B-21** | **(RESOLVED) PostgreSQL 17 reaches EOL 8 November 2029 — inside the programme's operational life.** No source document plans for it. D-029 required | §0.7.3 · P09-M02 |`
- Line 489: `records PostgreSQL as "supported to Nov 2029", which is **PostgreSQL 17's** date, not 16's.`
- Line 494: `| **Baseline 17** (EOL 8 Nov 2029) | Buys a year; still inside the Month 42 window |`
- Line 760: `Verified 2026-08-19: ... PostgreSQL 17 reaches EOL 8 Nov 2029, inside the programme`
- Line 4108: `PostgreSQL 17 reaches EOL 8 Nov 2029, inside the programme (D-029, B-21)`
- Line 4186: `PostgreSQL 17 was released 26 September 2024 and reaches EOL on 8 November 2029. The five-year support policy is fixed and published. November 2029 is PostgreSQL 17's date, not 16's — the alignment audit shifted the row by one version`

#### Root Cause & Discrepancy Analysis
Line 483 accidentally conflated PostgreSQL 16 and PostgreSQL 17:
- **PostgreSQL 16**: Released 14 September 2023, reaches EOL on **9 November 2028**.
- **PostgreSQL 17**: Released 26 September 2024, reaches EOL on **8 November 2029**.
The opening sentence of Line 483 mistakenly substituted the name "PostgreSQL 17" into the sentence describing PostgreSQL 16's EOL date ("9 November 2028").

#### Surgical Remediation Recommendation
Update Line 483 to clearly delineate the two versions:
```markdown
**PostgreSQL 16 reaches end of life on 9 November 2028, while PostgreSQL 17 reaches end of life on 8 November 2029.** PostgreSQL supports a major version for five years; 16 was released 14 September 2023, and 17 was released 26 September 2024. On a Q4-2026 kickoff, 9 Nov 2028 is roughly month 25 — inside Wave 6 (the Odoo major upgrade slot), whereas PostgreSQL 17's EOL on 8 November 2029 falls at Month 36 (tail end of Wave 9).
```

---

### FIND-DATA-02: Missing `pgvector` Extension in PostgreSQL 17 Container Specification

- **Target File:** `roadmap/IR-002_Final_Production_Implementation_Roadmap.md`
- **Location:** Lines 66, 967, 1102 (`P02-M05-T02`), 2764–2766 (`P09-M06`), 2855
- **Cross-Reference:** `primary-doc/1000FiX_ERP_Technology_Stack_Specification.md` Lines 1940, 2764, 2855
- **Severity:** HIGH (Runtime Architecture Defect)

#### Observation
1. In `IR-002` Line 66:
   `The database runs as a pinned container (postgres:17.0, digest-pinned), not as a host install`
2. In `IR-002` Line 1102 (`P02-M05-T02`):
   `Define the core profile: PostgreSQL 17, Redis 7, the object store chosen by D-028, Mailpit — ~2 GB, the default`
3. In `1000FiX_ERP_Technology_Stack_Specification.md`:
   - Line 1940: `M61 Knowledge Management & Technical Library ... Ollama (semantic search), PostgreSQL FTS ... CD-223…224`
   - Line 2855: `Knowledge semantic search | Ollama embeddings + vector index (CD-224) | W6 |`
4. The term `pgvector` does not appear anywhere in `IR-002` or `primary-doc`.

#### Root Cause & Discrepancy Analysis
Official upstream Docker images (`postgres:17.0` or `postgres:17-alpine`) do **not** include the `pgvector` C extension compiled or installed. When M61 (Knowledge Management) and M32 (Conversational AI / RAG virtual assistant) execute `CREATE EXTENSION vector;` for storing and indexing Ollama-generated vector embeddings (768 or 1536 dimensions), PostgreSQL will throw `ERROR: extension "vector" is not available`.

#### Surgical Remediation Recommendation
1. Update `IR-002` Line 66 and Line 1102 (`P02-M05-T02`) to mandate a digest-pinned image containing `pgvector` (e.g. `pgvector/pgvector:0.8.0-pg17` or custom internal Dockerfile based on `postgres:17-bookworm` with `postgresql-17-pgvector` installed).
2. Add explicit configuration parameters for pgvector indexing in Phase 2 / Phase 9:
   - Index type: HNSW (`CREATE INDEX ON fix_knowledge_article USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64);`)
   - Operator class: `vector_cosine_ops` (`<=>`) for cosine similarity.
   - Resource tuning: `maintenance_work_mem = 2GB` during index builds.

---

### FIND-DATA-03: Omission of PostgreSQL 17 Native Declarative Partitioning & Maintenance Automation

- **Target File:** `roadmap/IR-002_Final_Production_Implementation_Roadmap.md`
- **Location:** Line 3106 (`P11-M03-T03`), Line 1106 (`P02-M05-T06`), Line 1460 (`P03-M03-T02`)
- **Cross-Reference:** `project-guide-doc/03_Data_and_Information_Architecture/DA-001_Logical_and_Physical_Data_Model_and_Database_Schema_Specification.md` Section 9 (Lines 557–603)
- **Severity:** HIGH (Data Scalability & Operational Integrity)

#### Observation
In `IR-002`, table partitioning is mentioned exactly once across 4,361 lines:
`Line 3106: | P11-M03-T03 | Extend TimescaleDB partitioning and compression for telemetry volume | M48 · TSS §21.1 | Extended time-series store | 8 vCPU / 32 GB / 4 TB with compression | DE | T02 |`

In contrast, `DA-001` §9.1 explicitly mandates **12 partitioned tables with named immutable partition keys**:
1. `fix_service_order` (RANGE by `create_date`, Yearly from Year 3)
2. `fix_work_order` (RANGE by `create_date`, Yearly from Year 3)
3. `account_move` (RANGE by `date`, Yearly from Year 2)
4. `account_move_line` (RANGE by `date`, Yearly from Year 2)
5. `fix_notification_log` (RANGE by `create_date`, Monthly from W1)
6. `fix_api_usage_log` (RANGE by `create_date`, Monthly from W1)
7. `fix_audit_entry` (RANGE by `occurred_at`, Yearly from W1)
8. `fix_domain_event` (RANGE by `occurred_at`, Weekly from W1)
9. `fix_call_record` (RANGE by `create_date`, Monthly from W4)
10. `fix_location_ping` (TimescaleDB hypertable by `time`, partition by `technician_id`, W2)
11. `fix_telemetry_point` (TimescaleDB hypertable by `time`, partition by `asset_id`, W8)
12. `fix_metric_series` (TimescaleDB hypertable by `time`, W5)

Furthermore, `DA-001` rule `P-05` states:
`Partition maintenance (create-ahead, detach, drop) is automated with alerting. A missing future partition is an insert failure at midnight on 1 January.`

#### Root Cause & Discrepancy Analysis
`IR-002` failed to translate the 12-table partitioning mandate and rule `P-05` from `DA-001` into Phase 2 / Phase 3 engineering tasks. Because Odoo ORM does not natively manage PostgreSQL table partitioning (`DA-001` rule `O-03`), partitioning must be applied via forward-only database migration DDL. Without automated create-ahead maintenance (e.g. `pg_partman` or scheduled Airflow maintenance DAG), writes to tables like `fix_domain_event` or `fix_notification_log` will fail when new time intervals arrive.

#### Surgical Remediation Recommendation
1. Insert explicit task in `P02-M05` or `P03-M03` for declarative partitioning DDL and partition maintenance automation:
   - For high-churn tables starting W1 (`fix_domain_event` weekly, `fix_notification_log` monthly, `fix_audit_entry` yearly, `fix_api_usage_log` monthly).
   - Implement `tooling/scripts/partition-maintenance.sh` or an Apache Airflow DAG (`DAG-DB-PARTITION-MAINT`) scheduled daily to create partitions 30 days ahead and alert if lookahead partition is absent (`P-05`).
   - Implement `DM-2` partition drop / detach for data retention expiration (`DA-006`).

---

### FIND-DATA-04: PgBouncer Placement, Pool Mode & Prepared Statements Configuration

- **Target File:** `roadmap/IR-002_Final_Production_Implementation_Roadmap.md`
- **Location:** Line 1103 (`P02-M05-T03`), Line 3507
- **Cross-Reference:** `primary-doc/1000FiX_ERP_Technology_Stack_Specification.md` Lines 679, 2718, 4223
- **Severity:** MEDIUM (Architecture & Concurrency Tuning)

#### Observation
`IR-002` Line 1103 specifies:
`| P02-M05-T03 | Define auth (+ Keycloak 26, PgBouncer, ~3.5 GB) and integration (+ Kong, Apache Airflow, Novu, ~5 GB) | BE-001 §5.2 | 2 profiles | auth for cd_rbac_ext, SSO, roles, record rules. integration for M28, webhooks, orchestration, notifications | DE | T02 |`
Line 3507: `# make up PROFILE=auth # + Keycloak, PgBouncer (~3.5 GB)`

#### Root Cause & Discrepancy Analysis
1. **Profile Placement**: PgBouncer is a database proxy/connection pooler, not an authentication service. Placing PgBouncer in the `auth` profile means running `make up` on the default `core` profile connects Odoo directly to PostgreSQL (port 5432) without connection pooling. Developers and CI running on `core` will never test PgBouncer connection semantics.
2. **Transaction Pooling vs Session Pooling with Odoo**: TSS Line 2718 mandates: `PgBouncer transaction pooling | All application connections | 1,000 connections against 800+ concurrent users`.
   However, Odoo 19 uses cursors, advisory locks (`pg_advisory_lock`), `LISTEN/NOTIFY`, and temporary tables. Under `pool_mode = transaction`, without `server_reset_query = DISCARD ALL`, transaction pooling causes connection state leakage across Odoo workers. Furthermore, in PostgreSQL 17 / PgBouncer 1.21+, prepared statements across transaction pools require `max_prepared_statements = 250` or Odoo disabling named prepared statements.

#### Surgical Remediation Recommendation
1. Move PgBouncer into the `db` or `core` compose profile, or establish a dedicated `db-pool` service running on port 6432.
2. Document in `infra/compose/docker-compose.yml` and `infra/pgbouncer/pgbouncer.ini`:
   ```ini
   [pgbouncer]
   pool_mode = transaction
   max_client_conn = 1000
   default_pool_size = 50
   reserve_pool_size = 10
   server_reset_query = DISCARD ALL
   server_reset_query_always = 1
   max_prepared_statements = 250
   ```

---

### FIND-DATA-05: Missing Port 5433 for `postgres-resident` in Workstation Port Verification

- **Target File:** `roadmap/IR-002_Final_Production_Implementation_Roadmap.md`
- **Location:** Line 956 (`P02-M01-T10`)
- **Cross-Reference:** `erp-database/SKILL.md` Line 12; `erp-architect/SKILL.md` Line 14
- **Severity:** MEDIUM (Environment Setup & Verification)

#### Observation
`P02-M01-T10` reads:
```markdown
956: | `P02-M01-T10` | Verify no host PostgreSQL, Redis or Ceph Object Storage is running — **nothing but Odoo and the language toolchains lives on the host** | `BE-001` `DE-01` | Clean port map | `ss -ltnp \| grep -E ':(5432\|6379\|9000)'` returns nothing. A host PostgreSQL causes `port is already allocated` and silent version drift | `DE` | T06 |
```

#### Root Cause & Discrepancy Analysis
`erp-database/SKILL.md` Cognitive Framework #1 explicitly dictates:
`Sensitive data (NID, TIN, Biometrics) MUST reside physically on the postgres-resident cluster (Port 5433).`
If a developer or CI runner has a local service running on port 5433, or when local residency testing containers bind 5433, port conflicts will occur. Line 956 only filters for `5432|6379|9000`, omitting `5433`.

#### Surgical Remediation Recommendation
Update Line 956 to include port 5433:
`ss -ltnp | grep -E ':(5432|5433|6379|9000)'`

---

### FIND-DATA-06: Unresolved CD Placeholders & Omitted Identifiers for PDPA Compliance Services

- **Target File:** `roadmap/IR-002_Final_Production_Implementation_Roadmap.md`
- **Location:** Line 1575 (`P03-M09-T03`), Line 1581 (`P03-M09-T09`)
- **Cross-Reference:** `primary-doc/1000FiX_ERP_Technology_Stack_Specification.md` Lines 1625, 1974; `project-guide-doc/05_Security_Privacy_and_Compliance/SC-007_Data_Residency_and_Cross_Border_Transfer_Design.md` §4, §5.2
- **Severity:** HIGH (Traceability & Implementation Ambiguity)

#### Observation
In `IR-002`:
- Line 1575 (`P03-M09-T03`):
  `| P03-M09-T03 | Build the residency service (CD-M29-nn) — the sole client of Z4 | TSS §14.4 · SC-007 · BE-004 libs/py/fix_residency | Residency service + fix_residency client library | FF-09: fix_residency is the only client. Any other code path reaching Z4 fails the build | SL | T02 |`
- Line 1581 (`P03-M09-T09`):
  `| P03-M09-T09 | Build the PDPA data-subject-request skeleton: identity verification, regional assembly, resident-field request, portable machine-readable export | TSS §3.6.4 · M33 consent registry | DSR export path | The erasure saga lands with M33/M29 completion; the export path lands here | SL | T03, P03-M05-T07 |`

#### Root Cause & Discrepancy Analysis
1. `(CD-M29-nn)` in `P03-M09-T03` is an unpopulated placeholder. The formal, baselined custom development identifier across `TSS` (Line 1625), `DA-001` (Line 632), and `SC-007` (Line 87) is **`CD-233`** (`Residency service`, Python/FastAPI).
2. `P03-M09-T09` omits the formal custom development identifier for the DSR Orchestrator, which is baselined in `TSS` Line 1683 and Line 1974 as **`CD-248`** (`DSR orchestrator`).

#### Surgical Remediation Recommendation
- In Line 1575 (`P03-M09-T03`), replace `(CD-M29-nn)` with **`CD-233`**.
- In Line 1581 (`P03-M09-T09`), add **`CD-248`** to the task description and `Produces` column.

---

### FIND-DATA-07: Statutory Basis & Regulatory Alignment: Bangladesh PDPA 2026 vs "Thai PDPA"

- **Target File:** `roadmap/IR-002_Final_Production_Implementation_Roadmap.md`
- **Location:** Line 203, Lines 415–427 (§0.7.1), Line 751 (`P01-M02-T01`), Line 835 (`P01-M06-T09`)
- **Cross-Reference:** `primary-doc/1000FiX_ERP_Technology_Stack_Specification.md` Line 4261; `project-guide-doc/03_Data_and_Information_Architecture/DA-001_Logical_and_Physical_Data_Model_and_Database_Schema_Specification.md` §10.4
- **Severity:** MEDIUM (Regulatory Clarity & Risk Governance)

#### Observation
The audit prompt references "Thai PDPA". In `IR-002`:
- Line 203: `PDPA 2026 enforcement activates ~13 May 2027, inside Phase 7`
- Line 377: `penalties to BDT 50 lakh`
- Line 4261 of TSS: `PDPA 2026 | Bangladesh Personal Data Protection Act 2026 (Law 63 of 2026)`
- `DA-001` §10.4: `Personal Data Protection (Amendment) Ordinance, 2026 (Ordinance No. 23 of 2026), promulgated 5 February 2026`

#### Root Cause & Discrepancy Analysis
1. **Jurisdiction Grounding**: 1000FiX ERP is governed under the **Bangladesh Personal Data Protection Act 2026 (Law 63 of 2026)**, overseen by the National Data Management Authority (NDMA), with statutory roles including the Chief Data Officer (CDO) and statutory penalties up to BDT 50 lakh. Any external reference to "Thai PDPA" (Thailand B.E. 2562) is a jurisdictional conflation.
2. **Statutory Obligation Model (`DEP-31` / `D-013`)**: As discovered in `DA-001` §10.4, the February 2026 Amendment Ordinance clarified that the statutory localization mandate is for a **synchronised real-time local copy within Bangladesh** for restricted personal data and critical infrastructure, rather than exclusive physical isolation. IR-002 correctly registers `D-013` (Options A, B, C) in §0.7.1, but needs explicit confirmation that until `DEP-31` resolves, Option A (exclusive resident store Z4 via `CD-233`) remains the active implementation baseline.
3. **Cross-Border Transfer Prohibition for AI**: Section 14.3 of TSS and `NFR-099` forbid exporting customer interaction data outside Bangladesh, which is the exact architectural reason why conversational AI and RAG inference use self-hosted Ollama 0.5+ (`TC-036`) rather than commercial US/EU SaaS LLM endpoints (`TD-06`).

#### Surgical Remediation Recommendation
Add an explicit footnote or clarifying clause in §0.7.1 affirming that the governing statute is the **Bangladesh Personal Data Protection Act 2026 (Law 63 of 2026)** and its 2026 Amendment Ordinance, and that cross-border transfer controls (`NFR-099`) strictly prohibit unencrypted transit or offshore SaaS LLM forwarding.

---

### FIND-DATA-08: Missing Distributed Transaction Boundaries & ACID Saga Orchestration

- **Target File:** `roadmap/IR-002_Final_Production_Implementation_Roadmap.md`
- **Location:** Line 835 (`P01-M06-T09`), Lines 1500–1581 (`P03-M05`, `P03-M09`)
- **Cross-Reference:** `erp-database/SKILL.md` Anti-Patterns; `DA-001` §10.2 rules `RS-01`–`RS-06`; `TSS` §14.4
- **Severity:** HIGH (Data Integrity & Distributed ACID Boundaries)

#### Observation
`erp-database/SKILL.md` establishes:
`NEVER allow cross-database joins at the SQL level. Enforce proxy models in the Odoo application layer.`
In `DA-001` §10.2:
- Regional primary (`Z3`, port 5432) holds `fix_identity_document` with `resident_key uuid`.
- Bangladesh-resident store (`Z4`, port 5433) holds `resident_identity_value` (`resident_key uuid PK`, `value_ciphertext bytea`).
- Communication is strictly via HTTP REST to `CD-233` (Residency Service).

`IR-002` Line 835 recognizes: `It is a saga, not a DELETE` for the erasure path. However, for write paths (customer registration, KYC ingestion, employee onboarding), `IR-002` does not define the distributed transaction failure boundary.

#### Root Cause & Discrepancy Analysis
When creating a customer with an NID:
1. Odoo starts a PostgreSQL transaction on `erp_main` (port 5432).
2. The `ResidentDataHandler` client (`libs/py/fix_residency`) calls `CD-233` via HTTP POST to persist ciphertext in `postgres-resident` (port 5433).
3. If `CD-233` succeeds but the local Odoo transaction rolls back (e.g. unique constraint violation on email), an orphaned ciphertext record remains in `Z4`.
4. Conversely, if Odoo commits but `CD-233` times out, `fix_identity_document` has a dangling `resident_key` with no resident payload.
Traditional 2PC (Two-Phase Commit) between Odoo and FastAPI is antipattern-prone and causes distributed lock contention. The architecture requires a **Saga pattern with compensating actions** or a **two-phase reservation token** combined with the `RR-03` reconciliation worker.

#### Surgical Remediation Recommendation
Add an explicit task in `P03-M09` (e.g. `P03-M09-T11` or updating `T04`):
- Specify the **Two-Phase Reservation & Outbox Saga** for resident writes:
  1. Generate `resident_key = uuid4()`.
  2. Write local record in `PENDING_RESIDENCY` state within Odoo ACID transaction.
  3. Emit outbox event `residency.write_requested`.
  4. Outbox relay calls `CD-233`; upon 201 Created confirmation, transition state to `ACTIVE`.
  5. If `CD-233` permanently fails, trigger compensating rollback or tombstone.
  6. Reconcile daily via scheduled job `RR-03`.

---

### FIND-DATA-09: Mobile Local Storage Architecture: Drift ORM & Rejection of Isar/Hive

- **Target File:** `roadmap/IR-002_Final_Production_Implementation_Roadmap.md`
- **Location:** Line 1921 (`P05-M05-T03`), Line 989 (`P02-M02-T03`)
- **Cross-Reference:** `primary-doc/1000FiX_ERP_Technology_Stack_Specification.md` Line 2116, Line 3341; `project-guide-doc/02_Architecture_and_Design/AR-010_Offline_First_Synchronisation_Architecture.md` §4.1
- **Severity:** HIGH (Mobile Architecture & Local Data Persistence)

#### Observation
`IR-002` Line 1921 states:
`| P05-M05-T03 | Implement the command journal — append-only, in encrypted SQLite (SQLCipher), keyed from device credentials plus a server-issued key, wiped on remote revocation | AR-010 §3, §4.1 | Local store | Commands, not records. The journal is the only local truth; the read cache is never authoritative | MB | T02 |`

#### Root Cause & Discrepancy Analysis
1. `P05-M05-T03` names `encrypted SQLite (SQLCipher)`, but does not specify the Dart/Flutter ORM layer. In Flutter development, using raw `sqflite_sqlcipher` without a type-safe abstraction leads to schema maintenance errors.
2. Across mobile ecosystems, developers frequently attempt to substitute NoSQL stores like Isar or Hive. However, Isar had abandonment periods and lacks FIPS-compliant SQLCipher encryption. `Drift` (formerly Moor) with `sqlcipher_flutter_libs` is the approved stack choice because it provides compile-time query verification, reactive streams, schema migrations, and full SQLCipher encryption.

#### Surgical Remediation Recommendation
Refine Line 1921 (`P05-M05-T03`) to read:
`Implement the command journal — append-only, in encrypted SQLite (SQLCipher) using Drift ORM with sqlcipher_flutter_libs; keyed from device credentials plus server-issued key, wiped on remote revocation. Reject Isar/Hive (lacks certified SQLCipher encryption).`

---

### FIND-DATA-10: Conflict Resolution Architecture: Rejection of CRDTs & Adoption of Command Journaling

- **Target File:** `roadmap/IR-002_Final_Production_Implementation_Roadmap.md`
- **Location:** Lines 1919–1925 (`P05-M05-T01` to `T07`)
- **Cross-Reference:** `project-guide-doc/02_Architecture_and_Design/AR-010_Offline_First_Synchronisation_Architecture.md` Section 3 (Lines 131–147) and Section 5 (Lines 269–320)
- **Severity:** HIGH (Distributed Consistency & Business Invariant Enforcement)

#### Observation
`IR-002` Line 1925 specifies:
`| P05-M05-T07 | Implement conflict detection and the authority matrix — server-authoritative resolution | AR-010 §5 | Conflict engine | Outcomes: apply · reject · apply-with-conflict | BE | T06 |`
However, neither `IR-002` nor its summary explains the mathematical and architectural mechanism governing conflict resolution.

#### Root Cause & Discrepancy Analysis
As established in `AR-010` §3.1:
- **Record Sync (Last-Write-Wins / LWW)**: Rejected because concurrent edits silently destroy data (e.g. technician notes overwritten by dispatcher reassignment).
- **Diff Sync / CRDTs (Conflict-Free Replicated Data Types)**: Explicitly **REJECTED** in `AR-010` Line 140:
  *"CRDTs are excellent for text and sets. They cannot express 'a part may only be consumed if stock is reserved' — business invariants are not mergeable."*
- **Command Journaling (`AS-13`)**: Adopted. The mobile device logs *intents* (`work_order.consume_part`) rather than state mutations.
- **Conflict Evaluation Protocol**:
  1. Opaque sync tokens (`sync_token`) serve as high-watermark boundaries.
  2. Commands contain `base_version` (aggregate version when command was issued).
  3. Server checks if `base_version` matches current aggregate. If older, it intersects the change-set with the command's affected domain.
  4. If disjoint: auto-apply. If overlapping: apply server authority matrix (Tier 1: auto-merge non-conflicting, Tier 2: reject invariant breaches, Tier 3: human variance escalation for financial/stock variances).

#### Surgical Remediation Recommendation
Update `P05-M05-T07` in `IR-002` to explicitly specify:
- Rejection of CRDTs in favor of Command Journaling (`AS-13`).
- Inclusion of `base_version` optimistic locking and domain-intersection conflict detection.
- Implementation of the 3-tier resolution matrix (auto-apply, reject, human variance escalation).

---

### FIND-DATA-11: Premature Deferral of Full Observability Stack to Phase 6 (Wave 3)

- **Target File:** `roadmap/IR-002_Final_Production_Implementation_Roadmap.md`
- **Location:** Lines 2177–2178 (`P06-M08-T05` and `T06`), Line 1228 (`P02-M08-T09`)
- **Cross-Reference:** `project-guide-doc/10_Infrastructure_DevOps_and_Environments/PE-008_Observability_and_Monitoring_Design.md` Lines 24, 68–79
- **Severity:** HIGH (Operational Visibility & Delivery Sequencing)

#### Observation
In `IR-002`:
- Line 1228 (`P02-M08-T09`):
  `Stand up the local observability profile — OpenTelemetry, Prometheus, Loki, Tempo, Grafana — and wire a single correlation id across every hop` (Phase 2, Local).
- Line 2177 (`P06-M08-T05`):
  `Deploy the full observability stack — OpenTelemetry -> Prometheus + Loki + Tempo -> Grafana | TSS §17, §20.2 W3 · PE-008` (Phase 6 / Wave 3!).
- Line 2178 (`P06-M08-T06`):
  `Instrument every service and module with OpenTelemetry traces, metrics and structured logs ... Retrofitting instrumentation is far more expensive than adding it` (Phase 6 / Wave 3!).

In `PE-008`:
- Line 23–24: `priority: P0 | needed_by: W1`

#### Root Cause & Discrepancy Analysis
`PE-008` states that the observability stack is **needed by Wave 1 (Phase 3 & 4)**. Phase 4 deploys the transacting service core (M01, M04, M17, M33) into live staging and production. Deferring the deployment of OpenTelemetry, Prometheus, and Grafana to Phase 6 (Wave 3) means that Phases 3, 4, and 5 run in shared environments (`dev`, `sit`, `uat`, `staging`, `prod`) completely blind, violating `DoD-05` and `NFR-092`. Furthermore, task `P06-M08-T06` notes that "Retrofitting instrumentation is far more expensive than adding it", yet the roadmap forces exactly this retrofit by delaying module instrumentation to Phase 6.

#### Surgical Remediation Recommendation
1. Move `P06-M08-T05` (Deploy full observability stack) into **Phase 3 (Wave 1 Kernel, `P03-M01` or `P03-M03`)**.
2. Require that every module delivered in Phase 3, 4, and 5 includes OpenTelemetry tracing and RED/USE metrics as part of its Phase-specific DoD (`AS-15`), rather than retrofitting in Phase 6.

---

### FIND-DATA-12: Unresolved `NFR-092` Identifier Collision in Architecture Standards & Tracing

- **Target File:** `roadmap/IR-002_Final_Production_Implementation_Roadmap.md`
- **Location:** Line 1228 (`P02-M08-T09`), Line 2177 (`P06-M08-T05`), Line 2178 (`P06-M08-T06`)
- **Cross-Reference:** `project-guide-doc/10_Infrastructure_DevOps_and_Environments/PE-008_Observability_and_Monitoring_Design.md` Lines 44, 550–554
- **Severity:** HIGH (Requirements Traceability & Standards Collision)

#### Observation
`IR-002` repeatedly cites `NFR-092` as the requirement for distributed tracing and single correlation ID across every hop:
- Line 1228: `PE-008 · TSS §17 · NFR-092`
- Line 2177: `A single correlation id across every hop (NFR-092)`
- Line 2178: `PE-008 · NFR-092`

However, `PE-008` Finding #2 and §10.3 (Lines 44, 550–554) document:
`AP-02 (critical): NFR-092 means distributed tracing in 05-06 §7 and a PDPA transparency notice in 05-06 §6.3. ... renumber the PDPA block to NFR-102…NFR-104 ... Recorded as still open at 2026-08-19.`

#### Root Cause & Discrepancy Analysis
`05-06_NonFunctional_Requirements_and_Standards.md` duplicated `NFR-092`:
- In §6.3 (Privacy): `NFR-092` = PDPA Transparency Notice.
- In §7.0 (Platform/Ops): `NFR-092` = Distributed Tracing & W3C Trace Context.
`IR-002` cites `NFR-092` for distributed tracing without acknowledging or recording the renumbering decision mandated by `AP-02`.

#### Surgical Remediation Recommendation
1. In Section 0.7 (or Appendix I / §0.3.1), document the resolution of `AP-02`: affirm that `NFR-092` is retained exclusively for Distributed Tracing (W3C Trace Context + `correlation_id`), and the PDPA transparency notice requirement is officially renumbered to **`NFR-102`**.
2. Update all cross-references in `P01-M01` and `P03-M05` to point to `NFR-102`.

---

### FIND-DATA-13: Omission of Seven Specified Operational Telemetry Signals

- **Target File:** `roadmap/IR-002_Final_Production_Implementation_Roadmap.md`
- **Location:** Phases 2, 3, 4, 6
- **Cross-Reference:** `project-guide-doc/10_Infrastructure_DevOps_and_Environments/PE-008_Observability_and_Monitoring_Design.md` §12.3 (Lines 618–632)
- **Severity:** HIGH (Production Reliability & SRE Telemetry)

#### Observation
`PE-008` §12.3 explicitly catalogs:
`PE-008-F-03. Seven signals are required by name in existing documents and instrumented in none.`
1. **Outbox depth and age** (`AR-009` §5.4 — "Age is the leading indicator; depth alone hides a stuck partition")
2. **Scheduled job success, failure, and duration** (`OPS-05` — 60 business automations)
3. **`CD-233` latency** (`PE-001` Q-07 — critical path of every T5 read)
4. **WAL archive lag** (`PE-007` `FF-155` — the objective RPO measurement for `NFR-007`)
5. **Telemetry loss / dropped spans** (`CP-05` — observability pipeline health)
6. **`dr` digest parity** (`PE-004` `FF-134` — standby running identical container digest)
7. **Event delivery latency** (`NFR-043` — event bus SLA)

None of these seven signals are named or instrumented anywhere in `IR-002`.

#### Root Cause & Discrepancy Analysis
The roadmap outlines general tasks ("Instrument every service..."), but leaves out the seven specific telemetry gauges that were singled out as major specification omissions across the estate. For example, without instrumenting **WAL archive lag**, compliance with `NFR-007` (RPO <= 15 minutes) cannot be proven. Without **outbox age**, an event bus failure on a low-volume partition will remain undetected.

#### Surgical Remediation Recommendation
Add an explicit task to Phase 3 (`P03-M03` or `P03-M08`) and Phase 4:
`Implement Prometheus exporters and Grafana alerts for PE-008 §12.3 named signals: (1) outbox depth and age, (2) automated cron job outcome, (3) CD-233 residency proxy p95 latency, (4) PostgreSQL WAL archive lag gauge, (5) OTel dropped spans gauge, (6) DR container image digest parity check, and (7) end-to-end event transit latency.`

---

### FIND-DATA-14: Missing In-Country OpenTelemetry Architecture for Resident Store (Z4)

- **Target File:** `roadmap/IR-002_Final_Production_Implementation_Roadmap.md`
- **Location:** Line 1573 (`P03-M09-T01`), Line 2177 (`P06-M08-T05`)
- **Cross-Reference:** `project-guide-doc/10_Infrastructure_DevOps_and_Environments/PE-008_Observability_and_Monitoring_Design.md` §11 (Lines 557–590)
- **Severity:** MEDIUM (Regulatory Compliance & Telemetry Privacy)

#### Observation
`IR-002` sets up an observability profile and traces across services, but does not define how telemetry is handled at the Z4 residency boundary.

In `PE-008` §11:
- `RB-01`: `BD-R runs its own collector (CP-03) and its own metric, log and trace stores`
- `RB-02`: `Z4 logs and traces do not leave Bangladesh (FF-171)`
- `RB-03`: `Metrics may cross — aggregate counters and latencies carry no personal data`
- `RB-04`: `correlation_id and traceparent cross (CR-06) — they are opaque identifiers, not personal data — so a journey can be followed across the boundary without the content crossing it`
- `RB-05`: `A regional operator investigating a Z4-involved journey sees the shape and timing of the CD-233 call, and not its content`

#### Root Cause & Discrepancy Analysis
If all OpenTelemetry agents forward spans and logs to a single regional collector, any debug log, SQL trace, or span attribute emitted by `CD-233` or `postgres-resident` containing classified PII (e.g. NID query parameters) would be exported offshore, constituting a severe breach of `PDPA 2026` / `NFR-099` and violating fitness function `FF-171`.

#### Surgical Remediation Recommendation
Update `P03-M09-T02` and `P03-M09-T05` in `IR-002` to incorporate `PE-008` rules `RB-01` to `RB-06`:
- Deploy an isolated OpenTelemetry collector (`CP-03`) inside Bangladesh (`BD-R`).
- Configure collector filters to terminate Z4 trace spans and logs locally, exporting only aggregated metrics and scrubbed W3C `traceparent` metadata to the regional Grafana/Tempo cluster.

---

### FIND-DATA-15: Disaster Recovery Drill Delayed to Phase 11 (Wave 8)

- **Target File:** `roadmap/IR-002_Final_Production_Implementation_Roadmap.md`
- **Location:** Line 1328, Line 3179 (`P11-M07-T08`)
- **Cross-Reference:** `primary-doc/1000FiX_ERP_Technology_Stack_Specification.md` Line 730; `project-guide-doc/10_Infrastructure_DevOps_and_Environments/PE-007_Backup_and_Disaster_Recovery_Specification.md`
- **Severity:** MEDIUM (Disaster Recovery & Operational Continuity)

#### Observation
- In `IR-002` Line 1328, environment 12 is defined as:
  `| 12 | dr | Warm standby, RPO <= 15 min, RTO <= 2 h | Streaming replica | Yes, Bangladesh-resident standby |`
- However, the first scheduled execution of the DR drill appears at Line 3179:
  `| P11-M07-T08 | Run the DR drill — RPO <= 15 min, RTO <= 2 h — and record it | NFR-007 · PE-007 · FF-98 | DR drill record | Twice yearly. This is one of them | DE | T07 |`
  Phase 11 is **Wave 8 (Month 28–32)** of a 36-month programme.

#### Root Cause & Discrepancy Analysis
`PE-007` mandates that DR drills occur **twice yearly** starting from the first production release. Phase 4 / Gate `G1` puts the foundation and service core into production (Month 4). If the first DR drill is not executed until Phase 11 (Month 28), production operates for two years without proving that the streaming replica on the Bangladesh standby can achieve RTO <= 2 hours and RPO <= 15 minutes upon primary DC failure.

#### Surgical Remediation Recommendation
1. Add an initial DR rehearsal task in **Phase 4 (`P04-M10` Gate `G1`)** as a mandatory production readiness gate condition.
2. Schedule recurring DR drill milestones in **Phase 6 (`P06-M09`)** and **Phase 8 (`P08-M09`)** to fulfill the "twice yearly" requirement prior to the Phase 11 milestone.

---

## Summary Matrix of Concrete Textual Remediations for IR-002

| Finding ID | Target Line / Section in IR-002 | Current Defective Text | Proposed Surgical Replacement Text |
|---|---|---|---|
| **FIND-DATA-01** | Line 483 (§0.7.3) | `**PostgreSQL 17 reaches end of life on 9 November 2028.** PostgreSQL supports a major version for five years; 16 was released 14 September 2023.` | `**PostgreSQL 16 reaches end of life on 9 November 2028, while PostgreSQL 17 reaches end of life on 8 November 2029.** PostgreSQL supports a major version for five years; 16 was released 14 September 2023, and 17 was released 26 September 2024.` |
| **FIND-DATA-02** | Line 1102 (`P02-M05-T02`) | `PostgreSQL 17, Redis 7, the object store chosen by D-028, Mailpit` | `PostgreSQL 17 with pgvector extension (pgvector/pgvector:0.8.0-pg17 digest-pinned), Redis 7, the object store chosen by D-028, Mailpit` |
| **FIND-DATA-03** | Line 1460 (`P03-M03-T02`) | Add partition maintenance mandate | `Build cd_event_outbox — transactional outbox, fix.domain.event partitioned weekly by occurred_at (DA-001 §9.1), plus partition create-ahead automation with alerting (P-05)` |
| **FIND-DATA-04** | Line 1103 (`P02-M05-T03`) | `Define auth (+ Keycloak 26, PgBouncer, ~3.5 GB)...` | `Define auth (+ Keycloak 26, ~3 GB)...; move PgBouncer into db layer on port 6432 configured with pool_mode=transaction, server_reset_query=DISCARD ALL, and max_prepared_statements=250` |
| **FIND-DATA-05** | Line 956 (`P02-M01-T10`) | `grep -E ':(5432\|6379\|9000)'` | `grep -E ':(5432\|5433\|6379\|9000)'` |
| **FIND-DATA-06** | Line 1575 (`P03-M09-T03`) | `Build the residency service (CD-M29-nn)...` | `Build the residency service CD-233 (Python/FastAPI)...` |
| **FIND-DATA-06** | Line 1581 (`P03-M09-T09`) | `Build the PDPA data-subject-request skeleton...` | `Build the PDPA data-subject-request skeleton via CD-248 (DSR Orchestrator)...` |
| **FIND-DATA-08** | Line 1576 (`P03-M09-T04`) | Add Saga boundary | `Implement write-time field-level residency classification (NFR-086a) and two-phase reservation Saga with RR-03 reconciliation` |
| **FIND-DATA-09** | Line 1921 (`P05-M05-T03`) | `encrypted SQLite (SQLCipher)` | `encrypted SQLite (SQLCipher) via Drift ORM with sqlcipher_flutter_libs (rejecting Isar/Hive)` |
| **FIND-DATA-10** | Line 1925 (`P05-M05-T07`) | `Implement conflict detection and the authority matrix` | `Implement conflict detection and the authority matrix (AR-010 §5) using command journaling (AS-13, rejecting CRDTs) and opaque sync tokens` |
| **FIND-DATA-11** | Line 1417 (`P03-M01`) | Add W1 Observability task | `P03-M01-T11: Deploy initial OpenTelemetry, Prometheus and Grafana stack for Wave 1 environments per PE-008 needed_by: W1 mandate` |
| **FIND-DATA-12** | Line 1228 (`P02-M08-T09`) | `NFR-092` | `NFR-092 (Distributed Tracing; noting PDPA transparency renumbered to NFR-102 per PE-008 AP-02)` |
| **FIND-DATA-13** | Line 2178 (`P06-M08-T06`) | Add specific signal list | `Instrument every service and module with PE-008 §12.3 named signals: outbox depth & age, WAL archive lag, CD-233 latency, and job failure gauges` |
| **FIND-DATA-14** | Line 1574 (`P03-M09-T02`) | Add in-country telemetry | `Configure Z4 network isolation and in-country OTel collector (CP-03) per PE-008 rules RB-01…RB-06 (FF-171)` |
| **FIND-DATA-15** | Line 1791 (`P04-M09-T09`) | Add Phase 4 DR Drill | `P04-M10-T11: Execute initial live DR failover rehearsal (RPO <= 15m, RTO <= 2h) before Gate G1 sign-off` |

---
