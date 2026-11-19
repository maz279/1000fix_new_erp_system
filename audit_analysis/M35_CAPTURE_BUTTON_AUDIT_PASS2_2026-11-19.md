# M35 Marketing Campaigns: sub-module capture audit, second pass

**Date:** 19 Nov 2026 · **Area:** A03 · **Workspace fragment:** `cd_p03_portal/static/src/a03/m35.js`
**Backend:** `cd_campaign` 19.0.0.3.0 (new `models/fix_campaign_capture2.py`), `cd_p03_portal/controllers/a03/m35.py`.

The user again saw M35 sub-module pages without a relevant data-capture button. The first pass (14 Nov,
`M35_CAPTURE_BUTTON_AUDIT_2026-11-14.md`) had given every page a "+ New" for the list it shows. Its own guard
still passed on HEAD `742e46bc` (32/32). So this pass did not count buttons. It read each page against what the
specification says a person records there:
- §5 FR-MKT-001..040;
- §8.1, the campaign lifecycle;
- §9 BRU-MKT-01..14;
- §10.1, the owned entities;
- §11 AUT-MKT-01..14.

Judged that way, **seven of the eight pages were still missing captures the spec gives them**. Page 8 (Co-Marketing) was complete.

## What each page is supposed to capture, and what it had

| # | Page | Spec | Had (14 Nov) | Missing |
|---|---|---|---|---|
| 1 | Campaign Planning & Approval | FR-MKT-001..008, BRU-MKT-04/05/13, §8.1 | Campaign (name, channel, budget, dates) | **Campaign type, objective, success measure** (FR-MKT-001/004). **Programme** (FR-MKT-005, entity `fix.campaign.programme`). **Capacity check** against operations, with the Operations Director's override (FR-MKT-006, BRU-MKT-05 class A, lifecycle state "capacity checked"). **Emergency stop** (FR-MKT-008, BRU-MKT-13 hard rule: halt every channel and cancel queued messages). **Forward calendar with conflicts** (FR-MKT-007). |
| 2 | Audience from Segments | FR-MKT-009..015, BRU-MKT-08 | Include/exclude segments, holdout, estimate | **Suppression** of open complaints (BRU-MKT-08), credit hold and recent recipients (FR-MKT-013). **Intersect** (FR-MKT-010: "include, exclude and intersect"). |
| 3 | Journey Orchestration | FR-MKT-016..023, BRU-MKT-06/07 | Journey, trigger, members | **Priority between conflicting journeys** (FR-MKT-020, BRU-MKT-06 hard rule). **Exit on complaint or conversion** (FR-MKT-019, AUT-MKT-07/08). A **manual exit** with its reason. |
| 4 | Content & Offers | FR-MKT-024..029, BRU-MKT-09/10, T-09/T-10 | Creative (name, type, file reference), Offer | The creative **held no copy in any language**: no English or Bengali text, no Bengali version of a visual (BRU-MKT-10 hard rule). **No expiry** (BRU-MKT-09 hard rule, AUT-MKT-14), **no version** (FR-MKT-024/028). No SMS segment cost (T-10), no personalisation check (FR-MKT-026). **Offers from M10's mechanics** (FR-MKT-027) had no chip. No tracked **landing page** (FR-MKT-029). |
| 5 | Experimentation | FR-MKT-031, entity `fix.ab.test.significance` | Experiment, start, conclude with a winner | A winner was named with **no figures and no significance**: the "statistically valid winner selection" of FR-MKT-031 did not exist. |
| 6 | Budget & Attribution | FR-MKT-032..037, BRU-MKT-11, AUT-MKT-11/12 | Spend (actual), void, attribution model | **Committed spend** (FR-MKT-033: "committed and actual"). **Budget alerts** at 80 % and the pause at 100 % (AUT-MKT-12). **The measured result** (FR-MKT-036/037, AUT-MKT-11, entity `fix.attribution.result`): incremental revenue against the holdout and ROI. Without it, the lifecycle state "measured" could not be reached. |
| 7 | Portal Advertising | FR-MKT-030, entity `fix.ad.placement` | Placement, advertiser, window | **Position and page context**. Two ads could take the same slot at the same time. |
| 8 | Co-Marketing | Scope item 14 | Partners, MDF co-funding | Nothing missing. |

