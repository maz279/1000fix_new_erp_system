# A07 - /p03/model/write accepts only what a workspace form offers (the A03 R3
# whitelist applied to A07, workflow audit D1).
#
# The audit found that no A07 surface declared a `writable` whitelist, and 33
# of 46 models exposed a workflow field the form endpoint would write. The
# endpoint mechanism is tested in test_a03_write_whitelist.py; this keeps the
# A07 list in step with the A07 forms and proves every A07 surface declares it.
from odoo.addons.cd_p03_portal.controllers import a07, form_fields
from odoo.addons.cd_p03_portal.controllers import p03_generic_api as api
from odoo.addons.cd_p03_portal.controllers.a07.writable import WRITABLE


def test_a07_writable_matches_the_forms():
    """writable.py is generated; a form edited without regenerating it would
    have its new field refused on save. Regenerate with
    `python addons/platform/cd_p03_portal/controllers/form_fields.py --a07`."""
    editable = form_fields.editable_by_model()
    expected = {m: frozenset(editable.get(m, ())) for m in form_fields.surface_models("a07")}
    assert expected == WRITABLE


def test_every_a07_surface_declares_what_it_accepts():
    missing = [m for m, conf in a07.SURFACES.items() if "writable" not in conf]
    assert not missing
    for model in a07.SURFACES:
        assert api.SURFACES[model]["writable"] is WRITABLE[model]


def test_a07_whitelist_excludes_the_guarded_workflow_fields():
    """The fields the A07 P0 guards protect are never offered for editing."""
    for model, names in {
        "fix.facility.work.order": {"state", "verified_by_id", "completed_by_id"},
        "fix.equipment": {"operational_status", "retired_on"},
        "fix.iot.action": {"state", "outcome"},
        "fix.iot.consent": {"state", "revoked_by", "revoked_on"},
        "fix.device.identity": {"state"},
        "fix.vehicle.accident": {"state", "closed_by_id"},
    }.items():
        assert not (names & WRITABLE[model]), (model, sorted(names & WRITABLE[model]))
