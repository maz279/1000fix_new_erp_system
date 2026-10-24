#!/usr/bin/env python3
"""check_manifest_depends - FF-46 clean-install dependency closure.

Every model a first-party addon references (Many2one/One2many/Many2many
comodel, or _inherit) must be defined by a module in that addon's DECLARED
dependency closure. Otherwise the addon only works in a database where the
provider happens to be installed already, and a clean install fails at
registry load (R01 re-audit 2026-10-22: cd_gl_ext -> account.fiscal.year
broke `odoo-bin -i <all cd_*>` on a fresh database).

Exit 0 clean - 1 undeclared dependencies (remedy printed).
"""

from __future__ import annotations

import ast
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
MANIFEST_GLOBS = (
    "addons/**/__manifest__.py",
    "vendor/oca/*/*/__manifest__.py",
    "vendor/odoo/addons/*/__manifest__.py",
    "vendor/odoo/odoo/addons/*/__manifest__.py",
)
COMODEL = re.compile(
    r"fields\.(?:Many2one|One2many|Many2many)\(\s*(?:comodel_name\s*=\s*)?[\"']([\w.]+)[\"']"
)
INHERIT = re.compile(r"_inherit\s*=\s*\[?([^\]\n]+)")
NAME = re.compile(r"^\s+_name\s*=\s*[\"']([\w.]+)[\"']", re.M)


def main() -> int:
    manifests: dict[str, tuple[pathlib.Path, list[str]]] = {}
    for pattern in MANIFEST_GLOBS:
        for mf in ROOT.glob(pattern):
            try:
                deps = ast.literal_eval(mf.read_text(encoding="utf-8")).get("depends", [])
            except (ValueError, SyntaxError):
                continue
            manifests[mf.parent.name] = (mf.parent, [d for d in deps if isinstance(d, str)])

    defined_by: dict[str, set[str]] = {}
    for module, (path, _) in manifests.items():
        for py in path.rglob("*.py"):
            for model in NAME.findall(py.read_text(encoding="utf-8", errors="replace")):
                defined_by.setdefault(model, set()).add(module)

    def closure(module: str, seen: set[str]) -> set[str]:
        if module in seen or module not in manifests:
            return seen
        seen.add(module)
        for dep in manifests[module][1]:
            closure(dep, seen)
        return seen

    problems: set[tuple[str, str, str]] = set()
    for module, (path, _) in manifests.items():
        if path.relative_to(ROOT).parts[0] != "addons":
            continue
        reachable = closure(module, set()) | {"base"}
        for py in path.rglob("*.py"):
            if "tests" in py.parts:
                continue
            text = py.read_text(encoding="utf-8", errors="replace")
            refs = set(COMODEL.findall(text))
            for group in INHERIT.findall(text):
                refs.update(re.findall(r"[\"']([\w.]+)[\"']", group))
            for model in refs:
                providers = defined_by.get(model, set())
                if providers and not providers & reachable:
                    problems.add((module, model, ", ".join(sorted(providers))))

    if problems:
        print("check_manifest_depends: FAIL - models used without a declared dependency:")
        for module, model, providers in sorted(problems):
            print(f"  {module}: uses {model} (defined by {providers})")
        print("  remedy: add the providing module to 'depends' in the addon's __manifest__.py")
        return 1
    print(
        f"check_manifest_depends: OK - {len(manifests)} manifests, every referenced model reachable"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
