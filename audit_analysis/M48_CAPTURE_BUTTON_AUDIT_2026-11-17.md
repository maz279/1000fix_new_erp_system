# M48 IoT Telemetry & Predictive Maintenance — Sub-Module Capture Audit (2026-11-17)

**Question.** Does every M48 sub-module page carry a data-capture button that is relevant to what the
sub-module does?

**Sources.**
- Spec: `1000fix_ERP_Module/03_Modules/F_Asset_Equipment_and_Facilities/M48_IoT_Telemetry_and_Predictive_Maintenance.md`
  §3 (scope), §5 (FR-IOT-001..046, grouped §5.1-§5.5), §8 (stream and alert lifecycles), §9 (BRU-IOT-01..22),
  §10.1 (owned entities), §11 (AUT-IOT-01..21), §13 (roles and SoD).
- Function register: `contracts/nav/registry.json`, M48 `freg` (7 sub-modules, 51 functions).
  The register names no functions, so each page was matched to its spec section: page 1 = §5.1 (8 FRs),
  pages 2-3 = §5.2-§5.3, page 4 = §5.4 (8 FRs), pages 5-7 = §5.5.
- Code: `static/src/a07/m48.js`, `controllers/a07/m48.py`, `cd_stream_registry`.

**Method.** Each page was evaluated the way the browser does it: node ran the engine's own
`fregCreate` / `fregPanels` over the real registry. The result was then compared with the spec
records each sub-module covers.

## 1. What was there (HEAD 3efdab37)

| # | Sub-module | "+ New" | Chips | What was missing |
|---|---|---|---|---|
| 1 | Stream Registry & Onboarding (8) | Stream | Stream Binding | The device and consent lists were on the page with **no capture for either**. There was no signal definition (FR-IOT-004): the metric was free text with no expected range, so a suspect value passed silently (FR-IOT-016). There was no criticality assessment (FR-IOT-007, BRU-IOT-20). A device recorded no firmware, connectivity or gateway (FR-IOT-002). **Nothing decommissioned a stream or a device** (FR-IOT-008). |
| 2 | Protocol Adapters (7) | Protocol Adapter | none | No file batch channel (FR-IOT-012, P0: "a first-class channel"). The protocol list had no Sparkplug B, SNMP, file or AEMP telematics (FR-IOT-009/014/015). A stream had no source address (topic, node, OID) (FR-IOT-013). |
| 3 | Ingestion & Storage (9) | **Iot Device** (wrong record) | Downsampling Policy | Its own lists (downsampling policies, retention changes, gaps, readings, aggregates) sat on **no page**. The Retention Change form had no chip anywhere. |
| 4 | Threshold Alerting (8) | Alert Rule | Alert Rule | No maintenance window (FR-IOT-032, BRU-IOT-16, §8.3 "Suppressed"). The M48 scheduled-check alerts sat on no page. |
| 5 | Health Scoring (6) | **Failure Prediction** (wrong record) | none | Only a computed report: no health index history, so no trend (FR-IOT-037/038), and nothing decided which assets are scored. |
| 6 | Failure Prediction (7) | Failure Prediction | none | **A prediction no intervention acted on could never get an outcome** (FR-IOT-044, BRU-IOT-14: "every prediction has a recorded outcome"). No failure mode and no RUL interval (FR-IOT-039/041). |
| 7 | Prescriptive Routing (6) | Prescriptive Action | none | The intervention named no parts (M15) and no skill (M22) (FR-IOT-042). |

Other findings:
- The Alert Rule (25 fields), Telemetry Consent (26), Prescriptive Action and Failure Prediction forms
  had more than 15 fields and no tabs, against the project's form standard.
- fix_real holds **0 M48 rows**. Each of the four M48 roles has one holder (admin).

## 2. What was built

### Backend — `cd_stream_registry` 19.0.0.2.0, new file `models/fix_iot_capture.py`

- **`fix.iot.signal`** (FR-IOT-004): code, name, data type, canonical unit, expected range, sampling
  interval, criticality and retention class. Kept by the IoT Administrator; a code that streams carry
  cannot be renamed.
  - A stream that names a signal takes its metric, unit and interval from it.
  - Ingest keeps a reading outside the expected range and flags it **Out of Expected Range**
    (`quality_flag`, guarded) instead of passing it silently (FR-IOT-016).
- **`fix.iot.monitoring.scope`** — the criticality assessment (FR-IOT-007, BRU-IOT-20, ISO 17359):
  one asset (M45 equipment or M47 site), criticality, failure consequence, the signals selected and why,
  review date. The IoT Administrator records it; the assessor is stamped.
