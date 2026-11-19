# M13 Rental & EaaS: data-capture audit, second pass

**Date:** 19 Nov 2026 · **Estate:** fix_real on 8069, fix_dev on 8090 · **Branch:** `fix/m13-capture-pass2` · **Status:** deployed on fix_real and fix_dev 19 Nov; see §7

## 1. The question

The user again saw M13 sub-module pages "without a relevant data capture button". The 13 Nov pass ([M13_CAPTURE_BUTTON_AUDIT_2026-11-13.md](M13_CAPTURE_BUTTON_AUDIT_2026-11-13.md)) had given 8 of the 9 pages a button; the ninth, Analytics, is computed. This pass asks two harder questions:

- Does each page let a person capture **the records the spec says its function records**?
- Does every record the spec asks a person to enter have a capture anywhere at all?

## 2. Method

1. **Spec:** `1000fix_ERP_Module/03_Modules/D_Circular_and_Asset_Based_Business/M13_Rental_and_Equipment_as_a_Service.md`. This covers:
   - FR-RNT-001…044 and the lifecycle guards (§8);
   - rules BRU-RNT-01…22 and automations AUT-RNT-01…20;
   - the 18 owned entities (§10.1).

   The registry carries only per-page function counts (9/12/10/8/10/8/7/7/7 = 78), so FRs are mapped to pages by theme, as in the 13 Nov report.
2. **Code, as the user sees it:** the workspace's own page rule (`fregCreate` in `p03_workspace.js`), executed in node over the real registry, gives each page's "+ New" and chips.
3. **Model inventory:** every model, field and `action_*` of `cd_rental_asset`, cross-checked against the spec's entities and rules.

## 3. Findings (HEAD daa353b9)

Statically, every page still had its 13 Nov button. Against the spec, **eight of the nine pages lacked a record the spec names there, and none of those records existed as a model anywhere**. Of the spec's 18 owned entities, `fix.rental.extension`, `.swap`, `.loss`, `.exposure`, `fix.condition.photo` and the waiver election did not exist.

| # | Page | What it offered | What the spec requires (missing) |
|---|---|---|---|
| 1 | Fleet Register | fleet unit, kit, M37 SKU | FR-RNT-031: **inter-branch redeployment** with an M03 consignment, re-homing the unit. |
| 2 | Availability & Reservation | + New Reservation | FR-RNT-010 (**P1**): eligibility and **exposure limit**; BRU-RNT-05 approved **override**. **BRU-RNT-20 (hard): a rental to a party with no verified M33 identity was accepted**; nothing checked it. FR-RNT-032: no way to allocate a unit to a pool booking. |
| 3 | Agreements | prepare / sign the agreement | FR-RNT-016 **extension** and FR-RNT-033 versioned **variation**. `date_to` freezes at signature, so a live rental could never be extended. |
| 4 | Deposits & Waivers | deposit tender; "Loss Waiver Request" | FR-RNT-036: the **damage-waiver product** (fee %, excess, exclusions, per-agreement election, applied at assessment). The page's only "waiver" was a write-off of an unrecovered loss, which is a different thing. |
| 5 | Condition & Damage | condition report, damage | FR-RNT-021/023 (**P1**), T-04, **BRU-RNT-01/19 (hard)**: photographs. `photos_ref` was a typed link, so **a unit was handed over and closed with no photograph**. There was no hash, no M24 filing and no side-by-side of outbound vs inbound. |
| 6 | Returns & Recovery | return, damage | FR-RNT-025: **loss, theft and non-return** (escalation, valuation, police report, insurance claim, write-off). BRU-RNT-22 is unenforceable without it. |
| 7 | In-Rental Support | fault report, collection | FR-RNT-027: the **swap** itself (replacement unit, SLA target and met, condition report on both units). Only the fault was recorded. |
| 8 | Turnaround & PM | turnaround checklist, send to maintenance | FR-RNT-028 / AUT-RNT-12: PM **by calendar or usage per category**. `next_service_due` was written (+3 months) but **nothing read it**, so PM never fell due. |
| 9 | Analytics | — | Correct: computed. |

## 4. What was built

`cd_rental_asset` 19.0.0.2.0. A new file, `models/fix_rental_capture.py` (imported last), adds:

| Page | Record | Rules it enforces |
|---|---|---|
| 1 | `fix.rental.redeployment` (draft → in transit → received / cancelled) | Only an available unit with no open booking moves. Dispatch raises an M03 **branch_transfer** consignment and puts the unit **In Transit** (not bookable). Receipt is by a member of the **receiving** branch, never the dispatcher. It re-homes the unit; its history stays on it. |
| 2 | `fix.rental.exposure` (party, risk tier, limit, basis; open exposure and headroom computed) | Open exposure = the book value of each open rental's unit less its agreed deposit. A booking above the limit is **refused at reservation**. |
| 2 | `fix.rental.exposure.override` (requested → approved / rejected) | Figures snapshotted by the server. Refused when no limit is breached. **Decided by someone other than the requester.** |
| 2 | Identity gate on reservation | **BRU-RNT-20**: a verified, unexpired M33 identity document (party or its company), or no booking. Parameter `cd_rental_asset.require_verified_identity` (default on). |
| 2 | Allocation (form on the booking) | A unit of the **booked SKU** that is rentable; it is held (Reserved) for the booking. |
| 3 | `fix.rental.extension` (requested → applied / refused) | Shows availability against the unit's next booking (turnaround padding included) and the **rate-ladder re-price** before anyone decides. **Applied by another person**; refused if the date moved meanwhile. The agreement's `agreement_version` increments. An overdue flag clears when the new date is not past. |
| 4 | `fix.rental.waiver.plan` (draft → published → retired) | Fee % of gross rental, excess, accessory and theft cover, published exclusions. **Not published without Legal's review reference (spec Q-04, "not insurance")**, and published by someone other than its author. Published terms never change. |
| 4 | Waiver election on the booking (`waiver_plan_id`, `waiver_fee`) | A term of the agreement: frozen once sent or booked, and in the signed-terms digest. Its fee is **its own line on the Mushak 6.3**. |
| 4 | Damage `waiver_exclusion`, `police_report_ref`, `waiver_relief` | Applied **automatically at assessment**: on a covered damage the customer pays the excess. Gross negligence, deliberate damage and misuse are excluded; **theft only with a police report** (BRU-RNT-10). The charge approval, the deposit offset at close and the loss-waiver amount all use the charge net of the relief. |
| 5 | `fix.rental.condition.photo` | An image upload, **SHA-256 at capture**, filed in M24 as a `custody_photo`, with who and when. **Never replaced.** **Sealed** once the rental passes the report's stage: no edit or delete, and the M24 copy signature-locked. `integrity_ok` re-hashes the stored file. |
| 5 | Photo gates | Handover needs pre-delivery photographs; assessment and close need post-return ones (**BRU-RNT-01**). Parameter `cd_rental_asset.condition_photo_minimum` (default 1). A post-return report shows the **outbound photographs beside its own** (FR-RNT-023). |
| 6 | `fix.rental.loss` (open → recovered / written off; notice → recovery → legal) | A non-return is escalated before write-off. Theft needs its police report. **BRU-RNT-22**: a claim reference or a documented decision not to claim, plus the **unit's own routed write-off approval** (M63, tiered on book value), and a writer other than the reporter. Write-off: the deposit is forfeited up to the valuation, the balance is refunded, the rest is **invoiced through M20**, the rental is **Lost** (final), the unit is **Lost** and M49 disposal starts. `rental.asset_lost` is published. Recovery closes the case and the rental returns normally (**BRU-RNT-11**). |
| 7 | `fix.rental.swap` (open → executed / cancelled) | The SLA clock starts at capture (`swap_sla_hours`). Execution needs a same-SKU available replacement and **a grade for both units**. It moves the rental to the replacement and sends the faulty unit to turnaround. It writes two final condition reports (`swap_in`, `swap_out`), records SLA met, and publishes `rental.swap_executed`. |
| 8 | `fix.rental.pm.plan` (SKU or category; every N days and/or after N days on rent) + daily job | The **daily cron takes a due available unit out of availability** and opens its turnaround (AUT-RNT-12, BRU-RNT-21). Completing the turnaround sets the next due date from the plan. One active plan per SKU or category. |

Smaller changes:
- Lost units no longer count as pool capacity.
- Transit and lost units cannot be reserved.

**Workspace** (`cd_p03_portal`):
- `a05/m13.js` adds:
  - 9 lists, each with its workflow buttons, in the M13 rail;
  - 11 forms and 11 chips mapped onto pages 1–8;
  - the photo grids on the condition report;
  - the waiver fields on the reservation, agreement and damage forms.
- `controllers/a05/m13.py` serves the 9 models, with server-side picker domains (available units, open-stage reports, published plans).
- `writable.py` is regenerated. `form_fields.py` now honours `readonlyGrid` inside `grids`, so a display-only grid is not writable. Only M13 uses it, and a03/a09 regenerate unchanged.
- The **"+ New" of each page is unchanged**: the 13 Nov captures stay the primary action. The new records are the page's chips and lists.

