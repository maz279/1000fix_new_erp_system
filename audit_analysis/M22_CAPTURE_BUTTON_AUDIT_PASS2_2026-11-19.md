# M22 Learning & Certification: data-capture audit, second pass

**Date:** 19 Nov 2026 · **Branch:** `fix/m22-capture-pass2` (worktree `m22cap2-wt`, from `a6ca660a`) · **Spec:** `1000fix_ERP_Module/03_Modules/H_People_and_Workforce/M22_Learning_Competency_and_Certification.md` · **First pass:** `M22_CAPTURE_BUTTON_AUDIT_2026-11-13.md`

## 1. The question

The user again saw M22 sub-module pages without a relevant data-capture button.

The first pass (13 Nov) gave every page a "+ New" and a chip for every list on it, and built the training session. A count of chips is not the same as "relevant". This pass read each page against what a person decides there, per the spec:

- §5: the 40 features (FR-LMS-001…040);
- §8: the certification and training-need lifecycles;
- §9: the rules (BRU-LMS-01…15);
- §10.1: the 22 owned entities;
- §11: the automations.

For each, it asked whether that decision can be recorded on the page it belongs to.

## 2. What the spec says each page records (the gaps only)

| Page | What a person records there | Spec | Priority / class |
|---|---|---|---|
| 1 Competency Framework | The **role requirement**: for a role / position, each required competency with its own minimum level, mandatory flag and effective date | FR-LMS-002, entity `fix.role.competency` | P1 |
| 2 Skill Matrix & Assessment | The **gap analysis** (employee against role requirement) and the training need a gap raises | FR-LMS-005, FR-LMS-031 | P1 |
| 4 Training Delivery | The **training need** (lifecycle 8.2 starts with NEED IDENTIFIED), the **training plan** that consolidates needs per branch and period with its budget check, **participant feedback**, and **cancellation / substitution** of an enrolment | FR-LMS-031, 032, 036, 021; BRU-LMS-13 (H), BRU-LMS-10 (H); entities `fix.training.need`, `fix.training.plan` | P1 / P2 |
| 5 OJT & Mentoring | The **mentor assignment** and its **interactions** | FR-LMS-028, entity `fix.mentoring` | P2 |
| 6 Evidence & Analytics | The **effectiveness evaluation**: the operational measure the training targeted, before and after, and a conclusion | FR-LMS-035, BRU-LMS-15, AUT-LMS-12, entity `fix.training.effectiveness` | P1 / A |

## 3. What the code had (HEAD `a6ca660a`)

The page contents were evaluated the way the browser evaluates them: Node ran the engine's own `fregCreate` and `fregPanels` over the real registry fragments. The pass-1 guard (22/22) still passed.

| # | Page | "+ New" and chips at HEAD | Defect |
|---|---|---|---|
| 1 | Competency Framework | + Competency; Device Category, Learning Path | A learning path held **one** minimum level for all its competencies and named its role as **free text**. A role's per-competency requirement could not be recorded, and nothing linked a path to the employees it applies to. |
| 2 | Skill Matrix & Assessment | + Assessment; Assessment | **No gap analysis and no training need existed.** The Skill-Gap Heatmap counted levels per competency (below L3), not employees against their role. |
| 3 | Certification Register | + Certification; Certification | Matches the spec (register, renew, suspend, revoke, waivers). Unchanged. |
| 4 | Training Delivery | + Enrolment; Course, Learning Path, Training Session, Training Budget, Over-Budget Request | **No training need, no training plan, no feedback.** **An enrolment could never be withdrawn or substituted**: there was no such state or action and no delete right, so a wrong or cancelled seat stayed committed to the year's training budget and counted against the session's capacity for good. |
| 5 | OJT & Mentoring | + OJT; **no chip** | The page is named "Mentoring" but **no mentoring record existed** (only OJT). |
| 6 | Evidence & Analytics | + Audit Evidence; **no chip** | **No effectiveness evaluation.** The "Training Effectiveness" report counted pass rates, not the measure the training targeted (BRU-LMS-15). |

**fix_real (8069) at the time of the audit:** 504 employees (503 with a position), 3 learning paths (none with positions or per-competency requirements), 4 competencies, 0 courses, 0 enrolments, 0 sessions, 0 OJT records. The new gates therefore block no existing record.

## 4. What was built

### Workspace (`cd_p03_portal/static/src/a09/m22.js`)

