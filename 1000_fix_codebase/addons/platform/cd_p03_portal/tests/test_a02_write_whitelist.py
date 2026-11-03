# A02 - /p03/model/write accepts only what a workspace form offers (A2 of the
# A02 workflow audit, the A03 R3 whitelist applied to A02).
#
# The audit found that no A02 surface declared a `writable` whitelist, so the
# endpoint wrote any non-readonly field it was sent: a cashier set her own
# variance approver, a technician set qc_passed. The endpoint mechanism is
# tested in test_a03_write_whitelist.py; this keeps the A02 list in step with
# the A02 forms and proves every A02 surface declares it.
from odoo.addons.cd_p03_portal.controllers import a02, form_fields
from odoo.addons.cd_p03_portal.controllers import p03_generic_api as api
from odoo.addons.cd_p03_portal.controllers.a02.writable import WRITABLE


def test_a02_writable_matches_the_forms():
    """writable.py is generated; a form edited without regenerating it would
    have its new field refused on save. Regenerate with
    `python addons/platform/cd_p03_portal/controllers/form_fields.py --a02`."""
    editable = form_fields.editable_by_model()
    expected = {m: frozenset(editable.get(m, ())) for m in form_fields.surface_models("a02")}
    assert expected == WRITABLE


def test_every_a02_surface_declares_what_it_accepts():
    missing = [m for m, conf in a02.SURFACES.items() if "writable" not in conf]
    assert not missing
    for model in a02.SURFACES:
        assert api.SURFACES[model]["writable"] is WRITABLE[model]
