# M25 Business Intelligence: data-capture button audit

**Date:** 13–14 Nov 2026 · **Estate:** fix_real on port 8069
**Status:** live on 8069 since the 14 Nov 01:13 restart. `-u cd_bi_reporting` ran on fix_real first, and the user approved the deploy.

- The served bundle `f61c973` carries the new screens and the engine change.
- 8089 was down and no supervisor was running. A peer session relaunched 8069 while my relaunch was still booting. Its log is clean (155 modules, no errors).

## 1. The question

The M25 workspace has 7 sub-module pages (Function Register, 58 functions). Not all of them showed a button that captures the right record. Which pages should have one, and what should it open?

## 2. What the spec says

Sources:

- `1000fix_ERP_Module/03_Modules/J_Data_Analytics_and_Intelligence/M25_Business_Intelligence_and_Reporting.md` (FR-BID-001…034, lifecycles §8.1/§8.2, rules §9, entities §10, SoD §13)
- `contracts/nav/registry.json` (M25: 4 groups, 13 screens, 6 reports, forms Dashboard / Distribution Schedule / Alert Subscription)

| # | Sub-module | Spec | What a person records |
|---|---|---|---|
| 1 | Role Dashboards | FR-001…010 | a dashboard bound to a role, with a named owner and steward |
| 2 | Standard Report Library | FR-011…017 | nothing is typed into a pack, because packs are computed. A person **subscribes** to one (FR-023). |
| 3 | Self-Service | FR-018…022 | a saved (draft) dashboard, certified before it reaches an audience (BRU-BID-06) |
| 4 | Distribution & Alerting | FR-023…028 | a distribution schedule, and a threshold alert |
| 5 | Embedded Analytics | FR-029…032 | the analytics dataset connection the external BI workspace embeds from |
| 6 | Mobile | FR-005, 028 | a dashboard (mobile renders the role cockpits), or a low-bandwidth schedule |
| 7 | Lifecycle & Usage | FR-022, 033, **034** | the dashboard lifecycle acts, and an entry on the **spreadsheet-retirement register** (KPI-094 → zero) |

## 3. What the code had (before)

`fregCreate` / `fregPanels` were evaluated over the real registry, and the backend was read.

| # | Page | Capture before | Defect |
|---|---|---|---|
| 1 | Role Dashboards | + New Dashboard | Right record, but **the form had no Data Steward**, so *Submit for Review* was always refused ("Name the data steward") |
| 2 | Standard Report Library | + New Dashboard | **Wrong record.** The page listed saved dashboards, not the library. |
| 3 | Self-Service | + New Dashboard | Same steward defect. A draft could be marked "shared with every internal user" (BRU-BID-06). |
| 4 | Distribution & Alerting | + New Distribution Schedule | The report and the metric were free-typed keys (`M25:branch_league`, `overdue_gt_60d`). *Send Now* was served but on no screen. **A PDF or XLSX schedule always attached a CSV.** |
| 5 | Embedded Analytics | **none** | The sync-connection list refused + New and had no form. *Test* and *Run Snapshot* were served but on no screen. |
| 6 | Mobile | + New Dashboard | no chips |
| 7 | Lifecycle & Usage | + New Dashboard | **Wrong record.** The register (FR-BID-034) had **no model**, so the *Spreadsheets Retired* KPI tile had no source. The dashboard lifecycle actions (review, certification through M63, retirement) were served but declared on no screen. |

There is one more finding. The change request `docs/r10/CR-module-register-M25.md` claims FR-BID-034 is delivered by "`cd_metric_registry` manual report inventory". **No such model exists.**

## 4. What was changed

| # | Page | Capture now |
|---|---|---|
| 1 | Role Dashboards | + New Dashboard. The form has a **Data Steward**, and its status bar shows the lifecycle state. |
| 2 | Standard Report Library | **+ New Distribution Schedule**. The page reads the new **Standard Report Library** pack: each canonical pack with its audience, who may open it, active schedules, exports in the last 30 days and the last export. |
| 3 | Self-Service | + New Dashboard. A draft can no longer be shared (the server refuses it), and retiring a dashboard unshares it. |
| 4 | Distribution & Alerting | + New Distribution Schedule, plus an Alert chip. Report and metric are **dropdowns**. **Send Now** is on the list, and *Last Run Note* says why a send failed. A schedule now sends **the format it names**. |
| 5 | Embedded Analytics | **+ New Sync Connection** (new form; BI Sync Operators only). **Test Configuration** and **Run Snapshot Now** are on the list. |
| 6 | Mobile | + New Dashboard, plus chips Dashboard and Distribution Schedule |
| 7 | Lifecycle & Usage | **+ Register a Manual Pack** (new model `fix.bi.manual.pack`). The **Spreadsheet Retirement** list carries Start Parallel Run → Reconciled: Figures Match / Record Discrepancy → Retire Pack. The Dashboard Builder carries **Submit for Review**, **Request Certification** (asks why) and **Retire Dashboard**. The *Spreadsheets Retired* tile counts retired packs. |

