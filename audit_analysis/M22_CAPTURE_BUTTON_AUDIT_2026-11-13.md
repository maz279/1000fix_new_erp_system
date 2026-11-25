# M22 Learning & Certification: data-capture button audit

**Date:** 13 Nov 2026 · **Estate:** fix_real on port 8069 · **Status:** live on 8069/8089 since the 19:39/19:40 restart (user approved). `-u cd_competency` ran on fix_real first. Production bundle `aba7583`. Nothing is committed.

## 1. The question

The M22 workspace has 6 sub-module pages (Function Register, 52 functions). Not every page showed a capture button that fit what the page covers. Which records should each page capture, and what did it actually offer?

## 2. What the spec says

Sources:

- `1000fix_ERP_Module/03_Modules/H_People_and_Workforce/M22_Learning_Competency_and_Certification.md` (FR-LMS-001…040, BRU-LMS-01…15, lifecycle §8, entities §10)
- `contracts/nav/registry.json` (6 sub-modules)

| # | Sub-module | Spec | What a person records there |
|---|---|---|---|
| 1 | Competency Framework | FR-001/002/004 | a competency; a device category and tier; the competencies a role requires |
| 2 | Skill Matrix & Assessment | FR-003/005/006/007 | an assessment: assessor, method, score, evidence |
| 3 | Certification Register | FR-009…016, FR-039/040 | a certification; renew, suspend or revoke it; the eligibility override log |
| 4 | Training Delivery | FR-017…026, FR-029, FR-033 | course, learning path, **session (date, trainer, venue, capacity)**, enrolment, **attendance**, budget, over-budget request |
| 5 | OJT & Mentoring | FR-027/028 | an OJT record: mentor, period, hours, tasks observed |
| 6 | Evidence & Analytics | FR-035/038 | audit evidence for a technician or brand |

## 3. What the code had (before)

The engine's own `fregCreate` and `fregPanels` were run over the real registry. Every page and every nav screen was also clicked on 8069.

Every page did show a "+ New". The defects were in **relevance**: records the page lists or the spec assigns to it had no capture, and some forms could not record what the page is about.

| # | Page | Capture before | Defect |
|---|---|---|---|
| 1 | Competency Framework | + New Technical Competency Definition | The Device Categories list sat on the page **with no capture**. The role requirement (FR-002) had no capture here. |
| 2 | Skill Matrix & Assessment | + New Assessment | The form had **no method/evidence field** (FR-006: "evidence retained"). |
| 3 | Certification Register | + Certification | The **Certification Waivers** list (override log, FR-040) was on **no page at all**. |
| 4 | Training Delivery | + New Enrolment; Course and Learning Path chips | "Schedule & Attendance" captured an enrolment with **no session, date, trainer, venue or attendance**: no session model existed (FR-020/021/023). The Training Budget and Over-Budget Request lists were on the page **with no capture**. The Learning Path form had **no competencies and no courses**, so a path could not hold its content (FR-018). |
| 5 | OJT & Mentoring | + New OJT | The form had **no end date and no tasks observed** (FR-027). |
| 6 | Evidence & Analytics | + New Evidence | The form could **not name the technician or brand** the evidence proves (FR-038), nor where the original is held. |

Device Category form: it had no parent category.

## 4. What was changed

| # | Page | Capture now |
|---|---|---|
| 1 | Competency Framework | + New Competency, plus **Device Category** and **Learning Path** chips. The Learning Paths list is on the page; a path = target role + required competencies + minimum level (FR-002). |
| 2 | Skill Matrix & Assessment | + New Assessment; the form gains **Method & Evidence** |
| 3 | Certification Register | + Certification. The **Certification Waivers** list is now on the page. It stays create-less: a waiver is raised from the M02 job and decided in the approver's inbox. |
| 4 | Training Delivery | + New Enrolment (now with **Session** and **Attendance**), plus chips **Course**, **Learning Path**, **Training Session**, **Training Budget** and **Over-Budget Request**. A new **Training Sessions** list (in the nav too) has Schedule / Mark Held / Cancel. The Schedule & Attendance list has **Mark Attended / Mark Absent**. |
| 5 | OJT & Mentoring | + New OJT; the form gains **To** date and **Tasks Observed & Observations** |
| 6 | Evidence & Analytics | + New Evidence; the form gains **Audited Technician**, **Audited OEM Brand** and **Original Held At** |

