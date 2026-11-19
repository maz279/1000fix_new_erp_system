# M30 Platform Administration: sub-module capture audit, second pass

**Date:** 19 Nov 2026 · **Area:** A12 · **Workspace fragment:** `cd_p03_portal/static/src/a12/m30.js`
**Backend:** `cd_entity_config` 19.0.1.2.0 (`models/fix_platform_ops4.py`), `cd_p03_portal/controllers/a12/m30.py`,
plus one constraint in `cd_workshop` and three access rows in `cd_fpa` / `cd_attendance`.

The user again saw M30 sub-module pages without a relevant data-capture button. The first pass (14 Nov,
`M30_CAPTURE_BUTTON_AUDIT_2026-11-14.md`) had made every page capture each list it *showed*. Its own guard
still passed on HEAD (27/27). So this pass did not count buttons. It read each page against what the
specification says a person records there (§5 FR-ADM-001..040, §9 BRU-ADM-01..23, §10.1 owned entities).
Judged that way, **all six pages were still missing captures the spec gives them**, five of them P0.

## What each page is supposed to capture, and what it had

| # | Page | Spec | Had (14 Nov) | Missing |
|---|---|---|---|---|
| 1 | Branch Master | FR-ADM-002..005, 010 | Branch, Zone | **Branch capability profile** (FR-ADM-004, P0: which services and repair levels a branch performs, "so that intake, dispatch and booking respect it"). **Zone boundary** (FR-ADM-005: "geographic boundaries"); the geofence existed, but only on M02. |
| 2 | Entity Structure | FR-ADM-001, 006, 007, 010, 011 | Legal Entity only | **Cost centre** (FR-ADM-006, P0) and **business line** (FR-ADM-007, P0): both now exist, but in M54, writable only by finance. **Organisation change** (FR-ADM-011, BRU-ADM-08: effective-dated, history kept), which also covers renaming, re-zoning and relocating a branch (FR-ADM-010). |
| 3 | Config & Flags | FR-ADM-013..033 | Flag, change, parameter, job, environment | **Change freeze** (FR-ADM-028, hard rule BRU-ADM-22). **Emergency change path** (FR-ADM-017, P0; BRU-ADM-04). Flag **owning module and planned removal date** (FR-ADM-022, P0). **Component licence register** (FR-ADM-021). |
| 4 | Calendars | FR-ADM-008 | Calendar, Holiday | **Shift pattern** ("working calendars, shift patterns, … holidays"). It exists in M55, writable only by attendance supervisors. |
| 5 | Announcements | FR-ADM-039 (maintenance), 040 | Announcement, Notification config | **Maintenance window** (BRU-ADM-19, hard rule: outside 08:00–23:00, at most 4 h a month, announced 72 h ahead). Only the 72-hour lead was checked, on the announcement. The **Bengali title and message** of FR-ADM-040 were missing too. |
| 6 | Audit | FR-ADM-035..039 | DOFA ladder and band, release, restore test, DR drill | **Runbook** (FR-ADM-038, P0), **alert with a mandatory runbook** (FR-ADM-036, P0; BRU-ADM-14), **capacity review** (FR-ADM-037). |

How the gaps were confirmed:
- None of `fix.branch.capability`, `fix.org.change`, `fix.change.freeze`, `fix.maintenance.window`, `fix.runbook`,
  `fix.platform.alert`, `fix.capacity.metric` or `fix.component.licence` (or an equivalent) existed anywhere in `addons/`.
  - M66 ITSM has `fix.itsm.change` and employee-software licences, but no freeze, runbook or maintenance window.
  - The MSP runbooks and alerts (`fix.msp.*`) are customer-contract records.
- `fix.cost.centre` and `fix.business.line` (cd_fpa), `fix.shift.template` (cd_attendance) and `fix.geofence`
  exist. A Platform Admin could not write the first three (their ACL is finance / attendance supervisor only),
  so a chip on an M30 page would have been a dead button.

## What was changed

### Workspace (`m30.js`): what each page captures now

