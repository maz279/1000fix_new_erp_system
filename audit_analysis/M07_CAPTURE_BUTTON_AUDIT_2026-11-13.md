# M07 CRM & Sales Pipeline: data-capture button audit

**Date:** 13 Nov 2026 · **Estate:** fix_real on port 8069 · **Status:** tested (78 tests green on clone `fix_m07chk`); front end live; `cd_crm_ext` upgraded on fix_real; server restart held for other sessions' undeployed columns; nothing committed

## 1. The question

The M07 workspace has 10 sub-module pages. Not all of them showed a button to record data. Which pages should have one, what should it open, and does it save the right record?

## 2. What the spec says

Sources:

- `1000fix_ERP_Module/03_Modules/B_Customer_Engagement_and_Experience/M07_CRM_Sales_Pipeline_and_Account_Management.md` (FR-CRM-001…046, rules BRU-CRM-01…14, owned entities §10.1)

| # | Sub-module | Requirements | What a person records |
|---|---|---|---|
| 1 | Lead Capture & Qualification | FR-CRM-001…009 | a lead; its party match and conversion to an opportunity (BRU-CRM-02) |
| 2 | Opportunity Stages | FR-CRM-010…012 | an opportunity |
| 3 | Pipeline & Forecasting | FR-CRM-019…021, BRU-CRM-06/07 | a forecast snapshot, *taken* from the pipeline, never typed |
| 4 | Account Plans & Stakeholders | FR-CRM-028/029 | an account plan; the stakeholder map (`fix.stakeholder.map`) |
| 5 | Account-Manager Assignment | FR-CRM-026/027 | an assignment |
| 6 | QBR Programme | FR-CRM-033…038 | a QBR and its agreed actions |
| 7 | Activities | **FR-CRM-045 (P1)** | each call, meeting, site visit, e-mail and task (`fix.sales.activity`), with reminders |
| 8 | Renewal Pipeline | FR-CRM-039…043 | a renewal pursuit |
| 9 | Cross-Sell / Upsell | FR-CRM-044 | an expansion opportunity |
| 10 | Competitor Intelligence | FR-CRM-015 | competitor, their price and our price position on the opportunity |

## 3. What the code had (before)

M07 holds no data on fix_real: 0 leads, 0 accounts, 0 snapshots, 1 pipeline. So the capture buttons are the only way any CRM data gets in.

| # | Page | Before | Defect |
|---|---|---|---|
| 1 | Lead Capture | + New Lead | **Saved an opportunity.** The form's `type: 'lead'` was read-only, so it was never sent, and Odoo's default is *opportunity* for anyone without `crm.group_use_lead`. No user on fix_real has that right. A new lead never appeared on the Leads list. The list also had no action at all: a lead could not be converted (FR-CRM-007). |
| 3 | Pipeline & Forecasting | + New Forecast Snapshot | **Froze a snapshot of zeros.** The figures are read-only on the form, so none were sent. The snapshot locked on save (BRU-CRM-06), and its unique period/owner/pipeline key then made the scheduler skip the real snapshot. |
| 4 | Account Plans & Stakeholders | + New Account Plan | No stakeholder capture. `fix.account` (the key-account master: tier, health, contract value, QBR cadence) and `fix.account.stakeholder` were built on 31 Oct and served by **no screen**. |
| 7 | Activities | **nothing** (`create: false`) | The *Activity (call/visit/meeting)* form was a **crm.lead** form. It edited the lead's computed next-activity fields: the due date is read-only, so every save that set one was refused, and a summary on a lead with no pending activity went nowhere. Opened from its chip it created a new lead named after the "activity". No call or visit was ever recorded. |
| 9 | Cross-Sell / Upsell | **nothing** | The page listed **every** opportunity, not cross-sell ones, and offered no way to raise one. |
| 10 | Competitor Intelligence | **nothing**, `forms: []` | Listed `won_status in (won, lost)`, but lost deals are archived, so only won ones ever showed. `price_position` (FR-CRM-015) existed on the model and on no form. |
| 2, 5, 6, 8 | | correct | |

## 4. What was changed

