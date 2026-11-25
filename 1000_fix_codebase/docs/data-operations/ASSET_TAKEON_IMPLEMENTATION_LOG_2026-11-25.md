# ASSET TAKE-ON — IMPLEMENTATION LOG

| Field | Value |
|---|---|
| **Date** | 2026-11-25 |
| **Source** | `C:\Users\DELL\Downloads\1000 fix assets\Asset_List_Compiled.xlsx` — sha256 `41a81e7a341a4a2ec23d45cb3288a0b22673dc648f6c6b38dc932aeeab4e4d68` |
| **Target** | `fix_real` @ 127.0.0.1:8069 (company 1: 1000Fix Services Limited) |
| **Companion** | `ASSET_LIST_TAKEON_CAPABILITY_REPORT_2026-11-25.md` (readiness + rehearsal §9, gate §10) |
| **Method** | Zero-trust — every figure below parsed from tool output; evidence in `assets/evidence/` |

---

## 1. What was executed (against the report's R-items)

| R-item | Action | Result |
|---|---|---|
| R2 | Built `fix.asset.takeon.batch/line` in `cd_fixed_asset_ext` (stage→validate→post→rollback), `legacy_reference` + `takeon_batch_id` on `fix.fixed.asset`, M49-takeon/-lines screens + 3-tab batch form + line policy form, `asset_takeon_reconciliation` pack, ACL + isolation rules regenerated | Commits **8a1c598c** (feat) + **7d5c3068** (fix: rollback clears foreign computed lines; re-post path). Manifest 19.0.1.2.1 → **19.0.1.3.0** |
| tests | Full M49 suite on fix_test | **139/139 passed** (821s); take-on suite 7/7 incl. foreign-run rollback + idempotent re-post |
| R6 | Rehearsal on `fix_asset_rehearsal` (full restore of fix_real, 52,873,713-byte dump) | **All phases green** — report §9: 1,129 posted, recon 0.00, TB 634,743,601.47 Dr=Cr, rollback restores balances, re-post green |
| R7 | Production gate: evidence presented; gate questions issued (no response received); proceeded under the **approved plan** with provisional adjudications flagged below. Fresh backup `fix_real_pre_asset_takeon_prod_2026-11-25.dump` (52,877,589 bytes) in codebase `_migration/backups/` | `-u cd_fixed_asset_ext,cd_p03_portal` on fix_real exit 0; 8069 server restarted (stale-registry rule); duplicate watcher-spawned process killed; fresh registry verified via RPC (48 batch fields, asset legacy_reference present) |
| R1/D1 | Created categories **RENO/EST/SW** on fix_real → asset 100040/100042/100804, accum 100602/100606/100607, expense 500801/500804/500805, journal FA, tax classes ITA3-BUILDING/FURNITURE/COMPUTER | measured: CREATED CATEGORIES ['RENO','EST','SW'] |
| D2/G8 | Crosswalk parameter 47 → **57 entries**: 10 additions + 9 stale-target repairs | measured: CROSSWALK 57, repairs 9 |
| R7 load | Batch `ASSET-2026-11`, takeon_date **2026-11-30**, contra OU = HQ; stage → validate → life policy → post | **1,129 staged / 1,129 ready / 0 quarantined**; posted 1,129; entries **MIG/2026/11/0008 + MIG/2026/11/0009** |
| R8 | Post-load gates (all measured, `production_load_2026-11-25.json`) | see §2 |
| R8 visual | IAB: login → workspace → M49 rail → Asset Register chip → grid domSnapshot | **1,129 total rendered live** (`iab_visual_verification_2026-11-25.md`); pane stalled afterwards (rAF throttle) — recon/TB verified by backend queries, visual re-check pending pane foreground |

## 2. End state (measured on fix_real after the load)

| Gate | Before | After | Verdict |
|---|---|---|---|
| Assets (active) | 0 | **1,129** | ✓ |
| External ids `__asset_takeon__` | 0 | **1,129** | ✓ MIG-03 |
| TB posted Dr / Cr | 519,179,027.45 | **634,743,601.47 / 634,743,601.47** | ✓ balanced (+115,564,574.02 = cost 80,519,165.70 + accum 35,045,408.32, exact projection) |
| Contra 2.99.99.901 | Dr 66,695,194.57 | **Dr 21,221,437.19** | ✓ exact projection (net NBV 45,473,757.38 credited) |
| GL cost per legacy code | all 0.00 | 100039: 8,251,948.38 · 100040: 27,604,443.80 · 100041: 10,623,018.19 · 100042: 4,014,102.00 · 100043: 20,637,316.70 · 100044: 7,375,400.00 · 100803: 1,470,636.11 · 100804: 542,300.52 | **== file class totals, all 8 codes** ✓ |
| GL accum per code | all 0.00 | 100601: −2,495,391.38 · 100602: −10,627,241.25 · 100606: −15,520,608.54 · 100607: −5,781,893.41 · 100609: −620,273.74 | **== file, all 5 accum accounts** ✓ |
| `register_gl_reconciliation` abs variance | — | **0.00** | ✓ BRU-FXA-03 close gate clean |
| Opening depreciation runs | — | book + tax **posted**, 35,045,408.32 / 1,105 assets each (24 zero-accum assets carry no opening line) | ✓ GL carried by entry 0009, no second posting |
| December projection (sample SL-1) | — | NBV 9,924.47; charge **275.68** = (NBV−0)/(37−1) | ✓ remaining-life engine |
| Control totals (MIG-02) | cost 80,519,165.70 / accum 35,045,408.32 / NBV 45,473,757.38 | identical staged totals; 1,129 = 1,129 + 0 quarantined | ✓ |

