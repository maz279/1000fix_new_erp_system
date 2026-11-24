#!/usr/bin/env python3
"""run-mypy - the PYS-07/10/11 type gate (ci.yml stage 2) in one command.

R01 re-audit 2026-10-22: the stage ran `mypy --strict addons services libs`,
which never got past start-up ("corporate-sso is not a valid Python package
name"): services/ live in hyphenated folders and several of them own a
top-level `src` package, so they cannot share one mypy run. This runner
checks libs/ + addons/ in one run (configuration: pyproject [tool.mypy],
strict) and then every service in its own run, rooted at the service folder.
Addons migration scripts (version-dotted, unimportable dirs) are excluded from
the bulk addons run and checked one file per run, so the duplicate-module
start-up failure cannot block the gate and no script escapes it.

Usage: python tooling/ci/run-mypy.py [--only libs|addons|services|<service>]
       (run with the locked mypy: `uv run python tooling/ci/run-mypy.py`)
Exit 0 clean - 1 type errors - 2 mypy could not run.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "pyproject.toml"


def service_sources(service: Path) -> list[str]:
    """Product + test sources of one service, relative to the service root."""
    return sorted(
        p.relative_to(service).as_posix()
        for p in service.rglob("*.py")
        if not {"node_modules", "__pycache__", ".venv"} & set(p.parts)
    )


def run(args: list[str], cwd: Path, label: str) -> int:
    proc = subprocess.run(
        [sys.executable, "-m", "mypy", "--config-file", str(CONFIG), *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )
    out = (proc.stdout + proc.stderr).strip()
    last = out.splitlines()[-1] if out else "no output"
    # A config or start-up error can also exit 1/2: a real result always ends
    # with mypy's own summary line.
    if proc.returncode not in (0, 1) or not last.startswith(("Success:", "Found ")):
        print(f"run-mypy: {label}: MYPY FAILED TO RUN (exit {proc.returncode})\n{out}")
        return 2
    if proc.returncode == 1:
        print(out)
    print(f"run-mypy: {label}: {last}")
    return proc.returncode


def migration_scripts() -> list[Path]:
    """Odoo migration scripts live in version-dotted dirs (19.0.1.1.0) that can
    never be Python packages, so 27 post-migrate.py / 12 pre-migrate.py files
    all map to the same module name and a single mypy run dies at start-up
    ("Duplicate module named post-migrate"). They are checked one file per run
    instead - same strict config, nothing escapes the gate."""
    return sorted(p for p in (ROOT / "addons").rglob("*.py") if "migrations" in p.parts)


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    only = args[args.index("--only") + 1] if "--only" in args[:-1] else None
    results: list[int] = []
    for tree in ("libs", "addons"):
        if only in (None, tree):
            if tree == "addons":
                results.append(run(["--exclude", "/migrations/", "addons"], ROOT, tree))
                for mig in migration_scripts():
                    rel = mig.relative_to(ROOT).as_posix()
                    results.append(run([rel], ROOT, f"addons-migration:{rel}"))
            else:
                results.append(run([tree], ROOT, tree))
    for service in sorted(p for p in (ROOT / "services").iterdir() if p.is_dir()):
        if only not in (None, "services", service.name):
            continue
        sources = service_sources(service)
        if sources:
            results.append(run(sources, service, f"services/{service.name}"))
    if not results:
        print(f"run-mypy: nothing selected by --only {only!r}")
        return 2
    worst = 2 if 2 in results else (1 if 1 in results else 0)
    print(f"run-mypy: {'PASS' if worst == 0 else 'FAIL'} - {len(results)} run(s)")
    return worst


if __name__ == "__main__":
    sys.exit(main())
