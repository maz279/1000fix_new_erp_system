# ASSET LIST TAKE-ON — CAPABILITY & READINESS REPORT

| Field | Value |
|---|---|
| **Date** | 2026-11-25 |
| **Source file** | `C:\Users\DELL\Downloads\1000 fix assets\Asset_List_Compiled.xlsx` (131,072 bytes on disk; 1 sheet "Asset List") |
| **Source SHA-256** | `41a81e7a341a4a2ec23d45cb3288a0b22673dc648f6c6b38dc932aeeab4e4d68` |
| **Codebase audited** | `1000fix_new_erp_system/1000_fix_codebase` — `addons/domain/g_finance/cd_fixed_asset_ext` (M49, 19.0.1.2.1), `cd_gl_ext` (M19, 19.0.2.8.0), `addons/platform/cd_p03_portal` (19.0.1.5.3) |
| **Live DBs probed** | `fix_real` @ 127.0.0.1:8069 (uid 2 admin), `fix_dev` @ 127.0.0.1:8090; 8089 DOWN; core PG 5433 |
| **Method** | Zero-trust — every number below is parsed from the file, the database, or the code. Nothing simulated, nothing estimated. |
| **Evidence** | `1000fix-2/assets/evidence/{asset_xlsx_profile,estate_probe,wiring_probe,asset_dq}_2026-11-25.json` (+ summaries) |
| **Companion** | `DATA_UPLOAD_AND_UPDATE_OPERATIONS_MANUAL_2026-11-25.md` (the system-wide upload/update manual this report feeds) |

---

## 1. Executive Summary

**Three-part verdict:**

1. **Engine — CAPABLE.** M49 `cd_fixed_asset_ext` is installed on both databases at the current code version. It carries the full asset lifecycle (draft → active → disposed), dual-book depreciation (IAS 16 straight-line + ITA 2023 WDV memo book), seam-gated activation (BRU-FXA-01), frozen-terms discipline (BRU-FXA-10), and a register↔GL reconciliation that blocks period close (BRU-FXA-03). **But it has no bulk upload / take-on lane** — no wizard, no loader, no import screen. One must be built (this engagement, Phase 3).

2. **Estate — READY on `fix_real`.** All 7 seeded asset categories are **already wired** to posting accounts on journal **FA (id 59)**, and 5 of the 8 legacy asset GL codes in the file match those wired accounts exactly. **All 8 legacy asset GL codes exist and carry ZERO posted balance** — no double-count risk. The take-on contra `2.99.99.901` is live (Dr ৳66,695,194.57), 504 real employees and 152 branches are present, the 47-entry branch crosswalk parameter is live, the TB balances (Dr=Cr ৳519,179,027.45), and no fiscal lock is set. `fix_dev` is **not** a valid rehearsal target (categories unwired, real COA absent, 2 employees) — rehearsal runs on a **template copy of `fix_real`** instead (deviation from the generic plan, documented §7 R6).

3. **Data — NEAR-READY, 5 adjudications required.** 1,129 asset rows, **arithmetically perfect** (cost − accumulated = NBV on every row, 0 violations; FY labels 100% consistent with July–June acquisition dates). Control totals: **cost ৳80,519,165.70 / accumulated depreciation ৳35,045,408.32 / NBV ৳45,473,757.38**. Open items: 10 branch labels (94 rows) need crosswalk adjudication; 3 COA heads need new categories; 17 SL numbers are absent (filtered extract); the go-forward depreciation policy and take-on date need Finance sign-off.

**Recommendation:** build the governed `fix.asset.takeon` wizard on the proven `fix.ledger.takeon` pattern, adjudicate the five decisions (§7), rehearse on a `fix_real` template copy with a rehearsed rollback, then load `fix_real` behind an explicit approval gate with a pre-load dump.

---

## 2. What the file contains (measured audit)

### 2.1 Structure

One sheet **"Asset List"**, header on row 1, **1,129 data rows**, 12 columns, plus one trailing **"Total (filtered)"** row (excluded from the register; its values equal the sum of the 1,129 rows exactly — an internal control proof).

| # | Column | Semantics | Measured |
|---|---|---|---|
| 0 | SL | Legacy serial (row key) | 1,129 distinct, max **1146** → **17 numbers absent** (B1) |
| 1 | COA Code | Legacy asset **cost** GL code | 8 distinct; 17 rows blank (B2) |
| 2 | COA Head | Legacy asset class name | 9 distinct |
| 3 | Product Name (Short) | Asset description | 249 distinct |
| 4 | Acquisition Date | Real Excel dates | 2018-04-11 → 2026-11-22, 662 distinct |
| 5 | Financial Year | July–June FY label | 10 FYs (2017-18 → 2026-27); **0 mismatches** vs acquisition date |
| 6 | Cost Centre / Branch | Legacy branch / brand-desk label | 54 distinct; 44 resolve, **10 unresolved** (B4) |
| 7 | Cost (Tk) | Original cost | sum **80,519,165.70**; all > 0 |
| 8 | Accumulated Depreciation (Tk) | Position at extract | sum **35,045,408.32**; 0 ≤ accum ≤ cost on every row |
| 9 | Net Book Value (Tk) | Formula = Cost − Accum | sum **45,473,757.38**; identity holds ±0.005 on all 1,129 rows |
| 10 | Depreciation % | Formula = Accum / Cost | **fraction depreciated, NOT an annual rate** (B7) |
| 11 | Voucher / Move No | Legacy journal ref (JV-/PV-) | 995 distinct; **77 vouchers shared** by multiple assets (B6) |

