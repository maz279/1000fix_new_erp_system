# Behavioural tests for the M29 RBAC extension on the live ORM (`odoo_env`,
# rolled back after every test).
import contextlib

import pytest
from odoo.exceptions import ValidationError


@contextlib.contextmanager
def _rejects(env, exc, match):
    with pytest.raises(exc, match=match) as info, env.cr.savepoint():
        yield info


def _role(env, code, **vals):
    return env["fix.role"].create({"code": code, "name": vals.pop("name", code), **vals})


# --- fix.role ---------------------------------------------------------------------------


def test_role_code_must_use_the_register_format(odoo_env):
    with _rejects(odoo_env, ValidationError, match="R-nn format, got X-01"):
        _role(odoo_env, "X-01")
    roles = _role(odoo_env, "R-T10") | _role(odoo_env, "R-T11")
    roles._check_code()  # every valid code in a batch passes
    assert roles.mapped("code") == ["R-T10", "R-T11"]


def test_group_link_defaults_the_keycloak_role_to_the_code(odoo_env):
    group = odoo_env["res.groups"].create({"name": "Probe Workspace"})
    role = odoo_env["fix.role"].new({"code": "R-T12", "name": "Probe", "group_id": group.id})
    role._onchange_group()
    assert role.keycloak_role == "R-T12"


def test_group_link_keeps_an_explicit_keycloak_role(odoo_env):
    group = odoo_env["res.groups"].create({"name": "Probe Workspace"})
    role = odoo_env["fix.role"].new(
        {"code": "R-T13", "name": "Probe", "group_id": group.id, "keycloak_role": "realm-ops"}
    )
    role._onchange_group()
    assert role.keycloak_role == "realm-ops"
    unlinked = odoo_env["fix.role"].new({"code": "R-T14", "name": "No group"})
    unlinked._onchange_group()
    assert not unlinked.keycloak_role


# --- fix.sod.control ----------------------------------------------------------------------


def test_sod_control_cannot_pair_a_role_with_itself(odoo_env):
    role = _role(odoo_env, "R-T20")
    with _rejects(odoo_env, ValidationError, match="same role twice"):
        odoo_env["fix.sod.control"].create(
            {"code": "SOD-SELF", "name": "self", "role_a_id": role.id, "role_b_id": role.id}
        )


def test_check_assignment_blocks_only_active_blocking_controls(odoo_env):
    a, b, c = _role(odoo_env, "R-T21"), _role(odoo_env, "R-T22"), _role(odoo_env, "R-T23")
    Sod = odoo_env["fix.sod.control"]
    Sod.create({"code": "SOD-T21", "name": "Pay vs approve", "role_a_id": a.id, "role_b_id": b.id})
    Sod.create(
        {
            "code": "SOD-T22",
            "name": "Warn only",
            "role_a_id": a.id,
            "role_b_id": c.id,
            "conflict_action": "warn",
        }
    )

    with _rejects(odoo_env, ValidationError, match="SoD control SOD-T21: Pay vs approve"):
        Sod.check_assignment(a.id, b.id)
    with _rejects(odoo_env, ValidationError, match="SOD-T21"):
        Sod.check_assignment(b.id, a.id)  # the pair is unordered
    assert Sod.check_assignment(a.id, c.id) is True  # warn != block

    Sod.search([("code", "=", "SOD-T21")]).active = False
    assert Sod.check_assignment(a.id, b.id) is True  # archived control no longer blocks


# --- fix.isolation.tier ---------------------------------------------------------------------


def test_isolation_tier_name_follows_its_code(odoo_env):
    tiers = odoo_env["fix.isolation.tier"]
    tiers.search([("code", "=", "T4")]).unlink()
    tier = tiers.search([("code", "=", "T5")])
    tier.code = "T4"  # regression: the stored name had no @api.depends
    assert tier.name == "T4 - Management (Z5)"
    tiers.search([("code", "=", "T0")]).unlink()
    fresh = tiers.create({"code": "T0"})
    assert fresh.name == "T0 - Public"


# --- fix.feature.flag (role-scoped extension) -------------------------------------------------


def _flag(env, **vals):
    return env["fix.feature.flag"].create({"key": "probe.role.flag", "name": "Probe", **vals})


def test_role_scoped_flag_answers_per_role(odoo_env):
    granted, other = _role(odoo_env, "R-T30"), _role(odoo_env, "R-T31")
    _flag(odoo_env, enabled=True, scope="role", role_ids=[(6, 0, granted.ids)])
    Flag = odoo_env["fix.feature.flag"]
    assert Flag.is_enabled("probe.role.flag", role=granted) is True
    assert Flag.is_enabled("probe.role.flag", role=other) is False
    assert Flag.is_enabled("probe.role.flag") is False  # no role context: fail closed


def test_role_extension_fails_closed_for_unknown_or_disabled_flags(odoo_env):
    role = _role(odoo_env, "R-T32")
    Flag = odoo_env["fix.feature.flag"]
    assert Flag.is_enabled("probe.role.flag", role=role) is False
    _flag(odoo_env, enabled=False, scope="role", role_ids=[(6, 0, role.ids)])
    assert Flag.is_enabled("probe.role.flag", role=role) is False


def test_role_extension_delegates_non_role_scopes(odoo_env):
    _flag(odoo_env, enabled=True, scope="global")
    role = _role(odoo_env, "R-T33")
    assert odoo_env["fix.feature.flag"].is_enabled("probe.role.flag", role=role) is True


def test_field_rule_defaults_to_hidden(odoo_env):
    field = odoo_env["ir.model.fields"].search(
        [("model", "=", "res.partner"), ("name", "=", "vat")], limit=1
    )
    rule = odoo_env["fix.field.rule"].create({"model_id": field.model_id.id, "field_id": field.id})
    assert rule.permission == "hidden"
    assert rule.active
