import os

path = os.path.abspath("addons/platform/cd_p03_portal/controllers/a09/__init__.py")
with open(path, encoding="utf-8") as f:
    content = f.read()

target = """def kpis(env, module=None):
    if module in (None, "M21"):
        return {"M21": m21.kpis(env)}
    if module in ("M55",):
        return {"M55": m55.kpis(env)}
    if module in ("M56",):
        return {"M56": m56.kpis(env)}
    if module in ("M57",):
        return {"M57": m57.kpis(env)}
    if module in ("M22",):
        return {"M22": m22.kpis(env)}
    if module in ("M58",):
        return {"M58": m58.kpis(env)}
    if module in ("M59",):
        return {"M59": m59.kpis(env)}
    return {}"""

replacement = """def kpis(env, module=None):
    if module:
        mod = MODULES.get(module)
        return {module: mod.kpis(env)} if mod else {}
    return {code: mod.kpis(env) for code, mod in MODULES.items()}"""

norm_content = content.replace("\r\n", "\n")
norm_target = target.replace("\r\n", "\n")
norm_replacement = replacement.replace("\r\n", "\n")

if norm_target in norm_content:
    norm_content = norm_content.replace(norm_target, norm_replacement, 1)
    with open(path, "w", encoding="utf-8") as f:
        f.write(norm_content)
    print("Successfully updated kpis function in a09/__init__.py")
else:
    print("Target not found")
