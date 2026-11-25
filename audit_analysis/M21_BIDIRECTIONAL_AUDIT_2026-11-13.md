# M21 Core HR & Lifecycle: bidirectional audit (screen ⇄ backend)

**Date:** 13 Nov 2026 · **Estate:** fix_real on 8069 · **Scope:** every M21 sub-module page, list screen, data-capture form, report, KPI, workflow, approval route and cross-module hand-off (M02, M29, M55, M56).

## 1. Method

The audit ran in both directions.

- **Screen dump.** The M21 workspace fragment (`static/src/a09/m21.js`) was loaded in Node as a real module. It covers:
  - 5 navigation groups, 21 screens and 15 forms;
  - 8 report routes and 8 Function Register sub-modules;
  - every column, field, action and its state gate, status label, chip and preset.
- **Backend dump.** A read-only Odoo shell on fix_real covered the 15 M21 models. It recorded:
  - every field's type, required, read-only, stored, computed and groups flags, plus selection keys;
  - every `action_*` and cron method;
  - guarded fields, ACLs, record rules and crons;
  - who holds each M21 decision role.
- **Screen → backend.** Each column, form field, action, state gate, status label, report key, chip, Function Register mapping and write-whitelist entry resolves to something real.
- **Backend → screen.**
  - Every whitelisted action has a button.
  - Every model action is either on a screen or routed to the approval inbox.
  - Every required field can be captured.
- **Live probe on 8069.** Every list, form (new and existing record), report (with and without a period) and the KPI payload was called through `/p03/model/*` exactly as the screens call them. The 8 sub-module pages were opened in the browser.
- **Business logic.** Three reviewers read the transfer, exit/absence/disciplinary and contract/master-data backends against BLA 2006, the Labour Rules 2015 and ITA 2023. I re-checked **every finding against the code before fixing it**. One claim was wrong; see §3.
- **Proof.** One ORM test per defect, plus the existing A09 and estate suites, run on a private test database.

## 2. Live state on 8069 before the fixes

- **Endpoint level.**
  - The probe passed 37 of 37 surfaces with 0 errors and 0 dropped columns.
  - Existing records open in every form.
  - All 8 sub-module pages render, with their capture buttons.
- **Data on fix_real.**
  - 504 employees and 61 positions.
  - 0 contracts, transfers, exits, dependants, education or experience records; 1 document.
  - 4,673 identity-read log rows.
- **KPIs as served:**
  - headcount 504;
  - technicians 182 (a name match, see D-R4);
  - open positions 0;
  - probation ending 0;
  - service books 0.

The screens rendered. The defects below are in what they **capture, compute and decide**.

## 3. Discrepancies found and fixed

### Employee master

| # | What was wrong | Fix |
|---|---|---|
| F6 | The form posts `position_id` on every save. An unchanged position re-ran the BRU-HCM-10 seat check. Every position on fix_real has 1 sanctioned seat but up to 133 holders (imported by SQL), so **no employee of those positions could be saved**. | An unchanged position is not a new claim and is dropped from the write. A real new claim on a full seat is still refused. |
| F7 | Every save published `employee.moved`, so IT got a "Mover access review" for each edit. | The event is published only when a mover field actually changes. An applied movement publishes its own, richer event. |
| WLT | "Workplace Category" overrode hr's *computed* `work_location_type`. The form offered it, the server refused it as read-only, and nothing was ever stored. | New stored field `workplace_category`; hr's own field is left intact. |
| F4 | The maker-checker (FR-HCM-042) on bank, MFS, NID and e-TIN applied only under an active contract. An officer could overwrite the salary account of any of the 504 employees, and payroll would pay it once a contract started. | A **recorded** value changes only through an approved Employee Master Change, with or without a contract. A first capture is still typed on the form, which locks the field once it holds a value. |
| F2 | Form 6 printed the employee master's wage fields, which nothing maintained ("Basic Wage BDT 0.00" on a signed-off contract), and printed a blank nature as "permanent". | Contract activation keeps the master in step: wages, gross, employment nature, and the joining date if empty. Form 6 states the contract's own terms and refuses an employee with no contract. |
| F3 | Generating the unsigned Form 7 draft stamped `form7_endorsed_on` and cleared the BLR r.21 15-day overdue flag. | Generating no longer endorses. The book is endorsed when a second person verifies the signed scan. |
| F8 | One officer could upload a file onto a colleague's document and verify it. A new file kept the employee's old acknowledgement. A generated service-book entry could never take its signed scan (frozen), so it was a dead end. | The uploader is recorded and may not verify. A new file resets the acknowledgement. A generated entry accepts its signed scan once. |
| F5 | Two nominee records exist: the employee form and Dependants. The s.19 death split silently dropped the employee-form nominee as soon as any dependant nominee existed. | A death settlement is refused until the two agree (reconcile on Dependants & Nominees). |