- **`fix.iot.health`** — the asset health index as history (FR-IOT-037/038, AUT-IOT-11):
  - written by *Score Health Now* on a scope and by a nightly job over every active scope, never typed;
  - the same transparent rule as the Asset Health report, with the spec's four bands
    (healthy / watch / degraded / critical), the previous index, the trend and the contributing factors;
  - publishes `asset.health_updated`, and `asset.health_degraded` when the band worsens.
- **Device identity** (FR-IOT-002): firmware, serial number, connectivity, installed date and the
  gateway it reports through (must be a registered gateway). One record per device identifier.
- **Decommissioning** (FR-IOT-008), stream and device:
  - ingestion stops for good, open alerts and gaps close, the series is marked terminated, history is kept;
  - a decommissioned stream is never reactivated, and a decommissioned device takes no new stream;
  - publishes `telemetry.stream_decommissioned`.
- **Adapter channels**: Sparkplug B, SNMP, File Batch and AEMP telematics; a stream records its
  source address.
- **`fix.iot.file.batch`** (FR-IOT-012): a CSV export (stream, timestamp, value), at most 5,000 rows.
  - Every row goes through the **live ingest gates** (adapter enabled and keyed, stream active,
    consent, duplicates, future dates) and the alert rules.
  - Every refused row is reported with its reason (BRU-IOT-08: never silent loss).
  - A processed batch is kept as evidence: it can neither change nor be deleted.
- **`fix.iot.maintenance.window`** (FR-IOT-032, BRU-IOT-16):
  - one device or one site, at most 30 days;
  - requested, then approved by an IoT Manager **other than the requester**; terms fixed once requested;
  - while it runs, rule breaches on the asset raise no alert and are counted on the window.
- **Prediction outcome** (`action_record_outcome`, FR-IOT-044, BRU-IOT-14, AUT-IOT-16):
  - for a failure or degrading prediction with no intervention under way;
  - Failure Confirmed needs evidence; False Alarm and Unknown wait until the horizon has passed;
    Unknown is excluded from precision;
  - **whoever recorded the prediction does not record its outcome**;
  - publishes `intervention.outcome_recorded` with `intervention_performed: false`.
- **Prediction**: failure mode, and the RUL interval around the estimate (FR-IOT-039/041); both are
  model output, fixed once recorded.
- **Prescriptive action** (FR-IOT-042): recommended action, the M22 skill code (validated when M22 is
  installed), and part lines with free stock read from M15. Parts and skill are part of what is
  approved: after approval they change only through Revise Terms. Requesting approval publishes
  `intervention.proposed` with the parts and the skill.
- Sequences, the nightly health cron, ACLs and company record rules for the six new models.

### Workspace — `m48.js`, `controllers/a07/m48.py`, `controllers/a11/m26.py`, `writable.py`

| # | "+ New" | Chips | Lists on the page |
|---|---|---|---|
| 1 | Stream | Stream Binding, **Device / Gateway**, **Signal Definition**, **Telemetry Consent**, **Criticality Assessment** | streams, devices, **signals**, consents, **monitoring scope** |
| 2 | Protocol Adapter | Protocol Adapter, **File Batch Import** | adapters, **file batches** |
| 3 | **Downsampling Policy** | Downsampling Policy, **Retention Change** | pipeline health, **downsampling, retention changes, gaps, readings, aggregates** |
| 4 | Alert Rule | Alert Rule, **Maintenance Window** | rules, alert lifecycle, **maintenance windows**, **M48 alerts** |
| 5 | **Assess an Asset for Monitoring** | Criticality Assessment | health report, **health index history**, monitoring scope |
| 6 | Failure Prediction | Failure Prediction, **Record Prediction Outcome** | predictions, RUL |
| 7 | Prescriptive Action | Prescriptive Action (now with parts and skill) | prescriptive actions |

Also:
- The Stream, Device, Alert Rule, Consent, Prediction, Prescriptive Action and File Batch forms are tabbed.
- Decommission buttons are on the stream and device lists.
- *Score Health Now* is on the monitoring scope list.
- The new outcome action is served on the prediction surface in `a11/m26.py`, which owns it.

## 3. Evidence

- **Guard** `cd_p03_portal/tests/test_m48_capture_buttons.py`: engine-evaluated, 47 tests.
  - 47/47 pass on the fix.
  - 28/47 fail on HEAD 3efdab37 (run on a clean `git archive` of HEAD).
