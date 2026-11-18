# M07 CRM & Sales Pipeline: data-capture button audit, second pass

**Date:** 18 Nov 2026 · **Branch:** `fix/m07-capture-pass2` (worktree `m07cap2-wt`, from `6deb4dca`) · **Status:** built, tested, landed (`bbb27f2c`), pushed, and **live on fix_real (8069) and fix_dev (8090)** since 19 Nov 03:17 (see §7)

## 1. The question

The M07 workspace has 10 sub-module pages. The user saw pages that still have no relevant button to record data.

The first pass (13 Nov, `M07_CAPTURE_BUTTON_AUDIT_2026-11-13.md`) gave every page a "+ New" and fixed three buttons that saved the wrong record. A count of 10/10 buttons is not the same as "relevant". This pass reads each page against the spec's requirements, rules and owned entities, and asks whether what a person decides on that page can be recorded.

## 2. What the spec says

Source: `1000fix_ERP_Module/03_Modules/B_Customer_Engagement_and_Experience/M07_CRM_Sales_Pipeline_and_Account_Management.md` (§5 features, §8 lifecycles, §9 rules, §10.1 owned entities).

| Page | What a person records | Spec | Priority / class |
|---|---|---|---|
| 1 Lead Capture & Qualification | The qualification assessment (need, authority, budget, timing) and its outcome: qualified, disqualified with a reason, or returned to nurture | FR-CRM-002, FR-CRM-007/008, lifecycle §8.1 (captured → qualifying → qualified → converted / disqualified / recycled) | **P1** |
| 2 Opportunity Stages | The pursuit team: contributors and their roles | FR-CRM-013, entity `fix.opportunity.team` | P2 |
| 3 Pipeline & Forecasting | The quota the forecast is read against | FR-CRM-023, entity `fix.quota`; §7.1 "forecast against quota" | P2 |
| 5 Account-Manager Assignment | The published dedicated-manager criteria, and a dedicated assignment outside them only as an approved exception | FR-CRM-027, BRU-CRM-09, open question Q-01 | **P1** / rule class A |
| 6 QBR Programme | Agreed actions tracked to completion; an accepted recommendation raised as an opportunity | FR-CRM-037, FR-CRM-038 | P1 / P2 |
| 8 Renewal Pipeline | A renewal pursuit, with its source and its play | FR-CRM-039, FR-CRM-042 | **P1** |

## 3. What the code had (HEAD `6deb4dca`)

M07 holds no data on fix_real (0 leads, 0 accounts, 0 renewals, 0 QBRs, 1 pipeline), so the capture surfaces are the only way in.

| # | Page | Before | Defect |
|---|---|---|---|
| 1 | Lead Capture | + New Lead; list actions Score / Convert | **No qualification anywhere.** A lead converted straight from capture; there was no lead state, no BANT assessment, no disqualify and no nurture hand-back. The Lead form's tab "4. Kernel Match & Conversion" held **no field at all**. |
| 2 | Opportunity Stages | + New Opportunity | No opportunity team: the entity was never built. |
| 3 | Pipeline & Forecasting | + Take a Forecast Snapshot | No quota: the entity was never built, so attainment could not be measured. |
| 5 | Account-Manager Assignment | + New Account Assignment | **Anyone could pick "Dedicated Manager"** for any account. No criteria existed to publish, and BRU-CRM-09's exception approval was not enforced. |
| 6 | QBR Programme | + New QBR | Agreed actions existed only as lines inside each QBR. No list tracked them across reviews, and nothing turned an accepted recommendation into an opportunity. |
| 8 | Renewal Pipeline | + New Contract Renewal Pursuit | **The button could never save.** `fix.renewal.source_type` is required with no default and was not on the form, so every save was refused. The renewal play (FR-CRM-042) was not on the form either, and `lead_time_days` was shown editable although the model sets it. |

Pages 4, 7, 9 and 10 were correct and are unchanged.

## 4. What was built

`cd_crm_ext` 19.0.1.4.0, new file `models/fix_crm_capture.py` (imported last: it extends `crm.lead`, `fix.account.assignment` and `fix.qbr.action`).

