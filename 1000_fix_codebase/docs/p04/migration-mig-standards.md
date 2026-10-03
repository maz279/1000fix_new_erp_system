# Migration Standards — MIG-01…MIG-08 (P04-M09)

**Binding standards for every migration** (`MG-001`, TSS §19.2). These are not
guidelines; a migration that violates any MIG rule is rejected at the control
gate, not fixed after go-live.

| # | Rule | Enforcement |
|---|---|---|
| **MIG-01** | Every migration has a **specification, control totals, mock run, and rehearsed rollback** before it runs against production | `MG-005` mock + `MG-007` rehearsal |
| **MIG-02** | **Control totals reconciled BEFORE the load is accepted** — record count, value total, checksum. Not after: before | Reconciliation gate in the ETL pipeline |
| **MIG-03** | **Every migrated record carries its legacy reference, permanently** — legacy order lookup is a live requirement (`FR-SRM-088`), not a migration convenience | `legacy_reference` field on every target model |
| **MIG-04** | **Dry run against production-sized data before every cutover** (`DoD-10`) | `migration-staging` environment at production volume |
| **MIG-05** | **Data quality assessed BEFORE migration, with the business deciding** what to cleanse, migrate as-is, or leave behind (`MIG-05` — engineering does not make that call) | DQ report per source → business sign-off |
| **MIG-06** | **Migrated personal data goes through the SAME residency service as application data** — a bulk loader can bypass a runtime ORM check; that is the compliance breach the architecture exists to prevent, at scale, on day one | `libs/py/fix_residency` is the only path to Z4, including from the ETL |
| **MIG-07** | **Rollback rehearsed, not just documented** (`DoD-16`) — the MG-007 rollback is executed in the mock, not read from a document | Rollback rehearsal record |
| **MIG-08** | **Legacy systems decommissioned only after reconciliation sign-off** — not on go-live day | Business sign-off record precedes decommission authorisation |

## Wave 1 migration scope (P04-M09-T01…T04)

| Source | Target model | ETL key | Notes |
|---|---|---|---|
| Customer master (multiple contact-data sources) | `res.partner` + `fix.party.role` | Dedup under `M64-core` golden-record rules | Party kernel multi-role design rule applies |
| Device and customer asset master | `fix.device` | Serial/IMEI uniqueness; duplicates flagged for MDM review | M17 registry |
| Branch master | `fix.branch` | 5 pilot centres + Dhaka HQ | M30 entity config |
| Employee master | `hr.employee` + `fix.party.role(employee)` | JML event emission on import | M21-core; MV-01 payoff |

## Control-total template (MIG-02)

```
source: <source system name>
extracted_at: <timestamp>
record_count: <integer>
value_total: <decimal or "N/A">
checksum: <sha256 of the extract file>

loaded_at: <timestamp>
loaded_count: <integer — must equal record_count>
rejected_count: <integer>
rejection_reasons: <list>

reconciled_by: <name>
reconciled_at: <timestamp>
approved: <yes/no>
```
