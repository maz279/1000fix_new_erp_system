# M08 Contract Lifecycle (AMC): data-capture button audit

**Date:** 13 Nov 2026 · **Estate:** fix_real on port 8069 · **Status:** built and tested (748 passed, 0 failed, 0 skipped); registry part live for `?debug=assets` sessions only (see §7); report fix needs a restart; nothing committed

## 1. The question

The M08 workspace has 12 sub-module pages. Not all of them showed a button to record data. Which pages should have one, what should it open, and does it save the right record?

## 2. What the spec says

Source: `1000fix_ERP_Module/03_Modules/C_Commercial_Pricing_and_Revenue/M08_Contract_Lifecycle_Management.md` (FR-CTR-001…062, lifecycle §8, rules BRU-CTR-01…20, owned entities §10.1).

| # | Sub-module | Requirements | What a person records |
|---|---|---|---|
| 1 | Template-Driven Creation | FR-CTR-001/003/008 | a contract from a template |
| 2 | Parties & Approval | FR-CTR-004/012, §8 Draft → Pending Approval | parties and signatories; the submission for approval; the non-standard-terms (Legal) review |
| 3 | Coverage Scope | FR-CTR-013…016, BRU-CTR-01 | the covered assets (attach / detach), coverage rules, exclusions |
| 4 | Entitlement Engine | FR-CTR-017…024 | the entitlements; consumption is system-written (ledger) |
| 5 | SLA & Service Credits | FR-CTR-025…030, BRU-CTR-09 | contractual SLAs; a service credit (computed, then approved) |
| 6 | PM Schedules | FR-CTR-031/032 | a preventive / calibration visit |
| 7 | Amendments | FR-CTR-036…038 | an amendment |
| 8 | Renewal Governance | FR-CTR-045…049 | a renewal quote |
| 9 | Churn & Win-Back | FR-CTR-039…041, 050/051 | a suspension or termination notice; a churn reason |
| 10 | Pricing & Profitability | FR-CTR-047, 054…056 | a price change (escalation); cost and margin are computed |
| 11 | Documents & Signature | FR-CTR-010/011, Stamp Act 1899 | the executed agreement / e-signature; stamp duty |
| 12 | Obligation Calendar | FR-CTR-033/035 | an obligation (today: the PM visit) |

## 3. What the code had (before)

fix_real holds **no M08 data at all**: 0 contracts, entitlements, PM visits, amendments, renewals, terminations, stamp-duty rates, MSP contracts and SLA credits (6 contract templates only). The capture buttons are the only way the contract base can start.

Measured by executing the workspace's own page rule (`fregCreate` in `p03_workspace.js`) in node over the real registry:

| # | Page | Before | Defect |
|---|---|---|---|
| 2 | Parties & Approval | **nothing** (`create: false`, `forms: []`) | Submitting a draft for value approval and Legal's review existed only as list actions on another screen. |
| 3 | Coverage Scope | "+ Asset Attach / Detach" | **Opened the entitlement form.** The registry's *Asset Attach/Detach* form was wired to `fix.contract.entitlement`. **No form anywhere set the contract's covered assets (`covered_device_ids`) or its SLAs (`sla_policy_ids`)** — the contract form's tab "3. Coverage, SLAs & Visits" held only dates. Consequences: activation generates PM visits only for covered assets (`_generate_pm_schedule` returns at once when there are none), and an AMC order is accepted only for a covered device (BRU-SRM-03). A contract made in the workspace could never produce a PM visit or cover a device. |
| 4 | Entitlement Engine | "+ Asset Attach / Detach" | Same button as page 3, same mislabelled form. The form also carried a "Schedule" tab showing only *My Activity Deadline*. |
| 5 | SLA & Service Credits | **nothing** | The credit is mastered by M05 (`M05-form-credit`), which M08 did not open. |
| 9 | Churn & Win-Back | button, **no chip** | The termination form was offered but named by no form chip (`forms: []`), and not in the module's form list. |
| 10 | Pricing & Profitability | **nothing** (`create: false`) | A live contract's price changes only through a pricing amendment; the page offered no way to raise one. |
| 11 | Documents & Signature | **nothing** (`create: false`) | Activation requires a completed e-signature envelope and stamp duty discharged; neither could be recorded from this page. The Stamp Act Schedule I rate table (`M08-stampduty`) sat on no sub-module page and its form on no chip. |
| 1, 6, 7, 8, 12 | | correct | |

**Report defect found on the way:** *SLA Credit Register* (page 5) and *Contract P&L* (page 10) read `credit.contract_id`. `fix.msp.sla.credit` has no such field (the credit hangs off `msp_contract_id`, whose `contract_id` is the AMC). Both reports raise on the first credit — the same defect fixed in the M08 KPI route on 6 Nov, missed in these two. With 0 credits they showed "empty", hiding it.

Contract pickers on the amendment, renewal and termination forms offered every contract, including ones the server refuses (a draft cannot be amended, a terminated one cannot be renewed).

## 4. What was changed

All in `addons/platform/cd_p03_portal`:

