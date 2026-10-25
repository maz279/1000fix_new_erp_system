# A08 · Finance & Treasury — per-module workspace surfaces, merged here so the
# generic endpoints serve exactly what the eight module files declare.
from . import m19, m20, m49, m50, m51, m52, m53, m54

SURFACES = {}
for _mod in (m19, m20, m52, m50, m51, m53, m49, m54):
    for _model, _conf in _mod.SURFACES.items():
        if _model in SURFACES:
            raise ValueError("A08 surface %s is declared by two modules" % _model)
        SURFACES[_model] = _conf
