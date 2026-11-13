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
| BRU-RMS-09 patch outside window needs approval | built behind a switch, OFF on fix_real | **switched ON 13 Nov (owner decision)**: an install outside an open, approved window needs a routed exception. With no CAB Member or Change Manager appointed, neither a window nor an exception can be approved, so **no patch can be installed until those roles are filled** (fix_real has 0 patch records today) |
| BRU-RMS-03 credentials never in a ticket or note | not built | free text on alerts and tickets, sessions, runbooks and their runs, changes and backup jobs refuses credential-shaped text (`password: …`, `pwd=…`, `API key = …`, `token: …`) and points to the vault. Ordinary sentences ("password reset done") pass |
| BRU-RMS-13 a client sees only its own estate | internal company and operating-unit isolation rules on every M05 model | unchanged. No client portal (P04) access to M05 exists yet, so no client can see any MSP record |
| BRU-RMS-02 unattended access only where the contract grants it | not built | contract flag `Unattended Access Granted`; a session's access mode is attended unless it is set; refused at create and at start |
| BRU-RMS-05 SLA clocks follow the coverage window | not built (clock hours always) | contract `SLA Coverage Window`: 24 × 7 or Sun–Thu 09:00–18:00 Dhaka. Breach deadlines, monthly attainment and credits use it (public holidays not yet in the calendar) |
| BRU-RMS-07 overage never absorbed | not built | enrolling a device beyond the covered count is refused until the count is raised (an uplift, billed per device); the count cannot drop below the estate; a contract with no count bills every enrolled device |
| BRU-RMS-10 recurring incident linked to a problem | not built | the 3rd alert on an asset within 30 days (both values are settings) cannot be resolved until it is linked to a problem record; a runbook logs its run but leaves such an alert open |
| BRU-RMS-11 offboarding evidenced | not built | MSP Contracts: Start Offboarding, then Record Agent Removal per asset (evidence) and Record Access Revoked (evidence), then Complete Offboarding. It is refused while any agent remains or access is not revoked. No new asset or session once offboarding starts |
| BRU-RMS-12 recording retention, access logged | not built | contract `Recording Retention (days)` (365 by default; 0 = contract life); a daily job purges expired references (logged); **Open Recording** shows the reference and logs who opened it |

### Cross-module (verified on fix_real)
M08: entitlement and `contract.renewed` consumer. M17: device link for ticketing. M01: alert to service order and its outcome. M20: `msp.sla_credit_applied` consumer in `cd_settlement_ext`. M63: change, credit and patch-exception approvals. RMM collector: `ingest_telemetry`. All modules are installed and both M05 crons are active.

## Needs the owner (appointments, not code)
On fix_real today:
- **MSP CAB Member: 0 holders.** **MSP Change Manager: 0 holders.** No change, emergency change, maintenance window or estate-wide patch decision can be approved. The engine refuses with "No one can approve…".
- **MSP Engineer: only the System Administrator.** No staff user can record a reading, ticket, rule, runbook execution or backup job.
- MSP SLA Credit Approver: 3 holders (fine).

The owner decided on 13 Nov to **leave these roles unassigned for now**. The natural pool is the Corporate Service department (15 staff); the spec makes the Corporate Services Head the rule owner.

