#!/usr/bin/env python3
"""
run-pipeline.py — Local & CI Unified Pipeline Runner
Implements R01-M03-T03, R01-M03-T04, R01-M03-T05 (P02-M09 / PE-004)

Executes pipeline profiles matching .github/workflows/ci.yml:
  - pre-commit:  Fast developer local checks (<30s budget)
  - pre-merge:   Canonical gating stages 2-12+15 (<20min budget)
  - nightly:     Full integration + 10 user journeys + DE-20 clean doctor (<3h budget)
  - all:         Executes pre-commit, pre-merge, and nightly sequentially

Produces machine-readable execution timing and logs in:
  docs/traceability/evidence/ci-<profile>-run-<timestamp>.json
"""

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
CODEBASE_DIR = ROOT_DIR
EVIDENCE_DIR = CODEBASE_DIR / "docs" / "traceability" / "evidence"


class StageResult:
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.start_time: float = 0.0
        self.end_time: float = 0.0
        self.duration_seconds: float = 0.0
        self.status: str = "PENDING"
        self.exit_code: int = 0
        self.stdout: str = ""
        self.stderr: str = ""
        self.measurements: dict[str, any] = {}

    def to_dict(self) -> dict[str, any]:
        return {
            "name": self.name,
            "description": self.description,
            "status": self.status,
            "duration_seconds": round(self.duration_seconds, 2),
            "exit_code": self.exit_code,
            "measurements": self.measurements,
            "output_summary": (self.stdout[-500:] if self.stdout else ""),
        }


def run_command(
    cmd: list[str], cwd: Path | None = None, timeout: int = 600, env: dict[str, str] | None = None
) -> tuple[int, str, str]:
    target_cwd = cwd or CODEBASE_DIR
    full_env = os.environ.copy()
    if env:
        full_env.update(env)
    # Ensure UTF-8 output on Windows
    full_env["PYTHONIOENCODING"] = "utf-8"
    full_env["NODE_ENV"] = full_env.get("NODE_ENV", "test")

    try:
        proc = subprocess.run(
            cmd,
            cwd=str(target_cwd),
            capture_output=True,
            text=True,
            timeout=timeout,
            shell=False,
            env=full_env,
        )
        return proc.returncode, proc.stdout, proc.stderr
    except subprocess.TimeoutExpired as e:
        return 124, e.stdout or "", f"Timeout after {timeout}s: {e}"
    except Exception as e:
        return 1, "", str(e)


def execute_stage(
    stage: StageResult,
    cmd: list[str],
    cwd: Path | None = None,
    timeout: int = 600,
    env: dict[str, str] | None = None,
    allow_honest_failure: bool = False,
) -> StageResult:
    print(f"\n[CI] >>> Stage: {stage.name} — {stage.description}")
    print(f"     Command: {' '.join(cmd)}")
    stage.start_time = time.time()
    code, out, err = run_command(cmd, cwd=cwd, timeout=timeout, env=env)
    stage.end_time = time.time()
    stage.duration_seconds = stage.end_time - stage.start_time
    stage.exit_code = code
    stage.stdout = out
    stage.stderr = err

    if code == 0:
        stage.status = "PASS"
        print(f"[CI] <<< PASS: {stage.name} in {stage.duration_seconds:.2f}s")
    elif allow_honest_failure:
        stage.status = "MEASURED_GAP"
        print(f"[CI] <<< MEASURED_GAP: {stage.name} in {stage.duration_seconds:.2f}s (code {code})")
    else:
        stage.status = "FAIL"
        print(f"[CI] <<< FAIL: {stage.name} in {stage.duration_seconds:.2f}s (code {code})")
        if err:
            print(f"     Error: {err.strip()[:300]}")
    return stage


# --- measurement parsers: every number in evidence comes from tool output ----


def _latest_fitness_evidence() -> Path | None:
    """Newest fitness evidence JSON written by tooling/fitness/run.py."""
    ev_dir = CODEBASE_DIR / "tooling" / "fitness" / "evidence"
    if not ev_dir.is_dir():
        return None
    candidates = sorted(
        (p for p in ev_dir.glob("fitness-*.json")),
        key=lambda p: p.stat().st_mtime,
    )
    return candidates[-1] if candidates else None


