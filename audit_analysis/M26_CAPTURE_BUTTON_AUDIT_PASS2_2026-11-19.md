# M26 AI/ML Services: data-capture audit, second pass

**Date:** 19 Nov 2026 · **Branch:** `fix/m26-capture-pass2` (worktree `m26cap2-wt`, from `a6ca660a`) · **Spec:** `1000fix_ERP_Module/03_Modules/J_Data_Analytics_and_Intelligence/M26_AIML_Services_and_Model_Operations.md` · **First pass:** `M26_CAPTURE_BUTTON_AUDIT_2026-11-14.md`

## 1. The question

The user again saw M26 sub-module pages without a relevant data-capture button.

The first pass (14 Nov) gave each of the 7 pages a "+ New" and fixed a version form that could never save. Having a button is not the same as capturing what the page is for. This pass read each page against what a person decides or measures there, per the spec:

- §5: the 42 features;
- §8.1: the model lifecycle;
- §9: the rules;
- §10.1: the owned entities;
- §11: the automations.

For each, it asked whether that decision can be recorded on the page.

## 2. What the spec says each page records

The function register gives only page names and counts (58 functions over 7 pages), so pages are matched to the spec by theme, as in pass 1.

| Page | What a person records there | Spec | Priority / class |
|---|---|---|---|
| 2 Training Pipelines | A **training run**: code version, data snapshot, feature versions, hyperparameters, environment, metrics, outcome. Every version names the run that produced it. | FR-AIM-002/003, FR-AIM-004 (lineage), T-10, entity `fix.training.run`, BRU-AIM-03/17 | P2 / **H** |
| 3 Evaluation Gates | The **data-sufficiency gate**: the model's declared minimum history and volume, against what the data holds. Unmet is *deferred* with a revisit date. | FR-AIM-006, BRU-AIM-12, lifecycle §8.1, AUT-AIM-01/02, entity `fix.data.sufficiency.gate` | **P0 / H** |
| 3 Evaluation Gates | The **bias test**: segments, metric by segment, disparity, assessment, next due. Documented by someone external to the model's beneficiary. | FR-AIM-042, BRU-AIM-07, §13 SoD, entity `fix.bias.test` | **P0 / H** |
| 4 Deployment & Monitoring | **Production performance** per period: metric, target, floor, labelled sample. A floor breach demotes the version and restores the prior champion. | FR-AIM-008, BRU-AIM-19, T-05, AUT-AIM-07, entity `fix.model.performance` | **P0** / C |
| 5 Explainability, 7 Bengali NLP | The human override **with its reason**; on page 7, the confirmed fault. | BRU-AIM-05 (H), FR-AIM-021 ("the override trains the model") | **H** |
| 4 (Retire) | Retirement with the **consumers' confirmation** that the fallback is now the standing path. | FR-AIM-010, AUT-AIM-22 ("block retirement without consumer confirmation") | P2 |

Pages 1 (Portfolio & Governance) and 6 (GenAI & RAG) match the spec and keep their captures.

## 3. What the code had (HEAD `a6ca660a`)

The page contents below were evaluated the way the browser evaluates them: Node ran the engine's own `fregCreate` and `fregPanels` over the real registry fragments.

| # | Page | Captures at HEAD | Defect |
|---|---|---|---|
| 2 | Training Pipelines | Model Version | **No training run existed.** A version carried a free-text "training dataset" and nothing else. No run could be reproduced or compared. |
| 3 | Evaluation Gates | Evaluation Gate | **No data-sufficiency gate.** Promotion never asked whether the data sufficed (BRU-AIM-12, a hard rule). **No bias test record.** The version's bias status was a choice on the version form, typed by the person who registered it. |
| 4 | Deployment & Monitoring | Drift Observation, Fallback Test | **No production performance.** Nothing recorded a floor, so no version could ever be demoted (FR-AIM-008 P0). |
| 5 | Explainability | Model Card, Record Human Decision | **An override saved without a reason** (BRU-AIM-05). |
| 7 | Bengali NLP & OCR | Classify Fault Text, Run ML Model Inference | No way to record the confirmed fault for a classified complaint. |
| — | Model Registry / Deployment Patterns | Retire | **Retired with no consumer confirmation** (AUT-AIM-22). |

