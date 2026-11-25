# M01 Service Requests & Orders: data-capture button audit

**Date:** 17 Nov 2026 · **Branch:** `fix/m01-capture-buttons` (worktree `m01cap-wt`, from c5feece6) · **Status:** built and tested on a private clone (`fix_test_m01`); not committed, not deployed

## 1. The question

The M01 workspace has 13 sub-module pages (the Function Register). Not every page showed a button for recording data. Which pages should have one, what should it open, and what is missing?

## 2. What the spec says

Sources:

- `1000fix_ERP_Module/03_Modules/A_Service_Delivery_and_Operations/M01_Service_Request_and_Order_Management.md`: §3 scope, §5 requirements, §10 owned entities, §3.2/§3.3 ownership
- `05_Cross_Cutting_Specifications/05-01_Feature_and_Function_Register.md` (FR-SRM-001 … 088, 70 live requirements)

The 13 pages map one-to-one onto the 15 in-scope capabilities of §3.1. The spec also says who owns each record:

| Record | Owner | What M01 does with it |
|---|---|---|
| Service order, hold, rework link, repair warranty, service report | M01 | creates it |
| Diagnostic template (decision tree), SLA policy, **escalation rule** (`fix.escalation.rule`) | M01 | masters it |
| Fault code taxonomy | M37 defines it (§3.3) | assigns it |
| Warranty register | M09 | reads it for entitlement |
| Field work order / workshop repair order | M02 / M31 | creates it through the hand-off (FR-SRM-031) |

So a page should capture its own record. Where another module owns the record, the page should open **that module's** form, as M02 already does with M15 and M59.

## 3. What the code had (HEAD c5feece6)

Evaluated with the engine's own `fregCreate` / `fregPanels`, with the defects confirmed in the code:

| # | Page | Button | Chips | Defect |
|---|---|---|---|---|
| 1 | Omni-Channel Intake | + New Service Order | New Service Order | none |
| 2 | Lifecycle State Machine | + New Service Order | New Service Order | none (transitions are row actions) |
| 3 | Entitlement Evaluation & SLA Clock | — | — | **Nothing.** M09's warranty register form exists and was not reachable from here. |
| 4 | Complaint & Fault Taxonomy | — | — | **Nothing.** The list was `create: false`. M37's Fault Code form exists and was not reachable from here. |
| 5 | Diagnostic Templates | — | — | **Nothing, anywhere.** FR-SRM-021 (P0) requires the trees to be maintained, but no form existed for `fix.diagnostic.node` in any module. Trees could only be seeded. |
| 6 | Estimate & Approval | + New Diagnostic Estimate Request | yes | none |
| 7 | Assignment & Field Dispatch Hand-off | — | — | **Nothing.** The hand-off (`action_create_field_order`) was only a row action on the order book (FR-SRM-031, P0). |
| 8 | SLA Policy, Clock & Escalations | — | SLA Item only | **No SLA policy form anywhere** (FR-SRM-047, P0). The "Escalation Rules" screen listed the **policies themselves**: no escalation rule record existed (FR-SRM-049, P0, spec entity `fix.escalation.rule`). An SLA escalated once, at breach, to the branch Service Supervisor, with nothing to acknowledge. |
| 9 | Hold & Release | + Place Order on Hold | yes | none |
| 10 | QC & Rework | + New QC Checklist Inspection | yes | none |
| 11 | Service Reports & Repair Warranty | — | — | **Nothing.** Issuing the repair warranty (FR-SRM-045, P0) was a row button on one list only. |
| 12 | Operations Boards & WIP | — | — | correct: this is an analysis |
| 13 | API & Domain Events | — | — | correct: an event log, fed by a report |

Six of the 13 pages (3, 4, 5, 7, 8, 11) had no relevant capture.

## 4. What was changed

| # | Page | Capture now | How |
|---|---|---|---|
| 3 | Entitlement | **+ New Warranty Register Entry**, chip | Opens M09's form (owner). |
| 4 | Fault Taxonomy | **+ New Fault Code**, chip; the list's + New; a row opens the form | Opens M37's form (owner); it also carries the brand claim codes. |
| 5 | Diagnostic Templates | **+ New Diagnostic Tree Node**, chip; list + New | **New** form `M01-form-diag-node`. A question and its answers are captured together (answers grid on `children_ids`). The model's rule still applies: an end-of-path node needs a fault code, and a question cannot have one. |
| 7 | Dispatch Hand-off | **+ Hand Off to Field Dispatch**; chips *Receive Device into Workshop* (M31) and *Technician Work Order* (M02) | **New** form `M01-form-dispatch`. Step 1 picks an on-site, booked-in order with no field order. Save runs the order's own `action_create_field_order`, which keeps its checks: dispatch zone, no second live field order, priority mapping. |
| 8 | SLA & Escalations | **+ New SLA Policy**; chips *SLA Policy*, *SLA Item*, *Escalation Rule*; new screen **Escalations Raised** with **Acknowledge** | **New** form `M01-form-sla-policy`, with its SLA items as a grid. **New models** `fix.escalation.rule` and `fix.escalation.event` (see §5). "Escalation Rules" now lists rules. |
| 11 | Repair Warranty | **+ Issue Repair Warranty**, chip | **New** form `M01-form-rwty`. Step 1 picks a delivered or closed order with no warranty. Save runs `action_issue_repair_warranty`: issued once, recorded on the device history. |
| 12, 13 | — | none | Unchanged; the page says "No data-entry form: these records are not typed in here." |

