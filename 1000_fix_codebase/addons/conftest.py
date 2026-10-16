# addons/conftest.py - P07 verification harness.
#
# The module test suites import real model classes
# (from odoo.addons.cd_x.models... import FixX). Importing an Odoo addon
# requires Odoo's module machinery to have initialised its addons path;
# plain pytest cannot do that by itself, so this conftest bootstraps it at
# collection time: configure addons_path, initialise sys.path, then load
# every first-party module IN DEPENDENCY ORDER (cross-addon imports such as
# cd_ap_ext -> cd_tax_engine_bd.models require the dependency to be loaded
# first). No database is needed - model classes are built at import.
from __future__ import annotations

import sys
from pathlib import Path

CODE_ROOT = Path(__file__).resolve().parents[1]
for p in (str(CODE_ROOT), str(CODE_ROOT / "vendor" / "odoo")):
    if p not in sys.path:
        sys.path.insert(0, p)

import odoo  # noqa: E402
from odoo.modules.module import initialize_sys_path, load_openerp_module  # noqa: E402

# Reuse the canonical addons_path builder (REPO-15: single source). The
# generator file has a hyphenated name, so it is loaded by path.
import importlib.util  # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "generate_odoo_conf", CODE_ROOT / "tooling" / "scripts" / "generate-odoo-conf.py")
_gen = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_gen)
build_addons_path = _gen.build_addons_path

odoo.tools.config["addons_path"] = [
    str((CODE_ROOT / part).resolve()) for part in build_addons_path().split(",")]
initialize_sys_path()


def _load_order():
    """First-party module names in manifest-dependency order."""
    import re
    deps: dict[str, set[str]] = {}
    for mf in CODE_ROOT.glob("addons/**/__manifest__.py"):
        text = mf.read_text(encoding="utf-8", errors="replace")
        found = re.search(r"[\"']depends[\"']\s*:\s*\[(.*?)\]", text, re.S)
        deps[mf.parent.name] = set(
            re.findall(r"[\"']([A-Za-z0-9_.]+)[\"']", found.group(1))) if found else set()
    order: list[str] = []
    seen: set[str] = set()

    def visit(name: str) -> None:
        if name in seen:
            return
        seen.add(name)
        for dep in sorted(deps.get(name, ())):
            if dep in deps:
                visit(dep)
        order.append(name)

    for name in sorted(deps):
        visit(name)
    return order


_loaded = 0
for _mod in _load_order():
    load_openerp_module(_mod)
    _loaded += 1

# Some collectors/tools address the addons by their bare module name
# (import_module('cd_catalogue')) or under importlib relative path
# ('addons.platform.cd_event_outbox'); without an alias that re-EXECUTES the
# package under a non-odoo.addons name and Odoo's metaclass rejects the
# model classes. Aliasing makes every such import a sys.modules cache hit.
_mod_prefixes: dict[str, str] = {}
for _mf in CODE_ROOT.glob("addons/**/__manifest__.py"):
    _mod_prefixes[_mf.parent.name] = _mf.parent.relative_to(CODE_ROOT).as_posix().replace("/", ".")

for _name in list(sys.modules):
    if _name.startswith("odoo.addons.cd_"):
        _mod_part = _name[len("odoo.addons."):].split(".", 1)[0]
        _sub = _name[len(f"odoo.addons.{_mod_part}"):]
        _alias = _name[len("odoo.addons."):]
        sys.modules.setdefault(_alias, sys.modules[_name])
        if _mod_part in _mod_prefixes:
            _rel_alias = f"{_mod_prefixes[_mod_part]}{_sub}"
            sys.modules.setdefault(_rel_alias, sys.modules[_name])
print(f"conftest: {_loaded} first-party odoo modules loaded for test collection")
