# A04 - /p03/model/write accepts only what a workspace form offers (the A03 R3
# whitelist applied to A04, workflow audit C2 / D1).
#
# The audit found that no A04 surface declared a `writable` whitelist, and 54
# of 58 models were writable by a plain user. The endpoint mechanism is tested
# in test_a03_write_whitelist.py; this keeps the A04 list in step with the A04
# forms and proves every A04 surface declares it.
from odoo.addons.cd_p03_portal.controllers import a04, form_fields
from odoo.addons.cd_p03_portal.controllers import p03_generic_api as api
from odoo.addons.cd_p03_portal.controllers.a04.writable import WRITABLE


def test_a04_writable_matches_the_forms():
    """writable.py is generated; a form edited without regenerating it would
    have its new field refused on save. Regenerate with
    `python addons/platform/cd_p03_portal/controllers/form_fields.py --a04`."""
    editable = form_fields.editable_by_model()
    expected = {m: frozenset(editable.get(m, ())) for m in form_fields.surface_models("a04")}
    assert expected == WRITABLE


def test_every_a04_surface_declares_what_it_accepts():
    missing = [m for m, conf in a04.SURFACES.items() if "writable" not in conf]
    assert not missing
    for model in a04.SURFACES:
        assert api.SURFACES[model]["writable"] is WRITABLE[model]
