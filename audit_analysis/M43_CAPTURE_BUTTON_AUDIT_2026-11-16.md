# M43 Demand Planning & Replenishment — Sub-Module Capture Audit (2026-11-16)

**Trigger.** The user observed that not every M43 sub-module page has a relevant data-capture button.

**Sources**
- Spec: `1000fix_ERP_Module/03_Modules/E_Supply_Chain_and_Inventory/M43_Demand_Planning_and_Replenishment.md`. Sections used: §3 scope, §5 FR-DPL-001…032, §6 T-01/T-05/T-09, §8 lifecycles, §9 BRU-DPL-01…20, §10.1 owned entities.
- Code:
  - `cd_p03_portal/static/src/a06/m43.js` (the page registry);
  - `cd_p03_portal/controllers/a06/m43.py` (surfaces, packs);
  - `cd_demand_plan/models/fix_demand_ops.py` and `fix_demand_plan.py` (the seven M43 models).
- Live data: fix_real holds **no M43 record of any kind** (0 forecasts, segments, policies, plans, reviews, rebalances, scenarios). The Demand Planner role has 1 holder (admin) and the Demand Plan Approver role has none. fix_real has 292 stock locations and no van locations.

## 1. What was there (HEAD 19773ee8)

The pages were evaluated with the engine's own `fregCreate` / `fregPanels` in node — how the browser decides what a page shows. The guard `test_m43_capture_buttons.py` failed **22 of its 43 tests** on HEAD.

| # | Page | "+ New" | Form chips | Defect |
|---|---|---|---|---|
| 1 | **History & Cleansing** | **none** | **none** | `create: false`. The page listed forecasts. No outlier exclusion, outlier replacement, reclassification or censored-demand correction could be recorded (FR-DPL-003/004, T-01, BRU-DPL-05/19); `fix.demand.adjustment` did not exist. |
| 2 | Segmentation | Segment | — | No chip. |
| 3 | Forecast Orchestration | Forecast | Review Cycle | No forecast chip. No demand driver (installed base, contract, campaign, seasonality, branch opening) existed (FR-DPL-013). |
| 4 | **Accuracy Tracking** | **none** | **none** | `create: false`. Nothing on the page could be captured. |
| 5 | Safety Stock & ROP | Policy (module) | Policy Assignment | No service-level target per segment existed (FR-DPL-018, P0); a policy's service level was typed freely. |
| 6 | **Lead-Time** | **none** | **none** | `create: false`. The page listed policies. There was no lead time per supplier and nowhere to keep the supplier's **quoted** figure beside the actual (FR-DPL-019, BRU-DPL-09). |
| 7 | Planned Orders | Plan | — | No chip. The "New-Part Introduction" report sat on the page, but no new-part recommendation existed (FR-DPL-030). No end-of-life / last-time-buy plan existed (FR-DPL-031, BRU-DPL-14). |
| 8 | Multi-Echelon Rebalancing | Rebalance | Rebalance Proposal | The van-par report sat on the page, but no van par could be proposed, approved or published (FR-DPL-029 P0, BRU-DPL-12). No network stocking policy existed (FR-DPL-027 P0). |
| 9 | What-If | Scenario | — | No chip. |

In summary:
- 3 of the 9 pages captured nothing (1, 4, 6).
- 4 more (2, 3, 7, 9) had a "+ New" but no form chip.
- Eight §10.1 owned entities had no model: demand adjustment, demand driver, service-level target, lead-time model, NPI recommendation, EOL plan, van par recommendation, network policy.

## 2. What was built

### Backend — `cd_demand_plan` 19.0.0.4.0, new file `models/fix_demand_capture.py`

Each record carries its company, a sequence number, the person who prepared it, and inputs that freeze once it leaves its first state. Measured figures, states and approval stamps are guarded (`fix.guarded.mixin`), so they change only through the actions.

