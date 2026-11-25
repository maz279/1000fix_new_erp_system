# A09 People & Workforce — ERP audit: owner decisions (D1–D40), 23 Nov 2026

Scope: all seven A09 modules (M21 Core HR, M22 Learning & Certification, M55 Time & Attendance,
M56 Payroll & Statutory, M57 Performance & Incentives, M58 Talent Acquisition, M59 Health & Safety)
and their links to the other areas, audited against the code at `6f0d6a54` and against a copy of
production (`fix_real_a09`) taken on 22 Nov.

How it was done: nine read-only auditors (one per module, cross-area flows, workspace/security) with
rolled-back probes on the production copy; the lead walked all 80 registry screens in the in-app
browser on production and re-verified every high-severity claim with its own probes; statutory figures
were checked against primary texts where the auditors could read them (Labour Act and Rules) and
against professional summaries where they could not (the 2026 Amendment Act, income tax) — those are
marked for your adviser.

Result: **190 findings — P0 3 · P1 36 · P2 100 · P3 51.** One P1 was disproved by the lead
(a "colleague's payslip readable" claim was a test artefact — every real read path is refused) and
one P0 is a rollout item rather than a code bug (D2). The controls that were built in earlier rounds
held under attack: identity data (NID / TIN / passport) never leaks, state guards and maker-checker
refused every bypass tried, the payroll money path runs end to end and posts a balanced journal on
your real chart, and the workspace has no master-level security hole (194 models ACL-covered, 13
personas refused exactly as designed).

What the audit found, in one paragraph: **the people modules are structurally complete but not
ready to run, and a set of real defects sits behind them.** Nothing operational can start because
production holds 504 employees and no contracts, no bank or tax data and no certifications. Behind
that stand code defects in money (incentives never paid, a mid-month raise paid at one rate, holiday
work never paid, over-withheld tax), in law (statutory forms mislabelled, accident filings missing,
2026 figures not applied) and in flow (hire dead-ends, recruiter cannot see offers, leaver keeps
jobs). The fix program is running; the decisions below are the ones only you can take.

**Owner answers recorded 2026-11-23 (first round):**
- **Deploy:** approved — deploy to both servers once the module regression is green.
- **D10 (2026-Act figures):** hold until labour counsel confirms in writing; the switch
  `cd_hr_core.apply_labour_act_2026_figures` stays absent, so maternity 112 / festival 11 / 2-year
  death-benefit service remain in force, exactly as today.
- **D5 (provident fund):** decide later — ship "members only": no member register exists, so nobody is
  deducted (the 10%+10%-for-everyone default is removed).
- **D11 (income-tax table):** the enacted 2026-27 pack is approved only after the tax adviser signs it
  through the pack's own two-person flow; until then the current table stays in force.

**How to answer:** each item carries a recommendation. Reply "approve all as recommended" or list the
numbers you change. Anything you leave open keeps today's behaviour (stated under each item).

---

## 1. The decisions that block go-live — answer these first

**D1 — Load employment contracts and the statutory master data for the 504 employees.**
Measured on production: 0 employment contracts; 0 employees with a bank account or routing number;
0 with a TIN; joining date empty on all 504; sex, marital status and present address empty on all
504; NID present on 315 of 504. Consequence: payroll has nothing to compute, annual leave accrues
0 days for everyone, the maternity gate can never pass, gratuity and final settlement have nothing
to run on.
*Recommendation:* (a) HR issues a **contract take-on file** — one line per employee: employee code,
joining date, contract type, probation end, grade/band, basic and each allowance, gross — built from
the employee workbook already used for the November load; I build the loader through the normal
contract-creation path (versioned, marked "take-on", audit-trailed). (b) A short **HR data-capture
round** fills sex, marital status, father's/mother's name and present address (the Employee form
already has every field). (c) Bank/routing and TIN are collected from each employee before the
first payroll run — the preflight I am adding refuses a run that would pay nobody.
*If open:* nobody can be paid; do not schedule a first payroll run.