| # | Page | "+ New" | Form chips (new in **bold**) | New lists on the page |
|---|---|---|---|---|
| 1 | Branch Master | Branch | Zone, **Branch Capability**, **Zone Boundary** (opens M02's geofence form) | Branch Capability Profiles, Zone Boundaries |
| 2 | Entity Structure | Legal Entity | **Organisation Change**, **Cost Centre** and **Business Line** (open M54's forms) | Organisation Changes, Cost Centres, Business Lines |
| 3 | Config & Flags | Feature Flag | Configuration Change, **Change Freeze**, Registered Parameter, Scheduled Job, Environment, **Component Licence** | Change Freezes, Component Licences |
| 4 | Calendars | Working Calendar | Calendar Holiday, **Shift Pattern** (opens M55's form) | Shift Patterns |
| 5 | Announcements | Announcement | **Maintenance Window**, Notification Configuration | Maintenance Windows |
| 6 | Audit | DOFA Authority Ladder | Ladder Band, Release, Backup Restore Test, DR Drill, **Runbook**, **Alert**, **Capacity Review** | Runbooks, Alert Registry, Capacity Reviews |

Other workspace changes:
- **Configuration Changes** list: two new actions, "Apply as Emergency" and "File Change Record (emergency)". Two new columns: Emergency and Change Record Due By.
- **Change form**: an Emergency tick box. The change record is no longer required on an emergency proposal.
- **Feature Flag form**: Owning Module, Planned Removal, and a read-only "Past Removal Date".
- **Announcement form**: Bengali title and Bengali message.
- **Scheduled Job form**: a link to a runbook record.
- **Two new KPI tiles**: Emergency Changes Awaiting Record, and Maintenance Windows Planned.
- **Platform Health Console**: six new measured rows. They cover any freeze in force, emergency changes awaiting their record, maintenance minutes this month against the cap, runbooks past review, active alerts, and resources under 20% headroom.

The cost-centre, business-line, shift-pattern and zone-boundary lists on M30 pages are read-only (`create: false`). Their records are mastered and served by M54, M55 and M02. A surface may be declared by one area only, so the chips open those modules' own forms.

### Backend (`cd_entity_config` 19.0.1.2.0, new `models/fix_platform_ops4.py`)

- **`fix.branch.capability`** (FR-ADM-004). One row per branch, service and device category, holding the highest repair level the branch can take.
  - `cd_workshop` now refuses a workshop job above the profile of the workshop's branch.
  - A branch with no profile is not restricted, so nothing changes on the live estate until a profile is recorded.
  - A duplicate row is refused, including two rows with a blank ("every") category. The live test showed that a SQL UNIQUE let that pair through, because NULLs never collide.
- **`fix.org.change`** (FR-ADM-010/011, BRU-ADM-08). A rename, zone move or relocation of a branch, dated today or later and never backwards.
  - A **second Platform Admin approves** it. A change dated today applies at once; a later one is applied by the hourly job on its date.
  - The structure before the change is kept on the record and posted on the branch. Once approved, the record is never edited or deleted.
- **`fix.change.freeze`** (FR-ADM-028, BRU-ADM-22). While a freeze is in force:
  - applying a configuration change is refused;
  - changing a feature flag is refused, **except switching it off** (the kill switch, OPS-06).
  - A started freeze cannot be edited. It can only be lifted early, with a reason.
- **The emergency path on `fix.config.change`** (FR-ADM-017, BRU-ADM-04):
  - A routine change must cite its approved change record at proposal.
  - An emergency change is applied by its proposer alone, even during a freeze, and **every other Platform Admin is notified at once**.
  - It must file its change record within 24 hours, or the hourly job **reverts it automatically**. If the setting was changed again since, the job does not overwrite it and leaves it for a person to decide.
- **`fix.feature.flag`** gains `owning_module`, `planned_removal_date` and `stale` (FR-ADM-022/027).
- **`fix.component.licence`** (FR-ADM-021). Any class other than permissive (copyleft, AGPL, source-available, commercial) needs a note on how we comply.
- **`fix.maintenance.window`** (BRU-ADM-19). A window must lie between 23:00 and 08:00 Dhaka time, and planned windows total at most 240 minutes a month (`fix_maintenance.monthly_cap_minutes`).
  - "Draft the Announcement" raises a planned-maintenance announcement. A second Platform Admin publishes it, and publishing still refuses less than 72 hours of lead.
  - The work **cannot start until that announcement is published**.
  - An announced window cannot be moved; cancel it and plan another. Overrun is computed from the actual end.
- **`fix.platform.announcement`** gains `name_bn` and `body_bn` (FR-ADM-040).
- **`fix.runbook`** (FR-ADM-038) holds its steps or a document link, an owner, and a review period with the next due date.
- **`fix.platform.alert`** (FR-ADM-036, BRU-ADM-14):
  - every alert needs a runbook, and it must be an active one;
  - a runbook an active alert relies on cannot be archived.
- **`fix.capacity.metric`** (FR-ADM-037, OPS-08). Headroom and the projected date the resource fills are computed.
  - Below 20% headroom the review must choose to monitor or scale.
  - The measurement is evidence: only the decision and the note change afterwards, and a review is never deleted.
- **Access:**
  - Platform Admin and system only for organisation changes, licences, alerts and capacity reviews.
  - Every internal user may read capability profiles, freezes, maintenance windows and runbooks (operational information), but cannot write them.
  - Company isolation rules were generated for all eight models.
  - **Cross-module grants:** Platform Admins may now create and edit (not delete) cost centres and business lines (`cd_fpa`) and shift patterns (`cd_attendance`). The spec makes M30 own the cost-centre hierarchy and the business-line register (§3.3, §10.1); M54 keeps budgeting against them. Without these rows the chips would have been dead buttons.
- **Hourly jobs:** "M30: apply organisation changes that are due" and "M30: revert emergency configuration changes left without a change record".

## Evidence

- **Static page guard** `cd_p03_portal/tests/test_m30_capture_buttons.py` now expects every page's pass-2 captures, and passes in full. Its additions:
  - foreign chips must open a form and have an M30 list;
  - foreign records must be served by their owning module, and a Platform Admin must hold create/write on them;
  - the new stamps are never typeable;
  - the two new KPIs are served.
- **Other static guards** all pass: the estate page guard, the A12 write whitelist (the first run caught a field named `decision`, renamed to `scaling_action`), DOFA coverage, A12f, and the M02 / M54 / M55 page guards.
- **Live tests** `cd_entity_config/tests/test_m30_capture_pass2.py`: **35/35** on a private clone (`fix_test_m30c2`, upgraded with this code). The first pass's live suite still passes too: **67/67** together. Each test runs as a non-admin Platform Admin through `/p03/model/form|write|action`.
  - **The tests caught one real defect.** A SQL UNIQUE on (branch, service, category) let two "every category" rows in, because the blank category is NULL. It is now a Python check.
- **Mutation check:** 20 defects re-introduced one at a time; **20/20 turned the suite red**.
  - On the first run, 18/20 were red. The two survivors ("move a window under its announcement", "rewrite a capacity measurement") were each still refused by the form lock at the endpoint, so the model guard underneath was never exercised. The suite now also asserts both through the ORM.
- **Regression** on the same clone, covering cd_entity_config, cd_workshop, cd_fpa and cd_attendance plus the A12 portal guards: 1,310 tests, 118 failures/errors.
  - **All 118 reproduce on the base code** against the same database: the shared HEAD without this change gave 120 failures in those files.
  - They are clone-data fixtures: `fix_entity_company_unique`, seeded notification configs, and branch counts.
- **Browser walk:** headless Chromium against a private server on the clone (port 8147).
  - All 6 pages show their "+ New".
  - **All 12 new chips** are under "Forms Capturing It", and each opens a form with inputs, including M54's Cost Centre and Business Line, M55's Shift Pattern and M02's Zone Geofence.
  - All 27 new or changed lists and forms render with no console errors.
  - A runbook saved through the real form (RB-WALK-01, next review computed 2027-11-19).

## Gaps left

- **Archive policies and their execution** (FR-ADM-039 archival, BRU-ADM-20/21) are not built. Archiving live tables is a destructive operation that needs M24's retention classes first.
- **Job run log** (`fix.job.run`, FR-ADM-032) is not built. Run state is still read from the cron's own last/next call, so a failed run is not told apart from a successful one.
- **Environment promotion** (FR-ADM-016, BRU-ADM-03), **scoped values** (FR-ADM-014) and **environment comparison** (FR-ADM-020) are not built. The estate has no second running environment to promote from.
- **Flag targeting** by role, user or percentage (FR-ADM-023) is not built; flags still target global, branch or role scope.
- **Single-action branch provisioning** (FR-ADM-003, BRU-ADM-06) is not built. The capability profile and organisation change are its building blocks, but the atomic provisioning of stock location, cash drawer, queue and printers spans M15, M04 and M50.
- **A module-release gate on runbooks** (BRU-ADM-15) is not built. The release record has no module field to check against.
- **Merge of a branch** (FR-ADM-010) is not covered. The organisation change handles rename, zone move and relocation, but not reassigning open work.
- **People:** freezes, emergency changes and capacity reviews can be recorded by any Platform Admin. Organisation changes, configuration changes and maintenance announcements need a second one. fix_real has two Platform Admin holders (admin and one named user).