| # | Page | Chips now (new in bold) | New lists / actions |
|---|---|---|---|
| 1 | Competency Framework | Device Category, Learning Path (form gains **Applies to Positions** and a **Competency Requirements** grid: competency, minimum level, mandatory, effective from) | Learning Paths: **Raise Training Needs from Gaps** |
| 2 | Skill Matrix & Assessment | Assessment, **Training Need** | **Role Gap Analysis** (report), **Training Needs** |
| 4 | Training Delivery | **Training Need**, **Training Plan**, Course, Learning Path, Training Session, **Training Feedback**, Training Budget, Over-Budget Request | **Training Needs** (Enrol / Cancel), **Training Plans** (Submit / Approve / Return / Cancel), **Participant Feedback**; Schedule & Attendance: **Withdraw**, **Substitute Trainee** |
| 5 | OJT & Mentoring | **Mentoring**, **Mentoring Interaction** | **Mentoring** (Start / Close / Cancel), **Mentoring Interactions** |
| 6 | Evidence & Analytics | **Effectiveness Evaluation** | **Effectiveness Evaluations** (Record Evaluation) |

Every new form is tabbed. The Training Effectiveness report gains **Evaluations** and **Measure Improved** columns, and excludes withdrawn seats.

### Backend (`cd_competency` 19.0.0.4.0, `models/fix_competency_capture2.py`, imported last)

**Role requirement and gap analysis (FR-LMS-002 / 005)**

- `fix.role.competency`: a line on the learning path: competency, minimum level (L1–L4), mandatory, effective from. One per competency per path. Only Training Managers set it.
- `fix.learning.path.position_ids`: the positions the role applies to.
- The gap analysis measures every employee holding one of those positions against every requirement in force:
  - "held" is the latest passed assessment by an independent assessor;
  - a granted certification in date counts as L3, as in the Skill-Gap Heatmap;
  - it reads in the caller's environment, so assessment results stay S2 (BRU-LMS-12).
- **Raise Training Needs from Gaps** opens one need per gap that has no open need. It picks the path's course for that competency. A mandatory requirement gives a high-priority need. Running it twice raises nothing new.

**`fix.training.need` (FR-LMS-031, BRU-LMS-13, lifecycle 8.2)**

- It records the employee, the competency and/or the course that closes it, the source, a source reference, the priority, the statement and the due date.
- Sources: role gap, M57 performance, M23 non-conformance, M59 safety, M17 new product, M08 new brand, M21 role change, certification lapse, manager request.
- **A safety need is always Mandatory (AUT-LMS-07)**, on create and on every later write.
- Training Managers raise it. Everyone else reads only their own need and their direct reports' (S2).
- Lifecycle: Identified → Planned (when it joins a plan) → Enrolled → Closed / Cancelled.
- **A passed enrolment closes the need. A failed or withdrawn one re-opens it** (AUT-LMS-10).
- A need in a plan is enrolled only once that plan is approved (the budget check of 8.2).

**`fix.training.plan` (FR-LMS-032)**

- Annual or quarterly, per branch / operating unit, with a budget. The planned cost is one seat of each need's course.
- Needs join it while it is a draft.
- To submit, every need must name its course and the plan must be inside its budget (BRU-LMS-10).
- It is approved or returned by a **Training Budget Approver who did not submit it**. It is frozen once submitted.
- Cancelling it puts its open needs back on the register, unplanned.

**`fix.training.feedback` (FR-LMS-036)**

- Content, trainer and applicability ratings (1–5), would-recommend, and comments.
- **Only the trainee gives it**, after attending (or after a decided result when there is no session). A Training Manager records it only for a trainee with no account.
- One per enrolment. It cannot be changed once submitted.
- It is read by the trainee, the trainer, the manager, HR and Training.

**Enrolment withdrawal and substitution (FR-LMS-021)**

- **Withdraw** (Training Manager, with a reason, before attendance or a result) frees the seat and sets the seat cost to 0, so it leaves the year's committed budget.
- **Substitute** withdraws the trainee and enrols another on the same course and session. The substitute goes through the normal capacity and budget rules, and is linked to the seat it took.
- A session's seats, its capacity check, its "Mark Held" attendance check and the roster event now ignore withdrawn trainees.

**`fix.mentoring` and `fix.mentoring.interaction` (FR-LMS-028)**

- A Training Manager pairs a mentee with a mentor, with objectives, a start date and a planned end. The mentor is not the mentee, and the same pair cannot run twice at once. The pair is fixed once started.
- Interactions are logged on an active mentoring, after they happen: date, mode, duration, topics and actions agreed.
- **The mentor or a Training Manager logs them, never the mentee.** Only the person who logged an interaction corrects it.
- **Close** records the outcome (achieved, partly, not achieved). It is done by the mentor or a Training Manager, never the mentee, and only with at least one logged interaction.
- Both records are S2: the mentee, the mentor, the mentee's manager, HR and Training read them.

