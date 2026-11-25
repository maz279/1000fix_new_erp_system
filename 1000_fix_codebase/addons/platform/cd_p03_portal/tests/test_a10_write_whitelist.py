# A10 - /p03/model/write accepts only what a workspace form offers (the A03 R3
# whitelist applied to A10, workflow audit D7/S2).
#
# The A10 audit (2026-11-04) found 30 of 31 area models writable by a plain
# internal user and zero write whitelists: an NCR's state, a CAPA's verdict, a
# certificate's result and an obligation's compliance status were all typed
# fields. The endpoint mechanism itself is tested in
# test_a03_write_whitelist.py; this keeps the A10 list in step with the A10
# forms and proves every A10 surface declares it. The per-field refusal sweep
# lives in test_a10_control_suite.py.
from odoo.addons.cd_p03_portal.controllers import a10, form_fields
from odoo.addons.cd_p03_portal.controllers import p03_generic_api as api
from odoo.addons.cd_p03_portal.controllers.a10.writable import WRITABLE


def test_a10_writable_matches_the_forms():
    """writable.py is generated; a form edited without regenerating it would
    have its new field refused on save. Regenerate with
    `python addons/platform/cd_p03_portal/controllers/form_fields.py --a10`."""
    editable = form_fields.editable_by_model()
    expected = {m: frozenset(editable.get(m, ())) for m in form_fields.surface_models("a10")}
    assert expected == WRITABLE


def test_every_a10_surface_declares_what_it_accepts():
    missing = [m for m, conf in a10.SURFACES.items() if "writable" not in conf]
    assert not missing
    for model in a10.SURFACES:
        assert api.SURFACES[model]["writable"] is WRITABLE[model]


# The audit's S2 headline words. `capa_status` joins them because the GRC
# audit finding closes through its CAPA (M23-10's open-findings KPI counts
# exactly this field); `sync_status` words cover the Mayan claim (M24-8) and
# the e-signature envelope's journey (M24-2).
WORKFLOW_WORDS = {
    "state",
    "status",
    "approval_state",
    "capa_status",
    "compliance_status",
    "mayan_sync_status",
    "signing_status",
}


def test_a10_whitelist_never_offers_the_workflow_words():
    """A workflow-owned word is never an editable input on an A10 form: the
    audit closed every one of these behind an action or the approval engine,
    so a form offering them would only teach users to type what the server
    refuses."""
    offered = {
        model: sorted(names & WORKFLOW_WORDS)
        for model, names in WRITABLE.items()
        if names & WORKFLOW_WORDS
    }
    assert not offered, offered
