# M39 Subscriptions & Recurring: sub-module capture audit

**Date:** 19 Nov 2026 · **Area:** A04 · **Workspace fragment:** `cd_p03_portal/static/src/a04/m39.js`
**Backend:** `cd_subscription` 19.0.1.4.0 (`models/fix_m39_capture.py`, imported last), `cd_p03_portal/controllers/a04/m39.py`
**Spec:** `03_Modules/C_Commercial_Pricing_and_Revenue/M39_Subscription_and_Recurring_Revenue.md` §3.1, §5 (FR-SUB-001..044), §8, §9 (BRU-SUB-01..20), §10.1, §11
**Branch:** `fix/m39-capture-buttons` (worktree `1000 fix/m39cap-wt`)

The user reported that not every M39 sub-module page has a relevant data-capture button. Each of the ten
pages was checked against what the spec says a person records there, and against what the engine actually
renders: the guard runs the workspace's own `fregCreate` / `fregPanels` over the real registry.

## What the code offered (HEAD 742e46bc)

| # | Page | "+ New" | Chips | Problem |
|---|---|---|---|---|
| 1 | Subscription Object | + Subscription | Subscription | OK |
| 2 | Billing Schedules | **none** | Billing Schedule | The chip opened a **blank cycle charge**. A charge typed there was never invoiced (only `action_generate_charge` raises the invoice) and then **blocked the real cycle** (one charge per subscription and period). There was no schedule at all: billing rolled `next_invoice_date` by a fixed 30 / 91 / 365 days. |
| 3 | Charge Models | **none** | Billing Schedule (the same blank charge) | No charge lines. A subscription had one amount; no one-time, quantity-based or usage charge, and no rating tariff (FR-SUB-004/006/024, P0). |
| 4 | Quantity & Proration | **none** | Plan Change | The proration list said `create: false`. No quantity change existed (FR-SUB-005/012, P0). **Defect: an approved proration was never billed.** Nothing called `_fix_mark_invoiced` and nothing consumed `subscription.proration_approved`, so an approved upgrade charge or downgrade credit reached no invoice. |
| 5 | Usage Rating | **none** | **none** | The overage rate was typed on every reading (it could be typed as 0). The same source record could be metered twice (T-05). Usage that could not be rated had no queue (FR-SUB-030, BRU-SUB-08). |
| 6 | Billing Runs | **none** | **none** | The page listed cycle charges. There was no billing run, dry run, exception disposition or review (FR-SUB-031..038, BRU-SUB-17, P0). Billing was a per-subscription button or a switched-off daily job. |
| 7 | Credits & Adjustments | **none** | Plan Change | No service credit, dispute settlement, goodwill or correction record (FR-SUB-037, P0). |
| 8 | Suspend / Cancel / Renew | **none** (`create: false`) | **none** | Pause, resume and renewal did not exist. Cancellation (`action_cancel`) validated no notice (BRU-SUB-13) and was not even offered on the M39 subscription list. |
| 9 | Autopay & Dunning | **none** | Dunning Step | The mandate list said `create: false`. The "Dunning Step" chip opened a **blank subscription form**, so it created a subscription. |
| 10 | Metrics & Forecast | **none** (`create: false`) | **none** | Churn had no reason or competitor (FR-SUB-042, §10.1 `fix.churn.record`). **MRR counted a quarterly or annual amount as monthly** (BRU-SUB-15). |

No M39 record exists yet on fix_real or fix_dev (0 subscriptions, charges, usage readings, prorations and
mandates), so nothing had to be migrated.

## What was built

All decision and lifecycle stamps are guarded by `fix.guarded.mixin`, absent from the generated write
whitelist and read-only on the forms. Every new model carries company and operating unit, with generated
isolation rules (14 new rules).

**Page 2, Billing Schedules:** `fix.subscription.schedule` and its generated periods.
- Terms: anniversary or calendar alignment, billed in advance or in arrears, a partial first period prorated by day or billed in full, first period start and number of periods (1-36).
- The periods are generated (the grid is read-only) with the plain-language basis of each amount.
- **Activate** is done by a billing user who did not set it up. It supersedes the active schedule and moves the next invoice date to the first period. It is refused if the schedule overlaps a cycle already billed.
- From then on billing bills the next planned period: its own dates and its prorated amount. The 90-day forecast reads the planned periods (FR-SUB-010).

**Page 3, Charge Models:** `fix.subscription.line` with rate bands.
- Recurring (every cycle), one-time (the next cycle, once) or usage. Recurring and one-time lines are quantity × unit rate.
- A usage line is the rating tariff: metric, included quantity, and a flat rate, graduated tiers or volume bands.
- A Subscription Officer raises it. A billing user who did not raise it approves it, after which its terms are fixed (a quantity change is a proration; a new rate is a new line). Lines are ended, never deleted.
- The subscription's MRR contribution adds its active recurring lines.

