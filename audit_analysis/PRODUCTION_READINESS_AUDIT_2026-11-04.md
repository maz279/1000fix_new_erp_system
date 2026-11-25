# 1000FiX ERP — Production-Readiness Audit (2026-11-04)

> **Resumed audit.** This updates `PRODUCTION_READINESS_AUDIT_2026-10-23.md` after twelve days of
> remediation, the A02–A12 workflow/approval audit programme (30 Oct – 4 Nov), the A06/A07/A09
> control builds, and the merge of the A09 People branch onto the shared integration line.
> Every "verified" row below was re-measured in this session (SQL against `fix_dev`, static
> checks against the working tree, gate verifiers re-run live); items reported by prior sessions
> are cited as such and not re-executed here unless marked.

**Verdict: STILL NOT production-ready — but materially closer, and the blocker profile has changed.**
On 2026-10-23 the estate held critical authorisation holes, fabricated business outputs, and an
unversioned working tree. Today: all ten re-checked security/fabrication fixes from that audit are
present in the committed tree; the shared branch is **committed and pushed to origin**; the
programme's own gates have moved (G3 and G4 now exit PASS-WITH-CONDITIONS; G2 and G9 verifiers
now exist). What remains are (a) the external blockers that have been open since G0a (B-05b and
its cascade), (b) a set of business sign-offs and appointments no code change can make, (c) known
workflow-control gaps documented per area in `C:\software_project\software_project_14\working\`,
and (d) the A09 merge regression this audit re-measured is now **RESOLVED** — reconciled to a
clean 17-path regression (5,237 passed / 0 failed / 185 skipped, single process) and committed
locally as `db14e55a` on `fix/a09-merge` (5 Nov, §5); push/deploy awaits operator approval.

---

## 1. What changed since 2026-10-23 (re-verified today)

| Item | 2026-10-23 state | 2026-11-04 state (evidence, this session) |
|---|---|---|
| Version control | 2,265 uncommitted paths, nothing pushed | Branch `fix/a03-live-data-and-pending-work` at `fdcc2d70`, **identical to `origin/`** (pushed); **92** uncommitted paths in the main checkout |
| Security fixes §3.1–10 (relay, admin prefill, OIDC secret, portal auth, Kong, lifecycle token, P03 `_require_internal` ×11, portal ACLs, finance ACLs, vendor IDOR) | applied same day, uncommitted | **all still present in the committed tree** (grep-verified: relay session fence `route.ts:65`, `_require_internal` count 11, `_vendor_domain` scoped, no `NEXT_PUBLIC_OIDC_CLIENT_SECRET` in source — only stale `.next`/`.mimosa` caches) |
| Fabricated-output fixes §3.11–17 (consolidation fee, NBR ack, payout read-back, wipe certs, DEMO_* KPIs) | applied same day, uncommitted | present (consolidation `50000` absent; wipe cert default `pending_verification` at `fix_data_case.py:927`; no `DEMO_KPIS`/`DEMO_DISPUTES` in portal source) |
| Fabricated governance docs | 15 docs bannered | banners still on the three re-checked (`GV-003`, `BM-2026-10-D001`, `DEP-31` — provenance marker in first 5 lines each) |
| Company setup | main company → 1000 FiX Services Ltd., BDT, Bangladesh | **holding**: company 1 = `1000 FiX Services Ltd.` / Bangladeshi taka / Bangladesh |
| `NEW` order numbering | 825 renumbered, UNIQUE(name) | **holding**: 930 orders, 0 named `NEW`, 930 distinct names |
| Negative estimates | #4 rejected | **holding**: 0 not-rejected estimates with `grand_total < 0` |
| Withholding NULL supplier | backfilled | **holding**: 0 NULLs |
| `ir.cron` wiring | 27 rows in DB (server saw 8) | **104 rows** in `fix_dev` |
| Installed modules | 142 (71 `cd_*`) | **150 (79 `cd_*`)** — A07 bridges, `cd_vehicle_dispatch`, `cd_d365_chrome` etc. |
| Gate verifiers | G2 and G9 missing | **G2 and G9 exist and run** (written after the IR-002 audit flagged them) |
| Chart of accounts | 79 accounts (draft MD-035) | 159 accounts loaded (MD-035 approval still a business item) |
| Area workflow controls | not audited | A02–A12 audited; A03 gap-closure (W1–W9), A06+A11 (S0–S9/R1–R7/E1–E4), A07 (307/307), A09 P0a+P0b **built and deployed**; reports in `C:\software_project\software_project_14\working\` |
| Test estate | 5,087 passed / 0 failed (full) | 4,485–4,492 passing in the 4 Nov shared-branch runs (per session reports); A09 merge regression clean — **5,237 passed / 0 failed / 185 skipped** on the full 17-path gate, §5 |

**Known dev-DB residue (unchanged, accepted):** `Mitchell Admin` partner, `demo` user, 2 Odoo demo
companies (My US Company, My Company (Chicago)), 2 demo activities. The production compose sets
`without_demo = all`; the dev DB is not the production datum.

## 2. Gate status (all 13 verifiers re-run live this session; G8 partially — see its row)

| Gate | PASS | CONDITION | OPEN | FAIL | Verdict |
|---|---|---|---|---|---|
| G0a | 12 | 5 | **1 (B-05b)** | 0 | RED-OPEN-BLOCKERS (HOLD) |
| G0b | 8 | 1 | 1 | 1 | RED (blocked on G0a) |
| G1a | 4 | 4 | 0 | 2 | RED |
| G1 | 4 | 7 | 0 | 1 | RED |
| G2 | 0 | 9 | 1 | 0 | RED-OPEN |
| G3 | 5 | 7 | 0 | 0 | **PASS-WITH-CONDITIONS** (exit 0) |
| G4 | 11 | 7 | 0 | 0 | **PASS-WITH-CONDITIONS** (exit 0) |
| G5 | 5 | 3 | 0 | 2 | RED (PE-004 perf + PE-007 DR drill INCOMPLETE) |
| G6 | 2 | 4 | 0 | 4 | RED (perf/DR INCOMPLETE; hand-signed report rejected as evidence) |
| G7 | 2 | 6 | 0 | 2 | RED (perf/DR INCOMPLETE; Steering sign-off pending) |
| G8 | 1 | 3 | 0 | 2 | RED (G8-1 fitness 8 FAILs; G8-6 FF-27 exit 1). **Verifier trap:** it stalled 25 min at ~2 s CPU waiting on a non-running compose service (ClickHouse suspected) — killed; results from its partial output |
| G9 | 0 | 9 | 1 | 0 | RED-OPEN (G9-10 Steering closure sign-off — human) |
| GP | 4 | 3 | 0 | 5 | RED (verifier's own summary line; portal security headers, journeys 2 unexpected, customer bundle 409/400 KB, fitness FAILs) |

Movement vs 2026-10-23 ("no gate passes, 6 RED"): G3 and G4 now clear their verifiers with
conditions; G2/G9 verifiers exist and run. The cascade is unchanged: **G0a holds on B-05b**, and
per GV-009 proceed/hold is a Steering decision recorded in GV-003 — it cannot be closed in code.

## 3. Area control status (A02–A12; prior-session findings, cited)

Reports and probe evidence: `C:\software_project\software_project_14\working\A NN_Workflow_and_Approval_Report.md` + `A NN_evidence\`.

| Area | Audit verdict (probes) | Remediation state |
|---|---|---|
| A02 | 162/204 GAP (worst after A03) | P1–P3 built (routed floor 13), 2nd pass 31 Oct–1 Nov |
| A03 | approval *rules* good, workflow did not exist; DOFA fail-open | W1–W9 gap-closure built + deployed; 4th pass caught inbox-sudo engine bug |
| A04 | 239/290 GAP; cart-price tampering | C2–C13 controls **committed 4 Nov** on `feat/a04-c2-c13-controls` (4456ba27, 195 files + 1077c062 seed); integrator suites GREEN: 3,321 passed / 0 failed / 228 skipped on `fix_test_a4p` (peer-reported, not re-executed here); open: fresh-DB seed verification, v2 role-holder probes |
| A05 | 103/136 GAP; untrue ESG/DoE figures | build brief issued 4 Nov |
| A06 | report §6 S0–S9/R1–R7 | **built + deployed 4 Nov** (shared `3d8d33e9`, pushed); S0 archive run; synthetic approvers |
| A07 | fully implemented 4 Nov | **307/307 probes** with live switches |
| A08 | finance: payee not pinned after approval, period lock sudo, one accountant releases 50M | B1–B3 build in progress (`A08_build\`) |
| A09 | 316/380 GAP; payroll bank diversion after approval | **P0a+P0b deployed**; R2 rounds built; 8 real gaps open; **merged + committed `db14e55a`** (§5) |
| A10 | report in `working/` | — |
| A11 | M63 rule book/delegation writable by all; DQ inverted | E1–E4 **built + deployed** with A06 |
| A12 | 53 roles menu-only; self-approved access | report only |

**Cross-area truth:** the workflow/approval engine (M63/DOFA) now exists and is enforced in the
built areas, but A05, A08 remainder, A10 and A12 remediations are not yet built, and real
**approver appointments remain synthetic** — a business action.

### 3b. Roadmap phase coverage (R01–R11 → 4 Nov state)

The 11 `Revise_roadmap` phase docs each carry their own frontmatter status from the
2026-10-22 zero-trust audit; the fresher 4-Nov evidence is the area programme above and this
report's gates. Bridge (phase-doc status → 4-Nov reality):

| Phase | Scope | 4-Nov state |
|---|---|---|
| R01 | Foundation & governance closure | Gates G0a/G0b: tree committed+pushed, all 10 Oct-23 security fixes holding; still HOLD on external B-05b |
| R02 | Kernel & service-core runtime hardening | A02 P1–P3 built (2nd pass done); A03 W1–W9 built + deployed; G1/G1a verifiers still RED |
| R03 | Field ops, inventory, offline engine | A06 S0–S9/R1–R7 **built + deployed** (4 Nov); offline Flutter apps remain shells (§6.4) |
| R04 | Money, tax, document depth | A04 three remediation suites (final suite finished green 4 Nov after the session died — peer-verified); A08 B1–B3 built, B4/B5 died mid-build (`a08wt` 188 dirty) |
| R05 | Agreements, contact centre, PDPA | A05 103/136 GAP; build brief issued; `a05wt` 80 dirty files uncommitted (loss risk §6.3) |
| R06 | People, payroll, quality full depth | A09 P0a+P0b deployed; round-2 built; **merge committed `db14e55a` after a clean regression** (§5) |
| R07 | Asset businesses & event-bus migration | A07 fully implemented, 307/307 probes; R07's G6 dual-write/Kafka findings superseded by the A07 build; G6/G7 still RED on perf/DR *evidence* (external) |
| R08 | Marketplace, settlement, partner channel | A04 cart-price tampering fixed; A10 report only — 53 roles menu-only (unbuilt) |
| R09 | Intelligence, warehouse, IoT completion | models + metric-registry suite green (44 tests); ClickHouse warehouse not running on workstation; STT is echo-level (G8-3/4/5 conditions) |
| R10 | Multi-entity, module closure, pre-production | A11 E1–E4 built + deployed with A06; consolidation now posts real aggregates; A12 roles report only; env-ladder beyond local remains unprovisioned |
| R11 | Cutover, decommissioning, programme closure | NOT EXECUTED (Month-36); G9 RED-OPEN on Steering sign-off; no cutover has occurred |

## 4. Runtime liveness (this session)

- **Odoo 19 boots and serves on `fix_dev` (port 8069, HTTP 200)** with 150 installed modules —
  re-confirmed on a fresh process started for this audit.
- Authentication (`admin`/`admin`, db `fix_dev`): OK (uid 2).
- Menu count served: **976 menus** total (196 was the *custom-menu* figure at the Oct-23 audit;
  not directly comparable).
- **P03 workspace surface probe:** all **139/139** A09-area model-list screens
  (M21/M55/M56/M57/M22/M58/M59 — the extraction in `scratch/a09_screens_cols.json`) answered
  `/p03/model/records` with **0 dropped columns and 0 errors** (requested-minus-labels = ∅ for
  every screen; `hr.employee` sample: 51 rows, 7/7 labels). Scope note: this proves the freshly
  started process serves the A09 area's surfaces; the A06 deploy record separately reports
  663/663 surfaces served after the 4 Nov restart.
- **Full-estate form probe (this continuation, 4 Nov ~22:00):** every workspace **form** model
  extracted from the `cd_p03_portal` static JS via `form_fields.forms()` — **576/576 distinct
  models served with 0 endpoint errors** across all areas (a02–a12). 4 models returned dropped
  columns; verified against source:
  - `fix.partner.nid_number` — **by design**: field carries
    `groups="cd_entity_config.group_pii_unmasked"` (`cd_partner/models/fix_partner.py:57`);
    ordinary operators see `masked_nid`. Not a defect.
  - **Form/model drift (real, minor):** the a04 `fix.price.floor` form requests `cost_basis`
    (field exists nowhere), the a10 `fix.document.template` form and the a12
    `fix.country.pack.line` form request `active` (field not defined on those models — it exists
    on `fix.country.pack` but not its lines). The workspace silently drops these columns
    (the known silent-column-drop trap); fix by removing the columns from the forms or adding
    the fields.
  - 24 models returned 0 rows (unpopulated masters — a06 import/LC/tariff, a07 lease/IoT,
    calibration, a03 datasets etc.); expected on a dev DB, listed in
    `scratch/form_probe_results.json` for the data-migration checklist.

## 5. The A09 merge regression — RESOLVED (merge committed 5 Nov)

The blocker cited in the 4 Nov draft of this report ("74-failure block reproduces
deterministically, merge not committable as-is") is closed. Full trajectory:

- **Run3 (4 Nov, single process, 16 paths, `merge_run3.txt`): 75 failed / 4,791 passed.** Two
  measurement corrections established afterwards: run3's path set was **narrower than the
  planned 17-path gate** (it executed 5,051 tests vs the gate's 5,422 collected IDs — no
  `f_asset_facilities` tests ran at all), and the earlier "consignment/workshop
  order-dependent pollution" diagnosis does not explain run3's 75 (that block was
  stale-process interference in run2; run3's failures were real, per-class causes below).
- **Gate1 (first true 17-path run, 5 Nov ~00:00): 33 failed.** The largest class was
  ENVIRONMENT, not code: `cd_asset_finance_hse_bridge`, `cd_vehicle_dispatch` and
  `cd_asset_workorder_spine` were uninstalled on `fix_test_a9merge` — installed via `-i`
  (exit 0). One further failure was a midnight-crossing artifact (module-level TODAY frozen at
  collection 23:55, executed after 00:00).
- **Gate2: 17 failed — two code-reconciliation classes.**
  - *M22 first-run fixtures (13):* the merged M22/FR-LMS-039 dispatch gate refuses technicians
    holding no valid dispatch-gating certification, and the A07 bridge booking writes
    `technician_id` onto `fix.vehicle.assignment`, firing BRU-HSE-07 (employee driving
    licence). Mocking model methods is impossible in Odoo 19 (registry classes reject the
    patches), so the fixtures now create real gating competencies — **scoped to the device
    type**; an unscoped one is not enough — plus a driver licence each. The real eligibility,
    licence and vehicle gates stay live.
  - *UTC+6 frame splits (4):* the ORM stamps `context_today` (Asia/Dhaka) while tests asserted
    the UTC date; the two diverge 18:00–24:00 UTC. Asserts aligned (HSE return-to-work, PPE
    replace-by, M57 dispute deadline, attendance night-consent).
- **One split was a MODEL defect the merge created — fixed in the model.** M55 technician
  availability (`fix_attendance.action_check_technician_availability`, also a write-hook on
  `fix.work.order.technician_id`) read the UTC clock while the night-consent recheck decides on
  the Dhaka date — a **withdrawn BLA s.109 night consent failed open 00:00–06:00 Dhaka**. The
  check now reads `context_today`.
- **Gate3: 8 failed — the mirror class** surfaced by the model fix: every other fixture that
  built a "M55 satisfied" roster slot had it on the UTC date. The alignment rule that emerged
  (a first blanket alignment over-corrected and broke 4 expiry-boundary tests, then was
  narrowed): **per consumer** — roster slots (M55) on the context date; certification
  status/lapse/eligibility fixtures on UTC, the clock those models themselves run. Final
  verification of the four affected files: **145/145**.
- **Gate4 (the deciding run — verbatim 17-path command, single process, `-p no:randomly`,
  `fix_test_a9merge`, 5 Nov): 5,237 passed / 0 failed / 185 skipped / 3 subtests passed,
  1:39:36.** (5,237 + 185 = the 5,422 collected IDs; nothing deselected.)
- **Merge committed: `db14e55a`** on `fix/a09-merge` (parents `fdcc2d70` + `ec94898f`),
  working tree clean, all pre-commit hooks green (ruff, ruff-format, pylint-odoo SQL-02/XS-08,
  gitleaks). Hook note: ruff I001 re-sorted one import in `cd_field_service/models/__init__.py`
  at commit time; the module was smoke-tested (31/31) before the recommit, since import order
  can affect Odoo model load order.

**Root-cause taxonomy of the whole reconciliation:** (a) environment — three modules
uninstalled on the regression DB; (b) engine-env ACLs — post-W4 the approval engine applies
decisions in the *approver's* env, and A09 decider groups held `perm_write=0` on their own
models (13 ACL lines flipped to the estate convention: `write=1` plus the guard mixin refusing
direct state writes; deployment consequence: line managers deciding attendance regularisations
must hold the attendance officer role); (c) tests reconciled to composed controls —
dispatcher-only work-order assignment (A02), AUT-FLT-05 suspended-licence births, A07 vehicle
dispatchability documents, M21 exit notice, M62 second HSE officer; (d) UTC+6 frame alignment
including the M55 model fail-open above; (e) data-driven fixtures instead of mocks.

**Residual (flagged, NOT fixed):** `fix_competency.py:750` `dispatch_eligibility` reads
`fields.Date.today()` (UTC) internally — a certificate expiring UTC-today is still accepted
for a Dhaka-tomorrow job (one-day expiry-boundary fail-open). Recorded for follow-up.

**Not pushed.** Push, `fix_dev`/`fix_test` refresh and Phase B deploy await explicit operator
approval, per standing instruction.

## 5a. Fitness drift since 31 Oct (re-measured this continuation)

The G8-1/GP-9 "fitness clean" blocker currently reads **8 failing checks** — but only **3 are
new** since 31 Oct (the other 5 — FF-20/21/22/25/27 — already failed on 31 Oct and are known).
New failures and causes (checkers re-run live, shared checkout):

| Check | Failure | Cause (verified) | Fix |
|---|---|---|---|
| FF-06 cross-table | 6 violations | raw SQL in `cd_p03_portal/tests/test_a02_c3_control_kpis.py` referencing `fix_cash_shift`/`fix_data_wipe_certificate`/`fix_service_order`/`fix_field_order` (AS-01) | A02 session's test file; refactor to the published API or scope the checker for test files |
| FF-47 isolation rules | 3 modules drifted on shared tip: `cd_requisition`, `cd_stream_registry`, `cd_vendor_portal` | A06/A07 deploys moved the shared branch without regenerating isolation rules | `python tooling/generators/generate-isolation-rules.py` + commit |
| FF-48 deployment wiring | ~26 `event_without_consumer` NEW + 1 `button_not_allowed` (a06 m15.js `action_approve`) + 2 FIXED | baseline `deployment_wiring_baseline.json` stale after the A06/A07 event-contract changes | regenerate baseline (`--update-baseline`) with the A06/A07 events/consumers settled |

Two traps measured while re-running these: **FF-48 cannot run inside worktrees** (it parses
`vendor/odoo/odoo/orm/models.py`, and vendor is an empty submodule in worktrees — crashes
`FileNotFoundError`; run it from the main checkout only), and **the merge worktree's FF-47 drift
was 6 modules, not 3** — the A09 modules `cd_attendance`, `cd_hse`, `cd_talent` plus the shared
three. **Regenerated in the merge worktree before the commit** (8 files; generator `--check`
clean at `db14e55a`), so the merge ships no new isolation-rule drift.

## 6. What still blocks production (ordered)

1. **External (since day one):** B-05b and the G0a cascade; real bKash/Nagad/SSLCOMMERZ
   credentials and protocols; NBR IVAS; bank BEFTN read-back; independent penetration test;
   Board/Steering decisions; legacy data migration with sign-off; cutover.
2. **Business sign-offs no code can supply:** MD-035 CFO approval; real approver appointments
   (currently synthetic) and Finance countersign; the three "DEPLOY: tell user" decisions in the
   A09 integration TODO (NID/TIN post-migrate SYNTHETIC reads; competency device types blocking
   `fix_dev` job creation; first-cron committee moves).
3. **Engineering:** the A09 merge is **committed `db14e55a`** (5 Nov, §5) — remaining there:
   push + deploy on operator approval, and the flagged `fix_competency.py:750` UTC-clock
   follow-up; the 3 form-drift
   columns (§4); the FF-06/FF-48 baseline regenerations (§5a); A08 remainder, A05, A10, A12
   remediation builds; 92 uncommitted paths on the main checkout; stale `.next`/`.mimosa`
   caches still contain pre-fix artifacts and should be pruned before any image build; the
   Oct-23 "Still open" infra items that need a real cluster (TLS, DNS, registry push).
   **Near-term loss risk (peer-reported 4 Nov):** worktree `a05wt` (80 dirty files — A05's
   completed work) and `a08wt` (188 dirty — A08 builders B4/B5 died mid-build) are uncommitted;
   one `git reset` each away from loss. Commit or WIP-branch them before any worktree cleanup.
4. **Mobile and engines:** the four Flutter apps remain UI shells; OCR/STT/conversational-AI/
   document-rendering engines and OpenTelemetry export remain absent (unchanged).

## 7. Method

- SQL (read-only, `docker exec compose-postgres-1 psql -U fix -d fix_dev`) for every DB row count.
- `grep`/`find` on the working tree for every static fix check.
- Gate verifiers executed fresh: `powershell -File tooling\gate\verify-gate-*.ps1` (exit codes captured).
- pytest re-runs: single-file on `fix_test_a9merge`; full merge regression in background.
- Prior-session evidence (area reports, probe outputs) cited by path, not re-executed, except
  where this report says re-measured.

*Report status: FINAL — §5 updated 5 Nov with the resolved A09 merge regression and the
two-parent commit `db14e55a` (not pushed). Gate, runtime, area, and risk sections are complete.*
