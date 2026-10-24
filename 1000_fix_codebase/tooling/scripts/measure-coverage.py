#!/usr/bin/env python3
"""
measure-coverage.py — P02-M04 / R01-M04-T01 & T02 Unified Coverage Harness.

Measures estate-wide branch & line coverage across addons, services, and libs.
Implements the marker split:
  - Estate gate: 80% over EVERY source file under [tool.coverage.run] source
  - Statutory gate: tests marked "financial or tax", measured over the
    STATUTORY_SET below, 100% (DoD-03)

Produces (all deleted before each run — a failed run never leaves, or
re-reads, stale numbers):
  - .coverage (SQLite data of the estate run)
  - coverage.xml (Cobertura XML for CI/codecov)
  - htmlcov/ (interactive HTML browser report)
  - coverage.json (estate per-file data)
  - coverage-financial.json (statutory marker-run per-file data)
  - docs/traceability/evidence/coverage-baseline-report.json

Exit codes:
  0  measurement valid and every requested gate (--fail-under*) passed
  1  measurement valid, at least one requested gate failed
  2  measurement INVALID (pytest failed / no output / statutory path with
     no data) — nothing measured is trusted; the report says UNMEASURED

Denominator method (D6/D9): coverage.py only reports never-imported files
that sit in importable packages; hyphenated service folders
(services/notification-dispatcher, services/local-residency-stub, ...) are
not packages, so their files were invisible. pyproject sets
[tool.coverage.report] include_namespace_packages = true so coverage itself
reports them at 0%; in addition this harness enumerates every *.py under the
source roots (minus the configured omit patterns) and back-fills any file
still absent from the JSON as 0% covered, with statement/branch counts from
coverage's own parser. The back-filled list is written to the report.
"""

from __future__ import annotations

import argparse
import ast
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import UTC, datetime
from importlib import metadata
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_DIR = REPO_ROOT / "docs" / "traceability" / "evidence"
EVIDENCE_FILE = EVIDENCE_DIR / "coverage-baseline-report.json"
COV_JSON = REPO_ROOT / "coverage.json"
FIN_JSON = REPO_ROOT / "coverage-financial.json"
COV_XML = REPO_ROOT / "coverage.xml"
COV_DATA = REPO_ROOT / ".coverage"
HTMLCOV = REPO_ROOT / "htmlcov"

# Test roots collected by both runs (tests/ holds the cross-module journeys).
TEST_ROOTS = ("addons", "services", "libs", "tests")
# Must mirror [tool.coverage.run] source in pyproject.toml.
SOURCE_ROOTS = ("addons", "services", "libs")

ESTATE_TARGET = 80.0
STATUTORY_TARGET = 100.0
STATUTORY_MARKER = "financial or tax"

# ---------------------------------------------------------------------------
# STATUTORY_SET — the single source of truth for the DoD-03 100% gate.
# (path relative to the codebase root, why it is statutory). Every entry is
# measured by the "financial or tax" marker run; the register derives its
# 100% targets from this list (exported in the report as `statutory_set`).
# ---------------------------------------------------------------------------
STATUTORY_SET: tuple[tuple[str, str], ...] = (
    (
        "addons/domain/g_finance/cd_tax_engine_bd",
        "M51 Tax & Regulatory (BD): VAT/SD/AIT computation and Mushak returns filed with NBR",
    ),
    (
        "services/evat-adapter",
        "M51 NBR e-VAT (Mushak) submission adapter; its tests carry the tax marker",
    ),
    (
        "addons/domain/h_people/cd_payroll_bd",
        "M56 Payroll & Statutory: payslips, PF, gratuity, BEFTN batches (Labour Act / ITA 2023)",
    ),
    (
        "libs/py/payroll_engine",
        "M56 payroll calculation kernel — the ONLY payroll calculation authority "
        "(tax slabs, PF, gratuity, BEFTN file) used by cd_payroll_bd",
    ),
    (
        "services/payroll-engine",
        "M56 L5 service shell re-exporting the payroll kernel (public contract surface)",
    ),
    (
        "addons/domain/g_finance/cd_billing_engine",
        "M20 AR & invoicing: VAT-bearing customer invoices and credit notes",
    ),
    (
        "addons/domain/g_finance/cd_gl_ext",
        "M19 General Ledger: chart of accounts, fiscal-year close, journal postings",
    ),
    (
        "addons/domain/g_finance/cd_ap_ext",
        "M52 AP: vendor invoices and TDS/VDS withholding determination via M51",
    ),
    (
        "addons/domain/g_finance/cd_settlement_ext",
        "M53 Revenue recognition & settlement: seller payouts and payout reconciliation",
    ),
    (
        "libs/py/payout_rail",
        "INT-007 payout rail: money-movement batches used by cd_settlement_ext",
    ),
    (
        "services/pricing-engine",
        "Roadmap R01-M04 'pricing service': customer price computation",
    ),
    (
        "services/settlement-engine",
        "Roadmap R01-M04 'settlement service': settlement amount computation",
    ),
    (
        "services/reconciliation",
        "Roadmap R01-M04 'reconciliation service': bank-feed parsing and matching",
    ),
)


