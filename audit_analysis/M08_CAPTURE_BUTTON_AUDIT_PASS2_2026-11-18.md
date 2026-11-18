# M08 Contract Lifecycle (AMC): data-capture audit, second pass

**Date:** 18 Nov 2026 · **Estate:** fix_real on port 8069 (fix_dev on 8090) · **Branch:** `fix/m08-capture-pass2` · **Status:** built and verified on a private clone; see §7

## 1. The question

The user again saw M08 sub-module pages "without a relevant data capture button". The 13 Nov pass ([M08_CAPTURE_BUTTON_AUDIT_2026-11-13.md](M08_CAPTURE_BUTTON_AUDIT_2026-11-13.md)) had given every one of the 12 pages a "+ New". This pass asks the harder question: does each button capture **the record the spec says that function records**, and does every record the spec asks a person to enter have a capture at all?

## 2. Method

1. **Spec:** `1000fix_ERP_Module/03_Modules/C_Commercial_Pricing_and_Revenue/M08_Contract_Lifecycle_Management.md`: FR-CTR-001…062, the lifecycle guards (§8), rules BRU-CTR-01…20 and owned entities (§10.1). The registry carries only per-page function counts (12/8/10/14/10/9/8/9/6/10/7/5 = 108), so FRs are mapped to pages by theme, as in the 13 Nov report.
2. **Code, as the user sees it:** the workspace's own page rule (`fregCreate` in `p03_workspace.js`) **executed in node** over the real registry. For each page it gives the "+ New" and every chip, with the model and form each one opens.
3. **Model inventory:** an AST scan of `cd_contract_core` (every model, field and `action_*`), cross-checked against the spec's entities and rules.

## 3. Findings (HEAD 03f2d7b4)

Statically, all 12 pages had a "+ New" (the 13 Nov fix held). Against the spec, six pages captured the wrong thing or were missing a record that has no model anywhere:

| # | Page | What the button did | What the spec requires (missing) |
|---|---|---|---|
| 6 | PM Schedules | "+ PM Schedule" created **one ad-hoc visit** | FR-CTR-031 (P0) / 032: a per-contract preventive **and calibration** schedule, with lead time and site access window. Visit frequency was a constant per family (AMC 90 days, RAMC 120, managed 30, rental 180) in `PM_INTERVALS`: no contract could carry its own schedule. |
| 3 | Coverage Scope | listed devices only | FR-CTR-014: cover by asset type, brand or site, for a fluid estate. **BRU-CTR-01 (hard block) was not enforced:** an AMC contract activated covering nothing. |
| 4 | Entitlement Engine | "+ Contract Entitlement" (draft contracts only) | FR-CTR-022: **top-up** of a live contract; T-01 / BRU-CTR-16: the append-only **movement ledger**; BRU-CTR-04 / AUT-CTR-05: a cancelled order gave nothing back. |
| 5 | SLA & Service Credits | "+ SLA Credit" opened M05's credit, which the system computes (BRU-CTR-09) and which only exists for MSP contracts | FR-CTR-028: the **service credit scheme** (breach type, priority, cumulative rule, cap). |
| 9 | Churn & Win-Back | termination notice, lost renewal | FR-CTR-043 / **BRU-CTR-12 (hard block)**: dispute flag, legal hold, no auto-renewal or escalation while disputed. FR-CTR-040: resume with a **declared treatment** of the suspended period (resume just flipped the state). |
| 11 | Documents & Signature | e-signature envelope + stamp duty | FR-CTR-011 (P0) "wet or electronic". **Activation demanded a completed e-signature envelope, so a contract signed in ink could never be activated.** For a Bangladeshi corporate customer, ink is the common case. |
| 1 | Template-Driven Creation | + New Contract | BRU-CTR-19: a named 1000FiX **owner** (no such field). FR-CTR-006: master/subsidiary. The "Master Agreements" screen listed **every active contract**. |
| 2, 7, 8, 10, 12 | | correct | |

## 4. What was built

`cd_contract_core` 19.0.1.3.0. A new file, `models/fix_contract_capture.py` (imported last), adds:

