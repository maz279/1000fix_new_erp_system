import json

with open("tooling/scripts/a09_backend_analysis.json", encoding="utf-8") as f:
    backend = json.load(f)

with open("tooling/scripts/a09_metadata.json", encoding="utf-8") as f:
    meta = json.load(f)

for mod_code, mod_info in meta.items():
    print(f"\n==================== {mod_code} : {mod_info['en']} ====================")
    print("Reports:", mod_info.get("reports", []))
    print("Forms:", mod_info.get("forms", []))
    for grp in mod_info["groups"]:
        print(f"  [Group: {grp['en']}]")
        for sc in grp["screens"]:
            sc_id = sc["id"]
            sc_def = mod_info.get("screens_def", {}).get(sc_id, {})
            model = sc_def.get("model")
            cols = sc_def.get("cols", [])
            kind = sc_def.get("kind", sc.get("t"))
            actions = [a.get("m") for a in sc_def.get("actions", [])]
            print(f"    - Screen '{sc_id}' ({sc['en']}) kind={kind} model={model}")
            if cols:
                print(f"      current cols: {cols}")
            if actions:
                print(f"      actions: {actions}")
            if model and model in backend.get("models", {}):
                m_info = backend["models"][model]
                fields = list(m_info.get("fields", {}).keys())
                methods = m_info.get("methods", [])
                print(f"      backend fields: {fields[:10]} (total {len(fields)})")
                if methods:
                    print(f"      backend methods: {methods}")
