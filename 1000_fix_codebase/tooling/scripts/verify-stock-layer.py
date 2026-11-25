#!/usr/bin/env python3
"""Verify availability and manifest integrity of Odoo stock layer and OCA stock modules.

Validates Task R03-M01-T01:
- Odoo core 'stock' module present in vendor/odoo/addons/stock.
- Vendored OCA stock repositories (stock-logistics-workflow, stock-logistics-barcode, stock-logistics-warehouse).
- Manifest dependencies and key modules verified.

Every component status is MEASURED in the run (GV-009): each manifest is parsed
(ast.literal_eval), its `installable` flag read, its `depends` resolved against the
modules actually present under vendor/, and OCA module versions compared with the
Odoo series read from vendor/odoo/odoo/release.py. A component is PASS only when
all of those observations hold; anything else is FAIL with the reason recorded.

Emits structured JSON evidence to tooling/fitness/evidence/stock-layer-verification-latest.json.
Exit code: 0 PASS, 1 FAIL (derived from the checks).
"""

from __future__ import annotations

import ast
import json
import re
import sys
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
VENDOR_ODOO = REPO_ROOT / "vendor" / "odoo" / "addons"
VENDOR_ODOO_BASE = REPO_ROOT / "vendor" / "odoo" / "odoo" / "addons"
ODOO_RELEASE = REPO_ROOT / "vendor" / "odoo" / "odoo" / "release.py"
VENDOR_OCA = REPO_ROOT / "vendor" / "oca"
EVIDENCE_DIR = REPO_ROOT / "tooling" / "fitness" / "evidence"
EVIDENCE_NAME = "stock-layer-verification-latest.json"

REQUIRED_OCA_REPOS = [
    "stock-logistics-workflow",
    "stock-logistics-barcode",
    "stock-logistics-warehouse",
]

KEY_OCA_MODULES = [
    ("stock-logistics-workflow", "stock_no_negative"),
    ("stock-logistics-workflow", "scrap_reason_code"),
    ("stock-logistics-barcode", "barcodes_generator_product"),
    ("stock-logistics-warehouse", "stock_inventory"),
    ("stock-logistics-warehouse", "stock_location_is_sublocation"),
]

EXIT_CODES = {"PASS": 0, "FAIL": 1, "INCOMPLETE": 2}


