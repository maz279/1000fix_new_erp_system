# M37 Product & Service Catalogue: data-capture audit, third pass

**Date:** 19 Nov 2026 · **Estate:** fix_real on 8069, fix_dev on 8090 · **Branch:** `fix/m37-capture-pass3` (worktree `1000 fix/m37cap3-wt`) · **Earlier passes:** `M37_CAPTURE_BUTTON_AUDIT_2026-11-13.md`, `M37_CAPTURE_BUTTON_AUDIT_2026-11-14.md`

## 1. The question

The user still saw M37 sub-module pages without a relevant data-capture button. After the second pass every one of the 13 pages showed a "+ New" (re-confirmed: the engine's own `fregCreate` / `fregPanels`, run over the registry, give each page a capture). So the question this time was not *whether* a page has a button. It was whether the button opens a form that can hold **the record the spec says that page captures**.

## 2. Method

1. Read the spec, `1000fix_ERP_Module/03_Modules/C_Commercial_Pricing_and_Revenue/M37_Product_and_Service_Catalogue_Management.md`: §5 (FR-CAT-001…046), §9 (BRU-CAT-01…16) and §10.1 (owned entities).
2. Mapped each FR to the page that owns it (the registry's `freg` sub-modules).
3. For every page, compared the fields of the form its buttons open with the attributes the FR / entity names.
4. Read the models behind those forms, to tell "the form omits it" apart from "no model holds it".
5. Read-only counts on fix_real (§6).

## 3. Findings (before this pass, HEAD 742e46bc)

| # | Page | Button opened | What the spec says the page captures | Gap |
|---|---|---|---|---|
| 1 | Unified Item Master | Catalogue Item | FR-001…012 | none material |
| 2 | Typed Taxonomy | Catalogue Category (name, parent) | FR-004: bilingual, coded node; one commercial tree + presentation trees | **no Bengali name, code or tree type** |
| 3 | Service Definition | Service Definition (name, type, labour time) | FR-013…020: scope of work, inclusions, exclusions, prerequisites, deliverables, 9 delivery modes, standard duration per mode, skill + certification, repair warranty, consent flags, SLA template | **none of it existed, on the form or on any model** |
| 4 | rBOM & SRT | rBOM Line (operation, part, qty) | FR-022: per operation **per model**, with criticality and permitted alternates | **no model, criticality or alternate group** |
| 5 | Repair Operations | Service Definition (Labour Only) | FR-015/025/026, BRU-CAT-06: skill profile, fault → operation map, tooling | **no skill profile, so BRU-CAT-06 was only two-thirds enforced; no fault map, no tooling** |
| 6 | Kits & Bundles | Service Kit | FR-041: required/optional lines, substitution rules, explosion point | **none** |
| 7 | Product Hierarchy & Variants | Product Attribute | FR-005: attribute **sets per item class**, mandatory flag, per-channel requirement | **no attribute set** |
| 8 | Brand-Model-Device | Brand (with model lines) | FR-033, BRU-CAT-07: model compatibility matrix that blocks incompatible parts | **no matrix: nothing stopped an rBOM naming a part that does not fit**. The "Model Compatibility" KPI counted device models. |
| 9 | Fault Taxonomy | Fault Code (+ brand claim codes) | FR-042: symptom → category → fault → root cause, bilingual. FR-025: fault → operations | **no symptom, no root cause, no Bengali name, no operation map** |
| 10 | Part Identity | Catalogue Item (Spare Part) | FR-029: MPN, OEM reference | **the item form did not show the MPN; no OEM reference** |
| 11 | Contract & Protection Templates | Contract Template; Protection Product Template; Rental SKU | FR-037: protection cover (scope, exclusions, term, claim limit, eligibility). FR-038: subscription plans. FR-039: rental terms. FR-040: grade criteria and channels | **the protection form showed a labour time and observed repair minutes, and no cover**. **No subscription plan definition anywhere.** **The rental SKU had no minimum hire, deposit basis, condition or return criteria.** **Refurb grades could not be defined by any role** (ACL read-only, and no criteria or channel fields). |
| 12 | Tax & Rev-Rec | Tax & Revenue Classification | FR-043 | none (done in pass 2) |
| 13 | Lifecycle & Governance | Channel Publication | FR-044/045 | channel completeness ignored attribute requirements (FR-005 + FR-044) |

## 4. What was built

### Models

| Module (version) | Record / fields | Rules |
|---|---|---|
| cd_catalogue 19.0.1.4.0, `models/fix_catalogue_structure.py` (new) | item: `scope_of_work`, `inclusions`, `exclusions`, `prerequisites`, `deliverables`, `repair_warranty_days`, consent flags ×3, `tooling_required`, `workstation_class`, `manufacturer_part_number` (routed to the product), `oem_reference` | A service, inspection or labour item does not leave Draft without its scope of work and at least one delivery mode (FR-013/014/016). On an Active item a **set** scope, inclusion or exclusion changes only by Revise (BRU-CAT-12); a blank one may be completed (the 78 live service items). |
| | **fix.service.mode.duration** | One line per delivery mode (the nine of FR-014) with a positive standard duration; unique per mode; Catalogue Officer only. |
| | **fix.model.compatibility** | Part or operation ↔ model, compatible yes/no, fit note mandatory when not; one active row per pair. Declaring a part incompatible is refused while it sits on that model's rBOM. |
| | **fix.catalogue.attribute.set** (+ lines) | One active set per item class. A mandatory attribute "for every item" blocks Submit; a channel attribute makes the item incomplete for that channel's publication. Archived, never deleted. |
| | **fix.subscription.plan.def** | Billing frequency, commitment (≥ 1 month), included quantity and unit, overage unit; one per plan item; no price (BRU-CAT-01). |
| | product.category: `name_bn`, `code` (unique), `tree_type` | A node stays in its parent's tree. An item placed in a presentation category does not leave Draft (BRU-CAT-02). |
| cd_catalogue `fix_rbom.py` | rBOM line: `device_model_id`, `criticality`, `alternate_group` | **BRU-CAT-07**: the line's model must be one the operation declares, and a part declared incompatible with the model (or with any of the operation's models, for a general line) is refused. Unique per operation, part and model, including the blank-model twin. |
| cd_catalogue `fix_refurb_grade.py` | `cosmetic_criteria`, `functional_criteria`, four permitted-channel flags; officer write ACL | The officer defines criteria, warranty and channels. The grade code and M14's price multiplier are refused. |
| cd_catalogue `fix_rental_sku.py` | `min_hire_days`, `deposit_basis`, `condition_standard`, `return_criteria` | The minimum hire is not negative and not above the maximum. |
| cd_catalogue `fix_service_kit.py` | kit `explode_at`; component `is_optional`, `substitution` | — |
| cd_catalogue publication | channel completeness reads the attribute sets (FR-005 + FR-044) | — |
| cd_service_order 19.0.2.3.0, `models/fix_fault_taxonomy.py` (new) | **fix.fault.symptom**; **fix.fault.root.cause** (lines); fault code `name_bn`, `symptom_ids`, `operation_ids`; item `fault_code_ids` (same relation), `default_sla_policy_id` | Only repair operations (labour / service / inspection) resolve a fault. |
| cd_competency 19.0.0.5.0, `models/fix_catalogue_skill.py` (new) | item `required_competency_id`, `requires_certification` | **BRU-CAT-06** complete: a repair operation needs its skill profile before review. |
| cd_warranty_claims 19.0.2.3.0 | protection product `coverage_scope`, `exclusions` | — |

### Workspace (cd_p03_portal)

| # | Page | Capture now |
|---|---|---|
| 2 | Typed Taxonomy | Category form adds Bengali name, code and tree |
| 3 | Service Definition | The service form gains tabs **Scope of Work**, **Delivery Modes** (a grid of modes with durations, plus warranty and SLA), **Skill & Tooling**, and **Status & Consent** |
| 4 | rBOM & SRT | The rBOM form takes the model, criticality and alternate group; the list shows them |
| 5 | Repair Operations | The same service form: skill profile, certification, workstation, tooling, faults resolved, models |
| 6 | Kits & Bundles | Explosion point; optional and substitution per line |
| 7 | Product Hierarchy & Variants | **Attribute Sets** list + **Attribute Set** form (attribute lines) |
| 8 | Brand-Model-Device | **Model Compatibility Matrix** list + **Model Compatibility** form; the item form gets a Model Compatibility grid; the KPI now counts compatibility rows |
| 9 | Fault Taxonomy | The fault form adds Bengali name, symptoms, resolving operations and a root-cause grid; **Fault Symptoms** list + form |
| 10 | Part Identity | The item form shows the MPN and OEM reference |
| 11 | Contract & Protection | The protection template drops the labour fields. **Protection Product (Cover Terms)** chip opens M09's product, now with coverage scope and exclusions. **Subscription Plan Definitions** list + form. The rental SKU form takes its terms. Refurb grades open for definition (criteria, channels); code and multiplier are read-only. |

Write whitelists regenerated (a04, plus the a02 `fix.fault.code` entry). Isolation rules regenerated for cd_catalogue only; the generator's drift in 12 other modules belongs to peers and was not taken.

## 5. Verification

Private clone `fix_test_m37c3` (from fix_test_m25c2, upgraded with this pass's five modules and the five peer modules it lacked), private server on 8137.

- **Node guard** `cd_p03_portal/tests/test_m37_capture_buttons.py`: 71 pass. The 12 new checks **all fail on HEAD** (run with the HEAD registry, controllers and ACLs swapped in; the 59 earlier checks still pass there).
- **Live ORM tests**, new `cd_catalogue/tests/test_m37_capture_pass3.py` (20 tests: non-admin officer, publisher, clerk), with the whole cd_catalogue suite: **92 passed, 0 failed**. The suite caught one defect in this pass's own code, now fixed: a draft service's own delivery-mode lines counted as "references" and blocked its deletion.
- **Mutation check**: 19 mutants, each disabling one new rule (scope and delivery mode at Submit, BRU-CAT-12, commercial tree ×2, attribute set ×2, compatibility ×3, BRU-CAT-07 ×2, rBOM twin, plan uniqueness, mode duration, refurb fixed fields, hire period, BRU-CAT-06 skill, fault → operation, own-lines-not-references): **19/19 red**. The unmutated tests are 52/52 green under the same load.
- **Domain regression** (cd_service_order, cd_warranty_claims, cd_competency, cd_rate_card, cd_mdm_core): 800 tests; results in §5.1.
- **Headless walk (Playwright) on 8137**:
  - all 13 pages show their "+ New";
  - the five new chips (Attribute Set, Model Compatibility, Fault Symptom, Subscription Plan, Protection Product (Cover Terms)) open forms with inputs;
  - 12 lists and 13 new or changed forms render, with every new tab and section present;
  - a Fault Symptom saved through the form and was read back from the server.

  The only console error is a lazily loaded `web_tour` asset 500: the clone's attachment rows point at a filestore that was not copied, which is environmental.

### 5.1 Regression

- **cd_p03_portal suite + the two cd_contract_core A04 suites:** 6,447 tests, 8 failures in the first run. Two came from this pass and are fixed:
  - the fault form's tabs read 1, 2, 2, 3…; they are renumbered;
  - `test_a04_forms_show_their_children` recognised only `lines:` grids, so the new `grids:` (attribute lines, delivery modes, compatibility rows) read as "hidden". The guard now accepts `grids:` per named child field. The engine renders them, as M58 already uses.
- **Domain suites** (cd_service_order, cd_warranty_claims, cd_competency, cd_rate_card, cd_mdm_core): 800 tests. The 4 cd_mdm_core setup errors were serialization conflicts with the parallel portal run, and they pass when run alone.
- **The remaining failures are not this pass's.** Each one fails identically on the shared checkout's code (9ab2a035) against the same database:

| Test | Cause |
|---|---|
| test_a03_control_suite::test_every_routed_approval_refuses_to_be_pressed_directly | an integration-pattern go-live check fires first (peer) |
| test_m01_submodule_pages::…picked_from | M24-form-exception has no `pick` (M24) |
| test_m60_capture_buttons::test_the_new_file_loads_after_the_models_it_extends | M29's breach hand-off is imported after fix_m60_capture (M29/M60) |
| test_a04_register_reconciliation::test_f2 / zero_trust::test_no_form_is_flat | M36's untabbed forms |
| test_a04_register_reconciliation::test_f5 | under half of A04 forms carry a document vault (62/160). Every form added here has one. |
| cd_competency test_a09_m22_controls / round2 (4) | M22 dispatch surface and work-order flags (M22) |

### 5.2 Deployment (user-approved, 19 Nov 2026)

- **Landed** a1d445cb (code) and 1c234e57 (report) on `fix/a03-live-data-and-pending-work`, by fast-forward with a compare-and-swap ref update; **pushed** together with `fix/m37-capture-pass3`.
- **Backups:** `_migration/backups/fix_{real,dev}_pre_m37_capture3_2026-11-19.dump` (53 MB and 49 MB).
- **Upgrade:** `-u cd_catalogue,cd_service_order,cd_competency,cd_warranty_claims,cd_p03_portal,cd_partner` on fix_real, then on fix_dev. Both rc 0, with no ERROR and no missing table (155 and 151 modules). `cd_partner` (M40's) was in the version gap and is included by agreement with the M40 session.
- **Restart:** one restart of 8069 / 8090 at 13:24 UTC, done by the M40 session after both upgrades had exited. The gap check came back empty: 8069 = PID 60036, 8090 = PID 83644.
- **Live read-only checks, on both DBs:**
  - module versions 1.4.0 / 2.3.0 / 0.5.0 / 2.3.0;
  - the six new tables, 14 new ACL rows and 6 isolation rules exist;
  - the served bundle `01944e2` carries the new screens.
- **Live headless walk** on 8069 (fix_real) and on 8090 (fix_dev), signed in with the dev login, with no saves:
  - all 13 pages show their "+ New";
  - the five new chips open their forms;
  - 12 lists and 12 new or changed forms render their new tabs and sections;
  - **0 console errors** on either estate.

## 6. fix_real facts (read-only, 19 Nov)

16,178 items, of which 78 are service / inspection items and 0 labour (repair operation) items; 0 device models; 24 fault codes; 0 rBOM lines; 5 refurb grades; 0 rental SKUs; 0 kits; 0 protection products; 4 competencies; 1,357 categories. Nobody holds Catalogue Officer directly; admin holds Publisher, which implies Officer.

## 7. Owner decisions and remaining gaps

| Item | Status |
|---|---|
| Classify and define the 78 live service items (scope, delivery modes) and the 16,178 items' tax and revenue class | Owner data. Migrated items stay sellable; only new submissions and re-approvals need it. |
| Catalogue Officer / Publisher holders | Admin only. Approvals need a second publisher (BRU-CAT-05). |
| Device models | 0 on fix_real. Model-level rBOM, SRT and compatibility wait for them. |
| Estimate / issue blocking on incompatibility (FR-033 "block at estimate and issue") | M36 / M15 must call `fix.model.compatibility._incompatible`; the rBOM is guarded now. |
| M39 consuming plan definitions | `fix.subscription` still uses its own `plan` selection; switching it to `fix.subscription.plan.def` is M39's change. |
| Not built | rBOM header versioning (`catalogue.rbom_versioned`), fault-taxonomy versioning and publication (AUT-CAT-10), the bitemporal change log (FR-046 beyond chatter tracking), part supersession as its own dated record (FR-031 is covered by discontinue-with-successor). |
