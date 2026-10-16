# Pipeline Budget Measurement Report — Milestone R01-M03 (PE-004 / §0.8.4)

- **Date:** 2026-10-16
- **Milestone:** R01-M03 — First real CI execution and budget measurement
- **Repository:** `maz279/1000fix_new_erp_system` (branch: `develop`)
- **Evidence Base:**
  - `docs/traceability/evidence/ci-pre-commit-run-20261016T070322Z.json`
  - `docs/traceability/evidence/ci-pre-merge-run-20261016T070401Z.json`
  - `docs/traceability/evidence/ci-nightly-run-20261016T070749Z.json` (Run 1)
  - `docs/traceability/evidence/ci-nightly-run-20261016T071126Z.json` (Run 2)
  - `docs/traceability/evidence/branch-protection-rules.json`
  - `docs/traceability/evidence/ci-secrets-provisioned.json`

---

## 1. Executive Summary & Budget Conformance

Under roadmap §0.8.4, pipeline budgets are treated as **hard design constraints, not aspirations**.
Every profile was executed against the live system and measured with high-resolution telemetry.

| Profile | §0.8.4 SLA Budget | Measured Duration | Headroom / Margin | Conformance Verdict |
|---|---|---|---|---|
| **Pre-Commit** | $< 30\text{ s}$ | **0.69 s** | $29.31\text{ s}$ ($97.7\%$ headroom) | **PASS** |
| **Pre-Merge** | $< 20\text{ min}$ ($1,200\text{ s}$) | **32.30 s** | $1,167.70\text{ s}$ ($97.3\%$ headroom) | **PASS** |
| **Nightly (Run 1)** | $< 3\text{ h}$ ($10,800\text{ s}$) | **214.74 s** ($3.58\text{ min}$) | $10,585.26\text{ s}$ ($98.0\%$ headroom) | **PASS** |
| **Nightly (Run 2)** | $< 3\text{ h}$ ($10,800\text{ s}$) | **209.88 s** ($3.50\text{ min}$) | $10,590.12\text{ s}$ ($98.1\%$ headroom) | **PASS** |

**Overall Result:** $100\%$ of pipeline execution profiles comply with statutory §0.8.4 budget thresholds with substantial headroom.

---

## 2. Pre-Merge Stage-by-Stage Breakdown

The pre-merge profile exercises Stages 2 through 12 and Stage 15 as defined in `.github/workflows/ci.yml`.

| Stage ID | Description | Duration | Status | Key Output / Metric |
|---|---|---|---|---|
| **stage-02-lint-type** | Ruff linting & formatting check | 0.16 s | PASS | 0 errors across `addons`, `services`, `contracts`, `i18n`, `tooling` |
| **stage-03-model-registry** | Fitness rules & architecture bounds | 22.01 s | PASS | 26 checks evaluated, 0 failures (FF-01…FF-37) |
| **stage-04-unit** | Services unit suite & coverage | 0.88 s | PASS | 202 service tests passed; baseline measured |
| **stage-06-contract** | OpenAPI 3.1 contract schema verification | 0.06 s | PASS | 3 API specs valid (`customer`, `corporate`, `technician`) |
| **stage-07-event** | Outbox event schemas & status parity | 0.06 s | PASS | Event envelope fields verified against `fix.event.outbox` |
| **stage-08-security** | Secret leaks & digest immutability | 0.05 s | PASS | 0 `PLACEHOLDER-RESOLVE` occurrences in `infra/compose/` |
| **stage-09-architecture** | Doctor environment verification | 1.72 s | PASS | 14 sanity checks evaluated (12 PASS, 2 SKIP) |
| **stage-10-localisation** | Translation parity & completeness (DoD-08) | 0.08 s | PASS | 100% completeness verified across PO/POT catalogs |
| **stage-11-bundle** | Next.js client route gzip bundle budget | 0.11 s | PASS | Total bundle 251.6 KB $\le 400\text{ KB}$ budget |
| **stage-12-accessibility** | axe-core WCAG 2.2 AA audit | 7.15 s | PASS | 7 live routes audited; 0 violations |
| **stage-15-infrastructure** | Infrastructure configuration drift | 0.08 s | PASS | Odoo configuration matches generator baseline (REPO-15) |
| **TOTAL** | Pre-Merge Execution | **32.30 s** | **PASS** | **Budget limit: 1200 s** |

---

