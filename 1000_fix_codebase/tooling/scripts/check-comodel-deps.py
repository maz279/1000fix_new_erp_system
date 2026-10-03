# check-comodel-deps.py - P07 runtime bring-up finding.
#
# Odoo asserts at registry load that every relational FIELD's comodel is
# present. A comodel defined by a module that is NOT in the referring
# module's transitive depends crashes install with "unknown comodel_name".
# The static registry check whitelisted external models, so these ordering
# bugs only surfaced on the first real `odoo-bin -i`.
#
# This check maps every fix.* comodel to its defining module and verifies
# the referring module's depends closure covers it. OCA/odoo core comodels
# (operating.unit, res.*, hr.*, product.*) are checked against the vendor
# trees so platform-layer references to app models (hr.employee) are caught.
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ADDONS = REPO / "addons"
VENDOR = REPO / "vendor"

FIELD_RE = re.compile(
    r"fields\.(?:Many2one|One2many|Many2many)\(\s*[\"']([a-z0-9_.]+)[\"']")
NAME_RE = re.compile(r"_name\s*=\s*[\"']([a-z0-9_.]+)[\"']")


def module_tech_dir(mod: Path) -> str:
    return mod.name  # cd_party_master


def load_defining_modules() -> dict[str, set[str]]:
    """model name -> set of modules that DEFINE it (declare _name)."""
    defines: dict[str, set[str]] = {}
    # Odoo 19 moved the base module INTO the odoo package (odoo/addons/base)
    roots = [VENDOR / "odoo" / "addons", VENDOR / "odoo" / "odoo" / "addons"]
    oca = VENDOR / "oca"
    if oca.exists():
        roots += [d for d in oca.iterdir() if d.is_dir()]
    # first-party: platform + every domain category
    roots.append(ADDONS / "platform")
    if (ADDONS / "domain").exists():
        roots += [d for d in (ADDONS / "domain").iterdir() if d.is_dir()]
    for root in roots:
        if not root.exists():
            continue
        for mod in root.iterdir():
            if not (mod / "__manifest__.py").exists():
                continue
            for py in (mod / "models").rglob("*.py"):
                text = py.read_text(encoding="utf-8", errors="replace")
                for name in NAME_RE.findall(text):
                    defines.setdefault(name, set()).add(module_tech_dir(mod))
    return defines


def load_manifest_closure() -> tuple[dict[str, set[str]], dict[str, set[str]]]:
    """tech name -> direct depends; plus reverse map for first-party."""
    manifest_dirs: dict[str, Path] = {}
    for root in [ADDONS / "platform"] + [
        d for d in (ADDONS / "domain").iterdir() if d.is_dir()
    ]:
        for mod in root.iterdir():
            if (mod / "__manifest__.py").exists():
                manifest_dirs[mod.name] = mod
    # vendor manifests (name -> dir) for closure resolution; Odoo 19 moved the
    # base module INTO the odoo package (odoo/addons/base)
    vendor_roots = [VENDOR / "odoo" / "addons", VENDOR / "odoo" / "odoo" / "addons"]
    if (VENDOR / "oca").exists():
        vendor_roots += [d for d in (VENDOR / "oca").iterdir() if d.is_dir()]
    vendor_dirs: dict[str, Path] = {}
    for root in vendor_roots:
        for mod in root.iterdir():
            if (mod / "__manifest__.py").exists():
                vendor_dirs[mod.name] = mod

    deps: dict[str, set[str]] = {}
    for name, mod in {**vendor_dirs, **manifest_dirs}.items():
        try:
            mt = (mod / "__manifest__.py").read_text(encoding="utf-8")
            found = re.search(r"[\"']depends[\"']\s*:\s*\[(.*?)\]", mt, re.S)
            deps[name] = set(re.findall(r"[\"']([A-Za-z0-9_.]+)[\"']", found.group(1))) if found else set()
        except Exception:
            deps[name] = set()
    return deps, manifest_dirs


def closure(start: str, deps: dict[str, set[str]]) -> set[str]:
    seen: set[str] = set()
    stack = list(deps.get(start, ()))
    while stack:
        cur = stack.pop()
        if cur in seen:
            continue
        seen.add(cur)
        stack.extend(deps.get(cur, ()))
    return seen


def main() -> int:
    defines = load_defining_modules()
    deps, manifest_dirs = load_manifest_closure()
    failures = 0
    for tech, mod_dir in sorted(manifest_dirs.items()):
        clo = closure(tech, deps)
        for py in (mod_dir / "models").rglob("*.py"):
            text = py.read_text(encoding="utf-8", errors="replace")
            for comodel in FIELD_RE.findall(text):
                owners = defines.get(comodel)
                if not owners:
                    print(f"[FAIL] {tech}: {py.name} references {comodel} - defined NOWHERE in addons or vendor")
                    failures += 1
                    continue
                # same-module references are registry-safe (Odoo loads a
                # module's models together)
                if tech in owners:
                    continue
                if not (owners & clo):
                    where = ",".join(sorted(owners))
                    print(f"[FAIL] {tech}: {py.name} field comodel {comodel} (defined by {where}) "
                          f"not in depends closure")
                    failures += 1
    if failures:
        print(f"check-comodel-deps: {failures} violation(s)")
        return 1
    print("check-comodel-deps: OK - every relational field comodel is in its module's depends closure")
    return 0


if __name__ == "__main__":
    sys.exit(main())
