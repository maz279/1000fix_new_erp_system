# 1000FiX Integrated ERP — Data Upload & Update Operations Manual

| Field | Value |
|---|---|
| **Document ID** | 1000FIX-DATA-OPS-MANUAL-2026-001 |
| **Version** | 1.0 |
| **Date** | 2026-11-25 |
| **Classification** | Internal — Operations |
| **Owner** | Data Migration Lead with Finance (GL) and Master Data stewards |
| **Scope** | Every module, function, operation screen, data-capture form, ledger, report, trial balance, profit & loss account and balance sheet of the 1000FiX Odoo 19 ERP + 8 portals |
| **Method** | Zero-trust — every screen id, endpoint, model, field and figure cited here was read from the codebase or measured from the live databases on 2026-11-25. Evidence: `1000fix-2/assets/evidence/` |
| **Companions** | `assets/ASSET_LIST_TAKEON_CAPABILITY_REPORT_2026-11-25.md` (worked asset case) · `assets/evidence/workspace_inventory_2026-11-25.json` (full registry inventory) |
| **Binding standards** | MIG-01…MIG-08 (`docs/p04/migration-mig-standards.md`) · DM-001…DM-014 content pack · MG-001…MG-007 governance · `AGENTS.md` multi-tab form standard |

> **How to read this manual.** Part 0 is the map and the rules. Part 1 tells you WHICH of the five upload pathways to use. Parts 2–5 are the per-domain runbooks (masters, assets, ledgers, transactions). Part 6 explains how uploaded data becomes reports and statements. Part 7 is how to UPDATE what is already loaded. Parts 8–9 are the gates and the safety net. Part 10 is the reference appendices. When a procedure says "measure", it means parse the number from tool output — never type an expected value into evidence (GV-009).

---

## Part 0 — System map, access, golden rules

### 0.1 The estate (measured 2026-11-25)

| Component | Where | Notes |
|---|---|---|
| **Odoo 19 ERP — production data** | `http://127.0.0.1:8069` → DB **fix_real** | admin login; 504 employees, 24,188 partners, 152 branches, real 375-account COA |
| **Odoo 19 ERP — dev/demo** | `http://127.0.0.1:8090` → DB **fix_dev** | synthetic estate; categories unwired — NOT a rehearsal target for real data |
| **P03 Operations Workspace** | `http://127.0.0.1:8069/odoo` → 1000FiX Operations | the D365-style shell: 11 business areas A02–A12, 67 modules, all data screens/forms/reports |
| **Odoo native backend** | `http://127.0.0.1:8069/web` | list views, the native Import wizard (`base_import`), settings |
| **8 portals** | :3000 customer · :3001 corporate · :3002 analytics · :3003 seller · :3004 brand · :3005 agent-console · :3006 partner · :3007 vendor | Next.js; each talks to Odoo ONLY through its own allow-listed `/api/odoo` bridge (Part 1E) |
| **Core PostgreSQL** | 127.0.0.1:5433, user `fix` | DBs fix_real / fix_dev / fix_test + scratch copies; password in codebase `.env` (`POSTGRES_PASSWORD`) |
| **Codebase** | `1000 fix/1000fix_new_erp_system/1000_fix_codebase` | git root is the PARENT `1000fix_new_erp_system`; addons under `addons/domain/<area>/cd_*` + `addons/platform/cd_*` |
| **Data/migration root** | `all_working_folder/1000fix-2` | source spreadsheets, capability reports, implementation logs, `_analysis` scripts, `_migration` staged CSVs + backups |

**Port rule:** the port→DB binding SHIFTS between sessions (8069 has served fix_dev and fix_real on different days; 8089 is currently down). **Always re-probe before any claim or load**: authenticate with `db=fix_real` and `db=fix_dev` against each live port (JSON-RPC `/web/session/authenticate`) and read the returned `db`. A "Database not found" error means the port re-bound, not a dead server.

### 0.2 The golden rules

1. **Backup before every write to fix_real.** `pg_dump -Fc` into `_migration/backups/` (codebase) or `1000fix-2/_migration/backups/`, named `fix_real_pre_<change>_<timestamp>.dump`. Verify the dump restores into a scratch DB before trusting it.
2. **Never edit posted accounting data.** Posted journal entries are immutable (BRU-FIN-12). Corrections are NEW entries: reversals, take-on rollback mirrors, revaluation/disposal documents. The posting log + hash chain (`fix.journal.posting.log`, `fix.journal.chain.head`) record every act and are append-only (FR-FIN-042).
3. **Every migrated record carries its legacy reference permanently** (MIG-03): `legacy_reference` fields, or `ir.model.data` external ids (`__import__`-style modules). Idempotent re-runs UPDATE, never duplicate.
4. **Control totals reconciled BEFORE the load is accepted** (MIG-02): record count, value total, sha256 of the source — measured before AND after.
5. **No double take-on.** A GL that already carries a take-on must never receive another for the same position. Check the account's posted balance and the existing batch register (M19 take-on screens) first. Supersede = reverse the stale legs, then post the fresh batch (the customer-ledger supersede precedent, MIG/2026/11/0156-0157).
6. **Business decides data quality dispositions** (MIG-05): engineering quarantines and reports; the data owner rules what to cleanse, migrate as-is, or leave behind. Every decision lands in the batch decision log.
7. **Rollback is rehearsed, not just documented** (MIG-07). Every lane below has an `action_rollback`; run it in the mock before production.
8. **Shared estate discipline:** parallel sessions work this tree. Commit coherent sets early; verify commits by CONTENT not message; re-probe ports/registry after any `-u`; never `git stash` over someone's uncommitted work.
9. **Zero-trust evidence:** assertions are not evidence. Parse every number from tool output; label simulations; fail closed when something is unconfigured.
10. **Residency (MIG-06):** personal identifiers (NID/TIN) route through `libs/py/fix_residency` even in bulk loaders — never typed into ordinary columns.

### 0.3 Authority model (who may do what)

| Act | Required authority |
|---|---|
| View workspace screens | internal user + M29 module permission (`fix.module.permission`) + model ACL |
| Create/edit records via forms | caller's own ACL + surface `writable` whitelist; NO sudo on write |
| Stage/validate take-on batches | Accountant (`account.group_account_user`) / party registration admin (M33) |
| **Post take-on / depreciation / rollback** | **Accounting Administrator** (`account.group_account_manager`) — `require_takeon_authority` |
| Manual journal entries | maker-checker + DOFA tiers: ≤ ৳500,000 Finance Manager; ≤ ৳5,000,000 CFO; above MD/Board (params `cd_gl_ext.je_dofa_tier2_max` / `je_dofa_tier4_max`); approver ≠ preparer/editor |
| Period close / reopen | Accounting Administrator; reopen is time-boxed (≤3 days default), one named beneficiary, approved by a different administrator |
| Asset activation | accountant group + a posted capitalisation seam (BRU-FXA-01) |
| User creation | JML provisioning chain (M29) — users are never typed directly |

---

## Part 1 — The five upload pathways (decision tree)

```
What are you loading?
│
├─ ONE record (or a handful), interactive?
│   └─ PATHWAY A: P03 workspace D365 form  (Part 1A)
│
├─ A spreadsheet of master records, no accounting effect?
│   ├─ governed lane exists (partners, devices, COA)?  → PATHWAY C wizard
│   └─ otherwise → PATHWAY B: Odoo native Import wizard (external ids!)
│
├─ LEDGER / OPENING BALANCES / anything that posts to the GL?
│   └─ PATHWAY C: governed take-on wizard (M19) — ALWAYS, never raw import
│
├─ Production-scale real-data cut-over (thousands of rows, crosswalks)?
│   └─ PATHWAY D: reviewed odoo-bin shell loader (migrations/ pattern)
│
└─ Customer/partner self-service data (bookings, contracts, claims)?
    └─ PATHWAY E: portal bridge (scoped, ACL-gated)
```

