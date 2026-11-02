import json
import sys

sys.stdout.reconfigure(encoding="utf-8")

with open("tooling/scripts/a09_full_js_parsed.json", encoding="utf-8") as f:
    fe = json.load(f)

with open("tooling/scripts/a09_backend_analysis.json", encoding="utf-8") as f:
    be = json.load(f)

all_models = {}
for _mod_code, mdata in be.items():
    for item in mdata.get("models", []):
        mname = item.get("model") or item.get("inherit")
        if mname:
            all_models[mname] = item

print(f"Total backend models loaded: {len(all_models)}")
for m in sorted(all_models.keys()):
    print(f"  {m}: fields={len(all_models[m]['fields'])}, methods={all_models[m]['methods']}")
