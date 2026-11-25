#!/usr/bin/env python3
import ast
import json
from pathlib import Path

ROOT = Path(
    "c:/software_project/software_project_14/1000 fix/1000fix_new_erp_system/1000_fix_codebase"
)
H_PEOPLE = ROOT / "addons" / "domain" / "h_people"

addons = [
    ("M21", "cd_hr_core"),
    ("M55", "cd_attendance"),
    ("M56", "cd_payroll_bd"),
    ("M57", "cd_performance"),
    ("M22", "cd_competency"),
    ("M58", "cd_talent"),
    ("M59", "cd_hse"),
]

report = {}

for mid, addon_name in addons:
    addon_dir = H_PEOPLE / addon_name
    models_dir = addon_dir / "models"

    models = []
    if models_dir.exists():
        for py_file in models_dir.glob("*.py"):
            if py_file.name == "__init__.py":
                continue
            try:
                tree = ast.parse(py_file.read_text(encoding="utf-8"))
            except Exception as exc:  # unparsable file: report it, keep scanning
                print(f"skip {py_file}: {exc}")
                continue

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    model_name = None
                    inherit_name = None
                    methods = []
                    fields = []
                    for item in node.body:
                        if isinstance(item, ast.Assign):
                            for target in item.targets:
                                if isinstance(target, ast.Name):
                                    if target.id == "_name" and isinstance(
                                        item.value, ast.Constant
                                    ):
                                        model_name = item.value.value
                                    elif target.id == "_inherit":
                                        if isinstance(item.value, ast.Constant):
                                            inherit_name = item.value.value
                                        elif isinstance(item.value, ast.List):
                                            inherit_name = [
                                                e.value
                                                for e in item.value.elts
                                                if isinstance(e, ast.Constant)
                                            ]
                                    elif isinstance(item.value, ast.Call):
                                        fields.append(target.id)
                        elif isinstance(item, ast.FunctionDef) and not item.name.startswith("__"):
                            methods.append(item.name)

                    if model_name or inherit_name:
                        models.append(
                            {
                                "file": py_file.name,
                                "class": node.name,
                                "model": model_name,
                                "inherit": inherit_name,
                                "fields_count": len(fields),
                                "fields": fields[:12],
                                "methods": methods,
                            }
                        )

    views_dir = addon_dir / "views"
    views = [v.name for v in views_dir.glob("*.xml")] if views_dir.exists() else []

    security_dir = addon_dir / "security"
    has_acl = (security_dir / "ir.model.access.csv").exists() if security_dir.exists() else False

    report[mid] = {
        "addon": addon_name,
        "models_count": len(models),
        "models": models,
        "views": views,
        "has_acl": has_acl,
    }

output_path = ROOT / "tooling" / "scripts" / "a09_backend_analysis.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2, ensure_ascii=False)

print(f"Backend analysis written to {output_path}")
for mid, d in report.items():
    print(
        f"\n[{mid}] {d['addon']} ({d['models_count']} models, {len(d['views'])} view files, ACL={d['has_acl']})"
    )
    for m in d["models"]:
        print(
            f"  Model: {m['model'] or m['inherit']} ({m['fields_count']} fields, {len(m['methods'])} methods) in {m['file']}"
        )
        if m["methods"]:
            print(f"    Methods: {', '.join(m['methods'][:6])}")