# --------------------------------------------------------------------------- helpers


def rel_posix(path: str | Path) -> str:
    p = Path(path)
    if p.is_absolute():
        try:
            p = p.resolve().relative_to(REPO_ROOT)
        except ValueError:
            return p.as_posix()
    return p.as_posix()


def classify(rel: str) -> tuple[str, str, str, str]:
    """(module_name, category, group, module_root) by PATH PREFIX only."""
    parts = rel.split("/")
    if parts[0] == "addons":
        if len(parts) >= 4 and parts[1] == "domain" and parts[3].startswith("cd_"):
            return parts[3], "odoo-addon", f"addons/domain/{parts[2]}", "/".join(parts[:4])
        if len(parts) >= 3 and parts[1] == "platform" and parts[2].startswith("cd_"):
            return parts[2], "odoo-addon", "addons/platform", "/".join(parts[:3])
        return "addons:(root)", "odoo-addon", "addons", "addons"
    if parts[0] == "services":
        if len(parts) >= 3:
            return f"service:{parts[1]}", "microservice", "services", "/".join(parts[:2])
        return "services:(root)", "microservice", "services", "services"
    if parts[0] == "libs":
        if len(parts) >= 4 and parts[1] == "py":
            return f"lib:{parts[2]}", "shared-lib", "libs/py", "/".join(parts[:3])
        return "lib:(package-root)", "shared-lib", "libs", "libs"
    return "other", "general", "other", parts[0]


def statutory_module_names() -> dict[str, str]:
    """module name -> statutory path (each statutory path is one module root)."""
    out: dict[str, str] = {}
    for path, _why in STATUTORY_SET:
        name, _cat, _grp, root = classify(path + "/x.py")
        if root != path:
            raise SystemExit(f"STATUTORY_SET entry {path} is not a module root (got {root})")
        out[name] = path
    return out


def pct(covered: int, total: int) -> float | None:
    return round(covered / total * 100, 2) if total > 0 else None


def run_command(cmd: list[str], env: dict[str, str] | None = None) -> tuple[int, str, str]:
    full_env = os.environ.copy()
    if env:
        full_env.update(env)
    extra = [str(REPO_ROOT), str(REPO_ROOT / "vendor" / "odoo")]
    if full_env.get("PYTHONPATH"):
        extra.append(full_env["PYTHONPATH"])
    full_env["PYTHONPATH"] = os.pathsep.join(extra)
    full_env["PYTHONIOENCODING"] = "utf-8"
    proc = subprocess.run(
        cmd,
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        shell=False,
        env=full_env,
    )
    return proc.returncode, proc.stdout, proc.stderr


def clean_outputs() -> None:
    for f in (COV_JSON, FIN_JSON, COV_XML, COV_DATA, EVIDENCE_FILE):
        if f.exists():
            f.unlink()
    for f in REPO_ROOT.glob(".coverage.*"):  # parallel-mode leftovers
        f.unlink()
    if HTMLCOV.exists():
        shutil.rmtree(HTMLCOV)


def tool_versions() -> dict[str, str]:
    v = {"python": sys.version.split()[0]}
    for pkg in ("pytest", "pytest-cov", "coverage"):
        try:
            v[pkg] = metadata.version(pkg)
        except metadata.PackageNotFoundError:
            v[pkg] = "not-installed"
    return v


