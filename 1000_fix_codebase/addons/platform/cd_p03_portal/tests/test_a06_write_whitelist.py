# A06 - /p03/model/write accepts only what a workspace form offers (the A03 R3
# whitelist applied to A06, workflow audit D1).
#
# The A06 audit (2026-11-03) found that no A06 surface declared a `writable`
# whitelist, and 58 of 66 models exposed a workflow field the form endpoint
# would write. The endpoint mechanism is tested in test_a03_write_whitelist.py;
# this keeps the A06 list in step with the A06 forms and proves every A06
# surface declares it.
from odoo.addons.cd_p03_portal.controllers import a06, form_fields
from odoo.addons.cd_p03_portal.controllers import p03_generic_api as api
from odoo.addons.cd_p03_portal.controllers.a06.writable import WRITABLE


def test_a06_writable_matches_the_forms():
    """writable.py is generated; a form edited without regenerating it would
    have its new field refused on save. Regenerate with
    `python addons/platform/cd_p03_portal/controllers/form_fields.py --a06`."""
    editable = form_fields.editable_by_model()
    expected = {m: frozenset(editable.get(m, ())) for m in form_fields.surface_models("a06")}
    assert expected == WRITABLE


def test_every_a06_surface_declares_what_it_accepts():
    missing = [m for m, conf in a06.SURFACES.items() if "writable" not in conf]
    assert not missing
    for model in a06.SURFACES:
        assert api.SURFACES[model]["writable"] is WRITABLE[model]


def test_a06_whitelist_never_offers_state_or_status():
    """The audit's headline S2 finding: every A06 `state` (and the supplier's
    `status`) was settable from a workspace form."""
    offered = {
        model: sorted(names & {"state", "status", "approval_state", "match_state"})
        for model, names in WRITABLE.items()
        if names & {"state", "status", "approval_state", "match_state"}
    }
    assert not offered, offered
