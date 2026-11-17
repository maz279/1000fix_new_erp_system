# M58 Talent Acquisition & Onboarding: Sub-Module Capture Audit (2026-11-17)

**Trigger.** The user observed that not every M58 sub-module page has a relevant data-capture button.

**Sources**
- Spec: `1000fix_ERP_Module/03_Modules/H_People_and_Workforce/M58_Talent_Acquisition_and_Onboarding.md`. Sections used:
  - §3: scope (16 in-scope capabilities; boundaries with M21, M22, M29, M54, M57, M59);
  - §5: FR-TAO-001 … 034;
  - §6: T-01 … T-10 (T-07 tasks as first-class objects, T-08 document integrity);
  - §8: the requisition-to-hire and candidate-data lifecycles;
  - §9: BRU-TAO-01 … 17;
  - §10.1: the 18 owned entities;
  - §11: AUT-TAO-01 … 17;
  - §13: roles and boundaries.
- Code:
  - `cd_p03_portal/static/src/a09/m58.js`: the page registry (7 sub-module pages);
  - `cd_p03_portal/controllers/a09/m58.py`: surfaces, reports and KPIs;
  - `cd_talent/models/*.py`: requisition, candidate, interview, evaluation, assessment, check, offer, onboarding plan, task and template, headcount budget, first-90 review.
- Live data (fix_real, read-only count on 17 Nov): every M58 table is empty (0 requisitions, candidates, interviews, assessments, checks, offers, plans, tasks, reviews, budgets) except one onboarding template with 6 task lines. There are 61 positions in M21.

## 1. What was there (HEAD c5feece6)

The pages were evaluated with the engine's own `fregCreate` / `fregPanels` in node, which is how the browser decides what a page shows.

| Page | Sub-module | "+ New" | Chips | Defects |
|---|---|---|---|---|
| 1 | Workforce Planning & Requisition | Requisition | Requisition | The **Headcount Budget** list and form (BRU-TAO-01) existed but sat on **no page**. No **job profile** existed (FR-TAO-004 P1: responsibilities, M22 competencies, qualifications, experience, band). |
| 2 | Sourcing | Candidate | Candidate | "**Job Postings**" listed **requisitions**: there was no posting record (FR-TAO-005 P1), so nothing enforced "no posting before approval" (BRU-TAO-02) or "internal consideration before external posting" (FR-TAO-006 P1, AUT-TAO-02). No **referral** record (FR-TAO-007; the source was a bare "Employee Referral" label with no referrer and no reward decision, AUT-TAO-17). No **channel/agency** (FR-TAO-008) and no **recruitment cost** (§10.1), so cost per hire (FR-TAO-034 P1) could not be stated. |
| 3 | Screening | none (by design) | none | Correct: the page is a slice of applied/screening candidates worked with Screen, Invite and Reject-with-outcome. No change. |
| 4 | Interviews & Assessments | "Interview Evaluation" (actually the interview round) | Interview Evaluation | The **practical assessment** list was on the page but had **no capture** there (its form existed but was not a chip). The form had **no tasks and no evidence** (FR-TAO-016 P1: "assessor, tasks, result and evidence"). **My Panel Evaluations** sat on **no page**, and its list offered "+ New", which the server **always refuses** ("An evaluation is opened by naming the panelist"). The "+ New" was labelled "Interview Evaluation" although it schedules a round. |
| 5 | Checks & Offers | Offer | Offer | The **reference & background check** list was on the page with **no capture** there. The check form could not record the referee contact (FR-TAO-018). The offer could not state its **probation period or benefits** (FR-TAO-020 P1), so the draft contract had no probation end. |
| 6 | Pre-Boarding | **Onboarding Plan** (hand-made) | none | The "+ New" made an onboarding plan by hand, but the plan is **opened by the hire** from the accepted offer; a hand-made plan has no employee and cannot start. **No pre-boarding document** existed (FR-TAO-023/024 P1, T-08): nothing collected NID, photograph, certificates, experience letters or bank proof, nobody verified them, and onboarding completed without them. |
| 7 | Onboarding Orchestration | **First-90 Review** | none | The page captured only probation reviews. The **onboarding tasks** (FR-TAO-027 P1, T-07) list and form existed but sat on **no page**; the task form showed its plan read-only, so even from the list a new task could not be saved. **Onboarding templates** (the task set by role) had **no screen at all**. No **induction session** (FR-TAO-029 P1). No **mentor** (FR-TAO-031). Tasks had **no dependencies** (FR-TAO-027, T-07). No **day-one readiness** report (FR-TAO-033 P1), although the readiness cron existed. |

Guard `cd_p03_portal/tests/test_m58_capture_buttons.py` on HEAD: **39 of 48 tests fail**, covering 6 of the 7 pages.

## 2. What was built

### 2.1 Records (cd_talent 19.0.0.4.0, `models/fix_talent_capture.py`)

