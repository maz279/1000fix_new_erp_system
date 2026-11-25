#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(
    "c:/software_project/software_project_14/1000 fix/1000fix_new_erp_system/1000_fix_codebase"
)
REG_PATH = ROOT / "contracts" / "nav" / "registry.json"

with open(REG_PATH, encoding="utf-8") as f:
    reg = json.load(f)

modules_to_find = ["M21", "M55", "M56", "M57", "M22", "M58", "M59"]

modules = reg.get("modules", [])
mod_map = {m.get("id"): m for m in modules if isinstance(m, dict) and m.get("id")}

a09_mods = {mid: mod_map.get(mid, {}) for mid in modules_to_find}

output_path = ROOT / "tooling" / "scripts" / "a09_metadata.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(a09_mods, f, indent=2, ensure_ascii=False)

print(f"Successfully wrote A09 metadata for {len(a09_mods)} modules to {output_path}")

for mid, m in a09_mods.items():
    print(f"Module {mid}: en='{m.get('en')}' (area={m.get('area')})")
    print(f"  Groups: {len(m.get('groups', []))}")
    for g in m.get("groups", []):
        print(f"    - {g.get('id')}: {g.get('en')} ({len(g.get('screens', []))} screens)")
    print(f"  Reports: {len(m.get('reports', []))}")
    for r in m.get("reports", []):
        print(f"    - {r.get('id') if isinstance(r, dict) else r}")
