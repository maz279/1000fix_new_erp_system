#!/usr/bin/env python3
"""verify_fork_and_oca_matrix.py — P09-M02-T02 / R07-M02-T02: Fork Audit & OCA v20 Availability Matrix.

Verifies (GV-009: every status is measured in this run, READ-ONLY):
1. Fork Audit:
   - FORKS.yaml exists, parses, and every entry carries the mandatory fields.
   - vendor/ working tree has no modification that a FORKS.yaml entry does not authorise
     (`git status --porcelain -- vendor/`, the same rule as check-vendor-clean / FF-03).
   - every vendored OCA repository has a commit pin in tooling/versions.lock and vice versa.
   - every vendored OCA module manifest is on the Odoo series read from
     vendor/odoo/odoo/release.py, and VENDOR_ODOO_BRANCH matches that series.
2. OCA v20 Availability Assessment across the vendored repositories:
   - the locally observable state (vendored series, module count, pin) is measured;
   - upstream 20.0 availability lives on github.com/OCA and is NOT observable from this
     local, read-only run, so it is reported UNMEASURED per repository, and the
     D-025 §5 revisit trigger (>= 12 repositories migrated) is left undetermined.
3. Writes evidence to docs/traceability/evidence/fork-audit-and-oca-v20-matrix.json.

Overall verdict: FAIL if any check FAILs, else INCOMPLETE while anything is UNMEASURED.
Exit code: 0 PASS, 1 FAIL, 2 INCOMPLETE.
"""

from __future__ import annotations

import ast
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_DIR = REPO_ROOT / "docs" / "traceability" / "evidence"
EVIDENCE_NAME = "fork-audit-and-oca-v20-matrix.json"
FORKS_FILE = REPO_ROOT / "FORKS.yaml"
VERSIONS_LOCK = REPO_ROOT / "tooling" / "versions.lock"
VENDOR_DIR = REPO_ROOT / "vendor"
VENDOR_OCA = VENDOR_DIR / "oca"
ODOO_RELEASE = VENDOR_DIR / "odoo" / "odoo" / "release.py"

FORK_FIELDS = [
    "repo",
    "path",
    "reason",
    "upstream",
    "exit_plan",
    "approved_by",
    "added_in_release",
    "review_by_release",
]
# D-025 §5: fewer than 12 repositories with v20 availability at G5/G6 -> escalate.
D025_THRESHOLD = 12
V20_UNMEASURED_REASON = (
    "upstream 20.0 branch availability is held on github.com/OCA; this verifier is local and "
    "read-only and does not query the network"
)
EXIT_CODES = {"PASS": 0, "FAIL": 1, "INCOMPLETE": 2}


def overall_verdict(statuses: list[str]) -> str:
    if not statuses:
        return "INCOMPLETE"
    if "FAIL" in statuses:
        return "FAIL"
    if any(s != "PASS" for s in statuses):
        return "INCOMPLETE"
    return "PASS"


def _check(name: str, status: str, detail: str, **observed) -> dict:
    return {"check": name, "status": status, "detail": detail, **observed}


