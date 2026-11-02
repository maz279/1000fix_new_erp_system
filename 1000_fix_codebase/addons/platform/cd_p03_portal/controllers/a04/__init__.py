# A04 · Commercial & Revenue — per-module workspace surfaces, merged here so
# the generic endpoints serve exactly what the module files declare (same
# shape as controllers/a02, a03, a08, a11).
from . import m08, m09, m11, m12, m36, m37, m38, m39, m40

MODULES = {
    "M08": m08,
    "M09": m09,
    "M11": m11,
    "M12": m12,
    "M36": m36,
    "M37": m37,
    "M38": m38,
    "M39": m39,
    "M40": m40,
}

SURFACES = {}
for _mod in MODULES.values():
    for _model, _conf in _mod.SURFACES.items():
        if _model in SURFACES:
            raise ValueError("A04 surface %s is declared by two modules" % _model)
        SURFACES[_model] = _conf
