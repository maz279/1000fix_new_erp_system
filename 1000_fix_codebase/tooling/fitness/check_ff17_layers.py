#!/usr/bin/env python3
"""FF-17 — Layer discipline check (P03-M01-T04, blocking).

AR-007 layer rule: a platform module (addons/platform/) may NEVER depend on
a domain module (addons/domain/). This check reads every manifest under
addons/platform/ and fails if any `depends` entry resolves to addons/domain/.

Also checks DL-04 (every depends entry is used): a platform manifest whose
depends list includes a module that provides no importable symbol used in
that module is flagged as a WARNING (DL-04 review item, not auto-removed).

Exit: 0 pass / 1 layer violation (blocking) / warnings printed but exit 0.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PLATFORM = REPO_ROOT / "addons" / "platform"
DOMAIN = REPO_ROOT / "addons" / "domain"

# Known domain module names (populated by scanning addons/domain/)
DOMAIN_MODULES: set[str] = set()


def scan_domain_modules() -> set[str]:
    """Collect all technical names from addons/domain/**/__manifest__.py."""
    names: set[str] = set()
    if not DOMAIN.exists():
        return names
    for mf in DOMAIN.rglob("__manifest__.py"):
        text = mf.read_text(encoding="utf-8")
        m = re.search(r'"name"\s*:\s*"([^"]+)"', text)
        if m:
            names.add(m.group(1).lower().replace(" ", "_"))
    return names


def get_depends(manifest_path: Path) -> list[str]:
    """Extract the depends list from a manifest."""
    text = manifest_path.read_text(encoding="utf-8")
    m = re.search(r'"depends"\s*:\s*\[(.*?)\]', text, re.DOTALL)
    if not m:
        return []
    return re.findall(r'"([^"]+)"', m.group(1))


def main() -> int:
    global DOMAIN_MODULES
    DOMAIN_MODULES = scan_domain_modules()

    if not PLATFORM.exists():
        print("FF-17: SKIP - addons/platform/ not present yet")
        return 0

    violations: list[tuple[str, str]] = []
    warnings: list[tuple[str, str]] = []
    checked = 0

    for mf in sorted(PLATFORM.rglob("__manifest__.py")):
        module_dir = mf.parent.name
        depends = get_depends(mf)
        checked += 1
        for dep in depends:
            if dep in DOMAIN_MODULES:
                violations.append((module_dir, dep))
            # DL-04 heuristic: base/mail/web are always "used"; specific
            # cd_* deps that appear only once in the manifest text are suspect
            if dep.startswith("cd_") and dep != f"cd_{module_dir.replace('cd_', '')}":
                text = mf.read_text(encoding="utf-8")
                # if the dep appears only in the depends line (not in any
                # description, demo, or data file), flag as possibly unused
                count_outside = len(re.findall(re.escape(dep), text)) - 1
                if count_outside == 0:
                    # check if any data file references it
                    data_files = list(mf.parent.rglob("*.xml"))
                    referenced = any(dep in f.read_text(encoding="utf-8", errors="ignore")
                                     for f in data_files)
                    if not referenced:
                        warnings.append((module_dir, f"depends on {dep} but no XML references it (DL-04: every depends entry is used)"))

    if violations:
        print(f"FF-17: FAIL - {len(violations)} layer violation(s) (platform -> domain):")
        for module, dep in violations:
            print(f"  {module} depends on domain module {dep!r}")
        print("  remedy: platform modules NEVER depend on domain modules (AR-007 DL-01/FF-17).")
        print("          Move the shared concept to addons/platform/ or extract a library.")
        return 1

    if warnings:
        for module, msg in warnings:
            print(f"FF-17: WARN - {module}: {msg}")

    print(f"FF-17: OK - {checked} platform manifest(s) checked, 0 layer violations")
    return 0


if __name__ == "__main__":
    sys.exit(main())