**D2 — Decide the identity / SSO cutover wave.**
194 of 504 employees have no login; 32 active users have no employee record; 0 employees carry a
Keycloak id; none of the 54 roles is mapped to access groups (by design — every role change opens a
human access review). The 504 "employee joined" events were deliberately suppressed by the November
load ("IdP provisioning deferred to user-rollout wave"), so automatic provisioning has never run.
*Recommendation:* (a) confirm which employees need a login at all (recommend: head office, branch
managers, back office — not every technician); (b) rule the role → access-group mapping for the
roles those employees hold; (c) then re-deliver the joiner events for that population. Leave
"access review on every move" as it is.
*If open:* accounts are created by hand; the one-hour leaver deprovisioning KPI cannot be measured.

**D3 — Appoint real holders for every A09 role, at least two per approval role.**
16 of the 32 A09 groups have exactly one holder — the administrator. Measured: Payroll Officer and
Payroll Manager have the same three holders, and one account holds prepare + approve + pay; the HR
Director group and the CFO group (the two incentive signatures) have the same holders, so no
incentive scheme can ever receive two lawful signatures; Attendance Lock Manager is admin-only;
one HR Manager is both HSE Officer and Statutory Notification Authority; the sensitive-data
clearance group and the Data Protection Officer have no holder at all; 235 of 504 employees have no
line manager recorded, so their leave and overtime requests route to nobody.
*Recommendation:* name people for — HR Officer, HR Manager, Payroll Officer (two people who are
**not** Payroll Manager), Payroll Manager, Payroll Disbursement Releaser (Finance), Attendance
Supervisor, Attendance Lock Manager, Training Manager and verifier, Recruiter, Offer Approver,
HSE Officer, Occupational Health, Statutory Notification Authority (a different person from the HSE
Officer), Incentive Officer, Incentive Approver, HR Director, CFO delegate, sensitive-data clearance,
Data Protection Officer; and record the line manager for every employee. Remove the administrator
account from day-to-day operational roles.
*If open:* the separation-of-duties rules are satisfiable only by the administrator; approvals stall.

**D4 — Rule financial authority for HR money (approval matrix / DOFA tiers).**
No approval-authority matrix row exists for any of the 18 HR decision domains and no HR money model
carries a delegation-of-authority tier: a payroll release, a bonus run, a WPPF allocation or a final
settlement is approved by the role group at **any amount**.
*Recommendation:* adopt tiers — payroll release up to ৳10 lakh: Payroll Manager; above: Payroll
Manager + CFO; off-cycle payment, festival bonus and WPPF up to ৳1 lakh: Payroll Manager; above:
CFO; final settlement up to ৳2 lakh: HR Manager + Payroll Manager; above: CFO; incentive run:
HR Director + CFO (both, at any amount); offer above band and raise above band: CFO. Amounts are
yours to change.
*If open:* every HR payment is single-tier.

**D5 — Decide the provident fund.**
The engine today deducts 10 % employee + 10 % employer provident fund from **every** employee
although no fund, trustee or member register exists (being changed to "members only").
*Recommendation:* if 1000 FiX has no registered provident fund, set the company rates to 0
explicitly and do not take on members. If a fund exists, give me the member list with rates and the
fund's registration details, and load it before the first run.
*If open:* no PF is deducted (safe default after the fix).

**D6 — Set up competency and certification data.**
Pass marks are 0 on all four competencies, so no assessment can pass and nothing can be certified;
there are 0 certifications, so no technician passes the dispatch gate, which fails closed — all
field dispatch would be blocked the moment it is enforced. `home_appliance` is still not a valid
device type and tablet / desktop / TV jobs have no gating competency; learning paths carry no
positions or requirements.
*Recommendation:* (a) pass mark 70 %, validity 12 months (24 for safety certificates); (b) one
gating competency per device type actually repaired; (c) take on the technicians' real brand
certificates from your records; (d) fill the learning paths with positions and requirements.
*If open:* the dispatch gate stays blocking; the workshop gate stays open (see D38).

