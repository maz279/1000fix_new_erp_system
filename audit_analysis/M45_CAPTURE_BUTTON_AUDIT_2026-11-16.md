# M45 Enterprise Assets & Test Equipment — Sub-Module Capture Audit (2026-11-16)

**Question.** Does every M45 sub-module page carry a data-capture button that is relevant to what the
sub-module does?

**Sources.**
- Spec: `1000fix_ERP_Module/03_Modules/F_Asset_Equipment_and_Facilities/M45_Enterprise_Asset_and_Test_Equipment.md`
  §4 (design position), §5 (FR-EAM-001..046), §8 (lifecycle), §9 (BRU-EAM-01..22), §10.1 (owned entities),
  §11 (AUT-EAM-01..19), §13 (roles and SoD).
- Function register: `contracts/nav/registry.json`, M45 `freg` (7 sub-modules, 64 functions).
- Code: `static/src/a07/m45.js`, `controllers/a07/m45.py`, `cd_equipment_register`.

**Method.** Each page was evaluated the way the browser does it: node ran the engine's own
`fregCreate` / `fregPanels` over the real registry. The result was then compared with the spec
records each sub-module covers.

## 1. What was there (HEAD 48184ca8)

Every page had a "+ New", but only part of each sub-module could be captured.

| # | Sub-module | "+ New" | What was missing |
|---|---|---|---|
| 1 | Register & Classification (10) | Equipment | The class was free text: there was no class master and no measurement-critical flag (FR-EAM-002/003). The form captured no identity: no manufacturer, model, serial, asset tag, purchase reference, supplier, warranty or expected life (FR-EAM-001/004/006). There was no branch equipment profile (FR-EAM-009/037). |
| 2 | Issue / Custody / Transfer (11) | Issue | The Transfers list sat on the page with **no transfer capture**. There was no way to hand an item back with its condition (Return Item sent none, so every return waited for an inspection hold). |
| 3 | Kit Management (6) | Kit | No chip. |
| 4 | Calibration Management (16) | Calibration Record | Out-of-service holds were listed, but **none could be raised**. Calibration profiles and impact assessments sat on **no page**. There was no reference-standard register: `standard_ref` was text, so BRU-EAM-04 ("not against an expired standard") was unenforceable. There was no calibration recall (FR-EAM-029). |
| 5 | PM & Repair (8) | PM job | No **PM plan** (FR-EAM-032): every preventive job was typed by hand. A corrective job had no symptom, no repair route and no downtime (FR-EAM-033/034/036). |
| 6 | Usage Capture (6) | Usage | No chip. Impact assessments were not on the page. |
| 7 | Verification & Loss (7) | Single-item verification | No **loss / theft / damage report** with its accountability (FR-EAM-040). The reporter was never barred from approving the write-off (BRU-EAM-12). There was no blind count by branch (FR-EAM-038, AUT-EAM-12) and no retirement / disposal record (FR-EAM-042/043). A data-bearing item could leave without M06 erasure (BRU-EAM-16). |

