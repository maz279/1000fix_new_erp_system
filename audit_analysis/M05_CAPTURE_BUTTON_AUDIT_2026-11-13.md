# M05 Remote Support & MSP: sub-module capture-button audit (13 Nov 2026)

**Reported:** not every M05 sub-module page has a relevant data-capture button.
**Measured against:** the module spec `1000fix_ERP_Module/03_Modules/A_Service_Delivery_and_Operations/M05_Remote_Support_and_Managed_Services.md` (§5 functional requirements, §10 entities), the M05 registry (10 sub-modules, 93 functions) and the code in `cd_msp_contract` and `cd_p03_portal/static/src/a02/m05.js`.
**Live data on fix_real (8069):** 0 MSP contracts, 0 assets, 0 alerts, 0 reports, 1 MSP Engineer. The buttons are the only way any M05 record can be entered.

## What each page offered before, and what the spec says it captures

| # | Sub-module | Button before | Spec | Finding |
|---|---|---|---|---|
| 1 | Remote Sessions | + New Remote Session | FR-RMS-001..007 | correct |
| 2 | Monitored Estate | + New Managed Estate Device | FR-RMS-008 asset onboarding | correct; the form hid the IP, MAC and OS fields the model has; "Forms" panel empty |
| 3 | Metrics & Health Scoring | **none** (`create: false`) | FR-RMS-010/011: agentless devices and metric collection | **gap**: the metrics (CPU, RAM, disk, uptime) were written only by the collector, so no reading could be entered |
| 4 | Alerting Engine | **+ New MSP Ticket** | FR-RMS-015 alert rules (P1) | **wrong button, missing feature**: the screen is "Alert Rules & Inbox", but no alert-rule model existed anywhere in the codebase |
| 5 | On-Call & Escalation | + New On-Call Shift | FR-RMS-017/038 | correct; "Forms" panel empty |
| 6 | Runbooks & Remediation | + New Runbook | FR-RMS-018 | correct; "Forms" panel empty |
| 7 | Patch Management | + New Patch Update | FR-RMS-021/022 | correct; "Forms" panel did not list Patch Update |
| 8 | MSP Service Desk | **none** (its list refused "+ New") | FR-RMS-026: tickets from phone, email, portal, chat (P1) | **gap**: a ticket could only come from a monitoring alert, and the model had no field saying where it came from |
| 9 | Client Reporting | **none** | FR-RMS-035 periodic service reports | **gap**: reports are generated from a contract; a second click made a duplicate report for the same month |
| 10 | Onboarding Projects | + MSP Contract | FR-RMS-047 | correct: the sub-module's record is the module's |

## What was built

**Backend (`cd_msp_contract`, new file `models/fix_msp_rules.py`; module 19.0.3.1.0):**
- `fix.msp.alert.rule`: a threshold on CPU, memory, free disk or uptime, above or below, with a severity, scoped to one MSP contract or to all. MSP Engineers write; everyone else reads. Company and operating-unit isolation rules are generated.
- `fix.monitored.asset.action_record_reading(...)`: an engineer's reading. It goes through the same alerting as the collector. The first unhealthy transition raises an alert, then every rule in scope is evaluated, one open alert per rule and asset (spec T-10). An approved, open maintenance window suppresses all of it. It needs the MSP Engineer role, refuses impossible values, and records who read it.
- `fix.msp.alert.source` (Monitoring / Phone / Email / Client Portal / Chat) and `rule_id` (guarded: only a reading sets it). New constraint: an alert's asset must belong to its own contract.
- `action_generate_monthly_report` now refuses a second report for the same contract and month (the nightly run already skipped it).

**Workspace (`m05.js`, `controllers/a02/m05.py`, generated `writable.py`):**
- #3 **+ Record a Health Reading**: pick the asset, enter the reading. The metrics are inputs only through the reading; the generic write still refuses them.
- #4 **+ Define an Alert Rule**, plus a new "Alert Rules" list screen.
- #8 **+ Log a Client Ticket**: the ticket form starts as a phone report. The desk now lists client reports and ticketed alerts, with Acknowledge, Create Service Order, Resolve and Escalate.
- #9 **+ Generate a Monthly Service Report**: pick the contract; the server computes the figures.
- The "Forms" panel is filled on all ten pages. The estate form shows IP, MAC and OS.

## Evidence
- `cd_msp_contract/tests/test_m05_submodule_capture.py` runs the real `fregCreate` rule over the registry for all ten pages. It then saves each capture through the real controller as a non-admin MSP Engineer: rule, reading (raised, de-duplicated, out of scope, offline, window-suppressed, refused), client ticket landing on the desk, cross-contract ticket refused, forged rule link refused, monthly report once.
- The estate-wide guards `test_submodule_create_button.py` and `test_estate_module_pages.py` pass for all 67 modules.
- Click check on a disposable clone (`fix_m05chk`, port 8098): every M05 page renders its button.

## Not built (spec items with no model yet, outside "a button per page")
- FR-RMS-036 service-review meetings (`fix.service.review`): the "Client Service Reviews" screen lists the monthly reports.
- FR-RMS-047/048 onboarding and offboarding projects: the MSP contract is the onboarding record today.
- FR-RMS-020 major-incident declaration, FR-RMS-049 client contact permissions, FR-RMS-039..043 backup oversight and DR plans.