**D7 — Complete the position register and operating units.**
37 of 61 positions hold more staff than their sanctioned headcount (so every promotion into them
is refused after full approval); titles are duplicated ("Assistant Manager" and "Asst. Manager",
"Customer Success Executive" with and without "(CSE)"); no position carries a grade, so salary
bands link to nothing; 394 of 504 employees sit on "Main Operating Unit".
*Recommendation:* HR cleans the register — merge the duplicate titles, set sanctioned headcount
from the establishment, grade each position to one of the four bands (L2–L5); branch operating
units follow the rule agreed with the Assets area (an OU of its own once a Branch Manager is named).

**D8 — Confirm the holiday calendar.**
12 holidays are loaded, all for 2026; none is typed as a statutory festival day (so the 13-day
entitlement cannot be counted); only one of the four moon-dependent days is marked tentative; there
is no 2027 list.
*Recommendation:* HR confirms the list — the 13 festival holidays of the Labour Act plus the
national days — for the rest of 2026 and for 2027; I load them typed.

**D9 — Run the privacy-notice acknowledgement.**
All 504 employees show "Privacy Notice Pending". Under the Personal Data Protection Act 2026
(consent-based) the notice and consent must be in place before employee self-service opens.
*Recommendation:* acknowledge at first sign-in; hard-block self-service (not back-office work) for
employees who have not acknowledged.

---

## 2. Statutory figures — applied where the law is clear, to be confirmed by your advisers

**D10 — Labour (Amendment) Act 2026 figures (Act 43 of 2026, in force since 10 Apr 2026).**
The system still carries the pre-amendment figures. Being applied in code and by a safe upgrade
(only untouched defaults move; anything you changed by hand is left alone): maternity benefit
**120 days (60 before / 60 after)** — was 112; festival holidays **13 a year** — was 11;
death-benefit eligibility **1 year of service** — was 2; safety committees required in **every
establishment with 50 or more workers** — was factories only.
*Recommendation:* approve the application; have labour counsel confirm the gazette text (two
independent professional summaries agree; the gazette is in Bengali and was not read directly).

**D11 — Income-tax table for assessment year 2026-27.**
The engine's only tax table uses the pre-enactment draft thresholds (৳375,000 / 400,000 / 475,000 /
500,000), so it over-withholds from every employee. Enacted rates for 2026-27: nil up to
**৳400,000** (women and citizens 65+: 450,000; persons with a disability and third gender: 525,000;
gazetted freedom fighters: 550,000; a guardian of a disabled person: +50,000), then 10 % / 15 % /
20 % / 25 % / 30 %; minimum tax ৳5,000.
*Recommendation:* approve — the enacted tables for 2026-27, 2027-28/28-29 and 2029-30 are being
loaded as sourced, effective-dated statutory packs, and a run in a year with no approved pack will
be refused. Have your tax adviser confirm them from the Finance Act text.

**D12 — Investment rebate (tax adviser).**
The engine gives a rebate of the lower of 3 % of taxable income, 15 % of eligible investment or
৳10,00,000. One source reports the 2026 Act reduced this to 10 % and ৳7,50,000.
*Recommendation:* the rate and cap become selectable statutory-pack figures; adopt 10 % / 7,50,000
if your adviser confirms it. Until then the current figures apply.

**D13 — Separation benefits under the 2026 Act (labour adviser).**
The engine pays resignation compensation at 7 days' wages per year from the first day. Reports on
the 2026 Act describe a graduated benefit (7 days' wages a year up to 3 years, 15 days from 3 to 10,
30 days — or gratuity — from 10 years). The 30-days'-basic gratuity per year (45 days above 12
years, vesting after 5 years) matches the reports. Termination notice for monthly-rated permanent
staff stays at 120 days.
*Recommendation:* the bands become a statutory-pack option; pay resignation compensation only after
counsel confirms the substituted section. The "12 weeks' notice" figure one source mentions is
**not** supported — do not act on it.