### 2.2 Control totals (MIG-02 block)

```
source: Asset_List_Compiled.xlsx (1000 Fix legacy fixed-asset register, filtered extract)
extracted_at: 2026-11-25 (file mtime 2026-11-25 15:55)
record_count: 1129
value_total: cost 80,519,165.70 | accumulated 35,045,408.32 | NBV 45,473,757.38 (BDT)
checksum: sha256 41a81e7a341a4a2ec23d45cb3288a0b22673dc648f6c6b38dc932aeeab4e4d68
internal_proof: "Total (filtered)" row == sum of the 1,129 rows to the cent
```

### 2.3 Per-class totals (measured, proposed category crosswalk applied)

| Legacy head | COA code | Rows | Cost | Accum | NBV | Proposed category |
|---|---|---:|---:|---:|---:|---|
| Office Equipment | 100043 | 445 | 20,725,816.70 | 10,421,195.52 | 10,304,621.18 | **OFF** (wired ✓) |
| Computer & Computer Equipment | 100041 | 361 | 10,623,018.19 | 5,720,178.49 | 4,902,839.70 | **IT** (wired ✓) |
| Office Renovation | 100040 | 110 | 27,261,552.80 | 10,502,518.84 | 16,759,033.96 | **RENO** (new, G3) |
| Furniture | 100039 | 77 | 8,251,948.38 | 2,911,785.10 | 5,340,163.28 | **FURN** (wired ✓) |
| Establishment | 100042 | 68 | 3,925,602.00 | 2,187,627.92 | 1,737,974.08 | **EST** (new, G3) |
| Vehicle | 100044 | 20 | 7,375,400.00 | 2,495,391.38 | 4,880,008.62 | **VEH** (wired ✓) |
| Tools | 100803 | 19 | 1,470,636.11 | 620,273.74 | 850,362.37 | **TOOL** (wired ✓) |
| Office Decoration | *(blank)* | 17 | 342,891.00 | 124,722.41 | 218,168.59 | **RENO?** (adjudicate, B2) |
| Software and Software Development | 100804 | 11 | 542,300.52 | 61,714.92 | 480,585.60 | **SW** (new, G3) |
| Office Equipment *(1 row coded 100042)* | 100042 | 1 | *(included above)* | | | anomaly B3 |

### 2.4 Data-quality findings register

| ID | Finding | Impact | Disposition |
|---|---|---|---|
| **B1** | Filtered extract: SL 1–1146 with **17 absent**: 67, 196, 197, 257, 372, 373, 375, 376, 377, 453, 461, 479, 702, 708, 714, 747, 1099 | Register scope incomplete vs legacy | MIG-05: business confirms what was filtered out (disposals? fully-depreciated?) and either supplies the full register or signs the filtered scope |
| **B2** | SL 1010–1026 (17 rows, "Office Decoration") carry **no COA code** | Cannot resolve cost account from code | Head-based crosswalk assigns RENO (pending Finance confirmation); ৳342,891.00 cost |
| **B3** | 1 row: head "Office Equipment" but code **100042** (Establishment) | Code/head disagreement | Resolve by **code** (100042 → EST) unless Finance rules otherwise; flag on the batch line |
| **B4** | **10 branch labels (94 rows) unresolved** by name/crosswalk/aliases | Would quarantine at validate | Adjudication table §7 D2; extend `cd_gl_ext.legacy_ledger.branch_crosswalk` |
| **B5** | 3 heads (100040/100042/100804) have **no configured category** | Activation would fail closed | Create RENO/EST/SW categories (§7 D1) |
| **B6** | No asset tag/serial column; 77 vouchers shared across assets | Voucher is NOT a row key | Idempotency key = **SL within import batch**; external id `__asset_takeon__.a_<ref>_<SL>`; voucher kept as provenance |
| **B7** | No useful-life/rate column; "Depreciation %" = accum/cost; implied annual rates vary by class (median: IT 12.9%, OFF 11.9%, FURN 9.0%, RENO 9.0%, EST 8.2%, VEH 6.8%, TOOL 19.6%, SW 8.6%) | Go-forward monthly charge undefined | Finance decision D4: remaining life per class (engine re-spreads NBV over remaining months automatically — §3.2) |
| **B8** | Accumulated position is "as of" ~2026-11-22 (latest acquisition in file) | Take-on date must align | D5: takeon_date 2026-11-30, position accepted as the November opening; first new-system run = December 2026 |
| **B9** | 10 rows ≥99.9% depreciated (OFF 3, EST 3, Decoration 2, FURN 1, TOOL 1) | Near-zero NBV assets | Transfer as-is; engine's zero-charge skip handles them; no future charge |