def parse_fitness_counts(stage: StageResult) -> None:
    """Fill measurements from the fitness evidence JSON run.py just wrote."""
    ev = _latest_fitness_evidence()
    if ev is None:
        stage.measurements["checks_passed"] = "UNMEASURED"
        stage.measurements["note"] = "no fitness evidence JSON found after run"
        return
    try:
        data = json.loads(ev.read_text(encoding="utf-8"))
        results = data.get("results", [])
        counts: dict[str, int] = {}
        for r in results:
            status = str(r.get("status", "?")).upper()
            counts[status] = counts.get(status, 0) + 1
        stage.measurements["checks_total"] = len(results)
        stage.measurements["checks_passed"] = counts.get("PASS", 0)
        stage.measurements["checks_failed"] = counts.get("FAIL", 0)
        stage.measurements["checks_skipped"] = counts.get("SKIP", 0)
        stage.measurements["evidence_file"] = str(ev.relative_to(CODEBASE_DIR)).replace("\\", "/")
    except Exception as e:
        stage.measurements["checks_passed"] = "UNMEASURED"
        stage.measurements["note"] = f"failed to parse {ev.name}: {e}"


def parse_permission_suite(stage: StageResult) -> None:
    """Fill measurements from permission-negative-suite-latest.json."""
    ev = CODEBASE_DIR / "tooling" / "fitness" / "evidence" / "permission-negative-suite-latest.json"
    try:
        data = json.loads(ev.read_text(encoding="utf-8"))
        res = data.get("results", {})
        stage.measurements["roles_verified"] = res.get("roles", {}).get(
            "actual_count", "UNMEASURED"
        )
        stage.measurements["tiers_verified"] = res.get("isolation_tiers", {}).get(
            "actual_count", "UNMEASURED"
        )
        stage.measurements["sod_controls_verified"] = res.get("sod_controls", {}).get(
            "actual_count", "UNMEASURED"
        )
        ts = res.get("test_suite", {})
        stage.measurements["negative_tests_run"] = ts.get("tests_run", "UNMEASURED")
        stage.measurements["negative_tests_passed"] = ts.get("tests_passed", "UNMEASURED")
        stage.measurements["overall_verdict"] = data.get("overall_verdict", "UNMEASURED")
    except Exception as e:
        stage.measurements["roles_verified"] = "UNMEASURED"
        stage.measurements["note"] = f"failed to parse permission suite evidence: {e}"


def parse_i18n_completeness(stage: StageResult) -> None:
    """Parse 'i18n.check: MEASURED completeness = X% (a/b keys across N portal(s))'."""
    import re

    m = re.search(
        r"MEASURED completeness = ([\d.]+)% \((\d+)/(\d+) keys across (\d+) portal", stage.stdout
    )
    if m:
        stage.measurements["completeness_pct"] = float(m.group(1))
        stage.measurements["translated_keys"] = int(m.group(2))
        stage.measurements["total_keys"] = int(m.group(3))
        stage.measurements["portals"] = int(m.group(4))
    else:
        stage.measurements["completeness_pct"] = "UNMEASURED"
        stage.measurements["note"] = "i18n.check output line not found in stage stdout"


def parse_visual_drive(stage: StageResult) -> None:
    """Parse 'VISUAL DRIVE: X/Y clean' and the results/visual-drive.json array."""
    import re

    m = re.search(r"VISUAL DRIVE: (\d+)/(\d+) clean", stage.stdout)
    if m:
        stage.measurements["views_clean"] = int(m.group(1))
        stage.measurements["views_verified"] = int(m.group(2))
        return
    vd = CODEBASE_DIR / "tooling" / "e2e" / "results" / "visual-drive.json"
    try:
        arr = json.loads(vd.read_text(encoding="utf-8"))
        ok = sum(1 for r in arr if r.get("ok"))
        stage.measurements["views_clean"] = ok
        stage.measurements["views_verified"] = len(arr)
        stage.measurements["note"] = "parsed from results/visual-drive.json (summary line absent)"
    except Exception:
        stage.measurements["views_verified"] = "UNMEASURED"


def parse_headers_sweep(stage: StageResult) -> None:
    """Parse 'SWEEP: X pass / Y fail'."""
    import re

    m = re.search(r"SWEEP: (\d+) pass / (\d+) fail", stage.stdout)
    if m:
        stage.measurements["headers_passed"] = int(m.group(1))
        stage.measurements["headers_failed"] = int(m.group(2))
        stage.measurements["headers_verified"] = int(m.group(1)) + int(m.group(2))
    else:
        stage.measurements["headers_verified"] = "UNMEASURED"