| Record | Page | Rules enforced by the model |
|---|---|---|
| `fix.lead.qualification` | 1 | Only on an open lead (not an opportunity, not closed). **Qualified** needs a confirmed need and no "not established" authority, budget or timing. **Disqualified** needs a reason, and "other" needs notes; the lead is archived. **Not ready** returns it to nurture (FR-CRM-008); the lead is archived as *Returned to Nurture*. The assessor and time are stamped. The record cannot be edited or deleted. |
| `crm.lead.qualification_state` | 1 | Captured / Qualified / Disqualified / Returned to Nurture. A **guarded field**: set only by an assessment, never typed (create or write). **Convert to Opportunity is refused unless the lead is qualified** (FR-CRM-007), on top of the existing party-match gate (BRU-CRM-02). |
| `fix.opportunity.team` | 2 | Opportunities only; a person once per opportunity. The owner is not listed as a member. At most one executive sponsor. **Only the opportunity owner or a sales manager** changes the team. A won or lost deal's team is frozen. Also a grid on the Opportunity form (new tab "6a. Opportunity Team"). |
| `fix.sales.quota` | 3 | **Set by a sales manager only, and never for themselves.** Period is `YYYY`, `YYYY-Qn` or `YYYY-MM`; the target is above zero. One quota per seller, period and pipeline. Attainment is computed from won deals closed in the period, in Dhaka-local bounds. |
| `fix.account.eligibility` | 5 | The dedicated-manager criteria, **published by a sales manager (the CCO)**: annual spend (posted customer invoices less credit notes, last 12 months), annual contract value, and/or Strategic tier. At least one criterion. New criteria supersede the old (archived, never deleted). |
| `fix.account.assignment` (extended) | 5 | A **Dedicated Manager** assignment is measured against the criteria in force, and the basis is stamped. **Outside the criteria it needs an exception reason, and only a sales manager may record it** (BRU-CRM-09); the approver is stamped. The stamps cannot be typed. |
| `fix.qbr.action.action_raise_opportunity` | 6 | Only from a **held** review, once per action, never from a cancelled action. Creates a cross-sell opportunity on the account, with source *QBR Recommendation*, owned by the action's internal owner, and links it back. |

Workspace (`cd_p03_portal`):

- `static/src/a03/m07.js`:
  - New lists and forms: Qualification Assessments + *Qualify a Lead* (page 1), Opportunity Teams + *Add to an Opportunity Team* (page 2), Sales Quotas + *Set a Sales Quota* (page 3), Dedicated-Manager Criteria + *Publish Dedicated-Manager Criteria* (page 5), QBR Agreed Actions with *Mark Done / Cancel Action / Raise Opportunity* (page 6).
  - The Opportunity form gets the team grid.
  - The Lead form's qualification tab shows the qualification and the score.
  - The Assignment form gets the exception reason, basis and approver.
  - The Renewal form gets **source type** and **play**.
  - The module forms list grows from 14 to 18 entries.
- `controllers/a03/m07.py`: SURFACES gain 4 models, with **server-side picker domains**. Pickers read sudo, so the lead picker offers only open leads, the team picker opportunities and staff, and the quota picker staff. `fix.qbr.action` gains `action_raise_opportunity`. `writable.py` is regenerated.
- Isolation rules are regenerated for cd_crm_ext only; drift in 7 other modules was reverted.
- **No new domain events**: outcomes are posted to the record's chatter, so the event registry is unchanged.

## 5. Verification

All runs used `fix_test_m07`, a private copy of fix_test with 39 lagging modules upgraded first so it matches HEAD.