**Clean proofs:** 0 arithmetic-identity violations; 0 negative/zero costs; 0 FY mismatches; 0 duplicate SLs; all crosswalk targets exist as real branches; all dates valid and ≤ today.

---

## 3. Codebase capability inventory (M49)

### 3.1 What exists

`addons/domain/g_finance/cd_fixed_asset_ext/` (manifest `x_module_id: M49`, `x_cd_id: CD-M49-01`, 19.0.1.2.1):

- **`fix.fixed.asset`** (`models/fix_fixed_asset.py:124`): company, operating_unit_id (**branch**), name, code (Asset Tag, `FA-` sequence, UNIQUE per company), category_id, custodian_id (hr.employee), seam_id, gross, salvage, life_months, purchase_date, depreciation_start (computed from purchase, editable), state draft/active/disposed, monthly_depreciation (computed), and **book values computed from POSTED events only** (`_position`, line 339): cost, accumulated_depreciation, impairment_total, book_nbv, revaluation_surplus, tax_accumulated, tax_wdv, book_months_done.
- **Guards:** `ASSET_TERMS` (gross, salvage, life_months, purchase_date, depreciation_start, category_id, currency_id, company_id) **frozen once active** (write refusal, lines 247–279); only draft assets deletable (`_unlink_only_drafts`); custodian/branch change only via `fix.asset.transfer`.
- **Activation (BRU-FXA-01, `action_activate` line 455):** draft only + category + gross > 0 + an **unconsumed M19 seam** (`fix.fixed.asset.seam`, defined in `cd_gl_ext/models/fix_gl_ext.py:1394`) whose posted journal item is a **debit on the category's asset account equal to gross ±0.005**. An asset cannot be typed into existence "active".
- **Depreciation engine** (`models/fix_asset_depreciation.py`): `fix.asset.depreciation.run`/`.line`, dual book; **one line per asset/book/month (DB constraint)**; `action_compute` skips assets already charged by a POSTED line for that month; `action_post` → one entry per journal, one Dr/Cr pair per **category AND branch**, every line dimensioned; tax book is memo-only and refuses unverified M51 rates; monthly cron **prepares, never posts**.
- **The go-forward charge** (`_book_amount`, fix_fixed_asset.py:409): `remaining_straight_line(carrying, salvage, life_months − posted_months)` — the carrying amount is **automatically re-spread over the remaining life**, last month takes the remainder so NBV lands exactly on salvage. This is the engine-native hook the take-on uses (§7 R2).
- **Reconciliation (BRU-FXA-03):** `_fix_register_gl_reconciliation` (line 593) — per category: register cost vs asset account, accum+impairment vs accumulated account, open CWIP vs CWIP account; variance > tolerance (default ৳1.0) **blocks period close**.
- **Lifecycle documents:** capex request/budget (DOFA-routed), CWIP entry + capitalisation, transfer (acknowledged), revaluation/impairment (CFO approve), disposal (gain/loss), verification campaigns, IFRS 16 leases, depreciation-change documents (the ONLY way to change frozen terms).
- **Workspace:** 21 models served (`controllers/a08/m49.py`), screens incl. **M49-register**, M49-categories, M49-dep, M49-gl-recon, M49-dualbook, M49-nbv; form **M49-form-asset** (tabs Asset / Cost & Depreciation); 8 report packs (`register_gl_reconciliation`, `movement_schedule`, `dual_book`, `nbv_by_category`, `capex_vs_budget`, `disposal_gains`, `lease_summary`, `tax_depreciation_rates`); 5 KPI tiles.
- **Runbook:** `cd_fixed_asset_ext/runbook.md` §4.2 month-end procedure.

### 3.2 What it does NOT have

- **No take-on/import lane** — no `source_file`, no `action_stage`, no batch model, no loader in `migrations/` or `scratch/` (grep-verified; `scratch/m47_seed_assets.py` seeds M47 facilities plant, a different model).
- **No `legacy_reference` field** on `fix.fixed.asset` (MIG-03 requires a permanent legacy key) — and no serial_number or vendor_id. Provenance today would have to live in the name or an external id alone.
- **No opening-accumulated-depreciation entry path** — the register derives accum from posted depreciation lines only; a take-on must therefore create posted opening lines whose GL is carried by the take-on entry (design §7 R2, verified against `_book_amount`/`action_compute`).

---

## 4. Live estate state (measured 2026-11-25)