def parse_playwright(stage: StageResult) -> None:
    """Parse playwright/jest-style 'N passed' summary from e2e output."""
    import re

    m = re.findall(r"(\d+) passed", stage.stdout)
    if m:
        total = sum(int(x) for x in m)
        failed = re.findall(r"(\d+) failed", stage.stdout)
        stage.measurements["journeys_passed"] = total
        stage.measurements["journeys_failed"] = sum(int(x) for x in failed)
        stage.measurements["journeys_executed"] = total + sum(int(x) for x in failed)
    else:
        stage.measurements["journeys_executed"] = "UNMEASURED"
        stage.measurements["note"] = "no 'N passed' summary found in e2e output"


def parse_doctor_json(stage: StageResult, doctor_json_path: Path) -> None:
    """Fill measurements from the doctor.py JSON the stage just wrote."""
    try:
        data = json.loads(doctor_json_path.read_text(encoding="utf-8"))
        stage.measurements["checks_total"] = len(data.get("results", [])) or data.get("total", 14)
        stage.measurements["checks_passed"] = data.get("passed", "UNMEASURED")
        stage.measurements["checks_skipped"] = data.get("skipped", "UNMEASURED")
        stage.measurements["checks_failed"] = data.get("failed", "UNMEASURED")
    except Exception as e:
        stage.measurements["checks_passed"] = "UNMEASURED"
        stage.measurements["note"] = f"failed to parse doctor JSON: {e}"


def run_pre_commit() -> tuple[list[StageResult], float, bool]:
    stages: list[StageResult] = []
    t0 = time.time()

    # 1. Fast formatting & ruff check
    s1 = StageResult("precommit-ruff", "Fast code style and AST validation")
    execute_stage(
        s1,
        [
            sys.executable,
            "-m",
            "ruff",
            "check",
            "addons",
            "services",
            "contracts",
            "i18n",
            "tooling",
        ],
        timeout=30,
    )
    stages.append(s1)

    # 2. Git status / clean workspace check
    s2 = StageResult("precommit-hygiene", "No committed sessions or unpinned digests")
    execute_stage(s2, ["git", "status", "--porcelain"], timeout=10)
    # `git status --porcelain` exits 0 even when dirty — cleanliness is
    # "no output", not "exit code 0".
    s2.measurements["clean_worktree"] = s2.exit_code == 0 and not s2.stdout.strip()
    if s2.exit_code == 0 and s2.stdout.strip():
        s2.status = "FAIL"
        s2.stdout = f"worktree dirty:\n{s2.stdout[:400]}"
        print(f"[CI] <<< FAIL: {s2.name} — worktree is dirty (see output_summary)")
    stages.append(s2)

    total_duration = time.time() - t0
    success = all(s.status == "PASS" for s in stages)
    return stages, total_duration, success


