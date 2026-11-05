# A09 - /p03/model/write accepts only what a workspace form offers (B1 of the
# A09 workflow audit, the A03 R3 whitelist applied to A09).
#
# The audit found that no A09 surface declared a `writable` whitelist, so the
# endpoint wrote any non-readonly field it was sent: a payroll officer set a
# period's state, an employee set their own leave to approved. The endpoint
# mechanism is tested in test_a03_write_whitelist.py; this keeps the A09 list
# in step with the A09 forms and proves every A09 surface declares it.
from odoo.addons.cd_p03_portal.controllers import a09, form_fields
from odoo.addons.cd_p03_portal.controllers import p03_generic_api as api
from odoo.addons.cd_p03_portal.controllers.a09.writable import WRITABLE


def test_a09_writable_matches_the_forms():
    """writable.py is generated; a form edited without regenerating it would
    have its new field refused on save. Regenerate with
    `python addons/platform/cd_p03_portal/controllers/form_fields.py --a09`."""
    editable = form_fields.editable_by_model()
    expected = {m: frozenset(editable.get(m, ())) for m in form_fields.surface_models("a09")}
    assert expected == WRITABLE


def test_every_a09_surface_declares_what_it_accepts():
    missing = [m for m, conf in a09.SURFACES.items() if "writable" not in conf]
    assert not missing
    for model in a09.SURFACES:
        assert api.SURFACES[model]["writable"] is WRITABLE[model]
