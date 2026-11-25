# A03 - /p03/model/write accepts only what a workspace form offers (R3), and
# /p03/model/form shows workflow-locked fields read-only (R5).
#
# The A03 workflow audit (2026-11-03) found the endpoint wrote any field it
# was sent. The model guards (fix.guarded.mixin) closed the approval and
# state fields; this closes the rest of the surface: a field no form offers
# for editing is refused when it changes, and the forms stop offering inputs
# the server would refuse. Acts as a NON-ADMIN user throughout, because the
# superuser is trusted by the model guards and would hide a gap.
import itertools
from unittest import mock

import pytest
from odoo.addons.cd_p03_portal.controllers import a03, form_fields
from odoo.addons.cd_p03_portal.controllers import p03_generic_api as api
from odoo.addons.cd_p03_portal.controllers.a03.writable import WRITABLE

_SEQ = itertools.count(1)


class FakeRequest:
    def __init__(self, env):
        self.env = env


@pytest.fixture
def call():
    patchers = []

    def _call(env, route, **kw):
        p = mock.patch.object(api, "request", FakeRequest(env))
        p.start()
        patchers.append(p)
        return getattr(api.P03GenericApiController(), route)(**kw)

    yield _call
    for p in patchers:
        p.stop()


@pytest.fixture
def clerk_env(odoo_env):
    n = next(_SEQ)
    user = (
        odoo_env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "Whitelist Clerk %d" % n,
                "login": "whitelist.clerk.%d@a03.test" % n,
                "group_ids": [(6, 0, [odoo_env.ref("base.group_user").id])],
            }
        )
    )
    return odoo_env(user=user.id)


# --- the whitelist is the forms, exactly ------------------------------------


def test_the_scan_finds_forms():
    """A guard on the guard: an empty scan would make every list empty."""
    assert len(list(form_fields.forms())) >= 400


def test_writable_matches_the_forms():
    """writable.py is generated; a form edited without regenerating it would
    have its new field refused on save. Regenerate with
    `python addons/platform/cd_p03_portal/controllers/form_fields.py --a03`."""
    editable = form_fields.editable_by_model()
    expected = {m: frozenset(editable.get(m, ())) for m in form_fields.a03_surface_models()}
    assert expected == WRITABLE


def test_every_a03_surface_declares_what_it_accepts():
    missing = [m for m, conf in a03.SURFACES.items() if "writable" not in conf]
    assert not missing
    for model in a03.SURFACES:
        assert api.SURFACES[model]["writable"] is WRITABLE[model]


# --- the endpoint enforces it ----------------------------------------------


def _complaint(env):
    return env["fix.complaint"].create(
        {
            "name": "WL-PROBE",
            "customer_id": env(su=True)["res.partner"].create({"name": "WL Customer"}).id,
            "operating_unit_id": env["operating.unit"].search([], limit=1).id,
            "description": "whitelist probe",
            "severity": "minor",
        }
    )


def _off_screen_field(env, model):
    """An editable, unguarded scalar field that no workspace form offers."""
    fields = env[model]._fields
    locked = env[model]._fix_form_locked_fields()
    for name, field in sorted(fields.items()):
        if (
            field.type in ("char", "text")
            and field.store
            and not field.readonly
            and not field.compute
            and not field.related
            and name not in WRITABLE[model]
            and name not in locked
        ):
            return name
    pytest.skip("every scalar field of %s is on a form" % model)


def test_a_field_no_form_offers_is_refused(clerk_env, call):
    rec = _complaint(clerk_env)
    name = _off_screen_field(clerk_env, "fix.complaint")
    res = call(
        clerk_env,
        "model_write",
        model="fix.complaint",
        record_id=rec.id,
        values={name: "forged through the endpoint"},
    )
    assert "not editable on this screen" in res.get("error", ""), res
    assert rec[name] != "forged through the endpoint"


def test_an_unchanged_off_screen_echo_still_saves(clerk_env, call):
    rec = _complaint(clerk_env)
    res = call(
        clerk_env,
        "model_write",
        model="fix.complaint",
        record_id=rec.id,
        values={"currency_id": rec.currency_id.id, "description": "edited on the form"},
    )
    assert res.get("id") == rec.id, res
    assert rec.description == "edited on the form"


def test_a_workflow_field_change_is_refused_with_the_endpoint_message(clerk_env, call):
    rec = _complaint(clerk_env)
    res = call(
        clerk_env,
        "model_write",
        model="fix.complaint",
        record_id=rec.id,
        values={"state": "closed"},
    )
    assert "changes only through its workflow action" in res.get("error", ""), res
    assert rec.state == "new"


def test_create_drops_what_the_form_may_not_set(clerk_env, call):
    name = _off_screen_field(clerk_env, "fix.complaint")
    res = call(
        clerk_env,
        "model_write",
        model="fix.complaint",
        values={
            "name": "WL-CREATE",
            "customer_id": clerk_env(su=True)["res.partner"].create({"name": "WL C2"}).id,
            "operating_unit_id": clerk_env["operating.unit"].search([], limit=1).id,
            "description": "created on the form",
            "severity": "minor",
            "state": "closed",
            name: "smuggled in on create",
        },
    )
    rec = clerk_env["fix.complaint"].browse(res["id"])
    assert rec.state == "new" and rec[name] != "smuggled in on create"


# --- the form shows locked fields read-only --------------------------------


def _meta(call, env, model, names, record_id=None):
    res = call(
        env,
        "model_form",
        model=model,
        record_id=record_id,
        fields=[{"name": n} for n in names],
    )
    return {f["name"]: f for f in res["fields"]}


def test_guarded_fields_are_served_read_only(clerk_env, call):
    meta = _meta(call, clerk_env, "fix.campaign", ["budget_approved", "state", "budget", "name"])
    assert meta["budget_approved"]["readonly"] and meta["state"]["readonly"]
    assert not meta["budget"]["readonly"] and not meta["name"]["readonly"]


def test_a_captured_consent_is_served_read_only_but_a_new_one_is_not(odoo_env, clerk_env, call):
    notice = odoo_env["fix.transparency.notice"].create(
        {"version": "WL-1", "text_en": "Notice", "text_bn": "বিজ্ঞপ্তি"}
    )
    consent = odoo_env["fix.consent"].create(
        {
            "partner_id": odoo_env["res.partner"].create({"name": "WL Consent"}).id,
            "purpose": "marketing",
            "channel": "sms",
            "proof": "OTP-WL",
            "notice_version_id": notice.id,
        }
    )
    new = _meta(call, clerk_env, "fix.consent", ["purpose", "channel"])
    assert not new["purpose"]["readonly"] and not new["channel"]["readonly"]
    existing = _meta(call, clerk_env, "fix.consent", ["purpose", "channel"], consent.id)
    assert existing["purpose"]["readonly"] and existing["channel"]["readonly"]
