---
id: RR-01
title: "R01 — Foundation & Governance Closure"
series: Revised Implementation Roadmap (RIR) — 11 phases · 55 milestones
derives_from: IR-002 Phases 1–2 (P01-M01…P02-M10 residual items)
evidence_base: >
  IMPLEMENTATION_STATUS_AUDIT_REPORT.md (2026-10-15, 2-pass): G0a 10 PASS · 6 CONDITION · 2 OPEN
  (verdict HOLD on B-01/B-02); G0b 8 PASS · 3 OPEN; fitness 20 PASS · 7 SKIP (evidence
  fitness-20261015T134539Z.json); 8 digest placeholders across 4 compose files; CI never executed
  on a runner; zero coverage artefacts; update_roadmap.py co-located with the remediated roadmap.
status: PLANNED — evidence-derived
---

# R01 — Foundation & Governance Closure

## Charter

| | |
|---|---|
| **Purpose** | Close the external blockers that keep G0a at HOLD, repair the engineering-hygiene defects the audit measured, and put the pipeline and measurement apparatus into genuine execution — before any further feature build |
| **Source phases** | IR-002 P01 + P02 remainders |
| **Entry evidence** | G0a verifier `tooling/gate/verify-gate-g0a.ps1` → `RED-EXTERNAL-BLOCKERS-OPEN`; G0b-9/10/11 OPEN; fitness SKIPs FF-03/13/19/26/30/32/37 |
| **Exit** | G0a and G0b re-run and PASS (or Steering override recorded in GV-003); `verify-gate-g2.ps1` and `verify-gate-g9.ps1` exist so no roadmap gate is ever missing |
| **Evidence rule** | Every task cites the audit finding or artefact that proves it is outstanding |

---

## Milestone R01-M01 — External blocker closure (B-01, B-02, and the E1 conditions)

**Evidence:** gate-g0a-2026-10-01.json — `B-01 OPEN`, `B-02 OPEN`, verdict `RED-EXTERNAL-BLOCKERS-OPEN (HOLD)`.

| ID | Task | Evidence basis | Produces | Verify |
|---|---|---|---|---|
| R01-M01-T01 | Sign and send the DEP-31 engagement letter (`docs/p01-m02/DEP-31-engagement-scope.md` already drafted) — 6–10 week external lead, the longest on the critical path | G0a B-02 `OPEN`: "the external opinion (6-10 wk) and Board minute are outside any codebase" | Countersigned engagement | Letter reference in GV-003 |
| R01-M01-T02 | Convene the Board: minute D-001 charter approval, constitute Steering/ARB/DP Forum, appoint the PDPA-required Chief Data Officer and the Programme Content Lead | G0a B-01 `OPEN`; audit finding P-1: "a statutory PDPA role no source document appoints" | Board minutes; named CDO | Minute filed; GV-003 rows created |
| R01-M01-T03 | Receive the DEP-31 opinion, answer the five questions (§0.7.1 Q1–Q5), take D-13 (Option A/B/C) and re-scope P03-M09 residency build if Option B/C selected | §0.7.1: "Until D-013 is taken, P03-M09 builds Option A… the moment the opinion lands, re-scope" | Minuted D-013 | GV-003 entry with re-scope ruling |
| R01-M01-T04 | Settle the SoW F-08 amendment signature and D-002 super-user named individuals | G0a B-11/B-12 `CONDITION`: "amendment signature is external"; "named individuals are external" | Signed amendment; D-002 names | GV-003 rows closed |
| R01-M01-T05 | Execute the 4-week B-06 legacy profiling across the 48-source register already issued | G0a B-06 `CONDITION`: "register + ruling framework issued; the ~4-week profiling itself is execution" | 48 profiled sources with quality reports | Register rows complete |

---

## Milestone R01-M02 — Engineering hygiene: fitness SKIPs, digests, environment defects

