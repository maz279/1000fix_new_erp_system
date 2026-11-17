# M47 Facility, Branch Infrastructure & Workplace — Sub-Module Capture Audit (2026-11-17)

**Trigger.** The user observed that not every M47 sub-module page has a relevant data-capture button.

**Sources**
- Spec: `1000fix_ERP_Module/03_Modules/F_Asset_Equipment_and_Facilities/M47_Facility_Branch_Infrastructure_and_Workplace.md`. Sections used: §3 scope, §5 FR-FAC-001…044, §8 lifecycles, §9 BRU-FAC-01…21, §10.1 owned entities (27), §11 automations, §12.3 events, §13 roles and segregation of duties, §14 reports.
- Code:
  - `cd_p03_portal/static/src/a07/m47.js` (the page registry: 10 sub-module pages);
  - `cd_p03_portal/controllers/a07/m47.py` (surfaces, packs, KPIs);
  - `cd_facility/models/fix_facility.py`, `fix_facility_ops.py`, `fix_facility_compliance.py` (the 14 M47 models).
- Live data: fix_real holds **no M47 record of any kind** (0 sites, leases, licences, utilities, assets, PM jobs, work orders, safety items, incidents, projects, conditions, risk exceptions, demands). Role holders: Facility Manager 4, Branch Operations Lead 42, Operations Director 3.

## 1. What was there (HEAD ea2fdda1)

The pages were evaluated with the engine's own `fregCreate` / `fregPanels` in node, which is how the browser decides what a page shows.