### Contracts

| # | What was wrong | Fix |
|---|---|---|
| F10 | A contract version made before probation was confirmed copied the probation terms. On activation the cron deemed the worker permanent a second time. | The version inherits the confirmation. |
| F11 | The cron auto-activated a fixed-term version with no end date, so it never expired. Manual activation refuses this. | The cron skips it and raises an activity instead. |

### Transfer / promotion

| # | What was wrong | Fix |
|---|---|---|
| T1 | A gross-only raise reached the master's `wage` and an unchanged contract version, so **payroll kept paying the old figure**. | A pay change states its components. The gross must equal them, and an active contract is required. The master's gross is the new contract's gross. |
| T2 | The DOFA approval amount came from typed `current_gross`/`proposed_gross`. Typing equal figures routed a raise at amount 0. | The amount is read from the active contract (plus relocation money). |
| T3 | Transfer grant, luggage, travel and deputation money skipped Finance and the approval amount. | Finance clearance is required and the money counts towards the amount. Paying these grants is still not built (§5). |
| T4 | Recommend → technical evaluation → HR audit skipped the destination manager. Concur → HR audit skipped a required technical evaluation. | Technical evaluation follows concurrence. HR audit needs it for a technical promotion, a tier change or a named evaluator. |
| T5 | Apply moved the master at once, whatever the effective date, and a past date was accepted. | Apply is refused before the effective date, and a back-dated requisition is refused at recommendation. |
| T6 | The technical evaluator could be re-named after recommendation. The score could be edited after sign-off. The storekeeper could be re-named after their tick. | All three are frozen. |
| T7 | The "from" side (branch, position, manager, grade, tier, current pay) was typed, and it fed the `employee.moved` event and the M29 review. | Snapshot from the master and the contract at recommendation; read-only on the form. |
| T10 | Two open movements could both be applied. | One open movement per employee. |
| T11 | Approved → cancel → reset to draft reopened an approved movement. | Refused. |
| T12 | Routing treated a 0-seat position as unlimited, so the apply then failed after every approval. The position's branch was not checked. | 0 seats means full; the position must belong to the destination branch. |
| T14 | ESD, BGA and OEM accreditations were captured but never reached the master that M02 dispatch matches on. | They are part of the approved proposal and are applied. |
| T15 | Grade M2 mapped to band 6, so band 7 "Head of Dept" was unreachable. | M2 maps to band 7. |
| T17 | The subject or initiator could clear their own handover. | Refused. |

### Exit, absence and disciplinary

| # | What was wrong | Fix |
|---|---|---|
| E1 | **A dismissal could never be settled.** Payroll raised "no settlement rule", and the exit stuck in Cleared, so even the s.11 earned leave was never paid. | Settlement computes the earned leave. Whether any compensation is due on dismissal is left as a labour-counsel question, marked as such in the code. |
| E2 | Settling before the last working day terminated the contract, dropped the worker from the running payroll and revoked access at once. | Employment ends on the last working day (the daily cron), not at the approval. |
| E3 | Termination paid **120 days in lieu to every worker**. A temporary worker given his 30 days was paid 90 more, and the s.26(4) compensation went to temporary workers. | Notice follows the exit's statutory requirement (120 permanent / 30 temporary); s.26(4) applies to permanent workers only. |
| E4 | The resignation shortfall "Wages in Lieu of Notice" (s.27(3)) was never read. | A negative line recovers the days not served. |
| E5 | The BRU-EAM-09 asset gate (equipment, vehicle bookings, vehicles) checked state `draft`, but clearing happens in `notice`. **It never ran.** | Runs in `notice`. |
| E6 | A typed earlier charge date shortened the worker's s.24 seven days. Hearing and explanation dates were also back-datable. | The charge is dated the day it is served. Hearing and explanation dates are validated. |
| E7 | A contract-end exit could not be settled once the expiry cron had set the contract to `expired`. | Settlement reads any contract that ran. |
| E8 | A draft version closed by the settlement could become the "latest" contract, so the settled figure could never be paid. | The exit's pinned contract is the basic; a never-activated version is ignored. |
| E9/E10 | After a recalled decision, an absence case could not be re-requested from the screen. An explanation could not be typed while the decision was pending. | Gating and field lock corrected. |
| E12 | A dismissal decision changed nothing: the worker stayed on the books. | It opens the draft dismissal exit, linked to the case, for HR to confirm. |
| E14 | A hand-made "abandonment" exit could never be confirmed, yet it blocked the real s.27(3A) decision. | Refused unless opened by the case's decision. |
| E15 | A pending disciplinary decision could not be recalled from the screen. | Button and whitelist added. |
| E17 | The exit form hid the notice shortfall, payroll's settlement lines and who cleared each line. | Shown, read-only. |