| # | Page | Capture now | How |
|---|---|---|---|
| 1 | Lead Capture | **+ New Lead** (saves a lead) · list actions **Score Lead**, **Convert to Opportunity** | The form posts `type`, and the type is locked once saved (`_fix_form_locked_fields`). New `action_convert_to_opportunity` refuses a lead with no matched party (BRU-CRM-02) and keeps the source. |
| 2 | Opportunity Stages | + New Opportunity | The opportunity form posts its type too, so it stays right if "use leads" is ever switched on. |
| 3 | Pipeline & Forecasting | **+ Take a Forecast Snapshot** | `fix.forecast.snapshot.create` rolls the figures up from the owner's open opportunities: commit, best case and pipeline, the same roll-up the scheduler uses. Figures a caller sends are ignored. It refuses when there is nothing to forecast. |
| 4 | Account Plans & Stakeholders | + New Account Plan, chip **Key Account & Stakeholders** | New list *Key Accounts & Stakeholders* and form (profile, value and health, decision-maker grid). |
| 7 | Activities | **+ Log a Call, Visit or Meeting** | New model `fix.sales.activity` (the spec's entity): type, when, duration, location, lead/opportunity or account, outcome, notes, next step. A next step with a due date schedules a To-Do for the owner on the lead (or account). Moving the date replaces that To-Do rather than adding a second one. |
| 9 | Cross-Sell / Upsell | **+ New Commercial Opportunity & B2B KAM**, starts with *Cross-Sell* ticked | The page lists `is_cross_sell` opportunities. The page filter pre-fills the form. |
| 10 | Competitor Intelligence | **+ Record Competitor Intelligence** | Two steps: pick the opportunity, then record competitor, their bid and our price position. The opportunity form also shows price position now. The page lists opportunities with a competitor recorded. |

Files:

- `addons/domain/b_customer_engagement/cd_crm_ext/`: `models/fix_sales_activity.py` (new), `models/crm_lead_ext.py`, `models/fix_forecast.py`, `models/__init__.py`, `security/ir.model.access.csv`, `security/fix_isolation_rules.xml` (generated), `__manifest__.py` (19.0.1.3.0)
- `addons/platform/cd_p03_portal/`: `static/src/a03/m07.js`, `controllers/a03/m07.py` (serves `fix.sales.activity`, `fix.account`, `fix.account.stakeholder`, the conversion action), `controllers/a03/writable.py` (regenerated)
- Guard: `addons/platform/cd_p03_portal/tests/test_m07_submodule_capture.py`

## 5. Evidence

Clone `fix_m07chk` (from `fix_real_e2e3`), with `cd_crm_ext` and the lagging modules upgraded:

- `test_m07_submodule_capture.py` passes 30/30. It runs the real `fregCreate` in node over the registry, then saves through `/p03/model/write` and `/p03/model/action` **as a salesperson**, not the superuser:
  - a new lead lands on the Leads list;
  - a saved type cannot be changed by a write;
  - conversion is refused without a party, then keeps the source;
  - a cross-sell saves flagged;
  - an activity schedules its To-Do, and moving the date replaces it;
  - an activity with no subject is refused;
  - a forecast is refused with nothing to roll up, and figures a caller sends are ignored;
  - a key account saves with its stakeholders;
  - competitor intelligence is written on the picked opportunity.
- `cd_crm_ext/tests` passes 48/48.
- The A03 guards pass, plus the estate page standard, screen wiring and all-area sub-module mapping. Six estate-wide failures in the first run were peers' files caught mid-commit; all six pass on re-run.
- Lint is clean with the pinned ruff 0.8.4.

## 6. Deploy

| Step | Status |
|---|---|
| JavaScript (`m07.js`) | live: the server reads it from disk |
| backup | `all_working_folder/1000fix-2/_migration/backups/fix_real_pre_m07_capture_deploy_2026-11-13.dump` (47.7 MB) |
| `-u cd_crm_ext` on fix_real | **done** 13 Nov 02:26. Version 19.0.1.3.0, table `fix_sales_activity`, ACL, company rule all verified in Postgres. 8069 and 8089 still answer. |
| restart 8089, then 8069 | **held** (see below) |

Why the restart is held: a restart loads the whole working tree. A read-only check of fix_real against the current tree (`scratchpad/m07/schema_gap.py`) found stored fields with no column:

- `fix.purchase.advance.payment_failure`, `fix.purchase.advance.payment_move_id` (cd_requisition)
- `fix.vendor.invoice.advance_applied` (cd_ap_ext)

It also found tables that don't exist yet: `fix.bulk.buyback*`, `fix.device.bulk.*`, `fix.purchase.advance.application`. All of these are other sessions' uncommitted, undeployed work. After a restart, every query on vendor invoices and purchase advances would fail on 8069. M07's server side goes live with the next restart made after those modules are upgraded (or with them).

Until then, on 8069:

- *Activities* and *Key Accounts* answer "Model not served by the workspace screens".
- Saving price position is refused.
- Lead conversion is refused.

M07 holds no data, so nothing existing is affected.

Also found and repaired during the deploy (with the user's OK): at 02:00 something upgraded the shared `.venv`, including `cryptography` 42.0.8→50.0.2 and `lxml` 5.2.1→6.1.3. With those, Odoo cannot import (pyOpenSSL `lib.GEN_EMAIL`), so any restart would have failed to boot. Both were reinstalled at Odoo's pins (`vendor/odoo/requirements.txt`). The other upgraded packages (pydantic, mypy, pip, cyclonedx…) were left alone.

## 7. Not changed (noted)

- `M54-form-*` `version_type` uses the same read-only fixed value as the old Lead form, so it is probably never sent. It belongs to A08, so it was not touched here.
- Spec entities still not built: `fix.opportunity.team` (FR-CRM-013), `fix.territory` / `fix.quota` (FR-CRM-022/023), `fix.account.health` (FR-CRM-031). They are features, not capture buttons on existing pages.
