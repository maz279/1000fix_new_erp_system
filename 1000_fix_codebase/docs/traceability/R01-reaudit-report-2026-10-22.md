# R01 Re-Audit Report — Foundation & Governance Closure (second pass)

**Report date:** 22 October 2026
**Scope:** Roadmap `phase_1/R01_Foundation_and_Governance_Closure.md` (M01–M05), audited
against the working tree of `1000_fix_codebase` and the workspace git root it lives in.
**Relationship to earlier records:** supersedes the verdicts in `R01-exit-report.md` §1–§3
and extends `R01-correction-report.md` (2026-10-21). Neither earlier document is deleted;
both now carry a pointer here.
**Method:** every task's "Verify" column was re-executed, not re-read. Registry digests were
checked against the registries, the workflow was validated structurally, pre-commit was run on
a disposable copy of the tree, gate verifiers were read line by line and re-run, coverage was
re-derived from the raw JSON, and the running application was inspected in a browser.

---

## 0. Verdict

The 2026-10-21 correction pass fixed the *fabricated numbers* but left a second class of defect
untouched: **apparatus that cannot execute where the roadmap says it runs**, and **verifiers that
still grade outcomes PASS because a file exists**. The most consequential findings:

1. **No CI run was ever possible on GitHub.** The git root is the workspace; GitHub reads
   workflows only from `<root>/.github/workflows/`. `ci.yml`, `settings.yml` and `CODEOWNERS` sat
   inside `1000_fix_codebase/` and were silently ignored. 12 of 17 jobs also could not start
   (no checkout, `uv run` with no uv, an invalid gitleaks flag, a non-existent `artifacts upload`
   command), and the lock file did not contain ruff/mypy/pre-commit/pip-audit.
2. **The pre-commit layer (XS-19 "not optional") never ran at commit time.** `core.hooksPath`
   points at `.githooks/`, which had no `pre-commit` hook; and when run manually it rewrote
   212 vendor files (FF-03 then FAILED) and 119 business documents outside the codebase.
3. **The lint gate was quietly disabled in R01-M03** (commit `cd107153d5`): the ruff rule set
   was cut from `E,W,F,I,B,UP,S,C4,SIM,RUF` to `E,W,F` with F401/F841/E722 ignored, removing all
   security (S) and bug (B) checking. Even the weakened config failed (one E731).
4. **4 of 30 pinned image digests did not exist** in their registries (superset, python slim,
   a non-existent Novu repository, a misspelled MeshCentral repository).
5. **Gate verifiers still rubber-stamped.** G0a reported GREEN with an open E1 blocker and no
   GV-003 override; G2 graded "app in daily use by all Dhaka technicians" PASS on a narrative
   written before any deployment; G2-04 passed on an inventory sign-off whose rows do not sum to
   its totals; G9 graded Month-36 programme closure PASS today.

All of these are corrected below. After correction the **honest R01 position is RED on gates
G0a/G0b** (one open E1 blocker without a recorded Steering override) — that is the measurement
working, not a regression.

---

## 1. Defect register (found → fixed)

### 1.1 CI / repository structure (R01-M03)

| # | Defect | Evidence | Correction |
|---|---|---|---|
| RA-01 | Workflow, Probot settings and CODEOWNERS outside the git root — ignored by GitHub | `git ls-tree HEAD` at root: no `.github/`; remote `develop`/`main` @ `dfbf836d8` likewise | Moved to `<workspace>/.github/`; workflow runs with `defaults.run.working-directory: 1000_fix_codebase`; codebase `.github/README.md` points to the new location |
| RA-02 | 12 of 17 jobs could not start (no checkout; `uv run` without setup-uv; `gitleaks --redexit`; `artifacts upload`; pnpm workspace that does not exist; `docker build .` with no Dockerfile) | static analysis of the HEAD workflow | Every job checks out and sets up its toolchain; gitleaks via `gitleaks-action`; SBOM via `anchore/sbom-action`; container scan over the real service Dockerfiles; TS gate is `tsc --noEmit` per portal; release/gate jobs whose prerequisites do not exist yet **fail closed with an explicit message** |
| RA-03 | `uv.lock` held only pytest/coverage — `uv run ruff/mypy/pre-commit/pip-audit` impossible; service tests import fastapi/pydantic/yaml | `uv.lock` | `[dependency-groups] dev` added (ruff pinned 0.8.4 = pre-commit rev); lock regenerated (62 packages) |
| RA-04 | No structural check existed, so RA-01/02 went unnoticed for two audits | — | `tooling/ci/validate-workflow.py` (W1–W8); wired into G0b-2. Original workflow: 12 failures; new: PASS |
| RA-05 | CODEOWNERS generator emitted quoted (`"cd_x"`) and placeholder (`"—"`) paths — none of 313 rules could match | old `CODEOWNERS` | Generator fixed (strip quotes, skip placeholders, codebase prefix, write to `<root>/.github/CODEOWNERS`); 307 valid rules |
| RA-06 | Coverage stage in CI ran affected-selection output that pytest cannot resolve (bare module names → exit 4) and measured "statutory" over the whole estate (43%) | reproduced | Unit job calls the same harness as local (`measure-coverage.py --fail-under 80 --fail-under-financial 100`); affected-selection emits paths |

