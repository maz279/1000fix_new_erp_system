# M49 Fixed Assets & Capex: Sub-Module Capture Audit (2026-11-17)

**Trigger.** The user observed that not every M49 sub-module page has a relevant data-capture button.

**Sources**
- Spec: `1000fix_ERP_Module/03_Modules/G_Finance_and_Treasury/M49_Fixed_Assets_and_Capital_Investment.md`. Sections used:
  - §5: FR-FXA-001 … 034;
  - §8: the capital request, asset and verification lifecycles;
  - §9: BRU-FXA-01 … 26;
  - §10.1: the 24 owned entities;
  - §13: roles.
- Research: `audit_analysis/A08_FINANCE_RESEARCH.md` (M49 table).
- Code:
  - `cd_p03_portal/static/src/a08/m49.js`: the page registry (8 sub-module pages, 21 screens in the navigation);
  - `cd_p03_portal/controllers/a08/m49.py`: surfaces, reports and KPIs;
  - `cd_fixed_asset_ext/models/*.py`: the 15 M49 models.
- Live data (fix_real, read-only count on 17 Nov):
  - 7 asset categories and nothing else: 0 assets, capex requests, budgets, CWIP, depreciation runs, revaluations, disposals, transfers, verification campaigns and leases;
  - 4 users hold Accounting Manager directly, so the two-person steps below can be staffed.

## 1. What was there (HEAD 3efdab37)

The pages were evaluated with the engine's own `fregCreate` / `fregPanels` in node, which is how the browser decides what a page shows.

| Page | Sub-module | "+ New" | Chips | Defects |
|---|---|---|---|---|
| 1 | Capex & Approval | Capex Request | Capex Request | The page lists the **Capital Budget**, but no chip opens its form (the form existed). There is no **capital project** grouping requests under one budget and owner (FR-FXA-006 P1), and no **post-implementation review** (FR-FXA-007, BRU-FXA-24 class H). |
| 2 | Register & Capitalisation | Asset Capitalisation | Asset Capitalisation, Lease Contract | The page lists the **Asset Categories**, but no chip opens their form (the form existed). The **Lease Schedules** list sat on no page. |
| 3 | **Componentisation** | CWIP Entry | **none** | The page is named after componentisation, but **no component existed** (FR-FXA-014): a CWIP project capitalised into one asset with one life, and nothing could be split. FR-FXA-016 ("one or more active assets ... by an approved basis") was not possible. |
| 4 | Dual-Book Depreciation | Depreciation Run | **none** | No chip for the Depreciation Run. **No life or residual change** (FR-FXA-023 P0, BRU-FXA-10 class H): the code froze an in-service asset's life "until that document exists", and it never did. **No suspension** (FR-FXA-024). The Register-to-GL reconciliation sat on no page. |
| 5 | Revaluation & Impairment | Revaluation / Impairment | Revaluation / Impairment | Only a loss could be recorded. **The assessment itself was never recorded** (FR-FXA-032, BRU-FXA-26 class H): this means the annual review of indicators, the test, and above all the conclusion that nothing is impaired. |
| 6 | Transfers & Custody | Transfer | Transfer | No defect. |
| 7 | Verification & Tagging | Verification Campaign | **none** | No chip for the Campaign. The campaign form had **no branch scope**, although the list shows one. **No variance investigation** (FR-FXA-030 P0, BRU-FXA-15/16 class H): a missing or misplaced asset could only be marked found or missing by hand. It had no explanation, no proposed register correction and no approval. |
| 8 | Disposal | Disposal | Disposal | No defect. A write-off already needs its incident reference and carries the insurance claim. |

Guard `cd_p03_portal/tests/test_m49_capture_buttons.py` on HEAD: **18 of 40 tests fail**. The failures cover pages 1, 2, 3, 4, 5 and 7, the creatable lists with no capture, the orphan screens, the five missing records, and the category, campaign and capex fields.

## 2. What was built

