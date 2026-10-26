# A02 · Service Operations — per-module workspace surfaces, merged here so
# the generic endpoints serve exactly what the module files declare (same
# shape as controllers/a08). m04 re-registered 20:0x after its duplicate
# SURFACES entries (fix.token.queue / fix.walkin.intake, owned by m01)
# were removed — the M04 queue/intake actions live on the m01 entries.
from . import m01, m02, m03, m04, m31

MODULES = {
    "M01": m01,
    "M02": m02,
    "M03": m03,
    "M04": m04,
    "M31": m31,
}

SURFACES = {}
for _mod in MODULES.values():
    for _model, _conf in _mod.SURFACES.items():
        if _model in SURFACES:
            raise ValueError("A02 surface %s is declared by two modules" % _model)
        SURFACES[_model] = _conf
