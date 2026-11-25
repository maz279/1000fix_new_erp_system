# M26 AI/ML Services: data-capture button audit

**Date:** 14 Nov 2026 · **Estate:** fix_real on port 8069 · **Status:** **LIVE on 8069 since the user-approved 02:58 restart (14 Nov).** `-u cd_ml_services` ran on fix_real first (clean, 155 modules). Production bundle `56919ad`. Nothing is committed.

## 1. The question

The M26 workspace has 7 sub-module pages (Function Register, 58 functions). Not every page showed a capture button that fit what the page covers. Which records should each page capture, and what did it actually offer?

## 2. What the spec says

Sources:

- `1000fix_ERP_Module/03_Modules/J_Data_Analytics_and_Intelligence/M26_AIML_Services_and_Model_Operations.md` (FR-AIM-001…042, BRU-AIM-01…27, lifecycle §8, entities §10, roles §13)
- `contracts/nav/registry.json` (7 sub-modules, forms Model Version / Evaluation Gate / Guard-Rail Config)

| # | Sub-module | Spec | What a person records there |
|---|---|---|---|
| 1 | Portfolio & Governance | FR-AIM-001, BRU-AIM-11, §10.1 `fix.ai.risk` | a model with its purpose, **named consumer, accuracy target, defined fallback**, risk class, owner, review date; AI risks; guard rails |
| 2 | Training Pipelines | FR-AIM-002…004 | a model version: artefact, dataset, measured metrics |
| 3 | Evaluation Gates | FR-AIM-005/006/013, BRU-AIM-13 | a gate result by a reviewer who did not register the version |
| 4 | Deployment & Monitoring | FR-AIM-007…009/013, BRU-AIM-06, T-06 | **drift observations** (PSI / KS per feature); **fallback tests** ("record the result") |
| 5 | Explainability | FR-AIM-039…041, BRU-AIM-05/08 | the **model card**; the **human decision / override with its reason** |
| 6 | GenAI & RAG | FR-AIM-033…038, BRU-AIM-10/21…24 | generative sessions and corpus — only once an engine exists; before that, the **risks** that gate a roll-out |
| 7 | Bengali NLP & OCR | FR-AIM-021/030/032 | Bengali / English complaint text classified by the fault classifier |

## 3. What the code had (before)

The engine's own `fregCreate` / `fregPanels` were run over the real registry, and the form saves were driven through `/p03/model/write` as non-admin M26 role holders against **HEAD code** (clean HEAD worktree, upgraded clone).

| # | Page | Capture before | Defect |
|---|---|---|---|
| 1 | Portfolio & Governance | + New ML Model Catalogue Entry | The form had **none of the spec's declarations** (consumer, target, fallback, risk class, owner, review date): the model held no such fields. No AI risk register existed. |
| 2 | Training Pipelines | + New Model Version | **Could not save.** The form showed State as an editable choice with its default and posted `state='draft'`; the lifecycle guard refuses any typed state. Live HEAD probe: *"A model version is created as a DRAFT … state, approver and deploy date are not typeable."* |
| 3 | Evaluation Gates | + New Evaluation Gate | Worked; but no list of gates existed anywhere in the navigation. |
| 4 | Deployment & Monitoring | **none** (`create: false`) | Fallback tests (BRU-AIM-06, a hard rule) and drift observations had **no record at all**; drift was one number typed on the version. |
| 5 | Explainability | + New Model Version | Irrelevant (a new version, not the card) and broken (see 2). Editing a version — to write its card — echoed `state` and was refused: *"A model version changes state only through its lifecycle actions…"*. The override capture on a computed run was refused too: *"…the engine's half is not editable (M26): input_text, model_id."* — the form posts every field it shows. |
| 6 | GenAI & RAG | + New ML Model Catalogue Entry | A deterministic engine entry: **no generative kind exists** to choose, and no LLM endpoint is provisioned. |
| 7 | Bengali NLP & OCR | + New ML Inference Run (module button) | Any model could be picked; the page listed every run, not classifier runs. |

Also: the Model Registry list had **no Mark Evaluated / Request Promotion / Retire buttons** (the actions were served but on no screen), and the Deployment Patterns list offered "+ New" (a new draft version) although a deployment happens only by promotion.

## 4. What was changed

| # | Page | Capture now |
|---|---|---|
| 1 | Portfolio & Governance | **+ New ML Model** with a *Portfolio Declaration* tab (purpose, named consumer, accuracy target, defined fallback, risk class, model owner, next review); chips **AI Risk**, **Guard-Rail Config**; AI Risk Register list on the page |
| 2 | Training Pipelines | **+ New Model Version** — now saves; State, drift score, approver and deploy date are read-only |
| 3 | Evaluation Gates | **+ New Evaluation Gate** (version picker limited to draft/evaluated); new **Evaluation Gate Log** list |
| 4 | Deployment & Monitoring | **+ Record Drift Observation** (deployed versions only); chip **Record Fallback Test**; **Drift Observations** and **Fallback Tests** lists; the Inference Fallback report shows each model's defined fallback, last test and outcome |
| 5 | Explainability | **+ Write Model Card** (pick a version, write its card); chip **Record Human Decision** (pick a computed run, record the final decision and reason) |
| 6 | GenAI & RAG | **+ Record AI Risk** pre-set to *Generative* (egress, prompt injection, ungrounded answers, labelling) — the page lists generative risks beside the honest capability status |
| 7 | Bengali NLP & OCR | **+ Classify Fault Text**: classifier-only model picker, complaint text required; the page lists fault-classifier runs |

