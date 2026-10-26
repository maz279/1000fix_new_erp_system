# A02 · Service Operations — per-module workspace surfaces, merged here so
# the generic endpoints serve exactly what the module files declare (same
# shape as controllers/a08).
from . import m01, m02

MODULES = {
    "M01": m01,
    "M02": m02,
}

SURFACES = {}
for _mod in MODULES.values():
    for _model, _conf in _mod.SURFACES.items():
        if _model in SURFACES:
            raise ValueError("A02 surface %s is declared by two modules" % _model)
        SURFACES[_model] = _conf