**D14 — Overtime base (labour adviser).**
The engine pays overtime at twice **basic + dearness + ad-hoc** over 208 hours — the Act's wording.
Many practitioners read Labour Rules 2015 r.239(1) as basic **+ house rent + conveyance + medical**,
which for a work-force with house rent would mean materially higher overtime.
*Recommendation:* get a written ruling; until then keep the Act's base (current behaviour). The base
becomes a statutory-pack figure so the change is a setting, not a release.

**D15 — Pay for work on a weekly rest day or a festival holiday (labour adviser).**
Attendance records approved rest-day and holiday hours but payroll never paid them. Being fixed:
they are paid as overtime components. Open question: for a festival holiday the law is commonly
read as two days' substitute leave **plus** two days' additional basic wages.
*Recommendation:* festival holiday → substitute leave + 2× pay; weekly rest day → substitute day or
2× pay, employee's choice. Adviser to confirm.

**D16 — Festival bonus for an employee with less than one year's service (labour adviser).**
The engine skips employees with under one year entirely; a proportionate bonus is a common reading.
*Recommendation:* pay proportionate to days worked in the twelve months before the festival; the
rule becomes a statutory-pack option.

**D17 — Minimum wage and the wage-deduction cap (HR / labour adviser).**
No minimum-wage floor is set (the wage board for a service and repair business is not identified),
and recoveries from pay (equipment loss, overpayment) have no cap: the setting is 0, meaning the
whole balance can leave one month's pay.
*Recommendation:* set the floor at the lowest basic in your contracts until the wage board is
confirmed; cap all recoveries together at **20 % of net pay a month** and never below the floor;
confirm the 20 % with HR (the Assets area is waiting for the same figure for equipment recoveries).

**D18 — Final settlement clock.**
The law requires all dues within 30 working days of termination; nothing tracked it. Being fixed:
the due date is computed and shown, with overdue warnings. Nothing for you to decide — listed for
awareness.

---

## 3. Payroll policy

**D19 — Tax deduction method, bonus tax and the withholding return.**
Open settings: monthly-annualised or year-to-date tax; tax on the festival bonus (today none);
separate challan for salary tax; the screen says "Quarterly" returns while the code's due day is
the 25th of the following month.
*Recommendation:* year-to-date method; tax the bonus at the employee's marginal rate; one monthly
withholding statement and challan for salary tax; rename the screen to the frequency your adviser
confirms.

**D20 — Accounting configuration for payroll (Finance).**
Configured on the real chart: salary expense, employer PF expense, net salary payable, tax payable,
PF payable and the payroll journal. **Empty:** the originating BEFTN account and routing number
(so bonus, off-cycle and settlement payments cannot be released), gratuity expense and provision
(so the monthly gratuity provision never reaches the ledger), the three WPPF accounts, and the
recovery account.
*Recommendation:* Finance names these six accounts and the originating account; the payroll
preflight I am adding names each missing role before a run.

**D21 — Who posts payroll to the ledger.**
A real Payroll Manager could not post (the posting step needed accounting rights only the
administrator has), so runs were stranded after payment with no ledger line.
*Recommendation:* the Payroll Manager posts through the controlled posting funnel (being fixed);
Finance reconciles. Alternative: hand posting to Finance explicitly.

**D22 — Loans and advances.**
The module promises "Loans & Advances"; what exists is salary advances with a repayment schedule —
no loan, interest or statement model.
*Recommendation:* re-label the sub-register "Salary Advances" now and treat staff loans as a later
project.

**D23 — Parallel-run settings.**
All still off: variance threshold 0 %, bank-change cool-off 0 days, recovery source "payroll only".
*Recommendation:* before the first parallel run set variance threshold 5 % and bank-change cool-off
7 days.

---

## 4. Incentives and performance

**D24 — What the incentive scheme rewards, and when it is paid.**
Scheme v1 is still a draft with a band base of 0, so no run can compute. Score: 40 % first-time
fix, 25 % SLA, 20 % customer satisfaction, −15 % rework, 15 % salvage (which has no data source);
15 / 8 / 4 % of a band base. An incentive approved after its month's payroll was never paid (being
fixed: it is carried into the next payroll).
*Recommendation:* decide components, a volume gate, a cap and the band base in a scheme version 2;
pay the incentive with the **next** month's salary.