def load_fresh_json(path: Path, label: str, errors: list[str]) -> dict:
    if not path.is_file():
        errors.append(f"{label}: {path.name} was not produced")
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        errors.append(f"{label}: {path.name} unreadable: {e}")
        return {}


# --------------------------------------------------------------- denominator


def _omit_matcher():
    import coverage
    from coverage.files import GlobMatcher, prep_patterns

    cfg = coverage.Coverage(config_file=str(REPO_ROOT / "pyproject.toml")).config
    return GlobMatcher(prep_patterns(cfg.run_omit or []), "omit"), cfg


def enumerate_source_files(roots: tuple[str, ...]) -> list[str]:
    """Every *.py under roots, minus omit patterns and __pycache__."""
    matcher, _cfg = _omit_matcher()
    out: list[str] = []
    cwd = os.getcwd()
    os.chdir(REPO_ROOT)  # relative omit patterns (vendor/*) resolve against cwd
    try:
        for root in roots:
            for p in (REPO_ROOT / root).rglob("*.py"):
                if "__pycache__" in p.parts or "node_modules" in p.parts:
                    continue
                if matcher.match(str(p)):
                    continue
                out.append(rel_posix(p))
    finally:
        os.chdir(cwd)
    return sorted(out)


def static_counts(rel: str) -> dict | None:
    """Statement/branch counts for a never-executed file (coverage's parser)."""
    from coverage.parser import PythonParser

    _m, cfg = _omit_matcher()
    exclude = "|".join(f"(?:{x})" for x in (cfg.exclude_list or [])) or None
    try:
        parser = PythonParser(filename=str(REPO_ROOT / rel), exclude=exclude)
        parser.parse_source()
        n_statements = len(parser.statements)
        n_branches = sum(c for c in parser.exit_counts().values() if c > 1)
    except Exception:
        return None
    return {
        "covered_lines": 0,
        "num_statements": n_statements,
        "missing_lines": n_statements,
        "num_branches": n_branches,
        "covered_branches": 0,
        "missing_branches": n_branches,
        "percent_covered": 0.0 if (n_statements + n_branches) else 100.0,
    }


def normalise_files(
    data: dict, expected: list[str]
) -> tuple[dict[str, dict], list[str], list[str]]:
    """posix-rel -> summary; back-fill expected-but-absent files at 0%."""
    files = {rel_posix(k): v.get("summary", {}) for k, v in data.get("files", {}).items()}
    backfilled: list[str] = []
    unparseable: list[str] = []
    for rel in expected:
        if rel in files:
            continue
        s = static_counts(rel)
        if s is None:
            unparseable.append(rel)
            continue
        files[rel] = s
        backfilled.append(rel)
    return files, backfilled, unparseable


def summarise(files: dict[str, dict]) -> dict:
    t = dict.fromkeys(("ns", "cl", "ml", "nb", "cb", "mb"), 0)
    for s in files.values():
        t["ns"] += s.get("num_statements", 0)
        t["cl"] += s.get("covered_lines", 0)
        t["ml"] += s.get("missing_lines", 0)
        t["nb"] += s.get("num_branches", 0)
        t["cb"] += s.get("covered_branches", 0)
        t["mb"] += s.get("missing_branches", 0)
    total = t["ns"] + t["nb"]
    covered = t["cl"] + t["cb"]
    return {
        "files": len(files),
        "total_statements": t["ns"],
        "covered_statements": t["cl"],
        "missing_statements": t["ml"],
        "total_branches": t["nb"],
        "covered_branches": t["cb"],
        "missing_branches": t["mb"],
        "total_elements": total,
        "covered_elements": covered,
        "percent_covered": pct(covered, total),
    }


def is_pure_logic(rel: str) -> bool:
    """No Odoo import and defines at least one function/class."""
    try:
        tree = ast.parse((REPO_ROOT / rel).read_text(encoding="utf-8"))
    except Exception:
        return False
    has_def = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Import) and any(
            a.name == "odoo" or a.name.startswith("odoo.") for a in node.names
        ):
            return False
        if isinstance(node, ast.ImportFrom) and (node.module or "").split(".")[0] == "odoo":
            return False
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef):
            has_def = True
    return has_def


