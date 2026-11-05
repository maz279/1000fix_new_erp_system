# A10 remediation (2026-11-05), P1-4: one delegated-authority register (M60-6).
#
# The audit found two authority books that never read each other: the typed
# fix.grc.authority table — writable by every internal user, consulted by
# nothing — and the machinery that actually enforces authority (the DOFA
# ladders every tier derivation reads, and the M63 approval matrix the engine
# routes by). The register is now a derived VIEW: rows exist only as a
# rebuild from the enforced sources, a typed row is refused at the ORM (and
# the portal writer accepts nothing), and the rebuild is the Delegated
# Authority Owner's (CFO) act. A ruling resyncs it; a daily clock converges
# it after a matrix edit.
import itertools

import pytest
from odoo.exceptions import AccessError, UserError, ValidationError

_SEQ = itertools.count(1)


def _user(env, name, group=None):
    n = next(_SEQ)
    groups = [env.ref("base.group_user").id]
    if group:
        groups.append(env.ref(group).id)
    return env["res.users"].with_context(no_reset_password=True).create(
        {
            "name": "A10 P14 %s %d" % (name, n),
            "login": "a10p14.%s.%d@a10.test" % (name.replace(" ", "").lower(), n),
            "group_ids": [(6, 0, groups)],
        }
    )


def _ladder(env, name, target, basis, bands):
    return env["fix.dofa.ladder"].create(
        {
            "name": name,
            "target_model": target,
            "basis": basis,
            "company_id": env.company.id,
            "threshold_ids": [
                (0, 0, {"upper_bound": bound, "tier": tier}) for bound, tier in bands
            ],
        }
    )


def test_the_register_is_derived_not_typed(odoo_env):
    env = odoo_env
    Register = env["fix.grc.authority"]
    clerk = _user(env, "Clerk")  # an internal user: read the view, write nothing
    cfo = _user(env, "CFO", group="cd_grc.group_grc_dofa_admin")
    ladder = _ladder(
        env,
        "P14 service-risk ladder",
        "a10.p14.risk",
        "ruling",
        [(5000.0, "tier_1"), (50000.0, "tier_3"), (1e9, "tier_5")],
    )
    # the ruling is what fills the register — nothing was ever typed
    ladder.action_put_in_force(reference="Board minute BM-2026-11")
    rows = Register.search([("source_ref", "=", "fix.dofa.ladder:%d" % ladder.id)])
    assert len(rows) == 3
    top = rows.filtered(lambda r: r.amount_limit >= 1e9)
    assert top.role_title == "Tier 5 — Managing Director / Board"
    assert "a10.p14.risk" in top.authority_scope
    assert top.source == "dofa" and top.synced_at
    # a typed row is refused at the ORM even for the DoA admin — the ACL and
    # the form are layers, not the rule
    with pytest.raises(ValidationError, match="VIEW over the machinery"):
        Register.with_user(cfo).create(
            {"name": "Hand-typed authority", "role_title": "Anyone", "amount_limit": 9e9}
        )
    with pytest.raises(ValidationError, match="VIEW over the machinery"):
        rows[:1].with_user(cfo).write({"amount_limit": 9e9})
    with pytest.raises(ValidationError, match="VIEW over the machinery"):
        rows[:1].with_user(cfo).unlink()
    # and a plain internal user is stopped by the ACL layer the portal writer
    # checks before any ORM call (check_access_rights is what the endpoint
    # calls; the model guard would fire first inside write() itself)
    with pytest.raises(AccessError):
        Register.with_user(clerk).check_access_rights("write")
    Register.with_user(cfo).check_access_rights("write")  # the admin passes it


def test_rebuild_is_the_doa_admins_act(odoo_env):
    env = odoo_env
    Register = env["fix.grc.authority"]
    clerk = _user(env, "Clerk")
    cfo = _user(env, "CFO", group="cd_grc.group_grc_dofa_admin")
    ladder = _ladder(
        env, "P14 ladder", "a10.p14.risk2", "ruling", [(1000.0, "tier_1"), (1e9, "tier_4")]
    )
    ladder.action_put_in_force(reference="BM-1")
    assert Register.search([("source_ref", "=", "fix.dofa.ladder:%d" % ladder.id)])
    # the clock converges the register without anyone clicking
    res = Register.cron_rebuild_doa()
    assert res["created"] >= 2
    # the manual rebuild is the Delegated Authority Owner's act
    with pytest.raises(UserError, match="Delegated Authority Owner"):
        Register.with_user(clerk).action_rebuild()
    out = Register.with_user(cfo).action_rebuild()
    assert out["note"].startswith("Register rebuilt")


def test_the_register_reads_the_m63_matrix_too(odoo_env):
    env = odoo_env
    if "fix.approval.matrix" not in env:
        pytest.skip("cd_workflow_engine not installed")
    Register = env["fix.grc.authority"]
    rule = env["fix.approval.matrix"].create(
        {
            "name": "P14 estimate rule",
            "decision_domain": "estimate",
            "res_model": "a10.p14.estimate",
            "threshold": 25000.0,
            "approver_role": "R-24 Head of Service Delivery",
            "company_id": env.company.id,
        }
    )
    Register.cron_rebuild_doa()
    row = Register.search([("source_ref", "=", "fix.approval.matrix:%d" % rule.id)])
    assert len(row) == 1
    assert row.amount_limit == 25000.0
    assert row.role_title == "R-24 Head of Service Delivery"
    assert "M63 approval matrix" in row.authority_scope
    assert row.source == "matrix"
    # a retired rule is retired authority: the rebuild drops its row
    rule.active = False
    Register.cron_rebuild_doa()
    assert not Register.search([("source_ref", "=", "fix.approval.matrix:%d" % rule.id)])


def test_a_ruling_resyncs_the_register(odoo_env):
    env = odoo_env
    Register = env["fix.grc.authority"]
    # two bases for one target: putting the second in force retires the first
    first = _ladder(env, "P14 first", "a10.p14.risk3", "req_text",
                    [(100.0, "tier_0"), (1e9, "tier_3")])
    first.action_put_in_force(reference="BM-A")
    assert Register.search([("source_ref", "=", "fix.dofa.ladder:%d" % first.id)])
    second = _ladder(env, "P14 second", "a10.p14.risk3", "ruling",
                     [(100.0, "tier_0"), (9999.0, "tier_2"), (1e9, "tier_5")])
    second.action_put_in_force(reference="BM-B")
    # the view no longer describes the retired ladder's authority
    assert not Register.search([("source_ref", "=", "fix.dofa.ladder:%d" % first.id)])
    rows = Register.search([("source_ref", "=", "fix.dofa.ladder:%d" % second.id)])
    assert len(rows) == 3
    assert set(rows.mapped("source")) == {"dofa"}