**`fix.training.effectiveness` (FR-LMS-035, BRU-LMS-15)**

- It records the course and optionally a **held** session of it, the operational measure targeted, its unit and direction (higher or lower is better), the value before with its period, and the value after with its period.
- Change and result (improved / no change / worse) are computed.
- **Record Evaluation** needs the after-value, its period and a conclusion. **The session's trainer cannot evaluate their own session.** An evaluated record is final.

**Security**

- ACLs: requirement, need, plan, mentoring and evaluation are created by Training Managers only (`base.group_user` read). The Training Budget Approver writes plans. Feedback and interactions can be created by `base.group_user`, fenced by the code checks above. No deletes except requirement lines (the grid removes them).
- `security/fix_a09_m22_capture2_rules.xml`:
  - company rules on all 7 models;
  - operating-unit rules on need, plan and mentoring;
  - global S2 rules on need, mentoring, interaction and feedback.
- P03 surfaces declare server-side `pickers`: draft plans, active mentorings, held sessions, live sessions, enrolments that are not withdrawn. A09 surfaces are read as the caller, so the S2 rules apply in the workspace too.
- The write whitelist `a09/writable.py` was regenerated from the forms. No state, decider or outcome field is writable.
- No new domain events (they would need contract registration). Outcomes go to the chatter and to-dos.

## 5. Proof

| Check | Result |
|---|---|
| Guard `test_m22_capture_pass2.py`, engine-evaluated pages: each page offers the spec's capture, each new record is listed on its page and in the nav, every form field exists on its model and no form omits (or makes read-only) a required no-default field, the role-requirement grid, no workflow field writable, actions served and pickers fenced, ACL and S2 rules declared | **8/8**; **8/8 fail on HEAD** |
| Pass-1 guard `test_m22_capture_buttons.py` | 22/22 |
| Live `test_m22_capture_pass2_live.py`: non-admin Training Managers, a budget approver, a trainee, a mentor, a mentee (also as a Training Manager), a line manager and a bystander, through the ORM and the P03 endpoints | **12/12** |
| Workspace-wide static suites (estate pages, all sub-module mapping, create-button rules, A09 write whitelist, many2many picker, report export, form defaults, form engine, Tell-me) | all static checks pass; DB-backed failures on the stale shared `fix_test` were peers' missing tables, re-run on the private clone below |
| Regression on the private clone: all of `cd_competency/tests` + the DB-backed workspace suites | 1,440 passed, 4 failed, 1 setup error. See §5.2. |
| Mutation check | 22 of 24 mutants red. See §5.1. |
| Private server (`fix_test_m22c2`, port 8139), headless walk | the 6 pages show the chips in §4. Every new chip opens its tabbed form. The requirement grid shows "+ Add requirement". The 9 new or changed lists open with their actions and no error. A **Training Plan was saved through the real form** and is in the database (draft). The one JS error is Odoo's own `web_tour` asset on a fresh server (500), unrelated to M22. |

Two defects were caught only by the live tests and are fixed:

- The plan's cost first summed `mapped("course_id.cost_per_seat")`. A dotted `mapped` de-duplicates the courses, so two seats on one course were costed as one, and a plan over budget was submitted.
- A second feedback on the same enrolment reached the database's unique constraint instead of a clean refusal.

### 5.1 Mutation check

Each mutant re-introduces one defect. The script checked that each find-string matched exactly once, and restored the file byte for byte after each run (SHA-256 checked).

**22 of 24 mutants turn the live suite red.** They cover:

- the need: a safety need not forced mandatory, enrolment before the plan is approved, a pass that never closes it;
- the gap analysis: gaps raising a need twice, the held level ignored;
- the plan: submitted over budget, the submitter approves it, any trainer approves it, the cost counting each course once;
- feedback: given before attending, given by someone else, given twice;
- withdrawal: keeping the seat cost, the withdrawn trainee still holding the seat;
- mentoring: closed with no interaction, an interaction on a non-active mentoring, the mentor being the mentee, the mentee closing or logging (after one test was added, see below);
- evaluation: the trainer evaluating their own session, a session not held, an evaluated record editable.

The first run left four survivors:

- "Mentee closes own mentoring" and "mentee logs own interaction". The mentor-or-Training-Manager check also stopped a plain mentee, so the mentee bar only matters when the mentee is a Training Manager. A test now covers that case, and both mutants go red.
- **Two equivalents remain, both backed by the ACL**: "anyone raises a need" (`base.group_user` has no create right on needs) and "submitted feedback editable" (no one but the superuser has write on feedback).

### 5.2 Regression