- **Live** `cd_stream_registry/tests/test_m48_capture_live.py`: 14/14 on a private clone (`fix_test_m48`),
  none skipped.
  - Every capture goes through `/p03/model/form|write|action`, as non-admin holders of the M48 roles,
    rolled back.
  - The live tests found one defect the guard could not: the workspace leaves an empty field out of
    the save, and a constraint runs only when one of its fields is saved. A criticality assessment
    with **neither** an asset nor a site was accepted, and so was a maintenance window. Each check now
    also names a required field.
- **Mutation-checked**: each rule broken in turn turns its test red (9/9):
  - the out-of-range flag;
  - decommissioning closes alerts;
  - a scope names one asset;
  - the batch reports refused rows;
  - the window suppresses alerts;
  - the window approver is not the requester;
  - the outcome recorder is not the predictor;
  - a false alarm waits for the horizon;
  - approved parts are frozen.
- **Regression**: 5,236 tests across `cd_stream_registry`, `cd_ml_services`, `cd_asset_workorder_spine`,
  `cd_equipment_register`, `cd_facility` and all `cd_p03_portal` tests. There were 10 failures, and all
  10 fail identically on the unchanged HEAD code against the same clone:
  - M30/1 "Branch Master" `create`, already recorded by the M43-M46 audits;
  - 9 relay-dependent spine tests, caused by the clone's outbox backlog (as recorded by M27 and M45).
- **Events**: the six new event types are registered with their derived schemas
  (`contracts/events/`, 533 -> 539). The registry verifier's unregistered count drops from 23 to 17;
  the 17 left predate this work.
- **Lint**: ruff check and format are clean. `models/__init__` keeps the Odoo load order with
  `# ruff: noqa: I001`.
- **UI** on a private server (worktree code, `fix_test_m48`, port 8081, `?debug=assets`):
  - all 7 pages show the "+ New", chips and lists in the table above;
  - all 14 chip forms open with their fields, tabs where required, and no server error.
    The outcome form opens on its prediction picker.

## 4. Not built here

- **Rule types beyond a threshold** (rate of change, baseline, composite: FR-IOT-029),
  **cross-asset correlation** (FR-IOT-033) and the **escalation ladder** (FR-IOT-034). These are rule-engine
  work, not capture.
- **TimescaleDB storage** (FR-IOT-021..024, BRU-IOT-01): readings are still a PostgreSQL table. This is an
  infrastructure decision that predates this audit.
- **Back-pressure shed records** (FR-IOT-020): the in-process ingest has no queue to shed from.
- **Entitlement and the commercial route** (FR-IOT-043, BRU-IOT-13): predictions bind to company
  equipment (M45) only, so every intervention is recorded as internal. Customer assets (M17) have no
  prediction binding yet.
- **Per-device credentials** (FR-IOT-003): credentials are per adapter key, as before.
- **Archive to M62** (FR-IOT-026), **cohort analytics** (FR-IOT-045) and **model suspension on
  precision** (AUT-IOT-17).
- **Owner gaps on fix_real**: the four M48 roles are held only by admin, and there is no M48 data.

## 5. State (17 Nov 2026) — deployed on fix_real

The user approved "commit and deploy".

- **Commit.** `20dc185f` (fix) is on `fix/a03-live-data-and-pending-work`, landed by a compare-and-swap
  `update-ref` from 3efdab37 (the branch had not moved). It is **not pushed**.
- **Backup.** `fix_real_pre_m48_capture_2026-11-17.dump` (46.9 MB).
- **Upgrade.** `-u cd_stream_registry,cd_p03_portal` on fix_real exited 0 with no errors.
  - `cd_stream_registry` is now 19.0.0.2.0.
  - The 6 new tables, the 9 new columns and the nightly health cron (active) are in place.
- **Restart.** 8069 was restarted once (PID 54048 stopped). Supervisor 23964 relaunched it in about 6 s
  (PID 23080), and the log loaded 155 modules with no errors.
- **Verified live:**
  - all 6 new surfaces are served, with decommissioning on streams and devices, Record Outcome on
    predictions, and request / approve / cancel on maintenance windows;
  - the live bundle `1a7066c` contains every new M48 screen and form, and the M45 and M47 screens are kept.
- The deploy was coordinated with the M47 capture session, which held its own fix_real deploy until this
  one finished.

fix_real holds 0 rows in the new registers, so nothing was migrated. The four M48 roles are held only by
admin (§4): no non-admin role holder exists on fix_real to exercise the new captures yet.
