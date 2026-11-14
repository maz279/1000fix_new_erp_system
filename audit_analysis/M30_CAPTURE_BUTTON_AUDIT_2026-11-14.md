# M30 Platform Administration: sub-module capture audit

**Date:** 14 Nov 2026 · **Area:** A12 · **Workspace fragment:** `cd_p03_portal/static/src/a12/m30.js`
**Backend:** `cd_entity_config` (models), `cd_p03_portal/controllers/a12/m30.py` (surfaces, write whitelist, reports, KPIs)

The user reported that not every M30 sub-module page has a relevant data-capture button.
The report was right. Every page did show a "+ New" button. But on five of the six pages that button
covered only one of the records the page lists. One page offered a capture for the wrong record set,
nine screens sat on no page, and four registers the spec makes M30 own did not exist at all.

## What M30 is supposed to capture

The Function Register only names the six sub-modules (12 + 8 + 10 + 9 + 6 + 19 = 64 functions).
The detail is in `1000fix_ERP_Module/03_Modules/K_Platform_and_Technology/M30_Platform_Administration_and_Configuration.md`:
§3.1 (scope), §5 (FR-ADM-001..040), §9 (BRU-ADM-01..23) and §10.1 (owned entities).

| # | Sub-module | Spec basis | What a person records there |
|---|---|---|---|
| 1 | Branch Master | FR-ADM-002..005, 010 | Branches and dispatch zones |
| 2 | Entity Structure | FR-ADM-001, 006, 007 | Legal entities. Cost centres and business lines are in the spec too; see the gaps section. |
| 3 | Config & Flags | FR-ADM-013..019, 022..028, 029, 031..033; BRU-ADM-02, 11 | Feature flags, the **technical parameter registry**, **configuration changes** (versioned, second-person, rollback), the **scheduled job registry**, environments |
| 4 | Calendars | FR-ADM-008 | Working calendars and holidays |
| 5 | Announcements | FR-ADM-040 | Announcements and notification configuration |
| 6 | Audit | FR-ADM-035/036/039; BRU-ADM-17, 18; DOFA rulings | DOFA ladders and bands, releases, and the **restore-test** and **DR-drill** evidence. The health console and drift review are read-only. |

## What the code did (proved on HEAD before the fix)

`cd_p03_portal/tests/test_m30_capture_buttons.py` runs the engine's own `fregCreate` / `fregPanels` in node
over the real registry. I ran it against unmodified HEAD (a `git archive` copy). **14 of its 27 checks fail,
and all 6 pages fail.**

| # | Page | "+ New" on HEAD | Form chips on HEAD | Defect |
|---|---|---|---|---|
| 1 | Branch Master | + Branch | Branch | The page lists dispatch zones but had no Zone capture |
| 2 | Entity Structure | + Legal Entity | **none** | Environments were listed here and could not be captured |
| 3 | Config & Flags | + Feature Flag | Feature Flag | "Parameter Registry" and "Scheduled Job Registry" were read-only views of Odoo's own `ir.config_parameter` / `ir.cron`. **No configuration change record existed** (FR-ADM-015/018, BRU-ADM-02: "configuration changes must be traceable to an approved change record"), and **no job registry existed** (FR-ADM-031, BRU-ADM-11: every job has an owner, an expected duration and a failure impact). |
| 4 | Calendars | + Working Calendar | **none** | Calendar Holidays was on no page, so a holiday could not be captured from here |
| 5 | Announcements | + Announcement | Announcement | Notification configuration was listed but could not be captured |
| 6 | Audit | + DOFA Authority Ladder | Authority Ladder | Releases and ladder bands were listed (or orphaned) with no capture. **"Backup & DR (Customer Plans)" listed customer data-recovery plans**, which is M06's record (`fix.data.backup.plan`), so the platform's own restore tests (BRU-ADM-17) and DR drills (BRU-ADM-18) had nowhere to go. |

On no page at all: Calendar Holidays, Ladder Bands, Platform Health Console, Backup, plus five report
screens (Job Success Rate, Branch Registry, Flag Rollout, Calendar Coverage, DOFA Coverage).

One more defect that the new write-whitelist check found: the DOFA ladder form offered
"Matches Current Code" as an input. That field is computed from the code and never stored, so the server
never saved anything typed there. It is now shown read-only.

## What was changed

