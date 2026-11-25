#!/usr/bin/env python3
"""check-cd-id - FF-16 (P02-M08-T06): CD identifier form AND membership.

A regex-only check passes CD-M99-42, which is well-formed and denotes
nothing. This check resolves every CD- reference in changed files against
tooling/cd-register.yaml (BE-005 section 6).

Enablement (BE-005 section 10): WARNING from the first CI build, promoted to
BLOCKING at the G1 gate. Exit code: 0 ok / 1 violations / 2 misconfigured.
In Warning mode violations exit 0 with [WARN] lines so the pipeline records
them without blocking (promotion flips a single flag below).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
REGISTER = REPO_ROOT / "tooling" / "cd-register.yaml"
CD_RE = re.compile(r"\bCD-[A-Z0-9]{1,4}-\d{1,3}\b")

# G1 promotion flag - set by CI after the gate record (P02-M05-T08 plan).
BLOCKING = (REPO_ROOT / "tooling" / "fitness" / "FF16_BLOCKING").exists()


def load_register() -> set[str]:
    if not REGISTER.exists():
        print("check-cd-id: FAIL - cd-register.yaml missing (run generate-cd-register.ps1)")
        sys.exit(2)
    ids: set[str] = set()
    for line in REGISTER.read_text(encoding="utf-8").splitlines():
        m = re.search(r"^- id: (CD-\S+)", line)
        if m:
            ids.add(m.group(1))
    if not ids:
        print("check-cd-id: FAIL - register parsed empty")
        sys.exit(2)
    return ids


def main(argv: list[str]) -> int:
    registered = load_register()
    files = argv[1:] or []
    # Exemptions: the register itself, its generator output, vendored code,
    # and this checker.
    exempt = (
        "tooling/cd-register.yaml",
        "tooling/generators/",
        "vendor/",
        "tooling/scripts/check-cd-id.py",
    )
    violations: list[tuple[str, str]] = []
    for f in files:
        f = f.replace("\\", "/")
        if any(f.startswith(e) or Path(f).name == Path(e).name for e in exempt):
            continue
        p = Path(REPO_ROOT, f)
        if not p.exists() or p.is_dir():
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, IsADirectoryError):
            continue
        for ref in CD_RE.findall(text):
            if ref not in registered:
                violations.append((f, ref))
    if not violations:
        print(
            f"check-cd-id: OK - all CD references resolve in the register ({len(registered)} items)"
        )
        return 0
    mode = "FAIL" if BLOCKING else "WARN"
    for f, ref in violations:
        print(f"check-cd-id: [{mode}] {f}: {ref!r} is not a BE-005 section 6 item (CDR-08)")
    print("  remedy: use a registered identifier (tooling/cd-register.yaml), or issue the")
    print("          new item through BE-005 change control first.")
    return 1 if BLOCKING else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