On `fix_test_m22c2` (a clone brought to HEAD for all 166 modules: 0 models without a table), `cd_competency/tests` plus the DB-backed workspace suites (report export for every module, A09 control suite, A09 write whitelist, create-button rules, estate pages, sub-module mapping, many2many picker, A09 P0 people controls) gave **1,440 passed, 4 failed, 1 setup error**:

- **The 4 failures fail identically on untouched HEAD** (`a6ca660a`, detached worktree, same database):
  - the three round-2 relay tests (on a clone the event relay never publishes, as recorded in pass 1);
  - `test_workspace_dispatch_action_refuses_an_uncertified_technician`: the M02 field-order surface answers "Action not available for this surface". That surface is not M22's.
- **The setup error** (`test_enroll_techs_from_the_workspace`, a serialization failure) came from my own walk server's cron writing to the same clone. The test passes on a re-run with the server stopped.

## 6. Not built (owner decisions, automations or other modules)

| Item | Why |
|---|---|
| **Event-driven needs** from M57, M23, M59, M17 and M08 (AUT-LMS-04…08, T-06) | The need register and its sources exist now, so a person records them. Consuming those modules' events needs new contract-registered event consumers. That is an automation, not a capture. |
| **Brand-critical renewal escalation to the Service Head** (FR-LMS-012, BRU-LMS-05) | Page 3 records renewals (Renew drafts the new certificate), and the expiry cron alerts the manager. The competency has no "brand-critical" flag, and escalating to the Service Head is an automation. Owner to name the brand-critical certifications. |
| **Waiting list** (FR-LMS-021) | Cancellation and substitution are built. A full session still refuses a new enrolment rather than wait-listing it. |
| **Training vendor master** (FR-LMS-034, P2) | A session names its external provider as a partner. Rates, evaluations and contracts per vendor are not built. |
| **Effectiveness reminder 90 days after a session** (AUT-LMS-12) | The evaluation record exists. A cron flagging unevaluated sessions is not built. |
| **M55 consumer of `training.session.scheduled`** (FR-LMS-022) | Unchanged from pass 1. The event is published, but nobody consumes it yet. |
| **fix_real roles** | The Training Budget Approver role (needed to approve a plan) is held by admin only, as recorded in pass 1. The 3 learning paths name no positions yet, so the Role Gap Analysis is empty until a Training Manager fills them. |

## 7. State

- **Landed** `40421fae` (fix) + `a37d0844` (report) on `fix/a03-live-data-and-pending-work` by fast-forward (CAS `update-ref` + `read-tree -m -u`). Shared branch **pushed** (`87b79277..a37d0844`), and the feature branch `fix/m22-capture-pass2` too.
- **Deploy approved by the owner.**
  - Backups were taken first, both verified with `pg_restore -l` (1,892 and 1,889 table-data entries): `1000 fix/backups/fix_{real,dev}_pre_m22_capture2_2026-11-19.dump`.
  - `-u cd_competency,cd_p03_portal` ran on fix_real and on fix_dev; both exited 0.
  - Read-only check on both: cd_competency 19.0.0.4.0, the 7 new tables, 14 record rules.
- **LIVE on 8069 (fix_real) and 8090 (fix_dev) since 10:57 local, 19 Nov.**
  - The restart first needed every landed module upgraded, or the new processes would load code ahead of its schema. Peers kept landing during the deploy. With the owner's approval at each step, one wave upgraded the whole gap on both DBs, all with exit 0:
    - M27 `cd_contact_centre`, M23 `cd_qms_process`, M26 `cd_ml_services`;
    - M28 `cd_itsm`;
    - M25 `cd_bi_reporting`, M29 `cd_rbac_ext`, M30 `cd_entity_config` + `cd_fpa` + `cd_attendance`;
    - `cd_p03_portal`.
  - Before the restart, the version gap was 0 on both DBs.
  - Extra backups: `1000 fix/backups/fix_{real,dev}_pre_combined_m22_m23_m26_m27_2026-11-19.dump` (1,904 and 1,901 table-data entries).
  - One restart: 8069 = PID 64400, 8090 = PID 77212. Both logins answer 200. The new processes logged no ERROR, no missing table and no "Failed to load registry". Between the upgrade and the restart, the old 8069 process logged errors running the new M25/M29/M30 crons on its stale registry.
  - fix_real's live `web.assets_web.min.js` contains the new M22 forms.
  - **A signed-in, read-only headless walk on both 8069 and 8090** shows all 6 pages with the captures in §4. The 9 new or changed lists open with their actions and no error, and there are 0 JS errors.
  - Each peer session was told the PIDs, so it can run its own checks.
- Private clone `fix_test_m22c2`, its launch entry and the worktree `m22cap2-wt` were removed after verification.
