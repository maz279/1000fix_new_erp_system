# A02 control suite (A02 workflow audit, P0 acceptance and C1): one sweep over
# EVERY workflow-controlled field and routed approval of the A02 Service
# Operations surfaces, run as a non-admin user.
#
# The A02 audit (2026-11-03) found 41 of 53 A02 models writable by a plain
# internal user with only one of them guarded, so a cashier approved her own
# variance and an operator verified his own wipe certificate. This suite is
# the A03 control suite applied to A02: per guarded field, a changing write()
# is refused by the guard, and no workspace form offers the field as
# editable. The A02 audit's module probes (working/A02_evidence/probes/) cover
# the workflow actions' own refusals.

import itertools

import pytest
from odoo import fields
from odoo.addons.cd_p03_portal.controllers import a02
from odoo.addons.cd_p03_portal.controllers.a02.writable import WRITABLE
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
                "name": "A02 Control Suite Clerk %d" % n,
                "login": "a02.control.suite.%d@a02.test" % n,
                "group_ids": [(6, 0, [odoo_env.ref("base.group_user").id])],
            }
        )
    )
    return odoo_env(user=user.id)


def _guarded_models(env):
    out = []
    for model in sorted(a02.SURFACES):
        if model in env and hasattr(env[model], "_fix_guarded_fields"):
            out.append(model)
    return out


def _guarded_models_static():
    """Model names for parametrisation, before any database is open."""
    return sorted(a02.SURFACES)


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


# A02 audit C1/B1: the A02 approvals routed through the M63 engine. A floor,
# so that un-routing one fails here instead of silently shrinking the sweep.
ROUTED_FLOOR = 13
# Routed A02 approvals with no workspace surface of their own: the request is
# raised from the order or job screen and decided only from the inbox.
ROUTED_WITHOUT_SURFACE = ("fix.so.approval", "fix.workshop.waiver.request")


def _routed_models(env):
    return [
        name
        for name in sorted(set(a02.SURFACES) | set(ROUTED_WITHOUT_SURFACE))
        if name in env and getattr(env[name], "_approval_routed", False)
    ]


def test_every_routed_a02_approval_refuses_to_be_pressed_directly(odoo_env, clerk_env):
    """C1: an A02 approval routed through M63 cannot be granted by its button;
    only the approver's inbox applies it."""
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


def test_the_suite_reaches_the_area(odoo_env):
    """A guard on the guard: the A02 audit found 25 models exposing workflow
    fields; every one of them must now be guarded."""
    covered = list(_guarded_models(odoo_env))
    assert len(covered) >= 25, covered