### Screens, reports and KPIs

| # | What was wrong | Fix |
|---|---|---|
| S1 | "Appointment Letters" and "Service Books" each listed **every** document type. "+ New" from Service Books made an appointment letter. | Each list is filtered to its type. Service Books has its own form with a `service_book` preset. A third screen, "All Statutory Documents", lists everything. |
| S2 | Master Changes, Disciplinary and Absence Without Leave were on no sub-module page. | Lifecycle Events now carries Master Changes and Disciplinary; Exit Process carries Absence. |
| S3 | Transfer buttons offered Technical Evaluation from "recommended", and Reset/Cancel in states the method refuses. The pending/returned approval state was invisible. | Gates follow the methods; an approval-state column is added. |
| D-R1 | **Headcount & Movement** took *today's* headcount as the closing for any period. It counted every contract (drafts and versions) as a joiner and ignored transfers out, so the columns never reconciled. | Headcount at each date, joiners and leavers by date, transfers in and out. Each row satisfies closing = opening + joiners − leavers + in − out. |
| D-R2 | **Attrition** ignored the period the screen offers and divided by today's headcount, which leaves out the people who left. | The period is honoured; the rate is over the average headcount. |
| D-R3 | Headcount counted leavers: the exit records `left_date` and never archives the record. | Leavers are excluded from the KPIs and every report. |
| D-R4 | **Technicians** counted positions whose name contains "tech": 182 on fix_real. A Technology Head counted; a Service Engineer did not. | Employees holding Field Service / Technician, i.e. the M02 dispatch pool. |
| D-R5 | **Open Positions** = Σ sanctioned − employees with any position. On fix_real, over-filled positions cancelled the empty ones, so it showed 0. | Σ vacant seats per position. |
| D-R6 | The **Establishment Register** clipped vacancies at 0 and hid over-establishment. | New "Over Establishment" column, with a note. |
| D-R7 | **Probation Conversion** saw only contracts. The 205 employees marked "Probationary" on fix_real were invisible. | They are listed as "No probation contract on record". |

**Rejected after checking:** one reviewer said no existing employee record could open, because the workplace field would raise. On 8069 every employee form opened; the field simply never stored a value (WLT above).

## 4. Proof

See §7 for the test runs, the live verification and the deployment.

## 5. Not built: feature gaps, not discrepancies

- **Relocation money is never paid.** No module turns an approved transfer grant into a payment (M56 off-cycle). It is now cleared by Finance and approved, but payment is manual.
- **Suspension subsistence (s.24).** Payroll does not consume `employee.suspended`, so a suspended worker is paid in full.
- **Deputation reversion and transit leave.** Captured on the transfer; nothing acts on them.
- **Dependant nominee edits** need only HR Officer, with no maker-checker on a payee.
- **Second s.27(3A) notice.** The cron schedules a to-do; there is no served-proof field.

## 6. Owner decisions and data (fix_real)

| Item | Effect today | Needed |
|---|---|---|
| Positions: 61 rows, each with **1 sanctioned seat**, holding up to 133 employees. These are job titles imported as establishment seats. | Over establishment by 442 heads. Any transfer *into* such a position is refused (full). | The sanctioned establishment per position: the business's figure, not something to fabricate. |
| **0 employment contracts** (504 employees) | No payroll, Form 6, probation tracking or pay change; settlements are refused. | Contracts for each employee (joining date, basic and allowances): the payroll file the owner has kept pending. |
| **0 joining dates** | Movement and attrition cannot date anyone; the report says so. | Same source. |
| Legal Counsel, Executive, Finance, IT clearance, Assets clearance roles: **admin only** | Contract sign-off, movement and disciplinary decisions, settlement approval and exit clearance can be done only by the system administrator. | Name the holders (role grants are the owner's decision). |
| Dismissal compensation (s.23) | Not computed; earned leave only. | Labour counsel ruling. |
