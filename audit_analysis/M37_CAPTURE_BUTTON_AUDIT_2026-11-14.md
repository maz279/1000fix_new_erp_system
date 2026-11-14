# M37 Product & Service Catalogue: data-capture audit, second pass

**Date:** 14 Nov 2026 · **Estate:** fix_real on port 8069 · **Status:** live since the user-approved 22:42 restart, commit 0ba4a6d0 (unpushed) · **First pass:** `M37_CAPTURE_BUTTON_AUDIT_2026-11-13.md` (live since 13 Nov)

## 1. The question

The user still saw M37 sub-module pages without a relevant data-capture button. The first pass (13 Nov) gave every page *something*, but four pages captured only through a chip or a different module's form, and three spec records had nowhere to be captured at all. Which pages should capture what, and does the estate have the record to capture?

## 2. What the spec says

Source: `1000fix_ERP_Module/03_Modules/C_Commercial_Pricing_and_Revenue/M37_Product_and_Service_Catalogue_Management.md`, §5 (FR-CAT-001…046), §8 (lifecycle), §9 (BRU-CAT-01…16), §10.1 (owned entities).

| # | Sub-module | What a person records (spec) | Spec entity |
|---|---|---|---|
| 2 | Typed Taxonomy | a hierarchy node (FR-004) | fix.catalogue.category |
| 4 | rBOM & SRT | rBOM lines (FR-022) **and** effective-dated standard repair times with governed re-baselining (FR-023/024, BRU-CAT-11) | fix.repair.bom.line, **fix.standard.repair.time** |
| 5 | Repair Operations | coded operation with repair level and SRT (FR-021/027, BRU-CAT-06) | fix.repair.operation |
| 7 | Product Hierarchy & Variants | attribute sets and variant axes (FR-005/006) | fix.catalogue.attribute |
| 9 | Fault Taxonomy | fault code **with brand claim-code mapping** (FR-042) | fix.fault.taxonomy, **fix.fault.brand.map** |
| 10 | Part Identity | part with provenance grade (FR-034), hazard class (FR-035), **cross-references and alternates** (FR-030) | fix.part.item, **fix.part.crossref** |
| 12 | Tax & Rev-Rec | the item's **VAT class, SD, HS code and revenue pattern**; no activation without them (FR-043, BRU-CAT-02) | fields on fix.catalogue.item |
| 13 | Lifecycle & Governance | lifecycle moves (FR-045) **and versioned channel publications** with completeness scoring (FR-044) | **fix.catalogue.publication** |

## 3. What the estate had (HEAD 6601a728)

Verified by running the engine's own `fregCreate` / `fregPanels` over the registry (node guard), by reading the models, and by a read-only query of fix_real.

| # | Page | Capture before | Defect |
|---|---|---|---|
| 2 | Typed Taxonomy | chip only | No "+ New": the page's own list refused it although the category form works |
| 4 | rBOM & SRT | + New rBOM Line | **No SRT record exists.** The SRT was one float on the item, editable in place by any officer on an Active item, against BRU-CAT-11 |
| 5 | Repair Operations | + Service Definition (labour) | **No repair level field anywhere**, so BRU-CAT-06 could not be checked |
| 7 | Product Hierarchy & Variants | chip only (`create: false`) | Nothing for attributes or variants |
| 9 | Fault Taxonomy | + New Fault Code | **No brand claim-code mapping** (FR-042) |
| 10 | Part Identity | + New Catalogue Item | **No cross-reference / alternate record**, no provenance grade, no hazard class |
| 12 | Tax & Rev-Rec | chip to M51's tariff master (`create: false`) | **The item had no VAT class, HS code, SD flag or revenue pattern.** The item form's "Statutory HS Code & VAT" tab was empty, and BRU-CAT-02 was checked nowhere |
| 13 | Lifecycle & Governance | nothing (`create: false`) | **No publication record**: FR-044 channel projections could not be captured |

Pages 1, 3, 6, 8 and 11 were correct after the first pass.

fix_real facts (read-only query, 14 Nov): 16,178 items (13,345 parts, 2,170 finished goods, 663 accessories), all Active, none with any tax or revenue class; 24 fault codes; 161 brands; 0 device models; 0 rBOM lines; 0 VAT treatments; 0 product attributes; the Catalogue Officer, Publisher and product-manager roles are held by **admin only**.