### The retirement register (`fix.bi.manual.pack`)

The model follows spec §8.2: registered → parallel run → (discrepancy investigated) → accepted → retired.

- **BRU-BID-16:** a pack is never retired without a reconciled parallel run with matching figures.
- **Replacement:** the parallel run needs a named replacement, either a **certified** dashboard or a standard report of the library.
- **Who reconciles:** a BI Data Steward who is **not the pack's owner** (§13 SoD). A discrepancy needs a note, holds the retirement, and is investigated against the M62 metric (AUT-BID-13).
- **Who retires:** a steward who is not the owner. Retirement stamps the source data closed (BRU-BID-17).
- **Lifecycle fields:** they move only through the actions, and they cannot be typed on create or write.
- **Locking:** a retired pack is locked, and only a still-registered pack can be deleted.
- **Access:** BI Authors register; Data Stewards act; everyone internal reads. A company record rule is generated.

### Files

- `addons/domain/j_data_analytics/cd_bi_reporting/`:
  - `models/fix_bi_manual_pack.py` (new)
  - `models/fix_bi_selfservice.py`: share constraint; the schedule renders through `report_delivery.build` in its own format
  - ACL rows and the generated isolation rule
  - manifest 19.0.0.3.0
- `addons/platform/cd_p03_portal/controllers/a11/m25.py`: surface for the register, the `report_library` pack, the KPI source
- `addons/platform/cd_p03_portal/static/src/a11/m25.js`: page maps, forms, actions, choices
- `addons/platform/cd_p03_portal/static/src/p03_workspace.js`: `fregCreate` honours a named `create:` form on a report-fed page too. No other module combines the two, so nothing else changes.
- Tests:
  - `test_m25_capture_buttons.py`: 24 tests, **16 fail on HEAD**
  - `test_m25_capture_live.py`: 7 tests through `/p03/model/write`, `/p03/model/action`, `/p03/model/report` and `/p03/bi/kpis` as non-admin users
  - `cd_bi_reporting/tests/test_m25_manual_pack.py`: 15 tests
  - `test_kpi_tiles_served.py`: M25 no longer lists `spreadsheets_retired` as sourceless

## 5. Verification

- **Private clone `fix_test_m25`** (fix_test, upgraded to HEAD's schema):
  - cd_bi_reporting tests 40/40 (25 existing, 15 new)
  - M25 guard 24/24, live endpoint tests 7/7
  - estate page standard, A11 control suite, KPI tiles, declared-gap reports, report export standard and report subscriptions: about 735 passed
  - One failure is not mine: `test_m01_submodule_pages::test_an_existing_only_form_leads_to_the_list_its_record_is_picked_from` flags `M18-form-cert` (M18 fragment at HEAD).
- **Lint:** ruff 0.8.4 and pylint-odoo are clean on every changed Python file. `node --check` passes on both JS files.
- **fix_real after the deploy** (read-only probe, rolled back):
  - the table exists with 0 rows, along with its 4 ACL rows and its company rule
  - the surface serves the 4 actions
  - `report_library` answers as a real non-admin user with the six packs (exports show "—", because that user may not read the export audit)
- **Served bundle `f61c973`:** contains *Register a Manual Pack*, `M25-form-sync`, `report_library`, *Reconciled: Figures Match*, the metric choices, and `fregCreate` with the named-form check ahead of the report guard.
- **Not done:** a click-through in the browser pane. The pane is not signed in to 8069, and I did not type the admin password. The engine evaluation in §4 runs the same `fregCreate`/`fregPanels` code the browser runs.

## 6. Not built: needs an owner decision or a model

| Gap | Spec | Why it is not a button |
|---|---|---|
| **Nobody can certify, reconcile or retire on fix_real** | §13 | Every BI role (Author, Data Steward, Sync Operator, Company-Wide, Finance) is held by **admin only**. The certifier must not be the author, so with one holder no dashboard can be certified. This needs an owner appointment. |
| Dashboard usage telemetry | FR-BID-033 | `last_viewed_at` is never written, because nothing renders a *saved* dashboard (the role cockpits render by role). The column was removed from the screens rather than shown permanently empty. |
| Alert instances, acknowledgement, escalation | FR-025/026, `fix.alert.instance` | No model. An alert stamps its last value and fire time only, and notification transport is porting phase. |
| Annotation and commentary | FR-009, `fix.annotation` | No model |
| Embedded surface placement and signed tokens | FR-029, T-08, `fix.embedded.surface` | No model. The Embedded page captures the dataset connection. |
| Report definitions with owner and certification, report runs, restatement flags | FR-011/017, `fix.report.definition` / `fix.report.run` | Packs are code. The library pack lists them with their entitlement. |
| Burst-by-scope delivery | FR-024 | One schedule sends one rendering to named internal users |

### Facts on fix_real (14 Nov)

- 0 dashboards, schedules, alerts, sync connections and manual packs
- 14 export-log rows
- all five BI groups: admin only