**Page 4, Quantity & Proration:**
- A plan change can now be a **quantity change** on a recurring charge line: (new − old quantity) × rate × unused days ÷ cycle days. On approval the line takes the new quantity, and the base price is untouched.
- **Fix:** every approved proration is now netted into the next cycle charge, marked invoiced with that cycle's invoice, and never billed twice. A credit that would take the charge to zero or below waits for the following cycle (BRU-SUB-11: credit against future charges).
- "+ New Plan / Quantity Change" opens the proration form.

**Page 5, Usage Rating:**
- A reading names its tariff (or is matched to it by metric). The tariff then sets the metric, the commitment and the rate, and the overage is rated by the tariff. A rate typed on the reading is ignored.
- Source and source key: the same source record cannot be metered twice on a subscription.
- A reading that cannot be rated (no tariff and usage above the commitment with no rate, or a cancelled subscription) is kept as an **exception** with its cause. Billing skips it. The new **Unrated Usage Queue** lists them; **Re-rate** releases one once it has a tariff.
- "+ Record Usage Reading".

**Page 6, Billing Runs:** `fix.subscription.billing.run` with one unit per subscription.
- Scope: cycles due by a date, optionally one cycle, operating unit or customer.
- **Dry run** writes nothing but the units: amount, and an exception with its cause (no amount, no M08 contract (BRU-SUB-01), no customer, already billed, unrated usage).
- Every exception needs a disposition (skip, or bill anyway where that is allowed). **Review** is done by a Finance Manager who did not run the dry run (BRU-SUB-17).
- **Commit** bills unit by unit, each in its own savepoint. A failed unit is marked and the run is resumable; a committed unit is never billed again (T-02, FR-SUB-038).
- The cycle-charge list stays on the page, and its chip now opens an existing charge only. The charge shows **what it is made of** (base, usage overage, lines, prorations, adjustments, credits carried forward). The same text is added to the draft invoice line (BRU-SUB-19).

**Page 7, Credits & Adjustments:** `fix.subscription.adjustment`.
- Service credit, dispute settlement, goodwill or correction; credit or debit; reason and evidence; optionally the cycle concerned.
- A credit is approved under DOFA from the M63 inbox; a debit by a billing user. The author never approves it (BRU-SUB-18).
- On approval it is applied to the next cycle charge, then stamped with that charge and invoice.

**Page 8, Suspend / Cancel / Renew:** `fix.subscription.lifecycle`.
- Pause (with a "paused until" date), resume, cancel or renew, with a reason and an effective date (today or later).
- **Cancel** is refused unless notice was received at least the contract template's notice period before the effective date (`notice_period_days`, fallback `cd_subscription.cancellation_notice_days` = 30) (BRU-SUB-13).
- **Renew** sets a new term end. A price escalation needs the notice sent date, channel and evidence at least `cd_subscription.price_change_notice_days` (30) ahead (BRU-SUB-07). The escalation becomes a plan change that still goes through its own approval.
- Approval: a pause by a Finance Manager, the others by a billing user, never the requester (§8 guards). A future date is applied by a new daily job, which also ends a pause on its date. A paused subscription is not charged (BRU-SUB-12).

**Page 9, Autopay & Dunning:** "+ New Autopay Mandate" (the existing consent-checked mandate form). The Dunning Step chip opens an existing subscription only.

**Page 10, Metrics & Forecast:** `fix.subscription.churn`.
- Reason (price, service quality, competitor, business closed, non-payment, consolidation, other), with the competitor named when that is the reason.
- Logo churn is recorded once, only on a cancelled or churned subscription. Lost MRR is stamped from the subscription's monthly value; the start cohort is derived.
- **MRR fix:** MRR, ARR, the MRR waterfall and the plan mix use the monthly value: recurring amount plus active recurring lines, divided by the cycle's months (BRU-SUB-15).

## Evidence

- **Page guard** `cd_p03_portal/tests/test_m39_capture_buttons.py` runs the engine's own `fregCreate` / `fregPanels` in node over the real registry: **32 checks**.
  - Against unmodified HEAD (742e46bc), in a throwaway tree, **24 fail**: the missing "+" on pages 2-10, the pages that listed the wrong record, both blank-opening chips (cycle charge, dunning step), and the missing queue, quantity and tariff fields.
  - On the branch, **32/32 pass**.
- **Live suite** `cd_subscription/tests/test_m39_capture_live.py`: **26 tests** on a private clone of fix_dev (`fix_test_m39`, after `-u cd_subscription,cd_p03_portal`, 0 errors). They run as non-admin users (clerk, two Subscription Officers, two billing users, a Finance Manager, a DOFA tier-1 holder), on the ORM and through `/p03/model/write` and `/p03/model/action`. **26/26 pass.**
- **Mutation check:** 20 mutants, each removing one new rule. The first run killed 17. The 3 survivors were real test gaps: a reading on a tiered tariff (a flat tariff gave the same answer either way), a schedule's author activating it, and a lifecycle requester approving their own request (the old test was stopped by the role check first). Three tests were added; all 3 now turn red, so **20/20 are killed**.
- **Regression** on the same clone: every suite that touches subscriptions (`cd_subscription`, `cd_settlement_ext` A02/A08 M53, `cd_contract_core` A04, `cd_corporate_portal`, `cd_event_outbox`) plus the portal standards (estate pages, A03/A04 forms-show-children, A04 write whitelist, registry and sub-module mapping, KPI tiles, M53 capture, pickers, report export): **1,641 tests, 59 failures**.
  - The same six files were run with **unmodified HEAD code** on the same database: **every one of the 59 fails there too.** None fails only on the branch.
  - Their causes are outside M39: no VAT rate or GL account in the companies those tests create, the BRU-AST-03 provisional-identity rule on the warranty device fixture, flat M36 forms, and a branch mismatch in the corporate portal.