## Spec features built after the audit (13 Nov, owner decision "build all now")
| Spec | Built |
|---|---|
| FR-RMS-049 client contacts & permissions | **Client Contacts** screen and form: role, may raise tickets / approve changes / receive consent codes, escalation order and channel. A contact must belong to the client. A client-reported ticket must name a contact allowed to raise tickets; once contacts exist, only a permitted contact can consent to a remote session |
| FR-RMS-020 major incidents | **Major Incidents**: declare (engineer), Notify All Client Contacts (posts to every registered contact), Resolve (written resolution), Post-Incident Review by someone other than the declarer, which closes it. The workflow fields are guarded; alerts and tickets link to the incident |
| FR-RMS-036 service review meetings | **Service Review Meetings**: attendees, the report discussed (must be the contract's own), decisions, an actions grid, next review. It closes only when every action is done. The monthly reports screen is renamed **Monthly Service Reports** |
| FR-RMS-040 cloud subscriptions | **Cloud Subscriptions**: provider, plan, seats and seats in use, cost per seat, monthly cost, renewal date, a 30-day renewal flag (searchable) |
| FR-RMS-042/043 DR/BC plans & tests | **DR / BC Plans** (scope, RTO, RPO, test interval, last test, next due) and **DR Tests** (achieved RTO/RPO, evidence, tested by). A test is **Passed** only if both targets were met; it is evidence once recorded |
| FR-RMS-045/046 strategy & technology roadmap | **Technology Roadmap**: refresh, recommendation or deliverable per client; accept, decline, deliver. An accepted item becomes **one** M07 sales opportunity |

Every business rule BRU-RMS-01..13 has its control (BRU-RMS-09 switch on; BRU-RMS-13 holds trivially until a client portal exposes M05). Still outside M05's build: FR-RMS-039's backup data feed from M06/M48 (backup jobs are recorded by engineers), public holidays in the business-hours SLA calendar, and FR-RMS-041/044/052 (cloud cost optimisation, security-posture deliverable, licence compliance reporting). No screen promises any of them.

## FR traceability: all 62 M05 requirements (13 Nov, after the builds)
The spec delivers M05 across four layers: L2 OCA helpdesk (14 %), **L4 standalone open-source systems — Wazuh/osquery, SNMP collector, MeshCentral/RustDesk, TimescaleDB, Grafana (34 %)**, L5 custom Odoo (50 %), and an optional L6 commercial RMM agent (2 %). L4 items are integrations with those systems, not Odoo screens; items owned by another module are marked with it.

Status: **Built** = screens + rules + tests in M05 · **Partial** = the M05 side is built, a named piece is not · **Not built** · **Other layer/module** = delivered outside cd_msp_contract.

| FR | Requirement | Pri | Status | Where / what is missing |
|---|---|:-:|---|---|
| 001 | Session initiation from a ticket, one-time code | P1 | Built | Remote Sessions; consent code to the client contact; session links its service order |
| 002 | Consent before any connection | P0 | Built | BRU-01: OTP verified before Start |
| 003 | Attended and unattended access | P1 | Built | BRU-02 contract grant |
| 004 | Session recording, retention | P1 | Partial | reference, retention purge and logged opening built; the recording itself is MeshCentral/RustDesk (L4) |
| 005 | Session metering and billing | P1 | Partial | duration is computed; billing a session by entitlement is not built |
| 006 | File transfer control and malware scan | P1 | Not built | needs the L4 remote-access tool's transfer log |
| 007 | Session handover between engineers | P2 | Not built | L4 tool feature |
| 008 | Asset onboarding | P1 | Built | Estate & Agents, device cap (BRU-07) |
| 009 | Agent deployment | P1 | Other layer | L4/L6 agent; M05 keeps the agent id and health |
| 010 | Agentless monitoring | P1 | Partial | engineer health readings built; the SNMP/ICMP collector is L4 |
| 011 | Metric collection as time series | P1 | Partial | latest metrics per asset; the time-series store is L4 (TimescaleDB) |
| 012 | Software inventory | P2 | Not built | L4 (osquery) |
| 013 | Configuration baseline and drift | P2 | Not built | — |
| 014 | Health score | P2 | Built | Health Scoring report |
| 015 | Alert rules | P1 | Built | Alert Rules |
| 016 | Alert-to-ticket, de-duplication | P1 | Built | one open alert per rule; Create Service Order |
| 017 | Escalation through an on-call rota | P1 | Built | On-Call Rota, Escalate |
| 018 | Runbook automation, recorded | P2 | Built | Runbook Executions with outcome |
| 019 | Maintenance windows | P1 | Built | CAB approval, alert suppression |
| 020 | Major incident handling | P2 | Built | Major Incidents |
| 021 | Patch inventory | P2 | Built | Patch Management |
| 022 | Patch scheduling, window, approval | P2 | Built | BRU-09 on; ring roll-out and automatic rollback are L4 |
| 023 | Patch compliance reporting | P2 | Built | Patch Compliance Report |
| 024 | Endpoint protection oversight | P2 | Not built | L4 (Wazuh) |
| 025 | Vulnerability reporting | P3 | Not built | L4 (Wazuh) |
| 026 | Client ticketing by channel | P1 | Built | Log a Client Ticket with source and contact; the portal channel is P04 |
| 027 | Classification: service, urgency, impact → priority | P1 | Not built | tickets carry severity only |
| 028 | Contractual SLA | P1 | Partial | resolution SLA with coverage window and holidays built; the response-time SLA is not |
| 029 | Knowledge base | P2 | Other module | M61 |
| 030 | Problem management | P2 | Built | problem records, BRU-10 link |
| 031 | Change management | P2 | Built | CAB route, rollback (BRU-08) |
| 032 | Field escalation to M02 | P1 | Partial | a ticket raises an M01 service order; dispatch is M02's |
| 033 | Entitlement consumption | P1 | Partial | covered devices tracked; hours and incident allowances are not |
| 034 | Overage: bill or uplift | P1 | Partial | device overage refused until uplift (BRU-07); hours/incident overage not |
| 035 | Service reports | P1 | Built | Monthly Service Reports, bilingual |
| 036 | Service review meetings | P2 | Built | Service Review Meetings |
| 037 | SLA credits to M20 | P1 | Built | DOFA approval, M20 consumer |
| 038 | 24/7 coverage, out-of-hours cost recovery | P1 | Partial | coverage window and rota built; out-of-hours charging not |
| 039 | Backup service oversight | P2 | Built | Backup Jobs (engineer-recorded); an automatic feed from M06/M48 is not |
| 040 | Cloud subscriptions | P2 | Built | Cloud Subscriptions |
| 041 | Cloud cost reporting | P3 | Built | Cloud Cost & Optimisation |
| 042 | DR/BC plan register | P2 | Built | DR / BC Plans |
| 043 | DR test tracking | P2 | Built | DR Tests |
| 044 | Security posture reporting | P2 | Built | Security Posture (no endpoint-protection data: FR-024) |
| 045 | IT strategy deliverables | P3 | Built | Technology Roadmap |
| 046 | Technology roadmap feeding sales | P3 | Built | opportunity in M07 |
| 047 | Client onboarding project | P1 | Other module | project in M67; M05 has the contract and estate |
| 048 | Client offboarding | P1 | Built | BRU-11 |
| 049 | Client contact management | P1 | Built | Client Contacts |
| 050 | Client portal scope | P1 | Other module | P04 portal |
| 051 | Asset discovery | P2 | Not built | L4 |
| 052 | Licence compliance | P3 | Built | Licence Compliance (tracked subscriptions; device software needs FR-012) |
| 053 | Client asset warranty tracking | P2 | Not built | — |
| 054 | Automation library with approval | P2 | Partial | runbooks built; approval and versioning of scripts not |
| 055 | Scheduled maintenance tasks | P2 | Not built | L4 |
| 056 | Agent health, coverage gaps | P1 | Built | BRU-04 hourly check |
| 057 | Alert noise reduction | P1 | Partial | per-rule de-duplication and window suppression; tuning and correlation not |
| 058 | Client satisfaction | P1 | Not built | — |
| 059 | Profitability per client | P2 | Not built | — |
| 060 | Capacity planning | P2 | Not built | — |
| 061 | MSP analytics | P1 | Partial | 6 KPIs and 9 reports |
| 062 | Session from the contact centre | P1 | Other module | M27 launches it |

**Count (62):** Built 32 · Partial 12 · Not built 13 · Other layer or module 5 (009 L4/L6 agent, 029 M61, 047 M67, 050 P04, 062 M27).
**Not built in M05 at P1:** 006 file transfer control, 027 ticket classification and priority, 058 client satisfaction. Everything else unbuilt is P2/P3 or belongs to an L4 system or another module.

## Evidence
- `cd_msp_contract/tests/test_m05_bidirectional_audit.py` pins every fix above (20 tests).
- On a private copy of fix_test: the full M05 suite passed **150/150, 0 skipped**, and the estate-wide page and sub-module guards (all 67 modules) are green.
- **Mutation check 3/3 killed.** Re-introducing high-risk-only rollback, first-asset execution, or a period-blind report each turns the suite red.
- **Live on 8069 after deploy (13 Nov 03:51):** 40/40 M05 surfaces served (lists, forms, pick lists, reports with and without a period, KPIs), 0 dropped columns, 0 errors.
- Deploy: backup `_migration/backups/fix_real_pre_m05_audit_deploy_2026-11-13.dump`, `-u cd_msp_contract` (19.0.3.2.0), then 8089 and 8069 restarted.
- Event payloads unchanged; only the three msp_* contracts' publisher lists were regenerated.
- **BRU-RMS-03 (third deploy):** credential guard upgraded and live after 8089 and 8069 restarted; a ticket message containing "admin password: …" is refused on 8069 and nothing is saved; probe 40/40 on both servers. Backup `fix_real_pre_m05_bru03_deploy_2026-11-13.dump`.
- **Business rules (second deploy, 13 Nov 06:13):** `cd_msp_contract/tests/test_m05_business_rules.py` 13/13. The full M05 suite passes 161 behaviour tests; the two contract-form layout tests were updated for the new Lifecycle tab and pass 6/6. The estate and capture guards pass 635/635. Backup `fix_real_pre_m05_bru_deploy_2026-11-13.dump`, `-u cd_msp_contract` 19.0.3.3.0 (all 15 new columns present). Live probe on 8069 (pid started 06:13) and 8089: **40/40, 0 problems**; the new actions are whitelisted.
- **Spec features (fourth deploy, 13 Nov):** `test_m05_services.py` 10/10; on a fix_test copy the full M05 suite plus the estate-wide page and sub-module guards pass **790/790, 0 failed, 0 skipped**. Backup `fix_real_pre_m05_services_deploy_2026-11-13.dump`, `-u cd_msp_contract` 19.0.3.4.0 (8 new tables). **Live probe 54/54 M05 surfaces on 8069 and 8089, 0 problems.**
- **Mutation check of the rules built after the audit, run in memory** (a pytest plugin that switches each rule off for that test process only, so the shared code on disk never changed): business rules BRU-02, 03, 05, 07, 10, 11, 12 **7/7 killed**; features FR-049, 020, 036, 043, 046 **5/5 killed**. Each failure was the rule's own assertion ("did not raise"), not a crash.
- **Holiday calendar and the FR-041/044/052 reports (fifth deploy, 13 Nov):** live via `-u cd_msp_contract` (user-approved after the 13:09 peer restart had loaded the new column's code). Backup `fix_real_pre_m05_holiday_deploy_2026-11-13.dump`. Tested from an isolated worktree (peers' commit hooks were stashing the shared tree mid-run): M05 suite plus estate guards **793 passed, 0 failed, 0 skipped** on a private fix_test copy. The holiday test now builds its own calendar and proves the contract deadline moves past a closure. Live probe **57/57** M05 surfaces.