| Page | Record | Rules it enforces |
|---|---|---|
| 6 | `fix.contract.pm.plan`: type (preventive / calibration / inspection), asset or all covered, every N months, first due date, lead days, site access window | Activation generates the term's visits **from the plans**; without a plan the family interval still applies. Each visit carries its plan, type and `dispatch_from`. On a signed contract only a Contract Manager adds a plan (its visits start today) or retires one (its future visits are skipped); interval and dates are fixed. |
| 3 | `fix.contract.coverage.rule`: asset type / brand / customer site, cover window | Cover = listed **or** rule-matched assets of the customer. M01's AMC gate (`entitlement_active`), the order's entitlement line and PM generation all use it. Draft-only, like other terms. **BRU-CTR-01 enforced** for AMC/RAMC: no listed asset and no rule means no activation. |
| 4 | `fix.contract.entitlement.topup` (draft → submitted → applied / rejected) | Contract in force, counted entitlement only. A Contract Manager **other than the requester** applies it; publishes `contract.entitlement_topped_up` (with amount) for M39 billing. |
| 4 | `fix.contract.entitlement.movement`: append-only ledger | Written by grant (activation), consume, restore, top-up and prorate; refuses to be typed, edited or deleted. A **cancelled order restores** its draw once. |
| 5 | `fix.contract.credit.scheme`: breach type, priority, % of fee or fixed, per-breach or escalating, cap | A term (draft-only). `_scheme_credit(n, fee)` computes the capped credit. |
| 9 | `fix.contract.dispute` | On open: the contract's M24 documents go on **legal hold through the hold register**; the expiry cron neither escalates nor auto-renews a disputed contract. Closed by a Contract Manager **who did not open it**, with the resolution; holds are released unless another open dispute needs them. Events `contract.dispute_opened` / `contract.dispute_resolved`. |
| 9 | Reinstatement: `action_resume(treatment, note)` | A treatment must be declared: **extend_term** (term +suspended days), **forfeit**, or **prorate** (each counted entitlement cut for the suspended days, recorded in the ledger). `suspended_on` is stamped when a suspension executes. |
| 11 | Wet-ink signature: `signature_method`, signing date, **scan upload** (filed automatically as an M24 `fix.document`), `action_verify_wet_signature` | A second Contract Officer (not the recorder) verifies. The date cannot be in the future. Activation accepts a verified ink signature in place of the envelope; the filed original is signature-locked. Fixed once signed. |
| 1 | `owner_id` (defaults to the creator; stamped at submission if empty), `parent_contract_id` / `is_master_agreement` | One level; same customer; fixed after draft. "Master Agreements" now lists masters only. |

Workspace (`cd_p03_portal`): `a04/m08.js` adds 6 list screens (Coverage Rules, Entitlement Top-Ups, Entitlement Ledger, Service Credit Schemes, PM & Calibration Plans, Disputes & Legal Hold), 8 forms, 7 chips and the new page mappings. `controllers/a04/m08.py` serves the six models, plus the resume and verify actions on `fix.contract`. `writable.py` is regenerated; the ledger's whitelist is empty. The list action "Resume" was replaced by the Reinstatement form, because a resume must now declare its treatment.

Events: schemas for the 3 new events, plus the 4 M08 events from 13 Nov that were never registered (`contract.asset_attached/detached`, `contract.obligation_overdue`, `contract.renewal_lost`).

### Pages now

Executed page rule (node) and the live walk agree:

| # | Page | "+ New" | Chips |
|---|---|---|---|
| 1 | Template-Driven Creation | + Contract (now with owner and master agreement) | Contract |
| 2 | Parties & Approval | + Submit a Contract for Approval | Submit, Legal Review, Contract Party |
| 3 | Coverage Scope | + Attach / Detach Covered Assets | Asset Attach/Detach, **Coverage Rule**, Entitlement, Coverage Exclusion |
| 4 | Entitlement Engine | **+ Top Up an Entitlement** | **Entitlement Top-Up**, Entitlement (now shows its ledger) |
| 5 | SLA & Service Credits | **+ Add a Service Credit Rule** | **Service Credit Scheme**, SLA Credit (M05) |
| 6 | PM Schedules | **+ Set a PM / Calibration Plan** | **PM Schedule** (the plan), **PM Visit** (one extra visit) |
| 7 | Amendments | + New Contract Variation & Amendment | Amendment |
| 8 | Renewal Governance | + New Renewal Quote | Renewal Quote |
| 9 | Churn & Win-Back | + New Contract Suspension / Termination | Suspension / Termination, **Contract Dispute**, **Reinstatement**, Lost Renewal |
| 10 | Pricing & Profitability | + Raise a Price Revision | Price Revision |
| 11 | Documents & Signature | + Record Signature & Stamp Duty (now electronic **or wet ink**) | Signature & Stamp Duty, **Wet-Ink Signature Verification**, Signature Envelope (M24), Stamp Duty Rate |
| 12 | Obligation Calendar | + New Contract Obligation | Contract Obligation, PM Schedule (the plan) |