**Evidence:** fitness run 2026-10-15 — 7 SKIP (`FF-03, FF-13, FF-19, FF-26, FF-30, FF-32, FF-37` all "script missing" while `tooling/scripts/check-vendor-clean.sh` exists); 8 `PLACEHOLDER-RESOLVE` occurrences (core/novu, intelligence/clickhouse, asset-ml×3 incl. Kafka brokers, msp×3); audit V-3/V-6/V-9/V-12; D-2.

| ID | Task | Evidence basis | Produces | Verify |
|---|---|---|---|---|
| R01-M02-T01 | Fix the fitness runner's script-resolution path so FF-03 finds `check-vendor-clean.sh`, then implement or correctly re-classify the six other skipped checks (FF-13/19/26/30/32/37) | Audit V-3: "the FF-03 script actually exists in tooling/scripts/ — the runner looks in the wrong path" | `tooling/fitness/run.py` with 0 unexplained SKIPs | `python tooling/fitness/run.py` → ≥26 executed checks, 0 FAIL |
| R01-M02-T02 | Run `tooling/scripts/resolve-digests.ps1` to completion and replace all 8 placeholder digests (novu, clickhouse, kafka×3 asset-ml, ×3 msp); remove the cosmetic `:latest` tag from the ceph entry | Audit V-6 + V-12; grep count 8 across 4 compose files | Fully pinned compose files | `grep -c PLACEHOLDER-RESOLVE infra/compose/*.yml` → 0 |
| R01-M02-T03 | Add root `pyproject.toml` pytest config (`addopts = --import-mode=importlib`) so `pytest services` collects without the manual flag | Audit V-9: 8 packages fail collection by default | Fixed pytest config | `python -m pytest services -q` collects 202+ |
| R01-M02-T04 | Close the workstation RED: BitLocker on (elevated `manage-bde -on C:`), re-run `verify-workstation.ps1` to GREEN | P02-M01 record: "BitLocker… stays RED until the operator runs manage-bde" | GREEN workstation record | `tooling/workstation/verify-workstation.ps1` 0 FAIL |
| R01-M02-T05 | Archive `roadmap/update_roadmap.py` (move to `roadmap/_archive/` with a warning header) so the remediated IR-002 cannot be silently regenerated; reconcile the 35-vs-28 count inside `AUDIT_REPORT.md` | Audit D-2, D-4 | Archived script; corrected audit header | Folder check + count reconciled |

---

## Milestone R01-M03 — First real CI execution and budget measurement

**Evidence:** audit V-4 — "ci.yml is complete (17 stages) but there is no run evidence; pipeline budgets are unmeasured"; repo has no remote CI history (git log shows local commits only).

| ID | Task | Evidence basis | Produces | Verify |
|---|---|---|---|---|
| R01-M03-T01 | Push the repository to its remote with branch protection per `docs/guides/branch-protection.md` | Local-only git history (98 commits, no remote evidence) | Protected `develop`/`main` | Remote repo shows branches + protection |
| R01-M03-T02 | Provision the CI secrets/vars the workflow expects (PACT_BROKER_URL, FIX_A11Y_*) from the secret store — never literals | ci.yml references `secrets.PACT_BROKER_URL`, `vars.FIX_A11Y_USER` | Configured repo secrets | Workflow env resolves |
| R01-M03-T03 | Execute the first pre-merge run on a real runner; fix every red stage it exposes (expect the unit `--cov-fail-under=80` and localisation stages to fail initially — that is the measurement working) | Audit V-4/V-5; ci.yml stages 4/10 specify gates never executed | Green-or-honestly-red first run + fixes | Run URL archived in `docs/traceability/evidence/` |
| R01-M03-T04 | Execute the first nightly run (full integration profile + journeys) and the scheduled doctor-on-clean-runner (DE-20) | ci.yml `schedule: cron "0 18 * * *"`; P02-M10-T07 never ran | Nightly evidence | Two green nightly runs |
| R01-M03-T05 | Publish the measured pipeline budgets against §0.8.4 (pre-commit <30 s, pre-merge <20 min, nightly <3 h) and apply BG-01…BG-05 remedies where exceeded | §0.8.4: "the budget is a design constraint, not an aspiration" | Budget report | Report filed; overruns have named remedies |

