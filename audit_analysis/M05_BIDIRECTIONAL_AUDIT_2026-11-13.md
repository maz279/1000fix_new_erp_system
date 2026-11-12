# M05 Remote Support & MSP: bidirectional audit (13 Nov 2026)

**Scope:** every M05 screen, form, report, KPI, chip and sub-module page on port 8069 (fix_real), checked against the backend (`cd_msp_contract`, `controllers/a02/m05.py`). In the other direction, every backend model, field, action, report, cron, event, approval route and cross-module link checked against what the workspace exposes. Both checked against the module spec (`M05_Remote_Support_and_Managed_Services.md`: FR-RMS-*, BRU-RMS-01..13, T-01..13).

## Method (executable, not read-only)
1. **UI declaration:** the fragment `a02/m05.js` loaded as an ES module: 17 nav screens, 36 surfaces, all routes and chips. No dangling ids.
2. **UI → backend, live:** a probe called every list, form, pick list, report (with and without a period) and the KPI endpoint on 8069 exactly as the screens do, comparing requested columns and fields with what the server returned. Result: **36/36 served, 0 dropped columns, 0 errors.** Six form fields were found required by the model but not marked required (fixed).
3. **Backend → UI:** AST scan of every M05 model field and `action_*` method against every screen.
4. **Rules and flows:** spec rules mapped to code; approval routes checked against role holders on fix_real; cross-module consumers and crons checked on fix_real.

## Findings and what was done

### Defects in built functionality (fixed)
| # | Finding | Fix |
|---|---|---|
| D1 | Remote Resolution Rate, Alert-to-Ticket Conversion and SLA Credit Register declare a period, and the screen, PDF and email send it, but the reports **ignored it**: "October" showed all-time figures. | All three honour the period. Alerts are cut on Asia/Dhaka calendar days; credits on their service month. The backup log is now period-aware too. |
| D2 | Three reports (SLA by Client, Remote Resolution, Alert Conversion) had **no company filter**. | Every report and KPI is fenced to the user's companies. |
| D3 | Reports and KPIs read at most 300/500 records, so rates were **silently truncated**. | Counts use `search_count` over the whole set. |
| D4 | "Remote resolution" = resolved ÷ (ticketed or resolved), counting alerts resolved without a ticket as tickets. **It measured nothing.** | Now: resolved **without a service order** ÷ resolved. The report shows raised, resolved, remote, via order and open. The KPI uses the same definition. |
| D5 | SLA by Client averaged a month **with no SLA figure as 0 %**. | Unmeasured months are counted separately and kept out of the average; the MSP contract is named per row. |
| D6 | Open MSP Tickets KPI counted only acked/ticketed alerts, so a client's phoned-in ticket was not "open". | The KPI is the desk set (client reports plus ticketed alerts) not yet resolved. |
| D7 | Runbook "Log Execution with Evidence" sent no asset, so the run was recorded on the **first asset in scope**. An alert's execution was logged on a different device than the alert's. | A run is logged on the named asset, the alert's own asset, or the scope's only asset; otherwise it is refused. The asset must be in the runbook's scope and the alert on that asset. |
| D8 | Every logged execution was hard-coded **success**: a failed remediation could not be recorded (spec T-08 requires the outcome). `running` runs were never created, so `action_finish` was dead. | New `outcome` field. A failure needs a description and never resolves the alert. The log is immutable once written. |
| D9 | The runbook execution log (`fix.msp.runbook.run`) had **no screen**. | New **Runbook Executions** list and **Log Runbook Execution** form (sub-module 6). |
| D10 | Backup & Restore Test Log was a **"not built yet" placeholder**. | New `fix.msp.backup.job` (FR-RMS-039): job outcome, restore test, failures in a row. A failed or partial job raises one alert per plan. New **Backup Jobs** screen and **Record a Backup Job** form; the report reads them. |
| D11 | The Session Console offered "+ New", but a new session is not running and vanished from the console. | Console is read-only and points to Remote Sessions. |
| D12 | User-facing text with internal codes or false claims: "(FLAW-05.1)", "Msp Patch Policy", a note saying *"Every field here is the model's real field"*, an estate note promising serial and warranty fields that don't exist, a generic "Record Coverage" group. | Rewritten in business language. Patch Policies moved under Compliance. |
| D13 | Evidence the backend keeps but no screen showed: the Bengali report summary (DE-17), session protocol / linked service order / consent timestamps, credit manual flag / breaches / approved-at / applied-by, window closure, patch approved-on / deferred-until / tested-by, alert escalated-at, PIR date, policy approved-at. | Shown read-only on their forms and lists. |
| D14 | Six form fields required by the model were not marked required (session asset, technician, tool; change kind, type, risk). | Marked required. |

### Business rules
| Rule | Before | Now |
|---|---|---|
| BRU-RMS-01 consent before connection | enforced | unchanged |
| BRU-RMS-04 unmonitored asset = coverage gap within 24 h | **not built** | hourly `M05: report monitoring coverage gaps`: one major alert per silent asset, respecting maintenance windows |
| BRU-RMS-06 auto credits; manual needs CFO | enforced | unchanged |
| BRU-RMS-08 every change has a rollback plan | only **high-risk** changes | every change; a problem record is exempt |
| BRU-RMS-09 patch outside window needs approval | built behind a switch (off by default) | unchanged: switching it on is a business decision |
| BRU-RMS-02, 05, 07, 10, 11, 12 | not built | not built (see below) |

### Cross-module (verified on fix_real)
M08: entitlement and `contract.renewed` consumer. M17: device link for ticketing. M01: alert to service order and its outcome. M20: `msp.sla_credit_applied` consumer in `cd_settlement_ext`. M63: change, credit and patch-exception approvals. RMM collector: `ingest_telemetry`. All modules are installed and both M05 crons are active.

## Needs the owner (appointments, not code)
On fix_real today:
- **MSP CAB Member: 0 holders.** **MSP Change Manager: 0 holders.** No change, emergency change, maintenance window or estate-wide patch decision can be approved. The engine refuses with "No one can approve…".
- **MSP Engineer: only the System Administrator.** No staff user can record a reading, ticket, rule, runbook execution or backup job.
- MSP SLA Credit Approver: 3 holders (fine).

## Still not built (spec features without a model)
BRU-RMS-02 unattended access per contract, BRU-RMS-05 coverage-window SLA clocks, BRU-RMS-07 entitlement consumption and overage, BRU-RMS-10 recurring incidents linked to a problem record, BRU-RMS-11 client offboarding, BRU-RMS-12 recording retention. Also FR-RMS-036 service-review meetings, FR-RMS-020 major incidents, FR-RMS-049 client contact permissions, FR-RMS-040..046 cloud, DR and strategy lines.

## Evidence
- `cd_msp_contract/tests/test_m05_bidirectional_audit.py` pins every fix above (20 tests).
- On a private copy of fix_test: the full M05 suite passed **150/150, 0 skipped**, and the estate-wide page and sub-module guards (all 67 modules) are green.
- **Mutation check 3/3 killed.** Re-introducing high-risk-only rollback, first-asset execution, or a period-blind report each turns the suite red.
- **Live on 8069 after deploy (13 Nov 03:51):** 40/40 M05 surfaces served (lists, forms, pick lists, reports with and without a period, KPIs), 0 dropped columns, 0 errors.
- Deploy: backup `_migration/backups/fix_real_pre_m05_audit_deploy_2026-11-13.dump`, `-u cd_msp_contract` (19.0.3.2.0), then 8089 and 8069 restarted.
- Event payloads unchanged; only the three msp_* contracts' publisher lists were regenerated.
