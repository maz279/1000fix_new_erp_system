# M21 Core HR & Lifecycle: sub-module capture audit

**Date:** 17 Nov 2026 · **Base:** `42d00bb2` · **Branch:** `fix/m21-capture-buttons` · **Spec:** `1000fix_ERP_Module/03_Modules/H_People_and_Workforce/M21_Core_HR_and_Employee_Lifecycle.md`

The user saw M21 sub-module pages without a relevant data-capture button. This audit checked what each page should capture against the spec, what the code offers, and the data on fix_real.

## 1. Method

1. **Spec.** Each of the 8 Function Register sub-modules was mapped to its FR-HCM requirements (§5), entities (§10), rules (§9), automations (§11) and reports (§14).
2. **Code, as the browser evaluates it.** Node ran the workspace engine's own `fregCreate` and `fregPanels` over the real registry fragments. This gave each page's "+ New", its form chips and the lists it shows.
3. **Data on fix_real (8069).** Read-only counts of the M21 records.
4. **Build and proof.** The fixes were built in a worktree and tested on a private database (`fix_test_m21c`), with:
   - a static guard test;
   - a live ORM test run as non-admin HR users;
   - an endpoint probe of every M21 list, form and report;
   - a click-through of all 8 pages in the browser.

## 2. What the pages offered at HEAD

| # | Page | "+ New" | Chips | Lists on the page with no capture | Spec records with no capture anywhere |
|---|---|---|---|---|---|
| 1 | Employee Master | Employee | Employee | Academic Qualifications, Work Experience | — |
| 2 | Employment Contracts | Contract | none | — | — |
| 3 | Org Structure | Position | none | — | **Departments** (FR-HCM-020), **job profiles** (FR-HCM-022); a position had no job, department or frozen status (FR-HCM-023) |
| 4 | Lifecycle Events | Transfer | Transfer, Promotion | Master Changes, Disciplinary | — |
| 5 | Statutory Documents | Document | none | Service Books (form existed, no chip) | — |
| 6 | Dependants & Nominees | Dependant | none | — | — |
| 7 | **ESS / MSS** | **none** | **none** | — | **Employment privacy-notice acknowledgement** (FR-HCM-044 **P0**, BRU-HCM-12 **H**, AUT-HCM-02); employee rights requests (FR-HCM-045 **P0**) were on no page |
| 8 | Exit Process | Exit | Exit Clearance | Absence Without Leave | **Exit interview** (FR-HCM-038): the reason for leaving was free text |

Two further defects:

- **The Promotion chip opened the dossier with "Transfer" selected.** Saving it unchanged recorded a transfer.
- **Page 7 listed employees and captured nothing.** The page carried the probation report and an employee grid with `create: false`.

**fix_real (8069) at the time of the audit:**

- 504 employees, all with a department and a job.
- 23 departments and 61 job profiles exist, but **no M21 screen listed or captured them**. They could only be made in Odoo's back office.
- 2 transparency notices and 0 rights requests.
- No privacy-notice acknowledgement is possible: no record for one exists.

The guard test written for this audit fails **18 of 32** checks on HEAD.

## 3. What was built

### Workspace (`cd_p03_portal/static/src/a09/m21.js`)

| # | Page | "+ New" | Chips now |
|---|---|---|---|
| 1 | Employee Master | Employee | Employee, Education, Experience |
| 2 | Employment Contracts | Contract | Employment Contract |
| 3 | Org Structure | Position | Organisation Position, **Department**, **Job Profile** (new lists: Departments, Job Profiles) |
| 4 | Lifecycle Events | Transfer | Transfer, **Promotion (preset to Promotion)**, Master Change Request, Disciplinary Case |
| 5 | Statutory Documents | Document | Statutory Document, Service Book Entry |
| 6 | Dependants & Nominees | Dependant | Dependant / Nominee |
| 7 | ESS / MSS | **Privacy Notice Acknowledgement** | Privacy Notice Acknowledgement, **Rights Request**, Master Change Request (new lists: Privacy Notice Acknowledgements, Employee Rights Requests) |
| 8 | Exit Process | Exit | Exit Clearance, **Exit Interview**, Absence Without Leave (new list: Exit Interviews) |

Every list on every page now has its capture. The module's form chips grew from 4 to 19. Each chip sits on a page and opens a form.

### Backend (`cd_hr_core` 19.0.0.5.0, `models/fix_hr_capture.py`, imported last)

- **Job architecture (FR-HCM-022).** `hr.job` gains:
  - a job code, unique per company;
  - a Bengali title;
  - a job family and a band.
