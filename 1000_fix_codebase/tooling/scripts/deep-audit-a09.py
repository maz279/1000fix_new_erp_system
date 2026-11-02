#!/usr/bin/env python3
import json
import re
from pathlib import Path

ROOT = Path(
    "c:/software_project/software_project_14/1000 fix/1000fix_new_erp_system/1000_fix_codebase"
)
STATIC_A09 = ROOT / "addons" / "platform" / "cd_p03_portal" / "static" / "src" / "a09"
CTRL_A09 = ROOT / "addons" / "platform" / "cd_p03_portal" / "controllers" / "a09"
REG_PATH = ROOT / "contracts" / "nav" / "registry.json"

with open(REG_PATH, encoding="utf-8") as f:
    reg = json.load(f)

modules_data = {m["id"]: m for m in reg.get("modules", []) if m.get("id")}
A09_MODS = ["M21", "M55", "M56", "M57", "M22", "M58", "M59"]

detailed_findings = {}

for mid in A09_MODS:
    mod_reg = modules_data.get(mid, {})
    js_file = STATIC_A09 / f"{mid.lower()}.js"
    py_file = CTRL_A09 / f"{mid.lower()}.py"

    js_text = js_file.read_text(encoding="utf-8") if js_file.exists() else ""
    py_text = py_file.read_text(encoding="utf-8") if py_file.exists() else ""

    # Parse SCREENS dictionary
    screens_def = {}
    screen_blocks = re.findall(r"'([A-Z0-9_\-]+)':\s*\{([^\}]+)\}", js_text)

    # Check for D365 features in JS
    has_search_config = "search:" in js_text or "searchCols:" in js_text
    has_filter_chips_declared = "filterChips:" in js_text or "filters:" in js_text
    has_export_config = "export:" in js_text or "exportable:" in js_text
    has_date_picker = "period: true" in js_text

    # Reports in python
    reports_py = re.findall(r"def\s+([a-zA-Z0-9_]+)\s*\([^)]*\):", py_text)
    reports_py = [r for r in reports_py if not r.startswith("_") and r != "kpis"]

    # Forms in JS
    forms_js = re.findall(r"'([A-Z0-9_\-]+form[A-Z0-9_\-]*)':\s*\{", js_text)

    # Deficiencies checklist
    deficiencies = []
    if not has_search_config:
        deficiencies.append("No Quick-Find search fields configured for grids")
    if not has_filter_chips_declared:
        deficiencies.append(
            "No multi-dimensional facet/filter chips (e.g. Branch, Date Range, Category, Type)"
        )
    if "period: false" in js_text:
        deficiencies.append(
            "Reports hardcoded with 'period: false', preventing custom date-range selection"
        )
    if not has_export_config:
        deficiencies.append("No grid-level Export to Excel/CSV command bar buttons configured")
    if len(forms_js) < len(mod_reg.get("groups", [])):
        deficiencies.append(
            f"Incomplete in-workspace forms ({len(forms_js)} forms for {len(mod_reg.get('groups', []))} functional groups)"
        )

    detailed_findings[mid] = {
        "title": mod_reg.get("en"),
        "title_bn": mod_reg.get("bn"),
        "desc": mod_reg.get("desc"),
        "groups": [g.get("en") for g in mod_reg.get("groups", [])],
        "screens_count": len(re.findall(r"'M[0-9]+-[a-z0-9\-]+':\s*\{", js_text)),
        "forms_count": len(forms_js),
        "forms": forms_js,
        "reports_count": len(mod_reg.get("reports", [])),
        "reports_py": reports_py,
        "deficiencies": deficiencies,
    }

output_path = ROOT / "tooling" / "scripts" / "a09_detailed_deficiencies.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(detailed_findings, f, indent=2, ensure_ascii=False)

print(f"Detailed deficiencies written to {output_path}")
for mid, d in detailed_findings.items():
    print(f"\n[{mid}] {d['title']}")
    print(f"  Groups: {', '.join(d['groups'])}")
    print(f"  Forms: {len(d['forms'])} | Reports: {len(d['reports_py'])}")
    print("  Deficiencies:")
    for df in d["deficiencies"]:
        print(f"    - {df}")