### 1A — Pathway A: the D365 multi-tab form (single-record create/update)

**The UI path (identical for every module):**

1. Open the workspace → mega-menu → area → module → **list screen** (e.g. `M49-register`, `M33-directory`, `M21-directory`).
2. Click a row → the record opens in its **own closable tab** (universal record tabs, cap 16).
3. Click **"Open full record"** → the module's declared **D365 form** (`FORM_MODELS` map, e.g. `fix.branch → M30-form-branch`). Forms with >15 fields are partitioned into tabs (`tabs: [{id,label,bn,icon,badge}]`, ARIA tablist, bilingual) — the binding `AGENTS.md` standard.
4. Edit fields across tabs; child grids (one2many lines/grids) edit inline. Many2one pickers open a search popup for lists >10.
5. **Save** / **Save & Close** → ONE atomic `POST /p03/model/write` carrying header + lines + grids. New record = same endpoint with `record_id` omitted.

**What the engine enforces on every write** (`controllers/p03_generic_api.py:1332`):
- internal users only (`_require_internal`, NVR-22) → model must be in the merged `SURFACES` registry → M29 `_gate` permission → caller's own `check_access` (no sudo) → whole write in a **savepoint** (a refusal leaves nothing).
- **Readonly / guarded / off-whitelist fields:** an unchanged echo is dropped; a CHANGE is refused. Each surface's editable set is the generated `controllers/aXX/writable.py` frozenset (regenerated from the JS form declarations by `controllers/form_fields.py`).
- Coercions: many2one `{id,label}`→id; datetime-local→UTC (Asia/Dhaka); many2many→full id list; one2many→`(0,0,…)/(1,id,…)/(2,id)` commands in the same write; binary uploads→`ir.attachment` (10 MB cap).
- Errors are translated: constraint violations surface the authored message; NOT-NULL names the required field.

**Workflow actions** (Activate, Post, Confirm, Stage…) run via `POST /p03/model/action` — only methods whitelisted in the surface's `actions` set, gated as "approve", savepointed.

**Attachments:** record document panel → `/p03/model/attachment/upload` (PDF/JPG/PNG/DOCX, write-access gated).

### 1B — Pathway B: Odoo native Import wizard (spreadsheet masters)

`base_import` is installed on every DB (auto_install). Use it for masters WITHOUT a governed lane and WITHOUT accounting effect.

**Procedure (official Odoo doctrine):**
1. Open the model's **native list view** (`/web` → the model's action) → **⚙️ Action → Import records**.
2. Upload `.xlsx` or `.csv`. For CSV set separator/delimiter/date format explicitly (ISO `YYYY-MM-DD` recommended; ambiguous day/month dates are a silent systematic error).
3. Map columns to fields (enable "Show fields of relation fields (advanced)" for relational targets). Relational fields: reference by **External ID** (preferred for migration), Database ID, or name — **one mechanism per field**; duplicate names halt validation.
4. **Test** first, then Import. Large files: split batches (timeout risk).
5. **To UPDATE existing records:** the file MUST carry the `id` (External ID) column — "records that have already been imported are modified, instead of being created". The clean loop is **export-to-update**: list view → select records → Action → Export → tick **"I want to update data (import-compatible export)"** → edit the file → re-import.
6. **Warnings (official):** "Imports are permanent and cannot be undone"; keep External IDs consistent forever; explicitly empty cells WRITE empty values (omitted columns keep defaults); two records with the same External ID conflict.

**Estate conventions:** external-id module prefixes `__import__` / `__bd_bank_routing__` / `__asset_takeon__`; legacy keys `<import_ref>-<code>-<slug>` with `-2/-3` uniquifiers (MIG-03). UTF-8 with BOM for Bengali in CSV. Money as decimal text, never floats (DM-07). Dates stored UTC, presented Asia/Dhaka (DM-08).

### 1C — Pathway C: governed take-on wizards (the accounting lanes)

Every wizard follows the same doctrine: **upload Binary `source_file` → `action_stage` (openpyxl parse) → `action_validate` (arithmetic, crosswalks, duplicates, quarantine) → `action_post` (through the M19 funnel `post_with_dimensions`, never raw SQL) → `action_rollback` (mirror entry)**. Every action appends to `decision_log` + chatter; posting requires Accounting Administrator.

| Lane | Models | Workspace screens | What it loads |
|---|---|---|---|
| **Partner ledger** (AR/AP per party) | `fix.ledger.takeon.batch/line` | `M19-takeon`, `M19-takeon-lines`, form `M19-form-takeon` | partner_ledger.xlsx; link-or-create parties through M33 governance; ONE opening entry on journal **MIG**, partner-carrying AR/AP lines, net on contra |
| **Legacy GL archive** (anonymous history) | `fix.legacy.ledger.batch/line` | `M19-legacy-ledger`, `-lines`, `M19-legacy-ar-recon` | 201-style exports; archive rows + ONE branch-dimensioned net control entry on a dedicated NON-reconcileable account |
| **AP register** (voucher-level) | `fix.ap.takeon.batch/line` | M19 AP take-on screens | 200101 register; legacy debits ARE payables → posted as CREDITS, one line per open voucher |
| **Bank ledger history** | `fix.bank.takeon.batch/line` | `M19-bank-takeon`, `-lines` | "Ledger Statement: <GL code>" exports; each row its own dated entry on that bank GL |
| **COA / statutory chart** | `fix.chart.loader` + `fix.chart.account` | `M19-coa-loader`, `M19-coa`, `M19-coa-register` | MD-035 CSV; load → link Odoo accounts → reconcile chart |
| **Party master** (customers/vendors) | `fix.party.import.batch/line` | `M33-import-batches`, `M33-import-lines`, form `M33-form-party-import` | corp/stbl/vendor/customer/contact sheets; stage→validate→import→registration decision→roles→quality score→reconcile |
| **Bank statements** (evidence) | `fix.bank.statement.import/line` | `M50-statements` | CSV/MT940/XLSX; file-hash dedup; opening/closing validation; matching, NOT history |
| **Device bulk** | `fix.device.bulk.load/line` | M17 bulk screens | CSV/XLSX ≤5,000 rows; validate-in-savepoint per row, then all-or-nothing commit |
| **Fixed assets** | `fix.asset.takeon.batch/line` | `M49-takeon`, `M49-takeon-lines`, form `M49-form-takeon` | **built this engagement** — Part 3 |

**The wizard UI pattern** (identical across lanes): list screen → **+ New** → form tab *Source* (upload file, `import_ref`, `takeon_date`, contra account) → Save → command bar **1. Stage → 2. Validate → 3. Post** (or Import for party/ledger lanes) → inspect *Lines* screen (quarantined rows visible with reasons) → *Outcome/Decision Log* tabs. Rollback is a command-bar action on the batch.