## 4. What was built

### Models (cd_catalogue 19.0.1.2.0, cd_service_order 19.0.2.1.0)

| Record | Rules enforced |
|---|---|
| **fix.catalogue.item** + `hs_code`, `vat_class`, `sd_applicable`, `revenue_recognition`, `repair_level`, `provenance_grade`, `hazard_class`, `hazard_handling` | **BRU-CAT-02**: Submit and Approve refuse an item without VAT class and revenue class. **BRU-CAT-06**: a Labour Only item needs a repair level and an SRT. **BRU-CAT-15**: a hazardous item needs its handling constraints (constraint). HS code must be 4–10 digits. On a decided (Active…) item a **blank** classification may be completed (all 16,178 migrated items are blank); a **set** one changes only by Revise. `standard_labour_time` is frozen once decided (BRU-CAT-11). |
| **fix.srt.baseline** (new) | Officer proposes with evidence (source; a calibration needs measured jobs and their average). A Catalogue Publisher who neither wrote nor proposed it approves; on its effective date (now, or the new daily cron) it supersedes the previous baseline and a general one moves the item's SRT. Proposed baselines are frozen; history is never deleted. |
| **fix.part.crossref** (new) | Parts/accessories only, not self, unique, quality note mandatory for aftermarket/compatible; officer role. |
| **fix.catalogue.publication** (new) | Publisher role. Saving computes the next version, item count, completeness and a SHA-256 content hash. A customer-facing channel carries only Published items and is **refused** while any lacks its Bengali name or category (FR-044, BRU-CAT-04). A snapshot: only its note changes; never deleted. |
| **fix.fault.brand.map** (new, cd_service_order) | One brand claim code per fault code per brand; captured as the Fault Code form's lines. |

ACLs, company / operating-unit isolation rules (estate generator) and the SRT cron are included.

### Workspace (cd_p03_portal)

| # | Page | Capture now |
|---|---|---|
| 2 | Typed Taxonomy | **+ New Catalogue Category** |
| 4 | rBOM & SRT | + New rBOM Line; **SRT Baselines** list (Propose / Approve / Reject) and **SRT Baseline** chip |
| 5 | Repair Operations | + New Service Definition (Labour Only) now carries **Repair Level**; SRT Baselines list and chip |
| 7 | Product Hierarchy & Variants | **+ New Product Attribute** (values as lines); Catalogue Category chip |
| 9 | Fault Taxonomy | + New Fault Code with **Brand Claim Codes** lines |
| 10 | Part Identity | + New Catalogue Item (Spare Part) with **provenance and hazard**; **Part Cross-References** list and chip |
| 12 | Tax & Rev-Rec | **+ Classify an Item (Tax & Revenue)**: pick an unclassified item, set HS / VAT / SD / revenue; M51 VAT Treatment chip kept |
| 13 | Lifecycle & Governance | **+ Publish to a Channel**; Channel Publications list |

The item, service and protection forms now show the classification fields (the empty "Statutory HS Code & VAT" tab is filled). The five new lists sit in the module's nav groups. Write whitelists regenerated (a04 and the one a02 line for `brand_code_ids`).

### Files

- `addons/platform/cd_catalogue/`: `models/fix_catalogue_item.py`, `models/fix_catalogue_spec_records.py` (new), `models/__init__.py`, `security/ir.model.access.csv`, `security/fix_isolation_rules.xml`, `data/ir_cron.xml`, `__manifest__.py`, `tests/test_m37_capture_live.py` (new), `tests/test_a04_catalogue_controls.py` (helper classifies items)
- `addons/domain/a_service_delivery/cd_service_order/`: `models/fix_fault_code.py`, `security/ir.model.access.csv`, `__manifest__.py`
- `addons/platform/cd_p03_portal/`: `static/src/a04/m37.js`, `controllers/a04/m37.py`, `controllers/a04/writable.py`, `controllers/a02/writable.py`, `tests/test_m37_capture_buttons.py`

## 5. Verification (private clone fix_test_m37, port 8076)

