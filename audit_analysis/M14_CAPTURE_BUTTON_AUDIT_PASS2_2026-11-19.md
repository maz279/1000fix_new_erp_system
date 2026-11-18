# M14 Trade-In & Refurbishment: data-capture audit, pass 2

**Date:** 19 Nov 2026 · **Estate:** fix_real on 8069, fix_dev on 8090 · **Branch:** `fix/m14-capture-pass2` · **Status:** built and tested on branch `fix/m14-capture-pass2`; see §7

## 1. The question

The user again saw M14 sub-module pages without a relevant data-capture button. This was after the 13 Nov pass ([M14_CAPTURE_BUTTON_AUDIT_2026-11-13.md](M14_CAPTURE_BUTTON_AUDIT_2026-11-13.md)), which gave all 10 pages a "+ New".

Counted statically, every page still has a button. So this pass reads **relevance**: does each page let a person capture what the spec says that sub-module captures?

## 2. Sources

- `1000fix_ERP_Module/03_Modules/D_Circular_and_Asset_Based_Business/M14_TradeIn_Refurbishment_and_Resale.md`: FR-TRF-001…039 (§5), the state model (§8), BRU-TRF-01…24 (§9), entities (§10), automations (§11), and roles and SoD (§13).
- Code:
  - `cd_tradein`: models, security, data;
  - `cd_p03_portal`: `static/src/a05/m14.js`, `controllers/a05/m14.py`, `controllers/a05/writable.py`.
- Live data: fix_real and fix_dev both have **0 rows** in every M14 table. The buttons are the only way in, so nothing could be shown with records.

## 3. Findings: page by page against the spec

