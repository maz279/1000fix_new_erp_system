# A05 control suite (A05 workflow audit E13): one sweep over EVERY
# workflow-controlled field and routed approval of the A05 Circular Economy
# surfaces (M13 rental, M14 trade-in, M18 e-waste), run as a non-admin user.
#
# The A05 audit (2026-11-03) found 24 of 24 A05 models writable by a plain
# internal user, 0 write whitelists and 19 models exposing workflow fields: a
# reservation written straight to active, a payout approval state set over
# JSON-RPC, an ESG figure typed in. This suite is the A02 control suite
# applied to A05: per guarded field, a changing write() is refused; no
# workspace form offers the field as editable; every routed approval refuses
# its button. The module suites (test_a05_m13/m14/m18_controls.py) prove each
# action's own gates on the real path.

import itertools

import pytest
from odoo import fields
from odoo.addons.cd_p03_portal.controllers import a05
from odoo.addons.cd_p03_portal.controllers.a05.writable import WRITABLE
from odoo.exceptions import UserError

_SEQ = itertools.count(1)
# the guard's own refusal, or a module's stricter transition check
REFUSED = r"changes only through its workflow|cannot be set directly|cannot move|cannot change|can no longer"
ROUTED_MESSAGE = "approver's inbox"
SIMPLE = {
    "char",
    "text",
    "boolean",
    "selection",
    "integer",
    "float",
    "monetary",
    "date",
    "datetime",
    "many2one",
}


@pytest.fixture
def clerk_env(odoo_env):
    n = next(_SEQ)
    user = (
        odoo_env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "A05 Control Suite Clerk %d" % n,
                "login": "a05.control.suite.%d@a05.test" % n,
                "group_ids": [(6, 0, [odoo_env.ref("base.group_user").id])],
            }
        )
    )
    return odoo_env(user=user.id)


def _guarded_models(env):
    return [
        model
        for model in sorted(a05.SURFACES)
        if model in env and hasattr(env[model], "_fix_guarded_fields")
    ]


def _models_static():
    """Model names for parametrisation, before any database is open."""
    return sorted(a05.SURFACES)


def _forged_value(env, field, current):
    """A value different from `current` that a forger would send."""
    if field.type == "boolean":
        return not current
    if field.type == "selection":
        values = [v for v, _l in (field._description_selection(env) or [])]
        others = [v for v in values if v != current]
        return others[-1] if others else None
    if field.type in ("integer", "float", "monetary"):
        return (current or 0) + 7
    if field.type == "date":
        return fields.Date.add(fields.Date.today(), days=-400)
    if field.type == "datetime":
        return fields.Datetime.add(fields.Datetime.now(), days=-400)
    if field.type == "many2one":
        other = env[field.comodel_name].sudo().search([], limit=2)
        other = other - current if current else other
        return other[:1].id or None
    return "forged-by-the-control-suite"


@pytest.mark.parametrize("model", _models_static())
def test_every_guarded_field_refuses_a_direct_write(odoo_env, clerk_env, model):
    """E3: for every guarded field, a changing write() is refused."""
    if model not in odoo_env or not hasattr(odoo_env[model], "_fix_guarded_fields"):
        pytest.skip("%s carries no workflow-controlled fields" % model)
    record = clerk_env[model].new({})
    guarded = sorted(record._fix_guarded_fields())
    checked = 0
    for name in guarded:
        field = record._fields.get(name)
        if not field or field.type not in SIMPLE or not field.store or field.compute:
            continue
        if field.groups:
            continue  # the clerk cannot even read it (e.g. the agreement OTP digest)
        value = _forged_value(clerk_env, field, record[name])
        if value is None:
            continue
        with pytest.raises(UserError, match=REFUSED):
            record.write({name: value})
        checked += 1
    assert checked or not guarded, "%s declares guarded fields but none could be attacked" % model


@pytest.mark.parametrize("model", _models_static())
def test_no_form_offers_a_guarded_field_as_editable(odoo_env, model):
    """E3: a workflow-owned field is never an editable input on a workspace
    form, so the screen never offers what the server refuses."""
    if model not in odoo_env or not hasattr(odoo_env[model], "_fix_guarded_fields"):
        pytest.skip("%s carries no workflow-controlled fields" % model)
    guarded = odoo_env[model].browse()._fix_guarded_fields()
    offered = guarded & set(WRITABLE.get(model, ()))
    assert not offered, "the %s form offers workflow fields as editable: %s" % (
        model,
        sorted(offered),
    )


def test_every_surface_has_a_whitelist():
    """E3 / D1: every A05 surface declares what /p03/model/write may set."""
    missing = sorted(m for m, conf in a05.SURFACES.items() if conf.get("writable") is None)
    assert not missing, missing


# A05 audit E5/E11: the A05 approvals routed through the M63 engine. A floor,
# so that un-routing one fails here instead of silently shrinking the sweep.
ROUTED_FLOOR = 6
# Routed A05 approvals with no workspace surface of their own: the request is
# raised from the rental's damage screen and decided only from the inbox.
ROUTED_WITHOUT_SURFACE = ("fix.rental.charge.approval",)


def _routed_models(env):
    return [
        name
        for name in sorted(set(a05.SURFACES) | set(ROUTED_WITHOUT_SURFACE))
        if name in env and getattr(env[name], "_approval_routed", False)
    ]


def test_every_routed_a05_approval_refuses_to_be_pressed_directly(odoo_env, clerk_env):
    """E11: an A05 approval routed through M63 cannot be granted by its
    button; only the approver's inbox applies it."""
    routed = _routed_models(odoo_env)
    assert len(routed) >= ROUTED_FLOOR, routed
    for name in routed:
        record = clerk_env[name].new({})
        method = (
            "action_dofa_approve"
            if hasattr(record, "_dofa_route_guard")
            else record._approval_apply_method
        )
        with pytest.raises(UserError, match=ROUTED_MESSAGE):
            getattr(record, method)()
        if name in a05.SURFACES:
            assert {"action_request_approval", "action_recall_approval"} <= set(
                a05.SURFACES[name]["actions"]
            ), "%s is routed but its surface cannot raise or recall the request" % name


def test_the_suite_reaches_the_area(odoo_env):
    """A guard on the guard: the A05 audit found 19 models exposing workflow
    fields; every one of them must now be guarded."""
    covered = _guarded_models(odoo_env)
    assert len(covered) >= 19, covered
