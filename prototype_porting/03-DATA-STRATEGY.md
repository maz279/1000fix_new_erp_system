# Data Strategy — real data, test data, and the elimination of fabrications

Mandate wording: *"must have same data in the database (real data, test data), removing
all the dummy data, fabricated data, hard-coded data — exactly a real 100% deployable
software."* This document makes that enforceable.

## 1. The three data classes (never mixed — DE-12)

| Class | What it is | Where it may exist | How it enters |
|---|---|---|---|
| **REAL** | Production records: customers, devices, orders, invoices, payroll | `prod` (and `migration-staging` during rehearsal) only | MIG-standard migration (control totals, dry runs, reconciliation sign-off) or live traffic. **Never on a dev workstation, never masked-down** |
| **TEST** | The deterministic seed (`db/seeds/seed.py`, seed `1000fix`) — synthetic but *statutorily valid* (13-digit BINs, correct VAT rates, real constraint-passing values), idempotent double-run | `dev`, `test`, `staging` databases | `tasks.ps1 -Target seed` |
| **FORBIDDEN** | `demo_data.js`-style arrays, PRNG values generated at render time, hard-coded KPI numbers, sample names, canned statuses, mock lists inside app code | Nowhere in production artifacts. Test fixtures only under `**/tests/**`, `**/stories/**`, `db/seeds/**` | — |

## 2. What "same data in the database" means for every ported screen

A screen is correctly ported when:

1. Every grid column is produced by an API response field (or a QWeb/OWL `read_group`),
   never by a client-side generator.
2. Every KPI card reads an aggregate endpoint — no literals, no `Math.random`, no
   `if (demo)`.
3. Every status pill maps a backend state to the token status set (MD-027).
4. Money is BDT-carried from the backend (AS-10); the client formats via BN-007, never
   computes.
5. In seed mode the screen shows seeded rows; in production mode it shows migrated real
   rows — **the same code path**, different database. No `DEMO_MODE` branches in
   components (a single build-time env flag may only select the API base URL).

## 3. Elimination plan (PP6)

**Audit clarification (iteration 4)**: `demo_data.js` is two things, and the split
matters. Its *structural* arrays — `PORTALS` (12 entries), `JOURNEYS` (10, each
carrying step→screen links), `PERSONAS` (4) — are information architecture, not
fabricated data; they are **extracted into the navigation registry at PP0**. Everything
else in the file — the PRNG grid rows, KPI value arrays (`kpis:[{l,v,d,spark}]` in
nav_data), console scripts, dashboard widget datasets, Tell-ME record samples — is
fabrication and is eliminated as follows:

| Step | Action | Enforcement |
|---|---|---|
| E1 | `demo_data.js` is **not ported**. Any prototype logic that referenced it (grid column schemas, console scripts, dashboard widget sets) is re-expressed as: API response shapes (parity tests) + seed fixtures | Parity suite (below) |
| E2 | New CI check `check-no-fixtures.py`: scan `apps/**/src`, `addons/**/static`, shipped bundles for fixture smells (large literal object arrays of "records", `random(` in render paths, `mock*`, `demo*` filenames outside allowed dirs) | Pre-merge gate; fails closed |
| E3 | Sweep the existing Odoo estate for hard-coded demo values in views/templates (e.g. sample names in demo QWeb) — replace with field references | grep + review checklist per module |
| E4 | Seed extension policy: any data a portal E2E needs is added to `seed.py` (idempotent, search-before-create) — never a JSON fixture beside the test | Seed double-run check in CI |
| E5 | Real-data rehearsal env profile (`migration-staging`): loads via the migration pipeline with MIG-02 control totals verified; portals pointed at it for UAT | Migration rehearsal record; totals reconciliation report |

## 4. Data-shape parity suite

For each ported grid/report, a test asserts:
`set(expected_columns) ⊆ set(api_response_fields)` where `expected_columns` come from
the prototype's grid schemas (asset 10) — so nothing the prototype promised silently
disappears, and no column renders fabricated fallbacks.

## 5. Migration of real data (summary — governed by MIG-01…MIG-08)

- 48 legacy sources profiled in Phase 1; the two live trackers feed M01/P01.
- `MIG-02` control totals on every extract; `MIG-03` permanent legacy reference on every
  migrated record (FR-SRM-088 legacy order lookup keeps working after decommissioning).
- `MG-005` mock migration at production volume before every cutover; `MG-004`
  reconciliation with **business sign-off** before any legacy decommission (`MIG-08`).
- Developer workstations stay synthetic-only; this is a standing rule, not a preference.

## 6. Rules for the porting code itself

- No credential literals anywhere (env/secret store only — existing Mimosa constraint).
- Any server-side URL fetch goes through the SSRF guard (http/https only, host
  validated, no localhost/loopback/private/reserved targets) — existing constraint,
  applies to Next.js server components and Odoo alike.
- Portals never write to the database directly: they call the OpenAPI surface (AS-09);
  state changes flow through the event outbox (AS-08).

## 7. Statutory Regulatory Input Masking & Format Standards