### 4.1 Port / DB map

| Port | DB | Auth (admin) | Note |
|---|---|---|---|
| 8069 | **fix_real** | uid 2 ✓ | production-data estate |
| 8090 | **fix_dev** | uid 2 ✓ | synthetic/demo estate |
| 8089 | — | DOWN | former fix_real port, not running |

### 4.2 Module deployment (both DBs)

`cd_fixed_asset_ext 19.0.1.2.1`, `cd_gl_ext 19.0.2.8.0`, `cd_p03_portal 19.0.1.5.3`, `cd_billing_engine 19.0.2.11.0`, `cd_ap_ext 19.0.1.6.0`, `cd_cash_position 19.0.1.7.0`, `cd_tax_engine_bd 19.0.1.4.0`, `base_import 19.0.2.0` — all **installed**, matching the codebase manifests. `cd_user_migration` installed on fix_real only.

### 4.3 M49 category wiring on fix_real (journal **FA**, id 59)

| Category | Life (mo) | Salvage % | Asset account | Accum account | Expense account |
|---|---:|---:|---|---|---|
| IT | 36 | 0 | **100041** Computer & Computer Equipment (214) | 100607 Acc. Deprn. Computer HW & SW (275) | 500805 (515) |
| OFF | 60 | 0 | **100043** Office Equipment (216) | 100606 Acc. Deprn. Furniture & Office Equip (274) | 500804 (514) |
| FURN | 96 | 0 | **100039** Furniture (212) | 100606 (274) | 500804 (514) |
| VEH | 60 | 10 | **100044** Vehicle (217) | 100601 Acc. Depreciation Motor Vehicles (269) | 500803 (513) |
| TOOL | 60 | 0 | **100803** Tools (279) | 100609 Acc. Depreciation – Tools (620) | 500865 (517) |
| FIT | 60 | 0 | 100603 Leasehold Improvement (271) | 100602 Amortisation Leasehold (270) | 500801 (511) |
| ROU | 60 | 0 | 100801 Right of use Asset IFRS 16 (277) | 100802 (278) | 500851 (516) |

**All 8 legacy asset GL codes from the file exist on fix_real as `asset_fixed` accounts with 0.00 posted balance and 0 posted lines** (100039/100040/100041/100042/100043/100044/100803/100804). The asset GL is empty and awaiting take-on — **no double-count risk** (the standing rule from the bank take-on coordination notice).

### 4.4 Financial context (fix_real)

| Item | Measured |
|---|---|
| TB posted totals | Dr = Cr = **৳519,179,027.45** (35 posted moves) |
| MIG journal (id 42) | 1,837 posted lines, Dr ৳353,918,376.91 (prior take-ons) |
| AR control 100201 | Dr ৳153,859,759.09 |
| AP control 200101 | Cr ৳130,043,343.04 |
| **Contra 2.99.99.901** (Legacy Ledger Take-on Contra) | **Dr ৳66,695,194.57** |
| 2.99.99.902 (Unallocated Receipts) | Cr ৳68,172.00 |
| 300101 Data Migration Offset | Cr ৳255,345,740.58 |
| Company lock date | **None** (period open); `fix.period.close` rows: none |
| Employees / branches / OUs / partners | 504 active / 152 / 58 / 24,188 active |
| Existing batches | LEDGER-2026-11 **posted**; CASHCIH-2026-11 **posted**; CIH-2026-11 validated; LEGAR-2026-11 rolled_back; LEGBANK-IBBLR validated; 3 bank provenance batches staged/validated (deliberately unposted) |
| Control params | AR=100201, AP=200101, bank=100105, cash=100108, revenue=400100, vat_output=200902; branch crosswalk 47 entries, all targets exist |

**After the asset take-on** (arithmetic projection, to be re-measured post-load): contra 66,695,194.57 − 45,473,757.38 = **Dr ৳21,221,437.19** remaining; TB totals += ৳115,564,574.02 each side → **৳634,743,601.47**; BS fixed assets +৳45,473,757.38 NBV. The residual wash reclassifies to opening equity once the remaining subledgers are taken on (tier-1 rule, `fix_ledger_takeon.py:222–229`).

### 4.5 fix_dev contrast (why rehearsal moves to a fix_real copy)

Categories **unwired** (all posting fields None), legacy asset GL codes **absent** (generic 121000 chart), **2 employees**, no branch crosswalk parameter, no AR control parameter. Rehearsing the real file there would validate none of the real crosswalks. **Decision: rehearse on `CREATE DATABASE fix_asset_rehearsal TEMPLATE fix_real`** (throwaway-DB recipe, employee-migration precedent), then drop after restore-verify.

*Estate hygiene note (out of scope): fix_real's branch list contains ~60 "স্মোক ব্রাঞ্চ SMOKE…" synthetic leftovers and an "M30 AUDIT branch" — the crosswalk targets avoid them; flag to the platform steward.*