## 5. The escalation matrix (new)

Code: `cd_service_order/models/fix_sla_escalation.py`, module version 19.0.2.1.0 → 19.0.2.2.0.

- **Rule** (`fix.escalation.rule`). Fields: policy, optional KPI, level (1–100 % of the target in business time, matching the spec's 50/75/90/100 matrix), role (`res.groups`), acknowledgement required, instruction.
  - One role is told once per level.
  - Everyone can read rules. **Only Service Supervisors can create, change or delete them** (ACL).
- **Raised escalation** (`fix.escalation.event`). The existing 15-minute SLA cron (`cron_flag_breaches`) raises it after its breach pass.
  - It fires **once per level per clock series**, so a pause/resume (which creates a successor clock) does not escalate the same level again.
  - It skips paused clocks and delivered, closed or cancelled orders.
  - It gives each role holder in the order's branch a to-do, and publishes `sla.escalated` (contract registered).
  - With no role holder in the branch it is recorded as *No Role Holder In Branch*, not lost.
  - Nobody can type or edit one (ACL plus model guard). It moves only by **Acknowledge**, by a notified person or a Service Supervisor. Acknowledging closes the to-do and notes it on the order.

## 6. Evidence

| Check | Result |
|---|---|
| New guard `cd_p03_portal/tests/test_m01_capture_buttons.py` | **27/27** on the branch; **9/27 on HEAD**. Exactly pages 3/4/5/7/8/11 and the missing registers fail. |
| Live ORM `cd_service_order/tests/test_m01_sla_escalation.py` on `fix_test_m01` | **16/16** |
| Mutation check (10 defects re-introduced one at a time) | **9 killed.** The survivor ("escalation typable") is equivalent: the ACL still refuses the create. |
| Existing M01 page tests (`test_m01_submodule_pages.py`, `test_submodule_create_button.py`) | Updated to the new intended behaviour (6 assertions). 2 failures remain, and both also fail on untouched HEAD: M50 statement-line `pick`, M19/M30 declared-module rows. Not M01. |
| `-u all` on the clone | exit 0, 0 errors |
| Server probe on a private server (8093) | 6 lists, 0 columns dropped. Policy and items, rule, and node and answers all saved through `/p03/model/write`. Duplicate level, terminal node without a code, and a typed escalation were each refused with a business message. |
| UI walk, all 13 pages | Each page shows the button and chips in §4. New forms render with their tabs and grids. No console errors, no M01 server-log errors. |
| Regression (cd_service_order, cd_field_service, cd_workshop, cd_p03_portal) on `fix_test_m01` | **5,263 passed, 292 skipped, 3 failed.** All 3 also fail on untouched HEAD: M50 chip registry, M50 statement-line `pick`, M19/M30 declared-module rows. |
| ruff 0.8.4 check + format | clean |

**Not covered:** the pick-then-run step of *Hand Off to Field Dispatch* and *Issue Repair Warranty* was seen only in its empty state. The clone has no qualifying order, and fix_real has 0 service orders. The actions themselves are pre-existing and covered by the existing order tests.

## 7. Left open (owner or follow-up)

- **SLA policy and item edits are open to every internal user.** This is the pre-existing ACL `base.group_user` 1,1,1,0, which the spec limits to R05/R06. Escalation rules are restricted; policies were left as they are so this capture change does not alter existing access. Recommend a follow-up.
- **Diagnostic trees have no device category, brand or version scoping** (FR-SRM-021). The model is versionless by design (work orders store the node they reached), and nothing reads scoping fields yet. Adding them would create dead fields.
- **No escalation rules exist on fix_real.** Someone must decide who is told at 50, 75, 90 and 100 %. Until then, behaviour is unchanged: the single breach to-do to the Service Supervisor.

## 8. Deployment

**DEPLOYED 18 Nov 2026 (01:03 local), on user approval.**

1. **Commit.** 821559bc on `fix/a03-live-data-and-pending-work`, landed as a fast-forward from a520b717 (M56) with a compare-and-swap ref update. The shared checkout was synced and is clean. Not pushed.
   - The rebase merged a peer's identical 541→542 bump of the event registry count. Corrected to 543 (543 entries).
2. **Backups.** `_migration/backups/fix_real_pre_m01_capture_2026-11-18.dump` (50.2 MB) and `fix_dev_pre_m01_capture_2026-11-18.dump` (45.7 MB).
3. **Upgrade.** `-u cd_service_order,cd_p03_portal` on fix_real and fix_dev: exit 0, 0 errors. Both are now at cd_service_order 19.0.2.2.0, with both escalation models and 3 access rules.
   - The version-gap check over every `cd_` module was clean on both databases before the restart.
4. **Restart.**
   - 8069 (fix_real): new server PID 82916, login 200, 155 modules loaded, 0 errors. The supervisor loop was caught by the process match and stopped too; the parent watchdog relaunched it at once (now PID 35296).
   - 8090 (fix_dev): new server PID 3304 under the same supervisor (37700), login 200, 151 modules, 0 errors.
5. **Live bundle.** Both servers serve bundle b22b767, which contains the five new forms, the Escalations Raised list, the page mappings to M09 and M37, and the escalation-rule list.

fix_real holds 0 service orders and 0 escalation rules. The pages work, but the escalation matrix stays inactive until someone defines the rules (§7).