def _rel(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def read_manifest(path: Path) -> tuple[dict | None, str | None]:
    """Parse an Odoo manifest as a literal dict; return (data, error)."""
    try:
        data = ast.literal_eval(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, SyntaxError, UnicodeDecodeError) as exc:
        return None, f"manifest unparseable: {type(exc).__name__}: {exc}"
    if not isinstance(data, dict):
        return None, "manifest is not a dict literal"
    return data, None


def read_odoo_series() -> tuple[str | None, str | None]:
    """Read the Odoo series (e.g. '19.0') from vendor/odoo/odoo/release.py."""
    try:
        text = ODOO_RELEASE.read_text(encoding="utf-8")
    except OSError as exc:
        return None, f"cannot read {_rel(ODOO_RELEASE)}: {exc}"
    match = re.search(r"^version_info\s*=\s*\(\s*(\d+)\s*,\s*(\d+)", text, re.MULTILINE)
    if not match:
        return None, f"version_info not found in {_rel(ODOO_RELEASE)}"
    return f"{match.group(1)}.{match.group(2)}", None


def available_modules() -> set[str]:
    """Names of every module (dir with __manifest__.py) present under vendor/."""
    names: set[str] = set()
    for root in (VENDOR_ODOO, VENDOR_ODOO_BASE):
        if root.is_dir():
            names.update(p.parent.name for p in root.glob("*/__manifest__.py"))
    if VENDOR_OCA.is_dir():
        names.update(p.parent.name for p in VENDOR_OCA.glob("*/*/__manifest__.py"))
    return names


def check_module(
    component: str,
    mod_dir: Path,
    available: set[str],
    series: str | None,
    require_series: bool,
) -> dict:
    """Parse one module manifest and verify installable / depends / version series."""
    manifest = mod_dir / "__manifest__.py"
    problems: list[str] = []
    observed: dict = {}
    if not manifest.is_file():
        problems.append(f"manifest missing at {_rel(manifest)}")
    else:
        data, err = read_manifest(manifest)
        if err:
            problems.append(err)
        else:
            installable = data.get("installable", True)
            observed["installable"] = installable
            if installable is False:
                problems.append("manifest declares installable=False")
            depends = data.get("depends", [])
            observed["depends"] = depends
            if not isinstance(depends, list):
                problems.append("depends is not a list")
            else:
                unresolved = sorted(d for d in depends if d not in available)
                observed["unresolved_depends"] = unresolved
                if unresolved:
                    problems.append(f"depends not present under vendor/: {unresolved}")
            version = str(data.get("version", ""))
            observed["version"] = version
            if require_series:
                if series is None:
                    problems.append("Odoo series unknown - cannot check module version")
                elif not version.startswith(f"{series}."):
                    problems.append(f"version {version!r} is not on Odoo series {series}")
    return {
        "component": component,
        "path": _rel(mod_dir),
        "status": "FAIL" if problems else "PASS",
        "observed": observed,
        "problems": problems,
    }


def check_oca_repo(repo_name: str, series: str | None) -> dict:
    """Verify an OCA repo is vendored and every module manifest in it parses on-series."""
    repo_dir = VENDOR_OCA / repo_name
    problems: list[str] = []
    manifests = sorted(repo_dir.glob("*/__manifest__.py")) if repo_dir.is_dir() else []
    unparseable: list[str] = []
    off_series: list[str] = []
    if not repo_dir.is_dir():
        problems.append(f"OCA repository missing at {_rel(repo_dir)}")
    elif not manifests:
        problems.append("no module manifests found in repository")
    for mf in manifests:
        data, err = read_manifest(mf)
        if err:
            unparseable.append(mf.parent.name)
            continue
        version = str(data.get("version", ""))
        if series is not None and not version.startswith(f"{series}."):
            off_series.append(f"{mf.parent.name}={version}")
    if unparseable:
        problems.append(f"unparseable manifests: {unparseable}")
    if off_series:
        problems.append(f"modules not on Odoo series {series}: {off_series}")
    if series is None and manifests:
        problems.append("Odoo series unknown - cannot check module versions")
    return {
        "component": repo_name,
        "path": _rel(repo_dir),
        "status": "FAIL" if problems else "PASS",
        "modules_found": len(manifests),
        "problems": problems,
    }


def overall_verdict(statuses: list[str]) -> str:
    if not statuses:
        return "INCOMPLETE"
    if "FAIL" in statuses:
        return "FAIL"
    if any(s != "PASS" for s in statuses):
        return "INCOMPLETE"
    return "PASS"


def run_checks() -> dict:
    results: list[dict] = []

    series, series_err = read_odoo_series()
    results.append(
        {
            "component": "odoo_series",
            "path": _rel(ODOO_RELEASE),
            "status": "FAIL" if series_err else "PASS",
            "observed": {"series": series},
            "problems": [series_err] if series_err else [],
        }
    )

    available = available_modules()

    # 1. Core Odoo stock module (core manifests carry no series prefix)
    results.append(check_module("odoo_core_stock", VENDOR_ODOO / "stock", available, series, False))

    # 2. OCA repositories
    results.extend(check_oca_repo(repo_name, series) for repo_name in REQUIRED_OCA_REPOS)

    # 3. Key OCA stock modules
    for repo_name, mod_name in KEY_OCA_MODULES:
        results.append(
            check_module(
                f"{repo_name}/{mod_name}",
                VENDOR_OCA / repo_name / mod_name,
                available,
                series,
                True,
            )
        )

    errors = [f"{r['component']}: {p}" for r in results for p in r["problems"]]
    verdict = overall_verdict([r["status"] for r in results])
    return {
        "timestamp": datetime.now(UTC).isoformat(),
        "task": "R03-M01-T01",
        "milestone": "R03-M01",
        "verdict": verdict,
        "measurement": (
            "manifests parsed with ast.literal_eval; depends resolved against modules present "
            "under vendor/; OCA versions compared with vendor/odoo/odoo/release.py series"
        ),
        "checks_total": len(results),
        "checks_passed": sum(1 for r in results if r["status"] == "PASS"),
        "results": results,
        "errors": errors,
    }


def main() -> int:
    print("=" * 70)
    print("1000FiX ERP Platform: Odoo Stock & OCA Stock Layer Verification")
    print("Task: R03-M01-T01 (M15 Spare Parts & Inventory on Odoo stock + OCA)")
    print("=" * 70)

    evidence = run_checks()
    for r in evidence["results"]:
        extra = f" ({r['modules_found']} modules)" if "modules_found" in r else ""
        print(f"  [{r['status']}] {r['component']}{extra}")
        for p in r["problems"]:
            print(f"         - {p}")

    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    out_file = EVIDENCE_DIR / EVIDENCE_NAME
    with open(out_file, "w", encoding="utf-8", newline="\n") as f:
        json.dump(evidence, f, indent=2)

    verdict = evidence["verdict"]
    print("-" * 70)
    print(
        f"Stock Layer Verification Verdict: [{verdict}] "
        f"({evidence['checks_passed']}/{evidence['checks_total']} checks passed)"
    )
    print(f"Evidence written to: {_rel(out_file)}")
    print("=" * 70)

    return EXIT_CODES.get(verdict, 2)


if __name__ == "__main__":
    sys.exit(main())