## 3. Nightly Integration & User Journey Breakdown

The nightly profile exercises the full end-to-end integration footprint, including browser automation journeys and clean-runner environment verification.

| Stage ID | Description | Run 1 Duration | Run 2 Duration | Status | Notes |
|---|---|---|---|---|---|
| **nightly-journeys** | 10 Critical User Journeys (Playwright) | 158.30 s | 154.31 s | PASS | J01–J10 end-to-end user flows complete |
| **nightly-visual-drive** | 31-Route Visual Regression Drive | 34.26 s | 33.57 s | PASS | 31 portal responsive views validated |
| **nightly-headers-sweep** | 24-Point Security & CSP Headers Sweep | 20.58 s | 20.37 s | PASS | All 8 portal security headers verified |
| **nightly-de20-clean-doctor** | Clean Runner Doctor Verification (DE-20) | 1.59 s | 1.64 s | PASS | 14 checks executed; matches workstation standard |
| **TOTAL** | Nightly Execution | **214.74 s** | **209.88 s** | **PASS** | **Budget limit: 10,800 s (3 h)** |

---

## 4. Remedy Matrix Evaluation (BG-01 … BG-05)

Roadmap §0.8.4 defines named remedies for pipeline scaling as the application estate expands:

| Remedy | Mechanism | Implementation in Harness | Current Status |
|---|---|---|---|
| **BG-01** | **Affected-Component Selection** | `tooling/scripts/affected-selection.py` computes transitive diff graph | Integrated into `ci.yml` Stage 4. When diffs are isolated, only affected modules execute. |
| **BG-02** | **Fitness-First Gating** | Fast static schema & model registry checks execute before long tests | Integrated as Stage 3 (`fitness/run.py`). Bails out within 22s if architecture rules break. |
| **BG-03** | **Static Bundle Budget Enforcement** | `check-bundle.mjs` reads Next.js build manifests without server launch | Integrated as Stage 11. Executes in $\sim 0.11\text{ s}$ using gzip calculation. |
| **BG-04** | **Parallelized Accessibility Auditing** | `tooling/e2e/a11y-audit.mjs` uses headless browser page reuse | Integrated as Stage 12. Completes across 7 portals in $7.15\text{ s}$. |
| **BG-05** | **Scheduled Clean-Runner Isolation** | Clean-room environment reconstruction offloaded to Nightly profile | DE-20 doctor check runs in Nightly, maintaining Pre-Merge at $< 1\text{ min}$. |

---

## 5. Defects Exposed and Resolved During First CI Execution

In adherence to R01-M03-T03:
1. **Unbound Variable in `fix_contact_centre.py` (line 61)**:
   - *Defect:* `for conversation in conversation:` caused `UnboundLocalError` on agent handoff.
   - *Resolution:* Fixed to `for conversation in self:`.
2. **Invalid `# noqa` Directive in `notification-dispatcher/src/main.py` (line 83)**:
   - *Defect:* Slash separator `# noqa: A003/N802` rejected by ruff parser.
   - *Resolution:* Standardized to comma-delimited `# noqa: A003, N802`.
3. **Duplicate Translation Keys in `generate-p06-po.py` and `generate-p07-po.py`**:
   - *Defect:* Repeated keys (`Contract`, `Terms`, `Pack OK`, `Customer`) in static maps.
   - *Resolution:* Cleaned duplicate entries via automated AST pass.
4. **Git Bash Path Resolution on Windows**:
   - *Defect:* Direct `bash` invocation delegated to unconfigured WSL on Windows hosts.
   - *Resolution:* Updated `doctor.ps1` to resolve `C:\Program Files\Git\bin\bash.exe`.

---

## 6. Milestone Conclusion & Audit Sign-Off

Milestone **R01-M03** is **COMPREHENSIVELY COMPLETE**:
- **R01-M03-T01:** Pushed `develop` to remote `origin` (`https://github.com/maz279/1000fix_new_erp_system.git`) with branch protection rules recorded and enforced.
- **R01-M03-T02:** CI secrets and variables provisioned without plaintext exposure.
- **R01-M03-T03:** Pre-merge profile executed green (32.30s runtime); defects resolved; evidence recorded.
- **R01-M03-T04:** Two consecutive green nightly runs executed (214.74s and 209.88s); DE-20 clean doctor verified.
- **R01-M03-T05:** Pipeline budget report published with all §0.8.4 criteria met.
