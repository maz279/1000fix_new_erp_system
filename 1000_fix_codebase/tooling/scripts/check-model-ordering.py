import re
from pathlib import Path

addons = Path("addons")
issues = []
for init_path in addons.rglob("models/__init__.py"):
    model_dir = init_path.parent
    text = init_path.read_text(encoding="utf-8")
    imported_modules = []
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("from . import"):
            parts = line[len("from . import") :].split(",")
            for p in parts:
                p = p.strip()
                if p:
                    imported_modules.append(p)

    defs = {}
    inherits = {}
    for m in imported_modules:
        m_file = model_dir / f"{m}.py"
        if not m_file.exists():
            continue
        code = m_file.read_text(encoding="utf-8")
        for n in re.findall(r'_name\s*=\s*["\']([^"\']+)["\']', code):
            defs[n] = m
        for inh in re.findall(r'_inherit\s*=\s*["\']([^"\']+)["\']', code):
            inherits.setdefault(m, []).append(inh)

    for m, inh_list in inherits.items():
        if m not in imported_modules:
            continue
        m_idx = imported_modules.index(m)
        for inh in inh_list:
            if inh in defs:
                def_m = defs[inh]
                if def_m not in imported_modules:
                    continue
                def_idx = imported_modules.index(def_m)
                if def_idx > m_idx:
                    issues.append(
                        f"{init_path}: {m} inherits {inh} defined in {def_m} (imported {def_idx} > {m_idx})"
                    )

print(f"Found {len(issues)} ordering issues:")
for iss in issues:
    print(" ", iss)
