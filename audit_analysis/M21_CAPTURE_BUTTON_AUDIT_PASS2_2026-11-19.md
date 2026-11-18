# M21 Core HR & Lifecycle: data-capture audit, second pass

**Date:** 19 Nov 2026 · **Branch:** `fix/m21-capture-pass2` (worktree `m21cap2-wt`, from `422b005b`) · **Spec:** `1000fix_ERP_Module/03_Modules/H_People_and_Workforce/M21_Core_HR_and_Employee_Lifecycle.md` · **First pass:** `M21_CAPTURE_BUTTON_AUDIT_2026-11-17.md`

## 1. The question

The user again saw M21 sub-module pages without a relevant data-capture button.

The first pass (17 Nov) gave every page a "+ New" and chips for every list on it. A count of chips is not the same as "relevant". This pass read each page against what a person decides there, per the spec:

- §5: the 46 features;
- §8: the lifecycles;
- §9: the rules;
- §10.1: the owned entities;
- §11: the automations.

For each, it asked whether that decision can be recorded.

## 2. What the spec says each page records

| Page | What a person records there | Spec | Priority / class |
|---|---|---|---|
| 2 Employment Contracts | The end-of-probation review, with evidence, that confirmation or extension rests on | FR-HCM-016, FR-HCM-029 ("with review evidence"), AUT-HCM-03, KPI-218 | P1 |
| 3 Org Structure | A second position held concurrently (dual role), an acting charge, a dotted-line manager | FR-HCM-024 ("matrix and dotted-line"), BRU-HCM-10 ("approved dual-role record"), T-06, entity `fix.employee.assignment` | P1 / **H** |
| 4 Lifecycle Events | Confirmation at the end of probation | FR-HCM-029, lifecycle §8.1 (probation review → confirmed / extended) | P1 |
| 7 ESS / MSS | The manager's side: review the team, start a movement (FR-HCM-041). The employee's side: update permitted personal data through a request (FR-HCM-040/042) | FR-HCM-040, 041, 042 | P1 |
| 8 Exit Process | The knowledge handover in the clearance | FR-HCM-036 ("assets, van stock, tools, IT access, dues and knowledge handover") | **P1** |

## 3. What the code had (HEAD `422b005b`)

The page contents below were evaluated the way the browser evaluates them: Node ran the engine's own `fregCreate` and `fregPanels` over the real registry fragments. The pass-1 guard (32/32) still passed.

| # | Page | Chips at HEAD | Defect |
|---|---|---|---|
| 2 | Employment Contracts | Employment Contract | **No probation review existed.** "Confirm Probation" and "Extend Probation" were bare list buttons. Nothing recorded why, or who assessed the worker. KPI-218 ("probation reviews completed on time") could not be measured. |
| 3 | Org Structure | Position, Department, Job Profile | **No dual role, acting charge or dotted line could be recorded.** An employee had exactly one `position_id` and one `parent_id`. The spec's assignment entity was never built, so BRU-HCM-10's "approved dual-role record" had nowhere to live. |
| 4 | Lifecycle Events | Transfer, Promotion, Master Change, Disciplinary | Confirmation (FR-HCM-029) had no capture, as on page 2. |
| 7 | ESS / MSS | Notice Ack, Rights Request, Master Change | **The manager's side captured nothing** (FR-HCM-041): no review, no movement. The employee's change request covered bank, MFS, NID, e-TIN and overtime only. **Address, personal contact, emergency contact and family details could not be requested at all.** |
| 8 | Exit Process | Exit Clearance, Exit Interview, Absence | **No knowledge handover.** The clearance had four ticks: IT, Finance, HR, Assets. A leaver's open jobs, customers, files and shared accounts were handed to nobody on record. |

Pages 1, 5 and 6 match the spec and are unchanged.

**fix_real (8069) at the time of the audit:** 504 employees. There were 0 contracts, 0 exits, 0 transfers and 0 master changes. The new gates therefore block no existing record.

## 4. What was built

### Workspace (`cd_p03_portal/static/src/a09/m21.js`)