| Page | Record | What it does | Controls |
|---|---|---|---|
| 1 | `fix.demand.adjustment` | Outlier exclude / replace, reclassify to a non-routine stream, censored-demand correction for one part, location and month | **Overlay, never an edit (T-01).** Apply snapshots the M15 consumption beside the treated value; `action_compute_forecast` lays applied adjustments over the M15 series and marks them `*` in "History Used". A reason is required; replace must lower the month, censored must raise it; one applied adjustment per part/location/month; revoke needs a reason. Planner applies. |
| 3 | `fix.demand.driver` | Known demand influence by product, months and location, with expected impact % and basis | An active driver shows on every covering forecast (`driver_impact_pct`, `driver_note`). A planner override can cite it (`override_driver_id`, frozen with the forecast). |
| 5 | `fix.demand.service.target` | Target service level by ABC class, optional criticality and location type | A Demand Plan Approver other than the author activates it; it supersedes the target with the same key. **A policy below the most specific active target of its segment is refused at activation.** The policy shows its segment target. |
| 6 | `fix.demand.lead.time` | Lead time per product and supplier | The quoted days are typed and kept for comparison only. **Measure from Receipts** computes the actual sample count, mean, std dev and P95 from that supplier's posted M16 receipts (PO sent → receipt) and M44 imports (commitment → receipt). Changing the product, supplier or window clears the measurement. One per product and supplier. |
| 7 | `fix.demand.npi` | Initial stocking for a part with no history, by analogy part and/or installed base | An approver other than the preparer decides. Refused when it has neither an analogy nor installed-base data, or when the part already has M15 history. |
| 7 | `fix.demand.eol` | Run-down and last-time-buy quantity | **BRU-DPL-14.** The value is computed from the M15 standard cost. An approver other than the preparer approves it. Above `cd_demand_plan.ltb_cfo_threshold` (500,000 BDT) it then waits for a DOFA Tier 4 (CFO) approver who is neither. Reject needs a reason. |
| 8 | `fix.demand.network.policy` | Central / forward branches / vans per part | An approver other than the preparer approves it, superseding the earlier one. **A replenishment policy or van par at a location it excludes is refused.** |
| 8 | `fix.demand.van.par` | Van par min/max per part per van | **Compute from Van Use** reads the van's own M15 consumption over the replenishment cycle. A par that differs from the suggestion needs its reason. Approval by someone other than the preparer **publishes it as the van's M15 reorder rule** (BRU-DPL-12). |

Also: ACLs (a plain employee only reads; nobody deletes; the CFO group writes EOL), generated company rules, sequences, and the threshold parameter.

### Workspace — `m43.js`, `controllers/a06/m43.py`, `writable.py`

- Eight new list screens, each labelled in the navigation, with their actions served.
- Eight new forms. Every form offers only typed inputs; the regenerated `writable.py` whitelists exactly those fields.
- Every page now has its own capture and a chip for every record it lists:

| # | Page | "+ New" | Chips |
|---|---|---|---|
| 1 | History & Cleansing | Demand Adjustment | Demand Adjustment |
| 2 | Segmentation | Part Segmentation | Part Segmentation |
| 3 | Forecast Orchestration | Demand Forecast | Forecast, Demand Driver, Review Cycle |
| 4 | Accuracy Tracking | Review Cycle | Review Cycle |
| 5 | Safety Stock & ROP | Policy Assignment | Policy Assignment, Service-Level Target |
| 6 | Lead-Time | Lead-Time Model | Lead-Time Model |
| 7 | Planned Orders | Demand Plan | Plan, New-Part Recommendation, End-of-Life Plan |
| 8 | Multi-Echelon Rebalancing | Rebalance Proposal | Rebalance, Van Par Recommendation, Network Stocking Policy |
| 9 | What-If | What-If Scenario | What-If Scenario |

Page 4's record is measured, never typed (BRU-DPL-16: accuracy is not suppressible), so its capture is the review cycle that acts on accuracy.

## 3. Evidence

All runs below are on the worktree `m43cap-wt` (base HEAD 19773ee8) against the private database `fix_test_m43` (cloned from `fix_test`, then `-u all`: exit 0, 0 errors). fix_real was not touched.

