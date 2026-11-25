# A09 ERP audit — R6 · M58 Talent Acquisition & Onboarding

Auditor: R6 · Date: 2026-11-22 · Code: `addons/domain/h_people/cd_talent` @ worktree HEAD
`6f0d6a54` (module version 19.0.0.5.0), P03 surfaces `addons/platform/cd_p03_portal/controllers/a09/m58.py`,
`static/src/a09/m58.js`. Probes: `C:\Users\DELL\AppData\Local\Temp\a09erp\R6\` (probe1_facts.py,
probe2_chain.py, probe3_access.py). **Execution note:** the ORM probes were written but NOT
executed — the shared machine hit its usage cap and the lead stopped the runs — so every
"[probe…]" reference below is **[STATIC]** (source-verified, not executed). Findings F2, F12, F13
carry static evidence only; F1/F5 rely on file:line plus the module's own tests. The test
baseline run was interrupted mid-suite: **44 passed, 1 failed** (first failure at collection
position 45 = `test_a09_talent_r2.py::test_the_passed_assessment_becomes_the_m22_baseline_at_hire`,
before the short summary; run stopped by the lead, incomplete — needs a clean serial re-run).

## 3. Settings register (live values NOT measured — probe not completed)

| key | live on fix_real_a09 | code default | effect |
|---|---|---|---|
| `cd_talent.require_headcount_budget` | [probe not completed — read directly with: `docker exec compose-postgres-1 psql -U fix -d fix_real_a09 -Atc "select value from ir_config_parameter where key='cd_talent.require_headcount_budget'"`] | 0 | 0 = a requisition without any approved budget is ACCEPTED (BRU-TAO-01 half-off); an existing budget is always enforced |
| `cd_talent.candidate_retention_days` | [probe not completed — same query] | 0 | 0 = retention clock never set, erasure cron idle (F3) |
| `cd_talent.minimum_hiring_age` | [probe not completed] | 14 | 14 matches BLA 2006 s.34(1) (child <14 prohibited); adolescents 14–18 lawful only with a s.37 fitness certificate — not captured (ADVISER) |
| `cd_talent.readiness_lead_days` | [probe not completed] | 7 | day-one readiness escalation 7 days before start (AUT-TAO-11) |
| `cd_talent.internal_consideration_days` | [probe not completed] | 7 | external posting blocked until the internal window passes; 0 switches FR-TAO-006 off |
| `cd_talent.preboarding_documents` | [probe not completed] | nid,photo,academic,experience,bank | mandatory checklist issued at hire |
| `cd_hr_core.identity_hash_key` | [probe not completed] | minted at install | present = candidate/employee NID hashing active |

## 4. Measured facts on fix_real_a09 (L)

[probe not completed — probe1_facts.py is ready to run (settings register, per-group role holders,
all 28 M58 table counts, position headcount/grade coverage vs M57 bands, the 4 crons + cron-user
TZ, identity counts, onboarding template state, outbox counts, M63 domains); no live numbers were
captured before the cap. From the 17 Nov capture audit (verified then on fix_real, re-check live):
every M58 table empty except one onboarding template with 6 lines; 61 positions; all approver
groups held only by admin/root.]

---

## 1. Findings

| id | severity | category | finding | evidence | proposed fix | files a fixer would touch |
|---|---|---|---|---|---|---|
| M58-F1 | P1 | C/L | The hire chain cannot complete end-to-end without a manual M21 edit: `hr.employee.employee_code` has no default/sequence, the M58 hire (`_fix_create_employee`) does not set it, and the onboarding completion gate refuses ("the employee has no employee code (M29 keys the identity on it)") until HR types one by hand. Spec T-02 "no partial state" / KPI-287 "employees created manually rather than through handover". | `cd_talent/models/fix_talent.py:927-951` (create vals, no code), `fix_talent.py:1457` (gate); grep: no auto-assign of `employee_code` anywhere (`cd_employee_core/models/hr_employee_ext.py:48` plain Char); own test works around it by typing a code (`tests/test_a09_talent_r2.py:427`); probe2 log "employee_code set at hire? False" → "complete blocked". | Mint a company sequence `EMP/%(year)s/` (or reuse M21's) in `_fix_create_employee`, or make `employee_code` required-with-default on the M21 master (M21 side). | `cd_talent/models/fix_talent.py`, `cd_employee_core/models/hr_employee_ext.py` |
| M58-F2 | P1 | B/C | The Recruiter Officer — the module's primary operator (R45) — cannot read `fix.talent.offer` at all: the ACL grants offer read/write only to HR Manager, Offer Approver and CFO tier. The P03 "Checks & Offers" page and the Offer form raise AccessError for the recruiter; the recruiter cannot draft or even see offers, though the spec gives the recruiter C/R/U on the pipeline and denies only *approval*. | `cd_talent/security/ir.model.access.csv` lines 6/18/20 (no `group_talent` row for `fix.talent.offer`); probe2 "recruiter reads offers -> AccessError"; `controllers/a09/m58.py:36-37` kpis() special-cases the AccessError. | Add `access_fix_talent_offer_role` read (+create for drafts) for `cd_talent.group_talent`; keep issue/ approve behind the routed approval (already enforced). | `cd_talent/security/ir.model.access.csv` |
| M58-F3 | P1 | J/L | Candidate retention/erasure is OFF in code default and on live: `cd_talent.candidate_retention_days = 0` means `retention_until` is never set on rejection, so the erasure cron (AUT-TAO-16, BRU-TAO-14) never fires and unsuccessful applicants' data (NID in clear, family, documents) is retained indefinitely — precisely the PDPA 2026 exposure the spec bans (T-03; PDPA 2026 requires erasure when purpose ends and bars keeping data "longer than necessary"). | `cd_talent/models/fix_talent.py:841-851` (`if days:` …), `data/fix_talent_automation.xml:17-20` (value 0, noupdate), probe1 settings register; erasure mechanics proven to work when the clock is set (probe2 "erased candidate header"). | Owner decision + config: set a retention period (recommend 180 days, 365 with talent-pool consent) and make 0 refuse new applications rather than silently disabling erasure; implement the separate talent-pool period (field `talent_pool_consent` exists but has no effect). | `cd_talent/models/fix_talent.py`, `data/fix_talent_automation.xml`, owner |
| M58-F4 | P1 | I/T-04 | Candidate NID is held in CLEAR on `fix_candidate.nid_number` for the whole pipeline (only the hash is added). Spec T-04/AC-13: "NID and other sensitive identifiers reside in the Bangladesh-resident store, **both for candidates and for employees**"; the estate moved employee NIDs to the residency store (M21-A6) but candidates keep a plaintext column, readable by every role with candidate read (talent, both approvers, verifier, CFO tier, HR manager). | `cd_talent/models/fix_talent.py:497-503` (plain Char, help admits "held in clear only until the hire"), probe3 "verifier reads nid_number in clear: 1995123456789"; biodata migration erases only at hire (`migrations/19.0.0.3.0/post-migrate.py`). | Route candidate NID/birth-reg/passport writes through `libs/py/fix_residency` exactly like M21 (keep the keyed hash for duplicates); keep only the pointer + hash on the row. | `cd_talent/models/fix_talent.py`, `fix_candidate_biodata.py`, migration |
| M58-F5 | P2 | C | No reversal path for a hire: no action unhires a candidate, no `action_cancel` exists on `fix.onboarding.plan` (the "cancelled" state is unreachable by any real action), and a wrongly-completed hire leaves the employee, contract, M22 baseline, letter and published `employee.joined` in place with no undo (KPI-287 in reverse). | `fix_talent.py:1134-1144` (state list incl. cancelled), `1463-1494` (only action_start/action_complete); probe2 "plan has action_cancel? False", "candidate has action_unhire? False". | Add a guarded `action_cancel` on the plan (draft/in_progress only) that unlinks the draft contract + M22 baseline, archives the employee, clears `employee_id`, resets the candidate to offered and recalls the joiner event; keep completion final. | `cd_talent/models/fix_talent.py` |
| M58-F6 | P2 | G | 9 of the 10 spec domain events are never published: `requisition.approved/blocked`, `candidate.applied`, `assessment.completed`, `offer.issued/accepted/declined`, `onboarding.started`, `readiness.incomplete`, `candidate.erased`, `probation.plan_created` have no `fix.event.outbox` emit; only `employee.joined` flows (via the M21 master, correctly held to onboarding completion). M54 (headcount consumption event), M25 BI and M60 (erasure) consumers named in the spec get nothing. | grep: only `_emit_jml("employee.joined", …)` in `cd_talent` (`fix_talent.py:1493`); `contracts/events/master-event-registry.json` has no M58 events; probe2 outbox check. | Publish the spec's events through `libs/py/fix_events.publish` at the existing transitions (they all exist as actions); at minimum `requisition.approved`, `offer.accepted`, `onboarding.started`, `candidate.erased`. | `cd_talent/models/fix_talent*.py`, `contracts/events` regen |
| M58-F7 | P2 | G/K | Candidate outcome communication (FR-TAO-019, BRU-TAO-16, KPI-284) is an internal chatter note only: `action_reject` records the reason and `message_post`s; nothing sends SMS/e-mail to the candidate through M27 (`fix.notification.config` / transparency notices are unused by cd_talent). Every KPI-284 measure stays 0 by construction. | `fix_talent.py:832-854`; grep `fix.notification|transparency` in cd_talent → none. | On reject/offer-issue/offer-decline raise an M27 notification (SMS class, BD-01 masking rules) keyed on candidate phone; record the delivery on the candidate. | `cd_talent/models/fix_talent.py`, M27 service |
| M58-F8 | P2 | K | The appointment letter is a plain .txt blob, not a professional M24 document: `_fix_appointment_text` renders ASCII into `fix.hr.document.file_data` (`Appointment_Letter_*.txt`), with no letterhead, no Bengali text, no PDF, no cd_doc_suite print mixin, no cd_esignature envelope for the candidate's acceptance (acceptance is any binary the HR manager uploads). BLA 2006 s.5 + Labour Rules 2015 r.19 also expect the appointee's father's name and address in the letter, which the text omits. | `fix_talent.py:1211-1272`; probe2 "letter is plain text (not PDF/letterhead): True"; cd_doc_suite print mixin unused (`cd_doc_suite/models/fix_doc_print.py`). | Render the letter through the estate's document suite (letterhead PDF, Bengali version), add father's name + present address; send the candidate acceptance through `cd_esignature.envelope`. | `cd_talent/models/fix_talent.py`, `cd_doc_suite`, `cd_esignature` |
| M58-F9 | P2 | G/L | Onboarding template ships with no owners and no lead times: every default line has `owner_user_id` empty (falls back to the hiring manager or the recruiting user) and `due_offset_days = 0` (everything due on the join date), so "IT access", "tools", "ID card" and "safety" tasks are all dated the start date itself — the 7-day readiness escalation therefore always fires after the fact. AUT-TAO-10 requires due dates *before* the start date for provisioning tasks. | `data/fix_onboarding_template_data.xml` (noupdate; no owner/due fields set), `fix_talent.py:1358-1386` (fallback owner, `joined_date + offset`); probe2 "task due dates = joined date (no lead times): True"; Update-4 decision list "onboarding owners and lead times" still open. | Owner decision, then seed owners (IT task → IT role, stores → stores role, safety → HSE) and negative offsets (e.g. access −7, equipment −3, ID −2, safety −1); make the readiness lead `cd_talent.readiness_lead_days` interact with them. | `cd_talent/data/fix_onboarding_template_data.xml`, owner |
| M58-F10 | P2 | G | AUT-TAO-14 (day-30/60/90 check-in triggers) does not exist: `fix.talent.first90` is a manual record with no cron, no scheduled activity and no feed into the M57 probation review (spec §12.2 "First-90-days plan feeding the probation review"; FR-TAO-032 "feeding the M57 probation review"). | `fix_talent_ops.py:808-847` (model, no automation); grep: `first90` referenced by neither `cd_performance` nor `cd_hr_core`; only 4 M58 crons in `data/fix_talent_automation.xml`. | Cron: for each completed onboarding plan schedule day-30/60/90 activities to the mentor/reviewer; on day-90 open the M57 probation review record. | `cd_talent/models/fix_talent_ops.py`, `data/fix_talent_automation.xml`, `cd_performance` |
| M58-F11 | P2 | F/G | Referral reward (AUT-TAO-17) is approved in M58 but never paid: `cd_payroll_bd` contains no reference to `fix.talent.referral` — no one-off earning, no AP/payment path; the reward stops at a status field. Spec §12.2: "M56 Payroll — new employee payroll setup data; referral reward (Command)". Capture audit already flagged it (18 Nov, §4); still true at HEAD. | grep `referral` in `cd_payroll_bd/models/*` → none; `fix_talent_capture.py:577-608` (approval only); probe2 "HR manager approved reward: True" then nothing consumes it. | M56 side: add a one-off earning input reading approved `fix.talent.referral` rows (decided_by ≠ payer, paid after the new hire's confirmation per AUT-TAO-17) or an M52 AP line to the referring employee. | `cd_payroll_bd/models/…` (M56 owns the gap) |
| M58-F12 | P2 | D | Requisition approval does not exclude the hiring manager who is the *subject* of the hire chain: the SoD mixin excludes requester/creator/subject employees, but a Requisition Approver who is also the requisition's `hiring_manager_id` can approve their own requisition (they did not create it), and nothing stops the hiring manager from sitting on the interview panel that evaluates their own candidates. Spec §13 boundary is "a hiring manager sees only their own requisitions" (met) but BRU-TAO-07 independence is about panelists only. | `fix_people_approval.py:120-143` (conflict = create_uid/requester/subject/preparer; `hiring_manager_id` not consulted); `fix_talent.py:225-245` (`action_add_panelist` excludes only the candidate themselves). | Add `hiring_manager_id` to `_people_conflicted_users` for requisitions; refuse a panelist who is the requisition's hiring manager or its approver. | `cd_talent/models/fix_talent.py`, `fix_talent_ops.py` |
| M58-F13 | P2 | H | `first90_retention` KPI reports a false 0.0% when no review exists (unknown ≠ 0), and `funnel_conversion` uses `counts["applied"] or len(candidates) or 1` as base, which mixes denominators when applied=0 but other stages non-empty. Time-to-fill/report packs are honest ("Not filled"); the KPI tile is not. | `controllers/a09/m58.py:465` (`if reviews else 0.0`), `:168`; probe2 KPI dict. | Return `None` (renders "—") when there are no reviews; base the funnel strictly on the applied pool or state both. | `cd_p03_portal/controllers/a09/m58.py` |
| M58-F14 | P2 | A | FR-TAO-006/017/009 gaps that remain: talent pool (FR-TAO-009) not built (`talent_pool_consent` captured but unused — see F3); candidate comparison (FR-TAO-017) absent; internal-candidate sourcing from M57 succession (FR-TAO-006 second half) absent — `source='internal'` exists but nothing surfaces succession candidates. Known "not built" from the capture audit; verified still true at HEAD. | `fix_talent.py:484-495` (source list), no `fix.succession` reference in cd_talent (grep). | Backlog per owner priority (all P2 in spec). | `cd_talent` |
| M58-F15 | P3 | E | Offer `valid_until` is optional: an issued offer without a validity date never lapses (cron requires `valid_until` set) and stays "live" forever, blocking other offers for the candidate. FR-TAO-022 expects lapse tracking. | `fix_talent_ops.py:703-704` (gate only `if self.valid_until`), `:795-805` (cron filter). | Require `valid_until` at approval (default today+N config), or expire offers with no validity after N days. | `cd_talent/models/fix_talent_ops.py` |
| M58-F16 | P3 | E | Probation label promises "Skilled (3 months, extendable by 3)" but the constraint refuses >3 for skilled, so the extension the label advertises cannot be recorded (and the BLA extension rule is an open legal question — ADVISER). Clerical 6 / others 3 caps match BLA 2006 s.4(8). | `fix_talent_capture.py:51-57,1071-1080`. | Either implement the extension as a second write (extend −3, cap total 6) with counsel sign-off, or fix the label. | `cd_talent/models/fix_talent_capture.py` |
| M58-F17 | P3 | B/I | `fix.talent.first90` and the interview-evaluation list are unreachable for a Hiring Manager: ACL gives first90 read only to `group_talent` (and HR manager by implication), so the manager who runs the 30/60/90 conversation cannot see or record it from P03 (screen M58-first90). R06 is supposed to hold first-90 check-ins. | `ir.model.access.csv` (only `access_fix_talent_first90_role` on group_talent + mgr). | Add read/create for `group_hiring_manager` scoped by record rule to their requisition's plans. | `cd_talent/security/ir.model.access.csv`, `fix_a09_talent_rules.xml` |
| M58-F18 | P3 | B | Biodata hand-off nits: `marital_status == "separated"` maps to `single` on the employee (info lost); `religion == "undisclosed"` is dropped silently (fine) but `permanent_upazila` is concatenated into a free-text `permanent_address` (M21 has no structured permanent address) — Form 7 register quality depends on M21 fields. | `fix_candidate_biodata.py:577-580,571-575`. | Add the missing selection values on the M21 side or keep a note; M21 owns the address shape. | `cd_hr_core` (M21 side), `fix_candidate_biodata.py` |
| M58-F19 | P3 | G | Cron user timezone: the 4 M58 crons run as `base.user_root`, whose TZ on live is [probe1: see settings register]. `context_today` in the crons (offer expiry, erasure, task alerts, readiness) follows that TZ; if it is not Asia/Dhaka the "today" boundary shifts by hours against the business day. | `data/fix_talent_automation.xml` (user_root), probe1 `cron_users_tz`. | Set the cron users' TZ to Asia/Dhaka (estate-wide decision). | `cd_talent/data/fix_talent_automation.xml` or user record |
| M58-F20 | P3 | A | Age gate position: BRU-TAO-17 says minimum age is "verified before offer"; the code checks at offer ISSUE and at HIRE, but the candidate moves applied→screening→interview→"offered" stage un-checked (probe2 shows a 13-year-old reaching the offered stage; the block bites only when the offer is sent for approval). Also the offer-stage move has no interview-score bar for non-field roles (a "no" panel result blocks, but a mediocre "yes" panel with no assessment passes). | probe2 "13-year-old reached offer STAGE"; `fix_talent.py:806-830` (`action_offer` checks interviews/assessments only), `fix_talent_ops.py:708`. | Add `_fix_age_problems` to `action_offer` (cheap) — issue/hire gates already cover the money path. | `cd_talent/models/fix_talent.py` |

### Findings that closed (verified fixed at HEAD — not re-reported)
- Old M58-F1..F14 (3–6 Nov): hire needs requisition+offer+checks+interview+assessment+consent+age+duplicates — all enforced (probe2); requisition/offer/check approvals routed through M63 with requester≠approver≠subject (`fix.people.approval.mixin` + `_people_assert_not_conflicted`); offer band → CFO tier when out of band or no band; panel independence with private evaluations until full submission (record rules); onboarding completion reads evidence (NID check, acknowledged letter, verified pre-boarding docs, done mandatory tasks, bank/MFS, employee code, PPE for field roles); `employee.joined` held until onboarding completes; candidate NID cleared at hire and hashed with the M21 key; walk-in hire refused; direct `state` writes refused (ORM and /p03/model/write).
- A5 candidate-PII exposure: plain employees get AccessError on `fix.candidate` (no ACL row) and see no requisitions/plans (global scope rules) — probe3.
- Capture audit (17 Nov) + biodata standard (18 Nov): all 7 pages capture; 10-tab biodata form with 8 grids, SHA-256 evidence, verifier independence, data minimisation pre-offer, hire carry-over to M21 registers, pre-boarding prefill — present and guarded (static + live suites).

## 2. Spec-coverage matrix (M58 §5 FR-TAO-001…034)

| family | reqs | BUILT | PARTIAL | MISSING | notes |
|---|---|---|---|---|---|
| 5.1 Requisition & sourcing (FR-001…009) | 9 | 001,002*,003,004,005,008 | 006,007 | 009 | *002 budget gate OFF by default (F3-family setting); 006 internal-first window built, M57 internal candidates not; 007 referral captured+approved but unpaid (F11) |
| 5.2 Selection & assessment (FR-010…019) | 10 | 010,011,012,013,014,015,016,018 | 017,019 | — | 017 comparison not built; 019 outcome recorded but not communicated (F7) |
| 5.3 Offer & pre-boarding (FR-020…026) | 7 | 020,021,022,023,024,026 | 025 | — | 025 letter generated+acknowledged but plain text, no letterhead/e-sign (F8); 026 handover works but needs manual employee_code (F1) |
| 5.4 Onboarding (FR-027…034) | 8 | 027,028(as tasks),029,033,034 | 030,031,032 | — | 030 learning-path task exists but no M22 assignment link; 031 mentor field+check-ins; 032 first-90 recordable, no day-30/60/90 automation and no M57 feed (F10) |
| §6 T-01…T-10 | 10 | 01,02*,05,06,07,10 | 03,04,08,09 | — | T-03 erasure off (F3); T-04 residency not used for candidates (F4); T-08 hash+verifier yes, M24 storage no (F8); T-09 S3-grouped fields mostly, NID clear (F4) |
| §9 BRU-TAO-01…17 | 17 | 01*,02,03,04,05,06,07,08,09,10,11,12,13,17 | 14,16 | 15 | 14 automatic erasure off by default (F3); 16 outcome recorded, not communicated (F7); 15 "Bangladesh-resident store" not used for candidates (F4) |
| §11 AUT-TAO-01…17 | 17 | 01,04,05,06,07,08,09,10,11,12,13,16* | 02,17 | 14 | 16 fires only when retention set (F3); 02 internal window built, publication is manual; 14 no day-30/60/90 trigger; 17 approved but no payroll hand-off |
| §12.3 domain events | 10 | employee.joined | — | 9 | F6 |
| §14 reports | 13 | funnel, time-to-hire, cost/hire+source, offer acceptance (KPI), day-one readiness, onboarding completion (tasks screen), first-90, headcount vs budget (screen), referral (screen) | candidate retention compliance | early attrition, internal mobility | retention-compliance report absent (nothing to report while erasure off); early attrition needs M21 exit data |
| §15 KPIs 275–287 | 13 | 275,276,277(readiness),278(tasks),281,282,283,284*(recorded),287 | 279,280,286 | — | 279/286 unmeasurable until M22/M57 feeds and internal sourcing (F10/F14); 285 = 0 while erasure off |
| §13 roles | 11 | R30,R31,R06,R03,R48,R43,R44,R49(—) | R45 | R33,R40 | R45 recruiter blocked from offers (F2); R33 IT sees only own tasks ✓ but provisioning is a task not a command; R40 CDO: no consent/retention governance surface |

## 3. Settings register (live on fix_real_a09 — probe1)

| key | live | code default | effect of live value |
|---|---|---|---|
| `cd_talent.require_headcount_budget` | [probe1] | 0 | 0 = a requisition without any approved budget is ACCEPTED (BRU-TAO-01 half-off); an existing budget is always enforced |
| `cd_talent.candidate_retention_days` | [probe1] | 0 | 0 = retention clock never set, erasure cron idle (F3) |
| `cd_talent.minimum_hiring_age` | [probe1] | 14 | 14 matches BLA 2006 s.34(1) (child <14 prohibited); adolescents 14–18 lawful only with fitness certificate (s.37) — not checked by the code (ADVISER) |
| `cd_talent.readiness_lead_days` | [probe1] | 7 | day-one readiness escalation 7 days before start (spec AUT-TAO-11) |
| `cd_talent.internal_consideration_days` | [probe1] | 7 | external posting blocked until the internal window passes; 0 switches FR-TAO-006 off |
| `cd_talent.preboarding_documents` | [probe1] | nid,photo,academic,experience,bank | mandatory checklist issued at hire |
| `cd_hr_core.identity_hash_key` | [probe1] | minted at install | present = NID hashing active (shared with M21) |

## 4. Measured facts on fix_real_a09 (probe1)

- Role holders per group, M58 data counts, positions/bands coverage, cron state, identity state,
  onboarding template, outbox — filled from probe1_facts.log below.

## 5. Worked example — hire chain

The full synthetic worked example (budget → over-budget CFO routing → posting/internal window →
biodata gates → panel → checks → assessment → in-band vs out-of-band offers → accept → hire →
employee/contract/M22 baseline/letter/tasks/prefill → completion → `employee.joined` → reversal
probes → erasure/offer-expiry crons → referral → cost/KPI pack) is scripted, unexecuted, in
`C:\Users\DELL\AppData\Local\Temp\a09erp\R6\probe2_chain.py`; its output would land in
`probe2_chain.log` (not produced — run stopped by the lead).

## 6. Cross-area links

| link | state | which side is wrong |
|---|---|---|
| M58 → M21 employee+contract at hire | works (F1: code missing) | M58/M21 shared |
| M58 → M22 baseline at hire | works in-process (command, no event) | OK (spec allows command) |
| M58 → M29 `employee.joined` at onboarding completion | event published once; M29 provisions; payload carries branch_id/primary_role that the hire never sets (branch None unless M21 fills it) | M58 should set branch from requisition OU |
| M58 → M56 joiner proration | M56 prorates from contract joining_date (fix_payroll.py:666) | OK |
| M58 → M56 referral reward | no consumer | M56 side missing (F11) |
| M58 → M54 headcount budget | M54 has no headcount model; budget lives in M58; no `requisition.approved` event | M54 side absent (estate decision) |
| M58 → M24 documents | letter/ documents on `fix.hr.document` only; doc-suite print + esignature unused | M58 side (F8) |
| M58 → M27 notifications | none | M58 side (F7) |
| M58 → M57 first-90 → probation review | no feed | both sides (F10) |
| M58 → M60 `candidate.erased` | no event | M58 side (F6) |
| M58 → M30 branch/department/position | reads M21 position/dept; OU optional | OK |

## 7. Owner decisions (with R6 recommendation)

1. **Retention period** (F3): recommend 180 days (365 with talent-pool consent) and make 0 refuse new applications.
2. **Headcount budget required** (BRU-TAO-01): recommend switching `require_headcount_budget` to 1 once 2026/27 budgets are entered per department (probe1 shows how many exist).
3. **Onboarding owners + lead times** (F9): name IT/stores/facilities/HSE owners and negative offsets; keep decision from Update 4 open but unblock it.
4. **Minimum hiring age / adolescent hiring**: 14 is the statutory floor (BLA s.34(1)); if the company will not hire under-18s at all, set 18; otherwise add the s.37 fitness-certificate capture. ADVISER.
5. **Referral reward payment route** (F11): payroll earning vs M52 AP — recommend payroll one-off earning.
6. **Panel membership policy** (F12): exclude the hiring manager and the requisition approver from the panel? Recommend yes.
7. **First-90 owners** (F17): give hiring managers the first-90 surface.
8. **Reversal policy for a wrong hire** (F5): recommend a guarded cancel path.

## 8. Adviser questions

- Does the BLA (as amended 2013/2018) permit extending a skilled worker's 3-month probation by agreement to 6 (the code's label claims it, the cap forbids it)? s.4(8) caps clerical 6 / others 3.
- Adolescent (14–18) employment: does the company hire adolescents for any role, and if so who issues the s.37 fitness certificate? The code has no certificate capture.
- PDPA 2026 (Law 63 of 2026, passed 10 Apr 2026, repealing PDPO 2025): consent-based; no legitimate-interest basis (Securiti overview). Is "employment duties under law" the intended basis for the HIRED employee's data (so consent only governs candidates)? The code's data-minimisation comments still cite the 2025 Ordinance — cite PDPA 2026 when re-verifying religion/health sensitivity lists (the 2026 Act's sensitive list covers government IDs, biometrics, criminal records; religion/health sensitivity needs confirmation against the gazette text).

End of report — R6.