| # | Page | Chips now (new in bold) | New lists |
|---|---|---|---|
| 2 | Employment Contracts | Employment Contract, **Probation Review** | Probation Reviews |
| 3 | Org Structure | Position, Department, Job Profile, **Additional Assignment** | Dual Roles & Acting Charges |
| 4 | Lifecycle Events | Transfer, Promotion, **Probation Review**, Master Change, Disciplinary | Probation Reviews |
| 7 | ESS / MSS | Notice Ack, Rights Request, Master Change (now with a **Contact & Family** tab), **Probation Review**, **Transfer** | Probation Reviews, Transfer / Promote |
| 8 | Exit Process | Exit Clearance, **Exit Handover**, Exit Interview, Absence | Knowledge Handovers |

- New KPI **Probation Unreviewed (30d)**: probations ending within 30 days with no submitted review. A caller who cannot read reviews does not see it.
- **Open Positions** and the **Establishment Register** count an approved dual role as a filled seat.

### Backend (`cd_hr_core` 19.0.0.6.0, `models/fix_hr_capture2.py`, imported last)

**`fix.hr.probation.review` (FR-HCM-016/029)**

- The reviewer picks the employee. Only employees on an active probation are offered. The server resolves the probation contract, because a line manager holds no right on contracts (salary).
- It records four required ratings (attendance, quality, skill, conduct), plus customer handling, strengths, concerns, a recommendation (confirm, extend, do not confirm) and an evidence file.
- Who may write it: HR or the employee's line manager. Never the employee. The check runs before the record is stored.
- Submitting checks the statute. Extension is for a skilled worker only, once (BLA s.4(8)). An extension or a "do not confirm" must state its concerns.
- A submitted review is evidence. It cannot be edited or deleted.
- **HR's "Confirm Probation" and "Extend Probation" now require a submitted review that recommends that decision.** The deciding officer cannot be the reviewer. The contract records which review it was decided on.
- The statutory "deemed permanent" path (the cron, s.4(8)) is unchanged: no review is needed when nobody decided in time.

**`fix.hr.additional.assignment` (FR-HCM-024, BRU-HCM-10, T-06)**

- Three types: a dual role (a second position), an acting charge (with an end date), or a dotted-line manager.
- Only HR records one, and a different HR officer approves it. The approver can be neither the creator nor the subject.
- Terms are checked:
  - not the employee's own primary position;
  - not their solid-line manager;
  - not themselves;
  - same company;
  - no overlapping approved assignment of the same kind.
- **An approved, current dual role takes a sanctioned seat.** Approval is refused when the seat is full or the position is frozen. While the dual role runs, the employee seat check and the transfer seat check refuse to over-fill that position. Ending the assignment frees the seat.
- Once approved, the terms are fixed: end it and raise a new one.

**`fix.hr.exit.handover` (FR-HCM-036)**

- One per exit. It names the successor and lists:
  - open jobs, tickets and customer commitments (required);
  - customers and contacts;
  - files;
  - shared accounts to reset (never passwords);
  - van stock / spares return challan;
  - a signed handover note.
- It is written by the leaver, their line manager or HR, checked before it is stored.
- "Hand Over" locks the content.
- "Accept" is the successor's step. If the successor has no login, the leaver's line manager accepts instead. The leaver and whoever handed it over cannot accept.
- **HR's clearance tick now waits for an accepted handover.** The role and conflict checks still come first, as before.

**Employee master change (FR-HCM-040/042)**

- 14 proposed fields on the existing maker-checker request:
  - present address, thana and district;
  - personal phone and email;
  - primary emergency contact: name, relation, two phones and address;
  - marital status and spouse name;
  - the number of dependent children.
- The number of children is proposed with a tick box, so 0 is a real answer.
- They are applied through the same approval as bank and identity details, and frozen once submitted.

**Security**

- ACLs:
  - review and handover: `base.group_user` read/write/create, because a manager and a leaver write them, fenced by the code checks above; no delete;
  - assignment: HR only.