**The contra / wash doctrine (tier-1 rule):** every take-on nets against `2.99.99.901` "Legacy Ledger Take-on Contra" (dotted codes — Odoo 19's account-code regex is `^[A-Za-z0-9.]+$`). The wash carries the net legacy position until ALL subledgers (partners, AP, banks, stock, **assets**) are taken on; then it reclassifies to opening equity (300101 Data Migration Offset) so the wash reads zero. Measured 2026-11-25: contra Dr ৳66,695,194.57; after the asset take-on it will be Dr ৳21,221,437.19.

**Control codes are DEPLOYMENT PARAMETERS, not constants.** Check per company before any load:
`cd_billing_engine.account_code.ar` (estate: **100201**), `cd_gl_ext.ledger_takeon.receivable_account_code` / `.payable_account_code` (**200101**), `cd_ap_ext.account_code.ap`, `cd_cash_position.account_code.*`, `cd_gl_ext.legacy_ledger.branch_crosswalk` (47-entry JSON). Code defaults (121000/211000) are the generic BD chart — the real estate overrides them.

### 1D — Pathway D: reviewed odoo-bin shell loaders (production cut-overs)

For production-scale real-data loads with crosswalks and control totals. Proven precedents: `migrations/load_real_inventory.py` (14,198 items / 62,736 units on fix_real), `scratch/user_migration/load_*.py` (504 employees, 344 users), `scratch/a08_drive/fix_real_coa_seed.py`, `scratch/bank_master/bank_directory_load.py` (11,380 branches).

**Runner recipe (Windows/Git Bash, measured):**
```bash
cd 1000_fix_codebase
ROOTW=$(cygpath -w "$(pwd)")
export PYTHONPATH="$ROOTW;$ROOTW\\vendor\\odoo"   # WINDOWS-style paths; POSIX silently fails
python vendor/odoo/odoo-bin shell -c infra/odoo-conf/local.resolved.conf -d <db> --no-http < loader.py
```
- System Python312 (`~/AppData/Local/Programs/Python/Python312/python`) has psycopg2/openpyxl/lxml. The workspace `.venv` is gone.
- `odoo-bin shell` takes the script on **STDIN**; an abort mid-script = full ROLLBACK (no partial commit).
- Loader discipline (MIG-02): sha256 + count + value total BEFORE; idempotent upsert on the legacy key; SAVEPOINT per wave; re-measure AFTER; `decision_log`/print evidence; env switches for dry-run (`BANK_DIR_DRY_RUN=1`, `REAL_INV_PURGE=0` patterns).
- After any `-u` upgrade: the watchdog-restarted server may serve a STALE registry — kill + restart + re-verify `fields_get` before bulk writes.
- Scripts are written with the Write/Edit tools (the Mimosa hook rejects Bash heredoc writes); keep file paths as fixed literals or argv; `python -I` ignores PYTHONIOENCODING → `sys.stdout.reconfigure(encoding="utf-8")` inside.

### 1E — Pathway E: portal self-service bridges

Each portal (`apps/web/<name>/app/api/odoo/[...path]/route.ts`) is a POST-only, JSON-only, 1 MB-cap bridge to a server-configured Odoo origin (`ODOO_INTERNAL_URL`), with a **path allow-list**: one namespace per portal (`customer/`, `corporate/`, `analytics/`, `seller/`, `brand/portal/`, `contact/portal/`, `vendor/portal/`; partner is exact-only) + session endpoints. Staff endpoints (`/p03/*`, `/web/dataset/call_kw`) are REFUSED. The caller's Odoo session cookie is the only credential; Odoo-side ACLs apply to the portal user. **Consequence:** portal data (bookings, contracts, claims, referrals) is uploaded through the portal's own forms; it lands in the same Odoo models and flows into the same reports. Never point a portal at a DB it is not scoped for (the `.env.local` `ODOO_INTERNAL_URL` decision is per-portal).

### 1F — File conventions (every pathway, DM-012)

UTF-8 throughout (BOM for CSV with Bengali); ISO 8601 dates; decimal money with explicit currency (BDT); mobile numbers as TEXT (leading zero); blank ≠ NULL ≠ "N/A" — declare which means "no value"; one header row; no merged cells; a control block on every file (source, extracted_at, record_count, value_total, checksum); templates are ISSUED from the DM-012 pack, never hand-made; sheet selection BY LAYOUT (title match), never "first sheet" blindly.

---

## Part 2 — Master-data runbooks

> Universal update rule for masters: **export-to-update with external ids** (Pathway B) or the D365 form (Pathway A). Governed lanes (C) for bulk. Never rename permanent codes (employee code permanence FR-HCM-003; journal codes route money — reassigning a journal code silently re-routes payments).

### 2.1 Chart of Accounts (M19)
- **Screens:** `M19-coa` (statutory register), `M19-chart-account`, `M19-coa-register` (report), form `M19-form-chart-account`; loader `M19-coa-loader` + form `M19-form-coaload`.
- **Upload:** `fix.chart.loader.action_load_from_csv` (MD-035 CSV at `project_content/02_Master_Data_and_Configuration/02E_Finance_and_Statutory/MD-035_Chart_of_Accounts_Bangladesh.csv`) → `action_link_odoo_accounts` (ODOO_CHART_MAPPING) → `action_reconcile_chart` (accounting equation + no unmapped posted balance).
- **Odoo 19 traps:** `account.account` code lives in jsonb `code_store` keyed by ROOT company id (`code_store->>'1'`); `company_ids` M2M (no company_id); receivable/payable accounts MUST be reconcile=True; `account.group` membership is computed from equal-length prefix ranges (longest wins).
- **Update rules:** control-flag changes are governed (`fix.chart.control.change`, different approver); archive requires ZERO balance on both charts (COA-04); posting rules COA-01 postable leaf / COA-02 no manual posting on control accounts / COA-03 required dimensions.
- **Precedent:** real 375-row COA swapped onto fix_real 2026-11-08 (backup + idempotent phase-committed script).

### 2.2 Branches / Operating Units (M30)
- **Screens:** `M30-branches`, form `M30-form-branch`; zones/capabilities/geofences/provisioning screens.
- **Upload:** `scratch/user_migration/load_masters.py` / `load_branch_master.py` pattern; 152 branches live on fix_real (79 real + brand desks + synthetic smoke leftovers flagged for cleanup).
- **Crosswalk:** legacy labels resolve name → `cd_gl_ext.legacy_ledger.branch_crosswalk` → `LEGACY_BRANCH_ALIASES` (`fix_legacy_ledger.py:73`, 48-branch canonical). Extend the PARAMETER, not the code. Brand labels consolidate onto physical SCs (Sony→HQ, Honor B.City→Bashundhara City).
- **Update:** branch rename via form; every posting carries branch+OU (`fix.journal.dimension`, AS-03); an asset's branch changes only via acknowledged transfer.

### 2.3 House banks & bank directory (M50)
- **Screens:** `M50-accounts` (account.journal type=bank), form `M50-form-journal` (routing, BEFTN, treasury role).
- **Upload:** `scratch/bank_master/bank_directory_load.py` (11,380 branches, xmlids `__bd_bank_routing__.r_<routing>`, dry-run env) + `bank_master_import.py` (curated). 27 bank journals live; opening balances posted via the bank take-on lane (MIG/2026/11/0001 pattern).
- **Update rules:** journal CODE is load-bearing (payment params resolve by code); `res.partner.bank.unlink` ARCHIVES (record survives); mandates/signatories change via maker-checker (`fix.payee.bank.change`), never typed on the journal form.

### 2.4 Customers / parties (M33)
- **Screens:** `M33-directory` (scoped: logins/staff structurally excluded), form `M33-form-party`; import `M33-import-batches`/`-lines`.
- **Upload:** `fix.party.import.batch` (sheet kinds corp/stbl/vendor/customer/contact) → stage → validate (BD mobile regex, email normalisation, district→division, quarantine) → import (DRAFT parties, legacy keys, PDPA stamp) → decide registrations (two-tier, system-trusted cut-over) → assign roles → score quality → reconcile.
- **Update rules:** parties are BORN draft (create guard); activation via approval `_activate_if_complete`; dedup is a STEWARD queue (never auto-merge); `res.partner` has NO `mobile` field in Odoo 19 (phone only); company_id must be set or company-scoped grids hide the record.
- **Precedent:** 2,782 real customer parties live; 12,905 per-customer ledger files imported via `fix.ledger.takeon` (5,627 linked + 1,049 created; supersede of 472 stale legs).

### 2.5 Vendors / suppliers (M42 + M33 vendor kind)
- **Screens:** `M42-suppliers`, form `M42-form-supplier`; vendor portal onboarding via :3007 bridge.
- **Upload:** party import `vendor` kind + `cd_vendor_portal/fix_party_import_vendor.py`; supplier governance (segments, compliance docs, scores) via M42 forms.

### 2.6 Employees (M21)
- **Screens:** `M21-directory`, form **`M21-employee` (10 tabs:** identity/statutory/organization/academic/career/technical/compensation/health/emergency/vault**)** — the BLA 2006 / Labour Rules 2015 / ITA 2023 statutory block (name_bn, NID, e-TIN, tax zone/circle, Form 7 service book, BEFTN routing, MFS, overtime eligibility, next-of-kin).
- **Upload:** `scratch/user_migration/load_employees.py` (match on work_email; NID/TIN NOT typed — routed to `fix.identity.document` via residency, MIG-06); 504 real employees live with external ids.
- **Update rules:** **employee code is permanent** (FR-HCM-003 — swap records, never rename); marital status lives on `hr.version` (Odoo 19 `_inherits`); manager cycles must be resolved before import; JML events drive downstream provisioning.

### 2.7 Users / logins (M29)
- **Screens:** `M29-users` (create:false), `M29-form-provision`, `M29-jml`, `M29-module-permissions`.
- **Upload:** users are **provisioned by the JML chain** (joiner/mover/leaver events → `fix.access.request` → role grants), NEVER typed. Loader precedent: `load_users_roles.py` (344 users). Keycloak SSO wiring: `wire_oauth.py`.
- **Update:** role changes via M29 module-permission screens; SoD enforced; synthetic users are DEACTIVATED, never deleted (purge_synthetic.py pattern).

### 2.8 Items / catalogue (M37)
- **Screens:** `M37-items`, form `M37-item` (9 item types), services/parts-id/hierarchy/taxclass/publications/lifecycle.
- **Upload:** real inventory precedent `migrations/load_real_inventory.py` (14,198 items; three part identities: new SKU `default_code`, `legacy_erp_part_number`, MPN; keys `REAL:INV:<erp pn>`; control totals re-measured).
- **Update:** item record form; tax class via M37-taxclass; never delete referenced items — archive.

### 2.9 Warehouses / locations (M41)
- **Screens:** `M41-warehouse`, `M41-stock-location`, zones/bins; forms `M41-form-warehouse` etc.
- **Upload:** `load_warehouses.py` (603→236 canonical normalization precedent, crosswalk CSV in `1000fix-2/warehouse with location/`).
- **Stock VALUE take-on:** `fix.inventory.valuation.suspense.action_stock_takeon` — ONE entry per company per OU (Dr stock by brand / Cr 300101), runs ONCE per company (row lock), switches the company to real-time stock posting in the same transaction. Accounting Administrator.

---

## Part 3 — Fixed assets (M49): the Asset_List_Compiled.xlsx case

> Full measured audit: `assets/ASSET_LIST_TAKEON_CAPABILITY_REPORT_2026-11-25.md`. Summary of the end-to-end procedure:

### 3.1 The register model and its laws
`fix.fixed.asset`: code (FA- tag, unique per company), category, branch (operating_unit_id), custodian (hr.employee), gross, salvage, life_months, purchase_date, depreciation_start, state draft→active→disposed. **Book values (cost, accumulated, NBV, tax WDV) are computed from POSTED events only** — you cannot type an accumulated depreciation. **Terms freeze at activation** (ASSET_TERMS); corrections go through approved documents: `fix.asset.depreciation.change` (life/residual/suspend), revaluation/impairment (CFO), transfer (acknowledged), disposal (gain/loss). Only drafts are deletable.

### 3.2 Activation law (BRU-FXA-01)
An asset activates ONLY from an unconsumed **M19 seam** whose posted journal item is a debit on the category's asset account equal to gross ±0.005 (or via CWIP capitalisation / IFRS 16 lease). **Therefore an asset upload is an ACCOUNTING operation**: the take-on posts acquisition entries first, then creates seams, then activates.

### 3.3 The take-on procedure (`fix.asset.takeon`, built this engagement)
1. **Prerequisites (fail-closed):** every used category wired (journal + asset/accum/expense accounts) — fix_real's 7 categories are wired on journal FA; new heads (Office Renovation 100040, Establishment 100042, Software 100804) need RENO/EST/SW categories; branch crosswalk covers every label; period open at takeon_date; target GL codes carry no prior take-on.
2. **Stage:** upload the xlsx on `M49-form-takeon` (Source tab: file, import_ref `ASSET-2026-11`, takeon_date 2026-11-30) → `action_stage` parses 1,129 rows (SL is the row key; "Total (filtered)" rows skipped).
3. **Validate:** identity cost−accum=NBV ±0.005; SL uniqueness vs live external ids; category crosswalk; branch resolution (name→crosswalk→aliases; unresolved quarantined); life/salvage policy per row; custodian match optional. Quarantined rows are visible with reasons, never posted.
4. **Post (Accounting Administrator):**
   - Entry 1 (MIG journal): Dr each category asset account per asset (=gross, branch+OU on every line) / Cr contra 80,519,165.70.
   - Entry 2 (MIG journal): Dr contra 35,045,408.32 / Cr each category accum account per asset (=legacy accum).
   - One seam per asset → draft asset (legacy_reference `<ref>-SL-<sl>`, external id `__asset_takeon__.a_<ref>_<SL>`) → `action_activate`.
   - Opening depreciation runs (book + tax), period = takeon month, posted lines = legacy accum, **GL carried by Entry 2 — no second posting**. The engine's `_book_amount` then charges `(NBV−salvage)/remaining_months` from December, last month landing exactly on salvage.
5. **Reconcile:** `M49-gl-recon` (`register_gl_reconciliation`) zero variance per category; TB Dr=Cr; per-code GL == per-class file totals; batch decision log complete.
6. **Rollback (rehearsed 2026-11-25 on a fix_real copy):** mirror both entries, clear unposted foreign depreciation lines (a foreign POSTED charge blocks rollback — reverse that run first), unconsume seams, reverse activation, unlink drafts + opening runs + external ids. Batch → rolled_back; **balances restore, gross TB movement is append-only** (posted history is never erased). Re-post idempotently: `action_validate` from rolled_back → corrected policy → `action_post`.

### 3.4 Month-end after go-live (runbook.md §4.2)
1. Leases: Post Due Months. 2. Dual-book depreciation: create run per book → Compute → check notes → Post (accounting book posts Dr expense / Cr accumulated per category AND branch; tax book is memo-only and refuses unverified M51 rates). 3. Post approved disposals/revaluations. 4. Review Schedules & Movements (`movement_schedule`, IAS 16.73(e)). Re-running a month never charges twice (DB unique asset/book/month + posted-line skip).

### 3.5 Production record (2026-11-25, measured)
The lane was built (commits `8a1c598c` + `7d5c3068`, M49 suite 139/139), rehearsed on a restored fix_real copy (all gates green incl. rollback + idempotent re-post), and **executed on fix_real**: batch `ASSET-2026-11`, takeon_date 2026-11-30, entries **MIG/2026/11/0008 + 0009** — **1,129 assets active**, GL cost/accum match the file code-by-code, register↔GL variance **0.00**, TB **634,743,601.47 Dr=Cr**, contra **21,221,437.19**, 1,129 external ids, IAB grid verified live. Provisional adjudications (branch crosswalk repairs, Aftabnagar→HQ, life policy = category defaults + 1 / salvage 0, filtered 1,129-row scope) are **flagged for ratification** — correct via rollback + re-post. Full record: `assets/ASSET_TAKEON_IMPLEMENTATION_LOG_2026-11-25.md`.

---

## Part 4 — Ledgers & opening balances

### 4.1 Which lane for which ledger

| Legacy source | Lane | Control | Shape |
|---|---|---|---|
| partner_ledger.xlsx (per-party AR/AP) | `fix.ledger.takeon` | 100201 / 200101 (params) | ONE opening entry, partner-carrying lines, date_maturity=takeon_date; ageing/statements count MIG residuals via `open_takeon_balances` |
| 201 anonymous AR history | `fix.legacy.ledger` | dedicated non-reconcileable 100201 archive | archive rows + ONE branch-dimensioned net control entry; NEVER re-post anonymous history on receivable accounts |
| 200101 AP voucher register | `fix.ap.takeon` | dedicated legacy control | register debits ARE payables → CREDITS, one line per open voucher |
| Bank "Ledger Statement" exports | `fix.bank.takeon` | the bank GL in the title | row-level history, each row its own dated entry; GL-scoped duplicate guard |
| Cash in hand / cheque in hand | legacy lane (CASHCIH/CIH refs) | 100108 / 16556556 | aggregate control entries (precedents posted 2026-11-10) |
| Bank statements (evidence) | `fix.bank.statement.import` (M50) | bank journal | matching to receipts/settlements/executions; NOT history |
| Fixed assets | `fix.asset.takeon` (Part 3) | category accounts | acquisition + opening accum |
| Stock value | `action_stock_takeon` (M15) | stock accounts by brand | once per company; switches on real-time posting |

### 4.2 Opening-balance completion (the wash path)
Take-ons net on contra `2.99.99.901`. When every subledger is taken on, reclassify the residual wash to opening equity (300101) so the contra reads zero — the tier-1 rule documented in `fix_ledger_takeon.py:222–229`. Until then the contra balance IS the honest "not yet taken on" position. Measured path: 66.70M Dr → (assets) 21.22M Dr → (remaining subledgers) → 0.

### 4.3 Supersede (correcting an already-posted take-on)
Never edit posted lines. Pattern (customer-ledger precedent): post a **reversal mirroring the stale legs** (MIG/2026/11/0156), keep old-only legs that are still valid, then post the fresh batch (MIG/2026/11/0157). Or use the batch's own `action_rollback` (mirror) and re-post a corrected batch. Re-measure the TB and the control account after.

### 4.4 Subledger → GL proof
`/p03/gl/recon` + `subledger_reconciliation_rows` (AR open residuals + MIG take-on open; AP payable residuals + take-on; VAT output Mushak 6.3; VAT input supplier bills) — controls resolved via the deployment parameters, **fail closed** when unconfigured. `assert_subledgers_reconciled` gates period close. Per-customer proof: `ar_subledger_gl_recon` pack (M20). Legacy archive proof: `legacy_ar_control` pack (M19) — archive vs posted control per branch; do NOT net the partner take-on against it.

---

## Part 5 — Operational transactions (by area)

| Area | Modules | Data entry path | Bulk path | Notes |
|---|---|---|---|---|
| A02 Service Ops | M01 orders, M02 dispatch, M31 workshop, M03 logistics, M04 front desk, M05 MSP, M06 data | `so_intake`/`so_list`/`so_board`, fs_board, counter sale forms | device bulk (M17) for registry; service history via governed loaders | orders closed → billable events → AR invoices automatically (M20 queue) |
| A03 Customer | M33 party, M07 loyalty, M10 complaints, M34 consent, M27 contact centre, M32 assistant, M35 campaigns | M33 forms; contact-centre wrap-up mandatory | party import batches | PDPA lawful basis stamped at import |
| A04 Commercial | M37 catalogue, M11 pricing, M36 quotation/tender, M08 AMC, M09 warranty, M39 billing, M38 RMA, M12 marketplace, M40 partners | quotation/contract forms | catalogue loaders | AMC billing feeds M39 usage/proration |
| A05 Circular | M13 rental, M14 trade-in, M18 e-waste | rental/trade-in forms | — | fleet ledger + sequences governed |
| A06 Supply | M15 inventory, M41 WMS, M16 procurement, M42 suppliers, M43 demand, M44 import | PO/receipt forms; WMS execution screens | real-inventory loader; stock take-on | GRNI accrual blocks close if unposted |
| A07 Assets & Equip | M17 devices, M45 kits, M46 fleet, M47 facility, M48 IoT | device registration (serial/IMEI uniqueness) | `fix.device.bulk.load` (≤5,000 rows, validate-then-commit) | acquisition events bridge to M49 draft capex |
| A09 People | M21 HR, M55 attendance, M56 payroll, M57 performance, M22 learning, M58 talent, M59 HSE | employee 10-tab form; attendance/payroll screens | user_migration loaders | payroll tax via M51 verified rates |
| A10 Quality | M23 QMS, M60 GRC, M24 documents, M61 knowledge | NCR/risk/document forms | — | e-signature + repository governed |
| A11 Insight | M25 BI, M26 ML, M62/M63 | dashboards read live | — | no invented numbers: honest empty states |
| A12 Platform | M28 config, M29 IAM, M30 entity, M64 MDV, M65–M67 | admin forms | bank directory loader | M64 scores every migration batch |

**Never bulk-load:** posted accounting documents, user logins (JML only), approval decisions, audit logs, hash-chain rows. **Always bulk via a lane:** anything with a GL effect.

---

## Part 6 — Reports, trial balance, P&L, balance sheet

### 6.1 The computation chain (one query, three consumers)
`cd_gl_ext/models/fix_fiscal_year_ext.py` pure functions over **POSTED `account.move.line` only** (company + date window):
- `compute_trial_balance(env, company, date_from, date_to)` — opening + movement = closing per account; earlier-years P&L rolls into `equity_unaffected` (or an explicit undistributed row); returns `balanced`.
- `compute_pnl` — income/expense only; `net_profit = −sum(balance)`.
- `compute_balance_sheet(env, company, date_to)` — non-P&L **from inception** + `unclosed_profit_and_loss` (all P&L from inception, negated); no date_from.
- `compute_cash_flow` — direct-method-lite on `asset_cash` accounts, counterpart classification; M50 executions fallback (labelled).
- `opening_balances` — BS carries everything before date_from; P&L carries only the current fiscal year (**1 July–30 June**, BRU-FIN-19).
- Branch/OU slicing: `pnl_by_branch` (7 dimensions via `fix.journal.dimension`; unallocated bucket always present; ties exactly to company P&L).

**The same functions feed:** the statement screens (`/p03/gl/statements`), the M19 report packs (`REPORTS["trial_balance"|"pnl"|"balance_sheet"|"cash_flow"]`), and every export/email (`/p03/model/report/export`). **Figures cannot drift between screen, CSV, Excel, PDF and email.**

### 6.2 The screens and how to refresh them
| Screen | Kind | Statement |
|---|---|---|
| `M19-tb` | statement | Trial Balance |
| `M19-pl` | statement | Profit & Loss (BFRS) |
| `M19-bs` | statement | Balance Sheet |
| `M19-cf` | statement | Cash Flow |
| `M19-consol` | statement | Consolidated (aggregation, not elimination) |

**Refresh = nothing to do:** statements are computed live on open/period-change. After ANY upload that posts entries, re-open the screen (or change the period selector) — the new figures are already there. Draft/unposted moves NEVER appear; the close itself blocks on pending drafts.

**Export:** every statement screen carries **CSV / Excel / PDF / Email** buttons (ReportActions template). CSV = raw + UTF-8 BOM; XLSX = branded letterhead + meta + totals + notes; PDF = A4 print document (2,000-row cap with explicit truncation note); every download logged to `fix.bi.export.log`. Grid reports (`table_report` packs, 562 across the estate) export through the same endpoint with their declared filters — screen and export are ONE query.

**Drill-down:** statement row → journal register filtered by account (`glDrillAccount`); partner ledger/statement screens (`M19-partner-ledger`, `M19-partner-statement`) include MIG take-on residuals.

### 6.3 Reconciliation packs (the proof layer)
`register_gl_reconciliation` (M49, close gate) · `legacy_ar_control` (M19) · `ar_subledger_gl_recon` (M20) · `ap_ageing`/`grni_accruals` (M52) · `bank_recon_summary`/`daily_cash_position` (M50) · `movement_schedule`/`dual_book`/`nbv_by_category` (M49) · `/p03/gl/recon` (AR/AP/VAT) · `/p03/gl/audit` (posting log + outbox + hash chain).

### 6.4 KPI tiles
`/p03/finance/kpis` merges M19/M20/M50/M51/M52/M53/M49/M54 hooks (posted_moves_mtd, revenue_mtd, tb_imbalance, ar_invoices_mtd, dso, unreconciled_bank_lines, m49_gross_block, m49_nbv…). Tiles read the same posted data — an upload that posts moves updates them on refresh.

### 6.5 Period close (the statutory gate)
`fix.period.close` (M19-close screen): start period → generate the 10 SOP steps (each with an owning group) → mark done **with real evidence** (posted entry number / model,id / attachment) → ready (suspense clear + VAT return reconciled + no pending drafts + subledgers reconciled) → close (bank reconciled too; sets company `fiscalyear_lock_date` in the same transaction). Lock moves FORWARD only; the M19 funnel refuses locked-period postings for ALL sources including superuser. The only door back: approved time-boxed `fix.period.reopen`.

---

## Part 7 — Updating existing records (the rules)

### 7.1 What you may edit, and how
| Data class | Update path | Forbidden |
|---|---|---|
| Draft documents (any module) | D365 form / native import with external id | — |
| Master records (partner, employee, item, branch, bank) | form or export→edit→re-import (external id) | renaming permanent codes; typing NID/TIN (residency) |
| Posted journal entries | **NEW entry**: reversal / rollback mirror / revaluation / disposal | reset-to-draft (BRU-FIN-12), direct line edits, SQL |
| Take-on batches | `action_rollback` (mirror) → corrected re-post | editing posted lines; second take-on on the same GL |
| Active fixed assets | approved `fix.asset.depreciation.change` / revaluation / transfer / disposal | editing ASSET_TERMS (frozen) |
| Locked periods | approved `fix.period.reopen` (time-boxed, named user) | moving the lock date backward |
| Users / roles | JML chain / M29 permission screens | direct res.users creation |
| Guarded fields (`fix.guarded.mixin`) | only the owning workflow action (in-process token) | form writes, RPC, SQL |
| Audit logs / hash chain | append-only | any write/unlink (FR-FIN-042) |

### 7.2 The export→edit→re-import loop (masters)
1. List view → select → Export → **"I want to update data"** (includes External ID, importable fields only).
2. Edit ONLY the columns you intend to change (explicit blanks WRITE blanks; omitted columns keep values).
3. Test → Import. The external id makes it an UPDATE. Keep a copy of the exported file as the before-snapshot.
4. Verify: re-export and diff; measure the changed count.

### 7.3 Mass updates without a spreadsheet
- Governed multi-row workflow actions on list command bars (state-scoped).
- RPC `execute_kw` write in waves (Pathway D discipline: savepoints, control totals, decision log) — for internal tooling, never for accounting postings (those go through the funnel).
- **There is NO generic bulk-edit in the workspace engine** — by design. Batch data changes go through the governed lanes.

### 7.4 Correcting reports
Reports are never edited — they are computed. If a figure is wrong: find the posting (drill-down → `/p03/gl/audit`), correct the SOURCE via the proper document (reversal, dep change, revaluation, take-on rollback+re-post), and the statement updates itself. If the period is locked, reopen first (approved, time-boxed).

---

## Part 8 — Validation & sign-off gates

### 8.1 MIG-02 control-total template (every load)
```
source / extracted_at / record_count / value_total / checksum(sha256)
loaded_at / loaded_count(==record_count) / rejected_count / rejection_reasons
reconciled_by / reconciled_at / approved(yes/no)
```
Measured BEFORE the load is accepted — not after. The xlsx "Total (filtered)" row pattern (internal sum proof) is recommended on every source file.

### 8.2 Post-load reconciliation checklist
- [ ] TB Dr = Cr (company, posted) — measured, not asserted
- [ ] Each control account = its subledger (AR/AP/VAT via `/p03/gl/recon`; assets via `register_gl_reconciliation`; banks via statement matching)
- [ ] Per-code GL balances == per-class source totals (asset take-on: 8 legacy codes)
- [ ] Record counts: source == loaded + quarantined (every quarantine has a reason + disposition)
- [ ] External ids / legacy refs present on 100% of migrated records (MIG-03)
- [ ] No synthetic/demo residue in the loaded scope; no double take-on (batch register checked)
- [ ] Decision log complete; DQ dispositions signed by the data owner (MIG-05)
- [ ] Visual verification in the **in-app browser** (standing directive): the register grid, the recon screen, M19-tb/bs/pl render the measured figures

### 8.3 Four-eyes / DOFA quick reference
Manual JE ≤ ৳500k → Finance Manager; ≤ ৳5M → CFO; above → MD/Board. Approver must not be preparer/requester/editor; changed entries re-route. Take-on posting/rollback, period close/reopen, control-flag changes, bank charges above ceiling: Accounting Administrator with SoD. Capex/disposal/revaluation: DOFA-routed approvals.

---

## Part 9 — Rollback & recovery

### 9.1 Before any production write
```bash
# inside the postgres container (compose-postgres-1), then docker cp out
pg_dump -Fc -d fix_real -f /tmp/fix_real_pre_<change>_<ts>.dump
```
Store in `_migration/backups/`. **Restore-verify into a scratch DB** (`createdb scratch_verify … && pg_restore`) and re-measure the key counts before trusting the dump.

### 9.2 Lane-level rollback
Every take-on batch: `action_rollback` posts the mirror through the same funnel (branch dimensions preserved), retains archive/master rows as evidence, marks the batch rolled_back. Asset take-on additionally clears unposted foreign depreciation lines, unconsumes seams, reverses activation, unlinks drafts + opening runs + external ids, and accepts re-validation for an idempotent re-post. **Rollback restores account BALANCES; the TB's gross debit/credit movement grows by the mirror (append-only ledger) — Dr=Cr always holds.** **Rehearse it in the mock (MIG-07)** — the rehearsal record is part of the gate evidence (asset lane rehearsal: `1000fix-2/assets/evidence/rehearsal_*_2026-11-25.json`).

### 9.3 Database-level recovery
Restore the pre-change dump into a scratch DB, verify, then (only with explicit approval) replace the target. Posted-move purges are a LAST resort (SQL FK-graph walker pattern, children-first, NEVER-DELETE set: res_partner/hr_employee/res_users/res_company) — used only for synthetic de-seeding, never for real data.

### 9.4 Environment hazards (measured traps)
- Killed pytest leaves `idle in transaction (aborted)` sessions → `pg_terminate_backend` before re-running suites.
- Fresh `CREATE DATABASE … TEMPLATE` copies can lag code → `-u all --stop-after-init` on the copy first.
- Stale registry after `-u` → restart + re-verify fields_get.
- Shared-tree stash cycles delete uncommitted work → commit early; recovery via `git fsck --lost-found` + stash-commit grep.
- One Odoo server answers MULTIPLE DBs on a port → authenticate(db=) explicitly; cookie clashes across 127.0.0.1 ports → use distinct hostnames per portal/DB in the browser.

---

## Part 10 — Appendices

### Appendix A — Module / screen / form / report inventory (measured 2026-11-25)

Static parse of `controllers/aXX/mYY.py` (SURFACES models + actions, REPORTS packs) and `static/src/aXX/mYY.js` (screen declarations with kinds, form ids). Full detail (every model, action set, screen id, kind, form id): `assets/evidence/workspace_inventory_2026-11-25.json`. Counts are source-declared screens (the canonical navigation registry lists 823 menu screens; fragments declare additional sub-screens). M50's packs are defined via a helper the static parse does not expand — its 9+ packs are documented in Part 4/6.

| Module | Area | Served models | Screens | Forms | Report packs | Key upload/update lanes |
|---|---|---:|---:|---:|---:|---|
| M01 | a02 | 14 | 30 | 15 | 10 | D365 forms + native import |
| M02 | a02 | 14 | 38 | 17 | 16 | D365 forms + native import |
| M03 | a02 | 7 | 24 | 14 | 10 | D365 forms + native import |
| M04 | a02 | 11 | 27 | 21 | 8 | D365 forms + native import |
| M05 | a02 | 27 | 39 | 24 | 11 | D365 forms + native import |
| M06 | a02 | 18 | 25 | 22 | 6 | D365 forms + native import |
| M07 | a03 | 20 | 30 | 18 | 7 | D365 forms + native import |
| M08 | a04 | 17 | 33 | 24 | 12 | D365 forms + native import |
| M09 | a04 | 18 | 36 | 19 | 11 | D365 forms + native import |
| M10 | a03 | 22 | 32 | 18 | 9 | D365 forms + native import |
| M11 | a04 | 19 | 29 | 17 | 8 | D365 forms + native import |
| M12 | a04 | 14 | 33 | 18 | 16 | D365 forms + native import |
| M13 | a05 | 16 | 27 | 26 | 7 | D365 forms + native import |
| M14 | a05 | 13 | 27 | 16 | 8 | D365 forms + native import |
| M15 | a06 | 21 | 39 | 17 | 19 | Stock take-on (GL valuation) |
| M16 | a06 | 16 | 33 | 21 | 11 | D365 forms + native import |
| M17 | a07 | 24 | 36 | 26 | 9 | Device bulk load (validate-then-commit) |
| M18 | a05 | 23 | 34 | 28 | 6 | D365 forms + native import |
| M19 | a08 | 28 | 49 | 25 | 14 | COA loader; partner/legacy-AR/AP/bank take-on wizards |
| M20 | a08 | 25 | 46 | 21 | 12 | D365 forms + native import |
| M21 | a09 | 19 | 34 | 22 | 8 | Employee master form (10 tabs); scratch loaders |
| M22 | a09 | 20 | 29 | 18 | 7 | D365 forms + native import |
| M23 | a10 | 21 | 28 | 19 | 5 | D365 forms + native import |
| M24 | a10 | 21 | 26 | 18 | 4 | D365 forms + native import |
| M25 | a11 | 14 | 32 | 9 | 1 | D365 forms + native import |
| M26 | a11 | 13 | 26 | 15 | 10 | D365 forms + native import |
| M27 | a03 | 39 | 46 | 35 | 11 | D365 forms + native import |
| M28 | a12 | 23 | 23 | 19 | 6 | D365 forms + native import |
| M29 | a12 | 26 | 37 | 26 | 7 | User provisioning via JML (never typed) |
| M30 | a12 | 27 | 40 | 29 | 5 | D365 forms + native import |
| M31 | a02 | 25 | 33 | 25 | 7 | D365 forms + native import |
| M32 | a03 | 13 | 26 | 21 | 10 | D365 forms + native import |
| M33 | a03 | 25 | 32 | 29 | 7 | Party import batches (corp/stbl/vendor/customer) |
| M34 | a03 | 17 | 27 | 14 | 11 | D365 forms + native import |
| M35 | a03 | 16 | 28 | 22 | 7 | D365 forms + native import |
| M36 | a04 | 22 | 38 | 35 | 7 | D365 forms + native import |
| M37 | a04 | 17 | 36 | 22 | 11 | D365 forms + native import |
| M38 | a04 | 16 | 29 | 16 | 9 | D365 forms + native import |
| M39 | a04 | 10 | 22 | 11 | 9 | D365 forms + native import |
| M40 | a04 | 27 | 39 | 27 | 13 | D365 forms + native import |
| M41 | a06 | 36 | 53 | 39 | 15 | Warehouse/location master forms |
| M42 | a06 | 17 | 23 | 17 | 5 | D365 forms + native import |
| M43 | a06 | 15 | 24 | 15 | 9 | D365 forms + native import |
| M44 | a06 | 22 | 31 | 21 | 9 | D365 forms + native import |
| M45 | a07 | 19 | 32 | 21 | 12 | D365 forms + native import |
| M46 | a07 | 18 | 30 | 18 | 11 | D365 forms + native import |
| M47 | a07 | 30 | 44 | 29 | 14 | D365 forms + native import |
| M48 | a07 | 19 | 30 | 17 | 11 | D365 forms + native import |
| M49 | a08 | 21 | 28 | 18 | 8 | **Asset take-on wizard (this engagement)** |
| M50 | a08 | 29 | 41 | 25 | (helper) | Bank statement import (CSV/MT940/XLSX) |
| M51 | a08 | 20 | 34 | 16 | 9 | D365 forms + native import |
| M52 | a08 | 28 | 36 | 24 | 6 | D365 forms + native import |
| M53 | a08 | 21 | 25 | 16 | 6 | D365 forms + native import |
| M54 | a08 | 12 | 26 | 15 | 10 | D365 forms + native import |
| M55 | a09 | 22 | 35 | 18 | 7 | D365 forms + native import |
| M56 | a09 | 26 | 39 | 22 | 7 | D365 forms + native import |
| M57 | a09 | 21 | 27 | 21 | 5 | D365 forms + native import |
| M58 | a09 | 24 | 33 | 20 | 7 | D365 forms + native import |
| M59 | a09 | 26 | 33 | 26 | 5 | D365 forms + native import |
| M60 | a10 | 25 | 35 | 29 | 5 | D365 forms + native import |
| M61 | a10 | 15 | 21 | 11 | 6 | D365 forms + native import |
| M62 | a11 | 19 | 26 | 18 | 4 | D365 forms + native import |
| M63 | a11 | 12 | 20 | 14 | 7 | D365 forms + native import |
| M64 | a12 | 16 | 24 | 16 | 5 | D365 forms + native import |
| M65 | a12 | 10 | 20 | 14 | 3 | D365 forms + native import |
| M66 | a12 | 10 | 18 | 10 | 4 | D365 forms + native import |
| M67 | a12 | 12 | 22 | 12 | 7 | D365 forms + native import |
| **TOTAL** | 11 areas | **1,323** | **2,108** | **1,361** | **562** | |

### Appendix B — Load template column specs (per lane)

| Lane | Required columns | Key | Control proof |
|---|---|---|---|
| Asset take-on | SL, COA Code, COA Head, Product Name, Acquisition Date, FY, Cost Centre/Branch, Cost, Accum Dep, NBV, Voucher | SL per import_ref | Cost−Accum=NBV ±0.005; totals row |
| Partner ledger | Partner (6 legacy formats), Debit, Credit, Balance | legacy code/mobile/name | Debit−Credit=Balance ±0.005 |
| Legacy AR archive | Date, Journal Entry, Branch, Company, Created by/on, Debit, Credit, Balance | move ref | arithmetic + branch resolution |
| AP register | voucher ref, branch, debit/credit, balance | `AP:<voucher>` | register debits = payables |
| Bank history | title "Ledger Statement: <GL>", dated rows, balance | move name per GL | opening/closing tie |
| Party import | sheet kind corp/stbl/vendor/customer/contact; name, phone, email, district | `<ref>-<code>-<slug>` | BD mobile regex, dedup |
| Device bulk | serial/imei/mac/legacy_reference/model/purchase_date (aliases) | serial/IMEI uniqueness | ≤5,000 rows |
| COA loader | MD-035 four-block T-GG-SS-NNN CSV | code | sha256 + accounting equation |

### Appendix C — Access sheet (loopback-only, dev estate)

| Service | URL | Credentials |
|---|---|---|
| Odoo fix_real | http://127.0.0.1:8069/web/login | admin / admin (app); db-manager password in `.env` `ODOO_ADMIN_PASSWORD` |
| Odoo fix_dev | http://127.0.0.1:8090/web/login | admin / admin |
| Core PG | 127.0.0.1:5433 | fix / `.env` `POSTGRES_PASSWORD` |
| Keycloak | http://127.0.0.1:8080 | admin / `.env` `KEYCLOAK_ADMIN_PASSWORD`; realm 1000fix-dev |
| Portals | :3000–:3007 | per-portal synthetic users (see access-sheet memory); start: `npx next start --port N` from `apps/web/<name>` |
| Mailpit | http://127.0.0.1:8025 | — |
| Grafana | http://127.0.0.1:3300 | admin / `.env` |

### Appendix D — Script & evidence inventory (this engagement + precedents)

| Path | Purpose |
|---|---|
| `1000fix-2/_analysis/asset_takeon/profile_asset_xlsx.py` | file audit (sha256, structure, DQ) |
| `1000fix-2/_analysis/asset_takeon/probe_estate.py` | port/DB map + module/asset/GL/TB measurement |
| `1000fix-2/_analysis/asset_takeon/probe_wiring.py` | category accounts, crosswalk, batches, control balances |
| `1000fix-2/_analysis/asset_takeon/dq_asset_xlsx.py` | identity/coverage/crosswalk analysis |
| `1000fix-2/_analysis/asset_takeon/gen_inventory.py` | registry inventory generator |
| `1000fix-2/assets/evidence/*_2026-11-25.json` | measured evidence (all figures in this manual) |
| codebase `migrations/` | governed ETL pipeline + REHEARSAL.md + load_real_inventory.py |
| codebase `scratch/user_migration/`, `scratch/bank_master/`, `scratch/a08_drive/` | real-user / bank / COA loaders |
| codebase `_migration/backups/` | pre-change dumps |
| `1000fix-2/_migration/{scripts,staged,logs,evidence,backups}` | bank/branch/ledger take-on scripts + dry/apply log pairs |

### Appendix E — Sources

**Codebase (read this session):** `cd_fixed_asset_ext/models/{fix_fixed_asset,fix_asset_depreciation,fix_asset_master,fix_asset_common}.py` + `runbook.md`; `cd_gl_ext/models/{fix_gl_ext,fix_fiscal_year_ext,fix_ledger_takeon,fix_legacy_ledger,fix_ap_takeon,fix_bank_takeon,fix_chart_loader,fix_gl_recon,fix_gl_engine,fix_gl_chain,fix_gl_posting_control,fix_gl_dimension_pnl}.py`; `cd_billing_engine/models/{fix_ar_engine,fix_billing_engine}.py`; `cd_ap_ext/models/{ap_gl,fix_ap_ext,fix_ap_payment_run}.py`; `cd_cash_position/models/{treasury_common,fix_cash_position,bank_master}.py`; `cd_party_master/models/fix_party_import*.py`; `cd_device_registry/models/fix_device_bulk.py`; `cd_inventory/models/fix_stock_takeon.py`; `cd_p03_portal/controllers/{p03_generic_api,p03_gl_api,p03_finance_api,report_delivery,form_fields}.py` + `a08/{m19,m49,m50,m52,m20}.py` + `static/src/{p03_workspace.js,p03_workspace.xml,a08/m19.js,a08/m49.js}`; `docs/p04/migration-mig-standards.md`; `migrations/REHEARSAL.md`; `AGENTS.md`.

**Project documentation:** `project_content/12_Data_Migration_Content/DM-001…DM-014` (strategy, mappings, DQ standard, template pack, reconciliation spec, cutover checklist); `project-guide-doc/09_Data_Migration_and_Cutover/MG-001…MG-007`; `ERP system for 1000 fix/project_implementation_doc/12_Data_Migration_Runbook.md` (one-time migration; superseded operationally by this manual); `1000fix-2/` capability/implementation report pairs (bank, AR, AP, CIH, cheque, branch, warehouse, user).

**Internet (official Odoo documentation, fetched 2026-11-25):**
- [Export and import data](https://www.odoo.com/documentation/18.0/applications/essentials/export_import_data.html) — external-ID update rule, export-to-update, permanence warning, relational mapping.
- [Non-current assets and fixed assets](https://www.odoo.com/documentation/18.0/applications/finance/accounting/vendor_bills/assets.html) — depreciation methods, asset models, modify/dispose.
- [Year-end closing](https://www.odoo.com/documentation/18.0/applications/finance/accounting/reporting/year_end.html) — lock dates, hard lock, pre-close checklist, retained earnings.
- [Accounting & Invoicing index](https://www.odoo.com/documentation/18.0/applications/finance/accounting.html) — report catalogue (TB/BS/P&L/CF, partner ledger, ageing).

---

*Attestation: every screen id, endpoint, model, field, parameter and figure in this manual was read from the codebase or measured from the live databases on 2026-11-25 (evidence in `1000fix-2/assets/evidence/`). Projection figures are labelled as such. This manual is operational doctrine; the binding governance remains MIG-01…08 / DM / MG standards, which it implements rather than replaces.*
