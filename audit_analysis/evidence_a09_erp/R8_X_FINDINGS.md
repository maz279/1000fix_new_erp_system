# A09 "People & Workforce" ERP audit — R8 (cross-area & cross-module links)

Auditor: **R8** (cross-area). Date: 2026-11-22. Worktree HEAD `6f0d6a54`.
Scope: every link between the seven A09 modules (cd_hr_core M21, cd_competency M22,
cd_attendance M55, cd_payroll_bd M56, cd_performance M57, cd_talent M58, cd_hse M59),
the platform `cd_employee_core`, and every other area that touches A09 models — proved
end to end on the ORM where the budget allowed, otherwise [STATIC] with file:line.

Probe scripts and raw outputs: `C:\Users\DELL\AppData\Local\Temp\a09erp\R8\`
(`probe1_real.out`, `probe2_real.out`, `probe3_real.out`, `probe4_jml.out`,
`probe5_leaver.out`, `probe6_pay.out`, `probe7_final.out`, `probe8_real.out`,
`probe_event_registry.log`, `probe_deployment_wiring.log`).
All DB probes ran inside rolled-back transactions; no data persisted; no file under any
checkout was modified (one checker, `tooling/events/verify_event_registry.py`, writes an
evidence JSON into the worktree when run — the lead reverted it; do not re-run it
in-place).

Test suites (`cd_p03_portal/tests/test_a09_control_suite.py`, `test_a09_write_whitelist.py`,
`test_a09_p0_people_controls.py`, `cd_event_outbox/tests`, `cd_rbac_ext/tests`,
`tooling/tests`): **run by the lead** — my own background run was stopped after a
shared-DB deadlock (contention, not a product defect); counts not reported here.

---

## 1. Findings

| id | severity | category | finding (owning side in bold) | evidence | proposed fix | files a fixer would touch |
|---|---|---|---|---|---|---|
| X-F1 | **P0** | G/C | **Platform (cd_event_outbox + deployment), hits A09 hardest.** The joiner identity chain is dead in production: all **504/504 `employee.joined` events sit at bus status=failed** (emitted 2026-11-09), 18,587 outbox rows pending, **0/504 employees have a `keycloak_user_id`**, 0 `fix.jml.event` rows. Nothing in the repo drains the outbox to the bus (`drain_pending` has **no caller**: no ir.cron, no service), so the external `services/identity-lifecycle` Keycloak worker never receives joiner/leaver events → AUT-047 (create identity, assign role, grant portal) and the KPI-090 "deprovision within 1 h" IdP path can never fire on production. In-Odoo consumers are unaffected (relay works). | probe8_real.out + SQL: `employee.joined|failed|504`; grep `drain_pending` → no caller; `hr_employee_ext.py` keycloak field; `probe1_real.out` (keycloak ids 0) | Deploy an outbox→bus drainer (ir.cron or the notification-dispatcher-style service), retry `status='failed'`, and alert on failed/pending age (extend `cron_relay_age_alert` to bus status). Re-deliver the 504 failed joiner events. | `addons/platform/cd_event_outbox/` (new drain cron or extend `cron_relay_age_alert`), infra deployment |
| X-F2 | **P1** | G | **M02 (a_service_delivery), M15 (e_supply_chain), A07 (f_asset_facilities) — missing consumers.** `employee.left` is consumed only by cd_hr_core (Odoo login archive), cd_rbac_ext (groups/JML/ITSM unassign), cd_attendance (roster+on-call close) and the external identity service. The 05-03 catalogue names M02 and M15 as consumers; **no code in a_service_delivery / e_supply_chain / f_asset_facilities subscribes** — a leaver's open work orders / field orders stay assigned, vehicle bookings stay "booked", and their pending approvals-in-inbox are neither reassigned nor blocked. Exit clearance refuses only on ITSM assets (`_fix_refuse_outstanding_itsm_assets`, BRU-ITS-13) and toolkit custody — a **van booking and open jobs pass clearance**. Dynamic proof of the consumers that DO run: probe5 (login archived, roster slot removed, jml ok); the absence on the other side is grep-proven (0 refs to `employee.left` outside the four consumers). Van/work-order staleness NOT re-proven dynamically (service-order→device prerequisite chain too deep for remaining budget) — [STATIC] + consumer table. | grep across `domain/a_service_delivery`,`e_supply_chain`,`f_asset_facilities` (no `employee.left`); `cd_hr_exit_controls.py:331-357`; probe5_leaver.out | Add `fix.event.consumer` rows: M02 reassign/flag open `fix.work.order`/`fix.field.order` of a leaver; M46 release/flag `fix.vehicle.assignment`; and extend exit clearance to refuse while a vehicle booking or open job is held. | `addons/domain/a_service_delivery/*` (new consumer), `cd_vehicle_ext`, `cd_hr_core/models/fix_hr_exit_controls.py`, new consumer XML |
| X-F3 | **P1** | F | **M56/M19 (A09 owns the flag).** Gratuity GL accounts are **not configured** on `fix_real_a09` (`payroll_gratuity_expense_account_id=False`, `payroll_gratuity_provision_account_id=False`) while the monthly gratuity cron is live (ir.cron id=165, nextcall 2026-12-05) and `_post()` only books when **both** accounts exist — the BLA 30-days-per-year gratuity provision (spec `gratuity.accrued` → M19, Q-05 "material unrecorded liability") will silently produce no ledger entry after go-live. | probe2_real.out §9; `fix_payroll_gratuity.py:136-146`; probe6 (cron ran, 0 rows, no error) | Configure both accounts on company 1 before the first accrual month-end; make the cron raise/log loudly when eligible contracts exist but accounts are missing. | `res.company` payroll fields (finance config), `cd_payroll_bd/models/fix_payroll_gratuity.py` |
| X-F4 | **P1** | L | **A09 readiness.** `fix.employment.contract` has **0 rows** for 504 employees — payroll population, probation/contract-expiry crons, gratuity and settlement all have nothing to work on; first live payroll run impossible. Same class: 0 certifications (so the M22 dispatch gate, which fails CLOSED, will block **all** field dispatch until certs are loaded), 0 attendance/roster/leave/HSE/requisition rows. | probe2_real.out readiness counts | Load contracts (and certifications) before go-live; run the migration verification the specs demand (M22 certificate-by-certificate). | data migration, not code |
| X-F5 | **P1** | L/I | **M29/M21 identity mapping.** 504 active employees but only **310 have a login** (194 without); **32 active internal users have no employee record**; 0 keycloak ids (X-F1); 54 register roles, **0 have a `group_id`** (role→group mapping "never guessed" — every role change relies on a human access review, by design). No duplicate logins/NID hashes (0/0). | probe1_real.out §1; probe8_real.out | Reconcile the 32 orphan users and decide the 194 no-login employees (field workers without accounts?) before SSO cutover. | `cd_user_migration`, HR data |
| X-F6 | P2 | D | **M63/A09.** The approval-authority matrix has **no people rows at all**: the 18 `hr_*` decision domains added by `PEOPLE_DECISION_DOMAINS` have zero `fix.approval.matrix` rows on production, so every A09 approval runs on DEFAULT_RULE (any one holder of the coded group, 24 h SLA, 1 escalation). Nothing is stuck (all coded groups have ≥1 holder — table §3), but the per-domain SLA/voting/escalation policy the rule book promises is unused. | probe1_real.out §3 (6 matrix rows, none hr_*); `fix_people_approval.py:20-39` | Have HR Director + CFO rule at least the money domains (`hr_payroll_release`, `hr_offcycle`, `hr_bonus`, `hr_wppf`, `hr_exit`). | `fix.approval.matrix` data |
| X-F7 | P2 | D/I | **M29.** `cd_rbac_ext.group_sensitive_data_clearance` has **0 holders** on `fix_real_a09` — anything routed to it (sensitive-data clearance, step-up approvals) has no human who can act. (`E-Waste HSE Officer` also 0, out of A09 scope.) | probe3_real.out §A | Appoint holders or re-point the clearance flow. | `cd_rbac_ext` group membership |
| X-F8 | P2 | D | **M63/A09.** No A09 model carries `fix.dofa.mixin` (45 mixin children, none HR) so **no DOFA ladder can ever be ruled for HR money**; only `fix.complaint` and `fix.loyalty.ledger` have in-force ladders. Payroll release/off-cycle/bonus/WPPF/exit settlements are approved by the coded group **at any amount** — no tiered financial authority for the biggest recurring payment in the company. This is the brief's "none seeded for HR money — what happens": the role group decides, whatever the size. | probe2_real.out §4 | Owner decision: either add the DOFA mixin to the money models (`fix.payroll.period`, `fix.payroll.offcycle`, `fix.payroll.bonus.run`, `fix.wppf.allocation`, `fix.hr.exit`) or rule matrix rows with amount conditions. | `cd_hr_core`/`cd_payroll_bd` models, `cd_entity_config` |
| X-F9 | P2 | D | **M29 data.** 2 of 63 `fix.sod.control` rows have role_a/role_b = None (ids 63, 64) on production; and the register pairs Payroll Officer (R-41) only with HR Manager — there is **no Payroll Officer × Payroll Manager control** (SOD-03 preparer/approver) in the register (it is enforced in code: `action_approve` maker-checker + `check_releaser` SOD-29). | probe3_real.out §B; `fix_payroll.py:1111-1143`, `fix_payroll_disbursement.py:82-98` | Clean the 2 broken rows; add the R-41×Payroll-Manager pair so the register matches the code. | `fix.sod.control` data |
| X-F10 | P2 | G | **M56→M24.** Payslip/certificate archival to Documents is **not wired**: no `fix.document` creation anywhere in cd_payroll_bd (spec 12.2: M24 retention "Command"). `payroll.payslips_published` is in the FF-48 no-consumer baseline. | grep `fix.document` in cd_payroll_bd = 0 hits; wiring baseline | Add a consumer that archives each published payslip (and the tax certificate) as `fix.document` under the retention schedule. | `cd_payroll_bd`, `cd_document_core` |
| X-F11 | P2 | G | **Catalogue drift (05-03).** `payroll.approved` is published (`fix_payroll.py:1144`) with catalogue consumers M19+M24, but **no consumer exists** (baseline) — M19 posting actually happens in-process later at `action_post` (pay→post) and M24 is X-F10. Working money path, wrong contract text. | `fix_payroll.py:1144,1257`; deployment-wiring baseline | Update 05-03 (and the event registry description) to the as-built contract: in-process `action_post` + `payroll.posted`→M51. | docs `05-03_Integration_and_API_Catalogue.md` |
| X-F12 | P2 | C | **M58 settings shipped "off".** `cd_talent.require_headcount_budget=0` — the M54 headcount-budget requisition gate (spec 12.1 "requisition gate") is disabled; `cd_talent.candidate_retention_days=0` — PDPA candidate erasure (KPI-285) effectively off; `cd_hse.loneworker_tolerance_minutes=0`, `hazard_review_days=0`, `ppe_replacement_grace_days=0`; `cd_performance.incentive_dispute_days=0`, `incentive_clawback_days=0`. Each is a shipped-off control awaiting an owner ruling. | probe3_real.out §C | Owner decision per key (recommend: budget gate ON before requisitions go live; retention ≤ 365 days; tolerance/grace days set to policy). | `ir.config_parameter` |
| X-F13 | P2 | J | **M58 statutory.** `cd_talent.minimum_hiring_age=14` — the BLA floor for adolescent light work, but technician roles involve electrical/repair work where BLA/Rules set 18 for hazardous work. The hiring gate should be 18 for field/workshop roles. ADVISER: confirm the hazardous-work classification with counsel. | probe3_real.out §C; `cd_talent` age check | Role-aware minimum age (18 for technician/HSE-relevant roles). | `cd_talent` |
| X-F14 | P3 | C | **M21.** A plain `hr.employee` create (master screen, not the talent hire path) publishes `employee.joined` immediately — **even with `employee_code: false`**, which the identity service can only permanently fail on ("carries no employee code"). The talent path correctly holds the event until onboarding; the master-screen path fires a doomed event. | probe4_jml.out JOINER 2 (payload `"employee_code": false`) | In `cd_employee_core.create`, publish `employee.joined` only when `employee_code` is set (or default a code at create). | `platform/cd_employee_core/models/hr_employee_ext.py:106-130` |
| X-F15 | P3 | G | **M21 noise.** 2,520 `employee.moved` events (~5 per employee) sit pending on the bus — routine master writes (department/branch) each announced a "move"; the in-Odoo consumer opened access reviews for all of them on the load date. Not harmful, but the mover signal is noise, not moves; a real transfer publishes its own richer event. | SQL `employee.moved|pending|2520`; `fix_hr_core.py:1158-1196` | Consider only firing the write-hook event for branch/OU/position changes (drop bare department), or batching. | `cd_hr_core/models/fix_hr_core.py` |
| X-F16 | P2 | C | **M02→M55 availability, NOT CHECKED dynamically.** `availability.changed` (spec M55 12.3, blocking dependency for M02/M27/M31/M05) is not in the consumer XMLs and is not published by cd_attendance (no `publish(... "availability.changed"` hit). Roster/leave effects on dispatcher eligibility could not be found in the time budget — mark for the A01/A02 auditor or a follow-up. [STATIC, incomplete] | grep; A09 spec M55 §12.3 | Verify and wire `availability.changed` (or document the synchronous `/api/v1/availability` equivalent as the contract). | `cd_attendance`, `cd_field_service` |
| X-F17 | P3 | H | Notification templates for A09 events (bn+en) and people KPIs in the BI registry: the template/KPI models I probed for are **not in the registry under those names** — NOT CHECKED to conclusion (budget). M27 routing for people events is handled by the external notification-dispatcher NT registry; in-Odoo `fix.notif.delivery` has 0 rows. | probe8_real.out | Follow-up: diff the NT-001 matrix against A09 events (payslip available, cert expiring, roster published). | `cd_contact_centre`, NT registry |

Positive links proven working (no finding): the relay (`cron_relay`, 1-minute cron, per-subscription delivery rows, idempotent, savepoint-isolated, dead-letter at 3); leaver consumers (login archived + groups removed + roster/on-call closed + ITSM unassigned, all idempotent — probe5); mover access review (idempotent — probe5); identity outcome application (`identity.provisioned` → `keycloak_user_id`, re-delivery safe — probe4); BEFTN→M50 `fix.payment.execution` (sent, idempotent — probe6); M50 settle correctly refuses the cash leg without journal/payable accounts (nothing guessed — probe6); M51 salary-TDS intake refuses a `payroll.posted` whose move is not posted (probe6); HSE compensation → M56 off-cycle (probe6); M46 van gate refuses dispatch without fitness certificate + insurance (probe5); M22 cert gate blocks dispatch fail-closed, re-checks at start, and the `certification.expired/.suspended/.revoked` consumer flags not-started orders [STATIC: `fix_field_order_certification.py` + lead-run tests]; SoD on payroll approve/release (code read).

---

## 2. Link register (A09 side unless noted; E = evidence path in R8 folder)

| # | source: model.action / event | target: consumer / method | in-process / cron | exists? | fires? | correct? | evidence |
|---|---|---|---|---|---|---|---|
| L1 | hr.employee.create / onboarding.complete → `employee.joined` | external identity-lifecycle worker (Keycloak) via bus | bus (external worker) | yes (service) | **NO in prod** (bus failed 504/504) | design ok; dead transport | E: probe8_real.out, probe4_jml.out |
| L2 | `employee.joined` → IdP outcome `identity.provisioned` | hr.employee.consume_identity_lifecycle_event (+ drain cron 5 min) | ir.cron `drain_identity_lifecycle_events` | yes | yes (probe) | yes, idempotent | E: probe4_jml.out |
| L3 | hr.employee write(MOVER_FIELDS)/transfer apply → `employee.moved` | hr.employee.consume_employee_moved (access review activity) | relay cron | yes | yes (2,520 deliveries ok on real) | yes, idempotent; payload thin (code+dept) | E: probe5_leaver.out, SQL |
| L4 | hr.employee role write → `employee.role_changed` | hr.employee.consume_employee_role_changed | relay cron | yes | yes (0 events yet on real) | yes (opens review, lists SoD conflicts) | code `fix_hr_master_controls.py:456` |
| L5 | exit/last-working-day/mark-left → `employee.left` | hr.employee.consume_employee_left (Odoo login archive) | relay cron | yes | yes (probe) | yes, idempotent | E: probe5_leaver.out |
| L6 | `employee.left` | fix.jml.event.consume_employee_left (strip groups, deactivate user, unassign ITSM) | relay cron | yes | yes (probe) | yes | E: probe5_leaver.out |
| L7 | `employee.left` | hr.employee.consume_employee_left_roster (close roster + on-call) | relay cron | yes | yes (slots_removed=1) | yes | E: probe5_leaver.out |
| L8 | `employee.left` | M02 work/field orders, M15, M46 vehicle | relay cron | **NO consumer** | — | **BROKEN (X-F2)** | grep 0 refs |
| L9 | `employee.left` → `identity.deprovisioned` | KPI-090 stamp + `employee.keycloak.deprovisioned` | drain cron | yes | not in prod (bus) | code ok; manual HR-manager fallback exists | `fix_hr_core.py:1000-1122` |
| L10 | payroll period approve → `payroll.approved` | (catalogue: M19, M24) | — | **no consumer** | — | drift only; posting is in-process at post (X-F11) | baseline + code |
| L11 | payroll period post → `payroll.posted` | fix.salary.tds.consume_payroll_posted (M51) | relay cron | yes | yes (probe; refuses unposted move — correct) | yes, idempotent | E: probe6_pay.out |
| L12 | payroll period pay → `payroll.beftn_submitted` | fix.payment.execution.consume_payroll_beftn_submitted (M50) | relay cron | yes | yes (probe: sent, 100000) | yes, idempotent, totals checked | E: probe6_pay.out |
| L13 | bank confirmation → `payroll.beftn_settled` | fix.payment.execution.consume_payroll_beftn_settled (Dr net payable / Cr bank) | relay cron | yes | yes (probe; needs journal+payable — real chart has them) | yes, refuses to guess | E: probe6_pay.out |
| L14 | bank return → `payroll.beftn_returned` | consume_payroll_beftn_returned (net/book-back) | relay cron | yes | NOT probed (returns model not on test DB) | code-read ok | `fix_payroll_treasury.py:478` |
| L15 | off-cycle release → `payroll.offcycle_paid`; bonus → `payroll.bonus_paid` | M50 consumers | relay cron | yes | NOT probed | code-read ok | consumer XML |
| L16 | bonus post → `payroll.bonus_posted` | fix.salary.tds.consume_payroll_bonus_posted (M51) | relay cron | yes | NOT probed | code-read ok | XML + tests (lead) |
| L17 | HSE compensation award → `hse.compensation.awarded` | fix.payroll.offcycle.consume_compensation_awarded | relay cron | yes | yes (probe: 25,000 off-cycle) | yes | E: probe6_pay.out |
| L18 | recognition award → `recognition.awarded` | fix.payroll.offcycle.consume_recognition_awarded | relay cron | yes | NOT probed | code-read ok | XML |
| L19 | cert lapse cron → `certification.expired`/`.suspended`/`.revoked` | fix.certification.consume_certification_lost + M02 flag on not-started orders | ir.cron `_cron_certification_expiry` (daily, id=163) + relay | yes | cron yes (0 certs on real) | yes | data XML + code |
| L20 | training pass → `training.passed` | fix.training.enrollment.consume_training_passed | relay cron | yes | yes | yes | consumer table |
| L21 | A07 site/vehicle injury → `site.incident`/`vehicle.incident` | fix.hse.incident.consume_site_incident / consume_vehicle_incident (M59 case) | relay cron | yes | NOT probed (A07 side) | A07 tests cover (lead) | bridge XML |
| L22 | HSE incident report → `hse.incident_reported` | fix.hse.incident.consume_incident_reported (alert) | relay cron | yes | NOT probed | code-read ok | `fix_hse_automation.xml` |
| L23 | safety cert lapse → `certification.safety_lapsed` | fix.hse.safety.followup consumer | relay cron | yes | NOT probed | code-read ok | XML |
| L24 | lone-worker escalation → `hse.loneworker.escalated` | fix.hse.loneworker consumer + 5-min missed-checkout cron (id=170) | ir.cron | yes | NOT probed | code-read ok | XML |
| L25 | M46 van booking | fix.vehicle.assignment gate: fitness cert + insurance + licence | in-process constraint | yes | **yes (probe REFUSED without docs)** | yes | E: probe5_leaver.out |
| L26 | M22 eligibility on M02 dispatch | fix.field.order._fix_assert_certified (fail-closed; waiver path) | in-process | yes | yes (code + lead tests) | yes | `fix_field_order_certification.py` |
| M02→M55 availability (`availability.changed`) | cd_attendance → M02/M27/M31 | relay | **not published** | — | **NOT CHECKED (X-F16)** | grep |
| M56→M24 payslip archive | — | — | **not wired (X-F10)** | — | — | grep |
| M57→M56 incentive publish | `incentive.published` (spec) → payroll | — | **NOT CHECKED** (M57 auditor's side) | — | — | — |
| M25/M62 people KPIs | fix.kpi/metric models not found by name | — | — | — | **NOT CHECKED (X-F17)** | probe8 |

---

## 3. Decision-domain → coded group → holder count on `fix_real_a09`

All 18 A09 domains resolve via `fix.people.approval.mixin` to a CODE-declared group
(the matrix has no people rows, X-F6; DOFA cannot apply, X-F8). Measured holders:

| decision domain (`_approval_domain`) | model(s) | coded group (xmlid) | holders |
|---|---|---|---|
| hr_payroll_release / hr_offcycle / hr_bonus / hr_wppf / hr_statutory_pack | fix.payroll.period/.offcycle/.recovery/.bonus.run/.wppf.allocation, fix.statutory.pack | cd_payroll_bd.group_payroll_manager | **3** |
| BEFTN release (SOD-29) | fix.beftn.batch / mfs | cd_payroll_bd.group_payroll_release | **3** |
| hr_master_change / hr_leave | fix.hr.master.change, fix.leave.request | cd_hr_core.group_hr_officer | **5** |
| hr_contract | fix.employment.contract | cd_hr_core.group_hr_legal_counsel | 1 |
| hr_movement / hr_exit(abandon) / hr_disciplinary | fix.hr.transfer, fix.hr.abandonment, fix.hr.disciplinary.case | cd_hr_core.group_hr_executive | 1 |
| hr_exit (settlement) | fix.hr.exit | cd_hr_core.group_hr_finance | 1 |
| hr_attendance (adjustment) | fix.attendance.adjustment | hr.group_hr_manager | 5 |
| hr_attendance (approval/roster) | fix.attendance.approval, roster publication | hr_attendance.group_hr_attendance_user / cd_attendance.group_attendance_supervisor | 1 / 24 |
| hr_certification (+waiver) | fix.certification, fix.certification.waiver | cd_competency.group_certification_verifier / group_dispatch_override | 1 / 1 |
| hr_training_budget | fix.training.budget | cd_competency.group_training_budget_approver | 1 |
| hr_hse (incident/JSa) | fix.hse.* | cd_hse.group_hse_officer | 5 |
| hr_hse (compensation) | compensation proposal | cd_hse.group_injury_compensation_approver | 1 |
| hr_incentive | fix.incentive.run / .line / recognition | cd_performance.group_incentive_approver | 1 |
| hr_incentive_scheme | fix.incentive.scheme | cd_performance.group_scheme_hr_director | 1 |
| hr_review | fix.performance.review | cd_performance.group_performance_calibrator | 1 |
| hr_compensation | fix.compensation.proposal | cd_performance.group_compensation | 1 |
| hr_requisition | fix.job.requisition | cd_talent.group_requisition_approver | 1 |
| hr_requisition (headcount budget) | fix.headcount.budget | cd_entity_config.group_dofa_tier_4 | 3 |
| hr_background_check / hr_offer | fix.talent.check / fix.talent.offer | cd_talent.group_background_verifier / group_offer_approver | 1 / 1 |
| exit clearance IT / assets | fix.hr.exit ticks | cd_hr_core.group_clearance_it / group_clearance_assets | 1 / 1 |
| (platform) sensitive data clearance | M29 step-up | cd_rbac_ext.group_sensitive_data_clearance | **0 (X-F7)** |

**Zero-holder groups: 1** (`group_sensitive_data_clearance`). No A09 decision domain is
stuck for want of an approver. Live simulation on real (synthetic records, rolled back):
payroll period release → 3 named payroll managers; leave request → the subject's line
manager (manager-first path) — `probe3_real.out` §D.

SoD register: 63 rows; HR/payroll-relevant pairs: R-41 Payroll Officer × R-30 HR Manager,
R-30 × R-03 CFO, R-31 HR Officer × R-27/R-30, R-47 × R-30 (duplicates exist: ids 26/27,
28/29, 45/46, 55, 6/41/42/44 …); 2 rows have both roles NULL (X-F9).

## 4. A09 cron / consumer table (measured on `fix_real_a09`)

All A09 crons run as `__system__` (tz **Asia/Dhaka**), `nextcall` set, `active=True`:

| cron (ir.cron id) | code | interval | verdict |
|---|---|---|---|
| 154 M21 probation review | model._cron_probation_review() | 1 day | wired |
| 155 M21 contract expiry | model._cron_contract_expiry() | 1 day | wired |
| 156 M21 last working day (employee.left) | model._cron_process_last_working_days() | 1 hour | wired |
| 157 M21 settlement due | model._cron_flag_overdue_settlements() | 1 day | wired |
| 158 M21 disciplinary deadlines | model._cron_disciplinary_deadlines() | 1 day | wired |
| 159 M21 abandonment timeline | model._cron_abandonment_timeline() | 1 day | wired |
| 160 M21 identity residency move | model._cron_identity_residency_move() | 1 day | wired |
| 153 M55 leave accrual | model.cron_accrue_annual_leave() | 1 day | wired |
| 161/162 M55 attendance routing ×2 | cron_route_pending_attendance / cron_route_adjustments | 1 hour | wired |
| 163 M22 certification expiry | model._cron_certification_expiry() | 1 day | wired |
| 164 M56 withholding-return alerts | model.cron_return_due_alerts() | 1 day | wired |
| 165 M56 gratuity accrual | model.cron_accrue_gratuity() | 1 month | wired but **no GL accounts (X-F3)** |
| 230 M57 review chase | model._cron_chase_overdue() | 1 day | wired |
| 166–169 M58 readiness/offers/tasks/erase | 4 crons | 1 day | wired (erase off until retention >0, X-F12) |
| 170–174, 232–233 M59 loneworker/DIFE/committee/PPE/hazard/permits/plans | 7 crons | 5 min–1 day | wired |
| 30 M29 IdP outcomes (KPI-090) | model.drain_identity_lifecycle_events() | 5 min | wired; starved by X-F1 |
| M28 relay + age alert | cron_relay / cron_relay_age_alert | 1 min / 15 min | wired; health: unrelayed=0, dead=0 |

Cron↔method cross-check (static): every `cron_*`/`_cron_*` def in h_people has an
ir.cron row and vice versa — **no orphan on either side** (grep table in session log).

In-Odoo consumers for people events: 21 rows (see probe1 §6) — all models installed,
all methods callable, 0 failed deliveries; only `employee.moved` has real deliveries
(2,520 ok). Notable zero-delivery rows are simply events not yet emitted in prod
(no leaver, no payroll run, no certs).

## 5. Measured facts on `fix_real_a09`

- Employees 504 (all active); with login 310 (194 without); internal users 342 active,
  32 active without an employee; 0 duplicate logins; 0 duplicate NID hashes (315 hashed);
  **0 keycloak ids**; 0 jml events.
- Branches 73; employees with branch 504/504, OU 503/504, department 504, position 503,
  manager (parent) 269. **Employment contracts: 0.** Payroll periods: 0 (all states).
- Approvals: matrix 6 rows (estimate/discount/credit_note/expense/requisition/write_off),
  **0 people rows**; DOFA ladders 4 (2 in force, both non-HR); SoD 63 (2 broken, X-F9).
- Payroll GL config (company 1, real chart): salary 500008, PF expense 500006,
  net payable 2001821, TDS payable 200905, PF payable 200013, journal PAYR — configured;
  **gratuity expense/provision: NOT configured** (X-F3).
- Outbox: 19,091 rows; relay unrelayed=0, dead=0; bus pending 18,587; **employee.joined
  failed 504/504** (X-F1); employee.left/posted/beftn/cert events: 0 emitted yet.
- Readiness zeros (see X-F4): certifications, attendance records/locks, roster slots,
  leave/overtime, payslips, structures(ok: 1 statutory pack), requisitions, candidates,
  HSE incidents/hazards/loneworker/PPE, transfers, exits, incentives, work orders,
  field orders, vehicle assignments, headcount/training budgets, timesheets — all 0.
  Identity-access read log: 5,321 rows (NID reads logged — good).
- Settings of note (probe3 §C): see X-F12/X-F13.

## 6. Cross-area summary (which side is wrong)

- **Platform→A09 (X-F1):** platform event bus never delivers externally; joiner/leaver
  identity automation dead in prod. Wrong side: platform/deployment, not A09 logic.
- **A07→A09:** site/vehicle injury → HSE case consumers exist and are wired (bridge);
  van dispatch gate (fitness/insurance/licence) fires. Right on both sides.
- **A08 (g_finance)→A09:** M50 + M51 consumers exist, idempotent, defensively correct
  (probes). Wrong side: none found; A09 must configure gratuity accounts (X-F3).
- **A01/A02 (service delivery)→A09:** certification gate on dispatch correct and
  fail-closed; **but no leaver consumer (X-F2) — wrong side: a_service_delivery/
  f_asset_facilities**; availability.changed not found (X-F16, open).
- **A10/A12 (governance):** approval engine + relay solid; matrix/DOFA for HR money
  unruly (X-F6/X-F8) — owner decisions, not code defects; SoD register data quality (X-F9).
- **A11 (BI)/M27:** people KPIs and bn/en templates NOT CHECKED to conclusion (X-F17).

## 7. Owner decisions (with recommendation)

1. **Deploy/restart the external event bus and the outbox drainer** (X-F1) — recommend
   before any SSO cutover; re-deliver the 504 failed joiner events. [P0]
2. **Leaver reassignment policy** (X-F2): who gets a leaver's open jobs, van and inbox —
   recommend auto-flag to the branch manager + refuse exit clearance while held.
3. **Gratuity accounts** (X-F3): finance to configure both accounts before 2026-12-05.
4. **Rule the HR money domains** (X-F6/X-F8): matrix rows and/or DOFA mixin for payroll
   release, off-cycle, bonus, WPPF, exit settlement.
5. **Go-live gate**: load contracts + certifications first (X-F4) — otherwise payroll
   cannot run and dispatch is hard-blocked (fail-closed by design).
6. **Settings shipped off** (X-F12): budget gate, PDPA retention, lone-worker tolerance,
   PPE/hazard grace days, incentive dispute/clawback windows — rule each.
7. **Minimum hiring age** (X-F13): 18 for technician/HSE-relevant roles (ADVISER: confirm
   hazardous-work classification under BLA 2006 & Labour Rules 2015 with counsel).
8. **Sensitive-data clearance holders** (X-F7) and the 32 orphan active users (X-F5).

## 8. Adviser questions / NOT CHECKED

- Hazardous-work age classification for repair technicians (X-F13).
- M57 `incentive.published` → M56 hand-off (M57 auditor's chain) — NOT CHECKED here.
- M25/M62 people-KPI registry, M27 bn/en templates for A09 events, M23 training-evidence
  link, M60 risk inputs from A09 models — NOT CHECKED to conclusion (X-F17, budget).
- Attendance-lock → payroll gate, gross-to-net arithmetic, BEFTN file format — owned by
  the M55/M56 auditors and the lead-run suites; not duplicated here.
- Leaver van/work-order staleness proven statically (consumer absence) + partial dynamic
  proof; full dynamic re-run skipped (device/service-order prerequisite chain, budget).

*All probes rolled back; nothing persisted; read-only on code and production snapshot.*