- Global privacy rules in `security/fix_a09_m21_capture2_rules.xml`:
  - a review is read by the employee, their manager, the reviewer and HR;
  - a handover is read by the leaver, the successor, the line manager and HR;
  - all three records carry company rules.
- The two self-service models were added to the A09 permission matrix's `SELF_SERVICE` list, each with its reason.
- The P03 surfaces declare server-side `pickers`:
  - employees on probation;
  - unfrozen positions;
  - live exits.
- The write whitelist `a09/writable.py` was regenerated from the forms.

## 5. Proof

| Check | Result |
|---|---|
| Guard `test_m21_capture_pass2.py`, engine-evaluated pages: each page offers the spec's capture, each new record is listed on its page, every form field exists on its model and no form omits a required no-default field, surfaces/pickers/ACL/rules declared | **6/6** |
| Pass-1 guard `test_m21_capture_buttons.py`, estate page standard, A03/A09 writable-matches-forms | all pass. Two pass-1 checks were updated: page 7 now also lists the Transfer list it captures, and the load-order check expects `fix_hr_capture2` last |
| Live `test_m21_capture_pass2_live.py`: non-admin HR officers, a line manager, a leaver, a successor and a bystander, through the P03 endpoints and the ORM | **20/20** |
| Regression: all of `cd_hr_core/tests` (299) | 5 failures, **all 5 also fail on untouched HEAD** on the same database: 2 leave-accrual, the Keycloak-confirm access test, the attrition note test, and the permission matrix (peers' `fix.hse.*` and `fix.onboarding.induction`, which remain listed) |
| Existing tests changed because their meaning changed | `test_a09_m21_controls.py` and `test_a09_m21_r2_controls.py`: the probation decision is now arranged with a submitted review, and `_cleared()` with an accepted handover |
| Mutation check (one control removed at a time) | see §5.1 |
| Private server (`fix_test_m21c2`, port 8131), headless walk of the 8 pages | each page shows the chips in §4. Every new chip opens its tabbed form (3, 2, 3 tabs). The three new lists open with no error. 0 page errors |
| UI save | a dotted-line Additional Assignment was saved from the Org Structure chip, through the real form and Save. The row is in the database (`ADA/…/dotted_line`, draft) |

### 5.1 Mutation check

Each mutant re-introduces one defect. Before each run the mutant's find-string was checked to match exactly once, and the file was restored byte for byte after it.

**21 of 21 mutants turn the tests red:**

- review gates: confirm without a review; the recommendation ignored; the reviewer decides; anyone writes a review; submit without ratings; a submitted review editable;
- handover gates: the HR tick without a handover; anyone accepts; anyone writes one;
- dual roles: a full seat ignored; not counted as filled; the creator approves; a frozen position accepted; overlaps allowed; the seat check ignores dual roles;
- the contact change: proposals never applied; 0 children never applied; a submitted change editable;
- the KPI counting reviewed probations, the register ignoring dual roles, and the picker offering every employee.

The first run left one survivor, "contact proposals never applied". The test applied only the children request and never checked that an address reached the employee. The test now approves the address and emergency-contact request and asserts each field on the employee. It goes red on that mutant.

## 6. Not built (owner decisions or other modules)

| Item | Why |
|---|---|
| **Delegation of authority by position** (FR-HCM-027) | Unchanged from pass 1. The estate's authority register is M30's DOFA ladder, consumed by M63. Whether authority also attaches to positions is the owner's decision. |
| **Rehire as a new employment period** (FR-HCM-009, P2) | Unchanged. A rehire is a new employee record today. |
| **Manager reminders 30 and 7 days before a probation ends** (AUT-HCM-03) | The existing cron warns HR 14 days before. Notifying the line manager is an automation, not a capture. The new KPI shows the unreviewed probations meanwhile. |
| **Contractual notice longer than statute** (FR-HCM-017) | Notice is computed from the BLA at exit (s.26/27). No contract states a longer notice today. |
| **Hard block before the privacy notice is acknowledged** (BRU-HCM-12) | Unchanged from pass 1. It is the owner's call. |

## 7. State

_Filled in at landing and deploy._
