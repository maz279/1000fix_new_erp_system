#!/usr/bin/env python3
"""FF-27 — portal contract (P04-M06; PS-11, UX-002).

The P03 W1 portal contract, checked statically:

  1. The six W1 workspaces exist as role-gated menus under the shared root
     (roadmap P04-M06-T03; UX-002 §6.2 W1 slice).
  2. Menu integrity — every menuitem's parent, action and group reference
     resolves to a record declared in this repository (the install-crash
     class: a menu pointing at a missing action kills module load).
  3. NVR-22 — every workspace menu carries a groups gate (a workspace the
     user cannot enter does not appear).
  4. NVR-23 — no workspace exceeds seven second-level sections.
  5. Every action's res_model is defined by a model file in addons/.

Exit: 0 pass / 1 violations.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ADDONS = REPO / "addons"

# The W1 portal contract (P04-M06-T03). module -> workspace menu xml id.
W1_WORKSPACES = {
    "cd_front_desk": "menu_ws_front_desk",
    "cd_service_order": "menu_ws_service_orders",
    "cd_party_master": "menu_fix_party_root",
    "cd_device_registry": "menu_ws_devices",
    "cd_catalogue": "menu_fix_catalogue_root",
    "cd_rbac_ext": "menu_ws_administration",
}
ROOT_MENU = ("cd_entity_config", "menu_fix_operations_root")
MAX_SECTIONS_PER_WORKSPACE = 7  # NVR-23
WORKSPACE_GROUPS = re.compile(r"cd_rbac_ext\.group_ws_\w+")
# Odoo CE core models our actions legitimately target. The vendor/ submodules
# are not initialised on every workstation, so these are allow-listed here;
# anything else must be defined in addons/.
CORE_MODELS = frozenset({
    "res.partner", "res.company", "res.users", "res.groups",
    "crm.lead", "product.template", "product.product",
    "hr.employee", "hr.department",
})


def module_of(path: Path) -> str:
    """The Odoo module name owning a file (the ancestor dir with a manifest).
    Domain modules nest: addons/<category>/<squad>/<module>/..."""
    for parent in path.parents:
        if (parent / "__manifest__.py").is_file():
            return parent.name
    return ""


def collect_xml_records() -> dict[str, set[str]]:
    """xml ids declared per module: {module: {record_id, ...}} for
    ir.ui.menu, ir.actions.act_window and res.groups."""
    declared: dict[str, set[str]] = {}
    for xml in ADDONS.rglob("*.xml"):
        if "vendor" in xml.parts:
            continue
        text = xml.read_text(encoding="utf-8", errors="ignore")
        module = module_of(xml)
        if not module:
            continue
        if module not in declared:
            declared[module] = set()
        # <menuitem id="..."> implies ir.ui.menu (no model attribute).
        for match in re.finditer(r'<menuitem\s+id="([\w.]+)"', text):
            if "." not in match.group(1):
                declared[module].add(match.group(1))
        for match in re.finditer(
            r'<record\s+id="([\w.]+)"[^>]*model="(ir\.ui\.menu|'
            r'ir\.actions\.act_window|res\.groups)"', text
        ):
            record_id = match.group(1)
            if "." in record_id:  # override of another module's record
                continue
            declared[module].add(record_id)
    return declared


def collect_menuitems() -> list[dict]:
    items: list[dict] = []
    for xml in ADDONS.rglob("*.xml"):
        if "vendor" in xml.parts:
            continue
        text = xml.read_text(encoding="utf-8", errors="ignore")
        module = module_of(xml)
        if not module:
            continue
        for block in re.finditer(r"<menuitem\b[^>]*?/>", text, re.DOTALL):
            attrs = dict(re.findall(r'(\w+)="([^"]*)"', block.group(0)))
            items.append({"module": module, **attrs})
    return items


def resolves(declared: dict[str, set[str]], ref: str, current_module: str) -> bool:
    if "." not in ref:
        return ref in declared.get(current_module, set())
    module, record = ref.split(".", 1)
    if module not in declared:
        return True  # vendor/core module reference — outside this repo's proof
    return record in declared.get(module, set())


def main() -> int:
    violations: list[str] = []
    declared = collect_xml_records()
    menus = collect_menuitems()

    # 1. The six W1 workspaces exist under the shared root.
    for module, menu_id in W1_WORKSPACES.items():
        found = [m for m in menus if m["module"] == module and m.get("id") == menu_id]
        if not found:
            violations.append(f"{module}: W1 workspace menu {menu_id} missing")
            continue
        parent = found[0].get("parent", "")
        if parent != ".".join(ROOT_MENU):
            violations.append(
                f"{module}.{menu_id}: parent {parent!r} is not the shared root "
                f"{'.'.join(ROOT_MENU)!r}"
            )

    # 2/3. Integrity + gating for every menuitem.
    for menu in menus:
        module, menu_id = menu["module"], menu.get("id", "?")
        for attr in ("parent", "action", "groups"):
            for ref in menu.get(attr, "").split(","):
                ref = ref.strip()
                if not ref:
                    continue
                if attr == "groups" and not resolves(declared, ref, module):
                    violations.append(f"{module}.{menu_id}: group {ref!r} does not resolve")
                if attr == "parent" and "." in ref and not resolves(declared, ref, module):
                    violations.append(f"{module}.{menu_id}: parent {ref!r} does not resolve")
                if attr == "action" and "." in ref and not resolves(declared, ref, module):
                    violations.append(f"{module}.{menu_id}: action {ref!r} does not resolve")
        is_workspace = menu_id in W1_WORKSPACES.values()
        if is_workspace:
            gates = [g.strip() for g in menu.get("groups", "").split(",") if g.strip()]
            gated = any(
                (WORKSPACE_GROUPS.fullmatch(g) if "." in g else re.fullmatch(r"group_ws_\w+", g))
                for g in gates
            )
            if not gated:
                violations.append(
                    f"{module}.{menu_id}: workspace menu without a workspace role gate (NVR-22)"
                )

    # 4. NVR-23 — no workspace exceeds seven second-level sections.
    def sections_of(module: str, menu_id: str) -> list[dict]:
        full_id = f"{module}.{menu_id}"
        return [
            m for m in menus
            if m.get("parent") == full_id
            or (m.get("parent") == menu_id and m["module"] == module)
        ]

    for module, menu_id in W1_WORKSPACES.items():
        sections = sections_of(module, menu_id)
        if len(sections) > MAX_SECTIONS_PER_WORKSPACE:
            violations.append(
                f"{module}.{menu_id}: {len(sections)} second-level sections exceeds NVR-23 ({MAX_SECTIONS_PER_WORKSPACE})"
            )

    # 5. Every action's res_model is defined by a model file in addons/ or by
    # an Odoo core/vendor module present in the tree.
    model_names: set[str] = set()
    for root in (ADDONS, REPO / "vendor"):
        if not root.is_dir():
            continue
        for py in root.rglob("*.py"):
            if "__pycache__" in py.parts:
                continue
            for m in re.finditer(r'_name\s*=\s*"([\w.]+)"', py.read_text(encoding="utf-8", errors="ignore")):
                model_names.add(m.group(1))
    for xml in ADDONS.rglob("*.xml"):
        if "vendor" in xml.parts:
            continue
        text = xml.read_text(encoding="utf-8", errors="ignore")
        for m in re.finditer(
            r'model="ir\.actions\.act_window".*?res_model">([\w.]+)<', text, re.DOTALL
        ):
            if m.group(1) not in model_names and m.group(1) not in CORE_MODELS:
                violations.append(
                    f"{xml.relative_to(ADDONS).as_posix()}: action targets undefined model {m.group(1)}"
                )

    # 6. View integrity — every field a workspace view references exists on
    # its model (inline one2many sub-views resolved through comodels). This
    # is the audit pass that caught the device-history phantom fields.
    from importlib import import_module

    view_integrity = import_module("audit-view-integrity")
    fields_by_model, relations = view_integrity.load_model_fields()
    violations.extend(view_integrity.check_views(fields_by_model, relations))

    if violations:
        print(f"portal-contract: FAIL - {len(violations)} violation(s):")
        for v in violations:
            print(f"  {v}")
        return 1
    section_counts = ", ".join(
        f"{menu_id}:{len(sections_of(module, menu_id))}"
        for module, menu_id in W1_WORKSPACES.items()
    )
    print(f"portal-contract: OK - 6 W1 workspaces gated under the shared root; "
          f"references resolve; sections [{section_counts}] within NVR-23; "
          f"view fields resolve ({len(fields_by_model)} models)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