### 1.2 Engineering hygiene (R01-M02)

| # | Defect | Evidence | Correction |
|---|---|---|---|
| RA-07 | FF-03 FAIL — 212 vendor files rewritten by auto-fixing hooks | `check-vendor-clean.sh` exit 1 | Global `exclude:` for vendor/node_modules/odoo-data/htmlcov and `files: ^1000_fix_codebase/` in pre-commit; vendor restored from git (formatter-only diffs verified with `git diff -w`) — FF-03 OK |
| RA-08 | No `pre-commit` git hook under `core.hooksPath` | `.githooks/` listing | `.githooks/pre-commit` shim runs the codebase config; fails loudly if pre-commit is absent |
| RA-09 | `mixed-line-ending --fix=lf` vs `.gitattributes *.ps1 eol=crlf` — perpetual churn | config vs attributes | `.ps1/.psm1/.bat/.cmd` excluded from that hook |
| RA-10 | eslint/prettier/dart hooks reference toolchains that do not exist (no ESLint/Prettier config or dependency anywhere, no pnpm workspace, no fvm) — `pre-commit run -a` hung | repo scan | Parked on `stages: [manual]` with the reason in the config; CI uses per-portal `tsc` |
| RA-11 | Lint rule families removed in R01-M03 to make the stage green | `git diff cd107153d5~1 cd107153d5 -- pyproject.toml` | Restored; only narrow, documented per-file ignores (tests' asserts, `__init__` re-exports, `__manifest__` dict literals, Bengali text vs RUF001-003, two Odoo idioms) |
| RA-12 | 135 Python files not formatted with the pinned formatter | `ruff@0.8.4 format --check` | Formatted (semantics-preserving; full suite re-run) |
| RA-13 | 4 registry-rejected digests; 3 unpinned Dockerfile bases | `verify-compose-digests.py` | Real digests resolved from the registries; Novu → `ghcr.io/novuhq/novu/api:2.3.0`, MeshCentral → `ghcr.io/ylianst/meshcentral:1.1.60`; Dockerfiles pinned; `versions.lock` updated; tool kept as `tooling/scripts/verify-compose-digests.py` (72 refs, 0 failed, 9 PENDING-FIRST-BUILD) |
| RA-14 | Real security findings hidden by the weakened lint: `eval` of a manifest (test), `exec` of a script, md5 without `usedforsecurity=False`, exceptions re-raised without cause in GL/tax/payroll | ruff S/B | `ast.literal_eval`, `runpy.run_path`, `usedforsecurity=False`, `raise … from e` |
| RA-15 | `dbt_runner.py` recorded **100 rows / SUCCESS** when the row-count query failed | `services/bi-warehouse/src/dbt_runner.py` | Reports `UNVERIFIED` with the error and `rows_affected: null` |
| RA-16 | Source-text test broke when the formatter re-wrapped a call | `tests/test_m16_m42_break.py` | Asserts on the AST |
| RA-17 | `audit-repo-formats` reported any uncommitted edit as a non-deterministic generator; a BOM made one evidence JSON invalid | tool logic | Before/after snapshot of the generated directories; BOM stripped |

### 1.3 Measurement harness (R01-M04)

| # | Defect | Correction |
|---|---|---|
| RA-18 | Harness ignored pytest exit codes and silently re-read stale JSON on failure | Outputs cleaned before each run; exit codes recorded; invalid run → exit 2, UNMEASURED |
| RA-19 | Statutory set omitted the payroll calculation kernel (`libs/py/payroll_engine`), payout rail, e-VAT adapter, `cd_settlement_ext`, `cd_ap_ext`; one listed path never produced data | Single `STATUTORY_SET` with a reason per entry; every path verified to produce data |
| RA-20 | "Pure-logic min" over a hand-picked list excluding the worst file | Derived from code (statutory, no Odoo import); min is now `bank_feed_parser.py` |
| RA-21 | Module classification bug (`libs/py/trust_services` counted as a microservice); conftest and manifests counted as product code | Path-prefix classification; `*/conftest.py`, `*/__manifest__.py` omitted |
| RA-22 | Register: gap computed to 100 % not 80 %; duplicate story ID; unweighted means; stories citing non-existent modules; hard-coded "16 stories" / "G0b-10 satisfied" | Generator rewritten; targets from the statutory set; weighted; unique IDs |
| RA-23 | Gates never enforced (thresholds never passed) | `run-pipeline.py` and CI pass `--fail-under 80 --fail-under-financial 100`; verdict recorded honestly as FAIL |

### 1.4 Gate verifiers (R01-M05)

| # | Defect | Correction |
|---|---|---|
| RA-24 | G0a: CONDITION never affected the verdict; E1 blocker B-05b open with no GV-003 override yet GREEN | E1 CONDITION without an override row counts as OPEN; verdict `RED-OPEN-BLOCKERS` |
| RA-25 | G0a/G0b read two different CD registers (331 vs 332 items) | Canonical `tooling/cd-register.yaml`; delta vs IR-002 reported as CONDITION (CR needed) |
| RA-26 | G0a B-04/B-05 hard-coded evidence text; fit-gap register 3,347 rows vs 3,389 denominator graded PASS | Parsed; CONDITION with measured counts |
| RA-27 | G0b: OPEN not counted; bare-array JSON with no verdict; G0b-1/2/4/5 file-existence checks; G0b-9 blind to PENDING-FIRST-BUILD; G0b-11 read a pinned old G0a file | Object JSON with verdict; doctor check ids counted; workflow validator run; vendor check executed; PENDING markers → CONDITION; reads `gate-g0a-latest.json` |
| RA-28 | G2-01..06 PASS on repo-authored narratives; G2-04 sign-off internally inconsistent; G2-07/08/09 PASS on unrelated or existence-only artefacts; OPEN uncounted; onboarding-SLA file used as a proxy for Steering sign-off | Field outcomes CONDITION until telemetry exists; G2-04 FAIL on the arithmetic; proxies removed; provenance banners added to the six narratives |
| RA-29 | G9 graded Month-36 closure PASS today on document existence; wrong artefacts for G9-03/10 | All outcome criteria CONDITION/OPEN with measured facts (e.g. 8 of 12 web portals exist) |

---

## 2. Re-execution record (22 October 2026)

_Filled from the final measurement run — see §2 table below._

<!-- MEASUREMENTS -->

---

## 3. Visual inspection (live runtime)

Odoo 19 on `127.0.0.1:8069` against `fix_dev` (Postgres 17.4 in the project's compose
container), 142 modules loaded:

- **Login page** — renders correctly (brand panel, sign-in, passkey, hotline); no console errors
  except a service-worker registration refusal specific to the embedded browser
  (`/web/service-worker.js` returns 200 over HTTP).
- **Role Centre** — live KPIs, 67-module rail, approvals list render. **Defect found:** the
  "Revenue MTD (est.)" tile shows **৳ −200.30**. Root cause: estimate #4 has no lines and a
  discount of 200; `_compute_totals` produces a negative subtotal, applies VAT to it, and
  `action_approve` accepts the empty estimate. See §4.
- **Dispatch console & live map** — renders (50 branches / 20 technicians / 30 pending orders).
- **Coverage dashboard** (`htmlcov/index.html`) — renders the measured estate figure.
- **Smoke test on the live runtime** — `test-smoke.py` 15/15 (service-order lifecycle, outbox,
  ACL denial, idempotent seed).

---

## 4. Defects found outside R01 scope (recorded, proposed as follow-ups)

| # | Area | Defect |
|---|---|---|
| OS-1 | M01 estimates (`cd_service_order/models/fix_estimate.py`) | Negative estimate totals possible (discount > lines, VAT on a negative base), empty estimates approvable; `action_send` sets `sent` then tests for `approved` (dead branch) |
| OS-2 | M56 payroll (`cd_payroll_bd/models/fix_payroll.py`) | Salary bank file falls back to a hard-coded routing number and account number when an employee has none — money could be routed to a fabricated account |
| OS-3 | M02 offline sync (`cd_field_service/controllers/offline_sync_api.py`) | `batch_checksum` and `sync_token` are read from the request and never verified |
| OS-4 | Wave-1 migration rehearsal (`migrations/tests`) | Control totals no longer reconcile against `fix_dev` (branches 6 vs 53 after later seeding; attendance_opening not loaded) — the rehearsal needs its own database |
| OS-5 | Workstation verifier T10 | `WORKSTATION_RESERVED_PORTS` includes the project's own published ports, so T10 warns whenever this project's stack is up |

---

## 5. Items that remain open (cannot be closed from a code repository)

| Item | Owner | Why it is open |
|---|---|---|
| B-05b (E1) Steering approval of the CR — or a GV-003 override row | Steering | No approval or override exists; G0a/G0b stay RED until one is recorded |
| B-03/B-04/B-05/B-05c/B-10 conditions | Programme / Steering | Need a CR (CD count 332 vs 331), the 42 missing fit-gap rows, AR-006 acceptance, per-repo verification |
| First GitHub Actions run (R01-M03-T03/T04) | Repository owner | Requires pushing the relocated workflow and repository secrets; `gh` is not authenticated on this workstation and pushing is an owner action. `validate-workflow.py` passes |
| BitLocker (R01-M02-T04) | Workstation operator | Elevated `manage-bde -on C:` then `verify-workstation.ps1` (current: 8 PASS / 2 WARN / 0 FAIL) |
| Onboarding SLA "every joiner" (G0b-10) | Team lead | One joiner measured |
| Governance artefacts (DEP-31, Board minutes, SoW amendment, D-002 roster) | Steering | Left unmodified per the 2026-10-21 decision recorded in `R01-correction-report.md` §6. Note: they are repository-authored documents; a code repository cannot by itself evidence a Board meeting or a legal opinion |
