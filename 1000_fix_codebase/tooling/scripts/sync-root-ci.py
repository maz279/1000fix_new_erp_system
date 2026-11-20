#!/usr/bin/env python3
"""sync-root-ci — publish the CI pipeline where GitHub runs it.

The canonical pipeline is 1000_fix_codebase/.github/workflows/ci.yml (the
G0b/G2/G9 gates and audit-repo-formats check it there). GitHub, however, only
runs workflows from .github/workflows/ at the ROOT of the repository, so that
file never ran. This script writes the root copy, adapted to run from the
codebase directory:

- a top-level `defaults.run.working-directory: 1000_fix_codebase`
- explicit `working-directory:` values re-rooted under 1000_fix_codebase/

Edit the canonical file, then run (from the repository root or anywhere):

    python 1000_fix_codebase/tooling/scripts/sync-root-ci.py           # write
    python 1000_fix_codebase/tooling/scripts/sync-root-ci.py --check   # exit 1 on drift
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

CODEBASE = Path(__file__).resolve().parents[2]
REPO_ROOT = CODEBASE.parent
SOURCE = CODEBASE / ".github" / "workflows" / "ci.yml"
TARGET = REPO_ROOT / ".github" / "workflows" / "ci.yml"
SUBDIR = CODEBASE.name

HEADER = (
    "# =============================================================================\n"
    f"# GENERATED from {SUBDIR}/.github/workflows/ci.yml by\n"
    f"# {SUBDIR}/tooling/scripts/sync-root-ci.py - do not edit here; edit the\n"
    "# canonical file and re-run the script. GitHub runs workflows only from the\n"
    "# repository root, so this copy is the one that executes.\n"
    "# =============================================================================\n"
)


def render(src: str) -> str:
    if "\njobs:\n" not in src:
        raise SystemExit("canonical ci.yml has no top-level 'jobs:' key")
    if re.search(r"^defaults:", src, re.M):
        raise SystemExit("canonical ci.yml already declares top-level defaults; merge by hand")
    out = src.replace(
        "\njobs:\n",
        f"\ndefaults:\n  run:\n    working-directory: {SUBDIR}   # the codebase lives in a subdirectory\n\njobs:\n",
        1)
    out = re.sub(r"(working-directory: )(?!" + re.escape(SUBDIR) + r")(\S+)",
                 lambda m: f"{m.group(1)}{SUBDIR}/{m.group(2)}", out)
    # the defaults line itself must keep the bare subdirectory
    out = out.replace(f"working-directory: {SUBDIR}/{SUBDIR}", f"working-directory: {SUBDIR}")
    return HEADER + out


def main() -> int:
    wanted = render(SOURCE.read_text(encoding="utf-8"))
    current = TARGET.read_text(encoding="utf-8") if TARGET.exists() else None
    if current == wanted:
        print(f"sync-root-ci: OK - {TARGET.relative_to(REPO_ROOT)} matches the canonical pipeline")
        return 0
    if "--check" in sys.argv:
        print(f"sync-root-ci: DRIFT - run python {SUBDIR}/tooling/scripts/sync-root-ci.py")
        return 1
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(wanted, encoding="utf-8", newline="\n")
    print(f"sync-root-ci: wrote {TARGET.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