# --------------------------------------------------------------- measurement


def measure_all() -> dict:
    print("\n" + "=" * 70)
    print("1000 FiX ERP — Milestone R01-M04 Coverage Measurement Harness")
    print("=" * 70)
    errors: list[str] = []
    clean_outputs()
    started = datetime.now(UTC)
    t0 = time.time()

    # [1/3] Estate run. --cov (bare) uses [tool.coverage.run] source; the
    # pytest-cov fail-under is pinned to 0 so pytest's exit code reflects
    # TEST results only — the gates are applied below by this harness.
    print("\n[1/3] Executing full estate pytest with branch coverage...")
    cov_cmd = [
        sys.executable, "-m", "pytest", *TEST_ROOTS,
        "--cov", "--cov-branch", "--cov-fail-under=0",
        "--cov-report=xml:coverage.xml",
        "--cov-report=html:htmlcov",
        "--cov-report=json:coverage.json",
        "-p", "no:cacheprovider", "-q", "--tb=short",
    ]  # fmt: skip
    code, out, err = run_command(cov_cmd)
    estate_duration = time.time() - t0
    print(f"      Estate run completed in {estate_duration:.2f}s (pytest exit {code})")
    if code != 0:
        errors.append(f"estate pytest run exited {code}")
        print((out + err)[-3000:])

    # [2/3] Statutory marker split. Separate COVERAGE_FILE so the estate
    # .coverage is not overwritten by the marker run.
    print(f"\n[2/3] Executing statutory '{STATUTORY_MARKER}' marker split (DoD-03)...")
    t1 = time.time()
    tmpdir = tempfile.mkdtemp(prefix="cov-fin-")
    marker_cmd = [
        sys.executable, "-m", "pytest", *TEST_ROOTS,
        "-m", STATUTORY_MARKER,
        *[f"--cov={p}" for p, _ in STATUTORY_SET],
        "--cov-branch", "--cov-fail-under=0",
        "--cov-report=json:coverage-financial.json",
        "-p", "no:cacheprovider", "-q", "--tb=short",
    ]  # fmt: skip
    m_code, m_out, m_err = run_command(
        marker_cmd, env={"COVERAGE_FILE": str(Path(tmpdir) / ".coverage")}
    )
    shutil.rmtree(tmpdir, ignore_errors=True)
    marker_duration = time.time() - t1
    print(f"      Statutory run completed in {marker_duration:.2f}s (pytest exit {m_code})")
    if m_code != 0:
        errors.append(f"statutory marker pytest run exited {m_code}")
        print((m_out + m_err)[-3000:])

    # [3/3] Parse ONLY the files produced by this run (stale ones were deleted).
    print("\n[3/3] Parsing coverage metrics and computing per-module statistics...")
    cov_data = load_fresh_json(COV_JSON, "estate", errors)
    fin_data = load_fresh_json(FIN_JSON, "statutory", errors)

    estate_expected = enumerate_source_files(SOURCE_ROOTS)
    stat_roots = tuple(p for p, _ in STATUTORY_SET)
    stat_expected = enumerate_source_files(stat_roots)

    est_files, est_backfill, est_unparse = (
        normalise_files(cov_data, estate_expected) if cov_data else ({}, [], [])
    )
    fin_files, fin_backfill, fin_unparse = (
        normalise_files(fin_data, stat_expected) if fin_data else ({}, [], [])
    )
    # The statutory JSON must contain only statutory files.
    fin_files = {k: v for k, v in fin_files.items() if k.startswith(stat_roots)}

    valid = not errors
    estate = summarise(est_files)
    statutory = summarise(fin_files)
    if cov_data and not est_backfill:
        ct = cov_data.get("totals", {})
        if (ct.get("num_statements"), ct.get("num_branches")) != (
            estate["total_statements"],
            estate["total_branches"],
        ):
            errors.append("estate totals do not reconcile with coverage.json totals")
            valid = False

    # Per-module aggregation (estate run, all tests).
    stat_names = statutory_module_names()
    modules: dict[str, dict] = {}
    for rel, s in est_files.items():
        name, cat, grp, root = classify(rel)
        m = modules.setdefault(
            name,
            {
                "name": name, "category": cat, "group": grp, "path": root,
                "statutory": name in stat_names, "files": 0, "unexecuted_files": 0,
                "num_statements": 0, "covered_statements": 0, "missing_statements": 0,
                "num_branches": 0, "covered_branches": 0, "missing_branches": 0,
            },
        )  # fmt: skip
        m["files"] += 1
        if s.get("covered_lines", 0) == 0 and s.get("num_statements", 0) > 0:
            m["unexecuted_files"] += 1
        m["num_statements"] += s.get("num_statements", 0)
        m["covered_statements"] += s.get("covered_lines", 0)
        m["missing_statements"] += s.get("missing_lines", 0)
        m["num_branches"] += s.get("num_branches", 0)
        m["covered_branches"] += s.get("covered_branches", 0)
        m["missing_branches"] += s.get("missing_branches", 0)
    for m in modules.values():
        total = m["num_statements"] + m["num_branches"]
        covered = m["covered_statements"] + m["covered_branches"]
        m["total_elements"] = total
        m["covered_elements"] = covered
        m["percent_covered"] = pct(covered, total)  # None == n/a (no measurable code)
        m["target_percent"] = STATUTORY_TARGET if m["statutory"] else ESTATE_TARGET

    # Per statutory entry (marker run, marked tests only).
    statutory_entries = []
    for path, why in STATUTORY_SET:
        sub = {k: v for k, v in fin_files.items() if k.startswith(path + "/")}
        summ = summarise(sub)
        entry = {"path": path, "module": classify(path + "/x.py")[0], "why": why, **summ}
        if not sub:
            entry["status"] = "NO_DATA"
            errors.append(f"statutory path {path} produced no measured data")
            valid = False
        statutory_entries.append(entry)

    # Pure-calculation logic: every statutory file with no Odoo import that
    # defines a function/class. Measured from the marker run per file.
    pure_logic_per_file: dict[str, float | None] = {}
    for rel in sorted(fin_files):
        if is_pure_logic(rel):
            s = fin_files[rel]
            pure_logic_per_file[rel] = pct(
                s.get("covered_lines", 0) + s.get("covered_branches", 0),
                s.get("num_statements", 0) + s.get("num_branches", 0),
            )
    measured_pure = {k: v for k, v in pure_logic_per_file.items() if v is not None}
    if valid and measured_pure:
        pure_min_file = min(measured_pure, key=lambda k: measured_pure[k])
        pure_logic_coverage_pct = measured_pure[pure_min_file]
        pure_logic_basis = (
            "min of measured per-file percentages over every statutory file with no "
            "Odoo import that defines a function or class"
        )
    else:
        pure_min_file = None
        pure_logic_coverage_pct = None
        pure_logic_basis = "UNMEASURED (measurement invalid or no pure-logic files)"

    estate_pct = estate["percent_covered"] if valid else None
    stat_pct = statutory["percent_covered"] if valid else None

    def verdict(value: float | None, target: float) -> str:
        if value is None:
            return "UNMEASURED"
        return "PASS" if value >= target else "FAIL"

    def to_target(summ: dict, target: float) -> int | None:
        if not valid or not summ["total_elements"]:
            return None
        return max(0, math.ceil(target / 100 * summ["total_elements"]) - summ["covered_elements"])

    report = {
        "schema": "1000fix-erp/coverage-baseline-report/2",
        "timestamp": started.isoformat(),
        "measurement_valid": valid,
        "errors": errors,
        "tool_versions": tool_versions(),
        "runs": {
            "estate": {
                "command": cov_cmd[1:],
                "pytest_exit_code": code,
                "duration_seconds": round(estate_duration, 2),
            },
            "statutory": {
                "command": marker_cmd[1:],
                "pytest_exit_code": m_code,
                "duration_seconds": round(marker_duration, 2),
            },
        },
        "denominator": {
            "method": (
                "every *.py under [tool.coverage.run] source minus omit patterns; "
                "include_namespace_packages=true; files still absent from coverage JSON "
                "back-filled at 0% with coverage's PythonParser counts"
            ),
            "estate_source_files": len(estate_expected),
            "estate_backfilled_unexecuted_files": est_backfill,
            "statutory_backfilled_unexecuted_files": fin_backfill,
            "unparseable_files": sorted(set(est_unparse + fin_unparse)),
        },
        "estate_summary": {
            **estate,
            "percent_covered": estate_pct,
            "target_gate_percent": ESTATE_TARGET,
            "gap_to_target_percent": (
                round(max(0.0, ESTATE_TARGET - estate_pct), 2) if estate_pct is not None else None
            ),
            "elements_to_target": to_target(estate, ESTATE_TARGET),
            "status": verdict(estate_pct, ESTATE_TARGET),
        },
        "statutory_financial_tax_summary": {
            **statutory,
            "marker": STATUTORY_MARKER,
            "percent_covered": stat_pct,
            "pure_logic_coverage_percent": pure_logic_coverage_pct,
            "pure_logic_min_file": pure_min_file,
            "pure_logic_per_file": pure_logic_per_file,
            "pure_logic_basis": pure_logic_basis,
            "target_gate_percent": STATUTORY_TARGET,
            "gap_to_target_percent": (
                round(max(0.0, STATUTORY_TARGET - stat_pct), 2) if stat_pct is not None else None
            ),
            "elements_to_target": to_target(statutory, STATUTORY_TARGET),
            "status": verdict(stat_pct, STATUTORY_TARGET),
            "statutory_modules": [e["module"] for e in statutory_entries],
            "per_path": statutory_entries,
        },
        # Consumer alias kept for earlier readers of `statutory_summary`.
        "statutory_summary": {
            "percent_covered": stat_pct,
            "pure_logic_coverage_percent": pure_logic_coverage_pct,
            "target_gate_percent": STATUTORY_TARGET,
            "status": verdict(stat_pct, STATUTORY_TARGET),
        },
        "statutory_set": [{"path": p, "why": w} for p, w in STATUTORY_SET],
        "modules": sorted(modules.values(), key=lambda x: (x["category"], x["group"], x["name"])),
    }
    return report