| Check | Result |
|---|---|
| New guard `cd_p03_portal/tests/test_m07_capture_pass2.py` | **26/26 pass.** It runs the real `fregCreate`/`fregPanels` in node over the registry, then saves through `/p03/model/write` and `/p03/model/action` **as salespeople and a sales manager**, not the superuser. It includes a registry check that no M07 form leaves out a field its model requires (it caught the renewal form). |
| Mutation check: each of 24 rules removed in turn | **21/24 red.** The 3 survivors are equivalent: assessment immutability, quota "manager only" and criteria "manager only" are also refused by the access rights (salespeople hold read-only or no-write ACLs on those models), so removing the model check changes nothing a user can do. Files restored byte for byte (hash checked). |
| First-pass guard `test_m07_submodule_capture.py` + all `cd_crm_ext` tests | **78/78 pass.** One first-pass test now qualifies its lead before converting: the contract changed on purpose. |
| Regression: all `cd_p03_portal` + `cd_crm_ext` tests + the isolation-rule generator | **5,749 run: 5,424 passed, 315 skipped, 10 failed.** The **10 failures fail identically on an untouched HEAD tree** (rerun separately): M50 cheque chip and statement-line pick, 5 A10 guarded-field messages, the roster-gate message, M60 hold row form, M19/M30 page buttons. None involves M07. |
| In the browser, private server on 8137 (worktree code, a copy of `fix_test_m07`), headless Chromium | All 10 sub-module pages show their **+ New** and list their capture chips (the new chips: *Lead Qualification*, *Opportunity Team*, *Sales Quota*, *Dedicated-Manager Eligibility Criteria*). Every page's form opens with no error and no page error. A **Lead Qualification was saved through the form** as a sales manager: the lead picker offered only the one open lead, the save showed "Saved ✓" and the *Qualified* badge, and Postgres holds the assessment (assessed by the walk user) and the lead in state *qualified*. |

## 6. Not done / needs a decision

1. **The dedicated-manager criteria are the CCO's decision (Q-01).** No criteria are published on fix_real, so every dedicated assignment is an exception a sales manager must approve until the CCO publishes them. Asset-estate size (one of the spec's candidate measures) is not a criterion: no reliable asset count per party exists yet.
2. **AUT-CRM-06** (auto-assign a dedicated manager when an account crosses the threshold) is not built. The criteria are evaluated when an assignment is saved.
3. **Territories (FR-CRM-022, P2)** are not built. A territory needs evaluation rules on account changes (T-09), which is a feature, not a capture on an existing page.
4. **BRU-CRM-14** (management review above a value threshold before proposal) is still not enforced. The threshold is an owner decision.
5. **Lead de-duplication at capture (T-07, FR-CRM-009)** is not built. "Duplicate of an existing pursuit" is available as a disqualification reason.
6. Spec events `lead.qualified` and `lead.recycled` are not published: they are not in the event registry, and adding them is a contract change for M35/M25.

## 7. State

| Step | Status |
|---|---|
| Commit | `eca20c79` on `fix/m07-capture-pass2`, replayed onto the shared tip as **`bbb27f2c`** (after M10's `6d1dbd77`). The merged tree was re-checked: generated `writable.py` unchanged on regeneration; A03/M07/M10 page guards: 443 run, 257 passed, 184 skipped, 2 failed. Both failures are pre-existing (M60 hold row, M19/M30 page buttons); the row-form failure now also names M10's wallet row, from M10's landing, not M07. |
| Land | CAS `update-ref` on `fix/a03-live-data-and-pending-work` + `read-tree -m -u` in the shared checkout (clean before and after). |
| Push | `origin/fix/a03-live-data-and-pending-work` contains `bbb27f2c`; `origin/fix/m07-capture-pass2` pushed. |
| Backup | `all_working_folder/1000fix-2/_migration/backups/fix_real_pre_m07_capture2_2026-11-19.dump` (51.8 MB). |
| Deploy (user approved: both DBs) | Run by the M06 session in one coordinated wave: `-u cd_data_case,cd_crm_ext,cd_quotation,cd_rate_card,cd_p03_portal` on fix_real and fix_dev, version-gap check empty, one restart of both at 19 Nov 03:17 (8069 PID 65964, 8090 PID 77252). M07 ran no -u of its own, to avoid two upgrades on one database. |
| Live check (read-only, both DBs) | `cd_crm_ext` 19.0.1.4.0; the 4 new models, 6 ACL rows, 4 isolation rules and 5 new columns present; both servers started after the landing; live bundle `02e9383` carries the new forms (qualification, team, quota, criteria, QBR actions, renewal source type). |
| Data | fix_real has no M07 records yet (0 leads, 0 accounts), and **no dedicated-manager criteria are published**: until the CCO publishes them, every dedicated assignment is a sales-manager-approved exception. |
| Cleanup | Private clones `fix_test_m07`, `_m07r`, `_m07w` dropped; private server and launch entry removed; run worktree removed. |
