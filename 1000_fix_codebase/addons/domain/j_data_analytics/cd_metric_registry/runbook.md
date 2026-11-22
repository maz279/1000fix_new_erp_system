# Operational Runbook: 1000FiX Data Platform & Governance (cd_metric_registry)

**Document**: `addons/domain/j_data_analytics/cd_metric_registry/runbook.md`
**Standard**: DoD-11 (Per-Module Operational Runbook), AR-007 §3.1
**Module ID**: `M62` | **CD ID**: `CD-M62-01` | **Wave**: `W8`
**Category**: `Data Platform & Governance` | **Layer**: `L4 Analytics & Telemetry`
**Owner Squad**: `Data Platform & Governance`
**Version**: `19.0.0.3.0` | **License**: `LGPL-3`

---

## 1. Operational Overview & Scope

M62 is a **governance register over a data platform that does not execute yet**:
the data catalogue, lineage, data contracts, the metric registry (definitions and
their published versions), quality rules and their test evidence, incidents,
retention/cost policies and the analytical erasure register.

**No pipeline executor is connected on this estate.** Nothing in this module
moves data. A `fix.data.run` — and therefore a pipeline's `last_run_at` /
`last_success_at` — exists only when a person records and finishes a run in the
workspace. Freshness is measured from those records; cost is a projection from
the declared volumes and the policies' storage rate, **not a cloud bill**.

The one data movement tool in the repository (`services/bi-warehouse`,
PostgreSQL replica → ClickHouse) is wired to no cron, controller or DAG. Wiring
an executor is an owner decision, not a configuration task.

---

## 2. Module Topology & Dependencies

### 2.1 Upstream Dependencies (declared in the manifest)
`base`, `mail`, `hr`, `cd_entity_config` (the guarded-field mixin and DoA
tiers), `cd_event_outbox` (domain events), `cd_workflow_engine` (M63: every
governance decision routes there), `cd_service_order`, `cd_warranty_claims`,
`cd_party_master` (M33: the party master, the erasure request and the
`res.partner` unique key the "Customer Unique" rule measures).

### 2.2 Events
- **Emitted**: `data_quality.failing` (aggregate `fix.data.quality.rule`), when
  a rule's result is below its threshold. The registered consumer opens an
  incident and marks the entity degraded.
- **Consumed**: none.

---

## 3. Data Models

| Model | Table | Source file |
|---|---|---|
| `fix.data.entity` | `fix_data_entity` | `models/fix_metric_registry.py` |
| `fix.data.lineage` | `fix_data_lineage` | `models/fix_metric_registry.py` |
| `fix.data.quality.rule` | `fix_data_quality_rule` | `models/fix_metric_registry.py` |
| `fix.data.declassification.auth` | `fix_data_declassification_auth` | `models/fix_metric_registry.py` |
| `fix.data.pipeline` | `fix_data_pipeline` | `models/fix_data_platform.py` |
| `fix.data.run` | `fix_data_run` | `models/fix_data_platform.py` |
| `fix.data.contract` | `fix_data_contract` | `models/fix_data_platform.py` |
| `fix.metric.definition` | `fix_metric_definition` | `models/fix_data_platform.py` |
| `fix.metric.version` | `fix_metric_version` | `models/fix_data_platform.py` |
| `fix.metric.consumer` | `fix_metric_consumer` | `models/fix_data_platform.py` |
| `fix.data.quality.test` | `fix_data_quality_test` | `models/fix_data_platform.py` |
| `fix.data.incident` | `fix_data_incident` | `models/fix_data_platform.py` |
| `fix.data.retention.policy` | `fix_data_retention_policy` | `models/fix_data_platform.py` |
| `fix.data.purge.evidence` | `fix_data_purge_evidence` | `models/fix_data_platform.py` |
| `fix.data.source` | `fix_data_source` | `models/fix_m62_capture.py` |
| `fix.data.dimension` | `fix_data_dimension` | `models/fix_m62_capture.py` |
| `fix.glossary.term` | `fix_glossary_term` | `models/fix_m62_capture.py` |
| `fix.data.erasure` | `fix_data_erasure` | `models/fix_m62_capture.py` |

`models/fix_m62_capture.py` extends models from both other files and is
therefore imported last. `services/bi-warehouse` is NOT a dependency (it writes
no row of any of these tables).

---

## 4. Scheduled Jobs

| Job | Cadence | What it does |
|---|---|---|
| `M62: measure data quality rules` | hourly | Measures every active rule the runner can measure; records an immutable `measured=True` test row; publishes `data_quality.failing` below the threshold. A rule it cannot measure is **logged with its reason and counted as skipped** — it is never dropped in silence. |
| `M62: lapse and revert expired declassification authorisations` | daily | An approved, time-limited downgrade reverts to its original classification when it expires. |
| `M62: report records past retention (evidence only)` | weekly | Writes a disposition evidence row for records past retention. Deletes nothing. |

---

## 5. Seed-Integrity Repair (run once per estate, by hand)

Both live estates inherited seeded rows no model path can produce: metric
definitions "published" with no version, contracts "active" with no producer
signature, pipelines stamped with a last success no run produced, quality rules
"passing" that were never measured — most of them hanging off one unrelated
entity (an inventory snapshot pointing at a "Customer API Resource").

Run **as a Data Governance Officer or DoA Administrator** (a plain user is
refused):

```python
env["fix.data.entity"].action_repair_seed_residue()
```

It returns a dict of counts and logs every change. It:

1. drafts a definition that was published with no version;
2. drafts a contract that was active without the producer signature;
3. clears run stamps on a pipeline that has no recorded run;
4. moves a rule that was "passing" with a NULL `last_measured` to **Not yet
   tested** and clears the seeded result;
5. maps the entities that have one real model (`Service Orders Table →
   fix.service.order`, `Customer API Resource → res.partner`,
   `Identity Documents → fix.identity.document`), creates the registers the
   seeders never created (AR invoice ledger, Inventory snapshot, bKash
   settlement files) and re-points the seeded pipelines, contracts and quality
   rules to the entity each one names. It only re-points a row **still on the
   original hub**: a row an officer has moved is their ruling;
6. derives the retention `disposition` from a prose purge rule
   ("archive after 36 months" → archive, "…then pseudonymise" →
   pseudonymise) and gives a legacy cost row its company currency.
   **No retention period and no statutory floor is changed.**

`Order Events Stream` and `SLA Attainment KPI` keep `res_model = NULL`: they
have no single Odoo model, so no quality rule on them is measurable — the
module says so instead of pretending.

The method is **idempotent**: a second call changes nothing and returns zeros.

### 5.1 Quality rules: what is measurable

A rule is measured only when its entity maps to a model **and** it names a
check field the model has:

| Rule (seeded) | Check field | Why |
|---|---|---|
| `Orders Complete` (completeness) | none | The name states no column, and the fields that must always be filled on `fix.service.order` are model-required — a rule on one of them measures a guaranteed 100% forever. The officer chooses a column; until then the scorecard states "no check field". |
| `Customer Unique` (uniqueness) | `legacy_reference` | The party master designates exactly one key as unique per party (MIG-03 / FR-SRM-088, enforced by `_check_legacy_reference_unique`). One documented tolerated value exists (`CORP-2023-23`); if it still duplicates, the rule reports a real finding. |
| `Events Fresh` (timeliness) | none | Its entity has no model. |

Timeliness measures the share of records whose **own timestamp** (the check
field) falls inside the window — never `write_date`, which any unrelated edit
would bump.

---

## 6. Reading the Numbers

- **Measured vs manual.** A test row carries `measured`: `True` only when the
  runner measured the entity. A result a person typed is evidence but is
  labelled manual and **never counted as a measurement**.
- **The registry's six tiles** (KPI row, before the operational counters):
  - *Certified Metrics* — definitions published with a published version behind
    them. A published state with no version is not a certified metric.
  - *Quality Tests Passing* — % of the latest tests that were measured and
    passed; blank when none was ever measured.
  - *Freshness Lag* — minutes since the OLDEST last success among active
    pipelines; blank when none has ever run.
  - *Lineage Coverage* — entities with at least one lineage edge ÷ all
    entities.
  - *PII Columns Masked* — active `fix.sensitive.field` rules, read as the
    caller; blank when the account may not read the register.
  - *Warehouse Cost MTD* — Σ monthly cost of the active retention policies (a
    projection, not a cloud bill).
  A blank is honest: the value could not be measured. It is never a 0.

---

## 7. Retention Disposition

`action_purge` honours the policy's **Disposition** selection, not the prose:

| Disposition | What a disposition run does |
|---|---|
| `retain` (default) | reports eligible rows only |
| `archive` | reports eligible rows (archiving has no engine yet) |
| `pseudonymise` | reports eligible rows (pseudonymisation has no engine yet) |
| `delete` | deletes the entity's records older than the cutoff |

Every run writes an append-only `fix.data.purge.evidence` row. A legal hold
refuses the whole action. Shortening a period is an M63 request; a period below
the statutory floor is refused outright. Statutory floors are an owner
decision and are not derived from anything in this module.

---

## 8. Troubleshooting

```sql
-- The register's state (no `active` column: an entity is catalogued or not)
SELECT state, count(*) FROM fix_data_quality_rule GROUP BY state;
SELECT count(*) FROM fix_data_quality_rule WHERE check_field IS NULL;

-- Rules that cannot be measured: no model on the entity, or no check field
SELECT r.name, e.name AS entity, e.res_model, r.check_field
FROM fix_data_quality_rule r JOIN fix_data_entity e ON e.id = r.entity_id
WHERE r.active AND (e.res_model IS NULL OR r.check_field IS NULL);

-- Pipelines that never ran but carry a stamp (should be empty)
SELECT p.code, p.last_success_at FROM fix_data_pipeline p
WHERE p.last_success_at IS NOT NULL
  AND NOT EXISTS (SELECT 1 FROM fix_data_run r WHERE r.pipeline_id = p.id);

-- Contracts that claim active without the producer signature (should be empty)
SELECT dataset_code, version FROM fix_data_contract
WHERE state = 'active' AND producer_signed_by IS NULL;

-- Definitions that claim published without a published version (should be empty)
SELECT d.code FROM fix_metric_definition d
WHERE d.state = 'published'
  AND NOT EXISTS (SELECT 1 FROM fix_metric_version v
                  WHERE v.definition_id = d.id AND v.state = 'published');
```

A non-empty result above is the residue the repair in §5 removes.

---

## 9. Verification

```bash
FIX_TEST_DB=fix_test_a11_m62 python -m pytest \
  addons/domain/j_data_analytics/cd_metric_registry -q
```

The integrity suite is `tests/test_m62_integrity.py` (guards, repair, rule
states, disposition); the pack and KPI arithmetic is asserted in the portal
suite `cd_p03_portal/tests/test_a11_control_m62.py`.

---

*Last Updated: 2026-11-23 · Owner: Data Platform & Governance squad.*
