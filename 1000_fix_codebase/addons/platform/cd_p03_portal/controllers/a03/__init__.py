# A03 · Customer Experience — per-module workspace surfaces, merged here so
# the generic endpoints serve exactly what the module files declare (same
# shape as controllers/a02 and controllers/a08).
from . import m07, m10, m27, m32, m33, m34, m35

MODULES = {
    "M07": m07,
    "M10": m10,
    "M27": m27,
    "M32": m32,
    "M33": m33,
    "M34": m34,
    "M35": m35,
}

SURFACES = {}
for _mod in MODULES.values():
    for _model, _conf in _mod.SURFACES.items():
        if _model in SURFACES:
            raise ValueError("A03 surface %s is declared by two modules" % _model)
        SURFACES[_model] = _conf