How the gaps were confirmed:
- None of `fix.campaign.programme`, `fix.attribution.result` or a capacity check existed anywhere in `addons/`.
- `fix.campaign` had no type, objective, programme, halt or suppression field, and its state machine had no "halted" state.
- `fix.campaign.creative` had `reference` (one file key) and no text, language, expiry or version field.
- `fix.campaign.experiment` had no sample or conversion field.
- `fix.campaign.spend` had no stage.
- M10's `fix.loyalty.campaign.hook` (the voucher and points reward tied to a campaign) existed and staff could create it, but no M35 page offered it.
- The new page guard fails **16 of its 42 checks on HEAD**.

## What was changed

### Workspace (`m35.js`): what each page captures now

| # | Page | "+ New" | Form chips (new in **bold**) | New lists on the page |
|---|---|---|---|---|
| 1 | Campaign Planning & Approval | Campaign | **Campaign Programme**, **Capacity Check**, **Emergency Stop** | Campaign Programmes, Capacity Checks (action **Override (Operations Director)**), Campaign Calendar |
| 2 | Audience from Segments | Define Campaign Audience | (same form, now with **intersect** and **suppression**) | — |
| 3 | Journey Orchestration | Customer Journey | Behaviour Trigger, **Exit a Journey Member** | — |
| 4 | Content & Offers | Creative Asset | Offer, **M10 Voucher or Points Reward** (opens M10's form) | M10 Campaign Rewards (read-only, served by M10) |
| 5 | Experimentation | A/B Experiment | Conclude an Experiment (now **with the figures**) | — |
| 6 | Budget & Attribution | Campaign Spend | Void a Spend, **Measure a Campaign**, Attribution Model | Campaigns To Measure (action **Measure Against The Holdout**), Campaign Results |
| 7 | Portal Advertising | Portal Ad Placement | (same form, now with **position** and **page context**) | — |
| 8 | Co-Marketing | Name Co-Marketing Partners | MDF Co-Funding | — |

Other workspace changes:
- **Campaign form.**
  - Tab 1 gains type (required), programme, objective, success measure and target, and the capacity result.
  - The budget tab shows committed spend and the budget left after commitments.
  - The audience tab gains intersect and the three suppression switches.
  - The attribution tab gains the landing page, its tracked link and the last measurement.
  - The governance tab shows who stopped the campaign, when, why, and how many queued messages were cancelled.
- **Campaign Manager list.**
  - New columns: type and capacity.
  - New action: **Emergency Stop**, which asks for the reason.
- **Journey form.** Conflict group, priority, exit on complaint and exit on conversion.
- **Creative form.**
  - A new tab, "English & Bengali Copy": subject and body in each language.
  - It shows the personalisation used and the SMS segment count per language.
  - It takes the Bengali version reference of a visual asset.
  - It takes an expiry date (required) and shows the approved version.
- **Experiment.**
  - The conclusion form takes how many each variant reached and converted.
  - The experiment form shows both rates, the p-value and the confidence.
- **Spend.**
  - The form takes a stage: committed (order placed) or incurred (invoiced).
  - The list gains **Mark Invoiced**.
- **Programme form.** It shows its campaigns as a locked, server-filled grid.
- The result form is tabbed and read-only.

### Backend (`cd_campaign` 19.0.0.3.0, new `models/fix_campaign_capture2.py`)

- **Campaign definition** (FR-MKT-001/004/029):
  - `campaign_type` (the ten types of FR-MKT-004), `objective`, `success_measure` and `success_target`.
  - `landing_page_url`, which must be `https://`. Its `tracked_url` carries the UTM parameters.
- **`fix.campaign.programme`** (FR-MKT-005/032):
  - code (unique per company), period, owner and budget;
  - roll-up of campaign count, planned budget and actual spend.
  - The campaigns' budgets together may not exceed the programme budget, and a campaign must run inside the programme period.
- **`fix.campaign.capacity.check`** (FR-MKT-006, BRU-MKT-05):
  - It is made on a draft campaign whose audience has been estimated (§8.1 order).
  - Projected jobs = post-suppression reach × expected response %. They are compared with the jobs the branches can take in the window. The planner records where that figure comes from.
  - An insufficient check **blocks launch**. Only the new group **Capacity Override (Operations Director, M35)** overrides it, never the person who made the check, and always with a reason.
  - A check is evidence: it is never edited or deleted.
  - Setting `cd_campaign.capacity_check_required = 1` makes a check mandatory before launch. The default is 0, so existing campaigns are unaffected.
- **Emergency stop** (FR-MKT-008, BRU-MKT-13, T-07): `action_emergency_stop(reason)` on a running or paused campaign.
  - It pauses every journey and exits every member with the reason.
  - It **cancels every queued, unsent M27 message** of the campaign and of its journey members.
  - It records who, when, why and how many were cancelled, and sets the new state **halted**.
  - A halted campaign does not resume.
- **Calendar** (FR-MKT-007): `calendar_conflicts` names any other planned or running campaign that shares the channel, overlaps the window, and targets a shared segment (or everyone).
- **Suppression** (FR-MKT-010/013, BRU-MKT-08):
  - `intersect_segment_ids` keeps only members of every listed segment.
  - `suppress_open_complaints` (default **on**) uses M34's `fix.complaint` that is not accepted, closed or rejected.
  - `suppress_credit_hold` uses `fix.credit.profile.credit_hold`.
  - `suppress_recent_days` leaves out anyone who received another campaign that started in the last N days.
  - These apply to the estimate, which reports how many each removed; to launch; and to **every journey enrolment**.
  - They are fixed once the campaign launches, like the rest of the audience.
- **Journeys** (FR-MKT-019/020, BRU-MKT-06/14):
  - New fields: `conflict_group` and `priority` (1 = highest).
  - Entering a higher-priority journey exits the party from a lower one in the same group. A party already in an equal or higher one is not entered, and the campaign chatter says how many.
  - The holdout is never enrolled in any journey of the campaign (BRU-MKT-14). Before, only the campaign-audience kind excluded it.
  - `exit_on_complaint` and `exit_on_conversion` (both default on) are re-checked before every step.
  - `action_exit_member(reason)` takes a party out by hand.
- **Creative content** (FR-MKT-024..028, BRU-MKT-09/10, T-09/T-10, AUT-MKT-14). Approval is refused unless all of these hold:
  - copy has both an English and a Bengali body; a visual asset has its Bengali version reference;
  - the Bengali text contains Bengali script;
  - personalisation uses only `{name}`, `{device}`, `{service}`, `{branch}`, `{expiry_date}`, `{points}` and `{voucher}`, the same ones in both languages;
  - an expiry date in the future is set.

  After approval:
  - Each approval increments `version`.
  - Copy and expiry are frozen while the creative is pending or approved.
  - An expired creative **blocks launch and resume**.
  - A daily job warns the owner 7 days ahead and retires a creative when it expires.
- **Experiment significance** (FR-MKT-031):
  - `action_conclude` now takes the reach and conversions of each variant and stores them (guarded).
  - It computes the rates, the two-proportion p-value and the confidence.
  - A winner is accepted only when p < 0.05 (param `cd_campaign.experiment_alpha`) and the named variant converted better.
  - "No significant difference" is refused when the difference *is* significant.
- **Committed spend** (FR-MKT-033, BRU-MKT-11, AUT-MKT-12):
  - A spend is recorded as committed (order placed) or incurred (invoiced).
  - A commitment counts against the budget but not as actual spend until **Mark Invoiced**.
  - The stage never changes by a write.
  - At 80 % of the budget spent or committed, the owner is notified once. At 100 %, a running campaign pauses until the budget is raised and approved again.
- **`fix.attribution.result`** (FR-MKT-036/037, AUT-MKT-11). `action_measure` on a completed or halted campaign adds one row:
  - **Revenue** is posted customer invoices less refunds, per party, in the campaign window plus the attribution model's lookback.
  - **Reached and holdout groups:** for each, the buyers, the buy rate and the revenue.
  - **Incremental figures:** the holdout baseline is the holdout's revenue per head × the reached count. Incremental revenue and incremental buyers are measured against it.
  - **Attribution:** attributed conversions and revenue from the touch ledger under the pinned model.
  - **Cost and return:** cost is actual plus committed spend; incremental ROI is computed on it.
  - A row is flagged when it was measured before the window closed.
  - A result is never typed, edited or deleted; measuring again adds a row.
- **Ad slot** (FR-MKT-030): `position` and `page_context`. Two active placements cannot hold the same placement, page context and position in overlapping windows.
- **Access:**
  - Staff create and edit programmes and capacity checks, but never delete them. Only the Marketing Manager may delete a programme.
  - Staff read results only.
  - Company and operating-unit isolation rules were generated for the three new models.
  - New group `cd_campaign.group_capacity_override`; only admin holds it.
- **Daily job:** "Campaigns: warn of and retire expired creatives".
- **Older fixtures updated to the new rules:**
  - `test_a03_p2_campaign.py`: the creative fixture now carries a Bengali version and an expiry.
  - `test_m35_capture_live.py`: the experiment conclusion now carries its figures.

## Evidence

- **Static page guard** `cd_p03_portal/tests/test_m35_capture_buttons.py`, raised to the pass-2 expectations: **16 of 42 checks fail on HEAD `742e46bc`, 42/42 pass on the build.** It checks:
  - each page's captures, by form;
  - the pick-and-act forms (stop, exit, measure, conclude with figures);
  - stamps never writable, the result never writable;
  - access rows and isolation rules for the new registers;
  - that the foreign M10 chip opens M10's form and has a read-only M35 list;
  - the bilingual and expiry fields on the creative form, journey priority and exits, and the campaign definition.
- **Live tests** `cd_campaign/tests/test_m35_capture_pass2.py`: **23/23** on a private clone (`fix_test_m35c2`, a clone of `fix_test_m30c2` upgraded with this code).
  - They run as non-admin users through `/p03/model/write|action` wherever the workspace drives the step.
  - Pass 1's live suite and the rest of `cd_campaign` still pass: **67/67**.
- **Mutation check:** 20 defects re-introduced one at a time; **20/20 turn the suite red**.
  - On the first run, 17/20 were red. The three survivors were weak tests, not code defects:
    - the clerk refused an override for having made the check (segregation of duties), so the group check was never exercised;
    - a "both languages" refusal matched a different message by coincidence;
    - access rights hid the model's own "never typed" guard on results.
  - The tests now assert each one directly.
- **Regression** on the same clone: cd_campaign; M10 campaign hooks and loyalty live; M40 co-marketing; the contact-centre A03 approval-bypass, gap-closure and zero-trust suites; M07 A03; and the A03 portal guards (registry coverage, sub-module mapping, write whitelist, declared-gap reports, children shown, estate pages, create buttons, screen wiring, pickers).
  - **1,273 passed, 18 skipped, 3 failed, 4 errors.**
  - **Every failure reproduces on the base code** against the same database: 3 contact-centre tests (tariff cost, survey-question labels, M10 20 % redemption cap) and 4 brand-reimbursement report tests. These are clone-data fixtures; the clone's `fix_entity` rejects the tests' inserts.
- **Two defects found by the guards and the walk, both fixed before landing:**
  - The children guard found the programme form hid its campaigns. A read-only grid was added to fix that.
  - The **live walk** then showed that grid broke saving: a new programme's save posted `campaign_ids`, which that form may not write ("This screen does not edit campaign_ids"). The grid was removed. Campaigns stay on their own register (Campaign Manager, Campaign Calendar with its programme column), the programme form shows the roll-up, and the pair is listed as incidental in the guard.
  - The walk also showed three new list chips labelled with raw screen ids ("M35-programmes"). All six new lists are now named in the module's screen groups, in English and Bengali.
- **Browser walk.** Headless Chromium against a private server on the clone (port 8149, worktree code, signed in with the dev login):
  - all 8 pages show their "+ New";
  - all 13 chips under "Forms Capturing It" open forms with inputs, including M10's reward form;
  - all 27 new or changed lists and forms render; no screen chip shows a raw id; **0 console errors**;
  - a programme saved through the real form (`WALK-PROG-…`, 1 Nov 2026 to 31 Jan 2027, BDT 90,000, owner defaulted).

## Gaps left

- **No M02 capacity projection exists** (T-08). The capacity figure is entered by the planner with its source, and the projection is reach × expected response. When M02 publishes a capacity projection, the check should read it rather than take it typed.
- **The capacity check is not mandatory by default.** `cd_campaign.capacity_check_required` is 0, so only an insufficient check blocks a launch. Making it mandatory is the Marketing Head's call.
- **Nobody on fix_real holds Capacity Override or Marketing Manager.** Until the owner names the Operations Director (R05) and the Marketing Manager (R23), only admin can override a capacity check or put an attribution model in force.
- **Approval routing by audience size** (FR-MKT-002, BRU-MKT-04) still uses the budget DOFA ladder only. The estimate is shown to the approver, but a large audience on a small budget is not routed higher. No threshold is defined in the spec.
- **Revenue for measurement is invoiced revenue.** A response, voucher redemption or service order without a posted customer invoice is not counted. fix_real's GL holds take-on entries only, so a measurement there reads 0 until invoicing runs in the estate.
- **Predictive audiences** (FR-MKT-015, P3) and **seasonal campaign templates** (scope 13, AUT-MKT-13) are not built.
- **Lead hand-off** (FR-MKT-021/039) is unchanged: a journey step raises an M07 lead, and leads returned unqualified are not yet routed into a nurture journey automatically.
- **Approval routing for a capacity check is single-step.** The Operations Director overrides directly; there is no M63 inbox task for it.