### Backend: `cd_fixed_asset_ext` 19.0.1.1.0, new file `models/fix_asset_capture.py`

Every decision is taken by an accounting manager who did not raise the document (`check_sod`). Stamps and derived figures are guarded fields, never typed. Nothing is deleted, except a component line of an open CWIP project.

| Page | Record | Holds | Rules |
|---|---|---|---|
| 1 | `fix.capital.project` (FR-FXA-006/007) | Type (branch opening, workshop, IT, fleet, other), branch, accountable owner, total budget, schedule and business case. It also holds the approved capex, actual cost and headroom of its requests, and the post-implementation review: realised benefit, conclusion, documents, and the actual cost and variance stamped at review. | A manager other than the owner approves it. The budget, owner and scope are then fixed. **A capex request naming the project is refused at submission when approved and pending requests would exceed the project budget.** Completion waits for requests still in approval. At or above the review threshold (config key, 5,000,000 by default), a review is due a set number of days after completion (config key, 180 by default), and an overdue review is flagged on the list. **The owner never records the review** (BRU-FXA-24). |
| 3 | `fix.cwip.component` (FR-FXA-014/016) | Component, category (empty: the project's), share of cost, useful life (empty: the category's), residual percentage, and the resulting asset. | Shares total at most 100%, and exactly 100% to capitalise. **Capitalisation now creates one asset per component**: the cost is allocated by share, with the last component taking the rounding, and there is one entry with a debit per component's asset account. A category flagged **Componentisation Required** refuses a project with no components. A component is fixed once its project is capitalised. |
| 4 | `fix.asset.depreciation.change` (FR-FXA-023/024, BRU-FXA-10) | The kind of change (useful life / residual value, suspend, reinstate), the new life and residual, the justification, the life and residual before, and "applies from". | Approved by an accounting manager who did not request it. **Prospective only**: the new life must exceed the months already charged, and the residual must lie between 0 and the net book value. The book charge is the remaining carrying amount over the remaining months, so posted months are untouched. Validity is re-checked at approval, because depreciation may have run in between. **Suspension stops the accounting-book charge only.** The run skips the asset and Accrue Month refuses it, while the tax book carries on (BRU-FXA-12). A submitted change is frozen. |
| 5 | `fix.asset.impairment.assessment` (FR-FXA-032, BRU-FXA-26) | Scope (one asset, or a branch as the cash-generating unit), date, occasion (annual or trigger event), six IAS 36 indicators with evidence, conclusion, recoverable amount and test basis. On confirmation it stamps the carrying amount, the loss and the impairment raised. | **It is recorded whether or not an impairment results.** If an indicator is ticked, the conclusion must be a tested one. A manager other than the assessor confirms. A tested conclusion must agree with the stamped carrying amount, and the test needs its basis. **An impairment of one asset raises the draft IAS 36 document** on page 5, which the CFO tier approves and posts as before. A branch-level impairment must be allocated asset by asset. |
| 7 | `fix.asset.verification.variance` (FR-FXA-030, BRU-FXA-15/16) | The variance investigated (missing, found at another branch, or not in the register), investigator, findings, proposed correction and incident reference. On approval it stamps the transfer or write-off raised. | Only a variance result can be investigated, with one investigation per result. Each variance has its own set of allowed corrections. A write-off needs its incident reference (BRU-FXA-19). **Neither the counter nor the proposer approves.** Approval applies the correction: a "located" result is corrected to found, or a draft **transfer** to the branch where the asset was found, or a draft **write-off disposal**, is raised for its own approval. |

The existing models gained:
- On `fix.fixed.asset`: `depreciation_suspended` and `cwip_component_id` (both guarded), and the depreciation-change history.
- On `fix.cwip.entry`: its components, their share total, and the assets it capitalised into. `action_capitalise` now builds its assets from `_capitalisation_parts`.
- On `fix.capex.request`: `project_id`. It is pinned by the routed approval and locked after submission.
- On `fix.asset.category`: `componentisation_required`.
- On `fix.asset.verification.line`: a readable name (campaign / tag / result). Without it the variance picker would have shown `fix.asset.verification.line,12`.