**Proof on unchanged HEAD code** (clean detached worktree at `a6ca660a`, run against the upgraded clone, as non-admin users):

- the four models do not exist (`fix.ml.training.run`, `fix.ml.data.sufficiency`, `fix.ml.bias.test`, `fix.ml.performance.observation`: all absent);
- a Data Scientist created a version with `bias_status = passed`, and it was accepted;
- a clerk recorded a final decision different from the suggestion with no reason: `overridden=True reason=False`;
- a Model Owner retired a deployed version with no confirmation: `state = retired`.

The new guard `test_m26_capture_pass2.py` on HEAD: **8 failed** (every page test), 21 skipped (the models it drives do not exist there).

**fix_real (8069) at the time of the audit:** 7 models, 6 deployed versions (all `bias_status = untested`), and 0 gates, 0 runs, 0 risks, 0 drift observations, 0 fallback tests. The new rules therefore block no existing record.

## 4. What was built

### Workspace (`cd_p03_portal/static/src/a11/m26.js`)

| # | Page | "+ New" | Chips now (new in bold) | New lists |
|---|---|---|---|---|
| 2 | Training Pipelines | **Record Training Run** (was Model Version) | **Training Run**, Model Version | Training Runs |
| 3 | Evaluation Gates | Evaluation Gate | Evaluation Gate, **Data-Sufficiency Gate**, **Bias Test** | Data-Sufficiency Gates, Bias Tests |
| 4 | Deployment & Monitoring | Record Drift Observation | Drift Observation, **Performance Observation**, Fallback Test | Production Performance |
| 7 | Bengali NLP & OCR | Classify Fault Text | Classify Fault Text, **Record Human Decision**, Run ML Model Inference | — |

- The Model Version form links its **Training Run**, and shows the bias status read-only ("follows the newest Bias Test").
- The ML Model form's Portfolio Declaration tab gains **Minimum History (months)** and **Minimum Volume**.
- **Retire** (Model Registry, Deployment Patterns) now asks "Who confirmed the fallback is now the consumers' standing path?".
- The Model Accuracy & Retraining Log shows training runs, the last run and the last production metric per model.

### Backend (`cd_ml_services` 19.0.0.4.0, `models/fix_ml_validation.py`, imported last)

| Record | Rules |
|---|---|
| `fix.ml.training.run` | Code version, snapshot, feature versions, hyperparameters (a JSON object), environment, start/end, outcome. A succeeded run needs its metrics; a failed or abandoned one says why. **The recorder must confirm no recovered M06 customer data** (BRU-AIM-03). Recorder stamped; append-only. A version may name only a succeeded run of its own model. |
| `fix.ml.data.sufficiency` | The bar is **copied from the model's declaration**, not typed; a model with no declaration cannot be gated. The result (met / deferred) is derived; deferred needs a revisit date. Evaluator stamped; append-only. **Promotion needs the model's newest gate to read Met; none fails closed** (BRU-AIM-12). |
| `fix.ml.bias.test` | Segments, metric by segment, largest disparity, assessment, next due. **Refused for the version's registrant and for the model's owner** (§13 SoD). **It sets the version's bias status**, which is no longer typeable by anyone but the engine. Append-only. |
| `fix.ml.performance.observation` | On a deployed version only: period, metric, value, target, floor (on the right side of the target), higher-is-better, labelled sample (> 0). Breach is derived. **A breach demotes the version (new state Auto-Demoted) when a prior deployed version exists, which then serves again.** With no prior champion the version keeps serving and the breach is posted as escalated (T-02: a model problem never blocks the business). Append-only. |
| `fix.ml.inference.run` | A decision that differs from the suggestion **needs an override reason**, checked before anything is written. |
| `fix.ml.model.version` | `training_run_id`, state `demoted`, `demoted_at`, `demotion_reason`; `action_retire(confirmation)` refuses without it (non-superuser) and posts it on the version; a demoted version can be retired. |