*(Corrected 2026-10-05 forensic audit: the CDBL BO-account row was removed —
wrong business domain. Validation rules are grounded to what the estate
actually enforces; "EC sandbox verification" and invented checksums were
removed until a verified algorithm exists.)*

All user-facing data entry fields across R1 (OWL) and R2 (Next.js) must enforce defensive input masking and regex validation matching Bangladesh statutory mandates:

| Regulatory Identifier | Statutory Basis | Input Mask & Format | Validation Rule (as enforced in this estate) |
|---|---|---|---|
| **13-Digit BIN** | NBR VAT Act 2012 | `XXXXXXXXXXXXX` (13 numeric digits) | Digit-only + exact length (the `fix.mushak.register` constraint); no NBR-published checksum exists — length-only until one is verified |
| **10-Digit Smart NID** | Election Commission | `XXXXXXXXXX` (10 digits) | Digit-only + length; synthetic range on dev (DE-12) |
| **17-Digit Legacy NID** | Election Commission | `YYYYXXXXXXXXXXXXX` (17 digits) | Digit-only + length; year-of-birth prefix format |
| **12-Digit e-TIN** | Income Tax Act 2023 | `XXXX-XXXX-XXXX` (12 digits, hyphenated) | Digit-only + length; no published checksum — the TDS-rate linkage (10/15/20%) is backend logic (cd_tax_engine_bd), not a mask |

## 8. Financial Precision — the client renders, the backend computes

*(Corrected 2026-10-05: the previous text prescribed client-side scaled-integer
arithmetic and a UI-computed double-entry checksum — both violate AS-09 "no
business logic in views" and AS-10 backend monetary authority. Odoo's
`account.move` already refuses unbalanced entries server-side.)*

- **Money math is backend-only** (AS-09/AS-10): tax, totals, allocations and
  the Δ = Σdebits − Σcredits = 0 invariant are computed and enforced by Odoo
  (Decimal, currency-carrying fields). The UI never performs monetary
  arithmetic in any numeric type.
- **Portals display what the API returns**: BN-007 formatters render South
  Asian grouping (`1,23,45,678.00`) — formatting, not arithmetic. Where an
  API returns an imbalance (a draft voucher), the UI **displays the
  backend-computed variance** and disables submission against the backend's
  own verdict — it does not recompute it.
- **IEEE 754 therefore cannot drift** in the client, because the client holds
  no monetary accumulation at all.

## 9. Core Module Data-Shape Parity Schema Matrix

*(Corrected 2026-10-05: three model names were fabricated by the earlier
draft (`fix.front.desk.ticket`, `fix.device.registry`, `fix.tax.report` —
none exist). Real models verified against the installed registry. The
`/api/v1/*` endpoint paths are the PP1 PROPOSED surface — none exist today;
only the W4 slice (11 paths) is real. `fix.front.desk.ticket` → the front-
desk domain is `fix.token.queue` + `fix.walkin.intake` + `fix.cash.shift`.)*

| Module | Prototype Columns to Guarantee | Target Odoo Model (REAL) / API Endpoint (PROPOSED) |
|---|---|---|
| **M01 Service Orders** | `id`, `order_no`, `customer_name`, `device_brand`, `device_model`, `fault_code`, `status`, `sla_deadline`, `priority`, `technician_id` | `fix.service.order` / `/api/v1/service-orders` *(proposed)* |
| **M04 Front Desk** | `token_no`, `customer_phone`, `service_type`, `counter_no`, `wait_time`, `queue_status` | `fix.token.queue` + `fix.walkin.intake` + `fix.cash.shift` / `/api/v1/front-desk` *(proposed)* |
| **M17 Device Registry** | `imei_serial`, `brand`, `model`, `warranty_status`, `coverage_end`, `ownership_status` | `fix.device` (+ `fix.device.ownership`, `fix.warranty`) / `/api/v1/devices` *(proposed)* |
| **M19 Financial GL** | `voucher_no`, `date`, `account_code`, `account_name`, `debit_bdt`, `credit_bdt`, `reconciled` | `account.move` (+ `fix.gl_ext` dimensions) / `/api/v1/gl/entries` *(proposed)* |
| **M20 AR & Invoicing** | `invoice_no`, `corporate_ou`, `gross_amount`, `vat_mushak`, `tds_withheld`, `net_payable`, `due_date` | `fix.ar.invoice` (cd_billing_engine) / `/api/v1/invoices` *(proposed)* |
| **M33 Party Master** | `cif_id`, `party_name`, `party_type`, `bin`, `etin`, `nid`, `compliance_status`, `pep_sanctions_cleared` | `res.partner` + `fix.party.role`/`fix.identity.document`/`fix.consent` (cd_party_master) / `/api/v1/parties` *(proposed)* |
| **M51 Tax Engine BD** | `mushak_form`, `tax_period`, `taxable_base`, `vat_rate`, `vds_applicable`, `challan_no`, `reconciliation_status` | `fix.mushak.register` + `fix.vat.return` + `fix.tds.return` (cd_tax_engine_bd) / `/api/v1/tax-reports` *(proposed)* |
