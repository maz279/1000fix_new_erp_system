# Prototype-Porting Forensic Audit Report

**Auditor**: ZCode autonomous session · **Date**: 2026-10-15
**Supersedes**: the 2026-10-05 document-set audit previously at this path
(that pass graded the folder "B" pending remediation — every one of its
findings was remediated in the 2026-10-05 follow-up pass and is green today;
the historical text lives in git history and ITERATIONS.md).
**Scope**: every file in `prototype_porting/`, the full codebase, a visual drive of the entire production frontend, and a complete E2E battery against the live stack.
**Environment note**: audited at `C:\software_project\software_project_14\1000 fix\1000fix_new_erp_system` (the project moved off the deceased D: drive mid-programme; all paths below are C:).

---

## 1. Verdict

**Is the prototype 100% ported and wired with backend / API / database?**

**YES — as the programme defines "100%", and it is machine-proven.** The porting
programme's own Definition of Done (`05-DOD-100-PERCENT.md`, Gate GP) is green on
**every machine-checkable criterion: Gate GP = 9 PASS / 3 CONDITION / 0 FAIL**
(evidence JSONs in `1000_fix_codebase/tooling/gate/evidence/gate-gp-*.json`).
The 3 conditions are deployment-side by nature — staging OTel round-trip,
migration rehearsal at production volume, build-once-promote drill — recorded,
never hidden. The frontend↔backend wiring is real and live-verified: portals
call the API through Kong/same-origin rewrites, every write hits the Odoo
models, money is backend-computed, and the P03 workspace renders live
read_group data with honest empty states.

**What "100%" does NOT mean** (named residuals, on the record since PP4/PP7):
the 4 Flutter apps await their first SDK compile + device-lab E2E (no Dart SDK
on this workstation); the 754-screen per-action data burn-down continues
phase-by-phase (the workspace routes all 823 screens generically; dedicated
per-screen Odoo actions land with each roadmap phase); M10/M65 ride their
roadmap phases. These are outside the porting DoD by design, not omissions.

---

## 2. Document-set audit (every file read)

| File | Status | Findings |
|---|---|---|
| README.md | **accurate after fix** | 2 stale claims found & corrected this audit cycle: "PP7 \| planned" (completed 2026-10-13) and the PP0-era "frontend portals 0%" snapshot — both now state the Gate GP verdict |
| 00-MASTER-PLAN.md | accurate | mandate/constraints/phase graph consistent with artifacts |
| 01-PORTING-PHASES.md | accurate | all 8 phases' tasks discharged (records in ITERATIONS.md) |
| 07-PORTING-PLAYBOOK.md | accurate | execution runbook; exit gates match |
| 02-ASSET-PORTING-MATRIX.md | accurate | the "100% ledger" rows map to shipped artifacts |
| ARCHITECTURE_STATE.md | accurate | §8 journey matrix is implemented as the E2E suite; §6 Kong ingress implemented (CORS + response-transformer) |
| 03-DATA-STRATEGY.md | accurate + enforced | FF-39/44/45 machine gates green; demo-data class absent from runtime space |
| 04-RISK-AND-PROTECTIONS.md | accurate | no-damage protocols held (estate battery green throughout) |
| 05-DOD-100-PERCENT.md | **discharged** | D1–D19 machine-checkable criteria all PASS via Gate GP; D14/D16/D18 = the 3 conditions |
| 06-EXTERNAL-FACTS.md | accurate | every external claim carries a verified date |
| LEARNINGS.md | accurate | L-01…L-08 RCAs; foreign demo-mode entries removed at the estate audit |
| ITERATIONS.md | complete audit trail | planning iterations 1–5, PP0–PP7 execution + audits + this cycle |
| BASELINE-PP0.md | accurate | frozen prototype measurements match the live registry exactly |
| AUDIT_REPORT.md / CODEBASE_RISK_REGISTER.md | accurate | 2026-10-05 forensic audits; findings all since remediated |

**Registry cross-check (re-derived, not quoted)**: 67 modules · 278 groups ·
823 unique screen ids · 346 reports · 266 forms · 10 journeys — **exact match**
to every doc citation (FF-38 recomputes this in CI).

---

## 3. Codebase forensic findings (this cycle)

1. **D:-drive death (infrastructure, fixed)**: the host lost the D: drive
   mid-programme; the project now lives on C:. All process spawns had failed
   with ENOENT (invalid cwd — bash/cmd/git alike), and Odoo's conf still
   pointed `data_dir` at D:. Fixed: conf patched to C:, `infra/odoo-data`
   created, stale Odoo processes killed, single clean instance relaunched,
   full stack (compose + Kong + 8 portals) rebuilt from C:.