**D25 — Dispute and clawback windows.**
Both are 0: an employee cannot dispute an incentive line at all, and no clawback ever runs.
*Recommendation:* dispute window 5 working days, clawback window 30 days; an automatic clawback
appears on the run's approval statement and the employee is notified.

**D26 — Do an active performance-improvement plan or an open disciplinary case exclude an
employee from the incentive, a raise or a promotion?**
Today it does not.
*Recommendation:* yes, stated in the scheme version.

**D27 — Above-band exception.**
An offer above the salary band can be approved by the CFO (Tier 4), but a raise or promotion above
the band is refused outright.
*Recommendation:* allow it on the same CFO (Tier 4) approval (being built).
*Decision (owner, 2026-11-23):* **build it.** Done: `fix.band.exception` — the CFO tier approves,
from the M63 inbox, a named employee and grade up to a monthly gross; the band check honours it
(M57-F18 closed).

**D28 — Performance visibility.**
Payroll and HR generalists can read every rating, review and 360-degree feedback.
*Recommendation:* payroll sees published incentive amounts only; ratings and feedback are
HR-only (being built).
*Decision (owner, 2026-11-23):* **split now.** Done: payroll's groups read the incentive money
records (runs, lines, adjustments, clawbacks, disputes, recognition awards) and no longer the
scorecards, goals, reviews, PIPs or feedback (M57-F15 closed).

---

## 5. Recruitment and employee data

**D29 — Candidate data retention.**
The retention period is 0, so rejected candidates' data (including national ID in clear — being
moved to the protected store) is kept forever.
*Recommendation:* 180 days after the decision, 365 days for candidates who consent to stay in the
talent pool. Until a period is set the system will refuse to capture a candidate's national ID.
*Decision (owner, 2026-11-23):* **180 days / 365 with talent-pool consent.** Set as
`cd_talent.candidate_retention_days = 180` and `cd_talent.talent_pool_retention_days = 365`, with
the 19.0.0.7.0 migration moving the old 0 (M58-F3 closed). Also decided the same day:
`cd_talent.offer_validity_days = 14` — a new offer's default acceptance window (M58-F15).

**D30 — Minimum hiring age.**
14 — the legal floor for light work. Technician work involves electrical repair.
*Recommendation:* 18 for technician, workshop and field roles; 16 for others only with the
adolescent fitness certificate.

**D31 — Headcount budget before a requisition.**
The gate is off: a requisition without any approved budget is accepted.
*Recommendation:* switch it on once departmental budgets are entered.

**D32 — Onboarding and panels.**
Onboarding tasks have no owners or lead times (everything is due on the join date); the hiring
manager may sit on the interview panel for their own requisition.
*Recommendation:* IT access due 7 days before joining, equipment 3 days before, ID card 2 days
before, safety briefing on day one, owners named per task; the hiring manager and the approver
never sit on the panel (being enforced); allow a wrong hire to be cancelled before completion.

**D33 — Referral reward.**
An approved referral reward is never paid — payroll has no path for it.
*Recommendation:* pay it as a one-off payroll earning after the new hire completes probation.

**D34 — Statutory documents in Bengali, as letterheaded PDFs.**
Form 6(A) issue register, Form 7 service book, Form 8 register of workers, appointment letter, ID
card and service certificate are generated today as plain English text. Their labels and content are
being corrected; rendering them as bilingual letterheaded PDFs is a separate document-suite task.
*Recommendation:* build them in the same document suite as the customer documents.

---

## 6. Working time

**D35 — Working-time rules.**
Live rule: 60 hours a week as a label only; rest interval, spread-over and the 56-hour average are
all switched off; overtime is capped at 2 hours a day and 10 hours on a rest day.
*Recommendation:* a new rule version from 1 January 2027 — 48 hours a week standard, 60 including
overtime (so at most 12 payable overtime hours a week), 30 minutes' rest after 5 hours, 12-hour
spread-over, 56-hour average — all as warnings for the first quarter, then blocking.

