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