ACLs: Data Scientists record training runs, sufficiency gates, bias tests and performance; Evaluation Reviewers record sufficiency gates and bias tests; Model Owners record performance; every internal user reads. Company isolation rules regenerated for the four models only.

### Files

- `addons/domain/j_data_analytics/cd_ml_services/`: `models/fix_ml_validation.py` **new**, `models/fix_ml_governance.py`, `models/fix_ml_services.py`, `models/__init__.py`, `__manifest__.py`, `security/ir.model.access.csv`, `security/fix_isolation_rules.xml`
- `addons/platform/cd_p03_portal/static/src/a11/m26.js`, `controllers/a11/m26.py`
- Tests: `cd_p03_portal/tests/test_m26_capture_pass2.py` **new** (32 tests); updated to the new rules: `test_m26_capture_buttons.py` (page expectations), `test_a11_control_m26.py` (v05, r10, f01), `cd_ml_services/tests/test_ml_governance.py` (fixtures, retire, override)

## 5. Verification

All on the private clone `fix_test_m26c2` (copied from the M19 peer's clone at the same shared commit), after `-u cd_ml_services`: the module is at 19.0.0.4.0 and the four tables and new columns exist.

- **New guard** `test_m26_capture_pass2.py`: 32 passed. On HEAD code: 8 failed, 21 skipped (see §3).
- **Mutation check:** 19 mutants, each switching off one new rule. 16 were killed at once; the 2 test gaps found (a succeeded run with `{}` metrics, a lowered bar sent straight to the ORM) got tests and those mutants are now killed too. The one survivor is equivalent: putting `bias_status` back on the form whitelist still ends in a refusal, from the model's own guard.
- **Regression:** M26 suites (pass-1 guard, live captures, A11 M26 controls, cd_ml_services) plus the estate-wide suites (module pages, sub-module create button, screens wiring, report export standard, document buttons, KPI tiles, A11 cross-area, M25/M62/M63 controls): **1,101 tests, 0 failures, 2 skipped**.
  - Tests updated to the new rules: their fixtures now record a met data-sufficiency gate and seed the bias status the way a bias test would; retire passes a confirmation; an override carries a reason. Each also asserts the new refusal.
  - Not related to M26: `test_a07_p1_wiring.py::test_an_impact_assessment...` fails on this clone because `fix_device.population` is missing (the clone was never upgraded for that module).
- **ruff 0.8.4** check and format: clean.
- **Headless browser walk** on a private server (worktree code, port 8133, signed-in session, production bundle). Every page shows the "+ New" and chips in §4. Every new list and form opens with no error dialog, no console error and no "not served". The Training Run form shows its two tabs. The Model Registry list shows Mark Evaluated / Request Promotion / Retire.
- **Save through the real form** (Training Run, as the signed-in user):
  - without the M06 confirmation, the form showed *"Confirm that the training data holds no recovered M06 customer data - it is never used to train any model (BRU-AIM-03)."* and nothing was saved;
  - completed, it saved: stamped with the user, times stored in UTC (08:00 Dhaka → 02:00).

## 6. Open items (owner)

- **No model declares a minimum history or volume.** The spec gives none. Until the owner declares them on each model's Portfolio Declaration, no data-sufficiency gate can be recorded, so **no new version can be promoted**. The 6 deployed versions keep serving.
- **BRU-AIM-11** (no consumer, target and fallback → not deployed) is still not enforced: lead scoring and the BI aggregator have no stated target (as in pass 1).
- **Each M26 role still has one holder on fix_real.** The four-eyes rules (bias reviewer ≠ registrant ≠ model owner, promotion by another Model Owner) cannot be exercised by real people until more are named.
- Spec entities still with no record: the guard-rail intervention log (written by the gateway, not a person), the structured model card (`fix.model.card`: today one text field), and the generative session and retrieval corpus (no LLM endpoint exists).