**D36 — Unpaid leave and missing leave types.**
Approved unpaid leave had no effect on pay (being fixed); there is no unpaid, bereavement,
compensatory or special leave type.
*Recommendation:* add Leave Without Pay, Bereavement (3 days), Compensatory (earned on holiday
work) and Special (2 days); unpaid days are deducted in the month they fall.

**D37 — Attendance administration.**
Roster notice period 0 days, "dispatch only published rosters" off, team-coverage threshold 0 %.
*Recommendation:* notice 7 days, published-only on once rosters exist, coverage warning at 30 %.

---

## 7. Safety

**D38 — Safety committees and fire drills.**
Under the 2026 Act every establishment with 50 or more workers must have a safety committee (6–12
members, equal employer and worker representation, a chairperson and a co-chairperson, a two-year
term, meetings at least every three months) and a fire drill every six months. None is recorded.
*Recommendation:* identify which of your sites employ 50 or more people (head office at least),
name the members, and constitute the committees; schedule the drills per branch.

**D39 — Injury compensation.**
Compensation is an approved figure with no statutory floor. Being added: the statutory minimum
computed per the Labour Act — death ৳2,00,000, permanent total disablement ৳2,50,000, permanent
partial disablement as a scheduled percentage of that, temporary disablement as wage continuation —
and an award below the floor needs a recorded reason.
*Recommendation:* approve the statutory floors as defaults; your medical assessor records the
percentage of loss of earning capacity per case.

**D40 — Workshop certification gate.**
The field-service dispatch gate fails closed (no certificate, no job); the workshop gate was left
open on purpose pending your decision. A laptop-only technician is today eligible for an
appliance repair bench job.
*Recommendation:* enforce it closed from the date the competency data (D6) is loaded.

---

## 8. Estate items outside A09 (not code defects of the people modules — for the named owners)

| Item | Owner area | What is wrong |
|---|---|---|
| Outbox never drained to the message bus | Platform (A12) | 18,587 events sit "pending", nothing in the repository publishes them; no in-Odoo consumer is affected |
| Availability feed to dispatch | Service Operations (A02) | no `availability.changed` event, no availability projection; the two dispatch paths apply the shift window differently |
| Leaver hand-off to operations | A02 / A06 / A07 | nothing reassigns or blocks a leaver's open jobs, stock custody or van; the exit-clearance gate is being added on the HR side |
| Navigation registry | Platform | the generated registry is behind the fragments (108 screens, 8 titles) — regenerate it |
| Bengali labels on forms | Workspace engine | 2,073 of 2,224 A09 field labels show English in the Bengali UI although the translations exist |
| People notifications | Contact Centre (M27) | roster notices, candidate replies and safety alerts are internal activities only — no SMS / e-mail |
| Training cost, referral reward, incentive accrual | Finance (A08) | no hand-off to payables, budget or ledger; contracts are described in the evidence files |

---

## 9. Adviser questions (cannot be answered from the code or public summaries)

1. Labour counsel — gazette text of Act 43 of 2026 for maternity (120 days), festival holidays (13),
   death benefit (1 year), resignation-compensation bands, termination notice.
2. Labour counsel — whether Labour Rules rr.69–85 and Forms 23/27/28/29 were re-issued after the
   2026 Act.
3. Tax adviser — AY 2026-27 thresholds (D11), the investment rebate (D12), the salary withholding
   statement frequency, the salary-certificate section.
4. Labour adviser — overtime base (D14), holiday-work pay (D15), proportionate festival bonus (D16).
5. Whether the repair and service sector is gazetted under the new employment-injury scheme fund.
6. Which wage board covers an after-sales service company (D17).

---

## 10. Being fixed in code without a decision

*(filled in when the builder streams report — see the audit report `A09_ERP_AUDIT_REPORT_2026-11-23.md`)*
