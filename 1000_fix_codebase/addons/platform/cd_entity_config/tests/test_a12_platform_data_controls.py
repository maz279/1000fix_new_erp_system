"""A12 platform-data controls (P1-4) on the live ORM (`odoo_env`, rolled
back per test): the country-pack certification lifecycle and the locale-pack
activation gate, both in cd_entity_config/models/fix_platform_ops.py and
fix_country_pack.py (A12_Workflow_and_Approval_Report.md §6, M64/M65.md).

- a country pack loads only after validate → certify (a platform-admin
  decision, with a recorded basis and an audit row) → activate;
- a locale pack activates only at the configured minimum coverage
  (ir.config_parameter fix_locale.min_activation_coverage_pct);
- neither state machine is ever typed: the guarded mixin refuses direct
  writes and the JS forms no longer offer the field.
"""

import contextlib

import pytest
from odoo.exceptions import AccessError, UserError, ValidationError

ADMIN = "cd_entity_config.group_platform_admin"
STEWARD = "cd_entity_config.group_mdm_domain_steward"
REFUSED = (UserError, ValidationError, AccessError)


@contextlib.contextmanager
def _rejects(env, exc, match):
    with pytest.raises(exc, match=match) as info, env.cr.savepoint():
        yield info


@pytest.fixture
def make_user(odoo_env):
    counter = {"n": 0}

    def _make(*xmlids):
        counter["n"] += 1
        groups = [odoo_env.ref("base.group_user").id] + [odoo_env.ref(x).id for x in xmlids]
        return (
            odoo_env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": "A12 Platform Probe %d" % counter["n"],
                    "login": "a12.plat.probe.%d@test" % counter["n"],
                    "group_ids": [(6, 0, groups)],
                }
            )
        )

    return _make


@pytest.fixture
def admin(make_user):
    return make_user(ADMIN)


def _pack(odoo_env, user, code, lines=(("BAR", "Barishal", "বরিশাল"),), **vals):
    pack = (
        odoo_env["fix.country.pack"]
        .with_user(user)
        .create({"name": "Pack %s" % code, "code": code, "kind": "divisions", **vals})
    )
    for i, (lcode, name, name_bn) in enumerate(lines):
        odoo_env["fix.country.pack.line"].with_user(user).create(
            {
                "pack_id": pack.id,
                "code": "%s-%d" % (lcode, i),
                "name": name,
                "name_bn": name_bn,
            }
        )
    return pack


# --- P1-4: the country-pack lifecycle ----------------------------------------


def test_the_full_lifecycle_validate_certify_activate_load_retire(odoo_env, admin):
    pack = _pack(odoo_env, admin, "BD-A12-LIFE")
    assert pack.state == "draft"

    pack.with_user(admin).action_validate()
    assert pack.state == "validated"

    pack.with_user(admin).action_certify(note="BBS gazette, 2026 revision")
    assert pack.state == "certified"
    assert pack.certified_by_id == admin and pack.certified_on
    audit = (
        odoo_env["fix.security.audit"]
        .sudo()
        .search(
            [
                ("event", "=", "country.pack_certified"),
                ("object_ref", "=", "fix.country.pack,%d" % pack.id),
            ]
        )
    )
    assert audit, "certification wrote no audit row"

    pack.with_user(admin).action_activate()
    assert pack.state == "active"
    pack.with_user(admin).action_load()
    assert pack.loaded_at
    pack.with_user(admin).action_retire()
    assert pack.state == "retired"


def test_an_empty_pack_does_not_validate(odoo_env, admin):
    pack = (
        odoo_env["fix.country.pack"]
        .with_user(admin)
        .create({"name": "Empty probe", "code": "BD-A12-EMPTY", "kind": "postcodes"})
    )
    with _rejects(odoo_env, REFUSED, match="at least one line"):
        pack.with_user(admin).action_validate()
    assert pack.state == "draft"