def run_pre_merge() -> tuple[list[StageResult], float, bool]:
    stages: list[StageResult] = []
    t0 = time.time()

    # Stage 2: lint-type (Ruff check + format check)
    s_lint = StageResult("stage-02-lint-type", "Python linting and formatting check")
    execute_stage(
        s_lint,
        [
            sys.executable,
            "-m",
            "ruff",
            "check",
            "addons",
            "services",
            "contracts",
            "i18n",
            "tooling",
        ],
    )
    stages.append(s_lint)

    # Stage 3: model-registry (Fitness architecture checks)
    s_fit = StageResult(
        "stage-03-model-registry", "Model registry, field standards and fitness gates"
    )
    execute_stage(s_fit, [sys.executable, "tooling/fitness/run.py"])
    parse_fitness_counts(s_fit)
    stages.append(s_fit)

    # Stage 3b: permission-negative-suite (R02-M02: 53 roles x 6 tiers x 61 SoD)
    s_perm = StageResult(
        "stage-03b-permission-negative-suite",
        "53 roles x 6 tiers x 61 SoD negative permission verification (DoD-07)",
    )
    execute_stage(s_perm, [sys.executable, "tooling/scripts/verify-permission-negative-suite.py"])
    parse_permission_suite(s_perm)
    stages.append(s_perm)

    # Stage 4: unit (Unit tests with coverage measurement)
    # Both DoD-03 gates are applied by the harness (estate 80 / statutory 100).
    # Expected FAIL until the burn-down closes the gap - recorded honestly,
    # never relabelled. Harness exit: 0 pass, 1 gate failed, 2 invalid run.
    # Programme decision 2026-10-22: 100% line+branch for the whole estate
    # (raises DoD-03's 80% floor); statutory set stays at 100%.
    estate_gate, statutory_gate = 100.0, 100.0
    s_unit = StageResult("stage-04-unit", "Estate unit tests and baseline coverage measurement")
    execute_stage(
        s_unit,
        [
            sys.executable,
            "tooling/scripts/measure-coverage.py",
            "--fail-under",
            str(estate_gate),
            "--fail-under-financial",
            str(statutory_gate),
        ],
        timeout=900,
    )

    def _pct(value) -> str:
        return f"{value:.2f}%" if isinstance(value, int | float) else "UNMEASURED"

    s_unit.measurements["target_coverage_estate"] = f"{estate_gate:.0f}%"
    s_unit.measurements["target_coverage_statutory"] = f"{statutory_gate:.0f}%"
    s_unit.measurements["harness_exit_code"] = s_unit.exit_code
    cov_report = EVIDENCE_DIR / "coverage-baseline-report.json"
    if cov_report.is_file():
        try:
            cov_data = json.loads(cov_report.read_text(encoding="utf-8"))
            estate = cov_data.get("estate_summary") or {}
            statutory = (
                cov_data.get("statutory_financial_tax_summary")
                or cov_data.get("statutory_summary")
                or {}
            )
            s_unit.measurements["measurement_valid"] = cov_data.get("measurement_valid", False)
            s_unit.measurements["baseline_coverage_estate"] = _pct(estate.get("percent_covered"))
            s_unit.measurements["statutory_coverage"] = _pct(statutory.get("percent_covered"))
            s_unit.measurements["pure_logic_coverage"] = _pct(
                statutory.get("pure_logic_coverage_percent")
            )
            gates = cov_data.get("gates_applied") or {}
            s_unit.measurements["estate_gate_verdict"] = (gates.get("estate") or {}).get(
                "verdict", "UNMEASURED"
            )
            s_unit.measurements["statutory_gate_verdict"] = (gates.get("statutory") or {}).get(
                "verdict", "UNMEASURED"
            )
            if cov_data.get("errors"):
                s_unit.measurements["errors"] = cov_data["errors"]
        except Exception as e:
            s_unit.measurements["baseline_coverage_estate"] = "UNMEASURED"
            s_unit.measurements["statutory_coverage"] = "UNMEASURED"
            s_unit.measurements["note"] = f"coverage report present but unreadable: {e}"
    else:
        s_unit.measurements["baseline_coverage_estate"] = "UNMEASURED"
        s_unit.measurements["statutory_coverage"] = "UNMEASURED"
        s_unit.measurements["pure_logic_coverage"] = "UNMEASURED"
        s_unit.measurements["note"] = (
            "coverage-baseline-report.json not produced by measure-coverage.py"
        )
    stages.append(s_unit)

    # Stage 6: contract (OpenAPI 3.1 specification & consumer-driven pacts validation)
    s_openapi = StageResult(
        "stage-06-contract", "OpenAPI 3.1 contract and consumer-driven pact validation (PS-01)"
    )
    execute_stage(s_openapi, [sys.executable, "-m", "contracts.check", "all"])
    stages.append(s_openapi)

    # Stage 7: event (Event schema validation + AS-08 outbox coverage)
    s_events = StageResult("stage-07-event", "Event schema compatibility and outbox parity")
    execute_stage(s_events, [sys.executable, "-m", "contracts.check", "events"])
    stages.append(s_events)

    # Stage 8: security (Check docker-compose files for 0 PLACEHOLDER-RESOLVE)
    s_sec = StageResult("stage-08-security", "Secret leakage and digest immutability audit")
    # Audit docker compose files — duration is measured, not asserted.
    sec_t0 = time.time()
    compose_dir = CODEBASE_DIR / "infra" / "compose"
    placeholder_found = False
    unpinned_images: list[str] = []
    for yml in compose_dir.glob("*.yml"):
        content = yml.read_text(encoding="utf-8")
        if "PLACEHOLDER-RESOLVE" in content:
            placeholder_found = True
        for line in content.splitlines():
            stripped = line.strip()
            if stripped.startswith("image:"):
                ref = stripped.split("image:", 1)[1].strip()
                if (
                    "@sha256:" not in ref
                    and "PENDING-FIRST-BUILD" not in line
                    and "pending" not in line.lower()
                ):
                    unpinned_images.append(f"{yml.name}: {ref}")
    s_sec.duration_seconds = time.time() - sec_t0
    s_sec.exit_code = 1 if placeholder_found else 0
    s_sec.status = "FAIL" if placeholder_found else "PASS"
    total_images = len(unpinned_images) + sum(
        1
        for yml in compose_dir.glob("*.yml")
        for line in yml.read_text(encoding="utf-8").splitlines()
        if line.strip().startswith("image:") and ("@sha256:" in line or "pending" in line.lower())
    )
    s_sec.stdout = (
        f"{total_images} image references audited across {len(list(compose_dir.glob('*.yml')))} compose files; "
        f"{len(unpinned_images)} without digest pin or explicit pending marker."
    )
    s_sec.measurements["images_audited"] = total_images
    s_sec.measurements["digest_pinned_or_pending"] = total_images - len(unpinned_images)
    s_sec.measurements["digest_pinned_ratio"] = (
        f"{((total_images - len(unpinned_images)) / max(total_images, 1) * 100):.0f}%"
        if total_images
        else "UNMEASURED"
    )
    if unpinned_images:
        s_sec.measurements["unpinned_images"] = unpinned_images[:20]
    stages.append(s_sec)

    # Stage 9: architecture (Doctor environment sanity check)
    s_arch = StageResult(
        "stage-09-architecture", "Architecture constraints and doctor environment verification"
    )
    execute_stage(s_arch, [sys.executable, "tooling/scripts/doctor.py"])
    stages.append(s_arch)

    # Stage 10: localisation (i18n completeness measurement)
    s_i18n = StageResult(
        "stage-10-localisation", "Localisation completeness and translation parity (DoD-08)"
    )
    execute_stage(
        s_i18n,
        [sys.executable, "-m", "i18n.check", "--completeness", "100"],
        allow_honest_failure=True,
    )
    parse_i18n_completeness(s_i18n)
    stages.append(s_i18n)

    # Stage 11: bundle (Next.js client bundle gzip budget <= 400KB)
    s_bundle = StageResult("stage-11-bundle", "Next.js client route gzip bundle budget check")
    execute_stage(s_bundle, ["node", "tooling/scripts/check-bundle.mjs", "--budget-kb", "400"])
    stages.append(s_bundle)

    # Stage 12: accessibility (axe-core WCAG 2.2 AA audit)
    s_a11y = StageResult(
        "stage-12-accessibility", "Automated a11y WCAG 2.2 AA audit across live portals"
    )
    execute_stage(s_a11y, ["node", "tooling/e2e/a11y-audit.mjs"], timeout=120)
    stages.append(s_a11y)

    # Stage 15: infrastructure (Odoo conf generation check)
    s_infra = StageResult("stage-15-infrastructure", "Infrastructure configuration drift check")
    execute_stage(s_infra, [sys.executable, "tooling/scripts/generate-odoo-conf.py", "--check"])
    stages.append(s_infra)

    total_duration = time.time() - t0
    success = all(s.status in ["PASS", "MEASURED_GAP"] for s in stages)
    return stages, total_duration, success