def write_report(report: dict) -> None:
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    EVIDENCE_FILE.write_text(json.dumps(report, indent=2), encoding="utf-8")


def show(v: float | None) -> str:
    return f"{v:.2f}%" if v is not None else "UNMEASURED"


def main() -> int:
    parser = argparse.ArgumentParser(description="1000 FiX ERP Coverage Measurement Harness")
    parser.add_argument(
        "--fail-under", type=float, default=None, help="Fail if estate coverage under threshold"
    )
    parser.add_argument(
        "--fail-under-financial",
        type=float,
        default=None,
        help="Fail if statutory financial/tax marker coverage under threshold (DoD-03 gate is 100)",
    )
    args = parser.parse_args()

    report = measure_all()
    est = report["estate_summary"]
    fin = report["statutory_financial_tax_summary"]

    gates: dict[str, dict] = {}
    failed = False
    for key, value, threshold in (
        ("estate", est["percent_covered"], args.fail_under),
        ("statutory", fin["percent_covered"], args.fail_under_financial),
    ):
        if threshold is None:
            continue
        v = "UNMEASURED" if value is None else "PASS" if value >= threshold else "FAIL"
        gates[key] = {"threshold_percent": threshold, "measured_percent": value, "verdict": v}
        if v != "PASS":
            failed = True
            print(f"\n[FAIL] {key} coverage {show(value)} is below threshold {threshold}%")

    exit_code = 2 if not report["measurement_valid"] else 1 if failed else 0
    report["gates_applied"] = gates
    report["harness_exit_code"] = exit_code
    write_report(report)

    print(f"\n[ok] Coverage evidence saved to: {EVIDENCE_FILE}")
    print(f"     Estate Coverage:       {show(est['percent_covered'])} (target {ESTATE_TARGET}%)")
    print(
        f"     Statutory Fin/Tax:     {show(fin['percent_covered'])} (target {STATUTORY_TARGET}%)"
    )
    print(
        f"     Pure logic (min):      {show(fin['pure_logic_coverage_percent'])} "
        f"({fin['pure_logic_min_file']})"
    )
    print(f"     HTML Report:           {HTMLCOV / 'index.html'}")
    if report["errors"]:
        print("\n[INVALID] Measurement errors — numbers are NOT trusted:")
        for e in report["errors"]:
            print(f"     - {e}")
    print(f"\nharness exit code: {exit_code}")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