---

## 5. How top-class ERP systems handle this

| System | Fixed-asset take-on practice | Lesson applied |
|---|---|---|
| **SAP S/4HANA** | Legacy asset transfer via takeover values (acquisition cost + accumulated depreciation per asset) posted to reconciliation accounts; depreciation parameters per asset; a separate "legacy data transfer" date | Take on **cost AND accum per asset** with a single cutover date; never re-post history |
| **Oracle Fusion** | Assets ADI spreadsheet loader; opening balances as asset journals; retirement/reinstatement for corrections | Spreadsheet-driven bulk lane with validation before posting; corrections as new documents |
| **D365 F&O** | Data entities + staging tables; fixed-asset journal import; set-based processing | Stage → validate → post as one governed batch with a decision log |
| **Odoo core** | `base_import` with External IDs ("records that have already been imported are modified, instead of being created"; "imports are permanent and cannot be undone"); asset models + account-level automation; **no opening-accum import path** — assets are created from posted purchases | External-ID idempotency; the seam-gated activation is this estate's equivalent of "asset from a posted purchase"; the take-on entry IS the posted purchase |
| **Bangladesh context** | ITA 2023 Third Schedule reducing-balance classes; NBR Mushak registers | Dual book: IAS 16 accounting book posts GL; tax book is memo-only until the adviser verifies M51 rates |