Security and data:
- ACLs: the read-only finance group reads, accountants and managers write, and nobody deletes (except component lines).
- Company and branch isolation rules come from `generate-isolation-rules.py`. Only the M49 file was kept; the generator's pre-existing drift in four other modules was reverted.
- Four sequences: CPJ/, ADC/, AIA/, AVV/.

### Workspace: `m49.js`, `controllers/a08/m49.py`, `writable.py`

- Five new lists, on their pages and in the navigation:
  - Capital Projects;
  - CWIP Components;
  - Life, Residual & Suspension Changes;
  - Impairment Assessments;
  - Verification Variances.
- The new lists' actions are served, and their pickers are restricted: open CWIP, assets in service, variance results.
- Five new forms. Capital Project, Impairment Assessment and Verification Variance are tabbed (AGENTS.md).
- Changes to existing forms:
  - the Asset Category form gains **Capitalised as Components**;
  - the Verification Campaign form gains its **Branch Scope**;
  - the Capex Request form gains the **Capital Project**;
  - the CWIP form shows its components' share;
  - the Asset form and Register list show **Depreciation Suspended**.
- Orphan screens placed: Lease Schedules on page 2, Register-to-GL Reconciliation on page 4.
- `writable.py` was regenerated with `form_fields.py --a08`; only the M49 entries changed.

| Page | "+ New" | Chips after |
|---|---|---|
| 1 Capex & Approval | Capex Request | Capex Request, **Capex Budget**, **Capital Project** |
| 2 Register & Capitalisation | Asset Capitalisation | Asset Capitalisation, **Asset Category**, Lease Contract |
| 3 Componentisation | CWIP Entry | **CWIP Entry**, **CWIP Component** |
| 4 Dual-Book Depreciation | Depreciation Run | **Depreciation Run**, **Depreciation Change** |
| 5 Revaluation & Impairment | Revaluation / Impairment | Revaluation / Impairment, **Impairment Assessment** |
| 6 Transfers & Custody | Transfer | Transfer |
| 7 Verification & Tagging | Verification Campaign | **Verification Campaign**, **Verification Variance** |
| 8 Disposal | Disposal | Disposal |

## 3. Evidence

| Check | Result |
|---|---|
| Guard `cd_p03_portal/tests/test_m49_capture_buttons.py`. Node runs the engine's own `fregCreate`/`fregPanels` over the real registry. | **HEAD 3efdab37: 18 of 40 fail.** After: **40/40.** |
| Live tests `cd_fixed_asset_ext/tests/test_m49_capture_live.py`. They run as non-admin finance users on a private clone `fix_test_m49` (`-u all`, 0 errors), through the P03 write and action endpoints where a form exists. | **8/8.** |
| Mutation check: each rule removed in turn. The rules were: change approver SoD, suspension skip in the run, project budget cap, counter barred from deciding, impairment raising its document, components at capitalisation, prospective-life check. | **7 of 7 mutations turned the live tests red.** |
| Regression on the same clone, no server attached: `cd_fixed_asset_ext`, `cd_asset_finance_hse_bridge`, `cd_ap_ext`, and the `cd_p03_portal` a08 / estate / capture / whitelist / writable / KPI / report-export tests. | **2,802 tests: 1 failure, 33 skipped.** The failure was `test_a08_m49::test_form_chips_map_to_real_models`: the five chips whose forms already existed were missing from `FORM_MODELS`. Fixed; the file reruns 11/11. All 33 skips are "carries no workflow-controlled fields". |
| UI walk on a private server (port 8079, `?debug=assets`). | All 8 pages show the "+ New" and the chips in the table above. A Capital Project was saved from the page 1 chip's tabbed form: CPJ/2026/0001, Draft, review not required below the threshold. No console error except the pane's known CSRF 400 at sign-in. |
| `generate-isolation-rules.py`, `form_fields.py --a08`, pinned ruff 0.8.4 | Only the M49 entries changed. Format and lint are clean. |