- **Node guard** `test_m37_capture_buttons.py`: 59 pass; **19 fail on HEAD** code (run with the HEAD m37.js / writable / controller swapped in).
- **Live ORM tests** `test_m37_capture_live.py` (non-admin officer / publishers / clerk), with the whole cd_catalogue suite: all pass.
- Regression of the suites that create or submit catalogue items: cd_catalogue, cd_service_order, cd_rate_card, cd_rental_asset M13 controls, cd_mdm_core behaviour: pass. Two cd_contract_core A04 checks fail **on HEAD too**: M36's flat forms and the "half of A04 forms have a vault" ratio (46/100 on HEAD; every form added here has a vault).
- **UI on the private server:** all 13 pages show a "+" capture; page 12 picked an item, saved HS 8473.30.00 / Standard VAT / On delivery, and the set values then render read-only; page 13 refused the portal channel ("nothing … Active and Published") and published POS v1 (4 items, 100 %, hash), after which Channel renders read-only. Through `/p03/model/write`: SRT baseline, cross-reference (refused without quality note, then saved), attribute with two values, fault brand code all saved; typed `item_count` and `state` refused; the proposer approving their own baseline refused (SoD).

### Full regression on the final commit

The whole `cd_p03_portal` suite plus the two cd_contract_core A04 suites ran from the shared checkout at 7cce4dc3 against a fresh fix_test clone with the modules upgraded: **4,060 passed, 4 failed, 257 skipped, 0 errors**. Each failure was re-checked on the pre-change commit 6601a728 and fails the same way there:

| Test | Cause | Same on 6601a728 |
|---|---|---|
| test_submodule_create_button::test_no_submodule_page_offers_another_records_button | M30/1 Branch Master declares `create: 'module'` (m30.js line 71, not touched here) | yes |
| test_a04_register_reconciliation::test_f2_no_flat_forms_remain | eight untabbed M36 forms | yes, same list |
| test_a04_zero_trust_certification::test_no_form_is_flat | the same M36 forms | yes, same list |
| test_a04_register_reconciliation::test_f5_document_vaults_exist_on_the_major_forms | under half of A04 forms have a document tab | yes: 46/100 before, 51/105 after (every M37 form added here has one) |

## 6. Deploy (user-approved, 14 Nov)

- Commit 0ba4a6d0 on `fix/a03-live-data-and-pending-work` (worktree commit, branch moved with `update-ref` from 6601a728; hooks green). Unpushed.
- Backup: `_migration/backups/fix_real_pre_m37_second_pass_2026-11-14.dump` (48.7 MB).
- Pre-restart drift check of every model file against fix_real: no missing column (only abstract mixins and attachment binaries).
- `-u cd_catalogue,cd_service_order,cd_p03_portal` on fix_real: 155 modules, no error.
- 8069 relaunched from the shared checkout (new PID at 22:42), `/web/login` 200.
- Read-only probe as a non-admin user (rolled back): new fields and the five models are readable; every new surface is served with its whitelist; a non-admin SRT create is refused (AccessError); the SRT cron is active; 16,178 items are offered by the page-12 pick.
- The production bundle `5acc34c` contains the new screens (`M37-form-publication`, `M37-form-taxclass`, `M37-srt-baselines`, `M37-part-xref`, `brand_code_ids`).

## 7. Owner decisions and remaining gaps

| Item | Status |
|---|---|
| Classify 16,178 live items (VAT class, revenue pattern, HS code) | **Owner data.** Not guessed. Migrated items stay sellable; only new submissions and re-approvals need the classes. |
| Catalogue Officer / Publisher / product-manager roles | admin only on fix_real; SoD makes approvals and SRT re-baselines need a **second** publisher |
| Device models (0 on fix_real) | Needed for model-specific SRTs, compatibility and cross-reference scope |
| Not built (spec §10.1) | rBOM per operation per model with criticality/alternate groups (FR-022), model compatibility matrix (FR-033), symptom→root-cause tree (FR-042 hierarchy), attribute sets per item class (FR-005 beyond Odoo attributes), subscription plan definitions (FR-038, M39's area), bitemporal change log (FR-046) |