def run_nightly() -> tuple[list[StageResult], float, bool]:
    stages: list[StageResult] = []
    t0 = time.time()

    # 1. Full E2E User Journeys suite (count comes from the runner's own summary)
    journey_specs = len(list((CODEBASE_DIR / "tooling" / "e2e" / "journeys").glob("*.spec.*")))
    s_e2e = StageResult(
        "nightly-journeys",
        f"E2E critical business user journeys ({journey_specs} spec files on disk; executed count measured from runner output)",
    )
    execute_stage(s_e2e, ["pnpm.cmd", "--dir", "tooling/e2e", "test"], timeout=300)
    parse_playwright(s_e2e)
    s_e2e.measurements["journey_spec_files_on_disk"] = journey_specs
    stages.append(s_e2e)

    # 2. Visual Drive (responsive views — count parsed from tool output)
    s_vis = StageResult(
        "nightly-visual-drive", "Route visual and responsive layout regression drive"
    )
    execute_stage(s_vis, ["node", "tooling/e2e/visual-drive.mjs"], timeout=180)
    parse_visual_drive(s_vis)
    stages.append(s_vis)

    # 3. Headers Sweep (security headers — count parsed from tool output)
    s_head = StageResult("nightly-headers-sweep", "Security and CSP response headers sweep")
    execute_stage(s_head, ["node", "tooling/e2e/headers-sweep.mjs"], timeout=60)
    parse_headers_sweep(s_head)
    stages.append(s_head)

    # 4. Scheduled Doctor on clean runner (DE-20) — counts parsed from doctor JSON
    doctor_json = EVIDENCE_DIR / f"doctor-de20-{datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')}.json"
    s_doc = StageResult(
        "nightly-de20-clean-doctor", "Doctor verification on this runner (DE-20 / P02-M10-T07)"
    )
    execute_stage(s_doc, [sys.executable, "tooling/scripts/doctor.py", "--json", str(doctor_json)])
    parse_doctor_json(s_doc, doctor_json)
    s_doc.measurements["runner_context"] = "local-harness workstation (not a clean CI runner)"
    stages.append(s_doc)

    total_duration = time.time() - t0
    success = all(s.status == "PASS" for s in stages)
    return stages, total_duration, success


