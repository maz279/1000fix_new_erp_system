# Legacy Reference Survival & Live Lookup Proof (FR-SRM-088 / MIG-03)

## Task R11-M02-T02 Verification Record

- **Standard**: `MIG-03` (*Permanent legacy reference on every migrated record*) & `FR-SRM-088` (*Live legacy lookup*)
- **Executed**: 2026-10-22T10:21:49Z against 127.0.0.1:5433/fix_migration
- **Verdict (computed)**: `INCOMPLETE`
- **Resolution**: 124 / 124 lookups resolved (100.0%)
- **Lookup latency (measured)**: avg 0.958 ms, p95 1.291 ms, max 2.033 ms (target < 50.0 ms) — `PASS`
- **Production lookup after retirement**: `UNMEASURED` — lookup after legacy retirement on the production database, at production volume, cannot be observed from this workstation (DE-11 local-only endpoints; DE-12 no production data on a workstation)

---

### Domains

| Domain Model | Table | Rows with legacy ref | Lookups | Resolved | Max ms | Status |
|---|---|---:|---:|---:|---:|:---:|
| `fix.service.order` | `fix_service_order` | 0 | 0 | 0 | n/a | `INCOMPLETE` |
| `fix.device` | `fix_device` | 49 | 49 | 49 | 1.439 | `PASS` |
| `res.partner` | `res_partner` | 69 | 49 | 49 | 2.033 | `PASS` |
| `hr.employee` | `hr_employee` | 20 | 20 | 20 | 1.496 | `PASS` |
| `fix.branch` | `fix_branch` | 6 | 6 | 6 | 1.04 | `PASS` |

Checks not passed:

- `fix.service.order.coverage` — UNMEASURED: no committed extract carries legacy references for this domain, so no migrated record can be looked up

Legacy-reference survival is not established by this record (verdict `INCOMPLETE`).
