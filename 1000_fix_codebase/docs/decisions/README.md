# ADR Library (`AR-004`) — Index

Every architecture decision lives here as an Architecture Decision Record in
the strict format (**Status · Context · Options · Decision · Consequences ·
Revisit triggers**), and **each names its allocating authority** — the `DL-08`
rule: a decision that does not name its authority is a decision nobody can
revisit. The `GV-003` decision-log cross-references are maintained in
[`../p01-m02/GV-003-decision-log-entries.md`](../p01-m02/GV-003-decision-log-entries.md).

| D-nnn | Subject | Status | Authority | Date | ADR |
|---|---|---|---|---|---|
| `D-WS-001` | Windows-native workstation baseline (P02-M01 adaptation) | ACCEPTED | Product owner direction; engineering adaptation | 2026-09-30 | [`D-WS-001-windows-native-workstation-baseline.md`](D-WS-001-windows-native-workstation-baseline.md) |
| `D-013` | Split-residency data architecture | **ACCEPTED** (Option B taken, `B-02` closed) | Board, on the `DEP-31` opinion; `CA` records | 2026-10-12 | [`D-013-split-residency.md`](D-013-split-residency.md) |
| `D-025` | Odoo 19.0 baseline; W6 upgrade slot (Option A) | ACCEPTED | ARB → `CA` | 2026-10-01 | [`D-025-odoo-baseline-upgrade.md`](D-025-odoo-baseline-upgrade.md) |
| `D-026` | Portal frontend baseline: Next.js 16.2+/16.3 + Payload 3.73+ | ACCEPTED | ARB → `CA` | 2026-10-01 | [`D-026-portal-frontend-baseline.md`](D-026-portal-frontend-baseline.md) |
| `D-027` | Mobile framework: Flutter (single framework; P07 → PWA) | ACCEPTED | ARB → `CA`, with `MB` | 2026-10-01 | [`D-027-mobile-framework.md`](D-027-mobile-framework.md) |
| `D-028` | Object store: Ceph (replaces MinIO) | ACCEPTED | ARB → `CA` (taken in Phase 1 per IR-002 §0.7.3) | 2026-10-01 | [`D-028-object-store.md`](D-028-object-store.md) |
| `D-029` | PostgreSQL major version: baseline 17 | ACCEPTED | ARB → `CA` (as above) | 2026-10-01 | [`D-029-postgresql-major.md`](D-029-postgresql-major.md) |
| `D-030` | Restricted-licence register (annual review; complete enumeration) | ACCEPTED | ARB → `CA`; `SL` co-signs the gate design | 2026-10-01 | [`D-030-restricted-licence-register.md`](D-030-restricted-licence-register.md) |
| `D-031` | Redis licence currency: pin 7.2.x or Valkey | **PROPOSED** (ARB) | ARB → `CA` proposes | 2026-10-01 | [`D-031-redis-licence-currency.md`](D-031-redis-licence-currency.md) |
| `D-037` | Kafka event bus migration & Redis Streams retirement | **ACCEPTED** | ARB, Integration Lead, Platform Lead | 2026-10-18 | [`D-037-kafka-event-bus-migration.md`](D-037-kafka-event-bus-migration.md) |
| `D-038` | Odoo major-version upgrade slot execution & controlled deferral | **ACCEPTED** (Option A2) | ARB, Chief Architect (`CA`), Steering | 2026-10-18 | [`D-038-odoo20-upgrade-slot-execution.md`](D-038-odoo20-upgrade-slot-execution.md) |

## Rules this library enforces

- **`IR-06`:** no technology enters the stack without an ADR **and** a `D-nnn`
  row in `GV-003`. "It was quicker" is not a rationale.
- **`DL-08`:** the allocating authority is named in every record.
- **`AR-012` §10 (gate retro-check):** a gate added later does not retro-check
  what shipped before it — ADRs are dated, and dates are load-bearing.
- **Upstream facts are timestamped** (`RG-08`): the 2026-10-01 ADRs cite the
  first version-currency verification record
  ([`../../tooling/version-currency/evidence/verification-record-2026-10-01.md`](../../tooling/version-currency/evidence/verification-record-2026-10-01.md)),
  not the roadmap's 2026-08-19 figures.
