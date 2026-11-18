# M63 Process Automation: Sub-Module Capture Audit (2026-11-18)

**Trigger.** The user observed that not every M63 sub-module page has a relevant data-capture button.

**Sources**
- Spec: `1000fix_ERP_Module/03_Modules/J_Data_Analytics_and_Intelligence/M63_Process_Automation_and_Workflow_Orchestration.md`. Sections used:
  - §3: scope (18 capabilities) and boundaries (M28 transports events, M30 owns infrastructure schedules, M29 defines SoD);
  - §5: FR-BPA-001 … 032;
  - §8: the approval request, rule change and process instance lifecycles;
  - §9: BRU-BPA-01 … 25;
  - §10.1: the 20 owned entities;
  - §11: AUT-BPA-01 … 22;
  - §13: roles and the five incompatible combinations;
  - §15, §17: KPIs and AC-01 … 26.
- Function Register (`contracts/nav/registry.json`, freg 54): 7 sub-modules (Workflow Engine 11, Approval Chains 10, DoA Matrix 6, Business Rules 9, Scheduled & Event Jobs 7, Task Inbox 5, Audit & Performance 6).
- Code:
  - `cd_p03_portal/static/src/a11/m63.js`: the page registry (7 sub-module pages);
  - `cd_p03_portal/controllers/a11/m63.py`: surfaces, write whitelists, reports and KPIs;
  - `cd_workflow_engine/models/*.py`: the AUT register, the DoA matrix (the rule book the approval engine reads), workflow instances, the task inbox, business rules, substitutions, requests and history;
  - `cd_entity_config`: the DOFA value ladder and bands (kept by M30) and the scheduled-job registry (M30).
- Live data (fix_real, read-only count on 18 Nov):
  - **6** DoA matrix rows (discount, write-off, estimate, credit note, expense, requisition), all without a name, a model or an effective date;
  - **4** business rules, whose expressions are prose (`if order.total > customer.credit_limit: block`) that no code evaluates;
  - **0** automations: the 60-row AUT register (`data/aut_register.yaml`) was never loaded on fix_real;
  - **0** workflow instances, tasks, requests, history rows or substitutions;
  - DOFA tiers held by 20 / 42 / 7 / 3 / 1 users; DoA Administrator 1 (the development admin); Platform Admin 2;
  - 225 active scheduled actions (`ir.cron`), none of them missed by more than a day.

## 1. What was there (HEAD 32e24dc9)

The pages were evaluated with the engine's own `fregCreate` / `fregPanels` in node, which is how the browser decides what a page shows.

| Page | Sub-module | "+ New" | Chips | Defects |
|---|---|---|---|---|
| 1 | Workflow Engine | Workflow Definition | Workflow Definition | None on the page. An automation could declare only "manual fallback" or "retry"; FR-BPA-004 (P0) names five failure behaviours (block, retry, escalate, fall back, compensate). |
| 2 | Approval Chains | **none** | **none** | The page **captured nothing**. Its Substitution / OOO list is creatable and its form existed (`M63-form-substitution`), but nothing on the page opened it (FR-BPA-013/014). The approval requests and the approval history were on **no page**. |
| 3 | DoA Matrix | Approval Chain | Approval Chain | The matrix row says *how* an approval runs; **who may approve up to what value** (FR-BPA-009) is the DOFA ladder, kept in M30. Nothing on the page reached it, so the value side of the delegation of authority could not be captured from M63. |
| 4 | Business Rules | Business Rule | Business Rule | Its **"Rule Simulation" screen was the automation-rate report** under another name. **No simulation could be run or recorded** (FR-BPA-007 P1, BRU-BPA-04 H "a rule change must be simulated against historical transactions before activation", entity `fix.rule.simulation`). |
| 5 | Scheduled & Event Jobs | Workflow Definition (engine preset Airflow) | Workflow Definition | Only scheduled workflows were listed: **event-triggered automations were on no page** (FR-BPA-031 P0). No business job could be registered against the scheduled action that runs it, with an owner and missed-run detection (FR-BPA-030, AUT-BPA-12), although M30 has that registry. |
| 6 | Task Inbox | none | none | **Correct**: a task is raised by the approval engine and is never typed in. The all-tasks list (`M63-tasks`) was on no page. |
| 7 | Audit & Performance | **Workflow Instance** | none | The "+ New" **typed a workflow instance by hand**. Nothing in the code starts one, and the "Automation Rate" KPI was *completed instances ÷ all instances*, so a typed instance was a counted automation. What the page is for was missing: **the register of routine work** that is the denominator of the 85% target (AUT-BPA-21, AC-25, Q-02, entity `fix.automation.register`), and a **recorded manual intervention** (FR-BPA-008, BRU-BPA-15/23): Complete / Mark Failed / Escalate on the monitor changed an instance with no reason and no record of who did it. |

