import importlib.util
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

for mod_name in ["m21", "m22", "m55", "m56", "m57", "m58", "m59"]:
    path = os.path.join(
        "addons", "platform", "cd_p03_portal", "controllers", "a09", f"{mod_name}.py"
    )
    spec = importlib.util.spec_from_file_location(mod_name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    print(f"\n=== {mod_name.upper()} SURFACES ===")
    surfaces = getattr(mod, "SURFACES", {})
    for m, conf in surfaces.items():
        acts = list(conf.get("actions", set()))
        print(f"  {m}: actions={acts}")