---

## Milestone R01-M04 — Measurement harness: coverage, doctor, onboarding

**Evidence:** audit V-5 — "no coverage measurement anywhere; no `.coverage`/`coverage.xml`/`htmlcov` artefacts exist" although ci.yml stages specify `--cov-fail-under=80` and a 100% financial/tax job; G0b-10 OPEN.

| ID | Task | Evidence basis | Produces | Verify |
|---|---|---|---|---|
| R01-M04-T01 | Wire `pytest --cov` across addons with marker split: estate gate 80%, `financial or tax` marker gate 100%; define the marker set (cd_tax_engine_bd, cd_payroll_bd, cd_billing_engine, cd_gl_ext, pricing/settlement/reconciliation services) | ci.yml unit stage lines; audit V-5 | Coverage config + first measured report | `--cov-fail-under=80` run produces a report |
| R01-M04-T02 | Publish the baseline coverage number per module and register the gap-to-80% as burn-down stories (expect first measurement well under 80 — record it honestly) | DoD-03; P-3 capacity honesty principle | Coverage baseline register | Register with per-module % |
| R01-M04-T03 | Re-run `doctor.ps1` end-to-end with the Odoo runtime up (checks 6/7/10/13/14 currently SKIP on a cold host) and record all 14 | doctor.ps1 header: "checks 2/5/6/7 degrade to SKIP" | Full 14-check GREEN record | Doctor JSON evidence |
| R01-M04-T04 | Execute the onboarding SLA measurement with one joiner on `core` (budget 1.6–2.7 h; >4 h is a defect against BE-001) | G0b-10 OPEN: "per-joiner measurement - human execution at team mobilisation" | Measured SLA record | `docs/guides/onboarding-sla.md` row filled |

---

## Milestone R01-M05 — Gate closure and the missing verifiers

**Evidence:** gates G2 and G9 are the only two of the 12 roadmap gates with no verifier file (audit §3); G0b-11 requires the G0a override recorded or pass.

| ID | Task | Evidence basis | Produces | Verify |
|---|---|---|---|---|
| R01-M05-T01 | Write `tooling/gate/verify-gate-g2.ps1` — 10 criteria from IR-002 `P05-M10` (app in daily use, 24-h offline zero-loss, ≥15% route gain, ≥95% inventory accuracy, ≥60% online booking, paper withdrawn, L6 journeys 1–3 nightly, gate profile, Steering sign) | Audit finding: "`verify-gate-g2.ps1` does not exist — one of only two missing gate verifiers" | G2 verifier | Verifier runs and reports honestly |
| R01-M05-T02 | Write `tooling/gate/verify-gate-g9.ps1` — criteria from IR-002 `P12-M10` (decommission complete, hypercare exit, docs/training closure, security/compliance closure, PIR filed) | Audit finding: "no G9 verifier" | G9 verifier | Verifier runs |
| R01-M05-T03 | Re-run G0a after M01 lands: target 16 PASS · 0 OPEN; if any E1 remains, obtain the Steering override recorded in GV-003 (never silent) | G0b-11 OPEN: "G0a verdict HOLD… G0b entry requires the override recorded in GV-003" | G0a PASS or recorded override | `verify-gate-g0a.ps1` green / GV-003 row |
| R01-M05-T04 | Re-run G0b after M02–M04: target 11 checks 0 OPEN | G0b 8P/3OPEN | G0b evidence JSON | `gate-g0b` verdict ≥ PASS-with-conditions |
| R01-M05-T05 | Publish the R01 exit report: blockers closed, hygiene green, first CI budgets, coverage baseline — the evidence pack Steering needs to authorise R02/R03 build spend | §0.9 escalation discipline | R01 exit record | Filed in `docs/traceability/` |

---

**Sequence:** M01 → M02 → M03 → M04 → M05 (M02–M04 may parallel M01's external waits; M05 requires all).
