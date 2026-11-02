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

audit_summary = {}

for mid in A09_MODS:
    mod_reg = modules_data.get(mid, {})
    js_path = STATIC_A09 / f"{mid.lower()}.js"
    py_path = CTRL_A09 / f"{mid.lower()}.py"

    js_exists = js_path.exists()
    py_exists = py_path.exists()

    js_content = js_path.read_text(encoding="utf-8") if js_exists else ""
    py_content = py_path.read_text(encoding="utf-8") if py_exists else ""

    # Check screens in registry
    reg_screens = []
    for g in mod_reg.get("groups", []):
        for s in g.get("screens", []):
            if isinstance(s, dict):
                reg_screens.append(s.get("id") or s.get("key"))
            elif isinstance(s, str):
                reg_screens.append(s)

    # Check screens in JS
    js_screens = []
    screens_match = re.search(r"const SCREENS = \{([\s\S]*?)\n\};", js_content)
    if screens_match:
        for line in screens_match.group(1).splitlines():
            m = re.match(r"\s*['\"]([^'\"]+)['\"]\s*:", line)
            if m:
                js_screens.append(m.group(1))

    # Check reports in registry
    reg_reports = []
    for r in mod_reg.get("reports", []):
        if isinstance(r, dict):
            reg_reports.append(r.get("id") or r.get("key") or r.get("en"))
        elif isinstance(r, str):
            reg_reports.append(r)

    # Check report routes in JS
    js_report_routes = []
    rep_match = re.search(r"const REPORT_ROUTES = \{([\s\S]*?)\n\};", js_content)
    if rep_match:
        for line in rep_match.group(1).splitlines():
            m = re.match(r"\s*['\"]([^'\"]+)['\"]\s*:", line)
            if m:
                js_report_routes.append(m.group(1))

    has_form_models = "FORM_MODELS" in js_content
    has_form_chips = "FORM_CHIPS" in js_content
    has_create = "CREATE" in js_content

    py_routes = re.findall(r'@http\.route\(\s*(\[[^\]]*\]|"[^"]*"|\'[^\']*\')', py_content)
    has_surfaces = "SURFACES = {" in py_content
    has_reports_py = "REPORTS = {" in py_content
    has_kpis_py = "/kpis" in py_content

    models_referenced = set(re.findall(r'model:\s*[\'"]([a-zA-Z0-9_\.]+)[\'"]', js_content))
    models_referenced.update(re.findall(r'request\.env\[[\'"]([a-zA-Z0-9_\.]+)[\'"]\]', py_content))

    audit_summary[mid] = {
        "title": mod_reg.get("en"),
        "title_bn": mod_reg.get("bn"),
        "js_size": len(js_content),
        "py_size": len(py_content),
        "reg_screens_count": len(reg_screens),
        "reg_screens": reg_screens,
        "js_screens_count": len(js_screens),
        "js_screens": js_screens,
        "missing_screens": [s for s in reg_screens if s not in js_screens],
        "reg_reports_count": len(reg_reports),
        "reg_reports": reg_reports,
        "js_report_routes_count": len(js_report_routes),
        "has_form_models": has_form_models,
        "has_form_chips": has_form_chips,
        "has_create": has_create,
        "py_routes_count": len(py_routes),
        "has_surfaces": has_surfaces,
        "has_reports_py": has_reports_py,
        "has_kpis_py": has_kpis_py,
        "models_referenced": sorted(list(models_referenced)),
    }

output_path = ROOT / "tooling" / "scripts" / "a09_audit_summary.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(audit_summary, f, indent=2, ensure_ascii=False)

print(f"Audit summary written to {output_path}")
for mid, d in audit_summary.items():
    print(f"\n[{mid}] {d['title']}")
    print(
        f"  Screens: {d['js_screens_count']}/{d['reg_screens_count']} (missing: {d['missing_screens']})"
    )
    print(f"  Reports: {d['js_report_routes_count']}/{d['reg_reports_count']}")
    print(
        f"  Forms: has_form_models={d['has_form_models']}, has_form_chips={d['has_form_chips']}, has_create={d['has_create']}"
    )
    print(
        f"  Controller: {d['py_routes_count']} routes, has_surfaces={d['has_surfaces']}, has_reports={d['has_reports_py']}"
    )
    print(f"  Models: {', '.join(d['models_referenced'][:6])}...")