- **Headless browser walk** (Playwright, private server on port 8159 running this branch on a second clone, signed in with the dev login):

| Page | "+" button | Chips (every one opened its form) |
|---|---|---|
| 1 Subscription Object | + Subscription | Subscription |
| 2 Billing Schedules | + New Billing Schedule | Billing Schedule |
| 3 Charge Models | + New Charge Line / Tariff | Charge Line |
| 4 Quantity & Proration | + New Plan / Quantity Change | Plan Change · Charge Line |
| 5 Usage Rating | + Record Usage Reading | Usage Reading |
| 6 Billing Runs | + New Billing Run | Billing Run · Cycle Charge (existing only) |
| 7 Credits & Adjustments | + New Credit / Adjustment | Credit / Adjustment · Plan Change |
| 8 Suspend / Cancel / Renew | + Pause / Resume / Cancel / Renew | Lifecycle Request |
| 9 Autopay & Dunning | + New Autopay Mandate | Autopay Mandate · Dunning Step (existing only) |
| 10 Metrics & Forecast | + Record Churn Reason | Churn Record |

  23 screens (12 lists, 2 reports, 9 forms) loaded with no "not served" or field errors, and there were **0 console errors**. A Billing Run was **saved through its form** (BR/2026-11-19/00009, Draft).
- `ruff check` and `ruff format` (pinned 0.8.4) are clean. `fix_isolation_rules.xml` and `writable.py` were regenerated by their generators; only cd_subscription's rules file was kept from the isolation generator (its drift in 12 other modules was reverted).
- **Role holders** (direct membership): fix_real has 1 Subscription Officer, 1 Accountant and 4 Accounting Managers; fix_dev has 1, 2 and 1.

## Open (owner decisions, not built)

- **BRU-SUB-01 (every subscription has an M08 contract)** is reported by the billing run as an exception, not enforced on create. The A08 and quotation paths create subscriptions without a contract today; making it mandatory needs the owner's call and a data decision for those paths.
- **Final billing on cancellation (FR-SUB-020, BRU-SUB-14):** unbilled usage and the M08 early-termination charge are not yet settled in a final period. M08's `fix.contract.termination.penalty_amount` exists; linking it is the next step.
- **Downgrade at period end by default (FR-SUB-015)** and **backdated change within a governed window (FR-SUB-017)** are not built; a plan change takes effect today or later.
- **Late usage into the next open period (FR-SUB-025, BRU-SUB-09)** and **rerating as an adjustment (FR-SUB-028)** need M19's period-close status; corrections are made today as a correction adjustment.
- Consolidated and split billing accounts (FR-SUB-035/036, `fix.billing.account`) and the MRR snapshot / movement decomposition (FR-SUB-041, NRR) remain open.
- **People on fix_real:** count the holders of Subscription Officer, billing (Accountant) and Finance Manager before go-live. The new maker-checker rules need two different people in each pair.

## Deploy (19 Nov 2026, owner-approved)

1. The owner approved the deploy ("Yes, deploy now"). M35 was already running one combined `-u` wave covering every module behind its code, and the wave included `cd_subscription` and `cd_p03_portal`. M39 therefore ran no upgrade or restart of its own.
   - fix_real was upgraded at 12:38 UTC and fix_dev at 12:41.
   - M35 held the single restart until M36's `cd_quotation` was also upgraded, so no module was loaded without its tables.
2. Read-only check on **both** databases:
   - cd_subscription 19.0.1.4.0;
   - all 9 new tables and 7 new columns;
   - 21 ACL rows and 14 isolation rules;
   - the lifecycle cron installed and active.
3. One restart, by M35, at 12:51 UTC: 8069 (fix_real) = PID 52556, 8090 (fix_dev) = PID 80704. `/web/login` answers 200 on both. No module is behind its code on either database.
4. A headless walk on **both** live servers (dev login, nothing saved) shows the same result as the private server: all 10 pages show their "+" and chips, every chip opens its form, 23 screens and forms load, and there are **0 console errors**.

## State

- Code `fix(CD-M39-01)` 2f539ad0 and this report are on `fix/a03-live-data-and-pending-work`. The shared branch and `fix/m39-capture-buttons` are pushed.
- **LIVE on fix_real (8069) and fix_dev (8090)** since the 12:51 UTC restart.
- No M39 records exist yet on either database. Before go-live, give the maker-checker pairs two different people each (Subscription Officer / billing user / Finance Manager).