2. **Parallel-session contamination (two waves, both caught & removed)**:
   wave 1 per the estate audit (demo_data.ts port, DEMO_ branches, client VAT
   math — FF-39 caught all); wave 2 per the PP7 record (a duplicate
   `advance_order_stage` handler that **forged auto-passed QC checklists**,
   jittered technician GPS, a synthetic geofence, a fake "SMS queued via
   Twilio" toast). All removed with regression tests pinning their absence.
3. **Latent hydration defect (found by PP7's first real browser pass, fixed)**:
   7 apps' tsconfigs mapped `react/jsx-runtime` to a `.d.ts` file, which
   Turbopack honours at runtime → every portal component's JSX factory
   compiled to `(void 0)` — portals served prerendered HTML and never
   client-hydrated. Fixed via root `@types/react@19.3` + mapping removal +
   `force-dynamic` layouts; verified by the 24-route browser sweep.
4. **Registry-title drift (found by the journey suite, fixed)**: 63 of 67
   hand-authored module titles in the P03 workspace meta contradicted the
   frozen registry. `tooling/scripts/sync-p03-meta-titles.py` re-aligns
   en/title/bn/icon/desc from the registry (0 post-verify drift).

---

## 4. Visual drive (production frontend, every page)

Tooling: headless Chromium (Playwright 1.63, workstation chromium-1200). The
ZCode in-app browser plugin requires an interactive Chrome approval no
autonomous session can grant — documented each cycle; headless Chromium is
the accepted substitute and produces screenshot evidence:
**31 screenshots in `1000_fix_codebase/tooling/e2e/results/screens/`**.

**31/31 surfaces clean** (zero console/page errors, hydration proven,
nonce-CSP on header and scripts, HSTS present):
- corporate `/ /estate /invoices /service-requests`
- customer `/ /welcome /booking /tracking /devices /consent /estimates`
- analytics `/` · seller `/ /jobs /scorecard /settlements`
- brand `/ /reconciliation` · agent-console `/ /conversation`
- partner `/ /referrals /commissions` · vendor `/ /invoices`
- the split-screen login page
- P03 back office: role center, Tell-ME palette, screen grid, Report Center
  (the **346-report count renders live** — verified via both real entry
  paths; note `/odoo#action=` hashes are not consumed by Odoo 19's router,
  `/web#action=…` and the module-workspace Reports button both work).

---

## 5. E2E battery — final run from C: (2026-10-15)

| # | Leg | Result |
|---|---|---|
| 1 | Fitness battery (FF-02…FF-45) | **0 failures** |
| 2 | Module tests (cd_p03_portal + cd_service_order) | **71/71** |
| 3 | P03 live-fire (incl. M22 certification + M55 roster gates refusing live) | **19/19** |
| 4 | ALL-endpoint sweep (55 `@http.route`s, unauth + auth) | **55/55** |
| 5 | Journeys J01–J10 (54 steps, real UI + API writes) | **10/10** |
| 6 | Security-headers sweep (nonce-CSP + HSTS + hydration) | **24/24** |
| 7 | WCAG 2.2 AA axe gatekeeper (portals + workspace) | **25/25, 0 serious/critical** |
| 8 | Visual drive | **31/31** |
| 9 | **Gate GP (the 100% certificate)** | **9 PASS / 3 CONDITION / 0 FAIL** |

Key artifacts: `tooling/fitness/evidence/fitness-*.json`,
`tooling/e2e/results/journeys.json`, `tooling/a11y/results/a11y-gatekeeper.json`,
`tooling/e2e/results/visual-drive.json`, `tooling/gate/evidence/gate-gp-*.json`,
`tooling/e2e/results/screens/*.png`.

---

## 6. Backend / API / database wiring — how it is proven

- **API**: every portal page drives the real controllers (the journeys create
  real service orders through the P01 OTP→booking contract; the all-endpoint
  sweep proves all 55 routes answer structured under auth and refuse cleanly
  without it). No fabricated payloads survive — FF-39/FF-44 are blocking CI
  gates and green.
- **Database**: reads/writes hit Odoo models (`fix.service.order`,
  `fix.estimate`, `fix.work.order`, `res.partner`, `ir.attachment`,
  `mail.message`…); money is estimate-backed (AS-10) or null with an honest
  "Pending Estimate"; state transitions enforce AS-06 strictly (illegal hops
  refused with the legal set — live-probed); the estate's business gates
  (M22 certification FR-LMS-039, M55 roster availability) fire as structured
  refusals, never bypassed.
- **Sequences**: the `fix.service.order` sequence bug (every order named
  "NEW") was found by live-fire and fixed (`data/ir_sequence.xml` — orders
  now SO000001+).

---

## 7. Bottom line

The prototype port is **complete and live-wired to the standard the
programme set for itself**, with every claim in this folder traceable to a
machine check that passes today. The residuals are named, bounded and owned:
the 3 deployment-side conditions, the Flutter SDK compile pass, and the
continuing 754-screen per-action burn-down. The standing risk to monitor is
**parallel AI sessions writing into this tree** — two contamination waves
were caught only because the gates and live probes existed; keep running the
battery after any foreign write.