- **Departments (FR-HCM-020).** `hr.department` gains a department code (unique per company) and a Bengali name.
- **Positions (FR-HCM-023).** `fix.org.position` gains a job profile, a department and a **frozen** flag. A frozen position's empty seats are not vacancies:
  - the Open Positions KPI skips them;
  - the Establishment Register shows them in a new "Frozen Seats" column.
- **`fix.hr.notice.ack` (FR-HCM-044, BRU-HCM-12).** Records which published notice version an employee acknowledged, when and how.
  - A retired notice is refused.
  - A signed paper copy must be attached.
  - Only one live acknowledgement per employee and version is allowed.
  - Once recorded it is evidence: it cannot be edited or deleted.
  - Withdrawing consent-based processing is an HR action that states what was withdrawn, with the date and who recorded it stamped.
  - Access is HR Officer only; the Data Protection Officer can read.
  - New KPI **Privacy Notice Pending**: employees on the books with no live acknowledgement. A caller who cannot read acknowledgements does not see it.
- **`fix.hr.exit.interview` (FR-HCM-038).** One interview per exit, with the main and second reason for leaving and five 1–5 ratings.
  - The leaver cannot interview themselves.
  - A cancelled exit cannot be interviewed.
  - "Record" locks the answers.
  - Access is HR only. The **Attrition Analysis** now states the main reasons for leaving from recorded interviews, for HR callers only.
- **Employee rights requests** reuse M33's `fix.rights.request`: an employee is a party through their work contact. The new M21 list shows only employees' requests. Verification and fulfilment stay with the Data Protection Officer in M33.
- **Security.**
  - ACL rows for both new models, with no row for all internal users.
  - Company isolation rules in `security/fix_a09_m21_capture_rules.xml`.
  - The write whitelist (`controllers/a09/writable.py`) was regenerated from the forms. The a03 whitelist, which covers M33's rights request, is unchanged.

## 4. Proof

| Check | Result |
|---|---|
| Guard `test_m21_capture_buttons.py` (engine-evaluated pages, whitelists, ACL, load order) | **32/32** on the branch; **18/32 fail on HEAD** |
| Live `test_m21_capture_live.py` (non-admin HR officers, P03 endpoints, rollback) | **9/9** |
| Estate page standard, A09 write whitelist, M21 report labels | all pass |
| Endpoint probe from the page on the private server | 30 lists and reports, 0 errors; 20 forms, 0 errors |
| Browser click-through of the 8 pages | each shows the "+ New" and chips in §3 |
| UI save | Department "UIW Warranty Desk" saved from the Org Structure chip; the row is in the database with its Bengali name and code |
| Promotion chip | opens with Movement Type = Promotion |
| Mutation check (one control removed at a time) | 10/11 turn the live tests red; the survivor (deleting an acknowledgement) is also refused by the ACL, so it is equivalent |
| Regression (all A09 domain tests + the portal test folder) | 13 failures, **all identical on untouched HEAD** (event relay and access-review tests, M22 work-order flags, M30 Branch Master and M50 statement-line page checks); none names an M21 page |

The live tests found three things the static checks could not:

- **Department ordering.** `hr.department.complete_name` is not stored in Odoo 19, so it cannot order a search. The Departments list failed until it was ordered by name.
- **Constraint savepoints.** A constraint refusal happens after the INSERT, so tests must wrap each expected refusal in a savepoint.
- **Exit cancellation.** The existing segregation-of-duties control stops an exit's creator from cancelling it.

## 5. Not built (gaps for the owner)

| Item | Why it is not built here |
|---|---|
| **Delegation of authority by position** (FR-HCM-027) | The estate's single authority register is M30's DOFA ladder: value bands per document type, ruled by the CFO and board. A second, per-position register would split it. Whether authority should attach to positions is an owner decision. |
| **Rehire as a new employment period** (FR-HCM-009, P2) | No employment-period record exists. A rehire is a new employee record today. |
| **Hard block before the notice is acknowledged** (BRU-HCM-12 "before data is processed") | 504 employees on fix_real hold no acknowledgement. Blocking processing now would stop payroll and HR work. The KPI measures the gap instead; the owner decides when to enforce. |
| **An employment privacy-notice version** | fix_real's two notices are M33's customer notices. The DPO must publish the employment notice (Bengali and English) before HR can record acknowledgements. |
| **Leave Type** ("Record Coverage" group) | It is M55's record (spec §3.2). It stays where it is; the M55 audit owns its placement. |

## 6. Deployment

Not deployed. Deploying needs:

1. `-u cd_hr_core,cd_p03_portal` on fix_real.
2. One restart of 8069, because new controller surfaces only load at process start.

Both wait for the user's go-ahead and coordination with the peer sessions deploying on 8069.
