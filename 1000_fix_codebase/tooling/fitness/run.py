#!/usr/bin/env python3
"""Fitness runner (P02-M08-T07/T08): runs the registry, emits RN-01..RN-04
normalised results per check - "the gates are enabled" becomes a measurable
estate property, not a claim.

Security: script paths come from the repo-controlled registry and are
validated to resolve INSIDE tooling/ before execution; subprocess is invoked
with shell=False and a fixed argument list - no string concatenation into a
shell, ever.

Checks whose script is not yet present report SKIP with a remedy (a missing
check is visible, never silent). Until Phase 3 code lands, SKIP-visibility
is the honest state and the runner exits 0.
"""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
TOOLING_ROOT = (REPO_ROOT / "tooling").resolve()

ALLOWED_SUFFIXES = {".py", ".sh", ".ps1"}


def parse_registry() -> list[dict]:
    # Minimal reader for our own flat registry (no PyYAML dependency).
    checks: list[dict] = []
    cur: dict | None = None
    for raw in (HERE / "registry.yaml").read_text(encoding="utf-8").splitlines():
        if raw.startswith("  - id: "):
            if cur:
                checks.append(cur)
            cur = {"id": raw.split(":", 1)[1].strip()}
        elif cur is not None and raw.startswith("    ") and ":" in raw:
            k, v = raw.strip().split(":", 1)
            v = v.split("#")[0].strip()
            cur[k.strip()] = v
    if cur:
        checks.append(cur)
    return checks


def safe_script_path(script: str) -> Path | None:
    """Resolve a registry script to a path strictly inside tooling/."""
    candidates = [
        (HERE / script).resolve(),
        (TOOLING_ROOT / "scripts" / script).resolve(),
        (TOOLING_ROOT / script).resolve(),
    ]
    for candidate in candidates:
        try:
            candidate.relative_to(TOOLING_ROOT)
        except ValueError:
            continue
        if candidate.suffix in ALLOWED_SUFFIXES and candidate.is_file():
            return candidate
    return None


def build_command(script: str) -> list[str] | None:
    """Fixed argument lists only - never a shell string."""
    sp = safe_script_path(script)
    if sp is None:
        return None
    if sp.suffix == ".py":
        return [sys.executable, str(sp)]
    if sp.suffix == ".sh":
        git_bash = Path(r"C:\Program Files\Git\bin\bash.exe")
        if sys.platform == "win32" and git_bash.is_file():
            return [str(git_bash), str(sp)]
        return ["bash", str(sp)]
    return ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(sp)]


def result(suite: str, case: str, status: str, verifies: str, ms: float, remedy: str = "") -> dict:
    return {
        "suite": suite, "case": case, "status": status,
        "duration_ms": round(ms), "verifies": verifies,
        "artefacts": [], "message": "", "remedy": remedy,
        "ran_at_utc": datetime.now(timezone.utc).isoformat(),
    }


def main() -> int:
    results: list[dict] = []
    failures = 0
    for chk in parse_registry():
        cid, script = chk.get("id"), chk.get("script", "")
        enabled = chk.get("enabled", "true") != "false"
        blocking = chk.get("blocking", "false") == "true"
        if not script:
            results.append(result(cid, "registry", "FAIL", cid, 0, "registry entry has no script"))
            failures += 1
            continue
        if not enabled:
            msg = f"built, disabled; promotes at {chk.get('promote_to_blocking_at', 'gate')} (FG-04)"
            results.append(result(cid, "disabled-by-design", "SKIP", cid, 0, msg))
            print(f"[SKIP] {cid}: disabled-by-design - {msg}")
            continue
        cmd = build_command(script)
        if cmd is None:
            results.append(result(cid, "runner", "SKIP", cid, 0,
                                   f"check script not present/allowed under tooling/: {script} (visible, never silent)"))
            print(f"[SKIP] {cid}: script missing ({script}) - Phase 3 lands it with the code it checks")
            continue
        t0 = datetime.now()
        proc = subprocess.run(cmd, capture_output=True, text=True, shell=False, cwd=REPO_ROOT,
                              timeout=600, check=False)
        ms = (datetime.now() - t0).total_seconds() * 1000
        status = "PASS" if proc.returncode == 0 else ("FAIL" if blocking else "WARN")
        if status == "FAIL":
            failures += 1
        tail = (proc.stdout + proc.stderr).strip().splitlines()
        results.append(result(cid, script, status, cid, ms, tail[-1] if tail else ""))
        print(f"[{status}] {cid} ({ms:.0f} ms)")

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = HERE / "evidence" / f"fitness-{stamp}.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps({"schema": "1000fix-erp/fitness-results/1", "results": results},
                              indent=2), encoding="utf-8")
    print(f"\nfitness: {failures} failure(s); results -> {out.relative_to(REPO_ROOT)}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