- **Engine guard** `cd_p03_portal/tests/test_m43_capture_buttons.py` (43 tests): **22 failed on HEAD, 43/43 pass** after the change.
- **Live ORM + P03 endpoint tests** `cd_demand_plan/tests/test_m43_capture_live.py`: **16/16 pass.** Each test runs the proper path as the real role (Demand Planner, Demand Plan Approver, DOFA Tier 4), then attacks the control: self-approval, a missing reason, a forged state or measured figure through `/p03/model/write`, a clerk calling an action, an excluded location, and a CFO-stage approval by the first approver.
- **Mutation check:** with the overlay disabled and the target check removed, 3 of these tests failed as they should. Restored afterwards.
- **M43 suites together** (all of `cd_demand_plan/tests`, the guard, `test_a06_final_m43_m44.py`): **324 tests, 0 failed, 0 errors, 0 skipped** (JUnit).
- **Regression** (all of `cd_demand_plan` + `cd_p03_portal` tests): 4,552 run, **4,267 passed, 1 failed, 284 skipped**. The one failure, `test_submodule_create_button::test_no_submodule_page_offers_another_records_button`, is **M30 "Branch Master"** (`create: 'module'`), already in HEAD; it is not an M43 defect. The skips are outside M43.
- **Browser** (private server :8073 on `fix_test_m43`, admin): every page showed the intended "+ New" and chips:

  1 `+ New Demand Adjustment` · 2 `+ New Part Segmentation` · 3 `+ New Demand Forecast` + Forecast / Driver / Review chips · 4 `+ New Review Cycle` · 5 `+ Policy Assignment` + Service-Level Target · 6 `+ New Lead-Time Model` · 7 `+ New Demand Plan` + NPI / EOL · 8 `+ New Rebalance Proposal` + Van Par / Network · 9 `+ New What-If Scenario`.

  The Lead-Time and Van Par forms opened (Van Par with its two tabs), with no console errors. The test DB has no products, so the product picker there is empty; fix_real has 16,178.
- Lint: pinned ruff 0.8.4 `check` and `format --check` are clean on every changed Python file; `writable.py` and the isolation rules were regenerated by their generators.

## 4. Deploy to fix_real (8069), 2026-11-16 04:35–04:40 Dhaka

The owner approved the commit and the deploy.

1. **Rebased.** The worktree was moved onto the branch tip 7dd72dab (M42). The only shared file, the generated `writable.py`, merged cleanly; `form_fields.py --a06` regenerates it byte-identical.
2. **Re-tested.** The M43 + M42 guards pass 81/81 on the new base.
3. **Committed** 85961f37 (all hooks passed), then fast-forwarded `fix/a03-live-data-and-pending-work` from 7dd72dab with `update-ref`. Unpushed.
4. **Pre-checks.** The main checkout had no uncommitted files. Among the 83 compared modules, only `cd_demand_plan` was behind its code version, so there was no column gap from other work.
5. **Backed up** to `all_working_folder/1000fix-2/_migration/backups/fix_real_pre_m43_capture_2026-11-16.dump` (49 MB). The archive lists all 1,583 tables.
6. **Upgraded** with `-u cd_demand_plan,cd_p03_portal --stop-after-init`: exit 0, no errors. `cd_demand_plan` is now 19.0.0.4.0, and the 8 new models and 8 sequences exist.
7. **Restarted** 8069 once; the supervisor relaunched it as PID 49276. `/web/login` returns 200 and the boot log has no errors.
8. **Probed** (read-only, admin): `/p03/model/records` serves all 15 M43 models, with 0 rows (fix_real has no M43 data). The served bundle `web.assets_web` (99d6198) contains the new screens and forms.

## 5. Not done — spec gaps outside "a capture button"

- **Lead-time variability in safety stock (FR-DPL-020, BRU-DPL-07).** The policy formula is still z × σ(demand) × √L. The lead-time model now measures σ(lead time), but the formula does not use it yet.
- **Intermittency and lifecycle classes (FR-DPL-008/009)** and **method selection by class (BRU-DPL-04)**. The forecast is a moving average or a manual override; M26 is not built.
- **Planning exception worklist (FR-DPL-032, P0)** and **planned-order consolidation (FR-DPL-026)**.
- **Investment-change report to Finance (BRU-DPL-20)** and **guard rails on automatic application (T-13)**.
- **Inventory Manager vs Demand Plan Approver.** BRU-DPL-12/14 name the Inventory Manager. M43 uses its own Demand Plan Approver role, which has **0 holders on fix_real**, so until the owner appoints one, nothing in M43 that needs approval can be approved there (spec Q-06).
- fix_real has **no van locations**, so the van par page has nothing to size until M15 vans are set up.