**Workspace (`m30.js`)**
- Every page now names its captures explicitly (`create:` and `forms:`):
  - 1: + Branch, with a Zone chip. The page also offers the Branch Provisioning Time report.
  - 2: + New Legal Entity, with a Legal Entity chip. Environments moved to page 3.
  - 3: + New Feature Flag, with chips for **Configuration Change** ("Propose a Configuration Change"), **Registered Parameter**, **Scheduled Job** ("Register a Scheduled Job") and Environment. New lists: Configuration Changes, and Scheduled Actions (the raw `ir.cron` inventory, still read-only).
  - 4: + New Working Calendar, with a Calendar Holiday chip. Holidays are now on this page.
  - 5: + New Announcement, with a Notification Configuration chip.
  - 6: + New DOFA Authority Ladder, with chips for Ladder Band, Release, **Backup Restore Test** ("Record a Restore Test") and **DR Drill** ("Record a DR Drill"). Ladder Bands, Health, Backup and DR Drills are on the page.
- "Parameter Registry" now lists `fix.config.parameter`. "Scheduled Job Registry" now lists `fix.scheduled.job`. "Backup Restore Tests" now lists `fix.backup.verification` instead of customer plans.
- Two new KPI tiles: Config Changes Awaiting Apply, and Registered Jobs Missed.
- The Scheduled Job form is tabbed (16 fields), per the workspace multi-tab standard.

**Backend (`cd_entity_config` 19.0.1.1.0, new `models/fix_platform_ops3.py`)**, following spec §10.1:
- `fix.scheduled.job`: a real `ir.cron` plus an owner, expected duration, SLA, concurrent-safe flag, failure impact and runbook.
  - Schedule, last run and next run are read from the cron. **Missed Run** (T-09) means the job is enabled and its next call is overdue by more than its expected duration (at least 15 minutes).
  - A cron can be registered only once.
- `fix.config.parameter`: the registry of keys the workspace may change, with type, minimum/maximum or allowed values, owning module and impact.
  - **Only a system administrator registers a key.**
  - A key that looks like a credential (secret, password, token…) is refused, because a change record keeps old and new values.
- `fix.config.change`: proposed with an approved change reference (M66), and validated against the parameter's type and range at the point of change (FR-ADM-019).
  - **A second Platform Admin applies it** (BRU-ADM-02). It takes effect at once, without a restart, and the previous value is kept.
  - **One action rolls it back** (FR-ADM-018). Only the latest applied change of a key can be rolled back, and only while the setting still holds the value it applied; a value changed outside the register is never overwritten.
  - Audit rows carry the key and change number, never the value, because every internal user can read the trail.
- `fix.backup.verification`: a restore test with backup type, taken / tested times, duration, pass or fail, and evidence.
  - Once filed, only the note can change, and a test is never deleted.
  - A restore cannot predate its backup.
- `fix.dr.drill`: scenario and scope, with RPO and RTO achieved and checked against NFR-007 (15 min / 120 min).
  - **A second Platform Admin signs it off.** A drill that missed a target needs its issues recorded first.
  - Signed off means frozen.
- **Access:** all five are Platform Admin and system only. A plain employee reads none of them, and each has a company isolation rule (generated by `generate-isolation-rules.py`).
- Controller:
  - Five new surfaces and their write whitelists. State, stamps and computed run data are never writable.
  - The Platform Health Console gains five measured rows: unregistered active jobs, missed registered jobs, changes awaiting a second person, days since the last passed restore test, and DR drills signed off in the last 12 months.
  - The new KPIs are skipped for a caller who cannot read the registers, and both the KPIs and the health rows tolerate the models not being installed yet.

## Evidence

- `cd_p03_portal/tests/test_m30_capture_buttons.py`, 27 checks: **14 fail on HEAD, 27 pass after the fix.** The estate-wide page guard (`test_estate_module_pages.py`) still passes: 632 together.
- `cd_entity_config/tests/test_m30_capture_live.py`, **32/32 pass** on a private clone of fix_test (`fix_test_m30`, `-u cd_entity_config`). Each test runs as a non-admin Platform Admin through `/p03/model/form|write|action`. They show that:
  - all 17 capture forms open blank for their actor;
  - a plain employee can read none of the five registers;
  - a Platform Admin cannot register a key, and a credential key is refused;
  - an out-of-range value is refused, typed stamps are ignored, the proposer cannot apply, a second admin can, and the value changes at once;
  - an applied change is frozen, it rolls back in one action, and it is never rolled back over an outside change;
  - a job is registered once, takes the cron name, and shows Missed Run when stale;
  - the health console and KPIs read as the caller;
  - a restore test cannot be rewritten, through the endpoint or through the ORM;
  - a drill cannot be signed off by its recorder, and a missed target needs its issues first.
