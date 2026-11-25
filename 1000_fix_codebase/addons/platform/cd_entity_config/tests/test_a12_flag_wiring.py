"""A12 P2 / M30-9 — feature flags gate code, or they do not exist.

The register held decorative keys no code read (D1). Now a flag may only
exist for a capability the code actually gates: create/write refuse keys
outside FLAG_WIRED_KEYS, and the one shipped kill switch
(itsm.sla_auto_escalate) is read by cd_itsm's SLA escalation cron.
"""

import pytest
from odoo.exceptions import UserError

from ..models.fix_feature_flag import FLAG_WIRED_KEYS


def _admin(env):
    """A human platform administrator (not the superuser service mode)."""
    admin = env["res.users"].create(
        {
            "name": "A12 Flag Admin",
            "login": "a12_flag_admin",
            "email": "flag.admin@example.test",
            "group_ids": [(4, env.ref("cd_entity_config.group_platform_admin").id)],
        }
    )
    return admin


def test_the_wiring_registry_ships_a_real_kill_switch():
    assert "itsm.sla_auto_escalate" in FLAG_WIRED_KEYS


def test_a_decorative_flag_cannot_be_created(odoo_env):
    env = odoo_env
    with pytest.raises(UserError, match="No code reads a flag"):
        env["fix.feature.flag"].with_user(_admin(env)).create(
            {"key": "decorative.ponies", "name": "Ponies for everyone", "enabled": True}
        )


def test_a_decorative_key_cannot_be_written_onto_a_flag(odoo_env):
    env = odoo_env
    flag = env["fix.feature.flag"].create(
        {"key": "itsm.sla_auto_escalate", "name": "SLA auto-escalation kill switch"}
    )
    with pytest.raises(UserError, match="No code reads a flag"):
        flag.with_user(_admin(env)).write({"key": "decorative.ponies"})


def test_a_wired_flag_is_created_and_tracked(odoo_env):
    env = odoo_env
    flag = (
        env["fix.feature.flag"]
        .with_user(_admin(env))
        .create({"key": "itsm.sla_auto_escalate", "name": "SLA auto-escalation kill switch"})
    )
    assert flag.key == "itsm.sla_auto_escalate"
    assert flag.enabled is False  # safe default


def test_is_disabled_is_presence_based_opt_out(odoo_env):
    """is_disabled: True only when the row EXISTS and is disabled.

    Absent row = the default behaviour stays ON (the audit-mandated
    escalation keeps running); this is the opt-out twin of is_enabled's
    fail-closed opt-in, and the difference between them is the contract."""
    env = odoo_env
    Flags = env["fix.feature.flag"]
    # absent -> not disabled (default on)
    assert Flags.is_disabled("itsm.sla_auto_escalate") is False
    flag = env["fix.feature.flag"].create(
        {"key": "itsm.sla_auto_escalate", "name": "SLA auto-escalation kill switch"}
    )
    # present but enabled=False -> disabled
    assert Flags.is_disabled("itsm.sla_auto_escalate") is True
    # switched on -> not disabled
    flag.write({"enabled": True})
    assert Flags.is_disabled("itsm.sla_auto_escalate") is False


def test_the_opt_in_reader_still_fails_closed(odoo_env):
    """is_enabled keeps its A12 contract: unknown key answers False."""
    assert odoo_env["fix.feature.flag"].is_enabled("no.such.key") is False