Guard `cd_p03_portal/tests/test_m63_capture_buttons.py` on HEAD: **18 of 31 tests fail.** The failures cover pages 2, 3, 4, 5 and 7, the hand-typed instance, the simulation screen, page 5's presets, the creatable list with no capture, the orphan lists, the monitor actions without a reason, the three missing registers, their whitelists, security and load order, and the new KPIs.

## 2. What was built

### Backend: `cd_workflow_engine` 19.0.1.1.0, new file `models/fix_m63_capture.py` (imported last)

| Page | Record | Holds | Rules |
|---|---|---|---|
| 4 | `fix.rule.simulation` (FR-BPA-007, BRU-BPA-04/22, T-12) | The candidate rule (a DoA matrix row, usually a new version not yet in force) and a past period. The run's results: records evaluated, selected by the rule's condition, would route differently, kept by a more specific rule, a summary by the rule they would move from, and up to 20 sample records. | **Saving runs it.** It reads only: no request, task, activity or message is created (tested). It compares the candidate's terms (voting policy, SLA, escalations, final action, approver group, escalation target, calendar) with the rule that routed each record (its request's pinned rule) or would route it today; a rule written for the record's own model outranks a decision-domain rule. At most 5,000 records per run, newest first, and the summary says when the period held more. A record is named in the sample only to someone who may open it (§13). **Evidence**: never edited or deleted, results never typed. Run by a DoA Administrator; everyone may read. The matrix row shows its simulation count and last run; a new KPI **"Rules Never Simulated"** counts rows in force with no simulation (spec §15 target 0). |
| 7 | `fix.automation.register` (AUT-BPA-21, AC-25) | Routine task, process area, owning module, monthly volume; automated or not, the automation that does it, and the straight-through share; the automated volume follows. | **A task counts as automated only when it names an active AUT automation** (an automation nobody runs automates nothing). Volume above zero; straight-through 0-100%. Mark Reviewed stamps who confirmed the row and when (never typed). Maintained by the DoA Administrator; everyone may read; nobody deletes (archive). **The "Automation Rate" KPI and the "Automation Rate by Process" report are now the automated volume over the registered volume**, by process area, against the 85% target. |
| 7 | `fix.workflow.intervention` (FR-BPA-008, BRU-BPA-15/23, §13) | Instance, intervention (complete, mark failed, escalate, terminate), reason; operator, time, state before and after. | Only a **DoA Administrator or Platform Admin** intervenes; a **reason of at least a sentence** is required; complete, fail and terminate apply only to a running instance; **nobody completes an instance they started**. Append-only: no edit or deletion, even by the superuser. **The monitor's Complete / Mark Failed / Escalate buttons now ask why and create this record**; a fourth button, Terminate, cancels a running instance. New KPI "Interventions MTD". |
| 1 | `fix.automation` (extended) | Failure behaviour now offers the spec's five: block, retry, escalate, manual fall-back, compensate. | The two existing values are kept, so no row changes. |
| 3, 4 | `fix.approval.matrix`, `fix.automation` | Readable names. | fix_real's six matrix rows have no name, and the automation register had no name field: a picker showed `fix.approval.matrix,12`. A row now reads as its name, else its decision domain (with model and date); an automation as `AUT-nnn · trigger`. |