Two defects were found only by the live run and fixed before the evidence above:
- The guarded mixin refuses a generated reference or variance type passed in `create()`. These are now written through the guard after the create.
- The workspace answers a create with `{id, display_name}`, so the tests check for that.

## 4. Not built here (owner decisions or other modules)

- **Stock-to-asset conversion** (FR-FXA-018 P0, BRU-FXA-20/21). This is an M15 inventory movement at M15's value; it needs the M15 hand-off design. Not built.
- **Asset tag printing** (FR-FXA-019): barcode and QR labels for the branch printers. This is a report or print job, not a capture. The tag itself already exists (the asset code), and scanning works through Record Scanned Tag.
- **Capitalisation threshold and manual-creation reason code** (FR-FXA-010/013): these need the CFO's threshold and reason list (Q-06 family). A manual asset is still only put into service from its M19 seam, CWIP or lease (BRU-FXA-01).
- ~~**Insurance coverage register**~~ and ~~**componentising an asset acquired through the M19 seam**~~: both built afterwards, on the user's request. See §6.
- **Depreciation method change** (reducing balance in the accounting book): the book is straight-line only. The change document covers life and residual.
- **Capital project cash view (M50) and the CWIP ageing escalation** (FR-FXA-004/017) are reports and automations, not captures.

## 5. State

- Built and tested in worktree `m49cap-wt`. Fix commit 7b681233 is on the working branch `fix/a03-live-data-and-pending-work`, fast-forwarded from 23cc93ac (the M47/M48 tip). **Not pushed.**
- **Deployed on fix_real (8069) on 17 Nov 2026**, on the user's approval:
  1. Backup `fix_real_pre_m49_capture_2026-11-17.dump` (49.4 MB, reads back with pg_restore).
  2. `-u cd_fixed_asset_ext,cd_p03_portal` on fix_real exited 0. cd_fixed_asset_ext is now 19.0.1.1.0, and all 5 new models are registered.
  3. Working branch moved by compare-and-swap; the shared checkout was refreshed and is clean.
  4. Before the restart, all 83 installed cd_ modules matched their code. 8069 was restarted once: PID 7484 became 30868 (supervisor 23964) after 10 s. The log shows 155 modules loaded and no errors.
- Verified on the live server: all 5 new lists, plus capex, CWIP and the asset register, are served. Bundle 5a23f3f carries the 5 new screens and their forms.
- fix_real holds **no** fixed assets, CWIP entries, capex requests or projects, so every M49 list starts empty. That is a data take-on question for the owner, not a defect.
- **fix_dev (8090) upgraded the same day**, on the user's request:
  - Backup `fix_dev_pre_m49_capture_2026-11-17.dump` (40.6 MB).
  - Before the upgrade, the asset module was fix_dev's only version gap across its 80 installed cd_ modules. `-u` exited 0.
  - 8090 restarted: PID 24872 became 35160 (supervisor 37700) in 10 s, with no log errors.
  - The same 8 lists are served, and the bundle is 5a23f3f, the same as fix_real.
- Someone must set two figures in the config keys: the review threshold (`cd_fixed_asset_ext.capital_project_review_threshold`, default 5,000,000) and the review period (`cd_fixed_asset_ext.capital_project_review_days`, default 180). They are the CFO's to set.

## 6. Gaps closed afterwards (same day, user: "Build the two gaps")

Two of the §4 items were capture gaps that needed no owner decision. Both are built in `cd_fixed_asset_ext` 19.0.1.2.0, new file `models/fix_asset_gaps.py`.

### Page 3: components of an asset that comes in through the M19 seam (FR-FXA-014, IAS 16.43)

- **New record `fix.asset.component`**, recorded against a registered asset that is not yet in service:
  - its fields are the component, category, share of cost, life and residual %;
  - the shares may not exceed 100%;
  - a component can be edited or removed only while the asset is not in service;
  - an asset that came from a CWIP project is componentised on the project instead.