| Record | Spec | Controls |
|---|---|---|
| `fix.job.profile` | FR-TAO-004 | Responsibilities, M22 competencies, qualifications, minimum experience, M57 band. Named on the requisition (`job_profile_id`, frozen with the approval); a profile for another position is refused. Recruitment maintains it; hiring managers read it. |
| `fix.job.posting` | FR-TAO-005/006, BRU-TAO-02, AUT-TAO-02 | Published only for an **open, approved** requisition. Publishing an internal posting stamps "internal only until" (`cd_talent.internal_consideration_days`, default 7); an **external** posting names its channel and is refused until an internal posting's window has passed. What was published does not change. State, dates and publisher are stamped, never typed. A candidate may name the posting they applied through (it must be published and be their requisition's). |
| `fix.recruitment.channel` | FR-TAO-008 | Type, agency (required for an agency), cost model, agreed fee (required unless free), contract reference. |
| `fix.recruitment.cost` | §10.1, FR-TAO-034 | Positive amount, cost type, channel (required for an agency fee), invoice reference. **Refused on a requisition that is not approved** (BRU-TAO-02). Feeds the new **Cost per Hire** report. |
| `fix.talent.referral` | FR-TAO-007, AUT-TAO-17 | One per candidate; a self-referral (the referrer's own email, or the referrer hired as the candidate) is refused; the candidate's source becomes "Employee Referral". The **reward is approved only after the hire**, by an **HR manager who neither recorded nor made the referral**; or declined with a reason. Paid through payroll (M56). |
| `fix.preboarding.document` | FR-TAO-023/024, T-08, BRU-TAO-06 | **The hire issues the checklist** (`cd_talent.preboarding_documents`, default NID, photograph, academic, experience, bank proof), all mandatory. Upload stamps the uploader, time and **SHA-256**. A **Background Verifier who did not upload it** (and is not the new hire) verifies or rejects it with a reason; a re-upload after rejection goes back to submitted; a verified document is a record. **Onboarding completes only when every mandatory document is verified.** |
| `fix.onboarding.induction` | FR-TAO-029, BRU-TAO-11 | Session type (company, policy, safety, systems, brand, branch), time, conductor, venue. **Only the conductor records** attended or missed (never the new hire, never Recruitment on their behalf), and only **after the session starts**. A session still unrecorded holds the onboarding open; a field hire whose safety induction exists but was not attended cannot complete. Conductors read and record their own sessions (record rules). |

Existing records gain what their pages are about:
- **Practical assessment**: tasks performed and an evidence file (FR-TAO-016), frozen once the assessment is the M22 baseline.
- **Offer**: probation class (BLA s.4(8)), probation months (default 6, capped 6 clerical / 3 skilled or other), benefits; all part of the approved terms. A probation offer with no period is not issued. At hire the **draft contract gets its probation class and end date**, and the **appointment letter states the probation and benefits**.
- **Onboarding plan**: mentor/buddy (FR-TAO-031; never the new hire), mandatory-document counters.
- **Onboarding task**: "depends on" another task of the same plan (no loops); a dependent task cannot be completed while its prerequisite is open (T-07). The task's plan is editable on a new task (so "+ New" saves) and fixed afterwards. Ad-hoc tasks stay optional (mandatory tasks come only from the template).
- **Background check form**: the referee / issuing authority contact.

### 2.2 Pages (`m58.js`, `controllers/a09/m58.py`, regenerated `controllers/a09/writable.py`)

| Page | "+ New" | Chips | Lists on the page |
|---|---|---|---|
| 1 Workforce Planning & Requisition | Requisition | Requisition, **Headcount Budget**, **Job Profile** | Requisitions, Approval vs Budget, **Headcount Budget**, **Job Profiles** |
| 2 Sourcing | Candidate | Candidate, **Job Posting**, **Referral**, **Recruitment Channel**, **Recruitment Cost** | **Job Postings (postings)**, Candidate Pipeline, **Employee Referrals**, **Channels & Agencies**, **Recruitment Costs**; report **Cost per Hire** |
| 3 Screening | none (works existing applications) | none | Candidate Pipeline |
| 4 Interviews & Assessments | **Interview Round** | Interview Round, **Practical Assessment** | Structured Interviews, **My Panel Evaluations** (no "+ New"), Talent Assessment |
| 5 Checks & Offers | Offer | Offer, **Background Check** | Reference & Background, Offers |
| 6 Pre-Boarding | **Pre-Boarding Document** | Pre-Boarding Document | **Pre-Boarding Documents**, Pre-Boarding plans (no "+ New": the hire opens them) |
| 7 Onboarding Orchestration | **Onboarding Task** | Onboarding Task, **Induction Session**, First-90 Review, **Onboarding Template**, **Template Task** | **Onboarding Tasks**, **Induction Sessions**, First-90-Days, **Onboarding Templates**, **Template Tasks**; report **Day-One Readiness** |

The two system-written lists (My Panel Evaluations, Pre-Boarding plans) now say `create: false` with an empty-state explanation, and their forms open only from a row (`pick` message). Every new list model and action is served by the M58 controller; the write whitelist was regenerated from the forms, so stamped fields (state, verifier, SHA-256, reward decision, publication dates) cannot be posted.

### 2.3 Ripple

The two onboarding completion tests (`test_a09_talent_controls.py`, `test_a09_talent_r2.py`) now verify the pre-boarding documents before completing (helper `_verify_documents`); the first also asserts that completion is refused until they are verified. Both are behaviour changes required by FR-TAO-023/024, not test fixes.

## 3. Evidence

All run on a private clone `fix_test_m58` (template `fix_test`, upgraded with `-u all` from the worktree, exit 0) and a private server on port 8093. Nothing touched fix_real or fix_dev.

| Check | HEAD c5feece6 | After |
|---|---|---|
| Guard `test_m58_capture_buttons.py` (node runs the engine's `fregCreate`/`fregPanels` over the real registry) | **39 of 48 fail** | 48 / 48 pass |
| Estate page standard `test_estate_module_pages.py` (all 67 modules) | pass | pass |
| Live ORM + controller suite `cd_talent/tests/test_m58_capture_live.py` (non-admin users, real `/p03/model/write`) | n/a | 23 / 23 pass |
| All `cd_talent` suites + the A09 control suite, A09 P0 controls, write whitelist, A03/A04 registry coverage, KPI tiles, estate | n/a | **1,211 tests, 0 failed, 0 skipped** after one fix (below) |
| Mutation check: 15 controls broken one at a time (posting before approval, internal window, uploader verifies, document gate, checklist at hire, conductor only, not before start, referral maker approves, reward before hire, task dependency, probation cap, spend before approval, page 4 chip, evaluations "+ New", page 7 tasks) | n/a | **15 / 15 caught** |
| Server probe on 8093: every M58 list, report and form through `/p03/model/records`, `/report`, `/form` | n/a | 49 / 49 served, 0 errors |
| UI walk (8093, `?debug=assets`) | n/a | Page 6 shows "+ New Pre-Boarding Document" and its form (two tabs) opens; page 7 shows "+ New Onboarding Task", five capture chips and both reports |

The one failure on the first full run was real: the A09 control suite refuses a form that offers a workflow-guarded field, and the task's plan was guarded. The plan is the creator's input, not a workflow stamp, so it left the guard set and is now frozen by its own write check ("does not move"), which the live suite also tests.

Lint: `ruff check` and `ruff format` clean on every changed Python file.

## 4. Left for the owner

- **No M58 data on fix_real.** All M58 tables are empty; nothing live is affected by the new completion gate.
- **Who verifies documents and conducts inductions.** The Background Verifier role is held by the administrator only (existing A09 decision §7.1). Pre-boarding documents cannot be verified by the person who uploaded them, so at least one verifier besides the recruiter must be appointed before the first hire completes onboarding.
- **Policy settings** (system parameters, defaults in brackets): internal consideration window `cd_talent.internal_consideration_days` (7; 0 switches it off), the pre-boarding checklist `cd_talent.preboarding_documents` (nid, photo, academic, experience, bank).
- **Referral reward payment.** The approved reward is recorded on the referral; M56 has no one-off earnings input that reads it yet, so payroll pays it from the approved list.
- **Not built (spec P2 or another module's):** talent pool (FR-TAO-009), candidate comparison (FR-TAO-017), provisioning requests as commands to M29/M17 (FR-TAO-028: onboarding tasks with the IT, stores and facilities functions carry them today), learning-path assignment in M22 (FR-TAO-030).

## 5. Landing and deploy (18 Nov 2026, user-approved "Land and deploy")

- **Re-test on the combined tree** (rebased over M55 b5699893; `controllers/a09/writable.py` regenerated with both modules' fields): 1,258 tests, 0 failed, 0 errors, 0 skipped.
- **Landed** fix 261cc780 on `fix/a03-live-data-and-pending-work`: a compare-and-set fast-forward from 88625d2b, then the shared checkout synced with `read-tree -m -u`. Not pushed.
- **Backup**: `fix_real_pre_m58_capture_2026-11-18.dump` (50.0 MB, 51,498 entries) in `_migration/backups`.
- **fix_real**: `-u cd_talent,cd_p03_portal` exit 0, 0 errors. `cd_talent` is now 19.0.0.4.0 and the 7 new models exist. The version-gap check over 83 installed `cd_` modules found 0 gaps.
- **8069** restarted once: PID 28840 became 63524. Registry loaded with 155 modules and 0 errors; `/web/login` returns 200. The backend bundle `0ba1043` (attachment 10306) carries every new M58 form and report, and 8069 serves it.
- The peer sessions M55, M21, M56, M57 and M01 held their restarts and landings during the deploy.
- **fix_dev / 8090** was upgraded the same night on request ("Upgrade fix_dev"). Backup `fix_dev_pre_m58_capture_2026-11-18.dump` (45.6 MB, 51,311 entries). Only `cd_talent` lagged; `-u cd_talent,cd_p03_portal` exit 0, 0 errors. 8090 restarted PID 28660 -> 47236, registry loaded with 151 modules and 0 errors, bundle `0ba1043` (the same as fix_real) carries the M58 forms. Version gaps over 80 installed `cd_` modules: 0.
