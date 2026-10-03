# Wave 1 ETL Specifications — Customer, Device, Branch, Employee (P04-M09-T01…T04)

**Every migration has a specification before it runs** (MIG-01). This document
is that specification for the four Wave 1 masters. It binds to
`docs/p04/migration-mig-standards.md` (MIG-01…MIG-08) and the profiling
instrument in `docs/p01-m07/legacy-source-profiles.md` (48-source register).

Common rules, restated once because each is a control gate:

1. **MIG-03** — every target row carries `legacy_reference` = `<SOURCE>:<key>`,
   permanently. `FR-SRM-088` legacy order lookup is a live post-cutover
   requirement, not a migration convenience.
2. **MIG-06** — classified personal data (NID/passport/TIN/health notes) is
   written via `libs/py/fix_residency` → Z4, exactly as the runtime ORM mixin
   does. **A bulk loader that writes classified values into the regional store
   directly is the compliance breach the architecture exists to prevent.**
   The ETL's write path for classified fields IS `fix_residency`; there is no
   ETL-specific bypass and FF-09's scanner covers the `services/` tree.
3. **MIG-02** — control totals (record count, value total, checksum) reconcile
   BEFORE the load is accepted; the template is in the standards doc.
4. **MIG-05** — data quality is assessed per source; the BUSINESS decides
   cleanse / migrate-as-is / leave-behind. Engineering records, never decides.
5. Bengali normalisation (`name_bn` where present) uses the same
   transliteration rules as `UX-007`; a record without a Bengali name
   migrates without one — never machine-generated.

---

## ETL-1 — Customer master → `res.partner` + `fix.party.role` (T01)

| Aspect | Specification |
|---|---|
| Sources | All customer contact stores in the register (class 7): walk-in registers, phone logs, WordPress accounts, corporate contact lists |
| Target | ONE `res.partner` per human/legal entity; roles via `fix.party.role` (the multi-role design rule — customer, seller, corporate-contact are ROLES, never duplicate partners) |
| Match key | Progressive: `phone` normalised (8801XXXXXXXX) → then `email` lowercase → then fuzzy (`fix.dedup.rule`: name edit-distance ≤ 2 + same district) |
| Dedup decision | Blocking on exact phone match (hard fail at ETL); fuzzy matches **flag for M64 steward review** (`fix.dedup.rule` action=flag), never auto-merged |
| Classified fields | NID/passport/TIN → `residency.mixin` fields on `fix.identity.document` — written through `fix_residency`, never in the partner row |
| `legacy_reference` | `CUST:<source>:<source key>` on the partner |
| Roles from history | A customer with repair history gets `role=customer` with `since=first order date`; a corporate contact gets `role=corporate_admin` scoped to the corporate partner via `fix.party.hierarchy` |
| Consent | Any source with a recorded opt-out → `fix.consent(state=withdrawn, source=legacy)`; absence of a record is NOT consent — marketing consent starts empty |
| Rejections | Records with neither phone nor email nor name → quarantine file + DQ report row; the business rules on their disposition |
| Control totals | Count per source; checksum of extract; **value_total N/A** (no monetary field) — balance check is count-only |

## ETL-2 — Device & customer asset master → `fix.device` (T02)

| Aspect | Specification |
|---|---|
| Sources | Inventory/asset lists (class 6) + device fields embedded in service-order spreadsheets (class 2) |
| Target | `fix.device` with `fix.warranty` where evidenced |
| Match key | Serial/IMEI-1 uniqueness — the registry's own SQL constraint is the gate |
| Duplicates | Same serial in two sources → **flag for MDM review** (`fix.mdm.change.request`); never silently overwritten — the device registry's history integrity depends on this |
| Orphan devices | Device with no resolvable owner → `owner_id=False` + DQ row; branch stock devices link to the branch's internal partner |
| Model resolution | Free-text model strings → `fix.device.model` via brand+model fuzzy match; unmatched → new model row flagged `provisional=True` for catalogue stewardship |
| `legacy_reference` | `DEV:<source>:<serial>` |
| Warranty | Warranty text/dates migrate only with dates parseable to `start_date`/`end_date`; "1 year warranty" prose without a purchase date does NOT become a warranty row (DQ row instead) |

## ETL-3 — Branch master → `fix.branch` (T03)

| Aspect | Specification |
|---|---|
| Sources | `P01-M07-T02` branch profiles: 5 pilot service centres + Dhaka HQ |
| Target | `fix.branch` under the operating `fix.entity`, each with `operating_unit_id` (AS-03) and a `fix.working.calendar` from the national template |
| Match key | Branch code (assigned here if the source has none: `HQ`, `PC-01`…`PC-05`) |
| Address | Parsed into `fix.bd.address` parts (BN-007 §4 order); unparseable tails → `landmark` |
| `legacy_reference` | `BR:<profile key>` |
| Control totals | Count = 6 expected exactly; any variance blocks (a missing branch at cutover is an OU hole) |

## ETL-4 — Employee master → `hr.employee` + party role (T04)

| Aspect | Specification |
|---|---|
| Sources | HR/payroll Excel class 4 — **enabled by MV-01 (payroll rates load later; the 2026 Amendment rates are NOT in the source — P01-M02 §0.7.4)** |
| Target | `hr.employee` (+ JML events per M21-core) + `fix.party.role(role=employee)` |
| Match key | NID-resolved via residency ref where present, else phone; duplicates flagged, never merged |
| Classified | NID → `fix.identity.document` through `fix_residency` (MIG-06); salary figures from payroll sources are Wave 2+ scope, not this ETL |
| `legacy_reference` | `EMP:<sheet>:<row id>` |
| JML | Hire date = `first_contract_date`; the import emits one `employee.imported` event per record through `cd_event_outbox` (AS-08) |

---

## Pipeline order and rollback (T08/T09)

```
ETL-3 branches  →  ETL-1 customers  →  ETL-2 devices  →  ETL-4 employees
   (no deps)        (needs branches      (needs owners       (needs branches
                     for scoped corp       resolved in 1)      + customers for
                     hierarchy)                                  party roles)
```

- Each ETL runs **mock first at production volume on `migration-staging`**
  (MIG-04, `MG-005`), control totals reconciled before acceptance (MIG-02).
- Rollback: each ETL is idempotent by `legacy_reference` — the rehearsed
  rollback (MIG-07) is `DELETE WHERE legacy_reference LIKE '<SOURCE>:%'` plus
  the Z4 tombstone batch through `fix_residency.erase()`, **rehearsed in the
  mock**, not read from this page.
- Cutover acceptance = business reconciliation sign-off (T10, G1-03);
  decommissioning follows sign-off only (MIG-08).
