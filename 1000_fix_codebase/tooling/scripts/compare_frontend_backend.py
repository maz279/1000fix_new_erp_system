import json
import sys

sys.stdout.reconfigure(encoding="utf-8")

with open("tooling/scripts/a09_full_js_parsed.json", encoding="utf-8") as f:
    fe = json.load(f)

with open("tooling/scripts/a09_backend_analysis.json", encoding="utf-8") as f:
    be = json.load(f)

all_models = {}
for _mod_code, mdata in be.items():
    for mname, minfo in mdata.get("models", {}).items():
        all_models[mname] = minfo

print(f"Total backend models loaded: {len(all_models)}")

for mod_code, mod_data in fe.items():
    print(f"\n==================== {mod_code.upper()} ====================")
    screens = mod_data["SCREENS"]
    for sc in screens:
        sc_id = sc["id"]
        kind = sc.get("kind")
        if kind == "model_list":
            model = sc.get("model")
            cols = sc.get("cols", [])
            if model in all_models:
                minfo = all_models[model]
                be_fields = minfo.get("fields", {})
                be_methods = [m for m in minfo.get("methods", []) if m.startswith("action_")]
                actions = [a.get("m") for a in sc.get("actions", [])]

                # Check column count
                print(f"  {sc_id} ({model}): {len(cols)} cols: {cols}")
                if len(cols) <= 4:
                    avail = [
                        f
                        for f in be_fields
                        if f not in cols
                        and f not in ("id", "create_uid", "write_uid", "create_date", "write_date")
                    ]
                    print(f"    -> Can enrich cols with: {avail[:6]}")
                if be_methods and not actions:
                    print(f"    -> Has workflow actions: {be_methods}")
            else:
                print(
                    f"  {sc_id}: Model {model} not in domain addons (might be hr.employee or similar)"
                )