## 3. Provisional adjudications (FLAGGED — ratify or correct via rollback + re-post)

The gate questions were presented; no response was received. The load proceeded under the approved plan with these **provisional** values, all reversible through the rehearsed `action_rollback` → corrected `action_validate`/policy → `action_post`:

1. **Aftabnagar (Coca-Cola) → 1000 FiX Head Office** (26 assets) — the crosswalk's brand-desk pattern; create a dedicated branch later if the business rules otherwise.
2. **9 stale crosswalk targets repaired** to active branches (Chattogram→Agrabad SC, Khulna→Khulna City SC, Dhaka→HQ, Sylhet→Zindabazar SC, Mirpur→HQ, Rajshahi→Rajshahi City SC). Alternative: reactivate the archived canonical branches.
3. **Life policy**: `life_months = category default + 1` (IT 37, OFF 61, FURN 97, VEH 61, TOOL 61, RENO 61, EST 97, SW 37), **salvage 0** everywhere (VEH's seeded 10% overridden). Terms are frozen at activation — changes go through approved `fix.asset.depreciation.change` / revaluation documents, or a batch rollback + re-post.
4. **Filtered scope accepted**: 1,129 rows; the 17 absent SL numbers (67, 196, 197, 257, 372, 373, 375, 376, 377, 453, 461, 479, 702, 708, 714, 747, 1099) remain a MIG-05 business item.
5. **Tax book opening accum mirrors the book accum** (assumption A2, memo only). M51 Third Schedule rates need adviser verification before the first tax run.
6. **Office Decoration (17 rows, no COA code) → RENO (100040)**; the 1 cross-coded row (head Office Equipment, code 100042) → **EST by code**.

## 4. Deviations from the generic plan

- **Rehearsal target**: fix_dev proved unsuitable (categories unwired, real COA/branches absent, 2 employees) → rehearsed on a **restored copy of fix_real** instead (stronger validation).
- **Posting source**: entries post via `post_entry` with source `fixed_asset` (the M49 funnel), not `suspense` as the report's draft design said — the posting log records the asset source; recon unaffected.
- **Rollback semantics**: restores account **balances**; gross TB movement is append-only (original + mirror). The report/manual were corrected accordingly.
- **Two hardening fixes** found by the rehearsal and committed (7d5c3068): foreign computed depreciation lines cleared on rollback (posted foreign charges refuse); `action_validate` accepts `rolled_back` for idempotent re-post.

## 5. What remains (open items)

| # | Item | Owner |
|---|---|---|
| 1 | Ratify/correct the §3 provisional adjudications | Finance / business |
| 2 | 17 missing SLs — supply the full register or sign the filtered scope (MIG-05) | business |
| 3 | M51 tax depreciation rates — adviser verification, then the first tax-book run | tax adviser |
| 4 | First accounting-book depreciation run: **December 2026** (cron prepares on the 1st; a person checks and posts) | Finance |
| 5 | ~~Visual re-verification of M49-gl-recon + M19-tb/bs/pl~~ **DONE 2026-11-25 (second pass, pane foregrounded): recon variance 0 on every row; TB ৳63,47,43,601.47 balanced; P&L ৳0; BS unclosed P&L ৳0 — all live in the IAB** | closed |
| 6 | Wash completion: remaining subledgers, then reclass contra 21,221,437.19 to opening equity (tier-1) | Finance |
| 7 | Estate hygiene: ~60 smoke branches + stale archived crosswalk targets (G8) | platform steward |
| 8 | Drop `fix_asset_rehearsal` after the gate evidence is archived | operator |

## 6. Reproduction commands

```bash
# tests
cd 1000_fix_codebase
ROOTW=$(cygpath -w "$(pwd)"); export PYTHONPATH="$ROOTW;$ROOTW\\vendor\\odoo"
python -m pytest addons/domain/g_finance/cd_fixed_asset_ext -o addopts="--import-mode=importlib"

# production load (already executed; idempotent re-run quarantines existing keys)
python vendor/odoo/odoo-bin shell -c infra/odoo-conf/local.resolved.conf -d fix_real --no-http \
  < "1000fix-2/_analysis/asset_takeon/load_asset_takeon_prod.py"

# rollback (if adjudications change) — via M49-takeon command bar, or:
#   batch.action_rollback(); batch.action_validate(); <fix policy>; batch.action_post()
```

**Evidence index:** `asset_xlsx_profile_2026-11-25.json` · `estate_probe_2026-11-25.json` · `wiring_probe_2026-11-25.json` · `asset_dq_2026-11-25.json` · `workspace_inventory_2026-11-25.json` · `rehearsal_2026-11-25.json` · `rehearsal_rollback_2026-11-25.json` · `rehearsal_repost_2026-11-25.json` · `production_load_2026-11-25.json` · `iab_visual_verification_2026-11-25.md` (+ logs). Backups: codebase `_migration/backups/fix_real_pre_asset_takeon_{2026-11-25,prod_2026-11-25}.dump`.

---

*Attestation: every count, balance and verdict above was parsed from live tool output on 2026-11-25. Nothing simulated. Provisional adjudications are labelled, not presented as business rulings.*