**Binding internal standards:** MIG-01 (spec + control totals + mock + rehearsed rollback), MIG-02 (totals reconciled BEFORE acceptance), MIG-03 (permanent legacy reference), MIG-04 (production-sized dry run), MIG-05 (business decides DQ dispositions), MIG-06 (residency routing — no personal data in this file), MIG-07 (rollback rehearsed), MIG-08 (decommission after sign-off) — `docs/p04/migration-mig-standards.md`. Odoo official references: [Export and import data](https://www.odoo.com/documentation/18.0/applications/essentials/export_import_data.html), [Non-current assets](https://www.odoo.com/documentation/18.0/applications/finance/accounting/vendor_bills/assets.html), [Year-end closing / lock dates](https://www.odoo.com/documentation/18.0/applications/finance/accounting/reporting/year_end.html).

---

## 6. Gap register

| ID | Gap | Severity | Nature |
|---|---|---|---|
| **G1** | No asset take-on lane (wizard/loader/screens) | Blocker | Build (Phase 3) |
| **G2** | `fix.fixed.asset` lacks `legacy_reference` (MIG-03) + batch provenance | High | Add guarded fields `legacy_reference`, `takeon_batch_id` |
| **G3** | 3 categories missing for heads 100040/100042/100804 | High | Create RENO/EST/SW + wire accounts (D1) |
| **G4** | 10 branch labels unresolved (94 rows) | High | Crosswalk adjudication (D2) |
| **G5** | Go-forward depreciation policy undefined (no life/rate in file) | High | Finance decision (D4); engine re-spreads NBV over remaining life |
| **G6** | Opening accum has no entry path into the register | High | Engine-native design: posted opening run lines, GL carried by take-on entry (R2) |
| **G7** | Filtered scope — 17 SLs absent | Medium | Business confirmation (B1, MIG-05) |

---

## 7. Expert recommendations & decisions

### D1 — Category mapping (Finance to confirm)

**Recommended (faithful to the legacy chart):** create 3 categories so every legacy cost code posts to itself:

| New category | Code | Asset account | Accum account | Expense account | Life (D4) |
|---|---|---|---|---|---|
| Office Renovation | RENO | **100040** (exists, empty) | 100602 (shared with FIT) | 500801 | TBD |
| Establishment | EST | **100042** (exists, empty) | 100606 (shared with FURN/OFF) | 500804 | TBD |
| Software & Development | SW | **100804** (exists, empty) | 100607 (shared with IT) | 500805 | TBD |

Office Decoration (B2) → RENO pending confirmation; the 1 cross-coded row (B3) → EST by code. *Alternative (rejected):* consolidate into FIT/OFF/IT — simpler, but GL balances would land on different codes than the legacy TB, breaking code-by-code reconciliation.

### D2 — Branch adjudication (10 labels, 94 rows)

| Legacy label | Rows | Proposed target (exists in fix_branch) | Basis |
|---|---:|---|---|
| Aftabnagar (Coca-Cola) | 26 | **Decision needed** — no Aftabnagar branch exists; propose create "Aftabnagar Service Center" or map to HQ | brand-desk label |
| Huawei Branch | 24 | Huawei & other Mobile Service, Mirpur | brand desk exists |
| Honor Bogura ASC | 7 | Bogura Service Center | crosswalk pattern (Honor JFP ESP → Jamuna Future Park) |
| Samsung ASC Noakhali | 6 | Noakhali Service Center | CSC pattern |
| Samsung ASC Chattogram | 5 | চট্টগ্রাম শাখা (Chattogram) | Samsung CSP Dhaka → ঢাকা শাখা precedent |
| Xiaomi-Lohagara | 2 | Lohagara Service Center | exists |
| Honor Dinajpur ESP | 2 | Dinajpur Service Center | ESP pattern |
| Cox's Bazar CSC | 2 | Cox's Bazar Service Center | exists |
| Narayanganj CSC | 1 | Narayanganj Service Center | exists |
| Samsung ASC Rajshahi | 1 | রাজশাহী শাখা (Rajshahi) | CSC pattern |

Implementation: extend `cd_gl_ext.legacy_ledger.branch_crosswalk` (the canonical estate parameter) — no code change.

### D3 — Missing 17 SLs (B1)

Business confirms the filter criterion and either supplies the missing rows or signs the 1,129-row scope. The batch records the decision in its decision log (MIG-05).

### D4 — Go-forward depreciation policy (Finance to confirm)

The engine charges `(NBV − salvage) / remaining_months` automatically once opening lines exist. The take-on sets `life_months = remaining_months + 1` (the +1 is the opening month, counted as a posted month by `_book_amount`). Options per class: (a) adopt the seeded category lives as **remaining** life from cutover; (b) derive remaining life from the legacy implied rates (median table §2.4 B7); (c) supply the legacy depreciation policy document. **Salvage: ৳0 for all classes** unless Finance rules otherwise (VEH's seeded 10% default is overridden explicitly — the legacy figures show no salvage evidence). The decision is pinned per row on the batch line **before activation** (terms freeze).

### D5 — Take-on date

**2026-11-30** (month-end, FY 2026-27, period open, no lock). The file's position (~2026-11-22) is accepted as the November opening; **first new-system depreciation run = December 2026**. Opening tax-book lines mirror the book accum (assumption A2 — memo only; the tax adviser reconciles WDV later via M51 verified rates).

### R2 — The take-on lane (build spec, Phase 3)

`fix.asset.takeon.batch` / `fix.asset.takeon.line` in `cd_fixed_asset_ext`, modeled on `fix.ledger.takeon.batch` + `fix.device.bulk.load`:

- **Fields (batch):** name, source_file (Binary), source_filename, import_ref (default `ASSET-YYYY-MM`), takeon_date, company_id, state draft→staged→validated→posted→rolled_back, decision_log, counts/totals (computed), move_ids, run_ids.
- **Fields (line):** batch_id, sl, legacy_coa_code, legacy_head, product_name, acquisition_date, fy_label, branch_label, cost, accum_depreciation, nbv (computed check), dep_fraction, voucher, resolved category_id/branch (operating_unit)/custodian, life_months, salvage, state staged/quarantined/ready/posted/error, reject_reason, asset_id, seam_id, legacy_reference = `<import_ref>-SL-<sl>`.
- **action_stage:** openpyxl parse (header aliases), skip total rows, one line per asset.
- **action_validate:** arithmetic identity ±0.005; SL uniqueness (live external ids + intra-batch); category crosswalk (D1); branch resolution name → crosswalk → `LEGACY_BRANCH_ALIASES` (quarantine unresolved); custodian optional match; life/salvage policy present; **validate-in-savepoint** per row (device-bulk pattern).
- **action_post** (`require_takeon_authority` — Accounting Administrator; `assert_period_open`):
  1. **Entry 1 (acquisition, MIG journal, takeon_date):** one Dr line per asset on its category's asset account (= gross, branch+OU dimensions, name carries SL+voucher+product), one Cr contra line 80,519,165.70 → `post_with_dimensions`, source `suspense`, ref `<import_ref>-ASSET-TAKEON`.
  2. **Entry 2 (opening accum, MIG journal, takeon_date):** one Dr contra line 35,045,408.32, one Cr line per asset on its category's accum account (= legacy accum, branch dimensions), ref `<import_ref>-ASSET-ACCUM`.
  3. **Seams:** one `fix.fixed.asset.seam` per asset → its posted debit line (amount = gross, branch OU).
  4. **Assets:** create drafts (code = FA sequence, name = product, gross/salvage/life_months/purchase_date/depreciation_start = takeon month, category, branch, custodian, legacy_reference, takeon_batch_id) → `action_activate` each (consumes seam, publishes `asset.capitalized`).
  5. **Opening runs:** one book run + one tax run, period = takeon month, lines created under sudo (as the engine does) with amount = legacy accum, run marked posted via `_guarded()`, `move_ids` = Entry 2, note "GL carried by take-on entry — no second posting". The posted November line blocks any November re-charge (`action_compute` skip rule); December charges `(NBV−salvage)/remaining` natively.
  6. External ids `__asset_takeon__.a_<import_ref>_<SL>` (idempotent re-run = update, Odoo import doctrine).
- **action_rollback:** mirror both entries through the funnel; unconsume seams; reverse activation (guarded state→draft); unlink draft assets + opening runs/lines (sudo, as the engine writes them); external ids removed; batch → rolled_back. **Rehearsed, not just documented (MIG-07).**
- **Screens:** `M49-takeon`, `M49-takeon-lines`, form `M49-form-takeon` (3 tabs Source / Outcome / Decision Log, file upload) — the M19 wizard UI pattern; writable whitelist regenerated via `form_fields.py`.
- **Recon pack:** `asset_takeon_reconciliation` (batch totals vs posted GL vs register) + the existing `register_gl_reconciliation` as the close gate.

### R6–R10 — Execution sequence

- **R6 Rehearsal (MIG-01/04/07):** `CREATE DATABASE fix_asset_rehearsal TEMPLATE fix_real` → `-u cd_fixed_asset_ext` → full pipeline with the real file → control totals re-measured → register↔GL zero variance → TB balanced → December run computes correctly → **rollback executed** → baseline restored (restore-verify) → drop the scratch DB.
- **R7 Production gate:** present rehearsal evidence; **explicit user go-ahead**; `pg_dump fix_real` → `_migration/backups/fix_real_pre_asset_takeon_<ts>.dump`; load; re-measure everything.
- **R8 Post-load verification:** `register_gl_reconciliation` zero variance; TB Dr=Cr; per-code GL balances == per-class file totals; **in-app-browser visual inspection** of M49-register, M49-gl-recon, M19-tb/bs/pl (standing user directive).
- **R9 Go-forward:** December 2026 dual-book run (tax book only after M51 adviser verification); month-end per `runbook.md` §4.2.
- **R10 Wash narrative:** after assets, contra = Dr ৳21,221,437.19; remaining subledgers (stock etc.) then reclassify the wash to opening equity so it reads zero (tier-1 rule). The manual documents this as the opening-balance completion path.

---

## 8. Sources

**Local evidence (measured this session):** `assets/evidence/asset_xlsx_profile_2026-11-25.json` (file audit), `estate_probe_2026-11-25.json` (both DBs), `wiring_probe_2026-11-25.json` (category accounts, crosswalk, batches, control balances), `asset_dq_2026-11-25.json` (DQ + coverage); scripts in `_analysis/asset_takeon/`.

**Codebase:** `cd_fixed_asset_ext/models/{fix_fixed_asset,fix_asset_depreciation,fix_asset_master,fix_asset_common}.py`, `cd_gl_ext/models/{fix_gl_ext,fix_fiscal_year_ext,fix_ledger_takeon,fix_legacy_ledger,fix_ap_takeon,fix_bank_takeon,fix_chart_loader,fix_gl_recon}.py`, `cd_p03_portal/controllers/a08/{m49,m19}.py` + `static/src/a08/{m49,m19}.js`, `docs/p04/migration-mig-standards.md`, `project_content/12_Data_Migration_Content/DM-005/DM-012`, `cd_fixed_asset_ext/runbook.md`.

**Internet (official Odoo documentation):** [Export and import data](https://www.odoo.com/documentation/18.0/applications/essentials/export_import_data.html) · [Non-current assets and fixed assets](https://www.odoo.com/documentation/18.0/applications/finance/accounting/vendor_bills/assets.html) · [Year-end closing](https://www.odoo.com/documentation/18.0/applications/finance/accounting/reporting/year_end.html) · [Accounting index](https://www.odoo.com/documentation/18.0/applications/finance/accounting.html).

---

## 9. Rehearsal Record (2026-11-25, measured — MIG-01/02/04/07 satisfied)

**Environment:** `fix_asset_rehearsal` — a full restore of `fix_real` (pg_dump 52,873,713 bytes; backup extracted to codebase `_migration/backups/fix_real_pre_asset_takeon_2026-11-25.dump`). Modules upgraded: `cd_fixed_asset_ext` 19.0.1.3.0 + `cd_p03_portal`. **Commits:** `8a1c598c` (lane) + `7d5c3068` (rollback hardening + re-post path). **Tests:** full M49 suite **139/139 passed**; take-on suite 7/7 (incl. foreign-computed-run rollback and idempotent re-post).

| Phase | Measured result |
|---|---|
| **A — prerequisites** | Categories RENO/EST/SW created → 100040/100042/100804 (accum 100602/100606/100607, expense 500801/500804/500805, journal FA). Crosswalk 47→57 entries: 10 adjudicated additions + **9 stale-target repairs (G8)**. Baseline: TB Dr=Cr 519,179,027.45; contra Dr 66,695,194.57; 8 asset GL codes all 0.00; 0 assets |
| **B — stage/validate** | **1,129 staged / 1,129 ready / 0 quarantined.** Control totals exact: cost 80,519,165.70 / accum 35,045,408.32 / NBV 45,473,757.38 |
| **C — post** | 1,129 assets active via seams; entries **MIG/2026/11/0008 + 0009** (source `fixed_asset` through `post_entry`). **GL cost per code == file class totals (all 8 codes, incl. Decoration→100040 and the cross-coded row→100042); GL accum per code == file (5 accum accounts). `register_gl_reconciliation` abs variance = 0.00.** TB → **634,743,601.47 Dr=Cr** (= baseline + 115,564,574.02, the exact projection). Contra → **21,221,437.19** (exact projection). Opening runs book+tax posted (35,045,408.32 / 1,105 assets each; 24 zero-accum assets carry no opening line). November run computes **only the 24 zero-accum assets** — the 1,105 opening-line assets are skipped (no double charge). December sample charge 275.68 == (NBV−salvage)/(life−1) ✓ |
| **D — rollback** | Mirror entries posted; **assets 0, seams 0, opening runs 0, external ids 0; all 8 GL codes 0.00; contra restored 66,695,194.57**; lines ready again (1,129). The foreign *computed* November run's 24 lines cleared by the hardened rollback. **TB gross movement is append-only** (baseline + post + mirror = 750,308,175.49 Dr=Cr): rollback restores BALANCES, never erases posted history |
| **E — idempotent re-post** | `action_validate` from rolled_back → 1,129 ready → post → 1,129 active; recon variance 0.00; TB 865,872,749.51 Dr=Cr; contra 21,221,437.19; entries MIG/2026/11/0012 + 0013 |

**Evidence:** `assets/evidence/rehearsal_2026-11-25.json` (phases A–C), `rehearsal_rollback_2026-11-25.json` (D), `rehearsal_repost_2026-11-25.json` (E) + logs. Scripts: `_analysis/asset_takeon/{rehearse_asset_takeon,rehearse_rollback_continue,rehearse_repost}.py`.

### G8 (new) — stale branch-crosswalk targets

9 of the 47 crosswalk targets were **archived** by a prior branch consolidation (measured). Provisional repairs applied in the rehearsal (ALL require business ratification before production):

| Archived target | Provisional active target | Affected file labels |
|---|---|---|
| চট্টগ্রাম শাখা (Chattogram) | Chattogram Agrabad Service Center | Chattogram CSC, Xiaomi -Chattagram, Xiaomi-CTG EPZ (QSP) |
| খুলনা শাখা (Khulna) | Khulna City Service Center | Khulna CSC |
| ঢাকা শাখা (Dhaka) | 1000 FiX Head Office | Samsung CSP Dhaka |
| সিলেট শাখা (Sylhet) | Sylhet Zindabazar Service Center | Sylhet CSC |
| Mirpur Service Centre | 1000 FiX Head Office | Honor Mirpur ASC, Xiaomi -Mirpur-10 |
| রাজশাহী শাখা (Rajshahi) | Rajshahi City Service Center | Rajshahi CSC |

Alternative: reactivate the canonical geographic branches (they are the branch-master records) and keep the original crosswalk. **Business decides at the gate.**

---

## 10. Production Gate — adjudications required before the fix_real load

| # | Decision | Provisional rehearsal value | Status |
|---|---|---|---|
| D1 | Create RENO/EST/SW categories (accounts above) | created in rehearsal | **confirm** |
| D2 | 10 new branch labels (§7 D2) incl. **Aftabnagar (Coca-Cola) → HQ** (26 rows; no Aftabnagar branch exists — create one or accept HQ) | mapped | **confirm / rule Aftabnagar** |
| D3 | 17 missing SL numbers (B1) — filtered scope accepted? | 1,129-row scope | **business sign-off (MIG-05)** |
| D4 | Go-forward life policy: `life_months = category default + 1` (IT 37, OFF 61, FURN 97, VEH 61, TOOL 61, RENO 61, EST 97, SW 37), salvage 0 everywhere | applied | **Finance confirm or supply legacy policy** |
| D5 | takeon_date **2026-11-30**; position accepted as November opening; first new-system run December 2026 | applied | **confirm** |
| G8 | 9 stale crosswalk targets — repair vs reactivate canonical branches | repaired | **business ratify** |
| — | Tax book opening accum mirrors book accum (assumption A2); M51 rates need adviser verification before the tax run | applied (memo only) | **adviser item** |

**Production sequence (after gate):** fresh `pg_dump fix_real` → `-u cd_fixed_asset_ext,cd_p03_portal` on fix_real → apply ratified adjudications (categories + crosswalk parameter) → wizard stage/validate/post with `import_ref ASSET-2026-11` → re-measure all gates → IAB visual verification (M49-register, M49-gl-recon, M19-tb/bs/pl) → implementation log.

---

*Attestation: all counts, values, balances and coverage figures in this report were parsed from the source file, live database queries, or codebase reads on 2026-11-25. No value is estimated or simulated. Projection figures (§4.4 "after take-on") are labelled arithmetic projections and were CONFIRMED by the rehearsal (§9). Rehearsal adjudications are provisional and flagged for the production gate.*
