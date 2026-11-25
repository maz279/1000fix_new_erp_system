# A03 control suite (R9 of the A03 workflow audit): one sweep over EVERY
# workflow-controlled field and routed approval in the area, run as a
# non-admin user, so a control added to a model is attacked here without
# anyone writing a test for it.
#
# The audit found that the superuser hid every gap: superuser writes are
# trusted, and every existing suite ran as the superuser. So each case acts
# as a plain internal user, and asserts the refusal comes from the CONTROL
# (the guard or the routing), not from some unrelated validation.
#
# Per guarded field, three assertions (R9 a/b/c):
#   a. routed approvals refuse to be pressed directly (approver's inbox only);
#   b. a plain write() that changes the field is refused by the guard;
#   c. no workspace form offers the field as editable, so /p03/model/write
#      never receives it as an editable input (and refuses it if it does).
# The workflow actions' own refusals (wrong tier, SoD, missing evidence) are
# covered model by model in cd_contact_centre/tests/test_a03_approval_bypass.py,
# test_a03_zero_trust_certification.py and the engine suite.
import itertools

import pytest
from odoo import fields
from odoo.addons.cd_p03_portal.controllers import a03
from odoo.addons.cd_p03_portal.controllers.a03.writable import WRITABLE
from odoo.exceptions import UserError

_SEQ = itertools.count(1)
GUARD_MESSAGE = "changes only through its workflow"
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
                "name": "Control Suite Clerk %d" % n,
                "login": "control.suite.%d@a03.test" % n,
                "group_ids": [(6, 0, [odoo_env.ref("base.group_user").id])],
            }
        )
    )
    return odoo_env(user=user.id)


def _guarded_models(env):
    out = []
    for model in sorted(a03.SURFACES):
        if model in env and hasattr(env[model], "_fix_guarded_fields"):
            out.append(model)
    return out


def _guarded_models_static():
    """Model names for parametrisation, before any database is open."""
    return sorted(a03.SURFACES)


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


@pytest.mark.parametrize("model", _guarded_models_static())
def test_every_guarded_field_refuses_a_direct_write(odoo_env, clerk_env, model):
    """R9 b: for every guarded field, a changing write() is refused by the guard."""
    if model not in odoo_env or not hasattr(odoo_env[model], "_fix_guarded_fields"):
        pytest.skip("%s carries no workflow-controlled fields" % model)
    record = clerk_env[model].new({})
    guarded = sorted(record._fix_guarded_fields())
    checked = 0
    for name in guarded:
        field = record._fields.get(name)
        if not field or field.type not in SIMPLE or not field.store or field.compute:
            continue
        value = _forged_value(clerk_env, field, record[name])
        if value is None:
            continue
        with pytest.raises(UserError, match=GUARD_MESSAGE):
            record.write({name: value})
        checked += 1
    assert checked or not guarded, "%s declares guarded fields but none could be attacked" % model


@pytest.mark.parametrize("model", _guarded_models_static())
def test_no_form_offers_a_guarded_field_as_editable(odoo_env, model):
    """R9 c (R5): a workflow-owned field is never an editable input on a
    workspace form, so the screen never offers what the server refuses."""
    if model not in odoo_env or not hasattr(odoo_env[model], "_fix_guarded_fields"):
        pytest.skip("%s carries no workflow-controlled fields" % model)
    guarded = odoo_env[model].browse()._fix_guarded_fields()
    offered = guarded & set(WRITABLE.get(model, ()))
    assert not offered, "the %s form offers workflow fields as editable: %s" % (
        model,
        sorted(offered),
    )


def test_every_routed_approval_refuses_to_be_pressed_directly(odoo_env, clerk_env):
    """R9 a: an approval routed through M63 cannot be granted by its button."""
    routed = [
        name
        for name in sorted(odoo_env.registry.models)
        if not odoo_env[name]._abstract and getattr(odoo_env[name], "_approval_routed", False)
    ]
    assert routed, "no routed approvals found: the M63 engine is not wired in"
    for name in routed:
        record = clerk_env[name].new({})
        method = (
            "action_dofa_approve"
            if hasattr(record, "_dofa_route_guard")
            else record._approval_apply_method
        )
        with pytest.raises(UserError, match=ROUTED_MESSAGE):
            getattr(record, method)()


def test_the_suite_reaches_the_area(odoo_env):
    """A guard on the guard: the sweep must actually cover A03's controls."""
    covered = list(_guarded_models(odoo_env))
    assert len(covered) >= 10, covered