def test_certification_is_a_platform_admin_decision(odoo_env, admin, make_user):
    clerk = make_user()
    pack = _pack(odoo_env, admin, "BD-A12-CERT")
    pack.with_user(admin).action_validate()
    with _rejects(odoo_env, UserError, match="Platform Admin"):
        pack.with_user(clerk).action_certify(note="self-certified")
    assert pack.state == "validated"


def test_certification_needs_a_basis_and_a_validated_pack(odoo_env, admin):
    pack = _pack(odoo_env, admin, "BD-A12-BASIS")
    with _rejects(odoo_env, REFUSED, match="validated"):
        pack.with_user(admin).action_certify(note="jumping the queue")
    pack.with_user(admin).action_validate()
    with _rejects(odoo_env, REFUSED, match="basis"):
        pack.with_user(admin).action_certify()
    assert pack.state == "validated"


def test_loading_requires_certification_not_just_existence(odoo_env, admin):
    """The P1-4 finding: action_load ran from ANY state before."""
    pack = _pack(odoo_env, admin, "BD-A12-LOAD")
    with _rejects(odoo_env, REFUSED, match="certified, active"):
        pack.with_user(admin).action_load()
    assert not pack.loaded_at

    pack.with_user(admin).action_validate()
    with _rejects(odoo_env, REFUSED, match="certified, active"):
        pack.with_user(admin).action_load()
    assert not pack.loaded_at

    pack.with_user(admin).action_certify(note="gazette probe")
    with _rejects(odoo_env, REFUSED, match="certified, active"):
        pack.with_user(admin).action_load()
    assert not pack.loaded_at

    pack.with_user(admin).action_activate()
    pack.with_user(admin).action_load()
    assert pack.loaded_at


def test_an_uncertified_pack_does_not_activate(odoo_env, admin):
    pack = _pack(odoo_env, admin, "BD-A12-ACT")
    pack.with_user(admin).action_validate()
    with _rejects(odoo_env, REFUSED, match="certified"):
        pack.with_user(admin).action_activate()
    assert pack.state == "validated"


def test_pack_state_is_never_typed(odoo_env, admin):
    pack = _pack(odoo_env, admin, "BD-A12-GUARD")
    with _rejects(odoo_env, UserError, match="cannot be set directly"):
        pack.with_user(admin).write({"state": "certified", "certified_on": "2026-01-01"})
    assert pack.state == "draft" and not pack.certified_on


# --- M65: the locale-pack activation gate ------------------------------------


def _locale(odoo_env, user, code, coverage, **vals):
    return (
        odoo_env["fix.locale.pack"]
        .with_user(user)
        .create({"code": code, "name": "Locale %s" % code, "coverage_pct": coverage, **vals})
    )


def test_an_incomplete_locale_does_not_activate(odoo_env, admin):
    pack = _locale(odoo_env, admin, "bn_A12", 50)
    with _rejects(odoo_env, REFUSED, match="min_activation_coverage_pct"):
        pack.with_user(admin).action_activate()
    assert pack.state == "draft"


def test_a_complete_locale_activates_then_retires(odoo_env, admin):
    pack = _locale(odoo_env, admin, "bn_A12_OK", 100)
    pack.with_user(admin).action_activate()
    assert pack.state == "active"
    pack.with_user(admin).action_retire()
    assert pack.state == "retired"
    # re-activating a retired pack is a replacement decision, not a button
    with _rejects(odoo_env, REFUSED, match="draft"):
        pack.with_user(admin).action_activate()


def test_the_coverage_gate_reads_the_config_parameter(odoo_env, admin):
    odoo_env["ir.config_parameter"].sudo().set_param("fix_locale.min_activation_coverage_pct", "60")
    pack = _locale(odoo_env, admin, "bn_A12_TUNE", 65)
    pack.with_user(admin).action_activate()
    assert pack.state == "active"


def test_locale_state_is_never_typed(odoo_env, admin):
    pack = _locale(odoo_env, admin, "bn_A12_GUARD", 100)
    with _rejects(odoo_env, UserError, match="cannot be set directly"):
        pack.with_user(admin).write({"state": "active"})
    assert pack.state == "draft"
