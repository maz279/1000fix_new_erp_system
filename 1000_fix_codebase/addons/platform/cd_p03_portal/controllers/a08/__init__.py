# A08 · Finance & Treasury — per-module workspace surfaces, merged here so the
# generic endpoints serve exactly what the eight module files declare.
from . import m19, m20, m49, m50, m51, m52, m53, m54

# module code -> its file (for optional per-module hooks such as kpis(env))
MODULES = {
    "M19": m19,
    "M20": m20,
    "M52": m52,
    "M50": m50,
    "M51": m51,
    "M53": m53,
    "M49": m49,
    "M54": m54,
}

SURFACES = {}
for _mod in MODULES.values():
    for _model, _conf in _mod.SURFACES.items():
        if _model in SURFACES:
            raise ValueError("A08 surface %s is declared by two modules" % _model)
        SURFACES[_model] = _conf
