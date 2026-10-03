# D-029 — PostgreSQL major version: baseline 17

| | |
|---|---|
| **Decision ID** | `D-029` |
| **Date** | 2026-10-01 (decision taken in Phase 1 per IR-002 §0.7.3; this ADR records it, `P01-M02-T10`) |
| **Status** | ACCEPTED |
| **Deciders** | Chief Architect (`CA`) on the authority of the ARB |
| **Allocating authority** (`DL-08`) | `GV-002`; surfaced by the external verification of 2026-08-19 (`IRB-04`, Appendix I of IR-002); recorded in `AR-004`, cross-referenced from `GV-003` |
| **Closes** | `B-21` (PostgreSQL EOL inside the programme) |
| **Raise under** | `GV-003` |

## 1. Context — verified against upstream 2026-10-01

| Version | Released | End of life | Source |
|---|---|---|---|
| PostgreSQL 16 | 14 Sep 2023 | **9 Nov 2028** — month ~25 of a Q4-2026 kickoff, inside Wave 6 | postgresql.org/support/versioning |
| **PostgreSQL 17** | 26 Sep 2024 | **8 Nov 2029** — month ~37: clears the 36-month build, inside the Month-42 benefits window | postgresql.org/support/versioning; endoflife.date/postgresql |
| PostgreSQL 18 | 25 Sep 2025 | 14 Nov 2030 | endoflife.date/postgresql |

The TSS still specifies PostgreSQL 16 (§3.2, §4.1) — **superseded by this
decision**; a `CR-P01M02-01` against the TSS is raised by the traceability record
(`docs/traceability/P01-M02.md` §corrections).

## 2. Options evaluated

| Option | Assessment |
|---|---|
| Baseline 16 | EOL lands inside Wave 6 — forces a major upgrade mid-programme with no slack |
| **Baseline 17** | Clears the 36-month build window with a year of margin; full Odoo 19 + OCA v19 compatibility (the platform's stated floor) |
| Baseline 18 | Clears even the benefits review — **rejected at kickoff**: Odoo 19/OCA v19 compatibility for PG18 is unverified at the ecosystem level; adopting it means carrying that verification ourselves in Wave 1 |

## 3. Decision

1. **Baseline: PostgreSQL 17** across every environment; the `core` profile
   pins `postgres:17-alpine` by digest (`DE-06`).
2. **The PostgreSQL 18 question is re-opened at `P09-M02-T01`** (Wave 6):
   Odoo 20 + OCA v20 are the compatibility gates. PG17's EOL (month ~37) means
   a second major upgrade must land **between Wave 6 and month 37** — taking
   the same window as the Odoo upgrade is the deliberate option re-confirmed
   there, not a discovery.
3. `pg_upgrade` rehearsal is part of `P09-M02-T04` (migration dry run against
   a production-sized clone).

## 4. Consequences

- TSS correction required (16 → 17) — raised via `CR-P01M02-01`; the roadmap is
  already consistent.
- Extensions checked for PG17 at pin time: TimescaleDB 2.x (Apache-2.0
  features only, per TSS TC-023), `pgbouncer` current.
- The version-currency ritual re-checks the EOL table at every gate.

## 5. Revisit triggers

- OCA v20 repositories declaring PG18-only requirements before Wave 6 →
  re-open at that gate with the ecosystem evidence in hand.
- PG17 EOL policy change → immediate escalation.