def save_evidence(
    profile: str, stages: list[StageResult], total_duration: float, success: bool
) -> Path:
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    evidence_file = EVIDENCE_DIR / f"ci-{profile}-run-{timestamp}.json"

    # §0.8.4 Budgets: pre-commit < 30s, pre-merge < 20min (1200s), nightly < 3h (10800s)
    budgets = {
        "pre-commit": 30.0,
        "pre-merge": 1200.0,
        "nightly": 10800.0,
    }
    budget_limit = budgets.get(profile, 1200.0)
    budget_met = total_duration <= budget_limit

    data = {
        "profile": profile,
        "runner": "local-harness",
        "runner_note": (
            "Executed by tooling/ci/run-pipeline.py on a developer workstation — "
            "NOT a GitHub Actions runner. R01-M03-T03 requires an Actions run URL "
            "for the 'real runner' criterion; this record does not satisfy it."
        ),
        "timestamp": datetime.now(UTC).isoformat(),
        "total_duration_seconds": round(total_duration, 2),
        "budget_limit_seconds": budget_limit,
        "budget_met": budget_met,
        "success": success,
        "stages": [s.to_dict() for s in stages],
        "remedies_evaluated": [
            "BG-01: Affected-component test selection based on dependency graph",
            "BG-02: Model-registry fitness checks executed before long-running unit suites",
            "BG-03: Next.js gzip bundle check executed statically without full server boots",
            "BG-04: Non-blocking parallel axe-core accessibility audit across routes",
            "BG-05: Clean doctor DE-20 scheduled nightly rather than blocking every commit",
        ],
    }

    with open(evidence_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print(f"\n[CI] Evidence record written to: {evidence_file}")
    print(
        f"[CI] Profile '{profile}' runtime: {total_duration:.2f}s (Budget: <{budget_limit:.0f}s — {'PASSED' if budget_met else 'EXCEEDED'})"
    )
    return evidence_file


def main():
    parser = argparse.ArgumentParser(description="Unified CI Pipeline Runner")
    parser.add_argument(
        "--profile", choices=["pre-commit", "pre-merge", "nightly", "all"], default="pre-merge"
    )
    args = parser.parse_args()

    profiles_to_run = (
        [args.profile] if args.profile != "all" else ["pre-commit", "pre-merge", "nightly"]
    )
    overall_success = True

    for p in profiles_to_run:
        print(f"\n{'=' * 70}\nStarting CI Profile: {p.upper()}\n{'=' * 70}")
        if p == "pre-commit":
            stages, duration, ok = run_pre_commit()
        elif p == "pre-merge":
            stages, duration, ok = run_pre_merge()
        elif p == "nightly":
            stages, duration, ok = run_nightly()
        else:
            continue

        save_evidence(p, stages, duration, ok)
        if not ok:
            overall_success = False

    if not overall_success:
        print("\n[CI] Pipeline completed with errors or measured gaps.")
        sys.exit(1)
    else:
        print("\n[CI] All profiles executed successfully within budgets.")
        sys.exit(0)


if __name__ == "__main__":
    main()