| # | Sub-module | The spec says this page captures | What the page captured (HEAD daa353b9) | Gap |
|---|---|---|---|---|
| 1 | Intake (5 channels) | FR-TRF-001: channel (portal/app/counter/field/corporate), condition self-assessment, faults, age, photographs, warranty status. FR-TRF-035: accessories. FR-TRF-005 / BRU-TRF-09 (H): physical verification on receipt; an offer is revised **only** where the verified condition differs, with photographic evidence | Customer, NID, *acceptance* channel, device. **No intake channel, no declaration, no photos, no accessories.** The "Post-Inspection Value" was a plain number: anyone could type a value below the accepted offer with no evidence | **Yes** |
| 2 | Valuation Engine | FR-TRF-033 / BRU-TRF-10: offer = resale estimate − expected refurbishment, logistics, destruction and channel cost; below the category margin floor needs approval | Grid price × age × condition factors. **No resale estimate, no expected cost, no margin**, so no floor | **Yes** |
| 3 | Provenance Screening | FR-TRF-006: seller identity, IMEI/NEIR, blocklist, evidence | All present | No |
| 4 | Settlement | FR-TRF-007: settle by mobile money, bank transfer, cash or store credit | **The method was hard-coded to mobile money** in `action_pay`; no bank account could be given | **Yes** |
| 5 | Bulk Buy-Back | FR-TRF-009 lot + reconciliation | Built 13 Nov | No (the lot's intakes now record the corporate channel) |
| 6 | Destruction Gate | FR-TRF-011: attach the M06 certificate | Built 13 Nov | No capture gap (segregated location, see §6) |
| 7 | Refurbishment Orders | FR-TRF-036: rework after a failed QA, its cause and cost, kept apart from first-pass work. FR-TRF-013: before/after evidence. BRU-TRF-22 (H): activation lock removed only on proof of ownership | Step, technician, cost, notes. **No rework, no evidence, no ownership proof** | **Yes** |
| 8 | Grading & QA | FR-TRF-019 / BRU-TRF-12: the grade is **computed** from the QA results. BRU-TRF-13 / T-07: an override needs a justification and is not made by the QA technician. BRU-TRF-14 (H): the battery minimum per grade. FR-TRF-017: every test result | **The grade was a free choice** (default B), and `action_grade` took any grade typed on the request. No override record, no battery minimum, and QA kept two counters | **Yes** |
| 9 | Resale | FR-TRF-026: returns and post-sale support, with the failure fed back to grading. FR-TRF-038 (P0): re-confirm NEIR before listing | The listing preparation was there. **Nothing captured a return**, and the warranty's `claims_count` could never move. Listing did not re-check NEIR | **Yes** |
| 10 | Harvesting | FR-TRF-020 / BRU-TRF-19: route an unsellable unit to parts only, with the write-off approved above the supervisor. §13: routing and write-off approval are two people | The harvest line only. **No routing or write-off; a grade-E unit was harvested with no approval** | **Yes** |

## 4. What was built

### 4.1 `cd_tradein` 19.0.0.3.0: `models/fix_tradein_capture.py` (imported last)

**p1 Intake.**

On `fix.tradein.request`:
- `intake_channel` (5 channels; a lot's intakes set `corporate`);
- the declaration: `declared_condition`, `declared_faults`, `declared_age_months`, `oem_warranty_status`, `condition_photo_id`;
- five accessory flags plus `accessories_notes`.

The declaration freezes once the offer is sent, and the channel once the offer is accepted.

New `fix.tradein.intake.check` (Physical Intake Verification): verified condition, identity match, accessories, difference, photographic evidence and verified value. **Confirm Verification**:
- refuses a unit that is not the one offered;
- refuses a value above the accepted offer;
- refuses a lower value unless the condition is worse than declared, described and photographed (BRU-TRF-09);
- refuses the person who valued the unit (§13 SoD);
- then writes the graded value, so the customer accepts the revision through the existing step.

A graded value below the accepted offer written any other way is refused. The check is allowed from acceptance until the payout is requested.

**p2 Offer economics** on `fix.tradein.valuation`:
- New fields: resale estimate, the four expected costs, expected total, modelled margin and margin %.
- The floor is `cd_tradein.offer_margin_floor_pct` (15). Below the floor, the valuation is an override, approved by a valuation manager through the existing path.
- Apply is refused without a resale estimate.

**p4 Settlement:**
- `settlement_method` (mobile money, bank transfer, cash) and `settlement_bank_account_id`.
- A bank transfer needs an account of the seller.
- Both are part of the terms the payout approval pins: a change voids it.
- `action_pay` passes the method and the account to the treasury request.

**p7 Refurbishment** on `fix.refurbishment`:
- A step created while the unit's latest QA failed is **rework**. Its cause is required, and `is_rework` and `rework_qa_id` are guarded.
- The request shows `rework_cost` and `first_pass_cost` separately.
- Before/after photos.
- `activation_lock_removed` requires `ownership_proof_id` (constraint).

**p8 Grading & QA:**
- `fix.refurb.grade.battery_minimum_pct`, seeded A 85 / B 80 / C 75 / D 70 / E 0; a value the quality manager set is kept.
- `fix.tradein.grade` (now guarded):
  - `computed_grade` = the worst axis, dropped while the battery is below the grade's minimum, and parts-only below D's.
  - Blank grade = computed.
  - A different grade is an **override**: it needs a justification and the new **Refurbishment Supervisor** role. It is refused to anyone who created, ran or submitted the unit's QA (T-07), and stamped with who and when.
  - BRU-TRF-14 is a hard stop that no override lifts.
- `action_grade` takes the grade and battery from the latest certificate. Grading without one is refused, so a grade typed on the request no longer counts.
- New `fix.refurb.qa.test` rows on the QA form (test, expected, measured, outcome, equipment):
  - on submit, the totals are counted from the rows;
  - the rows freeze with the result.

**p9 Resale:**
- **NEIR at listing** (FR-TRF-038, AUT-TRF-15): Resale Ready on a handset requires a current, cleared provenance screen. A stale one is refused, so the unit is re-screened.
- New `fix.refurb.return`:
  - only a sold unit, with the grade at sale and the warranty stamped;
  - **Receive Return** needs a failure code (unless change of mind) and refuses a return outside the window (`cd_tradein.return_window_days`, 7) or the warranty;
  - it counts the warranty claim;
  - **Decide** is for a Refurbishment Supervisor who did not receive the return.

**p10 Harvest:** new `fix.refurb.writeoff` (Parts-Only Routing & Write-off).
- Cause, notes, destination (harvest/recycle), and cost-to-complete against the resale estimate.
- **Route** is by a Refurbishment Supervisor, and stamps the accumulated cost.
- **Approve** is by the new **Refurbishment Write-off Approver** role, never the router; **Reject** needs a reason.
- One live routing per unit.
- A harvest is refused until a routing to harvest is approved.

**Roles:** `group_refurb_supervisor` and `group_refurb_writeoff_approver`. Like the other M14 decision roles, they **ship empty**: appointing holders is a business decision.

**No new domain events.** Outcomes go to the trade-in chatter (see §6).

### 4.2 Workspace (`m14.js`, surfaces, whitelist)

- Pages:
  - p1 adds the list and form **Physical Intake Verification**;
  - p9 adds **Refurbished Returns** / **Refurbished Unit Return**;
  - p10 adds **Parts-Only Routing & Write-off**.
- The intake dossier gains a "Customer's Declaration" section.
- The valuation form gains "Offer Economics".
- Settlement and the dossier gain the method and account.
- The work order gains "Rework" and "Work Evidence".
- The QA form gains the protocol grid.
- The grading form shows the computed grade and the override; the request's grade is read-only.
- `controllers/a05/m14.py` serves the 3 new models with their actions.
- `writable.py` was regenerated with `form_fields.py --a05`: additions only.
- Record rules come from `generate-isolation-rules.py`; only `cd_tradein`'s file was kept. Nine other modules show pre-existing drift, left to their owners.

## 5. Evidence

Run on a private test DB `fix_test_m14c2` (cloned from a current peer template; `-u cd_tradein,cd_p03_portal` exit 0, no ERROR). Commands use the worktree code.

| Check | Result |
|---|---|
| Domain guard `cd_tradein/tests/test_m14_capture_pass2.py` (non-admin users; `/p03/model/write` and `/p03/model/action` where the workspace uses them) | 19 / 19 pass |
| Portal guard `cd_p03_portal/tests/test_m14_capture_buttons.py`: 14 new tests (node evaluates the engine's own `fregCreate` / `fregPanels`) | 35 / 35 pass. **The 14 new tests fail on the HEAD registry**; the 21 pass-1 tests pass on both |
| Mutation: 26 mutants, each removing one control from `fix_tradein_capture.py` | **26 / 26 caught.** The first run left one survivor: the gate's certificate clause sat behind `action_grade`'s own refusal. A direct gate assertion was added, and it is now caught |
| Regression (1,536 tests): cd_tradein, cd_ewaste, cd_marketplace, cd_settlement_ext, cd_ml_services, cd_asset_workorder_spine, cd_finance_nav, M15 A06 hand-off, portal A05 control suite, estate page standard (67 modules), sub-module mapping, create button, KPI tiles | 1,459 pass, 5 skip, **72 fail. All 72 fail identically on the main checkout without this change** (946c088f, baseline DB `fix_test_m14base`): cd_settlement_ext M53 (no GL account 252000, rate expectations) and the A07 asset spine. None are in trade-in, marketplace or e-waste |
| ruff 0.8.4 (pre-commit pin), check + format | clean |

Existing tests changed to the new rules (their intent kept):
- valuations carry a resale estimate;
- grading goes through a certificate (`certify`), so a typed grade no longer grades;
- a lower payout value goes through an intake verification;
- the value-change test now raises the value;
- the harvest test routes the unit first;
- the four master-grade behaviour tests assert that the certificate decides the grade and its master.

**Live walk** (headless Chromium on a private server, port 8096, worktree code, `debug=assets`):
- all 10 sub-module pages open and each shows its "+" button;
- pages 1, 9 and 10 show the new chips (Physical Intake Verification, Refurbished Unit Return, Parts-Only Routing & Write-off);
- all 9 changed forms open with no page error.

Saved through the real forms:

| Form | Saved as | What it shows |
|---|---|---|
| Trade-in | TRD/2026/00257 | channel `field`, declared condition `fair`, faults, age 14, charger |
| Physical Intake Verification | TIC/2026/00010 | the picker offered only the accepted and refurbishing units |
| Parts-Only Routing | RWO/2026/00008 | the picker offered only the refurbishing unit |
| Refurbishment step | `TRD/2026/00246 · Repair` | **this save failed before the fix** |
| Grading certificate, grade left blank | TGRD/2026/00062 | computed C (cosmetic C, battery 90%), no override |

Screenshots are in the session scratchpad (`m14/shots`).

## 6. Not built (owner decisions or other modules)

- **Segregated unsanitised location** (FR-TRF-034 / BRU-TRF-04, P0). The state machine already blocks refurbishment, listing and harvest without a verified certificate. The physical location needs M15 location typing.
- **Store credit and exchange offset** (FR-TRF-007/008): through M10 wallet / M38 order.
- **Domain events** `refurb.returned`, `refurb.grade_overridden`, `refurb.rejected`: no consumer exists yet, and adding them means a registry change.
- What a return decision triggers (re-open the unit for re-refurbishment, or harvest) and M18 routing on a recycle write-off are recorded, not automated.
- **Disclosure report** (FR-TRF-024), **grading audit sample** (FR-TRF-037), **ageing markdown** (FR-TRF-029): generated or scheduled, not captures.
- The two new roles ship empty.

## 7. State

- Built and tested in worktree `m14cap2-wt`, branch `fix/m14-capture-pass2`.
- fix_real and fix_dev still have 0 rows in every M14 table.
- The deploy is `-u cd_tradein,cd_p03_portal` on both DBs plus one restart. The cd_tradein cascade covers cd_marketplace, cd_ml_services, cd_asset_workorder_spine, cd_settlement_ext and cd_finance_nav.
- The deploy is coordinated with the M18 session, which needs `-u cd_ewaste,cd_p03_portal`, so one session runs the combined `-u` and a single restart.