- **Going into service.** `action_activate` now hands over to `_activate_from_seam`, a new hook in `fix_fixed_asset.py`. For an asset with components:
  - the shares must total 100%;
  - the cost is split by share, the last component taking the rounding remainder;
  - the asset record carries the first component, and each other component becomes a new asset with **Split From** pointing back to it;
  - a component in a category with its own asset account is reclassified in one posted entry (Dr its account, Cr the seam's account);
  - the seam is consumed once.
- **Required componentisation.** A category flagged "componentisation required" now refuses a seam activation that has no components, as CWIP capitalisation already did.

### Page 8: insurance cover (capability 20, BRU-FXA-25, AUT-FXA-20, FR-FXA-034)

- **New record `fix.asset.insurance`** (INS/ reference):
  - policy number, insurer, cover type, sum insured, premium, period and policy schedule upload;
  - it covers named assets or an asset class, optionally at one branch;
  - register value, gap and gap % are read live from the net book value of the covered assets in service.
- **Putting a policy in force** takes an accounting manager who did not record it. From then on the cover is fixed: an endorsement or renewal is a new policy that renews this one, and the old policy closes.
- **Coverage review** (by an accountant):
  - stamps the register value, sum insured and gap;
  - a gap beyond the tolerance (5%, either way) needs a note, and is reported to the CFO as a to-do for each accounting administrator of the company;
  - the review falls due 365 days after the last one;
  - both figures are config keys: `cd_fixed_asset_ext.insurance_gap_tolerance_percent` and `insurance_review_days`.
- **Claim linkage.** A disposal now names the policy its claim is made under (`insurance_id`). The policy must cover the asset and the loss date.
- **Access.** Sums insured are restricted to R03/R26/R27 (spec §13): the accountant and accounting manager groups only. The read-only group has no access.
- **Workspace.**
  - Two new lists: Asset Components (page 3) and Insurance Cover (page 8). Their chips and forms are on the same pages; the policy form has three tabs.
  - The asset form gains Split From, Components (% of Cost) and Insured Under.
  - The asset and disposal forms went past 15 fields and are now tabbed (AGENTS.md rule; the guard caught it).

### Evidence

| Check | Result |
|---|---|
| Guard `test_m49_capture_buttons.py`, extended to 47 checks | **Base 94bf9e99: 9 of 47 fail** (pages 3 and 8 lack the captures, the models are not served or secured, no claim link). After: **47/47.** The A08 registry test `test_a08_m49.py` passes 11/11. |
| Live tests `test_m49_gaps_live.py`, run as non-admin finance users on the private clone `fix_test_m49`, through the P03 write and action endpoints | **4/4.** |
| Mutation check: 11 rules removed in turn (components ignored, no reclassification, components editable in service, 100% not enforced, recorder puts the policy in force, gap not reported, no note required, cover editable in force, renewal leaves the old policy in force, claim on an uncovering policy, claim outside the period) | **11 of 11 mutations turned the tests red.** |
| Regression on the same clone, no server attached (scope as §3) | **2,960 tests: 1 failure, 34 skipped.** The failure is `test_a08_m50_registry::test_report_and_form_chips_route_to_real_targets`, "form chip 'Cheque' unmapped". It is in M50's own registry at the base commit 94bf9e99 (`FORM_MODELS` has no `M50:Cheque`), and this change touches no M50 file. Hand-off to M50. |
| UI walk on a private clone (port 8079, `?debug=assets`) | Page 3 shows the Asset Component chip and list, and page 8 the Insurance Policy chip and list. A policy was saved from the page 8 chip's tabbed form: INS/2026/0001, Draft, confirmed in the database. The Asset Component form opens with its picker. No console errors. Clone dropped afterwards. |
| `generate-isolation-rules.py`, `form_fields.py --a08`, pinned ruff 0.8.4 | Only the M49 entries changed (the generator's drift in four other modules was reverted). Format and lint are clean. |
