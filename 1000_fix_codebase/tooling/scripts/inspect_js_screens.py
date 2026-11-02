import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

a09_dir = os.path.abspath("addons/platform/cd_p03_portal/static/src/a09")
for mod in ["m21", "m22", "m55", "m56", "m57", "m58", "m59"]:
    p = os.path.join(a09_dir, f"{mod}.js")
    with open(p, encoding="utf-8") as f:
        content = f.read()

    # find all screens
    screens = re.findall(r"'([A-Z0-9\-]+)':\s*\{([^}]+)\}", content)
    print(
        f"\n==================== {mod.upper()} (Found {len(screens)} screens/reports/forms) ===================="
    )

    # Check reports with period: false
    period_false = re.findall(r"'([A-Z0-9\-]+)':\s*\{[^}]*period:\s*false[^}]*\}", content)
    print(f"Reports with period: false ({len(period_false)}): {period_false}")

    # Check screens with model_list
    model_lists = re.findall(r"'([A-Z0-9\-]+)':\s*\{[^}]*kind:\s*'model_list'[^}]*\}", content)
    print(f"Model lists ({len(model_lists)}): {model_lists}")