Security and data:
- ACLs: plain users read all three; the DoA Administrator creates simulations, maintains the register and intervenes; the Platform Admin intervenes; nobody writes a simulation or an intervention after it is made, and nobody deletes any of the three.
- Company isolation rules from `generate-isolation-rules.py`; only the cd_workflow_engine file was kept (the generator's drift in seven other modules was reverted).
- Sequences RSIM/ (simulations) and WFX/ (interventions).

### Workspace: `m63.js`, `controllers/a11/m63.py`

- Four new lists, on their pages and in the navigation: Event-Triggered Automations, Rule Simulation (now a list, not the report), Routine Work Register, Manual Interventions (new navigation group "Audit & Performance").
- Five new forms: Rule Simulation and Automation Register Entry (tabbed), Manual Intervention, and two presets of the workflow definition, **Scheduled Workflow** (engine Airflow) and **Event-Triggered Automation** (engine Odoo automated action), so a record shows on the list it was made from.
- Cross-module chips to the owners' own forms: **Authority Ladder** and **Ladder Band** (M30, the DOFA value ladder) on page 3, **Scheduled Job Registration** (M30, a business job registered against its scheduled action, with owner, failure impact and missed-run state) on page 5.
- The workflow instance form is read-only (`create: false`), with its intervention count; the write whitelist for instances is empty.
- Approval requests and history now sit on page 2; the all-tasks list on page 6, which says `create: false` explicitly.

| Page | "+ New" after | Chips after |
|---|---|---|
| 1 Workflow Engine | Workflow Definition | Workflow Definition |
| 2 Approval Chains | **Substitution / OOO** (was none) | **Substitution / OOO**, **Approval Chain** |
| 3 DoA Matrix | Approval Chain | Approval Chain, **Authority Ladder**, **Ladder Band** |
| 4 Business Rules | Business Rule | Business Rule, **Rule Simulation** |
| 5 Scheduled & Event Jobs | **Scheduled Workflow** | **Scheduled Workflow**, **Event-Triggered Automation**, **Scheduled Job Registration** |
| 6 Task Inbox | none (engine-raised) | none |
| 7 Audit & Performance | **Manual Intervention** (was a typed instance) | **Manual Intervention**, **Automation Register Entry** |

## 3. Evidence

| Check | Result |
|---|---|
| Guard `cd_p03_portal/tests/test_m63_capture_buttons.py`. Node runs the engine's own `fregCreate`/`fregPanels` over the real registry; it also checks every list column and form field against the model, every list action against the surface, the write whitelists against the forms, the presets of page 5, that the monitor's buttons ask why, that no result, stamp or outcome is writable, the ACLs, company rules and load order. | **HEAD 32e24dc9: 18 of 31 fail.** After: **31/31.** |
| Live tests `cd_workflow_engine/tests/test_m63_capture_live.py`, run as freshly created non-admin users (a plain employee, two DoA Administrators, a Platform Admin, a complaint clerk) on a private clone `fix_test_m63` of `fix_test` (`-u all`, 166 modules, exit 0, no error). | **22/22.** The first run caught a real defect, fixed before the result above: the simulation period was compared in UTC, so a record made at 03:00 Dhaka time fell outside "today" (the period is now the user's own days, converted to stored UTC bounds). |
| Mutation check: each rule removed in turn (terms compared, condition selects, simulation never changed, never deleted; automated names an automation, that automation is active, volume above zero, review needs write access; only operators intervene, reason required, only a running instance completes, not your own instance, intervention never changed, never deleted, operator stamped not typed, terminate cancels). | **13 of 16 mutations turned the live tests red**; the source was restored byte for byte (a baseline run was green first). The 3 survivors are equivalent: each removes a code check that the access rules also enforce (the simulation write guard, the review's write check, the operator check on intervening): a plain user still gets an access error from the ACL. |
| `test_a11_e1_e4.py` (the A11 E1-E4 controls). | Updated for the deliberate change: completing an instance now needs a reason and records an intervention; the three new models joined the surface list. **All pass.** |
| Regression on the same clone: every `cd_workflow_engine` test and the whole `cd_p03_portal` suite. | **5,446 tests.** After fixing what was mine (the monitor list now says `create: false` because its form is read-only; the estate test's page-5 example names the new Scheduled Workflow form) and removing a DoA row I had created through the UI on the clone (it collided by date with the tests' rows), the affected files re-ran: **1,003 tests, 2 failures**, both **identical on HEAD 32e24dc9** (`M50-form-stmtline: no pick instruction`, `M30/1 Branch Master` offering another record's button). Two more HEAD-identical failures in the full run are outside M63 (an M50 "Cheque" chip, an M22/M55 dispatch-gate message). |
| Workspace UI on a private server (port 8131) over the clone, signed in as admin, `?debug=assets`. | The seven pages show exactly the captures in the table above (read from the rendered buttons). A Rule Simulation was **saved from its tabbed form** and its "What Would Change" tab showed the run (rule as simulated, records evaluated, summary, run by, run at). A server probe from the page posted every M63 list, form and report, and the three M30 forms offered as chips, to their endpoints: **34/34, no error.** |

## 4. Not built here (owner decisions or other modules)

- **The AUT register is empty on fix_real.** The 60 catalogue automations ship in `data/aut_register.yaml` and load with `fix.automation.action_load_register()`; nobody has run it on fix_real. Loading it is a data step for the owner to approve.
- **Business rules are prose.** The four fix_real rules (`if order.total > customer.credit_limit: block` …) are evaluated by nothing: the thresholds that actually route approvals are the DoA matrix rows and the DOFA ladders, which is why the simulation runs matrix rows. Turning the repository into executable decision tables (FR-BPA-025/026, T-03) is an engineering build with a governance decision behind it (Q-03: who may author rules, in which domains).
- **Blocking activation without a simulation** (AC-03). A matrix row comes into force on its date; refusing an unsimulated row at routing time would change how every existing row routes (all six on fix_real are unsimulated). The KPI now shows the count; making it a hard block is a CTO / CFO decision.
- **The delegation-of-authority policy itself** (Q-01) and **the register of routine work** (Q-02) are governance artefacts. The screens to hold them now exist; their content is a business exercise.
- **Process definitions with steps, versions and compensation** (FR-BPA-001/003/005, entities `fix.process.definition`, `fix.process.step.log`, `fix.compensation.action`): there is no step engine to run them, so a capture form would hold paper. The AUT register with its named engine remains the definition.
- **Event subscriptions with idempotency keys** (FR-BPA-031): automations triggered by events are now listed and captured, but delivery and idempotency belong to M28's outbox and Odoo's automated actions.

## 5. State

_State on 18 Nov 2026, 08:20:_

- **Landed.** 0416704f and 734327d7 were fast-forwarded onto `fix/a03-live-data-and-pending-work`. They are not pushed.
- **Backups.** `fix_real_pre_m63_capture_2026-11-18.dump` and `fix_dev_pre_m63_capture_2026-11-18.dump`, in `_migration/backups`.
- **Upgraded.** `-u cd_workflow_engine,cd_p03_portal` ran on fix_real and then fix_dev. Both exited 0 with no ERROR lines. On both databases `cd_workflow_engine` is now 19.0.1.1.0, with the 3 new models, 7 access rows, and the RSIM/WFX sequences.
- **Restarted.** The restart was shared with the M59/M60 sessions. 8069 (fix_real) has run as PID 69352 since 08:09:37, and 8090 (fix_dev) as PID 82848 since about 08:13. Both `/web/login` return 200, and the registry loaded cleanly.
- **Verified on fix_real.** All 4 M63 surfaces are served. The `web.assets_web` bundle was rebuilt (a4f00da to bde638f) and contains the simulation, register, intervention and scheduled forms and the events list.
- **Rules Never Simulated.** The KPI's own method reads 6 on fix_real. That is the 6 undated, in-force DoA rows.
- **AUT catalogue loaded (owner's OK, 18 Nov 08:45).** `action_load_register` put 60 AUT rows on fix_real (32 Odoo automated actions, 16 Airflow, 12 domain service; company 1000Fix Services Limited). A second run added 0. Backup taken first: `fix_real_pre_aut_register_2026-11-18.dump`.
- **Still open (business data).** The automation-rate tile is computed from the routine-work register (`fix.automation.register`), not from the AUT catalogue, and that register has 0 rows. The tile reads 0 until someone records each process area's monthly volume on page 7 ("Automation Register Entry").
