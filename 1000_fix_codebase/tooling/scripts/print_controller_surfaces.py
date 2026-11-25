import os
import re

for mod in ["m21", "m22", "m55", "m56", "m57", "m58", "m59"]:
    p = os.path.join("addons", "platform", "cd_p03_portal", "controllers", "a09", f"{mod}.py")
    with open(p, encoding="utf-8") as f:
        text = f.read()
    match = re.search(r"SURFACES\s*=\s*\{.*?\n\}", text, re.DOTALL)
    if match:
        print(f"=== {mod}.py ===")
        print(match.group(0))
