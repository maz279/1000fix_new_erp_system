# A08 - /p03/model/write accepts only what a workspace form offers (the A03 R3
# whitelist applied to A08, workflow audit D1).
#
# The A08 audit (2026-11-04) found that no A08 surface declared a `writable`
# whitelist, and 71 of 97 models exposed a workflow field the form endpoint
# would write. The endpoint mechanism is tested in test_a03_write_whitelist.py;
# this keeps the A08 list in step with the A08 forms and proves every A08
# surface declares it.
from odoo.addons.cd_p03_portal.controllers import a08, form_fields
from odoo.addons.cd_p03_portal.controllers import p03_generic_api as api
from odoo.addons.cd_p03_portal.controllers.a08.writable import WRITABLE


def test_a08_writable_matches_the_forms():
    """writable.py is generated; a form edited without regenerating it would
    have its new field refused on save. Regenerate with
    `python addons/platform/cd_p03_portal/controllers/form_fields.py --a08`."""
    editable = form_fields.editable_by_model()
    expected = {m: frozenset(editable.get(m, ())) for m in form_fields.surface_models("a08")}
    assert expected == WRITABLE


def test_every_a08_surface_declares_what_it_accepts():
    missing = [m for m, conf in a08.SURFACES.items() if "writable" not in conf]
    assert not missing
    for model in a08.SURFACES:
        assert api.SURFACES[model]["writable"] is WRITABLE[model]


def test_a08_whitelist_never_offers_state_or_status():
    """The audit's D2 finding: an accountant set a bill's approval_state, a
    payment's state or a statement line's match_state from a workspace form."""
    offered = {
        model: sorted(names & {"state", "status", "approval_state", "match_state", "payment_state"})
        for model, names in WRITABLE.items()
        if names & {"state", "status", "approval_state", "match_state", "payment_state"}
    }
    assert not offered, offered
