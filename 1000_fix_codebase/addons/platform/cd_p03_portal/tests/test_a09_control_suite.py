# A09 control suite (A09 workflow audit B1, B6 and P3): one sweep over EVERY
# workflow-controlled field of the A09 People & Workforce surfaces, run as a
# non-admin user.
#
# The A09 audit (2026-11-03) found 0 of 65 A09 models guarded and 43 exposing
# workflow fields to their own operational role: an employee approved her own
# leave, a payroll officer wrote `state='approved'`. This suite is the A02/A03
# control suite applied to A09, with one addition the audit asked for (P3):
# a workflow-looking field on an A09 surface that is NOT guarded fails the
# suite, so a new A09 field cannot ship unguarded without someone saying why.
import itertools
import re

import pytest
from odoo import fields
from odoo.addons.cd_p03_portal.controllers import a09
from odoo.addons.cd_p03_portal.controllers.a09.writable import WRITABLE
from odoo.exceptions import AccessError, UserError

_SEQ = itertools.count(1)
GUARD_MESSAGE = "changes only through its workflow"
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

# A stored field whose name says it records a workflow outcome: a state, an
# approval, a verification, a sign-off, a clearance or who/when decided it.
WORKFLOW_NAME = re.compile(
    r"(^state$|_state$|^approval_|approv|verified|^is_verified|signed_off|"
    r"_signoff|decided|cleared|clearance_status|^locked|_locked$|^posted|"
    r"_posted_|^published|released_by|deprovision)"
)
# Fields that match the pattern but are not workflow outcomes. Each needs a
# reason; an entry without one is a hole in the suite. None is needed today:
# every workflow-looking field on an A09 surface is guarded.
NOT_WORKFLOW: dict[tuple[str, str], str] = {}


@pytest.fixture
def clerk_env(odoo_env):
    n = next(_SEQ)
    user = (
        odoo_env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "A09 Control Suite Clerk %d" % n,
                "login": "a09.control.suite.%d@a09.test" % n,
                "group_ids": [(6, 0, [odoo_env.ref("base.group_user").id])],
            }
        )
    )
    return odoo_env(user=user.id)


def _models_static():
    """Model names for parametrisation, before any database is open."""
    return sorted(a09.SURFACES)


def _workflow_fields(model):
    out = set()
    for name, field in model._fields.items():
        if not field.store or field.compute or field.related:
            continue
        if field.type not in ("selection", "boolean", "many2one", "date", "datetime"):
            continue
        if (model._name, name) in NOT_WORKFLOW:
            continue
        if WORKFLOW_NAME.search(name):
            out.add(name)
    return out


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
def test_every_workflow_field_is_guarded(odoo_env, model):
    """P3: every workflow-looking stored field on an A09 surface is guarded."""
    Model = odoo_env[model]
    wf = _workflow_fields(Model)
    if not wf:
        return
    assert hasattr(Model, "_fix_guarded_fields"), "%s has workflow fields %s and no guard" % (
        model,
        sorted(wf),
    )
    unguarded = wf - Model.browse()._fix_guarded_fields()
    assert not unguarded, "%s leaves workflow fields unguarded: %s" % (model, sorted(unguarded))


@pytest.mark.parametrize("model", _models_static())
def test_every_guarded_field_refuses_a_direct_write(odoo_env, clerk_env, model):
    """B1: for every guarded field, a changing write() is refused by the guard."""
    if not hasattr(odoo_env[model], "_fix_guarded_fields"):
        return
    record = clerk_env[model].new({})
    guarded = sorted(record._fix_guarded_fields())
    checked = 0
    for name in guarded:
        field = record._fields.get(name)
        if not field or field.type not in SIMPLE or not field.store or field.compute:
            continue
        # read the current value as superuser: a field restricted to a group
        # (hr.employee PSR stamps, P0-a) is unreadable to the clerk, and the
        # guard, not the read, is what is under test
        value = _forged_value(clerk_env, field, record.sudo()[name])
        if value is None:
            continue
        if field.groups and not clerk_env.user.has_groups(field.groups):
            # a field restricted to a group the clerk lacks (hr.employee PSR
            # stamps, P0-a) is refused by the field ACL before the guard runs
            with pytest.raises(AccessError):
                record.write({name: value})
        else:
            with pytest.raises(UserError, match=GUARD_MESSAGE):
                record.write({name: value})
        checked += 1
    assert checked or not guarded, "%s declares guarded fields but none could be attacked" % model


@pytest.mark.parametrize("model", _models_static())
def test_no_form_offers_a_guarded_field_as_editable(odoo_env, model):
    """A workflow-owned field is never an editable input on a workspace form,
    so the screen never offers what the server refuses."""
    if not hasattr(odoo_env[model], "_fix_guarded_fields"):
        return
    guarded = odoo_env[model].browse()._fix_guarded_fields()
    offered = guarded & set(WRITABLE.get(model, ()))
    assert not offered, "the %s form offers workflow fields as editable: %s" % (
        model,
        sorted(offered),
    )


def test_the_suite_reaches_the_area(odoo_env):
    """A guard on the guard: the A09 audit found 43 models exposing workflow
    fields; every one of them must now be guarded."""
    covered = [m for m in a09.SURFACES if hasattr(odoo_env[m], "_fix_guarded_fields")]
    assert len(covered) >= 43, sorted(covered)