**Data:**
- 5 sequences, one daily cron.
- 9 ACL rows and the generated isolation rules (12 rules).
- Event schemas `rental.asset_lost` and `rental.swap_executed` (spec §12.3).

**Nothing is seeded.** There is no waiver plan, exposure limit or PM interval: those are owner decisions (spec Q-04, Q-05, Q-08). Their rules apply once someone records them.

### Pages now

| # | Page | "+ New" | Chips |
|---|---|---|---|
| 1 | Fleet Register | + Fleet Serialized Asset Master | Kit, Rental SKU (M37), **Fleet Redeployment** |
| 2 | Availability & Reservation | + New Reservation | Reservation Cockpit, **Allocate a Fleet Unit**, **Rental Exposure Limit**, **Exposure Override Request** |
| 3 | Agreements | Prepare a Rental Agreement | Agreement, **Rental Extension**, **Damage Waiver Election** |
| 4 | Deposits & Waivers | Take a Security Deposit | Deposit, **Damage Waiver Election**, **Damage Waiver Plan**, Loss Waiver Request |
| 5 | Condition & Damage | + Condition Inspection Report (now with its photographs) | **Condition Photograph**, Damage Assessment |
| 6 | Returns & Recovery | Record a Rental Return | Damage Assessment, **Loss / Non-Return Case** |
| 7 | In-Rental Support | Report a Fault on a Live Rental | **Unit Swap-Out**, Return Collection |
| 8 | Turnaround & PM | Record a Turnaround Checklist | Preventive Maintenance Booking, **Preventive Maintenance Plan** |
| 9 | Analytics | — | — |

## 5. Evidence

All runs used a private clone, `fix_test_m13c2` (template `fix_test_m15c2`; `-u cd_rental_asset,cd_p03_portal`, exit 0, no error), with worktree code only.

**Guard** `cd_p03_portal/tests/test_m13_capture_pass2.py`, 33 tests:
- the page rule executed in node;
- every new list served with its columns and buttons;
- grid fields;
- every step through `/p03/model/write` or `/p03/model/action` as a non-admin rental clerk, with segregation proven by a second person.

Together with the pass-1 guard and the rental domain suite: **159 passed, 0 failed.**

**Mutation check** (32 defects re-introduced one at a time, each find-string preflighted to match exactly once): **32/32 turn the guard red.** The first run killed 31, and two results exposed real problems:
- **Survivor:** the dispatcher could receive their own redeployment. The test's dispatcher was not a member of the destination branch, so the membership check hid it. The test now makes the dispatcher a member of both branches.
- **Accidental kill, which was a real defect:** deleting a photograph while its report was open crashed on a foreign key. Odoo deleted the uploaded file with the photo, while the M24 document still pointed at it. Fixed: a withdrawn photograph's file passes to its (permanent) M24 document, which records the withdrawal. Now tested.

**Defects the live tests caught while building:**
- The receiving clerk of a redeployment could not read the unit, which was still homed at the sending branch. Receipt is now a checked custody transition: the receiver must belong to the receiving branch.
- Allocation accepted a unit of another SKU.

**Regression:** the whole `cd_p03_portal` suite, plus `tests/test_journey_08_rental.py` and `cd_document_core`: **5,934 tests.**
- One failure was caused by this change. The A05 control suite expects the guard's own message for a guarded field, and the photo's sealing message came first. Fixed: the guard now refuses first. Re-run green: A05 suite plus pass-2 guard, 106 passed, 8 skipped by design.
- **30 other failures and errors all fail identically on the baseline.** They were run by node ID on `fix_test_m13base` (a fresh clone of the same template) with the main checkout's code (`946c088f`): 30/30 fail there too.
- They are not M13: M49 inbox routing, the `fix_entity_company_unique` fixture collision in the M03/M01 tests, M06 restore-due date, M46, M54, M63 and the M01 map.

**Fixtures:** the rental tests' customers now carry a verified M33 identity, and their condition reports carry a photograph, because both are now required.

**Fitness:**
- Event schemas: OK (584).
- Manifest depends: OK.
- Isolation rules: rental is clean. The `--check` drift is in 9 peers' modules.
- Deployment wiring: the only new rental gaps were the two new events, which have no consumer, like every rental event. They are baselined beside the others.
- `ruff` 0.8.4: check and format clean.

**Live walk:** headless Chromium against a private server (port 8133) over the clone, under `?debug=assets`.
- All 9 pages show the "+ New" in the table above.
- All 12 new chips open their forms with no error and no console error.
- The server was stopped afterwards.

## 6. Not done / open