| # | Page | "+ New" | Form chips | Defect |
|---|---|---|---|---|
| 1 | Site Register | Site | Site | Lists **Occupancy & Condition** with no capture (its form existed, unreachable). **No site-type profile** (FR-FAC-002/017 P0): the compliance set a site type requires was one estate-wide parameter, and the licence-gap figures said so ("no site-type requirement is recorded"). |
| 2 | Lease Administration | Lease | Lease | Only the renewal-notice deadline and the end date were dated. **A rent review, break option, deposit return or landlord obligation had no record, owner or decision** (FR-FAC-009/010 P0). The rent schedule, IFRS 16 extracts and remeasurement items sat on no page. |
| 3 | Statutory Compliance | Licence | Licence | **No renewal record** (FR-FAC-021 P0): a renewal was a new licence row; who was responsible, the documents, the fee challan, the inspection and the cost were recorded nowhere. A licence held no issuing authority, fee or responsible person (FR-FAC-016). Signage and generator permits (§3.1 #6) were not licence types. The operating-risk exceptions sat on no page. |
| 4 | **Utilities** | Utility | **none** | The form was titled "Utility Account" but was a monthly bill. **No supply account** (FR-FAC-038 P0): provider account, meter, tariff, billing cycle held nowhere; a site with two meters could not bill both in one month. |
| 5 | **Infrastructure Assets** | Asset | **none** | **No outage record** (FR-FAC-027 P0): branch operating hours lost to a failed building service were unknown. No make, model, capacity or expected life (FR-FAC-024). The asset finance requests sat on no page. |
| 6 | **Building PM** | PM Job | **none** | **No generator / UPS test regime** (FR-FAC-026 P0): load test, run hours, fuel and battery were recorded nowhere, and a missed test escalated to nobody (BRU-FAC-10, AUT-FAC-11). |
| 7 | Work Orders | Work Order | Work Order | A request had no photograph and completion no evidence file (FR-FAC-031/034: only text). The AP cost entries sat on no page. |
| 8 | Safety & Security | Safety Inspection | Safety Inspection | Lists **Security & Incidents** with no capture. The hand-off problems (injuries waiting for an HSE case) sat on no page. |
| 9 | **Open / Close Projects** | Project | **none** | |
| 10 | Maintenance Demand Queue | none | none | Correct by design (system queue), but its form did not say so. |

Also: three existing forms of more than 15 fields had no tabs (utility bill, AP cost entry, asset finance request), against the AGENTS.md multi-tab rule.

The new guard (`test_m47_capture_buttons.py`) run against HEAD: **24 of 48 tests fail.**

## 2. What was built

### Backend — `cd_facility` 19.0.0.2.0, new file `models/fix_facility_capture.py`

| Page | Record | What it does | Controls |
|---|---|---|---|
| 1 | `fix.site.type.profile` (FR-FAC-002/017, BRU-FAC-01) | What a site of each type must hold: every site the trade licence, plus fire, health, environmental, signage and generator permits as ticked. | Set by a Branch Operations Lead; one profile per site type. **The readiness gate asks for exactly the profile's licences**, and the Licence Compliance / Critical-Date / KPI gap figures use the same set. A type with no profile keeps the estate default (`cd_facility.readiness_licence_types` for the gate, trade only for the gaps). |
| 2 | `fix.site.lease.event` (FR-FAC-009/010, AUT-FAC-04) | A dated obligation of a lease: rent review, break option, deposit return, landlord obligation, other. Owner, due date, amount, what the lease says. | Recorded by a Facility Manager on a lease that is not terminated, never before its start; an obligation says what it is. **Alerted at 90/60/30/15/7 days and once when it passes** (daily job, idempotent; re-dating restarts it) through `lease.critical_date_due` to the M47 Alerts screen. Listed on Critical-Date Control. **A rent review or break option is the CFO's decision** (DOFA Tier 4, exercise or not); an obligation is met by its owner or a Branch Operations Lead; **nobody decides an event they recorded**. Frozen once decided. |
| 3 | `fix.site.licence.renewal` (FR-FAC-021, BRU-FAC-03, AUT-FAC-02) | One renewal from initiation to the new licence: responsible person, issuing authority, documents assembled, fee challan, government fee, agent/inspection cost, late penalty with reason, inspection, receipt scan. | Opened by a Facility Manager; one in progress per licence; not at a closed site. **A trade licence renewal is neither opened nor submitted while the site's fire licence is expired.** Submit needs the documents and, for a fee, its challan. **Complete only on a new licence of the same site and type, current, running later than the old one, with its scan.** A renewal that paid a penalty is completed by someone other than its responsible person (§13). Frozen once completed; never deleted. Completed renewals count in **Cost per Site** (new Licence Renewals column). |
| 3 | `fix.site.licence` + authority, fee, responsible | FR-FAC-016: the issuing authority, the licence fee and who renews it. Signage and generator / fuel-storage permits are licence types. | **§13 SoD:** the licence's responsible person and the responsible person of any of its renewals may not decide the operating-risk exception its lapse raises (added to the existing recorder / accountable-manager rule). |
| 4 | `fix.site.utility.account` (FR-FAC-038) | The supply account: provider, account number, meter, tariff, billing cycle, connection capacity. | Registered and closed (with a reason) by a Facility Manager. The account number is unique per provider and utility (case-blind). Site, utility, provider and number are frozen: a new connection is a new account. |
| 4 | `fix.site.utility` + account | A bill names its account (meter). | A site with one active account of the utility has it filled in; with several, the bill must say which. **One bill per account and month**, so a site with two meters bills both (it could not before); a bill with no account keeps the old one-per-site-type-month rule. A closed account bills nothing after its closing month. The form is now "Utility Bill" and tabbed (Bill / Anomaly Review & Payment). |
| 5 | `fix.site.outage` (FR-FAC-027, AUT-FAC-12) | A building service that stopped: service, failed asset, start, cause, whether the branch could not operate, workaround, repair work order. | Recorded by anyone at the branch (spec §13 R06/R08). The asset and work order must be the site's; no start in the future. **End Outage** (a typed wall-clock time, Dhaka) computes the duration and, for a stopped branch, the **operating hours lost**; publishes `site.outage` (M04/M31). Frozen once ended. Feeds the new **Infrastructure Availability** report. |
| 5 | `fix.site.asset` + identity | Make, model, capacity, expected life (FR-FAC-024); the last generator/UPS test and the next due. | The asset form is tabbed (Asset / Status & Tests). |
| 6 | `fix.site.power.test` (FR-FAC-026, BRU-FAC-10, AUT-FAC-11) | A generator or UPS test: load test, no-load run, battery check, fuel check; result, hour meter, load, duration, fuel level, battery condition, finding. | Recorded by the branch. Only a generator or UPS; a UPS takes no fuel or run test; no test in the future; **the hour meter never goes back**; a failure says what failed and **raises a corrective facility work order** at an operational site. A test is frozen once recorded. **A generator or UPS in service whose test is overdue escalates to the Operations Director once per due date** (daily job; new `site.power_test_overdue` event routed by the alert spine). The interval is `cd_facility.power_test_interval_days`, default **30 days: a default the business must confirm** (the spec gives none). |
| 7 | `fix.facility.work.order` + photo, evidence file | A request carries a photograph of the problem; completion an evidence file beside the evidence text (FR-FAC-031/034). | The evidence file is frozen with the rest of the completion evidence once the work is completed. |

Also:
- ACLs: nobody deletes any new record. A plain employee reads the profile, events, renewals and accounts and records outages and tests.
- Company and operating-unit record rules through the site for all five site-scoped registers (`fix_facility_scope_rules.xml`).
- Five sequences (SLREN/, SLEV/, SUACC/, SOUT/, SPWT/) and two daily jobs (lease events, missed power tests).
- `cd_asset_workorder_spine` 19.0.0.3.1: `site.power_test_overdue` → M47 Alerts, role Operations Director.
- Event contracts: `site.outage` and `site.power_test_overdue` registered (`contracts/events`, registry 535); `lease.critical_date_due` re-derived for its second publisher.

### Workspace — `m47.js`, `controllers/a07/m47.py`, `writable.py`

- Six new list screens, each labelled in the navigation, with their actions served: Site Type Profiles, Lease Critical Events, Licence Renewals, Utility Accounts, Infrastructure Outages, Generator / UPS Tests.
- Six new forms; the renewal and power-test forms are tabbed. The utility bill, asset, AP cost entry and asset finance request forms are now tabbed (AGENTS.md: more than 15 fields).
- The demand form says it is raised by its source module (`create: false` with a pointer to the work order).
- New report pack **Infrastructure Availability** (outages, hours down, branch operating hours lost and failed power tests per site, last 90 days). Critical-Date Control lists open lease events; Cost per Site adds licence renewals; the licence-gap figures follow the profile.
- Pickers: a renewal's licence among unsuspended licences and its renewed licence among valid ones; a lease event's lease among active leases; responsible people among internal users; a power test's asset among generators and UPS in service.
- The regenerated `writable.py` whitelists exactly the typed inputs, and no state, stamp or derived figure.
- Every page now has its own capture and a chip for every record it lists; every working list sits on a page:

| # | Page | "+ New" | Chips | Lists on the page |
|---|---|---|---|---|
| 1 | Site Register | Site | Site, **Site Condition, Site Type Profile** | Sites, Occupancy & Condition, **Site Type Profiles** |
| 2 | Lease Administration | Lease | Lease, **Lease Critical Event** | Leases, **Lease Critical Events**, Critical-Date Control, **Rent Schedule, IFRS 16 Extracts, Remeasurement Items, AP Cost Entries** |
| 3 | Statutory Compliance | Licence | Licence, **Licence Renewal** | Licences, **Licence Renewals, Operating-Risk Exceptions**, Critical-Date Control |
| 4 | Utilities | Utility Bill | **Utility Bill, Utility Account** | Bills, **Utility Accounts, AP Cost Entries** |
| 5 | Infrastructure Assets | Infrastructure Asset | **Infrastructure Asset, Infrastructure Outage** | Assets, **Outages, Asset Finance Requests** (+ report **Infrastructure Availability**) |
| 6 | Building PM | PM Job | **PM Job, Power Test** | PM, **Generator / UPS Tests** |
| 7 | Work Orders | Facility Work Order | Facility Work Order | Work Orders, **AP Cost Entries** |
| 8 | Safety & Security | Safety Inspection | Safety Inspection, **Security Incident** | Safety, Security & Incidents, **Hand-off Problems** |
| 9 | Open / Close Projects | Site Project | **Site Project** | Projects |
| 10 | Maintenance Demand Queue | — (system queue) | — | Demands: raised by M45/M46/M48/M17, completed and routed from the row |

## 3. Evidence

| Check | Result |
|---|---|
| Guard `cd_p03_portal/tests/test_m47_capture_buttons.py` (node runs the engine's own `fregCreate`/`fregPanels` over the real registry) | **HEAD ea2fdda1: 24 of 48 fail** (pages 1–6, 8, 9; the system queue's form; eight orphan lists; the six registers; the existing forms' spec attributes; the three untabbed forms; security; load order; the escalation route). **After: 48/48.** |
| Live `cd_facility/tests/test_m47_capture_live.py` (non-admin users with the real roles, through the workspace endpoints, rolled back) | **9/9.** Mutation check: switching off each of fire-licence-first, the renewal-penalty SoD, the CFO lease decision, the renewal owner's exclusion from the lapse decision, one bill per meter and month, operating hours lost, the hour meter that never goes back, the profile in the readiness gate, the work order raised by a failed test and the once-only escalation **turns a test red, 10 of 10**; restored byte-identical. |
| Regression on a freshly cloned and fully upgraded DB (`fix_test_m47`, `-u all`, 0 errors), no server attached: all of `cd_facility`, `cd_asset_workorder_spine`, `cd_asset_finance_hse_bridge`, the M48 A07 operability suite and the whole `cd_p03_portal` suite | **4,984 tests, 10 failures, all pre-existing.** Nine are spine relay tests (`test_a07_p1_spine`, `test_a07_p1_wiring_round2`) that relay the oldest outbox events and never reach their own on a `fix_test` clone (the template's backlog, as recorded in the M46 audit); one is the known M30/M19 `test_no_submodule_page_offers_another_records_button`. **Baseline: the unchanged code (shared checkout at 3efdab37) fails the identical 10 on the same DB.** Re-run as a pair with a probe recording the database each test connected to: HEAD 3efdab37 → `fix_test_m47`, 32 run, 10 failed; this branch 8a76305c → `fix_test_m47`, 32 run, 10 failed; the failing sets are identical. |
| Lint | `ruff check` and `ruff format` (0.8.4) clean on every changed file; `node --check` on `m47.js`. |
| Event registry (`tooling/events/verify_event_registry.py`) | The two new events conform (registry 535/535; published-and-registered 462/479, from 460/477). The remaining 17 unregistered events and the `cwip.capitalised` producer gap are pre-existing and not M47's. |
| UI on a private server (port 8079, worktree code, `fix_test_m47`, no cron threads) | All 10 sub-module pages read from the rendered page show the "+ New", chips and lists in the table in §2. A site was created with "+ Site", then a Utility Account through page 4's new chip (provider picker, account, meter, tariff) and saved (`SUACC/2026/0037`, Active); after the save, site, utility, provider and account number render read-only. The Site Type Profile form refused admin, who is a Facility Manager but not a Branch Operations Lead on that DB — the intended control. |

## 4. Not built here (owner decisions or other modules)

- **Owner decisions:**
  - the generator / UPS test interval (30-day default, `cd_facility.power_test_interval_days`);
  - the site-type profiles themselves: which licences a service branch, warehouse, office and data centre need (spec Open Question Q-02 with the local authorities). Until a profile exists, the gate keeps `trade,fire` and the gap figures keep trade only;
  - the DOFA Tier 4 holders (3 on fix_real) now also decide rent reviews and break options; confirm that is the intended CFO / COO delegation.
- **Not modelled (P1/P2):**
  - security arrangements and key / alarm-code custody (FR-FAC-041, BRU-FAC-16/17): a register of named custodians reconciled at staff change needs the M21 leaver event;
  - deposit tracking and recovery workflow (FR-FAC-013): the lease holds the deposit amount, and a deposit return is now a lease critical event with an owner;
  - lease variation as a separate record (FR-FAC-015): the existing modification workflow covers it;
  - site zones (FR-FAC-004), occupancy record (FR-FAC-043) beyond the condition inspection's occupancy %, recurring services (FR-FAC-037), vendor SLA scorecard (FR-FAC-036), condition-triggered PM (FR-FAC-030, needs M48);
  - consumption anomaly against area and peer sites (FR-FAC-039): bills are still compared with their own history;
  - automatic renewal task at 60 days (AUT-FAC-01): a renewal needs a named responsible person, and nothing names one. The alerts still fire at 90/60/30/15/7 days.
- **Owner gaps on fix_real:** no M47 data at all. Every new decision is two-person (renewal with a penalty, lease event decisions, the risk exception); the roles exist to do that (Facility Manager 4, Branch Operations Lead 42, Operations Director 3, DOFA Tier 4 3).

## 5. State — deployed 17 Nov 2026 (user-approved "deploy at 8069 and commit")

- Coordinated with the M48 session, which was deploying at the same time: M47 waited for its upgrade and restart to finish, then rebased onto `20dc185f` + `b6e16ae8`. The only conflict was the event registry (both added entries; resolved to 541). `writable.py` merged and regenerates byte-identically. Re-tested on the combined code: 765 tests (M47 guard and live, M48 guard, estate pages, A07 write whitelist and form engine, sub-module mapping, KPI tiles), 0 failures.
- Commits `a86e8d81` (fix), `dbccaad7`, `21c55e8b` (report) landed on `fix/a03-live-data-and-pending-work` with a compare-and-swap `update-ref` from `b6e16ae8`; the shared checkout's files were synced and it is clean. **Not pushed.**
- fix_real:
  - Backup: `all_working_folder/1000fix-2/_migration/backups/fix_real_pre_m47_capture_2026-11-17.dump` (49 MB).
  - Ran `-u cd_facility,cd_asset_workorder_spine,cd_p03_portal`: exit 0, no errors. cd_facility 19.0.0.2.0, cd_asset_workorder_spine 19.0.0.3.1; the 6 new tables, the work-order evidence columns and the `site.power_test_overdue` consumer exist.
  - Before the restart, every installed `cd_` module's code version matched fix_real (83 modules, no gap), so the restart loaded no un-upgraded code.
- 8069 was restarted once: PID 23080 → 7484 (supervisor). Registry 155 modules, 0 errors; `/web/login` 200.
- Verified on the live code: all six new models are served by the workspace API; the served bundle `web.assets_web` `510590e` contains the six new forms and the Infrastructure Availability report.
- **fix_dev (8090) was not upgraded.** It runs from the same checkout and needs the same `-u` before its next restart.
- Cleaned up: the private test DB `fix_test_m47`, its filestore copy and the worktree. The branch `fix/m47-capture-buttons` is kept.