**A defect underneath the register.** The fitness gate required a current calibration on
**every** item. A screwdriver or laptop, which the spec registers on purpose ("the register is
deliberately wide, the control deliberately narrow", §4), could therefore never be issued, so the
Issue capture was unusable for most of a real register.

Other gaps:
- Three working lists sat on no page: alerts, calibration profiles and impact assessments.
- fix_real held 0 M45 rows, 0 Equipment Custodians, 0 Calibration Technicians and 10 Quality Managers.

## 2. What was built

### Backend — `cd_equipment_register` 19.0.0.2.0, new file `models/fix_equipment_capture.py`

- **`fix.equipment.category`** (the class): the seven spec classes. Measuring instruments and
  standards are calibration-controlled; IT assets are data-bearing. It is kept by the Quality Manager.
- **Equipment identity**: the class plus:
  - manufacturer, model, serial and asset tag (generated `1000FIX-EQ-nnnnnn`, unique, permanent);
  - purchase / GRN reference, acquired-on date, expected life;
  - supplier, warranty end and under-warranty flag;
  - criticality and home location.
- **Measurement-critical** comes from the class; an unclassified item stays controlled.
  - A non-critical item has calibration state `not_required`. It is issued, used and returned from
    a fault without a calibration.
  - It cannot produce a QC result (BRU-EAM-02/15).
  - Moving a registered item to another class is a Quality Manager decision.
- **Reference standard on a calibration**, plus provider and accreditation reference. A calibration
  against a standard that is not current on the day, or against an item that is not a standard, is
  refused (BRU-EAM-04, AUT-EAM-06). These fields are evidence: they are fixed once recorded.
- **Calibration recall** (`action_recall_calibration`):
  - done by a QM or Calibration Technician, with a reason;
  - opens a `recall` hold, so the item is out of service until a passing calibration after the recall;
  - gives the holder a to-do and publishes `equipment.calibration_recalled`.
- **`fix.branch.equipment.profile`**: the minimum held per branch and class. It shows held,
  fit & available, the shortfall and the capability exception (BRU-EAM-20). It is kept by the QM,
  and fed into the new *Register Completeness* report.
- **`fix.equipment.pm.plan`**:
  - covers one item or one class, triggered by elapsed days/months or by recorded uses;
  - raises one preventive job per item when due, never beside an open one, through a nightly cron
    and *Raise Due Jobs*;
  - counts from the item's last completed job of the plan.
- **PM job** gains: plan, work to do, symptom, repair route (internal / external provider) and
  downtime hours (frozen once done).
- **`fix.equipment.loss`** (lost / stolen / damaged):
  - Anyone reports it. The reporter, the custodian at loss and the value are stamped.
  - A lost or stolen item is Lost / Missing; a damaged one goes out of service.
  - Decisions: *Recovered* (where found), *Send to Repair* (raises a corrective job) or *Request
    Write-Off* (the existing routed approval).
  - The reporter is excluded from routing and refused at approval (BRU-EAM-12).
  - An optional recharge is published to M52 on write-off.
- **`fix.equipment.audit` + lines** (a blind count):
  - The counter lists what they find.
  - On *Complete Count*, everything the register expects in that store but nobody found is
    recorded missing, through the existing verification records and events.
  - Items out on issue or in transit are excluded from expected.
  - Only the named counter closes the count, and a counter who is custodian of an item counted is
    refused (SoD).
- **`fix.equipment.retirement`**:
  - basis, justification and replacement note;
  - approved as the item's write-off (authority matrix);
  - disposal route and reference;
  - a data-bearing item is not disposed without its M06 erasure certificate (BRU-EAM-16);
  - publishes `equipment.disposed`.
- Sequences, the PM-plan cron, ACLs (nobody deletes a register row) and company / OU record rules.

### Workspace — `m45.js`, `controllers/a07/m45.py`, `writable.py`

| # | "+ New" | Chips | Lists on the page |
|---|---|---|---|
| 1 | Equipment | Equipment, **Equipment Class**, **Branch Equipment Profile**, Write-Off | register, classes, branch profiles, classification + **Register Completeness** |
| 2 | Issue | Issue, **Return** (pick the issue, condition + damage), **Transfer** | issues, transfers, **alerts** |
| 3 | Kit | **Kit** | kits |
| 4 | Calibration Record | Calibration Record, **Calibration Profile**, **Calibration Standard**, **Calibration Recall** (pick + reason), **Out of Service** | schedule, certificates, **profiles**, **standards**, OOS, **impacts**, **alerts** |
| 5 | PM / Corrective Job | PM job, **PM Plan**, **Report Fault** | PM jobs, **PM plans**, OOS |
| 6 | Usage | **Usage** | usage, retrospective, **impacts** |
| 7 | **Schedule Verification Count** | **Verification Count**, Physical Verification, **Loss / Damage Report**, Write-Off, **Retirement** | **counts**, verifications, **loss & damage**, **write-offs**, **retirements** |

Other workspace changes:
- The equipment, calibration and loss forms are tabbed: each has over 15 fields, so the project
  standard requires tabs.
- Packs now read the class rather than the free-text category:
  - compliance reports "not measurement-critical";
  - loss & write-off now includes loss reports;
  - cost of ownership shows downtime.
- New KPI: Open Losses.
- Return takes `detail` (damage text) with the condition.
- An out-of-service hold on a non-critical item is resolved by a store keeper or QM without a calibration.

## 3. Evidence

- **Guard** `cd_p03_portal/tests/test_m45_capture_buttons.py`: engine-evaluated, 46 tests.
  - 46/46 pass on the fix.
  - 27/46 fail on HEAD 48184ca8 (run on a clean `git archive` of HEAD).
- **Live** `cd_equipment_register/tests/test_m45_capture_live.py`: 18/18 on a private clone (`fix_test_m45`).
  - Every capture goes through `/p03/model/form|write|action`, as non-admin role holders, rolled back.
- **Mutation-checked**: each rule broken in turn turns its test red:
  - the narrow gate (both layers);
  - the standard check;
  - the reporter SoD;
  - the blind count;
  - the erasure block.
  - A single-layer gate mutation survived, because the `not_required` state alone already holds the gate open (defence in depth).
- **Regression**: 5,265 tests across `cd_equipment_register`, `cd_workshop` (M31 QC), `cd_asset_finance_hse_bridge`, `cd_asset_workorder_spine`, `cd_facility`, `cd_stream_registry` and all `cd_p03_portal` tests. There were 10 failures, and all 10 predate this work:
  - M30/1 "Branch Master" `create`. This was already recorded as failing in HEAD by the M43/M44 audits.
  - 9 relay-dependent spine tests (vehicles, devices, telematics, service due). They fail identically on untouched HEAD code against the same clone, because of the clone's outbox backlog (the same cause the M27 audit recorded).
- **Lint**: ruff check and format are clean. `models/__init__` keeps the Odoo load order with `# ruff: noqa: I001` (as in M44). The isolation-rule check reports only the 4 modules that were already drifting.
- **UI** on a private server (worktree code, `fix_test_m45`, port 8072, `?debug=assets`):
  - all 7 pages show the "+ New", chips and lists in the table above;
  - every chip's form opens with its fields and no server error.

## 4. Not built here

- **FR-EAM-044** (requisition to M16 with justification) and **FR-EAM-046** (full cost of ownership):
  P2. The retirement captures the replacement justification; M16 owns the requisition.
- **FR-EAM-008** (documents through M24): the calibration certificate and loss evidence are uploaded
  on their records; an M24 retention binding is not added.
- **M48 condition-triggered PM** (AUT-EAM-19): Wave 8, as the spec says.
- **Owner gaps on fix_real**: 0 Equipment Custodians and 0 Calibration Technicians. Classes, branch
  profiles, plans and counts need these roles (A07 decision §H). There is still no M45 data.

## 5. State (17 Nov 2026) — deployed on fix_real

The user approved "Commit and deploy".

- **Commit.** `ea2fdda1` (fix) is on `fix/a03-live-data-and-pending-work`. It is **not pushed**.
  - It was built at base 48184ca8 and rebased onto the M46 commits (e68e99cc).
  - `writable.py` was regenerated after the rebase, so it carries both the M45 and M46 fields.
  - The M45 and M46 guards pass on the rebased tree, 84/84.
- **Backup.** `fix_real_pre_m45_capture_2026-11-17.dump` (46.8 MB), with 1,600 table-data entries.
- **Upgrade.** `-u cd_equipment_register,cd_p03_portal` on fix_real exited 0 with no errors.
  - `cd_equipment_register` is now 19.0.0.2.0.
  - The 7 new tables and the PM-plan cron (active) are in place.
- **Restart.** 8069 was restarted once (PID 49012 stopped). Supervisor 23964 relaunched it in about 5 s, and the log loaded 155 modules with no errors.
- **Verified live:**
  - All 7 new surfaces are served, and the recall and loss actions are exposed.
  - The standard picker is filtered to calibration standards.
  - A non-admin Quality Manager can create a class (rolled back).
  - The live bundle `391c86a` contains every new M45 screen and chip, and the M46 screens are kept.

fix_real holds 0 rows in the new registers, so nothing was migrated. Two owner gaps remain:
0 Equipment Custodians and 0 Calibration Technicians (§4).