1. **Owner decisions, now with a place to record them:**
   - the waiver plan(s) and Legal's review (Q-04);
   - exposure limits per party and deposit tiers (Q-05);
   - PM intervals per category (Q-08);
   - the photo minimum per category. One global minimum is a system parameter; the spec wants it per category.
2. **Field-level visibility** (spec §13) is not modelled: exposure limits and book values are readable by every rental user. There are no rental groups in this estate, and only `base.group_user` holds the ACLs.
3. **BRU-RNT-05 "one level above the branch"**: the override is decided by another person, but not by a hierarchy level, because no approver hierarchy exists for it.
4. **Extension re-signature:** an extension is recorded as a versioned variation without the customer re-signing. The spec asks for re-signature "where terms are material", and which variations are material is not defined.
5. **Swap:**
   - no photographs on the swap's two condition reports;
   - no 50%-SLA escalation (AUT-RNT-13);
   - a replacement from another branch is outside the clerk's record rules.
6. **Loss:** no 7/14-day automatic escalation (AUT-RNT-14), no remote lock (FR-RNT-041), and the waiver is not applied to a loss valuation.
7. **Not built (P3 or other areas):**
   - sub-rental (FR-RNT-034);
   - framework call-off (FR-RNT-011);
   - EaaS (FR-RNT-012);
   - metered usage (FR-RNT-015);
   - early-return refund rules (FR-RNT-017);
   - the utilisation time series (T-08);
   - offline mobile capture (FR-RNT-038);
   - telemetry (FR-RNT-042).
8. **fix_real holds 0 rentals, 0 fleet units and 0 rental SKUs**, so nothing here can be exercised on live data until the fleet is entered.

## 7. State

**LANDED, PUSHED AND DEPLOYED on fix_real (8069) and fix_dev (8090), 19 Nov 2026.** The owner chose "Land and deploy".

- **Backups first**, both checked with `pg_restore -l` (1,823 and 1,820 table-data entries): `1000 fix/backups/fix_real_pre_m13_capture2_2026-11-19.dump` and `fix_dev_pre_m13_capture2_2026-11-19.dump`.
- **Landed** `6beda45d` on `fix/a03-live-data-and-pending-work` by compare-and-swap from `2176de73`, and fast-forwarded the main checkout with `read-tree -m -u`. **Pushed** `2176de73..6beda45d`, plus `fix/m13-capture-pass2-landed`. The old `fix/m13-capture-pass2` holds the same changes before the rebase; it was not force-pushed.
- **Upgrade:** `cd_rental_asset` went in with M21's combined `-u` (`cd_hr_core,cd_device_registry,cd_ewaste,cd_rental_asset,cd_p03_portal`), run after M16's, on both databases, exit 0. On fix_real it created:
  - all 9 new tables and the 6 new columns on existing rental tables;
  - 9 ACL rows and 12 isolation rules;
  - the "M13 Rental: preventive maintenance due" cron (active) and 5 new sequences.

  Both databases have 18 `fix_rental_%` tables and `cd_rental_asset` 19.0.0.2.0.
- **A version gap caught on the way (not M13):** `cd_gl_ext` 19.0.2.5.0 (M19, `f98fd00f`) was landed but not upgraded. M21's log showed 336 "has no table" errors for its 6 new models. I flagged it, and M19 upgraded it on both databases before the restart.
- **Restart:** one restart, by M21 at 08:06:54, after every upgrade:
  - 8069 is PID 81988 (fix_real) and 8090 is PID 21792 (fix_dev), both answering 200;
  - since boot, both logs show the registry loaded, 0 "has no table" and 0 "Failed to load registry";
  - fix_real's only error line is a `SERIALIZATION_FAILURE` that Odoo retried successfully.
- **Production bundles:** both serve the new forms (`M13-form-swap`, `-photo`, `-waiver-plan`): fix_real's current bundle, and fix_dev's rebuilt at 08:08.
- **Signed-in live check, 19 Nov, after the restart.** This used the owner's own session in the in-app browser, through the endpoints the M13 screens call. It was read-only: actions were called on a non-existent record id, so nothing changed. On **fix_real (8069)** and **fix_dev (8090)** alike:
  - all 9 new lists are served with their declared columns, **0 dropped**;
  - all 13 new or changed forms return every declared field;
  - **17/17 new workflow buttons are accepted** by the running server ("Record not found"), while the control (`unlink`) is refused ("Action not available").

  The workspace UI itself was not drawn: the browser pane was hidden, and OWL does not render there. The visual walk of all 9 pages and 12 chips ran on the private clone (§5). fix_real holds no rental units, SKUs or rentals, so there is no live record to exercise yet.
- The private clone `fix_test_m13c2` is kept for re-checks; the baseline clone was dropped.
