# M35 Marketing Campaigns — Sub-module Capture Audit (2026-11-14)

**Question.** The user saw M35 sub-module pages without a relevant data-capture button.

**Sources compared.**
- Spec: `1000fix_ERP_Module/03_Modules/B_Customer_Engagement_and_Experience/M35_Marketing_Campaigns_and_Demand_Generation.md`
  - §3 scope, §5 FR-MKT-001..040, §6 T-01..T-11, §9 BRU-MKT-01..14, §10.1 owned entities, §13 roles.
- Code (HEAD `cc24bf5a`):
  - `cd_campaign` (models)
  - `cd_partner/models/fix_comarketing.py` (the M40 co-marketing link)
  - `cd_p03_portal/static/src/a03/m35.js` (the workspace)
  - `controllers/a03/m35.py` (surfaces and reports)
- Data: fix_real has **0** M35 business rows (campaigns, journeys, offers, creatives, ads, experiments, touches) and 2 M33 segments. No live record is affected by the changes.

## 1. Findings: what each page captured, against what the spec says it should

The Function Register gives M35 eight sub-module pages. The guard test `test_m35_capture_buttons.py` evaluates the pages with the engine's own `fregCreate`/`fregPanels`. On HEAD, **15 of its 32 checks fail**.

| # | Page | "+ New" on HEAD | What the spec says the page captures | Verdict |
|---|---|---|---|---|
| 1 | Campaign Planning & Approval | + Campaign | Campaign definition, brief, approval (FR-MKT-001/002) | OK |
| 2 | Audience from Segments | **+ Campaign** (the module's record) | The audience composed from governed M33 segments: include/exclude, suppression, holdout %, post-suppression reach (FR-MKT-009..014, BRU-MKT-02/03/14, entity `fix.audience.definition`) | **Wrong capture, and the data could not exist.** A campaign could not name a segment. Its audience was a **typed partner filter** (`audience_domain`), which BRU-MKT-02 forbids, or one of four fixed types. Three of those types need the typed filter to work at all. There was no holdout and no reach estimate before approval. |
| 3 | Journey Orchestration | + Customer Journey | Journeys and behaviour triggers (FR-MKT-016..022) | **Partial.** The page listed triggers, but the Behaviour Trigger form had no chip on it. The Journey Members list was on no page. |
| 4 | Content & Offers | + Creative Asset; chips Creative, Offer | Content library, offers (FR-MKT-024..028) | OK |
| 5 | Experimentation | + A/B Experiment; **no chips** | A/B test with variants, allocation, winner (FR-MKT-031, entity `fix.ab.test`) | **Wrong data.** Anyone could type the experiment's state (draft → concluded) and its "winner" note on the form. It had no start, no conclusion, no winner field, and nothing said what was being tested. |
| 6 | Budget & Attribution | **none** | Budget planning, spend tracking incl. spend outside the estate, budget control, versioned attribution model (FR-MKT-032..037, BRU-MKT-11/12, entities `fix.campaign.budget`, `fix.attribution.model`) | **No capture at all.** The page listed the touch ledger, which the system writes. Spend booked outside the estate (media, print, agency) had no record, so "actual spend" was message cost plus offer discounts only, and nothing stopped spend passing the approved budget. The attribution model was a method argument, not a record. |
| 7 | Portal Advertising | + Portal Ad Placement; **no chips** | Placement by page and position, advertiser, run window (FR-MKT-030, `fix.ad.placement`) | **Partial.** The button was right, but there was no advertiser and no run window. |
| 8 | Co-Marketing | **+ Campaign** | Brand co-marketing with partners (scope item 14; M40 owns the partner) | **Wrong capture.** The campaign form could not name a co-marketing partner, although the link exists (M40 `fix.campaign.partner_ids`). The page's report said "a dedicated co-marketing partner model does not exist", which was stale. |

**Integrity findings found on the way:**

- **Touch ledger.** Every internal user could create and edit attribution touches (`fix.campaign.touch`, ACL 1,1,1,0), including a conversion's value. That would forge attributed revenue. The ledger is written only by the delivery-log harvest (sudo).
- **Report.** The Attribution & ROI pack did not use the multi-touch attribution model that exists in code. It divided budget by responses.
- **Approval report.** The approver never saw a post-suppression reach (BRU-MKT-03).

## 2. What was built

### Models: `cd_campaign/models/fix_campaign_capture.py` (cd_campaign 19.0.0.2.0)

- **Audience on `fix.campaign`.**
  - New fields: `segment_ids` / `exclude_segment_ids` (M33 `fix.segment`), `holdout_pct` (0–50) and `holdout_key`.
  - New audience type "Governed M33 Segments". It resolves to the current members of the included segments, minus the excluded ones. Exclusions apply to every audience type.
  - `action_estimate_audience` writes the reach after consent, DND and holdout, with a breakdown. Requesting budget approval refreshes it (AUT-MKT-01).
  - The holdout is deterministic: a SHA-256 bucket of key and party (T-05). Campaigns that share a key share one holdout group.
  - At launch the holdout is removed from the recipients and recorded in `holdout_partner_ids` (BRU-MKT-14). Held-out parties are never enrolled in a journey.
  - Audience fields are fixed once the campaign leaves draft. A changed audience clears a stale estimate.
  - The estimate, the holdout and the pinned model are guarded fields.
- **`fix.campaign.spend`**: spend booked outside the estate, by category, with supplier and invoice reference.
  - It counts in the campaign's recorded spend.
  - A spend that would take the campaign past its budget is refused until the raised budget is re-approved (BRU-MKT-11).
  - It is never edited or deleted. It is voided with a reason (who and when are stamped).
- **`fix.attribution.model`**: code, method (the five models already in `fix_attribution.py`), lookback and auto-incremented version.
  - One model is in force at a time. A model that is or was in force is frozen; a change is a new version.
  - `action_complete` pins the model in force on the campaign, so a later model never restates it (BRU-MKT-12, T-06).
  - Only the new **Marketing Manager (M35)** group (or system) writes it. Staff read it.
- **Experiment.**
  - New fields: what is tested, variant labels, winner, started/concluded stamps.
  - `action_start` and `action_conclude(winner, note)` are the only way the state and the winner move (guarded).
  - The design is fixed once the experiment starts.
- **Ad placement**: advertiser (`res.partner`) and a run window that must run forward.
- **Security.**
  - Touch ledger: staff read-only.
  - Spend: staff record and void it, never delete it.
  - Attribution model: staff read; Marketing Manager writes.
  - Company and operating-unit isolation rules for spend (regenerated).

### Workspace: `m35.js`, `controllers/a03/m35.py`, `controllers/a03/writable.py` (regenerated)

| # | Page | "+ New" now | Chips now |
|---|---|---|---|
| 1 | Campaign Planning & Approval | + Campaign | Campaign |
| 2 | Audience from Segments | **+ Define Campaign Audience** (pick a draft campaign → segments, holdout) | Define Campaign Audience; list "Campaign Audiences" with **Estimate Reach** |
| 3 | Journey Orchestration | + New Customer Journey | Journey, **Behaviour Trigger**; Journey Members list placed |
| 4 | Content & Offers | + New Creative Asset | Creative Asset, Offer |
| 5 | Experimentation | + New A/B Experiment | A/B Experiment, **Conclude an Experiment** (winner and finding); **Start Experiment** action |
| 6 | Budget & Attribution | **+ New Campaign Spend** | Campaign Spend, **Void a Spend**, **Attribution Model**; lists Campaign Spend, Attribution Models (**Put In Force**) |
| 7 | Portal Advertising | + New Portal Ad Placement | Portal Ad Placement (with advertiser and window) |
| 8 | Co-Marketing | **+ Name Co-Marketing Partners** (pick a campaign → M40 partners) | Co-Marketing Partners, **MDF Co-Funding** (M40's form); lists Co-Marketing Campaigns, partner MDF |

Other workspace changes:

- **Campaign form.**
  - The audience tab no longer offers the typed filter. Its choice is "Governed M33 Segments" or "All Registered Customers".
  - It shows the segments, holdout, estimated reach and the pinned attribution model.
- **Reports.**
  - **Attribution & ROI** now credits conversions through the touch ledger. A completed campaign uses its pinned model; any other uses the model in force. It shows credited conversions, credited revenue and return on spend only where every credited conversion has a known value, and recorded spend.
  - **Co-Marketing Partner Report** shows the named partners, the partner fund (accrued, approved or paid MDF) and the company's share of the budget.
  - **Planning & Approval** shows the estimated reach after suppression.
- **List columns.** The grid prints a many2many as raw ids, so the lists show computed name columns (`segment_names`, `exclude_segment_names`, `comarketing_partner_names`).

## 3. Evidence

- **Guard test** `cd_p03_portal/tests/test_m35_capture_buttons.py` (node evaluates the real registry): **15/32 fail on HEAD, 32/32 pass** on the build.
- **Live test** `cd_campaign/tests/test_m35_capture_live.py`: 17 tests, run as non-admin users through the workspace endpoints on `fix_test_m35`. **17/17 pass.**
  - Mutation check: 6/6 mutants caught (holdout subtraction, budget control, audience freeze, model freeze, winner check, model pin).
- **Regression on `fix_test_m35`, all pass.**
  - cd_campaign full suite, M40 `test_comarketing_links`, `test_declared_gap_reports` and `test_report_export_standard`: 256 tests.
  - A03 control suite and gap-closure campaign tests: all pass; skips are by design (no rows, no guarded fields).
  - Estate page standard, A03 sub-module mapping, write whitelist, registry coverage and screens wiring all pass.
  - The one failure, `test_no_submodule_page_offers_another_records_button`, flags M19/2 and M30/1. It fails identically without this change.
- **UI on a private server** (port 8078, worktree code, `fix_test_m35`):
  - Page 2: "+ Define Campaign Audience" → picked the draft campaign → set segments, exclusion and a 10% holdout → saved ("Saved ✓").
  - Estimate Reach → "10 in the audience, 1 held out: 9".
  - Page 6: "+ New Campaign Spend" → saved BDT 15,000 → recorded spend 15,000, budget remaining 25,000.
  - Pages 3, 5, 7 and 8 show the buttons and chips in the table above. MDF Co-Funding opens M40's form. No console errors.

## 4. Left for the owner (not buildable without a decision)

1. **Who is the Marketing Manager?** The `cd_campaign.group_marketing_manager` group exists (admin only). The role map gives R-23 only the price-releaser group, and fix_real has no marketing role holders. Until someone is granted the group, only admin can put an attribution model in force.
2. **Retire the typed audience filter?** BRU-MKT-02 forbids it. The workspace no longer offers it, but the field and the three audience types that depend on it (warranty holders, corporate AMC, dormant 90d) remain in the backend.
   - Recommendation: define those three as M33 segments, then remove the field. This is the CDO's call.
3. **M02 capacity check (FR-MKT-006, BRU-MKT-05)** has no M02 capacity projection to read. It is not built.
4. **Programmes/calendar (FR-MKT-005/007)** have no model. Content expiry and the bilingual body of a creative (BRU-MKT-09/10) are not on the creative record. These are not part of the capture defect and are not built.
5. **Committed vs actual spend (FR-MKT-033).** Only actual spend is recorded; there is no commitment line.
