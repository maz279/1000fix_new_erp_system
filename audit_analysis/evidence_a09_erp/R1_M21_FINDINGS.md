# A09 ERP audit — R1 / M21 Core HR & Employee Lifecycle — FINDINGS

Auditor R1 · 2026-11-22 · code `a09erp-wt\1000_fix_codebase` (shared HEAD)
Scope: `cd_hr_core` (all 21 model files, security/, data/, views/), platform `cd_employee_core`,
P03 `controllers/a09/m21.py` + `static/src/a09/m21.js` + `a09/writable.py`, `fix.guarded.mixin`
(cd_entity_config), `cd_workflow_engine` approval spine, `cd_rbac_ext` SoD gate on hr.employee role
writes, `libs/py/fix_residency`; leave models (M55 spec leave sections). Specs read in full.

Evidence in this folder: `probe_real_readiness.out.txt` (SQL, fix_real_a09, read-only),
`probe_identity_guards.out.log` (ORM probe, fix_test_a09_r1, rolled back: 28 PASS / 1 expected-fail
confirming F9), `probe_real.sql`, `probe_identity_guards.py`. Test baseline: **run by the lead**
(this auditor's background run was stopped to relieve the shared machine; pass/fail counts
NOT CHECKED by R1 — the module's own suites exist: 278 test functions across the in-scope files).

---

## 1. Findings table

Severity: P0 money/legal/security broken · P1 core flow broken or bypassable · P2 rule/calc/report wrong · P3 polish.

| id | sev | cat | finding | evidence | proposed fix | files |
|---|---|---|---|---|---|---|
| M21-F26 | P1 | L | **fix_real_a09 holds 0 employment contracts** (table empty): all 504 loaded employees are "on the books" with no contract. Payroll (M56) pays from the contract, Form 6 refuses to generate, the under-contract master gate never engages, probation/expiry/exit crons have nothing to do. | SQL: `fix_employment_contract` state counts = 0 rows; 504 active employees without an active contract | Backfill contracts for the 504 (Hire/Onboard per employee, legal sign-off + activation) before any payroll run; the data-cleanup screen should list "employee without any contract" | migration + `fix_hr_cleanup_report.py` |
| M21-F27 | P1 | L | Statutory master coverage gaps on the 504: TIN held 0/504, passport 0, NID 315/504 (189 missing), sex 0/504, marital 0/504, present-address street/city 0/504, children 0. The maternity gender gate can never pass (sex unrecorded); Form 7/6(a) content and M56 tax profile are empty for everyone. | SQL probe §4; `fix_leave_controls.py:364-371` (sex gate) | Wave-4 enrichment of the 504 (the migration's known honest 'unrecorded'); add a data-completeness weekly report (spec §14 lists it; not built) | data migration + new report pack |
| M21-F28 | P1 | L | 37 of 61 positions hold more employees than their sanctioned headcount on fix_real_a09. The BRU-HCM-10 constraint blocks new writes but the loaded over-establishment persists, so any transfer/apply targeting those positions fails after full approval (the apply-time seat check refuses). | SQL: over-establishment positions = 37; `fix_hr_movement_controls.py:640-660` (`_fix_check_seat`) | Owner decision on the real establishment (raise headcount or reassign); until then the cleanup report should list every over-seat position | `fix_hr_cleanup_report.py` + company data |
| M21-F29 | P1 | D/L | Every M21 decision group except HR Officer/Manager holds exactly 1 user (admin): legal counsel, HR executive, HR finance, clearance-IT, clearance-assets (party DPO: 0). All routed M63 decisions (contract sign-off, executive movement/disciplinary/abandonment, settlement approval, IT/assets clearance) resolve to the administrator in practice; SoD "requester≠approver≠subject" is satisfiable only by admin-vs-officer pairs. No `fix.approval.matrix` row exists for any of the 18 HR decision domains (live matrix holds only discount/write_off/estimate/credit_note/expense/requisition). | SQL: group holders (§4); `fix_a09_m21_groups.xml` seeds root+admin only | Appoint real holders (report §7.1 item 1, still open); optionally seed matrix rows for the hr_* domains | business + `cd_hr_core/data` |
| M21-F1 | P2 | B/J | "Form 6(a) Worker Register" mislabels the statutory artefact: BLR 2015 r.23 prescribes the workers' register in **Form-8**; **Form 6(a)** (r.19(7)) is the 10-column register of when the appointment letter/ID card/service book were issued (no NID column). The code cites r.20 (service book = Form 7) for the register and adds a clear-NID column no prescribed form carries. | `fix_hr_core.py:905-930`, `m21.py:602-638`; gazette SRO 291-Law/2015 (BILS English) rules 19(7)/20/23 + Forms schedule, fetched 2026-11-22 | Rename/cite correctly; generate the real Form 6(a) issue register from `fix.hr.document`; move NID to Form 7/8 where lawful (owner decision) | `fix_hr_core.py`, `m21.py`, `m21.js` |
| M21-F2 | P2 | B/J | "Form 6 Appointment Letter" mislabeled: r.19(4)'s letter is unnumbered and must carry 10 named particulars (incl. spouse, worker class, wage scale + increment rate, other financial facilities, compliance statement) — the generator omits 5 of them; **Form-6 is the identity card** (r.19(5)) and `doc_type id_card` is wrongly labelled "Form 11" (Form 11 = discharge inability certificate, r.28). | `fix_hr_core.py:834-903`; `fix_hr_ops.py:648-651`; gazette | Fix labels; extend the letter payload to the r.19(4) list | `fix_hr_core.py`, `fix_hr_ops.py` |
| M21-F4 | P2 | A/K | FR-HCM-013/T-08 bilingual statutory documents unmet: Form 6/7/ID-card/s.31 generators emit English-only ASCII text (only `name_bn` appears inside s.31/ID card). BLR r.23(2) requires the workers' register in Bengali. | `fix_hr_core.py:789-903`, `fix_hr_exit_lifecycles.py:544-572`, `fix_hr_master_controls.py:329-358` [STATIC] | QWeb PDF templates, bn_BD bodies, letterhead | `cd_hr_core` report templates |
| M21-F5 | P2 | J | Maternity seeded at 112 days (8+8 weeks); the 2025-26 amendment raises s.46-47 to **120 days (60/60)** on a gross-wage basis (secondary sources; gazette not in repo). Half-split check reads `entitlement_days`, so a type edit propagates, but seed+floor stay 112. | `fix_hr_core.py:13-20`; `statutory_leave_data.xml`; Legal500/lexplosion 2025-26 alerts | Counsel-confirm, then seed 120 (and 60/60 split) | `statutory_leave_data.xml`, `fix_hr_core.py` |
| M21-F6 | P2 | E/J | `excludes_holidays=True` on casual/sick contradicts BLR r.106 ("if the weekly or festival leave falls into the Casual or Sick leave, the leave shall be included in the original leave"): with the M55 `_compute_days` override, registered festival days inside casual/sick leave are not charged. Live seed confirms t for casual/sick. | `fix_leave_controls.py:93-98`; `cd_attendance/models/fix_attendance_approval.py:536-557`; gazette r.106; SQL leave-type dump | Seed excludes_holidays=False for casual/sick (counsel note for annual) | `statutory_leave_data.xml` |
| M21-F7 | P2 | G | No producer of the M29 identity-lifecycle events: `consume_identity_lifecycle_event` + 5-min drain expect `identity.provisioned/deprovisioned/deprovision_failed`, but nothing in-tree publishes them (only a test string). The "idp" confirmation path can never fire; KPI-090/214 (24-h revocation) depends entirely on the HR manager's manual confirmation. | `fix_hr_core.py:1027-1139`; `data/identity_lifecycle_cron.xml`; grep (no publisher) | M29 identity-lifecycle service or outbox→Keycloak bridge; mark the KPI "manual-only" meanwhile | M29 addon (owner) |
| M21-F9 | P2 | I | `hr.employee.keycloak_id` is a second, unguarded Keycloak field: the guard covers `keycloak_user_id` (the one M29 uses) but the P03 employee form offers `keycloak_id` and nothing consumes it — an HR user can write a forged UUID the trail then shows as the IdP id (probe wrote `'forged-uuid'` successfully). | probe (expected-fail case); `fix_hr_core.py:231` vs `_fix_guarded_fields` :941-953; `a09/writable.py:1722`; `m21.js:374` | Remove the field (or relate it) and drop from whitelist+form | `fix_hr_core.py`, `a09/writable.py`, `m21.js` |
| M21-F13 | P2 | C | "Suspended" (FR-HCM-008, spec §8.1) exists only on the disciplinary case; `employment_status` has no suspended value, so M55/M02 consumers cannot see a running s.24 suspension from the employee. | `hr_employee_ext.py:81-96,197-210`; `fix_hr_disciplinary.py:124-129` [STATIC] | Derive suspended like notice_period (`fix_hr_master_controls.py:134-147`) | `cd_employee_core/models/hr_employee_ext.py` |
| M21-F15 | P2 | A/J | 10-year retention/disposal (BRU-HCM-11, T-09, AUT-HCM-13) unimplemented: no retention field, legal-hold flag or disposal cron for employee records. | grep (none in cd_hr_core) [STATIC] | retention_until + legal hold + cron (M24 hand-off) | `cd_hr_core/models`, data |
| M21-F20 | P2 | D | Historic "off/0" settings still off on all 3 companies: `fix_hr_suspension_subsistence_pct=0` **blocks every s.24 suspension**; leave coverage 0/flag (BRU-WFM-04 off); resignation 60/30, abandonment 10/10/7, weekly cap 48, death-benefit 2y all at the 2013 values the 2025-26 amendment reportedly changed. | SQL settings dump; `fix_hr_disciplinary.py:415-420` | Owner+counsel rulings (see §6); no code change | company settings |
| M21-F22 | P2 | B | Form 7 clock drift: r.21(1) puts the opening entry one month after becoming permanent (r.22(1): book opened within 15 days of appointment/probation end); code uses `last_event or joining_date + 15d` for everyone, and the overdue flag only recomputes on save (no cron). | `fix_hr_core.py:771-787`; gazette r.21/22 | Base first-entry due on confirmation; daily overdue refresh | `fix_hr_core.py` |
| M21-F24 | P2 | E | Employer-termination notice hard-coded 120/30 days (s.26 2013 text, benchmark "verified unchanged") while 2025-26 reporting says 12 weeks/pay-in-lieu and a new s.27(4) resignation compensation; citation rests on the benchmark alone. | `fix_hr_controls_common.py:24-28`; Legal500 alert | ADVISER: confirm gazette before first live termination; make it a setting if changed | `fix_hr_controls_common.py` |
| M21-F25 | P2 | D | s.31 service certificate: BLR r.31 requires issue within 15 days of the worker's **application**; the model auto-issues on a cleared/settled exit, tracks no application, and refuses re-issue ("already has service certificate") — a later statutory application cannot be served. | `fix_hr_exit_lifecycles.py:527-541`; gazette r.31 | Add `applied_on`; allow re-issue on application | `fix_hr_exit_lifecycles.py` |
| M21-F30 | P2 | B | ESS own-record view missing (FR-HCM-040/041/043): the M21-ess screen is only the probation-conversion report; no surface shows the employee their contract, payslips, leave balance or service record (record rules already permit own reads). | `m21.js:201`; registry.json | Own-record ESS panel (contract + leave balance + documents) reading under own rules | `m21.js`, `m21.py` |
| M21-F31 | P2 | L | Cost-centre/job-architecture coverage zero: 0/23 departments carry `fix_cost_centre`, 0/61 jobs carry `fix_job_family` on fix_real_a09 — the payroll GL cost-centre dimension (`_fix_effective_cost_centre`) resolves for nobody; job-family reporting is empty. | SQL §4 | Populate department cost centres from finance's GL list; classify jobs | data + `fix_hr_cost_centre.py` |
| M21-F32 | P2 | L | `cd_party_master.group_party_dpo` has 0 holders on fix_real_a09: PDPA rights requests and notice oversight (R40 CDO role) have no owner; the privacy-notice KPI is withheld for everyone. | SQL §4 | Appoint the DPO | business |
| M21-F3 | P3 | I | `action_export_form6a_register` has no explicit group gate; the controller docstring's "a non-HR caller is refused" holds only via hr.employee record rules (probe: plain user got AccessError). Any future rule loosening silently widens the register. | probe; `fix_hr_core.py:905-912` | Add explicit officer check (defence in depth) | `fix_hr_core.py` |
| M21-F10 | P3 | B | `fix.leave.type` writable whitelist contains `parent_id`, which the model does not define. | `a09/writable.py:899-910` [STATIC] | Remove | `a09/writable.py` |
| M21-F11 | P3 | B | `statutory_density_score` ("Statutory Density (%)", default 52.0) is decorative commentary exposed as a writable field and printed on the contract document. | `fix_hr_core.py:1312-1316`; writable.py [STATIC] | Remove from form/whitelist/doc | `fix_hr_core.py` etc. |
| M21-F12 | P3 | I | Leave-type seeds stamp `verified_on=2026-10-18` with `verified_by_id` NULL on all 6 types (live), although controls say verification is set only by `action_verify_citation` recording who verified (A09 P8). | SQL §4; `statutory_leave_data.xml`; `fix_leave_controls.py:88-92` | Seed False; HR re-verifies | `statutory_leave_data.xml` |
| M21-F14 | P3 | A | FR-HCM-009 rehire as a new employment period: not built (known owner decision). | capture pass-2 §6 [STATIC] | owner decision | — |
| M21-F16 | P3 | A | FR-HCM-002 one-party-per-employee unenforced: no constraint on `party_role_id`, no reconciliation (AC-01 unevidenced). | `hr_employee_ext.py:31-45` [STATIC] | constraint + cleanup-report line | `cd_employee_core` |
| M21-F17 | P3 | I | T-03/BRU-HCM-07 "step-up authentication" for S3 fields: only access logging exists; no step-up anywhere. | [STATIC] | architecture decision (M29) or drop the claim | — |
| M21-F18 | P3 | H | FR-HCM-025 org chart is a flat branch×position table; no hierarchy/drill-down (position `parent_id` loop-checked but never drawn). | `m21.py:581-599`; `m21.js` M21-orgchart [STATIC] | tree render | `m21.js` |
| M21-F19 | P3 | B | AUT-HCM-03 promised manager+HR alerts at 30/7 days; cron warns HR only at 14 days (known not-built). | `fix_hr_contract_controls.py:61,616-646` [STATIC] | add manager activities | `fix_hr_contract_controls.py` |
| M21-F21 | P3 | K | Statutory artefacts are .txt payloads; no PDF/letterhead/e-mail export path (report-export standard unapplied to employee documents). | `fix_hr_core.py:789-903` [STATIC] | QWeb PDF | `cd_hr_core/report` |
| M21-F23 | P3 | G | `employee.joined` published on create but no fix.event.consumer row exists for it in-tree (joiner side of the F7 hole). | `cd_employee_core/hr_employee_ext.py:106-130`; `fix_a09_m21_data.xml` (3 consumers, none for joined) [STATIC] | register consumer with M29 service | M29 addon |

Verified working (executable, probe 28 PASS): residency NID/TIN format+duplicate refusals; every read
logged; log readable only by HR Manager, append-only even as su; plain employee and line manager get
no NID value or search hit; guard refuses direct writes to contract/exit/leave state, settlement
amount, wage of an under-contract employee, recorded bank channel, employee-code rewrite; hand-made
abandonment exit refused; PSR self-verify refused; hearing before the 7-day window refused;
gross-only promotion refused; position loop refused. NOT CHECKED by R1 (lead baseline covers):
routed M63 approvals end-to-end, KPI/report packs executed against real data, live ir_cron rows,
leave request E2E, renderer of the 4 D365 forms in a browser.

---

## 2. Spec-coverage matrix (A)

| Family (spec §5/6/11/14/15) | Reqs | BUILT | PARTIAL | MISSING/WRONG |
|---|---|---|---|---|
| 5.1 Employee master FR-001..010 | 10 | 6 | 3 (002 party unenforced F16; 008 no suspended status F13; 010 search ok/hash) | 1 (009 rehire F14) |
| 5.2 Contract & terms FR-011..019 | 9 | 6 | 2 (013/014 bilingual F2/F4) | 1 (017 contractual longer notice, owner) |
| 5.3 Org & position FR-020..027 | 8 | 5 | 2 (025 chart F18; 021 OU alignment via rules) | 1 (027 DOFA-by-position, owner) |
| 5.4 Lifecycle FR-028..039 | 12 | 11 | 1 (039 JML consumer hole F7/F23) | 0 |
| 5.5 ESS & rights FR-040..046 | 7 | 5 | 1 (041 MSS team view partial) | 1 (045 erasure-vs-retention F15; 040 own-view F30 counted PARTIAL→see note) |
| §11 AUT-01..13 | 13 | 9 | 1 (AUT-03 F19) | 3 (AUT-02 hard block owner; AUT-13 F15; AUT-11 completeness report → weekly report missing) |
| §14 Reports (12) | 12 | 8 | 1 (statutory-artefact compliance KPI exists; report missing) | 3 (contract-expiry weekly, data-completeness weekly, self-service adoption, rights monthly) |
| §15 KPIs 212..222 | 11 | 7 | 2 (212/213 not surfaced as numbers) | 2 (219 M33-side clock, 222 perf) |
| **Totals** | **82** | **57** | **13** | **12** |

---

## 3. Settings register (live on fix_real_a09, all 3 companies identical)

| setting | live | default | operative? |
|---|---|---|---|
| `cd_hr_core.identity_hash_key` (ir.config_parameter) | set, 64 hex | minted at install | yes — duplicate NID/TIN checks live (0 duplicate groups found) |
| fix_hr_contract_weekly_hours_cap | 48 | 48 | yes (s.102 cap enforced; 0 violations — table empty) |
| fix_hr_resign_notice_permanent_days | 60 | 60 | yes (2025-26 tiers unconfirmed — F24) |
| fix_hr_resign_notice_temporary_days | 30 | 30 | yes |
| fix_hr_suspension_subsistence_pct | **0** | 0 | **no — blocks every suspension** (F20) |
| fix_hr_abandon_absence_days / reply / hearing | 10 / 10 / 7 | 10/10/7 | yes (2013 s.27(3A) text) |
| fix_hr_death_benefit_min_service_years | 2 | 2 | yes (2026 reportedly 1y — adviser) |
| fix_annual_leave_basis | service | service | yes (1/18 accrual; register empty) |
| fix_leave_coverage_max_pct / mode | 0 / flag | 0 / flag | **off** (BRU-WFM-04 not ruled) |

---

## 4. Measured facts on fix_real_a09 (ids/counts only; SQL probe)

- Employees: 504 total, 504 active, 0 archived. Users: 342 active internal, 310 with an employee (32 without).
- Contracts: **0 rows** (draft/active/anything). Leaves: 0 requests. Exits/transfers/disciplinary/abandonment/master-changes/probation-reviews/handovers/exit-interviews/notice-acks: **0 rows each**. Leave accrual register: 0. Documents: 1 (appointment), 0 service books → KPI-215 today = 0/504.
- Identity: NID held (hash) 315/504; TIN 0; passport 0; residency_ref 315; clear legacy columns hold 0 values (moved); identity read log already 5,321 rows; 0 duplicate NID/TIN/employee-code groups.
- Demographics: department 504/504, job 504/504 (hr.version), position/branch/OU/manager/bank/manager not all measured via ORM — SQL direct fields: job_band/parent_id/etc. [partially NOT CHECKED]; sex 0/504, marital 0/504, present street/city 0/504, children>0 0/504.
- Structure: 0 manager cycles; 0 active-but-left; 61 positions (0 frozen), **37 over establishment**; 23 departments (0 with cost centre); 61 jobs (0 with family).
- Role holders: hr_officer 5, hr_manager 5, payroll_officer 3, payroll_manager 3, legal_counsel 1, executive 1, finance 1, clearance_it 1, clearance_assets 1, party_dpo 0 (transitive implied groups).
- Approval matrix: 6 rows, domains discount/write_off/estimate/credit_note/expense/requisition — **no hr_* rows**; DOFA ladders: 4.
- Leave types (company 1 only): casual 10, sick 14 (cert required), annual 20 carry 40, festival 11, maternity **112**, paternity 10; verified_by_id NULL on all 6 (F12).
- Settings: see §3. Event consumers registered: employee.left/moved/role_changed (3). KPI-090 orphans (SQL form): 0.

---

## 5. Cross-area section

| link | state | which side wrong |
|---|---|---|
| M56 payroll inputs (contract/bank/tax/settlement I1) | Wired: `fix_payroll_settlement.py:72` overrides `_fix_settlement_breakdown`; death-benefit setting read `fix_payroll_statutory.py:167-186`; nominee payees pinned by M21; encashment source `_fix_unused_annual_leave_days` (I2) consumed at `fix_payroll.py:1824-1838` | M21 data side: 0 contracts, 0 TIN, 0 tax zones (F26/F27) — M56 cannot run |
| Cost centre → payroll GL | `_fix_effective_cost_centre` consumed (`fix_payroll.py:1003`) but 0 departments carry a code (F31) | M21 data |
| M29 JML | 3 consumers registered; no producer of identity.* events (F7); employee.joined unconsumed (F23); drain cron 5-min wired | M29 side |
| M30 branch/OU | operating_unit_id on employee/contract/leave + generated OU isolation rules | OK |
| M45/M46 custody | `toolkit_custody_ref` gates exit/movement asset clearance; ITSM outstanding assets block settlement (`fix_hr_exit_controls.py:331-357`) | OK |
| M24 documents | contract template/document link + `fix.document` generation; appointment/service book remain in-module txt (F21) | M21 side |
| M63 matrix | 18 HR domains added; no live matrix rows (F29) | configuration |
| SoD gate hr.employee role writes | `fix.sod.control.gate_role_set` on create+write (A10 P1-3) | OK |
| M58 hire | candidate NID scrubbed at hire (`fix_talent.py:872`) and on retention expiry | OK |

---

## 6. Owner decisions (recommendation) and adviser questions

1. **Backfill the 504 contracts + statutory demographics** (F26/F27) — blocking first payroll; recommendation: hire-contract backfill with legal sign-off batch, then enrichment wave for sex/marital/NID/TIN.
2. **Appoint holders** for legal counsel, HR executive, HR finance, clearance-IT, clearance-assets, and the party DPO (F29/F32); seed matrix rows for the hr_* domains if SLAs are wanted.
3. **Form 6(a) NID decision** (pending): recommendation — keep NID out of the register export (Form 8/Form 6(a) columns don't include it); masked last-4 only on Form 7 drafts as today (F1).
4. **Maternity 112→120** and **s.26 notice 120/30 vs 12 weeks + s.27(4) resignation compensation**: confirm the 2025-26 gazette (F5/F24).
5. **Rule the off settings**: suspension subsistence % (unblocks s.24), leave-coverage threshold, weekly-hours 48-vs-60 (F20).
6. **casual/sick holidays-in-leave charging (r.106)** — counsel; code default contradicts the rule (F6).
7. Unchanged owner items: privacy-notice hard block (AUT-HCM-02), DOFA-by-position, rehire periods.

Adviser questions: gazetted 2025-26 texts for s.19/s.26/s.27(4)/s.46; whether Form 8 requires any identity number; PDPA-2026 erasure vs the 10-year BLA retention override; correct reading of r.106 for annual leave.

Test baseline: run by the lead (R1's run was stopped for machine relief); module suites in scope = 278 test functions across 19 files (counts NOT CHECKED by R1).