### New record: `fix.training.session` (cd_competency)

These fields are all on the session record:

- course and delivery mode (classroom / practical / online / external)
- trainer (an employee), or an external provider and trainer (FR-029)
- venue
- start and end, and capacity
- seats taken and attended (both computed)
- state: planned → scheduled → held / cancelled

Rules, each covered by a test:

- Only Training Managers create or move a session; everyone else reads.
- The session ends after it starts. An external session names its provider or trainer.
- Scheduling needs a trainer, and a venue for classroom or practical sessions. It publishes `training.session.scheduled` with the trainees and the window, for the roster (FR-022 / BRU-LMS-08). **No M55 consumer exists yet.**
- A session is marked held only when every attendance is recorded. A held or cancelled session is final, and a session that already has recorded attendance cannot be cancelled.
- An enrolment may name a session of the same course. Capacity is enforced, and a held or cancelled session takes nobody new.
- Attendance is recorded by action only (never typed), by a Training Manager, never for oneself, and only on a scheduled session.
- **An absent trainee is not passed.** Enrolments without a session work exactly as before.

### Files

- `addons/domain/h_people/cd_competency/models/fix_training_session.py` **new**; `models/__init__.py`; `data/competency_ops_sequences.xml` (TRS/ sequence); `security/ir.model.access.csv`; `security/fix_isolation_rules.xml`
- `addons/platform/cd_p03_portal/static/src/a09/m22.js`
- `addons/platform/cd_p03_portal/controllers/a09/m22.py`: session surface, plus attendance actions on enrolment
- `addons/platform/cd_p03_portal/controllers/a09/writable.py`: regenerated; the diff holds only M22 lines
- Tests: `cd_p03_portal/tests/test_m22_capture_buttons.py` (22 tests, **15 fail on HEAD**) and `cd_competency/tests/test_m22_training_session.py` (15 tests)

## 5. Verification

- **Private clone `fix_test_m22`, built in worktree `1000 fix/m22wt` at HEAD:**
  - cd_competency suite: **92 passed, 3 failed**. The 3 are relay-based round-2 tests. On the clone the event relay never publishes (the event stays `pending`), and two of them fail identically with the new model unloaded. Calling the `training.passed` consumer directly creates the evidence with this change.
  - Workspace suites (estate pages, all sub-module mapping, create-button rules, A09 whitelist, A09 controls, M22 guard): **1,012 passed, 0 failed**.
  - ruff 0.8.4 check and format: clean.
- **fix_real:**
  - `-u cd_competency` clean: 155 modules, no errors. `fix_training_session` and the enrolment `session_id` / `attendance` columns exist.
  - Pre-restart column-gap check of peers' uncommitted model edits: none adds a stored column that is missing.
- **After the restart, production bundle (no debug):**
  - bundle `aba7583` contains the change;
  - 33 calls (every M22 list, form and report) with **0 errors, 0 dropped columns, 0 missing form fields**;
  - a session write is accepted by the whitelist ("Record not found" on a dummy id, not "not editable").
- **Click sweep of all 6 pages:** each shows the captures in section 4. The Training Session chip opens the form with no error.

## 6. Open items (owner / build)

- **fix_real has 0 courses, 0 enrolments, 0 assessments and 0 certifications.** The session form's Course picker is therefore empty until a Training Manager adds courses (Course chip on Training Delivery).
- `cd_competency.group_training` has 3 holders on fix_real (admin, Md. Masud Rana, Mostofa Monower). The verifier, dispatch-override and budget-approver roles are held by **admin only**, so grants, waivers and budgets cannot be decided by a real person yet (owner decision).
- Spec entities with **no model** (build gaps, not capture defects):
  - training needs (FR-031, auto-generated from M57/M23/M59/M17/M08 events)
  - training plan (FR-032)
  - training vendor master (FR-034); a session names its provider as a partner
  - effectiveness evaluation before/after (FR-035)
  - participant feedback (FR-036)
  - waiting lists and substitution (FR-021)
  - mentoring as a relationship apart from OJT (FR-028)
  - the M55 consumer that removes trainees' availability (FR-022): the event is published, nobody consumes it yet