Nav: Model Registry gains **Mark Evaluated / Request Promotion / Retire**; Deployment Patterns is create-less with **Retire**.

### Model changes (`cd_ml_services`, 19.0.0.3.0)

- `fix.ml.model`: `purpose`, `consumer_modules`, `accuracy_target`, `fallback_definition`, `risk_class`, `owner_id`, `review_date`. On every update `_seed_portfolio_declarations` fills **empty** fields from the spec table (§5.3–5.5) for the estate's kinds — consumer, target, fallback, risk class. It never overwrites a typed value; owner and review date stay empty (owner decision). Lead scoring and BI aggregator have no spec target, so none is invented.
- `fix.ml.fallback.test` **new**: model, consuming module, method (disabled / simulated), what the consumer did, outcome, incidents; tester stamped; append-only. Create: Model Owner, Data Scientist.
- `fix.ml.drift.observation` **new**: deployed version, feature, PSI, KS (0–1), threshold (default 0.2); `breached` derived; recorder stamped; append-only; refused on a version that is not deployed. The version's drift score = highest PSI of its newest monitoring day. Create: Data Scientist.
- `fix.ml.ai.risk` **new**: the AI risk register (risk, model or estate-wide, category, description, likelihood, impact, treatment, control reference, owner, review date, status), tracked. Create/edit: Model Owner, Data Scientist; everyone else reads.
- `fix.ml.inference.run.write`: an **unchanged echo** of the model / input is no longer an edit, so the human decision saves; a changed model or input is still refused (decision log).
- Workspace surfaces (`controllers/a11/m26.py`) now declare their write whitelist, which is what drops the echoed engine fields on save.

### Files

- `addons/domain/j_data_analytics/cd_ml_services/`: `models/fix_ml_assurance.py` **new**, `models/fix_ml_services.py`, `models/fix_ml_governance.py`, `models/__init__.py`, `data/ml_model_portfolio.xml` **new**, `__manifest__.py`, `security/ir.model.access.csv`, `security/fix_isolation_rules.xml` (regenerated by the generator)
- `addons/platform/cd_p03_portal/static/src/a11/m26.js`, `controllers/a11/m26.py`
- Tests: `cd_p03_portal/tests/test_m26_capture_buttons.py` (25 tests, **19 fail on HEAD**) and `test_m26_capture_live.py` (15 tests, endpoint as non-admin role holders)

## 5. Verification

- **HEAD proof** (clean HEAD worktree, non-admin users, through `/p03/model/write`): new version refused, model-card edit refused, human decision refused — the three messages quoted in §3.
- **Private clone `fix_test_m26`, worktree `1000 fix/m26wt`:** `-u all` clean (166 modules); the three tables exist and the seven catalogue entries carry the spec's declarations.
  - M26 live guard + existing A11 M26 audit suite + cd_ml_services governance tests: **82 collected, 0 failed, 1 skipped**.
  - Workspace estate suites (estate pages, sub-module create rules, screens wiring, report export standard, document buttons, A11 cross-area, KPI tiles, M26 guard): **862 collected, 860 passed, 2 skipped, 0 failed**.
  - ruff 0.8.4 check and format: clean.
- **fix_real (live):**
  - `-u cd_ml_services` clean (155 modules); module at 19.0.0.3.0; the 3 tables exist; the 5 spec kinds carry consumer, target and fallback, lead scoring and BI aggregator a consumer only.
  - Pre-restart check: no file other than this change was newer than the running server (started 01:13), so the restart published only M26.
  - 8069 was relaunched with its identical command (it had been started by hand from another session's shell; no supervisor). New pid up in 78 s, 0 errors in the log.
  - Both M26 guards run on fix_real inside a rolled-back transaction, as non-admin role holders: **40 passed**. Afterwards fix_real holds 0 risks, 0 drift observations, 0 fallback tests and 0 probe users.
  - Production bundle `56919ad` (signed-in session, no debug) contains all six new forms.
  - Click-through of all 7 pages in the signed-in workspace: each shows the button in §4; each button's form opens without an error. Write Model Card lists the 6 real versions; + New AI Risk on GenAI & RAG opens with Category = Generative AI.

## 6. Open items (owner / build)

- **fix_real has 0 gates, 0 guard rails, 0 runs** and 6 seeded versions (all deployed, bias untested). Each M26 role (Data Scientist, Evaluation Reviewer, Model Owner) has **one holder** — so the four-eyes promotion cannot be exercised by real people yet (owner decision: name holders).
- **BRU-AIM-11 not yet enforced at promotion** ("no consumer, target and fallback → not deployed"). The fields now exist and are seeded from the spec, but lead scoring and the BI aggregator have no stated target; enforcing now would block their next version. Owner to state those targets, then the rule can be switched on.
- **Bias status is still typed on the version** by the registrant; a passed bias *gate* does not set it. Spec §13 makes model owner and bias reviewer incompatible — a follow-up should derive the status from the bias gate.
- **An override without a reason is not refused** (BRU-AIM-05). The form asks for one; the model does not enforce it (an existing audit test writes a bare override).
- Spec entities with **no model** (build gaps, not capture defects): training run / experiment tracking (FR-AIM-002/003), data-sufficiency gate (FR-AIM-006), model performance history and auto-demotion (FR-AIM-008), guard-rail intervention log, generative session and retrieval corpus (no LLM endpoint exists), OCR engine.