| # | Page now offers | Form | How it saves |
|---|---|---|---|
| 1 | + Contract | `M08-record` (unchanged; tab 3 now has **Covered Assets** and **Contract SLAs**) | generic write |
| 2 | **+ Submit a Contract for Approval**; chip **Legal Review** | `M08-form-submit`, `M08-form-legal` (pick a draft / a contract awaiting Legal, then the justification / note) | `action_request_approval(justification)`, `action_legal_review(note)` — role, SoD and state checks stay in the model |
| 3 | **+ Attach / Detach Covered Assets**; chip **Entitlement** | `M08-form-coverage` (pick a draft contract, set covered devices and SLAs) | generic write; draft only (the model freezes cover once submitted) |
| 4 | + New Contract Entitlement | `M08-form-entitlement` retitled, junk tab removed, contract picker limited to drafts | generic write |
| 5 | **+ New SLA Credit** | `M05-form-credit` (M05 masters the credit) | M05's own form and approval |
| 9 | + New Contract Suspension / Termination; chip **Suspension / Termination Notice** | `M08-form-termination`, picker limited to in-force/suspended contracts | generic write, then DOFA from the list |
| 10 | **+ Raise a Price Revision** | `M08-form-price`: a pricing amendment (`presets: {kind: 'pricing'}`), picker limited to in-force contracts | generic write; applies only once approved |
| 11 | **+ Record Signature & Stamp Duty**; chips **Signature Envelope** (M24) and **Stamp Duty Rate** | `M08-form-signature` (pick a not-yet-active contract: envelope, Schedule I article, certificate, amount, exemption reason) | generic write; stamp terms editable only in draft (model lock) |

Files:
- `static/src/a04/m08.js` — mappings, 5 new forms, 9 new chips, picker filters, coverage fields on the contract form.
- `controllers/a04/writable.py` — regenerated: `covered_device_ids`, `sla_policy_ids` become writable on `fix.contract` (draft only, by the model's lock).
- `controllers/a04/m08.py` — the two reports read the AMC through the MSP contract.
- `tests/test_m08_submodule_capture.py` — new guard, 27 tests (registry rule executed in node + saves through the endpoints as non-admin Contract Officer / Legal users).

## 5. Evidence

- Node measurement of `fregCreate` before/after: before 4 pages `null`, pages 3 and 4 identical; after every page resolves its own capture (table §4).
- `test_m08_submodule_capture.py`: **27 passed** (00:59, private clone `fix_test_m08cap`), including: a draft contract takes covered assets through `/p03/model/write` and activation then schedules PM visits for that device; the cover of an in-force contract is offered read-only and stays unchanged; submit and Legal review run through `/p03/model/action`; a price revision saves as a draft pricing amendment and leaves the contract value untouched; stamp duty saves on a draft; both credit reports name the AMC behind a real credit.
- Live on 8069 under `?debug=assets` (admin, fix_real): each of the 12 pages shows its button and chips as in §4; the price form opens with *Pricing change* preset and the in-force picker says nothing qualifies (true: 0 contracts); the cover picker says there is no draft contract; the contract form's tab 3 shows Covered Assets and Contract SLAs. No error dialog.
- Regression in an isolated worktree (HEAD + only these files), private clone `fix_test_m08cap`, after Postgres recovered: the M08 guard, the estate page standard, all sub-module mapping and create-button rules, the A04 registry/whitelist/children tests, KPI tiles and the contract-core suite (`test_a04_c2_c13_contracts.py`): **748 passed, 0 failed, 0 skipped**.
- The guard fails on the old registry: with HEAD's `m08.js` restored, **9 of its 27 tests fail** (the page offers, the attach/detach wiring, the price preset).

## 6. Not fixed here (follow-ups)

1. **Scope amendments change nothing.** `_amendment_apply` handles only `pricing` and `term`; a `scope` amendment versions the contract and alters no asset, entitlement or SLA. Yet the entitlement guard tells users to change a live contract's cover "through an approved scope amendment". FR-CTR-015 (attach/detach mid-term with proration) is therefore not met for contracts in force. Needs model work (amendment lines for assets/entitlements) and M39 proration.
2. **Engine: a locked many2many change is dropped silently.** `_readonly_changed` in `p03_generic_api.py` returns *unchanged* for every many2many, so `/p03/model/write` drops a change to a locked many2many and still answers success. Forms cannot send it (the field is read-only), but a crafted call is told "saved". Cross-cutting: left alone while other sessions edit the engine.
3. **Spec entities not built:** parties and signatories (`fix.contract.party`), coverage rules by category/site and exclusions, the obligation register (`fix.contract.obligation`), service-credit schemes, suspension/reinstatement treatment of entitlement, churn reason on a lost renewal (FR-CTR-050). Page 2 captures the approval, not the parties; page 12 captures PM visits, not obligations.
4. **Data:** fix_real has 0 devices, so nothing can be covered until assets are registered in M17.

## 7. Deployment state

- The registry part is JavaScript, read from disk: it reaches users with the next asset rebuild or restart; `?debug=assets` shows it now.
- The two report fixes are a controller change: live only after a restart of 8069/8089.
- Postgres went into crash recovery from about 01:02 to 01:26 (whole-container fsync of the data directory, under load from the many parallel test databases); a run during that window skipped every DB test. The figures in §5 come from the re-run after recovery.