def _rel(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def read_odoo_series() -> str | None:
    try:
        text = ODOO_RELEASE.read_text(encoding="utf-8")
    except OSError:
        return None
    match = re.search(r"^version_info\s*=\s*\(\s*(\d+)\s*,\s*(\d+)", text, re.MULTILINE)
    return f"{match.group(1)}.{match.group(2)}" if match else None


def read_versions_lock() -> dict[str, str]:
    values: dict[str, str] = {}
    try:
        text = VERSIONS_LOCK.read_text(encoding="utf-8")
    except OSError:
        return values
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        values[key.strip()] = value.strip()
    return values


def oca_pins(lock: dict[str, str]) -> dict[str, str]:
    """VENDOR_OCA_FIELD_SERVICE=<sha> -> {'field-service': '<sha>'} (VENDOR_OCA_ORG excluded)."""
    return {
        key[len("VENDOR_OCA_") :].lower().replace("_", "-"): value
        for key, value in lock.items()
        if key.startswith("VENDOR_OCA_") and key != "VENDOR_OCA_ORG"
    }


def load_forks() -> tuple[list | None, str | None]:
    if not FORKS_FILE.is_file():
        return None, f"{_rel(FORKS_FILE)} not found"
    try:
        data = yaml.safe_load(FORKS_FILE.read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError) as exc:
        return None, f"{_rel(FORKS_FILE)} unparseable: {exc}"
    forks = data.get("forks", []) if isinstance(data, dict) else None
    if forks is None:
        forks = []
    if not isinstance(forks, list):
        return None, "`forks` is not a list"
    return forks, None


def git_status_vendor() -> tuple[str, list[str]] | None:
    """(repo-relative prefix, porcelain lines) for vendor/, or None when git is unavailable.

    Read-only: GIT_OPTIONAL_LOCKS=0 stops `git status` refreshing/locking the index."""
    env = {**os.environ, "GIT_OPTIONAL_LOCKS": "0"}
    try:
        prefix = subprocess.run(
            ["git", "-C", str(REPO_ROOT), "rev-parse", "--show-prefix"],
            capture_output=True,
            text=True,
            timeout=30,
            check=True,
            env=env,
        ).stdout.strip()
        out = subprocess.run(
            ["git", "-C", str(REPO_ROOT), "status", "--porcelain", "--", "vendor/"],
            capture_output=True,
            text=True,
            timeout=120,
            check=True,
            env=env,
        ).stdout
    except (OSError, subprocess.SubprocessError):
        return None
    return prefix, [line for line in out.splitlines() if line.strip()]


def authorised_prefixes(forks: list, prefix: str) -> list[str]:
    out = []
    for entry in forks:
        if not isinstance(entry, dict):
            continue
        repo = str(entry.get("repo", "")).strip()
        path = str(entry.get("path", "")).strip().strip("/")
        if repo == "odoo":
            base = f"{prefix}vendor/odoo"
        else:
            name = repo.split("/", 1)[1] if repo.lower().startswith("oca/") else repo
            base = f"{prefix}vendor/oca/{name}"
        out.append(f"{base}/{path}".rstrip("/"))
    return out


def _porcelain_path(line: str) -> str:
    path = line[3:].strip()
    if " -> " in path:
        path = path.split(" -> ", 1)[1]
    return path.strip('"')


def run_fork_audit(odoo_series: str | None, lock: dict[str, str]) -> tuple[dict, list[dict]]:
    checks: list[dict] = []

    forks, err = load_forks()
    checks.append(
        _check(
            "forks_yaml_parsed",
            "FAIL" if err else "PASS",
            err or f"{len(forks)} fork entr{'y' if len(forks) == 1 else 'ies'} declared",
        )
    )
    forks = forks or []

    incomplete = [
        {"index": i, "missing": [f for f in FORK_FIELDS if not (e or {}).get(f)]}
        for i, e in enumerate(forks)
        if not isinstance(e, dict) or any(not e.get(f) for f in FORK_FIELDS)
    ]
    checks.append(
        _check(
            "fork_entries_complete",
            "FAIL" if incomplete else "PASS",
            f"entries missing mandatory fields: {incomplete}"
            if incomplete
            else "every entry carries all mandatory fields",
        )
    )

    status = git_status_vendor()
    unauthorised: list[str] = []
    modified: list[str] = []
    if status is None:
        checks.append(
            _check(
                "vendor_worktree_clean",
                "UNMEASURED",
                "git is unavailable or this is not a git checkout - vendor/ modifications "
                "cannot be observed",
            )
        )
    else:
        prefix, lines = status
        allowed = authorised_prefixes(forks, prefix)
        modified = [_porcelain_path(line) for line in lines]
        unauthorised = [p for p in modified if not any(p.startswith(a) for a in allowed)]
        checks.append(
            _check(
                "vendor_worktree_clean",
                "FAIL" if unauthorised else "PASS",
                f"{len(unauthorised)} unauthorised modification(s) under vendor/: "
                f"{unauthorised[:20]}"
                if unauthorised
                else f"{len(modified)} modification(s) under vendor/, all FORKS.yaml-authorised",
            )
        )

    pins = oca_pins(lock)
    vendored = (
        sorted(p.name for p in VENDOR_OCA.iterdir() if p.is_dir()) if VENDOR_OCA.is_dir() else []
    )
    unpinned = sorted(set(vendored) - set(pins))
    not_vendored = sorted(set(pins) - set(vendored))
    pending = sorted(r for r, sha in pins.items() if not re.fullmatch(r"[0-9a-f]{40}", sha))
    pin_problems = []
    if not vendored:
        pin_problems.append(f"no repositories under {_rel(VENDOR_OCA)}")
    if unpinned:
        pin_problems.append(f"vendored but not pinned in versions.lock: {unpinned}")
    if not_vendored:
        pin_problems.append(f"pinned in versions.lock but not vendored: {not_vendored}")
    if pending:
        pin_problems.append(f"pins that are not a 40-hex commit: {pending}")
    checks.append(
        _check(
            "vendor_pins_match_tree",
            "FAIL" if pin_problems else "PASS",
            "; ".join(pin_problems)
            or f"{len(vendored)} vendored OCA repositories, each pinned in versions.lock",
        )
    )

    series_problems = []
    odoo_branch = lock.get("VENDOR_ODOO_BRANCH")
    if odoo_series is None:
        series_problems.append(f"Odoo series not readable from {_rel(ODOO_RELEASE)}")
    elif odoo_branch != odoo_series:
        series_problems.append(
            f"VENDOR_ODOO_BRANCH={odoo_branch!r} but vendored Odoo is {odoo_series}"
        )
    off_series: list[str] = []
    unparseable: list[str] = []
    for repo in vendored:
        for mf in sorted((VENDOR_OCA / repo).glob("*/__manifest__.py")):
            try:
                data = ast.literal_eval(mf.read_text(encoding="utf-8"))
                version = str(data.get("version", "")) if isinstance(data, dict) else ""
            except (OSError, ValueError, SyntaxError, UnicodeDecodeError):
                unparseable.append(f"{repo}/{mf.parent.name}")
                continue
            if odoo_series and not version.startswith(f"{odoo_series}."):
                off_series.append(f"{repo}/{mf.parent.name}={version}")
    if off_series:
        series_problems.append(f"modules off the {odoo_series} series: {off_series[:20]}")
    if unparseable:
        series_problems.append(f"unparseable manifests: {unparseable[:20]}")
    checks.append(
        _check(
            "vendored_series_consistent",
            "FAIL" if series_problems else "PASS",
            "; ".join(series_problems)
            or f"all vendored OCA modules and the Odoo pin are on series {odoo_series}",
        )
    )

    result = {
        "forks_file": _rel(FORKS_FILE),
        "authorised_fork_entries": len(forks),
        "forks_entries": forks,
        "vendor_modifications_observed": len(modified) if status is not None else None,
        "unauthorised_modifications": unauthorised if status is not None else None,
        "odoo_series": odoo_series,
        "vendor_odoo_branch_pin": odoo_branch,
    }
    fork_statuses = [c["status"] for c in checks]
    result["vendor_clean"] = overall_verdict(fork_statuses) == "PASS"
    result["as_05_ff_03_status"] = overall_verdict(fork_statuses)
    return result, checks


def evaluate_oca_v20_matrix(odoo_series: str | None, lock: dict[str, str]) -> tuple[dict, dict]:
    pins = oca_pins(lock)
    vendored = (
        sorted(p.name for p in VENDOR_OCA.iterdir() if p.is_dir()) if VENDOR_OCA.is_dir() else []
    )
    repos = []
    for repo in sorted(set(vendored) | set(pins)):
        repo_dir = VENDOR_OCA / repo
        series_seen: dict[str, int] = {}
        modules = sorted(repo_dir.glob("*/__manifest__.py")) if repo_dir.is_dir() else []
        for mf in modules:
            try:
                data = ast.literal_eval(mf.read_text(encoding="utf-8"))
                version = str(data.get("version", "")) if isinstance(data, dict) else ""
            except (OSError, ValueError, SyntaxError, UnicodeDecodeError):
                version = ""
            parts = version.split(".")
            series = ".".join(parts[:2]) if len(parts) >= 5 else "unknown"
            series_seen[series] = series_seen.get(series, 0) + 1
        repos.append(
            {
                "repo": repo,
                "vendored": repo_dir.is_dir(),
                "pin": pins.get(repo),
                "modules_vendored": len(modules),
                "vendored_series": series_seen,
                "v20_status": "UNMEASURED",
                "v20_reason": V20_UNMEASURED_REASON,
            }
        )
    vendored_on_v20 = sum(1 for r in repos if r["vendored_series"].get("20.0"))
    matrix = {
        "total_repositories_evaluated": len(repos),
        "baseline_series": odoo_series,
        "vendored_on_v20_count": vendored_on_v20,
        "status_breakdown": {"UNMEASURED": len(repos)},
        "threshold_required": D025_THRESHOLD,
        "migrated_count": None,
        "threshold_met": None,
        "d025_revisit_trigger_active": None,
        "strategic_recommendation": "UNDETERMINED - upstream v20 availability not measured",
        "repositories": repos,
    }
    check = _check(
        "oca_v20_availability",
        "UNMEASURED",
        f"{len(repos)} repositories: {V20_UNMEASURED_REASON}; D-025 section 5 trigger "
        f"(>= {D025_THRESHOLD} migrated) cannot be evaluated",
    )
    return matrix, check


def main() -> int:
    print("Starting Fork Audit & OCA v20 Availability Matrix Evaluation (R07-M02-T02)...")
    lock = read_versions_lock()
    odoo_series = read_odoo_series()

    fork_res, checks = run_fork_audit(odoo_series, lock)
    oca_res, v20_check = evaluate_oca_v20_matrix(odoo_series, lock)
    checks.append(v20_check)

    for c in checks:
        print(f"  [{c['status']}] {c['check']}: {c['detail']}")
    print(
        f"  OCA v20 matrix: {oca_res['total_repositories_evaluated']} repositories, "
        f"vendored series {odoo_series}, upstream v20 availability UNMEASURED"
    )

    statuses = [c["status"] for c in checks]
    verdict = overall_verdict(statuses)
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    out_file = EVIDENCE_DIR / EVIDENCE_NAME
    evidence_payload = {
        "test": "R07-M02-T02: Fork Audit & OCA v20 Availability Matrix Assessment",
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "verdict": verdict,
        "checks": checks,
        "fork_audit": fork_res,
        "oca_matrix": oca_res,
    }
    out_file.write_bytes(json.dumps(evidence_payload, indent=2).encode("utf-8"))
    print(f"  Evidence published: {out_file}")
    print(
        f"verify_fork_and_oca_matrix: {verdict} - {statuses.count('PASS')}/{len(statuses)} "
        "checks passed"
    )
    return EXIT_CODES.get(verdict, 2)


if __name__ == "__main__":
    sys.exit(main())