## 5. Evidence

All runs were on a private clone, `fix_test_m08b` (from `fix_test`, then `-u all`: 166 modules, exit 0), using worktree code only.

- **Guard** `cd_p03_portal/tests/test_m08_capture_pass2.py`: 22 tests. Every save runs through `/p03/model/write` or `/p03/model/action` as a non-admin Contract Officer or Manager. Together with the updated pass-1 guard `test_m08_submodule_capture.py`: **52 passed, 0 failed, 0 skipped.**
- **Mutation check** (`scratchpad/m08/mutate.py`): 25 defects re-introduced one at a time, each find-string preflighted to match exactly once. **25/25 turn the guard red.** The first run killed 23; the two survivors exposed real gaps in the guard: no rule-covered device was pushed through an AMC order, and the dispute test's contract lay outside the 90-day window, so its renewal assertion held vacuously. Both tests were fixed; the dispute test now has a non-disputed twin as a positive control.
- **Defects the tests caught while building:** a coverage rule naming none of type, brand or site was accepted, because an `@api.constrains` fires only for the fields written. Constraints are now also keyed to `contract_id`.
- **Regression** (contract core, MSP contract, quotation, subscription, billing engine, service order, P03 A04/estate/sub-module/KPI/whitelist guards): **1,968 tests**. The failures caused by this change (a stamp-exemption test whose contract covered nothing, which BRU-CTR-01 now refuses; two forms owning child records without showing them; the vault ratio) were fixed and re-run green. **4 remain, none caused by this change:**
  - `test_f2_no_flat_forms_remain` and `TestA04Workspace::test_no_form_is_flat`: 8 flat M36 forms, identical on HEAD.
  - `test_f5_document_vaults_exist_on_the_major_forms`: these A04 register tests hard-code the **main checkout's** path, not the code under test. The main checkout is already at 53/111 (47.7%) before this change. On this branch it is 58/114 (50.9%), so this change raises the ratio.
  - `test_no_submodule_page_offers_another_records_button`: names M30/1 Branch Master only.
- **Live walk** on a private server over the clone, under `?debug=assets`, with the bundle confirmed to contain the new identifiers: all 12 pages show the button and chips in the table above, with no error. Nine new or changed lists were requested with their declared columns; all were served, **0 columns dropped**. The PM plan form opens with its three tabs. The contracts list offers "Verify Wet-Ink Signature" and no longer offers a bare "Resume".

## 6. Not done / open

1. **M05 credit engine does not read the M08 credit scheme.** `_scheme_credit` computes the capped credit, but M05's computed credit (`fix.msp.sla.credit`) is MSP-only and uses its own rule. For a plain AMC contract, AUT-CTR-09 (compute the credit on a breach) still has no engine. This is M05's area.
2. **Entitlement period and reset (FR-CTR-018) and exhaustion treatment (FR-CTR-021)** are not modelled. Balances run for the whole term, and an exhausted entitlement is priced as standard service. They were deliberately not added as fields nothing enforces.
3. **The ledger mirrors the counter.** `quantity_consumed` is still the stored balance; the ledger records every movement beside it. BRU-CTR-16's "derived from the ledger" would need the counter replaced.
4. Coverage rules and credit schemes are draft-only. Scope amendment lines do not yet carry them, so a live contract changes them by a new term.
5. Not built (P1/P2): framework call-off (FR-CTR-007), novation (042), cancellation before commencement (044), service-review scheduling (034), owner reassignment on staff exit (AUT-CTR-17).
6. **fix_real holds no M08 contracts and no registered devices**, so nothing here can be exercised on live data until contracts are entered.
7. Pre-existing, other owners: the M36 flat forms, the estate vault ratio and the M30/1 create-button finding (§5).

## 7. State

Committed on `fix/m08-capture-pass2` (worktree `m08cap2-wt`). Not yet landed on `fix/a03-live-data-and-pending-work`, not deployed: `cd_contract_core` 19.0.1.3.0 needs `-u cd_contract_core,cd_p03_portal` on fix_real and fix_dev **and** a restart of 8069/8090 (new controller surfaces).
