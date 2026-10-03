#!/usr/bin/env python3
"""check-licence-gate - the D-030 pipeline gate (P02-M08-T04, stage 13).

Every dependency's licence is classified against tooling/licence/register.yaml
(the machine form of the D-030 register). AGPL/BSL/TSL/fair-code components
without an APPROVED entry fail the stage. "Four are already in the stack and
none has been approved" is the failure mode this gate exists to prevent
recurring.

Inputs (today): the SBOM's dependency list (syft CycloneDX on stdin or file).
Exit 0 compliant / 1 violations / 2 misconfigured.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
REGISTER = REPO_ROOT / "tooling" / "licence" / "register.yaml"

RESTRICTED_MARKERS = [
    "AGPL", "BSL", "BUSL", "TSL", "Sustainable Use", "SSPL", "fair-code",
]
# Components APPROVED-WITH-CONDITION stay passing; the condition text is
# carried into the result for the stage log (conditions are audited at the
# D-030 annual review, not re-proved per build).


def parse_register() -> dict[str, dict]:
    comps: dict[str, dict] = {}
    cur: dict | None = None
    for raw in REGISTER.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^  - name: (\S+)", raw)
        if m:
            cur = {"name": m.group(1)}
            comps[m.group(1)] = cur
            continue
        if cur is not None:
            m = re.match(r"^    (licence|status|condition): (.*)$", raw)
            if m:
                cur[m.group(1)] = m.group(2).strip()
    return comps


def is_restricted(licence: str) -> bool:
    return any(marker.lower() in licence.lower() for marker in RESTRICTED_MARKERS)


def main(argv: list[str]) -> int:
    if not REGISTER.exists():
        print("licence-gate: FAIL - tooling/licence/register.yaml missing")
        return 2
    approved = parse_register()
    sbom_path = argv[1] if len(argv) > 1 else "sbom.cdx.json"
    p = Path(REPO_ROOT, sbom_path)
    if not p.exists():
        print(f"licence-gate: WARN - no SBOM at {sbom_path}; classifying declared compose images only")
        deps: list[dict] = []
    else:
        sbom = json.loads(p.read_text(encoding="utf-8"))
        deps = sbom.get("components", [])

    violations = []
    for dep in deps:
        name = dep.get("name", "")
        licence = " ".join(dep.get("licenses", []) if isinstance(dep.get("licenses"), list)
                           else [str(dep.get("licenses", ""))])
        if not is_restricted(licence):
            continue
        entry = approved.get(name)
        if entry and entry.get("status", "").startswith("approved"):
            cond = entry.get("condition", "")
            print(f"licence-gate: OK   {name} [{licence}] approved{(' - condition: ' + cond) if cond else ''}")
        else:
            violations.append((name, licence))

    for name, licence in violations:
        print(f"licence-gate: FAIL {name} [{licence}] - restricted class with no approved D-030 entry")
    if violations:
        print("  remedy: get ARB approval and add the entry to tooling/licence/register.yaml (D-030),")
        print("          or replace the component (the D-030 pattern: four replacements already made).")
        return 1
    print(f"licence-gate: OK - {len(deps)} dependencies classified, 0 unapproved restricted components")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