- **Mutation check:** seven defects re-introduced one at a time; 6 turned the suite red, and the 7th is blocked by the ACL:
  - proposer self-apply, credential key accepted, restore test rewritable, drill self sign-off, out-of-range value accepted and rollback over an outside change each turned it red.
  - With the "only a system administrator registers a key" model check removed, the suite stayed green: the ACL (read-only for Platform Admin) still refuses. That is defence in depth, recorded here.
- **Browser check:** a separate Odoo ran on `fix_test_m30`, port 8072. The live 8069 server was not touched.
  - All 6 pages show their "+" button and list every capture under "Forms Capturing It".
  - The KPI tiles render.
  - "Record a Restore Test" saved RST/2026/0010 through the real form. The form then locked, and the row appeared on the Backup Restore Tests list.
  - All 19 M30 lists return every declared column (none silently dropped).
  - No console errors.
- Regression: see the deploy section.

## Gaps left (no model, or an owner decision)

- **Promotion through the environment ladder** (FR-ADM-016, BRU-ADM-03), **the emergency change path with auto-revert** (FR-ADM-017, BRU-ADM-04), **scoped values** (entity/branch, FR-ADM-014), **change freezes** (FR-ADM-028) and **environment comparison** (FR-ADM-020) are not built. A change applies to the environment it was made in. Promotion needs a second running environment that this estate does not have.
- **Alert registry and runbook registry** (`fix.platform.alert`, `fix.runbook`, BRU-ADM-14/15), **archive policy and runs**, **capacity metrics**, **component licence register**, **organisation change history** (`fix.org.change`) and **job run log** (`fix.job.run`; run state today comes from the cron's own last/next call, so a failed run is not distinguished from a successful one): no models.
- **Cost-centre hierarchy** (FR-ADM-006, P0): no model exists anywhere. The ledger dimension holds a free-text `cost_centre`. Building it means a finance decision on the code list.
- **Business lines** (FR-ADM-007): the spec says M30 owns them, but the code masters `fix.business.line` in M54 (FP&A), with finance access rights. It is not on an M30 page. Who owns it is an owner decision.
- **Branch provisioning as one action** (FR-ADM-003) and the full branch lifecycle (relocate/merge, FR-ADM-010) are not built. The branch moves only through Go Live / Suspend / two-person closure.
- **People:** a configuration change, a drill sign-off and environment masking each need a second Platform Admin. On fix_real the Platform Admin role has **two** holders, `admin` and one named user, so every second-person step depends on `admin`. Name a second real Platform Admin.

## Deploy (14 Nov 2026, user-approved)

- **Committed** `def9c525` on `fix/a03-live-data-and-pending-work`, with all hooks green. It was committed in a sparse worktree and the branch moved with `update-ref`, because the M29 session was busy in the shared checkout. **Not pushed.**
- **Regression** on the private `fix_test_m30` clone: cd_entity_config, the A12 M30/M65 suites, DOFA coverage, the A12 write whitelist and the estate page guard. About 864 tests: 0 failed, 2 skipped.
- **Drift check** on fix_real before the upgrade: the only gap was the five new tables.
- **No full pg_dump.** Dumps of these databases have crashed the shared Postgres before, and this upgrade only adds tables. The same upgrade had already run clean on the fix_test clone.
- **Upgrade:** `-u cd_entity_config` on fix_real reloaded 155 modules in 153 s, with no errors. Version is now 19.0.1.1.0; the 5 tables, ACLs and 3 sequences are present.
- **Restart:** 8069 restarted at 10:37 (PID 36404). It has no supervisor, so it was relaunched with `launch_8069.ps1`. The login page answered 200 in about 4 s, and the log shows "155 modules loaded" with no errors.
- **Live check on 8069 (read-only, nothing saved on fix_real):**
  - All 6 pages show their "+" button and list every capture under "Forms Capturing It".
  - All 14 lists probed return every declared column.
  - The KPIs serve `config_changes_pending` = 0 and `jobs_missed` = 0.
  - The health console shows its new rows: **211 active scheduled jobs, none registered**, no restore test on record ("never"), and 0 DR drills.
  - The only console errors are Odoo's service-worker registration failing, which is unrelated to M30.

What fix_real needs now is data, not code. The 211 jobs need registering (owners and failure impact), and a first restore test and a first DR drill need recording. A second named Platform Admin is needed for every second-person step.
