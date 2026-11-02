import json
import sys

sys.stdout.reconfigure(encoding="utf-8")

with open("tooling/scripts/a09_backend_analysis.json", encoding="utf-8") as f:
    be = json.load(f)

for mod_code, mdata in be.items():
    print(f"\n==================== {mod_code} ====================")
    for m in mdata.get("models", []):
        mname = m.get("model") or m.get("inherit")
        print(f"Model: {mname}")
        print(f"  Fields: {m.get('fields', [])}")
        print(f"  Methods: {m.get('methods', [])}")
