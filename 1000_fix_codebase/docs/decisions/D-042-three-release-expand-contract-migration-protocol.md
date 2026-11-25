# D-042 — Three-Release Expand/Migrate/Contract Schema Evolution Protocol
## Zero-Downtime Database Architecture Protocol for Production Releases (TSS §21.3 / PE-001)

| Metadata | Details |
|---|---|
| **Decision ID** | `D-042` |
| **Date** | 2026-10-21 (Milestone R10-M04-T06) |
| **Status** | ACCEPTED |
| **Deciders** | Chief Architect (`CA`), Lead Database Architect (`DBA`), Principal SRE |
| **Allocating authority** | TSS §21.3 · PE-001 · GV-003 Change Control · IR-002 P11-M07-T07 |
| **Target Architecture** | PostgreSQL 17 HA Cluster, Odoo 19 Kernel, Drizzle ORM Microservices |
| **Standard** | Zero-Downtime Continuous Deployment · Martin Fowler Evolutionary Database Design |

---

## 1. Context & Problem Statement

In an enterprise repair and after-sales service ecosystem handling 250,000+ monthly customers and continuous 24/7 retail front-desk ticketing, taking the primary PostgreSQL database offline for schema migrations (`ALTER TABLE ... ADD COLUMN NOT NULL`, column renames, or table drops) causes unacceptable downtime and table lock contention.

Under TSS §21.3 and PE-001, single points of failure and table-level exclusive locks (`AccessExclusiveLock`) on transactional tables (`res_partner`, `fix_work_order`, `account_move`, `stock_quant`) are prohibited.

---

## 2. Decision: The 3-Release Expand/Migrate/Contract Lifecycle

All database structural modifications across the 1000FiX estate must adhere to the formal 3-release evolutionary lifecycle:

```
┌────────────────────────────────────────────────────────────────────────┐
│                   3-RELEASE ZERO-DOWNTIME LIFECYCLE                    │
├─────────────────────┬──────────────────────────┬───────────────────────┤
│ Release N (Expand)  │ Release N+1 (Migrate)    │ Release N+2 (Contract)│
├─────────────────────┼──────────────────────────┼───────────────────────┤
│ • Add new column/   │ • Backfill historical    │ • Drop deprecated     │
│   table as NULLABLE │   data via background    │   column / table      │
│ • Application code  │   batch jobs             │ • Remove dual-writing │
│   writes to BOTH    │ • Application switches   │   code from apps      │
│   old & new columns │   reads to NEW column    │ • Schema clean and    │
│ • Reads from OLD    │ • Dual-writing continues │   compact             │
└─────────────────────┴──────────────────────────┴───────────────────────┘
```

### Phase 1: Release N — Expand
1. Add new columns or tables without locking tables (`ADD COLUMN ... NULL`, or with safe defaults).
2. Codebase dual-writes: every write mutation writes to both the legacy column and the new column.
3. Codebase reads exclusively from the legacy column.
4. If Release N is rolled back, existing code continues functioning without error because the legacy column was untouched.

### Phase 2: Release N+1 — Migrate
1. Execute asynchronous background data backfill (`tooling/scripts/mig-load.py` or Odoo migration script) to populate the new column for historical rows.
2. Verify row-count and checksum parity between old and new columns.
3. Switch application read paths to the new column. Dual-writing continues to maintain backward compatibility in case of emergency rollback.

### Phase 3: Release N+2 — Contract
1. Verify 100% of read/write traffic is utilizing the new column.
2. Stop dual-writing in application code.
3. Drop deprecated legacy column or table via a non-blocking background migration (`ALTER TABLE ... DROP COLUMN ...`).

---

## 3. Invariants & Guardrails

1. **No Destructive ALTER in Single Release**: Renaming a column or altering a column type in place is strictly blocked by CI fitness check `FF-06`.
2. **Backward & Forward Compatibility**: Version $N$ database must support Version $N-1$ and Version $N+1$ application containers concurrently during rolling updates (`GP-12`).
3. **Locking Constraints**: Foreign keys and unique constraints must be added with `NOT VALID` and validated in a subsequent transaction via `VALIDATE CONSTRAINT` to avoid table freezes.

---

## 4. Consequences & Operational Verification

- **Benefits**: Zero downtime during production rollouts; rolling blue-green and canary deployments are fully supported; automated rollbacks require zero schema reverts.
- **Verification**: Enforced by `tooling/fitness/run.py` and validated during the GP-12 build-once-promote staging drill.
